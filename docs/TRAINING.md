# Retraining

Use Python 3.12 for the archived PyTorch 2.5.1 recipes. Install an appropriate CUDA-enabled PyTorch build for the machine, then `pip install -r requirements-training.txt`. Exact recorded environments and hyperparameters are retained in the model environment file and per-run metadata. CPU imports were checked in the release validation environment; long GPU training was not repeated to create this artifact.

## Original PDE model implementations

```bash
python scripts/train.py --model M1 --dataset heat_generated --epochs 2500
python scripts/train.py --model B8 --dataset heat_generated --epochs 6000
python scripts/train.py --model B13 --dataset heat_generated --device cpu
```

`--dry-run` prints the command. New outputs are written under `outputs/training/`. The actual paper recipes include different epoch/step counts. Inspect the matching archived result JSON and model source before selecting a budget. This launcher runs locally; it does not submit cluster jobs or overwrite archived results. Paper-family scripts historically named `smoke_eval.py` are their actual training/evaluation entry points.

## Historical M8 and M9 correctors

A five-fold coarse ensemble supplies out-of-fold predictions for training the corrector. Each fold has two plain and two heteroscedastic members. The test ensemble uses four members from one fold, matching the training ensemble size.

```bash
for fold in 0 1 2 3 4; do
  for variant in plain hetero; do
    for seed in 42 123; do
      python scripts/train_corrector.py coarse --dataset heat_generated \
        --fold "$fold" --variant "$variant" --seed "$seed" \
        --work outputs/heat_correctors
    done
  done
done
python scripts/train_corrector.py assemble --dataset heat_generated --work outputs/heat_correctors
python scripts/train_corrector.py corrector --dataset heat_generated --model M8 --work outputs/heat_correctors
python scripts/train_corrector.py corrector --dataset heat_generated --model M9 --work outputs/heat_correctors
```

The defaults are 30,000 coarse optimizer steps and 6,000 corrector steps. Inspect the saved per-run JSON for early stopping and other actual settings. ERA5 is unpaired and uses the separate procedure below.

## Four added PDE datasets

Allen Cahn, Cahn Hilliard II, Fisher KPP and Phase field crystal have complete saved predictions in `campaigns/four_baselines/`. Earlier fits reused by that campaign are preserved under `four_library/`; the final generalized training adapter is `four_final_library/`. Use the frozen adapter to stage a new fit:

```bash
python scripts/prepare_campaign.py four_final_library --output outputs/four_final_library
python outputs/four_final_library/expert_worker.py --dataset sharp__allen_cahn_2d --kind direct --model mf_fno_transfer_film
python outputs/four_final_library/expert_worker.py --help
```

The adapter exposes direct, coarse, assemble and corrector stages, and denies training access to the reserved answer store. For a complete M8/M9 retraining, run coarse indices 0 through 19, assemble, then each corrector. Its `PLAN.json` is restricted to these four paper tasks; it does not select regenerated versions of other datasets. Exact roles and result provenance are retained in `campaigns/four_baselines/`.

For added baseline fits, prepare `four_baselines` similarly and consult `baseline_worker.py --help`. Historical baseline reuse records and errors are included rather than represented as independent new fits. Training/query array hashes in the frozen plans remain authoritative.

## ERA5

For direct library members M1–M7, the `four_library` source also contains the original ERA5 reserved-input adapter. After preparing that workspace, invoke `run_base.py --dataset era5 --model <identifier>`.

For the ERA5 correctors:

```bash
python scripts/prepare_campaign.py era5_library --output outputs/era5_library
python outputs/era5_library/run_corrector.py --backbone transolver
python outputs/era5_library/run_corrector.py --backbone convnext
```

The workspace starts with the archived OOF coarse inputs so a corrector can be retrained independently. To regenerate those inputs, remove the copied `outputs/era5_library/coarse/` directory, run `run_coarse.py --task 0` through `--task 19`, then `run_coarse.py --assemble`. Never remove `campaigns/era5_library/coarse/`, which is the reference artifact.

For ERA5 baselines:

```bash
python scripts/prepare_campaign.py era5_baselines --output outputs/era5_baselines
python outputs/era5_baselines/worker_st.py --help
python outputs/era5_baselines/worker_paper.py --help
```

Preparation links the released arrays and checks the input-file hashes. It issues a new source manifest for the relocated code. It does not certify a new scientific result. Record the new source manifest and environment alongside any newly trained outputs. The ERA5 baseline and library sources use their respective unpaired adapters, not the generic paired-PDE corrector loader.
