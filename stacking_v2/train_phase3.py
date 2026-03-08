"""
train_phase3.py  —  Phase 3: High-Fidelity (HF) Fine-tuning.

Loads the Phase-1 pre-trained weights, implements the Phase-2 "bridge"
(freezes the middle FiLM-modulated layers), then fine-tunes on a fraction
of the 3-D HF dataset while the early/late layers adapt to full 3-D variation.

Coordinate consistency
----------------------
  coord_min / coord_max are loaded from the Phase-1 norm_stats.json so the
  model sees the same coordinate space it was pre-trained on.
  Only the HF pressure statistics (p_mean / p_std) are re-derived from the
  VTK files, because 3-D RANS pressure may differ in scale from the 2-D LF
  pressure used in Phase 1.

Trainable / frozen split (default, num_layers=8 → 7 FiLM layers)
-----------------------------------------------------------------
  Always trainable
    modulation_net           (gamma/beta adapt to 3-D geometry)
    mlp.layers[0]            (input projection — learns from new z variation)
    mlp.layers[1]            (early layer kept flexible)
    mlp.layers[6]            (last FiLM layer before residual tail)
    mlp.extra                (unmodulated residual tail)
    mlp.output_layer
  Frozen  [freeze_start=2 .. freeze_end=5]
    mlp.layers[2..5]         (mid-network flow-physics representations)

Usage
-----
  python train_phase3.py --run_name frac0001 --train_frac 0.001
  python train_phase3.py --run_name frac001  --train_frac 0.01
  python train_phase3.py --run_name frac005  --train_frac 0.05
  python train_phase3.py --run_name frac010  --train_frac 0.10
  python train_phase3.py --run_name frac020  --train_frac 0.20
"""

import os, sys, json, time, argparse
import numpy as np, torch, pyvista as pv
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from torch.utils.data import DataLoader, Subset

# ── module paths ──────────────────────────────────────────────────────────────
_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parent / "hf_data"))

from model_v2       import FiLMNet3D, freeze_middle_layers, frozen_param_count
from dataset_hf_v2  import HFSurfaceDataset
from dataset_lf_v2  import collate_fn, split_dataset

# ── CLI ───────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Phase-3 HF fine-tuning")
parser.add_argument("--run_name",     type=str,   required=True,
                    help="Sub-folder name, e.g. frac010")
parser.add_argument("--train_frac",   type=float, default=0.10,
                    help="Fraction of HF training designs to use (0.001 → 0.20)")
parser.add_argument("--phase1_dir",   type=str,   default=None,
                    help="Path to Phase-1 checkpoint dir "
                         "(default: checkpoints/phase1/)")
parser.add_argument("--phase1_weights", type=str, default="film_best.pth",
                    help="Phase-1 weights file to initialise from")
parser.add_argument("--epochs",       type=int,   default=2500)
parser.add_argument("--batch_size",   type=int,   default=16)
parser.add_argument("--lr",           type=float, default=1e-4,
                    help="Fine-tuning LR (lower than Phase-1 to preserve features)")
parser.add_argument("--n_points",     type=int,   default=8192)
parser.add_argument("--max_pts_load", type=int,   default=100000)
parser.add_argument("--freeze_start", type=int,   default=2,
                    help="First mlp.layers index to freeze (inclusive)")
parser.add_argument("--freeze_end",   type=int,   default=5,
                    help="Last  mlp.layers index to freeze (inclusive)")
# HF data paths
parser.add_argument("--csv",     type=str, default=None)
parser.add_argument("--vtk_dir", type=str, default=None)
args = parser.parse_args()

# ── Paths ─────────────────────────────────────────────────────────────────────
HF_DIR   = _HERE.parent / "hf_data"
CSV      = args.csv     or str(HF_DIR / "data_car.csv")
VTK_DIR  = args.vtk_dir or str(HF_DIR / "PressureVTK")

PHASE1_DIR = Path(args.phase1_dir) if args.phase1_dir else \
             _HERE / "checkpoints" / "phase1"
PHASE1_WEIGHTS = PHASE1_DIR / args.phase1_weights

CKPT_DIR = _HERE / "checkpoints" / args.run_name
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
TRAIN_FRAC   = max(0.0, min(1.0, args.train_frac))
MAX_PTS_LOAD = args.max_pts_load if args.max_pts_load > 0 else None
FREEZE_START = args.freeze_start
FREEZE_END   = args.freeze_end

# ── Device ────────────────────────────────────────────────────────────────────
cuda_avail = torch.cuda.is_available()
device     = torch.device("cuda:0" if cuda_avail else "cpu")
print(f"Device: {device}" + (f"  ({torch.cuda.get_device_name(0)})" if cuda_avail else ""))
use_amp = cuda_avail
scaler  = torch.amp.GradScaler("cuda", enabled=use_amp)

# ─────────────────────────────────────────────────────────────────────────────
# Build Phase-3 norm stats
# ─────────────────────────────────────────────────────────────────────────────
# Coord/geom from Phase 1 (coordinate space must match pre-training).
# Pressure stats from HF VTK (3-D RANS may differ in scale from 2-D LF).

