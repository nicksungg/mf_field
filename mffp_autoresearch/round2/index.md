# MFFP Autoresearch Round 2 — Dashboard (updated 2026-08-01T16:30:30Z)

**First maintainer walk since the operator halt/resume cycle.**
Halt landed 2026-08-01T01:31:54Z (commit `10d4e4c`): 3 crons deleted,
2 in-flight agents killed mid-turn (r2s1-B3 builder, r2s2-B2 register turn),
2 SLURM jobs left running per operator instruction (66196690, 66197075).
Resume landed 2026-08-01 ~08:1x PDT (commit `b80e622`): both left-running
jobs confirmed COMPLETED, the r2s4-B3 signed-reach probe fix applied,
r2s1-B3 partials archived to `state/halt_partials/r2s1_B3/` (not reused),
5 agents re-dispatched, 3 crons re-created. All 4 background agents named in
this run's briefing are confirmed live/landed below — none treated as
abandoned.

## Streams

| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r2s1_direct | 23.0636 (best_floor_panel_geomean) | **3** | r2s1_direct-B1 **complete**; r2s1_direct-B2 **complete**; r2s1_direct-B3 **drafted** | B1/B2 unchanged (complete). B3: websearcher + brainstormer both complete since the last walk (`brainstormer/r2s1_direct/batch_3/` now holds `iteration_1.md`, `report.md`, `summary_so_far.md` — B3 chosen over close per the brainstormer's 4 grounds in `orchestrator_flow.md`); starter landed a TBD-free `B3.json` (family `models_r2/r2s1_stagefree_permode`, gap-card re-pricing the Bates-Granger blend-stage instrument defect); **builder now rebuilding fresh** (halt-killed mid-build, partials archived, worktree git-clean atop `9e10d41`) — `models_r2/r2s1_stagefree_permode/{basis,common,config,maps}.py` + `manifest.json` and 2 scratchpad preflight JSONs on disk as of this check, live and progressing (not stalled) | **0 live SLURM** for this stream; **1 live local process** (builder, confirmed via fresh worktree mtimes ~6-12 min old) | Builder in progress post-resume (fresh rebuild, no card-visible checkpoint yet) |
| r2s2_stacked | 23.0636 (best_floor_panel_geomean) | **2** | r2s2_stacked-B1 **complete**; r2s2_stacked-B2 **analyzing** | B1 unchanged (complete). B2: still `reanalysis_progress: turn_3`, part 7 null — mechanism turn 3 (decision-cost/UNITS-defect audit) already landed per `orchestrator_flow.md` (closed-form LSI Wiener explains 100/97/77/33% of gain; CNN rejected OOF; B1's corrector-futility calibration off by 7-180x; the 0.05 relative floor rule prices 10-817x mce — a UNITS defect) but not yet visible on-card; **register turn re-dispatched post-resume** (halt killed it mid-tool-promotion before part 7 was written) — confirmed live via `ps aux`, PID 1482785, running `tools/zero_gradient_stage_ladder.py` toolcheck against `worktrees/r2s2_stacked/B2/models_r2/r2s2_correctability`, ~15 min elapsed, not stalled; `tools/index.md` re-verified clean (no partial/duplicate entry from the killed turn) | **0 live SLURM** for this stream; **1 live local process** (register-turn toolcheck) | Register turn re-dispatched post-resume, in progress |
| r2s3_lf_train_signal | 23.0636 (best_floor_panel_geomean) | **3** | r2s3_lf_train_signal-B1 **complete**; r2s3_lf_train_signal-B2 **complete**; r2s3_lf_train_signal-B3 **analyzing** | B1/B2 unchanged (complete). **B3: `running` → `analyzing` this run** — initial-analyzer landed post-resume: job 66196690 (COMPLETED, 54.95 min, 33/33 legs, clean seam checks) transcribed into part 5. Panel geomean skill 17.1150 (primary arm `A1_lf_cov`), **falsification_verdict: falsified** — F1 clause needs 5/6 datasets, only 3/6 pass (`ifc_poisson`, `sharp__cahn_hilliard`, `sharp__fisher_kpp_2d` pass; `sharp__allen_cahn_2d`/`ext__helmholtz_2d` fail on the in-job 3-draw spread term, `sharp__phase_field_crystal_2d` fails on a sign-wrong effect — LF supply measured to HURT there). Card itself flags a knife-edge: if the clause were read as mce-only (dropping the spread term) 5/6 would pass and F1 would read CONFIRMED — explicitly flagged for the mechanism-analyzer. `cratered_verdict` fires on its 3rd limb only ("clause already fired decisively") — the run/measurement itself is clean, not a failure. Part 6 not yet written; `reanalysis_progress` still null — mechanism-analyzer not yet dispatched | **0 live SLURM** (job terminal); 0 live local processes for this card at this check | `running` → `analyzing` (initial-analyzer landed, falsified verdict, mechanism-analyzer not yet dispatched) |
| r2s4_diag | **19.8178** (certified_3seed_panel_geomean, CI95 [19.385, 20.527]) | **3** | r2s4_diag-B1 **complete**; r2s4_diag-B2 **complete**; r2s4_diag-B3 **analyzing** | B1/B2 unchanged (complete). **B3: `running` → `analyzing`** — initial-analyzer landed pre-resume (per resume-checklist item 4, ran with the signed-reach probe fix already applied): job 66197075 (COMPLETED, 91.57 min / 43.6% of its 210-min request, clean logs — flagged by the analyzer itself for this ledger) transcribed into part 5. Panel geomean skill 19.1728 (seed 0, primary arm `T0_cond_only`), **falsification_verdict: falsified**; delta vs the certified B1 anchor is -0.645 (nominally better, lower-is-better convention) but below the panel `min_claimable_effect` 1.1419 — reads as reproducing inside the carded 19.3-20.5 expected band, not a new claim (this is a diagnostic reproduction column, `cratered_verdict: n/a`). Guard flags on `fluid`/`heat_local` both traced to the 2-epoch guard leg being bit-identical to B2's same-dataset guard (no B3-introduced regression). Part 6 not yet written — **mechanism-analyzer turn 1 dispatched this cycle**, confirmed live via `ps aux`, PID 1525518, loading `preds_oof`/`preds_test` npz for `sharp__cahn_hilliard` | **0 live SLURM** (job terminal); **1 live local process** (mechanism-analyzer turn 1) | `running` → `analyzing` (initial-analyzer landed, falsified verdict, mechanism-analyzer turn 1 dispatched) |

**Anchor note**: r2s4_diag remains the only stream with a *certified* anchor
(`certified_3seed_panel_geomean`, 19.8178, replacing the training-free floor)
— r2s1_direct, r2s2_stacked, r2s3_lf_train_signal remain on the launch-time
`best_floor_panel_geomean` anchor (23.0636, `certified_utc`
2026-07-31T14:20:17Z, unchanged). No anchor deltas this run — all 4
`state/anchors/*.json` files' mtimes predate this run's entire window.
All anchors rendered verbatim from `state/anchors/*.json`.

**This run's headline**: **2 card-status deltas**, both `running` →
`analyzing` (`r2s3_lf_train_signal-B3` and `r2s4_diag-B3`, both via their
initial-analyzers landing post-halt/pre-or-post-resume respectively, both
returning a **falsified** verdict on part 5). Both new SLURM jobs
(66196690, 66197075) upserted into the timing ledger. 3 background
non-SLURM agents confirmed live and progressing (not stalled, not
abandoned): `r2s1_direct-B3` builder (fresh rebuild), `r2s2_stacked-B2`
register turn (re-dispatch), `r2s4_diag-B3` mechanism-analyzer turn 1
(freshly dispatched). No card reached `complete` this run. No reopen
candidates, no new guard-trip auto-rejects, no stream abandonment.

## Running / pending jobs

| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| (none — 0 live SLURM `r2-*` jobs) | — | — | — | — |

**0 live `r2-*` SLURM jobs** at this check (`squeue` shows only 2 unrelated
interactive `bash` jobs; `sacct` 2-day window shows 16 `r2-*` jobs, all
COMPLETED 0:0 — the 2 newest, 66196690 and 66197075, both landed during the
halt window per the operator's explicit "leave these running" instruction
and are now ledgered). **3 live local (non-SLURM) agent processes** at this
check, none stalled: `r2s1_direct-B3` builder (fresh worktree activity),
`r2s2_stacked-B2` register-turn toolcheck (PID 1482785), `r2s4_diag-B3`
mechanism-analyzer turn 1 (PID 1525518).

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

`r2s2_stacked-B2` (`analyzing`, `reanalysis_progress: turn_3`, register turn
re-dispatched post-resume, part 7 still null), `r2s3_lf_train_signal-B3`
(`analyzing`, part 5 written/falsified, part 6 pending, mechanism-analyzer
not yet dispatched) and `r2s4_diag-B3` (`analyzing`, part 5 written/
falsified, mechanism-analyzer turn 1 in progress) are all actively open but
none has part 7 written — not listed here until each card itself closes.
`r2s1_direct-B3` remains `drafted` (builder rebuilding fresh post-halt, no
part 5 yet).

## Flags

- **`r2s3_lf_train_signal-B3` initial-analyzer landed this run**:
  `running` → `analyzing`, falsified verdict on F1 (3/6 datasets pass a
  5-of-6 clause), decisive on a knife-edge spread-vs-mce reading in the
  clause text — the card itself flags this for the mechanism-analyzer
  (mce-only reading would flip 5/6 datasets to pass). Sign-wrong effect on
  `sharp__phase_field_crystal_2d` (LF supply measured to HURT) is the
  binding failure independent of the spread-vs-mce question. Mechanism-
  analyzer not yet dispatched for this card — worth watching next cycle.
- **`r2s4_diag-B3` initial-analyzer landed pre-resume, mechanism-analyzer
  turn 1 dispatched this cycle**: falsified verdict, but reads as a clean
  reproduction inside the certified B1 band (delta -0.645, below the panel
  min_claimable_effect 1.1419) rather than a new negative claim — this is a
  diagnostic reproduction column (`cratered_verdict: n/a`). Both guard
  flags (`fluid` 2.25x, `heat_local` 16.74x) traced to the 2-epoch guard leg
  being bit-identical to B2's same-dataset guard leg — not a B3-introduced
  regression.
- **`r2s2_stacked-B2` register turn re-dispatched post-resume**: the halt
  killed it mid-tool-promotion before part 7 was written; re-verified
  `tools/index.md` clean (no partial/duplicate entry survived the kill);
  confirmed live and progressing this run (PID 1482785, toolcheck ladder
  script, ~15 min elapsed).
- **`r2s1_direct-B3` builder rebuilding fresh post-halt**: prior partials
  (from the killed mid-build) archived to `state/halt_partials/r2s1_B3/`
  and confirmed NOT reused — worktree is git-clean atop base `9e10d41` with
  only fresh untracked `models_r2/`, `notes/`, `scratchpad/` content, all
  within ~6-12 min of this check. Family under construction:
  `models_r2/r2s1_stagefree_permode` (gap-card re-pricing the Bates-Granger
  blend-stage instrument defect via a stage-free per-mode closed-form head).
- **Stale orchestrator-owned files (informational, not this maintainer's to
  fix)**: all 4 `state/{stream}/current_stage.txt` files still read the
  halt-window placeholder ("HALTED by operator 2026-08-01 ...") even though
  2 of the 4 relevant cards have since advanced past that point
  (r2s3-B3/r2s4-B3 initial-analyzers landed). Worth the orchestrator
  refreshing these on its next pulse.
- **Real lead flagged inside `r2s2_stacked-B2` turn 2** (not yet a card
  claim, carried forward): a training-free interior-k LF average reportedly
  beats the trained corrector on `allen_cahn`/`cahn_hilliard` — worth
  tracking into part 6/7 once it lands on-card.
- **Round-level instrument-defect pattern (carried forward, now potentially
  a 3rd stream)**: `r2s1_direct`'s post-hoc-blend-stage instrument-error
  class (part 7, reinforced by the B3 websearch's Bates-Granger finding) and
  `r2s2_stacked-B2`'s statistic mis-specification/estimator-bias findings
  were already 2 independent streams flagging instrument defects;
  `r2s3_lf_train_signal-B3`'s knife-edge spread-vs-mce clause reading (this
  run) is a related but distinct instrument-sensitivity finding, worth
  folding into the same round-report action once B3 mechanism-analyzers
  land on both streams.
- **Timing ledger**: **2 new entries upserted this run** — job 66196690
  (`r2s3_lf_train_signal-B3-s0`, family `r2s3_coverage_panel`, 54.95 min on
  h200) and job 66197075 (`r2s4_diag-B3-s0`, family `r2s4_b3_projection`,
  91.57 min on h200, 43.6% of the 210-min request, clean logs per the
  initial-analyzer's own flag). Now **16 entries** total, JSON re-validated
  as parseable.
- **Analyzer caveat (r2s1_direct-B1, from code-review)**, carried forward:
  the D3 certificate's aleatoric-floor estimate is window-sensitive — at the
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
  visible in `squeue` as `r1-*` historically; none currently queued) —
  separate round, separate report.
- No reopen candidates on any of the 10 cards. No `blocked.md` file exists
  (no stream has ever blocked). **No abandoned streams** — none qualify
  (r2s1/r2s3/r2s4 at batch 3 with clean prior closes; r2s2 at batch 2 with a
  clean B1 close — no skip/block history anywhere). `state/streams/`
  directory still does not exist — consistent with no abandonments ever
  being needed.
- Repo hygiene: `git status --short experiment_cards/` shows exactly 2
  modified files this run, both legitimate other-agent (initial-analyzer)
  writes: `experiment_cards/r2s3_lf_train_signal/batch_3/B3.json` and
  `experiment_cards/r2s4_diag/batch_3/B3.json` (both `running`→`analyzing`
  with part 5 populated). This maintainer's own writes this run: `index.md`,
  `state/maintainer_report.md`, `state/timing_ledger.json` (2 entries
  upserted). No Write call this run touched `experiment_cards/`.
