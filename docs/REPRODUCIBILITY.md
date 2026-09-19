# Reproducing AutoMF

Choose the level of reproduction you need. The manuscript is not included or required.

| Task | Download | Command | What it does |
|---|---|---|---|
| Try ensemble fitting | Ordinary clone only | `python scripts/example_ensemble.py` | Fits three rules on five cases and scores five different cases |
| Check aggregate results | Ordinary clone only | `python scripts/reproduce_results.py --elo` | Recomputes ratios and Elo from unrounded saved dataset errors |
| Replay frozen analyses | Analysis LFS arrays | `python scripts/reproduce_results.py --full` | Rebuilds numerical summaries, tables and figures from per-case records |
| Retrain models | Required dataset/campaign arrays | See [training](TRAINING.md) | Trains new models using the supplied implementations |

The first two commands need `requirements-demo.txt`. They do not retrain base models. The example uses its own ten demonstration rows, separate from the benchmark's fixed reporting partitions.

## Full numerical replay

From the repository root, after installing Git LFS:

```bash
git lfs pull --include="analysis/data/**"
python -m pip install -r requirements-analysis.txt
python scripts/reproduce_results.py --full --output outputs/full_replay
```

The script copies the approximately 186 MB analysis bundle into a new output workspace, rebuilds the frozen analyses there, and checks the complete comparison against the reference. Reference inputs are not modified. Use a new output directory for a subsequent full replay. No LaTeX installation is required. The original table exporters also write standalone LaTeX table fragments as numerical outputs, but there is no manuscript to compile.

Outputs include readable CSV files at the chosen output root, plus generated figures, tables, workbooks, saved weights and checks under `replay/`. The primary aggregate covers all 22 datasets. Some archived diagnostic controls cover only the original 17 PDE tasks; they are retained for reproducibility and are not additional principal ensemble rules.

For those 17 tasks, `analysis/data/review_grams/` contains per-case matrices of normalized error inner products, sufficient to refit and evaluate fixed convex mixtures. The four additional PDE tasks and ERA5 have their own completed campaign records. All three principal rules use fitting examples separate from their evaluation examples. [Metric definitions](RESULTS.md).

## What is supplied

- All 22 dataset archives, plus separately prepared ERA5 training and reserved-query arrays.
- Generator and preparation source, parameter recipes, and available convergence/reference checks. Imported MFRNP and ERA5 archives are supplied as data; the original climate simulators are not included.
- Training, data-adapter, optimization, checkpoint-writing and prediction-export code for the baseline implementations and nine surrogates.
- Saved predictions where archived, per-case errors, fitting/evaluation partitions, weights and error Gram matrices.
- Numerical reproduction and visualization scripts.

The release does not contain every original trained checkpoint or optimizer state. Training scripts produce new checkpoints. Long GPU retraining was not repeated to package the release, and numerical replay does not imply bitwise reproducibility of a new GPU training run.

## Experimental scope

The compared methods use corresponding evaluation cases. Historical implementations differ in training data usage, validation, optimization and compute settings. The generic launcher's defaults are starting values; frozen campaign plans and per-run records define the specific reported recipes. A single final training seed is used per recipe. The repeated fitting partitions are not independent training-seed repeats.

The source data versions are preserved. Poisson I and Cavity use their corrected generated archives, and Poisson II uses the imported archive scored in the benchmark. Known task properties, including synthetic coarse pressure fields and incomplete initial-condition information in Cahn Hilliard I, are recorded in [dataset documentation](DATASETS.md) and the source metadata. Related archives can share physical simulations, and historical results informed development.

B9/B10 share inspected transfer code, and M8/M9 have identical archived Darcy predictions. Historical GP exports may reconstruct a fitted estimator rather than load an original serialized estimator. These records are preserved rather than represented as independent new fits.

## Integrity

To obtain and check all supplied files:

```bash
git lfs pull --include="" --exclude=""
python scripts/verify_release.py
```

The download is about 10.4 GB of unique LFS objects. `release_manifest.json` records file sizes and SHA256 values. The full integrity check requires all LFS assets. Use an unchanged checkout to verify the reference files. New experiment outputs belong under `outputs/`, which is ignored by Git.
