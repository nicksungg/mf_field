# MFFP Autoresearch Round 2 — Dashboard (updated 2026-08-01T20:54:00Z)

**Thirteenth maintainer walk since the operator halt/resume cycle.**
Halt landed 2026-08-01T01:31:54Z (commit `10d4e4c`), resume landed
2026-08-01 ~08:1x PDT (commit `b80e622`).

**Headline — unchanged since walk 12 (no card-level deltas this run).**
`r2s3_lf_train_signal-B4` (initial-analyzer, diagnostic, seed 0 only)
landed part 5 at walk 12 and moved `status: running` → `analyzing`.
Verdict: **F1∨F2∨F3∨F4 all FALSE → CARD CONFIRMED.**
The achievable-effect gate keeps `{ifc_poisson, sharp__cahn_hilliard,
sharp__allen_cahn_2d}` (membership changed vs B3's `{ifc, ch, fk}` —
`sharp__fisher_kpp_2d` retires: its raw effect 1.3132 is more than fully
absorbed by `ref_train_mean_n5`, 223/441/181% absorbed across the three
draws). The ceiling gate narrows further to `{sharp__cahn_hilliard}`
only. The pre-registered B5 trigger (any dataset's ridge-conditional-LOO
ceiling absorbing ≥50%) does **not** fire (max 26.9% on `ch`) — per
`iteration_1.md`'s locked rule, **the stream closes on B4** once the
mechanism-analyzer (turn 1 still in progress this run — a live
background process (`reanalysis_turn_1.py --repeats 40`, PID 2270940,
~17 min elapsed at this walk's check, within its own 1200s-per-attempt
budget) has not yet written `scratchpad/turn1/turn1_calibration_signal.json`;
the smoke-probe file `scratchpad/turn1_smoke/turn1_calibration_signal.json`
landed before walk 12 closed and is unchanged) and register turn land;
part 7 makes the formal close call, not part 5. The initial-analyzer's
handoff also flags that the effect is priced almost entirely by the
LF-free reference floors themselves, not by any calibration head — all
four "achievable" heads are numerically the identity — which reframes
B3's part-7 "output-calibration trick" hypothesis. Job 66268786 (98s,
`expansion` partition, CPU-only) remains COMPLETED (upserted to the
ledger at walk 12; unchanged this run).

