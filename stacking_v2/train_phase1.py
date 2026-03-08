"""
train_phase1.py  —  Phase 1: Low-Fidelity (LF) Pre-training.

The shared FiLMNet3D is trained exclusively on the large 2-D LF dataset.
Every surface point is embedded as (x, y=0, z=height) so the model learns
about 3-D coordinate inputs from day one; the width dimension stays at 0
until Phase 3 introduces real 3-D variation.

Output
------
  checkpoints/phase1/
    film_best.pth          — best validation weights
    film_final.pth         — final weights after all epochs
    film_epoch_?????.pth   — periodic snapshots (every 500 epochs)
    norm_stats.json        — LF  normalisation stats  (coord + geom + p)
    train_config.json      — full hyper-parameter record
    loss_history.csv
    loss_curve.png

Usage
-----
  python train_phase1.py
  python train_phase1.py --epochs 5000 --hidden_dim 512 --num_layers 8
"""

import os, sys, json, time, argparse
import numpy as np, torch
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from torch.utils.data import DataLoader, Subset

# ── add parent module paths ───────────────────────────────────────────────────
_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parent / "hf_data"))

from model_v2        import FiLMNet3D
from dataset_lf_v2  import LFSurfaceDataset, collate_fn, split_dataset

# ── CLI ───────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Phase-1 LF pre-training")
parser.add_argument("--epochs",       type=int,   default=5000)
parser.add_argument("--batch_size",   type=int,   default=32)
parser.add_argument("--lr",           type=float, default=5e-4)
parser.add_argument("--n_points",     type=int,   default=4096,
                    help="Surface points sampled per design per step "
                         "(LF has fewer points than HF 3-D meshes)")
parser.add_argument("--hidden_dim",   type=int,   default=512)
parser.add_argument("--num_layers",   type=int,   default=8)
parser.add_argument("--extra_layers", type=int,   default=5)
parser.add_argument("--y_width_hint", type=float, default=1.01,
                    help="Half-width of car [m] used when building coord_min/max "
                         "for the y-axis (should match HF VTK y range ≈ ±1.01 m)")
parser.add_argument("--z_noise_std", type=float, default=0.05,
                    help="Std-dev of Gaussian noise added to the normalised y-coord "
                         "(the z=0 span dimension) during Phase-1 training. "
                         "Keeps z-input weights active so the network does not "
                         "collapse 3-D space into a 2-D projection. "
                         "Applied to training batches only (not validation). "
                         "Default 0.05 (5%% of the normalised range).")
# LF data paths
parser.add_argument("--csv",          type=str, default=None)
parser.add_argument("--npz_dir",      type=str, default=None)
args = parser.parse_args()

# ── Paths ─────────────────────────────────────────────────────────────────────
LF_DIR  = _HERE.parent / "lf_data"
CSV     = args.csv    or str(LF_DIR / "data_car.csv")
NPZ_DIR = args.npz_dir or str(LF_DIR / "npz_surface_data")

CKPT_DIR = _HERE / "checkpoints" / "phase1"
CKPT_DIR.mkdir(parents=True, exist_ok=True)

BEST_PATH      = CKPT_DIR / "film_best.pth"
FINAL_PATH     = CKPT_DIR / "film_final.pth"
CFG_PATH       = CKPT_DIR / "train_config.json"
NORM_JSON_PATH = CKPT_DIR / "norm_stats.json"
LOSS_CSV_PATH  = CKPT_DIR / "loss_history.csv"
LOSS_PLOT_PATH = CKPT_DIR / "loss_curve.png"
RESUME_PATH    = CKPT_DIR / "resume_state.pth"

# ── Hyper-parameters ──────────────────────────────────────────────────────────
EPOCHS       = args.epochs
BATCH_SIZE   = args.batch_size
LR           = args.lr
N_POINTS     = args.n_points
TRAIN_RATIO  = 0.8
VAL_RATIO    = 0.1
TEST_RATIO   = 0.1
HIDDEN_DIM   = args.hidden_dim
NUM_LAYERS   = args.num_layers
EXTRA_LAYERS = args.extra_layers
COORD_DIM    = 3    # (x, y=0, z)
OUTPUT_DIM   = 1
Z_NOISE_STD  = args.z_noise_std

