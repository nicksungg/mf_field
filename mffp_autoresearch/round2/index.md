# MFFP Autoresearch Round 2 — Dashboard (updated 2026-08-01T17:56:38Z)

**Fifth maintainer walk since the operator halt/resume cycle.**
Halt landed 2026-08-01T01:31:54Z (commit `10d4e4c`), resume landed
2026-08-01 ~08:1x PDT (commit `b80e622`).

**Very high-churn walk** — 3 separate re-checks each caught a further
mid-walk delta, matching the pattern of prior runs' final re-verification
catches, but compounding this time. Final settled state:
**`r2s3_lf_train_signal-B3` closed end-to-end** (mechanism turn 3 + register
turn both landed; 10th card closed round-wide; batch-4 websearch already
dispatched and in progress). **`r2s1_direct-B3` went all the way from
`built` to `running`**: code-review (SUGGEST, 1 headline submit-blocker) →
orchestrator discharged the blocker with an explained re-smoke → **job
`66262741` submitted and PENDING in `squeue`**. **`r2s2_stacked-B3`**
drafted (brainstormer chose B3-not-close) with a builder worktree created
but no model code landed yet. **`r2s4_diag-B3`** advanced mechanism
`turn_2`→**`turn_3`** (19 findings; a probe-ordering bug was found and
self-corrected mid-turn), part 7 not yet written.

## Streams

| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r2s1_direct | 23.0636 (best_floor_panel_geomean) | 3 | r2s1_direct-B1 **complete**; r2s1_direct-B2 **complete**; r2s1_direct-B3 **running** *(new this run)* | B1/B2 unchanged. **B3 this run: `built`→`reviewed_suggest`→`running`.** Code-reviewer landed 9 findings (7 PASS, 2 SUGGEST): #5 non-blocking SLURM job-name nit; #6 HEADLINE — the disjoint-fold (helmholtz) contract-smoke was stale w.r.t. `HEAD`'s `code_hash`, named a submit blocker. The orchestrator discharged it: re-ran the smoke at `HEAD` with the full 72-key `ENV_ARGS` (exit 0, nRMSE 1.140818334879289 bit-identical to the builder's original run); the `code_hash` delta (`1e9abd22` vs `d8cc06f0`) is explained as env-inclusion in `code_hash()` — the empty-env hash at `HEAD` equals `d8cc06f0` exactly, so no code drift. Seed-0 job **`66262741` submitted, PENDING** (h200, Priority-queued) | **1 live/pending SLURM** (`r2-r2s1_direct-B3-s0`, job 66262741, PENDING) | `built`→`reviewed_suggest`→`running` this run |
| r2s2_stacked | 23.0636 (best_floor_panel_geomean) | 3 *(card now exists; `current_batch.txt` still stale at "2")* | r2s2_stacked-B1 **complete**; r2s2_stacked-B2 **complete**; r2s2_stacked-B3 **drafted** *(new this run)* | B1/B2 unchanged. **New this run**: the batch-3 brainstormer chose B3-not-close (a 4-arm zero-gradient scored design: `A1_lsi` scored, an Operator-Boosting base-swap control, 5 in-job fold/train seeds vs the certified mce) and drafted `r2s2_stacked-B3` (category `zero_gradient_stage_attribution`). A fresh worktree/branch `round2/exp-r2s2_stacked-B3` was created at base `9e10d41`; the builder has been dispatched but **no model code has landed yet** (`models_r2/` does not exist in the worktree at this final check, no live process). `state/r2s2_stacked/current_stage.txt` was **refreshed by the orchestrator this run** ("B3 building — brainstormer chose B3-not-close … builder dispatched 2026-08-01") — the 3-run-running staleness flagged by prior walks is **resolved**; `current_batch.txt` still reads stale "2" | **0 live SLURM**; **0 live local process** (builder dispatched, not yet producing code) | Card drafted + worktree created, staleness resolved (new) |
| r2s3_lf_train_signal | 23.0636 (best_floor_panel_geomean) | 4 *(websearch in progress; `current_batch.txt` still reads "3")* | r2s3_lf_train_signal-B1 **complete**; r2s3_lf_train_signal-B2 **complete**; r2s3_lf_train_signal-B3 **complete** *(closed this run — 10th card round-wide)* | B1/B2 unchanged. **B3 closed end-to-end this run**: mechanism turn 3 landed part 6 (23 findings) — F1/F2 knife-edge adjudicated **FALSIFIED**, robust across 5/7 defensible threshold readings (a new gain-calibrated split reading M4 independently fails F2 too). Register turn then landed part 7: `cratered_verdict: cratered` (third limb only — falsification fired decisively; no crash, well below the 1.5x-anchor crater bound). Panel geomean skill (`A1_lf_cov` primary arm) 17.114970 vs anchor 23.0636 (comparison arm `A0_nolf` 32.4663). 2 tools promoted: `tools/effect_threshold_readings.py`, `tools/map_dispersion_scale_shape.py`. `next_direction`: the round's success-criterion-1 (≥3-dataset claimable with/without-LF-training contrast) is still met on exactly 3 datasets under the operative threshold — a **B4-or-close decision input**. The stream has already progressed past that decision: batch counter advanced, a **B4 websearcher is live** (`websearches/r2s3_lf_train_signal/batch_4/summary_so_far.md` landed, iterations not yet started). `state/r2s3_lf_train_signal/current_stage.txt` was **refreshed by the orchestrator** to reflect the B3 close and B4-decision framing this run | **0 live SLURM** (job terminal); **0 live local process** (register turn + B4 websearch dispatch both settled at this check) | Closed: `analyzing`→`complete`→batch counter advancing to 4 (B4 websearch live) |
| r2s4_diag | **19.8178** (certified_3seed_panel_geomean, CI95 [19.385, 20.527]) | 3 | r2s4_diag-B1 **complete**; r2s4_diag-B2 **complete**; r2s4_diag-B3 **analyzing** | B1/B2 unchanged. B3: mechanism turn 3 **landed this run** (`reanalysis_progress: turn_2`→**`turn_3`**, 19 findings total, 6 new this turn). Spatial-dispersion probes (`--probe ab`) on the previously-untouched `advantage_unreachable` (13.12-136.18 skill units): per-band error-energy localisation confirmed (pfc 99.9% in one band; allen_cahn/fisher_kpp/cahn_hilliard each concentrated in 1-2 bands), an interface-proximity hypothesis (P3) **FALSIFIED**, a helmholtz-specific collapse-to-near-zero-field mechanism identified, and a mid-turn **probe-ordering bug found and self-corrected** (`oof_row_index` in the dumped npz is a permutation, not identity — first pass mismatched dataset-order vs npz-order, corrected before any finding was carded). Part 7 not yet written — register turn is the mechanism-analyzer's next step, still open. `state/r2s4_diag/current_stage.txt` still reads stale turn-1 text — **new staleness occurrence, first flagged this run** for this stream | **0 live SLURM** (job terminal); **0 live local process** (turn-3 script exited cleanly after landing its final leg) | Turn 3 landed (`turn_2`→`turn_3`), part 7 pending |

**Anchor note**: r2s4_diag remains the only stream with a *certified* anchor
(`certified_3seed_panel_geomean`, 19.8178) — r2s1_direct, r2s2_stacked,
r2s3_lf_train_signal remain on the launch-time `best_floor_panel_geomean`
anchor (23.0636, `certified_utc` 2026-07-31T14:20:17Z, unchanged). No anchor
deltas this run — all 4 `state/anchors/*.json` files' mtimes predate this
run's entire window. All anchors rendered verbatim from `state/anchors/*.json`.

## Running / pending jobs

| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| 66262741 | r2s1_direct-B3 (seed 0) | PENDING | 0:00 | (Priority) |

