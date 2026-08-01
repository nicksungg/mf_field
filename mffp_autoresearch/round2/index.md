# MFFP Autoresearch Round 2 — Dashboard (updated 2026-08-01T16:47:28Z)

**Second maintainer walk since the operator halt/resume cycle.**
Halt landed 2026-08-01T01:31:54Z (commit `10d4e4c`), resume landed
2026-08-01 ~08:1x PDT (commit `b80e622`).
Auto-sync commits `116a3d9` (main) and `9e05d65` (outputs), both
2026-08-01T16:32:30–49Z, landed ~2 minutes after the prior maintainer run's
RUN END and carry `r2s3_lf_train_signal-B3`'s mechanism-analyzer turn-1
write.
All 4 background agents named in the prior run's briefing remain
live/progressing this run — none treated as abandoned; two of them
(`r2s3_lf_train_signal-B3`, `r2s4_diag-B3`) have advanced from mechanism
turn 1 to turn 2 since the prior check.

## Streams

| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r2s1_direct | 23.0636 (best_floor_panel_geomean) | **3** | r2s1_direct-B1 **complete**; r2s1_direct-B2 **complete**; r2s1_direct-B3 **drafted** | B1/B2 unchanged (complete). B3: builder progressed past family construction into **contract-smoke validation** this run — `models_r2/r2s1_stagefree_permode/` fully populated, `score_panel.py --datasets ext__helmholtz_2d --epochs 2 --seed 0 --no_cache` now running (PID 1586645 + child `smoke_eval.py` PID 1587636, started 09:36 PDT, ~7 min elapsed at this check, not stalled) | **0 live SLURM** for this stream; **1 live local process** (builder contract-smoke) | Builder in progress — contract-smoke validation running, no card-visible checkpoint yet |
| r2s2_stacked | 23.0636 (best_floor_panel_geomean) | **2** | r2s2_stacked-B1 **complete**; r2s2_stacked-B2 **analyzing** | B1 unchanged (complete). B2: still `reanalysis_progress: turn_3` on-card, part 7 null. Register turn's toolcheck PID from the prior run (1482785) has exited; a **new** toolcheck script is now live — PID 1554309, `tools/zero_gradient_stage_ladder.py --family_dir .../r2s2_correctability --datasets sharp__cahn_hilliard --ks 1,16`, started 09:26 PDT, ~17 min elapsed, not stalled — plausibly verifying the "interior-k LF average beats trained corrector" lead carried forward from the prior run's Flags. `tools/index.md` unchanged (no partial/duplicate entry) | **0 live SLURM** for this stream; **1 live local process** (register-turn toolcheck, new PID) | Register turn continuing post-resume — new toolcheck step in progress |
| r2s3_lf_train_signal | 23.0636 (best_floor_panel_geomean) | **3** | r2s3_lf_train_signal-B1 **complete**; r2s3_lf_train_signal-B2 **complete**; r2s3_lf_train_signal-B3 **analyzing** | B1/B2 unchanged (complete). B3: `reanalysis_progress` `null`→**`turn_1`** this run (mechanism-analyzer turn 1 landed and auto-synced in commit `116a3d9`/`9e05d65`); part 6 still null. **Mechanism-analyzer has since progressed to turn 2** — live PIDs 1601912/1601914 (`reanalysis_turn_2_run_f4.sh`, started 09:40 PDT, ~7 min elapsed) and 1606457/1606458 (`tools/null_family_ceiling_audit.py --dataset sharp__allen_cahn_2d`, started 09:42 PDT, ~4 min elapsed), writing into `scratchpad/turn2_f4/` (dir mtime 09:46 PDT — actively updating during this check, not stalled) | **0 live SLURM** (job terminal); **2 live local processes** (turn-2 script + audit tool) | `reanalysis_progress: null`→`turn_1` this run; turn 2 now in progress |
| r2s4_diag | **19.8178** (certified_3seed_panel_geomean, CI95 [19.385, 20.527]) | **3** | r2s4_diag-B1 **complete**; r2s4_diag-B2 **complete**; r2s4_diag-B3 **analyzing** | B1/B2 unchanged (complete). B3: `reanalysis_progress` `null`→**`turn_1`** this run (mechanism-analyzer turn 1 landed; **this write is still uncommitted** at this check, file mtime 16:36:51Z — `git diff` shows only the `reanalysis_progress` field plus JSON re-escaping, no other content touched); part 6 still null. **Mechanism-analyzer has since progressed to turn 2** — live PID 1604205 (`reanalysis_turn_2.py`, started 09:41 PDT, ~9 min elapsed, not stalled) | **0 live SLURM** (job terminal); **1 live local process** (turn-2 script) | `reanalysis_progress: null`→`turn_1` this run (uncommitted); turn 2 now in progress |

