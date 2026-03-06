import os, numpy as np, pandas as pd, torch, random
import pyvista as pv
from torch.utils.data import Dataset, random_split

# Reproducibility
random.seed(0); np.random.seed(0); torch.manual_seed(0)


class CarSurface3DDataset(Dataset):
    """
    Reads data_car.csv + PressureVTK/*.vtk (pyvista PolyData).

    Each sample is one 3-D car design with:
      - 3-D surface coordinates   (N, 3)   [x=length, y=width, z=height]
      - surface pressure           (N,)
      - geometric condition params (from CSV columns 3:)

    model_name in CSV matches VTK filename: {model_name}.vtk
    """

    def __init__(self,
                 csv_path: str,
                 vtk_dir: str,
                 norm_stats: dict | None = None,
                 max_pts_per_design: int | None = None):
        """
        Parameters
        ----------
        csv_path            : path to data_car.csv
        vtk_dir             : directory containing the *.vtk surface meshes
        norm_stats          : pre-computed normalisation stats (for eval/inference)
        max_pts_per_design  : if set, randomly subsample to this many points
                              during loading (reduces RAM for very dense meshes)
        """
        super().__init__()

        df = pd.read_csv(csv_path)

        # Geometric parameter columns (from col index 3 onward)
        self.geom_cols  = df.columns[3:].tolist()
        self.cond_dim   = len(self.geom_cols)
        self.coord_dim  = 3   # x, y, z
        self.output_dim = 1   # pressure
        self.max_pts    = max_pts_per_design

        # ---------- filter rows that have a matching VTK ----------
        valid_rows = []
        for _, row in df.iterrows():
            vtk_path = os.path.join(vtk_dir, f"{row['model_name']}.vtk")
            if os.path.isfile(vtk_path):
                valid_rows.append(row)
        df = pd.DataFrame(valid_rows).reset_index(drop=True)
        print(f"[CarSurface3DDataset] matched CSV rows with VTK files: {len(df)}")

        self.csv     = df
        self.vtk_dir = vtk_dir

        # ---------- compute or accept normalisation stats ----------
        if norm_stats is None:
            geom_vals = df[self.geom_cols].values.astype(np.float32)
            geom_mean = geom_vals.mean(axis=0)
            geom_std  = geom_vals.std(axis=0)
            geom_std[geom_std == 0] = 1.0

            coord_min = np.array([ np.inf,  np.inf,  np.inf], dtype=np.float32)
            coord_max = np.array([-np.inf, -np.inf, -np.inf], dtype=np.float32)
            p_accum   = []

            print("[CarSurface3DDataset] Computing normalisation stats …")
            for _, row in df.iterrows():
                vtk_path = os.path.join(vtk_dir, f"{row['model_name']}.vtk")
                mesh     = pv.read(vtk_path)
                coords   = mesh.points.astype(np.float32)          # (N, 3)
                p        = mesh.point_data['p'].astype(np.float32)  # (N,)

                coord_min = np.minimum(coord_min, coords.min(axis=0))
                coord_max = np.maximum(coord_max, coords.max(axis=0))
                p_accum.append(p)

            all_p  = np.concatenate(p_accum)
            p_mean = float(all_p.mean())
            p_std  = float(all_p.std())
            if p_std == 0:
                p_std = 1.0

            norm_stats = dict(
                geom_mean=geom_mean, geom_std=geom_std,
                coord_min=coord_min, coord_max=coord_max,
                p_mean=np.float32(p_mean), p_std=np.float32(p_std),
            )
            print(f"[CarSurface3DDataset] Norm stats computed from {len(df)} designs")

        self.norm_stats = norm_stats
        self.geom_mean  = norm_stats['geom_mean']
        self.geom_std   = norm_stats['geom_std']
        self.coord_min  = norm_stats['coord_min']
        self.coord_max  = norm_stats['coord_max']
        self.p_mean     = norm_stats['p_mean']
        self.p_std      = norm_stats['p_std']

        # ---------- pre-load all designs into memory ----------
        self.samples = []
        skipped = 0
        for _, row in df.iterrows():
            vtk_path = os.path.join(vtk_dir, f"{row['model_name']}.vtk")
            mesh     = pv.read(vtk_path)
            coords   = mesh.points.astype(np.float32)          # (N, 3)
            p        = mesh.point_data['p'].astype(np.float32)  # (N,)

            if coords.shape[0] == 0:
                skipped += 1
                continue

            # Optional pre-subsampling to cap memory usage
            if self.max_pts is not None and coords.shape[0] > self.max_pts:
                sel    = np.random.choice(coords.shape[0], self.max_pts, replace=False)
                coords = coords[sel]
                p      = p[sel]

            # Normalise coordinates to [-1, 1] per axis
            coords_n = (2.0 * (coords - self.coord_min)
                        / (self.coord_max - self.coord_min + 1e-12) - 1.0)

            # Normalise pressure
            p_n = (p - self.p_mean) / self.p_std

            # Normalise geometric condition
            geom_raw = np.array([row[c] for c in self.geom_cols], dtype=np.float32)
            geom_n   = (geom_raw - self.geom_mean) / self.geom_std

            self.samples.append(dict(
                model_name=row['model_name'],
                coords=coords_n,   # (N, 3), normalised
                pressure=p_n,      # (N,),   normalised
                cond=geom_n,       # (C,),   normalised
            ))

        print(f"[CarSurface3DDataset] designs loaded: {len(self.samples)}, skipped: {skipped}")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        return self.samples[idx]


def car_collate_fn_3d(batch, n_points: int = 8192):
    """
    Collates a batch of 3-D designs.

    Returns
    -------
    coords_batch  : (B, n_points, 3)
    conds_batch   : (B, cond_dim)
    targets_batch : (B, n_points, 1)
    """
    all_coords, all_targets, all_conds = [], [], []

    for sample in batch:
        coords   = sample['coords']    # (N, 3)
        pressure = sample['pressure']  # (N,)
        cond     = sample['cond']      # (C,)

        N = coords.shape[0]
        if N < n_points:
            idx = np.random.choice(N, n_points, replace=True)
        else:
            idx = np.random.choice(N, n_points, replace=False)

        all_coords.append(coords[idx])            # (n_points, 3)
        all_targets.append(pressure[idx][:, None]) # (n_points, 1)
        all_conds.append(cond)

    coords_batch  = torch.from_numpy(np.stack(all_coords,  axis=0))  # (B, N, 3)
    targets_batch = torch.from_numpy(np.stack(all_targets, axis=0))  # (B, N, 1)
    conds_batch   = torch.from_numpy(np.stack(all_conds,   axis=0))  # (B, C)

    return coords_batch, conds_batch, targets_batch


def split_dataset(full_dataset, train_ratio=0.8, val_ratio=0.1, test_ratio=0.1):
    """Split into train / val / test (80 / 10 / 10 by default)."""
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6
    n_total = len(full_dataset)
    n_train = int(train_ratio * n_total)
    n_val   = int(val_ratio * n_total)
    n_test  = n_total - n_train - n_val
    return torch.utils.data.random_split(
        full_dataset, [n_train, n_val, n_test],
        generator=torch.Generator().manual_seed(42)
    )
