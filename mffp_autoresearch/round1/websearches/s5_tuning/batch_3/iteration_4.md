# Iteration 4 — Q4: systematic target-scaling / dynamic-range-placement studies in operator learning

## Search rationale

B2's mechanism finding is that the zscore win was **dynamic-range placement**, not
pattern recovery. For B3 to state that as a *measurement* with correct attribution, I need
to know whether operator learning has any systematic target-scaling ablation
(maxabs vs standardization vs per-sample) at all, or whether the field is simply silent —
s5-B2's row (ii) already found the nearest MF paper does not state its normalization
(https://arxiv.org/html/2511.01830). This turn tests that silence from two new angles
(operator-learning ablations; MF-specific normalization practice).

## Search terms used

1. `ablation study output normalization strategy neural operator target scaling min-max standardization comparison PDE`
2. `dynamic range of target field affects neural network regression accuracy scaling physics surrogate systematic comparison`
3. `multi-fidelity neural operator normalization ablation low-fidelity statistics scale high-fidelity target few samples`

## Findings

### Term 1 — operator-learning normalization ablations

Results: QuadNorm (https://arxiv.org/html/2605.07375); Fourier/Galerkin Transformer
supplement (https://proceedings.neurips.cc/paper/2021/file/d0921d442ee91b896ad95059d13df618-Supplemental.pdf);
Convolutional Neural Operators (https://arxiv.org/pdf/2302.01178); Multi-Grid Tensorized
FNO (https://arxiv.org/pdf/2310.00120); PDE-Transformer (https://arxiv.org/html/2505.24717);
Latent Neural Operator (NeurIPS 2024 proceedings PDF).

**FETCHED — QuadNorm, "Resolution-Robust Normalization for Neural Operators"
(https://arxiv.org/html/2605.07375)** (s2-B3 fetched this too; I re-fetched with a
target-scaling prompt so the s5 verdict rests on my own retrieval):
- the compared objects are **normalization layers**: *"Normalization layers ... including
  LayerNorm, InstanceNorm, GroupNorm, and RMSNorm, along with no normalization"*;
- the fetch's explicit finding on stage: *"The paper does not explicitly distinguish
  whether normalization applies to inputs, targets, or feature activations"*, and
  *"The paper lacks direct ablations comparing global vs. instance/per-sample or min-max
  vs. standardization approaches."*
- the citable methodological line: *"Most benchmarks evaluate at the training resolution,
  which masks the effect of normalization-induced cross-resolution degradation"*, and
  *"an empirical error-comparison ablation ... shows that quadrature-consistent
  normalization reduces this degradation to only 0.22 times the no-normalization reference
  on Darcy."*

So the closest thing operator learning has to a normalization ablation is about **layers
and resolution robustness**, not about **where the target's dynamic range is placed**.

### Term 2 — dynamic range of the target vs regression accuracy

Results: P3D (https://arxiv.org/html/2509.10186v1 — s2-B3 already logged its adaptive
instance norm as *conditioning*); https://arxiv.org/html/2601.13308; neural-field
aerodynamic surrogates (https://arxiv.org/html/2505.14704v1); Constitutive Manifold NNs
(https://arxiv.org/pdf/2506.13648); two emergentmind topic pages (secondary sources).
The search summariser's own conclusion, recorded verbatim because it is the finding:
*"the results don't appear to contain a specific paper focused exclusively on how dynamic
range of target fields affects neural network regression accuracy in physics surrogate
modeling."* **No usable primary result; nothing fetched.**

### Term 3 — MF-specific normalization practice

Results: MF-FNO for geological carbon storage (https://arxiv.org/pdf/2308.09113); MF NN
surrogate sampling (https://arxiv.org/pdf/1909.01859); generative MF downscaling
(https://arxiv.org/html/2509.22474v1); Multi-Fidelity Flow Matching
(https://arxiv.org/pdf/2605.16118); MF closure via conditional normalizing flows
(https://arxiv.org/html/2606.09857); review of MF models (https://arxiv.org/html/1609.07196v5).
Search snippet for 2308.09113: *"inputs like porosity and logarithmic permeability are
applied with min-max normalization"* — i.e. **input** normalization only, stated in
passing. **FETCH FAILED**: https://ar5iv.labs.arxiv.org/html/2308.09113 returned
"Fatal error during HTML conversion", no content. So I cannot upgrade that snippet to a
citation; it stays a search-listed lead.

## Interpretation

Two independent framings plus B2's row (ii) now agree: **operator learning has no
published systematic study of target-scaling choice / dynamic-range placement.** The
literature normalizes *layers* (QuadNorm), normalizes *instances for multi-physics scale
unification* (MPP/MORPH, iteration 1), and states input normalization in passing (MF-FNO
snippet) — but the target-scaler-as-a-knob question is unoccupied. This makes B3's
contribution a **measurement in a silent area**, which is precisely s5's charter and
carries no novelty claim.
