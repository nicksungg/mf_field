---
name: cycle-008-exp-11-build
description: Cycle-008 H1 (exp 11) — Builder + CEO PROCEED phase. Paper-config capacity bump on `fno_coregionalization` at `models/fno_coregionalization/smoke_eval.py SMOKE_DEFAULTS`. Single-file +10/-4 LOC commit 18d83a6 on `experiment/11-fno_coregionalization-paper-capacity` cut from cycle-007 H1 baseline `experiment/9-fno_coregionalization-constructor-fix @ 1249f2d` (the cycle-008 entry-baseline branch with the repaired anisotropic-modes constructor). Five SMOKE_DEFAULTS knobs touched, all matching `models/fno_coregionalization/full_config.json` (li2022ifc paper): `hidden_channels 32→128`, `K 10→20`, `n_blocks 4→6`, `modes_cap 12→16`, plus NEW `b_hidden=128` key. Required minimal plumbing: `b_hidden=p["b_hidden"]` kwarg added to the `FNOCoregionalization(...)` call site so the new SMOKE_DEFAULTS key actually reaches the constructor (without it the key would be dead). `model.py` byte-identical to `1249f2d` per cycle-007 H1 lesson and cycle-008 anti-pattern #6. H2 LF→HF schedule fields (`pretrain_lr`, `finetune_lr`, `pretrain_frac`) preserved verbatim. Smoke verification: 2-epoch end-to-end PASS on `data/ifc_heat` (`train_seconds=4.31` → ~2.15 s/epoch → 200-epoch projection ≈ 14-15 min total under 25-min kill-switch cap), `params=50,471,592` (50.47M, plausible for K=20/hidden=128/n_blocks=6/b_hidden=128), `peak_mem=1.73 GB`. Kept `epochs=200`, no warmup change needed. Leakage scan `flagged: false, risk_level: none`. Surface guard `factory guard --baseline 1249f2d --check-scope` clean. CEO PROCEED ready for R4 (200-epoch fresh smoke). `--no-github` honored — no push, no PR, no issue.
metadata:
  type: experiment
tags:
  - factory
  - experiment
  - factory_mffp
  - cycle-008
  - build
  - h1
  - fno_coregionalization
  - capacity-bump
  - paper-config
  - li2022ifc
project: factory_mffp
experiment_id: "011"
cycle: cycle-008
hypothesis_id: H1
phase: build
verdict: PROCEED
ceo_verdict_builder: PROCEED
date: 2026-06-02
branch: experiment/11-fno_coregionalization-paper-capacity
parent_branch: experiment/9-fno_coregionalization-constructor-fix
parent_commit: 1249f2d
commit: 18d83a6
files_changed: 1
loc_delta: "+10/-4"
target_file: models/fno_coregionalization/smoke_eval.py
model_py_edited: false
manifest_py_edited: false
inspiration_md_edited: false
full_config_json_edited: false
knob_hidden_channels_before: 32
knob_hidden_channels_after: 128
knob_K_before: 10
knob_K_after: 20
knob_n_blocks_before: 4
knob_n_blocks_after: 6
knob_modes_cap_before: 12
knob_modes_cap_after: 16
knob_b_hidden_before: 64
knob_b_hidden_after: 128
knob_b_hidden_new_key: true
b_hidden_plumbed_to_constructor: true
h2_lf_hf_schedule_preserved_verbatim: true
smoke_2ep_dataset: ifc_heat
smoke_2ep_train_seconds: 4.31
smoke_2ep_s_per_epoch: 2.15
smoke_2ep_params: 50471592
smoke_2ep_peak_mem_gb: 1.73
smoke_200ep_projection_min_total: "14-15"
smoke_kill_switch_cap_min: 25
smoke_warmup_change_needed: false
smoke_epochs_kept: 200
leakage_check_diff_risk_level: none
leakage_check_hypothesis_risk_level: none
surface_guard_baseline: 1249f2d
surface_guard_result: clean
no_github_mode: true
no_pr_created: true
no_push: true
no_issue_created: true
source: factory-archivist
---

