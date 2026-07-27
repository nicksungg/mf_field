"""Fisher-KPP (sharp traveling front) dataset generation.

Fisher-KPP:  d u/dt = D * laplace(u) + r * u (1 - u).
Invasion fronts of width ~sqrt(D/r) and speed 2 sqrt(D r) between the unstable
state u=0 and the stable carrying capacity u=1. Small D/r -> thin (sharp) front;
the LF coarse grid under-resolves it (bottom rung). Tagged 'semi-distinct'.

SOLVER: semi-implicit Fourier (same family as Cahn-Hilliard/Allen-Cahn):
  - implicit diffusion -D (-laplace), diagonalized against the DISCRETE -laplacian
    symbol (bounded -> consistent coarse solve);
  - explicit logistic reaction r u(1-u);
  - fresh FFT each step (Hermitian-safe); np.fft.fftn/ifftn serve 1D and 2D.
The logistic reaction keeps u in [0,1] for small dt; we clip to [0,1] after each
step as a safety net against round-off excursions. SAME dt at every resolution.

dt is provisional (validate on the box). IC: band-limited random field in [0,1] on
the coarsest grid, spectrally interpolated up -> identical continuous IC per level.

Field stored: u at fixed output time T (front developed, pre-domain-fill).
"""
from __future__ import annotations

import numpy as np

from ..common.spectral import spectral_interp, neg_laplacian_symbol
from ..common.sampling import latin_hypercube

NDIMS_SUPPORTED = (1, 2)

# Fixed timestep, same at every resolution. Conservative; 1st order in dt. (TBD-box.)
_DT = 1.0e-4


def _solve(u0: np.ndarray, D: float, r: float, domain_size: float,
           output_time: float, dt: float = _DT) -> np.ndarray:
    """Semi-implicit Fourier Fisher-KPP solve from u0 (1D or 2D); return u in [0,1]."""
    res = u0.shape[0]
    h = domain_size / res
    mlap = neg_laplacian_symbol(res, h, u0.ndim)          # >= 0, bounded
    nsteps = int(np.ceil(output_time / dt))
    dt = output_time / nsteps                              # land exactly on T
    denom = 1.0 / dt + D * mlap                            # implicit diffusion
    u = np.clip(u0.astype(np.float64), 0.0, 1.0).copy()
    for _ in range(nsteps):
        uh = np.fft.fftn(u)                               # FRESH each step -> Hermitian
        reaction = r * u * (1.0 - u)                      # explicit logistic
        uh_new = (uh * (1.0 / dt) + np.fft.fftn(reaction)) / denom
        u = np.clip(np.real(np.fft.ifftn(uh_new)), 0.0, 1.0)
    return u


def sample_configs(n: int, sampling_cfg: dict, ndim: int, seed: int) -> list[dict]:
    """Draw n Fisher-KPP condition specs (Latin-hypercube over D / r)."""
    assert ndim in NDIMS_SUPPORTED, f"fisher_kpp supports {NDIMS_SUPPORTED}, got {ndim}"
    draws = latin_hypercube(
        {"D": tuple(sampling_cfg["D_range"]),
         "r": tuple(sampling_cfg["r_range"])}, n, seed)
    return [{"D": draws["D"][i], "r": draws["r"][i],
             "domain_size": sampling_cfg["domain_size"], "ndim": ndim,
             "seed": seed + i} for i in range(n)]


def generate_sample(spec: dict, resolutions: list[int], hf_res: int, output_time: float
                    ) -> tuple[dict[int, np.ndarray], np.ndarray, list[str]]:
    """Generate one Fisher-KPP sample across the fidelity ladder (1D or 2D)."""
    ndim = int(spec["ndim"])
    res_min = min(resolutions)
    rng = np.random.default_rng(spec["seed"])
    shape = (res_min,) * ndim
    ic_coarse = 0.5 + 0.5 * (2 * rng.random(shape) - 1)   # random in [0,1]
    fields = {
        res: _solve(spectral_interp(ic_coarse, res), spec["D"], spec["r"],
                    spec["domain_size"], output_time)
        for res in resolutions
    }
    cond = np.array([spec["D"], spec["r"]], dtype=np.float64)
    names = ["D", "r"]
    return fields, cond, names
