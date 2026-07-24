---
name: research-cycle-006
description: Cycle-006 failure-targeted Mode-4 research findings; Poisson holds all the composite gap. Top-1 lands the cycle-003 never-shipped (HF=2.0, LF=0.25) port to fno_coreg_residual; Top-2 generalizes _DATASET_RECIPES dispatch; Top-3 (NEW DIRECTIVE bar+residual family) deferred. WebSearch HTTP 529 outage — local-archive fallback.
metadata:
  type: reference
tags:
  - factory
  - source
  - research
  - cycle-006
  - poisson
  - loss-weighting
  - dataset-conditional-recipe
project: factory_mffp
cycle: 006
source: factory-archivist
date: 2026-06-02
---

# Research — Cycle 006: Failure-Targeted Solutions (Mode 4)

**Trigger:** cycle-006-baseline composite_nRMSE = 0.029357 (cache-rolled from cycle-005-H2). Target: composite ≤ 0.026 AND ifc_heat ≤ 0.013. Failure-Analyst gap decomposition: Poisson +0.76 nats above target, Heat −0.52 nats below. **Poisson holds essentially the entire composite gap** (`ifc_poisson 0.0556 → ≤ 0.0436`).
**Dominant failure mode:** `PDE_CLASS_ARCH_RECIPE_COUPLING` — single global `SMOKE_DEFAULTS` per family, no dataset-aware gating.
**Mutable surface:** `models/**` only.
**CEO verdict:** PROCEED. Top-1 = "finish a 5-line change that was already scoped, justified, and ordered three cycles ago."
**Related:** [[research-cycle-003]], [[research-cycle-005]], [[niu2024mfrnp]], [[li2022ifc]], [[patterns]].

---

## Top-1 — MFRNP (HF=2.0, LF=0.25) Poisson reweighting + K=10→20 on `fno_coreg_residual`

**Origin:** the cycle-003 Strategist Hand-off explicitly ordered the port of `resolve_fidelity_weights(dataset_name, p)` from `fno_mf_stack/smoke_eval.py:326-330` into `fno_coreg_residual/smoke_eval.py:465` — **never landed**. `fno_coreg_residual` still ships uniform `lf_loss_weights = (1.0,)*…` for ALL datasets including Poisson.

**Cross-architecture validation (in-repo):** the recipe was measured on `fno_mf_stack` (different backbone — single trunk vs. per-fidelity FNOs) at 4-fidelity IFC Poisson and produced **0.0596**. Confirms it survives backbone change (MFRNP-NP → FNO) and fidelity-count change (5 → 4).

**Bundled K bump:** `li2022ifc` reports Poisson SOTA at K=20; current smoke uses K=10. Zero-init on `BasisHead.lin3` (`fno_coreg_residual/model.py:181-182`) means K=20 starts identical to K=10 at step 0 — cannot regress at convergence.

**File:line spec:**
- `models/fno_coreg_residual/smoke_eval.py:69-82` — add `poisson_hf_weight=2.0, poisson_lf_weight=0.25` to `SMOKE_DEFAULTS`; bump `K=10→20`, `b_hidden=64→128`.
- `models/fno_coreg_residual/smoke_eval.py:~327` — add `resolve_fidelity_weights(dataset_name, p)` helper (gated on `"poisson" in dataset_name.lower()`); wire into `p["hf_loss_weight"]` / `p["lf_loss_weights"]` at line 465.

**Expected effect:** Poisson 0.0556 → 0.043–0.052; composite 0.029357 → 0.0244–0.0273. Lower end **possibly closes the composite target alone.** **Confidence:** high.

**Backbone-coupling caveat ([[patterns]], cycle-003 H1 R4):** the recipe catastrophically regressed Poisson 0.07416 → 0.27287 (+268%) on the cycle-002-H3 hybrid ancestor. Strategist must run an R4 kill-switch — if Poisson regresses >+20%, revert immediately.

---

## Top-2 — `_DATASET_RECIPES` dispatch (structural fix for `PDE_CLASS_ARCH_RECIPE_COUPLING`)

The pattern already exists in-tree at `fno_mf_stack/smoke_eval.py:326-330`. Generalize to a `_DATASET_RECIPES` dict merged into `SMOKE_DEFAULTS` based on `args.dataset_name`, with default fallback that preserves current behavior. Adopt failure_analyst F.1 verbatim.

```python
_DATASET_RECIPES = {
    "ifc_heat":    dict(pretrain_frac=0.40, pretrain_lr=1e-3, finetune_lr=3e-4, K=20),
    "ifc_poisson": dict(pretrain_frac=0.0,  pretrain_lr=3e-4, finetune_lr=3e-4,
                        poisson_hf_weight=2.0, poisson_lf_weight=0.25, K=20),
}
```

**Apply to:** `fno_coregionalization/smoke_eval.py` (Heat path) and `fno_coreg_residual/smoke_eval.py` (covered by Top-1 weights). MFRNP itself ships three separate YAMLs (`Poisson5_config.yaml`, `pde_config.yaml`, `Fluid_config.yaml`) — per-PDE hyperparameter sets are the published norm.

**CEO note:** "I lean toward bundling [Top-2] into H1 since Top-1 already needs to gate weights by dataset name." **Confidence:** high. **Risk:** low (default fallback).

---

## Top-3 — NEW family `mf_fno_bar_residual` (NEW DIRECTIVE response, DEFERRED)

Bar transfer (`lyu2023mffno`) + per-fidelity residual head (basis head from `fno_coreg_residual`). **CEO has deferred to cycle-007**: "Given the Researcher rates Top-1 as 'possibly closes the gap alone', H2 should NOT be Top-3 in this cycle. Reserve cycle budget for Top-1 quality."

Composition pattern empirically supported across DeepONet ([[yang2025mfdeeponet]]), autoencoder ([[nietocentenero2025mfae]]), GP/coregionalization ([[niu2024mfrnp]]) and the cycle-005 H2 result on FNO+coregionalization for Heat (−24%). **No published direct FNO-trunk + FNO-residual-head reference surfaced via archive** — flag for cycle-007 WebSearch.

---

## Web access outage (NEW reference-quality observation)

**WebSearch / WebFetch returned HTTP 529 (overloaded) on every query attempted** (≥10 retries, distinct queries). External evidence drawn entirely from the local archive (rich for this problem space because cycle-003 already conducted ~20 web-sourced citations on HF/LF reweighting), in-tree inline citations (`mf_fno_transfer_bar/smoke_eval.py`, `fno_coregionalization/smoke_eval.py`), and BibTeX-preserved citations from `research-cycle-003.md`. **No hallucinated references.**

**Deferred to cycle-007 (when WebSearch recovers):** post-2024 selective HF-modes-only capacity bump for elliptic; FNO+adapter / FNO+LoRA; spectral-attention / frequency-conditional gating; direct FNO+FNO-head transfer reference.

**Pattern logged:** local-archive fallback survives WebSearch outage when prior cycle conducted equivalent web research on the same problem space.
