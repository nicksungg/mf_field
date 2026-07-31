# MFFP Autoresearch Round 2 — Dashboard (updated 2026-07-31T17:34:00Z)

## Streams

| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r2s1_direct | 23.0636 (best_floor_panel_geomean) | 1 | r2s1_direct-B1 | **analyzing** — seed-0 job COMPLETED (66163572, h200, 6.95 min), panel_geomean_skill **19.6444** (vs 23.0636 anchor); mechanism-analysis progressing past turn 2 (`reanalysis_turn_2_results.md` written) into **turn 3** (`reanalysis_turn_3.py` fresh) | 0 live (job done) | 2026-07-31T~17:29:49Z (turn-3 script started) |
| r2s2_stacked | 23.0636 (best_floor_panel_geomean) | 1 | r2s2_stacked-B1 | **analyzing** (new this run) — seed-0 **panel leg COMPLETED** (66166237, h200, 20.13 min, panel_geomean_skill **14.0756** on scored arm `frozen`; guard leg 66166238 completed last run, guard-panel skill 0.2792); initial-analyzer handed off (headline: stack adds ~nothing on the 5 paired panel datasets excl. ifc_poisson — emul_only 19.19 vs frozen 19.18, Δ0.002; the 24.68→14.08 apparent gain is driven entirely by the ifc_poisson column where `attribution.valid=false`); mechanism-analyzer turn 1 now in progress | 0 live (jobs done) | 2026-07-31T~17:31:42Z (mechanism-analyzer turn-1 script fresh) |
| r2s3_lf_train_signal | 23.0636 (best_floor_panel_geomean) | 1 | r2s3_lf_train_signal-B1 | **running** — seed-0 job (66165379) RUNNING since 16:45:32Z (~49 min elapsed at check), `hf_only` arm already scored (`result_panel_hf_only_s0.json`), now mid-`rung_native` arm stepping through per-dataset checkpoints (helmholtz/pfc/allen_cahn done, fisher_kpp checkpointing as of ~17:33:16Z) — confirmed live via filesystem-relative deltas, not stalled | 1 (RUNNING, ~49m) | 2026-07-31T~17:33:16Z (fresh fisher_kpp checkpoint write) |
| r2s4_diag | **19.8178** (certified_3seed_panel_geomean, CI95 [19.385, 20.527]) | 1 | r2s4_diag-B1 | **analyzing** — all 3 seeds COMPLETED (66161480/81/82, h200, ~4.1-4.4 min each); noise floor CERTIFIED/INSTALLED (unchanged, 16:49:04Z); mechanism-analysis turn 1 progressing (`reanalysis_turn_1_results.md` written ~17:32:53Z, `turn1_collapse.png` figure produced) — confirmed live, turn 1 nearing completion | 0 live (all done) | 2026-07-31T~17:32:53Z (turn-1 results md written) |

**Anchor note**: r2s4_diag remains the only stream with a *certified* anchor
(`certified_3seed_panel_geomean`, 19.8178, replacing the training-free floor)
— r2s1_direct, r2s2_stacked, r2s3_lf_train_signal remain on the launch-time
`best_floor_panel_geomean` anchor (23.0636, `certified_utc` 2026-07-31T14:20:17Z,
unchanged). No anchor deltas this run. All anchors rendered verbatim from
`state/anchors/*.json`.

**BATCH-1 WAVE FULLY SUBMITTED, all 4 seed-0 legs now COMPLETED at least once**
(r2s2_stacked's panel leg was the last outstanding batch-1 job to finish this
run); 3 of 4 streams are now in mechanism-analysis, r2s3_lf_train_signal is
the only stream still running its primary training job.

## Running / pending jobs

| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| 66165379 | r2s3_lf_train_signal-B1 (seed 0) | RUNNING | ~00:48:45 | hpc-sm-01-15 (arm `hf_only` done -> `rung_native` in progress) |
| 66149132 | (unrelated interactive `bash`) | RUNNING | ~3h34m | hpc-90-18 — not a round-2 job |
| 66162876 | (unrelated interactive `bash`) | RUNNING | ~1h19m | hpc-24-22 — not a round-2 job |
| 66166013 | (unrelated interactive `bash`) | RUNNING | ~42m | hpc-89-13 — not a round-2 job |

6 `r1-*` jobs also PENDING in the queue (round-1 top-3 seed-confirm work) —
out of this maintainer's scope, noted only for queue-context.

## Completed cards

(none — all 4 batch-1 cards still have `6_analysis`/`7_gap_and_future` as
placeholders; r2s1_direct, r2s2_stacked, and r2s4_diag all have populated
`5_actual_result` and are in active mechanism-analysis, but no card has
closed out yet)

| Card | Type | Panel geomean skill (±CI) | Falsification verdict | Tools promoted |
|---|---|---|---|---|
| r2s1_direct-B1 | model | 19.6444 (single seed 0, no CI yet) | pending analyzer | pending |
| r2s2_stacked-B1 | model | 14.0756 (single seed 0, no CI yet; scored arm `frozen`) | pending analyzer | pending |
| r2s4_diag-B1 | diagnostic | 19.8178 IQM, CI95 [19.385, 20.527] (3 seeds) | pending analyzer | n/a (diagnostic) |

## Flags

