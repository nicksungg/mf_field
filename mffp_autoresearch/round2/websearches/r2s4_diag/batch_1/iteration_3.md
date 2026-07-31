# Iteration 3 — `r2s4_diag` batch 1

## Search rationale

r2s4's third owned question is **overfitting anatomy at N_hf ∈ {5, 20, 50} and
N = 400** with train/test gap decomposition and effective sample counts
(program.md §12.4; the drift-class rule needs an n_eff estimate). Open question 4
from `summary_so_far.md`. I need to know whether (a) tiny-N operator-learning
generalization gaps have a published diagnostic vocabulary, (b) there is a
data-scaling-law expectation to compare our learning curve against, and (c)
effective-sample-size machinery exists that I can point the brainstormer at
instead of inventing one.

## Search terms used

1. `neural operator few training samples overfitting train-test generalization gap decomposition PDE surrogate diagnostic`
2. `operator learning data scaling law number of training samples error curve sample complexity FNO DeepONet`
3. `effective sample size correlated training samples deep learning diagnostic redundancy dataset`

## Findings per term

### Term 1 — tiny-N overfitting / generalization gap for neural operators

Top results: ReBaNO — Reduced Basis Neural Operator Mitigating Generalization
Gaps (https://arxiv.org/pdf/2509.09611), Learning Data-Efficient and
Generalizable Neural Operators via Fundamental Physics Knowledge
(https://arxiv.org/html/2602.15184v1), From Theory to Application: A Practical
Introduction to Neural Operators in Scientific Computing
(https://arxiv.org/html/2503.05598 ; https://doi.org/10.3390/math14132421),
Improved Generalization with Deep Neural Operators
(https://arxiv.org/pdf/2301.06701), Solver-Integrated Adversarial Training of
Neural Operators (https://arxiv.org/pdf/2510.18989). Recurring framing in the
returned summaries: generalization is defined as expected-vs-empirical loss and
should be "clearly separat[ed] ... from robustness"; small paired datasets bias
the operator toward the few configurations seen; the field's answer is
overwhelmingly *remedies* (physics losses, reduced bases, multi-level training,
residual-based error correction), not *diagnostics*. No fetch performed for this
term — the returned summaries were remedy-oriented and none named a train/test
gap decomposition protocol. Recorded as: no usable diagnostic-methodology result.

### Term 2 — data-scaling laws for operator learning

Top results: The Cost-Accuracy Trade-Off In Operator Learning With Neural
Networks (https://arxiv.org/abs/2203.13181), Operator Learning: A Statistical
Perspective (https://arxiv.org/abs/2504.03503), Neural Scaling Laws of Deep ReLU
and Deep Operator Network (https://arxiv.org/pdf/2410.00357), SPDEBench
(https://arxiv.org/pdf/2505.18511), Convolutional Neural Operators
(https://arxiv.org/pdf/2302.01178), The Cost-Accuracy Trade-Off ... and Size
Lowerbounds for Deep Operator Networks (https://arxiv.org/pdf/2308.06338).

The search-result summary asserts power-law error curves `E = (N0/N)^r`, an FNO
Navier–Stokes rate `r = 0.28`, ~60.1K samples for 1% error, and (from SPDEBench)
that for stochastic PDEs "performance improves only marginally with more
training data ... less than a factor of two when increasing from 1,000 to 10,000
samples, suggesting that the bottleneck lies in representational capacity rather
than data quantity."

**Fetched — de Hoop, Huang, Qian & Stuart, "The Cost-Accuracy Trade-Off In
Operator Learning With Neural Networks" (https://arxiv.org/abs/2203.13181)**:
title/authors confirmed; the fetch saw only the abstract ("a careful numerical
study" of the cost-accuracy trade-off, comparing "a variety of different neural
network architectures for operator approximation") and **could not confirm** the
power-law fits, the r = 0.28 rate, or the 60.1K figure. **I therefore do NOT
cite those numbers as established** — they are search-snippet-level only and
must be re-verified before any card quotes them.

**Fetched — Subedi & Tewari, "Operator Learning: A Statistical Perspective"
(https://arxiv.org/abs/2504.03503)**: title/authors confirmed; abstract
formalizes operator learning as "a function-to-function regression problem" and
flags "active data collection and the development of rigorous uncertainty
quantification frameworks" as future directions. Sample-complexity/minimax/error-
decomposition details are in the body, not the abstract — not confirmed here.

### Term 3 — effective sample size for correlated training data

Top results: influence of training sample size on DL soil-property models
(https://soil.copernicus.org/articles/6/565/2020/), impact of training sample
size on DL organ auto-segmentation
(https://iopscience.iop.org/article/10.1088/1361-6560/ac2206), optimal positive
sample size for DL (https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11431354/),
sample determination for DL electromagnetic tomography
(https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11054014/). Content is
applied-domain saturating learning curves plus one Pearson-correlation-based
sample-set optimization; the ESS notion returned is the standard MCMC-style
"number of independent samples achieving the same variance as the correlated
samples". **No usable PDE-surrogate-specific effective-sample-size diagnostic.**
No fetch performed — none of the hits are in our domain.

## Interpretation

Tiny-N operator learning is a heavily worked *remedy* literature with almost no
*diagnostic* literature: I found no published train/test gap decomposition
protocol for neural operators and no domain-specific n_eff estimator. Data-scaling
power laws exist as a comparison frame but I could not verify the specific rates
from a fetched source, so the brainstormer must not quote them. Next iteration:
the mandatory targeted refutation searches for the three candidate directions.
