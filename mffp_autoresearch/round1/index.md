# MFFP Autoresearch Round 1 — Dashboard (updated 2026-07-29T06:18:09Z)

## Gate status
| Gate | What | Status |
|---|---|---|
| G1 | eval-layer smoke + assertion drill | PASS (2026-07-28) |
| G2 | copy-LF baselines | PASS (2026-07-28) |
| G3 | batch 0: anchors + noise floor (3 seeds) | **PENDING** — array job `65956106` (r1-batch0) 31/36 COMPLETED, 0 RUNNING, 5 PENDING, 0 FAILED. First attempt `65955389` FAILED all 14 launched tasks (INFRA: bad GPU node `hpc-93-36`, now excluded) |
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
| 65956106_[31-35] (r1-batch0) | — (remaining G3 array tasks: 31-32 cahn\_hilliard seeds1-2, 33-35 ifc\_poisson seeds0-2, all × mf\_fno\_pinn\_transfer) | PENDING | 0:00 | Priority |

No jobs currently RUNNING (tasks 24-30, the allen_cahn/fisher_kpp/cahn_hilliard-seed0
group, all COMPLETED since the prior walk — 7 new completions, 0 FAILED). No
`r1-{stream}-B{N}-s{seed}` jobs exist yet (no cards submitted). No unrelated
non-r1 jobs remain in the user's queue this walk (sacct shows `65958902`,
`65958904`, `65960289` — all plain `bash`, all `CANCELLED by 28156`,
all ended between 2026-07-28T20:09 and 22:20, predating this round's active
window — no action needed, out of scope for this round, unchanged from prior
walks).

## Completed cards
| Card | Type | Panel geomean skill (±CI) | Falsification verdict | Tools promoted |
|---|---|---|---|---|
| _none — no cards created yet (all streams pre-G3)_ | | | | |

## Flags
- **G3 not yet certified**: no stream may pass its brainstormer gate until
  `state/anchors/*.json` and `state/noise_floor.json` exist. All 5 streams
  correctly parked at `websearch_done_awaiting_G3_brainstormer`.
- **G3 close to completion**: 31/36 array tasks COMPLETED, 0 FAILED
  throughout; only the tail 5 tasks (cahn_hilliard seeds1-2 +
  ifc_poisson x3, all mf_fno_pinn_transfer) remain, currently PENDING on
  cluster concurrency (not stalled — sacct confirms no non-r1 jobs
  competing for the user's slots). Given the ifc_poisson family-0 prior
  (~0.8-1.0 min/task) and cahn_hilliard family-0 prior (~44 min/task),
  expect G3 completion within the next 1-2 maintainer/orchestrator
  pulses once slots free up.
- **Prior batch-0 attempt (job 65955389) FAILED wholesale**: 14/14 launched
  array tasks fast-failed (~4-6s each) on node `hpc-93-36` (INFRA: CUDA
  busy). Diagnosed and fixed same day — `hpc-93-36` excluded via
  `--exclude` in `eval/run_batch0.sbatch`, resubmitted as `65956106`,
  currently healthy (31/36 COMPLETED, 0 FAILED).
- **reopen candidates**: none (no cards exist).
- **blocked.md**: does not exist — no blocked entries.
- **abandoned streams**: none.
- No transcript inbox present (`state/transcripts/inbox/` does not exist) —
  nothing to archive this run.
