# Iteration 1 — stream `r3s1_factorised`, batch 1

## Design context considered

- `summary_so_far.md` §6 (the seven unknowns), especially U1 (M15: mechanism or accident), U3 (ch data byte-identical between rounds -> a same-data prediction exists), U4 (the noise floor is provisional and has no `ifc_heat` entry), U5 (the shipped law loses to a 6-dof affine fit on both ifc cells), U6 (`ref_dc_only` never reported per-cell on the honest panel).
- The prior-art verdict from `round3/websearches/r3s1_factorised/batch_1/report.md`: D1 `preempted-but-MF-composition-open (cite)`, D2 `preempted-but-MF-composition-open (cite)`, D3 `preempted (cite)`.
- The stream question, `round3/project.yaml` `streams[0].question`: "does the recorded two-stage cross-coefficient factorised closed-form head beat the shipped condition->level law on the honest (completeness-certified) panel?"
- The §4.2 stream directive for `r3s1_factorised`: one condition->HF experiment built from scratch, no LF field as forward input at test (stripped view), floor arms mandatory. The two-stage closed-form head satisfies all three: it is a condition-only forward signature, it never opens an LF array, and floor arms are mandatory on it as a model card.
- The immutables block (§4.5) verbatim, held in view throughout; self-check in the final section.
- **Anchors, re-read at design time** per the orchestrator note, from `round3/state/anchors/launch_anchors.json` (mtime confirmed 2026-08-07, all four cards `CERTIFIED`, `pending_ifc_rescore: []`):
  - best-floor panel geomean **36.3912**; per-dataset best floors pfc 48.0773 (train_mean), allen_cahn 475.8568 (nn_condition), fisher_kpp 390.7015 (train_mean), cahn_hilliard 23.1803 (nn_condition), ifc_poisson 8.0409 (nn_condition), ifc_heat 1.3941 (nn_condition).
  - the shipped closed-form law `r2s1_direct-B3`: seed geomeans [28.3253, 28.1823, 28.1447], mean **28.2174**, ci95 [28.1096, 28.3253]; cells pfc 46.7083 / allen_cahn 279.1165 / fisher_kpp 374.8381 / cahn_hilliard 12.5650 / ifc_poisson 8.2507 / ifc_heat 0.9964.
  - `ifc_floors_repaired.affine_on_hf_train`: ifc_poisson nRMSE 0.057375492822121524, skill **1.5937636895033758**, oracle-affine residual 5.395916929396343e-16; ifc_heat nRMSE 0.07091833937569547, skill **0.9583559375093983**.
- **Noise floor**, `round3/state/anchors_repaired/noise_floor.json` (`_provisional: true`, `_source: round1-batch0-rescaled`, LF-consuming families): `min_claimable_effect` pfc **8.859540060286326**, allen_cahn **16.422284630500034**, fisher_kpp **158.33215324637433**, cahn_hilliard **1.1603569120520159**, ifc_poisson **0.23990756041925798**; **`ifc_heat` is absent from the file**. There is no panel-level entry.
- Pre-falsified levers, round-2 §5 verbatim: "Pre-falsified levers (r1 §5) still apply where relevant (WNO backbone swap, LF low-mode freezing, diffusion prior for point accuracy)". Plus the within-lineage negative, r2s1-B3 part 7: "Do NOT spend a batch on widening the head's basis: turn 3 F20 shows every deployable relaxation of the SET gate, down to fitting all 51 directions, makes the panel geomean worse."

## Proposal reasoning

### What round 3 changed that makes this batch cheap and decisive

The stream question names a specific recorded object. Round 2 measured it as an offline probe on saved artifacts and never shipped it as a scored arm; the number (18.6787) is void because the panel changed. But the *reason* it was inconclusive was `n = 1`: cahn_hilliard was the only cell with a high-dimensional condition vector, so "high cond_dim causes cross-coefficient structure" (M15) and "cahn_hilliard happens to have it" were indistinguishable.

Option-A regeneration changed the independent variable for free. Diffing the two floor files:

