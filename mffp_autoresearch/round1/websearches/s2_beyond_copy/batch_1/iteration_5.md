# Iteration 5 — s2_beyond_copy / batch 1  (§3.3 prior-art verdict — FINAL)

**Iteration cap**: this is iteration 5 of 5. **The cap is reached**; no further
searching. All verdicts below are consolidated here.

## Search rationale

Three loose ends from iteration 4, each a direct refutation target:
(a) the OpenReview fetch of *Spectral Shaping for Neural PDE Surrogates* failed, and
that paper is the nearest published relative of any per-band intervention — retry by
a different route;
(b) D1's **spatial** half (error stratified by distance to the interface) had no
retrieved precedent in iteration 2, which is exactly the kind of gap the project's
0-for-4 novelty record (program.md §13.3) says to distrust — search it directly;
(c) settle whether *any* MF operator-learning paper compares its fused prediction to
the **interpolated LF field** (the copy-LF reference). This is the load-bearing
novelty question for the whole stream.

## Search terms used

1. `"Spectral Shaping" neural PDE surrogates arxiv frequency band weighting method`
2. `neural operator error stratified by distance to shock or interface evaluation sharp interface region-wise error metric phase field benchmark`
3. `multi-fidelity operator learning does the fused prediction beat interpolated low-fidelity solution comparison bilinear upsampled coarse baseline`

## Findings

### Term 1 — Spectral Shaping

