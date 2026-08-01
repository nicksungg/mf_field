# MFFP Autoresearch Round 2 — Dashboard (updated 2026-08-01T18:46:15Z)

**Seventh maintainer walk since the operator halt/resume cycle.**
Halt landed 2026-08-01T01:31:54Z (commit `10d4e4c`), resume landed
2026-08-01 ~08:1x PDT (commit `b80e622`).

**Headline this run**: the `r2s1_direct-B3` `stage_blend_decoder` zero-field
item flagged in the prior walk has been **ADJUDICATED by the orchestrator
as rational selection, not a defect** — see Flags for the full reasoning.
Job 66262741 (seed 0) is **still PENDING**, unchanged.
Both B4 websearchers are now complete (`r2s3_lf_train_signal` and
`r2s4_diag`). `r2s3_lf_train_signal`'s B4 brainstormer has **resolved**:
decision is **card B4**, a training-free substitution-audit diagnostic —
**the card landed** (`r2s3_lf_train_signal-B4`, `drafted`) in a final
re-check just before this walk's close, moments after the first pass of
this dashboard was drafted.
`r2s4_diag`'s B4 brainstormer is **still running** (summary only, decision
not yet made).

## Streams

| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r2s1_direct | 23.0636 (best_floor_panel_geomean) | 3 | r2s1_direct-B1 **complete**; r2s1_direct-B2 **complete**; r2s1_direct-B3 **running** | Card unchanged this run. `state/r2s1_direct/current_stage.txt` **updated this run**: the WATCH ITEM opened last walk (helmholtz `stage_blend_decoder` zero-field prediction) has been **adjudicated as rational selection, not a defect** — per-sample rel-L2 exactly 1.0 (zero-prediction signature), blend `cal_table` shows every base+decoder worse than nRMSE 1.0 at 2-epoch smoke on helmholtz, same code path healthy (0.362) on ifc_poisson, arm is REFERENCE-only, never scored. Standing caveat for the initial-analyzer preserved: a zero-blend at FULL (200-epoch) tier would still be plausible-rational on helmholtz specifically, unless zero-collapse appears on any OTHER dataset. Seed-0 job **66262741 still PENDING** in `squeue` (Priority-queued, `Elapsed=00:00:00`) | **1 live/pending SLURM** (`r2-r2s1_direct-B3-s0`, job 66262741, PENDING) | Watch item adjudicated (defect ruled out); job still PENDING |
| r2s2_stacked | 23.0636 (best_floor_panel_geomean) | 3 *(card exists; `current_batch.txt` still stale at "2")* | r2s2_stacked-B1 **complete**; r2s2_stacked-B2 **complete**; r2s2_stacked-B3 **drafted** | Unchanged this run. Builder's family `models_r2/r2s2_zerograd/` (10 modules + `probes/`) was already fully landed by the prior walk's close; this run finds the same file set (pycache mtimes predate this run's window, no new source files). Card still `drafted`/`job_ids: []`, no `build_commit`, no contract-smoke result yet observed | **0 live SLURM** | No change this run |
| r2s3_lf_train_signal | 23.0636 (best_floor_panel_geomean) | 4 *(`current_batch.txt` still reads "3")* | r2s3_lf_train_signal-B1 **complete**; r2s3_lf_train_signal-B2 **complete**; r2s3_lf_train_signal-B3 **complete** (10th card, closed 2 walks ago) | Card unchanged this run. **B4 brainstormer completed this run**: decision **card B4** (`brainstormer/r2s3_lf_train_signal/batch_4/report.md`) — a training-free, `epochs=0`, no-GPU `lf_train_signal / substitution audit` diagnostic in a new probe family `models_r2/r2s3_b4_substitution/`, reading only B3's shipped leg JSONs and `*_preds.npz` dumps (never opens an LF field). Decisive pre-flight findings quoted: B3's ifc leg is 77.9% reproducible by an LF-free control already inside B3's own leg JSONs, and fisher_kpp's LF arm loses to its own `train_mean_n5` floor on all three draws — closing on B3 as-is would leave the round's central claim overstated by its own artifacts. Worktree `worktrees/r2s3_lf_train_signal/B4` exists (scaffolding only). **Card landed in this run's final re-check**: `experiment_cards/r2s3_lf_train_signal/batch_4/B4.json` (`status: drafted`, `job_ids: []`, `card_type: diagnostic`) — content matches the brainstormer report verbatim | **0 live SLURM**; card drafted, builder not yet observed | B4-or-close resolved → card B4 drafted |
| r2s4_diag | **19.8178** (certified_3seed_panel_geomean, CI95 [19.385, 20.527]) | 4 | r2s4_diag-B1 **complete**; r2s4_diag-B2 **complete**; r2s4_diag-B3 **complete** | Card unchanged this run. **B4 websearch completed this run**: `websearches/r2s4_diag/batch_4/` gained iterations 2-5 + `report.md` (up from summary-only at prior close) — verdict frames an "anatomy card open in composition" (the §12.4 ifc_poisson N_hf-anatomy diagnostic remains reachable) plus an equivalence-test remedy for the stream's claimability protocol. **B4 brainstormer now running** on this input: only `summary_so_far.md` present so far (no `iteration_1.md`/`report.md`), landed ~11:36-11:38 local, re-checked at close with no new file — decision not yet made. `state/r2s4_diag/current_stage.txt` still reads the B3-close summary text (not yet refreshed for the in-progress B4 brainstormer) | **0 live SLURM** (job terminal); brainstormer actively running (in-progress, not stalled — landed a file within this run's window) | B4 websearch complete; B4 brainstormer in progress |

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

