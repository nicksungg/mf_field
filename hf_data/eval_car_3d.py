"""
Evaluate FiLMNet3D on the test (or val/train) split.

Metrics (per-design, then averaged):
  MAE    : Mean Absolute Error
  MSE    : Mean Squared Error
  Rel-L1 : ||pred-true||_1 / ||true||_1
  Rel-L2 : ||pred-true||_2 / ||true||_2

All metrics reported in both normalised and physical (original) pressure units.

Usage
-----
    python eval_car_3d.py
    python eval_car_3d.py --split val
    python eval_car_3d.py --weights checkpoints_car_3d/film_epoch_02500.pth
"""

import argparse, json, os, numpy as np, torch, pandas as pd
from pathlib import Path
from torch.utils.data import Subset

from dataset_car_3d    import CarSurface3DDataset, split_dataset
from film_model_car_3d import FiLMNet3D

# ======================= CLI =======================
parser = argparse.ArgumentParser(description="Evaluate FiLMNet3D on 3-D car pressure")
parser.add_argument("--split",       type=str, default="test",
                    choices=["train", "val", "test"])
parser.add_argument("--run_name",    type=str, default=None,
                    help="Checkpoint sub-folder name (e.g. frac100, frac020, frac010, frac005)")
parser.add_argument("--weights",     type=str, default=None,
                    help="Path to .pth weights (default: checkpoints_car_3d/<run_name>/film_best.pth)")
parser.add_argument("--results_dir", type=str, default=None)
parser.add_argument("--n_points",    type=int, default=0,
                    help="Points to evaluate per design; 0 = use all available points")
parser.add_argument("--max_pts_load", type=int, default=100000,
                    help="Max points kept per design in RAM during dataset load")
args = parser.parse_args()

# ======================= Paths =======================
BASE     = Path(__file__).resolve().parent
_ckpt_base = BASE / "checkpoints_car_3d"
CKPT_DIR = (_ckpt_base / args.run_name) if args.run_name else _ckpt_base

CSV      = str(BASE / "data_car.csv")
VTK_DIR  = str(BASE / "PressureVTK")
NORM_JSON = CKPT_DIR / "norm_stats.json"
SPLIT_PT  = CKPT_DIR / "split_indices.pt"
WEIGHTS   = Path(args.weights) if args.weights else CKPT_DIR / "film_best.pth"
RESULTS_DIR = Path(args.results_dir) if args.results_dir else CKPT_DIR
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ======================= Device =======================
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(f"Device: {device}")

# ======================= Norm stats =======================
raw        = json.load(open(NORM_JSON))
norm_stats = {k: np.array(v, dtype=np.float32) if isinstance(v, list) else np.float32(v)
              for k, v in raw.items()}

# ======================= Dataset & split =======================
MAX_PTS = args.max_pts_load if args.max_pts_load > 0 else None
ds = CarSurface3DDataset(
    csv_path=CSV, vtk_dir=VTK_DIR,
    norm_stats=norm_stats,
    max_pts_per_design=MAX_PTS,
)

if SPLIT_PT.exists():
    indices = torch.load(SPLIT_PT, weights_only=False)
    split_map = {
        "train": indices["train_indices"],
        "val":   indices["val_indices"],
        "test":  indices["test_indices"],
    }
    eval_ds = Subset(ds, split_map[args.split])
    print(f"Loaded saved split indices from {SPLIT_PT}")
else:
    train_ds, val_ds, test_ds = split_dataset(ds)
    eval_ds = {"train": train_ds, "val": val_ds, "test": test_ds}[args.split]

print(f"Evaluating on '{args.split}' split: {len(eval_ds)} designs")

# ======================= Model =======================
cfg = json.load(open(CKPT_DIR / "train_config.json"))
m   = cfg["model"]
model = FiLMNet3D(
    cond_dim=m["cond_dim"],     coord_dim=m["coord_dim"],
    output_dim=m["output_dim"], hidden_dim=m["hidden_dim"],
    num_layers=m["num_layers"], extra_layers=m["extra_layers"],
).to(device)
model.load_state_dict(torch.load(WEIGHTS, map_location=device, weights_only=True))
model.eval()
print(f"Loaded weights from {WEIGHTS}")

# ======================= De-normalisation =======================
p_mean = float(norm_stats['p_mean'])
p_std  = float(norm_stats['p_std'])

def denorm(p_norm):
    return p_norm * p_std + p_mean

