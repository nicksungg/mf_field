# Complete B8 comparison and Elo ranking

## Resolving the missing comparisons

The original Heat II and Burgers B8 score files did not establish correspondence with the paper's evaluation cases. A search found trained checkpoints in the final campaign and other archives. An initial attempt to reproduce the Heat II archived errors from three saved checkpoints failed (ORCD job 22855021). These scores were not inserted by assuming that their row order matched.

Instead, job 22855488 evaluated the fixed `akash/checkpoints_final/s42/fno_coregionalization/<dataset>/best.pt` checkpoints for both datasets on the identified common test inputs. The same checkpoint rule was fixed for both datasets, without choosing whichever checkpoint had the best evaluation error. This was inference only, with no training, tuning, ensemble weight changes, or new simulations. The job used node2435 and excluded node2900, node4002, and node4200.

The two old result files are preserved under `data/b8_recovery/*__original_raw.json`. Fresh field predictions, targets, inputs, source hashes, checkpoint hashes, model code, and complete error vectors are bundled there. The new result records replace only the two B8 entries in the reporting inputs. `verify_b8_recovery.py` independently recalculates their errors and checks the frozen case provenance. The errors do not reproduce the old score files, and the manuscript describes them as fresh checkpoint evaluations rather than recovered old scores.

Mean relative L2 error on the paper's evaluation subsets, averaged over its three partitions:

* Heat II: 0.3201251088454657 percent.
* Burgers: 0.9282670861742585 percent.

The PDE baseline comparison now contains 221 verified entries (13 reference entries times 17 datasets). B1 through B11, M1 through M9, and the three reported ensemble rules all have results on all 18 datasets, including ERA5. Additional controls B12 and B13 are not part of Table 2's ranking.

## Table 2

Removed the coverage column. The PDE class ratio still uses the 17 PDE datasets across seven classes. The dataset ratio now includes all 18 datasets, including ERA5. Both ratios compare against the Selected model rule on the same dataset. The all dataset fitted mixture ratio is 0.9203074157243665, an 8.0 percent reduction after rounding, compared with the previous PDE only reduction of 8.2 percent. The PDE class reduction remains 12.4 percent. The fitted mixture improves on selection on 13 of 18 datasets using the existing one percent threshold.

Added Elo as the rightmost column and sorted all 23 rows by unrounded Elo. The implementation follows the release benchmark's ranking procedure: one comparison per method pair per dataset, all datasets included, initial rating 1500, K factor 32, scale 400, absolute error difference below 1e-12 treated as a tie, and 500 independently shuffled match orders with seeds 7 through 506. Each order resets the ratings. The displayed rating is the mean final rating, rounded to an integer. Variation across shuffles is saved for reproducibility, not interpreted as an experimental confidence interval. The first three rows are the Fitted mixture (1971), Inverse error mixture (1960), and Selected model (1860).

The new errors, ratios, matches, rankings, and per order variability are in `data/table2_ranking.json` and the `Table 2 ranking` workbook sheet. The appendix defines the rating update and each symbol. Source citations and M/B identifiers are preserved. The fixed 15 dataset sensitivity subset is retained and now described as excluding the two newly evaluated B8 entries. Other existing PDE analyses remain on their explicitly stated scope. The original manuscript is unchanged.
