# MFFP Autoresearch Round 3 — Dashboard (updated 2026-08-08T01:16:48Z)

## Status: BATCH 1 FULLY DISPATCHED — all four streams at slurm-seed0, five jobs PENDING

Since the last maintainer snapshot (2026-08-08T00:59:10Z), one delta landed — via the orchestrator/builder/reviewer (this maintainer made zero writes to any card).

1. **r3s2_field_reach-B1: attempt-2 review PASS, seed 0 submitted.**
   `review_notes` now holds 2 entries (attempt 1 `reviewed_fail` 2026-08-08T01:04:12Z — missing `ROUND2_EVAL_RESULTS`/`ROUND2_EVAL_CACHE` exports in `scripts/01_train_eval.sh`, the same eval-tree-redirect defect class that hit r3s1/r3s3/r3s4; attempt 2 `reviewed_pass` 2026-08-08T01:14:11Z).
   Fix commit **`d5069a7`** (child of `10bfcc7`, `models_r3/` diff empty — no family code touched) adds the two exports before both `score_panel.py` calls (scored panel + guard) plus the `$OUT_DIR/cache` mkdir; re-verified at runtime bit-identical (ifc_heat nRMSE 0.229258, skill 3.0978 unchanged) with the frozen `round2/eval/` tree confirmed untouched (md5-identical directory listings before/after).
   Orchestrator submitted directly to SLURM: job **`66832670`** (`r3-r3s2_field_reach-B1-s0`), submitted 2026-08-07T20:20 PDT, confirmed live via `squeue`/`sacct` — `gpu` partition, `PENDING (Priority)`.
   Card `status` → `submitted_seed0`, stage → `slurm-seed0`.

**All four streams are now at `slurm-seed0`** — batch 1 is fully dispatched. The `ROUND2_EVAL_RESULTS`/`ROUND2_EVAL_CACHE` redirect convention (hit 3 of 4 builders across the batch: r3s1, r3s2, and flagged pre-emptively for r3s3/r3s4) is now codified in `subagents/experiment-builder.md:218` — confirmed present this cycle.

No other card fields changed. `git status --short experiment_cards/` shows only the pre-existing orchestrator/builder/reviewer-caused modification to r3s2 (attempt-2 PASS + submission) — not touched by this maintainer's read-only reads.

All three launch gates remain **GREEN** on the 5-dataset scored panel (`state/gates.md`, unchanged since 2026-08-07T12:17Z certification): **G1-r3 GREEN**, **G2-r3 GREEN**, **G3-r3 GREEN**. ADR r3-0005 (pfc spectral-rung repair) remains **PROPOSED**, unchanged, still awaiting operator + mentor sign-off. No new ADR this cycle, no new HOLD entries.

**Program:** `program.md` · **Config:** `project.yaml` · **ADRs:** `docs/adr/` (0001 launch panel + A1, 0002 pfc crystalline box, 0003 estimator-integrity repairs, 0004 pfc report-only, 0005 pfc spectral-rung repair — PROPOSED) · **Card schema:** `experiment_cards/SCHEMA.md` · **Runbook:** `HOW_TO_LAUNCH.md`

## Streams
| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r3s1_factorised (gap) | 5-ds best-floor geomean 34.4198 | 1 | r3s1_factorised-B1 | reviewed PASS (attempt 2) → submitted_seed0; stage=slurm-seed0 | seed 0: `66829977`; guard leg: `66829978` (both `r3-r3s1_factorised-B1[-guard]-s0`, `gpu`, `nvidia_h200=1`), PENDING (Priority) — unchanged this cycle | attempt-2 PASS (2026-08-08T00:45:40Z); submitted 2026-08-07T19:05 PDT |
| r3s2_field_reach (gap) | 5-ds best-floor geomean 34.4198 | 1 | r3s2_field_reach-B1 | **reviewed PASS (attempt 2) → submitted_seed0**; stage=slurm-seed0 | seed 0: job `66832670` (`r3-r3s2_field_reach-B1-s0`, `gpu`, `nvidia_h200=1`), PENDING (Priority) | attempt-2 PASS (2026-08-08T01:14:11Z); submitted 2026-08-07T20:20 PDT — new this cycle |
| r3s3_lf_value (lever) | 5-ds best-floor geomean 34.4198 | 1 | r3s3_lf_value-B1 | reviewed SUGGEST → submitted_seed0; stage=slurm-seed0 | seed 0: job `66825323` (`r3-r3s3_lf_value-B1-s0`, `gpu`, `nvidia_h200=1`), PENDING (Priority) — unchanged this cycle | job corrected 2026-08-07T17:13Z (wrapper mis-schedule fix); no change since |
| r3s4_audit (diag) | 5-ds best-floor geomean 34.4198 | 1 | r3s4_audit-B1 | reviewed SUGGEST (attempt 2), FAIL discharged → submitted_seed0; stage=slurm-seed0 | seed 0: job `66826610` (`r3-r3s4_audit-B1-s0`, `gpu`, `nvidia_h200=1`), PENDING (Priority) — unchanged this cycle | attempt-2 review SUGGEST (2026-08-08T00:20:38Z); submitted 2026-08-07T18:15 PDT; no change since |

