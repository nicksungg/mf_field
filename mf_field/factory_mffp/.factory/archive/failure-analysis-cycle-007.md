---
name: failure-analysis-cycle-007
description: Cycle-007 R1 Failure Analyst report on the honest, reproducible baseline 0.039578 (geomean 0.02628 heat / 0.05961 poisson). Discrepancy from the historical aspirational best 0.029357 (cycle-005 H2) is explained by `fno_coregionalization` no longer composing on the current code-hash (COMMITTED_TREE_BROKEN — constructor signature `modes_h`/`modes_w`/`grid` mismatch). Top three interventions ranked: (1) repair `fno_coregionalization.__init__` ≈ −0.0092 composite, single-PR scope; (2) decouple `fno_coreg_residual` recipe per dataset ≈ −0.0016 composite (carry-over A); (3) add LF→HF two-stage transfer to `fno_coreg_residual` ≈ −0.0068 composite. Dominant failure mode by composite weight: COMMITTED_TREE_BROKEN (2 of 12 actionable cells, but largest single lever). Carry-over verdicts: signal A (K=20 / b_hidden=128 helps heat, hurts poisson — decoupling needed) confirmed; signal B (constructor fix is ~1 PR) confirmed. NEW cross-cycle pattern — second consecutive cycle of a silent regression where dirty-tree state was load-bearing for a banked baseline and the cache layer masked the loss until composite recomputation surfaced it.
metadata:
  type: project
tags:
  - factory
  - failure-analysis
  - factory_mffp
  - cycle-007
  - r1
  - committed-tree-broken
  - silent-regression-cache-layer
project: factory_mffp
cycle: cycle-007
phase: failure-analysis
round: r1
date: 2026-06-02
source: factory-archivist
ceo_verdict: PROCEED
baseline_composite: 0.039578
aspirational_best_composite: 0.029357
discrepancy_composite: 0.010221
discrepancy_pct: 34.8
ifc_heat_best_family: fno_coreg_residual
ifc_heat_best_value: 0.02628
ifc_poisson_best_family: fno_mf_stack
ifc_poisson_best_value: 0.05961
dominant_failure_mode: COMMITTED_TREE_BROKEN
broken_family: fno_coregionalization
broken_signature_kwargs: ["modes_h", "modes_w", "grid"]
top_intervention_composite_gain: -0.0092
top_intervention_scope: single-pr
---

# Failure Analysis — Cycle 007 R1 (factory_mffp)

## Cycle Setup
- **Branch under test:** `experiment/7-fno_coreg_lf_hf_transfer @ be36cba`.
- **Eval:** `bash scripts/cycle_eval.sh`, 81 s wall, 12 cache hits / 2 cache misses (`fno_coregionalization` both datasets).
- **R0 verdict (Evaluator):** PROCEED. Honest baseline = **0.039578** (geomean 0.02628 heat, 0.05961 poisson). See [[ceo-verdict-evaluator-r0]].
- **R1 verdict (Failure Analyst):** PROCEED — clean, structured, complete; quantitative deltas correctly traced; carry-over signals from cycle-006 correctly named. See [[ceo-verdict-failure_analyst]] (cycle-007 file).

## Headline — the 0.029357 discrepancy explained

| Reference point                              | composite_nRMSE | ifc_heat (best family) | ifc_poisson (best family)            |
|---                                           |---:             |---                     |---                                   |
| **R0 cycle-007 honest baseline (reproducible)** | **0.039578**  | 0.02628 `fno_coreg_residual` | 0.05961 `fno_mf_stack`         |
| Cycle-005 H2 historical project-best         | 0.029357        | 0.01551 `fno_coregionalization` | 0.05556 `fno_coreg_residual`    |
| Bar (parallel-bench `mf_fno_transfer_bar`)   | 0.0274          | 0.0128                 | 0.0587                               |
| Paper                                        | —               | 0.074                  | 0.036                                |

**Discrepancy = +0.010221 composite (+34.8%).** The cycle-005 H2 record is **not reproducible from the current committed tree**: the cached entries that produced 0.029357 key against code hashes `9528aeef4a5a` / `9be21a0f9ce9`, but the current `models/fno_coregionalization/` resolves to hash `4235deb6c27c`. Those cache files are still on disk; they no longer key-match. **0.029357 is to be treated as aspirational, not as a regression bar.** This is the framing the CEO locked in at R0 (see [[ceo-verdict-evaluator-r0]]).

## Dominant failure mode — COMMITTED_TREE_BROKEN

`fno_coregionalization` hard-crashes on both datasets with:

```
TypeError: FNOCoregionalization.__init__() got an unexpected keyword argument 'modes_h'
```
at `models/fno_coregionalization/smoke_eval.py:265`.

- `models/fno_coregionalization/model.py` declares `__init__(... modes: int, grid_size: int, b_hidden: int, ...)` (isotropic single `modes`, scalar `grid_size`).
- `models/fno_coregionalization/smoke_eval.py` was extended to compute and pass anisotropic `(modes_h, modes_w)` together with a tuple `grid` — the two surfaces diverged.
- The **cycle-006 standup CEO note confirms** a dirty `model.py` was the load-bearing signature for the cycle-005 H2 baseline (0.029357). That dirty file was lost in a hard reset during cycle-006 H1 Builder redirect #1 — see [[patterns]] §"Builder clean-isolation requires pre-clean working tree".
- **Category:** COMMITTED_TREE_BROKEN (mutable-surface, repairable, single-PR scope).
- **Composite-gap weight:** by cell count only 2 / 12 actionable cells; by composite impact, the **single largest lever available**, because reinstating the family recovers the cycle-005 cache `0.01551` on ifc_heat.

## Failure Distribution (12 actionable cells, excluding `v9_baseline`)

| Category                       | Cells | Composite-gap weight                                                                                       |
|---                             |---:   |---                                                                                                          |
| COMMITTED_TREE_BROKEN          | 2     | **Highest** — single fix → composite 0.0397 → ~0.0304 (≈ −0.0092, ~−23%).                                  |
| LOSS_RECIPE_GAP                | 5     | Medium — `mf_fno_transfer_bar` both (undertrained, 10s train_seconds), `transolver_attention_fusion` both (val/test gap), `transolver_residual` heat (eval-only). Best case (closing bar undertraining) → composite ≈ 0.0274. |
| ARCHITECTURE_OVERFIT           | 3     | Medium — `fno_coreg_residual` poisson regressed +33.5% vs c005; `transolver_residual` poisson cliff (44× bar). Closing the residual regression alone → composite −0.0016. |
| TRANSFER_SIGNAL_UNUSED         | 1     | Medium — `fno_coreg_residual` heat has no LF→HF pretrain stage; expected ≈ −0.0068 if added.               |
| ARCHITECTURE_UNDERFIT          | 1     | Low — `fno_mf_stack` heat (CPU-bound, hidden=32).                                                          |
| CAPACITY_PARETO                | 0 (latent) | Low — would bind if `fno_mf_stack` width is bumped on the CPU path.                                  |
| BAR_PARITY_NEW_FAMILY_NEEDED   | 0     | None observed — bar is reachable by repairing/configuring existing families.                               |

Taxonomy is stable across cycles 005 / 006 / 007 — no brand-new categories discovered this cycle.

## Top three interventions (ranked by expected composite delta)

### 1. Repair `fno_coregionalization` constructor signature  ≈ **−0.0092 composite**  (single-PR, COMMITTED_TREE_BROKEN)
- **Files:** `models/fno_coregionalization/model.py` (primary); possibly minor mirror in `models/fno_coregionalization/smoke_eval.py` to keep call-site stable.
- **Change shape:** make `FNOCoregionalization.__init__(...)` accept `modes_h: int, modes_w: int, grid: tuple[int,int]` and propagate to inner `FNOBlock` / `SpectralConv2d`. Intervention type **(e) constructor-signature fix**.
- **Expected impact:** composite 0.039578 → ~0.0304 if family recovers near cycle-005 cached heat 0.01551 with poisson held at current `fno_mf_stack` 0.05961. Net **≈ −0.0092 composite**, largest single lever.
- **Scope:** one PR; local to `model.py` and (if needed) the call site at `smoke_eval.py:265`.

### 2. Decouple `fno_coreg_residual` recipe per dataset  ≈ **−0.0016 composite**  (carry-over signal A, ARCHITECTURE_OVERFIT)
- **Files:** `models/fno_coreg_residual/smoke_eval.py` — gate overrides on `args.dataset_name`. The `_poisson_loss_knob` already exists in `models/fno_coreg_residual/full_config.json` but the smoke harness does not read it.
- **Change shape:** when `args.dataset_name == "ifc_poisson"`, apply HF=2.0 / LF=0.25 (the MFRNP recipe declared in `full_config.json`) **and** reduce K / b_hidden back from the cycle-006 (K=20, b_hidden=128) heat-bump that is now baked into the committed tree. Intervention type **(c) recipe/loss change**.
- **Expected impact:** restoring Poisson to ≤ 0.05556 (cycle-005 number) → composite geomean(0.02628, 0.05556) ≈ **0.0382, −0.0016**. If decoupling lets heat keep improving while Poisson returns to or beats c005, the gain is larger.
- **Scope:** one PR; pure config-routing logic in `smoke_eval.py`.

