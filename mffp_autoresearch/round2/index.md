# MFFP Autoresearch Round 2 — Dashboard (updated 2026-07-31T15:36:26Z)

## Streams

| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r2s1_direct | 23.0636 (best_floor_panel_geomean) | 1 | r2s1_direct-B1 (drafted) | builder in progress (`models_r2/r2s1_cond_decoder/` written — model.py/train.py/blend.py/certificate.py/config.py/floors.py; no builder handoff yet) | 0 | 2026-07-31T15:19:40Z |
| r2s2_stacked | 23.0636 (best_floor_panel_geomean) | 1 | r2s2_stacked-B1 (drafted) | builder in progress (`models_r2/r2s2_stack/` written — model.py/local_corrector.py/lsi_filter.py/bands.py/periodicity.py/upsample.py/probes.py; no builder handoff yet) | 0 | 2026-07-31T15:13:37Z |
| r2s3_lf_train_signal | 23.0636 (best_floor_panel_geomean) | 1 | r2s3_lf_train_signal-B1 (drafted) | builder in progress (`models_r2/r2s3_rung_supervised/` written — model.py/probes.py; no builder handoff yet) | 0 | 2026-07-31T15:16:13Z |
| r2s4_diag | 23.0636 (best_floor_panel_geomean) | 1 | r2s4_diag-B1 (drafted) | code-review (B1 dispatched 2026-07-31; build 870b62b, smoke green, resume verified) — advanced from builder mid-walk; sbatch submission (`submit.sh`) still not invoked, no `r2-*` job in squeue/sacct | 0 | 2026-07-31T15:36:03Z |

All four anchors are identical: the round-2 launch anchor is the panel
geomean of the best training-free floor per dataset
(`state/anchors/{stream}.json`, `provisional: false`, certified
2026-07-31T14:20:17Z). No stream has diverged yet.

All 4 streams have advanced from the prior maintainer run's mixed
brainstormer/starter positions into `builder` for batch 1. r2s2_stacked and
r2s4_diag drafted complete cards (`status: drafted`, no TBDs) and handed off
to builder; r2s1_direct and r2s3_lf_train_signal followed the same path.
r2s4_diag's builder finished and left a handoff for
code-reviewer/experiment-debugger/analyzers, then advanced to `code-review`
(build 870b62b, smoke green, resume verified) at 15:36:03Z — caught mid-walk,
after this run's delta report had already closed; will be reported as a
delta in the next maintainer run. The other three builders are still mid-run
(model-family files present, no handoff memo yet).

## Running / pending jobs

(none — no `r2-*` SLURM jobs found in `squeue`/`sacct`; `sacct` since
2026-07-29 shows only `r1-*` jobs and one unrelated interactive `bash`
session, job 66149132, RUNNING ~1h36m, unrelated to round 2. r2s4_diag's
`scripts/submit.sh` exists and is ready to submit `r2-r2s4_diag-B1-s0` but
has not been invoked yet — this is the next SLURM submission to watch for.)

## Completed cards

(none — all 4 batch-1 cards are `status: drafted` with empty `job_ids`,
`build_notes`, `debug_notes`, `review_notes`; no card has reached parts 5/7
with real content yet, and `5_actual_result`/`6_analysis`/`7_gap_and_future`
are still placeholders in all 4)

## Flags

- **Gates**: G1-r2 PASS, G2-r2 PASS, G3-r2 PASS (all 2026-07-31,
  `state/gates.md`) — round cleared for stream launch.
- **Noise floor**: `state/noise_floor.json` is still PROVISIONAL
  (`_source: round1-batch0-rescaled`) until r2s4-B1 certifies. r2s4_diag's
  builder has staged the real certification path (`scripts/03_certify.sh` →
  `mffp_autoresearch_outputs/round2/r2s4_diag/B1/eval/`) but has not run it
  on real seed-0/1/2 SLURM outputs yet — the only certification artifacts
  that exist so far (`scratchpad/certify_synthetic/*`) are explicitly
  FABRICATED build-time plumbing checks per that dir's own README and must
  never be cited or installed over `state/noise_floor.json`. Any claim
  inside the floor/anchor band remains noise until the real cert lands.
- **Round-1 top-3 seed confirms**: NOT launched — pending a separate,
  explicit operator (Eloise) gate (`state/orchestrator_flow.md`).
- No reopen candidates, no `blocked.md` entries, no abandoned streams — none
  are possible yet (all streams at batch 1, no skip/block history).
- Working tree note: `git status --short` shows uncommitted changes under
  `experiment_cards/` and `state/` (r2s4_diag/B1.json modified,
  r2s1_direct and r2s3_lf_train_signal batch_1 dirs untracked, two
  `current_stage.txt` files modified) — these are other subagents'
  (starter/builder) concurrent work-in-progress, not maintainer edits; the
  repo's own `round2: auto-sync` commits (most recent `ac7b4a6`
  2026-07-31T15:14:15Z) periodically land this work.
