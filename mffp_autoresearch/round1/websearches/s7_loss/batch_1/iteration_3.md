# iteration_3 — s7_loss / batch 1

## Search rationale

Two sub-questions remained thin: (d) the small-N_hf **multi-fidelity** regime
(where does the objective, as opposed to the architecture, carry the
multi-fidelity load?), and the structural / gradient-domain loss family
(SSIM-like), which is the only family in the task list not yet touched. I also
probed the literal seed direction of ADR 0012 — interface-aware weighting on
phase-field problems — to find out whether the weight maps published there are
physics-agnostic (ADR 0009 gate) or equation-derived.

## Search terms used

1. `multi-fidelity operator learning loss function weighting few high-fidelity samples training objective`
2. `structural similarity SSIM loss gradient loss training surrogate model turbulence field prediction sharper`
3. `interface-aware weighted loss phase field simulation deep learning gradient magnitude weight map sharp interface`

## Findings

### Term 1 — multi-fidelity objectives at small N_hf

- **Lu, Pestourie, Johnson, Romano (2022), "Multifidelity deep neural operators
  for efficient learning of partial differential equations with application to
  fast inverse design of nanoscale heat transport"** —
  https://arxiv.org/abs/2204.06684 (fetched). "Two standard DeepONets coupled by
  residual learning and input augmentation"; "significantly reduces the required
  amount of high-fidelity data and achieves one order of magnitude smaller error
  when using the same amount of high-fidelity data." Classified in the fetch as
  an **architectural** contribution, not an objective change.
- The rest of the retrieved set (feature-adjacent MF-PIML, MF-FNO transfer
  learning arXiv:2304.06972, MF Bayesian neural operator arXiv:2602.13257,
  transfer-learning MF-PIDNN) is the same shape: MF composition is carried by
  ARCHITECTURE or by a two-term data loss (`L_lf + L_hf`) with **scalar
  fidelity weights**. Fidelity weighting is described generically ("higher-
  weighted data with higher fidelity has a larger impact on training") — i.e.
  a per-fidelity scalar, not a structured objective.
- **Key negative result for the verdict**: I found no multi-fidelity work whose
  *contribution* is the shape of the HF-stage loss (band-weighted,
  amplitude-decomposed, LF-anchored). MF-specific loss engineering appears to
  stop at scalar per-fidelity weights.

### Term 2 — structural / SSIM-family losses

- Fetched survey page https://www.emergentmind.com/topics/structural-similarity-loss.
  Variants named there with attributions: **MS-SSIM** (Snell et al., 2015),
  **additive SSIM forms** (Cao et al., 2025, "smoother gradients and improved
  convergence"), **S3IM** stochastic structural similarity over randomly
  sampled pixel sets (Xie et al., 2023), **Watson's loss** with frequency-based
  weighting and perceptual masking (Czolbe et al., 2020). Evidence for
  sharpness: human preference "up to 7:1 in favor" of MS-SSIM over per-pixel
  losses (Snell et al. 2015). Known failure: **gradient vanishing in the
  multiplicative formulation**, mitigated by additive/stochastic variants.
  Critically for us, the page states it **does not document applications to PDE
  field regression or simulation-data super-resolution**.
- Search-page context (unfetched leads): SSIM/MS-SSIM used as a *metric* and in
  one case as a CNN training criterion for flow fields ("A CNN Model Based on
  Multiscale Structural Similarity for the Prediction of Flow Fields"); DSO
  (arXiv:2603.26800) argues MSE cannot distinguish vortex displacement from
  minor numerical fluctuation. Displacement-vs-amplitude is the same distinction
  s2-B1's M5a measures.

### Term 3 — interface-localized weighting on phase-field problems

- **Mullins, Kamila, Fahsi, Soulaimani (2025), "Physics-informed neural networks
  for solving moving interface flow problems using the level set approach"** —
  https://arxiv.org/html/2502.02440v1 (fetched). **Negative result**: contrary
  to the search-page summary, this paper uses **no** interface-localized or
  Gaussian band weighting. Its loss is `L = λ_ic L_ic + λ_r L_r + λ_eik L_eik`
  with weights set by **gradient normalization**, not spatial localization.
  Its weights are also all equation-derived (residual, Eikonal, mass
  conservation) — i.e. exactly what ADR 0009 forbids at test time and what s7
  must avoid.
- The wider result set for this term is entirely PINN/physics-embedded
  (phase-field fracture, level-set advection, PINO for phase-field). **No
  usable results** for a data-driven, physics-agnostic, gradient-magnitude
  weight map on supervised field regression.
- Note the one transferable technique that did appear: **gradient normalization
  of multi-term loss weights** (balancing term gradient magnitudes) — relevant
  if a candidate loss is a sum of heterogeneous terms, since fixed λ's are a
  known tuning trap.

## Interpretation

The multi-fidelity literature carries fidelity fusion in the architecture and
leaves the HF-stage objective as plain (weighted) L2, and the SSIM-family
literature is essentially absent from PDE field regression — so the composition
"structured objective x multi-fidelity, few HF samples" is under-occupied even
though each factor is individually published. The physics-agnostic constraint
also bites: the published interface-weighted losses are PINN losses whose
weights come from the equations, not from the field.
