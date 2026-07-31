# Iteration 3 — verify the classical baseline, the I8 information argument, and generative MF pipelines

## Search rationale

Iteration 2 left three things owed. (1) The ifc_poisson closed-form head looked like classical
non-intrusive reduced-basis modelling but PODNO turned out NOT to be that prior art, so the
Hesthaven-Ubbiali line needed a direct check. (2) B1's I8 — "a deterministic pseudo-LF is a
re-parameterisation, never an information channel" — is proposed in the card's
`cross_stream_notes` as a ROUND-LEVEL constraint; if it is just the data-processing inequality
then the brainstormer must present it as an application of a textbook theorem, not a finding.
(3) Option (A) needs its true nearest neighbour: multi-fidelity *generative* pipelines, and
specifically whether any of them synthesises the LF field from parameters and hands it to a
downstream stage.

## Search terms used

1. `Hesthaven Ubbiali non-intrusive reduced order modeling neural networks POD coefficients parameter regression 2018`
2. `deterministic intermediate representation adds no information data processing inequality cascaded surrogate equals direct model`
3. `conditional generative model of low-fidelity coarse solution given parameters multi-fidelity data augmentation synthetic low fidelity samples`

## Findings

### Term 1 — the classical parameter → POD-coefficient method

- [Hesthaven & Ubbiali 2018] "Non-intrusive reduced order modeling of nonlinear problems using
  neural networks", J. Comput. Phys. 363:55-78. Bibliographic record:
  https://ui.adsabs.harvard.edu/abs/2018JCoPh.363...55H/abstract (fetched — ADS returned an
  empty body, no abstract text); publisher page
  https://www.sciencedirect.com/science/article/abs/pii/S0021999118301190 (403 under WebFetch,
  batch-1 known dead end); ResearchGate mirror
  https://www.researchgate.net/publication/323409071 (403). Method description returned
  consistently by the search engine across both this term and iteration 2's term 3: "extracts a
  reduced basis from a collection of high-fidelity solutions via a proper orthogonal
  decomposition (POD) and employs artificial neural networks, particularly multi-layer
  perceptrons (MLPs), to accurately approximate the coefficients of the reduced model", with an
  offline routine (LHS + Levenberg-Marquardt) that searches for "the minimum amount of training
  samples to avoid overfitting". **Status: snippet-level, corroborated by three independent
  index records (ADS, ScienceDirect, Google Scholar lookup
  https://scholar.google.com/scholar_lookup?title=Non-Intrusive+Reduced+Order+Modeling+of+Nonlinear+Problems+Using+Neural+Networks);
  the abstract itself could not be fetched.** No claim beyond "parameter → POD coefficients,
  no online high-fidelity solve" is made from it.
- Adjacent, arXiv-fetchable if a verified citation is later required: "Non-intrusive reduced
  order modeling of parametric electromagnetic scattering problems through Gaussian process
  regression" — https://arxiv.org/pdf/2103.12472 (snippet-level).

### Term 2 — is I8 the data-processing inequality?

- Data processing inequality — https://en.wikipedia.org/wiki/Data_processing_inequality
  (snippet-level): "post-processing cannot increase information"; deterministic processing
  cannot increase the information contained in a random variable.
- "Information Loss in Deterministic Systems" (EURASIP thesis) —
  https://theses.eurasip.org/document/information-loss-in-deterministic-systems/
  (snippet-level).
- Cornell ECE 5630 Lecture 7 notes on the DPI —
  https://people.ece.cornell.edu/zivg/ECE_5630_Lectures7.pdf (snippet-level).
- No source found that states the DPI *specifically for stacked PDE surrogates* (i.e. "a
  learned intermediate field cannot beat a direct model of equal capacity"), nor one that
  measures it on field-valued multi-fidelity benchmarks.

### Term 3 — multi-fidelity generative pipelines

- **[VERIFIED, fetched]** "Multi-Fidelity Flow Matching: Cascaded Refinement of PDE Solutions"
  (MFFM) — https://arxiv.org/html/2605.16118. Fetch answer, verbatim quotes: *"MFFM operates
  downstream of S_LF and exploits u_LF as an informative summary of u_HF; the map we learn is
  the conditional refinement u_LF -> u_HF"*; the first cascade level's conditioning input is
  "the observed coarse input field or coarse past-frame block" — i.e. **a real LF solve is
  required at inference**; and *"All level networks are then optimized jointly"* — no frozen
  stage. So MFFM is a round-1-regime method, and its end-to-end training is another data point
  against frozen stacking. (MFFM is [N2]/§3.3 in
  `docs/reports/MF_Leaderboard_Beaters_2026_Report.md` — cited there, inference-input question
  answered here.)
- **[VERIFIED, fetched]** "Generative AI-enhanced Probabilistic Multi-Fidelity Surrogate
  Modeling Via Transfer Learning" — https://arxiv.org/html/2602.00072. Surjective normalizing
  flow pretrained on abundant LF to learn p(y_LF | theta), then fine-tuned on scarce HF to
  approximate p(y_HF | theta): *"the LF model is first pretrained on a large LF dataset ...;
  (ii) the pretrained model is then fine-tuned on a small HF dataset, allowing it to correct for
  LF-HF discrepancies via knowledge transfer."* Fetch confirms **at test time only parameters
  are required, no LF evaluation**, and there is **no separate downstream model** — the flow IS
  the predictor. This is exactly the round-2 regime and exactly r2s3's declared-baseline
  mechanism (LF-pretrain → HF-finetune), in its *probabilistic* form.
- "Multi-fidelity Generative Deep Learning Turbulent Flows" (Geneva & Zabaras) —
  https://arxiv.org/abs/2006.04731 (snippet-level; already cited in
  `docs/reports/MF_Sharp_HighFreq_Report.md` line 188): conditional invertible NN generating HF
  given "the solution of a computationally inexpensive but inaccurate low-fidelity solver" —
  again LF-at-test.
- "Generative multi-fidelity modeling and downscaling via spatial autoregressive transport
  maps" — https://arxiv.org/html/2509.22474v1 (snippet-level).

**ENOUGH** declared after this iteration: three independent turns have returned the same
structure (LF-at-test generative refiners, or single end-to-end condition→HF generative models;
never a synthesised LF handed to a frozen real-LF-trained corrector). Iteration 4 is spent
entirely on §3.3 refutation searches and the verdicts.

## Interpretation

The ifc_poisson closed-form head is the 2018 classical non-intrusive RB method modulo replacing
the MLP with a ridge, so it must be declared a baseline. I8 is the data-processing inequality
applied to a stacked surrogate — textbook as a theorem, unmeasured as a benchmark statement, so
the brainstormer may claim the *measurement* but not the *principle*. And the generative MF
literature is uniformly either LF-at-test (MFFM, Geneva-Zabaras) or single-model
condition→HF (arXiv:2602.00072); the specific option-(A) topology — synthesised realisation-aware
LF into a corrector trained on real coarse solves — has not appeared in any of 9 search terms.
