# B8 run completion and comparison coverage

Checked the saved B8 (fidelity basis FNO, `fno_coregionalization`) results for the two omitted PDE entries. Both training runs have completed result records:

* Heat II: `data/baseline_raw/fno_coregionalization__heat_local__s42.json`, with 512 test case errors and 625 LF plus 1875 joint training epochs recorded.
* Burgers: `data/baseline_raw/fno_coregionalization__sharp__burgers_2d__s42.json`, with 100 test case errors and the same epoch schedule recorded.

Neither raw record includes a source data manifest. The current matching audit also has no saved target/error export establishing correspondence with the common evaluation rows. Read only checks on ORCD found no matching B8 files for these two datasets in either `release/predictions_full` or `release/mf_field_surrogate_bench/results/predictions`. This search does not establish that recoverable checkpoints or exports are absent elsewhere.

Consequently, training completion is distinct from verified comparison coverage. Table 2 currently aggregates B8 over 15 of the 17 PDE datasets. Each included ratio uses the Selected model on the same dataset, so the issue is a different dataset subset, not a differently defined reference error. ERA5 B8 is separately completed, verified, and included, as documented in `ERA5_B8_COMPLETION_20260916.md`.

Replaced the ambiguous caption phrase about a different denominator with the explicit subset and reason. The appendix now distinguishes completed runs from unverified test case correspondence. No scores, datasets, trained models, or aggregate calculations were changed. The original manuscript remains untouched.
