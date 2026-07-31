# MFFP Autoresearch Round 2 — Dashboard (updated 2026-07-31T16:56:38Z)

## Streams

| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r2s1_direct | 23.0636 (best_floor_panel_geomean) | 1 | r2s1_direct-B1 | **analyzing** — seed-0 job COMPLETED (66163572, h200, 6.95 min), panel_geomean_skill **19.6444** (vs 23.0636 anchor); initial-analyzer dispatched | 0 live (job done) | 2026-07-31T16:50:57Z (job 66163572 COMPLETED) |
| r2s2_stacked | 23.0636 (best_floor_panel_geomean) | 1 | r2s2_stacked-B1 | **running** — code-review verdict **SUGGEST** landed 16:54:09Z (ifc_poisson unpaired-ladder deviation independently reproduced, 0.08-0.30 min cond distance every rung; A2-A3 flagged as an upper bound, not epoch-matched); seed-0 panel (66166237) + guard (66166238) jobs submitted and RUNNING | 2 (RUNNING, ~1m20s) | 2026-07-31T16:54:09Z (review SUGGEST) / jobs submitted ~16:55:18Z |
| r2s3_lf_train_signal | 23.0636 (best_floor_panel_geomean) | 1 | r2s3_lf_train_signal-B1 | **running** — code-review verdict SUGGEST (reviewed_suggest, 16:41:06Z; shared-scaler confound on ifc_poisson travels as an interpretation constraint, not a build defect — null F1 there is NOT evidence LF adds nothing); seed-0 job (66165379) RUNNING since 16:45:32Z, arm `hf_only` in progress | 1 (RUNNING, ~11m) | 2026-07-31T16:45:32Z (job submitted) |
| r2s4_diag | 23.0636 (best_floor_panel_geomean) | 1 | r2s4_diag-B1 | **analyzing** — all 3 seeds COMPLETED (66161480/81/82, h200, ~4.1-4.4 min each); `03_certify.sh` ran, noise floor **CERTIFIED and INSTALLED** over the provisional file (IQM panel geomean **19.8178**, beats the 23.0636 anchor); initial-analyzer dispatched (3-seed) | 0 live (all done) | 2026-07-31T16:49:04Z (noise_floor.json certified/installed) |

All four anchors are identical: the round-2 launch anchor is the panel
geomean of the best training-free floor per dataset
(`state/anchors/{stream}.json`, `provisional: false`, certified
2026-07-31T14:20:17Z). No stream has diverged yet.

**BATCH-1 WAVE FULLY SUBMITTED** (all 4 streams have at least seed-0 either
completed or running) — first major milestone since round-2 launch.

## Running / pending jobs

| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| 66166237 | r2s2_stacked-B1 (seed 0, panel) | RUNNING | ~00:01:20 | hpc-sm-01-04 |
| 66166238 | r2s2_stacked-B1 (seed 0, guard) | RUNNING | ~00:01:20 | hpc-sm-01-04 |
| 66165379 | r2s3_lf_train_signal-B1 (seed 0) | RUNNING | ~00:11:06 | hpc-sm-01-15 (arm `hf_only`, first of several arms) |
| 66149132 | (unrelated interactive `bash`) | RUNNING | ~2h57m | hpc-90-18 — not a round-2 job |
| 66162876 | (unrelated interactive `bash`) | RUNNING | ~41m | hpc-24-22 — not a round-2 job |
| 66166013 | (unrelated interactive `bash`) | RUNNING | ~4m | hpc-89-13 — not a round-2 job |

6 `r1-*` jobs also PENDING in the queue (round-1 top-3 seed-confirm work) —
out of this maintainer's scope, noted only for queue-context.

## Completed cards

(none — all 4 batch-1 cards still have `5_actual_result`/`6_analysis`/
`7_gap_and_future` as placeholders; jobs have completed but analyzers have
not yet written results back to the cards)

| Card | Type | Panel geomean skill (±CI) | Falsification verdict | Tools promoted |
|---|---|---|---|---|
| r2s1_direct-B1 | model | 19.6444 (single seed 0, no CI yet) | pending analyzer | pending |
| r2s4_diag-B1 | diagnostic | 19.8178 IQM, CI95 [19.385, 20.527] (3 seeds) | pending analyzer | n/a (diagnostic) |

## Flags

- **Noise floor certified**: `state/noise_floor.json` is now **REAL and
  INSTALLED** (`_provisional: false`, certified 2026-07-31T16:49:04Z, source
  `r2s4_diag-B1` 3-seed spread), replacing the round-1-rescaled provisional
  file (backed up at `state/noise_floor.provisional_r1rescaled.json.bak`).
  Panel-geomean IQM **19.8178**, CI95 [19.385, 20.527], min-claimable-effect
  1.142 (max of spread-maxmin and paired-null-95). Per-dataset
  min-claimable-effects are 10-1700x tighter than the provisional file (e.g.
  `sharp__fisher_kpp_2d` 1.22 -> 0.0007; `ifc_poisson` 0.24 -> 0.94 — note
  ifc_poisson's MCE *widened* vs provisional, the one dataset moving the
  other direction). This is the certification event ADR r2-0002 gated on —
  any downstream falsification/support-gate check using the noise floor
  should now use the certified file.
