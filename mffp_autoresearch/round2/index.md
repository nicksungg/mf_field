# MFFP Autoresearch Round 2 — Dashboard (updated 2026-08-01T21:20:00Z)

**Fourteenth maintainer walk since the operator halt/resume cycle.**
Halt landed 2026-08-01T01:31:54Z (commit `10d4e4c`), resume landed
2026-08-01 ~08:1x PDT (commit `b80e622`).

**Headline 1 — `r2s4_diag-B4` re-reviewed SUGGEST and SUBMITTED, new this
walk.** `status` moved `built` → `running`. The focused re-review
(scope `dc0d7ae..61cf430`) landed verdict **`reviewed_suggest`** at
2026-08-01T21:03:50Z: all 3 required fixes CLOSED (parents-only
`_repo_root`, fatal anatomy-probe deliverable assert, no-override
re-verify evidence — `diagnostic.json` 63,697 bytes at the real
`${OUTPUTS_ROOT}/round2/r2s4_diag/B4/eval/`), both SUGGEST items CLOSED,
blast radius PASS (5 files, no locked field touched), and the
orchestrator-made commit's provenance explicitly adjudicated ACCEPTABLE
(zero uncommitted diff, every hunk maps 1:1 to the required-fix list,
code_hash reproduces exactly). Pre-submit housekeeping then archived the
CONTRACT-TIER re-verification artifacts (2-epoch `diagnostic.json`,
`ledger_contamination_audit_s0.json`, `band_retention_probe_s0.json`, a
298 MB `preds_test_ifc_poisson_e2_s0.npz`, 8 files total) to
`${OUTPUTS_ROOT}/round2/r2s4_diag/B4/eval_contract_tier_archive/` —
confirmed on disk this walk, and the real `.../B4/eval/` dir is now
empty, clean for the actual 200-epoch scored run to land there. Seed 0
was then submitted: job **66269660** (`r2-r2s4_diag-B4-s0`), confirmed
**PENDING** via both `squeue` and `sacct` at this walk's check.

