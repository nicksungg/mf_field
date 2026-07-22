"""Figures for MF_FNO_CNN_Hybrid_Report.md.

fig_hybrid1_architecture.png   — the incumbent single-FNO transfer schedule
                                 (mf_fno_transfer_film, Elo 1820, rank #1/30) vs the
                                 proposed two-stage FNO(cond->LF) + FiLM-CNN(LF->HF).
fig_hybrid2_spectral_split.png — the frequency division of labour, computed (not sketched)
                                 from three analytic 1-D prototypes so the k^-1 shock tail
                                 is a fitted slope rather than an assertion.

Run:  python make_fig_hybrid.py
Everything is analytic, so there is no expensive generation step to cache: the whole
script re-renders in ~2 s and layout tweaks are cheap.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT1 = "fig_hybrid1_architecture.png"
OUT2 = "fig_hybrid2_spectral_split.png"

# Where the proposed FNO cutoff sits, and the band handed to the CNN.
K_CUT = 12
K_BAND = (8, 16)

KEY = ("LF / HF = low / high fidelity  ·  FNO = Fourier Neural Operator  ·  "
       "FiLM = feature-wise linear modulation  ·  $K$ = retained Fourier modes per dimension")

C_IN, C_FNO, C_LF, C_CNN, C_OUT = "#dfe6ee", "#bcd7f0", "#ffe3b0", "#c9e8c9", "#eccfe0"


# ============================================================================
# Figure 1 — architecture comparison
# ============================================================================
def box(ax, cx, cy, w, h, text, fc, fs=12):
    ax.add_patch(FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle="round,pad=0.6,rounding_size=1.6",
        facecolor=fc, edgecolor="#2f3b47", linewidth=1.4, zorder=2,
    ))
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fs, zorder=3, linespacing=1.35)


def arrow(ax, x0, x1, y):
    ax.add_patch(FancyArrowPatch(
        (x0, y), (x1, y), arrowstyle="-|>", mutation_scale=17,
        linewidth=1.5, color="#2f3b47", zorder=2,
    ))


fig = plt.figure(figsize=(13.2, 6.0), constrained_layout=True)
ax = fig.add_subplot(111)
ax.set_xlim(0, 100)
ax.set_ylim(-2, 100)
ax.axis("off")

# ---- top row: incumbent -----------------------------------------------------
Y1 = 76
ax.text(1, 95, "INCUMBENT  ·  mf_fno_transfer_film  ·  Elo 1820, rank #1 of 30",
        fontsize=12, fontweight="bold", color="#3b4c5e")
box(ax, 14, Y1, 22, 15, "condition vector\n$X \\in \\mathbb{R}^{d}$", C_IN)
box(ax, 48, Y1, 26, 15, "single FNO\nmodes $\\leq 12$", C_FNO)
box(ax, 83, Y1, 22, 15, "HF field\n$\\hat{Y}_{HF}$", C_OUT)
arrow(ax, 25.5, 34.5, Y1)
arrow(ax, 61.5, 71.5, Y1)
ax.text(48, Y1 - 11.5,
        "one forward pass · pretrain on $(X, Y_{LF})$, then fine-tune the same weights on $(X, Y_{HF})$\n"
        "the LF $\\it{field}$ is a pretraining target only — it is never an input, and is discarded after pretraining",
        ha="center", va="top", fontsize=10.4, color="#5a6b7d", linespacing=1.55)

# ---- bottom row: proposal ---------------------------------------------------
Y2 = 36
ax.text(1, 48, "PROPOSED  ·  two-stage spectral → local hybrid",
        fontsize=12, fontweight="bold", color="#3b4c5e")
box(ax, 8.5, Y2, 15, 15, "condition\nvector $X$", C_IN, fs=11)
box(ax, 29.5, Y2, 20, 15, "STAGE 1\nFNO$_{\\theta}$\nmodes $\\leq K$", C_FNO, fs=11)
box(ax, 50.5, Y2, 15, 15, "$\\hat{Y}_{LF}$\n(explicit)", C_LF, fs=11)
box(ax, 71.5, Y2, 20, 15, "STAGE 2\nCNN$_{\\phi}$\n+ FiLM$(X)$", C_CNN, fs=11)
box(ax, 90.5, Y2, 11, 15, "$\\hat{Y}_{HF}$", C_OUT, fs=11)
arrow(ax, 16.2, 19.3, Y2)
arrow(ax, 39.7, 42.8, Y2)
arrow(ax, 58.2, 61.3, Y2)
arrow(ax, 81.7, 84.8, Y2)

# FiLM side-channel, routed orthogonally between the boxes and the training captions
# so the dashed line crosses no text; its label masks the line centre.
Y_FILM, G = 20.0, "#4b8b4b"
ax.plot([8.5, 8.5], [Y2 - 7.5, Y_FILM], color=G, lw=1.3, ls=(0, (4, 3)), zorder=1)
ax.plot([8.5, 71.5], [Y_FILM, Y_FILM], color=G, lw=1.3, ls=(0, (4, 3)), zorder=1)
ax.add_patch(FancyArrowPatch(
    (71.5, Y_FILM), (71.5, Y2 - 7.5), arrowstyle="-|>", mutation_scale=15,
    linewidth=1.3, color=G, linestyle=(0, (4, 3)), zorder=1,
))
ax.text(40, Y_FILM, "FiLM: $X$ modulates every refiner block,  $h \\leftarrow \\gamma(X)\\odot h + \\beta(X)$",
        ha="center", va="center", fontsize=10.4, color="#3f7a3f", style="italic", zorder=3,
        bbox=dict(facecolor="white", edgecolor="none", pad=2.5))

ax.text(29.5, 12.0, "trained on abundant LF data\n(100 samples for ifc_heat)", ha="center", va="top",
        fontsize=10.2, color="#5a6b7d", linespacing=1.45)
ax.text(71.5, 12.0, "trained on scarce HF data\n(5 samples for ifc_heat)", ha="center", va="top",
        fontsize=10.2, color="#5a6b7d", linespacing=1.45)
ax.text(50, 1.0,
        "Both fidelities are resampled onto one working grid before training, so stage 2 is sharpening — not pixel-count super-resolution.",
        ha="center", fontsize=9.2, color="#8894a2", style="italic")

fig.suptitle(
    "Figure 1 — The incumbent puts multi-fidelity in the training schedule; the proposal puts it in the architecture\n"
    + KEY,
    fontsize=13, fontweight="bold", linespacing=1.6,
)
fig.savefig(OUT1, dpi=185, bbox_inches="tight", facecolor="white")
print(f"wrote {OUT1}")


# ============================================================================
# Figure 2 — the frequency division of labour
# ============================================================================
N = 2048
x = np.linspace(0.0, 1.0, N, endpoint=False)


def spectrum(f):
    """Normalised one-sided amplitude spectrum, k = 1..N/2 (DC dropped)."""
    c = np.abs(np.fft.rfft(f))[1:]
    return c / c.max()


# Smooth Gaussian bump: spectrum decays exponentially, exp(-k^2 sigma^2 / 2).
smooth = np.exp(-((x - 0.5) ** 2) / (2 * 0.05 ** 2))

# Cahn-Hilliard-like interface of width eps: exponential decay, but only past k ~ 1/eps.
eps = 0.01
interface = np.tanh((x - 0.35) / eps) - np.tanh((x - 0.70) / eps)

# Riemann shock: a true jump discontinuity -> |c_k| decays only as k^-1.
# Placed off-centre so the periodic spectrum has no exactly-zero harmonics.
shock = np.where(x < 0.62, 1.0, 0.35)

k = np.arange(1, N // 2 + 1)
S_smooth, S_iface, S_shock = spectrum(smooth), spectrum(interface), spectrum(shock)


def envelope(S, kk, n_bins=44):
    """Upper envelope in log-spaced k bins — the decay a truncation error actually sees.

    A periodic jump's spectrum has deep interference nulls between lobes; fitting raw
    samples would measure those nulls rather than the k^-1 decay of the lobe peaks.
    """
    edges = np.unique(np.round(np.logspace(0, np.log10(kk[-1]), n_bins)).astype(int))
    kc, sc = [], []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (kk >= lo) & (kk < hi)
        if m.any() and S[m].max() > 0:
            kc.append(np.sqrt(lo * hi))
            sc.append(S[m].max())
    return np.array(kc), np.array(sc)


k_env, S_env = envelope(S_shock, k)
sel = (k_env >= 20) & (k_env <= 400)
slope, intercept = np.polyfit(np.log10(k_env[sel]), np.log10(S_env[sel]), 1)

fig2 = plt.figure(figsize=(11.4, 7.8), constrained_layout=True)
gs2 = fig2.add_gridspec(2, 1, height_ratios=[1.0, 0.055])
axb = fig2.add_subplot(gs2[0, 0])

axb.loglog(k, S_smooth, color="#1f77b4", lw=2.2,
           label="smooth bump — exponential decay (most of the 42-dataset suite)")
axb.loglog(k, S_iface, color="#e08a1e", lw=1.4, alpha=0.8,
           label=f"sharp interface, $\\varepsilon={eps}$ — exponential only past $k\\sim1/\\varepsilon$")
axb.loglog(k, S_shock, color="#c0392b", lw=0.6, alpha=0.22)
axb.loglog(k_env, S_env, color="#c0392b", lw=2.2,
           label="jump discontinuity (shock) — lobe envelope")
k_fit = np.array([20.0, 400.0])
axb.loglog(k_fit, 10 ** (intercept + slope * np.log10(k_fit)),
           color="#7b241c", lw=3.0, ls="--",
           label=f"fitted shock tail: $|c_k| \\propto k^{{{slope:.2f}}}$")

axb.axvspan(K_CUT, k[-1], color="#c9e8c9", alpha=0.42, zorder=0)
axb.axvspan(*K_BAND, color="#bcd7f0", alpha=0.5, zorder=0)
axb.axvline(K_CUT, color="#2f3b47", lw=1.6)

axb.set_xlim(1, k[-1])
axb.set_ylim(1e-6, 12.0)
axb.set_xlabel("wavenumber $k$", fontsize=13)
axb.set_ylabel("normalised spectral amplitude   $|c_k| / \\max_k |c_k|$", fontsize=13)
axb.tick_params(labelsize=11)
axb.grid(True, which="both", alpha=0.22)
axb.legend(loc="lower left", fontsize=11, framealpha=0.95)

axb.text(3.2, 4.0, "STAGE 1 · FNO\nkeeps $k \\leq K$", ha="center", va="center",
         fontsize=12.5, color="#1f4e79", fontweight="bold", linespacing=1.4)
axb.text(np.sqrt(K_CUT * k[-1]), 4.0,
         "STAGE 2 (CNN) must supply this entire band —\n"
         "structurally unreachable for the FNO at any training budget",
         ha="center", va="center", fontsize=12.5, color="#2f6b2f", fontweight="bold",
         linespacing=1.45)
axb.annotate("proposed crossover $K\\in[8,16]$", xy=(K_CUT, 1.2e-4), xytext=(31, 3.0e-5),
             fontsize=11, color="#1f4e79", va="center",
             bbox=dict(facecolor="white", edgecolor="none", alpha=0.85, pad=2.0),
             arrowprops=dict(arrowstyle="->", color="#1f4e79", lw=1.2))

fig2.suptitle(
    "Figure 2 — Why split the work at a crossover frequency: the FNO's mode cutoff is a hard wall,\n"
    "and on a discontinuity the tail beyond it decays only as $k^{-1}$",
    fontsize=13.5, fontweight="bold", linespacing=1.5,
)
axf2 = fig2.add_subplot(gs2[1, 0])
axf2.axis("off")
axf2.text(0.0, 0.5,
          "Spectra computed by FFT of three analytic 1-D prototypes on $N$=2048 (smooth Gaussian $\\sigma$=0.05; tanh interface $\\varepsilon$=0.01; step jump 1.0$\\rightarrow$0.35);\n"
          "slope fitted on the lobe envelope over $20\\leq k\\leq400$. These prototypes illustrate the mechanism — they are not measurements of the 42 benchmark datasets.",
          fontsize=9, color="#8894a2", style="italic", va="center", linespacing=1.6)

fig2.savefig(OUT2, dpi=185, bbox_inches="tight", facecolor="white")
print(f"wrote {OUT2}  (fitted shock slope = {slope:.3f})")
