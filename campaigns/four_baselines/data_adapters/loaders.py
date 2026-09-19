"""Unified loaders for ifc_raw and npz_l* dataset layouts.

Two layouts in `data/<name>/`:

A) ifc_raw  (4 datasets: ifc_heat, ifc_poisson, chin_chun_isothermal, chin_chun_potential)
   ├── train/fidelity_<F>/Xs.npy   shape (N, cond_dim)
   ├── train/fidelity_<F>/ys.npy   shape (N, H, W)
   └── test/fidelity_<HF>/{Xs.npy, ys.npy}

B) npz_l*  (13 datasets: fluid, poisson_local, heat_local, era5, pm_test,
            advection_diffusion_generated, allen_cahn_generated,
            burgers_generated, burgers_param_generated, darcy_generated,
            heat_generated, lid_driven_cavity_generated, poisson_generated)
   ├── [<subdir>/]train_l<i>.npz   keys: x (N, cond_dim), y (N, n_cells_i)
   ├── [<subdir>/]test_l<i>.npz    same keys
   └── ood/test_l<i>.npz           optional, same keys

Fields in (A) are 2-D (H, W); fields in (B) are flat (n_cells,). This adapter
returns fields as flat (n_cells,) regardless, plus a `grid_shape_by_fid`
metadata dict giving the (H, W) reshape for the families that want it.
"""
from __future__ import annotations

import math
import re
from pathlib import Path
from typing import Literal

import numpy as np
import torch
from torch.utils.data import Dataset

Layout = Literal["ifc_raw", "npz_l", "chin_chun"]
Split = Literal["train", "test", "ood"]

_NPZ_FILE_RE = re.compile(r"^(train|test)_l(\d+)\.npz$")
_CHIN_CHUN_DIR_RE = re.compile(r"^full_(\d+)x\1_\w+_label$")


# ── layout detection ────────────────────────────────────────────────


def _find_npz_root(dataset_dir: Path) -> Path | None:
    """Return the directory that contains the train_l*.npz / test_l*.npz files.

    Some datasets put the npz files directly under dataset_dir; era5 puts them
    in `era5_train_test/`, pm_test puts them in `data/`. We scan one level deep.
    """
    if any(_NPZ_FILE_RE.match(p.name) for p in dataset_dir.iterdir() if p.is_file()):
        return dataset_dir
    for sub in dataset_dir.iterdir():
        if sub.is_dir() and any(_NPZ_FILE_RE.match(p.name) for p in sub.iterdir() if p.is_file()):
            return sub
    return None


def _find_chin_chun_root(dataset_dir: Path) -> Path | None:
    """Return the directory that contains chin_chun's full_<N>x<N>_*_label subdirs.

    After untarring chin_chun_{isothermal,potential}/*.tar.gz, the layout is:
        extracted/full_128x128_<name>_label/
        extracted/full_256x256_<name>_label/
    """
    for root in (dataset_dir, dataset_dir / "extracted"):
        if not root.is_dir():
            continue
        if any(_CHIN_CHUN_DIR_RE.match(p.name) for p in root.iterdir() if p.is_dir()):
            return root
    return None


def detect_layout(dataset_dir: Path) -> Layout:
    """Return 'ifc_raw' | 'npz_l' | 'chin_chun' based on dataset structure."""
    dataset_dir = Path(dataset_dir)
    if (dataset_dir / "train").is_dir() and any(
        p.is_dir() and p.name.startswith("fidelity_")
        for p in (dataset_dir / "train").iterdir()
    ):
        return "ifc_raw"
    if _find_chin_chun_root(dataset_dir) is not None:
        return "chin_chun"
    if _find_npz_root(dataset_dir) is not None:
        return "npz_l"
    raise FileNotFoundError(f"unknown dataset layout under {dataset_dir}")


# ── format A: ifc_raw ───────────────────────────────────────────────


