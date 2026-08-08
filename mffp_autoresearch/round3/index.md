# MFFP Autoresearch Round 3 — Dashboard (updated 2026-08-08T17:19:30Z)

## Status: r3s1 debugger FIXED + RELAUNCHED (debug attempt 1/5, guard leg back in flight) — r3s2/r3s3 still RUNNING, r3s4 certifier still PENDING

Since the last maintainer snapshot (2026-08-08T16:59:30Z), one delta landed.

1. **r3s1_factorised-B1: debug attempt 1 of 5 landed FIXED + RELAUNCHED.**
   Root cause: the vendored `DirectionBank` (method-of-snapshots POD) keeps every mode with `s > sqrt(eps)*s_max` — the numerical-accuracy boundary itself, with zero safety margin.
   `heat_local`'s DC-removed guard-field spectrum crosses `s/s_max ≈ 1e-5` at mode ~19, leaving modes 19-33 numerically undetermined, so the reconstructed rows failed the orthonormality assertion (`max|DD'-I| = 8.351e-01`).
   Fix (commit `3e06423`, child of `6770381`, confirmed via the worktree's own git log): adds `orthonormal_prefix_rank(D, tol)` to `models_r3/r3s1_twostage_crosscoef/basis.py` only — truncates to the longest leading block meeting the SAME 1e-8 tolerance before asserting; tolerance unchanged, assertion still fires verbatim if fewer than 1 mode survives.
   Applied to `WindowBasis` too (same latent defect, previously silent).
   Proven a bitwise no-op wherever the bank already passed: bank-level bitwise equality on all 5 scored cells plus `fluid`/`sharp__sod_1d` guards, and a full 5-cell rescore (`cached=False`, code_hash invalidated) reproducing geomean **25.06624704883453** bit-identical to the reviewed evidence.
   Only `heat_local` truncates (bank 34→19, window 32→18).
   Guard leg relaunched as job `66922977` (`r3-r3s1_factorised-B1-guard-s0`), submitted 2026-08-08T10:05 PDT — confirmed live via `squeue`+`sacct`+`scontrol` this walk, `gpu` partition, `cpu=4/mem=32G/gres:nvidia_h200=1`, `PENDING (Priority)`.
   Card `debug_notes` now holds 1 entry (attempt 1, class ALGO); `job_ids` has 3 entries (seed-0 main `66829977` COMPLETED, guard `66829978` FAILED, guard-relaunch `66922977` PENDING); card `status` → `running`, stage reverted to `slurm-seed0` (`state/r3s1_factorised/current_stage.txt`).
   Debugger's next-hypothesis note (for future reference if the relaunch fails again): suspect an index/arity assumption downstream in `stage2.py`/`discriminator.py` — a 19-direction bank no longer binds `select_max=32`/`stage2_max_directions=50` — not the POD itself.

2. **r3s2_field_reach-B1 seed 0 (`66832670`) and r3s3_lf_value-B1 seeds 1-2 (`66879960`/`66879961`) still RUNNING, unchanged.**
   Elapsed 00:33:59 / 00:33:27 / 00:33:27 at this walk, `.err` files present and empty on all three — no faults.

3. **r3s4_audit-B1 certifier (`66921555`) still PENDING, unchanged.**
   `expansion` partition, CPU-only (`cpu=4/mem=32G`, no `gres`), submitted 2026-08-08T09:54:57 local.

No card fields were modified by this maintainer run. `git status --short experiment_cards/` is clean — the r3s1 debug-note/job_ids/status writes are the debugger/orchestrator's own already-committed change (commit `ad0f2a2`), not touched by this maintainer.

All three launch gates remain **GREEN** on the 5-dataset scored panel (`state/gates.md`, unchanged since 2026-08-07T12:17Z certification): **G1-r3 GREEN**, **G2-r3 GREEN**, **G3-r3 GREEN**. ADR r3-0005 (pfc spectral-rung repair) remains **PROPOSED**, unchanged, still awaiting operator + mentor sign-off. No new ADR this cycle, no new HOLD entries.

**Program:** `program.md` · **Config:** `project.yaml` · **ADRs:** `docs/adr/` (0001 launch panel + A1, 0002 pfc crystalline box, 0003 estimator-integrity repairs, 0004 pfc report-only, 0005 pfc spectral-rung repair — PROPOSED) · **Card schema:** `experiment_cards/SCHEMA.md` · **Runbook:** `HOW_TO_LAUNCH.md`

## Streams
| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r3s1_factorised (gap) | 5-ds best-floor geomean 34.4198 | 1 | r3s1_factorised-B1 | `running`; main leg COMPLETED (cache-served, panel geomean 25.0662), guard leg FIXED + RELAUNCHED post debug attempt 1/5; stage=**slurm-seed0** | seed 0 main: `66829977` COMPLETED (0:07); guard (orig): `66829978` FAILED (0:12, exit 1, direction-bank orthonormality assertion on heat_local); guard (relaunch): `66922977`, **PENDING (Priority)** | debug attempt 1/5 FIXED + RELAUNCHED (commit `3e06423`, job `66922977` submitted 10:05 PDT) — new this cycle |
| r3s2_field_reach (gap) | 5-ds best-floor geomean 34.4198 | 1 | r3s2_field_reach-B1 | `submitted_seed0`; stage=slurm-seed0 | seed 0: job `66832670` (`r3-r3s2_field_reach-B1-s0`, `gpu`, `nvidia_h200=1`), **RUNNING** (00:33:59, node hpc-sm-02-04) | unchanged — still RUNNING |
| r3s3_lf_value (lever) | 5-ds best-floor geomean 34.4198 | 1 | r3s3_lf_value-B1 | `analyzing`; seed 0 COMPLETED + initial-analysis landed (panel geomean **10.8445**, verdict `proceed_to_seeds_1_2`, falsification **confirmed**); stage=slurm-seeds12 | seed 0: `66825323` COMPLETED (150m15s); seeds 1-2: `66879960`/`66879961` (`r3-r3s3_lf_value-B1-s{1,2}`), **RUNNING** (00:33:27, node hpc-sm-02-03) | unchanged — still RUNNING |
| r3s4_audit (diag) | 5-ds best-floor geomean 34.4198 | 1 | r3s4_audit-B1 | `analyzing`; **all 3 seeds COMPLETED** (geomeans 19.4235 / 19.5760 / 19.9318); stage=**certify** | seed 0: `66826610` COMPLETED (6m46s); seed 1: `66879667` COMPLETED (3m16s); seed 2: `66879668` COMPLETED (3m13s); certifier: `66921555` (`r3-r3s4_audit-B1-certify`), **PENDING (Priority)**, `expansion` partition (CPU-only, no GPU) | unchanged — certifier still PENDING |

Per-dataset best-floor skills (5-ds scored panel): allen_cahn_2d 475.8568 (nn_condition), fisher_kpp_2d 390.7015 (train_mean), cahn_hilliard 23.1803 (nn_condition), ifc_poisson 8.0409 (nn_condition), ifc_heat 1.3941 (nn_condition). pfc 48.0773 (train_mean) is **report-only**, excluded from the geomean per ADR r3-0004 (pending possible reinstatement under ADR r3-0005 — still PROPOSED, no sign-off).
Source: `state/anchors/launch_anchors.json` (re-aggregated 2026-08-07 ~19:17Z; unchanged this cycle).

## Running / pending jobs
| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| 66922977 | r3s1_factorised-B1 (guard relaunch, seed 0) | PENDING | 00:00:00 | `(Priority)`, partition `gpu`, `cpu=4/mem=32G/gres:nvidia_h200=1` — `r3-r3s1_factorised-B1-guard-s0` |
| 66921555 | r3s4_audit-B1 (certify D2-D4) | PENDING | 00:00:00 | `(Priority)`, partition `expansion`, `cpu=4/mem=32G`, no GPU — `r3-r3s4_audit-B1-certify` |
| 66832670 | r3s2_field_reach-B1 (seed 0) | RUNNING | 00:33:59 | node `hpc-sm-02-04`, partition `gpu`, `cpu=4/mem=32G/gres:nvidia_h200=1` — `r3-r3s2_field_reach-B1-s0` |
| 66879960 | r3s3_lf_value-B1 (seed 1) | RUNNING | 00:33:27 | node `hpc-sm-02-03`, partition `gpu`, `cpu=4/mem=32G/gres:nvidia_h200=1` — `r3-r3s3_lf_value-B1-s1` |
| 66879961 | r3s3_lf_value-B1 (seed 2) | RUNNING | 00:33:27 | node `hpc-sm-02-03`, partition `gpu`, `cpu=4/mem=32G/gres:nvidia_h200=1` — `r3-r3s3_lf_value-B1-s2` |

`66829977` (r3s1 seed 0 main) COMPLETED and `66829978` (r3s1 original guard) FAILED — dropped from this table, superseded by relaunch `66922977` (see Streams row + Flags). `66826610`, `66879667`, `66879668` (r3s4 seeds 0-2) dropped — all COMPLETED (see Streams row + timing ledger).

## Completed cards
| Card | Type | Panel geomean skill (±CI) | Falsification verdict | Tools promoted |
|---|---|---|---|---|
| — | — | — | — | none — no card has completed all 3 seeds + final review/certify yet. r3s3_lf_value-B1 has seed-0-only `5_actual_result` (panel geomean 10.8445, `ci95: null`, seeds 1-2 still RUNNING). r3s4_audit-B1 has all 3 seeds' raw results landed (19.4235 / 19.5760 / 19.9318) but the card's `5_actual_result.panel_geomean_skill` is still seed-0-only pending the certifier job (`66921555`, PENDING); `6_analysis`/`7_gap_and_future` are `null` on both. |

## Flags

- **r3s1_factorised-B1: debug attempt 1 of 5 FIXED + RELAUNCHED (cap `slurm_algo_attempts: 5`, 1 attempt used).** Root cause: POD rank cut sitting exactly on the numerical accuracy boundary; `heat_local`'s spectrum crosses it mid-bank (mode ~19 of 34). Fix is rank-aware truncation with unchanged tolerance (`basis.py` only, commit `3e06423`), proven bitwise no-op on all 5 scored panel cells plus both other guards, panel geomean 25.0662 reproduced bit-identical. Guard leg relaunched as `66922977`, PENDING. Card `status` → `running`, stage → `slurm-seed0`. Watch next cycle for the relaunch's outcome — if it fails again, the debugger's own note flags `stage2.py`/`discriminator.py` index/arity assumptions as the next hypothesis (since the truncated 19-direction bank no longer binds `select_max=32`/`stage2_max_directions=50`).
- **r3s1_factorised-B1 main seed-0 leg is cache-served, not a fresh run.** `66829977` completed in 7s with `epochs: 0` in the result JSON — `code_hash` unchanged since the previously-reviewed evidence, panel geomean skill 25.0662 bit-identical. This is expected caching behavior (per `eval/score.py`'s `(family, dataset, epochs, seed, code_hash)` cache key convention referenced in project CLAUDE.md), not a defect.
- **r3s4_audit-B1: all 3 seeds landed, certifier queued on the `expansion` (CPU-only) partition, still PENDING.** Per-seed panel geomeans 19.4235 / 19.5760 / 19.9318 — tight spread (~2.6% range), consistent with a stable diagnostic result. Certifier job `66921555` will presumably compute the 3-seed CI and run the D2-D4 probes (`cratered_check`, F3/F4 falsification clauses per `pre_directed_certifier_note`).
- **r3s3_lf_value-B1: seed-0 result confirms the card's hypothesis directionally.** `falsification_verdict: confirmed` (not fired) — the coverage channel, not the optimization channel, explains the LF-at-train benefit (97-101% of `E_total` on 10/10 positive cells). One sign inversion flagged: on ifc_poisson the coverage channel actively harms (E_cov = -2.77) on the repaired nested ladder — worth tracking once seeds 1-2 land (still RUNNING) whether this is seed noise or a real per-dataset exception. `guard_flags: ["heat_local"]` carried forward, unexplained, not gating — **note the coincidence with r3s1's guard-leg failure, also on `heat_local`**: different failure mode (ALGO assertion, now fixed, vs. an unexplained guard flag) but same dataset, still worth a cross-stream glance once the r3s1 relaunch and r3s3's seeds 1-2 both land.
- **r3s4_audit-B1: F1 (floor reproduction) FIRED as pre-directed, dual reading.** Known float64/float32 loader-precision seam (stripped-view breach on ifc_heat.nn_condition at 1.11e-9, just over the 1e-9 tol; native-dtype-control breaches on heat_local/sharp__sod_1d up to 7.7e-8) — adjudicated in prior cycles as a documented metrology property, not a defect; no anchor/floor value changed. F2 `not_fired` on both readings. F3/F4 await the certifier (still queued, PENDING).
- **Eval-tree hygiene — resolved for all 4 streams, convention now codified.** r3s1 fixed commit `6770381`; r3s2 fixed commit `d5069a7`; r3s3/r3s4 redirected correctly from the start. The `ROUND2_EVAL_RESULTS`/`ROUND2_EVAL_CACHE` pattern is documented in `subagents/experiment-builder.md:218`. No open items.
- **ADR r3-0005 (pfc spectral-rung repair) — still PROPOSED, blocking on operator + mentor sign-off.** Do not execute without both sign-offs (it amends the frozen round-2 eval convention). Unchanged this cycle.
- **Gates** (`state/gates.md`): G1-r3 **GREEN** (2026-08-05, data), G2-r3 **GREEN** (2026-08-07, 5-ds preflight), G3-r3 **GREEN** (2026-08-07, 5-ds anchor re-aggregation, best-floor 34.4198) — all unchanged this cycle.
- **Reopen candidates**: none (`reopen_candidate: false` on all 4 batch-1 cards).
- **blocked.md**: none found under any stream directory.
- **Abandoned streams**: none. All 4 streams are on batch 1, all actively progressing (1 relaunched post-debug-fix, 2 running, 1 with all 3 seeds landed + certifier queued). The 3-consecutive-skipped/blocked cap does not apply this early. No `state/streams/{stream}.json` markers exist (directory still does not exist).
- **Transcripts inbox**: empty — nothing to archive this run.
- **Timing ledger**: 5 entries, unchanged this cycle (r3s3_lf_value-B1 seed 0 `66825323` 150.25m; r3s4_audit-B1 seed 0 `66826610` 6.77m; r3s1_factorised-B1 seed 0 `66829977` 0.12m cache-served; r3s4_audit-B1 seed 1 `66879667` 3.27m; r3s4_audit-B1 seed 2 `66879668` 3.22m). The FAILED guard leg (`66829978`) is intentionally **not** upserted (ledger upserts COMPLETED jobs only), nor is the still-PENDING relaunch (`66922977`). 5 live jobs (2 PENDING, 3 RUNNING) have not finished.
- **Watch for next cycle**: r3s1's guard-relaunch outcome (`66922977` — PASS clears the failure, a second FAILURE moves to debug attempt 2/5 per the next-hypothesis note above); r3s4's certifier outcome (3-seed CI, F3/F4, `cratered_check`); whether r3s2/r3s3's RUNNING jobs complete; the `heat_local` coincidence between r3s1's guard leg and r3s3's carried-forward guard flag.

Maintained by the maintainer cron.