`r2s4_diag-B4` remains `status: reviewed_fail` at the card level; the
reviewer-mandated fix cycle finished in the worktree at walk 12 and is
**still uncommitted this run** (tip still `dc0d7ae`, no new commit
landed, `git diff` unchanged since walk 12): (1) the
`_repo_root()` resolver now iterates `WORKTREE_ROOT.parents` only, not
`[WORKTREE_ROOT] + .parents`; (2) `scripts/01_train_eval.sh`'s anatomy
call is now fatal (`exit 1` + explicit `[FAIL]` if `diagnostic.json` is
missing/empty) instead of masked by `|| echo [warn] ...`; (3) a fresh
**no-override** contract-tier re-verify (`scratchpad/reverify.log`,
`reverify_contract.json`, `reverify_diag/`) ran the full 201-leg matrix
and this time correctly wrote `diagnostic.json` (63.7 KB) to the real
`${OUTPUTS_ROOT}/round2/r2s4_diag/B4/eval/` — confirmed on disk at this
walk. The fix also folds in two reviewer SUGGEST items beyond the
required three: a noise-floor-JSON cross-check assertion on the
pre-registered equivalence bound, and an eval-layer/in-family metric-seam
assert. No agent process is currently active on this card (`ps aux`
clean at this walk's check too) — it remains at the natural handoff
point (commit + re-review) flagged at walk 12; the orchestrator has
queued a commit nudge to the builder and will take over the mechanical
commit itself if nothing lands by its next pulse.

Three previously-tracked GPU jobs remain **PENDING**, unchanged since
walk 11: 66262741 (`r2s1_direct-B3`, seed 0), 66267438 / 66267441
(`r2s2_stacked-B3` panel / guard) — all Priority-queued,
`Elapsed=00:00:00`, verified by both `squeue` and `sacct` at this run's
check. No new auto-sync since walk 12 — tip still `f3ce653`.

## Streams

| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r2s1_direct | 23.0636 (best_floor_panel_geomean) | 3 | r2s1_direct-B1 **complete**; r2s1_direct-B2 **complete**; r2s1_direct-B3 **running** | Unchanged this run. Seed-0 job **66262741 still PENDING** in `squeue`/`sacct` (Priority-queued, `Elapsed=00:00:00`) | **1 live/pending SLURM** (`r2-r2s1_direct-B3-s0`, job 66262741, PENDING) | No change; job still PENDING |
| r2s2_stacked | 23.0636 (best_floor_panel_geomean) | 3 | r2s2_stacked-B1 **complete**; r2s2_stacked-B2 **complete**; r2s2_stacked-B3 **running** | Unchanged this run — still `running`, job_ids `['66267438','66267441']`. Both jobs remain PENDING; job-name-collision watch item still applies once the guard leg starts running | **2 live/pending SLURM** (`r2-r2s2_stacked-B3-s0` 66267438, `r2-r2s2_stacked-B3-guard-s0` 66267441, both PENDING) | No change; both jobs still PENDING |
| r2s3_lf_train_signal | 23.0636 (best_floor_panel_geomean) | 4 | r2s3_lf_train_signal-B1..B3 **complete**; r2s3_lf_train_signal-B4 **analyzing — CONFIRMED (round's first confirmed card)** | Unchanged this run — `status: analyzing` (part 5 landed walk 12). Achievable gate `{ifc, ch, ac}`, ceiling gate `{ch}` only, fk retires. B5 trigger NOT fired → **stream closes on B4** after mechanism+register. Mechanism-analyzer turn 1 still in progress (live process ~17 min elapsed at check, no `turn1/` output yet) | **0 live SLURM** (job 66268786 COMPLETED prior to walk 12; ledger unchanged at 17 entries) | No card-level change this run; mechanism turn 1 in progress |
| r2s4_diag | **19.8178** (certified_3seed_panel_geomean, CI95 [19.385, 20.527]) | 4 | r2s4_diag-B1..B3 **complete**; r2s4_diag-B4 **reviewed_fail (fix cycle finished at walk 12, still uncommitted)** | `status` unchanged at `reviewed_fail`; worktree unchanged since walk 12 (tip still `dc0d7ae`, `git diff` identical, all 3 reviewer-mandated fixes still present but not committed). Orchestrator has queued a commit nudge to the builder and will take over the mechanical commit if nothing lands by its next pulse | **0 live SLURM** (card blocked pending commit + re-review; no re-submission yet) | No change this run; commit still pending — watch next walk |

**Anchor note**: r2s4_diag remains the only stream with a *certified* anchor
(`certified_3seed_panel_geomean`, 19.8178) — r2s1_direct, r2s2_stacked,
r2s3_lf_train_signal remain on the launch-time `best_floor_panel_geomean`
anchor (23.0636, `certified_utc` 2026-07-31T14:20:17Z, unchanged). No anchor
deltas this run — all 4 `state/anchors/*.json` files' mtimes predate this
run's entire window. All anchors rendered verbatim from
`state/anchors/*.json`.

## Running / pending jobs

| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| 66262741 | r2s1_direct-B3 (seed 0) | PENDING | 0:00 | (Priority) |
| 66267438 | r2s2_stacked-B3 (seed 0, panel) | PENDING | 0:00 | (Priority) |
| 66267441 | r2s2_stacked-B3 (seed 0, guard) | PENDING | 0:00 | (Priority) |

**3 live/pending `r2-*` SLURM jobs**, unchanged from the prior close — all
still PENDING at this run's check, confirmed by both `squeue` and
`sacct`. `sacct`'s 2-day window otherwise shows the same 17 pre-existing
`r2-*` jobs, all COMPLETED 0:0, identical to the prior ledger set (no new
completions this run).

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
| r2s2_stacked-B2 | diagnostic | 19.386837 (single seed 0, `provisional-single-seed`); vs anchor 23.0636 (-3.677, beyond certified mce 1.1419 but not anchor-certifying) | **falsified**: F1 fires (refit LSI corrector beats the promoted rule's training-free ceiling on 3 ladder cells), F2 fires (k=1 beats k=all beyond mce on 3 panel datasets), F3 fires (ladder-B partial coherence clears permutation-null on 5/6 datasets), F4 does not fire. `cratered_verdict: n/a` (diagnostic — no crater rule) | **2 tools**, both correctly indexed, no duplicates: `tools/zero_gradient_stage_ladder.py`, `tools/relative_gain_units_audit.py` — together they **retract the B1-promoted `surrogate_coherence_eligibility.py` rule as an eligibility GATE** (centring bug + frozen-vs-refit mismatch + 10-817x unit mispricing), demoting it to a directional-only predictor |
| r2s3_lf_train_signal-B3 | model | 17.114970 (`A1_lf_cov` primary arm, single seed 0) vs anchor 23.0636 (comparison arm `A0_nolf` 32.4663) | **falsified** (F1/F2 knife-edge adjudicated FALSIFIED, robust across 5/7 defensible threshold readings incl. a gain-calibrated split reading M4; only the two readings pricing zero HF-subset-draw variance return CONFIRMED); the round's success-criterion-1 (≥3-dataset claimable with/without-LF-training contrast) is still met on exactly 3 datasets under the operative threshold. `cratered_verdict: cratered` (third limb only — falsification fired decisively; not a crash, not >1.5x anchor) | **2 tools**, both correctly indexed: `tools/effect_threshold_readings.py` (7-reading threshold-adjudication tool; surfaces `mce_over_observed_split_range` as a provenance smell), `tools/map_dispersion_scale_shape.py` (splits inter-prediction dispersion into total vs shape-only; found allen_cahn's 3 LF-trained models sit within 0.41 skill units of each other but 100.5 units apart in function space — "scale, not map") |
| r2s4_diag-B3 | diagnostic | 19.172826 (single seed 0, no own-card CI — 1 seed; in-job 5-fold paired spreads are per-dataset thresholds, not a panel CI) | **falsified** (F3 stands and is hardened by two row-count/capacity controls; F4a fired on the ledger's own contaminated-quantity definition, not on a measurement failure — 0/4 under the corrected teacher-target term; F1 survives on 2 of its 3 needed cells, pfc's cell ruled uninformative by a ceiling argument). Mechanism headline: on 3 of 4 sharp datasets the condition-only arm's per-band error is ~1.00 above the lowest band — it contributes exactly zero energy above the spatial mean — while the LF field reproduces HF to 1e-2 to 1e-16 band relative error, i.e. essentially all panel structure is realisation information carried only by LF. `cratered_verdict: n/a` (diagnostic) | **2 tools**, both correctly indexed: `tools/ledger_contamination_audit.py` (prices whether a paired-arm delta *could* have fired via a triangle-inequality ceiling, and whether it's contaminated by a function-class term vs the true target term), `tools/band_retention_probe.py` (per-band retained-energy/relative-error decomposition; on its first foreign-data run it independently found the `stage_blend_decoder` zero-field arm in r2s1_direct-B3's shipped dumps — since adjudicated as rational selection, see Flags) |

`r2s1_direct-B3` and `r2s2_stacked-B3` are `running` (no part 5 yet) —
not listed here until they close. `r2s3_lf_train_signal-B4` is
`analyzing` — **CONFIRMED at part 5**, but part 6 (mechanism) and part 7
(register/close) have not landed yet — not listed in this table until it
closes; see the headline and Streams row above for the full verdict.
`r2s4_diag-B4` is `reviewed_fail` (fix cycle finished in the worktree,
uncommitted; re-review pending) — not listed here.

## Flags

- **The round's first CONFIRMED card, `r2s3_lf_train_signal-B4` (landed
  walk 12, unchanged this run)** — dashboard headline, see above.
  `status: analyzing` (landed walk 12);
  part 5 verdict F1∨F2∨F3∨F4 all FALSE; achievable gate
  `{ifc_poisson, sharp__cahn_hilliard, sharp__allen_cahn_2d}`; ceiling gate
  `{sharp__cahn_hilliard}` only; `sharp__fisher_kpp_2d` retires (fully
  absorbed by `ref_train_mean_n5`, 223/441/181% across draws — over-
  absorbed, not merely absorbed). B5 trigger NOT fired (max ceiling
  absorption 26.9% on `ch`, threshold 50%) → **stream closes on B4** per
  the pre-registered rule in `iteration_1.md`, pending the
  mechanism-analyzer (dispatched, turn 1) and register turn. Reading
  heterogeneity noted by the initial-analyzer: `ch` is unanimous 7/7 on
  all three contrasts; `ac` passes its primary reading (26.9x mce) but
  only 3/7 readings agree; `ifc` survives at 1.41x mce with 5/6 readings
  agreeing. Card-vs-job staleness flagged at walk 11's close remains
  resolved (unchanged this run). Mechanism-analyzer turn 1 remains
  in progress this run — live background process (`reanalysis_turn_1.py
  --repeats 40`, PID 2270940, ~17 min elapsed at check, 1200s timeout
  budget per attempt) has not yet produced `scratchpad/turn1/
  turn1_calibration_signal.json`; no stall — still within budget.
- **`r2s4_diag-B4` fix cycle, verified complete in the worktree at walk
  12, remains uncommitted this run** (build commit still `dc0d7ae`, no
  new commit on top of it, `git diff` byte-identical to walk 12). All three reviewer-mandated fixes from the `reviewed_fail`
  verdict confirmed present via `git diff` in
  `worktrees/r2s4_diag/B4`: (1) `_repo_root()` now iterates
  `WORKTREE_ROOT.parents` only (dropped `[WORKTREE_ROOT] +`); (2)
  `scripts/01_train_eval.sh`'s anatomy-script call is now fatal (`exit 1`
  + explicit `[FAIL]` message if `diagnostic.json` is missing/empty,
  replacing the masking `|| echo [warn] ...`); (3) a fresh **no-override**
  contract-tier re-verify ran (`scratchpad/reverify.log`,
  `reverify_contract.json`, `reverify_diag/`, 201 legs in 441.4s CPU) and
  this time correctly wrote `diagnostic.json` (63,697 bytes, confirmed on
  disk) to the real
  `${OUTPUTS_ROOT}/round2/r2s4_diag/B4/eval/diagnostic.json` — the exact
  seam that broke in attempt 1. Two reviewer SUGGEST items beyond the
  three required fixes were also folded in: a `noise_floor.json`
  cross-check assertion on the pre-registered equivalence bound (fails
  fatally before training if the value diverges from its declared
  source), and an eval-layer/in-family metric-seam assert on the scored
  leg; plus the ladder-audit certificate is now gated on the audit's own
  JSON verdict (`== "MISPAIRED"`), not on exit code alone (closes the
  residual argparse-exit-2 masking channel the reviewer flagged as
  SUGGEST). No agent process is currently active on this card (`ps aux`
  clean at this walk's check too) — still the natural handoff point for
  commit + re-review. The orchestrator has queued a commit nudge to the
  builder this cycle and will take over the mechanical commit itself if
  nothing lands by its next pulse. **Watch item for the next walk**:
  confirm a new commit lands on `round2/exp-r2s4_diag-B4` and a
  re-review verdict is produced; `job_ids` still `[]`, no SLURM
  submission yet.
- **`r2s2_stacked-B3` job-name-collision watch item, unchanged**: panel
  job 66267438 (`r2-r2s2_stacked-B3-s0`) and guard job 66267441
  (`r2-r2s2_stacked-B3-guard-s0`) remain distinctly named in `squeue`
  because both are still PENDING — the collision (reviewer finding R1,
  not code-fixed, tracked by job ID per the orchestrator's documented
  workaround) will only manifest once the guard leg starts RUNNING and
  its in-script `scontrol update` fires. Re-verify by job ID, not name,
  once either job transitions state.
- **Job 66262741 (r2s1_direct-B3, seed 0)**: confirmed via both `squeue`
  and `sacct` this run — still **PENDING**, Priority-queued, unchanged
  since the prior run's close.
- **Jobs 66267438 / 66267441 (r2s2_stacked-B3, seed 0 panel + guard)**:
  confirmed via both `squeue` and `sacct` this run — both still
  **PENDING**, Priority-queued, unchanged since the prior run's close.
- **Round-level instrument-defect pattern (carried forward, 7 independent
  confirmations; the `r2s4_diag-B4` code-review finding remains a
  distinct SLURM/path-resolution defect class, not folded into this
  count since it was caught pre-submission by review rather than in a
  scored run)**: `r2s1_direct`'s post-hoc-blend-stage class (adjudicated
  non-defective); `r2s2_stacked-B2`'s statistic mis-specification;
  `r2s4_diag-B3` turn-2's mis-specified `advantage_reachable`, turn-3's
  self-corrected probe-ordering bug; `r2s3_lf_train_signal-B3`'s resolved
  knife-edge; `r2s4_diag-B3` register-turn's ceiling/contamination/
  row-count triad and its foreign-data `stage_blend_decoder` zero-field
  catch — worth folding into the round-report action item once the round
  closes.
