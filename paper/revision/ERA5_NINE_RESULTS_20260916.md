# ERA5 result incorporation and inference description

Section 3.1 now defines each library member as its complete inference procedure. It explicitly identifies nearest neighbour retrieval in standardized parameter space as the alternative to a learned coarse prediction. The user supplies only the new parameter input. Calibration and evaluation exclusions remain explicit.

The ERA5 source snapshot now contains all nine individual models, both calibration budgets, all three calibration selections, and all fitted ensemble rules. M8 and M9 completed on SuperCloud on September 15. The earlier seven model results have been replaced throughout the tables, climate discussion, appendix, workbook and Figure 1. The plot retains the illustrative coarse blur and explicit x, y and prediction labels requested previously.

## Results included

At five calibration examples, the selected POD GP gives 6.7369% relative L2 error. Inverse error weighting gives 5.8146%, a 13.69% relative improvement, and fitted stacking gives 6.4877%, a 3.70% improvement. Uniform weighting gives 6.3730%. All nine experts are available to every ensemble rule, although a fitted rule may assign zero weight to an available expert. M8 gives 20.3541% and M9 gives 8.2403%. The unchanged seven evaluation inputs are historical archive cases, not fresh years.

The imported baseline snapshot contains eleven completed B1 through B12 entries, excluding B8. They represent ten independent fits because B10 explicitly reuses B9. The training mean is also reported as B13. Each completed prediction was checked against its metadata hash, frozen protocol, input identities and target grid before scoring on the same seven ERA5 evaluation cases. The autoregressive POD GP baseline gives 5.0032%, better than either ensemble. The paper states this limitation of the library comparison.

At the final live check, B8 was still running on ORCD as job 22776600_5, at stage 2 epoch 1000 of 1875. The production collector 22776601 was waiting on that job. No training job, frozen worker source, or production collector was changed. The reporting code scores the available frozen subset locally and explicitly records that the full baseline campaign is incomplete. No B8 result is imputed.

## Reproduction and preservation

`scripts/build_era5_completion.py` validates the bundled predictions and reproduces all 36 saved ensemble predictions against their archived per case errors. It checks the original case roles, equal calibration and evaluation targets across campaigns, prediction hashes, and baseline recipe aliases. The source package includes the required prediction and answer arrays, metadata, saved weights, and manifests, so no cluster access is needed for rebuilding.

The abstract, bibliography, PDE aggregates, historical individual errors and dataset gallery are unchanged. The original manuscript remains untouched. Redundant main text was tightened to retain the ICLR limit of nine main pages without altering the format or the newly requested technical description.

The live cluster folders were read only. The local import snapshot is `mf_field_era5_results_for_paper_20260916`, with its reproducible contents bundled under `data/era5_completion`.
