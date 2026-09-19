#!/usr/bin/env python3
"""Cahn-Hilliard sharpness sweep — the DATA side of the frequency-content transition study.

Use the interface width eps as a CONTINUOUS sharpness knob (same PDE, solver, IC,
domain — only eps changes) and measure, at a clean HF=256^2 reference:
  - HF spectral decay slope + energy fraction above an (illustrative) FNO cutoff
    -> the measurable "sharpness axis" the model crossover would be plotted against;
  - LF-HF rel_l2 for each coarse rung -> where the LF stops tracking HF (the confound
    to control: sharper eps also degrades LF, not just sharpens HF).

Outputs a table + data/explain/ch_sharpness_sweep.png. Run on the box (256^2 is heavy).
"""
from __future__ import annotations
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from mffp_sharp.pdes import cahn_hilliard as ch
from mffp_sharp.common import ladder, metrics

OUT = os.path.join(os.path.dirname(__file__), "..", "data", "explain")
LADDER = [64, 128, 256]      # HF = 256^2: resolves even the sharpest eps below
HF = 256
# Shorter T + smaller dt than the sample config: interface width ~ eps is fixed as soon as
# interfaces form, so the SHARPNESS measurement is T-independent. This keeps the 256^2 solves
# fast AND stable for sharp eps (the explicit nonlinear term needs a small dt on a fine grid).
T = 1.0
DT = 5.0e-5
EPS = [0.006, 0.008, 0.010, 0.013, 0.016, 0.020, 0.028]
K_MAX = 12                   # illustrative FNO mode cutoff


def radial(f):
    F = np.fft.fftshift(np.fft.fft2(f)); psd = np.abs(F) ** 2; n = f.shape[0]; c = n // 2
    y, x = np.indices((n, n)); r = np.hypot(x - c, y - c).astype(int); cnt = np.bincount(r.ravel())
    return np.arange(len(cnt)), np.bincount(r.ravel(), psd.ravel()) / np.maximum(cnt, 1)


def main():
    os.makedirs(OUT, exist_ok=True)
    rmin = min(LADDER); rng = np.random.default_rng(42)
    ic = 0.0 + 0.1 * (2 * rng.random((rmin, rmin)) - 1)
    rows = []
    print(f"{'eps':>6} {'cells@256':>9} {'HFslope':>8} {'E>k12':>9} {'relL2_128':>10} {'relL2_64':>9}")
    for eps in EPS:
        fields = {r: ch._solve(ch._spectral_interp(ic, r), eps, 1.0, 1.0, T, dt=DT) for r in LADDER}
        b = ladder.assemble_sample(fields, HF)
        hf = b["aligned"][HF]
        if not np.isfinite(hf).all():
            print(f"{eps:6.3f} {eps*HF:9.1f}   UNSTABLE (solver overflow at dt={DT:g})", flush=True)
            continue
        k, p = radial(hf); sel = (k >= 5) & (k <= 60) & (p > 0)
        slope = float(np.polyfit(np.log(k[sel]), np.log(p[sel]), 1)[0])
        frac = float(p[k > K_MAX].sum() / p[1:].sum())
        r128 = metrics.rel_l2(b["aligned"][128], hf)
        r64 = metrics.rel_l2(b["aligned"][64], hf)
        rows.append((eps, eps * HF, slope, frac, r128, r64))
        print(f"{eps:6.3f} {eps*HF:9.1f} {slope:8.2f} {frac:9.2e} {r128:10.3f} {r64:9.3f}", flush=True)

    rows = np.array(rows)
    if len(rows) < 2:
        print("not enough stable points for a figure"); return
    fig, ax = plt.subplots(1, 2, figsize=(13, 5), constrained_layout=True)
    ax[0].plot(rows[:, 0], -rows[:, 2], "o-", color="C0")
    ax[0].set_xlabel("interface width  eps"); ax[0].set_ylabel("HF decay steepness  (-slope)")
    ax[0].set_title("sharpness axis: smaller eps -> shallower decay -> more high-freq")
    ax[0].invert_xaxis()
    a2 = ax[0].twinx(); a2.semilogy(rows[:, 0], rows[:, 3], "s--", color="C1")
    a2.set_ylabel(f"energy fraction above k={K_MAX}", color="C1")

    ax[1].plot(rows[:, 0], rows[:, 4], "o-", label="128 vs HF(256)")
    ax[1].plot(rows[:, 0], rows[:, 5], "s-", label="64 vs HF(256)")
    ax[1].axhline(1.0, color="gray", ls=":"); ax[1].text(rows[-1, 0], 1.02, "diverged (rel_l2=1)", fontsize=7)
    ax[1].set_xlabel("interface width  eps"); ax[1].set_ylabel("LF-HF rel_l2")
    ax[1].set_title("LF divergence: where each LF rung stops tracking HF")
    ax[1].invert_xaxis(); ax[1].legend(fontsize=8)

    fig.suptitle("Cahn-Hilliard sharpness sweep (HF=256^2): eps as a continuous frequency knob")
    path = os.path.join(OUT, "ch_sharpness_sweep.png")
    fig.savefig(path, dpi=120); plt.close(fig)
    print("wrote", os.path.normpath(path))


if __name__ == "__main__":
    main()
