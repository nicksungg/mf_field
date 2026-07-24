# CEO Review: Evaluator Agent — Cycle-008 H3 (Experiment 13) — Phase R4 RUN

- **Verdict:** PROCEED (ratify Evaluator REVERT recommendation)
- **Rationale:** Evaluator's analysis is quantitative, kill-switch-checked, and unambiguous. H3 catastrophically regresses `fno_coreg_residual` on Heat (26× over universal kill-switch). Genuine architecture-falsified REVERT.

## Quantitative summary

| Metric | Value | vs target | Status |
|---|---|---|---|
| **Composite nRMSE (H3 branch)** | 0.030408 | minimize | flat vs baseline (family no longer wins either cell) |
| Composite vs baseline (1249f2d) | 0.000000 / +0.00% | improve | NEUTRAL |
| Composite vs previous best (cycle-008 H1 exp 11 = 0.027729) | +0.002679 / **+9.66%** | improve or hold | **REGRESSION** |
| `fno_coreg_residual × ifc_heat` | 0.509105 | < 0.0194 universal kill-switch | **TRIPPED 26×** (was 0.026 single-stage; +1837%) |
| `fno_coreg_residual × ifc_poisson` | 0.159364 | Builder predicted 0.05–0.06 | **+165% out of range** (was 0.074 single-stage; +115%) |
| H3-specific Stage3/Stage2 Heat ratio | 1.00 | < 1.25 → KEEP | NOT TRIPPED (Stage 2 already produced 0.509; Stage 3 was a no-op on Heat) |
| Smoke wall (fno_coreg_residual, both datasets) | 50.7 s | < 6 min projection | CLEAR (~7× under budget) |
| Total cycle_eval wall | 71 s | < 14400 s | CLEAR |
| val/test gap (Heat) | 12× (val 0.043 → test 0.509) | < 2× normal | massive — suggests final-state-checkpoint divergence OR overfitting |

## Why composite is flat at baseline

The composite is the geomean of per-dataset bests. On the H3 branch, `fno_coreg_residual` has regressed so badly that it no longer wins EITHER cell:
- `ifc_heat` best: `fno_coregionalization` at 0.01551 (unchanged from baseline)
- `ifc_poisson` best: `fno_mf_stack` at 0.05961 (unchanged from baseline)
- `fno_coreg_residual` was previously THE Heat 2nd-place (0.026 single-stage); now 0.509 — falls out of the leaderboard top tier entirely.

So the composite is mathematically flat at 0.030408 ONLY because the family's collapse doesn't enter the per-cell argmin. This is the **same surface pattern as H2** (composite flat at baseline → family non-dominant) but a **different underlying cause**: H2 added a NEW non-dominant family; H3 broke an existing dominant family.

## Architectural lesson (for cycle-009 failure analysis)

The H3 three-stage curriculum is **architecturally incompatible** with `fno_coreg_residual`:

1. **`fno_coreg_residual` is a residual ladder design** (per model.py:43-188). The HF prediction = LF features → residual correction → BasisHead aggregation. The LF and HF networks are designed to **co-evolve** — the HF network learns a correction that depends on the current LF representation.

2. **Stage 2 of H3 freezes the LF stack** (`requires_grad=False`), forcing the HF residual to correct against a fixed LF state. But the LF state from Stage 1 (LF-only pretrain, m != hf_m samples) is NOT the LF representation the HF residual was designed to correct — it's an out-of-distribution LF state from a pretraining regime the architecture wasn't built for.

3. **Result:** the HF residual learns garbage in Stage 2, with no information back to the LF stack to fix the mismatch. Stage 3's unfreeze comes too late — the HF residual is already in a poor local minimum. The val/test gap of 12× on Heat confirms catastrophic overfitting in this regime.

4. **In contrast, H1 (capacity bump on `fno_coregionalization`) and the prior single-stage `fno_coreg_residual` recipe** both train ALL networks co-evolved end-to-end. The architecture's inductive bias is preserved.

**Implication for cycle-009:** Three-stage frozen-LF-HF-residual curricula are architecturally appropriate ONLY for families where the LF and HF networks are independent by design (e.g., `mf_fno_transfer_bar` may fit — its LF FNO outputs a feature map that's an INPUT to the HF FNO, not a co-trained residual). For `fno_coreg_residual` and `fno_coregionalization` (co-evolved designs), end-to-end joint training remains the right recipe.

## Kill-switch design retrospective

The H3-specific kill-switch (`Stage3/Stage2 Heat ratio > 1.25 → REVERT to Stage 2`) was designed assuming Stage 3's unfreeze would be the source of damage (BasisHead instability + LF unfreeze at lr=9e-5). Reality: damage occurred in Stages 1/2; Stage 3 actually **helped Poisson 3.46×** (0.551 → 0.159) but couldn't recover Heat. The Stage3/Stage2 ratio was 1.00 because Stage 2 already produced 0.509 on Heat.

**Lesson for cycle-009 strategy:** kill-switches should ALSO include an absolute Stage 2 vs baseline check (e.g., `stage2_final_hf_test_nrmse > 1.25 × prior_single_stage_test_nrmse → REVERT to baseline`). The universal `ifc_heat > 0.0194` caught it — but only post-hoc, not mid-training.

## Recipe_hash guard outcome (meta-fix delivery successful)

Despite the architectural failure of H3, the cycle-003 backlog `recipe_hash` checkpoint guard meta-fix worked correctly:
- Per the Evaluator: "The recipe_hash guard worked as expected: stale ckpt was rejected, family retrained from scratch under the new recipe."
- The guard implementation is preserved in the H3 commit (420a51c) for reference. The PATTERN should be cherry-picked into other family smoke_eval.py files in cycle-009 as a portable utility (`models/_common/recipe_hash.py` perhaps).

**Important:** the recipe_hash guard is the H3 KEEP-worthy artifact in isolation. The three-stage curriculum is NOT keep-worthy. We should preserve the guard pattern for cycle-009 but NOT keep the H3 commit (the catastrophic Heat regression dominates).

## Decision

- **R5a (Hygiene Gate):** No hygiene regression — single file modified (smoke_eval.py), no test/lint/type configs touched. Pass.
- **R5b (Monotonic Improvement Check):** FAIL — composite +9.66% above previous best (0.027729 → 0.030408). Mandatory revert.
- **R5c (Universal Kill-Switch):** TRIPPED — `ifc_heat > 0.0194` triggered at 26× over (0.509 vs 0.0194). Mandatory revert.
- **R5d (Keep/Revert):** **REVERT** — universal kill-switch tripped + architectural hypothesis falsified for this family.

## Instructions for finalize

- Verdict: `revert` (genuine, NOT `revert_bookkeeping_keep_intent`)
- Notes field: `ceo:revert mode=research reason=architecture_incompatible_three_stage_on_residual_ladder metric=composite_nRMSE before=0.027729 after=0.030408 delta=+0.002679 delta_pct=+9.66 hygiene=pass monotonic=fail heat=0.509105 poisson=0.159364 universal_killswitch=tripped_26x h3_killswitch=not_tripped_design_flaw recipe_hash_guard=works_correctly hypothesis_type=code execution_artifacts=na e2e=pass backlog_cleared=recipe_hash_pattern_only`
- Keep the branch (`experiment/13-fno_coreg_residual-three-stage @ 420a51c`) for reference: the **`recipe_hash` checkpoint guard pattern** is reusable; the three-stage curriculum is not.
- Checkout the prior branch state (back to baseline 1249f2d or H1's 18d83a6 — banked-best-bearing) after finalize.
