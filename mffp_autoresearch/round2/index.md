# MFFP Autoresearch Round 2 — Dashboard (updated 2026-07-31T21:32:56Z)

## Streams

| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r2s1_direct | 23.0636 (best_floor_panel_geomean) | **2** | r2s1_direct-B1 **complete**; B2 in progress | **B1: unchanged, still COMPLETE.** **B2 builder still self-testing, new leg**: the `--datasets guard` sweep continues — now running `smoke_eval.py` directly on `heat_local` (2 epochs) via a fresh `score_panel.py` wrapper invocation (PID 128608/129675, ~3:37 CPU time, `R` state, confirmed live via `ps aux`). Card itself unchanged on disk (`status: drafted`, `job_ids: []`, no builder handoff note yet) | 0 live (no B2 jobs submitted yet) | Guard-dataset debug sweep continuing on `heat_local` |
| r2s2_stacked | 23.0636 (best_floor_panel_geomean) | **2** | r2s2_stacked-B1 **complete**; r2s2_stacked-B2 **drafted** | **B1: unchanged, still COMPLETE.** **B2 builder's contract is now complete**: `models_r2/r2s2_correctability/manifest.json` and `smoke_eval.py` landed this run (both absent last check) — the family now has all 9 mechanism modules + `manifest.json` + `smoke_eval.py` + `INSPIRATION.md`. **Live PID confirmed**: PID 129751 (~2:16 CPU time, `R` state) running `smoke_eval.py --dataset_name ext__helmholtz_2d --epochs 2 --seed 0` directly (not via `score_panel.py`), log shows M1/M1c coherence-threshold-calibration mechanism probes in progress (`gamma_b1`, `oracle_gain`, `CORRECTOR_FUTILE`/`UNDETERMINED` verdicts being computed per amplitude/bandwidth sweep point). Still no build commit on the worktree branch (only launch commit `9e10d41`) | 0 live (no B2 jobs submitted yet) | Contract now complete (manifest.json + smoke_eval.py landed); first direct smoke run in progress |
| r2s3_lf_train_signal | 23.0636 (best_floor_panel_geomean) | **2** | r2s3_lf_train_signal-B1 **complete**; B2 in progress | **B1: unchanged, still COMPLETE.** **B2 builder advanced two more debug legs**: the cahn_hilliard `A2_lf_cov_null` leg (same PID 121353 from last check) completed (`dbg_ch_A2.json` full split table written, `gate m=15 rank=5 null_active=True`), then `A3_lf_paired` also completed (`dbg_ch_A3.json` written, `null_active=False` as expected for the paired arm), and the driver moved on to `sharp__fisher_kpp_2d` `A2_lf_cov_null` — **live PID confirmed**: PID 130232 (new PID, ~1:27 CPU time, `R` state) running `smoke_eval.py --dataset_name sharp__fisher_kpp_2d --out scratchpad/dbg_fk_A2.json`. Worktree branch still uncommitted. Card unchanged (`status: drafted`, `job_ids: []`, `build_commit: null`) | 0 live (no B2 jobs submitted yet) | cahn_hilliard A2 + A3 legs completed; now mid-run on fisher_kpp A2 |
| r2s4_diag | **19.8178** (certified_3seed_panel_geomean, CI95 [19.385, 20.527]) | **2** | r2s4_diag-B1 **complete**; r2s4_diag-B2 **running** (seeds 0,1,2) | **B1: unchanged, still COMPLETE.** **B2's seed-0 SLURM job COMPLETED this run**: `66181609` (`r2-r2s4_diag-B2-s0`) finished at 21:16:51Z, elapsed 17:15, exit 0:0, `orchestrator_flow.md` records geomean 19.2799 finite on 6/6 datasets — the seed-0 gate passed. **Orchestrator then submitted seeds 1-2** (`66182923`/`66182924`, started 21:18:39Z) per the reviewer-adjudicated 3-seed exception (SS12.4 + B1 part-7 directive); card `job_ids` now `['66181609','66182923','66182924']`, `status: running`, unchanged otherwise | **2 live**: `66182923`/`66182924` RUNNING on `hpc-sm-01-04`, ~14:03 elapsed each | Seed 0 COMPLETED (17:15, first B2 completion); seeds 1-2 submitted and now running |

**Anchor note**: r2s4_diag remains the only stream with a *certified* anchor
(`certified_3seed_panel_geomean`, 19.8178, replacing the training-free floor)
— r2s1_direct, r2s2_stacked, r2s3_lf_train_signal remain on the launch-time
`best_floor_panel_geomean` anchor (23.0636, `certified_utc` 2026-07-31T14:20:17Z,
unchanged). No anchor deltas this run. All anchors rendered verbatim from
`state/anchors/*.json`.