### 3. Add LF→HF two-stage transfer to `fno_coreg_residual`  ≈ **−0.0068 composite**  (TRANSFER_SIGNAL_UNUSED)
- **Files:** `models/fno_coreg_residual/smoke_eval.py` (add `pretrain_frac` arg + warmup loop using only LF samples); `model.py` unchanged (residual stack already supports per-level forward). Intervention type **(d) transfer-pretraining add-on**.
- **Expected impact:** closes part of the 2.05× heat gap. If heat reaches 0.018, composite → geomean(0.018, 0.0596) ≈ **0.0328, −0.0068**. **Stackable with #2.**
- **Scope:** one PR; mirrors the H2 schedule the broken `fno_coregionalization` already declares.

## Carry-over verdicts from cycle-006

### Signal A — K=20 / b_hidden=128 vs MFRNP-Poisson recipe must be decoupled
- **Confirmed.** Cycle-006 H1 banked K=20 / b_hidden=128 as the architectural cause of a real **−13.1% heat improvement on `fno_coreg_residual`**, while the MFRNP loss reweighting did NOT transfer cross-architecture on Poisson (the +3.6% there was within noise). Cycle-007 R0 shows the bank settled in: heat moved 0.03519 → 0.02628 (−25.3% vs c005, the deepest improvement to date on this cell), poisson regressed 0.05556 → 0.07419 (**+33.5%** vs c005 — recipe-overfit-across-datasets becomes the dominant ARCHITECTURE_OVERFIT cell in R1).
- **Reading:** the heat-tuned recipe is now shared across both PDEs in the committed tree; **separating it per dataset is the carry-over action.** This is exactly intervention #2 above. See [[cycle-006-summary]] and [[cycle-006-exp-8]].

### Signal B — `fno_coregionalization` constructor fix is ~1 PR
- **Confirmed.** Cycle-006 CEO standup flagged the dirty `model.py` that was load-bearing for c005 H2 and was lost on the hard reset. R1 verifies the fix surface: `models/fno_coregionalization/model.py` (primary) + minor mirror in `smoke_eval.py:265`. The signature change is mechanical — accept `modes_h, modes_w, grid` and forward to `SpectralConv2d` / `FNOBlock`. **Scope is one PR.** This is intervention #1 above. See [[patterns]] §"Builder clean-isolation requires pre-clean working tree" and the cycle-006 close-out side-effect note.

## NEW cross-cycle pattern — silent regression masked by the cache layer

**Second consecutive cycle (006 → 007) where a "silent regression" surfaced only when the composite was recomputed end-to-end.** The pattern is:

