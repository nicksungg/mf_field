# Iteration 1 — Stream `r2s3_lf_train_signal`, Batch 2

## Design context considered

- `summary_so_far.md` §6 (unknowns 1–7), especially: the repaired network was
  never run (U1); the N_hf≈5-with-full-LF-coverage regime has never been
  constructed on the aligned datasets (U2); coverage vs curriculum was never
  separated (U3); the training-free null deficit `m = (d+1) − rank([X_hf,1])`
  is 1 / 15 / 0 on ifc_poisson / cahn_hilliard / fisher_kpp at N_hf = 5 (U4);
  the frozen floors are 400-row floors (U6).
- **Prior-art verdict** (`websearches/.../batch_2/report.md`): E1 preempted,
  E2 preempted-but-MF-composition-open, E3a weak/against-convention, E3b
  preempted (bug fix), E3c preempted-as-fix / open-as-measurement, E4
  preempted (mandatory engineering), **E5 novel**.
- **Immutables block (§4.5) verbatim** — reproduced and checked in the
  self-check section below.
- Anchor `state/anchors/r2s3_lf_train_signal.json` = 23.063617
  (best_floor_panel_geomean); per-dataset floors ifc 10.054891 (NN),
  cahn_hilliard 23.180342 (NN), fisher_kpp 11.993111 (mean).
- Certified `state/noise_floor.json` (`_provisional: false`):
  ifc_poisson **0.9377041**, sharp__cahn_hilliard **0.0912454**,
  sharp__fisher_kpp_2d **0.0007137**, panel 1.1418668.
- Pre-falsified levers (program.md §5 / r1 §5): WNO backbone swap, **LF
  low-mode freezing** (`mf_fno_spectral`), diffusion prior.
- Orchestrator turf boundary: `r2s4_diag-B2` (in build, 3 seeds) owns
  value-of-LF **accounting** — T0-vs-T1 aux-head ±LF at full N with
  `N_FIT_LEVELS = 20,80` and LF **paired to the fit rows**. This stream owns
  **optimizing** the LF training signal in models at N_hf≈5 with LF at
  conditions where no HF exists. Verified from
  `experiment_cards/r2s4_diag/batch_2/B2.json`: no N=5 leg on the sharp
  datasets, and no arm in which the LF pool covers conditions absent from the
  HF fit rows.
- Regime facts re-verified on disk today (not recalled):
  `stripped_data/ifc_poisson/train/fidelity_{8,16,32,64}` = 100/50/20/5 rows
  at 8²/16²/32²/64²; `stripped_data/sharp__cahn_hilliard/train_l{1,2,3}.npz`
  = 400 rows each at 64²/128²/256², `x (400,19)`;
  `sharp__fisher_kpp_2d` the same with `x (400,2)`.
- Declared baseline datum on disk (no re-run needed):
  `outputs/round2/r2s3_lf_train_signal/B1/eval/result_ifc_poisson_baseline_mf_fno_transfer_film_s0.json`
  → `mf_fno_transfer_film`, ifc_poisson, 200 epochs, seed 0, **nRMSE 0.055637,
  skill 1.5455**, same `nrmse_def_hash d3d0ade9…` / `copylf_def_hash 9753ff24…`
  as every round-2 result. ifc_poisson's native N_hf is 5, so this baseline is
  *exactly regime-matched* to the card's primary dataset.
- B1 reference points on ifc_poisson (card part 6): min-norm affine HF-only
  **3.4744** (information limit at any capacity); rung-32 affine + 5-row
  residual ridge **0.2427**; B1 `hf_only` 9.4466; B1 `rung_native` 16.7963;
  NN floor 10.0549; zero floor 27.7778.

## Proposal reasoning

### What the batch-2 verdict forces

