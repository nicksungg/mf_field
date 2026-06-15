"""Physics-informed transfer-learning FNO (FiLM conditioning).

Identical to mf_fno_transfer_film (pretrain on LF, fine-tune on HF, FiLM on X) —
the strongest model in the benchmark — PLUS a PDE-residual loss during HF
fine-tuning on datasets whose governing equation is exactly recoverable.

Only the POISSON datasets qualify: the solution satisfies ∇²u = f(x) with u=0
Dirichlet, and the source f(x) is recovered EXACTLY (validated rel-L2 1e-7) as a
quadratic map of the condition vector, f(x) = W·[x, x², 1], fit in closed form
from the HF training fields' Laplacian. The physics loss enforces ∇²u_pred = f(x)
on the ABUNDANT LF inputs as collocation points (extra supervision the data-only
fine-tune never sees), plus the Dirichlet boundary. Every other dataset falls back
to plain FiLM-transfer (no physics term), so this isolates the PINN contribution.
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
# datasets where ∇²u = f(x) holds exactly and f is recoverable from x (validated)
PINN_POISSON = {"poisson_generated", "poisson_local"}
SMOKE = dict(hidden_channels=64, n_blocks=4, modes_cap=12, batch_size=16,
             lr_pretrain=1e-3, lr_finetune=3e-4, weight_decay=1e-5, grad_clip=1.0,
             lam_pde=0.1, lam_bc=0.1)


def _cap_grid(grid, cap=WORK_CAP):
    H, W = int(grid[0]), int(grid[1]); m = max(H, W)
    if m <= cap:
        return (H, W)
    f = cap / m
    return (max(1, round(H * f)), max(1, round(W * f)))


def _modes(grid, cap):
    H, W = grid
    return (min(cap, max(H // 2, 1)), min(cap, W // 2 + 1))


def _to_grid(y_flat, src, dst):
    Hs, Ws = int(src[0]), int(src[1]); Hd, Wd = int(dst[0]), int(dst[1])
    t = torch.from_numpy(np.ascontiguousarray(y_flat, dtype=np.float32)).view(-1, 1, Hs, Ws)
    if (Hs, Ws) != (Hd, Wd):
        t = F.interpolate(t, size=(Hd, Wd), mode="bilinear", align_corners=False)
    return t.squeeze(1).numpy().astype(np.float32)


def _train(model, X, Y, scaler, epochs, lr, p, device, tag):
    if X.shape[0] == 0 or epochs <= 0:
        return
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=p["weight_decay"])
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(epochs, 1), eta_min=1e-6)
    Xt = torch.from_numpy(X).float(); Yt = torch.from_numpy(Y).float() / scaler
    n = X.shape[0]; bs = min(p["batch_size"], n); g = torch.Generator().manual_seed(0)
    for _ in range(epochs):
        model.train()
        perm = torch.randperm(n, generator=g)
        for i in range(0, n, bs):
            idx = perm[i:i + bs]
            opt.zero_grad(set_to_none=True)
            loss = F.mse_loss(model(Xt[idx].to(device)), Yt[idx].to(device))
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), p["grad_clip"]); opt.step()
        sched.step()


# ── PINN pieces (Poisson) ───────────────────────────────────────────────
def _poly(X):
    return np.concatenate([X, X ** 2, np.ones((X.shape[0], 1), np.float32)], 1).astype(np.float32)


def _laplacian(u, h):  # u (B,R,R) -> (B,R-2,R-2)
    return (u[:, 2:, 1:-1] + u[:, :-2, 1:-1] + u[:, 1:-1, 2:] + u[:, 1:-1, :-2]
            - 4 * u[:, 1:-1, 1:-1]) / (h * h)


def _fit_forcing(X_hf, Y_hf, R, h):
    """Closed-form W: [x,x²,1] -> interior source field f=∇²u, fit on HF train."""
    u = Y_hf.reshape(-1, R, R)
    f = _laplacian(torch.from_numpy(u).float(), h).numpy().reshape(X_hf.shape[0], -1)
    A = _poly(X_hf)
    W, *_ = np.linalg.lstsq(A, f, rcond=None)
    f_scale = max(float(np.abs(f).max()), 1e-8)
    rel = float(np.linalg.norm(A @ W - f) / (np.linalg.norm(f) + 1e-12))
    return W.astype(np.float32), f_scale, rel  # W: (2*cond+1, (R-2)^2)


def _forcing(X, W, R):
    return (_poly(X) @ W).reshape(X.shape[0], R - 2, R - 2).astype(np.float32)


def _train_pinn(model, X_d, Y_d, scaler, X_c, f_c, f_scale, epochs, lr, p, device, h, R, tag):
    """HF fine-tune with data MSE + λ·PDE-residual on collocation + λ·Dirichlet BC."""
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=p["weight_decay"])
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(epochs, 1), eta_min=1e-6)
    Xt = torch.from_numpy(X_d).float(); Yt = torch.from_numpy(Y_d).float() / scaler
    Xct = torch.from_numpy(X_c).float(); fct = torch.from_numpy(f_c).float() / f_scale  # normalized f
    nd = X_d.shape[0]; nc = X_c.shape[0]; bs = min(p["batch_size"], nd)
    lam, lam_bc = p["lam_pde"], p["lam_bc"]
    g = torch.Generator().manual_seed(0)
    for _ in range(epochs):
        model.train()
        perm = torch.randperm(nd, generator=g); permc = torch.randperm(nc, generator=g)
        for bi, i in enumerate(range(0, nd, bs)):
            idx = perm[i:i + bs]
            cidx = permc[(bi * bs) % nc: (bi * bs) % nc + bs]
            if cidx.numel() == 0:
                cidx = permc[:bs]
            opt.zero_grad(set_to_none=True)
            data_loss = F.mse_loss(model(Xt[idx].to(device)), Yt[idx].to(device))
            uc = model(Xct[cidx].to(device))                       # scaled prediction
            lap = _laplacian(uc * scaler, h) / f_scale             # normalized ∇²u
            pde_loss = F.mse_loss(lap, fct[cidx].to(device))
            bc = torch.cat([uc[:, 0, :], uc[:, -1, :], uc[:, :, 0], uc[:, :, -1]], 1)
            bc_loss = (bc ** 2).mean()                             # Dirichlet u=0 (scaled space)
            loss = data_loss + lam * pde_loss + lam_bc * bc_loss
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

    # physics only on square Poisson grids where f(x) is exact
    use_pinn = (args.dataset_name in PINN_POISSON) and (grid[0] == grid[1])
    pinn_meta = {"pinn_enabled": bool(use_pinn)}
    R = grid[0]; h = 1.0 / (R - 1)
    if use_pinn:
        W, f_scale, rel = _fit_forcing(X_hf, Y_hf, R, h)
        # collocation = abundant LF inputs ∪ HF inputs; f computed exactly from x
        X_coll = np.concatenate([X_lf, X_hf], 0)
        f_coll = _forcing(X_coll, W, R)
        pinn_meta.update({"forcing_recovery_relL2": rel, "n_collocation": int(X_coll.shape[0]),
                          "lam_pde": p["lam_pde"], "lam_bc": p["lam_bc"]})
        if rel > 0.05:                # safety: if forcing isn't actually recoverable, disable
            use_pinn = False; pinn_meta["pinn_enabled"] = False
            pinn_meta["disabled_reason"] = f"forcing_relL2={rel:.3f}>0.05"

    print(f"[data] {args.dataset_name} LF={lf} HF={hf} grid={grid} N_lf={X_lf.shape[0]} "
          f"N_hf={X_hf.shape[0]} PINN={use_pinn}", flush=True)

    model = FNO2d(cond_dim, hidden_channels=p["hidden_channels"], n_blocks=p["n_blocks"],
                  modes_h=mh, modes_w=mw, grid=grid).to(device)
    n_params = param_count(model)
    ckpt_dir = Path(args.ckpt_dir); ckpt_dir.mkdir(parents=True, exist_ok=True)
    last = ckpt_dir / "last.pt"; trained = False
    if last.exists():
        try:
            sd = torch.load(last, map_location=device, weights_only=False)
            if sd.get("epochs_target") == args.epochs and sd.get("grid") == list(grid) and sd.get("pinn") == use_pinn:
                model.load_state_dict(sd["model"]); trained = True; print("[resume] loaded", flush=True)
        except Exception as e:
            print(f"[resume] failed ({e})", flush=True)

    t_train = time.time()
    if not trained:
        print(f"[stage] pretrain on LF ({X_lf.shape[0]})", flush=True)
        _train(model, X_lf, Y_lf, scaler_lf, args.epochs, p["lr_pretrain"], p, device, "LF")
        print(f"[stage] fine-tune on HF ({X_hf.shape[0]}) PINN={use_pinn}", flush=True)
        if use_pinn:
            _train_pinn(model, X_hf, Y_hf, scaler_hf, X_coll, f_coll, f_scale,
                        args.epochs, p["lr_finetune"], p, device, h, R, "HF-PINN")
        else:
            _train(model, X_hf, Y_hf, scaler_hf, args.epochs, p["lr_finetune"], p, device, "HF")
        torch.save({"epochs_target": args.epochs, "grid": list(grid), "pinn": use_pinn,
                    "model": model.state_dict()}, last)
    train_seconds = time.time() - t_train

    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize()
    t_eval = time.time(); model.eval(); preds = []
    with torch.no_grad():
        for i in range(0, X_te.shape[0], p["batch_size"]):
            xb = torch.from_numpy(X_te[i:i + p["batch_size"]]).float().to(device)
            preds.append((model(xb) * scaler_hf).reshape(xb.shape[0], -1).cpu().numpy())
    if device.type == "cuda":
        torch.cuda.synchronize()
    eval_seconds = time.time() - t_eval
    pred = np.concatenate(preds, 0).astype(np.float64); target = Y_te.reshape(Y_te.shape[0], -1).astype(np.float64)
    n = int(target.shape[0])
    latency = (1000.0 * eval_seconds / max(n, 1)) if device.type == "cuda" else None
    peak = (torch.cuda.max_memory_allocated() / 1e6) if device.type == "cuda" else None

    extra = {"device": str(device), "hf_fidelity": int(hf), "lf_fidelity": int(lf),
             "mf_mechanism": "PINN_transfer_pretrainLF_finetuneHF_with_PDE_residual",
             "conditioning": "film_on_X_per_block", "work_grid": list(grid)}
    extra.update(pinn_meta)
    return finalize_and_write(
        out_path=out_path, model="mf_fno_pinn_transfer", dataset=args.dataset_name,
        pred=pred, target=target, work_grid=grid, n_params=int(n_params),
        train_seconds=train_seconds, eval_seconds=eval_seconds,
        latency_ms_per_sample=latency, peak_mem_mb=peak, seed=args.seed, extra=extra)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset_dir", required=True); ap.add_argument("--dataset_name", required=True)
    ap.add_argument("--epochs", type=int, required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--ckpt_dir", required=True); ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    run(args, out); print("[wrote]", out, flush=True)


if __name__ == "__main__":
    main()
