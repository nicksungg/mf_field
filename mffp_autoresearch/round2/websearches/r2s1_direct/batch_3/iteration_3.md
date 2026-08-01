# Iteration 3 — response-side predictable subspace, the rho formula, per-mode hybrids

## Search rationale

Iteration 2 showed the right statistics frame for direction C is not
feature-side PLS but **response-side** low-rank structure: "which directions of
the OUTPUT field are predictable from the condition" = reduced-rank regression.
Also retry the explicit two-forecast weight formula in terms of rho, and probe
whether "hybrid ROMs that pick a different regressor per mode" exist.

## Search terms used

1. `reduced-rank regression predictable subspace of multivariate response versus principal components of response`
2. `optimal combination weight formula (sigma2^2 - rho sigma1 sigma2)/(sigma1^2 + sigma2^2 - 2 rho sigma1 sigma2) two forecasts`
3. `hybrid surrogate selecting a different regression model for each POD mode non-intrusive ROM model selection per mode`

## Findings

### Term 1 — reduced-rank regression / response predictable subspace
Returns: "Principal component-guided sparse reduced-rank regression"
(https://arxiv.org/html/2601.07202); "Multivariate reduced rank regression by
signal subspace matching"
(https://www.sciencedirect.com/science/article/abs/pii/S0165168424000446);
"A note on rank reduction in sparse multivariate regression"
(https://pmc.ncbi.nlm.nih.gov/articles/PMC4797956/).
Engine text draws exactly the distinction we need: *"the predictable subspace in
reduced-rank regression focuses on the variance in the response that can be
explained by the predictors, whereas principal component analysis of the
response identifies the directions of maximum variance in the response itself,
regardless of predictability."* **Search return only.**
**Fetched**: https://arxiv.org/html/2601.07202 (Goto et al., "Principal
component-guided sparse reduced-rank regression") -> the fetch reports the paper
biases coefficients toward principal directions of the **explanatory** variables,
and *"does not appear to address"* energy-ranked response PCs vs the predictable
response subspace. **Fetched but NEGATIVE for our question** -- recorded, not
used as a preemption citation.

### Term 2 — the two-forecast weight in terms of rho
Returns: forecast-combination-puzzle papers (https://www.mdpi.com/2225-1146/7/3/39 ;
https://www.janmagnus.nl/papers/JRM113a.pdf), Wang & Hyndman review
(arXiv:2205.04216), and CRAN `MuMIn::BGweights`
(https://search.r-project.org/CRAN/refmans/MuMIn/html/BGweights.html ;
https://rdrr.io/cran/MuMIn/man/BGweights.html), plus arXiv:2602.11379.
The engine returned the closed form
`alpha* = (sigma_2^2 - rho sigma_1 sigma_2)/(sigma_1^2 + sigma_2^2 - 2 rho sigma_1 sigma_2)`
with *"rho is the correlation coefficient of the forecasting errors between the
models"* -- **search return only, no source attributed; not a citation.**
**Fetch attempted**: https://www.mdpi.com/2225-1146/7/3/39 -> **HTTP 403.**

### Term 3 — per-mode hybrid ROMs
Returns: error-learning surrogate for convection-dominated parametric problems
(https://arxiv.org/html/2605.29769); non-intrusive ROMs for partitioned FSI
(https://www.sciencedirect.com/science/article/abs/pii/S0889974624000914);
POD-Kriging / POD-PCE hybrids. Engine conclusion: *"specific mention of
selecting entirely different regression models for each individual POD mode
wasn't explicitly detailed in these results. The typical approach involves using
POD for dimensionality reduction, then applying a unified regression strategy to
the POD coefficients."* **Search return only.**

## Interpretation

Two independent engine passes now say the same thing about direction A: the
literature standard is *one shared regressor family applied to all modal
coefficients* (fitted independently per mode), and per-mode **family** selection
was not surfaced. The response-side "predictable subspace" concept is textbook
reduced-rank regression, but the one paper fetched was about predictor-side PCs,
so the preemption for direction C still needs a fetched source.
