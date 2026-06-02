"""
Smoke/full eval entrypoint for the fno_coregionalization family.

CLI matches `eval/MODEL_CONTRACT.md` exactly. Resumes from `ckpt_dir/last.pt`.

Data loading uses `data_adapters.load_mf_dataset` + `data_adapters.geometry.
resolve_grid`, so this family runs on every non-chin_chun dataset:
  * square 2-D grids (poisson/heat/darcy/…),
  * rectangular grids (era5/pm_test), and
  * 1-D fields (allen_cahn/burgers/…) represented as height-1 (1, L) grids.
A rectangular-capable 2-D FNO on a (1, L) grid is exactly a 1-D FNO, so all of
the above share one code path — the model no longer skips any dataset.

A *working-resolution cap* (`WORK_CAP`, longest side) keeps the single shared
FNO tractable on very large grids: era5's HF is 721x1440, which would be slow
and memory-heavy at full resolution. When the HF grid exceeds the cap the model
trains/evaluates on a proportionally downscaled working grid (era5 -> 128x256)
and the reported nRMSE is computed at that working grid. Every dataset whose HF
side is <= WORK_CAP (all of them except era5/pm_test) is unaffected and runs
bit-identically to before.

Pipeline per call:
  1. Load train; resolve each fid's (H, W); bilinearly resample to the working
     grid. m is the continuous fidelity index in [0, 1].
  2. Per-fidelity scalers (max(|y|)) from the post-split training subset.
  3. Build FNOCoregionalization at the working grid, modes per axis.
  4. H2: two-stage LF→HF transfer (lyu2023mffno recipe).
       Stage 1 (LF warm-up): `n_warmup = round(pretrain_frac * epochs)` epochs on
       LF-only samples (m != hf_m), fresh Adam at `pretrain_lr`, fresh cosine.
       Stage 2 (joint fine-tune): remaining `epochs - n_warmup` epochs on the
       full training set, fresh Adam at `finetune_lr`, fresh cosine. The K=10
       coregionalization basis stays trainable across both stages; trunk + head
       weights carry forward through the shared `model` object.
  5. Evaluate test/ood at the HF fidelity (resampled to the working grid);
     report L2 nRMSE.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset, Subset, random_split

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO_ROOT))

from model import FNOCoregionalization, param_count  # noqa: E402
from data_adapters import load_mf_dataset  # noqa: E402
from data_adapters.geometry import resolve_grid  # noqa: E402
from data_adapters.metrics import finalize_and_write  # noqa: E402


WORK_CAP = 256  # longest side of the working grid; only era5/pm_test exceed it.

SMOKE_DEFAULTS = dict(
    batch_size=8,
    lr=3e-4,
    weight_decay=1e-5,
    hidden_channels=32,
    K=10,
    n_blocks=4,
    modes_cap=12,
    val_frac=0.1,
    ckpt_every=10,
    grad_clip=1.0,
    # H2: two-stage LF→HF transfer schedule (lyu2023mffno recipe over the
    # li2022ifc coregionalization head). pretrain_frac fraction of args.epochs
    # is Stage 1 (LF-only, lr=pretrain_lr); the remainder is Stage 2 (joint
    # fine-tune, lr=finetune_lr). Fresh Adam + fresh CosineAnnealingLR per stage.
    pretrain_lr=1e-3,
    finetune_lr=3e-4,
    pretrain_frac=0.25,
)


def work_grid(grid, cap: int = WORK_CAP):
    """Downscale (H, W) proportionally so the longest side is <= cap."""
    H, W = int(grid[0]), int(grid[1])
    m = max(H, W)
    if m <= cap:
        return (H, W)
    f = cap / m
    return (max(1, round(H * f)), max(1, round(W * f)))


def _modes_for_grid(grid, cap: int):
    H, W = grid
    return (min(cap, max(H // 2, 1)), min(cap, W // 2 + 1))


def _resample_to(y2d: torch.Tensor, target) -> torch.Tensor:
    """y2d: (H, W) tensor → (target_h, target_w). No-op if already there."""
    th, tw = target
    if y2d.shape[0] == th and y2d.shape[1] == tw:
        return y2d
    up = F.interpolate(y2d.unsqueeze(0).unsqueeze(0), size=(th, tw),
                       mode="bilinear", align_corners=False)
    return up.squeeze(0).squeeze(0)


class AdapterMFDataset(Dataset):
    """Lazily resamples per-fidelity fields to a shared working grid.

    Each item: (X, y_work, m). Native (N, H, W) arrays per fid are kept in
    `raw_y_by_m` (for scaler computation) and resampled to the working grid
    on access — bounded memory even for era5.
    """

    def __init__(self, data: dict, dataset_name: str, target_grid):
        self.target_grid = (int(target_grid[0]), int(target_grid[1]))
        self.cond_dim = int(data["cond_dim"])
        fids = list(data["fids"])
        n_fids = len(fids)
        self.fid_list = fids
        if n_fids == 1:
            self.t_list = [1.0]
        else:
            self.t_list = [i / (n_fids - 1) for i in range(n_fids)]

        # index records as (fid_id, row) and resample lazily
        self.index: list[tuple[int, int]] = []
        self.fid_id_by_record: list[int] = []
        self.raw_y_by_m: dict[float, np.ndarray] = {}
        self._xs_by_fid: dict[int, np.ndarray] = {}
        self._y2d_by_fid: dict[int, np.ndarray] = {}

        for fid_id, fid in enumerate(fids):
            n_cells = int(data["field_by_fid"][fid].shape[1])
            H, W = resolve_grid(dataset_name, n_cells)
            xs = np.asarray(data["cond_by_fid"][fid], dtype=np.float32)
            ys_flat = np.asarray(data["field_by_fid"][fid], dtype=np.float32)
            if ys_flat.shape[1] != H * W:
                continue
            ys_2d = ys_flat.reshape(ys_flat.shape[0], H, W)
            t = float(self.t_list[fid_id])
            self.raw_y_by_m[t] = ys_2d
            self._xs_by_fid[fid_id] = xs
            self._y2d_by_fid[fid_id] = ys_2d
            for i in range(xs.shape[0]):
                self.index.append((fid_id, i))
                self.fid_id_by_record.append(fid_id)

        if not self.index:
            raise ValueError("No usable fidelities in this split")

    def __len__(self) -> int:
        return len(self.index)

    def __getitem__(self, idx: int):
        fid_id, row = self.index[idx]
        X = self._xs_by_fid[fid_id][row]
        y2d = torch.from_numpy(self._y2d_by_fid[fid_id][row]).float()
        y = _resample_to(y2d, self.target_grid)
        m = float(self.t_list[fid_id])
        return (torch.from_numpy(X).float(), y, torch.tensor(m, dtype=torch.float32))


def compute_per_fidelity_scalers(dataset, indices=None):
    """scaler[m] = max(|y|) over raw per-fidelity arrays, restricted to rows in
    `indices`. Returns (m_keys, scalers) sorted by m."""
    kept = list(range(len(dataset))) if indices is None else list(indices)
    rows_by_fid: dict[int, list[int]] = {}
    # recover per-fid row index for each record (records grouped by fid)
    record_to_row: list[int] = []
    row_within_fid = -1
    last_fid = -1
    for fid_id in dataset.fid_id_by_record:
        if fid_id != last_fid:
            row_within_fid = 0
            last_fid = fid_id
        else:
            row_within_fid += 1
        record_to_row.append(row_within_fid)
    for ridx in kept:
        fid_id = dataset.fid_id_by_record[ridx]
        rows_by_fid.setdefault(fid_id, []).append(record_to_row[ridx])

    out: dict[float, float] = {}
    for fid_id, rows in rows_by_fid.items():
        m = float(dataset.t_list[fid_id])
        raw = dataset.raw_y_by_m.get(m)
        if raw is None or len(rows) == 0:
            continue
        sub = raw[np.asarray(rows, dtype=np.int64)]
        out[m] = max(float(np.abs(sub).max()), 1e-12)
    global_max = max(out.values()) if out else 1.0
    for m in dataset.t_list:
        out.setdefault(float(m), global_max)
    items = sorted(out.items())
    return [m for m, _ in items], [s for _, s in items]


def nrmse_over_loader(model, loader, device) -> tuple[float, int]:
    model.eval()
    n = 0
    sq_sum = 0.0
    tgt_sq_sum = 0.0
    with torch.no_grad():
        for X, y, m in loader:
            X = X.to(device); y = y.to(device); m = m.to(device)
            pred = model(X, m)
            sq_sum += float(((pred - y) ** 2).sum().item())
            tgt_sq_sum += float((y ** 2).sum().item())
            n += X.size(0)
    if tgt_sq_sum <= 0 or n == 0:
        return float("nan"), n
    return float(np.sqrt(sq_sum / max(tgt_sq_sum, 1e-12))), n


def fields_over_loader(model, loader, device) -> tuple[np.ndarray, np.ndarray]:
    """Collect full predicted/target HF fields (de-normalized, raw units) on the
    working grid. Returns (pred_full, target_full) of shape (N, H*W) float32."""
    model.eval()
    preds: list[np.ndarray] = []
    tgts: list[np.ndarray] = []
    with torch.no_grad():
        for X, y, m in loader:
            X = X.to(device); y = y.to(device); m = m.to(device)
            pred = model(X, m)
            preds.append(pred.reshape(pred.shape[0], -1).cpu().numpy().astype(np.float32))
            tgts.append(y.reshape(y.shape[0], -1).cpu().numpy().astype(np.float32))
    if preds:
        return np.concatenate(preds, axis=0), np.concatenate(tgts, axis=0)
    return np.zeros((0, 0), dtype=np.float32), np.zeros((0, 0), dtype=np.float32)


def run(args) -> dict:
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    p = SMOKE_DEFAULTS

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    ds_dir = Path(args.dataset_dir)

    train_data = load_mf_dataset(ds_dir, split="train")
    hf_fid = train_data["hf_fid"]
    hf_cells = int(train_data["field_by_fid"][hf_fid].shape[1])
    hf_grid = resolve_grid(args.dataset_name, hf_cells)
    grid = work_grid(hf_grid)
    modes_h, modes_w = _modes_for_grid(grid, int(p["modes_cap"]))

    train_full = AdapterMFDataset(train_data, args.dataset_name, target_grid=grid)
    n_total = len(train_full)
    n_val = max(1, int(round(n_total * p["val_frac"])))
    n_tr = max(1, n_total - n_val)
    if n_tr + n_val != n_total:
        n_val = n_total - n_tr
    g = torch.Generator().manual_seed(args.seed)
    tr_ds, val_ds = random_split(train_full, [n_tr, n_val], generator=g)

    m_keys, scalers = compute_per_fidelity_scalers(train_full, tr_ds.indices)

    tr_loader = DataLoader(tr_ds, batch_size=p["batch_size"], shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=p["batch_size"], shuffle=False, num_workers=0)

    model = FNOCoregionalization(
        cond_dim=train_full.cond_dim,
        hidden_channels=p["hidden_channels"],
        K=p["K"],
        n_blocks=p["n_blocks"],
        modes_h=modes_h,
        modes_w=modes_w,
        grid=grid,
    ).to(device)
    # Scalers are computed once from the full train subset (LF + HF) and
    # applied across both stages — no per-stage rescaling (H2).
    model.set_scalers(m_keys, scalers)

    # ── H2: two-stage LF→HF transfer schedule ──
    n_warmup = int(round(p["pretrain_frac"] * args.epochs))
    n_finetune = args.epochs - n_warmup

    hf_fid_idx = train_full.fid_list.index(hf_fid)
    hf_m = float(train_full.t_list[hf_fid_idx])

    lf_tr_indices = [
        i for i in tr_ds.indices
        if abs(float(train_full.t_list[train_full.fid_id_by_record[i]]) - hf_m) > 1e-12
    ]
    lf_tr_loader = None
    if lf_tr_indices:
        lf_tr_loader = DataLoader(
            Subset(train_full, lf_tr_indices),
            batch_size=p["batch_size"], shuffle=True, num_workers=0,
        )

    ckpt_dir = Path(args.ckpt_dir); ckpt_dir.mkdir(parents=True, exist_ok=True)
    last_ckpt = ckpt_dir / "last.pt"
    best_ckpt = ckpt_dir / "best.pt"
    best_val = float("inf")

    # Resume guard: only a finished checkpoint (stage==2 AND epoch==epochs_target)
    # skips retraining. A stage-1-only checkpoint MUST not satisfy this guard.
    trained = False
    if last_ckpt.exists():
        try:
            sd = torch.load(last_ckpt, map_location=device, weights_only=False)
            if (sd.get("stage") == 2
                    and sd.get("epoch") == args.epochs
                    and sd.get("epochs_target") == args.epochs
                    and sd.get("grid") == list(grid)):
                ck_m = sd["model"].get("m_keys")
                ck_s = sd["model"].get("scalers")
                if ck_m is not None and ck_s is not None:
                    model.set_scalers(ck_m.cpu().tolist(), ck_s.cpu().tolist())
                model.load_state_dict(sd["model"])
                best_val = sd.get("best_val", float("inf"))
                trained = True
                print(f"[resume] finished checkpoint (stage 2, epoch {args.epochs}), "
                      f"best_val={best_val:.4e}")
        except Exception as e:
            print(f"[resume] failed ({e}) — starting fresh")

    def _save_last(stage: int, epoch: int):
        torch.save({
            "stage": stage, "epoch": epoch, "epochs_target": args.epochs,
            "grid": list(grid),
            "model": model.state_dict(),
            "best_val": best_val,
        }, last_ckpt)

    n_params = param_count(model)
    print(f"[start] {args.dataset_name} | params={n_params:,} | hf_grid={hf_grid} "
          f"work_grid={grid} modes=({modes_h},{modes_w}) width={p['hidden_channels']} | "
          f"n_train={n_tr} n_val={n_val} cond_dim={train_full.cond_dim} "
          f"m_keys={m_keys} scalers={[f'{s:.4g}' for s in scalers]} | "
          f"H2 schedule: n_warmup={n_warmup} (LF-only, lr={p['pretrain_lr']:.2g}) "
          f"n_finetune={n_finetune} (joint, lr={p['finetune_lr']:.2g}) "
          f"hf_m={hf_m:.4g} n_lf_train={len(lf_tr_indices)}")

    t_train = time.time()
    if not trained:
        # ─── Stage 1: LF-only warm-up ───
        if n_warmup > 0 and lf_tr_loader is not None:
            print(f"[stage 1] lf-only warmup: {n_warmup} epochs, "
                  f"lr={p['pretrain_lr']:.2g}, n_lf={len(lf_tr_indices)}")
            opt = torch.optim.Adam(model.parameters(),
                                   lr=p["pretrain_lr"], weight_decay=p["weight_decay"])
            sched = torch.optim.lr_scheduler.CosineAnnealingLR(
                opt, T_max=max(n_warmup, 1), eta_min=1e-6)
            for s1_epoch in range(1, n_warmup + 1):
                model.train()
                for X, y, m in lf_tr_loader:
                    X = X.to(device); y = y.to(device); m = m.to(device)
                    opt.zero_grad(set_to_none=True)
                    pred = model(X, m)
                    loss = ((pred - y) ** 2).mean()
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(model.parameters(), p["grad_clip"])
                    opt.step()
                sched.step()

                val_nrmse, _ = nrmse_over_loader(model, val_loader, device)
                if val_nrmse < best_val:
                    best_val = val_nrmse
                    torch.save({"model": model.state_dict()}, best_ckpt)
                if s1_epoch % p["ckpt_every"] == 0 or s1_epoch == n_warmup:
                    _save_last(stage=1, epoch=s1_epoch)
                    print(f"[stage 1 {s1_epoch:04d}/{n_warmup}] "
                          f"val_nRMSE={val_nrmse:.4e} best={best_val:.4e}")
        elif n_warmup > 0:
            print("[stage 1] skipped: no LF samples in training split "
                  "(single-fidelity dataset?)")

        # ─── Stage 2: joint fine-tune ───
        # FRESH optimizer + FRESH scheduler — Stage-1 momentum and schedule are
        # deliberately discarded at the boundary (see lyu2023mffno; stale
        # momentum is a documented cause of fine-tune divergence).
        if n_finetune > 0:
            print(f"[stage 2] joint fine-tune: {n_finetune} epochs, "
                  f"lr={p['finetune_lr']:.2g}")
            opt = torch.optim.Adam(model.parameters(),
                                   lr=p["finetune_lr"], weight_decay=p["weight_decay"])
            sched = torch.optim.lr_scheduler.CosineAnnealingLR(
                opt, T_max=max(n_finetune, 1), eta_min=1e-6)
            for s2_epoch in range(1, n_finetune + 1):
                model.train()
                for X, y, m in tr_loader:
                    X = X.to(device); y = y.to(device); m = m.to(device)
                    opt.zero_grad(set_to_none=True)
                    pred = model(X, m)
                    loss = ((pred - y) ** 2).mean()
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(model.parameters(), p["grad_clip"])
                    opt.step()
                sched.step()

                val_nrmse, _ = nrmse_over_loader(model, val_loader, device)
                if val_nrmse < best_val:
                    best_val = val_nrmse
                    torch.save({"model": model.state_dict()}, best_ckpt)
                global_epoch = n_warmup + s2_epoch
                if s2_epoch % p["ckpt_every"] == 0 or s2_epoch == n_finetune:
                    _save_last(stage=2, epoch=global_epoch)
                    print(f"[stage 2 {s2_epoch:04d}/{n_finetune}] "
                          f"val_nRMSE={val_nrmse:.4e} best={best_val:.4e}")
            # Final checkpoint at epoch==epochs_target satisfies the resume guard.
            _save_last(stage=2, epoch=args.epochs)
        else:
            # Pathological: epochs == n_warmup. Still mark stage 2 done.
            _save_last(stage=2, epoch=args.epochs)
    train_seconds = time.time() - t_train

    if best_ckpt.exists():
        model.load_state_dict(torch.load(best_ckpt, map_location=device)["model"])

    # Evaluation: HF-only on test/ood splits. test_hf full field -> finalize_and_write;
    # ood (if present) kept as an extra split.
    pred_full = np.zeros((0, 0), dtype=np.float32)
    target_full = np.zeros((0, 0), dtype=np.float32)
    ood_extra: dict = {}
    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()
        torch.cuda.synchronize()
    t_eval = time.time()
    for sub in ("test", "ood"):
        try:
            test_data = load_mf_dataset(ds_dir, split=sub)
        except (FileNotFoundError, ValueError):
            continue
        except Exception as e:
            if sub == "ood":
                ood_extra["ood_hf"] = {"error": str(e)}
            continue

        test_hf = test_data["hf_fid"]
        hf_only = dict(test_data)
        hf_only["fids"] = [test_hf]
        hf_only["cond_by_fid"] = {test_hf: test_data["cond_by_fid"][test_hf]}
        hf_only["field_by_fid"] = {test_hf: test_data["field_by_fid"][test_hf]}
        try:
            ds = AdapterMFDataset(hf_only, args.dataset_name, target_grid=grid)
        except Exception as e:
            if sub == "ood":
                ood_extra["ood_hf"] = {"error": str(e)}
            continue
        loader = DataLoader(ds, batch_size=p["batch_size"], shuffle=False, num_workers=0)
        if sub == "test":
            pred_full, target_full = fields_over_loader(model, loader, device)
        else:
            nrmse, n = nrmse_over_loader(model, loader, device)
            ood_extra["ood_hf"] = {"nRMSE": nrmse, "n_samples": n}
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    eval_seconds = time.time() - t_eval

    n_test = int(pred_full.shape[0])
    latency_ms = (1000.0 * eval_seconds / n_test) if n_test > 0 else None
    peak_mem_mb = (torch.cuda.max_memory_allocated() / 1e6
                   if torch.cuda.is_available() else None)

    extra = {
        "best_val_nRMSE": best_val,
        "device": str(device),
        "hf_grid": list(hf_grid),
        "modes": [int(modes_h), int(modes_w)],
        "notes": (
            f"H2: FNO+IFC coregionalization with two-stage LF→HF transfer training. "
            f"Stage 1: {n_warmup} LF-only epochs (lr={p['pretrain_lr']:.2g}, fresh Adam+cosine). "
            f"Stage 2: {n_finetune} joint epochs (lr={p['finetune_lr']:.2g}, fresh Adam+cosine). "
            f"K={p['K']}, blocks={p['n_blocks']}, modes=({modes_h},{modes_w}), "
            f"hidden={p['hidden_channels']}, hf_grid={hf_grid}, "
            f"work_grid={grid} (cap={WORK_CAP}), per-fidelity output "
            f"normalization (scalers={[f'{s:.4g}' for s in scalers]}). "
            f"Geometry via data_adapters.geometry.resolve_grid (1-D as height-1 grid)."
        ),
        "h2_stage1_epochs": int(n_warmup),
        "h2_stage2_epochs": int(n_finetune),
        "h2_pretrain_lr": float(p["pretrain_lr"]),
        "h2_finetune_lr": float(p["finetune_lr"]),
    }
    if ood_extra:
        extra["ood_splits"] = ood_extra

    res = finalize_and_write(
        out_path=Path(args.out),
        model="fno_coregionalization",
        dataset=args.dataset_name,
        pred=pred_full,
        target=target_full,
        work_grid=(int(grid[0]), int(grid[1])),
        n_params=int(n_params),
        train_seconds=train_seconds,
        eval_seconds=eval_seconds,
        latency_ms_per_sample=latency_ms,
        peak_mem_mb=peak_mem_mb,
        seed=args.seed,
        extra=extra,
    )
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset_dir", required=True)
    ap.add_argument("--dataset_name", required=True)
    ap.add_argument("--epochs", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ckpt_dir", required=True)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    # run() is the single writer (via finalize_and_write); don't re-write.
    run(args)
    print(f"[wrote] {out}")


if __name__ == "__main__":
    main()
