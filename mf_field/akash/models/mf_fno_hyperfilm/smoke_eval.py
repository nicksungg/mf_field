"""Smoke + fair-eval for mf_fno_hyperfilm (S1).

Generalizes the conditioning SOURCE of the FiLM winner: each FNO block FiLMs on
[X, c, f] where c is a DeepSets task-context from the HF train support set and f
is a normalized fidelity scalar (LF stage=0, HF stage=1).

Schedule (same as winner): LF-pretrain (f=0) -> HF-finetune (f=1). The task
context c is computed once from the HF train (X, field_summary(Y)) support set
before fine-tuning and reused for every query at eval. During LF pretrain we
compute c from the LF support set (its own fields), so the network always sees a
real, stage-consistent context.

--null sets use_context=False, use_fidelity=False, reducing the model to
FiLM-on-X (the winner). The smoke run reports BOTH null and full nRMSE.

Contract: --dataset_dir --dataset_name --epochs --out --ckpt_dir --seed [--null].
Resume: ckpt_dir/last.pt keyed on (epochs_target, grid, mode).
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

AKASH = Path(__file__).resolve().parents[2]            # …/mf_field/akash
sys.path.insert(0, str(AKASH))
sys.path.insert(0, str(Path(__file__).resolve().parent))   # local model.py

from common.backbone import param_count  # noqa: E402
from common.mffp import (load_mf_dataset, resolve_grid, finalize_and_write,  # noqa: E402
                         SMOKE, _cap_grid, _modes, _to_grid)
from model import HyperFiLM_FNO2d, DeepSetsContext, field_summary, SUMMARY_DIM  # noqa: E402

MAX_SUPPORT = 256  # cap support-set size for the DeepSets context (keep cheap)


def compute_context(ctx_enc, X, Y_grid, device, max_support=MAX_SUPPORT):
    """c = DeepSets( {concat(X_i, field_summary(Y_i))} ) over a support subset.

    X: (N, d), Y_grid: (N, H, W). Returns ctx tensor (ctx_dim,) on `device`.
    """
    n = X.shape[0]
    if n == 0:
        return torch.zeros(ctx_enc.ctx_dim, device=device)
    idx = np.arange(n)
    if n > max_support:
        rng = np.random.RandomState(0)
        idx = rng.choice(n, size=max_support, replace=False)
    Xt = torch.from_numpy(X[idx]).float().to(device)
    Yt = torch.from_numpy(Y_grid[idx]).float().to(device)
    summ = field_summary(Yt)                       # (S, SUMMARY_DIM)
    support = torch.cat([Xt, summ], dim=-1)        # (S, d+SUMMARY_DIM)
    return ctx_enc(support)                        # (ctx_dim,)


def train_stage(model, ctx_enc, X, Y, scaler, epochs, lr, p, device, tag,
                fidelity, context_src):
    """Train model+ctx_enc on (X, Y) at a given stage fidelity.

    context_src: (X_ctx, Y_ctx_grid) used to compute c each step (so the DeepSets
    encoder receives gradient), or None to keep c=0.
    """
    if X.shape[0] == 0 or epochs <= 0:
        return
    params = list(model.parameters())
    if model.use_context and context_src is not None:
        params += list(ctx_enc.parameters())
    opt = torch.optim.AdamW(params, lr=lr, weight_decay=p["weight_decay"])
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
        use_ctx = model.use_context and context_src is not None
        for i in range(0, n, bs):
            idx = perm[i:i + bs]
            xb = Xt[idx].to(device); yb = Yt[idx].to(device)
            opt.zero_grad(set_to_none=True)
            # recompute the task context each step so the DeepSets encoder gets a
            # fresh graph (it is a task-level descriptor, same support every time).
            ctx = (compute_context(ctx_enc, context_src[0], context_src[1], device)
                   if use_ctx else None)
            pred = model(xb, context=ctx, fidelity=fidelity)
            loss = F.mse_loss(pred, yb)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(params, p["grad_clip"])
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
    use_context = not args.null
    use_fidelity = not args.null
    mode = "null" if args.null else "full"

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

    # normalized fidelity scalars (log-spaced fids -> [0,1]; LF lowest=0, HF=1)
    fids = train["fids"]
    fmin, fmax = float(min(fids)), float(max(fids))
    def fnorm(fid):
        if fmax == fmin:
            return 1.0
        return (np.log(float(fid)) - np.log(fmin)) / (np.log(fmax) - np.log(fmin))
    f_lf, f_hf = (0.0, 1.0) if use_fidelity else (0.0, 0.0)
    # (stage scalars are LF=0,HF=1 by construction; keep fnorm available for doc)

    print(f"[data] {args.dataset_name} loader={train['loader']} mode={mode} LF={lf} HF={hf} "
          f"hf_native={hf_grid_native} work_grid={grid} modes=({modes_h},{modes_w}) "
          f"N_lf={X_lf.shape[0]} N_hf={X_hf.shape[0]} N_test={X_te.shape[0]} cond_dim={cond_dim} "
          f"f_lf_norm={fnorm(lf):.3f} f_hf_norm={fnorm(hf):.3f}", flush=True)

    model = HyperFiLM_FNO2d(cond_dim, hidden_channels=p["hidden_channels"],
                            n_blocks=p["n_blocks"], modes_h=modes_h, modes_w=modes_w,
                            grid=grid, ctx_dim=16,
                            use_context=use_context, use_fidelity=use_fidelity).to(device)
    elem_dim = cond_dim + SUMMARY_DIM
    ctx_enc = DeepSetsContext(elem_dim, hidden=64, ctx_dim=16).to(device)
    n_params = param_count(model) + (param_count(ctx_enc) if use_context else 0)

    ckpt_dir = Path(args.ckpt_dir); ckpt_dir.mkdir(parents=True, exist_ok=True)
    last = ckpt_dir / "last.pt"
    trained = False
    if last.exists():
        try:
            sd = torch.load(last, map_location=device, weights_only=False)
            if (sd.get("epochs_target") == args.epochs and sd.get("grid") == list(grid)
                    and sd.get("mode") == mode):
                model.load_state_dict(sd["model"])
                if use_context and "ctx_enc" in sd and sd["ctx_enc"] is not None:
                    ctx_enc.load_state_dict(sd["ctx_enc"])
                trained = True
                print("[resume] loaded finished checkpoint", flush=True)
        except Exception as e:
            print(f"[resume] failed ({e}); fresh", flush=True)

    t_train = time.time()
    if not trained:
        # LF pretrain (f=0); context computed from LF support
        print(f"[stage] pretrain on LF ({X_lf.shape[0]} samples) f={f_lf}", flush=True)
        ctx_src_lf = (X_lf, Y_lf) if use_context else None
        train_stage(model, ctx_enc, X_lf, Y_lf, scaler_lf, args.epochs,
                    p["lr_pretrain"], p, device, "LF-pretrain", f_lf, ctx_src_lf)
        # HF finetune (f=1); context computed from HF support
        print(f"[stage] fine-tune on HF ({X_hf.shape[0]} samples) f={f_hf}", flush=True)
        ctx_src_hf = (X_hf, Y_hf) if use_context else None
        train_stage(model, ctx_enc, X_hf, Y_hf, scaler_hf, args.epochs,
                    p["lr_finetune"], p, device, "HF-finetune", f_hf, ctx_src_hf)
        torch.save({"epochs_target": args.epochs, "grid": list(grid), "mode": mode,
                    "model": model.state_dict(),
                    "ctx_enc": ctx_enc.state_dict() if use_context else None}, last)
    train_seconds = time.time() - t_train

    # eval: freeze the HF task context (computed once from HF train support)
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize()
    model.eval(); ctx_enc.eval()
    with torch.no_grad():
        eval_ctx = (compute_context(ctx_enc, X_hf, Y_hf, device)
                    if use_context else None)
    t_eval = time.time()
    preds = []
    bs = p["batch_size"]
    with torch.no_grad():
        for i in range(0, X_te.shape[0], bs):
            xb = torch.from_numpy(X_te[i:i + bs]).float().to(device)
            pr = model(xb, context=eval_ctx, fidelity=f_hf) * scaler_hf
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
        out_path=out_path, model="mf_fno_hyperfilm", dataset=args.dataset_name,
        pred=pred, target=target, work_grid=grid, n_params=int(n_params),
        train_seconds=train_seconds, eval_seconds=eval_seconds,
        latency_ms_per_sample=latency, peak_mem_mb=peak_mem, seed=args.seed,
        extra={"device": str(device), "hf_fidelity": int(hf), "lf_fidelity": int(lf),
               "mf_mechanism": "transfer_LF_pretrain_HF_finetune",
               "conditioning": "film_on_[X,deepsets_context,fidelity]",
               "mode": mode, "use_context": use_context, "use_fidelity": use_fidelity,
               "ctx_dim": 16, "summary_dim": int(SUMMARY_DIM),
               "f_lf_norm": float(fnorm(lf)), "f_hf_norm": float(fnorm(hf)),
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
    ap.add_argument("--null", action="store_true",
                    help="ablation: use_context=False, use_fidelity=False (reduces to FiLM-on-X)")
    args = ap.parse_args()
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    res = run(args, out)
    print(f"[wrote] {out}", flush=True)
    print(f"[nRMSE] {res['splits']['test_hf']['nRMSE']:.6f}", flush=True)


if __name__ == "__main__":
    main()
