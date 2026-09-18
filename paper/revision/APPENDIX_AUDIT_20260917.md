# Appendix audit, 17 September 2026

The current 22 dataset manuscript was checked section by section against its
saved experiment artifacts, numerical reconstruction code, available model
implementations, plotting sources, and cited literature. Verified discrepancies
in the descriptions were corrected. No surrogate was retrained and no primary
prediction or ensemble fit was replaced. The normal build replays archived
fitting calculations for provenance. No reported evaluation result was changed.
The preceding manuscript directory was preserved.

The scope is an artifact and mathematical audit. It is not an independent
replication of all model training, a solver convergence study, or a certification
of physical climate metadata.

## Corrections and clarifications

1. **ERA5 inventory now describes the evaluated split.** The table previously
   gave the original archive counts of 65 fine training rows, a minimum of 328
   coarse rows, and 7 query rows. Although accompanying prose explained that
   those were source counts, they were inconsistent with the other rows' role
   in the actual experiment. It now gives 55 base fine training rows, a minimum
   of 313 retained coarse rows, and 17 reserved queries. Those queries contain
   the 10 example fitting pool and 7 evaluation cases. These values come from
   `data/era5_completion/nine/PLAN.json`. The original inventory is preserved.
2. **Grid and scaling checks are distinguished from physical metadata.** The
   old phrase said that coordinates and units were checked. The verified
   operations check array grids, target scaling and row identity. They do not
   verify physical ERA5 units or geographic coordinates.
3. **Coarse fidelity choices are explicit.** M1, M3, M4, M5 and M6 use the
   lowest registered coarse level. M2 pools fidelity pairs, M7 uses fine data
   only, and M8 and M9 predict the finest coarse level. In ERA5 these are level
   one versus level eight. A common dataset does not mean every model uses
   identical coarse information.
4. **Supplementary experiments are identified correctly.** The coarse
   resolution perturbation uses the additional Heat I input experiment, with
   128 evaluation cases. Its frozen weights were fitted on those same fitting
   examples before changing the coarse input procedure. They are not weights
   from the older main evaluation partition. The reported errors were correct.
5. **Stale references were removed or redirected.** The error geometry section
   no longer points to a removed direction control in the main results. The
   uniform averaging discussion now points to the table that actually reports
   it. Unreported adaptive gate prose was removed, and supplementary controls
   are distinguished from the three main rules.
6. **Elo scope is precise.** Every method uses the same current collection of
   22 datasets, with no further exclusions during Elo computation. This avoids
   implying that the historical choice of reporting scope was independent of
   previously inspected performance. The explanation now covers ties as well
   as wins and losses.
7. **Baseline aliases are consistent.** B10 reuses B9 predictions on ERA5 and
   the four additional datasets. The adaptation description now agrees with
   the detailed baseline caption about both cases.
8. **Reproducibility claims match the checks performed.** The complete training
   and simulation archives are retained separately. A clean manuscript package
   rebuild checks ensemble fitting, saved prediction evaluation and reporting.
   It does not establish successful retraining of the entire library.
9. **Figure descriptions match their transformations.** The ERA5 appendix
   documents the display interpolation and coarse thumbnail smoothing used by
   Figure 1. These do not alter numerical targets or predictions. The individual
   model heatmap identifies FiLM FNO transfer explicitly and uses the POD GP
   spelling consistently. Numerical color scales and dataset grouping were
   visually checked in all six gallery plates.
10. **The runnable example uses a main paper rule.** The README command now
    requests `fitted`, not the archived automatic selector. The mathematical
    loss comparison explicitly cites the existing engineering work on the
    influence of the fitting criterion.

## Section by section findings

