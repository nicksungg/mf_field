# MFFP Autoresearch Round 2 — Dashboard (updated 2026-07-31T21:56:37Z)

## Streams

| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r2s1_direct | 23.0636 (best_floor_panel_geomean) | **2** | r2s1_direct-B1 **complete**; B2 in progress | **B1: unchanged, still COMPLETE.** **B2 builder still in evidence-gathering, no card change**: guard-leg sweep continues, now running `smoke_eval.py` on `heat_local` (2 epochs) via `score_panel.py` — **live PID confirmed**: PID 142077 (~0:21 CPU time, `R` state), driven by a parent evidence-runs shell (PID 134531) that also ran the contract smoke (helmholtz) and small-N LOO (ifc_poisson/sod_1d) legs earlier in the same script. Builder handoff note (`notes/handoff_experiment_builder.md`) is present on disk (Wiener-filter family `models_r2/r2s1_selected_form`, 49/49 recipe knobs verified, provenance of every card TBD recorded) but its mtime (21:16:12Z) predates this run's window — carried-forward note-visibility discrepancy, see Flags. Worktree still fully uncommitted (`git status --short`: `models_r2/`, `notes/`, `scratchpad/`, `scripts/` all untracked; only the launch commit `9e10d41` on the branch). Card itself unchanged (`status: drafted`, `job_ids: []`, `build_commit: null`) | 0 live (no B2 jobs submitted yet) | Guard-leg evidence run (`heat_local`) in progress; handoff note present, no commit yet |
| r2s2_stacked | 23.0636 (best_floor_panel_geomean) | **2** | r2s2_stacked-B1 **complete**; r2s2_stacked-B2 **drafted** | **B1: unchanged, still COMPLETE.** **B2 builder wrote its handoff note this run** (`notes/handoff_experiment_builder.md`, mtime 21:47:03Z — within this run's window, ~9 min before this check) and launched its **first direct contract-smoke run**: `smoke_eval.py --dataset_name ext__helmholtz_2d --epochs 2 --seed 0` via `score_panel.py` — **live PIDs confirmed**: 137870 (driver shell), 137872 (`score_panel.py` wrapper), 137889 (`smoke_eval.py`, ~2:11 CPU time, `R` state). Family `models_r2/r2s2_correctability` (9 mechanism modules + `manifest.json` + `smoke_eval.py`, contract-complete since the prior run) still has no build commit (`git log` on the worktree branch: only launch commit `9e10d41`). Card unchanged (`status: drafted`, `job_ids: []`) | 0 live (no B2 jobs submitted yet) | Builder handoff written; first direct contract-smoke run in progress |
| r2s3_lf_train_signal | 23.0636 (best_floor_panel_geomean) | **2** | r2s3_lf_train_signal-B1 **complete**; r2s3_lf_train_signal-B2 **built** (new this run) | **B1: unchanged, still COMPLETE.** **B2 builder finished and committed this run** — **card delta**: `status` `drafted` → `built`. Build commit `945ee65` (message: "matched budget-equal +/-LF at N_hf~5 with LF at uncovered conditions (repaired-instrument neural channel)"), landed on the worktree branch on top of the launch commit. `build_notes` (fresh, not the earlier handoff-stage notes): oracle-discipline note (test-condition-fitted null-energy diagnostics kept structurally separate from every scored number, `_ORACLE` key suffix) and SLURM note (`--time 03:00:00`, sized from `r2s3_rung_supervised`'s 77.05 min/6-dataset comp in the timing ledger). `review_notes`/`debug_notes` both still empty — code-reviewer dispatched, no verdict yet (`state/r2s3_lf_train_signal/current_stage.txt`: "code-review (B2 dispatched 2026-08-01; build 945ee65, smoke green, resume bit-identical)"). No SLURM job submitted yet (awaiting review) | 0 live (awaiting code-review before submission) | Builder committed (945ee65); dispatched to code-reviewer |
| r2s4_diag | **19.8178** (certified_3seed_panel_geomean, CI95 [19.385, 20.527]) | **2** | r2s4_diag-B1 **complete**; r2s4_diag-B2 **analyzing** (new this run) | **B1: unchanged, still COMPLETE.** **B2's remaining two seeds COMPLETED this run** — **card delta**: `status` `running` → `analyzing` (`job_ids` unchanged, still `['66181609','66182923','66182924']`; all 3 now terminal). `sacct`: seed 1 (`66182923`) COMPLETED 00:17:12 elapsed, exit 0:0, ended 2026-07-31T21:35:51Z; seed 2 (`66182924`) COMPLETED 00:17:10, exit 0:0, ended 2026-07-31T21:35:49Z. Per-seed panel geomean skill: s0 19.2799, s1 20.2928, s2 20.0760 → 3-seed geomean **19.8829** (`orchestrator_flow.md` 03_accounting.sh output), matching B1's certified band [19.385, 20.527]. Orchestrator's initial-analyzer already ran (SUCCESS 6/6): **0/6 claimable transfer effects** (value-of-LF T1-T0 delta null at every N vs the certified min_claimable_effect) against a **5/5 claimable information-gap instrument** (ratios 13.5-95.3×) — an interpretable null, not a measurement failure; T0 reproduces the B1 certifier bit-identically on `ifc_poisson` (instrument validation); fold-fixed in-job spread explicitly **not** installed into `state/noise_floor.json` (per reviewer finding 3.2b). `state/r2s4_diag/current_stage.txt`: "mechanism-analysis (leads: helmholtz sign flip, ch info-gap 39.55, I-vs-T dissociation, N-scaling law)" — mechanism-analyzer now dispatched | 0 live (all 3 seeds COMPLETED) | Seeds 1-2 COMPLETED (17:12/17:10 elapsed); 3-seed geomean 19.8829; initial-analyzer landed an interpretable null; mechanism-analyzer dispatched |

**Anchor note**: r2s4_diag remains the only stream with a *certified* anchor
(`certified_3seed_panel_geomean`, 19.8178, replacing the training-free floor)
— r2s1_direct, r2s2_stacked, r2s3_lf_train_signal remain on the launch-time
`best_floor_panel_geomean` anchor (23.0636, `certified_utc` 2026-07-31T14:20:17Z,
unchanged). No anchor deltas this run. All anchors rendered verbatim from
`state/anchors/*.json`.

**This run's headline**: **two card-status deltas**. (1) `r2s4_diag-B2`'s
remaining two seeds (1, 2) both COMPLETED (`66182923`/`66182924`, ~17:1x min
each on h200), completing the round's first fully-3-seed B2 SLURM run; the
3-seed panel geomean (19.8829) reproduces B1's certified band, and the
orchestrator's initial-analyzer already landed a clean interpretable null on
the card's headline value-of-LF-as-training-signal question (0/6 claimable
transfer effects against a 5/5 claimable information-gap instrument) —
mechanism-analyzer now dispatched with 4 leads. (2) `r2s3_lf_train_signal-B2`'s
builder finished and committed (`945ee65`), moving the card `drafted` →
`built` and on to code-review. Sub-card (non-card-file) progress: `r2s2_stacked-B2`
wrote its builder handoff and launched its first direct contract-smoke run;
`r2s1_direct-B2` continues its guard-leg evidence-gathering run on
`heat_local`. Timing ledger upserted with 2 new entries (r2s4_diag-B2 seeds
1-2), now 10 entries.

## Running / pending jobs

| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| (none) | — | — | — | — |

**0 live `r2-*` SLURM jobs** this check (squeue + sacct cross-checked) — the
2 jobs live at last check (`66182923`/`66182924`) both transitioned to
COMPLETED this run; no new r2- job has been submitted since (r2s3_lf_train_signal-B2
awaits code-review before submission; r2s1_direct-B2/r2s2_stacked-B2 are
still in local builder territory). 3 local (non-SLURM) self-test/build
processes confirmed live via `ps aux`: r2s1_direct-B2 guard-leg evidence run
on `heat_local` (PID 142077), r2s2_stacked-B2's first direct contract-smoke
run on `ext__helmholtz_2d` (PID 137889). Unrelated interactive `bash` jobs
and round-1 `r1-*` jobs also visible in the queue — out of this maintainer's
scope, not itemized here.

## Completed cards

| Card | Type | Panel geomean skill (±CI) | Falsification verdict | Tools promoted |
|---|---|---|---|---|
| r2s4_diag-B1 | diagnostic | 19.8178 IQM, CI95 [19.385, 20.527] (3 seeds) | n/a (diagnostic — no falsification clauses); mechanism register complete, part 7 written | 2 tools, both correctly indexed: `tools/conditional_mean_collapse.py`, `tools/condition_predictability_ceiling.py` |
| r2s1_direct-B1 | model | 19.6444 (single seed 0, no CI yet) | **falsified in a split reading**: floors clause CONFIRMED (beats best floor on all 6 panel datasets, geomean −14.8% vs anchor) but the implicit architecture clause FALSIFIED — a ~156-parameter closed-form head reaches 19.0553/19.1666, statistically indistinguishable from the 15.9M-parameter shipped arm (0.52x the certified panel min_claimable_effect) | 2 tools, both correctly indexed: `tools/band_gain_counterfactual.py`, `tools/condition_identifiable_rank.py` |
| r2s3_lf_train_signal-B1 | model | 25.3919 (`rung_native`, single seed 0) | **falsified in a split reading**: F1 (primary, architecture) FALSIFIED with a 7.35-skill-unit sign inversion on `ifc_poisson`, traced to a shared-scaler confound; but the motivating INFORMATION claim is CONFIRMED — an architecture-free estimator recovers +3.2317 skill units from the same 170 disjoint LF rows (18.83% of the law's coefficient energy at cos 0.9993). F2 (native vs upsampled) survived; F3 (degeneracy) verdict depends on provisional vs re-certified floor thresholds (both recorded) | 2 tools, both correctly indexed: `tools/affine_ladder_voi.py`, `tools/posthoc_repair_ladder.py` |
| r2s2_stacked-B1 | model | 14.0756 (single seed 0, no CI yet; scored arm `frozen`; ~all margin from the unpaired `ifc_poisson` column) | clean negative with a measured mechanism, not a raw binary: the falsification clause was a conjunction that did **not** fire — conjunct 1 ("improve on `emul_only` by ≥2.0 skill units") **held** (measured improvement 0.0061, 326x below threshold) but conjunct 2 ("beat the NN-in-condition floor") **failed to hold** (beat it by 11.90 skill units, 130x the noise floor). Round-level headline (I8): a stacked intermediate representation is a re-parameterisation of the condition→HF hypothesis class, not a new information channel | 2 tools, both correctly indexed and register-confirmed: `tools/reachable_set_rank_audit.py`, `tools/surrogate_coherence_eligibility.py` |

r2s4_diag-B2 has all 3 seeds COMPLETED and an initial-analyzer pass landed
(interpretable null on value-of-LF transfer), but the card is not `complete`
— mechanism-analyzer is in progress (4 leads: helmholtz sign flip, ch
info-gap 39.55, I-vs-T dissociation, N-scaling law) and part 7 has not been
written. Not listed here until the card itself closes. r2s3_lf_train_signal-B2
is `built`, awaiting code-review; not listed here either.

## Flags

- **Two card-status deltas this run**: `r2s3_lf_train_signal-B2`
  `drafted` → `built` (build commit `945ee65`, dispatched to code-reviewer,
  `review_notes`/`debug_notes` still empty — no verdict yet); `r2s4_diag-B2`
  `running` → `analyzing` (`job_ids` unchanged at 3 entries, but all 3 are
  now terminal — seeds 1-2 COMPLETED this run). All other 6 cards'
  `status`/`job_ids` byte-identical to last run:
  `r2s1_direct-B1`/`r2s2_stacked-B1`/`r2s3_lf_train_signal-B1`/`r2s4_diag-B1`
  `complete`; `r2s1_direct-B2`/`r2s2_stacked-B2` `drafted`. `reopen_candidate`
  is `false` on all 8 cards.
- **r2s4_diag-B2 all 3 seeds now COMPLETED**: seed 0 (`66181609`, 17:15,
  reported last run) + seed 1 (`66182923`, 17:12, ended 2026-07-31T21:35:51Z)
  + seed 2 (`66182924`, 17:10, ended 2026-07-31T21:35:49Z), all exit 0:0 on
  h200. Per-seed panel geomean: 19.2799 / 20.2928 / 20.0760 → 3-seed geomean
  **19.8829**, reproducing B1's certified band [19.385, 20.527]. The
  orchestrator's initial-analyzer (SUCCESS, 6/6) landed **CRITERION-1**:
  0/6 claimable transfer effects (value-of-LF-as-training-signal null at
  every N) measured against a 5/5 claimable information-gap instrument
  (ratios 13.5-95.3×) — an interpretable null, sensitivity-proven rather than
  a dead measurement. T0 reproduces the B1 certifier bit-identically on
  `ifc_poisson` (instrument-validation check). 2 of the card's part-4
  predictions were not borne out (e.g. cahn_hilliard info gap measured 39.55
  vs a predicted 1.2-3). Fold-fixed in-job 3-seed spread explicitly **not**
  installed into `state/noise_floor.json` (per reviewer finding 3.2b — must
  be labelled "fold-fixed spread" if ever installed). Mechanism-analyzer now
  dispatched with 4 leads (helmholtz sign flip, ch info-gap 39.55, I-vs-T
  dissociation, N-scaling law).
- **r2s3_lf_train_signal-B2 builder committed this run**: build `945ee65`
  ("matched budget-equal +/-LF at N_hf~5 with LF at uncovered conditions
  (repaired-instrument neural channel)"). `build_notes` record oracle
  discipline (test-condition-fitted null-energy diagnostics kept
  structurally separate from every scored number via an `_ORACLE` key
  suffix) and the SLURM sizing (`--time 03:00:00`, from the `r2s3_rung_supervised`
  77.05-min/6-dataset comparator in the timing ledger). No SLURM job
  submitted yet — awaiting code-review.
- **r2s2_stacked-B2 builder progress (no card change)**: builder handoff note
  written this run (`notes/handoff_experiment_builder.md`, mtime 21:47:03Z,
  within this run's window) and its first direct contract-smoke run launched
  on `ext__helmholtz_2d` — **live PID confirmed**: 137889 (~2:11 CPU time,
  `R` state). Family contract has been complete since the prior run
  (`manifest.json` + `smoke_eval.py` alongside the 9 mechanism modules); no
  build commit on the worktree branch yet (only launch commit `9e10d41`).
- **r2s1_direct-B2 builder progress (no card change)**: guard-leg evidence
  run continues, now on `heat_local` — **live PID confirmed**: 142077 (~0:21
  CPU time, `R` state), part of the same evidence-runs shell (PID 134531)
  that already produced the contract smoke (helmholtz) and small-N LOO
  (ifc_poisson/sod_1d) legs. **Note-visibility discrepancy (new, flagged for
  continuity)**: `notes/handoff_experiment_builder.md` exists on disk with
  mtime 2026-07-31T21:16:12Z, which *predates* both this run's window and the
  prior run's window (21:32:56Z-21:37:40Z) — the prior maintainer run
  explicitly reported "no builder handoff yet" for this stream at that check.
  Either the prior check missed the file or the file's mtime does not
  reflect a later content update; the file's *content* (49/49 recipe knobs
  verified, full TBD-provenance table) is self-consistent with a completed
  handoff. No build commit exists (`git status --short` on the worktree:
  `models_r2/`, `notes/`, `scratchpad/`, `scripts/` all untracked), so the
  card itself is unaffected (`status: drafted`, `job_ids: []`) — flagged only
  as a process-visibility item, not a scoring concern.
- **Timing ledger**: **upserted this run** — 2 new entries for jobs
  `66182923` (r2s4_diag batch 2, seed 1, 17.2 min, h200, COMPLETED,
  2026-07-31T21:18:39Z→21:35:51Z, seed panel geomean skill 20.2928) and
  `66182924` (seed 2, 17.17 min, h200, COMPLETED, 21:18:39Z→21:35:49Z, seed
  panel geomean skill 20.0760). Seed-0 entry's note updated to point at
  these siblings instead of "still RUNNING". `_note` field updated: r2s4_diag-B2
  is now the round's first fully-COMPLETED 3-seed B2 card at the SLURM level
  (17.25/17.20/17.17 min per seed on h200). All 8 prior entries re-validated
  against current `sacct` output, unchanged. JSON re-validated as parseable
  (2 top-level keys: `_note`, `entries`; now **10** entries).
- **Timestamp anomaly (r2s1_direct-B1, unchanged, carried forward)**:
  `review_notes[0].utc` still reads `2026-07-31T17:05:00Z` (ahead-of-clock
  relative to the review file's actual write time, first flagged several
  runs ago). No scored quantity affected. Remains the card's only
  unresolved caveat since it closed `complete`.
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
  step-matched, per-rung-scaled repair of both confounds this round — its
  builder has now committed (`945ee65`).
- **r2s4_diag-B2 review finding 3.2b (carried forward)**: B2's in-job 3-seed
  spread randomizes init + batch order ONLY (folds fixed by
  `R2S4B2_SPLIT_SEED=0`) — narrower than B1's constants, which also
  randomized the val split. `operative_threshold = max(certified MCE, in-job
  spread)` stays conservative regardless; if B2's spread is ever installed
  into `state/noise_floor.json` it must be labelled "fold-fixed spread", not
  a drop-in replacement for B1's constants. (This run confirms it was NOT
  installed, per the initial-analyzer's own reporting.)
- **Gates**: G1-r2 PASS, G2-r2 PASS, G3-r2 PASS (all 2026-07-31,
  `state/gates.md`) — round cleared for stream launch. Unchanged this run.
- **Round-1 top-3 seed confirms**: NOT this maintainer's scope (round-1 jobs
  visible in `squeue` as `r1-*`, PENDING) — separate round, separate report.
- No reopen candidates on any of the 8 cards. No `blocked.md` file exists (no
  stream has ever blocked). No abandoned streams — none are possible yet
  (all 4 streams are batch 2 as of this run, all with clean B1 closes, no
  skip/block history anywhere). `state/streams/` directory still does not
  exist — consistent with no abandonments ever being needed.
- Repo hygiene: `git status --short .` (round root, excluding `worktrees/`)
  shows exactly 4 entries this run — `experiment_cards/r2s3_lf_train_signal/batch_2/B2.json`
  modified (the `drafted`→`built` delta, other-subagent write, not touched
  by this maintainer), `state/orchestrator_flow.md`,
  `state/r2s3_lf_train_signal/current_stage.txt`,
  `state/r2s4_diag/current_stage.txt` modified (orchestrator/stream-state
  owned, outside this maintainer's scope). The `r2s4_diag-B2` card's
  `running`→`analyzing` delta is already captured in the repo's most recent
  `round2: auto-sync` commit (`d04a8e9`, 2026-07-31T21:44:19Z), which landed
  after the prior maintainer run ended and before this run's card read —
  hence it shows clean against HEAD. This run's un-synced deltas: the
  r2s3 card change plus this maintainer's own writes (`index.md`,
  `state/maintainer_report.md`, `state/timing_ledger.json`). No Write call
  this maintainer run touched `experiment_cards/`.
