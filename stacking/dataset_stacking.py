"""
Stacking dataset for multi-fidelity 3-D car surface pressure prediction.

For every 3-D mesh point (x, y, z):
  - (x, z) are passed into the frozen 2-D FiLMNet (LF model) together with
    the design's geometric conditions to obtain a low-fidelity pressure guess.
  - The 2-D prediction is de-normalised to physical pressure units and then
    re-normalised using the 3-D (HF) pressure statistics.
  - The final input to the 3-D model is a 4-D coordinate:
        (x_norm_3d, y_norm_3d, z_norm_3d, Cp_2d_feat)

Coordinate convention
---------------------
  2-D model  : x = car length,  y = car height
  3-D mesh   : x = car length,  y = car width,   z = car height
  Mapping    : (x_3d, z_3d)  →  (x_2d, y_2d)
"""

import os, sys, json, numpy as np, pandas as pd, torch, random
import pyvista as pv
from pathlib import Path
from torch.utils.data import Dataset, random_split

# ── reproducibility ──────────────────────────────────────────────────────────
random.seed(0); np.random.seed(0); torch.manual_seed(0)

# ── module search path: import FiLMNet (2-D) and FiLMNet3D (3-D) ─────────────
_HERE   = Path(__file__).resolve().parent
_LF_DIR = _HERE.parent / "lf_data"
_HF_DIR = _HERE.parent / "hf_data"
sys.path.insert(0, str(_LF_DIR))
sys.path.insert(0, str(_HF_DIR))

from film_model_car    import FiLMNet    # 2-D LF model
from film_model_car_3d import FiLMNet3D  # 3-D HF backbone (coord_dim will be 4)


# ─────────────────────────────────────────────────────────────────────────────
# 2-D model loader / inference helper
# ─────────────────────────────────────────────────────────────────────────────

def load_lf_model(lf_weights: Path, lf_cfg: Path, device: torch.device) -> FiLMNet:
    """Load the frozen 2-D FiLMNet from a checkpoint."""
    cfg = json.load(open(lf_cfg))['model']
    model = FiLMNet(
        cond_dim=cfg['cond_dim'],   coord_dim=cfg['coord_dim'],
        output_dim=cfg['output_dim'], hidden_dim=cfg['hidden_dim'],
        num_layers=cfg['num_layers'], extra_layers=cfg['extra_layers'],
    ).to(device)
    model.load_state_dict(torch.load(lf_weights, map_location=device,
                                     weights_only=True))
    model.eval()
    for p in model.parameters():
        p.requires_grad_(False)
    return model


@torch.no_grad()
def predict_2d_batch(lf_model: FiLMNet,
                     xz_norm_np: np.ndarray,   # (N, 2)  — 2-D-normalised
                     cond_norm_np: np.ndarray,  # (C,)    — 2-D-normalised geom
                     device: torch.device,
                     chunk: int = 16384) -> np.ndarray:
    """
    Run the 2-D model over a point cloud in chunks.

    Returns Cp_2d in 2-D normalised pressure space (shape (N,)).
    """
    N = xz_norm_np.shape[0]
    preds = []
    cond_t = torch.from_numpy(cond_norm_np).unsqueeze(0).to(device)   # (1, C)

    for start in range(0, N, chunk):
        end    = min(start + chunk, N)
        c_t    = torch.from_numpy(xz_norm_np[start:end]).unsqueeze(0).to(device)  # (1, n, 2)
        out    = lf_model(c_t, cond_t).squeeze(-1).squeeze(0).cpu().numpy()       # (n,)
        preds.append(out)

    return np.concatenate(preds, axis=0)   # (N,)


# ─────────────────────────────────────────────────────────────────────────────
# Dataset
# ─────────────────────────────────────────────────────────────────────────────

