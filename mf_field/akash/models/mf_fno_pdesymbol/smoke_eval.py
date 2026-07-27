"""Smoke + fair-eval for mf_fno_pdesymbol (B4).

Condition the FNO on a learned PDE-identity embedding, indexed by `dataset_name`,
concatenated with X: the network FiLMs on [X, e_pde] per block. Same FiLM
backbone and transfer schedule (LF-pretrain -> HF-finetune) as the winner.

Single-dataset smoke = a single PDE id (0), so e_pde is one learned bias vector;
this verifies the plumbing. The DESIGNED VALUE is cross-dataset: training over
many datasets, each with its own id, yields a shared multi-PDE operator whose
per-PDE specialization lives entirely in the embedding table. We document this.

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
from model import PDESymbolFNO, param_count  # noqa: E402

EMBED_DIM = 8
N_PDES = 16  # capacity of the embedding table (id 0 used in single-dataset smoke)


class _FixedIdWrapper(torch.nn.Module):
    """Adapts PDESymbolFNO(x, pde_id) to the train_loop's model(x) signature."""

    def __init__(self, net, pde_id):
        super().__init__()
        self.net = net
        self.pde_id = int(pde_id)

    def forward(self, x):
        return self.net(x, pde_id=self.pde_id)


def run(args, out_path: Path) -> dict:
    torch.manual_seed(args.seed); np.random.seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    p = SMOKE
    ds_dir = Path(args.dataset_dir)
    pde_id = 0  # single-dataset smoke -> one PDE identity; cross-dataset uses 0..N-1

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
          f"N_lf={X_lf.shape[0]} N_hf={X_hf.shape[0]} N_test={X_te.shape[0]} cond_dim={cond_dim} "
          f"pde_id={pde_id} embed_dim={EMBED_DIM}", flush=True)

    model = PDESymbolFNO(cond_dim, n_pdes=N_PDES, embed_dim=EMBED_DIM,
                         hidden_channels=p["hidden_channels"], n_blocks=p["n_blocks"],
                         modes_h=modes_h, modes_w=modes_w, grid=grid).to(device)
    n_params = param_count(model)
    wrapped = _FixedIdWrapper(model, pde_id).to(device)

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
        train_loop(wrapped, X_lf, Y_lf, scaler_lf, args.epochs, p["lr_pretrain"], p, device, "LF-pretrain")
        print(f"[stage] fine-tune on HF ({X_hf.shape[0]} samples)", flush=True)
        train_loop(wrapped, X_hf, Y_hf, scaler_hf, args.epochs, p["lr_finetune"], p, device, "HF-finetune")
        torch.save({"epochs_target": args.epochs, "grid": list(grid),
                    "model": model.state_dict()}, last)
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
            pr = model(xb, pde_id=pde_id) * scaler_hf
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
        out_path=out_path, model="mf_fno_pdesymbol", dataset=args.dataset_name,
        pred=pred, target=target, work_grid=grid, n_params=int(n_params),
        train_seconds=train_seconds, eval_seconds=eval_seconds,
        latency_ms_per_sample=latency, peak_mem_mb=peak_mem, seed=args.seed,
        extra={"device": str(device), "hf_fidelity": int(hf), "lf_fidelity": int(lf),
               "mf_mechanism": "transfer_LF_pretrain_HF_finetune",
               "conditioning": "film_on_[X, learned_pde_identity_embedding]",
               "pde_id": int(pde_id), "embed_dim": int(EMBED_DIM), "n_pdes_capacity": int(N_PDES),
               "note": "single-dataset smoke uses one PDE id (one learned bias vector); the "
                       "designed value is cross-dataset (shared multi-PDE operator with per-PDE "
                       "embedding). This run verifies plumbing only.",
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
