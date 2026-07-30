# Iteration 1 — s2_beyond_copy batch 3

## Search rationale
B2's part-7 priority list names three non-architectural levers: (2) per-sample
target normalization (F10), (3) per-sample trust gate (F12), plus the tail
structure failure (F7/F11). Turn 1 opens the two *training-side* levers
(normalization, tail-aware weighting) and the *benchmark-hygiene* question the
mentor note needs (misregistration contaminating SR/MF claims).

## Search terms used
1. `per-sample instance normalization of regression targets neural operator PDE surrogate varying magnitude scales`
2. `heavy-tailed error distribution hard sample reweighting training neural PDE surrogate worst-case samples`
3. `grid alignment convention misregistration half-pixel shift contaminates super-resolution benchmark evaluation bicubic baseline`

## Findings

### Term 1 — per-sample target normalization in operator learning
Top results: Operator Boosting (https://arxiv.org/html/2606.17460), P3D
(https://arxiv.org/html/2509.10186, uses *adaptive instance normalization* but
as a conditioning mechanism, not target scaling), Latent Neural Operator
(https://proceedings.neurips.cc/paper_files/paper/2024/file/39f6d5c2e310a5a629dcfc4d517aa0d1-Paper-Conference.pdf),
deep transfer operator learning (https://arxiv.org/pdf/2204.09810), two
emergentmind topic pages on surrogate modeling.
**No result addresses per-sample (instance) normalization of the regression
TARGET for scale-spanning fields.** The surrogate-modeling topic page describes
the standard as global "normalization/standardization (zero mean, unit
variance)". Weak/no direct hit — the specific mechanism is not surfaced by this
framing. Deferred to a sharper framing in iteration 2.

### Term 2 — heavy-tail / hard-sample-aware training (STRONG)
- **ELADO: Elliptic PDE Assessment Datasets for Operator Learning** —
  fetched abstract at https://arxiv.org/abs/2606.20771 (the
  `/pdf/2606.20771` fetch returned undecoded binary — dead, see Dead ends).
  Abstract isolates as one of five difficulty sources: *"heavy-tailed solution
  distributions arising from light-tailed coefficient field distributions"*.
  Establishes that heavy-tailed target amplitude is a **named, benchmarked**
  difficulty axis in operator learning, and that the standard metric is "the
  mean relative L2 error".
- **"A numerical study into neural network surrogate model performance for
  uncertainty propagation"** — FETCHED https://arxiv.org/html/2605.16078.
  Directly on point and partly *negative*: *"models are primarily ranked based
  on their prediction accuracy in the tails of the thermal field
  distribution"*; *"worst-case prediction errors of the neural networks are an
  order of magnitude larger than the mean field error"* (one extrapolated
  sample 15.6x its mean error). They implemented cost-sensitive weighting with
  weights inversely proportional to sample probability density, aiming to
  "drive the distribution of the loss function towards a uniform distribution"
  — and it **backfired on test data**, raising max error from 76.63 K to
  96.72 K while improving training performance.
- **Residual-Quantile Adjustment (RQA)** for adaptive PINN training
  (https://arxiv.org/pdf/2209.05315, search-listed): reweighting by the
  residual distribution, "resetting values above certain quantiles toward
  median values" to stop a few large-residual points dominating.
- R3 sampling for PINNs (https://arxiv.org/pdf/2207.02338, search-listed) —
  collocation resampling, PINN-specific (ADR 0009 adjacent).

### Term 3 — misregistration contaminating SR/MF benchmarks
- Bart Wronski, "Bilinear down/upsampling, aligning pixel grids, and that
  infamous GPU half pixel offset" (https://bartwronski.com/2021/02/15/bilinear-down-upsampling-pixel-grids-and-that-half-pixel-offset/,
  search-listed): the two conventions (align pixel corners vs pixel centers);
  "odd length filters can stay centered, while even length filters shift the
  signal or image by half a pixel" — exactly our `grid_mode=True` defect, but
  as graphics folklore, not a benchmark-contamination paper.
- **Enhanced Super-Resolution Training via Mimicked Alignment for Real-World
  Scenes** (https://arxiv.org/pdf/2410.05410, search-listed): "inadequate
  alignment processes during training lead to super-resolution models that
  introduce geometric and color shifts, resulting in blurred outputs with poor
  performance on synthetic benchmarks"; synthetic benchmarks are used
  precisely "to ensure no misalignment between the input and ground truth".
- Misregistration in DEM differencing (researchgate) — remote-sensing analog.
**No paper found yet that reports a MISREGISTERED no-learning REFERENCE
inflating reported skill in an SR or MF benchmark.** That is the specific claim
the mentor note makes; needs one more adversarial framing (iteration 3/4).

## Dead ends
- `https://arxiv.org/pdf/2606.20771` → undecoded PDF binary; recovered via
  `/abs/`. (Batch-2 lesson repeats: prefer `/abs/` and `/html/`.)

## Interpretation
Tail-aware training is published and, in the one fetched PDE instance, a
*failed* lever — a strong prior against a naive tail-reweighting arm in B3.
Per-sample target normalization did not surface under an operator-learning
framing; either it is assumed-trivial preprocessing or genuinely under-treated,
and must be re-attacked with time-series/instance-norm vocabulary. The
registration-contamination literature exists in the SR *training-data* sense,
not in the *benchmark-reference* sense our note claims.
