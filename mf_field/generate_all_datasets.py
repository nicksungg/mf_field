#!/usr/bin/env python3
"""Self-contained generator for all 8 MFFP-Bench regenerable PDE datasets.

Portable single file: needs only ``numpy`` and ``scipy`` (no mffpbench install).

    python generate_all_datasets.py [OUT_DIR] [N_SAMPLES] [DATASET_NAME]

Defaults: OUT_DIR=./mffpbench_generated, N_SAMPLES=500 (-> 400 train / 100 test
per dataset, an 80/20 split by index). Writes MFRNP-convention npz files::

    OUT_DIR/<dataset>/train_lN.npz   (keys: x, y)
    OUT_DIR/<dataset>/test_lN.npz

The 8 solver bodies below are the verbatim mffpbench.generators sources, each
wrapped in a factory so their module-level names stay isolated.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np


class _NoopLog:
    def debug(self, *args, **kwargs):
        pass

    def info(self, *args, **kwargs):
        pass


log = _NoopLog()


def _make_poisson():
    import numpy as np
    from scipy.sparse import csc_matrix, diags
    from scipy.sparse.linalg import spsolve

    INPUT_DIM = 5
    BOUNDS = (0.1, 0.9)

    def _build_laplacian(n: int) -> csc_matrix:
        log.debug("poisson.build_laplacian", n=n)
        size = n * n
        main = np.full(size, 4.0)
        off = np.full(size - 1, -1.0)
        off[n - 1 :: n] = 0.0
        vertical = np.full(size - n, -1.0)
        return diags(
            [main, off, off, vertical, vertical],
            [0, 1, -1, n, -n],
            format="csc",
        )

    def _solve_one(n: int, params: np.ndarray) -> np.ndarray:
        log.debug("poisson.solve_one", n=n)
        u_0_x, u_1_x, u_y_0, u_y_1, u_dirac = (float(v) for v in params)
        x = np.linspace(0.0, 1.0, n)
        dx = x[1] - x[0]

        u_pad = np.zeros((n + 2, n + 2), dtype=np.float64)
        u_pad[0, :] = u_0_x
        u_pad[-1, :] = u_1_x
        u_pad[:, 0] = u_y_0
        u_pad[:, -1] = u_y_1
        if n % 2 == 0:
            mid = (n + 2) // 2
            u_pad[mid - 1 : mid + 1, mid - 1 : mid] = u_dirac
        else:
            mid = (n + 1) // 2
            u_pad[mid, mid] = u_dirac

        g = (
            u_pad[0:n, 1 : n + 1]
            + u_pad[2 : n + 2, 1 : n + 1]
            + u_pad[1 : n + 1, 0:n]
            + u_pad[1 : n + 1, 2 : n + 2]
        )
        b = dx**2 * g.flatten()
        a = _build_laplacian(n)
        solution = spsolve(a, b)
        return np.asarray(solution, dtype=np.float64).reshape(n, n)

    def generate(fidelity_levels, n_samples, seed):
        log.info("poisson.generate")
        if n_samples <= 0:
            raise ValueError(f"n_samples must be positive, got {n_samples}.")
        if not fidelity_levels:
            raise ValueError("fidelity_levels must not be empty.")
        rng = np.random.default_rng(seed)
        lo, hi = BOUNDS
        x_shared = rng.uniform(lo, hi, size=(n_samples, INPUT_DIM)).astype(np.float64)
        out = {}
        for level in fidelity_levels:
            if level < 2:
                raise ValueError(f"fidelity level must be >= 2, got {level}.")
            y = np.empty((n_samples, level * level), dtype=np.float64)
            for i in range(n_samples):
                y[i] = _solve_one(level, x_shared[i]).reshape(-1)
            out[int(level)] = {"X": x_shared.copy(), "Y": y}
        return out

    return generate


def _make_heat():
    import numpy as np

    INPUT_DIM = 3
    BOUNDS = ((0.0, 1.0), (-1.0, 0.0), (0.01, 0.1))

    def _thomas(a, b, c, d):
        log.debug("heat.thomas")
        n = b.shape[0]
        x = np.zeros(n, dtype=np.float64)
        for k in range(1, n):
            q = a[k] / b[k - 1]
            b[k] = b[k] - c[k - 1] * q
            d[k] = d[k] - d[k - 1] * q
        q = d[n - 1] / b[n - 1]
        x[n - 1] = q
        for k in range(n - 2, -1, -1):
            q = (d[k] - c[k] * q) / b[k]
            x[k] = q
        return x

    def _solve_one(n, params):
        log.debug("heat.solve_one", n=n)
        neumann_0, neumann_1, alpha = (float(v) for v in params)
        x = np.linspace(0.0, 1.0, n)
        dx = x[1] - x[0]
        dt = dx
        u = np.zeros((n + 1, n + 2), dtype=np.float64)
        for i in range(n):
            if 0.25 <= i * dx <= 0.75:
                u[0, i + 1] = 1.0
        coef = alpha * dt / dx**2
        for step in range(n):
            a = np.full(n, -coef, dtype=np.float64)
            b = np.full(n, 1.0 + 2.0 * coef, dtype=np.float64)
            c = np.full(n, -coef, dtype=np.float64)
            d = u[step, 1 : n + 1].astype(np.float64, copy=True)
            d[0] = (d[0] - (coef * 2.0 * dx * neumann_0)) / 2.0
            d[-1] = (d[-1] + (coef * 2.0 * dx * neumann_1)) / 2.0
            a[0] = 0.0
            b[0] = b[0] / 2.0
            c[-1] = 0.0
            b[-1] = b[-1] / 2.0
            u[step + 1, 1:-1] = _thomas(a, b, c, d)
        return u[1:, 1:-1].astype(np.float64, copy=True)

    def generate(fidelity_levels, n_samples, seed):
        log.info("heat.generate")
        if n_samples <= 0:
            raise ValueError(f"n_samples must be positive, got {n_samples}.")
        if not fidelity_levels:
            raise ValueError("fidelity_levels must not be empty.")
        rng = np.random.default_rng(seed)
        cols = [rng.uniform(lo, hi, size=n_samples) for lo, hi in BOUNDS]
        x_shared = np.stack(cols, axis=-1).astype(np.float64)
        out = {}
        for level in fidelity_levels:
            if level < 2:
                raise ValueError(f"fidelity level must be >= 2, got {level}.")
            y = np.empty((n_samples, level * level), dtype=np.float64)
            for i in range(n_samples):
                y[i] = _solve_one(level, x_shared[i]).reshape(-1)
            out[int(level)] = {"X": x_shared.copy(), "Y": y}
        return out

    return generate


def _make_burgers():
    import math
    import numpy as np

    NU = 0.01
    T_FINAL = 1.0
    U_MAX = 1.0
    N_MODES = 4
    INPUT_DIM = 2 * N_MODES

    def _build_ic(nx, params):
        amps = params[:N_MODES]
        phases = params[N_MODES:]
        x = np.arange(nx, dtype=np.float64) / nx
        u0 = np.zeros(nx, dtype=np.float64)
        for k in range(1, N_MODES + 1):
            u0 += (amps[k - 1] / k) * np.sin(2.0 * np.pi * k * x + phases[k - 1])
        peak = float(np.max(np.abs(u0)))
        if peak > 0.0:
            u0 /= peak
        return u0

    def _cfl_dt(nx):
        dx = 1.0 / nx
        dt_cfl = 0.4 * min(dx / U_MAX, 0.5 * dx * dx / NU)
        n_steps = max(1, int(math.ceil(T_FINAL / dt_cfl)))
        return T_FINAL / n_steps, n_steps

    def _rhs(u, k):
        u_hat = np.fft.fft(u)
        ux = np.fft.ifft(1j * k * u_hat).real
        uxx = np.fft.ifft(-(k * k) * u_hat).real
        return -u * ux + NU * uxx

    def _solve_one(nx, params):
        k = 2.0 * np.pi * np.fft.fftfreq(nx, d=1.0 / nx)
        dt, n_steps = _cfl_dt(nx)
        u = _build_ic(nx, params)
        for _ in range(n_steps):
            k1 = _rhs(u, k)
            k2 = _rhs(u + 0.5 * dt * k1, k)
            k3 = _rhs(u + 0.5 * dt * k2, k)
            k4 = _rhs(u + dt * k3, k)
            u = u + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
        return u

    def generate(fidelity_levels, n_samples, seed):
        log.info("burgers.generate")
        if n_samples <= 0:
            raise ValueError(f"n_samples must be positive, got {n_samples}.")
        if not fidelity_levels:
            raise ValueError("fidelity_levels must not be empty.")
        rng = np.random.default_rng(seed)
        amps = rng.uniform(-1.0, 1.0, size=(n_samples, N_MODES))
        phases = rng.uniform(0.0, 2.0 * np.pi, size=(n_samples, N_MODES))
        x_shared = np.concatenate([amps, phases], axis=1).astype(np.float64)
        out = {}
        for level in fidelity_levels:
            if level < 4:
                raise ValueError(f"fidelity level must be >= 4, got {level}.")
            y = np.empty((n_samples, level), dtype=np.float64)
            for i in range(n_samples):
                y[i] = _solve_one(level, x_shared[i])
            out[int(level)] = {"X": x_shared.copy(), "Y": y}
        return out

    return generate


def _make_advection_diffusion():
    import math
    import numpy as np

    A_VEL = (1.0, 0.5)
    D_DIFF = 0.01
    T_FINAL = 0.5
    SIGMA = 0.10
    INPUT_DIM = 2

    def _build_ic(nx, ny, params):
        cx, cy = float(params[0]), float(params[1])
        xs = np.arange(nx, dtype=np.float64) / nx
        ys = np.arange(ny, dtype=np.float64) / ny
        grid_x, grid_y = np.meshgrid(xs, ys, indexing="xy")
        return np.exp(-((grid_x - cx) ** 2 + (grid_y - cy) ** 2) / (2.0 * SIGMA * SIGMA))

    def _cfl_dt(nx, ny):
        dx = 1.0 / nx
        dy = 1.0 / ny
        ax, ay = A_VEL
        dt_adv = min(dx / max(abs(ax), 1e-12), dy / max(abs(ay), 1e-12))
        dt_diff = 0.5 / (D_DIFF * (1.0 / (dx * dx) + 1.0 / (dy * dy)))
        dt_cfl = 0.4 * min(dt_adv, dt_diff)
        n_steps = max(1, int(math.ceil(T_FINAL / dt_cfl)))
        return T_FINAL / n_steps, n_steps

    def _rhs(u, kx, ky):
        u_hat = np.fft.fft2(u)
        ux = np.fft.ifft2(1j * kx * u_hat).real
        uy = np.fft.ifft2(1j * ky * u_hat).real
        lap = np.fft.ifft2(-(kx * kx + ky * ky) * u_hat).real
        ax, ay = A_VEL
        return -(ax * ux + ay * uy) + D_DIFF * lap

    def _solve_one(nx, ny, params):
        kx_1d = 2.0 * np.pi * np.fft.fftfreq(nx, d=1.0 / nx)
        ky_1d = 2.0 * np.pi * np.fft.fftfreq(ny, d=1.0 / ny)
        kx, ky = np.meshgrid(kx_1d, ky_1d, indexing="xy")
        dt, n_steps = _cfl_dt(nx, ny)
        u = _build_ic(nx, ny, params)
        for _ in range(n_steps):
            k1 = _rhs(u, kx, ky)
            k2 = _rhs(u + 0.5 * dt * k1, kx, ky)
            k3 = _rhs(u + 0.5 * dt * k2, kx, ky)
            k4 = _rhs(u + dt * k3, kx, ky)
            u = u + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
        return u

    def generate(fidelity_levels, n_samples, seed):
        log.info("adv_diff.generate")
        if n_samples <= 0:
            raise ValueError(f"n_samples must be positive, got {n_samples}.")
        if not fidelity_levels:
            raise ValueError("fidelity_levels must not be empty.")
        rng = np.random.default_rng(seed)
        centres = rng.uniform(0.3, 0.7, size=(n_samples, 2)).astype(np.float64)
        out = {}
        for level in fidelity_levels:
            if level < 4:
                raise ValueError(f"fidelity level must be >= 4, got {level}.")
            y = np.empty((n_samples, level * level), dtype=np.float64)
            for i in range(n_samples):
                y[i] = _solve_one(level, level, centres[i]).reshape(-1)
            out[int(level)] = {"X": centres.copy(), "Y": y}
        return out

    return generate


def _make_allen_cahn():
    import numpy as np
    from scipy.linalg import solve_banded

    EPS = 0.01
    T_FINAL = 1.0
    DT = 0.005
    N_STEPS = 200
    INPUT_DIM = 2

    def _build_ic(nx, params):
        center = float(params[0])
        sign = float(params[1])
        x = np.linspace(-1.0, 1.0, nx)
        return sign * np.tanh((x - center) / (np.sqrt(2.0) * EPS))

    def _build_neumann_banded(nx, r):
        upper = np.full(nx, -r, dtype=np.float64)
        main = np.full(nx, 1.0 + 2.0 * r, dtype=np.float64)
        lower = np.full(nx, -r, dtype=np.float64)
        main[0] = 1.0 + r
        main[-1] = 1.0 + r
        upper[0] = 0.0
        lower[-1] = 0.0
        return np.stack([upper, main, lower], axis=0)

    def _solve_one(nx, params):
        dx = 2.0 / (nx - 1)
        r = (EPS * EPS) * DT / (dx * dx)
        a_banded = _build_neumann_banded(nx, r)
        u = _build_ic(nx, params)
        for _ in range(N_STEPS):
            rhs = u + DT * (u - u * u * u)
            u = solve_banded((1, 1), a_banded, rhs)
        return u

    def generate(fidelity_levels, n_samples, seed):
        log.info("allen_cahn.generate")
        if n_samples <= 0:
            raise ValueError(f"n_samples must be positive, got {n_samples}.")
        if not fidelity_levels:
            raise ValueError("fidelity_levels must not be empty.")
        rng = np.random.default_rng(seed)
        centers = rng.uniform(-0.7, 0.7, size=(n_samples,))
        signs = rng.choice([-1.0, 1.0], size=(n_samples,))
        x_shared = np.stack([centers, signs], axis=-1).astype(np.float64)
        out = {}
        for level in fidelity_levels:
            if level < 4:
                raise ValueError(f"fidelity level must be >= 4, got {level}.")
            y = np.empty((n_samples, level), dtype=np.float64)
            for i in range(n_samples):
                y[i] = _solve_one(level, x_shared[i])
            out[int(level)] = {"X": x_shared.copy(), "Y": y}
        return out

    return generate


def _make_burgers_param():
    import math
    import numpy as np

    T_FINAL = 1.0
    U_MAX = 1.0
    N_MODES = 4
    INPUT_DIM = N_MODES + 1
    NU_MIN = 1e-3
    NU_MAX = 1e-1

    def _build_ic(nx, amps, phases):
        x = np.arange(nx, dtype=np.float64) / nx
        u0 = np.zeros(nx, dtype=np.float64)
        for k in range(1, N_MODES + 1):
            u0 += (amps[k - 1] / k) * np.sin(2.0 * np.pi * k * x + phases[k - 1])
        peak = float(np.max(np.abs(u0)))
        if peak > 0.0:
            u0 /= peak
        return u0

    def _cfl_dt(nx, nu):
        dx = 1.0 / nx
        dt_cfl = 0.4 * min(dx / U_MAX, 0.5 * dx * dx / nu)
        n_steps = max(1, int(math.ceil(T_FINAL / dt_cfl)))
        return T_FINAL / n_steps, n_steps

    def _rhs(u, k, dealias_mask, nu):
        u_hat = np.fft.fft(u)
        u_hat_d = u_hat * dealias_mask
        u_d = np.fft.ifft(u_hat_d).real
        ux_d = np.fft.ifft(1j * k * u_hat_d).real
        nonlinear_hat = np.fft.fft(u_d * ux_d) * dealias_mask
        viscous_hat = -nu * (k * k) * u_hat
        rhs_hat = -nonlinear_hat + viscous_hat
        return np.fft.ifft(rhs_hat).real

    def _solve_one(nx, amps, phases, nu):
        k = 2.0 * np.pi * np.fft.fftfreq(nx, d=1.0 / nx)
        n_keep = nx // 3
        dealias_mask = (np.abs(k) <= 2.0 * np.pi * n_keep).astype(np.float64)
        dt, n_steps = _cfl_dt(nx, nu)
        u = _build_ic(nx, amps, phases)
        for _ in range(n_steps):
            k1 = _rhs(u, k, dealias_mask, nu)
            k2 = _rhs(u + 0.5 * dt * k1, k, dealias_mask, nu)
            k3 = _rhs(u + 0.5 * dt * k2, k, dealias_mask, nu)
            k4 = _rhs(u + dt * k3, k, dealias_mask, nu)
            u = u + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
        return u

    def generate(fidelity_levels, n_samples, seed):
        log.info("burgers_param.generate")
        if n_samples <= 0:
            raise ValueError(f"n_samples must be positive, got {n_samples}.")
        if not fidelity_levels:
            raise ValueError("fidelity_levels must not be empty.")
        rng = np.random.default_rng(seed)
        amps = rng.uniform(-1.0, 1.0, size=(n_samples, N_MODES))
        phases = rng.uniform(0.0, 2.0 * np.pi, size=(n_samples, N_MODES))
        log_nu = rng.uniform(math.log10(NU_MIN), math.log10(NU_MAX), size=(n_samples,))
        nus = 10.0 ** log_nu
        x_shared = np.concatenate([amps, log_nu[:, None]], axis=1).astype(np.float64)
        out = {}
        for level in fidelity_levels:
            if level < 4:
                raise ValueError(f"fidelity level must be >= 4, got {level}.")
            y = np.empty((n_samples, level), dtype=np.float64)
            for i in range(n_samples):
                y[i] = _solve_one(level, amps[i], phases[i], float(nus[i]))
            out[int(level)] = {"X": x_shared.copy(), "Y": y}
        return out

    return generate


def _make_darcy():
    import numpy as np
    from scipy.sparse import csr_matrix
    from scipy.sparse.linalg import spsolve

    L_CORR = 0.2
    SIGMA_LOGK = 1.0
    N_KL = 16
    N_REF = 48
    INPUT_DIM = N_KL
    FORCING = 1.0

    def _build_kl_basis(n_ref, l_corr, sigma, n_kl):
        coords = np.stack(
            np.meshgrid(
                np.linspace(0.0, 1.0, n_ref),
                np.linspace(0.0, 1.0, n_ref),
                indexing="ij",
            ),
            axis=-1,
        ).reshape(-1, 2)
        d = np.linalg.norm(coords[:, None, :] - coords[None, :, :], axis=-1)
        cov = (sigma * sigma) * np.exp(-d / l_corr)
        w, v = np.linalg.eigh(cov)
        idx = np.argsort(w)[::-1][:n_kl]
        eigvals = np.maximum(w[idx], 0.0)
        eigvecs = v[:, idx].reshape(n_ref, n_ref, n_kl)
        return eigvals, eigvecs

    def _bilinear_interp_eigvec(eigvec_ref, nx, ny):
        n_ref = eigvec_ref.shape[0]
        xs_t = np.linspace(0.0, 1.0, nx)
        ys_t = np.linspace(0.0, 1.0, ny)
        xs_r = np.linspace(0.0, 1.0, n_ref)
        ys_r = np.linspace(0.0, 1.0, n_ref)
        fx = np.clip(np.searchsorted(xs_r, xs_t) - 1, 0, n_ref - 2)
        fy = np.clip(np.searchsorted(ys_r, ys_t) - 1, 0, n_ref - 2)
        tx = (xs_t - xs_r[fx]) / (xs_r[fx + 1] - xs_r[fx])
        ty = (ys_t - ys_r[fy]) / (ys_r[fy + 1] - ys_r[fy])
        a = eigvec_ref[np.ix_(fy, fx)]
        b = eigvec_ref[np.ix_(fy, fx + 1)]
        c = eigvec_ref[np.ix_(fy + 1, fx)]
        d = eigvec_ref[np.ix_(fy + 1, fx + 1)]
        txg = tx[None, :]
        tyg = ty[:, None]
        return (1 - tyg) * ((1 - txg) * a + txg * b) + tyg * ((1 - txg) * c + txg * d)

    def _logK_field(z, eigvals, eigvecs_grid):
        weights = np.sqrt(eigvals) * z
        return eigvecs_grid @ weights

    def _solve_one(z, eigvals, eigvecs_ref, nx, ny):
        eigvecs_grid = np.empty((ny, nx, eigvals.shape[0]), dtype=np.float64)
        for j in range(eigvals.shape[0]):
            eigvecs_grid[:, :, j] = _bilinear_interp_eigvec(eigvecs_ref[:, :, j], nx, ny)
        log_k = _logK_field(z, eigvals, eigvecs_grid)
        k_field = np.exp(log_k)
        hx = 1.0 / (nx + 1)
        hy = 1.0 / (ny + 1)
        n = nx * ny
        rows, cols, vals = [], [], []

        def idx(i, j):
            return i * nx + j

        for i in range(ny):
            for j in range(nx):
                p = idx(i, j)
                k_c = k_field[i, j]
                k_w = 2.0 * k_c * k_field[i, j - 1] / (k_c + k_field[i, j - 1]) if j > 0 else k_c
                k_e = 2.0 * k_c * k_field[i, j + 1] / (k_c + k_field[i, j + 1]) if j < nx - 1 else k_c
                k_s = 2.0 * k_c * k_field[i - 1, j] / (k_c + k_field[i - 1, j]) if i > 0 else k_c
                k_n = 2.0 * k_c * k_field[i + 1, j] / (k_c + k_field[i + 1, j]) if i < ny - 1 else k_c
                ax = (k_w + k_e) / (hx * hx)
                ay = (k_s + k_n) / (hy * hy)
                rows.append(p); cols.append(p); vals.append(ax + ay)
                if j > 0:
                    rows.append(p); cols.append(idx(i, j - 1)); vals.append(-k_w / (hx * hx))
                if j < nx - 1:
                    rows.append(p); cols.append(idx(i, j + 1)); vals.append(-k_e / (hx * hx))
                if i > 0:
                    rows.append(p); cols.append(idx(i - 1, j)); vals.append(-k_s / (hy * hy))
                if i < ny - 1:
                    rows.append(p); cols.append(idx(i + 1, j)); vals.append(-k_n / (hy * hy))
        a = csr_matrix((vals, (rows, cols)), shape=(n, n))
        rhs = np.full(n, FORCING, dtype=np.float64)
        u_flat = spsolve(a, rhs)
        return u_flat.reshape(ny, nx)

    def generate(fidelity_levels, n_samples, seed):
        log.info("darcy.generate")
        if n_samples <= 0:
            raise ValueError(f"n_samples must be positive, got {n_samples}.")
        if not fidelity_levels:
            raise ValueError("fidelity_levels must not be empty.")
        eigvals, eigvecs_ref = _build_kl_basis(N_REF, L_CORR, SIGMA_LOGK, N_KL)
        rng = np.random.default_rng(seed)
        z_shared = rng.standard_normal(size=(n_samples, N_KL)).astype(np.float64)
        out = {}
        for level in fidelity_levels:
            if level < 4:
                raise ValueError(f"fidelity level must be >= 4, got {level}.")
            y = np.empty((n_samples, level * level), dtype=np.float64)
            for i in range(n_samples):
                y[i] = _solve_one(z_shared[i], eigvals, eigvecs_ref, level, level).reshape(-1)
            out[int(level)] = {"X": z_shared.copy(), "Y": y}
        return out

    return generate


def _make_lid_driven_cavity():
    import math
    import numpy as np
    from scipy.sparse import csr_matrix
    from scipy.sparse.linalg import factorized

    T_FINAL = 5.0
    U_LID = 1.0
    RE_MIN = 100.0
    RE_MAX = 1000.0
    INPUT_DIM = 1
    STEADY_TOL = 1e-4
    MAX_STEPS = 8000
    DT_SAFETY = 0.125

    def _build_poisson_factor(nx, ny):
        nxi = nx - 2
        nyi = ny - 2
        n = nxi * nyi
        hx = 1.0 / (nx - 1)
        hy = 1.0 / (ny - 1)
        inv_hx2 = 1.0 / (hx * hx)
        inv_hy2 = 1.0 / (hy * hy)
        rows, cols, vals = [], [], []
        for i in range(nyi):
            for j in range(nxi):
                p = i * nxi + j
                rows.append(p); cols.append(p); vals.append(-2.0 * (inv_hx2 + inv_hy2))
                if j > 0:
                    rows.append(p); cols.append(p - 1); vals.append(inv_hx2)
                if j < nxi - 1:
                    rows.append(p); cols.append(p + 1); vals.append(inv_hx2)
                if i > 0:
                    rows.append(p); cols.append(p - nxi); vals.append(inv_hy2)
                if i < nyi - 1:
                    rows.append(p); cols.append(p + nxi); vals.append(inv_hy2)
        a = csr_matrix((vals, (rows, cols)), shape=(n, n)).tocsc()
        return factorized(a)

    def _solve_psi(omega, solve_poisson):
        ny, nx = omega.shape
        nyi = ny - 2
        nxi = nx - 2
        rhs = -omega[1:-1, 1:-1].reshape(-1)
        psi_int = solve_poisson(rhs).reshape(nyi, nxi)
        psi = np.zeros_like(omega)
        psi[1:-1, 1:-1] = psi_int
        return psi

    def _apply_vorticity_bcs(omega, psi, hx, hy):
        omega[-1, :] = 2.0 * (psi[-1, :] - psi[-2, :]) / (hy * hy) - 2.0 * U_LID / hy
        omega[0, :] = 2.0 * (psi[0, :] - psi[1, :]) / (hy * hy)
        omega[:, 0] = 2.0 * (psi[:, 0] - psi[:, 1]) / (hx * hx)
        omega[:, -1] = 2.0 * (psi[:, -1] - psi[:, -2]) / (hx * hx)

    def _rhs(omega, psi, hx, hy, nu):
        o = omega
        p = psi
        u_int = (p[2:, 1:-1] - p[:-2, 1:-1]) / (2.0 * hy)
        v_int = -(p[1:-1, 2:] - p[1:-1, :-2]) / (2.0 * hx)
        omega_x_back = (o[1:-1, 1:-1] - o[1:-1, :-2]) / hx
        omega_x_fwd = (o[1:-1, 2:] - o[1:-1, 1:-1]) / hx
        omega_x = np.where(u_int >= 0.0, omega_x_back, omega_x_fwd)
        omega_y_back = (o[1:-1, 1:-1] - o[:-2, 1:-1]) / hy
        omega_y_fwd = (o[2:, 1:-1] - o[1:-1, 1:-1]) / hy
        omega_y = np.where(v_int >= 0.0, omega_y_back, omega_y_fwd)
        omega_xx = (o[1:-1, 2:] - 2.0 * o[1:-1, 1:-1] + o[1:-1, :-2]) / (hx * hx)
        omega_yy = (o[2:, 1:-1] - 2.0 * o[1:-1, 1:-1] + o[:-2, 1:-1]) / (hy * hy)
        rhs_int = -(u_int * omega_x + v_int * omega_y) + nu * (omega_xx + omega_yy)
        out = np.zeros_like(omega)
        out[1:-1, 1:-1] = rhs_int
        return out

    def _solve_one(nx, ny, re_value):
        nu = U_LID * 1.0 / re_value
        hx = 1.0 / (nx - 1)
        hy = 1.0 / (ny - 1)
        h = min(hx, hy)
        dt = DT_SAFETY * min(h * h / nu, h / U_LID)
        n_steps_target = max(1, int(math.ceil(T_FINAL / dt)))
        n_steps = min(n_steps_target, MAX_STEPS)
        solve_poisson = _build_poisson_factor(nx, ny)
        omega = np.zeros((ny, nx), dtype=np.float64)
        psi = np.zeros((ny, nx), dtype=np.float64)
        _apply_vorticity_bcs(omega, psi, hx, hy)
        for step in range(n_steps):
            omega_prev = omega.copy()
            psi = _solve_psi(omega, solve_poisson)
            _apply_vorticity_bcs(omega, psi, hx, hy)
            k1 = _rhs(omega, psi, hx, hy, nu)
            omega_mid = omega + 0.5 * dt * k1
            psi_mid = _solve_psi(omega_mid, solve_poisson)
            _apply_vorticity_bcs(omega_mid, psi_mid, hx, hy)
            k2 = _rhs(omega_mid, psi_mid, hx, hy, nu)
            omega = omega + dt * k2
            psi = _solve_psi(omega, solve_poisson)
            _apply_vorticity_bcs(omega, psi, hx, hy)
            if step > 0 and step % 25 == 0:
                res = float(np.max(np.abs(omega - omega_prev))) / dt
                if res < STEADY_TOL:
                    break
        return omega

    def generate(fidelity_levels, n_samples, seed):
        log.info("cavity.generate")
        if n_samples <= 0:
            raise ValueError(f"n_samples must be positive, got {n_samples}.")
        if not fidelity_levels:
            raise ValueError("fidelity_levels must not be empty.")
        rng = np.random.default_rng(seed)
        log_re = rng.uniform(math.log10(RE_MIN), math.log10(RE_MAX), size=(n_samples,))
        re_values = (10.0 ** log_re).astype(np.float64)
        x_shared = re_values[:, None]
        out = {}
        for level in fidelity_levels:
            if level < 4:
                raise ValueError(f"fidelity level must be >= 4, got {level}.")
            y = np.empty((n_samples, level * level), dtype=np.float64)
            for i in range(n_samples):
                y[i] = _solve_one(level, level, float(re_values[i])).reshape(-1)
            out[int(level)] = {"X": x_shared.copy(), "Y": y}
        return out

    return generate


GENERATORS = {
    "poisson_generated":             _make_poisson(),
    "heat_generated":                _make_heat(),
    "burgers_generated":             _make_burgers(),
    "advection_diffusion_generated": _make_advection_diffusion(),
    "allen_cahn_generated":          _make_allen_cahn(),
    "burgers_param_generated":       _make_burgers_param(),
    "darcy_generated":               _make_darcy(),
    "lid_driven_cavity_generated":   _make_lid_driven_cavity(),
}

LEVELS = {
    "poisson_generated":             [16, 32, 64],
    "heat_generated":                [16, 32, 64],
    "burgers_generated":             [64, 128, 256],
    "advection_diffusion_generated": [32, 64],
    "allen_cahn_generated":          [64, 128, 256],
    "burgers_param_generated":       [64, 128, 256],
    "darcy_generated":               [32, 64, 128],
    "lid_driven_cavity_generated":   [32, 64, 128],
}

SEED = 42
TRAIN_FRAC = 0.8


def main() -> None:
    out_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("./mffpbench_generated")
    n_samples = int(sys.argv[2]) if len(sys.argv) > 2 else 500
    only = sys.argv[3] if len(sys.argv) > 3 else None
    names = [only] if only else list(GENERATORS)
    n_train = int(round(n_samples * TRAIN_FRAC))
    for name in names:
        if name not in GENERATORS:
            raise SystemExit(f"unknown dataset {name!r}; choices: {list(GENERATORS)}")
        gen = GENERATORS[name]
        levels = LEVELS[name]
        t0 = time.time()
        data = gen(levels, n_samples, SEED)
        out_dir = out_root / name
        out_dir.mkdir(parents=True, exist_ok=True)
        for li, level in enumerate(sorted(data), start=1):
            X = data[level]["X"]
            Y = data[level]["Y"]
            np.savez(out_dir / f"train_l{li}.npz", x=X[:n_train], y=Y[:n_train])
            np.savez(out_dir / f"test_l{li}.npz", x=X[n_train:], y=Y[n_train:])
        print(f"{name}: N={n_samples} ({n_train}/{n_samples - n_train}) "
              f"levels={sorted(data)} {time.time() - t0:.1f}s", flush=True)


if __name__ == "__main__":
    main()
