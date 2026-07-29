# Websearch Report — Stream `s2_beyond_copy`, Batch 1

**Stream**: s2_beyond_copy
**Batch**: 1
**Total iterations**: 5
**Total WebSearch calls**: 15 (3 per iteration, cap respected)
**Total WebFetch calls**: 12 (8 usable, 4 dead — every dead fetch noted inline and in Dead ends)
**Cap hit**: **YES** — 5 of 5 iterations used; noted in `iteration_5.md` header.

**Pre-directed slot** (program.md §12.2 / §4.3): batch 1 of this stream **is a
diagnostic card by design**. The verdict below therefore covers the diagnostic (D1)
plus the two mechanisms it would motivate for batch 2 (D2, D3), so the brainstormer
can design the diagnostic to discriminate between them.

## Search trace

### Turn 1 — is the premise novel, and what is the citable metric machinery?
**Terms chosen** (and why): `summary_so_far.md` Q1-Q3. The stream's premise ("fusion
loses to its own input") had to be checked for prior documentation *before* any
diagnostic was designed; the diagnostic needed a published metric to stand on; and
"identity init" had to be checked because it is the obvious batch-2 mechanism.
- `multi-fidelity neural operator worse than low-fidelity baseline negative transfer …`
  → [iteration_1.md](iteration_1.md)
  - Key finding: retrieved MF work reports *negative transfer* (benefit shrinks with
    longer rollouts / different dynamics) but **no source reports a learned MF
    surrogate scoring worse than copying its own LF input**. WebFetch of
    https://arxiv.org/pdf/2511.01830 returned metadata only → dead end.
