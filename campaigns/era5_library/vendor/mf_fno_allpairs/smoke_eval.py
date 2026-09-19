"""Smoke + fair-eval for mf_fno_allpairs (S2).

ONE FNO over EVERY ordered fidelity pair (src < tgt). For each pair we build
training rows (X_i, f_src, f_tgt) -> Y_i@tgt resampled to the working grid, pool
all pairs, and train a single joint stage, then a short LF->HF finetune to sharpen
the target query. FiLM cond = [X, f_src, f_tgt] (cond_dim = d + 2).

Pairing across fidelities: ifc_raw aligns samples across fids; if two fids have
different N we intersect by index modulo the smaller N (documented, robust for
ifc_heat which is aligned so the modulo is a no-op).

Eval: query (f_src = lf_norm, f_tgt = hf_norm) -> HF field; de-normalize, finalize.

Contract: --dataset_dir --dataset_name --epochs --out --ckpt_dir --seed.
Resume: ckpt_dir/last.pt keyed on (epochs_target, grid).
"""
from __future__ import annotations

import argparse
import sys
import time
from itertools import combinations
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

MODEL_LIBRARY = Path(__file__).resolve().parents[2]            # …/mf_field/operator_library
sys.path.insert(0, str(MODEL_LIBRARY))
sys.path.insert(0, str(Path(__file__).resolve().parent))   # local model.py

from common.backbone import param_count  # noqa: E402
from common.mffp import (load_mf_dataset, resolve_grid, finalize_and_write,  # noqa: E402
                         SMOKE, _cap_grid, _modes, _to_grid)
from model import AllPairsFNO2d  # noqa: E402


def _fnorm_fn(fids):
    fmin, fmax = float(min(fids)), float(max(fids))
    def fnorm(fid):
        if fmax == fmin:
            return 1.0
        return (np.log(float(fid)) - np.log(fmin)) / (np.log(fmax) - np.log(fmin))
    return fnorm


def build_pairs(train, grid, args, fnorm):
    """Build pooled all-ordered-pairs training rows.

    Returns X_all (M, d+2), Y_all (M, H, W), and a per-fid (X, Y@grid) cache.
    """
    fids = train["fids"]
    field_cache = {}   # fid -> Y@grid (N_fid, H, W)
    cond_cache = {}    # fid -> X (N_fid, d)
    for fid in fids:
        native = resolve_grid(args.dataset_name, int(train["n_cells_by_fid"][fid]))
        field_cache[fid] = _to_grid(train["field_by_fid"][fid], native, grid)
        cond_cache[fid] = train["cond_by_fid"][fid].astype(np.float32)

    Xs, Ys = [], []
    pairs = list(combinations(fids, 2))  # ordered src<tgt
    for s, t in pairs:
        Xs_, Yt_ = cond_cache[s], field_cache[t]
        n = min(Xs_.shape[0], Yt_.shape[0])  # intersect by index (modulo no-op if aligned)
        Xsrc = Xs_[:n]
        Ytgt = Yt_[:n]
        fs = np.full((n, 1), fnorm(s), dtype=np.float32)
        ft = np.full((n, 1), fnorm(t), dtype=np.float32)
        Xs.append(np.concatenate([Xsrc, fs, ft], axis=1))
        Ys.append(Ytgt)
    X_all = np.concatenate(Xs, 0).astype(np.float32)
    Y_all = np.concatenate(Ys, 0).astype(np.float32)
    return X_all, Y_all, pairs