**Anchor note**: r2s4_diag remains the only stream with a *certified* anchor
(`certified_3seed_panel_geomean`, 19.8178, replacing the training-free
floor) — r2s1_direct, r2s2_stacked, r2s3_lf_train_signal remain on the
launch-time `best_floor_panel_geomean` anchor (23.0636, `certified_utc`
2026-07-31T14:20:17Z, unchanged). No anchor deltas this run — all 4
`state/anchors/*.json` files' mtimes predate this run's entire window.
All anchors rendered verbatim from `state/anchors/*.json`.

**This run's headline**: **2 on-card deltas**, both
`reanalysis_progress: null`→`turn_1` (`r2s3_lf_train_signal-B3` and
`r2s4_diag-B3`, mechanism-analyzer turn 1 landing on each — one already
auto-synced, one still uncommitted). Both mechanism-analyzers have since
progressed to **turn 2**, live and progressing at this check. The
`r2s1_direct-B3` builder advanced from family construction to
contract-smoke validation. `r2s2_stacked-B2`'s register turn continues with
a new toolcheck step. **No SLURM activity** (0 live `r2-*` jobs, no new
completions — timing ledger unchanged at 16 entries). No card reached
`complete` this run. No reopen candidates, no new guard-trip auto-rejects,
no stream abandonment. All 4 orchestrator-owned `current_stage.txt` files
were refreshed this cycle, resolving the prior run's stale-placeholder flag.

## Running / pending jobs

| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| (none — 0 live SLURM `r2-*` jobs) | — | — | — | — |

**0 live `r2-*` SLURM jobs** at this check (`squeue` shows only 2 unrelated
interactive `bash` jobs; `sacct` 2-day window shows 16 `r2-*` jobs, all
COMPLETED 0:0, identical job-ID set to the timing ledger — no new
completions since the last walk). **5 live local (non-SLURM) agent
processes** at this check, none stalled (elapsed computed via
`ps -o lstart` epoch deltas, not lexical clock reads): `r2s1_direct-B3`
builder contract-smoke (PID 1586645/1587636, ~7 min), `r2s2_stacked-B2`
register-turn toolcheck (PID 1554309, ~17 min), `r2s3_lf_train_signal-B3`
mechanism-analyzer turn 2 (PID 1601912/1601914 + 1606457/1606458, ~7/~4
min), `r2s4_diag-B3` mechanism-analyzer turn 2 (PID 1604205, ~9 min).

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
continuing, new toolcheck step in progress, part 7 still null),
`r2s3_lf_train_signal-B3` (`analyzing`, part 5 written/falsified, part 6
pending, mechanism-analyzer now on turn 2) and `r2s4_diag-B3` (`analyzing`,
part 5 written/falsified, mechanism-analyzer now on turn 2) are all
actively open but none has part 7 written — not listed here until each card
itself closes. `r2s1_direct-B3` remains `drafted` (builder now at
contract-smoke, no part 5 yet).

## Flags

