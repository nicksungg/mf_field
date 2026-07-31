# MFFP Autoresearch Round 2 — Dashboard (updated 2026-07-31T21:00:26Z)

## Streams

| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r2s1_direct | 23.0636 (best_floor_panel_geomean) | **2** | r2s1_direct-B1 **complete**; B2 in progress | **B1: unchanged, still COMPLETE.** **B2 builder continues self-testing**: new module `models_r2/r2s1_selected_form/wiener.py` plus a spectral/spatial equivalence self-test (`scratchpad/test_wiener_equivalence.py`/`.log`, all bands `identical=True`, max error ~1e-15 to 1e-18 — clean pass). Checkpoint-resume correctness now under active test (`scratchpad/_resume_tmp/a1.json`/`a2.json`, 2 vs 4 epochs on `sharp__sod_1d`). **Live PIDs confirmed**: `smoke_eval.py --dataset_name sharp__sod_1d --epochs 4 --out scratchpad/_resume_tmp/a2.json` and `scratchpad/test_resume.py` running at check time. Card itself unchanged on disk (`status: drafted`, `job_ids: []`, no builder handoff note yet) | 0 live (no B2 jobs submitted yet) | `models_r2/r2s1_selected_form/wiener.py` + resume self-test new this run |
| r2s2_stacked | 23.0636 (best_floor_panel_geomean) | **2** | r2s2_stacked-B1 **complete**; r2s2_stacked-B2 **drafted** (new this run) | **B1: unchanged, still COMPLETE.** **B2 is a new card this run**: starter SUCCESS (14/14, no TBDs) drafted `r2s2_correctability`, a diagnostic calibrating the coherence threshold + DPI closure measurement via two training-free intermediate ladders (oracle spectral mix, test-legal kNN-LF ladder) with the frozen DC corrector refit per rung. Builder dispatched; worktree `worktrees/r2s2_stacked/B2/` freshly checked out (full repo tree materialized, no `models_r2/` yet — earliest-stage B2 of any stream) | 0 live (no B2 jobs submitted yet) | `experiment_cards/r2s2_stacked/batch_2/B2.json` new this run (untracked, other-subagent write) |
| r2s3_lf_train_signal | 23.0636 (best_floor_panel_geomean) | **2** | r2s3_lf_train_signal-B1 **complete**; B2 in progress | **B1: unchanged, still COMPLETE.** **B2 builder wrote its handoff this run, then kept working**: `notes/handoff_experiment_builder.md` (21:10:00Z) validates the from-scratch family bit-for-bit against B1's published `ifc_poisson` numbers (`ref_linear_hfonly` 3.4744, rung-32 ladder 0.2427, oracle null-energy 0.18828 — all exact matches); flags for the reviewer: `ref_linear_mf` ties to rung 8 not rung 32 on ifc (all rungs affine to ~3e-8), penalty amplitude gain 0.551 reported-not-applied. **After** the handoff, builder continued running guard-dataset debug legs (`dbg_sod_A2`, `dbg_ch_A2`, `dbg_ch_A3`, `dbg_fk_A2`). **Live PID confirmed**: `smoke_eval.py --dataset_name sharp__cahn_hilliard --out scratchpad/dbg_ch_A2.json` (arm `A2_lf_cov_null`) running at check time. Worktree branch still uncommitted (only the launch commit `9e10d41`). Card itself unchanged on disk (`status: drafted`, `job_ids: []`, `build_commit: null`) | 0 live (no B2 jobs submitted yet) | `notes/handoff_experiment_builder.md` new this run |
| r2s4_diag | **19.8178** (certified_3seed_panel_geomean, CI95 [19.385, 20.527]) | **2** | r2s4_diag-B1 **complete**; r2s4_diag-B2 **running** (seed 0) | **B1: unchanged, still COMPLETE.** **B2 advanced fully through code-review and into SLURM this run**: code-reviewer verdict **SUGGEST (6/6)** — all sub-checks PASS/SUGGEST, no FAIL; headline adjudication ruled the card's 3-seed design **ADMISSIBLE** under program.md §12.4's standing training-diagnostic exception, and recommended the normal seed-0 gate (not B1's parallel 3-seed submit) — honored. **Orchestrator then submitted seed 0**: job **66181609** (`r2-r2s4_diag-B2-s0`, h200), now `status: running` on the card (`job_ids: ['66181609']`) | **1 live**: `66181609` RUNNING on `hpc-sm-01-04`, ~26s elapsed at check | card `status` → `reviewed_suggest` → `running`, `job_ids` set this run (git-diff confirmed, not this maintainer's write) |

**Anchor note**: r2s4_diag remains the only stream with a *certified* anchor
(`certified_3seed_panel_geomean`, 19.8178, replacing the training-free floor)
— r2s1_direct, r2s2_stacked, r2s3_lf_train_signal remain on the launch-time
`best_floor_panel_geomean` anchor (23.0636, `certified_utc` 2026-07-31T14:20:17Z,
unchanged). No anchor deltas this run. All anchors rendered verbatim from
`state/anchors/*.json`.

