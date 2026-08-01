"""Shared core for the FIRE-family uncertainty-source ablation.

Every family produces the per-pixel LF posterior-predictive summary FIELDS
[mu, sigma, q10, q50, q90], conditions a residual FNO on them, and predicts
HF = mu_LF + delta. The families differ ONLY in HOW the LF distribution is
obtained. This module holds the shared backbone, the shared residual runner,
and one class per uncertainty method:

  sampling (empirical percentiles):   SnapshotLF, SWAGLF, BatchEnsembleLF
  direct (predict the distribution):  QuantileLF, IQNLF, MDNLF
  Gaussian posterior:                 LaplaceLF, DKLGPLF
  (deep ensemble + MC-dropout already exist as standalone families)

CQR (calibrated percentiles) is handled by the runner's `calib_frac` hook.
"""
from __future__ import annotations

import copy
import math
import time
from pathlib import Path
from typing import Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

try:  # imported as _common.fire_core (models/ on sys.path — the family pattern)
    from _common.lf_registration import resample_fields
except ImportError:  # imported with models/_common/ itself on sys.path
    from lf_registration import resample_fields

Grid = Tuple[int, int]
QUANTILES = (0.1, 0.5, 0.9)
AUG_CH = 5  # [mu, sigma, q10, q50, q90]