**Headline 2 — `r2s3_lf_train_signal-B4` mechanism-analyzer completed
turn 2 and dispatched turn 3, all within this walk's window.** Turn 1
(informationally-empty-rows mechanism) finished with `scratchpad/
reanalysis_turn_1_results.md`: H-deg (structural degeneracy of a
5-row-fit calibration head) is the binding mechanism, H-cap is refuted
(ifc's identical head class reaches held-out R² 0.927 with real labels),
H-N is a real secondary limit (≈10 labelled rows needed to recover most
of ifc's amplitude channel — triple the stream's HF budget). Turn 1 also
priced the ch/hz "ceiling absorption" numbers as **clip artifact**: mean
clip fraction at n_fit=40 is 0.975–1.000 on ch/hz (vs 0.000 on fk, 0.012
on ifc) — the fitted head is the constant shrink `c=0.5` for
essentially every sample, not a condition-keyed law. **Turn 2**
(ifc-vs-ch anatomy + clip-free ceiling re-read) then confirmed and
sharpened this: `E_raw` splits into `E_struct` (amplitude-calibrated
remainder) + `E_amp` per dataset — ch's effect is **99–125× mce
structural** (median cos-with-truth 0.0003–0.0385 on the no-LF arm vs
0.962–0.964 with LF: the no-LF prediction is near-**orthogonal** to
truth, not mis-scaled), while hz's effect is **0.04–0.13× mce, i.e.
vanishes** once both arms are amplitude-calibrated (both hz arms are
near-orthogonal AND collapsed — "a contest between two failed
predictors"). Turn 2's clip-free ceiling re-read found the card's
`ridge_cond_loo_test` ceiling number is **bit-identical to a
zero-information constant gain of 0.5** on ch·d0, ch·d1, ac·d0, and all
3 hz draws (clip fraction 1.00 — the "law" never evaluates); only ifc
(LOO R² 0.937, clip fraction 0.01) and fk (R² 0.21–0.61, clip fraction
0.00) carry genuine condition-keyed content. Consequence for the B5
trigger: ch's 26.9% ceiling absorption (< 50% threshold) is now shown to
be **entirely the clip** (true LOO R² 0.077–0.334, actively harmful on
d2 at −0.626) — the trigger's non-firing is **more robust** than part
5's own reading. Turn 2 also self-corrected a turn-1 inference error
inline (ch/hz's tiny optimal scale is the `cos≈0` factor, not an
amplitude overshoot — flagged and corrected within the same mechanism
run, not a build defect). **Turn 3 dispatched and running now** (PID
2366199, started 2026-08-01T21:19Z, ~1 min elapsed at this walk's
close, well within its 1200s budget) testing H2: whether ac's effect is
a *tail* phenomenon (heavy tail of catastrophically broken no-LF samples)
rather than a level shift, to adjudicate {ifc, ch, ac} claimable-set
membership dataset-by-dataset. `reanalysis_progress` field on the card
now reads `turn_2`; `state/r2s3_lf_train_signal/current_stage.txt` is
**stale** — still reads "Mechanism turn 1 dispatched 2026-08-01", not
updated for turn 1's completion, turn 2's completion, or turn 3's
dispatch. Flagged for orchestrator pickup, not corrected (read-only for
state files owned by other agents' workflow steps — this maintainer
only writes its own designated state files).

Two previously-tracked GPU jobs remain **PENDING**, unchanged since walk
11: 66262741 (`r2s1_direct-B3`, seed 0), 66267438 / 66267441
(`r2s2_stacked-B3` panel / guard) — all Priority-queued,
`Elapsed=00:00:00`, verified by both `squeue` and `sacct` at this run's
check. Round-root auto-sync tip unchanged at `5ca8b12`
(2026-08-01T21:02:11Z) since before this walk opened — no new auto-sync
commit landed during this walk's window; the two card-status transitions
above (`r2s4_diag-B4` review+submit, `r2s3_lf_train_signal-B4` mechanism
turns) landed directly on the working branch, separate from the
auto-sync mechanism.

## Streams

| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r2s1_direct | 23.0636 (best_floor_panel_geomean) | 3 | r2s1_direct-B1 **complete**; r2s1_direct-B2 **complete**; r2s1_direct-B3 **running** | Unchanged this run. Seed-0 job **66262741 still PENDING** in `squeue`/`sacct` (Priority-queued, `Elapsed=00:00:00`) | **1 live/pending SLURM** (`r2-r2s1_direct-B3-s0`, job 66262741, PENDING) | No change; job still PENDING |
| r2s2_stacked | 23.0636 (best_floor_panel_geomean) | 3 | r2s2_stacked-B1 **complete**; r2s2_stacked-B2 **complete**; r2s2_stacked-B3 **running** | Unchanged this run — still `running`, job_ids `['66267438','66267441']`. Both jobs remain PENDING; job-name-collision watch item still applies once the guard leg starts running | **2 live/pending SLURM** (`r2-r2s2_stacked-B3-s0` 66267438, `r2-r2s2_stacked-B3-guard-s0` 66267441, both PENDING) | No change; both jobs still PENDING |
| r2s3_lf_train_signal | 23.0636 (best_floor_panel_geomean) | 4 | r2s3_lf_train_signal-B1..B3 **complete**; r2s3_lf_train_signal-B4 **analyzing — CONFIRMED (round's first confirmed card)** | `status` unchanged (`analyzing`, part 5 landed walk 12). Mechanism turn 1 + turn 2 **completed this walk** (H-deg/H-cap/H-N established; ch's effect confirmed structural/orthogonal not amplitude, 99-125x mce; hz's effect vanishes under amplitude calibration, 0.04-0.13x mce; ch/ac/hz ceiling numbers shown to be clip artifacts, only ifc/fk condition-keyed). Turn 3 **dispatched and running** (H2: is ac's effect a tail phenomenon) | **0 live SLURM** (job 66268786 COMPLETED prior to walk 12; ledger unchanged at 17 entries) | **2 mechanism turns completed + turn 3 dispatched this run** — largest single-walk analytical delta of the round so far |
| r2s4_diag | **19.8178** (certified_3seed_panel_geomean, CI95 [19.385, 20.527]) | 4 | r2s4_diag-B1..B3 **complete**; r2s4_diag-B4 **running** | `status` moved `built` → `running` this walk. Focused re-review verdict **`reviewed_suggest`** (2026-08-01T21:03:50Z) — all required fixes + SUGGEST items CLOSED, commit provenance adjudicated ACCEPTABLE. Contract-tier outputs archived to `eval_contract_tier_archive/`, deliverable path clean. Seed 0 **submitted** | **1 live/pending SLURM** (`r2-r2s4_diag-B4-s0`, job 66269660, PENDING) | **status transition this run** (`built`→`running`, review+submit); watch for job completion + initial-analyzer next walk |

**Anchor note**: r2s4_diag remains the only stream with a *certified* anchor
(`certified_3seed_panel_geomean`, 19.8178) — r2s1_direct, r2s2_stacked,
r2s3_lf_train_signal remain on the launch-time `best_floor_panel_geomean`
anchor (23.0636, `certified_utc` 2026-07-31T14:20:17Z, unchanged). No anchor
deltas this run — all 4 `state/anchors/*.json` files' mtimes predate this
run's entire window. All anchors rendered verbatim from
`state/anchors/*.json`.

## Running / pending jobs

| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| 66262741 | r2s1_direct-B3 (seed 0) | PENDING | 0:00 | (Priority) |
| 66267438 | r2s2_stacked-B3 (seed 0, panel) | PENDING | 0:00 | (Priority) |
| 66267441 | r2s2_stacked-B3 (seed 0, guard) | PENDING | 0:00 | (Priority) |
| 66269660 | r2s4_diag-B4 (seed 0) | PENDING | 0:00 | (Priority) |

**4 live/pending `r2-*` SLURM jobs** — one new this walk (66269660,
`r2s4_diag-B4-s0`, submitted after the `reviewed_suggest` re-review). All
4 confirmed still PENDING at this run's check by both `squeue` and
`sacct`. `sacct`'s 2-day window otherwise shows the same 17 pre-existing
`r2-*` jobs, all COMPLETED 0:0, identical to the prior ledger set (no new
completions this run).

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

`r2s1_direct-B3` and `r2s2_stacked-B3` are `running` (no part 5 yet) —
not listed here until they close. `r2s3_lf_train_signal-B4` is
`analyzing` — **CONFIRMED at part 5**, mechanism turns 1-2 complete and
turn 3 dispatched this walk, but part 6 (mechanism register) and part 7
(register/close) have not landed yet — not listed in this table until it
closes; see the headline and Streams row above for the full verdict.
`r2s4_diag-B4` is `running` (job 66269660 PENDING) — not listed here.

## Flags

- **The round's first CONFIRMED card, `r2s3_lf_train_signal-B4` —
  mechanism turns 1+2 completed and turn 3 dispatched this walk (the
  round's largest single-walk analytical delta)**. `status: analyzing`
  (unchanged, landed walk 12); part 5 verdict F1∨F2∨F3∨F4 all FALSE;
  achievable gate `{ifc_poisson, sharp__cahn_hilliard,
  sharp__allen_cahn_2d}`; ceiling gate `{sharp__cahn_hilliard}` only;
  `sharp__fisher_kpp_2d` retires. B5 trigger NOT fired (max ceiling
  absorption 26.9% on `ch` vs 50% threshold) → **stream closes on B4**
  per the pre-registered rule in `iteration_1.md`, pending the
  mechanism-analyzer's remaining turn(s) and the register turn.
  **Turn 1** established H-deg (a 5-row-fit calibration head is
  degenerate by construction, `sd(log c)` train ≤2.0e-06 vs test 0.03-6.6)
  as the binding mechanism, refuted H-cap (the same head class reaches
  held-out R² 0.927 on ifc with real labels), and quantified H-N (n≈10
  labelled rows would recover most of ifc's amplitude channel — triple
  the stream's HF budget). Turn 1 also found ch/hz's law-keyed heads are
  clip-saturated at n_fit=40 (mean clip fraction 0.975-1.000) — a fixed
  shrink-to-0.5, not a condition-keyed law — and self-corrected one
  inference (median optimal scale being tiny is the `cos≈0` factor, not
  amplitude overshoot). **Turn 2** confirmed H1 with a refinement: ifc
  is the only dataset with a genuinely condition-learnable amplitude
  channel (LOO R² 0.937, clip fraction 0.01); ch's effect is
  **structural** (99-125× mce after amplitude-calibrating both arms —
  the no-LF arm's prediction is near-orthogonal to truth, median cos
  0.0003-0.0385, vs 0.962-0.964 with LF); hz's effect **vanishes** under
  the same calibration (0.04-0.13× mce — both arms are near-orthogonal
  AND collapsed, "a contest between two failed predictors"). Turn 2's
  clip-free ceiling re-read showed ch/ac/hz's `ridge_cond_loo_test`
  ceiling numbers are **bit-identical to a zero-information constant
  gain of 0.5** on 6 of the 9 non-ifc/fk legs (clip fraction 1.00) — so
  ch's 26.9% B5-trigger reading is entirely the clip (true LOO R²
  0.077-0.334, harmful on d2 at −0.626), making the trigger's
  non-firing **more robust**, not less. **Turn 3 dispatched and
  running** at this walk's close (PID 2366199, started
  2026-08-01T21:19Z, ~1 min elapsed, within its 1200s budget) testing
  H2: whether ac's effect is a tail phenomenon vs a level shift, to
  adjudicate {ifc, ch, ac} membership dataset-by-dataset. **Staleness
  flagged, not corrected**: `state/r2s3_lf_train_signal/current_stage.txt`
  still reads "Mechanism turn 1 dispatched 2026-08-01" — has not been
  refreshed for turn 1's completion, turn 2's completion, or turn 3's
  dispatch; card's own `reanalysis_progress` field correctly reads
  `turn_2` as of this walk (will need a further bump once turn 3 lands).
  Orchestrator pickup item for next cycle.
- **`r2s4_diag-B4` re-reviewed SUGGEST and submitted, new this walk**:
  `status` `built` → `running`. Focused re-review (attempt 2, scope
  `dc0d7ae..61cf430`) landed **`reviewed_suggest`** at
  2026-08-01T21:03:50Z: all 3 required fixes CLOSED (verified LIVE
  against the re-verification artifact, not just by reading the diff —
  the equivalence-bound cross-check's recorded `noise_floor_json` path
  is the main-tree path, no stray `<worktree>/mffp_autoresearch_outputs`
  directory exists), both SUGGEST items CLOSED, `bash -n` clean on all 3
  scripts, blast radius PASS (5 files, no locked card field touched),
  and the orchestrator-made commit's provenance explicitly adjudicated
  ACCEPTABLE by three independent checks (zero uncommitted diff post-fix,
  every hunk maps 1:1 to the attempt-1 required-fix list, and the
  committed contract-smoke artifact's `code_hash` reproduces exactly
  when recomputed against the shipped files). The reviewer's remaining
  SUGGEST (pre-submit housekeeping, not a code change) was then executed:
  the CONTRACT-TIER re-verification artifacts (8 files, incl. the
  2-epoch `diagnostic.json` and a 298 MB preds npz) were archived to
  `${OUTPUTS_ROOT}/round2/r2s4_diag/B4/eval_contract_tier_archive/` —
  confirmed on disk this walk — leaving the real `.../B4/eval/`
  directory clean (0 files) for the scored 200-epoch run. Seed 0 was
  then submitted: job **66269660** (`r2-r2s4_diag-B4-s0`), confirmed
  **PENDING** via both `squeue` and `sacct` at this walk's check.
  Analyzer obligations recorded verbatim on the card's review_notes
  (per `state/r2s4_diag/current_stage.txt`, correctly refreshed this
  cycle): `epochs==200` assert, `O_UNCLASSIFIED`/`prereg_gap` recorded
  verbatim, watch for the symmetric second-lobe non-monotone reading.
  **Watch item for next walk**: job 66269660's completion, then the
  initial-analyzer.
- **`r2s2_stacked-B3` job-name-collision watch item, unchanged**: panel
  job 66267438 (`r2-r2s2_stacked-B3-s0`) and guard job 66267441
  (`r2-r2s2_stacked-B3-guard-s0`) remain distinctly named in `squeue`
  because both are still PENDING — the collision (reviewer finding R1,
  not code-fixed, tracked by job ID per the orchestrator's documented
  workaround) will only manifest once the guard leg starts RUNNING and
  its in-script `scontrol update` fires. Re-verify by job ID, not name,
  once either job transitions state.
- **Job 66262741 (r2s1_direct-B3, seed 0)**: confirmed via both `squeue`
  and `sacct` this run — still **PENDING**, Priority-queued, unchanged
  since the prior run's close.
- **Jobs 66267438 / 66267441 (r2s2_stacked-B3, seed 0 panel + guard)**:
  confirmed via both `squeue` and `sacct` this run — both still
  **PENDING**, Priority-queued, unchanged since the prior run's close.
- **Job 66269660 (r2s4_diag-B4, seed 0)**: new this walk — confirmed via
  both `squeue` and `sacct`, **PENDING**, Priority-queued.
- **Round-level instrument-defect pattern (carried forward, 7 independent
  confirmations; the `r2s4_diag-B4` code-review finding remains a
  distinct SLURM/path-resolution defect class, not folded into this
  count since it was caught pre-submission by review rather than in a
  scored run)**: `r2s1_direct`'s post-hoc-blend-stage class (adjudicated
  non-defective); `r2s2_stacked-B2`'s statistic mis-specification;
  `r2s4_diag-B3` turn-2's mis-specified `advantage_reachable`, turn-3's
  self-corrected probe-ordering bug; `r2s3_lf_train_signal-B3`'s resolved
  knife-edge; `r2s4_diag-B3` register-turn's ceiling/contamination/
  row-count triad and its foreign-data `stage_blend_decoder` zero-field
  catch — worth folding into the round-report action item once the round
  closes. Related, tracked as its own item, not folded into this count:
  `r2s3_lf_train_signal-B4` turn 1's self-corrected inference (tiny
  optimal scale on ch/hz being the `cos≈0` factor, not amplitude
  overshoot) — an in-flight self-correction within one mechanism-analyzer
  run, not an independent confirmation event.
