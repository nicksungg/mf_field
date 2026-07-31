# Iteration 1 — `r2s1_direct` batch 1 design

## Design context considered

- **summary_so_far.md section 6** (the six unknowns) and the prior-art verdict
  (D1/D2 `preempted`, D3 `preempted-but-MF-composition-open`).
- **program.md 12.1 verbatim** (quoted in summary section 2), plus ADR r2-0003
  (`docs/adr/0003-condition-vector-incompleteness.md`), which the orchestrator
  flagged as landing after program.md was written.
- **Immutables block (section 4.5 of my prompt), verbatim**, held in view through
  the whole design; self-check below.
- **Anchor**: `state/anchors/r2s1_direct.json` value 23.0636
  (`best_floor_panel_geomean`, `provisional: false`); per-dataset floors from
  `state/anchors/floors.json` (helmholtz 3.3441 zero / pfc 59.812 mean /
  allen_cahn 269.196 NN / fisher_kpp 11.993 mean / cahn_hilliard 23.180 NN /
  ifc_poisson 10.055 NN).
- **Noise floor**: `state/noise_floor.json`, `_provisional: true`,
  `min_claimable_effect` (skill units) helmholtz 10.6811, pfc 6.9839,
  allen_cahn 14.8152, fisher_kpp 1.2198, cahn_hilliard 1.1604, ifc_poisson
  0.2399. Program 4.3: provisional -> judged directly until r2s4-B1 certifies.
- **Pre-falsified levers** (r1 program 5): WNO backbone swap, LF low-mode
  freezing, diffusion prior for point accuracy. None is in this design.
- **Round-1 carry-ins actually read**: s5_tuning-B3 part 7 (helmholtz per-sample
  scale: legal LF proxy 0.367721 vs true-scale oracle 0.258380; closing open
  question = "a PREDICTED scale head"), the two-gate loss rule
  (`round1/state/orchestrator_flow.md:2801`), r1 report 5.3 (helmholtz zero
  predictor), 5.6 (drift-class rule).
- **Harness constraints read from code**: `eval/score_panel.py` points the family
  at `stripped_data/<ds>` and refuses views exposing >1 test level;
  `_extract_test_metric` selects the split named `test_hf`/`test` and errors on
  ambiguity -> **every extra arm must be emitted under a split name that does not
  start with `test`** (use `ref_*`, `cert_*`); it prefers `rel_l2_per_sample`.
  Family CLI is the unchanged six-arg factory contract; `code_hash` covers the
  family dir + `models/_common` + eval files + env knobs.

### Read-only measurements I made before designing (train split, stripped view)

Scratchpad scripts `probe.py` / `probe3.py` / `probe4.py`; all read
`stripped_data/*/train_l*.npz` only (no test file touched, no data written).

| dataset | cv(||y||) | NN-pair rel diff vs cond distance | aleatoric est | LOO-5NN R2 on log||y|| | cos(HF diff, LF diff) |
|---|---|---|---|---|---|
| pfc | 0.207 | FLAT (0.447 @ d<=0.054 ... 0.448 @ d<=0.472) | ~0.30-0.32 | 0.965 | 0.997 (median 1.000) |
| fisher_kpp | 0.060 | FLAT (0.330 -> 0.346) | ~0.233-0.245 | 0.986 | 0.969 (median 0.970) |
| allen_cahn | 0.559 | RISING (0.414 @ d<=0.198 -> 0.698 @ d<=0.885; slope +1.195, intercept 0.0076 -> 0.0616) | 0.062 (weak support) | 0.895 | 0.998 |
| helmholtz | 12.265 | RISING (0.427 -> 1.208; slope +3.169) | 0.193 (unreliable) | 0.140 (median scale err 42%) | 0.985 |
| cahn_hilliard | 0.038 | NO SUPPORT (min pair distance 2.822 in 19 standardized dims) | n/a | 0.076 (cv tiny, amplitude irrelevant) | n/a |

Two consequences that drove the design: (a) ADR r2-0003's three-dataset
stochastic grouping is right for pfc/fisher_kpp but **questionable for
allen_cahn**, whose pair profile is the signature of a deterministic
under-sampled map; (b) on helmholtz the *amplitude* channel, not the pattern
channel, is what destroyed round-1 models (100x norm range under one global
`max|Y|` scaler) — and round 1 closed s5 on exactly the open question of a
predicted scale head.

## Proposal reasoning (alternatives weighed and rejected)

