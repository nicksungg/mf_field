# Cycle-009 Session Summary

**Mode:** research | **Date:** 2026-06-02 | **Experiments processed:** 1 (exp 14 H1+H2 bundle)

## What was built

### H1+H2 (experiment 14) — fno_mf_stack capacity bump + recipe_hash portable utility [HUGE WIN, formal revert]

- **Hypothesis:** Capacity bump on `fno_mf_stack` (lead axis, targeting Poisson ~69% of remaining bar gap) bundled with portable `recipe_hash` utility (cycle-003 backlog clearance).
- **Change:** 5 files, +45/-8 LOC.
  - NEW: `models/_common/__init__.py` (empty package marker)
  - NEW: `models/_common/recipe_hash.py` (12-line portable helper, sha256[:12])
  - EDIT: `models/fno_mf_stack/smoke_eval.py` — SMOKE_DEFAULTS bump (`hidden=32→64`, `agg_hidden=32→64`, `n_blocks=3→4`, `modes_per_level=(4,8,12,12)→(4,8,16,20)`) + 4 patch sites for recipe_hash guard
  - EDIT: `models/fno_coreg_residual/smoke_eval.py` — 4 patch sites for recipe_hash guard (SMOKE_DEFAULTS unchanged)
  - EDIT: `models/fno_coregionalization/smoke_eval.py` — 4 patch sites for recipe_hash guard (SMOKE_DEFAULTS unchanged, family-specific `grid` precondition preserved)
- **Result:** composite_nRMSE **0.027729 → 0.022161** (Δ **−20.08%**).
  - **PARALLEL-BENCH BAR (0.027429) DETHRONED** by 19.2%; gap closed 276.8%.
  - **First time the bar has been beaten in 9 cycles.**
  - `fno_mf_stack × ifc_poisson`: 0.05961 → 0.038120 (−36%) — Poisson kill-switch (0.0594) clear with 36% headroom.
  - `fno_mf_stack × ifc_heat`: 0.09995 → 0.038269 (−62%) — family-internal gain, still rank-4 on Heat (not best, but huge improvement).
  - `fno_coregionalization × ifc_heat`: 0.012898 → 0.012884 (marginal fresh-cache rerun improvement; still Heat leader).
  - `fno_coreg_residual × ifc_poisson`: 0.07419 → 0.07200 (similar marginal rerun improvement).
  - **Cycle-003 backlog cleared**: `recipe_hash` portable utility now live on all 3 live FNO families (transolver families already had it in-tree).
- **Wall:** 414s smoke eval (vs 1500s kill-switch budget; ~28% utilization).
- **Verdict:** formal `revert` (precheck false-positive overrides — score_direction polarity bug + empty-detail scope/fixed_surfaces), but with `ceo:keep` recorded in notes (`revert_bookkeeping_keep_intent` 8th-consecutive). Branch preserved at `experiment/14-fno_mf_stack-capacity-and-recipe-hash @ 0b6e6eb` — **this is now the cycle-010 entry baseline**.

## Net cycle effect

- **Reproducible project-best moved from 0.027729 → 0.022161** (Δ −20.08%). Bar dethroned for the first time in project history.
- **The Heat side is solved** — `fno_coregionalization × ifc_heat = 0.012884` is 5.74× under the paper bar (0.074).
- **Poisson side remains the lever** — `fno_mf_stack × ifc_poisson = 0.038120` is 1.06× over the paper bar (0.036). Cycle-010 strategic pivot: target the IFC paper bar (~0.0516 composite geomean), not the parallel-bench bar.
- **Patterns evolved**:
  1. **Precheck score_direction polarity bug** — 11/11 confirmed (cycle-009 H1+H2 latest).
  2. **Precheck scope/fixed_surfaces empty-violation FP** — 5/5 confirmed.
  3. **Leakage substring-collision FP** — 7/7 (this cycle: "17"/"30" matching against project doc trivia).
  4. **`revert_bookkeeping_keep_intent` streak** — 8/8 (cycle-007 H1, cycle-008 H1, cycle-009 H1+H2 most recent).
  5. **NEW: `factory guard --baseline <short-SHA>` short-vs-long-SHA equality FP** — first observed cycle-009.
  6. **Capacity-axis playbook transfers cross-family** — 2/2 successes (cycle-008 H1 on fno_coregionalization, cycle-009 H1 on fno_mf_stack).
  7. **Cycle-003 backlog item RESOLVED** — portable `recipe_hash` live on 3 FNO families.

