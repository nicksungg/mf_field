# MFFP Autoresearch Round 2 — Dashboard (updated 2026-08-01T17:24:00Z)

**Fourth maintainer walk since the operator halt/resume cycle.**
Halt landed 2026-08-01T01:31:54Z (commit `10d4e4c`), resume landed
2026-08-01 ~08:1x PDT (commit `b80e622`).
This run's headline: the **`r2s3_lf_train_signal-B3` stall flag from the
last walk is resolved** — the orchestrator's relaunch of the two missing
F4 legs (`ch_d0`, `ifc`) landed, all 33 legs are now present, and the
mechanism-analyzer produced a full F4 verdict under all three
candidate-set readings; the card's `reanalysis_progress` advanced
`turn_1`→**`turn_2`**.
`r2s4_diag-B3`'s mechanism-analyzer also completed turn 2
(`turn_1`→**`turn_2`**), landing a corrected-quantity re-read of F4a and
opening a turn-3 question.
`r2s2_stacked`'s websearcher finished a full 5-iteration batch-3 websearch
report (stream not yet card-drafted).
**Mid-walk delta, caught during the pre-return checklist re-verification**:
`r2s1_direct-B3`'s builder finished — status `drafted`→**`built`**
(card mtime 17:23:11Z, landed after this run's initial pass), submit
scripts and `build_commit` now populated, `job_ids` still empty (not yet
submitted to SLURM). No live SLURM jobs, no other live agent processes at
this final check.

## Streams

| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r2s1_direct | 23.0636 (best_floor_panel_geomean) | **3** | r2s1_direct-B1 **complete**; r2s1_direct-B2 **complete**; r2s1_direct-B3 **built** *(new this run)* | B1/B2 unchanged. **B3: `drafted`→`built` this run** (caught mid-walk during pre-return re-verification, card mtime 17:23:11Z). Builder finished a from-scratch build of `models_r2/r2s1_stagefree_permode` (11 modules, fresh per the halt-window rebuild directive; prior partial output archived to `state/halt_partials/r2s1_B3/`, not consulted). Both contract-smoke legs passed (helmholtz panel_geomean_skill 3.815; ifc_poisson LOO variant 10.599), all 5 build gates (G-A..G-E) fire per the emitted result JSON, registration dispatch is grep-verified free of bare `F.interpolate`/`scipy.zoom`. `scripts_path` (submit.sh, submit_seeds_2_3.sh, 01_train_eval.sh) and `build_commit` (`2b030f0`) now populated; **`job_ids` still empty — not yet submitted to SLURM** | **0 live SLURM**; **0 live local process** (builder finished, no submission yet) | `drafted`→`built` this run (mid-walk) |
| r2s2_stacked | 23.0636 (best_floor_panel_geomean) | 2 (stream-state stale; batch-3 websearch already complete) | r2s2_stacked-B1 **complete**; r2s2_stacked-B2 **complete** | B1/B2 unchanged. **New this run**: `websearches/r2s2_stacked/batch_3/` landed a full 5-iteration + report.md websearch (finished ~17:14Z, after last run's RUN END) — surveys prior art for 3 candidate B3 directions, flags 2 as `preempted (cite)` (arXiv 2511.19794, 2508.05831) and identifies "switch off the learned corrector out-of-fold while a closed-form stage carries the gain" as the stream's only unpublished/publishable content. `state/r2s2_stacked/current_batch.txt` still reads "2" and `current_stage.txt` still reads the stale B2-register-turn text (same staleness flagged 3 runs running) — orchestrator-owned, not yet refreshed despite the batch-3 websearch already running to completion | **0 live SLURM**; **0 live local process** (websearcher finished, no brainstormer/builder started yet) | Batch-3 websearch complete (new) |
| r2s3_lf_train_signal | 23.0636 (best_floor_panel_geomean) | **3** | r2s3_lf_train_signal-B1 **complete**; r2s3_lf_train_signal-B2 **complete**; r2s3_lf_train_signal-B3 **analyzing** | B1/B2 unchanged. **B3 stall resolved this run**: last run's flagged turn-2 F4 audit gap (12/13 legs, `ch_d0`+`ifc` missing after an external `timeout 1200` wrapper expired) is fixed — `scratchpad/turn2_f4/` now has all F4-relevant leg JSONs including the previously-missing `f4_ch_d0.json` and `f4_ifc.json` (mtimes ~10:12-10:19 PDT, after last run's RUN END), and `reanalysis_turn_2_f4_verdict.json` renders the F4 clause under 3 candidate-set readings (`verbatim_max_mce_spread`: FALSIFIED; `worst_draw_vs_mce`/`mce_only`: NOT FALSIFIED) plus a channels plot. Card `reanalysis_progress` **`turn_1`→`turn_2`** (card mtime 17:18:25Z, after last run's window); part 6 still null (verdict not yet written to card — that is the mechanism-analyzer's next step, not this maintainer's) | **0 live SLURM** (jobs terminal); **0 live local process** (turn-2 F4 script and polling loop both exited cleanly, no longer running) | Stall recovered: F4 audit complete, `reanalysis_progress`→turn_2 |
| r2s4_diag | **19.8178** (certified_3seed_panel_geomean, CI95 [19.385, 20.527]) | **3** | r2s4_diag-B1 **complete**; r2s4_diag-B2 **complete**; r2s4_diag-B3 **analyzing** | B1/B2 unchanged. B3: mechanism-analyzer's turn 2 completed this cycle (`reanalysis_turn_2_results.md` + a follow-on `reanalysis_turn_2b_f4a.py` sub-analysis, mtimes up to 10:14-10:16 PDT). Turn 2 re-derives F4a under a corrected "teacher-target term" quantity (the carded `advantage_reachable` mixed two unrelated effects that nearly cancelled on helmholtz); under the correction, 3 estimators now agree to 0.0018 skill units and F4a reads as a **definitional artifact, not a measurement failure** — F3 stands substantively, F1/F2 survive. Turn 2 explicitly opens a turn-3 question (spatial structure of the untouched `advantage_unreachable`, 13.12-136.18 skill units). Card `reanalysis_progress` **`turn_1`→`turn_2`** (card mtime 17:16:34Z, after last run's window); part 6 still null | **0 live SLURM** (jobs terminal); **0 live local process** (turn-2 script exited, no turn-3 process started yet) | Turn 2 complete, `reanalysis_progress`→turn_2, turn 3 opened as next step |

**Anchor note**: r2s4_diag remains the only stream with a *certified* anchor
(`certified_3seed_panel_geomean`, 19.8178, replacing the training-free
floor) — r2s1_direct, r2s2_stacked, r2s3_lf_train_signal remain on the
launch-time `best_floor_panel_geomean` anchor (23.0636, `certified_utc`
2026-07-31T14:20:17Z, unchanged). No anchor deltas this run — all 4
`state/anchors/*.json` files' mtimes predate this run's entire window.
All anchors rendered verbatim from `state/anchors/*.json`.

## Running / pending jobs

| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| (none — 0 live SLURM `r2-*` jobs) | — | — | — | — |

**0 live `r2-*` SLURM jobs** at this check (`squeue` shows only 2 unrelated
interactive `bash` jobs, re-checked after r2s1_direct-B3's build completion
was caught; `sacct` 2-day window shows 16 `r2-*` jobs, all COMPLETED 0:0,
identical job-ID set to the timing ledger — no new completions since the
last walk, no upsert needed). `r2s1_direct-B3` is `built` with `job_ids`
still empty — no submission has happened yet, so no new ledger entry is
due. **0 live non-SLURM agent processes** matching last run's tracked
PIDs at this final check — a broad `ps aux` sweep found no
`reanalysis_*`, `contract_smoke*`, `write_card.py`, or websearch-driver
processes running for any of the 4 streams; all this-cycle background
work (r2s3's F4 audit, r2s4's turn-2 script, r2s2's websearcher,
r2s1's builder) completed and exited cleanly since the last walk.

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

`r2s3_lf_train_signal-B3` (`analyzing`, part 5 written/falsified, part 6
pending, `reanalysis_progress: turn_2`, F4 audit now complete across all 33
legs) and `r2s4_diag-B3` (`analyzing`, part 5 written/falsified,
`reanalysis_progress: turn_2` with turn 3 opened next) are all actively
open but neither has part 7 written — not listed here until each card
itself closes. `r2s1_direct-B3` is now `built` (not yet `complete` — no
part 5, `job_ids` empty, awaiting SLURM submission) — not listed here
until it closes.

## Flags

- **`r2s1_direct-B3` finished building this run (mid-walk delta)**: caught
  during the pre-return checklist re-verification, not the initial pass —
  same lesson as prior runs' mid-checklist catches. Status `drafted`→
  `built`, `build_commit` `2b030f0`, submit scripts populated,
  `job_ids` still `[]`. No SLURM submission has happened yet; the next
  card-visible event will be a `r2-r2s1_direct-B3-s{SEED}` job appearing
  in `squeue`/`sacct`.
- **`r2s3_lf_train_signal-B3` stall from the last walk is resolved**: the
  two missing F4 legs (`ch_d0`, `ifc`) landed in
  `scratchpad/turn2_f4/` (all 33 legs present), and
  `reanalysis_turn_2_f4_verdict.json` adjudicates the F4 clause under all
  3 candidate-set readings recorded last run
  (`verbatim_max_mce_spread`: **FALSIFIED**; `worst_draw_vs_mce` and
  `mce_only`: **NOT FALSIFIED**) — this is a genuine reading-sensitivity
  finding, not an unresolved gap. Card `reanalysis_progress` advanced
  `turn_1`→`turn_2`. Part 6 (verdict written to card) is the
  mechanism-analyzer's next step, still open.
- **`r2s4_diag-B3` turn 2 complete, turn 3 opened**: the corrected
  "teacher-target term" re-read of F4a found the card's original
  `advantage_reachable` quantity was mis-specified whenever the
  counterfactual estimator differs from the primary arm (two large,
  nearly-cancelling terms on helmholtz); under the correction 3 estimators
  now agree to 0.0018 skill units and F4a is read as a **definitional
  artifact**, not a measurement failure — F3 stands substantively, F1/F2
  survive. Turn 2 explicitly hands off a turn-3 question (spatial
  structure of the untouched `advantage_unreachable`, 13.12-136.18 skill
  units) — not yet started at this check (no live process).
- **`r2s2_stacked` batch-3 websearch complete**: full 5-iteration +
  report.md landed (~17:14Z), surveys prior art, flags 2 of 3 candidate B3
  directions as `preempted (cite)`, and identifies the "switch off the
  learned corrector out-of-fold, closed-form carries the gain" contrast as
  the stream's only unpublished/publishable B3 content. No card exists yet
  (brainstormer/builder not started) — expected next per the normal
  pipeline order.
- **Round-level instrument-defect pattern (carried forward, now 3
  independent confirmations)**: `r2s1_direct`'s post-hoc-blend-stage
  instrument-error class, `r2s2_stacked-B2`'s statistic
  mis-specification/estimator-bias findings (centring bug, frozen-vs-refit
  mismatch, unit mispricing — landed with part 7), and
  `r2s3_lf_train_signal-B3`'s knife-edge spread-vs-mce clause reading
  (this run: now resolved into a documented 3-reading adjudication) remain
  worth folding into the same round-report action once both B3
  mechanism-analyzers land part 6. `r2s4_diag-B3`'s turn-2 finding (the
  carded `advantage_reachable` mixing two unrelated effect terms) is a
  4th independent instance of the same instrument-sensitivity class —
  worth adding to that round-report action item.
- **Timing ledger**: **unchanged this run** — 16 entries, identical
  job-ID set to the union of all cards' `job_ids` (0 new completions since
  the last walk; `r2s1_direct-B3` has no `job_ids` yet either). Re-validated
  as parseable JSON.
