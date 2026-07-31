# Brainstormer Report — Stream `r2s1_direct`, Batch 2

**Stream**: `r2s1_direct` (class: gap)
**Batch**: 2
**Total iterations**: 1
**Slot filled**: 1 / 1 (no skip)
**Reopen candidates resolved**: 0 (none exist — see below)

## Slot

- **Category**: `gap / identification-vs-capacity localization — pre-registered
  training-free selection of a closed-form condition→HF head, Wiener-calibrated
  capacity ladder`

- **Card type**: `model`

- **Motivation**: The batch-2 prior-art verdict names this shape as the one
  that is open and the strongest available. E3 row, verbatim: **`preempted-but-
  MF-composition-open (cite)`** — "McGreivy & Hakim's 'weak baseline' = an
  inadequate **classical numerical solver**, and it prescribes **no baseline
  protocol**. A standing requirement to beat a ~10^2-parameter closed-form arm
  on a **copy-LF-skill** panel, plus per-dataset localization of where capacity
  is worth anything, is unprescribed. **Best-supported contribution shape for
  B2.**" The card is exactly that composition, and it discharges B1's binding
  part-7 `next_direction` ("Stop buying decoder capacity in this stream; spend
  B2 on IDENTIFICATION and CALIBRATION") item by item: (1) the scoreable-arm
  form is SELECTED by training-free train-split statistics — the E2 row is
  `preempted-but-MF-composition-open` with "Selecting a **field predictor's
  output parameterization** from statistics computable on the train split
  **without training any candidate**, pre-registered per dataset. Not found.";
  (2) the DC-only ridge joins the floor set and the blend base set; (3) the one
  open cell — `sharp__cahn_hilliard`'s 0.5511-skill (6.0× mce) surviving
  decoder advantage — is decided against a BAND-CALIBRATED competitor via the
  rank × centering sweep B1 named as the training-free decider; (4) no
  single-seed panel-geomean threshold appears anywhere in the falsification.
  The band-gain stage is shipped as **named machinery, not as the claim**: the
  E1 row is **`preempted (cite)`** — "B1's band-gain fit is an empirical
  non-causal Wiener filter, `H_nc = S_hy/S_yy`" — so the card declares it as a
  Wiener gain with the citation. Identifiable-rank truncation is used as an
  instrument only (verdict: presumed prior art, do not claim), and E4/per-class
  pfc appears only as an internal-validity reporting requirement, never as a
  headline (verdict: `PROVISIONAL`, search-return only).

- **Concrete config**: New from-scratch family `models_r2/r2s1_selected_form`
  (worktree `worktrees/r2s1_direct/B2`), condition-only forward signature,
  stripped view only, leakage tripwire, no LF at any stage.
  Per dataset: train split → fit 80% / model-selection 10% / calibration 10%,
  disjoint and asserted disjoint (LOO + fixed-epoch when `N_train < 20`, i.e.
  ifc_poisson); no test quantity is consulted in any fit or selection step.
  **Stage S (training-free, fit+selection folds only, written out before any
  test scoring)**: centering form by `ratio = ||mean_i y_i|| / geomean_i
  ||y_i||` with pre-registered `tau = 1.0` (`>= tau` → `fact` = unit-L2
  direction × `exp(mean log||y||)`; else `add` = plain mean-centred);
  rank `r_sel = clip(#{POD modes with 5-fold OOF R^2 > 0.1 from the condition},
  1, 32)` on a 50-mode fit-fold basis. **Head**: ridge from
  `[1, standardized condition]` to the `r_sel` POD coefficients (`(d+1)*r_sel`
  params — 60 on cahn_hilliard, 12 on pfc), alpha by exact LOO on a 13-point
  log grid. **Wiener band gains**: 6 radial Fourier bands, coordinate descent
  over a 41-point grid on [0, 2] (widened from B1's [0, 1.5] because B1's
  cahn_hilliard optimum sat ON the 1.5 edge), 2 passes, fitted on the
  *calibration* fold, applied identically to EVERY arm. **Blend**:
  `lambda*arm + (1-lambda)*base`, 21-point grid, bases {zero, train_mean,
  nn_condition, **dc_only**}, both chosen on the calibration fold.
  **Arms**: scored `test_hf` = selected form; reference splits (never starting
  with `test`) `ref_selrule_alt` (non-selected centering at `r_sel`),
  `ref_rank_{1,2,3,5,8,12,20,32}`, `ref_head_rff16` (~10^3 params),
  `ref_decoder_small` (w32/b2/modes16, ~10^5.6), `ref_decoder_big`
  (w64/b4/modes16/latent16, B1 scale ~10^7.2; both early-stopped on the
  model-selection fold), the uncalibrated twins `ref_raw_head` /
  `ref_raw_decoder_big`, and the floors `ref_dc_only`, `ref_zero`,
  `ref_train_mean`, `ref_nn_condition` (the three frozen ones seam-checked to
  `state/anchors/floors.json` at 1e-9, RAISING on mismatch).
  **Diagnostics (JSON, non-scored)**: selection statistics + chosen form; the
  full rank × centering test curve with the oracle-rank entry explicitly
  labelled ORACLE; the calibrated↔uncalibrated delta per arm; the R = 5
  fold-resample paired spread of (`test_hf` − `ref_decoder_big`) per dataset;
  per-class pfc scoring from a condition-only classifier fitted on train.
  Guards `heat_local, fluid, sharp__sod_1d` at contract tier (2 epochs).
  The decoder arms are **declared in-round baseline arms** (batch-1 verdict:
  bare conditioned decoders are `preempted`), not the contribution.

- **Recipe**:

```json
{
  "base_family": "none (new from-scratch family on the round2-substrate; condition-only forward signature; no round-1 code and no factory model code vendored; sole factory contact is a read-only import of mf_field/factory_mffp/data_adapters/loaders.py)",
  "base_commit": "9e10d414e35a96398f7b091bc84ddf936d88acc7",
  "family_dir": "models_r2/r2s1_selected_form",
  "datasets": "panel",
  "epochs": 200,
  "seeds": [0],
  "env": {
    "R2S1B2_SCORED_ARM": "selected_form_wiener_blend",
    "R2S1B2_SELECT_RULE": "centering_by_meanfield_ratio+rank_by_identifiable_modes",
    "R2S1B2_CENTER_STAT": "norm_meanfield_over_geomean_norm_y",
    "R2S1B2_CENTER_TAU": "1.0",
    "R2S1B2_CENTER_FORMS": "fact,add",
    "R2S1B2_RANK_STAT": "oof_r2_pod_coeff_ridge",
    "R2S1B2_RANK_TAU": "0.1",
    "R2S1B2_RANK_KFOLD": "5",
    "R2S1B2_RANK_MIN": "1",
    "R2S1B2_RANK_MAX": "32",
    "R2S1B2_RANK_SWEEP": "1,2,3,5,8,12,20,32",
    "R2S1B2_POD_BASIS_N": "50",
    "R2S1B2_HEAD_BASIS": "affine",
    "R2S1B2_HEAD_RIDGE_ALPHA": "exact_loo_grid_1e-6:1e2:13",
    "R2S1B2_HEAD_RFF_DIM": "16",
    "R2S1B2_WIENER_BANDS": "6",
    "R2S1B2_WIENER_GRID": "0:2.0:41",
    "R2S1B2_WIENER_PASSES": "2",
    "R2S1B2_WIENER_FIT": "calib_fold_coord_descent",
    "R2S1B2_WIENER_APPLY_TO": "all_arms",
    "R2S1B2_BLEND_BASES": "zero,train_mean,nn_condition,dc_only",
    "R2S1B2_BLEND_GRID": "0:1:21",
    "R2S1B2_BLEND_SELECT": "oof_calib_relL2",
    "R2S1B2_FOLD_MODEL_FRAC": "0.10",
    "R2S1B2_FOLD_CALIB_FRAC": "0.10",
    "R2S1B2_FOLD_DISJOINT": "1",
    "R2S1B2_FOLD_RESAMPLES": "5",
    "R2S1B2_SMALL_N_PROTOCOL": "loo",
    "R2S1B2_SMALL_N_THRESHOLD": "20",
    "R2S1B2_DECODER_ARMS": "small,big",
    "R2S1B2_DEC_SMALL": "width32,blocks2,modes16,latent8,film64",
    "R2S1B2_DEC_BIG": "width64,blocks4,modes16,latent16,film128",
    "R2S1B2_DEC_SELECT": "model_fold_best_epoch",
    "R2S1B2_DEC_LR": "1e-3",
    "R2S1B2_DEC_WD": "1e-5",
    "R2S1B2_DEC_BATCH": "16",
    "R2S1B2_DEC_CLIP": "1.0",
    "R2S1B2_DEC_SCHED": "cosine",
    "R2S1B2_DEC_LOSS": "rel_l2",
    "R2S1B2_DEC_DENOM_FLOOR": "p25_median",
    "R2S1B2_DEC_WORK_CAP": "256",
    "R2S1B2_REF_ARMS": "selrule_alt,rank_sweep,head_rff16,decoder_small,decoder_big,raw_head,raw_decoder_big,dc_only,zero,train_mean,nn_condition",
    "R2S1B2_FLOOR_ARMS": "nn_condition,train_mean,zero",
    "R2S1B2_FLOOR_SEAM_TOL": "1e-9",
    "R2S1B2_PFC_CLASS_SPLIT": "1",
    "R2S1B2_PFC_CLASS_CLF": "train_logreg_on_condition",
    "R2S1B2_LEAKAGE_TRIPWIRE": "1",
    "R2S1B2_NRMSE_IMPORT": "round2_eval_nrmse",
    "R2S1B2_DIAG_OUT": "mffp_autoresearch_outputs/round2/r2s1_direct/B2/eval",
    "_scored_arm": "selected_form_wiener_blend",
    "_scored_split": "test_hf",
    "_ref_split_prefix": "ref_ (and sel_/cap_) - extra splits MUST NOT start with 'test'",
    "_guard_tier": "contract (2 epochs) on heat_local,fluid,sharp__sod_1d",
    "_note": "keys prefixed _ are card directives, NOT passed to --env"
  }
}
```

- **Expected outcome** (seed 0, 200 epochs, skill units, all
  `provisional-single-seed`; anchor = best-floor panel geomean 23.0636):

  | dataset | best floor (arm) | B1 scored arm | expected `test_hf` | vs floor | certified mce |
  |---|---|---|---|---|---|
  | `ext__helmholtz_2d` | 3.3441 (zero) | 3.1043 | 3.05–3.20 **report-only**, zero-floor column shown | −7% | 2.9530 |
  | `sharp__phase_field_crystal_2d` | 59.8118 (mean) | 52.0314 | 46–53 (variant-C denominator caveat: 0.007381; no fidelity gap under band-limited) | −21% | 0.2130 |
  | `sharp__allen_cahn_2d` | 269.1959 (NN) | 244.4306 | 175–200 | −32% | 0.8797 |
  | `sharp__fisher_kpp_2d` | 11.9931 (mean) | 11.5839 | 11.50–11.60 | −3.6% | 0.00071 |
  | `sharp__cahn_hilliard` | 23.1803 (NN) | 12.8425 | 12.8–13.4 | −43% | 0.09125 |
  | `ifc_poisson` | 10.0549 (NN) | 9.7846 | 9.5–10.0, **anecdote-grade** (N_hf = 5) | −2.5% | 0.9377 |

  Panel geomean point estimate **~18.5** vs the anchor 23.0636 (−20%),
  **reported with no falsification weight** and explicitly NOT claimable as an
  improvement over B1's 19.6444 (the ~1.1-unit difference sits at the certified
  panel `min_claimable_effect` 1.1419 — B1 part-7 item 4).
  Mechanism predictions (the actual content): the ~10^2-parameter selected head
  matches or beats the 10^7.2-parameter calibrated decoder within each
  dataset's mce on 5 of 6 panel datasets; on `sharp__cahn_hilliard` the rank ×
  centering sweep closes B1's 0.5511-unit gap to within 0.27374 (3× mce), with
  the `add` centering (ratio 0.052) and `r_sel = 3` (with the sweep testing
  r ≤ 32) as the named repair; the calibrated↔uncalibrated delta is larger than
  the between-arm delta on ≥ 4 datasets. Every number cited above that is used
  as a threshold exceeds its dataset's certified noise floor (see the
  falsification legs).
  ADR r2-0003 is honoured: on pfc / fisher_kpp / allen_cahn no clause assumes
  skill→1; the comparison target is the conditional-mean / floor level.

