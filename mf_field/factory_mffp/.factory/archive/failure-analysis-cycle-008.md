---
name: failure-analysis-cycle-008
description: Cycle-008 baseline Failure Analyst report. Baseline 0.030408 is REPRODUCIBLE from clean tree on `experiment/9-fno_coregionalization-constructor-fix @ 1249f2d` — the cycle-005 H2 heat number 0.01551 survives a fresh end-to-end re-eval, retiring the silent-regression-cache-layer cliff. Bar (mf_fno_transfer_bar parallel-bench) = 0.027429; gap = +10.86% over bar, target = ≤0.024686 (−10% of bar). Dominant lever by composite log-weight = CAPACITY_PARETO on `fno_coregionalization` × `ifc_heat` — Heat contributes 12.6× more log-weight to the composite-gap-to-bar than Poisson (+0.191 vs +0.015). Three formal REVERTs on the MFRNP loss-recipe transfer lever (cycle-003 H1, cycle-006 H1, cycle-007 H2) = MFRNP is BOTH backbone-coupled AND dataset-entangled within the same family; do-not-retry pinned. Three new transfer-learning ideas surfaced and not yet tested in c008 state: (a) re-bind c007 H2 LF→HF two-stage schedule to the repaired fno_coregionalization constructor (committed code never evaluated); (b) NEW sibling family `models/fno_coreg_conditioned/` — m-conditioned single HF FNO (candidate unified Heat+Poisson winner); (c) curriculum LF→stack→HF-head on fno_coreg_residual (compose two specialists across three stages). New taxonomy category promoted active: NEAR_PARITY_INCREMENTAL on fno_mf_stack×Poisson (+1.5% over bar).
metadata:
  type: project
tags:
  - factory
  - failure-analysis
  - factory_mffp
  - cycle-008
  - baseline
  - reproducible-best
  - capacity-pareto-heat-dominant
  - family-pde-specialization-asymmetry
  - mfrnp-recipe-revert-3of3
  - lf-hf-transfer-h2-not-rebound
  - new-lever-coreg-m-conditioned-fno
  - new-lever-curriculum-lf-stack-hf-head
project: factory_mffp
cycle: cycle-008
phase: failure-analysis
round: baseline
date: 2026-06-02
source: factory-archivist
ceo_verdict: PROCEED
baseline_composite: 0.030408
baseline_commit: 1249f2d
baseline_branch: experiment/9-fno_coregionalization-constructor-fix
bar_composite: 0.027429
bar_heat: 0.01281
bar_poisson: 0.05871
dethrone_target: 0.024686
gap_to_bar_pct: 10.86
gap_log_ratio_heat: 0.191
gap_log_ratio_poisson: 0.015
heat_vs_poisson_log_weight_ratio: 12.6
ifc_heat_best_family: fno_coregionalization
ifc_heat_best_value: 0.01551
ifc_poisson_best_family: fno_mf_stack
ifc_poisson_best_value: 0.05961
dominant_failure_mode: CAPACITY_PARETO
dominant_failure_cell: "fno_coregionalization x ifc_heat"
dominant_cell_absolute: "fno_coregionalization x ifc_poisson (0.7501)"
mfrnp_recipe_revert_count: 3
mfrnp_recipe_revert_cycles: ["cycle-003-H1", "cycle-006-H1", "cycle-007-H2"]
new_levers_surfaced: 3
---

# Failure Analysis — Cycle 008 baseline (factory_mffp)

## Cycle Setup

- **Branch under test:** `experiment/9-fno_coregionalization-constructor-fix @ 1249f2d`.
- **Baseline composite_nRMSE:** **0.030408** (geomean of best per-dataset: ifc_heat 0.01551, ifc_poisson 0.05961).
- **Eval origin:** banked from cycle-007 H1 (the constructor-fix commit). First cycle where the cycle-005 H2 heat number 0.01551 survives a fresh end-to-end re-eval from a clean tree — the silent-regression-cache-layer cliff is retired.
- **CEO verdict:** PROCEED. See `.factory/reviews/ceo-verdict-failure_analyst.md`.
- **Full analysis source:** `.factory/research/runs/cycle-008-baseline/failure_analysis.md`.

## Headline numbers

