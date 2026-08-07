# Iteration 2 — r3s2_field_reach, batch 1

## Search rationale

Iteration 1 showed the *general* framing (condition a decoder on a finite-dimensional parameterization of the input function) is standard, but did not surface the specific internal topology.
So iteration 2 renames the target three ways: (1) the latent/physics-informed phrasing under which "parameters → initial latent state → time evolution → field decode" would actually be published; (2) the ablation question that any r3s2 claim would have to win — does a structured intermediate beat direct conditioning; (3) the domain phrasing, since our panel *is* Allen–Cahn / Cahn–Hilliard / phase-field-crystal — if someone already built a parameter-only surrogate for these systems, the direction is preempted in-domain.

## Search terms used

1. `physics-informed decoder reconstructs initial condition from latent parameters before time-stepping neural surrogate "initial condition" parameterized Fourier modes benchmark`
2. `structured intermediate representation versus direct conditioning ablation neural PDE surrogate does the intermediate help`
3. `parameter-to-field surrogate few high-fidelity samples spectral decoder Allen-Cahn Cahn-Hilliard phase field crystal condition vector only`

## Findings

### Term 1 — the latent phrasing (HIT)
- **[FETCHED]** "Parameterized Temporal Extrapolation of PDEs via Disentangled Latent Dynamics Manifold Fusion" (DLDMF), https://arxiv.org/html/2603.12676 (also https://arxiv.org/pdf/2603.12676). Verbatim from the fetched abstract: *"DLDMF maps PDE parameters through a deterministic feed-forward encoder that directly initializes and conditions a continuous latent state governed by a parameter-conditioned Neural Ordinary Differential Equation (Neural ODE)"*, fusing *"[spatial] coordinate, parameter embedding, and evolving latent state within a shared nonlinear decoder to reconstruct parameterized spatiotemporal solutions"*, explicitly *"without test-time optimization for instance-specific initialization"* (contrasted against latent pipelines that *"often require test-time optimization for instance-specific initialization"*).
  → This is the round-3 "internal option C" pipeline at the latent level: **parameter vector → initialized state → evolution → field decode, entirely feed-forward at test**. Published.
- Physics-Informed Latent Neural Operator (PI-Latent-NO), https://arxiv.org/html/2501.08428 (snippet-level) — two coupled DeepONets, a Latent-DeepONet plus a Reconstruction-DeepONet; the same reconstruct-from-latent shape.

### Term 2 — "does the structured intermediate help?" ablation
The search engine's own summary states the results *"don't contain a specific study directly comparing structured intermediate representation versus direct conditioning for neural PDE surrogates."*
Nearest neighbours returned (snippet-level, none fetched): INC — An Indirect Neural Corrector for Auto-Regressive Hybrid PDE Solvers, https://arxiv.org/html/2511.12764v1; Courant: a State-Adaptive Perceiver-Based Neural Surrogate…, https://arxiv.org/html/2605.25115v1 (lists parameter-conditioning among ablated components); Predictivity and Utility of Neural Surrogates of Multiscale PDEs, https://arxiv.org/html/2604.20061v1.
**No usable direct result for the attribution question.**

### Term 3 — in-domain (phase-field) parameter-only surrogates (HIT)
- **[FETCHED]** "Neural surrogates for crystal growth dynamics with variable supersaturation: explicit vs. implicit conditioning", https://arxiv.org/html/2604.21753. Verbatim: the two architectures are one that *"infers it implicitly by processing an input mini-sequence of a few evolution frames"* and one that *"takes the supersaturation parameter as an explicit input along with a single initial frame and predicts the entire sequence"*; *"the explicit parameter conditioning guarantees the best results, reproducing with high-fidelity the ground-truth profiles."*
  → Explicit-parameter conditioning is published and is reported to *win* against implicit inference on a phase-field-class system. **Crucially, the explicit arm still receives a real initial frame** — the paper does not synthesize the IC from parameters, which is exactly what our regime forces.
- Equivariant U-Shaped Neural Operators for the Cahn–Hilliard Phase-Field Model, https://arxiv.org/abs/2509.01293 / https://arxiv.org/html/2509.01293v3 (snippet-level) — learns evolution *"from short histories of past dynamics"*, i.e. field-in, not condition-only.
- Learning two-phase microstructure evolution using neural operators and autoencoder architectures, https://www.nature.com/articles/s41524-022-00876-7 (snippet-level) — field-in.
- Extrapolating Phase-Field Simulations in Space and Time with Purely Convolutional Architectures, https://arxiv.org/html/2509.20770 (snippet-level) — field-in.

## Interpretation

The mechanism r3s2 would most naturally propose — parameters feed-forward into an initialized state, evolve, decode a field — is published as DLDMF, and explicit-parameter conditioning is already reported to beat implicit inference on a phase-field-class system.
What remains conspicuously unfound after six terms is the *attribution* question (does the structured intermediate buy anything over direct condition→field conditioning) and any condition-only phase-field surrogate that never sees an initial frame at test — every in-domain surrogate found so far consumes a field or a short history.
Iteration 3 must (a) refresh the stacked pseudo-LF prior art with fetches made in THIS loop, since round-2's citations may not be reused, and (b) look for methodology for certifying a negative.
