# MFFP Autoresearch Round 2 — Dashboard (updated 2026-07-31T16:11:57Z)

## Streams

| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r2s1_direct | 23.0636 (best_floor_panel_geomean) | 1 | r2s1_direct-B1 (**built**) | code-review — builder finished (`build_commit` 0af8b38, `notes/handoff_experiment_builder.md` written 16:09:41Z); model family `models_r2/r2s1_cond_decoder/` complete (config/common/model/floors/certificate/train/blend/smoke_eval); contract smoke green (helmholtz 2ep, test_hf nRMSE 0.9301, skill 3.110); floor-seam check reproduces `floors.json` to 0.0 on all 9 panel+guard datasets; checkpoint resume verified both branches; `scripts/{01_train_eval.sh,submit.sh,submit_seeds_2_3.sh}` staged, not yet submitted | 0 | 2026-07-31T16:09:41Z (build_notes landed; card status field still `built`, no job_ids yet) |
| r2s2_stacked | 23.0636 (best_floor_panel_geomean) | 1 | r2s2_stacked-B1 (drafted) | builder DONE — `notes/handoff_experiment_builder.md` written 15:48:15Z (5 arms + S1/S2 sidecars + P1/P2 probes + gates V1-V7 built; flags ifc_poisson's rung ladder as UNPAIRED, arms A2/A5 there marked `arm_semantics_degraded=True`); card `status` field STILL not updated to `built` (23+ min after handoff, stage file still reads `builder`) — this is now the oldest outstanding builder->card-catchup lag in the round, worth flagging to the orchestrator if it persists another cycle | 0 | 2026-07-31T15:48:15Z |
| r2s3_lf_train_signal | 23.0636 (best_floor_panel_geomean) | 1 | r2s3_lf_train_signal-B1 (drafted) | builder in progress (`models_r2/r2s3_rung_supervised/` — model.py/probes.py; active guard-tier debug runs, most recent `scratchpad/dbg_sod.log` ~13 min old) — confirmed live via filesystem-relative epoch delta, not stalled; no builder handoff yet | 0 | 2026-07-31T15:16:13Z |
| r2s4_diag | 23.0636 (best_floor_panel_geomean) | 1 | r2s4_diag-B1 (**running**) | 3-seed certification jobs submitted (job_ids 66161480/81/82, `r2-r2s4_diag-B1-s{0,1,2}`) — all 3 currently **PENDING** (Priority) in both `squeue` and `sacct`, not yet started running, NodeList "None assigned" | 3 (all PENDING) | 2026-07-31T15:58:25Z (card status -> running, jobs submitted) |

All four anchors are identical: the round-2 launch anchor is the panel
geomean of the best training-free floor per dataset
(`state/anchors/{stream}.json`, `provisional: false`, certified
2026-07-31T14:20:17Z). No stream has diverged yet.

Since the prior maintainer run (15:55:30Z): r2s1_direct's builder finished
(handoff memo 16:09:41Z, card `status` advanced `drafted` -> `built`,
`build_commit` 0af8b38072e2f119e0c2aa35a6981dcd533e18c8, 9 detailed
`build_notes` entries incl. a flagged deviation on the D3 certificate
closest-pair-vs-random-pair fit); r2s4_diag's 3-seed certification run was
submitted to SLURM (jobs 66161480/81/82, card `status` `built` -> `running`)
but all 3 jobs remain PENDING (queue priority), none have started. r2s2_stacked
remains stuck at builder-done-but-card-not-caught-up for a second consecutive
run (now ~23 min stale). r2s3_lf_train_signal builder continues in progress,
confirmed live.

## Running / pending jobs

| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| 66161480 | r2s4_diag-B1 (seed 0) | PENDING | 00:00:00 | None assigned (Priority) |
| 66161481 | r2s4_diag-B1 (seed 1) | PENDING | 00:00:00 | None assigned (Priority) |
| 66161482 | r2s4_diag-B1 (seed 2) | PENDING | 00:00:00 | None assigned (Priority) |
| 66149132 | (unrelated interactive `bash`) | RUNNING | ~2h11m | hpc-90-18 — not a round-2 job |

r2s1_direct's `scripts/submit.sh` is staged (`r2-r2s1_direct-B1-s0`) but not
yet invoked. r2s2_stacked also has `scripts/submit.sh` +
`scripts/submit_guard.sh` staged and unsubmitted.

## Completed cards

(none — all 4 batch-1 cards still have `5_actual_result`/`6_analysis`/
`7_gap_and_future` as placeholders and no COMPLETED SLURM jobs yet;
r2s4_diag is the only card with live job_ids, all still PENDING)

## Flags

- **Gates**: G1-r2 PASS, G2-r2 PASS, G3-r2 PASS (all 2026-07-31,
  `state/gates.md`) — round cleared for stream launch. Unchanged this run.
- **Noise floor**: `state/noise_floor.json` is still PROVISIONAL
  (`_source: round1-batch0-rescaled`) until r2s4-B1 certifies. The real
  certification jobs (seeds 0-2) are now submitted but PENDING in the queue
  — no real cert data exists yet. The only certification-adjacent artifacts
  on disk (`worktrees/r2s4_diag/B1/scratchpad/certify_synthetic/*`) remain
  explicitly FABRICATED plumbing-check data per that dir's own README and
  must never be cited or installed over `state/noise_floor.json`.
- **Builder->card lag**: r2s2_stacked's builder handoff (15:48:15Z) has not
  been reflected in its card `status` or `current_stage.txt` for two
  consecutive maintainer runs (~23 min and counting) — flagged for the
  orchestrator; not yet actionable as a stall (well within normal pulse
  cadence) but the longest-outstanding lag in the round so far.
- **Round-1 top-3 seed confirms**: NOT launched — pending a separate,
  explicit operator (Eloise) gate (`state/orchestrator_flow.md`).
- No reopen candidates, no `blocked.md` entries, no abandoned streams — none
  are possible yet (all streams at batch 1, no skip/block history).
- Timing ledger: `state/timing_ledger.json` still has zero entries — no
  COMPLETED `r2-*` job exists yet to upsert.
- Repo hygiene: `git status --short` on `mffp_autoresearch/round2/` shows
  uncommitted working-tree changes to `experiment_cards/r2s1_direct/batch_1/B1.json`
  and `experiment_cards/r2s4_diag/batch_1/B1.json` from other subagents
  (builder/starter), not from this maintainer run — confirmed no Write call
  this run touched `experiment_cards/`. Most recent `round2: auto-sync`
  commit is `b471365` (2026-07-31T15:44:17Z), which predates these two
  working-tree changes.
