---
name: cycle-007-exp-9-build
description: Cycle-007 H1 (exp 9) — Builder + Reviewer phase. Repair FNOCoregionalization constructor at models/fno_coregionalization/model.py to accept anisotropic (modes_h, modes_w, grid: tuple) and propagate to FNOBlock. Single-file +9/-7 LOC commit 1249f2d on experiment/9-fno_coregionalization-constructor-fix cut from be36cba. 2-epoch smoke verification passed on both ifc_heat (val 2.29e-1) and ifc_poisson (val 2.71e-1) before commit. Inner SpectralConv2d / FNOBlock byte-identical; smoke_eval.py SMOKE_DEFAULTS + cycle-005 H2 LF→HF schedule byte-preserved. Reviewer PASS via factory guard --check-scope=clean; CEO PROCEED. Cross-cycle hygiene win: same Builder role that triggered the cycle-006 H1 dirty-tree-staging contamination produced a clean named-file commit here on the first attempt — no redirects burned.
metadata:
  type: experiment
tags:
  - factory
  - experiment
  - factory_mffp
  - cycle-007
  - build
  - h1
  - fno_coregionalization
  - constructor-fix
  - anisotropic-modes
  - builder-hygiene
project: factory_mffp
experiment_id: "009"
cycle: cycle-007
hypothesis_id: H1
phase: build
verdict: PROCEED
ceo_verdict_builder: PROCEED
ceo_verdict_reviewer: PROCEED
reviewer_verdict: PASS
date: 2026-06-02
branch: experiment/9-fno_coregionalization-constructor-fix
parent_branch: experiment/7-fno_coreg_lf_hf_transfer
parent_commit: be36cba
commit: 1249f2de87bfd15001c67a22ee4ea66343fecd2d
files_changed: 1
loc_delta: "+9/-7"
target_file: models/fno_coregionalization/model.py
smoke_ifc_heat_best_val_nRMSE: 0.22934
smoke_ifc_poisson_best_val_nRMSE: 0.27102
smoke_params: 1190708
builder_redirects_used: "0 of 2"
dirty_files_at_start: 15
dirty_files_committed: 0
source: factory-archivist
---

# Experiment #009 — Build phase: Cycle-007 H1 `fno_coregionalization` constructor fix

## Hypothesis

**Cycle-007 H1 — FIX, single-file, COMMITTED_TREE_BROKEN failure mode.** Repair the outer `FNOCoregionalization.__init__` in `models/fno_coregionalization/model.py` so the wrapper accepts the anisotropic signature `(modes_h, modes_w, grid: tuple)` that the call site at `smoke_eval.py:265` already passes. Inner classes (`SpectralConv2d`, `FNOBlock`) already accept `(modes_h, modes_w)`; the entire cycle-005 H2 LF→HF schedule (`smoke_eval.py:64-411`) is intact. The cycle-005 H2 baseline 0.029357 was load-bearing on a never-committed dirty `model.py` wiped by the cycle-006 H1 Builder's `git reset --hard`; this commit reconstructs the wrapper-level fix on the committed tree so the cell becomes runnable again.

Expected impact (per Strategist R2, anchored to cached cycle-005 numbers):
- `fno_coregionalization` / `ifc_heat`: NaN/error → ≈ 0.01551 (cycle-005 H2 cache reattach via byte-identical `smoke_eval.py`).
- Composite: 0.039578 → ≈ 0.0304 (delta ≈ −0.0092).
- R4 kill-switch: heat > 0.0194 ⇒ revert.

## Branch + commit