- **`r2s3_lf_train_signal-B3` mechanism-analyzer turn 1 landed this run**
  (`reanalysis_progress: null`→`turn_1`, auto-synced in `116a3d9`/`9e05d65`),
  **already progressed to turn 2** — live PIDs 1601912/1601914
  (`reanalysis_turn_2_run_f4.sh`) and 1606457/1606458
  (`tools/null_family_ceiling_audit.py`), writing into
  `scratchpad/turn2_f4/` (updated during this very check). Part 5's
  knife-edge spread-vs-mce clause reading (carried forward from the prior
  run) is presumably the subject of this turn's F4 audit — worth checking
  next cycle whether it resolved.
- **`r2s4_diag-B3` mechanism-analyzer turn 1 landed this run**
  (`reanalysis_progress: null`→`turn_1`, **still uncommitted** — file mtime
  16:36:51Z, no other content touched per `git diff`), **already progressed
  to turn 2** — live PID 1604205 (`reanalysis_turn_2.py`). Part 5's
  falsified verdict (F3 exception dead, F4a instrument-agreement limb
  fired on 4/4 sharp datasets, proj_best = proj_nn tautology flagged by the
  card itself) is presumably the subject of turn 2 — worth checking next
  cycle.
- **`r2s2_stacked-B2` register turn continuing**: the prior run's toolcheck
  PID (1482785) has exited; a new toolcheck script is live (PID 1554309,
  `tools/zero_gradient_stage_ladder.py --datasets sharp__cahn_hilliard
  --ks 1,16`, ~17 min elapsed) — plausibly verifying the "interior-k LF
  average beats trained corrector" lead flagged in the prior run's Flags.
  Part 7 still not written on-card.
- **`r2s1_direct-B3` builder advanced to contract-smoke validation**:
  `models_r2/r2s1_stagefree_permode/` fully populated, `score_panel.py`
  running (PID 1586645/1587636, ~7 min elapsed, `scratchpad/
  contract_smoke.log` present but still 0 bytes — run in flight, not
  stalled).
- **Stale orchestrator-owned files — RESOLVED this run**: all 4
  `state/{stream}/current_stage.txt` files, previously flagged as stuck on
  halt-window placeholder text, were refreshed by the orchestrator this
  cycle to reflect each stream's actual current stage (see Streams table).
- **Round-level instrument-defect pattern (carried forward)**:
  `r2s1_direct`'s post-hoc-blend-stage instrument-error class,
  `r2s2_stacked-B2`'s statistic mis-specification/estimator-bias findings,
  and `r2s3_lf_train_signal-B3`'s knife-edge spread-vs-mce clause reading
  remain 3 independent streams flagging instrument-sensitivity issues —
  worth folding into the same round-report action once both B3
  mechanism-analyzers land part 6.
- **Timing ledger**: **unchanged this run** — 16 entries, identical
  job-ID set to the union of all cards' `job_ids` (0 new completions since
  the last walk). Re-validated as parseable JSON.
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
- No reopen candidates on any of the 9 cards. No `blocked.md` file exists
  (no stream has ever blocked). **No abandoned streams** — none qualify
  (r2s1/r2s3/r2s4 at batch 3 with clean prior closes; r2s2 at batch 2 with a
  clean B1 close — no skip/block history anywhere). `state/streams/`
  directory still does not exist — consistent with no abandonments ever
  being needed.
- Repo hygiene: `git status --short experiment_cards/` shows exactly 1
  modified file this run, a legitimate other-agent (mechanism-analyzer)
  write still in progress: `experiment_cards/r2s4_diag/batch_3/B3.json`
  (`reanalysis_progress` field only, plus JSON re-escaping).
  `r2s3_lf_train_signal/batch_3/B3.json`'s equivalent turn-1 write already
  landed in the auto-sync commit and shows clean. This maintainer's own
  writes this run: `index.md`, `state/maintainer_report.md`.
  `state/timing_ledger.json` untouched (no new entries to upsert). No
  Write call this run touched `experiment_cards/`.
