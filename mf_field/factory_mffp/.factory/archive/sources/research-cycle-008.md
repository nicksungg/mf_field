---
name: research-cycle-008
description: Cycle-008 Researcher synthesis — failure-targeted Mode 4 web round. 5 new external citations validated (cao2025mflno, rahman2024codano, herde2024poseidon, beggs2025pdecond, engstruct2025mfft). Three hypotheses ranked A1 / B1 / B3; MFRNP loss-recipe SKIP confirmed; explicit bundling and kill-switch guidance. CEO PROCEED 2026-06-02.
metadata:
  type: reference
tags:
  - factory
  - source
  - research
  - cycle-008
  - failure-targeted
  - mode-4
source: factory-archivist
date: 2026-06-02
cycle: cycle-008
ceo_verdict: PROCEED
---

# Research — Cycle-008 — Failure-Targeted Synthesis

**Date:** 2026-06-02
**Web access:** WebSearch / WebFetch returned successfully (no HTTP 529
outage as in cycles 006/007). 5 focus-area searches + 8 follow-ups
completed. 4 successful WebFetches; IFC paper PDF + Lyu 2023 PDF returned
encoded streams (abstracts + secondary sources cover load-bearing claims).
**CEO verdict (researcher):** PROCEED 2026-06-02.

## Entry state

- **Baseline:** `composite_nRMSE = 0.030408` on
  `experiment/9-fno_coregionalization-constructor-fix @ 1249f2d`.
- **Bar to dethrone:** `mf_fno_transfer_bar` parallel-bench composite
  **0.027429**; **−10% target = 0.02469**, gap from baseline +21.7%.
- **Dominant lever:** **ifc_heat** (log-space contribution **12.6× larger**
  than ifc_poisson).
- **Mutable surface:** `models/**` only.
- **Skip per CEO verdict:** MFRNP loss-recipe / reweighting (REVERT 3/3
  in cycles 003 H1, 006 H1, 007 H2).

## New external citations (cycle-008 web round)

5 new bibtex_keys validated and ready for the pending
`papers_summary.csv` (see [[papers-summary-csv-state]]):

| Key | Title | Year/Venue | Use |
|---|---|---|---|
| [[cao2025mflno]] | MF-LNO: Laplace Neural Operator for parametric PDEs | arXiv:2502.00550 (Feb 2025) | Non-monotone fidelity-correlation pattern; linear+nonlinear residual decomposition |
| [[rahman2024codano]] | CoDA-NO: Codomain Attention Neural Operator | NeurIPS 2024 (arXiv:2403.12553) | Codomain-attention complement to FiLM conditioning |
| [[herde2024poseidon]] | Poseidon / scOT foundation model for PDEs | NeurIPS 2024 (arXiv:2405.19101) | Foundation-model-scale FiLM-via-LayerNorm precedent |
| [[beggs2025pdecond]] | Conditioning on PDE Parameters | arXiv:2509.09599 (Sep 2025) | Direct architectural blueprint for `fno_coreg_conditioned` (B1) |
| [[engstruct2025mfft]] | MF Pretrain-finetune Neural Operator (structural dyn.) | Eng. Struct. 2025 | 5th independent LF→HF schedule citation |

Carry-over keys (already in archive — re-confirmed this cycle):
[[lyu2023mffno]], [[gcs2023mffno]], [[tran2023ffno]], [[pan2022hyperfno]],
[[li2022ifc]], [[li2020fno]], [[niu2024mfrnp]], [[yang2025mfdeeponet]],
[[nietocentenero2025mfae]].

## Canonical 2024-2025 conditioning pattern

**The IFC outer-product basis `f(x, m) = B(m) · h(x)` is a 2022-era design.**
Three independent 2024-2025 papers canonicalise **FiLM-via-LayerNorm** as
the modern PDE-operator conditioning channel:
[[herde2024poseidon]], [[beggs2025pdecond]], [[rahman2024codano]].

Contemporary composition:

```
f(x, m) = FNO(x; γ(m), β(m))      where γ, β : MLP([m, m²])
LayerNorm(z) → γ(m) * LayerNorm(z) + β(m)
```

