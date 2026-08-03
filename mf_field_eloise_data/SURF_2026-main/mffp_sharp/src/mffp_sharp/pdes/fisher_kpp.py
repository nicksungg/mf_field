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

dt is provisional (validate on the box). IC: band-limited field in [0,1] built
deterministically from the exported ic_c* coefficients (common/ic_encoding) on the
coarsest grid, spectrally interpolated up -> identical continuous IC per level.

Field stored: u at fixed output time T (front developed, pre-domain-fill).
"""
from __future__ import annotations

import numpy as np

from ..common import ic_encoding
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
    """Draw n Fisher-KPP condition specs (Latin-hypercube over D / r + IC coeffs).

    `ic_modes` (config constant, default 3) widens the 2D IC mode square, which
    raises front density (IC level crossings) and condition dimension (16 coeffs
    at m=3, 48 at m=5). It is NOT a fidelity-gap lever: on the canonical measure
    (LF spectrally interpolated to HF; the block-average numbers previously
    quoted here carried a ~0.02-0.05 operator-mismatch floor and are retracted,
    see condition_completeness PROPOSAL) the T=0.30 gap is ~4.6e-4 at m=3 vs
    ~3.2e-4 at m=5 (measured 2026-08-03) — the same weak-gap order either way;
    the gap lever is solve time for nonlinear structure to build.
    """
    assert ndim in NDIMS_SUPPORTED, f"fisher_kpp supports {NDIMS_SUPPORTED}, got {ndim}"
    m2d = int(sampling_cfg.get("ic_modes", 3))
    draws = latin_hypercube(
        {"D": tuple(sampling_cfg["D_range"]),
         "r": tuple(sampling_cfg["r_range"]),
         **ic_encoding.ic_ranges(ndim, m2d)}, n, seed)
    return [{"D": draws["D"][i], "r": draws["r"][i],
             **{k: draws[k][i] for k in ic_encoding.ic_names(ndim, m2d)},
             "ic_modes": m2d,
             "domain_size": sampling_cfg["domain_size"], "ndim": ndim,
             "seed": seed + i} for i in range(n)]


def generate_sample(spec: dict, resolutions: list[int], hf_res: int, output_time: float
                    ) -> tuple[dict[int, np.ndarray], np.ndarray, list[str]]:
    """Generate one Fisher-KPP sample across the fidelity ladder (1D or 2D)."""
    ndim = int(spec["ndim"])
    res_min = min(resolutions)
    m2d = int(spec.get("ic_modes", 3))
    coeffs = ic_encoding.coeffs_from_spec(spec, ndim, m2d)
    ic_coarse = 0.5 + ic_encoding.build_ic(coeffs, res_min, 0.5, ndim)   # in [0,1]
    fields = {
        res: _solve(spectral_interp(ic_coarse, res), spec["D"], spec["r"],
                    spec["domain_size"], output_time)
        for res in resolutions
    }
    cond = np.array([spec["D"], spec["r"], *coeffs], dtype=np.float64)
    names = ["D", "r"] + ic_encoding.ic_names(ndim, m2d)
    return fields, cond, names
