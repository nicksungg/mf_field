# CEO Review: Strategist — Cycle-010 (HARD GATE)

- **Verdict:** PROCEED — **PLAN APPROVED**

## Hypotheses Approved (in priority order)

1. **H1 — `fno_mf_stack` capacity-axis 2nd step (conservative)** [HIGH, MUST LAND FIRST]
   - File: `models/fno_mf_stack/smoke_eval.py` SMOKE_DEFAULTS (lines 39-55)
   - Changes: `hidden=64→96`, `modes_per_level=(4,8,16,20)→(4,8,16,24)`
   - All other keys held (n_blocks=4, agg_hidden=64, MFRNP weights, LF modes_per_level[0..2])
   - Type: code. New: yes.
   - Expected: Poisson 0.0381→0.030-0.034 (-10 to -22%); composite 0.022161→0.0197-0.0212 (-5 to -11%)
   - Kill-switches: Poisson/Heat > 0.0594, wall > 1500s. Recipe_hash guards resume.

2. **H2 — `fno_mf_stack` LF→HF curriculum with frozen-LF stage 2 (NK2 carve-out)** [MEDIUM, SEPARATE PR after H1]
   - File: `models/fno_mf_stack/smoke_eval.py` SMOKE_DEFAULTS + training loop + compute_losses + optimizer construction
   - Changes: add `pretrain_frac=0.40`, `stage2_freeze_lf=True`; stage 1 LF-only fresh Adam@1e-3 + CosineAnnealingLR(stage1_epochs); stage transition freezes `lf_fnos[0..2]` + fresh Adam@3e-4 + CosineAnnealingLR(stage2_epochs); stage 2 joint loss with frozen LF stack
   - Clears O3 backlog item (cycle-009 close-out deferred curriculum).
   - Type: code. New: no (backlog).
   - Expected: further Poisson -5 to -15% on top of H1's banked result; composite 0.0184-0.0205 (~60-70% of GPODE bar)
   - DUAL kill-switch: absolute (Poisson/Heat > 0.0594) AND inter-stage (stage-2 best_val ≥ 0.90 × stage1_best_val); wall > 1800s
   - **Measured against H1's banked result, NOT cycle-010 baseline.** Separate experiment ID, separate PR.

## Hard Gate Checklist

- ✅ **Surface constraints**: H1 + H2 both touch `models/fno_mf_stack/smoke_eval.py` only (mutable surface). No fixed-surface leakage.
- ✅ **Ground truth leakage scan**: ran `factory leakage-check` on both hypothesis texts. Both returned `risk_level: none`, `flagged: false`. No findings.
- ✅ **Hypothesis count**: 2 hypotheses (max_new=2 budget honored; H1 = new, H2 = backlog clearance).
- ✅ **NK1 sidestep**: H1 = capacity-only (no conditioning change); H2 = curriculum-only (no conditioning change). Both NK1-clear.
- ✅ **NK2 carve-out for H2**: structurally justified by `models/fno_mf_stack/model.py:165-168` — 4 independent SmallFNO modules with NO shared weights. Pattern matches `yang2025mfdeeponet` freeze-LF protocol exactly. Mandatory dual kill-switch is included.
- ✅ **NK3 sidestep**: H1 and H2 both hold canonical MFRNP weights `(poisson_hf_weight=2.0, poisson_lf_weight=0.25)` unchanged. Neither perturbs loss weights.
- ✅ **Operational items**: N/A — both are Type: code. Eval is run via standard `cycle_eval.sh`, no Execution Step needed.
- ✅ **Backlog adequacy**: H2 fully addresses cycle-009 close-out O3 — same family (fno_mf_stack), NK2 carve-out (LF/HF-independent design), both absolute AND inter-stage kill-switches. No partial-cleanup gap.
- ✅ **No calendar-time estimates**.
- ✅ **Bundling caveat respected**: explicit "DO NOT bundle H1 + H2" rule with attribution-confounding rationale. Sequencing: H1 first → measure → bank → H2 on top.

## Sequencing Plan

- **Experiment 1 (H1)**: branch from `experiment/14-fno_mf_stack-capacity-and-recipe-hash @ 0b6e6eb` (cycle-010 baseline = previous best). Branch name `experiment/15-fno_mf_stack-capacity-axis-2nd-step`. Implement H1 SMOKE_DEFAULTS edit, smoke-verify with --epochs 2, then run full smoke. Verdict against cycle-010 baseline 0.022161.
- **Experiment 2 (H2)**: if H1 keeps, branch from H1's banked branch. Branch name `experiment/16-fno_mf_stack-curriculum-frozen-lf`. Implement H2 training loop changes. Verdict against H1's banked result. If H1 reverts, H2 still runs but from cycle-010 baseline (NB: this scenario is unlikely given H1's HIGH-confidence profile, but H2's curriculum lever is fresh-axis-distinct from capacity so it's defensible to run regardless).

## Issues Found

- None substantive. The strategy is internally consistent and aligns with the CEO priority signal from the failure-analyst/researcher verdicts.

## Instructions for Builder (H1 first)

- Implement only the SMOKE_DEFAULTS edit at `models/fno_mf_stack/smoke_eval.py:39-55`. Do not touch `model.py` or any other family.
- Before declaring ready: run `uv run python -m models.fno_mf_stack.smoke_eval --epochs 2 --dataset_dir data/ifc_heat --out /tmp/x.json --ckpt_dir /tmp/c --seed 0` to catch any import/recipe_hash issues.
- Update `models/fno_mf_stack/INSPIRATION.md` to cite the new bibtex keys: `mutransferfno2025`, `fnospectralperspective2024` (in addition to the cycle-009 set).
- Commit with message reflecting the cycle-010 H1 capacity-axis step.
- Branch: `experiment/15-fno_mf_stack-capacity-axis-2nd-step`.
- Do NOT open a GitHub PR (--no-github). Just commit locally.

## Instructions for Builder (H2 second — only after H1 keeps)

- Implement H2 atop H1's banked branch.
- Modifications to `models/fno_mf_stack/smoke_eval.py`: add two SMOKE_DEFAULTS keys, refactor optimizer/scheduler construction into a small helper, gate the training loop on stage, and apply `requires_grad_(False)` to `lf_fnos[0..2]` at the stage transition.
- Implement the inter-stage kill-switch: snapshot `stage1_best_val` from the val pass at the end of stage 1; at the end of stage 2, compare against `0.90 × stage1_best_val` and revert to stage-1 checkpoint if the threshold is not met.
- Smoke-verify with `--epochs 2` (will produce stage1_epochs=1, stage2_epochs=1 — exercises both stage gates and the freeze transition).
- Branch: `experiment/16-fno_mf_stack-curriculum-frozen-lf`.

## Next Action

Spawn Archivist (mandatory) → write checkpoint → begin Experiment 1 (H1).
