"""
Train FiLMNet to predict surface pressure on car geometries.

Input  : 2D surface coordinates (x, y)
Output : Surface pressure (scalar)
Cond.  : 23 geometric parameters from data_car.csv (col 4 → end)

model_name in the CSV maps to {model_name}_surface.npz in npz_surface_data/.
"""

import os, json, time, numpy as np, torch
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from torch.utils.data import DataLoader

from dataset_car import CarSurfaceDataset, car_collate_fn, split_dataset
from torch.utils.data import Subset
from film_model_car import FiLMNet

# ======================= Paths =======================
BASE = Path(__file__).resolve().parent
CSV  = str(BASE / "data_car.csv")
NPZ_DIR = str(BASE / "npz_surface_data")

CKPT_DIR = BASE / "checkpoints_car"
CKPT_DIR.mkdir(parents=True, exist_ok=True)

BEST_PATH      = CKPT_DIR / "film_best.pth"
FINAL_PATH     = CKPT_DIR / "film_final.pth"
CFG_PATH       = CKPT_DIR / "train_config.json"
NORM_JSON_PATH = CKPT_DIR / "norm_stats.json"
LOSS_CSV_PATH  = CKPT_DIR / "loss_history.csv"
LOSS_PLOT_PATH = CKPT_DIR / "loss_curve.png"

# ===================== Hyper-parameters =====================
EPOCHS      = 5000
BATCH_SIZE  = 32
LR          = 5e-4
TRAIN_RATIO = 0.8
VAL_RATIO   = 0.1
TEST_RATIO  = 0.1
N_POINTS    = 3000       # points sub-sampled per design per batch
COND_DIM    = 23         # geometric parameters
COORD_DIM   = 2          # x, y surface coordinates
OUTPUT_DIM  = 1          # pressure

# ===================== Device & AMP =====================
cuda_avail = torch.cuda.is_available()
device = torch.device("cuda:0" if cuda_avail else "cpu")
print(f"Device: {device}" + (f"  ({torch.cuda.get_device_name(0)})" if cuda_avail else ""))

use_amp = cuda_avail
scaler = torch.amp.GradScaler("cuda", enabled=use_amp)

# ===================== Dataset =====================
ds = CarSurfaceDataset(csv_path=CSV, npz_dir=NPZ_DIR)

# Save norm stats for later inference
norm_save = {k: v.tolist() if isinstance(v, np.ndarray) else float(v)
             for k, v in ds.norm_stats.items()}
json.dump(norm_save, open(NORM_JSON_PATH, "w"), indent=2)
print(f"Saved norm stats → {NORM_JSON_PATH}")

train_ds, val_ds, test_ds = split_dataset(ds, train_ratio=TRAIN_RATIO,
                                          val_ratio=VAL_RATIO,
                                          test_ratio=TEST_RATIO)
print(f"Train: {len(train_ds)}, Val: {len(val_ds)}, Test: {len(test_ds)}")

# Save test indices so the eval script can reproduce the exact split
torch.save({'train_indices': train_ds.indices,
            'val_indices':   val_ds.indices,
            'test_indices':  test_ds.indices}, CKPT_DIR / "split_indices.pt")

collate = lambda b: car_collate_fn(b, n_points=N_POINTS)
train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True,
                          collate_fn=collate, num_workers=4, pin_memory=True)
val_loader   = DataLoader(val_ds,   batch_size=BATCH_SIZE, shuffle=False,
                          collate_fn=collate, num_workers=4, pin_memory=True)

# ===================== Model =====================
model = FiLMNet(cond_dim=COND_DIM, coord_dim=COORD_DIM, output_dim=OUTPUT_DIM,
                hidden_dim=256, num_layers=4, extra_layers=3).to(device)

total_params = sum(p.numel() for p in model.parameters())
print(f"Model parameters: {total_params:,}")

opt = torch.optim.Adam(model.parameters(), lr=LR)
scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=EPOCHS, eta_min=1e-6)

