---
name: cycle-008-exp-12-final
description: Cycle-008 H2 (exp 12) FINAL — genuine REVERT (architecture-falsified on Poisson) on NEW family `fno_coreg_conditioned` (FiLM-via-LayerNorm on single full-resolution HF FNO). Branch `experiment/12-fno_coreg_conditioned-film @ 540e684` (PRESERVED; not merged). Composite_nRMSE 0.030408 (flat vs cycle-008 entry baseline, **+9.66% vs banked best 0.027729 from cycle-008 H1**). `fno_coreg_conditioned × ifc_heat` 0.017102 (2nd place behind `fno_coregionalization` 0.01551 by 10%); `fno_coreg_conditioned × ifc_poisson` 0.749915 (5th place; 12.6× over `fno_mf_stack` winner 0.05961; 5-15× outside Builder's predicted 0.05-0.15 range). Smoke wall 91.99 s total (16× under 25-min kill-switch). Both kill-switches CLEAR — failure mode is silent under-performance, not blow-up. Architectural lesson: FiLM-via-LayerNorm on HF-only FNO cannot synthesize the LF→HF correlation pathway that Poisson requires; m-conditioning via FiLM affines can re-scale a learned representation per fidelity but cannot CREATE LF→HF structure. The Poisson dataset has strong LF→HF signal that `fno_mf_stack` (0.05961) and `fno_coreg_residual` (0.07419) both exploit directly. **First genuine architecture-falsified REVERT since cycle-006 H1 (cross-architecture recipe non-portability) and cycle-007 H2 (per-dataset recipe dispatch heat-invariance violation) — explicitly NOT `revert_bookkeeping_keep_intent`** (composite genuinely failed to improve and regressed +9.66% vs banked best; bookkeeping precheck false-positives were present but non-load-bearing — R5b monotonic check independently demanded revert). Cycle-008 sequence summary: H1 KEEP intent (banked best 0.027729, bar gap 89.93% closed) + H2 GENUINE REVERT (no composite contribution). Cycle-009 entry baseline remains cycle-008 H1's `experiment/11 @ 18d83a6 @ 0.027729`. Cycle-009 strategy implication: any single-family Heat+Poisson candidate must either (a) re-introduce the LF→HF residual pathway, OR (b) condition on LF samples directly in the FiLM affines (e.g., γ(m, LF_features) instead of γ(m, m²)) — pure m-conditioning is insufficient.
metadata:
  type: experiment
tags:
  - factory
  - experiment
  - factory_mffp
  - cycle-008
  - h2
  - fno_coreg_conditioned
  - new-family
  - film-via-layernorm
  - final
  - revert-genuine
  - architecture-falsified-poisson
  - not-revert-bookkeeping
  - both-kill-switches-clear
  - silent-underperformance
project: factory_mffp
experiment_id: "012"
cycle: cycle-008
hypothesis_id: H2
phase: final
verdict: revert
verdict_type: substantive
verdict_class: architecture_falsified_on_poisson
verdict_class_explicit_not: revert_bookkeeping_keep_intent
ceo_intent: revert
formal_verdict: revert
evaluator_verdict: PASS_REVERT
ceo_verdict_evaluator: PROCEED
ceo_verdict_evaluator_doc: .factory/reviews/ceo-verdict-evaluator.md
date: 2026-06-02
branch: experiment/12-fno_coreg_conditioned-film
branch_preserved: true
branch_merged_to_trunk: false
parent_commit: 1249f2d
parent_commit_source: cycle-007 H1 (anisotropic-modes constructor fix) — cycle-008 entry baseline
commit: 540e684
score_before: 0.027729
score_after: 0.030408
score_delta: 0.002679
score_delta_pct: 9.66
score_delta_direction: regression
score_before_source: "cycle-008 H1 banked best (experiment/11 @ 18d83a6)"
score_before_label: previous_best
baseline_entry_composite: 0.030408
baseline_entry_source: "cycle-008 entry baseline (1249f2d) — pre-H1, pre-H2"
delta_vs_entry_baseline_pct: 0.0
delta_vs_entry_baseline_classification: flat
fno_coreg_conditioned_ifc_heat_nRMSE: 0.017102
fno_coreg_conditioned_ifc_heat_rank: 2
fno_coreg_conditioned_ifc_heat_leader: fno_coregionalization
fno_coreg_conditioned_ifc_heat_leader_value: 0.01551
fno_coreg_conditioned_ifc_heat_gap_to_leader_pct: 10.3
fno_coreg_conditioned_ifc_poisson_nRMSE: 0.749915
fno_coreg_conditioned_ifc_poisson_rank: 5
fno_coreg_conditioned_ifc_poisson_leader: fno_mf_stack
fno_coreg_conditioned_ifc_poisson_leader_value: 0.05961
fno_coreg_conditioned_ifc_poisson_multiple_over_leader: 12.6
builder_predicted_poisson_min: 0.05
builder_predicted_poisson_max: 0.15
builder_prediction_actual_multiple_low: 5.0
builder_prediction_actual_multiple_high: 15.0
builder_prediction_in_range: false
composite_contribution_from_new_family: 0
composite_contribution_classification: zero_dominance_neither_dataset
ifc_heat_leaderboard_winner_after: fno_coregionalization
ifc_heat_leaderboard_winner_value_after: 0.01551
ifc_heat_leaderboard_flipped: false
ifc_poisson_leaderboard_winner_after: fno_mf_stack
ifc_poisson_leaderboard_winner_value_after: 0.05961
ifc_poisson_leaderboard_flipped: false
smoke_wall_seconds_total_new_family: 91.99
smoke_wall_seconds_ifc_heat: 64.58
smoke_wall_seconds_ifc_poisson: 27.41
smoke_kill_switch_wall_threshold_seconds: 1500
smoke_kill_switch_wall_tripped: false
smoke_kill_switch_wall_headroom_multiple: 16
smoke_kill_switch_heat_threshold: 0.0194
smoke_kill_switch_heat_value: 0.017102
smoke_kill_switch_heat_tripped: false
smoke_kill_switch_heat_headroom_pct: 12
both_kill_switches_clear: true
failure_mode: silent_under_performance_not_blow_up
cycle_eval_total_wall_seconds: 93
cycle_eval_cache_status: "100% cache-hit for all other 16 cells; new family trained during Build phase (cached)"
hygiene_gate_r5a: PASS
hygiene_gate_r5a_rationale: "H2 added 4 NEW files in a new directory; no existing tests / lint configs / type configs touched"
monotonic_gate_r5b: FAIL
monotonic_gate_r5b_rationale: "composite +9.66% above banked best 0.027729 (0.027729 → 0.030408); mandatory revert"
precheck_gate_r5c_bookkeeping_failures: ["scope", "fixed_surfaces", "ground_truth_leakage"]
precheck_gate_r5c_score_direction_polarity_fired_in_opposite_polarity: true
precheck_gate_r5c_score_direction_polarity_note: "this run, +0.0027 nRMSE regression was reported as 'Score OK' (precheck treats higher-after-as-better, but composite_nRMSE is lower-is-better). The polarity bug is symmetric: usually flips improvements to 'regressions' (9 prior cycles), this time silenced a genuine regression as 'OK'."
precheck_gate_r5c_score_direction_polarity_count_total: 10
precheck_gate_r5c_bookkeeping_load_bearing_for_decision: false
precheck_gate_r5c_decision_grounded_in: R5b monotonic check (independent of precheck)
keep_revert_gate_r5d: REVERT
keep_revert_gate_r5d_class: architecture_falsified_on_poisson
keep_revert_gate_r5d_explicit_not: revert_bookkeeping_keep_intent
genuine_revert_project_history_count_after_h2: 4
genuine_revert_project_history_list: ["cycle-003 H1 (composite +91.7%)", "cycle-006 H1 (cross-architecture recipe non-portability)", "cycle-007 H2 (per-dataset dispatch heat-invariance violation, composite +12.36%)", "cycle-008 H2 (FiLM-via-LayerNorm architecture falsified on Poisson, composite +9.66% vs banked best)"]
revert_bookkeeping_keep_intent_streak_unchanged_after_h2: 7
loc_delta: "+828/-0"
files_changed: 4
files_changed_all_new: true
files_changed_under: models/fno_coreg_conditioned/
files_changed_existing_family_modified: 0
films_via_layernorm_architecture: "GroupNorm(affine=False) + MLP([m, m²]) → 2·C → γ, β with zero-init γ-projection"
films_via_layernorm_modes_kwargs: "separate modes_h: int = 12, modes_w: int = 12 (matches fno_coregionalization/model.py:89-90 and mf_fno_transfer_bar/model.py:70)"
films_via_layernorm_hidden_channels: 64
films_via_layernorm_n_blocks: 4
films_via_layernorm_m_feat_dim: 32
h2_lf_hf_schedule_preserved_verbatim: true
h2_pretrain_lr: 0.001
h2_finetune_lr: 0.0003
h2_pretrain_frac: 0.25
architectural_lesson: "FiLM-via-LayerNorm on HF-only FNO cannot synthesize LF→HF correlation pathway. m-conditioning via FiLM affines can re-scale learned representations per fidelity but cannot CREATE LF→HF structure. Poisson dataset has strong LF→HF signal (fno_mf_stack 0.05961 and fno_coreg_residual 0.07419 both exploit LF input directly). Heat dataset (where LF signal is less dominant) was near-miss at 0.01710 — competitive on PDEs where HF training data alone is sufficient; insufficient on PDEs where LF samples carry significant complementary information."
cycle_009_strategy_implication_a: "re-introduce LF→HF pathway (residual ladder)"
cycle_009_strategy_implication_b: "condition on LF samples directly in FiLM affines (γ(m, LF_features) instead of γ(m, m²))"
cycle_009_strategy_implication_negation: "pure m-conditioning is insufficient"
cycle_009_entry_baseline_composite: 0.027729
cycle_009_entry_baseline_branch: experiment/11-fno_coregionalization-paper-capacity
cycle_009_entry_baseline_commit: 18d83a6
cycle_009_entry_baseline_unchanged_by_h2: true
finalize_notes: "ceo:revert mode=research reason=architecture_falsified_on_poisson metric=composite_nRMSE before=0.027729 after=0.030408 delta=+0.002679 delta_pct=+9.66 hygiene=pass monotonic=fail heat=0.017102 poisson=0.749915 kill_switches=clear hypothesis_type=code execution_artifacts=na e2e=pass backlog_cleared=no"
no_github_mode: true
no_pr_created: true
no_push: true
no_issue_created: true
source: factory-archivist
---

# Experiment #012 FINAL — Cycle-008 H2: NEW family `fno_coreg_conditioned` (FiLM-via-LayerNorm) — REVERT (architecture-falsified on Poisson)

## Final verdict

**`revert`** — genuine, substantive, architecture-falsified on Poisson. **Explicitly NOT `revert_bookkeeping_keep_intent`.**

The architectural hypothesis (FiLM-via-LayerNorm on a single HF FNO can collapse `FAMILY_PDE_SPECIALIZATION_ASYMMETRY` into a single-family Heat+Poisson candidate) was tested honestly and falsified on Poisson. The model was implemented per spec, the runs completed cleanly (no NaN, no crash), and the result is the result.

This is the project's **4th genuine REVERT** (after cycle-003 H1, cycle-006 H1, cycle-007 H2) and the **first since cycle-007 H2** — not in the `revert_bookkeeping_keep_intent` streak (which remains at 7 from prior cycles).

## Quantitative outcome

| Metric | Value | vs target | Status |
|---|---|---|---|
| **Composite nRMSE (H2 branch)** | 0.030408 | minimize | flat vs entry baseline |
| Composite vs cycle-008 entry baseline (1249f2d) | 0.000000 / +0.00% | improve | NEUTRAL |
| Composite vs banked best (cycle-008 H1 exp 11 = 0.027729) | +0.002679 / **+9.66%** | improve or hold | **REGRESSION** |
| `fno_coreg_conditioned × ifc_heat` | 0.017102 | < 0.0194 kill-switch | CLEAR (2nd place; behind `fno_coregionalization` 0.01551 by ~10%) |
| `fno_coreg_conditioned × ifc_poisson` | 0.749915 | Builder predicted 0.05–0.15 | **OUT OF RANGE** (~5–15× worse than predicted; 5th place; behind `fno_mf_stack` 0.05961 by 12.6×) |
| Smoke wall (new family only) | 91.99 s | < 25-min kill-switch | CLEAR (~16× under budget) |
| Total cycle_eval wall | 93 s | budget 14400 s | CLEAR (cache-served all other families) |

### Per-dataset leaderboard (post-H2 cycle_eval)

| Dataset | Winner (post-H2) | Value | `fno_coreg_conditioned` rank | `fno_coreg_conditioned` value | Gap to leader |
|---|---|---:|---:|---:|---|
| `ifc_heat` | `fno_coregionalization` | 0.01551 | 2nd of 8 | 0.017102 | **+10.3%** (close near-miss) |
| `ifc_poisson` | `fno_mf_stack` | 0.05961 | 5th of 8 | 0.749915 | **12.6× over leader** (catastrophic) |

Neither dataset's leaderboard flipped — H2 dominates **zero cells**, contributes zero to composite.

## Why composite is exactly flat at entry baseline

The composite is the geomean of per-dataset bests. On the H2 branch:
- `ifc_heat` best: `fno_coregionalization` at 0.01551 (unchanged from baseline — H2 branch does NOT inherit H1's capacity bump, deliberately keeps `hidden_channels=64`, NOT H1's paper-config 128, to isolate the FiLM mechanism from the capacity axis).
- `ifc_poisson` best: `fno_mf_stack` at 0.05961 (unchanged from baseline).
- `fno_coreg_conditioned` does NOT dominate either cell → contributes ZERO to composite.

This is a clean "addition with no effect" outcome — the new family lands 2nd on Heat (close but non-dominant) and 5th on Poisson (catastrophic). The H2 architectural hypothesis was tested and fell short on both axes.

## Why this is NOT `revert_bookkeeping_keep_intent`

The 7 prior consecutive `revert_bookkeeping_keep_intent` cases (cycles 001, 002, 005, 007 H1, 008 H1, etc.) shared a specific pattern: **composite genuinely improved**, but the precheck `score_direction` polarity bug or empty-detail `scope`/`fixed_surfaces` check triggered a false revert. CEO override → effectively KEEP because the hypothesis was validated.

**This case is structurally different:**
1. Composite is **flat at baseline**, not improved.
2. Composite is **+9.66% above banked best** — a real regression vs the active project frontier.
3. The hypothesis predicted Poisson 0.05–0.15; actual is 0.7499 (5–15× off).
4. The architecture (FiLM-via-LayerNorm on a single HF FNO) was tested honestly and falsified on Poisson — no bookkeeping bug, no infrastructure issue, no schedule mis-binding.

**Note on precheck this cycle:** 3/4 documented bookkeeping patterns fired (scope, fixed_surfaces, ground_truth_leakage); the `score_direction` polarity bug fired in **OPPOSITE polarity** this time — the +0.0027 nRMSE regression was reported as "Score OK" (because the precheck treats higher-after-as-better, but composite_nRMSE is lower-is-better). This is the symmetric flip of the bug: usually silences improvements (9 prior cycles); this time silenced a regression. Precheck blocking_failures = `['scope', 'fixed_surfaces', 'ground_truth_leakage']`, but **CEO REVERT decision is independent of precheck** and is grounded in **Evaluator R5b monotonic check** (genuine +9.66% regression vs banked best). The polarity bug count is now 10 across project history (`score_direction_polarity_bug_count: 10` in the dashboard).

## Architectural lesson — failure mode classification (for cycle-009)

**FiLM-via-LayerNorm on single HF FNO is insufficient for `ifc_poisson`.** Specifically:

1. The Poisson dataset has strong LF→HF correlation signal — `fno_mf_stack` 0.05961 and `fno_coreg_residual` 0.07419 both exploit the LF input directly.
2. H2's HF-only architecture **discards the LF channel by design** — there is no LF→HF residual pathway, only m-conditioning via FiLM affines.
3. FiLM γ/β can **re-scale** a learned representation per fidelity, but cannot **CREATE** the LF→HF structure that the multi-fidelity families exploit.
4. Heat (where LF signal is less dominant) was a near-miss at 0.01710 — suggests FiLM-on-HF-only is competitive on PDEs where HF training data alone is sufficient, but not on PDEs where LF samples carry significant complementary information.

### Cycle-009 strategy implication

Any single-family Heat+Poisson candidate must either:

- **(a)** re-introduce the LF→HF pathway (residual ladder), OR
- **(b)** condition on LF samples directly in the FiLM affines (e.g., `γ(m, LF_features)` instead of `γ(m, m²)`).

**Pure m-conditioning is insufficient.** Any cycle-009 strategy proposing a single-family answer without one of (a) or (b) should be rejected at R2 with this experiment as the citation.

## Branch preservation

`experiment/12-fno_coreg_conditioned-film @ 540e684` is **PRESERVED for cycle-009 reference** — do NOT delete. The 828 LOC of FiLM-via-LayerNorm scaffolding may be useful if a revised hypothesis (FiLM-on-residual-with-LF-features in γ inputs) emerges from cycle-009 Poisson failure analysis.

- 4 NEW files under `models/fno_coreg_conditioned/`:
  - `model.py` (218 LOC; `FNOCoregConditioned` + `FiLMNorm`)
  - `smoke_eval.py` (517 LOC; cycle-007 H2 LF→HF schedule preserved verbatim)
  - `manifest.json` (6 LOC)
  - `INSPIRATION.md` (87 LOC; 5 bibtex_keys: `li2022ifc, li2020fno, lyu2023mffno, beggs2025pdecond, herde2024poseidon`)
- Files are NOT merged to the trunk — only branch metadata preserved.

## Cross-cycle CEO playbook update

This is the **second consecutive cycle where the CEO must distinguish two REVERT classes**:

- **`revert_bookkeeping_keep_intent`** — precheck false-positive WHEN composite genuinely improves. CEO override → effectively KEEP. 7 prior occurrences (cycles 001, 002, 005, 007 H1, 008 H1, plus earlier).
- **Genuine REVERT** — precheck may also fire, but composite truly regresses or fails to improve. CEO override does NOT apply; decision is grounded in R5b monotonic check. 4 prior occurrences (cycles 003 H1, 006 H1, 007 H2, 008 H2).

**The diagnostic question is NOT "did precheck fail?" but "does R5b monotonic check pass against the banked best?".** R5b is independent of precheck and is the load-bearing gate for keep-vs-revert when the hypothesis intent is "improve composite." If R5b passes (composite improved or held), bookkeeping-only failures can be overridden. If R5b fails (composite regressed or stayed flat at baseline below the banked best), the revert is genuine regardless of what the precheck reports.

This distinction is now appended to `patterns/patterns.md` as a cross-cycle pattern. See [[patterns]] §"Bookkeeping-overridable REVERT vs genuine architecture-falsified REVERT — the diagnostic is R5b, not precheck".

## Cycle-008 sequence summary

| Step | Hypothesis | Verdict class | Composite delta | Banked? |
|---|---|---|---:|---|
| Entry | cycle-007 H1 (constructor fix) baseline `1249f2d` | — | — (= 0.030408) | yes |
| H1 (exp 11) | Paper-config capacity bump on `fno_coregionalization` (K=20, n_blocks=6, b_hidden=128, hidden_channels=128, modes_cap=16) | `revert_bookkeeping_keep_intent` (KEEP intent) | **−8.81%** to 0.027729 | **YES — new project best, banked** |
| H2 (exp 12) | NEW family `fno_coreg_conditioned` (FiLM-via-LayerNorm) | **genuine REVERT** (architecture-falsified on Poisson) | flat 0.030408 / **+9.66% vs banked best** | NO — branch preserved, not merged |

**Net cycle-008 outcome:** reproducible project best 0.030408 → **0.027729** (`−8.81%`), 89.93% of bar gap closed by capacity-axis alone. Cycle-009 entry baseline = `experiment/11 @ 18d83a6 @ 0.027729`.

## Kill-switch summary

- `ifc_heat > 0.0194`: CLEAR (0.0171 < 0.0194 by 12%)
- Smoke wall-time > 25 min: CLEAR (1.53 min, 16× under)
- **Neither kill-switch triggered → revert is on composite/cell-dominance grounds, not on kill-switch grounds.** Failure mode classification: **silent under-performance, not blow-up.**

## Links

- Project dashboard: [[factory_mffp]]
- Review-phase companion (this morning, 2026-06-02 18:29Z): [[cycle-008-exp-12-review]]
- Build-phase companion: [[cycle-008-exp-12-build]]
- Cycle-008 H1 final (KEEP intent, banked best 0.027729): [[cycle-008-exp-11]]
- Cycle-008 H1 build: [[cycle-008-exp-11-build]]
- Cycle-008 strategy: [[cycle-008]] — R2 plan-approved snapshot
- Cycle-008 failure analysis (R1): [[failure-analysis-cycle-008]]
- Prior genuine REVERTs (cross-cycle reference):
  - [[cycle-006-exp-8]] (cross-architecture recipe non-portability)
  - [[cycle-007-exp-10]] (per-dataset dispatch, heat invariance violation)
- CEO verdict (Evaluator R4/R5 phase): `.factory/reviews/ceo-verdict-evaluator.md`
- Strategy snapshot driving H2: `.factory/strategy/current.md`
- Verdict record (factory CLI): `.factory/experiments/012/verdict.json`
- Parent baseline: `1249f2d` (cycle-007 H1 anisotropic-modes constructor fix)
- H2 branch HEAD: `540e684` on `experiment/12-fno_coreg_conditioned-film` (PRESERVED)
- Cross-cycle patterns appended this cycle:
  - [[patterns]] §"Bookkeeping-overridable REVERT vs genuine architecture-falsified REVERT — the diagnostic is R5b, not precheck" (NEW)
  - [[patterns]] §"FiLM-via-LayerNorm on HF-only FNO cannot synthesize LF→HF correlation — pure m-conditioning is insufficient for Poisson-class datasets" (NEW)
- Auto-memory honored: [[dirty-tree-staging]], [[factory-cli-invocation]]
