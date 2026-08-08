# MFFP Autoresearch Round 3 — Dashboard (updated 2026-08-08T19:19:37Z)

## Status: r3s3 seeds 1-2 COMPLETED and 3-seed initial-analysis LANDED (the round's first full 3-seed card, geomean 11.0789, falsification confirmed) — r3s4 certifier still PENDING, r3s1 guard relaunch still PENDING, r3s2 seeds 1-2 still PENDING

Since the last maintainer snapshot (2026-08-08T17:59:00Z), one delta landed, then advanced further mid-walk.

1. **r3s3_lf_value-B1 seeds 1-2 (`66879960`/`66879961`) COMPLETED, then the 3-seed initial-analysis landed within this same walk.**
   Both jobs: elapsed 02:20:08 / 02:20:09 (~2h20m each), exit `0:0`, `.err` empty, 60/60 legs each.
   Timing ledger upserted with both entries (140.13 / 140.15 min); 6 -> 8 entries.
   Shortly after (mtime 2026-08-08T19:17:33Z, inside this walk's window), the concurrent initial-analysis-3seed subagent rewrote the card's `5_actual_result` (not touched by the maintainer — read-only inspection only, no card writes issued): `seeds_available` -> `[0, 1, 2]`, panel geomean skill per-seed `[10.844515, 11.145049, 11.247141]`, **mean 11.078902**, `ci95 [10.844515, 11.247141]` (percentile bootstrap over the 3 seed-level geomeans — an explicit card note flags these seeds as HF-subset draws, not training-seed bootstrap in the usual sense).
   `cratered_verdict` unchanged: `proceed_to_seeds_1_2`.
   `falsification_verdict`: **confirmed** (carried through from the seed-0 reading, now corroborated on all 3 seeds) — coverage channel, not optimization channel, explains the LF-at-train benefit.
   `vs_anchor` (own-stream anchor r2s3_lf_train_signal-B3, 12.3288 [11.9785, 12.679]): delta **-10.14%**, beyond the anchor CI and beyond the certified panel noise floor (1.09x), but **entirely attributable to one dataset** — ifc_poisson (-38.97%, non-overlapping CI bands, 3.95x tau_d); ac/fk/ch/ifc_heat all overlap the anchor. Neither this card's A1_lf_all nor A0_nolf arm beats ifc_poisson's mandatory affine_on_hf_train floor.
   `guard_flags` unchanged: `["heat_local"]` (unexplained but not gating — r3s2's own heat_local guard leg ran clean, isolating this to r3s3, not dataset-wide).
   `status` still `analyzing`, `current_stage.txt` still reads `initial-analysis-3seed` (mtime 19:05:09Z) — `6_analysis`/`7_gap_and_future` are still `null`; the analyzer had not yet advanced the card to its next stage as of this walk's close.

Unchanged this cycle:

2. **r3s4_audit-B1 certifier (`66921555`) still PENDING.**
   `expansion` partition, CPU-only (`cpu=4/mem=32G`, no `gres`), submitted 2026-08-08T09:54:57 local — same `Reason=Priority`, `AllocTRES=(null)` as last cycle.

3. **r3s1_factorised-B1 guard relaunch (`66922977`) still PENDING.**
   `gpu` partition, `cpu=4/mem=32G/gres:nvidia_h200=1`, submitted 2026-08-08T10:05:31 local — unchanged.

4. **r3s2_field_reach-B1 seeds 1-2 (`66928385`/`66928386`) still PENDING.**
   `gpu` partition, `cpu=8/mem=64G/gres:nvidia_h200=1` each, submitted 2026-08-08T10:44:24 local — unchanged.

No card fields were modified by this maintainer run (`git status --short experiment_cards/` shows only the initial-analyzer's own concurrent write to r3s3_lf_value-B1, mtime inside this walk but not a maintainer write).

All three launch gates remain **GREEN** on the 5-dataset scored panel (`state/gates.md`, unchanged since 2026-08-07T12:17Z certification): **G1-r3 GREEN**, **G2-r3 GREEN**, **G3-r3 GREEN**. ADR r3-0005 (pfc spectral-rung repair) remains **PROPOSED**, unchanged, still awaiting operator + mentor sign-off. No new ADR this cycle, no new HOLD entries.

**Program:** `program.md` · **Config:** `project.yaml` · **ADRs:** `docs/adr/` (0001 launch panel + A1, 0002 pfc crystalline box, 0003 estimator-integrity repairs, 0004 pfc report-only, 0005 pfc spectral-rung repair — PROPOSED) · **Card schema:** `experiment_cards/SCHEMA.md` · **Runbook:** `HOW_TO_LAUNCH.md`

## Streams
| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r3s1_factorised (gap) | 5-ds best-floor geomean 34.4198 | 1 | r3s1_factorised-B1 | `running`; main leg COMPLETED (cache-served, panel geomean 25.0662), guard leg FIXED + RELAUNCHED post debug attempt 1/5; stage=slurm-seed0 | seed 0 main: `66829977` COMPLETED (0:07); guard (orig): `66829978` FAILED (0:12, exit 1, direction-bank orthonormality assertion on heat_local); guard (relaunch): `66922977`, **PENDING (Priority)** | unchanged — guard relaunch still PENDING |
| r3s2_field_reach (gap) | 5-ds best-floor geomean 34.4198 | 1 | r3s2_field_reach-B1 | `analyzing`; seed-0 initial-analysis landed (panel geomean **10.7213**, verdict `proceed_to_seeds_1_2`, F1 does-not-fire, F2 fires as pre-registered); stage=slurm-seeds12 | seed 0: `66832670` COMPLETED (00:44:20); seeds 1-2: `66928385`/`66928386` (`r3-r3s2_field_reach-B1-s{1,2}`), **PENDING (Priority)** | unchanged — seeds 1-2 still PENDING |
| r3s3_lf_value (lever) | 5-ds best-floor geomean 34.4198 | 1 | r3s3_lf_value-B1 | `analyzing`; **all 3 seeds COMPLETED + 3-seed panel geomean landed** (per-seed [10.8445, 11.1450, 11.2471], mean **11.0789**, ci95 [10.8445, 11.2471]); `falsification_verdict` **confirmed**; vs-anchor delta -10.14% (driven entirely by ifc_poisson); stage=initial-analysis-3seed | seed 0: `66825323` COMPLETED (150m15s); seeds 1-2: `66879960`/`66879961` (`r3-r3s3_lf_value-B1-s{1,2}`), **COMPLETED this cycle** (02:20:08 / 02:20:09, exit 0:0, 60 legs each) | **new this cycle — the round's first full 3-seed card; 3-seed panel geomean + falsification verdict landed mid-walk; `6_analysis`/`7_gap_and_future` still pending** |
| r3s4_audit (diag) | 5-ds best-floor geomean 34.4198 | 1 | r3s4_audit-B1 | `analyzing`; **all 3 seeds COMPLETED** (geomeans 19.4235 / 19.5760 / 19.9318); stage=certify | seed 0: `66826610` COMPLETED (6m46s); seed 1: `66879667` COMPLETED (3m16s); seed 2: `66879668` COMPLETED (3m13s); certifier: `66921555` (`r3-r3s4_audit-B1-certify`), **PENDING (Priority)**, `expansion` partition (CPU-only, no GPU) | unchanged — certifier still PENDING |

Per-dataset best-floor skills (5-ds scored panel): allen_cahn_2d 475.8568 (nn_condition), fisher_kpp_2d 390.7015 (train_mean), cahn_hilliard 23.1803 (nn_condition), ifc_poisson 8.0409 (nn_condition), ifc_heat 1.3941 (nn_condition). pfc 48.0773 (train_mean) is **report-only**, excluded from the geomean per ADR r3-0004 (pending possible reinstatement under ADR r3-0005 — still PROPOSED, no sign-off).
Source: `state/anchors/launch_anchors.json` (re-aggregated 2026-08-07 ~19:17Z; unchanged this cycle).

## Running / pending jobs
| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| 66922977 | r3s1_factorised-B1 (guard relaunch, seed 0) | PENDING | 00:00:00 | `(Priority)`, partition `gpu`, `cpu=4/mem=32G/gres:nvidia_h200=1` — `r3-r3s1_factorised-B1-guard-s0` |
| 66928385 | r3s2_field_reach-B1 (seed 1) | PENDING | 00:00:00 | `(Priority)`, partition `gpu`, `cpu=8/mem=64G/gres:nvidia_h200=1` — `r3-r3s2_field_reach-B1-s1` |
| 66928386 | r3s2_field_reach-B1 (seed 2) | PENDING | 00:00:00 | `(Priority)`, partition `gpu`, `cpu=8/mem=64G/gres:nvidia_h200=1` — `r3-r3s2_field_reach-B1-s2` |
| 66921555 | r3s4_audit-B1 (certify D2-D4) | PENDING | 00:00:00 | `(Priority)`, partition `expansion`, `cpu=4/mem=32G`, no GPU — `r3-r3s4_audit-B1-certify` |

`66879960`/`66879961` (r3s3 seeds 1-2) dropped from this table this cycle — COMPLETED (02:20:08 / 02:20:09, exit 0:0). `66832670` (r3s2 seed 0), `66829977`/`66829978` (r3s1 seed 0 main/original guard), `66826610`/`66879667`/`66879668` (r3s4 seeds 0-2), `66825323` (r3s3 seed 0) remain dropped from prior cycles (all COMPLETED/FAILED, superseded, or certified — see Streams row + timing ledger).

## Completed cards
| Card | Type | Panel geomean skill (±CI) | Falsification verdict | Tools promoted |
|---|---|---|---|---|
| — | — | — | — | none — no card has reached final review/certify with `6_analysis`/`7_gap_and_future` populated yet. r3s3_lf_value-B1 now has its full 3-seed `5_actual_result` landed (panel geomean **11.0789**, ci95 [10.8445, 11.2471], `falsification_verdict: confirmed`) but `6_analysis`/`7_gap_and_future` are still `null` and `status` is still `analyzing` (stage `initial-analysis-3seed`) — not yet a completed card. r3s2_field_reach-B1 has seed-0-only `5_actual_result` (panel geomean 10.7213, `ci95: null`, seeds 1-2 still PENDING). r3s4_audit-B1 has all 3 seeds' raw results landed (19.4235 / 19.5760 / 19.9318) but is pending the certifier job (`66921555`, PENDING). |

## Flags

- **r3s3_lf_value-B1: 3-seed panel geomean + falsification verdict landed this cycle — the round's first full 3-seed card.** Panel geomean **11.0789** (ci95 [10.8445, 11.2471]) vs own-stream anchor 12.3288 [11.9785, 12.679] — delta -10.14%, beyond anchor CI and beyond the certified panel noise floor (1.09x), but **entirely attributable to ifc_poisson** (-38.97%, non-overlapping bands); ac/fk/ch/ifc_heat all overlap the anchor. `falsification_verdict: confirmed` (coverage channel, not optimization channel). `guard_flags: ["heat_local"]` carried forward, unexplained, not gating. Card `status` still `analyzing`, `6_analysis`/`7_gap_and_future` still `null` — watch next cycle for the card to advance past `initial-analysis-3seed`.
- **r3s2_field_reach-B1: seed-0 initial-analysis landed — F1 does not fire, F2 fires (pre-registered modal outcome), seeds 1-2 still PENDING, unchanged since last cycle.** Panel geomean skill **10.7213** (vs. best-floor 34.4198 — well below floor, consistent with r3s3's landed 11.0789 3-seed result on the same panel). Guard panel geomean skill 0.2424, `guard_flags: []`.
- **r3s1_factorised-B1: debug attempt 1 of 5 FIXED + RELAUNCHED (cap `slurm_algo_attempts: 5`, 1 attempt used), guard relaunch (`66922977`) still PENDING, unchanged since last cycle.** Root cause: POD rank cut sitting exactly on the numerical accuracy boundary; `heat_local`'s spectrum crosses it mid-bank (mode ~19 of 34). Fix is rank-aware truncation with unchanged tolerance (`basis.py` only, commit `3e06423`), proven bitwise no-op on all 5 scored panel cells plus both other guards, panel geomean 25.0662 reproduced bit-identical.
- **r3s1_factorised-B1 main seed-0 leg is cache-served, not a fresh run.** `66829977` completed in 7s with `epochs: 0` in the result JSON — `code_hash` unchanged since the previously-reviewed evidence, panel geomean skill 25.0662 bit-identical. Expected caching behavior (per `eval/score.py`'s cache-key convention), not a defect.
- **r3s4_audit-B1: all 3 seeds landed, certifier queued on the `expansion` (CPU-only) partition, still PENDING, unchanged since last cycle.** Per-seed panel geomeans 19.4235 / 19.5760 / 19.9318 — tight spread (~2.6% range), consistent with a stable diagnostic result. Certifier job `66921555` will presumably compute the 3-seed CI and run the D2-D4 probes (`cratered_check`, F3/F4 falsification clauses).
- **r3s4_audit-B1: F1 (floor reproduction) FIRED as pre-directed, dual reading.** Known float64/float32 loader-precision seam (stripped-view breach on ifc_heat.nn_condition at 1.11e-9, just over the 1e-9 tol; native-dtype-control breaches on heat_local/sharp__sod_1d up to 7.7e-8) — adjudicated in prior cycles as a documented metrology property, not a defect; no anchor/floor value changed. F2 `not_fired` on both readings. F3/F4 await the certifier (still queued, PENDING).
- **Eval-tree hygiene — resolved for all 4 streams, convention now codified.** r3s1 fixed commit `6770381`; r3s2 fixed commit `d5069a7`; r3s3/r3s4 redirected correctly from the start. The `ROUND2_EVAL_RESULTS`/`ROUND2_EVAL_CACHE` pattern is documented in `subagents/experiment-builder.md:218`. No open items.
- **ADR r3-0005 (pfc spectral-rung repair) — still PROPOSED, blocking on operator + mentor sign-off.** Do not execute without both sign-offs (it amends the frozen round-2 eval convention). Unchanged this cycle.
- **Gates** (`state/gates.md`): G1-r3 **GREEN** (2026-08-05, data), G2-r3 **GREEN** (2026-08-07, 5-ds preflight), G3-r3 **GREEN** (2026-08-07, 5-ds anchor re-aggregation, best-floor 34.4198) — all unchanged this cycle.
- **Reopen candidates**: none (`reopen_candidate: false` on all 4 batch-1 cards).
- **blocked.md**: none found under any stream directory.
- **Abandoned streams**: none. All 4 streams are on batch 1, all actively progressing (1 awaiting guard relaunch, 1 seed-0 analyzed + seeds 1-2 PENDING, 1 with all 3 seeds landed + 3-seed panel geomean/falsification landed, 1 with all 3 seeds landed + certifier queued). The 3-consecutive-skipped/blocked cap does not apply this early. No `state/streams/{stream}.json` markers exist (directory still does not exist).
- **Transcripts inbox**: empty — nothing to archive this run.
- **Timing ledger**: 8 entries (2 new this cycle). New: r3s3_lf_value-B1 seed 1 `66879960` 140.13m, seed 2 `66879961` 140.15m. Prior 6 unchanged: r3s3_lf_value-B1 seed 0 `66825323` 150.25m; r3s4_audit-B1 seed 0 `66826610` 6.77m; r3s1_factorised-B1 seed 0 `66829977` 0.12m cache-served; r3s4_audit-B1 seed 1 `66879667` 3.27m; r3s4_audit-B1 seed 2 `66879668` 3.22m; r3s2_field_reach-B1 seed 0 `66832670` 44.33m. The FAILED guard leg (`66829978`) remains intentionally **not** upserted (ledger upserts COMPLETED jobs only), nor are the still-PENDING jobs (`66922977`, `66921555`, `66928385`, `66928386`).
- **Watch for next cycle**: r3s3's card advancing past `initial-analysis-3seed` (`6_analysis`/`7_gap_and_future`, `status` change); r3s2's seeds 1-2 (`66928385`/`66928386`, PENDING); r3s1's guard-relaunch outcome (`66922977`); r3s4's certifier outcome (3-seed CI, F3/F4, `cratered_check`).

Maintained by the maintainer cron.