**This run's headline**: **the round's 8th card drafted** (`r2s2_stacked-B2`,
all four streams now have a live B2 slot in the pipeline) and **the round's
first new SLURM submission since batch 1** — `r2s4_diag-B2` cleared code
review with a SUGGEST verdict (3-seed design ruled admissible under program
§12.4) and its seed-0 job (`66181609`) is now running, ending an 8-run streak
of zero live `r2-*` jobs. r2s1_direct-B2 and r2s3_lf_train_signal-B2 both
continue active builder self-test/debug with fresh live PIDs; r2s3's builder
also produced its handoff note this run (validated exactly against B1's
published numbers) but kept working past it and has not yet committed or
flipped card status.

## Running / pending jobs

| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| 66181609 | r2s4_diag-B2 (seed 0) | RUNNING | ~26s | hpc-sm-01-04 |

2 local (non-SLURM) self-test/debug processes confirmed live via `ps aux`:
r2s1_direct-B2 checkpoint-resume test (`sharp__sod_1d`, epochs 4) + its
driver `test_resume.py`; r2s3_lf_train_signal-B2 post-handoff debug run on
`sharp__cahn_hilliard` (arm `A2_lf_cov_null`). Unrelated interactive `bash`
jobs and round-1 `r1-*` jobs also visible in the queue — out of this
maintainer's scope, not itemized here.

## Completed cards

| Card | Type | Panel geomean skill (±CI) | Falsification verdict | Tools promoted |
|---|---|---|---|---|
| r2s4_diag-B1 | diagnostic | 19.8178 IQM, CI95 [19.385, 20.527] (3 seeds) | n/a (diagnostic — no falsification clauses); mechanism register complete, part 7 written | 2 tools, both correctly indexed: `tools/conditional_mean_collapse.py`, `tools/condition_predictability_ceiling.py` |
| r2s1_direct-B1 | model | 19.6444 (single seed 0, no CI yet) | **falsified in a split reading**: floors clause CONFIRMED (beats best floor on all 6 panel datasets, geomean −14.8% vs anchor) but the implicit architecture clause FALSIFIED — a ~156-parameter closed-form head reaches 19.0553/19.1666, statistically indistinguishable from the 15.9M-parameter shipped arm (0.52x the certified panel min_claimable_effect) | 2 tools, both correctly indexed: `tools/band_gain_counterfactual.py`, `tools/condition_identifiable_rank.py` |
| r2s3_lf_train_signal-B1 | model | 25.3919 (`rung_native`, single seed 0) | **falsified in a split reading**: F1 (primary, architecture) FALSIFIED with a 7.35-skill-unit sign inversion on `ifc_poisson`, traced to a shared-scaler confound; but the motivating INFORMATION claim is CONFIRMED — an architecture-free estimator recovers +3.2317 skill units from the same 170 disjoint LF rows (18.83% of the law's coefficient energy at cos 0.9993). F2 (native vs upsampled) survived; F3 (degeneracy) verdict depends on provisional vs re-certified floor thresholds (both recorded) | 2 tools, both correctly indexed: `tools/affine_ladder_voi.py`, `tools/posthoc_repair_ladder.py` |
| r2s2_stacked-B1 | model | 14.0756 (single seed 0, no CI yet; scored arm `frozen`; ~all margin from the unpaired `ifc_poisson` column) | clean negative with a measured mechanism, not a raw binary: the falsification clause was a conjunction that did **not** fire — conjunct 1 ("improve on `emul_only` by ≥2.0 skill units") **held** (measured improvement 0.0061, 326x below threshold) but conjunct 2 ("beat the NN-in-condition floor") **failed to hold** (beat it by 11.90 skill units, 130x the noise floor). Round-level headline (I8): a stacked intermediate representation is a re-parameterisation of the condition→HF hypothesis class, not a new information channel | 2 tools, both correctly indexed and register-confirmed: `tools/reachable_set_rank_audit.py`, `tools/surrogate_coherence_eligibility.py` |

## Flags

- **Card `status`/count deltas this run (both by other subagents — no card
  writes by this maintainer)**: **new card** `r2s2_stacked-B2` drafted
  (round's 8th card, all 4 streams now have a B2 slot in the pipeline);
  `r2s4_diag-B2` advanced `built` → `reviewed_suggest` → **`running`**
  (`job_ids: ['66181609']`) — code-review SUGGEST (6/6), 3-seed design ruled
  admissible, seed-0 job submitted. All other 6 cards unchanged: `r2s1_direct-B1`
  `complete`, `r2s1_direct-B2` `drafted`, `r2s2_stacked-B1` `complete`,
  `r2s3_lf_train_signal-B1` `complete`, `r2s3_lf_train_signal-B2` `drafted`,
  `r2s4_diag-B1` `complete`. `reopen_candidate` is `false` on all 8 cards.
- **First new SLURM submission since batch 1**: job `66181609`
  (`r2-r2s4_diag-B2-s0`) RUNNING on `hpc-sm-01-04` — ends an 8-consecutive-check
  streak of zero live `r2-*` jobs. Code-reviewer's adjudication: the card's
  in-job 3-seed spread is admissible as a paired-control estimate under
  program.md §12.4's drift-class rule, but B1's certified `min_claimable_effect`
  constants used a DIFFERENT randomization scope (seed varies init + batch
  order + the val split; B2 fixes the val split by `R2S3B2_SPLIT_SEED`) —
  flagged as an analyzer obligation (do not silently overwrite
  `state/noise_floor.json` with B2's spread without labeling the scope
  difference).
- **r2s1_direct-B2 builder progress**: new `wiener.py` module + a clean
  spectral/spatial equivalence self-test; checkpoint-resume correctness now
  under active live test (2 vs 4 epoch comparison on `sharp__sod_1d`). Card
  itself still `drafted`, `job_ids: []`, no builder handoff yet.
- **r2s3_lf_train_signal-B2 builder handoff written, then continued working**:
  handoff validates the family exactly against B1's published `ifc_poisson`
  numbers; two open watch-items flagged for the reviewer (rung-8-vs-32 tie,
  unapplied 0.551 penalty-amplitude gain). Worktree branch still uncommitted
  (only the launch commit present) — builder is still debugging guard
  datasets past its own handoff. The starter's forwarded env-key-count
  discrepancy (card says "23/25", lists 30 keys, carried forward several
  runs, unresolved) remains unaffected — key list stays authoritative.
- **Timestamp anomaly (r2s1_direct-B1, unchanged, carried forward)**:
  `review_notes[0].utc` still reads `2026-07-31T17:05:00Z` (ahead-of-clock
  relative to the review file's actual write time, first flagged several
  runs ago). No scored quantity affected. Remains the card's only
  unresolved caveat since it closed `complete`.
- **Timing ledger**: no new upsert this run (`66181609` is RUNNING, not yet
  COMPLETED; all 7 existing entries re-validated against current `sacct`
  output, still parseable JSON, no changes needed).
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
  item. The register turn's own ifc_poisson finding (LF field exactly affine
  in the 5-dim condition, ridge held-out 0.0000) independently corroborates
  r2s3-B1's affine-LOO finding (3.2e-08) — the ifc_poisson degeneracy is now
  cross-confirmed by two independent streams/estimators.
- **Analyzer caveat (r2s3_lf_train_signal-B1, from code-review)**, carried
  forward: the shared-max-abs-rungs scaler makes ifc_poisson's `rung_native`
  stage-1 loss ~42x amplitude-weighted toward rung 8 over HF (confound C1,
  card-locked design, not a build defect); F1 is epoch-matched but not
  step-matched (confound C2, ran IN FAVOR of the losing arm — does not
  explain away the inversion). r2s3-B2's card explicitly ships a
  step-matched, per-rung-scaled repair of both confounds this round.
- **Gates**: G1-r2 PASS, G2-r2 PASS, G3-r2 PASS (all 2026-07-31,
  `state/gates.md`) — round cleared for stream launch. Unchanged this run.
- **Round-1 top-3 seed confirms**: NOT this maintainer's scope (round-1 jobs
  visible in `squeue` as `r1-*`, PENDING) — separate round, separate report.
