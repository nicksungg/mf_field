# MFFP Autoresearch Round 2 — Dashboard (updated 2026-08-01T00:00:43Z)

## Streams

| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r2s1_direct | 23.0636 (best_floor_panel_geomean) | **2** | r2s1_direct-B1 **complete**; r2s1_direct-B2 **analyzing** | **B1: unchanged, still COMPLETE.** **B2: status field caught up this run — `running`→`analyzing`.** Full initial-analyzer result landed (SUCCESS 6/6): **falsification_verdict FALSIFIED** — L1 fired on 2/5 datasets (`sharp__allen_cahn_2d` +6.151 skill = 6.99x mce; `sharp__cahn_hilliard` +1.296 skill = 14.21x mce, both vs the in-job Wiener-calibrated `ref_decoder_big`) and L2 fired (4.7x, every fold resample agrees in sign) — **B1's "capacity buys nothing" claim is OVERTURNED on `sharp__cahn_hilliard`** (decoder advantage grew 0.55→1.30 skill units; no rank sweep rescues it; the band-3 gain is pinned on a grid edge, as B1's reviewer predicted). L3/L4 did not fire (floors beaten everywhere; the selection rule is vindicated on distinguishable cells). `sharp__phase_field_crystal_2d`/`sharp__fisher_kpp_2d` are dead cells (all 21 arms degenerate to `dc_only`, byte-identical). Panel geomean **18.3622** (informational only, no falsification weight per the card). `cratered_verdict`: `proceed_to_seeds_1_2`. Mechanism-analyzer dispatched next (real-capacity characterization on `cahn_hilliard` is the live question) — **turn 1 landed during this walk's final re-sweep** (`reanalysis_progress` `null`→`turn_1`, `6_analysis` still `null` — write-ordering lag): per `orchestrator_flow.md`, the L2 deficit is a **selection-rule ARITY BUG** — the rule preserved cardinality but fitted a contiguous window {0,1,2,3} instead of the true identifiable SET {0,1,12,13} (modes 12-13 hold 43-47% of DC energy; a set-based head reaches cos 0.9948 vs the window's 0.0593, recovering 0.513 skill units = 5.6x mce non-oracle); band-3 pinning = calibration overfit (Wiener stage costs 0.098 on test); basis capacity is NOT the bottleneck (decoder worse than oracle rank-2 — the edge is coefficient accuracy). Turn 2 dispatched, not yet landed | **0 live** (seed-0 job `66189580` terminal since prior run, no new job) | `status` `running`→`analyzing` + mechanism turn 1 landed, both this run |
| r2s2_stacked | 23.0636 (best_floor_panel_geomean) | **2** | r2s2_stacked-B1 **complete**; r2s2_stacked-B2 **analyzing** | **B1: unchanged, still COMPLETE.** **B2: no delta this run** — card content byte-identical to the last check (confirmed via mtime: last write was *before* the prior run's RUN END). Still `status: analyzing`, `reanalysis_progress: turn_1`, `6_analysis: null`. Panel geomean **19.3868** (band met vs launch anchor) from the already-landed initial-analysis; FALSIFIED 3/4 clauses but every F1-firing cell is a `B:all` LOO-artifact cell (excluding them F1→0, only F3 survives on 2); F2 **INVERTED** (k=1 beats k=all). **Note**: `orchestrator_flow.md` narrates further progress not yet reflected on-card — mechanism-analyzer turn 1 content (F1 traced to a **statistic mis-specification**: uncentred cross-spectra vs an affine corrector class; a centred repair flips `B:all` gamma to 0.99-1.00 and F1→0 cells — "the calibration card caught its own instrument's spec error") and a turn-2 dispatch (real closure question = 2 non-`B:all` F3 cells + F2 restatement) — this is the recurring write-ordering lag; **flagged for the next check, not yet scoreable from the card itself** | 0 live SLURM (both legs terminal, unchanged); no visible local process this check | none (card unchanged since last check) |
| r2s3_lf_train_signal | 23.0636 (best_floor_panel_geomean) | **2** | r2s3_lf_train_signal-B1 **complete**; r2s3_lf_train_signal-B2 **analyzing** | **B1: unchanged, still COMPLETE.** **B2: `reanalysis_progress` advanced `turn_2`→`turn_3` this run**, with full findings content landed (mechanism-analyzer turn 3, 6/6): `sharp__cahn_hilliard` three-channel anatomy — **68.3% of the A0→A2 gap is the 15 unseeable affine directions** (a coverage-of-design fact, not a curriculum effect: A3's pooling leaves the design rank BIT-IDENTICAL while the fields still differ by 0.398); LF calibrates amplitude on `cahn_hilliard` but does **not** teach direction; the dimension-control probe shows a "condition-response repair", not a "null-aligned defect". **Part 6 written**, including all 4 postmortem items; **M5** (the round-claimable deliverable): the A0-vs-A1 coverage contrast (`ifc_poisson` +5.97, `cahn_hilliard` +17.44 skill units) — A2 (the null-penalized arm) is reported alongside as the pre-registered mechanism that failed. Register turn dispatched next — **not yet landed**, part 7 still `null`, `status` correctly still `analyzing` | 0 live SLURM (seed-0 job terminal, unchanged); no visible local process this check | `reanalysis_progress` `turn_2`→`turn_3`; full turn-3 findings + part 6 landed |
| r2s4_diag | **19.8178** (certified_3seed_panel_geomean, CI95 [19.385, 20.527]) | **3** | r2s4_diag-B1 **complete**; r2s4_diag-B2 **complete**; r2s4_diag-B3 **drafted** | **B1/B2: unchanged, both still COMPLETE.** **B3: a new card landed during this run** — discovered only during the mandatory pre-return checklist re-verification (git-status-on-cards check), ~4.4 min after this run's start. `status: drafted`, `job_ids: []`, no build/job/review activity yet — the experiment-starter's output, a "teacher-projection channel ledger" diagnostic (out-of-fold condition→teacher-prediction projection of the r2s4-B2 LF-teacher arm, scored in copy-LF skill vs `T0_cond_only`; pre-registered `T0` reproduction expectation: panel geomean 19.3-20.5, within the panel mce 1.141867 of the 19.817845 anchor). Upstream this run (all file-timestamp-confirmed, inside this run's window): B3 websearcher **completed** (6th iteration + `report.md`, PARTIAL-ACCEPTED 7/8 per `orchestrator_flow.md` — sole miss a self-reported 1-iteration cap overrun) → B3 brainstormer **completed** (1/1 slot filled) → experiment-starter dispatched → **card drafted**. Nothing to score yet (pre-build) | **0 live** (all prior seeds terminal, unchanged; B3 not yet built/submitted) | B3 pipeline completed this run: websearcher→brainstormer→starter→**card drafted** (`status: drafted`) |

**Anchor note**: r2s4_diag remains the only stream with a *certified* anchor
(`certified_3seed_panel_geomean`, 19.8178, replacing the training-free floor)
— r2s1_direct, r2s2_stacked, r2s3_lf_train_signal remain on the launch-time
`best_floor_panel_geomean` anchor (23.0636, `certified_utc` 2026-07-31T14:20:17Z,
unchanged). No anchor deltas this run. All anchors rendered verbatim from
`state/anchors/*.json`.

**This run's headline**: two real card-level deltas at the initial pass —
**`r2s1_direct-B2` closed its initial-analysis with a FALSIFIED verdict that
overturns B1's headline "capacity buys nothing" claim on
`sharp__cahn_hilliard`** (decoder advantage grew from 0.55 to 1.30 skill
units, 14.21x the certified noise floor), and **`r2s3_lf_train_signal-B2`
landed its third and final mechanism-analyzer turn** with part 6 written
(M5: the A0-vs-A1 coverage contrast is the round-claimable deliverable),
moving to a register turn. `r2s2_stacked-B2` showed **no delta** at the
initial pass — its card content is unchanged since before the prior run's
close, even though `orchestrator_flow.md` narrates further mechanism-analyzer
progress (the recurring write-ordering-lag pattern, now escalated). **A 9th
card was then discovered during the mandatory pre-return re-verification**:
`r2s4_diag-B3` landed mid-walk (`status: drafted`, drafted by the
experiment-starter after the websearcher and brainstormer both completed
their batch-3 work inside this same run's window) — **cards walked revised
9/9**.

## Running / pending jobs

| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| (none) | — | — | — | — |

**0 live `r2-*` SLURM jobs** at this check (squeue + sacct cross-checked, no
transient-empty false positives — `sacct` shows all 14 `r2-*` jobs COMPLETED,
unchanged from the last check; `squeue` shows 0 `r2-*` entries, only
unrelated interactive `bash` jobs and round-1 `r1-*` PENDING seed-confirm
jobs, out of this maintainer's scope). All work landing this run
(initial-analysis, mechanism-analysis, websearch, brainstorm, card drafting)
was file-based agent activity, not a SLURM job.

## Completed cards

| Card | Type | Panel geomean skill (±CI) | Falsification verdict | Tools promoted |
|---|---|---|---|---|
| r2s4_diag-B1 | diagnostic | 19.8178 IQM, CI95 [19.385, 20.527] (3 seeds) | n/a (diagnostic — no falsification clauses); mechanism register complete, part 7 written | 2 tools, both correctly indexed: `tools/conditional_mean_collapse.py`, `tools/condition_predictability_ceiling.py` |
| r2s4_diag-B2 | diagnostic | 19.8829 own single-run 3-seed geomean (T0 primary arm; reproduces B1's certified band, not a re-certification) | **falsified**: the aux-LF-TARGET head is worth nothing at any N_fit in 20-320 on 15/15 dataset×N cells (7.42-101.12x the certified floor's resolving power); explicitly does NOT license the broader "LF doesn't help" claim (input-side + disjoint-supply channels untouched) | **3 tools**: `tools/ladder_pair_alignment_audit.py`, `tools/shrinkage_curve_anatomy.py`, `tools/condition_predictability_ceiling_fast.py` |
| r2s1_direct-B1 | model | 19.6444 (single seed 0, no CI yet) | **falsified in a split reading**: floors clause CONFIRMED (beats best floor on all 6 panel datasets, geomean −14.8% vs anchor) but the implicit architecture clause FALSIFIED — a ~156-parameter closed-form head reaches 19.0553/19.1666, statistically indistinguishable from the 15.9M-parameter shipped arm (0.52x the certified panel min_claimable_effect) | 2 tools, both correctly indexed: `tools/band_gain_counterfactual.py`, `tools/condition_identifiable_rank.py` |
| r2s3_lf_train_signal-B1 | model | 25.3919 (`rung_native`, single seed 0) | **falsified in a split reading**: F1 (primary, architecture) FALSIFIED with a 7.35-skill-unit sign inversion on `ifc_poisson`, traced to a shared-scaler confound; but the motivating INFORMATION claim is CONFIRMED — an architecture-free estimator recovers +3.2317 skill units from the same 170 disjoint LF rows (18.83% of the law's coefficient energy at cos 0.9993). F2 (native vs upsampled) survived; F3 (degeneracy) verdict depends on provisional vs re-certified floor thresholds (both recorded) | 2 tools, both correctly indexed: `tools/affine_ladder_voi.py`, `tools/posthoc_repair_ladder.py` |
| r2s2_stacked-B1 | model | 14.0756 (single seed 0, no CI yet; scored arm `frozen`; ~all margin from the unpaired `ifc_poisson` column) | clean negative with a measured mechanism, not a raw binary: the falsification clause was a conjunction that did **not** fire — conjunct 1 ("improve on `emul_only` by ≥2.0 skill units") **held** (measured improvement 0.0061, 326x below threshold) but conjunct 2 ("beat the NN-in-condition floor") **failed to hold** (beat it by 11.90 skill units, 130x the noise floor). Round-level headline (I8): a stacked intermediate representation is a re-parameterisation of the condition→HF hypothesis class, not a new information channel | 2 tools, both correctly indexed and register-confirmed: `tools/reachable_set_rank_audit.py`, `tools/surrogate_coherence_eligibility.py` |

`r2s1_direct-B2` (`analyzing`, initial-analysis landed this run — FALSIFIED,
B1's ch capacity claim overturned; mechanism-analyzer dispatched, not yet
landed), `r2s2_stacked-B2` (`analyzing`, unchanged this run — geomean 19.3868,
F1's LOO-artifact question live, mechanism turn 1 content still pending
on-card), `r2s3_lf_train_signal-B2` (`analyzing`, part 6 landed this run —
ch three-channel anatomy, M5 deliverable identified; register turn
dispatched) and `r2s4_diag-B3` (`drafted`, no build/job activity yet) are
all actively open but none has part 7 written (or, for B3, any build yet) —
not listed here until each card itself closes.

## Flags

- **`r2s1_direct-B2` FALSIFIED — overturns a B1 headline claim**: the
  initial-analyzer's verdict on `sharp__cahn_hilliard` directly contradicts
  B1's "a ~156-parameter closed-form head is statistically indistinguishable
  from the 15.9M-parameter shipped decoder" finding — B2's in-job
  Wiener-calibrated decoder now beats the scored closed-form arm by 1.296
  skill units (14.21x the certified `min_claimable_effect`), and the effect
  is stable across all 5 fold resamples. The mechanism-analyzer dispatched
  next is explicitly framed around "real-capacity characterization on ch" —
  worth watching for the round report, since it bears on whether B1's
  falsification stands as a `sharp__cahn_hilliard`-specific artifact or
  needs qualification.
- **Write-ordering lag, `r2s2_stacked-B2` (carried forward, unresolved,
  escalated)**: `orchestrator_flow.md` narrates a completed
  mechanism-analyzer turn-1 content landing (F1 traced to a **statistic
  mis-specification** — uncentred cross-spectra vs an affine corrector
  class; a centred repair flips `B:all` gamma to 0.99-1.00 and F1 fires on
  0 cells; "the calibration card caught its own instrument's spec error")
  and a turn-2 dispatch, but the card's own `6_analysis` field is still
  `null` and `reanalysis_progress` still reads `turn_1` — confirmed via
  mtime that the card has not been touched since *before* the prior
  maintainer run closed. This is the same benign write-ordering-lag class
  flagged repeatedly this round, now conspicuous because it is lagging by
  more than one turn's worth of narrated content — flagged explicitly for
  the orchestrator's attention if it persists past the next check.
- **9th card discovered mid-walk — `r2s4_diag-B3` drafted**: found only
  during this maintainer's mandatory pre-return checklist re-verification
  (the git-status-on-cards check), ~4.4 min after this run's start.
  `experiment_cards/r2s4_diag/batch_3/B3.json`: `status: drafted`,
  `card_type: diagnostic`, `job_ids: []`, no build/review/debug activity —
  pre-build stage. Body matches the brainstormer's slot: an out-of-fold
  condition→teacher-prediction projection of the r2s4-B2 LF-teacher arm's
  own predictions, scored in copy-LF skill against `T0_cond_only`, framed as
  closing the last unmeasured value-of-LF channel per program.md. This
  completes a full websearcher→brainstormer→starter→card-drafted pipeline
  traversal inside a single ~14-minute maintainer window — nothing to score
  yet, watch for the build/job dispatch at the next check.
- **Two card-content deltas at the initial pass** (both confirmed via
  `stat -c %Y` mtime, landing after the prior run's RUN END epoch):
  `r2s1_direct-B2` `running`→`analyzing` (full initial-analysis, FALSIFIED
  verdict) and `r2s3_lf_train_signal-B2` `reanalysis_progress` `turn_2`→
  `turn_3` (full turn-3 content + part 6 written). `r2s2_stacked-B2`
  unchanged (see above). Plus the mid-walk 9th-card discovery above. All
  other cards byte-identical to last check: `r2s1_direct-B1`/
  `r2s2_stacked-B1`/`r2s3_lf_train_signal-B1`/`r2s4_diag-B1`/`r2s4_diag-B2`
  `complete`. `reopen_candidate` is `false` on all 9 cards. No `debug_notes`
  on any card — no failures needing a debugger this run.
- **Timing ledger**: **no upsert this run** — no new terminal `r2-*` SLURM
  states (all 14 jobs in `sacct` were already COMPLETED and ledgered as of
  the prior check; `r2s4_diag-B3` has not built/submitted anything yet).
  Still **14 entries** total, JSON re-validated as parseable (`json.load`
  succeeded).
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
  `orchestrator_flow.md` for events whose `sacct`/mtime evidence places them
  on 2026-07-31. This run's fresh entries continue the same benign pattern —
  not a new distinct class, no scored quantity affected; timestamps in this
  report use filesystem-relative epoch deltas, never the flow log's lexical
  labels.
- **Gates**: G1-r2 PASS, G2-r2 PASS, G3-r2 PASS (all 2026-07-31,
  `state/gates.md`) — round cleared for stream launch. Unchanged this run.
- **Round-1 top-3 seed confirms**: NOT this maintainer's scope (round-1 jobs
  visible in `squeue` as `r1-*`, PENDING) — separate round, separate report.
- No reopen candidates on any of the 9 cards. No `blocked.md` file exists (no
  stream has ever blocked). No abandoned streams — none are possible yet
  (r2s1/r2s2/r2s3 at batch 2 with clean B1 closes; r2s4 at batch 3 with two
  clean closes B1/B2 and B3 just drafted — no skip/block history anywhere).
  `state/streams/` directory still does not exist — consistent with no
  abandonments ever being needed.
- Repo hygiene: `git status --short .` (round root, excluding `worktrees/`)
  shows 1 modified card file (`experiment_cards/r2s3_lf_train_signal/
  batch_2/B2.json`, turn-3 content — the round's auto-sync commit at
  23:44:15Z already captured `r2s1_direct-B2`'s initial-analysis landing)
  plus 1 new untracked card directory (`experiment_cards/r2s4_diag/batch_3/`,
  the newly-drafted B3 card) plus other-agent/orchestrator-owned modified/
  untracked files (`state/orchestrator_flow.md`,
  `state/r2s1_direct/current_stage.txt`, `state/r2s4_diag/current_stage.txt`,
  `brainstormer/r2s4_diag/batch_3/`, `tools/null_family_ceiling_audit.py`)
  — none touched by this maintainer. This maintainer's own writes this run:
  `index.md`, `state/maintainer_report.md` (`state/timing_ledger.json`
  content unchanged, gitignored, not part of the git-status comparison). No
  Write call this run touched `experiment_cards/`.
