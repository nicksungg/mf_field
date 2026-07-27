"""Quantify every benchmark dataset (no GPU, no harness dependency).

Reads raw factory-npz (train_l{k}.npz + meta.json) directly for all 43 datasets in
mffp_bench_combined.csv and measures, per dataset:

  Frequency / complexity (on HF fields)
    hf_highfreq_ratio  : spectral energy above half-Nyquist / total  (sharp -> high)
    hf_spectral_slope  : slope of log(radial power) vs log(k)         (smooth -> steep negative)
    hf_tv_rel          : mean |grad| / mean|field|  (real-space roughness)
    hf_pca_dim95       : # PCA comps for 95% variance of the field set
  HF<->LF correlation (the MF-learnability question)
    lf_hf_pearson      : per-sample corr(resampled LF, HF), mean
    lf_hf_rel_resid    : mean ||hf - LF_up|| / ||hf||
    lf_hf_lowband_corr / lf_hf_highband_corr : where in Fourier space LF & HF agree
  Parameter->field learnability
    pf_dist_corr       : Spearman corr(||dX||, ||dY||) over sample pairs (smooth op -> high)
    pf_var_explained   : R^2 of linear X -> top-PCA-coeffs fit
  Regime/scale: ndim, n_fid, cond_dim, n_hf, hf_grid, hf_amp_scale
  Degeneracy: composite flag from low lf_hf_pearson AND low pf_dist_corr

Out: akash/results/dataset_characterization.csv + _summary.md
"""
from __future__ import annotations

import csv
import json
import math
import os
from pathlib import Path

import numpy as np

ROOT = Path("/orcd/data/faez/001/nick")
MANIFEST = ROOT / "mffp_bench_combined.csv"
OUTDIR = ROOT / "mf_field/akash/results"
CAP = 128          # cap HF linear size for spectral/TV stats (cost); fields larger are downsampled
PCA_CAP = 48       # downsample size for PCA intrinsic-dim
NMAX = 100         # subsample this many fields for all stats
RNG = np.random.RandomState(0)

# degeneracy thresholds (tunable; validated against KS/cahn)
DEGEN_CORR = 0.3   # lf_hf_pearson below this == LF barely predicts HF
DEGEN_PF = 0.15    # pf_dist_corr below this == chaotic param->field map


FACTORY = ROOT / "mf_field/factory_mffp"
import sys
if str(FACTORY) not in sys.path:
    sys.path.insert(0, str(FACTORY))


def resolve_dir(collection: str, name: str) -> Path | None:
    if collection == "core":
        c = FACTORY / "data" / name                 # core: use the factory symlink + adapter
        return c if c.exists() else None
    if collection == "ext":
        b = ROOT / "mf_field_extension_data/data_400_100"
        cands = [b / f"{name}_generated", b / name]
    else:  # sharp
        b = ROOT / "mf_field/sharp_generated"
        cands = [b / f"{name}_generated", b / name, b / f"{name.replace('_2d','')}_generated"]
    for c in cands:
        if c.exists() and (c / "meta.json").exists():
            return c
    return None


def _reshape(y, grid, ndim):
    n = y.shape[0]
    if ndim == 1:
        return y.reshape(n, 1, grid[0])
    return y.reshape(n, grid[0], grid[1])


