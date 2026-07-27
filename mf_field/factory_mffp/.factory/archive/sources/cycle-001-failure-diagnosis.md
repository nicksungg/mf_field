---
name: cycle-001-failure-diagnosis
description: Cycle 001 failure picture for factory_mffp. composite_nRMSE=1.6595. F1=ifc_poisson value-scale collapse (95% of penalty). F2=ifc_heat backbone gap. F3=missing paper numbers. Root cause — no continuous fidelity index in v9.
metadata:
  type: reference
tags:
  - factory
  - source
  - failure-analysis
  - cycle-001
source: factory-archivist
date: 2026-05-15
cycle: "001"
project: factory_mffp
---

# Cycle 001 — Failure Diagnosis (factory_mffp)

## Composite score

`composite_nRMSE = 1.6595` (geomean of per-dataset test nRMSE on `ifc_heat`, `ifc_poisson`).

| dataset      | test nRMSE | best_val nRMSE | val→test gap | paper m=1 bar    |
|---           |---:        |---:            |---:          |---:              |
| ifc_heat     | 0.14883    | 0.05245        | ~3×          | 0.074 (IFC-ODE2) |
| ifc_poisson  | 18.50344   | 1.36508        | ~13.6×       | 0.036 (IFC-ODE2) |

## F1 — `ifc_poisson` test value-scale collapse (95% of composite penalty)

**Researcher's key diagnostic insight** (sharper than the manual CEO stub): the failure is **NOT** classical OOD distributional shift. It is a **value-scale shift across fidelities**.

The Poisson solution magnitude shrinks ~10× at every refinement step (Poisson finite-difference normalization — solution scale ∝ h² for the rescaled equation in `mffpbench`). Specifically:

| fidelity | y-max range            |
|---       |---                     |
| L1 8×8   | up to **0.0773**       |
| L2 16×16 | up to **0.0237**       |
| L3 32×32 | up to **0.00694**      |
| L4 64×64 | up to **0.00184** (train) / **0.00215** (test) |

The y-scale **collapses ~40× from L1 (8×8) to L4 (64×64)**. The model trains on 100 L1 + 50 L2 + 20 L3 + 2-3 effective HF samples (val_frac=0.2 steals from the 5 HF samples), so it learns to predict y at the LF scale (mean magnitude ~0.04). The test set is *exclusively L4* (mean magnitude ~0.0003). Predictions are 10–40× too large → RMSE/||target|| ≈ 0.01/0.001 ≈ 10. Observed 18.5 is consistent with this magnitude analysis.

**Why v9 fails structurally** (from reading `references/v9_baseline/model_v9.py`):
- v9 has **no continuous fidelity index**. Each LF stream is attended to separately via `cross_*_proj`, then mixed by a learned `gate_mlp(softmax)`.
- `pressure_embed` only feeds LF *output values* as an additive gate. The HF query side (`hf_encoder`) sees only coordinates + condition vector — **no fidelity index**.
- `prior_head` MLP is global → averages toward most-frequent training scale (L1 ≈ 0.04). For HF test (mean ~0.0003), prior is off by 100×.
- `delta_mlp` is zero-init and supposed to learn HF correction, but with only 2-3 effective HF training points and a 200-epoch smoke schedule, never accumulates enough HF signal to dwarf the prior.

## F2 — `ifc_heat` gap to SOTA (~5% of composite penalty by magnitude, but architecturally important)

- v9 test nRMSE = 0.149 vs IFC-ODE2 at m=1 = **0.074** (~2× worse), and ~3–4× worse than IFC-GPODE (~0.04 from Fig. 4(b)).
- Why heat is "only" 0.15 and not catastrophic: heat-equation y values are bounded **[0, 1] regardless of fidelity** → no value-scale shift.
- The Heat gap is therefore a **pure backbone / inductive-bias gap**, not a scale-shift failure. Transolver's slice-attention is wrong for regular-grid PDE data; FNO is the right inductive bias. See [[li2020fno]] and [[cycle-001-cross-cutting-findings]].

## F3 — Missing paper numbers (meta-blocker)

- `baselines/paper_baselines.json` has empty `"splits": {}` for both `ifc_heat` and `ifc_poisson`.
- `vs_paper.beats_paper` is forced to `false` regardless of model quality → `n_datasets_beating_paper` is stuck at 0.
- `baselines/` is a **fixed surface** — Researcher cannot edit. **Human action required**, see [[paper-baselines-proposals]].

## Failure distribution

- F1 — `ifc_poisson` test value-scale collapse: **~95%** of composite (the 18.5 entry dominates the geomean).
- F2 — `ifc_heat` gap to SOTA: ~5% by absolute magnitude, but the modeling lessons (better backbone, better MF fusion) directly transfer to F1.
- F3 — Missing paper numbers: not a numeric failure, a meta-blocker.

## Related

- [[li2022ifc]] — source paper for the datasets; contains the architectural answer (continuous-m basis).
- [[cycle-001-candidate-ranking]] — H1 fno_coregionalization and H2 fno_mf_stack proposed.
- [[cycle-001-cross-cutting-findings]] — per-fidelity normalization, val_frac=0.1, FNO > Transolver.
- [[paper-baselines-proposals]] — human-side TODO to commit IFC paper numbers.
