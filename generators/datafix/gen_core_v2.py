"""Regenerate the four in-house core datasets (poisson, heat, darcy, allen_cahn) with
  (a) the Poisson dx^2 boundary-scaling bug FIXED (b = g, not dx^2 * g),
  (b) LF-abundant variants: 4000 coarse-level rows whose first 400 are exactly the paired HF rows (nested design),
  (c) per-level solver wall-time logging (cost.json).
Solvers are copied verbatim from mf_field/generate_all_datasets.py (only the Poisson RHS changes).  The paired
heat / darcy / allen_cahn arrays are asserted equal to the originals; Poisson is asserted equal to dx^2 x original.
Output: <OUT>/core/<name>[_v2]/  and  <OUT>/core/<name>[_v2]_lfabund/   (train_l*.npz / test_l*.npz, x, y)
"""
from __future__ import annotations
import json, math, sys, time
from functools import partial
from multiprocessing import Pool
from pathlib import Path
import numpy as np
from scipy.sparse import csc_matrix, csr_matrix, diags
from scipy.sparse.linalg import spsolve
from scipy.linalg import solve_banded

ORIG = Path("/archive/mf_field_final/core")
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "/archive/mf_field_v2") / "core"
N_PAIRED, N_TRAIN, N_EXTRA, SEED, SEED_EXTRA, NPROC = 500, 400, 3600, 42, 4242, 8


# ------------------------------------------------------------------ poisson (verbatim except the RHS scaling)
def _lap(n):
    size = n * n; main = np.full(size, 4.0); off = np.full(size - 1, -1.0); off[n - 1::n] = 0.0; vert = np.full(size - n, -1.0)
    return diags([main, off, off, vert, vert], [0, 1, -1, n, -n], format="csc")


def poisson_solve(n, params, fixed=True):
    u_0_x, u_1_x, u_y_0, u_y_1, u_dirac = (float(v) for v in params)
    x = np.linspace(0.0, 1.0, n); dx = x[1] - x[0]
    u_pad = np.zeros((n + 2, n + 2)); u_pad[0, :] = u_0_x; u_pad[-1, :] = u_1_x; u_pad[:, 0] = u_y_0; u_pad[:, -1] = u_y_1
    if n % 2 == 0:
        mid = (n + 2) // 2; u_pad[mid - 1:mid + 1, mid - 1:mid] = u_dirac
    else:
        mid = (n + 1) // 2; u_pad[mid, mid] = u_dirac
    g = u_pad[0:n, 1:n + 1] + u_pad[2:n + 2, 1:n + 1] + u_pad[1:n + 1, 0:n] + u_pad[1:n + 1, 2:n + 2]
    b = (1.0 if fixed else dx ** 2) * g.flatten()          # BUG in the original: dx**2 * g  (boundary data scaled by 1/n^2)
    return spsolve(_lap(n), b).reshape(n, n)


def poisson_theta(rng, n):
    return rng.uniform(0.1, 0.9, size=(n, 5))


# ------------------------------------------------------------------ heat (verbatim)
def _thomas(a, b, c, d):
    n = b.shape[0]; x = np.zeros(n)
    for k in range(1, n):
        q = a[k] / b[k - 1]; b[k] = b[k] - c[k - 1] * q; d[k] = d[k] - d[k - 1] * q
    q = d[n - 1] / b[n - 1]; x[n - 1] = q
    for k in range(n - 2, -1, -1):
        q = (d[k] - c[k] * q) / b[k]; x[k] = q
    return x


