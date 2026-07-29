# MFFP Autoresearch Round 1 — Dashboard (updated 2026-07-29T05:56:26Z)

## Gate status
| Gate | What | Status |
|---|---|---|
| G1 | eval-layer smoke + assertion drill | PASS (2026-07-28) |
| G2 | copy-LF baselines | PASS (2026-07-28) |
| G3 | batch 0: anchors + noise floor (3 seeds) | **PENDING** — array job `65956106` (r1-batch0) 24/36 COMPLETED, 7 RUNNING, 5 PENDING, 0 FAILED. First attempt `65955389` FAILED all 14 launched tasks (INFRA: bad GPU node `hpc-93-36`, now excluded) |
| G4 | dry-run card s5\_tuning-B1 | PENDING (gated on G3) |

No card in `state/anchors/*.json` exists yet — every "Anchor" cell below is
unrendered pending G3 (per program.md §4.5, anchors live in exactly one place
and are never recomputed here).

## Streams
| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| s1_poisson | not yet certified (G3 pending) | 1 | none yet | websearch_done_awaiting_G3_brainstormer | — | websearch report filed (batch_1) |
| s2_beyond_copy | not yet certified (G3 pending) | 1 | none yet | websearch_done_awaiting_G3_brainstormer | — | websearch report filed (batch_1) |
| s3_testtime | not yet certified (G3 pending) | 1 | none yet | websearch_done_awaiting_G3_brainstormer | — | websearch report filed (batch_1); ADR 0003 corrected §12.3 prior |
| s4_hybrid_routing | not yet certified (G3 pending) | 1 | none yet | websearch_done_awaiting_G3_brainstormer | — | websearch report filed (batch_1) |
| s5_tuning | not yet certified (G3 pending) | 1 | none yet | websearch_done_awaiting_G3_brainstormer | — | websearch report filed (batch_1); dry-run card (G4) still gated on G3 |

No stream has an experiment card yet — `experiment_cards/` contains only
`SCHEMA.md`. All five streams are gated on G3 (batch-0 anchor + noise-floor
certification) before any brainstormer proposes a slot.

## Running / pending jobs
| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| 65956106_24 (r1-batch0) | — (G3 array, task 24: mf_fno_pinn_transfer × sharp\_\_allen\_cahn\_2d × seed0) | RUNNING | ~39 min | hpc-26-21 |
| 65956106_25 (r1-batch0) | — (task 25: mf_fno_pinn_transfer × sharp\_\_allen\_cahn\_2d × seed1) | RUNNING | ~33 min | hpc-24-36 |
| 65956106_26 (r1-batch0) | — (task 26: mf_fno_pinn_transfer × sharp\_\_allen\_cahn\_2d × seed2) | RUNNING | ~33 min | hpc-26-17 |
| 65956106_27 (r1-batch0) | — (task 27: mf_fno_pinn_transfer × sharp\_\_fisher\_kpp\_2d × seed0) | RUNNING | ~27 min | hpc-90-36 |
| 65956106_28 (r1-batch0) | — (task 28: mf_fno_pinn_transfer × sharp\_\_fisher\_kpp\_2d × seed1) | RUNNING | ~27 min | hpc-25-17 |
| 65956106_29 (r1-batch0) | — (task 29: mf_fno_pinn_transfer × sharp\_\_fisher\_kpp\_2d × seed2) | RUNNING | ~27 min | hpc-26-15 |
| 65956106_30 (r1-batch0) | — (task 30: mf_fno_pinn_transfer × sharp\_\_cahn\_hilliard × seed0) | RUNNING | ~26 min | hpc-26-18 |
| 65956106_[31-35] (r1-batch0) | — (remaining G3 array tasks: 31-32 cahn\_hilliard seeds1-2, 33-35 ifc\_poisson seeds0-2, all × mf\_fno\_pinn\_transfer) | PENDING | 0:00 | Priority |

No `r1-{stream}-B{N}-s{seed}` jobs exist yet (no cards submitted). No
unrelated non-r1 jobs remain in the user's queue this walk (previously
noted `65958904`, plain `bash`, ended `CANCELLED by 28156` at
2026-07-28T22:20:58 and is no longer in queue — no action needed, out of
scope for this round).

## Completed cards
| Card | Type | Panel geomean skill (±CI) | Falsification verdict | Tools promoted |
|---|---|---|---|---|
| _none — no cards created yet (all streams pre-G3)_ | | | | |

## Flags
- **G3 not yet certified**: no stream may pass its brainstormer gate until
  `state/anchors/*.json` and `state/noise_floor.json` exist. All 5 streams
  correctly parked at `websearch_done_awaiting_G3_brainstormer`.
- **Prior batch-0 attempt (job 65955389) FAILED wholesale**: 14/14 launched
  array tasks fast-failed (~4-6s each) on node `hpc-93-36` (INFRA: CUDA
  busy). Diagnosed and fixed same day — `hpc-93-36` excluded via
  `--exclude` in `eval/run_batch0.sbatch`, resubmitted as `65956106`,
  currently healthy (24/36 COMPLETED, 0 FAILED so far; family 0
  `mf_fno_transfer_film` — all 18 tasks — fully COMPLETED; family 1
  `mf_fno_pinn_transfer` now 6/18 done — the fast helmholtz_2d and
  phase_field_crystal_2d dataset groups — 7 tasks running on the slower
  allen_cahn_2d/fisher_kpp_2d/cahn_hilliard 256^2 datasets, elapsed 26-39
  min so far, within the ~44 min family-0 prior for these datasets; 5
  tail tasks pending on cluster concurrency). At current pace, remaining
  12 tasks (7 running + 5 pending) should clear well inside the 6h sbatch
  time budget once cluster concurrency admits the pending ones.
- **reopen candidates**: none (no cards exist).
- **blocked.md**: does not exist — no blocked entries.
- **abandoned streams**: none.
- No transcript inbox present (`state/transcripts/inbox/` does not exist) —
  nothing to archive this run.
