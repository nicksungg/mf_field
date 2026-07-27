---
name: research-cycle-010
description: Cycle-010 Researcher synthesis — failure-targeted Mode 4 round. O1 fno_mf_stack capacity-axis SECOND step (hidden=96, modes_per_level=(4,8,16,24), n_blocks=4) as H1 LEAD; O2 LF→HF curriculum with frozen LF stage 2 on fno_mf_stack as H2 SECONDARY (NK2 carve-out applies — LF/HF-independent design). O3 (B(m,LF_features)) and O4 (γ(m,LF_features) new family) DEFERRED — composite-mover prior weak for non-leader cells. Cycle-009 H1+H2 measured slope log(nRMSE)/log(params)≈−0.39; cycle-010 H1 predicted −10 to −22% Poisson (saturation-aware). 6 new bibtex candidates validated (15 keys ready for papers_summary.csv).
metadata:
  type: reference
tags:
  - factory
  - source
  - research
  - cycle-010
  - failure-targeted
  - mode-4
source: factory-archivist
date: 2026-06-02
cycle: cycle-010
ceo_verdict: pending
---

# Research — Cycle-010 — Failure-Targeted Synthesis (Mode 4)

**Date:** 2026-06-02
**Cycle:** cycle-010
**Source failure analysis:** `.factory/research/runs/cycle-010-baseline/failure_analysis.md`
**Web access:** WebSearch 10/10 successful across 5 focus areas; WebFetch landed 2 readable HTML excerpts (PI-RINO; UFNO-FiLM) and consistently returned PDF-binary or 403 for arXiv PDFs / ScienceDirect. Load-bearing protocol numbers sourced from in-tree MFRNP YAML configs, prior-cycle archive (cycles 005-009), and search-result snippets.
**CEO verdict (researcher):** Pending (this archive entry written immediately after Researcher; verdict will land at `.factory/reviews/ceo-verdict-researcher.md`).

## Entry state

- **Baseline:** `composite_nRMSE = 0.022161` on `experiment/14-fno_mf_stack-capacity-and-recipe-hash @ 0b6e6eb` (cycle-009 H1+H2 banked; identical reproduction in cycle-010 baseline).
- **Bar already beaten:** IFC-ODE2 composite 0.0516 → 0.43× (2.33× under); strategic target shifted to IFC-GPODE composite 0.0331 → currently 0.67× (already 33% under).
- **Dominant lever:** Poisson owns the entire remaining published-bar gap. `fno_mf_stack × ifc_poisson = 0.038120` is the load-bearing composite cell — 1.06× over IFC-ODE2, 2.12× over IFC-GPODE; no challenger within 1.9×.
- **Composite sensitivity:** closing Poisson best → 0.018 (GPODE) unlocks −31% composite; closing only to 0.036 (ODE2) unlocks −2.8%. Heat closure unlocks 0% (already past every published bar).
- **Mutable surface:** `models/**` only.
- **NK-zones in force:** NK1 (pure-m HF-only conditioning, c008 H2 falsified); NK2 (frozen-LF on co-evolved residual ladders, c008 H3 falsified) — carve-out for LF/HF-independent designs like `fno_mf_stack`; NK3 (MFRNP loss-weight transfer to coregionalization family, 3/3 REVERT).

## CEO focus areas addressed (5 sections O1-O5)

### O1 — FNO capacity scaling for elliptic PDE (Poisson)

**Recommended SMOKE_DEFAULTS bump for `models/fno_mf_stack/smoke_eval.py:39-55`:**

- **Conservative (H1 LEAD):** `hidden=96, modes_per_level=(4, 8, 16, 24), n_blocks=4` (Nyquist HF 24/33=73%; param count ~2.0-2.2M).
- **Aggressive fallback:** `hidden=128, modes_per_level=(4, 8, 16, 24), n_blocks=5` (~3.5M; matches `fno_coregionalization` paper-config in magnitude).
- **HARD HOLD:** `modes_per_level[3] ≤ 24` — `fnospectralperspective2024` saturation warning + `stresstest2025fno` fixed-config evidence argues against modes > ~24 on 64×64 elliptic.
- **HARD HOLD:** `hf_loss_weight=1.0, baseline_anchor_weight=0.5, poisson_hf_weight=2.0, poisson_lf_weight=0.25` (canonical MFRNP; NK3-blocked from perturbation).

