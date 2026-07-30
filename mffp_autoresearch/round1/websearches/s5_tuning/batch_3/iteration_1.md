# Iteration 1 — RevIN outside time series; target de-normalization by INPUT statistics

## Search rationale

Scope item 1 (Q1 in `summary_so_far.md`). s5-B2's row (i) already established that RevIN
is (a) scoped to time series in its critique paper and (b) present inside one PDE
surrogate (MPP). What B3 needs that B2 did not settle is narrower and load-bearing for
arm A3 `revin_lf`: the scale there is **`s_i = max|LF_i|`, a statistic of the INPUT**,
used to de-normalize a **raw** (non-residual) target. So I searched (a) RevIN's migration
out of forecasting into PDE surrogates, and (b) the general "normalize by input stats,
denormalize output by the same stats" construction in image-to-image regression, which is
the same mechanism in a different field.

## Search terms used

1. `reversible instance normalization RevIN applied to PDE surrogate operator learning not time series`
2. `normalize target by input statistics denormalize output image-to-image regression instance normalization`
3. `APEX amplitude anchors phase priors target-scarce higher-frequency wave prediction per-sample amplitude from coarse fidelity`

## Findings

### Term 1 — RevIN in PDE surrogates

Top results: MORPH (https://arxiv.org/html/2509.21670v3); MPP overview
(https://www.alphaxiv.org/overview/2310.02994v2); the RevIN critique
(https://arxiv.org/html/2603.11869, already cited by s5-B2); RevIN original
(https://openreview.net/forum?id=cGDAkQo1C0p, https://seharanul17.github.io/RevIN/).

**FETCHED — MORPH, "PDE Foundation Models with Arbitrary Data Modality"
(https://arxiv.org/html/2509.21670v3)**: uses **Reversible Instance Normalization** to
handle scale heterogeneity across PDE datasets. Verbatim: *"We normalize the data and
cache the corresponding means and standard deviations, then use these statistics to
exactly denormalize model outputs."* And: *"Unlike [MPP], which normalizes on-the-fly, we
pre-normalize the entire dataset and train on normalized batches, reducing the
normalization overhead incurred during training and fine-tuning, and inference."*
So: RevIN-style per-sample normalize/denormalize **is** established in PDE surrogate
modelling (two independent instances now: MPP and MORPH), and the statistics are the
**sample's own** (mean/sd of the instance), not a lower-fidelity companion field.

### Term 2 — target normalized by INPUT statistics, output denormalized

Top results: Normalization Equivariance for Arbitrary Backbones
(https://arxiv.org/pdf/2605.08193 / https://arxiv.org/abs/2605.08193); R2D2 series for
non-Cartesian MRI (https://arxiv.org/pdf/2503.09559); style-transfer test-time adaptation
(https://arxiv.org/pdf/2311.18270); a normalization-methods tutorial page
(https://ahmedbadary.github.io/work_files/research/dl/concepts/norm_methods); three USPTO
medical-imaging patents.

**FETCHED (twice — PDF and `/abs/`) — "Normalization Equivariance for Arbitrary Backbones,
with Application to Image Denoising" (https://arxiv.org/abs/2605.08193)**. Verbatim
abstract: *"Normalization Equivariance (NE) is a structural prior that improves robustness
to distribution shift in image-to-image tasks. A function f is normalization equivariant
iff f(a y + b1) = a f(y) + b1 for all a>0 and b in R. Existing NE methods constrain every
internal layer to NE-compatible operations. These constraints add runtime cost and exclude
standard transformer components such as softmax attention and LayerNorm. **We introduce
Wrapped Normalization Equivariance (WNE), a parameter-free wrapper that normalizes the
input, applies any backbone, and denormalizes the output. We prove every NE function
admits this factorization, so the wrapper exactly parameterizes the class of NE
functions.** On blind denoising, wrapping CNN and transformer architectures improves
robustness under noise-level mismatch with no measurable GPU overhead, while architectural
NE baselines are up to 1.6x slower."*
The PDF fetch additionally reported the construction as normalizing the target by
statistics computed from the **input** and denormalizing the output by those same
input-based statistics; the abstract itself states only "normalizes the input ...
denormalizes the output", so I cite the **abstract wording** as the load-bearing quote and
treat the target-side reading as the paper's own framing of the same wrapper. Domain:
**blind image denoising**, i.e. an image-to-image regression across a
degraded-input/clean-target boundary — not PDEs, not multi-fidelity.

### Term 3 — APEX (the nearest MF neighbour named by s5-B2)

Search-listed only: https://arxiv.org/pdf/2605.26732 (PDF endpoint; B2 recorded the
size/format hazard). Search snippet: *"combines transferable coarse amplitude and
physics-guided phase priors for higher-frequency wave-field prediction"*, *"amplitude
anchoring from coarse-resolution data"*, target-scarce regime. Not fetched this turn —
deferred to iteration 2 so the amplitude-anchor mechanism can be quoted verbatim, since
it is the single closest published thing to `revin_lf`.

## Interpretation

The generic "per-sample normalize / denormalize by an inference-available statistic"
wrapper is now **doubly preempted**: inside PDE surrogates by MPP+MORPH (self-statistics)
and, as a *theorem* about the whole function class, by WNE (input statistics,
parameter-free, image-to-image). What is still unretrieved is the specific composition
`statistic taken from the LOW-FIDELITY companion field, applied to a HIGH-fidelity raw
target, across a fidelity boundary` — APEX is the only candidate occupant and must be
fetched before any verdict.