# ===================== Save config =====================
cfg = dict(
    csv=CSV, npz_dir=NPZ_DIR,
    epochs=EPOCHS, batch_size=BATCH_SIZE, lr=LR,
    train_ratio=TRAIN_RATIO, val_ratio=VAL_RATIO, test_ratio=TEST_RATIO,
    n_points=N_POINTS,
    device=str(device), amp=use_amp,
    model=dict(cond_dim=COND_DIM, coord_dim=COORD_DIM, output_dim=OUTPUT_DIM,
               hidden_dim=256, num_layers=4, extra_layers=3),
    total_params=total_params,
)
json.dump(cfg, open(CFG_PATH, "w"), indent=2)

# ===================== Training =====================
best_val = float("inf")
t0 = time.time()
train_losses, val_losses = [], []

for epoch in range(1, EPOCHS + 1):
    # ---------- train ----------
    model.train()
    running, count = 0.0, 0
    for coords, conds, targets in train_loader:
        coords  = coords.to(device)
        conds   = conds.to(device)
        targets = targets.to(device)

        opt.zero_grad(set_to_none=True)
        with torch.amp.autocast("cuda", enabled=use_amp):
            pred = model(coords, conds)
            loss = torch.mean((pred - targets) ** 2)

        scaler.scale(loss).backward()
        scaler.step(opt)
        scaler.update()

        running += loss.item() * coords.size(0)
        count   += coords.size(0)

    train_mse = running / max(count, 1)
    scheduler.step()

    # ---------- validation ----------
    model.eval()
    v_running, v_count = 0.0, 0
    with torch.no_grad(), torch.amp.autocast("cuda", enabled=use_amp):
        for coords, conds, targets in val_loader:
            coords  = coords.to(device)
            conds   = conds.to(device)
            targets = targets.to(device)
            pred = model(coords, conds)
            vloss = torch.mean((pred - targets) ** 2)
            v_running += vloss.item() * coords.size(0)
            v_count   += coords.size(0)
    val_mse = v_running / max(v_count, 1)

    train_losses.append(train_mse)
    val_losses.append(val_mse)

    # ---------- checkpoint ----------
    if val_mse < best_val:
        best_val = val_mse
        torch.save(model.state_dict(), BEST_PATH)
        print(f"[epoch {epoch:04d}] train={train_mse:.4e}  val={val_mse:.4e}  <-- BEST")
    elif epoch % 50 == 0:
        print(f"[epoch {epoch:04d}] train={train_mse:.4e}  val={val_mse:.4e}")

    if epoch % 50 == 0:
        pd.DataFrame({
            'epoch': range(1, epoch + 1),
            'train_loss': train_losses,
            'val_loss': val_losses,
        }).to_csv(LOSS_CSV_PATH, index=False)

    if epoch % 500 == 0:
        torch.save(model.state_dict(), CKPT_DIR / f"film_epoch_{epoch:05d}.pth")
        print(f"  Periodic checkpoint saved (epoch {epoch})")

# ===================== Final saves =====================
torch.save(model.state_dict(), FINAL_PATH)

pd.DataFrame({
    'epoch': range(1, len(train_losses) + 1),
    'train_loss': train_losses,
    'val_loss': val_losses,
}).to_csv(LOSS_CSV_PATH, index=False)

# ===================== Loss plot =====================
loss_df = pd.read_csv(LOSS_CSV_PATH)
plt.figure(figsize=(10, 6))
plt.plot(loss_df['epoch'], loss_df['train_loss'], label='Train Loss', alpha=0.8)
plt.plot(loss_df['epoch'], loss_df['val_loss'],   label='Val Loss',   alpha=0.8)
plt.yscale('log')
plt.xlabel('Epoch')
plt.ylabel('MSE')
plt.title('Car Surface Pressure – FiLMNet Training')
plt.grid(True, which="both", ls="--", alpha=0.5)
plt.legend()
plt.tight_layout()
plt.savefig(LOSS_PLOT_PATH)
plt.close()

dt = time.time() - t0
print(f"\nDone in {dt/60:.1f} min  ({len(train_losses)} epochs)")
print(f"Best val MSE:  {best_val:.4e}")
print(f"Best weights:  {BEST_PATH}")
print(f"Final weights: {FINAL_PATH}")
print(f"Loss curve:    {LOSS_PLOT_PATH}")
