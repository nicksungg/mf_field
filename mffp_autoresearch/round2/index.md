# MFFP Autoresearch Round 2 — Dashboard (updated 2026-07-31T17:56:00Z)

## Streams

| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r2s1_direct | 23.0636 (best_floor_panel_geomean) | 1 | r2s1_direct-B1 | **analyzing** — seed-0 job COMPLETED (66163572, h200, 6.95 min), panel_geomean_skill **19.6444** (vs 23.0636 anchor); mechanism-analysis through turn 3 into follow-up sub-probes (`turn3_followup_b.py`, per-dataset amp/phase JSONs, most recent `turn3_followup_ext__helmholtz_2d.json`) — no `turn3_results.md` yet, still writing up | 0 live (job done) | 2026-07-31T17:48:11Z (turn-3 helmholtz follow-up JSON) |
| r2s2_stacked | 23.0636 (best_floor_panel_geomean) | 1 | r2s2_stacked-B1 | **analyzing** — seed-0 panel leg COMPLETED (66166237, h200, 20.13 min, panel_geomean_skill **14.0756** on scored arm `frozen`; guard leg 66166238 completed earlier); mechanism-analyzer turn 1 progressed to a `turn1b_emulator_vs_ridge` follow-up and just wrote `reanalysis_turn_1_results.md` — turn 1 write-up essentially complete | 0 live (jobs done) | 2026-07-31T17:53:14Z (turn-1 results md written, ~65s before this check) |
| r2s3_lf_train_signal | 23.0636 (best_floor_panel_geomean) | 1 | r2s3_lf_train_signal-B1 | **running** (major delta this run) — seed-0 job (66165379) RUNNING since 16:45:32Z (~1h07m elapsed), **PRIMARY `rung_native` arm now COMPLETE on all 6 panel datasets** (`result_panel_rung_native_s0.json`, panel_geomean_skill **25.3919**), now mid-`rung_upsampled` mechanism-control arm (ifc_poisson done, cahn_hilliard checkpointing as of ~17:52:41Z) — confirmed live, not stalled | 1 (RUNNING, ~1h07m) | 2026-07-31T17:52:41Z (fresh cahn_hilliard rung_upsampled checkpoint write) |
| r2s4_diag | **19.8178** (certified_3seed_panel_geomean, CI95 [19.385, 20.527]) | 1 | r2s4_diag-B1 | **analyzing** — all 3 seeds COMPLETED (66161480/81/82, h200, ~4.1-4.4 min each); noise floor CERTIFIED/INSTALLED (unchanged, 16:49:04Z); mechanism-analysis progressed turn 1 (complete, results.md + figure) into **turn 2** (`turn2.log` actively appending per-dataset kNN-ceiling/headroom rows: helmholtz/pfc/allen_cahn done as of this check) with `reanalysis_turn_3.py` already staged | 0 live (all done) | 2026-07-31T17:52:54Z (turn-2 log append, ~74s before this check) |

**Anchor note**: r2s4_diag remains the only stream with a *certified* anchor
(`certified_3seed_panel_geomean`, 19.8178, replacing the training-free floor)
— r2s1_direct, r2s2_stacked, r2s3_lf_train_signal remain on the launch-time
`best_floor_panel_geomean` anchor (23.0636, `certified_utc` 2026-07-31T14:20:17Z,
unchanged). No anchor deltas this run. All anchors rendered verbatim from
`state/anchors/*.json`.

**This run's headline event**: r2s3_lf_train_signal's PRIMARY `rung_native`
arm finished (panel_geomean_skill 25.3919), completing the last outstanding
primary-arm result of the round's batch-1 wave. Against the already-scored
`hf_only` control (panel_geomean_skill 26.8687, from a prior run), the
per-dataset contrast (lower skill = better; numbers below computed directly
from the two raw result JSONs for visibility only — falsification-clause
verdicts are the initial-analyzer's call, not made here):
- **ifc_poisson (F1, primary) — surprising direction**: `rung_native`
  16.7963 is *worse* than `hf_only` 9.4466 by 7.3497 skill units (the card's
  F1 clause requires `rung_native` to *beat* `hf_only` by more than the
  0.2399 certified/provisional floor; instead it is worse by ~30x that
  margin). If this holds up under the analyzer's read, it is the opposite of
  the card's pre-registered prediction (~10 skill-unit gain from the 170
  disjoint LF conditions) — flagged prominently, not adjudicated here.
- 5 condition-aligned datasets (F3, degeneracy prediction): `rung_native` vs
  `hf_only`, positive = `rung_native` better (lower skill) — helmholtz +17.16
  (exceeds provisional threshold 10.68), pfc +4.48 (< 6.98), allen_cahn
  -21.56 (`hf_only` better), fisher_kpp -0.86 (`hf_only` better),
  cahn_hilliard +0.51 (< 1.16) — only 1 of 5 exceeds its threshold.
- `rung_upsampled` mechanism control on ifc_poisson (already landed):
  nRMSE 29.97 — far worse than either primary arm; flagged as a number the
  mechanism-analyzer should sanity-check before use (could be a genuine
  finding or an arm-specific anomaly; not adjudicated here).

## Running / pending jobs

| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| 66165379 | r2s3_lf_train_signal-B1 (seed 0) | RUNNING | ~1:07:33 | hpc-sm-01-15 (`hf_only` + `rung_native` done -> `rung_upsampled` in progress) |
| 66149132 | (unrelated interactive `bash`) | RUNNING | ~3h53m | hpc-90-18 — not a round-2 job |
| 66162876 | (unrelated interactive `bash`) | RUNNING | ~1h37m | hpc-24-22 — not a round-2 job |
| 66166013 | (unrelated interactive `bash`) | RUNNING | ~1h00m | hpc-89-13 — not a round-2 job |

6 `r1-*` jobs also PENDING in the queue (round-1 top-3 seed-confirm work) —
out of this maintainer's scope, noted only for queue-context.

## Completed cards

(none — all 4 batch-1 cards still have `6_analysis`/`7_gap_and_future` as
placeholders; r2s1_direct, r2s2_stacked, and r2s4_diag all have populated
`5_actual_result` and are in active mechanism-analysis; r2s3_lf_train_signal's
primary arm just landed but its card `5_actual_result` is still `null`
pending the still-running job's remaining arms + declared-baseline gate)

| Card | Type | Panel geomean skill (±CI) | Falsification verdict | Tools promoted |
|---|---|---|---|---|
| r2s1_direct-B1 | model | 19.6444 (single seed 0, no CI yet) | pending analyzer | pending |
| r2s2_stacked-B1 | model | 14.0756 (single seed 0, no CI yet; scored arm `frozen`) | pending analyzer | pending |
| r2s4_diag-B1 | diagnostic | 19.8178 IQM, CI95 [19.385, 20.527] (3 seeds) | pending analyzer | n/a (diagnostic) |
| r2s3_lf_train_signal-B1 | model | 25.3919 (`rung_native`, single seed 0, primary arm just landed; card not yet updated — job still running) | pending analyzer (job still running) | pending |

## Flags

- **r2s3_lf_train_signal-B1 PRIMARY arm COMPLETED (this run's headline
  delta)**: `rung_native` finished all 6 panel datasets mid-job
  (`result_panel_rung_native_s0.json`, panel_geomean_skill 25.3919);
  `hf_only` control was already scored (26.8687, prior run). The job
  (66165379) continues RUNNING into the `rung_upsampled` mechanism-control
  arm (ifc_poisson landed at nRMSE 29.97 — flagged for the analyzer as an
  unusually large number to sanity-check, not adjudicated here) then still
  owes cahn_hilliard + pfc for that arm, the guard leg, and the declared-
  baseline (`mf_fno_transfer_film`) validity gate before the card's
  `5_actual_result` can be populated. Raw per-dataset numbers surfaced above
  for downstream visibility; falsification-clause verdicts are the
  initial-analyzer's call.
- **Mechanism-analysis progressing on all 3 already-analyzing streams**
  (all liveness-confirmed via filesystem-relative epoch deltas, none
  stalled): r2s1_direct-B1 (turn 3 core work done, now in follow-up sub-
  probes, ~6 min since last file write — write-up likely imminent);
  r2s2_stacked-B1 (turn 1 write-up (`reanalysis_turn_1_results.md`) just
  landed, ~65s before this check); r2s4_diag-B1 (turn 1 complete, turn 2's
  `turn2.log` actively appending per-dataset rows, ~74s before this check,
  turn 3 script already staged).
- **Timing ledger**: no new upserts this run — `state/timing_ledger.json`
  unchanged at 6 entries (`sacct` shows no newly-COMPLETED r2- jobs since
  the last run; 66165379 remains RUNNING and thus ineligible). Validated as
  parseable JSON (unmodified).
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
  window-robust and quotable.
- **Analyzer caveat (r2s2_stacked-B1, from code-review + initial-analyzer)**,
  carried forward: ifc_poisson's rung ladder is UNPAIRED (independent
  condition draws per rung, min distance 0.08-0.30, never 0) — matches
  r2s3's independent finding, a cross-stream benchmark-integrity item for the
  round report. A2/A5 arms there are `arm_semantics_degraded=True`; A2-A3 is
  an upper bound on shift, not epoch-matched. Do not quote the "A2-A3
  identically zero" code string (measured 0.00883).
- **Analyzer caveat (r2s3_lf_train_signal-B1, from code-review)**, carried
  forward and now directly relevant with the primary arm landed: the
  shared-max-abs-rungs scaler makes ifc_poisson's `rung_native` stage-1 loss
  ~42x amplitude-weighted toward rung 8 over HF — a card-locked design
  choice, not a build defect. F1 is epoch-matched but not step-matched
  (`rung_native` gets ~14x more optimizer steps per epoch than `hf_only` on
  ifc_poisson at batch 16). Both must be read alongside the F1 number above.
- **Gates**: G1-r2 PASS, G2-r2 PASS, G3-r2 PASS (all 2026-07-31,
  `state/gates.md`) — round cleared for stream launch. Unchanged this run.
- **Round-1 top-3 seed confirms**: NOT this maintainer's scope (round-1 jobs
  visible in `squeue` as `r1-*`, PENDING) — separate round, separate report.
- No reopen candidates, no `blocked.md` entries, no abandoned streams — none
  are possible yet (all streams at batch 1, no skip/block history).
- Repo hygiene: `git status --short` on `mffp_autoresearch/round2/` shows only
  `experiment_cards/r2s2_stacked/batch_1/B1.json` modified in the working
  tree (from another subagent's write this cycle, predating this maintainer
  run; most recent `round2: auto-sync` commit `d45f665`,
  2026-07-31T17:44:19Z); confirmed no Write call this run touched
  `experiment_cards/`.
