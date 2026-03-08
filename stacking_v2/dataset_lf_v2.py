"""
dataset_lf_v2.py  —  Phase-1 (LF 2-D) dataset for stacking_v2.

Coordinate embedding
--------------------
  LF surface data stores 2-D face-centre coordinates:
    surf_coords (M, 2) = (x = car length,  y = car height)

  The 3-D convention used throughout stacking_v2 is:
    (x = car length,  y = car width,  z = car height)

  Embedding:  LF (sx, sy)  →  3-D (sx, 0.0, sy)

  The three-dimensional coordinates are then normalised using the same
  HF norm_stats that Phase-3 uses, so the model sees a consistent input
  space throughout all phases.

Usage
-----
  norm_stats can be None → it will be estimated from the LF data geometry
  and a y-range of [-y_half, +y_half] (pass y_width_hint to match HF range).
  Normally you supply the HF norm_stats so the spaces are aligned.
"""

import os, numpy as np, pandas as pd, torch, random
from pathlib import Path
from torch.utils.data import Dataset

random.seed(0); np.random.seed(0); torch.manual_seed(0)


class LFSurfaceDataset(Dataset):
    """
    Loads 2-D car-wall surface data (npz_surface_data/*.npz) and
    embeds each surface point as a 3-D coordinate with y = 0.

    Parameters
    ----------
    csv_path        : path to data_car.csv
    npz_dir         : directory with *_surface.npz files
    norm_stats      : pre-computed normalisation stats (HF 3-D coord bounds).
                      Keys expected:
                        geom_mean, geom_std      — (C,) geometric condition stats
                        coord_min, coord_max     — (3,) 3-D x/y/z bounds
                        p_mean, p_std            — scalar pressure stats
                      If None, stats are estimated from the LF data itself
                      (y range estimated via y_width_hint).
    y_width_hint    : half-width of the car [m] used to set coord_min/max[1]
                      when norm_stats is None.  Default 1.0 (matches HF ~1 m).
    """

    def __init__(self,
                 csv_path: str,
                 npz_dir: str,
                 norm_stats: dict | None = None,
                 y_width_hint: float = 1.0):
        super().__init__()

        df = pd.read_csv(csv_path)
        self.geom_cols  = df.columns[3:].tolist()
        self.cond_dim   = len(self.geom_cols)
        self.coord_dim  = 3     # (x, y=0, z)
        self.output_dim = 1

        # ── Filter to rows with matching NPZ ─────────────────────────────────
        valid = []
        for _, row in df.iterrows():
            if os.path.isfile(os.path.join(npz_dir, f"{row['model_name']}_surface.npz")):
                valid.append(row)
        df = pd.DataFrame(valid).reset_index(drop=True)
        print(f"[LFSurfaceDataset] matched {len(df)} CSV rows with NPZ files")

        self.csv     = df
        self.npz_dir = npz_dir

        # ── Norm stats ────────────────────────────────────────────────────────
        if norm_stats is None:
            norm_stats = self._compute_norm_stats(df, npz_dir, y_width_hint)
            print(f"[LFSurfaceDataset] Computed norm stats from {len(df)} designs")

        self.norm_stats = norm_stats
        self.geom_mean  = norm_stats['geom_mean'].astype(np.float32)
        self.geom_std   = norm_stats['geom_std'].astype(np.float32)
        self.coord_min  = norm_stats['coord_min'].astype(np.float32)   # (3,)
        self.coord_max  = norm_stats['coord_max'].astype(np.float32)   # (3,)
        self.p_mean     = float(norm_stats['p_mean'])
        self.p_std      = float(norm_stats['p_std'])

        # ── Pre-load all designs ──────────────────────────────────────────────
        self.samples = []
        skipped = 0
        for _, row in df.iterrows():
            npz_path = os.path.join(npz_dir, f"{row['model_name']}_surface.npz")
            d      = np.load(npz_path)
            coords2d = d['surf_coords'].astype(np.float32)   # (N, 2): (x, h)
            p        = d['surf_p'].astype(np.float32)         # (N,)

            if coords2d.shape[0] == 0:
                skipped += 1
                continue

            # Embed as 3-D: (x, y=0, z=h)
            y_col    = np.zeros((coords2d.shape[0], 1), dtype=np.float32)
            coords3d = np.concatenate(
                [coords2d[:, :1], y_col, coords2d[:, 1:]], axis=1
            )    # (N, 3)

            # Normalise to [-1, 1] using 3-D HF coord bounds
            coords_n = (2.0 * (coords3d - self.coord_min)
                        / (self.coord_max - self.coord_min + 1e-12) - 1.0)

            # Normalise pressure
            p_n = (p - self.p_mean) / self.p_std

            # Normalise geometric condition
            geom_raw = np.array([row[c] for c in self.geom_cols], dtype=np.float32)
            geom_n   = (geom_raw - self.geom_mean) / self.geom_std

            self.samples.append(dict(
                model_name=row['model_name'],
                coords=coords_n.astype(np.float32),   # (N, 3)
                pressure=p_n.astype(np.float32),        # (N,)
                cond=geom_n.astype(np.float32),         # (C,)
            ))
            print(f"  [{len(self.samples):>3d}/{len(df)}] {row['model_name']}  "
                  f"pts={coords2d.shape[0]}", end="\r", flush=True)

        print()
        print(f"[LFSurfaceDataset] designs loaded: {len(self.samples)}, skipped: {skipped}")

    # ── internal helper ───────────────────────────────────────────────────────
    @staticmethod
    def _compute_norm_stats(df, npz_dir, y_width_hint):
        geom_vals = df[df.columns[3:]].values.astype(np.float32)
        geom_mean = geom_vals.mean(axis=0)
        geom_std  = geom_vals.std(axis=0)
        geom_std[geom_std == 0] = 1.0

        # x and z (height) from LF files; y is always 0 but we extend with hint
        xz_min = np.array([ np.inf,  np.inf], dtype=np.float32)
        xz_max = np.array([-np.inf, -np.inf], dtype=np.float32)
        p_accum = []

        for _, row in df.iterrows():
            path = os.path.join(npz_dir, f"{row['model_name']}_surface.npz")
            d    = np.load(path)
            c    = d['surf_coords'].astype(np.float32)   # (N, 2): x, height
            p    = d['surf_p'].astype(np.float32)
            xz_min = np.minimum(xz_min, c.min(axis=0))
            xz_max = np.maximum(xz_max, c.max(axis=0))
            p_accum.append(p)

        all_p  = np.concatenate(p_accum)
        p_mean = float(all_p.mean())
        p_std  = float(all_p.std())
        if p_std == 0:
            p_std = 1.0

        # Build 3-D coord stats: x → xz_min[0]; y → [-y_hint, +y_hint]; z → xz_min[1]
        coord_min = np.array([xz_min[0], -y_width_hint, xz_min[1]], dtype=np.float32)
        coord_max = np.array([xz_max[0], +y_width_hint, xz_max[1]], dtype=np.float32)

        return dict(
            geom_mean=geom_mean, geom_std=geom_std,
            coord_min=coord_min, coord_max=coord_max,
            p_mean=np.float32(p_mean), p_std=np.float32(p_std),
        )

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        return self.samples[idx]


