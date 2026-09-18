# Frozen review response reanalysis protocol

Specified on 15 September 2026 before computing new automatic selector scores or new subset summary scores. These analyses reuse previously inspected predictions and are post hoc exploratory checks, not prospective confirmation.

## Data and scope

Use all 60 existing historical dataset partitions: the 20 historical datasets, three existing partition identifiers, and nominal calibration budgets 5, 10, and 20. Preserve every original split and actual available calibration count. Use only authentic per case normalized error Gram matrices, with row and expert identity verified against archived metadata. Do not reconstruct per case Grams from their average. If those artifacts are unavailable, mark this component unavailable rather than approximating it. ERA5 stays a separate existing experiment and is not added to the historical aggregate.

## Fixed procedure

Use the exact bundled data/ensemble_rules.py fit_auto function. The candidate order is selected_single, inverse_mse, full. Each leave one out iteration fits each candidate on the other calibration cases and scores mean relative L2 on the omitted calibration case. Ties use the fixed candidate order. Refit the selected rule on all available calibration cases. No new tuning grid, features, per dataset choices, or evaluation guided exceptions are permitted. Persist all weights and calibration choices, with hashes, before computing any evaluation scores. Evaluation identities must be disjoint from the corresponding calibration identities.

The new selector uses this exact bundled implementation. Previously published fixed rule scores and weights remain unchanged. Replay comparisons will report any numerical differences between the exact bundled implementation and the historical fixed fits. The new exact implementation fixed rule scores will also be recorded to separate rule selection effects from numerical refitting differences.

## Comparisons and aggregation

At each budget, report all three fixed rules and the automatic rule on the same cases. Report frequencies of selected rules, mean evaluation error per dataset partition, equal dataset and equal class geometric ratios after averaging partition errors within each dataset, and wins/losses with the original 1 percent neutral threshold. Report automatic versus selected model, inverse weighting, fitted mixture, and hindsight best of the three fixed rules. Hindsight best is a diagnostic, never deployable selection. Report squared relative errors as a supplementary metric if per case Grams permit it. Overlapping partitions are not independent seeds and no significance claims will be made from their count.

Repeat central headline comparisons on four fixed scopes: all 20 historical datasets; the 15 retained by the five exclusions already recorded in data/audit_sensitivity.json; the common 18 datasets with every B1 through B11 baseline result; and the intersection of those two sensitivity subsets. For library and baseline minima, average partition errors before taking a minimum within a dataset and label all such minima retrospective. Preserve matched evaluation row and baseline seed averaging conventions of the existing paper. These checks do not equalize training resources.

## Verification and nonclaims

Verify source hashes, expert order, all original split mappings, calibration/evaluation exclusion, PSD and symmetry to floating point tolerance, simplex feasibility, inverse formula replay, original stored evaluation reconstruction, and saved weight hashes before/after scoring. Keep logs of any unavailable input or failed check. Do not update original artifacts. These analyses do not address matched training costs, fresh unseen family confirmation, new fine simulation savings, or simulator validation.
