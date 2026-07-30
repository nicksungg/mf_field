# Websearch Report — Stream `s1_poisson`, Batch 3

**Stream**: s1_poisson (gap) · **Batch**: 3 · **Total iterations**: 5 ·
**WebSearch calls**: 15 (3 per iteration, cap-respecting) ·
**WebFetch calls**: 12 attempted / **12 usable** (0 failures — every fetch used
`arxiv.org/abs`, `arxiv.org/html`, **ar5iv**, `pmc.ncbi.nlm.nih.gov`,
`scikit-learn.org` or `raw.githubusercontent.com`, per the batch-1/2 dead-end
rules; ScienceDirect / Springer / OpenReview / arXiv `/pdf` were never attempted) ·
**Cap hit**: **YES** (5 of 5, noted in `iteration_5.md`)

**Headline**: the round finally has a **first-hand fetch of the benchmark paper's
body** (via ar5iv, a route no prior batch tried), and it says the **0.018 stretch
bar is IFC-ODE2 extrapolating to a 128^2 mesh, not IFC-GPODE at 64^2** — contra
`docs/adr/0002-ifc-poisson-skill-reference.md`. Separately, the B3 gain head has a
**named, fetched preemption** (ROMES) that batches 1-2 never surfaced.

## Search trace

### Turn 1 — task (a): is a post-hoc per-sample output-calibration head published?
Terms: `post-hoc multiplicative bias correction head frozen surrogate model per-sample
scalar gain predicted from input parameters`; `neural operator output amplitude
calibration head predict per-sample scaling factor from PDE parameters`; `learned
output rescaling head trained on auxiliary cheap data applied to expensive target
regression calibration transfer`. Chosen to characterise the *object* before any
MF specificity, and to fetch APEX first-hand (s5-B2 flagged it as the top threat).
- APEX's anchor is a **field** retained from a coarser operator's **prediction**, in a
  frequency-fidelity setting: "A lower-frequency neural operator first provides a
  coarse prediction … from which we retain only the amplitude as a transferable
  structural anchor"; setting is "higher-frequency prediction under scarce target
  supervision" [cite: https://arxiv.org/abs/2605.26732 (fetched)] → iteration_1.md
- The borrow-strength-for-per-sample-correction idiom exists outside PDE ML (fSVA
  "borrows strength from a training set for individual sample batch correction")
  [cite: https://arxiv.org/abs/1301.3947 (search-return)] → iteration_1.md
- Engine negative: no source with an "output amplitude calibration head" for
  operators; what exists is parameter-conditioned scaling **inside** spectral layers
  (= the FiLM conditioning the base already has) → iteration_1.md

### Turn 2 — task (b): on which data is an MF scale parameter estimated?
Terms: `multi-fidelity estimate scale factor rho on low-fidelity data transfer to high
fidelity few samples hierarchical borrowing strength calibration parameter`; `bridge
function multiplicative correction … recursive co-kriging level-dependent scale`;
`scale factor estimated using low-fidelity samples because high-fidelity samples
insufficient …`. Chosen because B2 established the *object* rho but never the
*estimator*, and the card's entire novelty hinges on the estimator's data.
- The classical multiplicative/comprehensive correction: "y^HF = rho(x)·yLF(x)",
  "y^HF = rho(x)·yLF(x) + delta(x)", rho being "an SM created from the ratio between
  the HFM and the LFM" [cite: https://arxiv.org/html/1609.07196v5 (fetched)]
  → iteration_2.md
- LR-MFS: the scale factor is **constant** and "obtained simultaneously using linear
  regression" minimising "the prediction errors **at high-fidelity samples**"
  [cite: https://arxiv.org/abs/1705.02956 (fetched)] → iteration_2.md
- The archetype of the card's argument, in statistics: "the HF quantile is represented
  as a low-fidelity (LF) quantile evaluated at a covariate-dependent level … This
  reformulation reduces the problem to estimating the level function, which can be
  smoother than the HF quantile itself" [cite: https://arxiv.org/abs/2605.10406
  (fetched)] → iteration_2.md
- Adversarial: "**Different fidelity levels have distinct parameter estimates**"
  (recursive co-kriging cluster: https://arxiv.org/abs/1210.0686,
  https://royalsocietypublishing.org/doi/10.1098/rspa.2015.0018 — search-return)
  → iteration_2.md

### Turn 3 — task (c): small-N honesty + post-hoc fitting on a frozen operator
Terms: `calibration with very small calibration set n=5 unreliable leave-one-out
estimate optimistic overfitting regression rescaling`; `post-hoc error correction model
trained on residuals of frozen neural operator …`; `train correction model on
intermediate fidelity levels apply at highest fidelity level …`.
- "In this example the training set was intentionally kept very small. In this setting,
  optimizing the log-loss can still lead to poorly calibrated models **because of
  overfitting**"; and poor calibration "is bound to happen when the training size is
  too small" [cite: https://scikit-learn.org/stable/auto_examples/calibration/plot_compare_calibration.html
  (fetched)] → iteration_3.md
- REEF-GP fits a GP to "the residuals (prediction errors) of a frozen neural
  operator" but "**only quantif[ies] uncertainty and does not correct the mean
  prediction**" [cite: https://arxiv.org/abs/2606.17513 (fetched)] → iteration_3.md
- Residual-based error correction **does** correct the mean, but "by solving a linear
  variational problem based on the **PDE residual**" at inference — "quadratic
  reduction of its approximation error" [cite: https://arxiv.org/abs/2210.03008
  (fetched)] → iteration_3.md