- **Hardware tier switch (ADR r2-0004)**: h100 queue had an estimated
  2026-08-07 backlog (169 jobs) while h200 nodes sat idle; all 4 batch-1 jobs
  were moved to `gpu:nvidia_h200:1` before any of them had produced results
  (uniform-tier comparability preserved — no mixed-tier contamination).
  `project.yaml`'s `sbatch.gres` already reflects this
  (`gpu:nvidia_h200:1`, comment cites the ADR). All new timing-ledger
  entries this run are h200.
- **Timestamp anomaly (r2s1_direct-B1 review_notes)**: the card's
  `review_notes[0].utc` reads `2026-07-31T17:05:00Z`, which is **~11-14 min
  ahead of the actual system clock** at the time this maintainer ran
  (confirmed via `date -u`, ~16:51-16:56Z) and also postdates the card file's
  own mtime (16:23:17Z per `stat`). Read-only for cards, so not corrected
  here — flagged for the orchestrator/reviewer subagent's awareness in case
  its internal clock/timestamp logic is drifting; does not affect any scored
  quantity.
- **Analyzer caveat carried forward (r2s1_direct-B1, from code-review)**: the
  D3 certificate's aleatoric-floor estimate is window-sensitive. At the
  recipe's window (1000 closest pairs), `ext__helmholtz_2d` reads 1.200 —
  worse than the zero predictor (1.0) — despite the card's own gate stamping
  it `verdict: supported, trustworthy: true` (the gate tests `d_min`, not
  window width). The initial-analyzer must NOT report this as a ceiling for
  helmholtz (cite the zero-floor column instead); `allen_cahn`'s ceiling
  moves ~50% across windows (0.315-0.471) and must be reported as a range.
  `pfc`/`fisher_kpp` are window-robust and quotable.
- **Analyzer caveat (r2s2_stacked-B1, from code-review)**: ifc_poisson's rung
  ladder is UNPAIRED (independent condition draws per rung, min distance
  0.08-0.30, never 0) — matches r2s3's independent finding, an
  established cross-stream benchmark-integrity item for the round report
  (round-1's copylf `lf[:n_hf]` truncation semantics on ifc train were never
  valid pairs either). A2/A5 arms there are `arm_semantics_degraded=True`,
  and A2-A3 is an upper bound on shift, not epoch-matched. Analyzer must open
  `diag_ifc_poisson` since the panel JSON itself carries no degradation flag.
- **Analyzer caveat (r2s3_lf_train_signal-B1, from code-review)**: the
  shared-max-abs-rungs scaler makes ifc_poisson's `rung_native` stage-1 loss
  ~42x amplitude-weighted (~1770x in scaled MSE) toward rung 8 over HF — a
  card-locked design choice, not a build defect. A null/negative F1 on
  ifc_poisson is NOT by itself evidence LF training signal adds nothing;
  part 5 must report `extra.shared_scaler_max_abs` per arm alongside F1, and
  the natural B2 follow-up is a per-rung/per-stage-scaler variant. F1 is also
  epoch-matched but not step-matched (rung_native gets ~14x more optimizer
  steps per epoch than hf_only on ifc_poisson at batch 16).
- **Gates**: G1-r2 PASS, G2-r2 PASS, G3-r2 PASS (all 2026-07-31,
  `state/gates.md`) — round cleared for stream launch. Unchanged this run.
- **Round-1 top-3 seed confirms**: NOT this maintainer's scope (round-1 jobs
  visible in `squeue` as `r1-*`, PENDING) — separate round, separate report.
- No reopen candidates, no `blocked.md` entries, no abandoned streams — none
  are possible yet (all streams at batch 1, no skip/block history).
- **Timing ledger**: `state/timing_ledger.json` now has its first 4 entries
  (3x r2s4_diag seeds 0-2, 1x r2s1_direct seed 0; all h200, elapsed 4.13-6.95
  min) upserted from `sacct` this run. r2s2_stacked and r2s3_lf_train_signal
  jobs are still RUNNING, not yet eligible for the ledger.
- Repo hygiene: `git status --short` on `mffp_autoresearch/round2/` shows
  only `experiment_cards/r2s2_stacked/batch_1/B1.json` as modified in the
  working tree (from another subagent's card write this cycle, predating
  this maintainer run) — confirmed no Write call this run touched
  `experiment_cards/`.
