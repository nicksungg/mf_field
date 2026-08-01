# Summary so far — `r2s3_lf_train_signal`, batch 3

Stream question (program.md §12.3): how much does LF, available only during
training, help a condition→HF model? Launch anchor = best-floor panel geomean
**23.063617** (`state/anchors/r2s3_lf_train_signal.json`); certified
per-dataset `min_claimable_effect` from `state/noise_floor.json` (certified
2026-07-31, `provisional: false`): ifc_poisson 0.9377041,
sharp__cahn_hilliard 0.0912454, sharp__fisher_kpp_2d 0.0007137,
sharp__allen_cahn_2d 0.8797047, sharp__phase_field_crystal_2d 0.2130273,
ext__helmholtz_2d 2.9529916; panel geomean mce 1.1418668.

## What the stream has established (B1, B2)

`experiment_cards/r2s3_lf_train_signal/batch_2/B2.json` (status `complete`,
job 66185845, 17 legs, seed 0 only, `provisional-single-seed`) shipped the
matched, step-matched, normalization-matched ±LF contrast at N_hf = 5:

- **ifc_poisson**: `A0_nolf` 8.1344 → `A1_lf_cov` 2.1690 (LF at all rungs/all
  conditions, no penalty) → `A2_lf_cov_null` 3.4550 (PRIMARY, + null penalty).
  Value-of-LF **A0−A1 = +5.9654**, **A0−A2 = +4.6794** (4.99× mce). F1
  confirmed; sign flip vs B1's −7.3497.
- **sharp__cahn_hilliard** (m = 15 null deficit): A0 30.0783, A1 12.6346
  (draw 0 only), A2 13.34/13.18/12.83 over 3 HF-subset draws;
  `A3_lf_paired` (LF only at the 5 covered conditions) 30.9058 — *worse* than
  no-LF (part 5 M5: paired LF is mildly harmful).
- **sharp__fisher_kpp_2d** (m = 0): effect +1.2228, but **no arm beats the
  in-regime train_mean floor** (part 5 M3; ADR r2-0003 incomplete-condition
  bound).
- Part 5 M1/M2: the card's headline mechanism (null-direction penalty) is
  **net harmful where active** (ifc −1.286, ch −0.708 vs the penalty-free A1);
  the LF value is carried by plain **coverage**, not the penalty.
- Part 7 three-channel taxonomy: (i) direction supply (HF-design null space),
  (ii) row-space fit, (iii) level/amplitude. Shares: ifc 57–60 / ~40 / n.a.;
  ch 68 / 40 / 23; fk 0 / small / 77. Promoted tools:
  `tools/null_family_ceiling_audit.py`, `tools/design_coverage_audit.py`.

Part 7 `next_direction` asks B3 to be a **measurement-completion** card:
(1) A1 on cahn_hilliard draws 1–2; (2) extend the A0-vs-A1 contrast to all 6
panel datasets (only 3 of 6 scored ⇒ no panel-level statement today);
(3) optional single amplitude-corrected penalty leg on cahn_hilliard.

## Prior websearch state (do not re-derive)

`websearches/r2s3_lf_train_signal/batch_1/report.md`: D1 (LF-teacher
distillation) and D2 (auxiliary LF heads) `preempted-but-MF-composition-open`;
D3 (LF-as-parameter-coverage) `novel` — **superseded** in batch 2.
`websearches/r2s3_lf_train_signal/batch_2/report.md`: E1 (linear/affine MF
channel) **preempted** (arXiv:1705.02956, arXiv:2508.08517); E2 (LF rows at
disjoint conditions fill the HF design's null direction)
**preempted-but-MF-composition-open**; E3b (Nyquist-pinned modes)
**preempted**; E4 (per-dataset gate) **preempted** (arXiv:2403.08118);
**E5 (the matched ±LF measurement for a neural condition→field surrogate at
N_hf ≈ 5) `novel`** — the stream's remaining publishable content and round-2
success criterion 1. In-repo lit reports
(`docs/reports/MF_Leaderboard_Beaters_2026_Report.md` line 46) record
`mf_fno_transfer_film` as the mandatory declared LF-pretrain→HF-finetune
baseline (§12.3).

## Open questions batch 3 must price against prior art

1. Does a **panel-scale** (6-dataset), matched ±LF accounting for neural
   condition→field surrogates exist? (E5 was `novel` at 3 datasets; scale-up
   could hit benchmark/survey prior art.)
2. Is **design coverage** (LF at conditions carrying no HF row) already the
   published explanation of when LF helps — i.e. is the nested-vs-non-nested
   DoE literature the preemption for M5?
3. Is the **three-channel decomposition** of transfer benefit (null /
   row-space / level) already published as a diagnostic?
4. Is an **amplitude-calibrated** null/subspace penalty distinguishable from
   the already-preempted null-space-learning family (E3c)?
