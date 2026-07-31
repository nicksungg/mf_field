# Iteration 2 — the two part-7 options in their own literatures

## Search rationale

Iteration 1 established that the generative work sits DOWNSTREAM of the deterministic operator
and that coherence-as-prerequisite has a close published neighbour. This iteration attacks the
two concrete B2 options on their own terms:
(A) is the mean-vs-sample trade the card worries about ("an independent sample has coherence 0
in expectation and scores WORSE than the mean under relative L2") already measured in
scientific super-resolution, and is the K-sample posterior mean the standard answer;
(B1) is a factorised amplitude x shape head established for resonance-dominated parametric
wave surrogates (the helmholtz LEARNING-gap fix);
(B2) is "PCA/POD basis + closed-form ridge in the parameter" — which is exactly what B1's
mechanism analysis found ifc_poisson to be (rank-8 PCA + ridge exact to 6.2e-08) — simply the
classical non-intrusive reduced-basis method, in which case any ifc_poisson "closed-form head"
proposal is a rediscovery and must be declared as a baseline, not a contribution.

## Search terms used

1. `diffusion samples versus ensemble mean relative L2 error PDE super-resolution posterior mean sharper but worse pointwise`
2. `parametric Helmholtz neural operator resonance amplitude failure factorized amplitude shape decomposition surrogate frequency`
3. `POD reduced basis regression parameter to coefficients outperforms neural operator small training set POD-NN linear closed form`

## Findings

### Term 1 — sample vs ensemble mean under a pointwise metric

- "PODiff: Latent Diffusion in Proper Orthogonal Decomposition Space for Scientific
  Super-Resolution" — https://arxiv.org/html/2605.03399 (snippet-level, not fetched).
- "Solving Inverse Problems via Diffusion-Based Priors: An Approximation-Free Ensemble Sampling
  Approach" — https://arxiv.org/html/2506.03979 (snippet-level).
- "Diffusion Posterior Sampling for Super-Resolution under Gaussian Measurement Noise" —
  https://arxiv.org/abs/2512.21797 (snippet-level).
- Search-engine synthesis of these results: ensemble means from diffusion posterior samples
  give low RMSE/MAE with "Monte Carlo error of the posterior mean decays as K^(-1/2)", and
  "stochastic sampling not degrading reconstruction accuracy in controlled PDE settings"; the
  engine explicitly stated the specific sample-worse-than-mean-pointwise trade "isn't
  explicitly discussed in these search results". Treat as snippet-level only.
- Already in repo (do not re-derive): `docs/reports/MF_Sharp_HighFreq_Report.md` line 203/317 —
  "use generative models via a K-sample posterior *mean*, not single-sample realism", PDE-Refiner
  arXiv:2308.05732; line 221 perception-distortion under SR3 arXiv:2104.07636; line 252 the
  RG argument that inverse coarse-graining is necessarily stochastic (arXiv:1704.06279).

So: the K-sample-posterior-mean workaround is field-standard and already documented in-repo.
**But note what that implies for r2s2 option (A): the K-sample mean IS the conditional mean,
i.e. it returns exactly the object whose band>=1 coherence B1 measured at <= 0.52.** No fetched
source claims a generative stage-1 restores coherence for a downstream deterministic corrector.

### Term 2 — factorised amplitude/shape heads for resonant parametric problems

- **[VERIFIED, abs fetched]** "Factorized Neural Operators Decompose Dynamic and Persistent
  Responses" (FaNO) — https://arxiv.org/abs/2606.16900. Abstract verbatim: decomposes "spectral
  representations into equivariant-inspired dynamic responses and invariant-inspired persistent
  responses". This is a **transient-vs-persistent** factorization, NOT amplitude x spatial
  pattern; the fetch confirmed "No mentions of resonance or Helmholtz equations appear in the
  provided content."
- "FFT-Free Neural Operators for Helmholtz Scattering via Adaptive Coefficient Modulation"
  (HNO) — https://doi.org/10.3390/app16125997 (snippet-level): DeepONet-family branch-trunk
  with "bounded multiplicative gating on per-mode coefficients" and a "dual-path rank-32
  hypernetwork branch" — the closest published neighbour of a gated amplitude pathway, in the
  Helmholtz setting.
- "Out-of-distributional risk bounds for neural operators with applications to the Helmholtz
  equation" — https://arxiv.org/pdf/2301.11509 (snippet-level).
- "Learned frequency-domain scattered wavefield solutions using neural operators" —
  https://arxiv.org/html/2405.01272 (snippet-level).

### Term 3 — POD/reduced-basis + regression on the parameter

- **[VERIFIED, fetched — as a NEGATIVE]** "PODNO: Proper Orthogonal Decomposition Neural
  Operators" — https://arxiv.org/html/2504.18513v1/. The fetch confirms PODNO uses POD bases
  *inside* neural-operator kernel-integration layers and is "not a classical reduced-order model
  mapping parameters to coefficients"; it does not cite Hesthaven & Ubbiali and does not discuss
  affine parameter→coefficient maps or tiny training sets. So PODNO is NOT the prior art for the
  ifc_poisson closed-form head; the classical POD-NN line is (see below, needs verification).
- "Non-intrusive reduced order modeling of nonlinear problems using neural networks"
  (Hesthaven & Ubbiali, JCP 2018) —
  https://www.sciencedirect.com/science/article/abs/pii/S0021999118301190 (snippet-level;
  ScienceDirect 403s under WebFetch per batch-1 dead ends). Snippet: "extracts a reduced basis
  from a collection of high-fidelity solutions via proper orthogonal decomposition (POD) and
  employs artificial neural networks ... to accurately approximate the coefficients of the
  reduced model" — i.e. precisely parameter → POD-coefficient regression.
- "Non intrusive reduced order modeling of parametrized PDEs by kernel POD and neural networks"
  (Salvador, Dede', Manzoni) —
  https://www.sciencedirect.com/science/article/abs/pii/S0898122121003928 (snippet-level).
- "Neural-POD: A Plug-and-Play Neural Operator Framework for ... Nonlinear POD" —
  https://arxiv.org/html/2602.15632v2 (snippet-level).

## Interpretation

Option (B2)'s "closed-form / linear-in-condition head on ifc_poisson" is the classical
non-intrusive POD/reduced-basis method and should be declared a **baseline arm**, not a
mechanism — a targeted verification fetch is still owed (iteration 3) because ScienceDirect
blocks. Option (B1)'s amplitude x shape factorization has no exact published match yet: the
nearest neighbours factorize along different axes (FaNO: transient/persistent; HNO: per-mode
multiplicative gating). Option (A) is weakened rather than supported by this turn: the field's
standard fix for generative sharpness under a pointwise metric is the K-sample posterior mean,
which is the conditional mean B1 already measured at the failing coherence.
