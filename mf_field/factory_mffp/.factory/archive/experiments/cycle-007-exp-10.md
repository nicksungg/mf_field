---
name: cycle-007-exp-10
description: Cycle-007 H2 (exp 10) full lifecycle — Per-dataset MFRNP recipe dispatch for fno_coreg_residual. R4 result composite_nRMSE 0.039578 → 0.044470 (+12.36% REAL REGRESSION). fno_coreg_residual/ifc_heat regressed 0.02628 → 0.03487 (+32.70%) — Strategist's "Heat path invariant by construction" claim empirically FALSEd. fno_coreg_residual/ifc_poisson improved 0.07419 → 0.06087 (-17.96%) — real material gain but did not take leaderboard from fno_mf_stack 0.05961. Heat leaderboard flipped fno_coreg_residual → mf_fno_transfer_bar 0.03317. Poisson kill-switch (>0.089) NOT tripped. CEO formal verdict = REVERT (substantive, not bookkeeping); branch experiment/10-fno_coreg_residual-dataset-recipes @ 87f65b1 PRESERVED. Distinguishable from H1 revert_bookkeeping_keep_intent — H2 composite genuinely regressed; H1 composite genuinely improved. Both Builder + Reviewer phases PROCEEDed cleanly with single-file +29/-0 LOC additive commit — the failure is at the *experiment hypothesis* layer, not the build hygiene layer. Key cross-cycle pattern surfaced: "fresh-train variance can swamp claimed invariance — code-path equivalence does not imply numerical equivalence when fresh trains are involved."
metadata:
  type: experiment
tags:
  - factory
  - experiment
  - factory_mffp
  - cycle-007
  - h2
  - fno_coreg_residual
  - mfrnp
  - dataset-recipes
  - poisson-recipe
  - heat-invariance-violated
  - revert-genuine
  - fresh-train-variance
  - invariance-falsified