| Reference point                                  | composite_nRMSE | ifc_heat                       | ifc_poisson                |
|---                                               |---:             |---                             |---                         |
| **R0 cycle-008 baseline (reproducible)**         | **0.030408**    | 0.01551 `fno_coregionalization` | 0.05961 `fno_mf_stack`     |
| Cycle-007 H1 (same commit 1249f2d)               | 0.030408        | 0.01551 `fno_coregionalization` | 0.05961 `fno_mf_stack`     |
| Cycle-005 H2 (aspirational, dirty-tree)          | 0.029357        | 0.01551 `fno_coregionalization` | 0.05556 `fno_coreg_residual` |
| Bar (`mf_fno_transfer_bar` parallel-bench)       | 0.027429        | 0.01281                         | 0.05871                    |
| Bar dethrone target (−10%)                       | **≤0.024686**   | —                               | —                          |
| Paper                                            | —               | 0.074                           | 0.036                      |

- **Gap to bar:** +0.002978 composite (+10.86% over bar). About **one symmetric −10% step short** of dethroning.
- **Per-dataset log-space gap to bar:** ifc_heat +0.191 log-ratio (1.21× over bar) vs ifc_poisson +0.015 log-ratio (1.015× over bar) → **Heat contributes 12.6× more composite-gap log-weight than Poisson**.

## Dominant lever — CAPACITY_PARETO on `fno_coregionalization` × `ifc_heat`

By composite-gap log-weight, the **single highest-EV cell** to attack is `fno_coregionalization` × `ifc_heat` at 0.01551 (the leaderboard winner, but 1.21× over bar). Closing this from 0.01551 → 0.01022 (the symmetric −10% target if Poisson held) is the largest available lever.

**Within-family knobs in `models/fno_coregionalization/smoke_eval.py` `SMOKE_DEFAULTS`:**
- K=10 → 20 (paper config from `full_config.json`).
- `b_hidden`=64 → 128.
- `n_blocks`=4 → 6.
- epochs=200 → 100–150 with stronger warmup if wall-time bound.

**Expected impact (single PR):** heat 0.01551 → ~0.012, composite → ~0.027 — within striking distance of the bar.

## Dominant absolute-nRMSE failure — `fno_coregionalization` × `ifc_poisson` (0.7501)

