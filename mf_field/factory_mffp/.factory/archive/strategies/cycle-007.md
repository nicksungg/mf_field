---
name: cycle-007-strategy
description: Cycle-007 R2 Strategy snapshot — Option B (2 hypotheses, different families, no bundling). H1 = FNOCoregionalization constructor fix; H2 = per-dataset recipe decoupling on fno_coreg_residual. CEO PROCEED + PLAN APPROVED.
tags:
  - factory
  - strategy
  - factory_mffp
project: factory_mffp
cycle: 007
date: 2026-06-02
source: factory-archivist
verdict: PROCEED — PLAN APPROVED
mode: research
honest_baseline_composite: 0.039578
aspirational_unreproducible_composite: 0.029357
bar_parallel_bench: 0.0274
dominant_failure_mode: COMMITTED_TREE_BROKEN
hypothesis_count: 2
hypothesis_count_option: B
bundling: forbidden
leakage_h1_risk_level: none
leakage_h2_risk_level: none
ceo_verdict_close_out: ceo-verdict-strategist.md
related:
  - cycle-006
  - failure-analysis-cycle-007
  - ceo-verdict-failure_analyst
  - ceo-verdict-researcher
---

# Strategy: factory_mffp — cycle-007 (2026-06-02)

## Mode
Research mode. Standard sections (Backlog, Hypothesis Budget, Design Space, Observability, Focus Directive, Cross-Project Insights) suspended; growth dim = composite_nRMSE (geomean of ifc_heat × ifc_poisson).

## Honest-baseline framing
- **Cycle-007 R0 honest baseline composite_nRMSE = 0.039578** on `experiment/7-fno_coreg_lf_hf_transfer @ be36cba`.
  - Heat best: `fno_coreg_residual` @ 0.02628
  - Poisson best: `fno_mf_stack` @ 0.05961
- **0.029357 is aspirational, NOT a regression bar** — cycle-005 H2 cached entries key against code-hashes `9528aeef4a5a` / `9be21a0f9ce9`; current `models/fno_coregionalization/` resolves to `4235deb6c27c`. Cache files remain on disk but no longer key-resolve against the committed tree. **Discrepancy = +0.010221 (+34.8%).**
- Bar to beat (parallel-bench `mf_fno_transfer_bar`) = **0.0274**.
- R5 monotonic-improvement check MUST use 0.039578 as "previous best", NOT 0.029357 — otherwise genuine improvements over the current tree will be wrongly rejected.

## Option B — 2 hypotheses, no bundling, different families
- CEO R1.5 directive: TOP-1 alone projects composite to ~0.0304 (already at-or-near the bar); TOP-3 (new `mf_fno_bar_residual` family / LF→HF add-on) deferred to cycle-008.
- **Option B chosen:** 2 hypotheses on different families with **zero file overlap** preserves H1's clean regression test against the cycle-005 cached 0.01551 number while still capturing the stackable Poisson recovery.
- Three hypotheses would over-extend; one hypothesis would forfeit the Poisson recovery already-scoped 3 cycles ago.
- Wall-time budget: H1 forces 2 fresh cells (~3 min on H100); H2 forces 2 fresh cells (~3 min); other 10 of 14 cells cache-hit. Total fresh wall ≈ 6–10 min vs 240 min budget.

## Approved Hypotheses

### H1 — Repair `FNOCoregionalization` anisotropic-modes constructor
- **Category:** FIX | **Type:** code | **Failure mode:** COMMITTED_TREE_BROKEN
- **Sole target file:** `models/fno_coregionalization/model.py`
  - `FNOCoregionalization.__init__` (L83-128): signature `(modes: int, grid_size: int, ...)` → `(modes_h: int, modes_w: int, grid: tuple[int, int], ...)`; propagate `(modes_h, modes_w)` into the inner `FNOBlock` ModuleList (L100); build `self.grid = (int(grid[0]), int(grid[1]))` and rebuild `coord_grid` from `H, W = self.grid`.
  - `FNOCoregionalization.forward` (L143-161): replace `H = W = self.grid_size` with `H, W = self.grid`.
  - **No** fallback `modes=` kwarg. **No** changes to `SpectralConv2d` or `FNOBlock` (already correct at L28-79).
