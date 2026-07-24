---
name: cycle-008-exp-11
description: Cycle-008 H1 (exp 11) full lifecycle — Paper-config capacity bump on the cycle-007 H1 repaired anisotropic-modes constructor of `fno_coregionalization`. R4 result composite_nRMSE 0.030408 → 0.027729 (−8.81%); `fno_coregionalization × ifc_heat` 0.01551 → 0.012898 (−16.84%, takes ownership of the heat leaderboard from itself; all other families ≥2× worse on heat); `fno_coregionalization × ifc_poisson` 0.7501 → 0.5945 (−20.75%, composite-neutral — `fno_mf_stack` retains poisson at 0.0596). Bar `mf_fno_transfer_bar` parallel-bench 0.027429 short by +0.000300 (+1.09% above bar). Heat kill-switch (0.0194) clear with 33% headroom. 89.93% of the H1-entry bar gap closed by capacity-axis alone. Verdict `revert_bookkeeping_keep_intent` — 5th consecutive in cycle-007/008 (7th project-wide). Independent verification: scope clean, fixed_surfaces clean, leakage clean, smoke_test PASS; precheck `score_direction` polarity bug flips real −8.81% improvement to +8.81% "regression" (9-of-9 streak project-wide); precheck `scope`/`fixed_surfaces` short-SHA mismatch + empty-detail false positives (5th consecutive operator-action request for precheck overhaul). Branch `experiment/11-fno_coregionalization-paper-capacity @ 18d83a6` PRESERVED as new banked best for cycle-009 entry.
metadata:
  type: experiment
tags:
  - factory
  - experiment
  - factory_mffp
  - cycle-008
  - h1
  - fno_coregionalization
  - paper-config
  - capacity-bump
  - li2022ifc
  - revert-bookkeeping-keep-intent
  - precheck-polarity-bug
  - bar-gap-89pct-closed
