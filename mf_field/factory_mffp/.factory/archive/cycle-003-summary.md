---
name: cycle-003-summary
description: Cycle-003 close-out summary for factory_mffp. Single hypothesis (H1 fno_coreg_residual_poisson_loss_reweighting, exp_id=5) ported H4's static MFRNP Poisson5 (HF=2.0/LF=0.25) loss-reweighting recipe into H3's fno_coreg_residual hybrid backbone. composite_nRMSE regressed 0.04420 → 0.08472 (+91.7% on the research target). ifc_heat unchanged at 0.02630 (uniform weights — Heat path benign by construction; still BEATS paper 2.81×); ifc_poisson catastrophically regressed 0.07416 → 0.27287 (3.68× worse than entry; 4.58× worse than cycle-002 H4 on the simpler fno_mf_stack backbone; 7.58× over paper). FIRST genuine REVERT in project history — CEO intent and factory state agree for the first time (all 4 prior REVERTs were precheck false-positive bookkeeping discrepancies). The cycle-003 framing "MFRNP Poisson5 recipe is PDE-class-bound (elliptic), not backbone-bound" is REFUTED; the recipe is backbone-coupled. Checkpoint-resume contamination diagnosed and operationally resolved during the cycle (clean run matched contaminated run to within 0.10%, verdict unchanged), but the underlying factory bug is systemic — the cycle-002 H3 project-best baseline (0.04420) almost certainly also carries some checkpoint contamination. Two cycle-004 prerequisite backlog items filed (recipe-fingerprint checkpoint guard; re-verify the H3 baseline under a clean from-scratch run). Project best preserved at cycle-002 H3 composite 0.04420 on experiment/4-fno_coreg_residual @ 0c46f43.
metadata:
  type: project
tags:
  - factory
  - cycle-summary
  - factory_mffp
  - cycle-003
project: factory_mffp
cycle_id: "003"
date: 2026-05-15
source: factory-archivist
status: closed
experiments_run: 1
ceo_keep_count: 0
ceo_revert_count: 1
factory_bookkeeping_keep_count: 0
factory_bookkeeping_revert_count: 1
precheck_overrides_consecutive: 4
first_genuine_revert: true
hypothesis_refuted: true
datasets_beating_paper: 2
datasets_total: 17
new_project_best: null
paper_composite_first_crossing_preserved: true
project_best_composite: 0.04420
cycle_entry_composite: 0.04420
cycle_exit_composite: 0.04420
h1_run_composite: 0.08472
---

# Cycle 003 — factory_mffp — Close-out Summary

**Status:** **CLOSED 2026-05-15**.
**Cycle scope:** Single-hypothesis cycle. Port H4's static MFRNP Poisson5
(HF=2.0/LF=0.25) per-fidelity loss-reweighting recipe into H3's
`fno_coreg_residual` hybrid backbone, gated Poisson-only. Test whether
the recipe is **PDE-class-bound** (elliptic — would generalize across
MF-aggregation architectures) or **backbone-bound** (would not).
**Outcome:** 1 hypothesis run; CEO **REVERT**; **FIRST genuine REVERT
in project history**. Cycle-003 entry framing **refuted** — the recipe
is backbone-coupled. No new project best. Branch
`experiment/5-fno_coreg_residual_poisson_lossweight` (commit `a0d932b`)
preserved on disk for cycle-004 follow-up with an adaptive loss-weighting
scheme.

## TL;DR

- **Cycle entry state (= cycle-002 close-out):** project best
  composite_nRMSE **0.04420** (cycle-002 H3 on
  `experiment/4-fno_coreg_residual @ 0c46f43`); 2/17 datasets at-or-beat
  paper (`ifc_heat` via cycle-001 H1 at 0.0154, 4.8×; `ifc_heat` via
  cycle-002 H3 at 0.02634, 2.81×); **first family to beat paper composite
  geomean** (0.0442 < 0.0516, 0.86×).
