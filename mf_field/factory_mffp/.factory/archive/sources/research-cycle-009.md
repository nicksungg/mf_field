---
name: research-cycle-009
description: Cycle-009 Researcher synthesis — failure-targeted Mode 4 R1.5 round. O1 fno_mf_stack capacity recommendation (hidden=64, modes_per_level=(4,8,16,20)) with Nyquist-bound rationale; O2 recipe_hash source-of-truth correction (transolver_residual:14-46, not fno_coreg_residual); one new bibtex candidate stresstest2025fno; soft-correction to "Poisson > Heat modes" premise. CEO PROCEED 2026-06-02.
metadata:
  type: reference
tags:
  - factory
  - source
  - research
  - cycle-009
  - failure-targeted
  - mode-4
source: factory-archivist
date: 2026-06-02
cycle: cycle-009
ceo_verdict: PROCEED
---

# Research — Cycle-009 — Failure-Targeted Synthesis (R1.5)

**Date:** 2026-06-02
**Cycle:** cycle-009
**Source failure analysis:** `.factory/research/runs/cycle-009-baseline/failure_analysis.md`
**Web access:** WebSearch 5/5 successful; WebFetch hit two arXiv abstract-only landing pages — load-bearing capacity numbers sourced from in-archive prior cycles plus search-result snippets.
**CEO verdict (researcher):** PROCEED 2026-06-02.

## Entry state

- **Baseline:** `composite_nRMSE = 0.027729` on `experiment/11-fno_coregionalization-paper-capacity @ 18d83a6` (banked from cycle-008 H1).
- **Bar to dethrone:** parallel-bench composite **0.027429**; gap **+1.09%**.
- **Dominant lever (REVERSED vs cycle-008 baseline):** Poisson now owns **~69%** of the residual bar gap (`fno_mf_stack × ifc_poisson = 0.05961`, 1.5% over parallel-bench bar, 1.66× over IFC paper bar 0.036). Heat is essentially AT bar (0.012898, +0.7%).
- **Mutable surface:** `models/**` only.

## CEO focus areas addressed

1. **O1 — `fno_mf_stack` capacity-axis recommendation** (LEAD).
2. **O2 — `recipe_hash` portable utility** (SECONDARY, operational).
3. **O4 — FiLM-with-LF-features** (RESERVE only; correctly deferred).

## O1 — Capacity-axis recommendation (primary)

**Recommended SMOKE_DEFAULTS bump for `models/fno_mf_stack/smoke_eval.py:37-53`:**

```python
hidden=64,                       # was 32; matches in-tree full_config.json; inside MFRNP-author range (32-128)
agg_hidden=64,                   # was 32; mirrors hidden bump on aggregator MLP
n_blocks=4,                      # was 3; +33% depth, modest cost
modes_per_level=(4, 8, 16, 20),  # was (4, 8, 12, 12)
# Poisson loss weights UNCHANGED (already canonical-MFRNP: 2.0, 0.25)
```

**Nyquist-bound rationale** (per `SpectralConv2d.forward` auto-clamp at `models/fno_mf_stack/model.py:59-60` — `min(self.modes1, H // 2 + 1, H - 1)`):

| Level | Native res | rfft2 half-spectrum | Current modes_cap | Headroom | Action |
|---:|---:|---:|---:|---|---|
| 0 | 8×8 | 5 | 4 | Nyquist-bound (4/5) — bumping wastes weights | **UNCHANGED at 4** |
| 1 | 16×16 | 9 | 8 | Nyquist-bound (8/9) — bumping wastes weights | **UNCHANGED at 8** |
| 2 | 32×32 | 17 | 12 | Modest (12/17 = 71%) | **BUMP to 16 (full Nyquist)** |
| 3 | 64×64 (HF) | 33 | 12 | **Significant (12/33 = 36%)** — primary lever | **BUMP to 20 (~60% Nyquist)** |

**Variants offered:**
- Conservative fallback: `modes_per_level=(4, 8, 16, 16)` — HF stays at SpecB-FNO sweet-spot (16).
- Aggressive: `modes_per_level=(4, 8, 16, 24)` — HF pushed to 72% Nyquist, against diminishing-returns ceiling.

**Parameter-count delta:** per-FNO ~4-5× larger; total model ~250k → ~1.0M params (well below `fno_coregionalization` paper-config ~2.6M).

