# MFFP Autoresearch Round 2 — Dashboard (updated 2026-07-31T19:59:30Z)

## Streams

| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r2s1_direct | 23.0636 (best_floor_panel_geomean) | **2** | r2s1_direct-B1 **complete**; B2 in progress | **B1: unchanged, still COMPLETE.** **B2 advanced a full stage**: brainstormer/starter finished (worktree `round2/exp-r2s1_direct-B2` already existed) -> **builder now producing family code AND self-testing it**. `models_r2/r2s1_selected_form/` has 10 python modules (`config.py, common.py, ridge.py, floors.py, heads.py, wiener.py, blend.py, decoder.py, train.py, diagnostics.py`) + `smoke_eval.py` + `manifest.json` + `INSPIRATION.md`, all written this run's window; `__pycache__/*.pyc` present (module already imported/executed). **Live PID confirmed**: `score_panel.py --family_dir models_r2/r2s1_selected_form --datasets ext__helmholtz_2d --epochs 2 --no_cache` running a contract-tier smoke test at check time. Card itself unchanged on disk (`status: drafted`, `job_ids: []`) — no SLURM submission yet, consistent with an in-progress build/self-test | 0 live (no B2 jobs submitted yet) | `manifest.json`/`INSPIRATION.md` + contract smoke test, all within the last few min |
| r2s2_stacked | 23.0636 (best_floor_panel_geomean) | 1 | r2s2_stacked-B1 | **analyzing** — seed-0 panel leg COMPLETED (66166237, h200, 20.13 min, panel_geomean_skill **14.0756** on scored arm `frozen`; guard leg 66166238 completed earlier); mechanism-analysis remains in **turn 3**, actively producing files (`turn3_runD.json`/`.log`, `turn3_runE.json`/`.log`, `turn3_runA/B/C.log` all landed since last run). **Live PID confirmed**: `reanalysis_turn_3_fig.py` running at check time. `6_analysis`/`7_gap_and_future` still null as expected mid-turn. `reanalysis_progress` field on card still reads `turn_2` (lags the filesystem — same pattern seen on other streams pre-register-turn) | 0 live (jobs done) | `turn3_runE.log`/`turn3_corrector_E.json` <1 min old at check |
| r2s3_lf_train_signal | 23.0636 (best_floor_panel_geomean) | **2** | r2s3_lf_train_signal-B1 **complete**; B2 not yet drafted | **B1: unchanged, still COMPLETE** (all detail unchanged from last run). **B2 advanced two full stages this run**: websearch finished (`iteration_1..5.md` + `report.md` + `summary_so_far.md`, all landed within this run's window) -> **brainstormer now dispatched**, `current_stage.txt` = "brainstormer (B2 dispatched 2026-07-31; E1 preempted->baseline, E5 novel at N_hf~5; r2s4 turf boundary given)" (mtime ~9 min old at check, not stalled — `brainstormer/r2s3_lf_train_signal/batch_2/` dir exists but no output files yet, consistent with a just-dispatched agent). No `experiment_cards/r2s3_lf_train_signal/batch_2/B2.json` on disk yet — expected, drafted only after starter runs | 0 live (job done) | `state/r2s3_lf_train_signal/current_stage.txt` ~9 min old at check |
| r2s4_diag | **19.8178** (certified_3seed_panel_geomean, CI95 [19.385, 20.527]) | **2** | r2s4_diag-B1 **complete**; B2 drafted, builder actively self-testing | **B1: unchanged, still COMPLETE.** **B2 builder continues** (family `r2s4_b2_lfvalue` was already fully written last run) — this run adds a string of self-test artifacts: `scratchpad/contract_smoke.json`, per-dataset debug checkpoints (`dbg_ckpt_{ifc,sharp__sod_1d,fluid}/last.pt` + matching `.json`), then a fuller local self-test run (`rs.pid`, `rs_a.log`, `rs_b.json`, `probe_smoke/diagnostic.json`, `rs_ckpt/last.pt`, `res2_full.log`), the last landed essentially at check time. **Live PID confirmed**: `smoke_eval.py --dataset_name sharp__sod_1d --epochs 60 --out scratchpad/res2_full.json` running at check time. Card itself unchanged on disk (`status: drafted`, `job_ids: []`, `build_commit: null`) — no SLURM submission yet | 0 live (no B2 jobs submitted yet) | `scratchpad/res2_full.log` written essentially at check time |

**Anchor note**: r2s4_diag remains the only stream with a *certified* anchor
(`certified_3seed_panel_geomean`, 19.8178, replacing the training-free floor)
— r2s1_direct, r2s2_stacked, r2s3_lf_train_signal remain on the launch-time
`best_floor_panel_geomean` anchor (23.0636, `certified_utc` 2026-07-31T14:20:17Z,
unchanged). No anchor deltas this run. All anchors rendered verbatim from
`state/anchors/*.json`.

**This run's headline**: **no card `status` field changed this run** — the
round's 3 completions (r2s1_direct-B1, r2s3_lf_train_signal-B1, r2s4_diag-B1)
all carry over unchanged. All the action is local builder/mechanism-analysis
work, all confirmed live via `ps aux` PID matches (not just file-mtime
inference) for the first time on 3 of the 4 streams simultaneously: r2s1_direct
(contract-smoke self-test of the newly-built `r2s1_selected_form` family),
r2s2_stacked (mechanism-analysis turn 3 continuing), r2s4_diag (B2 builder's
local self-test on `sharp__sod_1d`). r2s3_lf_train_signal advanced two full
B2 stages (websearch -> brainstormer) confirmed via fresh file mtimes. Zero
live `r2-*` SLURM jobs — sixth consecutive check with none live; every B2
family is still in local/self-test territory, none has reached a SLURM
submission yet.

## Running / pending jobs

| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| (none) | — | — | — | No `r2-*` jobs live in `squeue` (confirmed via `sacct` cross-check — all 7 batch-1 jobs COMPLETED, no vanished-job false positives; no B2 jobs submitted yet for any stream). 3 local (non-SLURM) self-test processes confirmed live via `ps aux`: r2s1_direct-B2 contract smoke (`score_panel.py`/`smoke_eval.py` on `ext__helmholtz_2d`), r2s2_stacked-B1 turn-3 figure script, r2s4_diag-B2 self-test smoke (`smoke_eval.py` on `sharp__sod_1d`, 60 epochs) |

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
| r2s2_stacked-B1 | model | 14.0756 (single seed 0, no CI yet; scored arm `frozen`; ~all margin is the unpaired ifc_poisson column) | `confirmed` (initial-analyzer verdict; mechanism register turn 3 continuing, PID-confirmed live, `6_analysis`/`7_gap_and_future` still null) | pending (turn 3 in progress, not yet register) |

## Flags

- **No card-status deltas this run** — all 6 cards on disk (r2s1_direct-B1
  `complete`, r2s1_direct-B2 `drafted`, r2s2_stacked-B1 `analyzing`,
  r2s3_lf_train_signal-B1 `complete`, r2s4_diag-B1 `complete`, r2s4_diag-B2
  `drafted`) are unchanged in `status` from last run. `reopen_candidate` is
  `false` on all 6.
- **r2s1_direct B2 builder now producing and self-testing family code**: 10
  python modules + `smoke_eval.py` + `manifest.json` + `INSPIRATION.md`
  written this run's window under `models_r2/r2s1_selected_form/`; a
  contract-tier smoke test (`score_panel.py --datasets ext__helmholtz_2d
  --epochs 2 --no_cache`) is running right now (PID-confirmed) — live, not
  stalled. No SLURM submission yet.
- **r2s4_diag B2 builder continuing local self-tests**: a string of
  per-dataset debug checkpoints (ifc/sod_1d/fluid) followed by a fuller
  `sharp__sod_1d` self-test at 60 epochs, PID-confirmed running at check
  time. No SLURM submission yet.
- **r2s2_stacked-B1 turn 3 continues**: `turn3_runD`/`turn3_runE` artifacts
  landed since last run; PID-confirmed running `reanalysis_turn_3_fig.py`
  at check time — live, not stalled.
- **r2s3_lf_train_signal advanced into B2**: websearch complete, brainstormer
  now dispatched (~9 min old at check, not yet producing output — consistent
  with a just-dispatched agent, not stalled). No `B2.json` card yet
  (expected — drafted only after starter).
- **Timestamp anomaly (r2s1_direct-B1, unchanged, carried forward)**:
  `review_notes[0].utc` still reads `2026-07-31T17:05:00Z` (ahead-of-clock
  relative to the review file's actual write time, first flagged several
  runs ago). No scored quantity affected. Remains the card's only
  unresolved caveat since it closed `complete`.
- **Timing ledger**: no new upsert this run (all 7 entries from prior runs
  remain valid and match current `sacct` output exactly; re-validated as
  parseable JSON, no changes needed). Zero live `r2-*` jobs — sixth
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
  forward: the shared-max-abs-rungs scaler makes ifc_poisson's `rung_native`
  stage-1 loss ~42x amplitude-weighted toward rung 8 over HF (confound C1,
  card-locked design, not a build defect); F1 is epoch-matched but not
  step-matched (confound C2, "ran IN FAVOR of the losing arm" per the card's
  own `cratered_detail` — does not explain away the inversion). Cross-stream
  note: r2s3's HF-side affine LOO residual (3.2e-08 at every rung incl. the
  128 test rows) independently confirms r2s2_stacked-B1's earlier LF-side
  finding (ridge(cond) held-out nRMSE 0.0000 on the ifc_poisson LF field) —
  the ifc_poisson degeneracy is now cross-confirmed by two independent
  streams/estimators.
