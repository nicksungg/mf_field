# MFFP Autoresearch Round 2 — Dashboard (updated 2026-08-01T01:00:28Z)

## Streams

| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r2s1_direct | 23.0636 (best_floor_panel_geomean) | **3** | r2s1_direct-B1 **complete**; r2s1_direct-B2 **complete** | **B1: unchanged, still COMPLETE.** **B2: `analyzing` -> `complete` this run** (register turn landed 8/8, seventh card closed). `falsification_verdict: falsified` — H-r2s1-B2 (training-free ~10^2-param closed-form head matches a 10^7-param decoder everywhere, incl. cahn_hilliard) is FALSIFIED: **L1 fires** (loses to the in-job Wiener-calibrated `ref_decoder_big` by >mce on 2/5 decidable cells: `sharp__allen_cahn_2d` +6.151 skill/6.99x mce, `sharp__cahn_hilliard` +1.296 skill/14.21x mce), **L2 fires** (cahn_hilliard gap 4.74x the L2 threshold = 14.21x mce, stable across all 5 fold-resamples, no rank in the sweep rescues it), L3/L4 do not fire (clears every training-free floor; selection rule beats its own alternative on only 1/6 datasets). Panel geomean 18.3622 — single-seed, **no falsification weight** (card's own disclaimer), vs anchor -20% (not a claim) and vs B1 -1.2822 (1.12x the min_claimable_effect — **not claimable**). `anchor_updated: false`. 2 tools promoted (`blend_decorrelation_payoff.py`, `selection_set_vs_window_audit.py`). Part 7 flags a round-level **post-hoc-blend-stage instrument-error class** as prerequisite to any further capacity claim. Stream advanced to **batch 3**: B3 websearcher dispatched (B3-or-close decision deferred to the brainstormer), `websearches/r2s1_direct/batch_3/` created but empty at this check (no `iteration_1.md` yet) | **0 live SLURM** (both seed-0 jobs terminal, unchanged); 0 live local processes for this stream at this check | `r2s1_direct-B2` register-turn completion (7th card closed); stream advanced to batch 3, B3 websearcher dispatched |
| r2s2_stacked | 23.0636 (best_floor_panel_geomean) | **2** | r2s2_stacked-B1 **complete**; r2s2_stacked-B2 **analyzing** | **B1: unchanged, still COMPLETE.** **B2: no card-content delta this run** (still `reanalysis_progress: turn_2`, `6_analysis: null` — write-ordering lag persists, now spanning 3 checks). Landed-so-far (per `orchestrator_flow.md`, not yet on-card): turn 1 traced F1 to a statistic mis-specification (centred repair flips `B:all`'s gamma to 0.99-1.00, F1 fires on 0 cells); turn 2 traced the 2 surviving F3 cells to ESTIMATOR BIAS (zero-information control reproduces the firings to <=0.005) and F2 to an endpoint-comparison artifact — all three fired falsification clauses now traced to statistic/instrument defects, not a real model deficiency; candidate real lead flagged (a training-free interior-k LF average beats the trained corrector on allen_cahn/cahn_hilliard). **Turn-3 mechanism script confirmed live and progressing this run** (PID 232585, a fresh per-dataset loop invocation; `cahn_hilliard` and `phase_field_crystal_2d` legs already wrote outputs, now on the `fisher_kpp` leg 3/4, `allen_cahn` remaining) | 0 live SLURM (both legs terminal, unchanged); **1 live local process** (turn-3 mechanism script, PID 232585, leg 3/4) | No card-content delta; turn-3 script progressing (2/4 dataset legs written this run) |
| r2s3_lf_train_signal | 23.0636 (best_floor_panel_geomean) | **3** | r2s3_lf_train_signal-B1 **complete**; r2s3_lf_train_signal-B2 **complete**; r2s3_lf_train_signal-B3 **drafted** | **B1/B2: unchanged this run, both still COMPLETE.** **B3.json newly created this run** (mtime inside this run's window; captured by a mid-run auto-sync commit `5c40c02`): starter landed 15/15 — a 33-leg **measurement-completion** model card (`models_r2/r2s3_coverage_panel`, all 6 panel datasets, A0-vs-A1 matched-budget ±LF contrast, 3 draws/dataset, the cratering-avoidance penalty deleted). Close-on-B2 explicitly considered and rejected (4 grounds, incl. r2s4-B2's target-side null making this the only live criterion-1 route). **Builder now running** — mandatory contract-smoke evidence in progress (PID 234088, `ext__helmholtz_2d`, epochs=2); family files on disk (`model.py`, `affine_probe.py`, `lf_reference.py`, `refs.py`), no `scripts/` or git commit yet | **0 live SLURM** (seed-0 jobs from B1/B2 terminal, unchanged; B3 not yet built to a submittable state); **1 live local process** (B3 builder contract-smoke run, PID 234088) | New: `r2s3_lf_train_signal-B3.json` drafted (33-leg measurement-completion card); builder dispatched and running |
| r2s4_diag | **19.8178** (certified_3seed_panel_geomean, CI95 [19.385, 20.527]) | **3** | r2s4_diag-B1 **complete**; r2s4_diag-B2 **complete**; r2s4_diag-B3 **drafted** | **B1/B2: unchanged, both still COMPLETE.** **B3: no card change this run** (still `status: drafted`, `job_ids: []`, `build_commit: null`). Builder progressed substantially this run: 3/4 guard-set debug legs now landed on disk (`dbg_fluid.json`, `dbg_ifc_poisson.json`, `dbg_sharp__sod_1d.json`, plus a fresh `contract_smoke.json` and `scratchpad/smoke_arms/`), **currently running the 4th and last guard leg** (`heat_local`, PID 235830); `scripts/{01_train_eval.sh, 03_ledger.sh, submit.sh}` all now present (new this run) — **SLURM submission looks imminent but has not fired yet**, no git commit yet | **0 live SLURM** (all prior seeds terminal, unchanged; B3 not yet submitted); **1 live local process** (builder's `heat_local` guard-leg debug run, PID 235830, last of 4 guard legs) | Builder landed 3/4 guard legs + all SLURM scripts; now running the last leg, submission imminent |

**Anchor note**: r2s4_diag remains the only stream with a *certified* anchor
(`certified_3seed_panel_geomean`, 19.8178, replacing the training-free floor)
— r2s1_direct, r2s2_stacked, r2s3_lf_train_signal remain on the launch-time
`best_floor_panel_geomean` anchor (23.0636, `certified_utc` 2026-07-31T14:20:17Z,
unchanged). `r2s1_direct-B2`'s completion does **not** update the r2s1_direct
anchor (`anchor_updated: false` on-card — single seed, non-claimable per S2e).
No anchor deltas this run. All anchors rendered verbatim from
`state/anchors/*.json`.

**This run's headline**: **2 card-content deltas** — (1) `r2s1_direct-B2`
closed (`analyzing`->`complete`, **seventh card of the round**, falsified
verdict with L1+L2 firing, 2 tools promoted, stream advanced to batch 3);
(2) `r2s3_lf_train_signal-B3.json` newly drafted (33-leg measurement-completion
card, builder now running). Sub-card activity: `r2s2_stacked-B2`'s turn-3
script wrote 2 more dataset legs (now on leg 3/4); `r2s4_diag-B3`'s builder
landed 3/4 guard legs plus all its SLURM scripts and is running the last leg.
SLURM state (0 live, 14 total COMPLETED), timing ledger, anchors, gates, and
noise floor are all unchanged. A mid-run auto-sync commit (`5c40c02`,
2026-08-01T00:44:16Z) landed inside this run's window, capturing the B3 card
draft and websearcher/brainstormer batch-3 outputs — noted for repo-hygiene
accounting, not itself a maintainer write.

## Running / pending jobs

| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| (none — 0 live SLURM `r2-*` jobs) | — | — | — | — |

**0 live `r2-*` SLURM jobs** at this check (squeue + sacct cross-checked twice,
~4 min apart, no transient-empty false positives — `sacct` shows all 14
`r2-*` jobs COMPLETED, byte-identical to the last check; `squeue` shows 0
`r2-*` entries, only unrelated interactive `bash` jobs and round-1 `r1-*`
PENDING seed-confirm jobs, out of this maintainer's scope). **3 live local
(non-SLURM) processes** confirmed via `ps aux` at this check, all confirmed
progressing (not stalled): PID 232585 (`r2s2_stacked-B2` turn-3 mechanism
script, on the `fisher_kpp` leg, 3/4 dataset legs), PID 234088
(`r2s3_lf_train_signal-B3` builder's mandatory contract-smoke evidence run on
`models_r2/r2s3_coverage_panel`), PID 235830 (`r2s4_diag-B3` builder's last
guard-set debug leg, `heat_local`).

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

`r2s2_stacked-B2` (`analyzing`, `reanalysis_progress: turn_2`, turn-3 script
progressing, 3/4 dataset legs written), `r2s3_lf_train_signal-B3` (`drafted`,
builder running the mandatory contract-smoke evidence, no SLURM job yet) and
`r2s4_diag-B3` (`drafted`, builder running its last guard leg with all
scripts written, submission imminent) are all actively open but none has
part 7 written (or, for B3 cards, any build/job yet) — not listed here
until each card itself closes.

## Flags

- **`r2s1_direct-B2` closed this run — seventh card of the round**: register
  turn landed 8/8 (`analyzing`->`complete`). Falsified verdict overturns
  B1's implicit-architecture reading specifically via the `cahn_hilliard`
  cell (L1+L2 both fire there, 14.21x mce, stable across all 5 fold-resamples
  — not a fold-draw artifact). 2 tools promoted, both indexed in
  `tools/index.md` (confirmed via `git diff`). `anchor_updated: false`
  (single seed, card explicitly disclaims the panel-geomean number as a
  claim). Part 7 poses a possible B3 as instrument-repair-first, not
  capacity-first.
- **NEW round-level pattern flagged by `r2s1_direct-B2` part 7**: a
  **post-hoc-blend-stage instrument-error class** — the blend/floor-hedge
  stage's payoff is a closed-form monotone function of the arm-vs-base error
  correlation rho, so a "capacity win" can be entirely a decorrelation
  artifact (allen_cahn: the selected head IS `dc_only` numerically, rho=1.0000,
  so the blend structurally cannot pay it; the L1 "loss" reverses under an
  equal-rho counterfactual, 2.1-7.2x mce in the head's favor). This is now
  the **third independent instrument-defect finding this round**, alongside
  `r2s2_stacked-B2`'s statistic mis-specification (turn 1) and estimator-bias
  /endpoint-artifact (turn 2) — flagged as a round-level methodology risk
  worth a cross-stream write-up, not yet a round report action.
- **`r2s3_lf_train_signal-B3` newly drafted this run**: a 33-leg
  measurement-completion card (all 6 panel datasets, matched-budget ±LF
  contrast); close-on-B2 explicitly rejected on 4 grounds. Builder dispatched
  and actively running the mandatory contract-smoke evidence; no SLURM job
  yet.
- **`r2s4_diag-B3` builder progressing toward a SLURM submission**: 3/4
  guard-set debug legs landed this run (`fluid`, `ifc_poisson`,
  `sharp__sod_1d`), now running the last (`heat_local`); all three SLURM
  scripts (`01_train_eval.sh`, `03_ledger.sh`, `submit.sh`) now present on
  disk — worth watching next cycle for an actual `sbatch` submission.
- **`r2s2_stacked-B2` write-ordering lag — persists, now spanning 3
  consecutive checks**: `6_analysis` is still `null` on-card even though
  `reanalysis_progress` has read `turn_2` since two checks ago and a turn-3
  mechanism script (now PID 232585, distinct from the prior run's PID
  221177 — a fresh per-dataset-loop invocation, not evidence of a restart
  from scratch) continues writing per-dataset outputs. Confirmed not stalled
  (2 new dataset legs written this run). Flagged for continued watching.
- **Real lead flagged inside `r2s2_stacked-B2` turn 2** (not yet a card
  claim): a training-free interior-k LF average reportedly beats the trained
  corrector on `allen_cahn`/`cahn_hilliard` — worth tracking into part 6/7
  once it lands on-card.
- **Mid-run auto-sync commit noted**: `5c40c02` (2026-08-01T00:44:16Z) landed
  inside this run's window and captured `r2s3_lf_train_signal-B3.json`, its
  brainstormer/websearcher batch-3 outputs, plus an EARLIER partial version
  of `r2s1_direct-B2.json` (pre-completion) — `git show --stat` cross-checked
  (11 files, 1753 insertions). Not a maintainer write; noted for repo-hygiene
  accounting only.
- **Timing ledger**: **no upsert this run** — no new terminal `r2-*` SLURM
  states (all 14 jobs in `sacct` were already COMPLETED and ledgered; neither
  `r2s3_lf_train_signal-B3` nor `r2s4_diag-B3` has submitted anything to
  SLURM yet). Still **14 entries** total, JSON re-validated as parseable.
- **Analyzer caveat carried forward (r2s1_direct-B1, from code-review)**: the
  D3 certificate's aleatoric-floor estimate is window-sensitive — at the
  recipe's window (1000 closest pairs), `ext__helmholtz_2d` reads 1.200,
  worse than the zero predictor. Must not be reported as a ceiling for
  helmholtz; `allen_cahn`'s ceiling must be reported as a range
  (0.315-0.471); `pfc`/`fisher_kpp` are window-robust and quotable.
- **Analyzer caveat (r2s2_stacked-B1, from code-review + register turn),
  preserved for the round report**: `ifc_poisson`'s rung ladder is UNPAIRED
  (independent condition draws per rung, min distance 0.08-0.30, never 0) —
  matches r2s3's independent finding, a cross-stream benchmark-integrity
  item. Cross-confirmed by two independent streams/estimators.
- **Analyzer caveat (r2s3_lf_train_signal-B1, from code-review)**, carried
  forward: the shared-max-abs-rungs scaler makes ifc_poisson's `rung_native`
  stage-1 loss ~42x amplitude-weighted toward rung 8 over HF (confound C1,
  card-locked design, not a build defect); F1 is epoch-matched but not
  step-matched (confound C2). r2s3-B2's card shipped a step-matched,
  per-rung-scaled repair of both confounds this round (now closed).
- **Timestamp-ahead-of-clock / clock-skew anomaly class (carried forward, no
  new distinct occurrence flagged this run)**: prior runs flagged
  `review_notes[0].utc` fields reading ahead of the actual check time, and an
  informal "2026-08-01 ~0x:xx PDT" wall-clock labelling convention in
  `orchestrator_flow.md`. Not a new distinct class, no scored quantity
  affected; this report uses filesystem-relative epoch deltas throughout,
  never the flow log's lexical labels.
- **Gates**: G1-r2 PASS, G2-r2 PASS, G3-r2 PASS (all 2026-07-31,
  `state/gates.md`) — round cleared for stream launch. Unchanged this run.
- **Round-1 top-3 seed confirms**: NOT this maintainer's scope (round-1 jobs
  visible in `squeue` as `r1-*`, PENDING) — separate round, separate report.
- No reopen candidates on any of the 10 cards. No `blocked.md` file exists
  (no stream has ever blocked). No abandoned streams — none are possible yet
  (r2s1 now at batch 3 with 2 clean closes B1/B2; r2s2 at batch 2 with a
  clean B1 close; r2s3/r2s4 at batch 3, all prior batches clean closes — no
  skip/block history anywhere). `state/streams/` directory still does not
  exist — consistent with no abandonments ever being needed.
- Repo hygiene: `git status --short .` (round root, excluding `worktrees/`),
  checked twice ~4 min apart with identical results: 5 modified files —
  `experiment_cards/r2s1_direct/batch_2/B2.json` (the register-turn
  completion itemized above; a mid-run auto-sync commit captured an earlier
  partial version, so this is not a double-count), `state/orchestrator_flow.md`,
  `state/r2s1_direct/current_batch.txt`, `state/r2s1_direct/current_stage.txt`
  (stream-advance-to-batch-3 bookkeeping), `tools/index.md` (the 2 new tool
  entries) — plus 2 untracked new tool files (`tools/blend_decorrelation_payoff.py`,
  `tools/selection_set_vs_window_audit.py`). None of these 7 were touched by
  this maintainer. This maintainer's own writes this run: `index.md`,
  `state/maintainer_report.md` (`state/timing_ledger.json` content unchanged,
  gitignored, not part of the git-status comparison). No Write call this run
  touched `experiment_cards/`.
