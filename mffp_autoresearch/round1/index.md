# MFFP Autoresearch Round 1 — Dashboard (updated 2026-07-29T16:37:49Z)

## Gate status
| Gate | What | Status |
|---|---|---|
| G1 | eval-layer smoke + assertion drill | PASS (2026-07-28) |
| G2 | copy-LF baselines | PASS (2026-07-28) |
| G3 | batch 0: anchors + noise floor (3 seeds) | **PASS (2026-07-29)** — array job `65956106` (r1-batch0) 36/36 COMPLETED, 0 FAILED. `state/anchors/*.json` (5 files) + `state/noise_floor.json` certified 2026-07-29T14:28:45Z. Champion `mf_fno_transfer_film`, panel geomean skill 6.703 [6.219, 7.102] @ 200-epoch smoke tier |
| G4 | dry-run card s5\_tuning-B1 (split G4a/G4b per ADR 0006) | **PASS (2026-07-29)** — G4a (build-path) PASS: starter/builder/code-review mechanics validated end-to-end (build commit `ad29239`, reviewer verdict `reviewed_suggest`/submit-as-is). G4b (submit-path) PASS: guard job `65988185` COMPLETED in 46s with a valid seam-checked `score_panel` JSON at the analyzer-visible path; seed-0 panel job `65988184` RUNNING on H100 (`hpc-33-16`, ADR 0005). s1-s4 SLURM submissions unblocked (fire on each reviewed_pass/suggest) |

## Streams
| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| s1_poisson | best_skill_on_dataset (ifc_poisson) = 1.566 [1.456, 1.696], family mf_fno_transfer_film | 1 | **s1_poisson-B1** (`mf_composition / ladder-data-fusion`, base `mf_fno_allpairs`→`models_r1/mf_fno_ladder`, MFFP_LADDER_MODE 4-arm sweep, ifc_poisson, 200ep) | `drafted`, stage `builder_running` | — (not yet submitted) | Starter returned SUCCESS/drafted (13/13, no TBDs) at 16:22Z; builder dispatched, in flight (~15 min elapsed as of this walk) |
| s2_beyond_copy | copylf_bar = 1.0; certified best skills per dataset: helmholtz 13.82, pfc 11.51, allen_cahn 16.33, fisher_kpp 4.18, cahn_hilliard 5.53 | 1 | **s2_beyond_copy-B1** (`diagnostic / copy-LF excess-error forensics`, family `models_r1/s2_copylf_forensics`, 0ep diagnostic, 8 S2B1_* env knobs) | `drafted`, stage `builder_running` | — (not yet submitted; diagnostic, epochs=0) | Starter returned SUCCESS/drafted (13/13, no TBDs) at 16:22Z; builder dispatched, in flight |
| s3_testtime | champion_panel_geomean = 6.703 [6.219, 7.102], family mf_fno_transfer_film | 1 | **s3_testtime-B1** (`residual-lever-feasibility-diagnostic`, family `models_r1/hh_residual_anatomy`, ext__helmholtz_2d, 0ep diagnostic, 6 HHDIAG_* env knobs) | `drafted`, stage `builder_running` | — (not yet submitted; diagnostic, epochs=0) | Starter returned SUCCESS/drafted (14/14, no TBDs) at 16:21Z; handoff flags M0 hard-stop build gate + read-only last.pt dependency; builder dispatched, in flight |
| s4_hybrid_routing | champion_panel_geomean = 6.703 [6.219, 7.102], family mf_fno_transfer_film | 1 | **s4_hybrid_routing-B1** (`mf_composition_measurement`, base `fno_transolver_seq`, panel, 200ep, MFFP_CTX_SOURCE=auto) | `drafted`, stage `builder_running` | — (not yet submitted) | Starter returned SUCCESS/drafted (14/14, no TBDs) at 16:24Z; card mandates exactly two mechanical edits; open risk: 256² GPU memory unobserved beyond ifc_poisson contract run (H100 80GB mitigates vs assumed p100 16GB); builder dispatched, in flight |
| s5_tuning | champion_panel_geomean = 6.703 [6.219, 7.102], family mf_fno_transfer_film | 1 | **s5_tuning-B1** (`tuning_spectral_bandwidth`, status `reviewed_suggest`) | stage `seed0_running` | seed 0 = **65988184 RUNNING** (H100, ~19 min elapsed, hpc-33-16, 3/6 panel datasets written); guard = **65988185 COMPLETED** (46s, geomean skill 4.88 incl. guard datasets); anchor recert = **65988186 FAILED** (1s, bad venv path — see Flags) | Code-reviewer returned SUGGEST/submit-as-is (5 PASS, 2 non-blocking SUGGEST) at 16:18Z; ADR 0005 (H100) + ADR 0006 (G4 split) landed; seed 0 + guard + recert submitted 16:18Z on H100 |

