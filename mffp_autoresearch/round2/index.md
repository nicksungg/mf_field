# MFFP Autoresearch Round 2 — Dashboard (updated 2026-07-31T20:34:06Z)

## Streams

| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r2s1_direct | 23.0636 (best_floor_panel_geomean) | **2** | r2s1_direct-B1 **complete**; B2 in progress | **B1: unchanged, still COMPLETE.** **B2 builder continues self-testing** the already-fully-written `models_r2/r2s1_selected_form/` family: `heads.py` was re-edited this run (mtime-fresh), `scratchpad/test_resume.py`/`test_resume.log` (checkpoint-resume verification) landed, and submission scripts now exist (`scripts/01_train_eval.sh`, `scripts/submit.sh`, `scripts/submit_seeds_2_3.sh`) — same "builder nearing handoff" pattern seen on r2s4_diag-B2 last run. **Live PID confirmed**: `score_panel.py --family_dir models_r2/r2s1_selected_form --datasets ext__helmholtz_2d --epochs 2 --no_cache --env $ENV_ARGS` (a contract-smoke re-run reading the recipe straight out of `scripts/01_train_eval.sh`) running at check time. Card itself unchanged on disk (`status: drafted`, `job_ids: []`) — no SLURM submission yet | 0 live (no B2 jobs submitted yet) | `scratchpad/test_resume.py`/`scripts/submit.sh` new this run |
| r2s2_stacked | 23.0636 (best_floor_panel_geomean) | **2** | r2s2_stacked-B1 **complete**; B2 websearch in progress | **B1 CLOSED THIS RUN** (`status: analyzing` → **`complete`**, `reanalysis_progress: turn_3` → **`registered`**): the register turn finished — part 7 written (open_question/next_direction/cross_stream_notes/promoted_tools), 2 tools promoted (`tools/reachable_set_rank_audit.py`, `tools/surrogate_coherence_eligibility.py`, both confirmed indexed in `tools/index.md`). `notes/handoff_experiment_mechanism_analyzer.md` written 20:20Z. Headline finding (I8, round-level): "condition → intermediate field → HF" is a re-parameterisation of the condition→HF hypothesis class, never a new information channel — it inherits the same ceiling as a direct model of equal capacity; this stack sits at/past every training-free condition-only reference on 5/6 panel datasets with the corrector contributing ≤0.08% of the margin. **Stream then advanced into B2 websearch**: `websearches/r2s2_stacked/batch_2/{iteration_1,2,3}.md` + `summary_so_far.md` all present (new since last run); `current_stage.txt` = "websearch (B2 dispatched 2026-07-31; B1 complete)" | 0 live (jobs done) | `experiment_cards/r2s2_stacked/batch_1/B1.json` status→`complete` this run (git-diff confirmed, not this maintainer's write) |
| r2s3_lf_train_signal | 23.0636 (best_floor_panel_geomean) | **2** | r2s3_lf_train_signal-B1 **complete**; B2 in progress | **B1: unchanged, still COMPLETE.** **B2 builder now has fully-written family code** (was empty worktree last run): `models_r2/r2s3_null_supply/{model.py, smoke_eval.py, manifest.json, INSPIRATION.md, lf_reference.py, refs.py, affine_probe.py}` all present with compiled `__pycache__/`. **Live PID confirmed**: `smoke_eval.py --dataset_name ifc_poisson --out scratchpad/dbg_ifc_A2.json` (a debug run) running at check time. Card itself unchanged on disk (`status: drafted`, `job_ids: []`) — no SLURM submission yet | 0 live (no B2 jobs submitted yet) | `models_r2/r2s3_null_supply/` fully populated this run (new) |
| r2s4_diag | **19.8178** (certified_3seed_panel_geomean, CI95 [19.385, 20.527]) | **2** | r2s4_diag-B1 **complete**; B2 **built**, pre-review | **B1: unchanged, still COMPLETE.** **B2 card status advanced this run**: `status: drafted` → **`built`**, `build_commit: a1f3da4dd7873d668b434a279e7958c50c37477d` now set (was `null`); `build_notes` populated (family `models_r2/r2s4_b2_lfvalue` — matched T0/T1/I1/I2 arms, contract smoke exit 0 on `ext__helmholtz_2d`, coverage runs on `ifc_poisson`/`sharp__sod_1d`/`fluid`, all exit 0). `current_stage.txt` now reads "code-review (B2 dispatched...; build a1f3da4, smoke green, resume verified 3 ways)" — `review_notes: []` still, code-review has not written a verdict yet. **Live PID confirmed**: `score_panel.py --family_dir .../r2s4_b2_lfvalue --datasets sharp__phase_field_crystal_2d --epochs 2 --no_cache` (a per-dataset self-verification pass, likely code-reviewer-side) running at check time | 0 live (no B2 jobs submitted yet) | card `status`→`built`, `build_commit` set this run (git-diff confirmed, not this maintainer's write) |

**Anchor note**: r2s4_diag remains the only stream with a *certified* anchor
(`certified_3seed_panel_geomean`, 19.8178, replacing the training-free floor)
— r2s1_direct, r2s2_stacked, r2s3_lf_train_signal remain on the launch-time
`best_floor_panel_geomean` anchor (23.0636, `certified_utc` 2026-07-31T14:20:17Z,
unchanged). No anchor deltas this run. All anchors rendered verbatim from
`state/anchors/*.json`.

**This run's headline**: **two card `status` changes this run** (both by other
subagents, not this maintainer): **r2s2_stacked-B1 closed `complete`**
(register turn finished, 2 tools promoted, stream advanced into B2 websearch —
the round's 2nd fully-closed batch after r2s4_diag-B1/r2s1_direct-B1/
r2s3_lf_train_signal-B1) and **r2s4_diag-B2 advanced `drafted` → `built`**
(build_commit set, awaiting code-review verdict — the furthest any B2 has
progressed). r2s1_direct-B2 and r2s3_lf_train_signal-B2 both continue in
builder self-test with fresh live PIDs. Zero live `r2-*` SLURM jobs — eighth
consecutive check with none live; no B2 stream has reached SLURM submission
yet, though r2s1_direct-B2 and r2s4_diag-B2 both now have ready `submit.sh`
scripts.

## Running / pending jobs

| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| (none) | — | — | — | No `r2-*` jobs live in `squeue` (confirmed via `sacct` cross-check — all 7 batch-1 jobs COMPLETED, no vanished-job false positives; no B2 jobs submitted yet for any stream, despite r2s1_direct-B2 and r2s4_diag-B2 both now having ready `submit.sh`). 3 local (non-SLURM) self-test/debug processes confirmed live via `ps aux`: r2s1_direct-B2 contract-smoke re-run (`ext__helmholtz_2d`), r2s3_lf_train_signal-B2 debug run (`ifc_poisson`), r2s4_diag-B2 post-build self-verification (`sharp__phase_field_crystal_2d`) |

Unrelated interactive `bash` jobs and round-1 `r1-*` jobs also visible in the
queue — out of this maintainer's scope, not itemized here.

## Completed cards

| Card | Type | Panel geomean skill (±CI) | Falsification verdict | Tools promoted |
|---|---|---|---|---|
| r2s4_diag-B1 | diagnostic | 19.8178 IQM, CI95 [19.385, 20.527] (3 seeds) | n/a (diagnostic — no falsification clauses); mechanism register complete, part 7 written | 2 tools, both correctly indexed: `tools/conditional_mean_collapse.py`, `tools/condition_predictability_ceiling.py` |
| r2s1_direct-B1 | model | 19.6444 (single seed 0, no CI yet) | register-turn recalibration measurement narrows (but does not eliminate) the decoder-capacity claim on `sharp__cahn_hilliard` (4.29% / 6.0x MCE, flagged as open, not adjudicated) | 2 tools, both correctly indexed: `tools/band_gain_counterfactual.py`, `tools/condition_identifiable_rank.py` |
| r2s3_lf_train_signal-B1 | model | 25.3919 (`rung_native`, single seed 0) | **falsified** (F1 sign-inverted -7.35 skill units on ifc_poisson; F2 survives vs a diverged comparator; F3 threshold-provenance split, both readings recorded on the card). `7_gap_and_future`: open question is architecture-vs-information (network vs the closed-form linear/affine LF channel on ifc_poisson); `next_direction` recommends shipping the affine channel as its own B2 family — this is exactly the deliverable that B2 (`r2s3_null_supply`) is being built around | 2 tools, both correctly indexed: `tools/affine_ladder_voi.py`, `tools/posthoc_repair_ladder.py` |
| **r2s2_stacked-B1** (newly closed this run) | model | 14.0756 (single seed 0, no CI yet; scored arm `frozen`; ~all margin is the unpaired `ifc_poisson` column) | clean negative with a measured mechanism, not a raw "confirmed"/"falsified" binary: the card's own falsification clause was a conjunction that did **not** fire in either half as pre-registered — conjunct 1 ("improve on `emul_only` by ≥2.0 skill units") **held** (measured improvement 0.0061, 326x below threshold) but conjunct 2 ("beat the NN-in-condition floor") **failed to hold** (beat it by 11.90 skill units, 130x the noise floor), so the AND never triggered. Round-level headline (I8): the stacked class is capped by the same ceiling as a direct condition→HF model of equal capacity — an intermediate representation is a re-parameterisation, not a new information channel | 2 tools, both correctly indexed and register-confirmed: `tools/reachable_set_rank_audit.py`, `tools/surrogate_coherence_eligibility.py` |

## Flags

- **Card `status` deltas this run (2, both by other subagents — no card
  writes by this maintainer)**: `r2s2_stacked-B1` `analyzing` → `complete`
  (register turn finished, moved to Completed table above); `r2s4_diag-B2`
  `drafted` → `built` (`build_commit` now `a1f3da4dd7873d668b434a279e7958c50c37477d`,
  awaiting code-review verdict, `review_notes: []` still empty). All other 5
  cards unchanged: `r2s1_direct-B1` `complete`, `r2s1_direct-B2` `drafted`,
  `r2s3_lf_train_signal-B1` `complete`, `r2s3_lf_train_signal-B2` `drafted`,
  `r2s4_diag-B1` `complete`. `reopen_candidate` is `false` on all 7 cards.
- **r2s2_stacked stream advanced B1→B2**: websearch dispatched and 3/many
  iterations + `summary_so_far.md` already written this run — the fastest any
  stream has moved through websearch this round (same run window as B1's
  register turn closing).
- **r2s4_diag-B2 built, in code-review**: `build_commit` set, contract smoke
  green, resume verified 3 ways per `current_stage.txt`; a live PID-confirmed
  self-verification pass on `sharp__phase_field_crystal_2d` is running.
  `review_notes` still empty — no verdict written yet, not itself an anomaly
  (code-review just started).
- **r2s1_direct-B2 builder nearing handoff**: submission scripts
  (`scripts/01_train_eval.sh`, `submit.sh`, `submit_seeds_2_3.sh`) and a
  checkpoint-resume self-test (`test_resume.py`/`.log`) now exist alongside
  the already-complete family code — same pattern r2s4_diag-B2 showed one run
  before its `built` status change. Card itself still `drafted`,
  `job_ids: []`; no SLURM submission yet.
- **r2s3_lf_train_signal-B2 builder produced full family code this run**:
  `models_r2/r2s3_null_supply/` went from empty to 7 files including a
  compiled `__pycache__/`; live PID-confirmed debug run on `ifc_poisson`. The
  starter's forwarded transcription-count discrepancy (card's own
  `recipe.env._note` says "23/25" keys, actually lists 30 `R2S3B2_*` keys,
  carried forward from last run, not yet resolved by this builder run) is
  unaffected by today's progress — key list remains authoritative.