def _load_ifc_raw(dataset_dir: Path, split: Split) -> dict:
    split_dir = dataset_dir / split
    if not split_dir.is_dir():
        raise FileNotFoundError(f"split '{split}' not found at {split_dir}")
    fid_dirs = sorted(
        (p for p in split_dir.iterdir() if p.is_dir() and p.name.startswith("fidelity_")),
        key=lambda p: int(p.name.split("_")[1]),
    )
    if not fid_dirs:
        raise ValueError(f"no fidelity_* dirs under {split_dir}")

    fids: list[int] = []
    cond_by_fid: dict[int, np.ndarray] = {}
    field_by_fid: dict[int, np.ndarray] = {}
    grid_shape_by_fid: dict[int, tuple[int, int] | None] = {}

    for p in fid_dirs:
        f = int(p.name.split("_")[1])
        xs = np.load(p / "Xs.npy").astype(np.float32)
        ys = np.load(p / "ys.npy").astype(np.float32)
        if ys.ndim >= 3:
            # (N, H, W[, C]) → flatten the spatial dims, keep N first
            grid = tuple(ys.shape[1:])
            ys_flat = ys.reshape(ys.shape[0], -1)
            grid_shape_by_fid[f] = grid if len(grid) == 2 else None
        else:
            ys_flat = ys
            grid_shape_by_fid[f] = _infer_square_grid(ys.shape[-1])
        fids.append(f)
        cond_by_fid[f] = xs
        field_by_fid[f] = ys_flat

    hf_fid = max(fids)
    lf_fids = [f for f in fids if f != hf_fid]
    return {
        "fids": sorted(fids),
        "hf_fid": hf_fid,
        "lf_fids": lf_fids,
        "cond_by_fid": cond_by_fid,
        "field_by_fid": field_by_fid,
        "n_cells_by_fid": {f: field_by_fid[f].shape[1] for f in fids},
        "grid_shape_by_fid": grid_shape_by_fid,
        "cond_dim": int(cond_by_fid[hf_fid].shape[1]),
        "n_samples": int(cond_by_fid[hf_fid].shape[0]),
        "loader": "ifc_raw",
        "has_ood": (dataset_dir / "ood").is_dir(),
    }


# ── format B: npz_l* ────────────────────────────────────────────────


def _load_npz_l(dataset_dir: Path, split: Split) -> dict:
    npz_root = _find_npz_root(dataset_dir)
    if npz_root is None:
        raise FileNotFoundError(f"no train_l*.npz / test_l*.npz under {dataset_dir}")

    # for 'ood' split, look at <dataset>/ood/test_l*.npz
    if split == "ood":
        ood_dir = dataset_dir / "ood"
        if not ood_dir.is_dir():
            raise FileNotFoundError(f"no ood/ split under {dataset_dir}")
        pattern_split = "test"  # ood/ contains test_l*.npz
        scan_dir = ood_dir
    else:
        pattern_split = split
        scan_dir = npz_root

    files: list[tuple[int, Path]] = []
    for p in scan_dir.iterdir():
        if not p.is_file():
            continue
        m = _NPZ_FILE_RE.match(p.name)
        if m and m.group(1) == pattern_split:
            files.append((int(m.group(2)), p))
    if not files:
        raise FileNotFoundError(
            f"no {pattern_split}_l*.npz under {scan_dir}"
        )
    files.sort()

    fids: list[int] = []
    cond_by_fid: dict[int, np.ndarray] = {}
    field_by_fid: dict[int, np.ndarray] = {}
    grid_shape_by_fid: dict[int, tuple[int, int] | None] = {}

    for f, path in files:
        d = np.load(path)
        x = d["x"].astype(np.float32)
        y = d["y"].astype(np.float32)
        if y.ndim != 2:
            # (N, ...) -> flatten spatial dims for uniformity
            y = y.reshape(y.shape[0], -1)
        fids.append(f)
        cond_by_fid[f] = x
        field_by_fid[f] = y
        grid_shape_by_fid[f] = _infer_square_grid(y.shape[-1])

    # Sample counts can differ across fidelities (e.g., era5 train_l1=1222 vs train_l9=65).
    # Choose HF reference as max(fid). Caller should be aware sample alignment is per-fid.
    hf_fid = max(fids)
    lf_fids = [f for f in fids if f != hf_fid]
    return {
        "fids": sorted(fids),
        "hf_fid": hf_fid,
        "lf_fids": lf_fids,
        "cond_by_fid": cond_by_fid,
        "field_by_fid": field_by_fid,
        "n_cells_by_fid": {f: field_by_fid[f].shape[1] for f in fids},
        "grid_shape_by_fid": grid_shape_by_fid,
        "cond_dim": int(cond_by_fid[hf_fid].shape[1]),
        "n_samples": int(cond_by_fid[hf_fid].shape[0]),
        "loader": "npz_l",
        "has_ood": (dataset_dir / "ood").is_dir(),
    }


def _infer_square_grid(n_cells: int) -> tuple[int, int] | None:
    s = int(round(math.sqrt(n_cells)))
    return (s, s) if s * s == n_cells else None


