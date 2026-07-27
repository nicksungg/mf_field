---
name: cycle-006-ranked-findings
description: Top-3 ranked findings for cycle-006 Strategist — Top-1 (load-bearing, gap-closing, cycle-003 backlog port that never landed), Top-2 (structural _DATASET_RECIPES dispatch generalizing failure_analyst F.1), Top-3 (NEW DIRECTIVE mf_fno_bar_residual family, deferred to cycle-007 per CEO).
metadata:
  type: reference
tags:
  - factory
  - source
  - ranked-findings
  - cycle-006
  - strategist-handoff
project: factory_mffp
cycle: 006
source: factory-archivist
date: 2026-06-02
---

# Cycle-006 Ranked Findings — Strategist Hand-off

**Date:** 2026-06-02.
**Source documents:** [[research-cycle-006]], [[failure-analysis-cycle-006]], `.factory/reviews/ceo-verdict-researcher.md`.
**Composite gap:** 0.029357 → target 0.026 (gap +0.0034). Poisson contributes ~all of the gap in log-space.
**Related notes:** [[research-cycle-003]], [[patterns]].

---

## Top-1 (LOAD-BEARING) — `(HF=2.0, LF=0.25)` + K=10→20 on `fno_coreg_residual`

**Single-line CEO framing**: "finish a 5-line change that was already scoped, justified, and ordered three cycles ago."

- **Status:** documented external recipe (MFRNP `Poisson5_config.yaml`); cross-architecture in-repo validation at 0.0596 on `fno_mf_stack` (cycle-002 H4); **explicitly ordered by cycle-003 Strategist Hand-off as a port from `fno_mf_stack` → `fno_coreg_residual`** — never landed.
- **Files & lines:**
  - `models/fno_coreg_residual/smoke_eval.py:69-82` — extend `SMOKE_DEFAULTS`: add `poisson_hf_weight=2.0, poisson_lf_weight=0.25`; change `K=10 → K=20`, `b_hidden=64 → b_hidden=128`.
  - `models/fno_coreg_residual/smoke_eval.py:~327` (module scope) — add `resolve_fidelity_weights(dataset_name, p) -> tuple[float, float]`.
  - `models/fno_coreg_residual/smoke_eval.py:465` — replace uniform `p["lf_loss_weights"]` construction with dispatched weights.
  - `models/fno_coreg_residual/manifest.json:4` — update description.
- **Expected effect:** Poisson 0.0556 → 0.043–0.052; Heat 0.03519 → unchanged (uniform-weights branch); composite 0.029357 → 0.0244–0.0273. **Lower end crosses 0.0436 threshold and closes composite target.**
- **Risk:** very low — cite-grounded, gated on dataset name, zero-init on extra basis channels.
- **Confidence:** **high**.
- **CEO instruction to Strategist:** propose as H1 verbatim with file:line specs from research §1a / §1b.

### Backbone-coupling kill-switch

cycle-003 H1 R4 was the recipe's first failed port — on the `fno_coreg_residual`-ancestor hybrid family, Poisson regressed 0.07416 → 0.27287 (+268%, catastrophic). The cycle-006 Researcher's expected-effect estimate is bounded by both the cross-architecture validation (0.0596 on `fno_mf_stack`) AND the cycle-003 cautionary tale.

**Strategist R4 kill-switch**: if Poisson regresses >+20% post-port, **revert immediately** — the backbone-coupling pattern is re-firing. See [[patterns]] §"MFRNP per-fidelity loss-weighting recipes are backbone-coupled across MF aggregation architectures".

---

## Top-2 (HIGH-EV STRUCTURAL) — `_DATASET_RECIPES` dispatch in both fno_coreg families

**CEO framing:** "structural fix for the dominant failure mode. Even if Top-1 lands and closes the composite gap, future cycles will keep tripping on `PDE_CLASS_ARCH_RECIPE_COUPLING` until the dispatch is the standing pattern. Top-2 makes Top-1 robust to future re-tunings."

- **Status:** generalizes the in-tree pattern already accepted at `fno_mf_stack/smoke_eval.py:326-330` (`resolve_fidelity_weights(dataset_name, p)`). Implements failure_analyst F.1 verbatim across two families.
- **Files & lines:**
  - `models/fno_coregionalization/smoke_eval.py:64-82` — add `_DATASET_RECIPES` dict above `SMOKE_DEFAULTS`; in `run(args)` at line 239 merge `_DATASET_RECIPES.get(args.dataset_name, {})` into `p`.
  - `models/fno_coreg_residual/smoke_eval.py:69-82` — same pattern.