**Delta this walk**: G4 fully PASSed (G4a+G4b) and the operator unblocked all
four remaining streams' starters, which have all returned `drafted` and moved
to `builder_running` — the round now has five cards in flight simultaneously
for the first time. s5_tuning-B1's code review returned `reviewed_suggest`
and seed 0 + the guard-set contract job + a new H100 anchor-recertification
job were submitted; the guard job completed cleanly, seed 0 is progressing,
but the recert job failed immediately on a bad venv path in
`eval/run_recert_h100.sbatch` (see Flags — needs a debugger dispatch). Three
new ADRs landed (0005 H100 switch, 0006 G4 submit-verified split, 0007
propose-many/screen-cheap/promote-few for batch ≥ 2).

**Note (read-only observation, not a card violation)**: `s5_tuning-B1`'s
`job_ids` field in the card JSON is still `[]` even though three jobs
(65988184/85/86) have been submitted and one has already completed — this is
presumably pending the next orchestrator/builder touch to the card and is
flagged here for visibility, not corrected by the maintainer (read-only).

**Noise-floor alert** (from `state/noise_floor.json`, certified 2026-07-29):
`ext__helmholtz_2d` seed spread = 9.695 skill units (a diverging seed at
200 epochs) → min claimable effect there is 9.695, i.e. unfalsifiable at
smoke tier unless a design targets the instability itself. The other five
panel datasets have tight floors (0.24-1.63). s3_testtime's brainstormer
independently rediscovered/confirmed a related benchmark-integrity issue:
the Helmholtz operator is exactly diagonalized by a 2-D DST-I, so test HF
fields are reproducible to 2.2e-13 from the condition vector via two FFTs —
flagged for mentor attention, out of maintainer scope to act on.

## Running / pending jobs
| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| 65988184 | s5_tuning-B1 (seed 0, panel, H100) | RUNNING | ~19 min | hpc-33-16; 3/6 panel dataset result JSONs written so far |
| 65988185 | s5_tuning-B1 (guard-set contract, H100) | COMPLETED (46s) | — | geomean skill 4.88 incl. guard datasets; upserted into timing ledger this walk |
| 65988186 | anchor recert (`r1-recert-h100`, H100) | **FAILED** (exit 1, 1s) | — | `.err`: `.../mf_field_eloise_data/SURF_2026-main/.venv/bin/activate: No such file or directory` — wrong venv path in `eval/run_recert_h100.sbatch` (should be `$PROJECT_ROOT/.venv/bin/activate`, matching `01_train_eval.sh`/`02_guard_contract.sh`) |
| 65984594 | (unrelated) | RUNNING | ~2:08:06 | interactive `bash` session, out of round scope |

No `r1-{stream}-B{N}-s{seed}` jobs yet for s1-s4 (all `builder_running`,
not yet at submit stage). Historical CANCELLED jobs `65958902`/`65958904`/
`65960289` and the prior batch-0 INFRA failure `65955389` (fixed and
resubmitted as `65956106`) are unchanged, out of scope.

## Completed cards
| Card | Type | Panel geomean skill (±CI) | Falsification verdict | Tools promoted |
|---|---|---|---|---|
| _none — no cards have completed the full panel run yet; `s5_tuning-B1` seed 0 is RUNNING on SLURM (3/6 datasets written), s1/s2/s3/s4-B1 are mid-build_ | | | | |

