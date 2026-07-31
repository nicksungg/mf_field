# iteration_2 — `r2s4_diag` batch 3

## Search rationale

Field context for B2's Option B (coverage-greedy fit-fold selection on the one
*support-limited* dataset, cahn_hilliard: d_min 3.1178 in 19 standardised dims,
learning-curve slope 0.2327 and accelerating at N_fit = 320) and for the
round-level rule candidate B2's part 7(a) proposes (identifiability × support →
information-limited vs sample-limited, predictable training-free). Under
immutable §5.11 (no new HF data) the only admissible lever is WHICH existing
rows are fit on, so the relevant prior art is fixed-budget subset selection from
an existing pool, plus any published "will more data help?" pre-training
diagnostic.

## Search terms used

1. `fill distance space-filling subset selection of training samples for surrogate model fixed budget error bound`
2. `diagnose whether more training data will help noise-limited versus sample-limited regime learning curve prediction without training`
3. `coreset subset selection training data parametric PDE neural operator surrogate high-dimensional parameter space coverage`

## Findings per term

### Term 1 — fill distance / space-filling subset selection
Top results: *On minimizing the training set fill distance in machine learning
regression* (https://arxiv.org/abs/2307.10988); *Space-Filling Subset Selection
for an Electric Battery Model* (arXiv 2012.03541, PDF only); *Design of
Experiments for Emulations: A Selective Review* (arXiv 2505.09596, PDF only);
several Kriging/GP infill-sampling papers on ScienceDirect (abstract-gated).

FETCHED https://arxiv.org/abs/2307.10988 — Climaco & Garcke, 2023 (rev. Aug
2024). Studies **Farthest Point Sampling (FPS)**, i.e. "selecting a training set
by aiming to minimize the fill distance of the selected set", derives
"theoretical bounds on prediction error based on training set fill distance",
and reports the strategy "significantly reduces the maximum prediction error of
various regression models, outperforming alternative sampling approaches by a
large margin", and "increase[s] model stability for the specific case of Gaussian
kernel regression approaches". Search context adds the standard kernel result
that interpolation error bounds factor into fill distance × function norm ×
constant, and that "space-filling subsets result in more accurate surrogate
models than random subset selection".

→ Option B's *mechanism* (coverage-greedy fixed-budget subset selection, scored
against random/prefix subsets) is published, with theory, in exactly this shape.

### Term 2 — "will more data help?" as a pre-training diagnostic
Top results are mostly pedagogy (learning-curve bias/variance diagnosis blogs),
plus *Learning Curves for Noisy Heterogeneous Feature-Subsampled Ridge Ensembles*
(https://pmc.ncbi.nlm.nih.gov/articles/PMC10350086/), *Sample size determination
for prediction models via learning-type curves* (Wiley, Dayimu 2024), and
*A Risk Decomposition Framework for Pre-Hoc Fine-Tuning Prediction*
(https://arxiv.org/abs/2606.17649).

FETCHED https://arxiv.org/abs/2606.17649 — Luo, Wang & Tang, 2026. Predicts LLM
fine-tuning performance *before* training by "decomposing prediction risk into
two components: an intrinsic limit (static data-model compatibility) and a
reducible optimization variance", proves "optimization variance admits a
necessary lower bound on its decay rate", and organizes tasks into **three
regimes (Static-Sufficient, Dynamic-Critical, Noise-Dominant)** to decide whether
further probing helps. Same *shape* as B2's regime taxonomy, different domain
(LLM fine-tuning, scalar task metrics) and different inputs (probing runs, not a
training-free geometry statistic).

Search context also states the conventional diagnosis explicitly: curves still
descending ⇒ more data pays; both curves flat ⇒ "you've saturated the model's
capacity and more data is wasted"; and names the "signal-dominated /
intermediate / noise-dominated" regime phase diagram. So the *taxonomy* is
common knowledge; what B2 adds is deciding it **training-free** from
(identifiability, d_min).

### Term 3 — coreset / active selection for PDE-surrogate training
Top results: **PICore** (https://arxiv.org/abs/2507.17151, NeurIPS 2025 page
https://neurips.cc/virtual/2025/loc/san-diego/125937); *Data-Efficient Neural
Operator Training via Physics-Based Active Learning*
(https://arxiv.org/html/2605.21348); *Deep adaptive sampling for surrogate
modeling without labeled data* (arXiv 2402.11283, PDF only); *Data-Efficient
Time-Dependent PDE Surrogates* (https://arxiv.org/html/2509.06154v1).

FETCHED https://arxiv.org/abs/2507.17151 — Satheesh, Khandelwal, Ding & Balan,
2025. PICore "identifies the most informative training samples without requiring
access to ground-truth PDE solutions" by "leveraging a physics-informed loss to
select unlabeled inputs by their potential contribution to operator learning",
reporting "up to 78% average increase in training efficiency relative to
supervised coreset selection methods with minimal changes in accuracy". The
criterion is a **physics residual**, not coverage in parameter space. Search
context also surfaces PCA-KMeans trajectory selection and physics-residual-error
acquisition functions as the established alternatives.

Relevance caveat for this project: physics residuals are excluded at test by
r1 ADR 0009 (physics-agnostic at test) — but PICore is a *training-side* selector,
so the exclusion does not automatically apply; it does mean PICore is a
different selector class from the geometry-only one Option B would use.

## Interpretation

Option B's selection mechanism is squarely preempted (FPS/fill-distance, with
error bounds; coreset selection for neural operators with physics-residual
criteria), and even the regime taxonomy exists in another domain with a
pre-training risk decomposition. The unpreempted parts are likely (i) *choosing
the selector from a training-free identifiability × fill-distance measurement
that predicted which dataset is support-limited in advance*, and (ii) doing it in
copy-LF-skill units under a no-solver-at-test MF regime. Refutation searches
needed on both, plus on the "training-free regime classifier" claim itself.