**Mandatory dual kill-switches (carry from cycle-009):**
- Absolute: `Poisson_test > 0.0594` (cycle-008 baseline) → REVERT.
- Absolute: `Heat_test > 0.0594` → REVERT.
- Wall: > 1500s (~25 min) → REVERT.
- `recipe_hash` checkpoint guard (already in `_common/recipe_hash.py` from cycle-009 H2) MUST gate resume — so a stale c009-h1h2 ckpt cannot silently load against c010 weights.

**Expected impact:** Poisson 0.038 → 0.030-0.034 (−10 to −22%); composite 0.0197-0.0212 (−5 to −11%). Realistic range based on saturation flattening of the cycle-009 H1+H2 slope.

**Citations:** [[niu2024mfrnp]], [[li2020fno]], [[lyu2023mffno]], [[stresstest2025fno]], [[mutransferfno2025]], [[fnospectralperspective2024]].

**Confidence: HIGH.** Capacity-axis prior is the strongest evidence type in project history (H1 c008 + H1 c009 + H2 c009 all positive).

### O2 — Two-stage LF→HF curriculum on `fno_mf_stack` (NK2 carve-out)

**Recommended addition for `models/fno_mf_stack/smoke_eval.py:171-291` (training loop + `compute_losses`):**

- `pretrain_frac=0.40` (within published 0.25-0.50 band; below `pretrain_lowerdims2024` saturation flag).
- **Stage 1 (LF-only):** fresh `Adam @ lr=1e-3, weight_decay=1e-5`, fresh `CosineAnnealingLR(T_max=80, eta_min=1e-6)`. Skip HF residual + aggregator-anchor terms.
- **Stage 2 (joint with LF frozen):** at epoch 80, freeze `lf_fnos[0..2]` via `.requires_grad_(False)`. Fresh `Adam @ lr=3e-4` + fresh `CosineAnnealingLR(T_max=120, eta_min=1e-6)`. Resume full joint loss.
- Poisson recipe `(hf_loss_weight=2.0, lf_loss_weight=0.25)` UNCHANGED across stages.

**NK2 carve-out analysis (load-bearing):**
- NK2 closed frozen-LF curricula on **co-evolved residual ladders** (`fno_coregionalization`, `fno_coreg_residual`) where LF/HF share parameters via `B(m)·h(x)`.
- `fno_mf_stack` has 4 **independent** `SmallFNO` modules (`models/fno_mf_stack/model.py:136-242`); coupling only through the MFRNP aggregator MLP (~10k params).
- Freezing `lf_fnos[0..2]` after Stage 1 matches `yang2025mfdeeponet`'s freeze-LF pattern exactly.

**Mandatory dual kill-switches (novel carve-out — extra paranoia):**
- Absolute: Poisson test > 0.0594; Heat test > 0.0594 → REVERT.
- Inter-stage: Stage-2 best_val ≥ 0.90 × Stage-1 best_val (must reduce ≥10%) — else REVERT to Stage-1 ckpt, report `STAGE_2_NO_IMPROVEMENT`. **Mirrors cycle-008 H3 dual kill-switch.**
- Wall: > 1800s → REVERT.
- `recipe_hash` must hash `pretrain_frac, stage2_freeze_lf` into ckpt key.

**Expected impact:** Poisson 0.038 → 0.030-0.035 (−10 to −20%).

**Citations:** [[lyu2023mffno]] (primary protocol), [[yang2025mfdeeponet]] (freeze pattern), `gcs2023mffno`, `pretrain_lowerdims2024` (saturation warning), [[niu2024mfrnp]] (parent architecture).