class StackingDataset(Dataset):
    """
    Loads 3-D VTK meshes, augments every surface point with a frozen
    2-D LF model prediction, and returns 4-D coordinates:

        (x_norm_3d, y_norm_3d, z_norm_3d, Cp_2d_feat)

    Cp_2d_feat is the 2-D model's pressure prediction, de-normalised to
    physical units and then re-normalised with the 3-D (HF) pressure stats
    so it lives in the same space as the training target.

    Parameters
    ----------
    csv_path          : path to data_car.csv
    vtk_dir           : directory with *.vtk surface meshes
    lf_ckpt_dir       : directory containing the 2-D model checkpoints
                        (expects film_best.pth / film_final.pth, norm_stats.json,
                        train_config.json)
    lf_weights_name   : which LF weights file to use (default: film_best.pth)
    norm_stats        : pre-computed 3-D normalisation stats (for eval/inference)
    max_pts_per_design: optionally cap points per design to save RAM
    device            : device to use for 2-D inference (default: cuda:0 if available)
    """

    def __init__(self,
                 csv_path: str,
                 vtk_dir: str,
                 lf_ckpt_dir: str,
                 lf_weights_name: str = "film_best.pth",
                 norm_stats: dict | None = None,
                 max_pts_per_design: int | None = None,
                 device: torch.device | None = None):
        super().__init__()

        if device is None:
            device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.device = device

        lf_ckpt_dir = Path(lf_ckpt_dir)

        # ── 2-D model & its norm stats ────────────────────────────────────────
        lf_norm   = json.load(open(lf_ckpt_dir / "norm_stats.json"))
        self.lf_norm = {
            k: np.array(v, dtype=np.float32) if isinstance(v, list) else np.float32(v)
            for k, v in lf_norm.items()
        }
        self.lf_model = load_lf_model(
            lf_weights=lf_ckpt_dir / lf_weights_name,
            lf_cfg=lf_ckpt_dir / "train_config.json",
            device=device,
        )
        print(f"[StackingDataset] Loaded 2-D LF model from {lf_ckpt_dir / lf_weights_name}")

        # Convenience handles for 2-D normalisation
        self.lf_geom_mean  = self.lf_norm['geom_mean']   # (C,)
        self.lf_geom_std   = self.lf_norm['geom_std']    # (C,)
        self.lf_coord_min  = self.lf_norm['coord_min']   # (2,) — [x_min, h_min]
        self.lf_coord_max  = self.lf_norm['coord_max']   # (2,) — [x_max, h_max]
        self.lf_p_mean     = float(self.lf_norm['p_mean'])
        self.lf_p_std      = float(self.lf_norm['p_std'])

        # ── CSV & VTK setup ───────────────────────────────────────────────────
        df = pd.read_csv(csv_path)

        # Geometric parameter columns (col index 3 onward)
        self.geom_cols  = df.columns[3:].tolist()
        self.cond_dim   = len(self.geom_cols)
        self.coord_dim  = 4   # (x, y, z, Cp_2d)
        self.output_dim = 1
        self.max_pts    = max_pts_per_design

        # Filter rows without matching VTK
        valid_rows = []
        for _, row in df.iterrows():
            if os.path.isfile(os.path.join(vtk_dir, f"{row['model_name']}.vtk")):
                valid_rows.append(row)
        df = pd.DataFrame(valid_rows).reset_index(drop=True)
        print(f"[StackingDataset] matched CSV rows with VTK files: {len(df)}")

        self.csv     = df
        self.vtk_dir = vtk_dir

        # ── 3-D normalisation stats ───────────────────────────────────────────
        if norm_stats is None:
            geom_vals = df[self.geom_cols].values.astype(np.float32)
            geom_mean = geom_vals.mean(axis=0)
            geom_std  = geom_vals.std(axis=0)
            geom_std[geom_std == 0] = 1.0

            coord_min = np.array([ np.inf,  np.inf,  np.inf], dtype=np.float32)
            coord_max = np.array([-np.inf, -np.inf, -np.inf], dtype=np.float32)
            p_accum   = []

            print("[StackingDataset] Computing 3-D normalisation stats …")
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

            norm_stats = dict(
                geom_mean=geom_mean, geom_std=geom_std,
                coord_min=coord_min, coord_max=coord_max,
                p_mean=np.float32(p_mean), p_std=np.float32(p_std),
            )
            print(f"[StackingDataset] Norm stats computed from {len(df)} designs")

        self.norm_stats = norm_stats
        self.geom_mean  = norm_stats['geom_mean']
        self.geom_std   = norm_stats['geom_std']
        self.coord_min  = norm_stats['coord_min']  # (3,)
        self.coord_max  = norm_stats['coord_max']  # (3,)
        self.p_mean     = float(norm_stats['p_mean'])
        self.p_std      = float(norm_stats['p_std'])

        # ── Pre-load all designs ──────────────────────────────────────────────
        self.samples = []
        skipped = 0
        for _, row in df.iterrows():
            vtk_path = os.path.join(vtk_dir, f"{row['model_name']}.vtk")
            mesh     = pv.read(vtk_path)
            coords   = mesh.points.astype(np.float32)          # (N, 3) — raw
            p        = mesh.point_data['p'].astype(np.float32)  # (N,)

            if coords.shape[0] == 0:
                skipped += 1
                continue

            # Optional pre-subsampling to cap RAM usage
            if self.max_pts is not None and coords.shape[0] > self.max_pts:
                sel    = np.random.choice(coords.shape[0], self.max_pts, replace=False)
                coords = coords[sel]
                p      = p[sel]

            # ── Compute 2-D LF prediction ────────────────────────────────────
            # 2-D coordinates: (x_raw, z_raw) = (length, height)
            xz_raw = np.stack([coords[:, 0], coords[:, 2]], axis=1)  # (N, 2)

            # Normalise to 2-D model's coordinate space [-1, 1]
            xz_norm = (2.0 * (xz_raw - self.lf_coord_min)
                       / (self.lf_coord_max - self.lf_coord_min + 1e-12) - 1.0)

            # Normalise geom cond with 2-D model's geom stats
            geom_raw = np.array([row[c] for c in self.geom_cols], dtype=np.float32)
            geom_n_2d = (geom_raw - self.lf_geom_mean) / self.lf_geom_std

            # Run 2-D model → Cp_2d in 2-D normalised space (N,)
            cp_2d_norm = predict_2d_batch(
                self.lf_model, xz_norm.astype(np.float32),
                geom_n_2d, self.device
            )

            # De-normalise to physical pressure, then re-normalise to 3-D space
            cp_2d_phys = cp_2d_norm * self.lf_p_std + self.lf_p_mean
            cp_2d_feat = (cp_2d_phys - self.p_mean) / self.p_std   # (N,)

            # ── 3-D coordinate normalisation ─────────────────────────────────
            coords_n = (2.0 * (coords - self.coord_min)
                        / (self.coord_max - self.coord_min + 1e-12) - 1.0)  # (N, 3)

            # Append Cp_2d as 4th coordinate
            coords_4d = np.concatenate(
                [coords_n, cp_2d_feat[:, None]], axis=1
            ).astype(np.float32)   # (N, 4)

            # Normalise pressure target
            p_n = (p - self.p_mean) / self.p_std

            # Normalise geom cond with 3-D (HF) stats
            geom_n_3d = (geom_raw - self.geom_mean) / self.geom_std

            self.samples.append(dict(
                model_name=row['model_name'],
                coords=coords_4d,   # (N, 4): (x_3d, y_3d, z_3d, Cp_2d_feat)
                pressure=p_n,       # (N,)
                cond=geom_n_3d,     # (C,)
            ))
            print(f"  [{len(self.samples):>3d}/{len(df)}] {row['model_name']}  "
                  f"pts={coords.shape[0]}", end="\r", flush=True)

        print()
        print(f"[StackingDataset] designs loaded: {len(self.samples)}, skipped: {skipped}")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        return self.samples[idx]


# ─────────────────────────────────────────────────────────────────────────────
# Collate & split
# ─────────────────────────────────────────────────────────────────────────────

def stacking_collate_fn(batch, n_points: int = 8192):
    """
    Returns
    -------
    coords_batch  : (B, n_points, 4)
    conds_batch   : (B, cond_dim)
    targets_batch : (B, n_points, 1)
    """
    all_coords, all_targets, all_conds = [], [], []

    for sample in batch:
        coords   = sample['coords']    # (N, 4)
        pressure = sample['pressure']  # (N,)
        cond     = sample['cond']      # (C,)

        N = coords.shape[0]
        idx = (np.random.choice(N, n_points, replace=True)
               if N < n_points else
               np.random.choice(N, n_points, replace=False))

        all_coords.append(coords[idx])              # (n_points, 4)
        all_targets.append(pressure[idx][:, None])  # (n_points, 1)
        all_conds.append(cond)

    coords_batch  = torch.from_numpy(np.stack(all_coords,  axis=0))  # (B, N, 4)
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
