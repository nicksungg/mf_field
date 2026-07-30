# Iteration 3 — `s7_loss` batch 2

## Search rationale

Two structural facts from iterations 1–2 reshape the candidate set. (i) The
denominator floor is already shipped in the B1 family, so the "repair the
relative loss" branch reduces to the λ knob. (ii) The scored functional is
`mean_i ‖p_i − y_i‖ / ‖y_i‖` — **unsquared** (program.md §2.1) — while
`MFFP_S7_LOSS=rel` implements `mean_i rel_i²`. Those are different per-sample
gradient weightings, and the unsquared one is (I suspect) the *standard*
neural-operator training loss. This turn checks that, and opens the direction
the round's own structure suggests but the MF literature has not shown:
per-sample loss weighting by the **copy-LF residual** (the scored skill's
denominator), which — being a fixed per-sample constant — is convex in `p` and
so cannot reproduce B1's origin stationary point.

## Search terms used

1. `neuraloperator LpLoss relative L2 loss definition size_average unsquared standard FNO training loss implementation`
2. `skill score loss function training neural network normalize loss by baseline persistence climatology error weather forecasting`
3. `per-sample loss weighting inverse baseline error difficulty normalization heteroscedastic scientific machine learning surrogate training`

## Findings

### Term 1 — is unsquared relative-L2 the standard operator-learning loss?

Top results: `https://neuraloperator.github.io/dev/auto_examples/models/plot_SFNO_swe.html`,
`https://github.com/neuraloperator/Geo-FNO/blob/main/airfoils/naca_interp_fno.py`,
`https://arxiv.org/html/2412.10354v2` (A Library for Learning Neural
Operators), `https://github.com/neuraloperator/markov_neural_operator/`.

The returned material confirms `LpLoss` is the library's training loss and is
parameterized by `size_average` / `reduction` and order `p` (the SFNO example
uses `LpLoss(d=2, p=2, reduction="sum")`). **Fetch of
`https://arxiv.org/html/2412.10354v2` failed to resolve the definition**: the
paper says only that the library "provides common loss functions for training
neural operators" and does not give the formula; the fetch explicitly reports
no `LpLoss`/`H1Loss` formulation, no statement of per-sample norm ratios, and
no epsilon/clamping discussion. So the *practice* is visible but the
*definition* is not yet grounded in a fetched source — carried into iteration 5
as a targeted fetch.

### Term 2 — baseline/skill-normalized training objectives

Top results: `https://glossary.ametsoc.org/wiki/Skill`,
`https://www.cawcr.gov.au/projects/verification/`,
`https://jua.ai/articles/atmospheric-model-skill-scores/`,
`https://arxiv.org/pdf/2411.11268` (ACE2), `https://arxiv.org/pdf/2505.10191`.

Every hit treats skill as a **verification metric**: `SS = 1 − MSE_forecast /
MSE_reference` (MSSS against climatology or persistence), the exact structure
of our panel skill. The only training-side statement returned is a caution that
"when using loss functions based on forecast skill over autoregressive steps,
it is not guaranteed that lower loss will lead to small long-term climate
biases" — i.e. skill-shaped losses exist in weather ML rollouts, but the
returned hits give no per-sample construction and I could not attribute the
sentence to a fetched page this turn. No hit weights each *training sample* by
its own reference-baseline error. Carried to §3.3.

### Term 3 — per-sample weighting precedents

Top results: `https://arxiv.org/abs/2107.04497` (Batch Inverse-Variance
Weighting: Deep Heteroscedastic Regression),
`https://www.emergentmind.com/topics/weighted-loss-function`,
`https://iopscience.iop.org/article/10.1088/2632-2153/ac3712` (Inverse
Dirichlet weighting for PINNs), `https://www.emergentmind.com/topics/normalized-loss-function`.

**Fetched** `https://www.emergentmind.com/topics/weighted-loss-function`:
per-sample weighting is documented as serving "cost-sensitive learning,
**metric optimization**, or correcting non-i.i.d. sampling"; the named
per-sample constructions are metric-optimized bilevel meta-learned weights
(Zhao et al. 2018) and an auxiliary weight network (Mellatshahi et al. 2023).
Crucially it records a **failure mode we must pre-register**: "excessive
boosting of rare examples … can destabilize training, overfit low-frequency
patterns, or distort global performance", requiring "careful weight clipping …
or domain-informed tuning". The page states inverse-variance, amplitude
normalization and **baseline-error formulations are not elaborated**.

**Fetched** `https://arxiv.org/abs/2107.04497` (abstract only — the landing
page carries no formula): BIV "adapt[s] an inverse-variance weighted mean
square error, based on the Gauss-Markov theorem, for parameter optimization on
neural networks" and is "robust to near-ground truth samples". This is the
closest published relative of a fixed per-sample weight `w_i` in a squared
loss, but its `w_i` comes from **label noise variance**, not from a
reference-model error, and the fetch could not supply the formula.

Also noted from the returned summaries (not fetched, not citable): "per-curve
normalization makes loss insensitive to absolute amplitude" in surrogate
training — the same idiom, again presented as practice rather than method.

## Interpretation

Per-sample weighting is a well-populated *idiom space* (inverse-variance,
metric-optimized, auxiliary-network) with a documented destabilization failure
mode, but **weighting by the per-sample error of a reference/baseline model** —
which is exactly the panel's skill denominator and is available in this
benchmark as the copy-LF field — did not appear in any of nine returned hits
across two independent framings.

**ENOUGH** on field context declared here: three turns have mapped the
normalized-loss, weighted-loss, MF-loss and skill-score literatures and the
returns are now repeating (`emergentmind/normalized-loss-function` surfaced in
three separate turns). Iterations 4–5 are spent entirely on §3.3 refutation.
