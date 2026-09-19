# Baselines and surrogate library

Use the model IDs in [the main README](../README.md#what-is-being-compared) or [configs/models.json](../configs/models.json). The grouping describes each model's role in the comparison, while shared implementations remain together in the source tree.

| Group | IDs | Source | Entry point |
|---|---|---|---|
| Surrogate library | M1–M6 | [operator/transfer families](paper/) | `python scripts/train.py --model M1 ...` |
| Surrogate library | M7 | [POD GP](st_bench/) | `python scripts/train.py --model M7 ...` |
| Surrogate library | M8–M9 | [coarse prediction and correction](uqcorr/) | `python scripts/train_corrector.py ...` |
| Baselines | B1–B5, B11 | [classical and neural baselines](st_bench/) | `python scripts/train.py --model B1 ...` |
| Baselines | B6–B10 | [operator/transfer families](paper/) | `python scripts/train.py --model B8 ...` |
| Additional controls | B12–B13 | [kNN and training mean](st_bench/) | `python scripts/train.py --model B13 ...` |

Commands run from the repository root. The legacy directory name `models/paper/` means literature-based model code; it contains no manuscript. M1–M9 form the mixture. Baselines are evaluated individually and do not enter that mixture.

Read [adaptations and sources](../docs/MODELS.md) and [training instructions](../docs/TRAINING.md). ERA5 and the four later PDE tasks have exact campaign adapters under [campaigns/](../campaigns/). Common utilities remain under `common/` and `data_adapters/`.
