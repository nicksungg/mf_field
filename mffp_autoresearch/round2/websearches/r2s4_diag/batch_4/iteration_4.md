# Iteration 4 — ENOUGH on field context; refutation pass 1 (candidate A)

**ENOUGH declared**: field context is sufficient after three turns — I have the
sample-complexity theory for parametric elliptic PDEs (2412.17582), the learning-curve
literature's own verdict on 3-point curves (2103.10948, 2211.14061), the non-nested-design
methods literature (2511.20183), and the retirement/futility spine (2606.26158,
Lachin 2005). Iterations 4–5 spend the remaining budget on §3.3 refutation.

**Tooling**: `WebFetch` disabled; quotations `[bash-fetched]` via urllib. No `/pdf/` URLs.

## Candidate directions this stream-batch may propose

- **A — ifc overfitting-anatomy card**: the un-executed §12.4 mandate. Train the
  condition→HF certifier on the `ifc_poisson` ladder at N_hf ∈ {5, 20, 50}, decompose
  train vs test error at each rung, apply the drift-class rule (in-job paired controls
  only when n_eff/N < 1%), pre-register `unclaimable` as an admissible outcome against
  the certified per-dataset `min_claimable_effect` 0.93770.
- **B — close now**: no B4; the stream's value is the promoted instrument suite and the
  standing bound sentence from B3.

