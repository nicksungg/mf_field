#!/usr/bin/env python3
"""Why the KS control needs T in the 'tracking' window, not the chaotic-steady regime.

KS is chaotic: a tiny grid-induced difference between the 32^2 and 128^2 runs (same IC)
grows like e^(lambda t). At small T they still track (LF=blurry HF, gap = resolution).
At large T they decorrelate into different chaotic states (gap ~1, NOT a frequency effect).

Top: LF(32)-vs-HF(128) rel-L2 gap vs integration time T (the cliff).
Rows: LF (32 upsampled), HF (128), residual -- at T=15 (tracking) and T=50 (decorrelated).

Run: python scripts/explain_ks_chaos.py  -> data/explain/fig_ks_chaos.png
"""
from __future__ import annotations
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

from mffp_sharp.pdes import kuramoto_sivashinsky as ks
from mffp_sharp.common import ladder, metrics

OUT = os.path.join(os.path.dirname(__file__), "..", "data", "explain")
SPEC = {"L": 30.0, "ic_amplitude": 0.1, "seed": 42}


def fields_at(T):
    raw, _, _ = ks.generate_sample(SPEC, [32, 128], 128, T)
    b = ladder.assemble_sample(raw, 128)
    lf, hf = b["aligned"][32], b["aligned"][128]
    return lf, hf, metrics.rel_l2(lf, hf)


def main():
    os.makedirs(OUT, exist_ok=True)
    Ts = [2, 5, 10, 15, 20, 30, 40, 50]
    gaps = [fields_at(T)[2] for T in Ts]

    fig = plt.figure(figsize=(13, 9), constrained_layout=True)
    gs = GridSpec(3, 3, figure=fig, height_ratios=[1.1, 1, 1])

    # --- top: gap vs T ---
    axc = fig.add_subplot(gs[0, :])
    axc.plot(Ts, gaps, "o-", color="C0")
    axc.axhspan(0, 0.35, color="green", alpha=0.07)
    axc.axhspan(0.7, 1.2, color="red", alpha=0.07)
    axc.axvline(15, color="green", ls="--"); axc.axvline(50, color="red", ls="--")
    axc.text(15, 0.05, "T=15\ntracking", color="green", ha="center", fontsize=9)
    axc.text(50, 0.9, "T=50\ndecorrelated", color="red", ha="center", fontsize=9)
    axc.set_xlabel("integration time T"); axc.set_ylabel("LF(32)-vs-HF(128) rel-L2")
    axc.set_title("KS: LF and HF track at small T, then chaotically decorrelate (cliff between 20 and 50)")

    # --- rows: fields at T=15 and T=50 ---
    for row, T, tag, col in [(1, 15, "tracking", "green"), (2, 50, "decorrelated", "red")]:
        lf, hf, g = fields_at(T)
        vmax = max(abs(hf).max(), abs(lf).max())
        resid = hf - lf
        a = abs(resid).max()
        panels = [(lf, "LF (32 upsampled)", "viridis", -vmax, vmax),
                  (hf, "HF (128)", "viridis", -vmax, vmax),
                  (resid, f"HF - LF   (rel-L2={g:.2f})", "coolwarm", -a, a)]
        for j, (img, title, cmap, lo, hi) in enumerate(panels):
            ax = fig.add_subplot(gs[row, j])
            im = ax.imshow(img, origin="lower", cmap=cmap, vmin=lo, vmax=hi)
            ax.set_title(f"T={T} ({tag}):  {title}", color=col, fontsize=9)
            ax.set_xticks([]); ax.set_yticks([])
            fig.colorbar(im, ax=ax, fraction=0.046)

    fig.suptitle("Why the KS control uses T=15, not T=50: at T=50 LF and HF are DIFFERENT "
                 "chaotic states (gap~1), not the same field at two resolutions", fontsize=12)
    path = os.path.join(OUT, "fig_ks_chaos.png")
    fig.savefig(path, dpi=120)
    plt.close(fig)
    print("wrote", os.path.normpath(path))


if __name__ == "__main__":
    main()
