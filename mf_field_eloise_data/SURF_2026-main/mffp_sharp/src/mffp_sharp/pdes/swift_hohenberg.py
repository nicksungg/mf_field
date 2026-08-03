"""Swift-Hohenberg (pattern-former, spectral PEAK) dataset generation.

Swift-Hohenberg:  d u/dt = r u - (1 + laplace)^2 u - u^3.
Forms striped/hexagonal patterns with a characteristic wavenumber k=1; its spectrum
is a PEAK at k~1 (not a power law or knee), which is exactly the form-agnostic case
the energy-above-cutoff screen is designed to handle. Tagged 'distinct (pattern)'.

SOLVER: semi-implicit Fourier (same family as KS / Cahn-Hilliard):
  - the linear operator L(k) = r - (1 - k^2)^2 is treated IMPLICITLY (it can be
    positive near k^2=1 -> pattern growth; implicit handling stays stable). Uses the
    CONTINUOUS k^2 (SH patterns are smooth and well-resolved, like KS);
  - the cubic -u^3 is explicit, 2/3-rule de-aliased;
  - fresh FFT each step (Hermitian-safe); np.fft.fftn/ifftn serve 1D and 2D.
Stability needs dt < 1/r (so the implicit denom 1/dt - L stays positive); _DT is
conservative. SAME dt at every resolution.

IC: small band-limited field built deterministically from the exported ic_c*
coefficients (common/ic_encoding) on the coarsest grid, spectrally interpolated up
-> identical continuous IC per level (patterns grow from the SAME IC everywhere).

Field stored: u at fixed output time T (pattern developed).
"""
from __future__ import annotations

import numpy as np

from ..common import ic_encoding
from ..common.spectral import spectral_interp
from ..common.sampling import latin_hypercube

NDIMS_SUPPORTED = (1, 2)

# Fixed timestep, same at every resolution. Needs dt < 1/r; conservative. (TBD-box.)
_DT = 0.05


def _solve(u0: np.ndarray, r: float, domain_size: float, output_time: float,
           dt: float = _DT) -> np.ndarray:
    """Semi-implicit Fourier Swift-Hohenberg solve from u0 (1D or 2D); return u."""
    res = u0.shape[0]
    ndim = u0.ndim
    k1 = 2 * np.pi * np.fft.fftfreq(res, d=domain_size / res)
    k_axes = np.meshgrid(*([k1] * ndim), indexing="ij")
    k2 = sum(kk ** 2 for kk in k_axes)
    Lsym = r - (1.0 - k2) ** 2                              # linear operator symbol
    fi = np.fft.fftfreq(res) * res
    keep1 = np.abs(fi) <= res / 3.0                         # 2/3-rule de-alias (cubic)
    mask = np.logical_and.reduce(np.meshgrid(*([keep1] * ndim), indexing="ij"))
    nsteps = int(np.ceil(output_time / dt))
    dt = output_time / nsteps
    denom = 1.0 / dt - Lsym                                 # implicit linear (>0 if dt<1/r)
    u = u0.astype(np.float64).copy()
    for _ in range(nsteps):
        uh = np.fft.fftn(u)                                # FRESH each step -> Hermitian
        nlh = np.fft.fftn(u ** 3) * mask                   # explicit cubic, de-aliased
        uh_new = (uh * (1.0 / dt) - nlh) / denom
        u = np.real(np.fft.ifftn(uh_new))
    return u


def sample_configs(n: int, sampling_cfg: dict, ndim: int, seed: int) -> list[dict]:
    """Draw n Swift-Hohenberg condition specs (Latin-hypercube over r / ic_amplitude)."""
    assert ndim in NDIMS_SUPPORTED, f"swift_hohenberg supports {NDIMS_SUPPORTED}, got {ndim}"
    draws = latin_hypercube(
        {"r": tuple(sampling_cfg["r_range"]),
         "ic_amplitude": tuple(sampling_cfg["ic_amplitude_range"]),
         **ic_encoding.ic_ranges(ndim)}, n, seed)
    return [{"r": draws["r"][i], "ic_amplitude": draws["ic_amplitude"][i],
             **{k: draws[k][i] for k in ic_encoding.ic_names(ndim)},
             "domain_size": sampling_cfg["domain_size"], "ndim": ndim,
             "seed": seed + i} for i in range(n)]


def generate_sample(spec: dict, resolutions: list[int], hf_res: int, output_time: float
                    ) -> tuple[dict[int, np.ndarray], np.ndarray, list[str]]:
    """Generate one Swift-Hohenberg sample across the fidelity ladder (1D or 2D)."""
    ndim = int(spec["ndim"])
    res_min = min(resolutions)
    coeffs = ic_encoding.coeffs_from_spec(spec, ndim)
    ic_coarse = ic_encoding.build_ic(coeffs, res_min, spec["ic_amplitude"], ndim)
    fields = {
        res: _solve(spectral_interp(ic_coarse, res), spec["r"], spec["domain_size"],
                    output_time)
        for res in resolutions
    }
    cond = np.array([spec["r"], spec["ic_amplitude"], *coeffs], dtype=np.float64)
    names = ["r", "ic_amplitude"] + ic_encoding.ic_names(ndim)
    return fields, cond, names
