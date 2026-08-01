# MFFP Autoresearch Round 2 — Dashboard (updated 2026-08-01T20:14:35Z)

**Eleventh maintainer walk since the operator halt/resume cycle.**
Halt landed 2026-08-01T01:31:54Z (commit `10d4e4c`), resume landed
2026-08-01 ~08:1x PDT (commit `b80e622`).

**Headline this run**: `r2s3_lf_train_signal-B4` cleared code review
(verdict SUGGEST, submit-as-is) and was submitted — job 66268786, forced
onto the `expansion` partition after the `gpu` partition rejected the
gres-less submit (CLI `--partition` override per the builder's
pre-flagged fallback; build commit `bd1f746` untouched). The job already
**COMPLETED** per `sacct` (98s wall, training-free CPU diagnostic) —
card still reads `status: running`, so this is flagged as a staleness
item below rather than silently treated as closed; timing ledger
upserted regardless.
`r2s4_diag-B4` cleared its first review round with verdict
**`reviewed_fail`** — a real, non-cosmetic defect: `smoke_eval.py`'s
`_repo_root()` resolver treats the git worktree itself as the repo root
(a worktree is a full checkout carrying `project.yaml`), so the
diagnostic JSON the anatomy script expects at
`${OUTPUTS_ROOT}/r2s4_diag/B4/eval` is instead written under
`<worktree>/mffp_autoresearch_outputs/...`; the failure is masked by a
non-fatal `|| echo [warn]` in `03_anatomy.sh`, so **the job would exit 0
with no diagnostic.json at the carded output path** — a one-token
regression versus B3's working same-stream pattern (minimal fix:
`WORKTREE_ROOT.parents` only, not `[WORKTREE_ROOT] + .parents`). The
reviewer separately **endorsed** the builder's O1/O2/O3
pre-registration-gap handling as correct and must-preserve (not a FAIL
cause) — the locked CI-outcome clause doesn't partition the space, and
re-registering now would be a data-peeked amendment since the 2-epoch CI
already straddles the gap. No SLURM submission was ever made for this
card (`job_ids: []`); a re-review is required after the fix commit lands.
Both r2s1/r2s2 B3 SLURM jobs remain **PENDING**, unchanged: 66262741
(`r2s1_direct-B3`, seed 0), 66267438 / 66267441 (`r2s2_stacked-B3` panel /
guard) — all Priority-queued, `Elapsed=00:00:00`, verified by both
`squeue` and `sacct` at this run's check.

## Streams

| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r2s1_direct | 23.0636 (best_floor_panel_geomean) | 3 | r2s1_direct-B1 **complete**; r2s1_direct-B2 **complete**; r2s1_direct-B3 **running** | Unchanged this run. Seed-0 job **66262741 still PENDING** in `squeue`/`sacct` (Priority-queued, `Elapsed=00:00:00`) | **1 live/pending SLURM** (`r2-r2s1_direct-B3-s0`, job 66262741, PENDING) | No change; job still PENDING |
| r2s2_stacked | 23.0636 (best_floor_panel_geomean) | 3 | r2s2_stacked-B1 **complete**; r2s2_stacked-B2 **complete**; r2s2_stacked-B3 **running** | Unchanged this run — still `running`, job_ids `['66267438','66267441']`. Both jobs remain PENDING; the standing watch item (guard job's name will collide with the panel job's name once RUNNING; match by ID) still applies | **2 live/pending SLURM** (`r2-r2s2_stacked-B3-s0` 66267438, `r2-r2s2_stacked-B3-guard-s0` 66267441, both PENDING) | No change; both jobs still PENDING |
| r2s3_lf_train_signal | 23.0636 (best_floor_panel_geomean) | 4 | r2s3_lf_train_signal-B1..B3 **complete**; r2s3_lf_train_signal-B4 **running (reviewed SUGGEST, submitted this run)** | `status: built` → `running` (review verdict SUGGEST, submit-as-is; 3 analyzer seams S1-S3 recorded on `review_notes`). Job **66268786 submitted on the `expansion` partition** (CLI override — `gpu` partition rejected the gres-less job). `sacct` already shows this job **COMPLETED** (98s wall) — card `status` has not yet caught up; see Flags | **0 live SLURM** (job already COMPLETED per sacct, 1.63 min, training-free CPU diagnostic; ledger upserted this run) | Reviewed + submitted + completed, all within this run's window |
| r2s4_diag | **19.8178** (certified_3seed_panel_geomean, CI95 [19.385, 20.527]) | 4 | r2s4_diag-B1..B3 **complete**; r2s4_diag-B4 **reviewed_fail (this run)** | `status: built` → `reviewed_fail`. Blocking root cause: worktree-vs-repo-root path resolution bug masked by a non-fatal anatomy-script fallback — job would exit 0 with the deliverable diagnostic.json never written. O1/O2/O3 pre-registration-gap handling **ENDORSED** by the reviewer as correct (not the fail cause; do not re-register). `job_ids: []` — never submitted | **0 live SLURM** (card blocked pending fix + re-review) | Reviewed this run — needs a debugger/builder pass on the fix before resubmission |

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

