# MFFP Autoresearch Round 2 — Dashboard (updated 2026-08-02T05:41:00Z)

**Twenty-fifth maintainer walk since the operator halt/resume cycle —
fifth walk of the resumed session, and the first FULL walk since the
stall throttle lifted.**
Halt landed 2026-08-01T01:31:54Z (commit `10d4e4c`), first resume landed
2026-08-01 ~08:1x PDT (commit `b80e622`). A second session restart
happened ~2026-08-01T20:45 PDT (crons re-created: orchestrator pulse
`aa4dcb66`, maintainer `2c7fed88`, auto-sync `a45bd18b`; commit
`818faef8`). Walks 21-24 were light/no-delta walks under a queue-stall
throttle (last pair: `RUN START 2026-08-02T05:14:26Z` /
`RUN END 2026-08-02T05:20:00Z`, zero deltas). **The queue unstuck during
the walk-24→25 gap — this walk records real deltas for the first time
since walk 15, and the stall throttle is lifted; full 20-minute cadence
resumes.**

## Real deltas this walk (see `state/maintainer_report.md` RUN block for full detail)

- **`r2s1_direct-B3` seed-0 job `66262741` transitioned PENDING → RUNNING → FAILED**
  (exit `1:0`, ran 2026-08-01T22:11:52 → 22:25:13 PDT, elapsed **13:21**).
  Card `r2s1_direct-B3` status is still `running` in the card file (parts
  5/7 both empty) — an **experiment-debugger, attempt 1, has been dispatched
  by the orchestrator and is in flight** (per task brief; no fix commit yet
  visible in the `r2s1_direct/B3` worktree git log, tip still `2b030f0`).
  **Flagged for the orchestrator**, not actioned by this read-only walk.
- **`r2s2_stacked-B3` guard job `66267441` COMPLETED** (0 exit, ran
  2026-08-01T22:25:38 → 22:26:47 PDT, elapsed **1:09**) — contract-tier
  (2-epoch) guard leg on heat_local/fluid/sharp__sod_1d, family
  `r2s2_zerograd`. **Timing ledger upserted this walk** (job id
  `66267441`, `nvidia_h200`). The panel leg (job `66267438`, 200ep,
  panel datasets) is still **RUNNING** (~29.5 min elapsed at this walk's
  check, started 22:11:52 PDT). Card status unchanged (`running`, parts
  5/7 empty).
- **`r2s4_diag-B4` seed-0 job `66269660` COMPLETED** (0 exit, ran
  2026-08-01T22:27:16 → 22:33:14 PDT, elapsed **5:58**) — from-scratch
  FiLM-FNO family `models_r2/r2s4_b4_anatomy`, ifc_poisson panel, 200
  epochs, exhaustive 31-subset HF-count ladder. **Timing ledger upserted
  this walk** (job id `66269660`, `nvidia_h200`). Card status still
  `running` in the card file (parts 5/7 empty) — no downstream
  analysis stage has landed yet as of this walk.
- **Timing ledger**: 17 → **19 entries** after this walk's two upserts
  (both new jobs cross-confirmed against `sacct -j <id> --format=...,AllocTRES`
  as `nvidia_h200`). Re-validated as parseable JSON after the write.
- **squeue now shows only 1 live `r2-*` job** (`66267438`,
  `r2s2_stacked-B3-s0`, RUNNING on `hpc-sm-02-17`) — down from 4
  PENDING at walk 24. `66262741` (FAILED) and `66267441`/`66269660`
  (COMPLETED) have all left the queue.
- No abandonment trip (`STREAM_ABANDON_CAP`=3 not reached anywhere), no
  anchor deltas (all 4 `state/anchors/*.json` byte-identical, mtimes
  predate this run), no gate changes (G1-r2/G2-r2/G3-r2 all still PASS
  2026-07-31), no transcripts to file (`state/transcripts/inbox/` still
  does not exist).

## Streams

| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r2s1_direct | 23.0636 (best_floor_panel_geomean) | 3 | r2s1_direct-B1 **complete**; r2s1_direct-B2 **complete**; r2s1_direct-B3 **running** (parts 5/7 empty) | Seed-0 job **66262741 FAILED** (exit 1:0, 13:21 elapsed, ended 2026-08-01T22:25:13 PDT) — no longer in `squeue`. Experiment-debugger attempt 1 dispatched, in flight (orchestrator-owned) | **0 live SLURM**; 1 FAILED job awaiting debugger fix + relaunch | **Job FAILED this walk (was PENDING at walk 24)** |
| r2s2_stacked | 23.0636 (best_floor_panel_geomean) | 3 | r2s2_stacked-B1 **complete**; r2s2_stacked-B2 **complete**; r2s2_stacked-B3 **running** (parts 5/7 empty) | Guard job **66267441 COMPLETED** (1:09, ledger upserted). Panel job **66267438 RUNNING** on `hpc-sm-02-17` (~29.5 min elapsed of a 2:30:00 budget). Job-name-collision watch item (reviewer finding R1) now live — guard renamed itself to the panel's job name mid-run; matched by job ID throughout | **1 live SLURM** (`r2-r2s2_stacked-B3-s0`, 66267438, RUNNING) | **Guard job COMPLETED this walk (was PENDING at walk 24)** |
| r2s3_lf_train_signal | 23.0636 (best_floor_panel_geomean) | 4 | r2s3_lf_train_signal-B1..B4 **all complete** | **CLOSED (registered close, walk 15)**, unchanged this walk. Not an abandonment — `STREAM_ABANDON_CAP` never applied | **0 live SLURM** | No change since walk 15's close |
| r2s4_diag | **19.8178** (certified_3seed_panel_geomean, CI95 [19.385, 20.527]) | 4 | r2s4_diag-B1..B3 **complete**; r2s4_diag-B4 **running** (parts 5/7 empty) | Seed-0 job **66269660 COMPLETED** (5:58, ledger upserted, ended 2026-08-01T22:33:14 PDT) — no longer in `squeue`. Awaiting downstream analysis-stage dispatch (not yet visible in card) | **0 live SLURM**; 1 COMPLETED job awaiting next stage | **Job COMPLETED this walk (was PENDING at walk 24)** |

**Anchor note**: r2s4_diag remains the only stream with a *certified*
anchor (`certified_3seed_panel_geomean`, 19.8178) — r2s1_direct,
r2s2_stacked, and the closed r2s3_lf_train_signal remain on the
launch-time `best_floor_panel_geomean` anchor (23.0636, `certified_utc`
2026-07-31T14:20:17Z, unchanged). No anchor deltas this run — all 4
`state/anchors/*.json` files' mtimes predate this run's entire window,
content re-read and confirmed byte-identical to all prior runs. All
anchors rendered verbatim from `state/anchors/*.json`.

## Running / pending jobs

| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| 66267438 | r2s2_stacked-B3 (seed 0, panel) | RUNNING | ~29:32 (started 2026-08-01T22:11:52 PDT) | hpc-sm-02-17 |

**Only 1 live/pending `r2-*` SLURM job** — down from 4 PENDING at walk
24. The other 3 tracked jobs all resolved during the walk-24→25 gap:

| Job | Card | Final state | Elapsed | Ended (PDT) |
|---|---|---|---|---|
| 66262741 | r2s1_direct-B3 (seed 0) | **FAILED** (exit 1:0) | 13:21 | 2026-08-01T22:25:13 |
| 66267441 | r2s2_stacked-B3 (seed 0, guard) | **COMPLETED** | 1:09 | 2026-08-01T22:26:47 |
| 66269660 | r2s4_diag-B4 (seed 0) | **COMPLETED** | 5:58 | 2026-08-01T22:33:14 |

`sacct`'s 2-day window otherwise shows the same 17 pre-existing `r2-*`
jobs, all COMPLETED 0:0 (including 66268786,
`r2s3_lf_train_signal-B4-s0`, already in the timing ledger). All 4
jobs' finish states cross-confirmed by both `squeue` (jobs absent
except 66267438) and `sacct` (explicit per-job query with
`AllocTRES`/`Start`/`End`).

## Completed cards

*(unchanged this walk — no card transitioned to `complete`; the two
newly-COMPLETED/FAILED SLURM jobs above have not yet propagated into
their cards' parts 5/7, which remain empty on all three open-stream B3/B4
cards.)*

