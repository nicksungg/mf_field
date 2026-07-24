---
name: factory_mffp-005-experiment
description: H1 fno_coreg_residual_poisson_loss_reweighting (cycle-003 exp_id=5) — Outcome companion to factory_mffp-005-build. Ported H4's resolve_fidelity_weights helper (Poisson-only HF=2.0/LF=0.25) into H3's fno_coreg_residual hybrid. composite_nRMSE regressed 0.04420 → 0.08472 (+91.7% on the research target). ifc_heat unchanged at 0.02630 (uniform weights, still BEATS paper). ifc_poisson catastrophically regressed 0.07416 → 0.27287 (3.68× worse; 4.58× worse than H4 on simpler backbone). CEO=REVERT (genuine model regression, NOT precheck bookkeeping — FIRST genuine REVERT in project history). Cycle-003 framing that MFRNP Poisson5 recipe is "PDE-class-bound, not backbone-bound" REFUTED — the recipe is backbone-coupled. Checkpoint-resume contamination discovered and resolved (operationally) — clean from-scratch run 13974837 (549.15s, 200 epochs cuda) confirms verdict to within 0.10% of contaminated run 13973868. Project best preserved at cycle-002 H3 (0.04420 on experiment/4-fno_coreg_residual @ 0c46f43).
metadata:
  type: project
tags:
  - factory
  - experiment
  - factory_mffp
  - cycle-003
  - outcome
  - h1
  - poisson-loss-weighting
  - revert-genuine
  - first-genuine-revert
  - hypothesis-refuted
  - backbone-coupled-recipe
project: factory_mffp
experiment_id: "005"
phase: outcome
verdict_ceo: REVERT
verdict_factory: revert
score_before: 0.04420
score_after: 0.08472
score_delta: +0.04052
score_delta_pct: +91.7
cycle: "003"
hypothesis: H1
date: 2026-05-15
source: factory-archivist
---

# Experiment #005 — H1 `fno_coreg_residual_poisson_loss_reweighting` (cycle-003 outcome)

This is the **outcome companion** to [[factory_mffp-005-build]]. Full
mechanism, hard-gate results, and pre-flight smoke verification are in
the build note — this note focuses on the keep/revert decision, the
refuted scientific framing, the contamination handling, and the
cycle-004 implications.

## Hypothesis (cycle-003 H1)

**FIX, single additive knob.** Port H4's
`resolve_fidelity_weights(dataset_name, p)` helper from
`models/fno_mf_stack/smoke_eval.py` into H3's
`models/fno_coreg_residual/smoke_eval.py`. SMOKE_DEFAULTS adds
`poisson_hf_weight=2.0` / `poisson_lf_weight=0.25` (verbatim MFRNP
`Poisson5_config.yaml`). `compute_losses` extended with
`hf_fid_weight` / `lf_fid_weight` kwargs; resolver gates on
`"poisson" in dataset_name.lower()` and returns `(2.0, 0.25)` for
Poisson, `(1.0, 1.0)` for Heat.

**Compositional argument (Strategist, adopted by CEO at build phase):**
H3 supplies the IFC-path architectural asymmetry (continuous-m basis
head + per-fidelity output normalization). H1 adds the orthogonal
MFRNP-path loss-weighting asymmetry on top. The two SOTA routes
compose on one architecture; the MFRNP Poisson5 recipe is
**PDE-class-bound (elliptic), not backbone-bound** (per the cycle-002
H4 pattern [[patterns]] §"MFRNP `Poisson5_config.yaml` knobs (capacity
+ per-fidelity loss weighting) are independently load-bearing and
orthogonally decompose by dataset").

**Predicted impact (anchored to measured H4 Poisson, not forecast):**
- `ifc_poisson`: floor at H4's 0.0596, plausible upside below.
- `ifc_heat`: unchanged at ≈0.02634 (resolver returns uniform).
- `composite_nRMSE` floor at `geomean(0.02634, 0.0596) ≈ 0.0396`.

## Branch + commit (preserved on disk)

- Branch: `experiment/5-fno_coreg_residual_poisson_lossweight` —
  **intact at commit `a0d932b`**.
- Chain: master ← cycle-002 H3 (`0c46f43`) ← cycle-003 H1 (`a0d932b`).
- Diff vs parent: +67/-5 across
  `models/fno_coreg_residual/{smoke_eval.py, INSPIRATION.md}`.
- Not merged to master; not deleted. Kept on disk for cycle-004
  follow-up (adaptive loss-weighting hypothesis).

