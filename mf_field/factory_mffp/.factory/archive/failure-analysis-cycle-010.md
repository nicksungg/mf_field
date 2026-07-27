---
name: failure-analysis-cycle-010
description: Cycle-010 baseline Failure Analyst output (CEO=PROCEED). Composite_nRMSE 0.022161 reproduces cycle-009 H1+H2 exactly (all 14 cells cache-hit on commit 0b6e6eb). Both published composite bars already beaten — parallel-bench by 19.2%, IFC-ODE2 by 57%, IFC-GPODE by 33%. Dominant residual failure mode = POISSON_STRUCTURAL_GAP_PER_FAMILY_ASYMMETRY (heat winner fno_coregionalization 0.0129 is Poisson-catastrophic at 0.598 = 16.6× over paper; Poisson winner fno_mf_stack 0.0381 is heat-suboptimal at rank-4; no single family wins both). Load-bearing cell = fno_mf_stack × ifc_poisson 0.038120 (no challenger within 1.89×; closing this single cell to IFC-GPODE 0.018 unlocks −31% composite). 100% of remaining per-dataset published-bar gap lives on Poisson (heat already 4.7× under GPODE). Mechanism breakdown: ~50% K-basis B(m)=MLP([m,m²]) inadequate for non-uniform fidelity ladders (Poisson scalers span 42×, heat span 1×) — observed via fno_coregionalization × poisson val→test collapse (11×); ~30% MFRNP aggregator path Poisson-specialized; ~20% HF-only plain FNO un-bridged on Poisson. Trajectory 007→010 = 0.0396 → 0.0304 → 0.0277 → 0.0222 → 0.0222 (monotonic descent, cycle-010 plateaued at cycle-009 H1+H2 result). Recommended interventions ranked: (1) push fno_mf_stack capacity further (hidden 64→96, modes (4,8,16,20)→(4,8,16,24)/(4,8,20,28), n_blocks 4→5) — load-bearing-cell direct attack, NK-clear; (2) two-stage frozen-LF curriculum on fno_mf_stack — NK2 carve-out applies (LF/HF-independent design) with MANDATORY dual kill-switches (absolute + inter-stage); (3) fno_coregionalization Poisson-specific K-basis revision B(m, LF_features) — distinct from NK3 (basis parametrization vs loss-weighting); (4) restore/rewrite fno_coreg_conditioned with γ(m, LF_features) — NK1-safe speculative. NKs in force: NK1 pure m-conditioning HF-only, NK2 frozen-LF on residual ladders, NK3 MFRNP loss-weight transfer to coregionalization family (3/3). Three new failure-taxonomy entries introduced: POISSON_STRUCTURAL_GAP_PER_FAMILY_ASYMMETRY, K_BASIS_NON_UNIFORM_FIDELITY_LADDER_COLLAPSE, MFRNP_AGGREGATOR_POISSON_SPECIALIZATION. CEO Researcher search keys = 2024-2026 FNO capacity-axis on Poisson-class PDEs; multi-fidelity stacking architectures with LF input concatenation; FiLM-with-LF-features γ(m, LF_features) conditioning; PyTorch recipe-hash / checkpoint-contract patterns.
metadata:
  type: project
tags:
  - factory
  - failure-analysis
  - factory_mffp
  - cycle-010
  - baseline
  - poisson-structural-gap-per-family-asymmetry
  - k-basis-non-uniform-fidelity-ladder-collapse
  - mfrnp-aggregator-poisson-specialization
  - load-bearing-cell-fno_mf_stack-poisson
  - bars-already-beaten
  - parallel-bench-dethroned
  - ifc-ode2-dethroned
  - ifc-gpode-composite-dethroned
