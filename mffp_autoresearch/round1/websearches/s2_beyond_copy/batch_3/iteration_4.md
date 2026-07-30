# Iteration 4 — s2_beyond_copy batch 3 (REFUTATION turn 1)

## Search rationale
Field context declared ENOUGH at the end of iteration 3. These terms are
adversarial: each tries to REFUTE the novelty of one likely B3 direction.
D1 = per-sample target normalization of the MF residual; D2 = per-sample
trust/abstention gate selecting copy-LF vs model; D3 = the corrected-reference
(registration) reporting column and its benchmark-hygiene framing.

## Search terms used
1. `two-head network predicts normalized field shape and separate amplitude scale factor per sample operator learning magnitude decoupling` (refutes D1)
2. `conformal prediction fallback to physics baseline per input select neural surrogate or solver guarantee scientific machine learning` (refutes D2)
3. `benchmark baseline implementation bug inflated reported improvements machine learning re-evaluation corrected baseline reverses conclusions` (refutes D3)

## Findings

### Term 1 — D1 REFUTED in operator learning: "magnitude decoupling" (DiSOL)
- **Discrete Solution Operator Learning for Geometry-Dependent PDEs (DiSOL)** —
  FETCHED https://arxiv.org/html/2601.09143v1 (the `/pdf/` fetch aborted on
  size and the `/abs/` page carries only the first abstract line — see Dead
  ends). Quotes obtained from the HTML body:
  *"We define a per-sample amplitude u_lim"*; *"the dimensionless solution
  pattern u_h := U_h / u_lim, so that max_x |u_h(x)| = 1"*; all models predict
  the normalized pattern so that *"the maximum absolute value across spatial
  locations equals one"*; *"If an absolute-amplitude prediction is required, it
  can be reconstructed as Û_h = û_lim · û_h using an optional amplitude
  regressor"*; and *"all models (DiSOL and all baselines) are trained to
  predict the normalized pattern"*.
  So per-sample amplitude normalization + optional amplitude head is an
  established, named practice in operator learning ("magnitude decoupling"),
  applied to the SOLUTION field. The fetched HTML does **not** contain the
  log-amplitude regression / unstable-training discussion that the search
  snippet asserted, so that part is NOT cited.
  Not found in it: application to a **fidelity residual** `HF − LF` target, or
  any evaluation against a no-learning coarse baseline.

### Term 2 — D2 REFUTED at the protocol level, in the PDE setting
- Conformal prediction for neural operators
  https://arxiv.org/html/2606.09923, surrogate-UQ conformal
  https://arxiv.org/html/2408.09881v2 + IOP version
  https://iopscience.iop.org/article/10.1088/2632-2153/ae2e7b, multi-granularity
  CP for neural-operator surrogates https://arxiv.org/html/2607.17297 — all
  search-listed. Distribution-free finite-sample coverage for FNO fields is
  routine; localized CP "accurately identifies regions of elevated uncertainty".
- The search summary surfaces a **two-mode deployment policy**: "Mode 1
  (surrogate alone) for routine trajectories and Mode 2 (selective solver
  fallback gated by the error map)", motivated because "neural surrogates ...
  fail silently at sharp dynamical events, and detecting where the surrogate is
  unreliable without solving the system from scratch is the bottleneck". The
  source URL was not pinned in this turn — chased in iteration 5.
- Together with iteration 2's FETCHED
  https://arxiv.org/html/2603.14623 (safe iff `|y−g(x)| − |y−f(x)| ≤ τ`,
  Clopper–Pearson conformal calibration on a held-out set, routing from
  features alone), the *gating protocol* is published prior art.

### Term 3 — D3: benchmark-hygiene framing exists, the specific defect does not
- Accounting for Variance in ML Benchmarks (MLSys 2021),
  https://proceedings.mlsys.org/paper_files/paper/2021/file/0184b0cd3cfb185989f858a1d9f5c1eb-Paper.pdf
  — PDF fetch dead (binary). Search summary: "properly accounting for variance
  factors may go as far as changing the conclusions for the comparison, as
  shown for recommender systems, neural architecture pruning, and metric
  learning"; "comparisons to weak baselines can lead to inflated estimates of
  performance improvements".
- Nothing found on a **resampling-convention/registration bug in the reference
  itself** inflating a scientific-ML benchmark. Three framings now (iterations
  1, 3, 4); one final attempt in iteration 5 before declaring it an open,
  reportable observation for the mentor note.

## Dead ends
- `https://arxiv.org/pdf/2601.09143` and `.../2508.17902` → maxContentLength
  exceeded. `https://arxiv.org/abs/2601.09143` → abstract truncated to one
  sentence. `/html/<id>v1` worked; **prefer `/html/...v1` for large papers**.
- `proceedings.mlsys.org/...0184b0cd...Paper.pdf` → undecoded PDF binary.

## Interpretation
Both non-architectural levers B2's part 7 recommended are now retrieval-refuted
as *mechanisms*: per-sample amplitude normalization is DiSOL's "magnitude
decoupling" and the no-harm routing gate with conformal calibration is
arXiv:2603.14623. What no fetched source does is apply either to a
**multi-fidelity residual target measured against the no-learning coarse
reference** — which is exactly the composition B3 needs, and exactly the kind
of "preempted-but-MF-composition-open" verdict §13.3 expects.