## Pre-eval baselines (the numbers the verdict is measured against)

- **Cycle-003 entry baseline = 0.04420** — cycle-002 H3 best on
  `experiment/4-fno_coreg_residual @ 0c46f43`. This is the
  project-best the cycle-003 monotonic gate is measured against.
- **Cycle-002 H4 ifc_poisson = 0.0596** — the lower-bound expected
  H1 floor on Poisson assuming the recipe ports.
- **Predicted H1 composite floor = 0.0396** — `geomean(0.02634, 0.0596)`,
  ≈10% reduction vs cycle-003 entry 0.0442.
- **Published paper geomean = 0.0516** — external bar.

## Post-eval (H1 branch, eval_v9 splits, 200-epoch cycle_eval.sh)

| Metric                       | Value      | vs entry 0.0442   | vs paper 0.0516 | vs H4 0.0596 (poisson only) |
|---                           |---         |---                |---              |---                          |
| **composite_nRMSE**          | **0.08472**| +91.7% REGRESSION | 1.64× over      | —                           |
| ifc_heat                     | 0.02630    | unchanged         | **BEATS by 2.81×** | —                        |
| ifc_poisson                  | **0.27287**| **3.68× WORSE** (from 0.07416) | 7.58× over      | **4.58× WORSE**          |

**Comparison summaries:**
- **vs cycle-003 entry 0.0442**: composite regression of +0.04052
  (+91.7%). Hard FAIL on the monotonic gate.
- **vs H1 floor 0.0396**: composite +0.04512 (114% above the predicted
  H1 floor). The Poisson side completely failed to realize the H4
  recipe benefit.
- **vs paper geomean 0.0516**: ratio 1.642 (composite 64% worse than
  paper). H1 also dropped the project's "first family beating paper
  composite geomean" status that cycle-002 H3 achieved.
- **vs cycle-002 H4 on simpler backbone**: H1's ifc_poisson 0.27287 is
  **4.58× worse** than H4's 0.05961 on `fno_mf_stack`. Same recipe,
  different backbone → catastrophic harm.

## Why this is REVERT (and not bookkeeping)

Unlike cycles 001/002 H1/H2/H4/H3, where CEO intent was KEEP but
factory state was forced to REVERT by 4 known precheck infrastructure
bugs (score_direction polarity for lower-is-better, scope/fixed_surfaces
empty-detail, ground_truth_leakage substring-collision),
**cycle-003 H1 is the FIRST genuine REVERT in the project's history.**
The research target regressed massively (+91.7%); the project best
(cycle-002 H3 at 0.04420) must be preserved.

The Heat path (uniform weights, `hf_fid_w=1.0, lf_fid_w=1.0`) reproduced
the cycle-003 entry result exactly (0.02630 vs 0.02634, within seed
noise), **confirming the H1 code is benign when reweighting is off**.
The regression is **fully attributable** to the asymmetric (2.0, 0.25)
weights applied to H3's Poisson training.

**Precheck snapshot:**

```
score_direction: PASS (incorrectly — saw 0.0442 → 0.0847 as "OK"
                  assuming higher-is-better; known factory polarity
                  bug; genuine for this hypothesis is REGRESSION)
scope:           FAIL (known false-positive: empty detail)
fixed_surfaces:  FAIL (known false-positive: empty detail)
leakage:         FAIL (known substring-collision on 'poisson' from
                  factory.md mentioning "ifc_poisson")
anti_pattern:    PASS
smoke_test:      PASS
```

Precheck `passed=false`. For this hypothesis the CEO verdict aligns
with precheck failure (REVERT), unlike cycles 001/002 where the
failures were bookkeeping-only.

## Refuted scientific framing — recipe is backbone-coupled

Cycle-003's strategy framed the MFRNP Poisson5 recipe as
**PDE-class-bound (elliptic), not backbone-bound**, citing the
cycle-002 H4 finding that the recipe ported cleanly from MFRNP's own
residual stack to H2's `fno_mf_stack` (a different residual-stack
family with FNO backbones). The compositional argument predicted that
H3's IFC-architectural asymmetry would compose orthogonally with H4's
MFRNP-loss-weighting asymmetry. The clean H1 data **refutes** this:

| Backbone                            | (2.0, 0.25) Poisson effect          | Conclusion             |
|---                                  |---                                  |---                     |
| `models/fno_mf_stack` (cycle-002 H4) | ifc_poisson **0.0999 → 0.0596** (39% improvement) | Recipe helps      |
| `models/fno_coreg_residual` (cycle-003 H1) | ifc_poisson **0.0742 → 0.27287** (3.68× regression) | Recipe catastrophically harms |

**The recipe is backbone-coupled**, not backbone-independent. H3's
stack (per-fidelity y-scaler + MFRNP decoder-in-the-aggregation +
continuous-m basis head over HF latent) interacts destructively with
the asymmetric per-fidelity weighting in a way the simpler
`fno_mf_stack` aggregation does not.

**Mechanism hypothesis (informed by val/test gap):** H1's
`best_val_nRMSE=0.0783` is reasonable but `test=0.27287` — the model
trains to a fine validation minimum but generalizes terribly to
held-out test points. Plausible cause: upweighting the HF residual
(×2.0) over the basis-head + aggregation paths overconcentrates the
model's gradient budget on a narrow set of HF features that overfit,
while down-weighting LF supervision (×0.25) starves the cross-fidelity
sharing that H3's coregionalization stack depends on for generalization.
This is consistent with H3's architecture: the basis-head + aggregation
paths exist to spread information across fidelities, and uniformly
weighted LF is what gives those paths the learning signal they need.

**Aggregator-anchor scaling note** (build-phase design choice): the
H1 spec was written against H4's `smoke_eval.py`, which has no
aggregator anchor (pure residual stack). H3 has an
`agg_anchor_weight=0.5` regulariser. Builder treated "HF supervision"
as a single block and applied `hf_fid_weight` to both the HF residual
term *and* the aggregator anchor term. Effective HF/LF gradient
ratio is **slightly more aggressive than H4's pure 8:1** because the
anchor term is now upweighted too. The CEO accepted this at build
phase; the post-hoc question is whether (a) the recipe is fully
backbone-incompatible regardless of anchor scaling, or (b) the
slightly more aggressive ratio specifically pushed H3 over a cliff
that a literal 8:1 might have avoided. Cycle-004 ablation could
isolate this — but the magnitude of the regression (3.68×) makes (a)
the more likely root cause.

## Contamination handling (transparency — operationally resolved)

The first SLURM run for ifc_poisson (13973868) was contaminated: it
resumed from a partial CPU pre-train checkpoint left over from an
earlier 1800s cache-only local pass. **CEO actions on this session:**

1. Diagnosed contamination from `train_seconds=33.31s` on poisson
   vs ~461s on heat with similar dataset shapes.
2. Read checkpoint metadata via `torch.load` — both heat and poisson
   final `last.pt` had `epoch=200, epochs_target=200`, but heat trained
   fresh (461s) while poisson resumed mid-trajectory (33s).
3. Moved the contaminated poisson checkpoints to
   `.factory/research/runs/cycle-003-H1/contaminated_checkpoints/`
   (`poisson_best.pt`, `poisson_last.pt`).
4. Deleted the cached
   `results/raw/fno_coreg_residual__ifc_poisson__e200__s42__2c3be3539e1c.json`
   to force cache miss.
5. Submitted fresh SLURM job 13974837 — heat cached, poisson trained
   200 epochs from scratch on CUDA (`train_seconds=549.15`).
6. Verified clean result (0.27287) matches contaminated (0.27259) to
   within 0.10% — confirming the contamination did NOT confound the
   verdict.

**Underlying factory bug exposed (not a research issue but a systemic
one):** the checkpoint-resume guard (`epoch == epochs_target` AND
`cond_dim` match) does NOT invalidate checkpoints when the *training
recipe* changes. The same checkpoint will silently load across
experiments that change loss weights, learning-rate schedules, or any
other recipe knob. The previous cycle-002 H3 verdict's
`fno_coreg_residual_train_seconds: ifc_poisson: 25.0` was almost
certainly also contaminated, meaning **the project-best baseline
0.04420 itself may carry contamination** at an unknown but likely
smaller magnitude. Two cycle-004 backlog items filed:

- **Recipe-fingerprint checkpoint guard** — include loss-weight pair,
  any other recipe knob into the resume eligibility hash.
- **Re-verify cycle-002 H3 baseline** under a clean from-scratch run
  as a cycle-004 prerequisite before any further architectural
  experimentation.

## CEO decision

**REVERT.** Close experiment, leave branch on disk for reference but
do not promote toward master. **Cycle-003 closes with no new project
best**; cycle-002 H3 (0.04420 on `experiment/4-fno_coreg_residual @
0c46f43`) remains the project best.

