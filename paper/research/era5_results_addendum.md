# ERA5 result update — September 14, 2026

The repaired ERA5 summary completed at 08:59 EDT. At the 09:20 EDT check,
the four remaining PDE ensemble summaries were still absent.

The seven retrained experts use 55 HF base examples; all ten calibration inputs
and seven evaluation inputs are excluded from every LF/HF training table.
The full automatic procedure selects full stacking on every subset, but the
fixed inverse-error rule has lower final error. At K=5, inverse improves 2.35%
relative to the training-mean field, whereas auto/full worsens 0.53%.
POD–GP is constant across all 17 reserved inputs and matches mean-field error
to displayed precision. The case plot shows that neither mixture wins every case.

These results are reported separately from historical20 and fresh heat.
Three calibration selections reuse the same seven evaluation cases and base
seed42. K10 uses the same full ten-case pool in each selection; these are not
independent replicates. Historical evaluation inputs are now excluded from
training, but they are not a fresh-year holdout. No significance, climate-impact,
or automatic-selection superiority claim follows from this experiment.

Evidence: data/era5_summary.json, data/era5_archive_checks.json,
data/era5/s{71,172,273}/{fit.json,evaluation.json,locked_weights.npz,per_case_errors.npz}.
All 21 means and 63 published CSV rows are recomputed by scripts/build_data.py.
Original report-source.md remains the historical literature/research snapshot;
this addendum and the updated claim-source ledger record the new results.


## September 16 completion update

The earlier text above records the historical seven expert experiment and is superseded for current reporting. The paper now uses all nine experts and their corresponding ensembles. With five calibration examples, inverse weighting gives 5.8146 percent error and fitted weighting gives 6.4877 percent, compared with 6.7369 percent for the selected POD GP.

All twelve additional baseline entries are complete, representing eleven independent fits because B10 reuses B9. The final B8 fidelity basis FNO run gives 5.1503 percent mean relative L2 error on the same seven evaluation cases. Autoregressive POD GP remains the best baseline at 5.0032 percent. Both beat the two reported mixture rules. The production collector and local replay agree on every baseline case score. See revision/ERA5_B8_COMPLETION_20260916.md and data/era5_baselines_summary.json.
