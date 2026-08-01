"""DINO-embedding-conditioned HF correction (FNO backbone).

Tests the user hypothesis: does a pretrained vision foundation model (DINO) help
multi-fidelity field prediction by supplying a rich global descriptor of the LF
field as an extra feature?

    1. FNO_LF: train on abundant LF data (cond -> LF field).
    2. DINO (frozen): LF_pred(x) -> 3-channel 224x224 image -> CLS embedding e in R^768.
       FNO_LF is frozen after stage 1, so e is FIXED per input -> precomputed ONCE
       (no per-epoch DINO cost).
    3. FNO_delta: conditioned on [cond x, proj(e)] predicts the residual HF - LF_pred
       (residual mode, default) or HF directly (direct mode). Final HF = LF_pred + delta.

Ablation partner: fno_additive (same two-FNO additive rule WITHOUT the DINO feature)
isolates the DINO contribution. DINO defaults to DINOv2-base (open, locally cached);
set DINO_MODEL_ID = a dinov3-* repo + an HF token to use the latest gated model.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model import FNO2d, DinoConditionedFNO, param_count  # noqa: E402
from data_adapters import load_mf_dataset  # noqa: E402
from data_adapters.geometry import resolve_grid  # noqa: E402
from data_adapters.metrics import finalize_and_write  # noqa: E402

# Use the locally-cached weights; never hit the network on compute nodes.
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

WORK_CAP = 256
DINO_MODEL_ID = "facebook/dinov2-base"      # swap to a dinov3-* repo (+HF token) for latest
DINO_DIM = 768
DINO_RES = 224
IMAGENET_MEAN = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)
IMAGENET_STD = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)
SMOKE = dict(hidden_channels=64, n_blocks=4, modes_cap=12, batch_size=16,
             lr=1e-3, weight_decay=1e-5, grad_clip=1.0, d_emb=64, mode="residual",
             dino_batch=16)


def _cap_grid(grid, cap=WORK_CAP):
    H, W = int(grid[0]), int(grid[1]); m = max(H, W)
    if m <= cap:
        return (H, W)
    f = cap / m
    return (max(1, round(H * f)), max(1, round(W * f)))


def _modes(grid, cap):
    H, W = grid
    return (min(cap, max(H // 2, 1)), min(cap, W // 2 + 1))


sys.path.insert(0, str(HERE.parent))  # models/ -> _common package
from _common.lf_registration import resample_fields  # noqa: E402


def _to_grid(y_flat, src, dst, dataset_name):
    """Resample under the dataset's registration convention
    (models/_common/lf_registration.py; registration defect note item 1)."""
    return resample_fields(y_flat, src, dst, dataset_name)


def _train(model, X, target, scaler, epochs, lr, p, device, seed):
    if X.shape[0] == 0 or epochs <= 0:
        return
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=p["weight_decay"])
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(epochs, 1), eta_min=1e-6)
    Xt = torch.from_numpy(X).float(); Yt = torch.from_numpy(target).float() / scaler
    n = X.shape[0]; bs = min(p["batch_size"], n)
    g = torch.Generator().manual_seed(seed)
    for _ in range(epochs):
        model.train()
        perm = torch.randperm(n, generator=g)
        for i in range(0, n, bs):
            idx = perm[i:i + bs]
            xb = Xt[idx].to(device); yb = Yt[idx].to(device)
            opt.zero_grad(set_to_none=True)
            loss = F.mse_loss(model(xb), yb)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), p["grad_clip"])
            opt.step()
        sched.step()


def _train_dino(model, X, emb, target, scaler, epochs, lr, p, device, seed):
    if X.shape[0] == 0 or epochs <= 0:
        return
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=p["weight_decay"])
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(epochs, 1), eta_min=1e-6)
    Xt = torch.from_numpy(X).float(); Et = torch.from_numpy(emb).float()
    Yt = torch.from_numpy(target).float() / scaler
    n = X.shape[0]; bs = min(p["batch_size"], n)
    g = torch.Generator().manual_seed(seed)
    for _ in range(epochs):
        model.train()
        perm = torch.randperm(n, generator=g)
        for i in range(0, n, bs):
            idx = perm[i:i + bs]
            xb = Xt[idx].to(device); eb = Et[idx].to(device); yb = Yt[idx].to(device)
            opt.zero_grad(set_to_none=True)
            loss = F.mse_loss(model(xb, eb), yb)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), p["grad_clip"])
            opt.step()
        sched.step()


@torch.no_grad()
def _predict_field(model, X, scaler, device, bs):
    model.eval(); out = []
    for i in range(0, X.shape[0], bs):
        xb = torch.from_numpy(X[i:i + bs]).float().to(device)
        out.append((model(xb) * scaler).cpu().numpy())
    return np.concatenate(out, 0).astype(np.float32)


@torch.no_grad()
def _predict_dino(model, X, emb, scaler, device, bs):
    model.eval(); out = []
    for i in range(0, X.shape[0], bs):
        xb = torch.from_numpy(X[i:i + bs]).float().to(device)
        eb = torch.from_numpy(emb[i:i + bs]).float().to(device)
        out.append((model(xb, eb) * scaler).cpu().numpy())
    return np.concatenate(out, 0).astype(np.float32)


@torch.no_grad()
def _dino_embed(dino, fields, device, bs):
    """fields (N,H,W) raw units -> DINO CLS embeddings (N, DINO_DIM).

    Per-sample standardize -> [0,1], replicate to 3 channels, resize to 224,
    ImageNet-normalize, run frozen DINO, take the CLS token.
    """
    mean = IMAGENET_MEAN.to(device); std = IMAGENET_STD.to(device)
    out = []
    for i in range(0, fields.shape[0], bs):
        f = torch.from_numpy(fields[i:i + bs]).float().to(device).unsqueeze(1)  # (b,1,H,W)
        b = f.shape[0]
        fmin = f.amin(dim=(2, 3), keepdim=True); fmax = f.amax(dim=(2, 3), keepdim=True)
        f = (f - fmin) / (fmax - fmin + 1e-8)
        img = f.expand(b, 3, f.shape[2], f.shape[3])
        img = F.interpolate(img, size=(DINO_RES, DINO_RES), mode="bilinear", align_corners=False)
        img = (img - mean) / std
        cls = dino(pixel_values=img).last_hidden_state[:, 0]   # (b, DINO_DIM)
        out.append(cls.float().cpu().numpy())
    return np.concatenate(out, 0).astype(np.float32)


def _load_dino(device):
    from transformers import AutoModel
    dino = AutoModel.from_pretrained(DINO_MODEL_ID).to(device).eval()
    for prm in dino.parameters():
        prm.requires_grad_(False)
    return dino


def run(args, out_path: Path) -> dict:
    torch.manual_seed(args.seed); np.random.seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    p = SMOKE
    ds_dir = Path(args.dataset_dir)
    train = load_mf_dataset(ds_dir, "train"); test = load_mf_dataset(ds_dir, "test")
    hf = train["hf_fid"]; lf = min(train["lf_fids"]) if train["lf_fids"] else hf
    if hf not in test["fids"]:
        hf = test["hf_fid"]

    hf_native = resolve_grid(args.dataset_name, int(train["n_cells_by_fid"][hf]))
    lf_native = resolve_grid(args.dataset_name, int(train["n_cells_by_fid"][lf]))
    grid = _cap_grid(hf_native); mh, mw = _modes(grid, p["modes_cap"])

    X_lf = train["cond_by_fid"][lf].astype(np.float32)
    Y_lf = _to_grid(train["field_by_fid"][lf], lf_native, grid, args.dataset_name)
    X_hf = train["cond_by_fid"][hf].astype(np.float32)
    Y_hf = _to_grid(train["field_by_fid"][hf], hf_native, grid, args.dataset_name)
    X_te = test["cond_by_fid"][hf].astype(np.float32)
    Y_te = _to_grid(test["field_by_fid"][hf], hf_native, grid, args.dataset_name)
    cond_dim = int(X_hf.shape[1])
    s_lf = max(float(np.abs(Y_lf).max()), 1e-8) if Y_lf.size else 1.0
    s_hf = max(float(np.abs(Y_hf).max()), 1e-8) if Y_hf.size else 1.0
    direct = (p["mode"] == "direct")

    print(f"[data] {args.dataset_name} LF={lf} HF={hf} work_grid={grid} mode={p['mode']} "
          f"dino={DINO_MODEL_ID} N_lf={X_lf.shape[0]} N_hf={X_hf.shape[0]} N_test={X_te.shape[0]}", flush=True)

    fno_lf = FNO2d(cond_dim, p["hidden_channels"], p["n_blocks"], mh, mw, grid).to(device)
    fno_d = DinoConditionedFNO(cond_dim, DINO_DIM, p["d_emb"], p["hidden_channels"],
                               p["n_blocks"], mh, mw, grid).to(device)
    n_params = param_count(fno_lf) + param_count(fno_d)  # trainable params (DINO frozen, excluded)

    dino = _load_dino(device)

    ckpt_dir = Path(args.ckpt_dir); ckpt_dir.mkdir(parents=True, exist_ok=True)
    last = ckpt_dir / "last.pt"
    trained = False; res_scaler = s_hf
    if last.exists():
        try:
            sd = torch.load(last, map_location=device, weights_only=False)
            if sd.get("epochs_target") == args.epochs and sd.get("grid") == list(grid) \
               and sd.get("mode") == p["mode"]:
                fno_lf.load_state_dict(sd["fno_lf"]); fno_d.load_state_dict(sd["fno_d"])
                res_scaler = sd.get("res_scaler", s_hf); trained = True
                print("[resume] loaded", flush=True)
        except Exception as e:
            print(f"[resume] failed ({e})", flush=True)

    t_train = time.time()
    if not trained:
        print("[stage1] train FNO_LF on LF", flush=True)
        _train(fno_lf, X_lf, Y_lf, s_lf, args.epochs, p["lr"], p, device, seed=args.seed + 1)
        # frozen LF predictions on HF inputs -> DINO embeddings (precomputed once)
        lf_on_hf = _predict_field(fno_lf, X_hf, s_lf, device, p["batch_size"])
        emb_hf = _dino_embed(dino, lf_on_hf, device, p["dino_batch"])
        tgt = Y_hf if direct else (Y_hf - lf_on_hf).astype(np.float32)
        res_scaler = (s_hf if direct else max(float(np.abs(tgt).max()), 1e-8)) if tgt.size else 1.0
        print(f"[stage2] train DINO-conditioned FNO_delta ({p['mode']})", flush=True)
        _train_dino(fno_d, X_hf, emb_hf, tgt, res_scaler, args.epochs, p["lr"], p, device, seed=args.seed)
        torch.save({"epochs_target": args.epochs, "grid": list(grid), "mode": p["mode"],
                    "fno_lf": fno_lf.state_dict(), "fno_d": fno_d.state_dict(),
                    "res_scaler": res_scaler}, last)
    train_seconds = time.time() - t_train

    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize()
    t_eval = time.time()
    lf_te = _predict_field(fno_lf, X_te, s_lf, device, p["batch_size"])
    emb_te = _dino_embed(dino, lf_te, device, p["dino_batch"])
    d_te = _predict_dino(fno_d, X_te, emb_te, res_scaler, device, p["batch_size"])
    pred = (d_te if direct else (lf_te + d_te)).reshape(X_te.shape[0], -1).astype(np.float64)
    if device.type == "cuda":
        torch.cuda.synchronize()
    eval_seconds = time.time() - t_eval
    target = Y_te.reshape(Y_te.shape[0], -1).astype(np.float64)
    n = int(target.shape[0])
    latency = (1000.0 * eval_seconds / max(n, 1)) if device.type == "cuda" else None
    peak = (torch.cuda.max_memory_allocated() / 1e6) if device.type == "cuda" else None

    return finalize_and_write(
        out_path=out_path, model="fno_dino_residual", dataset=args.dataset_name,
        pred=pred, target=target, work_grid=grid, n_params=int(n_params),
        train_seconds=train_seconds, eval_seconds=eval_seconds,
        latency_ms_per_sample=latency, peak_mem_mb=peak, seed=args.seed,
        extra={"device": str(device), "hf_fidelity": int(hf), "lf_fidelity": int(lf),
               "mf_mechanism": f"DINO_embedding_conditioned_{p['mode']}_HF=LFpred+delta(x,DINO(LF))",
               "dino_model": DINO_MODEL_ID, "dino_dim": DINO_DIM, "fusion": "concat_broadcast",
               "predict_mode": p["mode"], "work_grid": list(grid)},
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
