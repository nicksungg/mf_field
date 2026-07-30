# iteration_1 — s1_poisson-B3 design

## Design context considered

- `brainstormer/s1_poisson/batch_3/summary_so_far.md` §6 (unknowns 1-6) and §1
  (prior-art verdicts (i)-(iv)).
- `program.md` §12.1 (quoted verbatim in summary §2), §5 immutables (quoted in
  §4.5 self-check below), §2.2 (ADR-0002 paper-bar reference for ifc_poisson),
  §4.4 (strict single seed), §4.5 (anchors / noise-floor rule).
- `state/anchors/s1_poisson.json`: 1.5656334312786022 skill (0.056363 nRMSE),
  3-seed certified. `state/noise_floor.json` `ifc_poisson.min_claimable_effect`
  = **0.23990756041925798 skill units = 0.0086367 nRMSE**.
- `experiment_cards/s1_poisson/batch_2/B2.json` parts 3-7 (read in full), the
  B2 worktree family
  `worktrees/s1_poisson/B2/models_r1/mf_fno_ladder_norm/{smoke_eval.py,model.py,backbone.py,manifest.json}`
  (read `build_rows`, `run`, the ckpt/resume block and the instrumentation
  helpers), and B2's shipped outputs
  (`mffp_autoresearch_outputs/round1/s1_poisson/B2/eval/...`).
- ADRs: 0002 (0.036 denominator), 0004 (seed 0 only, provisional-single-seed),
  0005 (H100), 0007 (propose-many/screen-cheap -- reconciliation below), 0009
  (no governing equations at test time).
- Pre-falsified levers (program.md §5): WNO backbone swap, LF low-mode freezing,
  diffusion prior for point accuracy. Plus B2 part 6's in-round measured
  exclusions: interface losses, local/CNN branches, LF defect correctors,
  spectral-mode capacity, per-row loss reweighting, stage unit-continuity
  "repair".

Fixed reference lines carried into the design (all from B2 part 5/6, single
seed 0, `nrmse_def_hash d3d0ade9...`):

| line | nRMSE | skill (/0.036) |
|---|---|---|
| B2 primary `allpairs__per_level` (the frozen base) | 0.034250020008724666 | 0.9513894446867965 |
| per-sample ORACLE gain on the base (hard ceiling) | 0.022917 | 0.6366 |
| LOO-ridge gain fitted **on test targets** (upper bound only) | 0.02431 | 0.6752 |
| ONE global oracle gain on the base (measured, no help) | 0.03511 | 0.9753 |
| stream anchor (3-seed certified) | 0.056363 | 1.5656334 |
| noise floor (min claimable effect) | 0.0086367 | 0.23990756 |

## Proposal reasoning

### The question this slot must own

B2 settled the mechanism and characterised the residual: 57.10 % of the winning
arm's remaining squared error is a **per-sample scalar gain**, that gain is
0.919-R^2 linear in the 5-D condition vector, and it **cannot be fitted from the
5 HF training rows** (6 parameters, 5 points). Batch 3's only live question is
therefore the one the websearcher scored `preempted-but-MF-composition-open`:
**can the gain law be estimated on the auxiliary ladder levels (where there are
100/50/20 samples) and transferred to the top level (where there are 5)?**

### Why this is a genuine experiment either way

