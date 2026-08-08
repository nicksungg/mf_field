# MFFP Autoresearch Round 3 — Dashboard (updated 2026-08-08T07:17:00Z)

## Status: BATCH 1 FIRST JOB RUNNING — r3s3 seed 0 live on GPU, three streams still PENDING

Since the last maintainer snapshot (2026-08-08T01:16:48Z), one delta landed: the batch's first job started executing.

1. **r3s3_lf_value-B1 seed 0 (job `66825323`) transitioned PENDING → RUNNING.**
   Started 2026-08-07T23:58:47 PDT (~2026-08-08T06:58:47Z), node `hpc-sm-02-17`, elapsed ~17-19 min as of this snapshot.
   `.err` log is clean (empty — no errors).
   `.out` log shows steady per-leg progress: 8 `A0_nolf` arm legs completed with `.done` markers under `eval/done/` (allen_cahn_2d d0/d1/d2, fisher_kpp_2d d0/d1/d2, cahn_hilliard d0/d1), currently on leg 9 (`cahn_hilliard d2`).
   Preflight artifacts for the run landed as expected: `condition_identifiable_rank_ch_s0.json`, `target_scale_spread_s0.json`, `affine_ladder_voi_ch_s0.json`, `done_s0.marker` under `preflight/`.
   Card `status` unchanged (`submitted_seed0`), stage unchanged (`slurm-seed0`) — no card-level transition expected until the job completes and the initial-analyzer picks it up.

The other four legs remain **PENDING**: r3s4 `66826610`, r3s1 `66829977` + guard `66829978`, r3s2 `66832670` — all reconfirmed live via `squeue`+`sacct` this cycle, unchanged state/reason (`Priority`).

No card fields changed this cycle (job-state transitions are SLURM-side, not card-side, until seed-0 completion). `git status --short experiment_cards/` is clean — this maintainer made zero writes to any card.

All three launch gates remain **GREEN** on the 5-dataset scored panel (`state/gates.md`, unchanged since 2026-08-07T12:17Z certification): **G1-r3 GREEN**, **G2-r3 GREEN**, **G3-r3 GREEN**. ADR r3-0005 (pfc spectral-rung repair) remains **PROPOSED**, unchanged, still awaiting operator + mentor sign-off. No new ADR this cycle, no new HOLD entries.

**Program:** `program.md` · **Config:** `project.yaml` · **ADRs:** `docs/adr/` (0001 launch panel + A1, 0002 pfc crystalline box, 0003 estimator-integrity repairs, 0004 pfc report-only, 0005 pfc spectral-rung repair — PROPOSED) · **Card schema:** `experiment_cards/SCHEMA.md` · **Runbook:** `HOW_TO_LAUNCH.md`

## Streams
| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r3s1_factorised (gap) | 5-ds best-floor geomean 34.4198 | 1 | r3s1_factorised-B1 | reviewed PASS (attempt 2) → submitted_seed0; stage=slurm-seed0 | seed 0: `66829977`; guard leg: `66829978` (both `r3-r3s1_factorised-B1[-guard]-s0`, `gpu`, `nvidia_h200=1`), PENDING (Priority) — unchanged this cycle | attempt-2 PASS (2026-08-08T00:45:40Z); submitted 2026-08-07T19:05 PDT |
| r3s2_field_reach (gap) | 5-ds best-floor geomean 34.4198 | 1 | r3s2_field_reach-B1 | reviewed PASS (attempt 2) → submitted_seed0; stage=slurm-seed0 | seed 0: job `66832670` (`r3-r3s2_field_reach-B1-s0`, `gpu`, `nvidia_h200=1`), PENDING (Priority) — unchanged this cycle | attempt-2 PASS (2026-08-08T01:14:11Z); submitted 2026-08-07T20:20 PDT |
| r3s3_lf_value (lever) | 5-ds best-floor geomean 34.4198 | 1 | r3s3_lf_value-B1 | reviewed SUGGEST → submitted_seed0; stage=slurm-seed0 | seed 0: job `66825323` (`r3-r3s3_lf_value-B1-s0`, `gpu`, `nvidia_h200=1`), **RUNNING** on `hpc-sm-02-17` since 2026-08-07T23:58:47 PDT, ~17-19 min elapsed, 8/N legs done — new this cycle | job corrected 2026-08-07T17:13Z (wrapper mis-schedule fix); **RUNNING as of this cycle** |
| r3s4_audit (diag) | 5-ds best-floor geomean 34.4198 | 1 | r3s4_audit-B1 | reviewed SUGGEST (attempt 2), FAIL discharged → submitted_seed0; stage=slurm-seed0 | seed 0: job `66826610` (`r3-r3s4_audit-B1-s0`, `gpu`, `nvidia_h200=1`), PENDING (Priority) — unchanged this cycle | attempt-2 review SUGGEST (2026-08-08T00:20:38Z); submitted 2026-08-07T18:15 PDT; no change since |