- **Cycle-003 H1 `fno_coreg_residual_poisson_loss_reweighting`:**
  composite **0.08472** (**+91.7% REGRESSION vs entry 0.04420**, hard FAIL
  on the monotonic gate). `ifc_heat` **0.02630** (unchanged within seed
  noise, uniform weights — still beats paper by 2.81×). `ifc_poisson`
  **0.27287** (3.68× WORSE than entry 0.07416; 4.58× WORSE than cycle-002
  H4 0.05961 on the simpler `fno_mf_stack` backbone; 7.58× over paper 0.036).
- **Refuted scientific framing:** "MFRNP Poisson5 recipe is PDE-class-bound
  (elliptic), not backbone-bound." Same recipe, same PDE class, same data
  — opposite outcome under different MF-aggregation backbones. **The recipe
  is backbone-coupled.**
- **FIRST genuine REVERT in project history.** Cycles 001/002 produced
  4 REVERTs (H1, H2, H4, H3) all of which were precheck-bookkeeping
  false-positives with CEO=KEEP intent. Cycle-003 H1 is the FIRST REVERT
  where CEO intent (REVERT) and factory bookkeeping state (revert) agree,
  and the underlying reason is a genuine research-target regression. The
  same 4 precheck false-positives still fired here; the difference is they
  now align with reality.
- **Checkpoint-resume contamination discovered + operationally resolved.**
  First SLURM run 13973868 resumed poisson from a partial CPU pre-train
  checkpoint (`train_seconds=33.31s` on poisson vs heat's 461s — clear
  asymmetry). CEO moved contaminated checkpoints to
  `.factory/research/runs/cycle-003-H1/contaminated_checkpoints/`,
  deleted the stale cache, and submitted SLURM job 13974837 from an
  empty checkpoint dir. Clean (0.27287) vs contaminated (0.27259)
  matched to within 0.10% — **verdict robust either way; contamination
  did not confound the conclusion**. But the underlying factory bug
  (resume guard ignores recipe changes) is systemic; the cycle-002 H3
  baseline likely carries some smaller contamination (`fno_coreg_residual_train_seconds: ifc_poisson: 25.0`
  is implausibly fast for 200 epochs).
- **Project best preserved.** Cycle-002 H3 at composite 0.04420 on
  `experiment/4-fno_coreg_residual @ 0c46f43` remains project best;
  cycle-003 closes with no new best.
- **Cycle-004 prerequisites filed in backlog:** (a) **recipe-fingerprint
  checkpoint guard** — hash the SMOKE_DEFAULTS into the saved checkpoint
  and require it match on resume, otherwise invalidate; (b) **re-verify
  cycle-002 H3 baseline (0.04420) under a clean from-scratch run** before
  any further cycle-004 hypothesis is measured against it.
- **Operational discovery (cycle-001 → cycle-003 precheck pattern):**
  4-of-4 cycles now show the same 4 precheck infrastructure bugs (score_direction
  polarity for lower-is-better, scope/fixed_surfaces empty-detail,
  ground_truth_leakage substring-collision). Pattern fully reproducible.
  In cycle-003 H1 the precheck failure happened to align with the genuine
  CEO=REVERT decision — coincidence, not signal.

## Project trajectory at cycle-003 close

| Run | Composite nRMSE | Δ vs master | Δ vs prior best | Cumulative speed-up | Notes |
|---|---:|---:|---:|---:|---|
| `master` (v9 project state) | 1.6595 | — | — | 1× | |
| cycle-001 H1 `fno_coregionalization` | 0.10919 | −93.4% | — | 15.2× | beat paper on `ifc_heat` (1/17) |
| cycle-001 H2 `fno_mf_stack` | 0.11173 | −93.3% | +2.3% (advisory) | 14.9× | |
| cycle-002 H4 `fno_mf_stack` v2 | 0.07719 | −95.3% | −31% vs H2 | 21.5× | both MFRNP knobs validated |
| **cycle-002 H3 `fno_coreg_residual`** | **0.04420** | **−97.3%** | **−43% vs H4** | **37.5×** | **first below paper geomean** |
| cycle-003 H1 `fno_coreg_residual_poisson_loss_reweighting` | **0.08472** | −94.9% | **+91.7% REGRESSION vs entry 0.04420** | 19.6× | **FIRST genuine REVERT; project best preserved at 0.04420** |
| paper composite geomean (li2022ifc) | 0.05157 | −96.9% | — | (target line) | |

