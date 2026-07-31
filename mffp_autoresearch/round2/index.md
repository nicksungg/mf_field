# MFFP Autoresearch Round 2 — Dashboard (updated 2026-07-31T18:55:09Z)

## Streams

| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r2s1_direct | 23.0636 (best_floor_panel_geomean) | 1 | r2s1_direct-B1 | **analyzing** — seed-0 job COMPLETED (66163572, h200, 6.95 min), panel_geomean_skill **19.6444**; mechanism-analysis **all 3 turns done** (`reanalysis_progress: turn_3`), handoff (`handoff_experiment_mechanism_analyzer.md`, ~18:20Z) addressed to the register turn; **register turn now actively in progress** — new tool `tools/band_gain_counterfactual.py` appeared on disk ~1 min before this check (not yet in `tools/index.md`), card itself being rewritten live (mtime ~18:47:30Z, still `7_gap_and_future: null`) | 0 live (job done) | card mtime 2026-07-31T18:47:30Z; register-turn tool write ~18:54Z (in progress at check time) |
| r2s2_stacked | 23.0636 (best_floor_panel_geomean) | 1 | r2s2_stacked-B1 | **analyzing** — seed-0 panel leg COMPLETED (66166237, h200, 20.13 min, panel_geomean_skill **14.0756** on scored arm `frozen`; guard leg 66166238 completed earlier); mechanism-analysis continues in **turn 2** (`turn2_reachable_set.png`, `reanalysis_turn_2_fig.py`, `turn2b_run.log` all <3 min old at check) — confirmed live, not stalled | 0 live (jobs done) | scratchpad write ~96 sec before this check |
| r2s3_lf_train_signal | 23.0636 (best_floor_panel_geomean) | 1 | r2s3_lf_train_signal-B1 | **analyzing** — seed-0 job (66165379) COMPLETED (77.05 min, all 5 legs); verdict **CRATERED + FALSIFIED** (F1 sign-inverted -7.35 skill units on ifc_poisson); mechanism-analysis progressed from turn 1 (confirmed live via `ps aux` last run) into **turn 2** (`turn2_panel_affinity.json`, `reanalysis_turn_2c.py`, `turn2_bands_and_voi.png`, all <3 min old at check) — confirmed live | 0 live (job done) | scratchpad write ~92 sec before this check |
| r2s4_diag | **19.8178** (certified_3seed_panel_geomean, CI95 [19.385, 20.527]) | **2** | r2s4_diag-B1 **complete**; B2 in progress | **B1: COMPLETE** (status flipped `analyzing` -> `complete` at card mtime 2026-07-31T18:38:14Z — the round's first fully-closed card: `7_gap_and_future` now populated, both promoted tools now correctly appear in `tools/index.md` (previous run's disk-inconsistency flag is now **resolved**)). **B2: websearch complete** (5 iterations + report + summary_so_far, all written 2026-07-31T18:44-18:54Z), now in **brainstormer** stage (`current_stage.txt`, dispatched; no `brainstormer/r2s4_diag/batch_2/` artifacts yet — dispatched-but-not-yet-producing, not stalled given websearch only just finished) | 0 live (all B1 jobs done; no B2 jobs yet) | B1 card completion 2026-07-31T18:38:14Z; B2 websearch report 2026-07-31T18:54:34Z (~15-25 min ago) |

**Anchor note**: r2s4_diag remains the only stream with a *certified* anchor
(`certified_3seed_panel_geomean`, 19.8178, replacing the training-free floor)
— r2s1_direct, r2s2_stacked, r2s3_lf_train_signal remain on the launch-time
`best_floor_panel_geomean` anchor (23.0636, `certified_utc` 2026-07-31T14:20:17Z,
unchanged). No anchor deltas this run. All anchors rendered verbatim from
`state/anchors/*.json`.

**This run's headline event**: **r2s4_diag-B1 is the round's first COMPLETE
card** (status `analyzing` -> `complete`, part 7 populated, both promoted
tools now correctly indexed in `tools/index.md` — resolving the
handoff-vs-disk inconsistency flagged for the last two runs) — and r2s4_diag
has already advanced into batch 2 (websearch done, brainstormer dispatched).
The other three streams continue live mechanism-analysis: r2s1_direct's
register turn is actively promoting tools right now (one new tool file
appeared mid-walk), r2s2_stacked and r2s3_lf_train_signal both progressed
from their respective turn-1s into turn 2. Zero live `r2-*` SLURM jobs
(third consecutive check) — all activity this run is local scripting.

## Running / pending jobs

| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| (none) | — | — | — | No `r2-*` jobs live in `squeue` (confirmed via `sacct` cross-check — all 7 batch-1 jobs COMPLETED, no vanished-job false positives) |

Unrelated interactive `bash` jobs and round-1 `r1-*` jobs also visible in the
queue — out of this maintainer's scope, not itemized here.

## Completed cards

| Card | Type | Panel geomean skill (±CI) | Falsification verdict | Tools promoted |
|---|---|---|---|---|
| r2s4_diag-B1 | diagnostic | 19.8178 IQM, CI95 [19.385, 20.527] (3 seeds) | n/a (diagnostic — no falsification clauses); mechanism register complete, part 7 written | 2 tools, both correctly indexed: `tools/conditional_mean_collapse.py`, `tools/condition_predictability_ceiling.py` |