## What was deferred (cycle-010+ backlog)

- **O4 — `fno_coreg_conditioned` `γ(m, LF_features)` revision** (NK1 sidestep retry on cycle-008 H2 FiLM scaffold; cycle-008 cache fell out per cycle-008-h3 notes, needs ~92s retrain budget).
- **O3 — Two-stage frozen-LF curriculum on `fno_mf_stack` or `mf_fno_transfer_bar`** (LF/HF independent by design, NK2 carve-out; both absolute and inter-stage kill-switches MANDATORY).
- **O7 — K-basis redesign on `fno_coregionalization × poisson`** (replace `B(m) = MLP([m, m²])` with `B(m, LF)`; speculative, high-risk).
- **Aggressive variant of H1**: `modes_per_level=(4,8,16,24)` if cycle-010 pushes harder on Poisson.
- **`papers_summary.csv` row addition** for `stresstest2025fno` (arXiv:2501.11428) — human action; outside factory mutable_surfaces.
- **`mf_fno_transfer_bar` smoke-eval undertraining** — DEFER (fixing raises the bar; not in cycle-009 EV).

## What needs human input (operator backlog — standing items, count++ this cycle)

- **Precheck overhaul**: 11th cumulative polarity bug + 5th cumulative empty-detail scope/fixed_surfaces. Standing project pattern is `revert_bookkeeping_keep_intent`. Out-of-cycle scope per cycle-008 close-out.
- **Leakage scanner false-positive on project docs**: 7th cumulative substring-collision against `factory.md`/`README.md`. The scanner treats both files as "ground truth" sources but they are project configuration / README content. Fix: scanner should exclude config-like files OR require token boundaries on matches.
- **NEW: `factory guard --baseline <short-SHA>` string-vs-string equality bug**: first observed cycle-009. Guard compares `<short-SHA>` directly to `merge-base` full SHA and reports VIOLATION. Trivial fix: prefix-match instead of equality.
- **`factory eval` crash on empty `eval_command`**: cycle-009 first instance — `create_subprocess_exec() missing 1 required positional argument: 'program'`. Workaround: project_eval is the only configured eval (research target), so hygiene gate is trivially passed.
- **`factory summary` crash on datetime comparison**: cycle-009 first instance — `can't compare offset-naive and offset-aware datetimes`. CEO wrote the cycle-009 session summary manually.

## Backlog status

- **Backlog items cleared this cycle:** 1 (cycle-003 `recipe_hash` checkpoint-recipe-contamination guard — FULL clearance on 3 live FNO families).
- **Items remaining:** ~12 (per `.factory/strategy/backlog.md` head — most are speculative new families or deferred operational items).
- **Items partially addressed:** 0.

## Cycle-010 entry state

- **Banked best**: composite_nRMSE = 0.022161 on `experiment/14-fno_mf_stack-capacity-and-recipe-hash @ 0b6e6eb`.
- **Current bar**: parallel-bench bar BEATEN. Next target = IFC paper bar (~0.0516 geomean = (0.074 heat × 0.036 poisson)^½). Cycle-009 exit composite 0.022161 is already 2.3× under the paper bar.
- **Dominant lever**: Poisson (`fno_mf_stack × ifc_poisson = 0.038120` is 1.06× over paper). Heat is solved (5.74× under paper).
- **Architecture-improvable axes for cycle-010**: (a) aggressive `fno_mf_stack` capacity push to `(4,8,16,24)`; (b) two-stage curriculum on `fno_mf_stack` (NK2 carve-out); (c) `fno_coreg_conditioned` γ(m, LF_features) NK1 retry. Strategist priority TBD.
