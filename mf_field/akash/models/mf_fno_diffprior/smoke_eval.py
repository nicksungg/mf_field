"""mf_fno_diffprior — latent PDE prior + conditional latent generation — smoke.

Pipeline (see model.py)
-----------------------
1. Train a conv AUTOENCODER on the abundant LF fields (resampled to the 256-cap
   working grid) -> learned prior over field shapes. EXPORT it to ae.pt.
2. Train a conditional DDIM latent GENERATOR [X, z_lf] -> z_hf on the HF train
   fields. z_lf is the LF latent for the aligned sample index (ifc_raw fidelities
   are index-aligned; we encode the smallest-LF train field, resampled to the
   working grid, sliced to the HF count). The diffusion path is shipped; a
   conditional-MLP fallback exists in model.py if diffusion is unstable.
3. EVAL: the ifc_raw TEST split has ONLY HF (128 samples) and is NOT
   index-aligned to the 5 HF-train samples, so NO per-sample LF field exists for
   a test sample. We therefore condition on X with a ZERO z_lf placeholder at
   eval (documented choice). We sample K times; mean is the prediction (nRMSE),
   per-pixel std across samples is reported as free UQ (extra.uq_mean_std).

Resume: ckpt_dir/last.pt keyed on (epochs_target, grid). ae.pt is (re)written
whenever a fresh train occurs and on resume is reconstructed from the checkpoint.
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

from common.mffp import (  # noqa: E402
    load_mf_dataset, resolve_grid, finalize_and_write, SMOKE,
    _cap_grid, _to_grid,
)
from model import (  # noqa: E402
    ConvAE, LatentDDIM, LatentMLPGenerator, param_count,
)

HERE = Path(__file__).resolve().parent
AE_PATH = HERE / "ae.pt"

# AE / generator config (kept tiny for fast smoke).
AE_CFG = dict(base_ch=32, latent_ch=16, latent_hw=(4, 4), zdim=64)
GEN_KIND = "diffusion"   # shipped path; "mlp" is the deterministic fallback
DDIM_TRAIN_STEPS = 200
DDIM_SAMPLE_STEPS = 10
UQ_K = 4


def _nrmse_agg(pred, target):
    p = np.asarray(pred, np.float64).reshape(pred.shape[0], -1)
    t = np.asarray(target, np.float64).reshape(target.shape[0], -1)
    return float(np.sqrt(((p - t) ** 2).sum() / max((t ** 2).sum(), 1e-12)))


def _train_ae(ae, Y, scaler, epochs, lr, grid, device, bs=16):
    if Y.shape[0] == 0 or epochs <= 0:
        return
    opt = torch.optim.AdamW(ae.parameters(), lr=lr, weight_decay=1e-5)
    Yt = torch.from_numpy(Y).float() / scaler
    n = Y.shape[0]
    g = torch.Generator().manual_seed(0)
    for ep in range(epochs):
        ae.train()
        perm = torch.randperm(n, generator=g)
        tot = 0.0
        for i in range(0, n, bs):
            idx = perm[i:i + bs]
            yb = Yt[idx].to(device)
            opt.zero_grad(set_to_none=True)
            recon = ae(yb, grid)
            loss = F.mse_loss(recon, yb)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(ae.parameters(), 1.0)
            opt.step()
            tot += float(loss.detach())
        if (ep + 1) % max(1, epochs // 5) == 0 or ep == epochs - 1:
            print(f"[AE {ep+1:04d}/{epochs}] mse={tot/max(1,(n+bs-1)//bs):.4e}", flush=True)


def _train_gen(gen, kind, Z_hf, COND, Z_lf, epochs, lr, device, bs=16):
    if Z_hf.shape[0] == 0 or epochs <= 0:
        return
    opt = torch.optim.AdamW(gen.parameters(), lr=lr, weight_decay=1e-5)
    n = Z_hf.shape[0]
    g = torch.Generator().manual_seed(0)
    for ep in range(epochs):
        gen.train()
        perm = torch.randperm(n, generator=g)
        tot = 0.0
        for i in range(0, n, bs):
            idx = perm[i:i + bs]
            z0 = Z_hf[idx].to(device); c = COND[idx].to(device); zl = Z_lf[idx].to(device)
            opt.zero_grad(set_to_none=True)
            if kind == "diffusion":
                loss = gen.loss(z0, c, zl)
            else:
                loss = F.mse_loss(gen(c, zl), z0)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(gen.parameters(), 1.0)
            opt.step()
            tot += float(loss.detach())
        if (ep + 1) % max(1, epochs // 5) == 0 or ep == epochs - 1:
            print(f"[GEN {ep+1:04d}/{epochs}] loss={tot/max(1,(n+bs-1)//bs):.4e}", flush=True)


def run(args, out_path: Path) -> dict:
    torch.manual_seed(args.seed); np.random.seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
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

    X_hf = train["cond_by_fid"][hf].astype(np.float32)
    Y_hf = _to_grid(train["field_by_fid"][hf], hf_grid_native, grid)
    Y_lf = _to_grid(train["field_by_fid"][lf], lf_grid_native, grid)
    X_te = test["cond_by_fid"][hf].astype(np.float32)
    Y_te = _to_grid(test["field_by_fid"][hf], hf_grid_native, grid)

    cond_dim = int(X_hf.shape[1])
    n_hf = X_hf.shape[0]
    # ifc_raw fidelities are index-aligned -> LF field for HF index i is Y_lf[i].
    Y_lf_aligned = Y_lf[:n_hf]
    # Scalers: AE trained in LF stats; HF latents encoded in HF stats. Use one
    # GLOBAL scaler (max|Y| over LF+HF train) so encode/decode units are shared.
    scaler = max(float(np.abs(Y_lf).max()), float(np.abs(Y_hf).max()), 1e-8)

    print(f"[data] {args.dataset_name} loader={train['loader']} LF={lf} HF={hf} "
          f"work_grid={grid} N_lf={Y_lf.shape[0]} N_hf={n_hf} N_test={X_te.shape[0]} "
          f"cond_dim={cond_dim} zdim={AE_CFG['zdim']} gen={GEN_KIND}", flush=True)

    ae = ConvAE(**AE_CFG).to(device)
    lf_dim = AE_CFG["zdim"]
    if GEN_KIND == "diffusion":
        gen = LatentDDIM(AE_CFG["zdim"], cond_dim, lf_dim, n_steps=DDIM_TRAIN_STEPS).to(device)
    else:
        gen = LatentMLPGenerator(AE_CFG["zdim"], cond_dim, lf_dim).to(device)
    n_params = param_count(ae, gen)

    ckpt_dir = Path(args.ckpt_dir); ckpt_dir.mkdir(parents=True, exist_ok=True)
    last = ckpt_dir / "last.pt"
    trained = False
    z_mu = torch.zeros(lf_dim); z_sd = torch.ones(lf_dim)   # latent standardization
    if last.exists():
        try:
            sd = torch.load(last, map_location=device, weights_only=False)
            if sd.get("epochs_target") == args.epochs and sd.get("grid") == list(grid):
                ae.load_state_dict(sd["ae"]); gen.load_state_dict(sd["gen"])
                z_mu = sd["z_mu"]; z_sd = sd["z_sd"]; trained = True
                print("[resume] loaded finished checkpoint", flush=True)
        except Exception as e:
            print(f"[resume] failed ({e}); fresh", flush=True)

    t_train = time.time()
    if not trained:
        # 1) AE prior on abundant LF fields.
        print(f"[stage] train AE on LF ({Y_lf.shape[0]} fields)", flush=True)
        _train_ae(ae, Y_lf, scaler, args.epochs, 1e-3, grid, device)
        ae.eval()
        # latent standardization stats from the abundant LF latents, so the
        # diffusion target matches the sampler's unit-variance prior (stability).
        with torch.no_grad():
            Z_lf_all = ae.encode(torch.from_numpy(Y_lf).float().to(device) / scaler).cpu()
        z_mu = Z_lf_all.mean(0); z_sd = Z_lf_all.std(0).clamp(min=1e-3)
        # 2) Encode HF targets and aligned LF -> standardized latents; train gen.
        with torch.no_grad():
            Z_hf = (ae.encode(torch.from_numpy(Y_hf).float().to(device) / scaler).cpu() - z_mu) / z_sd
            Z_lf = (ae.encode(torch.from_numpy(Y_lf_aligned).float().to(device) / scaler).cpu() - z_mu) / z_sd
        COND = torch.from_numpy(X_hf).float()
        print(f"[stage] train {GEN_KIND} generator ([X,z_lf]->z_hf, {n_hf} pairs)", flush=True)
        _train_gen(gen, GEN_KIND, Z_hf, COND, Z_lf, args.epochs, 1e-3, device)
        torch.save({"epochs_target": args.epochs, "grid": list(grid),
                    "ae": ae.state_dict(), "gen": gen.state_dict(),
                    "z_mu": z_mu, "z_sd": z_sd}, last)
    train_seconds = time.time() - t_train

    # EXPORT the AE for reuse by future latent-analysis families.
    torch.save({"ae": ae.state_dict(), "config": AE_CFG}, AE_PATH)
    print(f"[export] wrote AE -> {AE_PATH}", flush=True)

    # ── eval: condition on X with zero z_lf placeholder (test has no LF) ──
    ae.eval(); gen.eval()
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize()
    t_eval = time.time()
    Xt = torch.from_numpy(X_te).float().to(device)
    # eval z_lf placeholder: standardized-zero == the latent mean (test has no LF).
    z_lf_zero = torch.zeros(Xt.shape[0], lf_dim, device=device)
    z_mu_d = z_mu.to(device); z_sd_d = z_sd.to(device)
    sample_fields = []
    with torch.no_grad():
        for k in range(UQ_K):
            if GEN_KIND == "diffusion":
                gseed = torch.Generator(device=device).manual_seed(args.seed * 1000 + k)
                z_std = gen.sample(Xt, z_lf_zero, n_ddim=DDIM_SAMPLE_STEPS, generator=gseed)
            else:
                z_std = gen(Xt, z_lf_zero)  # deterministic; K copies identical
            z_hf = z_std * z_sd_d + z_mu_d                   # de-standardize
            field = ae.decode(z_hf, grid) * scaler          # raw units
            sample_fields.append(field.reshape(field.shape[0], -1).cpu().numpy())
    if device.type == "cuda":
        torch.cuda.synchronize()
    eval_seconds = time.time() - t_eval

    stack = np.stack(sample_fields, 0).astype(np.float64)   # (K, N, HW)
    pred = stack.mean(0)
    uq_mean_std = float(stack.std(0).mean())
    target = Y_te.reshape(Y_te.shape[0], -1).astype(np.float64)
    n_samples = int(target.shape[0])
    nrmse = _nrmse_agg(pred, target)
    print(f"[eval] nRMSE={nrmse:.6f} uq_mean_std={uq_mean_std:.6e}", flush=True)

    latency = (1000.0 * eval_seconds / max(n_samples, 1)) if device.type == "cuda" else None
    peak_mem = (torch.cuda.max_memory_allocated() / 1e6) if device.type == "cuda" else None

    return finalize_and_write(
        out_path=out_path, model="mf_fno_diffprior", dataset=args.dataset_name,
        pred=pred, target=target, work_grid=grid, n_params=int(n_params),
        train_seconds=train_seconds, eval_seconds=eval_seconds,
        latency_ms_per_sample=latency, peak_mem_mb=peak_mem, seed=args.seed,
        extra={"device": str(device), "hf_fidelity": int(hf), "lf_fidelity": int(lf),
               "mf_mechanism": "latent_AE_prior_on_LF_plus_conditional_latent_generation",
               "generator": GEN_KIND, "zdim": AE_CFG["zdim"],
               "ddim_sample_steps": DDIM_SAMPLE_STEPS if GEN_KIND == "diffusion" else None,
               "eval_lf_latent": "zero_placeholder_test_has_no_LF",
               "uq_K": UQ_K, "uq_mean_std": uq_mean_std,
               "ae_exported": str(AE_PATH),
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
    run(args, out)
    print(f"[wrote] {out}", flush=True)


if __name__ == "__main__":
    main()
