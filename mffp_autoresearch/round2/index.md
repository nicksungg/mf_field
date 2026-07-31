# MFFP Autoresearch Round 2 — Dashboard (updated 2026-07-31T15:11:14Z)

## Streams

| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r2s1_direct | 23.0636 (best_floor_panel_geomean) | 1 | — | brainstormer (B1; websearch done — D1/D2 preempted, D3 conditional-mean-cert open) | 0 | 2026-07-31T14:56:23Z |
| r2s2_stacked | 23.0636 (best_floor_panel_geomean) | 1 | — | starter (B1; proposal: native-grid pseudo-LF emulator → vendored dc_cleaned, 5 paired arms incl condmean_lf) | 0 | 2026-07-31T15:11:07Z |
| r2s3_lf_train_signal | 23.0636 (best_floor_panel_geomean) | 1 | — | brainstormer (B1; websearch complete — D3 novel, D1/D2 preempted-but-open) | 0 | 2026-07-31T14:54:45Z |
| r2s4_diag | 23.0636 (best_floor_panel_geomean) | 1 | — | starter (B1; proposal: floor cert + kNN cond-mean floor + 3-seed FiLM-FNO certifier) | 0 | 2026-07-31T15:10:22Z |

All four anchors are identical: the round-2 launch anchor is the panel
geomean of the best training-free floor per dataset
(`state/anchors/{stream}.json`, `provisional: false`, certified
2026-07-31T14:20:17Z). No stream has diverged yet.

All 4 streams have progressed one stage since the prior maintainer run
(all were `websearch` at 14:51:29Z): r2s1_direct and r2s3_lf_train_signal
are now at `brainstormer` (each produced a batch-1 brainstormer report —
`brainstormer/{stream}/batch_1/report.md`); r2s2_stacked and r2s4_diag have
advanced past brainstormer into `starter` (worktrees provisioned at
`worktrees/{stream}/B1/`), each with a slot filled 1/1 and 0 reopen
candidates (none exist round-wide — no cards drafted yet).

## Running / pending jobs

(none — no `r2-*` SLURM jobs found in `squeue`/`sacct`; `sacct` since
2026-07-29 shows only `r1-*` jobs and one unrelated interactive `bash`
session, job 66149132, RUNNING ~1h12m, unrelated to round 2)

## Completed cards

(none — `experiment_cards/{r2s1_direct,r2s2_stacked,r2s3_lf_train_signal,
r2s4_diag}/` contain only `.gitkeep`; batch 1 has not reached the
card-drafting stage for any stream yet — r2s2_stacked and r2s4_diag are
closest, now at the starter/worktree stage)

## Flags

- **Gates**: G1-r2 PASS, G2-r2 PASS, G3-r2 PASS (all 2026-07-31,
  `state/gates.md`) — round cleared for stream launch.
- **Noise floor**: `state/noise_floor.json` is PROVISIONAL
  (`_source: round1-batch0-rescaled`) until r2s4-B1 certifies a
  condition→HF 3-seed spread (ADR r2-0002). r2s4-B1's card (once drafted)
  is the one that will certify this — currently at the starter/worktree
  stage, card not yet written. Any claim inside the floor/anchor band is
  currently noise.
- **Round-1 top-3 seed confirms**: NOT launched — pending a separate,
  explicit operator (Eloise) gate (`state/orchestrator_flow.md`).
- No reopen candidates, no `blocked.md` entries, no abandoned streams — none
  are possible yet at batch 1 pre-card stage.
- Batch 1 websearch artifacts exist for all 4 streams
  (`websearches/{stream}/batch_1/`); r2s1/r2s2/r2s4 have 2 iterations +
  summary, r2s3 has 3 iterations + summary. Brainstormer output now present
  for all 4 streams (`brainstormer/{stream}/batch_1/`); r2s2_stacked and
  r2s4_diag have full `report.md` + `summary_so_far.md`, r2s1_direct has
  `summary_so_far.md` only so far, r2s3_lf_train_signal has
  `iteration_1.md` + `summary_so_far.md`.
