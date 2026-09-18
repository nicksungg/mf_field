# Future comparison on 25 corrected dataset settings

Status: deferred by the user on September 14, 2026. This document is a plan, not a launch instruction. The current paper keeps its existing 20 historical dataset settings plus ERA5, for 21 in total. Existing cluster jobs retain their prior authorization. No new training is submitted for this plan.

## Dataset scope

Use the 25 entries labeled 2D in `overleaf_interpretability_reframed (1).zip` as the identity list. Heat outputs are space and time arrays, and related parameterizations or sample budgets are settings of the same physical family.

Use corrected fields in place of erroneous Poisson fields, retaining each setting's original parameters, grids, and sample counts. The standard corrected Poisson dataset already exists. The MFRNP and IFC Poisson settings require correction and solver checks before reuse. Use the larger converged cavity dataset for the cavity entry. Restore IFC Heat and IFC Poisson. Do not count older and fixed copies of the same setting as additional datasets. Keep original files in the provenance archive, outside new training and scoring.

The proposed roster is:

| Group | Settings |
| --- | --- |
| Elliptic | Standard Poisson, MFRNP Poisson, IFC Poisson, Darcy, Helmholtz I, Helmholtz II, Eikonal, Pressure Poisson |
| Heat | Standard heat, MFRNP heat, IFC heat |
| Shocks | Burgers, Euler |
| Convection | Navier Stokes, cavity, Rayleigh Benard |
| Porous flow | Porous medium |
| Reaction diffusion | Allen Cahn, Cahn Hilliard I, Cahn Hilliard II, Fisher KPP, phase field crystal |
| Waves | Wave, shallow water |
| Climate | ERA5 |

This is 25 benchmark settings. Pressure Poisson's synthetic coarse data and Cahn Hilliard I's incomplete input conditioning require explicit handling and disclosure. A fixed count is not a certificate of solver correctness. Dataset selection and fixes must not depend on which methods win the evaluation.

## Implementation sequence

1. Freeze a single manifest with data versions, field quantities, grids, parameter definitions, file hashes, and training, validation, calibration, and evaluation input identities. Group related settings for any family holdouts.
2. Verify each Poisson correction by checking the original discrepancy and solving representative parameter cases. Verify that cavity uses the converged archive. Preserve parameter identities and label the adaptations to imported benchmarks.
3. Remove all reserved evaluation and calibration inputs from every relevant LF and HF base training table. For unpaired data, predict coarse fields at HF inputs and construct predictions excluding each training input's own observed LF occurrence.
4. Reuse existing checkpoints or predictions only when their data, input roles, and preprocessing match the frozen specification. Retrain every affected model when targets, training inputs, or preprocessing change.
5. Fill the agreed paper baseline library and all nine individual experts, counting shared models once. Train each corrector's shared coarse ensemble once. Save field predictions and per case errors on identical evaluation inputs.
6. Fit every mixture using the reserved calibration labels only. Save the weights before opening evaluation answers. Report the individual models, baseline methods, and ensemble rules on the same rows, with failures explicitly visible.
7. Record LF and HF label exposure, calibration labels, training compute, and inference cost. Distinguish matched evaluation inputs from matched training budgets.
8. Rebuild tables and aggregate statistics from the finalized roster. Do not reuse the current 20 dataset numerical aggregates under a 25 dataset heading.

## Time allowance

The earlier estimate of 3 to 7 days, roughly one week, is a provisional planning allowance for selective completion with compatible result reuse and regular access to four to eight GPUs. It is not a measured forecast for retraining every method on every setting. Queue delays, source compatibility, and the final missing run inventory can extend it. Estimate again from the frozen manifest and production training timings before launching.

## Current paper checkpoint

The current 21 setting paper retains its historical data versions and disclosed limitations. Deferring this plan does not silently correct those data or replace their reported errors. The historical 20 have all nine experts and the stored ensemble rules. ERA5 currently has seven experts and their mixtures, with M8, M9, and the nine expert ensemble refresh still pending.

For a fully populated 21 by 22 individual model table, the outstanding cells are M8 and M9 on ERA5, B1 through B12 on ERA5, and B8 on Heat II and Burgers. The existing source audit does not independently establish the two B8 case mappings. Old ERA5 baseline errors cannot be imported onto the new split. These gaps remain explicit in the current manuscript.

See `dataset_roster_history.md` for the source records behind the roster differences and cavity naming conflict.
