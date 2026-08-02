# MFFP Autoresearch Round 2 — Dashboard (updated 2026-08-02T14:41:30Z)

**Twenty-ninth maintainer walk since the operator halt/resume cycle —
first walk after the THIRD session restart.**
Halt landed 2026-08-01T01:31:54Z (commit `10d4e4c`), first resume landed
2026-08-01 ~08:1x PDT (commit `b80e622`), second restart landed
~2026-08-01T20:45 PDT.
This walk picks up after a **third session restart, ~2026-08-02T14:2x
UTC** (per `state/orchestrator_flow.md`'s tail entry, cross-checked
against this walk's own reads — see below).
The gap since the prior maintainer walk's `RUN END` (`2026-08-02T06:37:00Z`)
is **~7h57m**, consistent with the session being down for most of that
window rather than a normal ~20-30 min cron cadence; this walk is the
first to run since the resume.

## Real deltas this walk (see `state/maintainer_report.md` RUN block for full detail)

- **Session restart (third resume) confirmed independently.**
  `state/orchestrator_flow.md` (read-only to this maintainer) carries a
  freshly appended, still-uncommitted entry timestamped
  `2026-08-02 ~14:2x UTC`: prior session died after dispatching both
  turn-3 mechanism-analyzers (~08:0x/08:2x UTC); both cards were
  verified still at `reanalysis_progress=turn_2` with parts 6/7 null and
  0 live `r2-*` SLURM jobs at resume time; crons re-created session-only
  (pulse `707a5d1f` @10min, maintainer `838b5b42` @20min, auto-sync
  `e526548f` @30min, 7-day auto-expiry) — **this maintainer could not
  independently verify the cron IDs** (`crontab -l` is PAM-denied for
  this user on this cluster), so that detail is reported as claimed by
  the orchestrator, not directly confirmed; the fact that this walk is
  running at all is itself the practical confirmation the maintainer
  cron is alive again. Mechanism-analyzer turn 3 + register re-dispatched
  for BOTH `r2s1_direct-B3` and `r2s2_stacked-B3` (agents told to
  distrust stale turn-3 partials from the killed prior-session agent).
- **`r2s2_stacked-B3` mechanism-analyzer turn 3 LANDED DURING THIS
  WALK'S READ WINDOW.** Caught live via `git diff --stat` (73
  insertions / 34 deletions, uncommitted at read time, file mtime
  ~83 seconds before this walk's final re-check). `reanalysis_progress`
  advanced `turn_2` → **`turn_3`**; `6_analysis` now populated
  (`findings`/`interpretation`/`falsification_postmortem`/`surprises`
  keys present, no `turns` sub-object this time — differs from
  `r2s4_diag`'s structure). Part 7 still `null` — register turn not yet
  landed. Headline (turn 3, high confidence): **the class's entire
  headroom is exactly one scalar deep** — once the per-sample DC
  (spatial-mean) law is granted via a 9-feature quadratic ridge on the
  condition vector (96.6% of the level oracle, 3.72x the trained CNN's
  whole gain on `allen_cahn`, 5/5 fold seeds), 40-211x each dataset's
  certified MCE of oracle value remains unaddressed and none of it is
  reachable from the condition vector alone. Confirms/extends turn 2's
  finding that the headline A1-A2 win is a partial gradient-trained
  solve of a closed-form scalar regression, and turn 1's band-0/DC-
  energy-share framing (`pfc could_not_fire` reading superseded: a
  closed-form scalar law wins 6.03x pfc's certified mce, 152.7x what the
  degenerate A2 arm delivered). Part 5 unchanged (`panel_geomean_skill`
  20.0315 vs stream anchor 23.0636, falsified positive direction).
  Status unchanged `analyzing`.
- **`r2s1_direct-B3` remains at `reanalysis_progress=turn_2` at the
  card level** (mtime `2026-08-02T07:12:18Z`, unchanged since walk 27) —
  **but is actively computing turn 3 in the worktree scratchpad as of
  this walk's read**: `worktrees/r2s1_direct/B3/scratchpad/` shows
  `reanalysis_turn_3.py` through `reanalysis_turn_3c_report.json`, the
  freshest (`reanalysis_turn_3c_console.txt`) timestamped
  `2026-08-02T14:36:13Z` — essentially concurrent with this walk's read.
  Card write-back has not yet landed (`6_analysis`/`7_gap_and_future`
  still `null`); worth checking next walk.
- **SLURM: no change since walk 27/28.** `squeue -u $USER` shows **0
  live `r2-*` jobs** (only the unrelated long-running interactive
  `bash` job `66302920`, ~36 min elapsed — a different PID than the
  `66279812` seen in walks 26-28, consistent with a session restart
  bouncing the interactive shell too). `sacct` (2-day window) shows the
  same **22 `r2-*` job records** (21 COMPLETED + 1 FAILED `66262741`,
  superseded by relaunch `66285051`) — no new jobs, none vanished.
- **Timing ledger**: unchanged at **21 entries** — already current
  (all 21 COMPLETED jobs present by job ID; the 1 FAILED job correctly
  excluded). Re-validated parseable JSON; no upsert due this walk.
- No `STREAM_ABANDON_CAP` trip. No anchor deltas (all 4
  `state/anchors/*.json` byte-identical, mtimes still `2026-07-31`).
  No gate changes (G1-r2/G2-r2/G3-r2 all still PASS 2026-07-31). No new
  `state/adhoc_measurements/` entries (still just the 1 file from walk
  28, mtime `2026-08-01T23:55`). No transcripts to file
  (`state/transcripts/inbox/` still does not exist).

## Streams

| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r2s1_direct | 23.0636 (best_floor_panel_geomean) | 3 | r2s1_direct-B1 **complete**; r2s1_direct-B2 **complete**; r2s1_direct-B3 **analyzing** (part 5 populated, geomean 18.7500, falsified; parts 6/7 null) | Seed-0 debugged + relaunched (walk 26): `66262741` FAILED → fix `568522c` → `66285051` **COMPLETED**. Mechanism-analyzer turn 1 (walk 27) + turn 2 (walk 28) landed; **turn 3 actively computing in scratchpad this walk, not yet written back to card** | **0 live SLURM** | Scratchpad turn-3 activity ~14:36Z this walk; card unchanged since walk 27 |
| r2s2_stacked | 23.0636 (best_floor_panel_geomean) | 3 | r2s2_stacked-B1 **complete**; r2s2_stacked-B2 **complete**; r2s2_stacked-B3 **analyzing** (part 5 populated, geomean 20.0315, falsified positive; **part 6 now populated, turn 3**; part 7 null) | Guard `66267441` + panel `66267438` both COMPLETED. Mechanism-analyzer turn 3 **landed this walk** (headline: headroom is exactly one scalar deep past the condition-driven DC/level law); register turn pending | **0 live SLURM** | **`reanalysis_progress` turn_2→turn_3 this walk, caught live** |
| r2s3_lf_train_signal | 23.0636 (best_floor_panel_geomean) | 4 | r2s3_lf_train_signal-B1..B4 **all complete** | **CLOSED (registered close, walk 15)**, unchanged | **0 live SLURM** | No change this walk |
| r2s4_diag | **19.8178** (certified_3seed_panel_geomean, CI95 [19.385, 20.527]) | 4 | r2s4_diag-B1..B4 **all complete** | **complete**, unchanged since walk 28 register close. Stream still flagged **CLOSE CANDIDATE** (4 batches vs ~3-batch program budget) pending operator/end-of-round adjudication | **0 live SLURM** | No change this walk |

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

**0 live/pending `r2-*` SLURM jobs** — the queue has remained fully
drained since walk 26, unaffected by the session restart. All in-flight
work is at the analysis-agent / register-turn stage (non-SLURM
background processes writing to worktree scratchpads). `sacct`'s 2-day
window shows 22 `r2-*` job records total (21 COMPLETED + 1 FAILED
`66262741`, superseded by relaunch `66285051`). All states cross-
confirmed by both `squeue` (empty of `r2-*`) and `sacct`.

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
| r2s4_diag-B4 | diagnostic (mechanism/register) | 7.9412 — **single-dataset (ifc_poisson) scope only, not comparable to the 6-dataset panel anchor** (per card's own `scope_warning`) | n/a (diagnostic); mechanism register complete across 3 turns, part 7 written; H5/H4/H2/provenance findings folded into `cross_stream_notes` | `tools/hf_row_shapley_value.py`, `tools/gain_channel_ladder.py` |

`r2s1_direct-B3` has a COMPLETED SLURM job (relaunch `66285051`) and is
mid-computation on mechanism-analyzer turn 3 (scratchpad only, not yet
on the card) — remains card-level `analyzing` (parts 6/7 null).
`r2s2_stacked-B3` is `analyzing` with mechanism turn 3 now landed on
the card (part 6 populated) but part 7 (register) still pending —
neither listed above until they close.

## Flags

- **`r2s4_diag` stream — CLOSE CANDIDATE, unchanged since walk 28**: B4
  closed its register turn at 4 batches against a ~3-batch program
  budget. `state/r2s4_diag/current_stage.txt`: "do not open B5 without
  operator/end-of-round decision." Budget-overrun close candidate, not
  a `STREAM_ABANDON_CAP` trip. Surfacing for the orchestrator/operator,
  not actioned by this read-only maintainer walk.
- **Third session restart (~2026-08-02T14:2x UTC), new this walk**:
  ~7h57m gap since the prior maintainer `RUN END`. Turn-3 mechanism-
  analyzers re-dispatched for `r2s1_direct-B3` and `r2s2_stacked-B3`
  after the second-session's turn-3 agents were killed mid-flight;
  `r2s2_stacked-B3`'s scratchpad explicitly shows a `_v2` set of turn-3
  artifacts superseding stale `00:0x-00:1x` (local) partials from the
  killed agent — this maintainer treated only the `_v2`-derived,
  card-level write-back (which landed during this walk) as authoritative,
  per the resume note's own instruction; the stale partials were not
  used for any ledger or dashboard content. Cron re-creation
  (`707a5d1f`/`838b5b42`/`e526548f`) is reported by the orchestrator and
  could not be independently confirmed (`crontab -l` PAM-denied for this
  user); this walk's own successful execution is the practical evidence
  the maintainer cron is alive.
- **`r2s2_stacked-B3` mechanism-analyzer turn 3 landed mid-walk (new)**:
  `reanalysis_progress` `turn_2`→`turn_3`, `6_analysis` now populated
  (caught via live `git diff`, uncommitted at read time). Part 7 still
  `null` — register turn pending, worth a re-check next walk.
- **`r2s1_direct-B3` turn 3 in active computation, not yet landed
  (new)**: worktree scratchpad shows work as recent as
  `2026-08-02T14:36:13Z` (~5 min before this walk's close); card still
  reads `turn_2`. Re-check next walk.
- **`r2s1_direct-B3` debug loop resolved (attempt 1/5, class ALGO,
  walk 26), unchanged**: fix commit `568522c` (self-validating POD rank
  truncation in `pod_basis`); relaunch `66285051` COMPLETED clean.
- **Timing ledger unchanged this walk**: 21 entries, already current
  (all COMPLETED jobs in the 22-record `sacct` set present; the 1
  FAILED job `66262741` correctly excluded). Re-validated parseable
  JSON.
- **`r2s2_stacked-B3` job-name-collision watch item (reviewer finding
  R1), unchanged**: guard job 66267441 renamed itself to the panel
  job's name (`r2-r2s2_stacked-B3-s0`) mid-run — all queue/ledger checks
  matched by explicit job ID, never by name.
- **Queue remains fully drained**: 0 live/pending `r2-*` SLURM jobs
  (unchanged from walks 26-28, unaffected by the session restart). All
  in-flight work is at the analysis-agent / register-turn stage.
- **`r2s3_lf_train_signal` stream CLOSED (walk 15, unchanged)** — a
  legitimate registered trigger-non-fire close, NOT an abandonment.
  `STREAM_ABANDON_CAP` (=3) never applied. `state/streams/` correctly
  remains nonexistent.
- **Operator item, unchanged**: "ladder.py fix proposal awaiting Eloise
  review -> mentor sign-off" (per `state/orchestrator_flow.md`'s resume
  note) — outside this maintainer's scope; surfaced for visibility only.
- **Round-level instrument-defect pattern (carried forward, 7
  independent confirmations, unchanged this run)**: see prior walks'
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
- **Analyzer caveat (r2s2_stacked-B3, from code-review, updated this
  walk)**: pfc's pre-flight-instrument conflict directionally biases
  F1/F2/F3 toward confirming the card's hypothesis — turn 3's finding
  (a closed-form scalar law wins 6.03x pfc's certified mce, 5/5 fold
  seeds) is read by this maintainer as superseding, not resolving, the
  original bias concern; still worth a pfc-dropped re-check once part 7
  lands.
- **Analyzer caveat (r2s4_diag-B4, from part 7's `cross_stream_notes`,
  unchanged)**: (1) H5 ACTIONABLE — ifc's live route to criterion 1 is
  a per-sample GAIN channel (65.4% of n=5 error oracle-removable
  per-sample vs 0.19% globally); any capacity/architecture-only proposal
  on ifc is pre-priced as the wrong lever. (2) H4 ACTIONABLE DO-NOT —
  coverage/representativeness statistics select the WRONG HF rows on
  this design (Spearman −0.60); binds any active-learning/row-
  reweighting/typicality gate. (3) H2 INTERPRETIVE — the round's
  certified ifc `min_claimable_effect` (0.9377) sits at only the 48.4th
  percentile of its own 31-design sampling distribution; no current
  verdict flips, but claims within ~1.7x MCE should not lean on MCE
  alone. (4) PROVENANCE — cross-card numeric agreement to ~1e-6 between
  B1 and B4 reflects coincident seed integers on a 5-row/1-batch-per-
  epoch design, not independent replication.
- **Analyzer caveat (r2s3_lf_train_signal-B4, superseded walk 15,
  unchanged)**: folded into the completed part 6/7 register.
- **Gates**: G1-r2 PASS, G2-r2 PASS, G3-r2 PASS (all 2026-07-31,
  `state/gates.md`) — round cleared for stream launch. Re-read and
  confirmed unchanged this run.
- No reopen candidates on any of the 14 cards. No `blocked.md` file
  exists. **No abandoned streams** — `STREAM_ABANDON_CAP` never trips;
  `r2s4_diag`'s close is a budget-overrun candidate, not a cap trip.
  `state/streams/` directory still does not exist.
- Repo hygiene, final check: `git status --short .` at this run's close
  (round-root scope) shows 2 modified files — `experiment_cards/
  r2s2_stacked/batch_3/B3.json` (turn-3 write-back caught mid-flight
  this walk, not touched by this maintainer) and `state/
  orchestrator_flow.md` (resume-note append, not owned by this
  maintainer). Only `index.md` and `state/maintainer_report.md` written
  this run (timing ledger required no change).
