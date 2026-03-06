"""
Train the stacking multi-fidelity model.

Input  : 4-D coordinates  (x_3d, y_3d, z_3d, Cp_2d_feat)
           where Cp_2d_feat is the frozen 2-D LF model's pressure prediction,
           de-normalised to physical units and re-normalised with HF stats.
Output : 3-D surface pressure (scalar)
Cond.  : geometric parameters from data_car.csv (col 3 →)

Usage
-----
    python train_stacking.py
    python train_stacking.py --epochs 5000 --batch_size 16 --run_name frac100
    python train_stacking.py --train_frac 0.20 --run_name frac020
"""

import os, sys, json, time, argparse, numpy as np, torch
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from torch.utils.data import DataLoader, Subset

# ── add parent module paths ───────────────────────────────────────────────────
_HERE   = Path(__file__).resolve().parent
_HF_DIR = _HERE.parent / "hf_data"
sys.path.insert(0, str(_HF_DIR))

from film_model_car_3d import FiLMNet3D        # reused with coord_dim=4
from dataset_stacking  import (StackingDataset,
                                stacking_collate_fn,
                                split_dataset)

# ── CLI ───────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Train stacking MF model")
parser.add_argument("--epochs",       type=int,   default=5000)
parser.add_argument("--batch_size",   type=int,   default=16)
parser.add_argument("--lr",           type=float, default=5e-4)
parser.add_argument("--n_points",     type=int,   default=8192)
parser.add_argument("--hidden_dim",   type=int,   default=512)
parser.add_argument("--num_layers",   type=int,   default=8)
parser.add_argument("--extra_layers", type=int,   default=5)
parser.add_argument("--max_pts_load", type=int,   default=100000)
parser.add_argument("--train_frac",   type=float, default=1.0)
parser.add_argument("--run_name",     type=str,   default=None)
parser.add_argument("--lf_ckpt_dir",  type=str,   default=None,
                    help="Path to LF (2-D) checkpoint dir "
                         "(default: ../lf_data/checkpoints_car)")
parser.add_argument("--lf_weights",   type=str,   default="film_best.pth",
                    help="LF weights file name inside lf_ckpt_dir")
args = parser.parse_args()

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE    = _HERE
CSV     = str(_HERE.parent / "hf_data" / "data_car.csv")
VTK_DIR = str(_HERE.parent / "hf_data" / "PressureVTK")
LF_CKPT = Path(args.lf_ckpt_dir) if args.lf_ckpt_dir else \
          _HERE.parent / "lf_data" / "checkpoints_car"

_run_name = args.run_name or (
    f"frac{args.train_frac:.2f}".replace(".", "p")
)
CKPT_DIR = BASE / "checkpoints" / _run_name
CKPT_DIR.mkdir(parents=True, exist_ok=True)

BEST_PATH      = CKPT_DIR / "film_best.pth"
FINAL_PATH     = CKPT_DIR / "film_final.pth"
CFG_PATH       = CKPT_DIR / "train_config.json"
NORM_JSON_PATH = CKPT_DIR / "norm_stats.json"
LOSS_CSV_PATH  = CKPT_DIR / "loss_history.csv"
LOSS_PLOT_PATH = CKPT_DIR / "loss_curve.png"
RESUME_PATH    = CKPT_DIR / "resume_state.pth"   # full state for pause/resume

# ── Hyper-parameters ──────────────────────────────────────────────────────────
EPOCHS       = args.epochs
BATCH_SIZE   = args.batch_size
LR           = args.lr
N_POINTS     = args.n_points
TRAIN_RATIO  = 0.8
VAL_RATIO    = 0.1
TEST_RATIO   = 0.1
TRAIN_FRAC   = max(0.0, min(1.0, args.train_frac))
COORD_DIM    = 4    # (x, y, z, Cp_2d)
OUTPUT_DIM   = 1
HIDDEN_DIM   = args.hidden_dim
NUM_LAYERS   = args.num_layers
EXTRA_LAYERS = args.extra_layers
MAX_PTS_LOAD = args.max_pts_load if args.max_pts_load > 0 else None

