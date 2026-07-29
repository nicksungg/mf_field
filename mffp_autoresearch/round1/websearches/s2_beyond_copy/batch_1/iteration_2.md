# Iteration 2 — s2_beyond_copy / batch 1

## Search rationale

Iteration 1 closed the spectral half of the diagnostic (FreqNO-DPS `rFFT`/`H(k)`,
2606.03936) and closed the "identity init is novel?" question (it is not — Fixup).
Three gaps remain before a diagnostic can be specified:
(a) is *"skill relative to a copy-the-input reference"* an established evaluation
protocol anywhere, so the stream's metric convention is defensible and its novelty
claim is honest (program.md §13.3);
(b) the **spatial** half of the diagnostic — is there a citable interface-localized
error metric (error stratified by distance to the interface) for phase-field /
sharp-interface fields, which is what four of the five panel datasets are;
(c) is **LF/HF cross-spectral coherence vs wavenumber** an established MF diagnostic,
which the in-repo report proposes (MF_Sharp_HighFreq_Report §3.3, k_c at coherence
~0.7) but never cites a source for.

## Search terms used

1. `skill score forecast reference baseline persistence "worse than" surrogate must beat coarse solution multifidelity operator learning evaluation protocol`
2. `interface-localized error metric sharp interface phase field neural network narrow band signed distance evaluation diffuse interface`
3. `cross-spectral coherence low-fidelity high-fidelity correlation diagnostic predict when multifidelity helps wavenumber`

## Findings

### Term 1 — skill relative to a trivial reference

Results are dominated by meteorology/forecasting, not by operator learning:
PV intraday forecasting (https://arxiv.org/pdf/2303.08459), rolling-origin PM10
validation vs persistence (https://arxiv.org/pdf/2603.20315), M-ENIAC
(https://arxiv.org/pdf/2304.09070), proper scoring rules (ResearchGate 4742807),
AI surrogates for multiscale combustion (https://arxiv.org/pdf/2604.25617).

- The **skill-score convention itself is standard and old**: performance is expressed
  as relative improvement over a reference (climatology / persistence), "a perfect
  forecast yields 1, no improvement over the reference yields 0, and performance
  worse than the reference yields negative values"; the persistence (random-walk)
  baseline is literally *"the next value equals the most recently observed value"* —
  i.e. **copy the input**. So MFFP's copy-LF skill is the operator-learning transcript
  of forecasting's persistence skill.
- **No usable results** for an operator-learning / multi-fidelity paper that adopts a
  copy-the-LF-input reference. No fetch was worth spending here: the returned corpus
  is off-domain (energy/air-quality forecasting), and none of the MF or NO hits from
  iteration 1 used such a reference either.
- Reading: the *metric convention* is fully published (persistence skill, 1950s
  meteorology); what appears undocumented is its **application to multi-fidelity
  operator learning**, where the trivial reference is the model's own LF input field.

### Term 2 — interface-localized error

Results: medial-axis-aware SDF learning (https://arxiv.org/html/2604.16512); PINNs
for level-set interface advection
(https://iopscience.iop.org/article/10.1088/2632-2153/ae8b74); residual-attention
PINN for irregular interfaces (https://arxiv.org/html/2603.22803); phase-field neural
solver for moving contact lines (https://arxiv.org/html/2607.19690); sharp interface
tracking with the phase-field equation
(https://beckermann.lab.uiowa.edu/sites/beckermann.lab.uiowa.edu/files/2023-10/YingJCP.pdf);
Metric-Phase Fields (https://arxiv.org/html/2605.25503).

- The community's framing is consistent and useful, though it is stated as *sampling*
  strategy rather than as an evaluation metric: *"the important features of moving
  contact line dynamics are concentrated near the diffuse interface, and standard
  collocation sampling may miss these localized regions or require a very large
  number of points"* [https://arxiv.org/html/2607.19690]; and *"the sharp phase-field
  interface is difficult to represent with standard neural network outputs, since the
  order parameter changes rapidly across a thin diffuse layer"*.
  Residual-attention structures are reported to give *"more localized error
  distributions"* [https://arxiv.org/html/2603.22803].
- **No usable results for a named, standard "error vs distance-to-interface"
  evaluation metric.** The narrow-band idea is ubiquitous in level-set numerics as an
  algorithmic device, but the searches did not return a paper that reports
  neural-surrogate error *stratified by* signed-distance band as a diagnostic.
  Consequence: the batch-1 diagnostic can define this stratification without fear of
  duplicating a named metric, but must state plainly that the narrow-band device
  itself is classical.

### Term 3 — cross-spectral coherence as an MF diagnostic

Results: multi-scale coherence of represented flows (https://arxiv.org/pdf/2605.26412);
MIT OCW 12.864 notes on cross-spectra and coherence
(https://ocw.mit.edu/courses/12-864-inference-from-data-and-models-spring-2005/aa69dfa26f8aa32ad1c528f6c5318faf_tsamsfmt_1_18.pdf);
MathWorks cross-spectrum & magnitude-squared coherence doc; spectral estimation for
spatial point processes and random fields (https://arxiv.org/pdf/2312.10176);
cyclostationary blog on the spectral coherence function.

- **Definition, from the search-result synthesis of the MIT OCW notes + MathWorks
  doc:** cross-spectral densities standardized give **complex coherence — "the
  wavenumber-domain correlation between two processes"**; the modulus is magnitude
  coherence, the argument is phase. **Magnitude-squared coherence "measures the
  fraction of variance in one series at frequency f that is linearly predictable from
  the other series at the same frequency … the frequency-domain analogue of squared
  correlation"**, and *"phase estimates in the cross spectrum are only useful where
  significant frequency-domain correlation exists."*
  **WebFetch of the MIT OCW PDF → no usable results** (returned undecoded PDF
  streams); the definition above therefore rests on the search-result text of that
  page plus the MathWorks documentation page, and is standard textbook material, not
  a novel claim.
- **Multi-Scale Coherence of Represented Flows [cite: https://arxiv.org/pdf/2605.26412]
  (FETCHED).** Defines *multi-scale coherence* in a wavelet/multi-scale decomposition
  framework: decompose both a **represented (reduced) flow field and a reference
  field**, then quantify agreement **at each scale independently**. It is offered
  precisely to *"identify which scales or spatial frequencies are well-captured by a
  represented flow model versus where significant information loss occurs"* and to
  distinguish faithful scales from scales needing improvement. This is the closest
  published analogue of "per-band LF-vs-HF trust" as a *diagnostic*.
- Notable negative: the search engine's own synthesis states the results contain
  **no** information about *when* multi-fidelity approaches help as a function of
  LF/HF coherence. The MF-specific application of coherence-vs-k remains
  undocumented in what this loop retrieved.

## Interpretation

Both halves of the batch-1 diagnostic rest on standard, citable machinery — per-scale
coherence between a reduced and a reference field [2605.26412], magnitude-squared
coherence as the wavenumber-domain analogue of squared correlation (MIT OCW /
MathWorks), and per-band `rFFT`/`H(k)` bias [2606.03936] — while the *composition*
(applying them to LF-vs-model-vs-HF triples under a copy-LF skill reference) is not
retrievable in the literature this loop reached. The spatial half has no named metric,
so it can be defined here provided the classical narrow-band precedent is
acknowledged.
