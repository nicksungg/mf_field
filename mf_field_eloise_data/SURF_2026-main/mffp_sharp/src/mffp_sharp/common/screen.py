"""Sharpness auto-screen: energy-above-cutoff + sharpness coordinate + LF-HF gap.

The single metric is energy-above-cutoff
    f(k_c) = sum_{|k|>k_c} |u_hat|^2 / sum_{|k|>0} |u_hat|^2      (DC excluded),
the complementary cumulative radial spectrum. Form-agnostic (power-law, knee,
exponential, or spectral-peak spectra all handled). Spectral SLOPE is a descriptor
only -- never the gate. Works for 1D and 2D fields.

Gating: the only binary is the dimension-matched KS FLOOR (drop a candidate smoother
than the smooth control). Otherwise candidates are RANKED by the sharpness coordinate
    s = (f_cand - f_ks) / (f_euler - f_ks)
and by the LF-HF high-k gap (the quantity MF fusion rides on). No hand-picked f cut.
"""
from __future__ import annotations

import numpy as np


def radial_power(field: np.ndarray):
    """Integer-binned radial power spectrum. Returns (kr_int, power) with DC at index 0."""
    field = np.asarray(field)
    F = np.fft.fftn(field)
    psd = np.abs(F) ** 2
    n = field.shape[0]
    freqs = [np.fft.fftfreq(n) * n for _ in range(field.ndim)]
    grids = np.meshgrid(*freqs, indexing="ij")
    kr = np.sqrt(sum(g ** 2 for g in grids))
    kr_int = np.rint(kr).astype(int).ravel()
    power = np.bincount(kr_int, weights=psd.ravel())
    return np.arange(len(power)), power


def energy_above_cutoff(field: np.ndarray, k_c: float) -> float:
    """f(k_c) = energy at radial wavenumber > k_c, normalized by total non-DC energy."""
    kr, power = radial_power(field)
    nondc = power.copy()
    nondc[0] = 0.0
    total = nondc.sum()
    if total <= 0.0:
        return 0.0
    above = nondc[kr > k_c].sum()
    return float(above / total)


def cumulative_curve(field: np.ndarray, k_cs) -> dict:
    """f(k_c) over several cutoffs (the curve reported until FNO k_max is known)."""
    return {int(kc): energy_above_cutoff(field, kc) for kc in k_cs}


def sharpness_coordinate(f_cand: float, f_ks: float, f_euler: float) -> float:
    """s = (f_cand - f_ks)/(f_euler - f_ks); clamp to >= 0; nan if anchors coincide."""
    denom = f_euler - f_ks
    if abs(denom) < 1e-30:
        return float("nan")
    return float(max(0.0, (f_cand - f_ks) / denom))


def lf_hf_gap(lf_up: np.ndarray, hf: np.ndarray, k_c: float) -> float:
    """High-k content of the residual (hf - lf_up), both on the HF grid."""
    return energy_above_cutoff(np.asarray(hf) - np.asarray(lf_up), k_c)


def passes_floor(f_cand: float, f_ks_dimmatched: float) -> bool:
    """Floor: a candidate must be at least as sharp as the dimension-matched KS control."""
    return f_cand >= f_ks_dimmatched
