# Iteration 1 — the shrinkage/held-out gate-fitting axis

## Search rationale

B1's LICENSED-1 is "repair the gate's scoring split, KEEP the shrinkage line
search". s6-B2 already established that out-of-fold *combiner* fitting is
Wolpert 1992 (cited through fetched arXiv:1106.1684), so re-searching plain
stacking would be waste. The unanswered half is the **shrinkage**: is a scalar
blend weight fitted by a validation line search *that contains 0* -- i.e. a
shrunk, non-negativity-constrained, two-model stacking weight -- a named,
theorised object? Terms attack (1) the stacking-with-shrinkage theory, (2) the
multi-fidelity scale-factor / discrepancy literature where exactly one scalar
`rho` multiplies the LF model, (3) the James-Stein framing the orchestrator
asked about explicitly.

## Search terms used

1. `shrinkage ensemble weights stacked regression ridge regularization non-negativity Breiman stacked regressions cross-validation`
2. `multi-fidelity surrogate correction weight fitted on held-out samples scaling factor least squares shrinkage regularization few high-fidelity`
3. `James-Stein shrinkage estimator ensemble weights neural network model averaging regression small sample`

## Findings

### Term 1 — stacking IS shrinkage, and it is proved (FETCHED)
- **"Error Reduction from Stacked Regressions"**, https://arxiv.org/html/2309.09880
  (also https://arxiv.org/pdf/2309.09880) — **FETCHED.** Verbatim from the fetch:
  the paper proves *"the solution `alpha_hat` to program (8) satisfies
  `sum_{k=1..M} alpha_hat_k <= 1`"* and observes *"the unconstrained solution
  always satisfies `sum alpha_hat_k < 1` with near equality in most cases"*; and
  it gives a conditional guarantee that *"the population risk of the stacked
  model ... is strictly less than the population risk of the data-selected best
  single model"* (under `d_k >= d_{k-1} + 4/(2-tau)`). It also records
  **Breiman (1996)**'s non-negativity constraint on blending coefficients
  (search-return summary of the same result cluster).
  **Adversarial note for our card**: the fetch also states this variant
  *"does NOT require cross-validated/out-of-fold predictions"* — it regularizes
  by model degrees of freedom instead, *"a small departure from Breiman's
  formulation"*. So this paper is NOT a citation for the split repair; it is a
  citation for "shrunk, non-negativity-constrained blend weights are a studied
  estimator with a risk guarantee". The two mechanisms (proper split vs
  shrinkage) have *different* published homes.
- Other returns (not fetched): "A General Weighting Theory for Ensemble
  Learning Beyond Variance Reduction..." https://arxiv.org/html/2512.22286 ;
  Knight, "Shrinkage estimation, model averaging, and degrees of freedom"
  https://utstat.utoronto.ca/keith/papers/ridge.pdf ; tidymodels' stacking
  chapter https://www.tmwr.org/ensembles.html (search-return: regularized
  regression for ensemble weights is standard practice).

### Term 2 — the MF literature's one scalar is `rho`, fitted by least squares
- Search-returns describe the canonical MF comprehensive-correction form:
  *"built with surrogates for low-fidelity predictions and a discrepancy
  function, where a scale factor `rho` and discrepancy function are optimized"*
  — https://arxiv.org/pdf/1705.02956 ("Multi-Fidelity Surrogate Based on Single
  Linear Regression"), https://link.springer.com/article/10.1007/s00158-021-03044-5
  (MF surrogate on moving least squares, *"calculates low-fidelity scaling
  factors and unknown coefficients of the discrepancy function simultaneously"*),
  https://arxiv.org/pdf/2508.08517 (projection-based MF linear regression for
  data-scarce applications), https://www.researchgate.net/publication/361375560_Modified_Multifidelity_Surrogate_Model_Based_on_Radial_Basis_Function_with_Adaptive_Scale_Factor
  (adaptive scale factor). **All are scalar/GP/RBF surrogates over design
  variables, none is a field-valued neural corrector, and none of the returns
  mentions fitting `rho` on a split held out from the *base* model's own fit.**
  No usable fetch attempted this turn (the shapes are clear from the returns and
  they are nearest-neighbour context, not the verdict).

### Term 3 — the James-Stein connection is explicit and citable (FETCHED)
- **"Model averaging: A shrinkage perspective"**, https://arxiv.org/html/2309.14596
  — **FETCHED.** Verbatim: *"combining two linear smoothers by minimizing
  Mallows' Cp yields a James-Stein estimator"* (attributed in-paper to Kneip,
  1994, Section 5.1). The fetch confirms the paper is *"about purely statistical
  regression, not PDE/operator learning"*, and that *"the optimal model averaging
  estimator is a form of blockwise or Stein shrinkage"* in Gaussian
  sequence/regression settings (search-return phrasing of the same point).
- Adjacent returns, not fetched: "Ensemble minimaxity of James-Stein estimators"
  https://arxiv.org/pdf/2206.10856 ; "Frequentist Shrinkage under Inequality
  Constraints" https://arxiv.org/pdf/2001.10586 (the inequality-constrained =
  line-search-containing-0 shape); "Model averaging ... Optimal Model Averaging"
  https://arxiv.org/pdf/2110.12946 .

## Interpretation

The `alpha` line search in `fno_transolver_seq` is, in statistics, a
**two-model shrunk stacking weight** — and both halves of it are published
theory: non-negativity + shrinkage with a risk guarantee (2309.09880) and the
exact two-smoother/James-Stein identity (2309.14596, via Kneip 1994). Neither
source is PDE/operator learning and neither addresses the base-in-sample split
defect. So the card must claim **zero novelty for the estimator** and locate any
novelty in the *composition*: a shrunk gate over a field-valued neural
corrector, scored on a split held out from the base's own fine-tune.
