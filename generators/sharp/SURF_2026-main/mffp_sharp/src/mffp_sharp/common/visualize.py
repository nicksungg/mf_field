"""One-pager review figures for the researcher.

For a single sample, lays out: each fidelity's field (aligned to the HF grid),
the HF-minus-LF residual per LF level, the radially-averaged power spectrum
(does the sharp/high-frequency content survive?), and a table of LF-vs-HF panel
metrics. This is the visual the sample round produces for the approval gate.

matplotlib is imported lazily so the rest of the package stays importable on a
bare env.
"""
from __future__ import annotations

import numpy as np

from . import metrics as _metrics

# Pretty PDE names for the figure title.
_PDE_NAME = {"cahn_hilliard": "Cahn-Hilliard", "kuramoto_sivashinsky": "Kuramoto-Sivashinsky",
             "euler": "2D Euler Riemann"}

# Readable metric labels. The header shows a CURATED subset (spelled out); the full
# panel lives in sample_summary.json.
_METRIC_LABEL = {"rel_l2": "rel-L2", "linf": "L-inf", "wasserstein1": "Wass-1",
                 "interface_position": "feature-shift", "spectral_band": "high-k err",
                 "conservation": "mass-err", "ssim": "1-SSIM"}
_CURATED = ["rel_l2", "linf", "interface_position", "spectral_band"]

# Governing equation per PDE, as matplotlib mathtext (no LaTeX install needed).
_PDE_EQUATION = {
    "cahn_hilliard": r"$\partial_t c = M\,\nabla^2(c^3 - c - \varepsilon^2\,\nabla^2 c)$",
    "kuramoto_sivashinsky": r"$\partial_t u = -\nabla^2 u - \nabla^4 u - \frac{1}{2}|\nabla u|^2$",
    "euler": r"$\partial_t U + \nabla\cdot F(U) = 0$   (2D compressible Euler, Riemann IC)",
}

# Mathtext labels for condition-vector variable names (fall back to the raw name).
_COND_LABEL = {
    "eps": r"$\varepsilon$", "mobility": r"$M$", "mean_composition": r"$\bar c$",
    "L": r"$L$", "ic_amplitude": r"$A_0$", "gamma": r"$\gamma$",
    "pTL/pTR": r"$p_{TL}/p_{TR}$", "pBL/pTR": r"$p_{BL}/p_{TR}$", "pBR/pTR": r"$p_{BR}/p_{TR}$",
    "rTL/rTR": r"$\rho_{TL}/\rho_{TR}$", "rBL/rTR": r"$\rho_{BL}/\rho_{TR}$",
    "rBR/rTR": r"$\rho_{BR}/\rho_{TR}$",
}


def radial_spectrum(field: np.ndarray) -> np.ndarray:
    """Power spectrum vs wavenumber.

    1D: |rfft|**2, indexed by integer wavenumber 0..n//2.
    2D: azimuthally-averaged PSD vs radial wavenumber (unchanged).
    """
    field = np.asarray(field)
    if field.ndim == 1:
        return np.abs(np.fft.rfft(field)) ** 2
    F = np.fft.fftshift(np.fft.fft2(field))
    psd = np.abs(F) ** 2
    n = field.shape[0]
    cy, cx = n // 2, n // 2
    y, x = np.indices((n, n))
    r = np.hypot(x - cx, y - cy).astype(int)
    tbin = np.bincount(r.ravel(), psd.ravel())
    counts = np.bincount(r.ravel())
    return tbin / np.maximum(counts, 1)


def _header_lines(pde, sample_idx, resolutions, hf_res, aligned, metric_names,
                  condition, condition_names) -> list[str]:
    """Build the suptitle lines shared by the 1D and 2D one-pagers."""
    res_min = min(resolutions)
    lf_res = [r for r in resolutions if r != hf_res]
    pretty = _PDE_NAME.get(pde, pde)
    lines = [f"{pretty}  —  sample {sample_idx}"
             f"    (LF / IF / HF = low / intermediate / high fidelity)"]
    eq = _PDE_EQUATION.get(pde)
    if eq:
        lines.append(f"PDE:  {eq}")
    if condition is not None and condition_names is not None and len(condition_names):
        pairs = [f"{_COND_LABEL.get(n, n)}={float(v):.3g}"
                 for n, v in zip(condition_names, np.ravel(condition))]
        for c in range(0, len(pairs), 4):
            prefix = "condition vector:  " if c == 0 else " " * 19
            lines.append(prefix + "    ".join(pairs[c:c + 4]))
    if lf_res:
        m = _metrics.evaluate(aligned[res_min], aligned[hf_res], metric_names)
        shown = [k for k in _CURATED if k in m]
        errline = "    ".join(f"{_METRIC_LABEL.get(k, k)}={m[k]:.3g}" for k in shown)
        lines.append(f"coarsest LF ({res_min}^2) vs HF ({hf_res}^2) error:")
        lines.append(errline)
        lines.append(f"(full {len(m)}-metric panel in sample_summary.json)")
    return lines


