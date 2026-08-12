# MFFP benchmark — 42 datasets

Multi-fidelity field-prediction benchmark, organized into three collections.
Each dataset is a folder with `meta.json`, `README.md`, and aligned/nested `train_l*.npz` / `test_l*.npz` fidelity levels (`l1`=coarsest).
Full per-dataset stats in [`MANIFEST.csv`](MANIFEST.csv).

**Totals:** 42 datasets — core 15, ext 8, sharp 19.

> Note: `helmholtz_2d` and `kuramoto_sivashinsky_1d` appear in **both** `ext` and `sharp` (different generators/params) — they are kept separate by collection folder.

## Revision history

**2026-08-07 — two datasets revised (hub commit `36a5f198`).**
Both changes come from MFFP round-3 work that postdates the 2026-08-05 upload.
Scores computed against the 2026-08-05 revision are **not comparable** on these two datasets; the previous revision remains reachable through this repository's git history.

1. **`sharp/phase_field_crystal_2d` — regenerated on a crystalline box** (ADR r3-0002).
   The shipped parameter box admitted non-crystalline samples whose fidelity ladder had no gap at all (median bottom-rung gap $1.2 \times 10^{-6}$).
   The release now samples $r \in [-0.4, -0.3]$ and $\bar{\psi} \in [-0.25, -0.2]$, which is all-crystalline ($\sigma = -(r + 3\bar{\psi}^2) \ge 0.11$), restoring a real bottom-rung gap of $9.8 \times 10^{-3}$.
   All six arrays plus the dataset card changed.
   Its top-rung convergence was documented at the same time — see the `top-rung-converged` caveat below, and score this dataset at L1→L3.

2. **`sharp/allen_cahn_2d` — 22 task-void test rows trimmed**, $n = 100 \to 78$ (ADR r3-0003 D1).
   The removed rows carried no fidelity gap and so contributed no prediction task to the test split.
   **Test splits only** — the train arrays are unchanged, which is why the `N (HF)` column in the tables below (a train count) still reads 400 and no derived statistic in `MANIFEST.csv` moves.

`MANIFEST.csv` was recomputed for the affected rows with the original characterizer.

**2026-08-05 — corrected release.**
Three defect classes were fixed since the 2026-07-28 release.
Seven datasets changed; the other 35 are byte-identical.

