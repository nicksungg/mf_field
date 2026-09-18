# Dataset roster history audit

Checked September 14, 2026 against the interpretability ZIP, local release and session records, and ORCD regeneration metadata. This is a provenance note. No datasets, training jobs, manuscript results, or aggregates were changed.

## The counts refer to different lists

`/archive/workspace/overleaf_interpretability_reframed (1).zip`, member `figs/dataset_table_body.tex`, contains 30 entries: 25 labeled 2D and five labeled 1D. The labels describe array dimensionality imperfectly because the heat fields are space and time.

Relative to that ZIP's 25 entries labeled 2D, the later surrogate release roster omits `ifc_heat` and `ifc_poisson` and adds `poisson_generated_v2` and `lid_driven_cavity_v2`. Both older Poisson and cavity entries remain. The net count stays 25, but membership changes. This is an observed set difference, not evidence that a deliberate replacement decision was made.

The release's own `models/st_bench/roster_30.txt` already has the IFC omissions and two additions. Dropping its five 1D entries gives `data/roster_25.txt`. Thus the release README's description of dropping five 1D entries applies to a different 30 entry list from the interpretability ZIP.

The paper's historical main aggregate uses 20 of the later release's 25 entries. The five absent at that snapshot were ERA5, Cahn Hilliard II, Fisher KPP, Allen Cahn, and phase field crystal, owing to prediction coverage or protocol issues documented in `mf_field_ensemble_audit_20260913`. Later completion does not automatically update that frozen aggregate.

## Recorded Poisson fix

`/archive/workspace/mf_field_session_20260905/datafix/DATASET_ISSUES_2026-09-06.md`, lines 12 to 16, records the extra grid spacing squared factor in the Poisson right hand side. The audit also identifies inherited scaling defects in Poisson local and IFC Poisson.

The ORCD file `/archive/mf_field_v2/core/poisson_generated_v2/meta.json`, reread for this audit, states `RHS b = g (original: dx^2 * g)` and generation time `2026-09-06 02:12`. It retains a 400 training and 100 test setup. The release `data/README.md`, line 39, explicitly says both original and fixed Poisson are scored for comparability.

## Recorded cavity sequence and conflicting documentation

The September 6 audit, lines 17 to 19, distinguishes three stages: the original 400/100 dataset with an insufficient solver iteration limit, a converged 40/10 dataset using a 200000 step cap and tolerance 1e-5, and a larger converged 400/100 extension.

`mf_field_session_20260905/bench_ct/gen_cav.py`, lines 1 to 3, says the first 50 simulations reproduce the existing v2 shards. Its `merge_cav.py`, lines 27 to 29, records reuse of August v2 shards and the larger sample set. ORCD's `/archive/mf_field_v2/core/lid_driven_cavity_generated/meta.json` confirms the same source and generation time `2026-09-07 02:19`. The session progress ledger records successful merging.

The release README incorrectly describes the 40/10 archive as the unconverged dataset. That conflicts with the earlier audit, merge provenance, and the later paper visual audit. The current paper's `qa/cavity_visual_audit.json` verifies that the first training field in both cavity entries has the same hash and is vorticity. This visual audit does not independently rerun the solver or certify convergence.

The supported interpretation of the current two cavity entries is the smaller archive and its larger extension sharing simulations. They are not independent physical problems.

## What is and is not recorded about IFC removal

The session README, line 17, and `bench_ct/make_tasks.py`, line 13, explicitly exclude IFC Heat, IFC Poisson, and ERA5 from the older correction workflow requiring an observed coarse field for the same case. The literature task note `litsurvey/00_our_side.md`, line 11, states the unpaired data rationale.

However, the surrogate release's `models/st_bench/st_common.py`, lines 8 to 10, explicitly supports unpaired IFC format data. Its task builder has no default exclusions. The original `data/datasets_final.txt` still lists both IFC entries.

No explicit decision explaining the IFC omissions from the later surrogate release was found in the inspected records. Inheriting a correction workflow roster is a plausible explanation, not an established fact. Unpaired data alone does not justify exclusion from the present predicted coarse field method. The August 5 audit proposed dropping many datasets including IFC based on copy LF comparisons, but many of those proposed exclusions remained in the later release. That proposal is not proof of the later roster decision.

The inspected local and ORCD source roots had no Git metadata, so commit history could not be recovered from those copies.

## Advice for the manuscript

Use one explicit versioned roster with separate columns for the problem family, data version, sample budget, and completed model coverage. Use the physically fixed Poisson setup for primary physical conclusions and retain defective archives as historical comparisons. Treat the two cavity sample sizes as related settings rather than separate independent PDEs. Record the IFC entries' absence as a scope decision that still needs justification or further evaluation, rather than claiming that the solver fixes required their removal. The 20 entry aggregate must be labeled as the historical completed evaluation subset until it is explicitly rebuilt.
