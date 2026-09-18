"""Porous-medium equation (degenerate diffusion; compact-support sharp edge).

PME:  u_t = laplace(u^m),  m > 1.
Degenerate (diffusivity m u^(m-1) -> 0 as u -> 0), so solutions have COMPACT SUPPORT
with a sharp moving free boundary -- the high-wavenumber feature. The Barenblatt-Pattle
self-similar solution is exact and is the correctness test.

SOLVER: explicit finite-difference u^{n+1} = u^n + dt * laplace_h(u^n^m), with a
CFL-chosen substep dt and max(u,0) positivity. Periodic stencil (np.roll) on a domain
large enough that the compact support stays interior. SAME analytic IC per grid.

Field stored: u >= 0 at fixed output time T.
"""
from __future__ import annotations

import numpy as np

NDIMS_SUPPORTED = (1, 2)

_CFL = 0.2


def _laplacian(a: np.ndarray, h: float) -> np.ndarray:
    out = -2.0 * a.ndim * a
    for ax in range(a.ndim):
        out = out + np.roll(a, 1, ax) + np.roll(a, -1, ax)
    return out / h ** 2


def _solve(u0: np.ndarray, m: float, domain_size: float, output_time: float) -> np.ndarray:
    res = u0.shape[0]
    ndim = u0.ndim
    h = domain_size / res
    u = np.maximum(u0.astype(np.float64), 0.0).copy()
    # CFL for the (linearized) degenerate diffusion: dt < cfl * h^2 / (2*ndim*m*umax^(m-1))
    umax = max(float(u.max()), 1e-12)
    dt_cfl = _CFL * h ** 2 / (2.0 * ndim * m * umax ** (m - 1.0))
    nsteps = max(1, int(np.ceil(output_time / dt_cfl)))
    dt = output_time / nsteps
    for _ in range(nsteps):
        u = u + dt * _laplacian(u ** m, h)
        u = np.maximum(u, 0.0)
    return u


def _barenblatt_1d(x: np.ndarray, t: float, m: float, mass: float = 1.0) -> np.ndarray:
    """Barenblatt-Pattle exact solution in 1D (d=1)."""
    alpha = 1.0 / (m + 1.0)
    beta = alpha * (m - 1.0) / (2.0 * m)
    # C set so the profile is O(mass); a fixed C is fine for the self-similarity test.
    C = (mass) ** (2.0 * (m - 1.0) * alpha) if mass else 1.0
    inner = C - beta * (x ** 2) * t ** (-2.0 * alpha)
    inner = np.maximum(inner, 0.0)
    return t ** (-alpha) * inner ** (1.0 / (m - 1.0))


def sample_configs(n: int, sampling_cfg: dict, ndim: int, seed: int) -> list[dict]:
    assert ndim in NDIMS_SUPPORTED, f"porous_medium supports {NDIMS_SUPPORTED}, got {ndim}"
    rng = np.random.default_rng(seed)
    lm, hm = sampling_cfg["m_range"]
    la, ha = sampling_cfg["ic_amplitude_range"]
    return [{"m": float(rng.uniform(lm, hm)), "ic_amplitude": float(rng.uniform(la, ha)),
             "domain_size": sampling_cfg["domain_size"], "ndim": ndim,
             "seed": seed + i} for i in range(n)]


def generate_sample(spec: dict, resolutions: list[int], hf_res: int, output_time: float
                    ) -> tuple[dict[int, np.ndarray], np.ndarray, list[str]]:
    """Generate one PME sample. IC: a compact parabolic bump (1 - r^2)_+ * amplitude,
    evaluated analytically on each grid (same continuous IC), then evolved per level."""
    ndim = int(spec["ndim"])
    L = spec["domain_size"]
    fields = {}
    for res in resolutions:
        xs = np.arange(res) * L / res - L / 2.0
        axes = np.meshgrid(*([xs] * ndim), indexing="ij")
        r2 = sum(a ** 2 for a in axes)
        u0 = spec["ic_amplitude"] * np.maximum(1.0 - r2, 0.0)     # compact bump
        fields[res] = _solve(u0, spec["m"], L, output_time)
    cond = np.array([spec["m"], spec["ic_amplitude"]], dtype=np.float64)
    names = ["m", "ic_amplitude"]
    return fields, cond, names
