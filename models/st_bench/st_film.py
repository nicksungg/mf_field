"""FiLM-FNO controls and the transfer anchor on the family's own script (imported, not copied), leaderboard epoch semantics.

  --mode hf_only  : st_film_hf_only  fine rows only, from random init, lr_pretrain, --epochs (2500 = leaderboard HF budget)
  --mode lf_only  : st_film_lf_only  top coarse level only, --epochs, evaluated against the fine target on the working grid
                    + st_film_affine  rho * pred_lf(theta) + b with (rho, b) least squares on the fine training rows (written too)
  --mode pooled   : st_film_pooled   fidelity-blind: every level's rows resampled to the working grid and mixed, one stage, same optimizer STEPS as hf_only
  --mode transfer : st_film_transfer the family's schedule (pretrain on the coarsest level, fine-tune on fine), --epochs per stage
Result JSON = the family's finalize_and_write (splits.test_hf.rel_l2_mean etc.) + track/inputs fields.  No checkpoints (fresh run).
"""
from __future__ import annotations
import argparse, inspect, os, sys, time
from pathlib import Path
import numpy as np, torch
FAMILY = Path(os.environ.get("FILM_FAMILY", "/archive/mf_field/factory_mffp/models/mf_fno_transfer_film"))
ap = argparse.ArgumentParser()
ap.add_argument("--dataset_dir", required=True); ap.add_argument("--dataset_name", required=True); ap.add_argument("--out_dir", required=True)
ap.add_argument("--mode", required=True, choices=["hf_only", "lf_only", "pooled", "transfer"]); ap.add_argument("--epochs", type=int, default=2500)
ap.add_argument("--seed", type=int, default=42); ap.add_argument("--lf_level", type=int, default=0, help="1-based coarse level for lf_only; 0 = top coarse level")
ap.add_argument("--family", default=str(FAMILY)); ap.add_argument("--tag", default="st", help="result files are <arm>__<name>__e<tag>__s<seed>.json")
a = ap.parse_args(); fam = Path(a.family); sys.path.insert(0, str(fam)); sys.path.insert(0, str(fam.parent.parent))
import smoke_eval as se
torch.manual_seed(a.seed); np.random.seed(a.seed); device = torch.device("cuda" if torch.cuda.is_available() else "cpu"); p = se.SMOKE
train = se.load_mf_dataset(Path(a.dataset_dir), "train"); test = se.load_mf_dataset(Path(a.dataset_dir), "test"); hf = train["hf_fid"]
if hf not in test["fids"]:
    hf = test["hf_fid"]
lfs = sorted(f for f in train["lf_fids"] if f != hf)
hf_nat = se.resolve_grid(a.dataset_name, int(train["n_cells_by_fid"][hf])); grid = se._cap_grid(hf_nat); mh, mw = se._modes(grid, p["modes_cap"])
to_grid = (lambda y, s, d: se._to_grid(y, s, d, a.dataset_name)) if len(inspect.signature(se._to_grid).parameters) == 4 else se._to_grid
def level(f):
    g = se.resolve_grid(a.dataset_name, int(train["n_cells_by_fid"][f]))
    return train["cond_by_fid"][f].astype(np.float32), to_grid(train["field_by_fid"][f], g, grid), g
X_hf, Y_hf, _ = level(hf); X_te = test["cond_by_fid"][hf].astype(np.float32); Y_te = to_grid(test["field_by_fid"][hf], hf_nat, grid)
scaler_hf = max(float(np.abs(Y_hf).max()), 1e-8); cond_dim = int(X_hf.shape[1])
model = se.FNO2d(cond_dim, hidden_channels=p["hidden_channels"], n_blocks=p["n_blocks"], modes_h=mh, modes_w=mw, grid=grid).to(device)
n_params = int(se.param_count(model))
def predict(X, scaler):
    model.eval(); out = []
    with torch.no_grad():
        for i in range(0, len(X), p["batch_size"]):
            pr = model(torch.from_numpy(X[i:i + p["batch_size"]]).float().to(device)) * scaler; out.append(pr.reshape(pr.shape[0], -1).cpu().numpy())
    model.train(); return np.concatenate(out).astype(np.float64)
