# MFFP Autoresearch Round 3 — Dashboard (updated 2026-08-11T01:41:00Z)

## BATCH 2 CLOSED — all 8 round-3 cards (B1 + B2, all 4 streams) are `status: complete`

No SLURM jobs are live anywhere in the round (`squeue -u $USER` carries no `r3-*`/`r3RPR-*`/`r3-adr5-*` rows; only one unrelated `bash` job, pid 88593, not round-3).
Since the previous walk (RUN END 2026-08-10T14:47:30Z), all four batch-2 builders finished, were reviewed, launched their SLURM legs, and closed:

- **r3s1_factorised-B2** — new family `r3s1_predcrit_cascade` (closed-form, `epochs: 0`). Falsified via **G2(iii)**: an affirmative route confirmed, but the pre-registered success clause did not hold as stated. 3-seed panel geomean (scored arm `A2_predcrit`) **25.1243** [24.9477, 25.2757].
- **r3s2_field_reach-B2** — new family `r3s2_route` (stack vs direct switch). Falsified-via-G2(iii) with an affirmative route; new **stream anchor established at 10.0853** (`state/anchors/r3s2_field_reach.json`, `provisional:false`, certified 2026-08-10T17:47:43Z), beating the B1 anchor 12.9556 by 2.87 skill units and the training-free best-floor by 24.33.
- **r3s3_lf_value-B2** — new family `r3s3_row_efficiency`. **Confirmed**: knee at cap **c\* = 80** (7.0x the clause floor) plus a training-free surrogate for it. Card scores only 2 of the 5 panel datasets by design (cahn_hilliard + ifc_heat) — no round-3 5-dataset panel geomean is claimed; a diagnostic-only 2-dataset geomean is reported per seed [0.8898, 1.0040, 0.9508].
- **r3s4_audit-B2** — new tool `tools/ckpt_data_binding.py` (six-role checkpoint-binding instrument). **G1 confirmed 108/108** (recall 27/27-18/18-18/18, 0/27 false RETRAIN, Wilson95 [0, 0.125]); compound hypothesis falsified in its third conjunct only (**G5 fit-set seam, fired 1.9333x on cahn_hilliard — escalated-pending operator re-pricing confirmation**). Card scores 0 panel cells by design (diagnostic instrument, not a model).

**ADR r3-0006 (film-transfer / U-Net learned-baseline denominators) — CERTIFIED, live in reporting.**
`state/anchors/film_denominator.json`: `mf_fno_transfer_film`, 5-ds panel geomean 14.0770 (copy-LF units); film remains the panel baseline.
`state/anchors/unet_baseline.json`: ConvNeXt-U-Net, dead heat with film — 5-ds panel ratio 1.0034x, 6-ds panel ratio 1.0285x.
Film-denominated reading of batch 1 (recorded, not re-adjudicated): r3s3 (0.79) and r3s2 (0.92) beat the learned baseline; r3s4 (1.40) and r3s1 (1.77) lose to it.
Best-of-zoo certification sweep (5 contenders x 3 seeds, jobs 187123-137) was **ABORTED minutes after launch on operator instruction** ("previously-benchmarked models need no re-test against film-transfer"); outputs marked UNCERTIFIED; film-transfer stands as the ADR r3-0006 denominator on its factory-zoo championship record.

**ADR r3-0005 phase 2 — FULLY EXECUTED: pfc restored to the 6-dataset scored panel.**
Scored cell moved to L1(32²)→L3(128²) with the exact spectral reference (0.012358); 21 re-score jobs landed clean (18 first-pass + 3 re-vendored resubmissions after an initial vendoring-seam refusal on `r2s3_lf_train_signal-B3`, branch `8ce61fd`); fifth-class preflight on the new cell PASS with a priced `OUTLIER_DOMINATED` warn (MDD 65.8%, `state/preflight_pfc_adr0005_2026-08-10.json`).
**Best-floor lineage now 38.8368** (was 34.4198 on the 5-ds panel); all 4 anchor cards CERTIFIED with pfc cells: r2s1-B2 28.542 / r2s1-B3 30.1137 / r2s2-B1 90.1498 (pfc cell carries the known unregularised-LSI amplification caveat, pre-flagged by r3s2 mechanism work, fix class proven in r3s2-B2) / r2s3-B3 15.3998.
`state/anchors/launch_anchors.json` reflects the 6-dataset panel (mtime 2026-08-10T18:32:34-07:00, the most recent write in `state/anchors/`).
B1 cards carry an `adr_r3_0005_addendum` — their originally recorded numbers are NOT re-stated; the 5-ds registration for those cards stands, pfc claims are MDD-priced going forward.

## Streams

