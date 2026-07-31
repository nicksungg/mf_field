# MFFP Autoresearch Round 2 — Dashboard (updated 2026-07-31T23:03:00Z)

## Streams

| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r2s1_direct | 23.0636 (best_floor_panel_geomean) | **2** | r2s1_direct-B1 **complete**; r2s1_direct-B2 **built** | **B1: unchanged, still COMPLETE.** **B2: no card change this run**, still `built` / `review_notes: []`. Code-review continues — **directly confirmed live via `ps aux`**: PID 165937, a `smoke_eval.py` re-run of `models_r2/r2s1_selected_form` on `sharp__cahn_hilliard` (spot-check script sink `scratchpad/ch_run.log` / `reviewer_ch_check.json`), ~2:22 CPU time, `R` state — the reviewer independently re-verifying a leg, no verdict yet. `state/r2s1_direct/current_stage.txt` still reads "code-review (B2 dispatched 2026-08-01; build `d844bec`, smoke green, rank-statistic TBD to adjudicate)" | 0 live SLURM (no job yet; awaiting code-review); 1 live local process (reviewer spot-check, PID 165937) | No card-status change this run — code-review in progress, live spot-check process observed |
| r2s2_stacked | 23.0636 (best_floor_panel_geomean) | **2** | r2s2_stacked-B1 **complete**; r2s2_stacked-B2 **running** | **B1: unchanged, still COMPLETE. B2: no card change this run** — seed 0 panel job `66187052` continues RUNNING, now ~25 min elapsed of its 3:30:00 budget (raised 2h→3h30 per code-reviewer finding 5), steady, no state transition. Guard leg `66187053` remains COMPLETED (upserted last run) | **1 live** (`66187052`, seed 0 panel, RUNNING, ~25 min elapsed) | No change this run — job continues, same job-id, steady progress |
| r2s3_lf_train_signal | 23.0636 (best_floor_panel_geomean) | **2** | r2s3_lf_train_signal-B1 **complete**; r2s3_lf_train_signal-B2 **analyzing** (new this run) | **B1: unchanged, still COMPLETE.** **B2 advanced this run — card delta**: `status` `running`→`analyzing`. Job `66185845` (seed 0, 17 serial legs) transitioned RUNNING→COMPLETED (00:41:38 elapsed, exit 0:0 — well under its 3h budget, which was conservatively sized off B1's 6-dataset/77-min comparator; this card only scores a 3-dataset panel). All 17 per-leg result JSONs landed cleanly. The initial-analyzer then ran and wrote part 5: `falsification_verdict: confirmed`, `cratered_verdict: proceed_to_seeds_1_2`. The card pre-registers only 3 of 6 panel datasets (ifc_poisson, sharp__cahn_hilliard, sharp__fisher_kpp_2d) — explicitly **not comparable** to the 6-dataset launch anchor (flagged as such in part 5 itself). Informational 3-of-6 partial-panel geomean: primary arm `A2_lf_cov_null` **8.8917** vs no-LF control `A0_nolf` **16.0642** (lower is better). Per-dataset vs the anchor's own floor: ifc_poisson beats floor by 6.60 skill units (≫ 0.938 MCE), cahn_hilliard beats floor by 10.06 units (≫ 0.091 MCE), fisher_kpp is 3.35 units *worse* than floor (beyond its tiny 0.0007 MCE — a genuine per-dataset miss). `orchestrator_flow.md` has not yet logged the initial-analyzer's completion (write-ordering lag behind the card content, a recurring benign pattern) | 0 live SLURM (seed 0 terminal); 0 live local processes for this stream at this check | Job `66185845` COMPLETED → initial-analyzer landed (`confirmed` / `proceed_to_seeds_1_2`); card `running`→`analyzing` |
| r2s4_diag | **19.8178** (certified_3seed_panel_geomean, CI95 [19.385, 20.527]) | **2** | r2s4_diag-B1 **complete**; r2s4_diag-B2 **analyzing** | **B1: unchanged, still COMPLETE. B2: `status` unchanged (`analyzing`), but the mechanism-analyzer's turn 3 landed this run** (card mtime 22:53:13Z, inside this run's window): `reanalysis_progress` `turn_2`→`turn_3`; `6_analysis.findings` grew from 10 to **18** (adds T3-F1..T3-F8). Headline: 4/5 datasets are AT the N→∞ asymptote already at N=320 (cahn_hilliard the lone sample-limited dataset, slope 0.233 accelerating); lambda*(N) crosses 1 on cahn_hilliard (0.767→1.117 — the over-amplified-when-starved / over-smoothed-when-fed §12.4 overfitting anatomy); F3 re-confirmed as a certified null on a sensitive instrument (N-effects resolved 7.4-101x the floor while all 15 transfer-effect cells sit below it); support-not-identifiability predicts the training-free regime 5/5. Certified license: "the aux-LF-TARGET head is worth nothing at any N." Explicitly **not** licensed: "LF doesn't help" overall — the input-side and disjoint-supply channels are untouched by this card (r2s3-B2, which just completed above, is the direct test of the disjoint-supply channel). Orchestrator dispatched a "register turn" next (3 tool promotions incl. a pair-alignment pre-flight). `state/r2s4_diag/current_stage.txt` is stale relative to this (still shows the pre-turn-3 label) — write-ordering lag, not a scoring issue. Part 7 still absent — correctly still `analyzing`, not `complete` | 0 live SLURM (all 3 seeds terminal, unchanged); 0 live local processes at this check (turn-3 loop finished, register turn not yet started) | Mechanism-analyzer turn 3 COMPLETE (18/18 cumulative findings, N-scaling/overfitting-anatomy headline) → register turn dispatched |

