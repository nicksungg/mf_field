# Iteration 2 — task (b): borrowing strength across fidelity levels for a calibration/scale parameter

## Search rationale
The card's whole design constraint is "6 parameters, 5 HF rows", and its escape is
to fit the gain where the data is (the 175 pooled ladder rows) and apply it where
it is not (fidelity 64). Classical MF owns the object `rho` (B2 cited AR1/NARGP);
what B2 did NOT establish is **on which data rho is estimated**. If the classical
answer is "on the HF samples", the card's move (estimate on auxiliary levels) is
the differentiator; if the classical answer already includes "estimate it from the
cheap levels when HF is too scarce", the card is preempted at its core. This
iteration also fetches the in-repo report's [U-2] quantile-link paper first-hand,
because "reduce HF estimation to a smoother level function" is the same
borrow-strength argument the card needs.

## Search terms used
1. `multi-fidelity estimate scale factor rho on low-fidelity data transfer to high fidelity few samples hierarchical borrowing strength calibration parameter`
2. `bridge function multiplicative correction multi-fidelity surrogate rho estimated separately each fidelity level recursive co-kriging level-dependent scale`
3. `scale factor estimated using low-fidelity samples because high-fidelity samples insufficient to fit regression coefficients multi-fidelity surrogate small sample`

## Findings per term

### Term 1 — is the scale parameter estimated with borrowed strength?
Returns: MF matter-power-spectrum emulation (https://arxiv.org/pdf/2105.01081),
MF review (https://arxiv.org/html/1609.07196v5), LR-MFS
(https://arxiv.org/pdf/1705.02956), SMT MFK docs (already B2-fetched),
hierarchical kriging for high-dim MF (https://arxiv.org/pdf/2301.00216),
"Selecting scale factor of Bayesian multi-fidelity surrogate by minimizing
posterior variance" (https://www.sciencedirect.com/science/article/pii/S1000936122001042
— ScienceDirect, not fetched per the batch-2 403 rule).
Engine synthesis (search-return grade, explicitly flagged as such): the scale
factor "measures the strength of the linear information transfer from the
low-fidelity to the high-fidelity process", is "typically tuned by Maximum
Likelihood Estimation (MLE), though recent studies have reported that MLE may
sometimes result in poor surrogate accuracy", and in hierarchical kriging "a scale
factor is determined by solving an optimization problem to establish a
relationship between the hyperparameters of low-fidelity and high-fidelity
models".

**Fetch — [U-2] MF quantile regression via a local quantile link**
https://arxiv.org/abs/2605.10406 (**fetched**): "the HF quantile is represented as
a low-fidelity (LF) quantile evaluated at a covariate-dependent level"; "This
reformulation reduces the problem to estimating the level function, which can be
smoother than the HF quantile itself"; efficiency holds "when the LF and HF
conditional distributions have similar shapes". This is the **statistical
archetype of the card's argument**: replace a hard HF-scarce estimation problem
with a *smoother covariate-dependent link* borrowed across fidelities. It is a
scalar/quantile object at each covariate, not a field, and the link is estimated
from both LF and HF data.

### Term 2 — is rho level-dependent (the adversarial question)?
Returns: recursive co-kriging (https://arxiv.org/abs/1210.0686,
https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4528652/,
https://royalsocietypublishing.org/doi/10.1098/rspa.2015.0018), co-kriging→MF-NN
survey (https://arxiv.org/html/2605.02871), SMT MFCK docs
(https://smt.readthedocs.io/en/latest/_src_docs/applications/mfck.html),
bi-fidelity NN transfer (https://arxiv.org/pdf/2002.04495).
Engine synthesis (search-return grade): recursive co-kriging decouples the levels
into "a series of independent kriging models"; "In the autoregressive model (AR1),
rho(x) is a scaling/correlation factor (constant, linear or quadratic)"; "the
auto-regressive framework provides a mechanism for detecting pathology by
monitoring the scaling factor rho … (which is learned from the data)"; "**Different
fidelity levels have distinct parameter estimates**, with important differences
between estimates at different levels".

**Fetch — Review of multi-fidelity models** https://arxiv.org/html/1609.07196v5
(**fetched**). Verbatim: multiplicative correction is
"y^HF = rho(x) · yLF(x), where rho(x) serves as the multiplicative correction
factor, essentially an SM created from the ratio between the HFM and the LFM";
comprehensive correction is "y^HF = rho(x) · yLF(x) + delta(x)", such hybrids being
"more challenging but can be better predictors in most cases" because they
"simultaneously address discrepancies in both the magnitude and trend of the LFM
compared to the HFM". Crucially for the verdict: the multiplicative surrogate is
built **from the ratio between HFM and LFM at corresponding evaluation points** —
i.e. the classical object is a *cross-fidelity* ratio requiring paired HF
evaluations, not a model-error gain estimated on auxiliary levels.

### Term 3 — is "fit the scale on the cheap data because HF is too scarce" published?
Returns: LR-MFS abs (https://arxiv.org/abs/1705.02956), Bayesian scale-factor
selection (ScienceDirect + ResearchGate mirrors), adaptive-scale-factor RBF MFS
(https://link.springer.com/article/10.1186/s10033-022-00742-z, Springer — not
fetched, batch-2 303 rule), non-hierarchical LF data papers (ScienceDirect).
Engine synthesis: "the key idea is to consider the low-fidelity model as a basis
function in the multi-fidelity model with the scale factor as a regression
coefficient, and the scale factor and coefficients … obtained simultaneously using
linear regression"; "negative values or extremely large values of rho indicates a
risky prediction, which are likely to be associated with undesirable low-fidelity
models, inappropriate surrogate forms, or **inadequate samples**".

**Fetch — LR-MFS** https://arxiv.org/abs/1705.02956 (**fetched**): "The system
behavior (high-fidelity behavior) is approximated by a linear combination of the
low-fidelity predictions and a polynomial-based discrepancy function"; the scale
factor is a **constant, not input-dependent**, and "The scale factor and
coefficients of the basis functions are obtained simultaneously using linear
regression", the objective being to minimise "the prediction errors **at
high-fidelity samples**". So the canonical estimator for the MF scale factor is
least squares **on the HF samples** — exactly the estimator the card cannot use
(5 rows, 6 parameters).

## Interpretation
Classical MF owns the *object* (an input-dependent multiplicative correction
rho(x), possibly plus an additive delta(x) — "comprehensive correction"), and
owns the warning that rho estimates differ level-to-level and that extreme rho
signals inadequate samples. But every fetched estimator fits the scale **against
HF observations** (LR-MFS least squares on HF samples; the review's ratio between
HFM and LFM at paired points). The one fetched source that borrows strength for a
*link/scale* object across fidelities is the quantile-link paper (2605.10406), and
it does so for conditional quantiles of a scalar response, using both LF and HF
data. Nothing fetched yet fits a **model-error** gain on auxiliary fidelity rows
and transfers it to the HF level — which is precisely the card's construction.