| Stream | Anchor (skill, lower=better) | Batch 1 | Batch 2 | Status | Jobs (B1+B2) | Last change |
|---|---|---|---|---|---|---|
| r3s1_factorised | best-floor 38.8368 (6-ds, `launch_anchors.json`) | complete — panel 24.9573 [24.8726, 25.0662], confirmed | complete — panel 25.1243 [24.9477, 25.2757], falsified-on-novelty/G2(iii) | complete | 66829977/-78, 66922977, 144591-2, 163603, 165213-4 | B2 close 2026-08-10 |
| r3s2_field_reach | own-stream anchor **10.0853** (`r3s2_field_reach.json`, certified) | complete — panel 12.9556 [10.3180, 17.8277], falsified (F2 fires) | complete — panel 10.0853 [9.7249, 10.3528], falsified-via-G2(iii), new anchor | complete | 66832670, 66928385-6, 158775, 165550-1 | B2 close 2026-08-10 |
| r3s3_lf_value | best-floor 38.8368 (6-ds); no panel-geomean claim on B2 | complete — panel 11.0789 [10.8445, 11.2471], confirmed | complete — knee c\*=80 confirmed, training-free surrogate; diagnostic 2-ds geomean only | complete | 66825323, 66879960-1, 166258, 181977-8 | B2 close 2026-08-10 |
| r3s4_audit | certified noise floor (`state/anchors_repaired/noise_floor.json`, `_provisional:false`) | complete — panel 19.6438 [19.4235, 19.9318], falsified (metrology-limited F1) | complete — G1 confirmed 108/108; G5 escalated-pending | complete | 66826610, 66879667-8, 66921555, 165822, 168917-8, 181979 | B2 close 2026-08-10 |

## Running / pending jobs

None. `squeue -u $USER` empty of round-3 activity; `sacct` confirms no ambiguity (no transient-empty-squeue false negative). All round-3 SLURM compute for batches 1 and 2 (all 4 streams), the ADR r3-0006 baseline certifications, and the ADR r3-0005 phase-2 pfc re-score are landed.

## Completed cards

