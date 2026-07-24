---
name: failure-analysis-cycle-003
description: Cycle 003 baseline failure analysis (cycle-003 entry = cycle-002 H3 fno_coreg_residual at composite_nRMSE 0.04420). 1/2 datasets beating paper — ifc_heat PASS (0.02634 < 0.074 paper, 2.81× better); ifc_poisson FAIL (0.07416 > 0.036 paper, 2.06× over). Dominant failure mode `ABSENT_POISSON_LOSS_WEIGHTING` (new sub-category of DATASET_INVARIANT_TRAINING_RECIPE) — H3's smoke_eval.py applies uniform per-fidelity loss weights for every dataset; H4's resolve_fidelity_weights(hf=2.0, lf=0.25 for Poisson; uniform for Heat) was not ported. H3's full_config.json documents the alternative weights under `_poisson_loss_knob` marked 'off by default; orchestrator must opt in' — a dead Poisson-loss knob. Train/val/test gap signature on Poisson is val_nRMSE 0.02298 vs test 0.07416 → capacity sufficient, gradient signal allocation broken (uniform weights pull gradient toward LF terms, starving the HF residual). H3 IMPROVING overall (0.0772 → 0.0442, -43%) but REGRESSING on ifc_poisson (0.0596 → 0.0742, +25%). Secondary candidate failure modes (CAPACITY_OVERALLOC_TO_LF, MODES_TUNED_FOR_HEAT, BASIS_HEAD_MISCALIBRATION) all collapse into the same gradient-allocation root cause once weighting is fixed. CEO verdict PROCEED — publish-quality, no issues. Cycle-003 R1.5 Researcher greenlit with literature-search focus on (a) MF loss reweighting theory, (b) elliptic/Poisson HF up-weighting evidence, (c) curriculum/adaptive alternatives, (d) provenance of H4's (2.0, 0.25) recipe.
metadata:
  type: project
tags:
  - factory
  - failure-analysis
  - factory_mffp
  - cycle-003
  - poisson-loss-weighting
project: factory_mffp
cycle: "003"
phase: failure-analysis
date: 2026-05-15
source: factory-archivist
ceo_verdict: PROCEED
dominant_failure_mode: ABSENT_POISSON_LOSS_WEIGHTING
composite_nRMSE_entry: 0.04420
paper_geomean_bar: 0.0516
n_datasets_beating_paper: 1
---

# Failure Analysis — Cycle 003 Entry (factory_mffp)

This is the **cycle-003 baseline failure analysis**, performed on the
cycle-002 H3 result (`fno_coreg_residual`, branch
`experiment/4-fno_coreg_residual` @ `0c46f43`) which is the project-best
state inherited into cycle 003. See [[factory_mffp-004-outcome]] for the
full cycle-002 outcome record and [[failure-analysis-cycle-002]] for the
previous cycle's analysis. **CEO verdict on the Failure Analyst output:
PROCEED — publish-quality, no issues.** R1.5 Researcher is greenlit.

## Cycle Setup
- **Scope:** failure analysis of the **project-best entry state** for
  cycle 003 (`fno_coreg_residual` at composite_nRMSE 0.04420).
- **Datasets scored:** 2 / 2 — `ifc_heat`, `ifc_poisson` (smoke suite).
- **Comparison anchors:** paper per-dataset bars (ifc_heat 0.074,
  ifc_poisson 0.036; geomean 0.0516); cycle-002 H4 (Poisson best at
  0.0596).

## Headline Numbers

| Metric | Cycle-003 entry (H3) | Cycle-002 H4 | Paper bar | Verdict |
|---|---:|---:|---:|---|
| composite_nRMSE (geomean) | **0.04420** | 0.07719 | 0.0516 | **BEATS paper** (0.86×) |
| `ifc_heat` test nRMSE | **0.02634** | 0.09994 | 0.074 | **BEATS paper** (2.81×) |
| `ifc_poisson` test nRMSE | **0.07416** | 0.05961 | 0.036 | **MISSES paper** (2.06× over) |
| `n_datasets_beating_paper` | 1 / 2 | 0 / 2 | — | — |

**Trajectory** — composite improving (0.0772 → 0.0442, −43%); ifc_heat
dramatically improving (0.0999 → 0.0263, −74%); **ifc_poisson regressing
(0.0596 → 0.0742, +25%)**.

## Failure Distribution

```
PASS:                            1 / 2 (50%)   ifc_heat
ABSENT_POISSON_LOSS_WEIGHTING:   1 / 2 (50%)   ifc_poisson

Dominant failure mode: ABSENT_POISSON_LOSS_WEIGHTING (100% of failing datasets)
```

The dominant mode owns the **entirety** of the remaining gap to the
per-dataset paper bar.

## Dominant Failure — `ABSENT_POISSON_LOSS_WEIGHTING`

**Subcategory of:** `DATASET_INVARIANT_TRAINING_RECIPE`.