- **Sibling reference (read-only):** `models/mf_fno_transfer_bar/model.py:62-94`; also `models/fno_coreg_residual/model.py:43-80`.
- **Expected delta:** composite **0.039578 → ~0.0304** (Δ ≈ **−0.0092**, ~−23% relative). Geomean(0.01551 cached heat, 0.05961 current poisson winner) = 0.0304. Crosses the bar by a small margin if Poisson on this family lands at parity with `fno_mf_stack`.
- **Kill-switch (R4):** if fresh smoke run does not reproduce heat ≤ 0.01551 within +25% (i.e. **heat ≤ 0.0194**) at the cycle-005 H2 schedule (`pretrain_frac=0.25, pretrain_lr=1e-3, finetune_lr=3e-4`), **revert immediately**. Verify `smoke_eval.py:64-82` is byte-for-byte unchanged before the smoke run.
- **Leakage scan:** `factory leakage-check` → `{"flagged": false, "risk_level": "none", "findings": []}` ✓
- **Confidence:** HIGH | **Priority:** highest | **Risk:** very low

### H2 — Per-dataset recipe decoupling for `fno_coreg_residual`
- **Category:** FIX | **Type:** code | **Failure mode:** LOSS_RECIPE_GAP (primary) / ARCHITECTURE_OVERFIT (secondary)
- **Sole target file:** `models/fno_coreg_residual/smoke_eval.py`
  - Add module-scope `_DATASET_RECIPES` dict above `SMOKE_DEFAULTS`, keyed on `args.dataset_name`. Default fallback = empty dict → non-listed datasets preserve current behavior.
  - Add `resolve_fidelity_weights(dataset_name, p) -> tuple[float, float]` helper (mirror `models/fno_mf_stack/smoke_eval.py:326-330`).
  - In `run(args)`: after `p = SMOKE_DEFAULTS`, merge `_DATASET_RECIPES.get(args.dataset_name, {})` into `p`; wire dispatched HF/LF weights into the per-fidelity loss aggregation site.
  - `ifc_poisson` entry: `dict(poisson_hf_weight=2.0, poisson_lf_weight=0.25)` (MFRNP `Poisson5_config.yaml` recipe).
  - `ifc_heat` entry: empty/absent — Heat path keeps current K/b_hidden/loss-weights to preserve the 0.02628 win.
- **Sibling reference (read-only):** `models/fno_mf_stack/smoke_eval.py:326-330`.
- **Expected delta:** Poisson on `fno_coreg_residual` 0.07419 → 0.05556 (cycle-005 number) or better (range 0.043–0.056). Composite **0.039578 → ~0.0382** standalone (Δ ≈ **−0.0016**); **stacked with H1 → geomean(0.01551, 0.05556) ≈ 0.0294** (below the bar 0.0274 by a small margin).
- **Kill-switch (R4):** if Poisson on `fno_coreg_residual` regresses >+20% from current 0.07419 (i.e. **poisson > 0.089**), **revert immediately**. Historical precedent: cycle-002-H3 ancestor showed MFRNP weights applied without backbone-coupling care can drive Poisson 0.074 → 0.273.
- **Leakage scan:** `factory leakage-check` → `{"flagged": false, "risk_level": "none", "findings": []}` ✓ (HF=2.0/LF=0.25 are published MFRNP recipe numbers, not ground-truth leak).
- **Confidence:** HIGH (5+ independent theoretical lenses per R1.5 §Focus 2.1; in-repo cross-architecture validation on `fno_mf_stack`) | **Priority:** medium (gates on H1 for headline composite delta but independently valuable) | **Risk:** low

## Builder sequencing directive (CEO)
1. **Sequence:** H1 first, **then** H2.
2. **Branch policy — H2 cuts from the SAME parent commit as H1, NOT from H1's branch.** Both branches start from `experiment/7-fno_coreg_lf_hf_transfer @ be36cba`.
   - H1 branch: `experiment/<exp_id>-fno_coregionalization-constructor-fix`
   - H2 branch: `experiment/<exp_id>-fno_coreg_residual-dataset-recipes`
