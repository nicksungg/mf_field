# Iteration 1 — `r2s4_diag` batch 1

## Search rationale

r2s4-B1 is pre-directed to (a) certify training-free floors and (b) certify a
condition→HF 3-seed spread that replaces the provisional noise floor. Before
proposing anything, I need to know whether floor-panel certification and
seed-spread-as-claimable-effect are (i) established benchmarking hygiene with a
citable protocol, or (ii) ad-hoc per-benchmark practice. Open questions 1 and 2
from `summary_so_far.md`. Terms chosen to attack the trivial-baseline question,
the seed-variance-reporting question, and the general "benchmark pitfalls in
SciML" literature that would contain both.

## Search terms used

1. `neural operator PDE surrogate benchmark trivial baselines nearest neighbor constant predictor outperform`
2. `PDE surrogate benchmark random seed variance error bars statistical significance reporting neural operators`
3. `scientific machine learning benchmark pitfalls weak baselines reproducibility neural operators 2024`

## Findings per term

### Term 1 — trivial baselines for PDE surrogates

Top results: Operator Boosting (https://arxiv.org/abs/2606.17460), Predictivity
and Utility of Neural Surrogates of Multiscale PDEs
(https://arxiv.org/html/2604.20061v1), GAOT (https://arxiv.org/html/2505.18781v1),
Multiscale Neural PDE Surrogates (https://arxiv.org/html/2507.18067v2),
Data-Efficient Time-Dependent PDE Surrogates (https://arxiv.org/pdf/2509.06154).
No result directly reports "published neural operator loses to a constant/NN
predictor".

**Fetched — Operator Boosting (https://arxiv.org/abs/2606.17460)**: stagewise
residual-learning framework for compact neural-operator surrogates. Confirmed
from the abstract that it "start[s] from the empirical mean predictor in
normalized output coordinates" and then trains a sequence of small neural
operators on residual fields, folding each correction in through
validation-selected shrinkage. So the **train-mean predictor is used as an
explicit algorithmic starting point / floor** in the current literature — but as
an initialization, not as a reported evaluation arm. 30 dataset-architecture
combinations; 72–95% trainable-parameter reduction. No naive-baseline
comparison table is discussed.

**Fetched — Predictivity and Utility of Neural Surrogates of Multiscale PDEs
(https://arxiv.org/html/2604.20061v1)**: this is the closest hit to r2s4's
floor-certification premise. Verbatim from the fetch: "The key diagnostic is
whether classical reduced-order methods with comparable offline cost achieve
similar accuracy; if so, the benchmark tests interpolation, not the capacity to
handle multiscale physics." It also says "many successful benchmarks live on
low-dimensional solution manifolds where any competent reduced model will
interpolate well" and recommends comparing against "polynomial surrogates,
projection-based Reduced Order Models (ROMs), or neural networks" at identical
offline budget. Proposed reporting standards: problem characterization
(intrinsic dimension, scale separation, Lyapunov timescales), scale-aware
metrics (band-limited errors, derivative norms), end-to-end cost curves against
optimized solvers and ROM baselines at matched hardware. Explicitly **no**
value-of-information or systematic ablation-accounting framework.

### Term 2 — seed variance / significance reporting

Top results: Structure-Aware Epistemic UQ for Neural Operator PDE Surrogates
(https://arxiv.org/html/2603.11052), Data-Efficient and Generalizable Neural
Operators via Fundamental Physics Knowledge (https://arxiv.org/html/2602.15184v1),
PDEBench topic page (https://www.emergentmind.com/topics/pdebench), Active
Learning for Neural PDE Solvers (https://arxiv.org/pdf/2408.01536), Randomized
neural operator with conformal UQ (https://arxiv.org/pdf/2606.29440). Search
summary reports multi-seed mean ± std and 95%-CI-over-seeds shading as
*practice* in recent papers, and PDEBench as maintaining seed provenance — but
surfaced no paper that formalizes a seed-spread-derived
minimum-claimable-effect threshold.

**Fetched — Structure-Aware Epistemic UQ (https://arxiv.org/html/2603.11052)**:
deliberately does NOT use seed/ensemble spread; it injects stochasticity only
through the lifting module (channel-wise multiplicative dropout, Gaussian
feature perturbation), converting parameter uncertainty into uncertainty over
lifted feature fields, then calibrates bands. Reported as having **"no formal
protocol for statistical significance testing" between models** — coverage rate
and bandwidth plus qualitative comparison. Data regime is 1000 samples (2D
Darcy) / 889 (ShapeNet Car), i.e. not the tiny-N regime; the paper does not
explore severely data-limited settings.

**Fetch attempt failed** on https://arxiv.org/pdf/2504.03503 (Operator
Learning: A Statistical Perspective) — the PDF came back as an undecoded binary
stream. Retry as HTML in a later iteration if sample-complexity theory is still
needed.

### Term 3 — SciML benchmarking pitfalls

**Fetched — McGreivy & Hakim, "Weak baselines and reporting biases lead to
overoptimism in machine learning for fluid-related partial differential
equations" (https://arxiv.org/abs/2407.07218; journal version Nature Machine
Intelligence, https://www.nature.com/articles/s42256-024-00897-5)**. Abstract
verbatim finding: "Of articles that use ML to solve a fluid-related PDE and
claim to outperform a standard numerical method, we determine that 79% (60/76)
compare to a weak baseline." Also documents outcome reporting bias and
publication bias, concluding "ML-for-PDE solving research is overoptimistic".
The first PDF fetch (https://arxiv.org/pdf/2407.07218) failed as binary; the
abs-page fetch succeeded but exposes only the abstract — the abstract does not
enumerate a recommended baseline set nor discuss trivial/naive ML floors
(constant, NN-in-parameter, zero). Its baselines are *numerical solvers* at
matched accuracy/runtime, which is a different axis from r2s4's training-free
predictor floors.

## Interpretation

The "compare against a strong baseline" norm is established and heavily cited
(McGreivy & Hakim), and one 2026 position paper (2604.20061) states the
interpolation-diagnostic in almost exactly r2s4's terms — but for ROM/polynomial
surrogates at matched offline cost, not for a NN-in-condition / train-mean /
zero *training-free* floor panel reported as mandatory columns. Nothing found
yet formalizes seed spread into a minimum-claimable-effect threshold; the UQ
literature I sampled explicitly declines to provide a significance protocol.
Next: the value-of-information / privileged-information / auxiliary-signal
ablation-accounting literature, and tiny-N generalization-gap diagnostics.
