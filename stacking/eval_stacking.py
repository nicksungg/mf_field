"""
Evaluate the stacking multi-fidelity model on the test (or val/train) split.

Metrics (per-design, then averaged):
  MAE    : Mean Absolute Error
  MSE    : Mean Squared Error
  Rel-L1 : ||pred-true||_1 / ||true||_1
  Rel-L2 : ||pred-true||_2 / ||true||_2

All metrics reported in both normalised and physical (original) pressure units.

Usage
-----
    python eval_stacking.py
    python eval_stacking.py --split val
    python eval_stacking.py --run_name frac020 --weights film_final.pth
"""

import argparse, json, sys, numpy as np, torch, pandas as pd
from pathlib import Path
from torch.utils.data import Subset

# ── module paths ──────────────────────────────────────────────────────────────
_HERE   = Path(__file__).resolve().parent
_HF_DIR = _HERE.parent / "hf_data"
sys.path.insert(0, str(_HF_DIR))

from film_model_car_3d import FiLMNet3D
from dataset_stacking  import StackingDataset, split_dataset

# ── CLI ───────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Evaluate stacking MF model")
parser.add_argument("--split",       type=str, default="test",
                    choices=["train", "val", "test"])
parser.add_argument("--run_name",    type=str, default=None,
                    help="Checkpoint sub-folder (e.g. frac100, frac020); "
                         "default uses first available run")
parser.add_argument("--weights",     type=str, default="film_best.pth",
                    help="Weights filename inside the run folder")
parser.add_argument("--results_dir", type=str, default=None)
parser.add_argument("--n_points",    type=int, default=0,
                    help="Points per design; 0 = all")
parser.add_argument("--max_pts_load", type=int, default=100000)
parser.add_argument("--lf_ckpt_dir", type=str, default=None)
parser.add_argument("--lf_weights",  type=str, default="film_best.pth")
args = parser.parse_args()

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE      = _HERE
CKPT_BASE = BASE / "checkpoints"

if args.run_name:
    CKPT_DIR = CKPT_BASE / args.run_name
else:
    # auto-pick the first directory in checkpoints/
    candidates = [d for d in CKPT_BASE.iterdir() if d.is_dir()]
    if not candidates:
        raise RuntimeError(f"No run directories found in {CKPT_BASE}")
    CKPT_DIR = sorted(candidates)[0]
    print(f"[eval] Auto-selected run: {CKPT_DIR.name}")

WEIGHTS_PATH = CKPT_DIR / args.weights
RESULTS_DIR  = Path(args.results_dir) if args.results_dir else CKPT_DIR
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

CSV     = str(_HERE.parent / "hf_data" / "data_car.csv")
VTK_DIR = str(_HERE.parent / "hf_data" / "PressureVTK")
LF_CKPT = Path(args.lf_ckpt_dir) if args.lf_ckpt_dir else \
          _HERE.parent / "lf_data" / "checkpoints_car"

NORM_JSON  = CKPT_DIR / "norm_stats.json"
SPLIT_PT   = CKPT_DIR / "split_indices.pt"

# ── Device ────────────────────────────────────────────────────────────────────
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(f"Device: {device}")

# ── Load 3-D norm stats ───────────────────────────────────────────────────────
raw        = json.load(open(NORM_JSON))
norm_stats = {k: np.array(v, dtype=np.float32) if isinstance(v, list) else np.float32(v)
              for k, v in raw.items()}

