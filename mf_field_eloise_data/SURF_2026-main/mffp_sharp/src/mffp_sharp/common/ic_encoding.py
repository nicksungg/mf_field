"""Band-limited initial-condition encoding (the 2026-06-28 learnability fix, in the package).

Stochastic-IC PDEs must not draw an initial condition the condition vector cannot
describe: a fresh random IC per sample whose seed is never exported makes
`condition -> HF` a stochastic map, so a deterministic model can at best reach the
conditional mean (ADR r2-0003; the rel-L2 > 1 bug of 2026-06-28).
The fix: the IC is built deterministically from 16 low-Fourier-mode coefficients,
and THOSE coefficients are drawn in `sample_configs`'s Latin-hypercube design and
exported in `cond`/`param_names` as `ic_c0..ic_c15`.

The construction is verbatim `mf_field_eloise_data/generate_learnable.py` (already
validated on the 9 regenerated sharp variants; the existing cahn_hilliard
benchmark's reconstruction certificate pins it at machine precision) — keep it
byte-identical to that math.
"""
from __future__ import annotations

import numpy as np

K1D = 8          # 1D: modes 1..8 -> 16 coeffs
M2D = 3          # 2D: (kx,ky) in 0..2 minus DC -> 8 modes -> 16 coeffs


def n_coeffs(ndim: int) -> int:
    """Number of exported IC coefficients (16 for both supported ndims)."""
    return 2 * K1D if ndim == 1 else 2 * (M2D * M2D - 1)


def ic_names(ndim: int) -> list[str]:
    """Condition-vector names for the IC coefficients, in export order."""
    return [f"ic_c{j}" for j in range(n_coeffs(ndim))]


def ic_ranges(ndim: int) -> dict[str, tuple[float, float]]:
    """Latin-hypercube ranges for the IC coefficients (splat into the design)."""
    return {name: (-1.0, 1.0) for name in ic_names(ndim)}


def coeffs_from_spec(spec: dict, ndim: int) -> np.ndarray:
    """Collect the IC coefficients back out of a spec dict, in export order."""
    return np.array([spec[name] for name in ic_names(ndim)], dtype=np.float64)


def ic_1d(coeffs: np.ndarray, res: int, scale: float) -> np.ndarray:
    K = len(coeffs) // 2
    Ch = np.zeros(res, complex)
    for k in range(1, K + 1):
        Ch[k] = coeffs[k - 1] + 1j * coeffs[K + k - 1]
        Ch[res - k] = np.conj(Ch[k])
    u = np.fft.ifft(Ch).real
    return u / (np.max(np.abs(u)) + 1e-12) * scale


def ic_2d(coeffs: np.ndarray, res: int, scale: float) -> np.ndarray:
    xs = 2 * np.pi * np.arange(res) / res
    X, Y = np.meshgrid(xs, xs, indexing="ij")
    modes = [(a, b) for a in range(M2D) for b in range(M2D) if not (a == 0 and b == 0)]
    f = np.zeros((res, res))
    idx = 0
    for (kx, ky) in modes:
        f += coeffs[idx] * np.cos(kx * X + ky * Y) + coeffs[idx + 1] * np.sin(kx * X + ky * Y)
        idx += 2
    return f / (np.max(np.abs(f)) + 1e-12) * scale


def build_ic(coeffs: np.ndarray, res: int, scale: float, ndim: int) -> np.ndarray:
    """Dispatch on dimensionality (mirrors generate_learnable.build_ic)."""
    return ic_1d(coeffs, res, scale) if ndim == 1 else ic_2d(coeffs, res, scale)
