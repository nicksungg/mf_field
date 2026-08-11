# Brainstormer Report — Stream `r3s3_lf_value`, Batch 3

**Stream**: `r3s3_lf_value` · **Batch**: 3 (final, single slot) · **Total iterations**: 2 · **Slot filled**: 1/1 · **Reopen candidates resolved**: 0 (none exist)

> **REGISTRATION HOLD in force.** ADR r3-0007 (`docs/adr/0007-ifc-panel-composition-PROPOSED.md`) is PROPOSED. This report is transcribable the moment the hold lifts with **zero redesign under any of options A/B/C**: every clause is per-cell, the primary clause lives on the four sharp cells (untouched by the ADR), and the ADR's own execution plan states "per-dataset cells unchanged", so `c_ds`, `nrmse_film_mean` and `tau_rel` are ADR-invariant. The only transcription-time edits are the `R3S3B3_CELLS` list and the `_ifc_clause_status` note.

## Slot

- **Category**: `lf_value / pre-declared knee-predictability of the coverage ladder — a zero-anchor training-free structural prediction of the step-max knee cap on the film-transfer cells, sealed before any leg runs and confirmed by a minimal ratio-4 ladder, adjudicated in ADR r3-0006 film units`

- **Card type**: `model` (phase P is a CPU-only, zero-GPU pre-declaration stage; phase C trains 200-epoch legs)

- **Motivation**: The stream's own part-7 recommendation and the batch-3 scope both name knee-predictability, and the websearch prior-art verdict says the *direction of inference* is the one thing not preempted. Prior-art verdict K1, verbatim:

  > **K1 — pre-registered knee prediction** on the film-transfer cells: emit the training-free surrogate's predicted step-max knee cap *before any leg runs*, then confirm with a minimal 3-cap ladder — **preempted-but-MF-composition-open** — citations: `https://arxiv.org/pdf/2201.12150` (projective early stopping; b_sat; pre-exponential point); `https://arxiv.org/pdf/2210.14891` (BNSL: no way to extrapolate past an unobserved break); `https://kneed.readthedocs.io/en/stable/` (Kneedle knee detection); `https://arxiv.org/html/2606.02662` (MF: fixed ratio heuristic vs reactive tolerance); `https://arxiv.org/pdf/2102.01293` (exchange rate D_T; "cheaply predict the ideal pre-training ratio" listed as future work) — **What remains open**: "Do not claim saturation-point prediction, knee detection, or an exchange rate. Open: **zero anchors on the target cell** (all retrieved predictors consume a partial curve there); a **training-free structural** predictor rather than meta-features or a sibling-curve corpus; the **MF condition-coverage** axis with LF absent from the test path; and **pre-declaration + adjudication** of a numeric cap."

  B2 established the instrument post hoc on two cells (`tools/coverage_knee_surrogate.py`: Pearson 0.9842 on ch, 0.9774 on ifc_heat, same step-max knee cap on both) and its part 7 asks precisely for the pre-registered version. The card's claim is the direction of inference; `b_sat` / Kneedle / `D_T` are cited as METHOD, never as findings.

