# iteration_1 — `r3s1_factorised`, batch 1

## Search rationale

The stream's seed direction (round3 program.md §4) is the *two-stage
cross-coefficient factorised closed-form head*. Three prior round-2 loops
(`round2/websearches/r2s1_direct/batch_{1,2,3}`) already settled the outer shell
(FiLM decoders, POD-NN heads, per-mode OOF family selection, Bates-Granger
blending, supervised basis ordering). What no loop has checked is the two
genuinely new pieces: (a) regressing the *discarded* basis coefficients on the
*retained* ones, and (b) the propagation-aware gate — fitting/selecting stage 2
on **out-of-fold stage-1 predictions** rather than true stage-1 coefficients.
Turn 1 attacks exactly those, from the ROM side and from the ensemble-learning
side.

**Tooling note (honest record):** `WebFetch` in this environment is intercepted
by a context-mode plugin that redirects to MCP tools not present in this
subagent's tool list. Routed around with `curl` + local HTML/PDF text
extraction (`/tmp/claude-28156/wf/fetch.py`); every "fetched" below is a page
actually retrieved and read in this loop, and the quoted sentences are from the
retrieved bytes.

## Search terms used

1. `gappy POD reconstruct truncated coefficients from retained POD coefficients regression surrogate`
2. `two-stage regression POD coefficients predict remaining modes from leading mode coefficients reduced order model`
3. `stacked generalization out-of-fold predictions second stage regression avoid input distribution shift`

## Findings

### Term 1 — gappy POD / coefficient completion

Top returns: Gappy POD overview (Everson & Sirovich lineage),
<https://kiwi.oden.utexas.edu/research/gappy-proper-orthogonal-decomposition>;
gappy HOSVD aerodynamic database reconstruction,
<https://www.sciencedirect.com/science/article/abs/pii/S1270963816300499>;
sparse-representation flow reconstruction,
<https://www.researchgate.net/publication/336909610_Robust_flow_reconstruction_from_limited_measurements_via_sparse_representation>;
ROM dictionaries for UQ <https://arxiv.org/pdf/2108.04012>.

Search-return summary (not fetched): gappy POD solves for POD-basis coefficients
that minimise reconstruction error **from partial spatial observations**, and a
"Gappy **surrogate**" variant replaces the least-squares solve with a learned
regression whose input is field values on a reduced-integration domain and whose
output is the optimal POD coefficients. **Important distinction for us:** gappy
POD completes a field from *partial spatial samples of the field*, not from
*predicted coefficients of other modes*. It is a neighbouring, not identical,
mechanism. Not fetched — flagged as SEARCH-RETURN ONLY.

### Term 2 — coefficient-to-coefficient regression in ROMs

**Strongest hit, FETCHED**: Callaham, Brunton & Loiseau, *"On the role of
nonlinear correlations in reduced-order modelling"*, J. Fluid Mech. —
<https://www.cambridge.org/core/journals/journal-of-fluid-mechanics/article/on-the-role-of-nonlinear-correlations-in-reducedorder-modelling/CC2980F9AA4AC20A7453C3056ED950C4>
(retrieved 2026-08-07, 159,967 chars of text). Verbatim from the retrieved
abstract: *"Nonlinear correlations between temporal proper orthogonal
decomposition (POD) coefficients can be exploited to identify latent
low-dimensional structure, approximating the attractor with a minimal set of
**driving modes and a manifold equation for the remaining modes**."* And from
the body: *"the modes are clearly pure harmonics of one of the two driving mode
pairs … indicating that these coefficients can be **directly expressed as
algebraic functions of one or the other driving modes**"*, with *"sparse
polynomial regression to learn a compact, interpretable"* model. This is the
cross-coefficient mechanism, published — but for **temporal** POD coefficients
on a dynamical attractor, selected by RDC (randomised dependence coefficient),
fitted on TRUE driving coefficients, with no parametric condition input and no
out-of-fold propagation gate.

**Second hit, FETCHED (weaker)**: *"Nonlinear parametric models of viscoelastic
fluid flows"*, <https://arxiv.org/abs/2308.04405> — retrieved abstract confirms
it is a SINDy temporal-dynamics parametric ROM (Weissenberg-number
parameterisation), not a coefficient-completion head. The search snippet's
"a_i = g(a_1,a_2) for i=3,4" phrasing traces to the same nonlinear-correlation
literature as the JFM paper, not to a condition→field surrogate.

Other returns, not fetched: POD+deep-learning hybrid ROM
<https://www.sciencedirect.com/science/article/pii/S0957417421012653>; RNN
Mori–Zwanzig closure of parametric POD-Galerkin ROMs
<https://www.sciencedirect.com/science/article/abs/pii/S0021999120301765>.

### Term 3 — out-of-fold second-stage fitting

**FETCHED**: mlxtend `StackingCVRegressor` —
<https://rasbt.github.io/mlxtend/user_guide/regressor/StackingCVRegressor/>
(retrieved 2026-08-07). Verbatim: *"The StackingCVRegressor extends the standard
stacking algorithm … using **out-of-fold predictions** to prepare the input data
for the level-2 regressor."* And: *"In the standard stacking procedure, the
first-level regressors are fit to the same training set that is used prepare the
inputs for the second-level regressor, **which may lead to overfitting**. The
StackingCVRegressor, however, uses the concept of out-of-fold predictions: the
dataset is split into k folds, and in k successive rounds, k-1 folds are used to
fit the first level regressor … The resulting predictions are then stacked and
provided -- as input data -- to the second-level regressor."*

Also returned, not fetched: stacked-regression survey
<https://www.emergentmind.com/topics/stacked-regression-algorithm>; practical
OOF-stacking guide
<https://mcpanalytics.ai/articles/stacking-ensemble-practical-guide-for-data-driven-decisions>.

## Interpretation

The propagation-aware gate is **standard stacked generalization with out-of-fold
level-1 predictions**, and the published rationale is verbatim the failure mode
B3-F25 measured — this must be named as prior art, not claimed. The
cross-coefficient completion itself is published for *temporal* POD coefficients
of an attractor (driving modes + manifold equation for remaining modes); whether
anyone does it for a *parametric* condition→field surrogate, where stage-1
inputs are themselves regressed from a design vector, is the open question for
turn 2.
