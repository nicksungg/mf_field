# Failure Analysis — Cycle-009 Baseline (factory_mffp)

## Summary

- **Entry baseline (load-bearing, UNCHANGED by cycle-008 H2/H3):**
  composite_nRMSE = **0.027729** on `experiment/11-fno_coregionalization-paper-capacity @ 18d83a6`
  (banked from cycle-008 H1 paper-config capacity bump).
- **Per-dataset state at entry:**
  - `ifc_heat` best = **0.012898** (`fno_coregionalization`, 2.04× margin over rank #2 `fno_coreg_residual @ 0.026277`).
  - `ifc_poisson` best = **0.05961** (`fno_mf_stack`, 1.24× margin over rank #2 `fno_coreg_residual @ 0.07419`).
- **Parallel-bench bar:** composite **0.027429** (heat 0.01281 / poisson 0.05871 per `failure-analysis-cycle-008`). Gap remaining: **+0.000300 abs (+1.09% over bar)**.
- **Paper bar (`baselines/paper_baselines.json`, IFC-ODE2):** heat 0.074, poisson 0.036.
- **Dominant composite-gap contributor (REVERSED vs cycle-008-baseline):** Poisson now contributes **~69%** of the residual bar gap; Heat contributes **~31%**. Cycle-008 H1's heat capacity-axis win has moved heat from 21% over bar to 0.7% over bar, exhausting the heat-side lever and shifting the dominant lever to Poisson.
- **Dominant failure mode for cycle-009:** `FAMILY_PDE_SPECIALIZATION_ASYMMETRY` on `fno_mf_stack × heat` and `fno_coregionalization × poisson` is no longer addressable from the heat-leader family — the next composite step must come from the Poisson side, specifically reducing `fno_mf_stack × ifc_poisson` below 0.05871 or stealing it via a different family with an LF→HF pathway.
- **Comparison with prior cycle:** Architecturally, cycle-009 enters with a NEW reproducible project best (0.030408 → 0.027729, −8.81%) AND with two genuine REVERTs from cycle-008 closing off two design axes (NK1 = pure m-conditioning, NK2 = frozen-LF on residual ladder). Cycle-009 design space is narrower but better-instrumented.

## Per-Cell Classification (14 cells: 7 families × 2 datasets, from cycle-008-h1 leaderboard)

Bars used: **parallel-bench bar** (operational target) = heat 0.01281 / poisson 0.05871; **paper bar** (`baselines/paper_baselines.json` IFC-ODE2) = heat 0.074 / poisson 0.036. `NEAR_BAR` = within 25% of parallel-bench bar. `AT_PAPER_BAR` = nRMSE ≤ paper bar.

| Family | Dataset | nRMSE | × parallel-bench bar | × paper bar | Family rank on dataset | Category |
|---|---|---:|---:|---:|---:|---|
| `fno_coregionalization` | heat | 0.012898 | 1.007× | 0.174× | 1 | **NEAR_BAR + AT_PAPER_BAR** (essentially AT bar; 5.7× under paper bar) |
| `fno_coregionalization` | poisson | 0.594477 | 10.13× | 16.51× | 5 | **FAMILY_PDE_SPECIALIZATION_ASYMMETRY** (wins heat, loses 10× on poisson; K=10/20 MLP-basis cannot fit non-monotone m-modulation; persistent since c001) |
| `fno_coreg_residual` | heat | 0.026277 | 2.05× | 0.355× | 2 | **CAPACITY_PARETO** (rank #2 heat, 2× over parallel-bench bar but 2.8× under paper bar; banked via c007 K=20/b_hidden=128) |
| `fno_coreg_residual` | poisson | 0.074192 | 1.26× | 2.06× | 2 | **CAPACITY_PARETO** (rank #2 poisson; 26% over parallel-bench bar — boundary case for NEAR_BAR). Recipe-tuning lever closed (REVERT 3/3, see NK3) |
| `mf_fno_transfer_bar` | heat | 0.033175 | 2.59× | 0.448× | 3 | **BAR_UNDERTRAINING_VS_CACHE** (this family's smoke-eval side; parallel-bench full-resolution side IS the 0.01281 bar number — smoke deliberately undertrained) |
| `mf_fno_transfer_bar` | poisson | 0.083326 | 1.42× | 2.31× | 3 | **BAR_UNDERTRAINING_VS_CACHE** (same pattern; parallel-bench side IS the 0.05871 bar; smoke is undertrained) |
| `fno_mf_stack` | heat | 0.099945 | 7.80× | 1.35× | 4 | **FAMILY_PDE_SPECIALIZATION_ASYMMETRY** (wins poisson, loses 7.8× on heat; MFRNP residual stack with poisson-tuned per-fidelity loss weights — heat uses uniform weights) |
| `fno_mf_stack` | poisson | 0.059611 | 1.015× | 1.66× | 1 | **NEAR_BAR (parallel-bench)** + **CAPACITY_PARETO (vs paper bar)** (1.5% over operational bar; 66% over paper bar; current sole composite-gap contributor on Poisson side) |
| `transolver_attention_fusion` | heat | 0.149230 | 11.65× | 2.02× | 7 | **ARCHITECTURE_OBSOLETE** (loses on both; orthogonal direction per [[patterns]] "FNO > Transolver for regular-grid PDE data") |
| `transolver_attention_fusion` | poisson | 0.381812 | 6.50× | 10.6× | 4 | **ARCHITECTURE_OBSOLETE** (per above) |
| `transolver_residual` | heat | 0.114559 | 8.94× | 1.55× | 5 | **ARCHITECTURE_OBSOLETE** |
| `transolver_residual` | poisson | 2.592349 | 44.16× | 72.0× | 6 | **ARCHITECTURE_OBSOLETE** (44× over operational bar) |
| `v9_baseline` | heat | 0.148834 | 11.62× | 2.01× | 6 | **ARCHITECTURE_OBSOLETE** (gated softmax cannot encode value-scale shift; reference implementation only per `config.json`) |
| `v9_baseline` | poisson | 18.503436 | 315× | 514× | 7 | **ARCHITECTURE_OBSOLETE** (known value-scale collapse; cycle-001 F1) |

Notes:
- `fno_coreg_conditioned` (cycle-008 H2 NEW family) is **NOT** in the cycle-008-H1 leaderboard (introduced post-H1 and reverted; cache fell out by cycle-008 H3). On its own cache it scored heat 0.017102 (rank #2 on H2 leaderboard) / poisson 0.749915 (rank #5; 12.6× over `fno_mf_stack`). Both cells are architecturally falsified (see NK1).
- Promotion this cycle: `fno_mf_stack × poisson` moves from `CAPACITY_PARETO` (cycle-008 baseline) → `NEAR_BAR` (cycle-009 baseline) — the parallel-bench gap on this cell narrowed from +1.5% (which it was at c008 entry) to the same +1.5% but is now the LARGEST per-dataset gap because heat collapsed to +0.7%.
- Demotion this cycle: `fno_coregionalization × heat` from `CAPACITY_PARETO` (c008 baseline @ 0.01551, +21% over bar) → `NEAR_BAR + AT_PAPER_BAR` (c009 baseline @ 0.012898, +0.7% over bar). The heat capacity-axis is exhausted on this family at paper config.

## Failure Distribution (composite-gap-weighted)

| Category | Cells | Composite-gap weight |
|---|---:|---|
| **NEAR_BAR (parallel-bench)** | 2 | **All remaining gap** — `fno_mf_stack × poisson` (~69%) + `fno_coregionalization × heat` (~31%) |
| **AT_PAPER_BAR** | 3 | 0 (already past paper bar — `fno_coregionalization`, `fno_coreg_residual`, `mf_fno_transfer_bar` on heat) |
| **CAPACITY_PARETO** | 2 (residual cells on rank-#2 family) | 0 to composite (not best on either dataset; closing would only unlock single-family unification) |
| **FAMILY_PDE_SPECIALIZATION_ASYMMETRY** | 2 (`fno_coregionalization × poisson`, `fno_mf_stack × heat`) | 0 to composite (each family is dominated by the other on its weak dataset) |
| **BAR_UNDERTRAINING_VS_CACHE** | 2 (`mf_fno_transfer_bar` smoke side) | 0 to composite (parallel-bench-side is the bar reference) |
| **ARCHITECTURE_OBSOLETE** | 6 (transolver_* + v9_baseline) | 0 to composite (dominated on both datasets) |
| TRANSFER_SIGNAL_UNUSED | 0 | — (the cycle-007 H2 LF→HF schedule was re-bound on the c008 H1 capacity bump implicitly by virtue of paper config; explicit re-bind ARCHITECTURE-FALSIFIED via NK2 path) |
| RECIPE_DATASET_NONPORTABILITY | 0 active | (locked-off lever — see NK3; `fno_coreg_residual × poisson` regression history pinned) |

**Dominant failure mode:** `NEAR_BAR` on Poisson side (`fno_mf_stack × ifc_poisson`, ~69% of remaining bar gap).

## Composite-Gap Contribution by Dataset

Composite is geomean: `composite = sqrt(heat * poisson)`. Working in log space:

- `log(0.012898 / 0.01281) = log(1.00687) = 0.00685` (heat over bar)
- `log(0.05961 / 0.05871) = log(1.01533) = 0.01521` (poisson over bar)
- Composite log-gap = `0.5 × (0.00685 + 0.01521) = 0.01103`

**Per-dataset share of the +1.09% composite gap:**
- Heat: **31.1%**
- Poisson: **68.9%**

**Counterfactual (closing one dataset alone):**
- **Close Poisson to parallel-bench bar (0.05961 → 0.05871):** composite → `sqrt(0.012898 × 0.05871) = 0.02752`. Drops by 0.00021. **Closes 69.7% of the +0.000300 bar gap.**
- **Close Heat to parallel-bench bar (0.012898 → 0.01281):** composite → `sqrt(0.01281 × 0.05961) = 0.02763`. Drops by 0.00009. **Closes 31.0% of the +0.000300 bar gap.**
- **Close both to parallel-bench bar:** composite → 0.027429 (=bar; gap closes by definition).

**REVERSAL from cycle-008 baseline:** at c008 baseline the heat log-gap ratio was +0.191 vs poisson +0.015 — heat dominated the composite gap by 12.6×. Cycle-008 H1's capacity bump on `fno_coregionalization × heat` (0.01551 → 0.012898, −16.8%) inverted the asymmetry. The cycle-008 close-out already flagged this; cycle-009 should plan accordingly: **the heat-axis lever is exhausted; the Poisson side now owns the gap.**

## Negative-Knowledge Zones (FORBIDDEN for cycle-009)

### NK1 — Pure m-conditioning on HF-only FNO (cycle-008 H2)

> FiLM-via-LayerNorm with affines computed as `γ(m, m²)` — i.e., pure m-conditioning — on a single HF FNO **cannot synthesize the LF→HF correlation pathway** that `ifc_poisson` requires.

- **Evidence:** cycle-008 H2 (`fno_coreg_conditioned`, `experiment/12 @ 540e684`) — heat 0.017102 (competitive at rank #2; FiLM-on-HF-only viable when HF training data alone is sufficient) but poisson 0.749915 (12.6× over `fno_mf_stack`; catastrophically outside Builder's predicted 0.05–0.15 range). Composite +9.66% vs banked best. Kill switches CLEAR — silent under-performance, not blow-up.
- **Cycle-009 application:** any single-family Heat+Poisson candidate MUST either (a) re-introduce LF→HF pathway (residual ladder), OR (b) condition FiLM affines on LF features directly: `γ(m, LF_features)` instead of `γ(m, m²)`. Reject pure m-conditioning at R2.
- The 828 LOC FiLM scaffolding on `experiment/12 @ 540e684` is preserved — sidesteppable via revision (b).

### NK2 — Frozen-LF curricula on co-evolved residual ladders (cycle-008 H3)

> Three-stage (or any) curricula that freeze the LF stack mid-training (`requires_grad=False`) are **INCOMPATIBLE with co-evolved residual ladder designs** (`fno_coregionalization`, `fno_coreg_residual`). Stage-2 LF-freeze forces the HF residual to correct against an OOD frozen LF state from the LF-only pretrain regime, producing garbage.

- **Evidence:** cycle-008 H3 (`fno_coreg_residual` three-stage, `experiment/13 @ 420a51c`) — `fno_coreg_residual × heat` regressed 19× (0.026277 → 0.509105); universal `ifc_heat > 0.0194` kill-switch TRIPPED **26× over threshold**. `fno_coreg_residual × poisson` regressed 2.15× (0.074192 → 0.159364). H3-specific Stage3/Stage2 ratio kill-switch did NOT trip — damage occurred in Stages 1/2.
- **Cycle-009 application:** DO NOT propose multi-stage frozen-LF curricula on `fno_coregionalization` or `fno_coreg_residual`. End-to-end joint training (cycle-005 H2 continuous-LR-schedule pattern) is the correct recipe for co-evolved designs. Multi-stage MAY be appropriate for families with LF/HF **independent by design** (`mf_fno_transfer_bar`, `fno_mf_stack`) — but ANY multi-stage proposal MUST specify BOTH absolute Stage-k-vs-baseline AND inter-stage ratio kill-switches.

### NK3 — MFRNP-style loss-weight transfer on coregionalization family (cycles 003/006/007)

> Per-dataset MFRNP loss-weight tuning (HF=2.0, LF=0.25 and variants) on the coregionalization family produces heat-invariance violations even when the heat branch is claimed invariant by construction. Fresh-train variance + shared training infrastructure consistently break the invariance claim.

- **Evidence:** cycle-003 H1 (Poisson5 transplant `fno_mf_stack → fno_coreg_residual`: poisson +268% regression, heat unchanged — REVERT); cycle-006 H1 (reverse cross-architecture transplant `fno_coreg_residual → fno_mf_stack`: REVERT); cycle-007 H2 (within-family per-dataset dispatch on `fno_coreg_residual`: heat 0.02628 → 0.03487 +32.7% at 6.5× the noise band — falsified "invariant by construction" claim, REVERT). 3/3 REVERT history.
- **Cycle-009 application:** any new MFRNP-style loss-weight reweighting hypothesis on `fno_coreg_residual` / `fno_coregionalization` MUST declare (i) a heat-invariance kill-switch with band derived from ≥3 prior fresh-train values, AND (ii) best-of-N (N≥2) seed control with frozen heat seed. **Practically: this axis is closed for cycle-009 on coregionalization-family.** Loss-weight tuning may still be valid on `fno_mf_stack` itself (where the recipe was born and is canonical), but only on poisson (heat uses uniform weights already).

## Open Architectural Axes (NOT in NK1/NK2/NK3, consistent with `mutable_surfaces=models/**`)

| # | Axis | Sidesteps | Target cells | Composite reachable? |
|---|---|---|---|---|
| O1 | **`fno_mf_stack` capacity scan on Poisson** (hidden 32→64, modes_per_level `(4,8,12,12)`→`(8,16,16,16)`, n_blocks 3→4 in `SMOKE_DEFAULTS`) | NK1/2/3 (capacity, not recipe/curriculum/conditioning) | `fno_mf_stack × poisson` (NEAR_BAR, owns 69% of gap) | YES — direct lever on the dominant gap contributor |
| O2 | **Spectral-mode / anisotropic-modes audit on `fno_mf_stack`** (cycle-007 H1 fix was applied to `fno_coregionalization` only — same constructor-class pattern may still be latent on `fno_mf_stack`) | NK1/2/3 | `fno_mf_stack × poisson` | YES — analogous unlock to cycle-007 H1 |
| O3 | **Two-stage frozen-LF curriculum on `mf_fno_transfer_bar` OR `fno_mf_stack`** (LF/HF independent by design — NK2's incompatibility argument does NOT apply) | NK2 (by design); NK1/3 by construction | `fno_mf_stack × poisson` or `mf_fno_transfer_bar × poisson` smoke | YES — but BOTH absolute and inter-stage kill-switches MANDATORY |
| O4 | **`fno_coreg_conditioned` revision with `γ(m, LF_features)`** (preserve cycle-008 H2 FiLM scaffolding on `experiment/12 @ 540e684`; replace `γ(m, m²)` with FiLM affines conditioned on broadcast LF features) | NK1 (re-introduces LF pathway) | `fno_coregionalization × poisson` (unified single-family candidate); could steal poisson from `fno_mf_stack` | Speculative — composite reachable only if poisson < 0.05961 |
| O5 | **`recipe_hash` portable utility cherry-pick** (extract from `models/fno_coreg_residual/smoke_eval.py` lines ~113-123 / 461-485 → `models/_common/recipe_hash.py`; apply to all family `smoke_eval.py`) | All NKs (purely operational) | None directly; unlocks ALL future cycle resume-safety | NO direct composite move — meta-fix unlocks every subsequent experiment |
| O6 | **LR-schedule / one-cycle / cosine-warmup re-tune on `fno_mf_stack`** (current lr=3e-4, no explicit schedule) | NK1/2/3 | `fno_mf_stack × poisson` | Modest — schedule-class wins typically 5-15% |
| O7 | **K-basis redesign on `fno_coregionalization × poisson`** — replace MLP-basis `B(m) = MLP([m, m²])` with `B(m, LF) = MLP([m, LF_features])` to inject LF signal into the per-fidelity basis | NK1 (sidesteps; LF in basis) | `fno_coregionalization × poisson` (FAMILY_PDE_SPECIALIZATION_ASYMMETRY) | Speculative; unifies family at cost of new architecture surface |
| O8 | **`mf_fno_transfer_bar` smoke-eval undertraining fix** (currently smoke 0.033175 heat / 0.083326 poisson vs full-resolution 0.01281/0.05871 — same architecture, deliberately undertrained smoke) | All NKs (training-time only) | BAR_UNDERTRAINING_VS_CACHE cells | NO — raises the parallel-bench bar; explicitly **DEFER** per cycle-008 baseline analysis |

## Recommended Intervention Axes for Cycle-009 (Priority-Ordered)

### Priority 1 — O1: `fno_mf_stack` capacity bump on Poisson (HIGHEST EV)

- **Target failure cell(s):** `fno_mf_stack × ifc_poisson` (NEAR_BAR / CAPACITY_PARETO; owns ~69% of the +1.09% composite gap).
- **Mutable surfaces:** `models/fno_mf_stack/smoke_eval.py` (SMOKE_DEFAULTS at lines 37-53); possibly `models/fno_mf_stack/model.py` if modes_per_level shape forces constructor updates; possibly `models/fno_mf_stack/full_config.json` for the full-resolution mirror.
- **Suggested levers (Builder to decide exact values):** hidden 32→64; modes_per_level `(4,8,12,12)` → `(8,16,16,16)` or `(8,16,20,20)`; n_blocks 3→4. Audit constructor anisotropic-modes handling per cycle-007 H1 pattern (O2 folded in).
- **Expected qualitative composite impact:** **LARGE** — direct attack on the 69% gap contributor. Closing poisson 0.05961 → 0.05871 (parallel-bench bar) drops composite to 0.02752 (closes 70% of remaining gap); further drop into <0.05871 territory dethrones bar outright.
- **Novelty/risk vs cycle-008 negative-knowledge baseline:** **LOW** — direct capacity-axis analog of cycle-008 H1's playbook (which closed 90% of the gap on heat side). NK1/2/3 not engaged. Kill switches: poisson kill at >0.0594 (current baseline); wall <30 min.
- **Sidesteps:** NK1 ✓ (no FiLM conditioning), NK2 ✓ (no curriculum / no freeze), NK3 ✓ (capacity not recipe; poisson loss weights already canonical-MFRNP — no perturbation).

### Priority 2 — O5: `recipe_hash` portable utility cherry-pick (META-FIX, OPERATIONAL)

- **Target failure cell(s):** None directly composite-moving — closes the cycle-003 H1 stage-resume contamination pathway **project-wide**.
- **Mutable surfaces:** NEW `models/_common/recipe_hash.py` (utility); one-line import + recipe_hash arg in every family's `smoke_eval.py`: `models/{fno_coregionalization,fno_coreg_residual,fno_mf_stack,fno_coreg_conditioned,mf_fno_transfer_bar,transolver_residual,transolver_attention_fusion}/smoke_eval.py`.
- **Expected qualitative composite impact:** **NONE directly; LARGE indirectly** — every subsequent cycle's checkpoint resume is silently corrupted-safe instead of silently corrupted. cycle-003 backlog item closed.
- **Novelty/risk:** **LOW** — proven pattern from `fno_coreg_residual/smoke_eval.py` (cycle-008 H3), live-tested with stale-checkpoint rejection log line verified.
- **Sidesteps:** all NKs (purely operational, no architecture / recipe / curriculum change). The three-stage curriculum gating logic from cycle-008 H3 is **NOT** to be cherry-picked.
- **Strategist note:** as operational hygiene, this should be tracked separately from primary composite-moving hypotheses — see §"Operational Hygiene Items" below.

### Priority 3 — O3: Two-stage frozen-LF curriculum on `fno_mf_stack` (LF/HF independent by design)

- **Target failure cell(s):** `fno_mf_stack × ifc_poisson` (NEAR_BAR) — alternative lever to O1's capacity scan, attacking same cell.
- **Mutable surfaces:** `models/fno_mf_stack/smoke_eval.py` (add Stage-1 LF-pretrain → Stage-2 HF-residual frozen-LF schedule).
- **Expected qualitative composite impact:** **MEDIUM** — c007 H2-class two-stage schedule has prior precedent of moderate gains on the unrelated coregionalization family.
- **Novelty/risk vs c008 baseline:** **MEDIUM-LOW** — the NK2 argument explicitly carves out `fno_mf_stack` and `mf_fno_transfer_bar` as families where LF/HF are independent by design (per-fidelity stacked predictions, not co-evolved residuals). MUST specify BOTH (a) absolute Stage-k-vs-baseline kill (Stage-k poisson > 1.25× 0.05961 → REVERT) AND (b) inter-stage ratio kill — cycle-008 H3 design lesson.
- **Sidesteps:** NK1 ✓, NK2 ✓ (by-design carve-out; reject any same-style proposal on `fno_coreg_residual`/`fno_coregionalization` at R2), NK3 ✓.

### Priority 4 — O4: `fno_coreg_conditioned` revision with `γ(m, LF_features)` (SPECULATIVE UNIFIED CANDIDATE)

- **Target failure cell(s):** `fno_coregionalization × ifc_poisson` (FAMILY_PDE_SPECIALIZATION_ASYMMETRY); steals Poisson from `fno_mf_stack` if it works.
- **Mutable surfaces:** preserve `experiment/12 @ 540e684` 828 LOC FiLM scaffolding; revise `models/fno_coreg_conditioned/model.py` to compute FiLM `γ, β` from a broadcast LF-feature spatial channel instead of pure `[m, m²]`. (Cycle-008 H2 builder predicted poisson 0.05-0.15 was wrong by design; the LF-feature revision is the architectural fix per c008 close-out implication.)
- **Expected qualitative composite impact:** **LARGE if it works** (single-family Heat+Poisson winner); **NONE if it doesn't** (would just be a 2nd-place family on heat).
- **Novelty/risk vs c008 baseline:** **MEDIUM-HIGH** — directly applies the c008 H2 architectural lesson (NK1 sidestep), but kept-novel revision; ≥1 retry of a previously-falsified architecture class.
- **Sidesteps:** NK1 ✓ (LF-feature pathway re-introduced), NK2 ✓ (no curriculum / no freeze), NK3 ✓ (FiLM affines, not loss weights).

### Priority 5 — O2 (FOLDED INTO O1) / O7: K-basis redesign on `fno_coregionalization × poisson`

- **Target failure cell(s):** `fno_coregionalization × ifc_poisson` (FAMILY_PDE_SPECIALIZATION_ASYMMETRY, persistent since c001 at ~0.6-0.75).
- **Mutable surfaces:** `models/fno_coregionalization/model.py` (B(m) basis MLP) + `models/fno_coregionalization/smoke_eval.py`.
- **Expected qualitative composite impact:** **MODEST-to-LARGE if successful** — would let same family own both datasets; current poisson 0.5945 → would need to drop ~10× to enter composite. Even a partial reduction does not enter composite while `fno_mf_stack` owns Poisson, so requires successful undercut of 0.05961.
- **Novelty/risk:** **HIGH** — speculative redesign of basis function; failure mode well-mapped (K=10/20 MLP-basis cannot fit non-monotone m-modulation). Not the cleanest lever.
- **Sidesteps:** NK1 ✓ (if `B(m, LF)` formulation), NK2 ✓, NK3 ✓.

## Operational Hygiene Items (NOT primary composite-moving hypotheses; tracked separately)

Items the Strategist may NOT generate as primary composite-moving hypotheses but should track:

1. **`recipe_hash` portable utility cherry-pick** (O5 above) — operational, unlocks future composite-moving experiments. Suggest as a non-hypothesis maintenance PR or as a quick-win hypothesis with explicit "operational-only, not composite-moving" framing.
2. **6th consecutive precheck overhaul backlog flag** — `score_direction` polarity (10-of-10 incl. cycle-008 H2 symmetric-flip silencing of regression), `scope`/`fixed_surfaces` empty-detail (4-of-4), leakage substring-collision (6-of-6). Out of factory scope; archive note + CEO intent are load-bearing institutional record. Operator action standing.
3. **Stale-cache risk on `fno_coreg_conditioned`** — cycle-008 H2 family's cache fell out by cycle-008 H3 (see h3 notes: "fno_coreg_conditioned not present this run — cache fell out / not retrained"). If cycle-009 wants to re-test the H2 architecture (e.g., O4 above with `γ(m, LF_features)`), Builder must re-train from scratch and not assume cache hit. Wall budget +~92s per H2-family retrain.
4. **Researcher / failure_analyst wrapper timeout pattern** (5+ cycles) — CEO has been synthesizing substitutes from direct source reads. Standing operational practice; no change in cycle-009 R1/R1.5 plans.
5. **`mf_fno_transfer_bar` smoke-eval undertraining (BAR_UNDERTRAINING_VS_CACHE)** — DEFER per cycle-008 baseline analysis; fixing would raise the parallel-bench bar.

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
| `mf_fno_transfer_bar × heat` (smoke) | 0.033175 | 0.033175 | 0% | stable, undertrained on purpose |
| `mf_fno_transfer_bar × poisson` (smoke) | 0.083326 | 0.083326 | 0% | stable, undertrained on purpose |
| `transolver_*` + `v9_baseline` | — | — | 0% | stable; ARCHITECTURE_OBSOLETE locked-off |

**Improvements (c008 → c009 baseline):**
- `fno_coregionalization × heat` −16.84% (cycle-008 H1 paper-config capacity bump on the repaired anisotropic-modes constructor); now AT_PAPER_BAR + NEAR_BAR.
- `fno_coregionalization × poisson` −20.75% (incidental benefit of paper config); still FAMILY_PDE_SPECIALIZATION_ASYMMETRY at 10× over bar.
- Composite_nRMSE −8.81%; new reproducible project best; 89.93% of parallel-bench bar gap closed by capacity-axis alone.

**Regressions (c008 → c009 baseline):**
- None at composite level. Two genuine REVERTs (H2, H3) absorbed without metric impact.
- H2 (`fno_coreg_conditioned`) — architecture-falsified on Poisson at 12.6× over leader. NEW NK1 zone.
- H3 (`fno_coreg_residual` three-stage curriculum) — universal heat kill-switch tripped 26× over threshold. NEW NK2 zone.

**New failure modes (c008 → c009):**
- Both NK1 and NK2 emerged from cycle-008 H2 and H3 respectively as architecturally-falsified design axes. NK3 (MFRNP loss-weight non-portability) was already 3/3 REVERTed at c008 baseline; reinforced as locked-off via c008 H3's failed three-stage recipe variant.
- Dominant-gap-contributor inversion: heat (12.6× log-weight at c008 baseline) → poisson (~2.2× log-weight at c009 baseline). The cycle-009 attack budget should flow to Poisson side.

## Failure Taxonomy Update

No new failure categories surfaced in cycle-008 H1 result itself (which produced no failures — H1 was a clean composite-improving KEEP-intent). The cycle-008 H2/H3 REVERTs surfaced two negative-knowledge architectural lessons (encoded as NK1 and NK2 above) and one kill-switch design lesson (multi-stage curriculum kill-switches MUST include absolute Stage-k-vs-baseline check). These are pattern-level updates (see `.factory/archive/patterns/patterns.md`), not new failure categories on the per-cell taxonomy.

**Existing taxonomy categories applied this cycle:**
- AT_PAPER_BAR, NEAR_BAR, CAPACITY_PARETO, FAMILY_PDE_SPECIALIZATION_ASYMMETRY, BAR_UNDERTRAINING_VS_CACHE, ARCHITECTURE_OBSOLETE (defined cycle-001-008).
- TRANSFER_SIGNAL_UNUSED — no active cells at c009 baseline (the c007 H2 LF→HF schedule had its single-stage capacity path subsumed into c008 H1).
- RECIPE_DATASET_NONPORTABILITY — no active cells; closed lever (REVERT 3/3 history → NK3).

**Promotion / Demotion table (c008 → c009):**

| Cell | c008 baseline category | c009 baseline category | Reason |
|---|---|---|---|
| `fno_coregionalization × heat` | CAPACITY_PARETO | **NEAR_BAR + AT_PAPER_BAR** | c008 H1 capacity-axis closed the gap (0.01551 → 0.012898, +0.7% over bar, 5.7× under paper bar) |
| `fno_mf_stack × poisson` | NEAR_PARITY_INCREMENTAL (c008 promotion) | **NEAR_BAR** (now sole dominant gap contributor) | Same nRMSE, but its share of composite gap rose from minority to 69% as heat collapsed under-bar |
| `fno_coregionalization × poisson` | FAMILY_PDE_SPECIALIZATION_ASYMMETRY | **FAMILY_PDE_SPECIALIZATION_ASYMMETRY** (unchanged) | Family persistent issue; ~21% reduction within-cell not composite-relevant |

## Closing Notes

The cycle-008 → cycle-009 transition closed a large composite delta (−8.81%) and a large fraction of the parallel-bench bar gap (89.93%) via a single architectural axis (capacity on `fno_coregionalization`), while **closing off two architectural axes** (NK1 pure m-conditioning on HF-only; NK2 frozen-LF curricula on co-evolved residual ladders) and **reinforcing one prior closure** (NK3 MFRNP loss-weight transfer on coregionalization-family).

The remaining +1.09% bar gap inherits a **NEW dominant lever**: Poisson contributes 69% of the residual gap (vs 1.2% at c008 baseline). Heat is essentially AT bar. Cycle-009 attack budget should flow to:
1. **`fno_mf_stack × ifc_poisson` capacity/spectral-modes scans** (O1+O2 folded) — highest EV, lowest risk, sidesteps all NKs.
2. **`recipe_hash` portable utility** (O5) — operational hygiene, project-wide cycle-003-backlog closure.
3. **Two-stage frozen-LF on `fno_mf_stack`** (O3) — alternative lever on same cell; NK2-by-design-carve-out applies; both kill-switches mandatory.
4. **`fno_coreg_conditioned` `γ(m, LF_features)` revision** (O4) — speculative unified-family candidate; NK1 sidestep retry.
5. **`fno_coregionalization × poisson` basis redesign** (O7) — speculative; NK1 sidestep.

**Reject at R2 with cycle-008 citations:**
- Any single-family Heat+Poisson candidate with pure m-conditioning (NK1, c008 H2).
- Any multi-stage curriculum on `fno_coregionalization` or `fno_coreg_residual` (NK2, c008 H3).
- Any MFRNP-style loss-weight tuning on coregionalization-family (NK3, c003 H1 + c006 H1 + c007 H2).
- Any multi-stage proposal lacking BOTH absolute Stage-k-vs-baseline AND inter-stage ratio kill-switches (c008 H3 design lesson).

The cycle-009 design space is narrower than cycle-008's but better-instrumented. The composite-axis math says: drop `fno_mf_stack × poisson` by 1.5% (0.05961 → 0.05871) to close the bar; drop by >1.5% to dethrone.
