# MFFP Autoresearch Round 2 — Dashboard (updated 2026-08-02T07:11:12Z)

**Twenty-eighth maintainer walk since the operator halt/resume cycle —
eighth walk of the resumed session.**
Halt landed 2026-08-01T01:31:54Z (commit `10d4e4c`), first resume landed
2026-08-01 ~08:1x PDT (commit `b80e622`). A second session restart
happened ~2026-08-01T20:45 PDT (crons re-created: orchestrator pulse
`aa4dcb66`, maintainer `2c7fed88`, auto-sync `a45bd18b`; commit
`818faef8`). Walks 21-24 were light/no-delta walks under a queue-stall
throttle; walk 25 recorded real deltas for the first time since walk 15;
walks 26-27 recorded the r2s1_direct-B3 debug/relaunch and successive
analysis-agent progress. **This walk (28) is the busiest since the
queue unstuck**: `r2s4_diag-B4` closed its register turn and reached
`complete` status (tools promoted, part 7 written, stream flagged
CLOSE CANDIDATE), an orchestrator ad-hoc measurement landed applying
`r2s4_diag-B4`'s new `gain_channel_ladder.py` tool to `r2s3_lf_train_signal-B3`'s
shipped ifc arms, `r2s1_direct-B3` closed mechanism-analyzer turn 1
(landed prior to this walk) and turn 2 (landed **during** this walk's
read window — caught mid-flight), and `r2s2_stacked-B3` remains at
mechanism-analyzer turn 2 complete with turn 3 in flight. SLURM queue
is fully empty of `r2-*` jobs — all movement this walk is at the
analysis-agent / register-turn layer.

## Real deltas this walk (see `state/maintainer_report.md` RUN block for full detail)

- **`r2s4_diag-B4` REGISTER TURN COMPLETE — card closed.** Status
  advanced `analyzing` → **`complete`** (confirmed `reanalysis_progress`
  = `registered`, part 7 `7_gap_and_future` populated with
  `open_question` / `next_direction` / `cross_stream_notes` /
  `promoted_tools`). Two new tools promoted to `tools/` and confirmed
  present with fresh `tools/index.md` entries: `hf_row_shapley_value.py`
  (exact closed-form Shapley over the exhaustive `C(m,n)` HF-row-subset
  dump) and `gain_channel_ladder.py` (per-sample-scale / amplitude-vs-
  structure channel ladder across a sweep axis). Card's own
  `panel_geomean_skill` (7.9412, single-dataset ifc_poisson scope) is
  explicitly flagged in part 5 as NOT comparable to the 6-dataset stream
  panel anchor — carried into the Completed-cards table below with that
  scope caveat, not compared to 19.8178/23.0636.
  `state/r2s4_diag/current_stage.txt` now reads **CLOSE CANDIDATE**:
  the stream ran 4 batches against a ~3-batch program budget; per the
  file's own text, B5 must not open without operator/end-of-round
  adjudication. This is **not** an `STREAM_ABANDON_CAP` trip (all 4
  batches are `complete`, none `skipped`/`blocked`) — flagged separately
  below as a budget-overrun close candidate.
- **Orchestrator ad-hoc measurement archived**:
  `state/adhoc_measurements/r2s4B4_register_followup_r2s3B3_ifc_gain_channel_ladder.json`
  — a follow-up application of the newly-promoted `gain_channel_ladder.py`
  to `r2s3_lf_train_signal-B3`'s shipped `A0_nolf`/`A1_lf_cov` ifc arms.
  Result: `A1_lf_cov` (LF-at-train arm) shows `frac_removed_global`
  0.468 vs `A0_nolf`'s −0.006 (globally miscaled), and per-sample-gain
  headroom collapses from 0.661 (`A0_nolf`) to 0.646 (`A1_lf_cov`) —
  i.e. the LF arm's remaining error is dominantly a **global scale**
  defect (flag `GLOBALLY_MISCALED`), consistent with B4's part-7
  `open_question` about which channel r2s3-B3's ifc win actually moved.
  Purely archival — no card touched.
- **`r2s1_direct-B3` mechanism-analyzer turn 2 landed during this
  walk's read window.** Card's `reanalysis_progress` advanced
  `turn_1` → **`turn_2`** (caught via a live `git diff` against the
  committed tree: single-line change, uncommitted at read time — the
  freshest write of any card this walk, ~1.5 min old). `6_analysis` and
  `7_gap_and_future` remain `null` — turn 2's write-back has landed the
  progress marker but not yet the analysis body; status unchanged
  `analyzing`, part 5 unchanged (`panel_geomean_skill` 18.7500, single
  seed 0 — best single-seed panel of the round, anchor candidate;
  `falsification_verdict: falsified`). `job_ids` and `debug_notes`
  (1 entry, the walk-26 POD-rank fix) unchanged.
