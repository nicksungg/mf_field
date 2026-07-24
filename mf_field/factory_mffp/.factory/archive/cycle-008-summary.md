---
name: cycle-008-summary
description: Cycle-008 close-out for factory_mffp. Three hypotheses run on the cycle-007 H1 reproducible frontier — H1 (paper-config capacity bump on `fno_coregionalization`) KEEP intent / revert bookkeeping; H2 (NEW family `fno_coreg_conditioned` FiLM-via-LayerNorm on HF-only FNO) GENUINE REVERT (architecture-falsified on Poisson); H3 (three-stage frozen-LF curriculum on `fno_coreg_residual` + recipe_hash meta-fix) GENUINE REVERT (architecture-incompatible with co-evolved residual ladder). Net cycle effect — banked reproducible best moved 0.030408 → 0.027729 (−8.81%) on `experiment/11 @ 18d83a6`; **NEW project best**, **89.93% of parallel-bench bar gap closed by capacity-axis alone**, both H1 hard component targets MET (composite ≤ 0.028 AND heat ≤ 0.013). Cycle-008 net = **1 KEEP intent + 2 consecutive GENUINE REVERTs** — first time two genuine REVERTs appear in a single cycle (c006/c007 each had 1). Project genuine-REVERT count now 5 (c003 H1, c006 H1, c007 H2, c008 H2, c008 H3); `revert_bookkeeping_keep_intent` streak unchanged at 7 (H1 added). Two NEW cross-cycle architectural patterns surfaced as cycle-009 inputs — (a) FiLM-via-LayerNorm on HF-only FNO cannot synthesize LF→HF correlation pathway (pure m-conditioning insufficient for Poisson-class datasets where LF samples carry significant complementary information); (b) three-stage frozen-LF-HF-residual curricula are INCOMPATIBLE with co-evolved residual ladder designs (`fno_coreg_residual`, `fno_coregionalization`) — Stage-2 LF freeze forces HF residual to correct against OOD frozen LF state — but MAY be appropriate for families where LF and HF are independent by design (`mf_fno_transfer_bar`, `fno_mf_stack`). One NEW kill-switch design rule — multi-stage curriculum kill-switches MUST include an absolute Stage-k-vs-baseline check, not only an inter-stage ratio check. One META-FIX delivered — `recipe_hash` checkpoint guard pattern (cycle-003 backlog item) WORKS correctly; cycle-009 action = cherry-pick into portable utility (`models/_common/recipe_hash.py`) and apply to all family `smoke_eval.py` files. Precheck infra bugs (`score_direction` polarity 10-of-10 including H2's symmetric-flip silencing of a regression, `scope`/`fixed_surfaces` empty-detail 4-of-4, leakage substring collision 6-of-6) remain operator-flagged backlog — 6th consecutive cycle requiring overrides — precheck overhaul still out-of-cycle scope. Cycle-009 entry baseline UNCHANGED by H2/H3 = `experiment/11-fno_coregionalization-paper-capacity @ 18d83a6 @ composite 0.027729`; bar gap remaining +0.000300 (+1.09% above 0.027429 parallel-bench bar). All three cycle-008 branches preserved on disk (H1 banked best, H2 FiLM scaffolding for potential revisit, H3 recipe_hash pattern reuse).
metadata:
  type: project
tags:
  - factory
  - cycle-summary
  - factory_mffp
  - cycle-008
  - close-out
  - revert-bookkeeping-keep-intent
  - genuine-revert
  - architecture-falsified-poisson
  - architecture-incompatible-three-stage-on-residual-ladder
  - recipe-hash-meta-fix
  - new-reproducible-project-best
project: factory_mffp
cycle_id: "008"
date: 2026-06-02
source: factory-archivist
status: closed
experiments_run: 3
ceo_keep_count: 1
ceo_revert_count: 2
factory_bookkeeping_keep_count: 0
factory_bookkeeping_revert_count: 3
precheck_polarity_bug_total_after_cycle_008: 10
precheck_polarity_bug_opposite_polarity_count: 1
precheck_empty_detail_scope_fixed_surfaces_after_cycle_008: 4
leakage_substring_collision_consecutive_builder_phase_after_cycle_008: 6
revert_bookkeeping_keep_intent_streak_after_cycle_008: 7
genuine_revert_count_after_cycle_008: 5
genuine_revert_first_time_two_in_one_cycle: true
prior_genuine_reverts: "c003 H1 (+91.7%), c006 H1 (+4.3% aggregate), c007 H2 (+12.36% composite / +32.70% heat invariance falsified)"
new_genuine_reverts_cycle_008: "c008 H2 (+9.66% vs banked best, FiLM architecture-falsified on Poisson), c008 H3 (+9.66% vs banked best, three-stage incompatible with residual ladder, universal heat kill-switch tripped 26×)"
new_reproducible_project_best: true
project_best_composite_reproducible: 0.027729
project_best_branch: experiment/11-fno_coregionalization-paper-capacity
project_best_commit: 18d83a665f86fbb1b54a9d3b4fa8a78d3e6d11d7
prior_reproducible_project_best_composite: 0.030408
prior_reproducible_project_best_source: cycle-007 H1
aspirational_unreproducible_composite: 0.029357
aspirational_unreproducible_source: "cycle-005 H2 (reference only, NOT reproducible)"
cycle_008_entry_composite_baseline: 0.030408
cycle_008_exit_composite: 0.027729
cycle_delta_pct: -8.81
parallel_bench_bar_target_composite: 0.027429
parallel_bench_bar_short_by_abs: 0.000300
parallel_bench_bar_short_by_pct: 1.09
parallel_bench_bar_gap_closed_pct: 89.93
h1_id: "011"
h1_hypothesis: "fno_coregionalization paper-config capacity bump"
h1_branch: experiment/11-fno_coregionalization-paper-capacity
h1_parent_branch: experiment/9-fno_coregionalization-constructor-fix
h1_parent_commit: 1249f2d
h1_commit: 18d83a6
h1_files_changed: 1
h1_loc_delta: "+10/-4"
h1_target_file: models/fno_coregionalization/smoke_eval.py
h1_score_before: 0.030407732506238343
h1_score_after: 0.027728854219631654
h1_score_delta_pct: -8.81
h1_verdict: revert_bookkeeping_keep_intent
h1_ceo_intent: keep
h1_streak_revert_bookkeeping_keep_intent_after: 7
h1_ifc_heat_best_before: 0.01551
h1_ifc_heat_best_after: 0.012898497199156745
h1_ifc_heat_best_family_before: fno_coregionalization
h1_ifc_heat_best_family_after: fno_coregionalization
h1_ifc_heat_best_delta_pct: -16.84
h1_fno_coregionalization_owns_heat: true
h1_fno_coregionalization_heat_margin_over_second_place_multiple: 2.04
h1_kill_switch_heat_tripped: false
h1_kill_switch_heat_headroom_pct: 33.5
h1_target_met_composite_le_0_028: true
h1_target_met_heat_le_0_013: true
h1_target_met_composite_le_0_027429: false
h2_id: "012"
h2_hypothesis: "NEW family fno_coreg_conditioned — FiLM-via-LayerNorm on single HF FNO"
h2_branch: experiment/12-fno_coreg_conditioned-film
h2_parent_branch: cycle-008-entry-baseline
h2_parent_commit: 1249f2d
h2_commit: 540e684
h2_files_changed: 4
h2_files_changed_all_new: true
h2_loc_delta: "+828/-0"
h2_new_family_dir: models/fno_coreg_conditioned/
h2_score_before: 0.027729
h2_score_after: 0.030408
h2_score_delta_pct: 9.66
h2_score_delta_direction: regression
h2_verdict: revert
h2_verdict_type: substantive
h2_verdict_class: architecture_falsified_on_poisson
h2_verdict_class_explicit_not: revert_bookkeeping_keep_intent
h2_ceo_intent: revert
h2_fno_coreg_conditioned_ifc_heat_nRMSE: 0.017102
h2_fno_coreg_conditioned_ifc_heat_rank: 2
h2_fno_coreg_conditioned_ifc_heat_gap_to_leader_pct: 10.3
h2_fno_coreg_conditioned_ifc_poisson_nRMSE: 0.749915
h2_fno_coreg_conditioned_ifc_poisson_rank: 5
h2_fno_coreg_conditioned_ifc_poisson_multiple_over_leader: 12.6
h2_builder_predicted_poisson_min: 0.05
h2_builder_predicted_poisson_max: 0.15
h2_builder_prediction_in_range: false
h2_composite_contribution_from_new_family: 0
h2_both_kill_switches_clear: true
h2_failure_mode: silent_under_performance_not_blow_up
h2_architectural_lesson: "FiLM-via-LayerNorm on HF-only FNO cannot synthesize LF→HF correlation pathway. m-conditioning via FiLM affines can re-scale per-fidelity representations but cannot CREATE LF→HF structure. Poisson dataset has strong LF→HF signal (fno_mf_stack 0.05961 and fno_coreg_residual 0.07419 both exploit LF input directly); H2's HF-only architecture discards LF channel by design."
h2_cycle_009_strategy_implication_a: "re-introduce LF→HF pathway (residual ladder)"
h2_cycle_009_strategy_implication_b: "condition on LF samples directly in FiLM affines (γ(m, LF_features) instead of γ(m, m²))"
h2_cycle_009_strategy_implication_negation: "pure m-conditioning is insufficient for Poisson-class datasets"
h3_id: "013"
h3_hypothesis: "three-stage frozen-LF curriculum on fno_coreg_residual + recipe_hash checkpoint guard"
h3_branch: experiment/13-fno_coreg_residual-three-stage
h3_parent_branch: cycle-008-entry-baseline
h3_parent_commit: 1249f2d
h3_commit: 420a51c
h3_files_changed: 1
h3_loc_delta: "+401/-73"
h3_target_file: models/fno_coreg_residual/smoke_eval.py
h3_model_py_byte_identical_to_baseline: true
h3_score_before: 0.027729
h3_score_after: 0.030408
h3_score_delta_pct: 9.66
h3_score_delta_direction: regression
h3_verdict: revert
h3_verdict_type: substantive
h3_verdict_class: architecture_incompatible_three_stage_on_residual_ladder
h3_verdict_class_explicit_not: revert_bookkeeping_keep_intent
h3_ceo_intent: revert
h3_fno_coreg_residual_ifc_heat_before_single_stage: 0.026277
h3_fno_coreg_residual_ifc_heat_after_three_stage: 0.509105074500434
h3_fno_coreg_residual_ifc_heat_delta_pct: 1837.4
h3_fno_coreg_residual_ifc_heat_delta_multiple: 19
h3_fno_coreg_residual_ifc_heat_val_test_gap_multiple: 12
h3_fno_coreg_residual_ifc_poisson_before_single_stage: 0.074192
h3_fno_coreg_residual_ifc_poisson_after_three_stage: 0.15936368490302597
h3_fno_coreg_residual_ifc_poisson_delta_pct: 114.8
h3_universal_heat_kill_switch_threshold: 0.0194
h3_universal_heat_kill_switch_tripped: true
h3_universal_heat_kill_switch_ratio_over_threshold: 26.24
h3_h3_specific_stage3_stage2_heat_ratio: 1.0
h3_h3_specific_stage3_stage2_heat_kill_switch_tripped: false
h3_kill_switch_design_flaw: true
h3_architectural_lesson: "Three-stage frozen-LF-HF-residual curricula are INCOMPATIBLE with co-evolved residual ladder designs (fno_coreg_residual, fno_coregionalization). Stage 2's requires_grad=False LF freeze forces HF residual to correct against an OOD frozen LF state from LF-only pretrain regime, producing garbage. Stage 3's unfreeze comes too late — HF residual already in poor local minimum. End-to-end joint training (cycle-005 H2 continuous-LR-schedule pattern) remains the correct recipe for co-evolved designs. Three-stage curricula MAY be appropriate for families with LF and HF networks INDEPENDENT BY DESIGN (mf_fno_transfer_bar, fno_mf_stack)."
h3_kill_switch_design_lesson: "Multi-stage curriculum kill-switches MUST include BOTH (a) absolute Stage_k vs prior single-stage baseline check (stage_k_final_hf_test_nrmse > 1.25 × prior_single_stage_test_nrmse → REVERT to baseline) AND (b) inter-stage ratio checks at each transition. Single inter-stage ratio kill-switches assume damage occurs in LATER stage only — fragile."
h3_meta_fix_recipe_hash_guard_delivered: true
h3_meta_fix_cycle_003_backlog_item_closed_for_this_family: fix_checkpoint_resume_contamination_via_recipe_hash_guard
h3_meta_fix_cycle_009_action: cherry_pick_into_models_common_recipe_hash_py_and_apply_to_all_families
h3_meta_fix_three_stage_curriculum_keep_worthy: false
new_patterns_added: ["film-via-layernorm-cannot-synthesize-lf-hf-correlation", "three-stage-frozen-lf-incompatible-with-co-evolved-residual-ladder", "multi-stage-kill-switch-needs-stage2-vs-baseline-absolute-check", "bookkeeping-overridable-revert-vs-genuine-architecture-falsified-revert"]
existing_patterns_reinforced: ["precheck-score-direction-polarity-bug (9→10 includes symmetric-flip silencing of regression)", "precheck-empty-detail-scope-fixed-surfaces (3→4)", "leakage-check-substring-collision-builder-phase (5→6)", "revert_bookkeeping_keep_intent universal verdict (6→7)", "cross-architecture-recipe-portability-not-guaranteed (2→3 via three-stage incompatibility)", "fresh-train-variance-swamps-invariance (1→ reinforced by H3 val/test 12× gap)"]
cycle_009_entry_composite: 0.027729
cycle_009_entry_branch: experiment/11-fno_coregionalization-paper-capacity
cycle_009_entry_commit: 18d83a6
cycle_009_entry_baseline_unchanged_by_h2: true
cycle_009_entry_baseline_unchanged_by_h3: true
cycle_009_bar_gap_remaining_abs: 0.000300
cycle_009_bar_gap_remaining_pct: 1.09
cycle_009_preserved_reference_branches: ["experiment/11 @ 18d83a6 (banked best)", "experiment/12 @ 540e684 (FiLM scaffolding, 828 LOC for potential revisit with γ(m, LF_features))", "experiment/13 @ 420a51c (recipe_hash pattern for cycle-009 portable utility cherry-pick)"]
cycle_009_strategic_priorities: ["cherry-pick recipe_hash pattern from H3 into models/_common/recipe_hash.py and apply to all family smoke_eval.py files", "any single-family Heat+Poisson candidate MUST re-introduce LF→HF pathway OR condition on LF samples in FiLM affines — pure m-conditioning rejected at R2", "any multi-stage curriculum proposal MUST include Stage-k-vs-baseline absolute kill-switch AND only target families with LF/HF independent by design (mf_fno_transfer_bar, fno_mf_stack) — do NOT propose three-stage on residual-ladder families", "close remaining +1.09% bar gap — capacity axis exhausted on fno_coregionalization, next lever must come from ifc_poisson side (fno_mf_stack 0.05961 reduction OR fno_coregionalization × ifc_poisson <0.05961 takeover)", "6th consecutive operator request — precheck overhaul out-of-cycle"]
operator_action_flagged_consecutive_count: 6
operator_action_target: "precheck overhaul (score_direction polarity, scope/fixed_surfaces empty-detail, leakage substring-collision)"
operator_action_status: out_of_cycle_scope
---

# Cycle 008 — factory_mffp — Close-out Summary

**Status:** **CLOSED 2026-06-02**.
**Cycle scope:** Three hypotheses on the cycle-007 H1 reproducible
frontier. H1 = paper-config capacity bump on the freshly-repaired
`fno_coregionalization` anisotropic-modes constructor (single-file,
`CAPACITY_PARETO` failure mode). H2 = NEW family
`fno_coreg_conditioned` (FiLM-via-LayerNorm on single HF FNO,
single-family Heat+Poisson candidate, `FAMILY_PDE_SPECIALIZATION_ASYMMETRY`
failure mode). H3 = three-stage frozen-LF curriculum on
`fno_coreg_residual` (single-file, `TRANSFER_SIGNAL_UNUSED` failure mode)
with a mandatory `recipe_hash` checkpoint guard delivering the
cycle-003 backlog meta-fix.
**Outcome:** 3 hypotheses run; H1 = `revert_bookkeeping_keep_intent`
(CEO KEEP — composite genuinely improved −8.81%, precheck infra bugs
trip the formal verdict); H2 = **genuine REVERT**
(architecture-falsified on Poisson — composite +9.66% above banked
best); H3 = **genuine REVERT** (architecture-incompatible with
co-evolved residual ladder — universal heat kill-switch tripped 26×).
**Net cycle effect (the engineering win):** the project's banked
reproducible best moved from **0.030408** (cycle-007 H1) to
**0.027729** on `experiment/11-fno_coregionalization-paper-capacity @ 18d83a6`,
**89.93% of the parallel-bench bar gap closed by capacity-axis alone**.
Both H1 hard component targets MET (composite ≤ 0.028 AND heat ≤ 0.013).

## TL;DR

- **New reproducible project best:** composite_nRMSE **0.030408 → 0.027729**
  (−8.81%) on `experiment/11-fno_coregionalization-paper-capacity @ 18d83a6`
  (cycle-008 H1). `fno_coregionalization × ifc_heat` 0.01551 → **0.012898**
  (−16.84%); this family is now **sole holder of the heat leaderboard at
  >2× margin** over second-place `fno_coreg_residual @ 0.026277`. Both
  H1 hard component targets met (composite ≤ 0.028 ✅ AND heat ≤ 0.013 ✅);
  bar dethrone (≤ 0.027429) missed by +0.000300 (+1.09%). See
  [[cycle-008-exp-11]] and [[cycle-008-exp-11-build]].
- **H1 verdict:** `revert_bookkeeping_keep_intent` (7th project-wide;
  5th consecutive in cycles 007–008). All 4 real safety checks PASS
  (`ground_truth_leakage`, `anti_pattern`, `smoke_test`, independent
  `scope`/`fixed_surfaces`); precheck `score_direction` polarity (9th
  instance) and empty-detail `scope`/`fixed_surfaces` (4th instance)
  flipped the formal verdict.
- **H2 verdict:** **genuine REVERT** (4th project-wide; 1st in
  cycle-008). NEW family `fno_coreg_conditioned` (FiLM-via-LayerNorm
  on single HF FNO, 4 NEW files / +828/−0 LOC at `models/fno_coreg_conditioned/`).
  Composite **+9.66% above banked best** 0.027729; `ifc_heat` near-miss
  at 2nd place (0.017102 vs leader 0.01551, +10.3%); `ifc_poisson`
  catastrophic at 5th place (0.749915, 12.6× over `fno_mf_stack`
  0.05961). Branch `experiment/12-fno_coreg_conditioned-film @ 540e684`
  preserved for reference. See [[cycle-008-exp-12-final]] and
  [[cycle-008-exp-12-build]].
- **H3 verdict:** **genuine REVERT** (5th project-wide; 2nd in
  cycle-008). Three-stage frozen-LF curriculum on `fno_coreg_residual`
  (single-file, +401/−73 LOC at `smoke_eval.py`; `model.py`
  byte-identical to baseline). Composite **+9.66% above banked best**;
  `fno_coreg_residual × ifc_heat` 0.026 → **0.509** (19× regression;
  universal heat kill-switch tripped **26×** over 0.0194 threshold);
  `fno_coreg_residual × ifc_poisson` 0.074 → 0.159 (+115% out of
  Builder's 0.05–0.06 range; 2.15× the paper-recipe baseline). H3-specific
  Stage3/Stage2 Heat ratio kill-switch ratio=1.00 (did NOT trip —
  damage occurred in Stages 1/2; design flaw). Branch
  `experiment/13-fno_coreg_residual-three-stage @ 420a51c` preserved
  for `recipe_hash` pattern reuse **only** (three-stage curriculum
  NOT reusable). See [[cycle-008-exp-13-final]] and [[cycle-008-exp-13-build]].
- **Cycle-008 net = 1 KEEP intent + 2 consecutive GENUINE REVERTs —
  first time two genuine REVERTs appear in a single cycle** (c006 and
  c007 each had 1). Project genuine-REVERT count now **5**
  (c003 H1, c006 H1, c007 H2, c008 H2, c008 H3);
  `revert_bookkeeping_keep_intent` streak unchanged at **7** (H1 added).
- **META-FIX delivered:** `recipe_hash` checkpoint guard pattern
  (cycle-003 backlog item) WORKED CORRECTLY in live testing — stale
  checkpoint rejection log line verified (`[resume] REJECTED stale
  checkpoint: recipe_hash '148a2641b07fe5da' != '0095c3ff614e17b8'`).
  cycle-009 action: cherry-pick into a portable utility
  (`models/_common/recipe_hash.py`) and apply to ALL family
  `smoke_eval.py` files. The three-stage gating logic is NOT reusable.

## Net cycle effect

| Reference point | Composite | Reproducible? |
|---|---:|---|
| Cycle-002 H3 (prior reproducible project best, pre-c007) | 0.04420 | ✅ yes (`experiment/4 @ 0c46f43`, preserved) |
| Cycle-005 H2 (aspirational, unreproducible) | 0.029357 | ❌ no (cache hash 9528aeef no longer key-resolves) |
| Cycle-007 H1 (prior reproducible project best, pre-c008) | 0.030408 | ✅ yes (`experiment/9 @ 1249f2d`) |
| **Cycle-008 H1 (NEW reproducible project best)** | **0.027729** | **✅ yes (`experiment/11 @ 18d83a6`)** |
| Cycle-008 H2 (preserved-but-reverted, NEW family scaffolding) | 0.030408 (flat at entry) | ✅ yes — reverted from project state |
| Cycle-008 H3 (preserved-for-meta-fix-only) | 0.030408 (flat at entry) | ✅ yes — reverted from project state |
| Parallel-bench bar (`mf_fno_transfer_bar`) | 0.027429 | ✅ yes |

- **Cycle-008 closes with reproducible composite 0.027729**, which is
  −8.81% vs cycle-008 entry baseline (0.030408), −33.7% vs prior
  reproducible project best pre-c008 (cycle-002 H3 0.04420), and only
  +1.09% above the parallel-bench bar (0.027429). The aspirational
  unreproducible cycle-005 H2 reference (0.029357) is now BEATEN by
  −5.55% — the project has moved beyond the prior aspirational ceiling
  into reproducible territory.
- The **parallel-bench bar gap (+9.7% at H1 entry, +0.00298 abs) is
  89.93% closed** by H1's capacity-axis alone. The remaining
  +0.000300 (+1.09%) gap is now the cycle-009 dethrone target.
- The project's scoreboard moved meaningfully forward even though 2 of
  3 hypotheses formally REVERTed: H1 alone produced the largest
  cycle-on-cycle composite delta since cycle-005 H2's aspirational run.

## H1 = `revert_bookkeeping_keep_intent` (7th project-wide; 4th in the bookkeeping-revert-with-keep-intent series)

This is the **4th experiment in the bookkeeping-revert-with-keep-intent
sub-series** (the broader streak goes back to cycle-001, but the
**bookkeeping-revert with score-improvement-banked AND branch-preserved
as cycle-N+1 entry** sub-pattern is more recent):

| Cycle / hypothesis | Composite delta | Branch banked as next-cycle entry |
|---                  |---              |---                                |
| cycle-002 H3 — `fno_coreg_residual` hybrid (first family to beat paper composite geomean) | 0.0775 → 0.04420 (−43%) | `experiment/4 @ 0c46f43` |
| cycle-005 H2 — `fno_coregionalization` two-stage LF→HF transfer (aspirational, later non-reproducible) | 0.033726 → 0.029357 (−13%) | `experiment/7 @ be36cba` |
| cycle-007 H1 — `fno_coregionalization` constructor fix (restored cycle-005 frontier reproducibly) | 0.039578 → 0.030408 (−23.17%) | `experiment/9 @ 1249f2d` |
| **cycle-008 H1 — `fno_coregionalization` paper-config capacity bump (89.93% of bar gap closed)** | **0.030408 → 0.027729 (−8.81%)** | **`experiment/11 @ 18d83a6`** |

The "fix-then-bump" decomposition pattern is now operational: cycle-007
H1 repaired the constructor signature (structural enabler); cycle-008 H1
wired paper-capacity values through the repair (science lever). Each
got measured independently against the same baseline, separating
infrastructure repair from architectural science.

## H2 = genuine REVERT (FiLM-via-LayerNorm architecture-falsified on Poisson)

This is the **4th genuine REVERT in project history** (1st: cycle-003
H1 @ +91.7%; 2nd: cycle-006 H1 cross-architecture recipe non-portability;
3rd: cycle-007 H2 @ +12.36% composite / +32.70% heat invariance falsified).
H2's regression magnitude (+9.66% vs banked best) is smaller than c003
or c007, but the structural class is genuinely architectural: the
hypothesis was tested honestly per spec, runs completed cleanly (no
NaN, no crash), both kill-switches CLEAR (failure mode = silent
under-performance, not blow-up), and the result is the result.

**The architectural lesson (cycle-009 input):**

> **FiLM-via-LayerNorm on HF-only FNO cannot synthesize the LF→HF
> correlation pathway that `ifc_poisson` requires.** m-conditioning
> via FiLM affines (γ, β) can **re-scale** a learned representation
> per fidelity, but cannot **CREATE** the LF→HF structure that the
> multi-fidelity families exploit. The Poisson dataset has strong
> LF→HF signal that `fno_mf_stack` (0.05961) and `fno_coreg_residual`
> (0.07419) both exploit directly via LF-input pathways. H2's HF-only
> architecture discards the LF channel by design.

Heat was a near-miss at 2nd place (0.017102, +10.3% behind
`fno_coregionalization @ 0.01551`) — suggests FiLM-on-HF-only is
competitive on PDEs where HF training data alone is sufficient.

**Implication for cycle-009:** any single-family Heat+Poisson candidate
must either:
- **(a)** re-introduce the LF→HF pathway (residual ladder), OR
- **(b)** condition on LF samples directly in the FiLM affines
  (`γ(m, LF_features)` instead of `γ(m, m²)`).

Pure m-conditioning is insufficient. The 828 LOC of FiLM scaffolding
on `experiment/12 @ 540e684` is preserved for potential cycle-009
revisit with a `γ(m, LF_features)` revision.

## H3 = genuine REVERT (three-stage curriculum architecture-incompatible with residual ladder)

This is the **5th genuine REVERT in project history** and the **2nd
consecutive** in cycle-008 — the first cycle with two genuine REVERTs.
The damage profile is dramatic: `fno_coreg_residual × ifc_heat`
regressed **19×** from prior single-stage 0.026 to 0.509, tripping the
universal `ifc_heat > 0.0194` kill-switch **26×** over threshold.

**The architectural lesson (cycle-009 input):**

> **Three-stage frozen-LF-HF-residual curricula are INCOMPATIBLE with
> co-evolved residual ladder designs (`fno_coreg_residual`,
> `fno_coregionalization`).** These architectures assume LF and HF
> networks **co-evolve END-TO-END** — the HF residual depends on the
> **CURRENT** LF representation. Stage 2's `requires_grad=False` LF
> freeze forces the HF residual to correct against an
> **OUT-OF-DISTRIBUTION** frozen LF state from the LF-only pretrain
> regime, producing garbage. Stage 3's unfreeze comes too late — HF
> residual is already in a poor local minimum (val/test gap 12× on
> Heat confirms catastrophic overfitting or final-state-checkpoint
> divergence).

**The kill-switch design lesson (cycle-009 input):**

> Multi-stage curriculum kill-switches **MUST** include BOTH:
> - **(a)** an absolute Stage_k vs prior single-stage baseline check
>   (`stage_k_final_hf_test_nrmse > 1.25 × prior_single_stage_test_nrmse → REVERT to baseline`),
>   AND
> - **(b)** inter-stage ratio checks at each transition.
>
> Single inter-stage ratio kill-switches assume damage occurs in the
> LATER stage only — fragile. Real damage can occur in ANY stage.
> H3-specific Stage3/Stage2 Heat ratio = 1.00 because Stage 2 already
> produced 0.509; Stage 3 was a no-op on Heat. The universal
> `ifc_heat > 0.0194` kill-switch caught it only post-hoc at
> finalize time, not mid-training.

**Implication for cycle-009:**
- **DO NOT** propose three-stage frozen-LF curricula on `fno_coreg_residual`
  or `fno_coregionalization` — end-to-end joint training (cycle-005
  H2 continuous-LR-schedule pattern) is the right recipe for
  co-evolved designs.
- Three-stage curricula MAY be appropriate for families with LF and
  HF networks **independent by design**: `mf_fno_transfer_bar` (LF
  outputs a feature map that's an INPUT to the HF FNO, not a co-trained
  residual) and `fno_mf_stack` (per-fidelity stacked predictions).
- Any cycle-009 multi-stage proposal MUST specify BOTH absolute and
  inter-stage kill-switches per the lesson above.

### KEEP-worthy meta-fix (recipe_hash pattern)

Despite H3's architectural failure, the cycle-003 backlog
**`recipe_hash` checkpoint guard** meta-fix WORKED CORRECTLY:

- Live stale-checkpoint rejection log line verified:
  `[resume] REJECTED stale checkpoint: recipe_hash '148a2641b07fe5da' != '0095c3ff614e17b8'`
- The PATTERN — `sha256(json.dumps({**SMOKE_DEFAULTS,
  "stage_strides":[0.25,0.5,0.25]}, sort_keys=True).encode()).hexdigest()[:16]`
  written to `last.pt`/`best.pt` and checked at resume — is **reusable**.

**cycle-009 action:** cherry-pick the `recipe_hash` pattern from
`models/fno_coreg_residual/smoke_eval.py` (lines 113-123, 461-485,
495, 498, 505 — or thereabouts) into a portable utility
`models/_common/recipe_hash.py` and apply it to ALL family
`smoke_eval.py` files. This closes the cycle-003 H1 stage-resume
contamination pathway **project-wide**, not just for
`fno_coreg_residual`. The three-stage curriculum gating logic is
**NOT** reusable — do NOT cherry-pick stage gating into other
families with co-evolved residual ladder architectures.

## Two consecutive GENUINE REVERTs in one cycle (project first)

This is the **first cycle in project history with two genuine REVERTs**.
Both are architecture-falsified, not bookkeeping-induced:

| Verdict | Composite delta vs banked best | Class |
|---|---:|---|
| cycle-008 H2 | +9.66% (+0.002679 abs) | architecture_falsified_on_poisson (FiLM-on-HF-only insufficient for LF→HF correlation) |
| cycle-008 H3 | +9.66% (+0.002679 abs) | architecture_incompatible_three_stage_on_residual_ladder (frozen-LF curriculum vs co-evolved design) |

Same composite signature (flat at entry baseline; +9.66% vs H1 banked
best); different underlying causes (H2 added a NEW non-dominant family
contributing zero to composite; H3 BROKE an existing dominant family
out of the per-cell argmin). The CEO playbook correctly distinguished
both REVERTs as substantive (NOT `revert_bookkeeping_keep_intent`):
the R5b monotonic check independently demanded REVERT in both cases.

The two REVERTs **did not move the cycle-009 entry baseline** — H1's
`experiment/11 @ 18d83a6 @ 0.027729` is preserved as the cycle-009
entry.

## Precheck infra bugs — 6th consecutive cycle requiring overrides

| Bug | Count before c008 | Count after c008 | Note |
|---|---:|---:|---|
| `score_direction` polarity (lower-is-better metric) | 8 | **10** | H1 9th instance; H2 10th instance (symmetric flip — silenced regression as "Score OK") |
| Empty-detail `scope` / `fixed_surfaces` | 3 | **4** | H1 4th instance (short-SHA mismatch sub-class) |
| Leakage-check substring collision (builder phase) | 5 | **6** | H2 6th instance (4 findings: `satisfy, description, ifc_raw, frozen` — schema/dispatch tokens) |

`score_direction` symmetric flip note (H2): the polarity bug usually
silences improvements as "regressions"; in H2 it silenced a real
+0.0027 nRMSE regression as "Score OK" (because precheck treats
higher-after-as-better, but composite_nRMSE is lower-is-better — the
flip is symmetric). CEO REVERT decision in H2 was grounded in the R5b
monotonic check, **independent of precheck** — precheck was
non-load-bearing for the verdict.

**Operator action (6th consecutive request):** precheck overhaul.
Until overhauled, the archive note + CEO intent are the load-bearing
institutional record, not the precheck JSON.

## Cycle-009 entry point and strategic recommendations

**Cycle-009 entry baseline (load-bearing, UNCHANGED by H2 and H3):**
- Composite: **0.027729** (composite_nRMSE)
- Branch: `experiment/11-fno_coregionalization-paper-capacity`
- Commit: `18d83a6` (preserved on disk)
- Parent: `experiment/9-fno_coregionalization-constructor-fix @ 1249f2d`
- Per-dataset state: `ifc_heat` 0.012898 (via `fno_coregionalization`,
  2.04× margin over second-place); `ifc_poisson` 0.05961 (via
  `fno_mf_stack`).
- Bar gap remaining: composite 0.027729 vs bar 0.027429 = **+0.000300
  (+1.09% above bar)**. Capacity-axis exhausted on `fno_coregionalization`
  (paper-config is the natural ceiling).

**Preserved reference branches:**
- `experiment/11 @ 18d83a6` — banked best (cycle-009 entry baseline)
- `experiment/12 @ 540e684` — FiLM-via-LayerNorm scaffolding (828 LOC
  preserved for potential cycle-009 revisit with `γ(m, LF_features)`)
- `experiment/13 @ 420a51c` — `recipe_hash` checkpoint guard pattern
  (cycle-009 cherry-pick target for `models/_common/recipe_hash.py`
  portable utility; three-stage gating logic NOT reusable)

**Strategic recommendations for cycle-009:**

1. **Cherry-pick `recipe_hash` pattern into portable utility** —
   create `models/_common/recipe_hash.py` mirroring the H3
   `smoke_eval.py` implementation; apply it to ALL family
   `smoke_eval.py` files. This closes the cycle-003 H1 stage-resume
   contamination pathway PROJECT-WIDE. Estimated scope: small
   refactor + one-line import per family.

2. **Close the +1.09% bar gap on the Poisson side** — capacity-axis
   on `fno_coregionalization` is exhausted; next lever must come from
   the Poisson side. Two paths:
   - Reduce `fno_mf_stack × ifc_poisson` below 0.05961 (current
     leader; potential lever: targeted recipe tuning on this family
     only — but watch the cross-architecture portability lesson).
   - Push `fno_coregionalization × ifc_poisson` below 0.05961 (currently
     0.5945 — a 10× reduction gap; would let the same family own both
     datasets).

3. **Any single-family Heat+Poisson architecture proposal** must
   include EITHER (a) an LF→HF residual pathway OR (b) LF-feature
   conditioning in FiLM affines (`γ(m, LF_features)` instead of pure
   m-conditioning). Reject pure m-conditioning at R2 with cycle-008 H2
   as citation.

4. **Any multi-stage curriculum proposal** must (i) only target
   families with LF/HF networks independent by design
   (`mf_fno_transfer_bar`, `fno_mf_stack`), NOT residual-ladder
   families (`fno_coreg_residual`, `fno_coregionalization`); AND (ii)
   specify BOTH absolute Stage_k-vs-baseline AND inter-stage ratio
   kill-switches. Reject single inter-stage ratio kill-switches at R2
   with cycle-008 H3 as citation.

5. **Operator action (precheck overhaul, 6th consecutive request)**
   — `score_direction` polarity for lower-is-better metrics;
   `scope`/`fixed_surfaces` short-SHA mismatch + empty-detail;
   leakage substring-collision. Out of factory scope; archive note +
   CEO intent are the load-bearing institutional record until
   overhauled.

## Cross-cycle pattern updates

### Existing patterns reinforced

| Pattern | Before cycle-008 | After cycle-008 |
|---|---:|---:|
| `revert_bookkeeping_keep_intent` universal verdict | 6 evals | **7 evals (H1 added)** |
| Precheck `score_direction` polarity bug | 8 instances | **10 instances (H1 9th; H2 10th — symmetric flip silencing regression)** |
| Precheck empty-detail `scope`/`fixed_surfaces` FP | 3 instances | **4 instances (H1 added; short-SHA mismatch sub-class)** |
| Leakage-check substring collision (builder phase) | 5 sub-classes | **6 sub-classes (H2 added — 4 findings `satisfy, description, ifc_raw, frozen` — schema-required/dispatch tokens)** |
| Cross-architecture recipe portability NOT guaranteed | 2 instances | **3 instances (H3 three-stage curriculum incompatibility with co-evolved residual ladder — generalization of recipe non-portability)** |
| Fresh-train variance swamps claimed invariance | 1 instance | **reinforced by H3 val/test 12× gap on Heat (catastrophic divergence in a fresh-stage retrain)** |

### NEW cross-cycle patterns added in cycle-008

1. **"FiLM-via-LayerNorm on HF-only FNO cannot synthesize LF→HF
   correlation pathway"** — pure m-conditioning via FiLM affines can
   re-scale per-fidelity representations but cannot CREATE LF→HF
   structure. Insufficient for Poisson-class datasets where LF
   samples carry significant complementary information. First
   observed cycle-008 H2; cycle-009 implication = reject pure
   m-conditioning at R2 for single-family Heat+Poisson candidates.
   See [[patterns]] §"FiLM-via-LayerNorm on HF-only FNO…".

2. **"Three-stage frozen-LF-HF-residual curricula are INCOMPATIBLE
   with co-evolved residual ladder designs"** — `fno_coreg_residual`
   and `fno_coregionalization` assume LF and HF networks co-evolve
   end-to-end; Stage-2 LF freeze forces HF residual to correct
   against OOD frozen LF state. Three-stage MAY be appropriate for
   families with LF/HF independent by design (`mf_fno_transfer_bar`,
   `fno_mf_stack`). First observed cycle-008 H3; cycle-009 implication
   = reject three-stage on residual-ladder families at R2. See
   [[patterns]] §"Three-stage frozen-LF curricula are incompatible
   with co-evolved residual ladder designs".

3. **"Multi-stage curriculum kill-switches MUST include
   Stage-k-vs-baseline absolute check"** — single inter-stage ratio
   kill-switches assume damage occurs in the LATER stage only;
   fragile. cycle-008 H3 Stage3/Stage2 ratio was 1.00 because Stage 2
   already produced the damage; only the universal post-hoc
   `ifc_heat > 0.0194` kill-switch caught it. cycle-009 implication =
   any multi-stage proposal MUST specify BOTH absolute Stage_k vs
   prior single-stage baseline AND inter-stage ratio checks. See
   [[patterns]] §"Multi-stage curriculum kill-switches must include
   Stage-k-vs-baseline absolute check".

4. **"Bookkeeping-overridable REVERT vs genuine architecture-falsified
   REVERT — diagnostic is R5b, not precheck"** — the CEO playbook
   distinction surfaced explicitly in cycle-008 H2/H3 (2nd cycle
   requiring it after cycle-007 H2). Symptom of
   `revert_bookkeeping_keep_intent`: real composite improvement +
   precheck infra bugs trip formal verdict. Symptom of genuine REVERT:
   real composite regression (or universal kill-switch trip); precheck
   bugs incidental (may even flip in opposite polarity as in H2).
   The diagnostic is the **R5b monotonic check**, NOT precheck. See
   [[patterns]] §"Bookkeeping-overridable REVERT vs genuine
   architecture-falsified REVERT".

## Failures of process to surface in cycle-008

- **6th consecutive operator precheck overhaul request** — load-bearing
  for institutional reporting accuracy. The factory's headline
  disagreed with reality on all 3 hypotheses this cycle (H1
  improvement masked as regression; H2 regression silenced as "OK"
  via symmetric flip; H3 universal heat kill-switch trip not visible
  in precheck JSON). Until overhauled, the archive note + CEO intent
  are the load-bearing institutional record, not the precheck JSON.
- **H3 H3-specific Stage3/Stage2 kill-switch was structurally
  ineffective** — Builder + Strategist + Reviewer all approved a
  kill-switch design that assumed damage in Stage 3, but the actual
  damage occurred in Stages 1/2 and the universal heat kill-switch
  caught it only post-hoc. The kill-switch design lesson (above) is a
  cycle-009 process improvement.
- **Researcher / failure_analyst wrappers continued to time out
  (5+ cycles)** — CEO synthesized substitutes from direct source
  reads. Standing operational practice; no change required in
  cycle-009 R1 / R1.5 plans.
- **Builder hygiene was structurally easy on H1 + H3** (target file
  at HEAD pre-edit, not in dirty set; or new-file-only as in H2). The
  [[dirty-tree-staging]] auto-memory rule has not been stress-tested
  on a dirty-file target in cycle-008.
- **Strategist R2 H3 design flaw was not caught at R2 hard-gate** —
  the kill-switch presumed-Stage-3-damage assumption passed
  Strategist hard-gates but failed empirically. cycle-009 strategist
  should add a hard-gate for multi-stage curricula requiring both
  absolute and inter-stage kill-switches.

## Links

- Experiment notes:
  - [[cycle-008-exp-11]] (H1 full lifecycle)
  - [[cycle-008-exp-11-build]] (H1 build phase)
  - [[cycle-008-exp-12-final]] (H2 final/REVERT phase)
  - [[cycle-008-exp-12-review]] (H2 reviewer + CEO PROCEED)
  - [[cycle-008-exp-12-build]] (H2 build phase)
  - [[cycle-008-exp-13-final]] (H3 final/REVERT phase)
  - [[cycle-008-exp-13-build]] (H3 build phase)
- Failure analysis: [[failure-analysis-cycle-008]]
- Strategy snapshot: [[strategies/cycle-008]]
- Research note: [[sources/research-cycle-008]]
- Patterns updated:
  - [[patterns]] §"Factory precheck `score_direction` is polarity-buggy
    on lower-is-better metrics" (now 10-for-10 incl. symmetric flip)
  - [[patterns]] §"Factory precheck reports empty-detail
    `scope`/`fixed_surfaces` failures that contradict the standalone
    guard" (now 4-for-4)
  - [[patterns]] §"`revert_bookkeeping_keep_intent` universal verdict"
    (now 7-for-7 streak)
  - [[patterns]] §"Factory leakage-check fingerprints `factory.md`
    itself…" (now 6-for-6 builder-phase consecutive)
  - [[patterns]] §"FiLM-via-LayerNorm on HF-only FNO cannot synthesize
    LF→HF correlation" (NEW — first observation cycle-008 H2)
  - [[patterns]] §"Three-stage frozen-LF curricula incompatible with
    co-evolved residual ladder designs" (NEW — first observation
    cycle-008 H3)
  - [[patterns]] §"Multi-stage curriculum kill-switches must include
    Stage-k-vs-baseline absolute check" (NEW — first observation
    cycle-008 H3)
  - [[patterns]] §"Bookkeeping-overridable REVERT vs genuine
    architecture-falsified REVERT" (NEW — first explicit articulation
    cycle-008 H2; reinforced H3)
