"""FIRE-style distribution-conditioned residual learning (FNO backbone).

Field analog of FIRE (Yu, Sung & Ahmed 2026, arXiv:2601.22371). FIRE conditions
the HF correction on the LF model's posterior-predictive distribution (mean,
variance, quantiles) instead of the LF mean alone, so it handles spatially
heteroscedastic cross-fidelity discrepancy. We replace FIRE's tabular foundation
model (TabPFN) — which has no field equivalent and no pretraining here — with a
deep ENSEMBLE of FNOs that supplies the same distributional summaries as per-pixel
FIELDS.

Three stages (cf. FIRE Algorithm 1):
  1. LF inference:  train E independent FNOs on the abundant LF data. At any input,
       μ_LF = mean over members, σ_LF = std, q_τ = ensemble quantiles (τ∈{.1,.5,.9}).
  2. Distribution-conditioned residual:  r = HF - μ_LF(x_hf); train FNO_δ whose input
       is [cond x, coords, μ_LF, σ_LF, q10, q50, q90] (the LF summary FIELDS).
  3. Prediction + UQ:  ŷ = μ_LF(x*) + δ(x*, aug*);  σ²_total = σ²_LF + (δ is a point
       estimate here, so the reported predictive variance is the LF ensemble variance).

Contrast with fno_additive (HF = LF_pred + δ): identical additive decomposition, but
δ here is CONDITIONED ON the LF uncertainty field, not blind to it. Shares the verified
plumbing (resolve_grid + 256-cap working grid, full-field eval, finalize_and_write).
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
REPO_ROOT = HERE.parents[1]            # factory_mffp/
sys.path.insert(0, str(HERE))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model import FNO2d, FNO2dAug, param_count  # noqa: E402
from data_adapters import load_mf_dataset  # noqa: E402
from data_adapters.geometry import resolve_grid  # noqa: E402
from data_adapters.metrics import finalize_and_write  # noqa: E402

WORK_CAP = 256
SMOKE = dict(hidden_channels=64, n_blocks=4, modes_cap=12, batch_size=16,
             lr=1e-3, weight_decay=1e-5, grad_clip=1.0,
             ensemble=5, quantiles=(0.1, 0.5, 0.9))
AUG_CH = 2 + 3   # [mu, sigma, q10, q50, q90]


def _cap_grid(grid, cap=WORK_CAP):
    H, W = int(grid[0]), int(grid[1]); m = max(H, W)
    if m <= cap:
        return (H, W)
    f = cap / m
    return (max(1, round(H * f)), max(1, round(W * f)))


def _modes(grid, cap):
    H, W = grid
    return (min(cap, max(H // 2, 1)), min(cap, W // 2 + 1))


sys.path.insert(0, str(HERE.parent))  # models/ -> _common package
from _common.lf_registration import resample_fields  # noqa: E402


def _to_grid(y_flat, src, dst, dataset_name):
    """Resample under the dataset's registration convention
    (models/_common/lf_registration.py; registration defect note item 1)."""
    return resample_fields(y_flat, src, dst, dataset_name)


def _train(model, X, target, scaler, epochs, lr, p, device, seed):
    """Train a plain FNO2d: cond -> target/scaler (MSE)."""
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


def _train_aug(model, X, aug, target, scaler, epochs, lr, p, device, seed):
    """Train FNO2dAug: (cond, aug fields) -> target/scaler (MSE)."""
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
            loss = F.mse_loss(model(xb, ab), yb)
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
def _aug_predict(model, X, aug, scaler, device, bs):
    model.eval()
    out = []
    for i in range(0, X.shape[0], bs):
        xb = torch.from_numpy(X[i:i + bs]).float().to(device)
        ab = torch.from_numpy(aug[i:i + bs]).float().to(device)
        out.append((model(xb, ab) * scaler).cpu().numpy())
    return np.concatenate(out, 0).astype(np.float32)


def _lf_summaries(members, X, s_lf, device, bs, quantiles):
    """Stack ensemble member fields and return (mu, var, aug) for inputs X.

    mu, var : (N, H, W) raw units.  aug : (N, AUG_CH, H, W) normalized by s_lf —
    channels [mu, sigma, q_τ...]. Normalizing keeps the δ-model's extra inputs O(1).
    """
    preds = np.stack([_member_fields(m, X, s_lf, device, bs) for m in members], 0)  # (E,N,H,W)
    mu = preds.mean(0)
    var = preds.var(0)
    sigma = np.sqrt(var + 1e-12)
    qs = [np.quantile(preds, q, axis=0) for q in quantiles]                          # each (N,H,W)
    chans = [mu, sigma] + qs
    aug = np.stack([c / s_lf for c in chans], axis=1).astype(np.float32)             # (N,AUG_CH,H,W)
    return mu.astype(np.float32), var.astype(np.float32), aug


def run(args, out_path: Path) -> dict:
    torch.manual_seed(args.seed); np.random.seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    p = SMOKE
    E = int(p["ensemble"]); quants = p["quantiles"]
    ds_dir = Path(args.dataset_dir)
    train = load_mf_dataset(ds_dir, "train"); test = load_mf_dataset(ds_dir, "test")
    hf = train["hf_fid"]; lf = min(train["lf_fids"]) if train["lf_fids"] else hf
    if hf not in test["fids"]:
        hf = test["hf_fid"]

    hf_native = resolve_grid(args.dataset_name, int(train["n_cells_by_fid"][hf]))
    lf_native = resolve_grid(args.dataset_name, int(train["n_cells_by_fid"][lf]))
    grid = _cap_grid(hf_native); mh, mw = _modes(grid, p["modes_cap"])

    X_lf = train["cond_by_fid"][lf].astype(np.float32)
    Y_lf = _to_grid(train["field_by_fid"][lf], lf_native, grid, args.dataset_name)
    X_hf = train["cond_by_fid"][hf].astype(np.float32)
    Y_hf = _to_grid(train["field_by_fid"][hf], hf_native, grid, args.dataset_name)
    X_te = test["cond_by_fid"][hf].astype(np.float32)
    Y_te = _to_grid(test["field_by_fid"][hf], hf_native, grid, args.dataset_name)
    cond_dim = int(X_hf.shape[1])
    s_lf = max(float(np.abs(Y_lf).max()), 1e-8) if Y_lf.size else 1.0

    print(f"[data] {args.dataset_name} LF={lf} HF={hf} work_grid={grid} E={E} "
          f"N_lf={X_lf.shape[0]} N_hf={X_hf.shape[0]} N_test={X_te.shape[0]}", flush=True)

    members = [FNO2d(cond_dim, p["hidden_channels"], p["n_blocks"], mh, mw, grid).to(device)
               for _ in range(E)]
    fno_d = FNO2dAug(cond_dim, AUG_CH, p["hidden_channels"], p["n_blocks"], mh, mw, grid).to(device)
    n_params = sum(param_count(m) for m in members) + param_count(fno_d)

    ckpt_dir = Path(args.ckpt_dir); ckpt_dir.mkdir(parents=True, exist_ok=True)
    last = ckpt_dir / "last.pt"
    trained = False; res_scaler = 1.0
    if last.exists():
        try:
            sd = torch.load(last, map_location=device, weights_only=False)
            if sd.get("epochs_target") == args.epochs and sd.get("grid") == list(grid) \
               and sd.get("ensemble") == E:
                for m, msd in zip(members, sd["members"]):
                    m.load_state_dict(msd)
                fno_d.load_state_dict(sd["fno_d"])
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
        # LF distributional summaries on HF train inputs
        mu_hf, _, aug_hf = _lf_summaries(members, X_hf, s_lf, device, p["batch_size"], quants)
        residual = (Y_hf - mu_hf).astype(np.float32)
        res_scaler = max(float(np.abs(residual).max()), 1e-8) if residual.size else 1.0
        # 2) distribution-conditioned residual model
        print("[stage2] train FNO_delta on (HF - mu_LF) | aug", flush=True)
        _train_aug(fno_d, X_hf, aug_hf, residual, res_scaler, args.epochs, p["lr"], p,
                   device, seed=args.seed)
        torch.save({"epochs_target": args.epochs, "grid": list(grid), "ensemble": E,
                    "members": [m.state_dict() for m in members],
                    "fno_d": fno_d.state_dict(), "res_scaler": res_scaler}, last)
    train_seconds = time.time() - t_train

    # 3) predict + UQ on test
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize()
    t_eval = time.time()
    mu_te, var_te, aug_te = _lf_summaries(members, X_te, s_lf, device, p["batch_size"], quants)
    d_te = _aug_predict(fno_d, X_te, aug_te, res_scaler, device, p["batch_size"])
    pred = (mu_te + d_te).reshape(X_te.shape[0], -1).astype(np.float64)
    if device.type == "cuda":
        torch.cuda.synchronize()
    eval_seconds = time.time() - t_eval
    target = Y_te.reshape(Y_te.shape[0], -1).astype(np.float64)
    n = int(target.shape[0])
    latency = (1000.0 * eval_seconds / max(n, 1)) if device.type == "cuda" else None
    peak = (torch.cuda.max_memory_allocated() / 1e6) if device.type == "cuda" else None

    # UQ diagnostic (LF ensemble predictive variance): mean Gaussian NLL of the HF
    # target under N(pred, var_te). Pure diagnostic — not used by the ranking metric.
    sig2 = (var_te.reshape(n, -1) + 1e-6).astype(np.float64)
    err2 = (pred - target) ** 2
    nll = float(np.mean(0.5 * (np.log(2 * np.pi * sig2) + err2 / sig2))) if n else None

    return finalize_and_write(
        out_path=out_path, model="fno_fire_distcond", dataset=args.dataset_name,
        pred=pred, target=target, work_grid=grid, n_params=int(n_params),
        train_seconds=train_seconds, eval_seconds=eval_seconds,
        latency_ms_per_sample=latency, peak_mem_mb=peak, seed=args.seed,
        extra={"device": str(device), "hf_fidelity": int(hf), "lf_fidelity": int(lf),
               "mf_mechanism": "FIRE_distribution_conditioned_residual_HF=muLF+delta(aug)",
               "ensemble_size": E, "aug_channels": ["mu", "sigma", "q10", "q50", "q90"],
               "lf_ensemble_gaussian_nll": nll, "work_grid": list(grid)},
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
