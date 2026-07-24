"""Recursive multi-level correction (FNO backbone).

Survey family 3 (Peherstorfer et al.): recursive / hierarchical correction across
MORE THAN TWO fidelities — correct each level using the one below it, a recursive
co-kriging-style chain (Le Gratiet 2014 / Perdikaris 2017 nonlinear autoregressive).

For fidelity levels 0 (coarsest) .. L (HF), one FNO per level:

    pred_0(x) = FNO_0(cond=x)
    pred_k(x) = FNO_k(cond=x, prev_field=pred_{k-1}(x)),   k = 1 .. L

i.e. each level predicts its OWN field DIRECTLY, conditioned on (the cond vector
AND) the lower level's predicted field fed as an extra input channel. Final
prediction = pred_L (the recursion run bottom-up at inference).

NOTE — stability: an earlier version summed independently-scaled per-level residuals
(pred_k = pred_{k-1} + FNO_k(residual)); that telescoping SUM accumulated error
across levels and blew up (rel-L2 ~18 on a 3-level dataset). Predicting each level's
field directly (every output bounded by its own scaler) is the numerically stable
Perdikaris-style recursion and removes the blow-up.

DISTINCT from fno_mf_stack: stack runs N coarse-native FNOs and fuses ALL of them
AT ONCE through a single MLP aggregator (decoder-in-the-aggregation) + one HF delta.
This model is a STRICT SEQUENTIAL CASCADE — each level conditions only on the level
directly below it, recursing bottom-up — every per-level FNO at the common working
grid. The only family here that recursively exploits the full fidelity ladder
(heat_local=5, era5=9, poisson_local=5 levels; generated=3). On 2-fidelity datasets
it reduces to one conditioning step (≈ a learned nonlinear LF→HF map).

Shares the verified plumbing (resolve_grid + 256-cap working grid, full-field eval,
finalize_and_write). Contract + resume identical.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent.parent
sys.path.insert(0, str(HERE))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model import FNO2d, FNO2dCond, param_count  # noqa: E402
from data_adapters import load_mf_dataset  # noqa: E402
from data_adapters.geometry import resolve_grid  # noqa: E402
from data_adapters.metrics import finalize_and_write  # noqa: E402

WORK_CAP = 256
SMOKE = dict(hidden_channels=64, n_blocks=4, modes_cap=12, batch_size=16,
             lr=1e-3, weight_decay=1e-5, grad_clip=1.0)
# hidden=48/n_blocks=3 (a touch smaller than the 64/4 used by 2-fidelity families)
# because this trains ONE FNO PER LEVEL — keeps total params comparable on the
# many-fidelity datasets (era5=9 levels) instead of ballooning.


def _cap_grid(grid, cap=WORK_CAP):
    H, W = int(grid[0]), int(grid[1]); m = max(H, W)
    if m <= cap:
        return (H, W)
    f = cap / m
    return (max(1, round(H * f)), max(1, round(W * f)))


def _modes(grid, cap):
    H, W = grid
    return (min(cap, max(H // 2, 1)), min(cap, W // 2 + 1))


def _to_grid(y_flat, src, dst):
    Hs, Ws = int(src[0]), int(src[1]); Hd, Wd = int(dst[0]), int(dst[1])
    t = torch.from_numpy(np.ascontiguousarray(y_flat, dtype=np.float32)).view(-1, 1, Hs, Ws)
    if (Hs, Ws) != (Hd, Wd):
        t = F.interpolate(t, size=(Hd, Wd), mode="bilinear", align_corners=False)
    return t.squeeze(1).numpy().astype(np.float32)


def _train(model, X, target, scaler, epochs, lr, p, device, prev_field=None):
    """Train model(cond[, prev_field]) -> target/scaler. prev_field (raw units,
    (N,H,W)) is the lower level's predicted field, scaled by `scaler` to match the
    target's normalization before being fed as a channel."""
    if X.shape[0] == 0 or epochs <= 0:
        return
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=p["weight_decay"])
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(epochs, 1), eta_min=1e-6)
    Xt = torch.from_numpy(X).float(); Yt = torch.from_numpy(target).float() / scaler
    Pt = None if prev_field is None else torch.from_numpy(prev_field).float() / scaler
    n = X.shape[0]; bs = min(p["batch_size"], n); g = torch.Generator().manual_seed(0)
    for ep in range(epochs):
        model.train(); perm = torch.randperm(n, generator=g)
        for i in range(0, n, bs):
            idx = perm[i:i + bs]; xb = Xt[idx].to(device); yb = Yt[idx].to(device)
            pb = None if Pt is None else Pt[idx].to(device)
            opt.zero_grad(set_to_none=True)
            out = model(xb, pb) if pb is not None else model(xb)
            loss = F.mse_loss(out, yb); loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), p["grad_clip"]); opt.step()
        sched.step()


@torch.no_grad()
def _predict(model, X, scaler, device, bs, prev_field=None):
    """Raw-units field prediction. prev_field (N,H,W raw) scaled by `scaler` to feed."""
    model.eval(); out = []
    Pt = None if prev_field is None else torch.from_numpy(prev_field).float() / scaler
    for i in range(0, X.shape[0], bs):
        xb = torch.from_numpy(X[i:i + bs]).float().to(device)
        pb = None if Pt is None else Pt[i:i + bs].to(device)
        pr = model(xb, pb) if pb is not None else model(xb)
        out.append((pr * scaler).cpu().numpy())
    return np.concatenate(out, 0).astype(np.float32)


