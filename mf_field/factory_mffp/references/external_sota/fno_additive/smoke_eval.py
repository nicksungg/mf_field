"""Additive discrepancy correction (FNO backbone).

Survey family 1 (Peherstorfer et al., "Survey of Multifidelity Methods"): the
cleanest residual / delta-learning formulation.

    HF(x) ≈ LF_pred(x) + δ(x)

Two FNOs on the SAME geometry-general backbone as mf_fno_transfer:
  1. FNO_LF: trained on the abundant low-fidelity data (cond -> LF field).
  2. FNO_δ : trained on the scarce high-fidelity data to predict the RESIDUAL
            HF - FNO_LF(x)  (FNO_LF frozen). Final pred = FNO_LF(x) + FNO_δ(x).

Difference vs mf_fno_transfer (transfer/parameter-reuse): there it is ONE network
warm-started then fine-tuned; here there are TWO networks and the HF one learns an
explicit additive correction on the LF prediction's output. Difference vs
fno_mf_stack: stack uses N coarse per-fidelity FNOs + an MLP aggregator; this is the
pure 2-fidelity additive rule with both FNOs at the full working resolution.

Shares the verified plumbing (resolve_grid + 256-cap working grid, full-field eval,
finalize_and_write per-sample rel-L2 + bootstrap CI). Contract + resume identical.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent.parent
sys.path.insert(0, str(HERE))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model import FNO2d, param_count  # noqa: E402
from data_adapters import load_mf_dataset  # noqa: E402
from data_adapters.geometry import resolve_grid  # noqa: E402
from data_adapters.metrics import finalize_and_write  # noqa: E402

WORK_CAP = 256
SMOKE = dict(hidden_channels=64, n_blocks=4, modes_cap=12, batch_size=16,
             lr=1e-3, weight_decay=1e-5, grad_clip=1.0)


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


def _train(model, X, Y, scaler, epochs, lr, p, device, tag, target_field=None):
    """Train model(cond) -> field/scaler. If target_field given (the residual),
    supervise on that instead of Y (used for the delta network)."""
    if X.shape[0] == 0 or epochs <= 0:
        return
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=p["weight_decay"])
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(epochs, 1), eta_min=1e-6)
    Xt = torch.from_numpy(X).float()
    tgt = target_field if target_field is not None else Y
    Yt = torch.from_numpy(tgt).float() / scaler
    n = X.shape[0]; bs = min(p["batch_size"], n)
    g = torch.Generator().manual_seed(0)
    for ep in range(epochs):
        model.train()
        perm = torch.randperm(n, generator=g)
        for i in range(0, n, bs):
            idx = perm[i:i + bs]
            xb = Xt[idx].to(device); yb = Yt[idx].to(device)
            opt.zero_grad(set_to_none=True)
            loss = F.mse_loss(model(xb), yb)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), p["grad_clip"])
            opt.step()
        sched.step()


@torch.no_grad()
def _predict_field(model, X, scaler, device, bs):
    """Return raw-units field predictions (N, H, W) for cond X."""
    model.eval()
    out = []
    for i in range(0, X.shape[0], bs):
        xb = torch.from_numpy(X[i:i + bs]).float().to(device)
        out.append((model(xb) * scaler).cpu().numpy())
    return np.concatenate(out, 0).astype(np.float32)


def run(args, out_path: Path) -> dict:
    torch.manual_seed(args.seed); np.random.seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    p = SMOKE
    ds_dir = Path(args.dataset_dir)
    train = load_mf_dataset(ds_dir, "train"); test = load_mf_dataset(ds_dir, "test")
    hf = train["hf_fid"]; lf = min(train["lf_fids"]) if train["lf_fids"] else hf
    if hf not in test["fids"]:
        hf = test["hf_fid"]

    hf_native = resolve_grid(args.dataset_name, int(train["n_cells_by_fid"][hf]))
    lf_native = resolve_grid(args.dataset_name, int(train["n_cells_by_fid"][lf]))
    grid = _cap_grid(hf_native); mh, mw = _modes(grid, p["modes_cap"])

    X_lf = train["cond_by_fid"][lf].astype(np.float32)
    Y_lf = _to_grid(train["field_by_fid"][lf], lf_native, grid)
    X_hf = train["cond_by_fid"][hf].astype(np.float32)
    Y_hf = _to_grid(train["field_by_fid"][hf], hf_native, grid)
    X_te = test["cond_by_fid"][hf].astype(np.float32)
    Y_te = _to_grid(test["field_by_fid"][hf], hf_native, grid)
    cond_dim = int(X_hf.shape[1])
    s_lf = max(float(np.abs(Y_lf).max()), 1e-8) if Y_lf.size else 1.0
    s_hf = max(float(np.abs(Y_hf).max()), 1e-8) if Y_hf.size else 1.0

    print(f"[data] {args.dataset_name} LF={lf} HF={hf} work_grid={grid} "
          f"N_lf={X_lf.shape[0]} N_hf={X_hf.shape[0]} N_test={X_te.shape[0]}", flush=True)

    fno_lf = FNO2d(cond_dim, p["hidden_channels"], p["n_blocks"], mh, mw, grid).to(device)
    fno_d = FNO2d(cond_dim, p["hidden_channels"], p["n_blocks"], mh, mw, grid).to(device)
    n_params = param_count(fno_lf) + param_count(fno_d)

    ckpt_dir = Path(args.ckpt_dir); ckpt_dir.mkdir(parents=True, exist_ok=True)
    last = ckpt_dir / "last.pt"
    trained = False
    res_scaler = s_hf
    if last.exists():
        try:
            sd = torch.load(last, map_location=device, weights_only=False)
            if sd.get("epochs_target") == args.epochs and sd.get("grid") == list(grid):
                fno_lf.load_state_dict(sd["fno_lf"]); fno_d.load_state_dict(sd["fno_d"])
                res_scaler = sd.get("res_scaler", s_hf); trained = True
                print("[resume] loaded", flush=True)
        except Exception as e:
            print(f"[resume] failed ({e})", flush=True)

    t_train = time.time()
    if not trained:
        # 1) LF model on abundant LF data
        print("[stage] train FNO_LF on LF", flush=True)
        _train(fno_lf, X_lf, Y_lf, s_lf, args.epochs, p["lr"], p, device, "LF")
        # 2) residual target on HF samples: HF - LF_pred(x_hf)
        lf_on_hf = _predict_field(fno_lf, X_hf, s_lf, device, p["batch_size"])  # raw units
        residual = (Y_hf - lf_on_hf).astype(np.float32)
        res_scaler = max(float(np.abs(residual).max()), 1e-8) if residual.size else 1.0
        print("[stage] train FNO_delta on (HF - LF_pred)", flush=True)
        _train(fno_d, X_hf, None, res_scaler, args.epochs, p["lr"], p, device, "delta",
               target_field=residual)
        torch.save({"epochs_target": args.epochs, "grid": list(grid),
                    "fno_lf": fno_lf.state_dict(), "fno_d": fno_d.state_dict(),
                    "res_scaler": res_scaler}, last)
    train_seconds = time.time() - t_train

    # eval: HF ≈ LF_pred + delta
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize()
    t_eval = time.time()
    lf_te = _predict_field(fno_lf, X_te, s_lf, device, p["batch_size"])
    d_te = _predict_field(fno_d, X_te, res_scaler, device, p["batch_size"])
    pred = (lf_te + d_te).reshape(X_te.shape[0], -1).astype(np.float64)
    if device.type == "cuda":
        torch.cuda.synchronize()
    eval_seconds = time.time() - t_eval
    target = Y_te.reshape(Y_te.shape[0], -1).astype(np.float64)
    n = int(target.shape[0])
    latency = (1000.0 * eval_seconds / max(n, 1)) if device.type == "cuda" else None
    peak = (torch.cuda.max_memory_allocated() / 1e6) if device.type == "cuda" else None

    return finalize_and_write(
        out_path=out_path, model="fno_additive", dataset=args.dataset_name,
        pred=pred, target=target, work_grid=grid, n_params=int(n_params),
        train_seconds=train_seconds, eval_seconds=eval_seconds,
        latency_ms_per_sample=latency, peak_mem_mb=peak, seed=args.seed,
        extra={"device": str(device), "hf_fidelity": int(hf), "lf_fidelity": int(lf),
               "mf_mechanism": "additive_discrepancy_HF=LFpred+delta",
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
