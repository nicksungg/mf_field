---
name: cycle-008-strategy
description: Cycle-008 Strategy snapshot — 3 hypotheses (A1 > B1 > B3 menu). H1 = capacity bump on fno_coregionalization (paper config K=20); H2 = NEW family fno_coreg_conditioned with FiLM-via-LayerNorm; H3 = three-stage curriculum on fno_coreg_residual with mandatory recipe_hash checkpoint guard. CEO PROCEED + PLAN APPROVED.
tags:
  - factory
  - strategy
  - factory_mffp
project: factory_mffp
cycle: 008
date: 2026-06-02
source: factory-archivist
verdict: PROCEED — PLAN APPROVED
mode: research
baseline_composite: 0.030408
bar_parallel_bench: 0.027429
dethrone_target_minus10pct: 0.02469
dominant_composite_lever: fno_coregionalization × ifc_heat (12.6× log-weight)
single_family_blocker: fno_coregionalization × ifc_poisson = 0.7501
hypothesis_count: 3
hypothesis_count_cap: 3
priority_order: H1 > H2 > H3
bundling: forbidden
leakage_h1_risk_level: none
leakage_h2_risk_level: none
leakage_h3_risk_level: none
ceo_verdict_close_out: ceo-verdict-strategist.md
related:
  - cycle-007
  - failure-analysis-cycle-008
  - ceo-verdict-failure_analyst
  - ceo-verdict-researcher
---

# Strategy: factory_mffp — cycle-008 — 2026-06-02

## Verdict

**PROCEED — PLAN APPROVED** (CEO hard gate cleared).

- 3 hypotheses, all `Type: code`, all confined to `models/**`.
- All three pass `factory leakage-check` with `flagged: false, risk_level: none`.
- All six cycle-008 anti-patterns honored (see below).
- Priority order **H1 > H2 > H3** matches CEO R2 recommendation.

## Baselines

- **Reproducible baseline composite_nRMSE:** 0.030408 (current HEAD `experiment/9-fno_coregionalization-constructor-fix @ 1249f2d`).
- **Bar (`mf_fno_transfer_bar` parallel-bench composite):** 0.027429.
- **−10% dethrone target:** ≤ 0.02469.
- **Gap baseline → bar:** +10.9%; gap baseline → dethrone target: +23.2%.

## Hypotheses

### H1 — Capacity bump on `fno_coregionalization` to paper config (HIGH, EXPLOIT)

- **Failure mode:** `CAPACITY_PARETO` on `fno_coregionalization × ifc_heat` (dominant 12.6× log-weight composite lever).
- **Mutable surface:** `models/fno_coregionalization/smoke_eval.py` — `SMOKE_DEFAULTS` block only. **No `model.py` change** (cycle-007 H1 constructor repair already accepts the paper kwargs).
- **What:** Wire IFC paper `full_config.json` values into `SMOKE_DEFAULTS`:
  - `K=10 → 20`
  - `hidden_channels=32 → 128`
  - `b_hidden`: add `=128` (paper)
  - `n_blocks=4 → 6`
  - `modes_cap=12 → 16`
  - H2 LF→HF schedule (`pretrain_lr`, `finetune_lr`, `pretrain_frac`) UNCHANGED — banked from cycle-007 H2.
- **Expected per-cell delta:**
  - `ifc_heat`: 0.01551 → ~0.013 (high end ~0.012, low end ~0.014 reflects 200-epoch smoke budget).
  - `ifc_poisson`: 0.7501 → 0.5-0.7 (neutral on composite).
- **Expected composite delta:** 0.030408 → ~0.028 (high end ~0.026; low end ~0.029).
- **Kill-switch:** `ifc_heat` nRMSE > 0.0194 → REVERT. If smoke wall > 25 min on first SLURM run, drop epochs 200 → 120 with cosine warmup.
- **Wall budget:** ~12-15 min on a single H100 (within 30-min cap by ~2×).
- **Citations:** `li2022ifc` (paper K=20 config), `li2020fno`, `lyu2023mffno` (banked schedule).

### H2 — NEW family `fno_coreg_conditioned` with FiLM-via-LayerNorm (MEDIUM-HIGH, EXPLORE)

- **Failure mode:** `FAMILY_PDE_SPECIALIZATION_ASYMMETRY` on `fno_coregionalization × ifc_poisson = 0.7501` (12.61× over bar). Highest swing-EV in cycle-008 menu — only intervention that could collapse the asymmetry into a single-family answer.
- **Mutable surface:** NEW family directory `models/fno_coreg_conditioned/`:
  - `model.py`, `smoke_eval.py`, `manifest.json`, `INSPIRATION.md`
