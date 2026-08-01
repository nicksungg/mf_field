"""dg_transfer: discrepancy-gated FiLM on the transfer-learning FNO backbone.

The winning backbone (mf_fno_transfer_film) UNCHANGED:
  1. Pretrain a single gated FNO on abundant LF data (output scaled by scaler_lf).
  2. Fine-tune the SAME network on scarce HF data (lower LR, output scaled by
     scaler_hf — the per-stage re-scaling that sidesteps the Poisson collapse).
  3. Predict the HF field directly.

ADDED: a small LF ensemble supplies per-pixel uncertainty fields
[mu, sigma, q10, q50, q90]; those modulate every block of the transfer network via
zero-init Gates A (spatial FiLM) and B (spectral mode-gate). At init the gates are
identity, so the network equals mf_fno_transfer_film and can only improve.

Gates selectable via DG_GATES (default "A,B"). Contract:
--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed.
--epochs is BOTH the LF-pretrain and HF-finetune budget (as in mf_fno_transfer_film)
and the LF-ensemble budget.
"""
from __future__ import annotations

import argparse
import importlib.util as _ilu
import os
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model import DGTransferFNO, ALL_GATES, param_count  # noqa: E402
from data_adapters import load_mf_dataset  # noqa: E402
from data_adapters.geometry import resolve_grid  # noqa: E402
from data_adapters.metrics import finalize_and_write  # noqa: E402

# Small LF-ensemble member: plain FNO backbone, loaded under a distinct module name.
_fire_spec = _ilu.spec_from_file_location(
    "dg_transfer_lf_member", REPO_ROOT / "models" / "fno_fire_distcond" / "model.py")
_fire_mod = _ilu.module_from_spec(_fire_spec)
_fire_spec.loader.exec_module(_fire_mod)
FNO2d = _fire_mod.FNO2d  # noqa: E402

WORK_CAP = 256
SMOKE = dict(hidden_channels=64, n_blocks=4, modes_cap=12, batch_size=16,
             lr_pretrain=1e-3, lr_finetune=3e-4, weight_decay=1e-5, grad_clip=1.0,
             ensemble=3, lf_hidden=32, quantiles=(0.1, 0.5, 0.9), gate_ch=16)
AUG_CH = 2 + 3   # [mu, sigma, q10, q50, q90]


def _parse_gates() -> frozenset:
    raw = os.environ.get("DG_GATES", "A,B")
    return frozenset({t.strip().upper() for t in raw.split(",") if t.strip()} & ALL_GATES)


def _cap_grid(grid, cap=WORK_CAP):
    H, W = int(grid[0]), int(grid[1]); m = max(H, W)
    if m <= cap:
        return (H, W)
    f = cap / m
    return (max(1, round(H * f)), max(1, round(W * f)))


def _modes(grid, cap):
    H, W = grid
    return (min(cap, max(H // 2, 1)), min(cap, W // 2 + 1))


sys.path.insert(0, str(HERE.parent))  # models/ -> _common package
from _common.lf_registration import resample_fields  # noqa: E402


def _to_grid(y_flat, src, dst, dataset_name):
    """Resample under the dataset's registration convention
    (models/_common/lf_registration.py; registration defect note item 1)."""
    return resample_fields(y_flat, src, dst, dataset_name)


def _train_lf(model, X, Y, scaler, epochs, lr, p, device, seed):
    """Train a plain LF member: cond -> Y/scaler (MSE)."""
    if X.shape[0] == 0 or epochs <= 0:
        return
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=p["weight_decay"])
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(epochs, 1), eta_min=1e-6)
    Xt = torch.from_numpy(X).float(); Yt = torch.from_numpy(Y).float() / scaler
    n = X.shape[0]; bs = min(p["batch_size"], n); g = torch.Generator().manual_seed(seed)
    for _ in range(epochs):
        model.train()
        perm = torch.randperm(n, generator=g)
        for i in range(0, n, bs):
            idx = perm[i:i + bs]
            opt.zero_grad(set_to_none=True)
            loss = F.mse_loss(model(Xt[idx].to(device)), Yt[idx].to(device))
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), p["grad_clip"])
            opt.step()
        sched.step()


