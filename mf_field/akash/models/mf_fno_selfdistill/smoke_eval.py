"""Smoke + fair-eval for mf_fno_selfdistill (B6).

Fidelity bootstrapping (self-training). Same FiLM-on-X backbone and transfer
schedule as the winner, with one twist in the HF stage:

  1. LF-pretrain on the abundant low-fidelity data (winner's step 1).
  2. Use the LF-pretrained model to predict PSEUDO-HF labels on the LF inputs
     (the model's own LF predictions, treated as extra HF supervision targets
     in HF-scaler space).
  3. HF-finetune on a MIX of the few REAL HF samples (weight 1.0) + the pseudo-HF
     samples (weight `pseudo_weight` < 1.0), so the scarce real HF data dominates
     while the pseudo labels regularize / expand coverage of the input space.

`extra` reports n_real_hf, n_pseudo, and the pseudo weight.

Contract: --dataset_dir --dataset_name --epochs --out --ckpt_dir --seed
          [--pseudo_weight FLOAT].
Resume: ckpt_dir/last.pt keyed on (epochs_target, grid, pseudo_weight).
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

from common.mffp import (load_mf_dataset, resolve_grid, finalize_and_write,  # noqa: E402
                         SMOKE, _cap_grid, _modes, _to_grid, train_loop)
from model import FNO2d, param_count  # noqa: E402

DEFAULT_PSEUDO_WEIGHT = 0.3


def train_weighted(model, X, Y, W, scaler, epochs, lr, p, device, tag):
    """Train on (X, Y) with per-sample loss weights W (already in y/scaler space).

    Y is passed RAW (de-normalized) here and normalized by `scaler` internally so
    real and pseudo targets live in the same HF-scaler space.
    """
    if X.shape[0] == 0 or epochs <= 0:
        return
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=p["weight_decay"])
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(epochs, 1), eta_min=1e-6)
    Xt = torch.from_numpy(X).float()
    Yt = torch.from_numpy(Y).float() / scaler
    Wt = torch.from_numpy(W).float()
    n = X.shape[0]
    bs = min(p["batch_size"], n)
    g = torch.Generator().manual_seed(0)
    for ep in range(epochs):
        model.train()
        perm = torch.randperm(n, generator=g)
        tot = 0.0
        for i in range(0, n, bs):
            idx = perm[i:i + bs]
            xb = Xt[idx].to(device); yb = Yt[idx].to(device); wb = Wt[idx].to(device)
            opt.zero_grad(set_to_none=True)
            pred = model(xb)
            # per-sample weighted MSE
            se = (pred - yb) ** 2
            per_sample = se.flatten(1).mean(dim=1)
            loss = (wb * per_sample).sum() / wb.sum().clamp(min=1e-8)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), p["grad_clip"])
            opt.step()
            tot += float(loss.detach())
        sched.step()
        if (ep + 1) % max(1, epochs // 5) == 0 or ep == epochs - 1:
            print(f"[{tag} {ep+1:04d}/{epochs}] wmse={tot/max(1,(n+bs-1)//bs):.4e}", flush=True)


def run(args, out_path: Path) -> dict:
    torch.manual_seed(args.seed); np.random.seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    p = SMOKE
    ds_dir = Path(args.dataset_dir)
    pseudo_weight = float(args.pseudo_weight)

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
          f"pseudo_weight={pseudo_weight}", flush=True)

    model = FNO2d(cond_dim, hidden_channels=p["hidden_channels"], n_blocks=p["n_blocks"],
                  modes_h=modes_h, modes_w=modes_w, grid=grid).to(device)
    n_params = param_count(model)

    ckpt_dir = Path(args.ckpt_dir); ckpt_dir.mkdir(parents=True, exist_ok=True)
    last = ckpt_dir / "last.pt"
    trained = False; n_real = int(X_hf.shape[0]); n_pseudo = 0
    if last.exists():
        try:
            sd = torch.load(last, map_location=device, weights_only=False)
            if (sd.get("epochs_target") == args.epochs and sd.get("grid") == list(grid)
                    and sd.get("pseudo_weight") == pseudo_weight):
                model.load_state_dict(sd["model"]); trained = True
                n_real = sd.get("n_real", n_real); n_pseudo = sd.get("n_pseudo", 0)
                print("[resume] loaded finished checkpoint", flush=True)
        except Exception as e:
            print(f"[resume] failed ({e}); fresh", flush=True)

    t_train = time.time()
    if not trained:
        # 1) LF pretrain (winner's step)
        print(f"[stage] pretrain on LF ({X_lf.shape[0]} samples)", flush=True)
        train_loop(model, X_lf, Y_lf, scaler_lf, args.epochs, p["lr_pretrain"], p, device, "LF-pretrain")

        # 2) generate pseudo-HF labels on LF inputs from the LF-pretrained model
        model.eval()
        pseudo = []
        bs = p["batch_size"]
        with torch.no_grad():
            for i in range(0, X_lf.shape[0], bs):
                xb = torch.from_numpy(X_lf[i:i + bs]).float().to(device)
                pr = model(xb) * scaler_lf            # LF-scaler -> raw units
                pseudo.append(pr.reshape(pr.shape[0], grid[0], grid[1]).cpu().numpy())
        Y_pseudo = np.concatenate(pseudo, 0).astype(np.float32)   # raw units, on grid
        n_pseudo = int(Y_pseudo.shape[0])

        # 3) HF finetune on MIX: real HF (w=1) + pseudo-HF (w=pseudo_weight)
        X_mix = np.concatenate([X_hf, X_lf], axis=0)
        Y_mix = np.concatenate([Y_hf, Y_pseudo], axis=0).reshape(-1, grid[0], grid[1])
        W_mix = np.concatenate([np.ones(n_real, np.float32),
                                np.full(n_pseudo, pseudo_weight, np.float32)], axis=0)
        print(f"[stage] HF finetune on MIX: real={n_real} pseudo={n_pseudo} "
              f"(pseudo_weight={pseudo_weight})", flush=True)
        train_weighted(model, X_mix, Y_mix, W_mix, scaler_hf, args.epochs,
                       p["lr_finetune"], p, device, "HF-finetune-mix")

        torch.save({"epochs_target": args.epochs, "grid": list(grid),
                    "pseudo_weight": pseudo_weight, "n_real": n_real, "n_pseudo": n_pseudo,
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
        out_path=out_path, model="mf_fno_selfdistill", dataset=args.dataset_name,
        pred=pred, target=target, work_grid=grid, n_params=int(n_params),
        train_seconds=train_seconds, eval_seconds=eval_seconds,
        latency_ms_per_sample=latency, peak_mem_mb=peak_mem, seed=args.seed,
        extra={"device": str(device), "hf_fidelity": int(hf), "lf_fidelity": int(lf),
               "mf_mechanism": "transfer_LF_pretrain_HF_finetune_with_pseudoHF_bootstrap",
               "conditioning": "film_on_X_per_block",
               "self_distill": "LF_pretrained_model_predicts_pseudoHF_on_LF_inputs",
               "n_real_hf": int(n_real), "n_pseudo_hf": int(n_pseudo),
               "pseudo_weight": float(pseudo_weight),
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
    ap.add_argument("--pseudo_weight", type=float, default=DEFAULT_PSEUDO_WEIGHT)
    args = ap.parse_args()
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    res = run(args, out)
    print(f"[wrote] {out}", flush=True)
    print(f"[nRMSE] {res['splits']['test_hf']['nRMSE']:.6f}", flush=True)


if __name__ == "__main__":
    main()
