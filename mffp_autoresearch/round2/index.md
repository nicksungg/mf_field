# MFFP Autoresearch Round 2 — Dashboard (updated 2026-08-01T21:54:00Z)

**Sixteenth maintainer walk since the operator halt/resume cycle.**
Halt landed 2026-08-01T01:31:54Z (commit `10d4e4c`), resume landed
2026-08-01 ~08:1x PDT (commit `b80e622`).

**No changes since walk 15.**
The round is now fully compute-bound: all 14 cards are exactly where
walk 15 left them (`r2s3_lf_train_signal-B1..B4` all `complete`, the
stream formally CLOSED; `r2s1_direct-B1`/`B2` and `r2s2_stacked-B1`/`B2`
`complete`; `r2s1_direct-B3` and `r2s2_stacked-B3` `running` with no
part 5 yet; `r2s4_diag-B1..B3` `complete`, `r2s4_diag-B4` `running`).
`r2s3_lf_train_signal`'s close remains a legitimate registered
trigger-non-fire close, not an abandonment — full mechanism detail is
preserved in walk 15's `state/maintainer_report.md` entry and is not
repeated in full here.
No new analysis agents are in flight; every next stage for the three
open streams triggers on a SLURM job completion, and none of the four
tracked jobs has transitioned since walk 15.

## Streams

| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r2s1_direct | 23.0636 (best_floor_panel_geomean) | 3 | r2s1_direct-B1 **complete**; r2s1_direct-B2 **complete**; r2s1_direct-B3 **running** | Unchanged since walk 15. Seed-0 job **66262741 still PENDING** in `squeue`/`sacct` (Priority-queued, `Elapsed=00:00:00`), queue wait **~4.1 h** (submitted 2026-08-01T10:47:27 PDT) | **1 live/pending SLURM** (`r2-r2s1_direct-B3-s0`, job 66262741, PENDING) | No change; job still PENDING |
| r2s2_stacked | 23.0636 (best_floor_panel_geomean) | 3 | r2s2_stacked-B1 **complete**; r2s2_stacked-B2 **complete**; r2s2_stacked-B3 **running** | Unchanged since walk 15 — still `running`, job_ids `['66267438','66267441']`. Both jobs remain PENDING, queue wait **~2.3 h** each (submitted 2026-08-01T12:37:40 PDT); job-name-collision watch item still applies once the guard leg starts running | **2 live/pending SLURM** (`r2-r2s2_stacked-B3-s0` 66267438, `r2-r2s2_stacked-B3-guard-s0` 66267441, both PENDING) | No change; both jobs still PENDING |
| r2s3_lf_train_signal | 23.0636 (best_floor_panel_geomean) | 4 | r2s3_lf_train_signal-B1..B4 **all complete** | **CLOSED (registered close, walk 15)**, unchanged this walk. Formal part-7 close: no B5, graded criterion-1 legacy ch=A/ifc=B/ac=C, fk/pfc/hz retired. Not an abandonment — `STREAM_ABANDON_CAP` never applied (all 4 batches complete, no skip/block history) | **0 live SLURM** (job 66268786 COMPLETED 2026-08-01T13:10:49; already in ledger) | No change since walk 15's close |
| r2s4_diag | **19.8178** (certified_3seed_panel_geomean, CI95 [19.385, 20.527]) | 4 | r2s4_diag-B1..B3 **complete**; r2s4_diag-B4 **running** | Unchanged since walk 15. Seed 0 job 66269660 confirmed still **PENDING**, queue wait **~0.8 h** (submitted 2026-08-01T14:05:45 PDT) | **1 live/pending SLURM** (`r2-r2s4_diag-B4-s0`, job 66269660, PENDING) | No change; job still PENDING |

