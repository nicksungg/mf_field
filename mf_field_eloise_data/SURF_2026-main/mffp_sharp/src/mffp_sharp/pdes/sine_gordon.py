"""sine-Gordon (kinks + breathers; dispersive, 2nd-order in TIME) dataset generation.

sine-Gordon:  u_tt = laplace(u) - m^2 sin(u).
A nonlinear wave equation (second order in time) supporting kinks and breathers;
high-wavenumber content from steep kink fronts / breather oscillations. Distinct from
the parabolic/dispersive first-order solvers. 1D+2D.

SOLVER: Strang split-step on the (u, u_t) state ('kick-wave-kick'):
  - the LINEAR Klein-Gordon part u_tt = laplace(u) - m^2 u is propagated EXACTLY in
    Fourier with omega = sqrt(k^2 + m^2):
        u_hat(t) = u_hat cos(wt) + v_hat sin(wt)/w,
        v_hat(t) = -u_hat w sin(wt) + v_hat cos(wt)       (w-> dt limit at k=0,m=0);
  - the NONLINEAR remainder u_tt = -m^2 (sin u - u) is applied as a half velocity kick
    on each side. In the small-amplitude limit the kick vanishes -> exact Klein-Gordon.
np.fft.fftn/ifftn serve 1D and 2D. Starts from rest (u_t=0). Energy is conserved.

IC: band-limited field built deterministically from the exported ic_c* coefficients
(common/ic_encoding) on the coarsest grid, spectrally interpolated up -> identical
continuous IC per level. Field stored: u at fixed output time T.
"""
from __future__ import annotations

import numpy as np

from ..common import ic_encoding
from ..common.spectral import spectral_interp
from ..common.sampling import latin_hypercube

NDIMS_SUPPORTED = (1, 2)

# Fixed timestep, same at every resolution. (TBD-box.)
_DT = 5.0e-3


def _omega(res: int, domain_size: float, m: float, ndim: int) -> np.ndarray:
    k1 = 2 * np.pi * np.fft.fftfreq(res, d=domain_size / res)
    k_axes = np.meshgrid(*([k1] * ndim), indexing="ij")
    k2 = sum(kk ** 2 for kk in k_axes)
    return np.sqrt(k2 + m ** 2)


def _step_arrays(omega: np.ndarray, dt: float):
    cwt = np.cos(omega * dt)
    swt = np.sin(omega * dt)
    sinc = np.where(omega > 0, swt / np.where(omega > 0, omega, 1.0), dt)  # sin(wt)/w
    return cwt, swt, sinc


def _solve_with_velocity(u0: np.ndarray, m: float, domain_size: float,
                         output_time: float, dt: float = _DT):
    """Strang kick-wave-kick; return (u, v=u_t) at T. Starts from rest."""
    res = u0.shape[0]
    ndim = u0.ndim
    omega = _omega(res, domain_size, m, ndim)
    nsteps = int(np.ceil(output_time / dt))
    dt = output_time / nsteps
    cwt, swt, sinc = _step_arrays(omega, dt)
    u = u0.astype(np.float64).copy()
    v = np.zeros_like(u)
    for _ in range(nsteps):
        v = v - m ** 2 * (np.sin(u) - u) * (dt / 2.0)          # half kick
        uh = np.fft.fftn(u); vh = np.fft.fftn(v)               # full linear wave step
        uh_new = uh * cwt + vh * sinc
        vh_new = -uh * omega * swt + vh * cwt
        u = np.real(np.fft.ifftn(uh_new)); v = np.real(np.fft.ifftn(vh_new))
        v = v - m ** 2 * (np.sin(u) - u) * (dt / 2.0)          # half kick
    return u, v


def _solve(u0: np.ndarray, m: float, domain_size: float, output_time: float,
           dt: float = _DT) -> np.ndarray:
    """Return u at T (drops the velocity)."""
    return _solve_with_velocity(u0, m, domain_size, output_time, dt)[0]


def _energy(u: np.ndarray, v: np.ndarray, m: float, domain_size: float) -> float:
    """E = mean[ 1/2 v^2 + 1/2 |grad u|^2 + m^2 (1 - cos u) ] (per-cell, domain-normalized)."""
    res = u.shape[0]
    ndim = u.ndim
    k1 = 2 * np.pi * np.fft.fftfreq(res, d=domain_size / res)
    k_axes = np.meshgrid(*([k1] * ndim), indexing="ij")
    uh = np.fft.fftn(u)
    grad2 = np.zeros_like(u)
    for kk in k_axes:
        grad2 = grad2 + np.real(np.fft.ifftn(1j * kk * uh)) ** 2
    dens = 0.5 * v ** 2 + 0.5 * grad2 + m ** 2 * (1.0 - np.cos(u))
    return float(dens.mean())


def sample_configs(n: int, sampling_cfg: dict, ndim: int, seed: int) -> list[dict]:
    """Draw n sine-Gordon condition specs (Latin-hypercube over m / ic_amplitude)."""
    assert ndim in NDIMS_SUPPORTED, f"sine_gordon supports {NDIMS_SUPPORTED}, got {ndim}"
    draws = latin_hypercube(
        {"m": tuple(sampling_cfg["m_range"]),
         "ic_amplitude": tuple(sampling_cfg["ic_amplitude_range"]),
         **ic_encoding.ic_ranges(ndim)}, n, seed)
    return [{"m": draws["m"][i], "ic_amplitude": draws["ic_amplitude"][i],
             **{k: draws[k][i] for k in ic_encoding.ic_names(ndim)},
             "domain_size": sampling_cfg["domain_size"], "ndim": ndim,
             "seed": seed + i} for i in range(n)]


def generate_sample(spec: dict, resolutions: list[int], hf_res: int, output_time: float
                    ) -> tuple[dict[int, np.ndarray], np.ndarray, list[str]]:
    """Generate one sine-Gordon sample across the fidelity ladder (1D or 2D)."""
    ndim = int(spec["ndim"])
    res_min = min(resolutions)
    coeffs = ic_encoding.coeffs_from_spec(spec, ndim)
    ic_coarse = ic_encoding.build_ic(coeffs, res_min, spec["ic_amplitude"], ndim)
    fields = {
        res: _solve(spectral_interp(ic_coarse, res), spec["m"], spec["domain_size"],
                    output_time)
        for res in resolutions
    }
    cond = np.array([spec["m"], spec["ic_amplitude"], *coeffs], dtype=np.float64)
    names = ["m", "ic_amplitude"] + ic_encoding.ic_names(ndim)
    return fields, cond, names
