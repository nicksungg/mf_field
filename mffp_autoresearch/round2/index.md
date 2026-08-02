# MFFP Autoresearch Round 2 — Dashboard (updated 2026-08-02T06:24:00Z)

**Twenty-sixth maintainer walk since the operator halt/resume cycle —
sixth walk of the resumed session.**
Halt landed 2026-08-01T01:31:54Z (commit `10d4e4c`), first resume landed
2026-08-01 ~08:1x PDT (commit `b80e622`). A second session restart
happened ~2026-08-01T20:45 PDT (crons re-created: orchestrator pulse
`aa4dcb66`, maintainer `2c7fed88`, auto-sync `a45bd18b`; commit
`818faef8`). Walks 21-24 were light/no-delta walks under a queue-stall
throttle; walk 25 recorded real deltas for the first time since walk 15
(queue unstuck) and the stall throttle lifted. **This walk (26) continues
full cadence and records further real deltas: the r2s1_direct-B3 debug
attempt 1 landed and its relaunch completed, the r2s2_stacked-B3 panel
leg's timing-ledger upsert was backfilled, and both r2s2_stacked-B3 and
r2s4_diag-B4 advanced their analysis stages.**

## Real deltas this walk (see `state/maintainer_report.md` RUN block for full detail)

- **`r2s1_direct-B3` debugged (experiment-debugger attempt 1, class ALGO
  1/5) and relaunched.** Diagnosed job `66262741`'s FAILED guard leg
  (heat_local `RuntimeError: direction bank is not orthonormal`) as a
  zero-margin numerical-rank screen in `pod_basis` (method-of-snapshots
  squares the condition number). Fix landed as commit `568522c`
  (`_orthonormal_rank`, self-validating truncation to `1e-9`); blast
  radius confirmed narrow (only heat_local's POD rank changes, 33→17
  modes; all other datasets' scored quantities provably unmoved).
  Relaunched as seed-0 job **`66285051`**, which **COMPLETED** (0:0,
  ran 2026-08-01T23:07:45→23:09:34 PDT, elapsed **1:49**) — full
  panel+guard re-run, `panel_geomean_skill` 18.749953928575028 matches
  the debug note's stated 18.7500. Card `job_ids` now
  `['66262741', '66285051']`; status still `running` (parts 5/7 not
  yet populated — awaiting initial-analyzer). **Timing ledger upserted**
  (job `66285051`, 1.82 min, `nvidia_h200`).
- **`r2s2_stacked-B3` panel leg `66267438` timing-ledger entry
  backfilled** (was COMPLETED at walk 25 but missed that walk's upsert
  pass — flagged in this walk's task brief). Confirmed via `sacct -j
  66267438`: exit 0:0, ran 2026-08-01T22:11:52→22:56:38 PDT, elapsed
  **44:46**, `nvidia_h200`. **Timing ledger upserted.** Card's
  initial-analyzer has since run: part 5 populated,
  `panel_geomean_skill` **20.03153609874604** (single seed 0) vs the
  stream's launch anchor **23.0636** — **falsified in the positive
  direction** (beats the anchor). Status advanced `running`→
  `analyzing`; mechanism-analyzer turn 1 now in flight. Job-name-collision
  watch item (reviewer finding R1) reconfirmed: guard job `66267441`
  renamed itself to the panel job's name at runtime — this walk's
  ledger write matched by job ID, not name.
- **`r2s4_diag-B4` mechanism-analyzer turn 1 complete, turn 2 in
  flight.** `reanalysis_progress` advanced to **`turn_2`**; part 5
  (falsified F4, from walk 25) unchanged; parts 6/7 still empty pending
  turn 2.
- **Timing ledger**: 19 → **21 entries** after this walk's two upserts
  (`66267438` panel leg, `66285051` relaunch), both cross-confirmed
  against `sacct -j <id> --format=...,AllocTRES` (`nvidia_h200`) and
  each job's `result_panel_s0.json`. Re-validated parseable JSON after
  each write.
- **squeue now shows 0 live `r2-*` jobs** — the round's queue is fully
  drained; only the unrelated long-running interactive `bash` job
  (`66279812`, ~2:51:37 elapsed) remains.
- No abandonment trip (`STREAM_ABANDON_CAP`=3 not reached anywhere), no
  anchor deltas (all 4 `state/anchors/*.json` byte-identical, mtimes
  predate this run), no gate changes (G1-r2/G2-r2/G3-r2 all still PASS
  2026-07-31), no transcripts to file (`state/transcripts/inbox/` still
  does not exist).

## Streams

| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r2s1_direct | 23.0636 (best_floor_panel_geomean) | 3 | r2s1_direct-B1 **complete**; r2s1_direct-B2 **complete**; r2s1_direct-B3 **running** (parts 5/7 empty) | Seed-0 debugged + relaunched: `66262741` FAILED → fix commit `568522c` → `66285051` **COMPLETED** (1:49, panel_geomean_skill 18.7500). Awaiting initial-analyzer | **0 live SLURM** | **Relaunch COMPLETED this walk (was FAILED-awaiting-debugger at walk 25)** |
| r2s2_stacked | 23.0636 (best_floor_panel_geomean) | 3 | r2s2_stacked-B1 **complete**; r2s2_stacked-B2 **complete**; r2s2_stacked-B3 **analyzing** (part 5 populated, parts 6/7 empty) | Guard `66267441` and panel `66267438` both **COMPLETED** (44:46 + 1:09). Panel `panel_geomean_skill` 20.0315 vs anchor 23.0636 — **falsified positive direction**. Mechanism-analyzer turn 1 in flight | **0 live SLURM** | **Status advanced running→analyzing this walk; ledger backfilled for 66267438** |
| r2s3_lf_train_signal | 23.0636 (best_floor_panel_geomean) | 4 | r2s3_lf_train_signal-B1..B4 **all complete** | **CLOSED (registered close, walk 15)**, unchanged this walk. Not an abandonment — `STREAM_ABANDON_CAP` never applied | **0 live SLURM** | No change since walk 15's close |
| r2s4_diag | **19.8178** (certified_3seed_panel_geomean, CI95 [19.385, 20.527]) | 4 | r2s4_diag-B1..B3 **complete**; r2s4_diag-B4 **analyzing** (part 5 populated, parts 6/7 empty) | Seed-0 job `66269660` COMPLETED (walk 25, ledger upserted). Falsified F4; mechanism-analyzer turn 1 complete, `reanalysis_progress`=`turn_2`, turn 2 in flight | **0 live SLURM** | **`reanalysis_progress` advanced to turn_2 this walk** |

**Anchor note**: r2s4_diag remains the only stream with a *certified*
anchor (`certified_3seed_panel_geomean`, 19.8178) — r2s1_direct,
r2s2_stacked, and the closed r2s3_lf_train_signal remain on the
launch-time `best_floor_panel_geomean` anchor (23.0636, `certified_utc`
2026-07-31T14:20:17Z, unchanged). No anchor deltas this run — all 4
`state/anchors/*.json` files' mtimes predate this run's entire window,
content re-read and confirmed byte-identical to all prior runs. All
anchors rendered verbatim from `state/anchors/*.json`.

## Running / pending jobs

| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| *(none)* | — | — | — | — |

**0 live/pending `r2-*` SLURM jobs** — the queue is fully drained as of
this walk (down from 1 RUNNING at walk 25). Jobs that resolved during
the walk-25→26 gap:

| Job | Card | Final state | Elapsed | Ended (PDT) |
|---|---|---|---|---|
| 66285051 | r2s1_direct-B3 (seed 0, relaunch) | **COMPLETED** | 1:49 | 2026-08-01T23:09:34 |

`sacct`'s 2-day window now shows 21 `r2-*` job records total (18
pre-existing COMPLETED + `66262741` FAILED + `66267438`/`66267441`
COMPLETED + `66269660` COMPLETED + `66285051` COMPLETED). All states
cross-confirmed by both `squeue` (empty of `r2-*`) and `sacct` (explicit
per-job query with `AllocTRES`/`Start`/`End`).

## Completed cards

| Card | Type | Panel geomean skill (±CI) | Falsification verdict | Tools promoted |
|---|---|---|---|---|
| r2s4_diag-B1 | diagnostic | 19.8178 IQM, CI95 [19.385, 20.527] (3 seeds) | n/a (diagnostic); mechanism register complete, part 7 written | `tools/conditional_mean_collapse.py`, `tools/condition_predictability_ceiling.py` |
| r2s4_diag-B2 | diagnostic | 19.8829 own single-run 3-seed geomean (T0 primary arm) | **falsified**: aux-LF-TARGET head worth nothing at any N_fit 20-320 on 15/15 dataset×N cells | `tools/ladder_pair_alignment_audit.py`, `tools/shrinkage_curve_anatomy.py`, `tools/condition_predictability_ceiling_fast.py` |
| r2s1_direct-B1 | model | 19.6444 (single seed 0) | **falsified in a split reading**: floors clause CONFIRMED, architecture clause FALSIFIED (156-param closed-form head statistically indistinguishable from the 15.9M-param shipped arm) | `tools/band_gain_counterfactual.py`, `tools/condition_identifiable_rank.py` |
| r2s3_lf_train_signal-B1 | model | 25.3919 (`rung_native`, single seed 0) | **falsified in a split reading**: F1 FALSIFIED (shared-scaler confound); information claim CONFIRMED | `tools/affine_ladder_voi.py`, `tools/posthoc_repair_ladder.py` |
| r2s2_stacked-B1 | model | 14.0756 (single seed 0) | clean negative, conjunctive clause did not fire (conjunct 1 held, conjunct 2 failed) | `tools/reachable_set_rank_audit.py`, `tools/surrogate_coherence_eligibility.py` |
| r2s3_lf_train_signal-B2 | model | not computed (3-of-6 panel, informational) | **confirmed**; `cratered_verdict: proceed_to_seeds_1_2`; 1 guard flag | `tools/design_coverage_audit.py`, `tools/null_family_ceiling_audit.py` |
| r2s1_direct-B2 | model | 18.3622 (single seed 0, no falsification weight) | **falsified**: L1/L2 fire, L3/L4 do not | `tools/blend_decorrelation_payoff.py`, `tools/selection_set_vs_window_audit.py` |
| r2s2_stacked-B2 | diagnostic | 19.386837 (single seed 0) | **falsified**: F1/F2/F3 fire, F4 does not; retracts B1's `surrogate_coherence_eligibility.py` rule as a GATE | `tools/zero_gradient_stage_ladder.py`, `tools/relative_gain_units_audit.py` |
| r2s3_lf_train_signal-B3 | model | 17.114970 (`A1_lf_cov`, single seed 0) | **falsified** (knife-edge, 5/7 readings); success-criterion-1 met on exactly 3 datasets; `cratered_verdict: cratered` | `tools/effect_threshold_readings.py`, `tools/map_dispersion_scale_shape.py` |
| r2s4_diag-B3 | diagnostic | 19.172826 (single seed 0) | **falsified** (F3 hardened, F4a fires on corrected definition, F1 partial survival) | `tools/ledger_contamination_audit.py`, `tools/band_retention_probe.py` |
| r2s3_lf_train_signal-B4 | diagnostic (mechanism/register) | n/a — reuses B3's skills; graded criterion-1 legacy ch=A/ifc=B/ac=C | S1 **CONFIRMED false**; part 7: **formal stream close**, no B5 | `tools/gain_head_feasibility_audit.py`, `tools/effect_concentration_audit.py` |

`r2s1_direct-B3` has a COMPLETED SLURM job (relaunch `66285051`) but
remains `running` at the card level (parts 5/7 empty, awaiting
initial-analyzer). `r2s2_stacked-B3` and `r2s4_diag-B4` are both
`analyzing` (part 5 populated, parts 6/7 pending mechanism-analyzer
turns) — not listed here until they close.

## Flags

- **`r2s1_direct-B3` debug loop resolved (attempt 1/5, class ALGO)**:
  fix commit `568522c` (self-validating POD rank truncation in
  `pod_basis`); relaunch `66285051` COMPLETED clean. No further debugger
  action pending as of this walk; the round's first job-level FAILURE
  since launch is now resolved at the SLURM level, awaiting
  initial-analyzer consumption.
- **Timing ledger upserted this walk**: 2 new COMPLETED-job entries
  added (19 → 21 total) — `66267438` (r2s2_stacked-B3 panel, 44.77 min,
  `nvidia_h200`, **backfilled from walk 25's miss**) and `66285051`
  (r2s1_direct-B3 relaunch, 1.82 min, `nvidia_h200`). Both
  cross-confirmed via `sacct -j <id> --format=...,AllocTRES` before
  writing. JSON re-validated parseable after the write.
- **`r2s2_stacked-B3` job-name-collision watch item (reviewer finding
  R1), unchanged**: guard job 66267441 renamed itself to the panel
  job's name (`r2-r2s2_stacked-B3-s0`) mid-run — confirmed in the
  card's own orchestrator note. Both this walk's ledger entries and all
  queue checks matched by explicit job ID, never by name, per that
  finding.
- **Queue fully drained this walk**: 0 live/pending `r2-*` SLURM jobs
  (down from 1 RUNNING at walk 25). All in-flight work is now at the
  analysis-agent stage (initial-analyzer / mechanism-analyzer), not the
  SLURM stage.
- **`r2s3_lf_train_signal` stream CLOSED (walk 15, unchanged)** — a
  legitimate registered trigger-non-fire close, NOT an abandonment.
  `STREAM_ABANDON_CAP` (=3) never applied. `state/streams/` correctly
  remains nonexistent.
- **Round-level instrument-defect pattern (carried forward, 7 independent
  confirmations, unchanged this run)**: see prior walks'
  `state/maintainer_report.md` entries for full detail — worth folding
  into the round-report action item once the round closes.
- **`r2s1_direct-B3`'s `stage_blend_decoder` zero-field item — remains
  ADJUDICATED, defect ruled OUT** (unchanged from several walks ago). No
  further action needed.
- **Analyzer caveat (r2s1_direct-B1, from code-review)**, carried
  forward: D3 certificate's aleatoric-floor estimate is window-sensitive
  — `ext__helmholtz_2d` reads 1.200 at the recipe window, worse than
  the zero predictor; must not be reported as a ceiling.
- **Analyzer caveat (r2s2_stacked-B1, from code-review + register turn)**,
  preserved for the round report: `ifc_poisson`'s rung ladder is UNPAIRED
  — confirmed independently by r2s3 and r2s4-B2 (cross-stream
  benchmark-integrity item).
- **Analyzer caveat (r2s3_lf_train_signal-B1, from code-review)**,
  carried forward: shared-max-abs-rungs scaler confound (C1, card-locked
  design) and epoch-vs-step mismatch (C2); r2s3-B2 shipped the repair.
- **Analyzer caveat (r2s2_stacked-B3, from code-review, carried
  forward)**: pfc's pre-flight-instrument conflict directionally biases
  F1/F2/F3 toward confirming the card's hypothesis — re-check any "≥2 of
  4 decidable" verdict with pfc dropped once part 6/7 land (mechanism
  turn 1 now in flight).
- **Analyzer caveat (r2s3_lf_train_signal-B4, superseded walk 15,
  unchanged)**: folded into the completed part 6/7 register.
- **Gates**: G1-r2 PASS, G2-r2 PASS, G3-r2 PASS (all 2026-07-31,
  `state/gates.md`) — round cleared for stream launch. Re-read and
  confirmed unchanged this run.
- No reopen candidates on any of the 14 cards. No `blocked.md` file
  exists. **No abandoned streams** — none qualify. `state/streams/`
  directory still does not exist.
- Repo hygiene, final check: `git status --short experiment_cards/` at
  this run's close shows 3 modified files (`r2s1_direct/B3.json`,
  `r2s2_stacked/B3.json`, `r2s4_diag/B4.json`) — all confirmed as
  legitimate in-flight writes by the experiment-debugger /
  initial-analyzer / mechanism-analyzer subagents, not this maintainer
  walk. Only `index.md`, `state/maintainer_report.md`, and
  `state/timing_ledger.json` written this run.
