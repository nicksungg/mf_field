---
name: cycle-007-exp-10-build
description: Cycle-007 H2 (exp 10) — Builder + Reviewer phase. Decouple `fno_coreg_residual` MFRNP loss-weight recipe per dataset at `models/fno_coreg_residual/smoke_eval.py`. Single-file +29/-0 LOC additive commit 87f65b1 on `experiment/10-fno_coreg_residual-dataset-recipes` cut from `experiment/7-fno_coreg_lf_hf_transfer @ be36cba` (NOT from H1 branch — measured independently against honest baseline per Strategist R2). Adds module-scope `_DATASET_RECIPES = {"ifc_poisson": dict(poisson_hf_weight=2.0, poisson_lf_weight=0.25)}`, two new defaulted-to-1.0 SMOKE_DEFAULTS keys, a `resolve_fidelity_weights(dataset_name, p)` helper mirroring `fno_mf_stack/smoke_eval.py` sibling pattern, and dispatch via `p.update(_DATASET_RECIPES.get(args.dataset_name, {}))` immediately after `p = dict(SMOKE_DEFAULTS)`. Heat path is bit-equivalent to baseline by construction (defaults 1.0; gate on `"poisson" in dataset_name.lower()`). 2-epoch smoke verification passed on both datasets with correct dispatch log lines (`hf=1.0 lf=1.0` for ifc_heat, `hf=2.0 lf=0.25` for ifc_poisson). Reviewer PASS via `factory guard --check-scope=clean`; CEO PROCEED with documented leakage-check override on the dataset-name token `ifc_poisson` (public dispatch API, not ground truth). Same Builder role that triggered cycle-006 H1 dirty-tree-staging contamination used 0-of-2 redirects again — but as with H1, target file was at HEAD pre-edit so the rule held by structural easy case.
metadata:
  type: experiment
tags:
  - factory
  - experiment
  - factory_mffp
  - cycle-007
  - build
  - h2
  - fno_coreg_residual
  - dataset-recipes
  - mfrnp
  - poisson-recipe
  - leakage-check-override
  - builder-hygiene
project: factory_mffp
experiment_id: "010"
cycle: cycle-007
hypothesis_id: H2
phase: build
verdict: PROCEED
ceo_verdict_builder: PROCEED
ceo_verdict_reviewer: PROCEED
reviewer_verdict: PASS
date: 2026-06-02
branch: experiment/10-fno_coreg_residual-dataset-recipes
parent_branch: experiment/7-fno_coreg_lf_hf_transfer
parent_commit: be36cba
commit: 87f65b15e882ae285a782d114c96fd0e96ccea10
files_changed: 1
loc_delta: "+29/-0"
target_file: models/fno_coreg_residual/smoke_eval.py
sibling_pattern_file: models/fno_mf_stack/smoke_eval.py
dispatch_recipe_poisson: "poisson_hf_weight=2.0, poisson_lf_weight=0.25"
dispatch_recipe_heat: "empty (uniform 1.0/1.0 by SMOKE_DEFAULTS)"
heat_path_bit_equivalent_to_baseline: true
heat_gate_condition: "\"poisson\" in dataset_name.lower()"
smoke_ifc_heat_val_nRMSE_2ep: 0.4198
smoke_ifc_poisson_val_nRMSE_2ep: 0.2447
smoke_ifc_heat_dispatch_log: "[run] resolve_fidelity_weights: dataset=ifc_heat hf=1.0 lf=1.0"
smoke_ifc_poisson_dispatch_log: "[run] resolve_fidelity_weights: dataset=ifc_poisson hf=2.0 lf=0.25"
builder_redirects_used: "0 of 2"
dirty_files_at_start: 15
dirty_files_committed: 0
leakage_check_diff_risk_level: medium
leakage_check_diff_finding: "specific_value: 'ifc_poisson' from factory.md research_constraints[5] — false positive; ifc_poisson is the public DATASET NAME used as the dispatch key via args.dataset_name, NOT a ground-truth value"
leakage_check_hypothesis_risk_level: none
leakage_check_ceo_override: true
leakage_check_override_rationale: "Dataset name token is the public dispatch API; matches the same false-positive class as cycle-001 H1 shared-vocabulary findings ('description', 'frozen', 'ifc_raw'), not a real ground-truth leak."
source: factory-archivist
---

# Experiment #010 — Build phase: Cycle-007 H2 `fno_coreg_residual` per-dataset MFRNP recipe dispatch