print(f"\nLoading Phase-1 norm stats from {PHASE1_DIR / 'norm_stats.json'}")
p1_raw   = json.load(open(PHASE1_DIR / "norm_stats.json"))
p1_norm  = {k: np.array(v, dtype=np.float32) if isinstance(v, list) else np.float32(v)
            for k, v in p1_raw.items()}

# Derive geom stats from HF CSV so conditioning is in-distribution for HF designs
df_hf       = pd.read_csv(CSV)
geom_cols   = df_hf.columns[3:].tolist()
geom_vals   = df_hf[geom_cols].values.astype(np.float32)
hf_geom_mean = geom_vals.mean(axis=0)
hf_geom_std  = geom_vals.std(axis=0)
hf_geom_std[hf_geom_std == 0] = 1.0

# Scan HF VTK files for pressure statistics only (coords will use Phase-1 bounds)
print("Scanning HF VTK files for pressure statistics …")
vtk_files = sorted(Path(VTK_DIR).glob("*.vtk"))
p_accum   = []
for f in vtk_files:
    mesh = pv.read(f)
    p_accum.append(mesh.point_data["p"].astype(np.float32))
all_p    = np.concatenate(p_accum)
hf_p_mean = float(all_p.mean())
hf_p_std  = float(all_p.std())
if hf_p_std == 0:
    hf_p_std = 1.0
print(f"  HF pressure — mean: {hf_p_mean:.4f}   std: {hf_p_std:.4f}")
print(f"  Phase-1 LF  — mean: {float(p1_norm['p_mean']):.4f}   "
      f"std: {float(p1_norm['p_std']):.4f}")

# Merge: Phase-1 coord bounds + HF geom + HF pressure
norm_stats_hf = dict(
    geom_mean=hf_geom_mean,
    geom_std=hf_geom_std,
    coord_min=p1_norm['coord_min'],   # ← Phase-1 coordinate space
    coord_max=p1_norm['coord_max'],   # ← Phase-1 coordinate space
    p_mean=np.float32(hf_p_mean),
    p_std=np.float32(hf_p_std),
)

# Also record Phase-1 pressure stats for later output-rescaling reference
norm_stats_hf['lf_p_mean'] = p1_norm['p_mean']
norm_stats_hf['lf_p_std']  = p1_norm['p_std']

norm_save = {k: v.tolist() if isinstance(v, np.ndarray) else float(v)
             for k, v in norm_stats_hf.items()}
json.dump(norm_save, open(NORM_JSON_PATH, "w"), indent=2)
print(f"Saved HF norm stats → {NORM_JSON_PATH}")

# ── Dataset ───────────────────────────────────────────────────────────────────
ds = HFSurfaceDataset(
    csv_path=CSV,
    vtk_dir=VTK_DIR,
    norm_stats=norm_stats_hf,
    max_pts_per_design=MAX_PTS_LOAD,
)
COND_DIM = ds.cond_dim

train_ds, val_ds, test_ds = split_dataset(ds, TRAIN_RATIO, VAL_RATIO, TEST_RATIO)
print(f"Split — Train (full): {len(train_ds)}, Val: {len(val_ds)}, Test: {len(test_ds)}")

# Sub-sample training set
if TRAIN_FRAC < 1.0:
    n_sub   = max(1, int(len(train_ds) * TRAIN_FRAC))
    sub_gen = torch.Generator().manual_seed(0)
    sub_idx = torch.randperm(len(train_ds), generator=sub_gen)[:n_sub].tolist()
    full_sub_idx = [train_ds.indices[i] for i in sub_idx]
    train_ds = Subset(ds, full_sub_idx)
    print(f"Subsampled training set: {len(train_ds)} designs "
          f"({TRAIN_FRAC*100:.1f}% of full train)")

torch.save({'train_indices': list(train_ds.indices),
            'val_indices':   list(val_ds.indices),
            'test_indices':  list(test_ds.indices)},
           CKPT_DIR / "split_indices.pt")

collate      = lambda b: collate_fn(b, n_points=N_POINTS)
train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True,
                          collate_fn=collate, num_workers=4, pin_memory=True)
val_loader   = DataLoader(val_ds,   batch_size=BATCH_SIZE, shuffle=False,
                          collate_fn=collate, num_workers=4, pin_memory=True)

# ─────────────────────────────────────────────────────────────────────────────
# Model — load Phase-1 weights, then apply Phase-2 bridge (freeze middle layers)
# ─────────────────────────────────────────────────────────────────────────────
p1_cfg = json.load(open(PHASE1_DIR / "train_config.json"))
m      = p1_cfg["model"]

model = FiLMNet3D(
    cond_dim=COND_DIM, coord_dim=m["coord_dim"], output_dim=m["output_dim"],
    hidden_dim=m["hidden_dim"], num_layers=m["num_layers"],
    extra_layers=m["extra_layers"],
).to(device)

