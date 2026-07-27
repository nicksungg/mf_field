---
name: cycle-008-exp-13-build
description: Cycle-008 H3 (exp 13) — Builder + CEO PROCEED + Reviewer PASS + CEO PROCEED-ratify phase. Three-stage curriculum on `fno_coreg_residual` (S1 LF pretrain → S2 HF residual on frozen LF → S3 unfreeze-all) with MANDATORY `recipe_hash` checkpoint guard that delivers the cycle-003 backlog meta-fix. Branch `experiment/13-fno_coreg_residual-three-stage @ 420a51c` cut independently from cycle-008 entry baseline `1249f2d` (per Strategist R2 anti-pattern #3 — H1/H2/H3 independent code paths; not chained on H1's `experiment/11` or H2's `experiment/12`). Single-file mutable surface: `models/fno_coreg_residual/smoke_eval.py` (+401/-73 LOC) — `model.py` BYTE-IDENTICAL to baseline (BasisHead K=10 zero-init unchanged). Three-stage curriculum with strides `(0.25, 0.5, 0.25)` of `args.epochs`: S1 LF FNOs + LF decoders train on LF-only batches (`active_levels=list(range(0, hf_level))`, level<hf), `pretrain_lr=1e-3`, BasisHead frozen via `_set_basis_grad(False)`; S2 LF stack frozen via `_set_lf_stack_grad(False)` (ACTUAL `requires_grad=False`, NOT zero-loss masking — cycle-005 footgun avoided), HF FNO + HF decoder + aggregator + h_proj train, `finetune_lr=3e-4`, BasisHead still frozen; S3 `_set_lf_stack_grad(True) + _set_basis_grad(True)` — all params trainable at `lr=9e-5` (= `finetune_lr × 0.3` per cycle-003 BasisHead instability prior). Fresh `Adam` + fresh `CosineAnnealingLR` constructed inside `_train_stage` per stage (stale-momentum discipline per `lyu2023mffno`). Trainable-param gating verified: S1=9.115M / S2=3.561M / S3=9.120M; S1−S2 delta=5.554M ≈ LF stack params (FNOs[0..n_lf-1] + decoders[0..n_lf-1] per `model.py:227,236`); S3−S1 delta≈0.005M = BasisHead (K=10, b_hidden=64). MFRNP-ban discipline preserved across all 3 stages: `SMOKE_DEFAULTS` (lines 99-101) keeps `hf_loss_weight=1.0`, `lf_loss_weights=(1.0,1.0,1.0)`, `agg_anchor_weight=0.5` UNIFORM; `p` dict (line 403) = `dict(SMOKE_DEFAULTS)` is NEVER mutated per stage — `_train_stage` reads `p["lf_loss_weights"]`, `p["hf_loss_weight"]`, `p["agg_anchor_weight"]` unchanged across S1/S2/S3 (lines 178, 195). No HF=2.0 / LF=0.25 literal anywhere outside docstring-as-WARNING-on-ban (lines 16, 30). 4th-attempt-of-banned-recipe AVERTED — critical correctness check for H3. **`recipe_hash` checkpoint guard IMPLEMENTED AND LIVE-VERIFIED:** `_compute_recipe_hash` (lines 113-123) = `sha256(json.dumps({**SMOKE_DEFAULTS, "stage_strides":[0.25,0.5,0.25]}, sort_keys=True).encode()).hexdigest()[:16]` — exact spec formula. Persisted in every `_save_last` (line 495) AND `best.pt` (line 505). Resume gate (lines 461-485) requires `ok_recipe AND ok_stage AND ok_epoch AND ok_target AND ok_cond` (line 466). Builder ran live deliberate-mismatch test (mutated `pretrain_lr`): stale ckpt produces `[resume] REJECTED stale checkpoint: recipe_hash '148a2641b07fe5da' != '0095c3ff614e17b8'` and fresh training starts. Closes the cycle-003 H1 stage-resume-contamination pathway (SLURM 13973868 33s "train" via stale resume vs SLURM 13974837 549s clean rerun — same recipe, different result) for ALL future research-mode experiments on this family. **Kill-switch instrumented:** `stage2_final_hf_test_nrmse` (HF test nRMSE measured once at end of Stage 2 via `_eval_test_hf_nrmse` lines 269-287, 571-574) recorded in checkpoint (line 498) AND surfaced in result JSON (line 650). Mechanically comparable to the final returned `metric_value`. End-to-end smoke verified on BOTH `ifc_heat` AND `ifc_poisson` at `--epochs 2` (S1=0/S2=1/S3=1, ~4-5s wall) AND `--epochs 4` (S1=1/S2=2/S3=1, all stages activate). Projected ~6 min total smoke wall at 200 epochs on H100 (same as the prior single-stage `fno_coreg_residual` run, redistributed). No capacity bump (SMOKE_DEFAULTS `hidden_channels`, `n_blocks`, `K`, `modes_cap` unchanged). Surface guard: `factory guard . --baseline 1249f2d --check-scope` → clean; `git diff --name-only 1249f2d..420a51c` → exactly 1 file. Reviewer issued **PASS** with thorough line-by-line verification at file:line precision (every acceptance check cross-referenced); CEO ratified **PROCEED** independently confirming guard clean + 1-file diff + empty `model.py` diff. Leakage scanner expected to flag substring-collision false-positives (`ifc_raw`, `frozen`, `2.0`, `0.25`) — all confirmed benign by Reviewer (generic dataset family name, standard English describing `requires_grad=False`, docstring-as-WARNING on banned MFRNP recipe, `STAGE_STRIDES=[0.25,0.5,0.25]` constant — none are loss-weight literals). One non-blocking Stage-1 observation by Reviewer: HF FNO/decoder/aggregator/h_proj are explicitly set `requires_grad=True` in S1 even though `active_levels` excludes HF — benign (Adam with `zero_grad(set_to_none=True)` skips no-grad params; weight_decay does not drift them) but slightly inflates reported "trainable" count vs params that actually train. **META-FIX DELIVERY:** cycle-003 backlog item "fix checkpoint-resume contamination via recipe_hash guard" is SHIPPED as a side-effect of H3 — meta-validity improvement for ALL future research-mode experiments on this family. `--no-github` honored (no push, no PR, no `gh` calls, no issue). Next phase: Evaluator (`factory eval` / `bash scripts/cycle_eval.sh` on BOTH `ifc_heat` + `ifc_poisson`). Kill-switches enforced at R5: `ifc_heat > 0.0194` OR Stage 3 final Heat > 1.25 × `stage2_final_hf_test_nrmse` → REVERT. Monotonic-check baseline = cycle-008 H1 banked best composite **0.027729** (UNCHANGED by H2 GENUINE REVERT).
metadata:
  type: experiment
tags:
  - factory
  - experiment
  - factory_mffp
  - cycle-008
  - build
  - review
  - h3
  - fno_coreg_residual
  - three-stage-curriculum
  - recipe-hash-guard
  - meta-fix-cycle-003
  - lyu2023mffno
  - niu2024mfrnp
  - li2022ifc
  - yang2025mfdeeponet
  - engstruct2025mfft
project: factory_mffp
experiment_id: "013"
cycle: cycle-008
hypothesis_id: H3
phase: build_and_review
verdict: PROCEED
ceo_verdict_builder: PROCEED
ceo_verdict_reviewer: PROCEED
reviewer_verdict: PASS
date: 2026-06-02
branch: experiment/13-fno_coreg_residual-three-stage
parent_branch: cycle-008-entry-baseline
parent_commit: 1249f2d
parent_commit_source: cycle-007 H1 (anisotropic-modes constructor fix)
branch_independence_from_h1_h2: true
branch_independence_note: "branched from 1249f2d independent of H1's experiment/11 branch AND H2's experiment/12 branch per Strategist R2 §3 anti-pattern #3 — H1/H2/H3 must be independent code paths"
commit: 420a51c
commit_message: "feat(fno_coreg_residual): three-stage curriculum + recipe_hash checkpoint guard (cycle-008 H3)"
files_changed: 1
files_changed_loc_total: 474
files_changed_loc_delta: "+401/-73"
mutable_surface: models/fno_coreg_residual/smoke_eval.py
mutable_surface_count: 1
model_py_byte_identical_to_baseline: true
model_py_byte_identical_verification: "git diff 1249f2d..420a51c -- models/fno_coreg_residual/model.py is empty"
basis_head_unchanged: true
basis_head_location: models/fno_coreg_residual/model.py:43-188
three_stage_curriculum_implemented: true
stage_strides: "[0.25, 0.5, 0.25]"
stage_1_lf_pretrain: true
stage_1_stride: 0.25
stage_1_lr: 0.001
stage_1_active_levels: "list(range(0, hf_level))"
stage_1_basis_grad: false
stage_1_lf_stack_grad: true
stage_1_trainable_params_M: 9.115
stage_2_hf_residual_frozen_lf: true
stage_2_stride: 0.5
stage_2_lr: 0.0003
stage_2_basis_grad: false
stage_2_lf_stack_grad: false
stage_2_lf_freeze_mechanism: "actual requires_grad=False via _set_lf_stack_grad (lines 130-137), NOT zero-loss masking"
stage_2_cycle_005_footgun_avoided: true
stage_2_trainable_params_M: 3.561
stage_3_unfreeze_all: true
stage_3_stride: 0.25
stage_3_lr: 0.00009
stage_3_lr_rationale: "finetune_lr × 0.3 per cycle-003 BasisHead instability prior"
stage_3_basis_grad: true
stage_3_lf_stack_grad: true
stage_3_trainable_params_M: 9.120
param_gating_delta_S1_minus_S2_M: 5.554
param_gating_delta_S1_minus_S2_interpretation: "≈ LF stack params (FNOs[0..n_lf-1] + decoders[0..n_lf-1])"
param_gating_delta_S3_minus_S1_M: 0.005
param_gating_delta_S3_minus_S1_interpretation: "= BasisHead (K=10, b_hidden=64)"
fresh_optimizer_per_stage: true
fresh_scheduler_per_stage: true
optimizer: Adam
scheduler: CosineAnnealingLR
stale_momentum_discipline_citation: lyu2023mffno
mfrnp_ban_preserved_across_all_3_stages: true
hf_loss_weight: 1.0
lf_loss_weights: "(1.0, 1.0, 1.0)"
agg_anchor_weight: 0.5
p_dict_immutable_per_stage: true
p_dict_construction_line: 403
p_dict_construction: "dict(SMOKE_DEFAULTS)"
banned_recipe_hf_2_0_lf_0_25_literal_anywhere: false
banned_recipe_4th_attempt_averted: true
docstring_as_warning_on_ban: true
docstring_warning_lines: "16, 30"
recipe_hash_guard_implemented: true
recipe_hash_guard_live_verified: true
recipe_hash_function: "_compute_recipe_hash (lines 113-123)"
recipe_hash_formula: 'sha256(json.dumps({**SMOKE_DEFAULTS, "stage_strides":[0.25,0.5,0.25]}, sort_keys=True).encode()).hexdigest()[:16]'
recipe_hash_persisted_last_pt: true
recipe_hash_persisted_last_pt_line: 495
recipe_hash_persisted_best_pt: true
recipe_hash_persisted_best_pt_line: 505
resume_gate_clauses: "ok_recipe AND ok_stage AND ok_epoch AND ok_target AND ok_cond"
resume_gate_line: 466
resume_rejection_log_line: 485
recipe_hash_live_test_stale_hash: "148a2641b07fe5da"
recipe_hash_live_test_current_hash: "0095c3ff614e17b8"
recipe_hash_live_test_mutated_field: pretrain_lr
recipe_hash_live_test_outcome: "stale checkpoint REJECTED, fresh training started"
meta_fix_cycle_003_backlog_item_shipped: true
meta_fix_cycle_003_backlog_item_description: "fix checkpoint-resume contamination via recipe_hash guard"
meta_fix_failure_mode_closed: "cycle-003 H1 SLURM 13973868 33s stale-resume vs SLURM 13974837 549s clean rerun contamination"
meta_validity_improvement_scope: "all future research-mode experiments on fno_coreg_residual family"
kill_switch_instrumented: true
kill_switch_marker_field: stage2_final_hf_test_nrmse
kill_switch_marker_computed_via: "_eval_test_hf_nrmse (lines 269-287, 571-574)"
kill_switch_marker_persisted_checkpoint_line: 498
kill_switch_marker_surfaced_result_json_line: 650
kill_switch_h3_specific_threshold: "Stage 3 final Heat > 1.25 × stage2_final_hf_test_nrmse → REVERT to Stage 2"
kill_switch_universal_threshold: "ifc_heat > 0.0194 → REVERT"
smoke_2ep_dataset_heat: ifc_heat
smoke_2ep_dataset_poisson: ifc_poisson
smoke_2ep_stage_distribution: "S1=0 / S2=1 / S3=1"
smoke_2ep_wall_seconds: "4-5"
smoke_4ep_stage_distribution: "S1=1 / S2=2 / S3=1"
smoke_4ep_all_stages_activate: true
smoke_200ep_projection_min_total: 6
smoke_200ep_capacity_bump: false
smoke_200ep_capacity_unchanged_fields: "hidden_channels, n_blocks, K, modes_cap"
surface_guard_baseline: 1249f2d
surface_guard_check_scope: clean
surface_guard_diff_name_only_file_count: 1
surface_guard_model_py_diff_empty: true
surface_guard_fixed_surfaces_touched: false
surface_guard_existing_family_files_touched: false
leakage_check_diff_flagged_expected: true
leakage_check_diff_findings_expected: "ifc_raw, frozen, 2.0, 0.25"
leakage_check_diff_findings_disposition: "all benign — generic dataset family name (ifc_raw), standard English describing requires_grad=False (frozen), docstring-as-WARNING on banned MFRNP recipe (2.0, 0.25), STAGE_STRIDES=[0.25,0.5,0.25] constant (0.25)"
leakage_check_substring_collision_consecutive_count: 6
reviewer_non_blocking_observation: "Stage-1 HF FNO/decoder/aggregator/h_proj explicitly set requires_grad=True even though active_levels excludes HF — benign (Adam zero_grad(set_to_none=True) skips no-grad params; weight_decay does not drift them) but slightly inflates reported 'trainable' count"
no_github_mode: true
no_pr_created: true
no_push: true
no_issue_created: true
gh_calls: 0
git_push_calls: 0
cycle_008_h1_status_at_h3_build: closed_kept_banked_best_0_027729
cycle_008_h2_status_at_h3_build: closed_genuine_revert
cycle_008_entry_baseline_for_h3_monotonic_check: 0.027729
cycle_008_entry_baseline_source: "cycle-008 H1 banked best (experiment/11 @ 18d83a6); unchanged by H2 GENUINE REVERT"
citations: "niu2024mfrnp (residual-stack template), lyu2023mffno (LF→HF schedule + stale-momentum discipline), li2022ifc (basis head), yang2025mfdeeponet (freeze-trunk-fine-tune-merge-net staged training precedent), engstruct2025mfft (pretrain-finetune NO for multi-fidelity surrogate of structural dynamic systems)"
source: factory-archivist
---

# Experiment #013 — Build + Review phase: Cycle-008 H3 three-stage curriculum on `fno_coreg_residual` + `recipe_hash` checkpoint guard

## Hypothesis

**Cycle-008 H3 — EXPLOIT (Heat side) + EXPLORE (composition novel for this family), MEDIUM priority (rank 3).** Compose three independent curriculum stages on `models/fno_coreg_residual/`:

1. **Stage 1 (LF pretrain, stride 0.25):** train per-fidelity LF FNOs on LF-only samples at `pretrain_lr=1e-3`, fresh Adam + cosine, uniform loss weights (do NOT introduce MFRNP HF=2.0/LF=0.25 — the banned lever).
2. **Stage 2 (HF residual fine-tune, stride 0.5):** freeze LF stack via actual `requires_grad=False`, train HF FNO residual at `finetune_lr=3e-4`, fresh Adam + cosine, BasisHead remains zero-init and frozen.
3. **Stage 3 (basis-head unfreeze, stride 0.25):** unfreeze BasisHead AND LF stack, train all parameters at `9e-5` (= `finetune_lr × 0.3` per cycle-003 BasisHead instability prior), fresh Adam + cosine.

Exploits BOTH the `TRANSFER_SIGNAL_UNUSED` lever on `fno_coreg_residual × ifc_heat` (H2 schedule not yet applied to this family) AND the basis-head expressivity lever, without touching MFRNP loss weights.

**MANDATORY recipe_hash checkpoint guard** — hash `{**SMOKE_DEFAULTS, "stage_strides":[0.25,0.5,0.25]}` (sorted keys) as `sha256(...).hexdigest()[:16]`; write into every `last.pt` + `best.pt`; resume guard requires `recipe_hash == current AND stage==3 AND epoch==epochs_target AND cond_dim match`. Without this guard, H3 inherits the cycle-003 H1 stage-resume contamination failure mode (SLURM 13973868: 33 s "train" via stale resume vs SLURM 13974837: 549 s clean rerun, same recipe but different result).

**Expected impact (per cycle-008 Strategist R2):**
- `ifc_heat`: 0.02628 → 0.018-0.022 (Stage 2 frozen-LF fine-tune closes ~15-30% to bar; Stage 3 basis-head adds fine-grained m-modulation).
- `ifc_poisson`: 0.07419 → 0.05-0.06 (recovers cycle-005's 0.05556 paper-recipe number OR better; matches `fno_mf_stack` 0.05961 at parity).
- Composite: baseline 0.030408 → ~0.029-0.033 (geomean of Heat ~0.020 × Poisson ~0.055).

**Citations:** `niu2024mfrnp` (residual-stack template), `lyu2023mffno` (LF→HF schedule + stale-momentum discipline), `li2022ifc` (basis head), `yang2025mfdeeponet` (freeze-trunk-fine-tune-merge-net staged training precedent), `engstruct2025mfft` (pretrain-finetune NO for multi-fidelity surrogate of structural dynamic systems, ScienceDirect S0141029625016098).

## Branch + commit

- **Branch**: `experiment/13-fno_coreg_residual-three-stage`.
- **Base**: `1249f2d` directly (cycle-008 entry baseline — cycle-007 H1 anisotropic-modes constructor fix). **Branched independently of `experiment/11-fno_coregionalization-paper-capacity` (H1) AND `experiment/12-fno_coreg_conditioned-film` (H2)** per Strategist R2 §3 anti-pattern #3 — H1/H2/H3 mandated to be independent code paths off the same baseline, evaluable and keep/revertable on their own evidence without bundling-induced confounders.
- **Single new commit**: `420a51c` — `feat(fno_coreg_residual): three-stage curriculum + recipe_hash checkpoint guard (cycle-008 H3)`.
- **Chain**: `1249f2d` (c007 H1 constructor fix; cycle-008 entry baseline) ← `420a51c` (this H3). H3's `fno_coreg_residual` family is untouched at `1249f2d` baseline; H3 ships the three-stage curriculum + recipe_hash guard into that family's `smoke_eval.py` for the first time.
- **GitHub**: no PR, no push (`--no-github` honored — zero `gh` calls, zero `git push` calls).
- **Cycle-008 status at H3 build**: H1 CLOSED with banked best composite **0.027729** (cycle-009 entry baseline; UNCHANGED by H2 GENUINE REVERT); H2 CLOSED at GENUINE REVERT (architecture-falsified on Poisson; first genuine architecture-falsified revert since cycle-006 H1 / cycle-007 H2). H3 is the third and final cycle-008 hypothesis.

## What the Builder produced

`git diff --stat 1249f2d 420a51c`:

| File | Lines | Purpose |
|---|---:|---|
| `models/fno_coreg_residual/smoke_eval.py` | **+401 / −73** | Three-stage curriculum (`_train_stage` helper; `_set_basis_grad` and `_set_lf_stack_grad` freeze/unfreeze helpers at lines 130-137); recipe_hash checkpoint guard (`_compute_recipe_hash` at lines 113-123; resume gate at lines 461-485; persist at lines 495, 505); kill-switch instrumentation (`stage2_final_hf_test_nrmse` via `_eval_test_hf_nrmse` lines 269-287, 571-574, persisted to checkpoint line 498 + result JSON line 650); STAGE_STRIDES constant at line 110. |
| **Total** | **+401 / −73, 1 file** | Single-file mutable surface; `model.py` BYTE-IDENTICAL to baseline |

**`model.py` BYTE-IDENTICAL to baseline** — verified by CEO: `git diff 1249f2d..420a51c -- models/fno_coreg_residual/model.py` is empty. The `BasisHead` (K=10 with zero-init) at `models/fno_coreg_residual/model.py:43-188` is unchanged.

**All other surfaces byte-preserved against `1249f2d`** (per Strategist R2 anti-pattern #3 — H1/H2/H3 must be independent branches with zero file overlap):
- `models/fno_coregionalization/**` — UNTOUCHED.
- `models/fno_coreg_conditioned/**` — does not exist on this branch (H2's NEW family lives on `experiment/12` only).
- `models/fno_mf_stack/**` — UNTOUCHED.
- `models/mf_fno_transfer_bar/**` — UNTOUCHED.
- `models/transolver/**`, `models/transolver_lite/**` — UNTOUCHED.
- `eval/**`, `data/**`, `baselines/**`, `references/**`, `scripts/**`, `factory.md`, `README.md` — UNTOUCHED.

## Three-stage curriculum verification (Reviewer line-by-line at file:line precision)

### Stage 1 — LF pretrain (lines 509-538)

- `_set_basis_grad(False)` (line 512) freezes BasisHead.
- `_set_lf_stack_grad(True)` (line 513) trains LF FNOs + LF decoders.
- HF FNO + HF decoder + aggregator + h_proj are explicitly set `requires_grad=True` (lines 514-521) — Reviewer non-blocking note: even though `active_levels = list(range(0, hf_level))` (line 527) excludes HF from supervision, the trainable flag is set True. Benign because `compute_losses` returns None for `b_hf` so HF params receive no gradient; Adam with `zero_grad(set_to_none=True)` skips no-grad params; weight_decay does not drift them. Documents the architectural intent (HF stack alive for downstream stages) but slightly inflates the reported "trainable" count vs the params that actually train.
- Fresh `Adam(trainable, lr=pretrain_lr=1e-3)` + fresh `CosineAnnealingLR` constructed inside `_train_stage` (lines 327-330).
- Trainable param count: **S1 = 9.115M** (everything but BasisHead).

### Stage 2 — HF residual on frozen LF (lines 541-578)

- `_set_lf_stack_grad(False)` (line 545) — **ACTUAL `requires_grad=False`** on LF FNO + LF decoder params via `_set_lf_stack_grad` helper (lines 130-137). **NOT zero-loss masking — the cycle-005 footgun is correctly avoided.** Zero-loss masking still allows Adam moment buffers and weight_decay to drift LF params, which was a documented cycle-005 footgun. H3 implements the correct freeze discipline.
- `_set_basis_grad(False)` (line 546) keeps basis frozen.
- HF stack only trains: HF FNO, HF decoder, aggregator, h_proj.
- Fresh `Adam(trainable, lr=finetune_lr=3e-4)` + fresh `CosineAnnealingLR` (NOT continued from S1 — stale-momentum discipline per `lyu2023mffno`).
- Trainable param count: **S2 = 3.561M** (HF stack only).

### Stage 3 — unfreeze-all (lines 580-608)

- `_set_lf_stack_grad(True)` (line 583) AND `_set_basis_grad(True)` (line 584) — everything trainable.
- All params trainable at `lr = finetune_lr × 0.3 = 9e-5` per cycle-003 BasisHead instability prior.
- Fresh `Adam(trainable, lr=9e-5)` + fresh `CosineAnnealingLR`.
- Trainable param count: **S3 = 9.120M** (everything).

### Param-gating delta sanity

- **S1 − S2 = 5.554M ≈ LF stack params** (FNOs[0..n_lf-1] + decoders[0..n_lf-1] per `model.py:227,236`). The freeze helper at lines 130-137 walks exactly those.
- **S3 − S1 ≈ 0.005M = BasisHead** (K=10, b_hidden=64). Consistent with model.py structure.

## MFRNP-ban verification (Reviewer)

- `SMOKE_DEFAULTS` (lines 99-101): `hf_loss_weight=1.0`, `lf_loss_weights=(1.0, 1.0, 1.0)`, `agg_anchor_weight=0.5` — UNIFORM, exactly as the cycle-007 baseline.
- `p` dict (line 403) is `dict(SMOKE_DEFAULTS)` and is **NEVER mutated per stage** — `_train_stage` reads `p["lf_loss_weights"]`, `p["hf_loss_weight"]`, `p["agg_anchor_weight"]` unchanged across S1/S2/S3 (lines 178, 195).
- No HF=2.0 / LF=0.25 literal anywhere outside docstring-as-WARNING about the banned MFRNP recipe (lines 16, 30).
- **4th-attempt-of-banned-recipe AVERTED** — critical correctness check for H3. Anti-pattern #1 + #2 satisfied.

## `recipe_hash` checkpoint guard — implemented AND live-verified

### Implementation

```python
# Lines 113-123
def _compute_recipe_hash() -> str:
    payload = {**SMOKE_DEFAULTS, "stage_strides": [0.25, 0.5, 0.25]}
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True).encode()
    ).hexdigest()[:16]
```

- Persisted in every `_save_last` (line 495) AND `best.pt` (line 505) as `recipe_hash` field.
- Resume gate (lines 461-485) requires `ok_recipe AND ok_stage AND ok_epoch AND ok_target AND ok_cond` (line 466).
- Rejection log at line 485 prints `recipe_hash {sd['recipe_hash']!r} != {recipe_hash!r}`.

### Live verification

Builder ran a deliberate-mismatch test (mutated `pretrain_lr`):

```
[resume] REJECTED stale checkpoint: recipe_hash '148a2641b07fe5da' != '0095c3ff614e17b8'
```

Then fresh training starts from epoch 0. Reviewer cross-referenced the Builder's documented log line to the code at line 485 — exact match.

### Meta-fix delivery — cycle-003 backlog item SHIPPED

This guard closes the cycle-003 H1 stage-resume-contamination pathway:

- SLURM 13973868 (cycle-003 H1): 33 s "train" via stale resume — same hash, same target epoch, but altered recipe.
- SLURM 13974837 (cycle-003 H1 clean rerun): 549 s — same recipe, fresh from epoch 0, different (real) result.

The cycle-003 backlog item literally reads: *"Fix checkpoint-resume contamination in models/<family>/smoke_eval.py: the current resume guard (epoch == epochs_target AND cond_dim match) ignores changes to the training recipe ... Required fix: hash the SMOKE_DEFAULTS dict (or a stable recipe-fingerprint of {loss kwargs, optimizer kwargs, scheduler kwargs, seed-affecting code path}) and include it in the saved checkpoint as a 'recipe_hash' field; the resume guard must additionally require recipe_hash == current_recipe_hash."*

**This is SHIPPED as a side-effect of H3.** Meta-validity improvement for ALL future research-mode experiments on the `fno_coreg_residual` family — the 33s-stale-resume-vs-549s-clean-rerun contamination failure mode is closed.

## Kill-switch instrumentation

- `stage2_final_hf_test_nrmse` computed via `_eval_test_hf_nrmse` (lines 269-287, 571-574) after Stage 2 completes — same HF-test-nRMSE metric as the orchestrator's `primary_metric` (lines 635, 639). "Look but don't act" — kill-switch check happens at R5 finalize, not at training time.
- Stored in `_save_last` checkpoint (line 498) AND surfaced in result JSON (line 650).
- Stage-3 final Heat nRMSE comparison is **mechanically reproducible** at R5 from the recorded JSON fields.

### Thresholds enforced at R5

- **H3-specific**: Stage 3 final Heat > `1.25 × stage2_final_hf_test_nrmse` → REVERT to Stage 2.
- **Universal**: `ifc_heat` nRMSE > 0.0194 → REVERT (same threshold as H1's kill-switch; +25% over current 0.01551 leaderboard).

## End-to-end smoke verification — PASS on BOTH datasets

Builder ran the mandatory smoke check per research-constraint ("New-family changes must be verified end-to-end on `ifc_raw`") on **both** datasets:

| `--epochs` | dataset | stage distribution | wall (s) |
|---:|---|---|---:|
| 2 | `ifc_heat` | S1=0 / S2=1 / S3=1 | ~4-5 |
| 2 | `ifc_poisson` | S1=0 / S2=1 / S3=1 | ~4-5 |
| 4 | `ifc_heat` | S1=1 / S2=2 / S3=1 (all stages activate) | ~8-10 |
| 4 | `ifc_poisson` | S1=1 / S2=2 / S3=1 (all stages activate) | ~8-10 |

- Stride flooring `int(round(0.25 * 2)) = 0` for S1 at `--epochs 2` — acceptable smoke (S2 + S3 still execute). The stage-budget split code (lines 441-443) reproduces these numbers.
- At `--epochs 4`, all three stages activate (S1=1, S2=2, S3=1) — confirms full curriculum composes.
- Projected ~6 min total smoke wall at 200 epochs on H100 — same as the prior single-stage `fno_coreg_residual` run, redistributed across the three stages. No capacity bump.

**No capacity bump:** `SMOKE_DEFAULTS` values for `hidden_channels`, `n_blocks`, `K`, `modes_cap` are unchanged. H3 isolates the curriculum mechanism vs the current single-stage `fno_coreg_residual` baseline.

## Hard-gate results

### CEO verdict on Builder (`.factory/reviews/ceo-verdict-builder.md`)

**PROCEED.** No issues found.

- Surface guard: `factory guard . --baseline 1249f2d --check-scope` → clean. `git diff --name-only 1249f2d..420a51c` → exactly 1 file (`models/fno_coreg_residual/smoke_eval.py`, +401/-73). `git diff 1249f2d..420a51c -- models/fno_coreg_residual/model.py` empty.
- Diff matches hypothesis exactly. Three-stage curriculum implemented per spec; recipe_hash guard implemented per spec AND live-verified.
- Trainable-param gating verified: S1=9.115M / S2=3.561M / S3=9.120M. Deltas consistent with LF stack + BasisHead structure.
- No-GitHub mode honored (no push, no PR, no issue).
- Implementation additionally delivers the cycle-003 `recipe_hash` backlog item as a side-effect — meta-validity improvement for all future research-mode experiments on this family.

### Reviewer verdict (`.factory/reviews/reviewer-latest.md`)

**PASS (KEEP).** Reviewer issued thorough line-by-line verification at file:line precision — every acceptance check cross-referenced to a specific line in `models/fno_coreg_residual/smoke_eval.py`. Not a rubber-stamp.

- Guard check: PASS (eval_immutable, git_clean, experiment_branch, scope, surface_constraint all PASS).
- Three-stage gate verification: PASS (S1 / S2 / S3 all verified at exact line numbers).
- MFRNP-ban verification: PASS (4th-attempt-of-banned-recipe averted).
- recipe_hash guard verification: PASS (formula exact-match to spec, persisted in last.pt + best.pt, resume gate clauses verified, rejection log matches Builder's live test).
- Kill-switch instrumentation: PASS (`stage2_final_hf_test_nrmse` recorded; Stage-3 comparison mechanically reproducible).
- Param-gating sanity: PASS (S1/S2/S3 deltas consistent with LF stack + BasisHead structure).
- End-to-end smoke: PASS (both `ifc_heat` and `ifc_poisson` at `--epochs 2` and `--epochs 4`).
- Leakage scanner: false-positive substring collisions disposed (see below).

One non-blocking note: Stage-1 explicit `requires_grad=True` on HF stack (see Stage 1 description above) — benign, documents architectural intent, slightly inflates reported "trainable" count.

### CEO verdict on Reviewer (`.factory/reviews/ceo-verdict-reviewer.md`)

**PROCEED (ratify Reviewer PASS).** CEO independently confirmed guard clean, 1-file diff, empty `model.py` diff. Added findings beyond Builder's self-report:

1. Stage-1 trainable-flag note (non-blocking, see above) — worth noting for cycle-009 if param-count reporting is used as additional sanity check.
2. Stage-2 freeze discipline (cycle-005 footgun avoided) — Reviewer verified `_set_lf_stack_grad(False)` is ACTUAL `requires_grad=False`, NOT zero-loss masking.
3. MFRNP ban verification — 4th-attempt-of-banned-recipe AVERTED; critical correctness check for H3.
4. `recipe_hash` guard mechanics confirmed — exact spec formula, persisted in both `last.pt` and `best.pt`, resume gate clauses verified, rejection log matches Builder's live mismatch.
5. Param-gating delta sanity — consistent with model.py structure.
6. Leakage scanner disposition — Reviewer correctly identified false positives.

## Leakage-scanner false-positive disposition

Reviewer-verified at file:line precision:

- `ifc_raw` (lines 4, 203): generic dataset family name in docstrings. NOT ground-truth-derived.
- `frozen` (lines 31, 39, 324, 510, 542, 556, 657, 658): standard English describing `requires_grad=False`. NOT ground-truth-derived.
- `2.0` and `0.25` (lines 16, 30): appear in docstring-as-WARNING about the banned MFRNP recipe AND in the `STAGE_STRIDES = [0.25, 0.5, 0.25]` constant (line 110) — neither is a loss-weight literal. NOT a leakage signal.
- `satisfy`, `description`: absent from the diff. No false-positive expected.

This is the **6th consecutive operator-flagged 'leakage substring collision' bookkeeping bug** at Builder phase (the specific name pinned in the cycle-007 standup). The disposition is consistent with the `revert_bookkeeping_keep_intent` precedent established cycles 005-008 H2.

## Anti-patterns explicitly NOT triggered (all six cycle-008 anti-patterns)

1. **MFRNP loss-recipe / reweighting (HF=2.0, LF=0.25)** (BANNED; 3/3 REVERTs across cycles 003/006/007): satisfied — H3 ships uniform weights across all 3 stages; `p` dict immutable per stage; no banned literal anywhere outside docstring-as-WARNING. **4th-attempt-of-banned-recipe AVERTED.** Anti-pattern #1.
2. **Per-dataset MFRNP recipe dispatch** (BANNED; cycle-007 H2 REVERT): satisfied — no `_DATASET_RECIPES` dict, no per-dataset switching. Anti-pattern #2.
3. **H1+H2+H3 bundling** (FORBIDDEN; cycle-008 H1/H2/H3 must be independent branches): satisfied — H3 is on `experiment/13-fno_coreg_residual-three-stage` cut from `1249f2d` directly, NOT chained on `experiment/11` (H1) or `experiment/12` (H2). Zero file overlap with H1's or H2's mutable surfaces.
4. **D1 (`mf_fno_transfer_bar` smoke-config bump)** (DEFERRED to cycle-009+): satisfied — no edits to `models/mf_fno_transfer_bar/**`.
5. **A3 (F-FNO factorized spectral conv refactor)** (DEFERRED to cycle-009+ as `fno_coreg_ffno`): satisfied — no architectural refactor; H3 ships only curriculum + guard.
6. **`models/fno_coreg_residual/model.py` edits** (FORBIDDEN per Strategist R2 — BasisHead must stay unchanged): satisfied. CEO verified `git diff 1249f2d..420a51c -- models/fno_coreg_residual/model.py` is empty.

## Pending (R4 / R5)

- **R4 200-epoch run** via `bash scripts/cycle_eval.sh` on branch `experiment/13-fno_coreg_residual-three-stage @ 420a51c`. **BOTH `ifc_heat` AND `ifc_poisson` MANDATORY** per H3 research_constraint and kill-switch design. Cache MISS expected on the 2 `fno_coreg_residual × ifc_{heat,poisson}` cells (the three-stage curriculum is a new source-bytes configuration). Other cells cache-hit.
- **R4 kill-switches**:
  - **H3-specific**: Stage 3 final Heat > 1.25 × `stage2_final_hf_test_nrmse` → REVERT to Stage 2 verdict (do not re-add basis-head unfreeze).
  - **Universal**: `ifc_heat` nRMSE > 0.0194 → REVERT.
- **R5 verdict logic**:
  - Monotonic check uses **0.027729** as cycle-008 entry baseline (cycle-008 H1 banked best from `experiment/11 @ 18d83a6`; UNCHANGED by H2 GENUINE REVERT).
  - Expected per-cell per H3 hypothesis: `ifc_heat` 0.018-0.022, `ifc_poisson` 0.05-0.06, composite ~0.029-0.033.
  - **Decision rule**: KEEP if composite ≤ 0.027729 AND no kill-switch triggers AND hygiene clean. REVERT otherwise.
  - The `score_direction` polarity precheck bug will likely flip a real composite improvement back to a "+%" regression at R5 (10-of-10 streak through cycle-008 H2's silenced regression); CEO should pre-register the override at R5 entry.

## Implementation notes (carry into R4 interpretation)

- **Cache behavior**: source bytes for `models/fno_coreg_residual/smoke_eval.py` are new, so the 2 `fno_coreg_residual` cells (Heat + Poisson) will cache MISS at R4. Other 16 cells (8 existing families × 2 datasets) cache-hit because their source bytes are unchanged from `1249f2d`.
- **Wall budget on R4 SLURM**: ~6 min total smoke projection fits comfortably inside the 30-min H100 SLURM-side budget per Strategist R2. Same wall as the prior single-stage `fno_coreg_residual` run, redistributed across the three stages.
- **Cycle-008 close-out role**: H3 is the third and final cycle-008 hypothesis. H1 already KEPT (banked best 0.027729); H2 GENUINE REVERT (architecture-falsified on Poisson). H3 either (a) adds a second near-bar family on both PDEs (KEEP, useful for cycle-009 stacking), or (b) hits a kill-switch (REVERT, cycle-008 closes with H1's banked best unchanged).
- **Meta-fix delivery**: regardless of H3's R4/R5 outcome, the `recipe_hash` checkpoint guard is shipped to the `fno_coreg_residual` family — meta-validity improvement that lives in the code and improves the validity of all future research-mode experiments on this family. The cycle-003 backlog item is closed.

## Cross-cycle pattern notes

- **First three-stage curriculum hypothesis on `fno_coreg_residual` in project history.** Cycle-005 H2 (LF→HF schedule) and cycle-007 H2 (per-dataset recipe dispatch) were both two-stage at most. H3 is the first to compose three independent curriculum stages with explicit freeze/unfreeze discipline.
- **Cycle-003 backlog meta-fix shipped as side-effect.** The cycle-003 H1 contamination failure mode (SLURM 13973868 33s stale-resume vs SLURM 13974837 549s clean rerun) had been an open backlog item since cycle-003. H3's MANDATORY recipe_hash guard closes it for the `fno_coreg_residual` family. Pattern: backlog meta-fixes that are PREREQUISITE for a hypothesis to be valid are the highest-leverage cycle interventions (the guard improves validity for ALL future experiments on this family, not just H3).
- **Builder branch hygiene improving — fifth consecutive cycle** (cycle-007 H1, cycle-007 H2, cycle-008 H1, cycle-008 H2, now cycle-008 H3) with a clean single-commit Builder output, zero pre-existing dirty-file contamination committed despite the 15-file dirty working tree carried since cycle-005. [[dirty-tree-staging]] auto-memory rule continues to do its job.
- **Cycle-007 H2 cycle-005 footgun avoided.** H3 implements ACTUAL `requires_grad=False` on LF stack (not zero-loss masking). The cycle-005 footgun (zero-loss masking still allows Adam moments + weight_decay to drift LF params) is correctly avoided. Pattern: "freeze" must mean `requires_grad=False`, NOT zero-loss masking — verified in code review at file:line precision.
- **Stale-momentum discipline (per `lyu2023mffno`)** correctly applied — fresh `Adam` + fresh `CosineAnnealingLR` constructed inside `_train_stage` per stage. NOT continued from previous stage's optimizer/scheduler. Pattern: multi-stage curricula require fresh optimizer/scheduler per stage to avoid carrying stale momentum from a different objective.
- **MFRNP-ban discipline holding across 4 consecutive hypotheses.** Cycle-006 H1, cycle-007 H2, cycle-008 H1, cycle-008 H2 (NEW family), cycle-008 H3 — all 5 hypotheses (3 REVERT + 1 KEEP + 1 pending) have respected the MFRNP-ban directive. H3 is the 4th attempt at the banned-recipe family (`fno_coreg_residual`) that would have been the most tempting target for HF=2.0/LF=0.25 (cycle-007 H2's per-dataset dispatch was the previous attempt on this family). Pattern: stuck-protocol category bans, once issued, are correctly held over multiple cycles.

## Links

- Project dashboard: [[factory_mffp]]
- Cycle-008 strategy: [[cycle-008]] (canonical R2 strategy snapshot — H1 > H2 > H3 plan-approved with bundling-FORBIDDEN anti-pattern; H3 mutable surface = `models/fno_coreg_residual/smoke_eval.py` ONLY)
- Cycle-008 H1 build + final: [[cycle-008-exp-11-build]], [[cycle-008-exp-11]] (paper-config capacity bump on `fno_coregionalization`; banked best 0.027729; cycle-009 entry baseline)
- Cycle-008 H2 build + review + final: [[cycle-008-exp-12-build]], [[cycle-008-exp-12-review]], [[cycle-008-exp-12-final]] (NEW family `fno_coreg_conditioned` FiLM-via-LayerNorm; GENUINE REVERT — architecture-falsified on Poisson)
- Cycle-008 failure analysis: [[failure-analysis-cycle-008]]
- CEO Builder verdict: `.factory/reviews/ceo-verdict-builder.md` (cycle-008 H3)
- Builder report: `.factory/reviews/builder-latest.md`
- CEO Reviewer verdict: `.factory/reviews/ceo-verdict-reviewer.md` (cycle-008 H3)
- Reviewer report: `.factory/reviews/reviewer-latest.md`
- Cycle-003 H1 (parent contamination failure mode that recipe_hash closes): [[failure-analysis-cycle-003]] (SLURM 13973868 33s stale-resume vs SLURM 13974837 549s clean rerun)
- Cycle-005 H2 (banked LF→HF schedule that H3 redistributes across stages): [[factory_mffp-007]]
- Cycle-007 H1 (cycle-008 entry baseline at `1249f2d` — anisotropic-modes constructor signature inherited): [[cycle-007-exp-9-build]], [[cycle-007-exp-9]]
- Cycle-007 H2 (per-dataset dispatch REVERT on same family — banned-recipe lesson preserved): [[cycle-007-exp-10-build]], [[cycle-007-exp-10]]
- Auto-memory honored: [[dirty-tree-staging]], [[factory-cli-invocation]] (Builder used `factory <cmd>` not `uv run python -m factory`).
- Commit: `420a51c` on branch `experiment/13-fno_coreg_residual-three-stage`.
- Base: `1249f2d` (cycle-008 entry baseline; cycle-007 H1 anisotropic-modes constructor fix).
- Diff: `git diff 1249f2d..420a51c models/fno_coreg_residual/smoke_eval.py` (+401 / -73 across 1 file; zero existing-family edits; `model.py` byte-identical).