This turn refutes A ("has the overfitting anatomy of a PDE surrogate at single-digit N
already been published?"); iteration 5 refutes the non-nested-attribution component of A
and refutes B.

## Search rationale

Refutation-first: with field context settled, this turn's three terms are chosen to REFUTE
candidate A's novelty from three independent angles — (i) has someone already run an
HF-budget ablation at these sample counts reporting BOTH train and test error, (ii) is
`n_eff` an established diagnostic I would merely be re-implementing, (iii) does a
train/test-gap decomposition exist for operator learning at tiny N. A "no usable results"
on all three is the evidence the verdict needs; a hit on any one preempts the card.

## Search terms used

1. `ablation number of high-fidelity training samples 5 10 20 50 multi-fidelity neural network surrogate Poisson report train and test error`
2. `effective sample size estimate for deep learning training set redundancy diagnostic n_eff generalization`
3. `"train-test gap" decomposition memorization versus generalization operator learning tiny training set PDE parametric surrogate diagnostic study`

## Findings

### Term 1 — an HF-budget ablation reporting BOTH train and test error

Results: https://arxiv.org/pdf/2408.17075 , https://proceedings.mlr.press/v202/wu23p/wu23p.pdf ,
https://arxiv.org/pdf/2503.08408 , https://www.mdpi.com/2076-3417/15/19/10783 , plus three
ScienceDirect/Illinois items (all on the blocked-fetch list). The engine stated outright:
"the search results **do not contain the specific ablation study** you're looking for with
the exact sample sizes (5, 10, 20, 50) and train/test error metrics reported together".

**Fetched 1** — https://arxiv.org/abs/2408.17075 (abstract) and
https://arxiv.org/html/2408.17075v2 (full text, keyword-windowed), Brunel, Balesdent,
Brevault, Le Riche & Sudret, "A survey on multi-fidelity surrogates for simulators with
functional outputs: unified framework and benchmark" (CMAME) [bash-fetched]:
- Abstract: "More than a dozen of existing multi-fidelity surrogates have been implemented
  under the unified framework and evaluated on a set of benchmark problems … **most
  multi-fidelity surrogates outperform their tested single-fidelity counterparts under the
  considered settings. But no particular surrogate is performing better on every test
  case.** Therefore, the selection of a surrogate should consider … **the correlation
  between the low- and high-fidelity simulators, the size of the training set**, the local
  nonlinear variations in the residual fields, and the size of the training datasets."
- Full text, on pairing (this is the decisive sentence for A's non-nested component):
  "This approach can be achieved either **with a set of correspondences between some input
  samples from the distinct datasets [34], or without [35]**. In the context of this paper,
  a set of correspondence means that some snapshots have been obtained **for the same input
  variables values for different fidelity levels** … with n_c the number of common input
  variable vectors".
- Full text, on the HF-budget constraint: "if the computational cost of the high-fidelity
  simulator is especially high, **a small number of high-fidelity snapshots limits the
  number of exploitable low-fidelity snapshots. Hence, the surrogate may not take full
  advantage of the multi-fidelity context.**"
- Appendix D is titled "**Decomposition of the normed RMSE into normed DR and intermediate
  surrogate modeling RMSE**" — an error *decomposition* exists in this literature, but it
  splits dimension-reduction error from intermediate-surrogate error, **not** train from
  test.
- Explicit **negatives** from keyword probes over the full text: "learning curve",
  "overfit", "training set sizes", "high-fidelity training set", "number of high-fidelity
  training" — **all NOT FOUND**.

*Reading*: this is the closest thing to the proposed card that exists — an MF benchmark
over **functional (field) outputs** that varies training-set size and reports a per-source
error decomposition — and it contains **no train/test gap analysis and no overfitting
vocabulary at all**. It also gives the citable statement that the ifc regime (tiny HF
budget throttling the usable LF) is a recognised failure mode of MF surrogates.

### Term 2 — effective sample size / n_eff as a diagnostic

Results: https://arxiv.org/pdf/2512.14963 , https://arxiv.org/pdf/1606.04232 (DCNNs on a
Diet), https://pmc.ncbi.nlm.nih.gov/articles/PMC10659445/ , https://keras.io/examples/keras_recipes/sample_size_estimate/ ,
plus ScienceDirect/NCBI items on the blocked list. The engine confirmed: "the specific term
'n_eff' (effective sample size) you mentioned … **didn't appear prominently** in these
particular results", and what the literature offers instead is *redundancy pruning* ("a
point is deemed redundant if removing it degrades test accuracy by less than 10%").
**No usable results** for an n_eff-style diagnostic in this sense. Nothing fetched — every
returned primary item is about training-set *pruning/selection*, which is batch 3's
already-`preempted` D2 territory, not gap anatomy.

### Term 3 — train/test gap decomposition in operator learning at tiny N

Results (two engine passes): https://arxiv.org/pdf/2605.10277 (generalization error bounds,
Picard-type operator learning, **parabolic** PDEs), https://arxiv.org/html/2602.00884v1 ,
https://arxiv.org/pdf/2509.06154 (already a batch-3 citation), https://arxiv.org/html/2511.09729 ,
https://arxiv.org/pdf/2605.30112 ; second pass returned only off-domain
memorization/generalization work (diffusion models, NLP fine-tuning, grokking) plus
tertiary encyclopedia pages (bohrium.com, emergentmind.com).
The engine's closing statement: the results "**don't reveal a specific diagnostic study
focusing on operator learning for PDEs with tiny training sets** as described in your
query". Nothing fetched: the generalization-gap prose the engine surfaced is from
aggregator pages (bohrium, emergentmind) and is **not citable**; the one on-domain primary
(2605.10277) is asymptotic bound theory for a different PDE class (parabolic, not the
elliptic Poisson of the ifc ladder) and would not be a preemption even if fetched.

## Interpretation

Refutation pass 1 **fails to refute A's core**: the nearest neighbour is a CMAME-level MF
benchmark over functional outputs that sweeps training-set size and decomposes error by
*source* (DR vs intermediate surrogate) but never by *train vs test*, and whose full text
contains no overfitting vocabulary. What it DOES preempt is any claim to novelty in
"pairing matters" — the paired-vs-unpaired ("set of correspondences") distinction is
explicit and standard there, so the card must cite it rather than present the ifc ladder's
non-nestedness as a discovery. The n_eff component is unsupported by prior art in the
diagnostic sense and should be demoted to a descriptive statistic.
