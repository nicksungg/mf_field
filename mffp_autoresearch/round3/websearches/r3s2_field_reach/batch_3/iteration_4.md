# Iteration 4 — refutation pass 1: is "fit on the real intermediate, deploy on the generated one" a named regime in a physical-field science?

## Search rationale

Candidate directions for this batch (from the operator-fixed scope + B2 part 7):

- **D1** — the **emulator-ceiling ladder**: one FROZEN corrector scored on real-LF (oracle) inputs vs the emulator's pseudo-LF inputs across all scored cells, decomposing the stack's error into an ESTIMATOR term and a HALLUCINATION term.
- **D2** — **selection-input repair**: choose the corrector's regularisation on the EMULATOR's held-out output rather than on real LF.
- **D3** — use the ceiling **ratio** as a prospective decision instrument for whether the LF intermediate deserves its place in the graph (replacing a route contrast).

This iteration attacks D2 and the field-science half of D1. Iteration 3 found the mismatch in TTS; the sharper refutation question is whether a *physical-field* discipline has a standing name for training a downstream statistical model on real fields and deploying it on model-generated fields. Climate downscaling does — "perfect prognosis" vs "model output statistics" — so that is the term to run.

## Search terms used

1. `perfect prognosis versus model output statistics downscaling trained on reanalysis applied to GCM predictors mismatch bias`
2. `super-resolution neural network trained on real coarse simulations applied to emulator-generated coarse fields error attribution scientific machine learning`

## Findings

### Term 1 — Perfect Prognosis vs MOS: D2's regime is a fifty-year-old named dichotomy

Returned: <https://arxiv.org/pdf/2305.00974> (Deep generative models for PP climate downscaling), <https://gmd.copernicus.org/articles/13/2109/2020/> (GMD, deep-learning downscaling intercomparison), <https://www.cambridge.org/core/books/abs/statistical-downscaling-and-bias-correction-for-climate-research/perfect-prognosis/EA5518A3E857615670A0D8BC3A1E027E> (Maraun & Widmann textbook, ch. 11 "Perfect Prognosis"), <https://journals.ametsoc.org/view/journals/clim/27/1/jcli-d-13-00063.1.xml> (MOS downscaling of GCM precipitation), <https://www.researchgate.net/publication/246872410_MOS_Perfect_Prog_and_Reanalysis>.

**Fetched — arXiv:2305.00974, "On the use of Deep Generative Models for Perfect Prognosis Climate Downscaling"** (PDF, 17,810 chars), verbatim: *"we focus on a specific type of SD, named the **'Perfect' Prognosis (PP)** approach. PP downscaling leans on **observational datasets** to learn empirical relationships linking the predictors and the predictands. For the former, **reanalysis data** … is typically used … **Once the relationship is established in these 'perfect' conditions, we feed the model/algorithm with the equivalent GCM predictor variables** to obtain high-resolution climate projections."*

That is D2's regime exactly, with our nouns substituted: fit the downstream map under "perfect" conditions (real coarse solve ↔ our `R3S2_CORRECTOR_FIT_ON=real_lf`), then deploy it on *model-generated* predictors (our `R3S2_LF_INPUT=pseudo`). The alternative branch of the dichotomy — **Model Output Statistics**, i.e. fit the statistical relationship directly on the *model's own output* — is precisely the repair component (b) proposes, and it predates ML entirely (engine snippet, Journal of Climate 2014 / MOS-Perfect-Prog-Reanalysis literature; textbook chapter above). Engine summary, snippet-level: PP's known failure mode is that *"training on reanalysis predictors but applying the model to GCM predictors … can differ systematically"* and *"may produce implausible projections and alter the original global climate model signal"*; *"the MOS approach is preferred only when the predictor and predictand resolution gap is small"* — i.e. the community's own answer to "PP or MOS?" is regime-dependent and empirical, which is what the card would be measuring.

### Term 2 — SciML super-resolution: the ceiling principle is stated but not measured as a split

Returned: <https://arxiv.org/pdf/2301.10937> (Fukami, Fukagata & Taira, "Super-resolution analysis via machine learning: a survey for fluid flows"), <https://arxiv.org/html/2509.20683v1>, <https://iopscience.iop.org/article/10.1088/2632-2153/ada19f>, <https://arxiv.org/html/2310.06929v2>, <https://arxiv.org/html/2605.09004> (Separate Universe Super-Resolution Emulator), <https://arxiv.org/pdf/2510.16904>.

**Fetched — arXiv:2301.10937** (PDF, 99,195 chars), verbatim: *"For super-resolution analysis to reconstruct a physically accurate high-resolution flow field, **it is generally necessary that the low-resolution input data is accurate on its own coarse grid**. If the coarse flow field input is provided by some turbulent flow simulation (e.g. LES, DES, RANS), **it is important that the coarse flow be accurate to begin with. The super-resolved field would not be physically accurate if the low-resolution flow field (input) is deviated from the true solution.**"*

This is the *statement* of the emulator ceiling for exactly our topology (upstream coarse field → downstream super-resolver), from a survey. What it is **not** is a measurement: the survey asserts the dependence qualitatively and never runs the same frozen super-resolver on true-coarse vs simulated-coarse inputs to price the two terms. Engine summary on the same term reinforces the asserted-but-unmeasured status: *"Super-resolution result accuracy is limited by how accurate the training set was … super-resolution can only be as good as its training data fidelity."*

## Interpretation

D2 is **preempted at the level of the concept and the name**: perfect prognosis vs model output statistics is the standing dichotomy for "fit on real intermediates, deploy on generated ones" vs "fit on generated ones", in a field science with physical fields, decades before ML. D1's *principle* is likewise stated in the SciML super-resolution survey — but as an admonition, not a measured decomposition, and never with a *hallucinated* (condition-generated, non-solver) coarse field. Iteration 5 must make the last refutation attempt on D1's measured form and on D3's use of the ratio as a decision rule.
