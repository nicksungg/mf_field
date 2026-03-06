"""
Train FiLMNet3D to predict surface pressure on 3-D car geometries.

Input  : 3-D surface coordinates (x=length, y=width, z=height)
Output : Surface pressure (scalar)
Cond.  : geometric parameters from data_car.csv (col 3 → end)
Data   : PressureVTK/{model_name}.vtk  (pyvista PolyData, point array 'p')

Usage
-----
    python train_car_3d.py
    python train_car_3d.py --epochs 3000 --batch_size 16
"""

import os, json, time, argparse, numpy as np, torch
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from torch.utils.data import DataLoader, Subset

from dataset_car_3d   import CarSurface3DDataset, car_collate_fn_3d, split_dataset
from film_model_car_3d import FiLMNet3D

# ======================= CLI =======================
parser = argparse.ArgumentParser()
parser.add_argument("--epochs",     type=int,   default=5000)
parser.add_argument("--batch_size", type=int,   default=16)
parser.add_argument("--lr",         type=float, default=5e-4)
parser.add_argument("--n_points",   type=int,   default=8192,
                    help="Surface points sub-sampled per design per batch")
parser.add_argument("--hidden_dim", type=int,   default=512)
parser.add_argument("--num_layers", type=int,   default=8)
parser.add_argument("--extra_layers", type=int, default=5)
parser.add_argument("--max_pts_load", type=int, default=100000,
                    help="Max points kept per design in RAM (0 = keep all)")
parser.add_argument("--train_frac", type=float, default=1.0,
                    help="Fraction of training set to use (e.g. 0.2 = 20%%); default 1.0")
parser.add_argument("--run_name", type=str, default=None,
                    help="Checkpoint sub-directory name; defaults to 'frac{train_frac}'")
args = parser.parse_args()

# ======================= Paths =======================
BASE    = Path(__file__).resolve().parent
CSV     = str(BASE / "data_car.csv")
VTK_DIR = str(BASE / "PressureVTK")

_run_name = args.run_name or f"frac{args.train_frac:.2f}".replace(".", "p")
CKPT_DIR = BASE / "checkpoints_car_3d" / _run_name
CKPT_DIR.mkdir(parents=True, exist_ok=True)

BEST_PATH      = CKPT_DIR / "film_best.pth"
FINAL_PATH     = CKPT_DIR / "film_final.pth"
CFG_PATH       = CKPT_DIR / "train_config.json"
NORM_JSON_PATH = CKPT_DIR / "norm_stats.json"
LOSS_CSV_PATH  = CKPT_DIR / "loss_history.csv"
LOSS_PLOT_PATH = CKPT_DIR / "loss_curve.png"

# ======================= Hyper-parameters =======================
EPOCHS       = args.epochs
BATCH_SIZE   = args.batch_size
LR           = args.lr
N_POINTS     = args.n_points
TRAIN_RATIO  = 0.8
VAL_RATIO    = 0.1
TEST_RATIO   = 0.1
TRAIN_FRAC   = max(0.0, min(1.0, args.train_frac))
COND_DIM     = None   # inferred from CSV
COORD_DIM    = 3
OUTPUT_DIM   = 1
HIDDEN_DIM   = args.hidden_dim
NUM_LAYERS   = args.num_layers
EXTRA_LAYERS = args.extra_layers
MAX_PTS_LOAD = args.max_pts_load if args.max_pts_load > 0 else None

# ======================= Device & AMP =======================
cuda_avail = torch.cuda.is_available()
device     = torch.device("cuda:0" if cuda_avail else "cpu")
print(f"Device: {device}" + (f"  ({torch.cuda.get_device_name(0)})" if cuda_avail else ""))

use_amp = cuda_avail
scaler  = torch.amp.GradScaler("cuda", enabled=use_amp)

# ======================= Dataset =======================
ds = CarSurface3DDataset(
    csv_path=CSV,
    vtk_dir=VTK_DIR,
    max_pts_per_design=MAX_PTS_LOAD,
)
COND_DIM = ds.cond_dim

