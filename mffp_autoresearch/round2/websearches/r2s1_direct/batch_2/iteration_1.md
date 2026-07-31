# Iteration 1 — map the three B2 mechanism classes

## Search rationale

B1's part 7 says the stream should stop buying decoder capacity and spend B2
on **identification and calibration**. Three mechanisms are named there and
each needs its field context before any refutation search:
(a) per-spectral-band out-of-fold gain calibration of a trained field
predictor's POINT prediction (finding 2: calibration zeroes all non-DC gains
on every sharp dataset);
(b) a ~10^2-parameter closed-form (ridge / POD-coefficient) head as the
capacity control that the 15.9 M-parameter decoder must beat (finding: the
150-parameter head scored 19.0553 vs the decoder's 19.6444);
(c) training-free, statistic-driven selection of the output parameterization
(centering form via ||mean field||/geomean||y||, rank via the condition-
identifiable POD rank).

## Search terms used

1. `frequency band-wise gain calibration of neural operator predictions post-hoc spectral shrinkage`
2. `linear ridge baseline matches neural operator parametric PDE surrogate small parameter count`
3. `training-free selection of surrogate model form using dataset statistics parametric PDE reduced order`

## Findings

### Term 1 — band-wise gain calibration / spectral shrinkage

Top results:
- TF-SNO: Time-Frequency Gated Spectral Neural Operators — https://arxiv.org/pdf/2606.21189
- Correcting Neural Operator Spectral Bias via Diffusion Posterior Sampling
  with Sparse Observations (FreqNO-DPS) — https://arxiv.org/html/2606.03936
- Analysis of Fourier Neural Operators via Effective Field Theory — https://arxiv.org/pdf/2507.21833
- Gradient Descent as a Shrinkage Operator for Spectral Bias — https://arxiv.org/abs/2504.18207 , https://arxiv.org/html/2504.18207v1
- Mitigating Spectral Bias in Neural Operators via High-Frequency scaling — https://arxiv.org/pdf/2503.13695
- Iterative Refinement Neural Operators (IRNO) — https://arxiv.org/pdf/2605.24041

**FETCHED** https://arxiv.org/pdf/2606.21189 (TF-SNO): the band gating is
**learned end-to-end inside the architecture** ("Time-Frequency Gating",
"Spectral Regularization" as keywords), *not* a post-hoc calibration fitted on
held-out data. The fetch found **no** mention of shrinking band gains toward
zero as a held-out-fitted correction. The paper does report a "band-energy
calibration analysis" comparing physical power spectrum against learned gating
weights — i.e. band-resolved *diagnostics*, but of a learned in-architecture
gate.

Search-return note (not fetched): the FreqNO-DPS result is a "closed-form,
spectrally shaped guidance score that weights the surrogate contribution
according to its frequency-dependent accuracy" — the search return says
frequency-dependent calibration is "essential, not merely beneficial", but it
operates inside a diffusion posterior sampler and **requires sparse
observations at test time** (5% / 2% sensor coverage), which this round's
stripped view forbids.

Search-return note: arXiv:2504.18207 frames *gradient descent itself* as a
shrinkage operator masking Jacobian singular values — shrinkage-as-implicit-
regularization during training, not a post-hoc per-band gain fit.

### Term 2 — small-parameter closed-form baselines vs neural operators

Top results:
- Randomized neural operator for parametric PDEs with fast training and
  conformal UQ (PCA-RaNN) — https://arxiv.org/pdf/2606.29440
- Operator Boosting Produces Pareto-Efficient PDE Surrogates — https://arxiv.org/html/2606.17460
- Meta-Learned Basis Adaptation for Parametric Linear PDEs — https://arxiv.org/pdf/2604.09289
- Walsh-Hadamard neural operators — https://arxiv.org/html/2511.07347
- Physics-informed low-rank neural operators (PILNO) — https://arxiv.org/pdf/2509.07687

**FETCHED** https://arxiv.org/pdf/2606.29440 (PCA-RaNN): random fixed hidden
layer + **output layer solved in closed form by ridge regression** onto **PCA
coefficients** of the solution field; "significantly reduces trainable
parameters"; positioned as fast-training with accuracy competitive against
DeepONet/FNO on Burgers, Darcy, Navier-Stokes, backward heat. The fetch also
indicates PCA rank is chosen from **data-driven variance statistics** rather
than an arbitrary cutoff (the specific mechanism was not extractable from the
accessible portion — recorded as partial evidence, not a firm quote).

This is the closest published object to B1's "~150-parameter closed-form head":
condition/input -> PCA coefficients, ridge-solved, compared against neural
operators. It is prior art for the *architecture* of the control arm.

### Term 3 — training-free selection of surrogate model form

Top results:
- Multi-fidelity reduced-order surrogate modelling — https://royalsocietypublishing.org/rspa/article/480/2283/20230655/101080/Multi-fidelity-reduced-order-surrogate
- Data-driven ROM for parametric PDE eigenvalue problems via GPR — https://arxiv.org/pdf/2301.08934
- Reduced-dimension surrogate modeling (damage tolerance) — https://arxiv.org/pdf/2210.14054
- Tensorial ROMs for parametric coupled reaction-diffusion — https://arxiv.org/pdf/2603.14101

The only "training-free selection" found in this space is the **classical
singular-value energy criterion for rank r** (choose r by the proportion of
energy captured). The search engine explicitly reported no paper matching
"training-free selection of surrogate model form using dataset statistics".
No result selects the *centering/output parameterization* (direction x
amplitude vs additive) from a dataset statistic.

## Interpretation

Band-resolved spectral correction exists but is always either (i) learned
inside the architecture (TF-SNO, high-frequency scaling, IRNO) or (ii) a
test-time-observation-driven guidance term (FreqNO-DPS) — neither is a
post-hoc, out-of-fold gain fit on a frozen predictor's point output. The
closed-form control arm (PCA + ridge) is squarely published (PCA-RaNN), so any
B2 "tiny head" is a baseline, not a contribution. Rank selection by singular
value energy is classical; rank selection by *condition-identifiability*
(out-of-fold R^2 of each POD coefficient regressed on the parameters) was not
returned and needs a dedicated term in iteration 2.
