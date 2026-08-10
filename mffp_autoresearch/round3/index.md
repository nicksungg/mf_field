# MFFP Autoresearch Round 3 — Dashboard (updated 2026-08-10T14:45:00Z)

## STOP-THE-LINE #2: RESOLVED — HOLD cleared, repair (incl. extension) fully verified closed

`state/HOLD.json` no longer present at `state/` root (cleared 2026-08-10T12:57:53Z, per `state/HOLD_history.jsonl`).
Stale-checkpoint anchor contamination (launch-anchor ifc_poisson cells re-scored on repaired arrays with pre-repair weights) was quarantined, fresh-trained (jobs 89201-89211, all COMPLETED), re-audited CLEAN with `--fail-on-stale`, and the anchors rebuilt through the now-permanent `stale_gate()` in `tools/make_round3_anchors.py`.
Diff confined to ifc_poisson columns + derived aggregates; best-floor geomean **34.4198 unchanged** (training-free floors are checkpoint-independent).
`state/gates.md` G3-r3 **re-certified GREEN 2026-08-10**.

**Repair extension also verified CLOSED (2026-08-10):** 18 report-only pfc legs in `r2s3_lf_train_signal-B3`'s tree were quarantined and fresh-trained (jobs 147119-147121, ~8min each).
`zero_work_resume_scan --fail-on-zero-work` over the pfc pattern → **0/54 zero-work**, ckpts rewritten in-job.
18 allen_cahn zero-work legs remain by adjudication (benign test-split-trim variant, not part of this repair).
No new HOLD raised for the extension.

## BATCH 1 CLOSED — all four B1 cards `complete`; BATCH 2 LIVE — four builders in progress

All four streams have batch-2 websearch reports, brainstormer proposals, drafted B2 cards, and worktrees on `round3/exp-*-B2` branches.
No SLURM jobs are expected in the queue yet (builders write code, they do not launch).
Confirmed: `squeue -u $USER` carries no `r3-*`/`r3RPR-*` rows.

**Program:** `program.md` · **Config:** `project.yaml` · **ADRs:** `docs/adr/` (0001 launch panel + A1, 0002 pfc crystalline box, 0003 estimator-integrity repairs, 0004 pfc report-only, 0005 pfc spectral-rung repair — still PROPOSED) · **Card schema:** `experiment_cards/SCHEMA.md` · **Runbook:** `HOW_TO_LAUNCH.md`

## Streams

| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r3s1_factorised (gap) | 5-ds best-floor geomean 34.4198; own-stream anchor `state/anchors/r3s1_factorised.json` = 24.9573 [24.8726, 25.0662] | 2 | r3s1_factorised-B1 `complete`; B2 `drafted` | B1: 3-seed panel geomean **24.9573**, `falsification_verdict` **confirmed** (H holds — matched_ref control beaten on every seed; whole delta attributable to sharp__cahn_hilliard, L3 void for claims per ADR r3-0004 addendum). B2: builder LIVE — `models_r3/r3s1_predcrit_cascade` (13 files, untracked, mtime ~now) | B1 seed 0 `66829977` COMPLETED (cache-served); guard `66922977` COMPLETED; seeds 1-2 `144591`/`144592` COMPLETED (0:55 each, fresh compute). No B2 SLURM yet. | B1 seeds 1-2 landed + card reached `complete` since last walk |
| r3s2_field_reach (gap) | 5-ds best-floor geomean 34.4198; own-stream anchor `state/anchors/r3s2_field_reach.json` = 12.9556 [10.3180, 17.8277] | 2 | r3s2_field_reach-B1 `complete`; B2 `drafted` | B1: 3-seed panel geomean **12.9556**, `falsification_verdict` **falsified** (disjunctive clause: **F2 fires decisively** — corrector value unresolvable, 9-163x below one mce, round-2's ch null replicates; **F1 does not fire** — reach effect confirmed as IC information, not regularization, beyond threshold on every seed). B2: builder not yet writing `models_r3/r3s2_route` (no dir yet in worktree) | B1 all 3 seeds COMPLETED. No B2 SLURM yet. | B1 card reached `complete` (analyzer + mechanism wave) since last walk |
| r3s3_lf_value (lever) | 5-ds best-floor geomean 34.4198; own-stream anchor `r2s3_lf_train_signal-B3` REBUILT post-repair = 11.1689 [10.9988, 11.339] | 2 | r3s3_lf_value-B1 `complete`; B2 `drafted` | B1: 3-seed panel geomean **11.0789** [10.8445, 11.2471], `falsification_verdict` **confirmed** — vs-anchor delta recomputed post-repair: **-0.81% (NOT resolvable, 0.08x noise floor)**, superseding the pre-repair -10.14%/-38.97% artefact readings (annotated RESOLVED on the card). 2 tools promoted. B2: builder LIVE — `models_r3/r3s3_row_efficiency` (9 files, untracked, mtime ~now) | B1 all 3 seeds COMPLETED. No B2 SLURM yet. | vs-anchor delta recompute landed + part-7 blocking item CLOSED since last walk |
| r3s4_audit (diag) | 5-ds best-floor geomean 34.4198; **certified noise floor installed** `state/anchors_repaired/noise_floor.json` = 19.6438 (ci95 [19.4235, 19.9318], `_provisional:false`) | 2 | r3s4_audit-B1 `complete`; B2 `drafted` | B1: 3-seed panel geomean **19.6438**; certification table delivered; **F1 fired on the letter** (1.1056e-9 vs 1e-9 tol) — adjudicated **METROLOGY-LIMITED** (float32 loader seam ~70x below the breach; no scored-panel arm moves at 4dp); F2/F3/F4 confirm. `falsification_verdict` **falsified** (F1). B2: builder not yet writing `models_r3/r3s4_binding_fixture` (no dir yet in worktree) | B1 all 3 seeds + certifier COMPLETED. No B2 SLURM yet. | Noise floor installed (deferred until r3s1 seeds 1-2 landed, per pre-direction) + card `complete` since last walk |

Per-dataset best-floor skills (5-ds scored panel, `state/anchors/launch_anchors.json`): allen_cahn_2d 475.8568 (nn_condition), fisher_kpp_2d 390.7015 (train_mean), cahn_hilliard 23.1803 (nn_condition), ifc_poisson 8.0409 (nn_condition, **now repaired/re-certified**, no longer disputed), ifc_heat 1.3941 (nn_condition). pfc 48.0773 (train_mean) remains **report-only**, excluded from the geomean per ADR r3-0004 (its own repair extension verified closed 2026-08-10; reinstatement to the scored panel still gated on ADR r3-0005, still PROPOSED, no sign-off).
Source: `state/anchors/launch_anchors.json` (mtime 2026-08-10T05:55Z, rebuilt post-repair — rendered as-is per instruction, never recomputed by the maintainer).

## Running / pending jobs

| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| — | — | — | — | — |

No jobs running or pending anywhere in the round. All batch-1 SLURM compute (incl. the STOP-THE-LINE #2 repair jobs 89201-89211 and the pfc repair-extension jobs 147119-147121) is COMPLETED.
Batch-2 is at the experiment-builder stage for all 4 streams (code authoring in worktrees, no SLURM submission yet) — two builders (r3s1, r3s3) show live untracked file writes in `models_r3/` as of this walk; two (r3s2, r3s4) have not yet created their `models_r3/` family directory (earlier build stage, not a stall — no error signal, no stale lock, notes/handoff files in all four worktrees show recent activity within the last ~15 minutes).

## Completed cards

| Card | Type | Panel geomean skill (±CI) | Falsification verdict | Tools promoted |
|---|---|---|---|---|
| r3s1_factorised-B1 | model (gap) | **24.9573** (ci95 [24.8726, 25.0662], 3-seed 5-ds panel) | **confirmed** — matched one-stage control beaten on every seed (mean delta 0.5546); whole delta attributable to sharp__cahn_hilliard (stage-2 is a bitwise no-op on the other 4 cells at all 3 seeds); pfc/L3 adjudicated VOID for claims per ADR r3-0004 addendum | none recorded on card |
| r3s2_field_reach-B1 | model (gap) | **12.9556** (ci95 [10.3180, 17.8277], 3-seed 5-ds panel) | **falsified** — disjunctive clause: F2 FIRES (corrector value unresolvable, 9-163x below one mce), F1 does NOT fire (reach/IC-information effect confirmed beyond threshold on every seed). Stream anchor established (`state/anchors/r3s2_field_reach.json`). Cross-stream note: LSI amplification also fires on pfc anchor legs and the fluid guard cell. | none recorded on card |
| r3s3_lf_value-B1 | model (lever) | **11.0789** (ci95 [10.8445, 11.2471], 3-seed 5-ds panel) | **confirmed** — coverage channel (supply of distinct condition rows), not optimization channel. Post-repair vs-anchor recompute: **-0.81% delta, NOT resolvable (0.08x noise floor)** — the pre-repair -10.14%/-38.97% readings are now annotated as anchor artefacts and superseded. | `response_decomposition.py`, `stale_checkpoint_audit.py` |
| r3s4_audit-B1 | diagnostic | **19.6438** (ci95 [19.4235, 19.9318], 3-seed, certified — this value is now `state/anchors_repaired/noise_floor.json`) | **falsified** — F1 fires on the letter (1.1056e-9 vs 1e-9 tol), adjudicated METROLOGY-LIMITED (float32 loader seam, ~70x below the breach, no scored-panel arm moves at 4dp); F2/F3/F4 confirm | `stale_checkpoint_audit.py` (shared credit with r3s3), per-dataset ULP-band tolerance table delivered (routed to batch 2 contract fix) |

## Flags

- **STOP-THE-LINE #2 — RESOLVED.** `state/HOLD.json` cleared 2026-08-10T12:57:53Z (see `state/HOLD_history.jsonl`). Repair: 89-path quarantine, 14 fresh-trained anchor cells (jobs 89201-89211, all COMPLETED, ckpt mtime==result mtime, `resumed` 0/None), `--fail-on-stale` re-audit CLEAN on all 4 anchor trees, anchors rebuilt. Repair extension (18 report-only pfc legs, jobs 147119-147121) also verified CLOSED (0/54 zero-work post-repair). Residual instrument gap noted in `orchestrator_flow.md`: data-hash binding INSIDE family checkpoints remains open — routed to r3s4-B2 (`models_r3/_common/ckpt_binding.py`, priority-1 item on that card).
- **Batch 1 CLOSED.** All four B1 cards `status: complete`, all with populated `6_analysis`/`7_gap_and_future`. Batch-1 mechanism wave delivered cross-cutting findings (r3s1 SET-size/residual-saturation story replacing cond_dim; r3s2 LSI amplification firing cross-stream on pfc + fluid guard; r3s4 train_seconds audit rule priced at 0 unique TPs, routed for deletion). Routed to batch 2: (a) r3s4 fair-comparison-seam + F1-tolerance-table + ckpt-hash-binding contract fixes; (b) r3s3 seed-invariant 27-row ch hard-mask follow-up; (c) r3s2/r3s4 LSI-amplification instrument; (d) r3s1 SELECT_MAX-clip / SET-saturation discriminator.
- **Batch 2 dispatched, all 4 streams at experiment-builder stage.** Websearch + brainstormer artifacts present for all 4 streams (`websearches/*/batch_2/`, `brainstormer/*/batch_2/`); B2 cards `drafted` with `job_ids: []` (expected — builders don't launch SLURM); worktrees on `round3/exp-*-B2` branches. r3s1 (`r3s1_predcrit_cascade`, vendoring B1's `r3s1_twostage_crosscoef`) and r3s3 (`r3s3_row_efficiency`, vendoring B1's `r3s3_lf_channels`) show live in-progress (untracked) code in `models_r3/`; r3s2 (`r3s2_route`) and r3s4 (`r3s4_binding_fixture`) have not yet materialized a `models_r3/` dir — normal builder-stage variance, not a stall (no lock files, no error markers, `notes/handoff_experiment_starter.md` touched within the last ~15 min in all 4 worktrees).
- **Scheduler job-ID space reset (carried note).** Cluster `central`'s job-ID space reset since 2026-08-08: round-3 stream jobs were 66xxxxxx, repair jobs were 5-digit 892xx, `r3s1` batch-1 seeds 1-2 were 6-digit 144591/144592, pfc repair-extension jobs were 6-digit 147119-147121. `sacct` continues to resolve all ranges without ambiguity.
- **Gates** (`state/gates.md`): G1-r3 **GREEN** (2026-08-05), G2-r3 **GREEN** (2026-08-07, 5-ds preflight), G3-r3 **GREEN, RE-CERTIFIED 2026-08-10** (post stale-checkpoint repair rebuild — no longer disputed). All three gates GREEN and current.
- **ADR r3-0005 (pfc spectral-rung repair) — still PROPOSED, blocking on operator + mentor sign-off.** Unchanged this cycle.
- **Reopen candidates**: none (`reopen_candidate: false` on all 4 batch-1 cards; batch-2 cards not yet in a state to carry this field).
- **blocked.md**: none found under any stream directory.
- **Abandoned streams**: none. All 4 streams progressing normally into batch 2. The 3-consecutive-skipped/blocked cap does not apply. No `state/streams/{stream}.json` markers exist (directory still does not exist).
- **Transcripts inbox**: empty — nothing to archive this run.
- **Timing ledger**: 28 entries (was 12) — upserted this cycle: r3s1_factorised-B1 seeds 1-2 (`144591`/`144592`), 11 STOP-THE-LINE #2 repair jobs (`89201`-`89211`, anchor cards r2s1_direct/r2s2_stacked/r2s3_lf_train_signal), 3 pfc repair-extension jobs (`147119`-`147121`, r2s3_lf_train_signal-B3). All COMPLETED, all re-validated as parseable JSON after write.
- **Watch for next cycle**: batch-2 builder progress for r3s2/r3s4 (models_r3 dir not yet created as of this walk); first batch-2 SLURM submissions once builders finish + reviews pass.

Maintained by the maintainer cron.