- **Branch**: `experiment/9-fno_coregionalization-constructor-fix`.
- **Base**: `experiment/7-fno_coreg_lf_hf_transfer @ be36cba` (cycle-005 H2 — honest baseline; NOT main, NOT cycle-006's experiment/8).
- **Single new commit**: `1249f2d` — `fix(fno_coregionalization): repair anisotropic-modes constructor (cycle-007 H1)`.
- **GitHub**: no PR, no push (`--no-github` honored — no `gh` / `git push` calls).

## What the Builder produced

`git diff --stat be36cba 1249f2d`:

| File | Lines | Purpose |
|---|---:|---|
| `models/fno_coregionalization/model.py` | **+9 / −7** | Constructor signature swap `modes:int, grid_size:int → modes_h:int, modes_w:int, grid:tuple`; propagate to `FNOBlock(hidden_channels, modes_h, modes_w)`; `self.grid = (int(grid[0]), int(grid[1]))`; `coord_grid` built from `H, W = self.grid`; `forward()` reads `H, W = self.grid` |
| **Total** | **+9 / −7, 1 file** | All under `models/fno_coregionalization/**` |

**Critically:** `smoke_eval.py`, `manifest.json`, and the inner `SpectralConv2d` / `FNOBlock` class bodies are byte-identical to be36cba. The cycle-005 H2 two-stage schedule (`pretrain_frac=0.25, pretrain_lr=1e-3, finetune_lr=3e-4`, fresh `Adam` + `CosineAnnealingLR` per stage) is fully preserved, satisfying the R4 cache-reattach precondition for the cycle-005 cached 0.01551 number.

## Mechanism (verbatim against Strategist H1 spec)

Constructor signature swap (model.py:83-103, the only edit):
- **Before**: `modes: int = 12, grid_size: int = 64` ⇒ `self.grid_size = grid_size`, builds `FNOBlock(hidden_channels, modes, modes)`, `coord_grid` from `torch.linspace(-1.0, 1.0, grid_size)` square, `forward` reads `H = W = self.grid_size`.
- **After**: `modes_h: int = 12, modes_w: int = 12, grid: tuple = (64, 64)` ⇒ `self.grid = (int(grid[0]), int(grid[1]))`, builds `FNOBlock(hidden_channels, modes_h, modes_w)`, `coord_grid` from `ys = torch.linspace(-1.0, 1.0, H); xs = torch.linspace(-1.0, 1.0, W)` with `H, W = self.grid`, `forward` reads `H, W = self.grid`.
- **No fallback `modes=` kwarg** — per Strategist anti-pattern #2 (silently masks future regressions). Future callers MUST use the anisotropic kwargs explicitly.

This matches the sibling pattern at `models/mf_fno_transfer_bar/model.py:62-94` (Researcher's reference implementation).

## Pre-flight verification — PASSED both datasets

Builder ran the mandatory 2-epoch smoke on both target datasets (fresh trains; cache miss as expected — the `__code_hash__` for `models/fno_coregionalization/` changes with the constructor edit; resume-guard at `smoke_eval.py:304-318` is **not** triggered because there is no prior checkpoint matching the new constructor hash):

| Dataset | best_val_nRMSE | params | JSON output | Status |
|---|---:|---:|---|---|
| `ifc_heat` | **0.22934** | 1,190,708 | `/tmp/c007_h1_heat.json` | PASS |
| `ifc_poisson` | **0.27102** | 1,190,772 | `/tmp/c007_h1_poisson.json` | PASS |

**2-epoch values are expected for undertrained runs and do not invalidate the test** — the R4 kill-switch (heat ≤ 0.0194) is evaluated at the full 200-epoch schedule, not at 2 epochs. Both smoke runs completed cleanly with no constructor errors and no shape mismatches, confirming the (modes_h, modes_w, grid) propagation lands correctly at all call sites.

Smoke invocation: `$MFFP_PY models/fno_coregionalization/smoke_eval.py --epochs 2 --dataset_dir data/{ifc_heat,ifc_poisson} --dataset_name {ifc_heat,ifc_poisson} --out /tmp/x.json --ckpt_dir /tmp/c --seed 0`. (Builder noted the orchestrator template omitted `--dataset_name`; supplied it because the call site at `smoke_eval.py:247` resolves grid from `args.dataset_name`.)

## Reviewer PASS — substantive scope verification

`factory guard --check-scope` → **`clean`**. Reviewer's file-by-file scope verification confirmed:

- Only `models/fno_coregionalization/model.py` was modified (+9/-7).
- Constructor signature is `(modes_h, modes_w, grid, ...)` — no fallback `modes=` kwarg.
- `SpectralConv2d` and `FNOBlock` inner classes are byte-identical.
- `smoke_eval.py` and `manifest.json` are byte-preserved → `SMOKE_DEFAULTS` and the cycle-005 H2 LF→HF schedule are intact; cycle-005 cached 0.01551 heat regression test remains valid.
- No fixed-surface edits (`data/`, `eval/`, `baselines/`, `references/`, `scripts/`, `factory.md`, `README.md` all clean).
- Builder honored the [[dirty-tree-staging]] memory — only the H1 target file is in commit `1249f2d`; the 15 pre-existing dirty files (`bench/`, `data_adapters/`, `fairbench/`, `models/_grid_smoketest.py`, `references/external_sota/`, `results/...`, `scripts/smoke_one.sbatch`) were left untouched.

CEO independently spot-checked the diff (`git diff be36cba HEAD models/fno_coregionalization/model.py`), confirmed the file count, line count, and byte-preservation claims, and ratified Reviewer PASS via `ceo-verdict-reviewer.md` (PROCEED).

## Cross-cycle hygiene win (load-bearing for [[patterns]])

**Same Builder role that triggered the cycle-006 H1 dirty-tree-staging contamination produced a clean named-file commit here on the first attempt — zero redirects burned.**

| Cycle | Builder phase | Dirty files at start | Dirty files committed | Redirects used | Outcome |
|---|---|---:|---:|---|---|
| **cycle-006 H1** (exp 8, [[cycle-006-exp-8]]) | `git add <named file>` on already-dirty `smoke_eval.py` + `manifest.json` | ~15 (data_adapters migration cruft) | **357 contaminating LOC** (hidden=64→32, supported_datasets 2→15, data_adapters migration) | **1 of 2** (recovered via `git reset --hard` + surgical re-apply) | First attempt confounded; recovery commit `59b741f` clean at +30/-3 |
| **cycle-007 H1** (exp 9, this note) | `git add models/fno_coregionalization/model.py` on a file that was **at HEAD** (not pre-dirty) | **15** (same data_adapters / bench / fairbench / results / scripts cruft, still untouched) | **0** | **0 of 2** | First-attempt commit `1249f2d` clean at +9/-7 |

The mechanical difference: cycle-006 H1 named files that were already in the working-tree diff before Builder edits, so `git add <file>` swept in the pre-existing dirty state. Cycle-007 H1's target file (`models/fno_coregionalization/model.py`) was at HEAD before Builder edits, so `git add <file>` captured only the hypothesis diff. **The [[dirty-tree-staging]] auto-memory rule held by accident here** — the file the H1 hypothesis touched happened not to be one of the 15 pre-existing dirty files. The rule still needs the cycle-006 process gates ([[patterns]] §"Builder clean-isolation requires pre-clean working tree", steps 1-3) for general safety; this cycle was a structural easy case, not a process improvement.

## Hard-gate results

- **Surface guard**: `factory guard --check-scope` → `clean` against be36cba baseline.
- **Single-file constraint per Strategist directive**: satisfied — only `models/fno_coregionalization/model.py` modified.
- **No `SMOKE_DEFAULTS` drift** (Strategist anti-pattern #3): satisfied — `smoke_eval.py` byte-identical.
- **No fallback `modes=` kwarg** (Strategist anti-pattern #2): satisfied — explicit `modes_h, modes_w` only.
- **No fixed-surface edits** (Strategist anti-pattern #7): satisfied.
- **`--no-github` mode**: satisfied (no `gh` / `git push`).

## Implementation notes (carry into R4 interpretation)

- **Resume compatibility**: per Researcher R1.5 finding, `smoke_eval.py:304-318` already checks `grid` tuple identity, so the constructor-fix's `grid_size → grid: tuple` swap is structurally resume-compatible. However, the `__code_hash__` change forces a cache miss on `models/fno_coregionalization/` at R4 — expect a ~30s fresh smoke retrain. The cycle-005 H2 cached 0.01551 heat number is reachable only if the new fresh run reproduces it; R5 kill-switch lets ≤0.0194 (+25% headroom) count as success.
- **Anisotropic capacity is identical to the prior isotropic case** on square grids (ifc_heat and ifc_poisson both run at 64×64). `modes_h = modes_w = 12` and `grid = (64, 64)` map exactly to the prior `modes=12, grid_size=64` semantics, so any deviation from the cached 0.01551 at R4 is a fresh-train-stochasticity signal, **not** an architectural change signal. Param count `1,190,708` (vs cycle-005 H2 model footprint) is a quick sanity check the Evaluator can run at R4.
- **Constructor signature now matches `mf_fno_transfer_bar`** (`models/mf_fno_transfer_bar/model.py:62-94`) per Researcher reference implementation — anisotropic-modes signature is now consistent across all FNO families in the project.

## Anti-patterns explicitly NOT triggered

- No bundling with H2 recipe changes (Strategist anti-pattern #1) — H2 will cut a separate branch from `experiment/7@be36cba`, not from this H1 branch.
- No fallback kwarg (Strategist anti-pattern #2) — `modes_h, modes_w, grid` are explicit-only.
- No `SMOKE_DEFAULTS` drift (Strategist anti-pattern #3).
- No `mf_fno_bar_residual` new family (Strategist anti-pattern #4, deferred to cycle-008).
- No `_DATASET_RECIPES` Heat entry (Strategist anti-pattern #5, H2 territory).
- No transolver changes (Strategist anti-pattern #6).
- No fixed-surface edits (Strategist anti-pattern #7).
- No expected-effect numbers re-derived from ground-truth (Strategist anti-pattern #8).

## CEO sign-off (both phases)

- **CEO verdict on Builder** (`.factory/reviews/ceo-verdict-builder.md`, 2026-06-02): **PROCEED**.
- **CEO verdict on Reviewer** (`.factory/reviews/ceo-verdict-reviewer.md`, 2026-06-02): **PROCEED** (ratify Reviewer PASS).
- Diff is minimum-additive (+9/-7, 1 file); inner classes and the cycle-005 H2 schedule are byte-preserved; smoke completes on both datasets; scope guard clean; [[dirty-tree-staging]] memory honored.
- Ready for **R4** (post-change eval, 200-epoch fresh smoke) and **Evaluator handoff**.

## Pending (R4 / R5)

- 200-epoch run via `bash scripts/cycle_eval.sh` on `experiment/9-fno_coregionalization-constructor-fix`. Cache MISS expected on `models/fno_coregionalization/` cell only; other 13 cells should cache-hit.
- **R4 kill-switch**: if fresh smoke run does not reproduce heat ≤ 0.01551 within +25% (i.e. `heat ≤ 0.0194`) at the cycle-005 H2 schedule, revert immediately.
- **R5 verdict logic**: monotonic check uses **0.039578** as honest baseline (Strategist R2 contract; NOT the unreproducible aspirational 0.029357).
- **Expected impact at R4**: composite `0.039578 → ≈ 0.0304` (delta ≈ −0.0092); `ifc_heat` via fno_coregionalization `error/NaN → ≈ 0.01551`; stacks with H2 (deferred to a separate branch) to a projected `≈ 0.0294`.

## Links

- Project dashboard: [[factory_mffp]]
- Cycle-007 strategy: [[cycle-007]] (R2 strategy snapshot), `.factory/strategy/current.md`, `.factory/strategy/research.md` (R1.5)
- CEO Builder verdict: `.factory/reviews/ceo-verdict-builder.md`
- CEO Reviewer verdict: `.factory/reviews/ceo-verdict-reviewer.md`
- Builder report: `.factory/reviews/builder-latest.md`
- Reviewer report: `.factory/reviews/reviewer-latest.md`
- Failure analysis (R1) — root cause of COMMITTED_TREE_BROKEN: [[failure-analysis-cycle-007]]
- Cycle-006 H1 (the contamination instance this cycle did NOT repeat):
  [[cycle-006-exp-8]], [[cycle-006-summary]]
- Cycle-005 H2 (the project-best whose baseline this fix restores):
  [[factory_mffp-007]]
- Related patterns:
  [[patterns]] §"Builder clean-isolation requires pre-clean working tree",
  [[patterns]] §"Silent regression masked by the cache layer"
- Auto-memory honored: [[dirty-tree-staging]]
- Commit: `1249f2de87bfd15001c67a22ee4ea66343fecd2d` on branch `experiment/9-fno_coregionalization-constructor-fix`
- Base: `experiment/7-fno_coreg_lf_hf_transfer @ be36cba`
- Diff: `git diff be36cba..1249f2d models/fno_coregionalization/model.py` (+9 / -7, 1 file)
