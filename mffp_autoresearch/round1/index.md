# MFFP Autoresearch Round 1 — Dashboard (updated 2026-07-29T04:16:14Z)

## Gate status
| Gate | What | Status |
|---|---|---|
| G1 | eval-layer smoke + assertion drill | PASS (2026-07-28) |
| G2 | copy-LF baselines | PASS (2026-07-28) |
| G3 | batch 0: anchors + noise floor (3 seeds) | **PENDING** — array job `65956106` (r1-batch0) 6/36 COMPLETED, 6 RUNNING, 24 PENDING, 0 FAILED. First attempt `65955389` FAILED all 14 launched tasks (INFRA: bad GPU node `hpc-93-36`, now excluded) |
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
| 65956106_6 (r1-batch0) | — (G3 array, task 6: mf_fno_transfer_film × sharp__allen_cahn_2d × seed0) | RUNNING | ~35 min | hpc-24-32 |
| 65956106_7 (r1-batch0) | — (task 7: allen_cahn_2d × seed1) | RUNNING | ~32 min | hpc-26-18 |
| 65956106_8 (r1-batch0) | — (task 8: allen_cahn_2d × seed2) | RUNNING | ~31 min | hpc-25-17 |
| 65956106_9 (r1-batch0) | — (task 9: fisher_kpp_2d × seed0) | RUNNING | ~31 min | hpc-26-17 |
| 65956106_10 (r1-batch0) | — (task 10: fisher_kpp_2d × seed1) | RUNNING | ~31 min | hpc-26-21 |
| 65956106_11 (r1-batch0) | — (task 11: fisher_kpp_2d × seed2) | RUNNING | ~22 min | hpc-26-20 |
| 65956106_[12-35] (r1-batch0) | — (remaining G3 array tasks) | PENDING | 0:00 | Priority |

No `r1-{stream}-B{N}-s{seed}` jobs exist yet (no cards submitted). Two
unrelated non-r1 jobs in the user's queue (`65958904`, `65952144` — plain
`bash`) are out of scope for this round and not tracked.

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
  currently healthy (6 COMPLETED, 0 FAILED so far; tasks 6-11 still running
  at this walk, same as at the prior maintainer walk — no stall, tasks 6-11
  are the 256^2 sharp datasets which run longer than helmholtz/PFC).
- **reopen candidates**: none (no cards exist).
- **blocked.md**: does not exist — no blocked entries.
- **abandoned streams**: none.
- No transcript inbox present (`state/transcripts/inbox/` does not exist) —
  nothing to archive this run.
