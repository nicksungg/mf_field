"""Shared spectral helpers used by the Fourier-spectral PDE solvers.

Both Cahn-Hilliard and KS need the SAME band-limited up-interpolation so every
ladder level solves the identical continuous IC; it was duplicated in both solver
modules. Factored here and extended to 1D for the 1D spectral candidates. Also
provides the discrete (5-point) -Laplacian Fourier symbol that the semi-implicit
schemes diagonalize against (bounded -> no Gibbs blow-up on under-resolved coarse
grids; this is what makes the coarse solve a CONSISTENT solve, not an artifact).
"""
from __future__ import annotations

import numpy as np


def spectral_interp(field: np.ndarray, n_fine: int) -> np.ndarray:
    """Exact band-limited (zero-pad) interpolation of a periodic field to n_fine.

    1D -> length n_fine; 2D -> (n_fine, n_fine). `n_fine == n` returns a float64
    copy. Requires (n_fine - n) even (true for the dyadic ladder). Mirrors the
    original CH/KS 2D routine and applies the analogous 1D zero-pad.
    """
    field = np.asarray(field)
    if field.ndim == 1:
        n_c = field.shape[0]
        if n_fine == n_c:
            return field.astype(np.float64).copy()
        F = np.fft.fftshift(np.fft.fft(field))
        pad = (n_fine - n_c) // 2
        Fp = np.zeros(n_fine, dtype=complex)
        Fp[pad:pad + n_c] = F
        out = np.fft.ifft(np.fft.ifftshift(Fp)) * (n_fine / n_c)
        return np.real(out)
    if field.ndim == 2:
        n_c = field.shape[0]
        if n_fine == n_c:
            return field.astype(np.float64).copy()
        F = np.fft.fftshift(np.fft.fft2(field))
        pad = (n_fine - n_c) // 2
        Fp = np.zeros((n_fine, n_fine), dtype=complex)
        Fp[pad:pad + n_c, pad:pad + n_c] = F
        out = np.fft.ifft2(np.fft.ifftshift(Fp)) * (n_fine / n_c) ** 2
        return np.real(out)
    raise ValueError(f"unsupported field.ndim={field.ndim}; expected 1 or 2")


def neg_laplacian_symbol(res: int, h: float, ndim: int) -> np.ndarray:
    """Discrete (5-point) -Laplacian Fourier symbol: >= 0, bounded.

    Returns shape (res,) for ndim=1 or (res, res) for ndim=2. This is the same
    symbol Cahn-Hilliard diagonalizes against; using it (rather than the continuous
    k^2) keeps the coarse-grid solve bounded and consistent.
    """
    fr = np.fft.fftfreq(res)
    cx = np.cos(2 * np.pi * fr)
    if ndim == 1:
        return (2.0 / h ** 2) * (1.0 - cx)
    if ndim == 2:
        MX, MY = np.meshgrid(cx, cx, indexing="ij")
        return (2.0 / h ** 2) * (2.0 - MX - MY)
    raise ValueError(f"unsupported ndim={ndim}; expected 1 or 2")
