# Iteration 4 — refutation pass 1 (ENOUGH declared on field survey)

## Search rationale

**ENOUGH**: three field-survey turns have located the named literature for every
B2 candidate (differogram / difference-based variance estimation for the ceiling;
MSE-conditional-mean + post-hoc calibration for the shrinkage arm; generic
bias-variance-noise + operator sample-complexity for the overfitting anatomy).
Remaining iterations go to refuting novelty (3.3).

## Candidate directions this batch expects r2s4-B2 to propose

Derived from `experiment_cards/r2s4_diag/batch_1/B1.json 7_gap_and_future` and
program.md 12.4:

- **D1** — value-of-LF accounting: matched architecture/budget +/- LF-training
  signal, run on **helmholtz first** (the only dataset with certified headroom),
  with fisher_kpp / pfc / allen_cahn **pre-registered as NULL** datasets on the
  strength of B1's measured aleatoric barrier.
- **D2** — a ceiling estimator with support at 19 condition dims and at
  N_hf = 5 (B1's k-NN / matched-pair estimators have none): i.e. subspace or
  sensitivity-based dimension reduction *before* neighbour matching.
- **D3** — post-hoc shrinkage toward the model's own mean field, train-fold
  calibrated, as a MANDATORY reported arm and as the diagnostic statistic
  lambda*.
- **D4** — overfitting anatomy at N_hf in {5,20,50} (searched in iteration 3).

## Search terms used

1. `active subspace dimension reduction before nearest neighbor noise variance estimation high dimensional inputs` (D2)
2. `ablation study does low-fidelity data help matched budget same architecture negative result multifidelity surrogate no benefit` (D1)
3. `preregistered negative control dataset machine learning experiment predicted null result methodology` (D1 methodology)

## Findings

### Term 1 (D2) — subspace reduction before neighbour-based variance estimation

Both halves exist separately and named:

- "The Global Active Subspace Method" — https://arxiv.org/pdf/2304.14142 /
  abs page **FETCHED**: "The method uses expected values of finite differences of
  the underlying function to identify the important directions, and builds a
  surrogate model using the important directions on a lower dimensional
  subspace"; "accurate, efficient, and robust with respect to noise or lack of
  smoothness in the underlying function". Crucially, the fetched abstract page
  does **NOT** mention k-NN regression or projecting before distance
  computation — the search summary's claim that "active subspace methods have
  been tested for improving the performance of KNN regression … functions are
  first projected onto the active subspace, and then standard Euclidean distance
  is computed" is SNIPPET-ONLY and was not confirmed in the fetch. **Do not cite
  it as established.**
- "Nearest-Neighbor Variance Estimation (NNVE)" (JASA 97:460) —
  https://www.tandfonline.com/doi/abs/10.1198/016214502388618780 — a named
  published estimator that "measures 'outlyingness' … by the standardized
  distance between the point and its Kth nearest neighbor" and is "robust
  against a large proportion of noise points" (SNIPPET; paywalled, not fetched).
  It is robust *covariance* estimation, not conditional-noise estimation for a
  regression map — adjacent, not the same object.
- Also surfaced, unfetched: https://arxiv.org/pdf/2510.11871 (active subspaces
  in infinite dimension — the function-valued-output case, closest in spirit to
  a condition->field map), https://arxiv.org/pdf/2606.02315,
  https://www.sciencedirect.com/science/article/abs/pii/S0045782520304254
  (generalized active subspace for **mixed aleatory-epistemic** UQ).

### Term 2 (D1) — matched-budget MF ablations

- "Towards Multi-Fidelity Scaling Laws of Neural Surrogates in CFD" —
  https://arxiv.org/abs/2511.01830 — **FETCHED (abstract)**: "the first study of
  empirical scaling laws for multi-fidelity neural surrogate datasets"; it
  "reformulate[s] classical scaling laws" by "decomposing the dataset axis into
  compute budget and dataset composition"; conclusion is budget-dependent
  optimal LF:HF mixing. Snippet-level detail (NOT confirmed in the fetch, do not
  quote as fetched): model size fixed across experiments; "when the available
  dataset generation budget is limited, allocating all resources to
  high-fidelity samples does not lead to optimal test performance"; and the
  caveat "not all low-fidelity data necessarily improves model performance".
  **This is the closest published relative of D1** — a matched-model,
  budget-controlled LF-vs-HF composition study — but it is a *data-mixing under
  a generation budget* study for LF-consuming surrogates, not a
  privileged-information ablation where LF is absent at test.
- Unfetched neighbours: https://arxiv.org/pdf/2006.08341 (MF NAS with knowledge
  distillation), https://arxiv.org/pdf/2404.14456,
  https://www.sciencedirect.com/science/article/abs/pii/S1270963824000610.

### Term 3 (D1 methodology) — pre-registered nulls / negative controls

- Preregistration in ML exists as an advocacy literature: "Perspectives on
  Machine Learning from Psychology's Reproducibility Crisis" —
  https://arxiv.org/abs/2104.08878 — **FETCH RETURNED ABSTRACT PAGE ONLY**; the
  fetcher explicitly declined to attribute claims about preregistration/HARKing/
  null results to it without the full text. Treat as a pointer, not a citation
  for specific claims. The general framing "researchers publicly declare their
  hypotheses, experiments, and analysis plans before running their experiments …
  a foil against … HARKing, p-hacking, and selectively reporting" appears as a
  SNIPPET alongside https://www.cos.io/initiatives/prereg.
- "Dead Science Walking: Publication Bias and the AI Scientist Pipeline" —
  https://arxiv.org/pdf/2606.04220 (unfetched) — snippet: AI-scientist systems
  should retrieve "failed replications, negative trials, and null results in
  machine-readable form, with a structured schema for null results including
  hypothesis, protocol, outcome, effect size, confidence interval,
  preregistration link, and provenance". Directly endorses what an r2s4 card
  would produce.
- Snippet also notes the general scarcity: papers "infrequently assess
  algorithms in hypothetical task scenarios where no discernible effect is
  expected, though such analyses … approximate the null-distribution of the
  test-statistic".
- **No result found** where the null datasets of an ablation are pre-registered
  *because an information/aleatoric ceiling was measured first*.

## Interpretation

D1's components are each published (matched-budget MF composition studies;
preregistration; negative controls) but the specific composition — LF as
privileged train-only information, with the expected-null datasets certified in
advance by a measured aleatoric ceiling and the expected-signal dataset chosen by
certified headroom — was not found in any search. D2's two halves (active
subspace reduction; neighbour-based variance estimation) exist separately and
their combination was suggested only by an unconfirmed snippet; the honest B2
framing is "compose two named published methods", not "new estimator".
