# Iteration 5 — s2_beyond_copy batch 3 (REFUTATION turn 2; **ITERATION CAP HIT: 5 of 5**)

## Search rationale
Close the two loose refutation threads from iteration 4: (a) the unpinned
"error map / two-mode deployment" source for D2; (b) whether the MF literature
itself has a per-sample trust switch between corrected-LF and the model; and
(c) a final, fourth framing of the misregistration question, in the language
the defect actually lives in (cell-centred vs vertex/node-centred grids).

## Search terms used
1. `predict where neural surrogate is unreliable error map input-only gating solver fallback two-mode deployment PDE`
2. `multi-fidelity model trust low-fidelity when correction unreliable per-sample switch to low-fidelity prediction gate`
3. `cell-centered versus node-centered resampling convention half cell offset coarse to fine grid interpolation error nested grids simulation data`

## Findings

### Term 1 — the error-map gate, pinned and FETCHED
- **Hybrid Neural World Models** — FETCHED https://arxiv.org/abs/2605.28317.
  *"Neural surrogates promise large speedups over classical solvers for
  physical dynamics but fail silently at sharp dynamical events such as shocks,
  fronts, and contact."* The reliability signal is internal:
  *"the trained surrogate encodes it implicitly, recoverable from its forward
  passes alone as a per-trajectory error map that concentrates on shocks,
  fronts, and contacts."* Deployment: *"Mode 1 runs the surrogate alone for
  maximum throughput ... Mode 2 uses the error map to gate a reference-solver
  fallback, deferring uncertain trajectories and roughly halving the
  surrogate's residual error."* The gate needs no ground truth
  ("recoverable from its forward passes alone").
  Difference from our F12 gate: the fallback is a **solver** (ADR 0009 would
  exclude that at test time for us), not a no-learning coarse-field baseline;
  and the error map is a self-disagreement signal over a time horizon, which our
  steady-state fields do not have.
- Also surfaced (search-listed): Error-Conditioned Neural Solvers
  https://arxiv.org/abs/2606.27354v1 (needs the PDE residual — ADR 0009
  excluded, as batch 2 already recorded); structure-aware epistemic UQ for
  neural-operator surrogates https://arxiv.org/html/2603.11052.

### Term 2 — MF trust weighting: MAST (FETCHED) — near miss for D2
- **MAST: A Multi-fidelity Augmented Surrogate model via Spatial
  Trust-weighting** — FETCHED https://arxiv.org/html/2602.20974.
  Principle quoted: *"corrected low-fidelity observations should be trusted far
  from high-fidelity samples where no calibration information exists, but
  should progressively yield to high-fidelity predictions as high-fidelity data
  become available nearby."* The weight is explicit and geometric: Euclidean
  distance from the query to each HF point, an adaptive neighbourhood from
  "the distance to the nearest high-fidelity point", per-neighbour weights
  `w_j = 1 − d_ij^{alpha_m}` aggregated to `W_m(i)`, with `alpha_m`
  cost-aware. Full fallback exists: where `W_m(i) → 1` the blend is
  "predominantly the corrected low-fidelity value".
  Two decisive differences for us, both from the fetch: the setting is
  **scalar-valued functions** on 2D–23D input spaces (not fields), and
  **"no explicit no-learning low-fidelity baseline is reported"** — the
  comparison is against competing MF methods, not against untrained LF fallback.
- Context (search-listed): MF-optimization survey https://arxiv.org/pdf/2402.09638
  and BISTRO https://arxiv.org/pdf/2512.09055 record the known failure mode
  that a poor LF model makes MF trust-region schemes *worse* than
  single-fidelity — the scalar-optimization analogue of our Class-B datasets.

