# Iteration 4 — refutation turn 1 (targeted "has this been done?" searches)

## Search rationale

First explicit refutation turn. One targeted search per candidate direction:
A = per-mode out-of-fold model-family selection; B = post-hoc blending with a
baseline as an *evaluation* confound; C = keeping low-energy but predictable
components instead of the leading window.

## Search terms used

1. `choosing best regression model per mode cross-validation kriging polynomial neural network each POD coefficient comparison study`
2. `post-hoc blending with climatology baseline inflates skill score comparison between models decorrelation artifact evaluation`
3. `low-variance principal components highly predictable regression discard leading components supervised PCA response`

## Findings

### Term 1 (direction A refutation)
Returns: POD mode coefficient interpolation (arXiv:2303.08872); POD + PC-Kriging
for reacting flow
(https://www.sciencedirect.com/science/article/pii/S2590123021000244); hybrid
anchored-ANOVA POD/Kriging. Engine text: *"A wide variety of methods have been
applied for predictive regression learning on numerical data in POD-based
reduced-order modeling, including polynomial chaos expansion, Gaussian process
regression models, and neural networks"* and repeated-k-fold CV is used *"to
approximate performance on irregular parametric grids"*. Comparative studies
compare families **globally** (POD+PCE vs POD+PC-Kriging etc.), not per mode.
**No result naming per-mode family selection. Search return only.**

### Term 2 (direction B refutation)
**No usable results.** Returns were general skill-score material (Brier/RPSS
climatology reference discussions, FSS, IRI verification score descriptions).
The engine states outright: *"The search results don't contain specific
information about the exact topic you're asking about - which appears to be a
technical paper or research discussion on how post-hoc blending with climatology
baselines can artificially inflate skill score comparisons between models due to
decorrelation artifacts."* This is the first independent miss for direction B's
*composition*.

### Term 3 (direction C refutation) — decisive
Returns: "Covariance Supervised Principal Component Analysis" (arXiv:2506.19247);
Bair & Hastie et al., "Prediction by Supervised Principal Components"
(https://hastie.su.domains/Papers/spca_JASA.pdf); "Supervised PCA: A
Multiobjective Approach" (https://arxiv.org/abs/2011.05309); "Sufficient
principal component regression" (arXiv:2107.02150).
Engine text: *"Principal components derived by PCA are not guaranteed to be
informative of the response variable which can result in low prediction
accuracy when the goal is prediction"*; *"supervised principal component
analysis works by estimating a sequence of principal components that have
maximal dependence on the response variable"*; *"Bair and Tibshirani [2004]
first addressed supervised PCA"*; and, on the exact pathology B2 measured,
*"projecting data onto the top principal components can thus discard valuable
information"* about low-variance but tightly-regulated processes.
**Fetch attempted**: https://hastie.su.domains/Papers/spca_JASA.pdf -> **binary
PDF, no extractable text. Cited for nothing.**
**Fetch attempted**: https://www.janmagnus.nl/papers/JRM113a.pdf (direction B)
-> **binary PDF, no extractable text. Cited for nothing.**

## Interpretation

Direction C is preempted in substance: "leading variance-ranked components are
not the predictive ones; select components by dependence on the response" is the
founding statement of the supervised-PCA line -- a fetched citation is still
owed (turn 5). Direction B's *mechanism* is forecast-combination theory, but its
*composition as a benchmark-protocol defect* survived its first refutation
search with no usable result. Direction A survived a second refutation search
with no per-mode family-selection source named.
