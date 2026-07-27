"""MC-dropout distribution-conditioned residual learning (FNO backbone).

The cheap single-MODEL version of fno_fire_distcond: one LF FNO (with dropout)
instead of a 5-member ensemble. The LF posterior-predictive summaries (per-pixel
mean / std / quantile FIELDS) come from T stochastic forward passes with dropout
ON. The HF correction is conditioned on those summary fields exactly as in
fno_fire_distcond, and the residual is r = HF - mu_LF; final HF = mu_LF + delta.

Why MC-dropout (not a Gaussian-NLL head or pinball-quantile head): the LF solver
is deterministic, so the useful uncertainty is EPISTEMIC (model uncertainty under
scarce data), which dropout-sampling captures. Single-pass aleatoric heads (NLL/
quantile) have ~no signal here and the NLL head destabilises on hard datasets.

~2 FNOs (~1/3 the params of the 5-member ensemble), one training run.
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
REPO_ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model import FNO2dDrop, FNO2dAug, param_count  # noqa: E402
from data_adapters import load_mf_dataset  # noqa: E402
from data_adapters.geometry import resolve_grid  # noqa: E402
from data_adapters.metrics import finalize_and_write  # noqa: E402

WORK_CAP = 256
SMOKE = dict(hidden_channels=64, n_blocks=4, modes_cap=12, batch_size=16,
             lr=1e-3, weight_decay=1e-5, grad_clip=1.0,
             dropout=0.1, mc_samples=16, quantiles=(0.1, 0.5, 0.9))
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


def _to_grid(y_flat, src, dst):
    Hs, Ws = int(src[0]), int(src[1]); Hd, Wd = int(dst[0]), int(dst[1])
    t = torch.from_numpy(np.ascontiguousarray(y_flat, dtype=np.float32)).view(-1, 1, Hs, Ws)
    if (Hs, Ws) != (Hd, Wd):
        t = F.interpolate(t, size=(Hd, Wd), mode="bilinear", align_corners=False)
    return t.squeeze(1).numpy().astype(np.float32)


def _train(model, X, target, scaler, epochs, lr, p, device, seed):
    if X.shape[0] == 0 or epochs <= 0:
        return
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=p["weight_decay"])
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(epochs, 1), eta_min=1e-6)
    Xt = torch.from_numpy(X).float(); Yt = torch.from_numpy(target).float() / scaler
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
    if X.shape[0] == 0 or epochs <= 0:
        return
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=p["weight_decay"])
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(epochs, 1), eta_min=1e-6)
    Xt = torch.from_numpy(X).float(); At = torch.from_numpy(aug).float()
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
def _aug_predict(model, X, aug, scaler, device, bs):
    model.eval(); out = []
    for i in range(0, X.shape[0], bs):
        xb = torch.from_numpy(X[i:i + bs]).float().to(device)
        ab = torch.from_numpy(aug[i:i + bs]).float().to(device)
        out.append((model(xb, ab) * scaler).cpu().numpy())
    return np.concatenate(out, 0).astype(np.float32)


@torch.no_grad()
def _mc_summaries(model, X, s_lf, device, bs, T, quantiles, seed):
    """T MC-dropout passes -> (mu, var, aug) for inputs X.

    model.eval() freezes GroupNorm (no running stats anyway) while
    enable_mc_dropout() keeps dropout stochastic, so each pass is a different
    sub-network. Summaries computed per pixel over the T samples.
    """
    model.eval(); model.enable_mc_dropout()
    torch.manual_seed(seed)
    n = X.shape[0]
    samples = np.empty((T, n) + tuple(model.grid), dtype=np.float32)
    for t in range(T):
        outs = []
        for i in range(0, n, bs):
            xb = torch.from_numpy(X[i:i + bs]).float().to(device)
            outs.append((model(xb) * s_lf).cpu().numpy())
        samples[t] = np.concatenate(outs, 0)
    mu = samples.mean(0); var = samples.var(0); sigma = np.sqrt(var + 1e-12)
    qs = [np.quantile(samples, q, axis=0) for q in quantiles]
    aug = np.stack([c / s_lf for c in ([mu, sigma] + qs)], axis=1).astype(np.float32)
    return mu.astype(np.float32), var.astype(np.float32), aug


def run(args, out_path: Path) -> dict:
    torch.manual_seed(args.seed); np.random.seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    p = SMOKE
    T = int(p["mc_samples"]); quants = p["quantiles"]
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

    print(f"[data] {args.dataset_name} LF={lf} HF={hf} work_grid={grid} T={T} drop={p['dropout']} "
          f"N_lf={X_lf.shape[0]} N_hf={X_hf.shape[0]} N_test={X_te.shape[0]}", flush=True)

    fno_lf = FNO2dDrop(cond_dim, p["hidden_channels"], p["n_blocks"], mh, mw, grid, p["dropout"]).to(device)
    fno_d = FNO2dAug(cond_dim, AUG_CH, p["hidden_channels"], p["n_blocks"], mh, mw, grid).to(device)
    n_params = param_count(fno_lf) + param_count(fno_d)

    ckpt_dir = Path(args.ckpt_dir); ckpt_dir.mkdir(parents=True, exist_ok=True)
    last = ckpt_dir / "last.pt"
    trained = False; res_scaler = 1.0
    if last.exists():
        try:
            sd = torch.load(last, map_location=device, weights_only=False)
            if sd.get("epochs_target") == args.epochs and sd.get("grid") == list(grid):
                fno_lf.load_state_dict(sd["fno_lf"]); fno_d.load_state_dict(sd["fno_d"])
                res_scaler = sd.get("res_scaler", 1.0); trained = True
                print("[resume] loaded", flush=True)
        except Exception as e:
            print(f"[resume] failed ({e})", flush=True)

    t_train = time.time()
    if not trained:
        print("[stage1] train LF FNO (dropout) on LF", flush=True)
        _train(fno_lf, X_lf, Y_lf, s_lf, args.epochs, p["lr"], p, device, seed=args.seed + 1)
        mu_hf, _, aug_hf = _mc_summaries(fno_lf, X_hf, s_lf, device, p["batch_size"], T, quants, args.seed)
        residual = (Y_hf - mu_hf).astype(np.float32)
        res_scaler = max(float(np.abs(residual).max()), 1e-8) if residual.size else 1.0
        print("[stage2] train MC-dropout distribution-conditioned FNO_delta", flush=True)
        _train_aug(fno_d, X_hf, aug_hf, residual, res_scaler, args.epochs, p["lr"], p, device, seed=args.seed)
        torch.save({"epochs_target": args.epochs, "grid": list(grid),
                    "fno_lf": fno_lf.state_dict(), "fno_d": fno_d.state_dict(),
                    "res_scaler": res_scaler}, last)
    train_seconds = time.time() - t_train

    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize()
    t_eval = time.time()
    mu_te, var_te, aug_te = _mc_summaries(fno_lf, X_te, s_lf, device, p["batch_size"], T, quants, args.seed + 7)
    d_te = _aug_predict(fno_d, X_te, aug_te, res_scaler, device, p["batch_size"])
    pred = (mu_te + d_te).reshape(X_te.shape[0], -1).astype(np.float64)
    if device.type == "cuda":
        torch.cuda.synchronize()
    eval_seconds = time.time() - t_eval
    target = Y_te.reshape(Y_te.shape[0], -1).astype(np.float64)
    n = int(target.shape[0])
    latency = (1000.0 * eval_seconds / max(n, 1)) if device.type == "cuda" else None
    peak = (torch.cuda.max_memory_allocated() / 1e6) if device.type == "cuda" else None

    sig2 = (var_te.reshape(n, -1) + 1e-6).astype(np.float64)
    err2 = (pred - target) ** 2
    nll = float(np.mean(0.5 * (np.log(2 * np.pi * sig2) + err2 / sig2))) if n else None

    return finalize_and_write(
        out_path=out_path, model="fno_fire_mcdropout", dataset=args.dataset_name,
        pred=pred, target=target, work_grid=grid, n_params=int(n_params),
        train_seconds=train_seconds, eval_seconds=eval_seconds,
        latency_ms_per_sample=latency, peak_mem_mb=peak, seed=args.seed,
        extra={"device": str(device), "hf_fidelity": int(hf), "lf_fidelity": int(lf),
               "mf_mechanism": "MCdropout_distribution_conditioned_residual_HF=muLF+delta(aug)",
               "mc_samples": T, "dropout": p["dropout"],
               "aug_channels": ["mu", "sigma", "q10", "q50", "q90"],
               "lf_mc_gaussian_nll": nll, "work_grid": list(grid)},
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