**Rejected A — bare FiLM-FNO decoder as the card's contribution.** Directly
`preempted` (verdict D1: "Nothing mechanism-level. Admissible only as a
*measurement/baseline arm*"). Proposing it as the contribution invites the
reviewer's rebadge check (program 5.10) and repeats the 0-for-4 novelty pattern
(13.3). Kept, but **declared as the baseline architecture**, not as novelty.

**Rejected B — fixed-POD / RB coefficient regression as the contribution.**
`preempted` (D2: "POD-NN/PCA-Net prior art under a new name") and Lanthaler
2210.01074 proves linear reconstruction is inefficient for discontinuous
operators (4/6 panel datasets). Kept as a cheap closed-form **control arm** with
its failure mode predicted in advance, per the websearcher's item 6.

**Rejected C — pure identifiability-certification diagnostic card.** This is the
open composition (D3), but (i) the stream directive requires a from-scratch
condition->HF *experiment*, and (ii) ADR r2-0003 consequence 1 assigns per-dataset
floor certification to r2s4. Resolution: keep D3 as the **interpretation frame and
an in-job, training-free companion measurement** (zero extra compute) inside a
model card, and do not duplicate r2s4's test-split floor panel or 3-seed spread.

**Rejected D — distributional / ensemble-statistic scoring** on the stochastic
datasets (arXiv 2604.09664's approach). Forbidden as a primary score:
program 2.1 fixes one nRMSE definition and 5.3 freezes the eval layer.

**Rejected E — physics residuals / new HF samples / acquisition.** Barred by
r1 ADR 0009 (physics-agnostic at test) and program 5.11 (no new HF data); the
websearcher's item 6 flags acquisition as the literature's inadmissible answer.

**Chosen composition.** One new from-scratch family whose *architecture* is the
declared-preempted D1 decoder, made regime-appropriate by two elements that the
measurements above show are load-bearing, plus the D3 certificate:

1. **Amplitude-direction factorization.** The decoder emits a unit-L2
   *direction* field; a separate MLP head predicts log||y|| from the condition;
   prediction = exp(logamp) * direction. Motivation is measured, not aesthetic:
   the scored metric is per-sample relative L2, helmholtz's ||y|| spans >100x
   (cv 12.27), and round 1 showed 60% of the damage is the amplitude channel and
   that the true-scale oracle reaches skill 0.864 there while the LF-proxy scaler
   reaches only 0.367721/0.299033 = 1.230. Round 1's scale predictor consumed the
   **LF field** (illegal at test in round 2); this predicts the scale from the
   **condition vector**, which is precisely the open question s5-B3 closed on.
2. **Out-of-fold floor blend.** Final prediction = lambda * model +
   (1 - lambda) * b, with b chosen from {zero, train_mean, nn_condition} and
   lambda on a 21-point grid, both selected on a **calibration fold disjoint from
   the model-selection fold** (the r1 D3 val_idx double-consumption caveat is
   explicitly avoided; no test-split quantity ever enters). Two functions: it
   makes "beats the mandatory floor arms" a design property rather than a hope
   (program 2.2), and lambda* is itself a per-dataset readout of how much the
   condition vector buys over the best trivial predictor.
3. **In-job identifiability certificate (D3, training-free).** Condition-pair
   statistics on the train split: relative field difference vs standardized
   condition distance with a slope test and a zero-distance extrapolation
   (-> aleatoric nRMSE estimate -> maximum achievable skill per dataset), a
   `no_support` verdict when the nearest pair distance exceeds
   `R2S1_CERT_MIN_SUPPORT_D` (cahn_hilliard will trip this), and the
   **LF-carrier cosine** between the block-mean HF pair difference and the
   train-LF pair difference — the leg that makes the floor "validatable rather
   than assumed" (D3(i)) because the omitted driver is a stored coarse solve.
   Train-side LF only; program 5.9 makes train-side LF use explicitly free.

Loss follows the r1 **two-gate rule** (lambda_loss = 1 relative-L2 with a
p25-median denominator floor) rather than plain MSE — reuse of an established
round-1 rule, cited, not rediscovered.

Why this is genuine either way (program 1): if it works, we learn that the
amplitude channel was the binding constraint on condition->HF and we get the
round's first sub-anchor panel number; if it fails, we learn that a
well-conditioned from-scratch decoder cannot beat trivial predictors even where
the condition vector is provably complete, which makes the LF-training-signal
streams (r2s2/r2s3) the only remaining route — and the certificate quantifies,
per dataset, how much of the failure is irreducible.

## Proposal

- **Category**: `gap / identifiability-certified condition->HF decoder with a
  condition-predicted amplitude-direction factorization`
- **Card type**: `model`
- **Motivation**: verdict D1 is quoted verbatim in the report; the card takes the
  websearcher's own instruction ("The only open composition found is D3 ...
  instantiate the conditional-mean-barrier diagnostic on this panel, where the
  omitted driver is not abstract noise but the *stored LF coarse solve*") and
  makes it the interpretation frame of a from-scratch condition->HF model whose
  one regime-specific element answers round-1 s5-B3's closing open question.
- **Concrete config**: new family `models_r2/r2s1_cond_decoder`, built from
  scratch (no round-1 code vendored, condition-only forward signature, no field
  input at any stage of test). Condition standardized on train stats, embedded
  through 16 random Fourier features + a 128-wide MLP into a 16x16xC latent seed;
  4 FiLM-modulated spectral (FNO-style) blocks with `modes_cap=16`, hidden 64,
  progressive Fourier upsampling to the native HF grid (WORK_CAP 256); output
  normalized to unit L2 per sample (`R2S1_DIR_NORM=unit_l2`); separate 128-wide
  MLP head predicts log||y|| (`R2S1_AMP_HEAD=log_norm_mlp`); prediction =
  exp(logamp) * direction. Training: AdamW lr 1e-3, wd 1e-5, cosine schedule,
  batch 16, grad clip 1.0, 200 epochs, relative-L2 loss with p25-median
  denominator floor (two-gate rule), amplitude head trained jointly on log||y||
  (weight 1.0). Folds: 10% model-selection + 10% blend-calibration, disjoint,
  drawn from the train split only; when N_train < 20 (ifc_poisson, N_hf = 5) the
  protocol switches to leave-one-out for the blend and fixed-epoch training with
  no early stop. Emitted splits: `test_hf` = the scored blended arm;
  `ref_raw` (lambda forced to 1, same checkpoint - free), `ref_pod_lin`
  (rank-50 POD + ridge from the condition, closed form - the D2 control),
  `ref_zero` / `ref_train_mean` / `ref_nn_condition` (floor arms recomputed
  in-job and asserted equal to `state/anchors/floors.json` within 1e-9 - a seam
  check, not a re-certification), and `cert_*` (the D3 certificate:
  per-dataset aleatoric estimate, slope, support verdict, implied maximum
  achievable skill, LF-carrier cosine). Guards (`heat_local`, `fluid`,
  `sharp__sod_1d`) at contract tier (2 epochs) per program 2.3.
- **Recipe**: see report.md (identical JSON; transcribed verbatim by the starter).
- **Expected outcome** (skill units, primary blended arm, seed 0, 200 epochs):
  helmholtz 1.3-2.5 (floor 3.344, report-only, zero-floor column shown),
  pfc 44-55 (floor 59.812; certified ceiling ~41; pfc denominator caveat),
  allen_cahn 150-200 (floor 269.196; the interesting one - a win here says the
  map is condition-identifiable and refines ADR r2-0003),
  fisher_kpp 11.0-11.8 (floor 11.993; certified ceiling ~11 - almost no headroom
  exists), cahn_hilliard 12-19 (floor 23.180; 16 IC-Fourier dims make it the
  best-identified sharp dataset), ifc_poisson 9-10 (floor 10.055; anecdote-grade,
  N_hf = 5). Panel geomean point estimate **~17.3** vs the anchor 23.0636
  (-25%). Mandatory floor-arm comparison: the blend makes "at least the best
  floor" a design property, so the informative quantity is the *margin* over
  NN-in-condition / train_mean / zero per dataset, reported next to lambda*.
- **Expected falsification**: one sentence, in report.md (three legs: panel
  geomean > 19.60; failure to beat the best floor by >= 25% on BOTH
  cahn_hilliard and allen_cahn; or being worse than 1.15x the best floor on any
  scored panel dataset).
- **Anchor reference**: `null` (program 4.5 - all four round-2 streams are
  gap/lever/diag; own-stream anchor 23.0636 implicit).

## Status

- Slot **covered** (one proposal, model card).
- Skipped: no.
- Reopen candidates resolved: **none exist** (stream's first batch; verified
  `experiment_cards/r2s1_direct/` has no `B*.json`).
- Immutables self-check: **pass (10/10 + 11)** — evidence below.

### Immutables self-check (positive evidence per item)

1. **Data read-only.** The family calls `load_mf_dataset(dataset_dir, split)`
   with `dataset_dir` supplied by `score_panel.py` (= `stripped_data/<ds>`), and
   writes only to `--out`, `--ckpt_dir` and `R2S1_DIAG_OUT` under
   `mffp_autoresearch_outputs/`; N_hf stays 5 on ifc_poisson (the small-N
   protocol adapts folds instead of adding data), and no LF is constructed by
   downsampling HF anywhere (LF is read from `train_l*.npz` only, for the
   certificate's cosine leg).
2. **Panel + guard set fixed.** `recipe.datasets = "panel"` resolves through
   `project.yaml panel:` (the same 6 datasets); guards are the exact three in
   `project.yaml guard_set:` at contract tier; no dataset is added or dropped.
3. **Eval layer / spec untouched.** The design needs zero edits to
   `round2/eval/`: it conforms to the existing contract by naming the scored
   split `test_hf` and every extra arm `ref_*`/`cert_*`, which
   `_extract_test_metric` (read at `eval/score_panel.py:140-183`) accepts without
   modification.
4. **One nRMSE definition.** Scoring is whatever `score_panel.py` computes from
   `rel_l2_per_sample` on `test_hf`; the p25-median-floored relative loss is a
   *training* loss only and never touches the reported metric.
5. **Contract CLI fixed.** The family exposes exactly
   `--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed`; every knob in
   the design appears as an `R2S1_*` key in the recipe `env` block, which is how
   `score_panel.py --env` passes it (and it enters `code_hash`).
6. **Seeds / tier epochs fixed.** `recipe.seeds = [0]`, `recipe.epochs = 200`
   (smoke tier per `project.yaml tiers.smoke_epochs`), guards at 2
   (`contract_epochs`); no full-tier run is requested.
7. **Guarded factory surfaces untouched.** All new code lives in
   `models_r2/r2s1_cond_decoder/` on branch `round2/exp-r2s1_direct-B1`; the only
   factory contact is *importing* `data_adapters` (read-only import, the same
   pattern `mf_fno_transfer_film/smoke_eval.py:41-44` uses), and nothing under
   `factory_mffp/{eval,baselines,references,scripts,data}` or `akash/` is edited.
8. **Checkpoint-resume.** Single-stage training with one optimizer and two heads
   makes `<ckpt_dir>/last.pt` = {model+amp-head state, optimizer, epoch, rng,
   fold indices, grid} sufficient to resume; the blend/certificate stages are
   post-training and deterministic given the checkpoint, so resume is
   implementable exactly as in the round-1 families.
9. **Falsification vs noise floor.** Quoted `min_claimable_effect` (skill units):
   cahn_hilliard 1.1604 - my leg demands 23.180 -> <= 17.39, margin **5.79**;
   allen_cahn 14.8152 - leg demands 269.196 -> <= 201.90, margin **67.30**;
   no-harm clause at 1.15x gives margins pfc **8.97** (floor 6.9839), fisher_kpp
   **1.80** (1.2198), allen_cahn **40.38** (14.8152), cahn_hilliard **3.48**
   (1.1604), ifc_poisson **1.51** (0.2399) - all exceed their entries. The panel
   geomean leg (>= 15% below 23.0636) exceeds the implied geomean noise
   (~12.4%, computed as (1/6)*sqrt(0.70^2 + 5*0.12^2) from the same file's
   relative spreads). `ext__helmholtz_2d` is the one place where the provisional
   entry (10.6811, i.e. 3.2x the entire zero floor) cannot be exceeded by any
   threshold; it is therefore left **report-only** (program 2.3 continues r1's
   report-only discipline there) and carries no falsification weight, and the
   whole clause is judged directly per program 4.3 until r2s4-B1 certifies.
10. **Not a pre-falsified lever.** Nearest is round 1's per-sample target
    normalization line (s5-B3 `revin_lf`, s2-B3 `persample_pred`), which was NOT
    falsified but *closed as an open question*: both took the per-sample scale
    from the **LF field**, which is unavailable at test in round 2; this card
    predicts the scale from the **condition vector**, the exact successor s5-B3
    part 7 named. The three actually pre-falsified levers (WNO backbone swap, LF
    low-mode freezing, diffusion prior) appear nowhere in the design.
11. **Floor arms in the falsification reasoning.** The mandatory NN-in-condition
    / train-mean / zero arms from `state/anchors/floors.json` are (a) emitted as
    `ref_*` splits and asserted identical within 1e-9, (b) the blend's candidate
    bases, and (c) the reference of every falsification leg - the 25% legs are
    stated against the best floor per dataset and the no-harm clause is stated
    against 1.15x the best floor.
