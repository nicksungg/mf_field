#!/usr/bin/env python3
"""Visualize the CH sharpness transition: actual HF fields from smooth -> sharp as eps
shrinks, paired with their radial spectra developing a high-k tail past an FNO cutoff.

This is the teaching figure for docs/ch-sharpness-transition.md — it shows, on real CH
sample data, that eps continuously tunes frequency content (the knob the study uses).

Run on the box: python scripts/ch_sharpness_visual.py -> data/explain/ch_sharpness_visual.png
"""
from __future__ import annotations
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from mffp_sharp.pdes import cahn_hilliard as ch

OUT = os.path.join(os.path.dirname(__file__), "..", "data", "explain")
HF = 256
T = 1.0
DT = 5.0e-5
EPS = [0.028, 0.016, 0.010, 0.006]   # smooth -> sharp
K_MAX = 12                            # illustrative FNO mode cutoff


def radial(f):
    F = np.fft.fftshift(np.fft.fft2(f)); psd = np.abs(F) ** 2; n = f.shape[0]; c = n // 2
    y, x = np.indices((n, n)); r = np.hypot(x - c, y - c).astype(int); cnt = np.bincount(r.ravel())
    return np.arange(len(cnt)), np.bincount(r.ravel(), psd.ravel()) / np.maximum(cnt, 1)


def slope_of(p):
    k = np.arange(1, len(p)); sel = (k >= 5) & (k <= 60) & (p[1:] > 0)
    return float(np.polyfit(np.log(k[sel]), np.log(p[1:][sel]), 1)[0])


def main():
    os.makedirs(OUT, exist_ok=True)
    cache = os.path.join(OUT, "ch_visual_fields.npz")
    if os.path.exists(cache):
        d = np.load(cache); fields = [d[f"f{i}"] for i in range(len(EPS))]
        print("loaded cached fields (delete ch_visual_fields.npz to re-solve)", flush=True)
    else:
        rng = np.random.default_rng(42)
        ic_hf = ch._spectral_interp(0.0 + 0.1 * (2 * rng.random((64, 64)) - 1), HF)
        fields = []
        for eps in EPS:
            fields.append(ch._solve(ic_hf, eps, 1.0, 1.0, T, dt=DT))
            print(f"solved eps={eps:.3f}", flush=True)
        np.savez(cache, **{f"f{i}": f for i, f in enumerate(fields)})
    specs = [radial(f) for f in fields]
    slopes = [slope_of(p) for (_, p) in specs]

    from matplotlib.gridspec import GridSpec
    n = len(EPS)
    fig = plt.figure(figsize=(4 * n, 9.2), constrained_layout=True)
    gs = GridSpec(2, n, figure=fig, height_ratios=[1.0, 0.85])

    # Row 0: the fields, smooth -> sharp
    for j, (eps, f, s) in enumerate(zip(EPS, fields, slopes)):
        ax = fig.add_subplot(gs[0, j])
        im = ax.imshow(f, origin="lower", cmap="viridis", vmin=-1, vmax=1)
        tag = " (smooth)" if j == 0 else (" (sharpest)" if j == n - 1 else "")
        ax.set_title(f"eps = {eps:.3f}{tag}\nHF slope {s:.1f}", fontsize=10)
        ax.set_xticks([]); ax.set_yticks([])
        fig.colorbar(im, ax=ax, fraction=0.046)

    # Row 1: overlaid radial spectra (log-log), spanning the row
    axspec = fig.add_subplot(gs[1, :])
    for eps, (k, p), s in zip(EPS, specs, slopes):
        axspec.loglog(k[1:], p[1:] / p[1], label=f"eps={eps:.3f}  (slope {s:.1f})")
    axspec.axvline(K_MAX, color="purple", ls=":", lw=2)
    axspec.text(K_MAX * 1.1, 1e-2, f"FNO cutoff k={K_MAX}", color="purple", fontsize=9)
    axspec.axvspan(K_MAX, HF // 2, color="purple", alpha=0.05)
    axspec.set_xlabel("radial wavenumber (log)  ->  finer scales / higher frequency")
    axspec.set_ylabel("normalized power (log)")
    axspec.set_title("radial spectra: smaller eps -> fatter high-k tail past the FNO cutoff", fontsize=11)
    axspec.legend(fontsize=8, loc="lower left", title="smooth -> sharp")

    fig.suptitle("Cahn-Hilliard sharpness transition: eps continuously tunes frequency content",
                 fontsize=13)
    path = os.path.join(OUT, "ch_sharpness_visual.png")
    fig.savefig(path, dpi=120); plt.close(fig)
    print("wrote", os.path.normpath(path))


if __name__ == "__main__":
    main()
