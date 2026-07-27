"""mf_fno_ptr — FiLM-transfer winner + test-time PDE-residual refinement (PTR).

Training is byte-for-byte the winner `mf_fno_transfer_film` (LF-pretrain ->
HF-finetune over an FiLM-conditioned FNO on the 256-cap working grid). At eval
time, each de-normalized predicted field is refined by K gradient steps on the
FIELD tensor (NITO-style; see refine.py). The residual is per-dataset via a
registry; missing entries => NO-OP refinement => family == winner.

`extra` reports nRMSE_pre_refine (network output) and the headline post-refine
nRMSE; finalize_and_write's nRMSE/rel_l2 are computed from the POST-refine pred.

Contract: --dataset_dir --dataset_name --epochs --out --ckpt_dir --seed
          (+ --refine_steps --w_res --w_anchor --refine_lr).
--epochs is the HF fine-tune budget; LF pretrain uses the same (capped) budget.
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
from model import FNO2d  # noqa: E402
from refine import refine_field, get_residual_fn  # noqa: E402


def _nrmse_agg(pred, target):
    p = np.asarray(pred, np.float64).reshape(pred.shape[0], -1)
    t = np.asarray(target, np.float64).reshape(target.shape[0], -1)
    return float(np.sqrt(((p - t) ** 2).sum() / max((t ** 2).sum(), 1e-12)))


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

    model = FNO2d(cond_dim, hidden_channels=p["hidden_channels"], n_blocks=p["n_blocks"],
                  modes_h=modes_h, modes_w=modes_w, grid=grid).to(device)
    n_params = param_count(model)

    # ── resume ──
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
        print(f"[stage] pretrain on LF ({X_lf.shape[0]} samples)", flush=True)
        train_loop(model, X_lf, Y_lf, scaler_lf, args.epochs, p["lr_pretrain"], p, device, "LF-pretrain")
        print(f"[stage] fine-tune on HF ({X_hf.shape[0]} samples)", flush=True)
        train_loop(model, X_hf, Y_hf, scaler_hf, args.epochs, p["lr_finetune"], p, device, "HF-finetune")
        torch.save({"epochs_target": args.epochs, "grid": list(grid),
                    "model": model.state_dict()}, last)
    train_seconds = time.time() - t_train

    # ── eval: network output, then test-time PDE-residual refinement ──
    residual_fn = get_residual_fn(args.dataset_name)
    refine_active = residual_fn is not None and args.refine_steps > 0
    print(f"[refine] dataset={args.dataset_name} residual={'laplacian_prior' if residual_fn else 'NONE(no-op)'} "
          f"steps={args.refine_steps} lr={args.refine_lr} w_res={args.w_res} w_anchor={args.w_anchor} "
          f"active={refine_active}", flush=True)

    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize()
    t_eval = time.time()
    model.eval()
    preds_pre, preds_post = [], []
    bs = p["batch_size"]
    for i in range(0, X_te.shape[0], bs):
        xb = torch.from_numpy(X_te[i:i + bs]).float().to(device)
        with torch.no_grad():
            u_pred = model(xb) * scaler_hf            # (B,H,W) raw units
        preds_pre.append(u_pred.reshape(u_pred.shape[0], -1).cpu().numpy())
        u_ref = refine_field(u_pred, xb, grid, residual_fn,
                             steps=args.refine_steps, lr=args.refine_lr,
                             w_res=args.w_res, w_anchor=args.w_anchor)
        preds_post.append(u_ref.reshape(u_ref.shape[0], -1).cpu().numpy())
    if device.type == "cuda":
        torch.cuda.synchronize()
    eval_seconds = time.time() - t_eval

    pred_pre = np.concatenate(preds_pre, 0).astype(np.float64)
    pred_post = np.concatenate(preds_post, 0).astype(np.float64)
    target = Y_te.reshape(Y_te.shape[0], -1).astype(np.float64)
    n_samples = int(target.shape[0])
    nrmse_pre = _nrmse_agg(pred_pre, target)
    nrmse_post = _nrmse_agg(pred_post, target)
    print(f"[refine] nRMSE pre={nrmse_pre:.6f} post={nrmse_post:.6f} "
          f"(delta={nrmse_post - nrmse_pre:+.6e})", flush=True)

    latency = (1000.0 * eval_seconds / max(n_samples, 1)) if device.type == "cuda" else None
    peak_mem = (torch.cuda.max_memory_allocated() / 1e6) if device.type == "cuda" else None

    return finalize_and_write(
        out_path=out_path, model="mf_fno_ptr", dataset=args.dataset_name,
        pred=pred_post, target=target, work_grid=grid, n_params=int(n_params),
        train_seconds=train_seconds, eval_seconds=eval_seconds,
        latency_ms_per_sample=latency, peak_mem_mb=peak_mem, seed=args.seed,
        extra={"device": str(device), "hf_fidelity": int(hf), "lf_fidelity": int(lf),
               "mf_mechanism": "transfer_learning_pretrain_LF_finetune_HF",
               "conditioning": "film_on_X_per_block",
               "refinement": "test_time_pde_residual_on_field",
               "residual_kind": ("laplacian_smoothness_PLACEHOLDER" if residual_fn
                                 else "none_noop_equals_winner"),
               "refine_active": bool(refine_active),
               "refine_steps": int(args.refine_steps), "refine_lr": float(args.refine_lr),
               "w_res": float(args.w_res), "w_anchor": float(args.w_anchor),
               "nRMSE_pre_refine": nrmse_pre, "nRMSE_post_refine": nrmse_post,
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
    ap.add_argument("--refine_steps", type=int, default=20)
    ap.add_argument("--refine_lr", type=float, default=1e-2)
    ap.add_argument("--w_res", type=float, default=0.1)
    ap.add_argument("--w_anchor", type=float, default=1.0)
    args = ap.parse_args()
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    run(args, out)
    print(f"[wrote] {out}", flush=True)


if __name__ == "__main__":
    main()
