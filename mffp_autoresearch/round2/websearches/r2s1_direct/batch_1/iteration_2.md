# Iteration 2 — floor methodology and the incomplete-condition (stochastic) regime

## Search rationale

Two gaps left by turn 1. (a) program.md §2.2 makes NN-in-condition /
train-mean / zero floor arms mandatory on every model card; is that an
established protocol in the surrogate literature, or is it this project's own
convention? (b) The data check recorded in `summary_so_far.md` shows the
condition vector does not determine the field on pfc / fisher_kpp /
allen_cahn — so the honest question is what the literature does when the
parameters do not identify the target field.

## Search terms used

1. `nearest-neighbor baseline trivial predictor neural operator benchmark surrogate models fail to beat simple baselines`
2. `phase field microstructure prediction from process parameters stochastic initial condition deterministic surrogate conditional mean blurring`
3. (deferred — turn 2 used two terms; the third slot moved to turn 3 to keep
   the prior-art-refutation budget intact)

## Findings

### Term 1 — trivial/training-free floors as a reporting standard

Top results (WebSearch):
- "Benchmarking neural surrogates on realistic spatiotemporal multiphysics
  flows" (REALM) — https://arxiv.org/html/2512.18595
- "Specialized Foundation Models Struggle to Beat Supervised Baselines" —
  https://arxiv.org/html/2411.02796v1
- "Neural operator surrogate models of plasma edge simulations: feasibility and
  data efficiency" — https://iopscience.iop.org/article/10.1088/1741-4326/adfdfb
- "Operator Boosting Produces Pareto-Efficient PDE Surrogates" —
  https://arxiv.org/html/2606.17460
- "Towards Robust Surrogate Models: Benchmarking ML Approaches to Expediting
  Phase Field Simulations of Brittle Fracture" — https://arxiv.org/html/2507.07237
- "Direct Learning of Calibration-Aware Uncertainty for Neural PDE Surrogates"
  — https://arxiv.org/pdf/2602.11090

**Fetched** https://arxiv.org/html/2512.18595 (REALM, arXiv 2512.18595v2):
the benchmark compares surrogate *architectures* against high-fidelity
references and does **not** compare against trivial baselines (mean,
persistence, zero, nearest-neighbor). Its headline is an "illusion of mastery"
— a persistent gap between nominal accuracy metrics and physically trustworthy
behavior — but that is a metric-mismatch argument, not a floor argument.

Reading: a systematic training-free floor panel (NN-in-condition + train-mean +
zero, reported next to every model on every dataset) is NOT standard practice
in this literature. The search engine's own synthesis noted only that some
methods "start from the empirical mean predictor in normalized output
coordinates" — a normalization convention, not a certification arm.

### Term 2 — parameters that do not determine the field

Top results (WebSearch):
- "Learning noisy phase transition dynamics from stochastic partial
  differential equations" — https://arxiv.org/pdf/2604.09664 (abs:
  https://arxiv.org/abs/2604.09664)
- "Machine-learning-based surrogate modeling of microstructure evolution using
  phase-field" — https://www.sciencedirect.com/science/article/abs/pii/S0927025622004645
- "Accelerating phase-field-based microstructure evolution predictions via
  surrogate models trained by machine learning" (npj Comput Mater) —
  https://www.nature.com/articles/s41524-020-00471-8
- "Modeling Stochastic Conditional Dynamics from Sparse Observations via
  Kernel-Stabilized Flow Matching" — https://arxiv.org/pdf/2411.08314
- "Surrogate modeling of microstructure prediction in additive manufacturing"
  (NIST) — https://www.nist.gov/publications/surrogate-modeling-microstructure-prediction-additive-manufacturing

**Fetched** https://arxiv.org/abs/2604.09664 (2026-03-31): handles the
non-determinism by *building noise into the surrogate* (inter-cell flux split
into a deterministic mobility-weighted chemical-potential gradient plus a
learnable noise amplitude) and validates with **ensemble statistics rather than
pointwise metrics**, arguing flux-level stochasticity is "an architectural
necessity rather than an optional enhancement" because deterministic models
fundamentally cannot capture nucleation.

Also from the term-2 synthesis (search-engine text, not fetched, flagged): the
phase-field ML surrogate line universally takes the **initial microstructure as
an input** (3D U-Net on initial microstructure + thermal history), and where a
solver-based initialization is too expensive, a *conditional diffusion model
generates the synthetic initial condition* rather than the parameters being
asked to determine the field.

## Interpretation

Two things land. First, the mandatory floor-arm protocol (§2.2) has no clear
precedent in the surrogate-benchmark literature we can find — REALM, the
strongest 2025-26 benchmark hit, does not do it — so "floor certification for
parametric surrogates" is a live methodological contribution, not a rebadge.
Second, the phase-field surrogate literature agrees with the data check: nobody
predicts microstructure from process parameters *alone*; the initial
microstructure is always an input, or it is generated. On pfc/fisher_kpp/
allen_cahn our condition vector has no IC, so a deterministic condition→HF
model is estimating a conditional mean and its rel-L2 is floored by the
conditional spread. Turn 3 goes at the prior-art refutation for the specific
directions this stream will propose.
