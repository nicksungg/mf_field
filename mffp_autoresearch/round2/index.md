# MFFP Autoresearch Round 2 — Dashboard (updated 2026-08-01T19:20:00Z)

**Eighth maintainer walk since the operator halt/resume cycle.**
Halt landed 2026-08-01T01:31:54Z (commit `10d4e4c`), resume landed
2026-08-01 ~08:1x PDT (commit `b80e622`).

**Headline this run**: two new B4 cards now exist across the two streams
still open (`r2s3_lf_train_signal-B4`, `r2s4_diag-B4`), both `drafted`,
both with builders actively landing files.
`r2s4_diag-B4` is the program.md §12.4 exception card (WITH training) —
its part 2 records, for the first time on any card, that the literal
`N_hf ∈ {5, 20, 50}` mandate is **unexecutable** on `ifc_poisson` (no
20/50-row 64×64 training set exists) and re-expresses it as two
measurable halves (exhaustive HF-subset curve + within-rung
generalisation-gap ladder).
`r2s3_lf_train_signal-B4` is a training-free substitution audit whose
`expected_falsification` section is a fully pre-registered outcome table —
the stream's B4-vs-close call now resolves **mechanically** off a 2-of-3
threshold once the card's arms are scored, not a fresh brainstormer
judgment.
Job 66262741 (`r2s1_direct-B3`, seed 0) is **still PENDING**, unchanged.
`r2s2_stacked-B3` went `drafted` -> `built` — **caught mid-walk during
the pre-return checklist re-verification**: family `models_r2/r2s2_zerograd`
built (commit `86ef67cc`), contract smoke passed on `ext__helmholtz_2d`,
a genuine pfc pre-flight-instrument conflict recorded and stamped rather
than silently resolved, a timing risk flagged (51m44s wall for a 2-epoch
single-dataset smoke on a contended login node). `job_ids` still empty —
no SLURM submission yet.

## Streams

| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r2s1_direct | 23.0636 (best_floor_panel_geomean) | 3 | r2s1_direct-B1 **complete**; r2s1_direct-B2 **complete**; r2s1_direct-B3 **running** | Unchanged this run. Seed-0 job **66262741 still PENDING** in `squeue`/`sacct` (Priority-queued, `Elapsed=00:00:00`) | **1 live/pending SLURM** (`r2-r2s1_direct-B3-s0`, job 66262741, PENDING) | No change; job still PENDING |
| r2s2_stacked | 23.0636 (best_floor_panel_geomean) | 3 *(card exists; `current_batch.txt` still stale at "2")* | r2s2_stacked-B1 **complete**; r2s2_stacked-B2 **complete**; r2s2_stacked-B3 **built (caught mid-walk this run)** | `status: drafted` -> `built` caught during the pre-return checklist re-verification (card mtime 2026-08-01T19:13:40Z, after this run's first pass). Family `models_r2/r2s2_zerograd` built on branch `round2/exp-r2s2_stacked-B3`, commit `86ef67cc` (8 files re-vendored byte-identically from sibling B2, sha256-pinned). Contract smoke on `ext__helmholtz_2d` PASSED (exit 0, nRMSE 1.4487706717896234, skill 4.844847851928688, `code_hash` verified). Pre-flight instruments recorded a genuine `pfc` conflict (target-scale audit says switch to per-sample norm; eligibility audit says NO_GO) — implemented per the card's literal rule and stamped `conflict_with_eligibility` rather than silently resolved; only touches arms A2/A3, never the scored zero-gradient A1_lsi arm. TIMING RISK flagged: 2-epoch single-dataset smoke took 51m44s wall (contended login node, CPU-bound k-NN+rFFT); `--time 02:30:00` requested. `job_ids` still empty — no SLURM submission yet | **0 live SLURM** (no submission yet) | Built, caught mid-walk; not yet submitted |
| r2s3_lf_train_signal | 23.0636 (best_floor_panel_geomean) | 4 *(`current_batch.txt` still reads "3")* | r2s3_lf_train_signal-B1..B3 **complete** (10th card, closed 3 walks ago); r2s3_lf_train_signal-B4 **drafted** | **New this run's builder activity**: `worktrees/r2s3_lf_train_signal/B4/models_r2/r2s3_b4_substitution/` gained `controls.py` + `readings.py` (joining `manifest.json`/`paths.py`/`lf_guard.py`/`heads.py`, all landed within this run's window). Training-free (`epochs: 0`, no GPU) substitution-audit diagnostic. `expected_falsification` is a fully pre-registered 2-of-3 {ifc, ch, ac} threshold table over B3's shipped artifacts — the B4 outcome resolves mechanically, not by fresh brainstormer judgment. Predicted claimable set under the achievable-control gate: `{ch 113x, ac 26.8x, ifc 1.41x}` (fk retires); under the stricter ceiling gate: `{ch}` only | **0 live SLURM** (training-free; no submission expected) | Builder actively landing files this run |
| r2s4_diag | **19.8178** (certified_3seed_panel_geomean, CI95 [19.385, 20.527]) | 4 *(`current_batch.txt` still reads "3")* | r2s4_diag-B1..B3 **complete** (11th card, closed 3 walks ago); r2s4_diag-B4 **drafted (new this run)** | **Card landed this run** (18:52:32Z, 6 min after prior close): the program.md §12.4 exception card (WITH training, 200 epochs, strict 1 seed) — the stream's last live route to round success-criterion-1. Part 2 records, verbatim from the brainstormer's source iteration, that the literal `N_hf ∈ {5, 20, 50}` mandate is **unexecutable on `ifc_poisson`** (no 20-row/50-row 64×64 training set on disk) and re-expresses it as (1) an exhaustive HF-subset curve on the scored rung and (2) a within-rung generalisation-gap ladder across the 4 independent rungs, governed by a pre-registered equivalence bound (certified ifc MCE 0.9377041289531141, O1/O2/O3 outcome rule). Worktree created (fresh scaffolding only) — no model code beyond scaffold observed, builder not yet dispatched | **0 live SLURM** (card just drafted, no submission yet) | Card drafted this run; §12.4 unexecutable-mandate fact recorded |

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