Results: OpenReview forum + PDF
(https://openreview.net/forum?id=mmDkgLtYNI ;
https://openreview.net/pdf/f4355f5eb3abe0662366f2a4330393d2400459d3.pdf);
FreqNO-DPS (https://arxiv.org/abs/2606.03936); Predictivity/Utility
(https://arxiv.org/html/2604.20061v1); spectral-inspired NO
(https://arxiv.org/html/2505.21573v1); multiscale neural PDE surrogates for ocean
downscaling (https://arxiv.org/html/2507.18067v2).

- **WebFetch of the OpenReview PDF → no usable results** (second attempt; the
  browser-verification wall returned a login page again). The paper is therefore
  cited **only at search-snippet level**, explicitly flagged, never as a fetched
  source.
- Search-snippet content [snippet-only cite: https://openreview.net/forum?id=mmDkgLtYNI]:
  neural PDE surrogates *"suffer from an inability to model the spectrum of solutions
  adequately, especially in the medium to high frequency bands"*; three convergent
  causes — *"distribution shift over unrolls, spectral bias of the MSE loss, and
  spurious high frequency noise, or 'spectral junk', introduced by the use of
  pointwise nonlinearities"*; the method *"involves filtering the spectrum of
  activations after every layer of pointwise nonlinearities"*, claimed to fix the
  learned spectrum *"down to machine precision in some cases"*.
  **Mechanistically distinct from D3**: it filters *activations* inside the network
  for rollout stability; it does not copy an input's low band and it is not
  multi-fidelity. It does not preempt D3, but it does add a third published cause of
  spectral error (pointwise-nonlinearity junk) that D1's band decomposition should be
  able to see, and which the in-repo reports do not mention.
- Also recovered: FreqNO-DPS's *"spectrally shaped guidance score that weights the
  surrogate contribution according to its frequency-dependent accuracy"* — i.e.
  per-band trust weighting of a surrogate is published
  [cite: https://arxiv.org/abs/2606.03936, fetched in iteration 1].

### Term 2 — interface-/shock-stratified error metrics (refutes D1's spatial half)

Results: Shock-Aware Physics-Guided Fusion-DeepONet
(https://arxiv.org/pdf/2510.17887); Shearlet Neural Operators
(https://arxiv.org/html/2604.25181v1); Walsh-Hadamard NO for discontinuous
coefficients (https://arxiv.org/html/2511.07347v1); shock-centered low-rank
structure (https://arxiv.org/html/2605.12723); separation-transfer PINNs for Euler
(https://arxiv.org/pdf/2505.20361); PINNs for astrophysical shocks
(IOPscience 2632-2153/acf116).

- **Shock-Aware Fusion-DeepONet [cite: https://arxiv.org/pdf/2510.17887] (FETCHED) —
  this preempts the "invent a stratified metric" framing.** It defines exactly the
  stratified panel D1 was going to propose: **shock-window error** (accuracy within a
  defined region near the shock front), **gradient-weighted error** (weighting by
  |∇u|), and **shock-location error** (shock position accuracy, inferred from
  velocity-gradient peaks). Signed-distance-to-shock is used **both** as an input
  feature (trunk augmentation, with smooth shock indicators and multi-scale RBFs
  centered at the shock) **and** as an evaluation stratifier. Reported finding:
  improvements are *"especially pronounced in shock-window and gradient-weighted
  metrics, with benefits concentrated near the moving compression layer rather than
  uniformly over the full field"* — i.e. the stratified panel is what made the effect
  visible, which is the methodological argument for D1, already made by someone else.
- Consequence: D1 must **adopt and cite** this metric family rather than present it as
  new. That is a strengthening, not a weakening: a published stratifier makes the
  diagnostic's falsification clause defensible.

### Term 3 — does any MF operator paper use the interpolated-LF reference?

Results: MF-FNO transfer for fluid flow (https://arxiv.org/pdf/2304.06972 ;
AIP PoF 35/7/077118); MF DeepONet closure (ScienceDirect S0045782523002852);
Multifidelity DeepONets (https://arxiv.org/abs/2204.09157); transfer-learning MF PINN
(ScienceDirect S0021999120307166); MF fusion with concatenated NNs (Sci Rep
s41598-022-09938-8); progressive MF learning (ResearchGate 396517333); MF DeepONet
residual learning for ROM (AMSES s40323-023-00249-9); MF semi-supervised image SR
(PMC12431262).

- Every retrieved MF result is framed the same way — *low-fidelity data improves
  predictions relative to an HF-data-only model*, "progressive fusion … systematic
  increases in prediction accuracy … at each level" — i.e. baselines are
  **single-fidelity models or HF-budget curves**.
- **Explicit negative from the search engine's own synthesis:** *"the specific
  comparison you mentioned (fused prediction vs. interpolated low-fidelity solution
  with bilinear upsampling) does not appear in these particular results."*
  Combined with iteration 2 (the persistence-skill convention is meteorology's, not
  operator learning's) and iteration 4 (2604.20061 *names* the missing
  coarse-solution baseline as a gap in its own field), three independent passes agree:
  **the copy-LF reference is not a standard baseline in MF operator learning.**
- Honest caveat recorded: absence of evidence over 5 iterations is weak evidence of
  absence, and this loop reached only search-engine coverage. The verdict below is
  phrased accordingly.

## PRIOR-ART VERDICT (final)

### D1 — copy-LF excess-error decomposition (the batch-1 diagnostic card)

**Verdict: `preempted-but-MF-composition-open`.**

Preempted components, all fetched in this loop:
- Per-band diagnosis of PDE-surrogate error, as a no-new-model analysis paper:
  band-energy relative error, frequency-response lens over solution/operator/NTK
  spectra, λ̃_k ~ k^-2.01 [cite: https://arxiv.org/html/2604.20061v1].
- Per-band `rFFT` bias, amplitude transfer function `H(k)`, mode-wise residual
  variance, and cross-spectral-coherence validation
  [cite: https://arxiv.org/html/2606.03936].
- Per-scale coherence between a *represented/reduced* field and a reference field
  [cite: https://arxiv.org/pdf/2605.26412].
- Interface/shock-stratified evaluation: shock-window, gradient-weighted, and
  shock-location errors [cite: https://arxiv.org/pdf/2510.17887].
- Permutation-based input attribution (shuffle a feature, measure Δerror; unchanged
  error ⇒ the model ignored it), with the correlated-feature and
  estimate-on-held-out-data caveats
  [cite: https://christophm.github.io/interpretable-ml-book/feature-importance.html].

**What remains open** (state precisely; the brainstormer must quote it):
1. **The reference.** No fetched source decomposes surrogate error *relative to the
   model's own low-fidelity input field*. 2604.20061 explicitly flags this as a gap in
   its own analysis — it *"does not systematically compare neural surrogates against
   coarse/low-fidelity solutions as a direct baseline … rather than demonstrating
   whether surrogates outperform the coarse approximation they learn from."* The
   forecasting analogue (persistence skill: worse-than-reference ⇒ negative skill) is
   old and standard, but was not retrieved in any operator-learning or MF paper.
2. **The setting.** 2604.20061's worked example is Kuramoto-Sivashinsky (the *smooth
   control* on the in-repo sharpness axis); 2510.17887 is single-fidelity shock flow.
   No fetched source applies either to **sharp-2D multi-fidelity phase-field** data.
3. **The joint decomposition.** No fetched source combines spectral banding, interface
   stratification, and LF-input attribution on the *same* LF/model/HF triple, which is
   what discriminates the three mechanisms of iteration 3.

### D2 — identity-to-LF fusion (zero-init residual on `up(LF)`, gated correction)

**Verdict: `preempted-but-MF-composition-open`.**
- Preempted mechanism: identity-at-initialization via a zero-initialized residual
  branch — *"At initialization, the network computes the identity, since the residual
  branch contributes zero"* [cite: https://arxiv.org/pdf/1901.09321]; ZerO
  [cite: https://openreview.net/pdf?id=EYCm0AFjaSS, search-listed] and IDInit
  [cite: https://arxiv.org/html/2503.04626, search-listed] are the same family.
  Gated multi-fidelity fusion also exists (AGMF-Net, ScienceDirect
  S002980182502997X — search-listed, scalar-output Bayesian-optimization surrogate,
  not a field model).
- **Remains open**: no retrieved source ties the zero-init identity path to the
  **low-fidelity field** so that "never worse than copy-LF" is a structural property
  of a *multi-fidelity field predictor*; the search engine's synthesis stated
  outright that no such guarantee for neural operators appeared in its results.
  A card proposing D2 must present it as *composition*, cite Fixup for the
  mechanism, and claim novelty only for the MF binding + the gate's per-band /
  per-interface-distance conditioning that D1 would motivate.

### D3 — hard low-band constraint / band-split fusion

**Verdict: `preempted-but-MF-composition-open`.**
- Preempted: band-split reconstruct-only-the-missing-band is standard in speech SR
  (STSR, https://arxiv.org/html/2509.03913 — search-listed) and hyperspectral
  high/low-frequency-split SR (MDPI 2072-4292/15/9/2472 — search-listed); the in-repo
  report already credits AP-BWE for the audio original. The representational
  constraint is also a known theorem-shaped fact: FNO spectral layers *"truncate high
  wavenumbers by construction"*, and band-limited / representation-equivalent
  operators *"cannot generate new (higher) frequencies since their representation
  space is fixed"* (search-snippet, term 1 of iteration 4). Per-band trust weighting
  of a surrogate is published [cite: https://arxiv.org/abs/2606.03936].
  Activation-spectrum filtering is published but mechanistically different
  [snippet-only: https://openreview.net/forum?id=mmDkgLtYNI].
- **Remains open**: binding the preserved low band to a **real coarse PDE solve**
  (repo law: LF is never a downsample) and choosing `k_c` from measured LF/HF
  coherence. Note this is *not* the pre-falsified `mf_fno_spectral` LF low-mode
  freezing (program.md §5) only if the diagnostic shows the LF low band is actually
  accurate; **D3 must not be proposed before D1 reports**, or it re-runs a falsified
  lever.

## Interpretation

Nothing this stream is likely to propose is mechanism-novel; all three directions are
compositions. The one genuinely under-documented element — and the one that makes D1
worth running as a first-class experiment rather than an ablation — is the **copy-LF
reference itself**, which 2604.20061 names as a gap in the surrogate literature and
which no retrieved MF paper adopts.
