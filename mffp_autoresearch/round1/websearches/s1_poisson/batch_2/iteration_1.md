# iteration_1 — s1_poisson batch 2

## Search rationale

B1's mechanism finding is a **normalization** claim, not a composition claim:
one shared scaler over levels whose RMS spans 75.7x forces the network to learn
an amplitude law along its fidelity axis (74.7 % of squared error is per-sample
gain). Batch 1's search never touched normalization. So turn 1 goes straight at
task item (a): is per-fidelity / per-level target standardization documented as
a design choice anywhere, and is the shared-scaler failure mode named? I search
both the MF vocabulary ("per-fidelity") and the neural-operator vocabulary
("per-resolution", "level-wise"), plus a third term aimed at the pathology
itself (magnitude/scale mismatch between LF and HF).

## Search terms used

1. `per-fidelity normalization multi-fidelity neural network training standardize each fidelity level separately output scaling`
2. `multi-resolution neural operator training per-resolution normalization level-wise standardization appendix`
3. `low-fidelity high-fidelity data different magnitude scales normalization pitfall neural network surrogate amplitude mismatch fusion`

## Findings

### Term 1 — per-fidelity normalization in MF NNs

Search returned the usual MF-NN corpus (MFRNP, progressive MF, MF-HNP,
composite NN, MF-PINN) but **no source whose contribution or ablation is the
normalization scheme**. The engine's own synthesis conceded the point: "the
specific approach to per-fidelity standardization (standardizing each fidelity
level separately) isn't explicitly detailed in these results."

Fetched, adversarially, the two hits most likely to state a preprocessing
recipe:

- **MF-PINN with Bayesian UQ and adaptive residual learning**
  [https://arxiv.org/html/2602.01176v1] — the *only* scaling statement is
  §III-C1: "When the PDE variables have very different scales (e.g., pressure
  versus velocity), simple non-dimensionalization or rescaling of outputs can
  further improve conditioning and helps avoid pathological gradient
  magnitudes." That is scaling **across variables within one fidelity**, not
  across fidelity levels. No per-fidelity scaler procedure.
- **Berger et al., "General Multi-Fidelity Framework for Training ANNs with
  Computational Models"** (Front. Mater. 2019)
  [https://www.frontiersin.org/articles/10.3389/fmats.2019.00061/full] — fetch
  verdict: "the paper does not discuss normalization or scaling of training data
  across different fidelity levels." Its only related sentence is "we will skip
  units, assuming thereby implicitly appropriately normalized quantities" — i.e.
  the question is assumed away.

### Term 2 — per-resolution normalization in neural operators

- **QuadNorm: Resolution-Robust Normalization for Neural Operators**
  [https://arxiv.org/html/2605.07375] (fetched). Identifies that standard
  normalization layers "compute statistics through uniform averaging of discrete
  grid values, making normalization itself discretization-dependent": "If the
  same continuous field is resampled at a different resolution (H',W')≠(H,W),
  the discrete mean changes, even though the underlying function is the same."
  Fix = quadrature (trapezoidal) weights, so cross-resolution mismatch "decays
  quadratically with grid spacing" O(h²) instead of O(h). **Scope limit stated
  explicitly by the fetch**: the paper is about *internal* normalization layers
  across discretizations, and "does NOT discuss normalizing data/targets from
  different resolutions or fidelity levels with shared versus per-level
  scalers." Framing gift: it establishes normalization as "a critical yet
  under-examined" component in multi-resolution operator learning.
- Also surfaced (not fetched this turn): Multi-Grid Tensorized FNO
  [https://arxiv.org/pdf/2310.00120]; A Physics-informed Multi-resolution
  Neural Operator [https://arxiv.org/html/2510.23810]; MLMC-NO
  [https://arxiv.org/pdf/2505.12940] (already covered in batch 1).

### Term 3 — LF/HF magnitude mismatch as a documented pathology

Diffuse. The one on-topic thread the engine surfaced is the **classical MF-GP
scale factor** (the multiplicative ρ in Kennedy–O'Hagan-style autoregressive
models): "Selecting an appropriate scale factor is critical for prediction
accuracy... most studies use maximum likelihood estimation techniques that may
overlook the effect of the discrepancy function's waviness term" — surfaced via
[https://www.sciencedirect.com/science/article/abs/pii/S1270963824000610]
(abstract-only, paywalled; not fetched). Second-most-relevant: MF flow matching
calibrates "the source distribution ... to empirical residual statistics"
[https://arxiv.org/pdf/2605.16118] (batch-1 source). No result named a
shared-scaler-over-pooled-levels failure mode.

## Interpretation

Across three terms and four fetched/attempted sources, **the cross-fidelity
target normalization scheme is systematically unstated in the MF-NN
literature** — two fetched papers assume it away in as many words. The nearest
published neighbor to B1's mechanism is QuadNorm, which is about *internal*
layer statistics being discretization-dependent, not about *target* scalers
pooled over a fidelity ladder. The classical analog is the MF-GP scale factor ρ,
which learns the amplitude ratio explicitly rather than normalizing it away.
