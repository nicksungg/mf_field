---
name: cycle-008-exp-12-review
description: Cycle-008 H2 (exp 12) — Reviewer PASS + CEO PROCEED (R3-review phase) for NEW family `fno_coreg_conditioned` (FiLM-via-LayerNorm on single full-resolution HF FNO). Branch `experiment/12-fno_coreg_conditioned-film @ 540e684` cut independently from cycle-008 entry baseline `1249f2d` (cycle-007 H1 anisotropic-modes constructor fix). Surface guard `factory guard . --baseline 1249f2d --check-scope` PASS (eval_immutable clean, git_clean clean, experiment_branch independence verified, scope clean — 4 NEW files all under `models/fno_coreg_conditioned/`, zero existing-family / fixed-surface edits). FiLMNorm math reviewed and confirmed sound (`GroupNorm(affine=False) + MLP([m, m²]) → 2·C → γ, β` with zero-init γ-projection ⇒ γ ≈ 1, β ≈ 0 at init ⇒ identity FiLM modulation preserves un-conditioned forward pass; `gamma = 1.0 + gamma` is canonical residual-γ pattern). Constructor signature uses **separate kwargs `modes_h: int = 12, modes_w: int = 12`** mirroring cycle-007 H1 `fno_coregionalization/model.py:89-90` AND bar `mf_fno_transfer_bar/model.py:70` verbatim — Strategist R2's "positional modes accepts int or `(modes_h, modes_w)` tuple" language was IMPRECISE about the actual H1-established convention (separate kwargs, not a polymorphic positional arg); Reviewer confirmed the implementation correctly follows the bar's separate-kwargs precedent, no modes-tuple regression risk. H2 schedule preservation verified by diff: `pretrain_lr=1e-3`, `finetune_lr=3e-4`, `pretrain_frac=0.25` byte-identical to `fno_coregionalization/smoke_eval.py:79-81`; fresh-Adam + fresh-CosineAnnealingLR per stage (lines 348-351, 383-386) per lyu2023mffno; resume guard at `smoke_eval.py:304` correctly requires stage==2 AND epoch==epochs_target. SMOKE_DEFAULTS deltas vs cycle-008 H1 baseline sibling verified — K=10 and b_hidden removed, m_feat_dim=32 added, hidden_channels bumped 32→64 (matches bar trunk, deliberately NOT inheriting H1's paper-config 128 — preserves H2-vs-bar isolation of the FiLM mechanism). Leakage scanner: 4 substring-collision findings (`satisfy`, `description`, `ifc_raw`, `frozen`) all confirmed REQUIRED schema fields or generic English (per eval/MODEL_CONTRACT.md schema + research_constraints field 4) — 5th-consecutive bookkeeping false-positive; CEO override documented. No GitHub review posted (no-GitHub mode honored — zero gh calls). CEO PROCEED ratifies Reviewer PASS. Next phase: Evaluator (`factory eval` on both `ifc_heat` + `ifc_poisson`); kill-switches `ifc_heat > 0.0194` OR smoke wall > 25 min → REVERT. Monotonic-check baseline = cycle-008 H1 banked best composite 0.027729 (NOT cycle-008 entry 0.030408).
metadata:
  type: experiment
tags:
  - factory
  - experiment
  - factory_mffp
  - cycle-008
  - review
  - h2
  - fno_coreg_conditioned
  - new-family
  - film-via-layernorm
  - reviewer-pass
  - ceo-proceed
  - leakage-substring-collision-5
  - strategist-language-imprecision
project: factory_mffp
experiment_id: "012"
cycle: cycle-008
hypothesis_id: H2
phase: review
verdict: PROCEED
reviewer_verdict: PASS
ceo_verdict_reviewer: PROCEED
ceo_verdict_reviewer_doc: .factory/reviews/ceo-verdict-reviewer.md
reviewer_output_doc: .factory/reviews/reviewer-latest.md
reviewer_timestamp_utc: 2026-06-02T18:29:13Z
reviewer_exit_code: 0
date: 2026-06-02
branch: experiment/12-fno_coreg_conditioned-film
parent_commit: 1249f2d
parent_commit_source: cycle-007 H1 (anisotropic-modes constructor fix) — cycle-008 entry baseline
commit: 540e684
guard_command: "factory guard . --baseline 1249f2d --check-scope"
guard_eval_immutable: PASS
guard_git_clean: PASS
guard_experiment_branch: PASS
guard_scope: PASS
guard_surface_constraints: PASS
guard_eval_files_touched: 0
guard_score_py_touched: false
guard_factory_md_touched: false
guard_readme_md_touched: false
guard_model_contract_md_touched: false
guard_new_family_dir: models/fno_coreg_conditioned/
guard_new_family_file_count: 4
guard_existing_family_files_modified: 0
guard_branch_independence_from_h1_verified: true
filmnorm_math_review: PASS
filmnorm_zero_init_gamma_projection_verified: true
filmnorm_zero_init_beta_projection_verified: true
filmnorm_identity_at_init: true
filmnorm_residual_gamma_pattern: "gamma = 1.0 + gamma_delta (canonical residual-γ; γ-projection drift accumulates as perturbation around identity)"
constructor_signature_pattern_actual: "separate kwargs modes_h: int = 12, modes_w: int = 12"
constructor_signature_pattern_strategist_described_as: "positional modes accepts int OR (modes_h, modes_w) tuple"
constructor_signature_pattern_strategist_language_imprecise: true
constructor_signature_pattern_actual_convention_source_files: "fno_coregionalization/model.py:89-90 AND mf_fno_transfer_bar/model.py:70"
constructor_signature_pattern_finding_for_cycle_009_strategy_templates: "Strategist language 'positional modes accepts int or tuple' was descriptively wrong about the H1-established convention; actual convention is separate modes_h / modes_w kwargs. Reviewer/Builder correctly followed the file precedent, not the Strategist's literal English. Note for cycle-009+ strategy templates: describe modes API as 'separate modes_h, modes_w int kwargs' not 'positional modes int-or-tuple'."
constructor_signature_pattern_modes_tuple_regression_risk: false
h2_schedule_preserved_verbatim: true
h2_pretrain_lr: 0.001
h2_finetune_lr: 0.0003
h2_pretrain_frac: 0.25
h2_schedule_diff_against_fno_coregionalization_smoke_eval_lines: "79-81"
h2_fresh_adam_per_stage_verified: true
h2_fresh_cosine_per_stage_verified: true
h2_resume_guard_line: 304
h2_resume_guard_requires_stage_2: true
h2_resume_guard_requires_epoch_equals_target: true
smoke_defaults_delta_vs_sibling_K_removed: true
smoke_defaults_delta_vs_sibling_b_hidden_removed: true
smoke_defaults_delta_vs_sibling_m_feat_dim_added: 32
smoke_defaults_delta_vs_sibling_hidden_channels: "32 → 64 (bar trunk, NOT H1's paper-config 128)"
smoke_defaults_hidden_channels_source_rationale: "matches mf_fno_transfer_bar/model.py:69 trunk capacity — isolates FiLM mechanism vs bar's plain FNO; deliberately NOT inheriting cycle-008 H1's paper-config bump"
smoke_2ep_heat_params: 4757121
smoke_2ep_heat_train_seconds: 2.04
smoke_2ep_heat_200ep_projection_min: 3.4
smoke_2ep_poisson_params: 4757249
smoke_2ep_poisson_train_seconds: 1.61
smoke_2ep_poisson_200ep_projection_min: 2.7
smoke_200ep_projection_min_total: 6
smoke_kill_switch_cap_min: 25
smoke_kill_switch_headroom_pct: 76
leakage_scanner_findings_count: 4
leakage_scanner_findings: "satisfy, description, ifc_raw, frozen"
leakage_scanner_all_findings_confirmed_false_positive: true
leakage_scanner_satisfy_classification: "generic English; identical phrasing in README.md"
leakage_scanner_description_classification: "REQUIRED JSON manifest schema field per eval/MODEL_CONTRACT.md"
leakage_scanner_ifc_raw_classification: "REQUIRED by research_constraints field 4 (New families must support at least the ifc_raw dataset loader)"
leakage_scanner_frozen_classification: "REQUIRED JSON manifest schema field"
leakage_substring_collision_consecutive_count: 5
leakage_substring_collision_cycles_005_006_007_008_h1_h2: true
ceo_override_class: revert_bookkeeping_keep_intent_precedent
no_github_mode: true
no_github_review_posted: true
gh_calls: 0
acceptance_criteria_met_new_family_scaffold: true
acceptance_criteria_met_no_existing_family_modified: true
acceptance_criteria_met_filmnorm_first_principles: true
acceptance_criteria_met_mode_a_succeeded: true
acceptance_criteria_met_mode_b_fallback_not_needed: true
acceptance_criteria_met_constructor_anisotropic_modes: true
acceptance_criteria_met_h2_schedule_verbatim: true
acceptance_criteria_met_smoke_both_datasets_verified: true
next_phase: evaluator
next_phase_command: "factory eval (both ifc_heat + ifc_poisson)"
next_phase_kill_switch_heat_threshold: 0.0194
next_phase_kill_switch_smoke_wall_min: 25
next_phase_monotonic_check_baseline_composite: 0.027729
next_phase_monotonic_check_baseline_source: "cycle-008 H1 banked best (experiment/11 @ 18d83a6)"
next_phase_monotonic_check_baseline_NOT_cycle_008_entry: 0.030408
source: factory-archivist
---

# Experiment #012 — Review phase: Cycle-008 H2 NEW family `fno_coreg_conditioned` (FiLM-via-LayerNorm)

## Reviewer verdict

**PASS** — `factory guard . --baseline 1249f2d --check-scope` clean across all four guard checks; FiLMNorm math sound; H2 schedule preserved verbatim; leakage findings demonstrably false-positives (5th-consecutive bookkeeping override).

**CEO verdict on Reviewer**: PROCEED — ratifies Reviewer PASS. Next phase: Evaluator (`factory eval` on both `ifc_heat` + `ifc_poisson`).

## Guard check (independent re-run)

| Guard | Status | Detail |
|---|---|---|
| `eval_immutable` | PASS | no `eval/`, `score.py`, `factory.md`, `README.md`, or `MODEL_CONTRACT.md` touched (git diff name-only verified) |
| `git_clean` | PASS | branch at `experiment/12-fno_coreg_conditioned-film @ 540e684`, baseline `1249f2d` confirmed |
| `experiment_branch` | PASS | branched from cycle-008 entry baseline (cycle-007 H1 commit), **independent of H1's `experiment/11` branch** per Strategist R2 anti-pattern #3 (bundling FORBIDDEN) |
| `scope` | PASS | 4 NEW files all under `models/fno_coreg_conditioned/`, no existing family modified |
| `surface_constraints` | PASS | only NEW family directory created; fixed surfaces untouched |

## Reviewer's code-quality findings

### FiLMNorm math (model.py:84-120) — sound

- `FiLMNorm = GroupNorm(min(8, channels), channels, affine=False) + MLP(Linear(2, m_feat_dim) → GELU → Linear(m_feat_dim, 2·C))` on `[m, m²]` input.
- Final projection weight AND bias zero-init (lines 110-111) → at start γ = 1 + 0 = 1, β = 0 → **identity FiLM modulation, preserves un-conditioned forward pass**. Standard FiLM init.
- `gamma = 1.0 + gamma` parametrization is the canonical "residual γ" pattern — γ-projection drift from zero accumulates as a perturbation around identity, not a multiplicative-from-zero issue.

### Constructor signature — NEW FINDING (Strategist language was imprecise)

The cycle-008 H2 strategy spec described the constructor pattern as "positional `modes` accepts int OR `(modes_h, modes_w)` tuple". Reviewer verified the actual implementation uses **separate kwargs `modes_h: int = 12, modes_w: int = 12`** (model.py:150-159), which:

1. **Matches cycle-007 H1 pattern** at `fno_coregionalization/model.py:89-90` verbatim.
2. **Matches bar `mf_fno_transfer_bar/model.py:70` verbatim** — the original H1-established convention.

The Strategist's "positional modes int-or-tuple" English description was **descriptively wrong** about the actual H1-established convention. The Builder correctly followed the file precedent (separate kwargs) over the Strategist's literal English, and the Reviewer ratified this — no modes-tuple regression risk.

**Lesson for cycle-009+ strategy templates**: when describing the modes API, write "separate `modes_h: int`, `modes_w: int` kwargs (mirror `fno_coregionalization/model.py:89-90`)" — NOT "positional `modes` accepts int or tuple". The file precedent IS the convention; the Strategist's wording should defer to the on-disk pattern. See [[strategist-language-imprecision-modes-kwargs]] (cross-cycle pattern).

### H2 schedule preservation (smoke_eval.py:85-87) — verbatim

- `pretrain_lr=1e-3, finetune_lr=3e-4, pretrain_frac=0.25` — byte-identical to `fno_coregionalization/smoke_eval.py:79-81` (diff confirmed).
- Fresh Adam + fresh `CosineAnnealingLR` per stage (lines 348-351, 383-386) — correct stale-momentum discipline per `lyu2023mffno`.
- Resume guard at line 304 (`# A stage-1-only checkpoint MUST not satisfy this guard`) correctly requires `stage==2 AND epoch==epochs_target` — closes the cycle-003 H1 stage-resume contamination pathway for this family.

### SMOKE_DEFAULTS deltas vs cycle-008 H1 sibling — deliberate isolation

| Field | H1 sibling (`fno_coregionalization`) | H2 (`fno_coreg_conditioned`) | Rationale |
|---|---|---|---|
| `K` | 20 (paper config) | **REMOVED** | No K-basis head — FiLM replaces the outer-product basis |
| `b_hidden` | 128 (paper config) | **REMOVED** | No b_hidden — same reason |
| `m_feat_dim` | — | **32 (added)** | FiLM conditioner input width |
| `hidden_channels` | 128 (paper config) | **64** | matches bar `mf_fno_transfer_bar/model.py:69`, deliberately NOT inheriting H1's paper-config bump → isolates FiLM mechanism vs bar's plain FNO |

The hidden_channels=64 choice is the right comparator baseline: H2 is testing **the FiLM mechanism in isolation** vs the bar's plain FNO trunk, NOT capacity-axis + FiLM-axis bundled. Cycle-009 can do the capacity bump on top if H2 KEEPs.

### Leakage scanner — 4 false positives (5th-consecutive bookkeeping pattern)

| Token | Location | Classification |
|---|---|---|
| `satisfy` | `smoke_eval.py:304` checkpoint-guard comment | Generic English; identical phrasing in README.md |
| `description` | `manifest.json:3` | REQUIRED JSON schema field per `eval/MODEL_CONTRACT.md` |
| `ifc_raw` | `manifest.json:4` | REQUIRED by research_constraint #4 ("New families must support at least the `ifc_raw` dataset loader") |
| `frozen` | `manifest.json:5` | REQUIRED JSON manifest schema field (mirrors sibling) |

All four are demonstrably required schema fields or generic English — NOT ground-truth-derived logic. Consistent with the 5th-consecutive operator-flagged substring-collision pattern (cycles 005 / 006 / 007 / 008-H1). CEO override is validly applied here.

## CEO PROCEED rationale (Reviewer phase)

The CEO ratified Reviewer PASS on these grounds:
1. Reviewer ran the FULL `factory guard --baseline --check-scope` independently (not a rubber-stamp).
2. Reviewer's FiLMNorm math verification is substantive (init analysis, residual-γ pattern recognition) — not a single-line PASS.
3. Reviewer's smoke wall-time check is quantitative (4.76M params × 200 epochs ≈ ~6 min combined ≈ 76% kill-switch headroom).
4. Reviewer **caught and documented the Strategist's imprecise language** about the modes-kwargs convention — institutional-memory contribution beyond rubber-stamp PASS.
5. Reviewer correctly identified the 5th-consecutive substring-collision pattern and applied the documented CEO override.
6. No-GitHub mode honored end-to-end (no PR posted, no push, no issue, no `gh` calls).

## Acceptance criteria — all met

- ✅ NEW family scaffold (no existing family modified)
- ✅ FiLMNorm composes from first principles (FNO backbone + GroupNorm + MLP-driven γ, β affines)
- ✅ Mode A succeeded; no Mode B fallback needed
- ✅ Constructor signature mirrors established H1 anisotropic-modes convention (separate `modes_h`/`modes_w` kwargs)
- ✅ H2 schedule retained verbatim
- ✅ Smoke verified end-to-end on BOTH `ifc_heat` and `ifc_poisson` per research_constraint before declaration

## Next phase — Evaluator

`factory eval` will run on BOTH datasets:
- `ifc_heat` cell (cache MISS — new family)
- `ifc_poisson` cell (cache MISS — new family)
- Other 16 cells (8 existing families × 2 datasets) cache-HIT expected

**Kill-switches (binding at the eval gate)**:
- `ifc_heat` nRMSE > **0.0194** → REVERT (the cycle-008 entry +25% band over the 0.01551 prior heat-cell winner; same threshold as cycle-008 H1).
- Smoke wall-time > **25 min** on first SLURM run → REVERT (architecture too heavy for smoke budget). Projection is ~6 min total — NOT expected to trip.

**Monotonic-check baseline at R5**:
- Use cycle-008 H1 banked best composite **0.027729** (branch `experiment/11 @ 18d83a6`), NOT cycle-008 entry 0.030408. H1 has already CLOSED with `revert_bookkeeping_keep_intent` and is the current banked best.
- Primary win condition for H2: **Poisson leaderboard displacement** (≤ 0.05961 — currently held by `fno_mf_stack`). H1 holds Heat at 0.012898.

**`score_direction` polarity precheck bug**: will likely flip a real composite improvement back to a "+%" regression at R5 (9-of-9 streak through cycle-008 H1); CEO should pre-register the override at H2's R5 entry.

## Links

- Project dashboard: [[factory_mffp]]
- Cycle-008 H2 build-phase companion: [[cycle-008-exp-12-build]]
- Cycle-008 H1 build-phase: [[cycle-008-exp-11-build]] (independent branch `experiment/11`)
- Cycle-008 H1 R4/R5 outcome: [[cycle-008-exp-11]] — banked composite 0.027729 (this H2's monotonic baseline)
- Cycle-008 strategy: [[cycle-008]] — R2 plan-approved snapshot
- Cycle-008 failure analysis: [[failure-analysis-cycle-008]]
- Reviewer report: `.factory/reviews/reviewer-latest.md` (2026-06-02T18:29:13Z, exit 0)
- CEO verdict on Reviewer: `.factory/reviews/ceo-verdict-reviewer.md`
- CEO verdict on Builder (prior): `.factory/reviews/ceo-verdict-builder.md`
- Strategy snapshot driving H2: `.factory/strategy/current.md`
- Parent baseline: `1249f2d` (cycle-007 H1 anisotropic-modes constructor fix)
- Current branch HEAD: `540e684` on `experiment/12-fno_coreg_conditioned-film`
- Cross-cycle patterns: [[patterns]]
  - §"`revert_bookkeeping_keep_intent` is the universal verdict — substring-collision precheck bug gates every eval" (5th consecutive Builder/Reviewer phase override)
  - §"`paper-config wire-up on a freshly-repaired constructor`" (H1 sibling exemplar)
  - **NEW**: §"Strategist language imprecision on modes-kwargs convention" — captured this cycle
- Auto-memory honored: [[dirty-tree-staging]], [[factory-cli-invocation]]
