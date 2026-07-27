---
name: failure-analysis-cycle-009
description: Cycle-009 baseline Failure Analyst report. Baseline composite_nRMSE 0.027729 is REPRODUCIBLE on `experiment/11-fno_coregionalization-paper-capacity @ 18d83a6` (banked from cycle-008 H1 paper-config capacity bump). Bar (mf_fno_transfer_bar parallel-bench) = 0.027429; remaining gap = +0.000300 abs (+1.09% over bar). **DOMINANT-LEVER REVERSAL (cycle-008 → cycle-009):** Heat collapsed from +21% over bar to +0.7% over bar (cycle-008 H1 capacity-axis closed the heat side); Poisson now contributes ~69% of the remaining composite gap (was ~1.2% at cycle-008 entry); per-cell `fno_mf_stack × ifc_poisson` (0.05961, +1.5% over bar) is the SOLE dominant gap contributor. Cycle-009 attack budget MUST flow to the Poisson side; heat capacity-axis on `fno_coregionalization` is exhausted at paper config. Five prioritized intervention axes named with CEO priority signal — O1 LEAD (`fno_mf_stack` capacity bump on Poisson, mirrors c008 H1 playbook, sidesteps NK1/2/3, attacks the 69% gap contributor with LOW risk); O2 SECONDARY (`recipe_hash` portable utility cherry-pick from c008 H3, operational meta-fix, closes cycle-003 backlog project-wide); O3 DEFERRED (two-stage frozen-LF curriculum on `fno_mf_stack` — NK2 by-design carve-out applies; medium-EV); O4 SPECULATIVE RESERVE (`fno_coreg_conditioned` revision with `γ(m, LF_features)` — high-risk NK1 retry); O5 REJECTED for c009 (K-basis redesign on `fno_coregionalization × poisson` — too easy to disturb the c008 H1 banked Heat win). Three negative-knowledge forbidden zones enumerated and pinned (NK1 = pure m-conditioning on HF-only FNO from c008 H2; NK2 = frozen-LF curricula on co-evolved residual ladders from c008 H3; NK3 = MFRNP-style loss-weight tuning on coregionalization-family from c003/c006/c007 — 3/3 REVERT history). Cycle-009 design space is narrower than cycle-008's but better-instrumented.
metadata:
  type: project
tags:
  - factory
  - failure-analysis
  - factory_mffp
  - cycle-009
  - baseline
  - reproducible-best
  - dominant-lever-reversal-heat-to-poisson
  - near-bar-poisson-side
  - capacity-axis-exhausted-on-fno-coregionalization
  - nk1-pure-m-conditioning-forbidden
  - nk2-frozen-lf-on-residual-ladder-forbidden
  - nk3-mfrnp-loss-weight-coreg-family-forbidden
  - o1-fno-mf-stack-capacity-bump-poisson-lead
  - o2-recipe-hash-portable-utility-secondary