project: factory_mffp
experiment_id: "010"
cycle: cycle-007
hypothesis_id: H2
verdict: revert
verdict_type: substantive
ceo_intent: revert
formal_verdict: revert
ceo_intent_rationale: composite genuinely regressed +12.36%; Heat invariance claim empirically false (+32.70% on ifc_heat); Heat leaderboard lost to mf_fno_transfer_bar; Poisson gain (-17.96%) did not take leaderboard from fno_mf_stack
formal_verdict_rationale: same as intent — this is a real revert, not a precheck bookkeeping artifact
score_before: 0.039578
score_after: 0.044469863562733095
score_delta: 0.004891863562733093
score_delta_pct: 12.36
score_polarity: lower_is_better
metric: composite_nRMSE
ifc_heat_best_before: 0.02628
ifc_heat_best_after: 0.033174688880908174
ifc_heat_best_family_before: fno_coreg_residual
ifc_heat_best_family_after: mf_fno_transfer_bar
ifc_heat_best_delta_pct: 26.24
ifc_heat_leaderboard_flipped: true
ifc_poisson_best_before: 0.05961
ifc_poisson_best_after: 0.05961
ifc_poisson_best_family_before: fno_mf_stack
ifc_poisson_best_family_after: fno_mf_stack
ifc_poisson_best_delta_pct: 0.0
ifc_poisson_leaderboard_flipped: false
fno_coreg_residual_ifc_heat_before: 0.02628
fno_coreg_residual_ifc_heat_after: 0.03487293894936765
fno_coreg_residual_ifc_heat_delta_pct: 32.70
fno_coreg_residual_ifc_heat_invariance_band_pct: 5.0
fno_coreg_residual_ifc_heat_invariance_violated: true
fno_coreg_residual_ifc_poisson_before: 0.07419
fno_coreg_residual_ifc_poisson_after: 0.06086576400250346
fno_coreg_residual_ifc_poisson_delta_pct: -17.96
fno_coreg_residual_ifc_poisson_cycle_005_target: 0.05556
fno_coreg_residual_ifc_poisson_vs_target_pct: 9.55
fno_coreg_residual_fresh_train_cache_hash_h2: 528438a274db
fno_coreg_residual_fresh_train_cache_hash_h2_heat: 0.03487
fno_coreg_residual_fresh_train_cache_hash_h2_poisson: 0.06087
fno_coreg_residual_fresh_train_cache_hash_prior_d1: 1d967ad6e54c
fno_coreg_residual_fresh_train_cache_hash_prior_d2: 780ee99ed2d8
fno_coreg_residual_fresh_train_cache_hash_prior_d2_heat: 0.03059
fno_coreg_residual_fresh_train_cache_hash_prior_d2_poisson: 0.05756
kill_switch_poisson_threshold: 0.089
kill_switch_poisson_tripped: false
kill_switch_poisson_headroom_to_threshold: 0.028
target_met_composite_le_0_0274: false
target_met_composite_short_by: 0.017070
target_aspirational_composite_le_0_029357: false
target_aspirational_short_by: 0.015113
poisson_leaderboard_winner: fno_mf_stack
heat_leaderboard_winner_post_h2: mf_fno_transfer_bar
date: 2026-06-02
branch: experiment/10-fno_coreg_residual-dataset-recipes
branch_preserved: true
parent_branch: experiment/7-fno_coreg_lf_hf_transfer
parent_commit: be36cba
commit: 87f65b15e882ae285a782d114c96fd0e96ccea10
files_changed: 1
loc_delta: "+29/-0"
target_file: models/fno_coreg_residual/smoke_eval.py
sibling_pattern_file: models/fno_mf_stack/smoke_eval.py
dispatch_recipe_poisson: "poisson_hf_weight=2.0, poisson_lf_weight=0.25"
dispatch_recipe_heat: "empty (uniform 1.0/1.0 by SMOKE_DEFAULTS)"
heat_path_bit_equivalent_claimed: true
heat_path_bit_equivalent_observed: false
heat_path_invariance_disproof_mechanism: "Cache hash 528438a274db differs from prior hashes (1d967ad6e54c, 780ee99ed2d8) due to new code lines (even though dispatch is no-op for heat). Cache MISS forced fresh retrain. Fresh-train trajectory landed at a different optimum than prior runs — variance band on this cell empirically ≥ 33%, far exceeding the 5% invariance band."
heat_gate_condition: "\"poisson\" in dataset_name.lower()"
fno_coregionalization_status_on_branch: "BROKEN (constructor TypeError on modes_h kwarg — same as R0 baseline, not introduced by H2)"
reviewer_verdict: PASS
ceo_verdict_builder: PROCEED
ceo_verdict_reviewer: PROCEED
ceo_verdict_strategist: PROCEED_PLAN_APPROVED
ceo_verdict_evaluator: PASS_REVERT
ceo_verdict_e2e: revert
builder_redirects_used: "0 of 2"
dirty_files_at_start: 15
dirty_files_committed: 0
no_github_mode: true
duration_seconds_eval: 186
substantive_revert_count_after_h2: 2
revert_bookkeeping_keep_intent_streak_continues: true
revert_bookkeeping_keep_intent_streak_count: 6
genuine_revert_count_after_h2: 2
prior_genuine_revert_cycle: cycle-003 H1
prior_genuine_revert_delta_pct: 91.7
this_genuine_revert_delta_pct: 12.36
fresh_train_variance_pattern_first_observation: true
strategist_claim_falsified: "Heat path invariant by construction"
strategist_claim_falsified_evidence: "0.02628 → 0.03487 (+32.70%); invariance band 5%; falsification ratio 6.5×"
cycle_008_entry_composite_unchanged: 0.030408
cycle_008_entry_branch_unchanged: experiment/9-fno_coregionalization-constructor-fix
cycle_008_entry_commit_unchanged: 1249f2d
source: factory-archivist
---

# Experiment #010 — Cycle-007 H2: `fno_coreg_residual` per-dataset MFRNP recipe dispatch

## Hypothesis

**Cycle-007 H2 — FIX, single-file, LOSS_RECIPE_GAP (primary) / ARCHITECTURE_OVERFIT (secondary).**
Decouple the MFRNP HF/LF loss-weight recipe per dataset on `models/fno_coreg_residual/smoke_eval.py`
so Poisson-class elliptic cells receive the Wang 2024 MFRNP `Poisson5_config.yaml` prescription
(HF up-weighting 2.0, LF down-weighting 0.25) while Heat-class parabolic cells continue running
with uniform 1.0/1.0 weights. Strategist R2 anti-pattern #5 forbade any Heat-specific recipe —
Heat had to fall through to `SMOKE_DEFAULTS` so the architecture could not drift into Heat-specific
tuning.

**Strategist R2 claim (the load-bearing falsified claim):**

