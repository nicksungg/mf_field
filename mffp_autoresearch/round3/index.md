# MFFP Autoresearch Round 3 — Dashboard (updated 2026-08-08T09:58:11Z)

## Status: TWO STREAMS INTO 3-SEED ANALYSIS (r3s3, r3s4) — seed-0 initial results landed, seeds 1-2 dispatched; r3s1/r3s2 still queued at seed-0

Since the last maintainer snapshot (2026-08-08T09:37:49Z), three deltas landed.

1. **r3s3_lf_value-B1 seed-0 initial-analysis landed.**
   `status` `submitted_seed0` → `analyzing`, stage → `slurm-seeds12`.
   Panel geomean skill **10.844515** (primary arm `A1_lf_all`, 5-ds ADR r3-0004 scored panel, seed 0 only).
   `cratered_verdict`: `proceed_to_seeds_1_2`.
   `falsification_verdict`: **confirmed** (E_total exceeds tau_d on 3+ of the 4 threshold-carrying datasets after the ADR r3-0004 pfc-void adjustment; floor-gate passes on every carrier).
   Channel decomposition: the **coverage channel carries 97-101% of the LF-at-train effect** (`E_cov/E_total` in [0.972, 1.013] on 10/10 positive cells), optimization channel contributes <=4.8% on 9/10 cells (ac d2 the one outlier at 7.3%); one sign inversion on ifc_poisson (coverage channel harms there).
   Seeds 1-2 submitted directly: jobs `66879960`/`66879961` (`r3-r3s3_lf_value-B1-s{1,2}`), 2026-08-08T03:35 PDT, confirmed live **PENDING (Priority)**.

2. **r3s4_audit-B1 certifier job (`66826610`) COMPLETED** — 00:06:46 elapsed, exit `0:0`, clean `.err`.
   `state/timing_ledger.json` upserted (elapsed_min 6.77, phase breakdown D0 48s / D1 47.6s / train+eval 186.5s).
   Seed-0 initial-analysis landed in the same walk: `status` → `analyzing`, stage → `initial-analysis`.
   Panel geomean skill **19.423547** (5-ds scored panel).
   `cratered_verdict`: `proceed_to_seeds_1_2`.
   `falsification_verdict`: `pending_seeds` (F3/F4 need 3 seeds) — but the training-free probes already resolved: **F1 (floor reproduction) FIRED** as pre-directed, dual reading (stripped-view carded path: ifc_heat.nn_condition rel_diff 1.11e-9, just over the 1e-9 tol; native-dtype control: heat_local/sharp__sod_1d up to 7.7e-8 rel_diff) — confirmed float64/float32 loader-precision seam on disjoint dataset sets, all other conjuncts pass (geomean6 36.3912, geomean5 34.4198, lineage reproduces).
   **F2 (seam-is-not-real) `not_fired`** on both the scored-only reading (1/3 agree) and as-written incl.-report-only-pfc reading (1/4 agree).
   Seeds 1-2 submitted directly: jobs `66879667`/`66879668` (`r3-r3s4_audit-B1-s{1,2}`), 2026-08-08T03:15 PDT, confirmed live **PENDING (Priority)**.

3. **r3s1 (`66829977`+guard `66829978`) and r3s2 (`66832670`) unchanged, still PENDING (Priority)** — reconfirmed live via `squeue`+`sacct` (liveness lesson applied), no state change since last cycle.

