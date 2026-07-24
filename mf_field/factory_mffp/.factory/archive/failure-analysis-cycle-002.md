---
name: failure-analysis-cycle-002
description: Cycle 002 baseline failure analysis on master (v9_baseline only). Composite 1.6595 unchanged from cycle 000/001 baseline (cache hit — H1/H2 branches not yet merged). F1 (Poisson value-scale collapse) ~95% of composite, F2 (Heat backbone gap) ~5%. Two new cross-cycle failure modes added — F4 SMOKE_DEFAULT_UNDER_CAPACITY, F5 INVERSE_COMPLEMENTARY_FAMILIES. CEO-approved cycle-002 direction — hybrid fno_coreg_residual (H1 basis head over H2 residual stack) + cheap smoke-defaults bump on fno_mf_stack.
metadata:
  type: project
tags:
  - factory
  - failure-analysis
  - factory_mffp
  - cycle-002
project: factory_mffp
cycle: 002
phase: failure-analysis
date: 2026-05-15
source: factory-archivist
ceo_verdict: PROCEED
---

# Failure Analysis — Cycle 002 (factory_mffp)

## Cycle Setup
- **Scope:** baseline re-measure on `master` (v9_baseline only).
- **Datasets scored:** 2 / 2 — `ifc_heat`, `ifc_poisson` (smoke suite).
- **Run characteristics:** cache hit, 5 s wall, results reused from `results/smoke_latest.json`. Model file under test is still `references/v9_baseline/`.
- **CEO verdict on Failure Analyst:** **PROCEED**. No material issues; cycle-002 proceeds with master baseline = 1.6595 as the on-disk reference and the cycle-001 branch bests (H1=0.10919, H2=0.11173) as **trajectory context** (the experimental branches were not merged before cycle 002 — H1/H2 are off-master). See [[cycle-001-summary]] §"Awaiting human merge".

## Headline Numbers

| Metric | Master (v9, cycle 002) | Cycle 001 H1 (off-master) | Cycle 001 H2 (off-master) | Paper bar |
|---|---:|---:|---:|---:|
| composite_nRMSE | **1.6595** | 0.10919 | 0.11173 | — |
| `ifc_heat` test nRMSE | 0.14883 | **0.0154** (beats paper) | 0.1275 | 0.074 (IFC-ODE2) |
| `ifc_poisson` test nRMSE | 18.50343 | 0.7725 | **0.0979** | 0.036 (IFC-ODE2) |
| `n_datasets_beating_paper` | 0 / 2 | 1 / 2 | 0 / 2 | — |

**Cycle 000 baseline = 1.6595. Cycle 002 baseline = 1.6595.** Identical — same model file, same data, same seed. This is **not a regression and not a new baseline** — the on-disk research-target metric has not moved because H1 and H2 were not merged to master.

## Failure Distribution (geomean-weighted)

| Code | Name | Instances | Composite share | Severity |
|---|---|---:|---:|---|
| F1 | `POISSON_VALUE_SCALE_COLLAPSE` | 1 / 2 | **~95 %** | **dominant** |
| F2 | `BACKBONE_INDUCTIVE_BIAS_MISMATCH` | 1 / 2 | ~5 % | secondary |
| F3 | `MISSING_PAPER_BASELINES` (meta) | n/a | n/a | open — fixed-surface human action |
| **F4 (new)** | `SMOKE_DEFAULT_UNDER_CAPACITY` | cycle-001 H2 | n/a (cross-cycle) | recoverable via 1-knob config edit |
| **F5 (new)** | `INVERSE_COMPLEMENTARY_FAMILIES` | cycle-001 H1 vs H2 | n/a (cycle-spanning) | **structural target for cycle 002** |

### F1 — `POISSON_VALUE_SCALE_COLLAPSE`
- **Status on master:** dominant. `ifc_poisson` test nRMSE 18.50 vs paper bar 0.036 (514× over paper); val→test ratio ~13.6×.
- **Root cause (behavioral):** v9 routes prediction through a global `prior_head` MLP with no continuous fidelity index. Per-fidelity y-magnitudes collapse ~40× from L1 to L4 (observed scalers `[0.0773, 0.0237, 0.0069, 0.0018]`).
- **Status off-master (cycle 001 evidence):** mechanically resolved twice.
  - H1: 18.50 → 0.7725 (−95.8 %) via per-fidelity output normalization + continuous-m basis head.
  - H2: 18.50 → **0.0979 (−99.5 %)** via per-fidelity output normalization + MFRNP residual stack. **Best on Poisson — 7.9× better than H1.**
- **Cycle-002 prescription:** "carry the per-fidelity normalization forward in any new family" — not a novel intervention. See [[patterns]] §"Per-fidelity output normalization".

