# MFFP Autoresearch Round 3 — Dashboard (updated 2026-08-08T20:03:00Z)

## STOP-THE-LINE #2 IS ACTIVE — HOLD SET (2026-08-08T19:51:50Z, commit `26089e8`)

Stale-checkpoint anchor contamination.
r3s3_lf_value-B1's mechanism analyzer (turn 2) discovered that the mandated `last.pt` checkpoint-resume contract silently no-op'd several ADR r3-0002/r3-0003 anchor re-scores: the launch-anchor **ifc_poisson** cells for `r2s3_lf_train_signal-B3` (all 6 legs) and `r2s1_direct-B2`/`B3` (all seeds) resumed pre-repair weights (`resumed_from_step=5000`, `train_seconds` 1.3-2.9s, checkpoint mtimes 2026-08-03/04 vs ladder adoption 2026-08-05) and were re-scored on the repaired arrays with stale weights.
`r2s2_stacked-B1` is possibly mixed.
Checkpoints carry no data hash — the sibling gap to the score-cache hole that ADR r3-0003 D4 already closed.

**Blast radius:** `state/anchors/launch_anchors.json` **ifc_poisson columns + panel geomeans are invalid pending repair**.
r3s3-B1's own vs-anchor deltas (-38.97% ifc_poisson, -10.14% panel) are **artefacts of this contamination**, already recorded as such on the card — not real effects.
Round-3's own experiment legs are audited **CLEAN (0/225 stale)** — the contamination is confined to the launch-anchor tree, not batch-1 training.
No queued job depends on the stale cells; **none cancelled**.
The 4 already-queued jobs (certify `66921555`, r3s1 guard relaunch `66922977`, r3s2 seeds `66928385`/`66928386`) are **unaffected by the repair scope and correctly remain queued**.

**Batch advancement and claim adjudication are halted under HOLD.**
Repair plan on file (`state/orchestrator_flow.md` top entry): quarantine stale anchor cells + delete stale checkpoints -> fresh-train those anchor legs with empty checkpoint dirs -> re-audit with `stale_checkpoint_audit.py` -> rebuild anchors -> recompute affected deltas; permanent fix binds data hashes into checkpoints (sixth-class check) run at every anchor certification.
Operator adjudication pending.
The maintainer takes no action on cards or anchors (read-only) — this section exists to surface the HOLD prominently for the orchestrator/operator.

## Status: r3s3_lf_value-B1 reached `status: complete` (first card of the round to finish all 7 parts) — r3s4 certifier, r3s1 guard relaunch, and r3s2 seeds 1-2 all still PENDING, unchanged

Since the last maintainer snapshot (2026-08-08T19:19:37Z):