project: factory_mffp
cycle: cycle-010
phase: baseline_failure_analysis_complete
ceo_verdict_on_failure_analyst: PROCEED
date: 2026-06-02
source: factory-archivist
analyzed_branch: experiment/14-fno_mf_stack-capacity-and-recipe-hash
analyzed_commit: 0b6e6eb
composite_nRMSE: 0.022161
composite_reproduced_from_cycle_009_h1h2: true
all_cells_cache_hit: true
n_cells: 14
n_models: 7
n_datasets: 2
heat_best_value: 0.012884
heat_best_family: fno_coregionalization
heat_best_paper_ifc_ode2_ratio: 0.17
heat_best_paper_ifc_gpode_ratio: 0.21
poisson_best_value: 0.038120
poisson_best_family: fno_mf_stack
poisson_best_paper_ifc_ode2_ratio: 1.06
poisson_best_paper_ifc_gpode_ratio: 2.12
poisson_best_margin_over_rank_2: 1.89
poisson_rank_2_family: fno_coreg_residual
poisson_rank_2_value: 0.072000
bar_parallel_bench: 0.027429
bar_parallel_bench_ratio: 0.808
bar_parallel_bench_dethroned: true
bar_parallel_bench_under_pct: 19.2
bar_ifc_ode2_geomean: 0.0516
bar_ifc_ode2_geomean_ratio: 0.43
bar_ifc_ode2_geomean_dethroned: true
bar_ifc_gpode_geomean: 0.0331
bar_ifc_gpode_geomean_ratio: 0.67
bar_ifc_gpode_geomean_dethroned: true
remaining_target_bar: ifc_gpode_per_dataset
remaining_target_poisson_bar: 0.018
remaining_target_heat_bar: 0.061
remaining_target_heat_already_under: true
remaining_pct_of_gap_on_poisson: 100
remaining_pct_of_gap_on_heat: 0
dominant_failure_mode: POISSON_STRUCTURAL_GAP_PER_FAMILY_ASYMMETRY
secondary_failure_mode: K_BASIS_NON_UNIFORM_FIDELITY_LADDER_COLLAPSE
tertiary_failure_mode: MFRNP_AGGREGATOR_POISSON_SPECIALIZATION
load_bearing_cell: "fno_mf_stack × ifc_poisson"
load_bearing_cell_value: 0.038120
load_bearing_cell_no_challenger_within: 1.89
secondary_lever_cell: "fno_coregionalization × ifc_heat"
secondary_lever_cell_value: 0.012884
secondary_lever_cell_no_challenger_within: 2.04
mechanism_breakdown_k_basis_inadequate_pct: 50
mechanism_breakdown_mfrnp_aggregator_poisson_pct: 30
mechanism_breakdown_hf_only_un_bridged_pct: 20
fno_coreg_poisson_val_test_inflation: 11.07
v9_baseline_poisson_val_test_inflation: 13.5
fno_coreg_per_fid_scaler_heat: "[1, 1, 1, 1]"
fno_coreg_per_fid_scaler_poisson: "[0.077, 0.024, 0.0069, 0.0018]"
fno_coreg_per_fid_scaler_dynamic_range: 42
local_sensitivity_d_composite_d_heat: 0.86
local_sensitivity_d_composite_d_poisson: 0.29
counterfactual_poisson_to_ode2_composite: 0.021536
counterfactual_poisson_to_ode2_delta_pct: -2.8
counterfactual_poisson_to_gpode_composite: 0.015228
counterfactual_poisson_to_gpode_delta_pct: -31.3
counterfactual_heat_to_005_composite: 0.013806
counterfactual_heat_to_005_delta_pct: -37.7
trajectory_007_baseline: 0.039578
trajectory_008_baseline: 0.030408
trajectory_009_baseline: 0.027729
trajectory_009_h1h2: 0.022161
trajectory_010_baseline: 0.022161
trajectory_pattern: monotonic_descent_plateau_at_cycle_009_h1h2
intervention_1_target_family: fno_mf_stack
intervention_1_target_files: ["models/fno_mf_stack/smoke_eval.py", "models/fno_mf_stack/full_config.json"]
intervention_1_axis: capacity_bump
intervention_1_nk_status: clear
intervention_1_expected_composite_delta_pct: "-3 to -6"
intervention_2_target_family: fno_mf_stack
intervention_2_axis: two_stage_frozen_lf_curriculum
intervention_2_nk_carve_out: "NK2 — LF/HF-independent design (fno_mf_stack is per-fidelity stacked, not co-evolved residual ladder)"
intervention_2_dual_kill_switch_required: true
intervention_3_target_family: fno_coregionalization
intervention_3_axis: k_basis_with_lf_features
intervention_3_nk_distinction: "Not NK3 — NK3 = loss-weight transfer; this = basis parametrization"
intervention_4_target_family: fno_coreg_conditioned
intervention_4_axis: film_gamma_m_lf_features
intervention_4_nk_safe: "NK1-safe via LF pathway inclusion"
intervention_5_deferred_reason: nk3_blocked_mfrnp_loss_weight_transfer_to_coregionalization
intervention_6_deferred_reason: high_cost_low_prior
nk1_in_force: true
nk2_in_force: true
nk3_in_force: true
new_failure_taxonomy_entries:
  - POISSON_STRUCTURAL_GAP_PER_FAMILY_ASYMMETRY
  - K_BASIS_NON_UNIFORM_FIDELITY_LADDER_COLLAPSE
  - VAL_TO_TEST_INFLATION
  - MFRNP_AGGREGATOR_POISSON_SPECIALIZATION
