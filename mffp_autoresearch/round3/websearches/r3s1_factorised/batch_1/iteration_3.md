# iteration_3 — `r3s1_factorised`, batch 1 (§3.3 refutation work begins)

## Search rationale

Field context declared `ENOUGH` at the end of turn 2. Turns 3–5 are §3.3
refutation searches whose goal is to REFUTE novelty of the three directions this
batch is likely to propose:

- **D1** — ship the **propagation-aware two-stage cross-coefficient closed-form
  head** (stage 1 condition→SET coefficients; stage 2 remaining coefficients
  regressed on **out-of-fold stage-1 predictions**) as the scored condition→HF
  arm on the honest panel.
- **D2** — the **condition-dimension discriminator** for M15: per-direction OOF
  R² from the condition vs from the SET coefficients across all 6 panel cells
  (cond_dim 3/5/18/19/19/50), used as a **training-free pre-fit predictor** of
  whether the two-stage arm pays.
- **D3** — the **fitted closed-form floor battery** (`affine_on_hf_train`
  alongside nn_condition / train_mean / zero) as a mandatory reported arm any
  learned condition→HF claim must clear.

Turn 3 attacks D1 head-on from the multi-target-regression side (the ROM
literature was turn 2's angle; the ML side is where "treat other targets as
inputs" lives), plus a cascade/error-propagation angle and a baseline-discipline
angle for D3.

## Search terms used

1. `regressor chains multi-target regression using predicted outputs as inputs corrected training true versus predicted values`
2. `cascaded surrogate models error propagation second stage trained on predicted inputs bias correction`
3. `linear regression baseline neural operator parametric PDE benchmark few samples must beat affine baseline`

## Findings

### Term 1 — REFUTES D1's mechanism-level novelty

**FETCHED (decisive)**: Spyromitros-Xioufis, Tsoumakas, Groves & Vlahavas,
*"Multi-Target Regression via Input Space Expansion: Treating Targets as
Inputs"*, arXiv:1211.6581 v5 (Machine Learning journal) —
<https://arxiv.org/abs/1211.6581> (retrieved 2026-08-07). Verbatim from the
retrieved abstract:

> *"A family of multi-label classification methods address this challenge by
> **building a separate model for each target on an expanded input space where
> other targets are treated as additional input variables**. … we introduce two
> new methods for multi-target regression, called **Stacked Single-Target** and
> **Ensemble of Regressor Chains** … Furthermore, we highlight an inherent
> problem of these methods — **a discrepancy of the values of the additional
> input variables between training and prediction** — and develop extensions
> that **use out-of-sample estimates of the target variables during training** in
> order to tackle this problem. The results … show that, **when the discrepancy
> is appropriately mitigated**, the proposed methods attain consistent
> improvements over the **independent regressions baseline**."*

This is the two-stage head AND its propagation-aware gate, published in 2012/2016
under the names **Stacked Single-Target (SST)** and **Ensemble of Regressor
Chains (ERC)**, with the corrected (out-of-sample) variants; and the reported
effect — corrected variants beat *independent per-target regression*, uncorrected
ones do not reliably — is exactly what B3 turn-3 F25 measured on this panel
(true-input gate: panel 18.7500→19.9704; OOF-input gate: →18.6787).

Supporting returns, not fetched: Springer journal version
<https://link.springer.com/article/10.1007/s10994-016-5546-z>; multi-target SVR
via correlation regressor chains
<https://www.sciencedirect.com/science/article/abs/pii/S0020025517307946>;
probabilistic regressor chains <https://arxiv.org/pdf/1907.08087>; MTR via output
space quantization <https://arxiv.org/pdf/2003.09896>. Aggregated search return:
*"during training, actual true target values are used as inputs for subsequent
models, whereas during prediction/testing, the predicted values from previous
models in the chain are used"* — the named failure mode.

### Term 2 — cascaded surrogates / error propagation

Returns: cascaded NN surrogate for water-supply networks
<https://www.tandfonline.com/doi/full/10.1080/19942060.2025.2453080>; two-stage
surrogate for composite microstructure design
<https://www.sciencedirect.com/science/article/abs/pii/S095219762401594X>;
uncertainty propagation in Bayesian two-step procedures
<https://arxiv.org/pdf/2505.10510>; deep residual-error surrogate for
gravitational waves <https://arxiv.org/pdf/2203.08434>. Not fetched.
Aggregated search return: cascades where *"the probabilistic output distribution
of an upstream model serves as a noisy input for the downstream model"* and
*"in second-stage modeling, the goal is to appropriately propagate the impact of
input errors assessed in the first stage into ultimate predictions"*. This
literature propagates **uncertainty** forward; it does not fit the second stage
on out-of-fold first-stage point predictions, so it is a weaker preemption than
term 1 — recorded, not relied on.

### Term 3 — baseline discipline for D3

Returns: PCA-RaNN randomized neural operator with *"closed-form least-squares
readout, recasting latent operator learning as fixed-feature linear regression"*
<https://arxiv.org/html/2606.29440v1> (already cited by the round-2 r2s1-B2
loop); *"Numerical PDE solvers outperform neural PDE solvers"*
<https://arxiv.org/html/2507.21269v1>; meta-learned basis adaptation for
parametric linear PDEs <https://arxiv.org/pdf/2604.09289>; deep learning for
subspace regression <https://arxiv.org/pdf/2509.23249>. Not fetched this turn.
The aggregated search return is explicit and useful: *"the search results discuss
various baseline approaches and comparisons, but **don't explicitly detail a
requirement that methods must beat a linear regression or affine baseline in
few-sample settings**"* — i.e. no returned source establishes the mandatory
fitted-affine floor as standard practice. This is consistent with round 2's
finding (REALM compares against no trivial baselines, arXiv:2512.18595) and with
McGreivy & Hakim's weak-baseline critique (arXiv:2407.07218), both cited in
`round2/websearches/r2s1_direct/batch_{1,2}`.

## Interpretation

D1's mechanism is **preempted with a direct, fetched citation** (SST/ERC with
out-of-sample corrected training, arXiv:1211.6581) — the card must name it and
may not claim the cascade or its OOF gate as novel. D3's *methodological*
residue (a fitted closed-form affine floor as a mandatory published arm at
N_hf = 5) is unrefuted by one search and needs one more targeted attempt.
Turn 4 must (i) test whether SST/ERC has already been applied to PDE/ROM
coefficient targets, which would close D1's composition too, and (ii) attack D2.
