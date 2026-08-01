# MFFP Autoresearch Round 2 — Dashboard (updated 2026-08-01T01:17:18Z)

## Streams

| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r2s1_direct | 23.0636 (best_floor_panel_geomean) | **3** | r2s1_direct-B1 **complete**; r2s1_direct-B2 **complete** | **B1/B2: unchanged this run, both still COMPLETE** (both card mtimes strictly before this run's window). **B3 websearcher completed this run** (report.md + iteration_5.md landed after the prior run's close, cap hit 7/7, pdf-rule honored): C2 (blend = Bates-Granger 1969 minimum-variance combination; the "evaluation-artifact" reading of the round's own finding remains unpublished) is the best-supported composition; C1 open-but-thin; C3 PREEMPTED (supervised-PCA — bug-fix-only reading); C4 unchecked (diagnostic-only). **B3 brainstormer now dispatched** with the B3-or-close + instrument-repair-card option framed (`state/r2s1_direct/current_stage.txt`); `brainstormer/r2s1_direct/batch_3/` exists but is still empty at this check (no `iteration_1.md` yet, no local process observed for it via `ps aux` — likely an LLM-subagent stage not a background script) | **0 live SLURM** (both seed-0 jobs terminal, unchanged); 0 live local processes for this stream at this check | B3 websearcher SUCCESS (7/7); B3 brainstormer dispatched, not yet producing output |
| r2s2_stacked | 23.0636 (best_floor_panel_geomean) | **2** | r2s2_stacked-B1 **complete**; r2s2_stacked-B2 **analyzing** | **B1: unchanged, still COMPLETE.** **B2: no card-content delta this run** (still `reanalysis_progress: turn_2`, `6_analysis: null` — write-ordering lag persists, now spanning 4 checks). Landed-so-far (per `orchestrator_flow.md`, not yet on-card): turn 1 traced F1 to a statistic mis-specification; turn 2 traced the 2 surviving F3 cells to estimator bias + an endpoint-comparison artifact — all three fired falsification clauses now traced to statistic/instrument defects. **Turn-3 mechanism script progressed further this run**: now on its 4th and LAST dataset leg (`sharp__allen_cahn_2d`, PID 237590, a fresh per-leg invocation distinct from the prior run's PID 232585 which has since exited after completing the `fisher_kpp` leg) — `cahn_hilliard`, `phase_field_crystal_2d`, `fisher_kpp_2d` legs all confirmed written to disk this run, only `allen_cahn_2d` remains | 0 live SLURM (both legs terminal, unchanged); **1 live local process** (turn-3 mechanism script, PID 237590, on the last/4th leg) | No card-content delta; turn-3 script wrote its 3rd leg (`fisher_kpp`) and started the 4th/last (`allen_cahn`) |
| r2s3_lf_train_signal | 23.0636 (best_floor_panel_geomean) | **3** | r2s3_lf_train_signal-B1 **complete**; r2s3_lf_train_signal-B2 **complete**; r2s3_lf_train_signal-B3 **built** | **B1/B2: unchanged this run, both still COMPLETE.** **B3: `drafted` -> `built` this run** (card mtime inside this run's window): builder landed 10/10 — build commit `dfcd46c`, mandatory contract smokes exit 0 (including an A0-arm resume test on `ifc_poisson` reproducing bit-identically from checkpoint), deleted-surface negative tests correctly RAISE (`SystemExit` on any of the 4 deleted null-penalty env keys), 26/26 env keys + 33/33 legs verified present, the null-direction-penalty family confirmed fully deleted per the card's spec. `review_notes: []` — **code-reviewer now dispatched** (`state/r2s3_lf_train_signal/current_stage.txt`), not yet landed; no live local process for it observed via `ps aux` (likely LLM-subagent stage). Still no SLURM job (`job_ids: []`) | **0 live SLURM** (B1/B2 seed-0 jobs terminal, unchanged; B3 not yet submitted, awaiting code review before SLURM dispatch) | `drafted` -> `built` (builder SUCCESS 10/10); code-reviewer dispatched next |
| r2s4_diag | **19.8178** (certified_3seed_panel_geomean, CI95 [19.385, 20.527]) | **3** | r2s4_diag-B1 **complete**; r2s4_diag-B2 **complete**; r2s4_diag-B3 **built** | **B1/B2: unchanged, both still COMPLETE.** **B3: `drafted` -> `built` this run** (mtime landed ~29s after this run's initial RUN END, caught during final pre-return re-verification): builder landed its full deliverable — new from-scratch family `models_r2/r2s4_b3_projection/` (FiLM-FNO backbone, width 32/2 blocks/16 modes, provenance-commented from B1/B2, no round-1 reuse; B2's auxiliary-LF head removed, no aux arm on this card) + probe `probes/teacher_projection_ledger.py`; mandatory contract smoke exit 0 (`ext__helmholtz_2d`, nRMSE 2.0065/skill 6.7100, 2-epoch plumbing number); all 36 legs ran (1 primary T0 + 5 outer folds × [T0_k, I1_k, 4 inner teachers, proj_nn_k]); ledger identity verified exactly (`advantage_reachable + advantage_unreachable - advantage_total = 0.0`); checkpoint-resume certified beyond the contract minimum (full 36/36-leg replay bit-identical in 46s, plus a partial-deletion re-derive test also bit-identical); the `heat_local` debug leg that was still running at this run's earlier checks (PID 235830) evidently completed and fed into this build. `review_notes: []`, `job_ids: []` — code-reviewer presumably dispatched next (mirroring r2s3-B3's pattern), but `state/r2s4_diag/current_stage.txt` and `orchestrator_flow.md` are NOT yet updated to reflect this completion (same write-ordering lag seen repeatedly this round) | **0 live SLURM** (all prior seeds terminal, unchanged; B3 not yet submitted); 0 live local processes for this stream at this final check (builder process has exited) | `drafted` -> `built` (builder SUCCESS, build `fb00237f`); code-reviewer presumably dispatched next (stage file not yet updated) |

**Anchor note**: r2s4_diag remains the only stream with a *certified* anchor
(`certified_3seed_panel_geomean`, 19.8178, replacing the training-free floor)
— r2s1_direct, r2s2_stacked, r2s3_lf_train_signal remain on the launch-time
`best_floor_panel_geomean` anchor (23.0636, `certified_utc` 2026-07-31T14:20:17Z,
unchanged). No anchor deltas this run. All anchors rendered verbatim from
`state/anchors/*.json`.

**This run's headline**: **2 card-status deltas** — `r2s3_lf_train_signal-B3`
`drafted` -> `built` (builder SUCCESS 10/10, build `dfcd46c`, code-reviewer
dispatched) and `r2s4_diag-B3` `drafted` -> `built` (builder SUCCESS, build
`fb00237f`, caught during this run's final pre-return re-verification — landed
~29s after the initial RUN END timestamp). No card reached
`complete`/`analyzing` transitions this run (all 10 cards' `status` otherwise
unchanged from the prior check). Sub-card progress: `r2s1_direct-B3`'s
websearcher **completed** (report.md + iteration_5 landed after the prior
run's close, cap hit 7/7) and its brainstormer was dispatched (not yet
producing output); `r2s2_stacked-B2`'s turn-3 mechanism script wrote its 3rd
of 4 dataset legs and started the 4th (last). SLURM state (0 live, 14 total
COMPLETED, byte-identical across three cross-checks this run), timing
ledger, anchors, gates, and noise floor are all unchanged. A mid-run
auto-sync commit (`8cae345`, 2026-08-01T01:14:18Z) landed inside this run's
window, capturing the r2s3-B3 build + websearcher/tool outputs — noted for
repo-hygiene accounting, not itself a maintainer write.

## Running / pending jobs

| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| (none — 0 live SLURM `r2-*` jobs) | — | — | — | — |

**0 live `r2-*` SLURM jobs** at this check (squeue + sacct cross-checked
three times across this run, no transient-empty false positives — `sacct`
shows all 14 `r2-*` jobs COMPLETED, byte-identical throughout; `squeue` shows
0 `r2-*` entries, only unrelated interactive `bash` jobs and round-1 `r1-*`
PENDING seed-confirm jobs, out of this maintainer's scope). **0 live local
(non-SLURM) processes** at this final check (down from 2 mid-run — the
`r2s2_stacked-B2` turn-3 script and the `r2s4_diag-B3` builder's last debug
leg have both since completed/exited; the r2s3-B3 builder process had
already exited earlier this run).

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

`r2s2_stacked-B2` (`analyzing`, `reanalysis_progress: turn_2`, turn-3 script
on its last dataset leg), `r2s3_lf_train_signal-B3` (`built`, code-reviewer
dispatched, no SLURM job yet) and `r2s4_diag-B3` (`built`, code-reviewer
presumably next, no SLURM job yet) are all actively open but none has part 7
written (or, for B3 cards, a review/job/complete state yet) — not listed
here until each card itself closes.

## Flags

- **`r2s3_lf_train_signal-B3` builder SUCCESS this run**: `drafted` ->
  `built`, build `dfcd46c`, contract smokes exit 0 (incl. an A0-arm
  checkpoint-resume test on `ifc_poisson` reproducing bit-identically),
  deleted-surface negative tests correctly RAISE on all 4 removed
  null-penalty env keys, 26/26 env keys + 33/33 legs verified. Code-reviewer
  now dispatched next (`review_notes: []` still, not yet landed).
- **`r2s4_diag-B3` builder SUCCESS this run** (caught during final
  pre-return re-verification, ~29s after the initial RUN END): `drafted` ->
  `built`, build `fb00237f`, new from-scratch family
  `models_r2/r2s4_b3_projection/`, contract smoke exit 0, all 36 legs ran,
  ledger identity exact, checkpoint-resume certified beyond the mandatory
  minimum (full replay + partial-deletion re-derive both bit-identical).
  `state/r2s4_diag/current_stage.txt` and `orchestrator_flow.md` NOT yet
  updated to reflect this — worth watching next cycle for the code-review
  dispatch to land visibly.
- **`r2s1_direct-B3` websearcher SUCCESS this run**: cap hit 7/7, pdf-rule
  honored. Best-supported composition (C2): the blend stage is a
  Bates-Granger (1969) minimum-variance combination; the round's own
  "evaluation-artifact" reading of the blend's payoff (from B2 part 7)
  remains unpublished in this genre. Brainstormer now dispatched with a
  B3-or-close + instrument-repair-card option explicitly framed; no
  brainstormer output yet.
- **`r2s2_stacked-B2` write-ordering lag — persists, now spanning 4
  consecutive checks**: `6_analysis` is still `null` on-card even though
  `reanalysis_progress` has read `turn_2` since three checks ago and the
  turn-3 mechanism script (now on its 4th/last dataset leg) continues
  writing per-dataset outputs steadily (3/4 legs confirmed written this
  run). Confirmed not stalled through this run's checks. Flagged for
  continued watching — turn 3 should close out and land on-card soon.
- **Real lead flagged inside `r2s2_stacked-B2` turn 2** (not yet a card
  claim): a training-free interior-k LF average reportedly beats the trained
  corrector on `allen_cahn`/`cahn_hilliard` — worth tracking into part 6/7
  once it lands on-card.
- **NEW round-level pattern carried forward from last run**: a
  **post-hoc-blend-stage instrument-error class** flagged by
  `r2s1_direct-B2` part 7, now potentially reinforced by this run's
  `r2s1_direct-B3` websearch finding (C2: blend = textbook Bates-Granger
  minimum-variance combination) — alongside `r2s2_stacked-B2`'s statistic
  mis-specification and estimator-bias/endpoint-artifact findings, this is
  the round's recurring instrument-defect class across 2 independent
  streams; still not yet a round-report action.
- **Timing ledger**: **no upsert this run** — no new terminal `r2-*` SLURM
  states (all 14 jobs in `sacct` were already COMPLETED and ledgered; both
  `r2s3_lf_train_signal-B3` and `r2s4_diag-B3` are now `built` but neither
  has submitted anything to SLURM yet — both awaiting code review first).
  Still **14 entries** total, JSON re-validated as parseable.
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
  visible in `squeue` as `r1-*`, PENDING) — separate round, separate report.
- No reopen candidates on any of the 10 cards. No `blocked.md` file exists
  (no stream has ever blocked). No abandoned streams — none are possible yet
  (r2s1/r2s3/r2s4 at batch 3 with clean prior closes; r2s2 at batch 2 with a
  clean B1 close — no skip/block history anywhere). `state/streams/`
  directory still does not exist — consistent with no abandonments ever
  being needed.
- Repo hygiene: `git status --short .` (round root, excluding `worktrees/`),
  final check after a mid-run auto-sync commit (`8cae345`,
  2026-08-01T01:14:18Z) landed: only 1 remaining modified card file —
  `experiment_cards/r2s4_diag/batch_3/B3.json` (the `drafted`->`built` delta
  caught in this run's final re-verification, itemized above; postdates the
  auto-sync commit so was not captured by it) — plus the still-empty,
  untracked `brainstormer/r2s1_direct/batch_3/` (other-agent-owned,
  mid-flight). This maintainer's own writes this run: `index.md`,
  `state/maintainer_report.md` (`state/timing_ledger.json` content
  unchanged, gitignored, not part of the git-status comparison). No Write
  call this run touched `experiment_cards/`.
