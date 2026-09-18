"""sys.path shim onto factory_mffp + shared fair-eval plumbing & train helpers.

Importing this module:
  1. puts `factory_mffp/` on sys.path so `from data_adapters import ...` works,
  2. re-exports the fair-eval API every family must use for comparable numbers:
       load_mf_dataset, resolve_grid, finalize_and_write
  3. exposes the shared working-grid + training helpers (WORK_CAP, SMOKE,
     _cap_grid, _modes, _to_grid, train_loop) lifted from the winner's
     smoke_eval.py so every family trains/evaluates on the identical 256-cap grid
     with the identical optimizer schedule. A family overrides only what its
     mechanism requires.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

# ── locate factory_mffp (…/mf_field/factory_mffp) relative to this file ──
#   this file: …/mf_field/akash/common/mffp.py
MF_FIELD_ROOT = Path(__file__).resolve().parents[2]      # …/mf_field
FACTORY_ROOT = MF_FIELD_ROOT / "factory_mffp"
if str(FACTORY_ROOT) not in sys.path:
    sys.path.insert(0, str(FACTORY_ROOT))

from data_adapters import load_mf_dataset                 # noqa: E402
from data_adapters.geometry import resolve_grid           # noqa: E402
from data_adapters.metrics import finalize_and_write      # noqa: E402

__all__ = [
    "FACTORY_ROOT", "MF_FIELD_ROOT", "WORK_CAP", "SMOKE",
    "load_mf_dataset", "resolve_grid", "finalize_and_write",
    "_cap_grid", "_modes", "_to_grid", "train_loop",
]

WORK_CAP = 256
# Same hyperparameters as the winner so the comparison isolates the mechanism.
SMOKE = dict(hidden_channels=64, n_blocks=4, modes_cap=12, batch_size=16,
             lr_pretrain=1e-3, lr_finetune=3e-4, weight_decay=1e-5, grad_clip=1.0)


def _cap_grid(grid, cap: int = WORK_CAP):
    H, W = int(grid[0]), int(grid[1])
    m = max(H, W)
    if m <= cap:
        return (H, W)
    f = cap / m
    return (max(1, round(H * f)), max(1, round(W * f)))


def _modes(grid, cap):
    H, W = grid
    return (min(cap, max(H // 2, 1)), min(cap, W // 2 + 1))


def _to_grid(y_flat: np.ndarray, src_grid, dst_grid) -> np.ndarray:
    """(N, prod(src)) flat -> (N, Hd, Wd) on the working grid (bilinear)."""
    Hs, Ws = int(src_grid[0]), int(src_grid[1])
    Hd, Wd = int(dst_grid[0]), int(dst_grid[1])
    t = torch.from_numpy(np.ascontiguousarray(y_flat, dtype=np.float32)).view(-1, 1, Hs, Ws)
    if (Hs, Ws) != (Hd, Wd):
        t = F.interpolate(t, size=(Hd, Wd), mode="bilinear", align_corners=False)
    return t.squeeze(1).numpy().astype(np.float32)


def train_loop(model, X, Y, scaler, epochs, lr, p, device, tag, cond_fn=None):
    """Train `model` on (X cond, Y field-on-grid), supervised in y/scaler space.

    cond_fn: optional callable(xb_cond_batch) -> model input, default identity.
        Families whose forward signature differs (e.g. extra fidelity scalar)
        pass a closure here instead of rewriting the loop.
    """
    if X.shape[0] == 0 or epochs <= 0:
        return
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=p["weight_decay"])
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(epochs, 1), eta_min=1e-6)
    Xt = torch.from_numpy(X).float()
    Yt = torch.from_numpy(Y).float() / scaler
    n = X.shape[0]
    bs = min(p["batch_size"], n)
    g = torch.Generator().manual_seed(0)
    for ep in range(epochs):
        model.train()
        perm = torch.randperm(n, generator=g)
        tot = 0.0
        for i in range(0, n, bs):
            idx = perm[i:i + bs]
            xb = Xt[idx].to(device); yb = Yt[idx].to(device)
            opt.zero_grad(set_to_none=True)
            pred = model(cond_fn(xb)) if cond_fn else model(xb)
            loss = F.mse_loss(pred, yb)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), p["grad_clip"])
            opt.step()
            tot += float(loss.detach())
        sched.step()
        if (ep + 1) % max(1, epochs // 5) == 0 or ep == epochs - 1:
            print(f"[{tag} {ep+1:04d}/{epochs}] mse={tot/max(1,(n+bs-1)//bs):.4e}", flush=True)
