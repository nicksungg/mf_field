# iteration_2 — `r3s1_factorised`, batch 1

## Search rationale

Turn 1 established that (a) cross-coefficient completion is published for
*temporal* POD coefficients on an attractor, and (b) the propagation-aware gate
is textbook out-of-fold stacking. The two remaining questions are parametric:
does anyone do coefficient-on-coefficient completion for a **parameter→field**
surrogate, and is there a published statement of the M15 condition-dimension
effect (per-mode maps starve as parameter dimension grows; a shared /
cross-output stage recovers)? Round 3's panel makes M15 testable at n = 4
(cond_dim 18/19/19/50 vs round 2's single 19-dim cell), so pinning its prior art
is the highest-value search this turn.

## Search terms used

1. `parametric reduced order model regress POD coefficients hierarchically second stage coefficient dependence high-dimensional parameter Karhunen-Loeve input`
2. `curse of dimensionality parametric surrogate high dimensional random field parameter POD coefficient regression accuracy degrades`
3. `independent per-mode regression versus joint multi-output model POD coefficients correlated modes surrogate comparison`

## Findings

### Term 1 — parametric POD-coefficient regression, hierarchy

Returns: parametric MOR by ML for FSI
<https://link.springer.com/article/10.1007/s00366-023-01782-2>;
*Reduced-Order Models and Conditional Expectation: Analysing Parametric
Low-Order Approximations* <https://doi.org/10.3390/computation13020058>
(fetch attempt returned 233 chars — MDPI blocked; **NOT usable as a citation**);
LES pollutant-dispersion parametric ROM <https://arxiv.org/pdf/2208.01518>;
non-intrusive Navier–Stokes ROM
<https://people.sc.fsu.edu/~inavon/pubs/CMAME%20_293.pdf>.

The decisive statement in the aggregated search return is the standard
justification for the per-mode shape this stream is attacking: *"Because POD
reduced coefficients are decorrelated, independent regression models can be
designed for each coefficient to learn the relationship between coefficients and
parameters."* (search-return synthesis over the parametric-ROM results above;
**not fetched — SEARCH-RETURN ONLY**). Note the logical gap this exposes and
which the stream can exploit: POD coefficients are **linearly** decorrelated by
construction; that licenses nothing about **nonlinear** cross-coefficient
dependence, which is exactly the structure B3-F24 measured at OOF R² 0.92–0.94
on cahn_hilliard.

### Term 2 — curse of dimensionality in parametric surrogates

**FETCHED**: *A Multi-Fidelity Methodology for Reduced Order Models with
High-Dimensional Inputs*, <https://arxiv.org/html/2402.17061v1> (retrieved
2026-08-07, 135,612 chars). Verbatim: *"these spaces introduce significant
challenges, including the **curse of dimensionality, which stems from both
high-dimensional inputs and outputs** necessitating substantial training data
and computational effort. To address these complexities, this study introduces a
novel multi-fidelity, parametric, and non-intrusive ROM framework designed for
high-dimensional contexts."* Its remedy is **input-side**: active-subspace-style
(ASM) linear input dimension reduction plus PCA on outputs (PCAS), with the
multi-fidelity part supplying cheap samples; *"our methodology outperforms the
manifold-aligned ROM (MA-ROM) method by 50% in handling scenarios with large
input"*. It does **not** do output-coefficient-on-output-coefficient completion.

Other returns, not fetched: DR-in-surrogate-modelling review
<https://pmc.ncbi.nlm.nih.gov/articles/PMC9633505/> (already cited by the
round-2 r2s1-B3 loop); PCE + sparse PLS
<https://www.sciencedirect.com/science/article/abs/pii/S004578252030089X>; GP on
the Grassmann manifold
<https://www.sciencedirect.com/science/article/abs/pii/S0045782520304540>.
Aggregated search return: *"An inherent limitation of many surrogate models is
their susceptibility to the curse of dimensionality, which traditionally limits
their applicability to a maximum of O(10²) input dimensions."* — i.e. the
literature's dimension worry starts around 10², well above this panel's 18–50,
so M15's "starved at cond_dim ≥ ~10, with 320–400 fit rows" is NOT the classical
curse-of-dimensionality statement; it is a rows-per-dimension statement.

### Term 3 — independent per-output vs joint multi-output

**FETCHED**: Chen, Fan & Wang, *"When is multivariate kriging worthwhile? A
design-geometry analysis of heterotopic multi-output Gaussian processes"*,
<https://arxiv.org/abs/2607.06832> (retrieved 2026-08-07). Verbatim from the
retrieved abstract: *"Whether a joint multivariate kriging metamodel then
predicts better than separate univariate metamodels **has remained unresolved**:
careful simulation comparisons on common designs report little or no benefit
from multivariate kriging, yet the multi-fidelity and geostatistical literatures
are built on the premise that auxiliary outputs help."* Their answer is
design-geometry: *"We introduce **model-free diagnostics that can be computed
before fitting**, namely directed coverage, directed proximity and borrowing
potential indices"*, *"an exact identity for the oracle prediction gain of joint
modelling"*, and *"the estimability of cross-output dependence is controlled by a
kernel-weighted cross-design interaction mass"*, combined into *"a first-order
net benefit criterion for deciding when joint modelling is worthwhile."*
Crucially, their setting is **heterotopic** (different outputs observed at
different input locations) — the gain comes from design geometry, not from a
predictor being fed another output's *prediction*.

Other returns, not fetched: parametric ROM + ML spatial emulation
<https://arxiv.org/pdf/2308.14566>; nonlinear compressive reduced basis
<https://arxiv.org/pdf/2407.03769>.

## Interpretation

The "is cross-output borrowing worthwhile?" question is live and explicitly
unresolved in the metamodelling literature (arXiv:2607.06832), and its published
answer is a **pre-fit design-geometry criterion**, not a condition-dimension
criterion and not a two-stage predicted-coefficient cascade — which leaves M15's
specific discriminator open. The standard per-mode independence argument rests
on **linear** decorrelation of POD scores, a gap the two-stage head exploits;
that framing is available and citable. `ENOUGH` on field context — turns 3–5 go
to §3.3 refutation searches.
