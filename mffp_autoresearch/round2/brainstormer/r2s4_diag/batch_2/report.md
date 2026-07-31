# Brainstormer Report — Stream `r2s4_diag`, Batch 2

**Stream**: `r2s4_diag` (class: diag)
**Batch**: 2
**Total iterations**: 1 (immutables self-check passed on the first pass; no self-revision needed)
**Slot filled**: 1 / 1 (no skip)
**Reopen candidates resolved**: 0 of 0 (none exist — all four round-2 cards carry `reopen_candidate: false`)

## Slot

- **Category**: `diagnostic / value-of-LF accounting (DOPD advantage-gap ported to fields)
  + HF-sample-count scaling of the transfer effect`

- **Card type**: `diagnostic` (WITH training — the program.md §12.4 exception B1
  established: `epochs = 200`, `seeds = [0,1,2]`)

- **Motivation**: the batch-2 prior-art verdict row **D1** reads
  `preempted-but-MF-composition-open (cite)` — "Nothing found pre-registers the null
  datasets **from a measured training-free ceiling**, nor uses LF *fields* as privileged
  info for a *field-valued* output scored in copy-LF skill. Concrete adoptable design:
  DOPD's advantage-gap split (capability gap vs information gap) ported to fields."
  This card **is** that composition: r2s4-B1's measured training-free barriers
  (fisher_kpp 1.010x, pfc 1.139x, allen_cahn ~1.11x — part 6 T2-F1/T2-F2) pre-register the
  null datasets, and the capability/information split is adopted by citation rather than
  invented. It is also the round's only unmeasured success criterion (program.md §1
  criterion 1: "a matched with/without-LF-training contrast (same architecture, same
  budget)"), and it discharges three of B1's four part-7 owed items — (1) pose the contrast
  where headroom exists with the barrier-bound datasets pre-registered as nulls, (3) make
  train-fold-calibrated shrinkage a required reported column, (4) re-certify the seed
  spread on the arm actually compared. Item (2) — "build a ceiling estimator that works at
  19 condition dims and at N_hf=5" — is **deliberately NOT attempted**, on the batch-2
  websearcher's binding instruction 3 ("Do not propose 'build a ceiling estimator'";
  D2 is `preempted`, the 19-dim failure is "a **known theorem-level property**, not a bug",
  and at N_hf=5 arXiv:2410.23440 says no ceiling claim is defensible). The card instead
  measures a *relative* LF-present-vs-ablated gap, which needs no absolute ceiling and
  therefore also covers cahn_hilliard and ifc_poisson, B1's declared blind spot.