**Confidence: MEDIUM-HIGH.** Risk: MFRNP aggregator MLP may be load-bearing Poisson mechanism (failure_analysis §1.3); freezing LF stack might deny it cross-fidelity signal. Mitigation: dual kill-switch catches within Stage 2.

**Bundling guidance: H1 and H2 MUST land as SEPARATE PRs** — both touch `smoke_eval.py:39-55` SMOKE_DEFAULTS; confounded bundle would not let attribution survive.

### O3 — K-basis parametrization for coregionalization (DEFER / RESERVE)

`B(m, lf_feat)` on `fno_coregionalization` — replace `MLP([m, m²])` with mean-pooled LF features as additional input.

**Status: DEFER TO BACKLOG OR USE AS H3 RESERVE.**
- Dominant gap is `fno_mf_stack × poisson`, not `fno_coregionalization × poisson` (which is 0.598, 16.6× over leader).
- Recovering this cell to even 0.030 does not change composite leader.
- NK1-adjacent — pursue with caution if cycle-011+ revives.

**Citations:** [[li2022ifc]], [[liu2022neuralcoreg]], [[ufnofilm2025]], [[rahman2024codano]] (+ `wang2021mfhogp` arXiv:2006.04972).

### O4 — γ(m, LF_features) FiLM conditioning prior art (DEFER)

NK1-safe alternative to cycle-008 H2: γ context = scalar m + pooled LF features. UFNO-FiLM is the direct precedent.

**Status: DEFER TO BACKLOG.** A fresh family takes a full package-scaffold build (model.py, smoke_eval.py, data.py, manifest.json, INSPIRATION.md, full_config.json). High implementation cost; weak composite prior (cycle-008 B1 landed at 12.6× over leader on Poisson; the LF-features addition is a structural fix but unproven on IFC).

**Citations if pursued:** [[beggs2025pdecond]], [[herde2024poseidon]], [[ufnofilm2025]], [[rahman2024codano]], [[li2020fno]], [[li2022ifc]].

### O5 — 2025/2026 MF surrogate citations not yet catalogued

**6 new validated bibtex candidates (and 1 corrected arXiv ID):**

| bibtex_key | Use |
|---|---|
| `mutransferfno2025` (arXiv:2506.19396) | O1 — width-scaling LR-transfer guarantee |
| `ufnofilm2025` (arXiv:2511.20543) | O3/O4 — γ(scalar, LF_field) on FNO-family, 21% MAE gain |
| `pirino2025` (arXiv:2510.23810) | Multi-resolution backlog reference (function-encoder dict learning) |
| `fnospectralperspective2024` (arXiv:2404.07200) | O1 — Fourier-kernel saturation warning |
| `mfbpinn2026` (arXiv:2602.01176) | PINN backlog reference (hierarchical residual + Bayesian UQ) |
| `liu2022neuralcoreg` (arXiv:2109.09261) | O3 — canonical pre-FNO input-dependent coregionalization precedent |
| `stresstest2025fno` arXiv ID correction | `2501.11428` → `2601.11428` (Jan 2026) |

**Total ready-keys for `papers_summary.csv` after cycle-010: 15** (10 prior + 5 new validated + `liu2022neuralcoreg` as 6th new).

## Cross-Cycle Pattern: capacity-axis returns on `fno_mf_stack`

| Cycle | hidden | modes_per_level | n_blocks | params | Poisson | Δ |
|---|---|---|---|---|---|---|
| 008 baseline | 32 | (4,8,12,12) | 3 | ~250k | 0.0596 | — |
| 009-h1h2 | 64 | (4,8,16,20) | 4 | ~1.0M | 0.0381 | **−36%** |
| 010 H1 (proposed) | 96 | (4,8,16,24) | 4 | ~2.0M | 0.030-0.034 | **−10 to −22%** |

- Cycle-009 step: 4× params → −36% Poisson; slope `log(nRMSE) / log(params) ≈ −0.39`.
- Naïve extrapolation at same slope: 2× params → −27%. Literature flattens this to realistic −10 to −22%.
- **Capacity axis not yet exhausted on `fno_mf_stack`**; cycle-011 likely hits diminishing returns at hidden=128 / modes=24 ceiling unless axis changes (curriculum, architecture).