- `per-wavenumber band error decomposition diagnostic neural operator …`
  → [iteration_1.md](iteration_1.md)
  - Key finding: **FreqNO-DPS** supplies a ready diagnostic triple — frequency-banded
    relative FFT bias `rFFT` (measured −0.075 / −0.137 / −0.239 low/mid/high, negative
    = systematic attenuation), amplitude transfer function `H(k)` (`≈1` low-k,
    `|H(k)|≪1` in the bias regime), mode-wise residual variance — plus off-diagonal
    **cross-spectral coherence** offered as "a verification tool for applying the
    method to new surrogates". [cite: https://arxiv.org/html/2606.03936]
  - Key finding: a neural operator can be **"worse than trivial baselines (such as
    zero-padding or simple projection methods)"** in high-frequency bands.
    [cite: https://arxiv.org/pdf/2605.12997]
- `identity initialization zero-initialized residual branch …` → [iteration_1.md](iteration_1.md)
  - Key finding: **"At initialization, the network computes the identity, since the
    residual branch contributes zero"** — identity-at-init is generic published
    practice, so it cannot carry novelty. [cite: https://arxiv.org/pdf/1901.09321]

### Turn 2 — the reference convention, the spatial metric, and coherence
**Terms chosen**: close the three methodological gaps left by turn 1 — is copy-the-input
skill an established protocol; is there a named interface-localized error metric; is
LF/HF coherence-vs-k a cited MF diagnostic (the in-repo report asserts it without a source).
- `skill score forecast reference baseline persistence "worse than" …` → [iteration_2.md](iteration_2.md)
  - Key finding: the skill-score convention is standard in forecasting (reference =
    climatology/**persistence**, "the next value equals the most recently observed
    value"; worse-than-reference ⇒ negative skill). Copy-LF skill is the operator
    transcript of persistence skill. **No usable results** in operator learning.
- `interface-localized error metric sharp interface phase field …` → [iteration_2.md](iteration_2.md)
  - Key finding: **no usable results** for a named "error vs distance-to-interface"
    evaluation metric at this turn; the community frames interface-locality as a
    *sampling* problem ("important features … concentrated near the diffuse
    interface") [cite: https://arxiv.org/html/2607.19690]. (Superseded by turn 5.)
- `cross-spectral coherence low-fidelity high-fidelity …` → [iteration_2.md](iteration_2.md)
  - Key finding: **multi-scale coherence** — decompose a *represented/reduced* field
    and a reference field and quantify agreement **at each scale independently**, to
    "identify which scales … are well-captured … versus where significant information
    loss occurs". [cite: https://arxiv.org/pdf/2605.26412]. Magnitude-squared
    coherence = "fraction of variance … linearly predictable from the other series at
    the same frequency" (MIT OCW 12.864 page text; the PDF fetch failed → dead end).

### Turn 3 — the three candidate failure mechanisms
**Terms chosen**: a diagnostic that cannot separate hypotheses is not an experiment
(program.md §1), so search for the protocol that tests each of: model ignores LF;
residual-vs-direct; normalization.
- `input channel ablation shuffle test …` → [iteration_3.md](iteration_3.md)
  - Key finding: **permutation feature importance** — shuffle a feature, recompute
    error; *"unimportant if shuffling its values leaves the model error unchanged,
    because … the model ignored the feature"*; caveats: correlated features make
    unrealistic instances, and PFI must be estimated on held-out data.
    [cite: https://christophm.github.io/interpretable-ml-book/feature-importance.html]
- `residual learning versus direct prediction …` → [iteration_3.md](iteration_3.md)
  - Key finding: SR literature's "residual always wins" rests on LR being a
    **downsample** of HR (pixel-aligned by construction) — a premise MFFP violates by
    repo law; its documented residual failure mode is *artifacts in the residual
    target*, not target magnitude. No fetched source demonstrates the
    misalignment-dipole claim empirically → it stays a testable hypothesis.
- `normalization scheme neural operator multi-scale fields …` → [iteration_3.md](iteration_3.md)
  - Key finding: **QuadNorm** — normalization is "a critical yet under-examined
    component of neural operator architectures"; uniform-average statistics are
    discretization-dependent, which "creates a pathway for the normalization to break
    the resolution invariance"; transfer degradation grows with resolution ratio and
    with depth (2.9× → 4.7×, 4 → 8 layers); effects are architecture-dependent
    (QuadNorm *hurts* native FNO accuracy; helps Transolver up to 26%).
    [cite: https://arxiv.org/html/2605.07375]

### Turn 4 — §3.3 refutation, part 1 (ENOUGH declared on field context)
**Terms chosen**: one adversarial search per candidate direction (D3, D2, D1).
- `band-split hard constrain low frequency coefficients to input …` → [iteration_4.md](iteration_4.md)
  - Key finding: FNO layers "truncate high wavenumbers by construction"; band-limited
    operators "cannot generate new (higher) frequencies since their representation
    space is fixed". Band-split reconstruction is published in speech/hyperspectral SR;
    **no MF-PDE version retrieved**.
- `gated fusion multi-fidelity guaranteed at least as good as low-fidelity …` → [iteration_4.md](iteration_4.md)
  - Key finding: gated MF fusion exists (AGMF-Net, scalar-output BO surrogate), but the
    results contain **no** "at least as good as the low-fidelity model" guarantee for
    neural operators.
- `diagnostic analysis paper why neural PDE surrogate fails …` → [iteration_4.md](iteration_4.md)
  - **The main prior-art hit**: *Predictivity and Utility of Neural Surrogates of
    Multiscale PDEs* — a **diagnostic paper with no new model**: frequency-response
    lens over solution/operator/NTK spectra, band-energy relative error (KS: "dissipation-range
    bands exhibit huge relative mismatch due to the surrogate maintaining a nonzero
    high-k floor"), λ̃_k ~ k^-2.01 so "k=15 … requires 158× more training iterations
    than k=1", and MSE ⇒ "the average over all fine states consistent with the coarse
    input". **Crucially it "does not systematically compare neural surrogates against
    coarse/low-fidelity solutions as a direct baseline. This is a notable gap".**
    [cite: https://arxiv.org/html/2604.20061v1]

### Turn 5 — §3.3 refutation, part 2 (cap reached)
**Terms chosen**: retry the failed Spectral-Shaping fetch by another route; hit the
interface-stratified-metric gap head-on (distrust a clean-looking gap, §13.3); and
settle the copy-LF-reference novelty question.
- `"Spectral Shaping" neural PDE surrogates …` → [iteration_5.md](iteration_5.md)
  - Key finding (**snippet only — both OpenReview fetches hit the verification wall**):
    "spectral junk … introduced by the use of pointwise nonlinearities"; the method
    "filters the spectrum of activations after every layer of pointwise
    nonlinearities". Mechanistically distinct from band-split; adds a third published
    cause of spectral error the in-repo reports omit.
    [snippet-only: https://openreview.net/forum?id=mmDkgLtYNI]
- `neural operator error stratified by distance to shock or interface …` → [iteration_5.md](iteration_5.md)
  - Key finding: **the stratified metric family is published** — shock-window error,
    gradient-weighted error, shock-location error, with signed-distance-to-shock used
    both as input feature and evaluation stratifier; improvements "especially
    pronounced in shock-window and gradient-weighted metrics, with benefits
    concentrated near the moving compression layer rather than uniformly over the full
    field". [cite: https://arxiv.org/pdf/2510.17887]
- `multi-fidelity operator learning does the fused prediction beat interpolated LF …`
  → [iteration_5.md](iteration_5.md)
  - Key finding: every retrieved MF paper baselines against **single-fidelity models or
    HF-budget curves**; the search synthesis states the fused-vs-interpolated-LF
    comparison "does not appear in these particular results". Third independent pass
    agreeing that the copy-LF reference is not standard in MF operator learning.

## Prior-art verdict

| Candidate direction | Verdict | Citations (fetched) | What remains open |
|---|---|---|---|
| **D1** — copy-LF excess-error decomposition diagnostic: per-band `rFFT`/`H(k)`/coherence + interface-distance stratification + LF-permutation attribution, on the LF/model/HF triple, for the 5 beyond-copy panel datasets | **preempted-but-MF-composition-open** | https://arxiv.org/html/2604.20061v1 (band-energy error, frequency-response lens, no-new-model diagnostic); https://arxiv.org/html/2606.03936 (`rFFT` bands, `H(k)`, coherence check); https://arxiv.org/pdf/2605.26412 (per-scale coherence, represented vs reference field); https://arxiv.org/pdf/2510.17887 (shock-window / gradient-weighted / shock-location errors); https://christophm.github.io/interpretable-ml-book/feature-importance.html (permutation attribution) | (1) **The reference**: no fetched source decomposes error *relative to the model's own LF input*; 2604.20061 names the missing coarse-solution baseline as "a notable gap" in its own field. (2) **The setting**: 2604.20061's example is KS (the smooth control); 2510.17887 is single-fidelity shock flow — neither is sharp-2D **multi-fidelity** phase-field. (3) **The joint decomposition**: no source combines spectral banding + interface stratification + LF-input attribution on one LF/model/HF triple. |
| **D2** — identity-to-LF fusion: output = `up(LF)` at init via zero-init residual branch, learned gated correction (batch-2 candidate) | **preempted-but-MF-composition-open** | https://arxiv.org/pdf/1901.09321 (Fixup: "At initialization, the network computes the identity, since the residual branch contributes zero") | Binding the identity path to the **LF field** so "never worse than copy-LF" is structural for a *multi-fidelity field predictor*; the retrieved corpus contains no such guarantee for neural operators, and the one gated-MF surrogate found (AGMF-Net) is scalar-output BO, not a field model. Novelty may be claimed only for the MF binding + a gate conditioned on the per-band / per-interface-distance structure D1 measures. |
| **D3** — hard low-band constraint / band-split fusion, `k_c` from LF/HF coherence (batch-2 alternative) | **preempted-but-MF-composition-open** | https://arxiv.org/abs/2606.03936 (per-band trust weighting of a surrogate); FNO truncation + band-limited-operator facts and speech/hyperspectral band-split (search-listed, iteration_4/5) | Binding the preserved low band to a **real coarse PDE solve** (repo law: LF never a downsample) and setting `k_c` from measured coherence. **Gated on D1**: proposing it before the diagnostic shows the LF low band is accurate re-runs the pre-falsified `mf_fno_spectral` LF low-mode-freezing lever (program.md §5). |

## Citations summary

- Duraisamy, "Predictivity and Utility of Neural Surrogates of Multiscale PDEs" — https://arxiv.org/html/2604.20061v1 — fetched, iteration_4.md term 3
- "Correcting Neural Operator Spectral Bias via Diffusion Posterior Sampling with Sparse Observations" (FreqNO-DPS) — https://arxiv.org/html/2606.03936 (abs: https://arxiv.org/abs/2606.03936) — fetched, iteration_1.md term 2; iteration_5.md term 1
- "Frequency Bias and OOD Generalization in Neural Operators under a Variable-Coefficient Wave Equation" — https://arxiv.org/pdf/2605.12997 — fetched, iteration_1.md term 2
- Zhang, Dauphin & Ma, "Fixup Initialization" — https://arxiv.org/pdf/1901.09321 — fetched, iteration_1.md term 3
- Jafari, "Multi-Scale Coherence of Represented Flows" — https://arxiv.org/pdf/2605.26412 — fetched, iteration_2.md term 3
- Molnar, "Permutation Feature Importance", *Interpretable ML* ch. 23 — https://christophm.github.io/interpretable-ml-book/feature-importance.html — fetched, iteration_3.md term 1
- "QuadNorm: Resolution-Robust Normalization for Neural Operators" — https://arxiv.org/html/2605.07375 — fetched, iteration_3.md term 3
- "Shock-Aware Physics-Guided Fusion-DeepONet Operator for Rarefied Micro-Nozzle Flows" — https://arxiv.org/pdf/2510.17887 — fetched, iteration_5.md term 2
- "A phase-field neural solver for moving contact line problems" — https://arxiv.org/html/2607.19690 — search-listed with quoted snippet, iteration_2.md term 2
- "Spectral Shaping for Neural PDE Surrogates" — https://openreview.net/forum?id=mmDkgLtYNI — **snippet only, fetch failed twice**, iteration_4.md / iteration_5.md
- ZerO Initialization — https://openreview.net/pdf?id=EYCm0AFjaSS — search-listed only, iteration_1.md term 3
- IDInit — https://arxiv.org/html/2503.04626 — search-listed only, iteration_1.md term 3

## Dead ends

- WebFetch https://arxiv.org/pdf/2511.01830 (MF scaling laws, CFD) → returned PDF
  metadata only; no results section extractable. No claim made from it.
- WebFetch https://openreview.net/pdf/f4355f5eb3abe0662366f2a4330393d2400459d3.pdf and
  https://openreview.net/forum?id=mmDkgLtYNI → OpenReview browser-verification wall,
  twice. Cited at snippet level only, flagged as such.
- WebFetch of the MIT OCW 12.864 cross-spectra notes → undecoded PDF streams; the
  coherence definition rests on the search-result text plus the MathWorks doc page and
  is textbook material, not a novelty claim.
- Term `skill score … persistence … multifidelity operator learning evaluation protocol`
  → returned energy/air-quality forecasting only; useful for the *convention*, useless
  for operator-learning prior art.
- Term `interface-localized error metric … phase field` (iteration 2) → no named metric;
  the correct query turned out to be the **shock** vocabulary (iteration 5 term 2),
  which found the metric family immediately. Lesson for later batches: the sharp-2D
  literature indexes under "shock", not "interface".

## For the brainstormer

The brainstormer **MUST quote the D1 verdict** (`preempted-but-MF-composition-open`)
and its "what remains open" cell in the card's `prior_art` field.

1. **Do not present the diagnostic's metrics as new.** Per-band error decomposition
   [2604.20061, 2606.03936], per-scale coherence [2605.26412], and shock/interface-
   stratified error [2510.17887] are all published. Adopt them by citation. The card's
   novelty claim is the **reference** (copy-LF / persistence-style skill applied to MF
   operator learning) and the **setting** (sharp-2D MF phase-field), nothing more.
2. **The single strongest quotable gap**: 2604.20061 *"does not systematically compare
   neural surrogates against coarse/low-fidelity solutions as a direct baseline. This
   is a notable gap; comparisons focus on training error, rollout divergence, and
   idealized reduced-order models rather than demonstrating whether surrogates
   outperform the coarse approximation they learn from."* Three independent search
   passes found no MF operator paper that closes it.
3. **Design the diagnostic to separate three mechanisms**, because all three have
   published support and the data cannot currently distinguish them:
   (a) *the model never uses the LF field* — test by permuting LF across test samples
   with the condition vector fixed and measuring Δ nRMSE (PFI protocol + its
   held-out-data and correlated-feature caveats);
   (b) *the excess error is spectral* — per-band `rFFT`/`H(k)` of model vs of copy-LF,
   plus LF/HF coherence vs k, on the same triple;
   (c) *the excess error is interface-localized* — shock-window / gradient-weighted /
   distance-stratified error, model vs copy-LF.
   Mechanism (a) is the cheapest and the highest-information: `summary_so_far.md`
   notes best-zoo nRMSE is flat (0.18-0.48) while copy-LF spans 20× (0.016-0.33),
   which is the signature of an unused LF input.
4. **Falsification must be structural, not numeric.** `state/noise_floor.json` does not
   exist yet (batch 0 queued), so a threshold like "±0.005 nRMSE" is unfalsifiable.
   Phrase it as a concentration ratio (e.g. "≥X% of the excess-over-copy-LF error mass
   sits in band/stratum Y"), which program.md §12.2 already frames: *"the failure is
   concentrated in X" is falsified if the error excess is spatially/spectrally
   uniform*. The stream anchor is fixed by definition at **skill 1.0 = copy-LF** and
   needs no batch-0 certification.
5. **Two mechanisms are worth instrumenting cheaply inside the same diagnostic**, since
   both are checkable without training: QuadNorm's discretization-dependent
   normalization statistics [2605.07375] — live here because LF is bilinearly
   interpolated from a different grid before fusion — and the per-sample amplitude/
   pattern split (normalize by max|u| without restoring amplitude), which the
   literature treats as a design choice *with an explicit repair*, so its absence in a
   panel family is a findable bug.
6. **Do not propose D3 (band-split) before D1 reports.** Freezing/copying LF low modes
   is adjacent to the pre-falsified `mf_fno_spectral` lever (program.md §5); it is only
   defensible if the diagnostic shows the LF low band is measurably accurate on these
   datasets. D2 (identity-to-LF) is the safer batch-2 successor and is already
   mechanism-preempted by Fixup, so its card must claim only the MF composition.
7. **Keep §12.2's data-defect branch live.** If per-band coherence between LF and HF is
   low even at k→0, or the interface-distance stratification shows a systematic
   offset, the honest output is a dataset bug report to the mentor (program.md §13.4),
   not a model. No retrieved source distinguishes solver-legitimate LF/HF decorrelation
   from a pairing bug — the diagnostic must therefore include a same-parameter-vector
   sanity check on a handful of pairs.