> **"Heat path is invariant by construction."** Defaults `(1.0, 1.0)`; gate is `"poisson" in dataset_name.lower()`. The Heat code path will execute the *same* `p["hf_loss_weight"]` and `p["lf_loss_weights"]` as the baseline.

**Expected impact (Strategist R2 standalone projection):**
- `fno_coreg_residual` / `ifc_poisson`: 0.057564 → ≈ 0.05556 (cycle-006 H1 R4 cache reattach target).
- `fno_coreg_residual` / `ifc_heat`: 0.030590 → 0.030590 (bit-equivalent to baseline).
- Composite (standalone): 0.039578 → ≈ 0.0382 (Δ ≈ −0.0016).
- R4 kill-switch: poisson > 0.089 (+20% over current 0.057564) ⇒ revert.

## Result

**VERDICT: `revert` (genuine, substantive).** Branch `experiment/10-fno_coreg_residual-dataset-recipes @ 87f65b1` PRESERVED (per Archivist policy: preserved-branch ≠ kept-experiment; the branch is preserved so future cycles can examine the failure mode in detail, not because the work was accepted).

This is the **2nd genuine REVERT in project history** (the 1st was cycle-003 H1 at +91.7% composite regression). H2 is NOT in the `revert_bookkeeping_keep_intent` streak — composite genuinely regressed; precheck infra bugs were incidental, not load-bearing for the verdict.

| Metric | R0 honest baseline | R4 H2 after | Δ | Δ % | Direction |
|---|---:|---:|---:|---:|---|
| **composite_nRMSE** | **0.039578** | **0.044470** | **+0.004892** | **+12.36%** | ❌ regression |
| ifc_heat best-family nRMSE | 0.02628 (fno_coreg_residual) | **0.03317** (mf_fno_transfer_bar) | +0.00689 | +26.24% | ❌ regression (leaderboard flipped) |
| ifc_poisson best-family nRMSE | 0.05961 (fno_mf_stack) | 0.05961 (fno_mf_stack) | 0.0 | 0.0% | ◇ unchanged (winner unmoved) |
| fno_coreg_residual / ifc_heat | 0.02628 | **0.03487** | +0.00859 | **+32.70%** | ❌ invariance violated |
| fno_coreg_residual / ifc_poisson | 0.07419 | **0.06087** | −0.01333 | **−17.96%** | ✅ real improvement |
| Poisson kill-switch (≤ 0.089) | — | 0.06087 | −0.028 headroom | −31.6% under threshold | ✅ NOT tripped |
| Composite bar 0.0274 (parallel-bench) | — | 0.04447 | +0.01707 | +62.3% over | ❌ NOT crossed |
| Aspirational best 0.029357 | — | 0.04447 | +0.01511 | +51.5% over | ❌ NOT crossed |

**Hypothesis NOT validated.** The dispatch worked correctly for Poisson (−17.96%, real gain) but:
1. The "Heat invariance by construction" claim was empirically **falsified** — Heat regressed +32.70%, more than 6× outside the 5% invariance band.
2. The Heat regression flipped the heat leaderboard: `fno_coreg_residual` (0.02628 — was leaderboard winner) → `mf_fno_transfer_bar` (0.03317 — now leaderboard winner).
3. The Poisson gain did **not** flip the poisson leaderboard — `fno_mf_stack` retained the title at 0.05961; `fno_coreg_residual`'s improved 0.06087 only moved from further-behind to #2.
4. Net composite: gain on Poisson swamped by loss on Heat.

## What changed (R3 Builder)

