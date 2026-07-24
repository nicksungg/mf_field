"""ifc_raw loader for fno_coreg_residual.

Walks cat.pkl to discover the fidelity ladder. For each split (train / test /
ood) reads every fidelity_<R>/{Xs.npy, ys.npy} present and emits per-level
arrays keyed by the global level index (0..n_levels-1) plus the continuous
fidelity scalar m. The per-fidelity max-abs scaler is computed once from
the training subset so the model can predict in normalised space.

Each per-fidelity FNO trains at its native resolution — there is NO global
upsample of y to HF here. Decoded LF predictions are upsampled to the HF
grid inside the model (decoder-in-the-aggregation, MFRNP).
"""
from __future__ import annotations

import pickle
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader


def load_cat(ds_dir: Path) -> dict:
    with open(ds_dir / "cat.pkl", "rb") as f:
        return pickle.load(f)


def _read_level(ds_dir: Path, split: str, fid: int) -> Tuple[np.ndarray, np.ndarray]:
    sub = ds_dir / split / f"fidelity_{fid}"
    Xs = np.load(sub / "Xs.npy").astype(np.float32)
    ys = np.load(sub / "ys.npy").astype(np.float32)
    return Xs, ys


def load_split_levels(ds_dir: Path, split: str) -> Tuple[List[Dict], Dict]:
    """Returns (levels, cat). levels = list of dicts with keys
    level_idx, m, native_res, Xs, ys.

    level_idx is always the global fidelity-ladder index from cat['train'],
    so test/ood (which usually only carry HF) resolve to the last level.

    npz_l datasets (no cat.pkl / fidelity_* dirs, e.g. the 256² cavity) are read
    through the shared data_adapters shim so this model runs on them unchanged.
    """
    ds_dir = Path(ds_dir)
    if not (ds_dir / "cat.pkl").exists():
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # factory_mffp root
        from data_adapters.npz_compat import level_dicts
        return level_dicts(ds_dir, split)
    cat = load_cat(ds_dir)
    train_t_list = list(cat["train"]["t_list"])
    n_levels = len(train_t_list)

    if split not in cat:
        raise ValueError(f"cat.pkl has no {split!r} section (keys={list(cat.keys())})")
    info = cat[split]
    t_list = list(info["t_list"])
    fid_list = list(info["fid_list"])

    out: List[Dict] = []
    for m, fid in zip(t_list, fid_list):
        sub = ds_dir / split / f"fidelity_{fid}"
        if not (sub / "Xs.npy").exists() or not (sub / "ys.npy").exists():
            continue
        Xs, ys = _read_level(ds_dir, split, fid)
        # Global level index: prefer exact match against train t_list,
        # else fall back to the last level (HF) for test/ood.
        if m in train_t_list:
            global_idx = train_t_list.index(m)
        else:
            global_idx = n_levels - 1
        out.append({
            "level_idx": global_idx,
            "m": float(m),
            "native_res": int(fid),
            "Xs": Xs,
            "ys": ys,
        })
    return out, cat


def stratified_train_val_split(
    levels: List[Dict], val_frac: float, seed: int
) -> Tuple[List[Dict], List[Dict]]:
    """Per-level train/val split with val_frac. Keeps at least one training
    sample per level (val_frac is rounded to nearest int and clamped)."""
    rng = np.random.RandomState(seed)
    train_levels, val_levels = [], []
    for lvl in levels:
        N = lvl["Xs"].shape[0]
        n_val = int(round(N * val_frac))
        n_val = min(max(n_val, 0), max(0, N - 1))
        idx = rng.permutation(N)
        val_idx = idx[:n_val]
        tr_idx = idx[n_val:]

        def take(sel):
            return {
                "level_idx": lvl["level_idx"],
                "m": lvl["m"],
                "native_res": lvl["native_res"],
                "Xs": lvl["Xs"][sel],
                "ys": lvl["ys"][sel],
            }

        train_levels.append(take(tr_idx))
        val_levels.append(take(val_idx))
    return train_levels, val_levels


def compute_per_level_scaler(train_levels: List[Dict]) -> Dict[int, float]:
    """scaler[level_idx] = max(|y|) over training samples at that level (clamped)."""
    out: Dict[int, float] = {}
    for lvl in train_levels:
        ys = lvl["ys"]
        if ys.size == 0:
            out[lvl["level_idx"]] = 1.0
            continue
        v = float(np.abs(ys).max())
        out[lvl["level_idx"]] = max(v, 1e-8)
    return out


class PerLevelDataset(Dataset):
    """Flat dataset over samples from one fidelity level."""

    def __init__(self, lvl: Dict):
        self.Xs = torch.from_numpy(lvl["Xs"].astype(np.float32))
        self.ys = torch.from_numpy(lvl["ys"].astype(np.float32))
        self.level_idx = int(lvl["level_idx"])
        self.m = float(lvl["m"])

    def __len__(self):
        return self.Xs.shape[0]

    def __getitem__(self, i):
        return self.Xs[i], self.ys[i], self.level_idx, self.m


def build_loaders(
    ds_dir: Path, val_frac: float, seed: int, batch_size: int,
) -> Tuple[List[Tuple[Dict, DataLoader]],
           List[Tuple[Dict, DataLoader]],
           List[Dict],
           Dict[int, float],
           Dict]:
    """Builds per-level train/val loaders and a list of test_levels.

    train_loaders / val_loaders: list of (level_dict, DataLoader). The loader
    is None when the level's val slice is empty (returned for completeness).
    test_levels: raw per-level arrays for the test split.
    """
    train_levels_full, cat = load_split_levels(ds_dir, "train")
    train_levels, val_levels = stratified_train_val_split(
        train_levels_full, val_frac=val_frac, seed=seed,
    )
    scaler = compute_per_level_scaler(train_levels)

    g = torch.Generator().manual_seed(seed)

    def make_loader(lvl: Dict, shuffle: bool):
        ds = PerLevelDataset(lvl)
        if len(ds) == 0:
            return None
        return DataLoader(
            ds, batch_size=batch_size, shuffle=shuffle,
            generator=g if shuffle else None, num_workers=0,
        )

    train_loaders = [(lvl, make_loader(lvl, shuffle=True)) for lvl in train_levels]
    val_loaders = [(lvl, make_loader(lvl, shuffle=False)) for lvl in val_levels]

    test_levels, _ = load_split_levels(ds_dir, "test")
    return train_loaders, val_loaders, test_levels, scaler, cat