| Card | Type | Panel geomean skill (±CI) | Falsification verdict | Tools promoted |
|---|---|---|---|---|
| r3s1_factorised-B1 | model | 24.9573 [24.8726, 25.0662] | confirmed (matched one-stage control beaten every seed; delta 0.5546, attributable entirely to sharp__cahn_hilliard; L3 adjudicated VOID for claims) | — |
| r3s1_factorised-B2 | model | 25.1243 [24.9477, 25.2757] (scored arm `A2_predcrit`) | falsified-via-G2(iii): affirmative route confirmed | — |
| r3s2_field_reach-B1 | model | 12.9556 [10.3180, 17.8277] | falsified (F2 fires: corrector value unresolvable 9-163x below one mce; F1 reach/IC-information effect confirmed on every seed) | stream anchor `r3s2_field_reach.json` |
| r3s2_field_reach-B2 | model | **10.0853** [9.7249, 10.3528] | falsified-via-G2(iii): affirmative route + new stream anchor | `r3s2_field_reach.json` (certified, supersedes B1's anchor) |
| r3s3_lf_value-B1 | model | 11.0789 [10.8445, 11.2471] | confirmed (post-repair vs-anchor recompute: −0.81%, 0.08x noise floor, NOT resolvable — supersedes the pre-repair −10.14%/−38.97% stale-checkpoint artefact readings, now RESOLVED on the card) | — |
| r3s3_lf_value-B2 | model | no round-3 5-ds panel claim (2-ds diagnostic geomean [0.8898, 1.0040, 0.9508]) | confirmed — knee c\*=80, training-free surrogate | — |
| r3s4_audit-B1 | diagnostic | 19.6438 [19.4235, 19.9318] | falsified (F1 fires on the letter, 1.1056e-9 vs 1e-9 tol, adjudicated METROLOGY-LIMITED — ~70x below the float32 loader-seam spread; F2/F3/F4 confirm) | `tools/stale_checkpoint_audit.py`; certified noise floor installed |
| r3s4_audit-B2 | diagnostic | no panel cells scored by design (0/0) | falsified (G1 confirmed 108/108; compound hypothesis falsified in its 3rd conjunct — G5 fit-set seam, 1.9333x on ch, escalated-pending) | `tools/ckpt_data_binding.py` |

## Flags

- **Open operator item — G5 re-pricing confirmation.** r3s4_audit-B2's six-role checkpoint-binding instrument confirmed 108/108 on its first two conjuncts, but its third conjunct (G5 fit-set seam) fired 1.9333x on cahn_hilliard and is recorded as escalated-pending the operator's re-pricing confirmation. Not adjudicated as of this walk.
- **Open operator item — `program.md` §2 internal inconsistency (the "affine-floor question").** §2 line 29 lists pfc inside a "6-dataset" scored panel, but lines 34-36 describe the ADR r3-0004 5-dataset panel (pfc report-only, best-floor 34.4198) — that inconsistency predates this cycle. It is now further stale relative to ADR r3-0005 phase 2 (pfc restored to the scored panel, best-floor **38.8368**, per `state/anchors/launch_anchors.json` and `state/gates.md`'s 2026-08-10 resolution note). `program.md` is outside the maintainer's write scope; read-only observation only.
- **Open operator item — batch-3 scope decision.** All 8 batch-1/batch-2 cards are `complete`; no batch-3 cards, websearch reports, or brainstormer proposals exist yet for any stream (`current_batch.txt` for all 4 streams still reads `1`, `current_stage.txt` still holds batch-1/early-batch-2-era values, unrefreshed since — this is a stale tracker, not a stall: card status is the source of truth and all 8 are `complete`). Batch-3 orientation direction is on file per the operator's 2026-08-10 instruction ("round 3's target is the best LEARNED baseline, not copy-LF"; batch-3 cards will register success clauses against the certified best learned baseline) but no batch-3 cards have been drafted.
- **`state/gates.md` internal staleness.** The file's top "2026-08-10 (resolution)" note correctly documents ADR r3-0005 phase 2 (6-ds panel, best-floor 38.8368), but the `| gate | state | evidence |` table below it (G2-r3, G3-r3 rows) still describes the ADR r3-0004-era 5-dataset panel and cites the pre-ADR-r3-0005 best-floor 34.4198 and 5-seed-cell values (e.g. r2s1-B2 `[23.69, 23.79, 23.84]`) that were superseded by the 6-ds re-certification (r2s1-B2 mean now 28.542 per `launch_anchors.json`). Read-only for the maintainer — surfaced here, not corrected.
- **Process anomaly — part-5 lost-update race (r3s4_audit-B2).** Card's `5_actual_result` was clobbered to `null` by a concurrent full-card rewrite (lost-update race between card writers) during the batch-2 cycle; re-derived from artifacts with no data loss. Orchestrator routed a card-writing discipline note to the maintainer: json load-modify-dump writers must not interleave; prefer field-scoped writes and verify-after-write. No card content was touched by the maintainer in response — flagged here per the routing instruction.
- **Process anomaly — retroactive job_ids fixes.** r3s4_audit-B2's seed-1/seed-2 job IDs (168917-8) were omitted from the card at submission time and recorded retroactively after being flagged by the 3-seed analyzer. No other card shows this pattern this cycle.
- **STOP-THE-LINE #2 — fully resolved**, no open blast radius. `state/HOLD.json` absent; `state/HOLD_history.jsonl`'s 3rd (most recent) entry shows `cleared_at: 2026-08-10T12:57:53Z`. Repair + repair-extension both verified closed in prior cycles.
- **3 FAILED SLURM legs this cycle, all superseded — not a live problem.** `204523`/`204529`/`204535` (`r3-adr5-r2s3B3-pfc-s{0,1,2}`) FAILED (exit `1:0`, ~5s each) because the vendored pfc lift in `r2s3_lf_train_signal-B3`'s tree correctly refused the amended `panel_data` convention (ADR r2-0004 registration discipline firing as designed) — re-vendored on branch `8ce61fd` and resubmitted clean as `223738-40` (all COMPLETED). Not ledgered as compute cost under their original IDs.
- **Gates** (`state/gates.md`, read-only): G1-r3 GREEN (2026-08-05, unchanged), G2-r3 GREEN (2026-08-07, ADR r3-0004 scope, unchanged this cycle — see the internal-staleness flag above re: whether this should be re-scoped for the 6-ds panel), G3-r3 GREEN (2026-08-10 stale-checkpoint repair rebuild; see internal-staleness flag re: table not yet reflecting ADR r3-0005 phase 2's 6-ds re-certification). No gate is RED or disputed.
- No `reopen_candidate: true` cards. No `state/streams/{stream}.json` abandonment markers (directory does not exist; no stream has 3 consecutive skipped/blocked batches — all 4 streams have 2/2 batches `complete`). No `blocked.md` found anywhere under `experiment_cards/`, `worktrees/`, or `state/` (round-3 scope).

## Timing ledger

`state/timing_ledger.json`: 65 entries (28 → 65 this cycle, +37). New this cycle: r3s1_factorised-B2 (3 seeds, closed-form `epochs:0`, ~11.3-11.5min each), r3s2_field_reach-B2 (3 seeds, ~44-55min each), r3s3_lf_value-B2 (3 seeds, ~98.6min each), r3s4_audit-B2 (3 seeds ~2.5-7.9min + 1 pricing leg 0.5min), ADR r3-0006 film-transfer denominator (3 seeds, ~20.7min each), ADR r3-0006 U-Net baseline (3 seeds, ~56.3min each), ADR r3-0005 phase-2 pfc re-score (18 legs across r2s1-B2/r2s1-B3/r2s2-B1/r2s3-B3/film-pfc/unet-pfc x 3 seeds, ~1.4-8.3min each; the 3 originally-FAILED r2s3-B3 legs are intentionally excluded, only their successful re-vendored resubmissions are ledgered). Re-validated as parseable JSON after the write.