**This run's headline**: r2s4_diag-B2's seed 0 SLURM job **COMPLETED**
(the round's first B2 job completion, elapsed 17:15, geomean 19.2799 per
`orchestrator_flow.md`), triggering the seed-0 gate pass and submission of
seeds 1-2 (both now RUNNING) — the only card-file delta this run
(`job_ids` grew from 1 to 3 entries, `status` unchanged at `running`).
Sub-card progress on the other three streams: r2s2_stacked-B2's contract
completed (`manifest.json` + `smoke_eval.py` landed) and its first direct
smoke run is in progress (mechanism-calibration probes M1/M1c); r2s3's
builder finished 2 more debug legs (cahn_hilliard A2 + A3) and moved to
fisher_kpp; r2s1's builder continues its guard-dataset debug sweep on
`heat_local`. Timing ledger upserted with the newly COMPLETED job
(66181609, 17.25 min, h200) — the round's first B2-scale timing datum.

## Running / pending jobs

| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| 66182923 | r2s4_diag-B2 (seed 1) | RUNNING | ~14:03 | hpc-sm-01-04 |
| 66182924 | r2s4_diag-B2 (seed 2) | RUNNING | ~14:03 | hpc-sm-01-04 |

66181609 (r2s4_diag-B2 seed 0) COMPLETED this run (17:15 elapsed, exit 0:0) —
moved out of this table into the timing ledger. 3 local (non-SLURM)
self-test/debug processes confirmed live via `ps aux`: r2s1_direct-B2 guard
debug on `heat_local` (PID 128608/129675), r2s2_stacked-B2's first direct
smoke run on `ext__helmholtz_2d` (PID 129751), r2s3_lf_train_signal-B2 debug
leg on `sharp__fisher_kpp_2d` (PID 130232). Unrelated interactive `bash` jobs
and round-1 `r1-*` jobs also visible in the queue — out of this maintainer's
scope, not itemized here.

## Completed cards

| Card | Type | Panel geomean skill (±CI) | Falsification verdict | Tools promoted |
|---|---|---|---|---|
| r2s4_diag-B1 | diagnostic | 19.8178 IQM, CI95 [19.385, 20.527] (3 seeds) | n/a (diagnostic — no falsification clauses); mechanism register complete, part 7 written | 2 tools, both correctly indexed: `tools/conditional_mean_collapse.py`, `tools/condition_predictability_ceiling.py` |
| r2s1_direct-B1 | model | 19.6444 (single seed 0, no CI yet) | **falsified in a split reading**: floors clause CONFIRMED (beats best floor on all 6 panel datasets, geomean −14.8% vs anchor) but the implicit architecture clause FALSIFIED — a ~156-parameter closed-form head reaches 19.0553/19.1666, statistically indistinguishable from the 15.9M-parameter shipped arm (0.52x the certified panel min_claimable_effect) | 2 tools, both correctly indexed: `tools/band_gain_counterfactual.py`, `tools/condition_identifiable_rank.py` |
| r2s3_lf_train_signal-B1 | model | 25.3919 (`rung_native`, single seed 0) | **falsified in a split reading**: F1 (primary, architecture) FALSIFIED with a 7.35-skill-unit sign inversion on `ifc_poisson`, traced to a shared-scaler confound; but the motivating INFORMATION claim is CONFIRMED — an architecture-free estimator recovers +3.2317 skill units from the same 170 disjoint LF rows (18.83% of the law's coefficient energy at cos 0.9993). F2 (native vs upsampled) survived; F3 (degeneracy) verdict depends on provisional vs re-certified floor thresholds (both recorded) | 2 tools, both correctly indexed: `tools/affine_ladder_voi.py`, `tools/posthoc_repair_ladder.py` |
| r2s2_stacked-B1 | model | 14.0756 (single seed 0, no CI yet; scored arm `frozen`; ~all margin from the unpaired `ifc_poisson` column) | clean negative with a measured mechanism, not a raw binary: the falsification clause was a conjunction that did **not** fire — conjunct 1 ("improve on `emul_only` by ≥2.0 skill units") **held** (measured improvement 0.0061, 326x below threshold) but conjunct 2 ("beat the NN-in-condition floor") **failed to hold** (beat it by 11.90 skill units, 130x the noise floor). Round-level headline (I8): a stacked intermediate representation is a re-parameterisation of the condition→HF hypothesis class, not a new information channel | 2 tools, both correctly indexed and register-confirmed: `tools/reachable_set_rank_audit.py`, `tools/surrogate_coherence_eligibility.py` |

r2s4_diag-B2's seed 0 has a finite result (geomean 19.2799 per
`orchestrator_flow.md`) but the card is not `complete` — awaiting seeds 1-2
(both RUNNING) for the mandatory 3-seed paired spread before analysis. Not
listed here until the card itself closes.

## Flags

- **Only card-file delta this run**: `r2s4_diag-B2` `job_ids` grew from
  `['66181609']` to `['66181609','66182923','66182924']` (seed 0 COMPLETED,
  seeds 1-2 submitted and RUNNING); `status` unchanged at `running`. All
  other 7 cards' `status`/`job_ids` byte-identical to last run:
  `r2s1_direct-B1`/`r2s2_stacked-B1`/`r2s3_lf_train_signal-B1`/`r2s4_diag-B1`
  `complete`; `r2s1_direct-B2`/`r2s2_stacked-B2`/`r2s3_lf_train_signal-B2`
  `drafted`. `reopen_candidate` is `false` on all 8 cards.
