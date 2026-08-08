# MFFP Autoresearch Round 3 — Dashboard (updated 2026-08-08T00:20:36Z)

## Status: batch 1 — r3s3 wrapper mis-schedule corrected and real GPU job pending; r3s4 fix landed and re-review dispatched; r3s1 in code review; r3s2 still building

Since the last maintainer snapshot (2026-08-08T00:11:58Z), four deltas landed — all via the orchestrator/builders/reviewers/debugger (this maintainer made zero writes to any card):

1. **r3s3_lf_value-B1 wrapper mis-schedule corrected (this maintainer's flag, acted on).**
   The prior cycle's finding — job `66824243` was `sbatch scripts/submit.sh` itself (a login-node wrapper with no `#SBATCH` directives, queued on `expansion` with no GPU) rather than the wrapper being *executed* to launch the real training job — has been fixed.
   `sacct -j 66824243` now shows `State=CANCELLED+` (scancelled, `End=2026-08-07T17:13:27`).
   `scripts/submit.sh` was then run directly, which itself `sbatch`'d `01_train_eval.sh 0`, producing the real job **`66825323`**, correctly named `r3-r3s3_lf_value-B1-s0`, on the `gpu` partition with `gres/gpu:nvidia_h200=1`, `cpu=4`, `mem=32G`.
   Confirmed live in `squeue` as `PENDING (Priority)`.
   The card's `job_ids` array was updated accordingly (`{"seed": 0, "job_id": 66825323, ... "note": "corrects 66824243 (scancelled): submit.sh is a login-node wrapper..."}`) and `status` reads `submitted_seed0`.
   **The stale wrapper-mis-schedule flag is cleared from this dashboard** (see Flags — replaced with the corrected-state entry).
2. **r3s4_audit-B1 fix landed, re-review dispatched.**
   Commit `d84a31b` (`round3/exp-r3s4_audit-B1: review fixes — F4 gates on seed_mce (not tau_rel); cache redirect; sbatch the certify step; correct job-name mechanism`, nested repo at `worktrees/r3s4_audit/B1`, `2026-08-07T17:10:47-07:00`) resolves the reviewer's real FAIL finding.
   Verified in the diff: `probes/certify_thresholds.py`'s F4 escalation now reads `mce = per_ds[ds]["seed_mce"]` (the carded quantity) instead of `tau_rel`, with `tau_rel` retained as a clearly-labeled non-gating secondary (`breaches_on_tau_rel_secondary`) — the same dual-reporting pattern as F1/F2.
   `scripts/01_train_eval.sh` now also `export`s `ROUND2_EVAL_CACHE="$OUT_DIR/cache"` alongside `ROUND2_EVAL_RESULTS` (closes the cache-hit / missing-`rel_l2_per_sample` risk).
   `scripts/03_certify.sh` header now instructs `sbatch scripts/03_certify.sh` (not login-node execution), with a documented correction that no `slurm_rules.md` login-node allowance actually covers this step's cost (four 10k-resample bootstraps + leave-top-k influence + probe D4 refits — this build's own `contract_smoke.log` already recorded a login-node SIGKILL of comparable work).
   Stage advanced `builder-fix` → **`code-review`** (`state/r3s4_audit/current_stage.txt`, 2026-08-07T17:12:56-07:00); card `review_notes` still shows only the prior FAIL attempt (1) — the re-review has not yet landed as of this walk (no live reviewer process observed in `ps`), so no cap concern (`review_fail_attempts` cap is 3, still at 1).
3. **r3s1_factorised-B1 confirmed in code review.** Stage is `code-review` (`state/r3s1_factorised/current_stage.txt`), build unchanged at commit `960d88f` (family `models_r3/r3s1_twostage_crosscoef`, vendored from `round2/exp-r2s1_direct-B3 @ 2b030f02`; contract smoke exit 0, panel_geomean_skill 25.0662). Card `review_notes` still empty — review in progress, not yet landed.
4. **r3s2_field_reach-B1 still building.** Live `smoke_eval.py`/`score_panel.py` process confirmed (contract-tier pfc IC-path leg, `--no_cache`), ~28 min into the current invocation; card created `2026-08-07T18:06:20Z`, so builder has now been running **~6h14m** total. Compute-busy, not stalled — consistent with prior login-node-contention notes.

