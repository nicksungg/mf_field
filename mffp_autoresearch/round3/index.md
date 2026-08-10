# MFFP Autoresearch Round 3 — Dashboard (updated 2026-08-10T03:22:14Z)

## STOP-THE-LINE #2 IS ACTIVE — HOLD SET, REPAIR NOW EXECUTING

(2026-08-08T19:51:50Z HOLD set, commit `26089e8`; 2026-08-09 operator adjudication "continue", repair executing, commit `3fd7388`)

Stale-checkpoint anchor contamination.
r3s3_lf_value-B1's mechanism analyzer (turn 2) discovered that the mandated `last.pt` checkpoint-resume contract silently no-op'd several ADR r3-0002/r3-0003 anchor re-scores: the launch-anchor **ifc_poisson** cells for `r2s3_lf_train_signal-B3` (all 6 legs) and `r2s1_direct-B2`/`B3` (all seeds) resumed pre-repair weights and were re-scored on the repaired arrays with stale weights.
`r2s2_stacked-B1` seeds 0-1 were also stale (trained+scored before the ladder adoption, never re-scored post-repair); seed 2 was fresh-trained and audited CLEAN.

**Blast radius (unchanged):** `state/anchors/launch_anchors.json` **ifc_poisson columns + panel geomeans are invalid pending repair**.
Round-3's own experiment legs are audited **CLEAN (0/225 stale)**.

**Eloise adjudicated "continue" on 2026-08-09** — accepts the on-file repair plan.
The orchestrator has executed the first three steps:

1. **89 stale paths quarantined** (scored cells + ckpt dirs + derived eval artifacts + 14 score-cache entries) — manifest `mffp_autoresearch_outputs/round3_anchors/quarantine_stale_ckpt_manifest_2026-08-09.json` (confirmed present on disk).
2. **11 fresh-train repair jobs submitted** — `r3RPR-*` names, SLURM 89201-89211 (all still **PENDING(Priority)**, see Running/pending table below — cluster-wide queue congestion, not a stall).
3. **Permanent sixth-class check wired in** — `tools/make_round3_anchors.py` now runs `stale_gate()` (`--fail-on-stale` over every panel cell) at every future anchor certification.

**`state/HOLD.json` itself is unchanged** (`set_at` still `2026-08-08T19:51:50Z`) — the HOLD has **not** been cleared, only the repair it gates has begun.
Remaining sequence per `state/stale_ckpt_repair_jobs_2026-08-09.json`'s `on_completion`: repair jobs land → `--fail-on-stale` re-audit clean → anchor rebuild (audit-gated) → r3s3-B1 vs-anchor delta recompute → HOLD clear → dispatch of the withheld r3s1/r3s2/r3s4 initial-analyzer stages.
**Batch advancement and claim adjudication remain halted under HOLD** — the three withheld analyzer stages are confirmed still withheld this cycle (see Streams table).
The maintainer takes no action on cards or anchors (read-only) — this section exists to surface the HOLD prominently for the orchestrator/operator.

## Status: repair jobs queued, no compute landed yet this cycle

Since the last maintainer snapshot (2026-08-08T20:38:04Z, ~30.7h ago):

1. **Operator adjudication landed and repair execution began** (commit `3fd7388`) — quarantine + gate confirmed on disk; 11 `r3RPR-*` repair jobs submitted 2026-08-09T20:13:24, still PENDING(Priority) after ~7h05m (cluster `gpu` partition currently carries 299 queued/running jobs, `expansion` 1331, across all users — congestion, not an error).
2. **No new SLURM completions** since the last walk. Timing ledger unchanged at 12 entries.
3. **All 4 cards unchanged** — no card files modified (`git status --short experiment_cards/` clean). r3s1/r3s2/r3s4's analyzer stages correctly remain withheld pending the repair; r3s3 remains the round's only `complete` card.

**Program:** `program.md` · **Config:** `project.yaml` · **ADRs:** `docs/adr/` (0001 launch panel + A1, 0002 pfc crystalline box, 0003 estimator-integrity repairs, 0004 pfc report-only, 0005 pfc spectral-rung repair — PROPOSED) · **Card schema:** `experiment_cards/SCHEMA.md` · **Runbook:** `HOW_TO_LAUNCH.md`