- Engine negative: MF discrepancy models are fitted "on the residuals between the
  scaled low-fidelity predictions and **high-fidelity data**"; nothing fits a
  correction supervised only by lower levels → iteration_3.md

### Turn 4 — task (d): the benchmark paper itself (ar5iv breakthrough)
Terms: `Infinite-Fidelity Coregionalization IFC-GPODE Li Zhe neural ODE fidelity Poisson
nRMSE results table`; `"Infinite-Fidelity Coregionalization" latent output basis matrix
… training all fidelity data jointly`; `"IFC-ODE2" extrapolation "2.14" 128x128 mesh …`.
- Mechanism, first-hand: latent fidelity ODE "dh(m,x)/dm = phi(m,h(m,x),x)";
  **GPODE** = "b_ij(m) ~ GP(0, kappa(m,m'))" (best at m=1, degrades for m>1);
  **ODE2** = "db_ij(m)/dm = gamma(b_ij,m)" (better extrapolation); joint likelihood
  "p(Y|X) = prod_n N(y_n | B_n h(m_n,x_n), sigma^2 I)"; Poisson ladder
  "8x8, 16x16, 32x32 and 64x64" [cite: https://ar5iv.labs.arxiv.org/html/2207.00678
  (fetched twice, targeted)] → iteration_4.md
- **Attribution resolved**: "nRMSE of IFC-ODE2 at m=1 and m=2.14 is 0.036 vs. 0.018"
  with "m=2.14 corresponds to a 128x128 mesh, representing extrapolation beyond the
  highest training fidelity (m=1, 64x64 mesh)"; corroborated independently by a
  search-return over https://arxiv.org/pdf/2207.00678 ("The value 2.14 corresponds to
  a mesh of size 128x128"; "IFC-ODE^2 showing better performance when m > 1")
  → iteration_4.md
- Authors' repo confirms the two variants and the tensor-Gaussian variational
  posterior but gives no per-fidelity sample counts
  [cite: https://raw.githubusercontent.com/shib0li/Infinite-Fidelity-Coregionalization/main/README.md
  (fetched)] → iteration_4.md

