# Iteration 1 — map the three mechanism classes B2's part 7 points at

**Process rule honoured throughout this loop: no arXiv `/pdf/` URL was fetched
(only `/abs/` and `/html/`).**

## Search rationale

B2's part-7 `next_direction` names three things a B3 could be built from, none
of which has ever been prior-art-checked in this stream: (A) per-mode
out-of-fold map selection over a candidate bank for condition->POD-coefficient
regression (the one positive transfer: 10 params beat 1.59e7 params by 23.64x
mce on allen_cahn); (B) the finding that a shared post-hoc floor-blend stage
pays off as a closed-form function of rho, so cross-arm comparisons decided
there are decorrelation verdicts; (C) the selection-rule arity defect --
fitting the leading *energy* window instead of the identified *set* of
predictable modes. Turn 1 maps all three at once.

## Search terms used

1. `per-mode surrogate model selection for POD coefficient regression parametric PDE reduced basis`
2. `supervised basis selection predictable modes instead of energy-ranked POD for parameter-to-field surrogate`
3. `blending model prediction with baseline biases benchmark comparison error correlation optimal shrinkage weight`

## Findings

### Term 1 — per-mode POD-coefficient regression
Top returns: Frontiers PGD-based nonlinear regressions on POD modes
(https://frontiersin.org/articles/10.3389/fmats.2022.904707/full); Multi-fidelity
reduced-order surrogate modelling, Proc. Roy. Soc. A 480(2283):20230655
(https://royalsocietypublishing.org/rspa/article/480/2283/20230655/101080/Multi-fidelity-reduced-order-surrogate);
"Surrogates for Physics-based and Data-driven Modelling of Parametric Systems:
Review and New Perspectives" (https://link.springer.com/article/10.1007/s11831-026-10552-4);
data-driven ROM for parametric PDE eigenvalue problems via GPR
(https://www.sciencedirect.com/science/article/abs/pii/S0021999123005983).
The aggregated engine text states plainly: *"since POD provides an orthogonal
basis, modeling each modal coefficient independently avoids introducing
artificial correlations and yields a more efficient and scalable surrogate, with
K independent models employed, each associated with one modal coefficient"* and
*"independent GPR models used for each modal coefficient"* -- **search return
only, not fetched**, so it is recorded as strong evidence of standard practice
but is not a citation.
**Fetch attempted**: https://link.springer.com/article/10.1007/s11831-026-10552-4
-> **redirect-only to an IdP authorize endpoint (303), NOT followed** -> no
content, cited for nothing.

### Term 2 — predictability-ordered vs energy-ordered basis
Returns: POD-FNN transfer-learning surrogate (https://arxiv.org/pdf/2604.21220,
not fetched -- pdf), POD+RBF thermal surrogates
(https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12654062/), aerodynamic POD
surrogate reviews. Engine verdict, quoted: *"the search results do not appear to
contain specific information about 'supervised basis selection' using
'predictable modes' as an alternative to 'energy-ranked POD' for
parameter-to-field surrogates. The results focus on energy-based mode selection
rather than prediction-based or supervised mode selection approaches."*
It also confirms POD-NN as the standard shape (*"POD extracts the reduced basis
and neural networks approximate the map between flow parameters and POD
coefficients"*).

### Term 3 — blending with a baseline / optimal weights from error correlation
Returns: bias-variance trade-off and shrinkage of weights in forecast
combination (researchgate); "Explanation and Optimizing Multi-Model Blending
Algorithm Using Random Variables Theory", GRL 2025
(https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2024GL111622);
"A theoretical comparison of weight constraints in forecast combination and
model averaging" (https://arxiv.org/html/2510.26456).
**Fetched**: https://arxiv.org/html/2510.26456 -> it compares five weight
constraint spaces; per the fetch, it *"does not directly address combining
forecasts with a specific benchmark or baseline forecast"*, treats candidates
symmetrically, and *"does not explicitly derive optimal combination weights as
functions of error correlation between candidates and a baseline"*; its
Remark 1 connects non-negativity + sum-to-unity constraints to covariance-matrix
shrinkage. So: forecast-combination shrinkage is a mature field, but this
particular paper is not the citation for the rho-law.

## Interpretation

Per-mode independent regression on POD coefficients is standard practice (strong
search-return evidence, no fetch yet), so direction A cannot be claimed at the
"one model per mode" level -- only possibly at the "select the model FAMILY per
mode, out of fold, from a bank" level. Predictability-ordered basis selection
returned nothing directly, which is suspicious given supervised-DR literature
exists; term 2 must be re-run against the statistics vocabulary (PLS, supervised
PCA, reduced-rank regression). The blend rho-law is clearly forecast-combination
territory and needs a fetched primary citation.
