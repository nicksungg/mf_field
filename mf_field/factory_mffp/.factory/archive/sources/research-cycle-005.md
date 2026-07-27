---
tags:
  - factory
  - source
  - cycle-005
source: factory-archivist
date: 2026-06-02
---

# Research — cycle-005 (CEO-synthesized)

**Context:** Cycle-005 R0 baseline composite_nRMSE = **0.033726** (project-best,
24% better than cycle-004 0.04415). Bar to beat: `mf_fno_transfer_bar`
≈ 0.0274 composite (from `results/bench_metrics.csv` — the bar's own smoke
harness crashed, see H1 below). Dominant gap: **ifc_heat** (winner 0.0205
vs bar 0.0128, 1.6×). ifc_poisson (0.0556) already ≈ bar (0.0587).

## (a) H2 — Transfer-learning recipe for `fno_coregionalization`

Two-stage LF→HF training, mirroring `mf_fno_transfer_bar`:

- **Stage 1 (LF warm-up):** filter dataset to `m != hf_m` (LF fids only),
  train for `pretrain_frac * args.epochs` (default 25% = 50/200 epochs)
  at `lr=1e-3`. Coregionalization basis stays trainable — it needs LF
  supervision so the K=10 basis weights specialize.
- **Stage 2 (joint fine-tune):** full DataLoader (all fids), remaining
  150 epochs at `lr=3e-4` (3.3× lower, matches bar).
- **Fresh `AdamW` + fresh `CosineAnnealingLR(T_max=stage_epochs)` per
  stage.** Do NOT carry opt/sched state across boundary — bar's design
  is deliberate; stale momentum is a known fine-tune divergence mode.
- **Resume schema:** extend `last.pt` with `stage ∈ {1, 2}`; resume guard
  requires `stage == 2 AND epoch == epochs_target`.
- **Scalers:** computed once from full train subset (includes LF + HF) and
  baked via `model.set_scalers(...)` before Stage 1. No per-stage rescaling.
- **Target:** ifc_heat 0.0205 → ≤ 0.013, composite 0.0337 → ≤ 0.026
  (directly beats bar).
- **Files to touch:** `models/fno_coregionalization/smoke_eval.py` only
  (`SMOKE_DEFAULTS` + `main()` train loop). `model.py`, `data.py`,
  `manifest.json`, `full_config.json` unchanged.

## (b) H1 — 1-line REPO_ROOT fix for `mf_fno_transfer_bar`

`models/mf_fno_transfer_bar/smoke_eval.py:32` currently sets
`REPO_ROOT = HERE.parent.parent.parent` which resolves to `mf_field/`
(no `data_adapters/`), producing `ModuleNotFoundError: No module named
'data_adapters'` in both local-pass and SLURM (job 15313689).
**Fix:** `HERE.parent.parent`. Unblocks in-distribution bar comparison
on the smoke leaderboard. Prerequisite to H2's bar-beating claim.

## (c) Systemic wrapper-timeout issue (NOT in mutable scope — operator)

Both `researcher` (1800s + 1500s) and `failure_analyst` (1800s + 1200s)
wrappers timed out cycle-005 with no output, exit code 1. CEO synthesized
substitutes in both cases. Same root cause is suspected: auto-injected
playbooks under `.factory/playbooks/<role>.md` (fixed surface) likely
encourage excessive exploration before any file write. **Operator action
needed** — out of scope for any cycle hypothesis. Tracking flag for
future archivist invocations: if a third role hangs identically, escalate.

## Deferred (carry-forward Researcher TODOs)

`backlog.md` lines 3–5 unactioned: (1) li2022ifc per-fid nRMSE → paper
baselines JSON (operator-only, `baselines/` is fixed); (2) FIRE row in
`papers_summary.csv` (fixed); (3) 2024–2026 MF field-prediction WebSearch
(researcher never fired). All deferred to a future cycle when the
researcher wrapper is functional.

## Related
- [[li2022ifc]] — coregionalization basis used as the H2 head
- [[research-cycle-003]] — prior transfer-learning notes