# ───────────────────────── backbone ─────────────────────────
class SpectralConv2d(nn.Module):
    def __init__(self, in_ch, out_ch, modes_h, modes_w):
        super().__init__()
        self.in_ch, self.out_ch = in_ch, out_ch
        self.modes_h = max(1, modes_h); self.modes_w = max(1, modes_w)
        s = 1.0 / (in_ch * out_ch)
        self.w1 = nn.Parameter(s * torch.randn(in_ch, out_ch, self.modes_h, self.modes_w, dtype=torch.cfloat))
        self.w2 = nn.Parameter(s * torch.randn(in_ch, out_ch, self.modes_h, self.modes_w, dtype=torch.cfloat))

    def forward(self, x):
        B, _, H, W = x.shape
        x_ft = torch.fft.rfft2(x, norm="ortho")
        mh = min(self.modes_h, max(H // 2, 1)); mw = min(self.modes_w, W // 2 + 1)
        out = torch.zeros(B, self.out_ch, H, W // 2 + 1, dtype=torch.cfloat, device=x.device)
        out[:, :, :mh, :mw] = torch.einsum("bchw,cohw->bohw", x_ft[:, :, :mh, :mw], self.w1[:, :, :mh, :mw])
        if H >= 2 * mh:
            out[:, :, -mh:, :mw] = torch.einsum("bchw,cohw->bohw", x_ft[:, :, -mh:, :mw], self.w2[:, :, :mh, :mw])
        return torch.fft.irfft2(out, s=(H, W), norm="ortho")


class FNOBlock(nn.Module):
    def __init__(self, ch, mh, mw, dropout=0.0):
        super().__init__()
        self.spectral = SpectralConv2d(ch, ch, mh, mw)
        self.w = nn.Conv2d(ch, ch, 1)
        self.norm = nn.GroupNorm(min(8, ch), ch)
        self.drop = nn.Dropout2d(dropout) if dropout > 0 else nn.Identity()

    def forward(self, x):
        return self.drop(F.gelu(self.norm(self.spectral(x) + self.w(x))))


def _coord_grid(H, W):
    ys = torch.linspace(-1.0, 1.0, H); xs = torch.linspace(-1.0, 1.0, W)
    gy, gx = torch.meshgrid(ys, xs, indexing="ij")
    return torch.stack([gy, gx], 0).unsqueeze(0)


class FNOTrunk(nn.Module):
    """cond (+ optional extra input channels) -> penultimate feature map (B, hidden, H, W)."""
    def __init__(self, in_extra, hidden, n_blocks, mh, mw, grid, dropout=0.0):
        super().__init__()
        self.grid = (int(grid[0]), int(grid[1]))
        self.in_extra = in_extra
        self.lift = nn.Conv2d(in_extra + 2, hidden, 1)
        self.blocks = nn.ModuleList(FNOBlock(hidden, mh, mw, dropout) for _ in range(n_blocks))
        self.register_buffer("coord_grid", _coord_grid(*self.grid))

    def forward(self, feat):  # feat: (B, in_extra, H, W)
        B = feat.shape[0]; H, W = self.grid
        z = self.lift(torch.cat([feat, self.coord_grid.expand(B, 2, H, W)], 1))
        for blk in self.blocks:
            z = blk(z)
        return z


def _broadcast_cond(x, cond_dim, grid):
    B = x.shape[0]; H, W = grid
    return x.view(B, cond_dim, 1, 1).expand(B, cond_dim, H, W)


class FNO2d(nn.Module):
    """cond vector -> field, with `out_ch` output channels (1 by default)."""
    def __init__(self, cond_dim, hidden=64, n_blocks=4, mh=12, mw=12, grid=(64, 64), out_ch=1, dropout=0.0):
        super().__init__()
        self.cond_dim = cond_dim; self.grid = (int(grid[0]), int(grid[1])); self.out_ch = out_ch
        self.trunk = FNOTrunk(cond_dim, hidden, n_blocks, mh, mw, grid, dropout)
        self.proj = nn.Sequential(nn.Conv2d(hidden, hidden, 1), nn.GELU(), nn.Conv2d(hidden, out_ch, 1))

    def enable_mc_dropout(self):
        for m in self.modules():
            if isinstance(m, (nn.Dropout, nn.Dropout2d)):
                m.train()

    def features(self, x):
        return self.trunk(_broadcast_cond(x, self.cond_dim, self.grid))

    def forward(self, x):
        z = self.proj(self.trunk(_broadcast_cond(x, self.cond_dim, self.grid)))
        return z.squeeze(1) if self.out_ch == 1 else z


class FNO2dAug(nn.Module):
    """cond vector + K summary channels -> residual field."""
    def __init__(self, cond_dim, aug_ch, hidden=64, n_blocks=4, mh=12, mw=12, grid=(64, 64)):
        super().__init__()
        self.cond_dim = cond_dim; self.aug_ch = aug_ch; self.grid = (int(grid[0]), int(grid[1]))
        self.trunk = FNOTrunk(cond_dim + aug_ch, hidden, n_blocks, mh, mw, grid)
        self.proj = nn.Sequential(nn.Conv2d(hidden, hidden, 1), nn.GELU(), nn.Conv2d(hidden, 1, 1))

    def forward(self, x, aug):
        feat = torch.cat([_broadcast_cond(x, self.cond_dim, self.grid), aug], 1)
        return self.proj(self.trunk(feat)).squeeze(1)


def param_count(m):
    return sum(p.numel() for p in m.parameters())


# ───────────────────────── helpers ─────────────────────────
WORK_CAP = 256
_Z = {0.1: -1.2815515594, 0.5: 0.0, 0.9: 1.2815515594}  # standard-normal quantiles


def cap_grid(grid, cap=WORK_CAP):
    H, W = int(grid[0]), int(grid[1]); m = max(H, W)
    if m <= cap:
        return (H, W)
    f = cap / m
    return (max(1, round(H * f)), max(1, round(W * f)))


def modes(grid, c):
    H, W = grid
    return (min(c, max(H // 2, 1)), min(c, W // 2 + 1))


def to_grid(y_flat, src, dst, dataset_name=None):
    """Field resample under the dataset's registration convention
    (models/_common/lf_registration.py). dataset_name=None keeps the historic
    cell-centred bilinear path bit-for-bit (registration defect note, item 1)."""
    if dataset_name is None:
        Hs, Ws = int(src[0]), int(src[1]); Hd, Wd = int(dst[0]), int(dst[1])
        t = torch.from_numpy(np.ascontiguousarray(y_flat, dtype=np.float32)).view(-1, 1, Hs, Ws)
        if (Hs, Ws) != (Hd, Wd):
            t = F.interpolate(t, size=(Hd, Wd), mode="bilinear", align_corners=False)
        return t.squeeze(1).numpy().astype(np.float32)
    return resample_fields(y_flat, src, dst, dataset_name)


def pack_aug(mu, sigma, q10, q50, q90, s_lf):
    return np.stack([c / s_lf for c in [mu, sigma, q10, q50, q90]], axis=1).astype(np.float32)


def summaries_from_samples(samples, s_lf):
    """samples (K,N,H,W) -> (mu, var, aug) with aug = [mu,sigma,q10,q50,q90]/s_lf."""
    mu = samples.mean(0); var = samples.var(0); sigma = np.sqrt(var + 1e-12)
    q10, q50, q90 = (np.quantile(samples, q, axis=0) for q in QUANTILES)
    return mu.astype(np.float32), var.astype(np.float32), pack_aug(mu, sigma, q10, q50, q90, s_lf)


def gaussian_summaries(mu, sigma, s_lf):
    """mu,sigma (N,H,W) -> (mu, var, aug); quantiles via the Gaussian quantile fn."""
    q10 = mu + sigma * _Z[0.1]; q90 = mu + sigma * _Z[0.9]
    return mu.astype(np.float32), (sigma ** 2).astype(np.float32), pack_aug(mu, sigma, q10, mu, q90, s_lf)


# ───────────────────────── training utilities ─────────────────────────
def _opt(model, lr, wd, epochs):
    o = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=wd)
    return o, torch.optim.lr_scheduler.CosineAnnealingLR(o, T_max=max(epochs, 1), eta_min=1e-6)


def train_mse(model, X, Y, scaler, epochs, p, device, seed):
    if X.shape[0] == 0 or epochs <= 0:
        return
    o, sch = _opt(model, p["lr"], p["weight_decay"], epochs)
    Xt = torch.from_numpy(X).float(); Yt = torch.from_numpy(Y).float() / scaler
    n = X.shape[0]; bs = min(p["batch_size"], n); g = torch.Generator().manual_seed(seed)
    for _ in range(epochs):
        model.train()
        for i in range(0, n, bs):
            idx = torch.randperm(n, generator=g)[i:i + bs]
            o.zero_grad(set_to_none=True)
            loss = F.mse_loss(model(Xt[idx].to(device)), Yt[idx].to(device))
            loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), p["grad_clip"]); o.step()
        sch.step()


def _train_aug(model, X, aug, target, scaler, epochs, p, device, seed):
    if X.shape[0] == 0 or epochs <= 0:
        return
    o, sch = _opt(model, p["lr"], p["weight_decay"], epochs)
    Xt = torch.from_numpy(X).float(); At = torch.from_numpy(aug).float(); Yt = torch.from_numpy(target).float() / scaler
    n = X.shape[0]; bs = min(p["batch_size"], n); g = torch.Generator().manual_seed(seed)
    for _ in range(epochs):
        model.train()
        for i in range(0, n, bs):
            idx = torch.randperm(n, generator=g)[i:i + bs]
            o.zero_grad(set_to_none=True)
            loss = F.mse_loss(model(Xt[idx].to(device), At[idx].to(device)), Yt[idx].to(device))
            loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), p["grad_clip"]); o.step()
        sch.step()


@torch.no_grad()
def _aug_predict(model, X, aug, scaler, device, bs):
    model.eval(); out = []
    for i in range(0, X.shape[0], bs):
        xb = torch.from_numpy(X[i:i + bs]).float().to(device)
        ab = torch.from_numpy(aug[i:i + bs]).float().to(device)
        out.append((model(xb, ab) * scaler).cpu().numpy())
    return np.concatenate(out, 0).astype(np.float32)


# ───────────────────────── shared runner ─────────────────────────
def fire_run(args, out_path, model_name, make_lf, extra_meta, p, calib_frac=0.0, cov_alpha=0.1):
    """make_lf(cond_dim, grid, mh, mw, device) -> LF object with:
         .fit(X_lf, Y_lf, s_lf, epochs, seed) ; .summaries(X, s_lf) -> (mu,var,aug) ; .n_params()
    """
    from data_adapters import load_mf_dataset
    from data_adapters.geometry import resolve_grid
    from data_adapters.metrics import finalize_and_write

    torch.manual_seed(args.seed); np.random.seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    ds_dir = Path(args.dataset_dir)
    train = load_mf_dataset(ds_dir, "train"); test = load_mf_dataset(ds_dir, "test")
    hf = train["hf_fid"]; lf = min(train["lf_fids"]) if train["lf_fids"] else hf
    if hf not in test["fids"]:
        hf = test["hf_fid"]
    hf_native = resolve_grid(args.dataset_name, int(train["n_cells_by_fid"][hf]))
    lf_native = resolve_grid(args.dataset_name, int(train["n_cells_by_fid"][lf]))
    grid = cap_grid(hf_native); mh, mw = modes(grid, p["modes_cap"])

    X_lf = train["cond_by_fid"][lf].astype(np.float32); Y_lf = to_grid(train["field_by_fid"][lf], lf_native, grid, args.dataset_name)
    X_hf = train["cond_by_fid"][hf].astype(np.float32); Y_hf = to_grid(train["field_by_fid"][hf], hf_native, grid, args.dataset_name)
    X_te = test["cond_by_fid"][hf].astype(np.float32); Y_te = to_grid(test["field_by_fid"][hf], hf_native, grid, args.dataset_name)
    cond_dim = int(X_hf.shape[1])
    s_lf = max(float(np.abs(Y_lf).max()), 1e-8) if Y_lf.size else 1.0

    print(f"[data] {args.dataset_name} {model_name} LF={lf} HF={hf} grid={grid} "
          f"N_lf={X_lf.shape[0]} N_hf={X_hf.shape[0]} N_test={X_te.shape[0]}", flush=True)

    lfm = make_lf(cond_dim, grid, mh, mw, device)
    fno_d = FNO2dAug(cond_dim, AUG_CH, p["hidden_channels"], p["n_blocks"], mh, mw, grid).to(device)

    t0 = time.time()
    print("[stage1] fit LF uncertainty model", flush=True)
    lfm.fit(X_lf, Y_lf, s_lf, args.epochs, args.seed)
    mu_hf, _, aug_hf = lfm.summaries(X_hf, s_lf)
    residual = (Y_hf - mu_hf).astype(np.float32)
    res_scaler = max(float(np.abs(residual).max()), 1e-8) if residual.size else 1.0

    # optional CQR calibration split
    cov = None; width = None
    if calib_frac > 0 and X_hf.shape[0] >= 5:
        nh = X_hf.shape[0]; ncal = max(1, int(round(calib_frac * nh)))
        rng = np.random.RandomState(args.seed); perm = rng.permutation(nh)
        cal, tr = perm[:ncal], perm[ncal:]
        print(f"[stage2] train residual on {len(tr)} (CQR calib={len(cal)})", flush=True)
        _train_aug(fno_d, X_hf[tr], aug_hf[tr], residual[tr], res_scaler, args.epochs, p, device, args.seed)
        d_cal = _aug_predict(fno_d, X_hf[cal], aug_hf[cal], res_scaler, device, p["batch_size"])
        pred_cal = mu_hf[cal] + d_cal
        sig_cal = aug_hf[cal][:, 1] * s_lf + 1e-8            # sigma field (un-normalized)
        score = np.abs(Y_hf[cal] - pred_cal) / sig_cal       # normalized conformity score
        q = float(np.quantile(score, min(1.0, 1 - cov_alpha)))  # conformal multiplier
    else:
        print("[stage2] train residual (distribution-conditioned)", flush=True)
        _train_aug(fno_d, X_hf, aug_hf, residual, res_scaler, args.epochs, p, device, args.seed)
        q = None
    train_seconds = time.time() - t0

    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize()
    te = time.time()
    mu_te, var_te, aug_te = lfm.summaries(X_te, s_lf)
    d_te = _aug_predict(fno_d, X_te, aug_te, res_scaler, device, p["batch_size"])
    pred = (mu_te + d_te).reshape(X_te.shape[0], -1).astype(np.float64)
    if device.type == "cuda":
        torch.cuda.synchronize()
    eval_seconds = time.time() - te
    target = Y_te.reshape(Y_te.shape[0], -1).astype(np.float64)
    n = int(target.shape[0])
    latency = (1000.0 * eval_seconds / max(n, 1)) if device.type == "cuda" else None
    peak = (torch.cuda.max_memory_allocated() / 1e6) if device.type == "cuda" else None

    sig2 = (var_te.reshape(n, -1) + 1e-6).astype(np.float64)
    nll = float(np.mean(0.5 * (np.log(2 * np.pi * sig2) + (pred - target) ** 2 / sig2))) if n else None
    extra = {"device": str(device), "hf_fidelity": int(hf), "lf_fidelity": int(lf),
             "aug_channels": ["mu", "sigma", "q10", "q50", "q90"],
             "lf_gaussian_nll": nll, "work_grid": list(grid)}
    extra.update(extra_meta)
    if q is not None:
        sig_te = aug_te[:, 1] * s_lf + 1e-8
        half = (q * sig_te).reshape(n, -1)
        lo = pred - half; hi = pred + half
        cov = float(np.mean((target >= lo) & (target <= hi)))
        width = float(np.mean(2 * half))
        extra.update({"cqr_target_coverage": 1 - cov_alpha, "cqr_empirical_coverage": cov,
                      "cqr_mean_interval_width": width, "cqr_q_multiplier": q})

    return finalize_and_write(
        out_path=out_path, model=model_name, dataset=args.dataset_name,
        pred=pred, target=target, work_grid=grid, n_params=int(lfm.n_params() + param_count(fno_d)),
        train_seconds=train_seconds, eval_seconds=eval_seconds,
        latency_ms_per_sample=latency, peak_mem_mb=peak, seed=args.seed, extra=extra)
