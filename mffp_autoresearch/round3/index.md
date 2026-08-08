# MFFP Autoresearch Round 3 — Dashboard (updated 2026-08-08T20:19:30Z)

## STOP-THE-LINE #2 IS ACTIVE — HOLD SET (2026-08-08T19:51:50Z, commit `26089e8`)

Stale-checkpoint anchor contamination.
r3s3_lf_value-B1's mechanism analyzer (turn 2) discovered that the mandated `last.pt` checkpoint-resume contract silently no-op'd several ADR r3-0002/r3-0003 anchor re-scores: the launch-anchor **ifc_poisson** cells for `r2s3_lf_train_signal-B3` (all 6 legs) and `r2s1_direct-B2`/`B3` (all seeds) resumed pre-repair weights (`resumed_from_step=5000`, `train_seconds` 1.3-2.9s, checkpoint mtimes 2026-08-03/04 vs ladder adoption 2026-08-05) and were re-scored on the repaired arrays with stale weights.
`r2s2_stacked-B1` is possibly mixed.
Checkpoints carry no data hash — the sibling gap to the score-cache hole that ADR r3-0003 D4 already closed.

**Blast radius:** `state/anchors/launch_anchors.json` **ifc_poisson columns + panel geomeans are invalid pending repair**.
r3s3-B1's own vs-anchor deltas (-38.97% ifc_poisson, -10.14% panel) are **artefacts of this contamination**, already recorded as such on the card — not real effects.
Round-3's own experiment legs are audited **CLEAN (0/225 stale)** — the contamination is confined to the launch-anchor tree, not batch-1 training.
No queued job depends on the stale cells; **none cancelled**.

**Batch advancement and claim adjudication are halted under HOLD.**
As a direct consequence, the orchestrator is **deliberately withholding the analyzer stages for r3s1_factorised-B1, r3s2_field_reach-B1, and r3s4_audit-B1** even though their underlying SLURM jobs have now landed (see Streams table below) — their certified thresholds and claims would otherwise need recomputation once the anchor repair lands, so advancing them now would be wasted or misleading work.
This is why all three cards' `current_stage.txt` and card `status` are unchanged this cycle despite new COMPLETED jobs.
Repair plan on file (`state/orchestrator_flow.md` top entry): quarantine stale anchor cells + delete stale checkpoints -> fresh-train those anchor legs with empty checkpoint dirs -> re-audit with `stale_checkpoint_audit.py` -> rebuild anchors -> recompute affected deltas; permanent fix binds data hashes into checkpoints (sixth-class check) run at every anchor certification.
Operator adjudication pending.
The maintainer takes no action on cards or anchors (read-only) — this section exists to surface the HOLD prominently for the orchestrator/operator.

## Status: r3s4 certifier and r3s1 guard relaunch both COMPLETED this cycle; r3s2 seeds 1-2 now RUNNING — all three streams' analyzer stages remain deliberately withheld under HOLD

Since the last maintainer snapshot (2026-08-08T19:58:33Z):

