# MFFP Autoresearch Round 2 — Dashboard (updated 2026-07-31T22:34:18Z)

## Streams

| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r2s1_direct | 23.0636 (best_floor_panel_geomean) | **2** | r2s1_direct-B1 **complete**; r2s1_direct-B2 **built** (new this run) | **B1: unchanged, still COMPLETE.** **B2 builder finished this run — card delta**: `status` `drafted`→`built`, `build_commit` `d844bec` landed (family `models_r2/r2s1_selected_form`: config/common/ridge/heads/wiener/blend/floors/decoder/train/diagnostics/smoke_eval + manifest + INSPIRATION; a pre-registered training-free selection of a closed-form condition→HF head, Wiener-calibrated capacity ladder). Build was the round's longest so far (~10.1M tokens / 2.8h). Contract smoke green (helmholtz nRMSE 0.9327, skill 3.119), checkpoint-resume verified bit-identical both branches, 3 speedups verified to 1 ulp (540s→80s). One TBD flagged for the reviewer: the rank-statistic shipped affine+LOO with `r_sel` divergence from the tool baseline (adjudication needed). Orchestrator dispatched the code-reviewer (`state/r2s1_direct/current_stage.txt`: "code-review"); `review_notes` still empty — not yet returned | 0 live (no SLURM job yet; awaiting code-review before submission) | Builder SUCCESS (10/10), build `d844bec` landed → code-reviewer dispatched |
| r2s2_stacked | 23.0636 (best_floor_panel_geomean) | **2** | r2s2_stacked-B1 **complete**; r2s2_stacked-B2 **running** (new this run) | **B1: unchanged, still COMPLETE.** **B2 cleared build + code-review + SLURM submission this run — card delta**: `status` `drafted`→`running`. Build `bd54bcb` landed (family `models_r2/r2s2_correctability`: ladders A/B, disjoint 0.70/0.15/0.15 folds, floor+upsampler 1e-9 seam checks, `probes/correctability_law.py`). Code-reviewer verdict `reviewed_suggest` (6/6 PASS): F1 survives oracle-negative semantics via its margin rule but the analyzer must substitute the M1b spread and say so; k*-selection-variance risk flagged (helmholtz argmin picked k=1, 52% worse than k=all on test — report k* stability across fold seeds); A:1≡B:1 gap is an init-variance lower bound only. Orchestrator submitted seed 0: **panel job `66187052`** (walltime raised 2h→3h30 per reviewer finding 5) + **guard job `66187053`**. Guard leg already **COMPLETED** (2.4 min, upserted into timing ledger this run) | **1 live** (`66187052`, seed 0 panel, RUNNING); guard `66187053` COMPLETED this run | Build SUCCESS → code-review SUGGEST (no block) → orchestrator submitted seed 0 panel+guard; card `drafted`→`running`; guard leg COMPLETED |
| r2s3_lf_train_signal | 23.0636 (best_floor_panel_geomean) | **2** | r2s3_lf_train_signal-B1 **complete**; r2s3_lf_train_signal-B2 **running** | **B1: unchanged, still COMPLETE. B2: no card change this run** — job `66185845` (seed 0, h200, `--time 03:00:00`, 17 serial legs) continues RUNNING, now ~33 min elapsed (up from ~11 min at last check), confirmed live in both `squeue` (node `hpc-sm-01-04`) and `sacct`. No new legs' output observed at this check beyond what was already reported | **1 live** (`66185845`, seed 0, RUNNING, ~33 min elapsed) | No change this run — job continues, same PID/job-id, steady progress |
| r2s4_diag | **19.8178** (certified_3seed_panel_geomean, CI95 [19.385, 20.527]) | **2** | r2s4_diag-B1 **complete**; r2s4_diag-B2 **analyzing** | **B1: unchanged, still COMPLETE. B2: card status unchanged (`analyzing`)**, but the mechanism-analyzer's turn-1 reanalysis **completed this run** (6/6, per `orchestrator_flow.md`): the I-vs-T dissociation lead is EXPLAINED (the aux-LF target is exactly as condition-unidentifiable as HF on 4/5 datasets because the aux head duplicates the main task — the certified "information gap" is an INPUT statement while the transfer null is a TARGET statement, i.e. two different channels, not a contradiction); helmholtz remains the lone harmful exception; the cahn_hilliard info-gap miss is attributed to a support failure (d_min 3.12 in 19-d) vs fisher_kpp's aleatoric explanation — two distinct mechanisms behind one null; STRUCTURALLY, `lf[:n_hf]` gave the aux head only 5/170 ifc rows, so it could not reach r2s3's win by construction. A fast float32 ceiling-tool variant was staged for register promotion. Turn 2 dispatched (helmholtz sign flip, cross-referencing r2s3-B2 as the direct null-supply test) — no live process for it yet at this check (`ps aux` clean for this stream) | 0 live SLURM (all 3 seeds terminal, unchanged); 0 live local processes at this check (turn-1 loop finished, turn-2 not yet started) | Mechanism-analyzer turn-1 COMPLETE (6/6, I-vs-T dissociation explained) → turn-2 dispatched (helmholtz sign flip) |

