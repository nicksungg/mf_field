# Iteration 3 — task (c): small-N calibration honesty + post-hoc correction of a frozen operator

## Search rationale
Two jobs. (c) The card's headroom number (0.02431 at LOO-ridge R^2 0.919) is a
LOO estimate computed with test targets, over 128 test samples but a 5-D condition
vector; and the *fit* it proposes is either on 5 HF rows (infeasible) or on 175
ladder rows. I need fetched statements about how optimistic small-set calibration
fits and LOO estimates are, so the card cannot quote 0.02431 as a score. (a-cont)
I also need to know whether post-hoc fitting on a **frozen** operator's residuals
*to correct the mean* is published — the in-repo report's REEF-GP is the obvious
threat and must be fetched first-hand.

## Search terms used
1. `calibration with very small calibration set n=5 unreliable leave-one-out estimate optimistic overfitting regression rescaling`
2. `post-hoc error correction model trained on residuals of frozen neural operator improves accuracy learned discrepancy correction surrogate mean prediction`
3. `train correction model on intermediate fidelity levels apply at highest fidelity level transfer discrepancy learned at coarse levels neural surrogate`

## Findings per term

### Term 1 — small-N calibration
Returns: scikit-learn calibration comparison
(https://scikit-learn.org/stable/auto_examples/calibration/plot_compare_calibration.html),
"Validation and verification of regression in small data sets"
(https://www.sciencedirect.com/science/article/abs/pii/S0169743998001671 — not
fetched, 403 rule), no-harm calibration for Oaxaca-Blinder estimators
(https://arxiv.org/pdf/2012.09246), adaptive conformal coverage
(https://arxiv.org/pdf/2510.04318).
**Fetch — scikit-learn calibration docs** (**fetched**): "In this example the
training set was intentionally kept very small. In this setting, optimizing the
log-loss can still lead to poorly calibrated models **because of overfitting**";
and "note that for some dataset seeds, all models are poorly calibrated, even when
tuning the regularization parameter as above. This is bound to happen when the
**training size is too small** or when the model is severely misspecified." The
documented mitigation in the same page is cross-validated regularization
(`LogisticRegressionCV`, `Cs=np.logspace(-6,6,101)`, `cv=10`).
Engine synthesis on LOO (search-return grade, not fetched): "the gap between
leave-one-out estimators and true expected values stems from relatively small
values of n, and empirically this difference shrinks as n increases"; "a natural
concern is that calibration parameters overfit the calibration cell, which can be
addressed with leave-one-out cross-validation by recalibrating from remaining runs
and re-predicting"; "the finite-sample correction shrinks as O(1/n)".

### Term 2 — post-hoc correction of a frozen operator
Returns: **Residual-based error correction for neural-operator-accelerated Bayesian
inverse problems** (https://arxiv.org/abs/2210.03008,
https://www.osti.gov/pages/biblio/2421120), HiPreNets progressive residual training
(https://arxiv.org/pdf/2506.15064).
**Fetch 1 — REEF-GP** https://arxiv.org/abs/2606.17513 (**fetched**): a GP is fitted
post hoc "to the residuals (prediction errors) of a frozen neural operator", using
"the operator's intrinsic coordinate-feature representations to construct
geometry-aware uncertainties"; the fetch's verdict is explicit that it "**only
quantif[ies] uncertainty** and does not correct the mean prediction … the frozen
operator's predictions remain unchanged; the GP layer adds uncertainty bounds".
**Fetch 2 — residual-based error correction** https://arxiv.org/abs/2210.03008
(**fetched**): the authors "correct the prediction of a trained neural operator by
solving a linear variational problem based on the PDE residual", i.e. the
correction is computed **at inference from the PDE residual, not fitted from
data**, per sample; claim: "a trained neural operator with error correction can
achieve a quadratic reduction of its approximation error".

### Term 3 — is "fit the correction on the intermediate levels" published?
Returns: MF+transfer-learning surrogate papers
(https://arxiv.org/html/2602.00072, https://arxiv.org/pdf/2410.12241,
https://arxiv.org/pdf/2306.06904, https://arxiv.org/pdf/2605.02871,
https://www.sciencedirect.com/science/article/pii/S1995822625000482), plus a
surrogate-modelling overview PDF (itea4.org).
Engine synthesis (search-return grade): MFRNP "models the residual between the
aggregated output from lower fidelities and highest-fidelity ground truth"; "the
discrepancy can be modelled as a Gaussian process or other surrogate model
**trained on the residuals between the scaled low-fidelity predictions and
high-fidelity data**"; progressive transfer means "the model being transferred
sequentially across increasing hierarchical fidelity levels … each target model
inherits parameters from a closely related predecessor"; intermediate levels give
"a smoother transition … pyramid structure".
Read adversarially, all of these fit the discrepancy **against HF ground truth**
(MFRNP explicitly) or transfer *network weights* level-to-level; none fits a
correction *whose supervision comes only from the lower levels* and then applies
it at the top. No source in this return does what the card proposes.

## Interpretation
The two closest published relatives of "post-hoc head on a frozen operator" both
stop short of the card's construction in a citable way: REEF-GP fits the frozen
operator's residuals but only for uncertainty (no mean correction), and 2210.03008
corrects the mean but from the PDE residual at inference, not from a fitted
parametric law. On honesty, scikit-learn's own documentation supplies the sentence
the card needs about small-set calibration overfitting — which means the card must
present 0.02431 strictly as a LOO *upper bound* (part 6 already labels it so) and
must regularize any fitted gain law explicitly.
