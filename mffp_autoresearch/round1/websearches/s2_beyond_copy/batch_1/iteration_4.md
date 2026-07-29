# Iteration 4 — s2_beyond_copy / batch 1  (§3.3 prior-art work, part 1)

## ENOUGH on field context

**ENOUGH** — iterations 1-3 supply a citable metric set (per-band `rFFT`/`H(k)`,
multi-scale coherence, PFI permutation) and three separable mechanisms; further
context search has diminishing returns, so iterations 4-5 are spent on §3.3
refutation searches. Reason recorded per the websearcher protocol §3.2 step 1.

## Search rationale

Field context is closed (see ENOUGH above); this turn's three terms are chosen as
**refutation** searches, one per candidate direction below, per websearcher §3.3:
each is phrased to find the work that would show the direction has already been done.

## The candidate directions this stream-batch will propose

Derived from program.md §12.2 (batch 1 is a **diagnostic** by design) plus
`summary_so_far.md`'s open questions:

- **D1 (this batch's card)** — *copy-LF excess-error decomposition*: a no-training
  measurement that decomposes, per panel dataset, the excess error of a trained
  panel family over the copy-LF reference into (i) radial frequency bands
  (`rFFT`/`H(k)` bias vs copy-LF's own per-band bias), (ii) spatial strata by
  distance to the interface / high-|∇LF| set, (iii) an **LF-permutation** test of
  whether the model uses the LF field at all.
- **D2 (likely batch 2)** — *identity-to-LF fusion*: an architecture whose output
  equals `up(LF)` at initialization (zero-init residual branch), with a learned,
  gated correction, so skill ≤ 1 is structurally guaranteed at init.
- **D3 (alternative batch 2)** — *hard low-band constraint*: copy LF's Fourier
  coefficients below a per-dataset cutoff `k_c`; the network predicts only `k > k_c`
  plus a small low-band correction (the in-repo report's P4 `mf_band_split`).

## Search terms used

1. `band-split hard constrain low frequency coefficients to input predict only high wavenumbers neural operator spectral super-resolution copy low band`
2. `gated fusion multi-fidelity guaranteed at least as good as low-fidelity model learned gate falls back to low fidelity neural operator`
3. `diagnostic analysis paper why neural PDE surrogate fails localize error by frequency band and distance to interface no new model`

## Findings

### Term 1 — hard low-band copy (refutation target: D3)

Results: high-frequency scaling for spectral-bias mitigation (ResearchGate 389946465);
STSR speech SR (https://arxiv.org/html/2509.03913); equilibrium-conserving neural
operators for super-resolution (https://arxiv.org/pdf/2504.13422); multiscale FNO for
inverse wave scattering in highly oscillatory media (https://arxiv.org/pdf/2606.08448);
neural operators review (https://arxiv.org/pdf/2309.15325); FreqNO-DPS again
(https://arxiv.org/pdf/2606.03936); hyperspectral high-low frequency SR network
(MDPI 2072-4292/15/9/2472).

- Established facts recovered: FNO spectral convolution layers *"truncate high
  wavenumbers by construction"*; and band-limited / representation-equivalent
  operators (Spectral Neural Operators) *"cannot generate new (higher) frequencies
  since their representation space is fixed, introducing an irreducible approximation
  error based on the size of the predefined representation space."* That is the
  spectral wall stated as a theorem-shaped constraint, independent of the in-repo
  report.
- The **audio/vision analogue of D3 is unambiguously published** — spectral speech
  super-resolution and hyperspectral high/low-frequency-split SR networks both split
  the spectrum and reconstruct only the missing band. **No usable results** for a
  *multi-fidelity PDE operator* that hard-constrains the low band to a real coarse
  *solve*. No fetch spent: the returned SR papers are cross-domain confirmations, not
  MF prior art, and the mechanism's non-novelty is already established by the in-repo
  report's own citation of AP-BWE.
- Partial verdict for D3: **preempted-but-MF-composition-open** — see iteration 5 for
  the consolidated statement.

### Term 2 — gated / identity-guaranteed MF fusion (refutation target: D2)

Results: AGMF-Net ensemble adaptive gated multi-fidelity NN for Bayesian optimization
(ScienceDirect S002980182502997X); practical MF ML fusing deterministic and Bayesian
models (https://arxiv.org/html/2407.15110); MF data fusion via active subspaces
(https://arxiv.org/pdf/2010.08349); adaptive gated fusion for multimodal sentiment
(https://arxiv.org/html/2510.01677v1); emergentmind topic pages on gated / dual-gated
fusion.

- **Gated multi-fidelity fusion exists and is named**: AGMF-Net *"integrates deep
  gated expert fusion with ensemble-based uncertainty quantification, enabling
  accurate and robust multi-fidelity learning under limited high-fidelity data"* —
  but it is a **scalar-output surrogate for Bayesian optimization (hydrofoil design)**,
  not a field/operator model, and its gate is over experts, not over an
  identity-to-LF path.
- **Explicit negative, stated by the search engine's own synthesis:** the results
  *"don't contain specific information about the guarantee that a gated fusion model
  will be 'at least as good as the low-fidelity model' with a learned gate that
  'falls back to low-fidelity' for neural operators."* Combined with iteration 1's
  Fixup finding (identity-at-init is generic published practice), the honest reading
  is: components published, the *guarantee framing for MF field prediction* not
  retrieved.

### Term 3 — an existing diagnostic paper (refutation target: D1) — the real threat

Results: **"Predictivity and Utility of Neural Surrogates of Multiscale PDEs"**
(https://arxiv.org/html/2604.20061v1, https://arxiv.org/pdf/2604.20061);
"Spectral Shaping for Neural PDE Surrogates" (https://openreview.net/forum?id=mmDkgLtYNI);
"Predicting change, not states" (ScienceDirect S0045782525002622); data efficiency of
NO surrogates for plasma codes (https://arxiv.org/pdf/2402.08561); Courant perceiver
surrogate (https://arxiv.org/pdf/2605.25115); NN approximation of coarse-scale
surrogates in numerical homogenization (https://arxiv.org/pdf/2209.02624).

- **Predictivity and Utility of Neural Surrogates of Multiscale PDEs [cite:
  https://arxiv.org/html/2604.20061v1] (FETCHED).** Confirmed to be a **diagnostic /
  analysis paper with no new model** — the closest published relative of D1. Its
  machinery:
  (i) a **frequency-response lens** over three spectra — solution spectrum, operator
  spectrum (how the PDE maps forcing to solution in Fourier space), and ML spectrum
  (NTK eigenvalues per mode);
  (ii) **band-energy relative error** across wavenumber ranges — on Kuramoto-Sivashinsky
  it finds *"dissipation-range bands exhibit huge relative mismatch due to the surrogate
  maintaining a nonzero high-k floor"* while low/mid bands stay controlled;
  (iii) NTK eigenvalue decay measured at λ̃_k ~ k^-2.01, so *"k=15 mode requires 158x
  more training iterations than the k=1 mode"* at equal target amplitude;
  (iv) the MSE-conditional-expectation result stated plainly: *"A deterministic neural
  surrogate trained with MSE converges to the conditional expectation … the average
  over all fine states consistent with the coarse input"*;
  (v) "sweet spots": success when the solution manifold has low intrinsic dimension or
  physics damps high frequencies (diffusion-dominated, elliptic).
- **The three gaps that keep D1 alive**, per the same fetch:
  (a) *"the paper does not systematically compare neural surrogates against
  coarse/low-fidelity solutions as a direct baseline. This is a notable gap;
  comparisons focus on training error, rollout divergence, and idealized reduced-order
  models rather than demonstrating whether surrogates outperform the coarse
  approximation they learn from."* — precisely the copy-LF skill question;
  (b) multi-fidelity is only acknowledged in the conclusions (*"more general classes
  multi-fidelity approaches will also be relevant"* for residual corrections), not
  explored;
  (c) **no interface-localized error analysis** and no sharp-2D phase-field setting —
  its worked example is KS, which is the *smooth control* in the in-repo report's own
  axis (MF_Sharp_HighFreq_Report Part 0).
- **"Spectral Shaping for Neural PDE Surrogates" → WebFetch failed** (OpenReview
  browser-verification wall; the page returned only a verification screen). Recorded
  as a dead end; **no claim is made from it**. Retried by a different route in
  iteration 5.

## Interpretation

D1's mechanism (per-band + spectral-bias diagnosis of PDE surrogates) is published
[2604.20061]; what is *not* published there is the copy-the-coarse-solve reference,
the multi-fidelity setting, and interface-localized stratification — the paper itself
names the first as a gap. D2 and D3 are assembled from published components. Final
consolidated verdicts, plus one more refutation pass on the spectral-shaping paper
and on interface-stratified evaluation, in iteration 5.
