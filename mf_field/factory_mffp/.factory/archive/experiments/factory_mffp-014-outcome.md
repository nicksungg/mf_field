---
name: factory_mffp-014-outcome
description: Cycle-009 H1+H2 bundle (exp 14) FINAL — formal verdict `revert_bookkeeping_keep_intent` (8th-consecutive, 8-for-8 across project keep-intent evals), CEO intent KEEP. **NEW REPRODUCIBLE PROJECT BEST composite_nRMSE 0.022161** on `experiment/14-fno_mf_stack-capacity-and-recipe-hash @ 0b6e6eb` (−20.08% vs prior banked best 0.027729 from cycle-008 H1; −27.12% vs cycle-008 entry baseline 0.030408). **PARALLEL-BENCH BAR DETHRONED FOR THE FIRST TIME IN 9 CYCLES** — composite 0.022161 < bar 0.027429 by 19.2% (gap closed 276.8% — i.e. blew past the bar by 2.77× the prior remaining gap). H1 capacity bump on `fno_mf_stack` delivered massive Poisson improvement (0.05961 → 0.03812, −36%) PLUS unexpected huge family-internal Heat gain (0.09995 → 0.03827, −62%). Per-cell post: `ifc_heat` best `fno_coregionalization` 0.012884 (marginal cache-rerun improvement from 0.012898); `ifc_poisson` best NOW `fno_mf_stack` 0.038120 (was 0.05961). `fno_mf_stack` non-best on heat (4th) but huge family-internal gain. `fno_mf_stack` owns Poisson by wide margin (next-best `fno_coreg_residual` 0.07200, ~1.89× away). H2 `recipe_hash` portable utility WORKED CORRECTLY — all 3 FNO families reported `cache_status=miss` and retrained from scratch under new SMOKE_DEFAULTS hash (`fno_mf_stack` recipe `acdb1c11caa7` invalidated cycle-008 cache by design). Poisson kill-switch (0.0594 threshold) NOT TRIPPED (0.0381 vs 0.0594, 36% headroom); wall kill-switch (1500s) NOT TRIPPED (414s, 72% headroom). Project genuine-REVERT count UNCHANGED at 5; `revert_bookkeeping_keep_intent` streak now **8** (H1+H2 added); **5th-consecutive `ceo:keep` intent across the streak** (cycle-005 H2, cycle-007 H1, cycle-008 H1, cycle-009 H1+H2 — last cycle CEO judgment confirmed KEEP despite precheck-formal-revert). Precheck infra bugs (now 8 consecutive cycles of operator-backlog non-fixes): 7th-consecutive leakage substring-collision FP (token `"17"` from diff hunk header `@@ -176,9 +178,10 @@`); 5th-consecutive scope/fixed_surfaces empty-detail FP (short-SHA-vs-long-SHA string equality sub-class); 11th polarity (lower-is-better metric) FP; **NEW this cycle: `factory guard --baseline <short-SHA>` short-vs-long-SHA string-equality FP** in rooting check (Reviewer manually verified `git merge-base HEAD 18d83a6` returns the full 40-char SHA `18d83a6190d342e0156a2c2547dcf2b2b998d782` which IS the baseline; branch is correctly rooted). META-FIX FULLY CLEARED: cycle-003 backlog `recipe_hash` portability ask is now SHIPPED across the entire FNO family — H2 promoted the inline pattern (delivered cycle-008 H3 on `fno_coreg_residual` only) to a shared `models/_common/recipe_hash.py` utility consumed by 3 live FNO families (`fno_mf_stack`, `fno_coreg_residual`, `fno_coregionalization`); `transolver_residual` already had inline canonical pattern; `transolver_attention_fusion` already had it. Cycle-010 entry baseline = `experiment/14-fno_mf_stack-capacity-and-recipe-hash @ 0b6e6eb @ composite 0.022161` (first project composite under both the parallel-bench bar AND the paper geomean on Heat).
metadata:
  type: experiment
tags:
  - factory
  - experiment
  - factory_mffp
  - cycle-009
  - h1
  - h2
  - bundle
  - final
  - fno_mf_stack
  - capacity-bump-poisson
  - recipe-hash-portable-utility
  - meta-fix-cycle-003-CLEARED
  - revert-bookkeeping-keep-intent
  - revert-bookkeeping-keep-intent-8th-consecutive
  - ceo-keep-5th-consecutive
  - new-reproducible-project-best
  - parallel-bench-bar-dethroned
  - poisson-side-attack-success
  - guard-short-vs-long-sha-equality-fp-NEW
  - leakage-substring-collision-fp-7th
  - empty-detail-scope-fixed-surfaces-fp-5th
