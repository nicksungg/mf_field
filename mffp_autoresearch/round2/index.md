# MFFP Autoresearch Round 2 — Dashboard (updated 2026-08-01T18:12:00Z)

**Sixth maintainer walk since the operator halt/resume cycle.**
Halt landed 2026-08-01T01:31:54Z (commit `10d4e4c`), resume landed
2026-08-01 ~08:1x PDT (commit `b80e622`).

**Concurrency note (new this run, see Flags for detail)**: this walk's
single-in-flight check (performed ~17:54:25Z) found a clean completed
`RUN START 17:14:07Z`/`RUN END 17:25:30Z` pair and proceeded.
A second, fully independent maintainer walk (`RUN START 17:34:35Z` /
`RUN END 17:58:30Z`) had, in fact, already been running at that moment and
entirely overlapped this session — its `RUN START` marker had not yet been
physically appended to `state/maintainer_report.md` at the instant this
session read the file (a TOCTOU race, not a rule violation on either side).
That run's walk and this one agree on every fact both observed; this run
picked up from where that one left off rather than re-doing its work.

**Headline this run: `r2s4_diag-B3` CLOSED — 11th card closed round-wide.**
Also this run: `r2s2_stacked-B3`'s builder landed its first family code;
`r2s3_lf_train_signal`'s B4 websearch completed (5/5 + report); and a
**verified potential defect** was found in `r2s1_direct-B3`'s (non-scored)
`stage_blend_decoder` arm — see Flags, first item.

## Streams

| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r2s1_direct | 23.0636 (best_floor_panel_geomean) | 3 | r2s1_direct-B1 **complete**; r2s1_direct-B2 **complete**; r2s1_direct-B3 **running** | Unchanged this run except a new watch-item note. Seed-0 job **66262741 still PENDING** in `squeue` (Priority-queued, has not started running). `state/r2s1_direct/current_stage.txt` gained a **WATCH ITEM** this run (orchestrator-authored, prompted by r2s4-B3's register-turn tool finding): the contract-smoke `ext__helmholtz_2d` dump for arm `stage_blend_decoder` predicts identically zero; flagged for the initial-analyzer to re-check at full (200-epoch) tier once 66262741 lands | **1 live/pending SLURM** (`r2-r2s1_direct-B3-s0`, job 66262741, PENDING) | Watch-item noted; job still PENDING |
| r2s2_stacked | 23.0636 (best_floor_panel_geomean) | 3 *(card exists; `current_batch.txt` still stale at "2")* | r2s2_stacked-B1 **complete**; r2s2_stacked-B2 **complete**; r2s2_stacked-B3 **drafted** | B1/B2 unchanged. **New this run**: the B3 builder landed its first code in the fresh worktree — `models_r2/r2s2_zerograd/` now has 10 modules (`arms.py`, `bands.py`, `floors.py`, `folds.py`, `local_corrector.py`, `lsi_filter.py`, `model.py`, `periodicity.py`, `preflight.py`, `retrieval.py`, `upsample.py`) + a `probes/` package, plus 2 scratchpad preflight JSONs (`preflight_persample_norm_eligibility.json`, `preflight_target_scale_spread.json`) — up from 0 family files at the start of this run. No contract-smoke evidence yet, no `build_commit`, card still `drafted`/`job_ids: []` | **0 live SLURM**; builder actively writing files (mtimes within the last ~2 min of this check, not stalled) | Builder producing family code (new this run) |
| r2s3_lf_train_signal | 23.0636 (best_floor_panel_geomean) | 4 *(`current_batch.txt` still reads "3")* | r2s3_lf_train_signal-B1 **complete**; r2s3_lf_train_signal-B2 **complete**; r2s3_lf_train_signal-B3 **complete** (10th card, closed last run) | Unchanged card-wise this run. **B4 websearch completed this run**: `websearches/r2s3_lf_train_signal/batch_4/` now has all 5 iterations + `report.md` (15 WebSearch calls, 12 curl-fetches since `WebFetch` is disabled in-env — same route-around as r2s2's batch-3 loop). Verdict: direction (a) — a per-sample gain/calibration head — is `preempted-but-MF-composition-open` (DiSOL's optional amplitude regressor, arXiv:2601.09143; post-hoc affine de-shrinkage, arXiv:2508.01341); recommends the **training-free probe first** (`tools/residual_gain_learnability.py` on the shipped B3 dumps, no GPU) before any confirmatory training arm. Direction (b) (no-LF ensemble) rides along as an arm only, never the claim. Direction (c) (claimability-protocol repair) is **preempted — do not card**; cite Bouthillier et al. (arXiv:2103.03098) instead. Awaiting brainstormer | **0 live SLURM**; **0 live local process** (websearcher exited cleanly after landing `report.md`) | B4 websearch complete → awaiting brainstormer |
| r2s4_diag | **19.8178** (certified_3seed_panel_geomean, CI95 [19.385, 20.527]) | 4 *(new this run — B4 websearcher already dispatched)* | r2s4_diag-B1 **complete**; r2s4_diag-B2 **complete**; r2s4_diag-B3 **complete** *(closed this run — 11th card round-wide)* | **CLOSED this run**: `analyzing`/`turn_3` → `complete`/`registered`. Part 7 landed: 2 tools promoted (`tools/ledger_contamination_audit.py`, `tools/band_retention_probe.py`), 4 cross-stream notes (incl. the `stage_blend_decoder` zero-field finding reported to r2s1, not adjudicated by this card). `next_direction` recommends **closing the stream** unless the still-live `ifc_poisson` round-criterion is judged reachable via one further N_hf∈{5,20,50} diagnostic (program.md §12.4's one un-executed mandate) — the brainstormer owns that call. The stream has already acted: batch counter advanced to 4, a **B4 websearcher is live** (`websearches/r2s4_diag/batch_4/summary_so_far.md` landed, no iterations yet). `state/r2s4_diag/current_stage.txt` **still reads stale turn-1 text** — this staleness (first flagged last run) is now carried a second run | **0 live SLURM** (job terminal); **0 live local process** (register turn settled, B4 websearcher just starting) | Closed: `analyzing`→`complete`; batch counter → 4 (B4 websearch live) |

**Anchor note**: r2s4_diag remains the only stream with a *certified* anchor
(`certified_3seed_panel_geomean`, 19.8178) — r2s1_direct, r2s2_stacked,
r2s3_lf_train_signal remain on the launch-time `best_floor_panel_geomean`
anchor (23.0636, `certified_utc` 2026-07-31T14:20:17Z, unchanged). No anchor
deltas this run — all 4 `state/anchors/*.json` files' mtimes predate this
run's entire window. All anchors rendered verbatim from `state/anchors/*.json`.

## Running / pending jobs

| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| 66262741 | r2s1_direct-B3 (seed 0) | PENDING | 0:00 | (Priority) |

**1 live/pending `r2-*` SLURM job** (unchanged from last run — still queued
on Priority, has not started running). `sacct` 2-day window otherwise shows
the same 16 `r2-*` jobs, all COMPLETED 0:0, identical to the timing ledger —
no ledger upsert due (66262741 still PENDING). **0 live non-SLURM agent
processes** at this final check besides the r2s2-B3 builder (actively
writing family code, mtimes within ~2 min) and a just-dispatched r2s4-B3 B4
websearcher (1 file landed so far).

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
| r2s3_lf_train_signal-B3 | model | 17.114970 (`A1_lf_cov` primary arm, single seed 0) vs anchor 23.0636 (comparison arm `A0_nolf` 32.4663) | **falsified** (F1/F2 knife-edge adjudicated FALSIFIED, robust across 5/7 defensible threshold readings incl. a new gain-calibrated split reading M4; only the two readings pricing zero HF-subset-draw variance return CONFIRMED); the round's success-criterion-1 (≥3-dataset claimable with/without-LF-training contrast) is still met on exactly 3 datasets under the operative threshold. `cratered_verdict: cratered` (third limb only — falsification fired decisively; not a crash, not >1.5x anchor) | **2 tools**, both correctly indexed: `tools/effect_threshold_readings.py` (7-reading threshold-adjudication tool; surfaces `mce_over_observed_split_range` as a provenance smell), `tools/map_dispersion_scale_shape.py` (splits inter-prediction dispersion into total vs shape-only; found allen_cahn's 3 LF-trained models sit within 0.41 skill units of each other but 100.5 units apart in function space — "scale, not map") |
| r2s4_diag-B3 | diagnostic | 19.172826 (single seed 0, no own-card CI — 1 seed; in-job 5-fold paired spreads are per-dataset thresholds, not a panel CI) | **falsified** (F3 stands and is hardened by two row-count/capacity controls; F4a fired on the ledger's own contaminated-quantity definition, not on a measurement failure — 0/4 under the corrected teacher-target term; F1 survives on 2 of its 3 needed cells, pfc's cell ruled uninformative by a ceiling argument). Mechanism headline: on 3 of 4 sharp datasets the condition-only arm's per-band error is ~1.00 above the lowest band — it contributes exactly zero energy above the spatial mean — while the LF field reproduces HF to 1e-2 to 1e-16 band relative error, i.e. essentially all panel structure is realisation information carried only by LF. `cratered_verdict: n/a` (diagnostic) | **2 tools**, both correctly indexed: `tools/ledger_contamination_audit.py` (prices whether a paired-arm delta *could* have fired via a triangle-inequality ceiling, and whether it's contaminated by a function-class term vs the true target term), `tools/band_retention_probe.py` (per-band retained-energy/relative-error decomposition; on its first foreign-data run it independently found the `stage_blend_decoder` zero-field arm in r2s1_direct-B3's shipped dumps — see Flags) |

`r2s1_direct-B3` is `running` (job 66262741 PENDING, no part 5 yet) — not
listed here until it closes. `r2s2_stacked-B3` is `drafted` (not built) —
not listed here.

## Flags

- **VERIFIED — potential defect in `r2s1_direct-B3`'s `stage_blend_decoder`
  arm (new this run, independently confirmed by this maintainer against the
  raw artifact, not just the tool's report)**. r2s4-B3's newly-promoted
  `tools/band_retention_probe.py` was run on foreign data (r2s1's shipped
  `ext__helmholtz_2d` dumps) and reported `stage_blend_decoder` predicting
  identically zero. This maintainer independently loaded
  `.../r2s1_direct/B3/eval/preds_test_stage_blend_decoder_ext__helmholtz_2d_s0.npz`
  directly: `pred` array shape `(100, 9216)`, **`max(abs(pred)) == 0.0`
  exactly**. The other 6 sibling arms in the same directory
  (`ref_decoder_big`, `stage_bg_decoder`, `stage_bg_head`,
  `stage_blend_head`, `stage_wiener_decoder`, `stage_wiener_head`) all have
  nonzero predictions — the zero collapse is isolated to this one arm. The
  file's mtime (17:44:57Z) falls inside the orchestrator's gate-discharge
  re-smoke window, so the zero-collapse was already present in the
  original build, not introduced by that re-run. **This is not the card's
  officially scored arm** (`R2S1B3_SCORED_ARM=stagefree_permode_set_head`),
  so job 66262741's headline number is not directly built from it — but the
  recipe wires `stage_blend_decoder` into the Bates-Granger/blend
  combination machinery (`R2S1B3_BG_COMBINE=1`,
  `R2S1B3_BLEND_APPLY_TO=stage_arms_only`), so a silently-zero ingredient
  could still corrupt any blend-weight or combination reading downstream.
  **The orchestrator has already caught and is tracking this**:
  `state/r2s1_direct/current_stage.txt` now carries an explicit WATCH ITEM
  for the initial-analyzer, correctly framed as "plausibly rational at
  2-epoch smoke tier (helmholtz's best floor IS the zero predictor; the
  blend grid includes a zero base) but MUST be re-checked at the full
  200-epoch tier" — this is being treated as an open question to adjudicate
  once job 66262741 lands, not yet a confirmed crash. Flagging this
  explicitly for Eloise per the standing bug-discovery protocol: this
  maintainer has no write access to cards, models, or job control and
  cannot investigate or halt anything further — the orchestrator's plan to
  adjudicate at the initial-analyzer stage is a reasonable next step, but
  it is Eloise's call whether that is sufficient given the round is
  autonomous and job 66262741 is already queued.
- **`r2s4_diag-B3` CLOSED this run — 11th card closed round-wide**:
  mechanism turn 3 (19 findings, landed before this run) plus the register
  turn (part 7, 2 tools) both landed this run. Falsification verdict:
  **falsified** (F3 hardened, F4a resolved as a definitional artifact of
  the ledger not a real instrument failure, F1 survives on its 2
  informative cells). Headline finding: on 3 of 4 sharp datasets the
  condition-only arm contributes *exactly zero* energy above the spatial
  mean — the panel's structure is realisation information the LF field
  alone carries, which the stripped (no-LF-at-test) eval layer makes a
  structural bound on every stream, not a modelling deficiency in this
  card's arm. `next_direction` recommends **closing the stream** unless the
  still-live `ifc_poisson` round-criterion is judged worth one further
  N_hf∈{5,20,50} diagnostic (program.md §12.4's one un-executed mandate) —
  the brainstormer owns that call, and a B4 websearcher is already
  dispatched (`websearches/r2s4_diag/batch_4/summary_so_far.md`) to inform
  it.
- **`r2s2_stacked-B3` builder producing code (new this run)**: 10 family
  modules + a `probes/` package landed in
  `worktrees/r2s2_stacked/B3/models_r2/r2s2_zerograd/` plus 2 scratchpad
  preflight JSONs — up from 0 files at the start of this run. No
  contract-smoke evidence yet, card still `drafted`.
- **`r2s3_lf_train_signal` B4 websearch complete (new this run)**: 5/5
  iterations + `report.md`. Verdict: direction (a) (per-sample gain head)
  `preempted-but-MF-composition-open` — recommends running the
  training-free `tools/residual_gain_learnability.py` probe on the shipped
  B3 dumps *before* carding any confirmatory training arm, since the
  result is informative either way (if the head recovers the channel, the
  round's affirmative LF evidence reduces to output calibration; if not,
  "LF supplies a signal 5 HF rows provably cannot" is the stronger
  statement). Direction (b) (no-LF ensemble) rides along as an arm only.
  Direction (c) (claimability-protocol repair) is **preempted — do not
  card** (cite Bouthillier et al., arXiv:2103.03098, instead). Awaiting
  brainstormer.
- **Concurrency / single-in-flight race (new this run, process note for
  the operator, not a card issue)**: this session's in-flight check
  (`state/maintainer_report.md`, read ~17:54:25Z) found a clean, matched
  `RUN START 17:14:07Z`/`RUN END 17:25:30Z` pair and proceeded correctly per
  the letter of the rule. A second maintainer session had, in fact, already
  begun (`RUN START 17:34:35Z`) and ran to completion (`RUN END
  17:58:30Z`) fully inside this session's window — its `RUN START` marker
  simply had not yet been physically written to the shared report file at
  the moment this session's check read it (~20 min after that other
  session's embedded start-time, well under the 25-minute threshold, so had
  it been visible this session would correctly have no-op'd). No content
  conflict resulted — this run picked up and reported only the deltas that
  landed *after* that run's close, and both walks' findings agree on every
  fact both observed. Worth a look if the cron schedule allows two
  maintainer invocations to start close enough together that this kind of
  race recurs.
- **Round-level instrument-defect pattern (carried forward, now 7
  independent confirmations)**: adds this run's r2s4-B3 register-turn
  findings (`ledger_contamination_audit.py`'s ceiling/contamination/
  row-count triad, and the foreign-data `stage_blend_decoder` zero-field
  catch) to the prior 6 (`r2s1_direct`'s post-hoc-blend-stage class,
  `r2s2_stacked-B2`'s statistic mis-specification, `r2s4_diag-B3`
  turn-2's mis-specified `advantage_reachable`, turn-3's self-corrected
  probe-ordering bug, `r2s3_lf_train_signal-B3`'s resolved knife-edge) —
  worth folding into the round-report action item.
- **Timing ledger**: **unchanged this run** — 16 entries, still parseable
  JSON. `r2s1_direct-B3`'s job 66262741 remains PENDING, not COMPLETED — no
  upsert due yet.
- **Analyzer caveat (r2s1_direct-B1, from code-review)**, carried forward:
  the D3 certificate's aleatoric-floor estimate is window-sensitive — at
  the recipe's window (1000 closest pairs), `ext__helmholtz_2d` reads
  1.200, worse than the zero predictor. Must not be reported as a ceiling
  for helmholtz; `allen_cahn`'s ceiling must be reported as a range
  (0.315-0.471); `pfc`/`fisher_kpp` are window-robust and quotable.
- **Analyzer caveat (r2s2_stacked-B1, from code-review + register turn),
  preserved for the round report**: `ifc_poisson`'s rung ladder is UNPAIRED
  (independent condition draws per rung, min distance 0.08-0.30, never 0) —
  matches r2s3's independent finding, and is now also confirmed by r2s4-B2 —
  three independent streams/estimators, a cross-stream benchmark-integrity
  item.
- **Analyzer caveat (r2s3_lf_train_signal-B1, from code-review)**, carried
  forward: the shared-max-abs-rungs scaler makes ifc_poisson's `rung_native`
  stage-1 loss ~42x amplitude-weighted toward rung 8 over HF (confound C1,
  card-locked design, not a build defect); F1 is epoch-matched but not
  step-matched (confound C2). r2s3-B2's card shipped a step-matched,
  per-rung-scaled repair of both confounds this round (now closed).
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
- No reopen candidates on any of the 12 cards. No `blocked.md` file exists
  (no stream has ever blocked). **No abandoned streams** — none qualify
  (all 4 streams show clean complete/analyzing/drafted/running
  progressions with no skip/block history anywhere). `state/streams/`
  directory still does not exist — consistent with no abandonments ever
  being needed.
- Repo hygiene: `git status --short .` on the round root (excluding
  `worktrees/`) at this final check: `experiment_cards/r2s4_diag/batch_3/B3.json`
  (M — `analyzing`→`complete`, mechanism-analyzer/register-turn-owned),
  `state/r2s1_direct/current_stage.txt` (M — orchestrator-owned watch-item
  note), `state/r2s4_diag/current_stage.txt` (M — orchestrator-owned, still
  stale turn-1 text despite the card now `complete`), `tools/index.md`
  (M — 2 tool promotions from r2s4-B3's register turn),
  `websearches/r2s3_lf_train_signal/batch_4/` (M+?? — websearcher-owned,
  iterations 2-5 + report.md), `websearches/r2s4_diag/batch_4/` (?? —
  websearcher-owned, new dispatch). This maintainer's own writes this run:
  `index.md`, `state/maintainer_report.md`. No Write call this run touched
  `experiment_cards/`, `tools/`, or any other-agent-owned `state/` file.
  `state/timing_ledger.json` untouched (no COMPLETED job to upsert yet —
  gitignored regardless).