| Appendix | What it explains | Audit outcome |
|---|---|---|
| A | Why model error estimates affect the accuracy of the weighted average | The simplex perturbation bound, first order optimization gap, Hoeffding constants, diagonal weighting derivation, and ambiguity identity are correct under their stated assumptions. The bound is too loose to guarantee success with five fields. |
| B | How the nine models and baselines were implemented, trained, and combined | Checked the available training code, model components, fidelity choices, optimizer conventions, retrieval, coarse ensemble construction, and mixture code. It correctly distinguishes adapted components from faithful reproductions and preserves differences in training budgets. |
| C | Which datasets are included and how they are grouped | Verified 21 PDE datasets across seven descriptive classes plus ERA5, parameter dimensions, grids, source attribution and actual ERA5 split counts. |
| D | Every individual and mixture score, and changes with fitting budget | Recomputed errors and aggregates. The selected model and the hindsight best model are distinct references. Supplementary regularization and coarse resolution experiments are identified separately. |
| E | Whether conclusions depend on the comparison subset | Verified the 17, 14, 15 and 12 dataset subset definitions. The duplicate Darcy prediction archives are real and can make individual weights nonunique. The extra Heat I evaluation is part of an existing dataset, not a twenty third dataset. |
| F | All ERA5 model results, mixtures, fitting splits, and costs | Reconstructed the nine model errors and all three rule outputs at both budgets directly from saved fields. The same seven evaluation cases are used throughout. Native display resolution and evaluated working resolution are distinguished. |
| G | Relation to prior work, error geometry, and the choice of fitting loss | The comparison table does not assert measured superiority over complete prior systems. The squared versus unsquared loss counterexample, convex norm formulation and 51 retained solver records are consistent. |
| H | Every baseline score, Elo computation, model sources, and deployment steps | Checked 273 PDE baseline entries, ERA5 completion, matched evaluation identities and the 23 method Elo ranking. Duplicate baseline recipes are disclosed. The field example uses saved weights and identifies its illustrative selection. |
| I | Larger examples of every dataset | All 22 samples follow the fixed first training row rule. Checked class order, Cahn Hilliard adjacency, native array shapes, color scales, cavity vorticity and the ERA5 display description. |
| J | Reproducibility, AI assistance, and responsible use | Statements distinguish retained research archives from the portable manuscript package and identify what was actually rebuilt. |

## Independent numerical checks

`scripts/audit_appendix.py` supplements the existing paper verifier without
altering the saved weights. Its machine readable results are in
`qa/appendix_audit_checks.json`.

* Replayed 459 historical fixed rule outputs from saved per case error product
  matrices, covering 17 PDE datasets, three partitions, three budgets, and
  three main rules. The maximum discrepancy from archived per case errors was
  approximately 2.22e-16.
* Recomputed 18 ERA5 rule outputs directly from complete saved prediction fields,
  covering three fitting selections, two budgets, and three rules. Also checked
  the nine individual model errors and the constant POD GP prediction.
* Checked 108 additional dataset rule mean records against their saved case
  errors. The completion verifier additionally checks their sealed weights,
  prediction metadata, baseline identities and source hashes. Full prediction
  field replay for those four datasets is outside the compact package audit.
* Confirmed 3,058 PDE query rows, 1,842 evaluation appearances and 1,505 distinct
  dataset and row pairs. Fitting sets are nested and disjoint from evaluation
  within each partition. These counts do not establish independence across
  related dataset archives.
* Confirmed the fitted mixture's 11.6% reduction under PDE class aggregation,
  7.5% reduction across all 22 datasets and 16 improvements exceeding one
  percent, relative to the model selected using the fitting examples.
* Confirmed the ERA5 inverse mixture improves six of seven cases and the fitted
  mixture improves five, relative to the training mean. Their K=5 mean errors
  remain 5.8146% and 6.4877%. POD GP remains 6.7369%.
* Confirmed the coarse input perturbation and refresh errors, and the direct
  relative L2 control's 51 retained optimal solver statuses and tolerances.
* Rebuilt baseline comparisons, ranking, tables and plots using the existing
  source checks. The original primary summaries and Elo values are unchanged.

## Mathematical and source checks

For simplex weights the coefficients in the error matrix perturbation bound
are nonnegative and sum to one, yielding the stated uniform error bound and
then excess squared risk at most twice that error plus optimization error.
Hoeffding with entries bounded in absolute value by B yields exactly the
constant used in Appendix A. At the reported budgets the resulting bounds are
3.596B, 2.543B and 1.798B, all weaker than the trivial B bound. Pixels cannot be
substituted for independent fitting fields. The inverse rule minimizes the
diagonal quadratic objective, while the reported unsquared field norm is a
different loss. The two case example and cone formulation correctly show this
distinction.

The source descriptions were checked against available implementations and
the existing research ledger. Current primary source checks confirm that
optimized surrogate weighting is established in engineering
([Acar and Rais Rohani](https://link.springer.com/article/10.1007/s00158-008-0230-y)),
that selection and weighting from validation errors predate this study
([Viana et al.](https://link.springer.com/article/10.1007/s00158-008-0338-0)),
and that a unified functional output multifidelity benchmark already exists
([Brunel et al., author repository](https://sudret.ibk.ethz.ch/publications/preprints-archive/2024-006.html)).
The compact prior systems table is also consistent with the published AQBMF
formulation ([author copy](https://web.mae.ufl.edu/nkim/Papers/paper151.pdf)).
These are source and formulation checks, not a new exhaustive priority review
or a matched experimental comparison with those complete systems.

## What remains a limitation

The records support the stated numerical comparisons on their specified cases.
They do not establish equal training cost or fine label exposure, uncertainty
across independently trained libraries, physical validity of every solver,
or global climate forecasting skill. Historical evaluation inspection,
related archives, the duplicate Darcy entries, and the unresolved historical
B9/B10 score provenance remain disclosed. No editorial audit can resolve
those experimental limitations without additional evidence.