- **What:**
  - **Mode A (preferred):** Re-use anisotropic-modes `FNOBlock` from `models/mf_fno_transfer_bar/model.py:62-94`. Replace each `GroupNorm` with `FiLMNorm(channels, m_feat_dim)` that computes `γ(m), β(m) = MLP([m, m²])` and outputs `γ * GroupNorm(z) + β`. Output is HF prediction directly — no K-dim outer-product basis. Constructor MUST mirror cycle-007 H1 anisotropic-modes pattern (positional `modes` accepts `int` or `(modes_h, modes_w)`).
  - **Mode B (fallback):** Concatenate `B(m) ∈ R^K` (broadcast spatially) to FNO input channels; no FiLM modulation.
  - `smoke_eval.py`: copy from `fno_coregionalization` verbatim, preserving the H2 LF→HF schedule. Strip K/b_hidden, add `m_feat_dim=32`.
  - `INSPIRATION.md` MUST cite five papers verbatim with bibtex_keys: `li2022ifc`, `li2020fno`, `lyu2023mffno`, `beggs2025pdecond`, `herde2024poseidon`.
- **Backlog cleared:** Verbatim `siren_film_fidelity` (SIREN/FilmNet conditioned on fidelity index, residual ladder LF→HF) AND NEW DIRECTIVE (2026-05-31) seed (b) ("single full-resolution HF FNO conditioned on coregionalization-m basis"). Full adequacy on both.
- **Expected per-cell delta:**
  - `ifc_heat`: 0.01551 → 0.015-0.025 (speculative; FiLM matches or loses to current K=10 basis).
  - `ifc_poisson`: 0.7501 → 0.05-0.15 (closes most of 12.61× bar gap IF FiLM captures m-modulation).
- **Expected composite delta:** 0.030408 → 0.022-0.040 (wide; full-spectrum upside/downside).
- **Kill-switch:** (i) smoke wall > 25 min → REVERT; (ii) `ifc_heat` > 0.0194 → REVERT.
- **Wall budget:** ~10-15 min/cell on H100; total ~25 min (close to cap — kill-switch (i) catches overrun).
- **Citations:** `li2022ifc`, `li2020fno`, `lyu2023mffno`, `beggs2025pdecond` (FiLM-via-LayerNorm for PDE-parameter conditioning, arXiv:2509.09599), `herde2024poseidon` (Poseidon scOT time-conditioned LayerNorm, NeurIPS 2024, arXiv:2405.19101).

### H3 — Three-stage curriculum on `fno_coreg_residual` with mandatory `recipe_hash` checkpoint guard (MEDIUM, EXPLOIT + EXPLORE)

- **Failure mode:** `TRANSFER_SIGNAL_UNUSED` on `fno_coreg_residual × ifc_heat` (H2 schedule never applied to this family) + `RECIPE_DATASET_NONPORTABILITY` on Poisson. Schedule lever, NOT recipe lever.
- **Mutable surface:** `models/fno_coreg_residual/smoke_eval.py` ONLY (BasisHead in `model.py:43-188` unchanged).
- **What — three independent curriculum stages with uniform loss weights:**
  - **Stage 1 (LF pretrain, ~50 epochs at default 200 cap):** train per-fidelity LF FNOs on LF-only samples (m != hf_m), `pretrain_lr=1e-3`, fresh Adam + cosine. NO MFRNP weighting.
  - **Stage 2 (HF residual fine-tune, ~100 epochs):** freeze LF stack. Train HF FNO residual at `finetune_lr=3e-4`. BasisHead remains zero-init and frozen.
  - **Stage 3 (basis-head unfreeze, ~50 epochs):** unfreeze BasisHead AND LF stack. All params at `finetune_lr × 0.3 = 9e-5` (cycle-003 BasisHead instability prior).
- **MANDATORY recipe_hash checkpoint guard:** Hash `SMOKE_DEFAULTS` + `stage_strides` via `hashlib.sha256(json.dumps({**SMOKE_DEFAULTS, "stage_strides": [0.25, 0.5, 0.25]}, sort_keys=True).encode()).hexdigest()[:16]`; write as `recipe_hash` field in saved checkpoint. Resume guard requires `recipe_hash` match in addition to existing `epoch == epochs_target AND cond_dim match`. **Without this guard, H3 inherits cycle-003 H1 contamination failure (SLURM 13973868 stale-resume 33 s "train" vs SLURM 13974837 clean rerun 549 s).**
- **Backlog cleared:** Verbatim cycle-003 H1 checkpoint-resume contamination item. Side-effect: META-VALIDITY IMPROVEMENT FOR ALL FUTURE RESEARCH-MODE EXPERIMENTS.
- **Expected per-cell delta:**
  - `ifc_heat`: 0.02628 → 0.018-0.022 (Stage 2 frozen-LF fine-tune + Stage 3 basis modulation).
  - `ifc_poisson`: 0.07419 → 0.05-0.06 (recovers cycle-005 0.05556 paper-recipe number or better).
