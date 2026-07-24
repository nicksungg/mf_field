---
name: cycle-008-exp-13-final
description: Cycle-008 H3 (exp 13) FINAL — three-stage curriculum on fno_coreg_residual REVERTED (genuine, architecture-falsified-on-residual-ladder). Composite 0.030408 flat vs baseline / +9.66% vs banked best 0.027729. fno_coreg_residual × ifc_heat regressed 19× (0.026→0.509) tripping universal kill-switch 26× over. fno_coreg_residual × ifc_poisson regressed 2.15× (0.074→0.159). H3-specific Stage3/Stage2 kill-switch did NOT trip (ratio=1.0) — damage occurred in Stages 1/2; design flaw in kill-switch assumption. KEEP-worthy meta-fix delivered: recipe_hash checkpoint guard pattern works correctly, closes cycle-003 backlog item for ALL future research-mode experiments on this family. Architectural lesson — three-stage frozen-LF-HF-residual curricula are INCOMPATIBLE with co-evolved residual ladder designs (fno_coreg_residual, fno_coregionalization); end-to-end joint training remains the correct recipe for these families. Branch experiment/13-fno_coreg_residual-three-stage @ 420a51c preserved for recipe_hash pattern reuse; three-stage curriculum NOT reusable.
metadata:
  type: experiment
tags:
  - factory
  - experiment
  - factory_mffp
  - cycle-008
  - h3
  - fno_coreg_residual
  - three-stage-curriculum
  - recipe-hash-guard
  - meta-fix-cycle-003
  - genuine-revert
  - architecture-falsified
  - co-evolved-residual-ladder
  - kill-switch-design-flaw
project: factory_mffp
experiment_id: "013"
cycle: cycle-008
hypothesis_id: H3
phase: eval_complete_revert
verdict: revert
verdict_class: genuine_revert
verdict_subclass: architecture_incompatible_three_stage_on_residual_ladder
ceo_intent: revert
date: 2026-06-02
branch: experiment/13-fno_coreg_residual-three-stage
branch_status: preserved_for_recipe_hash_pattern_reuse_only
parent_branch: cycle-008-entry-baseline
parent_commit: 1249f2d
commit: 420a51c
mutable_surface: models/fno_coreg_residual/smoke_eval.py
mutable_surface_count: 1
files_changed_loc_delta: "+401/-73"
model_py_byte_identical_to_baseline: true
recipe_hash: 148a2641b07fe5da
stage_strides: [0.25, 0.5, 0.25]
score_metric: composite_nRMSE
score_before_baseline: 0.030407732506238343
score_before_banked_best: 0.027728854219631654
score_after: 0.030407732506238343
score_delta_vs_baseline: 0.0
score_delta_pct_vs_baseline: 0.0
score_delta_vs_banked_best: 0.002678878286606689
score_delta_pct_vs_banked_best: 9.660977209473298
fno_coreg_residual_ifc_heat_before_single_stage: 0.026277
fno_coreg_residual_ifc_heat_after_three_stage: 0.509105074500434
fno_coreg_residual_ifc_heat_delta_pct: 1837.4
fno_coreg_residual_ifc_heat_best_val: 0.042762876943228965
fno_coreg_residual_ifc_heat_val_test_gap_x: 12
fno_coreg_residual_ifc_poisson_before_single_stage: 0.074192
fno_coreg_residual_ifc_poisson_after_three_stage: 0.15936368490302597
fno_coreg_residual_ifc_poisson_delta_pct: 114.8
fno_coreg_residual_ifc_poisson_builder_expected_range: [0.05, 0.06]
fno_coreg_residual_ifc_poisson_observed_vs_expected_upper: 2.656
universal_heat_kill_switch_threshold: 0.0194
universal_heat_kill_switch_tripped: true
universal_heat_kill_switch_ratio_over_threshold: 26.24
h3_stage3_stage2_heat_ratio: 1.0
h3_stage3_stage2_heat_kill_switch_threshold: 1.25
h3_stage3_stage2_heat_kill_switch_tripped: false
h3_kill_switch_design_flaw: true
h3_stage3_stage2_poisson_ratio: 0.289
h3_stage3_stage2_poisson_note: "Stage 3 improved poisson 3.46× over Stage 2 — but absolute level (0.159) still 2.15× the paper-recipe baseline (0.074)."
smoke_wall_seconds_h3_family: 50.7
smoke_wall_budget_seconds: 360
smoke_wall_under_budget_factor: 7.1
total_cycle_eval_wall_seconds: 71
recipe_hash_guard_outcome: works_correctly
recipe_hash_guard_stale_rejection_log: "[resume] REJECTED stale checkpoint: recipe_hash '148a2641b07fe5da' != '0095c3ff614e17b8'"
recipe_hash_guard_keep_worthy_in_isolation: true
recipe_hash_guard_three_stage_curriculum_keep_worthy: false
cycle_003_backlog_item_closed_for_this_family: fix_checkpoint_resume_contamination_via_recipe_hash_guard
cycle_009_action_recipe_hash_pattern: cherry_pick_into_models_common_recipe_hash_py_and_apply_to_all_families
cycle_009_action_three_stage_curriculum: do_not_cherry_pick_stage_gating_logic
cycle_009_candidate_families_for_three_stage: [mf_fno_transfer_bar, fno_mf_stack]
cycle_009_NOT_candidate_families_for_three_stage: [fno_coreg_residual, fno_coregionalization]
project_genuine_revert_count: 5
project_revert_bookkeeping_keep_intent_count: 7
cycle_008_sequence: H1_KEEP_INTENT_0_027729 + H2_GENUINE_REVERT + H3_GENUINE_REVERT
cycle_008_consecutive_genuine_reverts: 2
cycle_008_entry_baseline_composite: 0.030408
cycle_008_h1_banked_best_composite: 0.027729
cycle_009_entry_baseline: experiment/11-fno_coregionalization-paper-capacity @ 18d83a6 @ 0.027729
cycle_009_entry_baseline_UNCHANGED_by_h3: true
source: factory-archivist
---