- Project dashboard: [[factory_mffp]]
- Prior cycle close-outs: [[cycle-001-summary]], [[cycle-002-summary]],
  [[cycle-003-summary]], [[cycle-005-summary]], [[cycle-006-summary]],
  [[cycle-007-summary]]
- Auto-memory honored: [[dirty-tree-staging]], [[factory-cli-invocation]]

## Closing footnote

Cycle-008 closes with a clean engineering win at the architecture
level: H1 produced the largest cycle-on-cycle composite delta since
cycle-005 H2's aspirational run, AND took the project past the
unreproducible cycle-005 H2 ceiling (0.029357) into reproducible
territory at 0.027729. The two consecutive GENUINE REVERTs (H2, H3)
are not failures of the factory but successes of the kill-switch +
monotonic-check protocol: both architectural hypotheses were tested
honestly, falsified empirically, and produced **cycle-009 strategy
inputs** that meaningfully constrain the next cycle's design space.
The `recipe_hash` meta-fix delivered as a side-effect of H3 closes a
cycle-003 backlog item for ALL future research-mode experiments on
the `fno_coreg_residual` family, and the cycle-009 portable utility
cherry-pick will extend the closure project-wide. Cycle-009 enters
with composite 0.027729, +1.09% above the parallel-bench bar, and a
clear strategic shopping list: (1) recipe_hash portable utility,
(2) close the +1.09% bar gap on the Poisson side, (3) reject pure
m-conditioning and three-stage-on-residual-ladder at R2 with this
cycle's architectural citations.
