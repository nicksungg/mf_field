"""Allen-Cahn (sharp interface, NON-conserved phase field) dataset generation.

Allen-Cahn:  d u/dt = M ( eps^2 * laplace(u) - (u^3 - u) ).
Thin interfaces of width ~eps between u = +/-1. Unlike Cahn-Hilliard the order
parameter is NOT conserved (the bulk relaxes to the nearer well), and the PDE is
2nd order, so it is milder than CH. Tagged 'near-CH' in the build set.

SOLVER: semi-implicit Fourier, cloned from the validated Cahn-Hilliard scheme:
  - the stiff diffusion -M eps^2 (-laplace) is treated IMPLICITLY, diagonalized by
    FFT against the DISCRETE 5-point -laplacian symbol (bounded -> consistent on the
    under-resolved coarse grid, no Gibbs blow-up);
  - the reaction -M(u^3 - u) is explicit;
  - the field is re-FFT'd from the real state each step (stays Hermitian).
np.fft.fftn/ifftn serve 1D and 2D with one body. SAME dt at every resolution.

dt is provisional (validate stability across the ladder on the box). IC: band-limited
random field on the coarsest grid, spectrally interpolated up so every ladder level
solves the IDENTICAL continuous IC.

Field stored: u at fixed output time T.
"""
from __future__ import annotations

import numpy as np

from ..common.spectral import spectral_interp, neg_laplacian_symbol
from ..common.sampling import latin_hypercube

NDIMS_SUPPORTED = (1, 2)

# Fixed timestep, same at every resolution. Conservative; 1st order in dt. (TBD-box.)
_DT = 1.0e-3


def _solve(u0: np.ndarray, eps: float, mobility: float, domain_size: float,
           output_time: float, dt: float = _DT) -> np.ndarray:
    """Semi-implicit Fourier Allen-Cahn solve from u0 (1D or 2D); return u."""
    res = u0.shape[0]
    h = domain_size / res
    mlap = neg_laplacian_symbol(res, h, u0.ndim)          # >= 0, bounded
    nsteps = int(np.ceil(output_time / dt))
    dt = output_time / nsteps                              # land exactly on T
    denom = 1.0 / dt + mobility * eps ** 2 * mlap          # implicit diffusion
    u = u0.astype(np.float64).copy()
    for _ in range(nsteps):
        uh = np.fft.fftn(u)                               # FRESH each step -> Hermitian
        reaction = mobility * (u ** 3 - u)                # explicit double-well force
        uh_new = (uh * (1.0 / dt) - np.fft.fftn(reaction)) / denom
        u = np.real(np.fft.ifftn(uh_new))
    return u


def sample_configs(n: int, sampling_cfg: dict, ndim: int, seed: int) -> list[dict]:
    """Draw n Allen-Cahn condition specs (Latin-hypercube over eps/mobility/mean)."""
    assert ndim in NDIMS_SUPPORTED, f"allen_cahn supports {NDIMS_SUPPORTED}, got {ndim}"
    draws = latin_hypercube(
        {"eps": tuple(sampling_cfg["eps_range"]),
         "mobility": tuple(sampling_cfg["mobility_range"]),
         "mean_composition": tuple(sampling_cfg["mean_composition_range"])}, n, seed)
    return [{"eps": draws["eps"][i], "mobility": draws["mobility"][i],
             "mean_composition": draws["mean_composition"][i],
             "domain_size": sampling_cfg["domain_size"], "ndim": ndim,
             "seed": seed + i} for i in range(n)]


def generate_sample(spec: dict, resolutions: list[int], hf_res: int, output_time: float
                    ) -> tuple[dict[int, np.ndarray], np.ndarray, list[str]]:
    """Generate one Allen-Cahn sample across the fidelity ladder (1D or 2D)."""
    ndim = int(spec["ndim"])
    res_min = min(resolutions)
    rng = np.random.default_rng(spec["seed"])
    shape = (res_min,) * ndim
    ic_coarse = spec["mean_composition"] + 0.1 * (2 * rng.random(shape) - 1)
    fields = {
        res: _solve(spectral_interp(ic_coarse, res), spec["eps"], spec["mobility"],
                    spec["domain_size"], output_time)
        for res in resolutions
    }
    cond = np.array([spec["eps"], spec["mobility"], spec["mean_composition"]],
                    dtype=np.float64)
    names = ["eps", "mobility", "mean_composition"]
    return fields, cond, names