**Anchor note**: r2s4_diag remains the only stream with a *certified* anchor
(`certified_3seed_panel_geomean`, 19.8178, replacing the training-free floor)
— r2s1_direct, r2s2_stacked, r2s3_lf_train_signal remain on the launch-time
`best_floor_panel_geomean` anchor (23.0636, `certified_utc` 2026-07-31T14:20:17Z,
unchanged). No anchor deltas this run. All anchors rendered verbatim from
`state/anchors/*.json`.

**This run's headline**: an unusually live check — two cards changed state
*during* the walk itself. `r2s3_lf_train_signal-B2`'s seed-0 job (`66185845`)
completed and its initial-analyzer landed a `confirmed`/`proceed_to_seeds_1_2`
verdict on a partial (3-of-6-dataset) panel; card moved `running`→`analyzing`.
`r2s4_diag-B2`'s mechanism-analyzer completed turn 3 (N-scaling law +
overfitting anatomy), taking cumulative findings to 18/18 and licensing a
narrow certified claim ("aux-LF-TARGET head worth nothing at any N") while
explicitly *not* licensing the broader "LF doesn't help" claim; `status`
stayed `analyzing` pending part 7. `r2s2_stacked-B2`'s panel job continues
steadily (~25 min of 3:30:00). `r2s1_direct-B2` remains in code-review with a
live reviewer spot-check process observed. Timing ledger **upserted with 1
new entry** this run (`66185845`, r2s3_lf_train_signal-B2 seed 0, 41.63 min)
— now **12 entries** total.

## Running / pending jobs

| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| 66187052 | r2s2_stacked-B2 (seed 0 panel) | RUNNING | ~25 min | hpc-sm-01-04 |

**1 live `r2-*` SLURM job** this check (squeue + sacct cross-checked):
`66187052` (r2s2_stacked-B2 seed 0 panel), continuing steadily. `66185845`
(r2s3_lf_train_signal-B2 seed 0) transitioned RUNNING→COMPLETED within this
run's window (00:41:38 elapsed, exit 0:0, confirmed terminal in `sacct` —
not a transient-empty false positive) and has been upserted into the timing
ledger. 1 live local (non-SLURM) process confirmed via `ps aux`:
r2s1_direct-B2's code-reviewer spot-check on `sharp__cahn_hilliard` (PID
165937, ~2:22 CPU time, `R` state). Unrelated interactive `bash` jobs and
round-1 `r1-*` jobs also visible in the queue — out of this maintainer's
scope, not itemized here.

## Completed cards

