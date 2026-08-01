# Iteration 2 — statistics vocabulary: Bates-Granger, PLS/supervised DR, per-mode CV

## Search rationale

Iteration 1 left two gaps: (i) no fetched citation for the closed-form optimal
two-way combination weight in terms of error correlation (the mechanism behind
B2's blend-payoff law); (ii) direction C ("fit the identified SET of predictable
modes, not the leading energy window") returned nothing under ROM vocabulary --
retry under statistics vocabulary, where supervised dimensionality reduction
lives. Also probe whether *cross-validated per-mode model choice* is named
anywhere.

## Search terms used

1. `Bates Granger optimal combination weight two forecasts formula error correlation rho variance`
2. `partial least squares output basis versus POD for parameter to field surrogate supervised dimensionality reduction`
3. `independent regressor per POD mode different model family selected by cross validation modal coefficient`

## Findings

### Term 1 — Bates-Granger
Returns: Elliott, "Averaging and the Optimal Combination of Forecasts"
(https://econweb.ucsd.edu/~grelliott/AveragingOptimal.pdf); Wang & Hyndman,
"Forecast combinations: an over 50-year review" (arXiv:2205.04216);
Hansen lecture notes (https://users.ssc.wisc.edu/~behansen/390/390Lecture23.pdf).
Engine text: *"The seminal work of Bates and Granger (1969) proposed a method to
find the so-called 'optimal' weights by minimizing the variance of the combined
forecast error, and discussed only combinations of pairs of forecasts"*, with
`w_opt = (Sigma^-1 1)/(1' Sigma^-1 1)`. **Search return only.**
**Fetch attempted**: https://users.ssc.wisc.edu/~behansen/390/390Lecture23.pdf ->
**binary PDF, no extractable text. Cited for nothing.**

### Term 2 — PLS / supervised DR vs POD
Returns: "Dimensionality Reduction in Surrogate Modeling: A Review of Combined
Methods" (https://pmc.ncbi.nlm.nih.gov/articles/PMC9633505/ ; also
https://link.springer.com/article/10.1007/s41019-022-00193-5); KPLS kriging
papers.
**Fetched**: https://pmc.ncbi.nlm.nih.gov/articles/PMC9633505/ ->
- *"supervised methods produce more suitable topology representations of
  input-output maps compared to unsupervised methods"* (PLS/LDA vs PCA/POD);
- on output-side basis selection: *"The review does **not** discuss or recommend
  selecting reduced bases specifically optimized for output predictability.
  Basis selection throughout focuses on variance/energy criteria"*;
- on how many components: *"The number of retained r components is selected
  based on captured variance of the full data. There is no discussion of
  selecting components based on their predictive contribution to the surrogate
  model's output accuracy."*

### Term 3 — per-mode model choice by CV
Returns: POD mode coefficient interpolation for reactor kinetics
(arXiv:2303.08872); POD modal coefficients via active subspaces
(arXiv:1907.12777); LES pollutant-dispersion ROM (arXiv:2208.01518).
Engine text: *"Because POD reduced coefficients are decorrelated, independent
models can be designed for each reduced coefficient"* and, on the exact
composition asked for, *"the specific combination of 'independent regressor per
POD mode with different model family selection via cross-validation' appears to
be a specialized technique used in specific reduced-order modeling
applications"* -- i.e. the engine did not name a source. **Search return only.**
**Fetch attempted**: https://arxiv.org/abs/2303.08872 -> abstract page only;
the fetch reports it *"doesn't specify whether separate interpolants are fitted
per mode or how model selection occurs"*. **Low-information; not used as
evidence.**

## Interpretation

The supervised-DR review is a usable fetched citation with a two-edged content:
supervised (label-aware) dimensionality reduction is established and preferred
for input-output maps, but that same review explicitly does NOT select retained
components by predictive contribution -- which is precisely B2's arity repair.
The Bates-Granger closed form is clearly the mechanism behind the blend law but
still lacks a fetched source (PDF extraction failed).
