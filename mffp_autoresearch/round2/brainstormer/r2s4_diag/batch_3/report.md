# Brainstormer Report — Stream `r2s4_diag`, Batch 3

**Stream**: `r2s4_diag` (class: diag)
**Batch**: 3
**Total iterations**: 1
**Slot filled**: 1 / 1 (no skip)
**Reopen candidates resolved**: 0 of 0 (none exist)

## Slot

- **Category**: `diagnostic / teacher-projection channel ledger (reachable vs unreachable
  privileged advantage) + test-split paired distillation contrast`

- **Card type**: `diagnostic` (WITH training, strict 1 seed; no seeds 1-2)

- **Motivation**: the batch-3 prior-art verdict row **D1** reads
  `preempted-but-MF-composition-open (cite)`, with the open column verbatim:
  *"Splitting privileged advantage into reachable/unreachable is published - but **no fetched
  source fits a map from student-observable inputs to the teacher's own predictions and scores
  that projection in the task metric** (AR-OPD: "No explicit function is fit"; CCH is
  representation-level for classification labels; ViCuR is a design principle). Nothing for a
  **field-valued** output in **copy-LF skill** units with a **coarse PDE solve** as the
  privileged channel and a **realized random IC** as the unobservable component; nothing
  pre-registers the outcome from an independently measured training-free barrier."*
  This card is that composition. `r2s4_diag-B2` closed the target-side channel (|T1-T0| inside
  its operative threshold in 15/15 dataset x N cells) and measured a large input-side teacher
  advantage (inner-fold `T0` vs `I1_lf_teacher` skill 36.363/0.384 pfc, 120.156/5.653
  allen_cahn, 11.323/0.838 fisher_kpp, 11.916/0.294 cahn_hilliard, 6.829/2.756 helmholtz;
  information-gap ratios 3.16-95.3, claimable 5/5) but never asked whether ANY of that
  advantage is a function of the condition - the last unmeasured channel of program.md 1
  criterion 1 and, per the orchestrator, the round's last diagnostic slot. The card fits an
  out-of-fold condition -> teacher-prediction map and scores the projection in copy-LF skill,
  pre-registering its nulls from an independently measured training-free barrier (B2 T1-F1/T1-F3
  centred cos(HF, LF-up) >= 0.997 and copy-LF train rel-L2 0.00194-0.02086 on the four sharp
  datasets; 0.3099 / 0.26506 on helmholtz). The reachable/unreachable split is adopted **by
  citation** (AR-OPD https://arxiv.org/html/2606.10385v1, DOPD https://arxiv.org/html/2606.30626v1),
  the aliasing mechanism is cited not asserted (https://arxiv.org/html/2505.09546, "the student
  state ... is given by a surjective mapping f(s~)=s" = ADR r2-0003), and TRIE
  (https://arxiv.org/html/2607.00196) carries the stochastic-map scoring caveat. It is a
  measurement, not a lever (12.4: "r2s4 measures, r2s3 optimizes").

- **Concrete config**:
  New from-scratch family `models_r2/r2s4_b3_projection/` (`manifest.json`, `model.py`,
  `projection.py`, `lf_reference.py`, `smoke_eval.py`, `INSPIRATION.md`) plus one probe
  `probes/teacher_projection_ledger.py`. Backbone identical to `r2s4_b2_lfvalue` /
  `r2s4_cert_min` (width 32, 2 FiLM-FNO blocks, 16 modes, FiLM-MLP width 64, ~1.06M params),
  re-implemented in the new family dir with provenance comments; optimizer/schedule/
  normalization byte-identical to B1/B2 (AdamW 1e-3, wd 1e-5, batch 16, cosine, clip 1.0, MSE
  in `train_zscore_global` target space, 200 epochs). Only `stripped_data` is read, at train
  and at test.
  - **Two-level folds**, fixed by `R2S4B3_SPLIT_SEED=0`, identical for every arm. Outer:
    5 folds of 80 over the 400 train rows; for outer fold k, `P_k` = the other 320 rows
    (matches B2's N_fit = 320 exactly) with a 40-row val slice carved inside `P_k` for HF-head
    model selection (same rule for every arm), and `E_k` = fold k is the evaluation slice.
    Inner: a 4-fold cross-fit **inside `P_k`** (teachers on 240 rows) that produces out-of-fold
    teacher predictions on all of `P_k`. No model that ever saw `E_k` contributes to the
    projection's targets or fit -> the projection is leakage-free by construction.
  - **Arms** (same backbone, optimizer, budget, folds):
    1. `T0_cond_only` - condition-only student. **PRIMARY scored arm** (`splits.test_hf`),
       trained once per dataset on B2's exact fixed split (fit 320 / val 40) so its test column
       is a 1-seed reproduction of B2's T0, plus one model per outer fold for the paired ledger.
    2. `I1_lf_teacher` - coords(2ch) + upsampled **real** LF(1ch), train-time only; evaluated on
       `E_k` only, **structurally no test code path** (immutable 5.9 - the stripped test view
       has no LF; this is why the ledger is measured on held-out TRAIN rows).
    3. `proj_knn` - k-NN average in per-dim train-standardised condition space over the
       teacher's OOF predictions on `P_k`; k on {1,2,4,8,16,32,64} by LOO **inside `P_k` only**.
    4. `proj_ridge` - closed-form ridge (pure numpy/torch, no new deps) from a degree-2
       polynomial condition feature map to the field; alpha by GCV inside `P_k` only; degree
       falls back to 1 if d_feat > 0.5 * n_fit (cahn_hilliard: 19 dims -> 210 features vs 320
       rows, so degree 2 is retained and the fallback is a recorded guard).
    5. `proj_nn` - the SAME FiLM-FNO at the same budget trained on the teacher's OOF targets
       (the genuine distillation student); condition-only at test, so it is **also scored on
       `test_hf`** and paired with `T0_k` fold-by-fold at zero extra training cost.
    `proj_best` = the estimator with the best **fit-side** criterion, selected without touching
    `E_k`; all three projections are reported regardless.
  - **The ledger** (all three quantities in the SAME units - skill on the same OOF rows with the
    same frozen denominator - so the identity is exact and B2's `transfer_efficiency` type
    mismatch cannot recur): `advantage_total = skill(T0) - skill(I1)`,
    `advantage_reachable = skill(T0) - skill(proj_best)`,
    `advantage_unreachable = skill(proj_best) - skill(I1)`, with
    `reachable + unreachable = total` checked numerically and
    `reachable_fraction = reachable / total` reported **only when `advantage_total` exceeds the
    operative threshold**. Names are project-local definitions; the total/reachable/unreachable
    *split concept* is adopted by citation (AR-OPD, DOPD).
  - **Operative threshold** per dataset/contrast:
    `max(certified min_claimable_effect (state/noise_floor.json), B2's fold-fixed same-model
    3-seed T0 spread, this card's in-job 5-fold paired spread)`. The 5 outer folds supply the
    in-job paired distribution, which is how a strict-1-seed card satisfies the 12.4
    drift-class rule ("only in-job paired controls are controls").
  - **Training-free pre-registration** (seconds, TRAIN split, reproduces B2 T1-F1/T1-F3):
    centred `cos(HF, LF-up)` and copy-LF train rel-L2 per dataset, written to the diagnostic
    JSON **before** any arm is scored; `advantage_reachable ~ 0` is pre-registered wherever
    cos >= 0.997.
  - **Dataset scoping**: ledger on helmholtz + the 4 sharp datasets; **helmholtz is
    report-only and adjudicates nothing** (B2 T2-F5: 3-seed T0 spread 1.6363 mean-of-ratios vs
    0.0656 energy-pooled, 24.9x), carried with an interpretive energy-pooled twin column -
    every scored number stays mean-of-ratios (immutable 5.4 untouched) and the artifact is
    presented as **project-local** per the D3 verdict. **ifc_poisson carries NO LF-paired arm**
    (B2 T2-F6: 0% of rows paired to their nearest condition under the `lf[:n_hf]` rule) - only
    the primary `T0` leg + floor arms, labelled anecdote-grade (N_hf = 5,
    https://arxiv.org/abs/2410.23440). `tools/ladder_pair_alignment_audit.py --fail-on
    mispaired` runs as a build pre-flight on every dataset carrying an LF arm, and
    `lf_reference.py` asserts `max_abs_diff == 0.0` against
    `eval/panel_data.py::copylf_prediction` on the TRAIN split (read-only call).
  - **Mandatory reported columns** per dataset: primary `T0` test skill + the three floor arms
    `ref_nn_condition` / `ref_train_mean` / `ref_zero` through the same nRMSE path (2.2, B2's
    merged-split pattern); the ledger triple with its operative threshold and claimable flag;
    the 5 fold-level paired deltas for `T0 - proj_nn` on `test_hf`; `proj_knn`/`proj_ridge`/
    `proj_nn` side by side; the inner-teacher vs outer-teacher OOF nRMSE ratio (instrument
    check); `I1` OOF skill against B2's inner-fold values (reproduction check). Guard leg at
    contract tier (2 epochs; heat_local, fluid, sharp__sod_1d).
  - **Artifacts** (B2 constraint 3): `preds_test.npz` and `preds_oof.npz` dumped per arm and
    fold, plus per-leg checkpoints, so mechanism turns are not limited to summary statistics.
  - **Checkpoint-resume**: B2's pattern - a single `<ckpt_dir>/last.pt` holding completed-leg
    results plus the in-flight leg's model/opt/sched/RNG state; a resumed job replays finished
    legs and continues the in-flight one at its stored epoch (immutable 5.8).

- **Recipe**:
```json
{
  "base_family": "none (new from-scratch family; FiLM-FNO backbone re-implemented from models_r2/r2s4_b2_lfvalue = r2s4_diag-B2 and models_r2/r2s4_cert_min = r2s4_diag-B1, same round, with provenance comments; NO round-1 reuse; reuses only the factory data_adapters plumbing loaders.load_mf_dataset / geometry.resolve_grid / metrics.finalize_and_write)",
  "base_commit": "9e10d414e35a96398f7b091bc84ddf936d88acc7",
  "family_dir": "models_r2/r2s4_b3_projection",
  "datasets": "panel",
  "epochs": 200,
  "seeds": [0],
  "env": {
    "R2S4B3_WIDTH": "32",
    "R2S4B3_BLOCKS": "2",
    "R2S4B3_MODES": "16",
    "R2S4B3_FILM_MLP_WIDTH": "64",
    "R2S4B3_BATCH": "16",
    "R2S4B3_LR": "1e-3",
    "R2S4B3_WD": "1e-5",
    "R2S4B3_CLIP": "1.0",
    "R2S4B3_SCHED": "cosine",
    "R2S4B3_TARGET_NORM": "train_zscore_global",
    "R2S4B3_ARMS": "T0_cond_only,I1_lf_teacher,proj_knn,proj_ridge,proj_nn",
    "R2S4B3_PRIMARY_ARM": "T0_cond_only",
    "R2S4B3_SPLIT_SEED": "0",
    "R2S4B3_OUTER_FOLDS": "5",
    "R2S4B3_INNER_FOLDS": "4",
    "R2S4B3_VAL_FRAC_IN_FIT": "0.125",
    "R2S4B3_VAL_MIN_N": "20",
    "R2S4B3_PRIMARY_SPLIT": "b2_fixed_fit0.8_val0.1",
    "R2S4B3_LEDGER_DATASETS": "ext__helmholtz_2d,sharp__phase_field_crystal_2d,sharp__allen_cahn_2d,sharp__fisher_kpp_2d,sharp__cahn_hilliard",
    "R2S4B3_REPORT_ONLY_DATASETS": "ext__helmholtz_2d",
    "R2S4B3_IFC_MODE": "primary_t0_only_anecdote",
    "R2S4B3_LF_RUNG": "max_lf_fid",
    "R2S4B3_LF_UPSAMPLE": "match_copylf_convention",
    "R2S4B3_PROJ_TARGET": "teacher_oof",
    "R2S4B3_PROJ_KNN_K": "1,2,4,8,16,32,64",
    "R2S4B3_PROJ_KNN_SELECT": "loo_fit_side",
    "R2S4B3_PROJ_RIDGE_DEGREE": "2",
    "R2S4B3_PROJ_RIDGE_DEGREE_FALLBACK_RULE": "degree1_if_dfeat_gt_half_nfit",
    "R2S4B3_PROJ_RIDGE_ALPHA_GRID": "1e-6:1e3:log12",
    "R2S4B3_PROJ_RIDGE_SELECT": "gcv_fit_side",
    "R2S4B3_PROJ_BEST_SELECT": "fit_side_only",
    "R2S4B3_PROJ_NN_SCORED_ON_TEST": "1",
    "R2S4B3_THRESHOLD_RULE": "max(certified_mce, b2_fold_fixed_t0_spread, in_job_fold_paired_spread)",
    "R2S4B3_B2_T0_SPREAD": "ext__helmholtz_2d:1.6363313226312677,sharp__phase_field_crystal_2d:0.28372761657901435,sharp__allen_cahn_2d:0.9191521219144931,sharp__fisher_kpp_2d:0.0004592455883685176,sharp__cahn_hilliard:0.1847460640603149",
    "R2S4B3_PREREG_TRAINING_FREE": "cos_centred_hf_lfup,copylf_train_rel_l2",
    "R2S4B3_PREREG_COS_NULL_CUTOFF": "0.997",
    "R2S4B3_ENERGY_POOLED_TWIN": "ext__helmholtz_2d",
    "R2S4B3_FLOOR_ARMS": "nn_condition,train_mean,zero",
    "R2S4B3_FLOORS_JSON": "mffp_autoresearch/round2/state/anchors/floors.json",
    "R2S4B3_NOISE_FLOOR_JSON": "mffp_autoresearch/round2/state/noise_floor.json",
    "R2S4B3_LADDER_AUDIT_FAIL_ON": "mispaired",
    "R2S4B3_DUMP_PREDS": "1",
    "R2S4B3_BOOTSTRAP_B": "10000",
    "R2S4B3_GUARD_EPOCHS": "2",
    "R2S4B3_DIAG_OUT": "mffp_autoresearch_outputs/round2/r2s4_diag/B3/eval"
  },
  "_brainstormer_recipe_notes": "base_commit = round2-substrate HEAD, verified by `git rev-parse round2-substrate` = 9e10d414e35a96398f7b091bc84ddf936d88acc7. Cost: 5 ledger datasets x [1 primary T0 + 5 outer folds x (T0_k + I1_k + 4 inner teachers + proj_nn_k)] = 180 legs, + 1 ifc primary leg + 3 guard legs (2 epochs) = 184 legs, most at N ~ 240-320. B2 (state/timing_ledger.json, job 66181609) ran 44 trainings + 22 ifc LOO legs + guard in 17.25 min on h200, so project 60-110 min; request `--time 03:30:00`. Strict 1 seed: only `submit.sh` is needed; no `submit_seeds_2_3.sh` leg. proj_knn/proj_ridge are closed-form/numpy - no new dependencies, no GPU beyond the teacher legs."
}
```

- **Expected outcome** (skill units; ledger columns in B2's inner-skill convention =
  OOF-train-row nRMSE divided by the frozen test copy-LF denominator; own-stream anchor =
  `certified_3seed_panel_geomean` **19.817845**, panel `min_claimable_effect` **1.141867**):
  - **Primary `T0_cond_only` on `test_hf`**: panel geomean **19.3-20.5**, i.e. within the
    panel MCE 1.141867 of the 19.817845 anchor (B2's per-seed values were 19.2799 / 20.2928 /
    20.0760) - a 1-seed reproduction of B2's instrument, not a claim.
  - **`advantage_total = skill(T0) - skill(I1)`**: 30-40 (pfc), 100-125 (allen_cahn),
    9-12 (fisher_kpp), 10-13 (cahn_hilliard), 3-5 (helmholtz, report-only) - all far above
    their operative thresholds (0.28373 / 0.91915 / 0.00071 / 0.18475 / 2.95299).
  - **`advantage_reachable = skill(T0) - skill(proj_best)`**: pre-registered **within the
    operative threshold** (i.e. no reachable component) on pfc (< 0.28373), allen_cahn
    (< 0.91915) and fisher_kpp (< 0.00071), because the teacher is a near-copy of HF there
    (cos >= 0.997) so its condition-projection is the same conditional mean `T0` already fits;
    **predicted to EXCEED its threshold on cahn_hilliard** (> 0.18475, magnitude 0.2-2.0), the
    panel's one support-limited dataset whose 16 `ic_c*` condition dims put the realised IC in
    the condition (B2 T3-F3). `reachable_fraction` < 0.02 on the three information-limited
    datasets, 0.02-0.20 on cahn_hilliard.
  - **`proj_nn` vs `T0` on `test_hf`, 5 in-job paired fold deltas**: |delta| within the
    operative threshold on the 4 sharp datasets (i.e. distillation from an LF-consuming teacher
    buys nothing on the scored split); sign unknown a priori, magnitude expected < 0.5x the
    threshold on pfc/allen_cahn/fisher_kpp.
  - **helmholtz (report-only)**: `advantage_reachable` 0-3 raw, reported beside its
    energy-pooled twin; no adjudication either way (B2 T2-F5).
  - **Instrument checks**: `I1` OOF skill within 2x of B2's inner-fold I1 (0.384 / 5.653 /
    0.838 / 0.294 / 2.756); inner-teacher OOF nRMSE within 1.5x of the outer teacher's.
  - **vs the noise floor**: every adjudicating threshold is
    `max(certified MCE, B2 fold-fixed spread, in-job fold spread)` and therefore >= the
    certified per-dataset floor by construction - fisher_kpp 0.0007136812826775696, pfc
    0.21302734961699343, allen_cahn 0.8797047190126648, cahn_hilliard 0.09124535322300886
    (raised to 0.1847460640603149 by B2's spread), helmholtz 2.95299157437233 (report-only).
  - **Honest read**: on the four sharp datasets a near-zero reachable component is *partly
    arithmetic* (teacher ~ HF), which is exactly why it is pre-registered from the
    training-free cos/rel-L2 numbers rather than sold as a discovery. The card's genuinely
    open content is (a) whether cahn_hilliard breaks the null - a second, independent test of
    B2's support-vs-information rule candidate; (b) the test-split distillation contrast, which
    is not implied by any arithmetic; (c) helmholtz's report-only column, the one dataset where
    the teacher is not a smoothed copy of HF. Either outcome closes the round's value-of-LF
    ledger with a publishable sentence.

- **Expected falsification**: the card's hypothesis - *"on the aligned panel the LF teacher's
  advantage over a condition-only student is realisation information that is not a function of
  the condition, so no training-only channel (distillation included) can carry it, EXCEPT on
  the support-limited cahn_hilliard whose condition carries the IC coefficients"* - is falsified
  if ANY of: **(F1, null breach)** `advantage_reachable` exceeds its operative threshold on
  >= 2 of {pfc 0.21302734961699343 -> 0.28372761657901435, allen_cahn 0.8797047190126648 ->
  0.9191521219144931, fisher_kpp 0.0007136812826775696}; **(F2, test-split distillation)**
  `proj_nn` beats `T0` on `test_hf` by more than the operative threshold, with consistent sign
  over the 5 in-job paired fold deltas, on >= 2 of the 4 sharp datasets; **(F3, the exception)**
  cahn_hilliard's `advantage_reachable` fails to exceed its operative threshold
  0.1847460640603149 (the card's risky structural prediction from B2's support-vs-information
  taxonomy dies, and the round-level rule candidate is not reproduced); or **(F4, instrument)**
  the three projection estimators disagree by more than the operative threshold on >= 3 of the
  4 sharp datasets, or `advantage_total` falls below the operative threshold on >= 2 of them
  (B2 measured 10.5-114.5 skill units of teacher advantage, so there would be nothing to
  decompose and no ledger statement would be licensed).
  *Attached reasoning*: the mandatory floor arms (`nn_condition` / `train_mean` / `zero` from
  `state/anchors/floors.json`) are reported as `ref_*` splits beside the primary arm on every
  dataset and are the standing "has this learned anything" comparison (2.2) - helmholtz's zero
  column 3.3441 stays visible under the report-only discipline (B2's T0 scored 6.8778 there,
  i.e. worse than the zero field), pfc's best floor is train_mean 59.8118 and allen_cahn's is
  nn_condition 269.1959; a ledger effect on a dataset where the primary arm does not beat its
  best floor is reported but not claimed. Deterministic pointwise scoring of the ADR r2-0003
  stochastic datasets measures a conditional mean (TRIE, https://arxiv.org/html/2607.00196).

- **Prior-art verdict quoted**: row **D1** of
  `websearches/r2s4_diag/batch_3/report.md`, verdict `preempted-but-MF-composition-open (cite)`,
  open column verbatim: *"Splitting privileged advantage into reachable/unreachable is published
  - but **no fetched source fits a map from student-observable inputs to the teacher's own
  predictions and scores that projection in the task metric** (AR-OPD: "No explicit function is
  fit"; CCH is representation-level for classification labels; ViCuR is a design principle).
  Nothing for a **field-valued** output in **copy-LF skill** units with a **coarse PDE solve** as
  the privileged channel and a **realized random IC** as the unobservable component; nothing
  pre-registers the outcome from an independently measured training-free barrier."*
  Citations for the card's `prior_art` block (fetched in that loop unless marked):
  https://arxiv.org/html/2606.10385v1 (AR-OPD), https://arxiv.org/html/2606.30626v1 (DOPD,
  batch 2, still binding), https://arxiv.org/html/2505.09546 (realizability / surjective
  f(s~)=s), https://arxiv.org/abs/2606.05718 (ViCuR), https://arxiv.org/abs/2602.04942 (+
  /html/2602.04942v1, pi-Distill/OPSD), https://arxiv.org/html/2510.13182 (CCH),
  https://arxiv.org/html/2607.00196 (TRIE), https://arxiv.org/abs/2410.23440 (no defensible
  claim at N_hf = 5), https://www.sciencedirect.com/science/article/abs/pii/S0952197625034293
  (**search-result confidence only, fetch 403**). Do-not-cite lists from batches 1-3 observed;
  nothing from `_untrusted_prior_attempt/` is used.

- **Immutables self-check**: **pass (11/11)**
  1. *Data read-only* - no generation, no extra HF; the 400 aligned train rows are re-partitioned
     into folds only, ifc_poisson's N_hf stays 5, LF is the stored `max_lf_fid` coarse solve
     upsampled by the frozen ADR r2-0001 convention (never downsampled HF), and the family opens
     dataset files read-only through `data_adapters/loaders.py`.
  2. *Panel + guard fixed* - `datasets: "panel"` (all 6 scored for the primary arm) and the guard
     leg runs exactly `heat_local, fluid, sharp__sod_1d` at 2 epochs; the ledger's restriction to
     5 datasets is a reporting scope, not a panel change, and ifc_poisson still appears with its
     primary column and floor arms.
  3. *Eval layer / spec untouched* - the card needs no edit to `round2/eval/`, `project.yaml`,
     `program.md` or any agent prompt; `eval/panel_data.py::copylf_prediction` and
     `eval/nrmse.py` are **called**, and `lf_reference.py` is a vendored copy asserted equal to
     the original (max_abs_diff == 0.0) rather than a modification.
  4. *One nRMSE definition* - every scored number flows through `eval/nrmse.py`; the training
     loss is free (MSE in z-scored space) and the helmholtz energy-pooled twin is an explicitly
     labelled interpretive column that scores nothing and replaces no metric.
  5. *Contract CLI fixed* - `smoke_eval.py` keeps the six-arg signature
     (`--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed`); all 45 knobs above are
     `R2S4B3_*` environment variables listed in `recipe.env` and echoed into the result JSON.
  6. *Seeds / tier* - `seeds: [0]` (strict 1-seed, project.yaml `seed_protocol.seeds`) and
     `epochs: 200` (smoke) with the guard leg at the contract tier 2; no full tier, no seeds
     1-2, no 12.4 certification exception requested.
  7. *Guarded factory surfaces untouched* - all new code is under
     `<worktree>/models_r2/r2s4_b3_projection/` and `<worktree>/probes/`; nothing under
     `mf_field/factory_mffp/{eval,baselines,references,scripts,data}`, `factory.md` or `akash/`
     is written.
  8. *Checkpoint-resume* - implementable and specified: B2's exact pattern, a single
     `<ckpt_dir>/last.pt` carrying completed-leg results plus the in-flight leg's
     model/opt/sched/RNG state, so a restarted job replays finished legs and resumes the
     in-flight one at its stored epoch (B2's `smoke_eval.py` lines 675-726 are the reference
     implementation to re-derive).
  9. *Threshold exceeds the noise floor* - every adjudicating threshold is
     `max(certified MCE, B2 fold-fixed T0 spread, in-job 5-fold paired spread)`, hence >= the
     certified floor by construction: F1 cites pfc 0.21302734961699343 (used at 0.28372761657901435),
     allen_cahn 0.8797047190126648 (used at 0.9191521219144931), fisher_kpp 0.0007136812826775696;
     F3 cites cahn_hilliard 0.09124535322300886 (used at 0.1847460640603149); helmholtz
     2.95299157437233 adjudicates nothing (report-only). Panel MCE 1.1418668211296108 is quoted
     for the primary-arm reproduction check.
  10. *Not a pre-falsified lever* - the nearest pre-falsified item is r2s4-B2's own auxiliary-LF-
     target head (target-side channel, closed 15/15) and r2s3-B1's LF-rung supervision (cratered).
     This card touches neither: it does not add an LF term to the student's loss and does not
     train on LF rungs; it fits a *post-hoc out-of-fold regression of a frozen teacher's
     predictions onto the condition* and measures the split. The WNO swap, LF low-mode freezing
     and diffusion-prior levers (program.md 5 / r1 5) are untouched.
  11. *Floor arms* - formally n/a (this is a `diagnostic` card, and 2.2 makes the arms mandatory
     on **model** cards), but they are included anyway following B1/B2: `ref_nn_condition`,
     `ref_train_mean` and `ref_zero` from `state/anchors/floors.json` are reported beside the
     primary arm on every panel dataset through the same nRMSE path, with a reproduce-frozen
     check, and they are named explicitly in the `expected_falsification` attached reasoning.

- **Anchor reference**: `null` (program.md 4.5 / the round-2 policy: null for all four round-2
  streams; the own-stream anchor `certified_3seed_panel_geomean` 19.817845 is implicit).

- **Source iteration**: [iteration_1.md](iteration_1.md)

## Reopen candidates

| Candidate | Verdict (retry/drop) | Eased conditions | Source iteration |
|---|---|---|---|
| _none_ — all 8 round-2 cards carry `reopen_candidate: false` (verified by reading every `experiment_cards/*/batch_*/B*.json`) | n/a | n/a | [iteration_1.md](iteration_1.md) |

## Skipped slot

Not applicable — the slot is filled.

## Summary table

| Slot | Category | One-liner | Status |
|---|---|---|---|
| 1 | diagnostic / teacher-projection channel ledger | Fit an out-of-fold condition -> LF-teacher-prediction map on held-out TRAIN rows (5 outer folds x 4 inner cross-fit folds, three projection estimators incl. a same-budget distillation student) and score the projection in copy-LF skill to split the teacher's advantage into reachable vs unreachable; nulls pre-registered from a training-free cos/rel-L2 barrier; cahn_hilliard predicted to be the one dataset with a reachable component; `proj_nn` also scored on `test_hf` for a 5-fold paired distillation contrast at 1 seed | filled |