print(f"\nLoading Phase-1 weights from {PHASE1_WEIGHTS}")
state_dict = torch.load(PHASE1_WEIGHTS, map_location=device, weights_only=True)
model.load_state_dict(state_dict)
print("Phase-1 weights loaded.")

# ── Phase 2: Bridge — freeze middle layers ────────────────────────────────────
freeze_middle_layers(model, freeze_start=FREEZE_START, freeze_end=FREEZE_END)
n_frozen, n_trainable = frozen_param_count(model)
total_params = n_frozen + n_trainable
print(f"\nPhase-2 bridge applied (freeze layers[{FREEZE_START}..{FREEZE_END}]):")
print(f"  Total params    : {total_params:,}")
print(f"  Frozen params   : {n_frozen:,}  ({100*n_frozen/total_params:.1f}%)")
print(f"  Trainable params: {n_trainable:,}  ({100*n_trainable/total_params:.1f}%)")

# Only pass trainable parameters to the optimiser
opt = torch.optim.Adam(
    filter(lambda p: p.requires_grad, model.parameters()), lr=LR
)
scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=EPOCHS, eta_min=1e-6)

# ── Resume ─────────────────────────────────────────────────────────────────────
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
    # Re-apply freeze (load_state_dict restores all weights but not grad flags)
    freeze_middle_layers(model, FREEZE_START, FREEZE_END)
    print(f"[Resume] Resuming from epoch {start_epoch}  (best_val={best_val:.4e})\n")
else:
    print("[Resume] Starting Phase-3 fine-tuning from scratch.")

# ── Save config ───────────────────────────────────────────────────────────────
cfg = dict(
    phase="phase3_hf_finetune",
    csv=CSV, vtk_dir=VTK_DIR,
    phase1_dir=str(PHASE1_DIR), phase1_weights=args.phase1_weights,
    epochs=EPOCHS, batch_size=BATCH_SIZE, lr=LR,
    train_ratio=TRAIN_RATIO, val_ratio=VAL_RATIO, test_ratio=TEST_RATIO,
    n_points=N_POINTS, max_pts_load=str(MAX_PTS_LOAD),
    device=str(device), amp=use_amp,
    freeze_start=FREEZE_START, freeze_end=FREEZE_END,
    train_frac=TRAIN_FRAC, run_name=args.run_name,
    model=dict(cond_dim=COND_DIM, coord_dim=m["coord_dim"],
               output_dim=m["output_dim"], hidden_dim=m["hidden_dim"],
               num_layers=m["num_layers"], extra_layers=m["extra_layers"]),
    total_params=total_params,
    frozen_params=n_frozen, trainable_params=n_trainable,
)
json.dump(cfg, open(CFG_PATH, "w"), indent=2)

# ── Loss ──────────────────────────────────────────────────────────────────────
def hybrid_loss(pred, targets):
    diff      = pred - targets
    mse       = torch.mean(diff ** 2)
    diff_sq   = torch.sum(diff ** 2, dim=1)
    true_sq   = torch.sum(targets ** 2, dim=1)
    rel_l2    = (torch.sqrt(diff_sq)
                 / torch.clamp(torch.sqrt(true_sq), min=1e-4))
    return mse + torch.mean(rel_l2), mse

# ── Training loop ─────────────────────────────────────────────────────────────
t0 = time.time()

if start_epoch > EPOCHS:
    print(f"[Resume] Already completed {EPOCHS} epochs — nothing to do.")
else:
    print(f"\n[Phase 3] Fine-tuning epochs {start_epoch} → {EPOCHS}  "
          f"({len(train_ds)} HF designs, frac={TRAIN_FRAC:.3f})")

for epoch in range(start_epoch, EPOCHS + 1):
    # ── train ──
    model.train()
    running, count = 0.0, 0
    for coords, conds, targets in train_loader:
        coords  = coords.to(device)
        conds   = conds.to(device)
        targets = targets.to(device)

        opt.zero_grad(set_to_none=True)
        with torch.amp.autocast("cuda", enabled=use_amp):
            loss, mse_t = hybrid_loss(model(coords, conds), targets)
        scaler.scale(loss).backward()
        scaler.unscale_(opt)
        torch.nn.utils.clip_grad_norm_(
            filter(lambda p: p.requires_grad, model.parameters()), max_norm=1.0
        )
        scaler.step(opt)
        scaler.update()
        mse_val = mse_t.item()
        if not (mse_val != mse_val):
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
plt.title(f'Phase 3 HF Fine-tuning — {args.run_name}')
plt.grid(True, which="both", ls="--", alpha=0.5)
plt.legend()
plt.tight_layout()
plt.savefig(LOSS_PLOT_PATH)
plt.close()

dt = time.time() - t0
print(f"\nPhase 3 done in {dt/60:.1f} min  ({len(train_losses)} epochs)")
print(f"Best val MSE   : {best_val:.4e}")
print(f"Best weights   : {BEST_PATH}")
print(f"Final weights  : {FINAL_PATH}")
print(f"Run name       : {args.run_name}")
