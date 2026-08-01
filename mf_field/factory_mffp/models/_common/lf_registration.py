"""Per-dataset grid-registration dispatch for model-side field resampling.

WHY THIS EXISTS (registration defect, 2026-08-01 note, item 1).  Every family
in this zoo used to lift LF fields to the working grid with
`F.interpolate(mode="bilinear", align_corners=False)`, which is bit-identical
to `scipy.ndimage.zoom(..., order=1, grid_mode=True)` — a CELL-CENTRED
coordinate map.  The sharp pseudo-spectral datasets are NODE-sampled and
dyadically nested, so that map displaces every value by (r-1)/2 HF cells
(half a cell at r=2).  Round 1's scoring reference carried the same shift and
it cancelled; the round-2 reference (`mffp_autoresearch/round2/eval/
panel_data.py`, ADR r2-0001) is correctly registered, so a model that still
lifts LF cell-centred feeds itself a half-cell-shifted field and pays for it.

This module gives model code the SAME per-dataset dispatch the eval layer
got.  The three interpolators and the dataset classification sets are a
verbatim transcription of `round2/eval/panel_data.py` @ substrate 9e10d414.

Fallback policy (deliberately DIFFERENT from the eval layer): the eval layer
RAISES on an unclassified dataset, because a reference convention is an ADR
decision.  Model-side, an unclassified dataset falls back to the legacy
cell-centred path — that is the status-quo behaviour for every factory smoke
dataset (era5, pm_test, poisson_local, sharp_generated, ...), none of which
has been audited, and `align_corners=False` is CORRECT for genuinely
cell-centred data.  Only the datasets proven node-sampled (the sharp panel)
and helmholtz's interior-node Dirichlet grid are dispatched away from legacy.

CACHE CAVEAT (same as fire_core.py): `eval/score.py::code_hash` hashes only
`models/<family>/**/*.py`, so editing THIS file does not invalidate family
caches.  After any edit here, re-run affected families with `--no_cache`.

Registration invariant for nested node data (the one-line test that would
have caught the defect on day one):

    resample_fields(coarse, lf_grid, hf_grid, ds)[:, ::r0, ::r1] == coarse

`models/_common/test_lf_registration.py` asserts it, plus the index-ramp
probe (bilinear interpolation of a linear ramp returns the source coordinate
each output pixel read).
"""
from __future__ import annotations

import numpy as np
import torch
import torch.nn.functional as F
from scipy.ndimage import map_coordinates

# ── begin verbatim block from round2/eval/panel_data.py @ 9e10d414 ───────
PERIODIC_NODE_DATASETS = {
    "sharp__phase_field_crystal_2d",
    "sharp__allen_cahn_2d",
    "sharp__fisher_kpp_2d",
    "sharp__cahn_hilliard",
}
DIRICHLET_NODE_DATASETS = {"ext__helmholtz_2d"}
LEGACY_CELL_DATASETS = {"heat_local", "fluid", "sharp__sod_1d", "ifc_poisson", "ifc_heat"}


def _node_aligned_periodic_up(lf2d: np.ndarray, hf_grid: tuple) -> np.ndarray:
    """Variant C: HF pixel (k,l) samples LF index (k/r0, l/r1), periodic wrap.

    Exact at shared nodes: up[::r0, ::r1] == lf bit-for-bit when nested.
    """
    h, w = lf2d.shape
    H, W = hf_grid
    if H % h or W % w:
        raise ValueError(f"variant C requires a nested grid, got {h, w} -> {H, W}")
    coords = np.meshgrid(
        np.arange(H, dtype=np.float64) * (h / H),
        np.arange(W, dtype=np.float64) * (w / W),
        indexing="ij",
    )
    return map_coordinates(lf2d, coords, order=1, mode="grid-wrap")


def _dirichlet_node_up(lf2d: np.ndarray, hf_grid: tuple) -> np.ndarray:
    """Variant E: interior-node Dirichlet grids x_j=(j+1)/(n+1) (helmholtz)."""
    h, w = lf2d.shape
    H, W = hf_grid
    jj = (np.arange(H, dtype=np.float64) + 1.0) * (h + 1) / (H + 1) - 1.0
    ll = (np.arange(W, dtype=np.float64) + 1.0) * (w + 1) / (W + 1) - 1.0
    coords = np.meshgrid(jj, ll, indexing="ij")
    return map_coordinates(lf2d, coords, order=1, mode="nearest")