### F2 — `BACKBONE_INDUCTIVE_BIAS_MISMATCH`
- **Status on master:** secondary. `ifc_heat` test nRMSE 0.14883 vs paper bar 0.074 (2.01× over paper).
- **Root cause (behavioral):** Transolver slice-attention is designed for geometry-general / irregular meshes; IFC datasets sit on a regular 64×64 grid where the dominant signal is a small set of Fourier modes. FNO is the literature-matched inductive bias.
- **Status off-master (cycle 001 evidence):** mechanically resolved by H1.
  - H1: 0.149 → **0.0154 (−89.6 %)** via FNO + continuous-m basis. **Beats paper bar by 4.8×.**
  - H2: 0.149 → 0.1275 (regression — 8.3× worse than H1) at smoke-default config (hidden=16, modes=(4,5,5,5), 2 blocks) — F4, not an F2 problem.
- **Cycle-002 prescription:** "build on top of H1's FNO + continuous-m basis." See [[patterns]] §"FNO > Transolver for regular-grid PDE data".

### F4 (NEW) — `SMOKE_DEFAULT_UNDER_CAPACITY`
- **First observed:** cycle 001 H2.
- **Description:** when a new family ships both a `smoke_eval.py` (with hard-coded `SMOKE_DEFAULTS`) and a `full_config.json` (spec-faithful sizes), and `smoke_eval.py` does not load `full_config.json`, the SLURM run uses the small CPU-smoke config. H2's smoke defaults (`hidden=16, modes=(4,5,5,5), 2 blocks`) ran with **49× fewer params** than H1, causing the Heat regression.
- **Distinction from F2:** F2 is an inductive-bias problem (wrong architecture); F4 is a **config-surface** problem (right architecture, undersized config). Fixable by a one-knob edit, not by changing the model family.
- **Cycle-002 prescription (pre-registered, cheap):** bump `models/fno_mf_stack/smoke_eval.py:SMOKE_DEFAULTS` to `hidden=32–64, modes=(4,8,12,12), 3 blocks`. Isolates "is residual-stack bad on Heat, or was H2 just under-capacity?" — single-knob causal test.
- See [[patterns]] §"`smoke_eval.py` may not consume `full_config.json`".

### F5 (NEW) — `INVERSE_COMPLEMENTARY_FAMILIES` (cross-cycle pattern, not per-instance failure)
- **First observed:** cycle 001 H1 vs H2.
- **Description:** H1 wins big on `ifc_heat` (0.0154, beats paper) and loses on `ifc_poisson` (0.7725, 21× over paper); H2 wins big on `ifc_poisson` (0.0979, 7.9× better than H1) and regresses on `ifc_heat` (0.1275, 8.3× worse than H1). The two families' inductive biases are inverse-complementary — neither dominates both. This is **the cycle-002 synthesis gap**: not a per-instance failure of any run, but the structural feature of project state at the end of cycle 001.
- **Cycle-002 prescription:** **synthesis, not diversification.** The single highest-EV move from project state is a hybrid that fuses both inductive biases in one network. See "Recommended cycle-002 hypothesis pair" below.
- See [[patterns]] §"Coregionalization head and MFRNP residual stack are a complementary architecture pair".

## CEO-Approved Cycle-002 Hypothesis Pair

The Failure Analyst proposed 4 ranked interventions all within `models/**`. The CEO endorsed the top two — they map cleanly to `hypothesis_budget.max_new = 2` and respect the `--no-github` flag (the "land H1/H2 to master" precondition is out of CEO scope; it is a human action).

### Cycle-002 H1: `fno_coreg_residual` (hybrid — high priority)
- **Mechanism:** H1's continuous-m basis head `Σ_k B_k(m)·h_k(x)` placed on top of H2's MFRNP residual stack with decoder-in-aggregation: HF prediction = `aggregate(decoded LFs upsampled) + Σ_k B_k(m)·h_k(x)`. Per-fidelity output normalization kept (mandatory cross-cutting hygiene).
- **Files (new family under mutable surface):** `models/fno_coreg_residual/{manifest.json, INSPIRATION.md, model.py, data.py, smoke_eval.py, full_config.json}`.
- **Capacity discipline:** use full config sizes from start (`hidden ≥ 32, modes=(4,8,12,12)`) to avoid F4. Allow per-dataset full configs.
- **Expected impact (if both wins are preserved):** composite ≈ `sqrt(0.0154 · 0.0979) ≈ 0.039`. Paper-class on both datasets; **2/2 beating paper plausible**.
- **Risk:** if HF residual budget forces basis K below the H1 minimum, Heat may not be captured. Mitigation: per-dataset `full_config.json` allows heavier configs on Heat.