project: factory_mffp
experiment_id: "014"
cycle: cycle-009
hypothesis_id: H1+H2
phase: final
verdict: revert
verdict_class: revert_bookkeeping_keep_intent
verdict_class_consecutive_count: 8
ceo_intent: keep
ceo_intent_consecutive_streak: 5
ceo_intent_streak_members: ["cycle-005-H2", "cycle-007-H1", "cycle-008-H1", "cycle-009-H1+H2"]
formal_verdict: revert
evaluator_verdict: PASS_KEEP
evaluator_recommendation: KEEP
ceo_verdict_evaluator: PROCEED
hypothesis_validated: true
date: 2026-06-02
branch: experiment/14-fno_mf_stack-capacity-and-recipe-hash
branch_status: banked_as_cycle_010_entry_baseline
branch_preserved: true
parent_branch: experiment/11-fno_coregionalization-paper-capacity
parent_commit: 18d83a6
parent_commit_source: "cycle-008 H1 banked best (paper-config capacity bump on fno_coregionalization)"
commit: 0b6e6eb
commit_message: "feat(fno_mf_stack): capacity bump + recipe_hash portable utility (cycle-009 H1+H2)"
files_changed: 5
loc_delta: "+45/-8"
mutable_surfaces_only: true
model_py_edited: false
data_py_edited: false
fixed_surface_edited: false
new_family_directory: false
loss_weights_unchanged: true
loss_weights_explicit_check: "poisson_hf_weight=2.0, poisson_lf_weight=0.25 NOT touched in models/fno_mf_stack/smoke_eval.py"
nk1_pure_m_conditioning_violation: false
nk2_frozen_lf_curriculum_violation: false
nk3_loss_weight_tuning_violation: false
score_metric: composite_nRMSE
score_before_banked_best: 0.027728854219631654
score_before_baseline: 0.030407732506238343
score_after: 0.022161472746117312
score_delta_vs_banked_best: -0.005567381473514342
score_delta_pct_vs_banked_best: -20.077935530321014
score_delta_vs_baseline: -0.008246259760121031
score_delta_pct_vs_baseline: -27.11895652998545
score_after_under_parallel_bench_bar: true
parallel_bench_bar: 0.027429
score_after_minus_bar_abs: -0.005268
score_after_pct_under_bar: 19.2
bar_gap_closed_pct: 276.8
bar_dethroned_first_time_in_cycles: 9
new_reproducible_project_best: true
ifc_heat_best_after_family: fno_coregionalization
ifc_heat_best_after_value: 0.012883724279424122
ifc_heat_best_before_value: 0.012898
ifc_heat_best_delta_pct: -0.11
ifc_heat_best_note: "marginal cache-rerun improvement; family-leader unchanged"
ifc_poisson_best_after_family: fno_mf_stack
ifc_poisson_best_after_value: 0.038120256505431285
ifc_poisson_best_before_value: 0.05961
ifc_poisson_best_delta_pct: -36.0
ifc_poisson_best_leadership_flip_this_cycle: false
ifc_poisson_best_leadership_margin_over_rank_2_x: 1.89
ifc_poisson_rank_2_family: fno_coreg_residual
ifc_poisson_rank_2_value: 0.07200016424130416
ifc_poisson_rank_2_before: 0.07419
ifc_poisson_rank_2_delta_pct: -3.0
fno_mf_stack_ifc_heat_before: 0.09995
fno_mf_stack_ifc_heat_after: 0.038268899048086086
fno_mf_stack_ifc_heat_delta_pct: -62.0
fno_mf_stack_ifc_heat_rank_after: 4
fno_mf_stack_ifc_heat_leader_after: fno_coregionalization
fno_mf_stack_ifc_heat_huge_family_internal_gain_non_best: true
fno_mf_stack_ifc_poisson_before: 0.05961
fno_mf_stack_ifc_poisson_after: 0.038120256505431285
fno_mf_stack_ifc_poisson_delta_pct: -36.0
fno_mf_stack_ifc_poisson_rank_after: 1
fno_mf_stack_owns_poisson_widely: true
fno_mf_stack_recipe_hash_after: acdb1c11caa7
fno_mf_stack_cache_status_heat: miss
fno_mf_stack_cache_status_poisson: miss
fno_mf_stack_cache_correctly_invalidated_by_design: true
fno_coreg_residual_recipe_hash_after: 1cc35377b46d
fno_coregionalization_recipe_hash_after: 5011def485a6
poisson_kill_switch_threshold: 0.0594
poisson_kill_switch_value: 0.038120256505431285
poisson_kill_switch_tripped: false
poisson_kill_switch_headroom_pct: 36
wall_kill_switch_threshold_seconds: 1500
wall_kill_switch_value_seconds: 414
wall_kill_switch_tripped: false
wall_kill_switch_headroom_pct: 72
cycle_eval_total_wall_seconds: 414
paper_bar_ifc_heat: 0.074
paper_bar_ifc_poisson: 0.036
paper_bar_ifc_heat_ratio_now: 0.17
paper_bar_ifc_heat_under_pct: 83
paper_bar_ifc_poisson_ratio_now: 1.06
paper_bar_ifc_poisson_under_paper_first_time: false
project_genuine_revert_count_after_h1h2: 5
project_genuine_revert_count_unchanged: true
project_revert_bookkeeping_keep_intent_streak_after_h1h2: 8
project_ceo_keep_intent_consecutive_streak: 5
hygiene_gate_r5a: PASS
monotonic_gate_r5b: PASS
monotonic_gate_r5b_rationale: "composite −20.08% vs banked best (0.027729 → 0.022161); R5b SATISFIED"
precheck_gate_r5c_score_direction_polarity_fired: true
precheck_gate_r5c_score_direction_polarity_count_total: 11
precheck_gate_r5c_score_direction_polarity_note: "−20.08% improvement reported as +20.08% regression — usual polarity (lower-is-better metric not honored)"
precheck_gate_r5c_scope_empty_detail_fired: true
precheck_gate_r5c_scope_empty_detail_count_total: 5
precheck_gate_r5c_fixed_surfaces_empty_detail_fired: true
precheck_gate_r5c_fixed_surfaces_empty_detail_count_total: 5
precheck_gate_r5c_leakage_substring_collision_fired: true
precheck_gate_r5c_leakage_substring_collision_consecutive_count: 7
precheck_gate_r5c_leakage_substring_collision_token: "17"
precheck_gate_r5c_leakage_substring_collision_root_cause: "diff hunk header @@ -176,9 +178,10 @@ collided with project-doc occurrences of '17' in factory.md / README.md (fixed_surfaces) in unrelated context"
precheck_gate_r5c_guard_short_vs_long_sha_equality_fp_NEW_this_cycle: true
precheck_gate_r5c_guard_short_vs_long_sha_equality_root_cause: "factory guard --baseline <short-SHA> performs string equality between caller-supplied 7-char baseline (18d83a6) and git merge-base output (full 40-char 18d83a6190d342e0156a2c2547dcf2b2b998d782); string ≠ but commits are identical. Caller manually verified `git merge-base HEAD 18d83a6` returns full SHA which IS the baseline."
precheck_gate_r5c_guard_short_vs_long_sha_equality_distinct_from_leakage_fp: true
precheck_gate_r5c_load_bearing_for_decision: false
precheck_gate_r5c_decision_grounded_in: "R5b monotonic check (composite −20.08% vs banked best; independent of precheck)"
keep_revert_gate_r5d: KEEP_INTENT_via_bookkeeping_revert
cycle_003_backlog_meta_fix_status: FULLY_CLEARED
cycle_003_backlog_meta_fix_clearance_scope: "3 live FNO families now consume models/_common/recipe_hash.py (fno_mf_stack, fno_coreg_residual, fno_coregionalization); transolver_residual already had canonical inline pattern; transolver_attention_fusion already had it. Project-wide stage-resume contamination pathway CLOSED for all FNO + Transolver families."
cycle_003_backlog_meta_fix_clearance_evidence: "all 3 FNO families reported `cache_status=miss` and retrained from scratch under new SMOKE_DEFAULTS hashes; fno_mf_stack new hash acdb1c11caa7 correctly invalidated any stale cycle-008 cache; fno_coreg_residual + fno_coregionalization stable hashes warm-resumed within-cycle correctly."
cycle_009_entry_baseline_outgoing: "experiment/11-fno_coregionalization-paper-capacity @ 18d83a6 @ composite 0.027729"
cycle_010_entry_baseline_incoming: "experiment/14-fno_mf_stack-capacity-and-recipe-hash @ 0b6e6eb @ composite 0.022161"
cycle_010_entry_baseline_under_parallel_bench_bar: true
cycle_010_entry_baseline_under_paper_heat: true
cycle_010_entry_baseline_under_paper_poisson: false
operator_backlog_items_unchanged_at_cycle_009_close: ["score_direction polarity", "scope/fixed_surfaces empty-detail", "leakage substring-collision"]
operator_backlog_items_added_at_cycle_009_close: ["factory guard --baseline short-vs-long-SHA string-equality FP"]
operator_backlog_items_cleared_at_cycle_009_close: ["recipe_hash portable utility for FNO family (cycle-003 backlog item)"]
source: factory-archivist
---

