# Direct reported loss control result

> Historical review record from 15 September. Its roster dependent counts are superseded by [the 16 September scope update](SCOPE_UPDATE_20260916.md). The current manuscript and generated results use 19 settings, with 18 in the common aggregate.

All 60 historical partitions across 20 datasets completed at K=5. These are post hoc results on previously inspected predictions, not independent confirmation. No training changed and the original manuscript remains untouched.

Relative L2 direct fitting versus selected model: class ratio 0.8569965583, dataset ratio 0.9014462533, 14 wins and 6 losses.

Versus original squared fitted mixture: class ratio 0.9801764242, dataset ratio 0.9779963220, 11 wins, 0 losses, 9 within one percent.

Versus inverse weighting: class ratio 0.9766328638, dataset ratio 0.9759548343, 10 wins, 2 losses, 8 within one percent.

The three rule automatic selector was not modified to include this new post hoc candidate.

All weights were fitted and saved before evaluation. All existing selected, inverse and squared fitted evaluation vectors were reproduced to the specified numerical tolerance. Source hashes, row and input group identities, mean calibration Grams, cone solver status, PSD handling and simplex feasibility checks passed. Raw results, per case errors, saved weights and solver metadata are in data/loss_control. The check summary is qa/loss_control_checks.json.

Replay dependencies: numpy, scipy, cvxpy==1.9.2, clarabel==0.11.1. Run `python scripts/review_loss_control.py fit` then `python scripts/review_loss_control.py evaluate` from the copied manuscript. The archived evidence contains versions and hashes. The existing build need not rerun this numerical analysis to display its frozen table.
