"""Panel dataset access + the CORRECTED copy-LF reference (round 2).

Round 1 established (s3-B1, report §5) that the round-1 copy-LF construction
`scipy.ndimage.zoom(..., order=1, grid_mode=True, mode="nearest")` misreads
node-sampled fields under a cell-centred convention — a fixed (r-1)/2 HF-cell
misregistration — and clamp-extends across periodic seams. Skill denominators
were inflated 2.0-8.6x on the sharp panel. Round 2 references are computed
under the per-dataset conventions of ADR r2-0001:

  - nested periodic pseudo-spectral datasets -> variant C: node-aligned
    bilinear with periodic wrap (HF pixel k samples LF index k/r exactly;
    LF node j coincides with HF node r*j).
  - ext__helmholtz_2d (Dirichlet interior-node grid x_j=(j+1)/(n+1), r=4,
    non-nested) -> variant E: interior-node coordinate map, clamped edges.
  - everything else (non-nested guards, 1-D signals) -> the round-1 legacy
    cell-centred path, which the registration audit certified as consistent
    for those datasets (fixing them makes their references WORSE).

Copy-LF remains the round's offline reference — `skill = nRMSE(model) /
nRMSE(copy-LF)` — computed once from stored test LF fields that round-2
models never see (stripped test view, spec §5). Assertions, not defaults.

`COPYLF_DEF_HASH` is the sha256 of this file; the baselines JSON and the
score cache carry it so references computed under different constructions can
never be silently compared (round-1 gap: NRMSE_DEF_HASH covered nrmse.py only).
"""
from __future__ import annotations

import hashlib
import pathlib
import subprocess
import sys
from pathlib import Path

import numpy as np
import yaml
from scipy.ndimage import map_coordinates, zoom

# ADR r2-0001: reference convention per dataset. A panel/guard dataset MUST be
# classified here or in LEGACY_CELL_DATASETS — an unknown 2-D dataset raises.
PERIODIC_NODE_DATASETS = {
    "sharp__phase_field_crystal_2d",
    "sharp__allen_cahn_2d",
    "sharp__fisher_kpp_2d",
    "sharp__cahn_hilliard",
}
DIRICHLET_NODE_DATASETS = {"ext__helmholtz_2d"}
LEGACY_CELL_DATASETS = {"heat_local", "fluid", "sharp__sod_1d", "ifc_poisson", "ifc_heat"}


def repo_root() -> Path:
    out = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
        cwd=Path(__file__).resolve().parent,
    )
    return Path(out.stdout.strip())


def load_config() -> dict:
    cfg_path = repo_root() / "mffp_autoresearch" / "round2" / "project.yaml"
    with open(cfg_path) as f:
        return yaml.safe_load(f)


def load_split(dataset_name: str, split: str) -> dict:
    """Load `data_root/<dataset_name>` split via the factory adapter (read-only).

    NOTE: this reads the ORIGINAL dataset (with test LF present) and exists for
    the offline reference/floor computations only. Models are evaluated against
    `stripped_data_root` (score_panel.py) and can never reach this path.
    """
    root = repo_root()
    cfg = load_config()
    factory_root = root / cfg["paths"]["factory_root"]
    dataset_dir = root / cfg["paths"]["data_root"] / dataset_name
    if not dataset_dir.exists():
        raise ValueError(f"dataset dir not found: {dataset_dir}")
    if str(factory_root) not in sys.path:
        sys.path.insert(0, str(factory_root))
    from data_adapters.loaders import load_mf_dataset  # noqa: import after path insert

    return load_mf_dataset(dataset_dir, split)


def _legacy_cell_centred_up(lf2d: np.ndarray, hf_grid: tuple) -> np.ndarray:
    """Round-1 convention: cell-centred bilinear zoom, clamp-extended edges."""
    factors = (hf_grid[0] / lf2d.shape[0], hf_grid[1] / lf2d.shape[1])
    return zoom(lf2d, factors, order=1, grid_mode=True, mode="nearest")


def _node_aligned_periodic_up(lf2d: np.ndarray, hf_grid: tuple) -> np.ndarray:
    """Variant C: HF pixel (k,l) samples LF index (k/r0, l/r1), periodic wrap.

    Exact at shared nodes: up[::r0, ::r1] == lf bit-for-bit when nested.
    """
    h, w = lf2d.shape
    H, W = hf_grid
    if H % h or W % w:
        raise ValueError(f"variant C requires a nested grid, got {h,w} -> {H,W}")
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


def copylf_prediction(data: dict, dataset_name: str = None) -> np.ndarray:
    """(N_hf, n_cells_hf): highest-LF-fidelity field resampled to the HF grid
    under the dataset's certified grid convention (ADR r2-0001).

    `dataset_name` selects the convention; None (synthetic/test data) uses the
    legacy path. A named 2-D dataset not classified in this module raises —
    convention assignment is an ADR decision, not a default.
    """
    hf_fid = data["hf_fid"]
    if not data["lf_fids"]:
        raise ValueError("no LF fidelities present")
    lf_fid = max(data["lf_fids"])

    lf = np.asarray(data["field_by_fid"][lf_fid], dtype=np.float64)
    hf = np.asarray(data["field_by_fid"][hf_fid], dtype=np.float64)
    lf_grid = data["grid_shape_by_fid"].get(lf_fid)
    hf_grid = data["grid_shape_by_fid"].get(hf_fid)
    n_hf = hf.shape[0]
    if lf.shape[0] < n_hf:
        raise ValueError(
            f"LF has fewer samples than HF ({lf.shape[0]} < {n_hf}); "
            "index alignment violated"
        )
    lf = lf[:n_hf]  # index-aligned truncation (repo convention: aligned/nested)

    if lf_grid is None or hf_grid is None:
        # 1-D signals (e.g. sod_1d): legacy path, certified clean by the audit.
        if lf.shape[1] == hf.shape[1]:
            return lf
        factor = hf.shape[1] / lf.shape[1]
        out = np.empty((n_hf, hf.shape[1]), dtype=np.float64)
        for i in range(n_hf):
            up = zoom(lf[i], factor, order=1, grid_mode=True, mode="nearest")
            if up.shape != (hf.shape[1],):
                raise ValueError(f"1-D interpolation produced {up.shape}, expected {(hf.shape[1],)}")
            out[i] = up
        return out

    if tuple(lf_grid) == tuple(hf_grid):
        return lf

    if dataset_name in PERIODIC_NODE_DATASETS:
        up_fn = _node_aligned_periodic_up
    elif dataset_name in DIRICHLET_NODE_DATASETS:
        up_fn = _dirichlet_node_up
    elif dataset_name is None or dataset_name in LEGACY_CELL_DATASETS:
        up_fn = _legacy_cell_centred_up
    else:
        raise ValueError(
            f"dataset {dataset_name!r} has no reference convention assigned "
            "(ADR r2-0001): classify it in panel_data.py before computing references"
        )

    out = np.empty((n_hf, hf_grid[0] * hf_grid[1]), dtype=np.float64)
    for i in range(n_hf):
        up = up_fn(lf[i].reshape(lf_grid), tuple(hf_grid))
        if up.shape != tuple(hf_grid):
            raise ValueError(f"interpolation produced {up.shape}, expected {tuple(hf_grid)}")
        out[i] = up.ravel()
    return out


COPYLF_DEF_HASH = hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
