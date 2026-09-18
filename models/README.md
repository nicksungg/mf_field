# Model source

The current manuscript uses nine library members and thirteen baseline entries, including two controls. The complete mapping and adaptation rationale are in `../docs/MODELS.md` and `../configs/models.json`.

`paper/` contains the operator and transfer model families. `st_bench/` contains classical POD/GP and pointwise neural baselines and their shared loaders. `uqcorr/` contains coarse ensemble fitting and the M8/M9 iterative correctors. `common/` and `data_adapters/` provide shared dependencies.

Use `../scripts/train.py` and the campaign-specific instructions in `../docs/TRAINING.md` to retrain. Subdirectory READMEs and comments retain historical experiment context; the release roster, manuscript and frozen per-run records determine which results are reported. A citation to a backbone is not a claim that its multifidelity adaptation is the original paper implementation.
