# Iteration 2 — `s4_hybrid_routing` batch 1

## Search rationale

Iteration 1 established that per-band and per-region routing over spectral-vs-
attention operator experts is published (SPAMoE, U-HNO) and that neither is
multi-fidelity. Iteration 2 attacks the two things that decide what batch 1 can
actually propose:
1. Is the **sequential FNO-base + attention-corrector residual hybrid** — i.e.
   the already-built `fno_transolver_seq` that §12.4 says batch 1 should score —
   itself published? (If yes, the benchmark card is measurement, not novelty; that
   is fine, but the card must say so.)
2. Does a **multi-fidelity MoE / fidelity-aware gating** paper exist? Term 3 of
   iteration 1 found nothing, but that was one generic query; this is the claimed
   surviving novelty so it needs a direct assault.
3. Is the P4 **band-split-against-the-LF-spectrum** idea from
   `docs/reports/MF_Sharp_HighFreq_Report.md` published in the MF setting?

## Search terms used

1. `sequential FNO base plus transformer residual corrector hybrid neural operator frozen base zero-init gate`
2. `multi-fidelity neural operator gating network low-fidelity field expert selection coarse solve routing`
3. `band-split neural operator hard constrain low frequency to low-fidelity spectrum predict high wavenumber multi-fidelity`

## Findings

### Term 1 — sequential frozen-base + residual corrector

Top results:
- SLE-FNO, single-layer extensions for continual learning in FNOs —
  https://iopscience.iop.org/article/10.1088/1402-4896/ae6bdd
- "Residual-based error corrector operator to enhance accuracy and reliability of
  neural operator surrogates of nonlinear variational boundary-value problems" —
  https://www.sciencedirect.com/science/article/abs/pii/S0045782523007193
- "Residual Factorized Fourier Neural Operator for simulation of 3-D turbulence"
  — https://openreview.net/forum?id=yGdoTL9g18
- NeuroForge (self-correcting CFD engine with calibrated physics-residual trust)
  — https://arxiv.org/html/2607.10333
- U-FNO topic page — https://www.emergentmind.com/topics/u-net-enhanced-fourier-neural-operator-u-fno
- Higher-Order FNO — https://arxiv.org/pdf/2606.28122

The result summary named **SpecB-FNO** ("residual ensemble architectures train
additional FNOs sequentially to model residuals dominated by high-frequency
content") and stated the general pattern "a frozen backbone augmented with a
lightweight task-specific residual module" and "the corrector can be trained
separately with the backbone frozen".

**Fetched** the U-FNO topic page
(https://www.emergentmind.com/topics/u-net-enhanced-fourier-neural-operator-u-fno)
to get a citable anchor for SpecB-FNO / sequential residual FNO stacking:
**it does not contain them** — U-FNO is a global-Fourier + U-Net hybrid, its
listed variants (IU-FNO, Fourier-MIONet) are implicit-recurrent / parameter-
efficient, not residual boosting. So this fetch gives **no usable citation** for
sequential residual stacking. Recorded honestly: SpecB-FNO appeared only in a
search-engine synthesis with no fetched URL, so **it may not be cited**.

The one squarely relevant *fetched* citation for "spectral base + attention
corrector" remains from iteration 1: **"Hybrid operator learning of wave
scattering maps in high-contrast media" — https://arxiv.org/html/2602.11197** —
FNO for the smooth background field plus a ViT-based corrector for the
high-contrast scattering part. That is the same composition as
`fno_transolver_seq`.

### Term 2 — multi-fidelity gating / MoE (the key term)

Top results:
- **"A MULTI-FIDELITY MIXTURE-OF-EXPERT FRAMEWORK"** (OpenReview) —
  https://openreview.net/pdf/2157297b4cbcecdff2cc0d1cff4fe740f12222e4.pdf
- "A Mixture of Experts Gating Network for Enhanced Surrogate Modeling in
  External Aerodynamics" — https://arxiv.org/abs/2508.21249
- "Ensemble adaptive gated multi-fidelity neural network for Bayesian
  optimization: hydrofoil design" —
  https://www.sciencedirect.com/science/article/abs/pii/S002980182502997X
- "Multi-fidelity prediction of fluid flow and temperature field based on
  transfer learning using FNO" — https://arxiv.org/pdf/2304.06972
- "A Multi-Fidelity Graph U-Net Model for Accelerated Physics Simulations" —
  https://arxiv.org/pdf/2412.15372
- Shodh-MoE — https://arxiv.org/pdf/2605.15179

**Fetch attempt on the MF-MoE OpenReview PDF FAILED** — OpenReview served a
browser-verification page, no content. The search-engine synthesis described it
as *"combining a pure neural operator with multiple solver-based hybrid models of
varying fidelity, leveraging them as expert models, with a physics-aware gating
network that dynamically selects the most appropriate expert based on input
characteristics to optimize both computational cost and predictive accuracy."*
**That description is NOT a citation** (not fetched) — flagged for a retry in
iteration 3 via a non-OpenReview mirror. Note the described setup routes among
*models of different fidelity/cost* (a cost-accuracy selector), which is a
different object from MFFP's "one HF prediction fused from a given LF field".

**Fetched** the aerodynamics MoE gating paper (https://arxiv.org/abs/2508.21249):
gates over three heterogeneous surrogates (DoMINO decomposable multi-scale neural
operator, X-MeshGraphNet, FigConvNet) with a **spatially-variant weighting
strategy assigning credibility to each expert based on its localized
performance** — i.e. **per-point/per-region gating over heterogeneous operator
experts, learned from localized error**. No multi-fidelity structure, no formal
no-harm guarantee (empirically beats both the ensemble average and the best
single expert).

This matters a lot: **"learned per-region gating over complementary operator
experts, weighted by localized expert error" — the most natural way to cash the
+30.6% FNO<->Transolver oracle — is published (2508.21249) in single-fidelity
form.**

### Term 3 — band-split against the LF spectrum

Top results: mostly speech (Band-split RNN, https://arxiv.org/abs/2212.00406 —
the audio-BWE ancestor the in-repo sharp report already cites), plus
- IRNO, "Iterative Refinement Neural Operators are Learned Fixed-Point Solvers"
  — https://arxiv.org/pdf/2605.24041 (already known; owned by `s3_testtime`)
- "Residual Multi-Fidelity Neural Network Computing" — https://arxiv.org/pdf/2310.03572
- MFPC-Net multi-fidelity physics-constrained neural process — https://arxiv.org/pdf/2010.01378
- Graph-Laplacian Bayesian multi-fidelity — https://arxiv.org/pdf/2409.08211

**No usable results** for the specific mechanism (hard-constrain the output's
sub-`k_c` Fourier band to the LF spectrum, predict only `k > k_c`, `k_c` set by
LF/HF cross-spectral coherence). The search engine's own summary says the same:
*"the specific paper on 'band-split neural operator' with hard constraints on
low-frequency to low-fidelity spectrum and high-wavenumber prediction does not
appear in these results."* One negative query only — not yet a novelty verdict.

## Interpretation

Per-region gating over complementary operator experts weighted by localized error
is published single-fidelity (arXiv:2508.21249), as is per-band routing over
operator experts (SPAMoE) and per-location hard branch routing (U-HNO); the
spectral-base + attention-corrector composition is published too
(arXiv:2602.11197). What no fetched source yet shows is **routing conditioned on
the LF field / on the LF-HF disagreement**, or **band-splitting against the LF
spectrum**. Iteration 3 must (a) recover a citable version of the MF-MoE paper,
and (b) run the two refutation queries that turn those negatives into verdicts.