# ── Device ────────────────────────────────────────────────────────────────────
cuda_avail = torch.cuda.is_available()
device     = torch.device("cuda:0" if cuda_avail else "cpu")
print(f"Device: {device}" + (f"  ({torch.cuda.get_device_name(0)})" if cuda_avail else ""))
use_amp = cuda_avail
scaler  = torch.amp.GradScaler("cuda", enabled=use_amp)

# ── Dataset ───────────────────────────────────────────────────────────────────
ds = LFSurfaceDataset(
    csv_path=CSV,
    npz_dir=NPZ_DIR,
    norm_stats=None,         # compute from LF data + y_hint
    y_width_hint=args.y_width_hint,
)
COND_DIM = ds.cond_dim

# Persist norm stats so Phase 3 can load them
norm_save = {k: v.tolist() if isinstance(v, np.ndarray) else float(v)
             for k, v in ds.norm_stats.items()}
json.dump(norm_save, open(NORM_JSON_PATH, "w"), indent=2)
print(f"Saved LF norm stats → {NORM_JSON_PATH}")
print(f"  coord_min : {ds.coord_min}")
print(f"  coord_max : {ds.coord_max}")
print(f"  p_mean    : {ds.p_mean:.4f}   p_std : {ds.p_std:.4f}")

train_ds, val_ds, test_ds = split_dataset(ds, TRAIN_RATIO, VAL_RATIO, TEST_RATIO)
print(f"Split — Train: {len(train_ds)}, Val: {len(val_ds)}, Test: {len(test_ds)}")

torch.save({'train_indices': list(train_ds.indices),
            'val_indices':   list(val_ds.indices),
            'test_indices':  list(test_ds.indices)},
           CKPT_DIR / "split_indices.pt")

collate      = lambda b: collate_fn(b, n_points=N_POINTS)
train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True,
                          collate_fn=collate, num_workers=4, pin_memory=True)
val_loader   = DataLoader(val_ds,   batch_size=BATCH_SIZE, shuffle=False,
                          collate_fn=collate, num_workers=4, pin_memory=True)

# ── Model ─────────────────────────────────────────────────────────────────────
model = FiLMNet3D(
    cond_dim=COND_DIM, coord_dim=COORD_DIM, output_dim=OUTPUT_DIM,
    hidden_dim=HIDDEN_DIM, num_layers=NUM_LAYERS, extra_layers=EXTRA_LAYERS,
).to(device)

total_params = sum(p.numel() for p in model.parameters())
print(f"Model parameters: {total_params:,}")

opt       = torch.optim.Adam(model.parameters(), lr=LR)
scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=EPOCHS, eta_min=1e-6)

# ── Resume ────────────────────────────────────────────────────────────────────
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
    print("[Resume] Starting from scratch.")

# ── Save config ───────────────────────────────────────────────────────────────
cfg = dict(
    phase="phase1_lf_pretrain",
    csv=CSV, npz_dir=NPZ_DIR,
    epochs=EPOCHS, batch_size=BATCH_SIZE, lr=LR,
    train_ratio=TRAIN_RATIO, val_ratio=VAL_RATIO, test_ratio=TEST_RATIO,
    n_points=N_POINTS, device=str(device), amp=use_amp,
    y_width_hint=args.y_width_hint,
    z_noise_std=Z_NOISE_STD,
    model=dict(cond_dim=COND_DIM, coord_dim=COORD_DIM, output_dim=OUTPUT_DIM,
               hidden_dim=HIDDEN_DIM, num_layers=NUM_LAYERS,
               extra_layers=EXTRA_LAYERS),
    total_params=total_params,
)
json.dump(cfg, open(CFG_PATH, "w"), indent=2)

