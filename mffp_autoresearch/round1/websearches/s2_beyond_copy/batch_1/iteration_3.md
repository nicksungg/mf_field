# Iteration 3 — s2_beyond_copy / batch 1

## Search rationale

Iterations 1-2 built the *measurement* side. This turn goes at the three concrete
**failure mechanisms** the diagnostic must be able to tell apart, because a
diagnostic that cannot discriminate hypotheses is not an experiment (program.md §1):
(a) **the model ignores its LF input** — the strongest reading of "best-zoo nRMSE is
flat at 0.18-0.48 while copy-LF spans 0.016-0.33" (`summary_so_far.md`), which needs a
published input-attribution protocol to test;
(b) **residual vs direct prediction** — the in-repo report claims the residual target
is *harder* than the field when LF mispositions a feature (MF_Sharp_HighFreq §0.2),
whereas super-resolution folklore says residual learning always wins; which is it,
and under what condition does it flip;
(c) **normalization** — §12.2 lists "normalization destroying amplitude structure" as
a candidate mechanism, with no citation attached.

## Search terms used

1. `input channel ablation shuffle test does neural surrogate actually use low-fidelity input feature importance operator learning diagnostic`
2. `residual learning versus direct prediction which is better when residual target is harder super-resolution multi-fidelity correction network comparison`
3. `normalization scheme neural operator multi-scale fields per-sample standardization destroys amplitude information failure`

## Findings

### Term 1 — does the model use its LF input?

