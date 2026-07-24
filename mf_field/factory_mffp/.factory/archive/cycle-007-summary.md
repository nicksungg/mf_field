---
name: cycle-007-summary
description: Cycle-007 close-out for factory_mffp. Two hypotheses run on the restored cycle-005 H2 frontier — H1 (constructor fix on fno_coregionalization) and H2 (per-dataset MFRNP recipe dispatch on fno_coreg_residual). Net cycle effect — banked reproducible best moved from 0.029357 (unreproducible aspirational, cycle-005 H2) to 0.030408 (reproducible, cycle-007 H1) despite BOTH hypotheses formally REVERTed. H1 = revert_bookkeeping_keep_intent (composite genuinely improved −23.17%; precheck infra bugs flipped the formal verdict — 6-for-6 streak). H2 = genuine REVERT (composite genuinely regressed +12.36%; Strategist "Heat invariant by construction" claim empirically falsified +32.70%). Three NEW infrastructure bugs documented — precheck score_direction polarity (now 8-of-8), precheck scope/fixed_surfaces empty-violation FPs (now 3-of-3), and leakage-check false-positive sub-class extended to dataset-name dispatch-key tokens. Cycle-008 entry — experiment/9-fno_coregionalization-constructor-fix @ 1249f2d (composite 0.030408). Cycle-008 strategic priorities — (i) build on banked H1 state, (ii) fix mf_fno_transfer_bar undertraining (BAR @ ~0.02743 still wins composite by 0.003), (iii) re-attempt Poisson improvement on fno_coreg_residual with proper invariance verification (e.g., warm-init from current cached state to control fresh-train variance).
metadata:
  type: project
tags:
  - factory
  - cycle-summary
  - factory_mffp
  - cycle-007
  - close-out
  - revert-bookkeeping-keep-intent
  - revert-genuine
  - new-reproducible-project-best
project: factory_mffp
cycle_id: "007"
date: 2026-06-02
source: factory-archivist
status: closed
experiments_run: 2
ceo_keep_count: 1
ceo_revert_count: 1
factory_bookkeeping_keep_count: 0
factory_bookkeeping_revert_count: 2
precheck_polarity_bug_total_after_cycle_007: 8
precheck_empty_detail_scope_fixed_surfaces_after_cycle_007: 3
revert_bookkeeping_keep_intent_streak_after_cycle_007: 6
genuine_revert_count_after_cycle_007: 2
prior_genuine_revert: "cycle-003 H1 (composite +91.7%)"
new_reproducible_project_best: true
project_best_composite_reproducible: 0.030408
prior_reproducible_project_best_composite: 0.04420
prior_reproducible_project_best_source: cycle-002 H3
aspirational_best_composite_unreproducible: 0.029357
aspirational_best_source: cycle-005 H2
cycle_007_entry_composite_honest_baseline: 0.039578
cycle_007_exit_composite: 0.030408
cycle_delta_pct_honest: -0.232
cycle_delta_pct_vs_aspirational: 0.036
parallel_bench_bar_target_composite: 0.02743
parallel_bench_bar_short_by: 0.00298
h1_id: "009"
h1_branch: experiment/9-fno_coregionalization-constructor-fix
h1_parent_branch: experiment/7-fno_coreg_lf_hf_transfer
h1_parent_commit: be36cba
h1_commit: 1249f2de87bfd15001c67a22ee4ea66343fecd2d
h1_score_before: 0.039578
h1_score_after: 0.030407732506238343
h1_score_delta_pct: -23.17
h1_verdict: revert_bookkeeping_keep_intent
h1_ceo_intent: keep
h1_files_changed: 1
h1_loc_delta: "+9/-7"
h2_id: "010"
h2_branch: experiment/10-fno_coreg_residual-dataset-recipes
h2_parent_branch: experiment/7-fno_coreg_lf_hf_transfer
h2_parent_commit: be36cba
h2_commit: 87f65b15e882ae285a782d114c96fd0e96ccea10
h2_score_before: 0.039578
h2_score_after: 0.044469863562733095
h2_score_delta_pct: 12.36
h2_verdict: revert
h2_verdict_type: substantive
h2_ceo_intent: revert
h2_files_changed: 1
h2_loc_delta: "+29/-0"
h2_strategist_invariance_claim_falsified: true
h2_falsification_ratio: 6.5
h2_fno_coreg_residual_heat_delta_pct: 32.70
h2_fno_coreg_residual_poisson_delta_pct: -17.96
new_patterns_added: ["fresh-train-variance-swamps-invariance", "leakage-check-dispatch-key-sub-class"]
existing_patterns_reinforced: ["precheck-score-direction-polarity-bug (7→8)", "precheck-empty-detail-scope-fixed-surfaces (2→3)", "revert_bookkeeping_keep_intent universal verdict (5→6)", "cross-architecture-recipe-portability-not-guaranteed (1→2)", "silent-regression-masked-by-cache-layer (1→2)"]
cycle_008_entry_composite: 0.030408
cycle_008_entry_branch: experiment/9-fno_coregionalization-constructor-fix
cycle_008_entry_commit: 1249f2d
cycle_008_strategic_priorities: ["build on banked H1 state", "fix mf_fno_transfer_bar undertraining (BAR still wins composite by 0.003)", "re-attempt Poisson improvement on fno_coreg_residual with empirical variance verification"]
---

