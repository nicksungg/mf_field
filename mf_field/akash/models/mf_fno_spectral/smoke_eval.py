"""Spectral fidelity-decomposition MF-FNO — smoke eval.

Flow (mirrors the winner mf_fno_transfer_film):
  working grid = _cap_grid(resolve_grid(name, n_cells[hf]))  (256-cap)
  LF field + HF field/test resampled to the working grid (_to_grid)
  per-stage scaler = max|Y| of that stage's training fields
  1) PRETRAIN on LF (all spectral weights trainable)
  2) FREEZE the LOW Fourier band (cutoff = min(modes_cap, lf_native_modes)),
     then FINE-TUNE on HF (only HIGH band + 1x1/FiLM/lift/proj move)
  3) eval full HF test, de-normalized -> finalize_and_write

Also asserts the frozen LOW-band spectral entries are byte-for-byte unchanged
across the HF fine-tune (reported in extra.frozen_low_band_unchanged).

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
from model import FNO2dSpectralMF  # noqa: E402


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

    # LOW band = what the LF native grid can resolve, capped by modes_cap.
    lf_grid_work = _cap_grid(lf_grid_native)
    lf_modes_h, lf_modes_w = _modes(lf_grid_work, p["modes_cap"])
    cutoff_h = min(modes_h, lf_modes_h)
    cutoff_w = min(modes_w, lf_modes_w)

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
          f"hf_native={hf_grid_native} lf_native={lf_grid_native} work_grid={grid} "
          f"modes=({modes_h},{modes_w}) low_cutoff=({cutoff_h},{cutoff_w}) "
          f"N_lf={X_lf.shape[0]} N_hf={X_hf.shape[0]} N_test={X_te.shape[0]} cond_dim={cond_dim}",
          flush=True)

    model = FNO2dSpectralMF(cond_dim, hidden_channels=p["hidden_channels"], n_blocks=p["n_blocks"],
                            modes_h=modes_h, modes_w=modes_w, grid=grid).to(device)
    n_params = param_count(model)

    ckpt_dir = Path(args.ckpt_dir); ckpt_dir.mkdir(parents=True, exist_ok=True)
    last = ckpt_dir / "last.pt"
    trained = False
    frozen_unchanged = None
    n_frozen = 0
    if last.exists():
        try:
            sd = torch.load(last, map_location=device, weights_only=False)
            if sd.get("epochs_target") == args.epochs and sd.get("grid") == list(grid):
                model.load_state_dict(sd["model"]); trained = True
                frozen_unchanged = sd.get("frozen_low_band_unchanged")
                n_frozen = int(sd.get("n_frozen_entries", 0))
                print("[resume] loaded finished checkpoint", flush=True)
        except Exception as e:
            print(f"[resume] failed ({e}); fresh", flush=True)

    t_train = time.time()
    if not trained:
        # 1) PRETRAIN on LF (all spectral weights trainable)
        print(f"[stage] pretrain on LF ({X_lf.shape[0]} samples)", flush=True)
        train_loop(model, X_lf, Y_lf, scaler_lf, args.epochs, p["lr_pretrain"], p, device, "LF-pretrain")

        # 2) FREEZE the LOW band, snapshot it, then FINE-TUNE on HF
        n_frozen = model.freeze_low_band(cutoff_h, cutoff_w)
        snaps_before = model.low_band_snapshots()
        print(f"[stage] froze LOW band: {n_frozen} complex entries (cutoff=({cutoff_h},{cutoff_w}))", flush=True)
        print(f"[stage] fine-tune on HF ({X_hf.shape[0]} samples)", flush=True)
        train_loop(model, X_hf, Y_hf, scaler_hf, args.epochs, p["lr_finetune"], p, device, "HF-finetune")

        # assert the frozen LOW band is unchanged after the HF fine-tune
        snaps_after = model.low_band_snapshots()
        frozen_unchanged = True
        for sb, sa in zip(snaps_before, snaps_after):
            if sb is None or sa is None:
                continue
            for wb, wa in zip(sb, sa):
                if not torch.equal(wb, wa):
                    frozen_unchanged = False
        assert frozen_unchanged, "FROZEN low-mode band changed during HF fine-tune!"
        print(f"[assert] frozen low-band unchanged = {frozen_unchanged}", flush=True)

        torch.save({"epochs_target": args.epochs, "grid": list(grid),
                    "model": model.state_dict(),
                    "frozen_low_band_unchanged": bool(frozen_unchanged),
                    "n_frozen_entries": int(n_frozen)}, last)
    train_seconds = time.time() - t_train

    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize()
    t_eval = time.time()
    model.eval()
    preds = []
    bs = p["batch_size"]
    with torch.no_grad():
        for i in range(0, X_te.shape[0], bs):
            xb = torch.from_numpy(X_te[i:i + bs]).float().to(device)
            pr = model(xb) * scaler_hf
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
        out_path=out_path, model="mf_fno_spectral", dataset=args.dataset_name,
        pred=pred, target=target, work_grid=grid, n_params=int(n_params),
        train_seconds=train_seconds, eval_seconds=eval_seconds,
        latency_ms_per_sample=latency, peak_mem_mb=peak_mem, seed=args.seed,
        extra={"device": str(device), "hf_fidelity": int(hf), "lf_fidelity": int(lf),
               "mf_mechanism": "spectral_decomposition_freeze_low_band_finetune_high",
               "conditioning": "film_on_X_per_block",
               "low_cutoff": [int(cutoff_h), int(cutoff_w)],
               "modes": [int(modes_h), int(modes_w)],
               "n_frozen_complex_entries": int(n_frozen),
               "frozen_low_band_unchanged": bool(frozen_unchanged) if frozen_unchanged is not None else None,
               "hf_grid_native": list(hf_grid_native), "lf_grid_native": list(lf_grid_native),
               "work_grid": list(grid)},
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
