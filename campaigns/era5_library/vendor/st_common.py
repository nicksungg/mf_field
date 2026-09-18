"""Surrogate-track benchmark (theta -> fine field; coarse data for TRAINING only): shared loader, GP/POD helpers, result I/O.

Data dict (all fields in scaled units, scale = rms of the top-coarse training fields):
  X_hf (n_hf, d) normalised theta | Y_hf (n_hf, H, W) fine field on the evaluation grid | hf_tr, hf_va row indices
  X_lf (n_lf, d)                  | Y_lf (n_lf, h, w) top-coarse native            | Y_lf_up (n_lf, H, W) prolonged | lf_tr, lf_va
  levels: list of dicts {X, Y, grid} for EVERY level (ascending), for fidelity-blind pooling
  Xtest, Ytest (n_te, H, W); grid (H, W); grid_lf (h, w); registration; paired (bool); cond_dim; scale
Paired datasets (mf_field_final npz_l, same theta rows at every level) go through bench_ct's ct_common.load_dataset (same
split seed, same registration choice, same prolongation).  Unpaired datasets (leaderboard ifc_raw / npz_l with unequal
row counts) go through factory_mffp's load_mf_dataset on the 256-capped working grid with bilinear resampling.
"""
from __future__ import annotations
import json, math, os, sys, time
from pathlib import Path
import numpy as np
import torch
from scipy.optimize import minimize
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from ct_common import (Unpaired, bootstrap_ci, fac_name, infer_grid, load_dataset as ct_load, nrmse, prolong,   # noqa: E402
                       rel_l2_per_sample, seed_all, sha256)

EPOCH_TAG = "st"                       # result files: <arm>__<dataset>__est__s<seed>.json
MF = Path(os.environ.get("MF_ROOT", "/archive/mf_field"))
FACTORY_DATA = Path(os.environ.get("MFFP_DATA", str(MF / "factory_mffp" / "data")))
FAMILY = Path(os.environ.get("FILM_FAMILY", str(MF / "factory_mffp" / "models" / "mf_fno_transfer_film")))


def result_path(out_dir, arm, rel, seed):
    return Path(out_dir) / f"{arm}__{fac_name(rel)}__e{EPOCH_TAG}__s{seed}.json"


# ------------------------------------------------------------------------------------------------------- loading
def _split(n, seed, val_frac, min_val):
    perm = np.random.default_rng(seed).permutation(n)
    n_val = max(min_val, int(round(val_frac * n))) if val_frac > 0 else min_val
    return np.sort(perm[n_val:]), np.sort(perm[:n_val])


def load_paired(rel, root, seed, val_frac, device, min_val):
    d = ct_load(rel, root, seed, val_frac=val_frac, device=device, min_val=min_val)
    tr, va = d["train_rows"], d["val_rows"]
    levels = [dict(X=d["X"], Y=d["Y"][i], grid=tuple(d["grids"][i])) for i in range(d["levels"])]
    return dict(rel=rel, name=d["name"], paired=True, cond_dim=d["cond_dim"], scale=d["scale"], registration=d["registration"],
                grid=tuple(d["grid"]), grid_lf=tuple(d["grids"][-2]), n_levels=d["levels"],
                X_hf=d["X"], Y_hf=d["Y"][-1], hf_tr=tr, hf_va=va,
                X_lf=d["X"], Y_lf=d["Y"][-2], Y_lf_up=d["Yup"][-1], lf_tr=tr, lf_va=va, levels=levels,
                Xtest=d["Xtest"], Ytest=d["Ytest"][-1], Ytest_lf_up=d["Yup_test"][-1],
                manifest=dict(d["manifest"], test_lf_used_at_inference=False, track="surrogate"))


