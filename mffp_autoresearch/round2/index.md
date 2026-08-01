# MFFP Autoresearch Round 2 — Dashboard (updated 2026-08-01T00:34:17Z)

## Streams

| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r2s1_direct | 23.0636 (best_floor_panel_geomean) | **2** | r2s1_direct-B1 **complete**; r2s1_direct-B2 **analyzing** | **B1: unchanged, still COMPLETE.** **B2: no card-content delta this run** (still `reanalysis_progress: turn_2`, `6_analysis: null` — same write-ordering lag). Landed content so far: initial-analysis FALSIFIED (L1 fired on 2/5 datasets — `sharp__allen_cahn_2d` +6.151 skill/6.99x mce, `sharp__cahn_hilliard` +1.296 skill/14.21x mce — overturning B1's "capacity buys nothing" claim on `cahn_hilliard`; L2 fired 4.7x; L3/L4 did not fire); panel geomean 18.3622 (informational). Mechanism turn 1: L2 deficit traced to a **selection-rule ARITY BUG** (set-head recovers 0.513 skill units = 5.6x mce non-oracle); basis capacity NOT the bottleneck. Mechanism turn 2 (per `orchestrator_flow.md`, not yet on-card): `allen_cahn`'s L1 firing is a **POST-HOC-STAGE ARTIFACT** (head beats the RAW decoder by +26.70 skill/30.3x mce; the blend is an error-decorrelation ensemble that pays the head almost nothing, cos 0.998 with `dc_only`; a 10-param per-mode OOF quadratic beats the 15.85M-param decoder by 23.6x mce); `cahn_hilliard`'s nonlinearity hypothesis is refuted (affine stage selected all modes on its own), residual (8.55x mce) attributed to a spatial bias on unidentifiable modes 2-3; `pfc`/`fisher_kpp` remain empty/dead cells. **Turn 3 mechanism script now confirmed live via `ps aux`** (PID 223413, `reanalysis_turn_3.py` running in the B2 worktree, ~11 min elapsed at this check — started before the prior run's close but only confirmed live this run) | **0 live SLURM** (seed-0 job `66189580` terminal, unchanged); **1 live local process** (turn-3 mechanism script, PID 223413) | Turn-3 mechanism script confirmed live via `ps aux` (no card-content delta) |
| r2s2_stacked | 23.0636 (best_floor_panel_geomean) | **2** | r2s2_stacked-B1 **complete**; r2s2_stacked-B2 **analyzing** | **B1: unchanged, still COMPLETE.** **B2: no card-content delta this run** (still `reanalysis_progress: turn_2`, `6_analysis: null`). Landed-so-far: turn 1 traced F1 to a statistic mis-specification (uncentred cross-spectra vs affine corrector class; centred repair flips `B:all`'s gamma to 0.99-1.00, F1 fires on 0 cells). Turn 2: the 2 surviving non-`B:all` F3 cells traced to **ESTIMATOR BIAS** (intermediate statistic is a measurable function of `sigma(cond)` but the true population statistic is 0 by DPI; zero-information control reproduces the firings to ≤0.005; excess anti-correlates with the conditioner residual at −0.560); F2 restated as an **endpoint-comparison artifact** (interior-k beats both k=1/k=all on 4/4; job's own k* already interior). **All three fired falsification clauses are now traced to statistic/instrument defects, not a real model deficiency.** Candidate real lead flagged: a training-free interior-k LF average beats the trained corrector on `allen_cahn`/`cahn_hilliard`. **Write-ordering lag persists, unchanged this run** (still 2 full turns' content not yet on-card). Turn-3 script continues running (same PID as last check, ~15 min elapsed — confirms it did not stall or crash) | 0 live SLURM (both legs terminal, unchanged); **1 live local process** (turn-3 mechanism script, PID 221177, continuing) | No card-content delta; turn-3 script continuing to run (not stalled) |
| r2s3_lf_train_signal | 23.0636 (best_floor_panel_geomean) | **3** | r2s3_lf_train_signal-B1 **complete**; r2s3_lf_train_signal-B2 **complete** | **B1/B2: unchanged this run, both still COMPLETE** (B2 closed last run — sixth card of the round, `confirmed` verdict, 2 tools promoted). **B3 pre-card pipeline advancing** (no `B3.json` yet, so nothing here is walked by the card glob — noted for situational awareness): the B3 brainstormer has started and produced `brainstormer/r2s3_lf_train_signal/batch_3/summary_so_far.md` (new this run, mtime ~4 min after the prior run's close) — synthesizes the websearcher's `preempted-but-MF-composition-open` verdict, program §12.3 conventions, B1/B2 prior-card findings, cross-stream notes (r2s4-B2's target-side null result; r2s1-B2's fisher_kpp dead-cell corroboration), and a 6-item UNKNOWN list (headline: 4/6 panel datasets have **zero affine coverage deficit** at N_hf=5 yet `fisher_kpp` still shows a claimable +1.2228 effect — the single most informative open question). No `iteration_1.md`/`report.md` yet — brainstormer mid-flight, not complete | **0 live SLURM** (seed-0 job terminal, unchanged); B3 not built (brainstorm in progress, no worktree/job yet) | New: B3 brainstormer stage-1 synthesis (`summary_so_far.md`) landed |
| r2s4_diag | **19.8178** (certified_3seed_panel_geomean, CI95 [19.385, 20.527]) | **3** | r2s4_diag-B1 **complete**; r2s4_diag-B2 **complete**; r2s4_diag-B3 **drafted** | **B1/B2: unchanged, both still COMPLETE.** **B3: no card change this run** (still `status: drafted`, `job_ids: []`, `build_commit: null` — pre-SLURM). Builder actively progressing: **a contract-smoke validation run confirmed live via `ps aux`** (PID 219145, `score_panel.py`/`smoke_eval.py` for `models_r2/r2s4_b3_projection` on `ext__helmholtz_2d`, epochs=2, seed=0, ~18.7 min elapsed at this check — this is new confirmation beyond the prior run's "model files landed" observation; not yet a SLURM submission). No git commit yet, no SLURM job submitted yet | **0 live SLURM** (all prior seeds terminal, unchanged; B3 not yet submitted); **1 live local process** (builder contract-smoke validation run, PID 219145) | Builder's contract-smoke validation run confirmed live (pre-SLURM) |

**Anchor note**: r2s4_diag remains the only stream with a *certified* anchor
(`certified_3seed_panel_geomean`, 19.8178, replacing the training-free floor)
— r2s1_direct, r2s2_stacked, r2s3_lf_train_signal remain on the launch-time
`best_floor_panel_geomean` anchor (23.0636, `certified_utc` 2026-07-31T14:20:17Z,
unchanged). No anchor deltas this run. All anchors rendered verbatim from
`state/anchors/*.json`.

**This run's headline**: **no card-content deltas** — all 9 cards are
byte-identical to the prior run's close (verified via `stat -c %Y` mtime,
all strictly before the prior run's RUN END epoch). Activity this run is
entirely sub-card: (1) the `r2s3_lf_train_signal` B3 brainstormer has begun
and produced a stage-1 synthesis (`summary_so_far.md`, new); (2)
`r2s1_direct-B2`'s turn-3 mechanism script is now confirmed live via
`ps aux` (was dispatched before the prior run's close but not confirmed
live then); (3) `r2s2_stacked-B2`'s turn-3 script continues running, same
PID as the prior check, confirming it has not stalled; (4) `r2s4_diag-B3`'s
builder is now confirmed running a pre-SLURM contract-smoke validation.
SLURM state, timing ledger, anchors, gates, and noise floor are all
unchanged.

## Running / pending jobs

| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| (none — 0 live SLURM `r2-*` jobs) | — | — | — | — |

**0 live `r2-*` SLURM jobs** at this check (squeue + sacct cross-checked, no
transient-empty false positives — `sacct` shows all 14 `r2-*` jobs COMPLETED,
byte-identical to the last check; `squeue` shows 0 `r2-*` entries, only
unrelated interactive `bash` jobs and round-1 `r1-*` PENDING seed-confirm
jobs, out of this maintainer's scope). **3 live local (non-SLURM) processes**
confirmed via `ps aux` at this check: PID 223413 (`r2s1_direct-B2` turn-3
mechanism script, ~11 min elapsed, newly confirmed live this run), PID
221177 (`r2s2_stacked-B2` turn-3 mechanism script, ~15 min elapsed,
continuing from the prior check — not stalled), PID 219145 (`r2s4_diag-B3`
builder's pre-SLURM contract-smoke validation run on
`models_r2/r2s4_b3_projection`, ~18.7 min elapsed, newly confirmed live
this run).

## Completed cards

| Card | Type | Panel geomean skill (±CI) | Falsification verdict | Tools promoted |
|---|---|---|---|---|
| r2s4_diag-B1 | diagnostic | 19.8178 IQM, CI95 [19.385, 20.527] (3 seeds) | n/a (diagnostic — no falsification clauses); mechanism register complete, part 7 written | 2 tools, both correctly indexed: `tools/conditional_mean_collapse.py`, `tools/condition_predictability_ceiling.py` |
| r2s4_diag-B2 | diagnostic | 19.8829 own single-run 3-seed geomean (T0 primary arm; reproduces B1's certified band, not a re-certification) | **falsified**: the aux-LF-TARGET head is worth nothing at any N_fit in 20-320 on 15/15 dataset×N cells (7.42-101.12x the certified floor's resolving power); explicitly does NOT license the broader "LF doesn't help" claim (input-side + disjoint-supply channels untouched) | **3 tools**: `tools/ladder_pair_alignment_audit.py`, `tools/shrinkage_curve_anatomy.py`, `tools/condition_predictability_ceiling_fast.py` |
| r2s1_direct-B1 | model | 19.6444 (single seed 0, no CI yet) | **falsified in a split reading**: floors clause CONFIRMED (beats best floor on all 6 panel datasets, geomean −14.8% vs anchor) but the implicit architecture clause FALSIFIED — a ~156-parameter closed-form head reaches 19.0553/19.1666, statistically indistinguishable from the 15.9M-parameter shipped arm (0.52x the certified panel min_claimable_effect) | 2 tools, both correctly indexed: `tools/band_gain_counterfactual.py`, `tools/condition_identifiable_rank.py` |
| r2s3_lf_train_signal-B1 | model | 25.3919 (`rung_native`, single seed 0) | **falsified in a split reading**: F1 (primary, architecture) FALSIFIED with a 7.35-skill-unit sign inversion on `ifc_poisson`, traced to a shared-scaler confound; but the motivating INFORMATION claim is CONFIRMED — an architecture-free estimator recovers +3.2317 skill units from the same 170 disjoint LF rows (18.83% of the law's coefficient energy at cos 0.9993). F2 (native vs upsampled) survived; F3 (degeneracy) verdict depends on provisional vs re-certified floor thresholds (both recorded) | 2 tools, both correctly indexed: `tools/affine_ladder_voi.py`, `tools/posthoc_repair_ladder.py` |
| r2s2_stacked-B1 | model | 14.0756 (single seed 0, no CI yet; scored arm `frozen`; ~all margin from the unpaired `ifc_poisson` column) | clean negative with a measured mechanism, not a raw binary: the falsification clause was a conjunction that did **not** fire — conjunct 1 ("improve on `emul_only` by ≥2.0 skill units") **held** (measured improvement 0.0061, 326x below threshold) but conjunct 2 ("beat the NN-in-condition floor") **failed to hold** (beat it by 11.90 skill units, 130x the noise floor). Round-level headline (I8): a stacked intermediate representation is a re-parameterisation of the condition→HF hypothesis class, not a new information channel | 2 tools, both correctly indexed and register-confirmed: `tools/reachable_set_rank_audit.py`, `tools/surrogate_coherence_eligibility.py` |
| r2s3_lf_train_signal-B2 | model | not computed (3-of-6 panel only, informational: `A2_lf_cov_null` 8.8918 vs `A0_nolf` 16.0642 on `ifc_poisson`/`sharp__cahn_hilliard`/`sharp__fisher_kpp_2d`) | **confirmed** (not falsified); `cratered_verdict: proceed_to_seeds_1_2`; 1 guard flag (`heat_local`, 18.86x, reasoned structural not `auto_reject`) | **2 tools**: `tools/design_coverage_audit.py`, `tools/null_family_ceiling_audit.py` (now a six-instrument identifiability/coverage family with the 4 tools above) |

`r2s1_direct-B2` (`analyzing`, `reanalysis_progress: turn_2`, turn-3
mechanism script confirmed live), `r2s2_stacked-B2` (`analyzing`,
`reanalysis_progress: turn_2`, turn-3 script continuing) and `r2s4_diag-B3`
(`drafted`, builder mid-validation, no SLURM job yet) are all actively open
but none has part 7 written (or, for B3, any build/job yet) — not listed
here until each card itself closes.

## Flags

- **No card-content deltas this run**: all 9 cards confirmed byte-identical
  to the prior run's close (`stat -c %Y` mtime on every card strictly
  before the prior run's RUN END epoch, 1785544140). Only sub-card activity
  (live processes, brainstormer stage-1 output) advanced this run.
- **`r2s3_lf_train_signal` B3 brainstormer stage 1 landed**:
  `brainstormer/r2s3_lf_train_signal/batch_3/summary_so_far.md` (new,
  untracked). Synthesizes the batch-2 websearcher's `preempted-but-MF-
  composition-open` verdict on the panel-completion ±LF ablation, program
  §12.3 conventions, B1/B2 prior findings, and cross-stream notes. Flags
  the round's single most informative open question: 4/6 panel datasets
  (`fisher_kpp`, `helmholtz`, `allen_cahn`, `pfc`) have **zero affine
  coverage deficit** at N_hf=5 per a fresh `design_coverage_audit.py` run
  (`m_reduction_full = 0`, `NO_DEFICIT_TO_FIX`), yet `fisher_kpp` still
  shows a claimable +1.2228 skill-unit effect from LF — whether the
  other 3 zero-deficit datasets behave the same way is unmeasured. No
  `iteration_1.md`/`report.md` yet.
- **`r2s1_direct-B2` turn-3 mechanism script confirmed live** (PID 223413,
  `reanalysis_turn_3.py`, ~11 min elapsed) — was dispatched before the
  prior run's close (script file mtime inside the prior run's window) but
  not confirmed live via `ps aux` in that run's check; confirmed running
  this run, not stalled.
- **`r2s2_stacked-B2` write-ordering lag — unchanged this run, still
  escalated**: the card's own `6_analysis` field is still `null` even
  though `reanalysis_progress` has been at `turn_2` for two consecutive
  checks and a turn-3 mechanism script (PID 221177) continues running —
  the lag between narrated/in-progress content and what actually lands on
  the card spans a full 2 turns' worth of findings (statistic
  mis-specification in turn 1; estimator bias + endpoint-comparison
  artifact in turn 2). Script confirmed not stalled (same PID, elapsed
  time advancing normally) — flagged for continued watching, not yet a
  genuine anomaly.
- **Real lead flagged inside `r2s2_stacked-B2` turn 2** (not yet a card
  claim): a training-free interior-k LF average reportedly beats the trained
  corrector on `allen_cahn`/`cahn_hilliard` — worth tracking into part 6/7
  once it lands on-card.
- **`r2s1_direct-B2` FALSIFIED — overturns a B1 headline claim (carried
  forward, unchanged this run)**: B2's in-job Wiener-calibrated decoder beats
  the scored closed-form arm by 1.296 skill units on `sharp__cahn_hilliard`
  (14.21x the certified `min_claimable_effect`), contradicting B1's
  "~156-parameter head is statistically indistinguishable from the
  15.9M-parameter shipped decoder" finding specifically on that dataset.
- **`r2s4_diag-B3` builder progressing pre-SLURM**: contract-smoke
  validation (`score_panel.py`/`smoke_eval.py`, `ext__helmholtz_2d`,
  epochs=2, seed=0) confirmed live via `ps aux` (PID 219145, ~18.7 min
  elapsed) — model-family files (`manifest.json`, `model.py`,
  `smoke_eval.py`, `projection.py`, `lf_reference.py`, `INSPIRATION.md`)
  already landed in the worktree per the prior run's check; no git commit
  or SLURM submission yet.
- **`r2s3_lf_train_signal-B2` closed — sixth card of the round (carried
  forward, unchanged this run)**: register turn landed 5/5 last run
  (`analyzing`→`complete`), `confirmed` verdict, 2 tools promoted
  (`design_coverage_audit.py`, `null_family_ceiling_audit.py`) into a
  six-instrument identifiability/coverage family. Part 7 explicitly frames
  B3 as a **measurement-completion card** (or an authorised close-on-B2
  fallback) — the brainstormer's stage-1 output (see above) engages with
  both options.
- **Timing ledger**: **no upsert this run** — no new terminal `r2-*` SLURM
  states (all 14 jobs in `sacct` were already COMPLETED and ledgered;
  `r2s4_diag-B3` has not submitted anything to SLURM yet, still in the
  pre-SLURM contract-smoke validation stage). Still **14 entries** total,
  JSON re-validated as parseable (`json.load` succeeded).
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
- No reopen candidates on any of the 9 cards. No `blocked.md` file exists (no
  stream has ever blocked). No abandoned streams — none are possible yet
  (r2s1/r2s2 at batch 2 with clean B1 closes; r2s3/r2s4 at batch 3, all prior
  batches clean closes — no skip/block history anywhere). `state/streams/`
  directory still does not exist — consistent with no abandonments ever
  being needed.
- Repo hygiene: `git status --short .` (round root, excluding `worktrees/`)
  shows, at this check, 1 modified card file —
  `experiment_cards/r2s1_direct/batch_2/B2.json` (unchanged content since
  the prior run, already captured then) — an other-subagent write, not
  touched by this maintainer. Also modified (this maintainer's own
  uncommitted writes from prior runs, not yet auto-synced): `index.md`,
  `state/maintainer_report.md`. Other-agent/orchestrator-owned
  modified/untracked files this run (none touched by this maintainer):
  `state/orchestrator_flow.md`, `state/r2s3_lf_train_signal/
  current_stage.txt`, `websearches/r2s3_lf_train_signal/batch_3/
  {iteration_5.md, report.md}` (unchanged since the prior run),
  `brainstormer/r2s3_lf_train_signal/batch_3/` (new, untracked — stage-1
  `summary_so_far.md`). This maintainer's own writes this run: `index.md`,
  `state/maintainer_report.md` (`state/timing_ledger.json` content
  unchanged, gitignored, not part of the git-status comparison). No Write
  call this run touched `experiment_cards/`.