- **`r2s1_direct-B3`'s `stage_blend_decoder` zero-field item — remains
  ADJUDICATED, defect ruled OUT** (unchanged from several walks ago). No
  further action needed.
- **Timing ledger**: unchanged this run (17 entries, re-validated as
  parseable JSON, 2-key top-level structure `_note`/`entries`). No
  upsert due — all 3 remaining live jobs (66262741/66267438/66267441)
  still PENDING (confirmed via both `squeue` and `sacct`), no new
  COMPLETED job appeared in the 2-day `sacct` window this run.
- **Analyzer caveat (r2s1_direct-B1, from code-review)**, carried forward:
  the D3 certificate's aleatoric-floor estimate is window-sensitive — at
  the recipe's window (1000 closest pairs), `ext__helmholtz_2d` reads
  1.200, worse than the zero predictor. Must not be reported as a ceiling
  for helmholtz; `allen_cahn`'s ceiling must be reported as a range
  (0.315-0.471); `pfc`/`fisher_kpp` are window-robust and quotable.
- **Analyzer caveat (r2s2_stacked-B1, from code-review + register turn),
  preserved for the round report**: `ifc_poisson`'s rung ladder is UNPAIRED
  (independent condition draws per rung, min distance 0.08-0.30, never 0) —
  matches r2s3's independent finding, and is also confirmed by r2s4-B2 —
  three independent streams/estimators, a cross-stream benchmark-integrity
  item.
