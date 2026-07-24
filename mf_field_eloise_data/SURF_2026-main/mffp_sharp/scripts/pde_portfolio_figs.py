#!/usr/bin/env python3
"""Clean HF-field thumbnails for docs/pde-summary.md: one per PDE + a combined
shock -> sharp-interface -> smooth strip. Loads existing sample HDF5 (no solving).

Run on the box: python scripts/pde_portfolio_figs.py -> data/explain/{pde}_field.png, pde_portfolio.png
"""
from __future__ import annotations
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from mffp_sharp.common import io

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, "..", "data", "sample")
OUT = os.path.join(HERE, "..", "data", "explain")
PDES = [
    ("euler", "2D Euler - shock", "density"),
    ("cahn_hilliard", "Cahn-Hilliard - sharp interface", "composition c"),
    ("kuramoto_sivashinsky", "Kuramoto-Sivashinsky - smooth control", "u - <u>"),
]


def hf_field(pde):
    d = io.read_dataset(os.path.join(DATA, f"{pde}_sample.h5"))
    return d["bundles"][0]["aligned"][d["hf_res"]]


def main():
    os.makedirs(OUT, exist_ok=True)
    fields = {p: hf_field(p) for p, _, _ in PDES}

    # combined strip
    fig, ax = plt.subplots(1, 3, figsize=(15, 5), constrained_layout=True)
    for a, (pde, title, _) in zip(ax, PDES):
        im = a.imshow(fields[pde], origin="lower", cmap="viridis")
        a.set_title(title, fontsize=11); a.set_xticks([]); a.set_yticks([])
        fig.colorbar(im, ax=a, fraction=0.046)
    fig.suptitle("Portfolio HF fields: shock -> sharp interface -> smooth", fontsize=13)
    fig.savefig(os.path.join(OUT, "pde_portfolio.png"), dpi=120); plt.close(fig)

    # individual thumbnails
    for pde, title, qty in PDES:
        fig, a = plt.subplots(figsize=(4.6, 4.3), constrained_layout=True)
        im = a.imshow(fields[pde], origin="lower", cmap="viridis")
        a.set_title(f"{title}\n(HF field: {qty})", fontsize=10)
        a.set_xticks([]); a.set_yticks([]); fig.colorbar(im, ax=a, fraction=0.046)
        fig.savefig(os.path.join(OUT, f"{pde}_field.png"), dpi=120); plt.close(fig)
    print("done -> data/explain/{euler,cahn_hilliard,kuramoto_sivashinsky}_field.png + pde_portfolio.png")


if __name__ == "__main__":
    main()
