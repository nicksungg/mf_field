# Iteration 3 — settle the two live threads: R^2-based rank truncation, and
# post-hoc gain correction of point predictions

## Search rationale

Iteration 2 left exactly two unresolved: (a) is truncating a POD basis at the
*predictable* rank (R^2 of the coefficient surrogate) established practice —
one aggregated search snippet said yes but the confirming fetch failed;
(b) does anyone fit a **multiplicative gain on a frozen model's point
prediction** using held-out data (the operation B1's band calibration
performs, and the operation `websearches/r2s4_diag/batch_2/report.md` D3 says
is missing from the surrogate-calibration literature, which only rescales
variance)? Two terms, both refutation-shaped.

## Search terms used

1. `truncate POD basis by R2 score of coefficient regression surrogate mode selection criterion instead of singular value energy`
2. `post-hoc multiplicative gain correction of trained surrogate point predictions fitted on validation set scientific machine learning`

(Only 2 terms this turn — the third slot was held back deliberately for the
refutation turn, since both of these are already refutation-shaped.)

## Findings

### Term 1 — R^2-based POD truncation

Top results:
- POD Mode Coefficient Interpolation: non-intrusive ROM for parametric reactor
  kinetics — https://arxiv.org/pdf/2303.08872
- Reduced-order surrogates for forced flexible-mesh coastal-ocean models — https://arxiv.org/pdf/2602.05416
- POD-based surrogate modeling of transitional flows with adaptive sampling in
  GP — https://www.sciencedirect.com/science/article/abs/pii/S0142727X1931210X
- Transfer-learning-enhanced POD-FNN surrogate — https://arxiv.org/pdf/2604.21220
- Development and comparative selection of surrogate models using ANN — https://www.sciencedirect.com/science/article/abs/pii/S0306261922005207

The engine's synthesis states the standard truncation menu explicitly —
"selecting a rank a priori, using a singular value cutoff, or ... cumulative
energy ratio, r = argmin(sum sigma_i^2 / sum sigma_j^2 < 1 - tau)" — and that
R^2 is a "commonly-used evaluation metric for surrogate models" used to pick
*between surrogate models*. It then states plainly: it "did not find specific
literature ... that directly addresses **truncating the POD basis specifically
by R2 score of coefficient regression as an alternative to singular value
energy-based selection**", calling the combination "more specialized or
recent".

Combined with iteration 2's opposing snippet ("references suggest reducing the
modes of a POD based on the R^2-Score of the POD coefficients surrogate
models"), the honest reading is: **the idea is in circulation in the ROM
community but I could not fetch a source that states it**. Recorded as such;
no citation will be attached to it in either direction.

### Term 2 — post-hoc gain correction of point predictions

Top results:
- Post-Training Corrections for Improved Time-Series Forecasting — https://arxiv.org/html/2505.15354
- The ROMES method for statistical modeling of reduced-order-model error — https://arxiv.org/pdf/1405.5170
- UQ of surrogate models using conformal prediction — https://arxiv.org/html/2408.09881
- Multi-granularity conformal prediction for neural-operator aerodynamic
  surrogates — https://arxiv.org/html/2607.17297
- Population-graph post-hoc correction of survival predictions — https://link.springer.com/chapter/10.1007/978-3-032-06103-4_19

**FETCHED** https://arxiv.org/html/2505.15354 (Post-Training Corrections for
Improved Time-Series Forecasting) — the decisive hit. It studies a library of
post-training corrections applied to a **frozen** forecaster and selected on
held-out data: **affine correction (scale + intercept)**, "**scale amplitude:
globally rescales the forecast around its mean to increase/decrease
oscillation amplitude**", piecewise scaling, linear-trend adjustment,
min/max factor increases, plus LLM-driven human-in-the-loop corrections. It
gives the closed form for the optimal affine parameters:
`a* = Cov(Y_true, Z)/Var(Z)`, `b* = E[Y_true] - a* E[Z]` — i.e. the textbook
regression-to-the-mean gain, exactly the *global scalar* version of B1's gain
calibration. Its selection procedure "sequentially select[s] correction
functions to identify with high probability the one achieving the lowest
predictive error".
Crucially, the fetch reports: "**No**, none explicitly target multiplicative
gains per frequency band or spectral component. The paper focuses on
time-domain transformations", and the methods "don't explicitly shrink toward
zero".

**FETCH FAILED** https://arxiv.org/pdf/1405.5170 (ROMES) — unreadable
compressed PDF; nothing quoted, not used as evidence.

Search-return note: the conformal-prediction line for surrogates/neural
operators (arXiv:2408.09881, arXiv:2607.17297) calibrates *nonconformity
scores / interval width* on held-out data — confirming r2s4-B2's D3 finding at
a second sample of the literature.

## Interpretation

Post-hoc, held-out-fitted correction of a frozen predictor's **point** output
IS published (arXiv:2505.15354), with a menu that includes the global
amplitude rescale and closed-form optimal affine gain — so "calibrate the
gain out of fold" is preempted at the *global scalar* level. What is not
found, in either the forecasting-correction or the neural-operator-calibration
literature, is the **band-resolved** version (a gain per wavenumber band) or
the use of the fitted gain vector as an *identifiability diagnostic*. That is
the precise seam B2 can occupy. Rank-by-predictability could not be pinned to
a fetchable source and must be treated as very likely established.
