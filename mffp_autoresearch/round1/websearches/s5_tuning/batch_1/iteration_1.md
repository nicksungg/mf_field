# Iteration 1 — Stream `s5_tuning`, Batch 1

## Search rationale

The batch is pre-directed (program.md §12.5) to the `modes_cap` 12 -> 32 knob on the
champion `mf_fno_transfer_film`. `summary_so_far.md` open questions 1-3 are the ones
that decide whether that knob is worth a card at all:

- Q1/Q2: is more modes monotonically better, or is there a documented overfitting /
  non-monotone regime? (M1 in `docs/proposals/MODELS_TO_TRY.md` *assumes* better; F22
  only asserts the cap doesn't scale with resolution.)
- Q3: does FNO **spectral bias** mean the extra modes never get learned, making the
  knob a no-op?

So turn 1 goes straight at the primary literature on FNO mode-count ablations, FNO
spectral bias, and the field's normative hyperparameter defaults (to see whether
`modes_cap=12` is an outlier or the field standard). Three terms, no truncation needed.

## Search terms used
1. "Fourier Neural Operator number of Fourier modes ablation overfitting truncation study"
2. "FNO spectral bias fails to learn high frequency modes neural operator"
3. "neural operator hyperparameter sensitivity benchmark modes width depth PDE"

## Findings

### Term 1: "Fourier Neural Operator number of Fourier modes ablation overfitting truncation study"

- [Gopakumar et al. 2024] "Plasma Surrogate Modelling using Fourier Neural Operators" —
  mode-count ablation: error decreases with modes but **plateaus at 8 modes** and does
  not improve further; low-mode FNOs give *smoother* fields, high-mode (kmax=8, 32)
  outputs are visibly **noisier** while preserving structure better. URL:
  https://arxiv.org/pdf/2311.05967 (journal version:
  https://iopscience.iop.org/article/10.1088/1741-4326/ad313a)
- [Kashefi & Mukerji 2024] "A novel Fourier neural operator framework for
  classification of multi-sized images" — reports a "critical interplay between the
  number of modes and the tendency for overfitting": beyond 2 modes the train/val loss
  **diverges severely**; optimal mode count for minimizing that divergence was 2. URL:
  https://arxiv.org/pdf/2402.11568
- [survey/overview] "Fourier Neural Operators Explained: A Practical Perspective" —
  frames mode truncation as **smoothness regularization**: m controls a bias-variance
  trade-off, "too small impairs expressivity, too large increases overfitting and
  cost". URL: https://arxiv.org/pdf/2512.01421
- [2026] "Forcing and Diagnosing Failure Modes of Fourier Neural Operators Across
  Diverse PDE Families" — failure patterns depend **jointly on architecture and PDE
  family** (3 architectures x 5 PDE families). URL: https://arxiv.org/abs/2601.11428
  (fetched below)

**WebFetch (arXiv:2601.11428, full PDF).** Summarizer reports: mode truncation is a
critical failure point; "increasing the number of retained Fourier modes provides only
marginal improvements" in regimes with sharp discontinuities / rapid spatial variation.
Per-family: **sharp-interface PDEs degrade severely even with more modes**;
**phase-field is intermediate** — extra modes help more than in sharp-interface cases
but plateau at moderate mode counts; **Helmholtz** needs disproportionately more modes
than theory suggests for mid-to-high frequency content; **Poisson is comparatively
well-suited to FNO and improves most consistently with added modes**. The paper's
framing is that architectural limits, not spectral resolution, dominate the failures.
*Confidence caveat:* the first fetch of the abstract page returned metadata only; the
PDF fetch produced this summary without verbatim quotes or numbers, so treat the
per-family ordering as a paraphrase to re-verify before citing it as a threshold.

### Term 2: "FNO spectral bias fails to learn high frequency modes neural operator"

- [Liu-Schiaffini / Qin et al. 2024] "Toward a Better Understanding of Fourier Neural
  Operators from a Spectral Perspective" — the load-bearing hit; **"simply increasing
  the number of retained Fourier modes is insufficient to overcome the spectral
  bias."** URL: https://arxiv.org/abs/2404.07200 (HTML fetched below)
