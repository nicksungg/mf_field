"""
ifc_raw loader for fno_coregionalization.

Reads `cat.pkl` for the fidelity ladder (`t_list`, `fid_list`, `ns_list`),
loads each `<split>/fidelity_<F>/{Xs.npy, ys.npy}`, and yields
`(X_vec, y_grid, m_scalar)` triples for training. Lower-fidelity `y` fields
are bilinearly upsampled to a fixed target size (default 64x64, the HF
resolution on the IFC datasets) so the FNO sees a single output resolution
and we can compute the loss against a model output that is itself 64x64.

Per-fidelity scalers (max(|y|) at fidelity m) are computed from the
raw per-fidelity arrays so the scaler is unaffected by upsampling, and
the helper accepts an `indices` mask so the scaler can be restricted to
the post-random_split training subset.
"""
from __future__ import annotations

import pickle
from pathlib import Path
from typing import Iterable

import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import Dataset


def _bilinear_upsample(y: np.ndarray, target: int) -> np.ndarray:
    if y.shape[0] == target and y.shape[1] == target:
        return y.astype(np.float32, copy=False)
    t = torch.from_numpy(y).float().unsqueeze(0).unsqueeze(0)
    up = F.interpolate(t, size=(target, target), mode="bilinear", align_corners=False)
    return up.squeeze(0).squeeze(0).numpy()


class IFCMultiFidelityDataset(Dataset):
    """Flattens samples across every fidelity present in the split.

    Each item: `(X, y_upsampled, m)` — X is the parameter vector (cond_dim,),
    y is the upsampled solution field (target_size, target_size), m is the
    continuous fidelity index in [0, 1] from cat.pkl.

    `self.raw_y_by_m[m]` keeps the raw (non-upsampled) y arrays per fidelity
    for downstream scaler computation. `self.fid_id_by_record[i]` is the
    integer fidelity-index id for sample i (used to mask raw arrays when
    a random_split subset is requested).
    """

    def __init__(self, dataset_dir: Path, split: str, target_size: int = 64):
        self.dataset_dir = Path(dataset_dir)
        self.split = split
        self.target_size = target_size

        with open(self.dataset_dir / "cat.pkl", "rb") as f:
            cat = pickle.load(f)
        if split not in cat:
            raise ValueError(f"cat.pkl has no {split!r} section (keys={list(cat.keys())})")
        info = cat[split]
        self.t_list = list(info["t_list"])
        self.fid_list = list(info["fid_list"])

        split_dir = self.dataset_dir / split

        self.records: list[tuple[np.ndarray, np.ndarray, float]] = []
        self.fid_id_by_record: list[int] = []
        self.raw_y_by_m: dict[float, np.ndarray] = {}
        self.cond_dim: int | None = None

        for fid_id, (t, fid) in enumerate(zip(self.t_list, self.fid_list)):
            fdir = split_dir / f"fidelity_{fid}"
            xs_path, ys_path = fdir / "Xs.npy", fdir / "ys.npy"
            if not xs_path.exists() or not ys_path.exists():
                continue
            Xs = np.load(xs_path).astype(np.float32)
            ys = np.load(ys_path).astype(np.float32)
            if self.cond_dim is None:
                self.cond_dim = int(Xs.shape[1])
            elif Xs.shape[1] != self.cond_dim:
                raise ValueError(
                    f"cond_dim mismatch in {fdir}: {Xs.shape[1]} vs {self.cond_dim}"
                )
            self.raw_y_by_m[float(t)] = ys
            for i in range(Xs.shape[0]):
                self.records.append((Xs[i], _bilinear_upsample(ys[i], target_size), float(t)))
                self.fid_id_by_record.append(fid_id)

        if not self.records:
            raise ValueError(f"No fidelity dirs with Xs.npy + ys.npy found under {split_dir}")

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, idx: int):
        X, y, m = self.records[idx]
        return (
            torch.from_numpy(X).float(),
            torch.from_numpy(y).float(),
            torch.tensor(m, dtype=torch.float32),
        )


def compute_per_fidelity_scalers(
    dataset: IFCMultiFidelityDataset,
    indices: Iterable[int] | None = None,
) -> tuple[list[float], list[float]]:
    """Compute `scaler[m] = max(|y|)` per fidelity over the raw per-fidelity
    arrays, restricted to the rows in `indices` (the post-random_split
    training subset). Returns `(m_keys, scalers)` sorted by m.
    """
    if indices is None:
        kept = list(range(len(dataset)))
    else:
        kept = list(indices)

    # Group record indices by fidelity, then map back to row indices into the
    # per-fidelity raw arrays (we walk records in fidelity-id order so
    # row indices line up).
    rows_by_fid: dict[int, list[int]] = {}
    row_within_fid = -1
    last_fid = -1
    record_to_row: list[int] = []
    for fid_id in dataset.fid_id_by_record:
        if fid_id != last_fid:
            row_within_fid = 0
            last_fid = fid_id
        else:
            row_within_fid += 1
        record_to_row.append(row_within_fid)
    for ridx in kept:
        fid_id = dataset.fid_id_by_record[ridx]
        rows_by_fid.setdefault(fid_id, []).append(record_to_row[ridx])

    out: dict[float, float] = {}
    for fid_id, rows in rows_by_fid.items():
        m = float(dataset.t_list[fid_id])
        raw = dataset.raw_y_by_m.get(m)
        if raw is None or len(rows) == 0:
            continue
        sub = raw[np.asarray(rows, dtype=np.int64)]
        v = float(np.abs(sub).max())
        out[m] = max(v, 1e-12)

    # Fill any missing fidelities (e.g. all rows landed in val) with the
    # global max so inference at that m doesn't divide-by-zero.
    if out:
        global_max = max(out.values())
    else:
        global_max = 1.0
    for fid_id, m in enumerate(dataset.t_list):
        out.setdefault(float(m), global_max)

    items = sorted(out.items())
    return [m for m, _ in items], [s for _, s in items]
