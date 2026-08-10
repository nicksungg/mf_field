# Brainstormer Report — Stream `r3s1_factorised`, Batch 2

(Persisted verbatim by the orchestrator from the brainstormer's inline return, 2026-08-10; the harness blocked that subagent's report-file writes.)

**Stream**: `r3s1_factorised` (gap) ·
**Batch**: 2 ·
**Total iterations**: 2 ·
**Slot filled**: yes (1 proposal, card type `model`) ·
**Reopen candidates resolved**: 0 of 0 (none exist)

## Slot

- **Category**: `gap / factorised-head stage-1 selection — permutation-calibrated per-direction predictability criterion replacing the SELECT_MAX clip, with the cap lift shipped beside it as a named bug-fix instrument, the SST input-space-expansion repair as a named preempted arm, and the n_SET/E_rem x reachability discriminator pre-registered on configurations the mechanism stage never saw`

- **Card type**: `model`

- **Motivation**: B1 certified the stream anchor at 24.9573 but the win is **one cell** (cahn_hilliard, +1.3073 vs `tau_rel` 0.3612) and stage 2 is a bitwise empty-gate no-op on the other four cells at every seed. The mechanism stage named the next gain precisely: *"`SELECT_MAX = 32` fired (`clip_rule = "raw set oversized -> top-32 by OOF R^2"`) [...] 0.0713 of encoded energy sits in unselected directions the raw condition predicts at OOF R^2 0.29-0.31 [...] **The cheapest available panel gain in this stream is raising `SELECT_MAX`**, not improving stage 2."* Round-3 success criterion 1 needs ≥ 1 certified mce on **≥ 2** scored datasets and the stream has one; fisher_kpp is the only resolvable sharp-cell negative under the matched 320-row budget (affine gap −104.2939, with 17× more of it outside the SET than inside). The websearcher requires the direction be **split**: the cap lift ships as an instrument, the *criterion* is the claim. Verdict quoted below.

