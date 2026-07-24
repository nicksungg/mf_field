"""
Adapter: train + evaluate D-MFD (Disentangled Multi-Fidelity Deep Bayesian
Active Learning, Wu et al. ICML 2023) as a multi-fidelity surrogate on any
factory_mffp dataset (ifc_raw, npz_l*, or chin_chun layouts) and emit the
JSON expected by ../../../eval/MODEL_CONTRACT.md.

This wraps the bare 2-fidelity model class at
`upstream/dmfdal_2f/model/pytorch/model.py` directly, bypassing
`upstream/dmfdal_2f/train.py` and `model/pytorch/supervisor.py` (which depend
on tensorflow / tensorboard / wandb-style yaml-config plumbing AND the active
learning loop). Only the multi-fidelity surrogate is exercised: one full pass
through LF + HF train data per epoch (matches supervisor's per-epoch shape),
NLL + KLD losses on both levels (no global_dist term — that requires paired
LF/HF data over the same inputs, which the factory datasets do not provide
across all 15 layouts).

Data is sourced via `data_adapters.load_mf_dataset`, which returns fields as
flat (N, n_cells) regardless of the underlying grid shape. D-MFD consumes
flat vectors per level naturally. Inputs/outputs are normalized per-level
with the upstream StandardScaler. nRMSE on the HF test split is reported as
splits.test_hf.nRMSE in raw units.

For the 2-fidelity wrapper we pick LF = smallest fidelity and HF = max
fidelity (one of the data["lf_fids"], data["hf_fid"]). If the HF train set
is tiny (N < 10), we widen context_percentage from upstream's [0.2, 0.5] to
[0.4, 0.6] so split_context_target keeps at least 1 context AND >=1 target
sample (the ifc_heat case has N=5).

Resume: <ckpt_dir>/last.pt is written each epoch with
{epoch, epochs_target, model, optim, l1_z_mu_all, l1_z_cov_all,
 l2_z_mu_all, l2_z_cov_all}; if it matches --epochs we skip training and go
straight to eval.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import random
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

HERE = Path(__file__).resolve().parent
UPSTREAM = HERE / "upstream" / "dmfdal_2f"
REPO_ROOT = HERE.parents[2]  # .../factory_mffp

# We import model.pytorch.model and model.pytorch.loss directly. We do NOT
# import model.pytorch.supervisor (which pulls tensorflow via lib.utils and
# also pulls torch.utils.tensorboard).
sys.path.insert(0, str(UPSTREAM))
# Make data_adapters importable from the repo root.
sys.path.insert(0, str(REPO_ROOT))

from model.pytorch.model import Model as DMFDModel  # noqa: E402
from model.pytorch.loss import nll_loss, kld_gaussian_loss  # noqa: E402

from data_adapters import load_mf_dataset  # noqa: E402
from data_adapters.geometry import resolve_grid  # noqa: E402
from data_adapters.metrics import finalize_and_write  # noqa: E402


# Longest side of a level's working grid. D-MFD's decoder output dim equals the
# field's flat cell count, so era5/pm_test (721x1440 ~1.04M cells) would build a
# >1M-wide decoder. We resample each level's field onto a 256-capped working
# grid (no-op for every other dataset) so the decoder stays tractable and every
# model is scored on the SAME common working grid. Data-handling/grid-layout
# only — the upstream Model (MLP encoders/decoders over flat vectors) is
# unchanged.
DMFD_WORK_CAP = 256


def _cap_grid(grid, cap: int = DMFD_WORK_CAP):
    """Downscale a 2-D (H, W) grid so its longest side is <= cap (no-op for 1-D
    or already-small grids)."""
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


class StandardScaler:
    """Match upstream lib.utils.StandardScaler (per-level mean/std)."""

    def __init__(self, mean, std):
        self.mean = float(mean)
        self.std = float(std) + 1e-12

    def transform(self, data):
        return (data - self.mean) / self.std

    def inverse_transform(self, data):
        return data * self.std + self.mean


def param_count(model):
    return (
        sum(p.numel() for p in model.parameters() if p.requires_grad),
        sum(p.numel() for p in model.parameters()),
    )


def make_silent_logger():
    """The upstream Model.__init__ stashes a logger but only .debug() / .info()
    is called. Give it a no-op logger so we don't spam stderr."""
    log = logging.getLogger("d_mfd.upstream")
    log.handlers = []
    log.addHandler(logging.NullHandler())
    log.setLevel(logging.WARNING)
    return log