**1 live/pending `r2-*` SLURM job** (unchanged from the prior run — still
queued on Priority, has not started running). `sacct` 2-day window
otherwise shows the same 16 `r2-*` jobs, all COMPLETED 0:0, identical to
the timing ledger — no ledger upsert due (66262741 still PENDING). Non-
SLURM agent activity this run: the `r2s3_lf_train_signal` B4 brainstormer
landed its decision and closed; the `r2s4_diag` B4 brainstormer is
actively running (in progress at close).

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
| r2s4_diag-B3 | diagnostic | 19.172826 (single seed 0, no own-card CI — 1 seed; in-job 5-fold paired spreads are per-dataset thresholds, not a panel CI) | **falsified** (F3 stands and is hardened by two row-count/capacity controls; F4a fired on the ledger's own contaminated-quantity definition, not on a measurement failure — 0/4 under the corrected teacher-target term; F1 survives on 2 of its 3 needed cells, pfc's cell ruled uninformative by a ceiling argument). Mechanism headline: on 3 of 4 sharp datasets the condition-only arm's per-band error is ~1.00 above the lowest band — it contributes exactly zero energy above the spatial mean — while the LF field reproduces HF to 1e-2 to 1e-16 band relative error, i.e. essentially all panel structure is realisation information carried only by LF. `cratered_verdict: n/a` (diagnostic) | **2 tools**, both correctly indexed: `tools/ledger_contamination_audit.py` (prices whether a paired-arm delta *could* have fired via a triangle-inequality ceiling, and whether it's contaminated by a function-class term vs the true target term), `tools/band_retention_probe.py` (per-band retained-energy/relative-error decomposition; on its first foreign-data run it independently found the `stage_blend_decoder` zero-field arm in r2s1_direct-B3's shipped dumps — now adjudicated, see Flags) |

`r2s1_direct-B3` is `running` (job 66262741 PENDING, no part 5 yet) — not
listed here until it closes. `r2s2_stacked-B3` is `drafted` (not built) —
not listed here.

## Flags

- **`r2s1_direct-B3`'s `stage_blend_decoder` zero-field item — ADJUDICATED
  this run, defect ruled OUT (was VERIFIED-but-open in the prior walk)**.
  The orchestrator's adjudication, now recorded in
  `state/r2s1_direct/current_stage.txt`: the smoke `stage_blend_decoder`
  zero-field prediction on `ext__helmholtz_2d` is **rational selection**,
  not a defect. Diagnostic evidence: per-sample rel-L2 exactly 1.0 (the
  zero-prediction signature); the blend `cal_table` shows every base +
  decoder combination scoring worse than nRMSE 1.0 at the 2-epoch smoke
  tier on helmholtz, so `calib_fold_relL2` correctly selected full
  zero-base weight; the same code path produces a healthy nonzero blend
  (0.362) on `ifc_poisson`, so this is not a broken code path — it is
  helmholtz-specific. The arm is REFERENCE-only and was never the card's
  scored arm (`R2S1B3_SCORED_ARM=stagefree_permode_set_head`). **Reopen
  condition preserved as a standing note for the initial-analyzer**: at
  the full 200-epoch tier, a zero-blend on helmholtz specifically would
  still be plausible-rational (helmholtz's best floor IS the zero
  predictor historically) — only treat a zero-collapse as a live concern
  again if it appears on any OTHER dataset. This closes the item this
  maintainer flagged with independent artifact verification (direct numpy
  load of the `.npz`, `max(abs(pred)) == 0.0`) two walks ago — no further
  action needed from this maintainer or Eloise on this item.
- **`r2s3_lf_train_signal` B4-or-close resolved this run: card B4**
  (`brainstormer/r2s3_lf_train_signal/batch_4/report.md`). Decision: a
  training-free (`epochs=0`, no GPU), single-run diagnostic — new probe
  family `models_r2/r2s3_b4_substitution/` — that measures how much of
  B3's certified ±LF effect is absorbed by an achievable LF-free control
  class (raw/global/ridge/kNN-calibrated heads, plus reference floors) vs
  test-fitted ceilings, reading only B3's shipped leg JSONs and
  `*_preds.npz` dumps (never opens an LF field). Motivated by B3 part 7's
  open question about whether the round's affirmative LF-value evidence
  reduces to an output-calibration trick. Decisive pre-flight inputs:
  B3's `ifc_poisson` leg is 77.9% reproducible by an LF-free control
  already computed inside B3's own leg JSONs, and `fisher_kpp`'s LF arm
  loses to its own `train_mean_n5` floor on all three draws — closing on
  B3 as-is would leave the round's central claim overstated by its own
  artifacts. Worktree `worktrees/r2s3_lf_train_signal/B4` exists
  (scaffolding only). **Update from this run's final re-check (caught after
  the first pass of this file was drafted)**: the starter turned the
  decision into an actual card, `experiment_cards/r2s3_lf_train_signal/batch_4/B4.json`
  (`status: drafted`, `job_ids: []`), content matching the brainstormer
  report verbatim — builder step not yet observed.