project: factory_mffp
experiment_id: "011"
cycle: cycle-008
hypothesis_id: H1
verdict: revert_bookkeeping_keep_intent
ceo_intent: keep
formal_verdict: revert
ceo_intent_rationale: composite improved -8.81% (0.030408 -> 0.027729); fno_coregionalization heat -16.84% (now project leader at 0.012898); poisson -20.75% on same family (composite-neutral); kill switch clear with 33% headroom; 89.93% of bar gap closed; all 4 real precheck checks (ground_truth_leakage, anti_pattern, smoke_test, scope independent verification) PASSED
formal_verdict_rationale: precheck score_direction polarity bug misreads -8.81% improvement as +8.81% regression (9-for-9 streak); scope/fixed_surfaces report empty-detail / short-SHA-mismatch false positives vs independent verification clean
score_before: 0.030407732506238343
score_after: 0.027728854219631654
score_delta: -0.002678878286606689
score_delta_pct: -8.80985876226417
score_polarity: lower_is_better
metric: composite_nRMSE
ifc_heat_best_before: 0.01551
ifc_heat_best_after: 0.012898497199156745
ifc_heat_best_family_before: fno_coregionalization
ifc_heat_best_family_after: fno_coregionalization
ifc_heat_best_delta_pct: -16.84
ifc_poisson_best_before: 0.05961
ifc_poisson_best_after: 0.05961
ifc_poisson_best_family_before: fno_mf_stack
ifc_poisson_best_family_after: fno_mf_stack
ifc_poisson_best_delta_pct: 0.0
fno_coregionalization_ifc_heat_after: 0.012898497199156745
fno_coregionalization_ifc_heat_before: 0.01551
fno_coregionalization_ifc_heat_delta_pct: -16.84
fno_coregionalization_ifc_heat_cache_status: miss
fno_coregionalization_ifc_poisson_after: 0.5944766713681287
fno_coregionalization_ifc_poisson_before: 0.7501
fno_coregionalization_ifc_poisson_delta_pct: -20.75
fno_coregionalization_ifc_poisson_cache_status: miss
fno_coregionalization_owns_heat: true
fno_coregionalization_heat_margin_over_second_place: 2.04
heat_second_place_family: fno_coreg_residual
heat_second_place_value: 0.026277487241491388
kill_switch_heat_threshold: 0.0194
kill_switch_heat_tripped: false
kill_switch_heat_headroom_pct: 33.5
kill_switch_heat_headroom_abs: 0.006501502800843255
bar_mf_fno_transfer_bar_parallel_bench: 0.027429
bar_gap_remaining_abs: 0.000299854219631654
bar_gap_remaining_pct: 1.09
bar_gap_closed_pct: 89.93
target_met_composite_le_0_0274: false
target_met_composite_le_0_028: true
target_met_heat_le_0_013: true
wall_seconds_heat: 169.91
wall_seconds_poisson: 144.75
wall_seconds_total: 315
wall_kill_switch_cap_seconds: 1500
wall_headroom_pct: 79
reviewer_verdict: PASS
ceo_verdict_builder: PROCEED
ceo_verdict_reviewer: PROCEED
ceo_verdict_strategist: PROCEED_PLAN_APPROVED
ceo_verdict_evaluator: PASS_KEEP
ceo_verdict_e2e: revert_bookkeeping_keep_intent
precheck_real_checks_passed: ["ground_truth_leakage", "anti_pattern", "smoke_test", "scope_independent", "fixed_surfaces_independent"]
precheck_infra_bug_failures: ["score_direction", "scope_polarity_or_short_sha", "fixed_surfaces_empty_detail"]
precheck_infra_bug_polarity_bug_count_after_h1: 9
revert_bookkeeping_keep_intent_streak_after_h1: 7
empty_detail_scope_fixed_surfaces_false_positive_count_after_h1: 4
operator_action_precheck_overhaul_consecutive_requests: 5
date: 2026-06-02
branch: experiment/11-fno_coregionalization-paper-capacity
branch_preserved: true
parent_branch: experiment/9-fno_coregionalization-constructor-fix
parent_commit: 1249f2d
commit: 18d83a6
files_changed: 1
loc_delta: "+10/-4"
target_file: models/fno_coregionalization/smoke_eval.py
no_github_mode: true
no_pr_created: true
no_push: true
no_issue_created: true
duration_seconds_eval: 315
cycle_009_entry_composite: 0.027729
cycle_009_entry_branch: experiment/11-fno_coregionalization-paper-capacity
cycle_009_entry_commit: 18d83a6
project_best_composite_after: 0.027729
project_best_branch_after: experiment/11-fno_coregionalization-paper-capacity
project_best_commit_after: 18d83a6
project_best_source_after: cycle-008 H1
prior_project_best_composite: 0.030408
prior_project_best_source: cycle-007 H1
source: factory-archivist
---

# Experiment #011 — Cycle-008 H1: `fno_coregionalization` paper-config capacity bump

## Hypothesis

**Cycle-008 H1 — EXPLOIT, HIGH priority, LOW risk, single-file, `CAPACITY_PARETO` failure mode.** Wire the
IFC paper `full_config.json` capacity values into `SMOKE_DEFAULTS` of
`models/fno_coregionalization/smoke_eval.py` so the cycle-007 H1 repaired anisotropic-modes
constructor finally runs at paper capacity instead of the prior under-capacity smoke defaults.

**Expected impact (Strategist R2, anchored to cycle-008 baseline 0.030408):**
- composite_nRMSE `0.030408 → ≈ 0.028` (high end ~0.026; low end ~0.029).
- `fno_coregionalization × ifc_heat` `0.01551 → ~0.013` (high end ~0.012, low end ~0.014).
- `fno_coregionalization × ifc_poisson` `0.7501 → 0.5-0.7` (composite-neutral; `fno_mf_stack` still owns poisson).
- Kill-switch: `ifc_heat > 0.0194` ⇒ REVERT.

## Result

**VERDICT: `revert_bookkeeping_keep_intent` (5th consecutive cycle-007/008 instance; 7th project-wide).**
CEO intent = **KEEP**; formal precheck record = **REVERT** due to infrastructure bugs (see §R5).
Branch `experiment/11-fno_coregionalization-paper-capacity @ 18d83a6` preserved as the new banked best
for cycle-009 entry.

