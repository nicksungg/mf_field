"""
eval_v2.py  —  Evaluate a Phase-3 stacking_v2 model.

Metrics (per-design, then averaged):
  MAE, MSE, Rel-L1, Rel-L2  in both normalised and physical pressure units.

Usage
-----
  python eval_v2.py --run_name frac010
  python eval_v2.py --run_name frac010 --weights film_final.pth
  python eval_v2.py --run_name frac010 --split val
"""

import argparse, json, sys, numpy as np, torch, pandas as pd
from pathlib import Path
from torch.utils.data import Subset

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parent / "hf_data"))

from model_v2      import FiLMNet3D
from dataset_hf_v2 import HFSurfaceDataset
from dataset_lf_v2 import split_dataset

# ── CLI ───────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Evaluate stacking_v2 Phase-3 model")
parser.add_argument("--run_name",     type=str,  default=None,
                    help="Checkpoint sub-folder (e.g. frac010); "
                         "default: first available run")
parser.add_argument("--weights",      type=str,  default="film_best.pth")
parser.add_argument("--split",        type=str,  default="test",
                    choices=["train", "val", "test"])
parser.add_argument("--n_points",     type=int,  default=0,
                    help="Points per design; 0 = all points")
parser.add_argument("--max_pts_load", type=int,  default=100000)
parser.add_argument("--results_dir",  type=str,  default=None)
parser.add_argument("--csv",          type=str,  default=None)
parser.add_argument("--vtk_dir",      type=str,  default=None)
args = parser.parse_args()

# ── Paths ─────────────────────────────────────────────────────────────────────
HF_DIR   = _HERE.parent / "hf_data"
CSV      = args.csv     or str(HF_DIR / "data_car.csv")
VTK_DIR  = args.vtk_dir or str(HF_DIR / "PressureVTK")

CKPT_BASE = _HERE / "checkpoints"
if args.run_name:
    CKPT_DIR = CKPT_BASE / args.run_name
else:
    candidates = [d for d in CKPT_BASE.iterdir()
                  if d.is_dir() and d.name != "phase1"]
    if not candidates:
        raise RuntimeError(f"No Phase-3 run directories found in {CKPT_BASE}")
    CKPT_DIR = sorted(candidates)[0]
    print(f"[eval] Auto-selected run: {CKPT_DIR.name}")

WEIGHTS_PATH = CKPT_DIR / args.weights
RESULTS_DIR  = Path(args.results_dir) if args.results_dir else CKPT_DIR
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ── Device ────────────────────────────────────────────────────────────────────
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(f"Device: {device}")

# ── Load norm stats ───────────────────────────────────────────────────────────
raw        = json.load(open(CKPT_DIR / "norm_stats.json"))
norm_stats = {k: np.array(v, dtype=np.float32) if isinstance(v, list) else np.float32(v)
              for k, v in raw.items()}

# Remove the LF reference keys before passing to dataset
ds_norm = {k: v for k, v in norm_stats.items()
           if k not in ('lf_p_mean', 'lf_p_std')}

# ── Dataset ───────────────────────────────────────────────────────────────────
MAX_PTS = args.max_pts_load if args.max_pts_load > 0 else None
ds = HFSurfaceDataset(
    csv_path=CSV, vtk_dir=VTK_DIR,
    norm_stats=ds_norm,
    max_pts_per_design=MAX_PTS,
)

SPLIT_PT = CKPT_DIR / "split_indices.pt"
if SPLIT_PT.exists():
    indices   = torch.load(SPLIT_PT, weights_only=False)
    split_map = {
        "train": indices["train_indices"],
        "val":   indices["val_indices"],
        "test":  indices["test_indices"],
    }
    eval_ds = Subset(ds, split_map[args.split])
    print(f"Loaded saved split indices → '{args.split}' split: {len(eval_ds)} designs")
else:
    train_ds, val_ds, test_ds = split_dataset(ds)
    eval_ds = {"train": train_ds, "val": val_ds, "test": test_ds}[args.split]
    print(f"Re-split (no saved indices) → '{args.split}': {len(eval_ds)} designs")

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
p_mean = float(norm_stats["p_mean"])
p_std  = float(norm_stats["p_std"])

def denorm(p_n):
    return p_n * p_std + p_mean

# ── Evaluation ────────────────────────────────────────────────────────────────
per_design = []

