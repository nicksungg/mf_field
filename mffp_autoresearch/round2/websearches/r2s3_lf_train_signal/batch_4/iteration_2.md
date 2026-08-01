# Iteration 2 — the gain channel from the conditioning / calibration vocabulary

## Search rationale

Turn 1 showed the PDE-surrogate vocabulary does not name a per-sample gain
head. B3's mechanism is really two generic objects wearing PDE clothes:
(i) a **conditioning mechanism that emits a scale** (FiLM γ is literally a
learned multiplicative scale — the round's own decoders are FiLM-conditioned,
so a "gain head" may be a special case of something the field considers
trivial), and (ii) a **post-hoc de-shrinkage / scale recalibration** of a
regressor whose training objective shrank its outputs toward the mean —
exactly B3's M2 ("relative-L2 rewards under-predicting amplitude at the
conditional-mean bound"). Turn 2 attacks both, plus the shape/magnitude
factorisation that a gain head implicitly assumes.

## Search terms used

1. `hypernetwork predicts output scale conditioning FiLM affine modulation amplitude recalibration regression few-shot`
2. `regression calibration multiplicative scale correction predicted signal magnitude shrinkage bias correction learned surrogate`
3. `two-stage shape and magnitude decomposition prediction normalize field predict norm separately deep learning spatial field`

## Findings

### Term 1 — conditioning that emits a scale

- **Distill, "Feature-wise transformations"** —
  https://distill.pub/2018/feature-wise-transformations/ [search return].
  Engine synthesis: "The FiLM generator is a specialized HyperNetwork that
  predicts the FiLM parameters of the FiLM-ed network… FiLM requires
  predicting far fewer parameters than Hypernetworks, but also has less
  modulation potential"; FiLM "applies feature-wise affine transformations…
  By leveraging learned scaling (gamma) and shifting (beta) parameters".
  **Consequence for direction (a)**: a condition→per-sample-scalar-gain head
  is, at mechanism level, a degenerate FiLM/hypernetwork (one γ on the output
  layer). The *mechanism* is textbook; only the empirical claim (how much of
  the LF-attributed value it recovers at N_hf = 5) can be open.
- **CoDA — Generalizing to New Physical Systems via Context-Informed Dynamics
  Model** — https://arxiv.org/pdf/2202.01889 [search return]: context-vector
  conditioning of dynamics models across physical systems; conditioning-from-a
  -parameter-vector for PDE dynamics is established.
- **Conditional Neural Field ROM for ditching load prediction** —
  https://arxiv.org/pdf/2605.21499 [search return]: condition→field ROM;
  another instance of the r2s1 genre, no amplitude head.

### Term 2 — post-hoc de-shrinkage of a regressor (the decisive hit)

- **"Debiasing Machine Learning Predictions for Causal Inference Without
  Additional Ground Truth Data: 'One Map, Many Trials'"** —
  https://arxiv.org/abs/2508.01341 **[curl-fetched: abstract + HTML body]**.
  Verbatim from the abstract: "because standard training objectives prioritize
  overall predictive accuracy, these predictions often suffer from
  **shrinkage toward the mean**, leading to attenuated estimates…"; "We
  introduce and evaluate two post-hoc correction methods — **Linear
  Calibration Correction (LCC)** and a **Tweedie's correction** approach —
  that substantially reduce shrinkage-induced prediction bias **without
  relying on newly collected labeled data**. LCC applies a simple linear
  transformation estimated on a **held-out calibration split**; Tweedie's
  method locally de-shrink predictions using density score estimates and a
  noise scale learned upstream."
  Body [curl-fetched]: LCC posits "𝔼[Ŷ_i | Y_i, A_i] = k Y_i + m, k > 0" and
  is applied to "a black-box model, requiring **no specialized retraining or
  customized loss function** that might reduce predictive performance"; the
  results section states "the linear calibration correction also performs
  nearly as well despite its simplicity, suggesting that **much of the bias
  arises from a first-order scaling distortion that can be identified on a
  small held-out calibration set**." The paper also notes the alternative of
  baking distribution-matching into training via "the mean squared error loss
  with an ℓ₂ penalty and a **quintile-bias term**", and flags "bias-variance
  trade-offs in the Tweedie family" as future work. Explicitly domain-general:
  "the methods are not geospatial-specific: they apply to any setting where
  imputed outcomes are reused downstream."
  **Scope limits (what it is NOT)**: scalar outcomes, not fields; a **global**
  (k, m) affine map, not a **per-sample gain conditioned on the parameter
  vector**; the target functional is downstream causal-effect bias, **not**
  prediction error — and its own framing warns that de-shrinking can cost
  predictive accuracy, which is precisely B3's M2 sign prediction.
- **CHRep: post-hoc calibration for spatial gene expression** —
  https://arxiv.org/pdf/2604.21573 [search return]: post-hoc calibration of a
  spatial prediction head; not fetched, listed as a nearer-than-expected
  neighbour for "post-hoc calibration of a spatially-resolved regressor".
- **Multiplicative Signal Correction** (chemometrics) — US patent 5568400
  https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/5568400 and
  https://www.sciencedirect.com/science/article/abs/pii/S016974390700216X
  [search returns]: per-sample multiplicative + additive scatter correction is
  a 30-year-old standard in spectroscopy calibration transfer. The *idea* of
  removing a per-sample multiplicative factor before comparing signals is old
  and named.

### Term 3 — shape/magnitude factorisation

- **End-to-end epicentral distance and magnitude determination from single
  station waveforms** —
  https://www.sciencedirect.com/science/article/pii/S2590197426000406
  [search return; **curl fetch returned a JS/paywall shell, body NOT usable** —
  flagged, no quote taken]. Engine synthesis only: "A pseudo-normalization
  strategy facilitates joint prediction through **label-level decoupling**,
  where normalized input is tasked with predicting magnitude contribution
  derived from waveform morphology. The final physical magnitude is recovered
  in post-processing by summing the network's probabilistic output with a
  **scale factor**." Treat as a search return, not a citation of record.
- **"From Cheap Geometry to Expensive Physics: Elevating Neural Operators via
  Latent Shape Pretraining"** — https://arxiv.org/html/2509.25788 [search
  return]: cheap-source → expensive-target pretraining for neural operators;
  relevant to the stream's LF-pretrain baseline genre, queued for turn 4 if a
  budget question needs it.
- Engine synthesis on normalization practice: "data is normalized and relative
  L2 error is computed on the normalized physics field for training loss and
  evaluation" [search return] — confirms the field's default is a *global*
  normalization, so per-sample output-scale handling is not standard practice
  in PDE surrogates even though it is standard in chemometrics.

## Interpretation

Direction (a)'s mechanism is preempted twice over at the generic level — as a
degenerate FiLM/hypernetwork scale (Distill) and as post-hoc de-shrinkage
calibration fitted on a small held-out split (LCC/Tweedie,
https://arxiv.org/abs/2508.01341, explicitly claimed domain-general) — but
neither instance is per-sample-conditioned, field-valued, or evaluated in a
regime where the alternative to calibration is *buying auxiliary low-fidelity
simulation data*. That last clause is the only thing the stream can still own,
and turn 3 must test whether even it has been done.
