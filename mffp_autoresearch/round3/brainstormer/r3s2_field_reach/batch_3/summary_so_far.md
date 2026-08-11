# Summary so far — Stream `r3s2_field_reach`, Batch 3

Sources read (paths relative to `mffp_autoresearch/round3/` unless absolute):
`websearches/r3s2_field_reach/batch_3/{report.md,iteration_*.md}`,
`experiment_cards/r3s2_field_reach/batch_{1,2}/B{1,2}.json`,
`state/batch3_scope_2026-08-10.md`, `program.md`, `../round2/program.md` §5/§12,
`docs/adr/0007-ifc-panel-composition-PROPOSED.md`, `docs/adr/0005-pfc-spectral-rung-repair.md`,
`state/anchors/{film_denominator,launch_anchors,r3s2_field_reach}.json`,
`state/anchors_repaired/{noise_floor,floors}.json`, `state/floor_tolerances.json`,
`worktrees/r3s4_audit/B2/scratchpad/reanalysis_turn_2_repricing.json`,
`tools/index.md`, `../round2/eval/{panel_data,score_panel}.py`,
`../round2/docs/round2_report.md` §2/§4/§6/§7.

## 1. Websearch findings + prior-art verdict

Three candidate directions were adjudicated (`websearches/r3s2_field_reach/batch_3/report.md`).

- **D1 — the emulator-ceiling ladder**: `preempted-but-MF-composition-open (cite)`.
  The strongest preemption is arXiv:2602.13416, which runs a frozen downscaler on real-coarse
  vs emulator-generated coarse *"to disentangle errors introduced by the downscaling step from
  those inherited from the LUCIE emulator"*; arXiv:2604.12440 states *"the oracle–predicted gap
  directly quantifies deployment readiness"* over a 4-rung ladder (96.34 / 93.28 / 24.63 / 16.71);
  Tacotron 2 §3.3.1 (arXiv:1712.05884) runs the crossed GT/predicted 2x2.
  What remains open: *"In **every** fetched instance the oracle intermediate is a deployable
  counterfactual ... No fetched source runs it (a) with an intermediate structurally unavailable at
  inference, (b) at N_hf = 5 with a closed-form corrector whose fold population C(5,3) is
  enumerable, or (c) priced against a certified training-free floor + certified baseline
  denominator in skill units. That triple is the claim."*
- **D2 — selection-input repair** (choose the corrector's regularisation on the emulator's held-out
  output): `preempted (cite)` — Perfect Prognosis / MOS (arXiv:2305.00974), IWCV
  (arXiv:1712.10050), GTA training (arXiv:1712.05884). *"usable ONLY as an instrument repair ...
  Presenting it as the idea is a rebadge."*
- **D3 — ceiling ratio as a prospective drop-the-intermediate decision rule**:
  `preempted-but-MF-composition-open (cite)`; every retrieved use answers *"which stage to
  improve"*, none answers *"should this stage exist at all"* — *"treat as an established absence ...
  It is a **methodological** contribution and must be registered as one."*
- Standing: **nothing is `novel`; the project record is 0-for-10.**

Brainstormer-facing items 4 and 6 are binding: register the **third (`no-LF`) rung** — the direct
condition→HF arm at matched budget, *"or the ceiling ratio has no denominator"* — and register in
film units against `state/anchors/film_denominator.json`.

## 2. Stream conventions (verbatim)

Round-3 `program.md` has no §12; it inherits the round-2 conventions. Round-3 §4 stream row:

> | `r3s2_field_reach` | gap | Can any architecture (including internal IC reconstruction from the complete condition vector) recover field-level structure the scalar-deep law cannot — and if not, is the negative certifiable? |

`../round2/program.md` §12.2 (`r2s2_stacked`, the inherited stream convention), verbatim:

> - **B1 is pre-directed by the spec** (Eloise's stacking proposal): train a FiLM-FNO **pseudo-LF emulator** (condition → LF field) on the TRAIN LF data, feed the best round-1 corrector — the s6 DC lineage / s4-B3 `dc_cleaned` stage (r1 geomean 0.1233–0.19 under OLD denominators; restate under corrected before claiming). Arms: **frozen corrector / fine-tuned corrector / end-to-end**, to separate emulator error from distribution shift (the corrector was trained on real LF; pseudo-LF is off-distribution for it).
> - Declared-reuse rule (§5.10a): the corrector is a frozen test-time sub-component — the reuse IS the experiment. ...
> - Failure is informative: if pseudo-LF → corrector loses to r2s1's direct models, the LF representation is not a useful bottleneck — that is the stream's falsification framing.

§12 preamble, verbatim: *"thresholds must clear the noise floor for the dataset(s) ... cite the
websearcher's prior-art verdict; every proposal carries a complete `recipe` block; floor arms
mandatory on model cards"*, plus **registration of model-side lifts** (ADR r2-0001 conventions;
*"A bare `F.interpolate`/`zoom` on a panel dataset is the (r-1)/2 registration defect and is a
reviewer FAIL"*) and **target-scaler pre-flight** on `sharp__phase_field_crystal_2d`.

Round-2 §5 immutable **#9 (stripped test view)**, verbatim: *"Models are evaluated ONLY against
`stripped_data_root` (test LF field files physically absent; `score_panel.py` points there and
refuses views that leak LF). Family code or scripts reading the original `data_root` at test time =
reviewer FAIL. Train-side LF use is free (that is the round's question)."*

Round-3 `program.md` §2 affine-floor rule, verbatim: *"Every card reporting an ifc number therefore
reports the fitted `affine_on_hf_train` floor next to it (ifc_poisson skill 1.59, ifc_heat 0.96);
an ifc claim that does not beat this floor has learned nothing beyond linearity, and skill < 1 on
ifc_heat is not by itself a strong claim."*

Batch-3 scope (`state/batch3_scope_2026-08-10.md`): **ONE card, the emulator-ceiling card**;
clauses in film units; `models_r3/_common/ckpt_binding.py` save hook mandatory; clause hygiene
(no threshold inside its own fold spread; justify a repair grid's FLOOR; enumerate C(N,n_fit)
instead of spending seeds); statistics ENERGY-weighted or held-out-loss; nn_condition-priced
claims carry the G5 fit-set band. **REGISTRATION HOLD** until ADR r3-0007 is decided.

## 3. Within-stream prior cards

- **B1** (`r3s2_stack_ic`, ic_synth front end → pseudo-LF → frozen DC corrector): anchor 12.9556
  (5-ds). F1 reach clause did not fire (the IC channel is real: ac 8.64x mce, ch 2.46x mce,
  shuffled-IC null worse everywhere); **F2 fired** — the trained stage-2 corrector earns <1.05
  skill units against 1.74/24.63 bars. Both ifc cells lost `affine_on_hf_train`.
- **B2** (`r3s2_route`, route switch + LSI repair): anchor **10.0853** (5-ds), *falsified on its own
  pre-registration* (G2 leg (iii): ifc_poisson band-3 unweighted mean |T| = 1.1851/1.1851/1.1494).
  Decisive measurements for batch 3:
  **F9** — the same frozen corrector reaches nRMSE **0.0195–0.0211** on ifc_poisson with **real LF**
  (better than the affine floor 0.0574, 6x better than the deployed A1 0.1194–0.1271) versus
  **0.119–2.147** with the emulator's pseudo-LF; the S2 oracle ladder was emitted only as a
  **train-held-out sidecar**, never as a scored arm.
  **F10** — leave-2-out over all **10** C(5,3) folds: ridge 1e-9 + k_cut clears leg (iii) on 10/10
  folds at held-out explained variance 0.9992, identical to the shipped repair to four decimals;
  the shipped band-limit costs 28% of held-out explained variance on ifc_heat, a cell that never
  trips at any fold.
  **F2** — the lambda actually needed is 5.264e-10–5.707e-10, 1750x below the grid's smallest
  non-zero point; the grid's FLOOR was never justified.
  **F7/F8** — the leg-(iii) statistic is an unweighted mode mean; the energy-weighted |T| never
  exceeds 1 anywhere, and on ac/fk/ch the top-octave transfer is a **canceller** (signed aggregate
  T = -1.0000 / -0.9996 / -1.0000), so the band-limit KEEPS the artefact there.
  **F11** — 74.2% of the panel route win comes from the two floor-disqualified ifc cells
  (ifc_poisson 65.1%, ifc_heat 9.1%); the claimable-3-cell win is 0.430x the full-panel figure.
  **F12** — per-cell delta/tau ratios are exactly unit-invariant; subset geomeans are not.
  **A7 ≈ A1 within 0.11 skill units on ac/fk/ch**: the stack's sharp-cell performance IS its front
  end, and the frozen corrector adds nothing there. On ifc_poisson A7 alone loses all four floors
  including zero, and the corrector recovers it (transport term ~ -3.04 nRMSE).
  Part 7 recommendation (verbatim, preference #1): *"A zero-GPU / low-GPU emulator-ceiling card ...
  (a) the real-LF oracle vs pseudo-LF ladder on all five cells, already emitted as S2 and needing
  only a proper scored arm; (b) selecting the corrector's regularisation on the EMULATOR's held-out
  output instead of on real LF ...; (c) the ridge = 1e-9 correction, carried as a footnote and not
  as an idea."*

## 4. Cross-stream cards

- **r3s4_audit-B2** part 7: the ifc `affine_on_hf_train` floor is a single-fold quantity — exhaustive
  LOO over C(5,4) moves ifc_heat 0.9584 → 1.8469 (fold sd 10.935 tau_rel, p95 20.53) and
  ifc_poisson 1.5938 → 4.2335 (+3.820 +- 0.719 tau_rel, 5/5 folds breach); quote the fold band via
  `tools/fitset_matched_n_audit.py`. Retraction: the round has been **over-warning** on ifc_poisson
  (absolute-bar caveat band is (0.691, 0.700), not 2.15x); ifc_heat's widens to (0.164, 0.389).
  G5 re-pricing (operator-adopted): matched-fit floors at **n = 320** are certified
  (`reanalysis_turn_2_repricing.json`, `_n_scored = 320`), nn_condition fit-set sd
  ac 13.78 / fk 16.41 / ch 0.65 / ifc_p 0.36 / ifc_h 0.097 skill units.
- **r3s1_factorised-B2** part 7: nRMSE is a mean of per-row ratios, so
  `amplitude_calibration_audit.py`'s **constant-norm oracle** caps any norm-blind arm —
  fisher_kpp 240.99 skill = 23.37x tau_rel, cahn_hilliard 1.92x, ifc_heat 1.23x.
  Any ceiling statement on those cells must disclose the amplitude cap.
- **r3s3_lf_value-B1** part 7: the stale-checkpoint class (now CLOSED) — run
  `zero_work_resume_scan.py` and bind dataset content into `last.pt`.

## 5. Reopen candidates

None. A scan of every round-3 card (`experiment_cards/*/batch_*/*.json`) returns zero entries with
`reopen_candidate: true`.

## 6. Prior-round record (tested directions relevant to this stream)

- **Stacking (condition→pseudo-LF → frozen corrector) beats the anchor but the corrector adds
  nothing** — r2s2-B1: *"stack stage adds only 0.0061 over `emul_only`"*; round-2 report §4:
  *"The stack's error is 99.98% stage-1 error on cahn_hilliard; a learned intermediate field is a
  re-parameterisation of the condition→HF class, never a new information channel."*
  **CONFIRMED, and re-confirmed on the repaired panel** by r3s2-B1 (F2) and B2 (A7 ≈ A1).
- **The oracle / real-LF gap on held-out TRAIN rows** — round-2 report §2 line 37 and §5 item 6:
  *"on held-out train rows raw copy-LF beats the round's fitted condition-only arms by 164.9x /
  77.0x / 12.3x / 49.5x (ac/ch/fk/pfc) — the no-LF-at-test regime, not architecture, dominates all
  of these numbers."*
  **CONFIRMED but never registered as a ceiling**: a part-7 caveat on r2s2-B3, measured before the
  panel repairs, with no fold enumeration, no corrector rung, no direct-arm denominator and no
  floor pricing. **Untested-on-repaired-panel** in that form (repairs: ADR r3-0001 ifc ladders,
  r3-0002 pfc box, r3-0003 ac trim, r3-0005 pfc spectral rung, r3-0006 film denominator).
- **Immutable-9 enforcement precedent** — round-2 report §7: *"stale killed-agent turn-3 partials
  for r2s2-B3 had read unstripped test LF; they were rejected and re-derived on the held-out train
  fold with `_no_test_lf_read=true`."* The held-out-train fold is the project's **established,
  enforced** substrate for any real-LF measurement. **CONFIRMED as procedure.**
- **Route contrast (direct vs stack) at matched budget** — r3s2-B2: affirmative at panel,
  unclaimable at every cell (F11). **REFUTED as a claim vehicle**; batch 3 must not repeat it.
- **LSI ridge / band-limit repair** — r3s2-B2 G2(iii). **REFUTED as a hypothesis**; survives only as
  an instrument setting with a justified grid floor (F2/F10).

## 7. What is UNKNOWN

1. **The ceiling itself is unmeasured as a first-class, pre-registered quantity.** B2's F9 is a
   sidecar on two ifc cells' held-out train rows with no direct-arm denominator, no fold
   enumeration on the sharp cells, and no floor pricing. Nobody knows, per cell, how much of the
   stack's error is *estimator* (what the corrector cannot fix even given a perfect LF) versus
   *hallucination* (what the emulator loses). r2s2-B3's 12–165x held-out-train figure says the
   ceiling is enormous; B2's A7 ≈ A1 says the realized fraction is ~0. **The product of those two
   statements — the realization fraction — has never been computed.**
2. **Whether the held-out-train split is a faithful proxy for the stripped test split.** The oracle
   rung is structurally unmeasurable on test (immutable #9; `score_panel.py` line 99 refuses views
   exposing test LF), so the ceiling can only live on held-out train rows. Whether the two
   *deployable* rungs rank and scale the same way on both splits is unknown, and it is the
   **licence condition** for reading the ceiling as a test-split statement.
3. **Whether selecting the corrector's regularisation on the emulator's own output** (the D2
   repair) recovers the ifc_poisson gap that band-deletion cost (F9/F10), and whether it helps or
   hurts on the sharp cells where the transfer is a canceller (F8) rather than an amplifier.
4. **pfc is scored but has no certified `min_claimable_effect`.**
   `state/anchors_repaired/noise_floor.json` (`_certified_utc` 2026-08-08,
   `_scored_panel_adr_r3_0004` = 5 cells) carries mce for ac / fk / ch / ifc_poisson / ifc_heat
   only; ADR r3-0005 restored pfc to the scored panel on 2026-08-10. No r3s2 card has ever run pfc
   (B1 dropped it under ADR r3-0004; B2 records
   `R3S2_TARGET_SCALER_PREFLIGHT: not_applicable_no_helmholtz_no_pfc_in_datasets`). Its scored cell
   is also **rung 1 with a spectral zero-pad lift** (`panel_data.py::SPECTRAL_RUNG_DATASETS = {"sharp__phase_field_crystal_2d": 1}`),
   not the `R3S2_EMU_RUNG=max` convention both prior cards used — an unexercised code path.
5. **The panel composition** (ADR r3-0007, PROPOSED: keep both ifc / demote both / demote poisson
   only). Any design that binds a clause to a panel-level statistic is hostage to it.
6. **Whether the ifc ceiling is claimable at all.** Both ifc cells lose `affine_on_hf_train` for
   every field arm this stream has built, and that floor is itself a ~+-11 tau fold-fragile
   quantity. B2's sharpest ceiling measurement (F9) lives on exactly the cell most likely to be
   demoted to report-only.
7. **What decision the ceiling ratio licenses.** D3 is an established absence in the literature:
   nobody converts an oracle gap into a *drop-the-intermediate* rule. Unknown: whether such a rule
   is decidable from three rungs at this sample size, and whether its verdict on our panel is
   DROP, EMULATOR-LIMITED, or KEEP — per cell.
