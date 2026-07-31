# Iteration 4 — §3.3 refutation pass and prior-art verdicts

## Search rationale

`ENOUGH` was declared at the end of iteration 3 (field context converged: three turns returned
the same structure). This iteration is spent entirely on refuting novelty for the four
candidate directions the brainstormer can propose from B1's part 7:

- **D1** realisation-aware (stochastic / ensemble) stage-1 pseudo-LF feeding the real-LF-trained
  corrector, falsification pre-registered in coherence units (part 7 option A);
- **D2a** factorised amplitude x normalised-shape head for `ext__helmholtz_2d`, and **D2b**
  closed-form linear/POD+ridge head for `ifc_poisson` (part 7 option B, run as condition→HF);
- **D3** the training-free coherence eligibility precondition as a round-level rule
  (`cross_stream_notes` item 3);
- **D4** the closure claim that a deterministic intermediate is a re-parameterisation and the
  stacked class is dead on this benchmark (I8).

Each got at least one search whose GOAL was to find the work that preempts it.

## Search terms used

1. `stochastic sample surrogate input to correction network trained on true simulations input distribution mismatch fine-tune on generated inputs PDE` (targets D1)
2. `separate amplitude magnitude and normalized shape prediction output head neural operator scale-aware loss parametric PDE surrogate` (targets D2a)
3. `training-free criterion predict whether error correction stage will improve surrogate before training go/no-go correctability test` (targets D3)

D2b and D4 were refuted in iteration 3 (terms 1 and 2 respectively) and are carried forward.

## Findings

### Term 1 (D1) — surrogate-generated inputs into a corrector trained on real solves

No usable results for the exact composition. Returns were about probabilistic surrogates in
general and about *training-data coverage* rather than stacked-input mismatch:

- "Learning Where to Simulate: Generative Active Sampling for Online PDE Surrogate Training" —
  https://arxiv.org/pdf/2606.09949 (snippet-level): the mismatch discussed is that "precomputed
  datasets may not adequately cover informative regions of the solution space"; the fix is
  streaming solver data during training — a *data-coverage* argument, not an
  input-realisation-shift argument.
- "Generative Neural Operators through Diffusion Last Layer" —
  https://arxiv.org/pdf/2602.04139 (snippet-level).
- "A numerical study into neural network surrogate model performance for uncertainty
  propagation" — https://arxiv.org/html/2605.16078 (snippet-level).
- Conditional-moment matching (CMMD) for stochastic surrogates was mentioned by the engine
  without a resolvable primary URL — NOT cited.

Combined with iterations 1 and 3 (which found only deterministic-operator → generative-corrector
orderings, and LF-at-test generative refiners): **no fetched source synthesises an LF-fidelity
field from a parameter vector and feeds it to a corrector trained on real coarse solves.**

### Term 2 (D2a) — amplitude x shape factorisation

- **[VERIFIED, abs fetched — and it CORRECTS a bad PDF fetch]** "Scale-Consistent Learning for
  Partial Differential Equations" — https://arxiv.org/abs/2507.18813. A first fetch of
  https://arxiv.org/pdf/2507.18813 returned an unsupported reading ("scale refers to the
  amplitude/magnitude of the solution ... the method does factorize predictions into magnitude
  and normalized components", hedged with "likely"/"suggests") from an 8.7 MB binary PDF. The
  abstract fetch refutes it: the paper's "scale" is **domain size** — "a given domain can be
  re-scaled to unit size, and the parameters and the boundary conditions of the PDE can be
  appropriately adjusted"; the contribution is a scale-consistency data-augmentation loss and a
  scale-informed neural operator (tested on Burgers, Darcy, **Helmholtz**, Navier-Stokes; 34%
  average error reduction). The PDF reading is DISCARDED. (Batch-1's dead-end lesson repeats:
  never trust a large-PDF WebFetch summary.)
- "Multiscale Neural PDE Surrogates for Prediction and Downscaling" —
  https://arxiv.org/html/2507.18067v1 (snippet-level): evaluates band-partitioned spectra, does
  not factorise an amplitude head.
- No source found that predicts a scalar amplitude and a unit-norm field separately for a
  resonance-dominated parametric problem. Nearest published neighbour remains iteration 2's HNO
  — "bounded multiplicative gating on per-mode coefficients", https://doi.org/10.3390/app16125997
  (snippet-level).

### Term 3 (D3) — training-free correctability criterion

