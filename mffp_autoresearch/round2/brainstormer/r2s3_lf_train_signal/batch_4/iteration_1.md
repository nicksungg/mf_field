# Iteration 1 — `r2s3_lf_train_signal`, batch 4 (B4-or-close)

## Design context considered

- `summary_so_far.md` §6 (the six unknowns) and the batch-4 prior-art verdict, especially row (a) `preempted-but-MF-composition-open` and the instruction "The deliverable is the measured share of the ±LF effect the LF-free head absorbs — never the head itself."
- **program.md §12.3 verbatim** (quoted in `summary_so_far.md` §2) plus the §12 common conventions (launch anchor 23.063616857615774; per-dataset floor table; certified `min_claimable_effect`; complete recipe; the ADR r2-0004 registration and target-scaler pre-flight rules).
- The **immutables block (§4.5 of the brainstormer contract)**, reproduced in the self-check below.
- The stream anchor `state/anchors/r2s3_lf_train_signal.json` = **23.063616857615774** (`best_floor_panel_geomean`) and the per-dataset floors: hz 3.3441095587226317 (zero), ifc 10.054890929609687 (NN), ac 269.19587575878967 (NN), ch 23.180342227117514 (NN), fk 11.99311063309952 (mean), pfc 59.8117544948052 (mean).
- `state/noise_floor.json` — now **certified** (`_provisional: false`, `_source: r2s4_diag-B1`): ifc 0.9377041289531141, ch 0.09124535322300886, fk 0.0007136812826775696, ac 0.8797047190126648, pfc 0.21302734961699343, hz 2.95299157437233, panel geomean 1.1418668211296108.
- Pre-falsified levers (r1 §5: WNO backbone swap, LF low-mode freezing, diffusion prior for point accuracy) — none is adjacent to this proposal.
- B3's part 7: the ranked B4 candidates, the explicit do-not ("no more LF-supply engineering on fisher_kpp or pfc"), the two promoted tools, and the honest statement of the stream's state (3/6 claimable legs of unequal quality, one training seed).

### Pre-flight (executed by this brainstormer, read-only, no writes outside scratchpad)

Precedent: B3's brainstormer ran `tools/design_coverage_audit.py` pre-flight before drafting. I ran a read-only probe over B3's shipped dumps
(`mffp_autoresearch_outputs/round2/r2s3_lf_train_signal/B3/eval/results_<tag>/r2s3_coverage_panel/<ds>_e200_s0_preds.npz`; script preserved as `preflight_gain_probe.py` beside this iteration for audit; nothing else written outside this batch directory). Three facts came out, and they reshaped the design:

**(P-1) The arms interpolate their 5 HF train rows, so the naive train-fitted gain head is exactly the identity.**
Per-sample optimal scale `c_i = <p_i,y_i>/||p_i||²` on the 5 HF train rows is `1.0000` for all five rows on every dataset checked (ch d0/d1/d2, ac d0/d1/d2, ifc, fk d0, pfc d0); train-row mean rel-L2 is 0.0005–0.0026. A head fitted in-sample on those rows absorbs **0.00%** of the ±LF effect on every leg, measured. This is the "5 HF rows provably cannot" branch of B3's open question, and it is now a measured fact rather than a conjecture — but it also means the *interesting* question is no longer "does the achievable head work" (it cannot, in-sample) but "how far below the ceilings does the whole LF-free control class sit".

**(P-2) The test-fitted ceilings are large and dataset-dependent** (all TEST-FITTED, upper bounds, never claims). Absorbed share of the ±LF effect, per-sample oracle gain applied to A0 only: ifc **89.8%** (8.1344 → 2.7607 vs A1 2.1501); ch **46.8/43.8/45.4%** (30.0783 → 21.9128, 27.2499 → 20.8002, 24.7591 → 19.2366); ac **101.3/181.2/107.3%** (974.56 → 203.05, 248.59 → 182.91, 311.24 → 205.53 vs A1 ≈ 212.7); fk d0 50.4%; pfc d0 −214%. A single *global* test-fitted gain absorbs much less and on ifc/ac-d1/d2/pfc is actively harmful.

**(P-3) B3's own leg JSONs already contain LF-free controls stronger than A0_nolf, and they were reported as floors, never as substitutes.** `ref_linear_hfonly` (min-norm affine fit on the same 5 HF rows) scores **3.4744** on ifc against A0's 8.1344 and A1's 2.1501 — i.e. an LF-free, training-free control absorbs **77.9%** of ifc's +5.98 effect on its own. On ch the `ref_zero` floor (23.9217) beats A0 on two of three draws.

