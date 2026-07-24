---
tags:
  - factory
  - strategy
  - factory_mffp
project: factory_mffp
cycle: 006
date: 2026-06-02
source: factory-archivist
verdict: PROCEED — PLAN APPROVED
---

# Strategy: factory_mffp — cycle-006

## Mode
Research mode. Dominant failure: `PDE_CLASS_ARCH_RECIPE_COUPLING`. Standard sections suspended; growth dim = composite_nRMSE (geomean of ifc_heat × ifc_poisson).

## Baseline (rolled forward from cycle-005-H2)
- Composite: `0.029357` (Heat=`0.01551`, Poisson=`0.05556`)
- Targets: composite ≤ `0.026` (MISS +0.00336); ifc_heat ≤ `0.013` (MISS +0.00251)
- Gap is **Poisson-gated**: Poisson contributes +0.76 nats above target; Heat is −0.52 nats below

## Approved Hypothesis (H1 only)

**Port MFRNP (HF=2.0, LF=0.25) Poisson loss reweighting + bump basis K=10→20 + add `_DATASET_RECIPES` dispatch on `fno_coreg_residual`.**

- Bundled scope: Top-1 (MFRNP recipe + K bump) + Top-2 (`_DATASET_RECIPES` dispatch) — CEO directive, since H1 already needs dataset-name gating
- Top-3 (`mf_fno_bar_residual` new family scaffold) **deferred to cycle-007**
- Category: FIX (finishes cycle-003 Strategist Hand-off leftover that never landed)
- Type: code
- Confidence: high; Risk: very low
- Mutable surface:
  - `models/fno_coreg_residual/smoke_eval.py:69-82` (extend `SMOKE_DEFAULTS`)
  - `models/fno_coreg_residual/smoke_eval.py:~327` (add `resolve_fidelity_weights` + `_DATASET_RECIPES`)
  - `models/fno_coreg_residual/smoke_eval.py:463-465` (wire dispatch into `run`)
  - `models/fno_coreg_residual/manifest.json:4` (description update)
- Reference (read-only): `models/fno_mf_stack/smoke_eval.py:80-86,326-330`

## Expected Impact
- Poisson on `fno_coreg_residual`: `0.05556 → 0.043–0.052` (lower end crosses ≤0.0436)
- Heat: unchanged (uniform-weights default branch)
- **Composite: `0.029357 → 0.0244–0.0273`** (lower end crosses target ≤0.026)

## CEO Hard Gate
All 9 checks passed: specificity, surface constraint, leakage scan (`flagged: false`), hypothesis count (1, within research-mode budget), targets dominant failure, realistic impact, growth dim tag, risk profile, anti-pattern adherence.

## Key Deferrals (cycle-007 candidates)
- Top-3: `mf_fno_bar_residual` new family scaffold (NEW DIRECTIVE response, largest swing-EV)
- F.1: extend `_DATASET_RECIPES` dispatch to `fno_coregionalization`
- F.2: Heat-side LF-warmup for `fno_coreg_residual`

## Known Downstream Risk
Eval R5 precheck has a `score_direction` polarity bug (7/7 confirmed lower-is-better). May flag real improvement as regression → record `revert_bookkeeping_keep_intent` per cycle-005 protocol; preserve branch.