Captured in detail in [[patterns]] §"FiLM-via-LayerNorm is the canonical
2024-2025 conditioning channel in PDE neural operators".

## Hypothesis menu — ranked

| Rank | Hyp | Family | Surface | Composite delta | Wall budget | Risk | Category |
|---:|---|---|---|---|---|---|---|
| **1** | **A1** | `fno_coregionalization` | `smoke_eval.py` SMOKE_DEFAULTS only | heat 0.01551→0.013 → composite ~0.028 | +6-10 min | LOW (paper config; banked schedule) | (a) capacity |
| **2** | **B1** | NEW `fno_coreg_conditioned/` | new family directory | speculative; collapses Heat-Poisson asymmetry; composite ~0.022-0.025 | +25 min (full scaffold) | MEDIUM (new architecture; no IFC-specific evidence) | (c) architecture |
| **3** | **B3** | `fno_coreg_residual` | `smoke_eval.py` + checkpoint guard | composite ~0.029-0.033 (Heat 0.018-0.022, Poisson 0.05-0.06) | +5 min | MEDIUM (cycle-003 checkpoint contamination — mandatory `recipe_hash` guard) | (b) schedule |
| 4 | A3 (DEFER) | NEW F-FNO family | full spectral refactor | speculative | full new family | medium | (c) architecture |
| 5 | C1 | `fno_mf_stack` | SMOKE_DEFAULTS | Poisson 0.05961→0.052-0.055 | +3 min | low | (a) capacity |
| DEFER | D1 | `mf_fno_transfer_bar` | smoke train | tightens bar number — **counterproductive** for −10% target | — | — | (d) bar |

### A1 — paper-config wire-up of `fno_coregionalization`

- **Wire-up only**, no `model.py` change (constructor was repaired in
  cycle-007 H1 — accepts all kwargs).
- **Verbatim from `models/fno_coregionalization/full_config.json`** which is
  an in-tree TODO:
  - `K=10 → 20`
  - `b_hidden=64 → 128`
  - `n_blocks=4 → 6`
  - `hidden_channels=32 → 128`
  - `modes_cap=12 → 16`
- Expected heat 0.01551 → ~0.013 (paper-K-config implied), composite ~0.028.
- **Kill-switch:** Heat > 0.0194 → REVERT.
- **If wall-time tight:** lower `epochs=200 → 120` with stronger warmup.

### B1 — NEW family `fno_coreg_conditioned`

- **Highest swing-EV in this cycle**, speculative; could collapse
  `FAMILY_PDE_SPECIALIZATION_ASYMMETRY` into a single-family answer.
- **Mode A (preferred):** FiLM-via-LayerNorm — replace each `GroupNorm`
  in `FNOBlock` with `FiLMNorm(channels, m_feat_dim)`:
  `γ(m), β(m) = MLP([m, m²])`; output `γ * GroupNorm(z) + β`.
- **Mode B (fallback):** broadcast-channel conditioning — concatenate
  `B(m) ∈ R^K` (broadcast to `(K, H, W)`) to the FNO input channels.
- Required files:
  - `models/fno_coreg_conditioned/model.py` (FNOBlock + FiLMNorm)
  - `models/fno_coreg_conditioned/smoke_eval.py` (copy from
    `fno_coregionalization`, keep H2 schedule, drop K/b_hidden or
    repurpose for FiLM MLP)
  - `models/fno_coreg_conditioned/manifest.json`
  - `models/fno_coreg_conditioned/INSPIRATION.md` (cite [[li2022ifc]],
    [[li2020fno]], [[lyu2023mffno]], [[beggs2025pdecond]],
    [[herde2024poseidon]])
- **Kill-switch:** wall > 25 min OR Heat > 0.0194 → REVERT.

### B3 — Three-stage curriculum on `fno_coreg_residual`

- **MANDATORY:** add `recipe_hash` field to checkpoint AND make the
  resume guard require recipe_hash match. Without this, B3 inherits the
  **cycle-003 contamination failure mode**.
