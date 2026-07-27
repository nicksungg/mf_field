"""Smoke + fair-eval for mf_fno_residfid (B5).

PDE-residual self-supervised auxiliary loss. Same transfer schedule and
FiLM-on-X backbone as the winner, but the training loss gains a weak physical
prior:

    loss = MSE(pred, target) + lambda * mean( ||Δu||^2 )

where Δu is the interior finite-difference Laplacian of the (de-normalized)
prediction, computed with a fixed 5-point conv stencil. This is a SMOOTHNESS
residual — a deliberately weak, dataset-agnostic placeholder for the true PDE
operator R(u) (which would be the actual governing equation). It nudges
predictions toward interior smoothness without any extra labels. Applied to the
HF stage (and optionally the LF stage via --resid_on_lf).

`extra` reports the loss weight `lambda` and the final mean residual magnitude
on the HF train set (data-loss-only vs residual-augmented, for reference).

Contract: --dataset_dir --dataset_name --epochs --out --ckpt_dir --seed
          [--resid_weight FLOAT] [--resid_on_lf].
Resume: ckpt_dir/last.pt keyed on (epochs_target, grid, resid_weight, resid_on_lf).
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
                         SMOKE, _cap_grid, _modes, _to_grid)
from model import FNO2d, param_count  # noqa: E402

DEFAULT_RESID_WEIGHT = 1e-3


def _laplacian_kernel(device):
    # 5-point interior Laplacian stencil (Δu), as a (1,1,3,3) conv weight.
    k = torch.tensor([[0., 1., 0.], [1., -4., 1.], [0., 1., 0.]], device=device)
    return k.view(1, 1, 3, 3)


def laplacian_residual(field_bhw, kernel):
    """mean ||Δu||^2 over interior points. field_bhw: (B,H,W) de-normalized."""
    if field_bhw.dim() == 2 or field_bhw.shape[-1] < 3 or field_bhw.shape[-2] < 3:
        return field_bhw.new_zeros(())
    u = field_bhw.unsqueeze(1)                      # (B,1,H,W)
    lap = F.conv2d(u, kernel)                       # valid -> interior only
    return (lap ** 2).mean()


def train_resid(model, X, Y, scaler, epochs, lr, p, device, tag, resid_weight, kernel):
    """Train with data MSE + resid_weight * mean||Δ(pred*scaler)||^2.

    Returns the mean residual magnitude over the last epoch (raw units).
    """
    if X.shape[0] == 0 or epochs <= 0:
        return 0.0
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=p["weight_decay"])
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(epochs, 1), eta_min=1e-6)
    Xt = torch.from_numpy(X).float()
    Yt = torch.from_numpy(Y).float() / scaler
    n = X.shape[0]
    bs = min(p["batch_size"], n)
    g = torch.Generator().manual_seed(0)
    last_resid = 0.0
    for ep in range(epochs):
        model.train()
        perm = torch.randperm(n, generator=g)
        tot = 0.0; rtot = 0.0; nb = 0
        for i in range(0, n, bs):
            idx = perm[i:i + bs]
            xb = Xt[idx].to(device); yb = Yt[idx].to(device)
            opt.zero_grad(set_to_none=True)
            pred = model(xb)
            data_loss = F.mse_loss(pred, yb)
            # residual on de-normalized field (raw physical units)
            resid = laplacian_residual(pred * scaler, kernel)
            loss = data_loss + resid_weight * resid
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), p["grad_clip"])
            opt.step()
            tot += float(data_loss.detach()); rtot += float(resid.detach()); nb += 1
        sched.step()
        last_resid = rtot / max(nb, 1)
        if (ep + 1) % max(1, epochs // 5) == 0 or ep == epochs - 1:
            print(f"[{tag} {ep+1:04d}/{epochs}] data_mse={tot/max(nb,1):.4e} "
                  f"resid={last_resid:.4e}", flush=True)
    return last_resid


def run(args, out_path: Path) -> dict:
    torch.manual_seed(args.seed); np.random.seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    p = SMOKE
    ds_dir = Path(args.dataset_dir)
    resid_weight = float(args.resid_weight)
    resid_on_lf = bool(args.resid_on_lf)

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
          f"resid_weight={resid_weight} resid_on_lf={resid_on_lf}", flush=True)

    model = FNO2d(cond_dim, hidden_channels=p["hidden_channels"], n_blocks=p["n_blocks"],
                  modes_h=modes_h, modes_w=modes_w, grid=grid).to(device)
    n_params = param_count(model)
    kernel = _laplacian_kernel(device)

    ckpt_dir = Path(args.ckpt_dir); ckpt_dir.mkdir(parents=True, exist_ok=True)
    last = ckpt_dir / "last.pt"
    trained = False; final_resid = None
    if last.exists():
        try:
            sd = torch.load(last, map_location=device, weights_only=False)
            if (sd.get("epochs_target") == args.epochs and sd.get("grid") == list(grid)
                    and sd.get("resid_weight") == resid_weight
                    and sd.get("resid_on_lf") == resid_on_lf):
                model.load_state_dict(sd["model"]); trained = True
                final_resid = sd.get("final_resid")
                print("[resume] loaded finished checkpoint", flush=True)
        except Exception as e:
            print(f"[resume] failed ({e}); fresh", flush=True)

    t_train = time.time()
    if not trained:
        print(f"[stage] pretrain on LF ({X_lf.shape[0]} samples)", flush=True)
        lf_w = resid_weight if resid_on_lf else 0.0
        train_resid(model, X_lf, Y_lf, scaler_lf, args.epochs, p["lr_pretrain"], p, device,
                    "LF-pretrain", lf_w, kernel)
        print(f"[stage] fine-tune on HF ({X_hf.shape[0]} samples)", flush=True)
        final_resid = train_resid(model, X_hf, Y_hf, scaler_hf, args.epochs, p["lr_finetune"],
                                  p, device, "HF-finetune", resid_weight, kernel)
        torch.save({"epochs_target": args.epochs, "grid": list(grid),
                    "resid_weight": resid_weight, "resid_on_lf": resid_on_lf,
                    "final_resid": float(final_resid), "model": model.state_dict()}, last)
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

    # report residual magnitude of the predictions on the test set (raw units)
    with torch.no_grad():
        pt = torch.from_numpy(pred.astype(np.float32)).view(-1, grid[0], grid[1]).to(device)
        test_resid = float(laplacian_residual(pt, kernel).item())
    print(f"[resid] final_train_resid={final_resid} test_pred_resid={test_resid:.4e}", flush=True)

    n_samples = int(target.shape[0])
    latency = (1000.0 * eval_seconds / max(n_samples, 1)) if device.type == "cuda" else None
    peak_mem = (torch.cuda.max_memory_allocated() / 1e6) if device.type == "cuda" else None

    return finalize_and_write(
        out_path=out_path, model="mf_fno_residfid", dataset=args.dataset_name,
        pred=pred, target=target, work_grid=grid, n_params=int(n_params),
        train_seconds=train_seconds, eval_seconds=eval_seconds,
        latency_ms_per_sample=latency, peak_mem_mb=peak_mem, seed=args.seed,
        extra={"device": str(device), "hf_fidelity": int(hf), "lf_fidelity": int(lf),
               "mf_mechanism": "transfer_LF_pretrain_HF_finetune",
               "conditioning": "film_on_X_per_block",
               "aux_loss": "laplacian_smoothness_residual_placeholder_for_true_PDE_operator",
               "resid_weight": float(resid_weight), "resid_on_lf": bool(resid_on_lf),
               "final_train_resid_magnitude": (float(final_resid) if final_resid is not None else None),
               "test_pred_resid_magnitude": test_resid,
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
    ap.add_argument("--resid_weight", type=float, default=DEFAULT_RESID_WEIGHT)
    ap.add_argument("--resid_on_lf", action="store_true",
                    help="also apply the residual auxiliary loss during LF pretrain")
    args = ap.parse_args()
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    res = run(args, out)
    print(f"[wrote] {out}", flush=True)
    print(f"[nRMSE] {res['splits']['test_hf']['nRMSE']:.6f}", flush=True)


if __name__ == "__main__":
    main()
