# Complete baseline coverage for the four additional paper datasets

## Scheduling update, September 16

Eight of the ten new fits have completed. The remaining NOMAD fits on Allen Cahn and phase field crystal remain in the existing array `22807011`, indices 2 and 6. That array is now eligible for both `mit_normal_gpu` and `mit_preemptable`, with Slurm choosing one partition for each task. No duplicate jobs were submitted. The existing H200 request, six hour limit, requeue setting, two task concurrency limit, and exclusions for nodes 2900, 4002 and 4200 are preserved. The collector `22807198` still depends on this same array. The plain `mit_normal` partition has CPUs only and continues to host the collector. This live scheduling override supersedes the single partition routing for those two indices below; the original submission scripts are historical records, not extra jobs to submit. See `monitor/NOMAD_MULTIPARTITION_20260916.json` for before and after scheduler evidence.

User instruction: preserve the paper's historical 20 datasets plus ERA5 and complete the baselines for the remaining four datasets. This campaign does not activate the separate corrected 25 dataset roster. Neither manuscript is edited.

The four are Cahn Hilliard II, Fisher KPP, Allen Cahn and phase field crystal. All 36 individual expert predictions and all four nine expert ensemble evaluations already exist.

| Dataset | New independent fits |
| --- | --- |
| Cahn Hilliard II | None |
| Fisher KPP | MFRNP, FNO coregionalization |
| Allen Cahn | NOMAD, MFRNP, FNO coregionalization, FNO transfer |
| Phase field crystal | NOMAD, MFRNP, FNO coregionalization, FNO transfer |

The release's results/README.md records that the latter three datasets were redefined after the legacy paper baseline runs. Fisher KPP changed from 2 to 50 input parameters, Allen Cahn from 3 to 19 with 78 current test cases, and phase field crystal from 2 to 18. Their incompatible legacy checkpoints are not evidence of completed current-definition runs. Current-definition Fisher KPP NOMAD and transfer results are already available and are reused.

Forty of 52 baseline table entries are ready. Ten new fits produce the remaining twelve entries because the two transfer labels have identical frozen architectures and executable recipes. No second independent fit is claimed for that alias. For Fisher KPP, its completed transfer-bar fit supplies both equivalent labels. The other two datasets receive one new transfer fit each.

Reuse follows the existing manuscript comparison standard. Statistical results have matching file hashes. Cahn Hilliard II paper baselines have matching saved target rows and original per-case error arrays. Fisher KPP's two current reruns are verified against original raw results, current conditioning dimensions, recorded parameter counts, the documented release data revision and the original launcher/loader ordering. Historical training-file hashes remain unavailable for those paper results; this limitation is retained rather than used to trigger wholesale reruns.

Training uses the four datasets' existing prepared training tables and zero-valued query placeholders. Calibration and evaluation answers remain separate. Reserved inputs are excluded from every training fidelity. Each new fit begins with a short GPU check on its actual dataset and then follows the frozen baseline recipe. The new paper fits use 2500 epochs, or separate 2500 epoch LF and HF stages for transfer models. Historical results retain their original recorded budgets. These are common evaluation cases and available data pools, not equal compute budgets.

Jobs:

* Preparation and artifact checks: 22806574, completed successfully.
* Training on `pi_faez`: 22807197, task indices 1, 4, 5 and 8, at most two simultaneous H100 GPUs, with a 96 hour limit.
* Training on `mit_normal_gpu`: 22807011, task indices 2 and 6, at most two simultaneous H200 GPUs, with a 6 hour limit.
* Training on `mit_preemptable`: 22807014, task indices 0, 3, 7 and 9, at most two simultaneous H200 GPUs, with a 48 hour limit and Slurm requeue enabled. The workers preserve optimizer and random state in resumable checkpoints.
* Automatic collection: 22807198 on the CPU partition `mit_normal`, after successful completion of all three arrays. It compares all thirteen baseline entries, all nine experts and the ensemble rules on identical evaluation rows, and writes results/comparison.csv plus results/COMPLETE.json.

All three training arrays exclude nodes 2900, 4002 and 4200. Each of the ten task indices belongs to exactly one partition. The existing ERA5 baseline campaign remains untouched. No duplicate SuperCloud fits are submitted. See JOBS.json, ROUTING_JOBS.json, PARTITION_ROUTING.json, TASKS.json, COVERAGE.json and REUSE.json for the exact inventory and provenance. All scientific training/configuration sources remain frozen in SOURCE.json. PARTITION_ROUTING.json records the current scheduling override to the older exclusions stored in PLAN.json.

The old pending array 22806679 and its collector 22806680 were cancelled before training started. The first partitioned pi_faez attempt, 22807010, failed its staged-data path check before training. Its dependent collector 22807015 was cancelled automatically. The dataset folder symlinks were replaced with hash-identical copies inside this campaign's data directory, preserving the strict path check and all frozen scientific sources. STAGING_FIX.json records that correction. The current scripts are train_pi_faez.sbatch, train_mit_normal_gpu.sbatch and train_mit_preemptable.sbatch. The original train.sbatch is superseded and must not be submitted alongside these arrays.