1. **Grid-registration ("half-pixel") defect** — the generator built each pre-aligned copy (`/fields_hf/res_R`) with a single cell-centred coordinate map, but the pseudo-spectral and periodic-FD solvers sample at nodes, and helmholtz on interior Dirichlet nodes.
   Every output pixel was read from a coordinate displaced by `(r-1)/2` HF cells — half a coarse cell — with clamp-extension across periodic seams instead of wrapping.
   The raw native-grid arrays were always correct; the shift lived in the aligned copies and in the fidelity-gap metrics the datasets reported about themselves (allen_cahn's LF→HF rel-L2 gap was inflated 3.2–4.7x).
   The generator now dispatches per PDE across three conventions (`node_periodic`, `node_dirichlet`, `cell_centered`), records the one it used as an `alignment_convention` attribute, and raises on an unclassified PDE rather than defaulting.

2. **Condition-vector incompleteness** — five sharp datasets drew per-sample initial-condition coefficients and consumed them in the solver without exporting them, so the condition vector did not determine the field.
   They were regenerated with the ICs encoded, which is why their `cond dim` grows sharply (e.g. `fisher_kpp_2d` 2 → 50).
   `core/burgers_param_generated` had the same defect in its IC phases; those were re-derived through the generation RNG chain and appended without re-solving (reconstruction certificate: rel-L2 = 0.0 over all 500 rows).

3. **Disjoint fidelity levels in `ifc_heat` / `ifc_poisson`** — parameter vectors were drawn independently per fidelity, so no sample existed at more than one fidelity and `HF - LF` residuals were undefined.
   Both were regenerated with nested parameter sets (verified: L2 ⊂ L1, L3 ⊂ L2, L4 ⊂ L3, train disjoint from test).
   Their stale `scalers/` and `cat.pkl`, fitted on the old sample set, were removed rather than re-shipped.

`MANIFEST.csv` and the tables below were recomputed from the corrected data with the original characterizer.
The `lf_hf_pearson` and degeneracy flags shifted for the seven affected datasets — most visibly `ifc_poisson` 0.827 → 0.909 and `fisher_kpp_2d` 0.758 → 0.984, both of which had been depressed by the defects rather than by anything physical.

## Degeneracy flags — read this before choosing datasets

**14 of the 42 datasets are degenerate in at least one of four ways.**
A degenerate dataset is not broken; it is unsuitable for measuring what this benchmark claims to measure, and a model can post an excellent score on it without doing anything interesting.
They are kept in the release because excluding them silently is worse than labelling them.

| flag | criterion | what it means |
|---|---|---|
| `mf_useless` | `lf_hf_pearson < 0.3` | The low-fidelity field carries essentially no information about the high-fidelity one. Multi-fidelity is pointless here by construction — there is nothing to transfer. |
| `operator_hard` | `pf_dist_corr < 0.15` | The condition vector barely predicts the field. Nothing conditions the prediction, so a model cannot do better than learning the field distribution. |
| `copy_lf_trivial` | raw **and** detrended `copy_lf_rel_l2 < 0.01` | Lifting LF onto the HF grid already reproduces HF to within 1%, structure included. Copying the coarse field solves the task; there is no fidelity gap to learn. |
| `level_dominated` | raw `< 0.01` but detrended `>= 0.01` | Copying LF looks near-perfect only because the field is nearly uniform. The score is dominated by a constant offset that LF gets for free, while the actual structure is still substantially wrong. |

### What `copy_lf_rel_l2` is

The error made by the dumbest possible model: don't predict anything, just take the coarse field, stretch it onto the fine grid, and submit that.
Per sample,

> `‖HF − lift(LF)‖₂ ⁄ ‖HF‖₂`, averaged over samples.

0.0006 means copying gets you to within 0.06% of the true field.
Any model has to beat this number to be doing anything at all.

Three things make it trustworthy — and one thing makes it treacherous:

- **Full resolution.**
  Not the characterizer's internal `lf_hf_rel_resid`, which nearest-index resamples onto a grid capped at 128 and misstates copy error in both directions (`allen_cahn_2d`: 0.0445 there, 0.0069 here).
- **Best-case registration.**
  `lift` is exactly the operation the half-pixel defect corrupted, so the value depends on how you interpolate.
  We take the minimum over the audited conventions, which is the best case for the copy hypothesis — a flagged dataset is trivial under *any* registration.
  (Reassuringly, the winning convention reproduces the generator's own per-PDE classification: node-periodic for the spectral solvers, cell-centred for the PyClaw ones.)
- **Relative, not absolute**, so it is comparable across datasets with wildly different amplitudes.
  The flip side: where LF and HF differ hugely in magnitude the ratio explodes and stops being informative — `ifc_poisson` reads 78.3 because an 8×8 Poisson solve and a 64×64 one are not on the same scale at all.
  Read large values as "not remotely trivial", not as a meaningful error.
- **The trap: it is not scale- or offset-free.**
  A nearly-uniform field has a large `‖HF‖` dominated by its constant level, which LF reproduces for free.
  So the **detrended** column — the same quantity after removing each sample's spatial mean from both fields — is the honest measure of structural agreement.
  Where the two disagree sharply, the raw number is measuring the offset, not the physics.

That is not hypothetical.
It is exactly what distinguishes the two flags:

| dataset | raw | detrended | ratio | verdict |
|---|---|---|---|---|
| `sharp/fisher_kpp_2d` | 0.0006 | 0.0216 | **35×** | level-dominated (HF field spans only [0.79, 1.00]) |
| `sharp/allen_cahn_2d` | 0.0069 | 0.1465 | **21×** | level-dominated — 15% structural error |
| `sharp/kuramoto_sivashinsky_2d` | 0.0047 | 0.0047 | 1.0× | genuinely trivial (zero-mean field) |

### The flagged datasets

| dataset | modes | raw / detrended copy rel-L2 |
|---|---|---|
| `sharp/fisher_kpp_1d` | copy-LF-trivial | 0.0023 / 0.0076 |
| `sharp/allen_cahn_1d` | operator-hard, copy-LF-trivial | 0.0027 / 0.0044 |
| `sharp/kuramoto_sivashinsky_2d` | operator-hard, copy-LF-trivial | 0.0047 / 0.0047 |
| `core/advection_diffusion_generated` | copy-LF-trivial | 0.0057 / 0.0066 |
| `sharp/sine_gordon_1d` | operator-hard, copy-LF-trivial | 0.0063 / 0.0063 |
| `sharp/kuramoto_sivashinsky_1d` | operator-hard, copy-LF-trivial | 0.0077 / 0.0077 |
| `sharp/fisher_kpp_2d` | level-dominated | **0.0006 / 0.0216** |
| `sharp/allen_cahn_2d` | operator-hard, level-dominated | **0.0069 / 0.1465** |
| `ext/gray_scott_2d` | MF-useless | LF–HF corr **0.008** |
| `ext/kuramoto_sivashinsky_1d` | MF-useless, operator-hard | LF–HF corr **−0.057** |
| `sharp/nls_1d` | operator-hard | 0.0124 / 0.0161 (borderline) |
| `sharp/phase_field_crystal_2d` | operator-hard, top-rung-converged | 0.0822 / 0.0939 (crystalline 2026-08-06 regen; L2→L3 carries no task — see its README) |
| `core/burgers_generated` | operator-hard | 0.2384 / 0.2384 |
| `core/burgers_param_generated` | operator-hard | 0.2767 / 0.2767 |

Three more sit just above the copy-LF threshold and deserve the same caution: `ext/pressure_poisson_poiseuille` (0.0117), `sharp/nls_1d` (0.0124), `ext/rayleigh_benard_2d` (0.0147).

### Scoring caveat: `top-rung-converged` (not a degeneracy mode)

`top-rung-converged` appears in the tables above alongside the four degeneracy flags, but it is a different kind of statement and is not counted in the 14.
A degeneracy flag says the *dataset* is unsuitable; this one says a particular *rung pairing* of an otherwise healthy dataset carries no task.

**Criterion.** Exact (spectral) interpolation of the top low-fidelity rung reproduces the high-fidelity field to $\le 10^{-5}$ relative $L_2$ on every test row.
When that holds, the LF→HF pair at the top of the ladder has no fidelity gap left to learn, and any score computed on it measures interpolation error rather than prediction skill.

**Who this affects.** `sharp/phase_field_crystal_2d` only.
Its crystalline fields are spectrally converged at L2 ($64^2$): exact interpolation of L2 reproduces L3 to $\le 1.7 \times 10^{-6}$ relative $L_2$ on every test row.
The real fidelity gap lives at **L1→L3**, with a per-row spectral copy gap of test median $4.5 \times 10^{-3}$.

**What to do.** Score this dataset at **L1→L3**, not L2→L3, and use spectral (not polynomial) interpolation when lifting LF for reference baselines.
Harnesses that select the low-fidelity input as `max(lf_fids)` will silently pick the converged rung and report a near-zero error that means nothing.
This is a property of how smooth one-mode PFC crystals are, not a defect in the arrays — the shipped fields are healthy physics.
Full statement in [`sharp/phase_field_crystal_2d/README.md`](sharp/phase_field_crystal_2d/README.md).

### Two caveats on `operator_hard`

**It is diluted by IC-encoded condition vectors.**
The five sharp datasets regenerated in this release now carry initial-condition coefficients in the condition vector, and distance correlation over a mostly-IC vector tends toward zero even when the field genuinely depends on it.
Read the flag as "distance correlation is the wrong instrument here", not "the map is unlearnable".
(An earlier revision cited `phase_field_crystal_2d` at 0.247 on its two physical parameters alone; after the 2026-08-06 crystalline regeneration that number is 0.024 — the crystalline map is genuinely stiff, ~1e4 linear amplification, so for this dataset the flag now reflects real physics rather than IC dilution.)

**The thresholds are hand-tuned**, described in the characterizer itself as "tunable; validated against KS/cahn".
They are a triage aid, not a verdict.
The flag is stable, though: over 6 independent subsamples `allen_cahn_2d` and `phase_field_crystal_2d` fire 6/6, while `fisher_kpp_2d` and `cahn_hilliard` fire 0/6.


## `core/` — 15 datasets

Base MFFP collection — classic multi-fidelity PDE/reanalysis benchmarks.

| # | dataset | dims | fidelities | cond dim | N (HF) | HF grid | LF–HF corr | copy-LF rel-L2 (raw / detrended) | flags |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **poisson_generated** | 2 | 3 | 5 | 400 | 64x64 | 0.977 | 16.4524 / 15.4279 | — |
| 2 | **heat_generated** | 2 | 3 | 3 | 400 | 64x64 | 0.989 | 0.0305 / 0.0607 | — |
| 3 | **burgers_generated** | 2 | 3 | 8 | 400 | 16x16 | 0.947 | 0.2384 / 0.2384 | operator-hard |
| 4 | **burgers_param_generated** | 2 | 3 | 9 | 400 | 16x16 | 0.927 | 0.2767 / 0.2767 | operator-hard |
| 5 | **advection_diffusion_generated** | 2 | 2 | 2 | 400 | 64x64 | 0.996 | 0.0057 / 0.0066 | copy-LF-trivial |
| 6 | **allen_cahn_generated** | 2 | 3 | 2 | 400 | 16x16 | 0.936 | 0.2611 / 0.2859 | — |
| 7 | **darcy_generated** | 2 | 3 | 16 | 400 | 128x128 | 0.995 | 0.0423 / 0.0709 | — |
| 8 | **lid_driven_cavity_generated** | 2 | 4 | 1 | 40 | 256x256 | 0.799 | 0.7029 / 0.7132 | — |
| 9 | **poisson_local** | 2 | 5 | 5 | 64 | 128x128 | 0.975 | 66.8286 / 65.6351 | — |
| 10 | **heat_local** | 2 | 5 | 3 | 1024 | 128x128 | 0.989 | 0.0340 / 0.0672 | — |
| 11 | **fluid** | 2 | 2 | 2 | 256 | 64x64 | 0.972 | 0.2051 / 0.2048 | — |
| 12 | **ifc_heat** | 2 | 4 | 3 | 5 | 64x64 | 0.956 | 0.0715 / 0.1316 | — |
| 13 | **ifc_poisson** | 2 | 4 | 5 | 5 | 64x64 | 0.909 | 78.2798 / 65.0214 | — |
| 14 | **era5** | 2 | 9 | 12 | 65 | 721x1440 | 0.995 | 0.1019 / 0.0990 | — |
| 15 | **pm_test** | 2 | 9 | 12 | 65 | 721x1440 | 0.995 | 0.1019 / 0.0990 | — |

## `ext/` — 8 datasets

Extension — new high-frequency 2D/1D fields the core set lacked.

| # | dataset | dims | fidelities | cond dim | N (HF) | HF grid | LF–HF corr | copy-LF rel-L2 (raw / detrended) | flags |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **helmholtz_2d** | 2 | 2 | 3 | 400 | 96x96 | 0.983 | 0.1097 / 0.1173 | — |
| 2 | **rayleigh_benard_2d** | 2 | 2 | 1 | 400 | 64x64 | 0.999 | 0.0147 / 0.0293 | — |
| 3 | **gray_scott_2d** | 2 | 2 | 2 | 400 | 72x72 | 0.008 | 183583542648.4986 / 169723011896.8980 | MF-useless |
| 4 | **wave_2d** | 2 | 2 | 3 | 400 | 80x80 | 0.846 | 0.5245 / 0.5511 | — |
| 5 | **eikonal_2d** | 2 | 2 | 3 | 400 | 64x64 | 0.990 | 0.0708 / 0.1157 | — |
| 6 | **cahn_hilliard_2d** | 2 | 2 | 2 | 400 | 64x64 | 0.333 | 0.8011 / 0.8493 | — |
| 7 | **kuramoto_sivashinsky_1d** | 2 | 2 | 3 | 400 | 256x120 | -0.057 | 1.2563 / 1.2945 | MF-useless, operator-hard |
| 8 | **pressure_poisson_poiseuille** | 2 | 4 | 2 | 400 | 64x64 | 0.927 | 0.0117 / 0.2781 | — |

## `sharp/` — 19 datasets

Sharp — shock / sharp-interface / smooth-control portfolio (SURF 2026).

| # | dataset | dims | fidelities | cond dim | N (HF) | HF grid | LF–HF corr | copy-LF rel-L2 (raw / detrended) | flags |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **euler** | 2 | 3 | 7 | 400 | 128x128 | 0.974 | 0.0574 / 0.1959 | — |
| 2 | **sod_1d** | 1 | 3 | 3 | 400 | 128 | 0.994 | 0.0508 / 0.1025 | — |
| 3 | **burgers_1d** | 1 | 3 | 2 | 400 | 128 | 0.939 | 0.2528 / 0.2528 | — |
| 4 | **burgers_2d** | 2 | 3 | 2 | 400 | 256x256 | 0.977 | 0.1935 / 0.1935 | — |
| 5 | **shallow_water_1d** | 1 | 3 | 2 | 400 | 128 | 0.723 | 0.0340 / 0.1618 | — |
| 6 | **shallow_water_2d** | 2 | 3 | 2 | 400 | 128x128 | 0.942 | 0.0504 / 0.3478 | — |
| 7 | **cahn_hilliard** | 2 | 3 | 19 | 400 | 256x256 | 0.990 | 0.0357 / 0.0358 | — |
| 8 | **allen_cahn_1d** | 1 | 3 | 19 | 400 | 512 | 1.000 | 0.0027 / 0.0044 | operator-hard, copy-LF-trivial |
| 9 | **allen_cahn_2d** | 2 | 3 | 19 | 400 | 256x256 | 0.993 | 0.0069 / 0.1465 | operator-hard, level-dominated |
| 10 | **porous_medium_1d** | 1 | 3 | 2 | 400 | 128 | 0.984 | 0.0425 / 0.0501 | — |
| 11 | **porous_medium_2d** | 2 | 3 | 2 | 400 | 256x256 | 0.994 | 0.0372 / 0.0381 | — |
| 12 | **fisher_kpp_1d** | 1 | 3 | 18 | 400 | 512 | 1.000 | 0.0023 / 0.0076 | copy-LF-trivial |
| 13 | **fisher_kpp_2d** | 2 | 3 | 50 | 400 | 256x256 | 0.984 | 0.0006 / 0.0216 | level-dominated |
| 14 | **phase_field_crystal_2d** | 2 | 3 | 18 | 400 | 128x128 | 0.877 | 0.0822 / 0.0939 | operator-hard, top-rung-converged |
| 15 | **kuramoto_sivashinsky_1d** | 1 | 3 | 17 | 400 | 512 | 1.000 | 0.0077 / 0.0077 | operator-hard, copy-LF-trivial |
| 16 | **kuramoto_sivashinsky_2d** | 2 | 3 | 17 | 400 | 256x256 | 0.995 | 0.0047 / 0.0047 | operator-hard, copy-LF-trivial |
| 17 | **nls_1d** | 1 | 3 | 17 | 400 | 512 | 1.000 | 0.0124 / 0.0161 | operator-hard |
| 18 | **sine_gordon_1d** | 1 | 3 | 17 | 400 | 512 | 1.000 | 0.0063 / 0.0063 | operator-hard, copy-LF-trivial |
| 19 | **helmholtz_2d** | 2 | 3 | 2 | 400 | 256x256 | 0.991 | 2.9333 / 2.9308 | — |