# Cycle 007 — factory_mffp — Close-out Summary

**Status:** **CLOSED 2026-06-02**.
**Cycle scope:** Two hypotheses on the broken cycle-005 H2 frontier.
H1 = constructor fix on `fno_coregionalization` (single-PR scope,
COMMITTED_TREE_BROKEN failure mode); H2 = per-dataset MFRNP recipe
dispatch on `fno_coreg_residual` (LOSS_RECIPE_GAP failure mode).
**Outcome:** 2 hypotheses run; H1 = `revert_bookkeeping_keep_intent`
(CEO KEEP — composite genuinely improved −23.17%, precheck infra bugs
trip the formal verdict); H2 = genuine REVERT (composite genuinely
regressed +12.36% — Strategist "Heat invariant by construction" claim
falsified at +32.70% on the Heat cell).
**Net cycle effect (the real engineering win despite both formal
reverts):** the project's banked **reproducible** best moved from
**0.029357 (aspirational, not reproducible from committed tree)** to
**0.030408 (reproducible) on `experiment/9-fno_coregionalization-constructor-fix @ 1249f2d`**.

## TL;DR

- **Honest baseline discovery (cycle-007 R0):** project best composite_nRMSE
  **0.039578** on `experiment/7-fno_coreg_lf_hf_transfer @ be36cba` — NOT
  cycle-005 H2's aspirational 0.029357 (which became unreproducible when
  cycle-006 H1's `git reset --hard` wiped the dirty load-bearing
  `fno_coregionalization/model.py`). The 0.039578 vs 0.029357 gap
  (+0.010221, +34.8%) was explained by `fno_coregionalization` hard-crashing
  both `ifc_heat` and `ifc_poisson` with
  `TypeError: FNOCoregionalization.__init__() got an unexpected keyword argument 'modes_h'`
  at `models/fno_coregionalization/smoke_eval.py:265`. See
  [[failure-analysis-cycle-007]] and the
  [[patterns]] §"Silent regression masked by the cache layer" (second
  consecutive cycle).
- **H1 (exp_id 009, `fno_coregionalization` anisotropic-modes constructor fix):**
  single file, +9/-7 LOC at `models/fno_coregionalization/model.py`.
  Constructor signature swap `(modes: int, grid_size: int) →
  (modes_h: int, modes_w: int, grid: tuple)`; inner classes already
  accepted anisotropic modes; cycle-005 H2 schedule in `smoke_eval.py:64-411`
  byte-preserved. **R4 result: composite 0.039578 → 0.030408
  (−23.17%, **REAL IMPROVEMENT**); `fno_coregionalization` on `ifc_heat`
  reproduces cycle-005 cache 0.01551 to within ≈+1e-8.** Heat kill-switch
  (≤ 0.0194) NOT tripped (20% headroom). Reviewer PASS substantive;
  Evaluator R4 PASS-KEEP. Verdict: `revert_bookkeeping_keep_intent`
  (6-for-6 streak) — formal REVERT due to 3 precheck infrastructure bugs
  (`score_direction` polarity flips −23% improvement to +23% "regression";
  empty-detail `scope` and `fixed_surfaces` violations report empty lists
  while standalone `factory guard --check-scope` reports `clean`). Branch
  `experiment/9-fno_coregionalization-constructor-fix @ 1249f2d` preserved
  as cycle-008 entry baseline. See [[cycle-007-exp-9]] and
  [[cycle-007-exp-9-build]].
