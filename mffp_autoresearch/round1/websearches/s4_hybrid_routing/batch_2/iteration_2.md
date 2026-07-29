# Iteration 2 — context density for attention-based correctors

## Search rationale

B1's LICENSED-2 says the corrector's only view of the LF field is `n_ctx = 1024`
points = 6.25-25% of the LF grid, and that recovered LF-direction fidelity
tracks coverage (pfc at 25% -> cosine 0.834; cahn_hilliard/fisher_kpp at 6.25%
-> 0.642/0.538). The prior-art question is therefore precise: **is the effect of
attention-context DENSITY on accuracy already published?** If yes, "widen the
context" is engineering, not a finding, and the card must claim no novelty for
it. Terms attack (1) generic operator-transformer context-point ablations,
(2) Transolver's own slice/point ablations (our corrector IS a Transolver),
(3) cross-attention conditioned on a coarse field specifically.

## Search terms used

1. `neural operator transformer number of context points ablation subsampled query points resolution attention full field input coarse`
2. `Transolver physics attention slice tokens number of slices ablation resolution scaling point cloud subsampling`
3. `cross-attention conditioning on coarse simulation field dense context tokens super-resolution correction neural operator`

## Findings

### Term 1 — context-count ablation exists and SATURATES (FETCHED)
- **AB-UPT**, "Scaling Neural CFD Surrogates for High-Fidelity Automotive
  Aerodynamics Simulations via Anchored-Branched Universal Physics Transformers",
  https://arxiv.org/html/2502.09692v3 — **FETCHED.** Verbatim: *"Increasing M
  enhances contextual information available at each query location without
  changing the amount of model parameters, thereby improving performance up to a
  saturation point (see Figure 5)."* (`M` = number of anchor tokens each query
  cross-attends to.) The fetch could not surface Figure 5's numbers, so the
  citable content is the **qualitative law** (more context helps, then
  saturates), not a coverage threshold.
- **GAOT**, "Geometry Aware Operator Transformer...", https://arxiv.org/html/2505.18781v4
  — **FETCHED, negative for our question.** Its ablations live in an appendix the
  fetch could not reach; the only quotable line is *"training GAOT on a randomly
  selected set of less than 10% of the total input points (per batch)"* for
  DrivAerNet++, which the fetch itself flags as *"their neural field capability
  rather than an ablation on attention context size"*. **Recorded as not usable.**
- Search-return (NOT fetched, so not citable as evidence, recorded to avoid
  re-searching): the engine summarised a centroid-sampling ablation where
  *"changing the percentage of sampling points from 7.6% to 30% yields similar
  accuracy"* on Elasticity while *"increasing the percentage from 3.3% to 26.4%
  steadily improves accuracy with diminishing returns beyond roughly 20-26%"* on
  PUC, recommending *"sampling at about 15-30% of the boundary points"*. The
  engine did not attribute it to a specific one of the returned papers and the
  two fetches above did not confirm it. **Treated as an unattributed lead, not a
  citation.** If confirmed it would be the closest thing to a published
  coverage-threshold result — and notably it says the answer is DATASET-DEPENDENT,
  which is exactly B1's pattern.
- Other returns: https://arxiv.org/html/2504.19452 (GINOT),
  https://www.sciencedirect.com/science/article/pii/S0045782525009405,
  https://arxiv.org/pdf/2602.04940 (Transolver-3, industrial-scale).

### Term 2 — Transolver's own ablation is about slices, not context density
- Search-returns state the slices matter: *"Ablation studies confirm that the
  learnable slices are critical for Transolver's performance; replacing them with
  fixed regular squares significantly degrades results, even on regularly gridded
  data like Darcy."* (engine summary over https://www.emergentmind.com/topics/Transolver-Architectures
  and the Transolver paper cluster) and that Physics-Attention *"assigns input
  points to M physical states ... reducing attention cost from O(N^2) to O(NK)"*.
  Transolver++ https://arxiv.org/pdf/2502.02414 and Transolver-3
  https://arxiv.org/pdf/2602.04940 scale the POINT COUNT to millions — i.e. the
  published Transolver line already treats "feed all the points" as the norm and
  subsampling as a budget compromise.
- **High-value adversarial lead**: "Transolver Is a Linear Transformer:
  Revisiting Physics-Attention Through the ..." (AAAI),
  https://ojs.aaai.org/index.php/AAAI/article/download/37003/40965 — **FETCH
  FAILED** (1.5 MB binary PDF, not decodable). B1's report already listed this
  claim as *uncitable*; it stays uncitable after a second attempt. Retry via a
  text mirror in iteration 3, because if Physics-Attention reduces to linear
  attention it directly weakens the "attention is the right corrector" premise.

### Term 3 — coarse-field cross-attention exists, and the attention weights ARE the interpolator
- **WorldParticle**, https://arxiv.org/pdf/2605.15305 — search-return only
  (not fetched): *"At decoder layer, particle tokens query super tokens through
  cross-attention, and the decoder performs a learned coarse-to-fine lifting
  where attention weights act as data-adaptive interpolation weights from
  super-token anchors to particles."* This is the mechanism-level statement that
  a sparse-anchor cross-attention decoder is a **learned interpolator** — the
  same reading B1 arrived at empirically ("read the coarse solve through a
  1024-point cloud and drag the FNO toward it").
- Also returned: https://arxiv.org/pdf/2603.00149 (physics-consistent diffusion
  for fluid super-resolution via multiscale residual correction — coarse field in,
  residual correction out), https://arxiv.org/pdf/2606.22946 (neural operator
  processes under partial observations, zero-shot super-resolution protocol).

## Interpretation

"More attention context helps, up to saturation" is published as a general law
(AB-UPT, fetched), and the Transolver line's own trajectory is toward feeding
*all* points, so **widening `n_ctx` carries no novelty**. What no fetched source
provides is a coverage threshold for a **coarse-solve LF field as the context of
a fidelity-gap corrector at N_hf ~ tens**; and the WorldParticle framing suggests
the honest hypothesis is that dense context makes the corrector a *better
interpolator of LF* — i.e. it raises attainment toward the skill-1.0 ceiling B1
diagnosed, and does not by itself break it.
