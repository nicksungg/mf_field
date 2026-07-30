# Iteration 1 — duplication-as-reweighting, and dedup effects

## Search rationale

Batch-4 scope directions 1 and 3. B3-T1-F2 asserts, as an in-repo measurement,
that `allpairs` = a per-level replication schedule and that "under `per_level`
normalization row share IS effective loss weight". Before the brainstormer
writes that into a card, I need the *published* form of the claim
"exact-duplicate replication acts as loss reweighting" — ideally with its known
caveats — plus the cleanest published account of what removing duplicates does
(the LLM dedup literature). Terms chosen to hit the formal statement (term 1),
the empirical dedup literature (term 2), and the exact technical name for the
equivalence surfaced by term 1 (term 3).

## Search terms used

1. `exact duplicate training examples equivalent to loss reweighting SGD importance weighting duplication`
2. `deduplicating training data language models duplicates memorization effect on training distribution weighting`
3. `"importance duplication" weighted empirical risk duplicating data points approximation weights`

## Findings

### Term 1 — duplication == importance weighting

Top-5 returns: Dynamic Loss-Based Sample Reweighting for LLM Pretraining
(https://arxiv.org/html/2502.06733v1); SoftDedup
(https://arxiv.org/html/2407.06654); Learning to Reweight Examples
(https://arxiv.org/pdf/1803.09050); Sampling and Loss Weights in Multi-Domain
Training (https://arxiv.org/pdf/2511.06913); Importance Weighted Generative
Networks (https://arxiv.org/pdf/1806.02512).

The productive hit is **Importance Weighted Generative Networks**, which names
the construction "importance duplication".

**FETCHED** https://ar5iv.labs.arxiv.org/html/1806.02512 (ar5iv route, per the
batch-3 rule for pre-2024 arXiv). Exact quotes returned by the fetch:

> "We can obtain an approximation to this method by including ⌈1/M(x_i)⌉
> duplicates of data point x_i in our training set."

> "Importance duplication obviously introduces discretization errors, and if
> our estimator is a U-statistic it will introduce bias (e.g. in the MMD
> example, if two or more copies of the data point x_i appear in a minibatch,
> then k(x_i,x_i) will appear in the first term of Equation 2)."

and the authors note that "even though this approach lacks theoretical
guarantees it provides generally good performance".

So the equivalence *is* published, is named, and is published **as an
approximation with named failure modes**, not as an identity. Two caveats
transfer directly to B4: (i) discretization — you can only realize integer
weight ratios by duplication (our ×1/×2/×3/×4 is exactly an integer schedule,
so this caveat is benign here); (ii) **duplicates co-occurring in a minibatch**
change the estimator, which for plain per-sample MSE is harmless in expectation
but is not nothing for the gradient *variance* at bs=16 with 5 HF rows
replicated ×4.

### Term 2 — dedup literature

Top-5: Deduplicating Training Data Makes Language Models Better
(https://arxiv.org/abs/2107.06499); ACL version
(https://aclanthology.org/2022.acl-long.577/); Deduplicating Training Data
Mitigates Privacy Risks (https://arxiv.org/pdf/2202.06539); Enhancing Data
Quality through Simple De-duplication (https://arxiv.org/pdf/2410.03545);
Undesirable Memorization survey (https://arxiv.org/pdf/2410.02650).

**FETCHED** https://arxiv.org/abs/2107.06499 — abstract states deduplication
"allows us to train models that emit memorized text ten times less frequently"
and that deduplicated models "require fewer train steps to achieve the same or
better accuracy". Search-return (not fetched) adds the superlinear regeneration
result (a sequence present 10× is emitted ~1000× more often), i.e. duplicate
count has a *nonlinear* effect on the learned distribution, not merely a linear
weight effect.

**FETCHED** https://arxiv.org/html/2407.06654 (SoftDedup): the paper explicitly
frames the two operations as alternatives — "Hard deduplication identifies and
removes duplicate samples. Soft deduplication identifies samples with high
commonness, decreasing their sampling weight during training." — and reports
"models achieve equivalent baselines in perplexity with a reduction of 26% to
39% in the number of required training steps". Notably the fetch found **no**
sentence in SoftDedup stating "duplication == implicit weighting" as a formal
claim; the framing there is empirical.

### Term 3 — the formal name

Confirms term 1: "importance duplication" is the term of art; nearest formal
sibling is Weighted ERM (https://arxiv.org/abs/2002.05145, search-return only).
No source found that states duplication==weighting as an *exact* identity for
SGD; the published statement is an approximation with caveats.

## Interpretation

Directions 1 and 3 are **preempted as ML-general**: the duplication-as-weighting
construction is published and named ("importance duplication",
https://ar5iv.labs.arxiv.org/html/1806.02512), and dedup's effect on required
train steps is published (https://arxiv.org/abs/2107.06499,
https://arxiv.org/html/2407.06654). Crucially for B4, **both fetched dedup
sources tie deduplication to a change in the number of training steps** — which
is exactly the confound B4 must control, and confirms that a dedup arm without
a step-matched partner would be uninterpretable.
