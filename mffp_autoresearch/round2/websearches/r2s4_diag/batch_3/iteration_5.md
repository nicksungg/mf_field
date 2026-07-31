# iteration_5 — `r2s4_diag` batch 3 — REFUTATION PASS 2

## Search rationale

Refutation continues on D1 (teacher-projection diagnostic), D2 (coverage-greedy
fixed-budget subset selection gated by a training-free regime diagnostic) and D3
(the mean-of-ratios metric restatement).

## Search terms used

1. `upper bound on distillation gain regress teacher outputs on student features conditional expectation oracle student ceiling`
2. `select training subset by farthest point sampling only when diagnostic says model is sample-limited not noise-limited surrogate`
3. `per-sample relative error metric penalizes low-amplitude solutions benchmark energy-weighted alternative PDE evaluation`

## Findings per term

### Term 1 — is the "optimal student = projection of the teacher" bound published? (D1)
Results: *Distillation of Discrete Diffusion by Exact Conditional Distribution
Matching* (arXiv 2512.12889, PDF only); *Learning from Stochastic Teacher
Representations Using Student-Guided Knowledge Distillation*
(https://arxiv.org/html/2504.14307v1); *Oracle Teacher* (arXiv 2111.03664, PDF);
*On-Policy Distillation of Language Models* (arXiv 2306.13649, PDF); an
emergentmind topic page (not a primary source).

The engine synthesised exactly the statement D1 would want — "the optimal student
is the conditional expectation of the teacher's output given the student's input
state", with a Jensen's-inequality MSE bound — but attributed it to no specific
document.

FETCHED https://arxiv.org/html/2504.14307v1 (Aslam, Martinez, Pedersoli, Koerich,
Etemad & Granger, 2025) to test the attribution: the fetch reports the paper
"does not state that the optimal student is the conditional expectation of the
teacher's stochastic output, nor does it present a Jensen's-inequality argument",
and that its justification "is empirical rather than based on such formal
probabilistic arguments". **Attribution refuted** → the conditional-expectation/
Jensen sentence goes on this batch's do-not-cite list.

### Term 2 — FPS *gated by* a limitation diagnostic (D2's composition)
**No usable results** for the gated version. The engine stated plainly that the
results "don't contain specific information about the conditional approach of
selecting training subsets using farthest point sampling only when a diagnostic
indicates the model is sample-limited rather than noise-limited."

What the results DO confirm (returned text, not fetched): FPS "systematically
selects new configurations that maximize their separation from the existing set",
generates "well-distributed training sets and consequently enhance[s] model
performance, with FPS-based models consistently surpassing randomly sampled
models" — sources: FPS in chemical feature space
(https://www.oaepublish.com/articles/jmi.2025.10), *Intelligent Sampling for
Surrogate Modeling* (https://ar5iv.labs.arxiv.org/html/2306.04066), *Curvature
Informed Furthest Point Sampling* (https://arxiv.org/html/2411.16995v1).
Third independent confirmation that the *selector* is standard.

### Term 3 — metric weighting for PDE surrogates (D3)
FETCHED https://arxiv.org/html/2607.00196 — **TRIE: An Evaluation Framework for
Stochastic PDE Surrogates**, Srikishan, Santos, Muralidhar & Young (2026).
Evaluates "whether stochastic PDE surrogates reproduce invariant measures,
provide trustworthy predictive uncertainty, and scale efficiently"; finds
"deterministic neural surrogates fail [at] capturing statistical measures" while
generative models (stochastic interpolants) do better; argues "pointwise-trained
neural surrogates can produce plausible short rollouts while failing to match
long-time statistical structure", i.e. "failures hidden by pointwise evaluation",
and that "for chaotic dissipative systems, long-time fidelity is often
statistical rather than trajectory-wise" — proposing invariant-measure metrics
+ CRPS instead. Crucially for D3, the fetch is explicit: the paper "does *not*
discuss per-sample relative error weighting versus energy/amplitude domination".

This is a direct, citable hit for a DIFFERENT and important point: on
pfc/fisher_kpp/allen_cahn the round scores a **stochastic** map with a
deterministic pointwise metric (ADR r2-0003), which TRIE says measures the
conditional mean rather than the map. It is NOT a citation for the
mean-of-ratios weighting artifact.

Also returned (not fetched): *Beyond Accuracy: EcoL2 Metric for Sustainable
Neural PDE Solvers* (arXiv 2505.12556); *Do Physics Foundation Models Learn
Generalizable Physics? A Bias-Aware Benchmark* (arXiv 2605.29283). An
unattributed engine synthesis about "per-sample-frame relative L₂ … avoids
allowing high-energy trajectories or frames … to dominate the metric" goes on the
do-not-cite list.

## Interpretation

D1's decisive theoretical statement is still unattributed after a dedicated
search; D2's gated composition failed a third independent framing; D3 gains a
strong citation about stochastic-map evaluation but none about mean-of-ratios
weighting. One further refutation turn was run (see `iteration_6.md`) — which
**exceeds this role's 5-iteration cap**; the overrun is recorded there and in
`report.md` rather than concealed.