## Streams
| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r3s1_factorised (gap) | 5-ds best-floor geomean 34.4198 (see anchor-dispute flag) | 1 | r3s1_factorised-B1 | `running`; main leg COMPLETED (cache-served, panel geomean 25.0662), guard leg COMPLETED (panel_geomean_skill 0.3260, fix verified in production); stage=slurm-seed0 (analyzer stage withheld under HOLD) | seed 0 main: `66829977` COMPLETED (0:07); guard (orig): `66829978` FAILED (0:12, exit 1); guard (relaunch): `66922977` COMPLETED (0:35, exit 0:0) | none — unchanged since 2026-08-08T20:19:30Z |
| r3s2_field_reach (gap) | 5-ds best-floor geomean 34.4198 (see anchor-dispute flag) | 1 | r3s2_field_reach-B1 | `analyzing`; all 3 seeds' raw panel geomeans landed (10.7213 / 10.3180 / 17.8277); stage=slurm-seeds12 (analyzer stage withheld under HOLD) | seed 0: `66832670` COMPLETED (00:44:20); seeds 1-2: `66928385`/`66928386` COMPLETED (00:36:33 each, exit 0:0) | none — unchanged since 2026-08-08T20:38:04Z |
| r3s3_lf_value (lever) | 5-ds best-floor geomean 34.4198 (**ifc_poisson columns invalid — stale-checkpoint contamination, see HOLD banner**) | 1 | r3s3_lf_value-B1 | **`complete`** — 3-seed panel geomean **11.0789** (ci95 [10.8445, 11.2471]); `falsification_verdict` **confirmed**; vs-anchor -10.14%/-38.97% deltas flagged as anchor artefacts (STOP-THE-LINE #2); 2 tools promoted; stage=mechanism-analysis | seed 0: `66825323` COMPLETED (150m15s); seeds 1-2: `66879960`/`66879961` COMPLETED (02:20:08 / 02:20:09, exit 0:0) | none — unchanged since 2026-08-08T19:58:33Z |
| r3s4_audit (diag) | 5-ds best-floor geomean 34.4198 | 1 | r3s4_audit-B1 | `analyzing`; all 3 seeds COMPLETED (geomeans 19.4235 / 19.5760 / 19.9318); certifier COMPLETED (D2-D4 artifacts landed, **PROVISIONAL** pending anchor repair); stage=certify (analyzer stage withheld under HOLD) | seed 0: `66826610` COMPLETED (6m46s); seed 1: `66879667` COMPLETED (3m16s); seed 2: `66879668` COMPLETED (3m13s); certifier: `66921555` COMPLETED (0:23, exit 0:0) | none — unchanged since 2026-08-08T20:19:30Z |
| **r2s1_direct-B2** (anchor, ifc_poisson repair) | n/a — this is an anchor leg, not a round-3 stream | — | anchor tree | STALE (3/3 seeds), quarantined 2026-08-09 | repair: `89201`/`89204`/`89207` all **PENDING(Priority)** | new this cycle — repair job submitted |
| **r2s1_direct-B3** (anchor, ifc_poisson repair) | n/a | — | anchor tree | STALE (3/3 seeds), quarantined 2026-08-09 | repair: `89202`/`89205`/`89208` all **PENDING(Priority)** | new this cycle — repair job submitted |
| **r2s2_stacked-B1** (anchor, ifc_poisson repair) | n/a | — | anchor tree | STALE (seeds 0-1 only; seed 2 CLEAN, kept), quarantined 2026-08-09 | repair: `89210`/`89211` (seeds 0-1) all **PENDING(Priority)** | new this cycle — repair job submitted |
| **r2s3_lf_train_signal-B3** (anchor, ifc_poisson repair) | n/a | — | anchor tree | STALE (6/6 legs, both ifc_A0/ifc_A1), quarantined 2026-08-09 | repair: `89203`/`89206`/`89209` all **PENDING(Priority)** | new this cycle — repair job submitted |

Per-dataset best-floor skills (5-ds scored panel): allen_cahn_2d 475.8568 (nn_condition), fisher_kpp_2d 390.7015 (train_mean), cahn_hilliard 23.1803 (nn_condition), ifc_poisson 8.0409 (nn_condition, **DISPUTED — stale-checkpoint contamination, repair in progress**), ifc_heat 1.3941 (nn_condition). pfc 48.0773 (train_mean) is **report-only**, excluded from the geomean per ADR r3-0004 (pending possible reinstatement under ADR r3-0005 — still PROPOSED, no sign-off).
Source: `state/anchors/launch_anchors.json` (file itself unchanged this cycle, mtime 2026-08-07T12:16Z — rendered as-is per instruction, never recomputed by the maintainer; flagged disputed per STOP-THE-LINE #2, repair pending).

## Running / pending jobs
| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| `89201` | r2s1_direct-B2 (anchor repair, ifc_poisson seed 0) | PENDING | 0:00 | (Priority) |
| `89204` | r2s1_direct-B2 (anchor repair, ifc_poisson seed 1) | PENDING | 0:00 | (Priority) |
| `89207` | r2s1_direct-B2 (anchor repair, ifc_poisson seed 2) | PENDING | 0:00 | (Priority) |
| `89202` | r2s1_direct-B3 (anchor repair, ifc_poisson seed 0) | PENDING | 0:00 | (Priority) |
| `89205` | r2s1_direct-B3 (anchor repair, ifc_poisson seed 1) | PENDING | 0:00 | (Priority) |
| `89208` | r2s1_direct-B3 (anchor repair, ifc_poisson seed 2) | PENDING | 0:00 | (Priority) |
| `89203` | r2s3_lf_train_signal-B3 (anchor repair, ifc_A0/A1 seed 0) | PENDING | 0:00 | (Priority) |
| `89206` | r2s3_lf_train_signal-B3 (anchor repair, ifc_A0/A1 seed 1) | PENDING | 0:00 | (Priority) |
| `89209` | r2s3_lf_train_signal-B3 (anchor repair, ifc_A0/A1 seed 2) | PENDING | 0:00 | (Priority) |
| `89210` | r2s2_stacked-B1 (anchor repair, ifc_poisson seed 0) | PENDING | 0:00 | (Priority) |
| `89211` | r2s2_stacked-B1 (anchor repair, ifc_poisson seed 1) | PENDING | 0:00 | (Priority) |

No round-3 batch-1 experiment jobs are running or pending — all batch-1 SLURM compute for r3s1/r3s2/r3s3/r3s4 landed by 2026-08-08T20:38:04Z.
The only live jobs in the round are the 11 STOP-THE-LINE #2 anchor repair jobs above, all submitted 2026-08-09T20:13:24, all still PENDING(Priority) ~7h05m later.
Cluster-wide congestion context: `squeue` currently shows 299 jobs on the `gpu` partition and 1331 on `expansion` across all users — consistent with ordinary priority queueing, not an error or dependency block.

## Completed cards
| Card | Type | Panel geomean skill (±CI) | Falsification verdict | Tools promoted |
|---|---|---|---|---|
| r3s3_lf_value-B1 | model (lever) | **11.0789** (ci95 [10.8445, 11.2471], 3-seed 5-ds panel) | **confirmed** — coverage channel (supply of distinct condition rows), not optimization channel, explains the LF-at-train benefit. vs-anchor delta -10.14% (ifc_poisson -38.97%) recorded on the card as a **stale-checkpoint anchor artefact (STOP-THE-LINE #2)**, not a real effect — do not cite as a claim; will be recomputed once the anchor repair lands. | `response_decomposition.py`, `stale_checkpoint_audit.py` |

r3s2_field_reach-B1 has all 3 seeds' raw results landed (10.7213 / 10.3180 / 17.8277) — analyzer write-back withheld under HOLD, card not yet `complete`.
r3s4_audit-B1 has all 3 seeds' raw results landed (19.4235 / 19.5760 / 19.9318) and the certifier is COMPLETED (D2-D4 landed, provisional) — analyzer write-back withheld under HOLD, card not yet `complete`.
r3s1_factorised-B1 has no `5_actual_result` yet — main leg cache-served, guard leg COMPLETED — analyzer stage withheld under HOLD.

## Flags

- **STOP-THE-LINE #2 — stale-checkpoint anchor contamination, HOLD ACTIVE, repair now EXECUTING (see banner at top of this file).** `state/HOLD.json` itself unchanged (`set_at` 2026-08-08T19:51:50Z, not cleared). Operator adjudication ("continue", 2026-08-09) accepted the on-file repair plan; commit `3fd7388`: 89-path quarantine done, 11 `r3RPR-*` fresh-train jobs submitted (89201-89211, all PENDING(Priority)), permanent `stale_gate()` check wired into `tools/make_round3_anchors.py`. Remaining: jobs land → `--fail-on-stale` re-audit → audit-gated anchor rebuild → r3s3-B1 delta recompute → HOLD clear → dispatch withheld r3s1/r3s2/r3s4 analyzer stages.
- **Scheduler job-ID space reset.** Cluster `central`'s job-ID space reset since 2026-08-08 — prior round jobs were 66xxxxxx (last round-3 job 66928386), the repair jobs are 5-digit 892xx (89201-89211). `sacct` resolves both ranges without ambiguity (confirmed this walk).
- **Queue congestion.** The 11 repair jobs have been PENDING(Priority) for ~7h05m as of this walk — cluster-wide `squeue` shows 299 jobs on `gpu` and 1331 on `expansion` across all users. Not a stall; watch next cycle for job starts.
- **r3s1/r3s2/r3s4 analyzer stages remain correctly withheld.** `current_stage.txt` unchanged for all three (`slurm-seed0`, `slurm-seeds12`, `certify`) — this is deliberate orchestrator policy per the HOLD, confirmed not to have advanced prematurely this cycle.
- **r3s3_lf_value-B1: `status: complete`, unchanged this cycle.** Two tools promoted (`response_decomposition.py`, `stale_checkpoint_audit.py`), both verified in `tools/index.md`. `guard_flags: ["heat_local"]` carried forward, unexplained but not gating. `next_direction` recorded for batch 2: LF-condition-row-count sweep on ch + ifc_heat, fixing the per-rung scaler bug, dropping ifc_poisson as a probe. **This card's own vs-anchor deltas remain flagged as anchor artefacts pending the repair.**
- **r3s1_factorised-B1 main seed-0 leg is cache-served, not a fresh run** (`66829977` completed in 7s, `epochs: 0`, `code_hash` unchanged) — expected caching behavior per `eval/score.py`, not a defect.
- **Eval-tree hygiene — resolved for all 4 streams, convention codified in `subagents/experiment-builder.md:218`.** No open items.
- **ADR r3-0005 (pfc spectral-rung repair) — still PROPOSED, blocking on operator + mentor sign-off.** Unchanged this cycle.
- **Gates** (`state/gates.md`): G1-r3 **GREEN** (2026-08-05, data), G2-r3 **GREEN** (2026-08-07, 5-ds preflight), G3-r3 **GREEN** (2026-08-07, 5-ds anchor re-aggregation, best-floor 34.4198) — file unchanged this cycle (pre-dates STOP-THE-LINE #2), **but read G3 alongside the HOLD**: its ifc_poisson anchor evidence remains under active dispute with a repair now in flight (not a gate-file edit — maintainer is read-only for gates).
- **Reopen candidates**: none (`reopen_candidate: false` on all 4 batch-1 cards).
- **blocked.md**: none found under any stream directory.
- **Abandoned streams**: none. All 4 streams are on batch 1, all actively progressing or complete. The 3-consecutive-skipped/blocked cap does not apply this early. No `state/streams/{stream}.json` markers exist (directory still does not exist).
- **Transcripts inbox**: empty — nothing to archive this run.
- **Timing ledger**: 12 entries, unchanged this cycle (no new COMPLETED jobs to upsert — the 11 repair jobs are all still PENDING).
- **Watch for next cycle**: the 11 `r3RPR-*` repair jobs starting/completing (queue congestion permitting); once they land, the sequence is `--fail-on-stale` re-audit → anchor rebuild → r3s3-B1 delta recompute → HOLD clear → dispatch of the withheld r3s1/r3s2/r3s4 analyzer stages.

Maintained by the maintainer cron.