analyst_doc: .factory/research/runs/cycle-010-baseline/failure_analysis.md
analyst_summary_doc: .factory/reviews/failure_analyst-latest.md
ceo_verdict_doc: .factory/reviews/ceo-verdict-failure_analyst.md
---

# Cycle-010 Baseline Failure Analysis (PROCEED 2026-06-02)

## Headline

- **Composite_nRMSE = 0.022161** — geomean(ifc_heat 0.012884 × ifc_poisson 0.038120). **Identical reproduction** of cycle-009 H1+H2: all 14 model×dataset cells `_cache: "hit"` on `experiment/14-fno_mf_stack-capacity-and-recipe-hash @ 0b6e6eb`. Zero drift.
- **Three published composite bars already beaten:** parallel-bench `mf_fno_transfer @ 0.027429` (−19.2%), IFC-ODE2 geomean 0.0516 (−57%), IFC-GPODE geomean 0.0331 (−33%).
- **Remaining frontier = per-dataset IFC-GPODE bars** (heat 0.061, poisson 0.018). **100% of remaining published-bar gap lives on Poisson** — heat is already 4.7× *under* GPODE; Poisson sits 2.12× *over* GPODE.

## Dominant residual failure mode — `POISSON_STRUCTURAL_GAP_PER_FAMILY_ASYMMETRY`

No single family is best on both datasets and the heat-winner is Poisson-catastrophic:

| Cell | Value | vs IFC-ODE2 | vs IFC-GPODE | Note |
|---|---|---|---|---|
| `fno_coregionalization × ifc_heat` | 0.012884 | 0.17× | 0.21× | Heat winner; secondary lever (no challenger within 2.04×) |
| `fno_coregionalization × ifc_poisson` | 0.597799 | **16.61×** | 33.21× | **Heat-winner is Poisson-catastrophic** |
| `fno_mf_stack × ifc_poisson` | 0.038120 | 1.06× | 2.12× | **Poisson winner; load-bearing cell (no challenger within 1.89×)** |
| `fno_mf_stack × ifc_heat` | 0.038269 | 0.52× | 0.63× | Poisson-winner heat-suboptimal (4th, behind 0.012884 / 0.026273 / 0.033175) |

## Load-bearing-cell analysis

Sensitivities at the current operating point: d(composite)/d(heat) = 0.86, d(composite)/d(poisson) = 0.29 — heat has 3× more per-unit-absolute sensitivity, **but relative room favors Poisson**:

| Counterfactual move | New composite | Δ |
|---|---|---|
| Poisson → 0.036 (IFC-ODE2) | 0.021536 | **−2.8%** |
| Poisson → 0.018 (IFC-GPODE) | 0.015228 | **−31.3%** |
| Heat → 0.005 (IFC-ODE2 well-tuned) | 0.013806 | **−37.7%** |

