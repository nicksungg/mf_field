"""
Adapter: train + evaluate MFTransolver_v9 on a single IFC-raw dataset, write
the JSON expected by ../../eval/MODEL_CONTRACT.md.

Wraps the existing train_v9.py / eval_v9.py logic but:
  - takes the contract args (--dataset_dir, --epochs, --out, --ckpt_dir, --seed)
  - resumes from ckpt_dir/last.pt if present (preemption-safe)
  - emits the contract JSON
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

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from model_v9 import MFTransolver_v9, param_count  # noqa: E402
from train_v9 import IFCRawMultiStreamDataset, hybrid_loss, make_collate_fn, get_prior_weight  # noqa: E402
from torch.utils.data import DataLoader, random_split  # noqa: E402


SMOKE_DEFAULTS = dict(
    batch_size=4, lr=3e-4, n_lf=1024, n_hf=2048,
    hidden_dim=128, n_slices=16, num_heads=4,
    encoder_layers=2, residual_layers=2,
    pos_enc_freqs=4, rbf_gamma_init=1.0,
    prior_weight_init=1.0, prior_weight_final=0.1, prior_decay_epochs=80,
    val_frac=0.2,
)


def evaluate(model, loader, device, use_amp):
    model.eval()
    n_samples = 0
    sq_sum = 0.0
    target_sq_sum = 0.0
    with torch.no_grad(), torch.amp.autocast("cuda", enabled=use_amp):
        for list_of_lf_toks, hf_tok, targets, _ in loader:
            list_of_lf_toks = [t.to(device) for t in list_of_lf_toks]
            hf_tok = hf_tok.to(device)
            targets = targets.to(device)
            pred = model(list_of_lf_toks, hf_tok)
            sq_sum += float(((pred - targets) ** 2).sum().item())
            target_sq_sum += float((targets ** 2).sum().item())
            n_samples += hf_tok.size(0)
    if target_sq_sum <= 0 or n_samples == 0:
        return float("nan"), n_samples
    return float(np.sqrt(sq_sum / max(target_sq_sum, 1e-12))), n_samples


def run(args):
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    p = SMOKE_DEFAULTS

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    use_amp = device.type == "cuda"
    scaler = torch.amp.GradScaler("cuda", enabled=use_amp)

    ds_dir = Path(args.dataset_dir)
    train_full = IFCRawMultiStreamDataset(ds_dir, split="train")
    n_val = max(1, int(len(train_full) * p["val_frac"]))
    n_tr = max(1, len(train_full) - n_val)
    if n_tr + n_val > len(train_full):
        n_val = len(train_full) - n_tr
    g = torch.Generator().manual_seed(args.seed)
    tr_ds, val_ds = random_split(train_full, [n_tr, n_val], generator=g)

    collate = make_collate_fn(p["n_lf"], p["n_hf"])
    tr_loader = DataLoader(tr_ds, batch_size=p["batch_size"], shuffle=True,
                           collate_fn=collate, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=p["batch_size"], shuffle=False,
                            collate_fn=collate, num_workers=0)

    model = MFTransolver_v9(
        cond_dim=train_full.cond_dim,
        hidden_dim=p["hidden_dim"], n_slices=p["n_slices"], num_heads=p["num_heads"],
        encoder_layers=p["encoder_layers"], residual_layers=p["residual_layers"],
        pos_enc_freqs=p["pos_enc_freqs"], rbf_gamma_init=p["rbf_gamma_init"],
        num_lf_streams=len(train_full.lf_fids),
    ).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=p["lr"], weight_decay=1e-5)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=args.epochs, eta_min=1e-6)

    ckpt_dir = Path(args.ckpt_dir); ckpt_dir.mkdir(parents=True, exist_ok=True)
    last_ckpt = ckpt_dir / "last.pt"
    best_ckpt = ckpt_dir / "best.pt"
    start_epoch, best_val = 1, float("inf")
    if last_ckpt.exists():
        sd = torch.load(last_ckpt, map_location=device)
        if sd.get("epochs_target") == args.epochs:
            model.load_state_dict(sd["model"])
            opt.load_state_dict(sd["opt"])
            sched.load_state_dict(sd["sched"])
            start_epoch = sd["epoch"] + 1
            best_val = sd.get("best_val", float("inf"))
            print(f"[resume] from epoch {start_epoch}/{args.epochs}, best_val={best_val:.4e}")

    trainable, total = param_count(model)
    print(f"[start] {args.dataset_name} | params={total:,} | start_epoch={start_epoch}")

    t_train = time.time()
    for epoch in range(start_epoch, args.epochs + 1):
        lam_prior = get_prior_weight(epoch, p["prior_weight_init"],
                                     p["prior_weight_final"], p["prior_decay_epochs"])
        model.train()
        for list_of_lf_toks, hf_tok, targets, _ in tr_loader:
            list_of_lf_toks = [t.to(device) for t in list_of_lf_toks]
            hf_tok = hf_tok.to(device); targets = targets.to(device)
            opt.zero_grad(set_to_none=True)
            with torch.amp.autocast("cuda", enabled=use_amp):
                comps = model(list_of_lf_toks, hf_tok, return_components=True)
                pred, prior, alpha = comps["pred"], comps["prior"], comps["alpha"]
                loss_main, _ = hybrid_loss(pred, targets)
                loss_prior, _ = hybrid_loss(prior, targets)
                entropy = -(alpha * torch.log(alpha.clamp_min(1e-8))).sum(dim=-1).mean()
                loss = loss_main + lam_prior * loss_prior - 1e-3 * entropy
            scaler.scale(loss).backward()
            scaler.unscale_(opt)
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            scaler.step(opt); scaler.update()
        sched.step()

        # cheap val to track best
        val_nrmse, _ = evaluate(model, val_loader, device, use_amp)
        if val_nrmse < best_val:
            best_val = val_nrmse
            torch.save({"model": model.state_dict()}, best_ckpt)

        if epoch % 10 == 0 or epoch == args.epochs:
            torch.save({"epoch": epoch, "epochs_target": args.epochs,
                        "model": model.state_dict(), "opt": opt.state_dict(),
                        "sched": sched.state_dict(), "best_val": best_val}, last_ckpt)
            print(f"[epoch {epoch:04d}/{args.epochs}] val_nRMSE={val_nrmse:.4e} best={best_val:.4e}")

    train_seconds = time.time() - t_train

    # load best for eval
    if best_ckpt.exists():
        model.load_state_dict(torch.load(best_ckpt, map_location=device)["model"])

    # evaluate on every test/ood split present in ds_dir
    splits = {}
    t_eval = time.time()
    for sub in ("test", "ood"):
        sub_dir = ds_dir / sub
        if not sub_dir.exists():
            continue
        try:
            ds = IFCRawMultiStreamDataset(ds_dir, split=sub)
        except Exception as e:
            splits[sub] = {"error": str(e)}
            continue
        loader = DataLoader(ds, batch_size=p["batch_size"], shuffle=False,
                            collate_fn=make_collate_fn(p["n_lf"], p["n_hf"]),
                            num_workers=0)
        nrmse, n = evaluate(model, loader, device, use_amp)
        splits[sub] = {"nRMSE": nrmse, "n_samples": n}
    eval_seconds = time.time() - t_eval

    return {
        "model": "v9_baseline",
        "dataset": args.dataset_name,
        "splits": splits,
        "n_params": int(total),
        "train_seconds": train_seconds,
        "eval_seconds": eval_seconds,
        "best_val_nRMSE": best_val,
        "device": str(device),
    }


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
    res = run(args)
    out.write_text(json.dumps(res, indent=2))
    print(f"[wrote] {out}")


if __name__ == "__main__":
    main()