# Experiment #014: Cycle-009 H1+H2 — `fno_mf_stack` capacity bump + `recipe_hash` portable utility

## Hypothesis

**H1** (Poisson dominant-lever attack — mirrors cycle-008 H1 playbook): capacity bump on `fno_mf_stack` SMOKE_DEFAULTS (`hidden 32→64`, `agg_hidden 32→64`, `n_blocks 3→4`, `modes_per_level (4,8,12,12)→(4,8,16,20)`) drives `fno_mf_stack × ifc_poisson` below the parallel-bench bar (0.05871) without touching loss weights (NK3 carve-out: `poisson_hf_weight=2.0`, `poisson_lf_weight=0.25` UNCHANGED). Targets the cycle-009 dominant-lever (~69% of remaining composite gap is Poisson-side; capacity-axis exhausted on `fno_coregionalization`).

**H2** (cycle-003 backlog meta-fix portability): promote the H3 inline `recipe_hash` pattern (cycle-008 H3 on `fno_coreg_residual`) to a shared `models/_common/recipe_hash.py` utility (12 LOC, `Mapping[str, Any]` typed, `default=str`, `sha256[:12]` truncation) and apply via canonical 4-patch-site refactor (import → compute → resume guard chained with family-specific preconditions → checkpoint save dict key) to all 3 mutable-surface FNO families.

