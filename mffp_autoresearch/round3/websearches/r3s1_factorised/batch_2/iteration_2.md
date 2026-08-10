# Iteration 2 — two-population / non-identifiable subpopulation structure

## Search rationale

The mechanism handoff's fourth finding is a *methodological* object, not an architecture: cahn_hilliard's 100-row test set splits into a seed-invariant 27/73 partition with an **empty band** in the per-row error histogram (0.62–0.99); the 27 are near in condition space (max 0.448 sigma/dim, NN-distance ratio 1.018) and 3.3x far in field space, so every condition-only arm scores them worse than `ref_zero`.
If batch 2 wants to *claim* this (rather than merely report it), the claim is "a benchmark cell can be certified condition-incomplete on an identified subpopulation".
This turn asks whether that diagnostic — and its PDE-surrogate framing (aleatoric floor from non-identifiable inputs) — is established.

## Search terms used

1. `bimodal error distribution neural operator test set subpopulation irreducible error parameter incompleteness PDE surrogate` — **TOOL ERROR: "Web search error: unavailable". No results returned; re-attempted under a different phrasing in iteration 3.**
2. `detecting missing input variables hidden latent factor regression subpopulation worse than mean predictor diagnostic`
3. `aleatoric uncertainty conditional mean floor parametric PDE benchmark non-identifiable inputs surrogate model limit`

## Findings

### Term 1

No usable results — search backend error (recorded above), not a null.

### Term 2 — missing-covariate / latent-group diagnostics (statistics side)

Returns are the **missing-data and latent-factor** literature, not the surrogate literature: MNAR latent-factor approaches [https://naijialiu.github.io/pics/LFA_21.pdf], factor analysis with missing data [https://arxiv.org/pdf/1801.03851], Bayesian data reweighting as a model-mismatch *diagnostic* [https://arxiv.org/pdf/1606.03860], sparse probabilistic PCA process monitoring [https://arxiv.org/pdf/1904.09514].
The one conceptually exact match returned as a snippet is the textbook unmeasured-group example — predicting a trait "much higher for men than women" without the gender covariate lets the regression "only capture one hereditary group, thus misrepresenting both groups" (snippet only, from the logistic-regression-with-missing-covariates return [https://arxiv.org/pdf/1805.04602]).
Interpretation: **omitted-variable-induced subpopulation failure is classical statistics**, so the *phenomenon* is certainly not novel; nothing returned instantiates it as a benchmark-certification procedure on PDE fields.
Not fetched (the class is clear from the returns and none would be the citation of record).

### Term 3 — aleatoric floors for parametric-PDE surrogates (one fetch)

**FETCHED** — Song et al., *Structure-Aware Epistemic Uncertainty Quantification for Neural Operator PDE Surrogates*, arXiv:2603.11052, 24 Feb 2026 — [cite: https://arxiv.org/abs/2603.11052].
Verbatim scope from the fetched abstract: it targets **epistemic** uncertainty "due to finite data, imperfect optimization, and distribution shift", by restricting MC sampling to the lifting module; benchmarks are discontinuous-coefficient Darcy and geometry-shifted 3D car CFD.
It is an *uncertainty-band* method, not a subpopulation-identification method, and it does not treat input incompleteness.
Corroborating snippet from the same turn: work in this area "do[es] not explicitly model **aleatoric** uncertainty" in largely-deterministic PDE settings, and "for a surrogate model with **non-identifiable parameters**, the algorithm would potentially have to deal with multimodalities" (snippet only, from the returns for [https://paulbuerkner.com/publications/pdf/2504.02919] / [https://arxiv.org/pdf/2504.02919] cluster).
Interpretation: the PDE-surrogate UQ literature returned here is epistemic-first; a certified *aleatoric floor caused by an incomplete condition vector, localised to named rows*, did not appear.

## Interpretation

The underlying statistics (omitted variable → a subpopulation the model cannot serve) is old and unclaimable, and PDE-surrogate UQ work returned so far is epistemic and band-shaped rather than subpopulation-identifying.
The sharpest remaining preemption risk for this direction is the ML **slice-discovery / subpopulation-shift** literature, which term 1's tool error prevented reaching — that is iteration 3's first job, together with the gated-residual-correction direction.
