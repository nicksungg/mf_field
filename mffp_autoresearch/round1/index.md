# MFFP Autoresearch Round 1 — Dashboard (updated 2026-07-29T17:23:12Z)

## Gate status
| Gate | What | Status |
|---|---|---|
| G1 | eval-layer smoke + assertion drill | PASS (2026-07-28) |
| G2 | copy-LF baselines | PASS (2026-07-28) |
| G3 | batch 0: anchors + noise floor (3 seeds) | **PASS (2026-07-29)** — array job `65956106` (r1-batch0) 36/36 COMPLETED, 0 FAILED. `state/anchors/*.json` (5 files) + `state/noise_floor.json` certified 2026-07-29T14:28:45Z. Champion `mf_fno_transfer_film`, panel geomean skill 6.703 [6.219, 7.102] @ 200-epoch smoke tier |
| G4 | dry-run card s5\_tuning-B1 (split G4a/G4b per ADR 0006) | **PASS (2026-07-29)** — G4a (build-path) PASS, G4b (submit-path) PASS. s1-s4 SLURM submissions unblocked (fire on each reviewed_pass/suggest) |

## Streams
| Stream | Anchor (skill) | Current batch | Card | Status | Jobs | Last change |
|---|---|---|---|---|---|---|
| s1_poisson | best_skill_on_dataset (ifc_poisson) = 1.566 [1.456, 1.696], family mf_fno_transfer_film | 1 | **s1_poisson-B1** (`mf_composition / ladder-data-fusion`, `models_r1/mf_fno_ladder`, MFFP_LADDER_MODE 4-arm sweep, ifc_poisson, 200ep) | `reviewed_suggest` (verdict SUGGEST/submit-as-is) | seed 0 = **65991280 COMPLETED** (4m28s, H100, 4 arms serial) | Reviewer verdict SUGGEST landed 17:04Z; seed 0 submitted and **completed** 17:16Z. Raw per-arm skills (orchestrator glance, not yet a verdict): two_level 2.853 / adjacent 6.055 / allpairs 5.813 / legacy_pairing 8.362 — correspondence fix clearly helps (allpairs > legacy_pairing) but two_level > allpairs is the headline pattern for the initial-analyzer (now dispatched; `5_actual_result` still null) |
| s2_beyond_copy | copylf_bar = 1.0; certified best skills per dataset: helmholtz 13.82, pfc 11.51, allen_cahn 16.33, fisher_kpp 4.18, cahn_hilliard 5.53 | 1 | **s2_beyond_copy-B1** (`diagnostic / copy-LF excess-error forensics`, `models_r1/s2_copylf_forensics`, 0ep diagnostic) | `reviewed_suggest` (verdict SUGGEST/submit-as-is) | seed 0 = **65991328 COMPLETED** (46s, H100, diagnostic) | Reviewer verdict SUGGEST landed 17:04Z; diagnostic run submitted and **completed** 17:16Z — `panel_geomean_skill 9.624` (lookup-table diagnostic per reviewer S3, **excluded from leaderboard/top-3 eligibility**, not a model). Initial-analyzer dispatched; `5_actual_result` still null |
| ~~s3_testtime~~ → **s3_warp** | s3_testtime (legacy anchor, retired) champion_panel_geomean = 6.703 [6.219, 7.102]; **s3_warp: no anchor file yet** (pre-card, websearch stage) | 1 | s3_testtime-B1 **`retired_by_operator`** (ADR 0010, audit trail kept) → s3_warp has no card yet | `websearch_running` | — | **Stream replaced this walk's window**: ADR 0010 (17:15Z) — Eloise: "remove s3 and replace." `s3_testtime-B1`'s builder was stopped mid-build (no GPU spent, no SLURM ever submitted); card status → `retired_by_operator`, explicitly **not** an abandonment/skip. New lever stream `s3_warp` (warp-then-correct registration fusion, NEW_MODELS.md Candidate D, physics-agnostic per ADR 0009) started fresh at batch 1; websearcher in flight — `websearches/s3_warp/batch_1/` has 3 iterations + a running `summary_so_far.md` (prior-art re-verification for MF PDE fusion specifically, per ADR 0010) |
| s4_hybrid_routing | champion_panel_geomean = 6.703 [6.219, 7.102], family mf_fno_transfer_film | 1 | **s4_hybrid_routing-B1** (`mf_composition_measurement`, base `fno_transolver_seq`, panel, 200ep) | `drafted`, stage `builder_running` | — (not yet submitted) | Unchanged this walk — builder still in flight. Worktree created ~16:20Z; family files, scripts, and a contract-smoke log were actively written through ~16:44Z (models_r1/fno_transolver_seq/*, scripts/01-03*.sh), but nothing newer as of this walk (~49 min since last file write, ~63 min since worktree creation) — no explicit stall signal yet (no error in logs, no debug_notes), but duration is growing; worth an orchestrator glance next pulse |
| s5_tuning | champion_panel_geomean = 6.703 [6.219, 7.102], family mf_fno_transfer_film | 1 | **s5_tuning-B1** (`tuning_spectral_bandwidth`) | `reviewed_suggest`, stage `initial_analysis_running` | seed 0 = **65988184 COMPLETED** (36m37s, H100) — `panel_geomean_skill 6.1958` vs anchor 6.7030 [6.219, 7.102], Δ≈−0.507, inside the 0.884 noise floor, not falsifying at 1 seed (ADR 0004) | Unchanged card fields this walk; initial-analyzer dispatched ~17:16Z, `5_actual_result`/`6_analysis` still null (in flight). Card's `job_ids` still does not list the completed anchor-recert job `65989241` — read-only observation, not corrected here |
| s6_local *(new)* | **no anchor file yet** (pre-card, websearch stage) | 1 | no card yet | `websearch_running` | — | **New stream this walk**: ADR 0011 (17:20Z) — Eloise proposed additional streams; orchestrator scoped `s6_local` (FNO × local-representation hybrids — CNN/ConvNeXt branch, direct test of H2, live because s5-B1's H1 result only improved geomean by 0.507 < the 0.884 floor). Fills the approved 4-6 stream envelope. FNO-Transolver variants explicitly routed to s4 batch 2 instead (not a new stream). Websearcher dispatched only ~2 min before this walk — no output yet |

## Running / pending jobs
| Job | Card | State | Elapsed | Node/Reason |
|---|---|---|---|---|
| 65984594 | (unrelated) | RUNNING | ~2:53 h | interactive `bash` session, out of round scope |

No `r1-{stream}-B{N}-s{seed}` jobs currently RUNNING/PENDING — all four submitted this window (`65988184`, `65991280`, `65991328`) and the anchor-recert retrain (`65989241`) have COMPLETED; s3_warp/s6_local are pre-card (websearch stage) and s4 is pre-submit (builder stage).

**Recently completed (this walk):**
| Job | Card | State | Elapsed | Result |
|---|---|---|---|---|
| 65991280 | s1_poisson-B1 (seed 0, 4-arm ladder, ifc_poisson, H100) | COMPLETED | 4m28s | per-arm skills two_level 2.853 / adjacent 6.055 / allpairs 5.813 / legacy_pairing 8.362; upserted into timing ledger |
| 65991328 | s2_beyond_copy-B1 (seed 0, diagnostic, 5-dataset panel, H100) | COMPLETED | 46s | `panel_geomean_skill 9.624` (lookup diagnostic, excluded from leaderboard); upserted into timing ledger |
| 65989241 | anchor recert retrain (`r1-recert-h100`, H100) | COMPLETED | 32m08s | genuine H100 retrain of champion `mf_fno_transfer_film`: `panel_geomean_skill 7.1171` vs certified anchor 6.7030 [6.2185, **7.1022**] — lands just **above** the anchor's own upper CI bound (Δ≈+0.015 over the CI edge). Consistent with the earlier false-positive-resume snapshot `65989097`'s 7.1034 (both real-H100 numbers cluster ~7.10-7.12, marginally above the p100-derived CI). Anchor JSONs unchanged (mtime/value identical) — no recomputation performed by the maintainer; this is the ADR 0005 H100 carry-over comparison the orchestrator/mentor were waiting on |

No `r1-{stream}-B{N}-s{seed}` jobs yet for s3_warp/s6_local (pre-card) or s4 (still `builder_running`). Historical CANCELLED jobs `65958902`/`65958904`/`65960289` and the prior batch-0 INFRA failure `65955389` (fixed and resubmitted as `65956106`) are unchanged, out of scope.

## Completed cards
| Card | Type | Panel geomean skill (±CI) | Falsification verdict | Tools promoted |
|---|---|---|---|---|
| _none — no card has reached the analysis stage (`5_actual_result` still null on all 5 existing cards). `s5_tuning-B1`, `s1_poisson-B1`, `s2_beyond_copy-B1` all have completed seed-0 runs with initial-analyzers now dispatched; `s3_testtime-B1` is terminal (`retired_by_operator`, no analysis to come); `s4_hybrid_routing-B1` is mid-build_ | | | | |

## Flags
- **Stream replacement — s3_testtime → s3_warp (ADR 0010, 2026-07-29T17:15Z)**:
  Eloise (operator): "remove s3 and replace." `s3_testtime-B1` builder stopped
  mid-build (no GPU spent, no SLURM ever submitted); card → `retired_by_operator`
  (locked fields preserved for audit; explicitly **not** counted as a
  skip/abandonment per ADR 0010's own text). New lever stream `s3_warp`
  (warp-then-correct registration fusion) started at batch 1 with a fresh
  websearcher — prior-art re-verification mandatory for MF PDE fusion
  specifically. No card/anchor exists yet for `s3_warp` (expected at this
  stage).
- **New stream s6_local (ADR 0011, 2026-07-29T17:20Z)**: Eloise proposed
  additional streams; orchestrator scoped `s6_local` (FNO × local-representation
  hybrids, direct H2 test) to fill the approved 4-6 stream envelope. Websearcher
  dispatched only minutes before this walk; must read
  `docs/reports/MF_FNO_CNN_Hybrid_Report.md` and diagnose the mentor's prior
  failed FNO-CNN attempt before proposing (constraint carried at birth).
- **New ADRs since last walk**: `0009-unknown-physics-constraint.md` (models
  must not assume known PDE at test time — weather is the canonical case;
  s3-B1's own diagnostic findings independently support it), `0010-s3-replacement.md`
  (see above), `0011-s6-local-stream.md` (see above).
- **Anchor-recert retrain landed above the certified CI** (informational,
  orchestrator/mentor territory, not actionable by the maintainer): genuine
  H100 retrain `65989241` → `panel_geomean_skill 7.1171`, and the earlier
  (checkpoint-resume false-positive) snapshot `65989097` → `7.1034` — both
  sit just above the certified anchor's upper CI bound `7.1022`. The anchor
  itself (`state/anchors/s5_tuning.json` etc., value 6.7030 [6.219, 7.102])
  is unchanged by this walk; no anchor file was edited or recomputed.
- **s1_poisson-B1 and s2_beyond_copy-B1 both moved `built`(review_running) →
  `reviewed_suggest`** this walk; both reviewer verdicts were SUGGEST/submit-as-is;
  both seed-0 jobs were submitted and completed within the same window
  (`65991280` 4m28s, `65991328` 46s). Initial-analyzers dispatched for both;
  `5_actual_result` still null on both cards pending analyzer return.
- **s4_hybrid_routing-B1**: still `drafted`/`builder_running`; worktree file
  activity stopped ~49 min ago after producing a full script set
  (`01_train_eval.sh` … `03_aggregate_panel.sh`) and a family
  (`models_r1/fno_transolver_seq`) — no error/debug_notes recorded, so not
  flagged as stalled yet, but duration (~63 min since worktree creation) is
  worth an orchestrator glance next pulse.
- **s5_tuning-B1 card `job_ids` stale vs SLURM reality** (carried over,
  read-only observation): still does not list `65989241` (the completed
  genuine anchor-recert retrain). No card edit made by the maintainer.
- **ADR 0004 — strict single-seed**, **ADR 0005 — H100 switch**, **ADR 0006 —
  G4 submit-verified split**, **ADR 0007 — propose-many/screen-cheap/promote-few**,
  **ADR 0008 — ignore pinn**: all carried over unchanged from prior walks (see
  prior `index.md` history in `state/maintainer_report.md` for full text).
- **s3_testtime benchmark-integrity flag** (for mentor, historical — the
  stream that raised it is now retired): `ext__helmholtz_2d` test HF fields
  are exactly reconstructable from the condition vector via two FFTs (2-D
  DST-I diagonalization). Compounds the existing noise-floor alert
  (`ext__helmholtz_2d` seed spread 9.695 skill units, unfalsifiable at smoke
  tier per `state/noise_floor.json`).
- **reopen candidates**: none (all cards have `reopen_candidate: false`).
- **blocked.md**: does not exist — no blocked entries.
- **abandoned streams**: none. `state/streams/` directory still does not
  exist — no batch has reached 3 consecutive skip/blocked (and `s3_testtime`'s
  operator retirement is explicitly excluded from this trigger per ADR 0010).
- **Transcript inbox**: `state/transcripts/` still does not exist — nothing
  to archive this run.
- **Timing ledger**: upserted 2 new COMPLETED r1- jobs this walk — `65991280`
  (s1_poisson B1 s0, `mf_fno_ladder`, ifc_poisson, 200ep, h100, 4.47 min) and
  `65991328` (s2_beyond_copy B1 s0, `s2_copylf_forensics`, 5-dataset
  diagnostic panel, 0ep, h100, 0.77 min) — 38 → 40 entries; re-validated as
  parseable JSON. Anchor-recert job `65989241` (`r1-recert-h100`) is an infra
  job with no `{stream}-B{N}-s{seed}` card mapping and is intentionally
  excluded from the per-card ledger, per the maintainer-role's stream-job
  matching rule (its result is surfaced above in Running/pending and Flags
  instead).
