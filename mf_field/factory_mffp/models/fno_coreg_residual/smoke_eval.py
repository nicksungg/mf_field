"""smoke_eval.py — contract entrypoint for fno_coreg_residual.

Trains the H3 hybrid (4 per-fidelity FNOs + MFRNP decoder-in-the-aggregation +
continuous-m basis head on HF latent) on one ifc_raw dataset and writes a
contract-compliant JSON to --out.

Training loss (in normalised y / scaler[m] space):

  L_total = sum_{k=0..n-2} LF_w[k]  * MSE(decoded_LF_k_native, y_lf_k_norm)
          +               HF_w      * MSE(agg + basis_residual, y_hf_norm)
          +               agg_w     * MSE(agg, y_hf_norm)      # anchor

The HF loss is what the basis head learns to correct; the aggregator anchor
keeps the MFRNP baseline meaningful (matching H2's training recipe).

Per-fidelity loss weights are off-by-default. The Poisson-only ablation
(HF_w=2, LF_w=0.25) lives in full_config.json behind a one-flag flip.

Ships at full-config sizes from the start (hidden=64, modes=(4,8,12,12),
3 blocks) per CEO instruction — no SMOKE_DEFAULTS regression.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

from data import build_loaders, load_split_levels  # noqa: E402
from model import FNOCoregResidual, param_count  # noqa: E402
from _common.recipe_hash import recipe_hash  # noqa: E402


# Full-config sizes from the start (CEO instruction: no smoke regression).
SMOKE_DEFAULTS = dict(
    batch_size=8,
    lr=3e-4,
    weight_decay=1e-5,
    val_frac=0.1,                # NOT 0.2 — preserves HF training samples
    hidden=64,                   # per-fidelity FNO channels (full-config)
    decoder_hidden=32,           # MFRNP-published
    K=10,                        # basis-head channels
    n_blocks=3,                  # spectral conv blocks per FNO
    b_hidden=64,                 # B(m) MLP hidden
    modes_per_level=(4, 8, 12, 12),
    native_resolutions=(8, 16, 32, 64),
    hf_loss_weight=1.0,
    agg_anchor_weight=0.5,
    lf_loss_weights=(1.0, 1.0, 1.0),   # one per LF level; HF is hf_loss_weight
    grad_clip=1.0,
)


def _to_device(t, device):
    return t.to(device, non_blocking=True)


def compute_losses(model, batches_by_level, scaler_tensor, p, device):
    """One training step: take next batch from each level loader and accumulate."""
    total = torch.zeros((), device=device)
    losses: dict = {}
    n_levels = model.n_levels

    # Per-level direct LF supervision (normalised target).
    for k in range(n_levels - 1):
        b = batches_by_level[k]
        if b is None:
            continue
        Xs, ys, _li, _m = b
        Xs = _to_device(Xs, device)
        ys = _to_device(ys, device)
        pred_norm = model.lf_decoded_native(Xs, level_idx=k)
        target_norm = ys / scaler_tensor[k]
        loss_k = F.mse_loss(pred_norm, target_norm)
        w = p["lf_loss_weights"][k] if k < len(p["lf_loss_weights"]) else 1.0
        losses[f"lf{k}"] = float(loss_k.detach().item())
        total = total + w * loss_k

    # HF residual-stack + basis-head loss (uses HF samples).
    b_hf = batches_by_level[n_levels - 1]
    if b_hf is not None:
        Xs, ys, _li, m_vals = b_hf
        Xs = _to_device(Xs, device)
        ys = _to_device(ys, device)
        m_t = torch.as_tensor(m_vals, dtype=torch.float32, device=device)
        out = model.hf_predict(Xs, m_t)
        target_norm = ys / scaler_tensor[n_levels - 1]
        loss_hf = F.mse_loss(out["pred"], target_norm)
        loss_anchor = F.mse_loss(out["agg"], target_norm)
        losses["hf"] = float(loss_hf.detach().item())
        losses["hf_anchor"] = float(loss_anchor.detach().item())
        total = total + p["hf_loss_weight"] * loss_hf + p["agg_anchor_weight"] * loss_anchor

    return total, losses


def evaluate_split(model, levels, scaler_tensor, batch_size, device):
    """nRMSE_L2 = sqrt(sum sq_err / sum sq_target). Evaluated by routing
    every test sample through the HF residual stack at the sample's m
    (typically m=1.0 since ifc_raw test sets are HF-only)."""
    model.eval()
    sq_sum = 0.0
    target_sq_sum = 0.0
    n_samples = 0
    R_hf = model.hf_res
    with torch.no_grad():
        for lvl in levels:
            Xs = torch.from_numpy(lvl["Xs"].astype(np.float32))
            ys = torch.from_numpy(lvl["ys"].astype(np.float32))
            m_arr = torch.full((Xs.shape[0],), float(lvl["m"]), dtype=torch.float32)
            for i in range(0, Xs.shape[0], batch_size):
                Xb = _to_device(Xs[i:i + batch_size], device)
                yb = _to_device(ys[i:i + batch_size], device)
                mb = _to_device(m_arr[i:i + batch_size], device)
                out = model.hf_predict(Xb, mb)
                pred_norm = out["pred"]  # at R_hf
                pred = pred_norm * scaler_tensor[model.n_levels - 1]
                R_target = yb.shape[-1]
                if pred.shape[-1] != R_target:
                    pred = F.interpolate(
                        pred.unsqueeze(1), size=(R_target, R_target),
                        mode="bilinear", align_corners=False,
                    ).squeeze(1)
                sq_sum += float(((pred - yb) ** 2).sum().item())
                target_sq_sum += float((yb ** 2).sum().item())
                n_samples += yb.shape[0]
    if target_sq_sum <= 0 or n_samples == 0:
        return float("nan"), n_samples
    return float(np.sqrt(sq_sum / max(target_sq_sum, 1e-12))), n_samples


def evaluate_val(model, val_loaders, scaler_tensor, device):
    """nRMSE_L2 over all val levels (normalised-space prediction de-scaled per level)."""
    model.eval()
    sq_sum = 0.0
    target_sq_sum = 0.0
    n_samples = 0
    R_hf = model.hf_res
    with torch.no_grad():
        for lvl, loader in val_loaders:
            if loader is None:
                continue
            k = int(lvl["level_idx"])
            for Xs, ys, _li, m_vals in loader:
                Xs = _to_device(Xs, device)
                ys = _to_device(ys, device)
                m_t = torch.as_tensor(m_vals, dtype=torch.float32, device=device)
                if k == model.n_levels - 1:
                    out = model.hf_predict(Xs, m_t)
                    pred_norm = out["pred"]
                else:
                    pred_norm = model.lf_decoded_native(Xs, level_idx=k)
                pred = pred_norm * scaler_tensor[k]
                R_target = ys.shape[-1]
                if pred.shape[-1] != R_target:
                    pred = F.interpolate(
                        pred.unsqueeze(1), size=(R_target, R_target),
                        mode="bilinear", align_corners=False,
                    ).squeeze(1)
                sq_sum += float(((pred - ys) ** 2).sum().item())
                target_sq_sum += float((ys ** 2).sum().item())
                n_samples += ys.shape[0]
    if target_sq_sum <= 0 or n_samples == 0:
        return float("nan"), n_samples
    return float(np.sqrt(sq_sum / max(target_sq_sum, 1e-12))), n_samples


def run(args) -> dict:
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    p = dict(SMOKE_DEFAULTS)
    rh = recipe_hash(SMOKE_DEFAULTS)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[device] {device} [recipe] hash={rh}")

    ds_dir = Path(args.dataset_dir).resolve()
    train_loaders, val_loaders, test_levels, scaler_dict, cat = build_loaders(
        ds_dir, val_frac=p["val_frac"], seed=args.seed, batch_size=p["batch_size"],
    )

    cond_dim = train_loaders[0][0]["Xs"].shape[1]
    n_levels = len(train_loaders)
    print(f"[data] {args.dataset_name} cond_dim={cond_dim} n_levels={n_levels}")
    for lvl, _ in train_loaders:
        print(f"  level {lvl['level_idx']} m={lvl['m']:.4f} res={lvl['native_res']} "
              f"n_train={lvl['Xs'].shape[0]} scaler={scaler_dict[lvl['level_idx']]:.4g}")

    # Native resolutions come from the data, not the ifc-ladder default, so the
    # per-level FNO output grids match the loaded dataset (e.g. the 256² cavity
    # ladder 32/64/128/256, not ifc_heat's 8/16/32/64).
    data_native_res = [lvl["native_res"] for lvl, _ in train_loaders]
    model = FNOCoregResidual(
        cond_dim=cond_dim,
        native_resolutions=data_native_res,
        modes_per_level=list(p["modes_per_level"][:n_levels]),
        hidden=p["hidden"],
        decoder_hidden=p["decoder_hidden"],
        K=p["K"],
        n_blocks=p["n_blocks"],
        b_hidden=p["b_hidden"],
        hf_res=int(data_native_res[n_levels - 1]),
    ).to(device)
    model.set_scaler(scaler_dict)
    scaler_tensor = model.scaler

    n_trainable, n_total = param_count(model)
    print(f"[model] params total={n_total:,} trainable={n_trainable:,}")

    opt = torch.optim.AdamW(model.parameters(), lr=p["lr"], weight_decay=p["weight_decay"])
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(args.epochs, 1), eta_min=1e-6)

    ckpt_dir = Path(args.ckpt_dir)
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    last_ckpt = ckpt_dir / "last.pt"
    best_ckpt = ckpt_dir / "best.pt"
    start_epoch = 1
    best_val = float("inf")
    if last_ckpt.exists():
        try:
            sd = torch.load(last_ckpt, map_location=device, weights_only=False)
            if (sd.get("epochs_target") == args.epochs
                    and sd.get("cond_dim") == cond_dim
                    and sd.get("recipe_hash") == rh):
                model.load_state_dict(sd["model"])
                opt.load_state_dict(sd["opt"])
                sched.load_state_dict(sd["sched"])
                start_epoch = sd["epoch"] + 1
                best_val = sd.get("best_val", float("inf"))
                print(f"[resume] from epoch {start_epoch}/{args.epochs} best_val={best_val:.4e}")
            else:
                print(f"[fresh] checkpoint guard mismatch (recipe_hash={sd.get('recipe_hash')} vs {rh}) — discarding")
        except Exception as e:
            print(f"[resume] failed ({e}) — starting fresh")

    t_train = time.time()
    for epoch in range(start_epoch, args.epochs + 1):
        model.train()
        iters = [iter(ldr) if ldr is not None else None for _, ldr in train_loaders]
        ldr_lens = [len(ldr) if ldr is not None else 0 for _, ldr in train_loaders]
        steps_per_epoch = max(ldr_lens) if any(ldr_lens) else 0

        epoch_total = 0.0
        n_steps = 0
        per_level_losses: dict = {}
        for _step in range(steps_per_epoch):
            batches_by_level = []
            for k in range(n_levels):
                if iters[k] is None:
                    batches_by_level.append(None)
                    continue
                try:
                    b = next(iters[k])
                except StopIteration:
                    iters[k] = iter(train_loaders[k][1])
                    b = next(iters[k])
                batches_by_level.append(b)

            opt.zero_grad(set_to_none=True)
            total_loss, losses = compute_losses(
                model, batches_by_level, scaler_tensor, p, device,
            )
            total_loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), p["grad_clip"])
            opt.step()

            epoch_total += float(total_loss.detach().item())
            for k_, v in losses.items():
                per_level_losses[k_] = per_level_losses.get(k_, 0.0) + v
            n_steps += 1

        sched.step()

        val_nrmse, n_val = evaluate_val(model, val_loaders, scaler_tensor, device)
        if val_nrmse == val_nrmse and val_nrmse < best_val:  # NaN-safe
            best_val = val_nrmse
            torch.save({"model": model.state_dict(), "epoch": epoch}, best_ckpt)

        if epoch % 10 == 0 or epoch == args.epochs:
            torch.save({
                "epoch": epoch,
                "epochs_target": args.epochs,
                "cond_dim": cond_dim,
                "recipe_hash": rh,
                "model": model.state_dict(),
                "opt": opt.state_dict(),
                "sched": sched.state_dict(),
                "best_val": best_val,
            }, last_ckpt)
            avg = epoch_total / max(n_steps, 1)
            print(f"[epoch {epoch:04d}/{args.epochs}] avg_loss={avg:.4e} "
                  f"val_nRMSE={val_nrmse:.4e} best={best_val:.4e}")

    train_seconds = time.time() - t_train

    # Restore best-val checkpoint if it exists.
    if best_ckpt.exists():
        try:
            sd = torch.load(best_ckpt, map_location=device, weights_only=False)
            model.load_state_dict(sd["model"])
            print(f"[restore-best] loaded best_ckpt at epoch {sd.get('epoch')}")
        except Exception as e:
            print(f"[restore-best] failed ({e}) — keeping last-epoch weights")

    # Evaluate every available test/ood split.
    splits: dict = {}
    t_eval = time.time()
    for sub in ("test", "ood"):
        sub_dir = ds_dir / sub
        if not sub_dir.exists():
            continue
        try:
            levels, _ = load_split_levels(ds_dir, sub)
        except Exception as e:
            splits[sub] = {"error": str(e)}
            continue
        if not levels:
            continue
        nrmse, n = evaluate_split(model, levels, scaler_tensor, p["batch_size"], device)
        splits[sub] = {"nRMSE": nrmse, "n_samples": n}
    eval_seconds = time.time() - t_eval

    primary_metric = splits.get("test", {}).get("nRMSE", float("nan"))

    return {
        "model": "fno_coreg_residual",
        "dataset": args.dataset_name,
        "metric_value": float(primary_metric),
        "splits": splits,
        "n_params": int(n_total),
        "train_seconds": train_seconds,
        "eval_seconds": eval_seconds,
        "best_val_nRMSE": best_val,
        "device": str(device),
        "notes": (
            f"H3 hybrid: 4 per-fidelity FNOs (hidden={p['hidden']}, "
            f"modes={list(p['modes_per_level'])}, blocks={p['n_blocks']}) + "
            f"MFRNP decoder-in-the-aggregation (decoder_hidden={p['decoder_hidden']}) + "
            f"continuous-m basis head (K={p['K']}, B(m)=MLP([m,m^2]) zero-init) on HF latent; "
            f"per-fidelity y-scaler, val_frac={p['val_frac']}."
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
