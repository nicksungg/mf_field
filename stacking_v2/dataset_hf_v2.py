"""
dataset_hf_v2.py  —  Phase-3 (HF 3-D) dataset for stacking_v2.

Loads high-fidelity 3-D car surface VTK meshes and returns normalised
3-D coordinates (x, y, z) and pressure.

The coord_min/coord_max MUST be the same as those used in Phase 1 so that
the model sees a consistent input space during fine-tuning.
Supply `norm_stats` computed by train_phase1.py to guarantee this.
"""

import os, numpy as np, pandas as pd, torch, random
import pyvista as pv
from pathlib import Path
from torch.utils.data import Dataset

random.seed(0); np.random.seed(0); torch.manual_seed(0)


class HFSurfaceDataset(Dataset):
    """
    Parameters
    ----------
    csv_path           : path to data_car.csv (HF version — same columns)
    vtk_dir            : directory with *.vtk surface meshes
    norm_stats         : pre-computed normalisation stats (from Phase 1).
                         If None, stats are computed from the loaded VTKs.
    max_pts_per_design : optional cap on points per design to save RAM
    """

    def __init__(self,
                 csv_path: str,
                 vtk_dir: str,
                 norm_stats: dict | None = None,
                 max_pts_per_design: int | None = None):
        super().__init__()

        df = pd.read_csv(csv_path)
        self.geom_cols  = df.columns[3:].tolist()
        self.cond_dim   = len(self.geom_cols)
        self.coord_dim  = 3
        self.output_dim = 1
        self.max_pts    = max_pts_per_design

        # ── Filter to rows with matching VTK ─────────────────────────────────
        valid = []
        for _, row in df.iterrows():
            if os.path.isfile(os.path.join(vtk_dir, f"{row['model_name']}.vtk")):
                valid.append(row)
        df = pd.DataFrame(valid).reset_index(drop=True)
        print(f"[HFSurfaceDataset] matched {len(df)} CSV rows with VTK files")

        self.csv     = df
        self.vtk_dir = vtk_dir

        # ── Norm stats ────────────────────────────────────────────────────────
        if norm_stats is None:
            norm_stats = self._compute_norm_stats(df, vtk_dir)
            print(f"[HFSurfaceDataset] Computed norm stats from {len(df)} designs")

        self.norm_stats = norm_stats
        self.geom_mean  = norm_stats['geom_mean'].astype(np.float32)
        self.geom_std   = norm_stats['geom_std'].astype(np.float32)
        self.coord_min  = norm_stats['coord_min'].astype(np.float32)   # (3,)
        self.coord_max  = norm_stats['coord_max'].astype(np.float32)   # (3,)
        self.p_mean     = float(norm_stats['p_mean'])
        self.p_std      = float(norm_stats['p_std'])

        # ── Pre-load ──────────────────────────────────────────────────────────
        self.samples = []
        skipped = 0
        for _, row in df.iterrows():
            vtk_path = os.path.join(vtk_dir, f"{row['model_name']}.vtk")
            mesh     = pv.read(vtk_path)
            coords   = mesh.points.astype(np.float32)           # (N, 3)
            p        = mesh.point_data['p'].astype(np.float32)  # (N,)

            if coords.shape[0] == 0:
                skipped += 1
                continue

            if self.max_pts and coords.shape[0] > self.max_pts:
                sel    = np.random.choice(coords.shape[0], self.max_pts, replace=False)
                coords = coords[sel]
                p      = p[sel]

            # Normalise coords to [-1, 1]
            coords_n = (2.0 * (coords - self.coord_min)
                        / (self.coord_max - self.coord_min + 1e-12) - 1.0)

            # Normalise pressure
            p_n = (p - self.p_mean) / self.p_std

            # Normalise geom cond
            geom_raw = np.array([row[c] for c in self.geom_cols], dtype=np.float32)
            geom_n   = (geom_raw - self.geom_mean) / self.geom_std

            self.samples.append(dict(
                model_name=row['model_name'],
                coords=coords_n.astype(np.float32),   # (N, 3)
                pressure=p_n.astype(np.float32),        # (N,)
                cond=geom_n.astype(np.float32),         # (C,)
            ))
            print(f"  [{len(self.samples):>3d}/{len(df)}] {row['model_name']}  "
                  f"pts={coords.shape[0]}", end="\r", flush=True)

        print()
        print(f"[HFSurfaceDataset] designs loaded: {len(self.samples)}, skipped: {skipped}")

    # ── internal helper ───────────────────────────────────────────────────────
    @staticmethod
    def _compute_norm_stats(df, vtk_dir):
        geom_vals = df[df.columns[3:]].values.astype(np.float32)
        geom_mean = geom_vals.mean(axis=0)
        geom_std  = geom_vals.std(axis=0)
        geom_std[geom_std == 0] = 1.0

        coord_min = np.array([ np.inf,  np.inf,  np.inf], dtype=np.float32)
        coord_max = np.array([-np.inf, -np.inf, -np.inf], dtype=np.float32)
        p_accum   = []

        print("[HFSurfaceDataset] Computing norm stats …")
        for _, row in df.iterrows():
            mesh   = pv.read(os.path.join(vtk_dir, f"{row['model_name']}.vtk"))
            coords = mesh.points.astype(np.float32)
            p      = mesh.point_data['p'].astype(np.float32)
            coord_min = np.minimum(coord_min, coords.min(axis=0))
            coord_max = np.maximum(coord_max, coords.max(axis=0))
            p_accum.append(p)

        all_p  = np.concatenate(p_accum)
        p_mean = float(all_p.mean())
        p_std  = float(all_p.std())
        if p_std == 0:
            p_std = 1.0

        return dict(
            geom_mean=geom_mean, geom_std=geom_std,
            coord_min=coord_min, coord_max=coord_max,
            p_mean=np.float32(p_mean), p_std=np.float32(p_std),
        )

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        return self.samples[idx]
