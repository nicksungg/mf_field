# MFFP Autoresearch Round 2 — Dashboard (updated 2026-07-31T19:38:05Z)

## Streams

| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r2s1_direct | 23.0636 (best_floor_panel_geomean) | **2** | r2s1_direct-B1 **complete**; B2 in progress | **B1: unchanged, still COMPLETE.** **B2 progressed a full stage**: websearch finished (5 iterations + `report.md`, all written 19:09-19:25Z) -> **brainstormer now dispatched**, `summary_so_far.md` written moments before this check. `current_stage.txt` = "brainstormer (B2 dispatched 2026-07-31; E1=Wiener named, E3 protocol shape, ch 6x-mce question)" | 0 live (job done) | brainstormer `summary_so_far.md` written just before this check |
| r2s2_stacked | 23.0636 (best_floor_panel_geomean) | 1 | r2s2_stacked-B1 | **analyzing** — seed-0 panel leg COMPLETED (66166237, h200, 20.13 min, panel_geomean_skill **14.0756** on scored arm `frozen`; guard leg 66166238 completed earlier); mechanism-analysis remains in **turn 3**, actively producing files (`turn3_runA/B/C.log`, `turn3_corrector_B.json`, freshest file ~1 min old at check) — file freshness confirms not stalled; `6_analysis`/`7_gap_and_future` still null as expected mid-turn | 0 live (jobs done) | `turn3_runA.log` ~1 min old at check |
| r2s3_lf_train_signal | 23.0636 (best_floor_panel_geomean) | 1 | r2s3_lf_train_signal-B1 **complete** | **B1: COMPLETE (headline, caught mid-walk during this run's pre-return checklist).** Status `analyzing` -> `complete` at card mtime 2026-07-31T19:36:02Z. `reanalysis_progress: turn_3` -> `registered`; `7_gap_and_future` populated: open question is whether a FiLM-FNO network carrying the per-rung scaler + HF-Nyquist mode-clipping trio can recover the linear probe's 0.2427 skill on ifc_poisson, or whether the affine/linear channel IS the correct B2 family (card bounds both sides, decides neither); `next_direction` recommends shipping the linear/affine LF channel as a contract-compliant B2 family family (0.2427 skill from LF rungs + 5 HF rows, zero test info, vs round-1 round-best 0.6087 and this card's shipped 16.7963). Verdict unchanged: **CRATERED + FALSIFIED** (F1 sign-inverted -7.35 skill units on ifc_poisson). 2 tools promoted, both now correctly indexed in `tools/index.md`: `affine_ladder_voi.py`, `posthoc_repair_ladder.py` (the transient un-indexed state flagged earlier in this same run resolved before return). `current_stage.txt`/`current_batch.txt` not yet caught up to the completion (still read the pre-register-turn state / batch 1) — expected orchestrator-side lag | 0 live (job done) | card completion 2026-07-31T19:36:02Z |
| r2s4_diag | **19.8178** (certified_3seed_panel_geomean, CI95 [19.385, 20.527]) | **2** | r2s4_diag-B1 **complete**; B2 drafted, builder actively producing family code | **B1: unchanged, still COMPLETE.** **B2 progressed**: builder stage (dispatched last run with only a bare worktree branch) is now **actively producing family code** — `models_r2/r2s4_b2_lfvalue/{model.py, lf_reference.py, manifest.json, INSPIRATION.md, smoke_eval.py}` all written within the last several min, plus a debug checkpoint (`scratchpad/dbg_ckpt_ifc/last.pt`, `dbg_ifc.json`) from what looks like a contract-tier smoke self-test. Card itself unchanged on disk (`status: drafted`, `job_ids: []`, `build_commit: null`) — no SLURM submission yet, consistent with an in-progress build | 0 live (no B2 jobs submitted yet) | `models_r2/r2s4_b2_lfvalue/smoke_eval.py` written a few min before this check |

**Anchor note**: r2s4_diag remains the only stream with a *certified* anchor
(`certified_3seed_panel_geomean`, 19.8178, replacing the training-free floor)
— r2s1_direct, r2s2_stacked, r2s3_lf_train_signal remain on the launch-time
`best_floor_panel_geomean` anchor (23.0636, `certified_utc` 2026-07-31T14:20:17Z,
unchanged). No anchor deltas this run. All anchors rendered verbatim from
`state/anchors/*.json`.

**This run's headline**: **r2s3_lf_train_signal-B1 is the round's THIRD
complete card**, caught landing mid-walk during this run's pre-return
checklist verification (card mtime 2026-07-31T19:36:02Z, inside this run's
window). Its register turn closed with an unresolved architecture-vs-
information open question (does the network recover what the closed-form
linear/affine LF channel already achieves on ifc_poisson?) and a concrete
B2 recommendation (ship the affine channel as its own family). Both
register-turn tools (`affine_ladder_voi.py`, `posthoc_repair_ladder.py`)
are correctly indexed. Otherwise no card `status` changed this run: r2s1_direct's
B2 finished websearch and moved into brainstormer; r2s4_diag's B2 builder
went from a bare worktree branch to actively-written family code
(`models_r2/r2s4_b2_lfvalue/`); r2s2_stacked's turn 3 continues (file-freshness
confirmed). Zero live `r2-*` SLURM jobs — fifth consecutive check with none
live; all activity this run is local scripting/builder work.

## Running / pending jobs

| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| (none) | — | — | — | No `r2-*` jobs live in `squeue` (confirmed via `sacct` cross-check — all 7 batch-1 jobs COMPLETED, no vanished-job false positives; no B2 jobs submitted yet for r2s4_diag or r2s1_direct) |

Unrelated interactive `bash` jobs and round-1 `r1-*` jobs also visible in the
queue — out of this maintainer's scope, not itemized here.

## Completed cards

| Card | Type | Panel geomean skill (±CI) | Falsification verdict | Tools promoted |
|---|---|---|---|---|
| r2s4_diag-B1 | diagnostic | 19.8178 IQM, CI95 [19.385, 20.527] (3 seeds) | n/a (diagnostic — no falsification clauses); mechanism register complete, part 7 written | 2 tools, both correctly indexed: `tools/conditional_mean_collapse.py`, `tools/condition_predictability_ceiling.py` |
| r2s1_direct-B1 | model | 19.6444 (single seed 0, no CI yet) | register-turn recalibration measurement narrows (but does not eliminate) the decoder-capacity claim on `sharp__cahn_hilliard` (4.29% / 6.0x MCE, flagged as open, not adjudicated) | 2 tools, both correctly indexed: `tools/band_gain_counterfactual.py`, `tools/condition_identifiable_rank.py` |
| r2s3_lf_train_signal-B1 | model | 25.3919 (`rung_native`, single seed 0) | **falsified** (F1 sign-inverted -7.35 skill units on ifc_poisson; F2 survives vs a diverged comparator; F3 threshold-provenance split, both readings recorded on the card). `7_gap_and_future`: open question is architecture-vs-information (network vs the closed-form linear/affine LF channel on ifc_poisson); `next_direction` recommends shipping the affine channel as its own B2 family | 2 tools, both now correctly indexed: `tools/affine_ladder_voi.py`, `tools/posthoc_repair_ladder.py` |

**In progress (not yet `complete`, all have `5_actual_result` populated;
`6_analysis`/`7_gap_and_future` status noted per card):**

| Card | Type | Panel geomean skill (±CI) | Falsification verdict | Tools promoted |
|---|---|---|---|---|
| r2s2_stacked-B1 | model | 14.0756 (single seed 0, no CI yet; scored arm `frozen`; ~all margin is the unpaired ifc_poisson column) | `confirmed` (initial-analyzer verdict; mechanism register turn 3 continuing, `6_analysis`/`7_gap_and_future` still null) | pending (turn 3 in progress, not yet register) |

## Flags

- **HEADLINE: r2s3_lf_train_signal-B1 is the round's third fully COMPLETE
  card**, caught landing mid-walk during this run's own pre-return checklist
  (card mtime 2026-07-31T19:36:02Z — after the main body of this run's walk
  was already drafted, but still inside the RUN START/END window). This
  maintainer updated both `index.md` and this delta report in place to
  reflect current disk truth rather than the earlier snapshot. `7_gap_and_future`
  poses an unresolved architecture-vs-information question on ifc_poisson
  (does the FiLM-FNO decoder recover what a closed-form affine LF channel
  already achieves, skill 0.2427 with zero test information?) and
  `next_direction` recommends a concrete B2: ship the linear/affine LF
  channel as its own contract-compliant family. Both register-turn tools
  (`affine_ladder_voi.py`, `posthoc_repair_ladder.py`) are correctly indexed
  in `tools/index.md` — the transient un-indexed state flagged earlier in
  this same run's walk has resolved before return. `state/r2s3_lf_train_signal/
  current_stage.txt` and `current_batch.txt` have not yet caught up to the
  completion (still read the pre-register mechanism-analysis stage / batch 1)
  — expected orchestrator-side lag, not an anomaly, worth confirming next
  run.
- **r2s1_direct B2 advanced a full stage**: websearch complete (5 iterations
  + `report.md`, all written 19:09-19:25Z) -> brainstormer dispatched,
  `summary_so_far.md` written moments before this check — confirmed live.
- **r2s4_diag B2 builder now actively writing family code**: from a bare
  worktree branch (last run) to `models_r2/r2s4_b2_lfvalue/{model.py,
  lf_reference.py, manifest.json, INSPIRATION.md, smoke_eval.py}` plus a
  debug checkpoint, all within the last several min — confirmed live, no
  SLURM submission yet (card still `status: drafted`, `job_ids: []`).
- **r2s2_stacked-B1 turn 3 continues**: freshest file (`turn3_runA.log`)
  ~1 min old at check; file-freshness confirms activity is ongoing, not
  stalled.
- **Timestamp anomaly (r2s1_direct-B1, unchanged, carried forward)**:
  `review_notes[0].utc` still reads `2026-07-31T17:05:00Z` (ahead-of-clock
  relative to the review file's actual write time, first flagged several
  runs ago). No scored quantity affected. Remains the card's only
  unresolved caveat since it closed `complete`.
- **Timing ledger**: no new upsert this run (all 7 entries from prior runs
  remain valid and match current `sacct` output exactly; re-validated as
  parseable JSON, no changes needed). Zero live `r2-*` jobs — fifth
  consecutive check with none live.
- **Analyzer caveat carried forward (r2s1_direct-B1, from code-review)**: the
  D3 certificate's aleatoric-floor estimate is window-sensitive — at the
  recipe's window (1000 closest pairs), `ext__helmholtz_2d` reads 1.200,
  worse than the zero predictor. Must not be reported as a ceiling for
  helmholtz; `allen_cahn`'s ceiling must be reported as a range
  (0.315-0.471); `pfc`/`fisher_kpp` are window-robust and quotable.
- **Analyzer caveat (r2s2_stacked-B1, from code-review + initial-analyzer)**,
  carried forward: ifc_poisson's rung ladder is UNPAIRED (independent
  condition draws per rung, min distance 0.08-0.30, never 0) — matches
  r2s3's independent finding, a cross-stream benchmark-integrity item for the
  round report. A2/A5 arms there are `arm_semantics_degraded=True`.
- **Analyzer caveat (r2s3_lf_train_signal-B1, from code-review)**, carried
  forward (now that the card is closed): the shared-max-abs-rungs scaler
  makes ifc_poisson's `rung_native` stage-1 loss ~42x amplitude-weighted
  toward rung 8 over HF (confound C1, card-locked design, not a build
  defect); F1 is epoch-matched but not step-matched (confound C2, "ran IN
  FAVOR of the losing arm" per the card's own `cratered_detail` — does not
  explain away the inversion). Cross-stream note: r2s3's HF-side affine LOO
  residual (3.2e-08 at every rung incl. the 128 test rows) independently
  confirms r2s2_stacked-B1's earlier LF-side finding (ridge(cond) held-out
  nRMSE 0.0000 on the ifc_poisson LF field) — the ifc_poisson degeneracy is
  now cross-confirmed by two independent streams/estimators.
- **Gates**: G1-r2 PASS, G2-r2 PASS, G3-r2 PASS (all 2026-07-31,
  `state/gates.md`) — round cleared for stream launch. Unchanged this run.
- **Round-1 top-3 seed confirms**: NOT this maintainer's scope (round-1 jobs
  visible in `squeue` as `r1-*`, PENDING) — separate round, separate report.
- No reopen candidates on any of the 5 cards. No `blocked.md` file exists (no
  stream has ever blocked). No abandoned streams — none are possible yet
  (r2s2 still batch 1 active; r2s1/r2s3/r2s4 all have clean B1 closes now,
  r2s1/r2s4 in batch 2 already, r2s3 not yet advanced by the orchestrator;
  no skip/block history anywhere in any stream). `state/streams/` directory
  still does not exist — consistent with no abandonments ever being needed.
- Repo hygiene: `git status --short` on
  `mffp_autoresearch/round2/experiment_cards/` shows only
  `r2s3_lf_train_signal/batch_1/B1.json` modified at final check (the
  register-turn completion write caught above) — not from this maintainer.
  Non-card writes seen in the broader round2 tree, all other subagents'
  legitimate in-progress/completed work: `state/r2s1_direct/current_stage.txt`
  (websearch->brainstormer transition), `brainstormer/r2s1_direct/batch_2/`
  (new dir), `tools/affine_ladder_voi.py` + `tools/posthoc_repair_ladder.py`
  (now committed to `tools/index.md`), `websearches/r2s1_direct/batch_2/
  {iteration_3,4,5,report}.md` (now complete). `state/orchestrator_flow.md`
  also modified (orchestrator-owned, outside this maintainer's scope).
  Confirmed no Write call this maintainer run touched `experiment_cards/`.
  `index.md` and `state/maintainer_report.md` are this maintainer's own
  writes. Most recent `round2: auto-sync` commit `55760b9`
  (2026-07-31T19:14:23Z), unchanged since last run — this run's deltas
  (including the r2s3 completion) are not yet auto-synced.