def run(args):
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    random.seed(args.seed)

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    ds_dir = Path(args.dataset_dir)
    train_data = load_mf_dataset(ds_dir, split="train")
    test_data = load_mf_dataset(ds_dir, split="test")

    train_fids = train_data["fids"]
    test_fids = test_data["fids"]
    if len(train_fids) < 2:
        raise RuntimeError(f"D-MFD 2f needs >=2 train fidelities; got {train_fids}")
    # 2-fid wrapper: LF = smallest train fid, HF = max (matches adapter's hf_fid).
    hf = train_data["hf_fid"]
    lf_candidates = train_data["lf_fids"]
    if not lf_candidates:
        raise RuntimeError(f"D-MFD 2f needs >=1 LF fid; got hf={hf}, lf={lf_candidates}")
    lf = min(lf_candidates)
    if hf not in test_data["field_by_fid"]:
        # Fall back to whatever HF the test split offers.
        hf = test_data["hf_fid"]
    print(f"[data] LF=fidelity_{lf}  HF=fidelity_{hf}  "
          f"(train fids={train_fids}, test fids={test_fids}, "
          f"loader={train_data['loader']})")

    l1_x_raw = train_data["cond_by_fid"][lf].astype(np.float32)
    l1_y_raw = train_data["field_by_fid"][lf].astype(np.float32)
    l2_x_raw = train_data["cond_by_fid"][hf].astype(np.float32)
    l2_y_raw = train_data["field_by_fid"][hf].astype(np.float32)
    test_x_raw = test_data["cond_by_fid"][hf].astype(np.float32)
    test_y_raw = test_data["field_by_fid"][hf].astype(np.float32)

    # ── Resolve a 256-capped working grid per level and resample fields onto
    # it. resolve_grid gives a concrete (H, W) (rectangular era5/pm_test, 1-D
    # as (1, L), square otherwise); capping keeps the per-level decoder output
    # dim tractable. The HF working grid is the common grid every model is
    # scored on (passed to finalize_and_write). No-op for non-era5 datasets.
    lf_grid_native = resolve_grid(args.dataset_name, int(l1_y_raw.shape[1]))
    hf_grid_native = resolve_grid(args.dataset_name, int(l2_y_raw.shape[1]))
    lf_work_grid = _cap_grid(lf_grid_native)
    hf_work_grid = _cap_grid(hf_grid_native)
    l1_y_raw = _resample_flat(l1_y_raw, lf_grid_native, lf_work_grid)
    l2_y_raw = _resample_flat(l2_y_raw, hf_grid_native, hf_work_grid)
    test_hf_grid_native = resolve_grid(args.dataset_name, int(test_y_raw.shape[1]))
    test_y_raw = _resample_flat(test_y_raw, test_hf_grid_native, hf_work_grid)
    print(f"[grids] lf_work_grid={lf_work_grid} hf_work_grid={hf_work_grid}")

    input_dim = l1_x_raw.shape[1]
    l1_output_dim = l1_y_raw.shape[1]
    l2_output_dim = l2_y_raw.shape[1]
    if l2_x_raw.shape[1] != input_dim:
        raise RuntimeError(
            f"D-MFD 2f wrapper assumes shared cond_dim across fidelities; "
            f"got LF cond_dim={input_dim} but HF cond_dim={l2_x_raw.shape[1]}"
        )

    # Per-level scalers fit on train. x-scaler is shared across levels (matches
    # upstream behavior where both l1_x and l2_x use l1_x_scaler).
    x_scaler = StandardScaler(np.mean(l1_x_raw), np.std(l1_x_raw))
    l1_y_scaler = StandardScaler(np.mean(l1_y_raw), np.std(l1_y_raw))
    l2_y_scaler = StandardScaler(np.mean(l2_y_raw), np.std(l2_y_raw))

    l1_x = x_scaler.transform(l1_x_raw).astype(np.float32)
    l2_x = x_scaler.transform(l2_x_raw).astype(np.float32)
    l1_y = l1_y_scaler.transform(l1_y_raw).astype(np.float32)
    l2_y = l2_y_scaler.transform(l2_y_raw).astype(np.float32)
    test_x = x_scaler.transform(test_x_raw).astype(np.float32)
    # test_y kept in raw units for nRMSE.

    levels_info = (
        f"input_dim={input_dim}  l1_output_dim={l1_output_dim}  "
        f"l2_output_dim={l2_output_dim}  "
        f"N(l1)={l1_x.shape[0]}  N(l2)={l2_x.shape[0]}  "
        f"N(test_hf)={test_x.shape[0]}"
    )
    print(f"[model] {levels_info}")

    # Build the upstream model. When HF train has very few samples (e.g.
    # ifc_heat N=5), upstream's default context_percentage [0.2, 0.5] can
    # produce 0 context or 0 target rows after split_context_target. Widen
    # the band to [0.4, 0.6] in that regime; otherwise keep upstream default.
    min_n = min(l1_x_raw.shape[0], l2_x_raw.shape[0])
    if min_n < 10:
        ctx_lo, ctx_hi = 0.4, 0.6
    else:
        ctx_lo, ctx_hi = 0.2, 0.5
    logger = make_silent_logger()
    model_kwargs = dict(
        device=str(device),
        hidden_layers=3,
        hidden_dim=128,
        z_dim=64,
        input_dim=input_dim,
        l1_output_dim=l1_output_dim,
        l2_output_dim=l2_output_dim,
        context_percentage_low=ctx_lo,
        context_percentage_high=ctx_hi,
    )
    model = DMFDModel(logger, **model_kwargs)
    model.to(device)
    n_trainable, n_total = param_count(model)

    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3, eps=1e-3)
    fidelity_weight = 2.0  # weight on l2 nll vs l1 nll (matches upstream default)
    max_grad_norm = 1.0

    # ---------- resume ---------------------------------------------------
    ckpt_dir = Path(args.ckpt_dir)
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    last_ckpt = ckpt_dir / "last.pt"
    start_epoch = 0
    z_state = None  # holds (l1_z_mu, l1_z_cov, l2_z_mu, l2_z_cov)
    if last_ckpt.exists():
        sd = torch.load(last_ckpt, map_location=device)
        if sd.get("epochs_target") == args.epochs:
            model.load_state_dict(sd["model"])
            optimizer.load_state_dict(sd["optim"])
            start_epoch = int(sd["epoch"]) + 1
            try:
                z_state = (
                    sd["l1_z_mu_all"].to(device), sd["l1_z_cov_all"].to(device),
                    sd["l2_z_mu_all"].to(device), sd["l2_z_cov_all"].to(device),
                )
            except KeyError:
                z_state = None
            print(f"[resume] epoch {start_epoch}/{args.epochs}")

    # x_ref / l1_y_ref / l2_y_ref are the "paired LF/HF" tensors that
    # upstream's _compute_global_dist_loss uses to encourage agreement between
    # LF and HF latent posteriors over a shared set of inputs. IFC has no
    # paired data across fidelities, so we drop that loss term entirely. We
    # still must give the model SOME (x_ref, l1_y_ref, l2_y_ref) tuple of
    # matching batch sizes — pick the first min(N_l1, N_l2) random rows of
    # each, which is enough to populate the encoder forward without affecting
    # any back-propped loss term we keep.
    n_ref = min(l1_x.shape[0], l2_x.shape[0])
    rng = np.random.default_rng(args.seed)
    ref_idx_l1 = rng.choice(l1_x.shape[0], size=n_ref, replace=False)
    ref_idx_l2 = rng.choice(l2_x.shape[0], size=n_ref, replace=False)
    x_ref_t = torch.from_numpy(l1_x[ref_idx_l1]).to(device)
    l1_y_ref_t = torch.from_numpy(l1_y[ref_idx_l1]).to(device)
    l2_y_ref_t = torch.from_numpy(l2_y[ref_idx_l2]).to(device)

    l1_x_t = torch.from_numpy(l1_x).to(device)
    l1_y_t = torch.from_numpy(l1_y).to(device)
    l2_x_t = torch.from_numpy(l2_x).to(device)
    l2_y_t = torch.from_numpy(l2_y).to(device)

    # ---------- training loop -------------------------------------------
    t_train = time.time()
    for epoch in range(start_epoch, args.epochs):
        model.train()
        optimizer.zero_grad()
        out = model(
            l1_x_t, l1_y_t, l2_x_t, l2_y_t,
            x_ref_t, l1_y_ref_t, l2_y_ref_t,
            test=False,
        )
        (l1_output_mu, l1_output_cov, l2_output_mu, l2_output_cov,
         l1_truth, l2_truth,
         l1_z_mu_all, l1_z_cov_all, l1_z_mu_c, l1_z_cov_c,
         l2_z_mu_all, l2_z_cov_all, l2_z_mu_c, l2_z_cov_c,
         _l1_r_mu_ref, _l1_r_cov_ref, _l2_r_mu_ref, _l2_r_cov_ref) = out

        l1_nll = nll_loss(l1_output_mu, l1_output_cov, l1_truth)
        l2_nll = nll_loss(l2_output_mu, l2_output_cov, l2_truth)
        l1_kld = kld_gaussian_loss(l1_z_mu_all, l1_z_cov_all, l1_z_mu_c, l1_z_cov_c)
        l2_kld = kld_gaussian_loss(l2_z_mu_all, l2_z_cov_all, l2_z_mu_c, l2_z_cov_c)
        loss = l1_nll + fidelity_weight * l2_nll + l1_kld + l2_kld

        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_grad_norm)
        optimizer.step()

        z_state = (
            l1_z_mu_all.detach(), l1_z_cov_all.detach(),
            l2_z_mu_all.detach(), l2_z_cov_all.detach(),
        )

        print(f"[epoch {epoch+1:04d}/{args.epochs}] "
              f"loss={loss.item():.4e}  l1_nll={l1_nll.item():.4e}  "
              f"l2_nll={l2_nll.item():.4e}  "
              f"l1_kld={l1_kld.item():.4e}  l2_kld={l2_kld.item():.4e}")

        torch.save({
            "epoch": epoch,
            "epochs_target": args.epochs,
            "model": model.state_dict(),
            "optim": optimizer.state_dict(),
            "l1_z_mu_all": z_state[0].cpu(),
            "l1_z_cov_all": z_state[1].cpu(),
            "l2_z_mu_all": z_state[2].cpu(),
            "l2_z_cov_all": z_state[3].cpu(),
        }, last_ckpt)

    train_seconds = time.time() - t_train

    # If we resumed at epochs_target with no z saved (older ckpt), do one
    # forward pass to populate z_state.
    if z_state is None:
        model.train()
        with torch.no_grad():
            out = model(
                l1_x_t, l1_y_t, l2_x_t, l2_y_t,
                x_ref_t, l1_y_ref_t, l2_y_ref_t,
                test=False,
            )
            z_state = (
                out[6].detach(), out[7].detach(),
                out[10].detach(), out[11].detach(),
            )

    # ---------- evaluate on HF test ------------------------------------
    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()
        torch.cuda.synchronize()
    t_eval = time.time()
    model.eval()
    test_x_t = torch.from_numpy(test_x).to(device)
    # Upstream's test branch requires both l1_x_test AND l2_x_test. We use the
    # HF test inputs at both levels (we only score the l2 output).
    with torch.no_grad():
        l1_pred_mu, _l1_pred_cov, l2_pred_mu, _l2_pred_cov = model(
            test=True,
            l1_x_test=test_x_t,
            l2_x_test=test_x_t,
            l1_z_mu_all=z_state[0], l1_z_cov_all=z_state[1],
            l2_z_mu_all=z_state[2], l2_z_cov_all=z_state[3],
        )
        # sample_z returns (1, B, D)-style tensors then squeezes during decode;
        # check actual shape and reduce sample dim if needed.
        pred = l2_pred_mu.cpu().numpy()
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    eval_seconds = time.time() - t_eval
    if pred.ndim == 3:
        pred = pred.mean(axis=0)
    pred_raw = l2_y_scaler.inverse_transform(pred)
    tgt_raw = test_y_raw  # (N, prod(hf_work_grid)) raw
    n_samples = int(tgt_raw.shape[0])

    if torch.cuda.is_available():
        latency_ms_per_sample = 1000.0 * eval_seconds / max(n_samples, 1)
        peak_mem_mb = torch.cuda.max_memory_allocated() / 1e6
    else:
        latency_ms_per_sample = None
        peak_mem_mb = None

    return finalize_and_write(
        out_path=Path(args.out),
        model="d_mfd",
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
            "lf_fidelity": int(lf),
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
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    # run() writes the file itself via finalize_and_write (single write).
    res = run(args)
    print(f"[wrote] {out}")
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