- **Analyzer caveat (r2s3_lf_train_signal-B1, from code-review)**, carried
  forward: the shared-max-abs-rungs scaler makes ifc_poisson's `rung_native`
  stage-1 loss ~42x amplitude-weighted toward rung 8 over HF (confound C1,
  card-locked design, not a build defect); F1 is epoch-matched but not
  step-matched (confound C2). r2s3-B2's card shipped a step-matched,
  per-rung-scaled repair of both confounds this round (now closed).
- **Analyzer caveat (r2s2_stacked-B3, from code-review, carried forward)**:
  pfc's pre-flight-instrument conflict directionally biases F1/F2/F3
  toward confirming the card's hypothesis — re-check any "≥2 of 4
  decidable" verdict with pfc dropped once part 6/7 land.
- **Analyzer caveat (r2s4_diag-B4, from code-review, now addressed in
  the uncommitted fix)**: `recipe.env R2S4B4_NOISE_FLOOR_JSON` was echoed
  into `resolved_recipe` but never read by the family; the fix adds a
  fatal cross-check assertion comparing the recipe's equivalence bound
  against the value the named file actually contains (see Flags above).
- **Analyzer caveat (r2s3_lf_train_signal-B4, from the initial-analyzer,
  new this run)**: card part 4's `E_ceil` column silently used `E_free`
  for the `fk`/`hz` rows instead of the class-wide `E_ceil` — the
  mechanism-analyzer must not quote that column verbatim for those two
  datasets. Also: `a0_split_ensemble` (15 HF rows, 3x compute) drives the
  `pfc` row on all 3 draws and `ac`'s d0 reading — label it wherever it
  drives a claim. Minor: card part 3 says "33 legs", the recipe and run
  both use 32.
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
- No reopen candidates on any of the 14 cards. No `blocked.md` file exists
  (no stream has ever blocked). **No abandoned streams** — none qualify
  (all 4 streams show clean complete/running/analyzing/reviewed_fail
  progressions with no skip/block history anywhere). `state/streams/`
  directory still does not exist — consistent with no abandonments ever
  being needed.
- Repo hygiene, final check: `git status --short experiment_cards/` on the
  round root is **clean** at this run's close — no card files were
  modified by the maintainer. This maintainer's own writes this run:
  `index.md`, `state/maintainer_report.md`. No changes were made to
  `state/timing_ledger.json` (no upsert due). Auto-sync tip unchanged
  at `f3ce653` since walk 12 — no external commits landed this run.