def load_unpaired(rel, seed, val_frac, device, min_val, cap=256):
    """Leaderboard-format dataset (factory_mffp/data/<name>): rows NOT aligned across levels; 256-capped working grid."""
    sys.path.insert(0, str(FAMILY)); sys.path.insert(0, str(FAMILY.parent.parent))
    from data_adapters import load_mf_dataset
    from data_adapters.geometry import resolve_grid
    name = fac_name(rel); ddir = FACTORY_DATA / name
    train = load_mf_dataset(ddir, "train"); test = load_mf_dataset(ddir, "test")
    hf = train["hf_fid"]
    if hf not in test["fids"]:
        hf = test["hf_fid"]
    lfs = sorted(f for f in train["lf_fids"] if f != hf)
    if not lfs:
        raise Unpaired(f"{rel}: no coarse level")
    lf = lfs[-1]
    def cap_grid(g):
        H, W = g; m = max(H, W)
        return (H, W) if m <= cap else (max(1, round(H * cap / m)), max(1, round(W * cap / m)))
    hf_nat = resolve_grid(name, int(train["n_cells_by_fid"][hf])); grid = cap_grid(hf_nat)
    lf_nat = resolve_grid(name, int(train["n_cells_by_fid"][lf]))
    to = lambda a: torch.as_tensor(np.asarray(a), dtype=torch.float32, device=device)
    def field(y, g_src, g_dst):
        t = to(y).reshape(-1, *g_src)
        return prolong(t, g_dst, "generic") if tuple(g_src) != tuple(g_dst) else t
    X_hf_raw = np.asarray(train["cond_by_fid"][hf], np.float32); X_lf_raw = np.asarray(train["cond_by_fid"][lf], np.float32)
    X_te_raw = np.asarray(test["cond_by_fid"][hf], np.float32)
    hf_tr, hf_va = _split(len(X_hf_raw), seed, val_frac, min_val); lf_tr, lf_va = _split(len(X_lf_raw), seed + 1, val_frac, min_val)
    xmean = X_hf_raw[hf_tr].mean(0); xstd = np.maximum(X_hf_raw[hf_tr].std(0), 1e-6)
    Y_lf_nat = to(train["field_by_fid"][lf]).reshape(-1, *lf_nat)
    scale = float(Y_lf_nat[lf_tr].square().mean().sqrt())
    levels = []
    for f in lfs + [hf]:
        g = resolve_grid(name, int(train["n_cells_by_fid"][f]))
        levels.append(dict(X=to((np.asarray(train["cond_by_fid"][f], np.float32) - xmean) / xstd), Y=field(train["field_by_fid"][f], g, g if f != hf else grid) / scale, grid=tuple(g if f != hf else grid)))
    Y_hf = field(train["field_by_fid"][hf], hf_nat, grid) / scale; Y_te = field(test["field_by_fid"][hf], hf_nat, grid) / scale
    return dict(rel=rel, name=name, paired=False, cond_dim=int(X_hf_raw.shape[1]), scale=scale, registration="generic",
                grid=tuple(grid), grid_lf=tuple(lf_nat), n_levels=len(lfs) + 1,
                X_hf=to((X_hf_raw - xmean) / xstd), Y_hf=Y_hf, hf_tr=hf_tr, hf_va=hf_va,
                X_lf=to((X_lf_raw - xmean) / xstd), Y_lf=Y_lf_nat / scale, Y_lf_up=prolong(Y_lf_nat / scale, grid, "generic"), lf_tr=lf_tr, lf_va=lf_va,
                levels=levels, Xtest=to((X_te_raw - xmean) / xstd), Ytest=Y_te, Ytest_lf_up=None,
                manifest=dict(rel=rel, dataset=name, loader=train.get("loader"), paired_exactly=False, hf_fid=int(hf), lf_fid=int(lf),
                              hf_grid_native=list(hf_nat), work_grid=list(grid), n_hf_train=int(len(hf_tr)), n_lf_train=int(len(lf_tr)),
                              n_test=int(len(X_te_raw)), seed=seed, cond_dim=int(X_hf_raw.shape[1]), test_lf_used_at_inference=False, track="surrogate"))


def load_any(rel, root, seed, val_frac=0.1, device="cpu", min_val=4):
    try:
        return load_paired(rel, root, seed, val_frac, device, min_val)
    except Unpaired as e:
        print(f"[data] {rel}: paired loader refused ({e}); using leaderboard loader", flush=True)
        return load_unpaired(rel, seed, val_frac, device, min_val)