- **Expected falsification** (one sentence): H-r2s1-B2 — "the condition→HF map
  on this panel is identification-limited, not capacity-limited, and a
  pre-registered training-free selection of output parameterization plus
  out-of-fold Wiener band gains lets a ~10^2-parameter closed-form head match a
  10^7-parameter trained decoder everywhere, including the one cell
  (`sharp__cahn_hilliard`) where B1's capacity advantage survived" — is
  FALSIFIED if **(L1)** the scored arm loses to the in-job Wiener-calibrated
  `ref_decoder_big` by more than that dataset's certified
  `min_claimable_effect` on ≥ 2 of {pfc 0.21303, allen_cahn 0.87970, fisher_kpp
  0.00071, cahn_hilliard 0.09125, ifc_poisson 0.93770}, **or (L2)** on
  `sharp__cahn_hilliard` the out-of-fold-selected closed-form arm still loses to
  `ref_decoder_big` by > 0.27374 skill units (3× the certified cahn_hilliard
  mce 0.09125, against B1's measured 0.5511-unit gap), **or (L3)** the scored
  arm is worse than 1.05× the best frozen floor on any scored panel dataset
  (pfc > 62.80, allen_cahn > 282.66, fisher_kpp > 12.593, cahn_hilliard >
  24.339) or worse than 1.15× on `ifc_poisson` (> 11.563), **or (L4)** the
  pre-registered selection rule is beaten on test by its own non-selected
  alternative (`ref_selrule_alt`) by more than that dataset's mce on ≥ 2 panel
  datasets; `ext__helmholtz_2d` is report-only with the zero-floor column and
  carries no falsification weight (its certified mce 2.9530 exceeds any effect
  available against a floor of 3.3441), and every number is labelled
  `provisional-single-seed`.

- **Prior-art verdict quoted** (verbatim from
  `websearches/r2s1_direct/batch_2/report.md`, "Prior-art verdict" table):
  - **E3** — "**`preempted-but-MF-composition-open (cite)`**" | citations
    "McGreivy & Hakim, weak baselines, Nature Mach. Intell. 2024 —
    https://arxiv.org/abs/2407.07218 ; PCA-RaNN closed-form ridge control arm —
    https://arxiv.org/pdf/2606.29440 ; (batch 1) REALM compares against no
    trivial baselines — https://arxiv.org/html/2512.18595" | "McGreivy &
    Hakim's 'weak baseline' = an inadequate **classical numerical solver**, and
    it prescribes **no baseline protocol**. A standing requirement to beat a
    ~10^2-parameter closed-form arm on a **copy-LF-skill** panel, plus
    per-dataset localization of where capacity is worth anything, is
    unprescribed. **Best-supported contribution shape for B2.**"
  - **E2** — "**`preempted-but-MF-composition-open (cite)`**" | citations
    "ASAMS automatic surrogate-model selection, grid+LOOCV over **trained**
    candidates — https://pmc.ncbi.nlm.nih.gov/articles/PMC7571090/ ; PCA+ridge
    coefficient regression — https://arxiv.org/pdf/2606.29440 ; (batch 1)
    POD-NN/PCA-Net — https://arxiv.org/html/2504.18513v1/" | "Selecting a
    **field predictor's output parameterization** from statistics computable on
    the train split **without training any candidate**, pre-registered per
    dataset. Not found. Caveat: rank-truncation-by-predictability is **presumed
    prior art** (unresolved, see below)."
  - **E1** — "**`preempted (cite)`** at the mechanism level" | citations
    "Wiener gain `H_nc=S_hy/S_yy` + Self-Wiener low-SNR hard-thresholding —
    https://www.emergentmind.com/topics/non-causal-wiener-filter ; frozen-model
    post-hoc affine/amplitude correction fitted on held-out data,
    `a*=Cov(Y,Z)/Var(Z)` — https://arxiv.org/html/2505.15354 ; in-architecture
    band gating — https://arxiv.org/pdf/2606.21189" | "... Use as machinery,
    never as the claimed method."
  - **E4** — "**`preempted (cite — SEARCH-RETURN ONLY, NOT FETCHED;
    PROVISIONAL)`**" | "**Do not headline E4 without a batch-3 confirming
    fetch**".
  - Unresolved thread, verbatim: "**Treat identifiable-rank truncation as
    presumed prior art and do not claim it.**"
  - Suggested card `prior_art.verdict`: **`preempted-pivoted`** (architecture
    and band-gain machinery preempted and declared as baselines/named
    machinery; the scored composition is E3 × E2).

- **Immutables self-check**: **pass (11/11)** — all eight §5 immutables plus
  the three round-2 extras carry positive evidence in
  [iteration_1.md](iteration_1.md) ("Immutables self-check" section). Nothing
  was flagged; no revision pass was needed. Headlines: `datasets: "panel"` and
  the frozen guard triple (2); scoring only through the unmodified
  `round2/eval/score_panel.py` and an import of `round2/eval/nrmse.py` rather
  than a re-implementation (3, 4); `seeds: [0]` per `project.yaml` and §4.2 and
  `epochs: 200` smoke / 2 contract (6); atomic meta-guarded `<ckpt_dir>/last.pt`
  resume for both decoder arms and deterministic re-derivation of the
  closed-form arms (8); every falsification margin quoted against
  `state/noise_floor.json` with helmholtz declared report-only because its mce
  2.9530 exceeds any available effect (9); nearest pre-falsified lever is LF
  low-mode freezing and the card uses no LF at all and freezes nothing (10);
  floor arms seam-checked at 1e-9 and leg L3 stated entirely in
  best-frozen-floor units with `ref_dc_only` added (11).

- **Anchor reference**: `null` (program.md §4.5 — `null` for all four round-2
  streams; the own-stream anchor 23.063616857615774 is implicit).

- **Source iteration**: [iteration_1.md](iteration_1.md)

## Reopen candidates

| Candidate | Verdict (retry/drop) | Eased conditions | Source iteration |
|---|---|---|---|
| (none — `experiment_cards/r2s1_direct/batch_1/B1.json` carries `reopen_candidate: false`, and `brainstormer/r2s1_direct/batch_1/report.md` line 211 records no candidate; no cross-stream card is flagged) | n/a | n/a | [iteration_1.md](iteration_1.md) |

## Skipped slot

Not applicable — the slot is filled.

## Summary table

| Slot | Category | One-liner | Status |
|---|---|---|---|
| B2 | gap / identification-vs-capacity localization | Training-free pre-registered selection of a ~10^2-parameter closed-form condition→HF head, with a four-point capacity ladder under one out-of-fold Wiener band calibration, deciding whether `sharp__cahn_hilliard`'s surviving decoder advantage is rank starvation, a centering artifact, or real | filled |
