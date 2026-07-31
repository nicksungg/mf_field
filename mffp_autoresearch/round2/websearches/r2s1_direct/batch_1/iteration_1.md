# Iteration 1 — the three §12.1 decoder classes

## Search rationale

program.md §12.1 names three design priors for condition→HF: FiLM-conditioned
FNO **decoders**, DeepONet branch–trunk (branch on the condition, trunk on
coordinates), and spectral/implicit decoders (SIREN/modulated-INR class).
§13.3 warns this is a heavily published area, so turn 1 maps the field for
each of the three classes before anything is proposed.

## Search terms used

1. `FiLM-conditioned neural operator decoder mapping PDE parameter vector to solution field surrogate`
2. `DeepONet branch network on PDE parameter vector trunk on coordinates parametric surrogate few training samples`
3. `implicit neural representation modulated INR surrogate parametric PDE CORAL coordinate-based few-shot`

## Findings

### Term 1 — FiLM-conditioned parameter→field decoders

Top results (WebSearch):
- "Parameter conditioned interpretable U-Net surrogate model for data-driven
  predictions of convection-diffusion-reaction processes" —
  https://arxiv.org/html/2601.22654v1
- "Generalizing PDE Emulation with Equation-Aware Neural Operators" —
  https://arxiv.org/html/2511.09729v1
- "Structure-Aware Epistemic Uncertainty Quantification for Neural Operator PDE
  Surrogates" — https://arxiv.org/pdf/2603.11052
- "Deep Neural ODE Operator Networks for PDEs" — https://arxiv.org/html/2510.15651
- "Flow matching Operators for Residual-Augmented Probabilistic Learning of
  PDEs" — https://arxiv.org/pdf/2512.12749

Search-engine synthesis (not fetched, flagged as such): FiLM is described as a
standard conditioning mechanism for generalizing a network across a PDE family
by modulating intermediate features from the parameter vector, used inside
encoder–decoder / U-Net architectures with a transposed-conv decoder projecting
latents back to the field; equation-aware emulation conditions on a vector
encoding of PDE terms and coefficients. Conclusion for our purposes: "condition
vector → FiLM → decoder → field" is textbook, not novel.

### Term 2 — branch–trunk from a parameter vector

Top results (WebSearch):
- "Reduced-Basis Deep Operator Learning for Parametric PDEs with Independently
  Varying Boundary and Source Data" — https://arxiv.org/pdf/2511.18260
- "Physics-Informed Neural Networks and Neural Operators for Parametric PDEs"
  (review) — https://arxiv.org/pdf/2511.04576
- "On the influence of over-parameterization in manifold based surrogates and
  deep neural operators" — https://arxiv.org/pdf/2203.05071
- "Constitutive Relations-Aware Deep Operator Networks" — https://arxiv.org/pdf/2405.13759
- "Bayesian DeepONet for noisy parametric PDEs" — https://arxiv.org/pdf/2111.02484
- Topic page "RB-DeepONet" — https://www.emergentmind.com/topics/rb-deeponet

**Fetched** https://arxiv.org/abs/2511.18260 (RB-DeepONet, submitted
2025-11-23): trunk is FIXED to a greedy-constructed reduced-basis space built
offline; the branch predicts only RB coefficients from the parameter/boundary/
source encodings; trained label-free from a projected variational residual;
compared against intrusive RB-Galerkin, POD-DeepONet and FEONet, competitive
accuracy at dramatically fewer trainable parameters. Abstract does not state a
training-sample count. Directly relevant: the "branch-on-parameters → linear
combination of a fixed basis" design is published, and is exactly the
low-capacity variance-reducing shape one would reach for at N_hf=5.
Also relevant: the search synthesis states appending parameters to the branch
input, concatenating them into the trunk, or dual-encoding both, are all
already-catalogued options.

### Term 3 — modulated INR / neural-field surrogates

Top results (WebSearch):
- "Vectorized Conditional Neural Fields: A Framework for Solving Time-dependent
  Parametric PDEs" — https://arxiv.org/pdf/2406.03919
- "Neural fields for rapid aircraft aerodynamics simulations" (Sci Rep 2024) —
  https://www.nature.com/articles/s41598-024-76983-w
- "Generalizable INRs via Instance Pattern Composers" — https://arxiv.org/pdf/2211.13223
- "Disentangled Latent Dynamics Manifold Fusion for Solving Parameterized PDEs"
  — https://arxiv.org/pdf/2603.12676
- "Architecture Shapes Transfer Specificity in Implicit Neural Representations"
  — https://arxiv.org/pdf/2606.06827
- "FA-INR: Adaptive INRs for Interpretable Exploration of Simulation Ensembles"
  — https://arxiv.org/html/2506.06858v3

Synthesis: CORAL is described as a two-stage refinement of DINo (shared-parameter
INR encoder/decoder trained first, then a dynamics block on the learned latent
codes); generalizable INRs work by modulating a coordinate MLP per instance.
Conditioning a neural field on simulation parameters is an established pattern
(FA-INR explicitly for simulation *ensembles* indexed by parameters).

## Interpretation

All three §12.1 design priors are published architecture patterns with named
prior art; none can be proposed as a novel mechanism on its own. The
still-unclaimed axes are (a) the few-HF regime with a *fixed/deterministic*
output basis (RB-DeepONet's shape, but nobody in these hits does it under a
multi-fidelity training signal), and (b) the reporting methodology — no hit so
far reports NN-in-condition / train-mean / zero floors. Turn 2 goes after the
regime (tiny N, parametric surrogate baselines/floors) rather than more
architectures.