**Anchor note**: r2s4_diag remains the only stream with a *certified* anchor
(`certified_3seed_panel_geomean`, 19.8178) — r2s1_direct, r2s2_stacked, and
the closed r2s3_lf_train_signal remain on the launch-time
`best_floor_panel_geomean` anchor (23.0636, `certified_utc`
2026-07-31T14:20:17Z, unchanged). No anchor deltas this run — all 4
`state/anchors/*.json` files' mtimes (2026-07-31, one at 2026-07-31T10:03
for r2s4_diag) predate this run's entire window; content re-read this
run and confirmed byte-identical to all prior runs' recorded values.
All anchors rendered verbatim from `state/anchors/*.json`.

## Running / pending jobs

| Job | Card | State | Elapsed | Queue wait (submit → now) | Node/Reason |
|---|---|---|---|---|---|
| 66262741 | r2s1_direct-B3 (seed 0) | PENDING | 0:00 | ~4.12 h (submit 2026-08-01T10:47:27 PDT) | (Priority) |
| 66267438 | r2s2_stacked-B3 (seed 0, panel) | PENDING | 0:00 | ~2.28 h (submit 2026-08-01T12:37:40 PDT) | (Priority) |
| 66267441 | r2s2_stacked-B3 (seed 0, guard) | PENDING | 0:00 | ~2.28 h (submit 2026-08-01T12:37:40 PDT) | (Priority) |
| 66269660 | r2s4_diag-B4 (seed 0) | PENDING | 0:00 | ~0.81 h (submit 2026-08-01T14:05:45 PDT) | (Priority) |

**4 live/pending `r2-*` SLURM jobs** — unchanged from walks 14/15, all 4
confirmed still PENDING at this run's check by both `squeue` and `sacct`.
Queue waits computed from `scontrol show job`'s `SubmitTime` against the
current wall clock (cluster confirmed America/Los_Angeles PDT via
`timedatectl`; epoch-delta arithmetic used throughout, never lexical
HH:MM comparison). `sacct`'s 2-day window otherwise shows the same 17
pre-existing `r2-*` jobs, all COMPLETED 0:0 (including 66268786,
`r2s3_lf_train_signal-B4-s0`, COMPLETED 2026-08-01T13:10:49, already in
the timing ledger) — no new completions this run.

## Completed cards