**No usable results.** Vocabulary collision: "go/no-go" returns neuroscience task literature;
the engine itself stated the specific framework "isn't addressed" by the returns. The only
adjacent hit is "Error modeling for surrogates of dynamical systems using machine learning" —
https://arxiv.org/abs/1701.03240 (snippet-level, not fetched), which models surrogate error
rather than predicting whether correction is worthwhile. The binding prior art for D3 therefore
remains iteration 1's FreqNO-DPS (https://arxiv.org/html/2606.03936) plus the time-series SCP
metric (https://arxiv.org/pdf/2509.23074).

## Prior-art verdicts

**D1 — realisation-aware stage 1 (stochastic/ensemble pseudo-LF) → real-LF-trained corrector,
falsified in coherence units.** `preempted-but-MF-composition-open (cite)`.
Published pieces: conditional generative LF→HF surrogates requiring a real LF solve at test
(Geneva & Zabaras, https://arxiv.org/abs/2006.04731, snippet-level; MFFM,
https://arxiv.org/html/2605.16118, VERIFIED: *"MFFM operates downstream of S_LF"*, no frozen
stage, all levels "optimized jointly"); probabilistic condition→HF multi-fidelity flows with LF
used only for pretraining (https://arxiv.org/html/2602.00072, VERIFIED: only parameters needed
at test, "no separate downstream model"); generative-corrector-downstream-of-operator ordering
(https://arxiv.org/pdf/2507.02106, snippet-level; FreqNO-DPS
https://arxiv.org/html/2606.03936, VERIFIED). **Open**: the specific topology
(parameter → *sampled* LF realisation → corrector trained on REAL coarse solves) and the
coherence-threshold acceptance criterion appear in no fetched source. **Strong negative prior
the brainstormer must confront, not ignore**: the field's standard defence of a pointwise metric
under a generative stage is the K-sample posterior mean
(`docs/reports/MF_Sharp_HighFreq_Report.md` lines 203/317, PDE-Refiner arXiv:2308.05732), which
IS the conditional mean B1 already measured at gamma_b1 <= 0.52; and a sample drawn independently
of the test row's realisation has coherence 0 with it in expectation. Composition open, outcome
predicted negative.

**D2a — factorised amplitude x normalised-shape head for helmholtz (condition→HF).**
`novel (thin — do not make it the claim)`. Nearest neighbours: FaNO
(https://arxiv.org/abs/2606.16900, VERIFIED abstract — factorises transient vs persistent, not
amplitude vs shape, no resonance/Helmholtz mention); scale-consistent learning
(https://arxiv.org/abs/2507.18813, VERIFIED abstract — domain rescaling, includes a Helmholtz
experiment); HNO's per-mode multiplicative gating
(https://doi.org/10.3390/app16125997, snippet-level). No exact match found, BUT
target/output normalisation is generic practice and these three terms did not exhaustively cover
the normalisation literature: propose it as an *implementation of a measured diagnosis* (FiLM
code eff-rank 1.00/1.00/1.00/1.00 while the map is continuous at nn-cosine +0.931), never as an
architectural contribution.

**D2b — closed-form / linear-in-condition (POD + ridge) head on ifc_poisson.**
`preempted (cite)`. [Hesthaven & Ubbiali 2018] "Non-intrusive reduced order modeling of
nonlinear problems using neural networks", JCP 363:55-78 —
https://ui.adsabs.harvard.edu/abs/2018JCoPh.363...55H/abstract /
https://www.sciencedirect.com/science/article/abs/pii/S0021999118301190 (snippet-level: POD
reduced basis from HF snapshots + a network approximating the reduced coefficients as a function
of the parameters, offline/online split, no online HF solve). Related: kernel-POD variant
https://www.sciencedirect.com/science/article/abs/pii/S0898122121003928 (snippet-level); GPR
variant https://arxiv.org/pdf/2103.12472 (snippet-level). **Open**: nothing about the mechanism.
The only open content is the *measurement* — that on this benchmark's 5-dim ifc_poisson condition
the map is affine to 6.2e-08, so a 4.78 M-parameter FiLM-FNO at 0.0821 is losing to a 1970s-class
reduced-basis method by six orders of magnitude, at N_hf = 5. Declare it a BASELINE arm.

**D3 — training-free coherence eligibility precondition for building a corrector.**
`preempted-but-MF-composition-open (cite)`. FreqNO-DPS
(https://arxiv.org/html/2606.03936, VERIFIED) states *"the same diagnostic serves as a
prerequisite check for applying the method to any new surrogate (Appendix B.6)"* and *"we
confirm it for the MIFNO via an off-diagonal cross-spectral coherence diagnostic"*; Spectral
Coherence Predictability is an established predictability surrogate in forecasting
(https://arxiv.org/pdf/2509.23074, snippet-level); in-repo, cross-spectral coherence < 0.7 is
already proposed as a band-cutoff estimator (`docs/reports/MF_Sharp_HighFreq_Report.md` lines
226/295/336). **Open**: FreqNO-DPS's check validates an *assumption of its own filter* (residual
covariance diagonal in Fourier); r2s2's rule is different in kind — a *calibrated threshold on
corrector VALUE* (gamma_b1 >= ~0.95, bracketed by the real→pseudo interpolation experiment) plus
an in-sample oracle-Wiener ceiling as an upper bound on any spatially-invariant linear stage.
No fetched source calibrates coherence against realised corrector value-add.

**D4 — closure claim: a deterministic intermediate is a re-parameterisation; the stacked class is
dead here.** `preempted (cite)` as a principle, open as a measurement. The principle is the data
processing inequality — https://en.wikipedia.org/wiki/Data_processing_inequality,
https://people.ece.cornell.edu/zivg/ECE_5630_Lectures7.pdf,
https://theses.eurasip.org/document/information-loss-in-deterministic-systems/ (all
snippet-level): "post-processing cannot increase information". Corroborating empirical priors
for preferring end-to-end over frozen stages: CALM-PDE §4.3 (batch-1 citation,
https://arxiv.org/abs/2505.12944) and MFFM's joint optimisation of all levels
(https://arxiv.org/html/2605.16118, VERIFIED). **Open**: no fetched source states the DPI
*for stacked PDE surrogates* or measures the resulting ceiling on field-valued multi-fidelity
benchmarks. Claim the measurement; cite the theorem for the principle.

## Interpretation

Iterations 1-4 never found the option-(A) topology, so its composition is open — but three
independent lines (K-sample-mean practice, independent-sample coherence, the DPI) predict it
fails, and B1 already measured the oracle ceiling on cahn_hilliard at ~1.6 skill units against a
14.08 panel geomean. Option (B)'s ifc_poisson half is squarely preempted by classical
non-intrusive reduced-basis modelling and should be run as a declared baseline whose interest is
the measurement; option (B)'s helmholtz half has no exact match but is architecturally thin.
Cap not hit (4 of 5 iterations).
