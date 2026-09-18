"""Gray-Scott (coupled reaction-diffusion; many sharp spots/stripes) dataset generation.

Gray-Scott:  u_t = Du laplace(u) - u v^2 + F (1 - u)
             v_t = Dv laplace(v) + u v^2 - (F + k) v.
A coupled 2-field system whose self-replicating spots / worms / stripes carry sharp
high-wavenumber structure (The Well's 6 canonical Pearson (F,k) regimes). Distinct
mechanism: multi-front pattern formation. 2D. The stored field is the ACTIVATOR v.

SOLVER: semi-implicit IMEX (same family as Allen-Cahn / Fisher-KPP, on a 2-field state):
  - implicit diffusion per field via the discrete -Laplacian symbol (bounded ->
    consistent coarse solve): denom_u = 1/dt + Du*mlap, denom_v = 1/dt + Dv*mlap;
  - explicit reaction (-u v^2 + F(1-u)) and (u v^2 - (F+k) v);
  - fresh FFT each step. SAME dt at every resolution.

IC (The Well style): u=1, v=0 background with a central perturbed square (u=0.5, v=0.25)
plus small noise, built on the coarsest grid and spectrally interpolated up so every
ladder level seeds the SAME continuous IC. Field stored: v at fixed output time T.
"""
from __future__ import annotations

import numpy as np

from ..common.spectral import spectral_interp, neg_laplacian_symbol
from ..common.sampling import latin_hypercube

NDIMS_SUPPORTED = (2,)

_DT = 1.0  # GS is mild with tiny diffusivities; dt~1 is standard. (TBD-box.)


def _solve(u0: np.ndarray, v0: np.ndarray, Du: float, Dv: float, F: float, k_rate: float,
           domain_size: float, output_time: float, dt: float = _DT):
    """Semi-implicit IMEX Gray-Scott solve from (u0, v0); return (u, v)."""
    res = u0.shape[0]
    h = domain_size / res
    mlap = neg_laplacian_symbol(res, h, 2)
    nsteps = int(np.ceil(output_time / dt))
    dt = output_time / nsteps
    denom_u = 1.0 / dt + Du * mlap
    denom_v = 1.0 / dt + Dv * mlap
    u = u0.astype(np.float64).copy()
    v = v0.astype(np.float64).copy()
    for _ in range(nsteps):
        uvv = u * v * v
        ru = -uvv + F * (1.0 - u)
        rv = uvv - (F + k_rate) * v
        uh = (np.fft.fft2(u) * (1.0 / dt) + np.fft.fft2(ru)) / denom_u
        vh = (np.fft.fft2(v) * (1.0 / dt) + np.fft.fft2(rv)) / denom_v
        u = np.real(np.fft.ifft2(uh))
        v = np.real(np.fft.ifft2(vh))
    return u, v


def sample_configs(n: int, sampling_cfg: dict, ndim: int, seed: int) -> list[dict]:
    """Draw n Gray-Scott condition specs (Latin-hypercube over F / k_rate)."""
    assert ndim in NDIMS_SUPPORTED, f"gray_scott supports {NDIMS_SUPPORTED}, got {ndim}"
    draws = latin_hypercube(
        {"F": tuple(sampling_cfg["F_range"]),
         "k_rate": tuple(sampling_cfg["k_rate_range"])}, n, seed)
    return [{"F": draws["F"][i], "k_rate": draws["k_rate"][i],
             "Du": sampling_cfg["Du"], "Dv": sampling_cfg["Dv"],
             "domain_size": sampling_cfg["domain_size"], "ndim": ndim,
             "seed": seed + i} for i in range(n)]


def generate_sample(spec: dict, resolutions: list[int], hf_res: int, output_time: float
                    ) -> tuple[dict[int, np.ndarray], np.ndarray, list[str]]:
    """Generate one Gray-Scott sample across the fidelity ladder (2D). Stored field = v."""
    res_min = min(resolutions)
    rng = np.random.default_rng(spec["seed"])
    u0c = np.ones((res_min, res_min))
    v0c = np.zeros((res_min, res_min))
    s = max(2, res_min // 8)
    a, b = res_min // 2 - s, res_min // 2 + s
    u0c[a:b, a:b] = 0.5
    v0c[a:b, a:b] = 0.25
    u0c += 0.01 * (2 * rng.random((res_min, res_min)) - 1)
    v0c += 0.01 * (2 * rng.random((res_min, res_min)) - 1)
    fields = {}
    for res in resolutions:
        u0 = spectral_interp(u0c, res)
        v0 = spectral_interp(v0c, res)
        _, v = _solve(u0, v0, spec["Du"], spec["Dv"], spec["F"], spec["k_rate"],
                      spec["domain_size"], output_time)
        fields[res] = v
    cond = np.array([spec["F"], spec["k_rate"]], dtype=np.float64)
    names = ["F", "k_rate"]
    return fields, cond, names
