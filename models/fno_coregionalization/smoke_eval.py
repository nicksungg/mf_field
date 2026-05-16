"""
Smoke/full eval entrypoint for the fno_coregionalization family.

CLI matches `eval/MODEL_CONTRACT.md` exactly: `--dataset_dir`, `--dataset_name`,
`--epochs`, `--out`, `--ckpt_dir`, `--seed`. Resumes from `ckpt_dir/last.pt` if
present (preemption-safe on `mit_preemptable`).

Pipeline per call:
  1. Load `IFCMultiFidelityDataset(split='train')`, random_split(val_frac=0.1).
  2. Compute per-fidelity scalers from the training subset's raw arrays.
  3. Build FNOCoregionalization, set scalers buffer.
  4. Train with Adam, lr=3e-4, cosine schedule, MSE on upsampled-to-64x64 y.
  5. Evaluate on every `test`/`ood` split present in dataset_dir; report L2
     nRMSE (`||y_pred - y|| / ||y||`) per split.
  6. Write contract-compliant JSON to `--out`.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader, random_split

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from model import FNOCoregionalization, param_count  # noqa: E402
from data import IFCMultiFidelityDataset, compute_per_fidelity_scalers  # noqa: E402


SMOKE_DEFAULTS = dict(
    batch_size=8,
    lr=3e-4,
    weight_decay=1e-5,
    hidden_channels=64,
    K=10,
    n_blocks=4,
    modes=12,
    val_frac=0.1,
    grid_size=64,
    ckpt_every=10,
    grad_clip=1.0,
)


def nrmse_over_loader(model, loader, device) -> tuple[float, int]:
    model.eval()
    n = 0
    sq_sum = 0.0
    tgt_sq_sum = 0.0
    with torch.no_grad():
        for X, y, m in loader:
            X = X.to(device); y = y.to(device); m = m.to(device)
            pred = model(X, m)
            sq_sum += float(((pred - y) ** 2).sum().item())
            tgt_sq_sum += float((y ** 2).sum().item())
            n += X.size(0)
    if tgt_sq_sum <= 0 or n == 0:
        return float("nan"), n
    return float(np.sqrt(sq_sum / max(tgt_sq_sum, 1e-12))), n


def run(args) -> dict:
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    p = SMOKE_DEFAULTS

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    ds_dir = Path(args.dataset_dir)

    train_full = IFCMultiFidelityDataset(ds_dir, split="train", target_size=p["grid_size"])
    n_total = len(train_full)
    n_val = max(1, int(round(n_total * p["val_frac"])))
    n_tr = max(1, n_total - n_val)
    if n_tr + n_val != n_total:
        n_val = n_total - n_tr
    g = torch.Generator().manual_seed(args.seed)
    tr_ds, val_ds = random_split(train_full, [n_tr, n_val], generator=g)

    m_keys, scalers = compute_per_fidelity_scalers(train_full, tr_ds.indices)

    tr_loader = DataLoader(tr_ds, batch_size=p["batch_size"], shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=p["batch_size"], shuffle=False, num_workers=0)

    model = FNOCoregionalization(
        cond_dim=train_full.cond_dim,
        hidden_channels=p["hidden_channels"],
        K=p["K"],
        n_blocks=p["n_blocks"],
        modes=p["modes"],
        grid_size=p["grid_size"],
    ).to(device)
    model.set_scalers(m_keys, scalers)

    opt = torch.optim.Adam(model.parameters(), lr=p["lr"], weight_decay=p["weight_decay"])
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(args.epochs, 1), eta_min=1e-6)

    ckpt_dir = Path(args.ckpt_dir); ckpt_dir.mkdir(parents=True, exist_ok=True)
    last_ckpt = ckpt_dir / "last.pt"
    best_ckpt = ckpt_dir / "best.pt"
    start_epoch, best_val = 1, float("inf")
    if last_ckpt.exists():
        try:
            sd = torch.load(last_ckpt, map_location=device)
            if sd.get("epochs_target") == args.epochs:
                # Set scaler buffers to match the checkpoint's shape before load.
                ck_m = sd["model"].get("m_keys")
                ck_s = sd["model"].get("scalers")
                if ck_m is not None and ck_s is not None:
                    model.set_scalers(ck_m.cpu().tolist(), ck_s.cpu().tolist())
                model.load_state_dict(sd["model"])
                opt.load_state_dict(sd["opt"])
                sched.load_state_dict(sd["sched"])
                start_epoch = sd["epoch"] + 1
                best_val = sd.get("best_val", float("inf"))
                print(f"[resume] from epoch {start_epoch}/{args.epochs}, best_val={best_val:.4e}")
        except Exception as e:
            print(f"[resume] failed ({e}) — starting fresh")

    n_params = param_count(model)
    print(f"[start] {args.dataset_name} | params={n_params:,} | "
          f"n_train={n_tr} n_val={n_val} cond_dim={train_full.cond_dim} "
          f"m_keys={m_keys} scalers={[f'{s:.4g}' for s in scalers]}")

    t_train = time.time()
    for epoch in range(start_epoch, args.epochs + 1):
        model.train()
        for X, y, m in tr_loader:
            X = X.to(device); y = y.to(device); m = m.to(device)
            opt.zero_grad(set_to_none=True)
            pred = model(X, m)
            loss = ((pred - y) ** 2).mean()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), p["grad_clip"])
            opt.step()
        sched.step()

        val_nrmse, _ = nrmse_over_loader(model, val_loader, device)
        if val_nrmse < best_val:
            best_val = val_nrmse
            torch.save({"model": model.state_dict()}, best_ckpt)

        if epoch % p["ckpt_every"] == 0 or epoch == args.epochs:
            torch.save({
                "epoch": epoch, "epochs_target": args.epochs,
                "model": model.state_dict(), "opt": opt.state_dict(),
                "sched": sched.state_dict(), "best_val": best_val,
            }, last_ckpt)
            print(f"[epoch {epoch:04d}/{args.epochs}] val_nRMSE={val_nrmse:.4e} best={best_val:.4e}")
    train_seconds = time.time() - t_train

    if best_ckpt.exists():
        model.load_state_dict(torch.load(best_ckpt, map_location=device)["model"])

    splits: dict = {}
    t_eval = time.time()
    for sub in ("test", "ood"):
        sub_dir = ds_dir / sub
        if not sub_dir.exists():
            continue
        try:
            test_ds = IFCMultiFidelityDataset(ds_dir, split=sub, target_size=p["grid_size"])
        except Exception as e:
            splits[sub] = {"error": str(e)}
            continue
        loader = DataLoader(test_ds, batch_size=p["batch_size"], shuffle=False, num_workers=0)
        nrmse, n = nrmse_over_loader(model, loader, device)
        splits[sub] = {"nRMSE": nrmse, "n_samples": n}
    eval_seconds = time.time() - t_eval

    return {
        "model": "fno_coregionalization",
        "dataset": args.dataset_name,
        "splits": splits,
        "n_params": int(n_params),
        "train_seconds": train_seconds,
        "eval_seconds": eval_seconds,
        "best_val_nRMSE": best_val,
        "device": str(device),
        "notes": (
            f"H1: FNO+IFC coregionalization, K={p['K']}, blocks={p['n_blocks']}, "
            f"modes={p['modes']}, hidden={p['hidden_channels']}, val_frac={p['val_frac']}, "
            f"per-fidelity output normalization (scalers={[f'{s:.4g}' for s in scalers]})"
        ),
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
