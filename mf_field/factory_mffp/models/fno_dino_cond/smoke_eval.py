"""DINO-embedding-conditioned multi-fidelity FNO.

Hypothesis: a frozen self-supervised vision foundation model (DINO) extracts
structural features from the LF predicted field that improve HF prediction.

Stages:
  1. FNO_LF: cond x -> LF field (trained on abundant LF data).
  2. DINO (frozen): featurize LF_pred(x) -> 768-d CLS embedding. Computed ONCE for
     the HF-train and test inputs (DINO + FNO_LF are frozen during HF training).
  3. FNO_HF (FNO2dDino): condition = [pde_params, proj(DINO emb)] -> predicts the
     residual (HF - LF_pred)  [MODE=residual]  or the HF field  [MODE=direct].

DINO model: facebook/dinov2-base (cached, open). DINOv3 (latest) is gated on HF;
swap DINO_MODEL_ID once access + an HF token are available — the 768-d ViT-B
interface is identical, so no other change is needed.

Shares the verified plumbing (resolve_grid + 256-cap working grid, full-field eval,
finalize_and_write per-sample rel-L2 + bootstrap CI).
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

os.environ.setdefault("HF_HUB_OFFLINE", "1")       # use the local cache on compute nodes
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]            # factory_mffp/
sys.path.insert(0, str(HERE))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model import FNO2d, FNO2dDino, param_count  # noqa: E402
from data_adapters import load_mf_dataset  # noqa: E402
from data_adapters.geometry import resolve_grid  # noqa: E402
from data_adapters.metrics import finalize_and_write  # noqa: E402

WORK_CAP = 256
DINO_MODEL_ID = "facebook/dinov2-base"   # swap to facebook/dinov3-vitb16-* once access granted
MODE = "residual"                        # "residual" (HF = LF + delta) or "direct" (HF)
SMOKE = dict(hidden_channels=64, n_blocks=4, modes_cap=12, batch_size=16,
             lr=1e-3, weight_decay=1e-5, grad_clip=1.0, dino_proj=32, dino_bs=16)
_IMAGENET_MEAN = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)
_IMAGENET_STD = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)


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
    n = X.shape[0]; bs = min(p["batch_size"], n); g = torch.Generator().manual_seed(seed)
    for _ in range(epochs):
        model.train(); perm = torch.randperm(n, generator=g)
        for i in range(0, n, bs):
            idx = perm[i:i + bs]
            xb = Xt[idx].to(device); yb = Yt[idx].to(device)
            opt.zero_grad(set_to_none=True)
            loss = F.mse_loss(model(xb), yb); loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), p["grad_clip"]); opt.step()
        sched.step()


def _train_dino(model, X, emb, target, scaler, epochs, lr, p, device, seed):
    if X.shape[0] == 0 or epochs <= 0:
        return
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=p["weight_decay"])
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(epochs, 1), eta_min=1e-6)
    Xt = torch.from_numpy(X).float(); Et = torch.from_numpy(emb).float()
    Yt = torch.from_numpy(target).float() / scaler
    n = X.shape[0]; bs = min(p["batch_size"], n); g = torch.Generator().manual_seed(seed)
    for _ in range(epochs):
        model.train(); perm = torch.randperm(n, generator=g)
        for i in range(0, n, bs):
            idx = perm[i:i + bs]
            xb = Xt[idx].to(device); eb = Et[idx].to(device); yb = Yt[idx].to(device)
            opt.zero_grad(set_to_none=True)
            loss = F.mse_loss(model(xb, eb), yb); loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), p["grad_clip"]); opt.step()
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
    """fields (N, H, W) raw -> DINO CLS embeddings (N, dino_dim).

    Per-sample min-max to [0,1], resize to 224, replicate to 3 channels, ImageNet-
    normalize, then take the CLS token. DINO stays frozen.
    """
    mean = _IMAGENET_MEAN.to(device); std = _IMAGENET_STD.to(device)
    out = []
    for i in range(0, fields.shape[0], bs):
        f = torch.from_numpy(fields[i:i + bs]).float().to(device).unsqueeze(1)  # (b,1,H,W)
        lo = f.amin(dim=(2, 3), keepdim=True); hi = f.amax(dim=(2, 3), keepdim=True)
        f = (f - lo) / (hi - lo + 1e-8)
        f = F.interpolate(f, size=(224, 224), mode="bilinear", align_corners=False)
        f = f.repeat(1, 3, 1, 1)
        f = (f - mean) / std
        emb = dino(pixel_values=f).last_hidden_state[:, 0]   # CLS token (b, dim)
        out.append(emb.float().cpu().numpy())
    return np.concatenate(out, 0).astype(np.float32)


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
    pde_dim = int(X_hf.shape[1])
    s_lf = max(float(np.abs(Y_lf).max()), 1e-8) if Y_lf.size else 1.0

    # frozen DINO
    from transformers import AutoModel
    dino = AutoModel.from_pretrained(DINO_MODEL_ID).to(device).eval()
    for q in dino.parameters():
        q.requires_grad_(False)
    dino_dim = int(dino.config.hidden_size)

    print(f"[data] {args.dataset_name} LF={lf} HF={hf} work_grid={grid} mode={MODE} "
          f"dino={DINO_MODEL_ID}({dino_dim}) N_lf={X_lf.shape[0]} N_hf={X_hf.shape[0]} "
          f"N_test={X_te.shape[0]}", flush=True)

    fno_lf = FNO2d(pde_dim, p["hidden_channels"], p["n_blocks"], mh, mw, grid).to(device)
    fno_hf = FNO2dDino(pde_dim, dino_dim, p["dino_proj"], p["hidden_channels"],
                       p["n_blocks"], mh, mw, grid).to(device)
    n_params = param_count(fno_lf) + param_count(fno_hf)   # trainable nets (DINO frozen, excluded)

    ckpt_dir = Path(args.ckpt_dir); ckpt_dir.mkdir(parents=True, exist_ok=True)
    last = ckpt_dir / "last.pt"
    trained = False; res_scaler = 1.0
    if last.exists():
        try:
            sd = torch.load(last, map_location=device, weights_only=False)
            if sd.get("epochs_target") == args.epochs and sd.get("grid") == list(grid) \
               and sd.get("mode") == MODE and sd.get("dino") == DINO_MODEL_ID:
                fno_lf.load_state_dict(sd["fno_lf"]); fno_hf.load_state_dict(sd["fno_hf"])
                res_scaler = sd.get("res_scaler", 1.0); trained = True
                print("[resume] loaded", flush=True)
        except Exception as e:
            print(f"[resume] failed ({e})", flush=True)

    t_train = time.time()
    if not trained:
        print("[stage1] train FNO_LF on LF", flush=True)
        _train(fno_lf, X_lf, Y_lf, s_lf, args.epochs, p["lr"], p, device, seed=args.seed + 1)
        # LF predictions on HF-train inputs -> DINO embeddings (frozen, computed once)
        lf_on_hf = _predict_field(fno_lf, X_hf, s_lf, device, p["batch_size"])
        emb_hf = _dino_embed(dino, lf_on_hf, device, p["dino_bs"])
        if MODE == "residual":
            tgt = (Y_hf - lf_on_hf).astype(np.float32)
        else:
            tgt = Y_hf
        res_scaler = max(float(np.abs(tgt).max()), 1e-8) if tgt.size else 1.0
        print(f"[stage2] train FNO_HF ({MODE}) on [pde, DINO(LF_pred)]", flush=True)
        _train_dino(fno_hf, X_hf, emb_hf, tgt, res_scaler, args.epochs, p["lr"], p,
                    device, seed=args.seed)
        torch.save({"epochs_target": args.epochs, "grid": list(grid), "mode": MODE,
                    "dino": DINO_MODEL_ID, "fno_lf": fno_lf.state_dict(),
                    "fno_hf": fno_hf.state_dict(), "res_scaler": res_scaler}, last)
    train_seconds = time.time() - t_train

    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize()
    t_eval = time.time()
    lf_te = _predict_field(fno_lf, X_te, s_lf, device, p["batch_size"])
    emb_te = _dino_embed(dino, lf_te, device, p["dino_bs"])
    hf_out = _predict_dino(fno_hf, X_te, emb_te, res_scaler, device, p["batch_size"])
    pred = (lf_te + hf_out if MODE == "residual" else hf_out).reshape(X_te.shape[0], -1).astype(np.float64)
    if device.type == "cuda":
        torch.cuda.synchronize()
    eval_seconds = time.time() - t_eval
    target = Y_te.reshape(Y_te.shape[0], -1).astype(np.float64)
    n = int(target.shape[0])
    latency = (1000.0 * eval_seconds / max(n, 1)) if device.type == "cuda" else None
    peak = (torch.cuda.max_memory_allocated() / 1e6) if device.type == "cuda" else None

    return finalize_and_write(
        out_path=out_path, model="fno_dino_cond", dataset=args.dataset_name,
        pred=pred, target=target, work_grid=grid, n_params=int(n_params),
        train_seconds=train_seconds, eval_seconds=eval_seconds,
        latency_ms_per_sample=latency, peak_mem_mb=peak, seed=args.seed,
        extra={"device": str(device), "hf_fidelity": int(hf), "lf_fidelity": int(lf),
               "mf_mechanism": f"DINO_embedding_conditioned_HF_{MODE}",
               "dino_model": DINO_MODEL_ID, "dino_dim": dino_dim, "fusion": "concat_cls",
               "mode": MODE, "work_grid": list(grid)},
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