project: factory_mffp
cycle: cycle-009
phase: failure-analysis
round: baseline
date: 2026-06-02
source: factory-archivist
ceo_verdict: PROCEED
baseline_composite: 0.027729
baseline_commit: 18d83a6
baseline_branch: experiment/11-fno_coregionalization-paper-capacity
bar_composite: 0.027429
bar_heat: 0.01281
bar_poisson: 0.05871
paper_bar_heat: 0.074
paper_bar_poisson: 0.036
gap_to_bar_abs: 0.000300
gap_to_bar_pct: 1.09
gap_to_bar_pct_closed_by_cycle_008_h1: 89.93
heat_gap_share_pct: 31.1
poisson_gap_share_pct: 68.9
gap_share_prior_cycle_008_baseline_heat_pct: 95.0
gap_share_prior_cycle_008_baseline_poisson_pct: 5.0
heat_vs_poisson_log_weight_ratio_cycle_008: 12.6
poisson_vs_heat_log_weight_ratio_cycle_009: 2.2
dominant_lever_reversal_event: true
dominant_failure_mode: NEAR_BAR
dominant_failure_cell: "fno_mf_stack x ifc_poisson"
dominant_failure_cell_nrmse: 0.05961
dominant_failure_cell_pct_over_bar: 1.5
counterfactual_close_poisson_to_bar_composite: 0.02752
counterfactual_close_poisson_to_bar_pct_of_gap_closed: 69.7
counterfactual_close_heat_to_bar_composite: 0.02763
counterfactual_close_heat_to_bar_pct_of_gap_closed: 31.0
ifc_heat_best_family: fno_coregionalization
ifc_heat_best_value: 0.012898
ifc_heat_best_margin_over_rank_2_multiple: 2.04
ifc_poisson_best_family: fno_mf_stack
ifc_poisson_best_value: 0.05961
ifc_poisson_best_margin_over_rank_2_multiple: 1.24
heat_at_paper_bar: true
heat_paper_bar_multiple_under: 5.7
intervention_axis_count: 5
intervention_axis_lead: "O1 fno_mf_stack capacity bump on Poisson"
intervention_axis_secondary: "O2 recipe_hash portable utility cherry-pick"
intervention_axis_deferred: ["O3 two-stage frozen-LF on fno_mf_stack"]
intervention_axis_speculative_reserve: ["O4 fno_coreg_conditioned with gamma(m, LF_features)"]
intervention_axis_rejected_for_cycle_009: ["O5 K-basis redesign on fno_coregionalization × poisson"]
nk_zones_count: 3
nk1_label: "pure m-conditioning on HF-only FNO (c008 H2)"
nk2_label: "frozen-LF curricula on co-evolved residual ladders (c008 H3)"
nk3_label: "MFRNP-style loss-weight tuning on coregionalization family (c003/c006/c007 3/3 REVERT)"
new_negative_knowledge_zones_this_cycle: 2
prior_negative_knowledge_zones_reinforced: 1
operational_hygiene_item_count: 5
operator_action_precheck_overhaul_consecutive_cycles: 6
operator_action_status: out_of_cycle_scope
preserved_reference_branches: ["experiment/11 @ 18d83a6 (banked best / c009 entry)", "experiment/12 @ 540e684 (FiLM scaffolding for O4 revisit)", "experiment/13 @ 420a51c (recipe_hash pattern for O2 cherry-pick)"]
mfrnp_recipe_revert_count: 3
mfrnp_recipe_revert_cycles: ["cycle-003-H1", "cycle-006-H1", "cycle-007-H2"]
---

# Failure Analysis — Cycle 009 baseline (factory_mffp)

## Cycle Setup

- **Branch under test:** `experiment/11-fno_coregionalization-paper-capacity @ 18d83a6` (banked from cycle-008 H1 paper-config capacity bump).
- **Baseline composite_nRMSE:** **0.027729** (geomean of best per-dataset: `ifc_heat` 0.012898 via `fno_coregionalization`, `ifc_poisson` 0.05961 via `fno_mf_stack`).
- **Eval origin:** UNCHANGED by cycle-008 H2 / H3 (both genuine REVERTs absorbed without metric impact). H1 was a clean composite-improving KEEP intent that delivered −8.81% composite and closed 89.93% of the parallel-bench bar gap on the heat side alone.
- **CEO verdict:** PROCEED. See `.factory/reviews/ceo-verdict-failure_analyst.md`.
- **Full analysis source:** `.factory/research/runs/cycle-009-baseline/failure_analysis.md`.

## Headline numbers

| Reference point                                  | composite_nRMSE | ifc_heat                          | ifc_poisson                |
|---                                               |---:             |---                                |---                         |
| **R0 cycle-009 baseline (reproducible)**         | **0.027729**    | **0.012898** `fno_coregionalization` | 0.05961 `fno_mf_stack`     |
| Cycle-008 entry (cycle-007 H1)                   | 0.030408        | 0.01551 `fno_coregionalization`   | 0.05961 `fno_mf_stack`     |
| Cycle-008 H1 banked (== c009 entry)              | 0.027729        | 0.012898 `fno_coregionalization`  | 0.05961 `fno_mf_stack`     |
| Bar (`mf_fno_transfer_bar` parallel-bench)       | 0.027429        | 0.01281                            | 0.05871                    |
| Paper bar (`baselines/paper_baselines.json`)     | —               | 0.074                              | 0.036                      |

