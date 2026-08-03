#!/usr/bin/env python3
"""Render the sample-round review figures from the saved npz (no re-solve).

One figure per regenerated variant: two samples as rows, each showing the LF field at
native resolution (blocky), the HF field, and the LF-vs-HF error on the HF grid, with
the governing equation + the sample's physical conditions in the header and the
completeness-certificate verdict as the takeaway line.

Usage: python render_review_figures.py            # writes figures/<variant>_review.{png,svg}
"""
from __future__ import annotations

import argparse
import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import FuncFormatter

_FMT = FuncFormatter(lambda v, _: f"{v:.3g}")   # no offset notation (near-constant fields)


def _cbar(fig, im, ax):
    cb = fig.colorbar(im, ax=ax, shrink=0.72, format=_FMT)
    cb.ax.tick_params(labelsize=8)
    return cb

from mffp_sharp.common.spectral import spectral_interp

ROOT = os.path.dirname(os.path.abspath(__file__))

PDES = {
    "phase_field_crystal_2d": {
        "eq": r"$\partial_t \psi = \nabla^2[(r + (1+\nabla^2)^2)\,\psi + \psi^3]$",
        "phys": ["r", "mean_density"],
    },
    "fisher_kpp_2d": {
        "eq": r"$\partial_t u = D\,\nabla^2 u + r\,u(1-u)$",
        "phys": ["D", "r"],
    },
    "allen_cahn_2d": {
        "eq": r"$\partial_t u = M(\varepsilon^2\,\nabla^2 u - (u^3 - u))$",
        "phys": ["eps", "mobility", "mean_composition"],
    },
}
_SYM = {"eps": r"$\varepsilon$", "mobility": "$M$", "mean_composition": r"$\bar{c}$",
        "mean_density": r"$\bar{\psi}$", "D": "$D$", "r": "$r$"}


def render(variant: str, root: str = ROOT, suffix: str = "_generated") -> str:
    d = os.path.join(root, f"{variant}{suffix}")
    meta = json.load(open(os.path.join(d, "meta.json")))
    cc = meta["condition_completeness"]
    lf_res = meta["ladder"][0][0]
    hf_res = meta["ladder"][-1][0]
    tr_lf = np.load(os.path.join(d, "train_l1.npz"))
    tr_hf = np.load(os.path.join(d, f"train_l{len(meta['ladder'])}.npz"))
    names = meta["param_names"]
    info = PDES[variant]

    fig = plt.figure(figsize=(12.5, 8.8), constrained_layout=True)
    gs = GridSpec(2, 3, figure=fig)
    for row, si in enumerate((0, 1)):
        lf = tr_lf["y"][si].reshape(lf_res, lf_res)
        hf = tr_hf["y"][si].reshape(hf_res, hf_res)
        lf_up = spectral_interp(lf, hf_res)
        err = hf - lf_up
        vmin, vmax = min(lf.min(), hf.min()), max(lf.max(), hf.max())
        e = max(abs(err.min()), abs(err.max())) or 1.0

        ax = fig.add_subplot(gs[row, 0])
        im = ax.imshow(lf, cmap="viridis", vmin=vmin, vmax=vmax, interpolation="nearest")
        ax.set_title(f"LF: real coarse solve ({lf_res}×{lf_res})", fontsize=10)
        phys = "  ".join(f"{_SYM.get(p, p)}={tr_lf['x'][si][names.index(p)]:.3g}"
                         for p in info["phys"])
        ax.set_ylabel(f"sample {si}\n{phys}", fontsize=9)
        _cbar(fig, im, ax)

        ax = fig.add_subplot(gs[row, 1])
        im = ax.imshow(hf, cmap="viridis", vmin=vmin, vmax=vmax, interpolation="nearest")
        ax.set_title(f"HF: same IC, fine solve ({hf_res}×{hf_res})", fontsize=10)
        _cbar(fig, im, ax)

        ax = fig.add_subplot(gs[row, 2])
        im = ax.imshow(err, cmap="coolwarm", vmin=-e, vmax=e, interpolation="nearest")
        rel = float(np.linalg.norm(err) / np.linalg.norm(hf))
        ax.set_title(f"Error HF − LF (LF interp. to HF grid)\n"
                     f"rel-L2 = {rel:.2e}", fontsize=10)
        _cbar(fig, im, ax)
    for ax in fig.axes:
        if hasattr(ax, "images") and ax.images:
            ax.set_xticks([]); ax.set_yticks([])

    rec = cc["reconstruction"]
    fig.suptitle(
        f"{variant} — sample round through the IC-encoded package path (2026-08-03)\n"
        f"{info['eq']}     |     LF / HF = low / high fidelity\n"
        f"condition vector = physical params + 16 IC Fourier coefficients "
        f"(ic_c0..ic_c15; full vector in meta.json)\n"
        f"Completeness certificate: {cc['verdict']} — re-solve from the condition vector "
        f"alone reproduces the field (rel-L2 = {rec['rel_L2_max']:.1e}, {rec['n_samples']} samples)",
        fontsize=10.5)
    out = os.path.join(ROOT, "figures")
    os.makedirs(out, exist_ok=True)
    for ext in ("png", "svg"):
        fig.savefig(os.path.join(out, f"{variant}_review.{ext}"), dpi=150)
    plt.close(fig)
    return os.path.join(out, f"{variant}_review.png")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=ROOT,
                    help="dataset root (e.g. benchmark_42/sharp for the production data)")
    ap.add_argument("--suffix", default="_generated",
                    help='dataset dir suffix ("" for the benchmark layout)')
    a = ap.parse_args()
    for v in PDES:
        print("wrote", render(v, a.root, a.suffix))