- **Timestamp anomaly (r2s1_direct-B1, unchanged, carried forward)**:
  `review_notes[0].utc` still reads `2026-07-31T17:05:00Z` (ahead-of-clock
  relative to the review file's actual write time, first flagged several
  runs ago). No scored quantity affected. Remains the card's only
  unresolved caveat since it closed `complete`.
- **Timing ledger**: no new upsert this run (all 7 entries from prior runs
  remain valid and match current `sacct` output exactly; re-validated as
  parseable JSON, no changes needed). Zero live `r2-*` jobs — eighth
  consecutive check with none live.
- **Analyzer caveat carried forward (r2s1_direct-B1, from code-review)**: the
  D3 certificate's aleatoric-floor estimate is window-sensitive — at the
  recipe's window (1000 closest pairs), `ext__helmholtz_2d` reads 1.200,
  worse than the zero predictor. Must not be reported as a ceiling for
  helmholtz; `allen_cahn`'s ceiling must be reported as a range
  (0.315-0.471); `pfc`/`fisher_kpp` are window-robust and quotable.
- **Analyzer caveat (r2s2_stacked-B1, from code-review + register turn),
  now closed out but preserved for the round report**: ifc_poisson's rung
  ladder is UNPAIRED (independent condition draws per rung, min distance
  0.08-0.30, never 0) — matches r2s3's independent finding, a cross-stream
  benchmark-integrity item. A2/A5 arms there are `arm_semantics_degraded=True`.
  The register turn's own ifc_poisson finding (LF field exactly affine in the
  5-dim condition, ridge held-out 0.0000) is independent corroboration of
  r2s3-B1's affine-LOO finding (3.2e-08) — the ifc_poisson degeneracy is now
  cross-confirmed by two independent streams/estimators.
