"""Smoke + fair-eval for mf_fno_cvblend (B7).

Control-variate inference blend. We train TWO FiLM FNOs:
  * an HF model  g_hf(X)  fine-tuned from an LF pretrain (the winner's pipeline),
  * an LF model  g_lf(X)  trained on LF only (the cheap correlated estimator).
At inference we blend per pixel:
      p = p_hf - beta * (p_lf - E[p_lf])
where p_hf = g_hf(X), p_lf = g_lf(X) evaluated on the SAME HF working grid, and
E[p_lf] is the mean LF prediction over the HF train set. Because g_lf is
correlated with g_hf's error, subtracting the (mean-centered) LF control variate
with an optimal scalar beta reduces variance (classic Monte-Carlo control
variates). beta* is fit on the HF TRAIN set in closed form:
      beta* = Cov(p_hf - y, p_lf) / Var(p_lf)
(the beta minimizing residual variance of the blended estimator vs the HF
target). `extra` reports beta and a simple UQ proxy (std of the control term).

Contract: --dataset_dir --dataset_name --epochs --out --ckpt_dir --seed.
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

from common.mffp import (load_mf_dataset, resolve_grid, finalize_and_write,  # noqa: E402
                         SMOKE, _cap_grid, _modes, _to_grid, train_loop)
from model import FNO2d, param_count  # noqa: E402


def _predict(model, X, scaler, device, bs):
    model.eval()
    preds = []
    with torch.no_grad():
        for i in range(0, X.shape[0], bs):
            xb = torch.from_numpy(X[i:i + bs]).float().to(device)
            pr = model(xb) * scaler
            preds.append(pr.reshape(pr.shape[0], -1).cpu().numpy())
    return np.concatenate(preds, 0).astype(np.float64) if preds else np.zeros((0, 1))


def run(args, out_path: Path) -> dict:
    torch.manual_seed(args.seed); np.random.seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    p = SMOKE
    ds_dir = Path(args.dataset_dir)

    train = load_mf_dataset(ds_dir, "train")
    test = load_mf_dataset(ds_dir, "test")
    hf = train["hf_fid"]
    lf = min(train["lf_fids"]) if train["lf_fids"] else hf
    if hf not in test["fids"]:
        hf = test["hf_fid"]

    hf_grid_native = resolve_grid(args.dataset_name, int(train["n_cells_by_fid"][hf]))
    lf_grid_native = resolve_grid(args.dataset_name, int(train["n_cells_by_fid"][lf]))
    grid = _cap_grid(hf_grid_native)
    modes_h, modes_w = _modes(grid, p["modes_cap"])

    X_lf = train["cond_by_fid"][lf].astype(np.float32)
    Y_lf = _to_grid(train["field_by_fid"][lf], lf_grid_native, grid)
    X_hf = train["cond_by_fid"][hf].astype(np.float32)
    Y_hf = _to_grid(train["field_by_fid"][hf], hf_grid_native, grid)
    X_te = test["cond_by_fid"][hf].astype(np.float32)
    Y_te = _to_grid(test["field_by_fid"][hf], hf_grid_native, grid)

    cond_dim = int(X_hf.shape[1])
    scaler_lf = max(float(np.abs(Y_lf).max()), 1e-8) if Y_lf.size else 1.0
    scaler_hf = max(float(np.abs(Y_hf).max()), 1e-8) if Y_hf.size else 1.0

    print(f"[data] {args.dataset_name} loader={train['loader']} LF={lf} HF={hf} "
          f"hf_native={hf_grid_native} work_grid={grid} modes=({modes_h},{modes_w}) "
          f"N_lf={X_lf.shape[0]} N_hf={X_hf.shape[0]} N_test={X_te.shape[0]} cond_dim={cond_dim}",
          flush=True)

    def mk():
        return FNO2d(cond_dim, hidden_channels=p["hidden_channels"], n_blocks=p["n_blocks"],
                     modes_h=modes_h, modes_w=modes_w, grid=grid).to(device)
    model_hf = mk(); model_lf = mk()
    n_params = param_count(model_hf) + param_count(model_lf)

    ckpt_dir = Path(args.ckpt_dir); ckpt_dir.mkdir(parents=True, exist_ok=True)
    last = ckpt_dir / "last.pt"
    trained = False; beta = None
    if last.exists():
        try:
            sd = torch.load(last, map_location=device, weights_only=False)
            if sd.get("epochs_target") == args.epochs and sd.get("grid") == list(grid):
                model_hf.load_state_dict(sd["model_hf"]); model_lf.load_state_dict(sd["model_lf"])
                beta = sd.get("beta"); trained = True
                print("[resume] loaded finished checkpoint", flush=True)
        except Exception as e:
            print(f"[resume] failed ({e}); fresh", flush=True)

    t_train = time.time()
    if not trained:
        # HF model: LF pretrain -> HF finetune (winner's pipeline)
        print(f"[stage] HF-model: pretrain LF ({X_lf.shape[0]})", flush=True)
        train_loop(model_hf, X_lf, Y_lf, scaler_lf, args.epochs, p["lr_pretrain"], p, device, "HFmdl-LF")
        print(f"[stage] HF-model: finetune HF ({X_hf.shape[0]})", flush=True)
        train_loop(model_hf, X_hf, Y_hf, scaler_hf, args.epochs, p["lr_finetune"], p, device, "HFmdl-HF")
        # LF model: LF only (the cheap correlated control variate)
        print(f"[stage] LF-model: train LF ({X_lf.shape[0]})", flush=True)
        train_loop(model_lf, X_lf, Y_lf, scaler_lf, args.epochs, p["lr_pretrain"], p, device, "LFmdl")

        # fit beta* on HF train: beta = Cov(p_hf - y, p_lf) / Var(p_lf), pooled over pixels
        p_hf_tr = _predict(model_hf, X_hf, scaler_hf, device, p["batch_size"])
        p_lf_tr = _predict(model_lf, X_hf, scaler_lf, device, p["batch_size"])  # LF model on HF inputs
        y_tr = Y_hf.reshape(Y_hf.shape[0], -1).astype(np.float64)
        lf_mean = p_lf_tr.mean(axis=0, keepdims=True)              # E[p_lf] per pixel
        cv = p_lf_tr - lf_mean                                     # mean-centered control
        err = p_hf_tr - y_tr
        var_cv = float((cv ** 2).sum())
        beta = float((err * cv).sum() / max(var_cv, 1e-12))
        print(f"[beta] control-variate beta*={beta:.4f}", flush=True)
        torch.save({"epochs_target": args.epochs, "grid": list(grid), "beta": beta,
                    "lf_mean": lf_mean, "model_hf": model_hf.state_dict(),
                    "model_lf": model_lf.state_dict()}, last)
    else:
        sd = torch.load(last, map_location=device, weights_only=False)
        lf_mean = sd["lf_mean"]
    train_seconds = time.time() - t_train

    # ── eval: blended prediction ──
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize()
    t_eval = time.time()
    p_hf_te = _predict(model_hf, X_te, scaler_hf, device, p["batch_size"])
    p_lf_te = _predict(model_lf, X_te, scaler_lf, device, p["batch_size"])
    cv_te = p_lf_te - lf_mean                                      # use TRAIN E[p_lf]
    pred = p_hf_te - beta * cv_te
    if device.type == "cuda":
        torch.cuda.synchronize()
    eval_seconds = time.time() - t_eval
    target = Y_te.reshape(Y_te.shape[0], -1).astype(np.float64)

    # UQ proxy + ablation: nRMSE of the HF model alone vs the blend
    def agg(pr):
        return float(np.sqrt(((pr - target) ** 2).sum() / max((target ** 2).sum(), 1e-12)))
    nrmse_hf_only = agg(p_hf_te)
    nrmse_blend = agg(pred)
    control_term_std = float(np.std(beta * cv_te))
    print(f"[cv] nRMSE hf_only={nrmse_hf_only:.6f} blend={nrmse_blend:.6f} "
          f"control_term_std={control_term_std:.4e}", flush=True)

    n_samples = int(target.shape[0])
    latency = (1000.0 * eval_seconds / max(n_samples, 1)) if device.type == "cuda" else None
    peak_mem = (torch.cuda.max_memory_allocated() / 1e6) if device.type == "cuda" else None

    return finalize_and_write(
        out_path=out_path, model="mf_fno_cvblend", dataset=args.dataset_name,
        pred=pred, target=target, work_grid=grid, n_params=int(n_params),
        train_seconds=train_seconds, eval_seconds=eval_seconds,
        latency_ms_per_sample=latency, peak_mem_mb=peak_mem, seed=args.seed,
        extra={"device": str(device), "hf_fidelity": int(hf), "lf_fidelity": int(lf),
               "mf_mechanism": "control_variate_inference_blend_of_LF_and_HF_FNOs",
               "conditioning": "film_on_X_per_block",
               "blend": "p = p_hf - beta*(p_lf - E[p_lf])",
               "cv_beta": float(beta), "control_term_std": control_term_std,
               "nRMSE_hf_only": nrmse_hf_only, "nRMSE_blend": nrmse_blend,
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
    res = run(args, out)
    print(f"[wrote] {out}", flush=True)
    print(f"[nRMSE] {res['splits']['test_hf']['nRMSE']:.6f}", flush=True)


if __name__ == "__main__":
    main()