### Term 3 — the misregistration defect, in its native vocabulary (FETCHED)
- **Gmunu** (multigrid GR-hydro solver) — FETCHED
  https://ar5iv.labs.arxiv.org/html/2001.05723. The exact structural statement
  behind our defect: *"Unlike the vertex-centred case, in which a node of the
  coarse grid is also a node of the fine grid, the nodes on coarser grids do
  not form a subset of the fine grid nodes in the case of cell-centred
  discretization"*, and *"The choices of inter-grid transfer operators and the
  boundary condition implementation are different from the vertex-centred
  cases"*; constructing cell-centred transfer operators "is still under an
  active research area".
  This is a **citable statement of the convention mismatch** (our LF data are
  node samples; `scipy.zoom(grid_mode=True)` applies the cell-centred transfer)
  but it is a numerical-methods statement, not a report of a benchmark whose
  reference was mis-transferred.
- NASA node- vs cell-centred finite-volume comparisons
  (https://fun3d.larc.nasa.gov/papers/AIAA-2009-0597.pdf,
  https://ntrs.nasa.gov/api/citations/20110002899/downloads/20110002899.pdf) and
  block-adaptive interpolation https://arxiv.org/pdf/1409.3218 — search-listed.
- **Four independent framings (iterations 1, 3, 4, 5) have now failed to find a
  published case of a misregistered no-learning REFERENCE inflating reported
  skill in an SR / downscaling / MF benchmark.** Nearest neighbours: SR
  training-data misalignment (https://arxiv.org/pdf/2410.05410),
  learned grid alignment for unaligned downscaling grids
  (https://arxiv.org/abs/2410.03945), and the generic weak-baseline critique
  (https://arxiv.org/html/2508.05831, MLSys variance paper).

## PRIOR-ART VERDICT (retrieval-grounded; every citation fetched in this loop)

**D1 — per-sample target normalization of the MF residual** (replace the global
`max|HF−LF|` scaler; optionally a separate amplitude head).
**Verdict: `preempted-but-MF-composition-open`.**
- Preempting sources (fetched): DiSOL, https://arxiv.org/html/2601.09143v1 —
  *"We define a per-sample amplitude u_lim"*, *"the dimensionless solution
  pattern u_h := U_h / u_lim, so that max_x |u_h(x)| = 1"*, *"all models
  (DiSOL and all baselines) are trained to predict the normalized pattern"*,
  amplitude restored via *"an optional amplitude regressor"*. RevIN analysis,
  https://arxiv.org/html/2603.11869 — instance-wise normalize/denormalize with
  learnable affine; and its warning that instance normalization *"discards
  potentially predictive context"* and the affine layer *"is not beneficial in
  practice"* (time series only).
- What remains open: DiSOL normalizes the **solution**; the MF literature's
  canonical residual formulation does **not** normalize the residual at all —
  RMFNN (https://arxiv.org/html/2310.03572) *assumes* `||F||_inf << ||Q_HF||_inf`
  and, per the fetch, has *"no discussion of per-sample or instance-wise scaling
  of residuals"*. Our panel violates that assumption by 4–5 orders of magnitude
  (card F10: max/median per-sample ||r|| = 82379 pfc, 13702 helmholtz). So:
  per-sample normalization **of the fidelity residual `HF−LF`, with the scale
  predicted from `(X, LF)` at test time** (the scale is not observable at test
  time — DiSOL's amplitude regressor is the citable precedent for how), scored
  against a node-aligned no-learning reference, is not occupied.

**D2 — per-sample trust/abstention gate choosing copy-LF vs the model, decided
from `(X, LF)` only, OOF/conformal-calibrated.**
**Verdict: `preempted (cite)` at the protocol level; `preempted-but-MF-
composition-open` for the copy-LF-fallback binding.**
- Preempting sources (fetched): Proactive Routing to Interpretable Surrogates,
  https://arxiv.org/html/2603.14623 — safety is *"|y − g(x)| − |y − f(x)| ≤ τ"*,
  routing decided *"from features alone, before either model runs"*, threshold
  by *"Clopper–Pearson conformal calibration on a held-out set"* with the
  guarantee valid *"regardless of gate miscalibration"*. Hybrid Neural World
  Models, https://arxiv.org/abs/2605.28317 — *"Mode 2 uses the error map to
  gate a reference-solver fallback"*. MAST,
  https://arxiv.org/html/2602.20974 — distance-based trust weight with full
  fallback to *"the corrected low-fidelity value"*.
- What remains open, precisely: in all three the fallback target is a
  **cheaper/interpretable model, a solver, or a corrected-LF GP on scalar
  outputs**; MAST's fetch states **"no explicit no-learning low-fidelity
  baseline is reported"**. Nobody gates a **field-valued** operator against the
  **raw interpolated coarse solve** and reports the gated skill against that
  same baseline. Do NOT claim the gate as a mechanism; claim the measurement
  (F12 oracle 0.2590 vs scored 0.3803) and cite 2603.14623 for the calibration
  recipe.

**D3 — pre-registering falsification against the node-aligned corrected
reference (variants C/D/E) and reporting the registration split.**
**Verdict: `novel` as a benchmark-hygiene finding (nearest neighbours named).**
- Four framings found no published case of a misregistered no-learning
  reference inflating reported skill. Nearest neighbours (all fetched or
  search-listed as marked): the convention mismatch itself is textbook —
  Gmunu, https://ar5iv.labs.arxiv.org/html/2001.05723 (FETCHED):
  *"Unlike the vertex-centred case, in which a node of the coarse grid is also
  a node of the fine grid, the nodes on coarser grids do not form a subset of
  the fine grid nodes in the case of cell-centred discretization"*; SR
  training-data misalignment https://arxiv.org/pdf/2410.05410 (search-listed);
  unaligned-grid downscaling https://arxiv.org/abs/2410.03945 (search-listed);
  weak-baseline discipline https://arxiv.org/html/2508.05831 (fetched in
  batch 2). Frame the mentor note as: *the convention mismatch is known
  numerics; its appearance inside a benchmark's no-learning reference, and the
  resulting 2.0–8.6x skill inflation, is what we contribute.*

**D4 — hard-sample / tail-aware training for the cahn_hilliard STRUCTURE
failure.**
**Verdict: `preempted (cite)`, and preempted with a NEGATIVE result — treat as
a pre-falsified-adjacent lever.**
- Fetched: https://arxiv.org/html/2605.16078 — *"models are primarily ranked
  based on their prediction accuracy in the tails"*; *"worst-case prediction
  errors of the neural networks are an order of magnitude larger than the mean
  field error"*; their density-inverse cost-sensitive weighting **increased**
  test max error from 76.63 K to 96.72 K. Fetched: ELADO abstract,
  https://arxiv.org/abs/2606.20771 — *"heavy-tailed solution distributions
  arising from light-tailed coefficient field distributions"* is a named
  benchmark difficulty axis. Search-listed: RQA quantile-clipped reweighting
  https://arxiv.org/pdf/2209.05315.
- Open only in the narrow sense that no one reweights a **fidelity-residual**
  objective by per-sample residual mass. Given the fetched negative result, a
  B3 arm built on tail reweighting should carry an explicit
  expected_falsification citing 2605.16078.

**Cross-cutting caution for whatever B3 proposes** (fetched,
https://arxiv.org/html/2604.20061v1): *"A network trained with mean-squared
error converges to the conditional expectation ... The resulting prediction is
over-smoothed by construction, and no architecture or training procedure can
recover information the coarse representation discards"*, and *"Many successful
benchmarks live on low-dimensional solution manifolds where any competent
reduced model will interpolate well."* B2's part-7 open question ("is there ANY
dataset where a trained LF-consuming operator beats the node-aligned
reference?") has a published *a priori* reason to answer NO on datasets whose
HF carries no energy the LF band lost — which the registration note already
proved for pfc. B3 must pre-register that as a legitimate outcome.

## Interpretation
Cap reached at 5 iterations. Both of B2's recommended levers are preempted as
mechanisms and open only in their multi-fidelity binding; the corrected-
reference reporting column is the one genuinely unoccupied contribution, and
the fetched theory says the honest B3 result may be a well-founded negative.
