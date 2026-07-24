---
name: cycle-009-exp-14-build
description: Cycle-009 H1+H2 bundle (exp 14) — Builder + CEO PROCEED phase. Single-commit two-hypothesis bundle on `experiment/14-fno_mf_stack-capacity-and-recipe-hash @ 0b6e6eb`, cut from cycle-008 H1 banked best `experiment/11-fno_coregionalization-paper-capacity @ 18d83a6` (clean parent). 5 files / +45/-8 LOC. **H1 scope:** `fno_mf_stack` capacity bump on Poisson side targeting the cycle-009 dominant-lever (Poisson contributes ~69% of remaining composite gap per `failure-analysis-cycle-009`). Four `SMOKE_DEFAULTS` edits at `models/fno_mf_stack/smoke_eval.py`: `hidden 32→64`, `agg_hidden 32→64`, `n_blocks 3→4`, `modes_per_level (4,8,12,12)→(4,8,16,20)`. Loss weights (`poisson_hf_weight=2.0`, `poisson_lf_weight=0.25`) explicitly UNCHANGED — Builder verified the H1 capacity-only carve-out, sidestepping NK3 (MFRNP-style loss-weight tuning forbidden on coregionalization-family from c003/c006/c007 3/3 REVERT history). All other recipe keys unchanged. Mirrors cycle-008 H1 playbook (paper-config capacity bump on `fno_coregionalization`) which closed the Heat dominant-lever. **H2 scope:** `recipe_hash` portable utility cherry-picked from `models/transolver_residual/smoke_eval.py` (canonical in-tree pattern, also matching cycle-008 H3 inline implementation on `fno_coreg_residual`) and promoted to shared `models/_common/recipe_hash.py` (12 LOC, `Mapping[str, Any]` typed, `default=str` for non-JSON-native values, `sha256[:12]` truncation). New empty `models/_common/__init__.py` makes it a package. Helper applied via canonical 4-patch-site refactor to all 3 mutable-surface FNO families (`fno_mf_stack`, `fno_coreg_residual`, `fno_coregionalization`): (A) `sys.path` shim + `from models._common.recipe_hash import recipe_hash` import; (B) `rh = recipe_hash(SMOKE_DEFAULTS)` computed once at top of training entry; (C) resume guard predicate chained with existing per-family checks (`epochs_target` and `cond_dim` on `fno_mf_stack`; `epochs_target` and `cond_dim` and `grid==list(grid)` on `fno_coregionalization` preserving family-specific resume preconditions); (D) `recipe_hash` key added to saved checkpoint dict. **Family recipe hashes after bump:** `fno_mf_stack = acdb1c11caa7` (NEW — invalidates ANY stale cycle-008 cache for this family by construction; intended cache-safety semantic); `fno_coreg_residual = 1cc35377b46d` (SMOKE_DEFAULTS unchanged, hash stable for warm-resume continuity); `fno_coregionalization = 5011def485a6` (SMOKE_DEFAULTS unchanged, hash stable). Surface-constraint check: all 5 files under `models/**` (mutable_surfaces). NO `model.py`, NO `data.py`, NO fixed-surface, NO new family directory (`models/_common/` is a utility package not a family), NO loss-weight perturbation, NO curriculum/freezing. Strictly within H1+H2 carve-out. **Leakage scanner:** `risk_level=medium`, 2 findings — both `"17"` matching diff hunk header `@@ -176,9 +178,10 @@`. **7th-consecutive substring-collision false-positive on PR diff** (project docs `factory.md`/`README.md` contain "17" in unrelated context); NOT actual ground-truth leakage from `data/` or `baselines/`. OVERRIDE per standing operator practice; flagged for cycle-009 close-out operator backlog. **Pre-Builder smoke verification:** 4 smoke runs at 2 epochs all completed without crash (`fno_mf_stack × ifc_heat` nRMSE 0.79, `fno_mf_stack × ifc_poisson` 0.59, `fno_coreg_residual × ifc_heat` 0.57, `fno_coregionalization × ifc_heat` 0.115 — sanity checks only, NOT real evaluation numbers; high values are expected at 2 epochs and confirm pipelines do not crash). Real evaluation will use full `SMOKE_DEFAULTS` epoch budget via `bash scripts/cycle_eval.sh`. CEO PROCEED issued with explicit file:line cross-reference (recipe_hash.py matches research.md §O2 design exactly; H1 capacity edits verified UNCHANGED loss weights). `--no-github` honored — no push, no PR, no issue. Closes cycle-003 backlog `recipe_hash` portability ask for the entire FNO family (after cycle-008 H3 delivered it inline for `fno_coreg_residual` only).
metadata:
  type: experiment
