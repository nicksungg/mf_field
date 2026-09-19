# Extra inputs, local field summaries and additional surrogates

**Adding the predicted-coarse Transolver and ConvNeXt correctors helped the fixed mixture. Adding input parameters and local field summaries did not improve the adaptive weight chooser in this test.**

The ORCD pilot is complete: feature preparation and all six fitting/evaluation tasks finished successfully. There are no remaining jobs in this campaign. Nodes 2900 and 4200 were excluded throughout.

## What was compared

Two pools use exactly the same 20 datasets, seven classes, 2,890 historical cases and three case partitions:

- **Seven models:** FiLM-FNO transfer, all-pairs FNO, ConvNeXt transfer, FIRE, WNO transfer, DeepONet and HF-only POD-GP.
- **Nine models:** those seven plus the uqcorr **Transolver-pred** and **ConvNeXt-pred** correctors. Both use a four-member predicted coarse ensemble, seed 42 and six refinement steps. The ConvNeXt corrector is distinct from the ConvNeXt transfer model already in the seven.

For each pool we tested four versions of the model-specific weight chooser: current 20 global field summaries; those summaries plus actual simulation inputs; plus 24 local field summaries; and plus both. Local summaries cover four quadrants, an outer 10% edge band and the interior. Simulation parameters retain separate meanings for each dataset, with fitting-only scaling. There are 70 input coordinates across the 20 datasets.

Every version still produces **one weight per model for the entire field**, with nonnegative weights summing to one. No spatially varying weights were trained. Each split has 1,733 fitting, 577 tuning and 580 evaluation cases. The same bounded linear scoring rule, 400 updates, three penalties and tuning-based fixed-mixture fallback apply throughout.

## Result 1: the additional features did not help this chooser

In **all 24 pool/split/feature-variant combinations**, tuning retained the fixed-mixture fallback. Thus current features, added inputs, added local summaries and both additions produced identical final evaluation predictions within each pool and split.

| Pool | Current features | + inputs | + local summaries | + both |
|---|---:|---:|---:|---:|
| Seven models: error / fit-only fixed mixture | 1.000 | 1.000 | 1.000 | 1.000 |
| Nine models: error / fit-only fixed mixture | 1.000 | 1.000 | 1.000 | 1.000 |

A stronger static control uses every fitting plus tuning label to fit its weights. The retained fit-only mixtures are 1.18% worse than that control in the seven-model pool and 0.76% worse in the nine-model pool. That small difference comes from calibration labels available to the final static fit; it is not an improvement attributable to field features.

The result is specific to this small bounded linear chooser and its tuning rule. It does not prove that the added inputs contain no useful information, or that a different adaptive method could not use them. The scoring architecture and the original seven-model predictions were held consistent; the original seven static control weights reproduce earlier saved weights within 1e-7 on the retained datasets.

## Result 2: the broader model pool helped

Using the stronger fixed mixture in both pools, nine models have **6.92% lower class-balanced error** than seven models. Ten datasets improve by more than 1%, two worsen by more than 1%, and eight change by less than 1%.

| Dataset | Seven-model fixed mixture | Nine-model fixed mixture | Relative change |
|---|---:|---:|---:|
| Corrected cavity | 0.2368% | **0.1377%** | 41.9% lower |
| Legacy cavity | 0.2958% | **0.1249%** | 57.8% lower; only two evaluation cases per split |
| Porous medium | 0.02815% | **0.02556%** | 9.2% lower |
| Local heat | 0.004498% | **0.004252%** | 5.5% lower |
| Generated heat | 0.006028% | **0.005803%** | 3.7% lower |
| Wave | 4.351% | **4.283%** | 1.6% lower |
| Euler | 5.620% | **5.556%** | 1.1% lower |
| Darcy | 2.251% | 2.251% | Essentially unchanged |
| Rayleigh–Benard | **0.003003%** | 0.003431% | 14.3% higher |
| Sharp Helmholtz | **4.150%** | 5.123% | 23.5% higher |

These are mean relative L2 errors expressed as percentages and averaged over the three meta-data partitions. Aggregate gains use geometric dataset error ratios balanced within classes and across classes. The 6.92% is not an arithmetic mean reduction.

