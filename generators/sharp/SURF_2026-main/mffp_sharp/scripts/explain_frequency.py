#!/usr/bin/env python3
"""Explanatory figures for docs/answers.md.

Self-contained (synthetic fields) so it needs no generated data. Run on the box:
    python scripts/explain_frequency.py            # writes to data/explain/
Produces:
    fig1_resolution.png         -- LF vs HF resolution: native blocky vs upsampled-blurry vs true
    fig2_radial_wavenumber.png  -- what radial wavenumber means (2D spectrum + rings + radial avg)
    fig3_spectral_decay.png     -- the money plot: sharp vs smooth spectral decay + FNO cutoff
    fig4_smoothness_decay.png   -- why exponential decay = smoother: e^-ak beats every 1/k^m
"""
from __future__ import annotations

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(__file__), "..", "data", "explain")


# ----- helpers ---------------------------------------------------------------

def radial_spectrum(field: np.ndarray):
    """Azimuthally-averaged power vs integer radial wavenumber."""
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


def tanh_interface(n: int, eps: float) -> np.ndarray:
    """A circular phase interface of width eps on an n x n unit grid (sharp but continuous)."""
    xs = (np.arange(n) + 0.5) / n
    X, Y = np.meshgrid(xs, xs, indexing="ij")
    dist = np.hypot(X - 0.5, Y - 0.5) - 0.25
    return np.tanh(dist / eps)