1. An experiment branch accumulates **dirty working-tree state** that is load-bearing for the eval (e.g., cycle-005 H2's `fno_coregionalization/model.py` had a constructor that matched the smoke harness's anisotropic call site).
2. The dirty state is **never committed**. The on-disk `smoke_latest.json` reflects a banked composite (0.029357) that depends on it.
3. A later cycle issues a `git reset --hard` (cycle-006 H1 Builder redirect #1, recovering from scope contamination) — wiping the uncommitted dirty file.
4. The **cache layer hides the loss** because the cycle eval re-resolves cached results by `__code_hash__` of each model directory. The new code hash for `fno_coregionalization` (`4235deb6c27c`) simply does not match any cached entry; the cell becomes a cache MISS that crashes silently, while the composite is re-computed without it.
5. The disk metric (`smoke_latest.json`) and the supposed "last keep result" diverge. The discrepancy is only surfaced when the next cycle's R0 evaluator runs end-to-end and reports the actual reproducible number.

**Cycle-006 incarnation:** the H1 Builder redirect's `git reset --hard` wiped the dirty `fno_coregionalization/model.py`. Cycle-007 R0 was the first eval after that reset; it surfaced the **+34.8% composite discrepancy** between the disk-cached aspirational best (0.029357) and the reproducible baseline (0.039578). The R0 Evaluator and R1 Failure Analyst both correctly diagnosed the cache/code-hash mismatch.

**Pattern name (proposed for [[patterns]]):** `silent-regression-cache-layer-masks-uncommitted-load-bearing-state`.

**Implications for future cycles:**
- Every cycle eval that reports a project best should additionally verify the result is reproducible from a **clean working tree at the commit hash**. A delta between `git status` clean re-eval and the cached `smoke_latest.json` is a silent-regression signal.
- The `cycle_eval` cache key should incorporate a "tree-cleanliness" tag (or refuse to bank composite numbers when the working tree is dirty). Without that, banked numbers depend on uncommitted state and are not durable across `git reset`s.
- The cycle-006 "Builder clean-isolation" pattern is the upstream root cause; this pattern is the downstream consequence at the cache-layer + composite-bookkeeping boundary.

## Cross-cycle comparison (005 → 006 → 007 R0)

| Metric / cell                                | c005 H2  | c006 H1 (exp/8) | c007 R0  | Trend                                 |
|---                                           |---:      |---:             |---:      |---                                    |
| composite_nRMSE                              | 0.029357 | 0.041963        | 0.039578 | regression vs c005, slight improve vs c006 |
| `fno_coregionalization` × ifc_heat           | 0.01551  | CRASH           | CRASH    | regressing → broken                   |
| `fno_coreg_residual` × ifc_heat              | 0.03519  | 0.03059 (−13%)  | 0.02628 (−25% vs c005) | **improving**             |
| `fno_coreg_residual` × ifc_poisson           | 0.05556  | 0.05756 (+3.6%) | 0.07419 (+33.5% vs c005) | **regressing**          |
| `fno_mf_stack` × ifc_poisson                 | n/a      | 0.05961         | 0.05961  | stable at bar parity                  |
| `mf_fno_transfer_bar` × ifc_heat             | n/a      | 0.03317         | 0.03317  | stable but undertrained (~10s train)  |
| `mf_fno_transfer_bar` × ifc_poisson          | n/a      | 0.08333         | 0.08333  | stable but undertrained               |

**Improvements c005 → c007:** `fno_coreg_residual` heat down 25.3% — the K=20 / b_hidden=128 architectural bump (banked in cycle-006) has paid off.

**Regressions c005 → c007:** `fno_coregionalization` not runnable; `fno_coreg_residual` poisson +33.5% (recipe-overfit-across-datasets).

**New failures:** the `modes_h` constructor mismatch was first hit in cycle-006 H1 and is now structurally embedded in the committed `experiment/7` tree on top of commit `be36cba` (which added the two-stage transfer schedule but did not update the constructor surface).

## CEO instructions for downstream agents (R2 Strategist)

From [[ceo-verdict-failure_analyst]] cycle-007 file (PROCEED verdict):

- Treat **0.039578 as the cycle-007 baseline**; use 0.029357 only as the "what was previously achievable on this branch" aspirational reference.
- The single largest composite lever is **intervention #1 (constructor repair)** — closes ~57% of the gap between honest baseline and aspirational best on its own.
- Interventions #2 and #3 are **stackable** on the residual family — addressing the c006 carry-over A and the unused transfer signal respectively.
- Per-dataset frontier: ifc_heat is gap-bound by reinstating `fno_coregionalization` (1.21× over bar at 0.01551 cached); ifc_poisson is gap-bound by `fno_mf_stack` near-parity (1.015× over bar at 0.05961) — Poisson is the "almost there" frontier; small wins compound.

## Related notes

- [[factory_mffp]] — project dashboard
- [[failure-analysis-cycle-002]] — prior failure-analysis archive structure
- [[failure-analysis-cycle-006]] — referenced but not yet written; cycle-006 H1 standalone close-out is in [[cycle-006-summary]] and [[cycle-006-exp-8]]
- [[cycle-006-exp-8]] — H1 experiment archive (MFRNP Poisson recipe + K=20 did not transfer cross-architecture)
- [[cycle-006-summary]] — cycle-006 close-out (REVERT)
- [[factory_mffp-007]] — cycle-005 H2 experiment archive (project best 0.029357, the aspirational target this cycle)
- [[patterns]] §"Builder clean-isolation requires pre-clean working tree" (upstream root cause), §"`smoke_eval.py` may not consume `full_config.json`" (related config-surface category), §"Factory precheck `score_direction` is polarity-buggy on lower-is-better metrics" (separate cross-cycle pattern)
- [[ceo-verdict-evaluator-r0]] — cycle-007 R0 honest baseline framing
- [[ceo-verdict-failure_analyst]] — cycle-007 R1 PROCEED verdict

## Tags

`failure-analysis`, `cycle-007`, `r1`, `committed-tree-broken`,
`fno_coregionalization-constructor-broken`, `recipe-overfit-across-datasets`,
`silent-regression-cache-layer`, `aspirational-best-not-reproducible`,
`carry-over-A-confirmed`, `carry-over-B-confirmed`,
`top-3-interventions-ranked`, `ceo-proceed`
