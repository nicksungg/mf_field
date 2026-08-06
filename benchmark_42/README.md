# MFFP benchmark — 42 datasets

Multi-fidelity field-prediction benchmark, organized into three collections. Each dataset is a folder with `meta.json`, `README.md`, and aligned/nested `train_l*.npz` / `test_l*.npz` fidelity levels (`l1`=coarsest). Full per-dataset stats in [`MANIFEST.csv`](MANIFEST.csv).

**Totals:** 42 datasets — core 15, ext 8, sharp 19.

> Note: `helmholtz_2d` and `kuramoto_sivashinsky_1d` appear in **both** `ext` and `sharp` (different generators/params) — they are kept separate by collection folder.

## Revision history

**2026-08-05 — corrected release.** Three defect classes were fixed since the 2026-07-28 release. Seven datasets changed; the other 35 are byte-identical.

1. **Grid-registration ("half-pixel") defect** — the generator built each pre-aligned copy (`/fields_hf/res_R`) with a single cell-centred coordinate map, but the pseudo-spectral and periodic-FD solvers sample at nodes, and helmholtz on interior Dirichlet nodes. Every output pixel was read from a coordinate displaced by `(r-1)/2` HF cells — half a coarse cell — with clamp-extension across periodic seams instead of wrapping. The raw native-grid arrays were always correct; the shift lived in the aligned copies and in the fidelity-gap metrics the datasets reported about themselves (allen_cahn's LF→HF rel-L2 gap was inflated 3.2–4.7x). The generator now dispatches per PDE across three conventions (`node_periodic`, `node_dirichlet`, `cell_centered`), records the one it used as an `alignment_convention` attribute, and raises on an unclassified PDE rather than defaulting.

2. **Condition-vector incompleteness** — five sharp datasets drew per-sample initial-condition coefficients and consumed them in the solver without exporting them, so the condition vector did not determine the field. They were regenerated with the ICs encoded, which is why their `cond dim` grows sharply (e.g. `fisher_kpp_2d` 2 → 50). `core/burgers_param_generated` had the same defect in its IC phases; those were re-derived through the generation RNG chain and appended without re-solving (reconstruction certificate: rel-L2 = 0.0 over all 500 rows).

3. **Disjoint fidelity levels in `ifc_heat` / `ifc_poisson`** — parameter vectors were drawn independently per fidelity, so no sample existed at more than one fidelity and `HF - LF` residuals were undefined. Both were regenerated with nested parameter sets (verified: L2 ⊂ L1, L3 ⊂ L2, L4 ⊂ L3, train disjoint from test). Their stale `scalers/` and `cat.pkl`, fitted on the old sample set, were removed rather than re-shipped.

`MANIFEST.csv` and the tables below were recomputed from the corrected data with the original characterizer. The `lf_hf_pearson` and degeneracy flags shifted for the seven affected datasets — most visibly `ifc_poisson` 0.827 → 0.909 and `fisher_kpp_2d` 0.758 → 0.984, both of which had been depressed by the defects rather than by anything physical.

## Degeneracy flags — read this before choosing datasets

**14 of the 42 datasets are degenerate in at least one of three ways.** A degenerate dataset is not broken; it is unsuitable for measuring what this benchmark claims to measure, and a model can post an excellent score on it without doing anything interesting. They are kept in the release because excluding them silently is worse than labelling them.

| flag | criterion | what it means |
|---|---|---|
| `mf_useless` | `lf_hf_pearson < 0.3` | The low-fidelity field carries essentially no information about the high-fidelity one. Multi-fidelity is pointless here by construction — there is nothing to transfer. |
| `operator_hard` | `pf_dist_corr < 0.15` | The condition vector barely predicts the field. Nothing conditions the prediction, so a model cannot do better than learning the field distribution. |
| `copy_lf_trivial` | `copy_lf_rel_l2 < 0.01` | Lifting LF onto the HF grid *already* reproduces HF to within 1% relative L2. Copying the coarse field solves the task; there is no fidelity gap to learn. |

`copy_lf_rel_l2` is measured at **full resolution** under the best of the audited registration conventions — the best case for the copy hypothesis, so a flagged dataset is trivial under any registration. Do not confuse it with the characterizer's internal `lf_hf_rel_resid`, which compares nearest-index-resampled fields on a grid capped at 128 and misstates copy error in both directions (`allen_cahn_2d`: 0.0445 there, 0.0069 here).

### The flagged datasets

| dataset | modes | key number |
|---|---|---|
| `sharp/fisher_kpp_2d` | copy-LF-trivial | copy rel-L2 **0.0006** |
| `sharp/fisher_kpp_1d` | copy-LF-trivial | copy rel-L2 0.0023 |
| `sharp/allen_cahn_1d` | operator-hard, copy-LF-trivial | copy rel-L2 0.0027 |
| `sharp/kuramoto_sivashinsky_2d` | operator-hard, copy-LF-trivial | copy rel-L2 0.0047 |
| `core/advection_diffusion_generated` | copy-LF-trivial | copy rel-L2 0.0057 |
| `sharp/sine_gordon_1d` | operator-hard, copy-LF-trivial | copy rel-L2 0.0063 |
| `sharp/allen_cahn_2d` | operator-hard, copy-LF-trivial | copy rel-L2 0.0069 |
| `sharp/kuramoto_sivashinsky_1d` | operator-hard, copy-LF-trivial | copy rel-L2 0.0077 |
| `ext/gray_scott_2d` | MF-useless | LF–HF corr **0.008** |
| `ext/kuramoto_sivashinsky_1d` | MF-useless, operator-hard | LF–HF corr **−0.057** |
| `sharp/nls_1d` | operator-hard | copy rel-L2 0.0124 (borderline) |
| `sharp/phase_field_crystal_2d` | operator-hard | pf corr ≈ 0 on the IC-encoded vector |
| `core/burgers_generated` | operator-hard | 16×16 HF grid |
| `core/burgers_param_generated` | operator-hard | 16×16 HF grid |

Three more sit just above the copy-LF threshold and deserve the same caution: `ext/pressure_poisson_poiseuille` (0.0117), `sharp/nls_1d` (0.0124), `ext/rayleigh_benard_2d` (0.0147).

### Two caveats on `operator_hard`

**It is diluted by IC-encoded condition vectors.** The five sharp datasets regenerated in this release now carry initial-condition coefficients in the condition vector, and distance correlation over a mostly-IC vector tends toward zero even when the field genuinely depends on it. `phase_field_crystal_2d` scores 0.247 on its two physical parameters alone but ≈0 on all 18 columns. Read the flag as "distance correlation is the wrong instrument here", not "the map is unlearnable".

**The thresholds are hand-tuned**, described in the characterizer itself as "tunable; validated against KS/cahn". They are a triage aid, not a verdict. The flag is stable, though: over 6 independent subsamples `allen_cahn_2d` and `phase_field_crystal_2d` fire 6/6, while `fisher_kpp_2d` and `cahn_hilliard` fire 0/6.


## `core/` — 15 datasets

Base MFFP collection — classic multi-fidelity PDE/reanalysis benchmarks.

| # | dataset | dims | fidelities | cond dim | N (HF) | HF grid | LF–HF corr | copy-LF rel-L2 | flags |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **poisson_generated** | 2 | 3 | 5 | 400 | 64x64 | 0.977 | 16.4524 | — |
| 2 | **heat_generated** | 2 | 3 | 3 | 400 | 64x64 | 0.989 | 0.0305 | — |
| 3 | **burgers_generated** | 2 | 3 | 8 | 400 | 16x16 | 0.947 | 0.2384 | operator-hard |
| 4 | **burgers_param_generated** | 2 | 3 | 9 | 400 | 16x16 | 0.927 | 0.2767 | operator-hard |
| 5 | **advection_diffusion_generated** | 2 | 2 | 2 | 400 | 64x64 | 0.996 | 0.0057 | copy-LF-trivial |
| 6 | **allen_cahn_generated** | 2 | 3 | 2 | 400 | 16x16 | 0.936 | 0.2611 | — |
| 7 | **darcy_generated** | 2 | 3 | 16 | 400 | 128x128 | 0.995 | 0.0423 | — |
| 8 | **lid_driven_cavity_generated** | 2 | 4 | 1 | 40 | 256x256 | 0.799 | 0.7029 | — |
| 9 | **poisson_local** | 2 | 5 | 5 | 64 | 128x128 | 0.975 | 66.8286 | — |
| 10 | **heat_local** | 2 | 5 | 3 | 1024 | 128x128 | 0.989 | 0.0340 | — |
| 11 | **fluid** | 2 | 2 | 2 | 256 | 64x64 | 0.972 | 0.2051 | — |
| 12 | **ifc_heat** | 2 | 4 | 3 | 5 | 64x64 | 0.956 | 0.0715 | — |
| 13 | **ifc_poisson** | 2 | 4 | 5 | 5 | 64x64 | 0.909 | 78.2798 | — |
| 14 | **era5** | 2 | 9 | 12 | 65 | 721x1440 | 0.995 | 0.1019 | — |
| 15 | **pm_test** | 2 | 9 | 12 | 65 | 721x1440 | 0.995 | 0.1019 | — |

## `ext/` — 8 datasets

Extension — new high-frequency 2D/1D fields the core set lacked.

| # | dataset | dims | fidelities | cond dim | N (HF) | HF grid | LF–HF corr | copy-LF rel-L2 | flags |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **helmholtz_2d** | 2 | 2 | 3 | 400 | 96x96 | 0.983 | 0.1097 | — |
| 2 | **rayleigh_benard_2d** | 2 | 2 | 1 | 400 | 64x64 | 0.999 | 0.0147 | — |
| 3 | **gray_scott_2d** | 2 | 2 | 2 | 400 | 72x72 | 0.008 | 183583542648.4986 | MF-useless |
| 4 | **wave_2d** | 2 | 2 | 3 | 400 | 80x80 | 0.846 | 0.5245 | — |
| 5 | **eikonal_2d** | 2 | 2 | 3 | 400 | 64x64 | 0.990 | 0.0708 | — |
| 6 | **cahn_hilliard_2d** | 2 | 2 | 2 | 400 | 64x64 | 0.333 | 0.8011 | — |
| 7 | **kuramoto_sivashinsky_1d** | 2 | 2 | 3 | 400 | 256x120 | -0.057 | 1.2563 | MF-useless, operator-hard |
| 8 | **pressure_poisson_poiseuille** | 2 | 4 | 2 | 400 | 64x64 | 0.927 | 0.0117 | — |

## `sharp/` — 19 datasets

Sharp — shock / sharp-interface / smooth-control portfolio (SURF 2026).

| # | dataset | dims | fidelities | cond dim | N (HF) | HF grid | LF–HF corr | copy-LF rel-L2 | flags |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **euler** | 2 | 3 | 7 | 400 | 128x128 | 0.974 | 0.0574 | — |
| 2 | **sod_1d** | 1 | 3 | 3 | 400 | 128 | 0.994 | 0.0508 | — |
| 3 | **burgers_1d** | 1 | 3 | 2 | 400 | 128 | 0.939 | 0.2528 | — |
| 4 | **burgers_2d** | 2 | 3 | 2 | 400 | 256x256 | 0.977 | 0.1935 | — |
| 5 | **shallow_water_1d** | 1 | 3 | 2 | 400 | 128 | 0.723 | 0.0340 | — |
| 6 | **shallow_water_2d** | 2 | 3 | 2 | 400 | 128x128 | 0.942 | 0.0504 | — |
| 7 | **cahn_hilliard** | 2 | 3 | 19 | 400 | 256x256 | 0.990 | 0.0357 | — |
| 8 | **allen_cahn_1d** | 1 | 3 | 19 | 400 | 512 | 1.000 | 0.0027 | operator-hard, copy-LF-trivial |
| 9 | **allen_cahn_2d** | 2 | 3 | 19 | 400 | 256x256 | 0.993 | 0.0069 | operator-hard, copy-LF-trivial |
| 10 | **porous_medium_1d** | 1 | 3 | 2 | 400 | 128 | 0.984 | 0.0425 | — |
| 11 | **porous_medium_2d** | 2 | 3 | 2 | 400 | 256x256 | 0.994 | 0.0372 | — |
| 12 | **fisher_kpp_1d** | 1 | 3 | 18 | 400 | 512 | 1.000 | 0.0023 | copy-LF-trivial |
| 13 | **fisher_kpp_2d** | 2 | 3 | 50 | 400 | 256x256 | 0.984 | 0.0006 | copy-LF-trivial |
| 14 | **phase_field_crystal_2d** | 2 | 3 | 18 | 400 | 128x128 | 0.928 | 0.0287 | operator-hard |
| 15 | **kuramoto_sivashinsky_1d** | 1 | 3 | 17 | 400 | 512 | 1.000 | 0.0077 | operator-hard, copy-LF-trivial |
| 16 | **kuramoto_sivashinsky_2d** | 2 | 3 | 17 | 400 | 256x256 | 0.995 | 0.0047 | operator-hard, copy-LF-trivial |
| 17 | **nls_1d** | 1 | 3 | 17 | 400 | 512 | 1.000 | 0.0124 | operator-hard |
| 18 | **sine_gordon_1d** | 1 | 3 | 17 | 400 | 512 | 1.000 | 0.0063 | operator-hard, copy-LF-trivial |
| 19 | **helmholtz_2d** | 2 | 3 | 2 | 400 | 256x256 | 0.991 | 2.9333 | — |
