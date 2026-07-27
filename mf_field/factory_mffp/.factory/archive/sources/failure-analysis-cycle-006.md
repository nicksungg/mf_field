---
name: failure-analysis-cycle-006
description: Cycle-006-baseline failure analysis — gap decomposition shows Poisson holds all of the composite gap (+0.76 nats above target vs Heat at −0.52 nats below); dominant failure mode is PDE_CLASS_ARCH_RECIPE_COUPLING (80% of in-tree family×dataset instances are not the dataset winner). Includes cache-hash forensics correcting the cycle-005 H2 framing that "H2 broke Poisson 15×" (it didn't — the failure predates H2 and is architectural).
metadata:
  type: reference
tags:
  - factory
  - source
  - failure-analysis
  - cycle-006
  - pde-class-coupling
  - poisson
project: factory_mffp
cycle: 006
source: factory-archivist
date: 2026-06-02
---

# Failure Analysis — Cycle-006 Baseline

**Branch:** `experiment/7-fno_coreg_lf_hf_transfer @ be36cba` (cycle-005 H2 outcome, project-best).
**Composite (geomean of 2 smoke datasets):** **0.029357**.
**Targets:** composite ≤ 0.026 (**MISS by +0.00336**); ifc_heat ≤ 0.013 (**MISS by +0.00251**).
**Mutable surfaces:** `models/**` only.
**Related notes:** [[research-cycle-006]], [[research-cycle-005]], [[research-cycle-003]], [[patterns]].

---

## Per-dataset leaderboard (7 families × 2 datasets)

### ifc_heat
| rank | family                       | nRMSE     | params  | note |
|----- |------------------------------|-----------|---------|------|
| 1    | fno_coregionalization (H2)    | **0.01551** | 1.19M  | WINS; only family below paper-paper-ratio 3.6× |
| 2    | mf_fno_transfer_bar           | 0.03317   | 4.74M   | bar (Lyu 2023), landed on smoke harness |
| 3    | fno_coreg_residual             | 0.03519   | 2.37M   | very tight per-sample distribution |
| 4    | transolver_residual            | 0.11430   | 0.70M   | cache hit; recipe failed pre-H2 |
| 5    | fno_mf_stack                   | 0.13010   | 2.35M   | no clear MF signal on Heat |
| 6    | v9_baseline                    | 0.14861   | 0.41M   | single-fidelity reference |
| 7    | transolver_attention_fusion    | 0.14916   | 2.28M   | attention fusion does not help |

### ifc_poisson
| rank | family                       | nRMSE       | params  | note |
|----- |------------------------------|-------------|---------|------|
| 1    | fno_coreg_residual           | **0.05556** | 2.37M   | WINS; ~1.54× paper |
| 2    | mf_fno_transfer_bar          | 0.08333     | 4.74M   | bar |
| 3    | fno_mf_stack                 | 0.08829     | 2.35M   | comparable to bar |
| 4    | transolver_attention_fusion  | 0.38327     | 2.28M   | not MF-aware on Poisson |
| 5    | fno_coregionalization        | **0.75015** | 1.19M   | **architecturally broken** — see §C below |
| 6    | transolver_residual          | 2.59704     | 0.70M   | catastrophic |
| 7    | v9_baseline                  | 18.48951    | 0.41M   | catastrophic |

---

## Gap decomposition

```
composite = sqrt(0.01551 * 0.05556) = 0.029357
target    = 0.026
log-space gap = log(0.029357) - log(0.026) = +0.1214
```

In log-space distance to the implied symmetric target (= 0.026):
- **Poisson contributes +0.76 nats above target.**
- **Heat contributes −0.52 nats below target.**

**Poisson holds essentially all of the composite gap.** Per-dataset closure thresholds (alone):
- Poisson 0.0556 → ≤ **0.0436** (1.27× improvement; closes composite gap)
- Heat 0.01551 → ≤ **0.01217** (1.27× improvement; closes composite gap AND the hard 0.013 target)

**Direction:** highest-EV moves are (a) Poisson improvements on whoever owns it (currently `fno_coreg_residual`), or (b) joint moves that pull both datasets down without breaking either. Pure Heat-focused work is allowed against the hard 0.013 target but does not by itself close composite-≤0.026.

---

## Cache-hash forensics — CRITICAL FRAMING CORRECTION

cycle-006 baseline reports all 14 runs as cache hits (`_cache: "hit"`); the current Heat 0.01551 and Poisson 0.75015 (on `fno_coregionalization`) are the cycle-005-H2 numbers rolled forward.

The cycle-005 H2 session-summary framing that "H2 broke Poisson 15×" was an **across-family comparison error**. Cache-hash forensics:

| Stage                                                | hash       | `fno_coregionalization` Poisson nRMSE |
|---                                                   |---         |---                                    |
| Pre-H2 (cycle-005 R0 baseline)                       | `9528aeef` | **0.77562** (already architecturally broken) |
| Post-H2 (cycle-005 H2 = cycle-006 R0)                 | `2954a13e` | **0.75015** (−3.3% improvement)        |

**H2 did NOT introduce the Poisson failure** on `fno_coregionalization`. The failure predates H2 by a wide margin and is **architectural** (single shared FNO trunk + K=10 basis head cannot encode Poisson's cross-fidelity scale mismatch). H2's effect on Poisson is a small −3.3% improvement; H2's effect on Heat is a clean −24.2%.

The "+15×" figure compared `fno_coregionalization`'s own Poisson nRMSE (0.75015) against the **other family's** Poisson winner (`fno_coreg_residual` @ 0.05556) — a 13.5× across-family ratio, not within-family before/after.

**This correction is also recorded in [[patterns]]** under "Multi-fidelity transfer-learning recipes are PDE-class-coupled across datasets within the same architecture" §CRITICAL FRAMING CORRECTION.

---

## Per-family failure classification

### C.1 `fno_coregionalization` — Heat winner / Poisson architecturally broken (NOT introduced by H2)

- `models/fno_coregionalization/smoke_eval.py:64-82` — `SMOKE_DEFAULTS` carries `pretrain_frac=0.25, pretrain_lr=1e-3, finetune_lr=3e-4`, applied uniformly across all datasets (no `dataset_name` gate).
- Per-sample distribution on Poisson (n=128): bounded `[~0.6, ~0.85]` with median ≈ 0.75 — **uniformly wrong attractor**, signature of systematic prediction-scale or scaler mismatch, not per-sample outlier.
- **Architectural root cause:** single shared FNO trunk on a single working grid for all fidelities, routing fidelity through continuous-m coregionalization basis (K=10, B(m) MLP head). Per-fidelity output scaler at `smoke_eval.py:265-276`. Heat's per-fidelity max(|y|) is approximately matched across the ladder (smoothing → small-amplitude perturbation). Poisson's elliptic solutions have substantially mismatched amplitude scales across fidelities. A single shared trunk asked to output `y/scaler[m]` for all fidelities forces the basis head to absorb cross-fidelity scale, not just structure, and K=10 basis underfits the residual amplitude → uniform ~0.75 attractor.
- **Failure stage:** training (recipe-insensitive to PDE class).
- **Category:** `PDE_CLASS_ARCH_RECIPE_COUPLING`.

### C.2 `fno_coreg_residual` — Poisson winner / Heat #3 (inverse failure mode)

- `models/fno_coreg_residual/smoke_eval.py:69-82` — `SMOKE_DEFAULTS` has NO LF→HF transfer schedule. Single-stage joint at `lr=3e-4`, AdamW + cosine (`:491-492`).
- Architecture: 4 per-fidelity FNOs (hidden=32, modes `[(4,5),(8,9),(12,12),(12,12)]`, blocks=3) + MFRNP decoder-in-the-aggregation (decoder_hidden=32) + continuous-m basis head (K=10).
- Loss (`:275-311`): LF direct supervision per level (uniform weight 1.0) + HF residual-stack `pred = agg + basis_residual` against `y_hf_norm` + `agg_anchor_weight=0.5` anchor on agg.
- **Why Heat #3, not #1:** per-fidelity-FNO ladder ([4,8,12,12] modes) deliberately starves spectral capacity at LF then aggregates upward. Heat's HF target is dominated by low-frequency smooth structure — `fno_coregionalization`'s single shared full-resolution trunk + K=10 across-fidelity basis is a better match. `fno_coreg_residual` wastes capacity on a multi-stage aggregation path that does not help Heat.
- **Why Poisson #1:** per-fidelity FNOs build separate spectral representations per fidelity; residual head learns HF correction over an LF-conditioned baseline — the right inductive bias for Poisson, whose LF solutions provide a strong amplitude prior but a structurally incomplete HF estimate.
- **Category:** `NO_TRANSFER_SIGNAL_HEAT` (new variant of the H2 finding).

### C.3 `transolver_*` — catastrophic on both datasets

- `transolver_residual`: Heat 0.114 (~7× worse than FNO winners), Poisson 2.60 (~47× worse). `transolver_attention_fusion`: similar shape.
- `train_seconds=0.0` and `_cache=hit` — these are stale from cycle-002/003; no re-run this cycle.
- **Failure shape:** token-sampled attention on 128 HF training samples for ifc_raw cannot match full-grid spectral backbone for regular-grid PDE tasks. With only 2048 HF tokens out of a 64×64=4096-cell field, half the HF signal is dropped each batch.
- **Category:** `ARCH_QUALITY_FAILURE`.

---

## Dominant failure mode — `PDE_CLASS_ARCH_RECIPE_COUPLING`

One global `SMOKE_DEFAULTS` per family with no dataset-name gating; the recipe-tuned good behavior on dataset A breaks the family on B. The composite metric papers over this by routing each dataset to whichever family currently owns it, but **no single in-tree family is simultaneously competitive on both** `ifc_heat` and `ifc_poisson`.

### 10-instance breakdown (5 in-tree families × 2 datasets; bar excluded)

| family ↓ / dataset →            | ifc_heat        | ifc_poisson    |
|---                              |---              |---             |
| fno_coregionalization (H2)      | #1 0.01551 ✓     | #5 0.75015 ✗    |
| fno_coreg_residual              | #3 0.03519 ~     | #1 0.05556 ✓    |
| fno_mf_stack                    | #5 0.13010 ✗     | #3 0.08829 ~    |
| transolver_residual             | #4 0.11430 ✗     | #6 2.59704 ✗    |
| transolver_attention_fusion     | #7 0.14916 ✗     | #4 0.38327 ✗    |
| (bar) mf_fno_transfer_bar       | #2 0.03317 ~     | #2 0.08333 ~    |

The **only family with comparable per-dataset rank is the bar** — `mf_fno_transfer_bar` sits at #2 on both. Every in-tree family is dataset-coupled.

### Distribution

```
PDE_CLASS_ARCH_RECIPE_COUPLING:   2/10 (20%)   fno_coregionalization·poisson, fno_mf_stack·heat
NO_TRANSFER_SIGNAL_*:             2/10 (20%)   fno_coreg_residual·heat (#3), fno_mf_stack·poisson (#3)
ARCH_QUALITY_FAILURE:             4/10 (40%)   transolver_residual + transolver_attention_fusion × both
PASS (winner):                    2/10 (20%)   fno_coregionalization·heat, fno_coreg_residual·poisson
```

**80% of in-tree instances are not the dataset winner.** Half are PDE-coupling failures within an otherwise viable architecture (fixable by recipe gating); half are architecture-quality failures (fixable only by backbone change). Fixing the 40% arch-quality instances does NOT close the composite gap — Poisson winner is already `fno_coreg_residual` at 0.0556.

---

## Failure taxonomy (state after cycle-006)

| name                              | description                                                                                       | first seen |
|-----------------------------------|---------------------------------------------------------------------------------------------------|------------|
| `ARCH_QUALITY_FAILURE`             | backbone fundamentally wrong for task shape                                                       | cycle-003  |
| `NO_TRANSFER_SIGNAL_HEAT`           | right backbone but lacks LF→HF transfer/curriculum trick the leader uses on Heat                 | cycle-006  |
| `NO_TRANSFER_SIGNAL_POISSON`         | mirror on Poisson                                                                                  | cycle-006  |
| `PDE_CLASS_ARCH_RECIPE_COUPLING`   | one global SMOKE_DEFAULTS per family with no dataset gating                                       | cycle-005  |
| `HARNESS_ANOMALY_NO_GPU_LOGIN_RUN` | cycle_eval.sh's local-pass cache pass timeouts on the login node — out of mutable scope          | cycle-005  |

---

## Cross-cycle comparison

| metric                          | cycle-005-baseline | cycle-005-H2 | cycle-006-baseline | trend |
|---------------------------------|--------------------|--------------|--------------------|-------|
| composite_nRMSE                  | 0.033726           | 0.029357     | 0.029357           | flat (H2 → baseline rolled forward) |
| ifc_heat winner / value          | fno_coreg / 0.02047 | fno_coreg / 0.01551 | fno_coreg / 0.01551 | improving (H2) then flat |
| ifc_poisson winner / value       | fno_coreg_residual / 0.05556 | fno_coreg_residual / 0.05556 | fno_coreg_residual / 0.05556 | flat |
| target_met_composite ≤ 0.026     | FALSE              | FALSE        | FALSE              | miss-but-closing |
| target_met_ifc_heat ≤ 0.013      | FALSE              | FALSE        | FALSE              | miss |
| mf_fno_transfer_bar on smoke     | BROKEN (REPO_ROOT) | 0.0526 geomean | 0.0526 geomean   | now landed (cycle-005 H1 fix) |
