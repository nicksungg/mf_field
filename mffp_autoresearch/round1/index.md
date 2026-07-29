# MFFP Autoresearch Round 1 — Dashboard (updated 2026-07-29T07:16:39Z)

## Gate status
| Gate | What | Status |
|---|---|---|
| G1 | eval-layer smoke + assertion drill | PASS (2026-07-28) |
| G2 | copy-LF baselines | PASS (2026-07-28) |
| G3 | batch 0: anchors + noise floor (3 seeds) | **PENDING** — array job `65956106` (r1-batch0) 34/36 COMPLETED, 2 RUNNING (tasks 31-32), 0 PENDING, 0 FAILED. First attempt `65955389` FAILED all 14 launched tasks (INFRA: bad GPU node `hpc-93-36`, now excluded) |
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
| 65956106_31 (r1-batch0) | — (G3 array task 31: mf_fno_pinn_transfer x sharp__cahn_hilliard seed1) | RUNNING | ~37 min | hpc-24-32 |
| 65956106_32 (r1-batch0) | — (G3 array task 32: mf_fno_pinn_transfer x sharp__cahn_hilliard seed2) | RUNNING | ~36 min | hpc-25-17 |

34/36 COMPLETED, 0 FAILED, 0 PENDING — unchanged since the prior walk except
elapsed time on the two RUNNING tail tasks (~35/36 min -> ~36/37 min),
consistent with the ~44 min typical for this family's 256^2 sharp datasets
(family-1 pattern on seed0/task30) — not stalled. Confirmed via
`squeue -j 65956106 -a -r` (tasks 31-32 `R`) cross-checked against
`sacct -j 65956106 -P` (RUNNING, exit 0:0 pending completion). No
`r1-{stream}-B{N}-s{seed}` jobs exist yet (no cards submitted). No unrelated
non-r1 jobs remain in the user's queue this walk (historical CANCELLED jobs
`65958902`, `65958904`, `65960289` unchanged, out of scope for this round).

## Completed cards
| Card | Type | Panel geomean skill (±CI) | Falsification verdict | Tools promoted |
|---|---|---|---|---|
| _none — no cards created yet (all streams pre-G3)_ | | | | |

## Flags
- **G3 not yet certified**: no stream may pass its brainstormer gate until
  `state/anchors/*.json` and `state/noise_floor.json` exist. All 5 streams
  correctly parked at `websearch_done_awaiting_G3_brainstormer`.
- **G3 close to completion**: 34/36 array tasks COMPLETED, 0 FAILED
  throughout; only the tail 2 tasks (cahn_hilliard seeds1-2,
  mf_fno_pinn_transfer) remain RUNNING (~36-37 min elapsed of ~44 min
  typical) — expected to finish within 1-2 more maintainer/orchestrator
  cycles.
- **Prior batch-0 attempt (job 65955389) FAILED wholesale**: 14/14 launched
  array tasks fast-failed (~4-6s each) on node `hpc-93-36` (INFRA: CUDA
  busy). Diagnosed and fixed same day — `hpc-93-36` excluded via
  `--exclude` in `eval/run_batch0.sbatch`, resubmitted as `65956106`,
  currently healthy (34/36 COMPLETED, 0 FAILED).
- **reopen candidates**: none (no cards exist).
- **blocked.md**: does not exist — no blocked entries.
- **abandoned streams**: none.
- No transcript inbox present (`state/transcripts/inbox/` does not exist) —
  nothing to archive this run.