# ── format C: chin_chun (extracted tarball) ─────────────────────────
#
# After running `tar -xzf wind_2d_<name>_small\ \(1\).tar.gz -C extracted/`,
# the layout is:
#   extracted/full_<N>x<N>_<dataset_label>/
#     urban_<...>_{train,valid,test}.npz       (chans named u,v,w or u,v,z)
#     urban_input_<...>_{train,valid,test}.npz (may be absent at L1 for potential)
#
# Each npz uses np.savez default key 'arr_0' and contains a (N, H, W, C) float64
# array. We stack output channels along the last axis and flatten the spatial
# dims so the canonical field is (N, H*W*C). cond comes from the input file;
# if absent at a level (chin_chun_potential L1), we fall back to the L2 input
# downsampled-by-stride to L1 resolution.


def _split_to_npz_token(split: Split) -> str:
    return {"train": "train", "test": "test", "ood": "test"}[split]


def _load_chinchun_arr(p: Path) -> np.ndarray:
    """np.savez files use 'arr_0'; others use named keys. Be permissive."""
    d = np.load(p)
    if "arr_0" in d.files:
        return d["arr_0"].astype(np.float32)
    # fallback: first key
    return d[d.files[0]].astype(np.float32)


def _load_chin_chun(dataset_dir: Path, split: Split) -> dict:
    if split == "ood":
        raise FileNotFoundError(f"chin_chun has no ood/ split (only train/valid/test)")
    root = _find_chin_chun_root(dataset_dir)
    if root is None:
        raise FileNotFoundError(f"no extracted/ subdir under {dataset_dir}; run `tar -xzf <tarball>`")
    split_tok = _split_to_npz_token(split)

    # Find fidelity dirs by parsing the resolution from full_<N>x<N>_*_label.
    fid_dirs: list[tuple[int, Path]] = []
    for p in sorted(root.iterdir()):
        if not p.is_dir():
            continue
        m = _CHIN_CHUN_DIR_RE.match(p.name)
        if m:
            fid_dirs.append((int(m.group(1)), p))
    fid_dirs.sort()
    if len(fid_dirs) < 2:
        raise ValueError(f"chin_chun needs >=2 fidelity subdirs under {root}, found {len(fid_dirs)}")

    cond_by_fid: dict[int, np.ndarray] = {}
    field_by_fid: dict[int, np.ndarray] = {}
    grid_shape_by_fid: dict[int, tuple[int, int] | None] = {}
    fids = [f for f, _ in fid_dirs]
    hf_fid = max(fids)

    # First pass: load each fidelity's output channels + input (if present)
    raw: dict[int, dict] = {}
    for fid, fdir in fid_dirs:
        files = sorted(fdir.iterdir())
        chan_files: dict[str, Path] = {}
        input_file: Path | None = None
        for f in files:
            if not f.is_file() or not f.name.endswith(".npz"):
                continue
            if not f.name.endswith(f"_{split_tok}.npz"):
                continue
            stem = f.name[: -len(f"_{split_tok}.npz")]
            if "input" in stem:
                input_file = f
                continue
            # Output channels: filename ends with _<chan> just before the split token.
            chan = stem.split("_")[-1]
            if chan in ("u", "v", "w", "z", "p"):
                chan_files[chan] = f
        if not chan_files:
            raise ValueError(f"no output channels found in {fdir} for split={split}")
        # Stack output channels in a stable order
        chan_order = sorted(chan_files.keys())
        ys = np.stack([_load_chinchun_arr(chan_files[c])[..., 0] for c in chan_order], axis=-1)
        # ys shape: (N, H, W, C)
        x = _load_chinchun_arr(input_file)[..., 0] if input_file is not None else None
        raw[fid] = {"x": x, "y": ys, "chans": chan_order, "grid": (ys.shape[1], ys.shape[2])}

    # Determine N_samples (use HF; assume all fids share N since the tarball
    # supplies aligned samples by index).
    n_hf = int(raw[hf_fid]["y"].shape[0])

    # If a fidelity has no input file, fall back to spatial-downsampled HF input.
    hf_x = raw[hf_fid]["x"]
    if hf_x is None:
        raise ValueError(f"chin_chun expects an input file at HF (fid={hf_fid}) but none was found")

    for fid in fids:
        x = raw[fid]["x"]
        y = raw[fid]["y"]  # (N, H, W, C)
        H, W, C = y.shape[1], y.shape[2], y.shape[3]
        # Cond: if missing, downsample HF input by stride to current resolution.
        # hf_x has been pre-squeezed to (N, H_hf, W_hf) — same will apply to x.
        if x is None:
            hf_H = hf_x.shape[1]
            stride = max(1, hf_H // H)
            x = hf_x[:, ::stride, ::stride][:, :H, :W]  # (N, H, W)
        # Flatten cond per-sample to a vector: take mean over spatial dims as a
        # simple, dimension-stable summary. (Most factory_mffp families consume
        # cond as a small fixed-dim vector; per-pixel input is not the contract.)
        cond_vec = x.reshape(x.shape[0], -1).mean(axis=1, keepdims=True).astype(np.float32)
        # Field: flatten H*W*C to a single per-sample vector
        field_vec = y.reshape(y.shape[0], -1).astype(np.float32)
        cond_by_fid[fid] = cond_vec
        field_by_fid[fid] = field_vec
        grid_shape_by_fid[fid] = (H, W) if C == 1 else None  # multi-channel: no clean 2-D shape

    lf_fids = [f for f in fids if f != hf_fid]
    return {
        "fids": sorted(fids),
        "hf_fid": hf_fid,
        "lf_fids": lf_fids,
        "cond_by_fid": cond_by_fid,
        "field_by_fid": field_by_fid,
        "n_cells_by_fid": {f: field_by_fid[f].shape[1] for f in fids},
        "grid_shape_by_fid": grid_shape_by_fid,
        "cond_dim": int(cond_by_fid[hf_fid].shape[1]),
        "n_samples": int(cond_by_fid[hf_fid].shape[0]),
        "loader": "chin_chun",
        "has_ood": False,
    }


# ── unified entrypoint ──────────────────────────────────────────────


def load_mf_dataset(dataset_dir: str | Path, split: Split = "train") -> dict:
    """Load any factory_mffp dataset in canonical multi-fidelity form.

    Args:
        dataset_dir: path to data/<name>/
        split: one of {"train", "test", "ood"}

    Returns a dict with keys:
        fids, hf_fid, lf_fids, cond_by_fid, field_by_fid,
        n_cells_by_fid, grid_shape_by_fid, cond_dim, n_samples, loader, has_ood.

    field_by_fid is always flat: shape (N_at_this_fid, n_cells_at_this_fid).
    grid_shape_by_fid[f] is (H, W) when the field has a square grid layout,
    else None — families that want 2-D inputs should reshape themselves.

    For npz_l* datasets, N_at_each_fid CAN differ (e.g., era5 has 1222 train
    samples at l1 but only 65 at l9). For ifc_raw, all fidelities are aligned
    by sample index. `n_samples` reports the HF count.
    """
    dataset_dir = Path(dataset_dir)
    layout = detect_layout(dataset_dir)
    if layout == "ifc_raw":
        return _load_ifc_raw(dataset_dir, split)
    if layout == "chin_chun":
        return _load_chin_chun(dataset_dir, split)
    return _load_npz_l(dataset_dir, split)


# ── torch Dataset wrapper ───────────────────────────────────────────


class MFDataset(Dataset):
    """torch.utils.data.Dataset wrapper around load_mf_dataset.

    __getitem__ returns:
        {
            "cond": (cond_dim,) np.float32,
            "lf_fields": [(n_cells_lf_i,) np.float32, ...] in ascending fid order,
            "hf_field": (n_cells_hf,) np.float32,
            "sample_id": str,
        }

    Sample alignment:
        - ifc_raw: all fidelities use the same idx → trivially aligned.
        - npz_l* with mismatched per-fid sample counts: __len__ uses HF count,
          LF fields are indexed modulo their length. (This matches the
          standard "more LF than HF" MF training pattern.) For era5 where HF
          is tiny, callers may want to do their own alignment instead.
    """

    def __init__(self, dataset_dir: str | Path, split: Split = "train"):
        self.dataset_dir = Path(dataset_dir)
        self.split = split
        self.data = load_mf_dataset(self.dataset_dir, split)
        # Use HF cond as canonical x for sample id / __len__
        self._n_hf = int(self.data["cond_by_fid"][self.data["hf_fid"]].shape[0])
        self.cond_dim = self.data["cond_dim"]
        self.hf_fid = self.data["hf_fid"]
        self.lf_fids = self.data["lf_fids"]
        self.fids = self.data["fids"]
        self.grid_shape_by_fid = self.data["grid_shape_by_fid"]
        self.n_cells_by_fid = self.data["n_cells_by_fid"]
        self.sample_ids = [
            f"{self.dataset_dir.name}_{split}_{i:04d}" for i in range(self._n_hf)
        ]

    def __len__(self) -> int:
        return self._n_hf

    def __getitem__(self, idx: int) -> dict:
        cond = self.data["cond_by_fid"][self.hf_fid][idx]
        hf_field = self.data["field_by_fid"][self.hf_fid][idx]
        lf_fields = []
        for f in self.lf_fids:
            arr = self.data["field_by_fid"][f]
            lf_fields.append(arr[idx % arr.shape[0]])
        return {
            "cond": cond,
            "lf_fields": lf_fields,
            "hf_field": hf_field,
            "sample_id": self.sample_ids[idx],
        }