- No reopen candidates on any of the 8 cards. No `blocked.md` file exists (no
  stream has ever blocked). No abandoned streams — none are possible yet
  (all 4 streams are batch 2 as of this run, all with clean B1 closes, no
  skip/block history anywhere). `state/streams/` directory still does not
  exist — consistent with no abandonments ever being needed.
- Repo hygiene: `git status --short` on
  `mffp_autoresearch/round2/experiment_cards/` shows exactly 2 entries this
  run — `r2s4_diag/batch_2/B2.json` modified (the `built`→`reviewed_suggest`→
  `running` chain) and `r2s2_stacked/batch_2/` untracked (the new B2 card) —
  both other-subagent writes, neither touched by this maintainer. Non-card
  writes seen in the broader round2 tree, all other subagents' legitimate
  in-progress work: `state/orchestrator_flow.md`,
  `state/r2s2_stacked/current_stage.txt`, `state/r2s4_diag/current_stage.txt`,
  `brainstormer/r2s2_stacked/batch_2/` (new),
  `worktrees/{r2s1_direct/B2,r2s2_stacked/B2,r2s3_lf_train_signal/B2,r2s4_diag/B2}/{scratchpad,notes,scripts,models_r2,probes}/`.
  Confirmed no Write call this maintainer run touched `experiment_cards/`.
  `index.md` and `state/maintainer_report.md` are this maintainer's own
  writes. Most recent `round2: auto-sync` commit `5f74072`
  (2026-07-31T20:14:17Z), unchanged since last run — this run's deltas
  (including the new B2 card and the SLURM submission) not yet auto-synced.
