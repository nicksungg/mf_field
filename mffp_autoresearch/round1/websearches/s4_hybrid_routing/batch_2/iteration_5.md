# Iteration 5 — FINAL (5-of-5 cap hit): retrieval-grounded verdicts

**Cap note**: this is iteration 5 of the 5 allowed. No further searching.

## Search rationale

Three last adversarial terms, one per mandated verdict, each phrased to find the
paper that KILLS the direction: (1) a published identity-safe / no-harm gated
corrector for neural operators with a validation-selected weight; (2) any
published ablation of LF-context size in MF operator learning; (3) any
attention-vs-convolution head-to-head on the exact PDE family of our panel
(phase-field / Cahn-Hilliard / Allen-Cahn).

## Search terms used

1. `identity-safe residual correction guaranteed not worse than base model gate scalar nested cross-validation neural operator surrogate no-harm`
2. `number of low-fidelity points sampled as input multi-fidelity operator learning accuracy versus context size coarse grid coverage ablation`
3. `phase field Cahn-Hilliard Allen-Cahn interface neural operator attention transformer versus convolutional U-Net comparison accuracy benchmark`

## Findings

### Term 1 — DIRECT HIT: the shrinkage-with-zero gate is PUBLISHED for neural operators (FETCHED)
- **"Operator Boosting Produces Pareto-Efficient PDE Surrogates"**,
  https://arxiv.org/html/2606.17460 — **FETCHED.** Verbatim from the fetch: the
  stage-`m` weight is chosen as
  `eta_m in argmin_{eta in Lambda} (1/N_val) sum_j || G_{m-1}(a_j^val) + eta*H_m(a_j^val) - u_j^val ||_2^2`,
  the shrinkage grid `Lambda` **includes `eta = 0`**, and this makes *"each stage
  validation-safe: if a trained correction does not reduce validation error, it
  can be rejected."* Base predictor is `G_0(a) = 0` in normalized coordinates,
  i.e. *"the empirical mean output field"* — the fetch states plainly *"This is
  **not** multi-fidelity ... No auxiliary solver is involved."* No monotone
  guarantee: *"several PDE-architecture pairs exhibit negative mean gains"*
  (e.g. *"CNO on 2D Navier-Stokes shows -202% error change"*), and *"success
  depends on whether the remaining residual is representable by the tiny
  correction class."*
  **On the split question — the exact defect s4-B1 found — the fetch reports the
  paper says only that all models use *"the same train/validation/test splits
  within each dataset"* and *"does not explicitly confirm whether validation data
  is withheld from previous full-size baseline training."*** So the published
  method shares the hazard and does not address it.
  Consequence: **LICENSED-1's estimator is preempted mechanism-for-mechanism**
  (validation-selected shrinkage with 0 in the grid, for neural-operator residual
  correction). What is not published is the *diagnosis* — that this exact
  estimator silently inverts when the base memorises the validation split — nor
  its MF instance.
- **"No-Harm Physics-Informed Inverse Learning with Residual-Calibrated
  Uncertainty"** (Katende), https://arxiv.org/pdf/2606.07153 — **FETCH FAILED**
  (895 KB PDF, only metadata decodable; title/author/arXiv-id confirmed). Its
  no-harm framing is therefore cited only as a *search-return*: the engine
  summarised it as allowing *"the learned output to replace a baseline only when
  its certified radius is no worse than the baseline radius ... If this condition
  fails, the method falls back to the baseline"*. Title says *Physics-Informed*
  and the fetch's metadata note says *"the title suggests the approach integrates
  physics (PDE residuals)"* ⇒ ADR-0009 (unknown physics) would disqualify that
  route for us anyway. **Not usable as a citation for a mechanism claim.**
- Also returned (search-returns, not fetched, all previously seen in s6-B2):
  ANCHOR https://arxiv.org/pdf/2512.19643 , residual-based error correctors
  https://arxiv.org/abs/2306.12047 , https://arxiv.org/pdf/2210.03008 ,
  MFRNP https://arxiv.org/pdf/2402.18846 .