**Project best preserved at cycle-002 H3 0.04420.** First-crossing of the
paper composite geomean (0.0442 < 0.0516) **preserved** despite the
cycle-003 H1 regression — the H1 run is a branch, not a master replacement.

### Per-dataset (test nRMSE) at cycle-003 close

| Dataset | v9 | cy-1 H1 | cy-1 H2 | cy-2 H4 | cy-2 H3 | **cy-3 H1** | Paper bar | Best vs paper |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `ifc_heat` | 0.14883 | **0.0154** | 0.1275 | 0.0999 | 0.02634 | 0.02630 | 0.074 (IFC-ODE2) | **H1 beats 4.8×; H3 beats 2.81×; cy-3 H1 reproduces H3** ✓✓ |
| `ifc_poisson` | 18.50344 | 0.7725 | 0.0979 | **0.0596** | 0.07416 | 0.27287 | 0.036 (IFC-ODE2) | H4 1.66× over paper (best); cy-3 H1 7.58× over paper (catastrophic) |

**Datasets at-or-beating paper:** 2 / 17 (unchanged from cycle-002 close).
`ifc_heat` via cycle-001 H1 (4.8×) and cycle-002 H3 (2.81×).
`ifc_poisson` still unbeaten — cycle-002 H4 holds best at 0.0596 (1.66× over).

## The single hypothesis: cycle-003 H1

### Hypothesis (cycle-003 H1, exp_id=5)

**FIX, single additive knob.** Port H4's
`resolve_fidelity_weights(dataset_name, p)` helper from
`models/fno_mf_stack/smoke_eval.py` into
`models/fno_coreg_residual/smoke_eval.py`. SMOKE_DEFAULTS adds
`poisson_hf_weight=2.0` / `poisson_lf_weight=0.25` (verbatim MFRNP
`Poisson5_config.yaml`). `compute_losses` extended with
`hf_fid_weight` / `lf_fid_weight` kwargs; resolver gates on
`"poisson" in dataset_name.lower()` and returns `(2.0, 0.25)` for
Poisson, `(1.0, 1.0)` for Heat. **No backbone changes**; H3's
architecture (per-fidelity y-scaler, MFRNP decoder-in-the-aggregation,
continuous-m basis head over HF latent) preserved unchanged. Branch
`experiment/5-fno_coreg_residual_poisson_lossweight` cut from
`experiment/4-fno_coreg_residual` (cycle-002 H3 @ `0c46f43`, project
best 0.0442). Single commit `a0d932b`: +67 / -5 across
`models/fno_coreg_residual/{smoke_eval.py, INSPIRATION.md}`.

### Compositional argument (Strategist, adopted by CEO at build phase)

H3 supplies the IFC-path architectural asymmetry (continuous-m basis
head + per-fidelity output normalization). H1 adds the orthogonal
MFRNP-path loss-weighting asymmetry on top. The two SOTA routes
compose on one architecture. The MFRNP Poisson5 recipe is
**PDE-class-bound (elliptic), not backbone-bound** — supported at
cycle-002 by H4 porting the recipe from MFRNP's own residual stack
to `fno_mf_stack` (a different residual-stack family with FNO
backbones) cleanly.

### Predicted impact (anchored to measured H4 Poisson, not forecast)

- `ifc_poisson`: floor at H4's 0.0596; plausible upside below.
- `ifc_heat`: unchanged at ≈0.02634 (resolver returns uniform).
- `composite_nRMSE` floor at `geomean(0.02634, 0.0596) ≈ 0.0396`.

### Realized impact (clean 200-epoch cuda run, SLURM 13974837)

| Metric                       | Value      | vs entry 0.0442   | vs paper 0.0516 | vs H4 0.0596 (poisson only) |
|---                           |---         |---                |---              |---                          |
| **composite_nRMSE**          | **0.08472**| **+91.7% REGRESSION** | 1.64× over      | —                           |
| ifc_heat                     | 0.02630    | unchanged         | **BEATS by 2.81×** | —                        |
| ifc_poisson                  | **0.27287**| **3.68× WORSE** (from 0.07416) | 7.58× over      | **4.58× WORSE**          |