with torch.no_grad():
    for i in range(len(eval_ds)):
        sample      = eval_ds[i]
        coords_np   = sample["coords"]    # (N, 3)
        pressure_np = sample["pressure"]  # (N,)
        cond_np     = sample["cond"]      # (C,)
        model_name  = sample["model_name"]

        N = coords_np.shape[0]
        if args.n_points > 0 and N > args.n_points:
            sel         = np.random.choice(N, args.n_points, replace=False)
            coords_np   = coords_np[sel]
            pressure_np = pressure_np[sel]
            N           = args.n_points

        coords_t = torch.from_numpy(coords_np).unsqueeze(0).to(device)  # (1, N, 3)
        cond_t   = torch.from_numpy(cond_np).unsqueeze(0).to(device)    # (1, C)

        pred_norm = model(coords_t, cond_t).squeeze(-1).squeeze(0).cpu().numpy()  # (N,)
        true_norm = pressure_np

        # ── normalised metrics ──
        diff_n   = pred_norm - true_norm
        mae_n    = np.mean(np.abs(diff_n))
        mse_n    = np.mean(diff_n ** 2)
        rel_l1_n = np.sum(np.abs(diff_n)) / (np.sum(np.abs(true_norm)) + 1e-12)
        rel_l2_n = (np.sqrt(np.sum(diff_n**2))
                    / (np.sqrt(np.sum(true_norm**2)) + 1e-12))

        # ── physical pressure metrics ──
        pred_p  = denorm(pred_norm)
        true_p  = denorm(true_norm)
        diff_p  = pred_p - true_p
        mae_p   = np.mean(np.abs(diff_p))
        mse_p   = np.mean(diff_p ** 2)
        rel_l1_p = np.sum(np.abs(diff_p)) / (np.sum(np.abs(true_p)) + 1e-12)
        rel_l2_p = (np.sqrt(np.sum(diff_p**2))
                    / (np.sqrt(np.sum(true_p**2)) + 1e-12))

        per_design.append(dict(
            model_name=model_name, n_points=N,
            mae_norm=mae_n,   mse_norm=mse_n,
            rel_l1_norm=rel_l1_n, rel_l2_norm=rel_l2_n,
            mae_phys=mae_p,   mse_phys=mse_p,
            rel_l1_phys=rel_l1_p, rel_l2_phys=rel_l2_p,
        ))
        print(f"  [{i+1:>3d}/{len(eval_ds)}] {model_name}  "
              f"rel-L2={rel_l2_n:.4f}", end="\r", flush=True)

print()
results_df = pd.DataFrame(per_design)
summary    = results_df.drop(columns=["model_name", "n_points"]).mean()
ckpt_stem  = WEIGHTS_PATH.stem

# ── Print ──────────────────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print(f"  stacking_v2 Evaluation  —  '{args.split}' split  "
      f"({len(eval_ds)} designs)")
print(f"  Run: {CKPT_DIR.name}   Weights: {ckpt_stem}")
print("=" * 65)
print("\n--- Normalised space ---")
print(f"  MAE        : {summary['mae_norm']:.6f}")
print(f"  MSE        : {summary['mse_norm']:.6f}")
print(f"  Relative L1: {summary['rel_l1_norm']:.6f}  "
      f"({summary['rel_l1_norm']*100:.3f}%)")
print(f"  Relative L2: {summary['rel_l2_norm']:.6f}  "
      f"({summary['rel_l2_norm']*100:.3f}%)")
print("\n--- Physical pressure units ---")
print(f"  MAE        : {summary['mae_phys']:.4f}")
print(f"  MSE        : {summary['mse_phys']:.4f}")
print(f"  Relative L1: {summary['rel_l1_phys']:.6f}  "
      f"({summary['rel_l1_phys']*100:.3f}%)")
print(f"  Relative L2: {summary['rel_l2_phys']:.6f}  "
      f"({summary['rel_l2_phys']*100:.3f}%)")
print("=" * 65)

# ── Save ──────────────────────────────────────────────────────────────────────
per_csv     = RESULTS_DIR / f"eval_{args.split}_{ckpt_stem}_per_design.csv"
summary_csv = RESULTS_DIR / f"eval_{args.split}_{ckpt_stem}_summary.csv"
results_df.to_csv(per_csv,     index=False)
summary.to_frame("value").to_csv(summary_csv)
print(f"\nPer-design results → {per_csv}")
print(f"Summary            → {summary_csv}")
