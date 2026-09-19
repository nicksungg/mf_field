"""Resolve a real 2-D grid shape (H, W) for any (dataset, fidelity) pair.

The unified `data_adapters.loaders` returns fields flat as (N, n_cells) plus a
`grid_shape_by_fid` that is only populated when n_cells is a *perfect square*.
That is too restrictive for the FNO-family models, which need a concrete (H, W)
to reshape the flat field onto a grid:

  * era5 / pm_test live on **rectangular** lat/lon grids (144x192, 721x1440, …)
    whose n_cells are not perfect squares → grid_shape was None → FNO skipped.
  * allen_cahn / burgers / burgers_param are **1-D** PDEs (lengths 64/128/256).
    64 and 256 happen to be perfect squares, so the loader mislabelled them as
    8x8 / 16x16 2-D grids, while 128 (not square) was dropped entirely.

This module returns an explicit (H, W) for every field. A 1-D field of length L
is returned as (1, L): a rectangular-capable 2-D FNO run on a height-1 grid is
exactly a 1-D FNO, so the model code stays single-path. Resolution order:

  1. A known per-dataset table (exact physical grids, incl. 1-D as (1, L)).
  2. Perfect square -> (s, s).
  3. Near-square integer factorisation -> (H, W) with H <= W, H maximal.
  4. Last resort -> (1, n_cells) (treat as 1-D).

The table is keyed by dataset *name* and matched by n_cells, so it is robust to
the per-fidelity sample-count quirks of the adapter. Adding a new dataset only
requires (optionally) appending its physical grids here; unknown datasets fall
back to factorisation and still run.
"""
from __future__ import annotations

import math
from typing import Dict, List, Tuple

Grid = Tuple[int, int]

# ── known physical grids, keyed by dataset name ─────────────────────
# Values are lists of (H, W). 1-D fields are written as (1, L). The resolver
# matches an observed n_cells against H*W of these entries.

_ERA5_GRIDS: List[Grid] = [
    (144, 192),   # 27648
    (160, 320),   # 51200
    (192, 288),   # 55296
    (180, 288),   # 51840
    (120, 180),   # 21600
    (132, 156),   # 20592
    (80, 96),     # 7680
    (192, 384),   # 73728
    (721, 1440),  # 1038240
]

_1D_LENGTHS = [64, 128, 256]

KNOWN_GRIDS: Dict[str, List[Grid]] = {
    "era5": _ERA5_GRIDS,
    "pm_test": _ERA5_GRIDS,  # alias of era5
    # 1-D PDEs: length-L signals, represented as height-1 grids.
    "allen_cahn_generated": [(1, L) for L in _1D_LENGTHS],
    "burgers_generated": [(1, L) for L in _1D_LENGTHS],
    "burgers_param_generated": [(1, L) for L in _1D_LENGTHS],
}


def _perfect_square(n: int) -> Grid | None:
    s = int(round(math.sqrt(n)))
    return (s, s) if s * s == n else None


def _near_square_factor(n: int) -> Grid:
    """Return (H, W), H <= W, with H as large as possible (closest to sqrt).

    Always succeeds: worst case returns (1, n) for a prime n.
    """
    for h in range(int(math.isqrt(n)), 0, -1):
        if n % h == 0:
            return (h, n // h)
    return (1, n)


def resolve_grid(dataset_name: str | None, n_cells: int) -> Grid:
    """Return an (H, W) grid with H*W == n_cells for this dataset/fidelity.

    A 1-D field is returned as (1, L). Never raises: an unfactorable n_cells
    falls back to (1, n_cells).
    """
    n_cells = int(n_cells)
    table = KNOWN_GRIDS.get(dataset_name or "")
    if table is not None:
        for (h, w) in table:
            if h * w == n_cells:
                return (int(h), int(w))
        # dataset is known but this n_cells isn't in the table — fall through.
    sq = _perfect_square(n_cells)
    if sq is not None:
        return sq
    return _near_square_factor(n_cells)


def resolve_grids_by_fid(dataset_name: str | None,
                         n_cells_by_fid: Dict[int, int]) -> Dict[int, Grid]:
    """Map each fidelity's n_cells to a concrete (H, W) grid."""
    return {f: resolve_grid(dataset_name, n) for f, n in n_cells_by_fid.items()}


def is_1d(grid: Grid) -> bool:
    return grid[0] == 1 or grid[1] == 1


__all__ = ["resolve_grid", "resolve_grids_by_fid", "is_1d", "KNOWN_GRIDS"]


# --- auto: load extra known grids (ext/sharp benchmark datasets) ---
def _load_extra_grids():
    import json as _json, os as _os
    p = _os.path.join(_os.path.dirname(__file__), "known_grids_extra.json")
    try:
        with open(p) as _f:
            for _k, _v in _json.load(_f).items():
                KNOWN_GRIDS[_k] = [tuple(_g) for _g in _v]
    except Exception:
        pass
_load_extra_grids()