- **Analyzer caveat (r2s3_lf_train_signal-B1, from code-review)**, carried
  forward: the shared-max-abs-rungs scaler makes ifc_poisson's `rung_native`
  stage-1 loss ~42x amplitude-weighted toward rung 8 over HF (confound C1,
  card-locked design, not a build defect); F1 is epoch-matched but not
  step-matched (confound C2, "ran IN FAVOR of the losing arm" per the card's
  own `cratered_detail` — does not explain away the inversion). r2s3-B2's
  card explicitly ships a step-matched, per-rung-scaled repair of both
  confounds this round.
- **Gates**: G1-r2 PASS, G2-r2 PASS, G3-r2 PASS (all 2026-07-31,
  `state/gates.md`) — round cleared for stream launch. Unchanged this run.
- **Round-1 top-3 seed confirms**: NOT this maintainer's scope (round-1 jobs
  visible in `squeue` as `r1-*`, PENDING) — separate round, separate report.
- No reopen candidates on any of the 7 cards. No `blocked.md` file exists (no
  stream has ever blocked). No abandoned streams — none are possible yet
  (all 4 streams are batch 2 as of this run, all with clean B1 closes, no
  skip/block history anywhere). `state/streams/` directory still does not
  exist — consistent with no abandonments ever being needed.
