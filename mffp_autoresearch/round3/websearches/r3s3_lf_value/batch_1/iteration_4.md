# Iteration 4 — r3s3_lf_value, batch 1 (refutation pass, part 2; final iteration)

## Search rationale

Turn 3 refuted D3 (privileged-teacher distillation into a deployment-input-only
student is published, with its failure mode characterised). This turn attacks the two
remaining candidate directions at their weakest points:

- **D1** — if the condition vector is *certified sufficient*, is the residual value of
  privileged/auxiliary data already characterised in theory (variance reduction /
  regularisation), which would make "LF-at-train helps by rate, not information" a
  restatement rather than a finding?
- **D2** — does an established vocabulary exist for *deciding* information-limit vs
  optimisation-limit, which would preempt r3s3 claiming the identifiability-vs-
  trainability discrimination as a novel diagnostic?

This is the last iteration (cap 5 not reached; stopping at 4 because both refutation
questions returned decisive, fetched answers and no candidate direction is left
unpriced).

## Search terms used

1. `privileged information provides no additional information when input is sufficient statistic distillation acts as variance reduction regularization regression`
2. `benchmark where parameter vector exactly determines PDE solution field does multi-fidelity still help sample efficiency deterministic mapping study`
3. `distinguishing whether failure is due to insufficient training data or optimization difficulty experiment design overparameterized surrogate phase retrieval`

## Findings

### Term 1 — what privileged data is worth when the input already determines the target

- **Safaryan, Peste & Alistarh, "Knowledge Distillation Performs Partial Variance
  Reduction", NeurIPS 2023** — **fetched (PDF body extracted)**
  https://proceedings.neurips.cc/paper_files/paper/2023/file/ee1f0da706829d7f198eac0edaacc338-Paper-Conference.pdf
  Verbatim:
  > "We show that, in the context of linear and deep linear models, KD can be
  > interpreted as a novel type of **stochastic variance reduction mechanism** ...
  > showing that KD acts as a form of **partial variance reduction, which can reduce
  > the stochastic gradient noise, but may not eliminate it completely, depending on
  > the properties of the teacher model**. Our analysis puts further emphasis on the
  > need for careful parametrization of KD, in particular w.r.t. the weighting of the
  > distillation loss."
  Read against our regime: when the observed input is sufficient, the surviving channel
  for a train-only auxiliary signal is exactly this — gradient-noise / variance
  reduction, i.e. an **optimisation** channel — and it is already formalised.
- Search returns, not fetched: https://arxiv.org/pdf/2209.08754 (arXiv version of the
  turn-3 PFD paper — "reducing the variance of model estimates by exploiting privileged
  features and unlabeled samples"); https://arxiv.org/html/2605.13143v1 (generalization
  of KD, information-theoretic view); https://arxiv.org/html/2410.01611 (DRUPI: dataset
  reduction using privileged information).

### Term 2 — MF on a benchmark where the parameters determine the field

- Search returns, none fetched: https://arxiv.org/abs/2605.16118 (Multi-Fidelity Flow
  Matching — "conditioning on the low-fidelity solution makes the residual refinement
  problem substantially easier than unconditional field generation"; LF is a *test-time
  condition*, i.e. not our regime); https://arxiv.org/html/2602.01176v1 (MF PINNs with
  Bayesian UQ for parametric PDEs); https://arxiv.org/pdf/2301.05729 (GAR);
  https://arxiv.org/pdf/2311.05606 (diffusion-generative MF); https://arxiv.org/pdf/2306.06904
  (differentiable MF fusion via NAS + transfer learning).
- **No usable result** for the specific setup: a benchmark carrying an explicit
  *completeness certificate* (HF field exactly reconstructible from the stored
  parameter vector) used to ask what LF can still contribute. Every retrieved MF-for-PDE
  paper either keeps LF in the inference path or never certifies that the parameters
  determine the field.

### Term 3 — deciding information-limit vs optimisation-limit

- **Cavaliere, Zdeborova et al.-lineage work: "Isolating the hard core of phaseless
  inference: the Phase selection formulation", arXiv:2502.04282** — **fetched (PDF body
  extracted)** https://arxiv.org/pdf/2502.04282. Verbatim:
  > "...phase retrieval ... exhibit[s] an **algorithmically hard phase where all known
  > polynomial-time algorithms struggle**, becoming trapped in local minima with low
  > overlap with the true signal. An interesting observation, however, is that from the
  > **information-theoretical point of view, Phase retrieval becomes possible — in
  > principle — as soon as the number of measurements equals the dimensionality of the
  > signal** ... Yet the loss of phase information strongly hinders the inference
  > performance of different local-search algorithms."
  This is the canonical **statistical-to-computational gap** vocabulary, and it maps
  onto r2s3-B4's cahn_hilliard question with uncomfortable precision: B4 found the
  no-LF arm's predictions essentially *uncorrelated with truth* (median per-sample
  cosine 0.0003-0.0385) while the LF arm is aligned (0.962-0.964) — i.e. the no-LF arm
  looks like a solver trapped in a low-overlap local minimum, not like a solver denied
  information. The distinction r3s3 wants to draw is therefore **a known distinction
  with a known name**; only the measurement on this panel is open.
- Search returns, not fetched: https://arxiv.org/abs/2009.12820 (experimental design
  for overparameterized/interpolative learning — classical OED theory targets
  *underparameterized* models); https://jmlr.csail.mit.edu/papers/volume22/20-603/20-603.pdf
  (classification vs regression in overparameterized regimes).

## Interpretation

Both refutation questions came back the same way: the **frames** are published
(privileged data as variance reduction / rate acceleration; statistical-vs-algorithmic
thresholds as the information-vs-optimisation dichotomy), and the **composition** is
not (LF-at-train priced in copy-LF skill units on a completeness-certified parametric
PDE panel, with LF absent from the test path by construction, at N_hf = 5 on the ifc
ladder). No iteration found a work that measures LF's train-only value where the
condition provably suffices. That is the verdict recorded in `report.md`.
