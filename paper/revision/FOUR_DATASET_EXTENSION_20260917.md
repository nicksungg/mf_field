# Four dataset extension, 17 September 2026

This manuscript is a new copy. The previous manuscript remains at
`/archive/workspace/mf_field_automf_paper_review_revision_20260915`.
The preservation manifest records the SHA256 hashes of all 1,438 prior files.

## Scope

The primary comparison has 22 datasets: 21 PDE datasets and ERA5. The additions
are Allen Cahn, Cahn Hilliard II, Fisher KPP, and Phase field crystal. The original
Poisson, original cavity, and original Helmholtz exclusions remain unchanged.
The previously included Cahn Hilliard is now Cahn Hilliard I.

Every primary dataset has nine individual models, eleven additional baseline
entries, and all three reported rules. B9 and B10 use the same frozen recipe.
The four additions explicitly reuse the B9 predictions for B10, as does ERA5.
This is complete tabular coverage, not eleven independent model families.

## Provenance

The completed ORCD campaign is
`/archive/mf_field/experiments/four_baselines_20260915`.
Its completion marker verifies 36 individual model prediction archives and
52 additional baseline entries, including the two unranked classical controls.
The last two NOMAD tasks and final collector completed successfully.

`data/four_dataset_completion/IMPORT_MANIFEST.json` records 108 imported artifacts.
The build checks completion hashes, saved weights, query identities, disjoint
fitting and evaluation rows, nested budgets, finite errors, and all per case
means. Stored baseline error vectors are rescored on each evaluation partition.
Prediction metadata ties other entries to the completed campaign's archives.
Actual fine training row zero was imported for each new gallery panel, with
source file and array hashes checked against the data definition in PLAN.json.
No displayed field is borrowed from an older dataset definition.

## Recomputed findings

At five fitting examples, the fitted mixture improves by more than 1% on
16 of 22 datasets, worsens on five, and is within 1% on one.
Its geometric error ratio to the Selected model is 0.883953 across the seven
PDE classes and 0.925060 across all 22 datasets, reductions of 11.6% and 7.5%.
The comparison is to a model selected on the same fitting examples.
The best library member beats the best additional baseline on 15 of 21 PDE
problems. This last comparison uses retrospective evaluation minima.
Seven of the nine library members lead on at least one PDE dataset.
Fitted and inverse error mixtures occupy the first two Elo positions.

The four added tasks favor four different library members. Fitted mixture gains
relative to the Selected model are 12.15% on Allen Cahn, 5.68% on Cahn Hilliard II,
2.76% on Fisher KPP, and 0.28% on Phase field crystal. The last is within the
paper's 1% neutrality threshold. Absolute errors on the harder tasks remain high.

## Updated artifacts and explicit diagnostic scope

The abstract, introduction, experiments, results, discussion, conclusion,
reproducibility statement, all primary tables, Elo, class and budget curves,
individual model heatmap, dataset gallery, detailed field plates, and inventory
use the expanded roster. The workbook and source package reproduce these values.

Detailed error geometry, automatic rule reanalysis, direct loss fitting, and
related sensitivity controls still cover the original 17 PDE datasets. These
analyses are labeled as a diagnostic subset throughout. Their historical values
are not silently reinterpreted as covering the four additions. The separate fresh
heat check and ERA5 experiment are unchanged. The original fixed predictions
and data sources remain retrospective evidence, not independent confirmation.

## Validation

The manuscript builds in the supplied ICLR 2026 template with nine main text
pages. Numeric and structural checks verify the primary scope, all dataset rows,
source hashes, mixture identities, aggregate calculations, deterministic Elo,
citations, and page limit. Visual inspection covers the main text and updated
appendix figures and tables. The packaged source is rebuilt from a clean
extraction and its tables and rendered text compared with the delivered PDF.
