"""
Evaluate a trained FiLMNet model on the test (or val) split.

Metrics (computed per-design, then averaged):
  - MAE   : Mean Absolute Error
  - MSE   : Mean Squared Error
  - Rel-L1: Relative L1 error  = ||pred-true||_1  / ||true||_1
  - Rel-L2: Relative L2 error  = ||pred-true||_2  / ||true||_2

All metrics are reported in **original (un-normalised) pressure units**
as well as in normalised space for reference.

Usage:
    python eval_car.py                        # evaluate on test split
    python eval_car.py --split val            # evaluate on val split
    python eval_car.py --weights checkpoints_car/film_epoch_02500.pth
"""

import argparse, json, os, numpy as np, torch, pandas as pd
from pathlib import Path
from torch.utils.data import DataLoader, Subset

from dataset_car import CarSurfaceDataset, car_collate_fn, split_dataset
from film_model_car import FiLMNet

# ====================== CLI ======================
parser = argparse.ArgumentParser(description="Evaluate FiLMNet on car surface pressure")
parser.add_argument("--split", type=str, default="test",
                    choices=["train", "val", "test"],
                    help="Which split to evaluate on (default: test)")
parser.add_argument("--weights", type=str, default=None,
                    help="Path to model weights (default: checkpoints_car/film_best.pth)")
parser.add_argument("--batch_size", type=int, default=1,
                    help="Batch size for evaluation (default: 1 = per-design)")
parser.add_argument("--results_dir", type=str, default=None,
                    help="Directory to save results (default: checkpoints_car/)")
args = parser.parse_args()

# ====================== Paths ======================
BASE = Path(__file__).resolve().parent
CKPT_DIR = BASE / "checkpoints_car"

CSV     = str(BASE / "data_car.csv")
NPZ_DIR = str(BASE / "npz_surface_data")
NORM_JSON = CKPT_DIR / "norm_stats.json"
SPLIT_PT  = CKPT_DIR / "split_indices.pt"
WEIGHTS   = Path(args.weights) if args.weights else CKPT_DIR / "film_best.pth"
RESULTS_DIR = Path(args.results_dir) if args.results_dir else CKPT_DIR
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ====================== Device ======================
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(f"Device: {device}")

# ====================== Load norm stats ======================
raw = json.load(open(NORM_JSON))
norm_stats = {k: np.array(v, dtype=np.float32) if isinstance(v, list) else np.float32(v)
              for k, v in raw.items()}

# ====================== Dataset & split ======================
ds = CarSurfaceDataset(csv_path=CSV, npz_dir=NPZ_DIR, norm_stats=norm_stats)

# Reproduce the exact train/val/test split used during training
if SPLIT_PT.exists():
    indices = torch.load(SPLIT_PT, weights_only=False)
    split_map = {"train": indices["train_indices"],
                 "val":   indices["val_indices"],
                 "test":  indices["test_indices"]}
    eval_ds = Subset(ds, split_map[args.split])
    print(f"Loaded saved split indices from {SPLIT_PT}")
else:
    # Fallback: re-derive (same seed guarantees same split)
    train_ds, val_ds, test_ds = split_dataset(ds)
    split_map = {"train": train_ds, "val": val_ds, "test": test_ds}
    eval_ds = split_map[args.split]

print(f"Evaluating on '{args.split}' split: {len(eval_ds)} designs")

# ====================== Model ======================
cfg = json.load(open(CKPT_DIR / "train_config.json"))
m = cfg["model"]
model = FiLMNet(cond_dim=m["cond_dim"], coord_dim=m["coord_dim"],
                output_dim=m["output_dim"], hidden_dim=m["hidden_dim"],
                num_layers=m["num_layers"], extra_layers=m["extra_layers"]).to(device)
model.load_state_dict(torch.load(WEIGHTS, map_location=device, weights_only=True))
model.eval()
print(f"Loaded weights from {WEIGHTS}")

# ====================== De-normalisation helpers ======================
p_mean = float(norm_stats['p_mean'])
p_std  = float(norm_stats['p_std'])


def denorm_pressure(p_norm):
    """Convert normalised pressure back to physical units."""
    return p_norm * p_std + p_mean


# ====================== Evaluation ======================
per_design = []   # per-design metrics

with torch.no_grad():
    for i in range(len(eval_ds)):
        sample = eval_ds[i]
        coords_np  = sample['coords']     # (N, 2)  normalised
        pressure_np = sample['pressure']   # (N,)    normalised
        cond_np    = sample['cond']        # (23,)   normalised
        model_name = sample['model_name']

        N = coords_np.shape[0]
        coords_t = torch.from_numpy(coords_np).unsqueeze(0).to(device) # (1, N, 2)
        cond_t   = torch.from_numpy(cond_np).unsqueeze(0).to(device)   # (1, 23)

        pred_norm = model(coords_t, cond_t).squeeze(-1).cpu().numpy()   # (N,)
        true_norm = pressure_np                                          # (N,)

        # --- metrics in normalised space ---
        diff_norm = pred_norm - true_norm
        mae_norm  = np.mean(np.abs(diff_norm))
        mse_norm  = np.mean(diff_norm ** 2)
        rel_l1_norm = np.sum(np.abs(diff_norm)) / (np.sum(np.abs(true_norm)) + 1e-12)
        rel_l2_norm = np.sqrt(np.sum(diff_norm ** 2)) / (np.sqrt(np.sum(true_norm ** 2)) + 1e-12)

        # --- metrics in original pressure units ---
        pred_phys = denorm_pressure(pred_norm)
        true_phys = denorm_pressure(true_norm)
        diff_phys = pred_phys - true_phys
        mae_phys  = np.mean(np.abs(diff_phys))
        mse_phys  = np.mean(diff_phys ** 2)
        rel_l1_phys = np.sum(np.abs(diff_phys)) / (np.sum(np.abs(true_phys)) + 1e-12)
        rel_l2_phys = np.sqrt(np.sum(diff_phys ** 2)) / (np.sqrt(np.sum(true_phys ** 2)) + 1e-12)

        per_design.append(dict(
            model_name=model_name,
            n_points=N,
            # normalised-space
            mae_norm=mae_norm,
            mse_norm=mse_norm,
            rel_l1_norm=rel_l1_norm,
            rel_l2_norm=rel_l2_norm,
            # physical-space
            mae_phys=mae_phys,
            mse_phys=mse_phys,
            rel_l1_phys=rel_l1_phys,
            rel_l2_phys=rel_l2_phys,
        ))

results_df = pd.DataFrame(per_design)

# ====================== Summary ======================
summary = results_df.drop(columns=["model_name", "n_points"]).mean()

print("\n" + "=" * 60)
print(f"  Evaluation Results  –  {args.split} split  ({len(eval_ds)} designs)")
print("=" * 60)
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
print("=" * 60)

# ====================== Save ======================
per_design_csv = RESULTS_DIR / f"eval_{args.split}_per_design.csv"
summary_csv    = RESULTS_DIR / f"eval_{args.split}_summary.csv"

results_df.to_csv(per_design_csv, index=False)
summary.to_frame("value").to_csv(summary_csv)

print(f"\nPer-design results → {per_design_csv}")
print(f"Summary            → {summary_csv}")
