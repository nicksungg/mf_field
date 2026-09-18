# Review response reanalysis

> Historical review record from 15 September. Its roster dependent counts are superseded by [the 16 September scope update](SCOPE_UPDATE_20260916.md). The current manuscript and generated results use 19 settings, with 18 in the common aggregate.

This is a new post hoc analysis of previously inspected frozen predictions. It is not a new test draw, new training run, prospective confirmation, or evidence that model training budgets are matched. The procedure was specified in `ANALYSIS_PROTOCOL.md` before new selector scores or subset summaries were computed. The original manuscript and original numerical artifacts were not changed.

## Inputs and verification

The local historical cache contained metadata but no per case matrices. The exact 20 cached Gram archives and row identity tables were therefore copied read only from ORCD. No cluster jobs were launched or modified. The copied files occupy about 9.3 MB. `data/review_analysis_source_manifest.json` records original remote paths, hashes, expert order, and prediction source hashes. Each copied labels/features hash agrees with its archived audit. Every calibration and evaluation row/group mapping agrees with the existing 60 split files.

All 180 new fits use the exact bundled `data/ensemble_rules.py` implementation, preserving its candidate order, tie handling, objective, and optimizer. All weights and calibration choices were saved before evaluation scoring began. The maximum reconstructed original per case error difference is 3.55e-15. New fitted mixture evaluation means agree with the historical implementation within 1.55e-15 relative. The maximum simplex residual is 3.33e-16. No changes to the original fixed rule results were necessary.

The nominal budgets are 5, 10, and 20. All 60 five field fits have five calibration fields. Cavity I has only eight available calibration fields, so its three partitions use eight at the nominal budgets of ten and twenty. The other 57 fits at those budgets use the nominal number. The three partitions reuse one trained library and overlap in cases. They are not independent training replications.

## Exact automatic selector

At five calibration fields, automatic selection gives class and dataset geometric ratios of **0.872862 and 0.914514** relative to calibration based selection of one expert. Using the existing one percent neutral interval, the automatic rule wins on 14 datasets, ties on four, and loses on two. The leave one out procedure selects the single expert rule 18 times, inverse weighting 15 times, and fitted stacking 27 times across the 60 partitions.

These improvements do not demonstrate superiority to rules fixed in advance. At five fields, automatic selection versus inverse weighting has class/dataset ratios **0.994715 / 0.990103**. Versus fitted stacking they are **0.998322 / 0.992174**. Thus its aggregate advantage over either mixture is small. At ten and twenty calibration fields, automatic selection is worse than fixed fitted stacking by approximately 1.6 and 1.5 percent in the class metric, respectively. Its class ratios to selecting one expert remain about 0.874.

The rule selected using evaluation errors separately for each partition is an unattainable diagnostic. Automatic selection has class/dataset ratios **1.02711 / 1.04203** relative to this diagnostic at five fields. The corresponding regret stays positive at the other budgets. A retrospective choice after averaging partitions within a dataset is a different comparator and can sometimes be beaten by case partition specific automatic choices. Both diagnostics are retained in JSON, with explicit names.

## Quality and coverage sensitivity

Each pair below is class geometric ratio / equal dataset geometric ratio at five fields.

| Scope | Number | Best library / best additional baseline | Fitted / selected | Automatic / selected |
|---|---:|---:|---:|---:|
| Historical | 20 | 0.7518 / 0.8223 | 0.8743 / 0.9217 | 0.8729 / 0.9145 |
| Audit retained | 15 | 0.7512 / 0.8234 | 0.8689 / 0.8979 | 0.8617 / 0.8889 |
| Common baseline coverage | 18 | 0.7769 / 0.8607 | 0.8705 / 0.9365 | 0.8682 / 0.9280 |
| Intersection | 13 | 0.7805 / 0.8773 | 0.8644 / 0.9141 | 0.8563 / 0.9031 |

The 15 dataset subset retains the exact five preexisting audit exclusions. The 18 dataset subset requires all eleven additional B1 to B11 baseline results. No subset membership uses the new errors. The overlap has 13 datasets.

The useful conclusion is that mixing versus calibrated expert selection survives these sensitivity checks. A stronger claim that the ensemble generally beats the best available individual expert is not supported. On the common 18 dataset subset, fitted stacking has an equal dataset ratio **1.02041** to the hindsight best individual, and automatic selection has ratio **1.01123**. Both are worse in that metric despite favorable class weighting. The main text should report this limitation explicitly. Neither baseline minima nor library minima are selected by a deployable calibration procedure, and training costs remain unequal.

## Integration files

- `tables/review_automatic_main.tex`: nine rows, fixed mixtures and complete selector at the three budgets on the same 20 datasets.
- `tables/review_sensitivity_main.tex`: four sensitivity scopes, compact class/dataset ratios.
- `tables/review_automatic.tex`: all three primary scopes and budgets.
- `tables/review_selection.tex`: selection frequencies and diagnostic regret.
- `tables/review_subsets.tex`: all central headline comparisons on every fixed scope.
- `tables/review_automatic_per_dataset.tex`: per dataset errors for fixed rules and automatic selection at five fields.
- `data/review_analysis.json`: all numerical means, ratios, squared metric summaries, scope memberships, and per partition scores.
- `data/review_analysis_fits.json`: choices and leave one out calibration scores, with locked weight hash.
- `data/review_analysis_locked_weights.npz` and `data/review_analysis_per_case_errors.npz`: reproducible arrays.
- `qa/review_analysis_checks.json`: source and numerical checks.

Reproduce using `python3 scripts/build_review_analysis.py` from the new draft directory. The script regenerates only files with review analysis names and does not change historical results or common data builders.

## Additional provenance observation

The source prediction hashes themselves are identical for M8 and M9 on Darcy and Helmholtz I. This is stronger than the review's observation of matching calibration Gram rows: the two entries reference the same complete archived prediction file in those settings. They therefore should not be described as two independently different predictors on those two datasets. This reanalysis preserves the historical library exactly, including these duplicate entries. It does not claim duplicate invariance of inverse weighting or perform a new deduplication experiment.