**1 live/pending `r2-*` SLURM job** (unchanged from the prior run — still
queued on Priority, has not started running). `sacct` 2-day window
otherwise shows the same 16 `r2-*` jobs, all COMPLETED 0:0, identical to
the timing ledger — no ledger upsert due. Non-SLURM agent activity this
run: `r2s3_lf_train_signal`'s B4 builder actively landing files;
`r2s2_stacked`'s B3 builder completed its build (contract smoke passed,
caught mid-walk going `drafted` -> `built`, no submission yet);
`r2s4_diag`'s B4 card freshly drafted, builder not yet dispatched.

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

`r2s1_direct-B3` is `running` (job 66262741 PENDING, no part 5 yet) — not
listed here until it closes. `r2s2_stacked-B3`, `r2s3_lf_train_signal-B4`,
`r2s4_diag-B4` are all `drafted` (not built/scored) — not listed here.

## Flags

- **`r2s2_stacked-B3` went `drafted` -> `built` — caught mid-walk during
  the pre-return checklist re-verification** (same class of catch as
  prior runs). First pass (`git status` at ~19:06Z) found the round root
  clean with the card still `drafted`; the pre-return re-check
  (~19:13Z) found `experiment_cards/r2s2_stacked/batch_3/B3.json`
  modified, card mtime 2026-08-01T19:13:40Z. Build: family
  `models_r2/r2s2_zerograd` on branch `round2/exp-r2s2_stacked-B3`,
  commit `86ef67cc` (forked from `round2-substrate` `9e10d41`); 8 files
  re-vendored byte-identically from the sibling B2 worktree, each
  sha256-pinned in `manifest.json._vendored`. Contract smoke on
  `ext__helmholtz_2d` (2 epochs) PASSED: exit 0, `splits.test_hf`
  nRMSE 1.4487706717896234, skill 4.844847851928688, committed-tree
  `code_hash` verified byte-identical to the smoke result's recorded
  hash. Pre-flight instruments recorded a genuine conflict on `pfc`
  between `target_scale_spread_audit` (NEAR_ZERO_TARGETS -> switch to
  per-sample normalisation) and `persample_norm_eligibility`
  (NO_GO_PROMOTES_NOISE) — implemented per the card's literal rule
  (target-scale verdict governs) and stamped `conflict_with_eligibility`
  on every affected record rather than silently resolved; the switch
  only touches arms A2/A3, never the scored zero-gradient `A1_lsi` arm,
  so no scored number depends on it. A TIMING RISK is flagged in
  `build_notes`: the 2-epoch single-dataset contract smoke took 51m44s
  wall on a contended login node (CPU-bound k-NN retrieval + rFFT
  transfer over 400x256x256 float64 blocks); `scripts/01_train_eval.sh`
  still requests `--time 02:30:00` per the card's own `_timing`
  estimate, sized against B2's much faster 33.58 min for fewer corrector
  trainings — worth a debugger's attention before the first submit.
  `job_ids` still empty — no SLURM submission observed yet as of this
  run's close.
- **`r2s4_diag-B4` card landed this run — first-time §12.4 fact recorded**.
  The program.md §12.4 exception card (WITH training, `epochs: 200`,
  strict 1 seed) — the stream's last live route to round success-
  criterion-1. Its part 2 records, transcribed verbatim from the
  brainstormer's source iteration (`brainstormer/r2s4_diag/batch_4/iteration_1.md`,
  "Step 3 — What can the {5, 20, 50} mandate actually mean here?"), that
  §12.4's literal `N_hf ∈ {5, 20, 50}` sweep is **unexecutable** on
  `ifc_poisson`: there is no 20-row or 50-row 64×64 training set on disk
  (`fidelity_32` has 20 rows at 32×32, `fidelity_16` has 50 rows at
  16×16, independently-drawn conditions each); manufacturing one is
  barred by immutables 1 and 11. The card re-expresses the mandate as two
  measurable halves instead: an exhaustive HF-subset learning curve
  (all `C(5,n)` subsets, n∈{1..5}) on the scored `fidelity_64` rung, and
  a within-rung generalisation-gap ladder across the 4 independent rungs
  with no cross-rung training. A pre-registered equivalence bound
  (certified ifc `min_claimable_effect` 0.9377041289531141; O1 EFFECT /
  O2 EQUIVALENCE / O3 INCONCLUSIVE, Harms & Lakens PubMed 30873486)
  governs the primary estimand `Delta_5_1`. Worktree
  `worktrees/r2s4_diag/B4` created (fresh scaffolding only) — builder not
  yet dispatched as of this run's close.