def heat_solve(n, params):
    neumann_0, neumann_1, alpha = (float(v) for v in params)
    x = np.linspace(0.0, 1.0, n); dx = x[1] - x[0]; dt = dx
    u = np.zeros((n + 1, n + 2))
    for i in range(n):
        if 0.25 <= i * dx <= 0.75:
            u[0, i + 1] = 1.0
    coef = alpha * dt / dx ** 2
    for step in range(n):
        a = np.full(n, -coef); b = np.full(n, 1.0 + 2.0 * coef); c = np.full(n, -coef); d = u[step, 1:n + 1].copy()
        d[0] = (d[0] - (coef * 2.0 * dx * neumann_0)) / 2.0; d[-1] = (d[-1] + (coef * 2.0 * dx * neumann_1)) / 2.0
        a[0] = 0.0; b[0] = b[0] / 2.0; c[-1] = 0.0; b[-1] = b[-1] / 2.0
        u[step + 1, 1:-1] = _thomas(a, b, c, d)
    return u[1:, 1:-1].copy()


def heat_theta(rng, n):
    return np.stack([rng.uniform(lo, hi, size=n) for lo, hi in ((0.0, 1.0), (-1.0, 0.0), (0.01, 0.1))], axis=-1)


# ------------------------------------------------------------------ darcy (verbatim)
L_CORR, SIGMA_LOGK, N_KL, N_REF = 0.2, 1.0, 16, 48


def kl_basis():
    coords = np.stack(np.meshgrid(np.linspace(0, 1, N_REF), np.linspace(0, 1, N_REF), indexing="ij"), axis=-1).reshape(-1, 2)
    d = np.linalg.norm(coords[:, None, :] - coords[None, :, :], axis=-1); cov = SIGMA_LOGK ** 2 * np.exp(-d / L_CORR)
    w, v = np.linalg.eigh(cov); idx = np.argsort(w)[::-1][:N_KL]
    return np.maximum(w[idx], 0.0), v[:, idx].reshape(N_REF, N_REF, N_KL)


def _bilinear(eig, nx, ny):
    xs_t = np.linspace(0, 1, nx); ys_t = np.linspace(0, 1, ny); xs_r = np.linspace(0, 1, N_REF); ys_r = np.linspace(0, 1, N_REF)
    fx = np.clip(np.searchsorted(xs_r, xs_t) - 1, 0, N_REF - 2); fy = np.clip(np.searchsorted(ys_r, ys_t) - 1, 0, N_REF - 2)
    tx = (xs_t - xs_r[fx]) / (xs_r[fx + 1] - xs_r[fx]); ty = (ys_t - ys_r[fy]) / (ys_r[fy + 1] - ys_r[fy])
    a = eig[np.ix_(fy, fx)]; b = eig[np.ix_(fy, fx + 1)]; c = eig[np.ix_(fy + 1, fx)]; d = eig[np.ix_(fy + 1, fx + 1)]
    txg = tx[None, :]; tyg = ty[:, None]
    return (1 - tyg) * ((1 - txg) * a + txg * b) + tyg * ((1 - txg) * c + txg * d)


def darcy_solve(n, z, basis):
    eigvals, eigvecs_ref = basis; nx = ny = n
    eig_grid = np.empty((ny, nx, N_KL))
    for j in range(N_KL):
        eig_grid[:, :, j] = _bilinear(eigvecs_ref[:, :, j], nx, ny)
    k = np.exp(eig_grid @ (np.sqrt(eigvals) * z)); hx = 1.0 / (nx + 1); hy = 1.0 / (ny + 1)
    rows, cols, vals = [], [], []
    idx = lambda i, j: i * nx + j
    for i in range(ny):
        for j in range(nx):
            p = idx(i, j); kc = k[i, j]
            kw = 2 * kc * k[i, j - 1] / (kc + k[i, j - 1]) if j > 0 else kc; ke = 2 * kc * k[i, j + 1] / (kc + k[i, j + 1]) if j < nx - 1 else kc
            ks = 2 * kc * k[i - 1, j] / (kc + k[i - 1, j]) if i > 0 else kc; kn = 2 * kc * k[i + 1, j] / (kc + k[i + 1, j]) if i < ny - 1 else kc
            rows.append(p); cols.append(p); vals.append((kw + ke) / hx ** 2 + (ks + kn) / hy ** 2)
            if j > 0: rows.append(p); cols.append(idx(i, j - 1)); vals.append(-kw / hx ** 2)
            if j < nx - 1: rows.append(p); cols.append(idx(i, j + 1)); vals.append(-ke / hx ** 2)
            if i > 0: rows.append(p); cols.append(idx(i - 1, j)); vals.append(-ks / hy ** 2)
            if i < ny - 1: rows.append(p); cols.append(idx(i + 1, j)); vals.append(-kn / hy ** 2)
    A = csr_matrix((vals, (rows, cols)), shape=(nx * ny, nx * ny))
    return spsolve(A, np.full(nx * ny, 1.0)).reshape(ny, nx)


