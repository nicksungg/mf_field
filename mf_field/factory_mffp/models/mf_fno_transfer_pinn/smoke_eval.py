"""Physics-informed transfer-learning FNO (FiLM conditioning) — PINN-transfer.

Identical to mf_fno_transfer_film (pretrain on LF, fine-tune on HF, FiLM-on-X)
EXCEPT the HF fine-tuning adds a PDE-operator-matching loss: for datasets with a
known elliptic operator L, we add lambda * ||L[u_pred] - L[u_hf]||^2 (scale-free).

At HF training points L[u]=-f (the source), so matching L[u_pred] to L[u_hf]
enforces the governing PDE exactly WITHOUT needing the analytic source — a
source-free, Sobolev-style physics constraint that supplies richer per-sample
supervision in the scarce-HF regime (the regime where transfer can overfit).

Operators (recovered/verified empirically from the data; mffpbench generators are
unavailable, so only the cleanly-recoverable ones are used):
  * laplacian  ∇²u           -> poisson_generated, poisson_local, ifc_poisson
  * darcy      ∇·(a(x)∇u)    -> darcy_generated  (a = exp(upsample of the 4x4 X field))
Every other dataset uses lambda=0 (== plain mf_fno_transfer_film), so the
comparison isolates the PHYSICS term on the datasets where it is valid.
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

WORK_CAP = 256
SMOKE = dict(hidden_channels=64, n_blocks=4, modes_cap=12, batch_size=16,
             lr_pretrain=1e-3, lr_finetune=3e-4, weight_decay=1e-5, grad_clip=1.0,
             lambda_pde=0.3)

# dataset -> elliptic operator with a cleanly recoverable form (verified on data)
PDE_KIND = {
    "poisson_generated": "laplacian", "poisson_local": "laplacian", "ifc_poisson": "laplacian",
    "darcy_generated": "darcy",
}

_LAP = torch.tensor([[0., 1., 0.], [1., -4., 1.], [0., 1., 0.]]).view(1, 1, 3, 3)


def _laplacian(u):  # u (B,H,W) -> (B,H,W); h absorbed (loss is scale-free)
    return F.conv2d(u.unsqueeze(1), _LAP.to(u.device), padding=1).squeeze(1)


def _darcy_div(u, a):  # ∇·(a ∇u), central differences (a: B,H,W)
    ux = torch.zeros_like(u); uy = torch.zeros_like(u)
    ux[:, 1:-1, 1:-1] = 0.5 * (u[:, 1:-1, 2:] - u[:, 1:-1, :-2])
    uy[:, 1:-1, 1:-1] = 0.5 * (u[:, 2:, 1:-1] - u[:, :-2, 1:-1])
    aux, auy = a * ux, a * uy
    div = torch.zeros_like(u)
    div[:, 1:-1, 1:-1] = (0.5 * (aux[:, 1:-1, 2:] - aux[:, 1:-1, :-2])
                          + 0.5 * (auy[:, 2:, 1:-1] - auy[:, :-2, 1:-1]))
    return div


def _operator(u, kind, a):
    return _darcy_div(u, a) if kind == "darcy" else _laplacian(u)


def _rel_pde_loss(pred, target, kind, a):
    """Scale-free interior PDE-operator matching loss."""
    Lp = _operator(pred, kind, a)[:, 1:-1, 1:-1]
    Lt = _operator(target, kind, a)[:, 1:-1, 1:-1]
    return ((Lp - Lt) ** 2).mean() / ((Lt ** 2).mean() + 1e-8)


def _cap_grid(grid, cap: int = WORK_CAP):
    H, W = int(grid[0]), int(grid[1]); m = max(H, W)
    if m <= cap:
        return (H, W)
    f = cap / m
    return (max(1, round(H * f)), max(1, round(W * f)))


def _modes(grid, cap):
    H, W = grid
    return (min(cap, max(H // 2, 1)), min(cap, W // 2 + 1))


def _to_grid(y_flat, src_grid, dst_grid):
    Hs, Ws = int(src_grid[0]), int(src_grid[1]); Hd, Wd = int(dst_grid[0]), int(dst_grid[1])
    t = torch.from_numpy(np.ascontiguousarray(y_flat, dtype=np.float32)).view(-1, 1, Hs, Ws)
    if (Hs, Ws) != (Hd, Wd):
        t = F.interpolate(t, size=(Hd, Wd), mode="bilinear", align_corners=False)
    return t.squeeze(1).numpy().astype(np.float32)


def _darcy_a(X, grid):
    """a = exp(upsample of the per-sample 4x4 log-permeability X) on the working grid."""
    B = X.shape[0]; r = int(round(X.shape[1] ** 0.5))
    a4 = torch.from_numpy(X.astype(np.float32)).view(B, 1, r, r)
    a = F.interpolate(a4, size=grid, mode="bilinear", align_corners=False).squeeze(1)
    return torch.exp(a)  # (B,H,W)


def _train(model, X, Y, scaler, epochs, lr, p, device, tag, kind=None, a_all=None):
    if X.shape[0] == 0 or epochs <= 0:
        return
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=p["weight_decay"])
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(epochs, 1), eta_min=1e-6)
    Xt = torch.from_numpy(X).float(); Yt = torch.from_numpy(Y).float() / scaler
    lam = p["lambda_pde"] if kind else 0.0
    n = X.shape[0]; bs = min(p["batch_size"], n); g = torch.Generator().manual_seed(0)
    for ep in range(epochs):
        model.train(); perm = torch.randperm(n, generator=g)
        for i in range(0, n, bs):
            idx = perm[i:i + bs]
            xb = Xt[idx].to(device); yb = Yt[idx].to(device)
            opt.zero_grad(set_to_none=True)
            pred = model(xb)
            loss = F.mse_loss(pred, yb)
            if lam > 0:
                a = a_all[idx].to(device) if a_all is not None else None
                loss = loss + lam * _rel_pde_loss(pred, yb, kind, a)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), p["grad_clip"]); opt.step()
        sched.step()


def run(args, out_path: Path) -> dict:
    torch.manual_seed(args.seed); np.random.seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    p = SMOKE
    ds_dir = Path(args.dataset_dir)
    train = load_mf_dataset(ds_dir, "train"); test = load_mf_dataset(ds_dir, "test")
    hf = train["hf_fid"]; lf = min(train["lf_fids"]) if train["lf_fids"] else hf
    if hf not in test["fids"]:
        hf = test["hf_fid"]
    hf_native = resolve_grid(args.dataset_name, int(train["n_cells_by_fid"][hf]))
    lf_native = resolve_grid(args.dataset_name, int(train["n_cells_by_fid"][lf]))
    grid = _cap_grid(hf_native); mh, mw = _modes(grid, p["modes_cap"])

    X_lf = train["cond_by_fid"][lf].astype(np.float32); Y_lf = _to_grid(train["field_by_fid"][lf], lf_native, grid)
    X_hf = train["cond_by_fid"][hf].astype(np.float32); Y_hf = _to_grid(train["field_by_fid"][hf], hf_native, grid)
    X_te = test["cond_by_fid"][hf].astype(np.float32); Y_te = _to_grid(test["field_by_fid"][hf], hf_native, grid)
    cond_dim = int(X_hf.shape[1])
    scaler_lf = max(float(np.abs(Y_lf).max()), 1e-8) if Y_lf.size else 1.0
    scaler_hf = max(float(np.abs(Y_hf).max()), 1e-8) if Y_hf.size else 1.0

    kind = PDE_KIND.get(args.dataset_name)
    a_hf = _darcy_a(X_hf, grid) if kind == "darcy" else None
    print(f"[data] {args.dataset_name} LF={lf} HF={hf} work_grid={grid} pde={kind or 'none'} "
          f"lambda={p['lambda_pde'] if kind else 0} N_lf={X_lf.shape[0]} N_hf={X_hf.shape[0]}", flush=True)

    model = FNO2d(cond_dim, hidden_channels=p["hidden_channels"], n_blocks=p["n_blocks"],
                  modes_h=mh, modes_w=mw, grid=grid).to(device)
    n_params = param_count(model)

    ckpt_dir = Path(args.ckpt_dir); ckpt_dir.mkdir(parents=True, exist_ok=True)
    last = ckpt_dir / "last.pt"; trained = False
    if last.exists():
        try:
            sd = torch.load(last, map_location=device, weights_only=False)
            if sd.get("epochs_target") == args.epochs and sd.get("grid") == list(grid):
                model.load_state_dict(sd["model"]); trained = True; print("[resume] loaded", flush=True)
        except Exception as e:
            print(f"[resume] failed ({e})", flush=True)

    t_train = time.time()
    if not trained:
        print(f"[stage] pretrain on LF ({X_lf.shape[0]})", flush=True)
        _train(model, X_lf, Y_lf, scaler_lf, args.epochs, p["lr_pretrain"], p, device, "LF")
        print(f"[stage] PINN fine-tune on HF ({X_hf.shape[0]}) pde={kind or 'none'}", flush=True)
        _train(model, X_hf, Y_hf, scaler_hf, args.epochs, p["lr_finetune"], p, device, "HF",
               kind=kind, a_all=a_hf)
        torch.save({"epochs_target": args.epochs, "grid": list(grid), "model": model.state_dict()}, last)
    train_seconds = time.time() - t_train

    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize()
    t_eval = time.time(); model.eval(); preds = []; bs = p["batch_size"]
    with torch.no_grad():
        for i in range(0, X_te.shape[0], bs):
            xb = torch.from_numpy(X_te[i:i + bs]).float().to(device)
            preds.append((model(xb) * scaler_hf).reshape(min(bs, X_te.shape[0] - i), -1).cpu().numpy())
    if device.type == "cuda":
        torch.cuda.synchronize()
    eval_seconds = time.time() - t_eval
    pred = np.concatenate(preds, 0).astype(np.float64); target = Y_te.reshape(Y_te.shape[0], -1).astype(np.float64)
    n = int(target.shape[0])
    latency = (1000.0 * eval_seconds / max(n, 1)) if device.type == "cuda" else None
    peak = (torch.cuda.max_memory_allocated() / 1e6) if device.type == "cuda" else None

    return finalize_and_write(
        out_path=out_path, model="mf_fno_transfer_pinn", dataset=args.dataset_name,
        pred=pred, target=target, work_grid=grid, n_params=int(n_params),
        train_seconds=train_seconds, eval_seconds=eval_seconds,
        latency_ms_per_sample=latency, peak_mem_mb=peak, seed=args.seed,
        extra={"device": str(device), "hf_fidelity": int(hf), "lf_fidelity": int(lf),
               "mf_mechanism": "transfer_learning_pretrain_LF_finetune_HF",
               "conditioning": "film_on_X_per_block",
               "physics": (kind or "none"), "lambda_pde": (p["lambda_pde"] if kind else 0.0),
               "hf_grid_native": list(hf_native), "work_grid": list(grid)},
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