The corrected cavity gains occur in all three partitions (nine/seven ratios 0.572, 0.595 and 0.576). Sharp Helmholtz's aggregate loss comes from one partition (ratio 1.521); the other two are essentially tied. Rayleigh–Benard worsens in all three. These descriptive repetitions are not independent base-model training seeds or significance tests.

The cavity mixtures assign the ConvNeXt corrector about **68% weight** on corrected cavity and **85%** on legacy cavity, averaged over partitions. The wave mixture assigns Transolver about **10.7%** and the ConvNeXt corrector about 0.02%. Both added models receive essentially zero weight on Darcy. This is consistent with usefulness depending on the dataset. Since both models were added together, these weights do not replace a separate ablation attributing gains to each model.

The nine-model fixed mixture also has 14.1% lower class-balanced error than selecting one of those nine models using the same fitting+tuning labels. The seven-model fixed mixture has 12.7% lower error than its corresponding selected-single-model control. These compare ensembles to selection using calibration answers, not an oracle that selects using evaluation answers.

## The older Transolver versions

The earlier **TransolverResidual** baseline has saved reevaluation errors of approximately 1.42% on Darcy and 1.49% on Euler. On paired NPZ datasets its evaluator uses **real coarse test fields**, so those results have a different prediction-time input budget. The same loader's alternate HF-only directory path can synthesize coarse input from the fine answer; that is a separate branch, not a reason to label the paired NPZ results as HF-answer leakage.

The older **FNO → Transolver sequential hybrid** also exists. Fourteen current datasets have historical records; all specify real-LF context, with correction active on four and zero on ten. In the zero-correction cases, including Darcy, Euler and wave, its output is its FNO base. The present solver-free pool adds the newer predicted-coarse corrector rather than silently treating the older real-coarse results as parameter-only predictions. See [variant audit](TRANSOLVER_VARIANTS.md).

## Interpretation and checks

This test supports expanding a calibrated ensemble with predictors that help on particular datasets. It does not yet support per-case adaptation from the extra features we tried. The largest aggregate gains are concentrated in cavity; additions can also overfit calibration cases and hurt another dataset.

The new correctors' inputs, grids and targets match the seven-model corpus. Maximum target discrepancy is 3.26e-8 in relative L2, and no evaluation inputs overlap the correctors' LF/HF training inputs. The saved corrector outputs are float32; their original TF32 settings were not recorded. The seven original neural outputs use the earlier strict-FP32 export. All methods within each pool use the same candidate arrays and canonical targets, so numerical inference differences are not changed during mixture comparison. No base-model training or new GPU inference was needed.

Four implementation tests passed locally and on ORCD. They check localized disagreement hidden by global summaries, case independence/model permutation, fitting-only parameter scaling and a synthetic case where parameters should control model preference. The caches reproduce the original seven-model features and error matrices. All six final artifact audits passed: source hashes, split identities, disjoint input groups, convex weights and saving/hashing evaluation weights before scoring.

This is exploratory reuse of historical benchmark data already consulted during method development. Extra fine labels for calibration count beyond base training labels. Sharp Cahn–Hilliard lacks the two added correctors and is excluded from both pools; climate remains excluded because its inputs appeared in LF training. Known legacy defects, including unlearnable ext Helmholtz, remain visible. No fresh-test, matched-total-compute, statistical-significance or lower-total-HF-label claim follows. Adding more feature coordinates also increases parameter count; this experiment is not a strict capacity-matched comparison.

An initial submission stopped at a missing-source-manifest preflight before any scientific fitting; its dependencies were cancelled. The manifest setup was fixed, the user-requested expert expansion was incorporated before any results existed, and the final source was frozen before the successful campaign. No additional experiment was launched after inspecting these results.

Artifacts: [full results](RESULTS.md), [CSV](results.csv), [plot](comparison.png), [PDF plot](comparison.pdf), [verification](QA.json), [preparation audit](PREPARATION.json). Remote: `/archive/mf_field/experiments/fieldgate_features_20260913`. Successful jobs: preparation `22671126`, fitting array `22671127`, collection `22671128`.
