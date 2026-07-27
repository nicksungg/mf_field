---
name: cycle-003-strategy-snapshot
description: Cycle-003 single-hypothesis strategy (H1 only) — port H4's resolve_fidelity_weights into H3 to activate Poisson HF up-weighting (2.0, 0.25); CEO PLAN APPROVED with documented leakage-scanner false positive
metadata:
  type: project
project: factory_mffp
date: 2026-05-15
cycle: 003
source: factory-archivist
tags:
  - factory
  - strategy
  - factory_mffp
  - cycle-003
---

# Strategy Snapshot: factory_mffp — cycle-003 (2026-05-15)

## CEO Verdict
**PLAN APPROVED** (HARD GATE PASS). Both Researcher and Strategist reviews PROCEED. One MEDIUM leakage-scanner flag — documented as known precheck-bookkeeping false positive (substring collision on dataset name `"poisson"`); same pattern as cycles 001 and 002 reverts.

## Cycle-Entry Metric
- **Project best:** `composite_nRMSE = 0.04420` (geomean of `ifc_heat=0.02634` + `ifc_poisson=0.07416`).
  - Source: cycle-002 H3 `fno_coreg_residual` on branch `experiment/4-fno_coreg_residual` @ `0c46f43`.
  - **Master is at 1.6595** because cycle-001 and cycle-002 were factory-reverted for precheck-bookkeeping bugs — model code is intact on the experiment branch only.
- **Paper bar (li2022ifc):** Heat=0.074, Poisson=0.036, geomean=0.0516. Heat beats by 2.81×; Poisson misses by 2.06×.
- **Datasets beating paper:** 1/2.

## Single-Hypothesis Design (CEO H1-only directive)

