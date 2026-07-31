# Iteration 2 — Q2: is post-hoc shrinkage toward the model's own conditional mean a published calibration operation?

## Search rationale

B1's part 7 item (3) wants "post-hoc shrinkage toward the model's own mean
field, calibrated on a held-out TRAIN fold" made a REQUIRED arm on every round-2
card (test-fitted oracle lambda* = 0.0 on helmholtz -> skill 6.17 -> 3.52, a 43%
gain; lambda* = 1.0 on pfc/allen_cahn/fisher_kpp; 1.1-1.5 on
cahn_hilliard/ifc_poisson). Two things need refuting: (i) the *operation*
(shrink a point prediction toward a mean, a James-Stein-flavoured move) and
(ii) the *diagnostic reading* (lambda* < 1 means the model's condition-dependence
is net harmful; lambda* > 1 means it is under-confident / amplitude-deficient).
Terms chosen to hit the calibration literature, the PDE-surrogate literature on
conditional-mean collapse, and the amplitude/spectral-recalibration literature
(the in-repo FreqNO-DPS lead from `summary_so_far.md`).

## Search terms used

1. `post-hoc shrinkage of regression predictions toward the mean calibration variance deficiency neural network`
2. `neural operator surrogate under-predicts amplitude regression to the mean conditional mean collapse MSE training`
3. `variance inflation recalibration deterministic surrogate prediction spectral amplitude correction post-processing`

## Findings

### Term 1 — post-hoc calibration in regression

The published post-hoc regression-calibration toolkit rescales the predictive
**variance**, not the predictive **mean**. Search summary: "In the regression
setting, post-hoc calibration analogous to temperature scaling can be achieved
by scaling the predicted variances by a scalar factor. Minimizing the negative
log-likelihood with respect to the calibration factor on a held-out validation
set yields a closed-form analytical solution"; `VarianceScaling` and `GPNormal`
are the named methods (SNIPPETS; primary artifact
https://github.com/EFS-OpenSource/calibration-framework — not fetched).
Other results (all unfetched): https://arxiv.org/pdf/2509.23665,
https://openaccess.thecvf.com/content/CVPR2021/papers/Tomani_Post-Hoc_Uncertainty_Calibration_for_Domain_Drift_Scenarios_CVPR_2021_paper.pdf,
https://www.emergentmind.com/topics/post-hoc-calibration-methods.
**No result described a scalar shrinkage of the point prediction toward the
model's own predicted mean field.**

### Term 2 — conditional-mean collapse in PDE surrogates — the strongest hit

"Predictivity and Utility of Neural Surrogates of Multiscale PDEs" —
https://arxiv.org/html/2604.20061v1 — **FETCHED**, exact quotes:

- "A network trained with mean-squared error converges to the conditional
  expectation û(u_c)=E[u|u_c], i.e. the average over all fine states consistent
  with the coarse input." … "The resulting prediction is over-smoothed by
  construction."
- "This is simply the optimal solution to Mean Squared Error (MSE)
  minimization. … no architecture or training procedure can recover information
  the coarse representation discards." / "This is not a training failure — it is
  the *optimal* MSE solution given the information available."
- "A surrogate can achieve excellent L² error while systematically
  misrepresenting the physics that matters." / "Small L² error can therefore
  coexist with large errors in physically decisive QoIs."
- Baseline discipline: "Many papers compare against weak baselines, use
  mismatched hardware, or ignore amortization."
- Proposed remedies: hybrid neural-classical resets with full-solver
  corrections; **generative (diffusion) models conditioned on coarse outputs to
  recover high-frequency content**; scale-aware metrics (band-limited errors,
  H¹/H² norms); Lyapunov-time and intrinsic-dimension proxies.

Also surfaced, unfetched: "The Prevalence of Neural Collapse in Neural
Multivariate Regression" —
https://proceedings.neurips.cc/paper_files/paper/2024/file/e4748b6b6ca49f04b6a8cfce1d5f9a70-Paper-Conference.pdf ;
"On the influence of over-parameterization in manifold based surrogates and deep
neural operators" — https://arxiv.org/pdf/2203.05071.

### Term 3 — amplitude / spectral recalibration as post-processing

- "Local Conformal Predictions for Calibrated Surrogates" (FALCON) —
  https://arxiv.org/html/2607.01354v1 — **FETCHED**: "conformal prediction, a
  distribution-free post-processing to complement trained surrogates with
  calibrated uncertainties"; it "exclusively adjusts interval widths … the
  central amplitude A_NN remains unchanged" — i.e. explicitly NOT point-
  prediction shrinkage. Calibration-set requirement: 5,000 points used, "coverage
  fluctuates strongly at n_calib=50, converges … from n_calib=500", ~1,000
  recommended as a practical minimum. **That size requirement rules conformal
  post-processing out for our 400-sample sharp panel and certainly for
  N_hf = 5.**
- "Correcting Neural Operator Spectral Bias via Diffusion Posterior Sampling
  with Sparse Observations" (FreqNO-DPS) — https://arxiv.org/pdf/2606.03936
  (not fetched here; already summarized in
  `docs/reports/MF_Leaderboard_Beaters_2026_Report.md` lines 32/102-108): the
  precedent for frequency-dependent *amplitude* recalibration — but it requires
  sparse observations at test, which the round-2 stripped view forbids.
- Snippet-level: "An additional post-processing step known as calibration aims
  to adjust the predicted variance towards the actual variance in the data" and
  a proton-spectrum surrogate performing "post-hoc variance recalibration … on a
  held-out calibration subset" (https://arxiv.org/pdf/2606.06210, unfetched).

## Interpretation

The *mechanism* of B1's shrinkage arm is preempted twice over — the collapse it
diagnoses is the textbook MSE-conditional-mean result stated verbatim in
arXiv:2604.20061, and scalar post-hoc rescaling on a held-out fold is standard
calibration practice — but every published post-hoc operator found rescales
*variance / interval width*, not the point prediction, and the two closest
amplitude-correcting methods (FreqNO-DPS, conformal) need test-time observations
or ~1000 calibration points that this regime does not have. What is genuinely
unpreempted is using lambda* itself as a **diagnostic statistic** (lambda* = 0
certifying that a model's condition-dependence is net harmful) and requiring it
as a mandatory reported arm.
