# MFFP Autoresearch Round 1 — Dashboard (updated 2026-07-29T18:17:57Z)

## Gate status
| Gate | What | Status |
|---|---|---|
| G1 | eval-layer smoke + assertion drill | PASS (2026-07-28) |
| G2 | copy-LF baselines | PASS (2026-07-28) |
| G3 | batch 0: anchors + noise floor (3 seeds) | **PASS (2026-07-29)** — array job `65956106` (r1-batch0) 36/36 COMPLETED, 0 FAILED. `state/anchors/*.json` (5 files) + `state/noise_floor.json` certified 2026-07-29T14:28:45Z. Champion `mf_fno_transfer_film`, panel geomean skill 6.703 [6.219, 7.102] @ 200-epoch smoke tier |
| G4 | dry-run card s5\_tuning-B1 (split G4a/G4b per ADR 0006) | **PASS (2026-07-29)** — G4a (build-path) PASS, G4b (submit-path) PASS. s1-s4 SLURM submissions unblocked (fire on each reviewed_pass/suggest) |
| G5 | H100 hardware carry-over comparison (ADR 0005) | **PASS (2026-07-29T17:26Z)** — genuine H100 retrain `65989241` vs the p100-certified anchor: geomean delta 0.0137, well inside the 0.884 noise floor; all per-dataset deltas inside their own floors too. Hardware confound closed — anchors (`state/anchors/*.json`) stand as certified, no recomputation |

## Streams
| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| s1_poisson | best_skill_on_dataset (ifc_poisson) = 1.566 [1.456, 1.696], family mf_fno_transfer_film | 1 | **s1_poisson-B1** (`mf_composition / ladder-data-fusion`, `models_r1/mf_fno_ladder`, 4-arm sweep, ifc_poisson, 200ep) | `analyzing`, stage `mechanism_analysis_running` | seed 0 = **65991280 COMPLETED** (4m28s, H100, 4 arms serial) | **Advanced this walk**: card's `reanalysis_progress` field is now populated with mechanism-analyzer turn markers (worktree scratchpad shows `turn2_out/turn2_results.json` written this window); `6_analysis` still null, turn 2 in flight — no verdict to report yet |
| s2_beyond_copy | copylf_bar = 1.0; certified best skills: helmholtz 13.82, pfc 11.51, allen_cahn 16.33, fisher_kpp 4.18, cahn_hilliard 5.53 | 1 | **s2_beyond_copy-B1** (`diagnostic / copy-LF excess-error forensics`, `models_r1/s2_copylf_forensics`, 0ep diagnostic) | `analyzing`, stage `mechanism_analysis_running` | seed 0 = **65991328 COMPLETED** (46s, H100, diagnostic) | **Advanced this walk**: card's `reanalysis_progress` moved `null` → `"turn_2"`; worktree scratchpad shows fresh turn-2 artifacts (`turn2_lf_ladder.png`, `turn2_stdout.txt`, `reanalysis_turn_2_results.md`, all written this window). Mechanism-analyzer live on turn 2; `6_analysis` still null |
| s3_testtime → **s3_warp** | s3_testtime (legacy, retired) champion_panel_geomean = 6.703 [6.219, 7.102]; **s3_warp: no anchor file yet** (diagnostic card, pre-analysis) | 1 | s3_testtime-B1 `retired_by_operator` (ADR 0010, audit trail kept) → **s3_warp-B1** (`experiment_cards/s3_warp/batch_1/B1.json`, drafted prior walk) | `drafted`, stage `builder_running` | none yet (diagnostic, epochs 0; job to follow build+review) | Unchanged in card status this walk; builder still active — `models_r1/s3_warp_oracle/{warp_core.py,smoke_eval.py}` and `scripts/{01_train_eval.sh,submit.sh}` all written this window, freshest write ~8 min before this scan (no new writes in the last ~8 min, consistent with a smoke-test subprocess running rather than a stall — watch next walk if still quiet) |
| s4_hybrid_routing | champion_panel_geomean = 6.703 [6.219, 7.102], family mf_fno_transfer_film | 1 | **s4_hybrid_routing-B1** (`mf_composition_measurement`, base `fno_transolver_seq`, panel, 200ep) | `reviewed_suggest` (unchanged) | **SLURM chain now live** (submitted since last walk, per orchestrator note): `65996887` (helmholtz) COMPLETED 15m28s, `65996889` (pfc) COMPLETED 15m28s, `65996893` (allen_cahn) RUNNING ~2m40s on hpc-33-19, `65996895` (fisher_kpp) RUNNING ~2m40s on hpc-33-22, `65996897` (cahn_hilliard) PENDING (Priority), `65996898` (ifc_poisson) PENDING (Priority), `65996899` (guard) PENDING (Priority), `65996900` (panel aggregate, afterok) PENDING (Dependency) | **Advanced this walk**: first `r1-{stream}-B{N}-s{seed}` SLURM activity of this walk window. `state/s4_hybrid_routing/current_stage.txt` now reads `seed0_running (jobs 65996887-65996900...)` — the prior walk's one-pulse lag is resolved. Per-dataset result JSONs exist for both completed jobs: helmholtz `alpha=0.0` (exact FNO-collapse, consistent with the 2-epoch contract smoke), skill 19.862; pfc `alpha=0.251` (non-zero gate), skill 3.282 — raw readouts only, no interpretation (analyzer's job) |
| s5_tuning | champion_panel_geomean = 6.703 [6.219, 7.102], family mf_fno_transfer_film | 1 | **s5_tuning-B1** (`tuning_spectral_bandwidth`) | `analyzing`, stage `mechanism_analysis_running` | seed 0 = **65988184 COMPLETED** (36m37s, H100) — `panel_geomean_skill 6.1958`; H100 anchor carry-over retrain **65989241 COMPLETED** (32m08s) → `7.1171`, PASS vs anchor (Gate G5) | **Advanced this walk**: card's `reanalysis_progress` moved `"turn_1"` → `"turn_2"`; worktree scratchpad shows fresh turn-2 artifacts (`turn2_band_relerr.png`, `turn2_fitgap.json`, `turn2_summary.json`, all written this window). `6_analysis` still null. Card `job_ids` still omits `65989241` (carried over, read-only observation) |
| s6_local | **no anchor file yet** (model card, pre-build) | 1 | **s6_local-B1** (`experiment_cards/s6_local/batch_1/B1.json`, drafted prior walk) | `drafted`, stage `builder_running` | none yet | Unchanged in card status this walk; builder actively live — freshest write 33s before this scan (`models_r1/s6_local_lf_corrector/*` + eval adapter pycache), no stall |
| s7_loss | **no anchor file yet** (model card, pre-build) | 1 | **s7_loss-B1** (`experiment_cards/s7_loss/batch_1/B1.json`, drafted prior walk) | `drafted`, stage `builder_running` | none yet | Unchanged in card status this walk; builder actively live — `scripts/screen_table.py` written ~3.3 min before this scan (after `submit.sh`/`submit_seeds_2_3.sh`/`00_screen.sh`/`01_train_eval.sh`), no stall |

