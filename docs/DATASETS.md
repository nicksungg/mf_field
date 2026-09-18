# Dataset sources and generators

The 22 entries in `configs/datasets.json` define the paper roster. The accompanying `verification/datasets.json` lists every fidelity's array shapes and input counts. Each NPZ contains parameter rows `x` and flattened fields `y`; grid geometry is specified by the model data adapters and the metadata. These are parameter-to-field tasks. Not all two-dimensional arrays are two-dimensional spatial domains: the heat example is a space-time field.

| Paper datasets | Source and generation code |
|---|---|
| Darcy and Heat I | In-house solvers in `generators/core/generate_all_datasets.py`, with the copied solver routines in `generators/datafix/gen_core_v2.py` |
| Poisson I | Corrected boundary scaling in `generators/datafix/gen_core_v2.py` |
| Cavity | Steady-state vorticity-streamfunction solver in `generators/cavity/lid_driven_cavity.py`, sharding in `generators/datafix/gen_cav.py` and merging in `merge_cav.py` |
| Eikonal, Rayleigh Bénard, Wave, Cahn Hilliard I | `generators/ext/solvers.py` and `generate_ext_standardized.py` |
| Pressure Poisson | `generators/ext/generate_pressure_poisson_std.py`; analytic fine pressure with synthetic block-averaged, perturbed coarse fields |
| Euler, Burgers, Shallow water, Porous medium, Allen Cahn, Cahn Hilliard II, Fisher KPP, Phase field crystal | `generators/sharp/generate_standardized.py`, per-variant ablation JSONs, and `generators/sharp/SURF_2026-main/mffp_sharp/` solver modules and `configs/sample.yaml` |
| Helmholtz | Sharp-field source with `generators/sharp/generate_helmholtz_fixed.py`, wavenumbers in [15,25] and unit-normalized fields |
| Poisson II, Heat II, Navier Stokes | Imported MFRNP archives (Niu et al., ICML 2024). The exact arrays are included; a new in-house simulator is not substituted for these tasks. |
| ERA5 | The MFRNP-distributed climate archive, citing Niu et al. (2024) and Hersbach et al. (2020). Original and prepared arrays plus preparation and role records are included. |

The available solver verification and convergence scripts accompany the source. Their scope varies. Links to an established numerical method or benchmark do not certify every parameter draw in this dataset. The manuscript appendix gives the relevant distinctions and citations.

## Array locations and input roles

- `datasets/{core,ext,sharp}/`: exact native archive training and query arrays for the PDE tasks; prepared ERA5 arrays under `datasets/core/era5/`.
- `datasets/source/era5/`: the original imported ERA5 archive, retained to explain and reproduce the reserved-input exclusion step. It is **not** the ERA5 training input for the reported clean evaluation.
- `datasets/answers/era5/`: actual fitting and evaluation targets on the working grid. The `test_l*.npz` files in prepared ERA5 training directories contain **zero target placeholders**. Do not use those zeros as evaluation answers.
- `campaigns/four_library/data/sharp/`: prepared versions for the four added PDEs, with reserved query answers withheld from training workers. The corresponding targets and role assignments are in that campaign's `answers/` and `ROLES.json`.
- `campaigns/era5_library/data/training.npz`: the unpaired LF/HF training arrays and query parameters for the coarse-surrogate/corrector recipe.
- `paper/data/historical_runs/` and later campaign `ROLES.json`: fixed fitting/evaluation case partitions. The raw archive's query pool is not identical to each reported evaluation subset.

ERA5 has 55 fine training examples, a pool of 10 fitting examples and seven evaluation examples. Reserved parameter identities were removed from every fidelity's training pool. The working output grid is 128 by 256; the native fine archive grid is 721 by 1440. Native grids, display interpolation and model working grids are distinct.

## Running generators

For a small inspection at an existing parameter vector, without changing any reference data:

```bash
python scripts/generate_fields.py --dataset poisson_generated_v2 --level 1 --rows 1 --output outputs/poisson_check.npz
python scripts/generate_fields.py --dataset heat_generated --level 1 --rows 1 --output outputs/heat_check.npz
python scripts/generate_fields.py --dataset ext__wave_2d --level 1 --rows 1 --output outputs/wave_check.npz
```

The command prints the difference from the stored field. These small checks do not validate every solver or establish a full-dataset regeneration.

Full sampling/sharding drivers and their original configurations are preserved under `generators/`. Set output directories explicitly before using them; historical filesystem prefixes are normalized as `/archive/...` and are provenance placeholders, not dependencies on the authors' machines. Sharp hyperbolic solvers require Clawpack/PyClaw and a Fortran compiler. Set `PYTHONPATH` to the bundled `mffp_sharp/src` directory before using its drivers. Imported MFRNP and ERA5 arrays can be reproduced at the preparation level from the bundled sources; the original upstream simulation infrastructure is not supplied by this artifact.