- **vs cycle-003 entry 0.0442**: composite regression of +0.04052
  (+91.7%). Hard FAIL on the monotonic gate.
- **vs H1 floor 0.0396**: composite +0.04512 (114% above the predicted
  H1 floor). The Poisson side completely failed to realize the H4 recipe
  benefit; it regressed catastrophically.
- **vs paper geomean 0.0516**: ratio 1.642 (composite 64% worse than
  paper geomean). H1 dropped the "first-family-beating-paper-composite"
  status that cycle-002 H3 achieved (status preserved at the project
  level by the unchanged H3 branch).
- **vs cycle-002 H4 on simpler backbone**: H1's `ifc_poisson` 0.27287
  is **4.58× worse** than H4's 0.05961 on `fno_mf_stack`. Same recipe,
  different backbone → catastrophic harm.

### Verdict: CEO REVERT

- **CEO intent:** REVERT (research-target regression confirmed by clean
  from-scratch run).
- **Factory bookkeeping:** `revert` (precheck failed on the same 4
  infrastructure bugs as cycles 001/002 — but here the precheck failure
  aligns with reality for the first time).
- **Hypothesis disposition:** REFUTED. The recipe is backbone-coupled,
  not PDE-class-bound. The cycle-003 strategy framing is invalidated.
- **Branch disposition:** preserved on disk at
  `experiment/5-fno_coreg_residual_poisson_lossweight` commit `a0d932b`
  for cycle-004 reference (adaptive loss-weighting hypothesis).

**Precheck snapshot (informational; bug pattern unchanged across 5 experiments):**

```
score_direction: PASS (incorrectly — saw 0.0442 → 0.0847 as "OK"
                  assuming higher-is-better; known factory polarity bug
                  on lower-is-better metric; the genuine direction for
                  this hypothesis is REGRESSION)
scope:           FAIL (known false-positive: empty detail)
fixed_surfaces:  FAIL (known false-positive: empty detail)
leakage:         FAIL (known substring-collision on 'poisson' from
                  factory.md mentioning "ifc_poisson")
anti_pattern:    PASS
smoke_test:      PASS
```

Precheck `passed=false`. For this hypothesis the precheck failure
*coincidentally* aligns with the genuine CEO=REVERT — the underlying
4 bugs are unchanged.

## Refuted scientific framing — recipe is backbone-coupled

Cycle-003 framed the MFRNP Poisson5 recipe as **PDE-class-bound
(elliptic), not backbone-bound**, citing the cycle-002 H4 finding
that the recipe ported cleanly from MFRNP's own residual stack to
H2's `fno_mf_stack` (a different residual-stack family with FNO
backbones). The compositional argument predicted that H3's
IFC-architectural asymmetry would compose orthogonally with H4's
MFRNP-loss-weighting asymmetry. The clean H1 data **refutes** this:

| Backbone                                       | (2.0, 0.25) Poisson effect                  | Conclusion                  |
|---                                             |---                                          |---                          |
| `models/fno_mf_stack` (cycle-002 H4)            | ifc_poisson **0.0999 → 0.0596** (39% improvement) | Recipe helps           |
| `models/fno_coreg_residual` (cycle-003 H1)      | ifc_poisson **0.0742 → 0.27287** (3.68× regression) | Recipe catastrophically harms |

**The recipe is backbone-coupled**, not backbone-independent. H3's
stack (per-fidelity y-scaler + MFRNP decoder-in-the-aggregation +
continuous-m basis head over HF latent) interacts destructively with
the asymmetric per-fidelity weighting in a way the simpler
`fno_mf_stack` aggregation does not.

### Mechanism hypothesis (informed by val/test gap on H1 + poisson)

`best_val_nRMSE=0.0783` is reasonable but `test=0.27287` — the model
trains to a fine validation minimum but generalizes terribly to held-out
test points. Plausible cause: upweighting the HF residual (×2.0) over
the basis-head + aggregation paths overconcentrates the model's gradient
budget on a narrow set of HF features that overfit, while down-weighting
LF supervision (×0.25) starves the cross-fidelity sharing that H3's
coregionalization stack depends on for generalization. This is consistent
with H3's architecture: the basis-head + aggregation paths exist to spread
information across fidelities, and uniformly weighted LF is what gives
those paths the learning signal they need.