| cell | cond_dim r2 -> r3 | copy-LF reference r2 -> r3 |
|---|---|---|
| `sharp__phase_field_crystal_2d` | 2 -> **18** | 0.00738077856100695 -> 0.018257409062703473 |
| `sharp__allen_cahn_2d` | 3 -> **19** | 0.0017807662982691156 -> 0.0020593576160366327 |
| `sharp__fisher_kpp_2d` | 2 -> **50** | 0.02144950364640668 -> 0.00016524586579046429 |
| `sharp__cahn_hilliard` | 19 -> **19** | 0.041802962686225575 -> **identical** |
| `ifc_poisson` | 5 -> 5 | repaired ladder, paper bar 0.036 |
| `ifc_heat` | (not in panel) -> 3 | paper bar 0.074 |

So the discriminator goes from n = 1 high / n = 1 low to **n = 4 high (18/19/19/50) vs n = 2 low (3/5)**, and cahn_hilliard — the cell that generated the hypothesis — is on **byte-identical data**, which gives a same-data point prediction to check the instrument against. That is an unusually good experimental setup and it costs almost nothing, because every arm in this card is closed-form.

### Alternatives weighed and rejected

1. **Propose D2 alone as a pure diagnostic card.** The websearcher calls D2 "the strongest novelty position available to this batch". Rejected as the *whole* card: the stream is class `gap` and its question is explicitly "does the head beat the shipped law", which requires a scored arm. Also, the discriminator's value is exactly its ability to *predict the payoff*, so measuring the payoff in the same job is what makes the diagnostic testable rather than descriptive. Resolution: card_type `model`, with the discriminator carried as a pre-registered, falsification-bearing diagnostic column (clause L3). This keeps the strongest novelty position and answers the stream question in one job.
2. **Widen the head's basis / relax the SET gate.** Explicitly pre-falsified within the lineage (F20: every deployable relaxation, down to fitting all 51 directions, makes the panel geomean worse). Rejected; the card holds tau = 0.1, min 1, max 32 fixed at the shipped values.
3. **Re-run the FiLM decoder arm as the capacity control.** Rejected: expensive (15.85 M params x 6 cells x 3 seeds), and r2s1-B3's M5 established that the head-vs-decoder headline was a *coordinate* verdict, not a capacity verdict (94.4 % of the decoder's deficit closed by a test-label-free coordinate replacement inside the head's own subspace). Architecture capacity is `r3s2_field_reach`'s question, not this stream's. Dropping it turns this into a zero-GPU-training card that can afford 3 seeds up front.
4. **Re-instate the Wiener / blend / Bates-Granger post-hoc stages.** Rejected outright: the scored column stays stage-free, and the card contains no calibration-consuming stage at all. This also removes the entire failure surface that falsified r2s1-B3.
5. **Make the ifc affine-floor repair the card's contribution.** Rejected per the D3 verdict: "Ship as a bug fix / instrument, never as a contribution." It enters as a mandatory reported arm only.
6. **Skip the slot.** Rejected: the stream question is concrete, the object exists, the panel change makes it answerable for the first time, and the cost is trivial.

### Why the falsification is priced the way it is

r2s1-B3's own postmortem is the binding constraint: it was FALSIFIED by a clause that "was UNPASSABLE BY CONSTRUCTION", whose "tolerance ... was 0.026-0.107 sigma of the 40-sample estimator it audited". M14 generalises it: "a statistic estimated on one fold and then consumed under a different input distribution". So every threshold here is priced against an instrument that actually measures the quantity being thresholded:

- **Panel level (L1).** `noise_floor.json` has **no panel entry**. The only measured panel-level noise instrument on the honest 6-dataset panel for a *closed-form condition-only* family is the certified 3-seed geomean spread of the anchor cards themselves: **0.1806** (`r2s1_direct-B3` [28.3253, 28.1823, 28.1447]) and **0.0746** (`r2s1_direct-B2`). Threshold **0.3612 = 2 x 0.1806** (and 4.84 x r2s1-B2's spread). Predicted effect: **0.4479** in the pessimistic ch-only case (28.2174 -> 27.7695, computed by propagating the pre-measured ch ratio 11.4148/12.5650 = 0.90846 through the 6-cell geomean), **1.15-1.58** if two or three more high-cond_dim cells move 5-8 %. So L1 is passable on the pre-measured effect alone with a 1.24x margin, and comfortably passable if M15 holds. It is a genuine two-sided test of the stream's question.
- **cahn_hilliard (L2).** Priced at **1.1603569120520159** skill units, i.e. exactly the provisional `min_claimable_effect` for that cell, so the clause strictly exceeds the noise floor as required. Honest disclosure recorded here and in the card: the predicted paired effect is **1.15-1.25** (certified one-stage cell 12.5650 x (1 - 0.90846) = 1.1502; seed-0 round-2 measurement 12.6601 -> 11.4148 = 1.2453), so **L2 is close to a coin flip**. That is deliberate and it is *not* the r2s1-B3 defect: B3's clause sat 20-40x outside its estimator's resolution and could not fire informatively either way, whereas a threshold placed at the centre of a pre-registered prediction interval is maximally informative. L1, not L2, carries the primary weight; L2 is the same-data reproduction check.
- **Discriminator (L3).** A dimensionless OOF R^2 margin, so per-dataset *skill* floors do not apply. Bar **0.30**, versus the largest round-2 measured no-op margin **0.0430** (fisher_kpp; controls allen_cahn +0.0054, pfc +0.0323, ifc_poisson -0.0751) -> **7.0x**. Anti-unpassability guard: the clause is judged at the 3-seed mean and the 3-seed spread of the statistic is reported per cell; if any cited cell's spread exceeds 0.10 the clause is recorded **unresolved**, not fired.
- **Floors (L4).** Frozen deterministic constants in `floors.json`, not noisy estimates, so the floor value *is* the threshold. Applied at 1.00x on the four sharp cells only. The two ifc cells carry **no** falsification weight (§12.1: "N_hf on ifc_poisson is 5 — every claim there is anecdote-grade"; and `noise_floor.json` has no `ifc_heat` entry at all) but MUST be reported against both the frozen floors and `affine_on_hf_train`, with the standing statement that the shipped law already **loses** to the fitted affine floor there (8.2507 vs 1.5938; 0.9964 vs 0.9584).

### Why a no-op cannot make things worse

Build gate G-E asserts that when the stage-2 gate selects zero directions the scored column equals `ref_head_onestage` to 1e-12. So on cells with no cross-coefficient structure (round 2: allen_cahn, pfc, fisher_kpp, ifc_poisson under the old conditions) the arm is a bitwise no-op, and the panel delta is bounded below by 0. The propagation-aware gate is what makes this true — F25 showed the true-input gate instead *damages* cells (helmholtz 3.8150 -> 6.1666). Naming that as a rediscovery of SST/ERC's published train/predict discrepancy is mandatory per the websearcher.

## Proposal

- **Category**: `gap / factorised-head composition — propagation-aware two-stage cross-coefficient closed-form head shipped as the scored condition->HF arm, with the condition-dimension discriminator (M15) as a pre-registered mechanism test at n = 4 high vs n = 2 low`
- **Card type**: `model`
- **Motivation** (quotes the prior-art verdict verbatim):
  The websearcher's D1 row reads **`preempted-but-MF-composition-open (cite)`**, and the open residue is: *"Only the **composition**: OOF-corrected target-as-input stacking on **reduced-basis coefficients of a parametric PDE field**, where stage-1 targets are themselves regressed from the condition vector, scored on a copy-LF-skill panel in the **no-LF-at-test** regime at N_hf down to 5. Three refutation searches returned nothing; the field's stated default ("model modal coefficients independently") is a *linear*-decorrelation argument that B3-F24's OOF R^2 0.92-0.94 contradicts. **The card must name SST/ERC and state that F25 rediscovered the published train/predict discrepancy.**"* The D2 row is also **`preempted-but-MF-composition-open (cite)`** with the residue *"the **independent variable and estimator** — both published criteria key on task affinity / heterotopic design geometry, neither on **condition dimension vs fit-row count** [...] **Strongest novelty position available to this batch — and it is a diagnostic claim, not an architecture claim.**"* The card therefore claims the composition and the discriminator, names Spyromitros-Xioufis et al. (arXiv:1211.6581, SST/ERC) as owning the cascade and the OOF gate, and records F25 as a rediscovery, not a finding.
- **Concrete config**: new from-scratch round-3 family `models_r3/r3s1_twostage_crosscoef`, condition-only forward signature, stripped view only, leakage tripwire, no LF at any stage, no gradient-trained arm.
  - **Scored column `test_hf`** = two-stage propagation-aware cross-coefficient head. Stage 1 is the shipped head unchanged: centering form by `ratio = ||mean_i y_i|| / geomean_i ||y_i||`, tau = 1.0 over {fact, add}; direction bank = {DC/spatial-mean} u {POD modes 0-49 of the DC-removed fit-fold residual in the selected centering form}; per direction a 5-fold OOF R^2 from the condition over the map bank {affine, quadratic, RBF kernel ridge, k-NN}, best family selected out of fold; fitted SET = directions clearing tau = 0.1 (min 1, max 32). **Stage 2 (new)**: the remaining directions are regressed on the **out-of-fold stage-1 predicted** SET coefficients over the same map bank, and the stage-2 gate is both **selected and fitted** on those OOF predictions (tau2 = 0.1). Empty gate => bitwise no-op.
  - **Reference arms** (never prefixed `test`): `ref_head_onestage` (the shipped law, matched folds/bases/seed — the paired control and the reproduction seam); `ref_twostage_true_gate` (stage 2 selected/fitted on TRUE stage-1 coefficients — the F25 negative control, reported as a named rediscovery); `ref_dc_only` (the condition->level closed-form law, required by round-3 success criterion 1); floors `ref_zero`, `ref_train_mean`, `ref_nn_condition` (seam-checked to `state/anchors_repaired/floors.json` at 1e-9, RAISING on mismatch); `ref_affine_on_hf_train` (seam-checked on the two ifc cells to `launch_anchors.json:ifc_floors_repaired` at 1e-9, reported without a seam check on the four sharp cells).
  - **Diagnostic columns** (L3-bearing): per direction and per cell, OOF R^2 (A) from the condition and (B) from the SET coefficients, plus the margin B - A, the selected stage-2 gate size, and the per-cell 3-seed spread of every scored quantity (a by-product this card hands to `r3s4_audit` for mce re-certification). Instrument: `round2/tools/coefficient_factorisation_audit.py`, adapted to round-3 eval paths on use and promoted via the register turn.
  - **Folds**: identical to the shipped head so the control is procedure-matched — disjoint 80 % fit / 10 % model-selection / 10 % calibration, asserted disjoint, 5 resamples; the calibration fold is **asserted unused** (there is no post-hoc stage in this card) rather than merged, so the fit fold stays at exactly 320 rows and the reproduction seam is meaningful. LOO when `N_train < 20` (ifc cells).
  - **Build gates**: **G-A** reproduction seam — `ref_head_onestage` per-cell 3-seed mean must match `launch_anchors.json` `cards["r2s1_direct-B3"].per_dataset_mean_skill` within 3 % relative per cell and the panel geomean within 28.2174 +/- 0.3612, RAISING (INFRA-class) otherwise; **G-B** floor seam checks at 1e-9; **G-C** stripped-view leakage tripwire (no path under `data_root`, no `train_l1`/`train_l2`/`lf` array opened at test) with the guard set run at the same tier; **G-D** target-scaler pre-flight via `tools/target_scale_spread_audit.py` on `sharp__phase_field_crystal_2d` and `sharp__cahn_hilliard` (the two cells the 2026-08-07 preflight flags with priced `cell_stability` warnings), verdict recorded before any test tensor is touched, `OUTLIER_DOMINATED`/`NEAR_ZERO_TARGETS` => per-sample target normalisation or a card-recorded justification; **G-E** stage-2 no-op assertion (empty gate => `test_hf` == `ref_head_onestage` to 1e-12).
- **Recipe**:

```json
{
  "base_family": "none (new from-scratch round-3 family on round3-substrate; condition-only forward signature; the ONE-STAGE control arm is vendored verbatim with provenance comments from branch round2/exp-r2s1_direct-B3 @ 2b030f02da70cde80c90de2463935461bd56debb, files models_r2/r2s1_stagefree_permode/{basis,common,config,floors,head,maps,registration}.py; decoder.py, stages.py and prelude.py are NOT vendored; no round-1 code; no LF array opened at any stage; sole factory contact is a read-only import of mf_field/factory_mffp/data_adapters/loaders.py)",
  "base_commit": "8aae33a7fab11ef8234f4bb7158c2bc1a8b4bf51",
  "family_dir": "models_r3/r3s1_twostage_crosscoef",
  "datasets": "panel",
  "epochs": 0,
  "seeds": [0, 1, 2],
  "env": {
    "R3S1B1_SCORED_ARM": "twostage_crosscoef_oof_gate",
    "R3S1B1_STAGE_POLICY": "scored_arm_is_stage_free_no_wiener_no_blend_no_bg",
    "R3S1B1_TRAINED_ARMS": "none",
    "R3S1B1_EPOCHS_RATIONALE": "every arm is closed-form least-squares/kernel; family asserts epochs==0 and instantiates no gradient-trained arm",
    "R3S1B1_DATA_VIEW": "stripped",
    "R3S1B1_LF_AT_ANY_STAGE": "0",
    "R3S1B1_LEAKAGE_TRIPWIRE": "1",
    "R3S1B1_PANEL": "sharp__phase_field_crystal_2d,sharp__allen_cahn_2d,sharp__fisher_kpp_2d,sharp__cahn_hilliard,ifc_poisson,ifc_heat",
    "R3S1B1_GUARDS": "heat_local,fluid,sharp__sod_1d",
    "R3S1B1_DIRECTION_BANK": "dc_meanfield,pod_0_49",
    "R3S1B1_POD_BASIS_N": "50",
    "R3S1B1_POD_DC_ORTHOGONALIZE": "1",
    "R3S1B1_CENTER_STAT": "norm_meanfield_over_geomean_norm_y",
    "R3S1B1_CENTER_TAU": "1.0",
    "R3S1B1_CENTER_FORMS": "fact,add",
    "R3S1B1_BASIS_FORM_MATCHED": "1",
    "R3S1B1_SELECT_INDEXING": "set",
    "R3S1B1_SELECT_STAT": "oof_r2_per_direction_best_family",
    "R3S1B1_SELECT_TAU": "0.1",
    "R3S1B1_SELECT_KFOLD": "5",
    "R3S1B1_SELECT_MIN": "1",
    "R3S1B1_SELECT_MAX": "32",
    "R3S1B1_MAP_BANK": "affine,quadratic,rbf_kernel_ridge,knn",
    "R3S1B1_MAP_SELECT": "oof_r2_per_direction",
    "R3S1B1_MAP_RIDGE_ALPHA": "exact_loo_grid_1e-6:1e2:13",
    "R3S1B1_MAP_KNN_K": "1,2,4,8",
    "R3S1B1_MAP_RBF_GAMMA": "median_heuristic",
    "R3S1B1_STAGE2_ENABLE": "1",
    "R3S1B1_STAGE2_INPUT": "oof_stage1_predictions",
    "R3S1B1_STAGE2_GATE_SELECT_ON": "oof_stage1_predictions",
    "R3S1B1_STAGE2_GATE_FIT_ON": "oof_stage1_predictions",
    "R3S1B1_STAGE2_TAU2": "0.1",
    "R3S1B1_STAGE2_MAP_BANK": "affine,quadratic,rbf_kernel_ridge,knn",
    "R3S1B1_STAGE2_KFOLD": "5",
    "R3S1B1_STAGE2_MIN_DIRECTIONS": "0",
    "R3S1B1_STAGE2_MAX_DIRECTIONS": "50",
    "R3S1B1_STAGE2_NOOP_ASSERT": "1e-12",
    "R3S1B1_REF_ARMS": "head_onestage,twostage_true_gate,dc_only,zero,train_mean,nn_condition,affine_on_hf_train",
    "R3S1B1_DECODER_ARMS": "none",
    "R3S1B1_FLOOR_SEAM_CHECK": "mffp_autoresearch/round3/state/anchors_repaired/floors.json@1e-9",
    "R3S1B1_AFFINE_FLOOR_SEAM_CHECK": "mffp_autoresearch/round3/state/anchors/launch_anchors.json:ifc_floors_repaired@1e-9",
    "R3S1B1_AFFINE_FLOOR_ALL_CELLS": "1",
    "R3S1B1_ANCHOR_REPRO_SEAM": "launch_anchors.json:cards.r2s1_direct-B3.per_dataset_mean_skill@3pct",
    "R3S1B1_FOLD_MODEL_FRAC": "0.10",
    "R3S1B1_FOLD_CALIB_FRAC": "0.10",
    "R3S1B1_CALIB_FOLD_USE": "none_asserted_unused",
    "R3S1B1_FOLD_DISJOINT": "1",
    "R3S1B1_FOLD_RESAMPLES": "5",
    "R3S1B1_SMALL_N_PROTOCOL": "loo",
    "R3S1B1_SMALL_N_THRESHOLD": "20",
    "R3S1B1_CONDDIM_DISCRIMINATOR": "1",
    "R3S1B1_DISCRIM_STAT": "per_direction_oof_r2_from_condition_vs_from_set_coefficients",
    "R3S1B1_DISCRIM_TOOL": "mffp_autoresearch/round2/tools/coefficient_factorisation_audit.py@adapted",
    "R3S1B1_DISCRIM_REPORT_CELLS": "panel6",
    "R3S1B1_TARGET_SCALE_PREFLIGHT": "sharp__phase_field_crystal_2d,sharp__cahn_hilliard",
    "R3S1B1_PER_CELL_SEED_SPREAD_REPORT": "1",
    "R3S1B1_CKPT_RESUME": "1",
    "R3S1B1_CKPT_PATH": "<ckpt_dir>/last.pt"
  }
}
```

- **Expected outcome** (3 seeds {0,1,2}; skill units; anchor = best-floor panel geomean **36.3912**; comparand = the shipped closed-form law **28.2174**):

| cell | cond_dim | best frozen floor | shipped law (certified) | expected `test_hf` | provisional mce |
|---|---|---|---|---|---|
| `sharp__phase_field_crystal_2d` | 18 | 48.0773 (train_mean) | 46.7083 | 42.0-46.8 | 8.8595 |
| `sharp__allen_cahn_2d` | 19 | 475.8568 (nn) | 279.1165 | 250-279 | 16.4223 |
| `sharp__fisher_kpp_2d` | 50 | 390.7015 (train_mean) | 374.8381 | 330-375 | 158.3322 |
| `sharp__cahn_hilliard` | 19 | 23.1803 (nn) | 12.5650 | 11.30-11.45 | 1.1604 |
| `ifc_poisson` | 5 | 8.0409 (nn) / affine 1.5938 | 8.2507 | 8.20-8.40 (no-op expected) | 0.2399 |
| `ifc_heat` | 3 | 1.3941 (nn) / affine 0.9584 | 0.9964 | 0.99-1.01 (no-op expected) | **absent** |
| **panel geomean** | — | **36.3912** | **28.2174** [28.1096, 28.3253] | **25.5-27.8, point ~26.8** | panel spread 0.1806 |

  Which metric moves and by how much: the scored per-cell skill of `test_hf` in the raw frame and the 6-cell panel geomean. Versus the anchor 36.3912 the point estimate is **-26 %**; versus the shipped law 28.2174 it is **-5 %** (paired delta ~1.4), with a pessimistic floor of **-1.6 %** (delta 0.4479) if only cahn_hilliard moves. Versus the noise floor: the panel delta's threshold 0.3612 is **2.00x** the measured panel instrument 0.1806 and **4.84x** r2s1-B2's 0.0746; the predicted panel delta is **1.24x-4.38x** that threshold. Mechanism prediction (L3): max per-direction margin [OOF R^2 from SET coefficients - OOF R^2 from the condition] **>= 0.30 on >= 3 of the 4 high-cond_dim cells** and **< 0.30 on both** low-cond_dim cells, against round-2's measured no-op margins of +0.0054 / +0.0323 / +0.0430 / -0.0751 (i.e. the bar is 7.0x the largest of them). Mandatory floor-arm reading: `test_hf` is expected to beat `ref_nn_condition`, `ref_train_mean` and `ref_zero` on all four sharp cells and to **lose to `ref_affine_on_hf_train` on both ifc cells** (8.2507 and 0.9964 vs 1.5938 and 0.9584) — the card makes **no ifc claim** and states the affine-floor rule verdict explicitly. Criterion-1 reading: `test_hf` vs `ref_dc_only` reported per cell, adjudicated against `r3s4_audit`'s certified mce, not against the provisional file.
- **Expected falsification** (one sentence):
  H-r3s1-B1 — "the cahn_hilliard cross-coefficient effect is a **condition-dimension mechanism**, not a dataset accident, and shipping it with a propagation-aware gate beats the shipped condition->level closed-form law on the honest panel" — is FALSIFIED if **(L1)** the seed-mean panel geomean of `test_hf` fails to beat the matched `ref_head_onestage` by more than **0.3612** skill units (2 x the certified 3-seed panel spread 0.1806 of `r2s1_direct-B3` in `state/anchors/launch_anchors.json` — the only panel-level noise instrument measured on this panel for a closed-form condition-only family; `noise_floor.json` has no panel entry), or the sign of that paired delta is not identical at all three seeds, **or (L2)** on `sharp__cahn_hilliard` — byte-identical data to round 2 (same copy-LF reference 0.041802962686225575, same `nn_condition` nRMSE 0.9690069811741324) where the effect was pre-measured at 12.6601 -> 11.4148 — `test_hf` fails to beat `ref_head_onestage` by more than **1.1603569120520159** skill units (that cell's provisional `min_claimable_effect`), **or (L3)** fewer than 3 of the 4 high-cond_dim cells {pfc 18, allen_cahn 19, cahn_hilliard 19, fisher_kpp 50} reach a maximum per-direction margin [OOF R^2 from the SET coefficients - OOF R^2 from the condition] **>= 0.30** at the 3-seed mean, or either low-cond_dim cell {ifc_heat 3, ifc_poisson 5} reaches it (clause recorded **unresolved**, not fired, on any cell whose 3-seed spread of that margin exceeds 0.10), **or (L4)** `test_hf` is worse than the best frozen floor on any of the four sharp cells (pfc > 48.0773, allen_cahn > 475.8568, fisher_kpp > 390.7015, cahn_hilliard > 23.1803); the two ifc cells carry no falsification weight (N_hf = 5, anecdote-grade per §12.1; `noise_floor.json` has no `ifc_heat` entry) but are reported against both the frozen floors and `affine_on_hf_train`; every number is `provisional` until the in-round 3-seed confirm and `r3s4_audit`'s mce re-certification land.
- **Anchor reference**: `null` (per §4.2/program.md §4.5: `null` for all four round-3 streams; the own-stream anchor — best-floor geomean 36.3912, with the shipped law 28.2174 as the named comparand — is implicit).

## Status

- Slot **covered** (one proposal, `model` card).
- Skipped: no.
- **Reopen candidates resolved**: none exist. `round3/experiment_cards/` contains no cards (batch 1 is the stream's first); all three round-2 `r2s1_direct` cards were read and each carries `reopen_candidate: false`; round-2 state is immutable under round-2 §5.13 and is therefore not a round-3 reopen source. Nothing to retry or drop.
- **Immutables self-check**: PASS (10/10 + item 11), evidence below.

### Immutables self-check (positive evidence for each)

1. **Data read-only.** The card reads `stripped_data_root` only, through `factory_mffp/data_adapters/loaders.py` imported read-only; it writes nothing under any dataset directory, adds no HF rows (N_hf stays 400 on the sharp cells and 5 on both ifc cells, exactly the counts in `floors.json`), and never constructs LF by downsampling HF — it never opens an LF array at all (`R3S1B1_LF_AT_ANY_STAGE: "0"`, tripwire `R3S1B1_LEAKAGE_TRIPWIRE: "1"`).
2. **Panel + guard set fixed.** `R3S1B1_PANEL` lists exactly the six names in `project.yaml:panel` and `R3S1B1_GUARDS` exactly the three in `project.yaml:guard_set`; helmholtz is absent from both (report-only, ADR D2) and the card scores no helmholtz cell.
3. **Eval layer / spec untouched.** Every arm is produced inside `models_r3/r3s1_twostage_crosscoef/smoke_eval.py` in the experiment worktree and scored by the frozen `round2/eval/score_panel.py` as-is; the card requires no edit to `round2/eval/`, `project.yaml`, `program.md` or any agent prompt — the only round-root files it *reads* are `state/anchors/launch_anchors.json` and `state/anchors_repaired/floors.json`, both for seam checks.
4. **One nRMSE definition.** The scored metric comes from `round2/eval/nrmse.py` via `score_panel.py` (`_nrmse_def_hash: d3d0ade9...` recorded in `floors.json`); the card defines no loss of its own — the closed-form arms are least-squares/kernel fits whose objective is internal to the fit and never substituted for the scored metric.
5. **Contract CLI fixed.** `smoke_eval.py` keeps the `--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed` signature from `eval/MODEL_CONTRACT.md`; every knob above is an environment variable in the recipe `env` block, none is a new flag.
6. **Seeds and tier epochs fixed.** Seeds are exactly {0, 1, 2} from `project.yaml:seed_protocol` (seed 0 scored, 1-2 the in-round confirm folded into the same chain per PROGRAM_NOTE MUST 4, affordable because no arm trains); `epochs: 0` is not a tier deviation but the honest value for a card with `R3S1B1_TRAINED_ARMS: "none"` — the smoke/contract tiers (200/2) govern gradient-trained arms and this card instantiates none.
7. **Guarded factory surfaces untouched.** The family's only factory contact is `import` of `mf_field/factory_mffp/data_adapters/loaders.py`; nothing under `factory_mffp/{data,baselines,eval,references,scripts}`, `factory.md`, `akash/`, `mf_field_eloise_data/` or `benchmark_42/` generation code is written or edited (the same read-only-import pattern the reviewer passed on r2s1-B3).
8. **Checkpoint-resume implementable.** `R3S1B1_CKPT_RESUME: "1"` with `<ckpt_dir>/last.pt` holding the per-dataset completion ledger plus the fitted closed-form state (centering form, POD basis, SET indices, selected map families and coefficients, stage-2 gate and coefficients); a preempted job reloads it and skips completed cells — the same mechanism r2s1-B3 shipped on `mit_preemptable`.
9. **Falsification thresholds exceed the noise floor, numbers quoted.** L1: threshold **0.3612** vs the applicable panel instrument **0.1806** (`launch_anchors.json` `r2s1_direct-B3` seed geomeans 28.3253/28.1823/28.1447) = **2.00x**, and vs r2s1-B2's 0.0746 = 4.84x; `noise_floor.json` carries no panel entry, so no per-dataset value applies to L1. L2: threshold **1.1603569120520159** = exactly `noise_floor.json["sharp__cahn_hilliard"].min_claimable_effect`, and the clause requires the effect to *exceed* it (predicted 1.15-1.25 — disclosed as near a coin flip, which is a maximally informative pre-registration and is not the r2s1-B3 unpassable-by-construction defect, whose tolerance sat 20-40x outside its estimator's resolution). L3: dimensionless OOF R^2 margin, bar **0.30** vs the largest measured no-op margin **0.0430** = **7.0x**, with an explicit unresolved-verdict guard at spread > 0.10. L4: frozen deterministic floor constants (48.0773 / 475.8568 / 390.7015 / 23.1803), which are the thresholds themselves. Cells cited by no clause: `ifc_poisson` (mce 0.2399) and `ifc_heat` (**no entry in `noise_floor.json`**) — deliberately excluded from falsification weight and reported only.
10. **Not a pre-falsified lever.** The round-2 §5 list is "WNO backbone swap, LF low-mode freezing, diffusion prior for point accuracy" — none is in this card (no backbone, no LF, no diffusion). The nearest *within-lineage* negative is r2s1-B3 part 7's "Do NOT spend a batch on widening the head's basis: turn 3 F20 shows every deployable relaxation of the SET gate, down to fitting all 51 directions, makes the panel geomean worse": this card does **not** widen the gate — tau = 0.1, min 1, max 32 and the 50-mode bank are held at the shipped values, and stage 2 adds directions only through a *separate* gate fitted on predicted stage-1 inputs, a different mechanism which F24/F25 pre-measured as an improvement (11.4148 on ch) rather than a relaxation. The second nearest is r2s1-B3's own falsified L2 (the Bates-Granger prelude clause): the card contains **no** Wiener, blend or Bates-Granger stage at all, so that mechanism is not re-proposed in any form.
11. **Mandatory floor arms present in the falsification reasoning.** `ref_nn_condition`, `ref_train_mean` and `ref_zero` are seam-checked to `state/anchors_repaired/floors.json` at 1e-9 and enter clause **L4** directly (pfc 48.0773, allen_cahn 475.8568, fisher_kpp 390.7015, cahn_hilliard 23.1803 — the best-floor arm per cell from `launch_anchors.json:best_floor.per_dataset`); `ref_affine_on_hf_train` is seam-checked on both ifc cells (1.5937636895033758 / 0.9583559375093983) and reported on the sharp cells, per the program.md §2 affine-floor rule; `ref_dc_only` (the condition->level law) is reported per cell for round-3 success criterion 1.