| Metric | Cycle-008 R0 baseline (cycle-007 H1) | R4 H1 after | Δ | Δ % | Direction |
|---|---:|---:|---:|---:|---|
| composite_nRMSE | 0.030408 | **0.027729** | **−0.002679** | **−8.81%** | ✅ improvement |
| ifc_heat best-family nRMSE | 0.01551 (fno_coregionalization) | **0.012898** (fno_coregionalization) | −0.002612 | −16.84% | ✅ improvement |
| ifc_poisson best-family nRMSE | 0.05961 (fno_mf_stack) | 0.05961 (fno_mf_stack) | 0.0 | 0.0% | ◇ unchanged (cache hit) |
| `fno_coregionalization × ifc_poisson` | 0.7501 | **0.5945** | −0.1556 | **−20.75%** | ✅ same-family improvement (composite-neutral) |
| Heat kill-switch (≤ 0.0194) | — | **0.012898** | −0.006502 headroom | 33.5% under threshold | ✅ NOT tripped |
| Composite bar 0.027429 (parallel-bench) | — | 0.027729 | +0.000300 | +1.09% over | ◇ short by 0.0003 |
| Bar gap closed (from H1 entry) | — | **89.93%** | — | — | ✅ dominant axis |
| Composite target ≤ 0.028 | — | 0.027729 | — | — | ✅ MET |
| ifc_heat target ≤ 0.013 | — | 0.012898 | — | — | ✅ MET |
| Aspirational composite ≤ 0.0274 | — | 0.027729 | +0.000300 | +1.09% | ◇ short by 0.0003 |

**Hypothesis validated largely.** Both component hard targets (composite ≤ 0.028 AND heat ≤ 0.013) met; the only miss is the dethrone-the-bar aspirational at composite ≤ 0.027429, by a hair (+0.0003, +1.09%). The capacity axis was the correct lever: with it alone the H1-entry bar gap (+9.7%) is 89.93% closed.

### `fno_coregionalization` family take-over of `ifc_heat`

The H1 bump pushes `fno_coregionalization × ifc_heat` from 0.01551 to **0.012898**, making this family the **sole project-history holder** of the heat leaderboard at >2× margin over the second-place family:

| Rank | Family | ifc_heat nRMSE | vs winner |
|---:|---|---:|---:|
| 1 | **fno_coregionalization** | **0.012898** | — |
| 2 | fno_coreg_residual | 0.026277 | 2.04× |
| 3 | mf_fno_transfer_bar | 0.033175 | 2.57× |
| 4 | fno_mf_stack | 0.099945 | 7.75× |
| 5 | transolver_residual | 0.114559 | 8.88× |
| 6 | v9_baseline | 0.148834 | 11.54× |
| 7 | transolver_attention_fusion | 0.149230 | 11.57× |

The heat lever is locked to this family. `ifc_poisson` remains owned by `fno_mf_stack` at 0.05961 (this family still 10× behind on poisson at 0.5945 — the composite-neutral side of the trade) — that is the next H2/H3 lever.

### Wall-time + kill-switch

- `cycle_eval.sh` wall 315 s total (~5.25 min): heat cell 169.91 s, poisson cell 144.75 s. ~79% under the 25-min smoke kill-switch cap. The pre-flight projection (14-15 min) was conservative — the actual SLURM H100 ran ~3× faster than the H100 smoke projection (likely Slurm-side I/O / dataset-load cost dominated the 4.31 s 2-epoch wall).
- Heat kill-switch (`ifc_heat > 0.0194`) **NOT tripped** — 0.012898 sits at 33.5% headroom (target ≤ 0.0194 vs realized 0.012898).
- Both `fno_coregionalization` cells were cache MISS (expected — `__code_hash__` changed from the smoke_eval.py edit); other 12 cells cache HIT.

## §R5 — `revert_bookkeeping_keep_intent` justification (5th consecutive)