No card fields were modified by this maintainer run. `git status --short experiment_cards/` is clean at the pre-return check; the r3s3/r3s4 deltas above are pre-existing orchestrator/initial-analyzer writes (mtimes ~02:48-02:52 local, predating this run's start), not touched by this maintainer.

All three launch gates remain **GREEN** on the 5-dataset scored panel (`state/gates.md`, unchanged since 2026-08-07T12:17Z certification): **G1-r3 GREEN**, **G2-r3 GREEN**, **G3-r3 GREEN**. ADR r3-0005 (pfc spectral-rung repair) remains **PROPOSED**, unchanged, still awaiting operator + mentor sign-off. No new ADR this cycle, no new HOLD entries.

**Program:** `program.md` · **Config:** `project.yaml` · **ADRs:** `docs/adr/` (0001 launch panel + A1, 0002 pfc crystalline box, 0003 estimator-integrity repairs, 0004 pfc report-only, 0005 pfc spectral-rung repair — PROPOSED) · **Card schema:** `experiment_cards/SCHEMA.md` · **Runbook:** `HOW_TO_LAUNCH.md`

## Streams
| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r3s1_factorised (gap) | 5-ds best-floor geomean 34.4198 | 1 | r3s1_factorised-B1 | reviewed PASS (attempt 2) → submitted_seed0; stage=slurm-seed0 | seed 0: `66829977`; guard leg: `66829978` (both `r3-r3s1_factorised-B1[-guard]-s0`, `gpu`, `nvidia_h200=1`), PENDING (Priority) — unchanged this cycle | attempt-2 PASS (2026-08-08T00:45:40Z); submitted 2026-08-07T19:05 PDT |
| r3s2_field_reach (gap) | 5-ds best-floor geomean 34.4198 | 1 | r3s2_field_reach-B1 | reviewed PASS (attempt 2) → submitted_seed0; stage=slurm-seed0 | seed 0: job `66832670` (`r3-r3s2_field_reach-B1-s0`, `gpu`, `nvidia_h200=1`), PENDING (Priority) — unchanged this cycle | attempt-2 PASS (2026-08-08T01:14:11Z); submitted 2026-08-07T20:20 PDT |
| r3s3_lf_value (lever) | 5-ds best-floor geomean 34.4198 | 1 | r3s3_lf_value-B1 | `analyzing`; seed 0 COMPLETED + initial-analysis landed (panel geomean **10.8445**, verdict `proceed_to_seeds_1_2`, falsification **confirmed**); stage=**slurm-seeds12** | seed 0: `66825323` COMPLETED (150m15s); seeds 1-2: `66879960`/`66879961` (`r3-r3s3_lf_value-B1-s{1,2}`), PENDING (Priority) — new this cycle | seed-0 analysis landed ~09:48Z; seeds 1-2 dispatched 2026-08-08T03:35 PDT — new this cycle |
| r3s4_audit (diag) | 5-ds best-floor geomean 34.4198 | 1 | r3s4_audit-B1 | `analyzing`; seed 0 (certifier) COMPLETED (6m46s) + initial-analysis landed (panel geomean **19.4235**, verdict `proceed_to_seeds_1_2`, F1 **FIRED** as pre-directed, F2 not_fired, F3/F4 pending); stage=**initial-analysis** | seed 0: `66826610` COMPLETED (6m46s); seeds 1-2: `66879667`/`66879668` (`r3-r3s4_audit-B1-s{1,2}`), PENDING (Priority) — new this cycle | seed-0 certifier COMPLETED + analysis landed ~09:52Z; seeds 1-2 dispatched 2026-08-08T03:15 PDT — new this cycle |

Per-dataset best-floor skills (5-ds scored panel): allen_cahn_2d 475.8568 (nn_condition), fisher_kpp_2d 390.7015 (train_mean), cahn_hilliard 23.1803 (nn_condition), ifc_poisson 8.0409 (nn_condition), ifc_heat 1.3941 (nn_condition). pfc 48.0773 (train_mean) is **report-only**, excluded from the geomean per ADR r3-0004 (pending possible reinstatement under ADR r3-0005 — still PROPOSED, no sign-off).
Source: `state/anchors/launch_anchors.json` (re-aggregated 2026-08-07 ~19:17Z; unchanged this cycle).

## Running / pending jobs
| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| 66829977 | r3s1_factorised-B1 (seed 0) | PENDING | 00:00:00 | `(Priority)`, partition `gpu`, `cpu=4/mem=32G/gres:nvidia_h200=1` — `r3-r3s1_factorised-B1-s0` |
| 66829978 | r3s1_factorised-B1 (guard leg, seed 0) | PENDING | 00:00:00 | `(Priority)`, partition `gpu`, `cpu=4/mem=32G/gres:nvidia_h200=1` — `r3-r3s1_factorised-B1-guard-s0` |
| 66832670 | r3s2_field_reach-B1 (seed 0) | PENDING | 00:00:00 | `(Priority)`, partition `gpu`, `cpu=4/mem=32G/gres:nvidia_h200=1` — `r3-r3s2_field_reach-B1-s0` |
| 66879960 | r3s3_lf_value-B1 (seed 1) | PENDING | 00:00:00 | `(Priority)`, partition `gpu`, `cpu=4/mem=32G/gres:nvidia_h200=1` — `r3-r3s3_lf_value-B1-s1` |
| 66879961 | r3s3_lf_value-B1 (seed 2) | PENDING | 00:00:00 | `(Priority)`, partition `gpu`, `cpu=4/mem=32G/gres:nvidia_h200=1` — `r3-r3s3_lf_value-B1-s2` |
| 66879667 | r3s4_audit-B1 (seed 1) | PENDING | 00:00:00 | `(Priority)`, partition `gpu`, `cpu=4/mem=32G/gres:nvidia_h200=1` — `r3-r3s4_audit-B1-s1` |
| 66879668 | r3s4_audit-B1 (seed 2) | PENDING | 00:00:00 | `(Priority)`, partition `gpu`, `cpu=4/mem=32G/gres:nvidia_h200=1` — `r3-r3s4_audit-B1-s2` |

`66825323` (r3s3 seed 0) and `66826610` (r3s4 seed 0) dropped from this table — both COMPLETED (see Streams row and timing ledger).

## Completed cards
| Card | Type | Panel geomean skill (±CI) | Falsification verdict | Tools promoted |
|---|---|---|---|---|
| — | — | — | — | none — no card has completed all 3 seeds / final review yet. r3s3_lf_value-B1 and r3s4_audit-B1 both have seed-0-only `5_actual_result` (panel geomean 10.8445 and 19.4235 respectively, both `ci95: null` pending seeds 1-2) and `6_analysis`/`7_gap_and_future` are still `null`. |

## Flags

- **r3s3_lf_value-B1: seed-0 result confirms the card's hypothesis directionally.** `falsification_verdict: confirmed` (not fired) — the coverage channel, not the optimization channel, explains the LF-at-train benefit (97-101% of `E_total` on 10/10 positive cells). One sign inversion flagged: on ifc_poisson the coverage channel actively harms (E_cov = -2.77) on the repaired nested ladder — worth tracking once seeds 1-2 land whether this is seed noise or a real per-dataset exception. `guard_flags: ["heat_local"]` carried forward, unexplained, not gating.
- **r3s4_audit-B1: F1 (floor reproduction) FIRED as pre-directed, dual reading.** This is the known float64/float32 loader-precision seam (stripped-view breach on ifc_heat.nn_condition at 1.11e-9, just over the 1e-9 tol; native-dtype-control breaches on heat_local/sharp__sod_1d up to 7.7e-8) — adjudicated in prior cycles as a documented metrology property, not a defect; no anchor/floor value changed. F2 `not_fired` on both readings. F3/F4 await seeds 1-2.
- **Both r3s3 and r3s4 now have 2 live SLURM jobs each (seeds 1-2), all PENDING (Priority).** Combined with r3s1 (2 jobs) and r3s2 (1 job), **7 jobs total** are in the SLURM queue this cycle, 0 RUNNING.
- **Two streams still queued at seed-0.** r3s1 (`66829977`+guard `66829978`), r3s2 (`66832670`) confirmed live via `squeue`+`sacct` this cycle (liveness lesson applied), reason `(Priority)`, unchanged since last cycle.
- **float64→float32 loader-precision seam** — previously found by r3s3/r3s4 builders on `affine_on_hf_train` floor reproduction, now also the deciding mechanism for r3s4's F1 FIRE this cycle. Adjudicated as a documented metrology property (strict 1e-9 `seam_check_floors` correctly retained; looser `ANCHOR_AFFINE_TOL=1e-7` sits well above every observed breach, max 7.7e-8). No anchor/floor value changed.
- **Eval-tree hygiene — resolved for all 4 streams, convention now codified.** r3s1 fixed commit `6770381`; r3s2 fixed commit `d5069a7`; r3s3/r3s4 redirected correctly from the start. The `ROUND2_EVAL_RESULTS`/`ROUND2_EVAL_CACHE` pattern is documented in `subagents/experiment-builder.md:218`. No open items.
- **ADR r3-0005 (pfc spectral-rung repair) — still PROPOSED, blocking on operator + mentor sign-off.** Do not execute without both sign-offs (it amends the frozen round-2 eval convention). Unchanged this cycle.
- **Gates** (`state/gates.md`): G1-r3 **GREEN** (2026-08-05, data), G2-r3 **GREEN** (2026-08-07, 5-ds preflight), G3-r3 **GREEN** (2026-08-07, 5-ds anchor re-aggregation, best-floor 34.4198) — all unchanged this cycle.
- **Reopen candidates**: none (`reopen_candidate: false` on all 4 batch-1 cards).
- **blocked.md**: none found under any stream directory.
- **Abandoned streams**: none. All 4 streams are on batch 1; two into 3-seed analysis (seeds 1-2 dispatched, all PENDING), two still queued at seed-0. The 3-consecutive-skipped/blocked cap does not apply this early. No `state/streams/{stream}.json` markers exist (directory still does not exist).
- **Transcripts inbox**: empty — nothing to archive this run.
- **Timing ledger**: 2 entries now (r3s3_lf_value-B1 seed 0, `66825323`, elapsed_min 150.25; r3s4_audit-B1 seed 0, `66826610`, elapsed_min 6.77 — new this cycle). The 7 live seed-1/2/guard jobs have not finished.
- **Watch for next cycle**: whether r3s3/r3s4 seeds 1-2 clear the priority queue and start RUNNING; whether r3s1/r3s2 finally start RUNNING (both have been PENDING (Priority) since 2026-08-07 19:05/20:20 PDT respectively, now over 12h queued — worth flagging to the orchestrator if this persists much longer); r3s3's ifc_poisson coverage-channel sign inversion resolution once 3-seed CI lands.

Maintained by the maintainer cron.
