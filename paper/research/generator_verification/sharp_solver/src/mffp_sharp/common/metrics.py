"""Metric panel for sharp fields.

rel-L2 alone averages over the smooth bulk and HIDES blur in the thin sharp
region (the whole reason FNO can look good where it actually fails). So we keep
rel-L2 for comparison against the deck, and add metrics that *see* the sharp
region: L-inf, Wasserstein-1, interface/shock-position error, high-wavenumber
spectral-band error, conservation error, SSIM.

All metrics compare two fields already on the SAME (HF) grid. `pred` is the
field under test (e.g. an LF field upsampled to HF, or a model prediction);
`ref` is the HF ground truth.
"""
from __future__ import annotations

import numpy as np


def rel_l2(pred: np.ndarray, ref: np.ndarray) -> float:
    """Relative L2 error (the deck's metric)."""
    denom = np.linalg.norm(ref.ravel())
    return float(np.linalg.norm((pred - ref).ravel()) / (denom + 1e-30))


def linf(pred: np.ndarray, ref: np.ndarray) -> float:
    """Worst-point absolute error — spikes exactly where a sharp feature is blurred."""
    return float(np.max(np.abs(pred - ref)))


def spectral_band(pred: np.ndarray, ref: np.ndarray, low_frac: float = 0.5) -> float:
    """High-wavenumber error as a fraction of the field's TOTAL spectral energy.

    Zeroes the lowest `low_frac` of (radial) wavenumbers and measures the L2 error in
    the remaining high band, normalized by the *total* energy of the reference.
    Works for 1D (fft) and 2D (fft2) fields.
    """
    pred = np.asarray(pred)
    ref = np.asarray(ref)
    n = ref.shape[0]
    if ref.ndim == 1:
        kr = np.abs(np.fft.fftfreq(n))
        fft = np.fft.fft
    elif ref.ndim == 2:
        ky = np.fft.fftfreq(n)[:, None]
        kx = np.fft.fftfreq(n)[None, :]
        kr = np.sqrt(ky**2 + kx**2)
        fft = np.fft.fft2
    else:
        raise ValueError(f"unsupported ndim={ref.ndim}; expected 1 or 2")

    mask = kr >= (low_frac * kr.max())            # keep high band only
    Fp = fft(pred) * mask
    Fr = fft(ref) * mask
    num = np.linalg.norm((Fp - Fr).ravel())
    den = np.linalg.norm(fft(ref).ravel()) + 1e-30   # TOTAL energy, not high-band
    return float(num / den)


def conservation(pred: np.ndarray, ref: np.ndarray) -> float:
    """Relative error in the conserved integral (mean) of the field."""
    return float(abs(pred.mean() - ref.mean()) / (abs(ref.mean()) + 1e-30))


def interface_position(pred: np.ndarray, ref: np.ndarray, level: float | None = None) -> float:
    """Mean displacement of a level/threshold contour, in grid cells.

    Generic shock/interface-position proxy: threshold both fields at `level`
    (default: midpoint of the ref range) and measure the symmetric-difference
    area divided by the contour length — i.e. how far the front moved on average.
    PDE-specific position metrics (e.g. shock locus) can override this.
    """
    if level is None:
        level = 0.5 * (float(ref.max()) + float(ref.min()))
    mp = pred >= level
    mr = ref >= level
    sym_diff = np.logical_xor(mp, mr).sum()
    # contour length ~ perimeter of ref mask (count boundary cells)
    perim = _boundary_count(mr)
    return float(sym_diff / (perim + 1e-30))


def ssim(pred: np.ndarray, ref: np.ndarray) -> float:
    """Structural similarity (1 = identical). Returns 1 - SSIM as an error.

    SSIM is defined via 2D windows; for 1D (or other non-2D) fields we return NaN so
    the panel still runs. Uses scikit-image if available; otherwise a NaN sentinel.
    """
    ref = np.asarray(ref)
    pred = np.asarray(pred)
    if ref.ndim != 2:
        return float("nan")
    try:
        from skimage.metrics import structural_similarity as _ssim
    except Exception:
        return float("nan")
    data_range = float(ref.max() - ref.min()) or 1.0
    val = _ssim(ref, pred, data_range=data_range)
    return float(1.0 - val)


def wasserstein1(pred: np.ndarray, ref: np.ndarray) -> float:
    """1D Wasserstein-1 between the two fields' value distributions (histograms).

    NOTE: this is the cheap DISTRIBUTIONAL W1 over pixel intensities, not full 2D
    optimal transport over the spatial plane. It catches "the front is the wrong
    height/shape" but not "the front is in the wrong place" (interface_position
    covers location). True 2D OT via POT is a TODO if Nicholas wants it.
    """
    from scipy.stats import wasserstein_distance
    return float(wasserstein_distance(pred.ravel(), ref.ravel()))


def _boundary_count(mask: np.ndarray) -> int:
    """Count cells on the boundary of a boolean mask (4-neighbour in 2D, 2-neighbour in 1D)."""
    m = np.asarray(mask)
    if m.ndim == 1:
        diff = np.zeros_like(m)
        diff[:-1] |= m[:-1] ^ m[1:]
        return int(diff.sum())
    diff = np.zeros_like(m)
    diff[:-1, :] |= m[:-1, :] ^ m[1:, :]
    diff[:, :-1] |= m[:, :-1] ^ m[:, 1:]
    return int(diff.sum())


_PANEL = {
    "rel_l2": rel_l2,
    "linf": linf,
    "wasserstein1": wasserstein1,
    "interface_position": interface_position,
    "spectral_band": spectral_band,
    "conservation": conservation,
    "ssim": ssim,
}


def evaluate(pred: np.ndarray, ref: np.ndarray, names: list[str]) -> dict[str, float]:
    """Run the requested metrics; unknown names raise."""
    out = {}
    for name in names:
        if name not in _PANEL:
            raise KeyError(f"unknown metric {name!r}; have {sorted(_PANEL)}")
        out[name] = _PANEL[name](pred, ref)
    return out
