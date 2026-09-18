# Completed ERA5 baseline coverage

Imported fidelity basis FNO predictions and metadata from the completed ORCD baseline campaign. Job 22776600_5 finished on September 16, 2026 at 11:29:54 Eastern. Collector 22776601 completed successfully at 11:34:14 Eastern.

The new B8 evaluation error is 0.0515025334760673, or 5.1503 percent, on the same seven evaluation inputs as the nine library members and ensemble rules. All twelve baseline entries are now present, representing eleven independent fits because B10 reuses B9. The training mean supplies the separate B13 control.

The reporting script verifies prediction and metadata identities, matching input rows, working grid, source and data manifests, and replays all baseline per case errors against the completed production collection. Original production outputs are retained under data/era5_completion/baselines/production_results. The B8 prediction and metadata are retained in their respective baseline folders.

Updated the ERA5 row in the detailed baseline table, main climate discussion, coverage descriptions, reporting workbook, and completion checks. Autoregressive POD GP at 5.0032 percent remains the best reported baseline. B8 at 5.1503 percent also beats the inverse mixture at 5.8146 percent and fitted mixture at 6.4877 percent. The nine expert predictions, calibration weights, ensemble scores, abstract, and PDE aggregate results remain unchanged. No training or weight fitting was performed. The original manuscript was not edited.