**3 live/pending `r2-*` SLURM jobs**, unchanged from the prior close — all
still PENDING at this run's check, confirmed by both `squeue` and
`sacct`. One additional `r2-*` job (66268786, `r2s3_lf_train_signal-B4`,
`expansion` partition) submitted and **COMPLETED** entirely within this
run's window (98s wall) — not "live" at this check, upserted into the
timing ledger. `sacct` 2-day window otherwise shows the same 16
pre-existing `r2-*` jobs, all COMPLETED 0:0, identical to the prior
ledger set.

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
`running`/reviewed-SUGGEST (job already COMPLETED per sacct, but no part
5/6/7 yet visible on the card) — not listed here until it closes.
`r2s4_diag-B4` is `reviewed_fail` (blocked pending fix + re-review, never
submitted) — not listed here.

## Flags

- **`r2s4_diag-B4` REVIEWED_FAIL this run — needs a debugger/builder
  pass, then re-review** (build commit `dc0d7ae`, review verdict
  `reviewed_fail`, `worktrees/r2s4_diag/B4/notes/handoff_code_reviewer.md`,
  landed 2026-08-01T20:12:29Z, ~4 min before this walk). **Blocking root
  cause**: `smoke_eval.py:331`'s `_repo_root()` iterates
  `[WORKTREE_ROOT] + WORKTREE_ROOT.parents`; because a git worktree of
  this repo is itself a full checkout carrying
  `mffp_autoresearch/round2/project.yaml`, the resolver returns the
  WORKTREE itself, so the diagnostic JSON lands at
  `<worktree>/mffp_autoresearch_outputs/round2/r2s4_diag/B4/eval` instead
  of the carded `${OUTPUTS_ROOT}/r2s4_diag/B4/eval`; `03_anatomy.sh`'s
  final `|| echo [warn] ...` makes this non-fatal, so **the job would
  exit 0 with no `diagnostic.json` written at the scored path** — a
  one-token regression versus B3's same-stream `_diag_out_dir()`, which
  iterates `.parents` only and is unaffected. **Minimal fix** per the
  reviewer: `for anc in WORKTREE_ROOT.parents:` (drop the
  `[WORKTREE_ROOT] +`), harden the anatomy-script call to be fatal /
  assert `diagnostic.json` is non-empty, then re-verify once at contract
  tier **without** any `R2S4B4_DIAG_OUT` override (neither of the
  builder's two verification runs exercised the seam that actually
  broke — both passed an absolute scratchpad path). **Not blocking**:
  reviewer independently **endorsed** the builder's handling of the
  O1/O2/O3 pre-registration-gap (the locked CI-outcome clause doesn't
  partition the space; the probe correctly reports `O_UNCLASSIFIED` with
  `prereg_gap=true` rather than forcing a verdict) — explicitly **not**
  the fail cause, and re-registering now would be a data-peeked
  amendment since the 2-epoch CI ([0.14594, 1.55431], half-width 0.70419
  < bound 0.93770) already straddles the gap. Downstream obligations for
  the initial-analyzer recorded verbatim on the card (record
  `O_UNCLASSIFIED`+`prereg_gap=true` as-is; watch for the CI-below-bound
  second lobe too; a successor card must pre-register a 4-way partition
  before any run). `job_ids: []` — no SLURM submission was ever made.
  `state/r2s4_diag/current_stage.txt` already anticipates a fix-and-
  resubmit cycle ("builder re-engaged with reviewer's 3 required fixes")
  but as of this run's close no new commit exists on top of `dc0d7ae` in
  `worktrees/r2s4_diag/B4` — **watch item for the next walk**: confirm
  the fix lands and a re-review verdict is produced.