- **Concrete config**:

  **Phase P — pre-declaration (CPU only, no GPU, before any leg).**
  1. Run `tools/coverage_knee_surrogate.py --kernel both --lam 1e-3` on every film-transfer cell of the decided panel over the dense ladder `{5,10,20,40,80,160,320,FULL}` (clipped/deduped to each cell's per-rung uncovered pool), draws `0,1,2`, `--n-hf 5` (ifc cells: `--draws native`), `--strat-mask` where a mask exists, `--out` per cell.
  2. Build each cell's **confirming ladder** by the mechanical rule (no discretion): `r3 = c_hat` (the dense step-max knee), `r2 = max(2, round(c_hat/4))`, `r1 = max(1, round(c_hat/16))`, `r4 = FULL`, enforcing `1 <= r1 < r2 < r3 < r4`; if `c_hat == FULL`, use `r3 = round(FULL/4)`, `r2 = round(FULL/16)`, `r1 = max(1, round(FULL/64))`. **Recompute the surrogate's step-max knee on `{r1,r2,r3,r4}`**; that value is the registered prediction `c_pred` (a divergence from `c_hat` is flagged, not overridden).
  3. Also emit, per cell: `c_pred` under the linear kernel (specificity control), the 64-draw histogram of `c_pred` (fold-population enumeration for the `n_fit = 5` closed-form stage), the full predicted `R_surr` curve on the 4 rungs, and the two structural nulls (`design_rank` saturation cap, `nnc` field oracle).
  4. Seal: write `state/r3s3_lf_value/prereg_knees_B3.json` with `_sealed_utc`, git commit, tool sha256 and a payload sha256; paste the payload verbatim into card part 4 and the sha256 into `R3S3B3_PREREG_SHA256`. **No GPU job may be submitted before the seal exists.**

  **Phase C — minimal confirming ladder (GPU).** New family `models_r3/r3s3_knee_prereg`, vendored byte-for-byte from `models_r3/r3s3_row_efficiency` @ `eedcc655` with four changes: (1) the hardcoded `CAP_LADDERS` dict is replaced by ladders read from the sealed prereg (`R3S3B3_LADDER_FROM_PREREG=1`), with a startup assert on the prereg sha256; (2) dataset-generality — the ch-only hard-mask path becomes a model-free re-derivation on any cell (top 27 % of test rows by nearest-train-HF-field rel-L2), stratified readout reported for every cell; (3) `models_r3/_common/ckpt_binding.py` @ `da855da` adopted verbatim so `data_binding` is written into `last.pt` at every save (batch-3 contract requirement), with `roles_read = cond_only` for `A0_nolf` and `lf_at_train` for the LF arms; (4) film-unit reporting (`skill_film = nRMSE / nrmse_film_mean(ds)`) plus `tau_rel_film` on every emitted statistic. Everything else — backbone width 64 / 4 blocks / modes cap 12 `pinned_min_rung_nyquist`, AdamW 1e-3 / wd 1e-5 / cosine / clip 1.0, `steps = epochs x 25`, HF batch 5 / LF batch 16, `_step_rng(seed, step)` resume contract, `per_rung_max_fullpool` arm-invariant scaler and its invariance assert, the per-rung cap draw `np.sort(np.random.default_rng([split_seed, fid]).permutation(n_uncov)[:min(c, n_uncov)])` — is unchanged from B2. Test path is condition-only on the stripped view; LF never enters the test path.

  **Arms** (per cell, per HF draw, per training seed): `A0_nolf` (cap 0), `A3c_lf_uncov_cap` at `r1`, `r2`, `r3`, and `A1_lf_all` (= rung `r4 = FULL`). 5 legs. Sharp cells use `SPLIT_SEED in {0,1,2}` (B2's identical HF draws); ifc cells are native `N_hf = 5`, one draw.

  **Registered statistic** (identical formula for the surrogate and the trained ladder): `R(c) = (nRMSE(A0_nolf) - nRMSE(arm@c)) / (nRMSE(A0_nolf) - nRMSE(A1_lf_all))` per fold, averaged over folds; steps `s_i = R(r_{i+1}) - R(r_i)`, `i = 1..3`; **knee `K = r_{argmax(s)+1}`**; margin `M_R = max(s) - second-max(s)`; `M_film = M_R x E_ds / nrmse_film_mean(ds)` with `E_ds` = fold-mean `nRMSE(A0) - nRMSE(A1)`. Threshold-free in R by construction.

  **Adjudicability gate per cell** (pre-declared): ADJUDICABLE iff (a) `M_film > tau_rel_film(ds)` with a *certified* `tau_rel`, and (b) the per-seed knee is unanimous across seeds {0,1,2}. Reported but not gating: the 9-fold leave-one-out jackknife modal knee and frequency. Non-adjudicable cells are published as UNRESOLVED with their margins — a pre-declared outcome, never a silent drop.

  **Cell roles**: predictive (zero anchors) = `sharp__allen_cahn_2d`, `sharp__fisher_kpp_2d`, `sharp__phase_field_crystal_2d`, `ifc_poisson`; reproduction controls (knee already measured by B2) = `sharp__cahn_hilliard` (cap 80), `ifc_heat` (cap 5). pfc is registered **conditionally**: adjudicated only if a certified pfc `tau_rel` exists at analysis time (none exists today — r3s4-B2: pfc "is enumerated in NO falsification clause"); otherwise reported with its film-unit margin and an explicit non-adjudication flag.

  **Blocking pre-flights**: prereg seal + sha256 + `_sealed_utc` precedes every leg start; scaler arm-invariance assert; pfc LF-rung-set assert against the ADR r3-0005 spectral rung-1 scored-cell convention and `_copylf_def_hash`; `R3S3B3_DATA_BINDING_ASSERT` + `ckpt_binding` coverage on every `last.pt`; floor seam 1e-9 against `floors.json`; `tools/stale_checkpoint_audit.py --fail-on-stale` over this card's own outputs before any scoring; never `--datasets panel` (that resolves the ROUND-2 panel) — always the explicit cell list.

- **Recipe**:

```json
{
  "base_family": "models_r3/r3s3_row_efficiency @ eedcc655b70471687c9b7f8e537ad206eddd437c (branch round3/exp-r3s3_lf_value-B2, card r3s3_lf_value-B2), vendored BYTE-FOR-BYTE with provenance comments into the NEW family models_r3/r3s3_knee_prereg. PLUS models_r3/_common/ckpt_binding.py vendored byte-for-byte from commit da855da (branch round3/exp-r3s4_audit-B2, path models_r3/_common/ckpt_binding.py), which imports the UNEDITED round3/tools/ckpt_data_binding.py. NEW in this card: (1) ladders read from the sealed pre-registration instead of the hardcoded CAP_LADDERS dict; (2) dataset-general model-free stratification mask (top 27 percent of test rows by nearest-train-HF-field rel-L2) replacing the ch-only imported mask; (3) ckpt_binding save hook (batch-3 contract requirement); (4) film-unit reporting through state/anchors/film_denominator.json. NOT a round-1 family, NOT mf_fno_transfer_film (that is the ADR r3-0006 DENOMINATOR, never an arm here), NO teacher/distillation/pretrain-finetune/auxiliary-loss arm (all preempted or certified null on B1), and the B2 D-D mediator clause is NOT re-run (B2 part 7 item 4).",
  "base_commit": "eedcc655b70471687c9b7f8e537ad206eddd437c",
  "family_dir": "models_r3/r3s3_knee_prereg",
  "datasets": "sharp__cahn_hilliard,sharp__allen_cahn_2d,sharp__fisher_kpp_2d,sharp__phase_field_crystal_2d[,ifc_heat][,ifc_poisson]  -- the bracketed ifc cells are included IFF the ADR r3-0007 decision keeps them scored (option A: both; option C: ifc_heat only; option B: neither). Explicit list always; NEVER --datasets panel.",
  "epochs": 200,
  "seeds": [0, 1, 2],
  "env": {
    "R3S3B3_PHASE": "C",
    "R3S3B3_PREREG_JSON": "/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch/round3/state/r3s3_lf_value/prereg_knees_B3.json",
    "R3S3B3_PREREG_SHA256": "<filled at transcription from the phase-P seal; the driver HARD-FAILS if absent or mismatched>",
    "R3S3B3_PREREG_ASSERT": "1",
    "R3S3B3_LADDER_FROM_PREREG": "1",
    "R3S3B3_CELLS": "sharp__cahn_hilliard,sharp__allen_cahn_2d,sharp__fisher_kpp_2d,sharp__phase_field_crystal_2d",
    "R3S3B3_ARM": "A3c_lf_uncov_cap",
    "R3S3B3_LF_COND_SET": "uncovered",
    "R3S3B3_LF_COND_CAP": "<r1|r2|r3 from the sealed ladder for this leg's dataset>",
    "R3S3B3_SPLIT_SEED": "0",
    "R3S3B3_N_HF": "5",
    "R3S3B3_SCALER": "per_rung_max_fullpool",
    "R3S3B3_SCALER_INVARIANCE_ASSERT": "1",
    "R3S3B3_WIDTH": "64",
    "R3S3B3_BLOCKS": "4",
    "R3S3B3_MODES_CAP": "12",
    "R3S3B3_MODE_POLICY": "pinned_min_rung_nyquist",
    "R3S3B3_STEPS_PER_EPOCH": "25",
    "R3S3B3_HF_BATCH": "5",
    "R3S3B3_LF_BATCH": "16",
    "R3S3B3_LR": "1e-3",
    "R3S3B3_WD": "1e-5",
    "R3S3B3_SCHED": "cosine",
    "R3S3B3_CLIP": "1.0",
    "R3S3B3_LAMBDA_LF": "1.0",
    "R3S3B3_LF_LIFT": "match_copylf_convention",
    "R3S3B3_REF_ARMS": "nn_condition_n5,train_mean_n5,zero,affine_on_hf_train,nn_condition_full,train_mean_full",
    "R3S3B3_FLOORS_JSON": "/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch/round3/state/anchors_repaired/floors.json",
    "R3S3B3_FLOOR_TOL": "1e-9",
    "R3S3B3_FLOOR_TOLERANCES_JSON": "/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch/round3/state/floor_tolerances.json",
    "R3S3B3_NOISE_FLOOR_JSON": "/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch/round3/state/anchors_repaired/noise_floor.json",
    "R3S3B3_FILM_DENOM_JSON": "/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch/round3/state/anchors/film_denominator.json",
    "R3S3B3_FILM_UNITS": "1",
    "R3S3B3_MCE_MODE": "certified_r3",
    "R3S3B3_ANCHORS_JSON": "/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch/round3/state/anchors/launch_anchors.json",
    "R3S3B3_G5_FITSET_BAND": "1",
    "R3S3B3_DATA_BINDING_ASSERT": "1",
    "R3S3B3_CKPT_BINDING": "1",
    "R3S3B3_TARGET_SCALE_AUDIT": "1",
    "R3S3B3_STALE_CKPT_ASSERT": "1",
    "R3S3B3_LF_ROW_MANIFEST": "1",
    "R3S3B3_STRATIFY_ROWS": "1",
    "R3S3B3_HARD_MASK_MODE": "rederive_model_free",
    "R3S3B3_HARD_MASK_TOPFRAC": "0.27",
    "R3S3B3_MEAN_REMOVED_REPORT": "1",
    "R3S3B3_DUMP_TEST_PREDS": "1",
    "R3S3B3_ALIGNMENT_REPORT": "0",
    "R3S3B3_CKPT_EVERY_STEPS": "250",
    "R3S3B3_GUARD_NSUB": "off",
    "_phase_P": "CPU-only, NO GPU, runs BEFORE any leg: python tools/coverage_knee_surrogate.py --dataset <cell> --caps 5,10,20,40,80,160,320,<FULL> --n-hf 5 --draws 0,1,2 --kernel both --lam 1e-3 --out <prereg_dir>/<cell>_dense.json ; then the ladder rule; then a re-run restricted to --caps r1,r2,r3,<FULL> for the REGISTERED prediction; then --draws <64-draw list> for the fold-population histogram; ifc cells use --draws native. Seal into R3S3B3_PREREG_JSON with _sealed_utc, git commit, tool sha256, payload sha256. NO sbatch submission is permitted before the seal file exists.",
    "_ladder_rule": "r3 = c_hat (dense step-max knee); r2 = max(2, round(c_hat/4)); r1 = max(1, round(c_hat/16)); r4 = FULL (per-rung uncovered pool = the A1_lf_all arm). Enforce 1 <= r1 < r2 < r3 < r4 by decrementing to the next distinct integer. If c_hat == FULL: r3 = round(FULL/4), r2 = round(FULL/16), r1 = max(1, round(FULL/64)), registered prediction = FULL. RATIO-4 SPACING IS LOAD-BEARING: on B2's own ch table the ratio-2 dense ladder's deciding margin is 0.00606 R = 0.20-0.30x tau_rel_film and its per-seed knee FLIPS (80/80/40), while the ratio-4 ladder {5,20,80,395} gives margin 0.1218 R = 4.11-5.97x tau_rel_film and a 3/3 seed-unanimous knee 80. The rule reproduces {5,20,80,395} on ch from the surrogate's own predicted cap 80.",
    "_statistic": "R(c) = (nRMSE(A0_nolf) - nRMSE(arm@c)) / (nRMSE(A0_nolf) - nRMSE(A1_lf_all)) per fold (HF draw x training seed), fold-mean; steps s_i = R(r_{i+1}) - R(r_i) for i=1..3; knee K = r_{argmax(s)+1} in {r2, r3, FULL}; margin M_R = max(s) - second-max(s); M_film = M_R * E_ds / nrmse_film_mean(ds), E_ds = fold-mean (nRMSE(A0) - nRMSE(A1)). NO absolute R threshold anywhere (B2 part 7; websearcher directive 4; contrast arXiv 2510.14878's absolute-MSE sample complexity).",
    "_adjudicability": "ADJUDICABLE iff (a) M_film > tau_rel_film(ds) = tau_rel * c_ds with a CERTIFIED tau_rel, and (b) per-seed knee unanimous over seeds {0,1,2}. Reported not gating: 9-fold leave-one-out jackknife modal knee + frequency. tau_rel_film: ch 0.021736, allen_cahn 0.076103, fisher_kpp 0.045486, ifc_heat 0.335905, ifc_poisson 0.562718, pfc UNDEFINED (no certified tau; conditional clause).",
    "_grid": "PER TRAINING SEED (3 seeds -> 3 SLURM jobs). Per sharp cell: 5 legs (A0_nolf, A3c@r1, A3c@r2, A3c@r3, A1_lf_all) x SPLIT_SEED in {0,1,2} = 15 legs; 4 sharp cells = 60. Per ifc cell (native N_hf=5, one draw): 5 legs; both = 10. Plus 1 guard leg (heat_local, epochs 2, arm A1_lf_all). TOTAL <= 71 legs/seed, <= 213 legs. At B2's measured 1.972 min/leg (state/timing_ledger.json) ~2.33 h/job.",
    "_hf_subset_draws": "SPLIT_SEED in {0,1,2} draws N_HF=5 of the 400 HF train rows via np.sort(np.random.default_rng(s).permutation(400)[:5]) - IDENTICAL to B1/B2/r2s3-B3, so the ch A0/A1 legs form an exact reproduction seam against B2.",
    "_cell_roles": "PREDICTIVE (zero anchors on the cell): sharp__allen_cahn_2d, sharp__fisher_kpp_2d, sharp__phase_field_crystal_2d, ifc_poisson. REPRODUCTION CONTROLS (knee measured by B2): sharp__cahn_hilliard (cap 80), ifc_heat (cap 5). pfc adjudicated ONLY if a certified pfc tau_rel exists at analysis time; otherwise reported with its film-unit margin and a non-adjudication flag.",
    "_adr_robustness": "The ADR r3-0007 execution plan states 'per-dataset cells unchanged', so c_ds / nrmse_film_mean / tau_rel do not move under any option; only panel aggregates do. Clauses are PER CELL, so demoting a cell deletes exactly its clause. The primary clause lives on the four sharp cells, present under A, B and C. The ifc cells are near-certainly UNRESOLVED anyway: clearing tau_rel_film 0.3359 (ifc_heat) / 0.5627 (ifc_poisson) needs M_R*E > 0.01214 / 0.02488 nRMSE against effects of order 0.025-0.03 nRMSE, i.e. M_R > 0.4-0.8.",
    "_floor_arms": "Every leg reports scored nRMSE and skill_film beside nn_condition / train_mean / zero from state/anchors_repaired/floors.json (ch 0.969007 / 1.001977 / 1.0; allen_cahn 0.979959 / 1.001702 / 1.0; fisher_kpp 0.067797 / 0.064562 / 1.0; pfc 1.187748 / 0.877766 / 1.0; ifc_heat 0.103164 / 0.130729 / 1.0; ifc_poisson 0.289472 / 0.324149 / 1.0), plus affine_on_hf_train on both ifc cells (0.070918 / 0.057375, program.md section 2). The per-cell FLOOR-CROSSING RUNG (smallest ladder rung whose scored nRMSE beats all three training-free floors) is a mandatory deliverable. Any nn_condition-priced statement carries that arm's fit-set noise band (G5 adoption, scope rule 5). Mean-removed nRMSE is additionally reported on fisher_kpp and ifc_heat (level-domination).",
    "_reporting_discipline": "ch is REFERENCE-FREE (ADR r3-0003 D2, MDD 1.7077): report ratios, R and film units, never a ch copy-LF skill delta. Every ifc number carries affine_on_hf_train and the paper bar. pfc carries the weak-fidelity-gap denominator caveat. Prior art is cited as METHOD ONLY: b_sat / projective early stopping (arXiv 2201.12150), Kneedle (kneed.readthedocs.io), effective data transferred D_T = k(D_F)^a N^b (arXiv 2102.01293), pre-registration for predictive modelling (arXiv 2311.18807). The novelty sentence is: BNSL states 'there does not (currently) exist a way to extrapolate the scaling behavior after that additional break' (arXiv 2210.14891) and the survey's meta-feature branch still consumes a partial empirical curve on the target dataset - our prediction uses ZERO anchors on the target cell. INSTRUMENT PRICING, declared before the prediction: the surrogate is a SHAPE/KNEE predictor, not a baseline (ch full-pool 0.5753 vs trained 0.5178, 11 percent worse in level; --kernel linear collapses to Pearson 0.622). TERMINOLOGY: the stratified subpopulation is FORWARD-SENSITIVE, defined inline; 'non-identifiable'/'unidentifiable' are BANNED; the rarity+memorization account (arXiv 1906.05271) is cited as the nearest published mechanism and explicitly contrasted (27/100 rows, condition distance 1.015-1.016x bulk).",
    "_blocking_preflights": "(1) prereg seal exists, sha256 matches R3S3B3_PREREG_SHA256, _sealed_utc precedes every leg start; (2) per_rung_max_fullpool arm-invariance assert with the recorded s_rung/s_hf table; (3) pfc LF-rung-set assert against the ADR r3-0005 spectral rung-1 scored-cell convention and _copylf_def_hash; (4) data-binding assert + ckpt_binding coverage on every last.pt; (5) floor seam 1e-9 vs floors.json; (6) tools/stale_checkpoint_audit.py --fail-on-stale over this card's outputs BEFORE scoring; (7) never --datasets panel.",
    "_slurm": "three jobs, one per training seed; partition gpu, gres gpu:nvidia_h200:1, --time 06:00:00 (2.6x headroom over the 2.33 h estimate, preemptable partition), --mail-user=ezeng@caltech.edu --mail-type=END,FAIL. Per-leg done marker keyed on (cell, arm, cap, split_seed, n_hf, epochs_target); resume from <ckpt_dir>/last.pt.",
    "_note": "Keys prefixed _ are card directives, NOT passed to --env. The --env set is exactly the 49 R3S3B3_* keys above; each leg overrides only R3S3B3_ARM, R3S3B3_LF_COND_SET, R3S3B3_LF_COND_CAP and R3S3B3_SPLIT_SEED (the guard leg also sets epochs=2). ARM<->selector binding asserted in smoke_eval: A0_nolf=(COND_SET none, CAP 0); A1_lf_all=(all, 0); A3c_lf_uncov_cap=(uncovered, CAP in the sealed ladder for that dataset). Any other combination raises."
  }
}
```

- **Expected outcome**:
  - **Primary (knee agreement).** Per predictive cell the pre-declared `c_pred` equals the trained step-max knee `K`. Chance-match probability is **1/3 per cell** (3 steps, knee in `{r2, r3, FULL}`); over the two always-certified predictive cells (`allen_cahn`, `fisher_kpp`) a joint chance match is 1/9, and 1/27 if pfc becomes adjudicable.
  - **Δ vs anchor**: **none claimed on the panel geomean.** The stream anchor (`r2s3_lf_train_signal-B3`, 11.1689 copy-LF units) is a reproduction seam that the `A1_lf_all` legs are only expected to reproduce; the launch best-floor geomean 38.8368 is untouched. The deliverable is a pre-registered prediction adjudicated in film units. Reported (not claimed): ch `A1_lf_all` expected at nRMSE ~0.518 → `skill_film` ~0.745, i.e. below the ADR r3-0006 film baseline on that cell.
  - **vs noise floor (film units, `tau_rel_film` = `tau_rel` x `c_ds`).** ch retro-check on B2's own data with this exact ladder rule: margin **0.1218 R** = **0.0894–0.1297 film units = 4.11–5.97x** `tau_rel_film`(ch) = 0.021736, seed-unanimous 3/3 (worst seed 0.0860 R = 2.9–4.2x). Expected margins on the new cells 0.08–0.30 R: `allen_cahn` (`tau_rel_film` 0.076103, E ~0.45–0.55 nRMSE) ⇒ **1.3–3.9x** floor; `fisher_kpp` (`tau_rel_film` 0.045486, E ~0.03–0.06) ⇒ **1.8–4.4x** floor; pfc margin reported in film units against the launch-anchor caveat pending a certified tau. The ifc cells are pre-declared to be **UNRESOLVED** (would need `M_R > 0.4–0.8`) — a reportable metrology result that is itself evidence for ADR r3-0007.
  - **Secondary, reported only (never falsifying):** the surrogate-vs-trained curve deviation (`mean |ΔR|` over the 3 interior rungs, ch reference 0.0386 R = 1.57 `tau_rel`); the per-cell floor-crossing rung; the stratified forward-sensitive ladder on every cell (ch reference: no knee at any cap for the 27 hard rows); the `design_rank` and `nnc` structural nulls; the linear-kernel knee as a specificity control.

- **Expected falsification**: FALSIFIED if the sealed pre-declared rbf-surrogate knee cap misses the trained step-max knee cap on **≥ 2 adjudicable predictive cells**, or if the `sharp__cahn_hilliard` reproduction control misses its pre-declared cap 80 (instrument instability) — where a cell counts as adjudicable only when its trained deciding-step margin exceeds one certified `tau_rel_film` (0.076103 `allen_cahn`, 0.045486 `fisher_kpp`, 0.021736 ch; pfc only if a pfc `tau_rel` is certified; the ifc cells pre-declared non-adjudicable at 0.335905 / 0.562718) and its per-seed knee is unanimous over seeds {0,1,2}; exactly one miss among the adjudicable predictive cells is published as "predicts on some cells, not a law", and fewer than two adjudicable predictive cells is published as INCONCLUSIVE with the sealed predictions and measured margins as the deliverable. Supporting floor-arm condition (mandatory, spec §3): every confirming leg is reported against `nn_condition` / `train_mean` / `zero` (and `affine_on_hf_train` on ifc) with the per-cell floor-crossing rung; if no rung of a cell's ladder beats all three training-free floors, that cell's knee is published as a shape result only and carries no value-of-LF claim.

- **Prior-art verdict quoted**: see **Motivation** above — K1 row of `websearches/r3s3_lf_value/batch_3/report.md` §"Prior-art verdict", quoted verbatim with its five citations and its "What remains open" column.

- **Immutables self-check**: **pass (11/11)**.
  1. *Data read-only* — the card reads `round2/stripped_data` through the frozen `round2/eval/panel_data.py` loader in both phases; `N_hf` stays 5 (native for ifc), no HF is added, no LF is regenerated or downsampled; the only writes are the family dir, the sealed prereg JSON under `state/r3s3_lf_value/`, and the outputs tree.
  2. *Panel + guard set fixed* — the cell list is a parameter read from the decided panel, never a redefinition; the guard leg is `heat_local` from the unchanged guard set `{heat_local, fluid, sharp__sod_1d}`; the ADR is the operator's instrument for composition, and the card registers nothing until it is decided.
  3. *Eval layer / spec untouched* — `panel_data.py`, `nrmse.py`, `project.yaml`, `program.md` and agent prompts are imported or read only; `tools/coverage_knee_surrogate.py` is invoked with existing CLI flags (`--dataset --caps --n-hf --draws --kernel --lam --strat-mask --out`), no edit.
  4. *One nRMSE definition* — both the surrogate and the trained legs score through `round2/eval/nrmse.py` (the surrogate imports it directly, line `from nrmse import nrmse`); R is a ratio of those nRMSEs; training loss is untouched.
  5. *Contract CLI fixed* — legs run through the family's `smoke_eval.py` with the unchanged `--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed` signature; every knob above is an `R3S3B3_*` env key in the recipe block.
  6. *Seeds and tier epochs* — seeds exactly `{0,1,2}`, scored legs at the smoke tier 200 epochs, the guard leg at contract tier 2 epochs; no full-tier run is requested.
  7. *Guarded factory surfaces untouched* — nothing under `mf_field/factory_mffp/{data,baselines,eval,references,scripts}`, `factory.md` or `akash/` is read for write or edited; the family lives at `models_r3/r3s3_knee_prereg` inside this card's own worktree.
  8. *Checkpoint resume* — the vendored B2 family already resumes from `<ckpt_dir>/last.pt` with the `_step_rng(seed, step)` contract and `R3S3B3_CKPT_EVERY_STEPS=250`; the adopted `models_r3/_common/ckpt_binding.py` writes `data_binding` into that same `last.pt` at every save, and `tools/stale_checkpoint_audit.py --fail-on-stale` runs before scoring.
  9. *Threshold exceeds the noise floor on every cited dataset* — quoted: ch margin 0.1218 R = 0.0894–0.1297 film units vs `tau_rel_film` 0.021736 (**4.11–5.97x**, worst seed 2.9–4.2x), measured on B2's shipped table with this exact ladder rule; `allen_cahn` bar 0.076103 (expected 1.3–3.9x); `fisher_kpp` bar 0.045486 (expected 1.8–4.4x); pfc has no certified `tau_rel` and is therefore only conditionally adjudicated; `ifc_heat` 0.335905 and `ifc_poisson` 0.562718 are pre-declared non-adjudicable rather than claimed against. No threshold sits inside its statistic's own fold spread — the ratio-2 alternative, whose margin is 0.20–0.30x the floor and whose per-seed knee flips 80/80/40, was rejected in `iteration_1.md` for exactly that reason.
  10. *Not a pre-falsified lever* — nearest pre-falsified items: B2's absolute-`R >= 0.90` clause (knife-edge at 0.89838) and B2's linear-fit D-D mediator clause. This card re-uses neither: the statistic is the threshold-free step-max knee cap on a resolvable ladder, and no mediator clause is run (`R3S3B3_ALIGNMENT_REPORT=0`). The stream's certified-null levers (distillation teacher, LF-pretrain→HF-finetune, auxiliary MF losses) are not proposed; `mf_fno_transfer_film` appears only as the ADR r3-0006 denominator.
  11. *Mandatory floor arms* — `R3S3B3_REF_ARMS` carries `nn_condition` / `train_mean` / `zero` (+ `affine_on_hf_train` on ifc) from `state/anchors_repaired/floors.json` at seam 1e-9, the per-cell floor-crossing rung is a required deliverable, the falsification clause's supporting condition demotes any cell whose ladder never crosses all three floors to a shape-only result, and `nn_condition`-priced statements carry the G5 fit-set noise band.
  - *Additional hygiene check (scope rule 3, "no 0-epoch selector"):* phase P is not a selector over model candidates — it is the object under test. Every rung it names is scored out of sample at the full 200-epoch budget, and its prediction is sha256-sealed before any leg starts.

- **Anchor reference**: `null` (per program.md §4.5 policy for all four round-3 streams: gap/lever/diag streams carry their own-stream anchor implicitly; round 3 has no champion-re-targeting tuning stream).

- **Source iteration**: [iteration_2.md](iteration_2.md) (constraint derived in [iteration_1.md](iteration_1.md))

## Reopen candidates

| Candidate | Verdict (retry/drop) | Eased conditions | Source iteration |
|---|---|---|---|
| *(none — all eight round-3 cards carry `reopen_candidate: false`)* | n/a | n/a | [iteration_1.md](iteration_1.md) |

## Skipped slot

Not applicable — the single slot is filled.

## Summary table

| Slot | Category | One-liner | Status |
|---|---|---|---|
| B3 | `lf_value / pre-declared knee-predictability` (model) | Seal the training-free surrogate's step-max knee cap for every film-transfer cell before any leg runs, then confirm with a 4-rung ratio-4 ladder adjudicated in ADR r3-0006 film units at 1.3–6.0x the certified floor | filled (transcribable on ADR r3-0007 decision; no redesign under A/B/C) |