- **H2 (exp_id 010, `fno_coreg_residual` per-dataset MFRNP recipe dispatch):**
  single file, +29/-0 LOC at `models/fno_coreg_residual/smoke_eval.py`
  (purely additive at source level). Module-scope `_DATASET_RECIPES`
  with `ifc_poisson: (HF=2.0, LF=0.25)` per Wang 2024 MFRNP
  `Poisson5_config.yaml`; Heat path falls through to SMOKE_DEFAULTS
  `(1.0, 1.0)` — Strategist R2 claimed "Heat invariant by construction"
  on this basis. **R4 result: composite 0.039578 → 0.044470 (+12.36%,
  GENUINE REGRESSION). `fno_coreg_residual / ifc_heat` 0.02628 → 0.03487
  (+32.70%, INVARIANCE VIOLATED, 6.5× the 5% claimed band).
  `fno_coreg_residual / ifc_poisson` 0.07419 → 0.06087 (−17.96%, real
  material gain but +9.55% short of cycle-005 target 0.05556 and did
  NOT beat `fno_mf_stack`'s native poisson winner 0.05961).** Heat
  leaderboard FLIPPED `fno_coreg_residual` → `mf_fno_transfer_bar`
  @ 0.03317. Poisson kill-switch (>0.089) NOT tripped (0.06087 is 31.6%
  under threshold); Heat side had no kill-switch by Strategist design.
  Verdict: **`revert` (genuine, substantive)** — 2nd genuine revert in
  project history (1st: cycle-003 H1 @ +91.7%). Branch
  `experiment/10-fno_coreg_residual-dataset-recipes @ 87f65b1` preserved
  for reference only — cycle-008 baseline UNCHANGED. See
  [[cycle-007-exp-10]] and [[cycle-007-exp-10-build]].

## Net cycle effect (the real engineering win)

| Reference point | Composite | Reproducible? |
|---|---:|---|
| Cycle-002 H3 (prior reproducible project best) | 0.04420 | ✅ yes (`experiment/4 @ 0c46f43`, preserved) |
| Cycle-005 H2 (aspirational, unreproducible) | 0.029357 | ❌ no (cache hash 9528aeef no longer key-resolves vs current 4235deb6) |
| Cycle-005 R0 baseline | 0.033726 | ✅ yes |
| Cycle-007 R0 honest baseline | 0.039578 | ✅ yes (`experiment/7 @ be36cba`) |
| **Cycle-007 H1 (new reproducible project best)** | **0.030408** | **✅ yes (`experiment/9 @ 1249f2d`)** |
| Cycle-007 H2 (preserved-but-reverted) | 0.044470 | ✅ yes — reverted from project state |
| Parallel-bench bar (still wins composite by 0.003) | 0.02743 | ✅ yes (`mf_fno_transfer_bar` parallel run) |

- **Cycle-007 closes with reproducible composite 0.030408**, which is
  −9.85% vs cycle-005 R0 baseline (0.033726), −31.2% vs prior
  reproducible project best (cycle-002 H3 0.04420), and only +3.58%
  above the aspirational unreproducible cycle-005 H2 (0.029357).
- The project's **scoreboard moved meaningfully forward** even though
  both hypotheses formally REVERTed. The reproducibility gap from
  cycle-005 H2 (the load-bearing dirty `model.py` wiped by cycle-006 H1
  `git reset --hard`) is now closed structurally — `fno_coregionalization`
  is runnable from a clean committed tree and reproduces cycle-005's
  heat 0.01551 winner exactly within rounding.
- The remaining gap to the parallel-bench bar 0.02743 is +0.00298
  (+10.85% over bar). The H1-calibration realistic-stretch band
  0.028–0.032 WAS met.

## H1 = `revert_bookkeeping_keep_intent` (the bookkeeping-revert-with-keep-intent pattern, 3rd in series)

This is the **3rd experiment in the bookkeeping-revert-with-keep-intent
series** within the broader 6-for-6 `revert_bookkeeping_keep_intent`
streak (the streak goes back to cycle-001, but the **bookkeeping-revert
with score-improvement-banked AND branch-preserved as cycle-N+1 entry**
sub-pattern is more recent):

| Cycle / hypothesis | Composite delta | Branch banked as next-cycle entry |
|---                  |---              |---                                |
| cycle-002 H3 — `fno_coreg_residual` hybrid (first family to beat paper composite geomean) | 0.0775 → 0.04420 (−43%) | `experiment/4-fno_coreg_residual @ 0c46f43` |
| cycle-005 H2 — `fno_coregionalization` two-stage LF→HF transfer | 0.033726 → 0.029357 (−13%) **(aspirational; later non-reproducible)** | `experiment/7-fno_coreg_lf_hf_transfer @ be36cba` |
| **cycle-007 H1 — `fno_coregionalization` constructor fix (restores cycle-005 frontier reproducibly)** | **0.039578 → 0.030408 (−23.17%)** | **`experiment/9-fno_coregionalization-constructor-fix @ 1249f2d`** |

The protocol is now operational: when (a) the real research metric
monotonically improves, (b) all 3 real safety checks pass
(`ground_truth_leakage`, `anti_pattern`, `smoke_test`), and (c) the
precheck infra bugs trip, the CEO records `revert_bookkeeping_keep_intent`
and preserves the branch as the next-cycle entry baseline.

## H2 = genuine REVERT (Heat invariance falsified)

This is the **2nd genuine REVERT in project history** (1st: cycle-003 H1
@ +91.7% composite regression). H2's regression magnitude is smaller
(+12.36%) but the structural class is identical: the composite
**genuinely regressed**, the precheck infra bugs (which still fire)
are NOT load-bearing for the verdict, and the branch preservation is
**reference-only**, not baseline-banked.

**The load-bearing falsified claim (Strategist R2, literal):**

> **"Heat path is invariant by construction."** Defaults `(1.0, 1.0)`;
> gate is `"poisson" in dataset_name.lower()`. The Heat code path will
> execute the *same* `p["hf_loss_weight"]` and `p["lf_loss_weights"]`
> as the baseline.

**R4 reality:** Heat regressed +32.70% (0.02628 → 0.03487 — 6.5× the
claimed 5% invariance band). Two non-exclusive mechanisms — (a) the
new code path unconditionally writes `p["hf_loss_weight"]` and
`p["lf_loss_weights"]` even when the dispatch dict returns empty for
Heat (runtime wiring changed despite the dispatch dict being empty);
(b) cache-hash flip `1d967ad6e54c → 528438a274db` forced a fresh
retrain whose trajectory landed at a different optimum — empirical
variance on this cell across 4 cache hashes is ≥ 34%, far exceeding
the 5% claimed band. See [[cycle-007-exp-10]] §"Key findings — cross-cycle
lessons" and [[patterns]] §"Fresh-train variance can swamp claimed
invariance".

## Three NEW infrastructure bugs documented in cycle-007

### Bug 1 — Precheck `score_direction` polarity bug (8th instance)

**Status:** existing pattern, EVIDENCE EXTENDED in cycle-007 H1 (now
8-for-8 across project history).

**Mechanism:** `precheck.py` treats `composite_nRMSE` as
higher-is-better even though it is lower-is-better (the precheck does
not read `primary_metric_lower_is_better` from `eval/smoke_config.json`).
The −23.17% H1 improvement is misread as a +23.17% "regression" and
the formal verdict flips to REVERT.

**Fix location:** `precheck.py` lives in
`/orcd/data/faez/001/nick/mf_field/akash/remote-factory-main` — **out
of cycle-007 mutable surface**. Cannot be fixed within the project
cycle; remains an upstream factory-infra issue.

See [[patterns]] §"Factory precheck `score_direction` is polarity-buggy
on lower-is-better metrics".

### Bug 2 — Precheck `scope` / `fixed_surfaces` empty-detail false positives (3rd instance)

**Status:** existing pattern, EVIDENCE EXTENDED in cycle-007 H1 (now
3-for-3 across project history).

**Mechanism:** Precheck reports `scope` and `fixed_surfaces` violation
lists as empty (zero details), yet the failure flag is still raised.
Standalone `factory guard --check-scope` on the same diff at the same
commit reports `clean`. The precheck and standalone disagree on the
identical scope-evaluation function.

**Fix location:** `precheck.py` parsing logic — out of cycle scope.

See [[patterns]] §"Factory precheck reports empty-detail `scope` /
`fixed_surfaces` failures that contradict the standalone guard".

### Bug 3 — Leakage-check `ground_truth_leakage` dataset-name dispatch-key false positive (NEW sub-class — cycle-007 H2)

**Status:** **NEW sub-class** of the existing leakage-check pattern.
Prior sub-classes (shared-vocabulary, numerical-substring collision)
are documented since cycle-001. **Cycle-007 H2 introduces a third
sub-class: dataset-name tokens used as PUBLIC DISPATCH API keys via
`args.dataset_name`.**

**Mechanism:** H2's `+29/-0 LOC` source change added the literal
string `"ifc_poisson"` to `models/fno_coreg_residual/smoke_eval.py` as
a `_DATASET_RECIPES` dictionary key. The leakage scanner walked
`factory.md` and matched the substring `"ifc_poisson"` against
research-constraints text on the same line, raising a `medium-risk`
flag. CEO override rationale (added to dashboard):

> Dataset name `ifc_poisson` is the public dispatch API via
> `args.dataset_name`, not a ground-truth value — same false-positive
> class as cycle-001 shared-vocabulary findings; sub-class extended
> to dataset-name dispatch keys.

**Fix location:** scanner needs token-class differentiation (value vs
schema vs documentation vs dispatch-key) — same out-of-cycle
factory-infrastructure work that has been open since cycle-001.

See [[patterns]] §"Factory leakage-check fingerprints `factory.md`
itself and produces false-positive medium-risk on shared vocabulary"
(cycle-007 H2 sub-class added).

## Cycle-008 entry point and strategic recommendations

**Cycle-008 entry baseline (load-bearing):**
- Composite: **0.030408**
- Branch: `experiment/9-fno_coregionalization-constructor-fix`
- Commit: `1249f2d` (preserved on disk)
- Parent: `experiment/7-fno_coreg_lf_hf_transfer @ be36cba`
- Per-dataset state: `ifc_heat` 0.01551 (via `fno_coregionalization`,
  reproducing cycle-005 cache); `ifc_poisson` 0.05961 (via
  `fno_mf_stack`).

**Strategic recommendations for cycle-008:**

1. **Build on the banked H1 state** — every cycle-008 hypothesis
   should branch off `experiment/9-fno_coregionalization-constructor-fix @ 1249f2d`,
   NOT `main` or `experiment/7`. Monotonic-improvement checks anchor
   at 0.030408, NOT 0.039578 (the cycle-007 R0 baseline) or 0.029357
   (the unreproducible cycle-005 aspirational).
2. **Attempt to fix `mf_fno_transfer_bar` undertraining** — the BAR
   (`mf_fno_transfer_bar` parallel-bench composite 0.02743) still
   wins composite by 0.003. The BAR is currently underconverged at
   smoke budget (~10 s wall) — closing the smoke-vs-parallel gap is
   the most direct path to surpassing the BAR composite. Highest-EV
   surface: smoke-budget allocation on the BAR's training schedule.
3. **Re-attempt Poisson improvement on `fno_coreg_residual` with
   proper invariance verification** — the H2 Poisson result (−17.96%)
   is real but was swamped by an unverified Heat regression. Two
   paths to recover the Poisson win without disrupting Heat:
   - **Warm-init from current cached state** — controls fresh-train
     trajectory variance by starting from a near-converged optimum
     rather than a random init; reduces the empirical variance band.
   - **In-architecture conditional** — move dispatch into
     `fno_coreg_residual/model.py` itself (dataset-aware forward pass)
     so `smoke_eval.py` stays byte-identical for Heat and the cache
     hash is preserved on the Heat cell.
   - **OR runtime feature flag** — gate the new dispatch behind
     `os.getenv("FNO_COREG_DATASET_DISPATCH")` so the default code path
     hashes byte-identically and Heat cache hits.
4. **Add Strategist hard-gate #11 (proposed in cycle-007 H2 close-out):**
   for any cell claimed "invariant by construction" that would be a
   fresh train (cache miss expected), require either (a) a kill-switch
   with a band ≥ 20% anchored to ≥ 3 prior fresh-train values, OR (b)
   explicit byte-identical cache-key proof.
5. **Defer:** `mf_fno_bar_residual` new family (Top-3 from cycle-007 R2)
   — still the highest-EV architectural move but should follow after
   the BAR-undertraining fix lands so the new family has a clear
   reference baseline.

## Cross-cycle pattern updates (existing patterns reinforced)

| Pattern | Before cycle-007 | After cycle-007 |
|---|---:|---:|
| `revert_bookkeeping_keep_intent` universal verdict | 5 evals | **6 evals (H1 added)** |
| Precheck `score_direction` polarity bug (lower-is-better metric) | 7 instances | **8 instances (H1 added)** |
| Precheck empty-detail `scope` / `fixed_surfaces` FP | 2 instances | **3 instances (H1 added)** |
| Cross-architecture recipe portability is NOT guaranteed | 1 instance (cycle-006 H1) | **2 instances (H2 Poisson partial port added)** |
| Silent regression masked by the cache layer | 1 instance (cycle-006) | **2 instances (cycle-007 R0 discovery added)** |
| Leakage-check substring-collision FP | 5 sub-classes (vocabulary, numerical, dataset-token, downstream, schema) | **6 sub-classes (H2: dataset-name dispatch-key added)** |

## NEW cross-cycle patterns added in cycle-007

1. **"Fresh-train variance can swamp claimed invariance"** — code-path
   equivalence at the source level does NOT imply numerical equivalence
   when fresh trains are involved. Cache-hash flip on a supposedly
   no-op code change forces retrain; the new trajectory may land at a
   different optimum than prior runs. First observed in cycle-007 H2;
   the 5% Strategist invariance band on `fno_coreg_residual / ifc_heat`
   was falsified by 6.5× when the empirical variance was ≥ 34%. See
   [[patterns]] §"Fresh-train variance can swamp claimed invariance".

2. **Leakage-check false-positive sub-class: dataset-name dispatch-key
   tokens** — strings used as the public dispatch API via
   `args.dataset_name` (e.g., `"ifc_poisson"` as a `_DATASET_RECIPES`
   dictionary key) trip the leakage scanner against research-constraints
   text in `factory.md`. Distinct from prior sub-classes
   (shared-vocabulary, numerical-substring) because the token is
   intentionally part of the public API. See [[patterns]] §"Factory
   leakage-check fingerprints `factory.md` itself…" (sub-class extended).

## Failures of process to surface in cycle-007

- **Researcher / failure_analyst wrappers timed out (continuing 4+
  cycles)** — CEO synthesized substitutes from direct source reads;
  this is now standing operational practice and should be normalized in
  cycle-008 R1 / R1.5 plans.
- **Strategist R2 missed empirical-variance verification** — the
  "Heat invariant by construction" claim passed the 10-check
  Strategist hard-gate suite but never measured the empirical variance
  band. Proposed hard-gate #11 (above) addresses this.
- **Builder hygiene was structurally easy** — both H1 and H2 had
  target files at HEAD pre-edit (not in the 15-file dirty set), so the
  [[dirty-tree-staging]] auto-memory rule held by construction. The
  rule has NOT been stress-tested on a dirty-file target in cycle-007.

## Links

- Experiment notes:
  - [[cycle-007-exp-9]] (H1 full lifecycle)
  - [[cycle-007-exp-9-build]] (H1 build phase)
  - [[cycle-007-exp-10]] (H2 full lifecycle)
  - [[cycle-007-exp-10-build]] (H2 build phase)
- Failure analysis: [[failure-analysis-cycle-007]]
- Strategy snapshot: [[strategies/cycle-007]]
- Patterns updated:
  - [[patterns]] §"Factory precheck `score_direction` is polarity-buggy
    on lower-is-better metrics" (now 8-for-8)
  - [[patterns]] §"Factory precheck reports empty-detail `scope` /
    `fixed_surfaces` failures that contradict the standalone guard"
    (now 3-for-3)
  - [[patterns]] §"`revert_bookkeeping_keep_intent` is the universal
    verdict — substring-collision precheck bug gates every eval"
    (now 6-for-6 streak)
  - [[patterns]] §"Fresh-train variance can swamp claimed invariance"
    (NEW — first observation cycle-007 H2)
  - [[patterns]] §"Factory leakage-check fingerprints `factory.md`
    itself…" (NEW sub-class — dataset-name dispatch-key tokens)
  - [[patterns]] §"Cross-architecture recipe portability is NOT
    guaranteed" (2-for-2 after cycle-007 H2 Poisson partial port)
  - [[patterns]] §"Silent regression masked by the cache layer"
    (2-for-2 after cycle-007 R0 discovery)
- Project dashboard: [[factory_mffp]]
- Prior cycle close-outs: [[cycle-001-summary]], [[cycle-002-summary]],
  [[cycle-003-summary]], [[cycle-005-summary]], [[cycle-006-summary]]

## Closing footnote

Cycle-007 closes with a substantive engineering win — the project's
reproducible best moved meaningfully forward (0.04420 → 0.030408,
−31.2%) — even though both hypotheses formally REVERTed. The
combination of (a) `revert_bookkeeping_keep_intent` (H1: real
improvement, infra bugs flipped the verdict) and (b) genuine REVERT
(H2: real regression, infra bugs incidental) demonstrates the
factory's protocol is robust: branch preservation lets us bank wins
that the precheck cannot record, while the genuine-revert path
prevents us from banking losses we can identify as real. The
cycle-008 strategic priorities (BAR-undertraining fix, in-architecture
Poisson dispatch with invariance verification, hard-gate #11) directly
follow from the cycle-007 evidence.
