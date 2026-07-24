"""Nonlinear Schrodinger (dispersive oscillatory wavepackets) dataset generation.

NLS:  i u_t + (1/2) u_xx + g |u|^2 u = 0   (g>0 focusing, g<0 defocusing).
High-wavenumber content comes from narrow soliton peaks (focusing) or oscillatory
wavepackets (defocusing) -- dispersion, not jumps. Tagged 'distinct'. For data we
use defocusing / sub-critical g (no collapse); the solver is validated on the exact
focusing bright soliton. 1D only (2D NLS deferred). The field is complex; we store
the real INTENSITY |u|^2 (the observable, T-determined field carrying the sharp peaks).

SOLVER: Strang split-step Fourier -- each sub-flow is solved EXACTLY:
  - linear half-step: u_t = (i/2) u_xx -> multiply u_hat by exp(-i k^2 (dt/2) / 2);
  - nonlinear full-step: u_t = i g |u|^2 u -> |u| is invariant, so u *= exp(i g |u|^2 dt);
  - linear half-step again.
Mass (integral of |u|^2) is conserved. SAME dt at every resolution.

IC: band-limited random real field on the coarsest grid, spectrally interpolated up ->
identical continuous IC per level. Field stored: |u(.,T)|^2.
"""
from __future__ import annotations

import numpy as np

from ..common.spectral import spectral_interp
from ..common.sampling import latin_hypercube

NDIMS_SUPPORTED = (1,)

# Fixed timestep, same at every resolution. Split-step is unconditionally stable on the
# linear part; dt bounds nonlinear phase accuracy. Conservative. (TBD-box.)
_DT = 1.0e-3


def _solve(u0: np.ndarray, nonlinearity: float, domain_size: float, output_time: float,
           dt: float = _DT) -> np.ndarray:
    """Strang split-step Fourier NLS solve from u0 (1D); return COMPLEX u."""
    res = u0.shape[0]
    k = 2 * np.pi * np.fft.fftfreq(res, d=domain_size / res)
    nsteps = int(np.ceil(output_time / dt))
    dt = output_time / nsteps
    lin_half = np.exp(-1j * (k ** 2) / 2.0 * (dt / 2.0))   # half linear-step propagator
    u = u0.astype(np.complex128).copy()
    for _ in range(nsteps):
        u = np.fft.ifft(np.fft.fft(u) * lin_half)          # half linear
        u = u * np.exp(1j * nonlinearity * np.abs(u) ** 2 * dt)   # full nonlinear (exact)
        u = np.fft.ifft(np.fft.fft(u) * lin_half)          # half linear
    return u


def sample_configs(n: int, sampling_cfg: dict, ndim: int, seed: int) -> list[dict]:
    """Draw n NLS condition specs (Latin-hypercube over nonlinearity / ic_amplitude)."""
    assert ndim in NDIMS_SUPPORTED, f"nls supports {NDIMS_SUPPORTED}, got {ndim}"
    draws = latin_hypercube(
        {"nonlinearity": tuple(sampling_cfg["nonlinearity_range"]),
         "ic_amplitude": tuple(sampling_cfg["ic_amplitude_range"])}, n, seed)
    return [{"nonlinearity": draws["nonlinearity"][i],
             "ic_amplitude": draws["ic_amplitude"][i],
             "domain_size": sampling_cfg["domain_size"], "ndim": ndim,
             "seed": seed + i} for i in range(n)]


def generate_sample(spec: dict, resolutions: list[int], hf_res: int, output_time: float
                    ) -> tuple[dict[int, np.ndarray], np.ndarray, list[str]]:
    """Generate one NLS sample across the fidelity ladder (1D). Stored field = |u|^2."""
    res_min = min(resolutions)
    rng = np.random.default_rng(spec["seed"])
    ic_coarse = spec["ic_amplitude"] * (2 * rng.random(res_min) - 1)
    fields = {
        res: np.abs(_solve(spectral_interp(ic_coarse, res).astype(np.complex128),
                           spec["nonlinearity"], spec["domain_size"], output_time)) ** 2
        for res in resolutions
    }
    cond = np.array([spec["nonlinearity"], spec["ic_amplitude"]], dtype=np.float64)
    names = ["nonlinearity", "ic_amplitude"]
    return fields, cond, names