### Term 2 — No usable results: MF operator learning has no LF-context-size ablation
- Returns were the standard MF operator-learning cluster: MF DeepONet
  https://arxiv.org/pdf/2204.06684 , https://arxiv.org/abs/2204.09157 ,
  discretization-independent MF operator learning https://arxiv.org/pdf/2507.07292
  (already fetched in batch 1), DeepONet MF residual ROM
  https://amses-journal.springeropen.com/articles/10.1186/s40323-023-00249-9 ,
  in-context multi-operator learning https://arxiv.org/pdf/2512.16074 ,
  context-aware MF hierarchies
  https://www.sciencedirect.com/science/article/abs/pii/S0045782523000312 .
  The only quantity anyone ablates is the **NUMBER OF LF SAMPLES** (engine
  summary: *"when the high-fidelity data is fixed, the overall predictive accuracy
  ... gradually increases with the increase in the number of low-fidelity data"* —
  https://arxiv.org/pdf/2511.11361), never the **spatial density of the LF field
  presented to the model**. **No usable results** — fourth independent negative
  on dense-LF-context (iter 2 term 3, iter 4 term 2, batch-1's LGFNet query, here).

### Term 3 — on OUR PDE family, LOCAL beats SPECTRAL and attention is ABSENT (FETCHED)
- **"Equivariant U-Shaped Neural Operators for the Cahn-Hilliard Phase-Field
  Model"**, https://arxiv.org/html/2509.01293v3 — **FETCHED.** Verbatim:
  *"Both E-UNO and UNO consistently achieve errors an order of magnitude lower
  than FNO"* on Cahn-Hilliard, and E-UNO reduces the max relative-L2 error
  *"by 34.32% compared to UNO at early stages where the evolution is dramatic"*
  (~11% lower free-energy deviation). Critically, per the fetch, the paper
  *"does **not** include any attention or transformer-based baseline"* —
  comparisons are FNO vs UNO variants only.
- Also returned (not fetched): U-SCANO, a U-shaped **spatial-channel attention**
  neural operator for Navier-Stokes-Cahn-Hilliard-heat
  https://www.sciencedirect.com/science/article/abs/pii/S1007570425009463 (the
  nearest published attention-on-Cahn-Hilliard artifact — but channel/spatial
  attention inside a U-Net, not a cross-attention corrector, and paywalled);
  PINO on coupled Allen-Cahn/Cahn-Hilliard https://arxiv.org/pdf/2507.18731 ;
  DeepRitzSplit https://arxiv.org/pdf/2604.18261 .

## THE PRIOR-ART VERDICTS

### (i) Properly-split shrinkage gate fitting for MF correctors
**`preempted (cite)` — for the estimator; the DIAGNOSIS is what is open.**
- Preempting the estimator: https://arxiv.org/html/2606.17460 (fetched) —
  validation-selected shrinkage over a grid containing 0, per residual-correction
  stage, for neural operators, explicitly *"validation-safe"*.
- Preempting the split rule: Wolpert 1992 via the fetched
  https://arxiv.org/pdf/1106.1684 (s6-B2 iteration 4) — *"the combiner must be
  trained on predictions from base classifiers applied to held-out data"*.
  Statistical shrinkage theory adds https://arxiv.org/html/2309.09880 (fetched:
  `sum alpha_hat <= 1`; conditional risk beat over the data-selected best single
  model) and https://arxiv.org/html/2309.14596 (fetched: *"combining two linear
  smoothers by minimizing Mallows' Cp yields a James-Stein estimator"*).
- **What remains open**: (a) no fetched source is multi-fidelity — Operator
  Boosting's base is the empirical mean, not a coarse solve; (b) no fetched source
  states that the shrinkage selection **inverts** when the base has memorised the
  scoring split, nor that the failure is one-sided (always toward `eta = 0`) —
  Operator Boosting *"does not explicitly confirm whether validation data is
  withheld from previous full-size baseline training"*; (c) B1's measurement that
  the wrongly-vetoed weight was the test optimum to 0.9% (−43% error, skill
  5.56→3.16) has no published analogue. **A card must claim ZERO novelty for the
  gate and frame the contribution as a protocol-defect measurement with a
  quantified cost**, citing 2606.17460 as the published instance of the same
  estimator that shares the hazard.

