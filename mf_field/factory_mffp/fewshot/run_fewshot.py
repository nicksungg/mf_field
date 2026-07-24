"""EXP1 — few-shot-HF sweep (paper hardening experiment 1).

Tests the mechanistic claim: transfer learning's advantage over output-space
discrepancy correction GROWS as high-fidelity data becomes scarce.

Both methods use the IDENTICAL FNO2d backbone (from references/external_sota/
mf_fno_transfer/model.py), so the ONLY variable is the multi-fidelity mechanism:
  - transfer    : pretrain one FNO on ALL low-fidelity data, then fine-tune the
                  same weights on the (subsampled) HF set. [weight-space transfer]
  - additive    : train FNO_LF on LF (frozen), train FNO_delta on the HF residual
                  HF - LF_pred over the (subsampled) HF set. [output-space residual]
  - hf_only     : train one FNO on the (subsampled) HF set ALONE — the no-MF control
                  showing how much LF helps at each N_HF.

For each (dataset, N_HF, mechanism, seed): cap the HF TRAIN set to N_HF random
samples (LF data untouched), train at the common 256-cap working grid, evaluate on
the FULL HF test field, write per-sample rel-L2 + bootstrap CI via finalize-style JSON.

Run one cell:
  python fewshot/run_fewshot.py --dataset_dir data/<ds> --dataset_name <ds> \
      --mechanism {transfer,additive,hf_only} --n_hf <int|all> --epochs <int> \
      --seed <int> --out <json> --ckpt_dir <dir>
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "references" / "external_sota" / "mf_fno_transfer"))

from model import FNO2d, param_count  # the verified geometry-general backbone
from data_adapters import load_mf_dataset
from data_adapters.geometry import resolve_grid
from data_adapters.metrics import per_sample_rel_l2, bootstrap_ci

WORK_CAP = 256
P = dict(hidden_channels=64, n_blocks=4, modes_cap=12, batch_size=16,
         lr=1e-3, lr_finetune=3e-4, weight_decay=1e-5, grad_clip=1.0)


def _cap_grid(grid, cap=WORK_CAP):
    H, W = int(grid[0]), int(grid[1]); m = max(H, W)
    if m <= cap:
        return (H, W)
    f = cap / m
    return (max(1, round(H * f)), max(1, round(W * f)))


def _modes(grid, cap):
    H, W = grid
    return (min(cap, max(H // 2, 1)), min(cap, W // 2 + 1))


def _to_grid(y_flat, src, dst):
    Hs, Ws = int(src[0]), int(src[1]); Hd, Wd = int(dst[0]), int(dst[1])
    t = torch.from_numpy(np.ascontiguousarray(y_flat, dtype=np.float32)).view(-1, 1, Hs, Ws)
    if (Hs, Ws) != (Hd, Wd):
        t = F.interpolate(t, size=(Hd, Wd), mode="bilinear", align_corners=False)
    return t.squeeze(1).numpy().astype(np.float32)


def _train(model, X, Y, scaler, epochs, lr, device, target_field=None):
    if X.shape[0] == 0 or epochs <= 0:
        return
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=P["weight_decay"])
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(epochs, 1), eta_min=1e-6)
    Xt = torch.from_numpy(X).float()
    tgt = target_field if target_field is not None else Y
    Yt = torch.from_numpy(tgt).float() / scaler
    n = X.shape[0]; bs = min(P["batch_size"], n); g = torch.Generator().manual_seed(0)
    for ep in range(epochs):
        model.train(); perm = torch.randperm(n, generator=g)
        for i in range(0, n, bs):
            idx = perm[i:i + bs]; xb = Xt[idx].to(device); yb = Yt[idx].to(device)
            opt.zero_grad(set_to_none=True)
            loss = F.mse_loss(model(xb), yb); loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), P["grad_clip"]); opt.step()
        sched.step()


@torch.no_grad()
def _predict(model, X, scaler, device):
    model.eval(); out = []
    for i in range(0, X.shape[0], P["batch_size"]):
        xb = torch.from_numpy(X[i:i + P["batch_size"]]).float().to(device)
        out.append((model(xb) * scaler).cpu().numpy())
    return np.concatenate(out, 0).astype(np.float32)


def run(args):
    torch.manual_seed(args.seed); np.random.seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    train = load_mf_dataset(args.dataset_dir, "train")
    test = load_mf_dataset(args.dataset_dir, "test")
    hf = train["hf_fid"]; lf = min(train["lf_fids"]) if train["lf_fids"] else hf
    if hf not in test["fids"]:
        hf = test["hf_fid"]
    hf_native = resolve_grid(args.dataset_name, int(train["n_cells_by_fid"][hf]))
    lf_native = resolve_grid(args.dataset_name, int(train["n_cells_by_fid"][lf]))
    grid = _cap_grid(hf_native); mh, mw = _modes(grid, P["modes_cap"])

    X_lf = train["cond_by_fid"][lf].astype(np.float32)
    Y_lf = _to_grid(train["field_by_fid"][lf], lf_native, grid)
    X_hf_all = train["cond_by_fid"][hf].astype(np.float32)
    Y_hf_all = _to_grid(train["field_by_fid"][hf], hf_native, grid)
    X_te = test["cond_by_fid"][hf].astype(np.float32)
    Y_te = _to_grid(test["field_by_fid"][hf], hf_native, grid)
    cond_dim = int(X_hf_all.shape[1])

    # ---- subsample HF train set to N_HF (seeded) ----
    N_avail = X_hf_all.shape[0]
    if str(args.n_hf).lower() == "all":
        n_hf = N_avail
    else:
        n_hf = min(int(args.n_hf), N_avail)
    rng = np.random.default_rng(args.seed)
    sel = rng.choice(N_avail, size=n_hf, replace=False)
    X_hf = X_hf_all[sel]; Y_hf = Y_hf_all[sel]

    s_lf = max(float(np.abs(Y_lf).max()), 1e-8) if Y_lf.size else 1.0
    s_hf = max(float(np.abs(Y_hf).max()), 1e-8) if Y_hf.size else 1.0

    print(f"[fewshot] {args.dataset_name} mech={args.mechanism} N_HF={n_hf}/{N_avail} "
          f"seed={args.seed} grid={grid} N_lf={X_lf.shape[0]} N_test={X_te.shape[0]}", flush=True)

    t0 = time.time()
    if args.mechanism == "hf_only":
        m = FNO2d(cond_dim, P["hidden_channels"], P["n_blocks"], mh, mw, grid).to(device)
        _train(m, X_hf, Y_hf, s_hf, args.epochs, P["lr"], device)
        pred = _predict(m, X_te, s_hf, device)
        n_params = param_count(m)

    elif args.mechanism == "transfer":
        m = FNO2d(cond_dim, P["hidden_channels"], P["n_blocks"], mh, mw, grid).to(device)
        _train(m, X_lf, Y_lf, s_lf, args.epochs, P["lr"], device)          # pretrain LF
        _train(m, X_hf, Y_hf, s_hf, args.epochs, P["lr_finetune"], device)  # finetune HF
        pred = _predict(m, X_te, s_hf, device)
        n_params = param_count(m)

    elif args.mechanism == "additive":
        fno_lf = FNO2d(cond_dim, P["hidden_channels"], P["n_blocks"], mh, mw, grid).to(device)
        fno_d = FNO2d(cond_dim, P["hidden_channels"], P["n_blocks"], mh, mw, grid).to(device)
        _train(fno_lf, X_lf, Y_lf, s_lf, args.epochs, P["lr"], device)
        lf_on_hf = _predict(fno_lf, X_hf, s_lf, device)
        resid = (Y_hf - lf_on_hf).astype(np.float32)
        s_r = max(float(np.abs(resid).max()), 1e-8) if resid.size else 1.0
        _train(fno_d, X_hf, None, s_r, args.epochs, P["lr"], device, target_field=resid)
        pred = _predict(fno_lf, X_te, s_lf, device) + _predict(fno_d, X_te, s_r, device)
        n_params = param_count(fno_lf) + param_count(fno_d)
    else:
        raise ValueError(f"unknown mechanism {args.mechanism}")
    train_seconds = time.time() - t0

    p = pred.reshape(pred.shape[0], -1).astype(np.float64)
    t = Y_te.reshape(Y_te.shape[0], -1).astype(np.float64)
    rel = per_sample_rel_l2(p, t)
    ci = bootstrap_ci(rel, seed=args.seed)
    agg = float(np.sqrt(((p - t) ** 2).sum() / max((t ** 2).sum(), 1e-12)))
    import json
    out = {
        "experiment": "fewshot_hf", "model": args.mechanism, "dataset": args.dataset_name,
        "n_hf": int(n_hf), "n_hf_available": int(N_avail), "seed": int(args.seed),
        "epochs": int(args.epochs), "work_grid": list(grid), "n_params": int(n_params),
        "train_seconds": train_seconds, "device": str(device),
        "splits": {"test_hf": {"nRMSE": agg, "rel_l2_mean": ci["mean"],
                               "rel_l2_ci95_lo": ci["lo"], "rel_l2_ci95_hi": ci["hi"],
                               "rel_l2_std": ci["std"], "n_samples": ci["n"]}},
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=2))
    print(f"[fewshot] {args.mechanism}/{args.dataset_name} N_HF={n_hf}: relL2={ci['mean']:.4e} "
          f"[{ci['lo']:.4e},{ci['hi']:.4e}] -> {args.out}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset_dir", required=True)
    ap.add_argument("--dataset_name", required=True)
    ap.add_argument("--mechanism", required=True, choices=["transfer", "additive", "hf_only"])
    ap.add_argument("--n_hf", required=True)  # int or "all"
    ap.add_argument("--epochs", type=int, default=2500)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ckpt_dir", default="/tmp/fewshot_ck")
    args = ap.parse_args()
    run(args)


if __name__ == "__main__":
    main()