- **Recipe:**
  ```python
  _DATASET_RECIPES = {
      "ifc_heat":    dict(pretrain_frac=0.40, pretrain_lr=1e-3, finetune_lr=3e-4, K=20),
      "ifc_poisson": dict(pretrain_frac=0.0,  pretrain_lr=3e-4, finetune_lr=3e-4,
                          poisson_hf_weight=2.0, poisson_lf_weight=0.25, K=20),
  }
  ```
- **Expected effect:**
  - `fno_coregionalization`: Heat 0.01551 → 0.013–0.015 (longer LF pretrain + K=20); Poisson unchanged.
  - `fno_coreg_residual`: Heat unchanged unless paired with Q3.3b; Poisson per Top-1.
- **Risk:** low — default fallback preserves current behavior.
- **Confidence:** **high**.
- **CEO bundling note:** "I lean toward bundling [Top-2] into H1 since Top-1 already needs to gate weights by dataset name." Either bundling or independent H2 is acceptable.

---

## Top-3 (DEFERRED) — NEW family `mf_fno_bar_residual`

**CEO framing:** "Given the Researcher rates Top-1 as 'possibly closes the gap alone', H2 should NOT be Top-3 in this cycle. Defer Top-3 to cycle-007 or whichever cycle follows the Top-1 outcome. Reserve cycle budget for Top-1 quality."

- **Status:** explicit response to the NEW DIRECTIVE in `backlog.md:20-35` (F.4 from failure_analyst). Highest swing-EV but full-cycle scaffold cost.
- **Composition:** single full-resolution FNO trunk (re-use `mf_fno_transfer_bar/model.py`'s `FNO2d` at ~4.7M params, hidden=64, n_blocks=4) + `BasisHead` from `fno_coreg_residual/model.py:168-188` (K=20, zero-init last layer). Two-stage schedule: Stage 1 LF pretrain at `lr=1e-3`, Stage 2 HF joint at `lr=3e-4`; fresh AdamW + cosine per stage.
- **Cite in manifest/docstrings:** `lyu2023mffno`, GCS MF-FNO, `li2022ifc`, `niu2024mfrnp`, `yang2025mfdeeponet`, `nietocentenero2025mfae`.
- **Expected effect:** plausible composite = geomean(~0.0075, ~0.045) ≈ 0.018. Well below 0.026.
- **Risk:** new family takes a full cycle; wall-budget tight (~25 min smoke); composition deteriorates if LF pretrain locks the trunk into a representation the HF head cannot correct.
- **Confidence:** medium. Composition well-precedented across analogous backbones (DeepONet, autoencoder, GP/coregionalization); no published direct FNO+FNO-head transfer example surfaced via archive — flag for cycle-007 WebSearch when API recovers.

---

## CEO prioritization summary (from `.factory/reviews/ceo-verdict-researcher.md`)

1. **Top-1 is the load-bearing experiment for cycle-006.** Single move that could close the composite target in one step at very low risk. Strategist should propose as H1 verbatim with file:line specs.
2. **Top-2** is excellent structural hygiene but does not by itself close the gap. Either bundle into H1's diff scope or propose as small standalone H2.
3. **Top-3** is the NEW DIRECTIVE response but is a full-cycle scaffold. Defer to cycle-007.
4. **Hypothesis count target: 1, possibly 2.** Top-1 sufficient as H1. Top-2 may be H2 only if genuinely independent of H1's diff — otherwise bundle.
5. **Surface constraint:** every modified file must be in `models/**`. No `data/`, `eval/`, `references/`, `scripts/`, `factory.md`, `README.md`, `baselines/` references.
6. **Leakage-check:** strip incidental numerical substrings from hypothesis text.
7. **Realism check:** Poisson 0.0556 → 0.043-0.052; composite 0.029357 → 0.0244-0.0273.

---

## Web-access outage (operational note)

WebSearch / WebFetch returned HTTP 529 (overloaded) on every query attempted in the Researcher session. Research drew from the local archive (`.factory/archive/sources/`) — unusually rich for this exact problem space because cycle-003 already conducted ~20 web-sourced citations on HF/LF loss reweighting. **No hallucinated references** — all citations carry original BibTeX keys and arXiv IDs preserved from prior cycles or in-tree code.

Flagged for cycle-007 retry:
- Post-2024 papers on selective HF-modes-only capacity bump for elliptic problems.
- Adapter / LoRA-style lightweight HF heads on top of LF-pretrained FNO.
- Spectral-attention / frequency-conditional gating for FNO modes.
- Direct FNO-trunk + FNO-residual-head transfer reference (would confirm Top-3 composition argument empirically).

See [[patterns]] §"Local-archive fallback survives WebSearch outage when prior cycle has conducted equivalent web research".