# ── Loss ──────────────────────────────────────────────────────────────────────
def hybrid_loss(pred, targets):
    """
    MSE  +  mean relative-L2 loss.

    FP16-safe implementation:
      - Clamp denominator to >= 1e-4 before sqrt so we never divide by zero
        even when targets round to 0 in FP16.  (FP16 smallest normal ~6e-5)
      - Return mse as a plain Python float so .item() is called once,
        outside the autocast region in the training loop.
    """
    diff      = pred - targets                                  # (B, N, 1)
    mse       = torch.mean(diff ** 2)
    diff_sq   = torch.sum(diff ** 2, dim=1)                    # (B, 1)
    true_sq   = torch.sum(targets ** 2, dim=1)                 # (B, 1)
    # clamp before sqrt to avoid inf/nan gradient at 0
    rel_l2    = (torch.sqrt(diff_sq)
                 / torch.clamp(torch.sqrt(true_sq), min=1e-4))
    return mse + torch.mean(rel_l2), mse

# ── Training loop ─────────────────────────────────────────────────────────────
t0 = time.time()

if start_epoch > EPOCHS:
    print(f"[Resume] Already completed {EPOCHS} epochs — nothing to do.")
else:
    print(f"\n[Phase 1] Training epochs {start_epoch} → {EPOCHS}")

for epoch in range(start_epoch, EPOCHS + 1):
    # ── train ──
    model.train()
    running, count = 0.0, 0
    for coords, conds, targets in train_loader:
        coords  = coords.to(device)    # (B, N, 3)
        conds   = conds.to(device)
        targets = targets.to(device)

        # ── z-noise regularisation ──────────────────────────────────────────
        # The y-dimension (index 1) is identically 0 in the LF 2-D data.
        # Adding small Gaussian noise keeps the z-input weights alive and
        # prevents the network collapsing 3-D coordinate space to 2-D.
        if Z_NOISE_STD > 0:
            noise = torch.randn_like(coords[:, :, 1:2]) * Z_NOISE_STD
            coords = coords.clone()
            coords[:, :, 1:2] = coords[:, :, 1:2] + noise
        # ────────────────────────────────────────────────────────────────────

        opt.zero_grad(set_to_none=True)
        with torch.amp.autocast("cuda", enabled=use_amp):
            loss, mse_t = hybrid_loss(model(coords, conds), targets)
        scaler.scale(loss).backward()
        # unscale before clip so clip operates on true gradient magnitudes
        scaler.unscale_(opt)
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        scaler.step(opt)
        scaler.update()
        mse_val = mse_t.item()
        if not (mse_val != mse_val):   # skip NaN (shouldn't happen now)
            running += mse_val * coords.size(0)
            count   += coords.size(0)

    train_mse = running / max(count, 1)
    scheduler.step()

    # ── validate ──
    model.eval()
    vr, vc = 0.0, 0
    with torch.no_grad(), torch.amp.autocast("cuda", enabled=use_amp):
        for coords, conds, targets in val_loader:
            coords  = coords.to(device)
            conds   = conds.to(device)
            targets = targets.to(device)
            _, vm = hybrid_loss(model(coords, conds), targets)
            vr += vm.item() * coords.size(0)
            vc += coords.size(0)
    val_mse = vr / max(vc, 1)

    train_losses.append(train_mse)
    val_losses.append(val_mse)

    # ── checkpoint ──
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
        print(f"  Periodic snapshot saved (epoch {epoch})")

# ── Final saves ───────────────────────────────────────────────────────────────
torch.save(model.state_dict(), FINAL_PATH)
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
plt.xlabel('Epoch')
plt.ylabel('MSE')
plt.title('Phase 1 — LF Pre-training')
plt.grid(True, which="both", ls="--", alpha=0.5)
plt.legend()
plt.tight_layout()
plt.savefig(LOSS_PLOT_PATH)
plt.close()

dt = time.time() - t0
print(f"\nPhase 1 done in {dt/60:.1f} min  ({len(train_losses)} epochs)")
print(f"Best val MSE   : {best_val:.4e}")
print(f"Best weights   : {BEST_PATH}")
print(f"Final weights  : {FINAL_PATH}")
print(f"Norm stats     : {NORM_JSON_PATH}")
print(f"Loss curve     : {LOSS_PLOT_PATH}")
print(f"\n→  Next step: run train_phase3.py using --phase1_dir {CKPT_DIR}")