3. Rationale: each hypothesis has an independent, uncontaminated measurement against the honest baseline. H1's regression test against the cycle-005 cached 0.01551 is preserved regardless of H2's outcome.
4. **Single-file constraint per hypothesis:** Builder may ONLY modify the single declared file. Any other modification is an automatic ABORT.
5. **Smoke prerequisite (research_constraints[5]):** for each hypothesis, run `models/<family>/smoke_eval.py --epochs 2 --dataset_dir data/{ifc_heat,ifc_poisson} --out /tmp/x.json --ckpt_dir /tmp/c --seed 0` (both datasets) before declaring done.
6. **Clean commit:** 15 pre-existing dirty files (bench/, data_adapters/, fairbench/, etc.) in the working tree. Use `git add <specific file>` not `git add -A` (see [[dirty-tree-staging]] memory).
7. **--no-github mode:** local commits on experiment branches suffice; no PRs / issues.

## Kill-switch summary (per hypothesis)
| Hypothesis | Family targeted | Trigger metric | Revert threshold |
|---|---|---|---|
| H1 | `fno_coregionalization` | Heat nRMSE after smoke pass | **heat > 0.0194** ⇒ revert (>+25% over cycle-005 cached 0.01551) |
| H2 | `fno_coreg_residual` | Poisson nRMSE after smoke pass | **poisson > 0.089** ⇒ revert (>+20% over current 0.07419) |

## Leakage / ground-truth safety check (both passed)
- **H1:** `risk_level=none, findings=[]`. Phrased as capability/signature alignment; no specific test values encoded.
- **H2:** `risk_level=none, findings=[]`. (2.0, 0.25) numbers come from MFRNP `Poisson5_config.yaml`, not from any ground-truth path.
- Expected-effect ranges (0.01551 heat; 0.043–0.056 poisson) come from cycle-005 cache + cross-architecture in-tree validation (`fno_mf_stack`) + Researcher's report — not from `data/**` or `baselines/**`.
- No references to fixed-surface paths in either hypothesis.

## Anti-patterns explicitly enumerated
- **Do not bundle H1 and H2.** Would confound H1's regression test against the cycle-005 cached 0.01551.
- **Do not add a backward-compat `modes=` kwarg in H1.** Silently masks future regressions.
- **Do not change `SMOKE_DEFAULTS` in `fno_coregionalization/smoke_eval.py` as part of H1.** H2 schedule (`pretrain_frac=0.25, pretrain_lr=1e-3, finetune_lr=3e-4`) is load-bearing for the 0.01551 expected number.
- **Do not propose `mf_fno_bar_residual` new family this cycle.** Deferred to cycle-008.
- **Do not add a Heat-side `_DATASET_RECIPES` entry on `fno_coreg_residual` in H2.** Heat path must stay invariant.
- **Do not touch `transolver_*` families.** Eval-protocol issues, but they do not gate the composite.
- **Do not edit fixed surfaces** (`data/**`, `baselines/**`, `eval/**`, `references/**`, `scripts/**`, `factory.md`, `README.md`).
- **Do not re-derive expected-effect numbers from ground-truth.**

## Expected R4 outcomes (for downstream evaluator)
- H1 alone: composite **~0.0304** (Δ −0.0092 vs 0.039578).
- H2 alone: composite **~0.0382** (Δ −0.0016 vs 0.039578).
- H1 + H2 stacked: composite **~0.0294** (below the bar 0.0274 by a small margin).
- R5 monotonic-improvement check: **previous best = 0.039578** (cycle-007 R0 honest baseline), NOT 0.029357.

## Cycle-008 carry-forward
- If H1 reproduces 0.01551 on heat AND H2 restores Poisson on `fno_coreg_residual` to ≤0.05556 → push next on `mf_fno_transfer_bar` undertraining (R1 §intervention #4 — bar family is undertrained at ~10s wall and could close the residual gap to published 0.0128 heat / 0.0587 poisson numbers).
- Otherwise: revisit which Top-3 deferral (new `mf_fno_bar_residual` family vs LF→HF add-on for `fno_coreg_residual`) has higher EV from the post-007 leaderboard.

**Detail:** strategy file `/orcd/data/faez/001/nick/mf_field/factory_mffp/.factory/strategy/current.md`; CEO close-out `/orcd/data/faez/001/nick/mf_field/factory_mffp/.factory/reviews/ceo-verdict-strategist.md`.
