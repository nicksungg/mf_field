---
name: failure-analysis-cycle-006
description: Cycle-006 baseline failure analysis on the project-best entry state (cycle-005 H2 `fno_coregionalization` two-stage LF→HF transfer @ composite_nRMSE 0.029357, branch `experiment/7-fno_coreg_lf_hf_transfer @ be36cba`). Targets composite ≤ 0.026 (MISS by +0.00336) and ifc_heat ≤ 0.013 (MISS by +0.00251). Log-space gap decomposition — **Poisson contributes +0.76 nats above target while Heat is −0.52 nats below** — so Poisson holds the entire composite gap; 1.27× per-dataset improvement on either dataset closes the composite. **CRITICAL FRAMING CORRECTION** captured in C.1 — H2 did NOT cause the `fno_coregionalization` Poisson regression. Cache hashes confirm pre-H2 (hash `9528aeef`, cycle-005 R0) Poisson = 0.77562 → post-H2 (hash `2954a13e`) = 0.75015 (**−3.3% improvement, not a 15× regression**). The cycle-005 H2 session-summary "broke Poisson 15×" framing was an across-family comparison error (fno_coregionalization Poisson vs fno_coreg_residual Poisson winner 0.0556). The architectural Poisson failure on fno_coregionalization predates H2 and is independent of the LF→HF transfer schedule. Dominant failure mode `PDE_CLASS_ARCH_RECIPE_COUPLING` (cycle-005's NEW PATTERN) re-confirmed: one global SMOKE_DEFAULTS per family with no dataset-name gating; the recipe-tuned good behavior on dataset A breaks the family on B. 10-instance per-family × per-dataset breakdown: 20% PDE-coupling, 20% no-transfer-signal, 40% arch-quality (transolver_*), 20% pass. **80% of in-tree instances are not the dataset winner**; half are PDE-coupling failures fixable by recipe gating, half are architecture-quality failures fixable only by backbone change. 5 ranked interventions F.1–F.5, all within `models/**`. CEO verdict PROCEED — publish-quality, no issues. Researcher R1.5 greenlit on dataset-conditional MF scheduling, bar+residual composition, Poisson-direct attacks on per-fidelity FNO, HF-first curriculum.
metadata:
  type: project
tags:
  - factory
  - failure-analysis
  - factory_mffp
  - cycle-006
  - pde-class-arch-recipe-coupling
  - h2-framing-correction
project: factory_mffp
cycle: "006"
phase: failure-analysis
date: 2026-06-02
source: factory-archivist
ceo_verdict: PROCEED
dominant_failure_mode: PDE_CLASS_ARCH_RECIPE_COUPLING
composite_nRMSE_entry: 0.029357
composite_target: 0.026
composite_gap: 0.003357
ifc_heat_target: 0.013
ifc_heat_gap: 0.002511
n_datasets_beating_paper: 1
project_best_branch: experiment/7-fno_coreg_lf_hf_transfer
project_best_commit: be36cba101807d97346a437b81f3f28072bf2003
---

# Failure Analysis — Cycle 006 Baseline (factory_mffp)

This is the **cycle-006 baseline failure analysis**, performed on the
cycle-005 H2 outcome (`fno_coregionalization` two-stage LF→HF transfer
schedule on `experiment/7-fno_coreg_lf_hf_transfer @ be36cba`) — the
project-best state at composite_nRMSE 0.029357. **CEO verdict on the
Failure Analyst output: PROCEED — publish-quality, no issues.**
Researcher R1.5 is greenlit. See [[factory_mffp-007]] for the cycle-005
H2 outcome record and [[failure-analysis-cycle-003]] for the previous
failure analysis.

## Cycle Setup
- **Scope:** failure analysis of the **project-best entry state** for
  cycle 006 (`fno_coregionalization` H2 schedule at composite_nRMSE
  0.029357 — first sub-0.030 in project history).
- **Datasets scored:** 2 / 2 — `ifc_heat`, `ifc_poisson` (smoke suite,
  64×64 working grid, `n=128`).
- **Mutable surfaces:** `models/**` only.
- **Cache state:** all 14 runs in `summary.json` report `_cache=hit` —
  cycle-006 baseline is the cycle-005-H2 cache rolled forward (no
  re-train this cycle). Identical numbers to cycle-005 H2.

## Headline Numbers

| Metric                          | Cycle-006 entry | Target  | Gap          | Status |
|---                              |---:             |---:     |---:          |---     |
| composite_nRMSE (geomean)       | **0.029357**    | ≤ 0.026 | **+0.00336** | MISS   |
| `ifc_heat` test nRMSE           | **0.01551**     | ≤ 0.013 | **+0.00251** | MISS   |
| `ifc_poisson` test nRMSE        | 0.05556         | —       | —            | —      |

In log-space:
```
composite = sqrt(0.01551 × 0.05556) = 0.029357
log(0.02936) − log(0.026) = +0.1214 nats
```
**Poisson contributes +0.76 nats above the implied symmetric per-dataset
target (0.026); Heat is −0.52 nats below.** Poisson holds all of the
composite gap; Heat already cleared its share.

## Distance-to-target Decomposition (§B)

- 1.27× improvement on **either** dataset alone closes the composite gap.
  - Heat alone: 0.01551 → ≤ **0.01217** (also clears hard ifc_heat target).
  - Poisson alone: 0.05556 → ≤ **0.04358** (only closes composite).
- Hard `ifc_heat ≤ 0.013` target is independent of composite — only Heat
  moves close it.
- **Highest-EV directions:** (a) Poisson improvements on whichever family
  owns it (currently `fno_coreg_residual`); (b) joint moves that pull
  both datasets down without breaking either. Pure Heat-focused work
  only addresses the hard `ifc_heat ≤ 0.013` target.

## Per-Dataset Leaderboard (§A)

### `ifc_heat` (7 runs)
| rank | family                       | nRMSE   | params | note |
|----- |------------------------------|---------|--------|------|
| 1    | fno_coregionalization        | **0.01551** | 1.19M | WINS, only one below paper 3.6× |
| 2    | mf_fno_transfer_bar          | 0.03317 | 4.74M | bar, smoke harness landed |
| 3    | fno_coreg_residual           | 0.03519 | 2.37M | tight per-sample distribution |
| 4    | transolver_residual          | 0.11430 | 0.70M | cache hit; recipe failed pre-H2 |
| 5    | fno_mf_stack                 | 0.13010 | 2.35M | no clear MF signal on Heat |
| 6    | v9_baseline                  | 0.14861 | 0.41M | single-fidelity reference |
| 7    | transolver_attention_fusion  | 0.14916 | 2.28M | attention fusion does not help |

### `ifc_poisson` (7 runs)
| rank | family                       | nRMSE     | params | note |
|----- |------------------------------|-----------|--------|------|
| 1    | fno_coreg_residual           | **0.05556** | 2.37M | WINS, ~1.54× paper |
| 2    | mf_fno_transfer_bar          | 0.08333   | 4.74M | bar |
| 3    | fno_mf_stack                 | 0.08829   | 2.35M | comparable to bar |
| 4    | transolver_attention_fusion  | 0.38327   | 2.28M | not MF-aware on Poisson |
| 5    | fno_coregionalization        | **0.75015** | 1.19M | **BROKEN** — see §C.1 |
| 6    | transolver_residual          | 2.59704   | 0.70M | catastrophic |
| 7    | v9_baseline                  | 18.48951  | 0.41M | catastrophic |

## CRITICAL Framing Correction (§C.1) — H2 did NOT cause the Poisson regression

**This corrects a load-bearing assumption from the cycle-005 H2
session-summary.** The cache hashes confirm:

| Stage                                            | hash       | ifc_poisson nRMSE | source |
|---                                               |---         |---:               |---     |
| Pre-H2 `fno_coregionalization` (cycle-005 R0)    | `9528aeef` | **0.77562**       | summary.json |
| Post-H2 `fno_coregionalization` (cycle-005 H2 = cycle-006 R0) | `2954a13e` | **0.75015**       | summary.json |

**H2's actual effect on Poisson: −3.3% (improvement).** H2's effect on
Heat: **−24.2%** (0.02047 → 0.01551). The cycle-005 H2 session-summary
"fno_coregionalization H2 schedule breaks Poisson 15×" framing was an
**across-family comparison error**: it compared the family's own Poisson
nRMSE (0.75015) against `fno_coreg_residual`'s Poisson winner (0.05556)
— a 13.5× ratio against a different family's number, not against
fno_coregionalization's prior Poisson.

**The architectural Poisson failure on fno_coregionalization predates
H2** and is independent of the LF→HF transfer schedule. The
[[patterns]] entry "Multi-fidelity transfer-learning recipes are
PDE-class-coupled across datasets within the same architecture" needs
its cycle-005 H2 table corrected — see §"Updates to cross-cycle
patterns" below.

### Architectural root cause (behavioral, predates H2)

The `fno_coregionalization` smoke recipe uses a **single shared FNO
trunk** on a single working grid for all fidelities and routes fidelity
through a continuous-m coregionalization basis (K=10, B(m) MLP head).
At `smoke_eval.py:265-276` it sets a per-fidelity output scaler
(`max(|y|)` per `m`). Poisson's elliptic solutions have a fundamentally
different LF→HF amplitude/structure relationship than Heat: Heat's
per-fidelity `max(|y|)` is approximately matched across the ladder
(smoothing → small-amplitude perturbation), whereas Poisson's
per-fidelity scales are substantially mismatched. **A single shared
trunk asked to output `y/scaler[m]` for all fidelities forces the basis
head to absorb cross-fidelity *scale*, not just structure, and the K=10
basis underfits the residual amplitude** — yielding a uniform ~0.75
attractor on every Poisson HF sample (per-sample distribution bounded
~[0.6, 0.85] with median ≈ 0.75 — signature of a systematic prediction-
scale mismatch, not a per-sample-outlier issue).

H2's LF-only warmup at `lr=1e-3` for 25% of epochs further commits the
trunk to LF-target statistics before HF is seen. On Heat (similar
amplitudes) this is a **free pretraining boost (−24%)**. On Poisson
(scale-mismatched, trunk under-capacity) warmup neither helps nor hurts
materially (−3.3%) **because the failure is upstream of the schedule**.

## Dominant Failure Mode — `PDE_CLASS_ARCH_RECIPE_COUPLING`

This was the NEW PATTERN named in cycle-005 H2 session-summary;
cycle-006 baseline is the same artifact and **confirms it**. One global
`SMOKE_DEFAULTS` per family with no dataset-name gating; the
recipe-tuned good behavior on dataset A breaks the family on B.

Every model family with a recipe knob (transfer schedule, loss weight,
per-fidelity scaler choice, residual basis K) shows a *different* best
setting for Heat vs Poisson. The composite metric papers over this by
routing each dataset to whatever family currently owns it, but **no
single family is simultaneously competitive on both**.

### Evidence — 5 in-tree families × 2 datasets = 10 instances

| family ↓ / dataset →            | ifc_heat        | ifc_poisson    |
|---                              |---              |---             |
| fno_coregionalization (H2)      | #1 0.01551 ✓    | #5 0.75015 ✗    |
| fno_coreg_residual              | #3 0.03519 ~    | #1 0.05556 ✓    |
| fno_mf_stack                    | #5 0.13010 ✗    | #3 0.08829 ~    |
| transolver_residual             | #4 0.11430 ✗    | #6 2.59704 ✗    |
| transolver_attention_fusion     | #7 0.14916 ✗    | #4 0.38327 ✗    |
| (bar) mf_fno_transfer_bar       | #2 0.03317 ~    | #2 0.08333 ~    |

The **only** family with comparable per-dataset rank is
`mf_fno_transfer_bar` — it sits at #2 on both. Every in-tree family is
dataset-coupled.

## Failure Distribution (§E) — 10 instances

```
PDE_CLASS_ARCH_RECIPE_COUPLING:   2 / 10 (20%)   fno_coregionalization·poisson, fno_mf_stack·heat
NO_TRANSFER_SIGNAL_*:             2 / 10 (20%)   fno_coreg_residual·heat (#3), fno_mf_stack·poisson (#3)
ARCH_QUALITY_FAILURE:             4 / 10 (40%)   transolver_residual + transolver_attention_fusion × both
PASS (winner):                    2 / 10 (20%)   fno_coregionalization·heat, fno_coreg_residual·poisson
```

**80% of in-tree instances are not the dataset winner.** Half are
PDE-coupling failures within an otherwise viable architecture (fixable
by recipe gating); half are architecture-quality failures (fixable only
by a backbone change). The transolver-* families are 40% of instances
but fixing them does **not** close the composite gap (Poisson winner is
already fno_coreg_residual).

## Per-family Failure-Mode Classification (§C)

- **C.1 `fno_coregionalization`** — Heat winner / Poisson architecturally
  broken. Cause is upstream of H2 (see §"Critical Framing Correction"
  above). Category: `PDE_CLASS_ARCH_RECIPE_COUPLING`.
- **C.2 `fno_coreg_residual`** — Poisson winner / Heat #3. No LF→HF
  transfer warmup at all (`smoke_eval.py:69-82, 491-499`); per-fidelity
  FNO ladder ([4,8,12,12] modes) starves low-fidelity spectral capacity
  then aggregates upward. Heat target is dominated by low-frequency
  smooth structure that the single shared trunk of
  `fno_coregionalization` matches better with fewer params. Category:
  `NO_TRANSFER_SIGNAL_HEAT` (new variant of the H2 finding).
- **C.3 `transolver_residual`** — catastrophic on both (Heat 0.114 = 7×
  FNO winners; Poisson 2.60 = 47× Poisson winner). Token-sampled
  attention (n_lf=1024, n_hf=2048) on a regular-grid 64×64=4096-cell
  field drops half the HF signal each batch. Stale cache from cycle-002/003.
  Category: `ARCH_QUALITY_FAILURE`.
- **C.4 cache hits everywhere** — `_cache=hit` for all 14 runs;
  cycle-006 metric is **identical** to cycle-005-H2 to all printed
  digits. Correct behavior (no recipe change between cycles) but
  **cycle-006 has no independent signal**.

## Recommended Interventions (§F, ranked by EV — all within `models/**`)

### F.1 (highest EV — cheapest gating move)
**Dataset-conditional schedule in `fno_coregionalization/smoke_eval.py`**

- **Why first**: H2 is the only recipe change between cycle-005 R0 and
  cycle-006 baseline; on Heat it gave −24% with essentially no Poisson
  movement. The architectural Poisson failure is upstream of H2, so
  gating H2 off on Poisson will NOT recover Poisson — but it **frees
  Poisson-specific recipe experimentation without breaking Heat**.
- **File:** `models/fno_coregionalization/smoke_eval.py` only.
- **Change (5 lines)**: at `smoke_eval.py:236-280`, read
  `args.dataset_name` and choose `pretrain_frac`/`pretrain_lr` from a
  `_DATASET_RECIPES` dict:
  ```python
  _DATASET_RECIPES = {
      "ifc_heat":    dict(pretrain_frac=0.25, pretrain_lr=1e-3, finetune_lr=3e-4),
      "ifc_poisson": dict(pretrain_frac=0.0,  pretrain_lr=3e-4, finetune_lr=3e-4),
  }
  ```
- **Expected effect**: Heat stays 0.01551 (recipe unchanged); Poisson
  recovers to its pre-H2 0.77562 (no composite change vs cycle-006
  baseline since fno_coregionalization is not the Poisson owner).
- **Risk**: none (gating is monotonic).

### F.2 (high EV — Heat-path composite gap closer)
**Add a short LF warmup in `fno_coreg_residual/smoke_eval.py` for Heat only**

- **Why second**: `fno_coreg_residual` currently has no transfer-warmup
  (Heat at 0.03519, #3, 2.3× the leader). The H2 mechanism that gave
  fno_coregionalization −24% on Heat is a candidate transfer for
  fno_coreg_residual's Heat. fno_coreg_residual is capacity-richer
  (2.37M vs 1.19M params).
- **File:** `models/fno_coreg_residual/smoke_eval.py` only.
- **Change**: at `smoke_eval.py:491-492`, wrap the cosine-scheduled
  training loop with an optional LF-only pre-stage gated on
  `args.dataset_name == "ifc_heat"`. Reuse the H2 pattern from
  `fno_coregionalization/smoke_eval.py:341-411` (fresh Adam, fresh
  cosine, short `n_warmup ≈ 0.15 * epochs`).
- **Expected effect**: Heat 0.03519 → target ≤ 0.025 (lifts to Heat #2);
  composite unchanged unless fno_coreg_residual passes fno_coregionalization
  on Heat. Poisson untouched.
- **Risk**: per-fidelity FNO ladder may not benefit from a shared-trunk
  warmup. Mitigation: warm only the HF-level FNO + basis head from
  LF samples bilinearly upsampled to HF grid (tighter bar analog).

### F.3 (medium EV — explore-direction)
**NEW family: HF-conditional curriculum (HF-first → LF-residual fine-tune)**

- **Why**: every existing family does "LF first → HF later" (or all
  together). HF-first → LF-refine is an orthogonal inductive bias,
  especially relevant for Poisson where the HF amplitude is what's hard.
- **Files (new family)**: `models/<new>/manifest.json`, `model.py`,
  `smoke_eval.py`. Reuse `FNO2d` or per-fidelity FNO from
  `fno_coreg_residual/model.py`. 2-stage curriculum (Stage 1 = HF-only
  short pre-train, lr=3e-4, ~30% epochs; Stage 2 = joint HF+LF residual
  fine-tune, lr=1e-4, LF-prediction-as-prior loss).
- **Expected effect**: unknown a priori. Provides a 3rd dataset-specific
  tuning axis.
- **Risk**: full cycle to scaffold/train/judge; "explore the orthogonal
  direction" EV rather than "close the gap deterministically".

### F.4 (medium EV — direct NEW DIRECTIVE response)
**NEW family: bar-style LF→HF transfer + `fno_coreg_residual` residual head**

- **Why**: cycle-005 H2 applied the LF→HF transfer mechanism to the
  coregionalization head and won Heat at 0.01551 — beating the bar's
  Heat (0.03317). The resulting Poisson is broken because the underlying
  head is fno_coregionalization. A new family that composes the **bar's
  exact recipe** with the **fno_coreg_residual** head (per-fidelity FNOs
  + residual aggregation) could combine both demonstrated strengths.
- **Files (new family)**: `models/<new>/manifest.json`, `model.py`,
  `smoke_eval.py`. Import the FNO2d backbone from
  `mf_fno_transfer_bar/model.py` for HF trunk; residual-aggregation
  head from `fno_coreg_residual/model.py`.
- **Expected effect**: if successful, this family is a candidate for
  **both** dataset wins — could land at #1 on both and break the
  dataset-coupling pattern.
- **Risk**: full cycle; bar uses 4.7M params and adding a residual head
  may roughly double param count; may not fit the 30-min smoke wall
  budget.

### F.5 (lower EV, cheap diagnostics)
- **`fno_mf_stack` Heat 0.13010** anomaly — diagnose at
  `models/fno_mf_stack/smoke_eval.py:71-86`: `poisson_*_weight`
  per-fidelity weights are NOT applied to Heat (dataset-name gated),
  so Heat uses uniform LF weighting. If that's the bug, mirror the
  per-PDE weighting pattern.
- **`transolver_*` recipes** — low-EV per F.4 reasoning
  (`ARCH_QUALITY_FAILURE` — backbone is wrong for this task shape).
  Leave for a free cycle.

## Updates to Cross-Cycle Patterns (Archivist action)

The [[patterns]] entry "Multi-fidelity transfer-learning recipes are
PDE-class-coupled across datasets within the same architecture" needs
its cycle-005 H2 table corrected:

- **WAS (incorrect)**: `ifc_poisson` cycle-005 R0 ≈ 0.05; post-H2 = 0.7501
  (+15× regression).
- **IS (cache hashes corrected)**: `ifc_poisson` cycle-005 R0 (pre-H2)
  = **0.77562** (the architecturally-broken value); post-H2 = **0.75015**
  (−3.3% improvement). The "+15× regression" framing was an across-family
  comparison against `fno_coreg_residual`'s Poisson winner.

The pattern itself **still stands** — multi-fidelity training recipes
ARE PDE-class-coupled — but the H2 evidence shows up as
*PDE-class-coupled in the architecture's pre-existing failure mode*, not
*PDE-class-coupled in the schedule's effect*. H2 acts uniformly small on
Poisson (−3.3%) because the architecture's K=10 basis cannot encode
Poisson's cross-fidelity scale mismatch regardless of the schedule.

## Failure Taxonomy Update (§H)

| name                              | first seen | status                                     |
|---                                |---         |---                                         |
| `ARCH_QUALITY_FAILURE`            | cycle-003  | re-confirmed (transolver_* on both datasets) |
| `NO_TRANSFER_SIGNAL_HEAT`         | **cycle-006** | NEW — fno_coreg_residual·heat, fno_mf_stack·heat |
| `NO_TRANSFER_SIGNAL_POISSON`      | **cycle-006** | NEW — fno_mf_stack·poisson |
| `PDE_CLASS_ARCH_RECIPE_COUPLING`  | cycle-005  | re-confirmed (2/10 instances)               |
| `HARNESS_ANOMALY_NO_GPU_LOGIN_RUN` | cycle-005 | still present; out of mutable scope         |
| `ABSENT_POISSON_LOSS_WEIGHTING`   | cycle-003  | resolved within `fno_mf_stack` family at H4 |

## Cross-Cycle Comparison

| metric                          | cycle-005-R0 | cycle-005-H2 | cycle-006-R0 | trend                |
|---                              |---:          |---:          |---:          |---                   |
| composite_nRMSE                 | 0.033726     | 0.029357     | 0.029357     | flat (H2 rolled forward) |
| ifc_heat winner / value         | fno_coreg / 0.02047 | fno_coreg / 0.01551 | fno_coreg / 0.01551 | improving then flat |
| ifc_poisson winner / value      | fno_coreg_residual / 0.05556 | fno_coreg_residual / 0.05556 | fno_coreg_residual / 0.05556 | flat |
| fno_coregionalization·poisson   | **0.77562** | **0.75015** | **0.75015** | architecturally broken throughout |
| target_met_composite ≤ 0.026    | FALSE        | FALSE        | FALSE        | miss-but-closing     |
| target_met_ifc_heat ≤ 0.013     | FALSE        | FALSE        | FALSE        | miss                 |
| mf_fno_transfer_bar smoke       | BROKEN       | 0.0526 geomean | 0.0526 geomean | landed (cycle-005 H1) |

Improvements (cycle-005 R0 → cycle-006 R0):
- `fno_coregionalization` Heat 0.02047 → 0.01551 (**−24.2%**) via H2.
- `mf_fno_transfer_bar` smoke harness: BROKEN → landed at #2 on both
  (cycle-005 H1 REPO_ROOT fix).

Regressions: **none** — the cycle-005 H2 session-summary "Poisson 15×
regression" framing was wrong; cache hashes show −3.3%.

## Out-of-scope / Operator Notes (§I)

- `cycle_eval.sh` local-pass GPU-gating issue: still present, out of
  mutable scope (`scripts/cycle_eval.sh`, `eval/score.py`, `eval/smoke_config.json`).
- Precheck score-direction polarity bug: 7/7 confirmed on
  lower-is-better evals. Out of mutable scope.
- `transolver_*` stale cache entries: `train_seconds=0.0` and
  `_cache=hit`; not actionable here.
- Working tree dirty-baseline scope issue: 15 pre-existing modified
  files at session start. Operator action only.

## Summary for Strategist (§J)

- Composite = 0.029357, target 0.026, gap +0.0034. **Poisson contributes
  ~all of the gap** in log-space (+0.76 nats above the symmetric target;
  Heat is −0.52 nats below).
- **Dominant failure mode**: `PDE_CLASS_ARCH_RECIPE_COUPLING` — recipes
  are tuned per family but applied per (family × dataset), so every
  recipe-knob change improves one dataset and breaks the sibling.
- **CRITICAL framing correction**: H2 did NOT cause the fno_coregionalization
  Poisson regression (cache hashes show −3.3% on Poisson, not +15×). The
  architectural failure on Poisson predates H2.
- **Cheapest concrete intervention** (F.1): dataset-conditional
  `pretrain_frac` in `fno_coregionalization/smoke_eval.py`. No EV
  downside; unlocks Poisson-specific recipe experimentation.
- **Highest single-cycle EV** (F.2): short LF-warmup for Heat only in
  `fno_coreg_residual/smoke_eval.py`. Could land Heat at #2 and tighten
  composite.
- **Biggest swings** (F.4): NEW family combining the bar's LF→HF transfer
  trick with the residual head — directly addresses the NEW DIRECTIVE.
- **Arch-quality failures** (transolver_*, 40% of instances): do not
  close the composite gap; leave for a free cycle.

## CEO Verdict on Failure Analyst — PROCEED

From `.factory/reviews/ceo-verdict-failure_analyst.md`:
- Per-dataset, per-family leaderboard concrete with all values from
  `summary.json`.
- Distance-to-target gap correctly decomposed in log-space.
- **Critical H2 framing correction captured** — corrects a load-bearing
  assumption from the sprint standup.
- Per-instance percent breakdown honest with the right majority
  observation: 80% of instances are not the dataset winner.
- All five interventions (F.1–F.5) name specific files in `models/**`
  with line references. No fixed-surface references.
- **Issues found: none material. Publish-quality.**

## Instructions to R1.5 Researcher (CEO greenlight)

Literature/web focus areas (paraphrased from
`.factory/reviews/ceo-verdict-failure_analyst.md`):
- **(a)** Dataset-conditional MF scheduling literature.
- **(b)** Specific composition: "bar-style LF→HF transfer + residual
  coregionalization head" — what does the field say about this
  composition?
- **(c)** Ways to attack Poisson directly on the per-fidelity FNO
  architecture.
- **(d)** HF-first curriculum literature (F.3 direction).

## Key Facts for Downstream Agents (from CEO verdict)

1. The composite gap (0.029357 → 0.026) is approximately fully held by
   Poisson. Poisson winner = `fno_coreg_residual @ 0.0556`. Reducing
   Poisson on `fno_coreg_residual` to ≤ 0.0436 closes the composite gap
   alone.
2. Reducing Heat on the `fno_coregionalization` winner from 0.01551 →
   0.01217 *also* closes the composite gap AND clears the hard
   `ifc_heat ≤ 0.013` secondary target.
3. F.1 is a "free" hygiene move on `fno_coregionalization` — it does
   NOT close the gap but unblocks future Poisson recipes.
4. F.2 is the highest single-cycle EV for closing the composite gap
   via the Heat path (port H2 to `fno_coreg_residual` for Heat only).
   Risk noted: per-fidelity FNO ladder may not benefit from a
   shared-trunk warmup; mitigation provided (warm only the HF-level FNO).
5. F.4 is the explicit response to the human-injected NEW DIRECTIVE
   (beat `mf_fno_transfer_bar`) — combine the bar's LF→HF transfer trick
   with the residual head. Highest "swing" EV.
6. The "10 instances, 80% fail" framing is the dominant failure mode
   the Strategist should target.

## Links

- Failure Analyst output: `.factory/research/runs/cycle-006-baseline/failure_analysis.md`
- CEO verdict: `.factory/reviews/ceo-verdict-failure_analyst.md`
- Cycle-005 H2 outcome (cycle-006 entry): [[factory_mffp-007]]
- Previous failure analysis: [[failure-analysis-cycle-003]]
- Project dashboard: [[factory_mffp]]
- Cross-project patterns: [[patterns]] (the H2 PDE-class pattern entry
  needs its cycle-005 H2 table corrected per §"Updates to Cross-Cycle
  Patterns" above)
