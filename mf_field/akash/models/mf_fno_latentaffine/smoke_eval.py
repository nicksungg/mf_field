"""Smoke + fair-eval for mf_fno_latentaffine (B1).

Tests the hypothesis "HF ~= LF + constant latent direction" (word2vec-style
offset) in a learned field-latent space.

Steps
-----
1. Obtain a ConvAE over fields on the working grid. We TRY to reuse the exported
   AE at mf_fno_diffprior/ae.pt (importable, class-compatible). If it loads we
   fine-tune it briefly on this dataset's LF fields; otherwise we train a fresh
   small AE. (The AE always reconstructs the abundant LF fields.)
2. Encode LF and HF TRAIN fields. The ifc fidelities are NOT sample-aligned
   (independent random conds per fidelity), so we measure a DISTRIBUTIONAL mean
   shift: delta = mean(z_hf) - mean(z_lf).
3. MEASUREMENT (the real deliverable): shift_direction_consistency. We bootstrap
   B resamples of the LF and HF latent sets, recompute the shift direction each
   time, and report (a) mean pairwise cosine similarity of those directions and
   (b) their relative std (norm of the std vector / norm of the mean vector).
   High cosine / low rel-std => the LF->HF map is ~one constant translation.
4. PREDICTION (ifc test is HF-only): train a tiny base regressor X->z_lf on LF
   train, then predict HF = decode(base(X_test) + delta). Still a valid full
   field + JSON.

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
                         SMOKE, _cap_grid, _modes, _to_grid, FACTORY_ROOT)
from model import ConvAE, BaseRegressor, param_count  # noqa: E402

DIFFPRIOR_AE = AKASH / "models" / "mf_fno_diffprior" / "ae.pt"


def _try_load_diffprior_ae(device):
    """Return a ConvAE initialized from the exported diffprior ae.pt, or None."""
    if not DIFFPRIOR_AE.exists():
        return None
    try:
        sd = torch.load(DIFFPRIOR_AE, map_location=device, weights_only=False)
        cfg = sd["config"]
        ae = ConvAE(base_ch=cfg["base_ch"], latent_ch=cfg["latent_ch"],
                    latent_hw=tuple(cfg["latent_hw"]), zdim=cfg["zdim"]).to(device)
        ae.load_state_dict(sd["ae"])
        print(f"[ae] reused exported diffprior ae.pt (zdim={cfg['zdim']})", flush=True)
        return ae
    except Exception as e:
        print(f"[ae] could not reuse diffprior ae.pt ({e}); building fresh", flush=True)
        return None


def _train_ae(ae, Y_grid, scaler, grid, epochs, lr, p, device, tag):
    """Reconstruction training of the AE on fields Y_grid (raw units)/scaler."""
    if Y_grid.shape[0] == 0 or epochs <= 0:
        return
    opt = torch.optim.AdamW(ae.parameters(), lr=lr, weight_decay=p["weight_decay"])
    Yt = torch.from_numpy(Y_grid).float() / scaler
    n = Y_grid.shape[0]
    bs = min(p["batch_size"], n)
    g = torch.Generator().manual_seed(0)
    for ep in range(epochs):
        ae.train()
        perm = torch.randperm(n, generator=g)
        tot = 0.0
        for i in range(0, n, bs):
            idx = perm[i:i + bs]
            yb = Yt[idx].to(device)
            opt.zero_grad(set_to_none=True)
            rec = ae(yb, grid)
            loss = F.mse_loss(rec, yb)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(ae.parameters(), p["grad_clip"])
            opt.step()
            tot += float(loss.detach())
        if (ep + 1) % max(1, epochs // 5) == 0 or ep == epochs - 1:
            print(f"[{tag} {ep+1:04d}/{epochs}] rec_mse={tot/max(1,(n+bs-1)//bs):.4e}", flush=True)


def _encode_all(ae, Y_grid, scaler, device, bs):
    ae.eval()
    zs = []
    with torch.no_grad():
        for i in range(0, Y_grid.shape[0], bs):
            yb = torch.from_numpy(Y_grid[i:i + bs]).float().to(device) / scaler
            zs.append(ae.encode(yb).cpu().numpy())
    return np.concatenate(zs, 0).astype(np.float64) if zs else np.zeros((0, ae.zdim))


def _train_base(base, X, Z, epochs, lr, p, device, tag):
    """Train base regressor X -> z (Z = LF latents)."""
    if X.shape[0] == 0 or epochs <= 0:
        return
    opt = torch.optim.AdamW(base.parameters(), lr=lr, weight_decay=p["weight_decay"])
    Xt = torch.from_numpy(X).float(); Zt = torch.from_numpy(Z).float()
    n = X.shape[0]
    bs = min(p["batch_size"], n)
    g = torch.Generator().manual_seed(0)
    for ep in range(epochs):
        base.train()
        perm = torch.randperm(n, generator=g)
        tot = 0.0
        for i in range(0, n, bs):
            idx = perm[i:i + bs]
            xb = Xt[idx].to(device); zb = Zt[idx].to(device)
            opt.zero_grad(set_to_none=True)
            loss = F.mse_loss(base(xb), zb)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(base.parameters(), p["grad_clip"])
            opt.step()
            tot += float(loss.detach())
        if (ep + 1) % max(1, epochs // 5) == 0 or ep == epochs - 1:
            print(f"[{tag} {ep+1:04d}/{epochs}] zmse={tot/max(1,(n+bs-1)//bs):.4e}", flush=True)


def _shift_consistency(z_lf, z_hf, n_boot=200, seed=0):
    """Bootstrap the distributional mean-shift direction and measure consistency.

    Returns dict with mean_pairwise_cosine, relative_std, n_boot, and the
    overall delta norm. LF/HF are NOT sample-aligned, so we resample each set
    independently and recompute delta = mean(z_hf*) - mean(z_lf*).
    """
    rng = np.random.RandomState(seed)
    n_lf, n_hf = z_lf.shape[0], z_hf.shape[0]
    delta_full = z_hf.mean(0) - z_lf.mean(0)
    dirs = []
    for _ in range(n_boot):
        ilf = rng.randint(0, n_lf, size=n_lf)
        ihf = rng.randint(0, n_hf, size=n_hf)
        d = z_hf[ihf].mean(0) - z_lf[ilf].mean(0)
        nrm = np.linalg.norm(d)
        if nrm > 1e-12:
            dirs.append(d / nrm)
    dirs = np.asarray(dirs)
    if len(dirs) < 2:
        return {"mean_pairwise_cosine": None, "relative_std": None,
                "n_boot": int(len(dirs)), "delta_norm": float(np.linalg.norm(delta_full))}
    # mean pairwise cosine via the mean direction (E[<d_i,d_j>] = ||mean||^2 + ...);
    # compute directly but cheaply: average cosine to the mean unit direction.
    mean_dir = dirs.mean(0)
    mean_dir_unit = mean_dir / max(np.linalg.norm(mean_dir), 1e-12)
    cos_to_mean = dirs @ mean_dir_unit
    # relative std of the (unnormalized) bootstrap deltas
    boot_deltas = []
    rng2 = np.random.RandomState(seed + 1)
    for _ in range(n_boot):
        ilf = rng2.randint(0, n_lf, size=n_lf)
        ihf = rng2.randint(0, n_hf, size=n_hf)
        boot_deltas.append(z_hf[ihf].mean(0) - z_lf[ilf].mean(0))
    boot_deltas = np.asarray(boot_deltas)
    rel_std = float(np.linalg.norm(boot_deltas.std(0)) /
                    max(np.linalg.norm(boot_deltas.mean(0)), 1e-12))
    return {"mean_cosine_to_mean_direction": float(cos_to_mean.mean()),
            "min_cosine_to_mean_direction": float(cos_to_mean.min()),
            "relative_std": rel_std, "n_boot": int(len(dirs)),
            "delta_norm": float(np.linalg.norm(delta_full))}


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

    X_lf = train["cond_by_fid"][lf].astype(np.float32)
    Y_lf = _to_grid(train["field_by_fid"][lf], lf_grid_native, grid)
    X_hf = train["cond_by_fid"][hf].astype(np.float32)
    Y_hf = _to_grid(train["field_by_fid"][hf], hf_grid_native, grid)
    X_te = test["cond_by_fid"][hf].astype(np.float32)
    Y_te = _to_grid(test["field_by_fid"][hf], hf_grid_native, grid)

    # does the test split carry aligned LF fields? (ifc: no -> HF-only fallback)
    test_has_lf = bool(test["lf_fids"]) and lf in test["fids"]

    cond_dim = int(X_hf.shape[1])
    scaler = max(float(np.abs(Y_lf).max()), float(np.abs(Y_hf).max()), 1e-8)  # shared AE scaler
    scaler_hf = max(float(np.abs(Y_hf).max()), 1e-8) if Y_hf.size else 1.0

    print(f"[data] {args.dataset_name} loader={train['loader']} LF={lf} HF={hf} "
          f"work_grid={grid} N_lf={X_lf.shape[0]} N_hf={X_hf.shape[0]} N_test={X_te.shape[0]} "
          f"cond_dim={cond_dim} test_has_lf={test_has_lf}", flush=True)

    # ── AE: reuse diffprior export if possible, else fresh ──
    ae = _try_load_diffprior_ae(device)
    reused_ae = ae is not None
    if ae is None:
        ae = ConvAE(base_ch=32, latent_ch=16, latent_hw=(4, 4), zdim=64).to(device)
    zdim = ae.zdim
    base = BaseRegressor(cond_dim, zdim).to(device)
    n_params = param_count(ae, base)

    ckpt_dir = Path(args.ckpt_dir); ckpt_dir.mkdir(parents=True, exist_ok=True)
    last = ckpt_dir / "last.pt"
    trained = False
    if last.exists():
        try:
            sd = torch.load(last, map_location=device, weights_only=False)
            if sd.get("epochs_target") == args.epochs and sd.get("grid") == list(grid):
                ae.load_state_dict(sd["ae"]); base.load_state_dict(sd["base"])
                trained = True
                print("[resume] loaded finished checkpoint", flush=True)
        except Exception as e:
            print(f"[resume] failed ({e}); fresh", flush=True)

    t_train = time.time()
    if not trained:
        # AE fine-tune/train on LF (the abundant fields); fewer epochs if reused.
        ae_epochs = max(args.epochs // 2, 1) if reused_ae else args.epochs
        print(f"[stage] AE recon on LF ({Y_lf.shape[0]} fields) epochs={ae_epochs} reused={reused_ae}", flush=True)
        _train_ae(ae, Y_lf, scaler, grid, ae_epochs, p["lr_pretrain"], p, device, "AE")
        # base regressor X->z_lf on LF latents
        z_lf_tr = _encode_all(ae, Y_lf, scaler, device, p["batch_size"])
        print(f"[stage] base regressor X->z_lf ({X_lf.shape[0]} samples)", flush=True)
        _train_base(base, X_lf, z_lf_tr.astype(np.float32), args.epochs, p["lr_pretrain"],
                    p, device, "base")
        torch.save({"epochs_target": args.epochs, "grid": list(grid),
                    "ae": ae.state_dict(), "base": base.state_dict()}, last)
    train_seconds = time.time() - t_train

    # ── encode train fields, fit constant latent shift delta ──
    z_lf = _encode_all(ae, Y_lf, scaler, device, p["batch_size"])
    z_hf = _encode_all(ae, Y_hf, scaler, device, p["batch_size"])
    delta = (z_hf.mean(0) - z_lf.mean(0)).astype(np.float32)
    consistency = _shift_consistency(z_lf, z_hf, n_boot=200, seed=args.seed)
    print(f"[measure] shift_direction_consistency={consistency}", flush=True)

    # ── prediction ──
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize()
    t_eval = time.time()
    ae.eval(); base.eval()
    preds = []
    bs = p["batch_size"]
    delta_t = torch.from_numpy(delta).to(device)
    with torch.no_grad():
        if test_has_lf:
            # aligned LF available: HF = decode(encode(LF_test) + delta)
            Y_lf_te = _to_grid(test["field_by_fid"][lf], lf_grid_native, grid)
            for i in range(0, Y_lf_te.shape[0], bs):
                yb = torch.from_numpy(Y_lf_te[i:i + bs]).float().to(device) / scaler
                z = ae.encode(yb) + delta_t
                fld = ae.decode(z, grid) * scaler
                preds.append(fld.reshape(fld.shape[0], -1).cpu().numpy())
            pred_path = "decode(encode(LF_test)+delta)"
        else:
            # HF-only fallback: z_lf_hat = base(X_test); HF = decode(z_lf_hat + delta)
            for i in range(0, X_te.shape[0], bs):
                xb = torch.from_numpy(X_te[i:i + bs]).float().to(device)
                z = base(xb) + delta_t
                fld = ae.decode(z, grid) * scaler
                preds.append(fld.reshape(fld.shape[0], -1).cpu().numpy())
            pred_path = "decode(base(X_test)+delta)_HF_only_fallback"
    if device.type == "cuda":
        torch.cuda.synchronize()
    eval_seconds = time.time() - t_eval
    pred = np.concatenate(preds, 0).astype(np.float64)
    target = Y_te.reshape(Y_te.shape[0], -1).astype(np.float64)

    n_samples = int(target.shape[0])
    latency = (1000.0 * eval_seconds / max(n_samples, 1)) if device.type == "cuda" else None
    peak_mem = (torch.cuda.max_memory_allocated() / 1e6) if device.type == "cuda" else None

    return finalize_and_write(
        out_path=out_path, model="mf_fno_latentaffine", dataset=args.dataset_name,
        pred=pred, target=target, work_grid=grid, n_params=int(n_params),
        train_seconds=train_seconds, eval_seconds=eval_seconds,
        latency_ms_per_sample=latency, peak_mem_mb=peak_mem, seed=args.seed,
        extra={"device": str(device), "hf_fidelity": int(hf), "lf_fidelity": int(lf),
               "hypothesis": "HF ~= LF + constant latent direction (delta)",
               "reused_diffprior_ae": bool(reused_ae), "zdim": int(zdim),
               "test_has_aligned_lf": bool(test_has_lf), "prediction_path": pred_path,
               "shift_direction_consistency": consistency,
               "delta_norm": float(np.linalg.norm(delta)),
               "note": "ifc LF/HF train are NOT sample-aligned (independent conds per fidelity); "
                       "delta is a DISTRIBUTIONAL mean shift and consistency is bootstrapped. "
                       "Test is HF-only so prediction uses the base(X)->z_lf fallback. "
                       "The consistency measurement is the real deliverable.",
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
