# MFFP Autoresearch Round 1 — Dashboard (updated 2026-07-29T16:19:00Z)

## Gate status
| Gate | What | Status |
|---|---|---|
| G1 | eval-layer smoke + assertion drill | PASS (2026-07-28) |
| G2 | copy-LF baselines | PASS (2026-07-28) |
| G3 | batch 0: anchors + noise floor (3 seeds) | **PASS (2026-07-29)** — array job `65956106` (r1-batch0) 36/36 COMPLETED, 0 FAILED. `state/anchors/*.json` (5 files) + `state/noise_floor.json` certified 2026-07-29T14:28:45Z. Champion `mf_fno_transfer_film`, panel geomean skill 6.703 [6.219, 7.102] @ 200-epoch smoke tier |
| G4 | dry-run card s5\_tuning-B1 | PENDING — card `built` (build_commit `ad29239`, 2026-07-29T16:10Z). Builder's contract-tier verification suite complete: default env reproduces the untouched factory family bit-for-bit (helmholtz 22.613192981264614, ifc_poisson 0.4900025652737081), checkpoint-resume from a genuinely-interrupted `last.pt` reproduces the same number, and `MFFP_MODES_CAP=32` fires correctly (n_params 4,774,465 → 33,610,305, `modes [32,32]`). `scripts_path`/`output_paths`/`build_commit` now populated in the card JSON. Stage advanced `builder_running` → `review_running`; code-reviewer dispatched (2026-07-29T16:10Z), still in flight as of this walk (no review file, `review_notes: []`). `job_ids` still `[]` — seed 0 not yet submitted, pending reviewer PASS/SUGGEST. Open item: guard-set contract check (`scripts/02_guard_contract.sh`) still needs to fire before any panel-win claim (program.md §2.3) |

## Streams
| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| s1_poisson | best_skill_on_dataset (ifc_poisson) = 1.566 [1.456, 1.696], family mf_fno_transfer_film | 1 | none yet | brainstormer_done_awaiting_G4 | — | Holding for G4 (s5's dry-run card); unchanged this walk |
| s2_beyond_copy | copylf_bar = 1.0; certified best skills per dataset: helmholtz 13.82, pfc 11.51, allen_cahn 16.33, fisher_kpp 4.18, cahn_hilliard 5.53 | 1 | none yet | brainstormer_done_awaiting_G4 | — | Holding for G4; unchanged this walk |
| s3_testtime | champion_panel_geomean = 6.703 [6.219, 7.102], family mf_fno_transfer_film | 1 | none yet | brainstormer_done_awaiting_G4 | — | Holding for G4; DIAGNOSTIC card + benchmark-integrity flag from prior walks still open, unchanged |
| s4_hybrid_routing | champion_panel_geomean = 6.703 [6.219, 7.102], family mf_fno_transfer_film | 1 | none yet | brainstormer_done_awaiting_G4 | — | Holding for G4; `mf_composition_measurement` proposal unchanged this walk |
| s5_tuning | champion_panel_geomean = 6.703 [6.219, 7.102], family mf_fno_transfer_film | 1 | **s5_tuning-B1** (`tuning_spectral_bandwidth`, status `built`) | review_running (per `current_stage.txt`) — code-reviewer dispatched 16:10Z, no return yet | — | Card advanced `drafted`→`built` (build_commit `ad29239`) since last walk; `scripts_path`/`output_paths` populated; stage `builder_running`→`review_running`; ADR 0004 (strict single-seed) now governs execution — only seed 0 will be submitted in-round |

**Delta this walk**: the s5_tuning builder's handoff (observed in-progress
last walk) has now formally landed in the card JSON (`built`, build_commit,
scripts/output paths, 5 build_notes) and the flow advanced the stage to
`review_running`, dispatching the code-reviewer — which has not yet
returned. Separately, a new operator decision (ADR 0004, strict single-seed)
was recorded: in-round experiments now submit seed 0 only, with seeds 1-2
reserved for an end-of-round top-3 confirmation pass; this does not touch
any card's locked `recipe.seeds` field, so no maintainer read-only
violation.

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