Results were mostly off-domain (PROTAC design, LLM surrogate fidelity, ferrofluid
channels) except the methodological anchor:
**Permutation Feature Importance** (Molnar, *Interpretable Machine Learning*, ch. 23,
https://christophm.github.io/interpretable-ml-book/feature-importance.html) and
LLM-attribution work (https://arxiv.org/html/2606.32008).

- **PFI [cite: https://christophm.github.io/interpretable-ml-book/feature-importance.html]
  (FETCHED).** Exact protocol: measure baseline error; randomly shuffle one feature's
  values, breaking the feature-outcome relationship; recompute error; importance =
  ratio or difference. Interpretation rule verbatim: a feature is important *"if
  shuffling its values increases the model error, because in this case the model
  relied on the feature for prediction"*, and unimportant when *"shuffling its values
  leaves the model error unchanged, because in this case the model ignored the
  feature for prediction"* — factor 1.0 / difference 0 means no contribution.
  Documented limitations to inherit: permutation manufactures unrealistic instances
  when features are correlated; correlated features redistribute importance; and PFI
  must be estimated **on data not used for training** or it is optimistic.
- Transplant for this stream: **permute the LF field across test samples** (keep the
  condition vector fixed) and measure the change in panel nRMSE. If the error is
  unchanged, the fusion families provably ignore the LF field at inference and the
  entire "fusion destroys LF information" framing is wrong in an informative way —
  they never had it. The PFI caveat about correlated inputs applies directly and
  honestly here (LF field and condition vector are strongly dependent), which is why
  the *cross-sample shuffle within the same dataset* is the right form.
- **No usable results** for an operator-learning paper that runs this test on an LF
  input channel. Not retrieved in this loop.

### Term 2 — residual vs direct prediction

Results: VDSR (https://arxiv.org/pdf/1511.04587); cascaded multi-scale cross network
(https://arxiv.org/pdf/1802.08808); artifact-free residual network
(https://arxiv.org/pdf/2009.12433); multiscale SR of fluid flows
(https://arxiv.org/html/2509.14721v1); physics-consistent diffusion for fluid SR via
multiscale residual correction (https://arxiv.org/pdf/2603.00149); MF +
learning-regularization for SISR (ScienceDirect S001600322200206X); probabilistic ML
regional climate risk (https://arxiv.org/pdf/2412.08079).

- The mainstream position, from the search synthesis: *"since a low-resolution image
  is already available as input, predicting high-frequency components is sufficient …
  residual networks converge much faster than direct prediction"*, and *"since the
  super-resolution prediction is largely similar to the input, residual learning is
  widely adopted in SR"*. In climate downscaling, *"modeling the residual between the
  high-resolution target and the interpolated low-resolution input leads to
  significant improvements"* including on extreme percentiles.
- **The documented failure condition is about the residual target's quality, not its
  size**: *"the drawback of learning residuals is that the target residual image often
  includes some artifacts"*, and the reported fix is architectural — train residual
  *features* but target the ground-truth image rather than the noisy residual image.
- Reading: SR literature's premise — LR input and HR target are **pixel-aligned by
  construction** (the LR is a downsample of the HR) — is exactly the premise MFFP
  violates by repo law (LF is an independent coarse *solve*, never a downsample).
  So the SR consensus "residual always wins" does not transfer, and the in-repo
  misalignment-dipole argument is not contradicted by it; but note that **no fetched
  source in this loop demonstrates the dipole claim empirically**. It remains a
  hypothesis this diagnostic can test, which is a point in the diagnostic's favor.

### Term 3 — normalization

Results: **QuadNorm** (https://arxiv.org/html/2605.07375 and /pdf/2605.07375);
multi-grid tensorized FNO (https://arxiv.org/pdf/2310.00120); discrete solution
operator learning (https://arxiv.org/pdf/2601.09143); MRE inversion with operator
learning (https://arxiv.org/pdf/2510.03372).

- **QuadNorm [cite: https://arxiv.org/html/2605.07375] (FETCHED).** States that
  normalization layers are *"a critical yet under-examined component of neural
  operator architectures"* and identifies **discretization dependence** as the defect:
  standard normalization computes statistics by uniform averaging over grid values, so
  *"the discrete mean changes, even though the underlying function is the same. This
  discretization dependence creates a pathway for the normalization to break the
  resolution invariance."* Fix: quadrature (trapezoidal) weights → O(h²) rather than
  O(h) statistic mismatch; BlendQuadNorm interpolates to LayerNorm with a parameter α.
  Documented effects: transfer degradation grows with the resolution ratio (2x-8x
  studied); the QuadNorm-over-LayerNorm advantage grows with depth (2.9x at 4 layers →
  4.7x at 8); equal point weights distort statistics on non-uniform meshes.
  **Architecture-dependent**: for periodic **FNO**, QuadNorm *sacrifices* native
  accuracy for transfer (BlendQuadNorm α=0.3 recovers it) — attributed to boundary
  perturbations interacting with periodic spectral features; for Galerkin/Transolver
  it improves native accuracy up to 26%. The fetched content contains **no** claim
  about harm to sharp fields specifically.
- Independently, the search synthesis surfaces the **per-sample amplitude**
  normalization pattern (divide by max |u| to get a dimensionless pattern, recover
  scale with a separate amplitude regressor) — the literature treats the
  amplitude/pattern split as a *deliberate design choice with an explicit repair*, not
  as an unrecognized failure. That weakens §12.2's "normalization destroys amplitude
  structure" as a *novel* mechanism claim but strengthens it as a **checkable
  implementation defect**: if a panel family normalizes per-sample and never restores
  amplitude, that is a bug the diagnostic would expose.
- Directly relevant to the MFFP setting: LF and HF live on **different grids** and
  the round's copy-LF reference bilinearly interpolates LF onto the HF grid, so
  QuadNorm's discretization-dependence pathway is live for any family that normalizes
  the LF field with grid-uniform statistics before fusing.

## Interpretation

The three mechanisms are now separable by measurement: LF-permutation error change
(does the model use LF at all — PFI protocol), per-band `rFFT`/`H(k)` and LF/HF
coherence (spectral vs spatial localization of the excess error), and a
normalization-statistics audit (QuadNorm's discretization pathway; per-sample
amplitude split). None of the three has a fetched source that already reports the
result for multi-fidelity operator learning. Remaining before the verdict: check
whether the specific batch-2-shaped mechanisms (hard low-band copy of LF; gated
identity-to-LF fusion) are published — that is §3.3 work, iteration 4.