tags:
  - factory
  - experiment
  - factory_mffp
  - cycle-009
  - build
  - h1
  - h2
  - bundle
  - fno_mf_stack
  - fno_coreg_residual
  - fno_coregionalization
  - capacity-bump-poisson
  - recipe-hash-portable-utility
  - meta-fix-cycle-003
  - dominant-lever-poisson
  - nk3-carve-out-loss-weights-unchanged
project: factory_mffp
experiment_id: "014"
cycle: cycle-009
hypothesis_id: H1+H2
phase: build
verdict: PROCEED
ceo_verdict_builder: PROCEED
date: 2026-06-02
source: factory-archivist
branch: experiment/14-fno_mf_stack-capacity-and-recipe-hash
parent_branch: experiment/11-fno_coregionalization-paper-capacity
parent_commit: 18d83a6
parent_commit_source: cycle-008 H1 banked best (paper-config capacity bump on fno_coregionalization)
commit: 0b6e6eb
commit_message: "feat(fno_mf_stack): capacity bump + recipe_hash portable utility (cycle-009 H1+H2)"
files_changed: 5
loc_delta: "+45/-8"
files_changed_list:
  - "models/_common/__init__.py (NEW empty)"
  - "models/_common/recipe_hash.py (NEW +12)"
  - "models/fno_mf_stack/smoke_eval.py (+19/-5 — H1 SMOKE_DEFAULTS + H2 refactor)"
  - "models/fno_coreg_residual/smoke_eval.py (+12/-2 — H2 refactor only)"
  - "models/fno_coregionalization/smoke_eval.py (+10/-1 — H2 refactor only)"
mutable_surfaces_only: true
model_py_edited: false
data_py_edited: false
fixed_surface_edited: false
new_family_directory: false
loss_weights_unchanged: true
loss_weights_explicit_check: "poisson_hf_weight=2.0, poisson_lf_weight=0.25 NOT touched in models/fno_mf_stack/smoke_eval.py"
h1_capacity_edits:
  hidden: "32 → 64"
  agg_hidden: "32 → 64"
  n_blocks: "3 → 4"
  modes_per_level: "(4,8,12,12) → (4,8,16,20)"
h2_recipe_hash_helper_loc: "models/_common/recipe_hash.py:1-13"
h2_recipe_hash_helper_lines: 12
h2_recipe_hash_helper_typing: "Mapping[str, Any]"
h2_recipe_hash_helper_default: "str (handles non-JSON-native values)"
h2_recipe_hash_helper_truncation: "sha256[:12]"
h2_recipe_hash_helper_source: "cherry-picked from models/transolver_residual/smoke_eval.py (canonical in-tree pattern)"
h2_patch_sites_per_family:
  A_import: "sys.path shim + from models._common.recipe_hash import recipe_hash"
  B_compute: "rh = recipe_hash(SMOKE_DEFAULTS) at top of training entry"
  C_resume_guard: "ok_recipe predicate chained with existing per-family resume checks"
  D_save_dict: "recipe_hash key added to saved checkpoint dict"
h2_families_refactored:
  - fno_mf_stack
  - fno_coreg_residual
  - fno_coregionalization
recipe_hash_post_bump:
  fno_mf_stack: "acdb1c11caa7"
  fno_coreg_residual: "1cc35377b46d"
  fno_coregionalization: "5011def485a6"
