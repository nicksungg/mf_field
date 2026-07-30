# Brainstormer Report — Stream `s1_poisson`, Batch 3

**Stream**: s1_poisson (gap) · **Batch**: 3 · **Total iterations**: 1 ·
**Slot filled**: yes (1 proposal, card_type `model`) ·
**Reopen candidates resolved**: 0 of 0 (none exist)

## Slot

- **Category**: post-hoc per-sample gain calibration transferred across fidelity
  levels / MF composition on a frozen ladder operator.
- **Card type**: `model`.
- **Motivation**: B2 settled the mechanism and characterised what is left:
  **57.10 %** of the winning arm's remaining squared error is a per-sample scalar
  gain that is **0.919-R^2 linear in the 5-D condition vector** and **cannot be
  fitted from the 5 HF training rows** (6 parameters, 5 points). The websearcher
  scores exactly this construction **`preempted-but-MF-composition-open`** and
  names the open surface verbatim: "Fitting the calibration law **on auxiliary
  fidelity levels of the same ladder, supervised by the frozen operator's own
  residual there, and transferring it to the top level at N_hf = 5**. Every
  fetched MF scale estimator fits against **HF** observations ... Frame as a
  **measured MF composition of published parts**." (full row quoted below). The mechanism sentence is the benchmark paper's own: IFC represents
  "latent output as a continuous function of the input and fidelity ... multiplied
  with a basis matrix", and B2's base has IFC's joint all-level training but **no
  per-sample coefficient factor**; g(X) is its rank-1, amplitude-only, post-hoc
  case (K > 1 is explicitly dated to batch 4). ROMES is the named preemption and
  goes into the card's `prior_art`; the card claims "not previously reported" for
  the exact construction and never "novel method".
