# Dataset audit 2026-09-06 — generation correctness, inputs, pairing

Scope: the 30-dataset roster (`mf_field_final/datasets_final.txt`). Method: read every generator, re-solve samples,
compare per-level statistics, hash test files against the leaderboard copies.

## Generation principle (all solver-backed datasets)
One theta set is drawn (seed 42, 500 rows -> 400 train / 100 test) and solved independently on every grid of the ladder.
Coarse levels are real coarse solves, not downsampled fine fields — except `ext/pressure_poisson_poiseuille` (see below).
Rows are index-paired across levels by construction ("aligned MF"); `ifc_*` were repaired to nested subsets on 2026-08-03.

## Findings
1. **Poisson dx^2 bug** (`poisson_generated`, and inherited `poisson_local`, `ifc_poisson`): boundary data multiplied by dx^2,
   so each level's field is dx(n)^2 times the true solution. Re-solve check: shipped 64x64 sample 0 == buggy RHS to 3e-15;
   correct solution max 1.46 vs shipped 0.00037. RMS ratios per rung 4.31, 4.16 (= (31/15)^2, (63/31)^2); poisson_local 4.22,
   4.12, 2.27, 1.79. MANIFEST `copy_lf_rel_l2` = 16.5 / 66.8 / 78.3 recorded the symptom. The IFC/MFRNP/D-MFDAL Poisson
   benchmark used in several papers therefore partly measures a 1/n^2 scale factor. Fixed copy: `mf_field_v2/core/poisson_generated_v2`.
2. **Lid-driven cavity**: original generator `MAX_STEPS=8000` leaves 128^2 (needs ~28k steps) and 256^2 (~100k) unconverged.
   The 400/100 v1 set is therefore not ground truth; the 40/10 v2 set (tol 1e-5, cap 200k) is. A 500-sample converged
   regeneration (samples 0-49 identical to v2) is being produced under `mf_field_v2`.
3. **pressure_poisson_poiseuille**: coarse levels = block-mean(HF) + U(0, 0.05*range) noise. Synthetic LF; excluded from the
   correction track.
4. **helmholtz_2d (ext)**: k in [4, 12] straddles cavity resonances; coarse and fine solutions decorrelate (copy-LF rel-L2 1.0).
   Correctly generated, but the coarse level is uninformative. `sharp/helmholtz_2d` normalises every field to unit norm
   for the same reason (amplitude removed from the task).
5. **Labelling**: `allen_cahn_generated` is 1-D (README said 2-D 16x16); `heat_*` fields are space-time (t, x).
6. **No LF abundance**: every solver-backed dataset has N_LF = N_HF = 400. The multi-fidelity premise (cheap coarse data in
   abundance) is not exercised; LF only provides a warm start. `_lfabund` variants (4000 coarse rows, first 400 = the paired
   HF rows) were generated for the core and ext datasets; sharp variants need the SURF/PyClaw environment and are pending.
7. **No cost accounting**: solver wall-time per level was never recorded; `mf_field_v2/*/meta.json` now carries
   `cost_per_solve` (median seconds per sample per level) for the regenerated sets.
8. **ext/cahn_hilliard_2d is not reconstructible from theta**: the current solver reproduces row 0 (rel 0.09) but not rows 1-2
   (1.59, 1.06); the shipped ICs were seeded by batch position. Condition vector incomplete for the surrogate track;
   correction track unaffected. No `_lfabund` variant.
9. **darcy regeneration is not bit-reproducible** (KL eigenvector signs depend on the LAPACK build): the v2 tree keeps the
   original paired arrays and appends 3600 new coarse rows drawn from the same distribution.
10. **Test-file identity**: 24 of 27 paired datasets have byte-identical test files between `mf_field_final` and the leaderboard
   copies; `sharp/fisher_kpp_2d`, `sharp/allen_cahn_2d`, `sharp/phase_field_crystal_2d` differ (regenerated 2026-08-06),
   so surrogate-track numbers on those three must come from reruns on the final copies.

## Inputs (theta) per dataset
| dataset | theta | levels |
|---|---|---|
| poisson_generated / poisson_local / ifc_poisson | 4 Dirichlet boundary values + centre source value, U(0.1, 0.9) | 16..64 / 16..128 / 8..64 |
| heat_generated / heat_local / ifc_heat | left flux U(0,1), right flux U(-1,0), diffusivity U(0.01,0.1); field (t, x) | 16..64 / 16..128 / 8..64 |
| darcy_generated | 16 KL coefficients of log-permeability | 32..128 |
| allen_cahn_generated | interface centre U(-0.7,0.7), sign; 1-D final state | 64..256 pts |
| lid_driven_cavity_generated | Re log-uniform [100, 1000] | 32..256 |
| fluid | 2 params (MFRNP release; generator not available to us) | 32, 64 |
| ext helmholtz / wave / eikonal | wavenumber or speed + source position | 24 -> 96 / 80 / 64 |
| ext rayleigh_benard | log10 Ra in [3, 4.3] | 24 -> 64 |
| ext cahn_hilliard_2d | log10 gamma, mean composition (single fixed IC) | 24 -> 64 |
| ext pressure_poisson | radius, v_max (synthetic LF) | 8..64 |
| sharp euler | 6 pressure/density ratios + gamma | 32..128 |
| sharp sod | rho_left, p_left, gamma | 32..128 |
| sharp burgers / shallow_water / porous_medium | IC amplitude + frequency / inner height + dam radius / m + amplitude | 32..128 or 64..256 |
| sharp cahn_hilliard / allen_cahn_2d / phase_field_crystal / fisher | 2-3 physics params + 16-48 Fourier IC coefficients | 64..256 / 32..128 |
| era5 | reanalysis; nine unrelated grids, not a ladder | excluded |

## Pairing
Same theta across fidelities is intended (aligned/nested design) and required for the correction track. It is *not* the
same as LF abundance: see finding 6.
