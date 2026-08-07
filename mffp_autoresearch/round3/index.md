# MFFP Autoresearch Round 3 — Dashboard (updated 2026-08-07T19:20:13Z)

## HOLD CLEARED 2026-08-07T19:17:33Z — pfc moved to report-only (ADR r3-0004), scored panel now 5 datasets

The HOLD set at 17:55:00Z (pfc scored-cell task-void: eval scores pfc at l2(64²)→l3(128²), where the ADR r3-0002 crystalline-box fields are spectrally converged — all 100 test rows task-void, gap ≤1.66e-6; certified 0.018257 reference was ~100% linear-interpolation artifact of the frozen ADR r2-0001 lift, not fidelity gap) was **cleared during this maintainer run** on operator adjudication ("proceed with plan").
**ADR r3-0004** (`docs/adr/0004-pfc-report-only.md`, accepted): `sharp__phase_field_crystal_2d` moves to **report-only** (same status as `ext__helmholtz_2d`) — models may still run it, cells appear flagged non-scoring, it does not enter the panel geomean or any claim clause.
**Scored panel is now 5 datasets**: `sharp__allen_cahn_2d`, `sharp__fisher_kpp_2d`, `sharp__cahn_hilliard`, `ifc_poisson`, `ifc_heat`.
Anchors re-aggregated over the 5-dataset panel (per-cell values unchanged, pfc columns dropped from geomeans) — best-floor lineage **75.0673 → 38.6300 → 36.3912 → 34.4198**.
All 3 drafted batch-1 cards have been patched by the orchestrator with an `adr_r3_0004_addendum` field: `recipe.datasets` replaced with the explicit 5-name panel (pfc removed; the literal `"panel"` value used to resolve to the *round-2* panel via `round2/project.yaml` — an r3s3-B1 brainstormer finding, now fixed on these cards); pfc-citing falsification clauses voided for claim purposes; locked brainstormer prose left untouched.
A separate draft ADR (coarse-rung scoring + spectral-lift reference, the "proper repair") is prepared but **not executed** — pending operator + mentor sign-off; if ratified, pfc can rejoin the scored panel mid-round.
HF release: pfc arrays ship unchanged (correct physics); dataset card/DEFECT_STATUS to document the top-rung convergence.