# Save norm stats for later inference
norm_save = {k: v.tolist() if isinstance(v, np.ndarray) else float(v)
             for k, v in ds.norm_stats.items()}
json.dump(norm_save, open(NORM_JSON_PATH, "w"), indent=2)
print(f"Saved norm stats → {NORM_JSON_PATH}")

train_ds, val_ds, test_ds = split_dataset(ds, TRAIN_RATIO, VAL_RATIO, TEST_RATIO)
print(f"Train (full): {len(train_ds)}, Val: {len(val_ds)}, Test: {len(test_ds)}")

# Subsample training set if TRAIN_FRAC < 1.0
if TRAIN_FRAC < 1.0:
    n_sub = max(1, int(len(train_ds) * TRAIN_FRAC))
    sub_gen = torch.Generator().manual_seed(0)
    sub_idx = torch.randperm(len(train_ds), generator=sub_gen)[:n_sub].tolist()
    # sub_idx are indices into train_ds.indices; remap to full dataset indices
    full_sub_idx = [train_ds.indices[i] for i in sub_idx]
    train_ds = torch.utils.data.Subset(ds, full_sub_idx)
    print(f"Subsampled training set: {len(train_ds)} designs ({TRAIN_FRAC*100:.0f}% of full train)")

# Persist split indices so eval can reproduce the exact partition
torch.save({'train_indices': list(train_ds.indices),
            'val_indices':   list(val_ds.indices),
            'test_indices':  list(test_ds.indices)}, CKPT_DIR / "split_indices.pt")

collate       = lambda b: car_collate_fn_3d(b, n_points=N_POINTS)
train_loader  = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True,
                           collate_fn=collate, num_workers=4, pin_memory=True)
val_loader    = DataLoader(val_ds,   batch_size=BATCH_SIZE, shuffle=False,
                           collate_fn=collate, num_workers=4, pin_memory=True)

# ======================= Model =======================
model = FiLMNet3D(
    cond_dim=COND_DIM, coord_dim=COORD_DIM, output_dim=OUTPUT_DIM,
    hidden_dim=HIDDEN_DIM, num_layers=NUM_LAYERS, extra_layers=EXTRA_LAYERS,
).to(device)

total_params = sum(p.numel() for p in model.parameters())
print(f"Model parameters: {total_params:,}")

opt       = torch.optim.Adam(model.parameters(), lr=LR)
scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=EPOCHS, eta_min=1e-6)

# ======================= Save config =======================
cfg = dict(
    csv=CSV, vtk_dir=VTK_DIR,
    epochs=EPOCHS, batch_size=BATCH_SIZE, lr=LR,
    train_ratio=TRAIN_RATIO, val_ratio=VAL_RATIO, test_ratio=TEST_RATIO,
    n_points=N_POINTS, max_pts_load=str(MAX_PTS_LOAD),
    device=str(device), amp=use_amp,
    model=dict(cond_dim=COND_DIM, coord_dim=COORD_DIM, output_dim=OUTPUT_DIM,
               hidden_dim=HIDDEN_DIM, num_layers=NUM_LAYERS, extra_layers=EXTRA_LAYERS),
    total_params=total_params,
    train_frac=TRAIN_FRAC, run_name=_run_name,
)
json.dump(cfg, open(CFG_PATH, "w"), indent=2)

# ======================= Hybrid Loss =======================
def compute_hybrid_loss(pred, targets):
    """
    pred    : (B, N, 1)
    targets : (B, N, 1)

    Returns total_loss (MSE + per-design Relative-L2), mse_item (float)
    """
    mse_loss = torch.mean((pred - targets) ** 2)

    diff_sq_sum = torch.sum((pred - targets) ** 2, dim=1)   # (B, 1)
    true_sq_sum = torch.sum(targets ** 2, dim=1)             # (B, 1)
    rel_l2      = torch.sqrt(diff_sq_sum) / (torch.sqrt(true_sq_sum) + 1e-8)
    rel_l2_loss = torch.mean(rel_l2)

    return mse_loss + rel_l2_loss, mse_loss.item()

