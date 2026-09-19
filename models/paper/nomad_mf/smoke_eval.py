"""nomad_mf — NOMAD (nonlinear-manifold-decoder DeepONet) with LF->HF transfer.

DeepONet-style operator X -> full field, built from scratch (see model.py). The
SHIPPED decoder is NONLINEAR (NOMAD, seidman2022nomad); `--decoder linear` flips
to the classical LINEAR DeepONet reconstruction (lu2021deeponet) as a control,
isolating linear-vs-nonlinear decoding on an identical branch + transfer schedule.

The multi-fidelity mechanism = TRANSFER LEARNING, mirroring the benchmark winner
`mf_fno_transfer_film` byte-for-byte in the training/eval plumbing:
  1. pretrain the branch+decoder on the abundant LOW-fidelity data (field
     resampled to the 256-cap working grid),
  2. fine-tune the SAME network on the scarce HIGH-fidelity data (lower LR),
  3. evaluate on the HF test split.

Shares the fair-eval plumbing (resolve_grid + 256-cap working grid, full-field
eval, finalize_and_write with per-sample rel-L2 + bootstrap CI + params/latency/
mem), so the comparison isolates the DECODER, not the metric or the schedule.

Contract: --dataset_dir --dataset_name --epochs --out --ckpt_dir --seed
          (+ --decoder {nonlinear,linear}).
--epochs is the HF fine-tune budget; LF pretrain uses the same (capped) budget.
Resume: ckpt_dir/last.pt keyed on (epochs_target, grid, decoder).
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import torch

MODEL_LIBRARY = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(MODEL_LIBRARY))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from common.mffp import (  # noqa: E402
    load_mf_dataset, resolve_grid, finalize_and_write, WORK_CAP, SMOKE,
    _cap_grid, _modes, _to_grid, FACTORY_ROOT, train_loop,
)
from model import NomadMF, param_count  # noqa: E402


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
    grid = _cap_grid(hf_grid_native)               # common working grid (256-cap)

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
          f"hf_native={hf_grid_native} work_grid={grid} decoder={args.decoder} "
          f"N_lf={X_lf.shape[0]} N_hf={X_hf.shape[0]} N_test={X_te.shape[0]} cond_dim={cond_dim}",
          flush=True)

    model = NomadMF(cond_dim, grid=grid, decoder=args.decoder).to(device)
    n_params = param_count(model)

    # ── resume ──
    ckpt_dir = Path(args.ckpt_dir); ckpt_dir.mkdir(parents=True, exist_ok=True)
    last = ckpt_dir / "last.pt"
    trained = False
    if last.exists():
        try:
            sd = torch.load(last, map_location=device, weights_only=False)
            if (sd.get("epochs_target") == args.epochs and sd.get("grid") == list(grid)
                    and sd.get("decoder") == args.decoder):
                model.load_state_dict(sd["model"]); trained = True
                print("[resume] loaded finished checkpoint", flush=True)
        except Exception as e:
            print(f"[resume] failed ({e}); fresh", flush=True)

    t_train = time.time()
    if not trained:
        # 1) PRETRAIN on low-fidelity (the abundant data)
        print(f"[stage] pretrain on LF ({X_lf.shape[0]} samples)", flush=True)
        train_loop(model, X_lf, Y_lf, scaler_lf, args.epochs, p["lr_pretrain"], p, device, "LF-pretrain")
        # 2) FINE-TUNE on high-fidelity (scarce), lower LR.
        print(f"[stage] fine-tune on HF ({X_hf.shape[0]} samples)", flush=True)
        train_loop(model, X_hf, Y_hf, scaler_hf, args.epochs, p["lr_finetune"], p, device, "HF-finetune")
        torch.save({"epochs_target": args.epochs, "grid": list(grid),
                    "decoder": args.decoder, "model": model.state_dict()}, last)
    train_seconds = time.time() - t_train

    # ── eval: full HF field on the working grid ──
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize()
    t_eval = time.time()
    model.eval()
    preds = []
    bs = p["batch_size"]
    with torch.no_grad():
        for i in range(0, X_te.shape[0], bs):
            xb = torch.from_numpy(X_te[i:i + bs]).float().to(device)
            pr = model(xb) * scaler_hf                      # de-normalize to raw units
            preds.append(pr.reshape(pr.shape[0], -1).cpu().numpy())
    if device.type == "cuda":
        torch.cuda.synchronize()
    eval_seconds = time.time() - t_eval
    pred = np.concatenate(preds, 0).astype(np.float64)
    target = Y_te.reshape(Y_te.shape[0], -1).astype(np.float64)
    n_samples = int(target.shape[0])
    latency = (1000.0 * eval_seconds / max(n_samples, 1)) if device.type == "cuda" else None
    peak_mem = (torch.cuda.max_memory_allocated() / 1e6) if device.type == "cuda" else None

    return finalize_and_write(
        out_path=out_path, model="nomad_mf", dataset=args.dataset_name,
        pred=pred, target=target, work_grid=grid, n_params=int(n_params),
        train_seconds=train_seconds, eval_seconds=eval_seconds,
        latency_ms_per_sample=latency, peak_mem_mb=peak_mem, seed=args.seed,
        extra={"device": str(device), "hf_fidelity": int(hf), "lf_fidelity": int(lf),
               "mf_mechanism": "transfer_learning_pretrain_LF_finetune_HF",
               "operator": "deeponet", "decoder": args.decoder,
               "decoder_kind": ("nonlinear_manifold_NOMAD" if args.decoder == "nonlinear"
                                else "linear_deeponet_control"),
               "latent_dim": int(model.latent_dim),
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
    ap.add_argument("--decoder", choices=["nonlinear", "linear"], default="nonlinear",
                    help="nonlinear = NOMAD (shipped); linear = DeepONet control")
    args = ap.parse_args()
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    run(args, out)
    print(f"[wrote] {out}", flush=True)


if __name__ == "__main__":
    main()
