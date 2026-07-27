"""High-wavenumber Helmholtz (steady, oscillatory) dataset generation.

-laplace(u) - k^2 u = f  on [0,L]^2, homogeneous Dirichlet, Gaussian source f.
A STEADY boundary-value problem (no time, no chaos -> dodges the snapshot-time and
LF-divergence criteria). High k -> oscillatory solution with energy at wavenumber ~k;
the coarse grid under-resolves the oscillation (the bottom rung). Solved by sparse
direct factorization (the indefinite system is best handled by a direct solver).

Field stored: u (real) on the interior grid. output_time is ignored (steady problem).
LF = a genuine coarse-grid discretization of the SAME continuous BVP (same analytic
source), never a downsample of the fine solution.
"""
from __future__ import annotations

import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import spsolve

NDIMS_SUPPORTED = (2,)


def _source(res: int, source_width: float, domain_size: float) -> np.ndarray:
    h = domain_size / (res + 1)
    xs = (np.arange(1, res + 1)) * h
    X, Y = np.meshgrid(xs, xs, indexing="ij")
    c = domain_size / 2.0
    return np.exp(-((X - c) ** 2 + (Y - c) ** 2) / (2.0 * source_width ** 2))


def _operator(res: int, k: float, domain_size: float):
    h = domain_size / (res + 1)
    main = -2.0 * np.ones(res)
    off = np.ones(res - 1)
    D = sp.diags([off, main, off], [-1, 0, 1]) / h ** 2     # 1D 2nd difference (Dirichlet)
    I = sp.identity(res)
    lap = sp.kron(I, D) + sp.kron(D, I)                      # 2D Laplacian
    A = (-lap) - k ** 2 * sp.identity(res * res)            # -lap - k^2 I  (indefinite)
    return A.tocsc()


def _solve(res: int, k: float, source_width: float, domain_size: float) -> np.ndarray:
    f = _source(res, source_width, domain_size)
    A = _operator(res, k, domain_size)
    u = spsolve(A, f.ravel())
    return u.reshape(res, res)


def residual(field: np.ndarray, res: int, k: float, source_width: float,
             domain_size: float) -> float:
    """Relative residual ||A u - f|| / ||f|| of the discrete Helmholtz solve."""
    A = _operator(res, k, domain_size)
    f = _source(res, source_width, domain_size).ravel()
    r = A.dot(field.ravel()) - f
    return float(np.linalg.norm(r) / (np.linalg.norm(f) + 1e-30))


def sample_configs(n: int, sampling_cfg: dict, ndim: int, seed: int) -> list[dict]:
    assert ndim in NDIMS_SUPPORTED, f"helmholtz supports {NDIMS_SUPPORTED}, got {ndim}"
    rng = np.random.default_rng(seed)
    lk, hk = sampling_cfg["wavenumber_range"]
    lw, hw = sampling_cfg["source_width_range"]
    return [{"wavenumber": float(rng.uniform(lk, hk)),
             "source_width": float(rng.uniform(lw, hw)),
             "domain_size": sampling_cfg["domain_size"], "ndim": ndim,
             "seed": seed + i} for i in range(n)]


def generate_sample(spec: dict, resolutions: list[int], hf_res: int, output_time: float
                    ) -> tuple[dict[int, np.ndarray], np.ndarray, list[str]]:
    """Steady Helmholtz; output_time ignored. Each resolution solves the same BVP."""
    fields = {res: _solve(res, spec["wavenumber"], spec["source_width"],
                          spec["domain_size"]) for res in resolutions}
    cond = np.array([spec["wavenumber"], spec["source_width"]], dtype=np.float64)
    names = ["wavenumber", "source_width"]
    return fields, cond, names
