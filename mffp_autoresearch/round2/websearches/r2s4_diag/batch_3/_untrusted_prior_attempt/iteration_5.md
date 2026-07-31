# Iteration 5 — refutation pass 2 (CAP: 5/5 iterations used) + full prior-art verdict

**Cap note**: this is iteration 5 of a maximum 5. Three terms this turn, as in every turn;
no truncations anywhere in the loop.

## Search rationale

Last chance to refute. (a) One more independent framing for D1's *operation* — "regress the
oracle's predictions on the available features to find the achievable ceiling" stated in
generic ML vocabulary rather than LUPI vocabulary. (b) Second independent framing for D3 —
nearest-neighbour distance in the *design space* as a predictor of surrogate error/coverage
(the d_min half of B2's rule). (c) Second independent framing for D4 — the mean-of-ratios
metric artifact, stated as a benchmark-ranking problem rather than a norm-sensitivity one.

## Search terms used

1. `regress oracle predictions on available features to find achievable ceiling feature ablation upper bound predictable component`
2. `nearest neighbour distance in design space predicts surrogate extrapolation error coverage criterion high dimensional parameter space`
3. `averaging per-sample normalized error overweights low-energy samples benchmark ranking artifact scientific machine learning`

## Findings

### Term 1 — "regress the oracle on available features" in generic vocabulary

**No usable results.** Everything returned was off-domain (LLM reasoning-accuracy
prediction https://arxiv.org/pdf/2604.16931, neural predictivity from LMs
https://arxiv.org/pdf/2606.26880, mutation analysis, gaze prediction). The search engine's
synthesis described the generic vocabulary that exists — an oracle "trained on a pooled
dataset containing all composition levels... establishes an upper bound", and
feature-ablation via "feature zeroing... residualization, and projection removal (which
remove variance associated with candidate quantities while preserving train-only fitting)"
— but attributed to no fetchable source in this domain (**SNIPPET, do-not-cite**). This is
the **third** independent framing to fail for D1's specific operation (after iteration 1
terms 2 and 3).

### Term 2 — nearest-neighbour distance in design space as a coverage/error diagnostic

- https://besjournals.onlinelibrary.wiley.com/doi/10.1111/2041-210X.13851 — Mila et al. 2022,
  "Nearest neighbour distance matching Leave-One-Out Cross-Validation (NNDM) for map
  validation", Methods in Ecology and Evolution. **FETCH FAILED (HTTP 402 Payment
  Required)** — title/venue/URL only. Named, published use of *nearest-neighbour distance
  distributions in predictor space* to decide whether a validation design matches the
  prediction task: the closest published relative of B2's d_min statistic found in the whole
  loop, from spatial statistics rather than SciML.
- https://www.sciencedirect.com/science/article/abs/pii/S009830049800020X (spatial coverage
  designs), https://pmc.ncbi.nlm.nih.gov/articles/PMC10078774/ (design-based properties of
  the NN spatial interpolator, incl. consistency conditions) — search results only; same
  spatial-statistics lineage.
- Nothing in the SciML/parametric-surrogate literature was returned that uses a
  nearest-train-neighbour distance to forecast whether more training rows will help. D3's
  operational half remains uncited in-domain after **two** dedicated searches (iteration 2
  term 2, this term).

### Term 3 — mean-of-ratios vs energy-pooled as a benchmark-ranking artifact