- **Concrete config**: new family `models_r1/mf_fno_ladder_gain`, vendored from
  B2's build commit `21fdcda...` (`mf_fno_ladder_norm`, sha256-16 verified:
  backbone `f56fa8029fad2ffb`, model `740ed992efcda53e`, smoke_eval
  `2f9ffd46970040db`, manifest `91a853aabc96fe60`, INSPIRATION `4a2b3230005fb9d1`)
  and renamed. Three additive code changes: (1) `MFFP_GAIN_HEAD in {none,
  ladder_level_intercept, ladder_pooled, hf_only}`, default `none`
  (bit-preserving) — a **closed-form** ridge fit of `log g = a_f + b.X` on the
  frozen operator's own per-level residual gains
  `g_i = <p_i,y_i>/<p_i,p_i>` with `p = model([X^{(f)}, f_src, f_tgt=fnorm(f)]) *
  level_scaler[f]` (exact at f=64 because B2 re-verified
  `level_scaler[64] == scaler_hf == 0.0018356895307078958`), applied as
  `pred = pred_base * clip(exp(a_64_used + b.X_test), [0.5, 2.0])`; lambda by
  closed-form LOO **on the arm's own fit rows only — no test target enters the fit
  or the lambda selection**; (2) one new `MFFP_LADDER_MODE` value `self_only`
  (all levels, no cross pairs, 175 rows); (3) `MFFP_GAIN_BASE_MUST_RESUME=1` for
  the head arms so they provably share ONE set of base weights with the control
  (paired contrast). Mandatory score-neutral instrumentation in every arm: the
  **per-level gain-law coefficient table** (a_f, b_f, R^2, in-level LOO R^2,
  mean/std/min/max of g and log g for f=8/16/32/64), pairwise cosine similarity
  among the per-level slopes, the pooled fit + chosen lambda, **leave-one-LEVEL-out
  R^2** (the test-free rehearsal of the primary estimator), `a_64` standard error,
  `g_hat` test statistics + clip fraction, an `MFFP_GAIN_FSRC=self` sidecar, and
  `pred_base` shipped inside `preds_test.npz`.
  **Five arms, one job, seed 0, serial, in this order**: `base__none` (control,
  trains the shared base, B2-continuity gate) → `gain__ladder_level_intercept`
  (**PRIMARY**: slope from levels 8/16/32, intercept from the 5 HF rows) →
  `gain__hf_only` (LR-MFS's published default: slope and intercept from the 5 HF
  rows) → `gain__ladder_pooled` (full-law transfer, no clause) →
  `self_only__none` (B2 part 7's composition arm, no clause).
  Validity gate (not a clause): the control must reproduce B2's 0.034250 within
  10 % (0.030825–0.037675).
- **Recipe**:
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
- **Expected outcome**: metric = `ifc_poisson` test nRMSE → skill vs paper bar
  0.036 (ADR 0002), seed 0 only, `provisional-single-seed` (ADR 0004).
  Control 0.03425 / 0.9514 (B2 reproduction). **Primary predicted 0.0302
  (0.0240–0.0343) = skill 0.839 (0.667–0.951)**, from the decomposition
  `nRMSE ~ sqrt(0.022917^2 + (1-R^2_transfer)*6.4787e-4)` at a modal
  `R^2_transfer ~ 0.4`. `gain__hf_only` 0.0355 (0.0335–0.0380) — it shrinks to
  the *measured* global-gain value 0.03511, which B2 showed is no help.
  `gain__ladder_pooled` 0.050 (0.040–0.070) from the 4.53 % per-level constant
  mismatch implied by B2's `ftgt_output_rms_sweep` (1.8827 delivered vs 1.8011
  required). `self_only__none` 0.055 (0.035–0.075), non-clause.
  **Delta vs the operative anchor (B2's 0.9513894 skill): +0.112 skill = 0.47x
  the floor — i.e. the modal prediction is that the primary clause is
  FALSIFIED.** Against the noise floor: the clause needs > **0.0086367 nRMSE
  (0.23990756 skill units)** while the total available effect is **0.009940**
  (to the test-fitted LOO bound 0.02431) to **0.011333** (to the per-sample
  oracle 0.022917) nRMSE — **1.15–1.31x the floor**; equivalently the clause
  fires iff the ladder-fitted law explains **>= 0.798** of the test oracle-gain
  variance versus the 0.919 achievable when fitting on the test gains themselves.
  A null result is the likely outcome and is still informative. 0.02431 is never
  written as a prediction (it used test targets); the 0.018 "stretch bar" is not
  used as a same-task target (verdict (iii)) and the attribution correction rides
  as a written operator recommendation. No new guard obligation (family defaults
  stay `head=none` + `scaler=shared`, bit-preserving); B2's guard debt stays owed
  at confirmation. Wall clock ~4–5 min on one H100, `--time=02:00:00`.
- **Expected falsification**: **F1 (primary)** — falsified if
  `gain__ladder_level_intercept` fails to beat `base__none` on `ifc_poisson` test
  nRMSE by more than the certified noise floor (seed-0 skill improving by
  <= 0.23990756 skill units = <= 0.0086367 nRMSE, i.e. not reaching
  <= 0.0256133 nRMSE / 0.711481 skill), which would mean the gain law measured at
  level 64 is not estimable from the auxiliary levels — the gain is a property of
  the HF solve (or of in-sample residuals) that the lower levels do not share.
  **F2 (composition)** — falsified if the primary fails to beat `gain__hf_only`
  by more than the same floor, which would mean the ladder supervision adds
  nothing over the literature's HF-observation fit and the open MF composition is
  empirically empty on this ladder. A 2x2 reading table for (F1, F2) and the
  mechanism-decider readings (per-level slope cosines; per-level intercept
  spread vs 3 %; ladder `std(log g)` vs B2's measured test-gain std 0.03046 as
  the in-sample-attenuation check) are pre-registered in the source iteration.
- **Prior-art verdict quoted** (verbatim from
  `websearches/s1_poisson/batch_3/report.md` "## Prior-art verdict", row (i)):
  "**(i)** Ladder-pooled per-sample **gain head** g(X) on the frozen
  `allpairs__per_level` base — head fitted on the **175 pooled ladder rows**
  (supervision = the frozen operator's residual at levels 8/16/32), applied at
  fidelity 64 where N_hf = 5 | **`preempted-but-MF-composition-open`** | ROMES:
  GP from cheap indicators to the error distribution; "correcting the
  reduced-order-model output with this surrogate can improve prediction accuracy
  by an order of magnitude" — https://arxiv.org/abs/1405.5170 ·
  multiplicative/comprehensive correction `y^HF = rho(x)·yLF(x)[+delta(x)]`, rho
  "an SM created from the ratio between the HFM and the LFM" —
  https://arxiv.org/html/1609.07196v5 · LR-MFS: scale factor by least squares
  **on HF samples** — https://arxiv.org/abs/1705.02956 · IFC: "latent output as a
  continuous function of the input and fidelity … multiplied with a basis matrix"
  (g(X) = the K=1 case) — https://ar5iv.labs.arxiv.org/html/2207.00678 · MF-POD
  coefficient regression — https://pmc.ncbi.nlm.nih.gov/articles/PMC10100049/ ·
  APEX per-sample amplitude anchor from a coarser operator in target-scarce MF —
  https://arxiv.org/abs/2605.26732 | Fitting the calibration law **on auxiliary
  fidelity levels of the same ladder, supervised by the frozen operator's own
  residual there, and transferring it to the top level at N_hf = 5**. Every
  fetched MF scale estimator fits against **HF** observations; ROMES's features
  are residual norms (not the condition vector) and its errors are HF-evaluated;
  REEF-GP fits frozen-operator residuals but "only quantif[ies] uncertainty and
  does not correct the mean prediction" (https://arxiv.org/abs/2606.17513);
  2210.03008 corrects the mean from the **PDE residual at inference**, not a
  fitted law (https://arxiv.org/abs/2210.03008). Frame as a **measured MF
  composition of published parts**."
  Also carried into the card: verdict (ii) "**`novel` (narrow, weak)** — say "not
  previously reported", never "novel method"" plus its adversarial prior
  ("recursive co-kriging fits **a separate rho per level**", "Different fidelity
  levels have distinct parameter estimates", search-return grade); verdict (iv)
  "report as an upper bound only". The card states explicitly that it is **not**
  REEF-GP and **not** PDE-residual correction at inference (also required by
  ADR 0009, which the design satisfies: no governing equation is used at test
  time — only the condition vector and the frozen operator).
- **Immutables self-check**: **pass (10/10)** on the first iteration, nothing
  flagged, no revision. Positive evidence for each of the 8 immutables plus the
  two round-1 extras is written out in the source iteration; the load-bearing
  ones: data read-only (fit consumes only `load_mf_dataset(..., "train")` arrays;
  the 5 HF rows fit exactly ONE parameter; no HF added; no LF built by
  downsampling), one nRMSE definition (the head changes the prediction, not the
  metric — `nrmse_def_hash d3d0ade9…` must match B2 and the floor), contract CLI
  fixed (six args untouched; all five new knobs declared in `recipe.env`),
  checkpoint-resume (the head is deliberately not in the ckpt key because it
  trains nothing and is re-derived deterministically from the loaded `done`
  checkpoint), floor (both clauses use 0.23990756 skill units = 0.0086367 nRMSE
  as a strict lower bound on the single cited dataset), not-a-pre-falsified-lever
  (nearest is the diffusion prior for point accuracy, gm ~ 0.95 — that replaced
  the predictive distribution with an end-to-end generative prior; this is a
  6-parameter closed-form multiplicative calibration of a frozen output, and it
  is none of B2's in-round measured exclusions either).
- **Anchor reference**: `"s1_poisson-B2"` (per the orchestrator's batch-3
  directive for the batch>=2 chain; the card's control arm *is* B2's primary arm,
  so 0.9513894 skill is the operative comparison). Noted honestly: program.md
  §4.5's per-stream policy defaults gap streams to `null` (B2 used `null`) and the
  certified stream anchor `state/anchors/s1_poisson.json` = 1.5656334 is unchanged
  by this card; part 4 carries both numbers so the choice hides nothing.
- **Source iteration**: [iteration_1.md](iteration_1.md)

## Reopen candidates

| Candidate | Verdict (retry/drop) | Eased conditions | Source iteration |
|---|---|---|---|
| *(none — B1 and B2 are both `status: complete` with `reopen_candidate: false`; no s1_poisson slot has ever been skipped)* | n/a | n/a | [iteration_1.md](iteration_1.md) |

## Skipped slot

Not applicable — the slot is filled.

## Summary table

| Slot | Category | One-liner | Status |
|---|---|---|---|
| s1_poisson-B3 | post-hoc per-sample gain calibration transferred across fidelity levels (MF composition on a frozen ladder operator) | Fit `log g = a_f + b·X` on the frozen base's own residual gains at ladder levels 8/16/32, transfer the shape `b` to level 64 and take only the intercept from the 5 HF rows; contrast against the literature's HF-only fit and against full-law transfer; the per-level coefficient table decides the mechanism whether or not the nRMSE clause fires | filled (`model`, 5 arms, 2 clauses, ~4–5 min H100) |

### Notes for downstream agents

1. **Honesty pre-registration**: the modal prediction is that F1 is falsified
   (0.47x the floor). The card must be written so that outcome is a finding, not
   a failure — the deciding artifact is the per-level coefficient table plus the
   leave-one-LEVEL-out R^2, both of which are computed without test targets.
2. **Builder hard rule**: the head-fit function must receive train arrays only;
   no test target may enter the fit or the lambda selection. The oracle ceiling
   (0.022917) stays a part-6 measurement from the shipped `preds_test.npz`, never
   an in-family computation.
3. **Operator note owed** (verdict (iii), program.md §13.4 written
   recommendation, no action): `docs/adr/0002-ifc-poisson-skill-reference.md`
   mis-attributes the 0.018 stretch bar — the fetched paper places 0.018 at
   m = 2.14 = 128^2 **extrapolation** for **IFC-ODE2**, not IFC-GPODE at 64^2.
   0.036 remains this round's denominator.
4. **Deferred to batch 4** (recorded so they are not lost): the K > 1 coefficient
   head with fixed bases (IFC's actual construction); a leave-one-level-out
   *retrain* if the in-sample-attenuation check fires; and reconciling s5-B1's
   "modes_cap 12→32 worth 14.6 % nRMSE on ifc_poisson" (measured on
   transfer_film) against B2's spectral-capacity exclusion (measured on
   `mf_fno_ladder_norm`).
5. **Summary length disclosure**: `summary_so_far.md` is ~1780 words, over the
   500–1200 guidance, because §1 and §2 carry the mandated verbatim verdict and
   §12.1 quote blocks.