## Result

**Formal verdict: `revert_bookkeeping_keep_intent` (8th-consecutive, 8-for-8 across project keep-intent evals).**

**CEO intent: KEEP** — 5th-consecutive `ceo:keep` across the streak (cycle-005 H2, cycle-007 H1, cycle-008 H1, cycle-009 H1+H2). Banked as cycle-010 entry baseline.

**Hypothesis: VALIDATED.** Both H1 and H2 delivered as specified.

## Quantitative outcome

| Metric | Value | vs target | Status |
|---|---:|---|---|
| **Composite nRMSE (H1+H2 branch)** | **0.022161** | < 0.027729 (banked best) | **NEW REPRODUCIBLE PROJECT BEST −20.08%** |
| Composite vs cycle-008 entry baseline (1249f2d) | −27.12% (0.030408 → 0.022161) | improve | massive improvement |
| Composite vs parallel-bench bar (0.027429) | **−19.2% under bar** | dethrone | **BAR DETHRONED FIRST TIME IN 9 CYCLES** (gap closed 276.8%) |
| `fno_mf_stack × ifc_poisson` | **0.038120** | < 0.0594 kill-switch (Builder predicted 0.05–0.06) | **NEW POISSON LEADER**; −36% vs prior `fno_mf_stack` 0.05961; 36% headroom over kill-switch |
| `fno_mf_stack × ifc_heat` | 0.038269 | (no target) | **−62% family-internal gain** (was 0.09995); non-best (4th, behind `fno_coregionalization` 0.012884) |
| `ifc_heat` best (post) | 0.012884 `fno_coregionalization` | hold | marginal cache-rerun improvement from 0.012898 (−0.11%); family-leader unchanged |
| `ifc_poisson` best (post) | **0.038120 `fno_mf_stack`** | minimize | `fno_mf_stack` retains Poisson cell at **1.89× margin** over rank-2 `fno_coreg_residual` @ 0.07200 |
| Poisson kill-switch | NOT TRIPPED | 0.0381 < 0.0594 threshold | 36% headroom |
| Wall kill-switch | NOT TRIPPED | 414 s < 1500 s threshold | 72% headroom |
| Recipe-hash cache-invalidation (`fno_mf_stack`) | `cache=miss`, fresh retrain | invalidate cycle-008 cache | **WORKS** — new hash `acdb1c11caa7` ≠ stale; H2 meta-fix verified live |
| Recipe-hash stable (`fno_coreg_residual`, `fno_coregionalization`) | hash unchanged, within-cycle correct | warm-resume continuity | hashes `1cc35377b46d`, `5011def485a6` stable; cache-status `miss` due to other-family rebuild ripples (marginal additional improvements) |

