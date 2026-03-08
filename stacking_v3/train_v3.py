"""
train_v3.py  —  End-to-end training of the Multi-Fidelity Transolver.

Single-phase training: the MFTransolver receives the full 2-D LF surface
pressure as a "physics-context" (Keys/Values) and attends to 3-D HF query
points (Queries) to predict C_{p,HF}.  No pre-training stage is required.

The train_frac flag controls the fraction of HF-labelled designs used for
training (the LF context is available for ALL designs — only the HF labels
are limited).

Output per run
--------------
  checkpoints/<run_name>/
    film_best.pth              — best validation weights
    film_final.pth             — final weights
    film_epoch_?????.pth       — periodic snapshots (every 500 epochs)
    norm_stats.json
    train_config.json
    split_indices.pt
    loss_history.csv
    loss_curve.png

Usage
-----
  python train_v3.py --run_name frac010  --train_frac 0.10
  python train_v3.py --run_name frac020  --train_frac 0.20 --epochs 3000
"""

import os, sys, json, time, argparse
import numpy as np, torch
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from torch.utils.data import DataLoader, Subset

# ── module path ───────────────────────────────────────────────────────────────
_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

from model_v3   import MFTransolver, param_count
from dataset_v3 import PairedMFDataset, paired_collate_fn, split_dataset

# ── CLI ───────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="stacking_v3 MFTransolver training")
parser.add_argument("--run_name",      type=str,   required=True)
parser.add_argument("--train_frac",    type=float, default=0.10)
parser.add_argument("--epochs",        type=int,   default=2500)
parser.add_argument("--batch_size",    type=int,   default=8)
parser.add_argument("--lr",            type=float, default=3e-4)
parser.add_argument("--n_lf",          type=int,   default=2048,
                    help="LF context points per design per step")
parser.add_argument("--n_hf",          type=int,   default=8192,
                    help="HF query points per design per step")
parser.add_argument("--hidden_dim",    type=int,   default=256)
parser.add_argument("--n_slices",      type=int,   default=32)
parser.add_argument("--num_heads",     type=int,   default=8)
parser.add_argument("--encoder_layers",type=int,   default=3)
parser.add_argument("--residual_layers",type=int,  default=3)
parser.add_argument("--pos_enc_freqs", type=int,   default=6)
parser.add_argument("--max_pts_hf",    type=int,   default=100000)
parser.add_argument("--max_pts_lf",    type=int,   default=0,
                    help="Cap on LF points loaded per design (0 = no cap)")
parser.add_argument("--csv",           type=str,   default=None)
parser.add_argument("--vtk_dir",       type=str,   default=None)
parser.add_argument("--npz_dir",       type=str,   default=None)
args = parser.parse_args()

# ── Paths ─────────────────────────────────────────────────────────────────────
HF_DIR  = _HERE.parent / "hf_data"
LF_DIR  = _HERE.parent / "lf_data"
CSV     = args.csv     or str(HF_DIR / "data_car.csv")
VTK_DIR = args.vtk_dir or str(HF_DIR / "PressureVTK")
NPZ_DIR = args.npz_dir or str(LF_DIR / "npz_surface_data")

CKPT_DIR       = _HERE / "checkpoints" / args.run_name
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
N_LF         = args.n_lf
N_HF         = args.n_hf
TRAIN_FRAC   = max(0.0, min(1.0, args.train_frac))
MAX_PTS_HF   = args.max_pts_hf if args.max_pts_hf > 0 else None
MAX_PTS_LF   = args.max_pts_lf if args.max_pts_lf > 0 else None
TRAIN_RATIO  = 0.8
VAL_RATIO    = 0.1
TEST_RATIO   = 0.1

# ── Device ────────────────────────────────────────────────────────────────────
cuda_avail = torch.cuda.is_available()
device     = torch.device("cuda:0" if cuda_avail else "cpu")
print(f"Device: {device}" + (f"  ({torch.cuda.get_device_name(0)})" if cuda_avail else ""))
use_amp = cuda_avail
scaler  = torch.amp.GradScaler("cuda", enabled=use_amp)