- **`r2s2_stacked-B3` mechanism-analyzer remains at turn 2 complete,
  turn 3 in flight** (no new landed delta this walk — `reanalysis_progress`
  still `turn_2`, `6_analysis`/`7_gap_and_future` still `null`, matching
  walk 27's read). Part 5 unchanged (`panel_geomean_skill` 20.0315 vs
  stream anchor 23.0636 — falsified in the positive direction). Status
  unchanged `analyzing`.
- **SLURM**: `squeue -u $USER` shows **0 live `r2-*` jobs** (only the
  unrelated long-running interactive `bash` job `66279812`, now
  ~3:51:22 elapsed). `sacct` (2-day window) shows the same **22 `r2-*`
  job records** as walks 26-27 (21 COMPLETED + 1 FAILED `66262741`,
  superseded by relaunch `66285051`) — no new jobs, none vanished.
- **Timing ledger**: unchanged at **21 entries** — already current (all
  21 COMPLETED jobs from the 22-record `sacct` set present by job ID;
  the 1 FAILED job correctly excluded). Re-validated parseable JSON;
  no upsert due this walk.
- No `STREAM_ABANDON_CAP` trip (r2s4_diag's close is a budget-overrun
  candidate, not an abandonment — see Flags). No anchor deltas (all
  4 `state/anchors/*.json` byte-identical, mtimes predate this run by
  >40h). No gate changes (G1-r2/G2-r2/G3-r2 all still PASS 2026-07-31).
  No transcripts to file (`state/transcripts/inbox/` still does not
  exist).

## Streams

| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r2s1_direct | 23.0636 (best_floor_panel_geomean) | 3 | r2s1_direct-B1 **complete**; r2s1_direct-B2 **complete**; r2s1_direct-B3 **analyzing** (part 5 populated, geomean 18.7500, falsified; parts 6/7 null) | Seed-0 debugged + relaunched (walk 26): `66262741` FAILED → fix `568522c` → `66285051` **COMPLETED**. Mechanism-analyzer turn 1 landed (walk 27), **turn 2 landed this walk** (progress marker only; body still null) | **0 live SLURM** | **`reanalysis_progress` turn_1→turn_2 this walk** |
| r2s2_stacked | 23.0636 (best_floor_panel_geomean) | 3 | r2s2_stacked-B1 **complete**; r2s2_stacked-B2 **complete**; r2s2_stacked-B3 **analyzing** (part 5 populated, geomean 20.0315, falsified positive; parts 6/7 null) | Guard `66267441` + panel `66267438` both COMPLETED. Mechanism-analyzer turn 2 complete (closed-form scalar-law reframing, walk 27), turn 3 in flight | **0 live SLURM** | No change this walk — turn 3 still pending |
| r2s3_lf_train_signal | 23.0636 (best_floor_panel_geomean) | 4 | r2s3_lf_train_signal-B1..B4 **all complete** | **CLOSED (registered close, walk 15)**, unchanged. New this walk: B3's shipped ifc arms were re-measured by an orchestrator ad-hoc `gain_channel_ladder.py` follow-up (archival only, card untouched) | **0 live SLURM** | Ad-hoc cross-card measurement archived (no card write) |
| r2s4_diag | **19.8178** (certified_3seed_panel_geomean, CI95 [19.385, 20.527]) | 4 | r2s4_diag-B1..B4 **all complete** | **B4 register turn complete this walk** — status `complete`, part 7 written, 2 tools promoted (`hf_row_shapley_value.py`, `gain_channel_ladder.py`). Stream flagged **CLOSE CANDIDATE** (4 batches vs ~3-batch program budget) pending operator/end-of-round adjudication | **0 live SLURM** | **B4 closed this walk; stream CLOSE CANDIDATE flag raised** |

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
drained since walk 26. All in-flight work is at the analysis-agent /
register-turn stage. `sacct`'s 2-day window shows 22 `r2-*` job records
total (21 COMPLETED + 1 FAILED `66262741`, superseded by relaunch
`66285051`). All states cross-confirmed by both `squeue` (empty of
`r2-*`) and `sacct`.

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
| **r2s4_diag-B4** *(NEW this walk)* | diagnostic (mechanism/register) | 7.9412 — **single-dataset (ifc_poisson) scope only, not comparable to the 6-dataset panel anchor** (per card's own `scope_warning`) | n/a (diagnostic); mechanism register complete across 3 turns, part 7 written; H5/H4/H2/provenance findings folded into `cross_stream_notes` | `tools/hf_row_shapley_value.py`, `tools/gain_channel_ladder.py` |

`r2s1_direct-B3` has a COMPLETED SLURM job (relaunch `66285051`) and a
mechanism-analyzer progress marker at `turn_2` (landed this walk), but
remains card-level `analyzing` (parts 6/7 null, awaiting the turn-2
analysis body). `r2s2_stacked-B3` is `analyzing` (part 5 populated,
mechanism turn 2 complete, turn 3 pending) — neither listed above
until it closes.

## Flags

- **`r2s4_diag` stream — CLOSE CANDIDATE (new this walk)**: B4 closed
  its register turn at 4 batches against a ~3-batch program budget.
  `state/r2s4_diag/current_stage.txt`: "do not open B5 without
  operator/end-of-round decision." This is a budget-overrun close
  candidate, distinct from `STREAM_ABANDON_CAP` (never tripped — all 4
  batches `complete`). Surfacing for the orchestrator/operator, not
  actioned by this read-only maintainer walk.
- **`r2s1_direct-B3` mechanism-analyzer turn 2 landed mid-walk (new)**:
  `reanalysis_progress` `turn_1`→`turn_2`, caught via live `git diff`
  (uncommitted at read time). `6_analysis`/`7_gap_and_future` still
  `null` — the analysis body has not yet followed the progress marker.
  Worth a re-check next walk to confirm the body lands and the card
  either closes or advances to turn 3.
- **`r2s1_direct-B3` debug loop resolved (attempt 1/5, class ALGO,
  walk 26), unchanged**: fix commit `568522c` (self-validating POD rank
  truncation in `pod_basis`); relaunch `66285051` COMPLETED clean.
- **Timing ledger unchanged this walk**: 21 entries, already current
  (walk 26's two upserts cover every COMPLETED job in the 22-record
  `sacct` set; the 1 FAILED job `66262741` correctly excluded).
  Re-validated parseable JSON.
- **`r2s2_stacked-B3` job-name-collision watch item (reviewer finding
  R1), unchanged**: guard job 66267441 renamed itself to the panel
  job's name (`r2-r2s2_stacked-B3-s0`) mid-run — confirmed in the
  card's own orchestrator note. All queue/ledger checks matched by
  explicit job ID, never by name.
- **Queue remains fully drained**: 0 live/pending `r2-*` SLURM jobs
  (unchanged from walks 26-27). All in-flight work is at the
  analysis-agent / register-turn stage.
- **`r2s3_lf_train_signal` stream CLOSED (walk 15, unchanged)** — a
  legitimate registered trigger-non-fire close, NOT an abandonment.
  `STREAM_ABANDON_CAP` (=3) never applied. `state/streams/` correctly
  remains nonexistent. New this walk: B3's shipped ifc arms were
  re-measured by an orchestrator ad-hoc follow-up using B4's newly
  promoted `gain_channel_ladder.py` (see Real deltas above) — result
  flags `A1_lf_cov` as `GLOBALLY_MISCALED`, archival only, no card
  reopened.
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
  turn 2 complete, turn 3 in flight).
