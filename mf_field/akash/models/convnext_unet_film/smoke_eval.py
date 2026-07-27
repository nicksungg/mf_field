"""Smoke + fair-eval for convnext_unet_film.

The benchmark-winning FNO+FiLM-transfer recipe with the ONLY change being the
backbone: the Fourier/FNO backbone -> a ConvNeXt-U-Net (encoder-decoder CNN with
ConvNeXt blocks; see model.py). Conditioning (per-block FiLM on X) and the
multi-fidelity mechanism (LF-pretrain -> HF-finetune transfer) are byte-for-byte
the winner, so the comparison isolates the backbone.

THE multi-fidelity mechanism = TRANSFER LEARNING:
  1. Pretrain one ConvNeXt-U-Net on the abundant LOW-fidelity data (resampled to
     the working grid).
  2. Fine-tune the SAME net on the scarce HIGH-fidelity data (lower LR).
  3. Evaluate on the HF test split.

Contract: --dataset_dir --dataset_name --epochs --out --ckpt_dir --seed.
--epochs is the HF fine-tune budget; LF pretraining uses the same budget.
Resume: ckpt_dir/last.pt keyed on (epochs_target, grid).
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

AKASH = Path(__file__).resolve().parents[2]                 # …/mf_field/akash
sys.path.insert(0, str(AKASH))
sys.path.insert(0, str(Path(__file__).resolve().parent))    # local model.py

from common.backbone import FiLMNorm, param_count  # noqa: E402,F401
from common.mffp import (load_mf_dataset, resolve_grid, finalize_and_write,  # noqa: E402
                         WORK_CAP, SMOKE, _cap_grid, _modes, _to_grid, FACTORY_ROOT)  # noqa: F401
from model import ConvNeXtUNet2d  # noqa: E402


def _train(model, X, Y, scaler, epochs, lr, p, device, tag):
    """Train model on (X cond, Y field-on-grid), supervised in y/scaler space."""
    if X.shape[0] == 0 or epochs <= 0:
        return
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=p["weight_decay"])
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(epochs, 1), eta_min=1e-6)
    Xt = torch.from_numpy(X).float()
    Yt = torch.from_numpy(Y).float() / scaler
    n = X.shape[0]
    bs = min(p["batch_size"], n)
    g = torch.Generator().manual_seed(0)
    for ep in range(epochs):
        model.train()
        perm = torch.randperm(n, generator=g)
        tot = 0.0
        for i in range(0, n, bs):
            idx = perm[i:i + bs]
            xb = Xt[idx].to(device); yb = Yt[idx].to(device)
            opt.zero_grad(set_to_none=True)
            pred = model(xb)
            loss = F.mse_loss(pred, yb)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), p["grad_clip"])
            opt.step()
            tot += float(loss.detach())
        sched.step()
        if (ep + 1) % max(1, epochs // 5) == 0 or ep == epochs - 1:
            print(f"[{tag} {ep+1:04d}/{epochs}] mse={tot/max(1,(n+bs-1)//bs):.4e}", flush=True)


def run(args, out_path: Path) -> dict:
    torch.manual_seed(args.seed); np.random.seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    p = SMOKE
    ds_dir = Path(args.dataset_dir)

    train = load_mf_dataset(ds_dir, "train")
    test = load_mf_dataset(ds_dir, "test")
    hf = train["hf_fid"]
    lf = min(train["lf_fids"]) if train["lf_fids"] else hf
    if hf not in test["fids"]:
        hf = test["hf_fid"]

    hf_grid_native = resolve_grid(args.dataset_name, int(train["n_cells_by_fid"][hf]))
    lf_grid_native = resolve_grid(args.dataset_name, int(train["n_cells_by_fid"][lf]))
    grid = _cap_grid(hf_grid_native)               # common working grid (256-cap)

    # LF / HF / test fields resampled to the working grid.
    X_lf = train["cond_by_fid"][lf].astype(np.float32)
    Y_lf = _to_grid(train["field_by_fid"][lf], lf_grid_native, grid)
    X_hf = train["cond_by_fid"][hf].astype(np.float32)
    Y_hf = _to_grid(train["field_by_fid"][hf], hf_grid_native, grid)
    X_te = test["cond_by_fid"][hf].astype(np.float32)
    Y_te = _to_grid(test["field_by_fid"][hf], hf_grid_native, grid)

    cond_dim = int(X_hf.shape[1])
    scaler_lf = max(float(np.abs(Y_lf).max()), 1e-8) if Y_lf.size else 1.0
    scaler_hf = max(float(np.abs(Y_hf).max()), 1e-8) if Y_hf.size else 1.0

    print(f"[data] {args.dataset_name} loader={train['loader']} LF={lf} HF={hf} "
          f"hf_native={hf_grid_native} work_grid={grid} "
          f"N_lf={X_lf.shape[0]} N_hf={X_hf.shape[0]} N_test={X_te.shape[0]} cond_dim={cond_dim} "
          f"ndim={'1D' if grid[0]==1 else '2D'}", flush=True)

    model = ConvNeXtUNet2d(cond_dim, base=48, n_levels=3, blocks_per_stage=2,
                           grid=grid).to(device)
    n_params = param_count(model)

    # sanity: a forward pass must preserve the working-grid shape (esp. H==1 in 1-D)
    with torch.no_grad():
        probe = model(torch.from_numpy(X_hf[:1]).float().to(device))
    assert tuple(probe.shape) == (1, grid[0], grid[1]), \
        f"output shape {tuple(probe.shape)} != (1,{grid[0]},{grid[1]}); U-Net broke the grid"
    print(f"[shape-check] forward output {tuple(probe.shape)} == (1,{grid[0]},{grid[1]}) OK "
          f"(height axis {'H==1 survived' if grid[0]==1 else 'H>1'})", flush=True)

    # ── resume ──
    ckpt_dir = Path(args.ckpt_dir); ckpt_dir.mkdir(parents=True, exist_ok=True)
    last = ckpt_dir / "last.pt"
    trained = False
    if last.exists():
        try:
            sd = torch.load(last, map_location=device, weights_only=False)
            if sd.get("epochs_target") == args.epochs and sd.get("grid") == list(grid):
                model.load_state_dict(sd["model"]); trained = True
                print("[resume] loaded finished checkpoint", flush=True)
        except Exception as e:
            print(f"[resume] failed ({e}); fresh", flush=True)

    t_train = time.time()
    if not trained:
        print(f"[stage] pretrain on LF ({X_lf.shape[0]} samples)", flush=True)
        _train(model, X_lf, Y_lf, scaler_lf, args.epochs, p["lr_pretrain"], p, device, "LF-pretrain")
        print(f"[stage] fine-tune on HF ({X_hf.shape[0]} samples)", flush=True)
        _train(model, X_hf, Y_hf, scaler_hf, args.epochs, p["lr_finetune"], p, device, "HF-finetune")
        torch.save({"epochs_target": args.epochs, "grid": list(grid),
                    "model": model.state_dict()}, last)
    train_seconds = time.time() - t_train

    # ── eval: full HF field on the working grid ──
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize()
    t_eval = time.time()
    model.eval()
    preds = []
    bs = p["batch_size"]
    with torch.no_grad():
        for i in range(0, X_te.shape[0], bs):
            xb = torch.from_numpy(X_te[i:i + bs]).float().to(device)
            pr = model(xb) * scaler_hf                      # de-normalize to raw units
            preds.append(pr.reshape(pr.shape[0], -1).cpu().numpy())
    if device.type == "cuda":
        torch.cuda.synchronize()
    eval_seconds = time.time() - t_eval
    pred = np.concatenate(preds, 0).astype(np.float64)
    target = Y_te.reshape(Y_te.shape[0], -1).astype(np.float64)
    n_samples = int(target.shape[0])
    latency = (1000.0 * eval_seconds / max(n_samples, 1)) if device.type == "cuda" else None
    peak_mem = (torch.cuda.max_memory_allocated() / 1e6) if device.type == "cuda" else None

    return finalize_and_write(
        out_path=out_path, model="convnext_unet_film", dataset=args.dataset_name,
        pred=pred, target=target, work_grid=grid, n_params=int(n_params),
        train_seconds=train_seconds, eval_seconds=eval_seconds,
        latency_ms_per_sample=latency, peak_mem_mb=peak_mem, seed=args.seed,
        extra={"device": str(device), "hf_fidelity": int(hf), "lf_fidelity": int(lf),
               "mf_mechanism": "transfer_learning_pretrain_LF_finetune_HF",
               "conditioning": "film_on_X_per_block",
               "backbone": "convnext_unet_3level",
               "hf_grid_native": list(hf_grid_native), "work_grid": list(grid)},
    )


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
    res = run(args, out)
    print(f"[wrote] {out}", flush=True)
    print(f"[nRMSE] {res['splits']['test_hf']['nRMSE']:.6f}", flush=True)


if __name__ == "__main__":
    main()