- Stages:
  - Stage 1 (LF pretrain): per-fidelity LF FNOs at `pretrain_lr=1e-3`
    for `pretrain_frac=0.25 × epochs ≈ 50 ep`. Heat keeps uniform weights;
    Poisson opt-in to "LF-only mask" — **does NOT add (2.0, 0.25) MFRNP
    weights**.
  - Stage 2 (residual fine-tune): freeze LF stack, train HF FNO residual
    at `finetune_lr=3e-4` for `0.5 × epochs ≈ 100 ep`.
  - Stage 3 (basis head unfreeze): unfreeze + add coregionalization-residual
    basis head for `0.25 × epochs ≈ 50 ep`.
- Expected composite ~0.033 (Heat 0.018-0.022, Poisson 0.05-0.06).
- **Kill-switch:** if Stage 3 regresses Heat by >+25% over Stage 2
  checkpoint, REVERT to Stage 2 (do not re-add basis head).

## Skip directive (re-stated)

**MFRNP loss-recipe variants — SKIP confirmed.** REVERT 3/3 prior holds
(cycles 003 H1, 006 H1, 007 H2). **NONE of A1 / B1 / B3 add MFRNP-style
loss reweighting:**

- A1 = capacity bump only (no recipe change).
- B1 = new architecture (no loss weights).
- B3 = redistributes existing weights across stages without changing
  them; heat keeps uniform.

Anti-pattern guard: any new hypothesis touching MFRNP-style HF/LF
reweighting needs (i) heat-invariance kill-switch and (ii) best-of-N
seeds with frozen heat seed — *not* worth re-attempting a 4th time.

## Bundling guidance

- **A1 + B1 INDEPENDENT** — different families, different files. Heat
  regression test for A1 stays clean if B1 lands as a separate PR. CEO
  approved up to 2 hypotheses bundled in cycle-008.
- **A1 + B3 share the H2 schedule code path** — bundling would confound
  the per-cycle Heat-invariance kill-switch. **Keep separate.**
- **If only one fits the budget**, A1 first; B1 in cycle-009.
- **If two fit**, A1 + B1 is the right pair.
- **If three fit**, A1 + B1 + B3 with B3 last (mandatory recipe_hash
  checkpoint guard adds wall time).

## CEO verdict

- **Verdict:** PROCEED (2026-06-02).
- **Issues found:** none.
- **Instructions for R2 Strategist:** generate at most 3 hypotheses;
  default ordering A1, B1, B3; each must include explicit kill-switch
  threshold, per-cell expected nRMSE, and mutable-surface scope; NO
  MFRNP loss-recipe variants; NO bundling A1+B1+B3 as a single PR.

## Mutable-surface map

- `models/fno_coregionalization/smoke_eval.py` — A1
- `models/fno_coreg_conditioned/{model.py,smoke_eval.py,manifest.json,INSPIRATION.md}` — B1 (NEW)
- `models/fno_coreg_residual/smoke_eval.py` + checkpoint format — B3
- `models/mf_fno_transfer_bar/smoke_eval.py` — D1 (DEFERRED)
- `models/fno_mf_stack/smoke_eval.py` — C1 (DEFERRED)

## Related notes

- [[failure-analysis-cycle-008]] — source failure analysis driving
  this research round
- [[research-cycle-006]], [[research-cycle-005]],
  [[research-cycle-003]], [[research-cycle-002]] — prior cycle notes
- [[lf-hf-pretrain-fraction-survey]] — pretrain_frac literature
  comparison
- [[anisotropic-spectral-modes-fno]] — (modes_h, modes_w) canonical
  split, repaired in cycle-007 H1
- [[per-dataset-recipes-mf-field]] — recipe-dispatch survey
- [[patterns]] — patterns.md (FiLM-via-LayerNorm pattern added this cycle)
- [[papers-summary-csv-state]] — pending csv state (9 new keys now ready)
- All [[cao2025mflno]], [[rahman2024codano]], [[herde2024poseidon]],
  [[beggs2025pdecond]], [[engstruct2025mfft]], [[pan2022hyperfno]],
  [[tran2023ffno]] sibling source notes