| Card | Type | Panel geomean skill (±CI) | Falsification verdict | Tools promoted |
|---|---|---|---|---|
| r2s4_diag-B1 | diagnostic | 19.8178 IQM, CI95 [19.385, 20.527] (3 seeds) | n/a (diagnostic — no falsification clauses); mechanism register complete, part 7 written | 2 tools, both correctly indexed: `tools/conditional_mean_collapse.py`, `tools/condition_predictability_ceiling.py` |
| r2s4_diag-B2 | diagnostic | 19.8829 own single-run 3-seed geomean (T0 primary arm; reproduces B1's certified band, not a re-certification) | **falsified**: the aux-LF-TARGET head is worth nothing at any N_fit in 20-320 on 15/15 dataset×N cells (7.42-101.12x the certified floor's resolving power); explicitly does NOT license the broader "LF doesn't help" claim (input-side + disjoint-supply channels untouched) | **3 tools**: `tools/ladder_pair_alignment_audit.py`, `tools/shrinkage_curve_anatomy.py`, `tools/condition_predictability_ceiling_fast.py` |
| r2s1_direct-B1 | model | 19.6444 (single seed 0, no CI yet) | **falsified in a split reading**: floors clause CONFIRMED (beats best floor on all 6 panel datasets, geomean −14.8% vs anchor) but the implicit architecture clause FALSIFIED — a ~156-parameter closed-form head reaches 19.0553/19.1666, statistically indistinguishable from the 15.9M-parameter shipped arm (0.52x the certified panel min_claimable_effect) | 2 tools, both correctly indexed: `tools/band_gain_counterfactual.py`, `tools/condition_identifiable_rank.py` |
| r2s3_lf_train_signal-B1 | model | 25.3919 (`rung_native`, single seed 0) | **falsified in a split reading**: F1 (primary, architecture) FALSIFIED with a 7.35-skill-unit sign inversion on `ifc_poisson`, traced to a shared-scaler confound; but the motivating INFORMATION claim is CONFIRMED — an architecture-free estimator recovers +3.2317 skill units from the same 170 disjoint LF rows (18.83% of the law's coefficient energy at cos 0.9993). F2 (native vs upsampled) survived; F3 (degeneracy) verdict depends on provisional vs re-certified floor thresholds (both recorded) | 2 tools, both correctly indexed: `tools/affine_ladder_voi.py`, `tools/posthoc_repair_ladder.py` |
| r2s2_stacked-B1 | model | 14.0756 (single seed 0, no CI yet; scored arm `frozen`; ~all margin from the unpaired `ifc_poisson` column) | clean negative with a measured mechanism, not a raw binary: the falsification clause was a conjunction that did **not** fire — conjunct 1 ("improve on `emul_only` by ≥2.0 skill units") **held** (measured improvement 0.0061, 326x below threshold) but conjunct 2 ("beat the NN-in-condition floor") **failed to hold** (beat it by 11.90 skill units, 130x the noise floor). Round-level headline (I8): a stacked intermediate representation is a re-parameterisation of the condition→HF hypothesis class, not a new information channel | 2 tools, both correctly indexed and register-confirmed: `tools/reachable_set_rank_audit.py`, `tools/surrogate_coherence_eligibility.py` |
| r2s3_lf_train_signal-B2 | model | not computed (3-of-6 panel only, informational: `A2_lf_cov_null` 8.8918 vs `A0_nolf` 16.0642 on `ifc_poisson`/`sharp__cahn_hilliard`/`sharp__fisher_kpp_2d`) | **confirmed** (not falsified); `cratered_verdict: proceed_to_seeds_1_2`; 1 guard flag (`heat_local`, 18.86x, reasoned structural not `auto_reject`) | **2 tools**: `tools/design_coverage_audit.py`, `tools/null_family_ceiling_audit.py` (a six-instrument identifiability/coverage family) |
| r2s1_direct-B2 | model | 18.3622 (single seed 0, `provisional-single-seed`, **no falsification weight** per card) | **falsified**: L1 fires (2/5 decidable cells lose to the in-job Wiener-calibrated `ref_decoder_big` by >mce — allen_cahn 6.99x, cahn_hilliard 14.21x); L2 fires (cahn_hilliard gap 4.74x the L2 threshold, stable across 5 fold-resamples, not rescued by any rank in the sweep); L3/L4 do not fire | **2 tools**: `tools/blend_decorrelation_payoff.py` (equal-rho blend counterfactual), `tools/selection_set_vs_window_audit.py` (selection-set-vs-window arity-bug detector) |
| r2s2_stacked-B2 | diagnostic | 19.386837 (single seed 0, `provisional-single-seed`); vs anchor 23.0636 (-3.677, beyond certified mce 1.1419 but not anchor-certifying) | **falsified**: F1 fires (refit LSI corrector beats the promoted rule's training-free ceiling on 3 ladder cells), F2 fires (k=1 beats k=all beyond mce on 3 panel datasets), F3 fires (ladder-B partial coherence clears permutation-null on 5/6 datasets), F4 does not fire. `cratered_verdict: n/a` (diagnostic — no crater rule) | **2 tools**, both correctly indexed, no duplicates: `tools/zero_gradient_stage_ladder.py`, `tools/relative_gain_units_audit.py` — together they **retract the B1-promoted `surrogate_coherence_eligibility.py` rule as an eligibility GATE** (centring bug + frozen-vs-refit mismatch + 10-817x unit mispricing), demoting it to a directional-only predictor |
| r2s3_lf_train_signal-B3 | model | 17.114970 (`A1_lf_cov` primary arm, single seed 0) vs anchor 23.0636 (comparison arm `A0_nolf` 32.4663) | **falsified** (F1/F2 knife-edge adjudicated FALSIFIED, robust across 5/7 defensible threshold readings incl. a gain-calibrated split reading M4; only the two readings pricing zero HF-subset-draw variance return CONFIRMED); the round's success-criterion-1 (≥3-dataset claimable with/without-LF-training contrast) is still met on exactly 3 datasets under the operative threshold. `cratered_verdict: cratered` (third limb only — falsification fired decisively; not a crash, not >1.5x anchor) | **2 tools**, both correctly indexed: `tools/effect_threshold_readings.py` (7-reading threshold-adjudication tool; surfaces `mce_over_observed_split_range` as a provenance smell), `tools/map_dispersion_scale_shape.py` (splits inter-prediction dispersion into total vs shape-only; found allen_cahn's 3 LF-trained models sit within 0.41 skill units of each other but 100.5 units apart in function space — "scale, not map") |
| r2s4_diag-B3 | diagnostic | 19.172826 (single seed 0, no own-card CI — 1 seed; in-job 5-fold paired spreads are per-dataset thresholds, not a panel CI) | **falsified** (F3 stands and is hardened by two row-count/capacity controls; F4a fired on the ledger's own contaminated-quantity definition, not on a measurement failure — 0/4 under the corrected teacher-target term; F1 survives on 2 of its 3 needed cells, pfc's cell ruled uninformative by a ceiling argument). Mechanism headline: on 3 of 4 sharp datasets the condition-only arm's per-band error is ~1.00 above the lowest band — it contributes exactly zero energy above the spatial mean — while the LF field reproduces HF to 1e-2 to 1e-16 band relative error, i.e. essentially all panel structure is realisation information carried only by LF. `cratered_verdict: n/a` (diagnostic) | **2 tools**, both correctly indexed: `tools/ledger_contamination_audit.py` (prices whether a paired-arm delta *could* have fired via a triangle-inequality ceiling, and whether it's contaminated by a function-class term vs the true target term), `tools/band_retention_probe.py` (per-band retained-energy/relative-error decomposition; on its first foreign-data run it independently found the `stage_blend_decoder` zero-field arm in r2s1_direct-B3's shipped dumps — since adjudicated as rational selection, see Flags) |
| r2s3_lf_train_signal-B4 | diagnostic (mechanism/register — no new score minted) | n/a — reuses B3's `score_panel` skills throughout; graded criterion-1 legacy in lieu of a single panel number: `sharp__cahn_hilliard`=**A** (113-125x mce), `ifc_poisson`=**B** (1.41x mce), `sharp__allen_cahn_2d`=**C** (26.9x mce, tail-borne); `sharp__fisher_kpp_2d`/`sharp__phase_field_crystal_2d`/`ext__helmholtz_2d` retired on every per-sample reading | S1 (F1∨F2∨F3∨F4) **CONFIRMED false** (part 5, unchanged); part 6 postmortem: F3's non-firing is a **clause inversion** — memorization (fit-row `sd(log c)≤2.0e-06`) is *why* the achievable-control class was vacuous, not a threat the reading survived. Part 7: **formal stream close**, no B5 (trigger did not fire; turn 2 showed the non-fire is more robust than part 5 read it) | **2 tools**, both correctly indexed, no duplicates: `tools/gain_head_feasibility_audit.py` (prices post-hoc gain-head feasibility against 2 zero-information nulls; catches fit-set degeneracy and clip-artifact ceilings), `tools/effect_concentration_audit.py` (per-sample effect concentration/adversarial-trim/amplitude-vs-structure decomposition) — both foreign-data-verified on r2s3-B2/B3 arm pairs |

`r2s1_direct-B3` and `r2s2_stacked-B3` are `running` (no part 5 yet) —
not listed here until they close. `r2s4_diag-B4` is `running` (job
66269660 PENDING) — not listed here.

## Flags

- **Round fully compute-bound, no card-level deltas since walk 15.**
  All 14 cards walked and confirmed unchanged: `r2s1_direct-B3` and
  `r2s2_stacked-B3` remain `running` with no part 5, `r2s4_diag-B4`
  remains `running`, and `r2s3_lf_train_signal` remains formally
  `complete`/CLOSED. The next actionable event for every open stream is
  a SLURM state transition on one of the four tracked jobs.
- **`r2s3_lf_train_signal` stream CLOSED (walk 15, unchanged)** — a
  legitimate registered trigger-non-fire close, NOT an abandonment.
  `STREAM_ABANDON_CAP` (=3) never applied (all 4 batches `complete`, no
  skip/block history anywhere). `state/streams/` correctly remains
  nonexistent. Full mechanism detail (graded criterion-1 legacy
  ch=A/ifc=B/ac=C; the F3-clause-inversion card-design lesson; the new
  standing publication rule to always report a diagnostic alongside its
  zero-information null) is preserved in walk 15's dashboard text and in
  `state/maintainer_report.md`'s `RUN START 2026-08-01T21:34:07Z` entry
  — not repeated in full here to avoid duplicating an unchanged record.
- **`r2s2_stacked-B3` job-name-collision watch item, unchanged**: panel
  job 66267438 (`r2-r2s2_stacked-B3-s0`) and guard job 66267441
  (`r2-r2s2_stacked-B3-guard-s0`) remain distinctly named in `squeue`
  because both are still PENDING — the collision (reviewer finding R1,
  not code-fixed, tracked by job ID per the orchestrator's documented
  workaround) will only manifest once the guard leg starts RUNNING and
  its in-script `scontrol update` fires. Re-verify by job ID, not name,
  once either job transitions state.
- **Job 66262741 (r2s1_direct-B3, seed 0)**: confirmed via both `squeue`
  and `sacct` this run — still **PENDING**, Priority-queued, queue wait
  ~4.12 h (submitted 2026-08-01T10:47:27 PDT), oldest of the 4 tracked
  jobs and the longest queue wait in the round to date.
- **Jobs 66267438 / 66267441 (r2s2_stacked-B3, seed 0 panel + guard)**:
  confirmed via both `squeue` and `sacct` this run — both still
  **PENDING**, Priority-queued, queue wait ~2.28 h each (submitted
  2026-08-01T12:37:40 PDT).
- **Job 66269660 (r2s4_diag-B4, seed 0)**: confirmed via both `squeue`
  and `sacct` this run — still **PENDING**, Priority-queued, queue wait
  ~0.81 h (submitted 2026-08-01T14:05:45 PDT), youngest of the 4.
- **Round-level instrument-defect pattern (carried forward, 7 independent
  confirmations, unchanged this run)**: `r2s1_direct`'s post-hoc-blend-
  stage class (adjudicated non-defective); `r2s2_stacked-B2`'s statistic
  mis-specification; `r2s4_diag-B3` turn-2's mis-specified
  `advantage_reachable`, turn-3's self-corrected probe-ordering bug;
  `r2s3_lf_train_signal-B3`'s resolved knife-edge; `r2s4_diag-B3`
  register-turn's ceiling/contamination/row-count triad and its foreign-
  data `stage_blend_decoder` zero-field catch — worth folding into the
  round-report action item once the round closes. `r2s3_lf_train_signal-
  B4`'s F3-inversion finding remains tracked separately as a card-design
  lesson, not folded into the count.
- **`r2s1_direct-B3`'s `stage_blend_decoder` zero-field item — remains
  ADJUDICATED, defect ruled OUT** (unchanged from several walks ago). No
  further action needed.
- **Timing ledger**: unchanged this run (17 entries, re-validated as
  parseable JSON, 2-key top-level structure `_note`/`entries`). No
  upsert due — all 4 live jobs (66262741/66267438/66267441/66269660)
  remain PENDING (confirmed via both `squeue` and `sacct`), no new
  COMPLETED job appeared in the 2-day `sacct` window this run.
- **Analyzer caveat (r2s1_direct-B1, from code-review)**, carried forward:
  the D3 certificate's aleatoric-floor estimate is window-sensitive — at
  the recipe's window (1000 closest pairs), `ext__helmholtz_2d` reads
  1.200, worse than the zero predictor. Must not be reported as a ceiling
  for helmholtz; `allen_cahn`'s ceiling must be reported as a range
  (0.315-0.471); `pfc`/`fisher_kpp` are window-robust and quotable.
- **Analyzer caveat (r2s2_stacked-B1, from code-review + register turn),
  preserved for the round report**: `ifc_poisson`'s rung ladder is UNPAIRED
  (independent condition draws per rung, min distance 0.08-0.30, never 0) —
  matches r2s3's independent finding, and is also confirmed by r2s4-B2 —
  three independent streams/estimators, a cross-stream benchmark-integrity
  item.
- **Analyzer caveat (r2s3_lf_train_signal-B1, from code-review)**, carried
  forward: the shared-max-abs-rungs scaler makes ifc_poisson's `rung_native`
  stage-1 loss ~42x amplitude-weighted toward rung 8 over HF (confound C1,
  card-locked design, not a build defect); F1 is epoch-matched but not
  step-matched (confound C2). r2s3-B2's card shipped a step-matched,
  per-rung-scaled repair of both confounds this round (now closed).
- **Analyzer caveat (r2s2_stacked-B3, from code-review, carried forward)**:
  pfc's pre-flight-instrument conflict directionally biases F1/F2/F3
  toward confirming the card's hypothesis — re-check any "≥2 of 4
  decidable" verdict with pfc dropped once part 6/7 land.
- **Analyzer caveat (r2s3_lf_train_signal-B4, superseded walk 15,
  unchanged)**: the prior caveat about `E_ceil` silently reusing `E_free`
  for the `fk`/`hz` rows, and the `a0_split_ensemble`-drives-`pfc`/`ac.d0`
  labelling item, are folded into the completed part 6/7 register — both
  are explicitly labelled in the card's own final findings. Card part 3's
  "33 legs" vs the recipe/run's 32 remains a minor, unresolved
  documentation mismatch (no scored quantity affected).
- **Timestamp-ahead-of-clock / clock-skew anomaly class (carried forward,
  no new distinct occurrence flagged this run)**: prior runs flagged
  `review_notes[0].utc` fields reading ahead of the actual check time, and
  an informal "2026-08-01 ~0x:xx PDT" wall-clock labelling convention in
  `orchestrator_flow.md`. Not a new distinct class, no scored quantity
  affected; this report uses filesystem-relative epoch deltas throughout,
  never the flow log's lexical labels.
- **Gates**: G1-r2 PASS, G2-r2 PASS, G3-r2 PASS (all 2026-07-31,
  `state/gates.md`) — round cleared for stream launch. Re-read and
  confirmed unchanged this run.
- **Round-1 top-3 seed confirms**: NOT this maintainer's scope (round-1
  jobs visible in `squeue` as `r1-*` historically; none currently queued) —
  separate round, separate report.
- No reopen candidates on any of the 14 cards. No `blocked.md` file exists
  (no stream has ever blocked). **No abandoned streams** — none qualify
  (all 4 streams show clean complete/running/closed progressions with no
  skip/block history anywhere; `r2s3_lf_train_signal`'s close is a
  legitimate registered trigger-non-fire close, NOT an abandonment —
  `STREAM_ABANDON_CAP` logic never applied). `state/streams/` directory
  still does not exist — consistent with no abandonments ever being
  needed.
- Repo hygiene, final check: `git status --short .` on the round root at
  this run's close shows `experiment_cards/r2s3_lf_train_signal/batch_4/
  B4.json`, `state/r2s3_lf_train_signal/current_stage.txt`, and
  `tools/index.md` (all orchestrator-owned, unchanged carry-forward from
  walk 15's register-turn writes), plus this maintainer's own writes
  `index.md` and `state/maintainer_report.md`. No changes made to
  `state/timing_ledger.json` (no upsert due). Auto-sync tip unchanged at
  `c883467` (2026-08-01T21:31:21Z) since before walk 15's open. No
  maintainer Write touched `experiment_cards/`, `tools/`, or any other-
  agent-owned `state/` file this run.
