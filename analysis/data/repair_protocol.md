# ERA5 repair and missing ensemble coverage

Authorized 2026-09-13. Remote: `/archive/mf_field/experiments/automl_repair_20260913`.
Every Slurm job excludes node2900 and node4200. Historical checkpoints, data and results stay intact.

## ERA5 corrections

The 65 original HF training rows become 55 base-training rows plus 10 calibration rows (original rows 55–64).
The seven original HF test rows remain evaluation rows. Every occurrence of any of these 17 reserved input
vectors is removed from every LF/HF training table, using exact float32 parameter identity. No old ERA5
checkpoint is reused. The experiment establishes input disjointness; it is not a strict forecast-origin
experiment, and no fresh-year claim is made. Calendar dates are not inferred from row positions.

The original all-pairs implementation paired source inputs with target fields by row index and also used
source-level inputs for HF finetuning. All 36 ERA5 fidelity pairs have misaligned input rows in the original
data. The repaired pooled training uses exact input joins and keeps each target field with its own input.
HF finetuning also uses the HF field's own parameters. The separate 25-dataset check finds this positional
pairing defect only in ERA5. Paired datasets retain their original input/target association.

The ERA5 pool comprises FiLM-FNO transfer, repaired all-pairs FNO, ConvNeXt transfer, FIRE, WNO transfer,
DeepONet, and HF-only POD-GP. The two OOF correctors require paired LF/HF data and remain explicitly
unavailable for ERA5. A separately trained fine-only FNO and a training-mean field are controls.

## Other runs

Sharp Cahn–Hilliard reuses the seven independently audited direct prediction arrays and adds its missing
coarse ensembles and Transolver/ConvNeXt correctors. Fisher–KPP, Allen–Cahn and phase-field crystal retrain
the six neural direct experts on the current data, refit POD-GP, and add both correctors. A fine-only FNO
is trained for each. This avoids relying on incomplete or ambiguous historical checkpoint coverage.

For each paired dataset, the coarse stage trains five folds × four members (plain/hetero × seeds 42/123).
Every training row gets four OOF predictions. Query inputs get exactly the four members from fold zero,
preserving ensemble size across training and inference. Members use 30,000 requested optimizer steps;
the inherited coarse trainer rounds to whole epochs. Correctors use 6,000 steps and six refinements.

Direct neural recipes retain the original 2,500-epoch setting and architecture. DeepONet retains its
original conversion to 125,000 optimizer steps. Other architectures have different update counts, as in
the baseline recipes; this is not a matched-total-compute claim. FNO/ConvNeXt/WNO/all-pairs/FIRE training
now checkpoints each stage, optimizer, scheduler and RNG state periodically for preemption recovery.
DeepONet's shorter run retains its existing finished-checkpoint behavior. Predictions use strict FP32
without TF32; full jobs request H200 GPUs. The working grid remains capped at side length 256, so ERA5
is evaluated at 128×256 rather than its native 721×1440 grid.

## Calibration and scoring

ERA5 tests calibration budgets 5 and 10. The four PDE datasets use three fixed 80/20 partitions of the
historical base-model test inputs into calibration pool/final evaluation, with nested budgets 5/10/20.
All case roles are assigned from input hashes before training. Base seed is 42; the three calibration
partitions are not independent base-training seeds.

The pipeline reports full convex stacking, inverse-MSE weights, calibration-selected single expert,
uniform averaging, repaired all-pairs, fine-only FNO, and the training mean. The `auto` rule uses
leave-one-out calibration error to choose among the single expert, inverse-MSE mixture and full mixture,
then refits that choice on the available calibration examples. All alternatives and losses are retained.
One weight per expert is used for the complete field. No evaluation score chooses the model or rule.

Training trees contain zero placeholders for query fields. Actual calibration and evaluation targets are
stored in separate files; training wrappers reject attempts to load the answers directory. Collectors
fit and save weights before opening the evaluation target file for their partition. A regression test
changes the final answers and verifies that this cannot change the learned weights.

## Remaining interpretation issues

The legacy-cavity test inputs occur in corrected-cavity training. Their separate within-dataset mixtures
do not cross-use checkpoints; both versions must be grouped for family holdouts. Use the corrected
cavity as the primary physical dataset and retain legacy cavity as a diagnostic. Similarly, corrected
Poisson is available for physical interpretation of the legacy scaling defect. Regenerating every legacy
PDE field is outside this checkpoint/split repair campaign. Existing generator-quality limitations,
incomplete conditioning and synthetic coarse levels remain documented in the earlier dataset audit.

Lower final error is an outcome to measure, not a reason to keep rerunning a dataset until it wins.
These historical cases have already informed development, and all results must be reported accordingly.

## Execution

Preparation and smoke jobs precede source freezing. `launch.py` submits direct models, four independent
coarse arrays, dependent OOF assembly and corrector jobs, and a collector per dataset. At most eight
training GPUs are requested concurrently: four direct tasks and one coarse/corrector task per paired
dataset. Dependency jobs do not occupy resources while waiting. `LAUNCH.json` records every submission.

Files: `PLAN.json`, `PREPARED.json`, `ROLES.json`, `PAIRING_AUDIT.json`, `SOURCE.json`; per-model artifacts
in `predictions/` and `metadata/`; resumable checkpoints in `checkpoints/` and `uqcorr/`; per-dataset
summaries, locked weights and per-case errors in `results/`.
