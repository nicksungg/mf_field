"""Smoke + fair-eval for mf_fno_incontext (B2).

In-context operator learning, NO fine-tune. A DeepSets encoder turns a few
support pairs (X_i, Y_i) into a task context c; the FNO FiLMs on [X_query, c].

Episodic training on LF: each step samples a support subset + a disjoint query
subset from the LF data, builds c from the support fields, and supervises the
query predictions (the model learns to READ examples). At eval the HF TRAIN pairs
are the support prompt and HF TEST inputs are the queries — HF transfer happens
in-context, the weights are NEVER updated on HF.

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

from common.mffp import (load_mf_dataset, resolve_grid, finalize_and_write,  # noqa: E402
                         SMOKE, _cap_grid, _modes, _to_grid)
from model import (InContextFNO, DeepSetsContext, field_summary, SUMMARY_DIM,  # noqa: E402
                   param_count)

CTX_DIM = 16
MAX_SUPPORT = 32   # support prompt size per episode / at eval


def build_context(ctx_enc, Xt, Yt, device):
    """c = DeepSets({ concat(X_i, field_summary(Y_i)) }). Xt:(S,d) Yt:(S,H,W)."""
    if Xt.shape[0] == 0:
        return torch.zeros(ctx_enc.ctx_dim, device=device)
    summ = field_summary(Yt)                       # (S, SUMMARY_DIM)
    support = torch.cat([Xt, summ], dim=-1)
    return ctx_enc(support)


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
    # single shared scaler: in-context model never re-fits at HF, so support and
    # query must live in the same output space. Use the LF training scale.
    scaler = max(float(np.abs(Y_lf).max()), float(np.abs(Y_hf).max()), 1e-8)

    print(f"[data] {args.dataset_name} loader={train['loader']} LF={lf} HF={hf} "
          f"hf_native={hf_grid_native} work_grid={grid} modes=({modes_h},{modes_w}) "
          f"N_lf={X_lf.shape[0]} N_hf={X_hf.shape[0]} N_test={X_te.shape[0]} cond_dim={cond_dim} "
          f"ctx_dim={CTX_DIM} max_support={MAX_SUPPORT}", flush=True)

    model = InContextFNO(cond_dim, ctx_dim=CTX_DIM, hidden_channels=p["hidden_channels"],
                         n_blocks=p["n_blocks"], modes_h=modes_h, modes_w=modes_w,
                         grid=grid).to(device)
    ctx_enc = DeepSetsContext(cond_dim + SUMMARY_DIM, hidden=64, ctx_dim=CTX_DIM).to(device)
    n_params = param_count(model) + param_count(ctx_enc)

    ckpt_dir = Path(args.ckpt_dir); ckpt_dir.mkdir(parents=True, exist_ok=True)
    last = ckpt_dir / "last.pt"
    trained = False
    if last.exists():
        try:
            sd = torch.load(last, map_location=device, weights_only=False)
            if sd.get("epochs_target") == args.epochs and sd.get("grid") == list(grid):
                model.load_state_dict(sd["model"]); ctx_enc.load_state_dict(sd["ctx_enc"])
                trained = True
                print("[resume] loaded finished checkpoint", flush=True)
        except Exception as e:
            print(f"[resume] failed ({e}); fresh", flush=True)

    t_train = time.time()
    if not trained:
        # episodic training on LF: sample support + disjoint query each step
        params = list(model.parameters()) + list(ctx_enc.parameters())
        opt = torch.optim.AdamW(params, lr=p["lr_pretrain"], weight_decay=p["weight_decay"])
        sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(args.epochs, 1), eta_min=1e-6)
        Xlf = torch.from_numpy(X_lf).float()
        Ylf = torch.from_numpy(Y_lf).float() / scaler
        n = X_lf.shape[0]
        q_bs = min(p["batch_size"], max(n // 2, 1))
        g = torch.Generator().manual_seed(0)
        print(f"[stage] episodic in-context training on LF ({n} samples)", flush=True)
        for ep in range(args.epochs):
            model.train(); ctx_enc.train()
            perm = torch.randperm(n, generator=g)
            tot = 0.0; nb = 0
            # several episodes per epoch
            n_ep = max(1, n // (q_bs + 1))
            for _ in range(n_ep):
                sup_n = min(MAX_SUPPORT, max(1, n // 2))
                idx = torch.randperm(n, generator=g)
                sup_idx = idx[:sup_n]; qry_idx = idx[sup_n:sup_n + q_bs]
                if qry_idx.numel() == 0:
                    qry_idx = idx[:q_bs]
                Xs = Xlf[sup_idx].to(device); Ys = Ylf[sup_idx].to(device)
                Xq = Xlf[qry_idx].to(device); Yq = Ylf[qry_idx].to(device)
                opt.zero_grad(set_to_none=True)
                ctx = build_context(ctx_enc, Xs, Ys, device)
                pred = model(Xq, ctx)
                loss = F.mse_loss(pred, Yq)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(params, p["grad_clip"])
                opt.step()
                tot += float(loss.detach()); nb += 1
            sched.step()
            if (ep + 1) % max(1, args.epochs // 5) == 0 or ep == args.epochs - 1:
                print(f"[episodic {ep+1:04d}/{args.epochs}] mse={tot/max(nb,1):.4e}", flush=True)
        torch.save({"epochs_target": args.epochs, "grid": list(grid),
                    "model": model.state_dict(), "ctx_enc": ctx_enc.state_dict()}, last)
    train_seconds = time.time() - t_train

    # ── eval: HF train pairs = support prompt; HF test inputs = queries (no finetune)
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize()
    model.eval(); ctx_enc.eval()
    with torch.no_grad():
        sup_n = min(MAX_SUPPORT, X_hf.shape[0])
        Xs = torch.from_numpy(X_hf[:sup_n]).float().to(device)
        Ys = torch.from_numpy(Y_hf[:sup_n]).float().to(device) / scaler
        eval_ctx = build_context(ctx_enc, Xs, Ys, device)
    t_eval = time.time()
    preds = []
    bs = p["batch_size"]
    with torch.no_grad():
        for i in range(0, X_te.shape[0], bs):
            xb = torch.from_numpy(X_te[i:i + bs]).float().to(device)
            pr = model(xb, eval_ctx) * scaler
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
        out_path=out_path, model="mf_fno_incontext", dataset=args.dataset_name,
        pred=pred, target=target, work_grid=grid, n_params=int(n_params),
        train_seconds=train_seconds, eval_seconds=eval_seconds,
        latency_ms_per_sample=latency, peak_mem_mb=peak_mem, seed=args.seed,
        extra={"device": str(device), "hf_fidelity": int(hf), "lf_fidelity": int(lf),
               "mf_mechanism": "in_context_no_finetune_HF_train_pairs_as_support_prompt",
               "conditioning": "film_on_[X_query, deepsets_support_context]",
               "ctx_dim": int(CTX_DIM), "support_size": int(min(MAX_SUPPORT, X_hf.shape[0])),
               "summary_dim": int(SUMMARY_DIM),
               "note": "episodic training on LF only; HF reached purely in-context (no HF gradient steps).",
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