| Card | Type | Panel geomean skill (±CI) | Falsification verdict | Tools promoted |
|---|---|---|---|---|
| r2s4_diag-B1 | diagnostic | 19.8178 IQM, CI95 [19.385, 20.527] (3 seeds) | n/a (diagnostic — no falsification clauses); mechanism register complete, part 7 written | 2 tools, both correctly indexed: `tools/conditional_mean_collapse.py`, `tools/condition_predictability_ceiling.py` |
| r2s1_direct-B1 | model | 19.6444 (single seed 0, no CI yet) | **falsified in a split reading**: floors clause CONFIRMED (beats best floor on all 6 panel datasets, geomean −14.8% vs anchor) but the implicit architecture clause FALSIFIED — a ~156-parameter closed-form head reaches 19.0553/19.1666, statistically indistinguishable from the 15.9M-parameter shipped arm (0.52x the certified panel min_claimable_effect) | 2 tools, both correctly indexed: `tools/band_gain_counterfactual.py`, `tools/condition_identifiable_rank.py` |
| r2s3_lf_train_signal-B1 | model | 25.3919 (`rung_native`, single seed 0) | **falsified in a split reading**: F1 (primary, architecture) FALSIFIED with a 7.35-skill-unit sign inversion on `ifc_poisson`, traced to a shared-scaler confound; but the motivating INFORMATION claim is CONFIRMED — an architecture-free estimator recovers +3.2317 skill units from the same 170 disjoint LF rows (18.83% of the law's coefficient energy at cos 0.9993). F2 (native vs upsampled) survived; F3 (degeneracy) verdict depends on provisional vs re-certified floor thresholds (both recorded) | 2 tools, both correctly indexed: `tools/affine_ladder_voi.py`, `tools/posthoc_repair_ladder.py` |
| r2s2_stacked-B1 | model | 14.0756 (single seed 0, no CI yet; scored arm `frozen`; ~all margin from the unpaired `ifc_poisson` column) | clean negative with a measured mechanism, not a raw binary: the falsification clause was a conjunction that did **not** fire — conjunct 1 ("improve on `emul_only` by ≥2.0 skill units") **held** (measured improvement 0.0061, 326x below threshold) but conjunct 2 ("beat the NN-in-condition floor") **failed to hold** (beat it by 11.90 skill units, 130x the noise floor). Round-level headline (I8): a stacked intermediate representation is a re-parameterisation of the condition→HF hypothesis class, not a new information channel | 2 tools, both correctly indexed and register-confirmed: `tools/reachable_set_rank_audit.py`, `tools/surrogate_coherence_eligibility.py` |

r2s3_lf_train_signal-B2 (`analyzing`, part 5 landed this run — `confirmed`
verdict on a partial 3-of-6-dataset panel, `proceed_to_seeds_1_2`) and
r2s4_diag-B2 (`analyzing`, mechanism-analyzer now 18/18 findings across 3
turns, register turn dispatched) are both actively closing but part 7 has
not been written on either — not listed here until the card itself closes.
r2s1_direct-B2 (`built`, awaiting code-review, live spot-check process) and
r2s2_stacked-B2 (`running`, seed 0 panel job `66187052` in flight) are not
listed here either.

## Flags

- **One card `status` delta this run**: `r2s3_lf_train_signal-B2`
  `running`→`analyzing` (seed 0 job `66185845` COMPLETED; initial-analyzer
  landed `confirmed`/`proceed_to_seeds_1_2` on an explicitly-partial,
  non-anchor-comparable 3-of-6-dataset panel). `r2s4_diag-B2`'s `status`
  field itself is unchanged (`analyzing`) but its `reanalysis_progress`
  advanced `turn_2`→`turn_3` with 8 new findings (18 total) — a substantive
  content delta without a status-field delta. All other 6 cards' `status`
  byte-identical to last run: `r2s1_direct-B1`/`r2s2_stacked-B1`/
  `r2s3_lf_train_signal-B1`/`r2s4_diag-B1` `complete`; `r2s1_direct-B2`
  `built`; `r2s2_stacked-B2` `running`. `reopen_candidate` is `false` on all
  8 cards. No `debug_notes` on any card — no failures needing a debugger.
- **r2s3_lf_train_signal-B2 initial-analyzer detail**: falsification
  `confirmed`, cratered `proceed_to_seeds_1_2`. Per-dataset vs the anchor's
  own floor (lower is better): ifc_poisson −6.60 skill units vs floor (MCE
  0.938), cahn_hilliard −10.06 units vs floor (MCE 0.091), fisher_kpp
  **+3.35 units worse than floor** (MCE only 0.0007 — a genuine, resolvable
  per-dataset miss even though the other two datasets win big). The card's
  part 4 pre-registered exactly this 3-of-6 scope ("no criterion-2 panel
  claim") — the informational partial-panel geomean (primary arm 8.8917 vs
  no-LF control 16.0642) is recorded for cratered-screening only and is
  explicitly flagged as not comparable to the 23.0636 six-dataset anchor.
- **r2s4_diag-B2 mechanism-analyzer turn 3 detail**: 4/5 datasets already at
  the N→∞ asymptote at N=320 (cahn_hilliard the lone sample-limited case,
  slope 0.233 and accelerating); lambda*(N) crosses 1 exactly on
  cahn_hilliard (0.767→1.117) — the §12.4 overfitting-anatomy signature
  (over-amplified when starved of samples, over-smoothed once fed more); F3
  re-confirmed a certified null on a sensitive instrument (N-effects
  resolved 7.4-101x the floor, all 15 transfer-effect cells below it);
  support-not-identifiability (from turns 1-2) predicts the training-free
  regime 5/5. Certified, narrow license: "the aux-LF-TARGET head is worth
  nothing at any N." NOT licensed by this card: the broader claim "LF
  doesn't help" — the input-side channel and the disjoint-supply channel are
  untouched (r2s3-B2, completed this run, is the direct empirical test of
  the disjoint-supply channel, and its per-dataset results above show a
  mixed picture: 2/3 datasets win big, 1/3 loses). Register turn dispatched
  next (3 tool promotions incl. a pair-alignment pre-flight) — not yet
  started at this check.
- **Timing ledger**: **1 new entry this run** — job `66185845`
  (r2s3_lf_train_signal-B2, batch 2, seed 0, family `r2s3_null_supply`,
  41.63 min, COMPLETED, 17-leg sweep over 3 panel datasets, well under its
  3h budget). Now **12 entries** total, all re-validated against current
  `sacct` output. JSON re-validated as parseable.
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
  seed-0 job has now COMPLETED (see above) and its initial-analyzer has
  landed.
- **r2s3_lf_train_signal-B2 code-review verdict detail (carried forward)**:
  `reviewed_suggest`, 8/8 PASS (5 nits, none blocking); 5 analyst-facing
  suggestions for the next stage, most notably: quote
  `gate_report.linear_mf_ladder.per_rung['32']` (0.2427) not
  `splits.ref_linear_mf` (1.354, a numerical-tie artifact); F2
  (`A5_lf_norepair` vs `A2`) is an instrument contrast, not
  capacity-matched (alpha 12 vs 4); `_ORACLE`-suffixed keys are
  test-condition-fitted and must never be quoted as arm scores; a TIMEOUT
  on the 3h/17-leg job is a resubmit, not an ALGO failure (idempotent via
  score cache + `last.pt`). These should now inform the initial-analyzer's
  part 6/7 writeup.
- **r2s4_diag-B2 review finding 3.2b (carried forward)**: B2's in-job 3-seed
  spread randomizes init + batch order ONLY (folds fixed by
  `R2S4B2_SPLIT_SEED=0`) — narrower than B1's constants, which also
  randomized the val split. `operative_threshold = max(certified MCE, in-job
  spread)` stays conservative regardless; if B2's spread is ever installed
  into `state/noise_floor.json` it must be labelled "fold-fixed spread", not
  a drop-in replacement for B1's constants. Not installed as of this run.
- **Timestamp-ahead-of-clock / clock-skew anomaly class (carried forward, no
  new distinct occurrence flagged this run)**: prior runs flagged
  `review_notes[0].utc` fields reading ahead of the actual check time for
  `r2s1_direct-B1` and `r2s3_lf_train_signal-B2`, and an informal
  "2026-08-01 ~0x:xx PDT" wall-clock labelling convention in
  `orchestrator_flow.md` for events that `sacct`'s cluster-local clock
  places on 2026-07-31. This run's fresh entries (turn 3, r2s3-B2
  completion) continue the same "2026-08-01" labelling for events landing
  2026-07-31T22:5x-23:0xZ by UTC — same benign clock-skew pattern, not a new
  distinct class. No scored quantity affected.
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
  shows 2 card-file deltas this run — `experiment_cards/r2s3_lf_train_signal/batch_2/B2.json`
  (`running`→`analyzing`, part 5 landed) and
  `experiment_cards/r2s4_diag/batch_2/B2.json` (turn-3 findings landed,
  `reanalysis_progress` `turn_2`→`turn_3`, `status` unchanged) — both
  other-subagent writes, none touched by this maintainer. Also modified:
  `state/orchestrator_flow.md` (orchestrator-owned, outside this
  maintainer's scope). This maintainer's own writes this run: `index.md`,
  `state/maintainer_report.md`, `state/timing_ledger.json` (gitignored, not
  part of the git-status comparison). No Write call this run touched
  `experiment_cards/`.
