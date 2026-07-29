# Iteration 1 — the data-estimated LSI defect filter (topic (a))

## Search rationale

B1's headline (F6/F7) is that a **zero-parameter closed-form shift-invariant
transfer function** `T(k) = sum_n R_hat LF_hat* / sum_n |LF_hat|^2`, fitted by
least squares on paired coarse/fine training solves, **beats the trained 72k
ConvNeXt on 3 of 4 datasets** and is numerically the *inverse of the bilinear
interpolation blur* (`|T(k)|` -> 1 monotonically by band). Batch 2 wants to
promote it to a **scored control arm**. Before that, the novelty question:
is "estimate the coarse->fine defect operator in closed form from a few paired
solves" published? Turn 1 attacks it from three angles: (i) the classical
numerics phrasing (defect/deferred correction + local Fourier analysis),
(ii) the signal-processing phrasing (Wiener deconvolution of interpolation
blur, coarse->fine transfer function), (iii) the adversarial phrasing (a linear
filter beating a neural net on PDE super-resolution — i.e. the weak-baseline
literature that would license *reporting* the filter even if it is not novel).

## Search terms used

1. `estimate defect correction operator from paired coarse and fine solves least-squares Fourier filter surrogate`
2. `learned transfer function coarse to fine grid correction Wiener deconvolution PDE interpolation blur super-resolution`
3. `linear filter baseline outperforms neural network PDE super-resolution downscaling deconvolution kernel fitted from training pairs`

(One earlier call was malformed and errored before reaching the search engine;
it is not counted as a WebSearch call.)

## Findings

### Term 1 — classical defect correction / local Fourier analysis
Returns the **venerable** side of the mechanism but no data-estimation:
- "COARSE GRID APPROXIMATION GOVERNED BY LOCAL FOURIER ANALYSIS" — coarse-grid
  operator accuracy is measured by **comparing Fourier symbols** of coarse and
  fine operators (DCA / Petrov–Galerkin GCA / collocation CCA)
  [search-return: https://www.researchgate.net/publication/255595433_COARSE_GRID_APPROXIMATION_GOVERNED_BY_LOCAL_FOURIER_ANALYSIS]
- "Error estimates for deferred correction methods in time"
  [search-return: https://www.sciencedirect.com/science/article/abs/pii/S0168927406000870]
- "Multiscale coupling of FFT-based simulations with the LDC approach" —
  **Local Defect Correction** coupling coarse and local grid problems
  [search-return: https://www.sciencedirect.com/science/article/abs/pii/S0045782522001967]

Interpretation of term 1: **defect correction and per-wavenumber comparison of
coarse vs fine operators are textbook multigrid/LFA material**, i.e. the
*mechanism* is unquestionably old. What no returned source does is **estimate
the correction transfer function empirically from a sample of paired solves and
score it on an ML benchmark**. No usable direct hit on that composition.

### Term 2 — Wiener/deconvolution framing
- **"Multiscale Corrections by Continuous Super-Resolution" (NH-CSR)**,
  https://arxiv.org/html/2411.07576v2 — **FETCHED.** Closest topical neighbor
  found: it learns "a mapping from a potentially incorrect coarse-scale
  solution to an improved upscaled solution", input = coarse FEM solution +
  coefficient map, target = fine-scale solution with "oscillatory structure"
  the coarse solve misses. **But**: the corrector is a *trained* network
  (coefficient-guided continuous SR, Gabor-wavelet coordinate encoding,
  multiscale implicit image function), trained **100,000 iterations** on
  128x128 synthetic FEM pairs; **"provides no zero-parameter linear filter or
  transfer function comparison"**; baselines are other *learned* SR models
  (LIIF, LIT, MetaSR); **no multi-fidelity framing**.
- **DWDN: Deep Wiener Deconvolution Network**,
  https://arxiv.org/html/2103.09962v2 — search-return only: a "learnable Wiener
  Filtering layer" / "feature-based Wiener deconvolution module" — i.e. Wiener
  deconvolution as a *differentiable layer inside* a deblurring CNN, in the
  image domain, not a standalone fitted defect operator between PDE grids.
  [search-return snippet: "The deconvolution module can be implemented as a
  learnable Wiener Filtering layer."]

### Term 3 — the adversarial / weak-baseline angle
- **"Numerical PDE solvers outperform neural PDE solvers"**,
  https://arxiv.org/html/2507.21269v1 — **FETCHED.** DeepFDM (differentiable
  finite-difference) reaches **"one to two orders of magnitude"** lower NMSE
  than FNO/U-Net/ResNet with **5–50x fewer parameters**; the paper's framing is
  that neural PDE solvers **"have not, until now, been carefully compared to
  established numerical PDE methods"** and that "previous work only compared
  neural methods against each other". **It does NOT use coarse-solve +
  correction or interpolated-coarse as a baseline** ("High resolution PDE
  solutions were projected onto a coarser grid" — i.e. it *downsamples*, which
  this repo's methodology law forbids as an LF construction).
- **"Exploring the Low-Pass Filtering Behavior in Image Super-Resolution"**,
  https://arxiv.org/html/2405.07919v2 — search-return: an SR network decomposes
  into "linear and non-linear components, where the linear system functions as a
  low-pass filter while the non-linear system injects high-frequency
  information". Independent support for B1's F7 reading of `|T(k)|`, in a
  different field.
- Search-return counter-evidence to keep honest: linear-regression patch filters
  "perform decently on edge reconstruction but have limitations due to the 2D
  filter only representing linear relationships"
  [https://proceedings.mlsys.org/paper_files/paper/2022/file/3134f61af2136e249b0d8f190cbdc508-Paper.pdf];
  interpolation-based linear filtering is "very fast but usually yield[s] blurry
  solutions corrupted with aliasing artifacts"
  [https://pmc.ncbi.nlm.nih.gov/articles/PMC6238924/].

## Interpretation

The *mechanism* (defect correction; comparing coarse/fine operator symbols per
wavenumber; Wiener deconvolution of a blur) is old and multiply published, but
across three framings nothing returned **estimates the coarse->fine defect
transfer function in closed form from paired solves and scores it against
learned operators**; the nearest learned neighbor (NH-CSR) explicitly ships
**no linear-filter baseline**. Meanwhile the weak-baseline literature
(DeepFDM) supplies a strong *licence to report* the filter: its whole thesis is
that neural PDE work under-compares against classical methods. Next turn:
padding (topic (b)).
