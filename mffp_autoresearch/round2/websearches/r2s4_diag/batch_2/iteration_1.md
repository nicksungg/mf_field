# Iteration 1 — Q1: is there a published aleatoric/irreducible-error ceiling estimator that survives 19 dims and N=5?

## Search rationale

B1's headline instrument is a *training-free aleatoric barrier* estimated two
ways (noise-debiased LOO k-NN bound; matched-pair extrapolation to zero
condition distance) — and its part 7 asks B2 to build one that works where those
have no support (cahn_hilliard: 19 dims, min train-pair distance 2.822;
ifc_poisson: N_hf = 5). Before proposing "build an estimator", find out what the
statistics literature already calls this. Prior expectation: matched-pair
extrapolation IS difference-based variance estimation in nonparametric
regression, a 1980s-vintage field. Three terms: (1) the classical statistics
handle, (2) the ML handle (aleatoric uncertainty via neighbours), (3) the PDE-
surrogate handle (intrinsic stochasticity when the parameter vector is
incomplete — exactly ADR r2-0003's situation).

## Search terms used

1. `estimating irreducible noise variance nonparametric regression difference-based estimator high dimensional`
2. `nearest neighbor estimator of aleatoric uncertainty irreducible error machine learning regression`
3. `intrinsic stochasticity ceiling parametric PDE surrogate random initial condition not in parameter vector`

## Findings

### Term 1 — difference-based variance estimation

Established, named field. Search results surface three canonical estimator
families ("the sample variance method, the partitioning method, and the
sequencing method") and a **directly load-bearing high-dimensional caveat**
(SNIPPET-ONLY, from the search summary of the Springer review — the chapter
itself is paywalled, redirect to `idp.springer.com` blocked the fetch):
"the first order difference based estimator that achieves minimax rate of
convergence in the one-dimensional case does not do the same in the high
dimensional case … the optimal order of differences depends on the number of
dimensions."

- "Nonparametric Error Variance Estimation in Regression: A Review" —
  https://link.springer.com/chapter/10.1007/978-3-032-07178-1_19 (FETCH FAILED:
  303 redirect to an auth host; snippet only)
- "Difference-based variance estimation in nonparametric regression with
  repeated measurement data" —
  https://www.sciencedirect.com/science/article/abs/pii/S0378375815000403
- "Variance function estimation in multivariate nonparametric regression with
  fixed design" —
  https://www.sciencedirect.com/science/article/pii/S0047259X0800105X
- "The differogram: Non-parametric noise variance estimation and its use for
  model selection" —
  https://www.sciencedirect.com/science/article/abs/pii/S0925231205001682
  (the differogram is *literally* B1's matched-pair-extrapolation-to-zero-
  distance construction, published for model selection)
- "On estimation of the noise variance in high-dimensional linear models" —
  https://arxiv.org/abs/1711.09208 — **FETCHED**: adaptive normalization of
  squared errors + spectral regularizers of the MLE to handle the nuisance
  regression coefficients; "we derive the upper bound for the concentration of
  the proposed method around the ideal estimator (the case of zero nuisance)".
  The abstract does NOT state minimax rates or sparsity conditions (do not
  attribute those to it).

### Term 2 — aleatoric uncertainty via neighbours

The ML side uses the same idea under a different name. Search summary: "A
nearest neighbors approach is well-suited to estimating aleatoric uncertainty —
remaining uncertainty due to irreducible error or the inherent stochasticity in
the system — since it can quantify the range of outcomes to be expected given
the observed features" (SNIPPET, attributed in results to the IBUG paper).

- IBUG, "Instance-Based Uncertainty Estimation for Gradient-Boosted Regression
  Trees" — https://arxiv.org/pdf/2205.11412 — **FETCH FAILED** (undecodable PDF
  binary; same failure mode batch 1 documented). Snippet also notes IBUG tunes
  k on *held-out* data, so its estimate mixes aleatoric and epistemic — the
  opposite of B1's train-only LOO discipline.
- "Position: Epistemic uncertainty estimation methods are fundamentally
  incomplete" — https://arxiv.org/html/2505.23506v4 (not fetched)
- "One Step Closer to Unbiased Aleatoric Uncertainty Estimation" —
  https://ojs.aaai.org/index.php/AAAI/article/download/29627/31065 (not fetched)

### Term 3 — intrinsic stochasticity in PDE surrogates

- **TRINE**, "Learning stochasticity: a nonparametric framework for intrinsic
  noise estimation" — https://arxiv.org/html/2511.13701 — **FETCHED**: kernel-
  based three-phase regression that estimates state-dependent intrinsic noise
  from single trajectories and "does not require repeated measurements at
  identical input states"; explicitly separates measurement noise from intrinsic
  stochasticity. BUT: all tested systems are 1-2 D (Ricker, FitzHugh-Nagumo,
  gene networks), sample sizes 1000-2000 points, and the paper "contains no
  explicit discussion of high-dimensional scalability". It is a *dynamical-
  systems trajectory* method, not a parametric-map method — it does not transfer
  to our (condition vector -> field) setting.
- Search summary also states the general framing for our ADR r2-0003 situation:
  "When a model has intrinsic noise (for each fixed value of parameters, the
  output is a random quantity), surrogate construction is not straightforward
  since there is no explicit control on the random sample space element"
  (SNIPPET, attributed to https://arxiv.org/pdf/2311.00553, polynomial-chaos
  surrogates for random fields with parametric uncertainty; not fetched).
- Also surfaced, unfetched: "Out-of-distribution generalization of deep-learning
  surrogates for 2D PDE-generated dynamics in the small-data regime" —
  https://arxiv.org/html/2601.08404v1.

## Interpretation

B1's ceiling estimators are preempted in method — the matched-pair extrapolation
is the **differogram** and the LOO k-NN bound is textbook difference-based /
neighbour-based variance estimation — and the very failure B1 hit (no support at
19 dims) is a *known theorem-level* property of that estimator class in high
dimensions, not a bug in B1's implementation. No fetched source offers a
parametric-map irreducible-error estimator for field-valued outputs at N=5, so
the specific composition B2 wants is still open; but the honest B2 framing is
"apply/adapt a named published estimator class and report where it provably has
no support", not "invent a ceiling estimator".
