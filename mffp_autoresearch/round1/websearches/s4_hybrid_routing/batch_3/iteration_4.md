# iteration_4 — fitted taper vs hard cutoff in band-limited correction

## Search rationale

B2's spectral caveat is the constraint that will shape the B3 corrector's
target: a **pure re-registration** removes 97.6-97.7 % of copy-LF error below
0.5 Nyquist and is **5.17x HARMFUL above it** (cos 0.205), while the **fitted**
LSI transfer function is clean in every band (cos 0.996). Before the card
claims that as a design insight, I have to establish whether the
fitted-gain-vs-brick-wall distinction is (as I suspect) textbook. Three angles:
(a) spectral tapering / Gibbs from a sharp cutoff, (b) Wiener's smoothly
decreasing gain vs truncated inverse filtering, (c) whether the underlying
node/cell-centred grid-transfer misregistration is itself known numerics.

## Search terms used

1. `fitted spectral taper versus sharp cutoff band-limited correction Gibbs ringing filter design neural network upsampling`
2. `Wiener filter optimal frequency-dependent gain versus ideal low-pass cutoff deconvolution noise amplification high wavenumber`
3. `grid interpolation phase shift misregistration node-centered cell-centered coarse fine multigrid transfer operator error high wavenumber`

## Findings

### Term 1 — tapering vs brick wall — **fetched**
https://pmc.ncbi.nlm.nih.gov/articles/PMC4915073/ (*Gibbs Ringing in Diffusion
MRI*), **fetched**, verbatim:
- *"A sharp cut-off or truncation in the k-space is equivalent to a convolution
  in spatial domain with a sinc function."*
- *"The oscillating lobes of the sinc function result in the ringing pattern
  around sharp edges."*
- *"those low-pass filters ... attenuate the higher-frequency components near
  the cutoff frequency ... results in the widening of the point spread
  function. Hence, those filters blur the signal and ... reduce spatial
  resolution."*
- *"Choosing a filter is a trade-off between the degree of suppression of the
  Gibbs artifacts and image blur."*
- *"Only windows without an abrupt discontinuity will fully suppress Gibbs
  oscillations."*
Other returns: https://arxiv.org/pdf/2501.04116 (dCoNNear — artifact-free NN
audio architecture), https://pmc.ncbi.nlm.nih.gov/articles/PMC7722184/ (NN for
Gibbs+noise removal in dMRI), https://arxiv.org/html/2606.15450 (data-driven
tapering in KDE), https://grokipedia.com/page/Ringing_artifacts .

### Term 2 — Wiener gain vs truncated inverse — **fetched**
https://vincmazet.github.io/bip/restoration/deconvolution.html (*Basics of
Image Processing*, deconvolution chapter), **fetched**, verbatim:
- truncation: *"One solution consists in considering only the low frequencies
  of Y/H. This is equivalent to truncating the result given by the inverse
  filter by cancelling the high frequencies before calculating the inverse
  Fourier transform."*
- *"the PSF H is generally a low-pass filter, so the values of H(m,n) tend
  towards 0 for high frequencies (m,n). Because H is in the denominator, this
  tends to drastically amplify the high frequencies of the noise."*
- Wiener: *"where H vanishes (typically in high frequencies), the problem of
  noise increase is no longer observed as with the inverse filter, since the
  inverse filter tends towards 0"*.
Supporting return (not fetched): http://www.math.tau.ac.il/~turkel/notes/wiener7-2.pdf
(*"The Wiener filter is the MSE-optimal stationary linear"* filter).

### Term 3 — node- vs cell-centred grid transfer
Returns: https://www.researchgate.net/publication/225576806_Cell-centred_multigrid_revisited ,
https://link.springer.com/article/10.1007/s10440-009-9533-2 (optimal transfer
operators from finite-difference approximations),
https://www.sciencedirect.com/topics/engineering/multigrid ,
https://arxiv.org/pdf/2604.19501 (real-shifted coarse-grid correction for
Helmholtz). Engine summary (not a citation): in cell-centred multigrid *"the
nodes on coarser grids do not form a subset of fine grid nodes, unlike
vertex-centred cases"*, and *"high-order inter-grid operators yield
well-aligned phases of successive grids"*. **No usable fetched result**, but
the returns are enough to record that the node/cell-centred mismatch and its
phase consequence are classical numerics — s3_warp-B1's finding is a *benchmark
defect report*, not a novel mechanism, and B3 must treat it that way.

## Interpretation

The fitted-taper-vs-hard-cutoff distinction is **textbook, twice over**: a
brick-wall cutoff is a sinc convolution that rings (PMC4915073) and a truncated
inverse filter is the naive alternative to a smoothly-varying optimal gain
(Wiener). B2's 5.17x above-0.5-Nyquist harm is therefore a *measurement of the
known artifact on this benchmark*, and the "use the fitted transfer function,
not a shift" directive is a textbook design choice — the card may cite it, must
not claim it.