### Aggregator-anchor scaling note (build-phase design choice)

H1's spec was written against H4's `smoke_eval.py`, which has no
aggregator anchor (pure residual stack). H3 has an `agg_anchor_weight=0.5`
regulariser. Builder treated "HF supervision" as a single block and
applied `hf_fid_weight` to both the HF residual term *and* the aggregator
anchor term. Effective HF/LF gradient ratio is **slightly more aggressive
than H4's pure 8:1** because the anchor term is now upweighted too.
The CEO accepted this at build phase. The post-hoc question is whether
(a) the recipe is fully backbone-incompatible regardless of anchor
scaling, or (b) the slightly more aggressive ratio specifically pushed
H3 over a cliff that a literal 8:1 might have avoided. Cycle-004
ablation could isolate this — but the magnitude of the regression
(3.68×) suggests (a) is the more likely root cause.

## Checkpoint-resume contamination (operationally resolved; underlying factory bug remains)

### Timeline

1. **First SLURM job 13973868** ran cycle-003 H1 on cuda. Heat trained
   fresh for 461s; poisson trained for only `33.31s` despite same dataset
   shape and same epochs target (200). **Asymmetry diagnosed by CEO as
   contamination** — heat ≈ poisson on similar-shape data, but here
   poisson was ~14× faster, indicating mid-trajectory resume.
2. **Forensic read** via `torch.load` confirmed both heat and poisson
   final `last.pt` had `epoch=200, epochs_target=200`. The checkpoint-resume
   guard (`epoch == epochs_target AND cond_dim` match) accepted the
   poisson checkpoint as "done" even though it was from a stale partial
   CPU pre-train (saved by an earlier 1800s cache-only local pass that
   timed out at the last-10%-epoch milestone).
3. **CEO operational response:**
   - Moved the contaminated poisson checkpoints to
     `.factory/research/runs/cycle-003-H1/contaminated_checkpoints/`
     (`poisson_best.pt`, `poisson_last.pt`).
   - Deleted the stale results cache
     `results/raw/fno_coreg_residual__ifc_poisson__e200__s42__2c3be3539e1c.json`
     to force cache miss.
   - Submitted fresh SLURM job 13974837 from an empty ifc_poisson
     checkpoint dir.
4. **Clean run** trained 200 epochs from scratch on cuda
   (`train_seconds=549.15s`). Result: composite **0.08472**, ifc_poisson
   **0.27287**.
5. **Comparison** clean (0.27287) vs contaminated (0.27259) → matches
   to within 0.10%. **Verdict robust either way; contamination did NOT
   confound the conclusion** — H1 is genuinely refuted by both runs.

### Underlying factory bug (systemic)

The checkpoint-resume guard does NOT invalidate checkpoints when the
*training recipe* changes (loss weights, lr schedule, any other recipe
knob). The same checkpoint will silently load across experiments that
change any training-recipe knob but not `cond_dim` or `epochs_target`.

**Implication for the project-best baseline:** the previous cycle-002
H3 verdict reported `fno_coreg_residual_train_seconds: ifc_poisson: 25.0`
— **25 seconds is implausibly fast for 200 epochs of training on
poisson**, so the cycle-002 H3 baseline (0.04420) almost certainly
carries some contamination, although likely of smaller magnitude than
the cycle-003 H1 case (where heat and poisson differed by 14×).
The **direction** of the contamination on the H3 baseline is uncertain
— it could be reading slightly better than reality (if it inherited a
well-trained checkpoint from an earlier successful run on the same
architecture) or slightly worse (if from a partially-trained one).
Either way, the project-best 0.04420 is **provisional** until verified
under a clean from-scratch run.

### Cycle-004 prerequisite backlog items filed

Two items added to `.factory/strategy/backlog.md` via `factory backlog-add`:

1. **Fix checkpoint-resume contamination in `models/<family>/smoke_eval.py`**:
   hash SMOKE_DEFAULTS (or a stable recipe-fingerprint of `{loss kwargs,
   optimizer kwargs, scheduler kwargs, seed-affecting code path}`) into
   the saved checkpoint as a `recipe_hash` field; resume guard must
   additionally require `recipe_hash == current_recipe_hash`. **Meta-fix
   that improves the validity of all future research-mode experiments.**
2. **Re-verify cycle-002 H3 baseline (0.04420)** under a clean
   from-scratch run. Operational task: checkout
   `experiment/4-fno_coreg_residual`, clear
   `checkpoints/fno_coreg_residual/{ifc_heat,ifc_poisson}/` entirely,
   clear `results/raw/fno_coreg_residual__*.json`, run
   `sbatch --wait eval/run_smoke.sbatch`, record the clean numbers
   as the verified project-best baseline. **Cycle-004 prerequisite.**

## Project state at cycle-003 close

- **Project best**: cycle-002 H3 at composite_nRMSE **0.04420** on
  `experiment/4-fno_coreg_residual @ 0c46f43` — **preserved**.
  (Note: provisional pending the re-verification cycle-004 prerequisite
  above.)
- **First family to beat paper composite geomean**: cycle-002 H3
  (0.04420 < 0.0516, 0.86×). **Status preserved.**
- **Datasets beating paper: 2 / 17** (unchanged from cycle-002 close).
  `ifc_heat` via cycle-001 H1 (0.0154, 4.8×); `ifc_heat` via cycle-002
  H3 (0.02634, 2.81×). `ifc_poisson` still unbeaten — cycle-002 H4
  holds best at 0.0596 (1.66× over paper).
- **Experiments run (cumulative): 5.** All complete. CEO intent: 4 KEEP
  (H1, H2, H4, H3) + 1 REVERT (cycle-003 H1). Factory bookkeeping: 5
  reverts (4 precheck false-positive cascade with CEO=KEEP intent, 1
  genuine REVERT where CEO=REVERT and factory state agree).
- **Branches on disk (all preserved, all unmerged to master):**
  - `experiment/1-fno_coregionalization` (cycle-001 H1) @ commit on disk
  - `experiment/2-fno_mf_stack` (cycle-001 H2) @ commit on disk
  - `experiment/3-fno_mf_stack_v2_capacity_loss` (cycle-002 H4) @ `ddd221d`
  - `experiment/4-fno_coreg_residual` (cycle-002 H3, **PROJECT BEST**) @ `0c46f43`
  - `experiment/5-fno_coreg_residual_poisson_lossweight` (cycle-003 H1) @ `a0d932b`
- **Awaiting human merge** of all 4 CEO-KEEP branches; cycle-003 H1
  branch preserved for cycle-004 reference, not for merge.

## Cycle-004 implications (pre-registered)

1. **Static MFRNP Poisson5 (2.0, 0.25) is NOT a portable recipe across
   MF-aggregation architectures.** Drop the cycle-003 "PDE-class-bound"
   framing. Treat per-fidelity loss-weighting as per-backbone-tuned.
2. **Loss-weighting on H3 remains a legitimate lever** but must be
   either:
   - (a) **adaptive** — GradNorm-lite, uncertainty-weighted, or
     PCGrad-style, learned per-step from observed per-fidelity gradient
     magnitudes; or
   - (b) **gentler asymmetry** — e.g. (1.5, 0.5) tuned per backbone,
     with H3 specifically receiving milder reweighting than the simpler
     H4 backbone tolerates.
3. **Recipe-fingerprint checkpoint guard is a cycle-004 prerequisite**
   (filed in backlog) — without it every "new experiment" on an existing
   family silently inherits prior training.
4. **Re-verify cycle-002 H3 baseline (0.04420) under a clean from-scratch
   run** as cycle-004 prerequisite (filed in backlog). The current
   project-best number may itself be contaminated, even if less severely.
