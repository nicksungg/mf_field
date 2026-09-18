# ERA5 nine model run status

Submitted on September 14, 2026 to SuperCloud, `archive-host`.

M8 is the Transolver inspired slice attention corrector. M9 is the ConvNeXt corrector. Both use coarse surrogate predictions at the fine input parameters. Their new data path does not require matching observed coarse answers. The seven existing ERA5 experts are reused.

The GPU preflight, job **5621590**, completed successfully in 4 minutes 17 seconds. All 16 tests passed, all 20 coarse members completed short training checks, and both correctors completed a training step and generated finite predictions on the full 128 by 256 working grid. These smoke outputs are isolated and are not scientific results.

| Stage | Job | Submission status |
| --- | --- | --- |
| Train 20 coarse members, at most four concurrently | 5621602 | Queued, `AssocGrpNodeLimit` |
| Assemble coarse predictions | 5621603 | Waiting for all coarse members |
| Train M8 and M9 | 5621604 | Waiting for assembly |
| Fit and evaluate nine model ensembles | 5621605 | Waiting for both correctors |

Every later stage requires successful completion of its predecessor. The production runs are queued, not yet training at this status check. The existing SuperCloud campaign is unchanged.

The input roles remain 55 fine base training cases, ten calibration cases, and seven evaluation cases. Reserved input identities occur in neither coarse nor fine base training. The correctors use 49 of the base cases for fitting and six for validation. Coarse predictions for fine training inputs come from models that excluded those input identities. The ensemble uses calibration budgets of five and ten, with evaluation answers opened only after weights are saved.

The collector requires all nine experts and checks nine dimensional weights for selected single, inverse error, full convex, uniform, and automatic rule selection. A learned rule can assign zero weight to an available model. The fine only control remains separate.

Submission commands are recorded in [LAUNCH.json](LAUNCH.json). The GPU check is recorded in [PREFLIGHT.json](PREFLIGHT.json). The frozen protocol is [EXPERIMENT.json](EXPERIMENT.json), with source hashes in [SOURCE.json](SOURCE.json).

Remote folder: `/archive/user/mf_field/experiments/era5_nine_20260914`.

Final outputs will be `results/era5__summary.json`, `results/era5.csv`, and `results/NINE_EXPERT_AUDIT.json` in that folder. No completed production result is available yet.
