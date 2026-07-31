# MFFP Autoresearch Round 2 — Dashboard (updated 2026-07-31T18:33:00Z)

## Streams

| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r2s1_direct | 23.0636 (best_floor_panel_geomean) | 1 | r2s1_direct-B1 | **analyzing** — seed-0 job COMPLETED (66163572, h200, 6.95 min), panel_geomean_skill **19.6444** (vs 23.0636 anchor); mechanism-analysis **turn 3 core write-up landed** (`reanalysis_turn_3_results.md`, ~2 min old at check) with follow-up sub-probes already run (`turn3_followup.py`/`turn3_followup_b.py`, per-dataset amp/phase JSONs for helmholtz/pfc/allen_cahn/fisher_kpp) — no register handoff yet, card `reanalysis_progress` still shows `turn_2` (not yet bumped by the analyzer) | 0 live (job done) | 2026-07-31T18:29:xxZ (turn-3 results write, ~2 min before this check) |
| r2s2_stacked | 23.0636 (best_floor_panel_geomean) | 1 | r2s2_stacked-B1 | **analyzing** — seed-0 panel leg COMPLETED (66166237, h200, 20.13 min, panel_geomean_skill **14.0756** on scored arm `frozen`; guard leg 66166238 completed earlier); mechanism-analyzer turn 1 write-up completed (`reanalysis_turn_1_results.md`), still mid-**turn 2** (`reanalysis_turn_2.py`/`reanalysis_turn_2b.py`, `turn2_runA.log` freshest file, <1 min old at check) | 0 live (jobs done) | 2026-07-31T18:33:xxZ (turn-2 log write, <1 min before this check) |
| r2s3_lf_train_signal | 23.0636 (best_floor_panel_geomean) | 1 | r2s3_lf_train_signal-B1 | **analyzing** — seed-0 job (66165379) COMPLETED (77.05 min total, all 5 legs: hf_only/rung_native/rung_upsampled/guard/baseline_gate); initial-analyzer verdict: **CRATERED + FALSIFIED** (F1 sign-inverted -7.35 skill units on ifc_poisson); mechanism-analyzer turn 1 **confirmed actively running** — live PID in `ps aux` (`python scratchpad/reanalysis_turn_1.py`, started 11:16 local, ~17 min elapsed at check, `timeout 1200`), not stalled | 0 live (job done) | live process, ~17 min into turn-1 script at check |
| r2s4_diag | **19.8178** (certified_3seed_panel_geomean, CI95 [19.385, 20.527]) | 1 | r2s4_diag-B1 | **analyzing** — all 3 seeds COMPLETED (66161480/81/82, h200, ~4.1-4.4 min each); **mechanism-analysis COMPLETE (3 turns + register)**, card `6_analysis` fully populated with findings; `7_gap_and_future` key present but still `null` and 2 newly-promoted tools not yet appended to `tools/index.md` (register turn's own claim not yet reflected on disk — flagged below, unchanged since last run) | 0 live (all done) | 2026-07-31T18:10:56Z (mechanism-analyzer register handoff written; unchanged this run) |

**Anchor note**: r2s4_diag remains the only stream with a *certified* anchor
(`certified_3seed_panel_geomean`, 19.8178, replacing the training-free floor)
— r2s1_direct, r2s2_stacked, r2s3_lf_train_signal remain on the launch-time
`best_floor_panel_geomean` anchor (23.0636, `certified_utc` 2026-07-31T14:20:17Z,
unchanged). No anchor deltas this run. All anchors rendered verbatim from
`state/anchors/*.json`.

**This run's headline event**: no SLURM/card-status changes — all four
batch-1 primary jobs completed in prior runs and no `r2-*` job is live. The
delta this run is purely mechanism-analysis progress: r2s1_direct-B1's turn 3
write-up landed (`reanalysis_turn_3_results.md`), r2s2_stacked-B1 continues
actively in turn 2, and r2s3_lf_train_signal-B1's turn-1 script was directly
confirmed running (live PID) rather than merely file-mtime-fresh. r2s4_diag-B1
is unchanged (register turn already complete as of the prior run).

## Running / pending jobs

| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| (none) | — | — | — | No `r2-*` jobs live in `squeue` (confirmed via `sacct` cross-check — all 7 batch-1 jobs COMPLETED, no vanished-job false positives) |
| 66149132 | (unrelated interactive `bash`) | RUNNING | ~4h33m | hpc-90-18 — not a round-2 job |
| 66162876 | (unrelated interactive `bash`) | RUNNING | ~2h17m | hpc-24-22 — not a round-2 job |
| 66166013 | (unrelated interactive `bash`) | RUNNING | ~1h40m | hpc-89-13 — not a round-2 job |

6 `r1-*` jobs also visible in the queue (5 PENDING, round-1 top-3 seed-confirm
work) — out of this maintainer's scope, noted only for queue-context.

## Completed cards

(none — all 4 batch-1 cards have `7_gap_and_future` still `null`; all 4 now
have populated `5_actual_result` and `6_analysis`, all in active
mechanism-analysis. r2s4_diag is closest to card-complete: 3 mechanism turns
+ register done, only part 7's write-up and the tools/index.md append
outstanding.)

| Card | Type | Panel geomean skill (±CI) | Falsification verdict | Tools promoted |
|---|---|---|---|---|
| r2s1_direct-B1 | model | 19.6444 (single seed 0, no CI yet) | pending mechanism-analyzer register | pending |
| r2s2_stacked-B1 | model | 14.0756 (single seed 0, no CI yet; scored arm `frozen`; ~all margin is the unpaired ifc_poisson column) | pending mechanism-analyzer register | pending |
| r2s3_lf_train_signal-B1 | model | 25.3919 (`rung_native`, single seed 0) | **falsified** (F1 sign-inverted; F2 survives vs diverged comparator; F3 threshold-dependent, see prior-run detail below) | pending |
| r2s4_diag-B1 | diagnostic | 19.8178 IQM, CI95 [19.385, 20.527] (3 seeds) | n/a (diagnostic — no falsification clauses); mechanism register complete | 2 new tools written to disk (`tools/conditional_mean_collapse.py`, `tools/condition_predictability_ceiling.py`) but **not yet indexed** in `tools/index.md` |

## Flags

- **No card-status or SLURM deltas this run** — all four batch-1 primary jobs
  landed in prior runs (7/7 entries in `state/timing_ledger.json`, unchanged);
  0 live `r2-*` jobs (squeue empty, sacct cross-checked, no vanished-job false
  positives). This is the second consecutive maintainer check with zero live
  round-2 SLURM jobs — all remaining batch-1 work is local mechanism-analysis
  scripting.
- **Mechanism-analysis progressing on all 3 non-r2s4 streams**, all
  liveness-confirmed (none stalled):
  - r2s1_direct-B1: turn 3 write-up landed (`reanalysis_turn_3_results.md`,
    ~2 min old at check) — key findings I3 (the metric's unidentifiable
    subspace rewards predicting less; centering/shrinkage/blend are
    calibration, not architecture) and I4 (pfc's capacity "gain" is a Jensen-gap
    artifact, reverses under mean-of-energy). Card's `reanalysis_progress`
    field still reads `turn_2` — a one-turn lag behind the filesystem, not yet
    bumped by the analyzer; noted, not treated as an anomaly (turns are
    written before the card field updates).
  - r2s2_stacked-B1: turn 1 write-up complete, actively mid-turn-2 (freshest
    file `turn2_runA.log`, <1 min old at check).
  - r2s3_lf_train_signal-B1: turn 1 **directly confirmed live via `ps aux`**
    (PID running `python scratchpad/reanalysis_turn_1.py` under a 1200s
    `timeout`, ~17 min elapsed) — stronger liveness evidence than file-mtime
    alone this check.
- **r2s4_diag-B1 mechanism-analysis register-turn inconsistency (unchanged,
  carried forward)**: the handoff note
  (`notes/handoff_experiment_mechanism_analyzer.md`) claims "card parts 6 and
  7 written" and "recorded in tools/index.md", but on disk `7_gap_and_future`
  is still `null` and neither `conditional_mean_collapse.py` nor
  `condition_predictability_ceiling.py` appears in `tools/index.md` yet (both
  `.py` files do exist under `tools/`). Not adjudicated here — flagged for
  the orchestrator/next agent to reconcile; no card or tools/index.md write
  made by this maintainer.
- **Timestamp anomalies (both unchanged, carried forward)**: (1)
  r2s1_direct-B1's `review_notes[0].utc` still reads `2026-07-31T17:05:00Z`
  (ahead-of-clock relative to the review file's actual write time). (2)
  r2s4_diag-B1's mechanism-analyzer handoff header still self-declares
  `2026-07-31T18:40Z` vs its actual `stat -c %Y` mtime `2026-07-31T18:10:56Z`
  (~29 min ahead). Two independent instances across two subagent types
  (code-reviewer, mechanism-analyzer) — worth escalating as systemic. No
  scored quantity affected in either case.
- **Timing ledger**: no new upsert this run (all 7 entries from prior runs
  remain valid and match current `sacct` output exactly; re-validated as
  parseable JSON, no changes needed).
- **Analyzer caveat carried forward (r2s1_direct-B1, from code-review)**: the
  D3 certificate's aleatoric-floor estimate is window-sensitive — at the
  recipe's window (1000 closest pairs), `ext__helmholtz_2d` reads 1.200,
  worse than the zero predictor, despite the card's gate stamping
  `verdict: supported, trustworthy: true` (gate tests `d_min`, not window
  width). Must not be reported as a ceiling for helmholtz; `allen_cahn`'s
  ceiling must be reported as a range (0.315-0.471); `pfc`/`fisher_kpp` are
  window-robust and quotable. (r2s4_diag-B1's own mechanism register
  independently confirms `min_pair_distance` 2.822 / `no_support` on
  cahn_hilliard, corroborating this family of caveats.)
- **Analyzer caveat (r2s2_stacked-B1, from code-review + initial-analyzer)**,
  carried forward: ifc_poisson's rung ladder is UNPAIRED (independent
  condition draws per rung, min distance 0.08-0.30, never 0) — matches
  r2s3's independent finding, a cross-stream benchmark-integrity item for the
  round report. A2/A5 arms there are `arm_semantics_degraded=True`; A2-A3 is
  an upper bound on shift, not epoch-matched. Do not quote the "A2-A3
  identically zero" code string (measured 0.00883).
- **Analyzer caveat (r2s3_lf_train_signal-B1, from code-review)**, carried
  forward: the shared-max-abs-rungs scaler makes ifc_poisson's `rung_native`
  stage-1 loss ~42x amplitude-weighted toward rung 8 over HF — a card-locked
  design choice, not a build defect (confound C1). F1 is epoch-matched but
  not step-matched (`rung_native` gets ~14x more optimizer steps per epoch
  than `hf_only` on ifc_poisson at batch 16 — confound C2, and per the
  card's own `cratered_detail`, C2 "ran IN FAVOR of the losing arm", i.e. the
  inversion is not explained away by this confound). Both confounds are
  recorded as attaching to the deciding F1 measurement.
- **Gates**: G1-r2 PASS, G2-r2 PASS, G3-r2 PASS (all 2026-07-31,
  `state/gates.md`) — round cleared for stream launch. Unchanged this run.
- **Round-1 top-3 seed confirms**: NOT this maintainer's scope (round-1 jobs
  visible in `squeue` as `r1-*`, PENDING) — separate round, separate report.
- No reopen candidates, no `blocked.md` entries, no abandoned streams — none
  are possible yet (all streams at batch 1, no skip/block history).
- Repo hygiene: `git status --short` on `mffp_autoresearch/round2/experiment_cards/`
  is **clean** this run (confirmed no Write call this run touched
  `experiment_cards/`). `index.md`, `state/maintainer_report.md`, and
  `state/orchestrator_flow.md` show as modified in the broader `round2/`
  status — the first two are this maintainer's own writes; the third is
  outside this maintainer's write scope (orchestrator-owned).