def run(args, out_path: Path) -> dict:
    torch.manual_seed(args.seed); np.random.seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    p = SMOKE
    ds_dir = Path(args.dataset_dir)
    train = load_mf_dataset(ds_dir, "train"); test = load_mf_dataset(ds_dir, "test")
    fids = sorted(train["fids"])                       # ascending: coarse..HF
    hf = train["hf_fid"]
    if hf not in test["fids"]:
        hf = test["hf_fid"]

    grid = _cap_grid(resolve_grid(args.dataset_name, int(train["n_cells_by_fid"][hf])))
    mh, mw = _modes(grid, p["modes_cap"])
    cond_dim = int(train["cond_by_fid"][hf].shape[1])

    # Per-level training data on the common working grid.
    levels = []  # list of dict(fid, X, Y)
    for f in fids:
        nat = resolve_grid(args.dataset_name, int(train["n_cells_by_fid"][f]))
        levels.append({
            "fid": f,
            "X": train["cond_by_fid"][f].astype(np.float32),
            "Y": _to_grid(train["field_by_fid"][f], nat, grid),
        })
    hf_native = resolve_grid(args.dataset_name, int(train["n_cells_by_fid"][hf]))
    X_te = test["cond_by_fid"][hf].astype(np.float32)
    Y_te = _to_grid(test["field_by_fid"][hf], hf_native, grid)

    print(f"[data] {args.dataset_name} fids={fids} (L={len(fids)}) HF={hf} "
          f"work_grid={grid} N_test={X_te.shape[0]}", flush=True)

    # One FNO per level. Level 0 takes cond only; higher levels also ingest the
    # lower level's predicted field (stable Perdikaris-style recursion — predicts
    # each level's field DIRECTLY, so outputs can't accumulate/blow up).
    fnos = []
    for li in range(len(fids)):
        fnos.append(FNO2dCond(cond_dim, p["hidden_channels"], p["n_blocks"], mh, mw, grid,
                              use_prev=(li > 0)).to(device))
    n_params = sum(param_count(m) for m in fnos)

    ckpt_dir = Path(args.ckpt_dir); ckpt_dir.mkdir(parents=True, exist_ok=True)
    last = ckpt_dir / "last.pt"; trained = False
    scalers = [1.0] * len(fids)
    if last.exists():
        try:
            sd = torch.load(last, map_location=device, weights_only=False)
            if sd.get("epochs_target") == args.epochs and sd.get("grid") == list(grid) \
               and len(sd.get("fnos", [])) == len(fnos):
                for m, st in zip(fnos, sd["fnos"]):
                    m.load_state_dict(st)
                scalers = sd["scalers"]; trained = True
                print("[resume] loaded", flush=True)
        except Exception as e:
            print(f"[resume] failed ({e})", flush=True)

    t_train = time.time()
    if not trained:
        # Level 0 (coarsest): predict its field directly from cond.
        s0 = max(float(np.abs(levels[0]["Y"]).max()), 1e-8)
        scalers[0] = s0
        print(f"[lvl 0 fid={fids[0]}] train field from cond (scaler={s0:.3g})", flush=True)
        _train(fnos[0], levels[0]["X"], levels[0]["Y"], s0, args.epochs, p["lr"], p, device)
        # Levels 1..L: predict THIS level's field directly, conditioned on the lower
        # level's predicted field (teacher-forced with the trained lower FNO).
        for k in range(1, len(fids)):
            Xk = levels[k]["X"]; Yk = levels[k]["Y"]
            sk = max(float(np.abs(Yk).max()), 1e-8) if Yk.size else 1.0
            scalers[k] = sk
            prev = _predict(fnos[k - 1], Xk, scalers[k - 1], device, p["batch_size"])  # raw
            print(f"[lvl {k} fid={fids[k]}] train field cond on lvl {k-1} pred (scaler={sk:.3g})", flush=True)
            _train(fnos[k], Xk, Yk, sk, args.epochs, p["lr"], p, device, prev_field=prev)
        torch.save({"epochs_target": args.epochs, "grid": list(grid),
                    "fnos": [m.state_dict() for m in fnos], "scalers": scalers}, last)
    train_seconds = time.time() - t_train

    # Inference: recurse up the ladder — each level's prediction feeds the next.
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize()
    t_eval = time.time()
    pred_cur = _predict(fnos[0], X_te, scalers[0], device, p["batch_size"])  # raw
    for k in range(1, len(fids)):
        pred_cur = _predict(fnos[k], X_te, scalers[k], device, p["batch_size"], prev_field=pred_cur)
    if device.type == "cuda":
        torch.cuda.synchronize()
    eval_seconds = time.time() - t_eval
    pred = pred_cur.reshape(X_te.shape[0], -1).astype(np.float64)
    target = Y_te.reshape(Y_te.shape[0], -1).astype(np.float64)
    n = int(target.shape[0])
    latency = (1000.0 * eval_seconds / max(n, 1)) if device.type == "cuda" else None
    peak = (torch.cuda.max_memory_allocated() / 1e6) if device.type == "cuda" else None

    return finalize_and_write(
        out_path=out_path, model="fno_multilevel", dataset=args.dataset_name,
        pred=pred, target=target, work_grid=grid, n_params=int(n_params),
        train_seconds=train_seconds, eval_seconds=eval_seconds,
        latency_ms_per_sample=latency, peak_mem_mb=peak, seed=args.seed,
        extra={"device": str(device), "n_levels": len(fids), "fids": [int(f) for f in fids],
               "mf_mechanism": "recursive_multilevel_nonlinear_autoregressive_field_cascade",
               "work_grid": list(grid)},
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
