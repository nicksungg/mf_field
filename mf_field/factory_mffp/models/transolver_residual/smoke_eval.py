"""
Train + evaluate TransolverResidual on a single ifc_raw dataset and emit the
JSON expected by ../../eval/MODEL_CONTRACT.md.

Uses the IFCRawMultiStreamDataset from references/v9_baseline/{train_v9,eval_v9}.py
for the loader (the eval variant handles HF-only test splits via downsampling).

Checkpoint resume guard checks both epoch target and recipe_hash, so changes
to SMOKE_DEFAULTS invalidate any prior checkpoint (fixes the contamination bug
flagged in the backlog).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader, random_split

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(PROJECT_ROOT / "references" / "v9_baseline"))

from model import TransolverResidual, param_count  # noqa: E402
from train_v9 import IFCRawMultiStreamDataset as TrainDataset, make_collate_fn  # noqa: E402
from eval_v9 import IFCRawMultiStreamDataset as EvalDataset  # noqa: E402


SMOKE_DEFAULTS = dict(
    batch_size=4, lr=3e-4, n_lf=1024, n_hf=2048,
    hidden_dim=192, n_slices=32, num_heads=6,
    encoder_layers=2, residual_layers=3,
    pos_enc_freqs=6, interp_gamma=4.0,
    val_frac=0.2,
)


def recipe_hash() -> str:
    payload = json.dumps(SMOKE_DEFAULTS, sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()[:12]


def nrmse(model, loader, device, use_amp):
    model.eval()
    sq_sum, target_sq_sum, n = 0.0, 0.0, 0
    with torch.no_grad(), torch.amp.autocast("cuda", enabled=use_amp):
        for list_of_lf_toks, hf_tok, targets, _ in loader:
            list_of_lf_toks = [t.to(device) for t in list_of_lf_toks]
            hf_tok = hf_tok.to(device); targets = targets.to(device)
            pred = model(list_of_lf_toks, hf_tok)
            sq_sum += float(((pred - targets) ** 2).sum().item())
            target_sq_sum += float((targets ** 2).sum().item())
            n += hf_tok.size(0)
    if target_sq_sum <= 0 or n == 0:
        return float("nan"), n
    return float(np.sqrt(sq_sum / max(target_sq_sum, 1e-12))), n


def hybrid_loss(pred, targets):
    diff = pred - targets
    mse = torch.mean(diff ** 2)
    rel = torch.sqrt(torch.sum(diff ** 2, dim=1)) / torch.clamp(torch.sqrt(torch.sum(targets ** 2, dim=1)), min=1e-4)
    return mse + torch.mean(rel), mse


def run(args):
    torch.manual_seed(args.seed); np.random.seed(args.seed)
    p = SMOKE_DEFAULTS
    rh = recipe_hash()

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    use_amp = device.type == "cuda"
    scaler = torch.amp.GradScaler("cuda", enabled=use_amp)

    ds_dir = Path(args.dataset_dir)
    train_full = TrainDataset(ds_dir, split="train")
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

    model = TransolverResidual(
        cond_dim=train_full.cond_dim,
        hidden_dim=p["hidden_dim"], n_slices=p["n_slices"],
        num_heads=p["num_heads"], encoder_layers=p["encoder_layers"],
        residual_layers=p["residual_layers"], pos_enc_freqs=p["pos_enc_freqs"],
        interp_gamma=p["interp_gamma"],
    ).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=p["lr"], weight_decay=1e-5)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=args.epochs, eta_min=1e-6)

    ckpt_dir = Path(args.ckpt_dir); ckpt_dir.mkdir(parents=True, exist_ok=True)
    last_ckpt = ckpt_dir / "last.pt"
    best_ckpt = ckpt_dir / "best.pt"
    start_epoch, best_val = 1, float("inf")
    if last_ckpt.exists():
        sd = torch.load(last_ckpt, map_location=device, weights_only=False)
        if sd.get("epochs_target") == args.epochs and sd.get("recipe_hash") == rh:
            model.load_state_dict(sd["model"])
            opt.load_state_dict(sd["opt"])
            sched.load_state_dict(sd["sched"])
            start_epoch = sd["epoch"] + 1
            best_val = sd.get("best_val", float("inf"))
            print(f"[resume] epoch {start_epoch}/{args.epochs}, best={best_val:.4e}")
        else:
            print(f"[fresh] checkpoint recipe_hash mismatch ({sd.get('recipe_hash')} != {rh}) — discarding")

    trainable, total = param_count(model)
    print(f"[start] {args.dataset_name} | params={total:,} | recipe_hash={rh}")

    t_train = time.time()
    for epoch in range(start_epoch, args.epochs + 1):
        model.train()
        for list_of_lf_toks, hf_tok, targets, _ in tr_loader:
            list_of_lf_toks = [t.to(device) for t in list_of_lf_toks]
            hf_tok = hf_tok.to(device); targets = targets.to(device)
            opt.zero_grad(set_to_none=True)
            with torch.amp.autocast("cuda", enabled=use_amp):
                comps = model(list_of_lf_toks, hf_tok, return_components=True)
                loss, _ = hybrid_loss(comps["pred"], targets)
            scaler.scale(loss).backward()
            scaler.unscale_(opt)
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            scaler.step(opt); scaler.update()
        sched.step()

        val_nrmse, _ = nrmse(model, val_loader, device, use_amp)
        if val_nrmse < best_val:
            best_val = val_nrmse
            torch.save({"model": model.state_dict()}, best_ckpt)
        if epoch % 10 == 0 or epoch == args.epochs:
            torch.save({"epoch": epoch, "epochs_target": args.epochs,
                        "recipe_hash": rh,
                        "model": model.state_dict(), "opt": opt.state_dict(),
                        "sched": sched.state_dict(), "best_val": best_val}, last_ckpt)
            print(f"[ep {epoch:04d}/{args.epochs}] val_nRMSE={val_nrmse:.4e} best={best_val:.4e}")
    train_seconds = time.time() - t_train

    if best_ckpt.exists():
        model.load_state_dict(torch.load(best_ckpt, map_location=device, weights_only=False)["model"])

    splits = {}
    t_eval = time.time()
    for sub in ("test", "ood"):
        sub_dir = ds_dir / sub
        if not sub_dir.exists():
            continue
        try:
            ds = EvalDataset(ds_dir, split=sub)
        except Exception as e:
            splits[sub] = {"error": str(e)}; continue
        loader = DataLoader(ds, batch_size=p["batch_size"], shuffle=False,
                            collate_fn=make_collate_fn(p["n_lf"], p["n_hf"]), num_workers=0)
        v, n = nrmse(model, loader, device, use_amp)
        splits[sub] = {"nRMSE": v, "n_samples": n}
    eval_seconds = time.time() - t_eval

    return {
        "model": "transolver_residual",
        "dataset": args.dataset_name,
        "splits": splits,
        "n_params": int(total),
        "train_seconds": train_seconds,
        "eval_seconds": eval_seconds,
        "best_val_nRMSE": best_val,
        "recipe_hash": rh,
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