**Single load-bearing cell:** `fno_mf_stack × ifc_poisson = 0.038120`. Closing it to IFC-GPODE 0.018 unlocks −31% composite. Rank-2 `fno_coreg_residual × poisson` is 1.89× away (0.072) — no slack from rebalancing within the family.

## Mechanism breakdown (per-cell evidence cited in analyst doc)

- **~50%** — K-basis B(m)=MLP([m,m²]) inadequate for non-uniform fidelity-magnitude ladders. Per-fidelity output scaler spans **42×** on Poisson ([0.077, 0.024, 0.0069, 0.0018]) vs **1×** on heat ([1, 1, 1, 1]). `fno_coregionalization × poisson` exhibits an 11× val→test collapse on the same architecture+curriculum that generalizes perfectly on heat.
- **~30%** — MFRNP aggregator path is Poisson-specialized. `fno_mf_stack` heat (0.0383) ≈ poisson (0.0381) — the aggregator equalizes dissimilar PDEs, suggesting it *is* the Poisson-scaling mechanism but sub-optimal on heat (where `fno_coregionalization` sits at 0.013).
- **~20%** — HF-only plain FNO architectures don't bridge to Poisson (`v9_baseline × poisson` 18.5, `transolver_residual × poisson` 2.6). Out-of-frame for composite movement.

## Cross-cycle trajectory (007 → 010)

| Cycle | composite | best heat | best poisson | event |
|---|---|---|---|---|
| 007 baseline | 0.039578 | 0.026277 (fno_coreg_residual) | 0.059611 (fno_mf_stack) | fno_coregionalization crashed (constructor bug) |
| 008 baseline | 0.030408 | 0.015511 (fno_coregionalization) | 0.059611 | constructor fix landed |
| 009 baseline | 0.027729 | 0.012884 (fno_coregionalization) | ~0.060 | fno_coregionalization paper-config capacity bump (cycle-008 H1) |
| **009-h1h2** | **0.022161** | 0.012884 | **0.038120** (fno_mf_stack) | fno_mf_stack capacity bump + recipe_hash, −20.08% |
| 010 baseline | 0.022161 | 0.012884 | 0.038120 | identical reproduction; all 14 cells cache-hit |

Monotonic descent for 4 cycles. Cycle-010 baseline = `experiment/14 @ 0b6e6eb` is the entry state for any cycle-010 hypothesis.

## Recommended interventions (ranked)

1. **Push `fno_mf_stack` capacity further (Poisson lever)** — `models/fno_mf_stack/smoke_eval.py` SMOKE_DEFAULTS. Sweep ladder: `modes_per_level (4,8,16,20) → (4,8,16,24) → (4,8,20,28)`; `hidden 64→96`; `n_blocks 4→5`. **NK-clear (in-family capacity).** Builder predicted floor 0.05–0.06; actual cycle-009 H1 floor 0.0381 was 36% better — capacity ladder may have additional headroom. **MANDATORY kill-switches:** Poisson > 0.0594 (cycle-008 baseline level); wall > 1500s. Expected impact: −10 to −20% Poisson → −3 to −6% composite (load-bearing-cell direct attack).
2. **Two-stage frozen-LF curriculum on `fno_mf_stack`** — `models/fno_mf_stack/smoke_eval.py` + `model.py`. **NK2 carve-out applies** — `fno_mf_stack` is per-fidelity stacked with MFRNP aggregator joining only at the output (LF/HF *independent by design*), NOT a co-evolved residual ladder. Apply cycle-008 H2 LF→HF schedule (50 LF-only / 150 joint, cosine restart). **MANDATORY dual kill-switches:** absolute (Poisson > 0.0594 AND heat > 0.0594) AND inter-stage (stage-2 best_val must reduce stage-1 best_val by ≥10%). Wall budget 1800s.
3. **`fno_coregionalization` Poisson-specific K-basis revision** — `models/fno_coregionalization/model.py`. Replace `B(m)=MLP([m, m²])` on Poisson with `B(m, LF_features)`. **NK-distance:** not NK3 (NK3 closed loss-weight transfer; this is basis parametrization — distinct mechanism, untouched axis). Heat-regression guard at 0.0194. Speculative — would not improve composite unless basis collapse below 0.038, but would create a second Poisson contender.
4. **Restore/rewrite `fno_coreg_conditioned` with `γ(m, LF_features)`** — `models/fno_coreg_conditioned/` (currently empty except `__pycache__`). NK1-safe via LF pathway inclusion. Lowest priority — substantial implementation surface (`model.py` + `smoke_eval.py` + `manifest.json` + `data.py`).
5. **Deferred — NK3-blocked:** MFRNP-Poisson recipe transfer to `fno_coreg_residual`. Do not pursue (3/3 failures).
6. **Deferred — high-cost low-prior:** transolver_residual revamp, MF-DeepONet.

