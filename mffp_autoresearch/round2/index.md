# MFFP Autoresearch Round 2 — Dashboard (updated 2026-07-31T23:36:01Z)

## Streams

| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r2s1_direct | 23.0636 (best_floor_panel_geomean) | **2** | r2s1_direct-B1 **complete**; r2s1_direct-B2 **running** (job just completed — analysis pending) | **B1: unchanged, still COMPLETE.** **B2: no card `status` field delta yet** (still `running`) — **but seed 0 job `66189580` completed mid-checklist**: RUNNING→COMPLETED, 00:16:50 elapsed, exit 0:0, well under its 3:00:00 budget (raised 2h→3h per the code-reviewer). Caught only during this maintainer's pre-return re-verification pass (it was still ~16 min into RUNNING at the run's initial squeue/sacct check). Family `r2s1_selected_form`, scored arm `selected_form_wiener_blend`. `status` field has not yet caught up to `analyzing`/initial-analyzer-dispatch — flagged for the next check | **0 live** (`66189580` terminal COMPLETED this run) | Job `66189580` RUNNING→COMPLETED (caught mid-checklist); timing ledger upserted |
| r2s2_stacked | 23.0636 (best_floor_panel_geomean) | **2** | r2s2_stacked-B1 **complete**; r2s2_stacked-B2 **analyzing** (two deltas landed this run) | **B1: unchanged, still COMPLETE.** **B2: two deltas this run.** (1) `status` field caught up — `running`→`analyzing`, reflecting an initial-analyzer result that had landed before this run's window: panel geomean **19.3868** (band met); FALSIFIED 3/4 clauses **but** all F1-firing cells are `B:all` LOO-artifact cells (train side = exact scaled copy of own real LF; test side = train_mean — excluding them F1 fires on 0 cells, only F3 survives on 2); F2 **INVERTED** (k=1 beats k=all); k* selection unstable 3/6 (helmholtz flips B:1↔B:4, contained by blend). (2) **`reanalysis_progress` landed `turn_1`** — the mechanism-analyzer's "artifact-vs-substance" turn, one of the three agents killed by the weekly-API-limit incident (see Flags), re-dispatched with partial-file-distrust instructions, now landed (`6_analysis` content still `null` — write-ordering lag, findings not yet readable from the card) | 0 live SLURM (both legs terminal, unchanged); mechanism-analyzer turn 1 landed (file-level, no OS process visible) | `status` `running`→`analyzing`; `reanalysis_progress` `null`→`turn_1` (mechanism turn 1 landed post usage-limit re-dispatch, content pending) |
| r2s3_lf_train_signal | 23.0636 (best_floor_panel_geomean) | **2** | r2s3_lf_train_signal-B1 **complete**; r2s3_lf_train_signal-B2 **analyzing** | **B1: unchanged, still COMPLETE.** **B2: no `status` field delta this run** (still `analyzing`), but `reanalysis_progress` advanced **`turn_1`→`turn_2`** (mechanism-analyzer turn 2, 7/7, re-landed after being killed early by the weekly-API-limit incident and re-dispatched): fisher m=0 gain = conditional-mean **variance reduction** (a level-swap reproduces 76.8%; LF adds no condition info; alignment unchanged — r2s4's "barrier" claim NOT overturned, LF affine 1.0133x the barrier); F5 sharp limb is a **task property** (all condition-response arms lose to constant, useful share negative); H8: penalty over-amplitude is monotone in rung coarseness, `in_rung_loo` picked the worst option on a 1e-8 tie (cost 0.64 = 0.68x floor, not individually claimable). **Write-ordering caveat persists**: `6_analysis` is still `null` in the card. Turn 3 dispatched (H9 cahn_hilliard channel decomposition + part 6) — not yet landed | 0 live SLURM (seed 0 terminal, unchanged); 0 live local processes for this stream at this check | `reanalysis_progress` `turn_1`→`turn_2` (mechanism-analyzer turn 2 landed after usage-limit kill+redispatch; findings content still pending) |
| r2s4_diag | **19.8178** (certified_3seed_panel_geomean, CI95 [19.385, 20.527]) | **3** | r2s4_diag-B1 **complete**; r2s4_diag-B2 **complete** | **B1/B2: unchanged, both still COMPLETE.** **B3 progress this run**: the B3 websearcher — one of the three agents killed early by the weekly-API-limit incident — was re-dispatched with partial-file-distrust instructions; its prior partial output is preserved under `websearches/r2s4_diag/batch_3/_untrusted_prior_attempt/`, and the fresh attempt has now produced **5 iteration files + `summary_so_far.md`** (empty at last check). Stream still at batch 3, `current_stage.txt` unchanged ("websearch (B3 dispatched 2026-08-01; B2 complete)") | 0 live SLURM (all seeds terminal, unchanged); websearcher actively producing output (not a local OS process visible via `ps aux`, tracked via file landings) | B3 websearcher: 0→5 iteration files + summary produced this run (post usage-limit re-dispatch) |

**Anchor note**: r2s4_diag remains the only stream with a *certified* anchor
(`certified_3seed_panel_geomean`, 19.8178, replacing the training-free floor)
— r2s1_direct, r2s2_stacked, r2s3_lf_train_signal remain on the launch-time
`best_floor_panel_geomean` anchor (23.0636, `certified_utc` 2026-07-31T14:20:17Z,
unchanged). No anchor deltas this run. All anchors rendered verbatim from
`state/anchors/*.json`.

**This run's headline**: a **weekly-API-limit incident** hit three agents
early (r2s2-B2 mechanism turn 1, r2s3-B2 mechanism turn 2, r2s4-B3
websearcher) before this run's window opened; the operator re-logged in and
all three were re-dispatched with partial-file-distrust instructions (their
partial output preserved, not trusted). **All three have now re-landed**
during this run's window: `r2s2-B2` mechanism turn 1 (content pending),
`r2s3-B2` mechanism turn 2 (7/7, content pending), `r2s4-B3` websearcher (5
iterations + summary). Separately, `r2s2_stacked-B2`'s card `status` field
caught up (`running`→`analyzing`) to an already-landed initial-analyzer
result (geomean 19.3868, F1 traced to a `B:all` LOO-artifact, F2 inverted).
**A SLURM job completion was also caught mid-checklist**: `r2s1_direct-B2`
seed 0 (`66189580`) transitioned RUNNING→COMPLETED (16:50 elapsed, well
under its 3h budget) — this happened after this run's initial squeue/sacct
pass and was only discovered during the maintainer's pre-return
re-verification; **all four B2 cards' SLURM-level compute has now completed
at least once, across every stream**. Timing ledger **upserted with 1 new
entry** this run (`66189580`) — now **14 entries** total.

## Running / pending jobs

| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| (none) | — | — | — | — |

**0 live `r2-*` SLURM jobs** at this check (squeue + sacct cross-checked, no
transient-empty false positives) — the 1 job live at the start of this run
(`66189580`) transitioned RUNNING→COMPLETED within this run's window,
confirmed terminal in `sacct` (exit 0:0, 00:16:50 elapsed), not just absent
from `squeue`. No local (non-SLURM) agent processes for this round were
directly visible via `ps aux` at this check (the mechanism-analyzer and
websearcher work landing this run are tracked via file timestamps /
`orchestrator_flow.md`, consistent with running inside the orchestrator's
own agent context rather than as separate visible shells). Unrelated
interactive `bash` jobs and round-1 `r1-*` jobs also visible in the queue —
out of this maintainer's scope, not itemized here.

## Completed cards

| Card | Type | Panel geomean skill (±CI) | Falsification verdict | Tools promoted |
|---|---|---|---|---|
| r2s4_diag-B1 | diagnostic | 19.8178 IQM, CI95 [19.385, 20.527] (3 seeds) | n/a (diagnostic — no falsification clauses); mechanism register complete, part 7 written | 2 tools, both correctly indexed: `tools/conditional_mean_collapse.py`, `tools/condition_predictability_ceiling.py` |
| r2s4_diag-B2 | diagnostic | 19.8829 own single-run 3-seed geomean (T0 primary arm; reproduces B1's certified band, not a re-certification) | **falsified**: the aux-LF-TARGET head is worth nothing at any N_fit in 20-320 on 15/15 dataset×N cells (7.42-101.12x the certified floor's resolving power); explicitly does NOT license the broader "LF doesn't help" claim (input-side + disjoint-supply channels untouched) | **3 tools**: `tools/ladder_pair_alignment_audit.py`, `tools/shrinkage_curve_anatomy.py`, `tools/condition_predictability_ceiling_fast.py` |
| r2s1_direct-B1 | model | 19.6444 (single seed 0, no CI yet) | **falsified in a split reading**: floors clause CONFIRMED (beats best floor on all 6 panel datasets, geomean −14.8% vs anchor) but the implicit architecture clause FALSIFIED — a ~156-parameter closed-form head reaches 19.0553/19.1666, statistically indistinguishable from the 15.9M-parameter shipped arm (0.52x the certified panel min_claimable_effect) | 2 tools, both correctly indexed: `tools/band_gain_counterfactual.py`, `tools/condition_identifiable_rank.py` |
| r2s3_lf_train_signal-B1 | model | 25.3919 (`rung_native`, single seed 0) | **falsified in a split reading**: F1 (primary, architecture) FALSIFIED with a 7.35-skill-unit sign inversion on `ifc_poisson`, traced to a shared-scaler confound; but the motivating INFORMATION claim is CONFIRMED — an architecture-free estimator recovers +3.2317 skill units from the same 170 disjoint LF rows (18.83% of the law's coefficient energy at cos 0.9993). F2 (native vs upsampled) survived; F3 (degeneracy) verdict depends on provisional vs re-certified floor thresholds (both recorded) | 2 tools, both correctly indexed: `tools/affine_ladder_voi.py`, `tools/posthoc_repair_ladder.py` |
| r2s2_stacked-B1 | model | 14.0756 (single seed 0, no CI yet; scored arm `frozen`; ~all margin from the unpaired `ifc_poisson` column) | clean negative with a measured mechanism, not a raw binary: the falsification clause was a conjunction that did **not** fire — conjunct 1 ("improve on `emul_only` by ≥2.0 skill units") **held** (measured improvement 0.0061, 326x below threshold) but conjunct 2 ("beat the NN-in-condition floor") **failed to hold** (beat it by 11.90 skill units, 130x the noise floor). Round-level headline (I8): a stacked intermediate representation is a re-parameterisation of the condition→HF hypothesis class, not a new information channel | 2 tools, both correctly indexed and register-confirmed: `tools/reachable_set_rank_audit.py`, `tools/surrogate_coherence_eligibility.py` |

r2s2_stacked-B2 (`analyzing`, initial-analysis landed — geomean 19.3868, F1's
LOO-artifact question is the live decision, F2 inverted — mechanism turn 1
just landed post usage-limit re-dispatch, `6_analysis` content still
pending) and r2s3_lf_train_signal-B2 (`analyzing`, part 5 `confirmed`/
`proceed_to_seeds_1_2` on a partial 3-of-6-dataset panel; mechanism turn 2
just re-landed, `6_analysis` content still pending) are both actively
closing but part 7 has not been written on either — not listed here until
the card itself closes. r2s1_direct-B2 (`running` in the card field, though
its SLURM job just completed — analysis not yet dispatched per the card)
is not listed here either.

## Flags

- **Weekly-API-limit incident, RESOLVED this run**: three agents were killed
  early by the weekly API limit before this run's window opened — `r2s2-B2`
  mechanism turn 1, `r2s3-B2` mechanism turn 2, `r2s4-B3` websearcher. The
  operator re-logged in and all three were re-dispatched with
  **partial-file-distrust instructions** (their partial output preserved but
  not trusted as authoritative — visible under
  `websearches/r2s4_diag/batch_3/_untrusted_prior_attempt/`). SLURM jobs
  were unaffected (confirmed — no `r2-*` job showed any anomaly in `sacct`
  spanning the incident window). **All three re-dispatches landed within
  this run's window**: `r2s3-B2` mechanism turn 2 re-landed cleanly (7/7);
  `r2s4-B3` websearcher produced 5 iterations + a summary; `r2s2-B2`
  mechanism turn 1 landed (`reanalysis_progress`→`turn_1`, though
  `6_analysis` content is still pending — the same benign write-ordering lag
  seen elsewhere this round, not a sign of a further problem). No card
  content was corrupted by the incident — the partial-file-distrust protocol
  appears to have worked as intended.
- **Mid-checklist discovery**: `r2s1_direct-B2`'s seed-0 SLURM job
  (`66189580`) transitioned RUNNING→COMPLETED (16:50 elapsed, exit 0:0)
  *after* this run's initial squeue/sacct pass — caught only during the
  maintainer's mandatory pre-return checklist re-verification. Timing ledger
  upserted (14 entries now). Card `status` field has not yet caught up
  (still `running`, no analyzer dispatched per the card) — flagged for the
  next maintainer check. This is the last of the four B2 cards' SLURM-level
  compute to complete — **all four B2 SLURM runs have now finished at least
  once, across every stream**.
- **Two card `status`-field deltas this run**: `r2s2_stacked-B2`
  `running`→`analyzing` (catching up to the already-landed initial-analyzer
  result). Two `reanalysis_progress` deltas without a `status`-field change:
  `r2s2_stacked-B2` `null`→`turn_1` and `r2s3_lf_train_signal-B2`
  `turn_1`→`turn_2` (both mechanism-analyzer turns, both re-landed post
  usage-limit kill+redispatch; both cards' `6_analysis` content still
  pending — write-ordering lag). All other cards' `status` byte-identical to
  last run: `r2s1_direct-B1`/`r2s2_stacked-B1`/`r2s3_lf_train_signal-B1`/
  `r2s4_diag-B1`/`r2s4_diag-B2` `complete`; `r2s1_direct-B2` `running`
  (despite its job now being terminal — analyzer not yet dispatched per the
  card). `reopen_candidate` is `false` on all 8 cards. No `debug_notes` on
  any card — no failures needing a debugger this run (the usage-limit
  incident is an infrastructure/operator event, correctly not recorded as a
  card-level `debug_notes` entry on any card).
- **r2s2_stacked-B2 initial-analysis detail**: panel geomean **19.3868**
  (band met vs the launch anchor 23.0636). FALSIFIED 3/4 clauses — **but**
  every F1-firing cell is a `B:all` LOO-artifact cell (train side is an
  exact scaled copy of own real LF; test side is `train_mean`); excluding
  those artifact cells, F1 fires on 0 cells and only F3 survives on 2. F2 is
  **INVERTED** (k=1 beats k=all — an empirical posterior sample beats the
  conditional mean). k* selection is **unstable on 3/6 datasets**
  (`ext__helmholtz_2d` flips B:1↔B:4 depending on fold seed), contained by
  the blend step. The live open question for the just-landed mechanism
  turn 1 is explicitly "artifact vs substance" for the F1 signal — findings
  content not yet readable from the card (`6_analysis` still `null`).
- **r2s3_lf_train_signal-B2 mechanism-analyzer turn 2 detail**: fisher_kpp's
  m=0 gain is explained as conditional-mean **variance reduction**, not new
  condition information (a level-swap experiment reproduces 76.8% of the
  effect; LF adds no condition info; alignment is unchanged) — this does
  **not** overturn r2s4's "barrier" claim (LF affine transform is only
  1.0133x the barrier). F5's sharp-limb falsification is confirmed as a
  **task property**, not an architecture failure (every condition-response
  arm loses to a constant predictor there, useful share negative). H8: the
  null-penalty's over-amplitude is monotone in rung coarseness;
  `in_rung_loo` selected the worst option on a numerically-tied (1e-8) case
  but the resulting cost (0.64) is 0.68x the noise floor — not individually
  claimable. Turn 3 (H9: cahn_hilliard channel decomposition + part 6)
  dispatched, not yet landed.
- **r2s4_diag-B2 register-turn/part-7 detail (carried forward, unchanged)**:
  last untouched value-of-LF channel = INPUT-SIDE privileged information (an
  LF-consuming teacher at train time whose advantage has to be distilled
  into a condition-only student). Recommended B3 (Option A): fit an
  out-of-fold condition→prediction projection of the LF-teacher arm's own
  test predictions, score the projection against the condition-only baseline
  T0 on the same folds. Pre-registered prediction: 4/5 datasets converge (LF
  collinear with HF, cos ≥ 0.997), `ext__helmholtz_2d` report-only.
  "Support-not-identifiability" remains a round-rule CANDIDATE, not yet
  certified (pending a 2nd confirming card). A benchmark-integrity item
  (ifc_raw eval assumption failed 4 independent places across this round)
  remains flagged for Eloise, outside this maintainer's remit to act on.
- **Timing ledger**: **1 new entry this run** — job `66189580`
  (r2s1_direct, batch 2, seed 0, family `r2s1_selected_form`, panel leg,
  16.83 min, COMPLETED, well under its 3:00:00 budget; completion caught
  mid-checklist, after the run's initial squeue/sacct pass). Now **14
  entries** total, JSON re-validated as parseable (`json.load` succeeded).
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
- **r2s3_lf_train_signal-B2 code-review verdict detail (carried forward)**:
  `reviewed_suggest`, 8/8 PASS (5 nits, none blocking); most notably: quote
  `gate_report.linear_mf_ladder.per_rung['32']` (0.2427) not
  `splits.ref_linear_mf` (1.354, a numerical-tie artifact); F2
  (`A5_lf_norepair` vs `A2`) is an instrument contrast, not
  capacity-matched (alpha 12 vs 4); `_ORACLE`-suffixed keys are
  test-condition-fitted and must never be quoted as arm scores; a TIMEOUT
  on the 3h/17-leg job is a resubmit, not an ALGO failure. Should inform the
  card's eventual part 6/7 writeup.
- **Timestamp-ahead-of-clock / clock-skew anomaly class (carried forward, no
  new distinct occurrence flagged this run)**: prior runs flagged
  `review_notes[0].utc` fields reading ahead of the actual check time, and an
  informal "2026-08-01 ~0x:xx PDT" wall-clock labelling convention in
  `orchestrator_flow.md` for events that `sacct`'s cluster-local clock
  places on 2026-07-31. This run's fresh entries continue the same benign
  pattern — not a new distinct class, no scored quantity affected.
- **Gates**: G1-r2 PASS, G2-r2 PASS, G3-r2 PASS (all 2026-07-31,
  `state/gates.md`) — round cleared for stream launch. Unchanged this run.
- **Round-1 top-3 seed confirms**: NOT this maintainer's scope (round-1 jobs
  visible in `squeue` as `r1-*`, PENDING) — separate round, separate report.
- No reopen candidates on any of the 8 cards. No `blocked.md` file exists (no
  stream has ever blocked). No abandoned streams — none are possible yet
  (r2s1/r2s2/r2s3 at batch 2 with clean B1 closes; r2s4 now at batch 3 with
  two clean closes B1/B2 — no skip/block history anywhere).
  `state/streams/` directory still does not exist — consistent with no
  abandonments ever being needed.
- Repo hygiene: `git status --short .` (round root, excluding `worktrees/`)
  shows 3 card-file deltas this run — `experiment_cards/r2s1_direct/batch_2/B2.json`
  (present in the diff against the pre-this-session baseline but
  content-unchanged since the last report — the addendum captured last run;
  its SLURM job completion has NOT yet propagated into a card field change),
  `experiment_cards/r2s2_stacked/batch_2/B2.json` (`running`→`analyzing`,
  `reanalysis_progress` `null`→`turn_1`), and
  `experiment_cards/r2s3_lf_train_signal/batch_2/B2.json`
  (`reanalysis_progress` `turn_1`→`turn_2`) — all other-subagent writes,
  none touched by this maintainer. Also modified/untracked (other-agent/
  orchestrator-owned, outside this maintainer's scope):
  `state/orchestrator_flow.md`, `state/r2s1_direct/current_stage.txt`,
  `state/r2s2_stacked/current_stage.txt`,
  `websearches/r2s4_diag/batch_3/iteration_1.md` (modified) plus
  `iteration_2.md`/`iteration_3.md`/`iteration_4.md`/`iteration_5.md`/
  `summary_so_far.md`/`_untrusted_prior_attempt/` (new, untracked). This
  maintainer's own writes this run: `index.md`, `state/maintainer_report.md`,
  `state/timing_ledger.json` (1 new entry, gitignored, not part of the
  git-status comparison). No Write call this run touched `experiment_cards/`.