Per-dataset best-floor skills (5-ds scored panel): allen_cahn_2d 475.8568 (nn_condition), fisher_kpp_2d 390.7015 (train_mean), cahn_hilliard 23.1803 (nn_condition), ifc_poisson 8.0409 (nn_condition), ifc_heat 1.3941 (nn_condition). pfc 48.0773 (train_mean) is **report-only**, excluded from the geomean per ADR r3-0004 (pending possible reinstatement under ADR r3-0005 — still PROPOSED, no sign-off).
Source: `state/anchors/launch_anchors.json` (re-aggregated 2026-08-07 ~19:17Z; unchanged this cycle).

## Running / pending jobs
| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| 66825323 | r3s3_lf_value-B1 (seed 0) | PENDING | 00:00:00 | `(Priority)`, partition `gpu`, `cpu=4/mem=32G/gres:nvidia_h200=1` — `r3-r3s3_lf_value-B1-s0` |
| 66826610 | r3s4_audit-B1 (seed 0) | PENDING | 00:00:00 | `(Priority)`, partition `gpu`, `cpu=4/mem=32G/gres:nvidia_h200=1` — `r3-r3s4_audit-B1-s0` |
| 66829977 | r3s1_factorised-B1 (seed 0) | PENDING | 00:00:00 | `(Priority)`, partition `gpu`, `cpu=4/mem=32G/gres:nvidia_h200=1` — `r3-r3s1_factorised-B1-s0` |
| 66829978 | r3s1_factorised-B1 (guard leg, seed 0) | PENDING | 00:00:00 | `(Priority)`, partition `gpu`, `cpu=4/mem=32G/gres:nvidia_h200=1` — `r3-r3s1_factorised-B1-guard-s0` |
| 66832670 | r3s2_field_reach-B1 (seed 0) | PENDING | 00:00:00 | `(Priority)`, partition `gpu`, `cpu=4/mem=32G/gres:nvidia_h200=1` — `r3-r3s2_field_reach-B1-s0` |

## Completed cards
| Card | Type | Panel geomean skill (±CI) | Falsification verdict | Tools promoted |
|---|---|---|---|---|
| — | — | — | — | none — batch 1 has not been scored (evaluated/analyzed) for any stream yet |

## Flags

- **BATCH 1 FULLY DISPATCHED.** All four streams (r3s1, r3s2, r3s3, r3s4) are now at `slurm-seed0`; five jobs PENDING (`66825323`, `66826610`, `66829977`, `66829978`, `66832670`), all confirmed live via `squeue`+`sacct` (liveness lesson applied).
- **r3s2_field_reach-B1 reviewed PASS on attempt 2, seed 0 submitted.** Job `66832670` PENDING; `review_fail_attempts` cap (3) not tripped (1 FAIL then 1 PASS) — same discharge pattern as r3s1's attempt 2.
- **float64→float32 loader-precision seam** — previously found by r3s3/r3s4 builders on `affine_on_hf_train` floor reproduction (~2.5–2.8e-9 stripped-view vs native-dtype, ifc_heat/ifc_poisson). Adjudicated as a documented metrology property (strict 1e-9 `seam_check_floors` correctly retained, reproduces at ≤2.744e-10; looser `ANCHOR_AFFINE_TOL=1e-7` sits ~36× above it). No anchor/floor value changed. Unchanged this cycle.
- **Eval-tree hygiene — resolved for all 4 streams, convention now codified.** r3s1 fixed commit `6770381`; r3s2 fixed commit `d5069a7` (this cycle); r3s3/r3s4 redirected correctly from the start. The `ROUND2_EVAL_RESULTS`/`ROUND2_EVAL_CACHE` pattern is now documented in `subagents/experiment-builder.md:218` for future batches. No open items.
- **ADR r3-0005 (pfc spectral-rung repair) — still PROPOSED, blocking on operator + mentor sign-off.** Do not execute without both sign-offs (it amends the frozen round-2 eval convention). Unchanged this cycle.
- **Gates** (`state/gates.md`): G1-r3 **GREEN** (2026-08-05, data), G2-r3 **GREEN** (2026-08-07, 5-ds preflight), G3-r3 **GREEN** (2026-08-07, 5-ds anchor re-aggregation, best-floor 34.4198) — all unchanged this cycle.
- **Reopen candidates**: none (`reopen_candidate: false` on all 4 batch-1 cards).
- **blocked.md**: none found under any stream directory.
- **Abandoned streams**: none. All 4 streams are on batch 1, all at slurm-seed0 (dispatched) — the 3-consecutive-skipped/blocked cap does not apply this early. No `state/streams/{stream}.json` markers exist.
- **Transcripts inbox**: empty — nothing to archive this run.
- **Timing ledger**: still no completed `r3-*` jobs to upsert (`state/timing_ledger.json` unchanged, entries: []) — all 5 live jobs are PENDING, not yet run.
- **Watch for next cycle**: all five PENDING jobs should start running; watch for first completions to seed the timing ledger and initial-analyzer dispatch (per `orchestrator_flow.md`, r3s4's certification adjudicates before other streams' claims).

Maintained by the maintainer cron.