1. **STOP-THE-LINE #2 / HOLD set** (see banner above) — the round's second stop-the-line event, discovered inside r3s3-B1's own mechanism analysis.
2. **r3s3_lf_value-B1 card completed.** `status` `analyzing` -> `complete`; `6_analysis` and `7_gap_and_future` now populated (both `null` last cycle).
   `current_stage.txt` -> `mechanism-analysis`.
   Three-turn mechanism analysis (`worktrees/r3s3_lf_value/B1/scratchpad/reanalysis_turn_{1,2,3}_results.md`):
   - **Turn 1** — A2_lf_covered is bit-behaviourally the *same learned function* as A0_nolf, not a partial step toward A1 (inter-arm distance D(A2,A1) is *larger* than D(A0,A1) on all 5 scored cells). The coverage-channel effect is an identifiability result (supply of distinct condition rows turns a noisy/misaligned condition-response into a real one), not an optimization/regularization result.
   - **Turn 2** — discovered the stale-checkpoint contamination (see HOLD banner); promoted `tools/stale_checkpoint_audit.py` (positive control 6/12 STALE on the anchor tree, negative control 0/225 on round-3's own legs).
   - **Turn 3 / synthesis** — ifc_poisson's sign inversion (independent of the stale-anchor issue) is a normalisation-matching failure: `per_rung_max` is computed over the rows an arm keeps, producing a ~1.64x mismatch between full-pool and row-matched arms; ifc_poisson is additionally a poor LF-value probe on its own merits (exactly affine in its 5-D condition vector, `affine_on_hf_train` floor 0.057375 unbeaten by any arm here).
   **Two tools promoted**: `tools/response_decomposition.py` (per-arm response amplitude/alignment decomposition — used to show A2≡A0) and `tools/stale_checkpoint_audit.py` (the stale-checkpoint detector) — both filed in `tools/index.md` with verified invocation commands.
   `falsification_verdict` **confirmed** (unchanged from last cycle's 3-seed reading): coverage channel, not optimization channel, explains the LF-at-train benefit.
   `next_direction` for batch 2: sweep `R3S3B1_LF_COND_CAP` over a geometric ladder (5..395 conditions) on cahn_hilliard + ifc_heat, 3 seeds, fixing the per-rung scaler bug and dropping ifc_poisson as an LF-value probe.

Unchanged this cycle:

3. **r3s4_audit-B1 certifier (`66921555`) still PENDING.**
   `expansion` partition, CPU-only (`cpu=4/mem=32G`, no `gres`), submitted 2026-08-08T09:54:57 local.

4. **r3s1_factorised-B1 guard relaunch (`66922977`) still PENDING.**
   `gpu` partition, `cpu=4/mem=32G/gres:nvidia_h200=1`, submitted 2026-08-08T10:05:31 local.

5. **r3s2_field_reach-B1 seeds 1-2 (`66928385`/`66928386`) still PENDING.**
   `gpu` partition, `cpu=8/mem=64G/gres:nvidia_h200=1` each, submitted 2026-08-08T10:44:24 local.

No card fields were modified by this maintainer run (`git status --short experiment_cards/` clean — the r3s3 completion is the mechanism-analyzer's own already-landed commit `26089e8`).

All three launch gates remain **GREEN** on the 5-dataset scored panel per `state/gates.md` (unchanged since 2026-08-07T12:17Z certification) — **but G3-r3's anchor evidence is now under active dispute** per STOP-THE-LINE #2 above; read G3 alongside the HOLD, not as an unqualified green.
ADR r3-0005 (pfc spectral-rung repair) remains **PROPOSED**, unchanged, still awaiting operator + mentor sign-off.

**Program:** `program.md` · **Config:** `project.yaml` · **ADRs:** `docs/adr/` (0001 launch panel + A1, 0002 pfc crystalline box, 0003 estimator-integrity repairs, 0004 pfc report-only, 0005 pfc spectral-rung repair — PROPOSED) · **Card schema:** `experiment_cards/SCHEMA.md` · **Runbook:** `HOW_TO_LAUNCH.md`

## Streams
| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r3s1_factorised (gap) | 5-ds best-floor geomean 34.4198 (see anchor-dispute flag) | 1 | r3s1_factorised-B1 | `running`; main leg COMPLETED (cache-served, panel geomean 25.0662), guard leg FIXED + RELAUNCHED post debug attempt 1/5; stage=slurm-seed0 | seed 0 main: `66829977` COMPLETED (0:07); guard (orig): `66829978` FAILED (0:12, exit 1, direction-bank orthonormality assertion on heat_local); guard (relaunch): `66922977`, **PENDING (Priority)** | unchanged — guard relaunch still PENDING |
| r3s2_field_reach (gap) | 5-ds best-floor geomean 34.4198 (see anchor-dispute flag) | 1 | r3s2_field_reach-B1 | `analyzing`; seed-0 initial-analysis landed (panel geomean **10.7213**, verdict `proceed_to_seeds_1_2`, F1 does-not-fire, F2 fires as pre-registered); stage=slurm-seeds12 | seed 0: `66832670` COMPLETED (00:44:20); seeds 1-2: `66928385`/`66928386` (`r3-r3s2_field_reach-B1-s{1,2}`), **PENDING (Priority)** | unchanged — seeds 1-2 still PENDING |
| r3s3_lf_value (lever) | 5-ds best-floor geomean 34.4198 (**ifc_poisson columns invalid — stale-checkpoint contamination, see HOLD banner**) | 1 | r3s3_lf_value-B1 | **`complete`** — first card of the round to finish all 7 parts; 3-seed panel geomean **11.0789** (ci95 [10.8445, 11.2471]); `falsification_verdict` **confirmed**; vs-anchor -10.14%/-38.97% deltas flagged as anchor artefacts (STOP-THE-LINE #2); 2 tools promoted; stage=mechanism-analysis | seed 0: `66825323` COMPLETED (150m15s); seeds 1-2: `66879960`/`66879961` COMPLETED (02:20:08 / 02:20:09, exit 0:0, 60 legs each) | **new this cycle — card reached `complete`, `6_analysis`/`7_gap_and_future` landed, STOP-THE-LINE #2 discovered in turn 2** |
| r3s4_audit (diag) | 5-ds best-floor geomean 34.4198 | 1 | r3s4_audit-B1 | `analyzing`; **all 3 seeds COMPLETED** (geomeans 19.4235 / 19.5760 / 19.9318); stage=certify | seed 0: `66826610` COMPLETED (6m46s); seed 1: `66879667` COMPLETED (3m16s); seed 2: `66879668` COMPLETED (3m13s); certifier: `66921555` (`r3-r3s4_audit-B1-certify`), **PENDING (Priority)**, `expansion` partition (CPU-only, no GPU) | unchanged — certifier still PENDING |

Per-dataset best-floor skills (5-ds scored panel): allen_cahn_2d 475.8568 (nn_condition), fisher_kpp_2d 390.7015 (train_mean), cahn_hilliard 23.1803 (nn_condition), ifc_poisson 8.0409 (nn_condition, **DISPUTED — stale-checkpoint contamination**), ifc_heat 1.3941 (nn_condition). pfc 48.0773 (train_mean) is **report-only**, excluded from the geomean per ADR r3-0004 (pending possible reinstatement under ADR r3-0005 — still PROPOSED, no sign-off).
Source: `state/anchors/launch_anchors.json` (file itself unchanged this cycle, mtime 2026-08-07T12:16Z — rendered as-is per instruction, never recomputed by the maintainer; flagged disputed per STOP-THE-LINE #2, repair pending operator adjudication).

## Running / pending jobs
| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| 66922977 | r3s1_factorised-B1 (guard relaunch, seed 0) | PENDING | 00:00:00 | `(Priority)`, partition `gpu`, `cpu=4/mem=32G/gres:nvidia_h200=1` — `r3-r3s1_factorised-B1-guard-s0`. Unaffected by HOLD's repair scope. |
| 66928385 | r3s2_field_reach-B1 (seed 1) | PENDING | 00:00:00 | `(Priority)`, partition `gpu`, `cpu=8/mem=64G/gres:nvidia_h200=1` — `r3-r3s2_field_reach-B1-s1`. Unaffected by HOLD's repair scope. |
| 66928386 | r3s2_field_reach-B1 (seed 2) | PENDING | 00:00:00 | `(Priority)`, partition `gpu`, `cpu=8/mem=64G/gres:nvidia_h200=1` — `r3-r3s2_field_reach-B1-s2`. Unaffected by HOLD's repair scope. |
| 66921555 | r3s4_audit-B1 (certify D2-D4) | PENDING | 00:00:00 | `(Priority)`, partition `expansion`, `cpu=4/mem=32G`, no GPU — `r3-r3s4_audit-B1-certify`. Unaffected by HOLD's repair scope. |

No live-job state changes this cycle — all 4 jobs confirmed still PENDING via `squeue` + `sacct` (no transient-empty-squeue ambiguity). `66879960`/`66879961` (r3s3 seeds 1-2), `66832670` (r3s2 seed 0), `66829977`/`66829978` (r3s1 seed 0 main/original guard), `66826610`/`66879667`/`66879668` (r3s4 seeds 0-2), `66825323` (r3s3 seed 0) remain dropped from prior cycles (all COMPLETED/FAILED, superseded, or certified — see Streams row + timing ledger).

## Completed cards
| Card | Type | Panel geomean skill (±CI) | Falsification verdict | Tools promoted |
|---|---|---|---|---|
| r3s3_lf_value-B1 | model (lever) | **11.0789** (ci95 [10.8445, 11.2471], 3-seed 5-ds panel) | **confirmed** — coverage channel (supply of distinct condition rows), not optimization channel, explains the LF-at-train benefit. vs-anchor delta -10.14% (ifc_poisson -38.97%) recorded on the card as a **stale-checkpoint anchor artefact (STOP-THE-LINE #2)**, not a real effect — do not cite as a claim. | `response_decomposition.py`, `stale_checkpoint_audit.py` |

r3s2_field_reach-B1 has seed-0-only `5_actual_result` (panel geomean 10.7213, `ci95: null`, seeds 1-2 PENDING) — not yet complete.
r3s4_audit-B1 has all 3 seeds' raw results landed (19.4235 / 19.5760 / 19.9318) but is pending the certifier job (`66921555`, PENDING) — not yet complete.
r3s1_factorised-B1 has no `5_actual_result` yet — main leg cache-served, guard leg relaunched and still PENDING.

## Flags

- **STOP-THE-LINE #2 — stale-checkpoint anchor contamination, HOLD ACTIVE (see banner at top of this file).** `state/HOLD.json` set 2026-08-08T19:51:50Z, commit `26089e8`. Launch-anchor ifc_poisson cells (r2s3-B3 all legs, r2s1-B2/B3 all seeds, r2s2-B1 possibly mixed) resumed pre-repair checkpoints and were scored on repaired data. `launch_anchors.json` ifc_poisson columns + panel geomeans invalid pending repair. Round-3's own experiment legs audited CLEAN (0/225). No queued job cancelled — none depend on the stale cells. Batch advancement and claim adjudication halted pending operator adjudication of the repair plan.
- **r3s3_lf_value-B1: card reached `status: complete` this cycle — the round's first fully-completed card.** Two tools promoted (`response_decomposition.py`, `stale_checkpoint_audit.py`), both verified in `tools/index.md`. `guard_flags: ["heat_local"]` carried forward from prior cycles, unexplained but not gating (r3s2's own heat_local guard leg ran clean — isolated to r3s3, not dataset-wide). `next_direction` recorded for batch 2: LF-condition-row-count sweep on ch + ifc_heat, fixing the per-rung scaler bug, dropping ifc_poisson as a probe.
- **r3s2_field_reach-B1: seed-0 initial-analysis landed — F1 does not fire, F2 fires (pre-registered modal outcome), seeds 1-2 still PENDING, unchanged since last cycle.** Panel geomean skill **10.7213**. Guard panel geomean skill 0.2424, `guard_flags: []`.
- **r3s1_factorised-B1: debug attempt 1 of 5 FIXED + RELAUNCHED (cap `slurm_algo_attempts: 5`, 1 attempt used), guard relaunch (`66922977`) still PENDING, unchanged since last cycle.** Root cause: POD rank cut sitting exactly on the numerical accuracy boundary; fix proven bitwise no-op on all 5 scored panel cells plus both other guards, panel geomean 25.0662 reproduced bit-identical.
- **r3s1_factorised-B1 main seed-0 leg is cache-served, not a fresh run** (`66829977` completed in 7s, `epochs: 0`, `code_hash` unchanged) — expected caching behavior per `eval/score.py`, not a defect.
- **r3s4_audit-B1: all 3 seeds landed, certifier queued on the `expansion` (CPU-only) partition, still PENDING, unchanged since last cycle.** Per-seed panel geomeans 19.4235 / 19.5760 / 19.9318 — tight spread (~2.6%).
- **r3s4_audit-B1: F1 (floor reproduction) FIRED as pre-directed** — known float64/float32 loader-precision seam, adjudicated in prior cycles as a documented metrology property, not a defect. F2 `not_fired`. F3/F4 await the certifier (still queued, PENDING).
- **Eval-tree hygiene — resolved for all 4 streams, convention codified in `subagents/experiment-builder.md:218`.** No open items.
- **ADR r3-0005 (pfc spectral-rung repair) — still PROPOSED, blocking on operator + mentor sign-off.** Unchanged this cycle.
- **Gates** (`state/gates.md`): G1-r3 **GREEN** (2026-08-05, data), G2-r3 **GREEN** (2026-08-07, 5-ds preflight), G3-r3 **GREEN** (2026-08-07, 5-ds anchor re-aggregation, best-floor 34.4198) — file unchanged this cycle, **but read G3 alongside STOP-THE-LINE #2**: its ifc_poisson anchor evidence is now under active dispute (not a gate-file edit — maintainer is read-only for gates).
- **Reopen candidates**: none (`reopen_candidate: false` on all 4 batch-1 cards).
- **blocked.md**: none found under any stream directory.
- **Abandoned streams**: none. All 4 streams are on batch 1, all actively progressing or complete (1 awaiting guard relaunch, 1 seed-0 analyzed + seeds 1-2 PENDING, 1 `complete`, 1 with all 3 seeds landed + certifier queued). The 3-consecutive-skipped/blocked cap does not apply this early. No `state/streams/{stream}.json` markers exist (directory still does not exist).
- **Transcripts inbox**: empty — nothing to archive this run.
- **Timing ledger**: 8 entries, unchanged this cycle (no new COMPLETED `r3-*` jobs). r3s3_lf_value-B1 seed 0 `66825323` 150.25m, seed 1 `66879960` 140.13m, seed 2 `66879961` 140.15m; r3s4_audit-B1 seed 0 `66826610` 6.77m, seed 1 `66879667` 3.27m, seed 2 `66879668` 3.22m; r3s1_factorised-B1 seed 0 `66829977` 0.12m cache-served; r3s2_field_reach-B1 seed 0 `66832670` 44.33m. FAILED guard leg (`66829978`) intentionally not upserted (ledger upserts COMPLETED jobs only), nor are the still-PENDING jobs.
- **Watch for next cycle**: operator adjudication on the STOP-THE-LINE #2 repair plan (quarantine + fresh retrain + ckpt data-hash binding); r3s2's seeds 1-2 (`66928385`/`66928386`, PENDING); r3s1's guard-relaunch outcome (`66922977`); r3s4's certifier outcome (3-seed CI, F3/F4, `cratered_check`) — note the certifier's own D2-D4 probes should be read against the disputed ifc_poisson anchor once it lands.

Maintained by the maintainer cron.