### Cycle-002 H2: `fno_mf_stack` smoke-defaults bump (cheap, pre-registered)
- **Mechanism:** edit-only one-knob change. `models/fno_mf_stack/smoke_eval.py:SMOKE_DEFAULTS` to read from `full_config.json` (or hard-bump to `hidden=32–64, modes=(4,8,12,12), 3 blocks`). No `model.py` change.
- **Precondition:** requires H2 branch to be landed (or work on `experiment/2-fno_mf_stack` directly).
- **Expected impact:** if F4 was the bottleneck, Heat returns to roughly H1's territory (0.02–0.04) while Poisson stays at 0.0979. Composite ≈ `sqrt(0.03 · 0.10) ≈ 0.055`. Also paper-class.
- **Decision value:** isolates F4 from inductive-bias claims about residual-stack on Heat. Decisive either way; cheap.

### Deferred
- **Intervention 3 (tune H1 harder on Poisson):** lower expected upside than H1 (cycle-002); H2 already showed residual stack is 7.9× better than basis-alone on Poisson. Fallback only.
- **Intervention 4 (third orthogonal family — `siren_film_fidelity`, `fire_field`, `transolver_residual`):** deferred. Cycle-001 evidence says **synthesis > diversification** from current project state.

## Cross-Cycle Comparison

| Cycle / Run | Composite | `ifc_heat` | `ifc_poisson` | Beats paper? | Vs master |
|---|---:|---:|---:|---|---|
| 000 baseline (master, v9) | 1.6595 | 0.14883 | 18.50 | 0 / 2 | — |
| 001 H1 (FNO + coreg) | **0.10919** | **0.0154** | 0.7725 | 1 / 2 (Heat) | −93.4 % |
| 001 H2 (FNO + MFRNP stack) | 0.11173 | 0.1275 | **0.0979** | 0 / 2 | −93.3 % |
| 002 baseline (master, v9) | 1.6595 | 0.14883 | 18.50 | 0 / 2 | unchanged |

Project on-disk state did not move between cycles 000 and 002 because experimental branches were not merged. Cycle-002 must reason from BOTH master (1.6595) and the branch bests (H1=0.10919, H2=0.11173) — explicitly.

## Failure Taxonomy (running)

| Code | Name | First observed | Status |
|---|---|---|---|
| F1 | `POISSON_VALUE_SCALE_COLLAPSE` | cycle 000 | confirmed twice fixable by per-fidelity normalization; residual-stack 8× stronger than continuous-m basis on Poisson |
| F2 | `BACKBONE_INDUCTIVE_BIAS_MISMATCH` (Transolver vs regular grid) | cycle 000 | fixed once by H1's FNO swap (Heat 0.149 → 0.0154) |
| F3 | `MISSING_PAPER_BASELINES` (meta) | cycle 000 | open — `baselines/**` is fixed surface, human action required |
| F4 (new) | `SMOKE_DEFAULT_UNDER_CAPACITY` | cycle 001 H2 | recoverable by 1-knob config edit (pre-registered cycle-002 H2) |
| F5 (new) | `INVERSE_COMPLEMENTARY_FAMILIES` | cycle 001 H1 vs H2 | structural — target of cycle-002 H1 hybrid |

## CEO Issues / Notes
- **None material.** CEO PROCEED on Failure Analyst output.
- **Minor:** the Failure Analyst recommended "land H1 and H2 to master" as a precondition. Out of CEO scope under `--no-github`. Cycle-002 will proceed with master baseline = 1.6595 and trajectory-aware comparison to H1/H2 branch bests.
- **Researcher instructions (next step, R1.5):** focus on F5 synthesis question — do FNO + coregionalization heads + residual stacking compose? Look for 2024–2026 empirical evidence on hybrid MF field-prediction architectures. Spot-check whether anyone has composed IFC-style coregionalization with MFRNP-style residual stacking; if novel, proceed on first-principles. Also surface smoke-vs-full-config best-practices literature for F4. Append to `.factory/strategy/research.md`. See [[ceo-verdict-failure_analyst]] (this cycle).

## Related notes
- [[factory_mffp-dashboard]] — project dashboard
- [[cycle-001-summary]] — cycle 001 close-out, complementary-pair pattern, pre-registered cycle-002 hypotheses
- [[factory_mffp-001-experiment]] — H1 final outcome
- [[factory_mffp-002-experiment]] — H2 final outcome
- [[patterns]] §"Per-fidelity output normalization", §"Continuous-fidelity index", §"FNO > Transolver", §"Coregionalization head and MFRNP residual stack are a complementary architecture pair", §"`smoke_eval.py` may not consume `full_config.json`"
- [[cycle-001-failure-diagnosis]] — prior-cycle F1/F2/F3 framing
- [[cycle-001-cross-cutting-findings]]