- **Gates**: G1-r2 PASS, G2-r2 PASS, G3-r2 PASS (all 2026-07-31,
  `state/gates.md`) — round cleared for stream launch. Unchanged this run.
- **Round-1 top-3 seed confirms**: NOT this maintainer's scope (round-1 jobs
  visible in `squeue` as `r1-*`, PENDING) — separate round, separate report.
- No reopen candidates on any of the 6 cards. No `blocked.md` file exists (no
  stream has ever blocked). No abandoned streams — none are possible yet
  (r2s2 still batch 1 active; r2s1/r2s3/r2s4 all have clean B1 closes and are
  in batch 2; no skip/block history anywhere in any stream). `state/streams/`
  directory still does not exist — consistent with no abandonments ever
  being needed.
- Repo hygiene: `git status --short` on
  `mffp_autoresearch/round2/experiment_cards/` is clean this run (no
  modified/untracked cards). Non-card writes seen in the broader round2
  tree, all other subagents' legitimate in-progress work:
  `state/r2s3_lf_train_signal/current_stage.txt`, `websearches/
  r2s3_lf_train_signal/batch_2/{iteration_1,3,4,5}.md`, `brainstormer/
  r2s3_lf_train_signal/batch_2/` (new, empty dir). `state/orchestrator_flow.md`
  also modified (orchestrator-owned, outside this maintainer's scope).
  Confirmed no Write call this maintainer run touched `experiment_cards/`.
  `index.md` and `state/maintainer_report.md` are this maintainer's own
  writes. Most recent `round2: auto-sync` commit `6fcdd3c`
  (2026-07-31T19:44:16Z) — this run's deltas are not yet auto-synced.
