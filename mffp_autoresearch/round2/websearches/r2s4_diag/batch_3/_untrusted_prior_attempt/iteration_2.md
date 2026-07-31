# Iteration 2 — Option B (coverage-greedy support repair) and the training-free regime rule

## Search rationale

B2's Option B proposes, under immutable §5.11 (no new HF data), replacing the nested
random fit-fold prefix with a **coverage-greedy selection at fixed N_fit** on
`sharp__cahn_hilliard` — the panel's one sample-limited dataset (b = 0.2327 accelerating,
d_min 3.1178 in 19 standardised dims). Two prior-art questions follow: (i) is
subset-selection-for-coverage *from an existing pool* published (as opposed to active
learning, which chooses *new* simulations — which §5.11 forbids)? and (ii) is B2's
proposed round-level rule — predict the learning-curve **regime** training-free from
identifiability x support — published? Term 3 attacks (ii) from the learning-curve side,
since if curve *extrapolation* is a mature field then B2's 3-point `c + a N^-b` fit is
preempted method and only the training-free predictor could be new.

## Search terms used

1. `coverage-based subset selection from existing training pool space-filling design neural PDE surrogate fixed budget versus random subsampling`
2. `predict whether more training data will help without training dataset diagnostic learning curve regime nearest neighbor coverage`
3. `learning curve extrapolation predict saturation point machine learning without full training small sample`

## Findings

### Term 1 — coverage-greedy subset selection from a fixed pool

- https://arxiv.org/abs/2012.03541 — "Space-Filling Subset Selection for an Electric
  Battery Model" — **FETCHED**. This is a direct preemption of Option B's *mechanism*.
  The method "selects those dynamic data points that fill the input space of the
  nonlinear model more homogeneously", from an existing (non-uniformly excited)
  measurement dataset, and is "evaluated against two baselines: random subset sampling
  and using all available data points", with the finding that space-filling selection
  "yields higher accuracy compared to random sampling". Domain: NARX battery impedance
  models, not PDE field surrogates; framed as a data-reduction method, **not** as a
  diagnostic of whether a dataset is support-limited.
- https://arxiv.org/abs/2606.09949 ("Learning Where to Simulate: Generative Active
  Sampling for Online PDE Surrogate Training") and
  https://www.sciencedirect.com/science/article/pii/S004578252030760X (ISMO) — both are
  **active learning**: they choose *new* solver runs, which immutable §5.11 forbids. Not
  usable as the design, usable as the contrast ("we cannot generate; we can only
  re-select").
- https://arxiv.org/html/2510.16806 ("Computational Budget Should Be Considered in Data
  Selection", CADS) — budget-constrained subset choice as bilevel optimization; general
  ML, gradient/valuation-based rather than coverage-based. Search result only.
- Search-engine synthesis asserted that coverage-based subset selection and gradient-based
  data valuation are "the two technical families most relevant to training subset
  selection" — SNIPPET only, **do-not-cite**.

### Term 2 — training-free "will more data help?" predictor

**No usable results.** The search returned kNN tutorials (analyticsvidhya, scikit-learn
docs, datasciencebook.ca), two 2000s-era ML patents, and a blog on diagnosing
bias/variance from learning curves. The one research hit,
https://arxiv.org/pdf/2502.15900 ("Explaining the Success of Nearest Neighbor Methods in
Prediction"), is about nonasymptotic guarantees for kNN prediction, not about using kNN
statistics to forecast another model's curve. The search engine stated plainly that the
results "don't contain specific content directly addressing the complete combination of
concepts in your query". This is the **first** dedicated failure for the training-free
regime predictor; a second independent framing is owed in a later turn.

### Term 3 — learning-curve extrapolation and ill-behaved curves

- https://arxiv.org/abs/2103.10948 — Viering & Loog, "The Shape of Learning Curves: a
  Review" — **FETCHED**. Two load-bearing statements. (a) The curve-shape literature is
  mature but *not* universal: the review "expresses... more scepticism towards the idea
  that it has been proven that power laws often provide accurate learning curve models".
  (b) Directly relevant to B2's helmholtz anomaly: the review highlights "examples of
  learning curves that are ill-behaved, showing worse learning performance with more
  training data".
- https://link.springer.com/article/10.1007/s10994-024-06619-7 ("Learning curves for
  decision making in supervised machine learning: a survey") — **FETCH BLOCKED**, 303
  redirect to `idp.springer.com` (same failure mode batch 2 recorded for
  `link.springer.com/chapter/*`; it applies to `/article/*` too). Title only.
- Also returned, not fetched: https://ada.liacs.nl/papers/KieEtAl24.pdf (learning-curve
  extrapolation methods across settings), https://arxiv.org/pdf/2310.20447 (Bayesian LC
  extrapolation with PFNs), https://onlinelibrary.wiley.com/doi/10.1002/sim.10121
  (sample-size determination via learning-type curves).

## Interpretation

Option B's mechanism is **preempted** by space-filling subset selection from a fixed pool
(arXiv:2012.03541), and curve extrapolation/saturation prediction is a mature field, so
B3 must not sell either as new. The genuinely open slots are (a) coverage-greedy
re-selection used as a *diagnostic* that separates support-limited from
information-limited datasets, and (b) the training-free predictor of the regime, which
has now failed one dedicated search. Viering & Loog's "ill-behaved learning curves" is
the citation B2's helmholtz kNN degradation (8.69 -> 20.59 skill as N goes 20 -> 320) has
been missing.
