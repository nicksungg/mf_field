"""Continuous-fidelity MF-FNO + learned Richardson extrapolation — smoke eval.

Flow:
  working grid = _cap_grid(resolve_grid(name, n_cells[hf]))  (256-cap)
  For EVERY fidelity: resample its field to the working grid (_to_grid), append
  the normalized fidelity scalar f to its condition vector, and POOL all of them
  into one training set (cond_dim = d + 1). One scaler (GLOBAL: max|Y| over the
  pooled fields) is used for train AND de-normalized eval, so the reported number
  and the super-fidelity number share the same units.
  f = (log(fid) - log(min_fid)) / (log(max_fid) - log(min_fid)) in [0, 1];
  hf -> f = 1.0, smallest LF -> f = 0.0.

  Train ONCE on the pooled set. Then:
   - HEADLINE: query the HF test conditions at f = 1.0 -> HF prediction (the
     comparable nRMSE reported in splits).
   - SUPER-FIDELITY: query the HF test conditions at several f, fit a per-pixel
     linear Richardson trend in f, extrapolate to f = f_super (> 1) toward the
     infinite-fidelity limit; its nRMSE-vs-HF is reported in extra
     (superfidelity_nRMSE).

Resume: ckpt_dir/last.pt keyed on (epochs_target, grid).
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import torch

AKASH = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(AKASH))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from common.backbone import param_count  # noqa: E402
from common.mffp import (  # noqa: E402
    load_mf_dataset, resolve_grid, finalize_and_write, SMOKE,
    _cap_grid, _modes, _to_grid, train_loop,
)
from model import FNO2dContinuousFidelity, richardson_extrapolate  # noqa: E402

# super-fidelity: f values to query for the per-pixel trend fit, and the
# extrapolation target (> 1.0, projecting past HF toward the limit).
F_TREND = np.array([0.6, 0.8, 1.0], dtype=np.float64)
F_SUPER = 1.25


def _norm_fid(fid, fmin, fmax):
    lo, hi = np.log(fmin), np.log(fmax)
    if hi <= lo:
        return 1.0
    return float((np.log(fid) - lo) / (hi - lo))


def _nrmse(pred, target):
    num = np.linalg.norm(pred - target, axis=1)
    den = np.linalg.norm(target, axis=1) + 1e-12
    return float(np.mean(num / den))


def run(args, out_path: Path) -> dict:
    torch.manual_seed(args.seed); np.random.seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    p = SMOKE
    ds_dir = Path(args.dataset_dir)

    train = load_mf_dataset(ds_dir, "train")
    test = load_mf_dataset(ds_dir, "test")
    hf = train["hf_fid"]
    if hf not in test["fids"]:
        hf = test["hf_fid"]
    fids = sorted(train["fids"])
    fmin, fmax = float(min(fids)), float(max(fids))

    hf_grid_native = resolve_grid(args.dataset_name, int(train["n_cells_by_fid"][hf]))
    grid = _cap_grid(hf_grid_native)
    modes_h, modes_w = _modes(grid, p["modes_cap"])

    # ── pool ALL fidelities onto the working grid, append f to the condition ──
    Xs, Ys = [], []
    f_by_fid = {}
    for fid in fids:
        Xf = train["cond_by_fid"][fid].astype(np.float32)
        gf = resolve_grid(args.dataset_name, int(train["n_cells_by_fid"][fid]))
        Yf = _to_grid(train["field_by_fid"][fid], gf, grid)
        f = _norm_fid(fid, fmin, fmax)
        f_by_fid[fid] = f
        fcol = np.full((Xf.shape[0], 1), f, dtype=np.float32)
        Xs.append(np.concatenate([Xf, fcol], axis=1))
        Ys.append(Yf)
    X_pool = np.concatenate(Xs, axis=0)
    Y_pool = np.concatenate(Ys, axis=0)
    cond_dim = int(X_pool.shape[1])               # d + 1

    # GLOBAL scaler over the pooled fields (documented: same scaler for eval).
    scaler = max(float(np.abs(Y_pool).max()), 1e-8) if Y_pool.size else 1.0
    hf_norm = _norm_fid(hf, fmin, fmax)           # == 1.0

    # HF test (target in raw units; cond WITHOUT f — f is appended at query time).
    X_te = test["cond_by_fid"][hf].astype(np.float32)
    Y_te = _to_grid(test["field_by_fid"][hf], hf_grid_native, grid)

    print(f"[data] {args.dataset_name} loader={train['loader']} fids={fids} HF={hf} "
          f"hf_native={hf_grid_native} work_grid={grid} modes=({modes_h},{modes_w}) "
          f"f_by_fid={ {k: round(v,3) for k,v in f_by_fid.items()} } hf_norm={hf_norm} "
          f"N_pool={X_pool.shape[0]} N_test={X_te.shape[0]} cond_dim={cond_dim}", flush=True)

    model = FNO2dContinuousFidelity(cond_dim, hidden_channels=p["hidden_channels"],
                                    n_blocks=p["n_blocks"], modes_h=modes_h, modes_w=modes_w,
                                    grid=grid).to(device)
    n_params = param_count(model)

    ckpt_dir = Path(args.ckpt_dir); ckpt_dir.mkdir(parents=True, exist_ok=True)
    last = ckpt_dir / "last.pt"
    trained = False
    if last.exists():
        try:
            sd = torch.load(last, map_location=device, weights_only=False)
            if sd.get("epochs_target") == args.epochs and sd.get("grid") == list(grid):
                model.load_state_dict(sd["model"]); trained = True
                print("[resume] loaded finished checkpoint", flush=True)
        except Exception as e:
            print(f"[resume] failed ({e}); fresh", flush=True)

    t_train = time.time()
    if not trained:
        # single pooled training pass across ALL fidelities at once.
        print(f"[stage] pooled train across fidelities ({X_pool.shape[0]} samples)", flush=True)
        train_loop(model, X_pool, Y_pool, scaler, args.epochs, p["lr_pretrain"], p, device, "pooled")
        torch.save({"epochs_target": args.epochs, "grid": list(grid),
                    "model": model.state_dict()}, last)
    train_seconds = time.time() - t_train

    # ── helper: predict the HF test conditions at a given fidelity coord f ──
    def predict_at(f_val: float) -> np.ndarray:
        fcol = np.full((X_te.shape[0], 1), f_val, dtype=np.float32)
        Xq = np.concatenate([X_te, fcol], axis=1)
        out = []
        bs = p["batch_size"]
        with torch.no_grad():
            for i in range(0, Xq.shape[0], bs):
                xb = torch.from_numpy(Xq[i:i + bs]).float().to(device)
                pr = model(xb) * scaler
                out.append(pr.reshape(pr.shape[0], -1).cpu().numpy())
        return np.concatenate(out, 0).astype(np.float64)

    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize()
    t_eval = time.time()
    model.eval()
    # HEADLINE: query at f = hf_norm (= 1.0)
    pred = predict_at(hf_norm)
    if device.type == "cuda":
        torch.cuda.synchronize()
    eval_seconds = time.time() - t_eval

    target = Y_te.reshape(Y_te.shape[0], -1).astype(np.float64)
    n_samples = int(target.shape[0])

    # SUPER-FIDELITY: per-pixel Richardson extrapolation in f.
    preds_trend = np.stack([predict_at(float(f)) for f in F_TREND], axis=0)  # (K, N, P)
    pred_super = richardson_extrapolate(F_TREND, preds_trend, F_SUPER)        # (N, P)
    superfidelity_nRMSE = _nrmse(pred_super, target)
    headline_nRMSE = _nrmse(pred, target)
    print(f"[eval] headline nRMSE(f=1.0)={headline_nRMSE:.4e} "
          f"superfidelity nRMSE(f={F_SUPER})={superfidelity_nRMSE:.4e}", flush=True)

    latency = (1000.0 * eval_seconds / max(n_samples, 1)) if device.type == "cuda" else None
    peak_mem = (torch.cuda.max_memory_allocated() / 1e6) if device.type == "cuda" else None

    return finalize_and_write(
        out_path=out_path, model="mf_fno_richardson", dataset=args.dataset_name,
        pred=pred, target=target, work_grid=grid, n_params=int(n_params),
        train_seconds=train_seconds, eval_seconds=eval_seconds,
        latency_ms_per_sample=latency, peak_mem_mb=peak_mem, seed=args.seed,
        extra={"device": str(device), "hf_fidelity": int(hf),
               "mf_mechanism": "continuous_fidelity_film_on_X_f_pooled_train",
               "conditioning": "film_on_[X,f]_per_block",
               "scaler_kind": "global_max_abs_over_pooled_fields",
               "fids": [int(x) for x in fids], "f_by_fid": {int(k): float(v) for k, v in f_by_fid.items()},
               "hf_norm": float(hf_norm), "f_trend": [float(x) for x in F_TREND],
               "f_super": float(F_SUPER),
               "superfidelity_nRMSE": float(superfidelity_nRMSE),
               "headline_nRMSE": float(headline_nRMSE),
               "hf_grid_native": list(hf_grid_native), "work_grid": list(grid)},
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset_dir", required=True)
    ap.add_argument("--dataset_name", required=True)
    ap.add_argument("--epochs", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ckpt_dir", required=True)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    run(args, out)
    print(f"[wrote] {out}", flush=True)


if __name__ == "__main__":
    main()