- **`r2s1_direct-B3`'s `stage_blend_decoder` zero-field item — remains
  ADJUDICATED, defect ruled OUT** (unchanged from several walks ago). No
  further action needed.
- **Timing ledger**: unchanged this run (17 entries, re-validated as
  parseable JSON, 2-key top-level structure `_note`/`entries`). No
  upsert due — all 4 live jobs (66262741/66267438/66267441/66269660)
  are PENDING (confirmed via both `squeue` and `sacct`), no new
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
- **Analyzer caveat (r2s4_diag-B4, from code-review, addressed and
  committed in `61cf430`, re-review confirmed CLOSED this walk)**:
  `recipe.env R2S4B4_NOISE_FLOOR_JSON` was echoed into `resolved_recipe`
  but never read by the family; the fix adds a fatal cross-check
  assertion comparing the recipe's equivalence bound against the value
  the named file actually contains — verified live against the
  re-verification artifact by the re-reviewer (see Flags above).
- **Analyzer caveat (r2s3_lf_train_signal-B4, from the initial-analyzer,
  carried forward)**: card part 4's `E_ceil` column silently used `E_free`
  for the `fk`/`hz` rows instead of the class-wide `E_ceil` — the
  mechanism-analyzer must not quote that column verbatim for those two
  datasets (turn 1/2 have not quoted it). Also: `a0_split_ensemble` (15
  HF rows, 3x compute) drives the `pfc` row on all 3 draws and `ac`'s d0
  reading — label it wherever it drives a claim (turn 2 explicitly
  labelled it). Minor: card part 3 says "33 legs", the recipe and run
  both use 32.
