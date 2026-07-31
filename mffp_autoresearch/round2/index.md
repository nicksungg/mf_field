# MFFP Autoresearch Round 2 — Dashboard (updated 2026-07-31T16:34:10Z)

## Streams

| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| r2s1_direct | 23.0636 (best_floor_panel_geomean) | 1 | r2s1_direct-B1 (**running**) | code-review verdict **SUGGEST — submit as-is** (`notes/handoff_code_reviewer.md`, 16:21:23Z; all 8 findings PASS); seed-0 job submitted per `scripts/submit.sh` | 1 (PENDING) | 2026-07-31T16:23:17Z (card status -> running, job 66163572 submitted) |
| r2s2_stacked | 23.0636 (best_floor_panel_geomean) | 1 | r2s2_stacked-B1 (drafted) | builder DONE (handoff 15:48:15Z: 5 arms + S1/S2 sidecars + P1/P2 probes + gates V1-V7; ifc_poisson rung ladder UNPAIRED, arms A2/A5 there marked `arm_semantics_degraded=True`); card `status` still not advanced to `built` (~44 min after handoff) — but fresh `scratchpad/contract_smoke.json` (helmholtz, ~82s old at check) confirms active review-in-progress, liveness-confirmed not stalled; now the longest-outstanding builder->card lag in the round | 0 | 2026-07-31T16:31:15Z (fresh contract_smoke.json write) |
| r2s3_lf_train_signal | 23.0636 (best_floor_panel_geomean) | 1 | r2s3_lf_train_signal-B1 (drafted) | builder in progress (`models_r2/r2s3_rung_supervised/`; extensive fresh scratchpad — dbg_pre/dbg_mid/dbg_ifc probes, resume.log within last few minutes) — confirmed live via filesystem-relative epoch delta, not stalled; no builder handoff yet | 0 | ~16:2xZ (scratchpad activity, see report) |
| r2s4_diag | 23.0636 (best_floor_panel_geomean) | 1 | r2s4_diag-B1 (running) | 3-seed certification jobs (66161480/81/82) still **PENDING** (Priority), unchanged since prior run | 3 (all PENDING) | 2026-07-31T15:58:25Z (unchanged) |

All four anchors are identical: the round-2 launch anchor is the panel
geomean of the best training-free floor per dataset
(`state/anchors/{stream}.json`, `provisional: false`, certified
2026-07-31T14:20:17Z). No stream has diverged yet.

Since the prior maintainer run (16:14:05Z): r2s1_direct's code-review landed
(verdict SUGGEST — submit as-is; mandatory analyzer caveat that the D3
certificate's aleatoric floor is window-sensitive and, at the recipe's
window, reads worse-than-zero-predictor on `ext__helmholtz_2d` — do not
report it as a ceiling there; report `allen_cahn`'s ceiling as a range) and
its seed-0 job (66163572) was submitted, still PENDING. r2s4_diag unchanged
(still 3 PENDING jobs). r2s2_stacked's builder-to-card lag has grown to ~44
min but is liveness-confirmed (fresh smoke-evidence write) rather than
stalled. r2s3_lf_train_signal continues active building, confirmed live.

## Running / pending jobs

| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| 66163572 | r2s1_direct-B1 (seed 0) | PENDING | 00:00:00 | None assigned (Priority) |
| 66161480 | r2s4_diag-B1 (seed 0) | PENDING | 00:00:00 | None assigned (Priority) |
| 66161481 | r2s4_diag-B1 (seed 1) | PENDING | 00:00:00 | None assigned (Priority) |
| 66161482 | r2s4_diag-B1 (seed 2) | PENDING | 00:00:00 | None assigned (Priority) |
| 66149132 | (unrelated interactive `bash`) | RUNNING | ~2h33m | hpc-90-18 — not a round-2 job |
| 66162876 | (unrelated interactive `bash`) | RUNNING | ~16m | hpc-24-22 — not a round-2 job |

r2s2_stacked has `scripts/submit.sh` + `scripts/submit_guard.sh` staged and
unsubmitted (review still in progress).

## Completed cards

(none — all 4 batch-1 cards still have `5_actual_result`/`6_analysis`/
`7_gap_and_future` as placeholders and no COMPLETED SLURM jobs yet; all 4
live jobs remain PENDING)

## Flags

- **Gates**: G1-r2 PASS, G2-r2 PASS, G3-r2 PASS (all 2026-07-31,
  `state/gates.md`) — round cleared for stream launch. Unchanged this run.
- **Noise floor**: `state/noise_floor.json` is still PROVISIONAL
  (`_source: round1-batch0-rescaled`) until r2s4-B1 certifies. The real
  certification jobs (seeds 0-2) remain PENDING in the queue — no real cert
  data exists yet. The only certification-adjacent artifacts on disk
  (`worktrees/r2s4_diag/B1/scratchpad/certify_synthetic/*`) remain explicitly
  FABRICATED plumbing-check data per that dir's own README and must never be
  cited or installed over `state/noise_floor.json`.
- **Analyzer caveat (r2s1_direct-B1, from code-review)**: the D3 certificate's
  aleatoric-floor estimate is window-sensitive (250/1000/4000/16000 closest
  pairs vs random-1000, measured by the reviewer). At the recipe's window
  (1000 closest), `ext__helmholtz_2d` reads 1.200 — worse than the zero
  predictor (1.0) — despite being flagged `verdict: supported, trustworthy:
  true` by the card's own gate (which tests `d_min`, not window width). The
  initial-analyzer/mechanism-analyzer must NOT report this as a ceiling for
  helmholtz (cite the zero-floor column instead); `allen_cahn`'s ceiling
  moves ~50% across windows and must be reported as a range (0.315-0.471),
  not a point value. `pfc` and `fisher_kpp` are window-robust and quotable.
  Zero-cost to fix (training-free, offline-regenerable), does not affect any
  scored split or pre-registered falsification threshold.
- **Builder->card lag**: r2s2_stacked's builder handoff (15:48:15Z) has not
  been reflected in its card `status` or `current_stage.txt` for three
  consecutive maintainer runs (now ~44 min and counting) — flagged for the
  orchestrator; liveness-confirmed via a fresh smoke-evidence write this run
  (not yet actionable as a stall, but now the longest-outstanding lag in the
  round).
- **Round-1 top-3 seed confirms**: NOT launched — pending a separate,
  explicit operator (Eloise) gate (`state/orchestrator_flow.md`).
- No reopen candidates, no `blocked.md` entries, no abandoned streams — none
  are possible yet (all streams at batch 1, no skip/block history).
- Timing ledger: `state/timing_ledger.json` still has zero entries — no
  COMPLETED `r2-*` job exists yet to upsert.
- Repo hygiene: `git status --short` on `mffp_autoresearch/round2/` shows
  uncommitted working-tree changes to `experiment_cards/r2s1_direct/batch_1/B1.json`,
  `state/orchestrator_flow.md`, and `state/r2s1_direct/current_stage.txt`
  from other subagents (review/orchestrator writes this cycle), not from this
  maintainer run — confirmed no Write call this run touched
  `experiment_cards/`. Most recent `round2: auto-sync` commit is `2779bcf`
  (2026-07-31T16:14:17Z), which predates these changes.
