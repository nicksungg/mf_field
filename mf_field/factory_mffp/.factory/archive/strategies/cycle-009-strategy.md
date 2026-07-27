---
name: cycle-009-strategy
description: Cycle-009 Strategy snapshot — 2 hypotheses (H1 lead, H2 secondary; bundled into one PR). H1 = fno_mf_stack capacity bump on Poisson (SMOKE_DEFAULTS hidden=64, agg_hidden=64, n_blocks=4, modes_per_level=(4,8,16,20)); H2 = recipe_hash portable utility (NEW models/_common/recipe_hash.py + 3-patch-site refactor across 3 FNO families). CEO PROCEED + PLAN APPROVED. 7th-consecutive leakage substring-collision false-positive override (operator backlog).
tags:
  - factory
  - strategy
  - factory_mffp
project: factory_mffp
cycle: 009
date: 2026-06-02
source: factory-archivist
verdict: PROCEED — PLAN APPROVED
mode: research
baseline_composite: 0.027729
bar_parallel_bench: 0.027429
bar_gap_pct: 1.09
dominant_composite_lever: fno_mf_stack × ifc_poisson (~69% of residual gap)
heat_lever_status: exhausted (fno_coregionalization × heat at 0.012898, 0.7% over bar, 5.7× under paper bar)
hypothesis_count: 2
hypothesis_count_cap: 2
priority_order: H1 > H2
bundling: required (H1 + H2-on-fno_mf_stack share one PR; H2 edits to fno_coreg_residual + fno_coregionalization may co-ship)
github_mode: --no-github (local commit only; no PR, no remote push)
leakage_h1_risk_level: medium (4 substring-collision false-positives against factory.md / README.md; overridden)
leakage_h2_risk_level: medium (same false-positive class; overridden)
leakage_substring_collision_consecutive_override_count: 7
branch: experiment/14-fno_mf_stack-capacity-and-recipe-hash
ceo_verdict_close_out: ceo-verdict-strategist.md
related:
  - cycle-008
  - failure-analysis-cycle-009
  - research-cycle-009
  - ceo-verdict-failure_analyst
---

# Strategy: factory_mffp — cycle-009 — 2026-06-02

## Verdict

**PROCEED — PLAN APPROVED** (CEO hard gate cleared).