# ── Device ────────────────────────────────────────────────────────────────────
cuda_avail = torch.cuda.is_available()
device     = torch.device("cuda:0" if cuda_avail else "cpu")
print(f"Device: {device}" + (f"  ({torch.cuda.get_device_name(0)})" if cuda_avail else ""))

use_amp = cuda_avail
scaler  = torch.amp.GradScaler("cuda", enabled=use_amp)

# ── Dataset ───────────────────────────────────────────────────────────────────
ds = StackingDataset(
    csv_path=CSV,
    vtk_dir=VTK_DIR,
    lf_ckpt_dir=str(LF_CKPT),
    lf_weights_name=args.lf_weights,
    max_pts_per_design=MAX_PTS_LOAD,
    device=device,
)
COND_DIM = ds.cond_dim

# Save 3-D norm stats for eval
norm_save = {k: v.tolist() if isinstance(v, np.ndarray) else float(v)
             for k, v in ds.norm_stats.items()}
json.dump(norm_save, open(NORM_JSON_PATH, "w"), indent=2)

# Save LF model norm stats as well (needed by eval to re-run 2-D inference)
lf_norm_save = {k: v.tolist() if isinstance(v, np.ndarray) else float(v)
                for k, v in ds.lf_norm.items()}
json.dump(lf_norm_save, open(CKPT_DIR / "lf_norm_stats.json", "w"), indent=2)
print(f"Saved HF norm stats → {NORM_JSON_PATH}")

train_ds, val_ds, test_ds = split_dataset(ds, TRAIN_RATIO, VAL_RATIO, TEST_RATIO)
print(f"Train (full): {len(train_ds)}, Val: {len(val_ds)}, Test: {len(test_ds)}")

# Sub-sample training set if requested
if TRAIN_FRAC < 1.0:
    n_sub   = max(1, int(len(train_ds) * TRAIN_FRAC))
    sub_gen = torch.Generator().manual_seed(0)
    sub_idx = torch.randperm(len(train_ds), generator=sub_gen)[:n_sub].tolist()
    full_sub_idx = [train_ds.indices[i] for i in sub_idx]
    train_ds = Subset(ds, full_sub_idx)
    print(f"Subsampled training set: {len(train_ds)} designs "
          f"({TRAIN_FRAC*100:.0f}% of full train)")

# Persist split indices
torch.save({'train_indices': list(train_ds.indices),
            'val_indices':   list(val_ds.indices),
            'test_indices':  list(test_ds.indices)},
           CKPT_DIR / "split_indices.pt")

collate      = lambda b: stacking_collate_fn(b, n_points=N_POINTS)
train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True,
                          collate_fn=collate, num_workers=4, pin_memory=True)
val_loader   = DataLoader(val_ds,   batch_size=BATCH_SIZE, shuffle=False,
                          collate_fn=collate, num_workers=4, pin_memory=True)

# ── Model (FiLMNet3D with coord_dim=4) ───────────────────────────────────────
model = FiLMNet3D(
    cond_dim=COND_DIM, coord_dim=COORD_DIM, output_dim=OUTPUT_DIM,
    hidden_dim=HIDDEN_DIM, num_layers=NUM_LAYERS, extra_layers=EXTRA_LAYERS,
).to(device)

total_params = sum(p.numel() for p in model.parameters())
print(f"Model parameters: {total_params:,}")

opt       = torch.optim.Adam(model.parameters(), lr=LR)
scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=EPOCHS, eta_min=1e-6)

# ── Resume from checkpoint if available ──────────────────────────────────────
start_epoch  = 1
best_val     = float("inf")
train_losses = []
val_losses   = []

if RESUME_PATH.exists():
    print(f"\n[Resume] Loading state from {RESUME_PATH}")
    state = torch.load(RESUME_PATH, map_location=device, weights_only=False)
    model.load_state_dict(state["model"])
    opt.load_state_dict(state["optimizer"])
    scheduler.load_state_dict(state["scheduler"])
    scaler.load_state_dict(state["scaler"])
    start_epoch  = state["epoch"] + 1
    best_val     = state["best_val"]
    train_losses = state["train_losses"]
    val_losses   = state["val_losses"]
    print(f"[Resume] Resuming from epoch {start_epoch}  (best_val={best_val:.4e})\n")