### (ii) Dense-LF-context attention correction at few/moderate HF samples
**`preempted-but-MF-composition-open (cite)`.**
- Preempting the *knob*: https://arxiv.org/html/2502.09692v3 (fetched, AB-UPT) —
  *"Increasing M enhances contextual information available at each query location
  ... thereby improving performance up to a saturation point"*. Preempting the
  *reading* of what such a decoder does: WorldParticle
  https://arxiv.org/pdf/2605.15305 (search-return) — cross-attention from a sparse
  anchor set is *"a learned coarse-to-fine lifting where attention weights act as
  data-adaptive interpolation weights"*. Nearest MF neighbour remains batch 1's
  LGFNet https://arxiv.org/abs/2603.29303 (LF as low-frequency carrier + local
  window + global self-attention, fidelity-gap delta).
- **What remains open**: no fetched source ablates the **spatial coverage of a
  coarse-solve LF field used as attention context** for a fidelity-gap corrector
  at N_hf on the order of tens; four independent searches returned only
  *LF-sample-count* ablations. **But the honest prediction from the same sources
  is unfavourable**: saturation (AB-UPT) plus the interpolation reading
  (WorldParticle) plus B1's own anatomy (correction ⟂ `hf − copylf`, cosine ≤0.02)
  all say denser context mainly makes the corrector a *better LF interpolator*,
  i.e. it walks toward the skill-1.0 ceiling rather than through it. Any card must
  pre-register that ceiling and a control that already attains it
  (`base + a*(copylf − base)`, B1 F13), or it is buying a known result.
  **Cross-stream**: s6 owns dense-LF *local* correction, so s4's version is only
  defensible as the **attention arm of a matched comparison** (see (iii)).

### (iii) Attention vs local filter for defect correction
**`novel` — as a measurement; and the prior is HOSTILE to attention.**
- Nearest neighbours, all fetched, none of which does the comparison:
  https://arxiv.org/html/2411.00040 (P2C2Net — coarse-correction ablation table,
  regular conv 0.1450 vs symmetric conv 0.0064, Fourier-block removal 0.1463;
  the fetch states it *"does not employ attention mechanisms anywhere ... nor does
  it compare attention-based approaches against convolutional or spectral
  methods"*); https://arxiv.org/html/2509.01293v3 (on Cahn-Hilliard *"Both E-UNO
  and UNO consistently achieve errors an order of magnitude lower than FNO"*, and
  *"does not include any attention or transformer-based baseline"*);
  https://arxiv.org/html/2511.09729v1 (four-way emulator comparison whose winner
  is *"a deep FiLMed residual network with spectral convolutions"*, attention only
  as channel modulation in LSC-FNO); https://arxiv.org/abs/2605.08318 (the one
  attention-beats-Fourier result, scoped by its own title to *"irregular
  domains"*, 3.7x on Heat2D-CG — our panel is regular grids, so it does not
  transfer); https://arxiv.org/abs/2511.06294 (fetched — Physics-Attention *"can
  be reformulated as a special case of linear attention, and ... the slice
  attention may even hurt the model performance"*, gains coming from
  *"the slice and deslice operations themselves"*).
- **What remains open / what to claim**: a **matched-budget head-to-head between
  a cross-attention corrector and a local (convolutional / LSI-filter) corrector
  on the SAME fidelity-gap residual target on regular sharp-interface grids** is
  in no fetched source. That is s4's uniquely-owned measurement. Frame it as
  *testing a hostile prior*: the fetched evidence predicts attention LOSES, and
  arXiv:2511.06294 supplies the mechanism for why (the attention part isn't doing
  the work; the slice/deslice pooling is). B1's fisher_kpp band-1 datapoint is the
  only pro-attention evidence anywhere in this loop, and term 3 of iteration 3
  found **no** published support for "nonlinear fronts need a nonlocal corrector".

## Interpretation

Two of the three directions are estimator-preempted (i, ii) and must claim zero
mechanism novelty; the third (iii) is a genuinely open comparison that the
fetched literature predicts s4 will LOSE — which under program.md §1 is the most
genuine experiment available to this stream, because either outcome kills or
promotes the whole attention-corrector class it owns.