**Wall budget:** current smoke 2-3 min wall; bumped config est. 4-8 min on H100. Kill-switch: `wall > 25 min OR ifc_poisson > 0.0594 → REVERT`.

**Expected effect:**
- Lower-bound: matches `full_config.json` projected smoke = 0.054-0.058 (closes ~70% of remaining bar gap).
- Upper-bound: 0.048-0.052 (dethrones bar; composite 0.0245-0.0250).
- Counterfactual: Poisson 0.05961 → 0.05871 closes 70% of the +1.09% bar gap.

## O2 — `recipe_hash` source-of-truth correction (IMPORTANT)

**Cycle-008's claim was wrong.** Failure_analysis cited the canonical `recipe_hash` pattern as living in `models/fno_coreg_residual/smoke_eval.py` lines ~113-123 / ~461-485. That file is 364 lines long and contains **NO `recipe_hash`** (`grep -n recipe_hash models/fno_coreg_residual/smoke_eval.py` returns nothing).

**Actual canonical source:** `models/transolver_residual/smoke_eval.py:14-46` (helper) + lines 108-120 (resume guard) + lines 144-149 (save). Also lives in `models/transolver_attention_fusion/smoke_eval.py`. The pattern was **never** in any FNO family.

**Cherry-pick destination:** new `models/_common/recipe_hash.py` (project-local; no external library per `research_constraints` — no Hydra/Determined/MLflow dependency for one 3-line helper).

```python
# models/_common/recipe_hash.py
from __future__ import annotations
import hashlib
import json
from typing import Any, Mapping


def recipe_hash(defaults: Mapping[str, Any]) -> str:
    payload = json.dumps(dict(defaults), sort_keys=True, default=str).encode()
    return hashlib.sha256(payload).hexdigest()[:12]
```

`default=str` handles `numpy.int64/float64` and tuple→list coercion; `dict(defaults)` materializes frozendict/MappingProxy.

**Target families (priority order):**
1. `models/fno_mf_stack/smoke_eval.py` (cycle-009 H1 touches this anyway — clean bundling)
2. `models/fno_coreg_residual/smoke_eval.py` (historical cycle-003 contamination pathway)
3. `models/fno_coregionalization/smoke_eval.py` (currently banked best — protect from drift)
4. `models/fno_coreg_conditioned/smoke_eval.py` (if O4 fires later)
5. `models/mf_fno_transfer_bar/smoke_eval.py` (protect bar from accidental smoke-side drift)

**DO NOT cherry-pick** the three-stage curriculum gating logic — it doesn't exist in `fno_coreg_residual` anyway (lived briefly on `experiment/13 @ 420a51c`, reverted via NK2). Just the helper.

**Risk floor:** zero. Cannot regress composite; only invalidates stale cache (intended) or locks-in fresh cache (intended). Indirectly closes cycle-003 backlog item project-wide.

**Bundling:** H1 + H2 can land as one PR (cleanest cache-safety story — the recipe_hash field added to `fno_mf_stack/smoke_eval.py` at the same time as the capacity bump means a stale cycle-008 H1 checkpoint cannot silently load against cycle-009 bumped weights).

## NEW bibtex candidate: `stresstest2025fno`