# ── Norm stats ────────────────────────────────────────────────────────────────
# Re-use pre-computed stats if available (saves scanning all VTK files again).
# We look for a shared "global_norm_stats.json" in checkpoints/; if absent
# we compute them and save them there for all subsequent runs to reuse.
GLOBAL_NORM_PATH = _HERE / "checkpoints" / "global_norm_stats.json"

if GLOBAL_NORM_PATH.exists():
    print(f"Loading shared norm stats from {GLOBAL_NORM_PATH}")
    raw        = json.load(open(GLOBAL_NORM_PATH))
    norm_stats = {k: np.array(v, dtype=np.float32) if isinstance(v, list)
                     else np.float32(v)
                  for k, v in raw.items()}
else:
    from dataset_v3 import compute_norm_stats
    print("Computing global norm stats (first run — this may take a few minutes)…")
    norm_stats = compute_norm_stats(CSV, VTK_DIR, NPZ_DIR)
    GLOBAL_NORM_PATH.parent.mkdir(parents=True, exist_ok=True)
    save_ns = {k: v.tolist() if isinstance(v, np.ndarray) else float(v)
               for k, v in norm_stats.items()}
    json.dump(save_ns, open(GLOBAL_NORM_PATH, "w"), indent=2)
    print(f"Saved global norm stats → {GLOBAL_NORM_PATH}")

# Save a copy in the run dir for self-contained evaluation
save_ns = {k: v.tolist() if isinstance(v, np.ndarray) else float(v)
           for k, v in norm_stats.items()}
json.dump(save_ns, open(NORM_JSON_PATH, "w"), indent=2)

# ── Dataset ───────────────────────────────────────────────────────────────────
ds = PairedMFDataset(
    csv_path=CSV, vtk_dir=VTK_DIR, npz_dir=NPZ_DIR,
    norm_stats=norm_stats,
    max_pts_hf=MAX_PTS_HF,
    max_pts_lf=MAX_PTS_LF,
)
COND_DIM = ds.cond_dim

train_ds, val_ds, test_ds = split_dataset(ds, TRAIN_RATIO, VAL_RATIO, TEST_RATIO)
print(f"Full split — Train: {len(train_ds)}, Val: {len(val_ds)}, Test: {len(test_ds)}")

# Sub-sample training HF-labelled designs
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

collate      = lambda b: paired_collate_fn(b, n_lf=N_LF, n_hf=N_HF)
train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True,
                          collate_fn=collate, num_workers=4, pin_memory=True)
val_loader   = DataLoader(val_ds,   batch_size=BATCH_SIZE, shuffle=False,
                          collate_fn=collate, num_workers=4, pin_memory=True)

# ── Model ─────────────────────────────────────────────────────────────────────
model = MFTransolver(
    cond_dim       = COND_DIM,
    hidden_dim     = args.hidden_dim,
    n_slices       = args.n_slices,
    num_heads      = args.num_heads,
    encoder_layers = args.encoder_layers,
    residual_layers= args.residual_layers,
    pos_enc_freqs  = args.pos_enc_freqs,
).to(device)

trainable_p, total_p = param_count(model)
print(f"MFTransolver parameters: {total_p:,} total  ({trainable_p:,} trainable)")

opt       = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=1e-5)
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
    print(f"[Resume] Resuming from epoch {start_epoch} (best_val={best_val:.4e})\n")
else:
    print("[Resume] Starting from scratch.")