else:
    print("[Resume] No checkpoint found — starting from scratch.")

# ── Save config ───────────────────────────────────────────────────────────────
cfg = dict(
    csv=CSV, vtk_dir=VTK_DIR,
    lf_ckpt_dir=str(LF_CKPT), lf_weights=args.lf_weights,
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

# ── Hybrid Loss ───────────────────────────────────────────────────────────────
def compute_hybrid_loss(pred, targets):
    mse_loss = torch.mean((pred - targets) ** 2)
    diff_sq  = torch.sum((pred - targets) ** 2, dim=1)   # (B, 1)
    true_sq  = torch.sum(targets ** 2, dim=1)             # (B, 1)
    rel_l2   = torch.sqrt(diff_sq) / (torch.sqrt(true_sq) + 1e-8)
    return mse_loss + torch.mean(rel_l2), mse_loss.item()

# ── Training loop ─────────────────────────────────────────────────────────────
t0 = time.time()

if start_epoch > EPOCHS:
    print(f"[Resume] Already completed {EPOCHS} epochs — nothing to do.")
else:
    print(f"[Train] Epochs {start_epoch} → {EPOCHS}")

for epoch in range(start_epoch, EPOCHS + 1):
    # ---- train ----
    model.train()
    running, count = 0.0, 0
    for coords, conds, targets in train_loader:
        coords  = coords.to(device)
        conds   = conds.to(device)
        targets = targets.to(device)

        opt.zero_grad(set_to_none=True)
        with torch.amp.autocast("cuda", enabled=use_amp):
            pred          = model(coords, conds)
            loss, mse_val = compute_hybrid_loss(pred, targets)

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
            pred         = model(coords, conds)
            _, v_mse_val = compute_hybrid_loss(pred, targets)
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

        # ---- save full resume state (pause/resume support) ----
        torch.save({
            "epoch":        epoch,
            "model":        model.state_dict(),
            "optimizer":    opt.state_dict(),
            "scheduler":    scheduler.state_dict(),
            "scaler":       scaler.state_dict(),
            "best_val":     best_val,
            "train_losses": train_losses,
            "val_losses":   val_losses,
        }, RESUME_PATH)

    if epoch % 500 == 0:
        torch.save(model.state_dict(), CKPT_DIR / f"film_epoch_{epoch:05d}.pth")
        print(f"  Periodic checkpoint saved (epoch {epoch})")

# ── Final saves ───────────────────────────────────────────────────────────────
torch.save(model.state_dict(), FINAL_PATH)

# Remove the resume state now that training is complete
if RESUME_PATH.exists():
    RESUME_PATH.unlink()
    print("[Resume] Training complete — resume_state.pth removed.")
pd.DataFrame({
    'epoch': range(1, len(train_losses) + 1),
    'train_loss': train_losses,
    'val_loss':   val_losses,
}).to_csv(LOSS_CSV_PATH, index=False)

loss_df = pd.read_csv(LOSS_CSV_PATH)
plt.figure(figsize=(10, 6))
plt.plot(loss_df['epoch'], loss_df['train_loss'], label='Train', alpha=0.8)
plt.plot(loss_df['epoch'], loss_df['val_loss'],   label='Val',   alpha=0.8)
plt.yscale('log')
plt.xlabel('Epoch'); plt.ylabel('MSE')
plt.title(f'Stacking MF Model – {_run_name}')
plt.grid(True, which="both", ls="--", alpha=0.5)
plt.legend(); plt.tight_layout()
plt.savefig(LOSS_PLOT_PATH); plt.close()

dt = time.time() - t0
print(f"\nDone in {dt/60:.1f} min  ({len(train_losses)} epochs)")
print(f"Best val MSE  : {best_val:.4e}")
print(f"Best weights  : {BEST_PATH}")
print(f"Final weights : {FINAL_PATH}")
print(f"Loss curve    : {LOSS_PLOT_PATH}")