**Definition:** a successor model family removes a dataset-conditional
loss-reweighting mechanism that an ancestor family had introduced and
that was the source of the ancestor's gains on the dataset in question.
Detection: a per-dataset regression appears between a strictly-more-capable
model and its weaker ancestor, while the ancestor's training loop applied
dataset-name-conditional weights and the successor's does not.

### Root cause (behavioral)
H3's training loop applies **uniform per-fidelity loss weights for every
dataset**. H4 explicitly introduced and validated a Poisson-specific
asymmetric reweighting (HF_weight=2.0, LF_weight=0.25; uniform on Heat),
which drove H4's 39% Poisson improvement over cycle-001 H2. H3 dropped
this mechanism when porting capacity forward.

### Concrete code evidence
- `models/fno_coreg_residual/smoke_eval.py` (**H3**, the cycle-003
  baseline): no `resolve_fidelity_weights` helper. `SMOKE_DEFAULTS`
  ships `hf_loss_weight=1.0, lf_loss_weights=(1.0, 1.0, 1.0)` and the
  per-dataset eval path never overrides them.
- `models/fno_mf_stack/smoke_eval.py` (**H4**, the prior family): has
  `resolve_fidelity_weights(dataset_name, p)` which returns `(hf=2.0,
  lf=0.25)` when `"poisson"` is in the dataset name, uniform otherwise.
- `models/fno_coreg_residual/full_config.json` (**H3**): documents the
  alternative weights under `_poisson_loss_knob` and explicitly states
  **"Off by default in the smoke harness; orchestrator must opt in by
  overriding hf_loss_weight and lf_loss_weights when running
  ifc_poisson"**.
- `scripts/cycle_eval.sh` → SLURM → `smoke_eval.py`: never sets the
  override. **The Poisson-loss knob is dead code at eval time.**

### Train/val/test gap signature
Best Poisson `val_nRMSE = 0.02298` vs test `0.07416` — a 3.23× val→test
gap. **Capacity is sufficient** (val number is well below the paper bar);
**gradient signal allocation is broken** (the optimiser is not pushed
hard enough toward the HF residual under uniform weighting). The
mechanism — uniform weights let LF terms dominate the loss → LF
gradients dominate the update → HF residual is starved → test split
(which scores HF predictions) suffers — is internally consistent and
explains why **Heat improved dramatically (no asymmetry needed there)
while Poisson regressed**.

## Secondary candidate failure modes (de-prioritized)

All three candidates investigated and de-prioritized because they
collapse into the same gradient-allocation root cause once weighting is
fixed:

| Candidate | Why it might matter on Poisson | Why it is *not* dominant |
|---|---|---|
| `CAPACITY_OVERALLOC_TO_LF` | H3 grew capacity (hidden=64, decoder_hidden=32, K=10) over H4 (hidden=32); extra LF params pull gradients away from HF residual under equal weighting. | Same root cause expressed differently — once HF/LF weighting is dataset-conditional, the capacity asymmetry stops dominating the gradient. |
| `MODES_TUNED_FOR_HEAT` | Modes (4,8,12,12) retained from H4's heat-friendly bump; Poisson may carry more energy at higher wavenumbers than 12. | val_nRMSE 0.02298 on Poisson says the in-distribution spectral budget is sufficient — the train/test gap dwarfs any mode-truncation bias. |
| `BASIS_HEAD_MISCALIBRATION` | The continuous-m basis-head `B(m)=MLP([m, m²])` is zero-init; under uniform loss weighting it may stay near zero for Poisson because LF gradients dominate. | Same gradient-allocation story. Worth re-checking *after* the fix; not worth changing the head right now. |

## Cross-Cycle Comparison (cycle-002 H4 → cycle-002 H3, as cycle-003 baseline)

```
Composite (geomean):   0.07719 → 0.04420   delta -0.0330  (-43%, IMPROVING)
ifc_heat:              0.09994 → 0.02634   delta -0.0736  (-74%, IMPROVING — now beats paper)
ifc_poisson:           0.05961 → 0.07416   delta +0.0146  (+25%, REGRESSING)
n_datasets_beating_paper: 0 → 1
```

- **Improvements** — Heat improved dramatically because the H3 hybrid
  (basis-head + MFRNP decoder-in-the-aggregation + coregionalization on
  the HF latent) matches Heat's smooth, low-mode spectral content. The
  continuous-m formulation lets the HF residual learn a structured
  correction without competing for capacity with the LF backbones.
- **Regressions** — Poisson regressed because H4's *dataset-conditional*
  loss reweighting was not carried into H3's training loop. H3 raised
  capacity (hidden 32 → 64, decoder_hidden 0 → 32, added K=10 basis
  head); under uniform weights, more capacity serves the LF terms whose
  gradients are no longer downweighted, **starving the HF residual** that
  the test split actually scores.