## Proposal reasoning

### The B4-or-close decision

Close-on-B3 would ship: F1/F2 falsified, mechanism M1–M6, two exported tools, and a criterion-1 claim resting on 3 legs of visibly unequal quality (ch strong, ifc mce-only by construction, fk fragile) at one training seed. The pre-flight shows that the leg quality is *worse* than the card records — ifc's headline +5.98 is 77.9% reproducible by a control already computed inside the same card, and fk's LF arm loses outright to its own `train_mean_n5` floor. Closing without that on the record would leave the round's central claim overstated in a way the round's own artifacts already refute. Carding B4 costs minutes of CPU on shipped artifacts and no new training. Decision: **card B4** as a training-free diagnostic.

### What to card

Direction (a) is the only cardable one and its *mechanism* is preempted (DiSOL's optional amplitude regressor; LCC's affine de-shrinkage). The open composition is the **substitution test**: how much of the certified ±LF effect an LF-free control absorbs on the same 5 HF rows. The pre-flight forces one enlargement of that framing: the honest LF-free control is not *only* the gain head — it is the best achievable LF-free alternative available to the same practitioner, which by P-3 includes the 5-row affine map and the training-free floors already in the card. Reporting only the (degenerate) gain head while a stronger LF-free control sits in the same JSONs would be cherry-picking. So the card prices LF against a **pre-registered LF-free control class**, with the gain head as the headline mechanism (verdict a), the split-ensemble as an arm only (verdict b, never a claim), and the floors/affine map as the "scratch-model" controls in the arXiv:2202.03365 sense.

### Alternatives weighed and rejected

1. **Close the stream on B3.** Rejected: see above; the cheapest available measurement materially changes what the round can claim, in both directions.
2. **Train the LOO-fold achievable head** (train on 4 of 5 rows, calibrate on the 5th, 5 folds × dataset × draw ≈ 35 GPU legs, ~60–90 min). Rejected for B4: its result is **bounded above** by the test-fitted condition-keyed ceiling this card computes for free, so if the ceiling does not absorb the effect the trained arm cannot either. It also adds a new family, a reviewer surface (stripped view, ADR r2-0004 registration), and 5-ALGO debug risk at the round's tail. Pre-registered as the *only* B5 trigger (see Status).
3. **Budget-matched no-LF ensemble as the card's claim.** Rejected — verdict (b) is explicit ("carries as a control arm only, never a claim"), and M5's generous non-budget-matched upper bound already answers the direction that matters (LF still wins by +219.17 on ac and +11.78 on ch; a budget-matched ensemble can only be worse). It rides along as a reported control column with the non-budget-matched label.
4. **Card the claimability-protocol repair (direction c).** Rejected — `preempted` by Bouthillier et al.; adopted as the card's statistics section instead (worst-draw gate against an axis-appropriate constant, ≥ the available draws, probability-of-improvement framing, per-test-sample bootstrap where the draw axis does not exist).
5. **More LF-supply engineering on fk/pfc.** Rejected by B3's explicit do-not; fk and pfc appear only as reported columns.
6. **A distillation / weight-averaging design.** Rejected by B3's M1b: an LF-trained arm is not a canonical solution (ac's three A1 models sit 100.5 skill units apart at inter-draw cosine 0.9485), so a single-teacher design assumes what the card refutes.

### Why this is not a rebadge

The card introduces no model family and makes no model claim: `card_type: diagnostic`, `epochs: 0`, no training, no round-1 code. The heads and the affine controls are post-hoc measurement instruments applied to already-shipped predictions. Per the websearcher: "A card that proposes *a gain head* is a rebadge; a card that proposes *the measurement — what share of the certified ±LF effect an LF-free gain head absorbs on the same 5 HF rows* — is the open composition."

## Proposal

- **Category**: `lf_train_signal / substitution audit — pricing the certified ±LF effect against the LF-free control class (achievable heads vs test-fitted calibration ceilings) on B3's shipped dumps`
- **Card type**: `diagnostic` (schema: "no training, single run, no seeds 1–2; `recipe.epochs = 0` is legal")
- **Anchor reference**: `null` (program §4.5 — all four round-2 streams; own-stream anchor 23.063616857615774 implicit)