**1 live/pending `r2-*` SLURM job** at this final check
(`r2-r2s1_direct-B3-s0`, job 66262741, submitted moments before this
walk's close after the code-reviewer's gate was discharged; queued on
Priority, not yet running). `sacct` 2-day window otherwise shows the same
16 `r2-*` jobs, all COMPLETED 0:0, identical to the timing ledger — no
ledger upsert due yet for 66262741 (still PENDING, not COMPLETED).
**0 live non-SLURM agent processes** at this final check — all this-cycle
background work (r2s3-B3's turn-3 script + register turn + B4 websearch
dispatch, r2s1-B3's code-reviewer + gate-discharge re-smoke, r2s2-B3's
worktree creation + builder dispatch, r2s4-B3's turn-3 script) has settled
or exited cleanly.

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
| r2s3_lf_train_signal-B3 | model | 17.114970 (`A1_lf_cov` primary arm, single seed 0) vs anchor 23.0636 (comparison arm `A0_nolf` 32.4663) | **falsified** (F1/F2 knife-edge adjudicated FALSIFIED, robust across 5/7 defensible threshold readings incl. a new gain-calibrated split reading M4; only the two readings pricing zero HF-subset-draw variance return CONFIRMED); the round's success-criterion-1 (≥3-dataset claimable with/without-LF-training contrast) is still met on exactly 3 datasets under the operative threshold. `cratered_verdict: cratered` (third limb only — falsification fired decisively; not a crash, not >1.5x anchor) | **2 tools**, both correctly indexed: `tools/effect_threshold_readings.py` (7-reading threshold-adjudication tool; surfaces `mce_over_observed_split_range` as a provenance smell), `tools/map_dispersion_scale_shape.py` (splits inter-prediction dispersion into total vs shape-only; found allen_cahn's 3 LF-trained models sit within 0.41 skill units of each other but 100.5 units apart in function space — "scale, not map") |

`r2s4_diag-B3` (`analyzing`, part 5 written/falsified, `reanalysis_progress:
turn_3` landed this run, part 6 has 19 findings, part 7 pending) is open
but has not landed part 7 — not listed here until it closes.
`r2s1_direct-B3` is `running` (job 66262741 PENDING, no part 5 yet) — not
listed here until it closes. `r2s2_stacked-B3` is `drafted` (not built) —
not listed here.

## Flags

- **`r2s3_lf_train_signal-B3` closed end-to-end this run — 10th card
  closed round-wide**: mechanism turn 3 (part 6, 23 findings) then the
  register turn (part 7, 2 tools) both landed inside this single walk.
  Falsification verdict: F1/F2 knife-edge **FALSIFIED** (5/7 defensible
  threshold readings agree, including a new gain-calibrated split reading
  M4 that independently fails F2). `cratered_verdict: cratered` on the
  third limb only (falsification fired decisively; job completed clean,
  well under the 1.5x-anchor crater bound). The stream has already acted
  on the B4-or-close decision this cycle: batch counter is advancing and
  a **B4 websearcher is live** (`websearches/r2s3_lf_train_signal/batch_4/
  summary_so_far.md` landed; full iteration set not yet run).