- **Gap to bar:** +0.000300 composite (+1.09% over bar). **89.93% of the cycle-008 entry gap closed** by cycle-008 H1 capacity-axis on the heat side alone.
- **Heat is essentially AT bar (+0.7% over) AND well past paper bar (5.7× under).** Bar dethrone is now a Poisson problem.

## DOMINANT-LEVER REVERSAL (cycle-008 baseline → cycle-009 baseline)

This is the **#1 headline of cycle-009**: the dominant composite-gap contributor INVERTED between dataset axes.

| Cycle baseline | Heat share of composite gap | Poisson share of composite gap | Dominant lever |
|---             |---:                         |---:                            |---             |
| **cycle-008 baseline** | ~95% (log-weight +0.191) | ~5% (log-weight +0.015) | **Heat** (12.6× larger log-weight than Poisson) |
| **cycle-009 baseline** | **31.1%** (log-weight +0.00685) | **68.9%** (log-weight +0.01521) | **Poisson** (2.2× larger log-weight than Heat) |

- **What flipped:** cycle-008 H1's capacity-axis bump on `fno_coregionalization` moved heat from 0.01551 (+21% over bar) to **0.012898** (+0.7% over bar; AT_PAPER_BAR + NEAR_BAR). The heat capacity lever is now exhausted on this family at paper config.
- **What inherits the gap:** `fno_mf_stack × ifc_poisson` at 0.05961 (+1.5% over bar) — the same nRMSE it held at cycle-008 entry, but now the SOLE dominant composite-gap contributor because heat collapsed below it.
- **Counterfactual math (closing one dataset alone):**
  - **Close Poisson to bar (0.05961 → 0.05871):** composite → 0.02752 (closes **69.7%** of the +0.000300 gap).
  - **Close Heat to bar (0.012898 → 0.01281):** composite → 0.02763 (closes 31.0% of the +0.000300 gap).
- **Strategic implication:** the cycle-008 close-out flagged this; cycle-009 confirms it. **Attack budget MUST flow to the Poisson side.**

## Five Prioritized Intervention Axes (CEO PROCEED-affirmed priority signal)

Open architectural axes consistent with `mutable_surfaces=models/**` and sidestepping all three forbidden zones (see §Negative-Knowledge Zones below).

### Priority 1 — O1: `fno_mf_stack` capacity bump on Poisson (CYCLE-009 LEAD, HIGHEST EV)

