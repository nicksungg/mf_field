# MFFP benchmark — 42 datasets

Multi-fidelity field-prediction benchmark, organized into three collections. Each dataset is a folder with `meta.json`, `README.md`, and aligned/nested `train_l*.npz` / `test_l*.npz` fidelity levels (`l1`=coarsest). Full per-dataset stats in [`MANIFEST.csv`](MANIFEST.csv).

**Totals:** 42 datasets — core 15, ext 8, sharp 19.

> Note: `helmholtz_2d` and `kuramoto_sivashinsky_1d` appear in **both** `ext` and `sharp` (different generators/params) — they are kept separate by collection folder.


## `core/` — 15 datasets

Base MFFP collection — classic multi-fidelity PDE/reanalysis benchmarks.

| # | dataset | dims | fidelities | cond dim | N (HF) | HF grid | LF–HF corr | flags |
|---|---------|------|-----------|----------|--------|---------|-----------|-------|
| 1 | **poisson_generated** | 2 | 3 | 5 | 400 | 64x64 | 0.977 | — |
| 2 | **heat_generated** | 2 | 3 | 3 | 400 | 64x64 | 0.989 | — |
| 3 | **burgers_generated** | 2 | 3 | 8 | 400 | 16x16 | 0.947 | operator-hard, degenerate |
| 4 | **burgers_param_generated** | 2 | 3 | 5 | 400 | 16x16 | 0.927 | operator-hard, degenerate |
| 5 | **advection_diffusion_generated** | 2 | 2 | 2 | 400 | 64x64 | 0.996 | — |
| 6 | **allen_cahn_generated** | 2 | 3 | 2 | 400 | 16x16 | 0.936 | — |
| 7 | **darcy_generated** | 2 | 3 | 16 | 400 | 128x128 | 0.995 | — |
| 8 | **lid_driven_cavity_generated** | 2 | 4 | 1 | 40 | 256x256 | 0.799 | — |
| 9 | **poisson_local** | 2 | 5 | 5 | 64 | 128x128 | 0.975 | — |
| 10 | **heat_local** | 2 | 5 | 3 | 1024 | 128x128 | 0.989 | — |
| 11 | **fluid** | 2 | 2 | 2 | 256 | 64x64 | 0.972 | — |
| 12 | **ifc_heat** | 2 | 4 | 3 | 5 | 64x64 | 0.940 | operator-hard, degenerate |
| 13 | **ifc_poisson** | 2 | 4 | 5 | 5 | 64x64 | 0.827 | — |
| 14 | **era5** | 2 | 9 | 12 | 65 | 721x1440 | 0.995 | — |
| 15 | **pm_test** | 2 | 9 | 12 | 65 | 721x1440 | 0.995 | — |

## `ext/` — 8 datasets

Extension — new high-frequency 2D/1D fields the core set lacked.

| # | dataset | dims | fidelities | cond dim | N (HF) | HF grid | LF–HF corr | flags |
|---|---------|------|-----------|----------|--------|---------|-----------|-------|
| 1 | **helmholtz_2d** | 2 | 2 | 3 | 400 | 96x96 | 0.983 | — |
| 2 | **rayleigh_benard_2d** | 2 | 2 | 1 | 400 | 64x64 | 0.999 | — |
| 3 | **gray_scott_2d** | 2 | 2 | 2 | 400 | 72x72 | 0.008 | MF-useless, degenerate |
| 4 | **wave_2d** | 2 | 2 | 3 | 400 | 80x80 | 0.846 | — |
| 5 | **eikonal_2d** | 2 | 2 | 3 | 400 | 64x64 | 0.990 | — |
| 6 | **cahn_hilliard_2d** | 2 | 2 | 2 | 400 | 64x64 | 0.333 | — |
| 7 | **kuramoto_sivashinsky_1d** | 2 | 2 | 3 | 400 | 256x120 | -0.057 | MF-useless, operator-hard, degenerate |
| 8 | **pressure_poisson_poiseuille** | 2 | 4 | 2 | 400 | 64x64 | 0.927 | — |

## `sharp/` — 19 datasets

Sharp — shock / sharp-interface / smooth-control portfolio (SURF 2026).

| # | dataset | dims | fidelities | cond dim | N (HF) | HF grid | LF–HF corr | flags |
|---|---------|------|-----------|----------|--------|---------|-----------|-------|
| 1 | **euler** | 2 | 3 | 7 | 400 | 128x128 | 0.974 | — |
| 2 | **sod_1d** | 1 | 3 | 3 | 400 | 128 | 0.994 | — |
| 3 | **burgers_1d** | 1 | 3 | 2 | 400 | 128 | 0.939 | — |
| 4 | **burgers_2d** | 2 | 3 | 2 | 400 | 256x256 | 0.977 | — |
| 5 | **shallow_water_1d** | 1 | 3 | 2 | 400 | 128 | 0.723 | — |
| 6 | **shallow_water_2d** | 2 | 3 | 2 | 400 | 128x128 | 0.942 | — |
| 7 | **cahn_hilliard** | 2 | 3 | 19 | 400 | 256x256 | 0.990 | — |
| 8 | **allen_cahn_1d** | 1 | 3 | 3 | 400 | 512 | 1.000 | operator-hard, degenerate |
| 9 | **allen_cahn_2d** | 2 | 3 | 3 | 400 | 256x256 | 0.984 | — |
| 10 | **porous_medium_1d** | 1 | 3 | 2 | 400 | 128 | 0.984 | — |
| 11 | **porous_medium_2d** | 2 | 3 | 2 | 400 | 256x256 | 0.994 | — |
| 12 | **fisher_kpp_1d** | 1 | 3 | 2 | 400 | 512 | 0.997 | operator-hard, degenerate |
| 13 | **fisher_kpp_2d** | 2 | 3 | 2 | 400 | 256x256 | 0.758 | — |
| 14 | **phase_field_crystal_2d** | 2 | 3 | 2 | 400 | 128x128 | 0.930 | — |
| 15 | **kuramoto_sivashinsky_1d** | 1 | 3 | 17 | 400 | 512 | 1.000 | operator-hard, degenerate |
| 16 | **kuramoto_sivashinsky_2d** | 2 | 3 | 17 | 400 | 256x256 | 0.995 | operator-hard, degenerate |
| 17 | **nls_1d** | 1 | 3 | 17 | 400 | 512 | 1.000 | operator-hard, degenerate |
| 18 | **sine_gordon_1d** | 1 | 3 | 17 | 400 | 512 | 1.000 | operator-hard, degenerate |
| 19 | **helmholtz_2d** | 2 | 3 | 2 | 400 | 256x256 | 0.991 | — |