Per-dataset best-floor skills (5-ds scored panel): allen_cahn_2d 475.8568 (nn_condition), fisher_kpp_2d 390.7015 (train_mean), cahn_hilliard 23.1803 (nn_condition), ifc_poisson 8.0409 (nn_condition), ifc_heat 1.3941 (nn_condition). pfc 48.0773 (train_mean) is **report-only**, excluded from the geomean per ADR r3-0004 (pending possible reinstatement under ADR r3-0005 — still PROPOSED, no sign-off).
Source: `state/anchors/launch_anchors.json` (re-aggregated 2026-08-07 ~19:17Z; unchanged this cycle).

## Running / pending jobs
| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| 66825323 | r3s3_lf_value-B1 (seed 0) | **RUNNING** | ~00:17-19 | `hpc-sm-02-17`, partition `gpu`, `cpu=4/mem=32G/gres:nvidia_h200=1` — `r3-r3s3_lf_value-B1-s0`; 8 legs done, on leg 9 (`cahn_hilliard d2`), `.err` clean |
| 66826610 | r3s4_audit-B1 (seed 0) | PENDING | 00:00:00 | `(Priority)`, partition `gpu`, `cpu=4/mem=32G/gres:nvidia_h200=1` — `r3-r3s4_audit-B1-s0` |
| 66829977 | r3s1_factorised-B1 (seed 0) | PENDING | 00:00:00 | `(Priority)`, partition `gpu`, `cpu=4/mem=32G/gres:nvidia_h200=1` — `r3-r3s1_factorised-B1-s0` |
| 66829978 | r3s1_factorised-B1 (guard leg, seed 0) | PENDING | 00:00:00 | `(Priority)`, partition `gpu`, `cpu=4/mem=32G/gres:nvidia_h200=1` — `r3-r3s1_factorised-B1-guard-s0` |
| 66832670 | r3s2_field_reach-B1 (seed 0) | PENDING | 00:00:00 | `(Priority)`, partition `gpu`, `cpu=4/mem=32G/gres:nvidia_h200=1` — `r3-r3s2_field_reach-B1-s0` |

## Completed cards
| Card | Type | Panel geomean skill (±CI) | Falsification verdict | Tools promoted |
|---|---|---|---|---|
| — | — | — | — | none — batch 1 has not been scored (evaluated/analyzed) for any stream yet |

## Flags

- **r3s3_lf_value-B1 seed 0 is RUNNING — first live execution of round 3.** Job `66825323` started ~2026-08-08T06:58:47Z, no errors, 8 legs completed and landing per-leg eval JSONs + checkpoints as expected. Not yet COMPLETED, so no timing-ledger entry or initial-analyzer dispatch yet — watch next cycle for completion.
- **Three streams still PENDING.** r3s1 (`66829977`+guard `66829978`), r3s2 (`66832670`), r3s4 (`66826610`) all confirmed live via `squeue`+`sacct` this cycle (liveness lesson applied), reason `(Priority)`, unchanged since last cycle.
- **float64→float32 loader-precision seam** — previously found by r3s3/r3s4 builders on `affine_on_hf_train` floor reproduction (~2.5–2.8e-9 stripped-view vs native-dtype, ifc_heat/ifc_poisson). Adjudicated as a documented metrology property (strict 1e-9 `seam_check_floors` correctly retained, reproduces at ≤2.744e-10; looser `ANCHOR_AFFINE_TOL=1e-7` sits ~36× above it). No anchor/floor value changed. Unchanged this cycle.
- **Eval-tree hygiene — resolved for all 4 streams, convention now codified.** r3s1 fixed commit `6770381`; r3s2 fixed commit `d5069a7`; r3s3/r3s4 redirected correctly from the start. The `ROUND2_EVAL_RESULTS`/`ROUND2_EVAL_CACHE` pattern is documented in `subagents/experiment-builder.md:218`. No open items.
- **ADR r3-0005 (pfc spectral-rung repair) — still PROPOSED, blocking on operator + mentor sign-off.** Do not execute without both sign-offs (it amends the frozen round-2 eval convention). Unchanged this cycle.
- **Gates** (`state/gates.md`): G1-r3 **GREEN** (2026-08-05, data), G2-r3 **GREEN** (2026-08-07, 5-ds preflight), G3-r3 **GREEN** (2026-08-07, 5-ds anchor re-aggregation, best-floor 34.4198) — all unchanged this cycle.
- **Reopen candidates**: none (`reopen_candidate: false` on all 4 batch-1 cards).
- **blocked.md**: none found under any stream directory.
- **Abandoned streams**: none. All 4 streams are on batch 1, all at slurm-seed0 (dispatched, one running) — the 3-consecutive-skipped/blocked cap does not apply this early. No `state/streams/{stream}.json` markers exist.
- **Transcripts inbox**: empty — nothing to archive this run.
- **Timing ledger**: still no COMPLETED `r3-*` jobs to upsert (`state/timing_ledger.json` unchanged, entries: []) — the one RUNNING job (r3s3 `66825323`) has not finished; the 4 PENDING jobs have not started.
- **Watch for next cycle**: r3s3 seed-0 completion (should seed the first timing-ledger entry and trigger initial-analyzer dispatch per `orchestrator_flow.md`); the 4 PENDING jobs should start running as GPU priority clears.

Maintained by the maintainer cron.