def step_field(n: int) -> np.ndarray:
    """A true discontinuity (half-plane jump) -- slowest spectral decay."""
    f = np.ones((n, n))
    f[:, : n // 2] = -1.0
    return f


def smooth_field(n: int) -> np.ndarray:
    """A smooth low-wavenumber field (sum of a few low harmonics) -- fast decay."""
    xs = (np.arange(n) + 0.5) / n
    X, Y = np.meshgrid(xs, xs, indexing="ij")
    return (np.sin(2 * np.pi * X) * np.cos(2 * np.pi * Y)
            + 0.5 * np.sin(4 * np.pi * X) + 0.3 * np.cos(2 * np.pi * Y))


def block_downsample(field: np.ndarray, n_coarse: int) -> np.ndarray:
    """Average-pool a fine field to n_coarse (a stand-in for a coarse-grid solve)."""
    n = field.shape[0]
    f = n // n_coarse
    return field.reshape(n_coarse, f, n_coarse, f).mean(axis=(1, 3))


def upsample_nearest(coarse: np.ndarray, n_fine: int) -> np.ndarray:
    rep = n_fine // coarse.shape[0]
    return np.kron(coarse, np.ones((rep, rep)))


# ----- figure 1: resolution --------------------------------------------------

def fig_resolution():
    n_hf, n_lf, eps = 128, 32, 0.02
    true_hf = tanh_interface(n_hf, eps)
    lf_native = block_downsample(true_hf, n_lf)           # "LF solve" (coarse)
    lf_up = upsample_nearest(lf_native, n_hf)             # LF shown on HF grid
    resid = true_hf - lf_up

    fig, ax = plt.subplots(1, 4, figsize=(17, 4.4), constrained_layout=True)
    for a, img, title, interp in [
        (ax[0], true_hf, f"HF: true 128x128 solve", "nearest"),
        (ax[1], lf_native, f"LF: 32x32 solve (native, blocky)", "nearest"),
        (ax[2], lf_up, "LF upsampled to 128x128\n(same pixels, no new detail = blurry)", "nearest"),
        (ax[3], resid, "HF - LF residual\n(= the missing sharp content)", "nearest"),
    ]:
        cmap = "coolwarm" if "residual" in title else "viridis"
        im = a.imshow(img, origin="lower", cmap=cmap, interpolation=interp)
        a.set_title(title, fontsize=10); a.set_xticks([]); a.set_yticks([])
        fig.colorbar(im, ax=a, fraction=0.046)
    fig.suptitle("Q1: LF and HF ARE different resolutions; the benchmark plots LF upsampled "
                 "onto the HF grid (needed to subtract for residuals)", fontsize=11)
    _save(fig, "fig1_resolution.png")


# ----- figure 2: radial wavenumber -------------------------------------------

def fig_radial_wavenumber():
    n = 128
    field = tanh_interface(n, 0.02)
    F = np.fft.fftshift(np.fft.fft2(field))
    logpsd = np.log10(np.abs(F) ** 2 + 1e-6)
    k, rad = radial_spectrum(field)

    fig, ax = plt.subplots(1, 2, figsize=(12, 5), constrained_layout=True)
    c = n // 2
    im = ax[0].imshow(logpsd, origin="lower", cmap="magma",
                      extent=[-c, c, -c, c])
    for rr in (8, 20, 40):
        ax[0].add_patch(plt.Circle((0, 0), rr, fill=False, color="cyan", lw=1.2))
        ax[0].text(rr / 1.41, rr / 1.41, f"k_r={rr}", color="cyan", fontsize=8)
    ax[0].set_title("2D power spectrum (log).  kx right, ky up.\n"
                    "radial wavenumber k_r = distance from center", fontsize=10)
    ax[0].set_xlabel("kx"); ax[0].set_ylabel("ky")
    fig.colorbar(im, ax=ax[0], fraction=0.046)

    ax[1].semilogy(k[1:], rad[1:])
    ax[1].set_title("radial power spectrum\n(average power on each ring vs k_r)", fontsize=10)
    ax[1].set_xlabel("radial wavenumber k_r  (left=smooth/large-scale, right=sharp/fine-scale)")
    ax[1].set_ylabel("power (log)")
    ax[1].axvline(n / 2, ls=":", color="gray"); ax[1].text(n / 2 - 18, rad[1], "Nyquist", fontsize=8)
    fig.suptitle("Q2: radial wavenumber collapses the 2D spectrum (left) to a 1D curve (right) "
                 "by averaging over each ring", fontsize=11)
    _save(fig, "fig2_radial_wavenumber.png")


# ----- figure 3: spectral decay (the money plot) -----------------------------

def fig_spectral_decay():
    n = 256
    cases = [
        ("Euler-like: true discontinuity (shock)", step_field(n), "C3"),
        ("Cahn-Hilliard-like: interface eps=0.01 (thin)", tanh_interface(n, 0.01), "C1"),
        ("Cahn-Hilliard-like: interface eps=0.04 (wider)", tanh_interface(n, 0.04), "C2"),
        ("KS / deck-like: smooth field", smooth_field(n), "C0"),
    ]
    fig, ax = plt.subplots(figsize=(9, 6), constrained_layout=True)
    for label, fld, col in cases:
        k, rad = radial_spectrum(fld)
        rad = rad / rad[1]                                # normalize at lowest nonzero k
        ax.loglog(k[1:n // 2], rad[1:n // 2], col, label=label)
    # 1/k^2 reference (power ~ amplitude^2 ~ (1/k)^2 for a jump)
    kk = np.arange(2, n // 2)
    ax.loglog(kk, (kk / 2.0) ** -2.0, "k--", lw=1, alpha=0.6, label="1/k^2 reference (discontinuity)")
    # illustrative FNO mode cutoff
    ax.axvline(12, color="purple", ls=":", lw=2)
    ax.text(13, 1e-3, "example FNO\nmode cutoff", color="purple", fontsize=9)
    ax.fill_betweenx([1e-12, 1e1], 12, n // 2, color="purple", alpha=0.05)
    ax.set_xlabel("radial wavenumber k_r")
    ax.set_ylabel("normalized power (log)")
    ax.set_ylim(1e-10, 2)
    ax.set_title("Q3: sharp fields keep energy at high k (slow decay); smooth fields don't.\n"
                 "Energy to the RIGHT of the cutoff is what FNO truncates away.")
    ax.legend(fontsize=8, loc="lower left")
    _save(fig, "fig3_spectral_decay.png")


def fig_smoothness_decay():
    """Pure math panel: a derivative buys a 1/k factor; exponential beats every power law."""
    k = np.linspace(1, 80, 800)
    a = 0.18
    curves = [
        ("1/k   (jump / shock: 0 derivatives)", 1.0 / k, "C3"),
        ("1/k^2 (kink: 1 derivative)", 1.0 / k ** 2, "C1"),
        ("1/k^4 (3 derivatives)", 1.0 / k ** 4, "C2"),
        (f"e^(-{a}k) (analytic: infinitely smooth)", np.exp(-a * k), "C0"),
    ]
    fig, ax = plt.subplots(1, 2, figsize=(13, 5.2), constrained_layout=True)

    # Left: log-log. Power laws are straight lines; exponential curves down through them all.
    for label, y, col in curves:
        style = "-" if "e^" not in label else "-"
        lw = 2.6 if "e^" in label else 1.8
        ax[0].loglog(k, y, col, lw=lw, label=label)
    ax[0].set_title("log-log: each derivative tilts the line one power steeper;\n"
                    "the exponential (blue) curves DOWN past every power law", fontsize=10)
    ax[0].set_xlabel("wavenumber k"); ax[0].set_ylabel("spectral amplitude")
    ax[0].set_ylim(1e-8, 2); ax[0].legend(fontsize=8, loc="lower left")

    # Right: semi-log. Exponential is a straight line; power laws flatten and sit ABOVE it.
    for label, y, col in curves:
        lw = 2.6 if "e^" in label else 1.8
        ax[1].semilogy(k, y, col, lw=lw, label=label)
    # mark where the exponential overtakes (drops below) each power law
    for label, y, col in curves[:3]:
        below = np.where(np.exp(-a * k) < y, k, np.inf)
        kc = below[np.isfinite(below)]
        if len(kc):
            ax[1].axvline(kc.min(), color=col, ls=":", lw=1, alpha=0.7)
    ax[1].set_title("semi-log: the exponential (blue) is a straight line and ends up\n"
                    "BELOW every power law -> 'smoother than any finite # of derivatives'",
                    fontsize=10)
    ax[1].set_xlabel("wavenumber k"); ax[1].set_ylabel("spectral amplitude")
    ax[1].set_ylim(1e-8, 2); ax[1].legend(fontsize=8, loc="upper right")

    fig.suptitle("Why exponential decay = smoothest: a function with m derivatives decays like "
                 "1/k^(m+1); analytic (infinitely smooth) decays exponentially, beating them all",
                 fontsize=11)
    _save(fig, "fig4_smoothness_decay.png")


def _save(fig, name):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=120)
    plt.close(fig)
    print("wrote", os.path.normpath(path))


if __name__ == "__main__":
    fig_resolution()
    fig_radial_wavenumber()
    fig_spectral_decay()
    fig_smoothness_decay()
    print("done -> data/explain/")
