# Iteration 1 — what the reference codebases/benchmarks actually normalize

## Search rationale

Open question Q1 (`summary_so_far.md`). Before proposing a scaler change on
`mf_fno_transfer_film` (`smoke_eval.py:136-137`, single global `max|Y|` per
stage), establish the field's normative practice first-hand: PDEBench (the
canonical benchmark), The Well (the newest large benchmark), and
`neuraloperator` (the reference FNO implementation whose defaults the zoo
inherited). If the norm is per-channel/dataset-level Gaussian rather than a
single global max-abs, the champion's scheme is an outlier and "move to the
field default" is a legitimate, cheap knob.

## Search terms used

1. `PDEBench normalization of data training FNO UnitGaussianNormalizer per-channel mean std`
2. `"the Well" dataset benchmark PDE surrogate normalization strategy per-field statistics 2024`
3. `neuraloperator library UnitGaussianNormalizer transform output denormalize documentation`

## Findings

### Term 1 — PDEBench / normalization in neural operators
- Search surfaced PDEBench primary sources
  (https://arxiv.org/pdf/2210.07182 ,
  https://papers.neurips.cc/paper_files/paper/2022/file/0a9747136d411fb83f0cf81820d44afb-Paper-Datasets_and_Benchmarks.pdf)
  but the returned snippets describe data format (HDF5, N/T/X/Y/Z/V arrays)
  and metrics, **not** a normalization prescription. No usable first-hand
  normalization statement extracted for PDEBench in this iteration.
- The highest-value hit was a dedicated normalization paper for this exact
  model class: **QuadNorm: Resolution-Robust Normalization for Neural
  Operators**, https://arxiv.org/pdf/2605.07375 (abs page fetched:
  https://arxiv.org/abs/2605.07375). Verbatim from the fetched abstract:
  *"Normalization layers in neural operators usually compute statistics by
  uniformly averaging discrete grid values, making the normalization itself
  discretization-dependent and thereby a source of transfer error across
  different resolutions or meshes."* It proposes quadrature-weighted statistics
  (QuadNorm / BlendQuadNorm), `O(h^2)`-consistent across discretizations, and
  claims "nearly resolution-invariant transfer". The PDF fetch of the same
  paper additionally reported that the work contrasts **global vs per-sample
  (instance)** statistics and **max-abs vs Gaussian standardization** — I flag
  that second fetch as a summarizer paraphrase, weaker evidence than the
  abstract quote above, and do not use it as a citation for any specific claim.
- Search-snippet-level note (not fetched, NOT citable as a paper claim): a
  snippet asserted that for neural operators normalization "must be either
  global or function-wise rather than dependent on spatial variables" to
  preserve discretization invariance. Recorded as a lead only.

### Term 2 — The Well
- Primary sources located: https://openreview.net/forum?id=00Sx577BT3 ,
  https://danfortunato.com/papers/TheWell.pdf , https://github.com/PolymathicAI/the_well .
  **All three fetches failed to yield the normalization section**: the PDF
  returned undecodable binary, OpenReview returned a browser-verification
  page, the GitHub README contains no normalization text. The search snippet
  claims per-field normalization from **training-split statistics only** and a
  **VRMSE** metric that normalizes error by the field's spatial variance — i.e.
  a metric whose 1.0 point is exactly "predict the per-sample spatial mean".
  That is directly relevant to open question Q5, but it is snippet-level and
  therefore **NOT citable**; iteration 4 must re-fetch it from a readable
  endpoint before any use.

### Term 3 — neuraloperator (the reference implementation) — USABLE
- Fetched https://raw.githubusercontent.com/neuraloperator/neuraloperator/main/neuralop/data/transforms/normalizers.py .
  `UnitGaussianNormalizer` "normalizes data to be zero mean and unit std";
  the reduction dims are explicit — "Has to include the batch-size (typically
  0). For instance, to normalize data of shape `(batch_size, channels, height,
  width)` along batch-size, height and width, pass `dim=[0, 2, 3]`" — giving
  statistics of shape `(1, C, 1, 1)`. `fit()` computes
  `torch.mean(data_batch, dim=self.dim, keepdim=True)` /
  `torch.std(...)`; `partial_fit()` accumulates running statistics over
  batches. So the reference implementation is **dataset-level, per-channel,
  Gaussian (mean/std)** — batch dim is always reduced, hence never per-sample —
  and `dim=None` degenerates to a global scalar mean/std.
- Library paper https://arxiv.org/html/2412.10354v1 fetched: it only says the
  library has "a flexible DataProcessor module to pipeline all normalization
  ... and transform raw outputs into the form expected for computing losses";
  no scheme details. Confirms denormalization of outputs is a first-class
  pipeline step, nothing more.

## Interpretation

The field's reference normalizer is dataset-level **Gaussian (mean/std),
optionally per-channel**, with the batch dimension always reduced — so the
champion's `max|Y|` (a single order statistic set by the most extreme training
field, no demeaning) is a non-standard choice, and "z-score / robust scaler"
is a move *toward* the default rather than an invention. Per-sample statistics
are absent from the reference implementation by construction (batch dim is
always in the reduction), which is the first hint that per-sample output
scaling is not a mere knob. QuadNorm establishes that normalization-statistic
choice is itself a publishable, actively-studied axis for neural operators —
so novelty claims on any scaler variant will be hard, but the axis is
legitimate and live.
