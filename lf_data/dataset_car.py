import os, numpy as np, pandas as pd, torch, random
from torch.utils.data import Dataset, random_split

# Reproducibility
random.seed(0); np.random.seed(0); torch.manual_seed(0)


class CarSurfaceDataset(Dataset):
    """
    Reads data_car.csv + npz_surface_data/*.npz.
    Each sample is one car design with:
      - 2D surface coordinates  (N, 2)
      - surface pressure         (N,)
      - 23 geometric condition parameters (from CSV columns 4–26)

    model_name in CSV matches NPZ filename: {model_name}_surface.npz
    """

    def __init__(self,
                 csv_path: str,
                 npz_dir: str,
                 norm_stats: dict | None = None):
        super().__init__()

        df = pd.read_csv(csv_path)

        # Geometric parameter columns (4th column onward, 0-indexed col 3:)
        self.geom_cols = df.columns[3:].tolist()  # 23 columns
        self.cond_dim  = len(self.geom_cols)
        self.coord_dim = 2   # x, y
        self.output_dim = 1  # pressure

        # ---------- filter rows that have a matching NPZ ----------
        valid_rows = []
        for _, row in df.iterrows():
            npz_path = os.path.join(npz_dir, f"{row['model_name']}_surface.npz")
            if os.path.isfile(npz_path):
                valid_rows.append(row)
        df = pd.DataFrame(valid_rows).reset_index(drop=True)
        print(f"[CarSurfaceDataset] matched CSV rows with NPZ files: {len(df)}")

        self.csv = df
        self.npz_dir = npz_dir

        # ---------- compute or accept normalisation stats ----------
        if norm_stats is None:
            geom_vals = df[self.geom_cols].values.astype(np.float32)
            geom_mean = geom_vals.mean(axis=0)
            geom_std  = geom_vals.std(axis=0)
            geom_std[geom_std == 0] = 1.0

            # Scan all NPZ files for coordinate and pressure stats
            coord_min = np.array([ np.inf,  np.inf], dtype=np.float32)
            coord_max = np.array([-np.inf, -np.inf], dtype=np.float32)
            p_accum = []

            for _, row in df.iterrows():
                npz_path = os.path.join(npz_dir, f"{row['model_name']}_surface.npz")
                d = np.load(npz_path)
                coords = d['surf_coords']  # (N, 2)
                p      = d['surf_p']       # (N,)
                coord_min = np.minimum(coord_min, coords.min(axis=0))
                coord_max = np.maximum(coord_max, coords.max(axis=0))
                p_accum.append(p)

            all_p = np.concatenate(p_accum)
            p_mean = float(all_p.mean())
            p_std  = float(all_p.std())
            if p_std == 0:
                p_std = 1.0

            norm_stats = dict(
                geom_mean=geom_mean, geom_std=geom_std,
                coord_min=coord_min, coord_max=coord_max,
                p_mean=np.float32(p_mean), p_std=np.float32(p_std),
            )
            print(f"[CarSurfaceDataset] Computed norm stats from {len(df)} designs")

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
            npz_path = os.path.join(npz_dir, f"{row['model_name']}_surface.npz")
            d = np.load(npz_path)
            coords = d['surf_coords'].astype(np.float32)  # (N, 2)
            p      = d['surf_p'].astype(np.float32)        # (N,)

            if coords.shape[0] == 0:
                skipped += 1
                continue

            # Normalize coordinates to [-1, 1]
            coords_n = 2.0 * (coords - self.coord_min) / (self.coord_max - self.coord_min + 1e-12) - 1.0

            # Normalize pressure
            p_n = (p - self.p_mean) / self.p_std

            # Normalize geometric condition
            geom_raw = np.array([row[c] for c in self.geom_cols], dtype=np.float32)
            geom_n   = (geom_raw - self.geom_mean) / self.geom_std

            self.samples.append(dict(
                model_name=row['model_name'],
                coords=coords_n,        # (N, 2)  normalized
                pressure=p_n,            # (N,)    normalized
                cond=geom_n,             # (23,)   normalized
            ))

        print(f"[CarSurfaceDataset] designs loaded: {len(self.samples)}, skipped: {skipped}")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        return self.samples[idx]


def car_collate_fn(batch, n_points=5000):
    """
    Collates a batch of designs.
    Returns:
      coords_batch  (B, n_points, 2)
      conds_batch   (B, cond_dim)
      targets_batch (B, n_points, 1)
    """
    all_coords, all_targets, all_conds = [], [], []

    for sample in batch:
        coords   = sample['coords']   # (N, 2)
        pressure = sample['pressure'] # (N,)
        cond     = sample['cond']     # (23,)

        N = coords.shape[0]
        # Guarantee exactly n_points (pad with replacement if N < n_points)
        if N < n_points:
            idx = np.random.choice(N, n_points, replace=True)
        else:
            idx = np.random.choice(N, n_points, replace=False)

        c_sub = coords[idx]              # (n_points, 2)
        p_sub = pressure[idx][:, None]   # (n_points, 1)

        all_coords.append(c_sub)
        all_targets.append(p_sub)
        all_conds.append(cond)           # No tiling required anymore

    coords_batch  = torch.from_numpy(np.stack(all_coords, axis=0))  # (B, N, 2)
    targets_batch = torch.from_numpy(np.stack(all_targets, axis=0)) # (B, N, 1)
    conds_batch   = torch.from_numpy(np.stack(all_conds, axis=0))   # (B, 23)
    
    return coords_batch, conds_batch, targets_batch


def split_dataset(full_dataset, train_ratio=0.8, val_ratio=0.1, test_ratio=0.1):
    """
    Split into train / val / test.
    Default: 80% train, 10% val, 10% test.
    """
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6
    n_total = len(full_dataset)
    n_train = int(train_ratio * n_total)
    n_val   = int(val_ratio * n_total)
    n_test  = n_total - n_train - n_val
    return random_split(full_dataset,
                        [n_train, n_val, n_test],
                        generator=torch.Generator().manual_seed(42))
