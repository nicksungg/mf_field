# MFFP Autoresearch Round 2 — Dashboard (updated 2026-08-02T15:03:00Z)

**Thirtieth maintainer walk since the operator halt/resume cycle —
second walk after the THIRD session restart.**
Halt landed 2026-08-01T01:31:54Z (commit `10d4e4c`), first resume landed
2026-08-01 ~08:1x PDT (commit `b80e622`), second restart landed
~2026-08-01T20:45 PDT, third restart landed ~2026-08-02T14:2x UTC (per
`state/orchestrator_flow.md`).
The gap since the prior maintainer walk's `RUN END` (`2026-08-02T14:44:32Z`)
is **~15 min**, back to normal cron cadence.

## Milestone this walk

**All 14 cards across all 4 streams are now `complete`** — for the first
time this round.
Both `r2s1_direct-B3` and `r2s2_stacked-B3` advanced through mechanism-analyzer
turn 3 and the register turn since the prior walk, landing `status: complete`,
`reanalysis_progress: registered`, part 7 populated.
This maintainer caught both already landed at this walk's first card read
(card mtimes `2026-08-02T14:54:51Z` and `2026-08-02T14:54:00Z`, i.e. within
~10 minutes of the prior walk's `RUN END` at `14:44:32Z`).

## Real deltas this walk (see `state/maintainer_report.md` RUN block for full detail)

- **`r2s1_direct-B3` register turn COMPLETE — card CLOSED.**
  `panel_geomean_skill` 18.749954 (single seed 0) — falsified via L2
  (turn 1: the calibration-fold Bates-Granger prelude clause was
  **unpassable by construction**, a unit mismatch between a between-seed
  100-row mce and a 40-row within-fold sampling question). Mechanism
  analysis across 3 turns (16 interpretation items, M1-M16): the headline
  "10-param head beats a 15.85M-param decoder by 75x mce on
  `allen_cahn`" is a **coordinate verdict, not a capacity verdict** (M5);
  headroom is coefficient-estimation, not basis-width, and survives a
  deployable relaxation test (M11); the per-direction OOF R² statistic
  used to call coefficients "condition-unidentifiable" actually measures
  **reach of the map family**, not identifiability — on `cahn_hilliard`
  a decoder recovers cross-coefficient structure the statistic scored as
  noise (OOF R² up to 0.94) (M12/M13). New hypothesis M15 (moderate
  confidence, n=1 caveat): this is a **condition-dimension effect** — the
  one panel cell with usable cross-coefficient structure is also the
  only one with a high-dimensional condition vector (19 scalars vs 2-3
  elsewhere). Part 7 next_direction: B4 should ship the propagation-aware
  two-stage closed-form head as the scored arm at 1+2 seeds and add a
  cond_dim discriminator. **2 tools promoted**:
  `tools/coefficient_factorisation_audit.py`, `tools/head_subspace_surgery.py`
  (both confirmed present on disk).
- **`r2s2_stacked-B3` register turn COMPLETE — card CLOSED.**
  `panel_geomean_skill` 20.031536 (single seed 0), falsified positive vs
  the 23.0636 anchor. `falsification_postmortem`: the pre-registered
  zero-gradient-ceiling hypothesis was **right about the architecture,
  wrong about the arithmetic** — the trained stage's value is a
  per-sample DC recalibration (a scalar regression on the condition
  vector), not a field correction, because the LSI stage structurally
  carries only a single shared DC gain across samples. Surprises: the
  condition→level law is exact to machine precision on `cahn_hilliard`
  (1-R² = 3.93e-15) yet worth almost nothing there (0.28x mce, HF DC
  energy share 0.0045); the `pfc` cell booked as a degenerate
  `could_not_fire` resolves to a closed-form channel worth 6.03x its
  certified mce; **all 64 POD coefficients on all 4 datasets have
  negative held-out R² from the condition vector** (a cleaner null than
  the probe was built to detect). Part 7 open question: after granting
  the closed-form level law, is there any legitimate move left for a
  condition-only class, or should the correct output of this stream be a
  **certified impossibility statement** — the residual carries 40-211x
  each dataset's certified mce with condition-only reachability negative
  at every rung on 4/4 decidable datasets, while the paired LF field
  carries that same residual almost perfectly (median per-sample
  fluctuation cosine ≥ 0.997 on 4/4). next_direction explicitly forbids
  another condition-only field corrector; supports (1) a cheap
  zero-gradient level arm reported as dataset-level not panel-level, and
  (2) a distributional/calibrated-uncertainty arm as the only
  construction with real headroom — with a caveat to price whether the
  round's rel-L2 geomean metric can reward it at all. **2 tools
  promoted**: `tools/condition_scalar_channel_ladder.py`,
  `tools/granted_channel_residual_ladder.py` (both confirmed present on
  disk).
- **SLURM: no change.** `squeue -u $USER` shows **0 live `r2-*` jobs**
  (only unrelated interactive `bash` job `66302920`). `sacct` (2-day
  window) shows the same **22 `r2-*` job records** as walks 26-29 (21
  COMPLETED + 1 FAILED `66262741`, superseded by relaunch `66285051`) —
  no new jobs, none vanished. Consistent with the task brief's note that
  the queue has been empty of `r2-*` jobs.
- **Timing ledger**: unchanged at **21 entries** — already current (all
  21 COMPLETED jobs present by job ID; the 1 FAILED job correctly
  excluded). Re-validated parseable JSON; no upsert due this walk
  (register/analysis-stage deltas are not SLURM jobs).
- No `STREAM_ABANDON_CAP` trip. No anchor deltas (all 4
  `state/anchors/*.json` byte-identical, mtimes still `2026-07-31`/`10:03`).
  No gate changes (G1-r2/G2-r2/G3-r2 all still PASS 2026-07-31). No new
  `state/adhoc_measurements/` entries. No transcripts to file
  (`state/transcripts/inbox/` still does not exist).

## Streams

| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r2s1_direct | 23.0636 (best_floor_panel_geomean) | 3 | r2s1_direct-B1 **complete**; r2s1_direct-B2 **complete**; r2s1_direct-B3 **complete** (registered; geomean 18.7500, falsified via L2-unpassable-by-construction; 16-item M1-M16 mechanism register, part 7 written) | All 3 batches complete. No stream close/abandon marker written; whether a B4 opens is an orchestrator/operator decision outside this maintainer's scope | **0 live SLURM** | Register turn landed this walk (card mtime `14:54:51Z`, ~10 min before this walk started) |
| r2s2_stacked | 23.0636 (best_floor_panel_geomean) | 3 | r2s2_stacked-B1 **complete**; r2s2_stacked-B2 **complete**; r2s2_stacked-B3 **complete** (registered; geomean 20.0315, falsified positive; 15-finding mechanism register, part 7 written) | All 3 batches complete. No stream close/abandon marker written; whether a B4 opens is an orchestrator/operator decision outside this maintainer's scope | **0 live SLURM** | Register turn landed this walk (card mtime `14:54:00Z`, ~10 min before this walk started) |
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
drained since walk 26. With both `r2s1_direct-B3` and `r2s2_stacked-B3`
now closed, there is no in-flight analysis-agent work on any card either
— all 14 cards are `complete`. `sacct`'s 2-day window shows 22 `r2-*`
job records total (21 COMPLETED + 1 FAILED `66262741`, superseded by
relaunch `66285051`). All states cross-confirmed by both `squeue` (empty
of `r2-*`) and `sacct`.

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
| r2s1_direct-B3 | model | 18.749954 (single seed 0) | **falsified via L2**: calibration-fold Bates-Granger prelude clause **unpassable by construction** (unit mismatch, tolerance 0.026-0.107 sigma of the 40-sample estimator it audits); mechanism register (M1-M16, 3 turns) reframes the headline decoder-vs-head comparison as coordinate, not capacity | `tools/coefficient_factorisation_audit.py`, `tools/head_subspace_surgery.py` |
| r2s2_stacked-B3 | model | 20.031536 (single seed 0) | **falsified positive** vs anchor 23.0636; pre-registered zero-gradient-ceiling hypothesis right on architecture, wrong on arithmetic (value = per-sample DC recalibration, not field correction); condition-only reachability negative at every rung on 4/4 decidable datasets post-level-law | `tools/condition_scalar_channel_ladder.py`, `tools/granted_channel_residual_ladder.py` |

**All 14 cards are now closed/complete** — no cards remain in
`running`/`analyzing` state as of this walk.

## Flags

- **MILESTONE, new this walk**: all 14 cards across all 4 streams are
  now `status: complete`. `r2s1_direct-B3` and `r2s2_stacked-B3` both
  completed their register turns since the prior walk (`RUN END
  2026-08-02T14:44:32Z`), landing within ~10 minutes of that prior
  walk's close. No `running`/`analyzing` cards remain anywhere in the
  round. Whether `r2s1_direct` or `r2s2_stacked` open a B4 is an
  orchestrator/operator decision — this read-only maintainer surfaces
  the milestone but does not act on it.
- **`r2s4_diag` stream — CLOSE CANDIDATE, unchanged since walk 28**: B4
  closed its register turn at 4 batches against a ~3-batch program
  budget. `state/r2s4_diag/current_stage.txt`: "do not open B5 without
  operator/end-of-round decision." Budget-overrun close candidate, not
  a `STREAM_ABANDON_CAP` trip. Surfacing for the orchestrator/operator,
  not actioned by this read-only maintainer walk.
- **`r2s1_direct-B3` register turn landed (new)**: `reanalysis_progress`
  `turn_3`→`registered`, `7_gap_and_future` now populated. 2 tools
  promoted (`coefficient_factorisation_audit.py`, `head_subspace_surgery.py`),
  both confirmed on disk. Open question flagged for a future card:
  whether the `cahn_hilliard` cross-coefficient-factorisation finding
  (M13/M15) is a condition-dimension effect or a single-cell accident
  (n=1 caveat, explicit in part 7).
- **`r2s2_stacked-B3` register turn landed (new)**: `reanalysis_progress`
  `turn_3`→`registered`, `7_gap_and_future` now populated. 2 tools
  promoted (`condition_scalar_channel_ladder.py`,
  `granted_channel_residual_ladder.py`), both confirmed on disk. Part 7
  raises a stream-level open question — whether the correct next output
  for a condition-only class on this panel is a certified impossibility
  statement rather than another corrector proposal; next_direction
  explicitly forbids another condition-only field corrector.
- **Third session restart (~2026-08-02T14:2x UTC), carried from walk 29**:
  crons re-created session-only (pulse `707a5d1f` @10min, maintainer
  `838b5b42` @20min, auto-sync `e526548f` @30min, 7-day auto-expiry) —
  reported by the orchestrator, could not be independently confirmed
  (`crontab -l` PAM-denied for this user); this walk's own successful
  execution (back to the normal ~15-20 min cadence) is further practical
  evidence the maintainer cron is healthy again.
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
  (unchanged from walks 26-29). No in-flight analysis-agent work remains
  either — all 14 cards are `complete`.
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
- **Analyzer caveat (r2s2_stacked-B3, from code-review, updated at the
  register turn)**: pfc's pre-flight-instrument conflict directionally
  biased F1/F2/F3 toward confirming the card's hypothesis — the register
  turn's finding (a closed-form scalar law wins 6.03x pfc's certified
  mce, 5/5 fold seeds) supersedes rather than resolves the original bias
  concern; folded into the closed card's part 6/7, no further re-check
  needed.
- **Analyzer caveat (r2s1_direct-B3, from the register turn, new)**: the
  card's L2 falsification clause is a UNIT-MISMATCH design defect
  (between-seed mce reused as a within-fold sampling tolerance,
  0.026-0.107 sigma resolving power) — flagged as a recipe repair for
  any future card exercising the same calibration-fold pattern, not just
  an r2s1-local finding; also flags fit-set-asymmetric blend bases
  (calibration fitted on 320 rows, test-side floors on the full 400) as
  a second cross-card recipe defect.
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
- Repo hygiene, final check: `git status --short experiment_cards/` at
  this run's close shows 2 modified files — `r2s1_direct/batch_3/B3.json`
  and `r2s2_stacked/batch_3/B3.json` (both register-turn write-backs
  described above, made by the register-turn subagents, not touched by
  this maintainer). `git status --short .` (round-root scope)
  additionally shows `state/orchestrator_flow.md` (not owned by this
  maintainer, stale tail not yet reflecting this walk's register
  completions) and `tools/index.md` + 4 new untracked `tools/*.py` files
  (register-turn tool promotions, not owned by this maintainer). Only
  `index.md` and `state/maintainer_report.md` written this run (timing
  ledger required no change).