def one_pager(bundle: dict, resolutions: list[int], hf_res: int, metric_names: list[str],
              pde: str, sample_idx: int, out_path: str,
              condition=None, condition_names=None) -> None:
    """Write a one-pager PNG for a single sample bundle.

    Dispatches on field dimensionality: 1D fields get line-plot panels, 2D fields
    get the heatmap layout. Both show the LF/IF/HF fields, the HF-LF residual, the
    radial/1D power spectrum, and a curated LF-vs-HF metric line in the header.
    """
    hf = bundle["aligned"][hf_res]
    if np.asarray(hf).ndim == 1:
        _one_pager_1d(bundle, resolutions, hf_res, metric_names, pde, sample_idx,
                      out_path, condition, condition_names)
    else:
        _one_pager_2d(bundle, resolutions, hf_res, metric_names, pde, sample_idx,
                      out_path, condition, condition_names)


def _one_pager_1d(bundle, resolutions, hf_res, metric_names, pde, sample_idx,
                  out_path, condition, condition_names) -> None:
    """1D one-pager: overlaid fields, residual lines, and the power spectrum."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    aligned = bundle["aligned"]
    raw = bundle["raw"]
    hf = aligned[hf_res]
    res_min = min(resolutions)
    lf_res = [r for r in resolutions if r != hf_res]

    fig, axes = plt.subplots(1, 3, figsize=(16.0, 5.0), constrained_layout=True)

    # Panel 0: native-resolution fields, each on its own cell-center x-axis.
    for res in resolutions:
        xr = (np.arange(res) + 0.5) / res
        tag = "HF" if res == hf_res else "LF" if res == res_min else "IF"
        axes[0].plot(xr, raw[res], marker="o", ms=3, label=f"{tag} ({res})")
    axes[0].set_title("solution field (native resolution)", fontsize=10)
    axes[0].set_xlabel("x (unit domain)")
    axes[0].set_ylabel("u")
    axes[0].legend(fontsize=8)

    # Panel 1: HF - LF residual per LF level, on the shared HF grid.
    xh = (np.arange(hf_res) + 0.5) / hf_res
    for res in lf_res:
        lftag = "LF" if res == res_min else "IF"
        axes[1].plot(xh, hf - aligned[res], label=f"HF - {lftag} ({res})")
    axes[1].axhline(0.0, color="gray", lw=0.8, ls=":")
    axes[1].set_title("error vs HF (on shared grid)", fontsize=10)
    axes[1].set_xlabel("x (unit domain)")
    axes[1].set_ylabel("error")
    axes[1].legend(fontsize=8)

    # Panel 2: power spectrum (log-log); annotate the HF power-law slope on k in [5,40].
    for res in resolutions:
        sp = radial_spectrum(aligned[res])
        kk = np.arange(1, len(sp))
        axes[2].loglog(kk, sp[1:], label=f"{res}")
    axes[2].axvline(res_min // 2, color="gray", ls=":", lw=1)
    hf_sp = radial_spectrum(hf)
    kk2 = np.arange(1, len(hf_sp))
    band = (kk2 >= 5) & (kk2 <= min(40, len(hf_sp) - 1)) & (hf_sp[1:] > 0)
    if band.sum() >= 3:
        slope = float(np.polyfit(np.log(kk2[band]), np.log(hf_sp[1:][band]), 1)[0])
        kref = np.array([5.0, float(min(40, len(hf_sp) - 1))])
        axes[2].loglog(kref, hf_sp[5] * (kref / 5) ** slope, "k--", lw=1.5, alpha=0.85,
                       label=f"HF decay slope ~ {slope:.1f}")
    axes[2].set_title("power spectrum (log-log)", fontsize=10)
    axes[2].set_xlabel("wavenumber (log)  ->  finer scales")
    axes[2].set_ylabel("power (log)")
    axes[2].legend(fontsize=8, title="grid (solid) / HF fit (dashed)")

    lines = _header_lines(pde, sample_idx, resolutions, hf_res, aligned,
                          metric_names, condition, condition_names)
    fig.suptitle("\n".join(lines), fontsize=9)
    fig.savefig(out_path, dpi=110)
    plt.close(fig)


def _one_pager_2d(bundle: dict, resolutions: list[int], hf_res: int, metric_names: list[str],
                  pde: str, sample_idx: int, out_path: str,
                  condition=None, condition_names=None) -> None:
    """Write a one-pager PNG for a single sample bundle (from ladder.assemble_sample).

    If `condition`/`condition_names` are given, the governing PDE and this sample's
    condition-vector values are shown in the header.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    aligned = bundle["aligned"]
    raw = bundle["raw"]
    hf = aligned[hf_res]
    lf_res = [r for r in resolutions if r != hf_res]
    ncols = len(resolutions)

    fig, axes = plt.subplots(2, ncols, figsize=(4 * ncols, 10.0), constrained_layout=True)
    if ncols == 1:
        axes = axes.reshape(2, 1)

    vmin, vmax = float(hf.min()), float(hf.max())
    res_min = min(resolutions)

    # Row 0: native-resolution fields (nearest interpolation -> LF is genuinely blocky,
    # HF is fine). Makes the resolution difference visible at a glance; the benchmark
    # itself uses the HF-aligned versions (residual row).
    for j, res in enumerate(resolutions):
        ax = axes[0, j]
        im = ax.imshow(raw[res], origin="lower", vmin=vmin, vmax=vmax, cmap="viridis",
                       interpolation="nearest")
        tag = "HF" if res == hf_res else "LF" if res == res_min else "IF"
        ax.set_title(f"{tag} ({res}x{res} grid)", fontsize=10)
        ax.set_xticks([]); ax.set_yticks([])
        fig.colorbar(im, ax=ax, fraction=0.046)
    axes[0, 0].set_ylabel("solution field\n(shown at native resolution)", fontsize=9)

    # Row 1: HF - LF residuals per LF level, then the radial spectrum.
    for j in range(ncols):
        ax = axes[1, j]
        if j < len(lf_res):
            res = lf_res[j]
            resid = hf - aligned[res]
            a = float(np.abs(resid).max()) or 1.0
            im = ax.imshow(resid, origin="lower", vmin=-a, vmax=a, cmap="coolwarm")
            lftag = "LF" if res == res_min else "IF"
            ax.set_title(f"Error between {lftag} ({res}x{res} grid)\n"
                         f"and HF ({hf_res}x{hf_res} grid)", fontsize=9)
            ax.set_xticks([]); ax.set_yticks([])
            if j == 0:
                ax.set_ylabel("error field\n(on shared 128 grid)", fontsize=9)
            fig.colorbar(im, ax=ax, fraction=0.046)
        else:
            # log-log: a power-law decay (e.g. a shock's spectrum) is a STRAIGHT line
            # whose slope is the decay exponent, so the decay rate is directly readable.
            for res in resolutions:
                sp = radial_spectrum(aligned[res])
                kk = np.arange(1, len(sp))
                ax.loglog(kk, sp[1:], label=f"{res}x{res}")
            ax.axvline(res_min // 2, color="gray", ls=":", lw=1)
            ax.text(res_min // 2, sp[1:].max(), f"{res_min}^2 Nyquist",
                    fontsize=7, va="top", color="gray")
            # Fit + DRAW the HF curve's decay slope (the field's frequency-content measure):
            # steeper (more negative) = smoother; shallower = more high-frequency content.
            hf_sp = radial_spectrum(hf)
            kk2 = np.arange(1, len(hf_sp))
            band = (kk2 >= 5) & (kk2 <= min(40, len(hf_sp) - 1)) & (hf_sp[1:] > 0)
            if band.sum() >= 3:
                slope = float(np.polyfit(np.log(kk2[band]), np.log(hf_sp[1:][band]), 1)[0])
                k0 = 5
                kref = np.array([5.0, float(min(40, len(hf_sp) - 1))])
                ax.loglog(kref, hf_sp[k0] * (kref / k0) ** slope, "k--", lw=1.5, alpha=0.85,
                          label=f"HF decay slope ~ {slope:.1f}")
            ax.set_title("radial power spectrum (log-log)", fontsize=10)
            ax.set_xlabel("radial wavenumber (log)  ->  finer scales")
            ax.set_ylabel("power (log)")
            ax.legend(fontsize=8, title="grid (solid) / HF fit (dashed)")

    # Header: shared suptitle (pretty name + ladder + curated LF-vs-HF panel).
    lines = _header_lines(pde, sample_idx, resolutions, hf_res, aligned,
                          metric_names, condition, condition_names)
    fig.suptitle("\n".join(lines), fontsize=9)

    fig.savefig(out_path, dpi=110)
    plt.close(fig)
