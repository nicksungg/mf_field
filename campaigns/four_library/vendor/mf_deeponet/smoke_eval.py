"""
Adapter: train + evaluate a Multifidelity DeepONet (Lu et al. 2022,
Phys. Rev. Research) on any factory_mffp dataset and emit the JSON expected by
../../../eval/MODEL_CONTRACT.md.

We follow the *residual + stacked-branch* MF recipe from the upstream
`src/poisson/deeponet_poisson.py`:

  - Branch input  = concat(x_HF_conditioning, vec(y_LF))       per sample
  - Trunk input   = HF grid coordinates                         shared across samples
  - Target        = y_HF - upsample(y_LF) on the HF grid        per sample (residual)

We use `deepxde.nn.DeepONetCartesianProd`, which evaluates each branch sample
at every trunk coordinate -- exactly our setup (one branch per sample, one
shared trunk grid).

Data is loaded via the unified `data_adapters.load_mf_dataset`, which returns
flat per-sample fields plus a `grid_shape_by_fid` metadata dict. This wrapper:

  - picks HF = `data["hf_fid"]` and LF = smallest of `data["lf_fids"]`;
  - reshapes LF/HF flat fields back to (N, H, W) using `grid_shape_by_fid`
    (2-D datasets) or (N, L) (1-D datasets);
  - upsamples LF to HF with bilinear (2-D) or linear (1-D) interpolation;
  - if `grid_shape_by_fid[hf_fid]` is None (truly irregular grid) the script
    exits 0 with `splits.test_hf.error` set -- DeepONet requires a structured
    trunk grid;
  - aligns LF rows to HF rows via nearest-neighbor lookup in standardized
    conditioning space (the IFC and several npz_l datasets have very different
    sample counts at LF vs HF, and the HF test split never ships companion LF
    data).

Resume: `<ckpt_dir>/last.pt` is written each call with
{epoch, epochs_target, model_state}; if `epochs_target == --epochs` we skip
training and go straight to eval. (DeepONet's `dde.Model.train` does not expose
per-step state cleanly, so we treat the whole `--epochs` value as one resumable
unit, matching how the contract uses resume on `preemptible_gpu`.)
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from pathlib import Path

# Cap BLAS thread pools BEFORE numpy/torch import to avoid pthread exhaustion
# on shared nodes (OpenBLAS defaults to physical core count, which trips
# RLIMIT_NPROC on multi-tenant systems).
os.environ.setdefault("OPENBLAS_NUM_THREADS", "4")
os.environ.setdefault("OMP_NUM_THREADS", "4")
os.environ.setdefault("MKL_NUM_THREADS", "4")

# DDE backend pin -- must be set BEFORE importing deepxde.
os.environ.setdefault("DDE_BACKEND", "pytorch")
os.environ["DDE_BACKEND"] = "pytorch"

import numpy as np
import torch
import torch.nn.functional as F

import deepxde as dde  # noqa: E402

# Make the factory_mffp data_adapters package importable. The smoke script
# lives at references/external_sota/mf_deeponet/smoke_eval.py; the repo root
# (factory_mffp/) is three levels up.
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from data_adapters import load_mf_dataset  # noqa: E402
from data_adapters.geometry import resolve_grid  # noqa: E402
from data_adapters.metrics import finalize_and_write  # noqa: E402


# Longest side of the working trunk grid. era5/pm_test are 721x1440 (~1.04M
# trunk coords) which is intractable for a Cartesian-product DeepONet; we cap
# the trunk/target to a 256-side working grid (no-op for every other dataset).
# This is a data-handling / hyperparameter choice — the DeepONet architecture
# (DeepONetCartesianProd, width/depth) is unchanged.
WORK_CAP = 256


def _cap_grid(grid, cap: int = WORK_CAP):
    """Downscale a 2-D (H, W) grid so its longest side is <= cap (no-op for 1-D
    or already-small grids)."""
    if not (grid is not None and len(grid) == 2):
        return grid
    H, W = int(grid[0]), int(grid[1])
    m = max(H, W)
    if m <= cap:
        return (H, W)
    f = cap / m
    return (max(1, round(H * f)), max(1, round(W * f)))


# ---------------------------------------------------------------------------
# Grid + upsampling utilities (1-D and 2-D).
# ---------------------------------------------------------------------------
def _is_2d(grid):
    return grid is not None and len(grid) == 2 and grid[0] > 0 and grid[1] > 0


def upsample_to_hf(y_lf_flat: np.ndarray, lf_grid, hf_grid) -> np.ndarray:
    """Upsample flat LF fields to the HF grid.

    y_lf_flat: (N, n_cells_lf)
    lf_grid:   (H_lf, W_lf) for 2-D, or (L_lf,) for 1-D.
    hf_grid:   same shape semantics.

    Returns (N, n_cells_hf) flat.
    """
    if _is_2d(lf_grid) and _is_2d(hf_grid):
        H_lf, W_lf = lf_grid
        H_hf, W_hf = hf_grid
        N = y_lf_flat.shape[0]
        t = torch.from_numpy(y_lf_flat).view(N, 1, H_lf, W_lf)
        t = F.interpolate(t, size=(H_hf, W_hf), mode="bilinear",
                          align_corners=False)
        return t.view(N, H_hf * W_hf).numpy()
    # 1-D path: lf/hf may be a 1-tuple (L,) (we produce these from
    # grid_shape_by_fid when n_cells is not a perfect square).
    L_lf = int(np.prod(lf_grid))
    L_hf = int(np.prod(hf_grid))
    N = y_lf_flat.shape[0]
    t = torch.from_numpy(y_lf_flat).view(N, 1, L_lf)
    t = F.interpolate(t, size=L_hf, mode="linear", align_corners=False)
    return t.view(N, L_hf).numpy()


def trunk_coords(grid) -> np.ndarray:
    """Generate trunk coordinates for the HF grid.

    2-D grid (H, W) -> (H*W, 2) xy in [0, 1]^2 (indexing='ij').
    1-D grid (L,)   -> (L, 1) x in [0, 1].
    """
    if _is_2d(grid):
        H, W = grid
        ax = np.linspace(0.0, 1.0, H, dtype=np.float32)
        ay = np.linspace(0.0, 1.0, W, dtype=np.float32)
        xx, yy = np.meshgrid(ax, ay, indexing="ij")
        return np.stack([xx.ravel(), yy.ravel()], axis=1)
    L = int(np.prod(grid))
    return np.linspace(0.0, 1.0, L, dtype=np.float32).reshape(L, 1)


def nn_lookup(query_cond: np.ndarray, ref_cond: np.ndarray) -> np.ndarray:
    """Nearest-neighbor index lookup in standardized cond space.

    Returns indices (Nq,) into ref_cond such that ref_cond[idx[i]] is closest
    to query_cond[i] (in standardized L2).
    """
    cm = ref_cond.mean(0, keepdims=True)
    cs = ref_cond.std(0, keepdims=True) + 1e-12
    a = (query_cond - cm) / cs
    b = (ref_cond - cm) / cs
    # block-wise to avoid the full (Nq, Nr) blowup on big sets
    Nq = a.shape[0]
    out = np.empty(Nq, dtype=np.int64)
    block = 1024
    for i in range(0, Nq, block):
        ai = a[i:i + block]
        d2 = ((ai[:, None, :] - b[None, :, :]) ** 2).sum(-1)
        out[i:i + block] = np.argmin(d2, axis=1)
    return out


# ---------------------------------------------------------------------------
# Skip-emit helper for irregular-grid datasets.
# ---------------------------------------------------------------------------
def _emit_skip(out_path: Path, args, reason: str) -> dict:
    res = {
        "model": "mf_deeponet",
        "dataset": args.dataset_name,
        "splits": {"test_hf": {"error": reason, "nRMSE": float("nan"),
                                "n_samples": 0}},
        "n_params": 0,
        "train_seconds": 0.0,
        "eval_seconds": 0.0,
        "device": "cpu",
        "notes": "skipped: deeponet requires structured grid",
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(res, indent=2))
    print(f"[skip] {reason}")
    print(f"[wrote] {out_path}")
    return res


# ---------------------------------------------------------------------------
# Run.
# ---------------------------------------------------------------------------
def run(args, out_path: Path):
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    random.seed(args.seed)
    dde.config.set_random_seed(args.seed)

    device = "cuda" if torch.cuda.is_available() else "cpu"

    ds_dir = Path(args.dataset_dir)

    # ── Load via the unified data adapter ────────────────────────────────
    train_data = load_mf_dataset(ds_dir, split="train")
    test_data = load_mf_dataset(ds_dir, split="test")

    if not train_data["lf_fids"]:
        return _emit_skip(out_path, args,
                          "deeponet requires at least one LF fidelity, none found")

    hf = train_data["hf_fid"]
    # smallest LF (most aggressive coarsening — matches Lu et al. spec)
    lf = min(train_data["lf_fids"])
    # If the test split's HF differs from train HF, fall back to test HF.
    if hf not in test_data["fids"]:
        hf = test_data["hf_fid"]

    # Resolve a concrete (H, W) for both fidelities via the geometry helper:
    # rectangular era5/pm_test, 1-D fields as (1, L), square otherwise. This
    # replaces the old reliance on grid_shape_by_fid (which was None for any
    # non-square n_cells), so DeepONet no longer skips era5/pm_test/1-D.
    hf_cells_native = int(train_data["n_cells_by_fid"][hf])
    lf_cells = int(train_data["n_cells_by_fid"][lf])
    hf_grid_native = resolve_grid(args.dataset_name, hf_cells_native)
    lf_grid = resolve_grid(args.dataset_name, lf_cells)
    # Cap the HF trunk/target to a 256-side working grid (no-op except era5/pm).
    hf_grid = _cap_grid(hf_grid_native)

    print(f"[data] loader={train_data['loader']} | train fidelities = "
          f"{train_data['fids']} | LF={lf} HF={hf}")
    print(f"[data] hf_grid={hf_grid} lf_grid={lf_grid}")

    # ── Materialize training pairs (HF cond + LF field per HF sample). ──
    x_hf_tr = train_data["cond_by_fid"][hf].astype(np.float32, copy=False)
    y_hf_tr = train_data["field_by_fid"][hf].astype(np.float32, copy=False)
    x_lf_all = train_data["cond_by_fid"][lf].astype(np.float32, copy=False)
    y_lf_all = train_data["field_by_fid"][lf].astype(np.float32, copy=False)
    # Resample the HF target field from its native grid to the (capped) working
    # grid so trunk coords, residual prior, and target all live on hf_grid.
    if hf_grid != hf_grid_native:
        y_hf_tr = upsample_to_hf(y_hf_tr, hf_grid_native, hf_grid).astype(np.float32)

    # Sample counts can differ across fidelities (ifc_heat HF=5, LF=100; era5
    # similar). We align by nearest-neighbor in standardized cond space.
    nn_tr = nn_lookup(x_hf_tr, x_lf_all)
    y_lf_tr = y_lf_all[nn_tr]  # (N_HF, n_cells_lf)

    # ── Test split: only HF; LF fields come from train-set NN lookup. ────
    x_hf_te = test_data["cond_by_fid"][hf].astype(np.float32, copy=False)
    y_hf_te = test_data["field_by_fid"][hf].astype(np.float32, copy=False)
    if hf_grid != hf_grid_native:
        y_hf_te = upsample_to_hf(y_hf_te, hf_grid_native, hf_grid).astype(np.float32)
    nn_te = nn_lookup(x_hf_te, x_lf_all)
    y_lf_te = y_lf_all[nn_te]  # (N_HF_te, n_cells_lf)

    n_cells_hf = int(np.prod(hf_grid))
    n_cells_lf = int(np.prod(lf_grid))
    cond_dim = int(x_hf_tr.shape[1])
    print(f"[data] HF cells={n_cells_hf} LF cells={n_cells_lf} "
          f"cond_dim={cond_dim} N_train={x_hf_tr.shape[0]} "
          f"N_test={x_hf_te.shape[0]}")

    # ── Residual targets: y_HF - upsample(y_LF) on the HF grid. ──────────
    y_lf_up_tr = upsample_to_hf(y_lf_tr, lf_grid, hf_grid)  # (N, n_cells_hf)
    y_lf_up_te = upsample_to_hf(y_lf_te, lf_grid, hf_grid)
    r_tr = y_hf_tr - y_lf_up_tr  # (N, n_cells_hf)
    r_te = y_hf_te - y_lf_up_te

    # ── Normalize: branch inputs and residual targets (train stats only). ─
    Xb_tr = np.hstack([x_hf_tr, y_lf_tr.reshape(y_lf_tr.shape[0], -1)])
    Xb_te = np.hstack([x_hf_te, y_lf_te.reshape(y_lf_te.shape[0], -1)])
    xb_mean = Xb_tr.mean(0, keepdims=True)
    xb_std = Xb_tr.std(0, keepdims=True) + 1e-6
    Xb_tr_n = (Xb_tr - xb_mean) / xb_std
    Xb_te_n = (Xb_te - xb_mean) / xb_std

    r_mean = r_tr.mean()
    r_std = r_tr.std() + 1e-12
    r_tr_n = (r_tr - r_mean) / r_std
    r_te_n = (r_te - r_mean) / r_std  # only for the val nRMSE print

    Xt = trunk_coords(hf_grid).astype(np.float32)  # (n_cells_hf, d_x)

    branch_in = Xb_tr_n.shape[1]
    trunk_in = Xt.shape[1]
    print(f"[shapes] branch_in={branch_in} trunk_in={trunk_in} "
          f"r_train={r_tr_n.shape} r_test={r_te_n.shape}")

    # ── Build DeepONet. ──────────────────────────────────────────────────
    width = 256
    depth = 5
    branch_layers = [branch_in] + [width] * depth
    trunk_layers = [trunk_in] + [width] * depth
    net = dde.nn.DeepONetCartesianProd(
        branch_layers,
        trunk_layers,
        activation="relu",
        kernel_initializer="Glorot normal",
    )

    # dde.data.TripleCartesianProd wants:
    #   X_train = (branch (N, m), trunk (P, d_x)), y_train (N, P)
    data = dde.data.TripleCartesianProd(
        X_train=(Xb_tr_n.astype(np.float32), Xt),
        y_train=r_tr_n.astype(np.float32),
        X_test=(Xb_te_n.astype(np.float32), Xt),
        y_test=r_te_n.astype(np.float32),
    )
    model = dde.Model(data, net)
    model.compile("adam", lr=1e-3, metrics=["mean l2 relative error"])

    n_total = sum(p.numel() for p in net.parameters())

    # ── Resume. ──────────────────────────────────────────────────────────
    # NOTE on --epochs mapping: deepxde's model.train(iterations=N) counts
    # gradient steps, not data-epochs. For this smoke test we map
    # `iterations = max(--epochs, args.epochs * 50)` so 2 epochs => 100 steps,
    # enough for a non-trivial signal in a few seconds.
    iterations = max(int(args.epochs), int(args.epochs) * 50)
    ckpt_dir = Path(args.ckpt_dir)
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    last_ckpt = ckpt_dir / "last.pt"
    do_train = True
    if last_ckpt.exists():
        sd = torch.load(last_ckpt, map_location=device)
        if sd.get("epochs_target") == int(args.epochs):
            net.load_state_dict(sd["model"])
            print(f"[resume] loaded checkpoint matching --epochs={args.epochs}")
            do_train = False

    t_train = time.time()
    if do_train:
        print(f"[train] iterations={iterations} (epochs={args.epochs})")
        model.train(iterations=iterations,
                    display_every=max(1, iterations // 4))
        torch.save({
            "epochs_target": int(args.epochs),
            "iterations": int(iterations),
            "model": net.state_dict(),
        }, last_ckpt)
    train_seconds = time.time() - t_train

    # ── Evaluate on HF test. ─────────────────────────────────────────────
    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()
        torch.cuda.synchronize()
    t_eval = time.time()
    pred_n = model.predict((Xb_te_n.astype(np.float32), Xt))
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    eval_seconds = time.time() - t_eval
    pred_n = np.asarray(pred_n)
    pred_residual = pred_n * r_std + r_mean  # de-normalize
    pred_full = pred_residual + y_lf_up_te  # add LF prior back
    n_samples = int(y_hf_te.shape[0])

    if torch.cuda.is_available():
        latency_ms_per_sample = 1000.0 * eval_seconds / max(n_samples, 1)
        peak_mem_mb = torch.cuda.max_memory_allocated() / 1e6
    else:
        latency_ms_per_sample = None
        peak_mem_mb = None

    return finalize_and_write(
        out_path=out_path,
        model="mf_deeponet",
        dataset=args.dataset_name,
        pred=pred_full,
        target=y_hf_te,
        work_grid=hf_grid,
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
            "iterations": int(iterations),
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
    # `run` writes the file itself: the skip path via _emit_skip, the normal
    # path via finalize_and_write. main() never writes (avoids double-write).
    res = run(args, out)
    print(f"[wrote] {out}")
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
