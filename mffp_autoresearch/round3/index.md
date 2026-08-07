# MFFP Autoresearch Round 3 — Dashboard (updated 2026-08-07T19:38:00Z)

## Status: batch 1, all 4 streams at builder stage — no SLURM jobs dispatched yet

HOLD (pfc scored-cell task-void) was cleared in the prior maintainer cycle via ADR r3-0004 (pfc report-only, scored panel = 5 datasets, best-floor geomean **34.4198**).
Since the last maintainer snapshot (19:20Z), three further deltas landed:

1. **HF release synced** (`f869636`, 19:26:18Z) — hub commit `36a5f198`; pfc row recomputed, dataset cards updated. pfc arrays ship unchanged (correct physics); only the card/DEFECT_STATUS metadata changed.
2. **ADR r3-0005 PROPOSED** (`9b07ce0`, 19:27:23Z, `docs/adr/0005-pfc-spectral-rung-repair-PROPOSED.md`) — the "proper repair" for pfc: re-point the scored cell to L1→L3 with a pfc-specific spectral reference lift, returning pfc to the scored panel (6 datasets) if ratified. **Status: PROPOSED, awaiting operator (Eloise) AND mentor sign-off** — this amends the frozen ADR r2-0001 eval convention, so it is explicitly not an orchestrator-level decision. Not executed; pfc remains report-only under ADR r3-0004 until sign-off lands. Measurements are already attached to the ADR (proposed cell: mean copy-gap 0.012358, `degenerate_rows` OK, `cell_stability` OUTLIER_DOMINATED with MDD 65.8%).
3. **r3s3_lf_value's starter completed** (`ae2001b`, 19:30:02Z): card `r3s3_lf_value-B1` created (`drafted`, `job_ids: []`), stage advanced `brainstorm → builder`. All four streams are now at the **builder** stage (`state/{stream}/current_stage.txt` = `builder` for all 4), each with an active `models_r3/<family>/` directory under active edit (file mtimes within the last ~2 minutes of this walk — builders are still writing code, not yet stalled).

**No `r3-{stream}-B{N}-s{seed}` SLURM jobs exist anywhere** — `squeue -u $USER` is empty and the 2-day `sacct` window has no `r3-` prefixed experiment jobs. All 4 batch-1 cards remain `status: drafted`, `job_ids: []`. This is expected: builders write family code before any training/eval job is submitted.

All three launch gates remain **GREEN** on the 5-dataset scored panel (`state/gates.md`, unchanged since last certification): **G1-r3 GREEN**, **G2-r3 GREEN**, **G3-r3 GREEN**.

**Program:** `program.md` · **Config:** `project.yaml` · **ADRs:** `docs/adr/` (0001 launch panel + A1, 0002 pfc crystalline box, 0003 estimator-integrity repairs, 0004 pfc report-only, 0005 pfc spectral-rung repair — PROPOSED) · **Card schema:** `experiment_cards/SCHEMA.md` (new, added with ADR r3-0005 commit) · **Runbook:** `HOW_TO_LAUNCH.md`

## Streams
| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r3s1_factorised (gap) | 5-ds best-floor geomean 34.4198 | 1 | r3s1_factorised-B1 (`experiment_cards/r3s1_factorised/batch_1/B1.json`) | drafted, not dispatched; stage=builder, family `models_r3/r3s1_twostage_crosscoef` actively building | none (job_ids: []) | card created 2026-08-07T17:52:11Z; builder file writes as recent as 19:37:21Z |
| r3s2_field_reach (gap) | 5-ds best-floor geomean 34.4198 | 1 | r3s2_field_reach-B1 (`experiment_cards/r3s2_field_reach/batch_1/B1.json`) | drafted, not dispatched; stage=builder, family `models_r3/r3s2_stack_ic` actively building | none (job_ids: []) | card created 2026-08-07T18:06:20Z; builder file writes as recent as 19:37:25Z |
| r3s3_lf_value (lever) | 5-ds best-floor geomean 34.4198 | 1 | r3s3_lf_value-B1 (`experiment_cards/r3s3_lf_value/batch_1/B1.json`) | drafted, not dispatched; stage=builder (advanced from brainstorm this cycle), family `models_r3/r3s3_lf_channels` actively building | none (job_ids: []) | card created 2026-08-07T19:21:21Z (starter dispatch, this cycle); builder file writes as recent as 19:36:21Z |
| r3s4_audit (diag) | 5-ds best-floor geomean 34.4198 | 1 | r3s4_audit-B1 (`experiment_cards/r3s4_audit/batch_1/B1.json`) | drafted, not dispatched; stage=builder, family `models_r3/r3s4_cert_min` actively building | none (job_ids: []) | card created 2026-08-07T17:55:05Z (this card's escalation triggered the now-resolved HOLD); builder file writes as recent as 19:37:17Z |

Per-dataset best-floor skills (5-ds scored panel): allen_cahn_2d 475.8568 (nn_condition), fisher_kpp_2d 390.7015 (train_mean), cahn_hilliard 23.1803 (nn_condition), ifc_poisson 8.0409 (nn_condition), ifc_heat 1.3941 (nn_condition). pfc 48.0773 (train_mean) is **report-only**, excluded from the geomean per ADR r3-0004 (pending possible reinstatement under ADR r3-0005).
Source: `state/anchors/launch_anchors.json` (re-aggregated 2026-08-07, ~19:17Z; unchanged this cycle).

## Running / pending jobs
| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| — | — | — | — | none live: `squeue -u $USER` empty; `sacct` (2-day window) has no `r3-{stream}-B*` entries — all 4 builders are mid-build at the agent/filesystem level, no SLURM submission observed yet |

## Completed cards
| Card | Type | Panel geomean skill (±CI) | Falsification verdict | Tools promoted |
|---|---|---|---|---|
| — | — | — | — | none — batch 1 has not been scored for any stream |

## Flags

- **ADR r3-0005 (pfc spectral-rung repair) — PROPOSED, blocking on operator + mentor sign-off.** Do not execute without both sign-offs (it amends the frozen round-2 eval convention). If ratified mid-round, pfc returns to the scored panel (6 datasets), anchors/floors must be re-recomputed, and all batch-1 cards' pfc thresholds re-issued (execution plan already written into the ADR).
- **Gates** (`state/gates.md`): G1-r3 **GREEN** (2026-08-05, data), G2-r3 **GREEN** (2026-08-07, 5-ds preflight), G3-r3 **GREEN** (2026-08-07, 5-ds anchor re-aggregation, best-floor 34.4198) — all unchanged this cycle.
- **HF release**: synced this cycle (hub commit `36a5f198`, commit `f869636`) — pfc row recomputed, cards updated; arrays unchanged.
- **Reopen candidates**: none (`reopen_candidate: false` on all 4 drafted cards).
- **blocked.md**: none found under any stream directory.
- **Abandoned streams**: none. All 4 streams are still on batch 1 (the 3-consecutive-skipped/blocked cap does not apply this early).
- **Transcripts inbox**: empty — nothing to archive this run.
- **Timing ledger**: still no completed `r3-*` jobs to upsert (`state/timing_ledger.json` unchanged, entries: []) — batch 1 has not reached SLURM submission for any stream yet.
- **Watch for next cycle**: all 4 builders should finish and submit SLURM training/eval jobs (`r3-{stream}-B1-s{seed}`) — expect `job_ids` and `status` to update, and the timing ledger to start populating, once that happens.

Maintained by the maintainer cron.
