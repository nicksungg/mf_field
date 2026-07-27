---
name: cycle-010-strategy
description: Cycle-010 Strategy snapshot — 2 hypotheses, sequenced and UNBUNDLED. H1 LEAD (HIGH, MUST LAND FIRST) = fno_mf_stack capacity-axis 2nd step (SMOKE_DEFAULTS hidden=64→96, modes_per_level=(4,8,16,20)→(4,8,16,24); n_blocks=4 held; ~2.0M params); H2 SECONDARY (MEDIUM, separate PR after H1 banks) = Lyu+yang2025mfdeeponet two-stage LF→HF curriculum on fno_mf_stack with FROZEN LF stage 2 (pretrain_frac=0.40, stage2_freeze_lf=True; fresh Adam+CosineAnnealingLR per stage); NK2 carve-out applied because model.py:165-168 has 4 independent SmallFNO modules; clears cycle-009 O3 backlog item. CEO PROCEED + PLAN APPROVED with explicit sequencing plan (H1 first → bank → H2 on H1's banked branch). Both leakage-check passed risk_level=none. Mandatory dual kill-switches on H2 (absolute Poisson/Heat ≤ 0.0594 AND inter-stage stage2_best_val ≥ 0.90 × stage1_best_val AND wall > 1800s).
tags:
  - factory
  - strategy
  - factory_mffp
project: factory_mffp
cycle: 010
date: 2026-06-02
source: factory-archivist
verdict: PROCEED — PLAN APPROVED
mode: research
baseline_composite: 0.022161
baseline_branch: experiment/14-fno_mf_stack-capacity-and-recipe-hash
baseline_commit: 0b6e6eb
baseline_identical_to: cycle-009-h1h2 (all 14 cells cache-hit, zero drift)
bar_ifc_ode2_geomean_ratio: 0.43
bar_ifc_gpode_geomean_ratio: 0.67
remaining_pct_of_gap_on_poisson: 100
load_bearing_cell: "fno_mf_stack × ifc_poisson"
load_bearing_cell_value: 0.038120
dominant_failure_mode: POISSON_STRUCTURAL_GAP_PER_FAMILY_ASYMMETRY
hypothesis_count: 2
hypothesis_count_cap: 2
priority_order: H1 > H2
bundling: forbidden (H1 + H2 both edit models/fno_mf_stack/smoke_eval.py; confounded bundle would not let attribution survive; H1 first → bank → H2 separate PR)
github_mode: --no-github (local commit only; no PR, no remote push)
leakage_h1_risk_level: none
leakage_h2_risk_level: none
leakage_flagged: false
h1_branch: experiment/15-fno_mf_stack-capacity-axis-2nd-step
h2_branch: experiment/16-fno_mf_stack-curriculum-frozen-lf
h1_mutable_surface: "models/fno_mf_stack/smoke_eval.py lines 39-55 (SMOKE_DEFAULTS only)"
h1_changes: "hidden=64→96, modes_per_level=(4,8,16,20)→(4,8,16,24)"
h1_unchanged: "n_blocks=4, agg_hidden=64, batch_size=8, lr=3e-4, weight_decay=1e-5, val_frac=0.1, native_resolutions=(8,16,32,64), hf_loss_weight=1.0, baseline_anchor_weight=0.5, poisson_hf_weight=2.0, poisson_lf_weight=0.25"
h1_param_estimate_million: 2.0
h1_expected_poisson_min: 0.030
h1_expected_poisson_max: 0.034
h1_expected_poisson_delta_pct_min: -22
h1_expected_poisson_delta_pct_max: -10
h1_expected_composite_min: 0.0197
h1_expected_composite_max: 0.0212
h1_expected_composite_delta_pct_min: -11
h1_expected_composite_delta_pct_max: -5
h1_kill_switch_poisson: 0.0594
h1_kill_switch_heat: 0.0594
h1_kill_switch_wall_seconds: 1500
h1_wall_budget_seconds_estimate: "600-900"
h1_nk_status: NK-clear
h1_priority: HIGH
h1_confidence: HIGH
h1_category: EXPLOIT
h1_new: true
h1_modes_hard_hold: "modes_per_level[3] ≤ 24 (~73% Nyquist) — fnospectralperspective2024 + stresstest2025fno saturation bound"
h2_mutable_surface: "models/fno_mf_stack/smoke_eval.py — SMOKE_DEFAULTS (lines 39-55) + training loop (lines 217-276) + compute_losses (lines 62-107) + optimizer construction (lines 182-194)"
h2_changes: "add SMOKE_DEFAULTS keys pretrain_frac=0.40, stage2_freeze_lf=True; refactor _build_opt_sched(model, p, t_max) helper; stage 1 = LF-only fresh Adam@1e-3 + CosineAnnealingLR(stage1_epochs); stage transition (epoch == stage1_epochs+1) applies requires_grad_(False) to lf_fnos[0..2] + rebuilds fresh stage-2 Adam@3e-4 + fresh cosine; stage 2 = joint loss with frozen LF stack"
h2_unchanged_mfrnp_weights: "(poisson_hf_weight=2.0, poisson_lf_weight=0.25) across both stages (NK3 invariant)"
h2_nk2_carve_out: "model.py:165-168 — 4 INDEPENDENT SmallFNO modules, coupled only through MFRNPAggregator MLP; NK2 anti-pattern's shared-K-basis mechanism does NOT apply"
h2_clears_backlog_item: "cycle-009 close-out O3 — Two-stage frozen-LF curriculum on fno_mf_stack or mf_fno_transfer_bar (LF/HF independent by design; NK2 carve-out); deferred until H1 capacity-axis lever exhausted"
h2_expected_poisson_min: 0.027
h2_expected_poisson_max: 0.032
h2_expected_poisson_delta_pct_min: -15
h2_expected_poisson_delta_pct_max: -5
h2_expected_composite_min: 0.0184
h2_expected_composite_max: 0.0205
h2_expected_composite_delta_pct_min: -17
h2_expected_composite_delta_pct_max: -7
h2_expected_composite_measured_against: "H1-banked composite, NOT cycle-010 baseline"
h2_kill_switch_poisson_absolute: 0.0594
h2_kill_switch_heat_absolute: 0.0594
h2_kill_switch_inter_stage_ratio: 0.90
h2_kill_switch_inter_stage_rule: "stage_2 best_val ≥ 0.90 × stage1_best_val (i.e. stage 2 must reduce val by ≥10%); if not met, REVERT to stage-1 checkpoint and report STAGE_2_NO_IMPROVEMENT"
h2_kill_switch_wall_seconds: 1800
h2_wall_budget_seconds_estimate: "1500-1700"
h2_nk_status: NK2 carve-out (structurally justified by LF/HF-independent design)
h2_priority: MEDIUM
h2_confidence: MEDIUM-HIGH
h2_category: EXPLORE-curriculum
h2_new: false (backlog clearance)
h2_pretrain_frac: 0.40
h2_stage1_lr: 0.001
h2_stage2_lr: 0.0003
h2_stage1_optimizer: "Adam (fresh)"
h2_stage2_optimizer: "Adam (fresh)"
h2_scheduler: "CosineAnnealingLR (fresh per stage, eta_min=1e-6)"
h2_freeze_target: "model.lf_fnos[0..2].requires_grad_(False)"
sequencing_plan: "Experiment 1 (H1): branch from baseline 0b6e6eb → experiment/15 → SMOKE_DEFAULTS edit → smoke-verify --epochs 2 → full smoke → verdict vs 0.022161. Experiment 2 (H2): branch from H1's banked branch → experiment/16 → training loop changes → verdict vs H1's banked composite. If H1 reverts, H2 still defensible (curriculum is fresh-axis-distinct from capacity)."
nks_in_force: ["NK1_pure_m_conditioning_hf_only_h1_clear_h2_clear", "NK2_frozen_lf_curriculum_on_residual_ladder_h2_carve_out_load_bearing", "NK3_mfrnp_loss_weight_to_coregionalization_h1_clear_h2_clear"]
backlog_deferrals: ["O1-aggressive (fno_mf_stack capacity 3rd step hidden=128, modes=(4,8,16,24), n_blocks=5 — pursue only if H1 lands net-positive AND wall <1500s)", "O3 (fno_coregionalization input-dependent K-basis B(m, LF_features) — defer until H1/H2 exhausted)", "O4 (NEW family fno_coreg_conditioned_v2 with γ(m, LF_features) FiLM — defer until H1+H2 fail to break 0.030 Poisson floor)", "Adjacent literature additions to papers_summary.csv — 15 keys ready (human-action)", "MFRNP_AGGREGATOR_POISSON_SPECIALIZATION axis — ablate aggregator topology in later cycle"]
new_bibtex_keys_cited_h1: ["mutransferfno2025", "fnospectralperspective2024"]
new_bibtex_keys_cited_h2: ["yang2025mfdeeponet", "pretrain_lowerdims2024"]
arxiv_id_correction_applied: "stresstest2025fno 2501.11428 → 2601.11428"
ceo_verdict_close_out: ceo-verdict-strategist.md
ceo_hard_gate_checklist: "10/10 PASS — surface constraints, leakage scan (both risk_level=none), hypothesis count (2/2 cap), NK1 sidestep, NK2 carve-out structurally justified, NK3 sidestep, operational items N/A, backlog adequacy (O3 fully addressed), no calendar estimates, bundling caveat respected"
related:
  - cycle-009-strategy
  - failure-analysis-cycle-010
  - research-cycle-010
  - cycle-008-summary
---

# Strategy: factory_mffp — cycle-010 — 2026-06-02

## Verdict

**PROCEED — PLAN APPROVED** (CEO hard gate cleared 10/10).

- 2 hypotheses (H1 = new, H2 = backlog clearance). max_new=2 budget honored.
- Both Type: code; both confined to `models/fno_mf_stack/smoke_eval.py` (mutable surface).
- All three cycle-010-binding anti-patterns (NK1/NK2/NK3) honored: H1 NK-clear; H2 takes the published NK2 carve-out (LF/HF-independent design, mandatory dual kill-switch as the carve-out's price).
- Priority order **H1 > H2** with **bundling EXPLICITLY FORBIDDEN** — both touch `smoke_eval.py:39-55` SMOKE_DEFAULTS and confounded H1+H2 would prevent attribution of Poisson reduction between the capacity-axis and curriculum-axis levers.
- Sequencing: H1 first → measure → bank → H2 on top of H1's banked branch.

## Baselines

- **Reproducible baseline composite_nRMSE:** 0.022161 (current HEAD `experiment/14-fno_mf_stack-capacity-and-recipe-hash @ 0b6e6eb`; identical to cycle-009 H1+H2 — all 14 model×dataset cells cache-hit, zero drift).
- **Paper-bar status:** Both IFC-ODE2 geomean (0.0516) at 0.43× and IFC-GPODE geomean (0.0331) at 0.67× — strategic target shifted to **IFC-GPODE per-dataset bars** (heat 0.061, poisson 0.018).
- **Per-dataset state at entry:**
  - `ifc_heat` best = 0.012884 (`fno_coregionalization`, 4.7× under GPODE — heat-lever EXHAUSTED).
  - `ifc_poisson` best = 0.038120 (`fno_mf_stack`, 1.06× over IFC-ODE2 / 2.12× over IFC-GPODE — sole composite-gap contributor).
- **Composite-leverage math:** Closing Poisson → 0.030 unlocks composite −11.3%; → 0.025 unlocks −19.0%; → 0.018 (GPODE) unlocks −31.3%. Heat closure unlocks 0%. **100% of remaining gap on Poisson; load-bearing cell = `fno_mf_stack × ifc_poisson`.**

## Hypotheses

### H1 — `fno_mf_stack` capacity-axis 2nd step (HIGH, EXPLOIT) — LEAD, MUST LAND FIRST

- **Hypothesis:** Second in-family capacity bump (`hidden 64→96`, `modes_per_level (4,8,16,20)→(4,8,16,24)`, `n_blocks=4` held) extends the cycle-009-h1h2 capacity-axis trajectory (slope `log(nRMSE)/log(params) ≈ −0.39`) into the next ~2× param tier without crossing the saturation cliff. Conservative HF-modes cap at 24 (≈73% Nyquist on 64×64) stays inside the `stresstest2025fno` / `fnospectralperspective2024` published-comfort range for elliptic Poisson, holds the canonical MFRNP loss recipe (NK3-invariant), and closes a measurable fraction of the residual Poisson gap.
- **Mutable surface:** `models/fno_mf_stack/smoke_eval.py` SMOKE_DEFAULTS dict at lines 39-55 ONLY. **No `model.py` change** (auto-clamp at `models/fno_mf_stack/model.py:32-78` verified). **No `data.py` change.**
- **Expected:** Poisson 0.0381 → 0.030–0.034 (−10 to −22%); composite 0.022161 → 0.0197–0.0212 (−5 to −11%). Midpoint 0.0205 ≈ 62% of IFC-GPODE bar.
- **Kill-switches:** Poisson_test > 0.0594 OR Heat_test > 0.0594 OR wall > 1500s → REVERT. `recipe_hash` checkpoint guard (already wired) gates resume.
- **Wall budget:** ~600–900s smoke total per dataset on a single H100.
- **NK status:** NK1-clear (no conditioning), NK2-clear (no curriculum), NK3-clear (canonical MFRNP weights held).
- **Confidence:** HIGH. **Branch:** `experiment/15-fno_mf_stack-capacity-axis-2nd-step`.

### H2 — `fno_mf_stack` LF→HF curriculum with frozen-LF stage 2 (MEDIUM, EXPLORE-curriculum, NK2 carve-out) — SECONDARY, SEPARATE PR

- **Hypothesis:** Applying the published Lyu 2023 + `yang2025mfdeeponet` LF-pretrain → HF-finetune-with-frozen-LF protocol to `fno_mf_stack` exploits the family's structural difference from NK2-blocked designs: 4 independent `SmallFNO` modules (`models/fno_mf_stack/model.py:165-168`) coupled only through the 1×1-conv `MFRNPAggregator` MLP decouple LF supervision from the HF residual gradient path. Freezing `lf_fnos[0..2]` after a `pretrain_frac=0.40` LF-only stage frees the HF FNO + aggregator's capacity to specialize on the m=1 residual without destroying the LF representation. Fresh `Adam + CosineAnnealingLR` per stage (Lyu's load-bearing invariant against stale-momentum divergence) gates the stage transition.
- **Mutable surface:** `models/fno_mf_stack/smoke_eval.py` — SMOKE_DEFAULTS (add `pretrain_frac=0.40, stage2_freeze_lf=True`), training loop (stage gate), `compute_losses` (stage-1 LF-only / stage-2 joint), optimizer construction (`_build_opt_sched(model, p, t_max)` helper). **No `model.py` change** — `.requires_grad_(False)` invoked from `smoke_eval.py`.
- **Expected:** further Poisson −5 to −15% on top of H1 (Poisson 0.030–0.034 → 0.027–0.032); composite 0.0184–0.0205 (~60–70% of IFC-GPODE bar). **Measured against H1's banked composite, NOT cycle-010 baseline.**
- **MANDATORY DUAL kill-switch:**
  - **Absolute:** Poisson_test > 0.0594 OR Heat_test > 0.0594 → REVERT.
  - **Inter-stage:** stage-2 best_val ≥ 0.90 × stage1_best_val (i.e. stage 2 must reduce val by ≥10%); if not met, REVERT to stage-1 checkpoint and report `STAGE_2_NO_IMPROVEMENT`.
  - **Wall:** > 1800s → REVERT.
- **Wall budget:** ~1500–1700s smoke total per dataset (stage 1 ~500s LF-only; stage 2 ~1000–1200s HF+aggregator at frozen LF).
- **NK status:** **NK2 carve-out (load-bearing)** — structural difference from `fno_coregionalization`/`fno_coreg_residual` (no shared K-basis; LF stack is loss-supervised in stage 1, gradient-isolated in stage 2 with no shared params). Matches `yang2025mfdeeponet`'s freeze-branch-and-trunk + train-only-merge protocol. NK1-clear; NK3-clear (canonical MFRNP weights unchanged across stages).
- **Clears backlog:** cycle-009 close-out O3 (deferred curriculum on LF/HF-independent design with mandatory dual kill-switch).
- **Confidence:** MEDIUM-HIGH. **Branch:** `experiment/16-fno_mf_stack-curriculum-frozen-lf`.

## Anti-patterns Honored (NK1/NK2/NK3)

- **NK1 — Pure m-conditioning on HF-only FNO (cycle-008 H2 REVERT).** Neither H1 (capacity-only) nor H2 (curriculum-only) engages this axis. Both NK1-clear.
- **NK2 — Frozen-LF curricula on co-evolved residual ladders (cycle-008 H3 REVERT) — WITH PUBLISHED CARVE-OUT FOR H2.** `fno_mf_stack`'s 4 independent `SmallFNO` modules with NO shared weights is the explicit carve-out. The NK2 mechanism (shared K-basis losing joint gradient signal when LF is frozen) does not apply. Mandatory dual kill-switch (absolute + inter-stage) is the carve-out's price.
- **NK3 — MFRNP-style loss-weight transfer to coregionalization family (3/3 REVERT cycles 003/006/007).** H1 holds `poisson_hf_weight=2.0, poisson_lf_weight=0.25` UNCHANGED on `fno_mf_stack` (canonical MFRNP-native recipe; not subject to NK3's cross-family transfer pattern). H2 is loss-weight-agnostic across stages. Both NK3-clear.

## Sequencing Plan (CEO-approved)

- **Experiment 1 (H1):** branch from `experiment/14 @ 0b6e6eb` → `experiment/15-fno_mf_stack-capacity-axis-2nd-step`. SMOKE_DEFAULTS edit only. Smoke-verify with `--epochs 2`, then full smoke. Verdict against cycle-010 baseline 0.022161. `--no-github`.
- **Experiment 2 (H2):** if H1 keeps, branch from H1's banked branch → `experiment/16-fno_mf_stack-curriculum-frozen-lf`. Training loop changes. Verdict against H1's banked result. If H1 reverts, H2 still defensible (curriculum is fresh-axis-distinct from capacity).
- **DO NOT bundle.** Each hypothesis = own experiment ID, own PR, own banked-or-reverted verdict.

## Hard Gate Checklist (CEO PASS — 10/10)

- Surface constraints: H1 + H2 both touch `models/fno_mf_stack/smoke_eval.py` only.
- Leakage scan: both hypotheses `risk_level: none, flagged: false`.
- Hypothesis count: 2 (max_new=2 budget).
- NK1 sidestep: H1 capacity-only, H2 curriculum-only.
- NK2 carve-out for H2: structurally justified by `model.py:165-168` (4 independent SmallFNO modules); mandatory dual kill-switch included.
- NK3 sidestep: canonical MFRNP weights held by both.
- Operational items: N/A (both Type: code).
- Backlog adequacy: H2 fully addresses cycle-009 O3.
- No calendar-time estimates.
- Bundling caveat: explicit "DO NOT bundle" rule with attribution rationale.

## Backlog (deferred to cycle-011+)

- **O1-aggressive** — `fno_mf_stack` capacity 3rd step (hidden=128, modes=(4,8,16,24), n_blocks=5; param count ~3.5M). Pursue only if cycle-010 H1 lands net-positive AND wall comfortably <1500s.
- **O3** — Input-dependent K-basis on `fno_coregionalization × poisson` (B(m, LF_features)). NOT NK3. MANDATORY heat guard `heat_test ≤ 0.0194` if pursued.
- **O4** — NEW family `fno_coreg_conditioned_v2` with γ(m, LF_features) FiLM (NK1-safe). HIGH implementation cost (full package scaffold).
- **Adjacent literature additions to `papers_summary.csv`** (human-action; 15 ready keys: 10 prior + 5 new + `yang2025mfdeeponet` + `liu2022neuralcoreg`). arXiv ID correction: `stresstest2025fno` 2501.11428 → 2601.11428.
- **`MFRNP_AGGREGATOR_POISSON_SPECIALIZATION`** axis — ablate aggregator topology in a later cycle.

## Citations

- H1: `niu2024mfrnp`, `li2020fno`, `lyu2023mffno`, `stresstest2025fno` (arXiv:2601.11428), `mutransferfno2025` (NEW; arXiv:2506.19396), `fnospectralperspective2024` (NEW; arXiv:2404.07200).
- H2: `lyu2023mffno` (arXiv:2304.06972), `yang2025mfdeeponet` (NEW; arXiv:2503.17941), `gcs2023mffno` (arXiv:2308.09113), `pretrain_lowerdims2024` (arXiv:2407.17616), `niu2024mfrnp`.

## Related

- [[failure-analysis-cycle-010]] — dominant failure mode and per-cell classification.
- [[research-cycle-010]] — research-mode source synthesis (O1-O5).
- [[cycle-009-strategy]] — prior capacity-axis step that this hypothesis chain extends.
- [[cycle-008-summary]] — NK1 (H2) and NK2 (H3) source REVERTs that gate cycle-010 anti-pattern logic.