The verdict removes three of B1's four candidate B2 families outright: the
linear channel (E1, preempted — "Ship it as a **cited baseline**, never as a
contribution"), Nyquist-pinned clipping (E3b, "Bug fix"), and the per-dataset
gate (E4, "Mandatory engineering; not a claim"). It also *demotes* batch 1's
D3 verdict: the parameter-coverage idea is now
`preempted-but-MF-composition-open`. Exactly one row is `novel`: **E5**, the
matched budget-equal ±LF measurement for a neural condition→field surrogate at
N_hf ≈ 5, priced against the certified 3-seed floor. So the card's deliverable
must be that measurement; the estimator work (repairs, linear channel) enters
as engineering and as declared baselines.

### Why B1's ifc-only framing is not enough

B1 produced a ±LF contrast on all six datasets, but it is not the E5
measurement for three reasons, all recorded on B1's own card: (C1) the arms
were **not normalization-matched** (one shared `max|y|` over all rungs vs the
HF-only arm's HF-only scaler — 42.1× apart on ifc), (C2) the arms were
**epoch-matched, not step-matched** (the LF arm took ~34× more optimizer steps
on ifc: 170 LF rows vs 5 HF rows), and (C3) on the five aligned datasets the
regime was N_hf = 400, where the ladder is degenerate by construction (r1
report §6) — so the only genuinely N_hf≈5 cell in the whole round is
ifc_poisson, n = 1 dataset, and it is also the panel's only affine dataset.
A one-dataset measurement whose dataset is structurally exceptional cannot
carry criterion 1.

### The construction that fixes all three

Restrict HF to 5 rows on the aligned datasets while keeping the **full 400-row
LF rungs**. This is free (existing files, no regeneration), and it manufactures
the missing regime: LF fields at 395 conditions where no HF row exists — E2's
open surface ("LF data can be evaluated at parameter values where no HF data
exists", https://arxiv.org/pdf/2508.08517) in the field-valued, neural,
certified-floor instance the verdict says is unretrieved. It also makes the
**coverage-vs-curriculum decomposition** constructible for the first time: LF
restricted to the same 5 conditions is pure resolution curriculum with zero
parameter coverage; LF at the other 395 is pure coverage. §12.3 demands
precisely this statement ("LF-as-signal designs must state what information the
LF rungs add that the HF rung does not already contain"). On ifc_poisson the
paired variant does not exist (rung conditions are pairwise disjoint, exact
overlap 0), which is why the aligned datasets are needed to answer it.

And it gives a *pre-registerable structural ordering* from a training-free
statistic: the affine null deficit `m = (d+1) − rank([X_hf,1])` at N_hf = 5 is
**1** on ifc_poisson (d=5), **15** on cahn_hilliard (d=19), **0** on fisher_kpp
(d=2). If the null-deficit story is right, the LF effect must order
cahn_hilliard ≳ ifc_poisson > fisher_kpp; if it is wrong, that ordering breaks.

### Alternatives weighed and rejected

**(A) Ship the linear/affine channel as the B2 family (B1's own first
recommendation).** Rejected: the verdict is `preempted` twice over
(https://arxiv.org/abs/1705.02956; https://arxiv.org/pdf/2508.08517), and the
websearcher's instruction 1 is explicit — card it as a *cited baseline*, expect
a rebadge check. It enters this card as the non-trained reference arm
`ref_linear_mf` (with `ref_linear_hfonly` = the min-norm information limit),
which is also B1 part 7 item (4)'s demand that the honest ifc bar be 0.2427,
not 16.7963.

**(B) A pure repair card: rerun B1's design with the trio on the full panel.**
Rejected: two thirds of the trio are `preempted` bug fixes, the third is
`preempted` as a fix, and the panel-wide full-N ±LF contrast is r2s4-B2's turf.
The repairs stay — as the *instrument* that makes the E5 measurement
interpretable, and priced in-job by one ablation arm — but they are not the
claim.

**(C) Distillation from a round-1 LF-consuming teacher (§5.10b role).**
Rejected for this batch: it needs a vendored round-1 corrector (r2s2's build
surface), it re-enters the "published MF-distillation composites" family the
batch-1 verdict marked `preempted` for D1/D2, and it would not produce a
matched ±LF contrast at N_hf≈5 — the one `novel` deliverable. Recorded as a
B3 candidate.

**(D) Add pfc / allen_cahn / helmholtz to the dataset set.** Rejected on cost
and on interpretability: pfc and allen_cahn are stochastic maps (ADR r2-0003 —
the realized IC is absent from the condition), so LF at *other* conditions
cannot supply a test sample's IC and any null is doubly confounded; helmholtz
is report-only (best floor = the zero field, 3.3441) and its certified mce
2.9530 is larger than any effect plausibly available at N_hf = 5. fisher_kpp is
kept as the m = 0 cell despite being stochastic, with the confound stated: its
predicted null has two candidate causes and this card does not disambiguate
them — it only uses the *ordering* against cahn_hilliard as the falsifiable
statement.

**(E) Make the per-dataset gate a switch that selects the scored arm** (B1
part 7 item (2)). Rejected: a data-dependent scored path invites exactly the
lineage-bound caveat round 1 recorded for routing rules, and with 3 datasets
its selection rule could never be validated. The gate statistics (affine-LOO
per rung, null dim `m`, LF null-direction recovery) are computed at prepare()
and **reported**, and they pre-register the per-dataset predictions; they never
choose an arm.

**(F) Re-run `mf_fno_transfer_film` as an in-job baseline arm at N_hf = 5 on
the sharp datasets.** Rejected: that would require modifying a factory family
(its subsampling is not exposed), and ifc_poisson's native N_hf is 5, so the
existing on-disk gate run (skill 1.5455, same hashes) is already an exactly
regime-matched declared baseline. It is cited, and the card states how the new
family differs (joint step-matched training with per-rung scalers, pinned
modes, and a null-direction penalty vs sequential LF-pretrain→HF-finetune with
no null-space machinery).

### The null-direction mechanism, concretely (E3c's open half, as a training
signal rather than a post-hoc fix)

B1 measured that the LF information *reaches the weights* (null-direction cos
+0.8497) but arrives with 2.65× gain, while the no-LF control puts 27.7% of its
law energy anti-aligned (cos −0.9919) in that same direction — a measured
violation of the min-norm implicit-bias prediction
(https://arxiv.org/pdf/2006.07356; theory context https://arxiv.org/pdf/2209.15265,
**search-returned only**, cited as such and never claimed as fetched). The
cheap, architecture-general way to act on that is a **paired-difference
penalty along the HF design's null directions**: sample a train condition `c`,
a unit null vector `v ∈ null([X_hf,1])`, a step `t`, and penalize
`|| [S(c+tv) − S(c)] − t·(vᵀ Θ_LF) ||²`, where `Θ_LF` is an affine law fitted
on the LF rung selected by that rung's own in-rung LOO. This constrains only
the directions the 5 HF rows cannot see, leaves the row space to the HF rows,
uses no test information, and is identically zero when `m = 0` — which is why
fisher_kpp is a structural null by construction, not by tuning.

## Proposal

- **Category**: `lf_train_signal / matched budget-equal ±LF at N_hf≈5 with
  LF-at-uncovered-conditions (coverage vs curriculum), repaired-instrument
  neural channel`
- **Card type**: `model`
- **Motivation**: the batch-2 prior-art verdict, verbatim —
  > **E5** — the **measurement**: matched, budget-equal with/without-LF-training
  > contrast for a **neural condition→field** surrogate at N_hf ≈ 5 (and N = 400
  > with condition-aligned rungs), per dataset, against a certified 3-seed noise
  > floor | **novel** (nearest neighbours named) | … | Everything: three
  > independent search framings (batch 1 iter 3; batch 2 iters 4 and 5) failed
  > to retrieve a matched-architecture with/without-LF accounting for neural
  > field surrogates at this sample count. This is round-2 success criterion 1
  > and the stream's remaining publishable content.

  with the composition surface from the same table —
  > **E2** … | **preempted-but-MF-composition-open** | … | The **field-valued,
  > neural, certified-floor** instance: null direction of a *condition* design
  > matrix filled by **coarse consistent PDE solves**, priced in skill units
  > against a 3-seed `min_claimable_effect` … **Supersedes batch 1's `novel`
  > verdict for D3.**

  and the two engineering rows carried as declared, cited engineering —
  > **E3b** … | **preempted** | https://arxiv.org/html/2310.00120 ("the first α
  > modes in each direction, where α is independent of the discretization") |
  > Nothing. This is the standard convention; B1 deviated from it. Bug fix.
  > **E4** … | **preempted** | https://arxiv.org/abs/2403.08118 … | Mandatory
  > engineering; not a claim.

- **Concrete config**: new from-scratch family
  `models_r2/r2s3_null_supply` (worktree `worktrees/r2s3_lf_train_signal/B2`),
  condition-only at test, stripped view only.
  - **Model** `NullSupplyDecoder(cond_dim, width=64, blocks=4)` with
    `forward(cond, out_hw) -> (B,H,W)`: coord channels built at forward time,
    lift 2→64, 4× [SpectralConv2d(α modes) + 1×1 conv + FiLM(cond) after
    GroupNorm + GELU], projection 64→128→1, FFT `norm="forward"`.
    **Mode policy `pinned_min_rung_nyquist`** (E3b, MG-TFNO convention):
    `α = min(MODES_CAP=12, min over ALL train rungs of floor(N_rung/2))`,
    computed once per dataset from the full rung set and applied **identically
    in every arm** (ifc → α = 4; cahn_hilliard / fisher_kpp → α = 12), so no
    mode weight is ever supervised by the 5 HF rows alone.
  - **Per-rung scaler** (E3a, declared as a dataset-convention fix, not a
    claim): `s_f = max|y|` over rung `f`'s own train fields; losses in
    per-rung-scaled units. The HF scaler is therefore **identical across arms**
    — this closes B1's confound C1.
  - **Step-matched budget** (closes C2): `steps = --epochs × 25`
    (200 → 5000; contract tier 2 → 50). Every arm takes the same steps, the
    same HF batch (all 5 rows every step), the same AdamW(1e-3, wd 1e-5),
    cosine over the same horizon, grad-clip 1.0. LF arms additionally draw one
    LF minibatch (16 rows, rungs cycled deterministically) per step. Budget
    equality is defined as *identical optimizer steps and identical HF-row
    exposure*; the LF arms' extra forward is the treatment and is stated.
  - **Loss**: `MSE_HF + LAMBDA_LF·MSE_LF + LAMBDA_NULL·NullPenalty`
    (all in per-rung-scaled units). `NullPenalty` as derived above, over
    `NULL_BATCH=8` sampled (c, v, t) triples per step, `t ~ U(−1,1)` in
    standardized condition units, `Θ_LF` = ridge-affine law on the LF rung
    selected by in-rung LOO, lifted to the HF grid with the ADR r2-0001
    convention (imported read-only from `round2/eval` / vendored with a 1e-9
    agreement assert on the TRAIN split — r2s4-B2's precedent). `m = 0`
    ⇒ penalty ≡ 0 by construction.
  - **N_hf = 5 protocol**: ifc_poisson is native (5 HF rows). On the aligned
    datasets, 5 HF rows are drawn by `R2S3B2_SPLIT_SEED` from the existing 400;
    the LF rungs keep all 400 conditions. No test row is ever touched; no data
    is regenerated; the 400 HF rows remain on disk unmodified.
  - **Arms** (each its own `ROUND2_EVAL_RESULTS` dir ⇒ its own `ckpt_dir` and
    cache key; env is hashed):

    | arm | LF pool | null penalty | datasets (split seeds) |
    |---|---|---|---|
    | `A0_nolf` | — | off | ifc(native), cahn_hilliard(0,1,2), fisher_kpp(0,1) |
    | `A1_lf_cov` | all rungs, all conditions | off | ifc(native), cahn_hilliard(0) |
    | `A2_lf_cov_null` **PRIMARY** | all rungs, all conditions | on | ifc(native), cahn_hilliard(0,1,2), fisher_kpp(0,1) |
    | `A3_lf_paired` | LF only at the 5 HF conditions | off (vacuous) | cahn_hilliard(0) |
    | `A5_lf_norepair` | all rungs | off | ifc(native) — B1's configuration in-job: shared `max|y|`, unpinned modes |

    On fisher_kpp `m = 0`, so `A2 ≡ A1` by construction and only `A2` is run
    (recorded, not hidden).
  - **Non-trained reference splits** (never named `test*`):
    `ref_linear_mf` (the **preempted** channel `c·A(cond) + R(cond)`: rung
    chosen by in-rung LOO, `c` and residual ridge on the 5 HF rows, α by exact
    LOO), `ref_linear_hfonly` (min-norm affine on the 5 rows = the information
    limit), and the floor arms `ref_zero`, `ref_train_mean_n5`,
    `ref_nn_condition_n5` (in-regime, from the same 5 rows) plus
    `ref_train_mean_full`, `ref_nn_condition_full` seam-checked to
    `state/anchors/floors.json` at 1e-9, **raising on mismatch**.
  - **Reported gate/instrument block** (E4, cited, never a switch): per-rung
    affine-LOO residual, `m`, singular values of `[X_hf,1]`, the null-direction
    energy fraction, LF→null recovery cosine/gain, per-arm train-vs-test gap,
    and per-arm predictions dumped at the HF **train** conditions (B1 part 7
    item (4)) so `tools/posthoc_repair_ladder.py` can price residual error
    without a retrain.
  - **Declared baseline** (§12.3): `mf_fno_transfer_film`, **cited** from
    B1's on-disk gate run (ifc_poisson, 200 epochs, seed 0, nRMSE 0.055637,
    skill **1.5455**, identical `nrmse_def_hash`/`copylf_def_hash`), with the
    stated differences (joint step-matched training, per-rung scalers, pinned
    modes, null-direction penalty vs sequential LF-pretrain→HF-finetune).
    No factory file is read for training and none is edited.
  - **Guard leg**: primary arm `A2` on `--datasets guard`, contract tier (2
    epochs), at each guard dataset's native N_hf (`R2S3B2_GUARD_NSUB=off`).

- **Recipe**: see the JSON block in `report.md` (identical content).

- **Expected outcome** (skill units, corrected denominators, seed 0,
  `provisional-single-seed`):

  | quantity | prediction | vs floor / anchor |
  |---|---|---|
  | ifc `A0_nolf` | 8–12 (best est. 9.5) | B1's `hf_only` was 9.4466; NN floor 10.0549 |
  | ifc `A2` (PRIMARY) | **2–8** (best est. 5) | must beat 10.0549 (F5); information limit 3.4744; declared baseline 1.5455; linear channel 0.2427 |
  | **ifc value-of-LF `A0 − A2`** | **+2 to +7** (best est. +4.5) | mce **0.9377041** → 2.1–7.5× the floor; B1 measured **−7.3497** |
  | ifc `A2 − A5_lf_norepair` | +5 to +12 | prices the repair trio in-job vs 0.9377041 |
  | cahn_hilliard `A0` (N=5, mean of 3 draws) | 25–45 | frozen 400-row NN floor 23.1803; in-regime floors reported |
  | cahn_hilliard `A0 − A2` | **+1 to +8** | vs `max(0.0912454, in-job paired spread over 3 draws)` |
  | cahn_hilliard `A3_lf_paired − A2` | +0.5 to +5 | coverage beyond curriculum, same threshold |
  | fisher_kpp `A0 − A2` (mean of 2 draws) | −0.5 to +0.5 | predicted **null**; ordering must sit below cahn_hilliard's effect |
  | panel geomean | **not computed** | 3 of 6 panel datasets scored; no criterion-2 panel claim; anchor 23.0636 quoted for context only |

  Rationale for the ifc sign flip: the null direction carries 18.83% of the
  law's coefficient energy and the LF rungs recover it at 0.940/0.982/0.996
  (B1 turn 2 B7); per-rung scaling removes the 1772× HF-loss deflation that
  B1's part 6 blames for the row-space damage (0.921 vs the control's 0.604);
  pinned modes remove the `|k|>4` band that was supervised by 5 deflated rows
  (worth +1.605 post hoc); the null penalty caps the 2.653× gain error. I do
  **not** predict beating the declared baseline (1.5455) or the preempted
  linear channel (0.2427) — the deliverable is the certified measurement, not
  a champion. Standing caveats carried: ifc_poisson is an exactly affine
  benchmark, so any bar-level number there is **rank recovery, not operator
  learning** (B1 part 6 M11); helmholtz/pfc are not scored, so their caveats
  do not arise.

- **Expected falsification** (per dataset, per mechanism — B1 part 7 item (2)
  and websearcher instruction 6):
  **F1 (primary)** falsified if on `ifc_poisson` `A2_lf_cov_null` fails to beat
  `A0_nolf` by more than the certified **0.9377041** skill units;
  **F2 (instrument)** falsified if `A2` fails to beat the in-job
  `A5_lf_norepair` on `ifc_poisson` by more than 0.9377041 (the repair trio was
  then not what changed B1's sign);
  **F3 (coverage vs curriculum)** falsified if on `sharp__cahn_hilliard`
  (`m = 15`) `A2` fails to beat `A3_lf_paired` by more than
  `max(0.0912454, in-job paired spread over the 3 draws)`;
  **F4 (structural ordering)** falsified if the mean LF effect
  `A0 − A2` on `sharp__fisher_kpp_2d` (`m = 0`) **exceeds** the same effect on
  `sharp__cahn_hilliard` (`m = 15`) by more than
  `max(0.0912454, in-job paired spread)`;
  **F5 (has it learned anything)** falsified if on `ifc_poisson` `A2` does not
  beat the best in-regime floor **10.054891** (`nn_condition` over the same 5
  rows; `train_mean` 11.206332, `zero` 27.777778 reported beside it), or if on
  `sharp__cahn_hilliard` / `sharp__fisher_kpp_2d` `A2` fails to beat its own
  in-regime N=5 best floor on ≥ 1 of the two.

- **Anchor reference**: `null` (program.md §4.5 — all four round-2 streams are
  gap/lever/diag; the own-stream anchor 23.063617 is implicit, and this card
  scores a 3-dataset subset so no panel-geomean claim is made).

## Immutables self-check (positive evidence for each)

1. **Data read-only** — the family calls `load_mf_dataset` on
   `stripped_data/<ds>` for train and test and writes nothing there; the
   `N_hf = 5` legs *select* 5 of the existing 400 train HF rows via
   `R2S3B2_SPLIT_SEED` (a training-procedure choice, explicitly permitted by
   r1 §5 "What CAN be changed: … training procedure"; direct precedent
   `r2s4_diag-B2` `R2S4B2_N_FIT_LEVELS=20,80`). No HF sample is added, no file
   regenerated, and LF is always the on-disk coarse solve (never downsampled
   HF): the rung tensors are read as-is from `train_l{1,2}.npz` /
   `train/fidelity_{8,16,32}` and only *lifted* to the HF grid inside the
   `Θ_LF` fit, never written back.
2. **Panel + guard fixed** — the card scores 3 of the 6 frozen panel datasets
   (`ifc_poisson,sharp__cahn_hilliard,sharp__fisher_kpp_2d`, a subset, nothing
   added) and the exact frozen guard trio `heat_local,fluid,sharp__sod_1d` at
   contract tier; it makes no panel-geomean claim precisely because it scores
   a subset.
3. **Eval layer / spec untouched** — all new code is
   `<worktree>/models_r2/r2s3_null_supply/**` plus scripts under
   `<worktree>/scripts/`; scoring runs through the unmodified
   `round2/eval/score_panel.py`; the ADR r2-0001 lift convention is *imported
   read-only* (or vendored with a 1e-9 assert against the eval implementation
   on the TRAIN split, r2s4-B2's precedent). Nothing under `round2/eval/`,
   `project.yaml`, `program.md`, `docs/adr/` or `subagents/` is written.
4. **One nRMSE definition** — every scored number comes from
   `score_panel.py` → `eval/nrmse.py` (`nrmse_def_hash d3d0ade9…`); the
   training objective (per-rung-scaled MSE + LF term + null penalty) is a
   training loss, which r1 §5 states is free ("training loss is free; the
   SCORED metric is not").
5. **Contract CLI fixed** — `smoke_eval.py` keeps the six-arg signature
   (`--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed`); every
   knob is an `R2S3B2_*` environment variable and every one of them appears in
   the recipe `env` block, so they enter the cache key.
6. **Seeds / tier epochs fixed** — `seeds: [0]` (round-2 strict 1-seed,
   `project.yaml seed_protocol.seeds=[0]`); `epochs: 200` (smoke) and `2` for
   the guard leg (contract). The subsample draws are **split** seeds
   (`R2S3B2_SPLIT_SEED`), recorded in env and distinct from the training seed;
   they do not add training seeds and do not touch the end-of-round top-3
   protocol.
7. **Guarded factory surfaces untouched** — the only factory contact is a
   read-only import of `data_adapters.loaders` / `data_adapters.geometry`
   (the pattern used by `r2s3_rung_supervised`, `r2s4_cert_min` and
   `r2s4_b2_lfvalue`); the declared baseline `mf_fno_transfer_film` is
   **cited from an existing result JSON**, not re-run and not edited; nothing
   under `factory_root/{eval,baselines,references,scripts,data}`, `factory.md`
   or `akash/` is opened for writing.
8. **Checkpoint-resume** — every arm writes `<ckpt_dir>/last.pt` every 250
   steps with `{step, steps_target, model, opt, sched, rng, arm, split_seed,
   dataset, alpha, per_rung_scalers, null_basis, theta_lf_digest}` and resumes
   exactly from it; a `done` marker keyed on `(steps_target, arm, split_seed,
   dataset)` makes resubmission after preemption idempotent (B1's pattern,
   which survived the 77-min job).
9. **Thresholds exceed the certified noise floor** — F1 and F2 use exactly
   `ifc_poisson.min_claimable_effect = 0.9377041289531141`; F3 and F4 use
   `max(sharp__cahn_hilliard.min_claimable_effect = 0.0912453532230089,
   in-job paired spread)`, which is ≥ the certified constant by construction;
   the fisher_kpp effect is additionally reported against
   `max(0.0007136812826775696, in-job spread over 2 draws)`; F5 uses the frozen
   floor 10.054891, itself 10.7× the ifc floor. Predicted effects (+2 to +7 on
   ifc, +1 to +8 on cahn_hilliard) exceed those constants by 2–80×.
10. **Not a pre-falsified lever** — nearest is **LF low-mode freezing**
    (`mf_fno_spectral`: "worst on sharp, catastrophic on lid-cavity"), which
    *freezes* LF-derived low modes inside the model. The difference: nothing is
    frozen here and no LF field enters the forward path at all; the mode policy
    fixes the *number of active spectral weights* to α independent of
    resolution so that every weight is supervised by every rung (MG-TFNO's
    convention, https://arxiv.org/html/2310.00120), and the LF signal acts only
    through a training loss and a null-direction penalty. Nearest in-stream is
    B1's rung supervision, which this card differs from on five recorded axes
    (per-rung vs shared scaler, pinned vs grid-clipped modes, null penalty,
    step- vs epoch-matching, N_hf=5-with-full-LF-coverage vs full-N aligned) —
    B1's falsification is cited in the motivation.
11. **Floor arms mandatory** — `ref_zero`, `ref_train_mean_n5`,
    `ref_nn_condition_n5` (in-regime) and the frozen `ref_train_mean_full` /
    `ref_nn_condition_full` seam-checked to `state/anchors/floors.json` at
    1e-9 with a RAISE on mismatch, reported beside every arm on every scored
    dataset; **F5 is written directly against them** (ifc best floor 10.054891
    vs `train_mean` 11.206332 vs `zero` 27.777778).

## Status

- Slot covered (one proposal, `model` card).
- Reopen candidates resolved: **none exist** — every round-2 card carries
  `reopen_candidate: false` (verified by reading all six card JSONs).
- Immutables self-check: **pass (11/11)** on this iteration; no revision
  needed, so no `iteration_2.md`.
