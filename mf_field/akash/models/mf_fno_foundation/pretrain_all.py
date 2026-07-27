"""BOUNDED cross-dataset foundation pretrain for FoundationFNO2d.

Iterates datasets under factory_mffp/data/*, loads each LF field, resamples to a
common working grid, and jointly pretrains the SHARED backbone + BPOM set-encoder
across all of them. Because the BPOM encoder maps any cond_dim -> a fixed
embedding, one set of weights serves every dataset.

This is a DEMO, kept small on purpose (few epochs, capped samples/dataset). It is
OPTIONAL: smoke_eval.py self-pretrains when pretrained.pt is absent. Each dataset
is wrapped in try/except and skipped on any failure.

Saves akash/models/mf_fno_foundation/pretrained.pt:
    {"shared": shared_state_dict, "grid": [H,W], "modes": [mh,mw],
     "hidden_channels", "n_blocks", "emb_dim", "datasets": [...]}

Run:
    factory_mffp/.venv/bin/python akash/models/mf_fno_foundation/pretrain_all.py \
        [--epochs 3] [--cap 128] [--max_datasets 6]
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

AKASH = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(AKASH))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from common.mffp import (load_mf_dataset, resolve_grid, SMOKE, _cap_grid,  # noqa: E402
                         _modes, _to_grid, FACTORY_ROOT)
from model import FoundationFNO2d, EMB_DIM, param_count  # noqa: E402

# A single common working grid for the shared backbone (all datasets resampled
# here so the spectral weights + grid are shared).
PRETRAIN_GRID = (64, 64)


def _gather_lf(ds_dir: Path, name: str, grid, cap: int):
    """Return (X, Y_grid) for this dataset's LF stage, capped to `cap` samples."""
    train = load_mf_dataset(ds_dir, "train")
    lf = min(train["lf_fids"]) if train["lf_fids"] else train["hf_fid"]
    lf_grid_native = resolve_grid(name, int(train["n_cells_by_fid"][lf]))
    X = train["cond_by_fid"][lf].astype(np.float32)
    Y = _to_grid(train["field_by_fid"][lf], lf_grid_native, grid)
    n = min(cap, X.shape[0])
    if n <= 0:
        raise ValueError("empty LF split")
    return X[:n], Y[:n], int(lf)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--cap", type=int, default=128)
    ap.add_argument("--max_datasets", type=int, default=8)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    torch.manual_seed(args.seed); np.random.seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    p = SMOKE
    grid = PRETRAIN_GRID
    mh, mw = _modes(grid, p["modes_cap"])

    data_root = FACTORY_ROOT / "data"
    bundles = []   # (name, X, Y, lf)
    for ds_dir in sorted(data_root.iterdir()):
        if not ds_dir.is_dir():
            continue
        if len(bundles) >= args.max_datasets:
            break
        try:
            X, Y, lf = _gather_lf(ds_dir, ds_dir.name, grid, args.cap)
            bundles.append((ds_dir.name, X, Y, lf))
            print(f"[load] {ds_dir.name:32s} N={X.shape[0]:4d} cond_dim={X.shape[1]:2d} lf={lf}", flush=True)
        except Exception as e:
            print(f"[skip] {ds_dir.name:32s} ({type(e).__name__}: {e})", flush=True)

    if not bundles:
        print("[pretrain_all] no datasets loaded; abort", flush=True)
        return

    model = FoundationFNO2d(hidden_channels=p["hidden_channels"], n_blocks=p["n_blocks"],
                            modes_h=mh, modes_w=mw, grid=grid, emb_dim=EMB_DIM).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=p["lr_pretrain"], weight_decay=p["weight_decay"])

    # Per-dataset scaler (max|Y|) so amplitudes don't dominate the joint loss.
    scalers = [max(float(np.abs(Y).max()), 1e-8) for (_, _, Y, _) in bundles]

    t0 = time.time()
    bs = p["batch_size"]
    for ep in range(args.epochs):
        model.train()
        order = np.random.permutation(len(bundles))
        ep_loss = 0.0; nb = 0
        for di in order:
            name, X, Y, lf = bundles[di]
            sc = scalers[di]
            Xt = torch.from_numpy(X).float()
            Yt = torch.from_numpy(Y).float() / sc
            n = X.shape[0]
            perm = torch.randperm(n)
            for i in range(0, n, bs):
                idx = perm[i:i + bs]
                xb = Xt[idx].to(device); yb = Yt[idx].to(device)
                opt.zero_grad(set_to_none=True)
                pred = model(xb)
                loss = F.mse_loss(pred, yb)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), p["grad_clip"])
                opt.step()
                ep_loss += float(loss.detach()); nb += 1
        print(f"[pretrain {ep+1}/{args.epochs}] mean_mse={ep_loss/max(nb,1):.4e}", flush=True)

    out = Path(__file__).resolve().parent / "pretrained.pt"
    torch.save({
        "shared": model.shared_state_dict(),
        "grid": list(grid), "modes": [mh, mw],
        "hidden_channels": p["hidden_channels"], "n_blocks": p["n_blocks"],
        "emb_dim": EMB_DIM,
        "datasets": [b[0] for b in bundles],
    }, out)
    print(f"[pretrain_all] {len(bundles)} datasets, {args.epochs} epochs, "
          f"{time.time()-t0:.1f}s, params={param_count(model)} -> {out}", flush=True)


if __name__ == "__main__":
    main()
