"""
dataset_v3.py  —  Paired LF + HF dataset for stacking_v3.

Each sample contains BOTH the 2-D LF surface data (the "physics-context")
AND the 3-D HF surface data (the training targets) for the same design.

Coordinate convention (shared, aligned with stacking_v2)
---------------------------------------------------------
  3-D space : (x = car length,  y = car width,  z = car height)
  LF 2-D    : (sx, sh)  →  embedded as (sx, 0.0, sh) in 3-D
  All coordinates are normalised to [-1, 1] using the HF mesh bounds.

Dataset split
-------------
  split_dataset() does a random 80/10/10 train/val/test split on the
  full paired dataset.  Pass the saved `split_indices.pt` dict to
  torch.utils.data.Subset when reproducing evaluation.

Collate
-------
  paired_collate_fn(batch, n_lf, n_hf)  →  (lf_tokens, hf_tokens, targets, conds)
    lf_tokens : (B, n_lf, C+4)   [x, y=0, z,  cond..., p_lf]
    hf_tokens : (B, n_hf, C+3)   [x, y,   z,  cond...]
    targets   : (B, n_hf, 1)     normalised C_{p,HF}
    conds     : (B, C)            geom condition (for logging / ablation)
"""

import os
import numpy as np
import pandas as pd
import torch
import random
import pyvista as pv
from pathlib import Path
from torch.utils.data import Dataset

random.seed(0)
np.random.seed(0)
torch.manual_seed(0)


# ─────────────────────────────────────────────────────────────────────────────
# Norm-stats helper  (call once before building the dataset)
# ─────────────────────────────────────────────────────────────────────────────