- **`r2s1_direct-B3` went from `built` all the way to `running` this
  run**: code-review landed SUGGEST (9 findings) with one HEADLINE submit
  blocker (finding #6 — disjoint-fold smoke stale vs `HEAD`'s code_hash).
  The orchestrator discharged the blocker itself, appending a review-note
  explaining the code_hash delta as an env-inclusion artifact (not code
  drift) after re-running the smoke bit-identically at `HEAD` with the
  full env — **this maintainer's earlier-in-walk flag of the code_hash
  mismatch as needing reconciliation was addressed by the orchestrator
  before this walk closed**, worth noting as a positive signal that
  cross-agent flags in this dashboard get acted on same-cycle. Seed-0 job
  **66262741 submitted, PENDING** on h200.
- **`r2s2_stacked-B3` drafted, builder dispatched, no model code yet**:
  brainstormer chose B3-not-close (4-arm zero-gradient scored design,
  direct successor to B2's part-7 open question); worktree/branch
  `round2/exp-r2s2_stacked-B3` created at base `9e10d41`. The
  previously-3-runs-running staleness on `state/r2s2_stacked/
  current_stage.txt` was **refreshed by the orchestrator this run** —
  resolved, no longer flagged. `current_batch.txt` still reads stale "2".
- **`r2s4_diag-B3` turn 3 landed this run, part 7 still open**: spatial
  probes on `advantage_unreachable` confirmed per-band error localisation
  (pfc/allen_cahn/fisher_kpp/cahn_hilliard each concentrated in 1-2
  bands), falsified an interface-proximity hypothesis (P3), and
  identified a helmholtz-specific near-zero-field collapse mechanism. A
  mid-turn probe-ordering bug (`oof_row_index` is a permutation, not
  identity) was found and self-corrected before any finding was carded —
  worth noting as clean self-correction, not an integrity concern.
  **New staleness this run**: `state/r2s4_diag/current_stage.txt` still
  reads turn-1 text despite the card being at turn 3 — first occurrence
  of this staleness class for this stream (the r2s2 and r2s3 analogues
  were both refreshed by the orchestrator this same run).
- **Round-level instrument-defect pattern (carried forward, now 6
  independent confirmations)**: `r2s1_direct`'s post-hoc-blend-stage
  instrument-error class, `r2s2_stacked-B2`'s statistic
  mis-specification findings, `r2s4_diag-B3` turn-2's mis-specified
  `advantage_reachable` AND turn-3's self-corrected probe-ordering bug,
  and `r2s3_lf_train_signal-B3`'s resolved knife-edge (an mce-only
  threshold reading was pricing the card's dominant noise source at
  zero) plus its companion "LF-trained models are not a canonical
  solution" finding — worth folding into the same round-report action
  item once r2s4-B3 lands part 7.
- **Timing ledger**: **unchanged this run** — 16 entries, still parseable
  JSON. `r2s1_direct-B3`'s new job 66262741 is PENDING, not COMPLETED —
  no upsert due yet; will be picked up next walk once it lands.
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
- No reopen candidates on any of the 11 cards (`r2s2_stacked-B3` included).
  No `blocked.md` file exists (no stream has ever blocked). **No abandoned
  streams** — none qualify (all 4 streams show clean complete/analyzing/
  drafted/running progressions with no skip/block history anywhere).
  `state/streams/` directory still does not exist — consistent with no
  abandonments ever being needed.
- Repo hygiene: `git status --short .` on the round root (excluding
  `worktrees/`) at this final check: `experiment_cards/r2s1_direct/batch_3/B3.json`
  (M — `built`→`reviewed_suggest`→`running`, code-reviewer/orchestrator-owned),
  `experiment_cards/r2s3_lf_train_signal/batch_3/B3.json`
  (M — `analyzing`→`complete`, mechanism-analyzer/register-turn-owned),
  `experiment_cards/r2s4_diag/batch_3/B3.json` (M — `turn_2`→`turn_3`,
  mechanism-analyzer-owned), `state/orchestrator_flow.md` +
  `state/{r2s1_direct,r2s2_stacked,r2s3_lf_train_signal}/current_stage.txt`
  (M — orchestrator-owned state refreshes, several resolving staleness
  this maintainer flagged in prior runs), `tools/effect_threshold_readings.py`
  + `tools/index.md` (M — tool promotion from r2s3-B3's register turn),
  `tools/map_dispersion_scale_shape.py` (?? — new tool from the same
  register turn), `brainstormer/r2s2_stacked/batch_3/report.md` +
  `experiment_cards/r2s2_stacked/batch_3/` + `websearches/r2s3_lf_train_signal/batch_4/`
  (?? — brainstormer/builder/websearcher-owned). `index.md` +
  `state/maintainer_report.md` (M — this maintainer's own writes this
  run). No Write call this run touched `experiment_cards/`, `tools/`, or
  any `state/` file this maintainer doesn't own. `state/timing_ledger.json`
  untouched (no COMPLETED job to upsert yet — gitignored regardless).
