"""Compatibility shim so legacy ifc_raw loaders can read npz_l datasets.

Five models still load data through their own readers that expect the old
ifc_raw layout (`cat.pkl` + `train/fidelity_<R>/{Xs,ys}.npy`):
fno_mf_stack, fno_coreg_residual (Family A, per-level dicts) and
transolver_residual, transolver_attention_fusion, v9_baseline (Family B,
`IFCRawMultiStreamDataset`). The other 12 models already read npz via
`data_adapters.load_mf_dataset`.

This module lets those five read the newer npz_l datasets (e.g. the
regenerated 256² lid-driven cavity) with NO on-disk conversion and without
touching the dataset directory (which would flip `detect_layout` for the
npz models). Each legacy loader falls back here when no fidelity_* dirs exist.

Fidelity key = native resolution (32/64/128/256), so the HF level is the
highest resolution exactly as in the ifc convention (`hf_fid = max(fids)`).
Fields are returned as 2-D (N, H, W) to match the on-disk ys.npy shape.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

from . import load_mf_dataset
from .geometry import resolve_grid


def has_npz_layout(dataset_dir, split: str = "train") -> bool:
    """True when `dataset_dir` has no fidelity_* dirs but does have npz levels."""
    dataset_dir = Path(dataset_dir)
    sd = dataset_dir / split
    if sd.is_dir() and any(
        p.is_dir() and p.name.startswith("fidelity_") for p in sd.iterdir()
    ):
        return False
    return len(list(dataset_dir.glob("*_l*.npz"))) > 0


def per_fidelity(dataset_dir, split: str):
    """Return (res_sorted, x_by_res, y_by_res) read from npz via data_adapters.

    res_sorted : ascending list of native resolutions (ints), HF last.
    x_by_res   : {res -> (N, cond_dim) float32}
    y_by_res   : {res -> (N, H, W)    float32}
    """
    dataset_dir = Path(dataset_dir)
    d = load_mf_dataset(str(dataset_dir), split=split)
    name = dataset_dir.name
    x_by_res: dict[int, np.ndarray] = {}
    y_by_res: dict[int, np.ndarray] = {}
    for f in d["fids"]:
        n = d["n_cells_by_fid"][f]
        grid = (d.get("grid_shape_by_fid") or {}).get(f) or resolve_grid(name, n)
        H, W = int(grid[0]), int(grid[1])
        r = max(H, W)
        x_by_res[r] = np.asarray(d["cond_by_fid"][f], dtype=np.float32)
        y_by_res[r] = np.asarray(d["field_by_fid"][f], dtype=np.float32).reshape(-1, H, W)
    res_sorted = sorted(x_by_res)
    return res_sorted, x_by_res, y_by_res


def _synth_cat(res_sorted, x_by_res):
    """Build a cat.pkl-equivalent dict from the per-resolution arrays."""
    n = len(res_sorted)
    t_list = [i / (n - 1) if n > 1 else 1.0 for i in range(n)]
    fid_list = list(res_sorted)
    ns_list = [int(x_by_res[r].shape[0]) for r in res_sorted]
    return {
        "fid_min": fid_list[0],
        "fid_max": fid_list[-1],
        "t_min": 0.0,
        "t_max": 1.0,
        "train": {"t_list": t_list, "fid_list": fid_list, "ns_list": ns_list},
        "test": {"t_list": [1.0], "fid_list": [fid_list[-1]], "ns_list": [ns_list[-1]]},
    }


def level_dicts(dataset_dir, split: str):
    """Family-A fallback: (levels, cat) matching ifc_raw load_split_levels().

    Each level dict has keys: level_idx (global, HF last), m (continuous in
    [0,1]), native_res, Xs (N,cond), ys (N,H,W). For test only the HF level is
    returned, matching the ifc convention (test carries HF only).
    """
    res_sorted, x_by_res, y_by_res = per_fidelity(dataset_dir, "train" if split == "test" else split)
    cat = _synth_cat(res_sorted, x_by_res)
    n = len(res_sorted)

    if split == "test":
        # HF target only; condition x + HF field come from the test split.
        d = load_mf_dataset(str(Path(dataset_dir)), split="test")
        name = Path(dataset_dir).name
        hf = d["hf_fid"]
        ncell = d["n_cells_by_fid"][hf]
        grid = (d.get("grid_shape_by_fid") or {}).get(hf) or resolve_grid(name, ncell)
        H, W = int(grid[0]), int(grid[1])
        Xs = np.asarray(d["cond_by_fid"][hf], dtype=np.float32)
        ys = np.asarray(d["field_by_fid"][hf], dtype=np.float32).reshape(-1, H, W)
        return [{
            "level_idx": n - 1, "m": 1.0, "native_res": int(max(H, W)),
            "Xs": Xs, "ys": ys,
        }], cat

    out = []
    for level_idx, r in enumerate(res_sorted):
        out.append({
            "level_idx": level_idx,
            "m": float(cat["train"]["t_list"][level_idx]),
            "native_res": int(r),
            "Xs": x_by_res[r],
            "ys": y_by_res[r],
        })
    return out, cat
