# Dataset overlap and ensemble outcome audit

The ORCD input arrays were reread independently for all 25 datasets in the release roster. ERA5 is the only dataset with HF-test parameter vectors repeated in its own LF training files: 7/7 cases. No HF-training overlap was found in any dataset. The other 24 pass this specific same-dataset input-membership check.

The check reproduces all 154 available seven-model export overlap flags and input row orders. On the 20-dataset nine-model corpus, both correctors also have no training-input overlap; their test-row mappings reproduce the saved mappings. All 60 dataset/partition runs pass an independent check of calibration/evaluation identities, nested budgets, saved weight hashes, answer-access records, and reported errors.

## A separate cross-version overlap

All 10 legacy-cavity test inputs occur in the corrected-cavity training data. They do not occur in the legacy-cavity training data. The fixed mixtures evaluated here use only the experts trained for their own dataset, so the corrected-cavity model is not an expert in the legacy-cavity mixture. Nevertheless, the two versions must not be presented as independent unseen physical problems. A claim that no model anywhere has seen those input values would be false. Keep both versions together for problem-family holdouts. The calibration/evaluation groups remain disjoint even when pooling the related versions.

## Every dataset, including missing ensemble coverage

| Dataset | HF test cases | LF input matches | HF input matches | Nine-model result |
|---|---:|---:|---:|---|
| poisson_generated | 100 | 0 | 0 | Available |
| poisson_local | 512 | 0 | 0 | Available |
| heat_generated | 100 | 0 | 0 | Available |
| heat_local | 512 | 0 | 0 | Available |
| darcy_generated | 100 | 0 | 0 | Available |
| lid_driven_cavity_generated | 10 | 0 | 0 | Available |
| fluid | 256 | 0 | 0 | Available |
| era5 | 7 | 7 | 0 | LF test-input overlap; ERA5 diagnostic only |
| ext__helmholtz_2d | 100 | 0 | 0 | Available |
| ext__rayleigh_benard_2d | 100 | 0 | 0 | Available |
| ext__wave_2d | 100 | 0 | 0 | Available |
| ext__eikonal_2d | 100 | 0 | 0 | Available |
| ext__cahn_hilliard_2d | 100 | 0 | 0 | Available |
| ext__pressure_poisson_poiseuille | 100 | 0 | 0 | Available |
| sharp__euler | 100 | 0 | 0 | Available |
| sharp__burgers_2d | 100 | 0 | 0 | Available |
| sharp__shallow_water_2d | 100 | 0 | 0 | Available |
| sharp__cahn_hilliard | 100 | 0 | 0 | Seven-model corpus available; two corrector experts missing |
| sharp__porous_medium_2d | 100 | 0 | 0 | Available |
| sharp__helmholtz_2d | 100 | 0 | 0 | Available |
| sharp__fisher_kpp_2d | 100 | 0 | 0 | Missing common base-export coverage in the current ensemble corpus |
| sharp__allen_cahn_2d | 78 | 0 | 0 | Missing common base-export coverage in the current ensemble corpus |
| sharp__phase_field_crystal_2d | 100 | 0 | 0 | Missing common base-export coverage in the current ensemble corpus |
| poisson_generated_v2 | 100 | 0 | 0 | Available |
| lid_driven_cavity_v2 | 100 | 0 | 0 | Available |

These are input-array counts, not the number of independent physical problems. The nine-model corpus has 2,890 cases, of which each partition reserves 580 for final evaluation; only two final legacy-cavity cases occur per partition. The other cases form the calibration pool. Three partitions reuse the same trained experts and are not three independent training seeds.

## Does the ensemble reduce reserved-case error?

The primary budget is five calibration fields per dataset. Those labels are additional to base training labels. Each mixture is compared with a single expert selected using the same calibration labels. All-pairs receives no corresponding extra fitting with these labels, so it is a useful named baseline but not a matched-total-label comparison.

| Calibration budget | Better than selected single (>1%) | Worse (>1%) | Within 1% | Better than all-pairs (>1%) |
|---|---:|---:|---:|---:|
| 5 | 14/20 | 6/20 | 0/20 | 17/20 |
| 10 | 14/20 | 4/20 | 2/20 | 19/20 |
| 20 | 14/20 | 5/20 | 1/20 | 19/20 |