# Experiment #011 — Build phase: Cycle-008 H1 `fno_coregionalization` paper-config capacity bump

## Hypothesis

**Cycle-008 H1 — EXPLOIT, HIGH priority, LOW risk, single-file, `CAPACITY_PARETO` failure mode.** Wire the IFC paper `full_config.json` capacity values into `SMOKE_DEFAULTS` of `models/fno_coregionalization/smoke_eval.py` so the cycle-007 H1 repaired anisotropic-modes constructor finally runs at paper capacity instead of the prior under-capacity smoke defaults. No `model.py` edit — anti-pattern #6 forbids it; the cycle-007 H1 constructor already accepts all paper kwargs.

Expected impact (per cycle-008 Strategist):
- `fno_coregionalization` × `ifc_heat`: 0.01551 → ~0.013 (high end ~0.012, low end ~0.014).
- `fno_coregionalization` × `ifc_poisson`: 0.7501 → 0.5-0.7 (composite-neutral; not the lever).
- Composite: 0.030408 → ~0.028 (high end ~0.026; low end ~0.029).
- Kill-switch: `ifc_heat` nRMSE > 0.0194 → REVERT. If smoke wall > 25 min on first SLURM run, drop epochs 200 → 120 with cosine warmup.

## Branch + commit

- **Branch**: `experiment/11-fno_coregionalization-paper-capacity`.
- **Base**: `experiment/9-fno_coregionalization-constructor-fix @ 1249f2d` (cycle-007 H1; new reproducible project best @ composite 0.030408; cycle-008 R0 baseline). The cycle-008 R2 builder-branch-base directive (`cycle_008_r2_builder_branch_base`).
- **Single new commit**: `18d83a6` — `feat(fno_coregionalization): paper-config capacity bump (cycle-008 H1)`.
- **Chain**: `be36cba` (c005 H2 schedule) ← `1249f2d` (c007 H1 constructor fix) ← `18d83a6` (this H1).
- **GitHub**: no PR, no push (`--no-github` honored — no `gh` / `git push` calls).

## What the Builder produced

`git diff --stat 1249f2d 18d83a6`:

| File | Lines | Purpose |
|---|---:|---|
| `models/fno_coregionalization/smoke_eval.py` | **+10 / −4** | Five SMOKE_DEFAULTS knobs bumped to paper (`hidden_channels`, `K`, `n_blocks`, `modes_cap`) + NEW `b_hidden=128` key + one-line plumbing `b_hidden=p["b_hidden"]` at the `FNOCoregionalization(...)` call site so the new key actually reaches the constructor; explanatory in-block comment naming the cycle and citing `full_config.json` (li2022ifc) as the source |
| **Total** | **+10 / −4, 1 file** | All under `models/fno_coregionalization/**` |

