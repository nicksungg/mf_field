# Companion material for the condensed appendix

The paper keeps the dataset protocol, all nine model adaptations, complete
baseline comparisons, fitting budgets, focused robustness checks, ERA5,
the additional Heat I check, and the mathematical explanation. This directory
indexes material retained outside the rendered paper. Removing repetition from
the paper does not remove numerical evidence from the source package.

## Enlarged dataset gallery

The following plots show every dataset with numerical display scales. Each
example is row zero of its HF training table. Coordinates are array indices.
The cavity target is vorticity and uses a symmetric logarithmic display scale.
ERA5 displays stored values on the native grid, without establishing physical
temperature units. Imported data are attributed in the manuscript inventory.

1. [Elliptic fields](../figures/dataset_detail_1.pdf).
2. [Diffusion and convection fields](../figures/dataset_detail_2.pdf).
3. [Shock and porous flow fields](../figures/dataset_detail_3.pdf).
4. [Reaction diffusion fields](../figures/dataset_detail_4.pdf).
5. [Wave fields](../figures/dataset_detail_5.pdf).
6. [ERA5 field](../figures/dataset_detail_6.pdf).

[Extraction manifest](../data/gallery_manifest.json) and
[sample arrays](../data/gallery_samples.npz) preserve source identities and
the fixed selection rule. [Original display description](archived_appendix/visual_appendix.tex)
records the numerical scales and cavity orientation.

## Exploratory branches

[Exploratory notes](EXPLORATORY_NOTES.md) summarize regularized mixtures,
coarse input refresh, and the longer concentration calculation. Their original
LaTeX descriptions are frozen in `archived_appendix/`. These files are reference
fragments from the appendix before condensation. Their old section and table
references are not the current manuscript numbering, and they are not included
by `main.tex`. They are not a second set of current main claims.

## Complete numerical records

- [All primary PDE rules and budgets](../data/paper_primary_summary.json).
- [All 22 dataset errors, aggregate ratios, and Elo](../data/table2_ranking.json).
- [Baseline errors on matched cases](../data/matched_baseline_cases.csv).
- [Baseline case correspondence](../data/matched_baseline_coverage.csv).
- [Numerical workbook](../data/paper_data.xlsx).
- [ERA5 per case baseline errors](../data/era5_baselines_per_case.csv).
- [Subset diagnostics](../data/review_analysis.json).
- [Direct loss control](../data/loss_control/evaluation.json).
- [Additional Heat I summary](../data/fresh_heat_summary.json).

Generated LaTeX tables also retain the detailed subset comparisons
(`tables/review_subsets.tex`), subset and budget comparisons
(`tables/review_fixed_budgets.tex`), individual errors
(`tables/individual_direct.tex`, `tables/individual_remaining.tex`), and source
summaries (`tables/baseline_provenance_1.tex` through `_3.tex`). They remain
rebuildable even where the condensed PDF refers to the main tables instead.
The [individual error heatmap](../figures/individual_models.pdf) and
[class and budget plot](../figures/results_overview.pdf) remain available here.

## Implementation and audit records

[Generator sources and numerical checks](../research/generator_verification/README.md)
distinguish published software and benchmark recipes from our implementation
checks. The record includes the numerical verification scripts and selected
convergence checks repeated for this revision.

The earlier descriptions of numerical precision, case replay, baseline
checkpoint recovery, and solver diagnostics are preserved in
[the archived protocol](archived_appendix/appendix.tex),
[baseline details](archived_appendix/visual_appendix.tex), and
[loss analysis](archived_appendix/analysis_detail.tex).
The [appendix audit](../revision/APPENDIX_AUDIT_20260917.md) documents the
artifact checks. [B8 checkpoint records](../data/b8_recovery/)
retain the Heat II and Burgers recovery details.

The portable ensemble program and paper rebuild use bundled predictions and
numerical records. Base model retraining and solver generation depend on the
separate benchmark and experiment archives, as stated in the paper.