- **r2s4_diag-B2 seed 0 COMPLETED**: `66181609` (`r2-r2s4_diag-B2-s0`),
  17:15 elapsed, exit 0:0, ended 2026-07-31T21:16:51Z (right at the boundary
  of the prior maintainer run's window, which last saw it RUNNING at ~12:37
  elapsed). `orchestrator_flow.md` records the seed-0 result as finite
  (geomean 19.2799, 6/6 datasets) and the gate as passed. Seeds 1-2
  (`66182923`/`66182924`) submitted 2026-07-31T21:18:39Z, both RUNNING on
  `hpc-sm-01-04`, ~14:03 elapsed at this check — steady progress, no state
  transitions yet.
- **r2s2_stacked-B2 builder's contract now complete**: `manifest.json` and
  `smoke_eval.py` landed this run (both absent at last check) alongside the
  9 mechanism modules from before. First direct smoke run in progress
  (`ext__helmholtz_2d`, 2 epochs, PID 129751 live) — mechanism-calibration
  probes (M1 coherence threshold sweep, M1c nonlinear stress test) producing
  `CORRECTOR_FUTILE`/`UNDETERMINED` verdicts per amplitude/bandwidth point.
  No build commit on the worktree branch yet (only launch commit `9e10d41`).
- **r2s1_direct-B2 builder progress**: guard-dataset debug sweep continues,
  now inside `smoke_eval.py` on `heat_local` (fresh PID 128608/129675, 2
  epochs). Card itself still `drafted`, `job_ids: []`, no builder handoff yet.
- **r2s3_lf_train_signal-B2 builder progress**: cahn_hilliard `A2_lf_cov_null`
  and `A3_lf_paired` legs both completed cleanly this run (full split tables
  written); driver moved on to `sharp__fisher_kpp_2d` `A2_lf_cov_null` (new
  PID 130232 live). Worktree branch still uncommitted. The starter's
  forwarded env-key-count discrepancy (card says "23/25", lists 30 keys,
  carried forward several runs, unresolved) remains unaffected — key list
  stays authoritative.
- **Timestamp anomaly (r2s1_direct-B1, unchanged, carried forward)**:
  `review_notes[0].utc` still reads `2026-07-31T17:05:00Z` (ahead-of-clock
  relative to the review file's actual write time, first flagged several
  runs ago). No scored quantity affected. Remains the card's only
  unresolved caveat since it closed `complete`.
- **Timing ledger**: **upserted this run** — new entry for `66181609`
  (r2s4_diag batch 2 seed 0, family `r2s4_b2_lfvalue`, 17.25 min, h200,
  COMPLETED, 2026-07-31T20:59:36Z→21:16:51Z), the round's first B2-scale
  timing datum. All 7 prior entries re-validated unchanged. JSON re-validated
  as parseable (2 top-level keys: `_note`, `entries`; now 8 entries). Seeds
  1-2 not yet upserted (still RUNNING).
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
- **r2s4_diag-B2 review finding 3.2b (carried forward)**: B2's in-job 3-seed
  spread randomizes init + batch order ONLY (folds fixed by
  `R2S4B2_SPLIT_SEED=0`) — narrower than B1's constants, which also
  randomized the val split. `operative_threshold = max(certified MCE, in-job
  spread)` stays conservative regardless; if B2's spread is ever installed
  into `state/noise_floor.json` it must be labelled "fold-fixed spread", not
  a drop-in replacement for B1's constants.
- **Gates**: G1-r2 PASS, G2-r2 PASS, G3-r2 PASS (all 2026-07-31,
  `state/gates.md`) — round cleared for stream launch. Unchanged this run.
- **Round-1 top-3 seed confirms**: NOT this maintainer's scope (round-1 jobs
  visible in `squeue` as `r1-*`, PENDING) — separate round, separate report.
- No reopen candidates on any of the 8 cards. No `blocked.md` file exists (no
  stream has ever blocked). No abandoned streams — none are possible yet
  (all 4 streams are batch 2 as of this run, all with clean B1 closes, no
  skip/block history anywhere). `state/streams/` directory still does not
  exist — consistent with no abandonments ever being needed.
- Repo hygiene: `git status --short` on `mffp_autoresearch/round2/` shows
  exactly 1 experiment_cards entry this run — `r2s4_diag/batch_2/B2.json`
  modified (the `job_ids` growth from seed-0 completion + seeds-1-2
  submission, other-subagent/orchestrator write, not touched by this
  maintainer); `git diff --stat` confirms 3 insertions/1 deletion, all
  inside the `job_ids` array. Broader tree: `state/orchestrator_flow.md`,
  `state/r2s4_diag/current_stage.txt` modified (orchestrator/stream-state
  owned, outside this maintainer's scope). `index.md`,
  `state/maintainer_report.md`, `state/timing_ledger.json` are this
  maintainer's own writes this run. Most recent `round2: auto-sync` commit
  `7761e6d` (2026-07-31T21:14:16Z) — this run's deltas (seed-0 completion,
  seeds-1-2 submission, timing-ledger upsert) postdate it and are not yet
  auto-synced.