- **Timestamp-ahead-of-clock / clock-skew anomaly class (carried forward,
  no new distinct occurrence flagged this run)**: prior runs flagged
  `review_notes[0].utc` fields reading ahead of the actual check time, and
  an informal "2026-08-01 ~0x:xx PDT" wall-clock labelling convention in
  `orchestrator_flow.md`. Not a new distinct class, no scored quantity
  affected; this report uses filesystem-relative epoch deltas throughout,
  never the flow log's lexical labels.
- **Gates**: G1-r2 PASS, G2-r2 PASS, G3-r2 PASS (all 2026-07-31,
  `state/gates.md`) — round cleared for stream launch. Unchanged this run.
- **Round-1 top-3 seed confirms**: NOT this maintainer's scope (round-1
  jobs visible in `squeue` as `r1-*` historically; none currently queued) —
  separate round, separate report.
- No reopen candidates on any of the 14 cards. No `blocked.md` file exists
  (no stream has ever blocked). **No abandoned streams** — none qualify
  (all 4 streams show clean complete/running/analyzing progressions with
  no skip/block history anywhere). `state/streams/` directory still does
  not exist — consistent with no abandonments ever being needed.
- Repo hygiene, final check: `git status --short experiment_cards/` on
  the round root shows `r2s3_lf_train_signal/batch_4/B4.json` and
  `r2s4_diag/batch_4/B4.json` **M** at this run's close (both
  orchestrator-owned — the mechanism-turn progress bump and the
  `built`→`running` review+submit transition, respectively, neither a
  maintainer edit) plus `state/r2s4_diag/current_stage.txt` **M**
  (orchestrator-owned refresh, matching the new `running` status). This
  maintainer's own writes this run: `index.md`, `state/maintainer_report.md`.
  No changes were made to `state/timing_ledger.json` (no upsert due).
  Round-root auto-sync tip unchanged at `5ca8b12` (2026-08-01T21:02:11Z)
  since before this walk's open — no new auto-sync commit; both card
  transitions above landed directly on the working branch, separate from
  the auto-sync mechanism.