- **Expected composite delta:** 0.030408 → ~0.029-0.033 (modest single-cycle; primary value is the recipe_hash guard).
- **Kill-switch:** Stage 3 regresses Heat by > +25% over Stage 2 checkpoint → REVERT to Stage 2 (do not re-add basis head). Also universal `ifc_heat` > 0.0194 over Stage 1 baseline.
- **Wall budget:** ~6 min on H100 (same total as current single-stage; redistributed across three stages).
- **Citations:** `niu2024mfrnp`, `lyu2023mffno`, `li2022ifc`, `yang2025mfdeeponet`, `engstruct2025mfft` (ScienceDirect S0141029625016098 — pretrain-finetune NO for multi-fidelity surrogate of structural dynamic systems, new cycle-008 web hit).

## Independence Check

- H1 → `models/fno_coregionalization/smoke_eval.py`
- H2 → NEW `models/fno_coreg_conditioned/{model.py, smoke_eval.py, manifest.json, INSPIRATION.md}`
- H3 → `models/fno_coreg_residual/smoke_eval.py`

**Zero file overlap.** All three branchable independently. Bundling forbidden (CEO directive R2 §3).

## Anti-patterns Honored (cycle-008-binding, all six)

1. **MFRNP loss-recipe / reweighting (HF=2.0, LF=0.25) — BANNED.** 3/3 REVERTs (cycle-003 H1, cycle-006 H1, cycle-007 H2). H1 = capacity-only; H2 = architecture-only; H3 = schedule-redistribution only with uniform weights.
2. **Per-dataset MFRNP recipe dispatch — BANNED.** REVERTed in cycle-007 H2 ("Heat invariant by construction" falsified at 6.5× noise band). H3 explicitly says "do NOT add MFRNP weighting".
3. **A1+B1+B3 bundling — FORBIDDEN.** Three independent code paths, three different family directories, no shared file edits.
4. **D1 (`mf_fno_transfer_bar` smoke-config bump) — DEFERRED.** Would raise the bar we must beat; counterproductive until smoke composite is already below parallel-bench bar.
5. **A3 (F-FNO factorized spectral conv refactor) — DEFERRED.** Full-family-scale change; no IFC-specific evidence; A1 is tighter for cycle-008 budget. Deferred to cycle-009+ as `fno_coreg_ffno`.
6. **`models/fno_coregionalization/model.py` edits for H1 — FORBIDDEN.** Cycle-007 H1 constructor already accepts all paper kwargs. Builder restricted to `SMOKE_DEFAULTS` only.

## Leakage-Check Receipts

- **H1:** `flagged: false, risk_level: none`
- **H2:** `flagged: false, risk_level: none`
- **H3:** `flagged: false, risk_level: none`

## Builder Instructions (R3)

- Process sequentially: H1 → H2 → H3 (each on its own experiment branch off `experiment/9-fno_coregionalization-constructor-fix @ 1249f2d`).
- For each: read issue, read CLAUDE.md and factory.md, branch, implement exactly per hypothesis, run smoke eval, commit, **do NOT push** (`--no-github` active).
- **H1 verify:** `--epochs 2 --dataset_dir data/ifc_heat --out /tmp/x.json --ckpt_dir /tmp/c --seed 0` before declaring ready.
- **H2 verify:** smoke_eval.py runs end-to-end on BOTH `ifc_heat` AND `ifc_poisson` before declaring ready (cycle-007 H1 constructor lesson).
- **H3 verify:** implement recipe_hash guard FIRST as standalone change; verify it correctly rejects mismatched checkpoints BEFORE adding three-stage logic.

## Cycle-009+ Backlog (new items)

- `fno_coreg_ffno` — A3 (F-FNO factorized spectral conv refactor) as NEW sibling family. `tran2023ffno` (ICLR 2023, arXiv:2111.13802; reported 31-85% error reduction).
- `fno_coreg_mflno` — Cao et al. 2025 (`cao2025mflno`, arXiv:2502.00550) linear+nonlinear residual decomposition. Direct alternative to B1 if FiLM under-fits Poisson.
- `mf_fno_transfer_bar` smoke-config bump (D1) — defer until smoke composite is decisively below the parallel-bench bar.
- `fno_mf_stack` capacity bump (C1) — `hidden=32→64`, `n_blocks=3→4`, `modes=(4,8,12,12)→(8,12,16,16)`. Secondary composite contributor; stackable on cycle-008 outcomes.

## Related Memories

- [[cycle-007]] — committed-tree-broken predecessor; H1 constructor repair and H2 LF→HF schedule banked into cycle-008 H1's no-op baseline.
- [[cycle-006]] — MFRNP recipe REVERT (anti-pattern lineage).
- [[cycle-003]] — checkpoint-resume contamination origin (H3 mandatory recipe_hash guard pays this off).
