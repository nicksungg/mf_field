#!/usr/bin/env python3
"""Compare radial power spectra: a HIGH-frequency vs a LOW-frequency PDE solution.

Uses the real design-batch HF (128^2) fields: Cahn-Hilliard (sharp interface =
high-frequency content) vs Kuramoto-Sivashinsky (smooth = low-frequency content).

Answers: higher radial wavenumber = finer spatial scale = HIGHER spatial frequency.
The sharp field keeps energy out to high k (fat tail); the smooth field's spectrum
collapses early. The gap on the right is exactly the "high-frequency content".

Run (after generating the design batch): python scripts/explain_spectra_compare.py
  -> data/explain/fig_spectra_compare.png
"""
from __future__ import annotations
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from mffp_sharp.common import io

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, "..", "data", "design")
OUT = os.path.join(HERE, "..", "data", "explain")


def radial_spectrum(field):
    F = np.fft.fftshift(np.fft.fft2(field))
    psd = np.abs(F) ** 2
    n = field.shape[0]
    c = n // 2
    y, x = np.indices((n, n))
    r = np.hypot(x - c, y - c).astype(int)
    tbin = np.bincount(r.ravel(), psd.ravel())
    cnt = np.bincount(r.ravel())
    rad = tbin / np.maximum(cnt, 1)
    return np.arange(len(rad)), rad


def hf_field(pde):
    d = io.read_dataset(os.path.join(DATA, f"{pde}_sample.h5"))
    return d["bundles"][0]["aligned"][d["hf_res"]]


def main():
    os.makedirs(OUT, exist_ok=True)
    ch = hf_field("cahn_hilliard")            # sharp interface  -> HIGH frequency
    ks = hf_field("kuramoto_sivashinsky")     # smooth           -> LOW frequency

    fig, ax = plt.subplots(1, 3, figsize=(15, 4.6), constrained_layout=True)

    ax[0].imshow(ch, origin="lower", cmap="viridis")
    ax[0].set_title("Cahn-Hilliard HF\n(sharp interface = HIGH frequency)", fontsize=10)
    ax[0].set_xticks([]); ax[0].set_yticks([])

    ax[1].imshow(ks, origin="lower", cmap="viridis")
    ax[1].set_title("Kuramoto-Sivashinsky HF\n(smooth = LOW frequency)", fontsize=10)
    ax[1].set_xticks([]); ax[1].set_yticks([])

    for fld, label, col in [(ch, "Cahn-Hilliard (sharp)", "C3"),
                            (ks, "Kuramoto-Sivashinsky (smooth)", "C0")]:
        k, p = radial_spectrum(fld)
        p = p / p[1]                          # normalize at lowest nonzero k
        ax[2].loglog(k[1:], p[1:], col, label=label)
    n = ch.shape[0]
    ax[2].axvspan(n // 4, n // 2, color="purple", alpha=0.06)
    ax[2].text(n // 4 + 1, 1e-1, "high-wavenumber\nband", color="purple", fontsize=8)
    ax[2].set_xlabel("radial wavenumber k_r   (->  finer scales / higher frequency)")
    ax[2].set_ylabel("normalized power (log)")
    ax[2].set_title("radial power spectra overlaid", fontsize=10)
    ax[2].legend(fontsize=8, loc="lower left")

    fig.suptitle("Higher radial wavenumber = finer spatial scale = higher frequency.  "
                 "The sharp field keeps energy at high k; the smooth one drops off early.",
                 fontsize=11)
    path = os.path.join(OUT, "fig_spectra_compare.png")
    fig.savefig(path, dpi=120)
    plt.close(fig)
    print("wrote", os.path.normpath(path))


if __name__ == "__main__":
    main()