- Repo hygiene: `git status --short` on
  `mffp_autoresearch/round2/experiment_cards/` shows exactly the 2 cards with
  legitimate status-field changes above (`r2s2_stacked/batch_1/B1.json`,
  `r2s4_diag/batch_2/B2.json`) as modified — both other-subagent writes,
  neither touched by this maintainer this run. Non-card writes seen in the
  broader round2 tree, all other subagents' legitimate in-progress work:
  `state/r2s2_stacked/{current_batch.txt,current_stage.txt}`,
  `worktrees/r2s1_direct/B2/{models_r2,scratchpad,scripts}/`,
  `worktrees/r2s2_stacked/B1/{notes,scratchpad}/`,
  `worktrees/r2s3_lf_train_signal/B2/{models_r2,mf_field}/`,
  `worktrees/r2s4_diag/B2/{probes,scratchpad}/__pycache__` and
  `scratchpad/{contract_smoke.json,contract_smoke.log,smoke_arms/}`,
  `websearches/r2s2_stacked/batch_2/` (new dir, untracked), `eval/cache/`,
  `eval/results/r2s4_b2_lfvalue/`. `state/orchestrator_flow.md` also
  modified (orchestrator-owned, outside this maintainer's scope). Confirmed
  no Write call this maintainer run touched `experiment_cards/`. `index.md`
  and `state/maintainer_report.md` are this maintainer's own writes. Most
  recent `round2: auto-sync` commit `5f74072` (2026-07-31T20:14:17Z) — this
  run's deltas are not yet auto-synced (auto-sync is a separate cron).