- **`r2s4_diag` B4 websearch complete this run**: `websearches/r2s4_diag/batch_4/`
  gained iterations 2-5 + `report.md` (up from summary-only at the prior
  close). Frames an "anatomy card open in composition" — the §12.4
  ifc_poisson N_hf∈{5,20,50} anatomy diagnostic remains reachable — plus
  an equivalence-test remedy for the stream's claimability protocol. Feeds
  the B4 brainstormer, which is **still running** at this run's close
  (only `summary_so_far.md` present, no `iteration_1.md`/`report.md` yet);
  decision not yet made, to be picked up next walk. `state/r2s4_diag/current_stage.txt`
  has not yet been refreshed to reflect the in-progress B4 brainstormer.
- **Job 66262741 (r2s1_direct-B3, seed 0)**: confirmed via both `squeue`
  and `sacct` — still **PENDING**, Priority-queued, unchanged since the
  prior run's close.
- **Round-level instrument-defect pattern (carried forward, now 7
  independent confirmations, no new occurrence this run)**: the prior 7
  (`r2s1_direct`'s post-hoc-blend-stage class — now itself adjudicated
  non-defective this run, see above; `r2s2_stacked-B2`'s statistic
  mis-specification; `r2s4_diag-B3` turn-2's mis-specified
  `advantage_reachable`, turn-3's self-corrected probe-ordering bug;
  `r2s3_lf_train_signal-B3`'s resolved knife-edge; `r2s4_diag-B3`
  register-turn's ceiling/contamination/row-count triad and its
  foreign-data `stage_blend_decoder` zero-field catch) — worth folding
  into the round-report action item once the round closes.
- **Timing ledger**: unchanged this run — 16 entries, still parseable
  JSON. `r2s1_direct-B3`'s job 66262741 remains PENDING, not COMPLETED —
  no upsert due yet.
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
  (all 4 streams show clean complete/drafted/running progressions with no
  skip/block history anywhere). `state/streams/` directory still does not
  exist — consistent with no abandonments ever being needed.
- Repo hygiene: `git status --short .` on the round root (excluding
  `worktrees/`) at this run's close: `brainstormer/r2s3_lf_train_signal/batch_4/iteration_1.md`,
  `brainstormer/r2s3_lf_train_signal/batch_4/preflight_gain_probe.py`,
  `brainstormer/r2s3_lf_train_signal/batch_4/report.md` (all ?? —
  brainstormer-owned, new this run), `brainstormer/r2s4_diag/batch_4/`
  (?? — brainstormer-owned, in-progress, new this run). This maintainer's
  own writes this run: `index.md`, `state/maintainer_report.md`. No Write
  call this run touched `experiment_cards/`, `tools/`, or any other-agent-
  owned `state/` file. `state/timing_ledger.json` untouched (no COMPLETED
  job to upsert yet — gitignored regardless).