## Flags
- **Anchor-recert job FAILED — needs a debugger/fix-and-relaunch dispatch**:
  `65988186` (`r1-recert-h100`, `eval/run_recert_h100.sbatch`) died in 1s with
  `.venv/bin/activate: No such file or directory` — the script sources
  `$PROJECT_ROOT/mf_field_eloise_data/SURF_2026-main/.venv/bin/activate`
  (that path does not exist on this checkout), whereas the sibling scripts
  `01_train_eval.sh`/`02_guard_contract.sh` correctly source
  `$PROJECT_ROOT/.venv/bin/activate` (matches `project.yaml` `paths.venv:
  .venv`). This is a genuine script bug, not a transient SLURM issue —
  `sacct` confirms FAILED with `ExitCode 1:0`, and the fix is a one-line venv
  path change before resubmitting. `orchestrator_flow.md`'s most recent pulse
  (16:34Z) still describes this job as "PENDING", so the orchestrator has not
  yet observed the failure — surfacing here for the next pulse/debugger.
- **s5_tuning-B1 card `job_ids: []` stale vs SLURM reality**: three jobs
  submitted and tracked in `current_stage.txt` (`seed0_running (job
  65988184; guard 65988185; recert 65988186)`) but not yet reflected in the
  card JSON's `job_ids` array — observational note only, no card edit made.
- **All four s1-s4 streams now in `builder_running`** (unblocked by G4 PASS
  this walk) — first time the round has 5 cards in flight simultaneously.
  Builders started 16:19Z-16:24Z (worktree mtimes), roughly 13-18 min into
  their run as of this walk; no stall signal yet.
- **ADR 0004 — strict single-seed** (2026-07-29T16:05Z): in-round execution
  is seed-0-only, seeds 1-2 reserved for an end-of-round top-3 confirmation
  pass. Cards' locked `recipe.seeds: [0,1,2]` fields are untouched —
  execution governed by the ADR, not a card edit.
- **ADR 0005 — H100 switch** (2026-07-29T16:17Z): s5-B1 seed 0 + future
  submits use `--gres=gpu:h100:1 --time=02:00:00` CLI overrides (200 epochs
  kept; a 30-min wall cap was proposed and rejected).
- **ADR 0006 — G4 submit-verified split** (2026-07-29T16:17Z): G4 split into
  G4a (build-path, unblocks starters/builders) and G4b (submit-path, unblocks
  SLURM submits) — both now PASS.
- **ADR 0007 — propose-many/screen-cheap/promote-few** (2026-07-29T16:25Z):
  codified for batch ≥ 2 model cards with design freedom; batch 1 (all
  current cards) is unaffected — cards already locked, builds in flight.
- **s3_testtime benchmark-integrity flag** (for mentor, not actionable by
  maintainer): `ext__helmholtz_2d` test HF fields are exactly reconstructable
  from the condition vector via two FFTs (2-D DST-I diagonalization) —
  any method with the exact operator at test time scores near-zero error
  without a learned model. Compounds the existing noise-floor alert.
- **Operator note**: a forked session audited 5 pre-kickoff proposal docs
  round-1 setup never read; convergent findings filed as uncertified batch-2
  candidate seeds in `docs/operator_notes/2026-07-29-proposals-backlog.md`
  (warp/registration fusion, residual-spectrum FFT diagnostic, pinn_transfer
  attribution, structural constraints). Not yet cited by any certified card.
- **reopen candidates**: none (all 5 cards have `reopen_candidate: false`).
- **blocked.md**: does not exist — no blocked entries.
- **abandoned streams**: none; `state/streams/` directory still does not
  exist (no batch has reached 3 consecutive skip/blocked to trigger it).
- **Transcript inbox**: `state/transcripts/` still does not exist — nothing
  to archive this run.
- **Timing ledger**: upserted 1 new COMPLETED r1- job this walk (guard
  job `65988185`, s5_tuning, h100, 0.77 min) — now 37 entries; re-validated
  as parseable JSON. Seed-0 job `65988184` still RUNNING (not upserted per
  spec — COMPLETED only); recert job `65988186` FAILED (not upserted; timing
  priors come from completed runs only).