**Byte-preserved files** (per cycle-008 anti-pattern #6 and Strategist R2 mutable-surface clause):
- `models/fno_coregionalization/model.py` — UNTOUCHED. Cycle-007 H1's repaired `FNOCoregionalization.__init__` already accepts `K`, `hidden_channels`, `n_blocks`, `modes_h`/`modes_w`, `grid`, and `b_hidden` kwargs; no constructor-signature work needed for the paper-config bump.
- `models/fno_coregionalization/manifest.json` — UNTOUCHED.
- `models/fno_coregionalization/INSPIRATION.md` — UNTOUCHED (citations already present from cycle-005 H2 / cycle-007 H1).
- `models/fno_coregionalization/full_config.json` — UNTOUCHED (it is the source-of-truth being mirrored into SMOKE_DEFAULTS).

**H2 LF→HF schedule preserved verbatim** (banked from cycle-005 H2 / cycle-007 H1): `pretrain_lr`, `finetune_lr`, `pretrain_frac` SMOKE_DEFAULTS keys are byte-identical to `1249f2d`. The two-stage outer loop in `run()` is untouched. The capacity bump composes on top of the already-banked schedule.

## Mechanism (verbatim against Strategist H1 spec)

The Builder shipped a single discrete change to `SMOKE_DEFAULTS` — replace the four under-capacity values with the paper config, plus add the new `b_hidden` key:

```python
SMOKE_DEFAULTS = dict(
    ...
    batch_size=8,
    lr=3e-4,
    weight_decay=1e-5,
    # H1 (cycle-008): paper-config capacity bump on the repaired constructor.
    # hidden_channels 32→128, K 10→20, n_blocks 4→6, modes_cap 12→16, plus
    # b_hidden=128 wired in (was constructor default 64). Values mirror
    # models/fno_coregionalization/full_config.json (li2022ifc paper config).
    hidden_channels=128,   # was 32
    K=20,                  # was 10
    n_blocks=6,            # was 4
    modes_cap=16,          # was 12
    b_hidden=128,          # NEW key — was constructor default 64
    val_frac=0.1,
    ...
)
```

And the corresponding minimal plumbing at the constructor call site in `run(args)`:

```python
model = FNOCoregionalization(
    ...
    modes_h=modes_h,
    modes_w=modes_w,
    grid=grid,
    b_hidden=p["b_hidden"],   # <- new kwarg so SMOKE_DEFAULTS["b_hidden"] actually reaches the constructor
).to(device)
```

The plumbing is **strictly necessary** — without it, `SMOKE_DEFAULTS["b_hidden"]` would be a dead key and the experiment's b_hidden=128 claim would silently fall back to the constructor default 64. Builder flagged this design choice in the report; CEO ratified as inside-the-hypothesis scope ("the file already declared as mutable; same line discipline as cycle-007 H1's `K`/`hidden`/`n_blocks` kwargs").

## Pre-flight verification — PASSED

Builder ran the mandatory smoke check per CEO/Strategist contract:

```bash
factory <cmd> smoke_eval.py --epochs 2 --dataset_dir data/ifc_heat \
    --out /tmp/h1_smoke_check.json --ckpt_dir /tmp/h1_ckpt_check --seed 0
```

| Metric | Value | Interpretation |
|---|---:|---|
| `train_seconds` | **4.31** | 2.15 s/epoch on H100 |
| `params` | **50,471,592** | 50.47M params (sanity-consistent with K=20, hidden=128, n_blocks=6, b_hidden=128) |
| `peak_mem` | **1.73 GB** | Comfortably within H100 capacity |
| **200-epoch projection** | **~7 min/cell × 2 cells ≈ 14-15 min total** | Under the 25-min kill-switch cap by ≈40% margin |
| exit | 0 | end-to-end successful |

**Decision: kept `epochs=200` (no warmup change needed).** The 25-min wall-budget kill-switch (Strategist R2: "If smoke wall > 25 min on first SLURM run, drop epochs 200 → 120 with cosine warmup") was not triggered. The 14-15 min projection leaves ~40% headroom even if the second cell (Poisson) trains slightly slower than Heat.

**2-epoch values are diagnostic only** — best_val_nRMSE numbers are not the R4 leaderboard signal. What the 2-epoch smoke proves is exactly what the Builder needed to prove:

1. The paper-config constructor instantiation runs end-to-end (no `TypeError`, no shape mismatch, no OOM).
2. `b_hidden=p["b_hidden"]` plumbing reaches the constructor (otherwise the param count would be smaller — 50.47M is consistent with `b_hidden=128`, not 64).
3. The H2 LF→HF schedule still runs (the 2-epoch run with `pretrain_frac=0.25` gives `n_warmup=0` and skips Stage 1, but Stage 2 alone completes both epochs — same diagnostic mode as cycle-005 H2's `--epochs 2`).
4. Wall-time projection comfortably under the kill-switch cap.

The full 200-epoch numbers will land at R4 via `bash scripts/cycle_eval.sh` on `experiment/11-fno_coregionalization-paper-capacity` (cache MISS expected on both `fno_coregionalization` cells due to `__code_hash__` change from the smoke_eval.py edit).

## Hard-gate results (CEO PROCEED)

- **Surface guard**: `factory guard --baseline 1249f2d --check-scope` → `clean`. 1 file changed (`models/fno_coregionalization/smoke_eval.py`), no fixed-surface modifications.
- **Single-file constraint** (cycle-008 Strategist H1 anti-pattern + R2 mutable-surface clause: `models/fno_coregionalization/smoke_eval.py SMOKE_DEFAULTS only`): satisfied. Only the smoke_eval.py file is modified; only the SMOKE_DEFAULTS block + one constructor-call kwarg line.
- **No `model.py` edit** (cycle-008 anti-pattern #6 — explicit Strategist restriction): satisfied. `models/fno_coregionalization/model.py` byte-identical to `1249f2d`.
- **Diff matches hypothesis exactly** (CEO line-by-line verification in `.factory/reviews/ceo-verdict-builder.md`):
  - `hidden_channels` 32→128 ✓
  - `K` 10→20 ✓
  - `n_blocks` 4→6 ✓
  - `modes_cap` 12→16 ✓
  - NEW `b_hidden=128` ✓
  - Plumbed `b_hidden=p["b_hidden"]` to `FNOCoregionalization(...)` call ✓
  - H2 schedule fields (`pretrain_lr`, `finetune_lr`, `pretrain_frac`) preserved verbatim ✓
  - `model.py` untouched ✓
- **Ground-truth leakage scan** (CEO ran `factory leakage-check --text-file <diff>`): `flagged: false, risk_level: none`. **First cycle-008 hypothesis with clean leakage scan on the actual diff** (Strategist R2 had already pre-registered `flagged: false, risk_level: none` on H1 at hypothesis level; the diff also clears).
- **`--no-github` mode**: satisfied. No `gh` calls, no `git push`, no PR, no issue.
- **Smoke verification end-to-end PASS**: confirmed (4.31s wall, 50.47M params, 1.73 GB peak, projection within cap).

## Surface modifications outside hypothesis-declared scope

**Acknowledged: one** — the `b_hidden=p["b_hidden"]` kwarg added at the `FNOCoregionalization(...)` call site is technically a second line touched, beyond the `SMOKE_DEFAULTS` block declared by the Strategist as the mutable surface. CEO approved:

- It is **necessary plumbing** — without it, `SMOKE_DEFAULTS["b_hidden"]=128` would be a dead key and the experiment would silently run with the constructor's default `b_hidden=64`, invalidating the hypothesis.
- It is in the **same file** already declared mutable for this hypothesis.
- It is **one line**.
- The same line-discipline precedent was set at cycle-007 H1 (`models/fno_coregionalization/model.py:83-128` constructor repair plumbed `K`, `hidden`, `n_blocks` kwargs through the same pattern). Cycle-008 H1 mirrors that pattern at the call site instead of the constructor.

## Implementation notes (carry into R4 interpretation)

- **Cache behavior**: the source bytes of `models/fno_coregionalization/smoke_eval.py` changed, so the `__code_hash__` for the `fno_coregionalization` cell changes. Expect cache MISS on BOTH `fno_coregionalization × ifc_heat` AND `fno_coregionalization × ifc_poisson` at R4. The other 12 cells (other 7 families × 2 datasets, minus the two `fno_coregionalization` cells) should cache-hit because their source bytes are unchanged from `1249f2d`.
- **Wall budget on R4 SLURM**: smoke wall projection 14-15 min total fits comfortably inside the 30-min H100 SLURM-side budget per Strategist R2; both cells (Heat + Poisson) within the same `scripts/cycle_eval.sh` invocation.
- **Heat target**: at R4 expect `fno_coregionalization × ifc_heat` ≈ 0.013 (high end ~0.012, low end ~0.014; Strategist R2 projection). Kill-switch trip if heat > 0.0194 (the +25% over the 0.01551 reproducible baseline that anchors the cycle-008 entry composite). Hard target for cycle-008 H1 KEEP: heat ≤ 0.013, composite ≤ 0.028.
- **Poisson note**: the 0.7501 → 0.5-0.7 projection is composite-neutral (Poisson winner is still `fno_mf_stack @ 0.05961`). H1 is not the Poisson lever; H2/H3 attack Poisson directly.
- **Composite target**: 0.030408 → ~0.028 (high end ~0.026; low end ~0.029). Crossing the bar `mf_fno_transfer_bar @ 0.02743` is the high end of the projection band; even a low-end landing at ~0.029 still moves the reproducible project best forward.

## Anti-patterns explicitly NOT triggered (all six cycle-008 anti-patterns)

1. **MFRNP loss-recipe / reweighting** (BANNED; 3/3 REVERTs): satisfied — H1 is capacity-only, no `hf_loss_weight` / `lf_loss_weights` edits. Anti-pattern #1.
2. **Per-dataset MFRNP recipe dispatch** (BANNED; cycle-007 H2 REVERT): satisfied — no `_DATASET_RECIPES` dict, no `resolve_fidelity_weights` helper added. Anti-pattern #2.
3. **A1+B1+B3 bundling** (FORBIDDEN; cycle-008 H1/H2/H3 must be independent branches): satisfied — H1 is on its own branch (`experiment/11-…`), single-file, single-family, zero file overlap with H2/H3's planned mutable surfaces.
4. **D1 (`mf_fno_transfer_bar` smoke-config bump)** (DEFERRED to cycle-009+): satisfied — no edits to `models/mf_fno_transfer_bar/**`.
5. **A3 (F-FNO factorized spectral conv refactor)** (DEFERRED to cycle-009+ as `fno_coreg_ffno`): satisfied — no architectural refactor.
6. **`models/fno_coregionalization/model.py` edits for H1** (FORBIDDEN per Strategist R2 explicit clause): satisfied — `model.py` byte-identical to `1249f2d`.

## CEO sign-off

- **CEO verdict on Builder** (`.factory/reviews/ceo-verdict-builder.md`, 2026-06-02): **PROCEED**. Diff matches hypothesis exactly; surface clean; leakage clean; smoke verification PASS with wall projection under cap.
- Diff is minimum-additive (+10/-4, 1 file); `model.py` / `manifest.json` / `INSPIRATION.md` / `full_config.json` byte-preserved; H2 LF→HF schedule preserved verbatim from cycle-007 H1; cycle-008 anti-pattern #6 satisfied; sibling families (`fno_mf_stack`, `fno_coreg_residual`, `mf_fno_transfer_bar`, transolver*) untouched.
- Ready for **R4** (post-change eval, 200-epoch fresh smoke on `experiment/11-fno_coregionalization-paper-capacity` via `bash scripts/cycle_eval.sh`).

## Pending (R3-review / R4 / R5)

- **R3 Reviewer**: instructions issued in CEO verdict — run `factory guard . --baseline 1249f2d --check-scope`, verify smoke result plausibility (50.47M params consistent with K=20/hidden=128/n_blocks=6/b_hidden=128 — in the right order of magnitude), read the +10/-4 1-file diff, print PASS or FAIL.
- **R4 200-epoch run** via `bash scripts/cycle_eval.sh` on `experiment/11-fno_coregionalization-paper-capacity`. Cache MISS expected on **both** `fno_coregionalization` cells (heat + poisson) due to `__code_hash__` change; other 12 cells cache-hit.
- **R4 kill-switches**:
  - `ifc_heat` nRMSE > 0.0194 → REVERT (the 0.01551 baseline +25% band).
  - Wall > 25 min on first SLURM run → drop epochs 200 → 120 with cosine warmup (not expected to trigger; projection is 14-15 min).
- **R5 verdict logic**:
  - Monotonic check uses **0.030408** as the cycle-008 entry baseline (cycle-007 H1's R4 result; current reproducible project best).
  - Hard targets: `ifc_heat` ≤ 0.013 AND composite ≤ 0.028 → strong KEEP.
  - Low-end band: composite ~0.029 (within ~5% of entry baseline) → still meaningful KEEP for the smoke leaderboard if heat actually moves below 0.01551.
  - The `score_direction` polarity precheck bug will likely flip a real composite improvement back to a "+%" regression at R5 (now an 8-of-8 streak); CEO should pre-register the override.

## Cross-cycle pattern notes

- **First hypothesis in project history to land a clean `flagged: false, risk_level: none` leakage scan both at hypothesis declaration (Strategist R2) AND on the actual diff (CEO at R3-builder).** Cycles 001-007 all tripped on substring-collision false positives (`"poisson"`, `"description"`, `"frozen"`, `"ifc_raw"`, `"modify"`, `"satisfy"`, `"loader"`, `"dataset"`, `"ifc_poisson"` dispatch-key, etc.). Cycle-008 H1's diff is small enough and avoids both factory.md / README.md shared vocabulary AND public-API dispatch keys — it is a pure SMOKE_DEFAULTS-value edit with a one-line kwarg plumb. The leakage-scan substring-collision pattern (long-running infra bug) does not fire on numerical-knob bumps that don't introduce new public-API tokens.
- **Cycle-008 anti-pattern compliance is unusually tight.** The Strategist R2 spec is essentially a structured numeric-knob list ("change these 5 SMOKE_DEFAULTS values"), and the Builder shipped exactly those 5 changes plus the one strictly-necessary plumbing line. No design-choice ambiguity, no in-between interpretations, no aggregator-anchor-scaling decision (cycle-003 H1) or `_DATASET_RECIPES` Heat-entry temptation (cycle-007 H2). This is a clean "spec → diff" mapping.
- **Builder branch hygiene improving** — third consecutive cycle (cycle-007 H1, cycle-007 H2, now cycle-008 H1) with a clean single-commit Builder output, zero pre-existing dirty-file contamination committed, despite the 15-file dirty working tree carried since cycle-005. Same structural-easy-case caveat applies (target file `smoke_eval.py` was at HEAD pre-edit). The [[dirty-tree-staging]] auto-memory rule continues to do its job for builds where the target file is not in the pre-existing dirty diff.

## Links

- Project dashboard: [[factory_mffp]]
- Cycle-008 strategy: [[cycle-008]] (canonical R2 strategy snapshot — H1 > H2 > H3 plan-approved)
- Cycle-008 failure analysis: [[failure-analysis-cycle-008]]
- CEO Builder verdict: `.factory/reviews/ceo-verdict-builder.md` (cycle-008 H1)
- Builder report: `.factory/reviews/builder-latest.md`
- Cycle-007 H1 (parent — the repaired anisotropic-modes constructor this H1 capacity-bumps): [[cycle-007-exp-9-build]], [[cycle-007-exp-9]]
- Cycle-007 H2 (sibling-family per-dataset recipe REVERT — the "do NOT add MFRNP weighting" lesson cycle-008 H1 honors): [[cycle-007-exp-10-build]], [[cycle-007-exp-10]]
- Cycle-005 H2 (parent of cycle-007 H1; the LF→HF schedule preserved verbatim in this H1): [[factory_mffp-007]]
- Related source notes (cycle-007 R1.5 inheritance):
  [[anisotropic-spectral-modes-fno]] — Li 2020 FNO `(modes_h, modes_w)` parameterization carried through `modes_cap=16`,
  [[per-dataset-recipes-mf-field]] — cycle-007 R1.5; NOT applied here (anti-patterns #1 and #2 forbid MFRNP weighting on this H1),
  [[lf-hf-pretrain-fraction-survey]] — cycle-007 R1.5 schedule study; cycle-008 H1 preserves the cycle-005 H2 `pretrain_frac=0.25` verbatim.
- Cycle-008 anti-pattern parents:
  [[patterns]] §"MFRNP recipes are backbone-coupled and dataset-entangled" (3-of-3 REVERTs lock-in),
  [[patterns]] §"Builder clean-isolation requires pre-clean working tree" (dirty-tree-staging precedent),
  [[patterns]] §"Silent regression masked by the cache layer" (RESOLVED in cycle-007 H1 — cycle-008 H1 inherits reproducible 0.030408 baseline).
- Auto-memory honored: [[dirty-tree-staging]], [[factory-cli-invocation]] (Builder used `factory <cmd>` not `uv run python -m factory`).
- Commit: `18d83a6` on branch `experiment/11-fno_coregionalization-paper-capacity`.
- Base: `experiment/9-fno_coregionalization-constructor-fix @ 1249f2d`.
- Diff: `git diff 1249f2d..18d83a6 models/fno_coregionalization/smoke_eval.py` (+10 / -4, 1 file).