# ======================= Evaluation =======================
per_design = []

with torch.no_grad():
    for i in range(len(eval_ds)):
        sample     = eval_ds[i]
        coords_np  = sample['coords']    # (N, 3)  normalised
        pressure_np = sample['pressure'] # (N,)    normalised
        cond_np    = sample['cond']      # (C,)    normalised
        model_name = sample['model_name']

        N = coords_np.shape[0]

        # Optional point subsampling for speed
        if args.n_points > 0 and N > args.n_points:
            sel       = np.random.choice(N, args.n_points, replace=False)
            coords_np = coords_np[sel]
            pressure_np = pressure_np[sel]
            N          = args.n_points

        coords_t = torch.from_numpy(coords_np).unsqueeze(0).to(device)  # (1, N, 3)
        cond_t   = torch.from_numpy(cond_np).unsqueeze(0).to(device)    # (1, C)

        pred_norm  = model(coords_t, cond_t).squeeze(-1).squeeze(0).cpu().numpy()  # (N,)
        true_norm  = pressure_np

        # ---- normalised-space metrics ----
        diff_n     = pred_norm - true_norm
        mae_n      = np.mean(np.abs(diff_n))
        mse_n      = np.mean(diff_n ** 2)
        rel_l1_n   = np.sum(np.abs(diff_n))  / (np.sum(np.abs(true_norm)) + 1e-12)
        rel_l2_n   = (np.sqrt(np.sum(diff_n**2))
                      / (np.sqrt(np.sum(true_norm**2)) + 1e-12))

        # ---- physical-space metrics ----
        pred_phys  = denorm(pred_norm)
        true_phys  = denorm(true_norm)
        diff_p     = pred_phys - true_phys
        mae_p      = np.mean(np.abs(diff_p))
        mse_p      = np.mean(diff_p ** 2)
        rel_l1_p   = np.sum(np.abs(diff_p))  / (np.sum(np.abs(true_phys)) + 1e-12)
        rel_l2_p   = (np.sqrt(np.sum(diff_p**2))
                      / (np.sqrt(np.sum(true_phys**2)) + 1e-12))

        per_design.append(dict(
            model_name=model_name, n_points=N,
            mae_norm=mae_n,   mse_norm=mse_n,
            rel_l1_norm=rel_l1_n, rel_l2_norm=rel_l2_n,
            mae_phys=mae_p,   mse_phys=mse_p,
            rel_l1_phys=rel_l1_p, rel_l2_phys=rel_l2_p,
        ))

results_df = pd.DataFrame(per_design)
summary    = results_df.drop(columns=["model_name", "n_points"]).mean()

ckpt_stem = WEIGHTS.stem  # e.g. film_best or film_final

# ======================= Print summary =======================
print("\n" + "=" * 65)
print(f"  FiLMNet3D Evaluation  –  {args.split} split  ({len(eval_ds)} designs)")
print(f"  Run: {args.run_name or 'default'}   Weights: {ckpt_stem}")
print("=" * 65)
print("\n--- Normalised space ---")
print(f"  MAE        : {summary['mae_norm']:.6f}")
print(f"  MSE        : {summary['mse_norm']:.6f}")
print(f"  Relative L1: {summary['rel_l1_norm']:.6f}  ({summary['rel_l1_norm']*100:.3f}%)")
print(f"  Relative L2: {summary['rel_l2_norm']:.6f}  ({summary['rel_l2_norm']*100:.3f}%)")
print("\n--- Physical pressure units ---")
print(f"  MAE        : {summary['mae_phys']:.4f}")
print(f"  MSE        : {summary['mse_phys']:.4f}")
print(f"  Relative L1: {summary['rel_l1_phys']:.6f}  ({summary['rel_l1_phys']*100:.3f}%)")
print(f"  Relative L2: {summary['rel_l2_phys']:.6f}  ({summary['rel_l2_phys']*100:.3f}%)")
print("=" * 65)

# ======================= Save =======================
per_csv     = RESULTS_DIR / f"eval_{args.split}_{ckpt_stem}_per_design.csv"
summary_csv = RESULTS_DIR / f"eval_{args.split}_{ckpt_stem}_summary.csv"
results_df.to_csv(per_csv, index=False)
summary.to_frame("value").to_csv(summary_csv)
print(f"\nPer-design results → {per_csv}")
print(f"Summary            → {summary_csv}")
