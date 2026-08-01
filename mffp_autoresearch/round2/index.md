# MFFP Autoresearch Round 2 — Dashboard (updated 2026-08-01T19:43:11Z)

**Ninth maintainer walk since the operator halt/resume cycle.**
Halt landed 2026-08-01T01:31:54Z (commit `10d4e4c`), resume landed
2026-08-01 ~08:1x PDT (commit `b80e622`).

**Headline this run**: the code-reviewer's `r2s2_stacked-B3` verdict
landed (SUGGEST — submit as-is) just before this walk started, and the
orchestrator acted on it **live, inside this run's window**:
`r2s2_stacked-B3` went `built` → `running`, with **panel job 66267438 and
guard job 66267441 both submitted** (PENDING, Priority-queued).
The code-reviewer's own R1 finding (a job-name collision once the guard
job renames itself mid-run — `01_train_eval.sh` ignores `$DATASETS` when
constructing the name) was **not** code-fixed; the orchestrator took the
reviewer's documented workaround instead (track both legs by job ID, not
name) and recorded it verbatim in `state/r2s2_stacked/current_stage.txt`.
This is a live watch item: once the guard job actually starts running,
its name will collide with the panel job's name in `squeue`/`sacct` — job
IDs remain the only reliable disambiguator.
Both remaining B4 builders continued: `r2s3_lf_train_signal-B4`'s
training-free substitution audit is mid-sweep across the panel
(`ifc_poisson` done, `sharp__cahn_hilliard` running); `r2s4_diag-B4`'s
anatomy card exercised its full contract path on a 2-epoch smoke
(`ext__helmholtz_2d`, panel_geomean_skill 7.545), including a `last.pt`
checkpoint write, plus separate exploratory `ifc_poisson` full-tier
shakeout/midleg runs in scratchpad (not yet wired into the family's
contract path).
Job 66262741 (`r2s1_direct-B3`, seed 0) remains **PENDING**, unchanged
across this entire run.
`current_stage.txt` was refreshed by the orchestrator this run for all
three streams this maintainer had flagged as stale (r2s2/r2s3/r2s4) —
that staleness item is resolved. `current_batch.txt` counters, however,
still read stale values for all three (r2s2 "2", r2s3 "3", r2s4 "3")
despite each stream having moved past those batches — a separate,
narrower staleness item, carried forward below.

## Streams

| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r2s1_direct | 23.0636 (best_floor_panel_geomean) | 3 | r2s1_direct-B1 **complete**; r2s1_direct-B2 **complete**; r2s1_direct-B3 **running** | Unchanged this run. Seed-0 job **66262741 still PENDING** in `squeue`/`sacct` (Priority-queued, `Elapsed=00:00:00`) | **1 live/pending SLURM** (`r2-r2s1_direct-B3-s0`, job 66262741, PENDING) | No change; job still PENDING |
| r2s2_stacked | 23.0636 (best_floor_panel_geomean) | 3 *(card exists; `current_batch.txt` still stale at "2")* | r2s2_stacked-B1 **complete**; r2s2_stacked-B2 **complete**; r2s2_stacked-B3 **running (caught mid-walk this run)** | `status: built` → `running` — code-reviewer's SUGGEST verdict landed ~19:38Z (build commit `86ef67cc`, all 8 review questions PASS, Q5 SLURM SUGGEST on the job-name-collision finding R1). Orchestrator submitted **panel job 66267438 + guard job 66267441** this run (both PENDING). `current_stage.txt` refreshed with the reviewer's 3 analyzer caveats: match by job ID not name (R1 workaround); no ceiling column owed on any surviving null (P2/R5, `alpha_nn==0` degenerate `could_not_fire` check); pfc pre-flight conflict biases toward the card's hypothesis, re-check any "≥2 of 4" verdict with pfc dropped (P1) | **2 live/pending SLURM** (`r2-r2s2_stacked-B3-s0` 66267438, `r2-r2s2_stacked-B3-guard-s0` 66267441, both PENDING) | Submitted this run, minutes before close |
| r2s3_lf_train_signal | 23.0636 (best_floor_panel_geomean) | 4 *(`current_batch.txt` still reads "3")* | r2s3_lf_train_signal-B1..B3 **complete**; r2s3_lf_train_signal-B4 **drafted** | Builder mid-sweep this run: `models_r2/r2s3_b4_substitution/` gained `readings.py` + `run_diagnostic.py` (joining `controls.py`/`manifest.json`/`paths.py`/`lf_guard.py`/`heads.py`). Smoke log shows `ifc_poisson` (1 draw) done in 54.21s, `sharp__cahn_hilliard` (3 draws) running at last check. Training-free (`epochs: 0`, no GPU) substitution-audit diagnostic; `expected_falsification` remains a fully pre-registered 2-of-3 {ifc, ch, ac} threshold table over B3's shipped artifacts | **0 live SLURM** (training-free; no submission expected) | Smoke sweep in progress this run |
| r2s4_diag | **19.8178** (certified_3seed_panel_geomean, CI95 [19.385, 20.527]) | 4 *(`current_batch.txt` still reads "3")* | r2s4_diag-B1..B3 **complete**; r2s4_diag-B4 **drafted** | Builder exercised the full contract path this run: `models_r2/r2s4_b4_anatomy/` gained `smoke_eval.py`/`subsets.py`/`rung_cv.py`/`lf_registration.py`/`model.py`; contract smoke on `ext__helmholtz_2d` (2 epochs) passed with `panel_geomean_skill` 7.545451722377857 and a `last.pt` checkpoint written. Separate exploratory `ifc_poisson` full-tier runs (`shakeout`, `midleg`) also landed in scratchpad — pre-registration/anatomy dry-runs, not yet the family's scored contract path | **0 live SLURM** (card drafted, no submission yet) | Contract-smoke path exercised this run, incl. checkpoint |

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

