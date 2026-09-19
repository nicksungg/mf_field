"""Phase-field crystal (PFC; periodic sharp lattice, conserved, stiff 6th order).

PFC:  d psi/dt = laplace[ (r + (1 + laplace)^2) psi + psi^3 ].
A conserved dynamics whose ground state is a crystalline lattice with characteristic
wavenumber |k|=1 -> a spectral PEAK. 6th-order and stiff. Distinct mechanism: periodic
sharp lattice. 2D. Field stored: psi at fixed output time T.

SOLVER: semi-implicit Fourier. In Fourier the linear symbol is
  L(k) = -k^2 (r + (1 - k^2)^2),
treated IMPLICITLY (denom = 1/dt - L), with the cubic term laplace(psi^3) = -k^2 psi3_hat
explicit and 2/3-rule de-aliased; fresh FFT each step. The leading laplacian leaves the
k=0 mode untouched, so the spatial mean (mass) is conserved exactly. SAME dt at every
resolution.

IC: mean_density + small band-limited noise on the coarsest grid, spectrally interpolated
up -> identical continuous IC per level. (Continuous k^2; PFC patterns are smooth/resolved.)
"""
from __future__ import annotations

import numpy as np

from ..common.spectral import spectral_interp
from ..common.sampling import latin_hypercube

NDIMS_SUPPORTED = (2,)

_DT = 0.1  # (TBD-box.)


def _solve(psi0: np.ndarray, r: float, domain_size: float, output_time: float,
           dt: float = _DT) -> np.ndarray:
    """Semi-implicit Fourier PFC solve from psi0 (2D); return psi."""
    res = psi0.shape[0]
    k1 = 2 * np.pi * np.fft.fftfreq(res, d=domain_size / res)
    KX, KY = np.meshgrid(k1, k1, indexing="ij")
    k2 = KX ** 2 + KY ** 2
    Lsym = -k2 * (r + (1.0 - k2) ** 2)                 # linear operator symbol
    fi = np.fft.fftfreq(res) * res
    keep1 = np.abs(fi) <= res / 3.0
    mask = np.logical_and.reduce(np.meshgrid(keep1, keep1, indexing="ij"))
    nsteps = int(np.ceil(output_time / dt))
    dt = output_time / nsteps
    denom = 1.0 / dt - Lsym                             # implicit linear
    psi = psi0.astype(np.float64).copy()
    for _ in range(nsteps):
        ph = np.fft.fft2(psi)
        nlh = -k2 * (np.fft.fft2(psi ** 3) * mask)     # laplace(psi^3) = -k^2 psi3_hat
        ph_new = (ph * (1.0 / dt) + nlh) / denom
        psi = np.real(np.fft.ifft2(ph_new))
    return psi


def sample_configs(n: int, sampling_cfg: dict, ndim: int, seed: int) -> list[dict]:
    """Draw n PFC condition specs (Latin-hypercube over r / mean_density)."""
    assert ndim in NDIMS_SUPPORTED, f"phase_field_crystal supports {NDIMS_SUPPORTED}, got {ndim}"
    draws = latin_hypercube(
        {"r": tuple(sampling_cfg["r_range"]),
         "mean_density": tuple(sampling_cfg["mean_density_range"])}, n, seed)
    return [{"r": draws["r"][i], "mean_density": draws["mean_density"][i],
             "ic_amplitude": sampling_cfg["ic_amplitude"],
             "domain_size": sampling_cfg["domain_size"], "ndim": ndim,
             "seed": seed + i} for i in range(n)]


def generate_sample(spec: dict, resolutions: list[int], hf_res: int, output_time: float
                    ) -> tuple[dict[int, np.ndarray], np.ndarray, list[str]]:
    """Generate one PFC sample across the fidelity ladder (2D)."""
    res_min = min(resolutions)
    rng = np.random.default_rng(spec["seed"])
    ic_coarse = spec["mean_density"] + spec["ic_amplitude"] * (
        2 * rng.random((res_min, res_min)) - 1)
    fields = {
        res: _solve(spectral_interp(ic_coarse, res), spec["r"], spec["domain_size"],
                    output_time)
        for res in resolutions
    }
    cond = np.array([spec["r"], spec["mean_density"]], dtype=np.float64)
    names = ["r", "mean_density"]
    return fields, cond, names