| Card | Type | Panel geomean skill (±CI) | Falsification verdict | Tools promoted |
|---|---|---|---|---|
| r2s4_diag-B1 | diagnostic | 19.8178 IQM, CI95 [19.385, 20.527] (3 seeds) | n/a (diagnostic); mechanism register complete, part 7 written | `tools/conditional_mean_collapse.py`, `tools/condition_predictability_ceiling.py` |
| r2s4_diag-B2 | diagnostic | 19.8829 own single-run 3-seed geomean (T0 primary arm) | **falsified**: aux-LF-TARGET head worth nothing at any N_fit 20-320 on 15/15 dataset×N cells | `tools/ladder_pair_alignment_audit.py`, `tools/shrinkage_curve_anatomy.py`, `tools/condition_predictability_ceiling_fast.py` |
| r2s1_direct-B1 | model | 19.6444 (single seed 0) | **falsified in a split reading**: floors clause CONFIRMED, architecture clause FALSIFIED (156-param closed-form head statistically indistinguishable from the 15.9M-param shipped arm) | `tools/band_gain_counterfactual.py`, `tools/condition_identifiable_rank.py` |
| r2s3_lf_train_signal-B1 | model | 25.3919 (`rung_native`, single seed 0) | **falsified in a split reading**: F1 FALSIFIED (shared-scaler confound); information claim CONFIRMED | `tools/affine_ladder_voi.py`, `tools/posthoc_repair_ladder.py` |
| r2s2_stacked-B1 | model | 14.0756 (single seed 0) | clean negative, conjunctive clause did not fire (conjunct 1 held, conjunct 2 failed) | `tools/reachable_set_rank_audit.py`, `tools/surrogate_coherence_eligibility.py` |
| r2s3_lf_train_signal-B2 | model | not computed (3-of-6 panel, informational) | **confirmed**; `cratered_verdict: proceed_to_seeds_1_2`; 1 guard flag | `tools/design_coverage_audit.py`, `tools/null_family_ceiling_audit.py` |
| r2s1_direct-B2 | model | 18.3622 (single seed 0, no falsification weight) | **falsified**: L1/L2 fire, L3/L4 do not | `tools/blend_decorrelation_payoff.py`, `tools/selection_set_vs_window_audit.py` |
| r2s2_stacked-B2 | diagnostic | 19.386837 (single seed 0) | **falsified**: F1/F2/F3 fire, F4 does not; retracts B1's `surrogate_coherence_eligibility.py` rule as a GATE | `tools/zero_gradient_stage_ladder.py`, `tools/relative_gain_units_audit.py` |
| r2s3_lf_train_signal-B3 | model | 17.114970 (`A1_lf_cov`, single seed 0) | **falsified** (knife-edge, 5/7 readings); success-criterion-1 met on exactly 3 datasets; `cratered_verdict: cratered` | `tools/effect_threshold_readings.py`, `tools/map_dispersion_scale_shape.py` |
| r2s4_diag-B3 | diagnostic | 19.172826 (single seed 0) | **falsified** (F3 hardened, F4a fires on corrected definition, F1 partial survival) | `tools/ledger_contamination_audit.py`, `tools/band_retention_probe.py` |
| r2s3_lf_train_signal-B4 | diagnostic (mechanism/register) | n/a — reuses B3's skills; graded criterion-1 legacy ch=A/ifc=B/ac=C | S1 **CONFIRMED false**; part 7: **formal stream close**, no B5 | `tools/gain_head_feasibility_audit.py`, `tools/effect_concentration_audit.py` |

`r2s1_direct-B3`, `r2s2_stacked-B3`, and `r2s4_diag-B4` all have
COMPLETED/FAILED SLURM jobs as of this walk but remain `running` at the
card level (parts 5/7 empty) — not listed here until they close.

## Flags