# ======================= Training loop =======================
best_val = float("inf")
t0 = time.time()
train_losses, val_losses = [], []

for epoch in range(1, EPOCHS + 1):
    # ---- train ----
    model.train()
    running, count = 0.0, 0
    for coords, conds, targets in train_loader:
        coords  = coords.to(device)
        conds   = conds.to(device)
        targets = targets.to(device)

        opt.zero_grad(set_to_none=True)
        with torch.amp.autocast("cuda", enabled=use_amp):
            pred             = model(coords, conds)
            loss, mse_val    = compute_hybrid_loss(pred, targets)

        scaler.scale(loss).backward()
        scaler.step(opt)
        scaler.update()
        running += mse_val * coords.size(0)
        count   += coords.size(0)

    train_mse = running / max(count, 1)
    scheduler.step()

    # ---- validation ----
    model.eval()
    v_running, v_count = 0.0, 0
    with torch.no_grad(), torch.amp.autocast("cuda", enabled=use_amp):
        for coords, conds, targets in val_loader:
            coords  = coords.to(device)
            conds   = conds.to(device)
            targets = targets.to(device)
            pred            = model(coords, conds)
            _, v_mse_val    = compute_hybrid_loss(pred, targets)
            v_running += v_mse_val * coords.size(0)
            v_count   += coords.size(0)
    val_mse = v_running / max(v_count, 1)

    train_losses.append(train_mse)
    val_losses.append(val_mse)

    # ---- checkpoint ----
    if val_mse < best_val:
        best_val = val_mse
        torch.save(model.state_dict(), BEST_PATH)
        print(f"[{epoch:05d}] train={train_mse:.4e}  val={val_mse:.4e}  <-- BEST")
    elif epoch % 50 == 0:
        print(f"[{epoch:05d}] train={train_mse:.4e}  val={val_mse:.4e}")

    if epoch % 50 == 0:
        pd.DataFrame({
            'epoch': range(1, epoch + 1),
            'train_loss': train_losses,
            'val_loss':   val_losses,
        }).to_csv(LOSS_CSV_PATH, index=False)

    if epoch % 500 == 0:
        torch.save(model.state_dict(), CKPT_DIR / f"film_epoch_{epoch:05d}.pth")
        print(f"  Periodic checkpoint saved (epoch {epoch})")

# ======================= Final saves =======================
torch.save(model.state_dict(), FINAL_PATH)
pd.DataFrame({
    'epoch': range(1, len(train_losses) + 1),
    'train_loss': train_losses,
    'val_loss':   val_losses,
}).to_csv(LOSS_CSV_PATH, index=False)

# Loss plot
loss_df = pd.read_csv(LOSS_CSV_PATH)
plt.figure(figsize=(10, 6))
plt.plot(loss_df['epoch'], loss_df['train_loss'], label='Train', alpha=0.8)
plt.plot(loss_df['epoch'], loss_df['val_loss'],   label='Val',   alpha=0.8)
plt.yscale('log')
plt.xlabel('Epoch'); plt.ylabel('MSE')
plt.title('3-D Car Surface Pressure – FiLMNet3D Training')
plt.grid(True, which="both", ls="--", alpha=0.5)
plt.legend(); plt.tight_layout()
plt.savefig(LOSS_PLOT_PATH); plt.close()

dt = time.time() - t0
print(f"\nDone in {dt/60:.1f} min  ({len(train_losses)} epochs)")
print(f"Best val MSE  : {best_val:.4e}")
print(f"Best weights  : {BEST_PATH}")
print(f"Final weights : {FINAL_PATH}")
print(f"Loss curve    : {LOSS_PLOT_PATH}")