## Why this is the load-bearing project event

This is the **first project composite under both the parallel-bench bar AND the paper geomean on Heat** (Heat geomean 0.012884 is 0.17× paper's 0.074; Poisson 0.038120 is 1.06× paper's 0.036, still slightly above paper). The cycle-008 H1 trajectory (89.93% bar gap closed via Heat-side capacity-axis) plus the cycle-009 H1 Poisson-side capacity-axis collapsed the remaining +1.09% bar gap and overshot by 19.2% under the bar. The capacity-axis playbook (paper-config bump on the dominant-lever family) generalizes to the Poisson family — first cross-family transfer of the H1 lever in project history.

## H2 meta-fix delivery — cycle-003 backlog FULLY CLEARED

The cycle-003 H1 stage-resume contamination pathway is now **closed project-wide for the entire FNO family**:

- `fno_mf_stack`, `fno_coreg_residual`, `fno_coregionalization` — now consume `models/_common/recipe_hash.py` (3 live FNO families).
- `transolver_residual` — already had canonical inline pattern (cherry-pick source for H2 helper).
- `transolver_attention_fusion` — already had it.

Live verification this cycle: `fno_mf_stack` new hash `acdb1c11caa7` correctly invalidated any stale cycle-008 cache (both `ifc_heat` and `ifc_poisson` reported `cache_status=miss` → forced fresh training under new H1 capacity — exactly the deliberate cache-safety semantic). `fno_coreg_residual` (`1cc35377b46d`) and `fno_coregionalization` (`5011def485a6`) stable hashes confirm SMOKE_DEFAULTS were not perturbed by the H2 refactor — the helper is correctness-preserving for unchanged-recipe families.

**Outstanding cycle-003 backlog beyond this scope:** none for the FNO family. The cycle-003 H1 33s-stale-resume-vs-549s-clean-rerun contamination failure mode is operationally closed for cycle-010+ research-mode experiments on all FNO families.

## NOT `revert_bookkeeping_keep_intent` for the usual reason — but it IS bookkeeping this cycle

The 7 prior consecutive `revert_bookkeeping_keep_intent` cases shared a specific pattern: composite **genuinely improved**, precheck false-positives tripped formal verdict, CEO override → effectively KEEP. **This case fits the pattern but at a record-shattering improvement scale:**

- Composite improved by −20.08% vs banked best — the **largest single-cycle composite improvement in project history**.
- All 4 documented precheck bookkeeping bugs fired:
  - **`score_direction` polarity (11th instance, usual polarity):** reported −20.08% improvement as +20.08% regression (lower-is-better metric still not honored — 9 cycles of operator backlog still ungrasped).
  - **`scope` empty-detail (5th instance):** false positive with `"detail": "Guard violations: "` (empty) — `factory guard --check-scope` independently reports clean.
  - **`fixed_surfaces` empty-detail (5th instance):** same pattern; short-SHA-vs-long-SHA string-equality sub-class.
  - **Leakage substring-collision (7th-consecutive builder phase):** token `"17"` matched diff hunk header `@@ -176,9 +178,10 @@` against project docs (`factory.md`/`README.md`) containing "17" in unrelated context. Standing operator override per cycle-008 close-out practice.
- **NEW this cycle: `factory guard --baseline <short-SHA>` short-vs-long-SHA string-equality FP** — distinct from the leakage substring FP. Caller passes 7-char `18d83a6`; `git merge-base HEAD 18d83a6` returns the full 40-char `18d83a6190d342e0156a2c2547dcf2b2b998d782`. Guard does string `==` between the short caller-arg and the full git output → mismatch reported even though both refer to the same commit. Reviewer manually verified `git rev-parse 18d83a6` matches the merge-base output prefix; branch IS correctly rooted at the cycle-008 H1 banked-best commit. **2nd known guard false positive class** (1st is the leakage substring FP); cycle-009 close-out operator backlog flag.

