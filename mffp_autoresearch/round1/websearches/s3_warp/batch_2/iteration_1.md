# iteration_1 — displacement parameterization + the single-interpolation question

## Search rationale

Batch 1 already adjudicated the general warp/MF landscape, so this iteration
attacks the two most load-bearing *design* questions of the narrow D1 card,
both of which are also novelty risks:

- (a) how to PREDICT a spatially varying, sub-cell (median |phi| 0.64-0.74 HF
  cells) displacement at small N — B1 F13 says only the 16x16-control-grid rung
  pays on cahn_hilliard, which smells like a low-mode/spectral parameterization,
  and batch 1's report already flagged "a low-Fourier-mode displacement head is
  the cheapest such prior and matches the FNO stack" as UNVERIFIED;
- (b) B1 F17's hard constraint: the double resample is what killed the oracle
  warp. Is "compose the warp with the upsample so only one interpolation
  happens" published, and under what name?

## Search terms used

1. `Fourier shift theorem spatially varying displacement field warping neural network band-limited resampling`
2. `low-dimensional spectral parameterization of deformation field neural registration few training samples`
3. `SRWarp warping spatially-varying super-resolution single interpolation joint upsampling warp avoid double resampling`

(A fourth call was attempted first and rejected by the tool for a malformed
parameter — no query was executed, so it is not counted.)

## Findings

### Term 1 — spectral / band-limited displacement parameterization

**Fourier-Net** (AAAI 2023) is a direct hit and a direct preemption of the
"low-Fourier-mode displacement head" idea. It replaces a U-Net decoder with a
**parameter-free, model-driven decoder = zero-padding layer + inverse DFT**, so
the network only ever predicts *a low-resolution representation of the
displacement field in a band-limited Fourier domain*
[cite: https://arxiv.org/abs/2211.16342 — fetched (abs page; the PDF at
https://arxiv.org/pdf/2211.16342 returned undecodable binary, flagged)].
Claimed cost vs TransMorph: **2.2 % of the parameters, 6.66 % of the mult-adds,
11.5x faster inference, +0.5 % Dice** — i.e. the band-limited displacement
representation is reported as *accuracy-neutral*, not a compromise. Follow-on
**Fourier-Net+** uses "deterministic Fourier-domain band-limiting for efficient
down- and up-sampling" and the same parameter-free decoder
[cite: https://arxiv.org/pdf/2307.02997 (search result);
https://research.manchester.ac.uk/en/publications/fourier-net-band-limited-spatial-representation-for-efficient-med/].
Neither fetched page states how the warp itself is applied (the abs page is
silent) — so whether Fourier-Net displaces spectrally or via a spatial
transformer is UNRESOLVED here and is the open half of question (b).

Also surfaced: **SRWarp** (CVPR 2021) reinterprets warping-with-enlargement as
a **spatially-varying super-resolution** problem, with an "adaptive warping
layer" and multiscale blending, motivated explicitly by "deform images with
sharp edges" [cite:
https://openaccess.thecvf.com/content/CVPR2021/papers/Son_SRWarp_Generalized_Image_Super-Resolution_under_Arbitrary_Transformation_CVPR_2021_paper.pdf ,
https://arxiv.org/abs/2104.10325v1 (search results)].

### Term 2 — low-dimensional deformation spaces at small N

The registration field's answer to few samples is a **learned low-dimensional
deformation subspace**, not a hand-picked mode cut: statistical deformation
models via PCA, or autoencoder/probabilistic latent codes, explicitly motivated
by "high-dimensional SDMs are difficult to train given orders of magnitude fewer
training samples" [cite: https://pubmed.ncbi.nlm.nih.gov/25720017/ ,
https://pmc.ncbi.nlm.nih.gov/articles/PMC8802338/ ,
https://arxiv.org/pdf/1804.07172 (search results)]. There is a dedicated study
of **the DOF of gridded control points in learning-based registration** [cite:
https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12919706/ (search result)], which
is exactly B1 F13's C4-vs-C16 question in the registration literature's own
language, and a review of learned vs model-based **regularization** in
registration [cite: https://arxiv.org/pdf/2412.15740 (search result)] — the
successor to batch 1's arXiv:2412.17982 finding that global smoothness penalties
are locally insufficient.

### Term 3 — the single-interpolation composition

Two published forms of "do the warp and the upsample in one shot":
- **SRWarp**'s framing (warp-with-enlargement := spatially varying SR) — the
  composition is the whole premise of the paper [cite: same URLs as term 1].
- **LTEW** (ECCV 2022, "Learning Local Implicit Fourier Representation for Image
  Warping"): "local textures estimated from a deep SR backbone are multiplied by
  locally-varying **Jacobian matrices of the coordinate transformation** to
  predict Fourier responses of a warped image" [cite:
  https://arxiv.org/abs/2207.01831 — fetched (abs page; the PDF and the ECVA PDF
  exceeded the fetch size limit, flagged)]. Fetched evidence says this is
  *feature-space* Jacobian modulation, NOT a single continuous query at warped
  coordinates — so it is a cousin, not the same construction.
- A search-snippet-level lead named **JUBW (Joint Upsampling and Backward
  Warping)**, described as performing "upsampling and backward warping in a
  single step without performing any interpolation at all, but additionally
  outputs sub-pixel distances and leaves finding a meaningful interpolation to
  the network itself". **The snippet carries no source URL** — the search engine
  attributed it loosely to the SRWarp context. This is NOT citation-grade yet
  and must be resolved in iteration 2 before any claim rests on it.

## Interpretation

The "low-mode spectral displacement head" that batch 1 recommended is
**published prior art in registration** (Fourier-Net's band-limited Fourier
displacement with a zero-pad + iFFT decoder) — so it is a legitimate, cite-able
*building block* but not a novelty carrier. The single-interpolation composition
that B1 F17 forces on us has at least two published parents (SRWarp's
warp-as-spatially-varying-SR, LTEW's Jacobian-modulated Fourier response), which
is good news for implementability and bad news for claiming it as new; the
strongest-sounding variant (JUBW, interpolation-free joint upsample+warp) is
still an unsourced snippet and must be pinned or dropped.