def _train_gated(model, X, aug, Y, scaler, epochs, lr, p, device, tag):
    """Train the gated transfer net: (cond, aug fields) -> Y/scaler (MSE)."""
    if X.shape[0] == 0 or epochs <= 0:
        return
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=p["weight_decay"])
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(epochs, 1), eta_min=1e-6)
    Xt = torch.from_numpy(X).float(); At = torch.from_numpy(aug).float()
    Yt = torch.from_numpy(Y).float() / scaler
    n = X.shape[0]; bs = min(p["batch_size"], n); g = torch.Generator().manual_seed(0)
    for ep in range(epochs):
        model.train()
        perm = torch.randperm(n, generator=g)
        tot = 0.0
        for i in range(0, n, bs):
            idx = perm[i:i + bs]
            xb = Xt[idx].to(device); ab = At[idx].to(device); yb = Yt[idx].to(device)
            opt.zero_grad(set_to_none=True)
            loss = F.mse_loss(model(xb, ab), yb)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), p["grad_clip"])
            opt.step()
            tot += float(loss.detach())
        sched.step()
        if (ep + 1) % max(1, epochs // 5) == 0 or ep == epochs - 1:
            print(f"[{tag} {ep+1:04d}/{epochs}] mse={tot/max(1,(n+bs-1)//bs):.4e}", flush=True)


@torch.no_grad()
def _member_fields(model, X, scaler, device, bs):
    model.eval()
    out = []
    for i in range(0, X.shape[0], bs):
        xb = torch.from_numpy(X[i:i + bs]).float().to(device)
        out.append((model(xb) * scaler).cpu().numpy())
    return np.concatenate(out, 0).astype(np.float32)


def _lf_summaries(members, X, s_lf, device, bs, quantiles):
    preds = np.stack([_member_fields(m, X, s_lf, device, bs) for m in members], 0)
    mu = preds.mean(0); var = preds.var(0); sigma = np.sqrt(var + 1e-12)
    qs = [np.quantile(preds, q, axis=0) for q in quantiles]
    aug = np.stack([c / s_lf for c in ([mu, sigma] + qs)], axis=1).astype(np.float32)
    return aug


@torch.no_grad()
def _gated_predict(model, X, aug, scaler, device, bs):
    model.eval()
    out = []
    for i in range(0, X.shape[0], bs):
        xb = torch.from_numpy(X[i:i + bs]).float().to(device)
        ab = torch.from_numpy(aug[i:i + bs]).float().to(device)
        out.append((model(xb, ab) * scaler).reshape(xb.shape[0], -1).cpu().numpy())
    return np.concatenate(out, 0).astype(np.float64)


def run(args, out_path: Path) -> dict:
    torch.manual_seed(args.seed); np.random.seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    p = SMOKE
    E = int(p["ensemble"]); quants = p["quantiles"]; gates = _parse_gates()
    ds_dir = Path(args.dataset_dir)
    train = load_mf_dataset(ds_dir, "train"); test = load_mf_dataset(ds_dir, "test")
    hf = train["hf_fid"]; lf = min(train["lf_fids"]) if train["lf_fids"] else hf
    if hf not in test["fids"]:
        hf = test["hf_fid"]

    hf_native = resolve_grid(args.dataset_name, int(train["n_cells_by_fid"][hf]))
    lf_native = resolve_grid(args.dataset_name, int(train["n_cells_by_fid"][lf]))
    grid = _cap_grid(hf_native); mh, mw = _modes(grid, p["modes_cap"])

    X_lf = train["cond_by_fid"][lf].astype(np.float32)
    Y_lf = _to_grid(train["field_by_fid"][lf], lf_native, grid, args.dataset_name)
    X_hf = train["cond_by_fid"][hf].astype(np.float32)
    Y_hf = _to_grid(train["field_by_fid"][hf], hf_native, grid, args.dataset_name)
    X_te = test["cond_by_fid"][hf].astype(np.float32)
    Y_te = _to_grid(test["field_by_fid"][hf], hf_native, grid, args.dataset_name)
    cond_dim = int(X_hf.shape[1])
    scaler_lf = max(float(np.abs(Y_lf).max()), 1e-8) if Y_lf.size else 1.0
    scaler_hf = max(float(np.abs(Y_hf).max()), 1e-8) if Y_hf.size else 1.0

    print(f"[data] {args.dataset_name} LF={lf} HF={hf} work_grid={grid} E={E} "
          f"gates={sorted(gates)} N_lf={X_lf.shape[0]} N_hf={X_hf.shape[0]} "
          f"N_test={X_te.shape[0]}", flush=True)

    members = [FNO2d(cond_dim, p["lf_hidden"], p["n_blocks"], mh, mw, grid).to(device)
               for _ in range(E)]
    net = DGTransferFNO(cond_dim, AUG_CH, p["gate_ch"], p["hidden_channels"], p["n_blocks"],
                        mh, mw, grid, gates=gates).to(device)
    n_params = sum(param_count(m) for m in members) + param_count(net)

    ckpt_dir = Path(args.ckpt_dir); ckpt_dir.mkdir(parents=True, exist_ok=True)
    last = ckpt_dir / "last.pt"
    trained = False
    if last.exists():
        try:
            sd = torch.load(last, map_location=device, weights_only=False)
            if sd.get("epochs_target") == args.epochs and sd.get("grid") == list(grid) \
               and sd.get("ensemble") == E and sd.get("gates") == sorted(gates):
                for m, msd in zip(members, sd["members"]):
                    m.load_state_dict(msd)
                net.load_state_dict(sd["net"]); trained = True
                print("[resume] loaded", flush=True)
        except Exception as e:
            print(f"[resume] failed ({e})", flush=True)

    t_train = time.time()
    if not trained:
        # 0) small LF ensemble for the uncertainty fields
        for i, m in enumerate(members):
            print(f"[stage0] train LF member {i + 1}/{E}", flush=True)
            _train_lf(m, X_lf, Y_lf, scaler_lf, args.epochs, p["lr_pretrain"], p,
                      device, seed=args.seed + 1 + i)
        aug_lf = _lf_summaries(members, X_lf, scaler_lf, device, p["batch_size"], quants)
        aug_hf = _lf_summaries(members, X_hf, scaler_lf, device, p["batch_size"], quants)
        # 1) PRETRAIN gated net on LF (per-stage scaler_lf)
        print(f"[stage1] pretrain gated net on LF ({X_lf.shape[0]})", flush=True)
        _train_gated(net, X_lf, aug_lf, Y_lf, scaler_lf, args.epochs, p["lr_pretrain"], p,
                     device, "LF-pretrain")
        # 2) FINE-TUNE on HF (per-stage scaler_hf, lower LR)
        print(f"[stage2] fine-tune gated net on HF ({X_hf.shape[0]})", flush=True)
        _train_gated(net, X_hf, aug_hf, Y_hf, scaler_hf, args.epochs, p["lr_finetune"], p,
                     device, "HF-finetune")
        torch.save({"epochs_target": args.epochs, "grid": list(grid), "ensemble": E,
                    "gates": sorted(gates), "members": [m.state_dict() for m in members],
                    "net": net.state_dict()}, last)
    train_seconds = time.time() - t_train

    # eval
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize()
    t_eval = time.time()
    aug_te = _lf_summaries(members, X_te, scaler_lf, device, p["batch_size"], quants)
    pred = _gated_predict(net, X_te, aug_te, scaler_hf, device, p["batch_size"])
    if device.type == "cuda":
        torch.cuda.synchronize()
    eval_seconds = time.time() - t_eval
    target = Y_te.reshape(Y_te.shape[0], -1).astype(np.float64)
    n = int(target.shape[0])
    latency = (1000.0 * eval_seconds / max(n, 1)) if device.type == "cuda" else None
    peak = (torch.cuda.max_memory_allocated() / 1e6) if device.type == "cuda" else None

    return finalize_and_write(
        out_path=out_path, model="dg_transfer", dataset=args.dataset_name,
        pred=pred, target=target, work_grid=grid, n_params=int(n_params),
        train_seconds=train_seconds, eval_seconds=eval_seconds,
        latency_ms_per_sample=latency, peak_mem_mb=peak, seed=args.seed,
        extra={"device": str(device), "hf_fidelity": int(hf), "lf_fidelity": int(lf),
               "mf_mechanism": "transfer_LFpretrain_HFfinetune + discrepancy-gated FiLM (A,B)",
               "ensemble_size": E, "lf_hidden": p["lf_hidden"], "gates": sorted(gates),
               "aug_channels": ["mu", "sigma", "q10", "q50", "q90"], "work_grid": list(grid)},
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
