# Iteration 2 — per-sample output scaling and robust scalers

## Search rationale

Open questions Q2 and Q3. Iteration 1 established that the reference operator
implementation is dataset-level per-channel Gaussian and structurally *cannot*
be per-sample (batch dim always reduced). B1 part 7 nonetheless names
per-sample scaling as the leading candidate (per-sample HF norms span 408x
under one global `max|Y|`). The decisive question for §12.5 is therefore
whether per-sample normalize-then-denormalize is published as a **model-agnostic
normalization wrapper** (knob) or only as a scalar prediction head
(architecture). Second, whether robust/quantile scalers are the documented
answer to a max-abs scaler set by one extreme sample.

## Search terms used

1. `per-sample normalization neural operator instance normalization input output scale prediction amplitude rescaling surrogate`
2. `robust quantile scaler versus max-abs normalization scientific machine learning outliers target scaling regression`
3. `reversible instance normalization RevIN per-sample denormalization output model-agnostic distribution shift`

## Findings

### Term 1 — per-sample / instance normalization for surrogates
- The operator-learning-specific query mostly returned style-transfer AdaIN
  patents and unrelated work; **no usable neural-operator per-sample output
  scaling result from this term**. Its one on-target hit was
  https://arxiv.org/html/2603.11869 ("On the Role of Reversible Instance
  Normalization"), which term 3 pursues. Also surfaced but not fetched:
  Permuted AdaIN https://arxiv.org/pdf/2010.05785 (image classification,
  global-statistics bias) — off-domain, not used.

### Term 2 — robust vs max-abs scaling — USABLE (methods-level, not PDE)
- Fetched https://scikit-learn.org/stable/auto_examples/preprocessing/plot_all_scaling.html .
  Verbatim: *"Both StandardScaler and MinMaxScaler are very sensitive to the
  presence of outliers"*; *"MaxAbsScaler therefore also suffers from the
  presence of large outliers"*; and for the robust alternative *"the centering
  and scaling statistics of RobustScaler are based on percentiles and are
  therefore not influenced by a small number of very large marginal
  outliers"*, with *"RobustScaler and QuantileTransformer are robust to
  outliers in the sense that adding or removing outliers in the training set
  will yield approximately the same transformation."* Caveat also recorded
  there: *"QuantileTransformer will also automatically collapse any outlier by
  setting them to the a priori defined range boundaries (0 and 1). This can
  result in saturation artifacts for extreme values."*
  Reference doc for the estimator itself:
  https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.RobustScaler.html
  (returned by search; not fetched separately).
- Interpretation for us: the max-abs sensitivity statement is exactly the
  champion's situation (`scaler = max|Y_train|`, one extreme field sets the
  scale for all). This is textbook/library-documented, i.e. **the robust-scaler
  swap is a standard practice with zero novelty**, which is the correct posture
  for a `tuning` card.
- Searched-but-unfetched leads (NOT citable): "The Impact of Feature Scaling In
  Machine Learning" https://arxiv.org/pdf/2506.08274 ;
  https://machinelearningmastery.com/robust-scaler-transforms-for-machine-learning/ .

### Term 3 — RevIN — the decisive knob-vs-architecture evidence
- Fetched https://arxiv.org/html/2603.11869 ("On the Role of Reversible
  Instance Normalization"). It states RevIN's mechanism explicitly:
  statistics are per instance over the look-back window,
  `mu_x = (1/L) sum_i x_i`, `sigma_x^2 = (1/(L-1)) sum_i (x_i - mu_x)^2`, and
  the pipeline is
  `x_tilde = alpha (x - mu_x)/sigma_x + beta`,
  `y_hat = sigma_x (f_theta(x_tilde) - beta)/alpha + mu_x`
  — i.e. **normalize the input per sample, run any model, denormalize the
  output with the same per-sample statistics**. The paper explicitly frames it
  as *"a preprocessing and postprocessing technique applicable across
  architectures"*, a *"normalization wrapper rather than an architectural
  modification"*. Its own ablations report: the learnable affine parameters
  (alpha, beta) are *"not beneficial in practice"*; **training in normalized
  space outperforms denormalized training**; and RevIN *"does not address all
  forms of heterogeneity"*, in particular **conditional distribution shift
  between input and output statistics** — the failure mode that matters for us,
  because our per-sample scale would have to be estimated from something other
  than the target.
- Original RevIN confirmed first-hand at https://seharanul17.github.io/RevIN/ :
  *"a generally applicable normalization-and-denormalization method with
  learnable affine transformation"*, model-agnostic, removing non-stationary
  information *"in the input layer and then restoring it in the output layer"*,
  reported significant forecasting improvements (ETT, ECL, Nasdaq). Other
  primary endpoints located: https://openreview.net/forum?id=cGDAkQo1C0p ,
  https://iclr.cc/virtual/2022/poster/6034 , https://github.com/ts-kim/RevIN
  (not fetched — the two above suffice).

## Interpretation

Per-sample normalize-and-denormalize is **published, and published precisely as
a model-agnostic pre/post-processing wrapper**, not as an architecture change —
that settles the §12.5 admissibility question in favour of s5 owning it, and
simultaneously kills any novelty claim. But RevIN derives its per-sample
statistics **from the model's own input**; our champion's input is a
`[batch, cond_dim]` vector with no field, so a RevIN-faithful port must take
the per-sample scale from a field that is available at inference (the LF field)
or from a predictor of it. RevIN's own documented limitation — conditional
shift between input and output statistics — is the exact risk of using LF
statistics to denormalize an HF prediction. Robust/quantile scaling is
library-documented standard practice against exactly the champion's max-abs
outlier sensitivity, with a documented saturation caveat for the quantile
variant.
