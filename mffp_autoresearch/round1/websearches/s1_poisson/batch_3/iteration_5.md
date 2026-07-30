# Iteration 5 — refutation pass + prior-art verdicts (**ITERATION CAP HIT: 5 of 5**)

## Search rationale (adversarial)
Iterations 1-4 established the neighbourhood; this turn tries to **kill** the three
candidate directions the B3 card can propose. The most dangerous framings of the
card, stated as an opponent would:
- "You are predicting per-sample coefficients of a field from the parameters, with
  the basis fixed — that is POD-coefficient regression / IFC with K=1."
- "You are fitting a statistical model of your own model's error from cheap
  features and using it to correct the output — that is ROMES."
- "You are fitting the correction where data is cheap and applying it where it is
  expensive — that is the whole multifidelity-correction literature."
Terms were chosen to surface exactly those three.

## Search terms used
1. `predict per-sample scalar coefficient amplitude of neural operator prediction learned from lower resolution training data multi-fidelity rank-one correction`
2. `multi-fidelity POD coefficient regression predict modal coefficients from parameters coarse mesh snapshots applied to fine mesh few high fidelity snapshots`
3. `ROMES method error surrogate predict reduced order model error from indicators Gaussian process Drohmann Carlberg statistical model of surrogate error`

## Findings per term

