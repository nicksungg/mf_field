# iteration_2 — s1_poisson batch 2

## Search rationale

Turn 1 showed the *data-normalization* question is unstated in MF-NN papers.
Turn 2 attacks task item (b) from the numerics side: ifc_poisson's levels obey
a near-exact h² amplitude law (RMS ratios 4.379/4.196/4.120 ≈ 4 = 2² per
halving). Numerical analysis has owned that structure for a century
(Richardson extrapolation, MLMC level-variance decay). If anyone has folded a
**known or estimated convergence order into a learned multi-fidelity model** —
i.e. rescaled level differences by h^p before learning — that is the direct
prior art for "per-level scaling as an inductive bias", and it likely lives in
the extrapolation / multilevel-solver literature, not the operator-learning one.

## Search terms used

1. `machine learning discretization error convergence rate h^p scaling residual between grid levels known asymptotic rate rescale before learning`
2. `Richardson extrapolation neural network multi-fidelity learn correction known order of accuracy grid refinement surrogate`
3. `multilevel neural network training level-dependent scaling of residual corrections telescoping difference magnitude decays with level`

## Findings

### Term 1 — h^p error scaling exploited in ML

Mostly off-target (optimization scaling laws, LMM discovery). The one usable
idea: in deep-learning discovery of dynamics via linear multistep methods
[https://arxiv.org/pdf/2103.11488] the total error splits into discretization +
approximation + optimization terms with a threshold h*: for h > h* the O(h^p)
discretization term dominates and is observable; below h* optimization error
dominates. Relevant as framing (the h^p law is only exploitable while it
dominates), not as a method. **No source found that rescales training targets
by a known h^p rate.**

### Term 2 — Richardson extrapolation × multi-fidelity — STRONG HIT

**Oates et al., "Probabilistic Richardson Extrapolation" / Gauss–Richardson
Extrapolation (GRE)** [https://pmc.ncbi.nlm.nih.gov/articles/PMC11985099/]
(fetched). It "unifies classical extrapolation methods with modern
multi-fidelity modelling" by treating extrapolation as statistical regression.
Mechanically it **encodes the convergence order into the prior**: the error
bound b(x) — "typically ... b(x) = x^r, where r represents the convergence
order" — enters a non-stationary kernel
`k(x,x') := σ²[k₀² + b(x)b(x')k_e(x,x')]`, and the fetch's key sentence:
"**This design ensures the normalized error (f(x)−f(0))/b(x) behaves
regularly**, naturally accounting for convergence rates through kernel
structure." When r is unknown it is **estimated by maximum quasi-likelihood**
(§2.8). This is h^p-aware level normalization, in a GP, for scalar/functional
QoIs — i.e. exactly the mechanism B1's per-level scaler approximates
empirically.

(The same work was returned twice in this turn's results; ADS record for
provenance: [https://ui.adsabs.harvard.edu/abs/2024arXiv240107562O/abstract],
arXiv id 2401.07562 — search-return, not fetched.)

Second hit, weaker but on-axis: **neural-network-enhanced integrators**
[https://arxiv.org/pdf/2504.05493] — "Approximating the local truncation error
using neural networks instead of Richardson extrapolation yields more design
freedom, allowing ... tailored regularization terms, domain-specific weighting,
or alternative error norms." So NN-replaces-Richardson exists for ODE local
truncation error; the direction is *replace* the rate, not *exploit* it.

### Term 3 — level-dependent scaling in multilevel NN training — STRONG HIT

**Aldirany, Cottereau, Laforest, Prudhomme, "Multi-level neural networks for
accurate solutions of boundary-value problems"** (CMAME)
[https://www.sciencedirect.com/science/article/abs/pii/S0045782523007892]
(**fetch failed, HTTP 403** — search-return only, so cited as snippet-grade).
Engine-returned characterization, twice, unprompted: "The size of the residual
becomes increasingly smaller at each level, **which requires normalization of
the solution error at each level**", and "each level of the correction process
introduces higher frequencies in the solution error, which is why the sequence
of neural networks should be of increasing complexity." That is the
shared-vs-per-level normalization argument stated as an established
requirement — but in the *sequential residual-correction PINN* setting (one
network per level, corrections to a solution), not in *data-driven MF fusion
over a fidelity ladder with pooled targets*.

Also surfaced, not fetched: Multilevel minimization for deep residual networks
[https://arxiv.org/pdf/2004.06196], Multigrade Neural Network Approximation
[https://arxiv.org/pdf/2601.16884], Multiscale NNs for Green's functions
[https://arxiv.org/pdf/2410.18439].

## Interpretation

The h^p-aware normalization idea is **not novel in principle**: GRE encodes it
in a GP kernel (fetched, unambiguous) and multi-level residual PINNs are
reported to *require* per-level error normalization (snippet-grade). Neither
source is a data-driven neural-operator MF fusion model with pooled multi-level
targets and a shared output scaler, which is the configuration B1 measured. The
open slot is narrowing to: per-level target standardization inside a **single
shared** fidelity-conditioned operator trained on **pooled** ladder rows.