**No usable results**, second independent failure (iteration 3 term 1 was the first). Hits
concerned aggregate-metric uncertainty (https://arxiv.org/html/2501.04234v1), per-target
rescaling in a spectroscopy benchmark (https://arxiv.org/pdf/2605.02003), and label-error
destabilisation of rankings (https://arxiv.org/pdf/2103.14749). The search engine stated:
"the search results don't specifically address the particular artifact you're asking
about". SAIBench (https://arxiv.org/pdf/2311.17869) and the NeurIPS SciML benchmark
(https://papers.neurips.cc/paper_files/paper/2022/file/0a9747136d411fb83f0cf81820d44afb-Paper-Datasets_and_Benchmarks.pdf)
are the nearest neighbours by topic; search results only, neither fetched.

## PRIOR-ART VERDICT (full text)

### D1 — teacher-projection diagnostic (B2 Option A; the analyst-recommended B3)

*Proposal shape*: train T0 (condition-only) and I1 (LF-teacher input) at matched budget,
dump per-arm test predictions, then fit an out-of-fold condition -> prediction map to I1's
own predictions and score `proj(I1)` against T0 to decide whether the certified information
gap is condition-expressible at all.

**Verdict: `preempted-but-MF-composition-open (cite)`.**

Preempted parts, all with fetched or search-returned sources from this loop:
- The *setting* — a teacher consuming train-only privileged inputs distilled into a student
  restricted to deployment-feasible inputs, for engineering surrogates — is published under
  the name **training-inference data asymmetry**:
  https://www.sciencedirect.com/science/article/abs/pii/S0952197625034293 (search result;
  fetch 403, all numbers do-not-cite) and, in the LM domain and fetched,
  https://arxiv.org/abs/2602.04942 (pi-Distill / OPSD).
- The *theory* is positive-result-oriented and supplies no ceiling:
  https://arxiv.org/abs/1903.03694 (FETCHED) proves teacher-student agreement shrinks the
  search space, and the fetch confirmed it states no failure/bound condition.
- The *gap decomposition* B3 wants is published for LLM routing:
  https://arxiv.org/abs/2607.03436 (FETCHED) — "the expected oracle decomposes as
  O^exp = O^repro + Delta, into reproducible single-commit headroom O^repro and a
  non-negative single-commit selection floor Delta", with a **recoverability asymmetry** and
  an explicit warning about "non-identifiability at k=1".

What remains open (state this, not novelty): no fetched source computes the
**condition-measurable projection of an LF-consuming field teacher** and reports it as the
transferable ceiling; three independent framings failed to find the operation at all. And
2607.03436's recoverable/irreducible split has never been instantiated where the irreducible
part is an **unrecorded random initial condition** and the output is a **field** scored in
copy-LF skill units.

Pre-registration material found this loop: https://arxiv.org/html/2601.22654v1 (FETCHED)
runs a **factorial IC x parameter test design** (50 x 50 = 2500 pairs, 50x50 error matrix,
row/column variance decomposition) and finds the **opposite** polarity to ADR r2-0003 —
"approximation difficulty varies primarily with the conditioning vector (i.e., the induced
PDE regime), rather than with the initial conditions". B3 should pre-register against that
counter-hypothesis rather than assume the IC dominates.

### D2 — coverage-greedy fit-fold selection at fixed N (B2 Option B, support repair on cahn_hilliard)

**Verdict: `preempted (cite)` at the mechanism level; composition open as a diagnostic.**

- https://arxiv.org/abs/2012.03541 (FETCHED) — "Space-Filling Subset Selection for an
  Electric Battery Model" selects, from an existing non-uniformly-sampled pool, "those
  dynamic data points that fill the input space of the nonlinear model more homogeneously",
  benchmarked against "random subset sampling and using all available data points", and
  reports higher accuracy than random sampling. That is Option B's mechanism, published.
- The greedy is standard k-center / farthest-point (snippet-level wording, do-not-cite;
  cite 2012.03541).
- The active-learning literature (https://arxiv.org/pdf/2606.09949,
  https://www.sciencedirect.com/science/article/pii/S004578252030760X) solves the adjacent
  problem by generating **new** solves — forbidden here by immutable §5.11, which is exactly
  why re-selection is the only lever and is worth stating.

Open: no source found uses coverage-greedy re-selection as a **diagnostic that separates a
support-limited dataset from an information-limited one** (explicit search-engine
non-result), nor pairs it with a training-free go/no-go predictor.

### D3 — training-free regime rule: identifiability x support (d_min) predicts the learning-curve regime

**Verdict: `preempted-but-MF-composition-open (cite)`.**

- General principle published: training-free, nearest-neighbour-based geometric statistics
  predict learning difficulty — https://arxiv.org/abs/2104.08894 (FETCHED): "low dimensional
  datasets are easier for neural networks to learn, and models solving these tasks generalize
  better from training to test data".
- Learning-curve fitting/extrapolation is a mature field —
  https://arxiv.org/abs/2103.10948 (FETCHED, Viering & Loog) — which also **warns against
  B2's own 3-point power-law fit**: the review "expresses... more scepticism towards the idea
  that it has been proven that power laws often provide accurate learning curve models", and
  documents "learning curves that are ill-behaved, showing worse learning performance with
  more training data" (the citation B2's helmholtz kNN degradation 8.69 -> 20.59 has been
  missing). Companion survey https://link.springer.com/article/10.1007/s10994-024-06619-7
  is FETCH-BLOCKED (303 -> idp.springer.com).
- The d_min half's nearest published relative is spatial statistics, not SciML: NNDM
  https://besjournals.onlinelibrary.wiley.com/doi/10.1111/2041-210X.13851 (fetch 402).

Open: the *conditional* form of the rule — LOW identifiability + SMALL d_min = information-
limited (more rows cannot help) vs REAL identifiability + d_min >> 1 = sample-limited (fix is
coverage) — as a **pre-training go/no-go for spending GPU**, in a PDE condition space, was
not found in two dedicated searches.

### D4 — energy-pooled restatement of the mean-of-ratios metric (B2 cross-stream item (b))

**Verdict: `novel` (weak sense — nothing close found in two independent framings), but it is a
reporting item, not an experiment.**

Nearest neighbours: (i) in-repo `docs/reports/MF_Sharp_HighFreq_Report.md` §0.3 — MSE + rel-L2
structurally prefer blur, "the SURF metric panel matters as much as any architecture change";
(ii) https://arxiv.org/html/2607.00196v1 (TRIE, FETCHED), which rejects pointwise scoring for
stochastic PDE surrogates outright — "the forcing realization is not observed at forecast
time, a surrogate cannot track a single reference trajectory indefinitely"; "pointwise-trained
neural surrogates fail" — and scores invariant measures/spectra/CRPS instead. TRIE is the
strongest external support for the claim that our panel's stochastic datasets are being scored
with an instrument the literature considers inappropriate. program.md §5.4 makes nRMSE
immutable, so this stays interpretive in-round.

## Interpretation

D1 survives as the strongest B3 card: its setting and its gap-decomposition are both
published (so cite, don't claim), but its actual operation failed three refutation framings
and its predicted outcome now has a citable counter-hypothesis to pre-register against. D2 is
mechanically preempted and should be sold as a diagnostic. D3 and D4 are report-level items
with, respectively, a strong general-ML precedent and no precedent at all.