# ── Dataset (reuses StackingDataset which precomputes 2-D predictions) ────────
MAX_PTS = args.max_pts_load if args.max_pts_load > 0 else None
ds = StackingDataset(
    csv_path=CSV, vtk_dir=VTK_DIR,
    lf_ckpt_dir=str(LF_CKPT),
    lf_weights_name=args.lf_weights,
    norm_stats=norm_stats,
    max_pts_per_design=MAX_PTS,
    device=device,
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

# ── Model ─────────────────────────────────────────────────────────────────────
cfg = json.load(open(CKPT_DIR / "train_config.json"))
m   = cfg["model"]
model = FiLMNet3D(
    cond_dim=m["cond_dim"], coord_dim=m["coord_dim"],
    output_dim=m["output_dim"], hidden_dim=m["hidden_dim"],
    num_layers=m["num_layers"], extra_layers=m["extra_layers"],
).to(device)
model.load_state_dict(torch.load(WEIGHTS_PATH, map_location=device, weights_only=True))
model.eval()
print(f"Loaded weights from {WEIGHTS_PATH}")

# ── De-normalisation ──────────────────────────────────────────────────────────
p_mean = float(norm_stats['p_mean'])
p_std  = float(norm_stats['p_std'])

def denorm(p_n):
    return p_n * p_std + p_mean

# ── Evaluation ────────────────────────────────────────────────────────────────
per_design = []

with torch.no_grad():
    for i in range(len(eval_ds)):
        sample      = eval_ds[i]
        coords_np   = sample['coords']    # (N, 4)  — includes Cp_2d_feat
        pressure_np = sample['pressure']  # (N,)
        cond_np     = sample['cond']      # (C,)
        model_name  = sample['model_name']

        N = coords_np.shape[0]

        if args.n_points > 0 and N > args.n_points:
            sel         = np.random.choice(N, args.n_points, replace=False)
            coords_np   = coords_np[sel]
            pressure_np = pressure_np[sel]
            N           = args.n_points

        coords_t = torch.from_numpy(coords_np).unsqueeze(0).to(device)   # (1, N, 4)
        cond_t   = torch.from_numpy(cond_np).unsqueeze(0).to(device)     # (1, C)

        pred_norm = model(coords_t, cond_t).squeeze(-1).squeeze(0).cpu().numpy()  # (N,)
        true_norm = pressure_np

        # ---- normalised metrics ----
        diff_n   = pred_norm - true_norm
        mae_n    = np.mean(np.abs(diff_n))
        mse_n    = np.mean(diff_n ** 2)
        rel_l1_n = np.sum(np.abs(diff_n)) / (np.sum(np.abs(true_norm)) + 1e-12)
        rel_l2_n = np.sqrt(np.sum(diff_n**2)) / (np.sqrt(np.sum(true_norm**2)) + 1e-12)

        # ---- physical metrics ----
        pred_p   = denorm(pred_norm)
        true_p   = denorm(true_norm)
        diff_p   = pred_p - true_p
        mae_p    = np.mean(np.abs(diff_p))
        mse_p    = np.mean(diff_p ** 2)
        rel_l1_p = np.sum(np.abs(diff_p)) / (np.sum(np.abs(true_p)) + 1e-12)
        rel_l2_p = np.sqrt(np.sum(diff_p**2)) / (np.sqrt(np.sum(true_p**2)) + 1e-12)

        per_design.append(dict(
            model_name=model_name, n_points=N,
            mae_norm=mae_n,   mse_norm=mse_n,
            rel_l1_norm=rel_l1_n, rel_l2_norm=rel_l2_n,
            mae_phys=mae_p,   mse_phys=mse_p,
            rel_l1_phys=rel_l1_p, rel_l2_phys=rel_l2_p,
        ))

results_df = pd.DataFrame(per_design)
summary    = results_df.drop(columns=["model_name", "n_points"]).mean()
ckpt_stem  = WEIGHTS_PATH.stem

# ── Print summary ─────────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print(f"  Stacking MF Evaluation  –  {args.split} split  ({len(eval_ds)} designs)")
print(f"  Run: {CKPT_DIR.name}   Weights: {ckpt_stem}")
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

# ── Save ──────────────────────────────────────────────────────────────────────
per_csv     = RESULTS_DIR / f"eval_{args.split}_{ckpt_stem}_per_design.csv"
summary_csv = RESULTS_DIR / f"eval_{args.split}_{ckpt_stem}_summary.csv"
results_df.to_csv(per_csv, index=False)
summary.to_frame("value").to_csv(summary_csv)
print(f"\nPer-design results → {per_csv}")
print(f"Summary            → {summary_csv}")