- **Concrete config**: new from-scratch family `models_r2/r2s4_b2_lfvalue/`
  (`manifest.json`, `model.py`, `smoke_eval.py`, `INSPIRATION.md`) plus one probe
  `probes/lf_value_accounting.py`. Backbone identical to `r2s4_cert_min` (width 32, 2
  FiLM-FNO blocks, 16 modes, FiLM-MLP width 64, ~1M params), re-implemented in the new
  family dir with provenance comments; optimizer/schedule/normalization byte-identical to
  B1 (AdamW 1e-3, wd 1e-5, batch 16, cosine, clip 1.0, MSE in `train_zscore_global` target
  space, 200 epochs).
  - **Folds** fixed by `R2S4B2_SPLIT_SEED=0`, identical across arms / N levels / training
    seeds: fit 0.8 / val 0.1 (model selection ONLY) / **inner 0.1 (LF-available evaluation
    and lambda* calibration ONLY)** — disjoint by construction because of round 1's D3
    val_idx double-consumption caveat (§12.1). ifc_poisson (N_hf=5): val and inner disabled
    (`VAL_MIN_N`/`INNER_MIN_N` = 20), final-epoch weights (B1's recorded caveat).
  - **LF definition**, identical on every dataset: the finest train LF rung
    `max(lf_fids)` — the same rung `eval/panel_data.py::copylf_prediction` uses for the
    skill denominator — upsampled to the HF grid with the same per-dataset ADR r2-0001
    convention (`node_aligned_periodic` / `dirichlet_node` / `legacy_cell_centred`),
    vendored with provenance and asserted at contract tier to agree with the eval
    implementation on the TRAIN split (a read-only call; the eval layer is not edited).
    Only `stripped_data` is read, at train and at test.
  - **Arms** (same backbone, optimizer, budget, folds):
    1. `T0_cond_only` — condition-only. **PRIMARY scored arm** (`splits.test_hf`); the
       without-LF arm and the in-job paired control (drift-class rule).
    2. `T1_lf_aux` — same trunk + a second 1x1 head predicting the upsampled LF field;
       loss = MSE_HF + `AUX_WEIGHT`*MSE_LF with a **separate LF scaler** (r1 s5 revin_lf
       two-scaler finding, §12.3; also the mechanism r2s3-B1's crater is attributed to).
       At test only the HF head runs, so the scored forward is identical to T0's.
    3. `I1_lf_teacher` — coords(2ch) + upsampled **real** LF(1ch); evaluated on the inner
       fold ONLY, structurally no test code path (immutable §5.9).
    4. `I2_lf_ablated` — identical architecture and budget, LF channel replaced by the
       constant fit-fold-mean LF field, **retrained from scratch**; inner fold ONLY.
       (I1 vs I2 = the DOPD **information gap**; T0 vs I2 on the inner fold = the
       **capability gap**, free.)
    On ifc_poisson I1/I2 run 5-fold leave-one-out and every number from them is labelled
    **anecdote-grade** and excluded from all falsification clauses (arXiv:2410.23440).
  - **N_fit sweep**: T0 and T1 additionally at `N_FIT_LEVELS = 20, 80` (nested subsamples
    of the same fit fold; 320 is the full leg) on the five N=400 datasets, with val / inner
    / test held fixed — §12.4's overfitting-anatomy direction folded in as the card's risky
    prediction.
  - **Mandatory reported columns** per arm x dataset: raw and shrunk skill
    (`P_bar + lambda*(P - P_bar)`, lambda* on grid 0.0:1.5:0.05 fitted on the **inner
    fold**, never on test), lambda* with a B=2000 bootstrap CI over the <=40 inner points
    (the websearcher's certifiability requirement), the three floor arms
    `ref_nn_condition`/`ref_train_mean`/`ref_zero` through the same nRMSE path (§2.2, B1's
    merge pattern, `test_hf` byte-identical), paired per-seed deltas, the in-job 3-seed
    spread of each compared pair, the operative threshold, `information_gap`,
    `capability_gap` and `transfer_efficiency`. Guard leg at contract tier (2 epochs;
    heat_local, fluid, sharp__sod_1d).
  - **Project-convention statistic** (defined locally, no literature standard claimed —
    websearcher instruction 6):
    `transfer_efficiency := [nRMSE(T0,test) - nRMSE(T1,test)] / [nRMSE(I2,inner) - nRMSE(I1,inner)]`,
    reported as undefined when the denominator is below its own in-job null, with the
    standing caveat that numerator and denominator live on different splits of the same
    generator.
  - Adapted-on-use from `tools/`: `conditional_mean_collapse.py` (shrinkage / lambda* /
    own-mean broadcast) and `condition_predictability_ceiling.py` (the barrier numbers used
    in the pre-registration table); adapted versions promoted via the register turn.

- **Recipe**:

```json
{
  "base_family": "none (new from-scratch family; backbone re-implemented from models_r2/r2s4_cert_min = r2s4_diag-B1, same round, with provenance comments; NO round-1 reuse; reuses only the factory data_adapters plumbing loaders.load_mf_dataset / geometry.resolve_grid / metrics.finalize_and_write)",
  "base_commit": "9e10d414e35a96398f7b091bc84ddf936d88acc7",
  "family_dir": "models_r2/r2s4_b2_lfvalue",
  "datasets": "panel",
  "epochs": 200,
  "seeds": [0, 1, 2],
  "env": {
    "R2S4B2_WIDTH": "32",
    "R2S4B2_BLOCKS": "2",
    "R2S4B2_MODES": "16",
    "R2S4B2_FILM_MLP_WIDTH": "64",
    "R2S4B2_BATCH": "16",
    "R2S4B2_LR": "1e-3",
    "R2S4B2_WD": "1e-5",
    "R2S4B2_CLIP": "1.0",
    "R2S4B2_SCHED": "cosine",
    "R2S4B2_TARGET_NORM": "train_zscore_global",
    "R2S4B2_LF_TARGET_NORM": "train_zscore_global_lf_separate",
    "R2S4B2_ARMS": "T0_cond_only,T1_lf_aux,I1_lf_teacher,I2_lf_ablated",
    "R2S4B2_PRIMARY_ARM": "T0_cond_only",
    "R2S4B2_SPLIT_SEED": "0",
    "R2S4B2_FIT_FRAC": "0.8",
    "R2S4B2_VAL_FRAC": "0.1",
    "R2S4B2_INNER_FRAC": "0.1",
    "R2S4B2_VAL_MIN_N": "20",
    "R2S4B2_INNER_MIN_N": "20",
    "R2S4B2_IFC_INNER_MODE": "loo_anecdote",
    "R2S4B2_N_FIT_LEVELS": "20,80",
    "R2S4B2_N_FIT_SWEEP_ARMS": "T0_cond_only,T1_lf_aux",
    "R2S4B2_LF_RUNG": "max_lf_fid",
    "R2S4B2_LF_UPSAMPLE": "match_copylf_convention",
    "R2S4B2_LF_ABLATION": "fit_fold_mean_lf",
    "R2S4B2_AUX_WEIGHT": "1.0",
    "R2S4B2_SHRINK_GRID": "0.0:1.5:0.05",
    "R2S4B2_SHRINK_CALIB": "inner_fold",
    "R2S4B2_SHRINK_BOOT": "2000",
    "R2S4B2_FLOOR_ARMS": "nn_condition,train_mean,zero",
    "R2S4B2_FLOORS_JSON": "mffp_autoresearch/round2/state/anchors/floors.json",
    "R2S4B2_NOISE_FLOOR_JSON": "mffp_autoresearch/round2/state/noise_floor.json",
    "R2S4B2_BOOTSTRAP_B": "10000",
    "R2S4B2_GUARD_EPOCHS": "2",
    "R2S4B2_DIAG_OUT": "mffp_autoresearch_outputs/round2/r2s4_diag/B2/eval"
  }
}
```

  `base_commit` = `round2-substrate` HEAD, verified by `git rev-parse round2-substrate`.
  Cost: ~44 trainings/seed of a ~1M-param FNO against B1's 6 at **4.13-4.42 min** total per
  seed (`state/timing_ledger.json`, h200), most on smaller fit folds -> **~30-45 min/seed**;
  request `--time 02:00:00`. The orchestrator may submit seed 0 via `submit.sh` and seeds
  1-2 via `submit_seeds_2_3.sh` — seed 0 answers the direction, seeds 1-2 deliver the
  re-certification B1 part 7 item (4) owes.

- **Expected outcome** (skill units, corrected denominators; own-stream anchor =
  `certified_3seed_panel_geomean` **19.8178**, panel `min_claimable_effect` **1.14187**):
  - Primary arm `T0_cond_only` panel geomean **19.8-22.5** (delta **+0.5 to +2.5** vs the
    19.8178 anchor, from the 320-of-400 fit fold; may exceed the 1.14187 panel floor and is
    itself the card's first N-scaling datum).
  - **Transfer gap** `|T1 - T0|` at full N vs `operative_threshold = max(certified MCE,
    in-job 3-seed paired spread)`: fisher_kpp < 0.05 (floor **0.00071**), pfc < 0.5
    (**0.21303**), allen_cahn < 1.5 (**0.87970**), cahn_hilliard < 0.3 (**0.09125**) — all
    pre-registered **nulls**; helmholtz 0-3 raw (**2.95299**; plausibly claimable on the
    shrunk column, since lambda* removes exactly the harmful condition-dependence that made
    B1's helmholtz spread 2.95299); **ifc_poisson the one predicted claimable full-N
    effect, sign NEGATIVE, magnitude 0.5-5 vs floor 0.93770** (r2s3-B1's unmatched
    comparable was -7.3497).
  - **Information gap** `nRMSE(I2)/nRMSE(I1)` on the inner fold: **>= 10** on fisher_kpp /
    pfc / allen_cahn (copy-LF nRMSE 0.02145 / 0.00738 / 0.00178 vs a condition-only barrier
    of 0.2479 / 0.3531 / 0.2623 — the realized IC lives in the LF field, ADR r2-0003);
    **smallest on cahn_hilliard (1.2-3)** whose 16 `ic_c*` dims put the IC in the condition
    — that ranking is a falsifiable structural prediction.
  - **Capability gap** `T0 - I2` on the inner fold: within the operative threshold on >= 5
    of 6 datasets (pre-registered from r2s1-B1 I1, "the architecture is not the binding
    constraint").
  - **transfer_efficiency** < 0.05 on the four sharp datasets; unknown on helmholtz;
    plausibly negative on ifc_poisson.
  - **N_fit sweep**: `|T1 - T0|` at N=20 exceeds its N=320 value by more than the operative
    threshold on >= 3 of 5 sweepable datasets.
  - **vs noise floor**: every threshold used is `max(certified MCE, in-job spread)`, hence
    >= the certified floor by construction on every cited dataset; the numbers are quoted
    verbatim above and B1's H5 ("the constants... are a LOWER bound for any less-collapsed
    successor") is why the `max(...)` form replaces the bare constant.
  - **Honest read on criterion 1**: I expect claimable full-N transfer effects on **1-2**
    panel datasets, not 3. If that is what lands, the deliverable is a certified value-of-LF
    measurement on a **sensitivity-proven** instrument plus the N-scaling law, and the
    maintainer adjudicates whether a certified null on a proven instrument satisfies
    criterion 1. I am not predicting 3 claimable effects to make the criterion come out
    right.

- **Expected falsification**: the card's hypothesis — "LF as a training-only signal pays
  only where the condition-only estimator is SAMPLE-limited, not where it is
  INFORMATION-limited, and a matched LF-ablation instrument can prove it sees the
  information that exists" — is falsified if ANY of: **(F1, instrument)** the inner-fold
  information-gap ratio `nRMSE(I2)/nRMSE(I1)` is < 2.0 on >= 2 of {fisher_kpp, pfc,
  allen_cahn}, where copy-LF nRMSE 0.02145/0.00738/0.00178 against a condition-only barrier
  0.2479/0.3531/0.2623 predicts >= 10; **(F2, barrier)** at full N_fit `|T1 - T0|` exceeds
  `max(certified min_claimable_effect, in-job 3-seed paired spread)` on >= 2 of {fisher_kpp
  0.0007136812826775696, pfc 0.21302734961699343, allen_cahn 0.8797047190126648};
  **(F3, scaling)** `|T1 - T0|` at N_fit=20 fails to exceed its N_fit=320 value by more than
  the operative threshold on >= 3 of the 5 sweepable datasets; or **(F4, calibration)** the
  inner-fold lambda* bootstrap CI (B=2000, n <= 40) admits a skill range exceeding the
  operative threshold on >= 4 of the 5 shrinkable panel datasets, or the raw and shrunk
  columns give different claimable/not-claimable verdicts on >= 2 panel datasets.
  *Attached reasoning*: the mandatory floor arms (`nn_condition`/`train_mean`/`zero` from
  `state/anchors/floors.json`) are reported as `ref_*` splits beside every arm on every
  dataset and are the standing "has this learned anything" comparison (§2.2) — helmholtz's
  zero column 3.3441 stays visible under the standing report-only discipline (B1's certifier
  scored 6.9438 there, i.e. worse than the zero field), and a transfer effect on a dataset
  where neither arm beats its best floor is reported but not claimed.

- **Prior-art verdict quoted** (verbatim from
  `websearches/r2s4_diag/batch_2/report.md`, `## Prior-art verdict`, row D1):
  > **D1** — value-of-LF accounting: matched architecture/budget +/- LF-training-signal,
  > helmholtz-first (only certified headroom), fisher_kpp/pfc/allen_cahn **pre-registered
  > as nulls** by B1's measured aleatoric barrier | `preempted-but-MF-composition-open
  > (cite)` | MF scaling laws — https://arxiv.org/abs/2511.01830 ; DOPD "privilege
  > illusion" — https://arxiv.org/html/2606.30626v1 ; negative asymmetric transfer —
  > https://arxiv.org/abs/2510.12615 ; (batch 1) Yang et al. non-monotone LUPI law —
  > https://arxiv.org/abs/2209.08754 | Nothing found pre-registers the null datasets **from
  > a measured training-free ceiling**, nor uses LF *fields* as privileged info for a
  > *field-valued* output scored in copy-LF skill. Concrete adoptable design: DOPD's
  > advantage-gap split (capability gap vs information gap) ported to fields.

  Binding secondary rows: **D2** `preempted (cite)` — "At N_hf = 5, arXiv:2410.23440 says no
  ceiling claim is defensible" (why no ceiling estimator is proposed and why ifc's
  inner-fold legs are anecdote-grade); **D3** `preempted-but-MF-composition-open (cite)` —
  "**lambda\* as a reported diagnostic statistic** ... was not found" and FALCON's ~1000-point
  calibration requirement (https://arxiv.org/html/2607.01354v1) (why lambda* is a reported
  column with a bootstrap CI, not a claimed arm); **D4**
  `preempted-but-MF-composition-open (cite)` — "if B2/B3 uses [n_eff] it must define it
  locally and say so" (why `transfer_efficiency` is labelled a project convention and no
  n_eff statistic is used at all).

- **Immutables self-check**: **pass (11/11)** — positive evidence for each item is written
  out in [iteration_1.md](iteration_1.md) §"Immutables self-check". Headlines:
  (1) only `stripped_data` is read and the N_fit sweep subsamples the existing fit fold —
  no sample is added and LF is the shipped coarse solve, never downsampled HF;
  (3) the sole `eval/` interaction is a read-only call in a contract-tier assertion;
  (5) all 30 knobs are `R2S4B2_*` env vars inside `recipe.env`, the six-arg CLI is
  unchanged; (6) `seeds: [0,1,2]` is exactly the immutable's seed set at smoke tier 200
  (guard at contract tier 2); (8) `<ckpt_dir>/last.pt` is keyed on (arm, dataset, N level,
  fold, epochs_target, grid, seed) and the arm loop itself is resumable;
  (9) every threshold is `max(certified MCE, in-job spread)` >= the certified floor by
  construction, numbers quoted; (10) nearest pre-falsified lever is **LF low-mode freezing**
  — that froze LF's low modes on an LF-consuming model *at test*, whereas this card uses LF
  as a soft auxiliary training target absent from the scored forward pass and claims no win
  from it; (11) floor arms are merged beside every arm and appear in the falsification
  reasoning despite this being a diagnostic card.

- **Anchor reference**: `null` (program.md §4.5 — null for all four round-2 streams; the
  own-stream anchor `certified_3seed_panel_geomean` 19.8178 is implicit)

- **Source iteration**: [iteration_1.md](iteration_1.md)

## Reopen candidates

| Candidate | Verdict (retry/drop) | Eased conditions | Source iteration |
|---|---|---|---|
| _none_ — all four round-2 batch-1 cards (`experiment_cards/{r2s1_direct,r2s2_stacked,r2s3_lf_train_signal,r2s4_diag}/batch_1/B1.json`) carry `reopen_candidate: false`, verified by reading each file; no candidate has ever been raised in this stream | n/a | n/a | [iteration_1.md](iteration_1.md) |

## Skipped slot

Not applicable — the slot is filled.

## Summary table

| Slot | Category | One-liner | Status |
|---|---|---|---|
| 1 / 1 | `diagnostic / value-of-LF accounting (DOPD advantage-gap ported to fields) + HF-sample-count scaling` | Matched +/- LF-training contrast (`T0_cond_only` vs `T1_lf_aux`) on the stripped test view, decomposed against an inner-fold LF-ablation advantage gap (`I1_lf_teacher` vs `I2_lf_ablated`) as the instrument's positive control, swept over N_fit in {20,80,320} to test "LF pays only where the estimator is sample-limited", with lambda* shrinkage and re-certified per-dataset thresholds | filled |