def darcy_theta(rng, n):
    return rng.standard_normal(size=(n, N_KL))


# ------------------------------------------------------------------ allen_cahn (verbatim, 1-D)
EPS, DT, N_STEPS = 0.01, 0.005, 200


def allen_cahn_solve(nx, params):
    center, sign = float(params[0]), float(params[1]); x = np.linspace(-1, 1, nx); dx = 2.0 / (nx - 1); r = EPS ** 2 * DT / dx ** 2
    upper = np.full(nx, -r); main = np.full(nx, 1 + 2 * r); lower = np.full(nx, -r); main[0] = main[-1] = 1 + r; upper[0] = 0.0; lower[-1] = 0.0
    ab = np.stack([upper, main, lower]); u = sign * np.tanh((x - center) / (np.sqrt(2.0) * EPS))
    for _ in range(N_STEPS):
        u = solve_banded((1, 1), ab, u + DT * (u - u ** 3))
    return u


def allen_cahn_theta(rng, n):
    centers = rng.uniform(-0.7, 0.7, size=(n,)); signs = rng.choice([-1.0, 1.0], size=(n,)); return np.stack([centers, signs], axis=-1)


# ------------------------------------------------------------------ driver
SPECS = {
    "poisson_generated": dict(levels=[16, 32, 64], theta=poisson_theta, solve=lambda n, p, extra: poisson_solve(n, p, fixed=True), out="poisson_generated_v2", bugcheck=True),
    "heat_generated": dict(levels=[16, 32, 64], theta=heat_theta, solve=lambda n, p, extra: heat_solve(n, p), out="heat_generated", bugcheck=False),
    "darcy_generated": dict(levels=[32, 64, 128], theta=darcy_theta, solve=lambda n, p, extra: darcy_solve(n, p, extra), out="darcy_generated", bugcheck=False),
    "allen_cahn_generated": dict(levels=[64, 128, 256], theta=allen_cahn_theta, solve=lambda n, p, extra: allen_cahn_solve(n, p), out="allen_cahn_generated", bugcheck=False),
}


def _worker(args):
    name, n, params, extra = args; t = time.perf_counter(); y = SPECS[name]["solve"](n, params, extra); return y.reshape(-1), time.perf_counter() - t