# ── end verbatim block ───────────────────────────────────────────────────


def convention_for(dataset_name: str) -> str:
    """'node_aligned_periodic' | 'dirichlet_node' | 'legacy_cell_centred'."""
    if dataset_name in PERIODIC_NODE_DATASETS:
        return "node_aligned_periodic"
    if dataset_name in DIRICHLET_NODE_DATASETS:
        return "dirichlet_node"
    # LEGACY_CELL_DATASETS explicitly, and every unclassified dataset by
    # fallback (see module docstring for why model-side falls back).
    return "legacy_cell_centred"


def _legacy_bilinear(y: np.ndarray, dst: tuple) -> np.ndarray:
    """(N, Hs, Ws) -> (N, Hd, Wd), bit-identical to the zoo's historic path."""
    t = torch.from_numpy(np.ascontiguousarray(y, dtype=np.float32)).unsqueeze(1)
    t = F.interpolate(t, size=(int(dst[0]), int(dst[1])),
                      mode="bilinear", align_corners=False)
    return t.squeeze(1).numpy().astype(np.float32)


def resample_fields(y_flat: np.ndarray, src_grid, dst_grid,
                    dataset_name: str) -> np.ndarray:
    """(N, prod(src)) or (N, Hs, Ws) -> (N, Hd, Wd) float32 under the
    dataset's registration convention.

    The node-aligned and Dirichlet coordinate maps are direction-agnostic:
    for a nested DOWNsample they hit source nodes exactly (decimation), so
    the same dispatch serves lift-to-HF and cap-to-working-grid alike.
    Height-1 grids (1-D signals) always take the legacy path, matching
    `panel_data.copylf_prediction`'s handling of `sharp__sod_1d`.
    """
    Hs, Ws = int(src_grid[0]), int(src_grid[1])
    Hd, Wd = int(dst_grid[0]), int(dst_grid[1])
    y = np.ascontiguousarray(y_flat, dtype=np.float32).reshape(-1, Hs, Ws)
    if (Hs, Ws) == (Hd, Wd):
        return y.copy()
    conv = convention_for(dataset_name)
    if Hs == 1 or conv == "legacy_cell_centred":
        return _legacy_bilinear(y, (Hd, Wd))
    if conv == "node_aligned_periodic" and Hs % Hd == 0 and Ws % Wd == 0:
        # nested DOWNsample of node data: coarse nodes are a subset of the
        # fine ones, so exact decimation IS the node-aligned map.
        return y[:, :: Hs // Hd, :: Ws // Wd].copy()
    up = _node_aligned_periodic_up if conv == "node_aligned_periodic" else _dirichlet_node_up
    out = np.empty((y.shape[0], Hd, Wd), dtype=np.float32)
    for i in range(y.shape[0]):
        out[i] = up(y[i].astype(np.float64), (Hd, Wd))
    return out


def node_periodic_upsample_torch(x: torch.Tensor, dst_hw: tuple) -> torch.Tensor:
    """Differentiable node-aligned periodic upsample for nested grids.

    x: (..., h, w) -> (..., H, W) with H = r0*h, W = r1*w, integer r0/r1.
    Output pixel (k, l) linearly interpolates the LF nodes around index
    (k/r0, l/r1) with periodic wrap — the torch twin of
    `_node_aligned_periodic_up`, safe inside a model forward pass.
    """
    h, w = x.shape[-2], x.shape[-1]
    H, W = int(dst_hw[0]), int(dst_hw[1])
    if H % h or W % w:
        raise ValueError(f"nested grid required, got {(h, w)} -> {(H, W)}")
    r0, r1 = H // h, W // w

    # interpolate along the last axis, then the second-to-last
    def _lerp_axis(t, r, dim):
        if r == 1:
            return t
        lo = torch.repeat_interleave(t, r, dim=dim)
        hi = torch.repeat_interleave(torch.roll(t, -1, dims=dim), r, dim=dim)
        n = t.shape[dim] * r
        wgt = (torch.arange(n, dtype=t.dtype, device=t.device) % r) / r
        shape = [1] * t.dim()
        shape[dim] = n
        wgt = wgt.view(shape)
        return lo * (1 - wgt) + hi * wgt

    out = _lerp_axis(x, r1, x.dim() - 1)
    out = _lerp_axis(out, r0, x.dim() - 2)
    return out
