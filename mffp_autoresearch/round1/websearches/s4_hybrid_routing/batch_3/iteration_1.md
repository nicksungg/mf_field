# iteration_1 — per-dataset / per-task routing in scientific ML

## Search rationale

The B3 slot is a ROUTER: LF-defect-correction wherever the test split ships an
LF fidelity, champion transfer path where it does not (`ifc_poisson`). The
first refutation axis is therefore the routing *object* itself. Three angles:
(a) routing between a **correction** path and a **surrogate/transfer** path in
SciML, (b) MoE/gating over neural operators keyed on a **dataset property**
(the closest published family; MoE-POT 2510.25803 was already fetched in
batch 1 so this turn looks for the ones batch 1 missed), (c) MF models that
must act when the **LF input is missing** at inference — the exact condition
that keys our router.

## Search terms used

1. `per-dataset model routing scientific machine learning selecting between correction model and surrogate model PDE`
2. `mixture of experts neural operators routing PDE families gating network dataset property`
3. `multi-fidelity model missing low-fidelity data at inference fallback single-fidelity prediction`

## Findings

### Term 1 — correction-vs-surrogate routing
Top returns: https://arxiv.org/html/2601.08404v1 (OOD generalization of 2D PDE
surrogates, small data), https://arxiv.org/pdf/2509.21670 (MORPH, arbitrary
data modality), https://arxiv.org/html/2503.10048 (Model-Agnostic Knowledge
Guided Correction / HyPER — a *correction* applied to a surrogate rollout, not
a router between two paths), https://royalsocietypublishing.org/rspa/article/481/2315/20250168/234236/
(surrogate robustness via data assimilation), https://arxiv.org/html/2507.18067v1
(multiscale PDE surrogates + downscaling).
The engine's own closing sentence: *"the specific 'per-dataset model routing'
concept you mentioned wasn't prominently featured in these results"*. **No
usable hit for a per-dataset correction-vs-transfer router.**

### Term 2 — MoE / gating over neural operators
- **A Greedy PDE Router for Blending Neural Operators and Classical Methods**,
  https://arxiv.org/pdf/2509.24814 (**fetched**, PDF; abstract re-fetched from
  https://arxiv.org/abs/2509.24814 for a clean quote). Abstract verbatim:
  *"Designing an optimal hybrid iterative solver — where, at each iteration, a
  solver is selected from an ensemble of solvers to leverage their
  complementary strengths — poses a challenging combinatorial problem."* The
  routing signal is **estimated error at each iteration** via *"an approximate
  greedy router that efficiently mimics a greedy approach to solver
  selection"*; granularity is **per-iteration** inside an iterative solve. The
  first (PDF) fetch also read the granularity as per-region and could not
  produce a verbatim decision rule — recorded as ambiguity; the `/abs/`
  abstract is the citable text. This is the nearest published "router between a
  learned and a classical path" and it is **not** keyed on a dataset property
  and **not** multi-fidelity.
- **Eradicating Negative Transfer in Multi-Physics Foundation Models via Sparse
  Mixture-of-Experts Routing**, https://arxiv.org/pdf/2605.15179 (**fetched**).
  Router granularity is **dataset level**, signal is **dataset identity**:
  *"Negative transfer occurs when training a unified model across multiple
  physics domains causes performance degradation on individual tasks compared
  to domain-specific models"*, avoided by *"porous routing"* — different
  datasets preferentially use different expert combinations. This is the
  closest published statement that **per-dataset routing is the fix for
  cross-dataset interference**.
- Also returned, not fetched: https://arxiv.org/abs/2510.25803 (MoE-POT —
  already fetched in `websearches/s4_hybrid_routing/batch_1/`; gating weights
  identify the PDE dataset with 98% accuracy), https://arxiv.org/pdf/2511.11627
  (SA-EMO), https://arxiv.org/pdf/2605.02124 (soft-to-hard routing),
  https://research.google/blog/mixture-of-experts-with-expert-choice-routing/.

### Term 3 — MF with missing LF at inference
Returns: https://arxiv.org/pdf/2301.05729 (GAR — treats *missing low-fidelity
data as latent variables* in a joint likelihood, i.e. imputation, **not**
routing to a different path), https://dl.acm.org/doi/10.1007/978-981-95-7072-0_32
(selection of *which LF data to acquire*, a design-of-experiments question),
https://arxiv.org/pdf/2304.04862 + https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10547726/
(graph-Laplacian few-shot LF improvement), https://arxiv.org/pdf/2511.15934
(implicit/explicit model error), https://iopscience.iop.org/article/10.1088/2632-2153/ad7ad5.
**No usable result**: nobody routes on *availability* of the LF field at
inference; the published treatments are imputation (GAR) or acquisition.

## Interpretation

Per-dataset routing IS published — but as MoE over a *shared* backbone keyed on
dataset identity for negative-transfer control (2605.15179, MoE-POT), and as
per-iteration solver selection inside a hybrid solve (2509.24814). Nothing
found routes between a *defect-correction* path and a *transfer* path, and
nothing routes on **LF availability**; GAR's answer to a missing LF is to
integrate it out, not to switch estimators.
