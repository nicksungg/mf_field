"""Smoke + fair-eval for mf_fno_lora (A4).

Fidelity-conditioned LoRA-adapted MF-FNO. Same FiLM-on-X FNO backbone as the
winner, but HF adaptation is PARAMETER-EFFICIENT:

  1. LF-pretrain the FULL backbone (abundant low-fidelity data).
  2. FREEZE the backbone; inject zero-init LoRA adapters into every 1x1 Conv2d
     (block w, lift, proj) and the FiLM-MLP Linears.
  3. HF-finetune ONLY the adapters (lower LR).

Because B is zero-init, the adapted model BEFORE HF-finetune == the LF-pretrained
model (exact reduction); we measure pre- vs post-finetune HF nRMSE to confirm the
adapters improve HF. `extra` reports adapter_params, adapter_norm (LF->HF-gap
proxy), and the % of params trained.

Contract: --dataset_dir --dataset_name --epochs --out --ckpt_dir --seed
          [--rank R] [--no_adapt_film].
Resume: ckpt_dir/last.pt keyed on (epochs_target, grid, rank, adapt_film).
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

from common.backbone import FNO2d, param_count  # noqa: E402
from common.mffp import (load_mf_dataset, resolve_grid, finalize_and_write,  # noqa: E402
                         SMOKE, _cap_grid, _modes, _to_grid, train_loop)
from model import inject_lora, adapter_l2_norm  # noqa: E402


def _eval_nrmse(model, X, Y_grid, scaler, device, bs):
    """Aggregate nRMSE on (X, Y_grid) with de-normalized predictions."""
    model.eval()
    preds = []
    with torch.no_grad():
        for i in range(0, X.shape[0], bs):
            xb = torch.from_numpy(X[i:i + bs]).float().to(device)
            pr = model(xb) * scaler
            preds.append(pr.reshape(pr.shape[0], -1).cpu().numpy())
    p = np.concatenate(preds, 0).astype(np.float64)
    t = Y_grid.reshape(Y_grid.shape[0], -1).astype(np.float64)
    return float(np.sqrt(((p - t) ** 2).sum() / max((t ** 2).sum(), 1e-12)))


def _train_adapters(model, adapters, X, Y, scaler, epochs, lr, p, device, tag):
    """Train ONLY `adapters` on (X cond, Y/scaler). Backbone stays frozen."""
    if X.shape[0] == 0 or epochs <= 0:
        return
    opt = torch.optim.AdamW(adapters, lr=lr, weight_decay=p["weight_decay"])
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
            torch.nn.utils.clip_grad_norm_(adapters, p["grad_clip"])
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
    adapt_film = not args.no_adapt_film

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

    model = FNO2d(cond_dim, hidden_channels=p["hidden_channels"], n_blocks=p["n_blocks"],
                  modes_h=modes_h, modes_w=modes_w, grid=grid).to(device)
    n_params_backbone = param_count(model)

    print(f"[data] {args.dataset_name} loader={train['loader']} LF={lf} HF={hf} "
          f"hf_native={hf_grid_native} work_grid={grid} modes=({modes_h},{modes_w}) "
          f"N_lf={X_lf.shape[0]} N_hf={X_hf.shape[0]} N_test={X_te.shape[0]} cond_dim={cond_dim} "
          f"rank={args.rank} adapt_film={adapt_film}", flush=True)

    # ── resume ──
    ckpt_dir = Path(args.ckpt_dir); ckpt_dir.mkdir(parents=True, exist_ok=True)
    last = ckpt_dir / "last.pt"
    trained = False
    nrmse_pre = None
    sd_cached = None
    if last.exists():
        try:
            sd = torch.load(last, map_location=device, weights_only=False)
            if (sd.get("epochs_target") == args.epochs and sd.get("grid") == list(grid)
                    and sd.get("rank") == args.rank and sd.get("adapt_film") == adapt_film):
                sd_cached = sd
                trained = True
                nrmse_pre = sd.get("nrmse_pre")
                print("[resume] loaded finished checkpoint", flush=True)
        except Exception as e:
            print(f"[resume] failed ({e}); fresh", flush=True)

    t_train = time.time()
    if not trained:
        # 1) LF pretrain — full backbone
        print(f"[stage] LF-pretrain full backbone ({X_lf.shape[0]} samples)", flush=True)
        train_loop(model, X_lf, Y_lf, scaler_lf, args.epochs, p["lr_pretrain"], p, device, "LF-pretrain")
        # 2) inject zero-init LoRA, freeze backbone
        adapters = inject_lora(model, rank=args.rank, alpha=1.0, adapt_film=adapt_film)
        model.to(device)
        # reduction check: pre-finetune HF nRMSE == frozen LF model on HF test
        nrmse_pre = _eval_nrmse(model, X_te, Y_te, scaler_hf, device, p["batch_size"])
        print(f"[reduction] pre-finetune HF nRMSE (== LF-pretrained model) = {nrmse_pre:.6f}", flush=True)
        # 3) HF finetune — adapters only
        print(f"[stage] HF-finetune adapters only ({X_hf.shape[0]} samples)", flush=True)
        _train_adapters(model, adapters, X_hf, Y_hf, scaler_hf, args.epochs,
                        p["lr_finetune"], p, device, "HF-finetune")
        torch.save({"epochs_target": args.epochs, "grid": list(grid),
                    "rank": args.rank, "adapt_film": adapt_film,
                    "model": model.state_dict(), "nrmse_pre": nrmse_pre}, last)
    else:
        # rebuild adapter-wrapped graph, then load the finished state_dict
        adapters = inject_lora(model, rank=args.rank, alpha=1.0, adapt_film=adapt_film)
        model.to(device)
        model.load_state_dict(sd_cached["model"])
    train_seconds = time.time() - t_train

    adapter_params = sum(int(a.numel()) for a in adapters)
    adapter_norm = adapter_l2_norm(adapters)
    total_params = n_params_backbone + adapter_params
    pct_trained = 100.0 * adapter_params / max(total_params, 1)

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
    nrmse_post = float(np.sqrt(((pred - target) ** 2).sum() / max((target ** 2).sum(), 1e-12)))
    latency = (1000.0 * eval_seconds / max(n_samples, 1)) if device.type == "cuda" else None
    peak_mem = (torch.cuda.max_memory_allocated() / 1e6) if device.type == "cuda" else None

    improved = (nrmse_pre is None) or (nrmse_post <= nrmse_pre)
    print(f"[reduction] HF nRMSE pre={nrmse_pre} post={nrmse_post:.6f} improved={improved}", flush=True)

    res = finalize_and_write(
        out_path=out_path, model="mf_fno_lora", dataset=args.dataset_name,
        pred=pred, target=target, work_grid=grid, n_params=int(total_params),
        train_seconds=train_seconds, eval_seconds=eval_seconds,
        latency_ms_per_sample=latency, peak_mem_mb=peak_mem, seed=args.seed,
        extra={"device": str(device), "hf_fidelity": int(hf), "lf_fidelity": int(lf),
               "mf_mechanism": "transfer_LF_pretrain_HF_finetune_LoRA_adapters",
               "conditioning": "film_on_X_per_block",
               "rank": int(args.rank), "adapt_film": bool(adapt_film),
               "adapter_params": int(adapter_params),
               "adapter_norm": float(adapter_norm),
               "backbone_params": int(n_params_backbone),
               "pct_params_trained": float(pct_trained),
               "hf_nrmse_pre_finetune": (None if nrmse_pre is None else float(nrmse_pre)),
               "hf_nrmse_post_finetune": float(nrmse_post),
               "finetune_improved_hf": bool(improved),
               "cond_dim": cond_dim,
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
    ap.add_argument("--rank", type=int, default=4)
    ap.add_argument("--no_adapt_film", action="store_true",
                    help="adapt only the 1x1 convs, not the FiLM MLPs")
    args = ap.parse_args()
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    res = run(args, out)
    print(f"[wrote] {out}", flush=True)
    print(f"[nRMSE] {res['splits']['test_hf']['nRMSE']:.6f}", flush=True)


if __name__ == "__main__":
    main()