# Experiment #013: H3 (cycle-008) — Three-stage curriculum on `fno_coreg_residual`

## Hypothesis

Composing three independent curriculum stages — (1) LF-only pretrain of per-fidelity FNOs, (2) freeze LF stack and train HF residual, (3) unfreeze and add the coregionalization-residual basis head — exploits BOTH the `TRANSFER_SIGNAL_UNUSED` lever on `fno_coreg_residual × ifc_heat` AND the basis-head expressivity lever, without touching MFRNP loss weights. MANDATORY `recipe_hash` checkpoint guard closes the cycle-003 H1 stage-resume contamination pathway as a side-effect meta-fix.

## Result

**REVERT (genuine, architecture-falsified)** — composite_nRMSE flat at baseline 0.030408 (+0.00% vs baseline; **+9.66% vs banked best 0.027729**).

The composite is flat ONLY because `fno_coreg_residual` regressed so badly it no longer wins either dataset cell on the leaderboard — its collapse never enters the per-cell argmin. Same surface pattern as cycle-008 H2 (composite flat at baseline → family non-dominant) but a different underlying cause: H2 added a NEW non-dominant family; H3 BROKE an existing dominant family.

## Quantitative outcome

| Metric | Value | Threshold / Target | Status |
|---|---|---|---|
| Composite nRMSE (H3 branch) | 0.030408 | < 0.027729 (banked best) | **REGRESSION +9.66%** |
| `fno_coreg_residual × ifc_heat` | 0.509105 | < 0.0194 universal kill-switch | **TRIPPED 26×** (was 0.026 single-stage; +1837%) |
| `fno_coreg_residual × ifc_poisson` | 0.159364 | Builder predicted 0.05–0.06 | **+165% out of range** (was 0.074 single-stage; +115%) |
| H3-specific Stage3/Stage2 Heat ratio | 1.00 | < 1.25 → KEEP | NOT TRIPPED (Stage 2 already produced 0.509; Stage 3 was a no-op on Heat) |
| Stage 3 vs Stage 2 Poisson ratio | 0.289 | (descriptive) | Stage 3 improved Poisson 3.46× over Stage 2 end; absolute level still 2.15× paper-recipe baseline |
| val/test gap on Heat | 12× (val 0.043 → test 0.509) | < 2× normal | **catastrophic** — final-state-checkpoint divergence OR overfitting |
| Smoke wall (fno_coreg_residual, both datasets) | 50.7 s | < 360 s projected | **CLEAR (~7× under budget)** |
| Total cycle_eval wall | 71 s | < 14400 s | CLEAR |
| Recipe_hash checkpoint guard | works correctly | live verification | **PASS — meta-fix delivered** |