# ── Save config ─────────────────────────────────────────────────────────────
cfg = dict(
    model_type="MFTransolver",
    csv=CSV, vtk_dir=VTK_DIR, npz_dir=NPZ_DIR,
    epochs=EPOCHS, batch_size=BATCH_SIZE, lr=LR,
    train_ratio=TRAIN_RATIO, val_ratio=VAL_RATIO, test_ratio=TEST_RATIO,
    n_lf=N_LF, n_hf=N_HF, max_pts_hf=str(MAX_PTS_HF),
    device=str(device), amp=use_amp,
    train_frac=TRAIN_FRAC, run_name=args.run_name,
    model=dict(
        cond_dim=COND_DIM, hidden_dim=args.hidden_dim,
        n_slices=args.n_slices, num_heads=args.num_heads,
        encoder_layers=args.encoder_layers, residual_layers=args.residual_layers,
        pos_enc_freqs=args.pos_enc_freqs,
    ),
    total_params=total_p, trainable_params=trainable_p,
)
json.dump(cfg, open(CFG_PATH, "w"), indent=2)

# ── Loss ──────────────────────────────────────────────────────────────────────
def hybrid_loss(pred: torch.Tensor, targets: torch.Tensor):
    """MSE + mean relative-L2 per design."""
    diff    = pred - targets                               # (B, N, 1)
    mse     = torch.mean(diff ** 2)
    diff_sq = torch.sum(diff ** 2,    dim=1)              # (B, 1)
    true_sq = torch.sum(targets ** 2, dim=1)              # (B, 1)
    rel_l2  = (torch.sqrt(diff_sq)
               / torch.clamp(torch.sqrt(true_sq), min=1e-4))
    return mse + torch.mean(rel_l2), mse

# ── Training loop ─────────────────────────────────────────────────────────────
t0 = time.time()
print(f"\n[MFTransolver] Training {args.run_name}  "
      f"epochs {start_epoch}→{EPOCHS}  "
      f"({len(train_ds)} HF designs, frac={TRAIN_FRAC:.3f})\n")

for epoch in range(start_epoch, EPOCHS + 1):
    # ── train ──
    model.train()
    running, count = 0.0, 0
    for lf_tok, hf_tok, targets, _ in train_loader:
        lf_tok  = lf_tok.to(device)
        hf_tok  = hf_tok.to(device)
        targets = targets.to(device)

        opt.zero_grad(set_to_none=True)
        with torch.amp.autocast("cuda", enabled=use_amp):
            pred          = model(lf_tok, hf_tok)
            loss, mse_t   = hybrid_loss(pred, targets)

        scaler.scale(loss).backward()
        scaler.unscale_(opt)
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        scaler.step(opt)
        scaler.update()

        mse_v = mse_t.item()
        if mse_v == mse_v:   # not NaN
            running += mse_v * lf_tok.size(0)
            count   += lf_tok.size(0)

    train_mse = running / max(count, 1)
    scheduler.step()

    # ── validate ──
    model.eval()
    vr, vc = 0.0, 0
    with torch.no_grad(), torch.amp.autocast("cuda", enabled=use_amp):
        for lf_tok, hf_tok, targets, _ in val_loader:
            lf_tok  = lf_tok.to(device)
            hf_tok  = hf_tok.to(device)
            targets = targets.to(device)
            _, vm   = hybrid_loss(model(lf_tok, hf_tok), targets)
            vr += vm.item() * lf_tok.size(0)
            vc += lf_tok.size(0)

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
            'epoch':      range(1, epoch + 1),
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

# ── Final saves ────────────────────────────────────────────────────────────────
torch.save(model.state_dict(), FINAL_PATH)
if RESUME_PATH.exists():
    RESUME_PATH.unlink()
    print("[Resume] Training complete — resume_state.pth removed.")

pd.DataFrame({
    'epoch':      range(1, len(train_losses) + 1),
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
plt.title(f'MFTransolver stacking_v3 — {args.run_name}')
plt.grid(True, which="both", ls="--", alpha=0.5)
plt.legend()
plt.tight_layout()
plt.savefig(LOSS_PLOT_PATH)
plt.close()

dt = time.time() - t0
print(f"\nDone in {dt/60:.1f} min  ({len(train_losses)} epochs)")
print(f"Best val MSE   : {best_val:.4e}")
print(f"Best weights   : {BEST_PATH}")
print(f"Final weights  : {FINAL_PATH}")
print(f"Run name       : {args.run_name}")
