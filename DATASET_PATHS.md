# Benchmarked dataset pathnames

All 42 datasets, as of the HuggingFace restructure of 2026-07-28 (commit `56c1328149`).
Supersedes the pre-restructure version of this file, which described the deleted
`mf_field_data/` / `mf_field_extension_data/` / `mf_field_eloise_data/` trees.

Layout: `benchmark_42/<collection>/<dataset>/` with `train_l*.npz` / `test_l*.npz`
(`l1` = coarsest), keys `x` (conditions) and `y` (flattened field).

Harness names add a collection prefix — `<name>` for core, `ext__<name>`, `sharp__<name>` —
because `helmholtz_2d` and `kuramoto_sivashinsky_1d` exist in **both** ext and sharp
as different datasets.

Flags come from `benchmark_42/MANIFEST.csv`. `r` is `lf_hf_pearson`.


## `core/` — 15 datasets

| dataset | path | harness name | fid | N_hf | HF grid | r | flags |
|---|---|---|---|---|---|---|---|
| `poisson_generated` | `benchmark_42/core/poisson_generated/` | `poisson_generated` | 3 | 400 | 64x64 | 0.977 | — |
| `heat_generated` | `benchmark_42/core/heat_generated/` | `heat_generated` | 3 | 400 | 64x64 | 0.989 | — |
| `burgers_generated` | `benchmark_42/core/burgers_generated/` | `burgers_generated` | 3 | 400 | 16x16 | 0.947 | operator-hard, degenerate |
| `burgers_param_generated` | `benchmark_42/core/burgers_param_generated/` | `burgers_param_generated` | 3 | 400 | 16x16 | 0.927 | operator-hard, degenerate |
| `advection_diffusion_generated` | `benchmark_42/core/advection_diffusion_generated/` | `advection_diffusion_generated` | 2 | 400 | 64x64 | 0.996 | — |
| `allen_cahn_generated` | `benchmark_42/core/allen_cahn_generated/` | `allen_cahn_generated` | 3 | 400 | 16x16 | 0.936 | — |
| `darcy_generated` | `benchmark_42/core/darcy_generated/` | `darcy_generated` | 3 | 400 | 128x128 | 0.995 | — |
| `lid_driven_cavity_generated` | `benchmark_42/core/lid_driven_cavity_generated/` | `lid_driven_cavity_generated` | 4 | 40 | 256x256 | 0.799 | — |
| `poisson_local` | `benchmark_42/core/poisson_local/` | `poisson_local` | 5 | 64 | 128x128 | 0.975 | has `ood/` |
| `heat_local` | `benchmark_42/core/heat_local/` | `heat_local` | 5 | 1024 | 128x128 | 0.989 | has `ood/` |
| `fluid` | `benchmark_42/core/fluid/` | `fluid` | 2 | 256 | 64x64 | 0.972 | — |
| `ifc_heat` | `benchmark_42/core/ifc_heat/` | `ifc_heat` | 4 | 5 | 64x64 | 0.940 | operator-hard, degenerate |
| `ifc_poisson` | `benchmark_42/core/ifc_poisson/` | `ifc_poisson` | 4 | 5 | 64x64 | 0.827 | — |
| `era5` | `benchmark_42/core/era5/` | `era5` | 9 | 65 | 721x1440 | 0.995 | — |
| `pm_test` | `benchmark_42/core/pm_test/` | `pm_test` | 9 | 65 | 721x1440 | 0.995 | — |

## `ext/` — 8 datasets

| dataset | path | harness name | fid | N_hf | HF grid | r | flags |
|---|---|---|---|---|---|---|---|
| `helmholtz_2d` | `benchmark_42/ext/helmholtz_2d/` | `ext__helmholtz_2d` | 2 | 400 | 96x96 | 0.983 | — |
| `rayleigh_benard_2d` | `benchmark_42/ext/rayleigh_benard_2d/` | `ext__rayleigh_benard_2d` | 2 | 400 | 64x64 | 0.999 | — |
| `gray_scott_2d` | `benchmark_42/ext/gray_scott_2d/` | `ext__gray_scott_2d` | 2 | 400 | 72x72 | 0.008 | **MF-USELESS**, degenerate |
| `wave_2d` | `benchmark_42/ext/wave_2d/` | `ext__wave_2d` | 2 | 400 | 80x80 | 0.846 | — |
| `eikonal_2d` | `benchmark_42/ext/eikonal_2d/` | `ext__eikonal_2d` | 2 | 400 | 64x64 | 0.990 | — |
| `cahn_hilliard_2d` | `benchmark_42/ext/cahn_hilliard_2d/` | `ext__cahn_hilliard_2d` | 2 | 400 | 64x64 | 0.333 | — |
| `kuramoto_sivashinsky_1d` | `benchmark_42/ext/kuramoto_sivashinsky_1d/` | `ext__kuramoto_sivashinsky_1d` | 2 | 400 | 256x120 | -0.057 | **MF-USELESS**, operator-hard, degenerate |
| `pressure_poisson_poiseuille` | `benchmark_42/ext/pressure_poisson_poiseuille/` | `ext__pressure_poisson_poiseuille` | 4 | 400 | 64x64 | 0.927 | — |

## `sharp/` — 19 datasets