### Motivation (quotes the prior-art verdict)

Verbatim from `websearches/r2s3_lf_train_signal/batch_4/report.md` "## Prior-art verdict", row (a):

> **(a)** LF-free **gain/amplitude head** conditioned on the condition vector, fitted on the same 5 HF rows, used as a **substitution test** for LF's train-time value (training-free probe on shipped dumps first, then one confirmatory arm) | **preempted-but-MF-composition-open** | … Only the **composition**: using the head as a **control that prices auxiliary low-fidelity training data**. No retrieved MF ablation output-scale-corrects its single-fidelity baseline (turn 4 t1), and the direct query "is the auxiliary-data gain just calibration?" returned **no usable results** (turn 3 t2). … **The deliverable is the measured share of the ±LF effect the LF-free head absorbs — never the head itself.**

and the framing instruction, verbatim: "Frame it as a **control baseline** in the sense of https://arxiv.org/abs/2202.03365 (blind-guess / scratch-model / maximal-supervision), sitting alongside the round's mandatory floor arms (§2.2)."

Within-stream driver: B3 part 7's open question — "The unresolved question is whether an ACHIEVABLE gain head … recovers most of it. If yes, the round's affirmative value-of-LF evidence largely reduces to an output-calibration trick that costs no LF data at all … if no, LF supplies a calibration signal that 5 HF rows provably cannot".

### Concrete config

New probe family `models_r2/r2s3_b4_substitution/` (worktree `worktrees/r2s3_lf_train_signal/B4`), `epochs 0`, seed 0, **no training, no GPU maths, no new predictions**. It reads only: (i) B3's 33 shipped leg result JSONs (for the exact `rel_l2_per_sample` arrays and the floor splits), (ii) B3's 33 `*_preds.npz` dumps (`pred_test`, `cond_test_raw`, `pred_hf_train`, `target_hf_train`, `cond_hf_train_raw`, `selected_train_rows`), (iii) HF test targets via `round2/eval/panel_data.py` (the offline reference path), (iv) `state/anchors/floors.json` and `state/noise_floor.json`. It never touches an LF field, and it writes nothing outside its own `DIAG_OUT`.

**Control class (all LF-free; per dataset, per draw).**
*Achievable* (no test targets anywhere in the fit): `A0_raw`; `A0 + H_global_train` (median of the 5 train-row optimal scales); `A0 + H_ridge_cond_train` (ridge-affine law for log-gain on the condition vector, LOO-λ over the 5 rows); `A0 + H_knn_cond_train`; `ref_linear_hfonly`; `ref_nn_condition_n5`; `ref_train_mean_n5`; `ref_zero`; `A0_split_ensemble` (mean of the 3 draw predictions — **labelled NON-budget-matched**, 15 HF rows and 3× compute, usable in one direction only).
*Ceilings* (TEST-FITTED, labelled on every line, never claims): `C1_global_test`; `C2_ridge_cond_loo_test` (the condition-keyed law `tools/residual_gain_learnability.py` fits by LOO on the test split — the decisive ceiling for "is the gain a function of something available at inference"); `C3_per_sample_oracle`. Each ceiling is applied to every achievable control, and the best is reported.