## What Changed

Three-stage curriculum (S1 LF pretrain stride 0.25 lr=1e-3 BasisHead frozen → S2 HF residual stride 0.5 lr=3e-4 LF frozen via actual `requires_grad=False` NOT zero-loss masking → S3 unfreeze all stride 0.25 lr=9e-5 per cycle-003 BasisHead instability prior) + MANDATORY `recipe_hash` checkpoint guard implemented in `models/fno_coreg_residual/smoke_eval.py` (+401/-73 LOC). `model.py` BYTE-IDENTICAL to baseline. Branch `experiment/13-fno_coreg_residual-three-stage @ 420a51c` cut independently from cycle-008 entry baseline `1249f2d`.

## Architectural lesson (input to cycle-009 strategy)

Three-stage frozen-LF-HF-residual curricula are **architecturally INCOMPATIBLE** with co-evolved residual ladder designs (`fno_coreg_residual`, `fno_coregionalization`).

1. **`fno_coreg_residual` is a residual ladder design** (`model.py:43-188`). The HF prediction = LF features → residual correction → BasisHead aggregation. The LF and HF networks are designed to **co-evolve** — the HF network learns a correction that depends on the current LF representation.

2. **Stage 2 of H3 freezes the LF stack** (`requires_grad=False`), forcing the HF residual to correct against a fixed LF state. But the LF state from Stage 1 (LF-only pretrain, `m != hf_m` samples) is NOT the LF representation the HF residual was designed to correct — it's an out-of-distribution frozen LF state from a pretraining regime the architecture wasn't built for.

3. **Result:** the HF residual learns garbage in Stage 2, with no information back to the LF stack to fix the mismatch. Stage 3's unfreeze comes too late — the HF residual is already in a poor local minimum. The val/test gap of 12× on Heat confirms catastrophic overfitting (or final-state-checkpoint divergence) in this regime.

4. **In contrast, H1 (capacity bump on `fno_coregionalization`) and the prior single-stage `fno_coreg_residual` recipe** both train ALL networks co-evolved end-to-end. The architecture's inductive bias is preserved.

