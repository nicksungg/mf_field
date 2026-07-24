"""DG-FNO: discrepancy-gated residual learning on an FNO backbone.

Three stages (LF front-end identical to fno_fire_distcond, the FIRE keeper):
  1. LF inference:  train E independent FNOs on abundant LF data; per-pixel
       summaries mu_LF, sigma_LF, q10/q50/q90 as FIELDS.
  2. Gated residual:  r = HF - mu_LF; train DGOperator -> (delta, rho). The
       uncertainty fields MODULATE the operator (spatial FiLM + spectral mode-gate)
       instead of being concatenated, and the correction is gated:
       HF = mu_LF + rho(x) * delta. Trained with MSE(rho*delta, r / res_scaler).
  3. Predict + diagnostic:  HF = mu_LF + rho*delta; report corr(rho, |HF-mu_LF|).

Gates are selectable via the DG_GATES env var (default "A,B,C"); each is zero-init,
so the operator starts as an X-FiLM residual model and grows the gates.

Shares the verified plumbing (resolve_grid + 256-cap working grid, full-field eval,
finalize_and_write) so the comparison isolates the gating mechanism.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]            # factory_mffp/
sys.path.insert(0, str(HERE))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model import DGOperator, ALL_GATES, param_count  # noqa: E402
from data_adapters import load_mf_dataset  # noqa: E402
from data_adapters.geometry import resolve_grid  # noqa: E402
from data_adapters.metrics import finalize_and_write  # noqa: E402

# The LF ensemble front-end is the verified FIRE keeper backbone. Load it under a
# distinct module name so it does not collide with this family's own `model` module.
import importlib.util as _ilu  # noqa: E402
_fire_path = REPO_ROOT / "models" / "fno_fire_distcond" / "model.py"
_fire_spec = _ilu.spec_from_file_location("dg_fno_lf_member", _fire_path)
_fire_mod = _ilu.module_from_spec(_fire_spec)
_fire_spec.loader.exec_module(_fire_mod)
FNO2d = _fire_mod.FNO2d  # noqa: E402  (fno_fire_distcond plain FNO member)

WORK_CAP = 256
SMOKE = dict(hidden_channels=64, n_blocks=4, modes_cap=12, batch_size=16,
             lr=1e-3, weight_decay=1e-5, grad_clip=1.0,
             ensemble=5, quantiles=(0.1, 0.5, 0.9), gate_ch=16)
AUG_CH = 2 + 3   # [mu, sigma, q10, q50, q90]


def _parse_gates() -> frozenset:
    raw = os.environ.get("DG_GATES", "A,B,C")
    sel = {t.strip().upper() for t in raw.split(",") if t.strip()}
    return frozenset(sel & ALL_GATES)


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


def _train(model, X, target, scaler, epochs, lr, p, device, seed):
    """Train a plain FNO2d LF member: cond -> target/scaler (MSE)."""
    if X.shape[0] == 0 or epochs <= 0:
        return
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=p["weight_decay"])
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(epochs, 1), eta_min=1e-6)
    Xt = torch.from_numpy(X).float()
    Yt = torch.from_numpy(target).float() / scaler
    n = X.shape[0]; bs = min(p["batch_size"], n)
    g = torch.Generator().manual_seed(seed)
    for _ in range(epochs):
        model.train()
        perm = torch.randperm(n, generator=g)
        for i in range(0, n, bs):
            idx = perm[i:i + bs]
            xb = Xt[idx].to(device); yb = Yt[idx].to(device)
            opt.zero_grad(set_to_none=True)
            loss = F.mse_loss(model(xb), yb)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), p["grad_clip"])
            opt.step()
        sched.step()


def _train_dg(model, X, aug, target, scaler, epochs, lr, p, device, seed):
    """Train DGOperator: (cond, aug fields) -> rho*delta ~ target/scaler (MSE)."""
    if X.shape[0] == 0 or epochs <= 0:
        return
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=p["weight_decay"])
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(epochs, 1), eta_min=1e-6)
    Xt = torch.from_numpy(X).float()
    At = torch.from_numpy(aug).float()
    Yt = torch.from_numpy(target).float() / scaler
    n = X.shape[0]; bs = min(p["batch_size"], n)
    g = torch.Generator().manual_seed(seed)
    for _ in range(epochs):
        model.train()
        perm = torch.randperm(n, generator=g)
        for i in range(0, n, bs):
            idx = perm[i:i + bs]
            xb = Xt[idx].to(device); ab = At[idx].to(device); yb = Yt[idx].to(device)
            opt.zero_grad(set_to_none=True)
            delta, rho = model(xb, ab)
            loss = F.mse_loss(rho * delta, yb)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), p["grad_clip"])
            opt.step()
        sched.step()


@torch.no_grad()
def _member_fields(model, X, scaler, device, bs):
    """Raw-units field predictions (N, H, W) for one ensemble member."""
    model.eval()
    out = []
    for i in range(0, X.shape[0], bs):
        xb = torch.from_numpy(X[i:i + bs]).float().to(device)
        out.append((model(xb) * scaler).cpu().numpy())
    return np.concatenate(out, 0).astype(np.float32)


@torch.no_grad()
def _dg_predict(model, X, aug, scaler, device, bs):
    """Return (delta*rho in raw units, rho field) as (N,H,W) each."""
    model.eval()
    d_out, r_out = [], []
    for i in range(0, X.shape[0], bs):
        xb = torch.from_numpy(X[i:i + bs]).float().to(device)
        ab = torch.from_numpy(aug[i:i + bs]).float().to(device)
        delta, rho = model(xb, ab)
        d_out.append(((rho * delta) * scaler).cpu().numpy())
        r_out.append(rho.cpu().numpy())
    return (np.concatenate(d_out, 0).astype(np.float32),
            np.concatenate(r_out, 0).astype(np.float32))


def _lf_summaries(members, X, s_lf, device, bs, quantiles):
    """Stack member fields -> (mu, var, aug). aug=[mu,sigma,q10,q50,q90]/s_lf."""
    preds = np.stack([_member_fields(m, X, s_lf, device, bs) for m in members], 0)  # (E,N,H,W)
    mu = preds.mean(0)
    var = preds.var(0)
    sigma = np.sqrt(var + 1e-12)
    qs = [np.quantile(preds, q, axis=0) for q in quantiles]
    chans = [mu, sigma] + qs
    aug = np.stack([c / s_lf for c in chans], axis=1).astype(np.float32)            # (N,AUG_CH,H,W)
    return mu.astype(np.float32), var.astype(np.float32), aug


def run(args, out_path: Path) -> dict:
    torch.manual_seed(args.seed); np.random.seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    p = SMOKE
    E = int(p["ensemble"]); quants = p["quantiles"]
    gates = _parse_gates()
    ds_dir = Path(args.dataset_dir)
    train = load_mf_dataset(ds_dir, "train"); test = load_mf_dataset(ds_dir, "test")
    hf = train["hf_fid"]; lf = min(train["lf_fids"]) if train["lf_fids"] else hf
    if hf not in test["fids"]:
        hf = test["hf_fid"]

    hf_native = resolve_grid(args.dataset_name, int(train["n_cells_by_fid"][hf]))
    lf_native = resolve_grid(args.dataset_name, int(train["n_cells_by_fid"][lf]))
    grid = _cap_grid(hf_native); mh, mw = _modes(grid, p["modes_cap"])

    X_lf = train["cond_by_fid"][lf].astype(np.float32)
    Y_lf = _to_grid(train["field_by_fid"][lf], lf_native, grid)
    X_hf = train["cond_by_fid"][hf].astype(np.float32)
    Y_hf = _to_grid(train["field_by_fid"][hf], hf_native, grid)
    X_te = test["cond_by_fid"][hf].astype(np.float32)
    Y_te = _to_grid(test["field_by_fid"][hf], hf_native, grid)
    cond_dim = int(X_hf.shape[1])
    s_lf = max(float(np.abs(Y_lf).max()), 1e-8) if Y_lf.size else 1.0

    print(f"[data] {args.dataset_name} LF={lf} HF={hf} work_grid={grid} E={E} "
          f"gates={sorted(gates)} N_lf={X_lf.shape[0]} N_hf={X_hf.shape[0]} "
          f"N_test={X_te.shape[0]}", flush=True)

    members = [FNO2d(cond_dim, p["hidden_channels"], p["n_blocks"], mh, mw, grid).to(device)
               for _ in range(E)]
    dg = DGOperator(cond_dim, AUG_CH, p["gate_ch"], p["hidden_channels"], p["n_blocks"],
                    mh, mw, grid, gates=gates).to(device)
    n_params = sum(param_count(m) for m in members) + param_count(dg)

    ckpt_dir = Path(args.ckpt_dir); ckpt_dir.mkdir(parents=True, exist_ok=True)
    last = ckpt_dir / "last.pt"
    trained = False; res_scaler = 1.0
    if last.exists():
        try:
            sd = torch.load(last, map_location=device, weights_only=False)
            if sd.get("epochs_target") == args.epochs and sd.get("grid") == list(grid) \
               and sd.get("ensemble") == E and sd.get("gates") == sorted(gates):
                for m, msd in zip(members, sd["members"]):
                    m.load_state_dict(msd)
                dg.load_state_dict(sd["dg"])
                res_scaler = sd.get("res_scaler", 1.0); trained = True
                print("[resume] loaded", flush=True)
        except Exception as e:
            print(f"[resume] failed ({e})", flush=True)

    t_train = time.time()
    if not trained:
        # 1) LF ensemble on abundant LF data (independent seeds -> predictive spread)
        for i, m in enumerate(members):
            print(f"[stage1] train LF member {i + 1}/{E}", flush=True)
            _train(m, X_lf, Y_lf, s_lf, args.epochs, p["lr"], p, device, seed=args.seed + 1 + i)
        mu_hf, _, aug_hf = _lf_summaries(members, X_hf, s_lf, device, p["batch_size"], quants)
        residual = (Y_hf - mu_hf).astype(np.float32)
        res_scaler = max(float(np.abs(residual).max()), 1e-8) if residual.size else 1.0
        # 2) gated distribution-conditioned residual operator
        print("[stage2] train DGOperator on (HF - mu_LF) | gated aug", flush=True)
        _train_dg(dg, X_hf, aug_hf, residual, res_scaler, args.epochs, p["lr"], p,
                  device, seed=args.seed)
        torch.save({"epochs_target": args.epochs, "grid": list(grid), "ensemble": E,
                    "gates": sorted(gates), "members": [m.state_dict() for m in members],
                    "dg": dg.state_dict(), "res_scaler": res_scaler}, last)
    train_seconds = time.time() - t_train

    # 3) predict + diagnostic on test
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize()
    t_eval = time.time()
    mu_te, var_te, aug_te = _lf_summaries(members, X_te, s_lf, device, p["batch_size"], quants)
    d_te, rho_te = _dg_predict(dg, X_te, aug_te, res_scaler, device, p["batch_size"])
    pred = (mu_te + d_te).reshape(X_te.shape[0], -1).astype(np.float64)
    if device.type == "cuda":
        torch.cuda.synchronize()
    eval_seconds = time.time() - t_eval
    target = Y_te.reshape(Y_te.shape[0], -1).astype(np.float64)
    n = int(target.shape[0])
    latency = (1000.0 * eval_seconds / max(n, 1)) if device.type == "cuda" else None
    peak = (torch.cuda.max_memory_allocated() / 1e6) if device.type == "cuda" else None

    # Diagnostic: does the learned gain field rho(x) locate the LF->HF discrepancy?
    rho_corr = None
    if "C" in gates:
        rho_flat = rho_te.reshape(-1).astype(np.float64)
        err_flat = np.abs((Y_te - mu_te).reshape(-1)).astype(np.float64)
        if rho_flat.std() > 1e-12 and err_flat.std() > 1e-12:
            rho_corr = float(np.corrcoef(rho_flat, err_flat)[0, 1])

    return finalize_and_write(
        out_path=out_path, model="dg_fno", dataset=args.dataset_name,
        pred=pred, target=target, work_grid=grid, n_params=int(n_params),
        train_seconds=train_seconds, eval_seconds=eval_seconds,
        latency_ms_per_sample=latency, peak_mem_mb=peak, seed=args.seed,
        extra={"device": str(device), "hf_fidelity": int(hf), "lf_fidelity": int(lf),
               "mf_mechanism": "DG-FNO_gated_residual_HF=muLF+rho(x)*delta(gated_aug)",
               "ensemble_size": E, "gates": sorted(gates),
               "aug_channels": ["mu", "sigma", "q10", "q50", "q90"],
               "rho_mean": float(rho_te.mean()), "rho_err_corr": rho_corr,
               "work_grid": list(grid)},
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
