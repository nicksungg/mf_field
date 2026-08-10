# Iteration 1 — basis-truncation criteria for regression-driven surrogates

## Search rationale

Card part 7 names raising `SELECT_MAX` above 32 as "the largest identified, unexploited gain in the stream", and the mechanism handoff frames it as a *truncation* failure: fisher_kpp strands 0.0713 of condition-reachable encoded energy in directions the clip removed.
The generalisation batch 2 would want to claim is a **truncation criterion keyed on predictability rather than on energy** (keep a direction if the condition can predict its coefficient out-of-fold, not if it carries energy).
This turn asks whether that criterion — and its evaluation at tiny N — is already published.

## Search terms used

1. `POD basis truncation criterion regression predictability instead of energy reduced order model surrogate`
2. `adaptive rank selection number of POD modes cross-validation parametric surrogate few training samples`
3. `POD-NN surrogate how many modes to retain mode-wise regression error truncation operator learning`

## Findings

### Term 1 — truncation criteria beyond energy

The field's named criteria are **relative information content (RIC)** and **Gavish–Donoho singular-value hard thresholding (GD-SVHT)** — both energy/noise-level criteria, neither predictability-based (search-snippet only).
One concrete instance selects the truncation rank *jointly with the regression model* by leave-one-out cross-validation: a parametric-POD/HODMD framework where "the POD truncation rank, HODMD delay dimension, and interpolation model are selected using leave-one-out cross-validation, with polynomial, radial basis function, and Gaussian process regression models considered as interpolation candidates" — [cite: https://doi.org/10.3390/en19102387] (**search-snippet only, not fetched**).
Also surfaced: parametric POD (PPOD) motivated explicitly by classical POD coefficients being *hard to regress* — [cite: https://www.mdpi.com/1996-1073/17/1/146] (snippet only).
Interpretation: rank-as-a-CV-hyperparameter is standard; per-direction predictability as an *inclusion* criterion was not returned.

### Term 2 — adaptive rank selection at few samples

**Largely a dead end for the question asked.** Nine of nine returns are adaptive *sampling* (where to place the next snapshot: Voronoi/CV-error/variance-based exploitation), e.g. [https://arxiv.org/pdf/1910.00298] (Adaptive Sampling for the Reduced Basis Method), [https://www.cambridge.org/core/journals/data-centric-engineering/article/novel-adaptive-sampling-approach-with-batch-selection-.../EDE3801EB370807254D5DD7F1B73EF37], [https://pmc.ncbi.nlm.nih.gov/articles/PMC11236939/].
None is about how many/which basis directions to retain. Not fetched.

### Term 3 — mode-wise error decomposition and non-energy mode selection (two fetches)

**FETCHED** — Koike, Mohan, Henry de Frahan, Qian & Bessac, *Sparse POD Mode Selection and Manifold Dimensionality Reduction with Neural Networks* (SparseModesNet), arXiv:2605.27756 v2, 30 Jun 2026 — [cite: https://arxiv.org/abs/2605.27756].
Verbatim from the fetched abstract: linear methods "struggle … for data with slowly decaying Kolmogorov $n$-widths … moreover, **energy-based truncation can discard low-energy modes needed to capture small-scale features**"; and existing NN-manifold methods "employ **energy-based selection**".
Their fix is LassoNet hierarchical sparsity in a nonlinear decoder that "simultaneously **select[s] informative modes** and learn[s] a nonlinear mapping that minimizes **reconstruction error**".
So: the *critique of energy truncation* and *task-driven mode selection* are both published as of mid-2026 — but the selection signal is autoencoder **reconstruction** error on the snapshots, not out-of-fold **predictability from a parameter/condition vector**, and the regime is turbulent channel flow (Re_tau 5200), i.e. many snapshots, not N_hf ~ 5–400.

**FETCHED** (NSF PAR record) — *Physically interpretable surrogate modeling of thermal fields in electronics cooling using combined POD and neural networks* — [cite: https://par.nsf.gov/biblio/10684905].
Verbatim: "An error decomposition analysis quantifies **POD truncation and NN regression error contributions across dataset sizes, identifying a POD-truncation error floor that defines the surrogate's accuracy ceiling**."
This is exactly the accounting shape of the fisher_kpp finding (error attributable to truncation vs to the regression), published, on a 4-mode POD-NN thermal surrogate.

## Interpretation

The two load-bearing generalities behind the `SELECT_MAX` direction are already in the literature: energy-based truncation is a known failure mode (arXiv:2605.27756) and truncation-vs-regression error decomposition is a known diagnostic (par.nsf.gov/biblio/10684905).
What did **not** return is a criterion that keeps a direction because its coefficient is *predictable out-of-fold from the condition vector*, nor any of this at N_hf in the single/low-hundreds.
Next turn moves to the two-population / non-identifiability question.