- [2025] "Mitigating Spectral Bias in Neural Operators via High-Frequency ..." —
  spectral bias toward low frequencies stems from frequency truncation used for
  efficiency; hurts PDEs with strong high-frequency oscillation. URL:
  https://arxiv.org/pdf/2503.13695
- [2026] "SirenFNO: Efficient and Full Frequency Learning of Fourier Neural Operators"
  — targets full-frequency learning in FNO. URL: https://arxiv.org/html/2606.11518
- [2026] "Frequency Bias and OOD Generalization in Neural Operators under a
  Variable-Coefficient Wave Equation" — FNO degrades when test ICs carry higher
  frequencies than training. URL: https://arxiv.org/pdf/2605.12997
- [2026] "Iterative Refinement Neural Operators are Learned Fixed-Point Solvers"
  (IRNO) — spectral-bias mitigation by iterative refinement; already known to this
  project as proposal N1 for `s3_testtime`. URL: https://arxiv.org/pdf/2605.24041

**WebFetch (arXiv:2404.07200, HTML).** Identifies **"Fourier parameterization bias"**:
kernels parameterized in Fourier space are more strongly biased toward the *dominant*
frequencies of the target than spatially-parameterized kernels, because PDE energy is
far more concentrated in Fourier space (for Navier-Stokes, 1.2% of Fourier pixels hold
99% of the energy), so the loss is dominated by a few modes. Consequence quoted
directly: with expanded kernels FNO "still focuses on a few dominant frequencies and
cannot effectively learn the additional parameters to approximate non-dominant
frequencies" — their Fig. 4(a) shows error curves *rising* near the higher frequencies
**inside** the truncation zone. Their remedy is **SpecB-FNO**: iteratively train extra
FNO residual modules on the previous stage's prediction error (the residual's energy is
more evenly spread in Fourier space). Reported relative-error reductions vs FNO: Darcy
46.6%, NS(nu=1e-5) 63.3%, shallow water 39.0%, diffusion-reaction 92.5%, ~50% average.

### Term 3: "neural operator hyperparameter sensitivity benchmark modes width depth PDE"

- [2025] "A comprehensive comparison of neural operators for 3D industry-scale
  engineering designs" — benchmarks under **capacity-aligned presets** (S/M/L, ~O(1M),
  O(10-50M), O(100-1000M) params) so that families are compared at matched parameter
  count, with `width`, `layers`, `modes`, `heads` as the structural knobs. URL:
  https://arxiv.org/html/2510.05995v1
- [2025] "Benchmarking neural surrogates on realistic spatiotemporal multiphysics
  flows" — same unified-hyperparameter-selection discipline. URL:
  https://arxiv.org/pdf/2512.18595
- Field-standard FNO settings recurring across these benchmark papers: 1-D with
  16 modes / width 64; **2-D PDEs with (12, 12) modes and width 20**; 3-D
  Navier-Stokes (12,12,12) modes / width 20 — i.e. **`modes_cap=12` is the canonical
  FNO default, not an oversight**, though it was set for the original 64^2 Darcy/NS
  benchmarks, not for 256^2 grids.

## Interpretation (1-3 sentences)

The strongest result in the field is *against* the naive form of this batch's
pre-directed knob: 2404.07200 states explicitly that raising the retained-mode count
does not overcome FNO's spectral bias, because Fourier-space parameterization keeps the
loss dominated by a handful of high-energy modes, and two independent ablations report
mode-count **plateaus** (plateau at 8) or outright **train/val divergence** past a small
mode count. Simultaneously, `modes_cap=12` turns out to be the field-standard FNO
default for 2-D — inherited from 64^2 benchmarks — which is exactly the F22 complaint
(it doesn't scale to 256^2) but also means "12 is arbitrary" is not itself evidence that
32 is better. The benchmark literature also supplies the fairness discipline this card
needs: mode ablations there are run at **capacity-aligned parameter budgets**, which our
12 -> 32 bump (7.1x spectral params) is not.
