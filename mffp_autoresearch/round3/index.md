# MFFP Autoresearch Round 3 — Dashboard (updated 2026-08-08T17:57:19Z)

## Status: r3s2 seed-0 initial-analysis landed (F1 does not fire, F2 fires, seeds 1-2 dispatched) — r3s3 seeds 1-2 still RUNNING, r3s4 certifier still PENDING, r3s1 guard relaunch still PENDING

Since the last maintainer snapshot (2026-08-08T17:41:00Z), one delta landed.

1. **r3s2_field_reach-B1 seed-0 initial-analysis landed.**
   `status` `submitted_seed0`→`analyzing`.
   `panel_geomean_skill.mean` **10.721262489424966** (5-ds ADR r3-0004 scored panel, `E1_frozen` pre-registered scored arm, seed 0 only, `ci95: null` at n=1) — bit-identical to the value already recorded in the timing ledger.
   `cratered_verdict` `proceed_to_seeds_1_2` (3.21x below the cratered line; lower is better).
   `falsification_verdict` `pending_seeds` at the card level, but the seed-0 clause readings are decisive: **F1 (reach clause) DOES NOT FIRE** — the IC-synthesis effect beats its rescaled `min_claimable_effect` threshold on both surviving datasets (ch 2.46x mce, ac 8.64x mce; pfc voided under ADR r3-0004), and a zero-information shuffled-IC null control (derangement-verified, 0 fixed points) is WORSE than E0 everywhere, confirming the gain is attributable to the real IC channel.
   **F2 (corrector-value clause) FIRES as pre-registered** — the trained stage-2 corrector earns <1.05 skill units against thresholds of 1.74/24.63 on ch/ac (both `beats: false`), matching the card's own part-4 pre-registration verbatim.
   Off-clause note: on ifc_poisson the corrector is worth +83.9 skill units, but a training-free closed-form ladder beats the trained arm there too — no ifc claim available.
   `guard_flags: []` (r3s2's own `heat_local` guard leg ran clean, confirming r3s1's guard-leg ALGO failure two cycles ago is isolated to r3s1's direction-bank code, not dataset-specific).
   Orchestrator submitted seeds 1-2 directly: jobs `66928385`/`66928386` (`r3-r3s2_field_reach-B1-s{1,2}`), submitted 2026-08-08T10:44 PDT, confirmed live via `squeue`+`sacct`+`scontrol` — `gpu` partition, `cpu=8/mem=64G/gres:nvidia_h200=1` (wider request than the other 3 streams' 4/32G, consistent with this card's own recorded ~12.6x over-provisioning note, not a new anomaly), `PENDING (Priority)`.

2. **r3s3_lf_value-B1 seeds 1-2 (`66879960`/`66879961`) still RUNNING, unchanged.**
   Elapsed 01:13:53 / 01:13:53 at this walk (up from 00:54:38 last cycle), `.err` empty on both, `.out` tails show healthy progress into the `A3_lf_uncovered` arm's `cahn_hilliard` d1 leg — no faults, no stall.

3. **r3s4_audit-B1 certifier (`66921555`) still PENDING, unchanged.**
   `expansion` partition, CPU-only (`cpu=4/mem=32G`, no `gres`), submitted 2026-08-08T09:54:57 local.

4. **r3s1_factorised-B1 guard relaunch (`66922977`) still PENDING, unchanged.**
   `gpu` partition, `cpu=4/mem=32G/gres:nvidia_h200=1`, submitted 2026-08-08T10:05:31 local (debug attempt 1/5 fix from two cycles ago).

No card fields were modified by this maintainer run. `git status --short experiment_cards/` shows only the initial-analyzer's own pre-existing write to r3s2_field_reach-B1 (mtime predates this walk).

All three launch gates remain **GREEN** on the 5-dataset scored panel (`state/gates.md`, unchanged since 2026-08-07T12:17Z certification): **G1-r3 GREEN**, **G2-r3 GREEN**, **G3-r3 GREEN**. ADR r3-0005 (pfc spectral-rung repair) remains **PROPOSED**, unchanged, still awaiting operator + mentor sign-off. No new ADR this cycle, no new HOLD entries.

**Program:** `program.md` · **Config:** `project.yaml` · **ADRs:** `docs/adr/` (0001 launch panel + A1, 0002 pfc crystalline box, 0003 estimator-integrity repairs, 0004 pfc report-only, 0005 pfc spectral-rung repair — PROPOSED) · **Card schema:** `experiment_cards/SCHEMA.md` · **Runbook:** `HOW_TO_LAUNCH.md`

## Streams
| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r3s1_factorised (gap) | 5-ds best-floor geomean 34.4198 | 1 | r3s1_factorised-B1 | `running`; main leg COMPLETED (cache-served, panel geomean 25.0662), guard leg FIXED + RELAUNCHED post debug attempt 1/5; stage=slurm-seed0 | seed 0 main: `66829977` COMPLETED (0:07); guard (orig): `66829978` FAILED (0:12, exit 1, direction-bank orthonormality assertion on heat_local); guard (relaunch): `66922977`, **PENDING (Priority)** | unchanged — guard relaunch still PENDING |
| r3s2_field_reach (gap) | 5-ds best-floor geomean 34.4198 | 1 | r3s2_field_reach-B1 | `analyzing`; seed-0 initial-analysis landed (panel geomean **10.7213**, verdict `proceed_to_seeds_1_2`, F1 does-not-fire, F2 fires as pre-registered); stage=slurm-seeds12 (implied by seeds-1-2 dispatch) | seed 0: `66832670` COMPLETED (00:44:20); seeds 1-2: `66928385`/`66928386` (`r3-r3s2_field_reach-B1-s{1,2}`), **PENDING (Priority)** | **new this cycle — initial-analysis landed, seeds 1-2 dispatched** |
| r3s3_lf_value (lever) | 5-ds best-floor geomean 34.4198 | 1 | r3s3_lf_value-B1 | `analyzing`; seed 0 COMPLETED + initial-analysis landed (panel geomean **10.8445**, verdict `proceed_to_seeds_1_2`, falsification **confirmed**); stage=slurm-seeds12 | seed 0: `66825323` COMPLETED (150m15s); seeds 1-2: `66879960`/`66879961` (`r3-r3s3_lf_value-B1-s{1,2}`), **RUNNING** (01:13:53, node hpc-sm-02-03) | unchanged — still RUNNING |
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
| 66879960 | r3s3_lf_value-B1 (seed 1) | RUNNING | 01:13:53 | node `hpc-sm-02-03`, partition `gpu`, `cpu=4/mem=32G/gres:nvidia_h200=1` — `r3-r3s3_lf_value-B1-s1` |
| 66879961 | r3s3_lf_value-B1 (seed 2) | RUNNING | 01:13:53 | node `hpc-sm-02-03`, partition `gpu`, `cpu=4/mem=32G/gres:nvidia_h200=1` — `r3-r3s3_lf_value-B1-s2` |

`66832670` (r3s2 seed 0) dropped from this table this cycle — COMPLETED, superseded by seeds 1-2. `66829977`/`66829978` (r3s1 seed 0 main/original guard), `66826610`/`66879667`/`66879668` (r3s4 seeds 0-2) remain dropped from prior cycles (all COMPLETED/FAILED, superseded, or certified — see Streams row + timing ledger).

## Completed cards
| Card | Type | Panel geomean skill (±CI) | Falsification verdict | Tools promoted |
|---|---|---|---|---|
| — | — | — | — | none — no card has completed all 3 seeds + final review/certify yet. r3s2_field_reach-B1 and r3s3_lf_value-B1 both have seed-0-only `5_actual_result` (panel geomean 10.7213 / 10.8445, `ci95: null`, seeds 1-2 still PENDING/RUNNING). r3s4_audit-B1 has all 3 seeds' raw results landed (19.4235 / 19.5760 / 19.9318) but the card's `5_actual_result.panel_geomean_skill` is still seed-0-only pending the certifier job (`66921555`, PENDING); `6_analysis`/`7_gap_and_future` are `null` on all three. |

## Flags

- **r3s2_field_reach-B1: seed-0 initial-analysis landed — F1 does not fire, F2 fires (pre-registered modal outcome), seeds 1-2 dispatched.** Panel geomean skill **10.7213** (vs. best-floor 34.4198 — well below floor, consistent with r3s3's landed 10.8445 result on the same panel; both LF-value/field-reach streams show similar sub-floor skill so far). Guard panel geomean skill 0.2424, `guard_flags: []` (heat_local guard leg ran clean here, isolating r3s1's ALGO failure to r3s1's own code, not the dataset). Watch next cycle for seeds 1-2 (`66928385`/`66928386`, PENDING) to land and the card-level falsification verdict to finalize.
- **r3s1_factorised-B1: debug attempt 1 of 5 FIXED + RELAUNCHED (cap `slurm_algo_attempts: 5`, 1 attempt used), guard relaunch (`66922977`) still PENDING, unchanged since last cycle.** Root cause: POD rank cut sitting exactly on the numerical accuracy boundary; `heat_local`'s spectrum crosses it mid-bank (mode ~19 of 34). Fix is rank-aware truncation with unchanged tolerance (`basis.py` only, commit `3e06423`), proven bitwise no-op on all 5 scored panel cells plus both other guards, panel geomean 25.0662 reproduced bit-identical. Card `status` → `running`, stage → `slurm-seed0`. Watch next cycle for the relaunch's outcome.
- **r3s1_factorised-B1 main seed-0 leg is cache-served, not a fresh run.** `66829977` completed in 7s with `epochs: 0` in the result JSON — `code_hash` unchanged since the previously-reviewed evidence, panel geomean skill 25.0662 bit-identical. Expected caching behavior (per `eval/score.py`'s cache-key convention), not a defect.
- **r3s4_audit-B1: all 3 seeds landed, certifier queued on the `expansion` (CPU-only) partition, still PENDING, unchanged since last cycle.** Per-seed panel geomeans 19.4235 / 19.5760 / 19.9318 — tight spread (~2.6% range), consistent with a stable diagnostic result. Certifier job `66921555` will presumably compute the 3-seed CI and run the D2-D4 probes (`cratered_check`, F3/F4 falsification clauses).
- **r3s3_lf_value-B1: seed-0 result confirms the card's hypothesis directionally; seeds 1-2 still RUNNING (~74 min elapsed, no faults).** `falsification_verdict: confirmed` (not fired) — the coverage channel, not the optimization channel, explains the LF-at-train benefit (97-101% of `E_total` on 10/10 positive cells). One sign inversion flagged on ifc_poisson (coverage channel harms there), worth tracking once seeds 1-2 land whether this is seed noise or a real per-dataset exception. `guard_flags: ["heat_local"]` carried forward, unexplained, not gating — notably r3s2's own heat_local guard leg ran clean, so this is not a dataset-wide issue.
- **r3s4_audit-B1: F1 (floor reproduction) FIRED as pre-directed, dual reading.** Known float64/float32 loader-precision seam (stripped-view breach on ifc_heat.nn_condition at 1.11e-9, just over the 1e-9 tol; native-dtype-control breaches on heat_local/sharp__sod_1d up to 7.7e-8) — adjudicated in prior cycles as a documented metrology property, not a defect; no anchor/floor value changed. F2 `not_fired` on both readings. F3/F4 await the certifier (still queued, PENDING).
- **Eval-tree hygiene — resolved for all 4 streams, convention now codified.** r3s1 fixed commit `6770381`; r3s2 fixed commit `d5069a7`; r3s3/r3s4 redirected correctly from the start. The `ROUND2_EVAL_RESULTS`/`ROUND2_EVAL_CACHE` pattern is documented in `subagents/experiment-builder.md:218`. No open items.
- **ADR r3-0005 (pfc spectral-rung repair) — still PROPOSED, blocking on operator + mentor sign-off.** Do not execute without both sign-offs (it amends the frozen round-2 eval convention). Unchanged this cycle.
- **Gates** (`state/gates.md`): G1-r3 **GREEN** (2026-08-05, data), G2-r3 **GREEN** (2026-08-07, 5-ds preflight), G3-r3 **GREEN** (2026-08-07, 5-ds anchor re-aggregation, best-floor 34.4198) — all unchanged this cycle.
- **Reopen candidates**: none (`reopen_candidate: false` on all 4 batch-1 cards).
- **blocked.md**: none found under any stream directory.
- **Abandoned streams**: none. All 4 streams are on batch 1, all actively progressing (1 awaiting guard relaunch, 1 seed-0 analyzed + seeds 1-2 dispatched, 1 running seeds 1-2, 1 with all 3 seeds landed + certifier queued). The 3-consecutive-skipped/blocked cap does not apply this early. No `state/streams/{stream}.json` markers exist (directory still does not exist).
- **Transcripts inbox**: empty — nothing to archive this run.
- **Timing ledger**: 6 entries, unchanged this cycle (no new COMPLETED `r3-*` jobs — r3s2 seed 0's value was already upserted last cycle when `66832670` completed). Entries: r3s3_lf_value-B1 seed 0 `66825323` 150.25m; r3s4_audit-B1 seed 0 `66826610` 6.77m; r3s1_factorised-B1 seed 0 `66829977` 0.12m cache-served; r3s4_audit-B1 seed 1 `66879667` 3.27m; r3s4_audit-B1 seed 2 `66879668` 3.22m; r3s2_field_reach-B1 seed 0 `66832670` 44.33m. The FAILED guard leg (`66829978`) is intentionally **not** upserted (ledger upserts COMPLETED jobs only), nor are the still-PENDING/RUNNING jobs (`66922977`, `66921555`, `66928385`, `66928386`, `66879960`, `66879961`).
- **Watch for next cycle**: r3s2's seeds 1-2 (`66928385`/`66928386`, PENDING) and card-level falsification verdict; r3s1's guard-relaunch outcome (`66922977`); r3s4's certifier outcome (3-seed CI, F3/F4, `cratered_check`); whether r3s3's seeds 1-2 (RUNNING ~74 min) complete.

Maintained by the maintainer cron.
