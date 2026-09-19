"""Correction-track benchmark: shared data loading, prolongation, metrics, result I/O.

Task: predict the HF field of a test instance from (theta, REAL coarse solves of that instance).
Data layout: <root>/<rel>/{train,test}_l<i>.npz with keys x (N, cond), y (N, cells); levels ascending in
resolution; rows paired across levels (asserted). 1-D datasets have cells = L (grid (1, L)).
"""
from __future__ import annotations
import hashlib, json, math, os, random, time
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F

REGS = ["periodic_cell", "periodic_node", "generic", "interior_dirichlet"]
EPOCH_TAG = "ct"          # result files: <model>__<dataset>__e<EPOCH_TAG>__s<seed>.json


class Unpaired(Exception):
    pass


def sha256(path, n=1 << 22):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(n)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def seed_all(seed):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)


def fac_name(rel):
    return rel.split("/", 1)[1] if rel.startswith("core/") else rel.replace("/", "__")


def infer_grid(ncells):
    s = math.isqrt(ncells)
    return (s, s) if s * s == ncells else (1, ncells)


def resample_axis(y, axis, n_new, reg):
    """Linear interpolation along one axis under a grid-registration convention."""
    n = y.shape[axis]
    if n == n_new:
        return y
    dev, dt = y.device, y.dtype
    t = torch.arange(n_new, device=dev, dtype=torch.float64)
    src = y
    if reg == "interior_dirichlet":                       # nodes at (i+1)/(n+1); zero Dirichlet boundary
        s = (t + 1) / (n_new + 1) * (n + 1)               # index in zero-padded source (pad node 0 and n+1)
        pad = [0] * (2 * y.dim())
        k = y.dim() - 1 - axis
        pad[2 * k] = 1; pad[2 * k + 1] = 1
        src = F.pad(y, pad)
        i0 = s.floor().clamp(0, n).long(); i1 = (i0 + 1).clamp(max=n + 1); w = s - i0
    elif reg == "generic":                                # cell-centred, non-periodic, border-clamped
        s = ((t + 0.5) / n_new * n - 0.5).clamp(0, n - 1)
        i0 = s.floor().clamp(max=n - 1).long(); i1 = (i0 + 1).clamp(max=n - 1); w = s - i0
    elif reg in ("periodic_cell", "periodic_node"):
        off = 0.5 if reg == "periodic_cell" else 0.0
        s = ((t + off) / n_new * n - off) % n
        i0 = s.floor().long() % n; i1 = (i0 + 1) % n; w = s - s.floor()
    else:
        raise ValueError(reg)
    y0 = src.index_select(axis, i0); y1 = src.index_select(axis, i1)
    shape = [1] * y.dim(); shape[axis] = n_new
    w = w.to(dt).view(shape)
    return y0 * (1 - w) + y1 * w


def prolong(y, grid, reg):
    """y: (N, h, w) native -> (N, grid[0], grid[1])."""
    for axis, n_new in zip((1, 2), grid):
        y = resample_axis(y, axis, int(n_new), reg)
    return y


def rel_l2_per_sample(pred, y):
    axes = tuple(range(1, y.dim()))
    return ((pred - y).flatten(1).norm(dim=1) / y.flatten(1).norm(dim=1).clamp_min(1e-8))


def nrmse(pred, y):
    return float((pred - y).norm() / y.norm().clamp_min(1e-20))


def bootstrap_ci(v, n=1000, seed=0):
    rng = np.random.default_rng(seed); v = np.asarray(v, dtype=np.float64)
    m = np.array([rng.choice(v, len(v), replace=True).mean() for _ in range(n)])
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def choose_registration(y_src, y_dst_native, grid_dst):
    errs = {}
    for c in REGS:
        try:
            up = prolong(y_src, grid_dst, c)
            errs[c] = float(rel_l2_per_sample(up, y_dst_native).mean())
        except Exception:
            errs[c] = float("inf")
    best = min(errs, key=errs.get)
    return best, errs