Single file, +29/-0 LOC, branch cut from `experiment/7-fno_coreg_lf_hf_transfer @ be36cba` (NOT from H1's `experiment/9-…`, per Strategist R2 "each hypothesis measured independently against honest baseline"):

| File | Lines | Purpose |
|---|---:|---|
| `models/fno_coreg_residual/smoke_eval.py` | **+29 / −0** | Module-scope `_DATASET_RECIPES = {"ifc_poisson": dict(poisson_hf_weight=2.0, poisson_lf_weight=0.25)}`; two new defaulted-to-1.0 `SMOKE_DEFAULTS` keys (`poisson_hf_weight`, `poisson_lf_weight`); `resolve_fidelity_weights(dataset_name, p)` helper; dispatch via `p.update(_DATASET_RECIPES.get(args.dataset_name, {}))` after `p = dict(SMOKE_DEFAULTS)`; per-fidelity weight wiring `p["hf_loss_weight"] = hf_w; p["lf_loss_weights"] = tuple([lf_w] * max(n_levels - 1, 0))`; dispatch log line at runtime |
| **Total** | **+29 / −0, 1 file** | All under `models/fno_coreg_residual/**` |

**Critically additive at the source level:** every change was a new line — zero deletions, zero modifications to existing lines. `models/fno_coreg_residual/model.py`, `manifest.json`, `INSPIRATION.md`, `full_config.json` byte-identical to `be36cba`. Sibling pattern source at `models/fno_mf_stack/smoke_eval.py`. Builder + Reviewer detail at [[cycle-007-exp-10-build]].

**But — source-level additivity is NOT runtime invariance.** The new code path *unconditionally writes* `p["hf_loss_weight"]` and `p["lf_loss_weights"]` after dispatch returns. For Heat, the dispatch returns the SMOKE_DEFAULTS defaults `(1.0, 1.0)`, which the new lines then write. If the original code path either (a) didn't explicitly write `p["lf_loss_weights"]` at that position, or (b) computed `lf_loss_weights` as a single scalar instead of a tuple of length `n_levels-1`, the runtime tensor shapes / loss aggregation path differs — even when the numerical values are nominally identical.

## R0 → R5 lifecycle

### R0 — honest baseline (inherited from cycle-007 R0)
- Honest baseline composite = **0.039578** on `experiment/7-fno_coreg_lf_hf_transfer @ be36cba`.
- `fno_coreg_residual / ifc_heat` = 0.02628 (leaderboard winner for ifc_heat).
- `fno_coreg_residual / ifc_poisson` = 0.07419 (#2; `fno_mf_stack` wins at 0.05961).
- `fno_coregionalization` already broken on this baseline (TypeError on `modes_h` kwarg) — not introduced by H2.
- See [[ceo-verdict-evaluator-r0]].

### R1 — failure analysis (inherited from cycle-007 R1)
- H2's targeted failure mode: **LOSS_RECIPE_GAP** — `fno_coreg_residual` uses uniform 1.0/1.0 loss weights for both Heat and Poisson; literature (Wang 2024 MFRNP) prescribes (2.0, 0.25) for Poisson-class.
- Secondary: ARCHITECTURE_OVERFIT — cycle-006 carry-over A confirmed K=20/b_hidden=128 helps Heat (−13%) and hurts Poisson (+3.6%) on `fno_coreg_residual`.
- See [[failure-analysis-cycle-007]].

### R1.5 — research (inherited from cycle-007 R1.5)
- Sibling pattern at `models/fno_mf_stack/smoke_eval.py` already implements dataset-name dispatch — directly portable.
- Wang 2024 MFRNP `Poisson5_config.yaml` is the canonical source for the (2.0, 0.25) recipe.
- See `.factory/strategy/research.md`.

### R2 — strategy (PLAN APPROVED, claim later falsified)
- Option B: 2 hypotheses, no bundling. H2 = per-dataset recipe decoupling.
- Strategist explicit claim: **"Heat path invariant by construction."** Defaults (1.0, 1.0); gate excludes "heat". This claim was the load-bearing assertion that justified the no-kill-switch on the Heat side.
- Heat-side kill-switch deliberately omitted on the assumption of construction-invariance.
- Poisson-side kill-switch: poisson > 0.089 (+20% over current `fno_coreg_residual` poisson 0.057564).
- See [[ceo-verdict-strategist]].

### R3 — build (clean isolation, no redirects)
- Branch `experiment/10-fno_coreg_residual-dataset-recipes` cut from `experiment/7@be36cba`.
- Commit `87f65b1`: 1 file, +29/-0 LOC.
- 2-epoch smoke verified on both datasets with correct dispatch log lines (`hf=1.0 lf=1.0` for ifc_heat, `hf=2.0 lf=0.25` for ifc_poisson).
- `factory guard --check-scope = clean`. Reviewer PASS. CEO PROCEED on both Builder and Reviewer with documented leakage-check override on the dataset-name token `ifc_poisson` (public dispatch API, not ground truth).
- Builder redirects used: **0 of 2** (caveat: structural easy case — target file at HEAD pre-edit).
- See [[cycle-007-exp-10-build]], [[ceo-verdict-builder]], [[ceo-verdict-reviewer]].

### R4 — post-change evaluation (FAIL — REVERT signal)
- Eval: `bash scripts/cycle_eval.sh` on `experiment/10-fno_coreg_residual-dataset-recipes @ 87f65b1`, 186 s wall.
- Cache misses on both `fno_coreg_residual × {ifc_heat, ifc_poisson}` (new code hash `528438a274db`). Fresh retrains on both cells.
- **Composite 0.044470 (Δ +0.004892, +12.36% vs honest baseline) — FAIL.**
- `fno_coreg_residual / ifc_heat` = **0.034873** (was 0.02628; **+32.70%**, INVARIANCE VIOLATED).
- `fno_coreg_residual / ifc_poisson` = **0.060866** (was 0.07419; **−17.96%**, real improvement but +9.55% over cycle-005 target 0.05556).
- Heat leaderboard winner flipped: `fno_coreg_residual` → `mf_fno_transfer_bar` 0.033175.
- Poisson leaderboard winner unchanged: `fno_mf_stack` 0.059611.
- Poisson kill-switch (> 0.089) **NOT tripped** (0.060866 is 31.6% under threshold).
- Hypothesis NOT validated. See [[evaluator-latest]].

### R5 — formal verdict (REVERT, substantive)
- **CEO intent = REVERT** — composite genuinely regressed; invariance claim genuinely falsified; Heat leaderboard genuinely lost. The intent IS the revert; there is no "keep" hidden behind precheck bugs here.
- **Formal verdict = REVERT** — agrees with CEO intent.
- **This is NOT in the `revert_bookkeeping_keep_intent` streak.** That streak (now 6, from H1) is for cases where composite improved but precheck infra bugs misrecorded a revert. H2 composite truly regressed.
- Branch `experiment/10-fno_coreg_residual-dataset-recipes @ 87f65b1` PRESERVED so future cycles can inspect the failure mode in detail. Preservation ≠ keep — the experiment is reverted from project state.
- Cycle-008 entry baseline UNCHANGED at **composite 0.030408** on `experiment/9-fno_coregionalization-constructor-fix @ 1249f2d` (from H1). H2's preserved branch is reference-only.

## Why this is a genuine revert, not `revert_bookkeeping_keep_intent`

The 6-streak `revert_bookkeeping_keep_intent` pattern fires when **all three** conditions hold:
1. The real research metric monotonically improves.
2. All real safety checks (`ground_truth_leakage`, `anti_pattern`, `smoke_test`) pass.
3. The precheck infra bugs (`score_direction` polarity, empty-detail `scope` / `fixed_surfaces`) trip and the formal record reports REVERT.

For H2:
1. ❌ Composite **regressed** +12.36% (0.039578 → 0.044470). Condition 1 fails.
2. ✅ All real safety checks would pass.
3. ⚠️ Precheck infra bugs would still trip (every cycle does), but they are NOT load-bearing here — the verdict is REVERT regardless of precheck.

**The cycle-003 H1 parallel:** that experiment was framed as the only genuine REVERT in project history because composite genuinely regressed 0.04420 → 0.08472 (+91.7%). H2 is the second of its kind, at a smaller magnitude (+12.36%) but the same structural class.

**Distinguishing trait:** in H1 (genuine improvement masked by precheck bugs), the branch preservation is intent-load-bearing — the cycle-008 baseline pulls FROM the preserved branch. In H2 (genuine regression), the branch preservation is reference-only — the cycle-008 baseline is **unchanged** (still cycle-007 H1's `experiment/9` @ `1249f2d`).

## Key findings — cross-cycle lessons

### Finding 1: The Strategist's "invariant by construction" claim was empirically false

> **Claim (Strategist R2):** "Heat path is invariant by construction. Defaults `(1.0, 1.0)`; gate excludes `'heat'` in dataset_name. The Heat code path will execute the same `p["hf_loss_weight"]` and `p["lf_loss_weights"]` as the baseline."
> **Reality (R4):** Heat regressed +32.70% (0.02628 → 0.03487). The invariance band was 5%; falsification ratio 6.5×.

**Two candidate mechanisms (non-exclusive):**

**A. Code-path side effect.** The new code path unconditionally writes `p["hf_loss_weight"]` and `p["lf_loss_weights"]` in `run()` *even when* `_DATASET_RECIPES.get(dataset_name, {})` returns the empty dict. If the original code:
- Did not have `p["hf_loss_weight"]` / `p["lf_loss_weights"]` explicitly written at that position, OR
- Wrote them with a different default than `(1.0, 1.0)` per-position, OR
- Wrote `lf_loss_weights` as a different tensor shape than `tuple([lf_w] * max(n_levels - 1, 0))`,

then the runtime wiring CHANGED for Heat even though the dispatch dict was empty. Strategist's "invariant by construction" reasoned over the dispatch dict only, not the unconditional downstream writes.

**B. Fresh-train variance with cache-hash flip.** Code hash changed `1d967ad6e54c` → `528438a274db`, invalidating the cache. Prior fresh-train values on this cell:
- cycle-005 baseline (hash A): fno_coreg_residual / ifc_heat = 0.03519
- cycle-006 H1 R4 (hash B): 0.03059
- cycle-007 R0 (hash 1d967ad6e54c): 0.02628 ← Strategist's anchor
- cycle-007 H2 R4 (hash 528438a274db): 0.03487 ← this run

Range: 0.02628 → 0.03519 — empirical run-to-run variance on this cell **alone** is ≥ 34%. The Strategist's "invariance" was anchored on the single low value (0.02628) without measuring the variance band. The 5% invariance band was a fiction.

**Both mechanisms likely contribute** — A explains why the regression direction is consistent (the new lines forced a shape change that disadvantages the trajectory); B explains why the magnitude exceeds what a "shouldn't-matter" rewrite would predict.

### Finding 2: Fresh-train variance can swamp claimed invariance (NEW cross-cycle pattern)

**Pattern statement:** A "no-op" code change that touches loss-aggregation logic is NEVER truly invariant when fresh trains are involved. Cache hash changes force retrain, and the new training trajectory may land at a different optimum than prior runs — even when the code path is mathematically equivalent for one dataset.

**Generalization for cycle-008+ strategist rules:**
- BEFORE claiming "invariant by construction" on a fresh-train cell, **measure the empirical variance band** by running ≥3 fresh trains on that cell with different cache-bust trivia. If the variance band exceeds the claimed invariance band, the claim is unsupported.
- For any code change that touches loss-aggregation, training-loop wiring, or optimizer construction — even if mathematically equivalent — assume fresh-train variance ≥ 20% on the affected cell and either (a) include a kill-switch on the supposedly-invariant cell, or (b) gate the change behind a runtime feature flag so the cache hash is preserved for the unaffected cell.
- **Bookkeeping flip:** the cycle-007 H1 fno_coregionalization/ifc_heat cell *did* reproduce the cycle-005 cache 0.01551 exactly within 1e-8 — but only because the constructor fix was a wrapper-level signature swap that produced bit-equivalent training given the same hash inputs. H2's smoke_eval.py change altered the training loop input itself.

### Finding 3: Poisson recipe transfer is a real but partial gain

The MFRNP (2.0, 0.25) recipe on `fno_coreg_residual / ifc_poisson` produced a real improvement (0.07419 → 0.06087, −17.96%) — confirming the LOSS_RECIPE_GAP hypothesis was directionally correct on the Poisson side. But:
- Magnitude fell **+9.55% short** of the cycle-005 cache target 0.05556 — the recipe alone does not fully reach cycle-005's frontier for this cell.
- Did NOT take the poisson leaderboard from `fno_mf_stack` (0.05961 < 0.06087 by 2.1%).
- The architectural difference between `fno_coreg_residual` (residual decoder over `fno_mf_stack`'s coregionalization kernel) absorbs some of the loss-asymmetry signal — recipe portability across architectures is partial, NOT plug-in (consolidating the cycle-006 H1 pattern at higher confidence: "Cross-architecture recipe portability is NOT guaranteed even when receiving architecture shares structural family").

### Finding 4: The dispatch mechanism itself works

Builder verification showed the dispatch log lines emit correctly:
- `[run] resolve_fidelity_weights: dataset=ifc_heat hf=1.0 lf=1.0`
- `[run] resolve_fidelity_weights: dataset=ifc_poisson hf=2.0 lf=0.25`

The mechanism is sound; the failure is at the hypothesis layer ("Heat is invariant" was wrong), not the implementation layer.

## What this leaves for cycle-008

- **Cycle-008 entry baseline UNCHANGED:** composite 0.030408 on `experiment/9-fno_coregionalization-constructor-fix @ 1249f2d` (from H1).
- **fno_coreg_residual on Poisson** has a real gain available (0.07419 → 0.06087 with MFRNP recipe), but stacking it requires a strategy that doesn't disrupt the cycle-005 Heat anchor. Two paths:
  1. **Runtime feature flag**: gate the new code path behind `os.getenv("FNO_COREG_DATASET_DISPATCH")` so heat-cell cache hash is preserved. This still changes source but preserves the hash key.
  2. **In-architecture conditional**: move the dispatch into `fno_coreg_residual.model.py` itself (e.g., dataset-aware forward pass) so the smoke_eval.py path stays byte-identical for Heat. Higher engineering cost; cleaner invariance.
- **Poisson leaderboard remains the geomean bottleneck.** `fno_mf_stack / ifc_poisson` at 0.05961 (1.65× over paper 0.036). Pushing `fno_coreg_residual` poisson below `fno_mf_stack` requires either the recipe + a small architecture tweak, or a different family.
- **Heat is solved** at the cycle-005 frontier (0.01551 via fno_coregionalization on cycle-008 entry baseline). Further heat gains require architectural advance below 0.01551, not recipe fixes.
- **New strategist rule** (from this experiment): for any change that touches loss-aggregation OR training-loop wiring, REQUIRE an empirical variance-band measurement on all "invariant" cells before claiming construction-invariance. Without this measurement, no kill-switch can be omitted.

## Anti-patterns explicitly NOT triggered

- ✅ No bundling with H1 (Strategist anti-pattern #1) — H2 branch cut independently from `experiment/7@be36cba`.
- ✅ No `_DATASET_RECIPES` Heat entry (Strategist anti-pattern #5) — dispatch dict only has `ifc_poisson` key.
- ✅ No `SMOKE_DEFAULTS` drift (Strategist anti-pattern #3) — original keys byte-preserved, only two new keys appended.
- ✅ No fallback shim for the recipe API (Strategist anti-pattern #2) — `_DATASET_RECIPES.get(name, {})` returns empty by design.
- ✅ No fixed-surface edits (Strategist anti-pattern #7).
- ✅ No expected-effect numbers re-derived from ground-truth (Strategist anti-pattern #8).

## What was wrong with the strategy

The R2 strategy passed all 10 CEO hard-gate checks AND was internally consistent — but it **omitted a required check**: empirical variance-band measurement on cells claimed to be invariant. The "invariant by construction" reasoning is valid for source-level equivalence but does not bind on fresh-train trajectories when the cache hash changes.

**Recommendation to incorporate as a CEO hard-gate check in cycle-008**:

> Hard-gate (proposed): for any hypothesis claiming "invariant by construction" on a cell that would be a fresh train (cache miss expected), require either (a) a kill-switch on the supposedly-invariant cell with a band ≥ 20% (anchored to empirical variance, not source equivalence), OR (b) explicit evidence that the cache hash is preserved (proof of byte-identical input to the cache-key function).

## Links

- Project dashboard: [[factory_mffp]]
- Build phase note: [[cycle-007-exp-10-build]]
- Strategy snapshot: [[cycle-007]]
- Failure analysis (R1): [[failure-analysis-cycle-007]]
- CEO verdicts: [[ceo-verdict-builder]], [[ceo-verdict-reviewer]], [[ceo-verdict-strategist]], [[ceo-verdict-evaluator]], [[ceo-verdict-evaluator-r0]], [[ceo-verdict-failure_analyst]]
- Evaluator latest report: [[evaluator-latest]]
- Researcher latest report: [[researcher-latest]]
- Sibling cycle-007 experiment (H1): [[cycle-007-exp-9]] (genuine improvement; this is the cycle-008 entry baseline)
- Prior genuine revert: [[factory_mffp-005-experiment]] (cycle-003 H1, +91.7% composite regression)
- Related patterns:
  - [[patterns]] §"Fresh-train variance can swamp claimed invariance" (NEW — first observation this experiment)
  - [[patterns]] §"Cross-architecture recipe portability is NOT guaranteed" (cycle-006 H1; reinforced 2-for-2)
  - [[patterns]] §"Per-fidelity output normalization is the cheapest large win" (continues to hold)
  - [[patterns]] §"Factory precheck `score_direction` is polarity-buggy" (precheck still trips but is incidental here)
- Commit: `87f65b15e882ae285a782d114c96fd0e96ccea10` on branch `experiment/10-fno_coreg_residual-dataset-recipes`
- Base: `experiment/7-fno_coreg_lf_hf_transfer @ be36cba`
- Research run summary: `.factory/research/runs/cycle-007-h2/summary.json`