The factory `finalize` recorded `revert` again due to the same precheck infrastructure pattern that has held for cycles 005-008:

1. **`score_direction` polarity bug** — precheck interprets the metric as higher-is-better and flips the real `-8.81%` improvement (0.030408 → 0.027729 on lower-is-better composite_nRMSE) into a `+8.81%` "regression". 9-of-9 across project history; the bug is now load-bearing every cycle.
2. **`scope` empty-detail / short-SHA-mismatch false positive** — precheck reports a scope violation against an unresolvable short-SHA baseline (reuse of `1249f2d` short form vs the precheck's full-SHA expectation). Independent verification with `factory guard . --baseline 1249f2d --check-scope` on the same diff was clean. 4th consecutive.
3. **`fixed_surfaces` empty-detail false positive** — precheck reports a fixed-surface violation with empty detail. Independent verification reads the diff: 1 file under `models/fno_coregionalization/`, no fixed-surface touches. 4th consecutive.
4. **All real checks PASS**: `ground_truth_leakage` (flagged=false, risk=none — first cycle with clean leakage on BOTH the hypothesis declaration AND the actual diff), `anti_pattern`, `smoke_test`, and the independent `scope`/`fixed_surfaces` re-runs.

**CEO override** applied — branch and code preserved. The factory-vs-CEO disagreement is purely bookkeeping infrastructure, NOT a research outcome. This is now the 5th consecutive request for a precheck overhaul (operator action, out of factory scope).

## Anti-pattern compliance (all six cycle-008 anti-patterns satisfied)

1. **MFRNP loss-recipe / reweighting BANNED** (3/3 prior REVERTs lock-in) — satisfied. H1 is capacity-only; no `hf_loss_weight` / `lf_loss_weights` edits.
2. **Per-dataset MFRNP recipe dispatch BANNED** (cycle-007 H2 REVERT) — satisfied. No `_DATASET_RECIPES` dict, no `resolve_fidelity_weights` helper added.
3. **A1+B1+B3 bundling FORBIDDEN** — satisfied. H1 on its own branch, single-file, single-family, zero file overlap with H2/H3's planned mutable surfaces.
4. **D1 (`mf_fno_transfer_bar` smoke-config bump) DEFERRED to cycle-009+** — satisfied. No edits to `models/mf_fno_transfer_bar/**`.
5. **A3 (F-FNO factorized spectral conv refactor) DEFERRED to cycle-009+ as `fno_coreg_ffno`** — satisfied. No architectural refactor.
6. **`models/fno_coregionalization/model.py` edits FORBIDDEN for H1** (Strategist R2 explicit clause) — satisfied. `model.py` byte-identical to `1249f2d`.

## Cross-cycle pattern notes

- **Paper-config wire-up on a freshly-repaired constructor delivered the dominant composite lever as predicted by failure_analysis.** Cycle-008 R1 failure analysis identified `CAPACITY_PARETO` on `fno_coregionalization × ifc_heat` as the dominant failure mode (12.6× composite log-weight); H1 capacity-axis alone closed 89.93% of the +9.7% bar gap. The fix-then-bump pattern (cycle-007 H1 repaired the constructor signature; cycle-008 H1 wired the paper capacity through the repair) is a clean two-cycle decomposition — separating the structural enabler (constructor signature) from the science lever (capacity values) lets each get measured independently against the same baseline.
- **Capacity-axis was the right call; recipe-axis (banned this cycle) was correctly avoided.** The cycle-007 H2 REVERT and 3-of-3 MFRNP-recipe REVERT streak both pointed at "do not bring loss-reweighting into this family yet." Cycle-008 H1 honored that boundary AND extracted the dominant gain — confirming the anti-pattern boundary was wisdom, not over-caution.
- **First hypothesis in project history to land both hard component targets in the same R4.** Both composite ≤ 0.028 AND heat ≤ 0.013 cleared; only the bar dethrone (composite ≤ 0.027429) missed, and by +0.0003. Two clean target hits, one near-miss.
- **First hypothesis with clean leakage on both passes** (carries over from build-phase note). The leakage-check substring-collision pattern (long-running infra bug since cycle-001) does not fire on numerical-knob bumps that don't introduce new public-API tokens.
- **Precheck overhaul is now load-bearing for the factory's institutional reporting accuracy.** Five consecutive cycles have surfaced the same bug pattern; the factory's headline "revert" disagrees with reality every time. Until overhauled, the archive note + CEO intent are the load-bearing institutional record, not the precheck JSON.

## What got banked

- **New reproducible project best**: composite_nRMSE **0.027729** (was 0.030408 at cycle-007 H1).
- Branch `experiment/11-fno_coregionalization-paper-capacity @ 18d83a6` preserved as the cycle-009 entry baseline.
- The chain is now `be36cba` (c005 H2 schedule) ← `1249f2d` (c007 H1 constructor fix) ← `18d83a6` (c008 H1 paper capacity).
- `fno_coregionalization` is the sole holder of the `ifc_heat` leaderboard at 0.012898 (>2× margin); the rest of the heat leaderboard now derives from this family's residual variants.

## What's still on the table for cycle-009

- **Bar dethrone**: +0.000300 (+1.09%) above the parallel-bench bar (0.027429). The capacity axis is exhausted on `fno_coregionalization` (paper-config is the natural ceiling); the next +1.09% must come from elsewhere — most likely `ifc_poisson` (which this family is 10× behind `fno_mf_stack` on, at 0.5945 vs 0.05961 — but the composite is geomean-weighted, so closing that gap matters at the composite log-weight).
- **`ifc_poisson` lever**: `fno_mf_stack @ 0.05961` is the current poisson winner. A successful poisson reduction by `fno_mf_stack` would directly improve composite; alternatively, getting `fno_coregionalization × ifc_poisson` below `fno_mf_stack`'s 0.05961 would let the same family own both datasets.
- **Operator: precheck overhaul** (5th consecutive request) — `score_direction` polarity for lower-is-better metrics; `scope`/`fixed_surfaces` short-SHA mismatch + empty-detail; the factory's headline disagreed with reality 5 cycles in a row.

## Links

- Project dashboard: [[factory_mffp]]
- Cycle-008 build-phase note (companion): [[cycle-008-exp-11-build]] — paper-config knob list, pre-flight smoke verification, surface guard, leakage scan, CEO PROCEED rationale
- Cycle-008 strategy: [[cycle-008]] — canonical R2 strategy snapshot (H1 > H2 > H3 plan-approved; anti-patterns enumerated)
- Cycle-008 failure analysis: [[failure-analysis-cycle-008]] — `CAPACITY_PARETO` dominant; H1 capacity-axis predicted as primary lever
- CEO verdicts: `.factory/reviews/ceo-verdict-builder.md`, `.factory/reviews/ceo-verdict-reviewer.md`, `.factory/reviews/ceo-verdict-e2e.md`
- R4 summary: `.factory/research/runs/cycle-008-h1/summary.json` — PASS, composite 0.027729, delta -8.81%, bar_gap_closed_pct 89.93
- Parent hypotheses:
  - [[cycle-007-exp-9]] — cycle-007 H1 constructor fix that this capacity bump runs on top of
  - [[factory_mffp-007]] — cycle-005 H2 LF→HF schedule preserved verbatim in this H1
- Source notes inherited (cycle-007 R1.5):
  - [[anisotropic-spectral-modes-fno]] — Li 2020 `(modes_h, modes_w)` carried through `modes_cap=16`
  - [[lf-hf-pretrain-fraction-survey]] — cycle-005 H2 `pretrain_frac=0.25` preserved verbatim
- Cross-cycle patterns: [[patterns]]
- Auto-memory honored: [[dirty-tree-staging]], [[factory-cli-invocation]]
- Branch: `experiment/11-fno_coregionalization-paper-capacity @ 18d83a6` — PRESERVED as cycle-009 entry baseline.
- Diff: `git diff 1249f2d..18d83a6 models/fno_coregionalization/smoke_eval.py` (+10 / -4, 1 file).