recipe_hash_fno_mf_stack_new: true
recipe_hash_fno_mf_stack_invalidates_cycle_008_cache: true
recipe_hash_fno_mf_stack_invalidation_intent: "deliberate — H1 capacity bump MUST trigger fresh training, not warm-resume from any stale cycle-008 cache"
recipe_hash_fno_coreg_residual_stable: true
recipe_hash_fno_coregionalization_stable: true
fno_coregionalization_resume_guard_preserves_grid_check: true
fno_coregionalization_resume_guard_chain: "ok_recipe AND ok_epoch AND ok_cond AND sd.get('grid') == list(grid)"
fno_mf_stack_resume_guard_chain: "ok_recipe AND ok_epoch AND ok_cond"
pre_builder_smoke_runs:
  fno_mf_stack_ifc_heat_2ep_nrmse: 0.79
  fno_mf_stack_ifc_poisson_2ep_nrmse: 0.59
  fno_coreg_residual_ifc_heat_2ep_nrmse: 0.57
  fno_coregionalization_ifc_heat_2ep_nrmse: 0.115
pre_builder_smoke_runs_purpose: "sanity-only (no-crash check); 2-epoch nRMSE NOT real evaluation"
leakage_scan_risk_level: medium
leakage_scan_findings_count: 2
leakage_scan_findings_token: "17"
leakage_scan_findings_source: "diff hunk header @@ -176,9 +178,10 @@ — substring-collision with project docs containing '17' in unrelated context"
leakage_scan_false_positive_streak: 7
leakage_scan_override: true
leakage_scan_override_rationale: "standing operator practice — NOT actual ground-truth leakage from data/ or baselines/"
leakage_scan_operator_backlog_item: "cycle-009 close-out — leakage scanner substring tokenization needs upgrade (7-FP streak)"
surface_guard_baseline_sha: "18d83a6"
surface_guard_check_scope: clean
no_github_compliance: true
no_push: true
no_pr: true
no_gh_calls: true
no_issue: true
scope_creep_check: clean
mfrnp_ban_discipline_preserved: true
nk1_pure_m_conditioning_violation: false
nk2_frozen_lf_curriculum_violation: false
nk3_loss_weight_tuning_violation: false
o1_dominant_lever_addressed: true
o2_meta_fix_secondary_addressed: true
cycle_003_backlog_meta_fix: "extends cycle-008 H3 recipe_hash delivery (which was inline-only on fno_coreg_residual) to a portable utility used by 3 families; closes the cycle-003 backlog item project-wide for the FNO family"
next_phase: "Reviewer (factory guard --baseline 18d83a6 --check-scope, PR diff review, code-quality assessment) → Evaluator (bash scripts/cycle_eval.sh on both ifc_heat + ifc_poisson)"
baseline_composite_to_beat: 0.027729
baseline_composite_source: "cycle-008 H1 banked best (fno_coregionalization paper-config capacity bump)"
expected_dominant_attack_cell: "fno_mf_stack × ifc_poisson (cycle-009 baseline 0.05961, +1.5% over bar)"
---

# Build Note: Cycle-009 H1+H2 Bundle (Experiment 14) — fno_mf_stack capacity + recipe_hash portable utility

## Scope

Two-hypothesis bundle in a single commit on `experiment/14-fno_mf_stack-capacity-and-recipe-hash @ 0b6e6eb`, cut from cycle-008 H1 banked best `18d83a6`.

- **H1**: capacity bump on `fno_mf_stack` SMOKE_DEFAULTS (Poisson dominant-lever attack)
- **H2**: `recipe_hash` portable utility (`models/_common/recipe_hash.py`) applied to 3 FNO families

5 files / +45/-8 LOC. CEO Builder verdict: **PROCEED**.

## Files Changed

| File | LOC | Purpose |
|---|---|---|
| `models/_common/__init__.py` | NEW (empty) | makes `_common` a package |
| `models/_common/recipe_hash.py` | NEW +12 | shared helper, cherry-picked from `transolver_residual/smoke_eval.py` |
| `models/fno_mf_stack/smoke_eval.py` | +19/-5 | H1 SMOKE_DEFAULTS + H2 4-patch-site refactor |
| `models/fno_coreg_residual/smoke_eval.py` | +12/-2 | H2 4-patch-site refactor only |
| `models/fno_coregionalization/smoke_eval.py` | +10/-1 | H2 4-patch-site refactor only |

## H1: fno_mf_stack Capacity Bump

Four `SMOKE_DEFAULTS` edits at `models/fno_mf_stack/smoke_eval.py`:

| Key | Before | After |
|---|---|---|
| `hidden` | 32 | 64 |
| `agg_hidden` | 32 | 64 |
| `n_blocks` | 3 | 4 |
| `modes_per_level` | (4,8,12,12) | (4,8,16,20) |