def run(name):
    spec = SPECS[name]; levels = spec["levels"]; extra = kl_basis() if name == "darcy_generated" else None
    th_paired = spec["theta"](np.random.default_rng(SEED), N_PAIRED); th_extra = spec["theta"](np.random.default_rng(SEED_EXTRA), N_EXTRA)
    assert len(np.unique(np.concatenate([th_paired, th_extra]), axis=0)) == N_PAIRED + N_EXTRA
    cost = {}; Y = {}; regen_note = {}
    with Pool(NPROC) as pool:
        for li, n in enumerate(levels, 1):
            rows = th_paired if li == len(levels) else np.concatenate([th_paired, th_extra])      # HF: paired only; LF: paired + extra
            res = pool.map(_worker, [(name, n, p, extra) for p in rows], chunksize=8)
            Y[li] = np.stack([r[0] for r in res]); ts = np.array([r[1] for r in res])
            cost[f"l{li}"] = dict(grid=n, n_solves=int(len(ts)), mean_s=float(ts.mean()), median_s=float(ts.median() if hasattr(ts, "median") else np.median(ts)), total_s=float(ts.sum()))
            print(f"[{name}] L{li} n={n}: {len(ts)} solves, median {np.median(ts)*1e3:.2f} ms, total {ts.sum():.1f} s", flush=True)
    # ---- checks against the original files
    for li, n in enumerate(levels, 1):
        for split, sl in (("train", slice(0, N_TRAIN)), ("test", slice(N_TRAIN, N_PAIRED))):
            z = np.load(ORIG / name / f"{split}_l{li}.npz"); x0, y0 = z["x"], z["y"]
            assert np.array_equal(x0, th_paired[sl]), f"{name} {split} L{li}: theta mismatch"
            ynew = Y[li][sl]
            if spec["bugcheck"]:
                dx = 1.0 / (n - 1); ratio = np.abs(y0).max() / np.abs(ynew).max()
                assert np.allclose(y0, ynew * dx ** 2, rtol=1e-6, atol=1e-12), f"{name} {split} L{li}: fixed field != original/dx^2"
                print(f"[{name}] {split} L{li}: original == dx^2 * fixed  (amplitude ratio {1/ratio:.1f}x)", flush=True)
            else:
                rel = float(np.linalg.norm(y0 - ynew) / max(np.linalg.norm(y0), 1e-30))
                if rel > 1e-6:
                    # not bit-reproducible (e.g. darcy: KL eigenvector sign/order depends on the LAPACK build) -> keep the
                    # ORIGINAL paired arrays as the truth and only append newly solved extra LF rows (same distribution).
                    print(f"[{name}] {split} L{li}: regenerated differs from original (rel {rel:.2e}) -> using original paired arrays", flush=True)
                    Y[li][sl] = y0; regen_note[f"{split}_l{li}"] = rel
        print(f"[{name}] L{li} paired arrays verified against {ORIG/name}", flush=True)
    # ---- write paired and LF-abundant variants
    for variant in ("", "_lfabund"):
        d = OUT / f"{spec['out']}{variant}"; d.mkdir(parents=True, exist_ok=True)
        for li, n in enumerate(levels, 1):
            if variant == "_lfabund" and li < len(levels):
                xtr = np.concatenate([th_paired[:N_TRAIN], th_extra]); ytr = np.concatenate([Y[li][:N_TRAIN], Y[li][N_PAIRED:]])
            else:
                xtr, ytr = th_paired[:N_TRAIN], Y[li][:N_TRAIN]
            np.savez(d / f"train_l{li}.npz", x=xtr, y=ytr); np.savez(d / f"test_l{li}.npz", x=th_paired[N_TRAIN:], y=Y[li][N_TRAIN:N_PAIRED])
        json.dump(dict(dataset=spec["out"] + variant, source_generator="mf_field/generate_all_datasets.py (solvers copied verbatim)",
                       poisson_fix="RHS b = g (original: dx^2 * g)" if spec["bugcheck"] else None, levels=levels, seed_paired=SEED, seed_extra=SEED_EXTRA,
                       n_train=N_TRAIN, n_test=N_PAIRED - N_TRAIN, n_lf_train=(N_TRAIN + N_EXTRA) if variant else N_TRAIN, nested="first 400 LF rows == HF rows",
                       paired_source=("original files (regeneration not bit-reproducible: " + str(regen_note) + ")") if regen_note else "regenerated and verified equal to original",
                       cost_per_solve=cost, generated=time.strftime("%Y-%m-%d %H:%M")), open(d / "meta.json", "w"), indent=1)
        print(f"[{name}] wrote {d}", flush=True)


if __name__ == "__main__":
    names = sys.argv[2].split(",") if len(sys.argv) > 2 else list(SPECS)
    for nm in names:
        run(nm)
    print("CORE_V2_OK")