**In progress (not yet `complete`, all have `5_actual_result`+`6_analysis`
populated, `7_gap_and_future` still `null`):**

| Card | Type | Panel geomean skill (±CI) | Falsification verdict | Tools promoted |
|---|---|---|---|---|
| r2s1_direct-B1 | model | 19.6444 (single seed 0, no CI yet) | pending mechanism-analyzer register (turns done, register in progress) | 1 new tool appearing on disk now (`band_gain_counterfactual.py`), not yet indexed; 2 more expected per orchestrator log ("3 tool promotions, name-collision warning given") |
| r2s2_stacked-B1 | model | 14.0756 (single seed 0, no CI yet; scored arm `frozen`; ~all margin is the unpaired ifc_poisson column) | pending mechanism-analyzer register (turn 2 in progress) | pending |
| r2s3_lf_train_signal-B1 | model | 25.3919 (`rung_native`, single seed 0) | **falsified** (F1 sign-inverted; F2 survives vs diverged comparator; F3 threshold-dependent) | pending (turn 2 in progress) |

## Flags

- **HEADLINE: r2s4_diag-B1 is the round's first fully COMPLETE card.**
  Status transitioned `analyzing` -> `complete` at card mtime
  2026-07-31T18:38:14Z (inside this run's window — prior run ended
  18:34:12Z). `7_gap_and_future` populated (open question on
  architecture-vs-information gap; next-direction names 4 concrete B2 tasks).
  The **previously-flagged tools/index.md inconsistency is now resolved**:
  both `conditional_mean_collapse.py` and `condition_predictability_ceiling.py`
  are correctly indexed (`tools/index.md` lines 58-59, 1878, 1921).
- **r2s4_diag has already advanced to batch 2**: `current_batch.txt` = 2,
  `current_stage.txt` = "brainstormer (B2 dispatched 2026-07-31; D2
  estimator-naming correction binding; DOPD advantage-gap design)". B2
  websearch is done (`websearches/r2s4_diag/batch_2/{iteration_1..5,report,
  summary_so_far}.md`, all written 2026-07-31T18:44-18:54Z) — per
  `state/orchestrator_flow.md`'s own log: D2 corrects B1's ceiling estimators
  as already-published objects; D1 opens value-of-LF as a DOPD
  advantage-gap-ablation design; D3 sells a lambda*/James-Stein shrinkage
  diagnostic. No `brainstormer/r2s4_diag/batch_2/` artifacts on disk yet
  (dispatched moments ago per stage-file mtime ~132s old at check) — not
  stalled.
- **r2s1_direct-B1 register turn caught mid-flight**: while walking this
  run, a new tool file `tools/band_gain_counterfactual.py` appeared on disk
  (~1 min old at check) and the card itself was being actively rewritten
  (`experiment_cards/r2s1_direct/batch_1/B1.json` mtime advancing during the
  walk) — confirmed live via `git status --short` showing it as freshly
  modified. Per `state/orchestrator_flow.md`, the register turn promotes 3
  tools total with "a name-collision warning given" (not yet resolved on
  disk at check time — only 1 of 3 visible). Expect this to complete by the
  next maintainer run.
- **Mechanism-analysis progressing on r2s2_stacked and r2s3_lf_train_signal**,
  both now in turn 2 (up from turn 1 last run), both liveness-confirmed via
  scratchpad files <3 min old at check — not stalled.
- **Timestamp anomaly (r2s1_direct-B1, unchanged, carried forward)**:
  `review_notes[0].utc` still reads `2026-07-31T17:05:00Z` (ahead-of-clock
  relative to the review file's actual write time, first flagged several
  runs ago). No scored quantity affected. (The r2s4_diag mechanism-analyzer
  handoff ahead-of-clock anomaly flagged in prior runs is now moot — that
  card has moved to `complete` and past it into B2.)
- **Timing ledger**: no new upsert this run (all 7 entries from prior runs
  remain valid and match current `sacct` output exactly; re-validated as
  parseable JSON, no changes needed). Zero live `r2-*` jobs — third
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
  own `cratered_detail` — does not explain away the inversion).
- **Gates**: G1-r2 PASS, G2-r2 PASS, G3-r2 PASS (all 2026-07-31,
  `state/gates.md`) — round cleared for stream launch. Unchanged this run.
- **Round-1 top-3 seed confirms**: NOT this maintainer's scope (round-1 jobs
  visible in `squeue` as `r1-*`, PENDING) — separate round, separate report.
- No reopen candidates on any of the 4 cards. No `blocked.md` file exists
  (no stream has ever blocked). No abandoned streams — none are possible yet
  (r2s1/r2s2/r2s3 all still batch 1 active; r2s4 just entered batch 2 with
  a clean B1 close, no skip/block history anywhere).
- Repo hygiene: `git status --short` on `mffp_autoresearch/round2/
  experiment_cards/` shows all 3 non-r2s4 cards as actively modified by
  other subagents mid-walk (r2s1_direct's register turn, plus r2s2_stacked/
  r2s3_lf_train_signal presumably from mechanism-analyzer turn-2 progress
  writes) — confirmed no Write call this maintainer run touched
  `experiment_cards/`. `index.md` and `state/maintainer_report.md` are this
  maintainer's own writes.