- **Analyzer caveat (r2s4_diag-B4, NEW this walk, from part 7's
  `cross_stream_notes`)**: (1) H5 ACTIONABLE — ifc's live route to
  criterion 1 is a per-sample GAIN channel (65.4% of n=5 error
  oracle-removable per-sample vs 0.19% globally); any capacity/
  architecture-only proposal on ifc is pre-priced as the wrong lever.
  (2) H4 ACTIONABLE DO-NOT — coverage/representativeness statistics
  select the WRONG HF rows on this design (Spearman −0.60); binds any
  active-learning/row-reweighting/typicality gate. (3) H2 INTERPRETIVE
  — the round's certified ifc `min_claimable_effect` (0.9377) sits at
  only the 48.4th percentile of its own 31-design sampling
  distribution; no current verdict flips, but claims within ~1.7x MCE
  should not lean on MCE alone. (4) PROVENANCE — cross-card numeric
  agreement to ~1e-6 between B1 and B4 reflects coincident seed
  integers on a 5-row/1-batch-per-epoch design, not independent
  replication.
- **Analyzer caveat (r2s3_lf_train_signal-B4, superseded walk 15,
  unchanged)**: folded into the completed part 6/7 register.
- **Gates**: G1-r2 PASS, G2-r2 PASS, G3-r2 PASS (all 2026-07-31,
  `state/gates.md`) — round cleared for stream launch. Re-read and
  confirmed unchanged this run.
- No reopen candidates on any of the 14 cards. No `blocked.md` file
  exists. **No abandoned streams** — `STREAM_ABANDON_CAP` never trips;
  `r2s4_diag`'s close is a budget-overrun candidate, not a cap trip.
  `state/streams/` directory still does not exist.
- Repo hygiene, final check: `git status --short experiment_cards/` at
  this run's close shows 1 modified file (`r2s1_direct/B3.json`, the
  turn-2 progress-marker write caught mid-flight this walk) — not
  touched by this maintainer walk. Only `index.md` and
  `state/maintainer_report.md` written this run (timing ledger required
  no change).