**Scouting (not stream-bound)**: the stream-gap-mining websearcher closed out last walk (9/9 iterations, `s8_data` formally DO NOT OPEN). No change this walk.

## Running / pending jobs
| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| 65996887 | s4_hybrid_routing-B1 (helmholtz) | COMPLETED | 15m28s | — |
| 65996889 | s4_hybrid_routing-B1 (pfc) | COMPLETED | 15m28s | — |
| 65996893 | s4_hybrid_routing-B1 (allen_cahn) | RUNNING | ~2m40s | hpc-33-19 |
| 65996895 | s4_hybrid_routing-B1 (fisher_kpp) | RUNNING | ~2m40s | hpc-33-22 |
| 65996897 | s4_hybrid_routing-B1 (cahn_hilliard) | PENDING | 0:00 | Priority |
| 65996898 | s4_hybrid_routing-B1 (ifc_poisson) | PENDING | 0:00 | Priority |
| 65996899 | s4_hybrid_routing-B1 (guard) | PENDING | 0:00 | Priority |
| 65996900 | s4_hybrid_routing-B1 (panel aggregate, afterok) | PENDING | 0:00 | Dependency (waits on all six dataset jobs) |
| 65984594 | (unrelated) | RUNNING | ~3:50h | interactive `bash` session, out of round scope |