**Bookkeeping is non-load-bearing for the decision:** CEO KEEP intent grounded in R5b monotonic check (composite −20.08% < 0.027729; independent of precheck) AND R5c universal kill-switches both CLEAR (Poisson 36% headroom, wall 72% headroom). R5b PASS — the streak ratchets from 7 → **8**.

## What Changed (H1+H2 single-commit bundle on `experiment/14 @ 0b6e6eb`)

5 files / +45/-8 LOC. Single commit. Parent: cycle-008 H1 banked best (`experiment/11 @ 18d83a6`).

**H1 — `fno_mf_stack` capacity bump (4 SMOKE_DEFAULTS edits):**

| Key | Before | After |
|---|---|---|
| `hidden` | 32 | 64 |
| `agg_hidden` | 32 | 64 |
| `n_blocks` | 3 | 4 |
| `modes_per_level` | (4,8,12,12) | (4,8,16,20) |

Loss weights (`poisson_hf_weight=2.0`, `poisson_lf_weight=0.25`) **explicitly UNCHANGED** — verified file:line by Builder + CEO. NK3 carve-out preserved; MFRNP-style loss-weight tuning ban on coregionalization-family-adjacent recipes (3/3 REVERT history) sidestepped.

**H2 — `recipe_hash` portable utility (4-patch-site refactor on 3 FNO families):**

- `models/_common/__init__.py` (NEW empty) — package marker
- `models/_common/recipe_hash.py` (NEW +12) — `recipe_hash(defaults: Mapping[str, Any]) -> str` returning `sha256(json.dumps(dict(defaults), sort_keys=True, default=str).encode()).hexdigest()[:12]`
- `models/fno_mf_stack/smoke_eval.py` (+19/-5) — H1 SMOKE_DEFAULTS + H2 4-patch-site refactor (A import, B compute, C resume guard chained `ok_recipe AND ok_epoch AND ok_cond`, D save-dict key)
- `models/fno_coreg_residual/smoke_eval.py` (+12/-2) — H2 4-patch-site refactor only
- `models/fno_coregionalization/smoke_eval.py` (+10/-1) — H2 4-patch-site refactor only (resume guard preserves family-specific `sd.get("grid") == list(grid)` precondition)

## Per-cell results (full)

| Cell | Before | After | Δ |
|---|---:|---:|---:|
| `fno_coregionalization × ifc_heat` (leader) | 0.012898 | **0.012884** | −0.11% |
| `fno_coreg_residual × ifc_heat` | 0.026277 | 0.026273 | flat |
| `mf_fno_transfer_bar × ifc_heat` | 0.033175 | 0.033175 | flat (cache) |
| `fno_mf_stack × ifc_heat` | 0.09995 | **0.038269** | **−62%** (4th, non-best) |
| `fno_mf_stack × ifc_poisson` (NEW leader) | 0.05961 | **0.038120** | **−36%** |
| `fno_coreg_residual × ifc_poisson` (rank 2) | 0.07419 | 0.07200 | −3.0% |
| `mf_fno_transfer_bar × ifc_poisson` | 0.08333 | 0.08333 | flat (cache) |

## Cycle-008 → cycle-009 streak counters

| Counter | Before cycle-009 H1+H2 | After cycle-009 H1+H2 |
|---|---:|---:|
| Project genuine-REVERT count | 5 | **5 (UNCHANGED)** |
| `revert_bookkeeping_keep_intent` consecutive streak | 7 | **8** |
| `ceo:keep` intent consecutive streak | 4 | **5** |
| Leakage substring-collision FP consecutive (builder phase) | 6 | **7** |
| `score_direction` polarity FP count (any polarity) | 10 | **11** |
| `scope`/`fixed_surfaces` empty-detail FP count | 4 | **5** |
| Guard short-vs-long SHA equality FP class | 0 | **1 (NEW this cycle)** |
| Cycle-003 backlog `recipe_hash` portability — FNO family | partially closed (1/3, c008 H3 inline only) | **FULLY CLEARED (3/3 + 2 Transolver already had it)** |