- **Target cell:** `fno_mf_stack × ifc_poisson` (NEAR_BAR; owns ~69% of the +1.09% composite gap).
- **Mutable surfaces:** `models/fno_mf_stack/smoke_eval.py` SMOKE_DEFAULTS (lines ~37–53); possibly `models/fno_mf_stack/model.py` if modes_per_level shape forces constructor updates; possibly `models/fno_mf_stack/full_config.json` for the full-resolution mirror.
- **Suggested levers (Builder to decide exact values):** hidden 32→64; modes_per_level `(4,8,12,12)` → `(8,16,16,16)` or `(8,16,20,20)`; n_blocks 3→4. **Audit constructor anisotropic-modes handling per cycle-007 H1 pattern** (O2 from the analyst's enumeration folds in here — the constructor-class repair pattern that unlocked `fno_coregionalization` may still be latent on `fno_mf_stack`).
- **Expected qualitative composite impact:** **LARGE** — direct attack on the 69% gap contributor. Mirrors the cycle-008 H1 playbook (capacity bump on the bar-near family) which delivered −8.81% composite.
- **Risk:** **LOW** — direct capacity-axis analog. NK1/2/3 not engaged. Kill switches: poisson kill at >0.0594 (current baseline); wall <30 min.
- **NK sidesteps:** NK1 ✓ (no FiLM conditioning), NK2 ✓ (no curriculum / no freeze), NK3 ✓ (capacity not recipe; poisson loss weights already canonical-MFRNP — no perturbation).
- **CEO signal:** **HIGHEST-EV cycle-009 lead.**

### Priority 2 — O2: `recipe_hash` portable utility cherry-pick (SECONDARY, OPERATIONAL META-FIX)

- **Target cell(s):** None directly composite-moving — closes the cycle-003 H1 stage-resume contamination pathway **project-wide**.
- **Mutable surfaces:** NEW `models/_common/recipe_hash.py` (utility extracted from `models/fno_coreg_residual/smoke_eval.py` lines ~113–123 / 461–485, proven via cycle-008 H3); one-line import + `recipe_hash` arg in every family's `smoke_eval.py` (fno_coregionalization, fno_coreg_residual, fno_mf_stack, fno_coreg_conditioned, mf_fno_transfer_bar, transolver_residual, transolver_attention_fusion).
- **Expected qualitative composite impact:** **NONE directly; LARGE indirectly** — every subsequent cycle's checkpoint resume is silently corrupted-safe instead of silently corrupted. cycle-003 backlog item closes project-wide.
- **Risk:** **LOW** — proven pattern from cycle-008 H3 with live-tested stale-checkpoint rejection log line verified.
- **NK sidesteps:** all NKs (purely operational, no architecture / recipe / curriculum change). The three-stage curriculum gating logic from cycle-008 H3 is **NOT** to be cherry-picked.
- **CEO signal:** **Strong secondary. Acceptable as a parallel hypothesis.** Low-risk, sidesteps all NKs, closes cycle-003 backlog project-wide.

### Priority 3 — O3: Two-stage frozen-LF curriculum on `fno_mf_stack` (DEFERRED)

- **Target cell:** `fno_mf_stack × ifc_poisson` (NEAR_BAR) — alternative lever to O1's capacity scan, attacking the same cell.
- **Mutable surfaces:** `models/fno_mf_stack/smoke_eval.py` (add Stage-1 LF-pretrain → Stage-2 HF-residual frozen-LF schedule).
- **Expected qualitative composite impact:** **MEDIUM** — c007 H2-class two-stage schedule has prior precedent of moderate gains on the unrelated coregionalization family. CEO note: heat doesn't move because `fno_mf_stack × heat` is rank-3, not winner — medium-EV at best for the composite.
- **Risk:** **MEDIUM-LOW** — the NK2 argument explicitly carves out `fno_mf_stack` and `mf_fno_transfer_bar` as families where LF/HF are independent by design (per-fidelity stacked predictions, not co-evolved residuals). MUST specify BOTH (a) absolute Stage-k-vs-baseline kill (Stage-k poisson > 1.25× 0.05961 → REVERT) AND (b) inter-stage ratio kill — cycle-008 H3 design lesson.
- **NK sidesteps:** NK1 ✓, NK2 ✓ (by-design carve-out; reject any same-style proposal on `fno_coreg_residual`/`fno_coregionalization` at R2), NK3 ✓.
- **CEO signal:** **DEFER** — even with NK2-by-design carve-out, multi-stage on a 7.8× heat-underperformer is medium-EV at best.

### Priority 4 — O4: `fno_coreg_conditioned` revision with `γ(m, LF_features)` (SPECULATIVE RESERVE)

- **Target cell:** `fno_coregionalization × ifc_poisson` (FAMILY_PDE_SPECIALIZATION_ASYMMETRY); steals Poisson from `fno_mf_stack` if it works.
- **Mutable surfaces:** preserve `experiment/12 @ 540e684` 828 LOC FiLM scaffolding; revise `models/fno_coreg_conditioned/model.py` to compute FiLM `γ, β` from a broadcast LF-feature spatial channel instead of pure `[m, m²]`. Directly applies the cycle-008 H2 architectural lesson (NK1 sidestep), but kept-novel revision; ≥1 retry of a previously-falsified architecture class.
- **Expected qualitative composite impact:** **LARGE if it works** (single-family Heat+Poisson winner); **NONE if it doesn't** (would just be a 2nd-place family on heat).
- **Risk:** **MEDIUM-HIGH** — speculative redesign; full-cycle scaffold cost already paid in cycle-008 H2.
- **NK sidesteps:** NK1 ✓ (LF-feature pathway re-introduced), NK2 ✓ (no curriculum / no freeze), NK3 ✓ (FiLM affines, not loss weights).
- **CEO signal:** **KEEP ON RESERVE, NOT recommended for cycle-009 lead.** High-risk NK1 retry.

### Priority 5 — O5: K-basis redesign on `fno_coregionalization × poisson` (REJECTED for cycle-009)

- **Target cell:** `fno_coregionalization × ifc_poisson` (FAMILY_PDE_SPECIALIZATION_ASYMMETRY, persistent since c001 at ~0.6–0.75).
- **Mutable surfaces:** `models/fno_coregionalization/model.py` (B(m) basis MLP) + `models/fno_coregionalization/smoke_eval.py`.
- **Expected qualitative composite impact:** **MODEST-to-LARGE if successful** — would let same family own both datasets; current poisson 0.5945 → would need to drop ~10× to enter composite. Even a partial reduction does not enter composite while `fno_mf_stack` owns Poisson, so requires successful undercut of 0.05961.
- **Risk:** **HIGH** — speculative redesign of basis function; failure mode well-mapped (K=10/20 MLP-basis cannot fit non-monotone m-modulation). Not the cleanest lever.
- **NK sidesteps:** NK1 ✓ (if `B(m, LF)` formulation), NK2 ✓, NK3 ✓.
- **CEO signal:** **REJECT for cycle-009.** Speculative high-risk on a family already paper-bar-overshooting on Heat; too easy to disturb the H1 banked Heat win.

## Negative-Knowledge Zones (FORBIDDEN for cycle-009)

Three pinned forbidden zones — two NEW (NK1, NK2 from cycle-008 H2/H3) plus one REINFORCED (NK3 from cycles 003/006/007). Constrain the Strategist's R2 hard-gate.

### NK1 — Pure m-conditioning on HF-only FNO (cycle-008 H2)

> FiLM-via-LayerNorm with affines computed as `γ(m, m²)` — i.e., pure m-conditioning — on a single HF FNO **cannot synthesize the LF→HF correlation pathway** that `ifc_poisson` requires.

- **Evidence:** cycle-008 H2 (`fno_coreg_conditioned`, `experiment/12 @ 540e684`) — heat 0.017102 (competitive at rank #2; FiLM-on-HF-only viable when HF training data alone is sufficient) BUT poisson 0.749915 (12.6× over `fno_mf_stack`; catastrophically outside Builder's predicted 0.05–0.15 range). Composite +9.66% vs banked best. Kill switches CLEAR — silent under-performance, not blow-up.
- **Cycle-009 application:** any single-family Heat+Poisson candidate MUST either (a) re-introduce LF→HF pathway (residual ladder), OR (b) condition FiLM affines on LF features directly: `γ(m, LF_features)` instead of `γ(m, m²)`. **Reject pure m-conditioning at R2.**
- The 828 LOC FiLM scaffolding on `experiment/12 @ 540e684` is preserved — sidesteppable via revision (b), which is exactly O4 above.

### NK2 — Frozen-LF curricula on co-evolved residual ladders (cycle-008 H3)

> Three-stage (or any) curricula that freeze the LF stack mid-training (`requires_grad=False`) are **INCOMPATIBLE with co-evolved residual ladder designs** (`fno_coregionalization`, `fno_coreg_residual`). Stage-2 LF-freeze forces the HF residual to correct against an OOD frozen LF state from the LF-only pretrain regime, producing garbage.

- **Evidence:** cycle-008 H3 (`fno_coreg_residual` three-stage, `experiment/13 @ 420a51c`) — `fno_coreg_residual × heat` regressed 19× (0.026277 → 0.509105); universal `ifc_heat > 0.0194` kill-switch TRIPPED **26× over threshold**. `fno_coreg_residual × poisson` regressed 2.15× (0.074192 → 0.159364). H3-specific Stage3/Stage2 ratio kill-switch did NOT trip — damage occurred in Stages 1/2.
- **Cycle-009 application:** **DO NOT propose multi-stage frozen-LF curricula on `fno_coregionalization` or `fno_coreg_residual`.** End-to-end joint training (cycle-005 H2 continuous-LR-schedule pattern) is the correct recipe for co-evolved designs. Multi-stage MAY be appropriate for families with LF/HF **independent by design** (`mf_fno_transfer_bar`, `fno_mf_stack` — which carves out O3 above) — but ANY multi-stage proposal MUST specify BOTH absolute Stage-k-vs-baseline AND inter-stage ratio kill-switches.

### NK3 — MFRNP-style loss-weight transfer on coregionalization family (cycles 003/006/007, REINFORCED by c008 H3)

> Per-dataset MFRNP loss-weight tuning (HF=2.0, LF=0.25 and variants) on the coregionalization family produces heat-invariance violations even when the heat branch is claimed invariant by construction. Fresh-train variance + shared training infrastructure consistently break the invariance claim.

- **Evidence (3/3 REVERT history):** cycle-003 H1 (Poisson5 transplant `fno_mf_stack → fno_coreg_residual`: poisson +268% regression, heat unchanged — REVERT); cycle-006 H1 (reverse cross-architecture transplant `fno_coreg_residual → fno_mf_stack`: REVERT); cycle-007 H2 (within-family per-dataset dispatch on `fno_coreg_residual`: heat 0.02628 → 0.03487 +32.7% at 6.5× the noise band — falsified "invariant by construction" claim, REVERT).
- **Cycle-009 application:** any new MFRNP-style loss-weight reweighting hypothesis on `fno_coreg_residual` / `fno_coregionalization` MUST declare (i) a heat-invariance kill-switch with band derived from ≥3 prior fresh-train values, AND (ii) best-of-N (N≥2) seed control with frozen heat seed. **Practically: this axis is closed for cycle-009 on coregionalization-family.** Loss-weight tuning may still be valid on `fno_mf_stack` itself (where the recipe was born and is canonical), but only on poisson (heat uses uniform weights already).

## Operational Hygiene Items (NOT primary composite-moving hypotheses)

Items the Strategist may NOT generate as primary composite-moving hypotheses but should track:

1. **`recipe_hash` portable utility cherry-pick** (O2 above) — operational, unlocks future composite-moving experiments. Strategist framing: suggest as a non-hypothesis maintenance PR or as a quick-win hypothesis with explicit "operational-only, not composite-moving" framing. CEO classifies as **strong secondary**, acceptable as a parallel hypothesis.
2. **6th consecutive precheck overhaul backlog flag** — `score_direction` polarity (10-of-10 incl. cycle-008 H2 symmetric-flip silencing of regression), `scope`/`fixed_surfaces` empty-detail (4-of-4), leakage substring-collision (6-of-6). Out of factory scope; archive note + CEO intent are load-bearing institutional record. **Operator action standing.**
3. **Stale-cache risk on `fno_coreg_conditioned`** — cycle-008 H2 family's cache fell out by cycle-008 H3. If cycle-009 wants to re-test the H2 architecture (e.g., O4 above with `γ(m, LF_features)`), Builder must re-train from scratch and not assume cache hit. Wall budget +~92s per H2-family retrain.
4. **Researcher / failure_analyst wrapper timeout pattern** (5+ cycles) — CEO has been synthesizing substitutes from direct source reads. Standing operational practice; no change in cycle-009 R1 / R1.5 plans.
5. **`mf_fno_transfer_bar` smoke-eval undertraining (BAR_UNDERTRAINING_VS_CACHE)** — DEFER per cycle-008 baseline analysis; fixing would raise the parallel-bench bar and is counterproductive to cycle-009's dethrone objective.

## Per-Cell Classification (14 cells: 7 families × 2 datasets)

| Family | Dataset | nRMSE | × bar | Category |
|---|---|---:|---:|---|
| `fno_coregionalization` | heat | 0.012898 | 1.007× | **NEAR_BAR + AT_PAPER_BAR** (essentially AT bar; 5.7× under paper bar) |
| `fno_coregionalization` | poisson | 0.594477 | 10.13× | **FAMILY_PDE_SPECIALIZATION_ASYMMETRY** (persistent since c001) |
| `fno_coreg_residual` | heat | 0.026277 | 2.05× | CAPACITY_PARETO (banked via c007 K=20/b_hidden=128) |
| `fno_coreg_residual` | poisson | 0.074192 | 1.26× | CAPACITY_PARETO (recipe-tuning lever closed → NK3) |
| `mf_fno_transfer_bar` | heat (smoke) | 0.033175 | 2.59× | BAR_UNDERTRAINING_VS_CACHE (parallel-bench side IS 0.01281 bar) |
| `mf_fno_transfer_bar` | poisson (smoke) | 0.083326 | 1.42× | BAR_UNDERTRAINING_VS_CACHE (parallel-bench side IS 0.05871 bar) |
| `fno_mf_stack` | heat | 0.099945 | 7.80× | FAMILY_PDE_SPECIALIZATION_ASYMMETRY (heat uses uniform weights) |
| `fno_mf_stack` | poisson | 0.059611 | 1.015× | **NEAR_BAR (parallel-bench) — SOLE DOMINANT COMPOSITE-GAP CONTRIBUTOR (~69%)** |
| `transolver_attention_fusion` | heat | 0.149230 | 11.65× | ARCHITECTURE_OBSOLETE |
| `transolver_attention_fusion` | poisson | 0.381812 | 6.50× | ARCHITECTURE_OBSOLETE |
| `transolver_residual` | heat | 0.114559 | 8.94× | ARCHITECTURE_OBSOLETE |
| `transolver_residual` | poisson | 2.592349 | 44.16× | ARCHITECTURE_OBSOLETE |
| `v9_baseline` | heat | 0.148834 | 11.62× | ARCHITECTURE_OBSOLETE (gated softmax cannot encode value-scale shift) |
| `v9_baseline` | poisson | 18.503436 | 315× | ARCHITECTURE_OBSOLETE (known value-scale collapse) |

**Promotion this cycle:** `fno_mf_stack × poisson` from CAPACITY_PARETO (c008 baseline) → **NEAR_BAR** (c009 baseline; sole dominant gap contributor).
**Demotion this cycle:** `fno_coregionalization × heat` from CAPACITY_PARETO (c008 baseline @ 0.01551, +21% over bar) → **NEAR_BAR + AT_PAPER_BAR** (c009 baseline @ 0.012898, +0.7% over bar). The heat capacity-axis is exhausted on this family at paper config.

## Cross-Cycle Comparison (Cycle-008 → Cycle-009 baseline)

| Metric / cell | c008 baseline (c007 H1 entry) | c008 H1 (banked → c009 entry) | Delta | Trend |
|---|---:|---:|---:|---|
| composite_nRMSE | 0.030408 | **0.027729** | −8.81% | **improving** (new reproducible project best) |
| Bar gap (vs 0.027429) | +10.86% | **+1.09%** | −9.77 pp | **89.93% closed** by H1 capacity-axis alone |
| `fno_coregionalization × heat` | 0.01551 | **0.012898** | −16.84% | **improving** (paper-config capacity) |
| `fno_coregionalization × poisson` | 0.75015 | 0.594477 | −20.75% | improving but irrelevant to composite (rank #5) |
| `fno_coreg_residual × heat` | 0.026277 | 0.026277 | 0% | stable |
| `fno_coreg_residual × poisson` | 0.074192 | 0.074192 | 0% | stable; recipe-tuning lever closed |
| `fno_mf_stack × heat` | 0.099945 | 0.099945 | 0% | stable; family asymmetry persistent |
| `fno_mf_stack × poisson` | 0.059611 | 0.059611 | 0% | stable; **now the dominant composite-gap contributor (69%)** |

**Headline c008 → c009:**
- Reproducible best moved from 0.030408 → 0.027729 (−8.81%); 89.93% of parallel-bench bar gap closed by capacity-axis alone.
- Heat capacity-axis on `fno_coregionalization` is exhausted at paper config; NEW dominant lever is Poisson side.
- Two new NK zones (NK1, NK2) emerged from cycle-008 H2/H3 architecturally-falsified REVERTs.

## Closing Notes

The cycle-008 → cycle-009 transition closed a large composite delta (−8.81%) and a large fraction of the parallel-bench bar gap (89.93%) via a single architectural axis (capacity on `fno_coregionalization`), while **closing off two architectural axes** (NK1 pure m-conditioning on HF-only; NK2 frozen-LF curricula on co-evolved residual ladders) and **reinforcing one prior closure** (NK3 MFRNP loss-weight transfer on coregionalization-family).

The remaining +1.09% bar gap inherits a **NEW dominant lever**: Poisson contributes 69% of the residual gap (vs ~5% at c008 baseline). Heat is essentially AT bar. Cycle-009 attack budget should flow to:

1. **O1 (LEAD):** `fno_mf_stack × ifc_poisson` capacity / spectral-modes scan — highest EV, lowest risk, sidesteps all NKs.
2. **O2 (SECONDARY):** `recipe_hash` portable utility — operational hygiene, project-wide cycle-003-backlog closure.
3. **O3 (DEFERRED):** Two-stage frozen-LF on `fno_mf_stack` — alternative lever on same cell; NK2-by-design-carve-out applies; both kill-switches mandatory.
4. **O4 (SPECULATIVE RESERVE):** `fno_coreg_conditioned` `γ(m, LF_features)` revision — NK1 sidestep retry.
5. **O5 (REJECTED for c009):** `fno_coregionalization × poisson` basis redesign — too easy to disturb the H1 banked Heat win.

**Reject at R2 with cycle-008 citations:**
- Any single-family Heat+Poisson candidate with pure m-conditioning (NK1, c008 H2).
- Any multi-stage curriculum on `fno_coregionalization` or `fno_coreg_residual` (NK2, c008 H3).
- Any MFRNP-style loss-weight tuning on coregionalization-family (NK3, c003 H1 + c006 H1 + c007 H2).
- Any multi-stage proposal lacking BOTH absolute Stage-k-vs-baseline AND inter-stage ratio kill-switches (c008 H3 design lesson).

The cycle-009 design space is narrower than cycle-008's but better-instrumented. The composite-axis math says: drop `fno_mf_stack × poisson` by 1.5% (0.05961 → 0.05871) to close the bar; drop by >1.5% to dethrone.

## Related notes

- [[cycle-008-summary]] — cycle-008 close-out; 1 KEEP intent + 2 genuine REVERTs producing NK1 and NK2 inputs.
- [[failure-analysis-cycle-008]] — prior baseline framing; heat-dominant 12.6× log-weight reversed into c009's Poisson-dominant 2.2× log-weight.
- [[failure-analysis-cycle-007]] — cycle-007 H1 constructor-fix that enabled c008 H1 capacity bump.
- [[failure-analysis-cycle-003]] — first genuine REVERT (MFRNP cross-architecture recipe portability disproof → NK3 root).
- [[failure-analysis-cycle-006]] — second cross-architecture recipe transfer failure (NK3 reinforcement).
- [[patterns]] §"FiLM-via-LayerNorm on HF-only FNO cannot synthesize LF→HF correlation" (NK1 root).
- [[patterns]] §"Three-stage frozen-LF curricula incompatible with co-evolved residual ladder designs" (NK2 root).
- [[patterns]] §"Multi-stage curriculum kill-switches must include Stage-k-vs-baseline absolute check" (c008 H3 design lesson).
- [[patterns]] §"Cross-architecture recipe portability is NOT guaranteed even when receiving architecture shares structural family" (NK3 root).
- [[patterns]] §"Fresh-train variance can swamp claimed invariance" (NK3 reinforcement).
- [[factory_mffp]] — project dashboard.

## Tags

`failure-analysis`, `cycle-009`, `baseline`, `reproducible-best`,
`dominant-lever-reversal-heat-to-poisson`,
`near-bar-poisson-side`, `capacity-axis-exhausted-on-fno-coregionalization`,
`nk1-pure-m-conditioning-forbidden`, `nk2-frozen-lf-on-residual-ladder-forbidden`,
`nk3-mfrnp-loss-weight-coreg-family-forbidden`,
`o1-fno-mf-stack-capacity-bump-poisson-lead`,
`o2-recipe-hash-portable-utility-secondary`,
`o3-two-stage-frozen-lf-on-fno-mf-stack-deferred`,
`o4-fno-coreg-conditioned-gamma-m-lf-features-reserve`,
`o5-k-basis-redesign-on-coregionalization-poisson-rejected`,
`operator-action-precheck-overhaul-6th-consecutive`