## NK-zone sidesteps

- **NK1:** H1 sidesteps (no FiLM); H2 sidesteps (no conditioning change).
- **NK2:** H1 sidesteps (no curriculum); H2 takes the **published carve-out** — `fno_mf_stack`'s LF/HF-independent design is the precise structural condition NK2 calls out. **Dual kill-switch MANDATORY.**
- **NK3:** H1 sidesteps (canonical (2.0, 0.25) Poisson weights unchanged); H2 sidesteps (staging only, weights unchanged).

All three hypotheses NK-clear modulo named carve-outs.

## Synthesis — Buildable interventions ranked

| Rank | Hyp | Family | Surface | Expected Poisson | Expected composite | Wall | NK status |
|---:|---|---|---|---|---|---|---|
| **1** | **H1 (LEAD)** | `fno_mf_stack` | `smoke_eval.py:39-55` | 0.030-0.034 (−10 to −22%) | 0.0197-0.0212 (−5 to −11%) | ~700-900s (kill 1500s) | NK-clear |
| **2** | **H2 (SECONDARY)** | `fno_mf_stack` | `smoke_eval.py:171-291` + `compute_losses` | 0.030-0.035 (−10 to −20%) | 0.0197-0.0220 (−1 to −11%) | ~1500-1700s (kill 1800s) | NK2-carve-out-clear |
| 3 | H3 (RESERVE) | `fno_coregionalization` | `model.py` B-basis | 0.10-0.30 (recover, not lead) | no composite move | ~600-800s | NK1-adjacent |
| 4 | (DEFER) | new family | full scaffold | speculative | speculative | est. 25-30 min | NK1-safe |

**Recommended Strategist allocation:**
- `max_new ≥ 2`: H1 + H2 (SEPARATE PRs, H1 first).
- `max_new = 1`: H1 only.
- `max_new ≥ 3`: H1 + H2 + H3 RESERVE.

**DO NOT bundle H1 + H2** — they share `smoke_eval.py:39-55` and would confound attribution.

## Mutable-surface map

- `models/fno_mf_stack/smoke_eval.py` — H1 (SMOKE_DEFAULTS) + H2 (training loop / `compute_losses` / optimizer construction).
- `models/fno_mf_stack/full_config.json` — H1 (optional reference target bump).
- `models/fno_mf_stack/model.py` — H2 (no edit; `lf_fnos[*].requires_grad_(False)` invoked from smoke_eval).
- `models/_common/recipe_hash.py` — H2 (read-only; SMOKE_DEFAULTS additions auto-hashed).
- `models/fno_coregionalization/model.py + smoke_eval.py` — H3 RESERVE only.

## Related notes

- [[research-cycle-009]] — last cycle's research; capacity-axis first step
- [[research-cycle-008]] — cycle-008 NK1 and NK2 closing experiments
- [[failure-analysis-cycle-010]] — upstream failure analysis (in main `.factory/archive/`)
- [[niu2024mfrnp]] — parent architecture; Poisson5_config canonical weights
- [[li2020fno]] — FNO backbone
- [[li2022ifc]] — IFC paper bar reference
- [[lyu2023mffno]] — LF→HF schedule primary protocol
- [[yang2025mfdeeponet]] — freeze-LF pattern precedent for H2
- [[anisotropic-spectral-modes-fno]] — modes_h/modes_w convention
- [[lf-hf-pretrain-fraction-survey]] — pretrain_frac survey across published MF-FNO
- [[mutransferfno2025]], [[ufnofilm2025]], [[pirino2025]], [[fnospectralperspective2024]], [[mfbpinn2026]], [[liu2022neuralcoreg]] — 6 new cycle-010 citations
- [[stresstest2025fno]] — arXiv ID corrected this cycle (2501→2601)
- [[papers-summary-csv-state]] — now 15 keys ready