Legacy cavity has only eight calibration-pool cases, so nominal budgets 10 and 20 both use eight there. The full mixture has 12.6% lower class-balanced geometric error than the selected singleton at budget five; at budget ten the reduction is 13.9%. These are aggregate descriptive improvements, not universal gains or significance claims.

### Primary five-calibration-field results

Errors are mean relative L2 percentages, averaged over three partitions. Negative changes favor the mixture.

| Dataset | Selected single | Full mixture | All-pairs | Change vs selected single |
|---|---:|---:|---:|---:|
| darcy_generated | 2.52202% | 2.3329% | 3.44071% | -7.50% |
| sharp__euler | 6.09279% | 5.7324% | 6.07621% | -5.92% |
| heat_generated | 0.00971632% | 0.00620325% | 0.0125158% | -36.16% |
| poisson_generated | 0.00377941% | 0.00397344% | 0.0672691% | +5.13% |
| ext__cahn_hilliard_2d | 12.1614% | 10.6611% | 12.5249% | -12.34% |
| ext__eikonal_2d | 1.80881% | 1.76395% | 2.1513% | -2.48% |
| ext__helmholtz_2d | 131.863% | 115.246% | 118.026% | -12.60% |
| ext__pressure_poisson_poiseuille | 0.0733517% | 0.0802409% | 0.0695322% | +9.39% |
| ext__rayleigh_benard_2d | 0.00300899% | 0.00268826% | 0.00915009% | -10.66% |
| ext__wave_2d | 4.84073% | 4.27458% | 6.30928% | -11.70% |
| fluid | 1.6069% | 1.49667% | 1.68521% | -6.86% |
| heat_local | 0.00661984% | 0.00435085% | 0.00878319% | -34.28% |
| lid_driven_cavity_generated | 0.136143% | 0.124635% | 0.75784% | -8.45% |
| lid_driven_cavity_v2 | 0.164294% | 0.141696% | 0.289895% | -13.76% |
| poisson_generated_v2 | 0.00684342% | 0.00788219% | 0.0387161% | +15.18% |
| poisson_local | 0.012093% | 0.0129128% | 0.535569% | +6.78% |
| sharp__burgers_2d | 0.516186% | 0.501656% | 0.533461% | -2.81% |
| sharp__helmholtz_2d | 6.24593% | 6.5522% | 3.47758% | +4.90% |
| sharp__porous_medium_2d | 0.0324973% | 0.0263209% | 0.0324973% | -19.01% |
| sharp__shallow_water_2d | 0.366692% | 0.388548% | 0.366692% | +5.96% |

All budgets and every dataset comparison are included in `per_dataset_errors.csv`; no dataset-specific method is picked using its evaluation score.

## What this supports

The defensible application target is an automatic procedure trained separately on each user dataset, selecting models and weights with reserved calibration examples, then predicting new held-out parameter inputs. The base models may train on other cases of that same dataset. This claim does not require the base models to generalize to a wholly untrained PDE family.

The current evidence supports lower reserved-case errors on most of the 20 completed datasets, not all 25 and not every dataset. To claim coverage of the full roster, fix the ERA5 split and retrain for the desired unseen-input protocol; complete the missing expert coverage for sharp Cahn–Hilliard, Fisher–KPP, Allen–Cahn and phase-field crystal; and report all failures alongside gains. An automated choice between a singleton and a mixture must be made from calibration data rather than whichever one wins on the final test.

## Limits of this check

- Equality is assessed at float32 precision, matching the current model inputs. No field answers were loaded by the independent ORCD input scan.
- This rereads current training files and reconciles current export artifacts. It is not a reconstruction of every historical checkpoint training history or a certification of all 24 baseline implementations.
- The disjoint calibration/test check is within each saved run. Across repeated partitions a case can change roles, and these historical outcomes have already influenced research decisions. A frozen procedure still needs fresh confirmation for a strong paper claim.
- Passing input membership does not fix the separately documented generator defects, incomplete conditioning, synthetic coarse levels or missing cost accounting. See the existing `mf_field_session_20260905/datafix/DATASET_ISSUES_2026-09-06.md`; those issues need their own per-dataset handling.
- No new models were trained, no jobs were cancelled, and no Slurm jobs were submitted by this audit.

## Reproduce

Run `audit_remote.py` on ORCD with the factory_mffp Python, redirect its JSON output to `raw_input_audit.json`, then run `python build_report.py` locally. `QA.json`, `dataset_coverage.csv`, and `per_dataset_errors.csv` retain every checked dataset and comparison.
