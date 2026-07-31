# Iteration 3 — targeted prior-art refutation (§3.3 pass 1 of 2)

## Search rationale

The three directions r2s1-B1 is likely to propose, from program.md §12.1 plus
turns 1–2:

- **D1** FiLM-conditioned FNO/spectral **decoder**: condition vector → spectral
  latent → HF field, no input function.
- **D2** Fixed/learned-basis coefficient decoder: condition → coefficients of a
  basis built from the HF training fields (branch–trunk with a non-learned
  trunk), pitched as the variance-reducing shape for N_hf = 5.
- **D3** Report every panel number against an *estimated aleatoric / conditional-
  mean floor*, i.e. certify per dataset whether condition→HF is identifiable at
  all before crediting a model.

Each term below is a deliberate attempt to REFUTE the novelty of one direction.

## Search terms used

1. `POD-DeepONet POD-NN regression of proper orthogonal decomposition coefficients from PDE parameters data-efficient`  (refute D2)
2. `FiLM conditioning Fourier neural operator generate field from scalar parameters only no input function decoder`  (refute D1)
3. `irreducible error floor unidentifiable parameters surrogate benchmark conditional mean optimal predictor relative L2 aleatoric limit operator learning`  (refute D3)

## Findings

### Term 1 (refute D2) — parameters → modal coefficients

Top results:
- "PODNO: Proper Orthogonal Decomposition Neural Operators" —
  https://arxiv.org/html/2504.18513v1/
- "POD-DL-ROM: Enhancing deep learning-based ROMs for nonlinear parametrized
  PDEs by POD" — https://www.sciencedirect.com/science/article/pii/S0045782521005120
- "A hybrid Decoder-DeepONet operator regression framework for unaligned
  observation data" — https://arxiv.org/pdf/2308.09274
- "Variationally correct operator learning: Reduced basis neural operator with a
  posteriori error estimation" — https://arxiv.org/html/2512.21319
- "Temporal Extrapolation Generalization of POD and RBF Surrogates …" —
  https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12654062/

**Fetched** https://arxiv.org/html/2504.18513v1/ (PODNO, arXiv:2504.18513v1,
April 2025). It states explicitly that **PCA-Net and POD-NN** "use
dimensionality reduction to project inputs/outputs onto low-dimensional
subspaces, then map coefficients with simple DNNs", and that **POD-DeepONet**
combines POD with DeepONet's encoder–decoder. The search synthesis adds that
POD-NN "was later re-discovered and generalized under different names, such as
PCA-net and POD-DeepONet", and that POD-ANN builds "regression models linking
input parameters to the coefficients of the POD basis".
⇒ D2's mechanism (parameters → POD/RB coefficients → field) is squarely
published, and RB-DeepONet (iteration_1, https://arxiv.org/abs/2511.18260)
is the 2025 fixed-trunk instance.

### Term 2 (refute D1) — scalar-only conditioning of an FNO

Top results:
- "Fourier Neural Operators Explained: A Practical Perspective" (Duruisseaux,
  Kossaifi, Anandkumar) — https://arxiv.org/pdf/2512.01421
- "Accelerating Phase Field Simulations Through a Hybrid Adaptive FNO with
  U-Net Backbone" — https://arxiv.org/pdf/2406.17119
- "Multi-fidelity prediction of fluid flow and temperature field based on
  transfer learning using FNO" — https://arxiv.org/pdf/2304.06972
- NVIDIA PhysicsNeMo FNO docs (ModAFNO) —
  https://archive.docs.nvidia.com/physicsnemo/26.03/physicsnemo/api/models/fnos.html
- neuraloperator docs — https://neuraloperator.github.io/dev/theory_guide/fno.html

**Fetch attempted** on https://arxiv.org/pdf/2512.01421 — the PDF text did not
extract (only metadata: authors Duruisseaux, Kossaifi, Anandkumar; v2 dated
2026-01-26). So I do NOT claim a fetched quote from it. What is citable from
the search return itself: the result set names **ModAFNO** ("extends AFNO with
modulation capabilities for conditioning on auxiliary inputs (e.g., time,
parameters)"), documented at the NVIDIA PhysicsNeMo model page above, and
sinusoidal embedding of scalar conditions as the standard strategy.
⇒ Scalar/parameter modulation of a spectral operator is shipped production
code, not a research contribution.

### Term 3 (refute D3) — aleatoric floor / conditional-mean barrier

Top results:
- "Diagnosing the Conditional-Mean Barrier in Scientific Machine-Learning
  Surrogates" — https://arxiv.org/html/2605.28076
- "Parameter uncertainties for imperfect surrogate models in the low-noise
  regime" — https://arxiv.org/pdf/2402.01810 /
  https://iopscience.iop.org/article/10.1088/2632-2153/ad9fce
- "Variationally correct operator learning: RB neural operator with a
  posteriori error estimation" — https://arxiv.org/html/2512.21319

**Fetched** https://arxiv.org/html/2605.28076 (arXiv:2605.28076v3, 2026-07-06).
The "conditional-mean barrier": under squared loss a deterministic surrogate
learns E[Y|X] and is then *scientifically inadequate* because irreducible
conditional variability remains — precisely the one-to-many situation created by
"coarse-graining or partial observation". Its 3-part diagnostic: (1) residual–
feature orthogonality probes, (2) effect-size thresholding, (3) **aleatoric floor
estimation** — when residuals stabilize, the residual mean-square σ̂_r² estimates
E[Var(Y|X)], to be *reported alongside* deterministic model error. Crucially for
us, the fetch reports the paper **does not explicitly address surrogates with
unidentified random inputs such as random initial conditions**; with drivers
outside X the framework still applies but the floor is understood to rise.
⇒ D3's general machinery is published (July 2026); its instantiation as a
per-dataset *identifiability certificate for a multi-fidelity field panel* — where
the missing driver is recoverable from the withheld LF field — is not covered by
the fetched source.

## Interpretation

D1 and D2 are refuted as mechanisms: both are catalogued prior art, so any
r2s1-B1 proposal must be pitched as a *measurement under this regime*, not an
invention. D3 survives partially: the conditional-mean-barrier diagnostic exists
and even prescribes reporting the aleatoric floor, but nobody in the fetched
material ties that floor to a hidden driver that a *lower-fidelity solve*
observes. Turn 4 closes the remaining refutation question — has anyone already
published exactly "parameters alone cannot predict this field, the coarse solve
carries the missing information" for a multi-fidelity benchmark?