All three gates are GREEN again on the 5-dataset panel (`state/gates.md`, re-certified 2026-08-07): **G1-r3 GREEN**, **G2-r3 GREEN** (`preflight_launch_5ds_2026-08-07.json` PASS), **G3-r3 GREEN** (all 4 anchor-family cards CERTIFIED on the 5-ds re-aggregation).
**Builders now dispatched at the agent level** for r3s1/r3s2/r3s4, and the r3s3 starter has been dispatched (per orchestrator commit `873075c`, landed 2026-08-07T19:19:30Z, ~1 min after this maintainer's prior snapshot) — but **no SLURM job has appeared yet**: all 3 cards still show `status: drafted`, `job_ids: []` as of 19:20:13Z, and `squeue`/`sacct` show no `r3-*` experiment jobs. Expect status/job_ids to update on the next maintainer cycle once builders finish and submit training jobs.

**Program:** `program.md` · **Config:** `project.yaml` · **ADRs:** `docs/adr/` (0001 launch panel + A1, 0002 pfc crystalline box, 0003 estimator-integrity repairs, 0004 pfc report-only) · **Runbook:** `HOW_TO_LAUNCH.md`

## Streams
| Stream | Anchor (skill, best_floor arm) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r3s1_factorised (gap) | 5-ds best-floor geomean 34.4198 | 1 | r3s1_factorised-B1 (`experiment_cards/r3s1_factorised/batch_1/B1.json`) | drafted, not dispatched; ADR r3-0004 addendum applied | none (job_ids: []) | card created 2026-08-07T17:52:11Z; addendum patched ~19:17Z |
| r3s2_field_reach (gap) | 5-ds best-floor geomean 34.4198 | 1 | r3s2_field_reach-B1 (`experiment_cards/r3s2_field_reach/batch_1/B1.json`) | drafted, not dispatched; ADR r3-0004 addendum applied | none (job_ids: []) | card created 2026-08-07T18:06:20Z; addendum patched ~19:17Z |
| r3s3_lf_value (lever) | 5-ds best-floor geomean 34.4198 | 1 | none yet | brainstorm-done; starter still withheld (was under HOLD; HOLD now cleared — expect starter dispatch next cycle) | none | brainstormer report landed (`brainstormer/r3s3_lf_value/batch_1/report.md`); stage file = `brainstorm` |
| r3s4_audit (diag) | 5-ds best-floor geomean 34.4198 | 1 | r3s4_audit-B1 (`experiment_cards/r3s4_audit/batch_1/B1.json`) | drafted, not dispatched; ADR r3-0004 addendum applied | none (job_ids: []) | card created 2026-08-07T17:55:05Z (this card's escalation is what *triggered* the HOLD that ADR r3-0004 now resolves); addendum patched ~19:17Z |

Per-dataset best-floor skills (5-ds scored panel): allen_cahn_2d 475.8568 (nn_condition), fisher_kpp_2d 390.7015 (train_mean), cahn_hilliard 23.1803 (nn_condition), ifc_poisson 8.0409 (nn_condition), ifc_heat 1.3941 (nn_condition). pfc 48.0773 (train_mean) is **report-only**, excluded from the geomean per ADR r3-0004.
Source: `state/anchors/launch_anchors.json` (re-aggregated 2026-08-07, ~19:17Z).

## Running / pending jobs
| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| — | — | — | — | none live: `squeue -u $USER` empty; `sacct` (2-day window) has no `r3-{stream}-B*` entries — builders/starter dispatched at the agent level (orchestrator commit `873075c`) but no SLURM submission observed yet |

## Completed cards
| Card | Type | Panel geomean skill (±CI) | Falsification verdict | Tools promoted |
|---|---|---|---|---|
| — | — | — | — | none — batch 1 has not been scored for any stream |

## Flags

- **Resolved this run**: HOLD (pfc scored-cell task-void) cleared 2026-08-07T19:17:33Z via ADR r3-0004 (operator "proceed with plan"). Gates re-certified GREEN on the 5-dataset scored panel. This is a genuinely concurrent transition observed mid-walk — the maintainer's initial read (started 19:15:22Z) caught the HOLD still active; a re-check at pre-return-checklist time (19:17–19:18Z) caught the clear + card-patch already landed. Dashboard above reflects the final, post-transition state.
- **Follow-up needed**: a spectral-lift-reference repair ADR (the "proper repair" for pfc's rung-scoring convention) is drafted but not yet ratified by operator + mentor — track for a possible mid-round pfc reinstatement to the scored panel.
- **r3s3_lf_value starter**: was deliberately withheld while the HOLD was active; with the HOLD now cleared, the starter should dispatch on the next orchestrator cycle — flagging so the orchestrator doesn't leave it stalled.
- **Reopen candidates**: none (`reopen_candidate: false` on all 3 drafted cards).
- **blocked.md**: none found under any stream directory.
- **Abandoned streams**: none. All 4 streams are still on batch 1 (the 3-consecutive-skipped/blocked cap does not apply this early).
- **HF upload**: was frozen pending adjudication (pfc row + arrays); ADR r3-0004 says pfc arrays ship unchanged with DEFECT_STATUS documentation of the top-rung convergence — confirm this has been actioned.
- **Transcripts inbox**: empty — nothing to archive this run.
- **Timing ledger**: no round-3 experiment `r3-*` jobs exist yet (batch 1 never dispatched); `state/timing_ledger.json` carries only a scope note. The r2-/r3PFC-prefixed jobs visible in `sacct` (66610529–36) are anchor-certification-family jobs, not round-3 experiment cards, and are out of scope for this ledger.

Maintained by the maintainer cron.
