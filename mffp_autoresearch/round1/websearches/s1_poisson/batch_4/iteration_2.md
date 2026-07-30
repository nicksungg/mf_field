# Iteration 2 — step-count vs epoch-count confounds; matched-control practice

## Search rationale

Batch-4 scope direction 2. B3-T1-F2's confound is *exactly* an
epoch-matched-but-not-step-matched comparison: `allpairs` runs 18 gradient
steps/epoch vs `self_only`'s 11 at bs=16 (1.64x), because duplication inflates
the row count. I need (a) a published, citable articulation that epoch-matched
comparisons conflate algorithm with compute, and (b) the canonical construction
of the matched control (scale the other arm's epochs, and/or read the
longer-running arm off at the matching update count) — so the B4 card can cite
the recipe rather than invent it. Terms 1 and 2 target the general ML
methodology; term 3 checks whether the neural-operator / scientific-ML
literature has its own statement of the same rule (closer to home = better
citation for this project).

## Search terms used

1. `compute-matched versus epoch-matched comparison confound number of gradient steps data selection ablation fair comparison`
2. `data pruning subset selection baseline must control for number of training steps equal iterations not equal epochs`
3. `neural operator training ablation matched number of optimization steps rather than epochs when dataset size differs`

## Findings

### Term 1 — the explicit statement (BEST HIT OF THE BATCH for direction 2)

Top-5 returns: Baseline-Free Policy Optimization for Neural Combinatorial
Optimization (https://arxiv.org/pdf/2606.10321); Bilevel Graph Structure
Learning, Revisited (https://arxiv.org/pdf/2605.07577); Flow Matching Policy
Gradients (https://flowreinforce.github.io/); Condensing Graphs via One-Step
Gradient Matching (https://arxiv.org/pdf/2206.07746); A Negative Result on
Gradient Matching for Selective Backprop (https://arxiv.org/pdf/2312.05021).

**FETCHED** https://arxiv.org/abs/2606.10321 — abstract-level quote returned:
"at matched gradient updates, GRPO achieves solution quality within 2% of
POMO". (The abs page does not carry the methodology; second fetch below.)

**FETCHED** https://arxiv.org/html/2606.10321v1 — the methodology quotes:

> "However, this comparison conflates algorithmic quality with compute: GRPO
> performs 8x more gradient updates per epoch than REINFORCE and POMO."

> "GRPO, PPO, and P3O perform K inner PPO epochs per training step, each
> iterating over mini-batches, yielding approximately 88 gradient updates per
> outer batch" ... "~312K gradient updates for GRPO versus ~39K for REINFORCE
> and POMO, an 8x ratio."

and the construction of the matched controls: they train "POMO and REINFORCE
for 800 epochs to match GRPO's 312K updates at 100 epochs", and additionally
read "GRPO performance at epoch 12 to match the baseline methods' 39K update
budget at 100 epochs".

This is a near-exact structural analogue of B4: same confound (updates/epoch
differ because of a data-schedule choice), same two-sided remedy (scale the
short arm's epochs UP; read the long arm off EARLY). It also demonstrates the
outcome that matters most to us: **the epoch-matched ranking reversed** — GRPO
"achieved the lowest cost on all four benchmarks" epoch-matched, but
update-matched "POMO proved most efficient per gradient update" (search-return
summary of the same paper). An epoch-matched ranking flipping under
step-matching is a *documented* phenomenon, not a hypothetical.

### Term 2 — data-pruning practice

Top-5: Dataset Pruning (https://openreview.net/pdf?id=4wZiAXD29TQ, OpenReview =
known dead route, not fetched); Less is More: Data Pruning for Faster
Adversarial Training (https://arxiv.org/pdf/2302.12366); Spike-aware Data
Pruning (https://arxiv.org/pdf/2510.04098); Accelerating Deep Learning with
Dynamic Data Pruning (https://arxiv.org/pdf/2111.12621); Data Pruning
Simplified (https://celerdata.com/glossary/data-pruning-simplified-a-practical-guide).

Search-return only (no fetch — every top hit was an `arxiv.org/pdf` or
OpenReview URL, both on batch-3's dead-route list): the returned synthesis
states the methodological point ("a smaller subset per epoch means fewer
iterations per epoch than the full dataset baseline"; controlling total
training iterations rather than epochs "ensures a fairer comparison") but I
could not attach it to a quotable fetched sentence. **Recorded as
search-return, not as a citation.** The dedup-side version of the same point IS
fetched, in iteration_1.md (https://arxiv.org/abs/2107.06499,
https://arxiv.org/html/2407.06654 — both tie dedup to a change in required
train steps).

### Term 3 — scientific-ML / neural-operator version

**No usable results.** Nothing in the top-9 states a step-matching rule for
operator learning. The one lead, PENCO (https://arxiv.org/pdf/2512.04863,
search-return claimed a "Fixed optimization budget" safeguard), was **FETCHED**
at https://arxiv.org/abs/2512.04863 and the fetch found no such sentence —
the search summariser appears to have hallucinated the safeguard from the
abstract. Logged as a dead end and a summariser-reliability data point
consistent with batch 3's warning.

## Interpretation

Direction 2 is **preempted as ML-general with an unusually clean citation**:
https://arxiv.org/html/2606.10321v1 states the confound verbatim ("conflates
algorithmic quality with compute", 8x updates/epoch) and gives both matched
controls B4 plans to run. No scientific-ML source states the rule for operator
learning, so B4's contribution is the in-repo *measurement*, not the method.
