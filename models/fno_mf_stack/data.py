"""ifc_raw loader for fno_mf_stack.

Reads cat.pkl to discover the fidelity ladder (4 levels) and loads
per-fidelity (Xs.npy, ys.npy) tensors. Outputs (X, y, m, level_idx) tuples
where level_idx routes a sample through the FNO trained on its fidelity.
Computes per-fidelity max-abs `scaler[m]` from training data so the model can
predict in normalized space and de-normalize at inference.
"""
from __future__ import annotations

import pickle
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import Dataset


def load_cat(ds_dir: Path) -> dict:
    with open(ds_dir / "cat.pkl", "rb") as f:
        return pickle.load(f)


def load_split(ds_dir: Path, split: str):
    """Return list of (level_idx, m_value, native_res, Xs, ys) tuples.

    For training: walks every fidelity_<R>/ directory under train/.
    For test: only the highest-fidelity directory is present (test/fidelity_64).
    """
    cat = load_cat(ds_dir)
    if split == "train":
        t_list = cat["train"]["t_list"]
        fid_list = cat["train"]["fid_list"]
    else:
        t_list = cat[split]["t_list"]
        fid_list = cat[split]["fid_list"]

    out = []
    n_levels = len(cat["train"]["fid_list"])
    for level_idx, (m, fid) in enumerate(zip(t_list, fid_list)):
        sub = ds_dir / split / f"fidelity_{fid}"
        Xs = np.load(sub / "Xs.npy").astype(np.float32)
        ys = np.load(sub / "ys.npy").astype(np.float32)
        # level_idx in test refers to the global level index (e.g. m=1.0 → last level)
        global_idx = cat["train"]["t_list"].index(m) if m in cat["train"]["t_list"] else n_levels - 1
        out.append({
            "level_idx": global_idx,
            "m": float(m),
            "native_res": int(fid),
            "Xs": Xs,
            "ys": ys,
        })
    return out, cat


class IFCRawPerLevelDataset(Dataset):
    """A flat dataset over samples from a single fidelity level."""

    def __init__(self, Xs: np.ndarray, ys: np.ndarray, level_idx: int, m: float):
        assert Xs.shape[0] == ys.shape[0]
        self.Xs = torch.from_numpy(Xs.astype(np.float32))
        self.ys = torch.from_numpy(ys.astype(np.float32))
        self.level_idx = level_idx
        self.m = float(m)

    def __len__(self):
        return self.Xs.shape[0]

    def __getitem__(self, i):
        return self.Xs[i], self.ys[i], self.level_idx, self.m


def stratified_train_val_split(level_arrays, val_frac: float, seed: int):
    """For each level, split (Xs, ys) into (train, val) by val_frac.

    val_frac is rounded to nearest int per level; min 0 (if level has <2 samples).
    Returns parallel structures: train_levels, val_levels (each a list-of-dict
    with keys level_idx, m, native_res, Xs, ys).
    """
    rng = np.random.RandomState(seed)
    train_levels, val_levels = [], []
    for lvl in level_arrays:
        N = lvl["Xs"].shape[0]
        n_val = int(round(N * val_frac))
        n_val = min(max(n_val, 0), max(0, N - 1))
        idx = rng.permutation(N)
        val_idx = idx[:n_val]
        tr_idx = idx[n_val:]

        def slice_lvl(sel):
            return {
                "level_idx": lvl["level_idx"],
                "m": lvl["m"],
                "native_res": lvl["native_res"],
                "Xs": lvl["Xs"][sel],
                "ys": lvl["ys"][sel],
            }

        train_levels.append(slice_lvl(tr_idx))
        val_levels.append(slice_lvl(val_idx))
    return train_levels, val_levels


def compute_per_level_scaler(train_levels) -> dict:
    """scaler[level_idx] = max(|y|) over training samples at that level (clamped)."""
    s = {}
    for lvl in train_levels:
        ys = lvl["ys"]
        if ys.size == 0:
            s[lvl["level_idx"]] = 1.0
            continue
        v = float(np.abs(ys).max())
        s[lvl["level_idx"]] = max(v, 1e-8)
    return s


def build_loaders(ds_dir: Path, val_frac: float, seed: int, batch_size: int):
    """Returns (train_loaders_per_level, val_loaders_per_level, test_levels, scaler, cat).

    Each per-level loader yields (Xs_batch, ys_batch).
    """
    train_levels_full, cat = load_split(ds_dir, "train")
    train_levels, val_levels = stratified_train_val_split(train_levels_full, val_frac, seed)
    scaler = compute_per_level_scaler(train_levels)

    g = torch.Generator().manual_seed(seed)

    def make_loader(lvl, shuffle):
        ds = IFCRawPerLevelDataset(lvl["Xs"], lvl["ys"], lvl["level_idx"], lvl["m"])
        if len(ds) == 0:
            return None
        return torch.utils.data.DataLoader(
            ds, batch_size=batch_size, shuffle=shuffle,
            generator=g if shuffle else None, num_workers=0,
        )

    train_loaders = [(lvl, make_loader(lvl, shuffle=True)) for lvl in train_levels]
    val_loaders = [(lvl, make_loader(lvl, shuffle=False)) for lvl in val_levels]

    test_levels, _ = load_split(ds_dir, "test")
    return train_loaders, val_loaders, test_levels, scaler, cat