This is a **genuine, scientifically-informative REVERT** — not a
bookkeeping artefact. The hypothesis was clearly stated, executed
cleanly (after contamination resolution), and falsified by data. The
factory recorded a `revert` for the first time in alignment with CEO
intent. The branch is preserved for cycle-004 to revisit with an
adaptive (rather than static) loss-weighting scheme.

## Cycle-004 implications

1. **Static MFRNP Poisson5 (2.0, 0.25) is NOT a portable recipe across
   MF-aggregation architectures.** Drop the cycle-003 framing of
   "PDE-class-bound". The recipe is backbone-coupled.
2. **Loss-weighting on H3 is still a legitimate lever** but must be
   either:
   - (a) **adaptive** — GradNorm-lite, uncertainty-weighted, or
     PCGrad-style, learned per-step from observed per-fidelity
     gradient magnitudes;
   - (b) **gentler asymmetry** — e.g. (1.5, 0.5) tuned per backbone,
     with H3 specifically receiving milder reweighting than the
     simpler H4 backbone tolerates.
3. **Checkpoint-resume guard needs a recipe fingerprint.** Without
   it every "new experiment" on an existing family silently inherits
   prior training. This is a factory-infrastructure bug worth
   pre-registering as a cycle-004 backlog item.
4. **Re-verify the cycle-002 H3 baseline (0.04420) under a clean
   from-scratch run** as cycle-004 prerequisite. The current
   project-best number may itself be contaminated, even if less
   severely.
5. **The aggregator-anchor question** (anchor scaled by `hf_fid_weight`
   vs unscaled, when an asymmetric per-fidelity weighting is active)
   is a real architectural design question that the cycle-003 H1 run
   could not isolate from the overall recipe-incompatibility signal.
   If cycle-004 returns to static weighting at all, an anchor-scaling
   ablation would be cheap.

## Status of the project-best record

- **Project best**: cycle-002 H3 at composite_nRMSE = 0.04420
  (`experiment/4-fno_coreg_residual @ 0c46f43`).
- **First family to beat paper composite geomean**: cycle-002 H3
  (0.04420 < 0.0516, 0.86×). **Status preserved.**
- **First family to beat paper ifc_heat bar individually**:
  cycle-002 H3 at 0.02634 (2.81× under paper 0.074). Also reproduced
  by cycle-003 H1 at 0.02630 (uniform-weight Heat path is unchanged).
- **Datasets beating paper**: 2 / 17 (`ifc_heat` via H1 cycle-001 at
  0.0154, 4.8× margin; `ifc_heat` via H3 cycle-002 at 0.02634, 2.81×
  margin). `ifc_poisson` still unbeaten — H4 holds best at 0.0596
  (1.66× over paper).

## Links

- Project dashboard: [[factory_mffp]]
- Build companion: [[factory_mffp-005-build]]
- Parent project-best architecture: [[factory_mffp-004-outcome]]
  (cycle-002 H3, the architecture this hypothesis built on)
- Provenance of the ported recipe: [[factory_mffp-003-experiment]]
  (cycle-002 H4 on simpler backbone — recipe origin)
- Cycle-003 strategy: [[cycle-003-strategy]]
- Cycle-003 failure analysis: [[failure-analysis-cycle-003]]
- Source papers / configs: [[mfrnp_poisson5_config]], [[niu2024mfrnp]],
  [[li2022ifc]], [[boulle2023ellipticdata]], [[chen2018gradnorm]]
- Cross-cycle patterns refuted/refined by this experiment:
  [[patterns]] §"MFRNP `Poisson5_config.yaml` knobs… orthogonally
  decompose by dataset" (cycle-002 H4 framing now bounded — recipe is
  backbone-coupled within MF-aggregation architectures);
  [[patterns]] new entry "MFRNP per-fidelity loss-weighting recipes
  are backbone-coupled across MF aggregation architectures"
- Commit: `a0d932b` on branch
  `experiment/5-fno_coreg_residual_poisson_lossweight`
- Base: `experiment/4-fno_coreg_residual` @ `0c46f43`
- SLURM jobs: 13973868 (contaminated, ~20 fresh GPU epochs),
  13974837 (clean, 200 epochs from scratch on cuda, `train_seconds=549.15`)
- Clean verdict artefact: `.factory/research/runs/cycle-003-H1/summary.json`
- CEO verdict: `.factory/reviews/ceo-verdict-evaluator.md`
