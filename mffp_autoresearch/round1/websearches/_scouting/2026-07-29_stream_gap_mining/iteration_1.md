# Iteration 1 — angles (a) cross-dataset pretraining, (c) retrieval, (d) in-context

## Search rationale

Open the three highest-prior angles from the operator brief. (c) is prompted
by the in-round finding that a training-free knn10-in-X beats the 200-epoch
champion on `pfc` by 3.045 skill units (above the 1.151 floor) - an
instance-based component demonstrably carries signal a trained FNO does not.
(d) is prompted by "few HF pairs define the task". (a) is the deferred
`s8_data` candidate and needs its literature support assessed before the
operator spends a stream slot on it.

## Search terms used

1. `retrieval-augmented neural operator PDE nearest-neighbor prior 2025`
2. `in-context operator learning few-shot PDE adaptation 2025 2026`
3. `multi-fidelity operator learning cross-dataset pretraining low-fidelity
   corpus transfer few high-fidelity samples`

## Findings per term

### T1 — retrieval-augmented neural operator

No paper matching "retrieval-augmented neural operator" as a named method
surfaced. Nearest neighbors returned:

- Buitrago-Restrepo et al., ICLR 2025 (per search summary): explicit **memory
  buffers** storing spatiotemporal patterns for time-dependent PDEs, to reduce
  autoregressive rollout error. Memory over a model's own trajectory, not
  retrieval from a training bank.
- "Operator Boosting Produces Pareto-Efficient PDE Surrogates" —
  https://arxiv.org/pdf/2606.17460 — FETCHED. Sequential residual boosting:
  train small operators iteratively, each correcting the previous one's
  residual; Pareto-better accuracy/cost than one big FNO/DeepONet. **Not
  multi-fidelity** (explicitly: "residual boosting of PDE surrogates rather
  than multi-fidelity data"). Ensemble/cascade class, not retrieval.
- "Beyond Nearest Neighbors: Semantic Compression and Graph-Augmented [vector
  search]" — https://arxiv.org/pdf/2507.19715 — IR paper, not PDE. Not usable.

**Interpretation for T1**: retrieval/nonparametric components for operator
learning appear to be an *under-occupied* niche in the PDE literature; what
exists is memory-over-own-rollout, not bank retrieval. Needs one more targeted
pass (iteration 2/3) before any novelty claim.

### T2 — in-context operator learning, few-shot

- **MOFS: Multi-Operator Few-Shot Learning for Generalization Across PDE
  Families** — https://arxiv.org/abs/2508.01211 — FETCHED. Two-stage:
  prompt-conditioned inference on known operators, then contrastive fine-tuning
  aligning vision/frequency/text latents. Components: shared FNO encoder with
  self-supervised pretraining (masked-field reconstruction + frequency-spectrum
  prediction), text-conditioned operator embeddings, and
  **memory-augmented multimodal prompting with gated fusion**. Benchmarks
  Darcy Flow + Navier-Stokes variants. **Explicitly NOT multi-fidelity** (the
  fetched abstract has no LF/HF notion). ICLR 2026 submission
  (https://openreview.net/forum?id=x46qJUo38Q).
- Also surfaced, not fetched: "Graph In-Context Operator Networks for
  Generalizable Spatiotemporal Prediction" https://arxiv.org/pdf/2603.12725;
  "PDE Generalization of In-Context Operator Networks: 1D Scalar Nonlinear
  Conservation Laws" https://arxiv.org/pdf/2401.07364; "Test-time
  Generalization for Physics through Neural Operator Splitting"
  https://arxiv.org/pdf/2602.00884; "Pre-Generating Multi-Difficulty PDE Data
  for Few-Shot Neural PDE Solvers" https://arxiv.org/pdf/2512.00564; "ENMA"
  https://arxiv.org/pdf/2506.06158.

**Interpretation for T2**: the in-context/meta-learning class is well
populated and its stated target is *cross-PDE-family* generalization, which
is NOT this round's problem (our 6 panel datasets are each trained
separately). ICON-style methods also want many demonstration pairs and a
transformer training budget - a poor fit for a 200-epoch smoke tier.

### T3 — cross-dataset / multi-fidelity pretraining

- "Multi-fidelity prediction of fluid flow and temperature field based on
  transfer learning using Fourier Neural Operator" —
  https://arxiv.org/pdf/2304.06972 (WebFetch FAILED: maxContentLength
  exceeded; recorded as a search-result hit only, no content claim made).
- "Multi-fidelity Fourier Neural Operator for Fast Modeling of Large-Scale
  Geological Carbon Storage" — https://arxiv.org/pdf/2308.09113 (hit only).
- "Understanding multi-fidelity training of machine-learned force-fields" —
  https://arxiv.org/pdf/2506.14963 (hit only).
- "Cross-functional transferability in universal machine learning interatomic
  potentials" — https://arxiv.org/pdf/2504.05565 /
  https://www.nature.com/articles/s41524-025-01796-y (hit only).
- Search-engine synthesis (not a fetched claim, flagged as such): the field
  names three strategies - transfer learning, multi-fidelity learning, mixed
  multi-fidelity training - and names **negative transfer** as the documented
  failure mode when LF/HF correlation is weak.

**Interpretation for T3**: LF-pretrain -> HF-finetune is the *textbook*
recipe, i.e. exactly what `mf_fno_transfer_film` already is. Angle (a) as
"pretrain on LF then finetune on HF" is preempted by the whole field. The only
version of (a) that could be novel is **cross-DATASET** pretraining (pretrain
on the 35+ non-panel dataset dirs, finetune per panel dataset), which needs
its own refutation search AND an operator fairness ruling under immutable 1.

## Interpretation (overall)

The three angles separate sharply: (d) in-context is well-populated but aimed
at a different problem (cross-family generalization) and budget-hostile;
(a) LF->HF pretraining is preempted by the field and by our own champion;
(c) retrieval-from-a-training-bank is the one with no direct PDE hit yet and
the one our own knn10 measurement independently motivates. Iteration 2 goes to
(b) uncertainty/trust-region fusion and (e) recurring-mechanism sweep.
