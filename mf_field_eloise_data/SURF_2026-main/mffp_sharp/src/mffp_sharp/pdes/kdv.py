"""Korteweg-de Vries (dispersive soliton trains) dataset generation.

KdV:  d u/dt + 6 u u_x + delta^2 u_xxx = 0.
A smooth IC disperses into a train of solitons; the high-wavenumber content comes
from the narrow soliton peaks (dispersion, not jumps). Tagged 'distinct (dispersion)'.
1D only (2D KP-II deferred).

SOLVER: integrating-factor RK4 (IF-RK4), the canonical Trefethen 'p27'/kursiv scheme.
In Fourier the linear part is purely dispersive,
  u_hat_t = L u_hat + g * (u^2)_hat,   L = i*delta^2*k^3,   g = -3 i k  (= -6 u u_x),
so the linear operator is integrated EXACTLY via E = exp(L*dt/2), E2 = exp(L*dt), and
the quadratic nonlinearity is advanced with 4th-order Runge-Kutta in the
integrating-factor variable, 2/3-rule de-aliased. (A first-order IF-Euler step is too
weakly stable here and blows up at realistic amplitudes; RK4 has a far larger stability
region.) Fresh real-space FFT each substep keeps the state Hermitian (stays real). KdV
conserves the integral of u, so the spatial mean (k=0 mode) is preserved exactly.

IC: band-limited field built deterministically from the exported ic_c* coefficients
(common/ic_encoding) on the coarsest grid, spectrally interpolated up -> identical
continuous IC per level. Field stored: u at fixed output time T.
"""
from __future__ import annotations

import numpy as np

from ..common import ic_encoding
from ..common.spectral import spectral_interp
from ..common.sampling import latin_hypercube

NDIMS_SUPPORTED = (1,)

# Fixed timestep, same at every resolution. IF-RK4 is stable at far larger dt than
# IF-Euler; this is conservative. (TBD-box.)
_DT = 1.0e-3


def _solve(u0: np.ndarray, delta: float, domain_size: float, output_time: float,
           dt: float = _DT) -> np.ndarray:
    """Integrating-factor RK4 Fourier KdV solve from u0 (1D); return u (real)."""
    res = u0.shape[0]
    k = 2 * np.pi * np.fft.fftfreq(res, d=domain_size / res)
    Lsym = 1j * delta ** 2 * k ** 3                        # linear dispersive operator
    fi = np.fft.fftfreq(res) * res
    mask = np.abs(fi) <= res / 3.0                         # 2/3-rule de-alias (quadratic)
    g = -3.0j * k                                          # nonlinear prefactor
    nsteps = int(np.ceil(output_time / dt))
    dt = output_time / nsteps
    E = np.exp(dt * Lsym / 2.0)
    E2 = np.exp(dt * Lsym)

    def Nl(vh):
        # pure function of its argument vh (the RK stages pass E*(v+..) etc., not the outer v)
        u = np.real(np.fft.ifft(vh))
        return g * (np.fft.fft(u ** 2) * mask)

    v = np.fft.fft(u0.astype(np.float64))
    for _ in range(nsteps):
        a = Nl(v)
        b = Nl(E * (v + 0.5 * dt * a))
        c = Nl(E * v + 0.5 * dt * b)
        d = Nl(E2 * v + dt * E * c)
        v = E2 * v + dt * (E2 * a + 2.0 * E * (b + c) + d) / 6.0
    return np.real(np.fft.ifft(v))


def sample_configs(n: int, sampling_cfg: dict, ndim: int, seed: int) -> list[dict]:
    """Draw n KdV condition specs (Latin-hypercube over delta / ic_amplitude)."""
    assert ndim in NDIMS_SUPPORTED, f"kdv supports {NDIMS_SUPPORTED}, got {ndim}"
    draws = latin_hypercube(
        {"delta": tuple(sampling_cfg["delta_range"]),
         "ic_amplitude": tuple(sampling_cfg["ic_amplitude_range"]),
         **ic_encoding.ic_ranges(1)}, n, seed)
    return [{"delta": draws["delta"][i], "ic_amplitude": draws["ic_amplitude"][i],
             **{k: draws[k][i] for k in ic_encoding.ic_names(1)},
             "domain_size": sampling_cfg["domain_size"], "ndim": ndim,
             "seed": seed + i} for i in range(n)]


def generate_sample(spec: dict, resolutions: list[int], hf_res: int, output_time: float
                    ) -> tuple[dict[int, np.ndarray], np.ndarray, list[str]]:
    """Generate one KdV sample across the fidelity ladder (1D)."""
    res_min = min(resolutions)
    coeffs = ic_encoding.coeffs_from_spec(spec, 1)
    ic_coarse = ic_encoding.build_ic(coeffs, res_min, spec["ic_amplitude"], 1)
    fields = {
        res: _solve(spectral_interp(ic_coarse, res), spec["delta"], spec["domain_size"],
                    output_time)
        for res in resolutions
    }
    cond = np.array([spec["delta"], spec["ic_amplitude"], *coeffs], dtype=np.float64)
    names = ["delta", "ic_amplitude"] + ic_encoding.ic_names(1)
    return fields, cond, names