### Turn 5 — refutation pass + verdicts (CAP)
Terms: `predict per-sample scalar coefficient amplitude of neural operator prediction
learned from lower resolution training data multi-fidelity rank-one correction`;
`multi-fidelity POD coefficient regression predict modal coefficients from parameters
coarse mesh snapshots applied to fine mesh few high fidelity snapshots`; `ROMES method
error surrogate predict reduced order model error from indicators …`.
- **ROMES** — the loop's strongest preemption: "Gaussian-process regression" maps
  "computationally inexpensive 'error indicators'" to "a distribution over the true
  error", and "**correcting the reduced-order-model output with this surrogate can
  improve prediction accuracy by an order of magnitude**", explicitly contrasted with
  "existing 'multifidelity correction' approaches"
  [cite: https://arxiv.org/abs/1405.5170 (fetched)] → iteration_5.md
- Parameter -> per-sample-coefficient regression with a fixed basis, fused across
  fidelities, is standard in MF-POD: "The low-fidelity is built by extending on the
  whole parameter space a one-dimensional response surface constructed over the AS
  corresponding to each POD coefficient" [cite: https://pmc.ncbi.nlm.nih.gov/articles/PMC10100049/
  (fetched)] → iteration_5.md
- Explicit negative: no source predicts a **per-sample scalar amplitude** for a
  trained operator's output → iteration_5.md

## Prior-art verdict

