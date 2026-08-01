# Iteration 1 — few-shot sample-complexity field context

**Tooling note**: `WebFetch` is DISABLED in this environment (every call returns a
context-mode redirect error, and the redirect target MCP tools are not in this
subagent's tool list). Per the orchestrator's instruction I routed around with
`Bash` + `urllib` GETs (script at
`scratchpad/fetch.py`, UA-spoofed, HTML→text, keyword-windowed). **Every quotation
below is labelled `[bash-fetched]` with the exact URL.** Batch 3's process rule is
observed: no arXiv `/pdf/` URLs are fetched; only `/abs/` and `/html/`.

## Search rationale

B3 part 7 leaves exactly one live candidate: overfitting anatomy at N_hf ∈ {5, 20, 50}
on the ifc ladder. Before any novelty verdict I need the field context: does published
work characterise the train/test gap for PDE surrogates / operator learning at
*extreme* few-shot (single-digit N), and are learning curves at that N even
well-behaved? Three orthogonal framings: sample-complexity/learning-curve, gap
decomposition, and the double-descent/interpolation-threshold literature (N_hf = 5 with
an FNO decoder is deep in the over-parameterised regime, where a peak near the
interpolation threshold would confound a train/test-gap reading).

## Search terms used

1. `neural operator sample complexity extremely small training set 5 to 50 samples learning curve PDE surrogate`
2. `train test generalization gap decomposition few-shot PDE surrogate overfitting anatomy data scarce operator learning`
3. `double descent neural operator scientific machine learning small data regime function regression`

## Findings

### Term 1 — sample complexity / learning curves for neural operators

Top results: https://arxiv.org/html/2604.20061v1 (already a binding batch-1/2 citation),
https://arxiv.org/pdf/2512.08444 , https://arxiv.org/pdf/2312.14688 ,
https://arxiv.org/pdf/2412.17582 , https://arxiv.org/html/2605.08938 ,
https://arxiv.org/html/2606.29440 .

The search engine's own synthesis stated that neural operators "typically require a
relatively small amount of training data, in the order of a thousand input-output
pairs", and that "the rate of convergence of neural operators with respect to the
number of training samples evolves in two regimes" — and then stated outright that the
results "don't specifically address the extremely small regime of 5-50 samples".

**Fetched 1** — https://arxiv.org/abs/2412.17582 , Reinhardt, Wang & Zech,
"Statistical Learning Theory for Neural Operators" (submitted 23 Dec 2024)
[bash-fetched]: "given a map $G_0:\mathcal X\to\mathcal Y$ between two separable Hilbert
spaces, we analyze the problem of recovering $G_0$ from $n\in\mathbb N$ noisy
input-output pairs"; "We provide general convergence results for least-squares-type
empirical risk minimizers over compact regression classes … in terms of their
approximation properties and metric entropy bounds, which are derived using empirical
process techniques. This generalizes classical results from finite-dimensional
nonparametric regression to an infinite-dimensional setting."; "Assuming $G_0$ to be
holomorphic, we prove algebraic (in the sample size $n$) convergence rates in this
setting, thereby overcoming the curse of dimensionality"; the prototypical example is
"the learning of the non-linear solution operator to a parametric elliptic partial
differential equation".
*Reading*: this is the closest theory to the ifc ladder (parametric elliptic PDE =
Poisson), and it is asymptotic-in-$n$ rate theory. It gives no finite-$n$ statement at
$n=5$; it reinforces batch 1/2's binding constraint (arXiv:2410.23440) that no
ceiling/information-gap claim is defensible at N_hf = 5.

**Fetched 2** — https://arxiv.org/abs/2512.08444 , Hauptmann & Öktem, "Learned iterative
networks: An operator learning perspective" (v2, 28 Jun 2026) [bash-fetched]: abstract
is a survey of unrolled reconstruction operators for computational imaging — the
"two regimes" sentence the engine attributed to it is **not present in the fetched
abstract**. Recorded as a NON-attribution: do not cite the two-regime claim to this
paper.

### Term 2 — train/test gap decomposition at few-shot

Top results: https://arxiv.org/html/2508.01211 , https://www.emergentmind.com/topics/generalization-gap ,
https://arxiv.org/html/2505.24190 , https://arxiv.org/pdf/2511.09729 ,
https://dl.acm.org/doi/fullHtml/10.1145/3386252 .

**Fetched 3** — https://arxiv.org/abs/2508.01211 , Li & Zhe, "Multi-Operator Few-Shot
Learning for Generalization Across PDE Families" (2 Aug 2025) [bash-fetched]: "existing
neural operator methods require abundant training data for each specific PDE and lack
the ability to generalize across PDE families. In this work, we propose MOFS: a unified
multimodal framework for multi-operator few-shot learning, which aims to generalize to
unseen PDE operators using only a few demonstration examples."
*Reading*: "few-shot" in the operator-learning literature means **few shots of a NEW
operator after pretraining on many others** — a transfer setting. That is structurally
different from this round's regime (one PDE family, 5 HF samples, no cross-family
pretraining corpus). It is a *method* paper, not a gap-anatomy paper. The engine's
"generalization gap … decomposed into intrinsic error (finite-sample effects and
overfitting) and external error (distribution shift)" sentence came from
emergentmind.com, an aggregator page, not from a primary source — **not citable**.

### Term 3 — double descent in the small-data regime

Top results were all tertiary (Wikipedia, mlu-explain, DataCamp, Data Science Dojo,
emergentmind, alignmentforum) plus one off-domain primary
(https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10895367/ , graph convolution networks).
The engine confirmed: "they don't specifically address neural operators for scientific
machine learning or function regression in small data regimes". **No usable results**
for double descent in operator learning / field regression. Nothing fetched (the
tertiary pages carry no attributable claim, and PMC has 403'd in prior batches).

## Interpretation

The extreme-few-shot regime this card would probe (N_hf ∈ {5, 20, 50}, one PDE family,
no pretraining corpus) is **not** what "few-shot operator learning" means in the
literature — that term is reserved for cross-family transfer. The nearest primary work
is asymptotic sample-complexity theory for exactly our PDE class (parametric elliptic),
which by construction says nothing at n = 5. This is early evidence that an ifc-ladder
overfitting-anatomy measurement is under-served by prior art, but I have not yet
searched the two decisive framings: unpaired MF ladders, and criterion-retirement /
stopping-rule methodology.
