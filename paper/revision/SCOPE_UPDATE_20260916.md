# Author requested roster update, 16 September 2026

The original Poisson archive (`poisson_generated`) and small cavity archive
(`lid_driven_cavity_generated`)
are removed from the current manuscript, every displayed results table, the
gallery and detail plates, the expert heatmap, and all reported aggregates.
The retained Poisson, cavity and ERA5 archives retain their data identities. This is a
reporting scope change, not a new model fit or a correction of retained fields.

The paper now contains 19 settings: 18 in the common nine member comparison
and the separate ERA5 experiment. Completing the four additional settings
would bring this roster to 23. Those runs are outside this manuscript snapshot.
This edit does not import newer ERA5 results or change the ongoing campaigns.

The removal follows the author's instruction after inspecting dataset
provenance. It is not an exclusion rule selected to improve ensemble scores.

## Recomputed results

* The historical comparison now has 54 partitions, 2,780 query pool rows,
  1,674 evaluation appearances and 1,368 distinct dataset and row identities.
* The fitted mixture improves on calibration based selection on 13 settings
  and worsens on 5. Class and dataset error ratios are 0.8730908791 and
  0.9153610430, corresponding to reductions of 12.7% and 8.5%.
* Against the hindsight best library member, the ratios are 0.9127739154 and
  0.9984021119. The equal dataset advantage is only 0.2%.
* Automatic selection is replayed for 162 fits. Its five field class and
  dataset ratios to the selected model are 0.8722258852 and 0.9096675466.
  It has 13 wins, 3 changes within 1%, and 2 losses.
* The direct relative L2 control reuses the original locked weights for the
  54 retained partitions. Its reductions against squared error fitting are
  2.0% across classes and 2.3% across datasets.
* There are 232 verified additional baseline cells. Common B1 to B11 coverage
  contains 16 settings. The audit sensitivity contains 15 settings and their
  intersection contains 13.

The retained per setting predictions, calibration memberships and original
fixed weights are unchanged. Archived source snapshots remain available for
provenance. `scripts/paper_scope.py` applies the reporting exclusions, and
`data/paper_mechanism_summary.json` contains newly computed aggregates. The
old mechanism snapshot is not used directly for published summaries.

The original direct loss fitting script is preserved in
`data/loss_control/fit_script.py`, with the exact hash recorded when those
weights were fitted. The current reporting script verifies that original
identity before evaluating the retained partitions.

Earlier dated review notes and fit protocols describe the preceding roster.
This note, the current README, manuscript and generated result files supersede
their scope dependent counts. Pooled exploratory gate and regularization
headline numbers tied to the larger archive are omitted from the manuscript.

The prior revision package is backed up outside the manuscript directory in
`../automf_revision_backups_20260916/before_dataset_removal.zip`. The original
manuscript in `../mf_field_automf_paper_20260914` is unchanged.

## Display labels after the subsequent author instruction

| Stable archive identifier | Current manuscript name | Previous name |
| --- | --- | --- |
| `poisson_generated_v2` | Poisson I | Poisson II |
| `poisson_local` | Poisson II | Poisson III |
| `lid_driven_cavity_v2` | Cavity I | Cavity II |

The renumbering changes only display labels. Dataset membership, predictions,
calibration partitions, citations attached to the imported archive, and all
computed errors remain unchanged. Older dated provenance notes use the former
names. Stable archive identifiers disambiguate them.