def _train(model, X, Y, scaler, epochs, lr, p, device, tag):
    if X.shape[0] == 0 or epochs <= 0:
        return
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=p["weight_decay"])
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(epochs, 1), eta_min=1e-6)
    Xt = torch.from_numpy(X).float()
    Yt = torch.from_numpy(Y).float() / scaler
    n = X.shape[0]
    bs = min(p["batch_size"], n)
    g = torch.Generator().manual_seed(0)
    for ep in range(epochs):
        model.train()
        perm = torch.randperm(n, generator=g)
        tot = 0.0
        for i in range(0, n, bs):
            idx = perm[i:i + bs]
            xb = Xt[idx].to(device); yb = Yt[idx].to(device)
            opt.zero_grad(set_to_none=True)
            pred = model(xb)
            loss = F.mse_loss(pred, yb)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), p["grad_clip"])
            opt.step()
            tot += float(loss.detach())
        sched.step()
        if (ep + 1) % max(1, epochs // 5) == 0 or ep == epochs - 1:
            print(f"[{tag} {ep+1:04d}/{epochs}] mse={tot/max(1,(n+bs-1)//bs):.4e}", flush=True)


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
    grid = _cap_grid(hf_grid_native)
    modes_h, modes_w = _modes(grid, p["modes_cap"])
    fnorm = _fnorm_fn(train["fids"])

    # all-pairs pooled training set
    X_all, Y_all, pairs = build_pairs(train, grid, args, fnorm)

    # LF->HF finetune rows (src=lf, tgt=hf) and HF test rows
    hf_native = hf_grid_native
    lf_native = resolve_grid(args.dataset_name, int(train["n_cells_by_fid"][lf]))
    X_lf = train["cond_by_fid"][lf].astype(np.float32)
    Y_hf_tr = _to_grid(train["field_by_fid"][hf], hf_native, grid)
    n_ft = min(X_lf.shape[0], Y_hf_tr.shape[0])
    fs_q = np.full((n_ft, 1), fnorm(lf), dtype=np.float32)
    ft_q = np.full((n_ft, 1), fnorm(hf), dtype=np.float32)
    X_ft = np.concatenate([X_lf[:n_ft], fs_q, ft_q], axis=1).astype(np.float32)
    Y_ft = Y_hf_tr[:n_ft]

    X_te_raw = test["cond_by_fid"][hf].astype(np.float32)
    Y_te = _to_grid(test["field_by_fid"][hf], hf_native, grid)
    n_te = X_te_raw.shape[0]
    fs_te = np.full((n_te, 1), fnorm(lf), dtype=np.float32)
    ft_te = np.full((n_te, 1), fnorm(hf), dtype=np.float32)
    X_te = np.concatenate([X_te_raw, fs_te, ft_te], axis=1).astype(np.float32)

    cond_dim = int(X_all.shape[1])  # d + 2
    # single global scaler from the pooled all-pairs targets
    scaler = max(float(np.abs(Y_all).max()), 1e-8) if Y_all.size else 1.0
    scaler_hf = max(float(np.abs(Y_ft).max()), 1e-8) if Y_ft.size else scaler

    print(f"[data] {args.dataset_name} loader={train['loader']} LF={lf} HF={hf} "
          f"n_pairs={len(pairs)} pairs={[(int(s),int(t)) for s,t in pairs]} "
          f"hf_native={hf_native} work_grid={grid} modes=({modes_h},{modes_w}) "
          f"M_allpairs={X_all.shape[0]} N_ft={X_ft.shape[0]} N_test={n_te} cond_dim={cond_dim} "
          f"f_lf={fnorm(lf):.3f} f_hf={fnorm(hf):.3f}", flush=True)

    model = AllPairsFNO2d(cond_dim, hidden_channels=p["hidden_channels"],
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
        # 1) joint all-pairs training (pooled over every ordered pair)
        print(f"[stage] all-pairs joint train ({X_all.shape[0]} rows)", flush=True)
        _train(model, X_all, Y_all, scaler, args.epochs, p["lr_pretrain"], p, device, "allpairs")
        # 2) short LF->HF finetune to sharpen the eval query (rescale to HF stats)
        ft_epochs = max(1, args.epochs // 2)
        print(f"[stage] LF->HF finetune ({X_ft.shape[0]} rows, {ft_epochs} ep)", flush=True)
        _train(model, X_ft, Y_ft, scaler_hf, ft_epochs, p["lr_finetune"], p, device, "ft")
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
        out_path=out_path, model="mf_fno_allpairs", dataset=args.dataset_name,
        pred=pred, target=target, work_grid=grid, n_params=int(n_params),
        train_seconds=train_seconds, eval_seconds=eval_seconds,
        latency_ms_per_sample=latency, peak_mem_mb=peak_mem, seed=args.seed,
        extra={"device": str(device), "hf_fidelity": int(hf), "lf_fidelity": int(lf),
               "mf_mechanism": "allpairs_joint_train_then_lf2hf_finetune",
               "conditioning": "film_on_[X,f_src,f_tgt]",
               "n_pairs": len(pairs),
               "pairs": [[int(s), int(t)] for s, t in pairs],
               "f_lf_norm": float(fnorm(lf)), "f_hf_norm": float(fnorm(hf)),
               "hf_grid_native": list(hf_native), "work_grid": list(grid)},
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