- **`r2s3_lf_train_signal-B4` builder actively landing files this run —
  second first-time fact recorded**. `worktrees/r2s3_lf_train_signal/B4/models_r2/r2s3_b4_substitution/`
  gained `controls.py` and `readings.py` since the prior close, joining
  `manifest.json`/`paths.py`/`lf_guard.py`/`heads.py` (all within this
  run's window). Training-free (`epochs: 0`, no GPU) substitution-audit
  diagnostic. Its `expected_falsification` section is a fully
  pre-registered outcome table (every comparator number measured, not
  merely predicted, in the brainstormer's pre-flight from B3's shipped
  artifacts) whose rule is "fewer than 2 of {ifc, ch, ac} keep an LF
  advantage over the best achievable LF-free control above their
  certified min_claimable_effect on every draw" — meaning the stream's
  B4-vs-close call now resolves **mechanically** off this 2-of-3
  threshold once the card's arms are scored, rather than requiring a
  fresh subjective brainstormer judgment. Net predicted finding already
  on the card: achievable-gated claimable set `{ch 113x, ac 26.8x,
  ifc 1.41x}` (fk retires); ceiling-gated claimable set `{ch}` only.
- **`r2s2_stacked-B3` builder still in its smoke-fix loop**: card
  unchanged (`drafted`, `build_commit: null`, `job_ids: []`). No new
  `.py` source files in `models_r2/r2s2_zerograd/` since the prior
  close, but a live checkpoint write was caught mid-walk
  (`eval/results/r2s2_zerograd/ckpt_ext__helmholtz_2d_e2_s0/last.pt`,
  mtime essentially real-time at the check) — confirms an active
  contract-smoke run in progress, not a stalled process.
- **Job 66262741 (r2s1_direct-B3, seed 0)**: confirmed via both `squeue`
  and `sacct` — still **PENDING**, Priority-queued, unchanged since the
  prior run's close.
- **Staleness (renewed this run, on both remaining B4-active streams)**:
  `state/r2s3_lf_train_signal/current_batch.txt` and
  `state/r2s4_diag/current_batch.txt` both still read "3" despite both
  streams now having drafted B4 cards; both streams' `current_stage.txt`
  files still read their B3-complete/close-decision text, not yet
  refreshed for the B4 cards' existence. Orchestrator-owned staleness,
  consistent with the pattern flagged in prior walks.
- **Round-level instrument-defect pattern (carried forward, 7
  independent confirmations, no new occurrence this run)**: `r2s1_direct`'s
  post-hoc-blend-stage class (adjudicated non-defective);
  `r2s2_stacked-B2`'s statistic mis-specification; `r2s4_diag-B3`
  turn-2's mis-specified `advantage_reachable`, turn-3's self-corrected
  probe-ordering bug; `r2s3_lf_train_signal-B3`'s resolved knife-edge;
  `r2s4_diag-B3` register-turn's ceiling/contamination/row-count triad
  and its foreign-data `stage_blend_decoder` zero-field catch — worth
  folding into the round-report action item once the round closes.
- **`r2s1_direct-B3`'s `stage_blend_decoder` zero-field item — remains
  ADJUDICATED, defect ruled OUT** (unchanged from 2 walks ago). The
  smoke `stage_blend_decoder` zero-field prediction on
  `ext__helmholtz_2d` is rational selection (per-sample rel-L2 exactly
  1.0, blend `cal_table` shows every base+decoder worse than nRMSE 1.0
  at 2-epoch smoke on helmholtz, same code path healthy on
  ifc_poisson). Standing note preserved for the initial-analyzer at
  full 200-epoch tier. No further action needed.
- **Timing ledger**: unchanged this run — 16 entries, still parseable
  JSON. `r2s1_direct-B3`'s job 66262741 remains PENDING, not COMPLETED —
  no upsert due yet.
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
- Repo hygiene, final re-check: `git status --short` on the round root
  at close shows one delta — `experiment_cards/r2s2_stacked/batch_3/B3.json`
  (M — builder-owned, caught mid-walk, see Flags above; not yet
  committed by the external auto-sync as of this check). Earlier in the
  run an external auto-sync process (commit `a3f28ef`, "round2:
  auto-sync 2026-08-01T19:01:39Z") had already committed the B4-related
  deltas before this run's first check. This maintainer's own writes
  this run: `index.md` (rewritten again to capture the mid-walk catch),
  `state/maintainer_report.md`. No Write call this run touched
  `experiment_cards/`, `tools/`, or any other-agent-owned `state/` file.
  `state/timing_ledger.json` unchanged (no COMPLETED job to upsert yet —
  gitignored regardless).