| dataset | path | harness name | fid | N_hf | HF grid | r | flags |
|---|---|---|---|---|---|---|---|
| `euler` | `benchmark_42/sharp/euler/` | `sharp__euler` | 3 | 400 | 128x128 | 0.974 | — |
| `sod_1d` | `benchmark_42/sharp/sod_1d/` | `sharp__sod_1d` | 3 | 400 | 128 | 0.994 | — |
| `burgers_1d` | `benchmark_42/sharp/burgers_1d/` | `sharp__burgers_1d` | 3 | 400 | 128 | 0.939 | — |
| `burgers_2d` | `benchmark_42/sharp/burgers_2d/` | `sharp__burgers_2d` | 3 | 400 | 256x256 | 0.977 | — |
| `shallow_water_1d` | `benchmark_42/sharp/shallow_water_1d/` | `sharp__shallow_water_1d` | 3 | 400 | 128 | 0.723 | — |
| `shallow_water_2d` | `benchmark_42/sharp/shallow_water_2d/` | `sharp__shallow_water_2d` | 3 | 400 | 128x128 | 0.942 | — |
| `cahn_hilliard` | `benchmark_42/sharp/cahn_hilliard/` | `sharp__cahn_hilliard` | 3 | 400 | 256x256 | 0.990 | — |
| `allen_cahn_1d` | `benchmark_42/sharp/allen_cahn_1d/` | `sharp__allen_cahn_1d` | 3 | 400 | 512 | 1.000 | operator-hard, degenerate |
| `allen_cahn_2d` | `benchmark_42/sharp/allen_cahn_2d/` | `sharp__allen_cahn_2d` | 3 | 400 | 256x256 | 0.984 | — |
| `porous_medium_1d` | `benchmark_42/sharp/porous_medium_1d/` | `sharp__porous_medium_1d` | 3 | 400 | 128 | 0.984 | — |
| `porous_medium_2d` | `benchmark_42/sharp/porous_medium_2d/` | `sharp__porous_medium_2d` | 3 | 400 | 256x256 | 0.994 | — |
| `fisher_kpp_1d` | `benchmark_42/sharp/fisher_kpp_1d/` | `sharp__fisher_kpp_1d` | 3 | 400 | 512 | 0.997 | operator-hard, degenerate |
| `fisher_kpp_2d` | `benchmark_42/sharp/fisher_kpp_2d/` | `sharp__fisher_kpp_2d` | 3 | 400 | 256x256 | 0.758 | — |
| `phase_field_crystal_2d` | `benchmark_42/sharp/phase_field_crystal_2d/` | `sharp__phase_field_crystal_2d` | 3 | 400 | 128x128 | 0.930 | — |
| `kuramoto_sivashinsky_1d` | `benchmark_42/sharp/kuramoto_sivashinsky_1d/` | `sharp__kuramoto_sivashinsky_1d` | 3 | 400 | 512 | 1.000 | operator-hard, degenerate |
| `kuramoto_sivashinsky_2d` | `benchmark_42/sharp/kuramoto_sivashinsky_2d/` | `sharp__kuramoto_sivashinsky_2d` | 3 | 400 | 256x256 | 0.995 | operator-hard, degenerate |
| `nls_1d` | `benchmark_42/sharp/nls_1d/` | `sharp__nls_1d` | 3 | 400 | 512 | 1.000 | operator-hard, degenerate |
| `sine_gordon_1d` | `benchmark_42/sharp/sine_gordon_1d/` | `sharp__sine_gordon_1d` | 3 | 400 | 512 | 1.000 | operator-hard, degenerate |
| `helmholtz_2d` | `benchmark_42/sharp/helmholtz_2d/` | `sharp__helmholtz_2d` | 3 | 400 | 256x256 | 0.991 | — |

## Filtering

**MF-useless (2)** — LF carries no information about HF; no MF method can win:

- `ext/gray_scott_2d`
- `ext/kuramoto_sivashinsky_1d`

**Degenerate (11)** — excluded from `compute_elo_full.py`'s headline ranking,
but *not* from `score.py`'s `composite_nRMSE`, which is what the factory optimizes:

- `core/burgers_generated`
- `core/burgers_param_generated`
- `core/ifc_heat`
- `ext/gray_scott_2d`
- `ext/kuramoto_sivashinsky_1d`
- `sharp/allen_cahn_1d`
- `sharp/fisher_kpp_1d`
- `sharp/kuramoto_sivashinsky_1d`
- `sharp/kuramoto_sivashinsky_2d`
- `sharp/nls_1d`
- `sharp/sine_gordon_1d`

**Learnable (31 of 42)** — the set to judge model deltas on:

```
core/poisson_generated
core/heat_generated
core/advection_diffusion_generated
core/allen_cahn_generated
core/darcy_generated
core/lid_driven_cavity_generated
core/poisson_local
core/heat_local
core/fluid
core/ifc_poisson
core/era5
core/pm_test
ext/helmholtz_2d
ext/rayleigh_benard_2d
ext/wave_2d
ext/eikonal_2d
ext/cahn_hilliard_2d
ext/pressure_poisson_poiseuille
sharp/euler
sharp/sod_1d
sharp/burgers_1d
sharp/burgers_2d
sharp/shallow_water_1d
sharp/shallow_water_2d
sharp/cahn_hilliard
sharp/allen_cahn_2d
sharp/porous_medium_1d
sharp/porous_medium_2d
sharp/fisher_kpp_2d
sharp/phase_field_crystal_2d
sharp/helmholtz_2d
```

## Not in the benchmark

`cfd_geneva/` holds the Geneva & Zabaras backward-step and cylinder-array CFD data.
It is absent from the 42-dataset roster and from HuggingFace entirely after the restructure —
that directory is the only known copy. See `cfd_geneva/README.md`.