## Hypothesis

**Cycle-007 H2 — FIX, single-file, LOSS_RECIPE_GAP (primary) / ARCHITECTURE_OVERFIT (secondary) failure mode.** Decouple the MFRNP HF/LF loss-weight recipe per dataset on `models/fno_coreg_residual/smoke_eval.py` so that Poisson-class ellipticPDE cells receive the Wang 2024 MFRNP `Poisson5_config.yaml` prescription (HF up-weighting 2.0, LF down-weighting 0.25) while Heat-class parabolic cells continue running with uniform 1.0/1.0 weights. Strategist R2 anti-pattern #5 forbids a Heat-specific `_DATASET_RECIPES` entry — Heat must fall through to `SMOKE_DEFAULTS` uniform-identity so the architecture cannot drift into Heat-specific tuning.

Expected impact (per Strategist R2 standalone projection from honest baseline 0.039578):
- `fno_coreg_residual` / `ifc_poisson`: 0.057564 → ≈ 0.05556 (cycle-006 H1 R4 cache reattach via the same recipe).
- `fno_coreg_residual` / `ifc_heat`: 0.030590 → 0.030590 (bit-equivalent to baseline; Heat path defaults preserved).
- Composite (standalone): 0.039578 → ≈ 0.0382 (delta ≈ −0.0016).
- Composite (stacked with H1): aspirational ≈ 0.0294 — but H2 is measured independently from `experiment/7@be36cba`, NOT chained onto H1's branch.
- R4 kill-switch: poisson > 0.089 (+20% over current `fno_coreg_residual` poisson 0.057564) ⇒ revert.

## Branch + commit

- **Branch**: `experiment/10-fno_coreg_residual-dataset-recipes`.
- **Base**: `experiment/7-fno_coreg_lf_hf_transfer @ be36cba` (cycle-005 H2 — honest baseline; **NOT** the cycle-007 H1 branch `experiment/9-…`).
- **Single new commit**: `87f65b1` — `feat(fno_coreg_residual): per-dataset MFRNP recipe dispatch (cycle-007 H2)`.
- **GitHub**: no PR, no push (`--no-github` honored — no `gh` / `git push` calls).
- **Builder branch policy compliance**: per Strategist R2 directive "H2 does NOT chain from H1's branch — each hypothesis measured independently against honest baseline" — Builder cut `experiment/10-…` directly from `be36cba`, satisfying the no-bundling rule and preserving the regression test against the H1 R4 result.

## What the Builder produced

`git diff --stat be36cba 87f65b1`:

| File | Lines | Purpose |
|---|---:|---|
| `models/fno_coreg_residual/smoke_eval.py` | **+29 / −0** | Module-scope `_DATASET_RECIPES`; two new defaulted-to-1.0 `SMOKE_DEFAULTS` keys (`poisson_hf_weight`, `poisson_lf_weight`); `resolve_fidelity_weights(dataset_name, p)` helper; dispatch via `p.update(_DATASET_RECIPES.get(args.dataset_name, {}))` after `p = dict(SMOKE_DEFAULTS)`; per-fidelity weight wiring `p["hf_loss_weight"] = hf_w; p["lf_loss_weights"] = tuple([lf_w] * max(n_levels - 1, 0))`; dispatch log line at runtime |
| **Total** | **+29 / −0, 1 file** | All under `models/fno_coreg_residual/**` |

**Critically additive**: every change is a new line — zero deletions, zero modifications to existing lines. `models/fno_coreg_residual/model.py`, `models/fno_coreg_residual/manifest.json`, `models/fno_coreg_residual/INSPIRATION.md`, and `models/fno_coreg_residual/full_config.json` are byte-identical to `be36cba` (confirmed via `git show --stat`). `SMOKE_DEFAULTS` original keys (`K=10`, `b_hidden=64`, `hidden=64`, `lr=3e-4`, epochs/schedule) are also byte-preserved — only two new keys appended.

## Mechanism (verbatim against Strategist H2 spec)

The Builder shipped four discrete additions, in this order:

1. **Module-scope recipe dispatch dict** (smoke_eval.py:41-48):
   ```python
   _DATASET_RECIPES = {
       "ifc_poisson": dict(poisson_hf_weight=2.0, poisson_lf_weight=0.25),
   }
   ```
   Only `ifc_poisson` has an entry — Heat path has zero entries (anti-pattern #5: no Heat-specific recipe). Comment block cites Wang 2024 MFRNP `Poisson5_config.yaml` as the source.

2. **Two new `SMOKE_DEFAULTS` keys** (smoke_eval.py:67-68):
   ```python
   poisson_hf_weight=1.0,
   poisson_lf_weight=1.0,
   ```
   Both default to `1.0` so that for any dataset name **not** in `_DATASET_RECIPES`, the uniform-identity weights are preserved. The `p.update(...)` dispatch only overrides these defaults when the dataset key is present.

3. **`resolve_fidelity_weights` helper** (smoke_eval.py:74-83):
   ```python
   def resolve_fidelity_weights(dataset_name: str, p: dict) -> tuple[float, float]:
       if dataset_name and "poisson" in dataset_name.lower():
           return (float(p["poisson_hf_weight"]), float(p["poisson_lf_weight"]))
       return (1.0, 1.0)
   ```
   The gate is `"poisson" in dataset_name.lower()` — for Heat the helper returns `(1.0, 1.0)` regardless of `p` contents. **Heat invariance is structural**: even if `p["poisson_hf_weight"]` were corrupted, the Heat path would still return `(1.0, 1.0)` because the gate short-circuits before reading `p`.

4. **Dispatch site in `run(args)`** (smoke_eval.py:200-216):
   ```python
   p = dict(SMOKE_DEFAULTS)
   p.update(_DATASET_RECIPES.get(args.dataset_name, {}))    # <- new
   ...
   n_levels = len(train_loaders)
   hf_w, lf_w = resolve_fidelity_weights(args.dataset_name, p)
   p["hf_loss_weight"] = hf_w                               # <- new
   p["lf_loss_weights"] = tuple([lf_w] * max(n_levels - 1, 0))  # <- new
   print(f"[run] resolve_fidelity_weights: dataset={args.dataset_name} hf={hf_w} lf={lf_w}")  # <- new
   ```
   The `p.update(...)` runs unconditionally; the `.get(key, {})` returns `{}` for non-poisson keys, so the update is a no-op for Heat. The `p["hf_loss_weight"]` / `p["lf_loss_weights"]` writes also run unconditionally — but for Heat they write the same `1.0`/`(1.0, 1.0, 1.0)` values that were already at `SMOKE_DEFAULTS` (n_levels=4 gives 3 LF levels per cycle-005 H2 setup).

This matches the sibling pattern at `models/fno_mf_stack/smoke_eval.py` (the Researcher's R1.5 reference implementation), where the same module-scope dispatch dict + helper exists for the same MFRNP recipe.

## Heat path invariance — provable by construction

The Heat path is byte-equivalent in **effect** to the baseline, even though the dispatch code runs unconditionally:

| Step | Heat (ifc_heat) | Poisson (ifc_poisson) |
|---|---|---|
| `p.update(_DATASET_RECIPES.get(args.dataset_name, {}))` | `.get("ifc_heat", {}) = {}` → no-op | `.get("ifc_poisson", {})` → overwrites `poisson_hf_weight=2.0, poisson_lf_weight=0.25` |
| `resolve_fidelity_weights(args.dataset_name, p)` | gate `"poisson" in "ifc_heat".lower()` False → returns `(1.0, 1.0)` | gate True → returns `(2.0, 0.25)` |
| `p["hf_loss_weight"]` value | 1.0 (== `SMOKE_DEFAULTS["hf_loss_weight"]`) | 2.0 (overridden) |
| `p["lf_loss_weights"]` value | `(1.0, 1.0, 1.0)` (== `SMOKE_DEFAULTS["lf_loss_weights"]` for n_levels=4) | `(0.25, 0.25, 0.25)` |

**Heat invariance gate is dual**: the `_DATASET_RECIPES` dict is empty for Heat keys AND the `resolve_fidelity_weights` helper gates on the substring. Either layer alone would suffice; both together make Heat regression structurally impossible without a code change.

The R4 200-epoch run on `fno_coreg_residual` × `ifc_heat` should **cache-hit** at code_hash level if the cache keys on syntactic `__code_hash__`. If the cache misses (which is likely — `__code_hash__` is content-addressed and the diff changes the source bytes even though Heat-path behavior is identical), the resulting fresh-train number should land within fresh-train stochasticity of the baseline 0.030590. R4 kill-switch on heat is implicit (no Strategist threshold set since Heat path is invariant by construction); operationally the Evaluator should flag any heat regression > 5% as an unexpected divergence.

## Pre-flight verification — PASSED both datasets

Builder ran the mandatory 2-epoch smoke on both target datasets (fresh trains; cache miss expected because the source bytes of `smoke_eval.py` changed):

| Dataset | best_val_nRMSE (2-ep) | dispatch log | Status |
|---|---:|---|---|
| `ifc_heat` | 0.4198 | `[run] resolve_fidelity_weights: dataset=ifc_heat hf=1.0 lf=1.0` ✓ | PASS |
| `ifc_poisson` | 0.2447 | `[run] resolve_fidelity_weights: dataset=ifc_poisson hf=2.0 lf=0.25` ✓ | PASS |

**2-epoch values are diagnostic only** — these are not the R4 leaderboard numbers. What the 2-epoch smoke proves is exactly what the Builder needed to prove:

1. The dispatch wiring runs at all (no `KeyError`, no `TypeError`, no shape mismatch).
2. The dispatch log line prints the **expected** weights for each dataset — `hf=1.0 lf=1.0` for Heat (uniform pass-through), `hf=2.0 lf=0.25` for Poisson (MFRNP recipe applied).
3. The training loop completes 2 epochs without numerical instability (no NaN losses; nRMSE values monotonically improving direction).

The full 200-epoch numbers will land at R4 via `bash scripts/cycle_eval.sh` on `experiment/10-fno_coreg_residual-dataset-recipes`.

## Reviewer PASS — substantive scope verification

`factory guard --check-scope` → **`clean`**. Reviewer's file-by-file scope verification confirmed:

- Only `models/fno_coreg_residual/smoke_eval.py` was modified (+29/-0). No `model.py`, `manifest.json`, `INSPIRATION.md`, `full_config.json` edits.
- `_DATASET_RECIPES = {"ifc_poisson": dict(poisson_hf_weight=2.0, poisson_lf_weight=0.25)}` matches the Strategist spec exactly (no Heat entry — anti-pattern #5 satisfied).
- `resolve_fidelity_weights` helper at module scope, gates on `"poisson" in dataset_name.lower()` per spec.
- `run()` dispatch via `p.update(_DATASET_RECIPES.get(args.dataset_name, {}))` placed immediately after `p = dict(SMOKE_DEFAULTS)` per spec.
- `SMOKE_DEFAULTS` original keys (K=10, b_hidden=64, hidden=64, lr=3e-4, epochs/schedule) **byte-preserved** — only two new defaulted-to-1.0 keys appended.
- Heat path bit-equivalent to baseline (defaults are 1.0; gate excludes "heat"-containing dataset names).
- Smoke verification logs the correct dispatch lines for both datasets (`hf=1.0 lf=1.0` for Heat, `hf=2.0 lf=0.25` for Poisson).
- No fixed-surface edits (`data/`, `eval/`, `baselines/`, `references/`, `scripts/`, `factory.md`, `README.md` all clean).
- Builder honored the [[dirty-tree-staging]] memory — only the H2 target file is in commit `87f65b1`; the 15 pre-existing dirty files (`bench/`, `data_adapters/`, `fairbench/`, `models/_grid_smoketest.py`, `references/external_sota/`, `results/...`, `scripts/smoke_one.sbatch`) were left untouched.

CEO independently spot-checked the diff (`git diff be36cba HEAD models/fno_coreg_residual/smoke_eval.py`), confirmed the file count, line count, and byte-preservation claims, and ratified Reviewer PASS via `.factory/reviews/ceo-verdict-reviewer.md` (PROCEED).

## Leakage-check override — dataset-name token false positive

`factory leakage-check` on the diff returned `risk_level: medium` with a single finding: the token `ifc_poisson` in the diff matches `ifc_poisson` in `factory.md` line 42 (`research_constraints[5]` lists smoke datasets). CEO override applied because:

1. **`ifc_poisson` is the public DATASET NAME used as the dispatch key via `args.dataset_name`** — it is the **API contract**, not a ground-truth value. Any builder that wants to gate behavior on `ifc_poisson` (as `models/fno_mf_stack/smoke_eval.py` already does) will trip the same flag.
2. **The hypothesis-level leakage check returned `risk_level: none`** before any code was written — the leak is purely a code-vs-`factory.md` collision, not a hypothesis-derivation issue.
3. **This matches the existing false-positive class** documented at [[patterns]] §"Factory leakage-check fingerprints `factory.md` itself and produces false-positive medium-risk on shared vocabulary" — the scanner does string-substring matching without distinguishing **value-class semantics** (eval-weight constant vs. paper-baseline metric vs. **public dispatch key**).

**New sub-pattern recorded** (extends the existing leakage-check pattern): the leakage-check failure mode now includes **dataset-name tokens used as public dispatch keys**. This is a distinct sub-class from the cycle-001 shared-vocabulary findings (`description`, `frozen`, `ifc_raw`) and the cycle-001 H2 numerical-substring class (`0.10`, `0.20`): the dataset-name token is the **explicit API** the builder dispatches on, not incidental shared vocabulary. Any future builder that adds a dataset-conditional branch will trip the same flag.

**Distinction from the cycle-007 H1 precheck infra bugs** ([[cycle-007-exp-9]] §verdict): the H1 case involved three independent precheck failures — `score_direction` polarity bug (8-for-8), empty-detail `scope`, empty-detail `fixed_surfaces` — all of which are bugs in **`precheck.py` itself** (out-of-cycle remote-factory-main code). The H2 leakage-check finding is a different infrastructure subsystem (`factory leakage-check`, not `precheck.py`), a different failure class (substring-collision, not polarity inversion), and lives in a different file. They are two separate infra bugs in the same family ("the factory scanner produces false positives when its corpus includes `factory.md`"), but the root causes and fix sites are distinct. See [[patterns]] §"Factory precheck `score_direction` is polarity-buggy" (H1 case) vs. §"Factory leakage-check fingerprints `factory.md` itself" (this H2 case).

**Workflow rule re-confirmed**: when leakage-check reports `risk_level=medium` on a dataset-name token, the CEO must inspect whether the token is a **public dispatch key** (e.g., `args.dataset_name` matches against it). If yes — override; the token is API, not leak. If no — investigate further.

## Cross-cycle hygiene update (Builder role)

**Same Builder role that triggered cycle-006 H1 dirty-tree-staging contamination produced its second clean named-file commit in this cycle on the first attempt — zero redirects burned again.**

| Cycle | Builder phase | Dirty files at start | Dirty files committed | Redirects used | Outcome |
|---|---|---:|---:|---|---|
| **cycle-006 H1** ([[cycle-006-exp-8]]) | `git add <named file>` on already-dirty `smoke_eval.py` + `manifest.json` | ~15 | **357 contaminating LOC** | **1 of 2** | Recovery commit `59b741f` (+30/-3) after `git reset --hard` |
| **cycle-007 H1** ([[cycle-007-exp-9-build]]) | `git add models/fno_coregionalization/model.py` on a file at HEAD | **15** | **0** | **0 of 2** | First-attempt commit `1249f2d` (+9/-7) |
| **cycle-007 H2** (this note) | `git add models/fno_coreg_residual/smoke_eval.py` on a file at HEAD | **15** | **0** | **0 of 2** | First-attempt commit `87f65b1` (+29/-0) |

**Caveat (same as H1) — rule held by structural easy case, not by improved process discipline.** Target file `models/fno_coreg_residual/smoke_eval.py` was at HEAD before Builder edits (not in the pre-existing 15-file dirty diff), so `git add <file>` captured only the H2 hypothesis diff. The [[dirty-tree-staging]] auto-memory rule did its job (Builder noted the 15 dirty files and used `git add <specific file>`), but the test was easier because the target wasn't pre-dirty. The process gates from [[patterns]] §"Builder clean-isolation requires pre-clean working tree" (pre-clean at session start / `git checkout HEAD -- <file>` / staged-diff audit) remain mandatory for general safety — and the next Builder who targets a file that **is** pre-dirty will face the same trap that contaminated cycle-006 H1.

**2-for-2 within cycle-007 is a positive signal but not yet evidence of behavior change.** What it does demonstrate: the Strategist's hypothesis-design discipline (picking small surgical files for the H1/H2 specs) is incidentally protecting the Builder by avoiding the dirty-file landmines. A counterfactual where the next hypothesis targets one of the 15 pre-existing dirty files would re-test the actual process compliance.

## Hard-gate results

- **Surface guard**: `factory guard --check-scope` → `clean` against `be36cba` baseline.
- **Single-file constraint per Strategist directive**: satisfied — only `models/fno_coreg_residual/smoke_eval.py` modified.
- **No `SMOKE_DEFAULTS` drift on original keys** (Strategist anti-pattern #3): satisfied — `K=10`, `b_hidden=64`, `hidden=64`, `lr=3e-4`, all epochs/schedule keys byte-preserved; the two new keys are appended-only and default to uniform 1.0/1.0 so the existing semantics are unchanged.
- **No fixed-surface edits** (Strategist anti-pattern #7): satisfied.
- **No bundling with H1** (Strategist anti-pattern #1): satisfied — H2 cut from `experiment/7@be36cba`, not from `experiment/9-…`.
- **No Heat-specific `_DATASET_RECIPES` entry** (Strategist anti-pattern #5): satisfied — only `ifc_poisson` key exists; Heat falls through to uniform-identity defaults.
- **No transolver changes** (Strategist anti-pattern #6): satisfied.
- **No `mf_fno_bar_residual` new family** (Strategist anti-pattern #4): satisfied (deferred to cycle-008).
- **No expected-effect numbers re-derived from ground-truth** (Strategist anti-pattern #8): satisfied — Builder's 2-epoch numbers are diagnostic only, not predictions.
- **`--no-github` mode**: satisfied (no `gh` / `git push`).
- **Leakage-check override documented**: yes — CEO override applied with rationale (dataset name is public dispatch API, not ground truth); hypothesis-level leakage was `none`.

## Implementation notes (carry into R4 interpretation)

- **Cache behavior**: the source bytes of `models/fno_coreg_residual/smoke_eval.py` changed, so the `__code_hash__` for the `fno_coreg_residual` cell changes. Expect cache MISS on both `fno_coreg_residual / ifc_heat` and `fno_coreg_residual / ifc_poisson` at R4. Other 12 cells (other 7 families × 2 datasets, minus the two `fno_coreg_residual` cells) should cache-hit because their source bytes are unchanged.
- **Heat regression test**: at R4 expect heat `≈ 0.030590` (cycle-007 R0 honest baseline value for `fno_coreg_residual / ifc_heat`), within fresh-train stochasticity. The Heat path is bit-equivalent **by construction** even though the cache misses; any deviation > 5% from 0.030590 is a fresh-train signal, not a semantic change.
- **Poisson improvement test**: at R4 expect poisson `≈ 0.05556` (the cycle-006 H1 R4 `fno_coreg_residual / ifc_poisson` cache reattach target), down from 0.057564. R4 kill-switch trip if poisson > 0.089.
- **Stacking with H1**: H1 (constructor fix at `models/fno_coregionalization/model.py`) and H2 (recipe dispatch at `models/fno_coreg_residual/smoke_eval.py`) touch **disjoint files in disjoint families**. The R4 composite for H2 standalone uses honest baseline 0.039578; the projected stacked composite (H1 + H2) is ≈ 0.0294 (aspirational, reachable only if both branches' R4 numbers compose linearly). Whether to merge both branches is a cycle-008 entry decision, not an in-cycle bundling.
- **Resume-state compatibility**: not applicable — `_DATASET_RECIPES` dispatch only changes loss-weight scalars, not model architecture; no `state_dict` keys change. The cache-miss is purely from the `__code_hash__` change on `smoke_eval.py`, not from a wire-format incompatibility.

## Anti-patterns explicitly NOT triggered

- No bundling with H1 (Strategist anti-pattern #1) — H2 cut from `experiment/7@be36cba`, not from H1 branch.
- No fallback kwarg (Strategist anti-pattern #2) — N/A here (no constructor change), but spirit preserved: `_DATASET_RECIPES.get(..., {})` is explicit-dispatch with empty-dict fallback, not silent kwarg drift.
- No `SMOKE_DEFAULTS` drift on existing keys (Strategist anti-pattern #3) — only **new** keys appended with uniform-identity defaults.
- No `mf_fno_bar_residual` new family (Strategist anti-pattern #4) — deferred to cycle-008.
- No `_DATASET_RECIPES` Heat entry (Strategist anti-pattern #5) — only `ifc_poisson` key exists.
- No transolver changes (Strategist anti-pattern #6).
- No fixed-surface edits (Strategist anti-pattern #7).
- No expected-effect numbers re-derived from ground-truth (Strategist anti-pattern #8).

## CEO sign-off (both phases)

- **CEO verdict on Builder** (`.factory/reviews/ceo-verdict-builder.md`, 2026-06-02): **PROCEED**. Leakage-check override on `ifc_poisson` dataset-name token applied with documented rationale.
- **CEO verdict on Reviewer** (`.factory/reviews/ceo-verdict-reviewer.md`, 2026-06-02): **PROCEED** (ratify Reviewer PASS).
- Diff is minimum-additive (+29/-0, 1 file); `model.py` / `manifest.json` / `INSPIRATION.md` / `full_config.json` all byte-preserved; smoke completes on both datasets with correct dispatch logs; scope guard clean; [[dirty-tree-staging]] memory honored; sibling pattern at `models/fno_mf_stack/smoke_eval.py` is the load-bearing reference implementation.
- Ready for **R4** (post-change eval, 200-epoch fresh smoke on `experiment/10-fno_coreg_residual-dataset-recipes`).

## Pending (R4 / R5)

- 200-epoch run via `bash scripts/cycle_eval.sh` on `experiment/10-fno_coreg_residual-dataset-recipes`. Cache MISS expected on **both** `fno_coreg_residual` cells (heat + poisson) due to `__code_hash__` change; other 12 cells should cache-hit.
- **R4 kill-switch**: if fresh smoke run produces `fno_coreg_residual / ifc_poisson > 0.089` (+20% over honest baseline 0.057564), revert immediately.
- **R4 Heat regression check**: if `fno_coreg_residual / ifc_heat` deviates > 5% from baseline 0.030590, flag for fresh-train stochasticity vs. unexpected semantic divergence investigation (Heat path is bit-equivalent by construction; > 5% deviation would be a strong signal of a non-additive interaction).
- **R5 verdict logic**: monotonic check uses **0.039578** as honest baseline (Strategist R2 contract). The composite improvement under standalone H2 is small (≈ −0.0016) and may itself trigger the `score_direction` polarity bug (8-of-8 streak); CEO should pre-register the override.
- **Expected impact at R4 (standalone)**: composite `0.039578 → ≈ 0.0382` (delta ≈ −0.0016); `fno_coreg_residual / ifc_poisson` `0.057564 → ≈ 0.05556`; `fno_coreg_residual / ifc_heat` invariant. Poisson winner family may flip from `fno_mf_stack @ 0.05961` to `fno_coreg_residual @ 0.05556` (cross-family winner reshuffle at the poisson cell).

## Links

- Project dashboard: [[factory_mffp]]
- Cycle-007 strategy: `.factory/strategy/current.md`, `.factory/strategy/research.md` (R1.5)
- CEO Builder verdict: `.factory/reviews/ceo-verdict-builder.md`
- CEO Reviewer verdict: `.factory/reviews/ceo-verdict-reviewer.md`
- Builder report: `.factory/reviews/builder-latest.md`
- Reviewer report: `.factory/reviews/reviewer-latest.md`
- Cycle-007 H1 build (sibling hypothesis, separate branch): [[cycle-007-exp-9-build]], [[cycle-007-exp-9]]
- Failure analysis (R1) — root cause of `LOSS_RECIPE_GAP` / `ARCHITECTURE_OVERFIT`: [[failure-analysis-cycle-007]]
- Cycle-006 H1 (the carry-over: cross-architecture recipe portability is NOT guaranteed): [[cycle-006-exp-8]], [[cycle-006-summary]]
- Cycle-005 H2 (the project-best whose `experiment/7@be36cba` this H2 cuts from): [[factory_mffp-007]]
- Sibling reference implementation (Researcher R1.5): `models/fno_mf_stack/smoke_eval.py` (same `_DATASET_RECIPES` + `resolve_fidelity_weights` pattern, predates this H2)
- Related patterns:
  [[patterns]] §"Factory leakage-check fingerprints `factory.md` itself and produces false-positive medium-risk on shared vocabulary" (extended with new dataset-name-token sub-class),
  [[patterns]] §"Builder clean-isolation requires pre-clean working tree",
  [[patterns]] §"Cross-architecture recipe portability is NOT guaranteed" (cycle-006 carry-over; the H2 dispatch is designed to expose, not hide, this asymmetry)
- Auto-memory honored: [[dirty-tree-staging]]
- Commit: `87f65b15e882ae285a782d114c96fd0e96ccea10` on branch `experiment/10-fno_coreg_residual-dataset-recipes`
- Base: `experiment/7-fno_coreg_lf_hf_transfer @ be36cba`
- Diff: `git diff be36cba..87f65b1 models/fno_coreg_residual/smoke_eval.py` (+29 / -0, 1 file)
