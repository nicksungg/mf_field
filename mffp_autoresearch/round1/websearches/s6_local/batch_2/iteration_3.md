# Iteration 3 — per-sample trust / selective prediction for correctors (topic (c))

## Search rationale

B1's F3 relocated the whole trust hypothesis: an oracle **per-pixel** map is
worth <= 4.1% and is *harmful* on cahn_hilliard (+17%), whereas an oracle
**per-sample scalar** on the same trained corrector gives pfc -22.8% and
helmholtz 0.1623 vs copy-LF 0.3295 (**skill 0.49 on the one dataset B1 had to
report as a no-op**). Part 7 item (4) therefore proposes a head predicting
`alpha_i` from `(X_i, cheap LF-field statistics)`, fitted on the held-out slice.
The mechanism has three plausible published homes and this turn probes all
three: (i) the ML-native one — **selective prediction / reject-option
regression**, where a model abstains per input; (ii) the MF-native one —
**per-sample trust weighting between a corrected LF value and an HF model**;
(iii) the operator-learning one — **learned error estimators that decide when to
trust a surrogate**. ADR 0009 is the sharp knife here: anything needing the PDE
residual at test time is disqualified as a *model* and can only be prior art for
a diagnostic.

## Search terms used

1. `selective prediction reject option regression neural PDE surrogate per-sample confidence fallback to baseline`
2. `per-sample adaptive blending weight multi-fidelity surrogate learned confidence when to trust correction`
3. `learned error estimator predicts per-sample error of neural operator decide whether to trust surrogate or fall back`

## Findings

### Term 1 — selective prediction / reject option: the generic mechanism is published
- **SelectiveNet (Geifman & El-Yaniv, ICML 2019)**,
  https://ar5iv.labs.arxiv.org/html/1901.09192 (also
  https://proceedings.mlr.press/v97/geifman19a.html) — **FETCHED.** Three heads
  on a shared body: prediction `f`, **selection `g`**, auxiliary `h`; `g` gives
  *"if g(x)=1; don't know, if g(x)=0"*, coverage = *"the probability mass of the
  non-rejected region"*. Two facts matter for us: (1) *"the paper addresses both
  classification and regression"* — selective **regression** is in scope;
  (2) **"All heads train jointly on the same data end-to-end ... enforcing the
  coverage constraint during training, not on held-out data."** So the canonical
  selective-prediction design has *exactly the in-sample-selector structure that
  B1's F4/F5 identified as its own protocol defect.*
- Adjacent, search-return only: "Learning to Reject with a Fixed Predictor"
  https://openreview.net/pdf?id=dCHbFDsCZz ; "Selective Nonparametric Regression
  via Testing" https://ar5iv.labs.arxiv.org/html/2309.16412 ; "Model Agnostic
  Explainable Selective Regression via Uncertainty Estimation"
  https://arxiv.org/pdf/2311.09145 . The "fixed predictor" framing (reject on top
  of a FROZEN predictor) is the structural analogue of part 7's "freeze the
  corrector, train the gate on a later fold".
- Explicit negative from the search engine: *"The search results don't contain
  specific information about neural PDE surrogates with per-sample confidence and
  fallback-to-baseline strategies."*

### Term 2 — MF trust weighting: the tightest named threat, and it does not reach fields
- **MAST — "A Multi-fidelity Augmented Surrogate model via Spatial
  Trust-weighting"**, https://arxiv.org/html/2602.20974 — **FETCHED.** Same
  vocabulary as our proposal ("trust weighting", fusing a *corrected LF* value
  with an HF prediction): *"points near high-fidelity samples should favour
  high-fidelity predictions, while distant points should favour corrected
  low-fidelity values"*; fusion
  `y~_i = W_m^(i) (y_i + mu_delta) + (1 - W_m^(i)) mu_M(x_i)`.
  **Three disqualifying differences**: (a) *"MAST is a scalar-output Gaussian
  process surrogate, not a field or operator model. There is no involvement with
  images, PDE solution fields, or spatial grids."* (b) the weight is **purely
  geometric** — *"derived from distance and cost ratios, not learned from data
  features"* (trust radius `r_i = sqrt(d_min)`); (c) it trusts the LF branch
  *far* from HF samples, i.e. it is a design-space extrapolation device, not an
  estimate of whether the defect operator is valid for this sample.
- Context, search-return: correction/discrepancy-function MF fusion "adding
  correction terms to low-fidelity data" is standard
  [https://arxiv.org/pdf/2402.09638 survey; https://arxiv.org/pdf/2212.03375].

### Term 3 — learned error estimators for operators: published, but physics-gated
- **ANCHOR — "Error-Controlled Adaptive Numerical Correction for Neural Operator
  Time Marching"**, https://arxiv.org/html/2512.19643v2 — **FETCHED.** Trigger:
  `eta_t > eta_thres_t`, and then *"the responsibility for time advancement is
  transferred to the high-fidelity numerical solver."* But *"The proposed error
  estimator is inherently physics-informed, being computed from the PDE
  residual"* (`r^_t = ||r_t||_2/||u_t||_2`, EMA-smoothed), and *"Decisions occur
  per-timestep across the entire spatial domain simultaneously—not per-pixel or
  per-sample independently."* **ADR-0009-disqualified as a model** and the wrong
  granularity anyway.
- Same pattern in the residual-based-corrector line (all search-return,
  all physics-requiring): https://arxiv.org/pdf/2306.12047 ,
  https://arxiv.org/pdf/2210.03008 , https://arxiv.org/html/2512.21319
  (a-posteriori error estimation for a reduced-basis neural operator).
- A **data-driven** exception worth a re-check: "A Deep Risk Estimator for Known
  Operator Learning", https://arxiv.org/html/2605.08517 — search-return only,
  not fetched, must not be cited as evidence.

## Interpretation

The generic mechanism (abstain/blend per input) is thoroughly published, but each
published instance misses on a different axis that matters here: SelectiveNet is
selective *regression* with the selector trained **in-sample** (the very defect
B1 diagnosed), MAST is per-sample MF trust weighting but on **scalar GPs with a
purely geometric weight and no fields**, and the operator-side error estimators
(ANCHOR, residual correctors) are **physics-gated** and per-timestep. No fetched
source produces a **data-driven per-sample scalar, fitted on a held-out fold,
that decides whether a field-valued defect corrector should be applied at all**
with a copy-LF fallback. Next turn: the in-sample gate / stacking-leakage
question (topic (d)).
