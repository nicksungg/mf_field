"""smoke_eval.py — contract entrypoint for fno_mf_stack.

Trains the 4-FNO MFRNP residual stack on one ifc_raw dataset and writes a
contract-compliant JSON to --out.

Loss:
  L_total = sum_k MSE(FNO_k(X), y_k_normalized)          # direct LF supervision
          + MSE(baseline + delta, y_HF_normalized)        # HF residual-stack
          + MSE(baseline, y_HF_normalized)                # aggregator anchor

All LF FNOs contribute gradients via both their direct loss and (indirectly)
the HF residual-stack loss.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from data import build_loaders  # noqa: E402
from model import FNOMFStack, param_count  # noqa: E402


# Smoke config = scaled-down full_config.json (full uses hidden=64).
# Cycle-002 H4 capacity bump: hidden 16→32, modes (4,5,5,5)→(4,8,12,12),
# spectral blocks 2→3. Pre-registered MFRNP Poisson5 knob.
SMOKE_DEFAULTS = dict(
    batch_size=8,
    lr=3e-4,
    weight_decay=1e-5,
    val_frac=0.1,
    hidden=32,
    agg_hidden=32,
    n_blocks=3,
    modes_per_level=(4, 8, 12, 12),
    native_resolutions=(8, 16, 32, 64),
    hf_loss_weight=1.0,
    baseline_anchor_weight=0.5,
    # Cycle-002 H4 per-fidelity loss weights (MFRNP Poisson5_config.yaml).
    # Applied ONLY when dataset_name contains "poisson"; Heat uses uniform.
    poisson_hf_weight=2.0,
    poisson_lf_weight=0.25,
)


def _to_device(t, device):
    return t.to(device, non_blocking=True)


def compute_losses(model, batches_by_level, scaler_tensor, p, device,
                   hf_fid_weight: float = 1.0, lf_fid_weight: float = 1.0):
    """One training step batch composition: take next batch from each level loader.

    hf_fid_weight / lf_fid_weight implement the MFRNP Poisson5 per-fidelity
    weighting (HF=2, LF=0.25 on Poisson; both =1 on Heat). They multiply the
    *normalized* per-fidelity MSE residuals — per-fidelity output normalization
    via `scaler_tensor[k]` is applied to the target before the residual is
    formed, so the weighting acts on already-normalized losses.
    """
    losses = {}
    total = 0.0

    # LF direct losses (fidelity index m < 1 — multiplied by lf_fid_weight)
    n_levels = model.n_levels
    for k in range(n_levels - 1):
        b = batches_by_level[k]
        if b is None:
            continue
        Xs, ys, _li, _m = b
        Xs = _to_device(Xs, device)
        ys = _to_device(ys, device)
        pred_norm = model.lf_predict_native(Xs, level_idx=k)
        target_norm = ys / scaler_tensor[k]
        loss_k = F.mse_loss(pred_norm, target_norm)
        losses[f"lf{k}"] = loss_k.detach().item()
        total = total + lf_fid_weight * loss_k

    # HF residual-stack loss (fidelity index m = 1 — multiplied by hf_fid_weight)
    b_hf = batches_by_level[n_levels - 1]
    if b_hf is not None:
        Xs, ys, _li, m_vals = b_hf
        Xs = _to_device(Xs, device)
        ys = _to_device(ys, device)
        m_t = torch.as_tensor(m_vals, dtype=torch.float32, device=device)
        out = model.hf_predict(Xs, m_t)
        target_norm = ys / scaler_tensor[n_levels - 1]
        loss_hf = F.mse_loss(out["pred"], target_norm)
        loss_base = F.mse_loss(out["baseline"], target_norm)
        losses["hf"] = loss_hf.detach().item()
        losses["hf_base_anchor"] = loss_base.detach().item()
        total = total + hf_fid_weight * (
            p["hf_loss_weight"] * loss_hf + p["baseline_anchor_weight"] * loss_base
        )

    return total, losses


def evaluate_test(model, test_levels, scaler_tensor, batch_size, device):
    """Eval on test_levels (HF only — m=1). Returns nRMSE_L2."""
    model.eval()
    sq_sum = 0.0
    target_sq_sum = 0.0
    n_samples = 0
    with torch.no_grad():
        for lvl in test_levels:
            Xs = torch.from_numpy(lvl["Xs"].astype(np.float32))
            ys = torch.from_numpy(lvl["ys"].astype(np.float32))
            m_arr = torch.full((Xs.shape[0],), float(lvl["m"]), dtype=torch.float32)
            for i in range(0, Xs.shape[0], batch_size):
                Xb = _to_device(Xs[i:i + batch_size], device)
                yb = _to_device(ys[i:i + batch_size], device)
                mb = _to_device(m_arr[i:i + batch_size], device)
                # Always evaluate via the HF residual stack at m=lvl['m'].
                # Even if level_idx < n_levels-1, we want the HF prediction in
                # 64x64 native (the test set is HF-only per ifc_raw convention).
                out = model.hf_predict(Xb, mb)
                pred_norm = out["pred"]
                pred = pred_norm * scaler_tensor[model.n_levels - 1]
                # If the test resolution doesn't match HF, downsample/upsample.
                R_target = yb.shape[-1]
                if pred.shape[-1] != R_target:
                    pred = F.interpolate(pred.unsqueeze(1), size=(R_target, R_target),
                                         mode="bilinear", align_corners=False).squeeze(1)
                sq_sum += float(((pred - yb) ** 2).sum().item())
                target_sq_sum += float((yb ** 2).sum().item())
                n_samples += yb.shape[0]
    if target_sq_sum <= 0 or n_samples == 0:
        return float("nan"), n_samples
    return float(np.sqrt(sq_sum / max(target_sq_sum, 1e-12))), n_samples


def resolve_fidelity_weights(dataset_name: str, p: dict) -> tuple[float, float]:
    """MFRNP Poisson5 weights apply only when dataset name contains 'poisson';
    Heat (and any other dataset) uses uniform weighting per published pde_config.yaml."""
    is_poisson = "poisson" in (dataset_name or "").lower()
    if is_poisson:
        return float(p["poisson_hf_weight"]), float(p["poisson_lf_weight"])
    return 1.0, 1.0


def run(args):
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    p = SMOKE_DEFAULTS
    hf_fid_w, lf_fid_w = resolve_fidelity_weights(args.dataset_name, p)
    print(f"[loss-weights] dataset={args.dataset_name} hf_fid_weight={hf_fid_w} lf_fid_weight={lf_fid_w}")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[device] {device}")

    ds_dir = Path(args.dataset_dir).resolve()
    train_loaders, val_loaders, test_levels, scaler_dict, cat = build_loaders(
        ds_dir, val_frac=p["val_frac"], seed=args.seed, batch_size=p["batch_size"],
    )

    cond_dim = train_loaders[0][0]["Xs"].shape[1]
    n_levels = len(train_loaders)
    print(f"[data] cond_dim={cond_dim} n_levels={n_levels}")
    for lvl, ldr in train_loaders:
        print(f"  level {lvl['level_idx']} m={lvl['m']:.4f} res={lvl['native_res']} "
              f"n_train={lvl['Xs'].shape[0]} scaler={scaler_dict[lvl['level_idx']]:.4g}")

    model = FNOMFStack(
        cond_dim=cond_dim,
        native_resolutions=list(p["native_resolutions"][:n_levels]),
        modes_per_level=list(p["modes_per_level"][:n_levels]),
        hidden=p["hidden"],
        agg_hidden=p["agg_hidden"],
        n_blocks=p["n_blocks"],
        hf_res=int(p["native_resolutions"][n_levels - 1]),
    ).to(device)
    model.set_scaler(scaler_dict)
    scaler_tensor = model.scaler  # (n_levels,) buffer on device

    n_params_trainable, n_params_total = param_count(model)
    print(f"[model] params total={n_params_total:,} trainable={n_params_trainable:,}")

    opt = torch.optim.AdamW(model.parameters(), lr=p["lr"], weight_decay=p["weight_decay"])
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(args.epochs, 1), eta_min=1e-6)

    ckpt_dir = Path(args.ckpt_dir)
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    last_ckpt = ckpt_dir / "last.pt"
    start_epoch = 1
    best_val = float("inf")
    if last_ckpt.exists():
        try:
            sd = torch.load(last_ckpt, map_location=device, weights_only=False)
            if sd.get("epochs_target") == args.epochs and sd.get("cond_dim") == cond_dim:
                model.load_state_dict(sd["model"])
                opt.load_state_dict(sd["opt"])
                sched.load_state_dict(sd["sched"])
                start_epoch = sd["epoch"] + 1
                best_val = sd.get("best_val", float("inf"))
                print(f"[resume] from epoch {start_epoch}/{args.epochs} best_val={best_val:.4e}")
        except Exception as e:
            print(f"[resume] failed to load checkpoint ({e}); starting fresh")

    t_train = time.time()
    n_lf_levels = n_levels - 1

    for epoch in range(start_epoch, args.epochs + 1):
        model.train()
        # Build per-level iterators fresh each epoch
        iters = []
        for lvl, ldr in train_loaders:
            iters.append(iter(ldr) if ldr is not None else None)

        # Step count per epoch = max length across loaders (so HF gets reused if shorter)
        ldr_lens = [len(ldr) if ldr is not None else 0 for _, ldr in train_loaders]
        steps_per_epoch = max(ldr_lens) if any(ldr_lens) else 0

        epoch_losses = {"total": 0.0}
        n_steps = 0
        for step in range(steps_per_epoch):
            batches_by_level = []
            for k in range(n_levels):
                if iters[k] is None:
                    batches_by_level.append(None)
                    continue
                try:
                    b = next(iters[k])
                except StopIteration:
                    # restart shorter loader so it cycles within the epoch
                    iters[k] = iter(train_loaders[k][1])
                    b = next(iters[k])
                batches_by_level.append(b)

            opt.zero_grad(set_to_none=True)
            total_loss, losses = compute_losses(
                model, batches_by_level, scaler_tensor, p, device,
                hf_fid_weight=hf_fid_w, lf_fid_weight=lf_fid_w,
            )
            total_loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            opt.step()

            epoch_losses["total"] += float(total_loss.detach().item())
            for k, v in losses.items():
                epoch_losses[k] = epoch_losses.get(k, 0.0) + v
            n_steps += 1

        sched.step()

        # Save every 10 epochs OR at final
        if epoch % 10 == 0 or epoch == args.epochs:
            torch.save({
                "epoch": epoch,
                "epochs_target": args.epochs,
                "cond_dim": cond_dim,
                "model": model.state_dict(),
                "opt": opt.state_dict(),
                "sched": sched.state_dict(),
                "best_val": best_val,
            }, last_ckpt)
            tot = epoch_losses.get("total", 0.0) / max(n_steps, 1)
            print(f"[epoch {epoch:04d}/{args.epochs}] avg_loss={tot:.4e}")

    train_seconds = time.time() - t_train

    # Eval
    t_eval = time.time()
    test_nrmse, n_test = evaluate_test(
        model, test_levels, scaler_tensor, p["batch_size"], device
    )
    eval_seconds = time.time() - t_eval
    print(f"[test] nRMSE={test_nrmse:.4e} n_samples={n_test}")

    return {
        "model": "fno_mf_stack",
        "dataset": args.dataset_name,
        "metric_value": test_nrmse,
        "splits": {
            "test": {"nRMSE": test_nrmse, "n_samples": n_test},
        },
        "n_params": int(n_params_total),
        "train_seconds": train_seconds,
        "eval_seconds": eval_seconds,
        "device": str(device),
        "hf_fid_weight": hf_fid_w,
        "lf_fid_weight": lf_fid_w,
        "notes": (
            f"4 FNOs (hidden={p['hidden']}, modes={list(p['modes_per_level'])}, "
            f"{p['n_blocks']} blocks) + MFRNP aggregator + HF residual; per-fidelity y-scaler; "
            f"per-fidelity loss weights HF={hf_fid_w} LF={lf_fid_w} (MFRNP Poisson5 gated)."
        ),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset_dir", required=True)
    ap.add_argument("--dataset_name", default=None,
                    help="Short dataset name; defaults to basename(dataset_dir).")
    ap.add_argument("--epochs", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ckpt_dir", required=True)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    if args.dataset_name is None:
        args.dataset_name = Path(args.dataset_dir).resolve().name

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    res = run(args)
    out.write_text(json.dumps(res, indent=2))
    print(f"[wrote] {out}")


if __name__ == "__main__":
    main()