# ─────────────────────────────────────────────────────────────────────────────
# Collate & split  (shared by LF and HF datasets)
# ─────────────────────────────────────────────────────────────────────────────

def collate_fn(batch, n_points: int = 8192):
    """
    Randomly samples n_points per design and stacks to tensors.

    Returns
    -------
    coords  : (B, n_points, 3)
    conds   : (B, cond_dim)
    targets : (B, n_points, 1)
    """
    all_c, all_t, all_g = [], [], []
    for s in batch:
        N   = s['coords'].shape[0]
        idx = (np.random.choice(N, n_points, replace=True)
               if N < n_points else
               np.random.choice(N, n_points, replace=False))
        all_c.append(s['coords'][idx])
        all_t.append(s['pressure'][idx][:, None])
        all_g.append(s['cond'])

    return (
        torch.from_numpy(np.stack(all_c, 0)),   # (B, N, 3)
        torch.from_numpy(np.stack(all_g, 0)),   # (B, C)
        torch.from_numpy(np.stack(all_t, 0)),   # (B, N, 1)
    )


def split_dataset(full_ds, train_ratio=0.8, val_ratio=0.1, test_ratio=0.1,
                  seed=42):
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6
    n  = len(full_ds)
    nt = int(train_ratio * n)
    nv = int(val_ratio * n)
    ne = n - nt - nv
    return torch.utils.data.random_split(
        full_ds, [nt, nv, ne],
        generator=torch.Generator().manual_seed(seed)
    )
