# Failure_Analyst Agent Output

- **timestamp:** 2026-06-02T21:03:27Z
- **exit_code:** 0

---

Wrote the analysis file. Here's the stdout summary for the CEO review.

---

# Failure Analysis — Cycle 010 Baseline (summary)

## Summary
- **Composite_nRMSE = 0.022161** (geomean: ifc_heat 0.012884 × ifc_poisson 0.038120). Identical reproduction of cycle-009-h1h2; all 14 cells cache-hit.
- **Both published composite bars already beaten**: ratio vs IFC-ODE2 geomean (0.0516) = 0.43×; ratio vs IFC-GPODE geomean (0.0331) = 0.67×.
- **Dominant failure mode**: `POISSON_STRUCTURAL_GAP_PER_FAMILY_ASYMMETRY` — heat winner `fno_coregionalization` (0.0129, 5.7× under IFC-ODE2) catastrophically fails on Poisson (0.598, 16.6× over); Poisson winner `fno_mf_stack` (0.0381, 1.06× over IFC-ODE2) is the only family within bar range on Poisson. No single family wins both datasets.

## Failure Distribution (where the residual gap lives)
- **Per-dataset gap to IFC-GPODE bar**: ifc_poisson 2.12× *over* GPODE — **100% of remaining published-bar gap is on Poisson**. ifc_heat is 4.7× *under* GPODE — zero remaining gap.
- **Per family on Poisson**: fno_mf_stack 0.038 (load-bearing) → fno_coreg_residual 0.072 → mf_fno_transfer_bar 0.083 → fno_coregionalization 0.598 (1469% over best). transolver/v9 families ≥10× over best on Poisson — out-of-frame.
- **By mechanism**: ~50% K-basis B(m)=MLP([m,m²]) inadequate for non-uniform fidelity ladders (Poisson scalers span 42×, heat span 1×); ~30% MFRNP aggregator is Poisson-specialized; ~20% HF-only plain FNO architectures un-bridged on Poisson.

## Composite Sensitivity
- d(composite)/d(heat) = 0.86, d(composite)/d(poisson) = 0.29 (heat ~3× more sensitive per unit absolute).
- BUT relative room favors Poisson: closing Poisson best → IFC-GPODE 0.018 yields **−31% composite**; closing → IFC-ODE2 0.036 yields only −2.8%.
- **Load-bearing cell**: `fno_mf_stack × ifc_poisson` (0.038120). No challenger within 1.9×. All composite movement this cycle hinges on this cell.

## Cross-Cycle Trajectory (007 → 010)
| Cycle | composite | best heat | best poisson |
|---|---|---|---|
| 007 baseline | 0.03958 | 0.0263 | 0.0596 |
| 008 baseline | 0.03041 | 0.0155 | 0.0596 |
| 009 baseline | 0.02773 | 0.0129 | ~0.060 |
| **009-h1h2** | **0.02216** | 0.0129 | **0.0381** |
| 010 baseline | 0.02216 | 0.0129 | 0.0381 |

## Recommended Interventions (ranked)
1. **Push fno_mf_stack capacity** — `models/fno_mf_stack/smoke_eval.py` SMOKE_DEFAULTS: hidden 64→96, modes_per_level (4,8,16,20)→(4,8,16,24) or (4,8,20,28), n_blocks 4→5. Highest-prior composite mover. NK-clear. Mandatory kill-switches: Poisson > 0.0594, wall > 1500s.
2. **Two-stage frozen-LF curriculum on fno_mf_stack** — `models/fno_mf_stack/smoke_eval.py` + `model.py`. NK2 carve-out applies (LF/HF-independent design). **MANDATORY dual kill-switches**: absolute (Poisson > 0.0594, heat > 0.0594) AND inter-stage (stage-2 best_val must reduce stage-1 best_val by ≥10%).
3. **fno_coregionalization Poisson-specific K-basis revision** — `models/fno_coregionalization/model.py`. Replace B(m)=MLP([m,m²]) with B(m, LF_features) on Poisson. Distinct from NK3 (NK3 = loss-weight transfer; this = basis parametrization). Heat-regression guard at 0.0194.
4. **Restore/rewrite fno_coreg_conditioned with γ(m, LF_features)** — `models/fno_coreg_conditioned/` (currently empty except `__pycache__`). NK1-safe (includes LF pathway). Speculative, last priority.
5. (Deferred — **NK3-blocked**): MFRNP-Poisson recipe transfer to fno_coreg_residual. Do not pursue.
6. (Deferred): transolver_residual revamp, MF-DeepONet — high-cost low-prior; later cycles.

## Anti-Patterns in Force (NKs)
- **NK1** — pure m-conditioning on HF-only FNO without LF→HF pathway.
- **NK2** — frozen-LF curricula on co-evolved residual ladders (fno_coregionalization, fno_coreg_residual). Permitted on LF/HF-independent designs (fno_mf_stack, mf_fno_transfer_bar) only with mandatory dual kill-switches.
- **NK3** — MFRNP-style loss-weight transfer to coregionalization family (3/3 failures).

Full per-instance detail in `.factory/research/runs/cycle-010-baseline/failure_analysis.md`.