**3 live/pending `r2-*` SLURM jobs** (up from 1 at the prior close — the
new pair submitted this run following the code-reviewer's SUGGEST
verdict). `sacct` 2-day window otherwise shows the same 16 `r2-*` jobs,
all COMPLETED 0:0, identical to the timing ledger — no ledger upsert due
(all 3 live jobs are PENDING, none COMPLETED yet). Non-SLURM agent
activity this run: `r2s3_lf_train_signal`'s B4 builder mid-sweep through
its training-free panel; `r2s4_diag`'s B4 builder exercised its full
contract-smoke path including checkpoint resume machinery.

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

`r2s1_direct-B3` and `r2s2_stacked-B3` are `running` (no part 5 yet) — not
listed here until they close. `r2s3_lf_train_signal-B4`,
`r2s4_diag-B4` are `drafted`/builder-active (not built/scored) — not
listed here.

## Flags

- **`r2s2_stacked-B3` went `built` → `running` — the code-reviewer's
  SUGGEST verdict and the orchestrator's submission both landed inside
  this run's window** (verdict ~19:38Z, submission moments later,
  caught within a few minutes of it happening). Verdict: **SUGGEST —
  submit as-is**. All 8 review questions PASS except Q5 (SLURM
  correctness), which is SUGGEST on finding **R1**: `01_train_eval.sh`
  renames *any* job to `r2-r2s2_stacked-B3-s${SEED}` unconditionally
  (ignores `$DATASETS`), so `submit_guard.sh`'s distinct
  `--job-name=r2-r2s2_stacked-B3-guard-s0` is overwritten mid-run to
  collide with the panel job's name — violating slurm_rules §6 (one job
  name = one card+seed), the key this maintainer matches jobs on. The
  code fix was **not** applied; the orchestrator took the reviewer's
  documented workaround instead — track both legs by job ID, not name —
  and recorded this in `state/r2s2_stacked/current_stage.txt`. **Both
  jobs submitted this run**: panel `66267438` (`r2-r2s2_stacked-B3-s0`)
  and guard `66267441` (`r2-r2s2_stacked-B3-guard-s0`), both currently
  **PENDING** and still distinctly named in `squeue` (the collision only
  manifests once the guard leg actually starts running via its in-script
  `scontrol update`) — **watch item for the next walk**: confirm via job
  ID, not name, once either job transitions to RUNNING.
  Other review findings, no action required before submit: P1 (pfc
  pre-flight conflict is real but structurally confined to arms A2/A3,
  never the scored `A1_lsi` arm — carries a directional caveat toward
  confirming the card's hypothesis, re-check any "≥2 of 4" verdict with
  pfc dropped); P2/R5 (no ceiling/headroom column and no prediction
  dumps shipped — `ledger_contamination_audit.py` and
  `band_retention_probe.py` cannot run post-hoc on this card, though
  `alpha_nn==0` degenerate-null cases remain detectable from the shipped
  record); P3 (the `--time 02:30:00` request is credible — the 51m44s
  smoke ran CPU-bound on a contended login node with a 23% duty cycle,
  while `state/timing_ledger.json`'s in-family comparator `r2s2_stacked-B2`
  (33.58 min actual, same panel/lineage) scales to ~56 min, well inside
  the requested window — do not raise it).