| Candidate direction | Verdict | Citations (fetched in THIS loop unless marked) | What remains open |
|---|---|---|---|
| **(i)** Ladder-pooled per-sample **gain head** g(X) on the frozen `allpairs__per_level` base — head fitted on the **175 pooled ladder rows** (supervision = the frozen operator's residual at levels 8/16/32), applied at fidelity 64 where N_hf = 5 | **`preempted-but-MF-composition-open`** | ROMES: GP from cheap indicators to the error distribution; "correcting the reduced-order-model output with this surrogate can improve prediction accuracy by an order of magnitude" — https://arxiv.org/abs/1405.5170 · multiplicative/comprehensive correction `y^HF = rho(x)·yLF(x)[+delta(x)]`, rho "an SM created from the ratio between the HFM and the LFM" — https://arxiv.org/html/1609.07196v5 · LR-MFS: scale factor by least squares **on HF samples** — https://arxiv.org/abs/1705.02956 · IFC: "latent output as a continuous function of the input and fidelity … multiplied with a basis matrix" (g(X) = the K=1 case) — https://ar5iv.labs.arxiv.org/html/2207.00678 · MF-POD coefficient regression — https://pmc.ncbi.nlm.nih.gov/articles/PMC10100049/ · APEX per-sample amplitude anchor from a coarser operator in target-scarce MF — https://arxiv.org/abs/2605.26732 | Fitting the calibration law **on auxiliary fidelity levels of the same ladder, supervised by the frozen operator's own residual there, and transferring it to the top level at N_hf = 5**. Every fetched MF scale estimator fits against **HF** observations; ROMES's features are residual norms (not the condition vector) and its errors are HF-evaluated; REEF-GP fits frozen-operator residuals but "only quantif[ies] uncertainty and does not correct the mean prediction" (https://arxiv.org/abs/2606.17513); 2210.03008 corrects the mean from the **PDE residual at inference**, not a fitted law (https://arxiv.org/abs/2210.03008). Frame as a **measured MF composition of published parts**. |
| **(ii)** The exact construction (frozen MF operator + per-sample scalar output gain + supervision only from lower levels + N_hf = 5) | **`novel` (narrow, weak)** — say "not previously reported", never "novel method" | Nearest neighbours, in order: https://arxiv.org/abs/1405.5170 (ROMES) · https://arxiv.org/abs/2605.10406 (MF quantile-link: replace HF-scarce estimation with a *smoother* covariate-dependent link borrowed across fidelities) · https://arxiv.org/abs/2605.26732 (APEX: amplitude, but a field from a prediction) · https://arxiv.org/abs/1301.3947 (fSVA borrow-strength idiom, search-return) | Nothing found combining (a)-(d). **But the transfer assumption is the experiment**, and the literature's prior is against it: recursive co-kriging fits **a separate rho per level** and "Different fidelity levels have distinct parameter estimates" (search-return, iteration_2); the review's rho(x) is defined level-pair-wise. Pre-register the negative reading exactly as B2 part 7 demands. |
| **(iii)** The 0.018 stretch bar / IFC gap analysis | **attribution `mis-stated` in the round's own docs; mechanism gap nameable** | https://ar5iv.labs.arxiv.org/html/2207.00678 (fetched): "nRMSE of IFC-ODE2 at m=1 and m=2.14 is 0.036 vs. 0.018"; "m=2.14 corresponds to a 128x128 mesh, representing extrapolation beyond the highest training fidelity (m=1, 64x64 mesh)"; IFC-GPODE "smallest error at m=1 … performance drops when m>1"; corroborating search-return over https://arxiv.org/pdf/2207.00678 | **0.018 is ODE2 at 128^2 extrapolation**, i.e. a different task from our 64^2 test split, and it is not GPODE's — contra `docs/adr/0002-ifc-poisson-skill-reference.md`. ADRs are immutable in-round: keep 0.036 as denominator, cite this, and route the correction to the operator as a written note. **Structural gap**: IFC = per-sample fidelity-continuous latent coefficients x shared fidelity-varying bases under one joint likelihood; the base has the joint training but **no per-sample coefficient factor**. g(X) is its rank-1 amplitude-only case; a K>1 coefficient head with fixed bases is the indicated batch-4 successor, not a batch-3 scope creep. |
| **(iv)** Reporting the LOO headroom 0.02431 as an achievable target | **`preempted` methodological warning — report as an upper bound only** | https://scikit-learn.org/stable/auto_examples/calibration/plot_compare_calibration.html (fetched): small calibration sets "can still lead to poorly calibrated models **because of overfitting**"; poor calibration "is bound to happen when the training size is too small". Mitigation shown in the same source is cross-validated regularization | Nothing novel. The card must keep part 6's own label ("the LOO fit uses the test targets, so 0.0243 is an upper bound on a calibration head, not a score"), regularize the fitted head, and choose the regularization strength without touching test targets. |

## Citations summary

- [Drohmann & Carlberg 2015] "The ROMES method for statistical modeling of reduced-order-model error" (SIAM/ASA JUQ) — https://arxiv.org/abs/1405.5170 (**fetched**); mirrors seen not fetched: https://epubs.siam.org/doi/10.1137/140969841 — used in: iteration_5, verdicts (i)/(ii)
- [Li, Wang, Kirby, Zhe 2022] "Infinite-Fidelity Coregionalization for Physical Simulation" (NeurIPS 2022) — **https://ar5iv.labs.arxiv.org/html/2207.00678 (fetched, TWICE, targeted — the round's first successful fetch of this paper's body)**; abs https://arxiv.org/abs/2207.00678; repo https://raw.githubusercontent.com/shib0li/Infinite-Fidelity-Coregionalization/main/README.md (**fetched**, low yield) — used in: iteration_4, verdicts (i)/(iii)
- [Fernández-Godino et al.] "Review of multi-fidelity models" — https://arxiv.org/html/1609.07196v5 (**fetched**) — used in: iteration_2, verdict (i)
- [Zhang, Kim, Park et al. 2017] "Multi-Fidelity Surrogate Based on Single Linear Regression" (LR-MFS) — https://arxiv.org/abs/1705.02956 (**fetched**) — used in: iteration_2, verdict (i)
- [Liu & Zhang 2026] "Multi-fidelity quantile regression via a local quantile link" — https://arxiv.org/abs/2605.10406 (**fetched**) — used in: iteration_2, verdict (ii)
- [Vendrell-Gallart, Negarandeh & Bostanabad 2026] "REEF-GP: post-hoc GP on a frozen operator's residuals" — https://arxiv.org/abs/2606.17513 (**fetched**) — used in: iteration_3, verdict (i)
- [Cao, O'Leary-Roseberry, Jha, Oden, Ghattas 2023] "Residual-based error correction for neural operator accelerated infinite-dimensional Bayesian inverse problems" — https://arxiv.org/abs/2210.03008 (**fetched**); mirrors https://www.osti.gov/pages/biblio/2421120 — used in: iteration_3, verdict (i)
- [APEX 2026] "Amplitude Anchors and Phase Priors for Target-Scarce Higher-Frequency Wave Prediction" — https://arxiv.org/abs/2605.26732 (**fetched**) — used in: iteration_1, verdicts (i)/(ii)
- [Tezzele et al. 2023] "A multifidelity approach coupling parameter space reduction and non-intrusive POD …" — https://pmc.ncbi.nlm.nih.gov/articles/PMC10100049/ (**fetched**); arXiv mirror https://arxiv.org/pdf/2206.01243 (not fetched) — used in: iteration_5, verdict (i)
- [scikit-learn docs] "Comparison of Calibration of Classifiers" — https://scikit-learn.org/stable/auto_examples/calibration/plot_compare_calibration.html (**fetched**) — used in: iteration_3, verdicts (ii)/(iv)
- [Parker, Bravo, Leek 2013] "Removing batch effects for prediction problems with frozen surrogate variable analysis" (fSVA) — https://arxiv.org/abs/1301.3947 (search-return) — used in: iteration_1, verdict (ii)
- [Le Gratiet & Garnier 2012/2015] recursive co-kriging — https://arxiv.org/abs/1210.0686 , https://royalsocietypublishing.org/doi/10.1098/rspa.2015.0018 , https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4528652/ (all **search-return only**) — used in: iteration_2, verdict (ii) (the level-dependence caveat is search-return grade and must be labelled as such)

**Leads seen but NOT fetched — MUST NOT be cited as evidence**: "Selecting scale
factor of Bayesian multi-fidelity surrogate by minimizing posterior variance"
(https://www.sciencedirect.com/science/article/pii/S1000936122001042); adaptive-scale-
factor RBF MFS (https://link.springer.com/article/10.1186/s10033-022-00742-z);
"Mean-Model Bias Correction Method" (https://link.springer.com/chapter/10.1007/978-3-031-99155-4_11);
MF reduced-order surrogate modelling (https://royalsocietypublishing.org/rspa/article/480/2283/20230655/101080/Multi-fidelity-reduced-order-surrogate);
"Understanding multi-fidelity training of machine-learned force-fields"
(https://arxiv.org/pdf/2506.14963); "Hypothesis Transfer Learning via Transformation
Functions" (https://arxiv.org/pdf/1612.01020); "Error modeling for surrogates of
dynamical systems using machine learning" (https://arxiv.org/pdf/1701.03240);
corrector-operator for NO surrogates (ResearchGate 371758310); MF-FNO GCS
(https://arxiv.org/pdf/2308.09113 — batch-1 fetch failure, still uncited).

## Dead ends

- **`arxiv.org/pdf`, ScienceDirect, Springer, OpenReview** — not attempted at all this
  loop; batches 1-2 proved all four fail from this cluster. Zero fetch failures is the
  result of obeying that rule.
- **ar5iv is the fix for pre-2024 arXiv papers** (no `/html/` endpoint exists for
  them). This is the single most useful infrastructure finding of the batch:
  `https://ar5iv.labs.arxiv.org/html/<arxiv_id>` recovered the benchmark paper's body
  after two batches of failures. **Add it to every future websearcher's route list.**
- **Summariser digits are unreliable**: two fetches of the *same* ar5iv page rendered
  the Poisson per-level sample counts as "100, 50, 20, and 5" and "256, 128, 64, and
  32". Structural claims from a fetch are usable; **single table digits need two
  independent renderings** (which is why the 0.018/m=2.14 claim was cross-checked and
  the sample counts were not adopted).
- **Term "rank-one correction" / "amplitude"** — collapses into unrelated
  linear-algebra and seismology material, reproducing batch 2's finding that the
  productive vocabulary is "scale factor rho", "bridge function", "discrepancy",
  "error surrogate".
- **Nothing at N_hf = 5, again** (third batch running). The literature supplies
  mechanisms and no effect sizes for this regime; every defensible B3 claim is ordinal
  (head vs frozen base), not absolute.

## For the brainstormer

The brainstormer MUST quote the verdict row for whatever it proposes.

1. **Quote verdict (i) verbatim: `preempted-but-MF-composition-open`, and name ROMES
   in the card's `prior_art`.** "Fit a statistical model of your own surrogate's error
   from cheap features and use it to correct the output" is published, named, and
   reported to buy an order of magnitude
   (https://arxiv.org/abs/1405.5170). The card's only admissible claim is the **MF
   composition**: the law is fitted on *auxiliary fidelity levels of the same ladder*
   (supervision = the frozen operator's own residual at levels 8/16/32) and applied at
   the top level where N_hf = 5. Every fetched MF scale estimator instead fits against
   HF observations (LR-MFS explicitly, https://arxiv.org/abs/1705.02956).
2. **The strongest available motivation sentence, fully cited**: IFC — the paper that
   sets this stream's bar — represents the field as "the latent output as a continuous
   function of the input and fidelity … multiplied with a basis matrix"
   (https://ar5iv.labs.arxiv.org/html/2207.00678). B2's base already has IFC's joint
   all-level training but **no per-sample coefficient factor**; g(X) is its rank-1
   amplitude-only, post-hoc case. Use this as the motivation, and cap the scope: a
   K>1 coefficient head is a **batch-4** question.
3. **Pre-register the literature's own reason the head may fail — this is the card's
   honest negative.** Recursive co-kriging assigns **each level its own rho**, and
   "Different fidelity levels have distinct parameter estimates" (search-return grade,
   iteration_2; the review's rho(x) is defined level-pair-wise,
   https://arxiv.org/html/1609.07196v5). If the gain law is level-dependent, a
   ladder-fitted g(X) cannot transfer — exactly B2 part 7's negative reading ("the
   gain is a property of the HF solve that the lower levels do not share"). Make this a
   *measurement*: report the fitted gain law's coefficients **per level** (levels 8/16/32
   separately) as score-neutral instrumentation. That single table decides the
   mechanism regardless of whether the nRMSE clause fires, and it is cheap.
4. **Honesty guardrails on the headroom.** 0.02431 is a LOO upper bound computed with
   test targets (B2 part 6 says so); scikit-learn's own docs supply the citable warning
   that small-set calibration overfits and that poor calibration "is bound to happen
   when the training size is too small"
   (https://scikit-learn.org/stable/auto_examples/calibration/plot_compare_calibration.html).
   So: regularize the head, choose the regularization strength **without** test
   targets, and never write 0.0243 as a prediction. The whole available effect is
   0.0099-0.0113 nRMSE against a **0.0086367** floor (≈1.15-1.31x) — quote both
   numbers in the same sentence and say plainly that a null result is the likely
   outcome and is still informative.
5. **Two adjacent constructions to state you are NOT doing** (so reviewers can check):
   you are **not** doing REEF-GP (frozen-operator residual GP that "only quantif[ies]
   uncertainty and does not correct the mean prediction",
   https://arxiv.org/abs/2606.17513), and you are **not** doing PDE-residual
   correction at inference (https://arxiv.org/abs/2210.03008 — that is s3 territory and
   would need the Poisson operator applied per sample). Also respect s5's territory
   ruling: a *learned* scale head is architecture, not a knob, so this belongs in s1's
   model card, not s5's (`websearches/s5_tuning/batch_2/report.md`).
6. **Stretch-bar hygiene, and one written note to the operator.** Keep 0.036 as the
   denominator (ADR 0002 is immutable in-round). But the fetched paper places
   **0.018 at m=2.14 = 128^2 extrapolation, for IFC-ODE2** — not IFC-GPODE at 64^2 —
   so the card should stop describing 0.018 as an achievable same-task target and
   should record the attribution correction as a recommendation to the mentor/operator
   (program.md §13.4: written recommendation, not action). Batch 1 already flagged this
   as unresolved; it is now resolved at fetch grade, with an independent corroborating
   search return.
7. **Infrastructure**: use `https://ar5iv.labs.arxiv.org/html/<id>` for any pre-2024
   arXiv paper. It is why this batch has zero fetch failures and the previous two did
   not.