- **New failure mode** — `ABSENT_POISSON_LOSS_WEIGHTING`, strictly a
  porting/regression class.

## Recommended Interventions (ranked by impact/cost ratio)

All within the mutable surface `models/**`.

1. **Port H4's per-fidelity loss reweighting into H3** (highest leverage,
   cheap, isolated).
   - File: `models/fno_coreg_residual/smoke_eval.py`.
   - Behaviorally: add a helper analogous to H4's
     `resolve_fidelity_weights(dataset_name, p)` that detects whether
     the dataset name contains `"poisson"` and returns the elevated HF /
     suppressed LF weights; pass into the existing `compute_losses` call.
     Data path, model, and optimiser stay untouched.
   - **Expected effect** (anchored to H4's *measured* Poisson, not a
     forecast): ifc_poisson lands in H4's neighbourhood (~0.060) at
     minimum; combining H3's basis head with H4's loss weighting plausibly
     does better. Composite floor at ≈0.0396 even at exact H4-Poisson
     parity (a further −10% from 0.0442).
   - **Risk:** Heat result depends on existing uniform weighting; the
     override must be strictly Poisson-conditional to avoid disturbing
     the Heat win.

2. **(Conditional)** Spot-check Poisson-specific capacity allocation if
   intervention 1 does not fully close the gap. Files:
   `smoke_eval.py`, `full_config.json`.

3. **(Conditional)** Investigate basis-head calibration on Poisson if
   1+2 still leave a gap. Files: `model.py`, `smoke_eval.py`.

The first intervention is the only one that should be acted on for
cycle-003 H5; the rest are contingent and intentionally not pre-committed.

## Failure Taxonomy Update

**New category** (added cycle 003):

- **`ABSENT_POISSON_LOSS_WEIGHTING`** (sub-category of
  `DATASET_INVARIANT_TRAINING_RECIPE`): a successor family removes a
  dataset-conditional loss-reweighting mechanism that an ancestor family
  had introduced and that was the source of the ancestor's gains.
  Detection signature: per-dataset regression between a strictly-more-capable
  model and its weaker ancestor, where the ancestor's training loop applied
  dataset-name-conditional weights and the successor's does not.
  Mitigation: port the helper, gate on dataset name.

## CEO Verdict on Failure Analyst — PROCEED

Reasoning (paraphrased from `.factory/reviews/ceo-verdict-failure_analyst.md`):
- Per-dataset failure classification is specific and quantified.
- Dominant failure mode grounded in concrete code evidence (file diff +
  H3's own `full_config.json` admitting the knob is "off by default").
- Train/val/test gap evidence is precise and the gradient-allocation
  mechanism is internally consistent.
- Secondary candidates correctly de-prioritized as collapsing into the
  same root cause.
- Suggested interventions stay strictly within mutable surfaces
  (`models/fno_coreg_residual/{smoke_eval.py, model.py, full_config.json}`);
  no fixed-surface references.
- Expected effect anchored to **measured** H4 Poisson (0.0596), not a
  forecast — appropriate epistemic humility.

**Issues found: none. Publish-quality.**

## Instructions to R1.5 Researcher (CEO greenlight)

Literature/web focus areas:
- **(a) MF loss reweighting theory** — theoretical grounding for HF/LF
  asymmetry in multi-fidelity training.
- **(b) Elliptic/Poisson HF up-weighting evidence** — any 2024-2026 MF
  papers confirming elliptic / Poisson-class PDEs benefit specifically
  from HF up-weighting vs other PDE classes.
- **(c) Curriculum / adaptive alternatives** — does dataset-conditional
  curriculum or annealed weighting outperform a fixed multiplier?
- **(d) Provenance of H4's `(2.0, 0.25)`** — hand-tuned, or derived from
  a cited paper? If derived, surface the source so the Strategist can
  reason about whether the same recipe transfers to other Poisson-like
  datasets when expanding beyond the smoke set.
- **Alternative balanced-loss formulations** for the Strategist to
  compare against H4's static (2.0, 0.25): per-fidelity variance
  normalization, GradNorm-style adaptive balancing, uncertainty
  weighting.

Append findings to `.factory/strategy/research.md`.

## Links

- Failure Analyst output: `.factory/research/runs/cycle-003-baseline/failure_analysis.md`
- CEO verdict: `.factory/reviews/ceo-verdict-failure_analyst.md`
- Cycle-002 H3 (current best, cycle-003 entry): `.factory/research/runs/cycle-002-H3/summary.json` — see [[factory_mffp-004-outcome]]
- Cycle-002 H4 (Poisson reference): `.factory/research/runs/cycle-002-H4/summary.json` — see [[factory_mffp-003-outcome]]
- Project dashboard: [[factory_mffp]]
- Previous cycle's failure analysis: [[failure-analysis-cycle-002]]
- Cross-project patterns: [[patterns]]
