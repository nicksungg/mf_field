"""Fidelity ladder: resolution levels and dyadic up-interpolation to the HF grid.

Every fidelity is interpolated up onto the HF grid so residuals (HF - LF) are
well-defined. The ladder is dyadic (each level doubles), so coarse grid points
land exactly on HF grid points and the up-interpolation is a clean nested
operation rather than an artifact-prone resample.

We keep BOTH the raw native-grid field (provenance) and the up-interpolated
version (for residuals), per the methodology template in TO-DO.md.
"""
from __future__ import annotations

import numpy as np
from scipy.interpolate import RegularGridInterpolator


def _cell_centers(n: int) -> np.ndarray:
    """Cell-center coordinates on [0, 1] for an n-cell grid (finite-volume convention)."""
    return (np.arange(n) + 0.5) / n


def upsample_to_hf(field: np.ndarray, hf_res: int, order: str = "linear") -> np.ndarray:
    """Interpolate an LF field up onto the HF grid.

    Accepts a 1D field (length res) or a square 2D field (res x res). Uses
    cell-center coordinates on the unit domain so LF and HF share the same physical
    domain. `order` is "linear" (default) or "nearest".

    1D uses np.interp (endpoint-clamped at the boundary cell centers); 2D uses
    RegularGridInterpolator with linear extrapolation, unchanged from before.
    """
    field = np.asarray(field, dtype=np.float64)

    if field.ndim == 1:
        res = field.shape[0]
        if res == hf_res:
            return field.copy()
        src = _cell_centers(res)
        dst = _cell_centers(hf_res)
        if order == "nearest":
            idx = np.clip(np.round(dst * res - 0.5).astype(int), 0, res - 1)
            return field[idx]
        return np.interp(dst, src, field)

    if field.ndim == 2:
        res = field.shape[0]
        assert field.shape == (res, res), f"expected square field, got {field.shape}"
        if res == hf_res:
            return field.copy()
        src = (_cell_centers(res), _cell_centers(res))
        interp = RegularGridInterpolator(
            src, field, method=order, bounds_error=False, fill_value=None
        )
        yy, xx = np.meshgrid(_cell_centers(hf_res), _cell_centers(hf_res), indexing="ij")
        pts = np.stack([yy.ravel(), xx.ravel()], axis=-1)
        return interp(pts).reshape(hf_res, hf_res)

    raise ValueError(f"unsupported field.ndim={field.ndim}; expected 1 or 2")


def assemble_sample(raw_fields: dict[int, np.ndarray], hf_res: int) -> dict:
    """Bundle a single sample's per-resolution raw fields into the stored layout.

    Parameters
    ----------
    raw_fields : {resolution: native-grid field}
    hf_res     : the high-fidelity resolution (the common grid for residuals)

    Returns a dict with both the raw fields and HF-aligned versions, ready for io.py.
    """
    aligned = {res: upsample_to_hf(f, hf_res) for res, f in raw_fields.items()}
    return {
        "raw": raw_fields,        # native-grid fields, for provenance
        "aligned": aligned,       # all on the HF grid, for residuals/training
        "hf_res": hf_res,
    }