- **`r2s3_lf_train_signal-B4` reviewed SUGGEST and submitted this run,
  then completed within this same run's window** (build commit
  `bd1f746`, review verdict SUGGEST/submit-as-is, 3 analyzer seams S1-S3
  transcribed onto `review_notes` for the initial-analyzer). Job
  **66268786** was submitted on the **`expansion` partition** — the
  `gpu` partition rejected the gres-less submit, so the orchestrator used
  a CLI `--partition` override per the builder's pre-flagged fallback
  (build itself untouched). `sacct` shows the job **COMPLETED** already
  (`Start` 13:09:11 PDT / `End` 13:10:49 PDT, 98s wall, ~4 min before
  this walk) — training-free CPU-only diagnostic, no GPU, no checkpoint
  contract. **Staleness item**: the card's `status` field still reads
  `running` and `job_ids` still lists only `66268786` with no part
  5/6/7 populated — the card has not yet caught up to the job's actual
  completion. Timing ledger upserted this run regardless (17th entry).
  **Watch item for the next walk**: confirm the card transitions to
  reflect the completed job and that part 5's measured values are picked
  up by the initial-analyzer.
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
- **Job 66268786 (r2s3_lf_train_signal-B4, seed 0, expansion
  partition)**: confirmed via `squeue` (absent — no longer live) and
  `sacct` (COMPLETED 0:0, 98s wall) this run — see the dedicated flag
  above for the card-vs-job staleness gap.
- **Staleness — `r2s3_lf_train_signal-B4` card status lags its job's
  actual completion (new this run)**: see flag above; carried forward
  until the card catches up.
- **Round-level instrument-defect pattern (carried forward, 7 independent
  confirmations; this run's `r2s4_diag-B4` code-review finding is a
  distinct SLURM/path-resolution defect class, not folded into this
  count since it was caught pre-submission by review rather than in a
  scored run)**: `r2s1_direct`'s post-hoc-blend-stage class (adjudicated
  non-defective); `r2s2_stacked-B2`'s statistic mis-specification;
  `r2s4_diag-B3` turn-2's mis-specified `advantage_reachable`, turn-3's
  self-corrected probe-ordering bug; `r2s3_lf_train_signal-B3`'s resolved
  knife-edge; `r2s4_diag-B3` register-turn's ceiling/contamination/
  row-count triad and its foreign-data `stage_blend_decoder` zero-field
  catch — worth folding into the round-report action item once the round
  closes.
- **`r2s1_direct-B3`'s `stage_blend_decoder` zero-field item — remains
  ADJUDICATED, defect ruled OUT** (unchanged from several walks ago). No
  further action needed.
- **Timing ledger**: upserted this run — 17 entries (was 16), still
  parseable JSON. New entry: job 66268786 (`r2s3_lf_train_signal-B4`
  seed 0, `models_r2/r2s3_b4_substitution`, CPU-only, `expansion`
  partition, 1.63 min). The 3 previously-tracked live SLURM jobs remain
  PENDING, not COMPLETED — no further upsert due for them.
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
- **Analyzer caveat (r2s4_diag-B4, from code-review, new this run)**:
  `recipe.env R2S4B4_NOISE_FLOOR_JSON` is echoed into `resolved_recipe`
  but never read by the family, and resolves (if it ever were read) to
  the worktree's stale `noise_floor.json` (`ifc_poisson.min_claimable_effect`
  0.2399, not the certified 0.9377) — inert today since the probe reads
  the main tree's file via an absolute path, but a future analyst quoting
  `resolved_recipe` verbatim could pick up the wrong number.
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
  (all 4 streams show clean complete/running/reviewed_fail progressions
  with no skip/block history anywhere). `state/streams/` directory still
  does not exist — consistent with no abandonments ever being needed.
- Repo hygiene, final check: `git status --short .` on the round root at
  close shows `experiment_cards/r2s3_lf_train_signal/batch_4/B4.json` and
  `experiment_cards/r2s4_diag/batch_4/B4.json` (both M — orchestrator/
  reviewer-owned, `built` → `running`/`reviewed_fail` this run), plus
  `state/r2s3_lf_train_signal/current_stage.txt` and
  `state/r2s4_diag/current_stage.txt` (both M — orchestrator-owned
  refresh, already matching the cards' new statuses at this run's open),
  and this maintainer's own writes: `index.md`, `state/maintainer_report.md`,
  `state/timing_ledger.json`. No Write call this run touched
  `experiment_cards/`, `tools/`, or any other-agent-owned `state/` file.
