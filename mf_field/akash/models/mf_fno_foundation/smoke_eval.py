"""Smoke + fair-eval for mf_fno_foundation (A3).

Cross-dataset foundation MF-FNO. A BPOM-style set-encoder maps the variable-width
parameter vector X (cond_dim 1..16) to a FIXED 64-dim embedding, so ONE shared
FNO backbone can be FiLM-conditioned uniformly across every dataset. The shared
backbone + BPOM encoder may be pretrained jointly across datasets (pretrain_all.py
-> pretrained.pt) and reloaded here, then HF-finetuned on the target dataset.

Flow (matches the winner's transfer schedule):
  1. init FoundationFNO2d on the target dataset's working grid.
  2. if pretrained.pt exists -> load the shared backbone+BPOM (shape-tolerant,
     since the pretrain grid/modes may differ from this dataset's working grid);
     ELSE self-pretrain on the target dataset's LF fields.
  3. HF-finetune on the scarce HF fields (lower LR).
  4. eval the full HF test field, de-normalized; finalize_and_write.

The contract smoke (ifc_heat alone) passes WITHOUT pretrained.pt via the
self-pretrain path.

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
import torch.nn.functional as F

AKASH = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(AKASH))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from common.backbone import param_count  # noqa: E402
from common.mffp import (load_mf_dataset, resolve_grid, finalize_and_write,  # noqa: E402
                         SMOKE, _cap_grid, _modes, _to_grid, train_loop)
from model import FoundationFNO2d, EMB_DIM  # noqa: E402

PRETRAINED = Path(__file__).resolve().parent / "pretrained.pt"


def _load_shared_tolerant(model, shared_sd, device):
    """Load matching-shape tensors from a foundation `shared` state_dict.

    The pretrain grid/modes may differ from this dataset's working grid, so the
    spectral weights (shape depends on modes) and coord-grid-derived sizes can
    mismatch. We copy every parameter whose shape matches and skip the rest. The
    BPOM encoder + 1x1 convs + FiLM MLPs are grid/cond_dim-independent and so
    always transfer; only the spectral kernels may be partly skipped.
    """
    own = model.state_dict()
    loaded, skipped = 0, 0
    new_sd = {}
    for k, v in own.items():
        if k in shared_sd and tuple(shared_sd[k].shape) == tuple(v.shape):
            new_sd[k] = shared_sd[k].to(device)
            loaded += 1
        else:
            new_sd[k] = v
            if k != "coord_grid":
                skipped += 1
    model.load_state_dict(new_sd)
    return loaded, skipped


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

    model = FoundationFNO2d(hidden_channels=p["hidden_channels"], n_blocks=p["n_blocks"],
                            modes_h=modes_h, modes_w=modes_w, grid=grid, emb_dim=EMB_DIM).to(device)
    n_params = param_count(model)

    # ── source of the pretrained backbone ──
    used_foundation = False
    foundation_datasets = []
    f_loaded = f_skipped = 0
    if PRETRAINED.exists():
        try:
            ck = torch.load(PRETRAINED, map_location=device, weights_only=False)
            f_loaded, f_skipped = _load_shared_tolerant(model, ck["shared"], device)
            foundation_datasets = ck.get("datasets", [])
            used_foundation = True
            print(f"[foundation] loaded pretrained.pt (matched={f_loaded} skipped={f_skipped} "
                  f"datasets={len(foundation_datasets)})", flush=True)
        except Exception as e:
            print(f"[foundation] load failed ({e}); self-pretrain", flush=True)

    print(f"[data] {args.dataset_name} loader={train['loader']} LF={lf} HF={hf} "
          f"hf_native={hf_grid_native} work_grid={grid} modes=({modes_h},{modes_w}) "
          f"N_lf={X_lf.shape[0]} N_hf={X_hf.shape[0]} N_test={X_te.shape[0]} cond_dim={cond_dim} "
          f"foundation={used_foundation}", flush=True)

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
        if not used_foundation:
            # self-pretrain on this dataset's LF (the no-foundation path)
            print(f"[stage] self-pretrain on LF ({X_lf.shape[0]} samples)", flush=True)
            train_loop(model, X_lf, Y_lf, scaler_lf, args.epochs, p["lr_pretrain"], p, device, "LF-pretrain")
        else:
            print("[stage] skip self-pretrain (using foundation backbone)", flush=True)
        # HF-finetune (always)
        print(f"[stage] fine-tune on HF ({X_hf.shape[0]} samples)", flush=True)
        train_loop(model, X_hf, Y_hf, scaler_hf, args.epochs, p["lr_finetune"], p, device, "HF-finetune")
        torch.save({"epochs_target": args.epochs, "grid": list(grid),
                    "model": model.state_dict()}, last)
    train_seconds = time.time() - t_train

    # ── eval ──
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

    res = finalize_and_write(
        out_path=out_path, model="mf_fno_foundation", dataset=args.dataset_name,
        pred=pred, target=target, work_grid=grid, n_params=int(n_params),
        train_seconds=train_seconds, eval_seconds=eval_seconds,
        latency_ms_per_sample=latency, peak_mem_mb=peak_mem, seed=args.seed,
        extra={"device": str(device), "hf_fidelity": int(hf), "lf_fidelity": int(lf),
               "mf_mechanism": "transfer_LF_pretrain_HF_finetune",
               "conditioning": "film_on_BPOM_set_embedding",
               "cond_dim": cond_dim, "emb_dim": EMB_DIM,
               "used_foundation_pretrain": used_foundation,
               "foundation_datasets": foundation_datasets,
               "foundation_matched_tensors": int(f_loaded),
               "foundation_skipped_tensors": int(f_skipped),
               "hf_grid_native": list(hf_grid_native), "work_grid": list(grid)},
    )
    return res


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
