# Summary so far — stream `r3s1_factorised`, batch 1

All paths below are relative to `mffp_autoresearch/` unless absolute.

## 1. Websearch findings + prior-art verdict

Source: `round3/websearches/r3s1_factorised/batch_1/report.md` (5 iterations, 15 WebSearch, 8 usable fetches; the loop routed around a broken WebFetch with `curl` and recorded every blocked source as not-citable).

Three candidate directions were adjudicated.

- **D1** — ship the propagation-aware two-stage cross-coefficient closed-form head as the scored condition->HF arm — verdict **`preempted-but-MF-composition-open (cite)`**.
  The cascade mechanism AND the out-of-fold-corrected gate are both owned by Spyromitros-Xioufis et al., *Multi-Target Regression via Input Space Expansion* (arXiv:1211.6581, Stacked Single-Target / Ensemble of Regressor Chains); the OOF gate is textbook (mlxtend `StackingCVRegressor`); cross-coefficient completion for POD coefficients is published (Callaham/Brunton/Loiseau, JFM).
  Open residue: "Only the **composition**: OOF-corrected target-as-input stacking on **reduced-basis coefficients of a parametric PDE field**, where stage-1 targets are themselves regressed from the condition vector, scored on a copy-LF-skill panel in the **no-LF-at-test** regime at N_hf down to 5."
  The report is explicit that "The card must name SST/ERC and state that F25 rediscovered the published train/predict discrepancy."
- **D2** — the **condition-dimension discriminator** (per-direction OOF R^2 from the condition vs from the SET coefficients across all 6 cells, cond_dim 3/5/18/19/19/50) as a training-free pre-fit predictor of whether the two-stage arm pays — verdict **`preempted-but-MF-composition-open (cite)`**; the *idea* of a pre-fit "should we share?" predictor is published (arXiv:2310.16241 task affinity; arXiv:2607.06832 heterotopic kriging design geometry), the **independent variable** (condition dimension vs fit-row count) and the instantiation on PDE reduced-basis coefficients are not. Called out as "**Strongest novelty position available to this batch — and it is a diagnostic claim, not an architecture claim.**"
- **D3** — fitted closed-form floor battery (`affine_on_hf_train` + nn_condition + train_mean + zero) — verdict **`preempted (cite)`**; "Ship as a bug fix / instrument, never as a contribution."

Framing directive worth repeating: the published justification for one-regressor-per-mode ("POD reduced coefficients are decorrelated" / "modeling them independently avoids introducing artificial correlations") is a **second-order** argument that licenses nothing about nonlinear cross-coefficient dependence — which r2s1-B3's F24 measured at OOF R^2 0.92-0.94.

Also binding: "Every number in the card is new" — round-2's 18.6787 / 11.4148 / 12.6601 are void *as panel numbers*; the launch best-floor geomean is **36.3912**, re-verified at act time.

## 2. §12 conventions verbatim

Round-3 `program.md` §5: "Round-2 §12 methodological rules apply verbatim". Round-2 §12 preamble, the ADR r2-0004 additions, and §12.1 — the stream's governing conventions — reproduced byte-for-byte from `round2/program.md`:

>
> Common to all streams: quote the launch anchor (best-floor geomean 23.06) and
> the per-dataset floor table verbatim when designing; thresholds must clear
> the noise floor for the dataset(s) — while `state/noise_floor.json` is
> provisional, judge falsification clauses directly (§4.3); cite the
> websearcher's prior-art verdict; every proposal carries a complete `recipe`
> block; floor arms mandatory on model cards (§2.2).

> Two further conventions, added 2026-08-01 between batches (ADR r2-0004):
>
> - **Registration of model-side lifts.** Any family or instrument code that
>   resamples a field between grids (LF→HF lift, working-grid cap, prediction
>   resample) MUST use the ADR r2-0001 per-dataset conventions — vendor the
>   interpolators from `eval/panel_data.py` (the r2s2-B1/r2s3-B2 precedent) or
>   use `factory_mffp/models/_common/lf_registration.py`. A bare
>   `F.interpolate`/`zoom` on a panel dataset is the (r−1)/2 registration
>   defect and is a reviewer FAIL.
> - **Target-scaler pre-flight.** Any model card that trains on
>   `ext__helmholtz_2d` or `sharp__phase_field_crystal_2d` runs
>   `tools/target_scale_spread_audit.py` on those datasets pre-flight; an
>   `OUTLIER_DOMINATED` or `NEAR_ZERO_TARGETS` verdict requires per-sample
>   target normalisation (or a card-recorded justification for keeping a
>   global scaler). Round 1's `lf_resid_fno` helmholtz 4.14 / pfc 8206×-noise
>   failures were exactly these two verdicts left unhandled.