First `r1-{stream}-B{N}-s{seed}` SLURM chain of this walk window: s4_hybrid_routing's 8-job submission (2 arms + guard + aggregate confirmed by sacct/squeue; helmholtz and pfc arms COMPLETED, allen_cahn/fisher_kpp RUNNING, cahn_hilliard/ifc_poisson/guard/aggregate PENDING on priority/dependency). All other in-flight work this window remains agentic (mechanism-analyzer turn-2 on s1/s2/s5; builders on s3_warp/s6_local/s7_loss), none of which are SLURM jobs.

## Completed cards
| Card | Type | Panel geomean skill (±CI) | Falsification verdict | Tools promoted |
|---|---|---|---|---|
| _none — no card has reached final analysis (`6_analysis` still null on all cards with results, per-seed provisional-single-seed only, ADR 0004). `s1_poisson-B1`, `s2_beyond_copy-B1`, `s5_tuning-B1` are in `mechanism_analysis_running` (turn 2 in flight on all three); `s3_testtime-B1` is terminal (`retired_by_operator`, no analysis to come); `s4_hybrid_routing-B1` is `reviewed_suggest` with its seed-0 SLURM chain now 2/6 dataset arms COMPLETED, 2 RUNNING, 2 PENDING (+ guard/aggregate PENDING); `s3_warp-B1`/`s6_local-B1`/`s7_loss-B1` are `drafted`, mid-build_ | | | | |

## Flags
- **s4_hybrid_routing's seed-0 SLURM chain submitted and live this walk** — 8 jobs total (6 per-dataset arms + guard + afterok aggregate), matching the orchestrator's note verbatim (65996887/89/93/95/97/98 + 65996899 guard + 65996900 aggregate). 2 of 6 dataset arms COMPLETED (helmholtz, pfc), 2 RUNNING, 2 PENDING on priority; guard PENDING on priority; aggregate PENDING on its afterok dependency. `state/s4_hybrid_routing/current_stage.txt` now correctly reflects `seed0_running` — the prior walk's one-pulse lag is resolved.
- **Timing ledger upserted this walk**: 2 new COMPLETED-job entries added for `65996887` (helmholtz, 15.47 min, h100, family `fno_transolver_seq`) and `65996889` (pfc, 15.47 min, h100, same family) — ledger now 42 entries (was 40), still valid JSON.
- **Mechanism-analyzer turn 2 live on three streams**: `s1_poisson-B1` and `s2_beyond_copy-B1`/`s5_tuning-B1` all show fresh turn-2 scratchpad artifacts (plots, JSON summaries) written this window; `s2_beyond_copy-B1`'s and `s5_tuning-B1`'s `reanalysis_progress` card field advanced accordingly (`null`→`turn_2`, `turn_1`→`turn_2`). No `6_analysis` verdicts yet on any of the three — content of the in-progress turns is the mechanism-analyzer's finding to report, not summarized here.
- **Three drafted-card streams (`s3_warp`, `s6_local`, `s7_loss`) all show live builder filesystem activity** — no stalls. `s3_warp`'s freshest write is ~8 min old (scripts + smoke_eval.py already written; plausibly mid-subprocess, worth a liveness re-check next walk if still quiet), `s6_local` 33s old, `s7_loss` ~3.3 min old.
- **G5 (ADR 0005 H100 carry-over)**: remains RESOLVED PASS (17:26Z, carried over, unchanged this walk).
- **s5_tuning-B1 card `job_ids` stale vs SLURM reality** (carried over, read-only observation, unchanged): still does not list `65989241` (the completed genuine anchor-recert retrain). No card edit made by the maintainer.
- **ADRs unchanged this walk**: 0001-0012 all carried over, no new ADR since 0012 (s7_loss stream, prior walk).
- **s3_testtime benchmark-integrity flag** (carried over, historical — stream now retired): `ext__helmholtz_2d` test HF fields are exactly reconstructable from the condition vector via two FFTs. Compounds the existing noise-floor alert (helmholtz seed spread 9.695 skill units, unfalsifiable at smoke tier).
- **reopen candidates**: none (all cards have `reopen_candidate: false`).
- **blocked.md**: does not exist — no blocked entries.
- **abandoned streams**: none. `state/streams/` directory still does not exist — no batch has reached 3 consecutive skip/blocked (and `s3_testtime`'s operator retirement remains explicitly excluded from this trigger per ADR 0010).
- **Transcript inbox**: `state/transcripts/` still does not exist — nothing to archive this run.
- **Timing ledger**: 42 entries after this walk's 2-entry upsert (was 40); valid JSON confirmed post-write.