- **r2s2_stacked panel leg COMPLETED (this run's headline delta)**: job
  66166237 finished at 17:15:26Z (20.13 min, h200), card `status` moved
  `running` -> `analyzing`, `5_actual_result` populated (scored arm `frozen`,
  panel_geomean_skill 14.0756). Initial-analyzer's headline finding: **the
  stack (emulator + frozen round-1 DC corrector) adds essentially nothing on
  the 5 paired panel datasets** — emul_only 19.1863 vs frozen 19.1843 (Δ
  0.002, well inside the floor 1.1419); the apparent 24.68→14.08 gain vs. the
  unpaired-composite comparator is driven entirely by one degraded column
  (ifc_poisson 87.02→2.99) where the corrector is pseudo-LF-fit and
  `attribution.valid=false`. Two pre-registrations broke: A4≤A2 inverts on
  6/6 panel datasets (holds 3/3 guard); ADR r2-0003's A2≈A5 holds only on
  fisher_kpp. Sidecar S2 shows emulator error is ~all the error (real-LF
  corrector nRMSE 1.7e-7 to 5.9e-3 vs pseudo-LF 0.24-0.46). Mechanism-analyzer
  now investigating the panel/guard corrector-gating split and cahn_hilliard.
- **All 4 streams' batch-1 seed-0 jobs have now completed at least once**
  (r2s3_lf_train_signal's primary training job is the sole still-RUNNING
  piece, ~49 min elapsed, actively progressing through the `rung_native` arm).
- **Timing ledger**: `state/timing_ledger.json` gained 1 new upsert this run
  — r2s2_stacked's panel leg (66166237, 20.13 min, h200, `family: r2s2_stack`,
  `leg: panel`), and the prior guard-leg entry's note was updated to point at
  it (no longer "still RUNNING"). 6 entries total now. r2s3_lf_train_signal's
  job (66165379) is still RUNNING, not yet eligible.
- **Mechanism-analysis in progress on 3/4 streams** (all liveness-confirmed
  via filesystem-relative epoch deltas, none stalled): r2s1_direct-B1 (turn 3
  of 3 started, following completed turns 1-2 on POD-vs-scored-model
  comparison, overfit anatomy, lambda bimodality); r2s2_stacked-B1 (turn 1
  just started, per initial-analyzer's handoff — see flag above); r2s4_diag-B1
  (turn 1 nearing completion — results md + figure written, leads: fisher
  cond-mean convergence, helmholtz tail, kNN floor structure).
- **Timestamp anomaly (r2s1_direct-B1 review_notes)**, carried forward
  unchanged: `review_notes[0].utc` still reads `2026-07-31T17:05:00Z`, ahead
  of system clock at the time it was written and postdating the card's own
  mtime (16:23:17Z). Read-only for cards, flagged for awareness; no scored
  quantity affected.
- **Analyzer caveat carried forward (r2s1_direct-B1, from code-review)**: the
  D3 certificate's aleatoric-floor estimate is window-sensitive — at the
  recipe's window (1000 closest pairs), `ext__helmholtz_2d` reads 1.200,
  worse than the zero predictor, despite the card's gate stamping
  `verdict: supported, trustworthy: true` (gate tests `d_min`, not window
  width). Must not be reported as a ceiling for helmholtz; `allen_cahn`'s
  ceiling must be reported as a range (0.315-0.471); `pfc`/`fisher_kpp` are
  window-robust and quotable. The mechanism-analyzer (now in turn 3) should
  respect this caveat.
- **Analyzer caveat (r2s2_stacked-B1, from code-review + initial-analyzer)**,
  carried forward and now reinforced by the initial-analyzer's own finding
  above: ifc_poisson's rung ladder is UNPAIRED (independent condition draws
  per rung, min distance 0.08-0.30, never 0) — matches r2s3's independent
  finding, a cross-stream benchmark-integrity item for the round report. A2/A5
  arms there are `arm_semantics_degraded=True`; A2-A3 is an upper bound on
  shift, not epoch-matched. Do not quote the "A2-A3 identically zero" code
  string (measured 0.00883).
- **Analyzer caveat (r2s3_lf_train_signal-B1, from code-review)**, carried
  forward: the shared-max-abs-rungs scaler makes ifc_poisson's `rung_native`
  stage-1 loss ~42x amplitude-weighted toward rung 8 over HF — a card-locked
  design choice, not a build defect. A null/negative F1 on ifc_poisson is NOT
  by itself evidence LF training signal adds nothing; part 5 must report
  `extra.shared_scaler_max_abs` per arm alongside F1. F1 is epoch-matched but
  not step-matched (rung_native gets ~14x more optimizer steps per epoch than
  hf_only on ifc_poisson at batch 16).
- **Gates**: G1-r2 PASS, G2-r2 PASS, G3-r2 PASS (all 2026-07-31,
  `state/gates.md`) — round cleared for stream launch. Unchanged this run.
- **Round-1 top-3 seed confirms**: NOT this maintainer's scope (round-1 jobs
  visible in `squeue` as `r1-*`, PENDING) — separate round, separate report.
- No reopen candidates, no `blocked.md` entries, no abandoned streams — none
  are possible yet (all streams at batch 1, no skip/block history).
- Repo hygiene: `git status --short` on `mffp_autoresearch/round2/` shows
  uncommitted changes to `experiment_cards/{r2s1_direct,r2s2_stacked,
  r2s4_diag}/batch_1/B1.json`, `index.md`, `state/maintainer_report.md`,
  `state/orchestrator_flow.md`, and `state/r2s2_stacked/current_stage.txt` —
  the experiment_cards changes are from other subagents'/orchestrator's
  writes this cycle, predating this maintainer run (most recent
  `round2: auto-sync` commit `091df99`, 2026-07-31T17:14:16Z); confirmed no
  Write call this run touched `experiment_cards/`.
