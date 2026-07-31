# Brainstormer Report — Stream `r2s3_lf_train_signal`, Batch 2

**Stream**: `r2s3_lf_train_signal` (lever) · **Batch**: 2 ·
**Total iterations**: 1 · **Slot filled**: 1/1 ·
**Reopen candidates resolved**: 0 (none exist)

## Slot

- **Category**: `lf_train_signal / matched budget-equal ±LF at N_hf≈5 with
  LF-at-uncovered-conditions (coverage vs curriculum), repaired-instrument
  neural channel`

- **Card type**: `model`

- **Motivation**: the batch-2 prior-art verdict leaves exactly one `novel`
  row, and it is this card's deliverable (verbatim from
  `websearches/r2s3_lf_train_signal/batch_2/report.md` "## Prior-art verdict"):

  > **E5** — the **measurement**: matched, budget-equal with/without-LF-training
  > contrast for a **neural condition→field** surrogate at N_hf ≈ 5 (and N = 400
  > with condition-aligned rungs), per dataset, against a certified 3-seed noise
  > floor | **novel** (nearest neighbours named) | Nearest:
  > https://arxiv.org/pdf/2508.08517 (HF-only vs MF comparison — but linear POD
  > regression, no neural arm, no seed-noise floor); https://arxiv.org/abs/2403.08118
  > (harmful-source characterisation, not a matched training ablation) |
  > Everything: three independent search framings (batch 1 iter 3; batch 2 iters
  > 4 and 5) failed to retrieve a matched-architecture with/without-LF accounting
  > for neural field surrogates at this sample count. This is round-2 success
  > criterion 1 and the stream's remaining publishable content.

  The composition surface it is instantiated on, same table:

  > **E2** — LF rows at **disjoint** conditions supply the null direction of the
  > 5×6 HF design (rank completion at N_hf = 5) | **preempted-but-MF-composition-open**
  > | https://arxiv.org/html/2510.15337 …; https://arxiv.org/pdf/2508.08517 ("LF
  > data can be evaluated at parameter values where no HF data exists"; HF-only
  > baseline; LF can degrade); https://arxiv.org/abs/2511.20183 | The
  > **field-valued, neural, certified-floor** instance: null direction of a
  > *condition* design matrix filled by **coarse consistent PDE solves**, priced
  > in skill units against a 3-seed `min_claimable_effect`, on a panel where 5/6
  > datasets have **condition-aligned** rungs. **Supersedes batch 1's `novel`
  > verdict for D3.**

  And the two rows carried as declared, cited engineering rather than claims:

  > **E1** — ship the linear/affine LF channel … | **preempted** |
  > https://arxiv.org/abs/1705.02956 …; https://arxiv.org/pdf/2508.08517 … |
  > Nothing at the mechanism level. … Ship it as a **cited baseline**, never as
  > a contribution.
  > **E3b** — mode clipping pinned at the HF Nyquist for every rung |
  > **preempted** | https://arxiv.org/html/2310.00120 ("the first α modes in
  > each direction, where α is independent of the discretization") | Nothing.
  > This is the standard convention; B1 deviated from it. Bug fix.
  > **E4** — training-free per-dataset gate … | **preempted** |
  > https://arxiv.org/abs/2403.08118 … | Mandatory engineering; not a claim.

  Within-stream driver: `r2s3_lf_train_signal-B1` (complete, cratered) measured
  both endpoints on ifc_poisson and ran neither of the resulting experiments —
  information value of the disjoint LF rows **+3.2317** skill units (linear
  estimator reaching 0.2427) against a delivered **−7.3497** through the
  network — with three separately priced defects (shared scaler → 1772× HF-loss
  deflation; unsupervised `|k|>4` band; null-direction gain 2.653× too large,
  vs the no-LF control's 27.7% anti-aligned law energy at cos −0.9919). Its
  part 7 asks for exactly the repaired three-arm run this card ships, and its
  reviewer confounds C1 (arms not normalization-matched) and C2 (epoch- not
  step-matched) are closed by construction here. Turf: the sibling measurement
  `r2s4_diag-B2` owns the **accounting** (T0-vs-T1 aux head, full N, LF paired
  to the fit rows, `N_FIT_LEVELS=20,80`); this card owns **optimizing** the LF
  training signal at N_hf≈5 with LF at conditions where no HF exists, and does
  not duplicate r2s4-B2's full-N panel contrast. B1's architecture-tax
  observation is carried as a *cited* theory context
  (https://arxiv.org/pdf/2209.15265, search-returned only) and as a *measured*
  violation of the min-norm implicit-bias prediction
  (https://arxiv.org/pdf/2006.07356, fetched), never as a claim of novelty.

- **Concrete config**: new from-scratch family `models_r2/r2s3_null_supply`
  (worktree `worktrees/r2s3_lf_train_signal/B2`), condition-only at test,
  stripped view only, no LF tensor constructed on any test path.
  - `NullSupplyDecoder(cond_dim, width=64, blocks=4)`,
    `forward(cond, out_hw) -> (B,H,W)`; coord channels at forward time; lift
    2→64; 4× [SpectralConv2d(α) + 1×1 conv + FiLM(cond) after GroupNorm +
    GELU]; projection 64→128→1; FFT `norm="forward"`.
  - **Mode policy `pinned_min_rung_nyquist`** (E3b bug fix, MG-TFNO):
    `α = min(12, min over ALL train rungs of floor(N_rung/2))`, computed once
    per dataset and identical in every arm → ifc_poisson α = 4 (rungs
    8/16/32/64), cahn_hilliard and fisher_kpp α = 12 (rungs 64/128/256). No
    mode weight is ever supervised by the 5 HF rows alone.
  - **Per-rung scaler** `s_f = max|y|` on rung `f`'s own train fields (E3a,
    declared as an amplitude-convention fix, not a claim); the HF scaler is
    therefore identical across arms (closes B1's C1).
  - **Step-matched budget** (closes B1's C2): `steps = --epochs × 25`
    (200 → 5000; contract 2 → 50); every arm takes the same steps, sees all 5
    HF rows every step, same AdamW(1e-3, wd 1e-5) + cosine + clip 1.0. LF arms
    additionally draw one 16-row LF minibatch per step (rungs cycled
    deterministically).
  - **Loss** `MSE_HF + 1.0·MSE_LF + 1.0·NullPenalty` in per-rung-scaled units.
    `NullPenalty` = paired-difference penalty along the HF design's null
    directions: sample `c` from the train conditions, `v ∈ null([X_hf,1])`,
    `t ~ U(−1,1)` (standardized units), penalize
    `‖[S(c+tv) − S(c)] − t·(vᵀΘ_LF)‖²`, where `Θ_LF` is a ridge-affine law on
    the LF rung selected by that rung's own in-rung LOO, lifted to the HF grid
    with the ADR r2-0001 convention (imported read-only / vendored with a 1e-9
    train-split agreement assert). `m = dim null = 0` ⇒ penalty ≡ 0 by
    construction.
  - **N_hf = 5 protocol**: native on ifc_poisson; on the two aligned datasets
    5 of the existing 400 train HF rows are drawn by `R2S3B2_SPLIT_SEED` while
    the LF rungs keep all 400 conditions (LF at 395 conditions with no HF row).
    Training-free null deficit at N_hf = 5: `m` = 1 (ifc, d=5), **15**
    (cahn_hilliard, d=19), **0** (fisher_kpp, d=2).
  - **Arms** (each with its own `ROUND2_EVAL_RESULTS` dir ⇒ own `ckpt_dir`
    and cache key):

    | arm | LF pool | null penalty | dataset(split seeds) |
    |---|---|---|---|
    | `A0_nolf` | — | off | ifc(native), ch(0,1,2), fk(0,1) |
    | `A1_lf_cov` | all rungs, all conditions | off | ifc(native), ch(0) |
    | `A2_lf_cov_null` **PRIMARY** | all rungs, all conditions | on | ifc(native), ch(0,1,2), fk(0,1) |
    | `A3_lf_paired` | LF at the 5 HF conditions only | vacuous | ch(0) |
    | `A5_lf_norepair` | all rungs (B1 config: shared `max|y|`, unpinned modes) | off | ifc(native) |

    On fisher_kpp `m = 0` ⇒ `A2 ≡ A1`; only `A2` is run and the identity is
    recorded.
  - **Non-trained reference splits** (never named `test*`): `ref_linear_mf`
    (the preempted channel `c·A(cond)+R(cond)`, rung by in-rung LOO, `c` and
    residual ridge on the 5 HF rows, α by exact LOO), `ref_linear_hfonly`
    (min-norm affine = the information limit), and the floor arms `ref_zero`,
    `ref_train_mean_n5`, `ref_nn_condition_n5` (in-regime) plus
    `ref_train_mean_full` / `ref_nn_condition_full` seam-checked to
    `state/anchors/floors.json` at 1e-9, RAISING on mismatch.
  - **Reported gate/instrument block** (E4 — reported, never a switch):
    per-rung affine-LOO residual, `m`, singular values of `[X_hf,1]`,
    null-direction energy fraction, LF→null recovery cosine/gain, per-arm
    train-vs-test gap, and predictions dumped at the HF **train** conditions
    (B1 part 7 item (4)).
  - **Declared baseline** (§12.3): `mf_fno_transfer_film`, **cited** from B1's
    on-disk gate run — ifc_poisson, 200 epochs, seed 0, nRMSE **0.055637**,
    skill **1.5455**, `nrmse_def_hash d3d0ade9… / copylf_def_hash 9753ff24…`
    (`…/round2/r2s3_lf_train_signal/B1/eval/result_ifc_poisson_baseline_mf_fno_transfer_film_s0.json`);
    ifc_poisson's native N_hf is 5, so it is exactly regime-matched. Stated
    differences: joint step-matched training with per-rung scalers, pinned
    modes and a null-direction penalty vs sequential LF-pretrain→HF-finetune
    with no null-space machinery. Not re-run, not edited.
  - **Guard leg**: `A2` on `--datasets guard`, contract tier (2 epochs), native
    N_hf (`R2S3B2_GUARD_NSUB=off`).

- **Recipe**:

```json
{
  "base_family": "none (new from-scratch family; NOT vendored from mf_fno_transfer_film, mf_fno_ladder* or models_r2/r2s3_rung_supervised — see iteration_1.md 'Alternatives weighed and rejected' and the five-axis differentiator list in immutables item 10)",
  "base_commit": "9e10d414e35a96398f7b091bc84ddf936d88acc7",
  "family_dir": "models_r2/r2s3_null_supply",
  "datasets": "ifc_poisson,sharp__cahn_hilliard,sharp__fisher_kpp_2d",
  "epochs": 200,
  "seeds": [0],
  "env": {
    "R2S3B2_ARM": "A2_lf_cov_null",
    "R2S3B2_SPLIT_SEED": "0",
    "R2S3B2_N_HF": "5",
    "R2S3B2_WIDTH": "64",
    "R2S3B2_BLOCKS": "4",
    "R2S3B2_MODES_CAP": "12",
    "R2S3B2_MODE_POLICY": "pinned_min_rung_nyquist",
    "R2S3B2_SCALER": "per_rung_max",
    "R2S3B2_STEPS_PER_EPOCH": "25",
    "R2S3B2_HF_BATCH": "5",
    "R2S3B2_LF_BATCH": "16",
    "R2S3B2_LR": "1e-3",
    "R2S3B2_WD": "1e-5",
    "R2S3B2_SCHED": "cosine",
    "R2S3B2_CLIP": "1.0",
    "R2S3B2_LAMBDA_LF": "1.0",
    "R2S3B2_LAMBDA_NULL": "1.0",
    "R2S3B2_NULL_BATCH": "8",
    "R2S3B2_NULL_T": "1.0",
    "R2S3B2_NULL_RUNG_SELECT": "in_rung_loo",
    "R2S3B2_LF_LIFT": "match_copylf_convention",
    "R2S3B2_RANK_TOL": "1e-10",
    "R2S3B2_REF_ARMS": "linear_mf,linear_hfonly,nn_condition_n5,train_mean_n5,zero,nn_condition_full,train_mean_full",
    "R2S3B2_FLOORS_JSON": "mffp_autoresearch/round2/state/anchors/floors.json",
    "R2S3B2_FLOOR_TOL": "1e-9",
    "R2S3B2_NOISE_FLOOR_JSON": "mffp_autoresearch/round2/state/noise_floor.json",
    "R2S3B2_GATE_REPORT": "1",
    "R2S3B2_DUMP_TRAIN_PREDS": "1",
    "R2S3B2_CKPT_EVERY_STEPS": "250",
    "R2S3B2_GUARD_NSUB": "off",
    "_note": "keys prefixed _ are card directives, NOT passed to --env. The --env set for the PRIMARY leg is exactly the 25 R2S3B2_* keys above; each additional leg overrides only R2S3B2_ARM and R2S3B2_SPLIT_SEED (and, for A5_lf_norepair, R2S3B2_SCALER=shared_max_all_rungs + R2S3B2_MODE_POLICY=grid_nyquist_clip).",
    "_primary_arm": "A2_lf_cov_null",
    "_legs": [
      {"tag": "ifc_A0", "datasets": "ifc_poisson", "R2S3B2_ARM": "A0_nolf", "R2S3B2_SPLIT_SEED": "native"},
      {"tag": "ifc_A1", "datasets": "ifc_poisson", "R2S3B2_ARM": "A1_lf_cov", "R2S3B2_SPLIT_SEED": "native"},
      {"tag": "ifc_A2", "datasets": "ifc_poisson", "R2S3B2_ARM": "A2_lf_cov_null", "R2S3B2_SPLIT_SEED": "native"},
      {"tag": "ifc_A5", "datasets": "ifc_poisson", "R2S3B2_ARM": "A5_lf_norepair", "R2S3B2_SPLIT_SEED": "native", "R2S3B2_SCALER": "shared_max_all_rungs", "R2S3B2_MODE_POLICY": "grid_nyquist_clip"},
      {"tag": "ch_A0_s0", "datasets": "sharp__cahn_hilliard", "R2S3B2_ARM": "A0_nolf", "R2S3B2_SPLIT_SEED": "0"},
      {"tag": "ch_A0_s1", "datasets": "sharp__cahn_hilliard", "R2S3B2_ARM": "A0_nolf", "R2S3B2_SPLIT_SEED": "1"},
      {"tag": "ch_A0_s2", "datasets": "sharp__cahn_hilliard", "R2S3B2_ARM": "A0_nolf", "R2S3B2_SPLIT_SEED": "2"},
      {"tag": "ch_A2_s0", "datasets": "sharp__cahn_hilliard", "R2S3B2_ARM": "A2_lf_cov_null", "R2S3B2_SPLIT_SEED": "0"},
      {"tag": "ch_A2_s1", "datasets": "sharp__cahn_hilliard", "R2S3B2_ARM": "A2_lf_cov_null", "R2S3B2_SPLIT_SEED": "1"},
      {"tag": "ch_A2_s2", "datasets": "sharp__cahn_hilliard", "R2S3B2_ARM": "A2_lf_cov_null", "R2S3B2_SPLIT_SEED": "2"},
      {"tag": "ch_A1_s0", "datasets": "sharp__cahn_hilliard", "R2S3B2_ARM": "A1_lf_cov", "R2S3B2_SPLIT_SEED": "0"},
      {"tag": "ch_A3_s0", "datasets": "sharp__cahn_hilliard", "R2S3B2_ARM": "A3_lf_paired", "R2S3B2_SPLIT_SEED": "0"},
      {"tag": "fk_A0_s0", "datasets": "sharp__fisher_kpp_2d", "R2S3B2_ARM": "A0_nolf", "R2S3B2_SPLIT_SEED": "0"},
      {"tag": "fk_A0_s1", "datasets": "sharp__fisher_kpp_2d", "R2S3B2_ARM": "A0_nolf", "R2S3B2_SPLIT_SEED": "1"},
      {"tag": "fk_A2_s0", "datasets": "sharp__fisher_kpp_2d", "R2S3B2_ARM": "A2_lf_cov_null", "R2S3B2_SPLIT_SEED": "0"},
      {"tag": "fk_A2_s1", "datasets": "sharp__fisher_kpp_2d", "R2S3B2_ARM": "A2_lf_cov_null", "R2S3B2_SPLIT_SEED": "1"},
      {"tag": "guard_A2", "datasets": "guard", "epochs": 2, "R2S3B2_ARM": "A2_lf_cov_null", "R2S3B2_SPLIT_SEED": "0", "R2S3B2_GUARD_NSUB": "off"}
    ],
    "_sweep": "ONE SLURM job per seed runs the 17 legs serially. For each leg: export ROUND2_EVAL_RESULTS=<OUT_DIR>/eval/results_<tag> (so out_json and ckpt_dir cannot collide across legs), then call score_panel.py --family_dir <worktree>/models_r2/r2s3_null_supply --datasets <leg datasets> --epochs <200|2> --seed $SEED --env R2S3B2_ARM=<...> --env R2S3B2_SPLIT_SEED=<...> --env <the remaining 23 keys verbatim> --out <OUT_DIR>/eval/result_<datasets>_<tag>_s${SEED}.json. score_panel caches per (family,dataset,epochs,seed,code_hash incl. env), so resubmission after preemption skips finished legs — the script is idempotent.",
    "_declared_baseline": {
      "family": "mf_fno_transfer_film",
      "role": "program.md §12.3 mandatory declared baseline (LF-pretrain -> HF-finetune from the condition vector); CITED, not re-run, per the websearcher's instruction 1 and because ifc_poisson's native N_hf=5 makes B1's existing gate run exactly regime-matched",
      "cited_numbers_source": "mffp_autoresearch_outputs/round2/r2s3_lf_train_signal/B1/eval/result_ifc_poisson_baseline_mf_fno_transfer_film_s0.json (200 epochs, seed 0, round-2 eval layer)",
      "cited_values": {"ifc_poisson_nRMSE": 0.055637439592454, "ifc_poisson_skill": 1.5454844331237223, "nrmse_def_hash": "d3d0ade9191c13bacc40702f3eb26ad290e01641cacee22a1d2233b74c035850", "copylf_def_hash": "9753ff24e856f595748492dec6cb6c215d748f97e8ec4a679b651f8846da907a"},
      "differences_from_this_family": "joint step-matched HF+LF training with per-rung scalers, HF-Nyquist-pinned mode set, and a null-direction paired-difference penalty at N_hf=5; transfer_film is sequential LF-pretrain->HF-finetune with one scaler, grid-clipped modes and no null-space machinery"
    },
    "_reference_arms_prior_art": {
      "ref_linear_mf": "the PREEMPTED linear/affine MF channel, shipped as a cited baseline only: https://arxiv.org/abs/1705.02956 (LR-MFS), https://arxiv.org/pdf/2508.08517 (projection-based MF linear regression for data-scarce applications). B1's measured value on ifc_poisson: skill 0.2427.",
      "ref_linear_hfonly": "min-norm affine on the 5 HF rows = the HF-only information limit; B1 measured 3.4744 on ifc_poisson."
    },
    "_guard_leg": "primary arm only: score_panel.py --datasets guard --epochs 2 --seed 0 (contract tier, program.md §2.3), native N_hf",
    "_slurm": {
      "gres": "gpu:nvidia_h200:1",
      "partition": "gpu",
      "time": "03:00:00",
      "budget_note": "state/timing_ledger.json: r2s3_rung_supervised ran 5 legs over the 6-dataset panel in 77.05 min on h200 at 200 epochs with 400-row HF epochs. Here every HF stage sees 5 rows and the LF stages run at 64^2/128^2 (cahn_hilliard, fisher_kpp) or 8^2/16^2/32^2 (ifc), so the 17 legs are estimated at 60-110 min total; 03:00:00 leaves margin for h200 contention."
    }
  }
}
```

- **Expected outcome** (skill units, corrected denominators, seed 0,
  `provisional-single-seed`):

  | quantity | prediction | vs floor / anchor |
  |---|---|---|
  | ifc `A0_nolf` | 8–12 (best est. 9.5) | B1's `hf_only` 9.4466; NN floor 10.054891 |
  | ifc `A2_lf_cov_null` (PRIMARY) | **2–8** (best est. 5) | information limit 3.4744; declared baseline 1.5455; preempted linear channel 0.2427 |
  | **ifc value-of-LF `A0 − A2`** | **+2 to +7** (best est. +4.5) | certified mce **0.9377041** → **2.1–7.5× the floor**; B1 measured **−7.3497** |
  | ifc `A5_lf_norepair − A2` | +5 to +12 | prices the repair trio in-job vs 0.9377041 |
  | cahn_hilliard `A0` (mean of 3 draws, N_hf=5) | 25–45 | frozen 400-row NN floor 23.180342; in-regime N=5 floors reported beside it |
  | cahn_hilliard `A0 − A2` | **+1 to +8** | vs `max(0.0912454, in-job paired spread over 3 draws)` → ≥ 11× the floor |
  | cahn_hilliard `A3_lf_paired − A2` | +0.5 to +5 | coverage beyond curriculum, same threshold |
  | fisher_kpp `A0 − A2` (mean of 2 draws) | −0.5 to +0.5 | predicted **null**; must sit below cahn_hilliard's effect (raw effect also reported vs `max(0.0007137, in-job spread)`) |
  | panel geomean | **not computed** | 3 of 6 panel datasets scored; no criterion-2 panel claim; stream anchor 23.063617 quoted for context only |

  Why the ifc sign should flip: the null direction carries 18.83% of the law's
  coefficient energy and the LF rungs recover it at 0.940/0.982/0.996 (B1 turn
  2 B7); per-rung scaling removes the 1772× HF-loss deflation B1's part 6
  blames for the row-space damage (0.921 vs the control's 0.604); pinned modes
  remove the `|k|>4` band that only 5 deflated rows supervised (+1.605 post
  hoc); the null penalty caps the 2.653× gain error. The card does **not**
  predict beating the declared baseline (1.5455) or the preempted linear
  channel (0.2427) — the deliverable is the certified measurement, not a
  champion. Standing caveat carried: ifc_poisson is an exactly affine benchmark
  (affine-LOO 3.2e-08), so any bar-level number there is **rank recovery, not
  operator learning** (B1 part 6 M11). helmholtz and pfc are not scored, so
  their standing caveats do not arise on this card.

- **Expected falsification**: **F1 (primary)** — falsified if on `ifc_poisson`
  `A2_lf_cov_null` fails to beat the matched, step-matched, normalization-matched
  `A0_nolf` control by more than the certified **0.9377041** skill units;
  **F2 (instrument)** — falsified if `A2` fails to beat the in-job
  `A5_lf_norepair` (B1's configuration) on `ifc_poisson` by more than
  0.9377041; **F3 (coverage vs curriculum)** — falsified if on
  `sharp__cahn_hilliard` (`m = 15`) `A2` fails to beat `A3_lf_paired` by more
  than `max(0.0912454, in-job paired spread over the 3 draws)`;
  **F4 (structural ordering)** — falsified if the mean LF effect `A0 − A2` on
  `sharp__fisher_kpp_2d` (`m = 0`) exceeds that on `sharp__cahn_hilliard`
  (`m = 15`) by more than the same operative threshold; **F5 (has it learned
  anything)** — falsified if on `ifc_poisson` `A2` does not beat the best
  in-regime floor **10.054891** (`nn_condition` on the same 5 rows;
  `train_mean` 11.206332 and `zero` 27.777778 reported beside it), or if `A2`
  fails to beat its own in-regime N=5 best floor on both sharp datasets.

- **Prior-art verdict quoted**: see **Motivation** above — the `novel` E5 row,
  the `preempted-but-MF-composition-open` E2 row, and the `preempted` E1 / E3b
  / E4 rows, quoted verbatim with their citations
  (https://arxiv.org/pdf/2508.08517, https://arxiv.org/abs/2403.08118,
  https://arxiv.org/html/2510.15337, https://arxiv.org/abs/2511.20183,
  https://arxiv.org/abs/1705.02956, https://arxiv.org/html/2310.00120,
  https://arxiv.org/html/2510.01608, https://arxiv.org/pdf/2006.07356,
  https://arxiv.org/pdf/2209.15265 — the last **search-returned only**, cited
  as such).

- **Immutables self-check**: **pass (11/11)** — positive evidence per item in
  [iteration_1.md](iteration_1.md) "Immutables self-check". Key items: (1) data
  read-only, the N_hf=5 legs *select* 5 of the existing 400 train HF rows
  (training-procedure freedom, r1 §5; precedent `r2s4_diag-B2`
  `R2S4B2_N_FIT_LEVELS=20,80`), no HF added, LF never downsampled HF; (3) all
  code under `<worktree>/models_r2/r2s3_null_supply/**`, eval layer imported
  read-only; (6) `seeds: [0]`, epochs 200 / guard 2 — the subsample draws are
  **split** seeds in the env, not training seeds; (9) thresholds are exactly
  the certified constants (ifc 0.9377041) or `max(certified, in-job spread)`
  (cahn_hilliard 0.0912454, fisher_kpp 0.0007137); (10) nearest pre-falsified
  lever is LF low-mode **freezing** — nothing is frozen here and no LF field
  enters the forward path; (11) `ref_zero` / `ref_train_mean_n5` /
  `ref_nn_condition_n5` plus the 1e-9 seam-checked frozen floors are reported
  beside every arm and F5 is written against them.

- **Anchor reference**: `null` (program.md §4.5 — all four round-2 streams are
  gap/lever/diag; own-stream anchor 23.063617 implicit; a 3-dataset subset is
  scored, so no panel-geomean claim is made).

- **Source iteration**: [iteration_1.md](iteration_1.md)

## Reopen candidates

| Candidate | Verdict (retry/drop) | Eased conditions | Source iteration |
|---|---|---|---|
| _none_ — all six round-2 cards carry `reopen_candidate: false` (verified by reading every `experiment_cards/*/*/B*.json`) | n/a | n/a | [iteration_1.md](iteration_1.md) |

## Skipped slot

Not applicable — the slot is filled.

## Summary table

| Slot | Category | One-liner | Status |
|---|---|---|---|
| 1 | `lf_train_signal / matched budget-equal ±LF at N_hf≈5 with LF-at-uncovered-conditions` | New from-scratch `r2s3_null_supply` FiLM-FNO decoder with per-rung scalers, HF-Nyquist-pinned modes and a null-direction paired-difference penalty; step-matched ±LF arms at N_hf=5 on ifc_poisson (m=1), cahn_hilliard (m=15) and fisher_kpp (m=0), with a coverage-vs-curriculum control and the preempted linear channel + floors as declared reference arms | filled |