1. **r3s4_audit-B1 certifier (`66921555`) COMPLETED** — 23s, exit `0:0`, `expansion` partition (CPU-only).
   D2 (seed noise) + D3 (row noise, two-threshold fusion) artifacts landed at `eval/{diagnostic.json, noise_floor_candidate.json, diagnostic_cell_integrity.json}` (`worktrees/r3s4_audit/B1/scratchpad/d3_fixture/eval/`).
   Verdicts: F1 (floor repro) `unavailable`; F2 (seam-is-not-real) `not_fired` (1/3 ADR r3-0004 scored-only, 1/4 as-written); F3 (reference noise negligible) `not_fired`; F4 (seed_mce > 2x provisional) `not_fired` (0 breaches on the 2 datasets this D2/D3 fusion sub-panel scores: ifc_heat + cahn_hilliard).
   Fusion-panel geomean (ifc_heat + cahn_hilliard subset, **not** the full 5-ds panel) ci95 [8.3526, 8.5735], seed_mce 0.2208.
   **PROVISIONAL** — these artifacts read `state/anchors_repaired/floors.json`, which sits in the same anchor-repair scope as the contaminated launch-anchor ifc_poisson cells (STOP-THE-LINE #2); will be recomputed after the retrain repair lands.
2. **r3s1_factorised-B1 guard relaunch (`66922977`) COMPLETED** — 35s, exit `0:0`, `gpu` partition.
   `result_guard_s0.json` landed: `panel_geomean_skill` **0.3260** over guards `heat_local,fluid,sharp__sod_1d`, all 3 legs present, no failure.
   The debug attempt-1 (of 5) POD-rank numerical-boundary fix is now **verified in production**, superseding the original guard leg (`66829978`, FAILED, exit 1, direction-bank orthonormality assertion on heat_local).
3. **r3s2_field_reach-B1 seeds 1-2 (`66928385`/`66928386`) now RUNNING** — ~18-19 min elapsed at time of this walk, `gpu` partition, confirmed via `squeue` (node `hpc-sm-02-17`) + `sacct` (no transient-empty ambiguity). Previously PENDING.

Unchanged this cycle:

4. **r3s3_lf_value-B1 remains `complete`** (first card of the round to finish all 7 parts) — no new activity.

**Orchestrator policy note**: r3s1/r3s2/r3s4's analyzer stages are deliberately withheld under the HOLD (see banner above) — this is not a stall.
`current_stage.txt` is unchanged for all three (`slurm-seed0`, `slurm-seeds12`, `certify` respectively) despite the new COMPLETED jobs above; card `status` fields are likewise unchanged (`running`, `analyzing`, `analyzing`).

No card fields were modified by this maintainer run (`git status --short experiment_cards/` clean).

All three launch gates remain **GREEN** on the 5-dataset scored panel per `state/gates.md` (unchanged since 2026-08-07T12:17Z certification) — **but G3-r3's anchor evidence is now under active dispute** per STOP-THE-LINE #2 above; read G3 alongside the HOLD, not as an unqualified green.
ADR r3-0005 (pfc spectral-rung repair) remains **PROPOSED**, unchanged, still awaiting operator + mentor sign-off.

**Program:** `program.md` · **Config:** `project.yaml` · **ADRs:** `docs/adr/` (0001 launch panel + A1, 0002 pfc crystalline box, 0003 estimator-integrity repairs, 0004 pfc report-only, 0005 pfc spectral-rung repair — PROPOSED) · **Card schema:** `experiment_cards/SCHEMA.md` · **Runbook:** `HOW_TO_LAUNCH.md`

## Streams
| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r3s1_factorised (gap) | 5-ds best-floor geomean 34.4198 (see anchor-dispute flag) | 1 | r3s1_factorised-B1 | `running`; main leg COMPLETED (cache-served, panel geomean 25.0662), guard leg **RELAUNCH COMPLETED** (panel_geomean_skill 0.3260, fix verified in production); stage=slurm-seed0 (analyzer stage withheld under HOLD) | seed 0 main: `66829977` COMPLETED (0:07); guard (orig): `66829978` FAILED (0:12, exit 1); guard (relaunch): `66922977` **COMPLETED (0:35, exit 0:0)** | **new this cycle — guard relaunch COMPLETED, `result_guard_s0.json` landed** |
| r3s2_field_reach (gap) | 5-ds best-floor geomean 34.4198 (see anchor-dispute flag) | 1 | r3s2_field_reach-B1 | `analyzing`; seed-0 initial-analysis landed (panel geomean **10.7213**, verdict `proceed_to_seeds_1_2`); stage=slurm-seeds12 (analyzer stage withheld under HOLD) | seed 0: `66832670` COMPLETED (00:44:20); seeds 1-2: `66928385`/`66928386` (`r3-r3s2_field_reach-B1-s{1,2}`), **RUNNING (~18-19 min)** | **new this cycle — seeds 1-2 transitioned PENDING -> RUNNING** |
| r3s3_lf_value (lever) | 5-ds best-floor geomean 34.4198 (**ifc_poisson columns invalid — stale-checkpoint contamination, see HOLD banner**) | 1 | r3s3_lf_value-B1 | **`complete`** — first card of the round to finish all 7 parts; 3-seed panel geomean **11.0789** (ci95 [10.8445, 11.2471]); `falsification_verdict` **confirmed**; vs-anchor -10.14%/-38.97% deltas flagged as anchor artefacts (STOP-THE-LINE #2); 2 tools promoted; stage=mechanism-analysis | seed 0: `66825323` COMPLETED (150m15s); seeds 1-2: `66879960`/`66879961` COMPLETED (02:20:08 / 02:20:09, exit 0:0, 60 legs each) | unchanged |
| r3s4_audit (diag) | 5-ds best-floor geomean 34.4198 | 1 | r3s4_audit-B1 | `analyzing`; all 3 seeds COMPLETED (geomeans 19.4235 / 19.5760 / 19.9318); certifier **COMPLETED** (D2-D4 artifacts landed, **PROVISIONAL** pending anchor repair); stage=certify (analyzer stage withheld under HOLD) | seed 0: `66826610` COMPLETED (6m46s); seed 1: `66879667` COMPLETED (3m16s); seed 2: `66879668` COMPLETED (3m13s); certifier: `66921555` (`r3-r3s4_audit-B1-certify`) **COMPLETED (0:23, exit 0:0)**, `expansion` partition (CPU-only) | **new this cycle — certifier COMPLETED, D2-D4 artifacts landed (provisional)** |

Per-dataset best-floor skills (5-ds scored panel): allen_cahn_2d 475.8568 (nn_condition), fisher_kpp_2d 390.7015 (train_mean), cahn_hilliard 23.1803 (nn_condition), ifc_poisson 8.0409 (nn_condition, **DISPUTED — stale-checkpoint contamination**), ifc_heat 1.3941 (nn_condition). pfc 48.0773 (train_mean) is **report-only**, excluded from the geomean per ADR r3-0004 (pending possible reinstatement under ADR r3-0005 — still PROPOSED, no sign-off).
Source: `state/anchors/launch_anchors.json` (file itself unchanged this cycle, mtime 2026-08-07T12:16Z — rendered as-is per instruction, never recomputed by the maintainer; flagged disputed per STOP-THE-LINE #2, repair pending operator adjudication).

## Running / pending jobs
| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| 66928385 | r3s2_field_reach-B1 (seed 1) | RUNNING | ~00:18:37 | node `hpc-sm-02-17`, partition `gpu`, `cpu=8/mem=64G/gres:nvidia_h200=1` — `r3-r3s2_field_reach-B1-s1`. Unaffected by HOLD's repair scope. |
| 66928386 | r3s2_field_reach-B1 (seed 2) | RUNNING | ~00:18:37 | node `hpc-sm-02-17`, partition `gpu`, `cpu=8/mem=64G/gres:nvidia_h200=1` — `r3-r3s2_field_reach-B1-s2`. Unaffected by HOLD's repair scope. |

`66921555` (r3s4 certify) and `66922977` (r3s1 guard relaunch) both COMPLETED this cycle and dropped from `squeue`/pending — see Streams table + Completed-jobs coverage below. No other live jobs. Confirmed via `squeue` (only the 2 r3s2 RUNNING rows present) + `sacct` (no transient-empty-squeue ambiguity).

## Completed cards
| Card | Type | Panel geomean skill (±CI) | Falsification verdict | Tools promoted |
|---|---|---|---|---|
| r3s3_lf_value-B1 | model (lever) | **11.0789** (ci95 [10.8445, 11.2471], 3-seed 5-ds panel) | **confirmed** — coverage channel (supply of distinct condition rows), not optimization channel, explains the LF-at-train benefit. vs-anchor delta -10.14% (ifc_poisson -38.97%) recorded on the card as a **stale-checkpoint anchor artefact (STOP-THE-LINE #2)**, not a real effect — do not cite as a claim. | `response_decomposition.py`, `stale_checkpoint_audit.py` |

r3s2_field_reach-B1 has seed-0-only `5_actual_result` (panel geomean 10.7213, `ci95: null`, seeds 1-2 now RUNNING) — not yet complete.
r3s4_audit-B1 has all 3 seeds' raw results landed (19.4235 / 19.5760 / 19.9318) and the certifier is now COMPLETED (D2-D4 landed, provisional) — analyzer write-back withheld under HOLD, card not yet `complete`.
r3s1_factorised-B1 has no `5_actual_result` yet — main leg cache-served, guard leg relaunch COMPLETED — analyzer stage withheld under HOLD.

## Flags

- **STOP-THE-LINE #2 — stale-checkpoint anchor contamination, HOLD ACTIVE (see banner at top of this file).** `state/HOLD.json` set 2026-08-08T19:51:50Z, commit `26089e8`, unchanged this cycle. Launch-anchor ifc_poisson cells (r2s3-B3 all legs, r2s1-B2/B3 all seeds, r2s2-B1 possibly mixed) resumed pre-repair checkpoints and were scored on repaired data. `launch_anchors.json` ifc_poisson columns + panel geomeans invalid pending repair. Round-3's own experiment legs audited CLEAN (0/225). No queued job cancelled — none depend on the stale cells. **New this cycle**: the orchestrator is deliberately withholding the analyzer stages for r3s1/r3s2/r3s4 despite new COMPLETED SLURM jobs (guard relaunch, certifier) — not a stall, a HOLD-driven policy choice pending operator adjudication of the repair plan.
- **r3s4_audit-B1: certifier `66921555` COMPLETED this cycle — D2-D4 artifacts landed but marked PROVISIONAL.** F1 unavailable, F2/F3/F4 all `not_fired`. The D2/D3 fusion sub-panel scores only ifc_heat + cahn_hilliard (not the full 5-ds panel) but reads `state/anchors_repaired/floors.json`, which is in-scope for the STOP-THE-LINE #2 repair — recompute expected once the anchor repair lands.
- **r3s1_factorised-B1: guard relaunch `66922977` COMPLETED this cycle — debug fix verified in production.** `result_guard_s0.json` landed, panel_geomean_skill 0.3260, guards `heat_local,fluid,sharp__sod_1d` all clean. Debug attempt 1 of 5 used (cap `slurm_algo_attempts: 5`). Root cause: POD rank cut sitting exactly on the numerical accuracy boundary; fix proven bitwise no-op on all 5 scored panel cells plus both other guards.
- **r3s2_field_reach-B1: seeds 1-2 (`66928385`/`66928386`) transitioned PENDING -> RUNNING this cycle**, ~18-19 min elapsed. seed-0 initial-analysis: F1 does not fire, F2 fires (pre-registered modal outcome). Panel geomean skill **10.7213**. Guard panel geomean skill 0.2424, `guard_flags: []`.
- **r3s1_factorised-B1 main seed-0 leg is cache-served, not a fresh run** (`66829977` completed in 7s, `epochs: 0`, `code_hash` unchanged) — expected caching behavior per `eval/score.py`, not a defect.
- **r3s3_lf_value-B1: `status: complete`, unchanged this cycle.** Two tools promoted (`response_decomposition.py`, `stale_checkpoint_audit.py`), both verified in `tools/index.md`. `guard_flags: ["heat_local"]` carried forward, unexplained but not gating. `next_direction` recorded for batch 2: LF-condition-row-count sweep on ch + ifc_heat, fixing the per-rung scaler bug, dropping ifc_poisson as a probe.
- **Eval-tree hygiene — resolved for all 4 streams, convention codified in `subagents/experiment-builder.md:218`.** No open items.
- **ADR r3-0005 (pfc spectral-rung repair) — still PROPOSED, blocking on operator + mentor sign-off.** Unchanged this cycle.
- **Gates** (`state/gates.md`): G1-r3 **GREEN** (2026-08-05, data), G2-r3 **GREEN** (2026-08-07, 5-ds preflight), G3-r3 **GREEN** (2026-08-07, 5-ds anchor re-aggregation, best-floor 34.4198) — file unchanged this cycle, **but read G3 alongside STOP-THE-LINE #2**: its ifc_poisson anchor evidence is now under active dispute (not a gate-file edit — maintainer is read-only for gates).
- **Reopen candidates**: none (`reopen_candidate: false` on all 4 batch-1 cards).
- **blocked.md**: none found under any stream directory.
- **Abandoned streams**: none. All 4 streams are on batch 1, all actively progressing or complete (1 guard relaunch landed + analyzer withheld, 1 seed-0 analyzed + seeds 1-2 RUNNING, 1 `complete`, 1 certifier landed + analyzer withheld). The 3-consecutive-skipped/blocked cap does not apply this early. No `state/streams/{stream}.json` markers exist (directory still does not exist).
- **Transcripts inbox**: empty — nothing to archive this run.
- **Timing ledger**: 10 entries (was 8). **New this cycle**: `66921555` (r3s4_audit-B1 certify, 0.38m, PROVISIONAL) and `66922977` (r3s1_factorised-B1 guard-s0 relaunch, 0.58m, panel_geomean_skill 0.3260). Unchanged: r3s3_lf_value-B1 seed 0 `66825323` 150.25m, seed 1 `66879960` 140.13m, seed 2 `66879961` 140.15m; r3s4_audit-B1 seed 0 `66826610` 6.77m, seed 1 `66879667` 3.27m, seed 2 `66879668` 3.22m; r3s1_factorised-B1 seed 0 `66829977` 0.12m cache-served; r3s2_field_reach-B1 seed 0 `66832670` 44.33m. FAILED guard leg (`66829978`) intentionally not upserted (ledger upserts COMPLETED jobs only).
- **Watch for next cycle**: operator adjudication on the STOP-THE-LINE #2 repair plan (quarantine + fresh retrain + ckpt data-hash binding); r3s2's seeds 1-2 (`66928385`/`66928386`, RUNNING, expect ~2h20m total per r3s3's precedent on this partition/gpu combo); whether the orchestrator advances r3s1/r3s2/r3s4's analyzer stages once HOLD-adjudicated (they are currently deliberately withheld, not stalled).

Maintained by the maintainer cron.
