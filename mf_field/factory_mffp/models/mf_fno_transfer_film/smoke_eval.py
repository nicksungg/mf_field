"""Transfer-learning multi-fidelity FNO with FiLM conditioning on X.

Identical to `mf_fno_transfer_bar` (Lyu et al. 2023, Phys. Fluids,
arXiv:2304.06972; geological-carbon-storage MF-FNO, arXiv:2308.09113) in every
respect — backbone, transfer schedule, fair-eval plumbing — EXCEPT the model:
the condition vector X is injected via per-block FiLM affine modulation instead
of being concatenated as constant input channels (see model.py). This isolates
the CONDITIONING mechanism (concat vs FiLM) on top of the transfer-learning bar.

THE multi-fidelity mechanism = TRANSFER LEARNING, not residual / coregionalization:
  1. Pretrain a single FNO on the abundant LOW-fidelity data (its field resampled
     to the common working grid).
  2. Fine-tune the SAME network on the scarce HIGH-fidelity data (lower LR).
  3. Evaluate on the HF test split.

Shares the SAME fair-eval plumbing (resolve_grid + 256-cap working grid,
full-field eval, finalize_and_write with per-sample rel-L2 + bootstrap CI +
params/latency/mem) so the comparison isolates the CONDITIONING mechanism, not
the backbone or the metric.

Contract: --dataset_dir --dataset_name --epochs --out --ckpt_dir --seed.
--epochs is the HF fine-tune budget; LF pretraining uses the same budget (capped).
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

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model import FNO2d, param_count  # noqa: E402
from data_adapters import load_mf_dataset  # noqa: E402
from data_adapters.geometry import resolve_grid  # noqa: E402
from data_adapters.metrics import finalize_and_write  # noqa: E402

sys.path.insert(0, str(HERE.parent))  # models/ -> _common package
from _common.lf_registration import resample_fields  # noqa: E402

WORK_CAP = 256
SMOKE = dict(hidden_channels=64, n_blocks=4, modes_cap=12, batch_size=16,
             lr_pretrain=1e-3, lr_finetune=3e-4, weight_decay=1e-5, grad_clip=1.0)


def _cap_grid(grid, cap: int = WORK_CAP):
    H, W = int(grid[0]), int(grid[1])
    m = max(H, W)
    if m <= cap:
        return (H, W)
    f = cap / m
    return (max(1, round(H * f)), max(1, round(W * f)))


def _modes(grid, cap):
    H, W = grid
    return (min(cap, max(H // 2, 1)), min(cap, W // 2 + 1))


def _to_grid(y_flat: np.ndarray, src_grid, dst_grid, dataset_name: str) -> np.ndarray:
    """(N, prod(src)) flat -> (N, Hd, Wd) on the working grid, resampled
    under the dataset's registration convention (node-aligned for the sharp
    panel, Dirichlet interior-node for helmholtz, the historic cell-centred
    bilinear elsewhere — registration defect note item 1, ADR r2-0001)."""
    return resample_fields(y_flat, src_grid, dst_grid, dataset_name)


def _train(model, X, Y, scaler, epochs, lr, p, device, tag):
    """Train model on (X cond, Y field-on-grid). Y supervised in y/scaler space."""
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
    modes_h, modes_w = _modes(grid, p["modes_cap"])

    # LF training data: cond + field, field upsampled to the working grid.
    X_lf = train["cond_by_fid"][lf].astype(np.float32)
    Y_lf = _to_grid(train["field_by_fid"][lf], lf_grid_native, grid, args.dataset_name)
    # HF training data.
    X_hf = train["cond_by_fid"][hf].astype(np.float32)
    Y_hf = _to_grid(train["field_by_fid"][hf], hf_grid_native, grid, args.dataset_name)
    # HF test.
    X_te = test["cond_by_fid"][hf].astype(np.float32)
    Y_te = _to_grid(test["field_by_fid"][hf], hf_grid_native, grid, args.dataset_name)

    cond_dim = int(X_hf.shape[1])
    # Per-stage output scaler from that stage's training fields (max|y|).
    scaler_lf = max(float(np.abs(Y_lf).max()), 1e-8) if Y_lf.size else 1.0
    scaler_hf = max(float(np.abs(Y_hf).max()), 1e-8) if Y_hf.size else 1.0

    print(f"[data] {args.dataset_name} loader={train['loader']} LF={lf} HF={hf} "
          f"hf_native={hf_grid_native} work_grid={grid} modes=({modes_h},{modes_w}) "
          f"N_lf={X_lf.shape[0]} N_hf={X_hf.shape[0]} N_test={X_te.shape[0]} cond_dim={cond_dim}",
          flush=True)

    model = FNO2d(cond_dim, hidden_channels=p["hidden_channels"], n_blocks=p["n_blocks"],
                  modes_h=modes_h, modes_w=modes_w, grid=grid).to(device)
    n_params = param_count(model)

    # ── resume ──
    ckpt_dir = Path(args.ckpt_dir); ckpt_dir.mkdir(parents=True, exist_ok=True)
    last = ckpt_dir / "last.pt"
    trained = False
    if last.exists():
        try:
            sd = torch.load(last, map_location=device, weights_only=False)
            if sd.get("epochs_target") == args.epochs and sd.get("grid") == list(grid):
                model.load_state_dict(sd["model"]); trained = True
                print(f"[resume] loaded finished checkpoint", flush=True)
        except Exception as e:
            print(f"[resume] failed ({e}); fresh", flush=True)

    t_train = time.time()
    if not trained:
        # 1) PRETRAIN on low-fidelity (the abundant data)
        print(f"[stage] pretrain on LF ({X_lf.shape[0]} samples)", flush=True)
        _train(model, X_lf, Y_lf, scaler_lf, args.epochs, p["lr_pretrain"], p, device, "LF-pretrain")
        # 2) FINE-TUNE on high-fidelity (scarce), lower LR. Re-scale to HF stats:
        #    the network now predicts y/scaler_hf, so its LF-pretrained weights
        #    transfer the spatial structure; fine-tuning adapts amplitude+detail.
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
        out_path=out_path, model="mf_fno_transfer_film", dataset=args.dataset_name,
        pred=pred, target=target, work_grid=grid, n_params=int(n_params),
        train_seconds=train_seconds, eval_seconds=eval_seconds,
        latency_ms_per_sample=latency, peak_mem_mb=peak_mem, seed=args.seed,
        extra={"device": str(device), "hf_fidelity": int(hf), "lf_fidelity": int(lf),
               "mf_mechanism": "transfer_learning_pretrain_LF_finetune_HF",
               "conditioning": "film_on_X_per_block",
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
    run(args, out)
    print(f"[wrote] {out}", flush=True)


if __name__ == "__main__":
    main()