- **Analyzer caveat (r2s1_direct-B1, from code-review)**, carried forward:
  the D3 certificate's aleatoric-floor estimate is window-sensitive — at
  the recipe's window (1000 closest pairs), `ext__helmholtz_2d` reads
  1.200, worse than the zero predictor. Must not be reported as a ceiling
  for helmholtz; `allen_cahn`'s ceiling must be reported as a range
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
- No reopen candidates on any of the 10 cards. No `blocked.md` file exists
  (no stream has ever blocked). **No abandoned streams** — none qualify
  (r2s1/r2s3/r2s4 at batch 3 with clean prior closes; r2s2 at batch 2
  card-wise / batch 3 websearch-wise, both prior batches complete — no
  skip/block history anywhere). `state/streams/` directory still does not
  exist — consistent with no abandonments ever being needed.
- **Stale orchestrator-owned file noted (not actionable by this
  maintainer), now 3 runs running**: `state/r2s2_stacked/current_stage.txt`
  still reads "B2 register turn ... part 7 + tool promotion in progress"
  even though B2 closed 2 runs ago with part 7 written, and the stream has
  since progressed all the way to a completed batch-3 websearch —
  flagging again for the orchestrator to refresh on its next pulse.
- Repo hygiene: `git status --short .` on the round root (excluding
  `worktrees/`) at this final check: `experiment_cards/r2s1_direct/batch_3/B3.json`
  (M — `drafted`→`built`, builder-owned, caught mid-walk),
  `experiment_cards/r2s3_lf_train_signal/batch_3/B3.json`
  (M — `reanalysis_progress: turn_1`→`turn_2`, mechanism-analyzer-owned),
  `experiment_cards/r2s4_diag/batch_3/B3.json` (M — same field, same
  progression, mechanism-analyzer-owned), `index.md` + `state/maintainer_report.md`
  (M — this maintainer's own writes this run), `websearches/r2s2_stacked/batch_3/`
  (?? — the websearcher's 7 new files). No Write call this run touched
  `experiment_cards/`. `state/timing_ledger.json` untouched (no new
  entries to upsert — no SLURM job exists yet for the newly-built
  r2s1_direct-B3; gitignored so it never shows in this diff regardless).