### Term 1
Returns: neural-operator primer (https://arxiv.org/pdf/2503.05598), corrector
operator for NO surrogates
(https://www.researchgate.net/publication/371758310_Corrector_Operator_to_Enhance_Accuracy_and_Reliability_of_Neural_Operator_Surrogates_of_Nonlinear_Variational_Boundary-Value_Problems),
MF-FNO for geological carbon storage (https://arxiv.org/pdf/2308.09113 — batch-1
fetch failure, still uncited), MF-FNO transfer learning
(https://arxiv.org/pdf/2304.06972), solver-based correction for ODE predictors
(ml4physicalsciences NeurIPS ML4PS 2025 #319).
Engine synthesis: MF-FNO work pairs 32^3 LF with 64^3 HF realizations; "the
residual-based error correction method builds on using lower-fidelity solutions to
estimate modeling errors, and treats the neural operator prediction as an initial
guess and solves a variational problem to correct the residual error" (consistent
with the fetched 2210.03008 in iteration 3). **No source predicts a per-sample
scalar amplitude for an operator's output.** Explicit negative recorded.

### Term 2 — the POD-coefficient framing
Returns: MF reduced-order surrogate modelling
(https://royalsocietypublishing.org/rspa/article/480/2283/20230655/101080/Multi-fidelity-reduced-order-surrogate),
MF + active-subspace + non-intrusive POD (https://pmc.ncbi.nlm.nih.gov/articles/PMC10100049/,
https://arxiv.org/pdf/2206.01243), MF surrogates for time-series outputs
(https://arxiv.org/pdf/2109.11374).
Engine synthesis: "POD at the high-fidelity level extracts a global basis that
represents predominant spatial patterns, and the LSTM network model approximates
the corresponding expansion coefficients"; "independent models employed for each
modal coefficient"; parameters-to-coefficients maps are built by "linear
interpolation, Gaussian process regression, radial basis function interpolation,
multi-fidelity methods, inverse distance weighting, and artificial neural networks".
**FETCH — https://pmc.ncbi.nlm.nih.gov/articles/PMC10100049/ (fetched)**: "the
modal coefficients C, also called reduced state variables, we project the data onto
the POD subspace: C = Phi^T S"; "**The low-fidelity is built by extending on the
whole parameter space a one-dimensional response surface constructed over the AS
corresponding to each POD coefficient**"; the levels are then fused by hierarchical
GPs where "high-fidelity outputs depend on low-fidelity predictions through an
autoregressive structure".
Adversarial reading: **parameter -> per-sample coefficient regression with a fixed
spatial basis, fused across fidelities, is thoroughly published** (POD-ROM + MF-GP
family, and IFC itself per iteration 4). What is NOT in these sources is doing it as
a *post-hoc scalar rescaling of a trained neural operator's own output* whose
supervision comes from the operator's residual at other fidelity levels.

### Term 3 — the ROMES framing (the strongest hit of the loop)
Returns: https://arxiv.org/abs/1405.5170, https://epubs.siam.org/doi/10.1137/140969841,
error modelling for surrogates with ML (https://arxiv.org/pdf/1701.03240),
ROM-ES UQ report (https://www.osti.gov/servlets/purl/1122962).
**FETCH — https://arxiv.org/abs/1405.5170 (fetched)**: ROMES uses
"**Gaussian-process regression**" to map "computationally inexpensive 'error
indicators'" to "**a distribution over the true error**", and "**correcting the
reduced-order-model output with this surrogate can improve prediction accuracy by
an order of magnitude**"; it explicitly contrasts with "existing 'multifidelity
correction' approaches, which often fail for reduced-order models and suffer from
the curse of dimensionality".
Adversarial reading: **"fit a statistical model of your own surrogate's error from
cheap features and use it to correct the output" is published, named, and is
reported to buy an order of magnitude.** Any B3 card that presents the gain head as
a new idea is 0-for-5 on this project's novelty record. The residual openings are
(i) ROMES's indicators are residual norms / dual-weighted residuals, not the
condition vector; (ii) ROMES corrects a *scalar output or norm*, not a per-sample
multiplicative gain on a field; (iii) ROMES's training data are HF-evaluated error
samples, not other fidelity levels of a ladder.

## PRIOR-ART VERDICTS

### (i) Ladder-pooled per-sample gain-head calibration for an MF operator
(freeze `allpairs__per_level`; head g(X) multiplying the field output; **fitted on
the 175 pooled ladder rows**, not the 5 HF rows)
**Verdict: `preempted-but-MF-composition-open`.**
Preempting citations, all fetched this loop: ROMES —
GP from cheap indicators to the error distribution, "correcting the reduced-order-
model output with this surrogate can improve prediction accuracy by an order of
magnitude" (https://arxiv.org/abs/1405.5170); the MF review's multiplicative /
comprehensive correction `y^HF = rho(x)·y^LF(x) + delta(x)`
(https://arxiv.org/html/1609.07196v5); LR-MFS, whose scale factor is fitted by least
squares **on the HF samples** (https://arxiv.org/abs/1705.02956); IFC itself, whose
field is "the latent output as a continuous function of the input and fidelity …
multiplied with a basis matrix" — the card's g(X) is the K=1 amplitude-only case
(https://ar5iv.labs.arxiv.org/html/2207.00678); POD-coefficient MF regression
(https://pmc.ncbi.nlm.nih.gov/articles/PMC10100049/); APEX's per-sample amplitude
anchor taken from a lower-fidelity operator in a target-scarce MF regime
(https://arxiv.org/abs/2605.26732).
**What remains open, precisely**: fitting the calibration law on **auxiliary
fidelity levels of the same ladder, supervised by the frozen operator's own
residual at those levels, and transferring it to the top level where N_hf = 5**.
Every fetched estimator for a multiplicative MF correction is fitted against
**HF** observations (LR-MFS explicitly; the review's rho(x) is "an SM created from
the ratio between the HFM and the LFM"); ROMES's indicators are residual norms, not
a condition vector, and its training errors are HF-evaluated; REEF-GP fits a frozen
operator's residuals but "only quantif[ies] uncertainty and does not correct the
mean prediction" (https://arxiv.org/abs/2606.17513); 2210.03008 corrects the mean
but from the PDE residual at inference, not from a fitted law
(https://arxiv.org/abs/2210.03008). **Mandatory framing**: a *measured* MF
composition of published parts, never an invention.

### (ii) Any preemption of the exact construction?
**Verdict: `novel` (narrow, weak — claim "not previously reported", never "novel
method").** Across 15 searches over three batches, no fetched source (a) freezes a
multi-fidelity neural operator, (b) fits a per-sample scalar output gain as a
function of the condition vector, (c) using supervision from the operator's
residuals at *lower* fidelity levels only, (d) at N_hf = 5. Nearest neighbours, in
order of closeness: ROMES (same idea, different features/target/fit data), the MF
quantile-link (borrows a *smoother* covariate-dependent link across fidelities to
survive HF scarcity — "the HF quantile is represented as a low-fidelity quantile
evaluated at a covariate-dependent level … which can be smoother than the HF
quantile itself", https://arxiv.org/abs/2605.10406), APEX (amplitude from a coarser
model, but a **field** and from a prediction, not a fitted scalar law), fSVA's
borrow-strength-for-per-sample-correction idiom (https://arxiv.org/abs/1301.3947).
**Adversarial caveat the card must carry**: the *transfer* assumption is the whole
experiment, and the literature's own prior is against it — recursive co-kriging
gives **each level its own** rho, "Different fidelity levels have distinct parameter
estimates" (search-return, iteration 2), and the review's rho(x) is defined
level-pair-wise. If the gain law is level-dependent, the head cannot transfer, which
is exactly part 7's pre-registered negative reading. Honesty constraint from
iteration 3: scikit-learn's own docs say small calibration sets overfit — "optimizing
the log-loss can still lead to poorly calibrated models because of overfitting …
bound to happen when the training size is too small"
(https://scikit-learn.org/stable/auto_examples/calibration/plot_compare_calibration.html)
— so 0.02431 stays a LOO **upper bound**, and any fit must be regularized with the
regularization strength chosen without touching test targets.

### (iii) IFC-GPODE gap analysis (the 0.018 stretch)
**Verdict: the stretch bar's attribution is `mis-stated in the round's own
documents`, and the mechanism gap is nameable.**
Fetched (https://ar5iv.labs.arxiv.org/html/2207.00678): IFC-GPODE = GP prior over
each fidelity-varying basis element, "b_ij(m) ~ GP(0, kappa(m,m'))", best at m=1 but
degrading for m>1; IFC-ODE2 = a neural ODE for the bases, "db_ij(m)/dm = gamma(b_ij,
m)", better extrapolation; "nRMSE of IFC-ODE2 at m=1 and m=2.14 is 0.036 vs. 0.018",
with "m=2.14 corresponds to a 128x128 mesh" (independently corroborated by the
iteration-4 term-3 search return). **So 0.018 is IFC-ODE2 extrapolating to a
128^2 mesh — a different task from predicting the 64^2 field — not IFC-GPODE at
64^2** as `docs/adr/0002-ifc-poisson-skill-reference.md` states. ADRs are immutable
in-round (program.md §5.3): the card must keep using 0.036 as the denominator, may
cite this finding, and the correction goes to the operator as a written note.
**What the base lacks vs IFC**: IFC factorises the field into **per-sample,
fidelity-continuous latent coefficients x shared fidelity-varying spatial bases**
under one joint likelihood over all levels, "p(Y|X) = prod_n N(y_n | B_n h(m_n,x_n),
sigma^2 I)". B2's base already has joint all-level training and a fidelity tag; it
has **no explicit per-sample coefficient factor**. The B3 gain head is the rank-1
amplitude-only version of that factor — which both motivates the card and caps its
ambition: if the K=1 head only recovers part of the 57.1 % amplitude term, the
indicated next mechanism is a **K>1 coefficient head with fixed bases** (still not
IFC, which learns the bases' fidelity ODE too), and that is a batch-4 question, not
a batch-3 one.
