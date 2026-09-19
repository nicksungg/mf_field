"""WP1 FiLM-FNO arms with FIXED optimizer steps (not epochs), on top of the family's own script (imported, not copied).
  --lf_steps 0            -> R0: fine-only from random init
  --lf_steps S (>0)       -> R1: pretrain on the coarse pool at --lf_level (default: top coarse level), then fine-tune on HF
Epochs are derived per split so every budget sees the same number of optimizer steps (batch 16)."""
import argparse, inspect, math, sys, time
from pathlib import Path
import numpy as np, torch
import os
FAMILY = Path(os.environ.get("MF_ROOT", "/archive/mf_field")) / "factory_mffp/models/mf_fno_transfer_film"
ap = argparse.ArgumentParser()
ap.add_argument("--dataset_dir", required=True); ap.add_argument("--dataset_name", required=True); ap.add_argument("--out", required=True); ap.add_argument("--ckpt_dir", required=True)
ap.add_argument("--seed", type=int, default=42); ap.add_argument("--lf_steps", type=int, default=30000); ap.add_argument("--hf_steps", type=int, default=30000)
ap.add_argument("--lf_level", type=int, default=0, help="1-based coarse level to pretrain on; 0 = top coarse level"); ap.add_argument("--family", default=str(FAMILY))
a = ap.parse_args(); fam = Path(a.family); sys.path.insert(0, str(fam)); sys.path.insert(0, str(fam.parent.parent))
import smoke_eval as se
torch.manual_seed(a.seed); np.random.seed(a.seed); device = torch.device("cuda" if torch.cuda.is_available() else "cpu"); p = se.SMOKE
train = se.load_mf_dataset(Path(a.dataset_dir), "train"); test = se.load_mf_dataset(Path(a.dataset_dir), "test"); hf = train["hf_fid"]
lfs = sorted(train["lf_fids"]); lf = (lfs[a.lf_level - 1] if a.lf_level > 0 else lfs[-1]) if lfs else hf
hf_nat = se.resolve_grid(a.dataset_name, int(train["n_cells_by_fid"][hf])); lf_nat = se.resolve_grid(a.dataset_name, int(train["n_cells_by_fid"][lf]))
grid = se._cap_grid(hf_nat); mh, mw = se._modes(grid, p["modes_cap"])
to_grid = (lambda y, s, d: se._to_grid(y, s, d, a.dataset_name)) if len(inspect.signature(se._to_grid).parameters) == 4 else se._to_grid
X_hf = train["cond_by_fid"][hf].astype(np.float32); Y_hf = to_grid(train["field_by_fid"][hf], hf_nat, grid)
X_te = test["cond_by_fid"][hf].astype(np.float32); Y_te = to_grid(test["field_by_fid"][hf], hf_nat, grid)
use_lf = a.lf_steps > 0
if use_lf:
    X_lf = train["cond_by_fid"][lf].astype(np.float32); Y_lf = to_grid(train["field_by_fid"][lf], lf_nat, grid)
def epochs_for(steps, n): return max(1, math.ceil(steps / max(1, math.ceil(n / p["batch_size"]))))
scaler_hf = max(float(np.abs(Y_hf).max()), 1e-8)
print(f"[data] {a.dataset_name} HF={hf} N_hf={len(X_hf)} grid={grid} | {'LF='+str(lf)+' N_lf='+str(len(X_lf)) if use_lf else 'fine-only'} | steps lf={a.lf_steps if use_lf else 0} hf={a.hf_steps}", flush=True)
model = se.FNO2d(int(X_hf.shape[1]), hidden_channels=p["hidden_channels"], n_blocks=p["n_blocks"], modes_h=mh, modes_w=mw, grid=grid).to(device)
t0 = time.time()
if use_lf:
    scaler_lf = max(float(np.abs(Y_lf).max()), 1e-8); e_lf = epochs_for(a.lf_steps, len(X_lf))
    print(f"[stage] LF pretrain {len(X_lf)} rows x {e_lf} epochs (~{a.lf_steps} steps) lr {p['lr_pretrain']}", flush=True)
    se._train(model, X_lf, Y_lf, scaler_lf, e_lf, p["lr_pretrain"], p, device, "LF-pretrain")
e_hf = epochs_for(a.hf_steps, len(X_hf)); lr_hf = p["lr_finetune"] if use_lf else p["lr_pretrain"]
print(f"[stage] HF {'fine-tune' if use_lf else 'from scratch'} {len(X_hf)} rows x {e_hf} epochs (~{a.hf_steps} steps) lr {lr_hf}", flush=True)
se._train(model, X_hf, Y_hf, scaler_hf, e_hf, lr_hf, p, device, "HF")
train_seconds = time.time() - t0
model.eval(); preds = []
with torch.no_grad():
    for i in range(0, len(X_te), p["batch_size"]):
        pr = model(torch.from_numpy(X_te[i:i + p["batch_size"]]).float().to(device)) * scaler_hf; preds.append(pr.reshape(pr.shape[0], -1).cpu().numpy())
pred = np.concatenate(preds).astype(np.float64); target = Y_te.reshape(len(Y_te), -1).astype(np.float64)
out = Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
se.finalize_and_write(out_path=out, model=("film_r1" if use_lf else "film_r0"), dataset=a.dataset_name, pred=pred, target=target, work_grid=grid, n_params=int(se.param_count(model)),
                      train_seconds=train_seconds, eval_seconds=0.0, latency_ms_per_sample=None, peak_mem_mb=(torch.cuda.max_memory_allocated() / 1e6) if device.type == "cuda" else None, seed=a.seed,
                      extra=dict(regime="R1" if use_lf else "R0", n_hf_train=int(len(X_hf)), n_lf_train=int(len(X_lf)) if use_lf else 0, lf_fidelity=int(lf) if use_lf else None,
                                 lf_steps=a.lf_steps if use_lf else 0, hf_steps=a.hf_steps, lf_epochs=e_lf if use_lf else 0, hf_epochs=e_hf, hf_grid_native=list(hf_nat), work_grid=list(grid)))
print(f"[wrote] {out}", flush=True)