- **Concrete config**: new family `models_r3/r3s1_predcrit_cascade`, vendoring B1's `models_r3/r3s1_twostage_crosscoef` verbatim with provenance comments; condition-only forward signature; stripped view only; leakage tripwire; no LF array opened at any stage; **no gradient-trained arm** (every arm closed-form, `epochs: 0`).

  **Five scored/matched arms, single-knob deltas** (stage-2 gate statistic and `tau2 = 0.1` frozen across all of them, so the only knobs are the stage-1 rule and the stage-2 input):

  | arm | stage-1 selection rule | stage-2 input | role |
  |---|---|---|---|
  | `A0_b1_replica` | tau 0.1, `SELECT_MAX` 32 | OOF stage-1 predictions | matched control + batch-1 reproduction seam |
  | `A1_cap_lift` | tau 0.1, `SELECT_MAX` 51 (= bank size ⇒ cap inactive) | OOF stage-1 predictions | **bug-fix instrument**, no novelty claim |
  | `A2_predcrit` | **permutation-calibrated per-direction threshold**, no cap | OOF stage-1 predictions | **DECLARED SCORED ARM** (D1's claimable criterion) |
  | `A3_predcrit_sst` | permutation-calibrated, no cap | `[OOF stage-1 predictions, condition]` | combined; **report-only**, pre-declared ineligible to become the headline ex post |
  | `A4_b1_sst` | tau 0.1, `SELECT_MAX` 32 | `[OOF stage-1 predictions, condition]` | isolates D4/SST alone |

  **The criterion.** Admit bank direction `d` iff `max_f OOF-R²(d, f)` exceeds the 95th percentile of its own **permutation null**: `B = 200` draws, each permuting the condition rows **within the fit fold only** (one shared row permutation per draw serves all 51 directions), recomputing the identical 5-fold OOF R² over the identical map bank `{affine, quadratic, RBF-KR, kNN}`. No count cap; `SELECT_MIN = 1` retained. This replaces *both* arbitrary constants (`tau = 0.1`, `SELECT_MAX = 32`) with a per-direction, per-dataset null — strictly more conservative than tau = 0.1 on pure-noise residuals (allen_cahn's leftover, max OOF R² 0.0013) and strictly more permissive on the directions the cap stranded (fisher_kpp, 0.29–0.31).

  **Small-N fallback.** At `N_fit = 5` (both ifc cells, LOO) the null is degenerate: `R3S1B2_PERM_MIN_ROWS = 20` reverts A1–A4 to A0's shipped rule there, asserted **bitwise** (gate G-F). Consequence declared up front: **this batch makes no ifc claim**, and all panel movement is sharp-cell movement.

  **Reference / floor arms** (all reported `@fit` on the scored arm's own 320-row fit fold — the paired comparand used by every clause — *and* `@full` on 400 rows as the frozen-floor seam, per part 7's hygiene rule and the r3s4 seam): `head_onestage` (stage 2 disabled, matched folds; also the anchor comparand), `dc_only` (the condition→level law required by success criterion 1), `zero`, `train_mean`, `nn_condition` (seam-checked 1e-9 to `state/anchors_repaired/floors.json`), `affine_on_hf_train` (seam-checked to `launch_anchors.json:ifc_floors_repaired`, reported on all five cells).

  **Report-only diagnostics** answering B1's `open_question`, on cahn_hilliard + allen_cahn only: stage-2 input replaced by (a) PCA-3 of the condition, (b) a seeded random 3-d projection, (c) the true SET coefficients under matched fit/predict. No falsification clause attached.

  **Build gates**: G-A anchor reproduction (A0 reproduces `state/anchors/r3s1_factorised.json:per_dataset_per_seed_skill` at 1e-9; RAISE, INFRA-class); G-B floor seams 1e-9; G-C stripped-view leakage tripwire + guards at the same tier; G-D target-scaler pre-flight on cahn_hilliard before any test tensor is opened; G-E stage-2 empty gate ⇒ bitwise no-op at 1e-12; G-F ifc small-N fallback bitwise no-op at 1e-12; G-G permutation-null scope tripwire (fit-fold rows only; selection frozen before the test tensor is opened).

- **Recipe**:

```json
{
  "base_family": "models_r3/r3s1_twostage_crosscoef vendored verbatim with provenance comments from branch round3/exp-r3s1_factorised-B1 @ 6770381 (own-stream batch-1 family; NOT a round-1 family, so round-2 immutable 10's declared-reuse roles (a)/(b) do not apply); condition-only forward signature; no round-1 or round-2 code beyond what B1 already vendored; no LF array opened at any stage; sole factory contact is a read-only import of mf_field/factory_mffp/data_adapters/loaders.py",
  "base_commit": "f7259d6ef1ff2364690419a02336af5e608769d5",
  "family_dir": "models_r3/r3s1_predcrit_cascade",
  "datasets": "sharp__allen_cahn_2d,sharp__fisher_kpp_2d,sharp__cahn_hilliard,ifc_poisson,ifc_heat",
  "epochs": 0,
  "seeds": [0, 1, 2],
  "env": {
    "R3S1B2_SCORED_ARM": "A2_predcrit",
    "R3S1B2_ARMS": "A0_b1_replica,A1_cap_lift,A2_predcrit,A3_predcrit_sst,A4_b1_sst",
    "R3S1B2_SCORED_ARM_LOCKED_PREREG": "1",
    "R3S1B2_STAGE_POLICY": "scored_arm_is_stage_free_no_wiener_no_blend_no_bg",
    "R3S1B2_TRAINED_ARMS": "none",
    "R3S1B2_EPOCHS_RATIONALE": "every arm is closed-form least-squares/kernel plus a permutation null of the same closed-form selection pass; family asserts epochs==0 and instantiates no gradient-trained arm",
    "R3S1B2_DATA_VIEW": "stripped",
    "R3S1B2_LF_AT_ANY_STAGE": "0",
    "R3S1B2_LEAKAGE_TRIPWIRE": "1",
    "R3S1B2_PANEL": "sharp__allen_cahn_2d,sharp__fisher_kpp_2d,sharp__cahn_hilliard,ifc_poisson,ifc_heat",
    "R3S1B2_REPORT_ONLY_EXCLUDED": "sharp__phase_field_crystal_2d",
    "R3S1B2_GUARDS": "heat_local,fluid,sharp__sod_1d",
    "R3S1B2_DIRECTION_BANK": "dc_meanfield,pod_0_49",
    "R3S1B2_POD_BASIS_N": "50",
    "R3S1B2_POD_DC_ORTHOGONALIZE": "1",
    "R3S1B2_CENTER_STAT": "norm_meanfield_over_geomean_norm_y",
    "R3S1B2_CENTER_TAU": "1.0",
    "R3S1B2_CENTER_FORMS": "fact,add",
    "R3S1B2_BASIS_FORM_MATCHED": "1",
    "R3S1B2_SELECT_INDEXING": "set",
    "R3S1B2_SELECT_STAT": "oof_r2_per_direction_best_family",
    "R3S1B2_SELECT_KFOLD": "5",
    "R3S1B2_SELECT_MIN": "1",
    "R3S1B2_A0_SELECT_TAU": "0.1",
    "R3S1B2_A0_SELECT_MAX": "32",
    "R3S1B2_A1_SELECT_TAU": "0.1",
    "R3S1B2_A1_SELECT_MAX": "51",
    "R3S1B2_A2_SELECT_RULE": "permutation_calibrated_per_direction",
    "R3S1B2_A2_SELECT_MAX": "51",
    "R3S1B2_PERM_B": "200",
    "R3S1B2_PERM_ALPHA": "0.05",
    "R3S1B2_PERM_SHARED_DRAWS": "1",
    "R3S1B2_PERM_SCOPE": "fit_fold_rows_only",
    "R3S1B2_PERM_RNG": "numpy_default_rng(1000+seed)",
    "R3S1B2_PERM_MIN_ROWS": "20",
    "R3S1B2_SMALL_N_FALLBACK": "shipped_tau_0.1_max_32",
    "R3S1B2_MAP_BANK": "affine,quadratic,rbf_kernel_ridge,knn",
    "R3S1B2_MAP_SELECT": "oof_r2_per_direction",
    "R3S1B2_MAP_RIDGE_ALPHA": "exact_loo_grid_1e-6:1e2:13",
    "R3S1B2_MAP_KNN_K": "1,2,4,8",
    "R3S1B2_MAP_RBF_GAMMA": "median_heuristic",
    "R3S1B2_STAGE2_ENABLE": "1",
    "R3S1B2_STAGE2_TAU2": "0.1",
    "R3S1B2_STAGE2_GATE_SELECT_ON": "oof_stage1_predictions",
    "R3S1B2_STAGE2_GATE_FIT_ON": "oof_stage1_predictions",
    "R3S1B2_STAGE2_INPUT_A0A1A2": "oof_stage1_predictions",
    "R3S1B2_STAGE2_INPUT_A3A4": "oof_stage1_predictions_concat_condition",
    "R3S1B2_STAGE2_MAP_BANK": "affine,quadratic,rbf_kernel_ridge,knn",
    "R3S1B2_STAGE2_KFOLD": "5",
    "R3S1B2_STAGE2_MIN_DIRECTIONS": "0",
    "R3S1B2_STAGE2_MAX_DIRECTIONS": "50",
    "R3S1B2_STAGE2_NOOP_ASSERT": "1e-12",
    "R3S1B2_DIAG_STAGE2_INPUT_ARMS": "pca3_condition,rand3_condition,true_set_coefficients",
    "R3S1B2_DIAG_STAGE2_CELLS": "sharp__cahn_hilliard,sharp__allen_cahn_2d",
    "R3S1B2_DIAG_REPORT_ONLY": "1",
    "R3S1B2_REF_ARMS": "head_onestage,dc_only,zero,train_mean,nn_condition,affine_on_hf_train",
    "R3S1B2_REF_FIT_BUDGET": "fit_fold_and_full",
    "R3S1B2_PAIRED_CLAUSES_USE": "at_fit_320",
    "R3S1B2_DECODER_ARMS": "none",
    "R3S1B2_FLOOR_SEAM_CHECK": "mffp_autoresearch/round3/state/anchors_repaired/floors.json@1e-9",
    "R3S1B2_AFFINE_FLOOR_SEAM_CHECK": "mffp_autoresearch/round3/state/anchors/launch_anchors.json:ifc_floors_repaired@1e-9",
    "R3S1B2_AFFINE_FLOOR_ALL_CELLS": "1",
    "R3S1B2_ANCHOR_REPRO_SEAM": "mffp_autoresearch/round3/state/anchors/r3s1_factorised.json:per_dataset_per_seed_skill@1e-9_on_A0",
    "R3S1B2_FOLD_MODEL_FRAC": "0.10",
    "R3S1B2_FOLD_CALIB_FRAC": "0.10",
    "R3S1B2_CALIB_FOLD_USE": "none_asserted_unused",
    "R3S1B2_FOLD_DISJOINT": "1",
    "R3S1B2_FOLD_RESAMPLES": "5",
    "R3S1B2_SMALL_N_PROTOCOL": "loo",
    "R3S1B2_SMALL_N_THRESHOLD": "20",
    "R3S1B2_DISCRIM_STAT": "E_rem_times_max0_reach_from_stage2_input",
    "R3S1B2_DISCRIM_THRESHOLD": "0.05",
    "R3S1B2_DISCRIM_PREREG_CONFIGS": "sharp__allen_cahn_2d,sharp__fisher_kpp_2d,sharp__cahn_hilliard|A1,A2",
    "R3S1B2_DISCRIM_TOOL": "mffp_autoresearch/round2/tools/coefficient_factorisation_audit.py@adapted",
    "R3S1B2_TARGET_SCALE_PREFLIGHT": "sharp__cahn_hilliard",
    "R3S1B2_PER_CELL_SEED_SPREAD_REPORT": "1",
    "R3S1B2_TIMING_PREFLIGHT": "1",
    "R3S1B2_TIMING_BUDGET_MIN_PER_SEED": "150",
    "R3S1B2_PERM_B_FALLBACK": "50",
    "R3S1B2_PERM_CKPT_BLOCK": "25",
    "R3S1B2_CKPT_RESUME": "1",
    "R3S1B2_CKPT_PATH": "<ckpt_dir>/last.pt"
  }
}
```

- **Expected outcome**

  Anchor: `state/anchors/r3s1_factorised.json` = **24.9573** [24.8726, 25.0662], cells ac 279.1165 / fk 374.8381 / ch 11.2577 / ifc_poisson 8.2507 / ifc_heat 0.9964.

  - **`sharp__fisher_kpp_2d` — the metric that moves.** A1/A2 mean skill expected in **275–345** (gain 30–100, point estimate ~315, gain ~60). Basis: the matched-budget affine gap is 104.2939 and the residual attribution puts 17× more of it outside the SET (+0.1202) than inside (−0.0072), while the stranded directions are condition-predictable at OOF R² 0.29–0.31. **vs noise floor**: fisher_kpp `tau_rel` = **10.3128** (`seed_mce` 5.8550) ⇒ the point estimate is **5.8× the floor**, and even the pessimistic end (30) is 2.9×.
  - **Panel geomean.** Point estimate **~24.10**, Δ ≈ **0.86** vs the anchor = **1.68× the certified `_panel_geomean` seed_mce 0.5083**. Pricing table (fisher_kpp-only gain → panel Δ → ×mce): 10.31 → 0.139 → 0.27×; 20 → 0.272 → 0.54×; 30 → 0.413 → 0.81×; **36.65 → 0.508 → 1.00×**; 46 → 0.645 → 1.27×; 60 → 0.856 → 1.68×; 100 → 1.502 → 2.95×; 104.29 → 1.576 → 3.10×.
  - **Round-3 success criterion 1, second cell.** `ref_dc_only` on fisher_kpp is 282.76 (`@full`; the `@fit` value is recomputed in-job). A A2 value ≤ ~272.4 makes fisher_kpp the stream's **second** cell exceeding the condition→level law by ≥ 1 certified mce. This is the stretch outcome, pre-registered as L3b below and explicitly not load-bearing for the card.
  - **Specificity (report-only, no clause).** allen_cahn: leftover residual is pure noise (max OOF R² 0.0013 / −0.0038), so a null-calibrated threshold should **not** admit it — expect |A2 − A0| < `tau_rel` 18.6198. cahn_hilliard: `n_SET = 3` was never cap-limited, so A1 ≡ A0 bitwise there; pod_5/pod_6 are at OOF R² −0.0059/−0.0170 **from the condition**, so the calibrated criterion should not pull them into stage 1 and the stage-2 gate (9/10/9 directions) should survive. ifc cells: A1–A4 ≡ A0 bitwise by G-F.
  - **Floor-arm comparison (mandatory, spec §3).** Expected A2 vs `state/anchors_repaired/floors.json`: fisher_kpp ~315 vs `nn_condition` 410.2818 / `train_mean` 390.7015 / `zero` 6051.5886 — clears all three; allen_cahn ~279 vs 475.8568 / 486.4148 / 485.5883 — clears; cahn_hilliard ~11.3 vs 23.1803 / 23.9691 / 23.9217 — clears; ifc_heat 0.9964 vs 1.3941 / 1.7666 / 13.5135 — clears. **Two standing negatives this card does NOT repair and must report**: ifc_poisson 8.2507 **loses** to `nn_condition` 8.0409, and both ifc cells lose to `affine_on_hf_train` (1.5938 / 0.9584) — carried forward from B1 unchanged by construction (G-F).

- **Expected falsification** (all at the 3-seed mean; all paired comparands `@fit` = 320 rows; **no clause enumerates `pfc`**):
  - **L1 (SHIPPING, cell)** — if neither `A1_cap_lift` nor `A2_predcrit` improves `sharp__fisher_kpp_2d` mean skill relative to the certified anchor cell 374.8381 by ≥ **10.3128** (fisher_kpp `tau_rel`; `seed_mce` 5.8550), the cap-stranded reachable energy is not recoverable by widening stage 1 and the batch's premise is FALSIFIED.
  - **L2 (SHIPPING, panel)** — if `A2_predcrit` fails to improve the panel geomean relative to the certified stream anchor 24.9573 by ≥ **0.5083** (certified `_panel_geomean` `seed_mce`), FALSIFIED. (Requires a fisher_kpp-equivalent gain ≥ 36.65; reachability priced in `iteration_2.md` R2.)
  - **L3 (NOVELTY SCOPE)** — if `A2_predcrit` fails to beat `A1_cap_lift` on the panel geomean by ≥ **0.5083**, the *criterion* claim is FALSIFIED, the batch must be reported as the `SELECT_MAX` bug-fix with **no novelty claim**, and D1's residue stays open. Card-level shipping verdict unaffected.
  - **L3b (criterion-1 second cell, sub-claim, non-load-bearing)** — if `A2_predcrit` fails to beat `ref_dc_only@fit` on `sharp__fisher_kpp_2d` by ≥ **10.3128**, the "second scored dataset for round-3 success criterion 1" sub-claim is FALSIFIED; L1/L2 stand independently.
  - **L4 (D4 / SST minimal repair — named, never claimed)** — if `A4_b1_sst` fails to improve `sharp__cahn_hilliard` mean skill vs `A0_b1_replica` by ≥ **0.3612** (ch `tau_rel`; `seed_mce` 0.0912), the input-space expansion of arXiv:1211.6581 is a **no-op on this panel** and is reported as a certified null. (Modal expected outcome; its firing is itself the deliverable.)
  - **L5 (D2 discriminator, pre-registered on unseen configurations)** — define, pre-unlock and on the fit fold only, `S(cell, arm) = E_rem × max(R_reach, 0)`, where `E_rem` is the fraction of encoded fit-fold energy outside the stage-1 admitted set and `R_reach` is the max over remaining directions of that direction's OOF R² **from that arm's stage-2 input**. Pre-registered threshold `S* = 0.05` (provenance: the three A0 measurements ac ≈ 0.000, ch ≈ 0.214, fk ≈ 0.000 — a fitted cut, applied out-of-sample). Prediction: stage-2 paired gain ≥ that cell's `tau_rel` when `S ≥ S*`, and |gain| < `tau_rel` when `S < S*`. Evaluated on the **six configurations `{allen_cahn, fisher_kpp, cahn_hilliard} × {A1, A2}`**, none of which the mechanism stage saw. Wrong on ≥ **2 of 6** ⇒ the `n_SET`/`E_rem`×reachability discriminator is FALSIFIED as a pre-fit predictor. (ifc cells are excluded by construction: N_hf = 5, G-F no-op, and F22 already showed the OOF R² statistic fails to transfer there.)

- **Prior-art verdict quoted** (verbatim from `round3/websearches/r3s1_factorised/batch_2/report.md`, "Prior-art verdict" table):
  - **D1** — "replace the `SELECT_MAX = 32` clip with an adaptive **predictability-criterion** basis selection (admit a direction when its coefficient is OOF-predictable from the condition), feeding the OOF-corrected stage 2" | **`preempted-but-MF-composition-open (cite)`** | Citations: "https://arxiv.org/abs/2605.27756 (energy-truncation critique + task-driven mode selection); https://arxiv.org/abs/2511.18260 (greedy certified RB selection; RB-vs-statistical error split); https://par.nsf.gov/biblio/10684905 (truncation-vs-regression error floor); https://arxiv.org/abs/1907.12239 (mode count swept against predictability); https://arxiv.org/abs/2606.29440 (closed-form LSQ readout on PCA coefficients)" | What remains open: "A **per-direction inclusion criterion keyed on out-of-fold predictability from the condition vector** — not energy, not reconstruction error, not a certified residual bound — with the retained set feeding an OOF-corrected cascade, in the **no-LF-at-test** regime at N_hf 5–400 on a copy-LF-skill panel. Five refutation queries returned no per-direction predictability screen. **Raising the numeric cap is a bug-fix, not the claim.**"
  - **D2** — "training-free pre-unlock discriminator `n_SET` / `E_rem` x reachability, predicting whether the cascade pays" | **`preempted-but-MF-composition-open (cite)`** | What remains open: "The **estimator**: a pre-fit statistic from the reduced basis' unexplained residual energy x condition-reachability, on PDE reduced-basis coefficients. Open — but this is a **repeat bet**: batch 1's `cond_dim` discriminator was falsified by its own controlled pair, and the replacement statistic was *fitted on the same 5 cells* it would be pre-registered against."
  - **D4** — "feed stage 2 `[predicted SET coefficients, condition]`" | **`preempted (cite)`** | "https://arxiv.org/pdf/1211.6581 — *Multi-Target Regression via **Input Space Expansion**: Treating Targets as Inputs*" | What remains open: "Nothing. Augmenting the original inputs with OOF-predicted targets **is** SST. Ship as the named minimal repair of batch 1's information loss; never as a contribution."
  - **D5** — "gated stagewise residual correction with a rejectable gate" | **`preempted (cite)`** | "https://arxiv.org/abs/2606.17460 — Operator Boosting: stagewise residual learning from the empirical-mean predictor with **validation-selected shrinkage** (grid includes zero ⇒ a stage can be rejected), on PDEBench/APEBench/The Well, 30 dataset-architecture pairs" | What remains open: "Nothing at the mechanism level. A card proposing 'a gate that can decline the correction' restates this paper."
  - Also binding, §For the brainstormer 3: "**Do not describe the family's architecture as new.** arXiv:2606.29440 (PCA-RaNN, Jun 2026) publishes a closed-form least-squares readout on PCA coefficients for parametric PDEs, and arXiv:2511.18260 (RB-DeepONet) publishes parameters→RB-coefficients with a certified greedy basis. Distinguish this card by the *selection rule* and the no-LF-at-test few-HF regime, not by the head."

- **Immutables self-check**: **pass (11/11)** — full positive evidence per item in [`iteration_2.md`](iteration_2.md) §"Immutables self-check — post-revision". Flagged in iteration 1 and revised: items 6/8 (permutation-null wall clock and preemption ⇒ added `R3S1B2_TIMING_PREFLIGHT` + `R3S1B2_PERM_B_FALLBACK` + `R3S1B2_PERM_CKPT_BLOCK`) and item 9 (L2 reachability ⇒ priced with the fisher_kpp-equivalent table, per the B3 M14 "unpassable by construction" postmortem). Two further revisions from the same pass: G-F added for the degenerate N=5 null, and the declared scored arm moved from A3 to **A2** so the headline does not ride on the riskiest knob.

- **Anchor reference**: `null` (per program.md §4.5 — all four round-3 streams are gap/lever/diag; the own-stream anchor `state/anchors/r3s1_factorised.json` = 24.9573 is implicit and is the comparand named in L2).

- **Source iteration**: [iteration_1.md](iteration_1.md) (design), [iteration_2.md](iteration_2.md) (self-revision + self-check; governing version)

## Reopen candidates

| Candidate | Verdict (retry/drop) | Eased conditions | Source iteration |
|---|---|---|---|
| *(none exist)* | — | — | [iteration_1.md](iteration_1.md) §Status |

All four round-3 batch-1 cards were read back and carry `reopen_candidate: false`; no r3s1 slot was skipped in batch 1, so there is nothing to reopen.

## Skipped slot

Not applicable — the slot is filled.

## Summary table

| Slot | Category | One-liner | Status |
|---|---|---|---|
| 1 | gap / factorised-head stage-1 selection | Replace the arbitrary `SELECT_MAX = 32` clip with a permutation-calibrated per-direction OOF-predictability criterion (the claim), shipping the bare cap lift beside it as a named bug-fix instrument and the SST concat as a named preempted repair; five single-knob closed-form arms, `epochs: 0`, 3 seeds. | filled (`model`) |

## Notes for the orchestrator (from the brainstormer's return)

- Batch-1 path convention confirmed: `/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch/round3/brainstormer/r3s1_factorised/batch_1/`. `mffp_autoresearch_outputs/round3/brainstormer/` does not exist; `mffp_autoresearch_outputs/round3/` holds only per-stream run artifacts.
- `base_commit` is current trunk HEAD `f7259d6ef1ff2364690419a02336af5e608769d5` on branch `mffp-trunk-eloise` (read at design time; the builder should re-resolve at worktree-creation time as B1 did).
- Every certified constant quoted here was read from `state/anchors_repaired/noise_floor.json` (`_provisional: false`, `_certified_utc: 2026-08-08T20:00:07Z`): panel `seed_mce` 0.5082844131597604; `tau_rel` — allen_cahn 18.61975759925883, fisher_kpp 10.312814173562199, cahn_hilliard 0.36124864423263325, ifc_poisson 0.6910000683054431, ifc_heat 0.1640195793751628. No clause enumerates `pfc`.
