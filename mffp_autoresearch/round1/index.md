# MFFP Autoresearch Round 1 — Dashboard (updated 2026-07-29T04:55:48Z)

## Gate status
| Gate | What | Status |
|---|---|---|
| G1 | eval-layer smoke + assertion drill | PASS (2026-07-28) |
| G2 | copy-LF baselines | PASS (2026-07-28) |
| G3 | batch 0: anchors + noise floor (3 seeds) | **PENDING** — array job `65956106` (r1-batch0) 14/36 COMPLETED, 3 RUNNING, 19 PENDING, 0 FAILED. First attempt `65955389` FAILED all 14 launched tasks (INFRA: bad GPU node `hpc-93-36`, now excluded) |
| G4 | dry-run card s5\_tuning-B1 | PENDING (gated on G3) |

No card in `state/anchors/*.json` exists yet — every "Anchor" cell below is
unrendered pending G3 (per program.md §4.5, anchors live in exactly one place
and are never recomputed here).

## Streams
| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| s1_poisson | not yet certified (G3 pending) | 1 | none yet | websearch_done_awaiting_G3_brainstormer | — | websearch report filed (batch_1) |
| s2_beyond_copy | not yet certified (G3 pending) | 1 | none yet | websearch_done_awaiting_G3_brainstormer | — | websearch report filed (batch_1) |
| s3_testtime | not yet certified (G3 pending) | 1 | none yet | websearch_done_awaiting_G3_brainstormer | — | websearch report filed (batch_1); ADR 0003 corrected §12.3 prior |
| s4_hybrid_routing | not yet certified (G3 pending) | 1 | none yet | websearch_done_awaiting_G3_brainstormer | — | websearch report filed (batch_1) |
| s5_tuning | not yet certified (G3 pending) | 1 | none yet | websearch_done_awaiting_G3_brainstormer | — | websearch report filed (batch_1); dry-run card (G4) still gated on G3 |

No stream has an experiment card yet — `experiment_cards/` contains only
`SCHEMA.md`. All five streams are gated on G3 (batch-0 anchor + noise-floor
certification) before any brainstormer proposes a slot.

## Running / pending jobs
| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| 65956106_12 (r1-batch0) | — (G3 array, task 12: mf_fno_transfer_film × sharp__cahn_hilliard × seed0) | RUNNING | ~26 min | hpc-26-17 |
| 65956106_13 (r1-batch0) | — (task 13: sharp__cahn_hilliard × seed1) | RUNNING | ~25 min | hpc-25-17 |
| 65956106_14 (r1-batch0) | — (task 14: sharp__cahn_hilliard × seed2) | RUNNING | ~25 min | hpc-26-21 |
| 65956106_[17-35] (r1-batch0) | — (remaining G3 array tasks: 17 = ifc_poisson seed2, 18-35 = mf_fno_pinn_transfer × all 6 datasets × 3 seeds) | PENDING | 0:00 | Priority |

No `r1-{stream}-B{N}-s{seed}` jobs exist yet (no cards submitted). One
unrelated non-r1 job in the user's queue (`65958904`, plain `bash`,
PENDING) is out of scope for this round and not tracked. (The other
previously-noted non-r1 job, `65952144`, ended `TIMEOUT` at 04:00:11
elapsed on 2026-07-28T21:49 — no longer in queue, no action needed.)

## Completed cards
| Card | Type | Panel geomean skill (±CI) | Falsification verdict | Tools promoted |
|---|---|---|---|---|
| _none — no cards created yet (all streams pre-G3)_ | | | | |

## Flags
- **G3 not yet certified**: no stream may pass its brainstormer gate until
  `state/anchors/*.json` and `state/noise_floor.json` exist. All 5 streams
  correctly parked at `websearch_done_awaiting_G3_brainstormer`.
- **Prior batch-0 attempt (job 65955389) FAILED wholesale**: 14/14 launched
  array tasks fast-failed (~4-6s each) on node `hpc-93-36` (INFRA: CUDA
  busy). Diagnosed and fixed same day — `hpc-93-36` excluded via
  `--exclude` in `eval/run_batch0.sbatch`, resubmitted as `65956106`,
  currently healthy (14/36 COMPLETED, 0 FAILED so far; 256^2 sharp-field
  tasks run ~44 min/task vs ~7-12 min for helmholtz_2d/phase_field_crystal_2d,
  and ifc_poisson runs ~47s/task — not a stall, well within the 6h sbatch
  time budget). At current pace, remaining 22 tasks (3 running + 19
  pending) should clear well inside the time budget once cluster
  concurrency admits the pending ones.
- **reopen candidates**: none (no cards exist).
- **blocked.md**: does not exist — no blocked entries.
- **abandoned streams**: none.
- No transcript inbox present (`state/transcripts/inbox/` does not exist) —
  nothing to archive this run.