## Anti-patterns in force (NKs)

- **NK1** (cycle-008 H2): pure m-conditioning on HF-only FNO without LF→HF pathway. Closed.
- **NK2** (cycle-008 H3): frozen-LF curricula on co-evolved residual ladders (`fno_coregionalization`, `fno_coreg_residual`). Permitted on LF/HF-independent designs (`fno_mf_stack`, `mf_fno_transfer_bar`) **only with mandatory dual kill-switches**.
- **NK3** (cycles 003/006/007): MFRNP-style loss-weight transfer to coregionalization family. 3/3 failures. Closed.

## Failure taxonomy additions (cycle-010)

- `POISSON_STRUCTURAL_GAP_PER_FAMILY_ASYMMETRY` — dominant. Different families win different datasets; heat-winner is Poisson-broken and vice-versa.
- `K_BASIS_NON_UNIFORM_FIDELITY_LADDER_COLLAPSE` — `B(m)=MLP([m,m²])` generalizes on uniform fidelity scalers but collapses 11× on non-uniform (42× dynamic range) ladders.
- `VAL_TO_TEST_INFLATION` — cross-cell category for val/test ratio > 5× (fno_coregionalization × poisson 11×, v9_baseline × poisson 13.5×, transolver_residual × poisson 5.2×). Flag for future generalization-gap analyses.
- `MFRNP_AGGREGATOR_POISSON_SPECIALIZATION` — fno_mf_stack heat/poisson equalized at ~0.038; aggregator is Poisson-shaped, sub-optimal on heat.

## CEO instructions for Researcher R1.5 (downstream)

Search keys (citation: [[ceo-verdict-failure_analyst]] — also recorded under cycle-009's R1.5 guidance):

- 2024–2026 FNO capacity-axis on Poisson-class PDEs (modes scaling, channel width, n_blocks vs Poisson nRMSE).
- 2024–2026 multi-fidelity stacking architectures (LF predictions concatenated/added to HF FNO inputs — the `fno_mf_stack` pattern).
- 2024–2026 FiLM-with-LF-features `γ(m, LF_features)` conditioning for multi-fidelity field prediction.
- 2024–2026 portable training utility patterns (recipe-hash, checkpoint contracts) in PyTorch reproducibility / MLOps literature.

Search keywords: "Poisson equation FNO multi-fidelity", "Lyu 2023 MFFNO modes ablation", "FNO modes cap channel width Poisson".

## Links

- Analyst full doc: [.factory/research/runs/cycle-010-baseline/failure_analysis.md](../research/runs/cycle-010-baseline/failure_analysis.md)
- Analyst summary: [.factory/reviews/failure_analyst-latest.md](../reviews/failure_analyst-latest.md)
- CEO verdict: [.factory/reviews/ceo-verdict-failure_analyst.md](../reviews/ceo-verdict-failure_analyst.md)
- Cycle-009 close-out (entry baseline): [[factory_mffp-014-outcome]]
- Cycle-009 strategy snapshot: [[strategies/cycle-009-strategy]]
- Patterns: [[patterns/patterns]]
