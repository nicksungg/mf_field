"""
Adapter: train + evaluate MFRNP (Multi-Fidelity Residual Neural Processes,
Niu et al. ICML 2024) on any factory_mffp dataset and emit the JSON expected
by ../../../eval/MODEL_CONTRACT.md.

This wraps the upstream model at `upstream/model/Model.py` directly, bypassing
`upstream/train.py` and `upstream/model/supervisor.py` (which depend on `ray`
and `wandb`). The training-loop body here mirrors `supervisor.py:_run_epoch`
and `calculate_loss` faithfully.

The upstream `MultiFidelityModel` consumes flat vectors per level. The
factory_mffp data adapter (`data_adapters.load_mf_dataset`) returns each
field flat as (N_fid, n_cells_fid), so it is a 1:1 match for MFRNP's
per-level `output_dims=[n_cells_l1, n_cells_l2, ...]`. Inputs/outputs are
normalized per-level with the upstream `StandardScaler`. nRMSE on the HF
test split is reported (in raw units) as `splits.test_hf.nRMSE`.

Small-HF defensive logic (kept from the prior ifc_heat-only wrapper): when
the HF training count is small (<=10), skip the 90/10 train/valid split and
widen the model's internal context_percentage from 0.20/0.25 to 0.40/0.60 so
that `floor(N_batch * ctx)` stays >=1 and `ba_z_agg` does not crash.

For npz_l* datasets where sample counts differ per fidelity (era5 is the
notable case: LF=1222 vs HF=65), MFLoader naturally trims to the smallest
level's batch (this is consistent with upstream's MultiFidelityDataLoader
behavior).

Resume: <ckpt_dir>/last.pt is written each epoch with
{epoch, epochs_target, model, optim, z_mu_all, z_cov_all}; if it matches
--epochs we skip training and go straight to eval.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
import types
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

HERE = Path(__file__).resolve().parent
UPSTREAM = HERE / "upstream"

# ---------------------------------------------------------------------------
# Stub `torchvision` BEFORE importing upstream Model.py, because upstream does
# `import torchvision.transforms as transforms` for an antialiased Resize that
# we replace with torch.nn.functional.interpolate (no torchvision needed).
# ---------------------------------------------------------------------------
if "torchvision" not in sys.modules:
    tv = types.ModuleType("torchvision")
    tv_t = types.ModuleType("torchvision.transforms")

    class _ResizeStub:
        def __init__(self, size, antialias=True):
            self.size = size

        def __call__(self, x):
            # x: (B, H, W) — upstream calls this on a reshape to (B, H, W)
            # match the same output by adding a channel dim then interpolating.
            if x.dim() == 3:
                x = x.unsqueeze(1)
                y = F.interpolate(x, size=self.size, mode="bilinear",
                                  align_corners=False, antialias=True)
                return y.squeeze(1)
            return F.interpolate(x, size=self.size, mode="bilinear",
                                 align_corners=False, antialias=True)

    tv_t.Resize = _ResizeStub
    tv.transforms = tv_t
    sys.modules["torchvision"] = tv
    sys.modules["torchvision.transforms"] = tv_t

sys.path.insert(0, str(UPSTREAM))

# Make the factory_mffp data_adapters package importable. The smoke script
# lives at references/external_sota/mfrnp/smoke_eval.py; the repo root is
# three levels up (mfrnp -> external_sota -> references -> factory_mffp).
REPO_ROOT = HERE.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model.Model import MultiFidelityModel  # noqa: E402
from model import loss as mf_loss  # noqa: E402
from lib.utils import StandardScaler  # noqa: E402

from data_adapters import load_mf_dataset  # noqa: E402
from data_adapters.geometry import resolve_grid  # noqa: E402
from data_adapters.metrics import finalize_and_write  # noqa: E402


# Longest side of a level's working grid. era5/pm_test (721x1440) would give a
# >1M-output decoder and a non-square reshape that crashes upstream's resizer;
# capping to 256 keeps decoders tractable. No-op for every other dataset.
# Data-handling/hyperparameter only — the upstream MultiFidelityModel is
# unchanged; we just (a) resample fields to a working grid and (b) pass the
# upstream `fid_lats` kwarg so it uses its rectangular reshape path instead of
# the square-only fallback that crashes on era5/1-D fields.
MFRNP_WORK_CAP = 256


def _cap_grid(grid, cap: int = MFRNP_WORK_CAP):
    H, W = int(grid[0]), int(grid[1])
    m = max(H, W)
    if m <= cap:
        return (H, W)
    f = cap / m
    return (max(1, round(H * f)), max(1, round(W * f)))


def _resample_flat(y_flat: np.ndarray, src_grid, dst_grid) -> np.ndarray:
    """Resample (N, prod(src_grid)) flat fields to (N, prod(dst_grid))."""
    if tuple(src_grid) == tuple(dst_grid):
        return y_flat.astype(np.float32, copy=False)
    Hs, Ws = int(src_grid[0]), int(src_grid[1])
    Hd, Wd = int(dst_grid[0]), int(dst_grid[1])
    t = torch.from_numpy(np.ascontiguousarray(y_flat, dtype=np.float32)).view(-1, 1, Hs, Ws)
    t = F.interpolate(t, size=(Hd, Wd), mode="bilinear", align_corners=False)
    return t.view(y_flat.shape[0], Hd * Wd).numpy().astype(np.float32)


def split_train_valid(Xs, ys, train_ratio=0.9, seed=0):
    """90/10 in-split holdout for the epoch-level validation print only.

    Used when the HF training count is large enough that carving off a 10%
    valid slice still leaves enough samples for the model's internal
    context/target split. Per-level (Xs[lvl], ys[lvl]) need not share the
    same N; each level is shuffled and split independently.
    """
    rng = np.random.default_rng(seed)
    tr_x, va_x, tr_y, va_y = [], [], [], []
    for x, y in zip(Xs, ys):
        n = x.shape[0]
        idx = rng.permutation(n)
        n_tr = max(1, int(train_ratio * n))
        # ensure at least 1 valid sample if there is room
        if n_tr >= n:
            n_tr = max(1, n - 1) if n > 1 else n
        tr_idx, va_idx = idx[:n_tr], idx[n_tr:]
        if len(va_idx) == 0:
            va_idx = tr_idx[: max(1, len(tr_idx) // 5)]
        tr_x.append(x[tr_idx]); tr_y.append(y[tr_idx])
        va_x.append(x[va_idx]); va_y.append(y[va_idx])
    return tr_x, tr_y, va_x, va_y


# ---------------------------------------------------------------------------
# Mini-batch loader mirroring upstream `MultiFidelityDataLoader`. Each level
# may have different N; we cap batch_size at the min level size, which keeps
# the model's `forward` happy (all `xs[level]` arrive with the same batch dim).
# ---------------------------------------------------------------------------
class MFLoader:
    def __init__(self, Xs, ys, device, batch_size, shuffle=True, seed=0):
        self.Xs = Xs
        self.ys = ys
        self.device = device
        self.shuffle = shuffle
        self.rng = np.random.default_rng(seed)
        max_bs = min(x.shape[0] for x in Xs)
        self.batch_size = min(batch_size, max_bs)
        self.n_iter = max(1, max_bs // self.batch_size) * self.batch_size

    def __iter__(self):
        if self.shuffle:
            for lvl in range(len(self.Xs)):
                idx = self.rng.permutation(self.Xs[lvl].shape[0])
                self.Xs[lvl] = self.Xs[lvl][idx]
                self.ys[lvl] = self.ys[lvl][idx]
        for b in range(0, self.n_iter, self.batch_size):
            xs = [torch.from_numpy(x[b:b + self.batch_size]).to(self.device)
                  for x in self.Xs]
            ys = [torch.from_numpy(y[b:b + self.batch_size]).to(self.device)
                  for y in self.ys]
            yield xs, ys


# ---------------------------------------------------------------------------
# Loss aggregation: lifted from supervisor.calculate_loss but stripped of
# scaler-aware nRMSE bookkeeping (we compute nRMSE outside, in raw units).
# ---------------------------------------------------------------------------
def compute_train_loss(output, levels, fidelity_weight, lower_fidelity_weight):
    total = 0.0
    for level in range(1, levels + 1):
        nll = mf_loss.nll_loss(
            output["output_mus"][level - 1],
            output["output_covs"][level - 1],
            output["targets"][level - 1],
            return_numpy=False,
        )
        kld = mf_loss.kld_gaussian_loss(
            output["z_mu_all"][level - 1], output["z_cov_all"][level - 1],
            output["z_mu_cs"][level - 1], output["z_cov_cs"][level - 1],
        )
        w = fidelity_weight if level == levels else lower_fidelity_weight
        total = total + nll * w + kld
    return total


def param_count(model):
    n = sum(p.numel() for p in model.parameters())
    n_trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return n_trainable, n


def run(args):
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    random.seed(args.seed)

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    ds_dir = Path(args.dataset_dir)

    # ── Load via the unified data adapter ────────────────────────────────
    # The adapter returns:
    #   data["fids"]:           sorted list of fidelity ids (ascending)
    #   data["hf_fid"]:         the high-fidelity id (== max(fids))
    #   data["cond_by_fid"]:    {fid: (N_fid, cond_dim) np.float32}
    #   data["field_by_fid"]:   {fid: (N_fid, n_cells_fid) np.float32, FLAT}
    # Flat fields are exactly what MFRNP's MultiFidelityModel expects per level.
    train_data = load_mf_dataset(ds_dir, split="train")
    test_data = load_mf_dataset(ds_dir, split="test")

    train_fids = train_data["fids"]
    hf = train_data["hf_fid"]
    # If the test split's HF differs from the train HF (rare but possible),
    # fall back to the test HF so the test metric is on a fidelity present in
    # the test split.
    if hf not in test_data["fids"]:
        hf = test_data["hf_fid"]

    print(f"[data] loader={train_data['loader']} | train fidelities = {train_fids} | HF = {hf}")

    # Materialize per-level train arrays in ascending-fid order. The adapter
    # already flattens fields to (N, n_cells); no further reshape needed.
    Xs_train_all = [train_data["cond_by_fid"][f].astype(np.float32, copy=False)
                    for f in train_fids]
    ys_train_all = [train_data["field_by_fid"][f].astype(np.float32, copy=False)
                    for f in train_fids]

    # Test: only HF (the contract metric is `splits.test_hf.nRMSE`).
    Xs_test_hf = [test_data["cond_by_fid"][hf].astype(np.float32, copy=False)]
    ys_test_hf = [test_data["field_by_fid"][hf].astype(np.float32, copy=False)]

    # ── Resolve a working grid per fidelity and resample fields onto it. ──
    # resolve_grid gives a concrete (H, W) (rectangular era5/pm_test, 1-D as
    # (1, L), square otherwise); cap the longest side so the per-level decoder
    # output dim stays tractable (era5 HF 721x1440 -> 128x256). fid_lats then
    # tells upstream to use its rectangular reshape path.
    work_grids = []          # per train fidelity, ascending
    for f in train_fids:
        nat = resolve_grid(args.dataset_name, int(train_data["n_cells_by_fid"][f]))
        work_grids.append(_cap_grid(nat))
    ys_train_all = [
        _resample_flat(y, resolve_grid(args.dataset_name, int(train_data["n_cells_by_fid"][f])), wg)
        for y, f, wg in zip(ys_train_all, train_fids, work_grids)
    ]
    hf_work_grid = work_grids[train_fids.index(hf)] if hf in train_fids else _cap_grid(
        resolve_grid(args.dataset_name, int(test_data["n_cells_by_fid"][hf])))
    ys_test_hf = [
        _resample_flat(ys_test_hf[0], resolve_grid(args.dataset_name, int(test_data["n_cells_by_fid"][hf])),
                       hf_work_grid)
    ]
    # Per-level latitudes (H) for upstream's rectangular reshape/resize path.
    fid_lats = [int(g[0]) for g in work_grids]
    print(f"[grids] work_grids={work_grids} fid_lats={fid_lats} hf_work_grid={hf_work_grid}")

    # ── Small-HF defensive split ────────────────────────────────────────
    # The IFC datasets are tiny at high fidelity (ifc_heat HF has 5 train
    # samples), so a 90/10 train/valid split + the model's internal 20%/25%
    # context/target split would produce empty contexts and crash `ba_z_agg`.
    # When HF is small we keep all training data and use a slice of train as
    # a cheap held-out for the epoch print only. The contract metric is
    # always computed on the HF test split.
    n_hf_train = ys_train_all[-1].shape[0]
    small_hf = n_hf_train <= 10
    if small_hf:
        print(f"[data] small HF training count ({n_hf_train}) -> skipping 90/10 split, "
              f"using widened context_percentage 0.4/0.6")
        Xs_tr, ys_tr = Xs_train_all, ys_train_all
        Xs_va = [x[: max(1, x.shape[0] // 5)] for x in Xs_train_all]
        ys_va = [y[: max(1, y.shape[0] // 5)] for y in ys_train_all]
    else:
        Xs_tr, ys_tr, Xs_va, ys_va = split_train_valid(
            Xs_train_all, ys_train_all, train_ratio=0.9, seed=args.seed)

    # Per-level scalers fit on train; one shared x-scaler from level 1.
    scaler_x = StandardScaler(np.mean(Xs_tr[0]), np.std(Xs_tr[0]) + 1e-12)
    scalers_y = [
        StandardScaler(np.mean(y), np.std(y) + 1e-12) for y in ys_tr
    ]
    Xs_tr = [scaler_x.transform(x) for x in Xs_tr]
    Xs_va = [scaler_x.transform(x) for x in Xs_va]
    ys_tr = [s.transform(y) for s, y in zip(scalers_y, ys_tr)]
    ys_va = [s.transform(y) for s, y in zip(scalers_y, ys_va)]
    # Test HF uses the HF scaler (last level).
    Xs_test_hf = [scaler_x.transform(x) for x in Xs_test_hf]

    levels = len(train_fids)
    input_dim = Xs_tr[0].shape[1]
    output_dims = [y.shape[1] for y in ys_tr]
    print(f"[model] levels={levels} input_dim={input_dim} output_dims={output_dims}")

    # Build model. We pass device via model_kwargs; upstream Model.__init__
    # places submodules on that device.
    # Context split must yield >=1 context AND >=1 target at the smallest
    # batch size. The IFC HF split is tiny (N=5), so widen the context range
    # from the upstream 0.20/0.25 to 0.40/0.60 when HF is small; for
    # larger-HF datasets keep the upstream defaults.
    ctx_lo, ctx_hi = (0.4, 0.6) if small_hf else (0.2, 0.25)
    model_kwargs = dict(
        hidden_dim=128,
        z_dim=64,
        hidden_layers=3,
        context_percentage_low=ctx_lo,
        context_percentage_high=ctx_hi,
        device=str(device),
        # Per-level latitudes so upstream uses its rectangular reshape/resize
        # path (handles era5 rectangular + 1-D fields); without this it falls
        # back to a square int(n**0.5) reshape that crashes on those datasets.
        fid_lats=fid_lats,
    )
    model = MultiFidelityModel(
        levels=levels,
        input_dim=input_dim,
        output_dims=output_dims,
        **model_kwargs,
    )
    model.to(device)
    n_trainable, n_total = param_count(model)

    optim = torch.optim.Adam(model.parameters(), lr=1e-3, eps=1e-3)
    fidelity_weight = 2.0
    lower_fidelity_weight = 1.0
    batch_size = 2048

    # ---- resume ---------------------------------------------------------
    ckpt_dir = Path(args.ckpt_dir); ckpt_dir.mkdir(parents=True, exist_ok=True)
    last_ckpt = ckpt_dir / "last.pt"
    start_epoch = 0
    z_mu_all = None
    z_cov_all = None
    if last_ckpt.exists():
        sd = torch.load(last_ckpt, map_location=device)
        if sd.get("epochs_target") == args.epochs:
            model.load_state_dict(sd["model"])
            optim.load_state_dict(sd["optim"])
            start_epoch = int(sd["epoch"]) + 1
            z_mu_all = [t.to(device) for t in sd.get("z_mu_all", [])] or None
            z_cov_all = [t.to(device) for t in sd.get("z_cov_all", [])] or None
            print(f"[resume] epoch {start_epoch}/{args.epochs}")

    train_loader = MFLoader(Xs_tr, ys_tr, device, batch_size,
                            shuffle=True, seed=args.seed)
    valid_loader = MFLoader(Xs_va, ys_va, device, batch_size,
                            shuffle=False, seed=args.seed)

    # ---- training -------------------------------------------------------
    t_train = time.time()
    last_output = None
    for epoch in range(start_epoch, args.epochs):
        model.train()
        for xs, ys in train_loader:
            optim.zero_grad()
            output = model(xs, ys)
            loss_val = compute_train_loss(
                output, levels, fidelity_weight, lower_fidelity_weight)
            loss_val.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optim.step()
            last_output = output
        # capture z_mu_all/z_cov_all from the final training batch (matches
        # supervisor.py behavior).
        if last_output is not None:
            z_mu_all = [t.detach() for t in last_output["z_mu_all"]]
            z_cov_all = [t.detach() for t in last_output["z_cov_all"]]

        # cheap validation print
        model.eval()
        with torch.no_grad():
            for xs, ys in valid_loader:
                if z_mu_all is None:
                    break
                out = model.evaluate(xs, ys, z_mu_all, z_cov_all)
                # report HF nRMSE in normalized units
                pred = out["model_pred"].cpu().numpy()
                tgt = out["targets"][-1].cpu().numpy()
                num = np.sqrt(np.mean((pred - tgt) ** 2))
                den = np.sqrt(np.mean(tgt ** 2)) + 1e-12
                print(f"[epoch {epoch+1:04d}/{args.epochs}] "
                      f"valid HF nRMSE (norm units) = {num/den:.4e}")
                break

        # save every epoch (cheap for a smoke run)
        torch.save({
            "epoch": epoch,
            "epochs_target": args.epochs,
            "model": model.state_dict(),
            "optim": optim.state_dict(),
            "z_mu_all": [t.cpu() for t in z_mu_all] if z_mu_all else [],
            "z_cov_all": [t.cpu() for t in z_cov_all] if z_cov_all else [],
        }, last_ckpt)
    train_seconds = time.time() - t_train

    # If we resumed at epochs_target, z_mu_all already loaded. If neither
    # ran nor loaded any z, do one extra training-step style forward pass on a
    # single train batch to populate z_mu_all/z_cov_all so evaluate() works.
    if z_mu_all is None:
        model.train()
        for xs, ys in train_loader:
            output = model(xs, ys)
            z_mu_all = [t.detach() for t in output["z_mu_all"]]
            z_cov_all = [t.detach() for t in output["z_cov_all"]]
            break

    # ---- evaluate on test HF -------------------------------------------
    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()
        torch.cuda.synchronize()
    t_eval = time.time()
    model.eval()
    # We feed `xs` at every level using HF Xs (so the model's broadcast in
    # evaluate() works); ys placeholder must match each level's output_dim.
    # The model only uses the HF entry of `xs` for the final ensemble plus
    # the per-level decoder reshape. To match upstream behavior we replicate
    # HF test Xs to every level, with zero-valued ys (only used to compute
    # NLL which we ignore — model_pred is what we want).
    xs_test = [torch.from_numpy(Xs_test_hf[0]).to(device) for _ in range(levels)]
    ys_test = [torch.zeros(Xs_test_hf[0].shape[0], od, device=device)
               for od in output_dims]
    with torch.no_grad():
        out = model.evaluate(xs_test, ys_test, z_mu_all, z_cov_all)
        pred_norm = out["model_pred"].cpu().numpy()  # (N, HF*HF), normalized
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    eval_seconds = time.time() - t_eval
    # inverse-transform back to raw units using HF scaler (last level)
    hf_scaler = scalers_y[-1]
    pred_raw = hf_scaler.inverse_transform(pred_norm)
    tgt_raw = ys_test_hf[0]  # already raw, shape (N, prod(hf_work_grid))
    n_samples = int(tgt_raw.shape[0])

    if torch.cuda.is_available():
        latency_ms_per_sample = 1000.0 * eval_seconds / max(n_samples, 1)
        peak_mem_mb = torch.cuda.max_memory_allocated() / 1e6
    else:
        latency_ms_per_sample = None
        peak_mem_mb = None

    return finalize_and_write(
        out_path=Path(args.out),
        model="mfrnp",
        dataset=args.dataset_name,
        pred=pred_raw,
        target=tgt_raw,
        work_grid=hf_work_grid,
        n_params=int(n_total),
        train_seconds=train_seconds,
        eval_seconds=eval_seconds,
        latency_ms_per_sample=latency_ms_per_sample,
        peak_mem_mb=peak_mem_mb,
        seed=args.seed,
        extra={
            "device": str(device),
            "hf_fidelity": int(hf),
            "levels": int(levels),
        },
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset_dir", required=True)
    ap.add_argument("--dataset_name", required=True)
    ap.add_argument("--epochs", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ckpt_dir", required=True)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    # run() writes the file itself via finalize_and_write (single write).
    res = run(args)
    print(f"[wrote] {out}")
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