def write(arm, pred, train_seconds, extra):
    out = Path(a.out_dir) / f"{arm}__{a.dataset_name}__e{a.tag}__s{a.seed}.json"; out.parent.mkdir(parents=True, exist_ok=True)
    res = se.finalize_and_write(out_path=out, model=arm, dataset=a.dataset_name, pred=pred, target=Y_te.reshape(len(Y_te), -1).astype(np.float64), work_grid=grid,
                                n_params=n_params, train_seconds=train_seconds, eval_seconds=0.0, latency_ms_per_sample=None,
                                peak_mem_mb=(torch.cuda.max_memory_allocated() / 1e6) if device.type == "cuda" else None, seed=a.seed,
                                extra=dict(track="surrogate", inputs_at_inference=["theta"], conditioning="film_on_X_per_block", epochs=a.epochs,
                                           n_hf_train=int(len(X_hf)), n_test=int(len(X_te)), hf_grid_native=list(hf_nat), work_grid=list(grid), family_script=str(fam / "smoke_eval.py"), **extra))
    print(f"[wrote] {out}  rel_l2_mean={res['splits']['test_hf']['rel_l2_mean']:.5g}", flush=True)
t0 = time.time()
if a.mode == "hf_only":
    print(f"[data] {a.dataset_name} fine-only N_hf={len(X_hf)} grid={grid} epochs={a.epochs}", flush=True)
    se._train(model, X_hf, Y_hf, scaler_hf, a.epochs, p["lr_pretrain"], p, device, "HF-only")
    write("st_film_hf_only", predict(X_te, scaler_hf), time.time() - t0, dict(mf_mechanism="none_hf_only", lr=p["lr_pretrain"]))
elif a.mode == "lf_only":
    lf = lfs[a.lf_level - 1] if a.lf_level > 0 else lfs[-1]; X_lf, Y_lf, g_lf = level(lf); scaler_lf = max(float(np.abs(Y_lf).max()), 1e-8)
    print(f"[data] {a.dataset_name} coarse-only LF={lf} native={g_lf} N_lf={len(X_lf)} grid={grid} epochs={a.epochs}", flush=True)
    se._train(model, X_lf, Y_lf, scaler_lf, a.epochs, p["lr_pretrain"], p, device, "LF-only"); tt = time.time() - t0
    pred_te = predict(X_te, scaler_lf); pred_tr = predict(X_hf, scaler_lf)
    write("st_film_lf_only", pred_te, tt, dict(mf_mechanism="coarse_only_no_fine_labels", lf_fidelity=int(lf), lf_grid_native=list(g_lf), n_lf_train=int(len(X_lf)), lr=p["lr_pretrain"]))
    A = np.stack((pred_tr.ravel(), np.ones(pred_tr.size)), 1); sol, *_ = np.linalg.lstsq(A, Y_hf.reshape(-1).astype(np.float64), rcond=None); rho, b = float(sol[0]), float(sol[1])
    write("st_film_affine", rho * pred_te + b, tt, dict(mf_mechanism="affine_correction_of_coarse_surrogate", rho=rho, b=b, lf_fidelity=int(lf), n_lf_train=int(len(X_lf)), n_fine_rows_for_fit=int(len(X_hf))))
elif a.mode == "pooled":
    Xs, Ys, ns = [X_hf], [Y_hf], {int(hf): int(len(X_hf))}
    for f in lfs:
        Xf, Yf, _ = level(f); Xs.append(Xf); Ys.append(Yf); ns[int(f)] = int(len(Xf))
    Xp, Yp = np.concatenate(Xs), np.concatenate(Ys); scaler = max(float(np.abs(Yp).max()), 1e-8)
    e_pool = max(1, int(round(a.epochs * len(X_hf) / len(Xp))))          # same optimizer steps as the fine-only arm
    print(f"[data] {a.dataset_name} pooled rows per level {ns} total={len(Xp)} grid={grid} epochs={e_pool} (= {a.epochs} fine-only epochs in steps)", flush=True)
    se._train(model, Xp, Yp, scaler, e_pool, p["lr_pretrain"], p, device, "pooled")
    write("st_film_pooled", predict(X_te, scaler), time.time() - t0, dict(mf_mechanism="fidelity_blind_pooling", rows_per_level=ns, pooled_epochs=e_pool, lr=p["lr_pretrain"]))
else:
    lf = min(lfs); X_lf, Y_lf, g_lf = level(lf); scaler_lf = max(float(np.abs(Y_lf).max()), 1e-8)
    print(f"[data] {a.dataset_name} transfer LF={lf} (coarsest, family default) N_lf={len(X_lf)} N_hf={len(X_hf)} grid={grid} epochs={a.epochs}/stage", flush=True)
    se._train(model, X_lf, Y_lf, scaler_lf, a.epochs, p["lr_pretrain"], p, device, "LF-pretrain")
    se._train(model, X_hf, Y_hf, scaler_hf, a.epochs, p["lr_finetune"], p, device, "HF-finetune")
    write("st_film_transfer", predict(X_te, scaler_hf), time.time() - t0, dict(mf_mechanism="transfer_learning_pretrain_LF_finetune_HF", lf_fidelity=int(lf), n_lf_train=int(len(X_lf)), lr_pretrain=p["lr_pretrain"], lr_finetune=p["lr_finetune"]))