**Deliverables.** Per (dataset, draw): the raw effect `E_raw = skill(A0) − skill(A1)`; the substituted effect `E_free = skill(best achievable LF-free control) − skill(A1)`; the ceiling-substituted effect `E_ceil`; the **absorbed share** of each; the 7-reading claimability recount via `tools/effect_threshold_readings.py` (primary reading `worst_split_vs_mce`, per Bouthillier's "randomize every source / probability of improvement" and B3 M0); paired per-test-sample bootstrap CIs (B = 10000, seed 0) where the draw axis does not exist; the arm-symmetry column (the same heads applied to A1); the memorization statistics behind P-1; and `tools/map_dispersion_scale_shape.py --ensemble` for the split-ensemble control. Floor arms (`ref_nn_condition_n5`, `ref_train_mean_n5`, `ref_zero`, plus the frozen full-row floors seam-checked at 1e-9) are reported next to **every** calibrated variant: a control that "absorbs the effect" but loses to the best in-regime floor has learned nothing (§2.2 discipline carried into a diagnostic).

**Standing caveats carried on every row**: `ext__helmholtz_2d` report-only (ADR r2-0004: HF test fields reproduce from the condition vector to 2.2e-13 via two FFTs); pfc carries the band-limited-denominator caveat (`eval/copylf_baselines.json _notes.pfc`); ac/fk/pfc carry ADR r2-0003 (incomplete condition vector ⇒ conditional-mean bound and M2's shrinkage reward, so an intervention that *fixes* amplitude is expected to score worse there); all numbers stay `provisional-single-seed` (training seed 0).

### Recipe

```json
{
  "base_family": "none (training-free diagnostic probe; no model family is trained or scored. Reads ONLY r2s3_lf_train_signal-B3's shipped artifacts, build_commit dfcd46c6b51b5fe0bd533b9c670a7cdbf9d13830, job 66196690. NO round-1 reuse of any kind; reuses only round2/eval/panel_data.py + eval/nrmse.py read-only and four tools/ probes adapted to round-2 paths)",
  "base_commit": "9e10d414e35a96398f7b091bc84ddf936d88acc7",
  "family_dir": "models_r2/r2s3_b4_substitution",
  "datasets": "ifc_poisson,sharp__cahn_hilliard,sharp__fisher_kpp_2d,sharp__allen_cahn_2d,sharp__phase_field_crystal_2d,ext__helmholtz_2d",
  "epochs": 0,
  "seeds": [0],
  "env": {
    "R2S3B4_DUMP_ROOT": "mffp_autoresearch_outputs/round2/r2s3_lf_train_signal/B3/eval",
    "R2S3B4_SOURCE_FAMILY": "r2s3_coverage_panel",
    "R2S3B4_LEGS": "ifc_A0,ifc_A1,ch_A0_d0,ch_A0_d1,ch_A0_d2,ch_A1_d0,ch_A1_d1,ch_A1_d2,fk_A0_d0,fk_A0_d1,fk_A0_d2,fk_A1_d0,fk_A1_d1,fk_A1_d2,ac_A0_d0,ac_A0_d1,ac_A0_d2,ac_A1_d0,ac_A1_d1,ac_A1_d2,pfc_A0_d0,pfc_A0_d1,pfc_A0_d2,pfc_A1_d0,pfc_A1_d1,pfc_A1_d2,hz_A0_d0,hz_A0_d1,hz_A0_d2,hz_A1_d0,hz_A1_d1,hz_A1_d2",
    "R2S3B4_TREATMENT_ARM": "A1_lf_cov",
    "R2S3B4_CONTROL_ARM": "A0_nolf",
    "R2S3B4_ACHIEVABLE_HEADS": "identity,global_train,ridge_cond_train,knn_cond_train",
    "R2S3B4_CEILING_HEADS": "global_test,ridge_cond_loo_test,per_sample_oracle",
    "R2S3B4_ACHIEVABLE_CONTROLS": "a0_raw,a0_head,ref_linear_hfonly,ref_nn_condition_n5,ref_train_mean_n5,ref_zero,a0_split_ensemble",
    "R2S3B4_ENSEMBLE_LABEL": "non_budget_matched_upper_bound_15hf_rows_3x_compute",
    "R2S3B4_HEAD_TARGET": "per_sample_optimal_scale",
    "R2S3B4_HEAD_CLIP": "0.5,2.0",
    "R2S3B4_RIDGE_LAMBDAS": "1e-6,1e-5,1e-4,1e-3,1e-2,1e-1,1,10,100",
    "R2S3B4_KNN_K": "1,2,3",
    "R2S3B4_CAL_FOLDS": "loo5",
    "R2S3B4_SYMMETRY_ARM": "A1_lf_cov",
    "R2S3B4_READINGS": "verbatim_max_mce_spread,mce_only,paired_se_over_splits,persample_ci_excludes_zero,median_stat_verbatim,worst_split_vs_mce,log_effect_vs_own_range",
    "R2S3B4_PRIMARY_READING": "worst_split_vs_mce",
    "R2S3B4_NOISE_FLOOR_JSON": "mffp_autoresearch/round2/state/noise_floor.json",
    "R2S3B4_FLOORS_JSON": "mffp_autoresearch/round2/state/anchors/floors.json",
    "R2S3B4_FLOOR_TOL": "1e-9",
    "R2S3B4_SEAM_TOL_REL": "1e-3",
    "R2S3B4_BOOTSTRAP_B": "10000",
    "R2S3B4_BOOTSTRAP_SEED": "0",
    "R2S3B4_REPORT_ONLY_DATASETS": "ext__helmholtz_2d",
    "R2S3B4_CAVEAT_DATASETS": "sharp__phase_field_crystal_2d:band_limited_denominator,sharp__allen_cahn_2d:adr_r2_0003,sharp__fisher_kpp_2d:adr_r2_0003,sharp__phase_field_crystal_2d:adr_r2_0003",
    "R2S3B4_STREAM_PER_DATASET": "1",
    "R2S3B4_DIAG_OUT": "mffp_autoresearch_outputs/round2/r2s3_lf_train_signal/B4/eval",
    "_note": "keys prefixed _ are card directives, NOT passed to --env. The --env set is exactly the 27 R2S3B4_* keys above. epochs=0: the probe trains nothing and calls no optimizer; score_panel.py is NOT the entry point (the round-1 epochs-0 precedent is s2_beyond_copy-B1). Tools to adapt to round-2 eval paths and re-promote via the register turn: tools/residual_gain_learnability.py, tools/gain_calibration_ceiling.py, tools/effect_threshold_readings.py, tools/map_dispersion_scale_shape.py — their round-1 headers point at round1/eval/panel_data.py.",
    "_walltime": "--time 00:40:00. Basis: the pre-flight computed 9 of the 33 legs (ch x3, ac x3, ifc, fk, pfc) including per-sample oracle scales and target loads in under 4 minutes on the login node; 33 legs x 3 achievable heads x 3 ceilings is numpy-only and I/O-bound over 4.1 GB of dumps. CPU-only: no GPU maths is performed. Partition/gres per project.yaml; the orchestrator may drop the gres request since no CUDA kernel is launched.",
    "_memory": "R2S3B4_STREAM_PER_DATASET=1 means one dataset is resident at a time (largest: allen_cahn 6 legs x 100 x 65536 float32 + targets ~200 MB).",
    "_no_lf_assert": "the probe must RAISE if any code path opens an LF field or any file under stripped-out LF keys; every output JSON records lf_read_anywhere=false, field_input_at_test=false, trained_parameters=0.",
    "_declared_baseline": "program.md 12.3's mandatory declared baseline mf_fno_transfer_film is CITED, not re-run (ifc_poisson, 200 ep, seed 0, nRMSE 0.055637439592454, skill 1.5454844331237223, hashes d3d0ade9... / 9753ff24..., from r2s3-B1). This card trains nothing, so the rebadge question is answered by construction: no family is created."
  }
}
```

### Expected outcome

All figures below are **measured in the pre-flight** from B3's shipped artifacts (skill units, corrected denominators, training seed 0, `provisional-single-seed`) unless marked *predicted*.

| dataset | `E_raw` (draw-mean) | best achievable LF-free control | `E_free` worst draw | vs certified mce | ceiling-substituted `E_ceil` worst draw (per-sample oracle) |
|---|---|---|---|---|---|
| `ifc_poisson` | +5.9843 | `ref_linear_hfonly` 3.4744 | **+1.3243** (single native draw) | 0.9377041 → **1.41×** | +0.6106 → **below mce** |
| `sharp__cahn_hilliard` | +14.7762 | `ref_zero` 23.9217 / `ref_linear_hfonly` 22.959 | **+10.3548** | 0.0912454 → **113×** | +6.632 → **72.7×** |
| `sharp__allen_cahn_2d` | +298.90 | `ref_zero` 561.482 / `ref_linear_hfonly` 235.983 / `A0` 311.281 | **+23.611** | 0.8797047 → **26.8×** | −29.44 → **sign reversal** |
| `sharp__fisher_kpp_2d` | +1.3132 | `ref_train_mean_n5` 12.865–13.162 | **−2.568** | fails on sign | −2.568 |
| `sharp__phase_field_crystal_2d` | −2.5588 | `A0` / split-ensemble 54.55 | **−10.7** | fails on sign (M2 predicted) | −11.74 |
| `ext__helmholtz_2d` (report-only) | +5.7169 | `ref_zero` 3.3441 | **−2.615** | fails on sign; report-only regardless | −2.615 |

*Predicted* additions the card measures and the pre-flight did not: the achievable heads add **≈ 0.00** on every leg (P-1: the 5 train rows are interpolated to rel-L2 0.0005–0.0026 and their per-sample optimal scale is 1.0000, so `H_global_train` and `H_ridge_cond_train` are the identity to within clipping); the decisive unknown is `C2_ridge_cond_loo_test` on `ifc_poisson`, which sits between `C1_global_test` (0% absorbed — it is actively harmful there, 8.1344 → 8.1844) and `C3_per_sample_oracle` (89.8% absorbed). The documented prior is that it lands near the oracle: `tools/residual_gain_learnability.py`'s own header records LOO-linear R² = 0.919 for exactly this dataset's 5-D condition vector (round-1 `s1_poisson-B2`). I therefore predict `C2` absorbs 60–90% on ifc and 20–45% on ch.

**Net expected finding**: under the achievable-control gate the criterion-1 claimable set is **{ch (113×), ac (26.8×), ifc (1.41×)}** — still three datasets, but with different membership than B3's {ifc, ch, fk} and with `fk` retiring outright (its LF arm loses to its own `train_mean_n5` floor by 1.2–2.6 skill units on all three draws). Under the ceiling gate only **{ch}** survives. Every one of these deltas is far above the panel-geomean mce 1.1418668 and, where quoted per dataset, above that dataset's certified constant, except where the table says "fails".

### Expected falsification

**F1 (primary, achievable-control gate)** — FALSIFIED if, on fewer than **2 of the 3** datasets `{ifc_poisson, sharp__cahn_hilliard, sharp__allen_cahn_2d}`, the LF advantage measured against the **best achievable LF-free control** exceeds that dataset's certified `min_claimable_effect` on **every** HF-subset draw (`worst_split_vs_mce`; ifc 0.9377041289531141, ch 0.09124535322300886, ac 0.8797047190126648), with `ifc_poisson` additionally required to show a paired per-test-sample bootstrap 95% CI excluding zero because its single native draw makes it an mce-only pass by construction.
**F2 (class ceiling, the strong form)** — FALSIFIED if the LF advantage over the best **ceiling-corrected** control (`C1`/`C2`/`C3` applied to every achievable control) fails to exceed 0.09124535322300886 on every draw of `sharp__cahn_hilliard`; the corresponding ceiling failures on `ifc_poisson` (predicted +0.611 < 0.9377) and `sharp__allen_cahn_2d` (predicted sign reversal) are **pre-registered as the card's finding, not as its falsification**.
**F3 (mechanism)** — the statement "the 5 HF train rows carry no usable calibration supervision because the arm interpolates them" is FALSIFIED if the median |log per-sample optimal scale| over the 5 train rows exceeds 0.05 on **≥ 2 of the 6** panel datasets; if F3 fires, the achievable head has real supervision and its measured absorbed share replaces the ceiling argument as the headline.
**F4 (instrument seam)** — FALSIFIED (card reports no substitution numbers and flags an instrument break) if any raw arm skill recomputed from the dumps deviates from its B3-recorded per-leg skill by more than **1e-3 relative** (pre-flight max observed 1.31e-4, on `ac_A0_d0`), or if any full-row floor split re-read from the leg JSONs disagrees with `state/anchors/floors.json` at 1e-9.

## Status

- **Slot covered**: yes — one diagnostic proposal, `r2s3_lf_train_signal-B4`.
- **Skipped**: no.
- **Reopen candidates resolved**: none exist for this stream (all 12 round-2 cards carry `reopen_candidate: false`).
- **B4-or-close decision**: **card B4** (reasoning above).
- **Pre-registered B5 trigger** (the card's part 7 makes the call, not this iteration): a B5 is warranted **only** if F3 fires, or if `C2_ridge_cond_loo_test` absorbs ≥ 50% on `sharp__cahn_hilliard`; in either case the confirmatory arm is the LOO-fold achievable head (train on 4 of 5 rows, calibrate on the held-out 5th, 5 folds × dataset × draw, ~35 legs, 60–90 min by B3's timing ledger). If neither fires, the stream closes on B4 with the substitution audit as its final deliverable.
- **Immutables self-check**: **pass (11/11)** — below.

## Immutables self-check (positive evidence per item)

1. **Data read-only** — the probe reads B3's shipped `*_preds.npz` and result JSONs plus HF test targets through `round2/eval/panel_data.py` (whose docstring states it "reads the ORIGINAL dataset … for the offline reference/floor computations only"); it generates no data, adds no HF samples, keeps N_hf = 5 as B3 drew it (`selected_train_rows` is read, never re-drawn), and never downsamples HF to fabricate LF — it never opens an LF field at all (`_no_lf_assert` in the recipe).
2. **Panel + guard set fixed** — `recipe.datasets` lists exactly the six panel datasets of program §2.3 in B3's order; no guard leg is needed because nothing is trained and no panel win is claimed (§2.3 requires guards only for a card claiming a panel win).
3. **Eval layer / spec untouched** — the probe imports `round2/eval/nrmse.py` and `round2/eval/panel_data.py` read-only and writes only under `R2S3B4_DIAG_OUT` (`mffp_autoresearch_outputs/round2/r2s3_lf_train_signal/B4/eval`) and its own `models_r2/r2s3_b4_substitution/`; it requires no edit to `round2/eval/`, `project.yaml`, `program.md`, or any agent prompt.
4. **One nRMSE definition** — every score, including every calibrated variant, is computed by `eval/nrmse.py::nrmse` (verified to be `mean_i ||pred_i − target_i||₂/||target_i||₂`, which reproduces B3's recorded skills: my pre-flight recomputation of `ch_A0_d0` gives 30.0783 against the card's 30.07828518225339); F4 pins that seam at 1e-3 relative and the claimability recount uses the leg JSONs' exact `rel_l2_per_sample` arrays.
5. **Contract CLI fixed** — no CLI is changed; all 27 knobs are `R2S3B4_*` env keys inside the recipe block, following the round-1 `epochs: 0` precedent `s2_beyond_copy-B1` (`S2B1_*` keys + `S2B1_DIAG_OUT`).
6. **Seeds / tier epochs fixed** — `seeds: [0]`, `epochs: 0`; SCHEMA.md line 70–71 states verbatim that diagnostic cards have "no training, single run, no seeds 1–2; `recipe.epochs = 0` is legal", and no smoke/contract/full budget is consumed because no optimizer step is taken.
7. **Guarded factory surfaces untouched** — nothing under `factory_mffp/{eval,baselines,references,scripts,data}`, `factory.md`, or `akash/` is read for mutation or written; the probe's only factory-adjacent dependency is the read-only loader reached through `round2/eval/panel_data.py`.
8. **Checkpoint-resume from `<ckpt_dir>/last.pt`** — no training occurs, so no checkpoint contract is triggered; resumability is instead satisfied structurally by `R2S3B4_STREAM_PER_DATASET=1` writing one completed per-dataset JSON under `DIAG_OUT` before starting the next, so a preempted job re-runs only the unfinished datasets (minutes).
9. **Falsification threshold exceeds the certified noise floor for every cited dataset** — F1 cites ifc (predicted margin **1.3243** vs mce **0.9377041289531141** = 1.41×), ch (**10.3548** vs **0.09124535322300886** = 113×) and ac (**23.611** vs **0.8797047190126648** = 26.8×); F2 cites ch (**6.632** vs **0.09124535322300886** = 72.7×). All four exceed the certified per-dataset constants, and all exceed the panel-geomean constant 1.1418668211296108 except ifc's, which is why F1 additionally requires a per-test-sample bootstrap CI there.
10. **Not a pre-falsified lever** — the nearest pre-falsified items (r1 §5: WNO backbone swap, LF low-mode freezing, diffusion prior for point accuracy) are all *architectural* levers; this card proposes no architecture and trains nothing. The nearest *prior-art* hazard is the amplitude regressor itself (DiSOL arXiv:2601.09143; LCC arXiv:2508.01341), which the websearcher rules a rebadge **if proposed as a head**; the difference here is that the head is an instrument inside a substitution measurement whose deliverable is the absorbed share of a certified ±LF effect — the composition the verdict marks open. The nearest *successful* prior is round-1 `s1_poisson-B3`'s calibration head, cited as the source of the R² = 0.919 prior rather than re-proposed.
11. **Floor arms** — this is a diagnostic card, but the §2.2 floor discipline is carried anyway: `ref_nn_condition_n5`, `ref_train_mean_n5` and `ref_zero` are in the achievable control class itself (so the floors compete as substitutes, not merely as annotations), the frozen full-row floors are seam-checked at 1e-9 against `state/anchors/floors.json`, and F1/F2 reasoning is stated in terms of the *best* LF-free control, which on ch is the `ref_zero` floor (23.9217) and on fk is the `ref_train_mean_n5` floor (12.865–13.162) — the two places where a floor beats a trained arm.