def compute_norm_stats(csv_path: str,
                       vtk_dir:  str,
                       npz_dir:  str) -> dict:
    """
    Compute normalisation statistics from ALL designs that have both
    an HF VTK and an LF NPZ file.

    Returns a dict with keys:
        geom_mean, geom_std   : (C,)  float32
        coord_min, coord_max  : (3,)  float32  — from 3-D HF meshes
        p_mean, p_std         : scalar float32 — from 3-D HF RANS pressure
        lf_p_mean, lf_p_std   : scalar float32 — from 2-D LF pressure
    """
    df        = pd.read_csv(csv_path)
    geom_cols = df.columns[3:].tolist()

    # ── geometric condition stats ────────────────────────────────────────────
    geom_vals       = df[geom_cols].values.astype(np.float32)
    geom_mean       = geom_vals.mean(axis=0)
    geom_std        = geom_vals.std(axis=0)
    geom_std[geom_std == 0] = 1.0

    # ── coord bounds (from HF VTK) + HF pressure ─────────────────────────────
    coord_min = np.array([ np.inf,  np.inf,  np.inf], dtype=np.float32)
    coord_max = np.array([-np.inf, -np.inf, -np.inf], dtype=np.float32)
    hf_p_accum = []

    for _, row in df.iterrows():
        vtk_path = os.path.join(vtk_dir, f"{row['model_name']}.vtk")
        if not os.path.isfile(vtk_path):
            continue
        mesh   = pv.read(vtk_path)
        coords = mesh.points.astype(np.float32)
        p      = mesh.point_data['p'].astype(np.float32)
        coord_min = np.minimum(coord_min, coords.min(axis=0))
        coord_max = np.maximum(coord_max, coords.max(axis=0))
        hf_p_accum.append(p)
        print(f"  [norm] scanning HF: {row['model_name']}", end="\r", flush=True)

    print()
    all_hf_p = np.concatenate(hf_p_accum)
    hf_p_mean = float(all_hf_p.mean())
    hf_p_std  = float(all_hf_p.std())
    if hf_p_std == 0:
        hf_p_std = 1.0

    # ── LF pressure stats ────────────────────────────────────────────────────
    lf_p_accum = []
    for _, row in df.iterrows():
        npz_path = os.path.join(npz_dir, f"{row['model_name']}_surface.npz")
        if not os.path.isfile(npz_path):
            continue
        d = np.load(npz_path)
        lf_p_accum.append(d['surf_p'].astype(np.float32))

    all_lf_p = np.concatenate(lf_p_accum)
    lf_p_mean = float(all_lf_p.mean())
    lf_p_std  = float(all_lf_p.std())
    if lf_p_std == 0:
        lf_p_std = 1.0

    return dict(
        geom_mean=geom_mean.astype(np.float32),
        geom_std=geom_std.astype(np.float32),
        coord_min=coord_min,
        coord_max=coord_max,
        p_mean=np.float32(hf_p_mean),
        p_std=np.float32(hf_p_std),
        lf_p_mean=np.float32(lf_p_mean),
        lf_p_std=np.float32(lf_p_std),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Paired Dataset
# ─────────────────────────────────────────────────────────────────────────────

class PairedMFDataset(Dataset):
    """
    Loads paired LF (npz) + HF (vtk) surface data for each design.

    Each sample dict contains:
        model_name  : str
        lf_coords   : (M, 3)  LF 2-D coords embedded as (x, 0, z), normalised
        lf_pressure : (M,)    normalised LF surface pressure  C_{p,LF}
        hf_coords   : (N, 3)  HF 3-D surface coords, normalised
        hf_pressure : (N,)    normalised HF surface pressure  C_{p,HF}  [target]
        cond        : (C,)    normalised geometric condition
    """

    def __init__(self,
                 csv_path:            str,
                 vtk_dir:             str,
                 npz_dir:             str,
                 norm_stats:          dict | None = None,
                 max_pts_hf:          int  | None = None,
                 max_pts_lf:          int  | None = None):
        super().__init__()

        df             = pd.read_csv(csv_path)
        self.geom_cols = df.columns[3:].tolist()
        self.cond_dim  = len(self.geom_cols)

        # ── Find designs with both VTK and NPZ ────────────────────────────────
        valid = []
        for _, row in df.iterrows():
            vtk_ok = os.path.isfile(os.path.join(vtk_dir,
                                                  f"{row['model_name']}.vtk"))
            npz_ok = os.path.isfile(os.path.join(npz_dir,
                                                  f"{row['model_name']}_surface.npz"))
            if vtk_ok and npz_ok:
                valid.append(row)
        df = pd.DataFrame(valid).reset_index(drop=True)
        print(f"[PairedMFDataset] found {len(df)} designs with both LF+HF files")

        # ── Norm stats ────────────────────────────────────────────────────────
        if norm_stats is None:
            print("[PairedMFDataset] computing norm stats …")
            norm_stats = compute_norm_stats(csv_path, vtk_dir, npz_dir)

        self.norm_stats = norm_stats
        self.geom_mean  = norm_stats['geom_mean'].astype(np.float32)
        self.geom_std   = norm_stats['geom_std'].astype(np.float32)
        self.coord_min  = norm_stats['coord_min'].astype(np.float32)   # (3,)
        self.coord_max  = norm_stats['coord_max'].astype(np.float32)   # (3,)
        self.p_mean     = float(norm_stats['p_mean'])
        self.p_std      = float(norm_stats['p_std'])
        self.lf_p_mean  = float(norm_stats['lf_p_mean'])
        self.lf_p_std   = float(norm_stats['lf_p_std'])

        # ── Pre-load all designs ──────────────────────────────────────────────
        self.samples = []
        skipped = 0
        for _, row in df.iterrows():
            # ── HF VTK ───────────────────────────────────────────────────────
            vtk_path = os.path.join(vtk_dir, f"{row['model_name']}.vtk")
            mesh     = pv.read(vtk_path)
            hf_c     = mesh.points.astype(np.float32)           # (N, 3)
            hf_p     = mesh.point_data['p'].astype(np.float32)  # (N,)

            if hf_c.shape[0] == 0:
                skipped += 1
                continue

            if max_pts_hf and hf_c.shape[0] > max_pts_hf:
                sel  = np.random.choice(hf_c.shape[0], max_pts_hf, replace=False)
                hf_c = hf_c[sel]
                hf_p = hf_p[sel]

            # ── LF NPZ ───────────────────────────────────────────────────────
            npz_path  = os.path.join(npz_dir, f"{row['model_name']}_surface.npz")
            d         = np.load(npz_path)
            coords2d  = d['surf_coords'].astype(np.float32)   # (M, 2): (x, h)
            lf_p_raw  = d['surf_p'].astype(np.float32)        # (M,)

            if coords2d.shape[0] == 0:
                skipped += 1
                continue

            if max_pts_lf and coords2d.shape[0] > max_pts_lf:
                sel      = np.random.choice(coords2d.shape[0], max_pts_lf,
                                            replace=False)
                coords2d = coords2d[sel]
                lf_p_raw = lf_p_raw[sel]

            # Embed 2-D → 3-D: (x, y=0, z=h)
            y_col   = np.zeros((coords2d.shape[0], 1), dtype=np.float32)
            lf_c    = np.concatenate([coords2d[:, :1], y_col,
                                      coords2d[:, 1:]], axis=1)   # (M, 3)

            # ── Normalise ─────────────────────────────────────────────────────
            span = self.coord_max - self.coord_min + 1e-12
            hf_c_n  = (2.0 * (hf_c  - self.coord_min) / span - 1.0)
            lf_c_n  = (2.0 * (lf_c  - self.coord_min) / span - 1.0)
            hf_p_n  = (hf_p     - self.p_mean)    / self.p_std
            lf_p_n  = (lf_p_raw - self.lf_p_mean) / self.lf_p_std

            # ── Geom condition ────────────────────────────────────────────────
            geom_raw = np.array([row[c] for c in self.geom_cols], dtype=np.float32)
            geom_n   = (geom_raw - self.geom_mean) / self.geom_std

            self.samples.append(dict(
                model_name  = row['model_name'],
                lf_coords   = lf_c_n.astype(np.float32),    # (M, 3)
                lf_pressure = lf_p_n.astype(np.float32),    # (M,)
                hf_coords   = hf_c_n.astype(np.float32),    # (N, 3)
                hf_pressure = hf_p_n.astype(np.float32),    # (N,)
                cond        = geom_n.astype(np.float32),     # (C,)
            ))
            n = len(self.samples)
            print(f"  [{n:>4d}/{len(df)}] {row['model_name']}  "
                  f"HF={hf_c.shape[0]}pts  LF={coords2d.shape[0]}pts",
                  end="\r", flush=True)

        print()
        print(f"[PairedMFDataset] loaded: {len(self.samples)}, skipped: {skipped}")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        return self.samples[idx]


# ─────────────────────────────────────────────────────────────────────────────
# Collate  (builds token tensors from raw numpy arrays)
# ─────────────────────────────────────────────────────────────────────────────

def paired_collate_fn(batch: list, n_lf: int = 2048, n_hf: int = 8192):
    """
    Sub-sample n_lf LF points and n_hf HF points per design, then stack
    into the token format expected by MFTransolver.

    Returns
    -------
    lf_tokens : (B, n_lf, C+4)  [x, y=0, z, cond..., p_lf]
    hf_tokens : (B, n_hf, C+3)  [x, y, z, cond...]
    targets   : (B, n_hf, 1)    normalised C_{p,HF}
    conds     : (B, C)
    """
    lf_list, hf_list, tgt_list, cond_list = [], [], [], []

    for s in batch:
        C = s['cond'].shape[0]

        # ── Sample LF ─────────────────────────────────────────────────────────
        M  = s['lf_coords'].shape[0]
        li = (np.random.choice(M, n_lf, replace=True)
              if M < n_lf else
              np.random.choice(M, n_lf, replace=False))

        lf_c   = s['lf_coords'][li]      # (n_lf, 3)
        lf_p   = s['lf_pressure'][li]    # (n_lf,)
        cond_e = np.tile(s['cond'], (n_lf, 1))   # (n_lf, C)
        # LF token: [x, y=0, z,  cond...,  p_lf]
        lf_tok = np.concatenate([lf_c, cond_e, lf_p[:, None]], axis=-1)  # (n_lf, C+4)
        lf_list.append(lf_tok)

        # ── Sample HF ─────────────────────────────────────────────────────────
        N  = s['hf_coords'].shape[0]
        hi = (np.random.choice(N, n_hf, replace=True)
              if N < n_hf else
              np.random.choice(N, n_hf, replace=False))

        hf_c   = s['hf_coords'][hi]      # (n_hf, 3)
        hf_p   = s['hf_pressure'][hi]    # (n_hf,)
        cond_e = np.tile(s['cond'], (n_hf, 1))   # (n_hf, C)
        # HF token: [x, y, z,  cond...]
        hf_tok = np.concatenate([hf_c, cond_e], axis=-1)       # (n_hf, C+3)
        hf_list.append(hf_tok)
        tgt_list.append(hf_p[:, None])                          # (n_hf, 1)
        cond_list.append(s['cond'])

    return (
        torch.from_numpy(np.stack(lf_list,  axis=0)).float(),  # (B, n_lf, C+4)
        torch.from_numpy(np.stack(hf_list,  axis=0)).float(),  # (B, n_hf, C+3)
        torch.from_numpy(np.stack(tgt_list, axis=0)).float(),  # (B, n_hf, 1)
        torch.from_numpy(np.stack(cond_list,axis=0)).float(),  # (B, C)
    )


# ─────────────────────────────────────────────────────────────────────────────
# Train / val / test split
# ─────────────────────────────────────────────────────────────────────────────

def split_dataset(full_ds, train_ratio=0.8, val_ratio=0.1, test_ratio=0.1,
                  seed=42):
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6
    n  = len(full_ds)
    nt = int(train_ratio * n)
    nv = int(val_ratio * n)
    ne = n - nt - nv
    return torch.utils.data.random_split(
        full_ds, [nt, nv, ne],
        generator=torch.Generator().manual_seed(seed),
    )