> ### 12.1 `r2s1_direct` (gap)
>
> - **Bar**: the per-dataset floor table (§2.3). Beating NN-in-condition with
>   400 train samples is necessary but nowhere near sufficient; the interesting
>   question is how close a from-scratch condition→HF surrogate gets to
>   skill 1.0 on each dataset.
> - Design priors (spec §6): FiLM-conditioned FNO **decoders** (condition →
>   spectral latent → field), DeepONet-style branch–trunk (branch on condition,
>   trunk on coordinates), spectral/implicit decoders (SIREN/modulated INR
>   class). Condition vectors are 2–19 dims; ifc_poisson's is 5-dim.
> - **ADR r2-0003 (corrects a spec §4 grounding fact)**: on pfc, fisher_kpp
>   and allen_cahn the condition vector is NOT complete — per-sample random
>   ICs live only in the fields, so condition→HF is a stochastic map and
>   deterministic models are bounded by the conditional-mean floor
>   (train_mean > NN on those floors is the symptom). Skill→1 is unreachable
>   there; design and falsify against the conditional-mean floor, and treat
>   bare FiLM-decoders as declared baselines (prior-art verdict: preempted).
> - **Helmholtz lesson** (r1 report §5): the zero field is the floor to beat
>   there — any helmholtz claim must show the zero-floor column.
> - **pfc caveat** (§2.3): denominator 0.007381 under variant C; no
>   fidelity gap under band-limited. State it on every pfc claim.
> - N_hf on ifc_poisson is 5 — every claim there is anecdote-grade; prefer
>   variance-reducing designs (r1 s1 lesson: ensembling, physics residuals are
>   out per ADR 0009 — physics-agnostic at test).
> - Overfitting is THE central threat at these sample counts; r2s4's
>   overfitting-anatomy diagnostics feed this stream. Train/val discipline in
>   the recipe is mandatory (no test-split peeking; the round-1 D3 val_idx
>   double-consumption caveat is the cautionary tale).

Round-3 amendments that override the quoted numbers: the launch anchor is **36.3912** not 23.06 (`round3/program.md` §2); ADR r2-0003's incompleteness caveat is **retired** — "The IC coefficients ARE in the condition vector now" (`round3/program.md` §1), which is exactly what raises cond_dim to 18/19/19/50 on the four sharp cells; the pfc denominator caveat now reads 0.018257409062703473 (crystalline-box swap, ADR r3-0002); and §2's **affine-floor rule** adds `affine_on_hf_train` as a mandatory reported arm on every ifc cell.

## 3. Within-stream prior cards

`round3/experiment_cards/` does not exist — batch 1 is the stream's first card. The stream's *lineage* card is round-2 `experiment_cards/r2s1_direct/batch_3/B3.json` (status `complete`, `reopen_candidate: false`, build commit `2b030f02da70cde80c90de2463935461bd56debb`, worktree `round2/worktrees/r2s1_direct/B3`, family `models_r2/r2s1_stagefree_permode` — 16 source files present on disk). Load-bearing content:

- **part 7 `next_direction`**: "B4 for r2s1_direct should SHIP the propagation-aware two-stage closed-form head as the scored arm and settle both halves of the open question in one job" — plus "Do NOT spend a batch on widening the head's basis: turn 3 F20 shows every deployable relaxation of the SET gate, down to fitting all 51 directions, makes the panel geomean worse."
- **T3-F24**: on cahn_hilliard the head's discarded coefficients are predicted by its own SET coefficients at fit-fold OOF R^2 0.9410 / 0.9243 / 0.8446 / 0.6230 / 0.4514; a deployable closed-form two-stage head (tau2 = 0.1, 11 extra directions, 3 520 stage-2 parameters) scores 11.4341 on ch. Controls: allen_cahn max stage-2 OOF R^2 **+0.0054**, pfc **+0.0323**, fisher_kpp **+0.0430**, ifc_poisson **-0.0751** — all no-ops.
- **T3-F25**: the arm needs a **propagation-aware** gate — selected/fitted on TRUE stage-1 coefficients it damaged helmholtz 3.8150->6.1666 and the panel 18.7500->19.9704; selected and fitted on **out-of-fold stage-1 predictions** it kept ch (11.4148, 13.65x that dataset's mce) and moved the panel to 18.6787.
- **M15 (hypothesis, moderate confidence)**: "the pattern is a CONDITION-DIMENSION effect [...] Testable prediction: at cond_dim >= ~10 a closed-form per-direction head under-performs a shared-representation estimator and a two-stage head recovers most of the gap; at cond_dim <= 3 neither moves. Caveat: n = 1 high-cond_dim cell in this panel."
- **M14 / falsification postmortem**: B3 was FALSIFIED by a clause (L2) that turn 1 showed was **unpassable by construction** — a tolerance priced against a mismatched estimator ("40-row calibration statistic, 20-40x too coarse for the quantity it decides"). This is the single most important design constraint on the present card.
- Promoted tools: `tools/coefficient_factorisation_audit.py`, `tools/head_subspace_surgery.py` (both verified present in `round2/tools/`).

Certified round-3 anchor cells (`round3/state/anchors/launch_anchors.json`, all four cards CERTIFIED 2026-08-07): `r2s1_direct-B3` seed geomeans **[28.3253, 28.1823, 28.1447]**, mean **28.2174**, ci95 [28.1096, 28.3253]; per-dataset mean skill pfc 46.7083 / allen_cahn 279.1165 / fisher_kpp 374.8381 / cahn_hilliard 12.5650 / ifc_poisson 8.2507 / ifc_heat 0.9964. This *is* the shipped condition-only closed-form law on the honest panel, and it already beats the best-floor anchor 36.3912.

## 4. Cross-stream cards

- `r2s2_stacked-B1` — via B3 part-7 `cross_stream_notes` item 2: its verdict that cahn_hilliard's fluctuation headroom is "condition-UNREACHABLE (all negative held-out R^2) = genuine class ceiling" was reached with the same per-direction factorisation "and should be re-tested cross-coefficient before being treated as a ceiling". Directly relevant: this batch's diagnostic answers it. Certified geomean 27.5068 with a known ifc_poisson seed-2 instability (seed geomeans [24.2391, 22.3658, 35.9154]).
- `r2s3_lf_train_signal-B3` — round 3's best certified card (geomean 15.5893; ifc_heat 0.0725). An LF-at-train family, outside this stream's arm class, but it fixes the honest scale of what condition-only arms give up.
- `r2s1_direct-B2` — certified 29.1188, seed geomeans [29.0812, 29.1193, 29.1558] (spread 0.0746): a second closed-form seed-spread instrument.

## 5. Reopen candidates

None. `round3/experiment_cards/` contains no cards; every round-2 `r2s1_direct` card carries `reopen_candidate: false` (verified by reading B1/B2/B3 JSON) and round-2 state is immutable (round-2 §5.13), so no round-2 card is a round-3 reopen candidate. Resolution recorded in `iteration_1.md` §Status.

## 6. What is UNKNOWN

1. **Is the cahn_hilliard cross-coefficient effect a condition-dimension mechanism or a dataset accident?** This is M15 and it is the stream's whole question. Round 2 could not answer it (n = 1 high-cond_dim cell). Round 3 makes it n = 4 vs n = 2 *for free*, because option-A regeneration put the IC coefficients into the condition vector: pfc 2->18, allen_cahn 3->19, fisher_kpp 2->50 (verified by diffing `round2/state/anchors/floors.json` against `round3/state/anchors_repaired/floors.json`; cahn_hilliard was already 19). Nobody has measured the discriminator on the new cells.
2. **Which way does higher cond_dim push?** Two opposed effects, both real, neither measured: more condition dims -> per-direction kernel/kNN maps are **starved** at 320 fit rows (M15's mechanism, favours stage 2); but more condition dims -> the condition now *determines* the field, so the per-direction condition maps should get **stronger** (disfavours stage 2). The experiment is decisive precisely because the sign is not predictable from theory.
3. **Does the pre-measured ch effect survive re-measurement?** cahn_hilliard data is byte-identical between rounds (same copy-LF reference 0.041802962686225575, same `nn_condition` nRMSE 0.9690069811741324, same cond_dim 19, no `_data_note` in the round-3 floors), so 12.6601->11.4148 is a same-data prediction — but it was **seed 0 only** and never ran at 3 seeds, and the certified 3-seed ch cell for the shipped head is 12.5650, not 12.6601.
4. **What is the actual per-cell noise floor for a closed-form condition-only family on the honest panel?** `round3/state/anchors_repaired/noise_floor.json` is `_provisional: true`, `_source: round1-batch0-rescaled`, derived from **LF-consuming** families, and it has **no `ifc_heat` entry at all**. Its `min_claimable_effect` values (pfc 8.8595, allen_cahn 16.4223, fisher_kpp 158.3322, cahn_hilliard 1.1604, ifc_poisson 0.2399) are policy floors (~10 % of a round-1 mean skill), not measurements of this arm class. The only *measured* panel-level instrument on the honest panel is the certified 3-seed geomean spread of the closed-form condition-only families themselves: 0.1806 (r2s1-B3), 0.0746 (r2s1-B2). r3s4 owns the re-certification; this card can supply per-cell 3-seed spreads for a closed-form condition-only family as a by-product.
5. **Why does the shipped closed-form law lose to a 6-dof affine fit on both ifc cells?** `affine_on_hf_train` scores ifc_poisson 1.5938 (oracle-affine residual 5.4e-16) and ifc_heat 0.9584, versus the head's 8.2507 and 0.9964. The head's SET gate, selected by LOO OOF R^2 on 5 rows, evidently discards structure a min-norm full-field affine LS keeps. Unmeasured, and it is a standing embarrassment for every condition-only claim on ifc.
6. **Is anything reachable beyond the level law?** `ref_dc_only` (the condition->level closed-form law) has never been reported per-cell on the honest panel, yet round-3 success criterion 1 is stated *against* it: "exceeds the condition->level closed-form law by >= 1 certified mce on >= 2 scored datasets".
7. **Does fisher_kpp have any usable basis at all?** M16 (low-moderate confidence): 92.1 % of its centered test energy was off the fit-fold POD bank, its skill "almost entirely a level result". With cond_dim now 50 and a 100x smaller copy-LF reference (0.02144950364640668 -> 0.00016524586579046429) this may have changed completely; unmeasured.