**Anchor note**: r2s4_diag remains the only stream with a *certified* anchor
(`certified_3seed_panel_geomean`, 19.8178, replacing the training-free floor)
— r2s1_direct, r2s2_stacked, r2s3_lf_train_signal remain on the launch-time
`best_floor_panel_geomean` anchor (23.0636, `certified_utc` 2026-07-31T14:20:17Z,
unchanged). No anchor deltas this run. All anchors rendered verbatim from
`state/anchors/*.json`.

**This run's headline**: **all four batch-2 cards have now cleared their
build stage** ("LAST B2 BUILD DONE — all four batch-2 cards now built" per
`orchestrator_flow.md`). Two card-status deltas this run: `r2s1_direct-B2`
`drafted`→`built` (build `d844bec` landed, code-reviewer dispatched, not yet
returned) and `r2s2_stacked-B2` `drafted`→`running` (build `bd54bcb` →
code-review `reviewed_suggest` → SLURM submitted, panel job `66187052` still
running, guard job `66187053` already COMPLETED). `r2s3_lf_train_signal-B2`
continues unchanged (job `66185845` still RUNNING, ~33 min in). `r2s4_diag-B2`
card status unchanged (`analyzing`) but its mechanism-analyzer's turn-1
reanalysis completed (6/6) with the I-vs-T dissociation lead explained;
turn-2 dispatched. Timing ledger **upserted with 1 new entry** this run
(`66187053`, r2s2_stacked-B2 guard leg, 2.4 min) — now **11 entries** total.

## Running / pending jobs

| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| 66185845 | r2s3_lf_train_signal-B2 (seed 0) | RUNNING | ~33 min | hpc-sm-01-04 |
| 66187052 | r2s2_stacked-B2 (seed 0 panel) | RUNNING | ~5 min | hpc-sm-01-04 |

