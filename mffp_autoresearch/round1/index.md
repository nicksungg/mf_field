# MFFP Autoresearch Round 1 — Dashboard (updated 2026-07-29T05:15:35Z)

## Gate status
| Gate | What | Status |
|---|---|---|
| G1 | eval-layer smoke + assertion drill | PASS (2026-07-28) |
| G2 | copy-LF baselines | PASS (2026-07-28) |
| G3 | batch 0: anchors + noise floor (3 seeds) | **PENDING** — array job `65956106` (r1-batch0) 19/36 COMPLETED, 2 RUNNING, 15 PENDING, 0 FAILED. First attempt `65955389` FAILED all 14 launched tasks (INFRA: bad GPU node `hpc-93-36`, now excluded) |
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
| 65956106_19 (r1-batch0) | — (G3 array, task 19: mf_fno_pinn_transfer × ext\_\_helmholtz\_2d × seed1) | RUNNING | ~1 min | (started 22:14:44) |
| 65956106_20 (r1-batch0) | — (task 20: mf_fno_pinn_transfer × ext\_\_helmholtz\_2d × seed2) | RUNNING | ~1 min | (started 22:14:44) |
| 65956106_[21-35] (r1-batch0) | — (remaining G3 array tasks: 21-23 phase\_field\_crystal\_2d, 24-26 allen\_cahn\_2d, 27-29 fisher\_kpp\_2d, 30-32 cahn\_hilliard, 33-35 ifc\_poisson, all × mf\_fno\_pinn\_transfer × 3 seeds) | PENDING | 0:00 | Priority |

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
  currently healthy (19/36 COMPLETED, 0 FAILED so far; family 0
  `mf_fno_transfer_film` — all 18 tasks — now fully COMPLETED; family 1
  `mf_fno_pinn_transfer` underway, task 18/36 done in 7.58 min matching
  the helmholtz_2d prior, tasks 19-20 running ~1 min in). At current pace,
  remaining 17 tasks (2 running + 15 pending) should clear well inside the
  6h sbatch time budget once cluster concurrency admits the pending ones.
- **reopen candidates**: none (no cards exist).
- **blocked.md**: does not exist — no blocked entries.
- **abandoned streams**: none.
- No transcript inbox present (`state/transcripts/inbox/` does not exist) —
  nothing to archive this run.