**Implication for cycle-009:** three-stage curricula MAY be appropriate for families where LF and HF networks are **independent by design** (e.g., `mf_fno_transfer_bar` — its LF FNO outputs a feature map that's an INPUT to the HF FNO, not a co-trained residual; `fno_mf_stack` — per-fidelity stacked predictions, no explicit residual). For `fno_coreg_residual` and `fno_coregionalization` (co-evolved designs), end-to-end joint training remains the right recipe.

## Kill-switch design retrospective

The H3-specific kill-switch (`Stage3/Stage2 Heat ratio > 1.25 → REVERT to Stage 2`) was designed assuming Stage 3's unfreeze would be the source of damage (BasisHead instability + LF unfreeze at `lr=9e-5`). **Reality:** damage occurred in Stages 1/2; Stage 3 actually helped Poisson 3.46× (0.551 → 0.159) but couldn't recover Heat. The Stage3/Stage2 ratio was 1.00 because Stage 2 already produced 0.509 on Heat.

The universal `ifc_heat > 0.0194` kill-switch caught it — but only post-hoc at finalize time, not mid-training.

**Lesson for cycle-009 kill-switch design (the missing piece in H3):**

Multi-stage curricula MUST include an absolute Stage 2 vs baseline check in addition to the universal post-hoc kill-switch:

```
stage2_final_hf_test_nrmse > 1.25 × prior_single_stage_test_nrmse → REVERT to baseline
```

This catches Stage-2-internal damage before Stage 3 wastes additional wall time. The cycle-009 strategy templates for any multi-stage hypothesis must specify BOTH:
- Per-stage absolute thresholds (vs the prior single-stage baseline on the same family)
- Inter-stage ratio thresholds (between consecutive stages)

Single inter-stage ratio kill-switches assume damage occurs in the LATER stage; this assumption is fragile.

## KEEP-worthy meta-fix (recipe_hash pattern)

Despite the architectural failure of the H3 three-stage curriculum, the cycle-003 backlog **`recipe_hash` checkpoint guard** meta-fix WORKED correctly:

- Stale checkpoint rejection log line verified: `[resume] REJECTED stale checkpoint: recipe_hash '148a2641b07fe5da' != '0095c3ff614e17b8'`.
- Family retrained from scratch under the new recipe (correct behavior).
- The PATTERN — `sha256(json.dumps({**SMOKE_DEFAULTS, "stage_strides":[0.25,0.5,0.25]}, sort_keys=True).encode()).hexdigest()[:16]` written to `last.pt`/`best.pt` and checked at resume — is **reusable**.

**cycle-009 action:** cherry-pick the `recipe_hash` pattern from H3's `smoke_eval.py` into a portable utility (e.g. `models/_common/recipe_hash.py`) and apply it to ALL family `smoke_eval.py` files. This closes the cycle-003 H1 stage-resume contamination pathway **project-wide**, not just for `fno_coreg_residual`.

The recipe_hash guard is the H3 KEEP-worthy artifact **in isolation**. The three-stage curriculum is **NOT** keep-worthy. We preserve the guard pattern for cycle-009 but do NOT keep the H3 commit (the catastrophic Heat regression dominates).

## Branch preservation

- **Branch:** `experiment/13-fno_coreg_residual-three-stage @ 420a51c` — PRESERVED.
- **What to reuse:** the `recipe_hash` checkpoint guard implementation (lines 113-123, 461-485, 495, 498, 505 of `smoke_eval.py`) — verbatim or refactored into a shared utility module.
- **What NOT to reuse:** the stage gating logic (Stage 1 LF pretrain, Stage 2 frozen-LF HF residual, Stage 3 unfreeze) — do NOT cherry-pick into other families with co-evolved residual ladder architectures. Architectural lesson above applies.
- **Cycle-009 entry baseline:** UNCHANGED from cycle-008 H1 banked best `experiment/11-fno_coregionalization-paper-capacity @ 18d83a6 @ composite 0.027729`. The H3 REVERT does NOT move the project baseline.

## Cycle-008 sequence summary

- **H1 (KEEP intent, banked):** composite 0.030408 → 0.027729 (−8.81%), `fno_coregionalization × ifc_heat` 0.01551 → 0.012898 (−16.84%). New project best; 89.93% of parallel-bench bar gap closed. Verdict label `revert_bookkeeping_keep_intent` (precheck-bookkeeping override).
- **H2 (GENUINE REVERT):** new family `fno_coreg_conditioned` (FiLM-via-LayerNorm); composite flat at entry baseline 0.030408 / +9.66% vs banked best. Architecture-falsified on Poisson (FiLM cannot synthesize LF→HF correlation). Branch `experiment/12-fno_coreg_conditioned-film @ 540e684` preserved.
- **H3 (GENUINE REVERT):** three-stage curriculum on `fno_coreg_residual`; composite flat at entry baseline 0.030408 / +9.66% vs banked best. Architecture-falsified on residual ladder (three-stage frozen-LF curriculum incompatible with co-evolved design). Branch `experiment/13-fno_coreg_residual-three-stage @ 420a51c` preserved for `recipe_hash` pattern reuse only.

Cycle-008 net: **one KEEP intent** (banked best at 0.027729) + **two consecutive GENUINE REVERTs**. Project genuine-REVERT count now 5 (cycle-003 H1, cycle-006 H1, cycle-007 H2, cycle-008 H2, cycle-008 H3). Project `revert_bookkeeping_keep_intent` streak remains at 7 unchanged.

## Links

- Project: factory_mffp
- Branch: `experiment/13-fno_coreg_residual-three-stage @ 420a51c` (preserved)
- Parent baseline: `1249f2d` (cycle-008 entry)
- Build phase note: [[cycle-008-exp-13-build]]
- Prior cycle-008 H2 final note: [[cycle-008-exp-12-final]]
- Prior cycle-008 H1 note: [[cycle-008-exp-11]]
- Strategy snapshot: [[factory_mffp-2026-06-02]] (cycle-008 strategy)
- Patterns:
  - [[patterns]] — "Three-stage frozen-LF-HF-residual curricula are incompatible with co-evolved residual ladder designs" (NEW, this exp)
  - [[patterns]] — "Multi-stage kill-switches must include Stage-2-vs-baseline absolute check, not only inter-stage ratio" (NEW, this exp)
  - [[patterns]] — "Bookkeeping-overridable REVERT vs genuine architecture-falsified REVERT" (cycle-008 H2)
  - [[patterns]] — "FiLM-via-LayerNorm on HF-only FNO cannot synthesize LF→HF correlation" (cycle-008 H2, related architectural-falsification class)