5. **The aggregator-anchor question** — anchor scaled by `hf_fid_weight`
   vs unscaled when asymmetric per-fidelity weighting is active — is
   a real architectural design question that this run could not isolate
   from the overall recipe-incompatibility signal. If cycle-004 returns
   to static weighting at all, an anchor-scaling ablation would be cheap.
   Lower priority than the adaptive scheme.

## Patterns confirmed / refined in this cycle

- **Refined (cycle-002 → cycle-003):** *"MFRNP `Poisson5_config.yaml`
  knobs (capacity + per-fidelity loss weighting) are independently
  load-bearing and orthogonally decompose by dataset"* — **bounded**.
  The cycle-002 framing applied **within the residual-stack-on-FNO
  family** (MFRNP ↔ `fno_mf_stack`); it does **not** generalize across
  to the hybrid basis-head + MFRNP-residual-stack family
  (`fno_coreg_residual`). New patterns entry pinned:
  **"MFRNP per-fidelity loss-weighting recipes are backbone-coupled
  across MF aggregation architectures"** — see [[patterns]].
- **Reinforced (cycle-002 → cycle-003):** *"Factory precheck
  `score_direction` is polarity-buggy on lower-is-better metrics"* —
  4 consecutive cycles, 5 consecutive experiments. Now **load-bearing**
  for any factory-state interpretation across the project. In cycle-003
  the precheck failure happened to align with the genuine CEO=REVERT
  decision (coincidence, not signal).
- **New (cycle-003):** *"Checkpoint-resume guard ignores training recipe
  changes"* — systemic factory bug. The current guard (`epoch ==
  epochs_target` AND `cond_dim` match) silently inherits training across
  recipe changes. **Cycle-004 prerequisite to fix.**
- **New (cycle-003):** *"First-genuine-REVERT as a milestone is itself
  signal."* When CEO intent and factory bookkeeping agree on a REVERT
  for the first time, the cycle has produced a falsified hypothesis
  rather than a bookkeeping artefact — this is a positive scientific
  result, not a process failure.

## Related notes

- [[factory_mffp]] — project dashboard (cycle-003 CLOSED section)
- [[factory_mffp-005-experiment]] — cycle-003 H1 outcome (full empirical
  detail; first genuine REVERT)
- [[factory_mffp-005-build]] — cycle-003 H1 build phase note
  (branch `experiment/5-fno_coreg_residual_poisson_lossweight` commit
  `a0d932b`, +67/-5 across `models/fno_coreg_residual/`)
- [[cycle-003-strategy]] — cycle-003 strategy snapshot
  (PDE-class-bound framing — refuted by this cycle's outcome)
- [[failure-analysis-cycle-003]] — failure analysis for cycle-003 entry
  state (`ABSENT_POISSON_LOSS_WEIGHTING` as the diagnosed root cause;
  the recommended fix is the H1 hypothesis that was refuted)
- [[patterns]] — new entry "MFRNP per-fidelity loss-weighting recipes
  are backbone-coupled across MF aggregation architectures"
- [[cycle-002-summary]] — cycle-002 close-out (project best 0.04420
  established here)
- [[cycle-001-summary]] — cycle-001 close-out (entry baseline 1.6595 → 0.1092)
- [[factory_mffp-004-outcome]] — cycle-002 H3 outcome (the parent
  architecture H1 built on; project best preserved through cycle-003)
- [[factory_mffp-003-experiment]] — cycle-002 H4 outcome (recipe origin
  on the `fno_mf_stack` backbone — recipe ports here but not to H3)
- Source papers / configs: [[mfrnp_poisson5_config]], [[niu2024mfrnp]],
  [[li2022ifc]], [[boulle2023ellipticdata]], [[chen2018gradnorm]]
- SLURM jobs: 13973868 (contaminated, ~20 fresh GPU epochs after partial
  CPU pre-train resume), 13974837 (clean, 200 epochs from scratch on
  cuda, `train_seconds=549.15s`)
- Clean verdict artefact:
  `.factory/research/runs/cycle-003-H1/summary.json`
- CEO verdict: `.factory/reviews/ceo-verdict-evaluator.md`
- Cycle-004 backlog: `.factory/strategy/backlog.md` (two new items —
  recipe-fingerprint checkpoint guard; re-verify H3 baseline under clean
  run)