No other card fields changed. `git status --short experiment_cards/` shows only pre-existing orchestrator/builder/reviewer-caused modifications to r3s1, r3s3, r3s4 (none from this maintainer's reads).

All three launch gates remain **GREEN** on the 5-dataset scored panel (`state/gates.md`, unchanged since 2026-08-07T12:17Z certification): **G1-r3 GREEN**, **G2-r3 GREEN**, **G3-r3 GREEN**. ADR r3-0005 (pfc spectral-rung repair) remains **PROPOSED**, unchanged, still awaiting operator + mentor sign-off.

**Program:** `program.md` · **Config:** `project.yaml` · **ADRs:** `docs/adr/` (0001 launch panel + A1, 0002 pfc crystalline box, 0003 estimator-integrity repairs, 0004 pfc report-only, 0005 pfc spectral-rung repair — PROPOSED) · **Card schema:** `experiment_cards/SCHEMA.md` · **Runbook:** `HOW_TO_LAUNCH.md`

## Streams
| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r3s1_factorised (gap) | 5-ds best-floor geomean 34.4198 | 1 | r3s1_factorised-B1 | **built** (`960d88f`); stage=code-review, review in progress | none (job_ids: []) | stage advanced to code-review (`state/r3s1_factorised/current_stage.txt`, 2026-08-07T17:10:31-07:00) |
| r3s2_field_reach (gap) | 5-ds best-floor geomean 34.4198 | 1 | r3s2_field_reach-B1 | drafted, not dispatched; stage=builder, family `models_r3/r3s2_stack_ic` actively building (live process confirmed) | none (job_ids: []) | card created 2026-08-07T18:06:20Z; builder running ~6h14m, still compute-busy |
| r3s3_lf_value (lever) | 5-ds best-floor geomean 34.4198 | 1 | r3s3_lf_value-B1 | **reviewed SUGGEST → submitted_seed0**; stage=slurm-seed0 | seed 0: job `66825323` (**real GPU job**, `r3-r3s3_lf_value-B1-s0`, `gpu` partition, `gres/gpu:nvidia_h200=1`), PENDING (Priority); `66824243` (mis-scheduled wrapper) CANCELLED | job corrected this cycle: wrapper scancelled, real job submitted (`2026-08-07T17:13Z`) |
| r3s4_audit (diag) | 5-ds best-floor geomean 34.4198 | 1 | r3s4_audit-B1 | **F4-gating defect fixed** (`d84a31b`); stage=code-review, re-review dispatched, not yet landed | none (job_ids: []) | fix commit `d84a31b` (2026-08-07T17:10:47-07:00); stage builder-fix → code-review (17:12:56-07:00) |

Per-dataset best-floor skills (5-ds scored panel): allen_cahn_2d 475.8568 (nn_condition), fisher_kpp_2d 390.7015 (train_mean), cahn_hilliard 23.1803 (nn_condition), ifc_poisson 8.0409 (nn_condition), ifc_heat 1.3941 (nn_condition). pfc 48.0773 (train_mean) is **report-only**, excluded from the geomean per ADR r3-0004 (pending possible reinstatement under ADR r3-0005 — still PROPOSED, no sign-off).
Source: `state/anchors/launch_anchors.json` (re-aggregated 2026-08-07 ~19:17Z; unchanged this cycle).

## Running / pending jobs
| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| 66825323 | r3s3_lf_value-B1 (seed 0) | PENDING | 00:00:00 | `(Priority)`, partition `gpu`, `cpu=4/mem=32G/gres:nvidia_h200=1` — correctly-named real training job (`r3-r3s3_lf_value-B1-s0`), replaces the scancelled wrapper `66824243` |

## Completed cards
| Card | Type | Panel geomean skill (±CI) | Falsification verdict | Tools promoted |
|---|---|---|---|---|
| — | — | — | — | none — batch 1 has not been scored (evaluated/analyzed) for any stream yet |

## Flags

- **r3s3_lf_value-B1 job now correctly scheduled** (prior-cycle flag cleared). Wrapper job `66824243` (`sbatch scripts/submit.sh`, no `#SBATCH` directives, `expansion` partition, no GPU) was scancelled; `scripts/submit.sh` executed properly and dispatched the real GPU job `66825323` (`r3-r3s3_lf_value-B1-s0`, `gpu` partition, `nvidia_h200` gres), now `PENDING (Priority)`. No further action needed; watch for it to start/complete next cycle.
- **r3s4_audit-B1 review-FAIL defect fixed, re-review dispatched, not yet landed.** Fix commit `d84a31b` gates F4 on `seed_mce` (verified via diff), redirects `ROUND2_EVAL_CACHE`, and switches `03_certify.sh` to `sbatch` submission. `review_fail_attempts` remains at 1 of the project cap (3). Stage is `code-review`; no live reviewer process observed as of this walk — expect the re-review verdict next cycle.
- **r3s1_factorised-B1 in code review**, not yet landed (`review_notes` still empty). Build (`960d88f`) unchanged, contract smoke panel_geomean_skill 25.0662.
- **r3s2_field_reach-B1 builder still running (~6h14m total)** — confirmed compute-busy (live `smoke_eval.py`/`score_panel.py` process, pfc IC-path leg under `--no_cache`), consistent with the login-node-contention pattern already logged in `orchestrator_flow.md`. Not stalled; watch if this exceeds a full day without landing.
- **float64→float32 loader-precision seam** — independently found by both r3s3 and r3s4 builders on `affine_on_hf_train` floor reproduction (~2.5–2.8e-9 stripped-view vs native-dtype, ifc_heat/ifc_poisson). Adjudicated as a documented metrology property (strict 1e-9 `seam_check_floors` correctly retained and reproduces at ≤2.744e-10; the looser `ANCHOR_AFFINE_TOL=1e-7` reproduction-seam tolerance sits ~36× above it). No anchor/floor value changed. Unchanged this cycle.
- **Eval-tree hygiene, 2 streams still open** — `round2/eval/results/{r3s1_twostage_crosscoef,r3s2_stack_ic}/` and matching `round2/eval/cache/*` entries were written by builder-time smoke invocations without `ROUND2_EVAL_RESULTS`/`ROUND2_EVAL_CACHE` redirection (r3s3/r3s4 now redirect correctly, including r3s4's newly-added cache redirect this cycle). Flagged in `orchestrator_flow.md` as a required item before either stream's SLURM submission. Unchanged this cycle.
- **ADR r3-0005 (pfc spectral-rung repair) — still PROPOSED, blocking on operator + mentor sign-off.** Do not execute without both sign-offs (it amends the frozen round-2 eval convention). Unchanged this cycle.
- **Gates** (`state/gates.md`): G1-r3 **GREEN** (2026-08-05, data), G2-r3 **GREEN** (2026-08-07, 5-ds preflight), G3-r3 **GREEN** (2026-08-07, 5-ds anchor re-aggregation, best-floor 34.4198) — all unchanged this cycle.
- **Reopen candidates**: none (`reopen_candidate: false` on all 4 batch-1 cards).
- **blocked.md**: none found under any stream directory.
- **Abandoned streams**: none. All 4 streams are still on batch 1 (the 3-consecutive-skipped/blocked cap does not apply this early).
- **Transcripts inbox**: empty — nothing to archive this run.
- **Timing ledger**: still no completed `r3-*` jobs to upsert (`state/timing_ledger.json` unchanged, entries: []) — the one live job (`66825323`) is PENDING, not yet run.
- **Watch for next cycle**: r3s3's real GPU job (`66825323`) should start/complete; r3s4's re-review verdict should land; r3s1's review verdict should land; r3s2's builder should finish and submit.

Maintained by the maintainer cron.