CEO directive: generate exactly 1 hypothesis. GradNorm-lite (Researcher's optional H2) deferred to cycle-004 to **cleanly attribute** the composite move to the loss-weighting knob alone. `hypothesis_budget.max_new = 2` is the ceiling, not the floor.

### H1: `fno_coreg_residual_poisson_loss_reweighting`
- **Category:** FIX
- **Failure mode:** F6 `ABSENT_POISSON_LOSS_WEIGHTING` (sole remaining gap to two-of-two paper-beating; 100% of failing-dataset surface).
- **Branch base:** `experiment/4-fno_coreg_residual` (cycle-002 H3 — current best 0.0442). **NOT master.**
- **Mutable surface:** `models/fno_coreg_residual/**` only.
  - `smoke_eval.py` — port `resolve_fidelity_weights(dataset_name, p)` helper from `models/fno_mf_stack/smoke_eval.py` (H4 family); wire into `compute_losses`; add `poisson_hf_weight=2.0`, `poisson_lf_weight=0.25` to `SMOKE_DEFAULTS`.
  - `INSPIRATION.md` — append citations: `mfrnp_poisson5_config` (primary provenance), `boulle2023ellipticdata` (theoretical grounding for elliptic vs parabolic distinction), `chen2018gradnorm` (theoretical context only — no code ported).
  - `full_config.json` — optional, only if `_poisson_loss_knob` keys need renaming for `SMOKE_DEFAULTS` consistency.
- **Mechanism (verbatim Researcher-spec'd, CEO-confirmed):**
  ```python
  def resolve_fidelity_weights(dataset_name: str, p: dict) -> tuple[float, float]:
      is_poisson = "poisson" in (dataset_name or "").lower()
      if is_poisson:
          return float(p.get("poisson_hf_weight", 2.0)), float(p.get("poisson_lf_weight", 0.25))
      return float(p.get("hf_loss_weight", 1.0)), 1.0
  ```
- **Defaults verbatim from MFRNP `Poisson5_config.yaml`:** `(HF=2.0, LF=0.25)` — **NOT in MFRNP paper**, single inline comment `"# highest fidelity weight"`. H4 (4-fid FNO) cross-architecture validated by recovering Poisson to 0.0596.
- **Heat path:** uniform `(1.0, 1.0)` unchanged — basis-head + FNO does the work.
- **Per-fidelity output normalization:** stays in place (cycle-001 fix); loss weights apply on top of normalized residuals.

## Compositional Framing (CEO-adopted)
H3 already provides **architectural** IFC-path asymmetry (continuous-m basis head + per-fidelity output normalization). Cycle-003 H1 adds **loss-weighting** MFRNP-path asymmetry on top. The two SOTA routes (IFC architectural + MFRNP loss-weighting) **compose orthogonally** on a single architecture.

## Expected Impact (anchored to *measured* H4 Poisson, not forecast)
- `ifc_poisson` test nRMSE: floor at H4-measured **0.0596** (loss-weighting on uncomposed FNO at hidden=32). Plausible upside below 0.0596 because H3 has hidden=64 + basis head.
- `ifc_heat` test nRMSE: unchanged at ≈0.0263 (resolver gates off Heat).
- `composite_nRMSE` floor: **geomean(0.02634, 0.0596) ≈ 0.0396** (-10% vs cycle-003 entry 0.0442; **-23% vs paper geomean 0.0516**).
- `n_datasets_beating_paper`: 1 → potentially 2 if H3 hybrid clears 0.036 on Poisson under loss-weighting recipe.

## Failure Mode Map (cycle-003 entry)
| Code | Mode | Status |
|---|---|---|
| F1 | `ifc_poisson` value-scale collapse | resolved on H3 (per-fidelity output normalization) |
| F2 | `ifc_heat` backbone gap | resolved on H3 (FNO + basis head) |
| F4 | Smoke-default under-capacity | resolved on H4/H3 (hidden=64, modes=(4,8,12,12), 3 blocks) |
| F5 | Inverse-complementary families | resolved on H3 (hybrid wins Heat outright) |
| **F6** | **`ABSENT_POISSON_LOSS_WEIGHTING`** | **sole remaining gap — H1 target** |
| F3 | Missing paper baselines splits (meta) | fixed-surface human action — out of scope |

All four prior failure modes (F1/F2/F4/F5) **resolved** on H3; only F6 remains.

## Known Precheck Bookkeeping False Positive
- **Scanner output:** `leaked_token: "poisson"`, `leak_type: "specific_value"`, `source_file: factory.md`, context `"fno_coreg_residual_poisson_loss_reweighting. P"`.
- **Why false positive:** `factory.md:42` says `"smoke datasets are ifc_heat and ifc_poisson"` — the token is a **dataset name**, not a value. The H1 mechanism *must* gate on `"poisson"` to route the published MFRNP recipe; rephrasing cannot remove the token without inverting the mechanism.
- **Same pattern as 4 prior factory reverts.** Sprint Standup tracks as "ground_truth_leakage substring-collision". Each was `revert_bookkeeping_keep_intent` — model science good, precheck bug tripped the gate.
- **Out-of-scope follow-up:** scanner needs to distinguish dataset-name tokens from value tokens. Factory-infrastructure issue, not model-science.

## Why GradNorm-Lite Deferred to Cycle-004
- CEO directive binding — clean attribution of cycle-003 composite move to loss-weighting knob alone.
- Adding GradNorm simultaneously confounds attribution between fixed-recipe and adaptive-recipe contributions.
- Cycle-004 then has a known H1-only baseline to compare GradNorm against.

## Surface Constraints (re-verified)
- **mutable_surfaces:** `models/**` only.
- **fixed_surfaces:** `data/**`, `baselines/**`, `eval/**`, `references/**`, `factory.md`, `README.md`, `scripts/**` — **no fixed-surface touches in H1**.
- **research_constraints:** no new family (additive on H3); smoke wall-time unchanged from cycle-002 H3 (well under 30 min on H100); no external API/weights at eval time.

## Builder Pre-Flight (mandatory)
Dual-dataset 2-epoch smoke required before declaring ready:
- `--dataset_dir data/ifc_heat`: resolved weights MUST be `(1.0, 1.0)` (regression guard).
- `--dataset_dir data/ifc_poisson`: resolved weights MUST be `(2.0, 0.25)` (activation check).
Both contract JSONs must include `metric_value`.

## Risk Profile: LOW
- (a) Heat regression — only if resolver activates on Heat; gating on `"poisson"` substring + dual-dataset pre-flight guards.
- (b) Loss-weight × normalization interaction — Builder diffs against H4's `compute_losses` site to confirm same ordering.
- (c) HF/LF role inversion — copy-paste from H4's working implementation; signature `(hf, lf) = resolve_fidelity_weights(...)` matches H4 call sites.

## Backlog
- **No new in-mutable-surface backlog items this cycle.**
- Researcher flagged 7 new bibtex rows for `papers_summary.csv` (chen2018gradnorm, kendall2018uncertainty, wang2020gradpathologies, wang2021ntkpinn, boulle2023ellipticdata, zhan2024ada2mf, mfrnp_poisson5_config) — repo root file (fixed surface), human action.
- Cycle-004 candidates (deferred, not added as new items):
  - `fno_coreg_residual_gradnorm` — if cycle-003 H1 lands ≤ 0.0396 and next leverage is decoupling from hand-tuned (2.0, 0.25).
  - Per-dataset Poisson capacity / modes override — conditional on H1 leaving Poisson > 0.036.
  - Basis-head calibration probe — conditional on H1 leaving Poisson > 0.036 AND basis-head MLP weights stay near zero-init.

## Related
- Cycle-002 strategy snapshot: [[cycle-002-strategy]]
- Cycle-001 strategy snapshot: [[cycle-001-strategy]]
- Project dashboard: [[factory_mffp]]