def load_dataset(rel, root, seed, val_frac=0.1, device="cpu", min_val=4):
    root = Path(root); d = root / rel
    def lv(p):
        return int(p.stem.split("_l")[1])
    trains = sorted(d.glob("train_l*.npz"), key=lv); tests = sorted(d.glob("test_l*.npz"), key=lv)
    if len(trains) < 2:
        raise Unpaired(f"{rel}: fewer than two training levels found ({len(trains)})")
    if [lv(p) for p in trains] != [lv(p) for p in tests]:
        raise Unpaired(f"{rel}: test levels {[lv(p) for p in tests]} != train levels {[lv(p) for p in trains]}")
    hashes = {}
    def read(paths):
        xs, ys, grids = [], [], []
        for p in paths:
            with np.load(p) as z:
                x = z["x"].astype(np.float32); y = z["y"].astype(np.float32)
            if not (np.isfinite(x).all() and np.isfinite(y).all()):
                raise ValueError(f"nonfinite data in {p}")
            xs.append(x); ys.append(y); hashes[str(p)] = sha256(p)
        # dataset-level dimensionality: if ANY level's cell count is not a perfect square the dataset is 1-D (grid (1, L)).
        oned = any(infer_grid(y.shape[1])[0] == 1 for y in ys)
        grids = [(1, y.shape[1]) if oned else infer_grid(y.shape[1]) for y in ys]
        ys = [torch.from_numpy(y.reshape(-1, *g)) for y, g in zip(ys, grids)]
        for x in xs[1:]:
            if x.shape != xs[0].shape or not np.array_equal(x, xs[0]):
                raise Unpaired(f"{rel}: condition rows differ across levels -> not index-paired")
        return xs[0], ys, grids
    x_tr, y_tr, grids = read(trains); x_te, y_te, grids_te = read(tests)
    if grids != grids_te:
        raise Unpaired(f"{rel}: train grids {grids} != test grids {grids_te}")
    cells = [g[0] * g[1] for g in grids]
    if any(b <= a for a, b in zip(cells, cells[1:])):
        raise ValueError(f"{rel}: levels not ascending {grids}")
    L = len(grids); n = len(x_tr)
    perm = np.random.default_rng(seed).permutation(n)
    n_val = max(min_val, int(round(val_frac * n))); val = np.sort(perm[:n_val]); tr = np.sort(perm[n_val:])
    xmean = x_tr[tr].mean(0); xstd = np.maximum(x_tr[tr].std(0), 1e-6)
    scale = float(y_tr[-2][tr].square().mean().sqrt())
    if not scale > 1e-12:
        raise ValueError("degenerate LF scale")
    grid = grids[-1]
    reg, reg_errs = choose_registration(y_tr[-2][tr], y_tr[-1][tr], grid)
    to = lambda a: torch.as_tensor(a, dtype=torch.float32, device=device)
    data = dict(
        rel=rel, name=fac_name(rel), levels=L, grids=grids, grid=grid, hf=L - 1, top_lf=L - 2, registration=reg,
        registration_errors=reg_errs, scale=scale, train_rows=tr, val_rows=val, n_train=len(tr), n_val=len(val), n_test=len(x_te),
        cond_dim=int(x_tr.shape[1]), xmean=xmean, xstd=xstd,
        X=to((x_tr - xmean) / xstd), Xtest=to((x_te - xmean) / xstd),
        Y=[y.to(device) / scale for y in y_tr],            # native grids, scaled, ALL training rows (index with train_rows / val_rows)
        Ytest=[y.to(device) / scale for y in y_te],        # native grids, scaled; Ytest[-1] is the HF target
        Yup=[prolong(y.to(device) / scale, grid, reg) for y in y_tr[:-1]],       # LF levels prolonged to HF grid (train)
        Yup_test=[prolong(y.to(device) / scale, grid, reg) for y in y_te[:-1]],
        manifest=dict(rel=rel, dataset=fac_name(rel), levels=L, native_grids=[list(g) for g in grids], registration=reg,
                      registration_errors_top_lf_to_hf_train=reg_errs, n_train_rows=len(tr), n_val_rows=len(val), n_test=len(x_te),
                      val_frac=val_frac, seed=seed, cond_dim=int(x_tr.shape[1]), y_scale_top_lf_train=scale,
                      test_lf_used_at_inference=True, paired_exactly=True, sha256=hashes, files=[str(p) for p in trains + tests]),
    )
    return data


def ls_gain(start, target):
    return float((start * target).sum() / start.square().sum().clamp_min(1e-20))


def evaluate_and_write(out_path, model_name, data, pred_hf, extra, train_seconds, n_params, device_name, seed):
    """pred_hf: (N_test, H, W) scaled units on the HF grid. Metrics are scale-invariant."""
    y = data["Ytest"][-1]
    pred_hf = pred_hf.to(y.device)
    per = rel_l2_per_sample(pred_hf, y).detach().cpu().numpy().astype(np.float64)
    lo, hi = bootstrap_ci(per)
    res = dict(model=model_name, dataset=data["name"], track="correction", seed=seed,
               splits={"test_hf": dict(nRMSE=nrmse(pred_hf, y), rel_l2_mean=float(per.mean()), rel_l2_ci95_lo=lo, rel_l2_ci95_hi=hi,
                                       rel_l2_std=float(per.std()), rel_l2_per_sample=per.tolist(), n_samples=int(len(per)))},
               n_params=int(n_params), train_seconds=float(train_seconds), device=device_name, work_grid=list(data["grid"]),
               hf_level=data["hf"] + 1, levels=data["levels"], eval_protocol="full_field_on_native_hf_grid",
               inputs_at_inference=["theta", "real_lf_solves_of_test_instance"], manifest=data["manifest"])
    res.update(extra)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    tmp = str(out_path) + ".tmp"
    with open(tmp, "w") as f:
        json.dump(res, f)
    os.replace(tmp, out_path)
    return res


def write_excluded(out_path, model_name, rel, reason, seed):
    res = dict(model=model_name, dataset=fac_name(rel), track="correction", seed=seed, excluded=True, reason=reason,
               splits={"test_hf": {"error": reason, "nRMSE": float("nan"), "rel_l2_mean": None, "n_samples": 0}})
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(res, f)
    return res