# ------------------------------------------------------------------------------------------------------- POD + GP
def pod_fit(Y, energy=0.999, max_modes=64):
    """Y (n, cells) float64 -> mean (cells,), basis (r, cells), coefficients (n, r), captured energy."""
    mean = Y.mean(0); Yc = Y - mean
    U, S, Vt = np.linalg.svd(Yc, full_matrices=False)
    en = np.cumsum(S ** 2) / max(float((S ** 2).sum()), 1e-30)
    r = int(min(max_modes, len(S), max(1, int(np.searchsorted(en, energy) + 1))))
    return mean, Vt[:r], Yc @ Vt[:r].T, float(en[r - 1])


def ard_rbf(X1, X2, log_ell, log_sf):
    d = (X1[:, None, :] - X2[None, :, :]) / np.exp(log_ell)[None, None, :]
    return np.exp(2 * log_sf) * np.exp(-0.5 * (d ** 2).sum(-1))


def _nlml_generic(params, X, C, kern):
    n, r = C.shape
    K = kern(params, X, X) + (np.exp(2 * params[-1]) + 1e-8) * np.eye(n)
    try:
        L = np.linalg.cholesky(K)
    except np.linalg.LinAlgError:
        return 1e25
    a = np.linalg.solve(L, C)
    return float(0.5 * (a ** 2).sum() + r * np.log(np.diag(L)).sum() + 0.5 * n * r * math.log(2 * math.pi))


def fit_gp(X, C, kern, x0s, bounds, maxiter=200):
    """Shared-hyperparameter GP over r standardised outputs C (n, r); params[-1] = log noise. Returns best scipy result."""
    best = None
    for x0 in x0s:
        res = minimize(_nlml_generic, x0, args=(X, C, kern), method="L-BFGS-B", bounds=bounds, options=dict(maxiter=maxiter))
        if best is None or res.fun < best.fun:
            best = res
    return best


class SharedGP:
    """ARD-RBF GP with hyperparameters shared across POD coefficients (Kennedy-O'Hagan arm convention of bench_ct)."""
    def __init__(self, X, C, seed, restarts=2):
        self.X = X; self.cm, self.cs = C.mean(0), np.maximum(C.std(0), 1e-12); self.Cs = (C - self.cm) / self.cs
        d = X.shape[1]; rng = np.random.default_rng(seed)
        x0s = [np.concatenate((np.zeros(d), [0.0], [math.log(0.1)]))]
        for _ in range(restarts - 1):
            x0s.append(np.concatenate((rng.uniform(-0.5, 1.0, d), [rng.normal(0, 0.3)], [math.log(0.3)])))
        bounds = [(-3.0, 4.0)] * d + [(-4.0, 3.0), (-7.0, 1.0)]
        self.kern = lambda p, A, B: ard_rbf(A, B, p[:d], p[d])
        self.fit = fit_gp(X, self.Cs, self.kern, x0s, bounds); p = self.fit.x
        K = self.kern(p, X, X) + (np.exp(2 * p[-1]) + 1e-8) * np.eye(len(X))
        self.L = np.linalg.cholesky(K); self.A = np.linalg.solve(self.L.T, np.linalg.solve(self.L, self.Cs)); self.p = p

    def predict(self, Xs, return_var=False):
        Ks = self.kern(self.p, Xs, self.X); mean = Ks @ self.A * self.cs + self.cm
        if not return_var:
            return mean
        v = np.linalg.solve(self.L, Ks.T)
        var = np.maximum(np.exp(2 * self.p[-2]) - (v ** 2).sum(0), 1e-12)          # (n*,) shared predictive variance (standardised units)
        return mean, var[:, None] * self.cs[None, :] ** 2

    def info(self):
        d = self.X.shape[1]
        return dict(gp_log_lengthscales=self.p[:d].tolist(), gp_log_signal=float(self.p[d]), gp_log_noise=float(self.p[-1]),
                    gp_nlml=float(self.fit.fun), gp_converged=bool(self.fit.success))


