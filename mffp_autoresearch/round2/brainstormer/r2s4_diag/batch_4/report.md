# Brainstormer Report — Stream `r2s4_diag`, Batch 4

**Stream**: `r2s4_diag` (class: diag)
**Batch**: 4
**Total iterations**: 1 (cap 5, respected)
**Slot filled**: 1 / 1 (not skipped)
**Reopen candidates resolved**: 0 of 0 (none exist for this stream)
**B4-or-close decision**: **B4** — see "B4-or-close decision" below.

## Slot

- **Category**: diagnostic / ifc_poisson few-HF anatomy — exhaustive HF-subset learning
  curve + within-rung generalisation-gap ladder on the non-nested ifc ladder, with a
  pre-registered equivalence outcome.

- **Card type**: `diagnostic` (WITH training — the program.md 12.4 exception;
  `epochs: 200`, strict 1 card seed).

- **Motivation**: executes the stream's one un-executed 12.4 mandate ("overfitting anatomy
  at N_hf ∈ {5, 20, 50} (ifc ladder) … train/test gap decomposition") on the only panel
  dataset where a round success criterion is still live, and does so in exactly the slice
  the batch-4 prior-art verdict leaves open (row A, quoted verbatim below): a train-vs-test
  decomposition for a field-valued condition→HF surrogate at single-digit N, in copy-LF
  skill units against the pre-certified ifc `min_claimable_effect` 0.9377041289531141, on a
  ladder called non-nested **by citation** (https://arxiv.org/abs/2407.17087,
  https://arxiv.org/html/2408.17075v2) and never presented as a discovery. It is the
  measurement that either underwrites or honestly bounds the round's live criterion-1
  route: `r2s3_lf_train_signal-B3` moved ifc from `A0_nolf` 8.13438381993564 to
  `A1_lf_cov` **2.150091575784423** (effect 5.984292244151218, 6.4x the MCE), and
  `r2s2_stacked-B3` is in build with its own ifc leg — neither can currently say whether
  that gain is "LF information" or "more effective samples".

- **Concrete config**: new from-scratch family `models_r2/r2s4_b4_anatomy/`
  (`manifest.json`, `model.py`, `subsets.py`, `rung_cv.py`, `smoke_eval.py`,
  `INSPIRATION.md`) + probe `probes/few_hf_anatomy.py`. FiLM-FNO backbone re-implemented
  from `models_r2/r2s4_cert_min` (r2s4-B1) with provenance comments — width 32, 2 blocks,
  16 modes, FiLM-MLP 64, ~1.06M params; optimizer/schedule/normalisation byte-identical to
  B1/B2/B3 (AdamW 1e-3, wd 1e-5, batch 16, cosine, clip 1.0, MSE in `train_zscore_global`,
  200 epochs). Reads `stripped_data/ifc_poisson` only. **All legs run in ONE
  `smoke_eval.py` invocation with a single dataset load** (B2/B3 pattern).
  - **Group A — exhaustive HF-subset curve** on the scored rung `fidelity_64` (N = 5):
    all C(5,n) subsets for n ∈ {1..5} (31 total) x 3 **in-job replicate init seeds** at
    width 32 (93 legs), plus width 8 at n ∈ {1,3,5} (16 subsets x 3 = 48 legs). Per leg:
    in-sample nRMSE on its own n rows; frozen 128-row `test_hf` nRMSE and skill (paper bar
    0.036); the 5−n unused HF rows as a descriptive micro-holdout; and the three floor arms
    **recomputed on the same n rows**. Primary scored arm -> `splits.test_hf`: n = 5,
    width 32, replicate 0.
  - **Group C — within-rung generalisation-gap ladder** (rungs are independent designs):
    5-fold CV inside each of `fidelity_8` (n_fit 80, 8x8), `fidelity_16` (40, 16x16),
    `fidelity_32` (16, 32x32), `fidelity_64` (4, 64x64), width 32, 3 replicates = 60 legs.
    Reports in-sample rel-L2, held-out rel-L2 (rung-native, dimensionless), `gap`,
    `gap_ratio`, and the rung's own `train_mean` / `nn_condition` floors.
    **No cross-rung training; no cross-grid interpolation in any adjudicating column.**
  - **Group D — bridging column, REPORT-ONLY, adjudicates nothing**: group-C predictions
    lifted to 64x64 via `models/_common/lf_registration.py::resample_fields(...,
    dataset_name="ifc_poisson")` = `legacy_cell_centred` (ADR r2-0001; `eval/panel_data.py`
    line 48 puts ifc_poisson in `LEGACY_CELL_DATASETS`), scored on the 128-row test set.
    Zero extra training; one-sided resolution confound stated.
  - **Group E — training-free pre-registration**, written BEFORE any arm is scored:
    frozen ifc floor reproduction to 1e-9; non-nestedness certificate via
    `tools/ladder_pair_alignment_audit.py --fail-on mispaired`; `tools/band_retention_probe.py`
    energy above each rung's Nyquist; `tools/design_coverage_audit.py` condition-distance
    statistics **labelled descriptive, explicitly NOT an n_eff diagnostic**.
  - **Group F — mis-specification guards** via `tools/ledger_contamination_audit.py`:
    control column declared N/A on the N-axis (same estimator, budget and procedure at
    every n ⇒ function-class term identically zero) with the width contrast labelled as the
    one genuine function-class contrast; matched `n_fit` asserted within every cell and
    fold; triangle-inequality headroom `D(pred_{n=1}, pred_{n=5})` reported **before** any
    delta is read against the threshold.
  - **Statistics**: primary estimand `Delta_5_1 = mean_skill(n=1,w32) − mean_skill(n=5,w32)`;
    90 % CI by stratified bootstrap (B = 10000, rng 0; Agarwal et al.), stratified by n;
    secondary **paired** column over all 120 nested chains S1⊂…⊂S5 at zero extra training
    cost — the in-job paired control the 12.4 drift-class rule demands on a strict-1-seed
    card. **Equivalence bound = certified ifc MCE 0.9377041289531141**, with three
    pre-registered outcomes, **two of which are claims**: O1 EFFECT (CI entirely above the
    bound), **O2 EQUIVALENCE** (CI entirely inside ±bound — an informative null, Harms &
    Lakens PubMed 30873486), O3 INCONCLUSIVE (half-width > bound, pre-stated so it cannot
    be spun).
  - **Bounding claim (extrapolation-free)**: report [min, max] of condition-only test skill
    over all 31 x 3 cells and state whether r2s3-B3's `A1_lf_cov` 2.150091575784423 lies
    inside or outside it, with the margin against the MCE.
  - **Forbidden and pre-registered**: no scaling law / extrapolation from the curve
    (https://arxiv.org/abs/2103.10948); no ceiling or information-gap claim at N_hf = 5
    (https://arxiv.org/abs/2410.23440); no `n_eff` diagnostic. **A non-monotone curve or
    ladder is a RESULT, not a harness bug** (https://arxiv.org/abs/2211.14061).
  - **Checkpoint-resume**: B3's single-`last.pt` completed-legs + in-flight-leg pattern.
  - **Target-scaler pre-flight**: N/A (section-12 rule names helmholtz and pfc only),
    recorded on the card rather than silently skipped.

- **Recipe**:
```json
{
  "base_family": "none (new from-scratch family; FiLM-FNO backbone re-implemented from models_r2/r2s4_cert_min = r2s4_diag-B1 with provenance comments; NO round-1 reuse; reuses only the factory data_adapters plumbing loaders.load_mf_dataset / geometry.resolve_grid / metrics.finalize_and_write and models/_common/lf_registration.py for the report-only bridging column)",
  "base_commit": "9e10d414e35a96398f7b091bc84ddf936d88acc7",
  "family_dir": "models_r2/r2s4_b4_anatomy",
  "datasets": "ifc_poisson",
  "epochs": 200,
  "seeds": [0],
  "env": {
    "R2S4B4_WIDTH": "32",
    "R2S4B4_BLOCKS": "2",
    "R2S4B4_MODES": "16",
    "R2S4B4_FILM_MLP_WIDTH": "64",
    "R2S4B4_BATCH": "16",
    "R2S4B4_LR": "1e-3",
    "R2S4B4_WD": "1e-5",
    "R2S4B4_CLIP": "1.0",
    "R2S4B4_SCHED": "cosine",
    "R2S4B4_TARGET_NORM": "train_zscore_global",
    "R2S4B4_SPLIT_SEED": "0",
    "R2S4B4_REPLICATES": "3",
    "R2S4B4_REPLICATE_SEMANTICS": "in_job_init_replicates_from_split_seed_not_card_seeds",
    "R2S4B4_SUBSET_LEVELS": "1,2,3,4,5",
    "R2S4B4_SUBSET_ENUMERATION": "exhaustive_all_31",
    "R2S4B4_CAPACITY_WIDTHS": "32,8",
    "R2S4B4_CAPACITY_LEVELS": "1,3,5",
    "R2S4B4_PRIMARY_LEG": "n5_w32_rep0",
    "R2S4B4_PRIMARY_SPLIT": "test_hf",
    "R2S4B4_RUNGS": "fidelity_8,fidelity_16,fidelity_32,fidelity_64",
    "R2S4B4_RUNG_FOLDS": "5",
    "R2S4B4_RUNG_SCORING": "native_grid_rel_l2",
    "R2S4B4_NO_CROSS_RUNG_TRAINING": "1",
    "R2S4B4_BRIDGE_COLUMN": "report_only",
    "R2S4B4_BRIDGE_REGISTRATION": "models_common_lf_registration.resample_fields",
    "R2S4B4_BRIDGE_CONVENTION": "legacy_cell_centred",
    "R2S4B4_NESTED_CHAINS": "all_120",
    "R2S4B4_PRIMARY_ESTIMAND": "delta_skill_n1_minus_n5_w32",
    "R2S4B4_CI_METHOD": "stratified_bootstrap_by_n",
    "R2S4B4_CI_LEVEL": "0.90",
    "R2S4B4_BOOTSTRAP_B": "10000",
    "R2S4B4_BOOTSTRAP_RNG_SEED": "0",
    "R2S4B4_EQUIVALENCE_BOUND": "0.9377041289531141",
    "R2S4B4_EQUIVALENCE_BOUND_SOURCE": "state/noise_floor.json:ifc_poisson.min_claimable_effect",
    "R2S4B4_OUTCOME_RULE": "O1_effect_if_ci_above_bound;O2_equivalence_if_ci_within_bound;O3_inconclusive_if_halfwidth_gt_bound",
    "R2S4B4_LF_EFFECT_BOUND_REFERENCE": "2.150091575784423",
    "R2S4B4_LF_EFFECT_BOUND_SOURCE": "experiment_cards/r2s3_lf_train_signal/batch_3/B3.json:5_actual_result.per_dataset.ifc_poisson.arms.A1_lf_cov.draw_mean_skill",
    "R2S4B4_FLOOR_ARMS": "nn_condition,train_mean,zero",
    "R2S4B4_FLOOR_ARMS_PER_SUBSET": "1",
    "R2S4B4_FLOORS_JSON": "mffp_autoresearch/round2/state/anchors/floors.json",
    "R2S4B4_FLOOR_TOL": "1e-9",
    "R2S4B4_NOISE_FLOOR_JSON": "mffp_autoresearch/round2/state/noise_floor.json",
    "R2S4B4_PREREG_TRAINING_FREE": "floor_repro,ladder_nonnestedness,band_energy_above_rung_nyquist,design_coverage",
    "R2S4B4_LADDER_AUDIT_FAIL_ON": "mispaired",
    "R2S4B4_CONTAMINATION_AUDIT": "control_column_na_same_estimator;matched_nfit_within_cell;triangle_headroom_before_threshold",
    "R2S4B4_F1_INSAMPLE_NRMSE_MAX": "0.10",
    "R2S4B4_TARGET_SCALER_PREFLIGHT": "na_ifc_poisson_not_in_scope",
    "R2S4B4_DUMP_PREDS": "1",
    "R2S4B4_GUARD_DATASETS": "heat_local,fluid,sharp__sod_1d",
    "R2S4B4_GUARD_EPOCHS": "2",
    "R2S4B4_DIAG_OUT": "mffp_autoresearch_outputs/round2/r2s4_diag/B4/eval"
  }
}
```
  Recipe notes: `base_commit` = `round2-substrate` HEAD, verified by
  `git rev-parse round2-substrate` = 9e10d414e35a96398f7b091bc84ddf936d88acc7. Leg budget
  93 + 48 + 60 = **201 trainings** plus 3 guard legs at 2 epochs; every group-A leg is
  200 optimiser steps on ≤ 5 rows of 64x64 and the largest group-C leg is 80 rows of 8x8,
  all in one process with a single dataset load. B3 ran 184 far larger legs in 92 min, so
  expect **45–75 min**; request `--time 02:00:00`. Strict 1 card seed ⇒ only `submit.sh`,
  no `submit_seeds_2_3.sh`. Groups D–F are numpy/closed-form post-processing over
  already-trained legs: no extra GPU, no new dependencies.

- **Expected outcome** (skill units, corrected denominators; own-stream anchor
  `certified_3seed_panel_geomean` **19.817844731907492**, adjudicating per-dataset anchor
  ifc mean skill **8.261220201059428**, ifc MCE **0.9377041289531141**):
  - Primary leg (n = 5, w32, rep 0) test skill **8.0–8.6** — within the MCE of both B1's
    certified 8.261220201059428 and r2s3-B3's `A0_nolf` 8.13438381993564. Instrument
    check, not a claim; a diagnostic card's primary leg is *supposed* to reproduce the
    anchor rather than move it.
  - n = 1 skill **10.5–13.0** (at/above the `nn_condition` floor 10.054890929609687).
  - **`Delta_5_1` predicted +2.0 to +4.5 skill units = 2.1x–4.8x the MCE 0.9377041289531141**
    ⇒ outcome **O1 EFFECT** expected.
  - In-sample nRMSE at n = 5 predicted **< 0.02** vs test 0.2928 (gap ratio > 14x) — the
    variance/sample-limited signature.
  - Rung `gap_ratio` ~30–100 at n_fit = 4 falling to **1.5–5** at n_fit = 80.
  - Bounding claim: min over all 31 x 3 cells predicted **≥ 7.5**, so r2s3-B3's
    `A1_lf_cov` 2.150091575784423 sits **outside** the accessible-HF envelope by **≥ 5.3
    skill units = 5.7x the MCE**.
  - Floors reproduce to 1e-9; `ref_zero` == 1.0 exactly.
  - **vs the noise floor**: every adjudicating threshold is the certified ifc
    `min_claimable_effect` 0.9377041289531141 or `max(that, in-job spread)`; ifc is the
    only dataset the card cites and it is the only floor that applies.

- **Expected falsification**: the hypothesis — *"at N_hf = 5 on ifc_poisson the
  condition→HF surrogate is variance/sample-limited rather than architecture-limited: it
  fits its 5 training rows to near-zero in-sample error while test error sits at ~8x the
  paper bar, marginal HF samples move test skill by more than the certified MCE over 1→5,
  and the generalisation gap closes as the within-rung design grows 20x"* — is falsified if
  ANY of: **(F1)** in-sample nRMSE at n = 5, w32 exceeds **0.10** (= 2.7778 skill units,
  **2.96x** the MCE, whose nRMSE equivalent is 0.9377041289531141 x 0.036 = 0.03375735);
  **(F2)** outcome **O3** fires — the 90 % CI half-width on `Delta_5_1` exceeds
  **0.9377041289531141**; **(F3)** width 8 beats width 32 at n = 5 by more than
  `max(0.9377041289531141, in-job subset x replicate spread)`; **(F4)** the rung
  `gap_ratio` at n_fit = 80 is not smaller than at n_fit = 4 by more than the in-job fold
  spread; or **(F5)** any frozen ifc floor deviates from `state/anchors/floors.json` by
  > 1e-9 relative or `ref_zero` != 1.0 exactly (the card's highest-value outcome — it would
  invalidate every ifc number in the round). *Attached floor-arm reasoning (spec section 3
  / program 2.2)*: `nn_condition` / `train_mean` / `zero` are reported beside the model at
  **every** n, not just n = 5, so the "has this learned anything" comparison exists at every
  point of the curve; at n = 5 they must reproduce 10.054890929609687 /
  11.206332455369639 / 27.77777777777778 to 1e-9, and any curve point where the model does
  not beat its own-n best floor by more than the MCE is **reported but not claimed**. A
  non-monotone curve or ladder is pre-registered as the published ill-behaved-learning-curve
  phenomenon (https://arxiv.org/abs/2211.14061), NOT a falsification and NOT a harness bug.

- **Prior-art verdict quoted** (verbatim from
  `websearches/r2s4_diag/batch_4/report.md`, section "Prior-art verdict", row A —
  candidate "**A — ifc_poisson overfitting anatomy at N_hf ∈ {5, 20, 50}**", verdict
  **`preempted-but-MF-composition-open`**):
  > **No fetched source performs a train-vs-test error decomposition for a field-valued
  > condition→HF surrogate at single-digit HF sample counts.** Also uncited: doing it in
  > copy-LF-skill units against a *pre-certified* per-dataset min-claimable-effect, and on
  > an explicitly non-nested ladder whose rungs are therefore independent designs.
  > **NOT open**: the n_eff/effective-sample-size *diagnostic* (no usable results across
  > two batches; demote to a descriptive statistic) and anything resembling a scaling law
  > / sample-complexity extrapolation from 3 points.

  Citations carried on the row (all bash-fetched in the batch-4 loop):
  https://arxiv.org/abs/2407.17087 (non-nested MF assessed method-by-method) ·
  https://arxiv.org/abs/2408.17075 , https://arxiv.org/html/2408.17075v2
  (paired/unpaired standard, tiny-HF-budget throttle, source-wise error decomposition) ·
  https://arxiv.org/abs/2403.08627 (scarce-HF ⇒ high variance, bias/variance analysis) ·
  https://arxiv.org/abs/2511.20183 (non-nested MF-GP) ·
  https://arxiv.org/abs/2103.10948 , https://arxiv.org/abs/2211.14061 (few-point curves
  unfittable / ill-behaved) · https://arxiv.org/abs/2412.17582 (asymptotic-in-n theory for
  parametric elliptic PDEs) · https://arxiv.org/abs/2508.01211 ("few-shot" ≠ our regime).
  Plus the loop's key remedy, carried into the design:
  > "evaluate null-results using **equivalence tests**, Bayesian estimation, and Bayes
  > factors"; "no statistical approach can actually prove that the null-hypothesis is true"
  — Harms & Lakens 2018, PubMed **30873486**. And binding from earlier batches:
  https://arxiv.org/abs/2410.23440 (**at N_hf = 5 no ceiling / information-gap claim is
  defensible**), https://ar5iv.labs.arxiv.org/html/2108.13264 (Agarwal et al., the adopted
  bootstrap protocol).

- **Immutables self-check**: **pass (11/11)** — positive evidence for each of program.md
  section 5's 8 items plus the 3 round-2 extras is recorded in
  [iteration_1.md](iteration_1.md) section "Immutables self-check". Highlights: no field is
  ever produced by decimating an HF field and the only resampling in the card is a
  *prediction upsample* through the sanctioned ADR r2-0001 entry point (item 1 + the
  section-12 registration rule); the 51 knobs all live in `recipe.env` and reach the family
  only through `score_panel.py --env` (item 5); `seeds: [0]` is strict-1-seed and the R = 3
  replicates are in-job, declared via `R2S4B4_REPLICATE_SEMANTICS`, never reported as a
  seed CI (item 6); every adjudicating threshold is the certified ifc MCE
  0.9377041289531141 or larger, and F1's 0.10 in-sample nRMSE is 2.96x it (item 9); the
  nearest pre-falsified lever is LF low-mode freezing and the card freezes nothing and
  never mixes LF into any training arm — `R2S4B4_NO_CROSS_RUNG_TRAINING=1` (item 10); floor
  arms are recomputed **per subset at every n**, exceeding the requirement (item 11). No
  revision was required, so there is no iteration 2.

- **Anchor reference**: `null` (program.md 4.5 / section 12 — all four round-2 streams are
  gap/lever/diag, the own-stream anchor is implicit, and round 2 has no
  champion-re-targeting tuning stream).

- **Source iteration**: [iteration_1.md](iteration_1.md)

## B4-or-close decision (program 4.6)

**Decision: run B4.** `r2s4_diag-B3` part 7 recommends "close the stream **unless** the
maintainer judges criterion 1 (ifc_poisson at the paper bar) still reachable by another
stream, in which case run ONE ifc-ladder card scoped to N_hf in {5, 20, 50} with the in-job
paired protocol and a pre-registered 'unclaimable' outcome." I read
`r2s3_lf_train_signal/batch_3/B3.json` part 5 directly: on ifc_poisson `A1_lf_cov` scores
**2.150091575784423** (nRMSE 0.07740329672823923 vs the paper bar 0.036) against `A0_nolf`
8.13438381993564, an effect of 5.984292244151218 skill units that passes its operative
threshold. Criterion 1's ifc route is not merely reachable, it carries the round's largest
value-of-LF number — and `r2s2_stacked-B3` is in build with a panel (hence ifc) leg. B3's
escape clause therefore fires *for* a B4, and this proposal is precisely the card B3
specified: ifc-scoped, in-job paired (120 nested chains), with the "unclaimable" outcome
pre-registered — upgraded, per the websearcher, from a bare "unclaimable" label to a
**claimable equivalence statement** bounded by the certified MCE.

The close-now option was weighed and rejected on the verdict's own grounds: row B says a
bare close is "**not retrieval-supported**" because "no fetched source retires a criterion
for INFEASIBILITY (only saturation)" and futility stopping carries a stated type-II price
(Lachin 2005, PubMed 16134130); row B-prime (close *with* the futility statement) is
explicitly "*a report artifact, not an experiment card*" — so spending the slot on it would
produce no card at all.

**Carried recommendation to the maintainer** (not this slot's business, but it should not
be lost): ship row B-prime's futility/equivalence statement in the round report regardless
of this card's outcome, together with the stream's promoted-tool suite, since the verdict
identifies that as the retrieval-supported form of a close-out.

## Reopen candidates

| Candidate | Verdict (retry/drop) | Eased conditions | Source iteration |
|---|---|---|---|
| *(none — `r2s4_diag` B1/B2/B3 all carry `reopen_candidate: false` and `skipped_reason: null`, verified by reading each card JSON)* | n/a | n/a | [iteration_1.md](iteration_1.md) |

## Skipped slot

Not applicable — the slot is filled.

## Summary table

| Slot | Category | One-liner | Status |
|---|---|---|---|
| B4 | diagnostic / ifc_poisson few-HF anatomy (exhaustive HF-subset curve + within-rung gap ladder, pre-registered equivalence outcome) | Exhausts all 31 HF subsets and all 4 ifc rungs on their native grids to decide whether ifc_poisson at N_hf = 5 is sample-limited or architecture-limited, with the certified MCE 0.9377041289531141 as an equivalence bound so both branches are claims — and bounds r2s3-B3's 5.98-skill-unit LF effect without extrapolating. | filled |