This cell has persisted since cycle-001 at ~0.75. The K=10 MLP-basis `B(m)=MLP([m,m²])` cannot fit Poisson's non-monotone m-modulation; Heat works at 0.01551 because Heat's m-modulation is smooth-monotone. The cell does NOT enter the composite (Poisson winner is `fno_mf_stack`), but disqualifies fno_coregionalization from being a single-family answer to the project. **A different family (callout #5b below) is the cleaner unified path.**

## Failure Distribution (12 actionable cells; v9 reference excluded)

| Category                              | Cells | Composite-gap weight |
|---                                    |---:   |---                   |
| **CAPACITY_PARETO**                   | 1     | **Highest** — fno_coregionalization × heat, +21% over bar, 12.6× log-weight |
| FAMILY_PDE_SPECIALIZATION_ASYMMETRY   | 2     | High structural — fno_coregionalization/Poisson 0.7501; fno_mf_stack/Heat 0.0999 |
| NEAR_PARITY_INCREMENTAL (NEW c008)    | 1     | Medium — fno_mf_stack/Poisson +1.5% over bar |
| TRANSFER_SIGNAL_UNUSED                | 1     | Medium — fno_coreg_residual/Heat (H2 schedule never rebound) |
| RECIPE_DATASET_NONPORTABILITY         | 1     | Already-explored — fno_coreg_residual/Poisson, REVERT 3/3 lever |
| BAR_UNDERTRAINING_VS_CACHE            | 2     | Low — mf_fno_transfer_bar smoke side both datasets |
| BACKBONE_INDUCTIVE_BIAS_MISMATCH      | 4     | Low — transolver_* + v9 orthogonal direction |

**Promotions this cycle:** `NEAR_PARITY_INCREMENTAL` promoted latent → active (fno_mf_stack/Poisson is now 1.015× over bar; was 1.50× in cycle-002 H4).

## Five Required Callouts (CEO PROCEED-affirmed)

### 1. Heat is the dominant composite lever (12.6× larger log-weight than Poisson)
Heat +21.05% over bar (log-ratio +0.191); Poisson +1.53% over bar (log-ratio +0.015). Closing heat 0.01551 → 0.01022 is the single highest-EV step. **All attack budget should flow here first.**

### 2. `fno_coregionalization` × Poisson (0.7501) is NOT cleanly addressable within the family
- Persists since cycle-001; K=10 MLP-basis cannot fit Poisson non-monotone m-modulation.
- Within-family levers: K=10→20, neural-ODE basis (expensive), re-binding the c007 H2 LF→HF schedule.
- **The cell is NOT mechanically required for composite** — `fno_mf_stack` already owns Poisson at 0.05961.
- **A different family** (intervention 5b: `fno_coreg_conditioned`) is the cleaner answer for unifying Heat+Poisson in one architecture.

### 3. Residual families (fno_coreg_residual, fno_mf_stack) — architecture vs recipe constraint
Both families are **architecture-improvable, recipe-stuck**.
- `fno_coreg_residual` heat moved −25.3% c005→c008 via K=20/b_hidden=128 (architecture); 3 cycles of recipe tweaks REVERTed.
- `fno_mf_stack` at paper-canonical MFRNP recipe; only capacity/curriculum remain.
- **Loss-recipe levers should not be retried; capacity and transfer-schedule levers remain.**

### 4. Cross-architecture portability lesson — MFRNP recipes do NOT transfer (3 formal REVERTs)
1. **cycle-003 H1** — MFRNP Poisson5 recipe (HF=2.0/LF=0.25) transplant from `fno_mf_stack` → `fno_coreg_residual`. Heat unchanged; Poisson +268% regression. REFUTED the framing "PDE-class-bound recipe": **recipe is backbone-coupled**.
2. **cycle-006 H1** — Cross-architecture transplant `fno_coreg_residual` → `fno_mf_stack`. Cross-architecture transfer failed. REVERT.
3. **cycle-007 H2** — Per-dataset dispatch WITHIN `fno_coreg_residual` (heat keeps current recipe, poisson reverts to MFRNP). "Heat invariant by construction" claim **empirically falsified at 6.5× the noise band** (heat 0.02628 → 0.03487, +32.7%) due to fresh-train variance + shared training infrastructure. REVERT.

**Conclusion (cycle-008 lock-in):** MFRNP HF=2.0/LF=0.25 reweighting is **backbone-coupled AND dataset-entangled within the same family**. Any new MFRNP-style reweighting hypothesis must declare a heat-invariance kill-switch AND best-of-N (N≥2) seed control with frozen heat seed. **Prior on this lever = REVERT 3/3. DO NOT RETRY.**

### 5. Three new transfer-learning ideas (not yet tested in c008 state)

**(a) Re-bind c007 H2 LF→HF two-stage schedule to the repaired fno_coregionalization constructor.**
The schedule is committed code on the parent branch but the H1 commit reverted to a one-stage train when fixing the constructor. Re-applying the schedule on top of H1 is a one-PR addition that has been blocked since c007. Files: `models/fno_coregionalization/smoke_eval.py` (re-wire `pretrain_frac` arg + 2-stage optimizer/scheduler reset). Projected heat: ≈0.018 on residual family; on coregionalization with proper constructor could move heat further toward bar (0.01281).

**(b) NEW family `models/fno_coreg_conditioned/` — single full-resolution HF FNO conditioned on coregionalization-m basis.**
Currently `f(x,m) = sum_k B_k(m) * h_k(x)`. Proposed: feed `B(m) ∈ R^K` as a *broadcast spatial conditioning channel* into a single HF FNO. Decouples m-modulation from the FNO trunk and lets full FNO capacity be reused per-m. **Candidate single-family answer for unified Heat + Poisson winner** (addresses FAMILY_PDE_SPECIALIZATION_ASYMMETRY). NEW sibling family, not a fix to fno_coregionalization (project rule: "do not delete or rename existing model families").

**(c) NEW: Curriculum LF→stack→HF-head on fno_coreg_residual.**
Three-stage training: Stage 1 LF-only pretrain of per-fidelity FNOs in fno_mf_stack style (Poisson recipe); Stage 2 freeze LF stack, train HF FNO residual; Stage 3 unfreeze + add coregionalization-residual head from fno_coreg_residual for fine-grained m-modulation. Composes two specialists in stages instead of as a hybrid architecture. Needs recipe-fingerprint checkpoint guard (cycle-003 lesson). Files: `models/fno_coreg_residual/smoke_eval.py`.

## Recommended Interventions (ranked, all within `models/**`)

1. **`fno_coregionalization` capacity bump** (CAPACITY_PARETO) — K=10→20, b_hidden=64→128, n_blocks=4→6 in `models/fno_coregionalization/smoke_eval.py SMOKE_DEFAULTS`. Expected heat 0.01551 → ~0.012, composite → ~0.027. **Single largest lever.**
2. **NEW family `models/fno_coreg_conditioned/`** — m-conditioned single HF FNO. Speculative; candidate single-family Heat+Poisson winner.
3. **Re-bind c007 H2 LF→HF schedule on repaired fno_coregionalization** — committed code never evaluated. One-PR.
4. **Curriculum LF→stack→HF-head on fno_coreg_residual** — staged-training composition of the two specialists.
5. **fno_mf_stack capacity bump on Poisson** — NEAR_PARITY_INCREMENTAL; smaller composite lever (12.6× less log-weight).

**Defer:** `mf_fno_transfer_bar` smoke-undertraining fix — does not help composite; raises the bar to dethrone.

**Do NOT retry:** MFRNP loss-recipe dispatch on `fno_coreg_residual` (prior = REVERT 3/3).

## Cross-Cycle Comparison (005 → 008)

| Metric / cell                                | c005 H2  | c006 H1  | c007 R0  | c007 H1 (=c008 base) | Trend                                          |
|---                                           |---:      |---:      |---:      |---:                  |---                                            |
| composite_nRMSE                              | 0.029357 | 0.041963 | 0.039578 | **0.030408**         | aspirational → reproducible                  |
| `fno_coregionalization` × ifc_heat           | 0.01551  | CRASH    | CRASH    | **0.01551**          | recovered exactly                            |
| `fno_coregionalization` × ifc_poisson        | 0.77562  | CRASH    | CRASH    | **0.75015**          | recovered; STILL 12.6× over bar              |
| `fno_coreg_residual` × ifc_heat              | 0.03519  | 0.03059  | 0.02628  | 0.02628              | improving — K=20/b_hidden=128 banked         |
| `fno_coreg_residual` × ifc_poisson           | 0.05556  | 0.05756  | 0.07419  | 0.07419              | regressing — recipe-overfit-across-datasets  |
| `fno_mf_stack` × ifc_poisson                 | 0.08829  | 0.05961  | 0.05961  | 0.05961              | stable at near-bar parity                   |
| `mf_fno_transfer_bar` × ifc_heat (smoke)     | n/a      | 0.03317  | 0.03317  | 0.03317              | stable, undertrained                         |
| `mf_fno_transfer_bar` × ifc_poisson (smoke)  | n/a      | 0.08333  | 0.08333  | 0.08333              | stable, undertrained                         |

**Headline c005 → c008:**
- Reproducible best moved from aspirational unreproducible 0.029357 → reproducible 0.030408 — the H1 constructor fix recovered c005's heat cache exactly.
- `fno_coregionalization` family is re-runnable from committed tree; silent-regression-cache-layer pattern is resolved.
- `fno_coreg_residual` heat −25.3% improvement banked; Poisson +33.5% regression on the recipe-overfit lever (recipe-dispatch lever is now closed).

## Constraint re-statements pinned for cycle-008+ Strategist

- **MFRNP recipe transfer (cross-architecture OR per-dataset-within-family):** prior REVERT 3/3. Any new hypothesis adding MFRNP-style reweighting must declare (i) a kill-switch on heat invariance with band derived from ≥3 prior fresh-train values, AND (ii) best-of-N seed control with the heat seed frozen across treatment/control. (See [[patterns]] §"Fresh-train variance can swamp claimed invariance".)
- **Family selection:** for the Poisson frontier, do NOT chase fno_coregionalization; let `fno_mf_stack` own Poisson and put coregionalization capacity into Heat. Cross that with the new `fno_coreg_conditioned` family for the unified-architecture bet.

## Related notes

- [[failure-analysis-cycle-007]] — prior R1 baseline framing; 0.039578 → 0.030408 reconciliation via the H1 constructor fix.
- [[cycle-007-summary]] — H1 PROCEED (constructor fix), H2 REVERT (heat invariance falsified).
- [[failure-analysis-cycle-003]] — first genuine REVERT (cross-architecture recipe portability disproof).
- [[failure-analysis-cycle-006]] — second cross-architecture recipe transfer failure (REVERT).
- [[patterns]] §"Cross-architecture recipe portability is NOT guaranteed even when receiving architecture shares structural family" — second supporting observation (cycle-007 H2 = 3/3 reverts).
- [[patterns]] §"Fresh-train variance can swamp claimed invariance" — cycle-007 H2 instance, applies to all future "invariant by construction" Strategist claims.
- [[patterns]] §"silent-regression-cache-layer-masks-uncommitted-load-bearing-state" — RESOLVED by cycle-008 reproducible baseline.
- [[factory_mffp]] — project dashboard.

## Tags

`failure-analysis`, `cycle-008`, `baseline`, `reproducible-best-recovered`,
`capacity-pareto-heat-dominant`, `family-pde-specialization-asymmetry`,
`cross-architecture-recipe-nonportability-3of3-revert`,
`recipe-dataset-nonportability`, `fno_coregionalization-poisson-intrinsic`,
`bar-undertraining-smoke-vs-parallel-bench`, `lf-hf-transfer-h2-schedule-not-rebound`,
`new-lever-coreg-m-conditioned-fno`, `new-lever-curriculum-lf-stack-hf-head`,
`near-parity-incremental-new-c008`