class PODGP:
    """theta -> field emulator: POD of training fields + SharedGP on the coefficients."""
    def __init__(self, X, Y, seed, energy=0.999, max_modes=64, restarts=2):
        self.mean, self.basis, C, self.energy = pod_fit(Y, energy, max_modes)
        self.gp = SharedGP(X, C, seed, restarts); self.r = self.basis.shape[0]

    def coefficients(self, Y):
        return (Y - self.mean) @ self.basis.T

    def predict(self, Xs):
        return self.gp.predict(Xs) @ self.basis + self.mean

    def info(self, prefix=""):
        return {prefix + "pod_modes": int(self.r), prefix + "pod_energy_captured": self.energy, **{prefix + k: v for k, v in self.gp.info().items()}}


# ------------------------------------------------------------------------------------------------------- results
def evaluate_and_write(out_path, arm, data, pred_hf, extra, train_seconds, n_params, device_name, seed):
    y = data["Ytest"]; pred_hf = torch.as_tensor(pred_hf, dtype=torch.float32, device=y.device).reshape(y.shape)
    per = rel_l2_per_sample(pred_hf, y).detach().cpu().numpy().astype(np.float64); lo, hi = bootstrap_ci(per)
    res = dict(model=arm, dataset=data["name"], track="surrogate", seed=seed,
               splits={"test_hf": dict(nRMSE=nrmse(pred_hf, y), rel_l2_mean=float(per.mean()), rel_l2_ci95_lo=lo, rel_l2_ci95_hi=hi,
                                       rel_l2_std=float(per.std()), rel_l2_per_sample=per.tolist(), n_samples=int(len(per)))},
               n_params=int(n_params), train_seconds=float(train_seconds), device=device_name, work_grid=list(data["grid"]),
               paired=bool(data["paired"]), n_levels=int(data["n_levels"]), eval_protocol="full_field_on_hf_grid",
               inputs_at_inference=["theta"], manifest=data["manifest"])
    res.update(extra)
    # optional predicted-field dump (release/predictions); inert unless SAVE_PRED_DIR is set
    pd_dir = os.environ.get("SAVE_PRED_DIR")
    if pd_dir:
        try:
            Path(pd_dir).mkdir(parents=True, exist_ok=True)
            np.savez_compressed(Path(pd_dir) / f"{arm}__{data['name']}__s{int(seed)}.npz",
                                pred=pred_hf.detach().cpu().numpy().reshape(len(per), -1).astype(np.float16),
                                target=y.detach().cpu().numpy().reshape(len(per), -1).astype(np.float16),
                                rel_l2_per_sample=per.astype(np.float32), work_grid=np.asarray(data["grid"], dtype=np.int32),
                                model=np.str_(arm), dataset=np.str_(data["name"]), seed=np.int32(seed))
        except Exception as e:
            print(f"[warn] SAVE_PRED_DIR dump failed: {e}", flush=True)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True); tmp = str(out_path) + ".tmp"
    with open(tmp, "w") as f:
        json.dump(res, f)
    os.replace(tmp, out_path)
    return res


def write_excluded(out_path, arm, rel, reason, seed):
    res = dict(model=arm, dataset=fac_name(rel), track="surrogate", seed=seed, excluded=True, reason=reason,
               splits={"test_hf": {"error": reason, "nRMSE": float("nan"), "rel_l2_mean": None, "n_samples": 0}})
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(res, f)
    return res


def coordinates(grid, reg, device):
    axes = []
    for n in grid:
        if reg == "interior_dirichlet":
            x = (torch.arange(n, device=device) + 1) / (n + 1)
        else:
            off = 0.5 if reg == "periodic_cell" else 0.0
            x = (torch.arange(n, device=device) + off) / n
        axes.append(x * 2 - 1)
    gy, gx = torch.meshgrid(*axes, indexing="ij")
    return torch.stack((gy, gx), -1).reshape(-1, 2).float()          # (cells, 2)