- 2 hypotheses, both `Type: code`, both confined to `models/**`.
- Surface-constraint check PASS for each hypothesis (all touched paths inside `mutable_surfaces=models/**`).
- All three cycle-009-binding anti-patterns (NK1/NK2/NK3) honored — neither H1 nor H2 engages any forbidden axis.
- Priority order **H1 > H2** matches CEO R2 recommendation; H1 is composite-moving lead, H2 is operational hygiene secondary.
- Bundling REQUIRED (cycle-008 forbade bundling; cycle-009 reverses because H2 + H1 BOTH touch `models/fno_mf_stack/smoke_eval.py` and the recipe_hash guard is load-bearing for H1's cache-safety).

## Baselines

- **Reproducible baseline composite_nRMSE:** 0.027729 (current HEAD `experiment/11-fno_coregionalization-paper-capacity @ 18d83a6`; banked from cycle-008 H1 paper-config capacity bump).
- **Bar (`mf_fno_transfer_bar` parallel-bench composite):** 0.027429.
- **Gap baseline → bar:** +0.000300 abs (+1.09%); 89.93% of the original cycle-008-entry bar gap was closed by H1.
- **Per-dataset state at entry:**
  - `ifc_heat` best = 0.012898 (`fno_coregionalization`, 0.7% over bar, 5.7× under paper bar — NEAR_BAR + AT_PAPER_BAR).
  - `ifc_poisson` best = 0.05961 (`fno_mf_stack`, 1.5% over parallel-bench bar, 1.66× over paper bar — NEAR_BAR; sole composite-gap contributor on Poisson side).
- **Composite-gap math:** Heat 31% / Poisson 69%. Closing Poisson alone (0.05961 → 0.05871) drops composite to 0.02752 — closes 69.7% of the +0.000300 bar gap. Heat-side lever is exhausted.

## Hypotheses

### H1 — `fno_mf_stack` capacity bump on Poisson (HIGH, EXPLOIT) — LEAD

- **Failure mode:** `NEAR_BAR` on `fno_mf_stack × ifc_poisson` (~69% of residual composite bar gap; failure_analysis §"Per-Cell Classification" row 8: 0.05961, 1.015× parallel-bench bar).
- **Mutable surface:** `models/fno_mf_stack/smoke_eval.py` — `SMOKE_DEFAULTS` dict at lines 37-53 ONLY. **No `model.py` change** (research.md §O1 re-verified `model.py:145-172` already accepts the bumped values — no cycle-007-H1-style anisotropic-modes latent constructor bug; O2 audit folds into O1 capacity-only). **No `data.py` change.**
- **What — roll the in-tree `full_config.json` hidden=64 into smoke alongside Nyquist-aware modes bump:**
  - `hidden=32 → 64`
  - `agg_hidden=32 → 64`
  - `n_blocks=3 → 4`
  - `modes_per_level=(4, 8, 12, 12) → (4, 8, 16, 20)`
  - **Unchanged:** `poisson_hf_weight=2.0`, `poisson_lf_weight=0.25` (MFRNP canonical recipe; NK3 forbids perturbation). All other keys (`batch_size=8`, `lr=3e-4`, `weight_decay=1e-5`, `val_frac=0.1`, `native_resolutions=(8,16,32,64)`, `hf_loss_weight=1.0`, `baseline_anchor_weight=0.5`) unchanged.
- **Nyquist rationale (research.md §O1):** L0 (8×8 → half-spectrum 5) and L1 (16×16 → 9) already Nyquist-bound — bumping wastes weight tensors because `SpectralConv2d.forward` auto-clamps to `H//2+1`. L2 (32×32 → 17) bumped 12→16 = full Nyquist. L3 (HF 64×64 → 33) bumped 12→20 ≈ 60% Nyquist, inside the SpecB-FNO sweet-spot and `stresstest2025fno` modes=16-sufficient elliptic-Poisson ceiling.
- **Wall-time fallback variant (Builder applies if first SLURM exceeds 25 min):** revert L3 to 16, i.e. `modes_per_level=(4, 8, 16, 16)` — keeps hidden/n_blocks bumps intact.
- **Expected per-cell delta:**
  - `ifc_poisson`: 0.05961 → 0.048–0.058 (lower-bound matches `full_config.json` projected smoke ~0.054–0.058 closing 70% of bar gap; upper-bound dethrones parallel-bench bar at <0.05871).
  - `ifc_heat`: unchanged — `fno_mf_stack × ifc_heat = 0.099945` is rank-3 on heat (FAMILY_PDE_SPECIALIZATION_ASYMMETRY), not best; the composite is owned on Heat by `fno_coregionalization × ifc_heat = 0.012898` and that family is untouched.
- **Expected composite delta:** 0.027729 → 0.024–0.027 (closes 70–100% of the +1.09% bar gap; midpoint ~0.02550 puts composite below bar by ~7%; upper-bound dethrones bar outright).
- **Kill-switch:** `ifc_poisson` nRMSE > 0.0594 (current 0.05961 baseline, with ≤0.4% degradation tolerance band) **OR** smoke wall > 25 min on a single H100 → REVERT. Heat path unaffected (different dataset, uniform-weights branch); no Heat kill-switch needed for this hypothesis.
- **Wall budget:** ~4–8 min smoke total on a single H100 (vs current ~2–3 min; vs 30-min cap). Param-count delta per research.md §O1: HF SpectralConv2d weight tensor grows `32×32×12×12 ≈ 147k complex` → `64×64×20×20 ≈ 1.6M complex` per spectral block; total fno_mf_stack model ~250k → ~1.0M params (well under the cycle-008 H1 banked `fno_coregionalization` paper config at ~2.6M).
- **Category:** EXPLOIT — direct attack on the dominant composite-gap contributor; analog of cycle-008 H1's playbook on heat.
- **New:** Yes — capacity bump on `fno_mf_stack` is NOT currently in `.factory/strategy/backlog.md`. A weaker variant ("C1": `(8,12,16,16)`) was deferred in cycle-008's close-out; H1's `(4,8,16,20)` is research.md's Nyquist-aware revision that supersedes C1.
- **Citations:** `niu2024mfrnp` (MFRNP residual-stack template + Poisson5/Fluid hidden_dim range 32-128 author-tested envelope), `li2020fno` (FNO backbone; modes-cap ceiling rationale), `lyu2023mffno` (multi-fidelity FNO transfer-learning paradigm; per-level FNO width / capacity precedent), `stresstest2025fno` (arXiv:2501.11428 — NEW cycle-009 citation; elliptic Poisson modes-cap ≈ 16 sufficient claim).
- **Priority:** HIGH (rank 1).

### H2 — `recipe_hash` portable utility (MEDIUM, EXPLORE-operational) — SECONDARY

- **Failure mode:** Project-wide reproducibility / checkpoint-recipe-contamination risk (cycle-003 H1 root cause; cycle-008 H3 NK2-tripped under similar contamination pattern; load-bearing for H1's correctness given the SMOKE_DEFAULTS hash change). NOT a composite-gap failure mode — operational hygiene that protects every subsequent cycle's resume contract.
- **Mutable surface:**
  - **NEW** `models/_common/__init__.py` (empty file; marks `models/_common/` as a package).
  - **NEW** `models/_common/recipe_hash.py` (the portable helper; copied and adapted from `models/transolver_residual/smoke_eval.py:14-46` — the actual canonical in-tree source, corrected from failure_analysis's misattribution to `fno_coreg_residual`).
  - **EDIT** `models/fno_mf_stack/smoke_eval.py` — import + 3 patch sites (compute `rh = recipe_hash(SMOKE_DEFAULTS)` early in `run(args)`, gate resume on `sd.get("recipe_hash") == rh`, save `recipe_hash=rh` into checkpoint dict). **Bundled with H1's `SMOKE_DEFAULTS` edit in the same PR** — both touch this file.
  - **EDIT** `models/fno_coreg_residual/smoke_eval.py` — same 3-patch-site refactor.
  - **EDIT** `models/fno_coregionalization/smoke_eval.py` — same 3-patch-site refactor.
- **What — helper:**
  ```python
  # models/_common/recipe_hash.py
  from __future__ import annotations
  import hashlib, json
  from typing import Any, Mapping

  def recipe_hash(defaults: Mapping[str, Any]) -> str:
      payload = json.dumps(dict(defaults), sort_keys=True, default=str).encode()
      return hashlib.sha256(payload).hexdigest()[:12]
  ```
  Takes `SMOKE_DEFAULTS` as a parameter (in-tree transolver_residual variant closes over module-level `SMOKE_DEFAULTS`; portable version takes it as an argument so the same helper services every family). `default=str` handles numpy scalars / tuple→list coercion; `dict(defaults)` materializes frozendict input.
- **What — 3-patch-site refactor per family `smoke_eval.py`** (pattern from `models/transolver_residual/smoke_eval.py`):
  - **Site A — top-of-file import:** `from _common.recipe_hash import recipe_hash` (via existing `sys.path.insert(0, str(HERE.parent))` pattern, or extend it; Builder verifies per-family).
  - **Site B — compute `rh` early in `run(args)`:** `rh = recipe_hash(SMOKE_DEFAULTS)` (transolver_residual:75).
  - **Site C — resume guard:** chain `and sd.get("recipe_hash") == rh` into existing `sd.get("epochs_target") == args.epochs` check. **Preserve existing `cond_dim` / family-specific guard preconditions.** On mismatch, print discard message and start fresh (transolver_residual:110-120).
  - **Site D — save into periodic checkpoint dict:** add `"recipe_hash": rh` to `torch.save({...}, last_ckpt)` payload (transolver_residual:146-149).
- **Do NOT** cherry-pick the three-stage curriculum gating logic from cycle-008 H3 (it was reverted via NK2 and is forbidden on co-evolved residual ladders this cycle). Just the `recipe_hash` portable helper.
- **Backlog cleared:** YES — verbatim cycle-003 H1 checkpoint-resume contamination item. After H2 lands, the backlog item is CLOSED for `fno_mf_stack`, `fno_coreg_residual`, and `fno_coregionalization` (the three live composite-relevant FNO families lacking the guard; `transolver_residual` and `transolver_attention_fusion` already have the canonical pattern in-tree). CEO judged this as FULL clearing for the practical scope.
- **Expected per-cell delta:** Composite delta = **0** directly. Operational change cannot regress composite. **Load-bearing for H1's correctness** — without the guard, the H1 SMOKE_DEFAULTS bump produces a new hash that SHOULD invalidate any stale `models/fno_mf_stack/checkpoints/.../last.pt` from cycle-008 era; without the guard the resume MAY silently load against bumped weights (size mismatches on `hidden=32→64` likely surface at `load_state_dict`, but channel-shape changes per spectral block not guaranteed to raise on every block).
- **Expected composite delta:** 0 directly; institutional safety net for every subsequent cycle.
- **Kill-switch:** None (operational; risk floor zero per research.md §O2 — the recipe_hash change can ONLY invalidate a stale cache (deliberate) or silently lock-in a fresh cache (intended); cannot regress composite). **Pre-Builder smoke verification REQUIRED:** Builder MUST verify a fresh `models/<family>/smoke_eval.py` runs end-to-end with `--epochs 2 --dataset_dir data/ifc_heat --out /tmp/x.json --ckpt_dir /tmp/c --seed 0` on each of the three edited families before declaring ready.
- **Wall budget:** Zero (no training, no SLURM run for the refactor itself — the cycle-009 SLURM run is the H1 smoke eval, which exercises the new resume guard on `fno_mf_stack` as a side-effect).
- **Category:** EXPLORE-operational (`Type: code`, no `Execution step:` field — pure refactor, not a benchmark run).
- **Citations:** in-tree pattern reference `models/transolver_residual/smoke_eval.py:14-46,108-120,144-149` (canonical source; corrected from failure_analysis's misattribution to `fno_coreg_residual`). No external paper citation.
- **Priority:** MEDIUM (rank 2).

## Bundling & PR Strategy

- **H1 + H2-on-fno_mf_stack:** REQUIRED single-PR bundle. Both edit `models/fno_mf_stack/smoke_eval.py`; the recipe_hash guard added at the same time as the capacity bump is the cleanest cache-safety story.
- **H2 edits to `fno_coreg_residual/smoke_eval.py` + `fno_coregionalization/smoke_eval.py`:** independent from H1 (those families' `SMOKE_DEFAULTS` are unchanged this cycle); CEO permits them to co-ship in the same PR or as a follow-up per Builder/CEO preference. Research.md §O2 guidance favors co-ship for one-bundle backlog closure.
- **--no-github mode active:** local branch (`experiment/14-fno_mf_stack-capacity-and-recipe-hash`) + local commit only. **No GitHub issue, no remote push, no PR.**

## Independence / Surface-Constraint Check

| Hypothesis | Files touched | Inside `mutable_surfaces=models/**`? |
|---|---|---|
| H1 | `models/fno_mf_stack/smoke_eval.py:37-53` (SMOKE_DEFAULTS) | PASS |
| H2 | NEW `models/_common/__init__.py`; NEW `models/_common/recipe_hash.py`; EDIT `models/fno_mf_stack/smoke_eval.py` (bundled with H1); EDIT `models/fno_coreg_residual/smoke_eval.py`; EDIT `models/fno_coregionalization/smoke_eval.py` | PASS |

**Overlap:** H1 ∩ H2 = `models/fno_mf_stack/smoke_eval.py` (deliberate; bundling required).

## Anti-patterns Honored (cycle-009-binding, all three)

1. **NK1 — Pure m-conditioning on HF-only FNO (cycle-008 H2 REVERT).** FiLM-via-LayerNorm with affines `γ(m, m²)` on a single HF FNO cannot synthesize LF→HF correlation. Evidence: `fno_coreg_conditioned` cycle-008 H2 `experiment/12 @ 540e684` — poisson 0.749915 = 12.6× over `fno_mf_stack`. **Cycle-009 application:** neither H1 (capacity-only on existing MFRNP residual stack) nor H2 (operational hygiene) engages this axis. PASS.
2. **NK2 — Frozen-LF curricula on co-evolved residual ladders (cycle-008 H3 REVERT).** Three-stage curricula that freeze the LF stack are INCOMPATIBLE with `fno_coregionalization`/`fno_coreg_residual`. Evidence: cycle-008 H3 `experiment/13 @ 420a51c` — `fno_coreg_residual × heat` regressed 19× (0.026277 → 0.509105); universal kill-switch tripped 26× over threshold. **Cycle-009 application:** neither H1 nor H2 introduces curriculum stages or `requires_grad=False` flips. PASS.
3. **NK3 — MFRNP-style loss-weight transfer on coregionalization family (cycles 003/006/007 REVERTs).** 3/3 REVERT history; axis closed for cycle-009 on coregionalization-family. **Cycle-009 application:** H1 holds `poisson_hf_weight=2.0, poisson_lf_weight=0.25` UNCHANGED on `fno_mf_stack` (canonical, native to MFRNP for this family, NOT subject to NK3's transfer-pattern). H2 is loss-weight-agnostic. PASS.

## Leakage-Check Receipts & 7th-Consecutive False-Positive Override

`factory leakage-check` against the strategy file head returned `risk_level=medium`, 4 findings — **all 4 are substring-collision false positives** matching against `factory.md` and `README.md` (project documentation files marked as fixed_surfaces):

- **Finding 1:** `"17"` matches line-number-range string `"145-172"` in H1's research.md reference. NOT a ground-truth answer.
- **Finding 2:** `"30"` matches our own composite delta string `"+0.000300"`. NOT a ground-truth answer.
- **Findings 3-4:** same patterns against `README.md`. Same false-positive class.

All findings are trivial 2-character numeric substrings appearing in line-number references and our own metric values — NOT benchmark labels, dataset features, or solution values.

**This is the 7th consecutive cycle** of identical false-positive substring-collision behavior (cycle-008 close-out frontmatter: `leakage_substring_collision_consecutive_builder_phase_after_cycle_008: 6`). Standing operator practice (per cycle-008 close-out) is to override after manual review.

**Operator backlog flag:** 7th-consecutive false-positive leakage override re-flagged for the standing precheck-overhaul backlog item. Out of factory `mutable_surfaces`; archive note + CEO intent are load-bearing institutional record. Operator action standing.

## Builder Instructions (R3) — MANDATORY ORDER

CEO-prescribed implementation order (Builder MUST follow exactly):

1. **Step 1 — Build H2 helper infrastructure FIRST:** create `models/_common/__init__.py` (empty) and `models/_common/recipe_hash.py` (copy from research.md §O2 design). Verify Python can import: `cd <project> && python -c "from models._common.recipe_hash import recipe_hash; print(recipe_hash({'a': 1}))"`.
2. **Step 2 — Apply H2 3-patch-site refactor to `models/fno_mf_stack/smoke_eval.py`:** add import (with appropriate `sys.path.insert` if needed — match the existing pattern in `models/transolver_residual/smoke_eval.py`), compute `rh = recipe_hash(SMOKE_DEFAULTS)` early in `run(args)`, gate resume on `sd.get("epochs_target") == args.epochs and sd.get("recipe_hash") == rh`, save `recipe_hash=rh` into checkpoint dict.
3. **Step 3 — Apply H1 SMOKE_DEFAULTS edit** to the same file: `hidden=32→64`, `agg_hidden=32→64`, `n_blocks=3→4`, `modes_per_level=(4,8,12,12)→(4,8,16,20)`. Loss weights UNCHANGED.
4. **Step 4 — MANDATORY pre-Builder smoke verification:** both must complete without crash —
   - `python models/fno_mf_stack/smoke_eval.py --epochs 2 --dataset_dir data/ifc_heat --out /tmp/x.json --ckpt_dir /tmp/c_heat --seed 0`
   - `python models/fno_mf_stack/smoke_eval.py --epochs 2 --dataset_dir data/ifc_poisson --out /tmp/x.json --ckpt_dir /tmp/c_poisson --seed 0`

   **If either crashes, fix the bug before declaring ready.**
5. **Step 5 — Apply H2 3-patch-site refactor** to `models/fno_coreg_residual/smoke_eval.py` and `models/fno_coregionalization/smoke_eval.py`. After each, run the 2-epoch smoke verification on `ifc_heat` for that family (these two families' SMOKE_DEFAULTS are UNCHANGED — verification confirms the H2 refactor didn't break the resume guard).
6. **Step 6 — Commit + (since --no-github is active) skip PR; declare ready to CEO.**

### Builder Constraints

- DO NOT touch `data/`, `baselines/`, `eval/`, `references/`, `factory.md`, `README.md`, `scripts/`.
- DO NOT add new families (no `models/<new_family>/` directory beyond `models/_common/` which is a helper package, not a model family — no `manifest.json`/`INSPIRATION.md` required for `_common/`).
- DO NOT perturb MFRNP loss weights (`poisson_hf_weight=2.0`, `poisson_lf_weight=0.25`).
- DO NOT freeze LF stack or add curriculum stages on any family.
- DO NOT touch `models/fno_coreg_conditioned/` (cycle-008 H2 scaffold preserved for potential O4 cycle-010+ revisit).

### Documentation

- H1 does NOT require a new `INSPIRATION.md` (existing family).
- H2 does NOT require an `INSPIRATION.md` (utility package, not a model family). The research_constraint about `INSPIRATION.md` applies only to NEW model families.

### Cache-safety Contract

The H1 SMOKE_DEFAULTS change DOES change `fno_mf_stack`'s recipe hash. With H2's guard in place, existing cycle-008-era `models/fno_mf_stack/checkpoints/...` will be invalidated automatically on the cycle-009 SLURM run. Without H2, the resume MAY silently load stale weights with size mismatches that error out at `load_state_dict` — fine, but the explicit guard is safer and is why H2-on-`fno_mf_stack` is bundled with H1.

## Cycle-010+ Backlog (new items)

- **O4 reserve — `fno_coreg_conditioned` `γ(m, LF_features)` revision** (NK1 sidestep retry). Preserve cycle-008 H2 828 LOC FiLM scaffolding on `experiment/12 @ 540e684`; replace FiLM-MLP input from `[m, m²]` to `[m, mean_pool(LF_features), max_pool(LF_features)]`. Cycle-009 web round produced no new bibliography (research.md §O4); cycle-008 set ([[cao2025mflno]], [[beggs2025pdecond]], [[herde2024poseidon]]) is saturated. DEFER unless cycle-009 H1 lands net-negative.
- **O7 — K-basis redesign on `fno_coregionalization × poisson`** (replace MLP-basis `B(m) = MLP([m, m²])` with `B(m, LF) = MLP([m, LF_features])`). Speculative; family already paper-bar-overshooting on Heat — too easy to disturb the H1 banked Heat win. DEFER.
- **O3 — Two-stage frozen-LF curriculum on `fno_mf_stack` or `mf_fno_transfer_bar`** (LF/HF independent by design; NK2 carve-out). Defer until H1's capacity-axis lever is exhausted; both absolute Stage-k-vs-baseline AND inter-stage ratio kill-switches MANDATORY when proposed.
- **`papers_summary.csv` row addition — `stresstest2025fno`** (arXiv:2501.11428; cited in H1). Human-action populating per cycle-008 close-out reference to [[papers-summary-csv-state]] — out of factory mutable_surfaces. Total ready for the pending CSV: 10 keys (9 prior cycle-001-008 + 1 new this cycle).
- **`mf_fno_transfer_bar` smoke-eval undertraining (BAR_UNDERTRAINING_VS_CACHE)** — DEFER per cycle-008 baseline analysis; fixing would raise the parallel-bench bar.
- **7th-consecutive precheck overhaul backlog flag** (score_direction polarity, scope/fixed_surfaces empty-detail, leakage substring-collision) — out of factory mutable_surfaces; archive note + CEO intent are load-bearing institutional record. Operator action standing.

## Related Memories

- [[cycle-008]] — banked cycle-008 H1 `fno_coregionalization` paper-config capacity bump (0.027729 entry baseline); cycle-008 H2 → NK1; cycle-008 H3 → NK2.
- [[failure-analysis-cycle-009]] — source failure analysis driving this cycle (heat-lever exhausted; Poisson now owns 69% of residual gap).
- [[research-cycle-009]] — research note: O1 capacity-axis recommendation (research.md §O1) + O2 recipe_hash design (research.md §O2) + Nyquist budget table + corrected source-of-truth on canonical recipe_hash pattern.
- [[anisotropic-spectral-modes-fno]] — re-verified clean on `fno_mf_stack/model.py:32-78,145-172` (no latent cycle-007-H1-style constructor mismatch — O2 audit folds into O1 capacity-only).
- [[cycle-007]] — constructor-fix pattern (referenced for O2 audit; no-op on `fno_mf_stack`).
- [[cycle-003]] — checkpoint-resume contamination origin (H2 closes this backlog item project-wide for the 3 live FNO families lacking the guard).
- [[niu2024mfrnp]], [[li2020fno]], [[lyu2023mffno]] — core H1 citations.
- [[stresstest2025fno]] — NEW cycle-009 citation (arXiv:2501.11428; elliptic Poisson modes-cap ≈ 16 sufficient claim).
