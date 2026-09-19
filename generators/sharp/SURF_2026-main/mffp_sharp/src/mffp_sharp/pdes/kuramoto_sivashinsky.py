"""2D Kuramoto-Sivashinsky (smooth CONTROL) dataset generation.

KS:  d u/dt = -laplace(u) - laplace(laplace(u)) - (1/2)|grad u|^2
Spatiotemporally chaotic but SPECTRALLY SMOOTH -- no shocks, energy decays fast
in wavenumber. This is the control: FNO should do fine here, and LF (coarse grid)
should stay CLOSE to HF (small LF-HF gap by design). If LF and HF differ a lot,
the control isn't behaving as a control -> flag it.

SOLVER (validated on box 2026-06-15). py-pde's explicit integrator blows up on the
stiff 4th-order operator. We use a custom semi-implicit Fourier scheme (same family
as the Cahn-Hilliard fix):
  - linear part u_t = (k^2 - k^4) u: the stiff biharmonic (-k^4, damping) is treated
    IMPLICITLY, the mild -laplace(u) (+k^2) explicitly;
  - the nonlinear -1/2|grad u|^2 is explicit, 2/3-rule de-aliased (quadratic);
  - EXACT spectral derivatives (the control field is smooth & well-resolved by design,
    so no Gibbs issue -- this is where spectral accuracy is appropriate);
  - the field is re-FFT'd from the real state each step (Hermitian-safe; carrying the
    complex state drifts non-Hermitian and the unstable k<1 modes amplify the drift).
KS is far less stiff than CH (linear growth lambda_max=0.25), so dt~0.05 is ample.

MEAN DRIFT: this KS form has d/dt <u> = -1/2 <|grad u|^2> < 0, so the spatial mean
runs off to large negative values while only the FLUCTUATION is statistically steady.
We store the zero-mean fluctuation u - <u> (the physically meaningful, T-determined
field); the drift is a deterministic gauge offset that would otherwise dominate the
rel-L2 denominator and mask the real LF-HF differences. (Flag for the researcher.)

IC: band-limited random field generated on the coarsest grid from the sample seed and
spectrally interpolated up -> every ladder level solves the IDENTICAL continuous IC.

Field stored: u - <u> at fixed output time T (past the initial transient).
"""
from __future__ import annotations

import numpy as np

from ..common.spectral import spectral_interp
from ..common.sampling import latin_hypercube

NDIMS_SUPPORTED = (1, 2)

# Fixed timestep, same at every resolution (consistency: only the grid changes). (TBD.)
_DT = 0.05


def _solve(u0: np.ndarray, L: float, output_time: float, dt: float = _DT) -> np.ndarray:
    """Semi-implicit Fourier KS solve from initial field u0 (1D or 2D); return u - <u>."""
    res = u0.shape[0]
    ndim = u0.ndim
    k1 = 2 * np.pi * np.fft.fftfreq(res, d=L / res)
    ks_axes = np.meshgrid(*([k1] * ndim), indexing="ij")   # per-axis wavenumber arrays
    k2 = sum(kk ** 2 for kk in ks_axes)
    k4 = k2 ** 2
    fi = np.fft.fftfreq(res) * res
    keep1 = np.abs(fi) <= res / 3.0                         # 2/3-rule de-alias (quadratic)
    mask = np.logical_and.reduce(np.meshgrid(*([keep1] * ndim), indexing="ij"))
    nsteps = int(np.ceil(output_time / dt))
    dt = output_time / nsteps
    denom = 1.0 / dt + k4                                   # implicit biharmonic (-k^4 damping)
    u = u0.astype(np.float64).copy()
    for _ in range(nsteps):
        uh = np.fft.fftn(u)                                # FRESH each step -> stays Hermitian
        grad2 = sum(np.real(np.fft.ifftn(1j * kk * uh)) ** 2 for kk in ks_axes)
        nl = -0.5 * grad2
        nlh = np.fft.fftn(nl) * mask
        uh_new = (uh * (1.0 / dt + k2) + nlh) / denom
        u = np.real(np.fft.ifftn(uh_new))
    return u - u.mean()                                     # store zero-mean fluctuation


def sample_configs(n: int, sampling_cfg: dict, ndim: int, seed: int) -> list[dict]:
    """Draw n KS condition specs (Latin-hypercube over L / ic_amplitude)."""
    assert ndim in NDIMS_SUPPORTED, f"kuramoto_sivashinsky supports {NDIMS_SUPPORTED}, got {ndim}"
    draws = latin_hypercube(
        {"L": tuple(sampling_cfg["L_range"]),
         "ic_amplitude": tuple(sampling_cfg["ic_amplitude_range"])}, n, seed)
    return [{"L": draws["L"][i], "ic_amplitude": draws["ic_amplitude"][i],
             "ndim": ndim, "seed": seed + i} for i in range(n)]


def generate_sample(spec: dict, resolutions: list[int], hf_res: int, output_time: float
                    ) -> tuple[dict[int, np.ndarray], np.ndarray, list[str]]:
    """Generate one KS sample across the fidelity ladder.

    `spec` keys: L, ic_amplitude, seed. Same L and same (band-limited) IC at every res.
    """
    res_min = min(resolutions)
    ndim = int(spec.get("ndim", 2))
    rng = np.random.default_rng(spec["seed"])
    ic_coarse = spec["ic_amplitude"] * (2 * rng.random((res_min,) * ndim) - 1)
    fields = {
        res: _solve(spectral_interp(ic_coarse, res), spec["L"], output_time)
        for res in resolutions
    }
    cond = np.array([spec["L"], spec["ic_amplitude"]], dtype=np.float64)
    names = ["L", "ic_amplitude"]
    return fields, cond, names
