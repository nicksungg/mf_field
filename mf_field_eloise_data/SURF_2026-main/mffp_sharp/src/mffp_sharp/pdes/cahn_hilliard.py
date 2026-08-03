"""2D Cahn-Hilliard (sharp interface) dataset generation.

Cahn-Hilliard: d c/dt = M * laplace( c^3 - c - eps^2 * laplace(c) ).
Solutions develop thin interfaces of width ~eps between c=+/-1 phases.

LF recipe: coarse grid that UNDER-RESOLVES eps -> blurred interface.
HF recipe: fine grid that resolves eps (h <= eps/2) -> sharp interface.
Same solver, same IC at every fidelity; only the grid changes.

CRITICAL coupling: eps must be chosen so 32^2 under-resolves it while 128^2
resolves it. If 32^2 already matches 128^2, eps is too large (or the ladder wrong)
-- this is the per-PDE bottom-rung check in the sample round.

Field stored: composition c at fixed output time T (snapshot, interfaces formed
but pre-full-coarsening).

SOLVER (validated on box 2026-06-15). py-pde's explicit integrator blows up on
this stiff 4th-order PDE (verified: real-space reference shows the equation/config
are physically fine, solution bounded). We use a custom semi-implicit Fourier
scheme instead:
  - the stiff biharmonic (-gamma*lap^2) is treated IMPLICITLY, diagonalized by FFT
    using the *discrete* 5-point Laplacian symbol (bounded -> no spectral Gibbs
    blow-up on the under-resolved coarse grid; this IS a consistent coarse solve);
  - the mild -lap(c) and the nonlinear lap(c^3) are explicit;
  - the field is re-FFT'd from the real state each step so the Fourier state stays
    exactly Hermitian (carrying the complex state drifts non-Hermitian and the
    unstable modes amplify the drift -> THE blow-up bug we hit).
Stable to dt~5e-4 across the 32/64/128 ladder; mass-conserving; phase-separates to
+/-1. SAME dt at every resolution (consistency: only the grid changes).

IC: a band-limited field built deterministically from the exported ic_c* coefficients
(common/ic_encoding, scale 0.1 -- the generate_learnable.py convention) on the coarsest
grid and spectrally interpolated up, so every ladder level solves the IDENTICAL
continuous IC (else each grid would spinodally decompose into a different pattern and
HF-LF residuals would be meaningless).
"""
from __future__ import annotations

import numpy as np

from ..common import ic_encoding
from ..common.spectral import spectral_interp
from ..common.sampling import latin_hypercube

NDIMS_SUPPORTED = (2,)

# Fixed timestep, same at every resolution (consistency: only the grid changes).
# Conservative vs the ~5e-4 stability limit; accuracy is 1st order in dt. (TBD w/ Nicholas.)
_DT = 2.0e-4


def _solve(c0: np.ndarray, eps: float, mobility: float, domain_size: float,
           output_time: float, dt: float = _DT) -> np.ndarray:
    """Semi-implicit Fourier Cahn-Hilliard solve from initial field c0; return c [res,res]."""
    res = c0.shape[0]
    h = domain_size / res
    fr = np.fft.fftfreq(res)
    cx = np.cos(2 * np.pi * fr)
    MX, MY = np.meshgrid(cx, cx, indexing="ij")
    mlap = (2.0 / h ** 2) * (2.0 - MX - MY)          # discrete -laplacian symbol (>=0, bounded)
    gamma = eps ** 2
    nsteps = int(np.ceil(output_time / dt))
    dt = output_time / nsteps                        # land exactly on T
    denom = 1.0 / dt + mobility * gamma * mlap ** 2   # implicit biharmonic
    c = c0.astype(np.float64).copy()
    for _ in range(nsteps):
        ch = np.fft.fft2(c)                          # FRESH each step -> stays Hermitian
        rhs = ch * (1.0 / dt + mobility * mlap) - mobility * mlap * np.fft.fft2(c ** 3)
        c = np.real(np.fft.ifft2(rhs / denom))
    return c


def sample_configs(n: int, sampling_cfg: dict, ndim: int, seed: int) -> list[dict]:
    """Draw n Cahn-Hilliard condition specs (Latin-hypercube over eps/mobility/mean)."""
    assert ndim in NDIMS_SUPPORTED, f"cahn_hilliard supports {NDIMS_SUPPORTED}, got {ndim}"
    draws = latin_hypercube(
        {"eps": tuple(sampling_cfg["eps_range"]),
         "mobility": tuple(sampling_cfg["mobility_range"]),
         "mean_composition": tuple(sampling_cfg["mean_composition_range"]),
         **ic_encoding.ic_ranges(2)}, n, seed)
    return [{"eps": draws["eps"][i], "mobility": draws["mobility"][i],
             "mean_composition": draws["mean_composition"][i],
             **{k: draws[k][i] for k in ic_encoding.ic_names(2)},
             "domain_size": sampling_cfg["domain_size"], "ndim": ndim,
             "seed": seed + i} for i in range(n)]


def generate_sample(spec: dict, resolutions: list[int], hf_res: int, output_time: float
                    ) -> tuple[dict[int, np.ndarray], np.ndarray, list[str]]:
    """Generate one Cahn-Hilliard sample across the fidelity ladder.

    `spec` keys: eps, mobility, mean_composition, domain_size, seed.
    Same eps and same (band-limited) IC at every resolution -- only the grid changes.
    """
    res_min = min(resolutions)
    coeffs = ic_encoding.coeffs_from_spec(spec, 2)
    ic_coarse = spec["mean_composition"] + ic_encoding.build_ic(coeffs, res_min, 0.1, 2)
    fields = {
        res: _solve(spectral_interp(ic_coarse, res), spec["eps"], spec["mobility"],
                    spec["domain_size"], output_time)
        for res in resolutions
    }
    cond = np.array([spec["eps"], spec["mobility"], spec["mean_composition"], *coeffs],
                    dtype=np.float64)
    names = ["eps", "mobility", "mean_composition"] + ic_encoding.ic_names(2)
    return fields, cond, names
