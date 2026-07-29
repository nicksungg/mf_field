"""Panel dataset access + the copy-LF predictor.

Wraps the factory's read-only data adapter (`mf_field/factory_mffp/data_adapters/
loaders.py::load_mf_dataset`) and provides the copy-LF baseline prediction: the
highest LF fidelity field, bilinearly interpolated onto the HF grid.

Copy-LF is the round's reference model — `skill = nRMSE(model) / nRMSE(copy-LF)`
(spec §2). Assertions, not defaults: any structural surprise raises.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import numpy as np
import yaml
from scipy.ndimage import zoom


def repo_root() -> Path:
    out = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
        cwd=Path(__file__).resolve().parent,
    )
    return Path(out.stdout.strip())


def load_config() -> dict:
    cfg_path = repo_root() / "mffp_autoresearch" / "round1" / "project.yaml"
    with open(cfg_path) as f:
        return yaml.safe_load(f)


def load_split(dataset_name: str, split: str) -> dict:
    """Load `data_root/<dataset_name>` split via the factory adapter (read-only)."""
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


def copylf_prediction(data: dict) -> np.ndarray:
    """(N_hf, n_cells_hf): highest-LF-fidelity field interpolated to the HF grid.

    Raises ValueError if either grid shape is unknown (non-square layout) or the
    LF split has fewer samples than HF (index alignment is the repo convention).
    """
    hf_fid = data["hf_fid"]
    if not data["lf_fids"]:
        raise ValueError("no LF fidelities present")
    lf_fid = max(data["lf_fids"])

    lf = np.asarray(data["field_by_fid"][lf_fid], dtype=np.float64)
    hf = np.asarray(data["field_by_fid"][hf_fid], dtype=np.float64)
    lf_grid = data["grid_shape_by_fid"].get(lf_fid)
    hf_grid = data["grid_shape_by_fid"].get(hf_fid)
    if lf_grid is None or hf_grid is None:
        raise ValueError(
            f"grid shape unknown (lf_fid {lf_fid}: {lf_grid}, hf_fid {hf_fid}: {hf_grid}); "
            "copy-LF needs 2-D grids to interpolate between"
        )
    n_hf = hf.shape[0]
    if lf.shape[0] < n_hf:
        raise ValueError(
            f"LF has fewer samples than HF ({lf.shape[0]} < {n_hf}); "
            "index alignment violated"
        )
    lf = lf[:n_hf]  # index-aligned truncation (repo convention: aligned/nested)

    if tuple(lf_grid) == tuple(hf_grid):
        return lf

    factors = (hf_grid[0] / lf_grid[0], hf_grid[1] / lf_grid[1])
    out = np.empty((n_hf, hf_grid[0] * hf_grid[1]), dtype=np.float64)
    for i in range(n_hf):
        up = zoom(lf[i].reshape(lf_grid), factors, order=1, grid_mode=True, mode="nearest")
        if up.shape != tuple(hf_grid):
            raise ValueError(f"interpolation produced {up.shape}, expected {tuple(hf_grid)}")
        out[i] = up.ravel()
    return out
