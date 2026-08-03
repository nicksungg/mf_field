"""Fidelity ladder: resolution levels and dyadic up-interpolation to the HF grid.

Every fidelity is interpolated up onto the HF grid so residuals (HF - LF) are
well-defined. The ladder is dyadic (each level doubles), so on node-sampled
grids coarse points land exactly on HF grid points and the up-interpolation is
a clean nested operation rather than an artifact-prone resample.

We keep BOTH the raw native-grid field (provenance) and the up-interpolated
version (for residuals), per the methodology template in TO-DO.md.

REGISTRATION CONVENTIONS (registration-defect fix, 2026-08-01 note item 2).
The old implementation applied ONE coordinate map — cell-centred, x_j =
(j+0.5)/n — to every PDE.  That map is only correct for finite-volume solver
output (PyClaw cell averages).  The pseudo-spectral / periodic-FD solvers in
this package sample their fields at NODES x_j = j/n, and helmholtz on interior
Dirichlet nodes x_j = (j+1)/(n+1); pushing node data through the cell-centred
map displaces every value by (r-1)/2 HF cells (half a coarse cell at r=2),
baking a registration shift into the stored aligned arrays and into the
LF-vs-HF fidelity-gap metrics computed from them.  The raw native-grid arrays
were always correct.

This module now dispatches per PDE, mirroring the audited implementations in
`mffp_autoresearch/round2/eval/panel_data.py` (ADR r2-0001) and
`mf_field/factory_mffp/models/_common/lf_registration.py`:

  - node_periodic  : HF node k samples LF index k*h/H exactly, periodic wrap
                     (variant C).  Exact at shared nodes on a nested ladder:
                     up[::r, ::r] == lf.
  - node_dirichlet : interior-node coordinate map x_j = (j+1)/(n+1), clamped
                     at the boundary (variant E; helmholtz).
  - cell_centered  : the original cell-centred map, kept verbatim — it is the
                     CORRECT convention for finite-volume (PyClaw) output.

An unclassified PDE RAISES (convention assignment is a design decision, never
a default), matching the eval layer's policy.
"""
from __future__ import annotations

import numpy as np
from scipy.interpolate import RegularGridInterpolator
from scipy.ndimage import map_coordinates

# ── per-PDE convention classification ────────────────────────────────────────
# Keyed by solver module name (`pdes/<name>.py`, the `module:` field of a
# config block).  Grounds: pseudo-spectral (np.fft) and periodic np.roll-stencil
# solvers evaluate on nodes x_j = j*L/n; PyClaw solvers store cell averages at
# p_centers x_j = (j+0.5)*L/n; helmholtz solves on interior Dirichlet nodes
# x_j = (j+1)*h, h = L/(n+1).
PERIODIC_NODE_PDES = {
    "allen_cahn",
    "cahn_hilliard",
    "fisher_kpp",
    "gray_scott",
    "kdv",
    "kuramoto_sivashinsky",
    "nls",
    "phase_field_crystal",
    "porous_medium",
    "sine_gordon",
    "swift_hohenberg",
}
DIRICHLET_NODE_PDES = {"helmholtz"}
CELL_CENTERED_PDES = {"burgers", "euler", "shallow_water", "sod"}

CONVENTIONS = ("node_periodic", "node_dirichlet", "cell_centered")


def convention_for_pde(pde: str) -> str:
    """Return the registration convention for a solver module name.

    Raises on an unclassified PDE — mirroring the eval layer
    (`panel_data.copylf_prediction`), a convention is assigned by audit of the
    solver's grid, never defaulted.
    """
    if pde in PERIODIC_NODE_PDES:
        return "node_periodic"
    if pde in DIRICHLET_NODE_PDES:
        return "node_dirichlet"
    if pde in CELL_CENTERED_PDES:
        return "cell_centered"
    raise ValueError(
        f"PDE module {pde!r} has no grid-registration convention assigned; "
        "classify it in mffp_sharp.common.ladder (PERIODIC_NODE_PDES / "
        "DIRICHLET_NODE_PDES / CELL_CENTERED_PDES) after auditing the "
        "solver's grid. Refusing to default (registration-defect note "
        "2026-08-01, item 2)."
    )


def _cell_centers(n: int) -> np.ndarray:
    """Cell-center coordinates on [0, 1] for an n-cell grid (finite-volume convention)."""
    return (np.arange(n) + 0.5) / n


def _map_order(order: str) -> int:
    if order == "linear":
        return 1
    if order == "nearest":
        return 0
    raise ValueError(f"unsupported order {order!r}; expected 'linear' or 'nearest'")