| bibtex_key | Reference | Use in cycle-009 |
|---|---|---|
| `stresstest2025fno` (working name) | "Forcing and Diagnosing Failure Modes of FNO Across Diverse PDE Families" ([arXiv:2501.11428](https://arxiv.org/abs/2501.11428), Jan 2025) | O1 capacity-axis ceiling argument — per-PDE-family stress-test reports `modes=16` is sufficient for elliptic regimes. Confirms elliptic spectrum is low-mode-dominated; per-fidelity-modulation is the harder dimension. |

**Status:** ready for `papers_summary.csv` (human-action populating per [[papers-summary-csv-state]]). Brings total ready-keys to **10** (9 prior cycle-008 keys + 1 new).

All other citations in cycle-009 research.md are carry-over from existing archive notes — no additional source-note files required.

## Soft-correction to failure_analysis premise

**Failure_analysis's claim:** "Poisson tends to need higher modes than Heat at the same grid resolution."

**Soft-correction (NOT well-supported by 2024-2026 literature):** both elliptic Poisson and parabolic Heat are **low-mode-dominated** per the [arXiv:2501.11428] stress-test ("in smooth, elliptic, or laminar regimes, most of the energy is captured by a handful of low-frequency modes"). The asymmetry in our project is **m-modulation non-monotonicity**, not spatial-spectrum content.

**Implication for O1 rationale:** the capacity-bump justification is:
1. Under-resolved HF FNO (current 12/33 = 36% Nyquist on 64×64 grid), AND
2. Increased channel width needed to resolve the m-modulation residual across the 4-FNO stack.

NOT a "Poisson needs more spectral content than Heat" argument. CEO accepts this correction — does not change the recommendation, just the rationale.

## O4 — Reserve (FiLM-with-LF-features)

Cycle-009 web round produced **NO new bibliography** for `γ(m, LF_features)` revision. Closest precedents remain cycle-008-curated: [[cao2025mflno]], [[beggs2025pdecond]], [[herde2024poseidon]]. **DEFER to cycle-010+** unless O1 lands net-negative. Cite at most 2 papers if pursued: `cao2025mflno` and `beggs2025pdecond` (both already validated in cycle-008).

## NK-zone sidesteps (all hypotheses)

- **NK1** (pure m-conditioning on HF-only FNO, cycle-008 H2): sidestepped by O1 (no FiLM); sidestepped by O2 (operational only).
- **NK2** (frozen-LF curricula on co-evolved residual ladders, cycle-008 H3): sidestepped by O1 (no curriculum); `fno_mf_stack` is LF/HF-independent by design, so a curriculum would be carve-out-legal but Strategist MUST NOT bundle one with H1.
- **NK3** (MFRNP loss-weight transfer on coregionalization-family, cycles 003/006/007): sidestepped by O1 (capacity not recipe; poisson loss weights `(2.0, 0.25)` already canonical-MFRNP — no perturbation).

## CEO verdict (cycle-009 R1.5)

- **Verdict:** PROCEED (2026-06-02).
- **Issues found:** none. The source-of-truth correction is a net positive — saves the Builder a wasted lookup.
- **Instructions for R2 Strategist:** generate exactly 2 hypotheses (matches `max_new: 2`):
  - **H1 (LEAD, EXPLOIT, code):** O1 capacity bump on `fno_mf_stack`; primary `(4,8,16,20)` with conservative `(4,8,16,16)` as wall-time fallback. Kill-switch: `Poisson > 0.0594 OR wall > 25 min → REVERT`. Citations: `niu2024mfrnp`, `li2020fno`, `lyu2023mffno`, `stresstest2025fno`.
  - **H2 (SECONDARY, EXPLORE-operational, code):** O2 recipe_hash portable utility. Surfaces: NEW `models/_common/recipe_hash.py` + edits to `fno_mf_stack/smoke_eval.py` (bundled with H1), `fno_coreg_residual/smoke_eval.py`, `fno_coregionalization/smoke_eval.py`. Source: `models/transolver_residual/smoke_eval.py:14-46`. **H2 can land as part of H1's PR.**

## Mutable-surface map

- `models/fno_mf_stack/smoke_eval.py` — H1 (SMOKE_DEFAULTS at lines 37-53) + H2 (recipe_hash integration)
- NEW `models/_common/recipe_hash.py` — H2 helper
- `models/fno_coreg_residual/smoke_eval.py` — H2 application
- `models/fno_coregionalization/smoke_eval.py` — H2 application

## Related notes

- [[research-cycle-008]] — last cycle's research; bibliography carried forward; sourced corrected this cycle
- [[research-cycle-006]], [[research-cycle-005]], [[research-cycle-003]], [[research-cycle-002]] — prior cycle notes
- [[anisotropic-spectral-modes-fno]] — re-verified clean on `fno_mf_stack/model.py` (no latent cycle-007-H1-style constructor bug)
- [[cycle-007-constructor-fix-pattern]] — O2-axis audit was a no-op on this family
- [[niu2024mfrnp]] — architectural template for `fno_mf_stack`; Poisson5_config canonical loss weights
- [[li2020fno]] — canonical FNO backbone; mode/width ablation ranges
- [[li2022ifc]] — IFC paper bar reference
- [[per-dataset-recipes-mf-field]] — confirms (2.0, 0.25) is Poisson-specific
- [[cao2025mflno]], [[beggs2025pdecond]], [[herde2024poseidon]], [[rahman2024codano]] — O4 deferred bibliography
- [[papers-summary-csv-state]] — now 10 keys ready including new `stresstest2025fno`