- **STOP-THE-LINE watch item (not a bug, informational)**: `r2s1_direct-B3`
  seed-0 job **FAILED** this walk (exit 1:0, 13:21 elapsed). Per task
  brief, an experiment-debugger (attempt 1) is already dispatched by the
  orchestrator and in flight — this maintainer confirmed no fix commit
  has yet landed in the `worktrees/r2s1_direct/B3` git log (tip
  `2b030f0`, unchanged). This is the round's first job-level FAILURE
  since launch; flagged for the orchestrator to track through the
  debugger's resolution, not actioned here (read-only for cards).
- **Timing ledger upserted this walk**: 2 new COMPLETED-job entries
  added (17 → 19 total) — `66267441` (r2s2_stacked-B3 guard, 1.15 min,
  `nvidia_h200`) and `66269660` (r2s4_diag-B4 panel, 5.97 min,
  `nvidia_h200`). Both cross-confirmed via `sacct -j <id>
  --format=...,AllocTRES` before writing. JSON re-validated parseable
  after the write.
- **`r2s2_stacked-B3` job-name-collision watch item, now MANIFESTED**:
  guard job 66267441 renamed itself to the panel job's name
  (`r2-r2s2_stacked-B3-s0`) mid-run per reviewer finding R1 (unfixed,
  tracked-by-job-ID workaround) — confirmed in the card's own
  orchestrator note. Both this walk's ledger entries and all queue
  checks matched by explicit job ID, never by name, per that finding.
- **Queue unstuck this walk**: all 4 previously-PENDING jobs resolved
  during the walk-24→25 gap (1 FAILED, 2 COMPLETED, 1 transitioned to
  RUNNING). Stall throttle lifted; full 20-minute cadence resumes from
  this walk onward.
- **`r2s3_lf_train_signal` stream CLOSED (walk 15, unchanged)** — a
  legitimate registered trigger-non-fire close, NOT an abandonment.
  `STREAM_ABANDON_CAP` (=3) never applied. `state/streams/` correctly
  remains nonexistent.
- **Round-level instrument-defect pattern (carried forward, 7 independent
  confirmations, unchanged this run)**: see prior walks'
  `state/maintainer_report.md` entries for full detail — worth folding
  into the round-report action item once the round closes.
- **`r2s1_direct-B3`'s `stage_blend_decoder` zero-field item — remains
  ADJUDICATED, defect ruled OUT** (unchanged from several walks ago). No
  further action needed.
- **Analyzer caveat (r2s1_direct-B1, from code-review)**, carried
  forward: D3 certificate's aleatoric-floor estimate is window-sensitive
  — `ext__helmholtz_2d` reads 1.200 at the recipe window, worse than
  the zero predictor; must not be reported as a ceiling.
- **Analyzer caveat (r2s2_stacked-B1, from code-review + register turn)**,
  preserved for the round report: `ifc_poisson`'s rung ladder is UNPAIRED
  — confirmed independently by r2s3 and r2s4-B2 (cross-stream
  benchmark-integrity item).
- **Analyzer caveat (r2s3_lf_train_signal-B1, from code-review)**,
  carried forward: shared-max-abs-rungs scaler confound (C1, card-locked
  design) and epoch-vs-step mismatch (C2); r2s3-B2 shipped the repair.
- **Analyzer caveat (r2s2_stacked-B3, from code-review, carried
  forward)**: pfc's pre-flight-instrument conflict directionally biases
  F1/F2/F3 toward confirming the card's hypothesis — re-check any "≥2 of
  4 decidable" verdict with pfc dropped once part 6/7 land (now
  imminent given the guard leg's completion).
- **Analyzer caveat (r2s3_lf_train_signal-B4, superseded walk 15,
  unchanged)**: folded into the completed part 6/7 register.
- **Gates**: G1-r2 PASS, G2-r2 PASS, G3-r2 PASS (all 2026-07-31,
  `state/gates.md`) — round cleared for stream launch. Re-read and
  confirmed unchanged this run.
- No reopen candidates on any of the 14 cards. No `blocked.md` file
  exists. **No abandoned streams** — none qualify. `state/streams/`
  directory still does not exist.
- Repo hygiene, final check: `git status --short experiment_cards/` on
  the round root at this run's open/close is fully clean — no card
  files modified by this walk. Only `index.md`, `state/maintainer_report.md`,
  and `state/timing_ledger.json` written this run.