def _upsample_cell_centered(field: np.ndarray, hf_res: int, order: str) -> np.ndarray:
    """The original (pre-fix) map, verbatim: correct for finite-volume data."""
    if field.ndim == 1:
        res = field.shape[0]
        src = _cell_centers(res)
        dst = _cell_centers(hf_res)
        if order == "nearest":
            idx = np.clip(np.round(dst * res - 0.5).astype(int), 0, res - 1)
            return field[idx]
        return np.interp(dst, src, field)

    res = field.shape[0]
    src = (_cell_centers(res), _cell_centers(res))
    interp = RegularGridInterpolator(
        src, field, method=order, bounds_error=False, fill_value=None
    )
    yy, xx = np.meshgrid(_cell_centers(hf_res), _cell_centers(hf_res), indexing="ij")
    pts = np.stack([yy.ravel(), xx.ravel()], axis=-1)
    return interp(pts).reshape(hf_res, hf_res)


def _upsample_node_periodic(field: np.ndarray, hf_res: int, order: str) -> np.ndarray:
    """Variant C (panel_data/lf_registration): HF node k samples LF index
    k*h/H, linear, periodic wrap.  Exact at shared nodes when nested."""
    res = field.shape[0]
    if hf_res % res:
        raise ValueError(
            f"node_periodic requires a nested (dyadic) ladder, got {res} -> {hf_res}"
        )
    if field.ndim == 1:
        coords = [np.arange(hf_res, dtype=np.float64) * (res / hf_res)]
        return map_coordinates(field, coords, order=_map_order(order), mode="grid-wrap")
    ax = np.arange(hf_res, dtype=np.float64) * (res / hf_res)
    coords = np.meshgrid(ax, ax, indexing="ij")
    return map_coordinates(field, coords, order=_map_order(order), mode="grid-wrap")


def _upsample_node_dirichlet(field: np.ndarray, hf_res: int, order: str) -> np.ndarray:
    """Variant E (panel_data/lf_registration): interior Dirichlet nodes
    x_j = (j+1)/(n+1), clamped at the boundary."""
    res = field.shape[0]
    idx = (np.arange(hf_res, dtype=np.float64) + 1.0) * (res + 1) / (hf_res + 1) - 1.0
    if field.ndim == 1:
        return map_coordinates(field, [idx], order=_map_order(order), mode="nearest")
    coords = np.meshgrid(idx, idx, indexing="ij")
    return map_coordinates(field, coords, order=_map_order(order), mode="nearest")


_UPSAMPLERS = {
    "node_periodic": _upsample_node_periodic,
    "node_dirichlet": _upsample_node_dirichlet,
    "cell_centered": _upsample_cell_centered,
}


def upsample_to_hf(
    field: np.ndarray, hf_res: int, order: str = "linear", *, convention: str
) -> np.ndarray:
    """Interpolate an LF field up onto the HF grid under an explicit convention.

    Accepts a 1D field (length res) or a square 2D field (res x res). `order`
    is "linear" (default) or "nearest".  `convention` is required — one of
    CONVENTIONS; use `convention_for_pde()` to look it up from the solver
    module name.  There is deliberately no default (registration-defect note
    2026-08-01, item 2).
    """
    if convention not in CONVENTIONS:
        raise ValueError(
            f"unknown convention {convention!r}; expected one of {CONVENTIONS}"
        )
    field = np.asarray(field, dtype=np.float64)
    if field.ndim not in (1, 2):
        raise ValueError(f"unsupported field.ndim={field.ndim}; expected 1 or 2")
    if field.ndim == 2:
        res = field.shape[0]
        assert field.shape == (res, res), f"expected square field, got {field.shape}"
    if field.shape[0] == hf_res:
        return field.copy()
    return _UPSAMPLERS[convention](field, hf_res, order)


def assemble_sample(raw_fields: dict[int, np.ndarray], hf_res: int, *, pde: str) -> dict:
    """Bundle a single sample's per-resolution raw fields into the stored layout.

    Parameters
    ----------
    raw_fields : {resolution: native-grid field}
    hf_res     : the high-fidelity resolution (the common grid for residuals)
    pde        : solver module name; selects the registration convention
                 (raises on an unclassified PDE)

    Returns a dict with both the raw fields and HF-aligned versions, ready for
    io.py, plus the convention used (provenance).
    """
    convention = convention_for_pde(pde)
    aligned = {
        res: upsample_to_hf(f, hf_res, convention=convention)
        for res, f in raw_fields.items()
    }
    return {
        "raw": raw_fields,        # native-grid fields, for provenance
        "aligned": aligned,       # all on the HF grid, for residuals/training
        "hf_res": hf_res,
        "pde": pde,
        "convention": convention,
    }
