# MFFP Autoresearch Round 3 — Dashboard (updated 2026-08-08T16:59:30Z)

## Status: FIRST FAILURE OF THE ROUND (r3s1 guard leg, ALGO class, debugger dispatched) — r3s4 all 3 seeds landed, certifier queued; r3s2/r3s3 running

Since the last maintainer snapshot (2026-08-08T09:59:03Z), four deltas landed.

1. **r3s1_factorised-B1 seed-0 split outcome: main leg COMPLETED clean, guard leg FAILED.**
   Main leg `66829977` COMPLETED in 7s — cache-served (`code_hash` unchanged since the reviewed evidence), panel geomean skill **25.0662** (5-ds), values bit-identical to the reviewed evidence, `epochs: 0` in the result JSON confirming the cache hit.
   Guard leg `66829978` **FAILED**, exit `1:0`, in 12s.
   Traceback: `RuntimeError: direction bank is not orthonormal: max|DD'-I| = 8.351e-01` raised in `models_r3/r3s1_twostage_crosscoef/basis.py:164` (`DirectionBank.__init__`), reached via `selection_stage` on the `heat_local` guard dataset.
   Classified **ALGO** (a real numerical-correctness assertion in the family's own code, not an infra/env fault).
   Orchestrator dispatched the experiment-debugger; `state/r3s1_factorised/current_stage.txt` → `debugger` (mtime ~09:45:30 local / 16:45:30Z, ~14 min before this walk).
   **Debug attempt 1 of 5** (cap: `slurm_algo_attempts: 5`) — in progress at time of this walk: no new commit past `6770381` in the `r3s1_factorised/B1` worktree, no `notes/handoff_experiment_debugger.md` yet. Card `status`/`job_ids` unchanged (`debug_notes: []` still empty — the debugger has not yet landed its verdict).

2. **r3s4_audit-B1 seeds 1-2 COMPLETED — all 3 seeds now in.**
   `66879667` (seed 1) COMPLETED 3m16s, panel geomean skill **19.5760**.
   `66879668` (seed 2) COMPLETED 3m13s, panel geomean skill **19.9318**.
   Both clean exit `0:0`, `.err` empty.
   `state/timing_ledger.json` upserted with both (elapsed_min 3.27 / 3.22).
   Orchestrator submitted the certifier leg directly: job `66921555` (`r3-r3s4_audit-B1-certify`), 2026-08-08T10:00 PDT, on the **`expansion` partition** (CPU-only, no `gres`, 4 CPU / no GPU — orchestrator adjudication: "expansion-partition CLI override... CPU-only bootstrap job, no H200").
   Confirmed live via `squeue`+`sacct`+`scontrol` — `PENDING (Priority)`.
   Card `job_ids` updated with the new `certify (D2-D4)` leg entry; `status` still `analyzing`, `5_actual_result.panel_geomean_skill` still seed-0-only (`per_seed: [19.4235]`, `ci95: null`) pending the certifier's 3-seed rollup.
   `state/r3s4_audit/current_stage.txt` → `certify`.

3. **r3s2_field_reach-B1 seed 0 (`66832670`) transitioned PENDING → RUNNING.**
   Confirmed via `squeue` (RUNNING, TIME 16:07) + `sacct` (State RUNNING, Start 2026-08-08T09:42:40 local, End Unknown — consistent) + `scontrol` (node `hpc-sm-02-04`, TimeLimit 03:00:00).
   No card-level transition due yet (RUNNING is SLURM-side only).

4. **r3s3_lf_value-B1 seeds 1-2 (`66879960`/`66879961`) transitioned PENDING → RUNNING.**
   Both on node `hpc-sm-02-03`, RUNNING TIME 15:35, `sacct` cross-checked (Start 2026-08-08T09:43:12 local, End Unknown).
   No card-level transition due yet.

No card fields were modified by this maintainer run. `git status --short experiment_cards/` shows one delta (r3s4_audit's `job_ids` certify-leg append) — confirmed via `git diff` to be the orchestrator's own pre-existing write, not touched by this maintainer.

All three launch gates remain **GREEN** on the 5-dataset scored panel (`state/gates.md`, unchanged since 2026-08-07T12:17Z certification): **G1-r3 GREEN**, **G2-r3 GREEN**, **G3-r3 GREEN**. ADR r3-0005 (pfc spectral-rung repair) remains **PROPOSED**, unchanged, still awaiting operator + mentor sign-off. No new ADR this cycle, no new HOLD entries.

**Program:** `program.md` · **Config:** `project.yaml` · **ADRs:** `docs/adr/` (0001 launch panel + A1, 0002 pfc crystalline box, 0003 estimator-integrity repairs, 0004 pfc report-only, 0005 pfc spectral-rung repair — PROPOSED) · **Card schema:** `experiment_cards/SCHEMA.md` · **Runbook:** `HOW_TO_LAUNCH.md`

## Streams
| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r3s1_factorised (gap) | 5-ds best-floor geomean 34.4198 | 1 | r3s1_factorised-B1 | `submitted_seed0`; main leg COMPLETED (cache-served, panel geomean 25.0662), **guard leg FAILED (ALGO)**; stage=**debugger** | seed 0 main: `66829977` COMPLETED (0:07); guard: `66829978` **FAILED** (0:12, exit 1, direction-bank orthonormality assertion on heat_local) | guard FAILED + debugger dispatched ~16:45:30Z (debug attempt 1/5, in progress, no verdict yet) — new this cycle |
| r3s2_field_reach (gap) | 5-ds best-floor geomean 34.4198 | 1 | r3s2_field_reach-B1 | `submitted_seed0`; stage=slurm-seed0 | seed 0: job `66832670` (`r3-r3s2_field_reach-B1-s0`, `gpu`, `nvidia_h200=1`), **RUNNING** (16:07, node hpc-sm-02-04) | PENDING → RUNNING — new this cycle |
| r3s3_lf_value (lever) | 5-ds best-floor geomean 34.4198 | 1 | r3s3_lf_value-B1 | `analyzing`; seed 0 COMPLETED + initial-analysis landed (panel geomean **10.8445**, verdict `proceed_to_seeds_1_2`, falsification **confirmed**); stage=slurm-seeds12 | seed 0: `66825323` COMPLETED (150m15s); seeds 1-2: `66879960`/`66879961` (`r3-r3s3_lf_value-B1-s{1,2}`), **RUNNING** (15:35, node hpc-sm-02-03) | PENDING → RUNNING (both seeds) — new this cycle |
| r3s4_audit (diag) | 5-ds best-floor geomean 34.4198 | 1 | r3s4_audit-B1 | `analyzing`; **all 3 seeds now COMPLETED** (geomeans 19.4235 / 19.5760 / 19.9318); stage=**certify** | seed 0: `66826610` COMPLETED (6m46s); seed 1: `66879667` COMPLETED (3m16s); seed 2: `66879668` COMPLETED (3m13s); certifier: `66921555` (`r3-r3s4_audit-B1-certify`), **PENDING (Priority)**, `expansion` partition (CPU-only, no GPU) | seeds 1-2 COMPLETED + certifier submitted 2026-08-08T10:00 PDT — new this cycle |

Per-dataset best-floor skills (5-ds scored panel): allen_cahn_2d 475.8568 (nn_condition), fisher_kpp_2d 390.7015 (train_mean), cahn_hilliard 23.1803 (nn_condition), ifc_poisson 8.0409 (nn_condition), ifc_heat 1.3941 (nn_condition). pfc 48.0773 (train_mean) is **report-only**, excluded from the geomean per ADR r3-0004 (pending possible reinstatement under ADR r3-0005 — still PROPOSED, no sign-off).
Source: `state/anchors/launch_anchors.json` (re-aggregated 2026-08-07 ~19:17Z; unchanged this cycle).

## Running / pending jobs
| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| 66921555 | r3s4_audit-B1 (certify D2-D4) | PENDING | 00:00:00 | `(Priority)`, partition `expansion`, `cpu=4/mem=32G`, no GPU — `r3-r3s4_audit-B1-certify` |
| 66832670 | r3s2_field_reach-B1 (seed 0) | RUNNING | 00:16:07 | node `hpc-sm-02-04`, partition `gpu`, `cpu=4/mem=32G/gres:nvidia_h200=1` — `r3-r3s2_field_reach-B1-s0` |
| 66879960 | r3s3_lf_value-B1 (seed 1) | RUNNING | 00:15:35 | node `hpc-sm-02-03`, partition `gpu`, `cpu=4/mem=32G/gres:nvidia_h200=1` — `r3-r3s3_lf_value-B1-s1` |
| 66879961 | r3s3_lf_value-B1 (seed 2) | RUNNING | 00:15:35 | node `hpc-sm-02-03`, partition `gpu`, `cpu=4/mem=32G/gres:nvidia_h200=1` — `r3-r3s3_lf_value-B1-s2` |

`66829977` (r3s1 seed 0 main) and `66829978` (r3s1 guard) dropped — COMPLETED / FAILED respectively (see Streams row + Flags). `66826610`, `66879667`, `66879668` (r3s4 seeds 0-2) dropped — all COMPLETED (see Streams row + timing ledger).

## Completed cards
| Card | Type | Panel geomean skill (±CI) | Falsification verdict | Tools promoted |
|---|---|---|---|---|
| — | — | — | — | none — no card has completed all 3 seeds + final review/certify yet. r3s3_lf_value-B1 has seed-0-only `5_actual_result` (panel geomean 10.8445, `ci95: null`, seeds 1-2 now RUNNING). r3s4_audit-B1 has all 3 seeds' raw results landed (19.4235 / 19.5760 / 19.9318) but the card's `5_actual_result.panel_geomean_skill` is still seed-0-only pending the certifier job (`66921555`, PENDING); `6_analysis`/`7_gap_and_future` are `null` on both. |

## Flags

- **NEW — r3s1_factorised-B1 guard leg FAILED, debugger dispatched (debug attempt 1 of 5, cap `slurm_algo_attempts: 5`).** Job `66829978`, exit `1:0`, `RuntimeError: direction bank is not orthonormal: max|DD'-I| = 8.351e-01` in `basis.py:164` (`DirectionBank.__init__`), reached via `selection_stage` on the `heat_local` guard dataset. Classified **ALGO** (numerical-correctness assertion inside the family's own code). No fix/relaunch commit yet in the `r3s1_factorised/B1` worktree (still at `6770381`); no debugger handoff note yet. **This is a debugger-in-progress condition, not yet requiring orchestrator action** — flagging per the maintainer's mandate to surface failures needing a debugger; the debugger is already dispatched and running. Watch next cycle for either a fix+relaunch or attempt 2/5.
- **r3s1_factorised-B1 main seed-0 leg is cache-served, not a fresh run.** `66829977` completed in 7s with `epochs: 0` in the result JSON — `code_hash` unchanged since the previously-reviewed evidence, panel geomean skill 25.0662 bit-identical. This is expected caching behavior (per `eval/score.py`'s `(family, dataset, epochs, seed, code_hash)` cache key convention referenced in project CLAUDE.md), not a defect — noted for completeness since it produces an unusually short elapsed time in the timing ledger.
- **r3s4_audit-B1: all 3 seeds landed, certifier queued on the `expansion` (CPU-only) partition.** Per-seed panel geomeans 19.4235 / 19.5760 / 19.9318 — tight spread (~2.6% range), consistent with a stable diagnostic result. Certifier job `66921555` will presumably compute the 3-seed CI and run the D2-D4 probes (`cratered_check`, F3/F4 falsification clauses per `pre_directed_certifier_note`). This is an orchestrator CPU-partition override (no GPU needed for a bootstrap/certify job) — noted, not flagged as an anomaly.
- **r3s3_lf_value-B1: seed-0 result confirms the card's hypothesis directionally.** `falsification_verdict: confirmed` (not fired) — the coverage channel, not the optimization channel, explains the LF-at-train benefit (97-101% of `E_total` on 10/10 positive cells). One sign inversion flagged: on ifc_poisson the coverage channel actively harms (E_cov = -2.77) on the repaired nested ladder — worth tracking once seeds 1-2 land (now RUNNING) whether this is seed noise or a real per-dataset exception. `guard_flags: ["heat_local"]` carried forward, unexplained, not gating — **note the coincidence that r3s1's new guard-leg failure is also on `heat_local`**; different failure mode (ALGO assertion vs. an unexplained guard flag) but same dataset, worth a cross-stream glance once r3s1's debugger lands its diagnosis.
- **r3s4_audit-B1: F1 (floor reproduction) FIRED as pre-directed, dual reading.** This is the known float64/float32 loader-precision seam (stripped-view breach on ifc_heat.nn_condition at 1.11e-9, just over the 1e-9 tol; native-dtype-control breaches on heat_local/sharp__sod_1d up to 7.7e-8) — adjudicated in prior cycles as a documented metrology property, not a defect; no anchor/floor value changed. F2 `not_fired` on both readings. F3/F4 await the certifier (now queued).
- **Eval-tree hygiene — resolved for all 4 streams, convention now codified.** r3s1 fixed commit `6770381`; r3s2 fixed commit `d5069a7`; r3s3/r3s4 redirected correctly from the start. The `ROUND2_EVAL_RESULTS`/`ROUND2_EVAL_CACHE` pattern is documented in `subagents/experiment-builder.md:218`. No open items.
- **ADR r3-0005 (pfc spectral-rung repair) — still PROPOSED, blocking on operator + mentor sign-off.** Do not execute without both sign-offs (it amends the frozen round-2 eval convention). Unchanged this cycle.
- **Gates** (`state/gates.md`): G1-r3 **GREEN** (2026-08-05, data), G2-r3 **GREEN** (2026-08-07, 5-ds preflight), G3-r3 **GREEN** (2026-08-07, 5-ds anchor re-aggregation, best-floor 34.4198) — all unchanged this cycle.
- **Reopen candidates**: none (`reopen_candidate: false` on all 4 batch-1 cards).
- **blocked.md**: none found under any stream directory.
- **Abandoned streams**: none. All 4 streams are on batch 1, all actively progressing (1 in debugger, 1 running, 1 with 2 seeds running, 1 with all 3 seeds landed + certifier queued). The 3-consecutive-skipped/blocked cap does not apply this early. No `state/streams/{stream}.json` markers exist (directory still does not exist).
- **Transcripts inbox**: empty — nothing to archive this run.
- **Timing ledger**: 5 entries now (r3s3_lf_value-B1 seed 0 `66825323` 150.25m; r3s4_audit-B1 seed 0 `66826610` 6.77m; r3s1_factorised-B1 seed 0 `66829977` 0.12m cache-served — new; r3s4_audit-B1 seed 1 `66879667` 3.27m — new; r3s4_audit-B1 seed 2 `66879668` 3.22m — new). The FAILED guard leg (`66829978`) is intentionally **not** upserted (ledger upserts COMPLETED jobs only). 4 live jobs (1 PENDING, 3 RUNNING) have not finished.
- **Watch for next cycle**: r3s1's debugger verdict (fix+relaunch vs. attempt 2/5); r3s4's certifier outcome (3-seed CI, F3/F4, `cratered_check`); whether r3s2/r3s3's RUNNING jobs complete; the `heat_local` coincidence between r3s1's new guard failure and r3s3's carried-forward guard flag.

Maintained by the maintainer cron.