Loss weights (`poisson_hf_weight=2.0`, `poisson_lf_weight=0.25`) **explicitly UNCHANGED** — verified by Builder + CEO. Capacity-only carve-out sidesteps NK3 (MFRNP-style loss-weight tuning forbidden by 3/3 REVERT history on coregionalization-family from c003/c006/c007). Mirrors cycle-008 H1 playbook that closed the Heat dominant-lever.

## H2: recipe_hash Portable Utility — Canonical 4-Patch-Site Refactor

Helper (`models/_common/recipe_hash.py:1-13`, 12 LOC):

```python
def recipe_hash(defaults: Mapping[str, Any]) -> str:
    payload = json.dumps(dict(defaults), sort_keys=True, default=str).encode()
    return hashlib.sha256(payload).hexdigest()[:12]
```

Applied per family (all 3):

- **A — import**: `sys.path` shim + `from models._common.recipe_hash import recipe_hash`
- **B — compute**: `rh = recipe_hash(SMOKE_DEFAULTS)` at top of training entry
- **C — resume guard**: `ok_recipe` predicate chained with existing per-family resume checks (`fno_coregionalization` preserves `sd.get("grid") == list(grid)` family-specific precondition)
- **D — save dict**: `recipe_hash` key added to saved checkpoint dict

## Recipe Hashes After Bump

| Family | Hash | Status |
|---|---|---|
| `fno_mf_stack` | `acdb1c11caa7` | **NEW** — invalidates any stale cycle-008 cache (deliberate; H1 capacity bump must trigger fresh training, not warm-resume) |
| `fno_coreg_residual` | `1cc35377b46d` | stable (SMOKE_DEFAULTS unchanged) |
| `fno_coregionalization` | `5011def485a6` | stable (SMOKE_DEFAULTS unchanged) |

## Leakage Scan — 7th-Consecutive Substring-Collision FP

- `risk_level=medium`, 2 findings, both token `"17"`
- Root cause: diff hunk header `@@ -176,9 +178,10 @@` collides with project-doc occurrences of "17" in unrelated context (`factory.md`/`README.md`)
- NOT actual ground-truth leakage from `data/` or `baselines/`
- CEO override per standing operator practice
- **Operator backlog item (cycle-009 close-out):** leakage scanner substring tokenization needs upgrade — 7-FP streak indicates the scanner is not pulling its weight on PR diffs

## Pre-Builder Smoke Sanity (2-epoch, no-crash only — NOT real evaluation)

- `fno_mf_stack × ifc_heat` 0.79
- `fno_mf_stack × ifc_poisson` 0.59
- `fno_coreg_residual × ifc_heat` 0.57
- `fno_coregionalization × ifc_heat` 0.115

High values expected at 2 epochs; the real numbers come from `bash scripts/cycle_eval.sh` at full `SMOKE_DEFAULTS` epoch budget.

## Compliance

- Surface guard `factory guard --baseline 18d83a6 --check-scope` clean — all 5 files under `models/**`
- No `model.py`, no `data.py`, no fixed-surface, no new family directory, no loss-weight perturbation, no curriculum/freezing
- `--no-github` honored — no push, no PR, no `gh` calls, no issue
- NK1/NK2/NK3 forbidden zones all respected

## Meta-Fix Delivery

Cycle-003 backlog item `recipe_hash` portability extends from cycle-008 H3 (inline-only on `fno_coreg_residual`) to a shared `models/_common/recipe_hash.py` utility used by 3 families — closes the backlog for the FNO family project-wide.

## Links

- Project: factory_mffp
- Cycle: cycle-009
- Parent baseline (commit): 18d83a6 (cycle-008 H1 banked best, composite 0.027729)
- This commit: 0b6e6eb
- Strategy: [[cycle-009-strategy]]
- Failure analysis: [[failure-analysis-cycle-009]]
- Precedent (capacity playbook): [[cycle-008-exp-11-build]]
- Precedent (recipe_hash inline): [[cycle-008-exp-13-build]]
- Next phase: Reviewer → Evaluator (`bash scripts/cycle_eval.sh` on `ifc_heat` + `ifc_poisson`)