- **`r2s3_lf_train_signal-B4` builder mid-sweep this run**:
  `models_r2/r2s3_b4_substitution/` gained `readings.py` and
  `run_diagnostic.py`. Smoke log confirms `ifc_poisson` (1 draw)
  completed in 54.21s with `certified_min_claimable_effect`
  0.9377041289531141 correctly read from `state/anchors/floors.json`;
  `sharp__cahn_hilliard` (3 draws) was running at last check. No status
  change on the card yet (still `drafted`, `job_ids: []`, training-free
  so no SLURM submission expected).
- **`r2s4_diag-B4` builder exercised the full contract path this run**:
  `models_r2/r2s4_b4_anatomy/` gained `smoke_eval.py`, `subsets.py`,
  `rung_cv.py`, `lf_registration.py`, `model.py`. Contract smoke on
  `ext__helmholtz_2d` (2 epochs) passed — `panel_geomean_skill`
  7.545451722377857 — with a `last.pt` checkpoint written under
  `scratchpad/eval_results/`, confirming the checkpoint-resume
  contract requirement is exercised. Separate exploratory `ifc_poisson`
  full-tier runs (`shakeout`, `midleg`, plus 31-subset `ifc_full_ckpt`
  prediction dumps) also landed in scratchpad — these look like
  pre-registration/anatomy dry-runs for the card's exhaustive-subset
  design, not yet wired into the scored contract path. No status change
  on the card yet (still `drafted`, `job_ids: []`).
- **Job 66262741 (r2s1_direct-B3, seed 0)**: confirmed via both `squeue`
  and `sacct` at two checks this run — still **PENDING**, Priority-queued,
  unchanged since the prior run's close.
- **Jobs 66267438 / 66267441 (r2s2_stacked-B3, seed 0 panel + guard)**:
  new this run, confirmed via both `squeue` and `sacct` at final
  re-check — both **PENDING**, Priority-queued, distinctly named as of
  this check (see job-name-collision watch item above).
- **Staleness, narrower now**: `current_stage.txt` was refreshed by the
  orchestrator this run for all three streams previously flagged
  (r2s2/r2s3/r2s4) — **that item is resolved**. `current_batch.txt`
  counters remain stale, however: `state/r2s2_stacked/current_batch.txt`
  reads "2" (card is on batch 3), `state/r2s3_lf_train_signal/current_batch.txt`
  and `state/r2s4_diag/current_batch.txt` both read "3" (cards are on
  batch 4). Orchestrator-owned; carried forward as a narrower, still-open
  item.
- **Round-level instrument-defect pattern (carried forward, 7 independent
  confirmations, no new occurrence this run)**: `r2s1_direct`'s
  post-hoc-blend-stage class (adjudicated non-defective);
  `r2s2_stacked-B2`'s statistic mis-specification; `r2s4_diag-B3`
  turn-2's mis-specified `advantage_reachable`, turn-3's self-corrected
  probe-ordering bug; `r2s3_lf_train_signal-B3`'s resolved knife-edge;
  `r2s4_diag-B3` register-turn's ceiling/contamination/row-count triad
  and its foreign-data `stage_blend_decoder` zero-field catch — worth
  folding into the round-report action item once the round closes.
- **`r2s1_direct-B3`'s `stage_blend_decoder` zero-field item — remains
  ADJUDICATED, defect ruled OUT** (unchanged from 3 walks ago). No
  further action needed.
- **Timing ledger**: unchanged this run — 16 entries, still parseable
  JSON. All 3 live SLURM jobs remain PENDING, not COMPLETED — no upsert
  due yet.
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
- **Analyzer caveat (r2s2_stacked-B3, from this run's code-review, new)**:
  pfc's pre-flight-instrument conflict directionally biases F1/F2/F3
  toward confirming the card's hypothesis (see Flags above) — re-check
  any "≥2 of 4 decidable" verdict with pfc dropped once part 6/7 land.
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
  (all 4 streams show clean complete/drafted/running progressions with no
  skip/block history anywhere). `state/streams/` directory still does not
  exist — consistent with no abandonments ever being needed.
- Repo hygiene, final re-check: `git status --short .` on the round root
  at close shows two deltas — `experiment_cards/r2s2_stacked/batch_3/B3.json`
  (M — orchestrator-owned, `built`→`running`, job_ids populated, caught
  mid-walk) and `state/r2s2_stacked/current_stage.txt` (M — orchestrator-
  owned refresh with the reviewer's caveats). The r2s3/r2s4
  `current_stage.txt` refreshes observed earlier in this run were already
  committed by the external auto-sync (`1b2da59`, "round2: auto-sync
  2026-08-01T19:32:26Z") before this run's final check. This maintainer's
  own writes this run: `index.md`, `state/maintainer_report.md`. No Write
  call this run touched `experiment_cards/`, `tools/`, or any other-
  agent-owned `state/` file. `state/timing_ledger.json` unchanged (no
  COMPLETED job to upsert yet — gitignored regardless).