No `r1-{stream}-B{N}-s{seed}` jobs in `squeue`/`sacct` — `s5_tuning-B1`
has not been submitted (card `job_ids` still empty; awaiting code-reviewer
PASS/SUGGEST). `scripts/submit.sh` and `scripts/02_guard_contract.sh` exist
and are ready to fire but have not been invoked. One unrelated `bash` job
(`65984594`, RUNNING, ~1:48:04 elapsed) is an interactive session, out of
round scope. Historical CANCELLED jobs `65958902`/`65958904`/`65960289` and
the prior batch-0 INFRA failure `65955389` (14/14 FAILED, bad node
`hpc-93-36`, fixed and resubmitted as `65956106`) are unchanged, out of
scope. G3's array `65956106` remains 36/36 COMPLETED, 0 FAILED (no new
r1- completions this walk — nothing new to upsert into the timing ledger).

## Completed cards
| Card | Type | Panel geomean skill (±CI) | Falsification verdict | Tools promoted |
|---|---|---|---|---|
| _none — no cards have completed the full panel run yet; `s5_tuning-B1` is built and in code-review, not yet submitted to SLURM_ | | | | |

## Flags
- **G4 still PENDING — card built, in code review, not yet submitted**:
  `s5_tuning-B1` (modes_cap 12→32 env-knob on champion `mf_fno_transfer_film`,
  panel @200ep) advanced `drafted`→`built` this walk (build_commit `ad29239`,
  2026-07-29T16:10Z), all three contract-tier proofs pass (default-
  equivalence bit-for-bit, checkpoint-resume reproduces the same number,
  cap-32 fires with correct param count). Stage `builder_running`→
  `review_running`; code-reviewer dispatched 16:10Z, still in flight as of
  this walk (no review file, `review_notes: []`). Next expected: reviewer
  PASS/SUGGEST → seed-0 submit via `scripts/submit.sh` + fire
  `scripts/02_guard_contract.sh` (required by §2.3 before any panel-win
  claim). Falsification threshold: 3-seed-anchor-referenced mean panel
  geomean skill must drop ≤5.819 (0.884 below the 6.703 anchor) AND no
  stable dataset improve beyond its certified `min_claimable_effect`, or F22
  (modes_cap bottleneck) is falsified — note per ADR 0004 the in-round run
  itself is now single-seed (provisional-single-seed label), with the 3-seed
  anchor CI still the comparison basis. Prior-art verdict: preempted-pivoted
  — licensed only as a measurement (iFNO/AFNO/MG-TFNO already cover the
  mode-count question), not a novelty claim.
- **ADR 0004 — strict single-seed (new this walk)**: operator-directed
  (2026-07-29T16:05Z) change from the 1+2 seed protocol to seed-0-only
  in-round execution, with seeds 1-2 reserved for an end-of-round top-3
  confirmation pass; `project.yaml`/`program.md` edited by the orchestrator
  session with the ADR as trail (per the ADR 0003 precedent). Cards' locked
  `recipe.seeds: [0,1,2]` fields are untouched — execution governed by the
  ADR. Applies to `s5_tuning-B1` and all later cards.
- **All 4 non-s5 streams (s1-s4) hold at `brainstormer_done_awaiting_G4`**:
  correct per gate discipline — orchestrator-owned, maintainer observes only.
- **s3_testtime benchmark-integrity flag** (for mentor, not actionable by
  maintainer): `ext__helmholtz_2d` test HF fields are exactly reconstructable
  from the condition vector via two FFTs (2-D DST-I diagonalization) —
  any method with the exact operator at test time scores near-zero error
  without a learned model. Compounds the existing noise-floor alert.
- **s4_hybrid_routing** proposal (`mf_composition_measurement`) is the first
  card design this round whose prediction path cross-attends to real
  test-time LF (the certified champion never consumes LF at test time) —
  worth watching once it reaches G4-cleared batch-1 dispatch.
- **Operator note**: a forked session audited 5 pre-kickoff proposal docs
  round-1 setup never read; convergent findings filed as uncertified batch-2
  candidate seeds in `docs/operator_notes/2026-07-29-proposals-backlog.md`
  (warp/registration fusion, residual-spectrum FFT diagnostic, pinn_transfer
  attribution, structural constraints). Not yet cited by any certified card.
- **reopen candidates**: none (only 1 card exists, status `built`,
  `reopen_candidate: false`).
- **blocked.md**: does not exist — no blocked entries.
- **abandoned streams**: none; `state/streams/` directory still does not
  exist (no batch has reached 3 consecutive skip/blocked to trigger it).
- **Transcript inbox**: `state/transcripts/` still does not exist — nothing
  to archive this run.
- **Timing ledger**: no new COMPLETED r1- jobs since last walk (still 36/36
  entries from the G3 array); `timing_ledger.json` re-validated as parseable
  JSON, unchanged.
