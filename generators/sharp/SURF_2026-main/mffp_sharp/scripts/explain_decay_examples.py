#!/usr/bin/env python3
"""Concrete analytic functions whose Fourier transforms have KNOWN closed forms,
illustrating 1/k, 1/k^2, exponential, and Gaussian (super-exponential) decay.

Each row: the function f(x) (left) and |spectrum| with its analytic envelope (right).
The numerical FFT (dots) lands on the closed-form envelope (line) in every case.

    1/k   : sawtooth  f(x)=x on (-pi,pi)      b_n = 2(-1)^(n+1)/n          (a JUMP)
    1/k^2 : parabola  f(x)=x^2 on (-pi,pi)     a_n = 4(-1)^n / n^2          (a KINK: f' jumps)
    e^-|k|: Lorentzian f(x)=1/(1+x^2)          F(k)=pi e^-|k|              (analytic, poles at +-i)
    e^-k^2: Gaussian  f(x)=e^(-x^2/2)          F(k)=sqrt(2pi) e^(-k^2/2)   (entire: smoothest)

Run: python scripts/explain_decay_examples.py  -> data/explain/fig5_analytic_pairs.png
"""
from __future__ import annotations
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(__file__), "..", "data", "explain")


def periodic_pair(func, N=4096):
    """Fourier coefficients |c_n| of a 2pi-periodic function sampled on (-pi,pi)."""
    x = np.linspace(-np.pi, np.pi, N, endpoint=False)
    f = func(x)
    C = np.fft.rfft(f) / N
    n = np.arange(C.shape[0])
    return n, np.abs(C)


def continuous_pair(func, L=60.0, N=1 << 15):
    """Approximate continuous |F(k)| of a (decaying) function via FFT on [-L,L]."""
    x = np.linspace(-L, L, N, endpoint=False)
    dx = x[1] - x[0]
    f = func(x)
    F = np.fft.rfft(f) * dx
    k = 2 * np.pi * np.fft.rfftfreq(N, d=dx)
    return k, np.abs(F)


def main():
    os.makedirs(OUT, exist_ok=True)
    fig, ax = plt.subplots(4, 2, figsize=(12, 14), constrained_layout=True)

    # ---- row 0: sawtooth -> 1/k (jump discontinuity) --------------------------
    xp = np.linspace(-3 * np.pi, 3 * np.pi, 2000)
    saw = lambda x: ((x + np.pi) % (2 * np.pi)) - np.pi
    ax[0, 0].plot(xp, saw(xp), "C3")
    ax[0, 0].set_title("sawtooth  f(x)=x on (-pi,pi)   — JUMP (not continuous)")
    n, c = periodic_pair(saw)
    ax[0, 1].loglog(n[1:200], c[1:200], "C3.", ms=4, label="|c_n| (FFT)")
    ax[0, 1].loglog(n[1:200], (1.0 / np.pi) / n[1:200], "k-", lw=1, label="envelope  ~ 1/n")
    ax[0, 1].set_title("coefficients decay like 1/k"); ax[0, 1].legend(fontsize=8)

    # ---- row 1: parabola -> 1/k^2 (corner / kink) -----------------------------
    par = lambda x: (((x + np.pi) % (2 * np.pi)) - np.pi) ** 2
    ax[1, 0].plot(xp, par(xp), "C1")
    ax[1, 0].set_title("parabola  f(x)=x^2 on (-pi,pi)   — KINK (f continuous, f' jumps)")
    n, c = periodic_pair(par)
    ax[1, 1].loglog(n[1:200], c[1:200], "C1.", ms=4, label="|a_n| (FFT)")
    ax[1, 1].loglog(n[1:200], (4.0 / np.pi) / n[1:200] ** 2, "k-", lw=1, label="envelope  ~ 1/k^2")
    ax[1, 1].set_title("one more derivative -> one more power: 1/k^2"); ax[1, 1].legend(fontsize=8)

    # ---- row 2: Lorentzian -> e^-|k| (analytic) -------------------------------
    xc = np.linspace(-8, 8, 2000)
    lor = lambda x: 1.0 / (1.0 + x ** 2)
    ax[2, 0].plot(xc, lor(xc), "C0")
    ax[2, 0].set_title("Lorentzian  f(x)=1/(1+x^2)   — analytic (poles at x=+-i)")
    k, F = continuous_pair(lor)
    m = k < 25
    ax[2, 1].semilogy(k[m], F[m], "C0.", ms=3, label="|F(k)| (FFT)")
    ax[2, 1].semilogy(k[m], np.pi * np.exp(-k[m]), "k-", lw=1, label="envelope  pi e^-|k|")
    ax[2, 1].set_title("EXPONENTIAL decay e^-|k|  (rate = distance to nearest pole = 1)")
    ax[2, 1].legend(fontsize=8)

    # ---- row 3: Gaussian -> e^-k^2/2 (entire: smoothest) ----------------------
    gau = lambda x: np.exp(-x ** 2 / 2)
    ax[3, 0].plot(xc, gau(xc), "C2")
    ax[3, 0].set_title("Gaussian  f(x)=e^(-x^2/2)   — entire (analytic everywhere)")
    k, F = continuous_pair(gau)
    m = k < 12
    ax[3, 1].semilogy(k[m], F[m], "C2.", ms=3, label="|F(k)| (FFT)")
    ax[3, 1].semilogy(k[m], np.sqrt(2 * np.pi) * np.exp(-k[m] ** 2 / 2), "k-", lw=1,
                      label="envelope  sqrt(2pi) e^-k^2/2")
    ax[3, 1].set_title("SUPER-exponential decay e^-k^2/2  (curves down even on a log axis)")
    ax[3, 1].legend(fontsize=8)

    for a in ax[:, 0]:
        a.set_xlabel("x"); a.set_ylabel("f(x)")
    for a in ax[:, 1]:
        a.set_xlabel("wavenumber k"); a.set_ylabel("|spectrum|")

    fig.suptitle("Smoothness sets Fourier decay: jump -> 1/k, kink -> 1/k^2, "
                 "analytic -> exponential, entire -> Gaussian", fontsize=12)
    path = os.path.join(OUT, "fig5_analytic_pairs.png")
    fig.savefig(path, dpi=120)
    plt.close(fig)
    print("wrote", os.path.normpath(path))


if __name__ == "__main__":
    main()