## Operator backlog status at cycle-009 close

**Cleared:**
- `recipe_hash` portable utility for FNO family (cycle-003 backlog item) — fully clear on `fno_mf_stack`, `fno_coreg_residual`, `fno_coregionalization`; both Transolver families already had the canonical inline pattern.

**Carried forward (8th consecutive cycle of operator-backlog non-fix):**
- `score_direction` polarity for lower-is-better metrics (11 total firings, 9 cycles).
- `scope` / `fixed_surfaces` empty-detail (5 total firings, includes short-SHA-vs-long-SHA sub-class).
- Leakage substring-collision (7-consecutive builder-phase override).

**NEW this cycle:**
- `factory guard --baseline <short-SHA>` performs string equality between the 7-char caller arg and the full 40-char `git merge-base HEAD <ref>` output → mismatch even when commits are identical. Distinct from leakage substring FP; 2nd known guard FP class. Cycle-010 close-out reminder.

## Cycle-010 entry state

- **Composite:** **0.022161** (composite_nRMSE) — first composite under both parallel-bench bar (0.027429) and paper Heat geomean (0.074); Poisson 0.038120 still 1.06× over paper Poisson 0.036.
- **Branch:** `experiment/14-fno_mf_stack-capacity-and-recipe-hash`
- **Commit:** `0b6e6eb` (preserved on disk)
- **Parent:** `experiment/11-fno_coregionalization-paper-capacity @ 18d83a6` (cycle-008 H1 banked best — also preserved)
- **Per-dataset state:** `ifc_heat` 0.012884 via `fno_coregionalization` (5.74× margin over paper); `ifc_poisson` 0.038120 via `fno_mf_stack` (NEW leader, 1.89× margin over `fno_coreg_residual` 0.07200; 1.06× over paper).
- **Bar status:** dethroned by 19.2% (composite 0.022161 < bar 0.027429). Cycle-010 monotonic-improvement baseline = **0.022161**.
- **Preserved reference branches:** `experiment/14 @ 0b6e6eb` (cycle-010 entry), `experiment/11 @ 18d83a6` (cycle-008 H1 banked best — fallback reference), `experiment/13 @ 420a51c` (cycle-008 H3 recipe_hash inline pattern source), `experiment/12 @ 540e684` (FiLM scaffolding — still available for γ(m, LF_features) revisit), branches from cycle-002 (`experiment/4 @ 0c46f43`) and cycle-007 (`experiment/9 @ 1249f2d`).

## Links

- Project: factory_mffp
- Branch: `experiment/14-fno_mf_stack-capacity-and-recipe-hash @ 0b6e6eb` (banked as cycle-010 entry)
- Parent baseline: `experiment/11 @ 18d83a6` (cycle-008 H1 banked best, composite 0.027729)
- Build-phase predecessor: [[cycle-009-exp-14-build]]
- Cycle entry strategy: [[cycle-009-strategy]]
- Failure analysis: [[failure-analysis-cycle-009]]
- Capacity-axis playbook precedent (Heat-side): [[cycle-008-exp-11-build]] (cycle-008 H1 paper-config capacity bump on `fno_coregionalization`)
- Recipe_hash inline pattern source (cycle-008 H3): [[cycle-008-exp-13-final]]
- Patterns updated:
  - [[patterns]] — "Capacity-axis playbook transfers cross-family: paper-config SMOKE_DEFAULTS bump on the dominant-lever family closes a dominant gap" (NEW cross-cycle pattern, this exp)
  - [[patterns]] — "`revert_bookkeeping_keep_intent` 8th-consecutive at record-improvement scale (−20.08% composite); precheck bookkeeping ungrasped 9 cycles" (REINFORCEMENT)
  - [[patterns]] — "`factory guard --baseline <short-SHA>` short-vs-long-SHA string-equality false positive — 2nd known guard FP class distinct from leakage substring FP" (NEW this cycle)
  - [[patterns]] — "Cycle-003 backlog `recipe_hash` portability — fully cleared for FNO family by H2 portable utility (`models/_common/recipe_hash.py`); cache-invalidation semantic verified live" (CLEARANCE)
- Next phase: cycle-010 Failure Analyst on `experiment/14 @ 0b6e6eb`; baseline composite = 0.022161.