def _down(f, cap):
    """Downsample a (N,H,W) stack to <=cap linear size by strided averaging-ish (slicing)."""
    H, W = f.shape[1], f.shape[2]
    sh = max(1, H // cap); sw = max(1, W // cap)
    return f[:, ::sh, ::sw]


def _resample_to(f, H, W):
    """nearest-ish resample (N,h,w)->(N,H,W) via index mapping (cheap, no torch)."""
    n, h, w = f.shape
    yi = (np.linspace(0, h - 1, H)).round().astype(int)
    xi = (np.linspace(0, w - 1, W)).round().astype(int)
    return f[:, yi][:, :, xi]


def highfreq_ratio_and_slope(f):
    """f: (N,H,W). Radial power spectrum -> (highfreq energy ratio, log-log slope)."""
    F = np.fft.rfft2(f, axes=(1, 2))
    P = (np.abs(F) ** 2).mean(0)                      # (H, W//2+1)
    H, Wp = P.shape
    ky = np.fft.fftfreq(H)[:, None] * H
    kx = (np.arange(Wp))[None, :]
    kr = np.sqrt(ky ** 2 + kx ** 2)
    kmax = kr.max()
    if kmax <= 0:
        return float("nan"), float("nan")
    hi = P[kr > 0.5 * kmax].sum()
    tot = P[kr > 0].sum()
    ratio = float(hi / tot) if tot > 0 else float("nan")
    # radial binning for slope
    nb = 24
    bins = np.linspace(kr[kr > 0].min(), kmax, nb)
    idx = np.digitize(kr.ravel(), bins)
    Pf = P.ravel()
    ks, ps = [], []
    for b in range(1, nb):
        m = idx == b
        if m.sum() > 0 and Pf[m].sum() > 0:
            ks.append(0.5 * (bins[b - 1] + bins[b])); ps.append(Pf[m].mean())
    slope = float("nan")
    if len(ks) >= 4:
        lk, lp = np.log10(np.array(ks) + 1e-12), np.log10(np.array(ps) + 1e-30)
        slope = float(np.polyfit(lk, lp, 1)[0])
    return ratio, slope


def band_corr(lf, hf, lowfrac=0.25):
    """corr of low- vs high-Fourier-band content between LF_up and HF. f:(N,H,W)."""
    def band(f, lo):
        F = np.fft.rfft2(f, axes=(1, 2))
        H, Wp = F.shape[1], F.shape[2]
        ky = np.abs(np.fft.fftfreq(H)[:, None] * H); kx = np.arange(Wp)[None, :]
        kr = np.sqrt(ky ** 2 + kx ** 2); kmax = kr.max()
        mask = (kr <= lowfrac * kmax) if lo else (kr > lowfrac * kmax)
        Fm = F * mask[None]
        return np.fft.irfft2(Fm, s=(f.shape[1], f.shape[2]), axes=(1, 2))
    out = []
    for lo in (True, False):
        a = band(lf, lo).reshape(lf.shape[0], -1); b = band(hf, lo).reshape(hf.shape[0], -1)
        cs = [_pear(a[i], b[i]) for i in range(a.shape[0])]
        out.append(float(np.nanmean(cs)))
    return out[0], out[1]


def _pear(a, b):
    a = a - a.mean(); b = b - b.mean()
    da, db = np.linalg.norm(a), np.linalg.norm(b)
    return float((a @ b) / (da * db)) if da > 0 and db > 0 else float("nan")


def pca_dim95(f):
    x = f.reshape(f.shape[0], -1).astype(np.float64)
    x = x - x.mean(0, keepdims=True)
    # gram-matrix SVD (N small)
    g = x @ x.T
    ev = np.linalg.eigvalsh(g)[::-1].clip(min=0)
    if ev.sum() <= 0:
        return 1
    c = np.cumsum(ev) / ev.sum()
    return int(np.searchsorted(c, 0.95) + 1)


def param_field(X, f):
    """Spearman corr of pairwise ||dX|| vs ||dY||, and linear X->PCA-coeff R^2."""
    n = X.shape[0]
    Y = f.reshape(n, -1).astype(np.float64)
    # pairwise distances on a sample of pairs
    npair = min(2000, n * (n - 1) // 2)
    ii = RNG.randint(0, n, npair); jj = RNG.randint(0, n, npair)
    ok = ii != jj
    ii, jj = ii[ok], jj[ok]
    dX = np.linalg.norm(X[ii] - X[jj], axis=1)
    dY = np.linalg.norm(Y[ii] - Y[jj], axis=1)
    dist_corr = _spearman(dX, dY)
    # linear X -> top PCA coeffs R^2
    Yc = Y - Y.mean(0)
    try:
        # top-k pca coeffs via gram
        g = Yc @ Yc.T
        w, V = np.linalg.eigh(g)
        k = min(10, n - 1)
        coeffs = V[:, -k:] * np.sqrt(np.clip(w[-k:], 0, None))   # (n, k) scores
        Xa = np.hstack([X, np.ones((n, 1))])
        beta, *_ = np.linalg.lstsq(Xa, coeffs, rcond=None)
        pred = Xa @ beta
        ss_res = ((coeffs - pred) ** 2).sum(); ss_tot = ((coeffs - coeffs.mean(0)) ** 2).sum()
        r2 = float(1 - ss_res / ss_tot) if ss_tot > 0 else float("nan")
    except Exception:
        r2 = float("nan")
    return dist_corr, r2


def _spearman(a, b):
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    return _pear(ra.astype(float), rb.astype(float))


def _load_fields(coll, name, d: Path):
    """Return (Xhf, Fhf(N,H,W), Flf(N,h,w), ndim, nfid, cond_dim, g_hf) for either layout."""
    if (d / "meta.json").exists():                 # ext / sharp: direct npz + ladder
        meta = json.load(open(d / "meta.json"))
        ndim = int(meta.get("ndim", 2)); ladder = meta["ladder"]; nfid = len(ladder)
        zhf = np.load(d / f"train_l{nfid}.npz"); zlf = np.load(d / "train_l1.npz")
        Xhf = zhf["x"].astype(np.float64)
        Fhf = _reshape(zhf["y"].astype(np.float64), ladder[-1], ndim)
        Flf = _reshape(zlf["y"].astype(np.float64), ladder[0], ndim)
        return Xhf, Fhf, Flf, ndim, nfid, int(Xhf.shape[1]), ladder[-1]
    # core: factory adapter (handles npz_l / era5 / ifc raw + KNOWN_GRIDS)
    from data_adapters import load_mf_dataset
    from data_adapters.geometry import resolve_grid
    tr = load_mf_dataset(d, "train")
    hf = tr["hf_fid"]; lf = min(tr["lf_fids"]) if tr["lf_fids"] else hf
    nfid = len(tr["fids"])
    g_hf = tr["grid_shape_by_fid"].get(hf) or resolve_grid(name, int(tr["n_cells_by_fid"][hf]))
    g_lf = tr["grid_shape_by_fid"].get(lf) or resolve_grid(name, int(tr["n_cells_by_fid"][lf]))
    ndim = 1 if int(g_hf[0]) == 1 else 2
    Xhf = np.asarray(tr["cond_by_fid"][hf], dtype=np.float64)
    Fhf = np.asarray(tr["field_by_fid"][hf], dtype=np.float64).reshape(-1, int(g_hf[0]), int(g_hf[1]))
    Flf = np.asarray(tr["field_by_fid"][lf], dtype=np.float64).reshape(-1, int(g_lf[0]), int(g_lf[1]))
    g_hf2 = [int(g_hf[0]), int(g_hf[1])] if ndim == 2 else [int(g_hf[1])]
    return Xhf, Fhf, Flf, ndim, nfid, int(Xhf.shape[1]), g_hf2


def characterize(coll, name, d: Path) -> dict:
    Xhf, Fhf, Flf, ndim, nfid, cond_dim, g_hf = _load_fields(coll, name, d)
    # subsample
    nh = min(NMAX, Fhf.shape[0])
    sel = RNG.choice(Fhf.shape[0], nh, replace=False)
    Fhf_s = Fhf[sel]; Xhf_s = Xhf[sel]
    # downsample HF for spectral/TV
    Fhf_c = _down(Fhf_s, CAP)
    amp = float(np.abs(Fhf_s).mean())
    hf_hi, hf_slope = highfreq_ratio_and_slope(Fhf_c)
    # TV (relative roughness); 1-D fields are (N,1,W) so skip the singleton axis
    gx = np.abs(np.diff(Fhf_c, axis=2)).mean()
    gy = 0.0 if Fhf_c.shape[1] < 2 else float(np.abs(np.diff(Fhf_c, axis=1)).mean())
    tv_rel = float((gy + gx) / (amp + 1e-12))
    pca = pca_dim95(_down(Fhf_s, PCA_CAP))
    # HF<->LF correlation (align by min N, resample LF up to HF-capped grid)
    nmin = min(Fhf.shape[0], Flf.shape[0], NMAX)
    a = Flf[:nmin]; b = Fhf[:nmin]
    Hc, Wc = Fhf_c.shape[1], Fhf_c.shape[2]
    a_up = _resample_to(_down(a, CAP) if max(a.shape[1], a.shape[2]) > CAP else a, Hc, Wc)
    b_c = _resample_to(_down(b, CAP) if max(b.shape[1], b.shape[2]) > CAP else b, Hc, Wc)
    pears = [_pear(a_up[i].ravel(), b_c[i].ravel()) for i in range(nmin)]
    lf_hf_pear = float(np.nanmean(pears))
    rr = [np.linalg.norm((b_c[i] - a_up[i])) / (np.linalg.norm(b_c[i]) + 1e-12) for i in range(nmin)]
    lf_hf_resid = float(np.nanmean(rr))
    lo_c, hi_c = band_corr(a_up, b_c)
    # param->field
    pf_corr, pf_r2 = param_field(Xhf_s, Fhf_c)
    mf_useless = lf_hf_pear < DEGEN_CORR        # LF carries no signal about HF (MF pointless)
    operator_hard = pf_corr < DEGEN_PF          # chaotic param->field (nothing predicts it)
    return dict(
        collection=coll, dataset=name, ndim=ndim, n_fid=nfid, cond_dim=cond_dim,
        n_hf=int(Fhf.shape[0]), hf_grid="x".join(map(str, g_hf)), hf_amp_scale=round(amp, 6),
        hf_highfreq_ratio=round(hf_hi, 4), hf_spectral_slope=round(hf_slope, 3),
        hf_tv_rel=round(tv_rel, 4), hf_pca_dim95=pca,
        lf_hf_pearson=round(lf_hf_pear, 4), lf_hf_rel_resid=round(lf_hf_resid, 4),
        lf_hf_lowband_corr=round(lo_c, 4), lf_hf_highband_corr=round(hi_c, 4),
        pf_dist_corr=round(pf_corr, 4), pf_var_explained=round(pf_r2, 4),
        mf_useless=int(mf_useless), operator_hard=int(operator_hard),
        degenerate=int(mf_useless or operator_hard),
    )


def main():
    rows_in = list(csv.DictReader(open(MANIFEST)))
    out = []
    for r in rows_in:
        coll, name = r["collection"], r["dataset"]
        d = resolve_dir(coll, name)
        if d is None:
            print(f"[skip] {coll}/{name}: dir not found"); continue
        try:
            res = characterize(coll, name, d)
            out.append(res)
            tags = [t for t, k in (("MF-USELESS", "mf_useless"), ("OP-HARD", "operator_hard")) if res[k]]
            flag = "  *" + ",".join(tags) + "*" if tags else ""
            print(f"  {coll:5s} {name:28s} hf_corr={res['lf_hf_pearson']:.3f} "
                  f"hi_freq={res['hf_highfreq_ratio']:.3f} pf={res['pf_dist_corr']:.3f}{flag}", flush=True)
        except Exception as e:
            import traceback; print(f"[ERR] {coll}/{name}: {e}"); traceback.print_exc()
    if not out:
        print("no datasets characterized"); return
    OUTDIR.mkdir(parents=True, exist_ok=True)
    cols = list(out[0].keys())
    with open(OUTDIR / "dataset_characterization.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader()
        for r in out:
            w.writerow(r)
    mfu = [r["dataset"] for r in out if r["mf_useless"]]
    oph = [r["dataset"] for r in out if r["operator_hard"]]
    md = [f"# Dataset characterization ({len(out)} datasets)\n",
          f"- **MF-useless** (LF<->HF corr < {DEGEN_CORR}; multi-fidelity cannot help): {mfu or 'none'}",
          f"- **Operator-hard** (param->field corr < {DEGEN_PF}; chaotic map, nothing predicts it): {oph or 'none'}\n",
          "Sorted by HF<->LF correlation (low = MF can't help):\n",
          "| dataset | coll | ndim | hf_corr | rel_resid | hi_freq | spec_slope | tv_rel | pca95 | pf_corr | flags |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(out, key=lambda x: x["lf_hf_pearson"]):
        fl = ",".join([t for t, k in (("MFU", "mf_useless"), ("OPH", "operator_hard")) if r[k]])
        md.append(f"| {r['dataset']} | {r['collection']} | {r['ndim']}D | {r['lf_hf_pearson']} | "
                  f"{r['lf_hf_rel_resid']} | {r['hf_highfreq_ratio']} | {r['hf_spectral_slope']} | "
                  f"{r['hf_tv_rel']} | {r['hf_pca_dim95']} | {r['pf_dist_corr']} | {fl} |")
    open(OUTDIR / "dataset_characterization_summary.md", "w").write("\n".join(md) + "\n")
    print(f"\n[wrote] dataset_characterization.csv + _summary.md ({len(out)} rows)")
    print(f"  MF-useless: {mfu}")
    print(f"  Operator-hard: {oph}")


if __name__ == "__main__":
    main()