The literature's prior is *against* transfer -- recursive co-kriging fits a
separate rho per level ("Different fidelity levels have distinct parameter
estimates", search-return grade). So a null is not a wasted batch: it converts
B2's 0.02431 "headroom" into a measured statement that the gain is a property of
the HF solve, which closes the calibration direction on the round's flagship
dataset. The websearcher demands, and I adopt, the instrumentation that makes
the batch informative independent of the metric: **the per-level gain-law
coefficient table** ("That single table decides the mechanism regardless of
whether the nRMSE clause fires, and it is cheap").

### Getting the estimator right (the design's real content)

A naive pooled ridge on all 175 rows is *not* the right construction, and
working out why produced the design:

The gain at level f is only defined relative to an assumed output scale for that
level. I define the per-level prediction with the family's own per-level scaler,
`p_i = model([X_i, f_src, f_tgt=fnorm(f)]) * level_scaler[f]`. This is exact at
the top level because B2 T1 re-verified bit-for-bit that
`level_scaler[64] == scaler_hf == 0.0018356895307078958`, i.e. at f = 64 this IS
the scored eval path. Then the least-squares per-sample gain
`g_i = <p_i, y_i> / <p_i, p_i>` is O(1) at every level and the law splits into

```
log g_i = a_{f(i)}  +  b . X_i          (per-level constant + shared shape)
```

which is precisely the co-kriging decomposition the adversarial prior is about:
`a_f` are the "distinct per-level parameter estimates", `b` is the transfer
assumption. This yields three *different* estimators, which are the card's arms:

1. **shape transfer** (`ladder_level_intercept`, PRIMARY): `b` from levels
   8/16/32 (170 rows), `a_64` from the 5 HF train rows -- 1 parameter from 5
   points, which *is* feasible (contrast: 6 from 5, which is not). This is the
   open MF composition.
2. **full-law transfer** (`ladder_pooled`): `b` **and** one shared `a` from
   levels 8/16/32, nothing from level 64. B2 part 7's literal proposal, and the
   construction the co-kriging prior says must fail. Its predicted damage is
   computable from B2's own `ftgt_output_rms_sweep`: delivered f_tgt dynamic
   range 1.8827 vs 1.8011 required = a **4.53 %** systematic per-level constant
   mismatch, against a residual-gain std of 3.05 % -- so this arm should be
   clearly worse, and if it is NOT, the per-level constants are not distinct and
   that is a finding against the literature's prior.
3. **no transfer** (`hf_only`): `a` and `b` both from the 5 HF rows with ridge --
   LR-MFS's published default ("scale factor by least squares **on HF
   samples**"). Predicted null-or-worse, and predicted from a *measured* number:
   B2 measured that ONE global oracle gain gives 0.03511 (worse than the base
   0.034250), and a heavily-regularised 6-parameter fit on 5 points shrinks
   toward exactly that global gain.

Regularisation honesty (verdict (iv)): lambda is chosen by closed-form LOO on
**the arm's own fit rows only** -- never test targets, never the HF rows for the
ladder arms. The head is applied with a pre-registered clip g in [0.5, 2.0]
(recorded, expected never to bind: B2's test gains lie in [0.90123, 1.03765]).

**The test-free transfer predictor.** Because the same estimator can be
rehearsed inside the ladder, I require a **leave-one-LEVEL-out** measurement:
fit `b` on two of {8,16,32}, refit the held-out level's own intercept on its own
rows (the exact analogue of what arm 1 does at level 64), and report R^2 on the
held-out level's demeaned log-gains. That number predicts the clause outcome
*without touching a test target*, and it is the strongest single line the card
can carry.

**Named threat I must pre-register**: the base was trained on the very rows the
head is fitted on, so ladder gains are *in-sample* residual gains and may be
flatter than the out-of-sample test gains (std 0.03046). Mitigation is
measurement, not repair: report per-level `std(log g)` next to B2's measured test
value. A leave-one-level-out retrain is the only real fix and costs a new base
per level -- out of scope for a minutes-long batch, named as the batch-4 option.

### Sizing the clause honestly (why a null is the modal prediction)

Decompose the base's squared error at the mean-nRMSE level:
`0.034250^2 = 1.17306e-3`; structure floor `0.022917^2 = 5.2519e-4`; amplitude
part `6.4787e-4` (55.2 % -- consistent with part 6's per-sample 57.10 %, the
small difference being pooled-vs-per-sample averaging). A head capturing a
fraction R^2 of the oracle-gain variance lands near
`sqrt(5.2519e-4 + (1-R^2)*6.4787e-4)`. Setting that equal to the clause target
0.02561335 gives `(1-R^2) <= 0.2019`, i.e.

> **the clause fires iff the ladder-fitted law explains >= ~0.80 of the test-set
> oracle-gain variance, versus the 0.919 that was achievable when fitting on the
> test gains themselves.**

That is the honest framing of "the whole available effect is 0.0099-0.0113 nRMSE
against a **0.0086367** floor (~1.15-1.31x)": the head must capture ~87 % of an
upper bound that itself cheated. **My modal expectation is that F1 is
falsified** (point estimate R^2_transfer ~ 0.4 -> 0.0302 nRMSE, Delta 0.0040 =
0.47x the floor), and I say so in part 4 rather than after the fact.

### Alternatives weighed and rejected

- **K > 1 coefficient head (IFC's real construction, fixed bases + coefficient
  regression).** Rejected for this slot: the websearcher explicitly dates it to
  batch 4 ("not a batch-3 scope creep"), and it cannot be interpreted before the
  rank-1 case is measured -- if the rank-1 gain does not transfer, no higher-rank
  coefficient will either.
- **`modes_cap 12 -> 32` on `mf_fno_ladder_norm`** (motivated by s5-B1's
  cross-note: 14.6 % nRMSE on ifc_poisson for the transfer_film champion).
  Rejected: B2 part 6 measured *this* family's error as bulk- and band-0-
  dominated with every radial band improving, and B2 part 7 puts spectral-mode
  capacity on the explicit do-not-spend list for this dataset; it is also a knob,
  and the measured amplitude term (57.1 % of squared error) is the larger and
  better-characterised lever. Recorded as a batch-4 alternative because the two
  findings are on different families and are not formally reconciled.
- **Seed ensembling / variance reduction** (§12.1's other blessed direction).
  Rejected for this slot: ADR 0004 forbids in-round seeds 1-2, so an ensemble
  over seeds cannot be scored this round without violating the seed protocol.
- **A GP/kNN gain head instead of a linear one.** Rejected: B2 measured LOO kNN
  R^2 0.823-0.867 < ridge-linear 0.919 on the same targets, so the linear law is
  the better-supported functional form, and a GP would add hyperparameters that
  must then be selected without test targets.
- **Fitting the head against B2's shipped checkpoint offline** (via
  `tools/regen_preds_from_ckpt.py`). Rejected as the scored path: the scored
  number must come through `eval/score_panel.py` -> the family contract, and
  writing into a completed card's output tree would mutate B2's artifacts.
  Retained as the mechanism-analyzer's cross-check route.
- **PDE-residual correction at inference / REEF-GP.** Explicitly NOT proposed:
  ADR 0009 forbids requiring governing equations at test time, and REEF-GP "only
  quantif[ies] uncertainty and does not correct the mean prediction". Stated in
  the card so reviewers can check.
- **Making `self_only` the card's subject.** Rejected as subject, accepted as a
  non-clause arm: B2 part 7 asked for it ("55 % of F2's value is the level-graded
  row multiplicity ... never been seen at hidden 64"), it needs its own base
  (different row set, hence its own ckpt key) and ~50 s, and it cannot confound
  the calibration clauses because it carries no head and appears in no clause.

### ADR 0007 reconciliation

The arms here are not a candidate pool to screen and promote: G0 is the control
the clause is defined against, G1 is the pre-registered primary fixed before
submit, G2/G3 are the two published-estimator contrasts that give the primary
its meaning, and G4 is a non-clause measurement B2 requested. All five are
reported; nothing is selected on results. This is the same reconciliation B2's
card recorded, and it satisfies ADR 0007's guardrail ("The promoted variant's
identity is fixed in the card BEFORE the 200-epoch submit").

## Proposal

- **Category**: post-hoc per-sample gain calibration transferred across fidelity
  levels / MF composition on a frozen ladder operator.
- **Card type**: `model`.
- **Motivation** (quoting the batch-3 prior-art verdict, row (i), verbatim):
  "**`preempted-but-MF-composition-open`** ... **What remains open**: Fitting the
  calibration law **on auxiliary fidelity levels of the same ladder, supervised
  by the frozen operator's own residual there, and transferring it to the top
  level at N_hf = 5**. Every fetched MF scale estimator fits against **HF**
  observations ... Frame as a **measured MF composition of published parts**."
  The mechanism sentence, also from the verdict table: IFC represents "latent
  output as a continuous function of the input and fidelity ... multiplied with a
  basis matrix" and "the base has the joint training but **no per-sample
  coefficient factor**"; g(X) is its rank-1 amplitude-only, post-hoc case. ROMES
  is named as the preemption ("correcting the reduced-order-model output with
  this surrogate can improve prediction accuracy by an order of magnitude",
  https://arxiv.org/abs/1405.5170); the card claims "not previously reported" for
  the exact construction and never "novel method".

- **Concrete config**. New family `models_r1/mf_fno_ladder_gain`, vendored in the
  fresh B3 worktree from B2's build commit:
  `git checkout 21fdcdade463a4ceebb52a80d329790d8a401af7 -- models_r1/mf_fno_ladder_norm`
  then `git mv models_r1/mf_fno_ladder_norm models_r1/mf_fno_ladder_gain`.
  Provenance to verify before any edit (sha256-16, measured in this run):
  `backbone.py f56fa8029fad2ffb`, `model.py 740ed992efcda53e`,
  `smoke_eval.py 2f9ffd46970040db`, `manifest.json 91a853aabc96fe60`,
  `INSPIRATION.md 4a2b3230005fb9d1`. B2's frozen base checkpoint, recorded for
  provenance only (NOT read at runtime -- B3 retrains its own base so it never
  writes into a completed card's outputs): `.../B2/eval/results_allpairs__per_level/
  mf_fno_ladder_norm/ckpt_ifc_poisson_e200_s0/mode_allpairs__scal_per_level/last.pt`,
  sha256 `4800de6f8304e5a8fcc872dbe3393396b4dcc3dbf31fd7faf3832a5df0b17989`.

  Code changes (three, all additive):
  1. **`MFFP_GAIN_HEAD in {none, ladder_level_intercept, ladder_pooled, hf_only}`,
     default `none` (bit-preserving).** After the timed scored forward pass, in
     `eval()` under `no_grad` and consuming no RNG, fit the closed-form
     ridge law `log g = a_f + b.X` (X standardised by ladder-row mean/std;
     intercepts unpenalised; lambda by closed-form LOO on the arm's own fit rows,
     grid from `MFFP_GAIN_LAMBDA_GRID`), then set
     `pred = pred_base * clip(exp(a_64_used + b.X_test), MFFP_GAIN_CLIP)`.
     Per-level predictions for the fit use
     `p = model([X^{(f)}, f_src, f_tgt=fnorm(f)]) * level_scaler[f]`,
     `g_i = <p_i,y_i>/<p_i,p_i>`, with `f_src` = the scored convention
     `fnorm(lf)` (`MFFP_GAIN_FSRC=eval`, default) -- justified by B2 T3's
     measured f_src inertness (rel-L2 0.0089) and cross-checked by the
     `MFFP_GAIN_FSRC=self` sidecar. Fit rows per head: `ladder_level_intercept`
     -> slope on levels 8/16/32 (170 rows) + `a_64` from the 5 HF train rows;
     `ladder_pooled` -> shared a and b on levels 8/16/32 only; `hf_only` -> a and
     b on the 5 HF rows only. **Hard rule for the builder: the fit function
     receives train arrays only; no test target may enter the fit or the lambda
     selection.**
  2. **`MFFP_LADDER_MODE` gains one value `self_only`** (`arm_levels` = all fids,
     `arm_cross_pairs` = [] -- 175 rows, uniform multiplicity). Two lines; the
     existing ckpt key `mode_<mode>__scal_<scaler>` separates it automatically.
  3. **`MFFP_GAIN_BASE_MUST_RESUME in {0,1}`** (default 0): when 1 the run
     hard-fails unless it loaded a finished base checkpoint, so the three head
     arms provably share ONE set of base weights with the control (a paired
     contrast, not a re-trained one). Arms run in order in a single job; the
     control trains the base, the head arms resume it from the same ckpt root.
  Score-neutral instrumentation into `extra.gain_head` (every arm, including
  `none`): the **per-level coefficient table** (n, `a_f`, `b_f`, in-level R^2,
  in-level LOO R^2, mean/std/min/max of g and log g) for f = 8/16/32/64;
  the pooled fit (shared b, per-level intercepts, chosen lambda + LOO curve);
  pairwise cosine similarity among `b_8,b_16,b_32,b_64` and each vs pooled b;
  **leave-one-LEVEL-out R^2** (fit on two levels, held-out level's own intercept,
  the exact rehearsal of the primary arm); `a_64` standard error over the 5 rows;
  `g_hat` test statistics + clip fraction; rel-L2 between `pred_base` and the
  calibrated prediction; `head_fit_seconds`; the `MFFP_GAIN_FSRC=self` sidecar
  table. `preds_test.npz` additionally ships `pred_base` alongside `pred` and
  `target` so the analyzer can re-derive every number through
  `${ROUND_ROOT}/eval/nrmse.py` and `tools/residual_gain_learnability.py` without
  retraining.

  **Five arms, one SLURM job, seed 0, serial, run in this order:**

  | # | arm tag | `MFFP_LADDER_MODE` | `MFFP_GAIN_HEAD` | `MUST_RESUME` | role |
  |---|---|---|---|---|---|
  | G0 | `base__none` | allpairs | none | 0 | **control**; trains the shared frozen base; B2-continuity gate |
  | G1 | `gain__ladder_level_intercept` | allpairs | ladder_level_intercept | 1 | **PRIMARY**; in F1 and F2 |
  | G2 | `gain__hf_only` | allpairs | hf_only | 1 | LR-MFS published default; F2 comparator |
  | G3 | `gain__ladder_pooled` | allpairs | ladder_pooled | 1 | full-law transfer; co-kriging prior test; **no clause** |
  | G4 | `self_only__none` | self_only | none | 0 | B2 part 7's composition arm; **no clause** |

  `MFFP_LADDER_SCALER=per_level` in every arm. Each arm gets its own
  `ROUND1_EVAL_RESULTS=<outputs>/eval/results_<tag>` and `--out
  result_ifc_poisson_<tag>_s0.json` (B1/B2 build trap 1); G1-G3 point at the same
  ckpt root as G0 so the base weights are shared.

  **Validity gate (not a clause)**: G0 must reproduce B2's seed-0 0.034250 within
  10 % (0.030825-0.037675); B1->B2 reproduced to <0.04 %, so a miss means the
  vendoring or a knob default changed inherited behaviour and every contrast is
  suspect (ALGO, fix before reading results).

- **Recipe** (transcribed verbatim into the card):

```json
{
  "base_family": "mf_fno_ladder_norm",
  "base_commit": "21fdcdade463a4ceebb52a80d329790d8a401af7",
  "family_dir": "models_r1/mf_fno_ladder_gain",
  "datasets": "ifc_poisson",
  "epochs": 200,
  "seeds": [0],
  "env": {
    "MFFP_LADDER_MODE": "allpairs",
    "MFFP_LADDER_SCALER": "per_level",
    "MFFP_GAIN_HEAD": "ladder_level_intercept",
    "MFFP_GAIN_LAMBDA_GRID": "1e-6,1e-5,1e-4,1e-3,1e-2,1e-1,1,10",
    "MFFP_GAIN_CLIP": "0.5,2.0",
    "MFFP_GAIN_FSRC": "eval",
    "MFFP_GAIN_BASE_MUST_RESUME": "1",
    "_arms": [
      {"tag": "base__none", "MFFP_LADDER_MODE": "allpairs", "MFFP_GAIN_HEAD": "none", "MFFP_GAIN_BASE_MUST_RESUME": "0"},
      {"tag": "gain__ladder_level_intercept", "MFFP_LADDER_MODE": "allpairs", "MFFP_GAIN_HEAD": "ladder_level_intercept", "MFFP_GAIN_BASE_MUST_RESUME": "1"},
      {"tag": "gain__hf_only", "MFFP_LADDER_MODE": "allpairs", "MFFP_GAIN_HEAD": "hf_only", "MFFP_GAIN_BASE_MUST_RESUME": "1"},
      {"tag": "gain__ladder_pooled", "MFFP_LADDER_MODE": "allpairs", "MFFP_GAIN_HEAD": "ladder_pooled", "MFFP_GAIN_BASE_MUST_RESUME": "1"},
      {"tag": "self_only__none", "MFFP_LADDER_MODE": "self_only", "MFFP_GAIN_HEAD": "none", "MFFP_GAIN_BASE_MUST_RESUME": "0"}
    ],
    "_primary_arm": "gain__ladder_level_intercept",
    "_design": "one frozen base (G0 trains it, G1-G3 resume the SAME ckpt so the head contrasts are paired), three published gain-law estimators differing ONLY in which rows the law is fitted on, plus one non-clause composition arm. Head fit is CLOSED-FORM (no training, no RNG, no gradient): epochs=200 applies to the base only. All five arms are reported; the primary is fixed before submit (ADR 0007 guardrail).",
    "_sweep": "ONE SLURM job, seed 0, five score_panel.py calls in the table order, each with --env for its arm; export ROUND1_EVAL_RESULTS=<outputs>/eval/results_<tag> per arm; ckpt root shared across G0-G3 so the base weights are identical (ckpt key mode_<mode>__scal_<scaler>/last.pt, head NOT in the key because it trains nothing).",
    "_contract_check": "before submit, contract tier (2 epochs) on ifc_poisson for all five arms AND on the guard set (heat_local, fluid, sharp__sod_1d) with MFFP_GAIN_HEAD=ladder_level_intercept, to prove the head degrades gracefully on npz_l layouts and 2-level ladders (precedent: B2's results_guard e2 run). Contract numbers are plumbing, never results.",
    "_source": "vendored from branch round1/exp-s1_poisson-B2 @ 21fdcda path models_r1/mf_fno_ladder_norm (sha256-16: backbone.py f56fa8029fad2ffb, model.py 740ed992efcda53e, smoke_eval.py 2f9ffd46970040db, manifest.json 91a853aabc96fe60, INSPIRATION.md 4a2b3230005fb9d1), renamed to models_r1/mf_fno_ladder_gain. B2's frozen base ckpt sha256 4800de6f8304e5a8fcc872dbe3393396b4dcc3dbf31fd7faf3832a5df0b17989 is recorded for provenance and NOT read at runtime. akash/** and factory_root/{eval,baselines,references,scripts,data} are never touched.",
    "_sbatch": "partition gpu, --gres=gpu:h100:1 (ADR 0005), --time=02:00:00; B2 ran 5 arms in 5.6 min, B3 trains 2 bases + 3 closed-form head fits ~= 4-5 min."
  }
}
```

- **Expected outcome** (metric: `ifc_poisson` test nRMSE -> skill vs paper bar
  0.036, ADR 0002; seed 0 only, `provisional-single-seed`, ADR 0004):

  | arm | predicted nRMSE | predicted skill | basis |
  |---|---|---|---|
  | G0 `base__none` | 0.03425 (0.0308-0.0377 gate) | 0.9514 | B2 seed-0 reproduction |
  | **G1 PRIMARY** | **0.0302 (0.0240-0.0343)** | 0.839 (0.667-0.951) | structure floor 0.022917 + (1-R^2)*amplitude, R^2_transfer ~0.4 (0-0.9) |
  | G2 `hf_only` | 0.0355 (0.0335-0.0380) | 0.986 | shrinks to the measured global-gain value 0.03511 |
  | G3 `ladder_pooled` | 0.050 (0.040-0.070) | 1.39 | 4.53 % per-level constant mismatch from B2's ftgt sweep, added to a 3.4 % base error |
  | G4 `self_only__none` | 0.055 (0.035-0.075) | 1.53 | proxy 0.135253 sits 1.09x below two_level and 1.55x above allpairs; production two_level 0.078548, allpairs 0.034250 |

  - **Delta vs the operative anchor** (B2's primary, skill 0.9513894): G1
    predicted at 0.839, i.e. Delta = 0.112 skill = **0.47x the 0.23990756 floor**
    -- below the floor, so **the modal prediction is that F1 is FALSIFIED**. The
    clause fires only if the ladder-fitted law explains >= 0.798 of the test
    oracle-gain variance (arithmetic in "Sizing the clause" above).
  - **Delta vs the stream anchor** (1.5656334, 3-seed certified): every allpairs
    arm here is far better; that comparison is not what this card is about, and
    G0 already carries it from B2.
  - **Vs the noise floor**: F1 needs > 0.0086367 nRMSE = 0.23990756 skill units;
    the total available effect is 0.009940 (to the test-fitted LOO bound 0.02431)
    to 0.011333 (to the oracle 0.022917) nRMSE = **1.15-1.31x that floor**. This
    is a tight budget and a null result is the likely outcome and is still
    informative.
  - **Never claimed**: 0.02431 is an upper bound computed with test targets, not
    a prediction; and the 0.018 "stretch bar" is IFC-ODE2 extrapolating to 128^2
    (verdict (iii)), so this card does not describe it as a same-task target and
    the card carries the attribution correction as a written recommendation to
    the operator (ADR 0002 stays the denominator).
  - **Guard set**: no new obligation -- the family default stays
    `MFFP_GAIN_HEAD=none` + `MFFP_LADDER_SCALER=shared` (bit-preserving), so
    B2's owed guard run stays owed at the end-of-round confirmation; the
    contract-tier guard call in `_contract_check` is plumbing only.
  - **Cratered forewarning**: threshold 1.5 x B2's 0.9513894 = 1.4271 skill =
    0.051374 nRMSE. G3 and G4 are predicted at/above it; they are non-clause
    arms and the card's verdict keys on the primary G1 (predicted 0.839).
  - **Wall clock**: ~4-5 min/seed on one H100 (two base trainings ~76 s + ~50 s,
    three ckpt-resume + closed-form fits ~15 s each); `--time=02:00:00`.

- **Expected falsification** (two clauses; both thresholds are the certified
  floor):
  - **F1 -- transfer clause (PRIMARY).** Falsified if
    `gain__ladder_level_intercept` fails to beat `base__none` on `ifc_poisson`
    test nRMSE by more than the certified noise floor -- seed-0 skill improving
    by <= **0.23990756 skill units (<= 0.0086367 nRMSE)**, i.e. not reaching
    <= 0.0256133 nRMSE / <= 0.711481 skill -- which would mean the per-sample
    gain law measured at level 64 is not estimable from the auxiliary ladder
    levels, i.e. the gain is a property of the HF solve (or of in-sample
    residuals) that the lower levels do not share, closing the calibration
    direction for this stream.
  - **F2 -- composition clause.** Falsified if `gain__ladder_level_intercept`
    fails to beat `gain__hf_only` by more than the same floor, which would mean
    the ladder supervision adds nothing over the literature's HF-observation fit
    and the open MF composition is empirically empty on this ladder.
  - **Pre-registered reading table** (so no outcome can be re-narrated):
    F1 pass & F2 pass -> the MF composition works, ordinally, on the round's
    flagship dataset; F1 pass & F2 fail -> calibration helps but the 5 HF rows
    sufficed (LR-MFS's default is adequate at N_hf=5; the composition is empty);
    F1 fail & F2 pass -> the ladder law beats the HF-only law but neither clears
    the floor, i.e. the direction is real and below the round's resolution, not
    claimable; F1 fail & F2 fail -> calibration is not transferable at all and
    B2's 0.02431 headroom was an artifact of fitting on test targets.
  - **Mechanism decider, independent of both clauses**: the per-level coefficient
    table plus the leave-one-LEVEL-out R^2. Pre-registered reading -- slopes
    `b_8,b_16,b_32` mutually consistent (pairwise cosine >= 0.7) and consistent
    with `b_64` => the gain law's *shape* is level-transferable (a finding
    against the co-kriging prior) whatever the nRMSE says; slopes inconsistent =>
    "Different fidelity levels have distinct parameter estimates" is confirmed on
    this ladder and G1's null is explained rather than merely observed;
    per-level intercepts `a_f` differing by >> 3 % => the full-law transfer arm
    G3 must be worse, which is the quantitative version of the same prior.
    Also pre-registered: if per-level `std(log g)` on the ladder levels is much
    below B2's measured test-gain std 0.03046, the fitted law is in-sample-
    attenuated and G1's null is a base-overfit artifact, not a physics claim.

- **Anchor reference**: `"s1_poisson-B2"`. The card's control arm and frozen base
  *are* B2's primary arm, so the operative comparison is B2's 0.9513894 skill,
  and the orchestrator's batch-3 directive states `anchor_reference: s1_poisson-B2
  (batch>=2 chain)`. Noted honestly: program.md §4.5's per-stream policy makes
  `null` the default for gap streams (B2 used `null`) and the certified stream
  anchor in `state/anchors/s1_poisson.json` (1.5656334) is unchanged by this
  card; both numbers are carried in part 4 so nothing is hidden by the choice.

## Immutables self-check (program.md §5 is authoritative)

1. **Data read-only** -- PASS. The head reads only existing arrays through the
   inherited `load_mf_dataset(ds_dir, "train")` path (`cond_by_fid`,
   `field_by_fid`), opens nothing for writing under any dataset dir, adds no HF
   samples (the 5 HF train rows fit exactly ONE intercept parameter), and never
   constructs an LF field by downsampling HF -- the only resampling is the
   inherited `_to_grid` bilinear lift of each level's TARGET onto the 64x64 work
   grid, which is B1/B2's unchanged convention.
2. **Panel + guard set fixed** -- PASS. `recipe.datasets = "ifc_poisson"`, a
   panel member; the guard set appears only as a 2-epoch plumbing call with the
   project.yaml `guard` expansion, unmodified; no dataset is added or removed.
3. **Eval layer / spec untouched** -- PASS. Every edit is inside the B3 worktree
   at `models_r1/mf_fno_ladder_gain`; scoring runs the unmodified
   `${ROUND_ROOT}/eval/score_panel.py`; the proposal requires no change to
   `round1/eval/`, `project.yaml`, `program.md`, ADRs or subagent prompts (the
   0.018 attribution correction is routed as a written operator note precisely
   because ADR 0002 may not be edited in-round).
4. **One nRMSE definition** -- PASS. The head modifies the *prediction* only; the
   calibrated `pred` is handed to the same inherited `finalize_and_write(...)`
   which routes through `eval/nrmse.py`, so every arm must report
   `nrmse_def_hash d3d0ade9191c13bacc40702f3eb26ad290e01641cacee22a1d2233b74c035850`
   (B2's and the noise floor's hash) and the analyzer verifies it.
5. **Contract CLI fixed** -- PASS. `smoke_eval.py` keeps the six-argument
   signature (`--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed`)
   untouched; the five new knobs (`MFFP_GAIN_HEAD`, `MFFP_GAIN_LAMBDA_GRID`,
   `MFFP_GAIN_CLIP`, `MFFP_GAIN_FSRC`, `MFFP_GAIN_BASE_MUST_RESUME`) and the new
   `MFFP_LADDER_MODE` value are all declared in `recipe.env` above and therefore
   enter the cache key.
6. **Seeds {0,1,2} and tier epochs fixed** -- PASS. `seeds: [0]` (ADR 0004
   strict single seed), `epochs: 200` = the smoke tier, contract tier 2 for the
   plumbing check only; no full-tier run is requested; the head is closed-form so
   it consumes no epoch budget.
7. **Guarded factory surfaces untouched** -- PASS. The family is vendored from
   the round's own branch `round1/exp-s1_poisson-B2 @ 21fdcda`, not from
   `factory_root/models/` or `akash/`; the proposal writes only under
   `worktrees/s1_poisson/B3/` and `mffp_autoresearch_outputs/round1/s1_poisson/B3/`,
   and explicitly does not read or write B2's completed output tree at runtime.
8. **Checkpoint-resume from `<ckpt_dir>/last.pt`** -- PASS. The base's inherited
   `_save_ckpt`/`last.pt` staged resume (joint/finetune/done, atomic write, meta
   guard on epochs/grid/mode/scaler/seed) is unchanged and the head is deliberately
   NOT part of the checkpoint key: it trains nothing and is re-derived
   deterministically in seconds from the loaded `done` checkpoint, so a
   preemption at any point resumes exactly as B2's runs did.
9. **Falsification threshold vs the noise floor** -- PASS. Both clauses use
   `state/noise_floor.json`'s `ifc_poisson.min_claimable_effect` =
   **0.23990756041925798 skill units = 0.0086367 nRMSE** as a strict lower bound
   ("by more than"), i.e. G1 must reach <= 0.0256133 nRMSE (<= 0.711481 skill)
   against G0's 0.034250 (0.9513894). `ifc_poisson` is the only dataset cited.
10. **Not a pre-falsified lever** -- PASS. Nearest §5 entry is the **diffusion
    prior for point accuracy** (gm ~ 0.95): both target point accuracy post-hoc,
    but that lever replaced the predictive distribution with a generative prior
    trained end-to-end, whereas this is a 6-parameter closed-form multiplicative
    calibration of a frozen operator's output with no generative model and no
    backbone change. It is also none of the other two §5 entries (no backbone
    swap, no spectral-mode manipulation) and none of B2's in-round measured
    exclusions (no interface loss, no CNN/local branch, no LF-consuming defect
    corrector, no `modes_cap` change, no per-row loss reweighting, no stage
    unit-continuity edit -- B2's `shared_reweight` failure is a *training* loss
    weighting, this is a *post-hoc output* scaling of a frozen model).

## Status

- Slot **covered** (one proposal, `model` card, five arms, two clauses).
- Skipped: no.
- Reopen candidates resolved: **none exist** (B1 and B2 both `complete` with
  `reopen_candidate: false`).
- Immutables self-check: **pass (10/10)**, no revision needed -> no
  `iteration_2.md`.
