---
name: lf-hf-pretrain-fraction-survey
description: Survey of pretrain-fraction choices in current MF-FNO literature — Lyu 2023 GCS at ~0.50, DPOT 2024 at 0.667, cycle-005 H2 at 0.25, and the Pretraining-in-Lower-Dims 2024 saturation warning
metadata:
  type: reference
tags:
  - factory
  - source
  - transfer-learning
  - pretrain-fraction
  - mf-fno
source: factory-archivist
date: 2026-06-02
cycle: cycle-007
---

# LF→HF Pretrain Fractions in Current MF-FNO Literature

Compiled during cycle-007 R1.5 to position the cycle-005 H2 schedule
(`pretrain_frac=0.25`) within the published range, and to set a defensible
follow-up bump to `pretrain_frac=0.40` for Heat under `_DATASET_RECIPES`.

## Definition

`pretrain_frac = epochs_stage1 / (epochs_stage1 + epochs_stage2)` where
Stage 1 is LF-only warm-up (loss masked to `m != hf_m`) and Stage 2 is
the joint LF+HF (or HF-only) fine-tune. Stage 2's LR is typically 3-10×
smaller than Stage 1's, and **fresh optimiser + scheduler per stage** is
canonical (Lyu 2023 documents stale momentum as a fine-tune divergence
mode).

## Published values

| Source | Stage 1 (LF) budget | Stage 2 (HF) budget | `pretrain_frac` | Reference |
|---|---|---|---|---|
| **`mf_fno_transfer_bar`** (in-tree, IN-TREE BAR; Lyu-style) | `args.epochs` (200) | `args.epochs` (200) | **0.50** | `models/mf_fno_transfer_bar/smoke_eval.py:158-165` |
| **Cycle-005 H2** (in-tree; current `fno_coregionalization`) | `0.25 * args.epochs` | `0.75 * args.epochs` | **0.25** | `models/fno_coregionalization/smoke_eval.py:81` |
| Lyu 2023 ([arXiv:2304.06972](https://arxiv.org/abs/2304.06972), Phys. Fluids) | "abundant LF" pretrain → "scarce HF" fine-tune, both at full budget per stage | n/a | **≈0.50** | `lyu2023mffno` |
| GCS MF-FNO ([arXiv:2308.09113](https://arxiv.org/abs/2308.09113)) | Per-stage parity (same schedule as Lyu) | n/a | **≈0.50** | `gcs2023mffno` (Sci. of Total Environment 2024) |
| DPOT ([arXiv:2403.03542](https://arxiv.org/pdf/2403.03542)) | 1000 epochs pretrain | 500 epochs fine-tune | **0.667** | AdamW @ 1e-3 throughout |
| FreqMoE ([arXiv:2505.06858](https://arxiv.org/pdf/2505.06858)) | "early epochs" low-freq | "later epochs" high-freq | (frequency-curriculum, not data-split — orthogonal) | 2025 |

## Saturation warning

- **Citation**: `pretrain_lowerdims2024` —
  [arXiv:2407.17616](https://arxiv.org/pdf/2407.17616).
- Examines fine-tuning of F-FNO after lower-dimensional pretraining.
  Reports that pretrain budget **plateaus** and can **hurt** generalisation
  past a threshold. **Argues against** very-large `pretrain_frac`.
- Implication: do **not** justify pushing `pretrain_frac` past ≈0.5;
  supports the recommendation of `0.40` for Heat in cycle-007 Focus 2.

## Cycle-007 recommendations (cited)

### Option A — Conservative: keep cycle-005 H2 (RECOMMENDED for the constructor-fix PR)

`pretrain_frac=0.25, pretrain_lr=1e-3, finetune_lr=3e-4`. This is the
schedule that produced the **0.01551 cached number** we are trying to
recover. **Do not change the recipe in the same PR as the constructor
fix** — confounds the regression test against the cached number.
Confidence: HIGH.

### Option B — Aggressive, push closer to bar's 0.50 (FOLLOW-UP)

Bump `pretrain_frac=0.40` for Heat (in-tree analogue at
`_DATASET_RECIPES["ifc_heat"]`). Literature basis: the bar uses 0.50,
DPOT uses 0.667 — 0.40 is a within-literature step that increases LF
dose without hitting the saturation flag from Pretraining-in-Lower-Dims.
Expected effect: heat 0.01551 → 0.013–0.015 (marginal but possibly
crosses the 0.013 sub-target). Confidence: MEDIUM-HIGH.

### Option C — Disable on Poisson

`pretrain_frac=0.0` for `ifc_poisson` (lit basis: cycle-006 architectural
diagnosis: the single-trunk H2 schedule does **NOT** help Poisson on
this family; cycle-005 evidence — H2 left Poisson essentially unchanged).
The Poisson lever lives elsewhere (loss reweighting in `fno_coreg_residual`,
not H2 dose). Confidence: HIGH.

### Bibliographic invariant

**`fresh Adam + fresh CosineAnnealingLR per stage`** — this is
`lyu2023mffno`'s deliberate choice (stale momentum is a documented
fine-tune divergence mode, cited at
`models/fno_coregionalization/smoke_eval.py:75-82` and confirmed in the
bar's `smoke_eval.py`). Keep this invariant in any schedule variant.

## The cycle-006 H2 commit (`be36cba`) — what is salvageable

- Commit message: `feat(fno_coregionalization): two-stage LF→HF transfer
  schedule (H2)`.
- The smoke_eval.py file with the schedule **is in the tree**:
  `models/fno_coregionalization/smoke_eval.py:64-411`.
- Stage 1 (LF warm-up): `n_warmup = round(pretrain_frac * args.epochs) = 50`
  at `pretrain_frac=0.25, epochs=200`. LF-only (`m != hf_m`). **Fresh
  `Adam` at `pretrain_lr=1e-3`** + fresh `CosineAnnealingLR(T_max=n_warmup)`.
- Stage 2 (joint fine-tune): `n_finetune = 200 − 50 = 150` epochs on full
  set. **Fresh `Adam` at `finetune_lr=3e-4`** + fresh
  `CosineAnnealingLR(T_max=n_finetune)`.
- Resume guard at `smoke_eval.py:304-318` already checks `grid` tuple
  identity — **the model.py constructor fix's switch from scalar
  `grid_size` → tuple `grid` is resume-compatible**.
- **The ONLY thing lost** is the `model.py` constructor signature.
  Schedule, resume guard, docstring, citations (`lyu2023mffno`, `li2022ifc`)
  all intact. Builder's job is **purely** to rebuild
  `FNOCoregionalization.__init__` to match the harness.

## Related notes

- [[anisotropic-spectral-modes-fno]] — sibling note on the modes_h/modes_w
  constructor abstraction the H2 schedule depends on.
- [[research-cycle-005]] — H2 design rationale (LF→HF transfer added to
  `fno_coregionalization`); produced the 0.01551 Heat result we are
  reattaching.
- [[research-cycle-006]] — cycle-006 H1/H2 reasoning; deferred new family
  `mf_fno_bar_residual` carried forward to cycle-008.
- [[per-dataset-recipes-mf-field]] — Focus 2 `_DATASET_RECIPES` table
  that consumes these pretrain_frac values.
- [[cycle-007-constructor-fix-pattern]] — root-cause pattern: H2 commit
  shipped without its load-bearing `model.py` partner.