**2 live `r2-*` SLURM jobs** this check (squeue + sacct cross-checked): the
continuing `66185845` (r2s3_lf_train_signal-B2 seed 0) and the newly
submitted `66187052` (r2s2_stacked-B2 seed 0 panel). `66187053`
(r2s2_stacked-B2 seed 0 guard) transitioned RUNNING→COMPLETED within this
run's window (2.4 min elapsed, confirmed terminal in both `squeue`'s absence
and `sacct`'s `COMPLETED` state — not a transient-empty false positive,
directly cross-checked) and has been upserted into the timing ledger. No
live local (non-SLURM) builder/debug/analyzer processes at this check
(`ps aux` clean for all `r2s1`/`r2s2`/`r2s4` patterns — the r2s1 and r2s2
builders finished and handed off, and r2s4's turn-2 mechanism-analyzer has
not yet started producing output); a single unrelated background polling
loop (PID 145527, waiting on job `66185845`'s terminal state via `sacct`)
is visible but is the orchestrator's own poller, out of this maintainer's
scope. Unrelated interactive `bash` jobs and round-1 `r1-*` jobs also
visible in the queue — out of this maintainer's scope, not itemized here.

## Completed cards

| Card | Type | Panel geomean skill (±CI) | Falsification verdict | Tools promoted |
|---|---|---|---|---|
| r2s4_diag-B1 | diagnostic | 19.8178 IQM, CI95 [19.385, 20.527] (3 seeds) | n/a (diagnostic — no falsification clauses); mechanism register complete, part 7 written | 2 tools, both correctly indexed: `tools/conditional_mean_collapse.py`, `tools/condition_predictability_ceiling.py` |
| r2s1_direct-B1 | model | 19.6444 (single seed 0, no CI yet) | **falsified in a split reading**: floors clause CONFIRMED (beats best floor on all 6 panel datasets, geomean −14.8% vs anchor) but the implicit architecture clause FALSIFIED — a ~156-parameter closed-form head reaches 19.0553/19.1666, statistically indistinguishable from the 15.9M-parameter shipped arm (0.52x the certified panel min_claimable_effect) | 2 tools, both correctly indexed: `tools/band_gain_counterfactual.py`, `tools/condition_identifiable_rank.py` |
| r2s3_lf_train_signal-B1 | model | 25.3919 (`rung_native`, single seed 0) | **falsified in a split reading**: F1 (primary, architecture) FALSIFIED with a 7.35-skill-unit sign inversion on `ifc_poisson`, traced to a shared-scaler confound; but the motivating INFORMATION claim is CONFIRMED — an architecture-free estimator recovers +3.2317 skill units from the same 170 disjoint LF rows (18.83% of the law's coefficient energy at cos 0.9993). F2 (native vs upsampled) survived; F3 (degeneracy) verdict depends on provisional vs re-certified floor thresholds (both recorded) | 2 tools, both correctly indexed: `tools/affine_ladder_voi.py`, `tools/posthoc_repair_ladder.py` |
| r2s2_stacked-B1 | model | 14.0756 (single seed 0, no CI yet; scored arm `frozen`; ~all margin from the unpaired `ifc_poisson` column) | clean negative with a measured mechanism, not a raw binary: the falsification clause was a conjunction that did **not** fire — conjunct 1 ("improve on `emul_only` by ≥2.0 skill units") **held** (measured improvement 0.0061, 326x below threshold) but conjunct 2 ("beat the NN-in-condition floor") **failed to hold** (beat it by 11.90 skill units, 130x the noise floor). Round-level headline (I8): a stacked intermediate representation is a re-parameterisation of the condition→HF hypothesis class, not a new information channel | 2 tools, both correctly indexed and register-confirmed: `tools/reachable_set_rank_audit.py`, `tools/surrogate_coherence_eligibility.py` |

r2s4_diag-B2 has all 3 seeds COMPLETED, an initial-analyzer pass, and now a
completed mechanism-analyzer turn-1 (6/6), but the card is not `complete` —
turn-2 was just dispatched and part 7 has not been written. Not listed here
until the card itself closes. r2s1_direct-B2 (`built`, awaiting code-review)
and r2s2_stacked-B2 (`running`, seed 0 panel job `66187052` in flight) are
not listed here either.

## Flags

- **Two card-status deltas this run**: `r2s1_direct-B2` `drafted`→`built`
  (build `d844bec` landed, code-reviewer dispatched, `review_notes` still
  empty) and `r2s2_stacked-B2` `drafted`→`running` (build `bd54bcb` →
  code-review `reviewed_suggest` → SLURM jobs `66187052`/`66187053`
  submitted). All four batch-2 cards are now built or further along — the
  round's build phase for this batch is complete
  (`orchestrator_flow.md`: "LAST B2 BUILD DONE — all four batch-2 cards now
  built"). Unchanged: `r2s1_direct-B1`/`r2s2_stacked-B1`/
  `r2s3_lf_train_signal-B1`/`r2s4_diag-B1` `complete`; `r2s3_lf_train_signal-B2`
  `running`; `r2s4_diag-B2` `analyzing`. `reopen_candidate` is `false` on all
  8 cards.
- **r2s1_direct-B2 build detail**: build `d844bec` — family
  `models_r2/r2s1_selected_form`, condition-only forward signature at every
  stage, no round-1 or factory model code vendored (sole factory contact is
  a read-only import of `mf_field/factory_mffp/data_adapters/loaders.py`).
  Contract smoke on `ext__helmholtz_2d`: nRMSE 0.9327, skill 3.119.
  Checkpoint-resume verified bit-identical on both branches; 3 speedups
  verified to 1 ulp (540s→80s runtime). One TBD for the reviewer to
  adjudicate: the rank-statistic shipped affine+LOO with `r_sel` divergence
  from the tool baseline (decidability question, not a build defect). No
  SLURM job submitted yet — awaiting code-review.
- **r2s2_stacked-B2 code-review verdict detail**: `reviewed_suggest`, 6/6
  PASS. Findings: (1) F1 survives oracle-negative semantics via its
  `max(3x spread, 0.05)` margin, but the analyzer must substitute the M1b
  spread explicitly and say so in part 6; (2) k*-selection-variance risk —
  on `ext__helmholtz_2d` the argmin picked k=1, which scored 52% worse than
  k=all on held-out test; the analyzer should report k* stability across
  fold seeds, not just the point estimate; (3) the A:1≡B:1 ladder-rung gap
  is an init-variance lower bound only, not a tight estimate. Orchestrator
  raised the panel job's walltime 2h→3h30 in response to finding 5 before
  submitting.
- **r2s2_stacked-B2 guard leg COMPLETED this run**: job `66187053`,
  2.4 min elapsed (`heat_local`/`fluid`/`sharp__sod_1d`, 2 epochs),
  confirmed COMPLETED (exit 0:0) in `sacct`, no longer in `squeue` — upserted
  into `state/timing_ledger.json` as the round's 11th entry.
- **r2s4_diag-B2 mechanism-analyzer turn-1 COMPLETE this run (no card
  change)**: 6/6 per-dataset reanalyses landed. Headline finding: the
  I-vs-T (information-vs-transfer) dissociation is EXPLAINED — the aux-LF
  target is exactly as condition-unidentifiable as HF on 4/5 datasets
  because the aux head duplicates the main task (the certified "information
  gap" is an INPUT statement; the transfer null is a TARGET statement — two
  different channels, not a contradiction). `ext__helmholtz_2d` remains the
  lone harmful exception. The `sharp__cahn_hilliard` info-gap miss is a
  support failure (`d_min` 3.12 in 19-d) vs `sharp__fisher_kpp_2d`'s
  aleatoric explanation — two distinct mechanisms behind one null.
  STRUCTURAL note: `lf[:n_hf]` gave the aux head only 5/170 `ifc_poisson`
  rows, so it could not reach r2s3's win by construction. A fast float32
  ceiling-tool variant was staged for register promotion. Turn 2 dispatched
  (helmholtz sign flip, cross-referencing r2s3-B2 as the direct null-supply
  test) — not yet started at this check.
- **Timing ledger**: **1 new entry this run** — job `66187053`
  (r2s2_stacked-B2, batch 2, seed 0, guard leg, family
  `r2s2_correctability`, 2.4 min, COMPLETED). Now **11 entries** total, all
  re-validated against current `sacct` output. JSON re-validated as
  parseable. `66185845` and `66187052` remain RUNNING — nothing further to
  upsert for them yet.
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
  build is now in code-review-cleared, seed-0-running state (job `66185845`,
  ~33 min elapsed of a 3h budget).
- **r2s3_lf_train_signal-B2 code-review verdict detail (carried forward)**:
  `reviewed_suggest`, 8/8 PASS (5 nits, none blocking); 5 analyst-facing
  suggestions for the next stage, most notably: quote
  `gate_report.linear_mf_ladder.per_rung['32']` (0.2427) not
  `splits.ref_linear_mf` (1.354, a numerical-tie artifact); F2
  (`A5_lf_norepair` vs `A2`) is an instrument contrast, not
  capacity-matched (alpha 12 vs 4); `_ORACLE`-suffixed keys are
  test-condition-fitted and must never be quoted as arm scores; a TIMEOUT
  on the 3h/17-leg job is a resubmit, not an ALGO failure (idempotent via
  score cache + `last.pt`).
- **r2s4_diag-B2 review finding 3.2b (carried forward)**: B2's in-job 3-seed
  spread randomizes init + batch order ONLY (folds fixed by
  `R2S4B2_SPLIT_SEED=0`) — narrower than B1's constants, which also
  randomized the val split. `operative_threshold = max(certified MCE, in-job
  spread)` stays conservative regardless; if B2's spread is ever installed
  into `state/noise_floor.json` it must be labelled "fold-fixed spread", not
  a drop-in replacement for B1's constants. Not installed as of this run.
- **Timestamp-ahead-of-clock anomaly class (carried forward, no new distinct
  occurrence flagged this run beyond what's already on record)**: prior runs
  flagged `review_notes[0].utc` fields reading ahead of the actual check
  time for `r2s1_direct-B1` and `r2s3_lf_train_signal-B2`. This run's
  `orchestrator_flow.md` entries use an informal "2026-08-01 ~0x:xx PDT"
  wall-clock label for events that, cross-checked against `sacct`'s
  cluster-local clock (`2026-07-31T15:2x-15:3x` local, i.e.
  `2026-07-31T22:2x-22:3x` UTC via the ledger's established +7h offset),
  actually occurred on 2026-07-31 — consistent with the same subagent
  clock-skew pattern, not a new distinct class. No scored quantity affected.
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
  shows 3 card-file deltas this run — `experiment_cards/r2s1_direct/batch_2/B2.json`
  (`drafted`→`built`), `experiment_cards/r2s2_stacked/batch_2/B2.json`
  (`drafted`→`running`), `experiment_cards/r2s4_diag/batch_2/B2.json`
  (no maintainer-visible content delta this run, already-tracked from a
  prior orchestrator write) — all other-subagent writes, none touched by
  this maintainer. Also modified: `state/orchestrator_flow.md`,
  `state/r2s1_direct/current_stage.txt`, `state/r2s2_stacked/current_stage.txt`
  (orchestrator/stream-state owned, outside this maintainer's scope). This
  maintainer's own writes this run: `index.md`, `state/maintainer_report.md`,
  `state/timing_ledger.json` (gitignored, not part of the git-status
  comparison). No Write call this run touched `experiment_cards/`.
