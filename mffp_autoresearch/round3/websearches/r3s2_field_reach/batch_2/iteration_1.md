# Iteration 1 — is regularised/shrunk spectral transfer-function estimation from tiny samples established methodology?

## Search rationale

B1's single most actionable mechanism finding is a **methodology defect, not a science result**: the vendored `dc_cleaned` stage-2 estimates a full 64x64 complex per-wavenumber LSI Wiener operator `T(k)` from `n_fit = 3` HF/LF residual pairs with `S6_LSI_RIDGE = 0`, and above the LF Nyquist (band 4) the estimate is an unregularised 0/0 that reached |T| = 66.2 on ifc_poisson seed 2, dumping 2311.94 units of relative band-4 error energy (`summary_so_far.md` item 3). Before proposing "ridge / band-limit `T`" as a B2 lever, I must establish whether this is textbook — because if it is, the brainstormer may use it as an **instrument repair** but must not claim it as a mechanism (program.md §13.3; the project is 0-for-4 on novelty).

## Search terms used

1. `regularized Wiener filter transfer function estimated from few training pairs multi-fidelity spectral correction coarse to fine`
2. `shrinkage estimation frequency response function small sample cross-spectral density regularization ill-conditioned`
3. `deconvolution high wavenumber amplification above Nyquist band-limiting Tikhonov regularization coarse grid solution correction`

## Findings

### Term 1 — regularised Wiener / transfer-function estimation from few pairs, multi-fidelity framing

**No usable results for the multi-fidelity composition.** The engine returned generic Wiener-filter literature (speech enhancement, optical sparse aperture restoration, binaural hearing aids, a system-identification overview) and stated explicitly that "the specific combination ... particularly regarding multi-fidelity spectral correction with a coarse-to-fine approach and estimation from few training pairs — appears to be a specialized topic". The one substantive snippet-level statement, from the MDPI system-identification overview <https://www.mdpi.com/2076-3417/11/17/7774> (**snippet-only — a direct fetch returned HTTP 403**), is that regularised Wiener filters matter "when operating in noisy environments and/or when only a low quantity of data is available for the estimation of the statistics", the regularisation parameter trading data fidelity against large filter coefficients. That is precisely our failure mode, described as standard practice.

Other snippet-only results: <https://www.researchgate.net/publication/8355680_Wiener_filter_estimation_of_transfer_functions>; <https://arxiv.org/html/2507.13863v1> (tiny-NN-controlled parameterised multichannel Wiener filter).

### Term 2 — shrinkage of spectral matrices under low sample support (FETCHED)

**Directly on point, and it is a 50-year-old statistical staple.**

- [Schneider-Luftman & Walden 2015] "Partial Coherence Estimation via Spectral Matrix Shrinkage under Quadratic Loss" — <https://arxiv.org/pdf/1511.07030> — **FETCHED this loop** (pypdf). Verbatim: *"If the number of complex degrees of freedom only slightly exceeds the dimension of the multivariate stationary time series, spectral matrices are poorly conditioned and shrinkage techniques suggest themselves."* They derive quadratic-loss and Hilbert–Schmidt shrinkage estimators for **spectral and precision matrices**, i.e. exactly the frequency-domain objects a per-wavenumber Wiener operator is built from, and evaluate oracle vs non-oracle (fully estimated) variants.
- [Tong et al. 2018] "Linear Shrinkage Estimation of Covariance Matrices Using Low-Complexity Cross-Validation" — <https://arxiv.org/abs/1810.08360> — **FETCHED this loop**. Verbatim: *"Shrinkage can effectively improve the condition number and accuracy of covariance matrix estimation, especially for low-sample-support applications with the number of training samples smaller than the dimensionality"*; they give analytic **leave-one-out cross-validation** rules for choosing the shrinkage coefficient that reach "near-oracle performance". With `n_fit = 3` this is the literature's own answer to "how do I pick the ridge".

Snippet-only neighbours: <https://www.sciencedirect.com/science/article/pii/S0047259X08001942> (shrinkage in the frequency domain of multivariate time series — "numerically more stable due to a smaller condition number"); <https://link.springer.com/rwe/10.1007/978-1-4614-4547-0_8> (Frequency Response Function Estimation — windowing reduces variance at the cost of resolution); <https://www.sciencedirect.com/science/article/pii/S1474667017477974> (wavelet-shrinkage FRF estimation); <https://arxiv.org/html/2508.17412v4> (over-shrinkage / negative regularisation).

### Term 3 — high-wavenumber amplification, Nyquist band-limiting, Tikhonov

Generic Tikhonov-deconvolution literature only (spectral deconvolution, antenna de-embedding, statistical treatments): <https://ieeexplore.ieee.org/document/6313911/>, <https://ieeexplore.ieee.org/document/9785496/>, <https://ideas.repec.org/a/taf/lstaxx/v43y2014i20p4384-4400.html>. All snippet-level; none reaches the coarse-grid-solution-correction composition, and the engine said so. One reusable framing from the snippet text: deconvolving past the sampling limit "violates the Nyquist–Shannon sampling theorem since a deconvolved point source cannot be accurately represented by any sampling or pixel size" — the standard justification for hard band-limiting rather than ridging.

**In-repo prior websearch (cite, do not re-derive)**: `docs/reports/MF_Sharp_HighFreq_Report.md` line 260 already records the fitted-transfer-kernel-plus-learned-prior recipe (galaxy deblurring, Li & Alexander, arXiv:2211.01567 — "fit the actual LF↔HF transfer kernel from training pairs (one FFT pass), then unroll a few proximal-gradient steps with the FNO as the learned prox"), and lines 224–230 / 293–297 record the coherence-gated band-split (hard-constrain the band below the wavenumber where LF/HF cross-spectral coherence drops below ~0.7, predict only above it).

## Interpretation

Regularising / shrinking a spectral transfer-function estimate under low sample support is **unambiguously textbook** — with published, data-driven rules for choosing the shrinkage coefficient at exactly our sample sizes — so the B2 `T(k)` repair is an instrument fix that must be cited, never claimed. What is *not* retrievable is anyone applying it inside a multi-fidelity coarse→fine correction stage at `n_fit ≈ 3`, or the coherence-gated Nyquist band-limit as a stability guarantee for such a stage; that composition is where the remaining novelty question lives, and iteration 4/5 will attack it directly as a refutation search.

## Tooling note

`WebFetch` is intercepted by the context-mode plugin in this environment (batch-1 lesson); all fetches used `python3 urllib.request` + `pypdf` via `scratchpad/fetch.py`. `export.arxiv.org` API returned HTTP 429/timeout and was abandoned; `www.mdpi.com` returned HTTP 403. Sources reachable only as search-engine snippets are labelled **snippet-only** above and carry no verdict.
