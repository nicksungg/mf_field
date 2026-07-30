# iteration_4 — can a net resolve a 0.64-cell displacement at all? plus the
# spectral warp primitive and a phase-field-native metric

## Search rationale

B1 F11 puts the residual displacement on cahn_hilliard at **median |phi| =
0.64-0.74 HF cells** — sub-cell. Before designing any head, the feasibility
question is whether learned displacement estimators are even accurate at sub-cell
magnitudes, and what architecture the literature says is required there. Second,
iteration 2 pinned the *idea* of a single-interpolation warp but not a primitive
that works on periodic spectral data (our sharp datasets are point samples on a
periodic node grid, B1 F1) — is band-limited resampling at deformed coordinates
a standard object? Third, a phase-field-native interface-displacement metric for
the evaluation question.

## Search terms used

1. `subvoxel precise registration CNN limitation sub-pixel displacement accuracy learned registration SuperWarp`
2. `non-uniform FFT resampling at deformed coordinates band-limited image warping spectral interpolation periodic`
3. `machine learning correct interface position error coarse grid phase-field simulation shift interface location Cahn-Hilliard coarse solve`

## Findings

### Term 1 — SuperWarp: the sub-cell regime has a published diagnosis, and it is favourable to us

**SuperWarp** (WBIR 2022) is a direct, fetched treatment of subvoxel-precise
learned registration [cite: https://pmc.ncbi.nlm.nih.gov/articles/PMC9645132/ —
fetched; https://arxiv.org/abs/2205.07399 ;
https://link.springer.com/chapter/10.1007/978-3-031-11203-4_12]. Four findings
that bear directly on D1's head design:

1. **Diagnosis of plain U-Net displacement heads**: a standard U-Net is *"jointly
   tasked with feature extraction and matching in addition to deformation
   estimation, which is not handled well by a fully convolutional network"*, and
   the entanglement is worst in **untextured regions** (for us: the bulk phases
   away from interfaces, which is most of a cahn_hilliard field).
2. **The Horn-Schunck duality**: given the true displacement you can harmonize
   the images in normalized-intensity space; given harmonized images, recovering
   displacement is easy. The two tasks are separable, and the architecture should
   separate them.
3. **The threshold that matters to us**: *"the optical flow equation holds only
   when displacement magnitudes remain less than one voxel"*; SuperWarp therefore
   warps features at each U-Net level so that only sub-voxel residuals are ever
   estimated. **Our residual displacement is already 0.64-0.74 cells** — i.e.
   inside the single-scale validity regime, so a coarse-to-fine pyramid is NOT
   required for the narrow cahn_hilliard card, which removes a large chunk of
   design complexity. (It is also a warning: at ±12-voxel displacements, the
   scale they test, a single-scale head is invalid — that is not our regime.)
4. **Supervision**: direct supervision on target warps *"outperforms
   self-supervised registration requiring segmentations"* (Dice 0.954 vs 0.906;
   endpoint error down ~80 % on foreground pixels). This is the citable parent
   for a design we can actually run: B1's own warp fitter can produce ORACLE
   displacements on the TRAIN split (HF is available at train time), so the
   displacement head can be trained with a *direct displacement loss* rather than
   only through the end-to-end nRMSE — and B1 leg D's nearest-neighbour retrieval
   is the zero-parameter version of the same idea.

Supporting: the registration-regularization review [cite:
https://arxiv.org/pdf/2412.15740 (search result, iteration 1)] and the DOF study
of gridded control points [cite:
https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12919706/ (search result,
iteration 1)] are the two places to price the C4-vs-C16 DOF question if needed.

### Term 2 — the spectral warp primitive exists, generically, and is not a warping paper

There is no "warp a field spectrally" paper in these results; what exists is the
generic machinery: **NUFFT** (interpolate onto a dense uniform grid then FFT,
Kaiser-Bessel kernels, ~O(N log N)) [cite: https://arxiv.org/pdf/1605.05231 ,
https://arxiv.org/pdf/1604.06236 (search results)], and — closer to our exact
need — **FFT-based interpolation of a PERIODIC BAND-LIMITED signal from samples
at nonuniform positions in a regular grid** [cite:
https://ieeexplore.ieee.org/document/7076647/ ,
https://dl.acm.org/doi/10.1109/TSP.2015.2419178 ,
https://www.researchgate.net/publication/264862796_Zero-padding_FFT_interpolation_from_nonuniform_samples_lying_in_a_regular_grid
(search results, none fetched — IEEE/ACM paywalls, flagged)]. Also a 2026
geoscience application of an *elastic* NUFFT for irregularly sampled fields
[cite: https://arxiv.org/pdf/2606.21278 (search result)].

Read: the single-interpolation composition B1 F17 demands is buildable from
standard signal-processing parts (zero-pad FFT upsample composed with sampling at
warped node coordinates), and — importantly for the verdict — the *primitive* is
textbook, so no novelty attaches to it either way. Cheapest legal implementation
for a smooth, low-mode `phi`: a single `grid_sample`/spectral evaluation of the
RAW LF at the warped HF node coordinates (one interpolation), or exact Fourier
shift for the constant-displacement arm (B1 F16 already used exactly that).

### Term 3 — a phase-field-native interface-displacement metric exists but I could not source it

The search surfaced the right object: in phase-field representations the
interface is the `phi = 0.5` isoline, and *"when the interface displaces with
respect to its original position by a small distance delta(S)"* the perturbed
field is *"the original field plus a gradient term multiplied by the interface
displacement"*, with a **mean squared interface displacement** defined as an
integral measure — i.e. exactly the first-order identity `dphi ≈ |grad phi| *
delta` that converts an L2 field error into an interface-displacement error.
**Source not obtained**: the snippet came from
https://asset.library.wisc.edu/1711.dl/LWH3N26W7XUHQ9E/R/file-c2af0.pdf and the
fetch returned unparseable binary (4.2 MB). **Not citation-grade — flagged.**
Nothing else in the results corrects interface *position* on a coarse phase-field
solve with ML; the coarse-interface literature answers with **adaptive mesh
refinement** instead [cite: https://arxiv.org/pdf/2510.21749 ,
https://arxiv.org/abs/2607.25142 ,
https://www.sciencedirect.com/science/article/pii/S0045782526001295 (search
results)], and the phase-field-ML literature is about learning the dynamics
[cite: https://arxiv.org/pdf/2203.16692 , https://arxiv.org/pdf/2407.20126
(search results)].

## Interpretation

The feasibility news is good and specific: at 0.64-0.74 cells we are inside the
single-scale optical-flow validity regime SuperWarp identifies, so no pyramid is
needed; but SuperWarp also says a plain U-Net head is the wrong instrument in
untextured regions and that **direct displacement supervision** (available to us
from an oracle fit on the train split) beats similarity-only training. The
spectral single-interpolation warp is textbook machinery, so it is an obligation,
not a claim. The phase-field interface-displacement metric is the right
evaluation object but I could not source it; if the brainstormer wants it, it
must be re-derived in-repo (`dphi ≈ |grad phi| delta` is elementary) and NOT
cited to the unfetched PDF.
