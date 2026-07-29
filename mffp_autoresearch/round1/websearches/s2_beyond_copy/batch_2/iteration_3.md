# Iteration 3 — hybrid parametric+nonparametric, and the "beat the lookup" discipline

**WebSearch calls**: 3 | **WebFetch calls**: 3 (2 usable, 1 dead)

## Search rationale

Two remaining task legs. (c) If the brainstormer proposes a hybrid — trained
operator PLUS a nearest-neighbour residual component — is that a published
composition? (d) Is "a trained model must beat a training-free floor" itself a
published comparison discipline, or is it our own reporting convention? The
first matters because iteration 2 showed both halves are published separately;
if the hybrid is also published, direction (iii) collapses too. The second
matters because batch 1's F6 result is only *reportable* if the framing is
defensible; the scouting sweep flagged C7 ("training-free baselines beat
trained surrogates") as external corroboration and I re-fetch its source here
so the citation is grounded in THIS loop.

## Search terms used

1. `hybrid neural network plus k-nearest-neighbor residual correction nonparametric memory augmented regression scientific`
2. `simple nearest neighbor lookup baseline outperforms trained deep learning surrogate benchmark evaluation criticism`
3. `neural PDE surrogate benchmarks weak baselines linear model outperforms evaluation protocol critique operator learning`

## Findings

### Term 1 — hybrid learned + kNN residual

Results list: Twin Neural Network improved k-NN regression
(https://arxiv.org/pdf/2310.00664 / abs https://arxiv.org/abs/2310.00664),
K-nearest-neighbor-enhanced Residual Learning for image restoration
(https://www.sciencedirect.com/science/article/abs/pii/S0952197626000977),
OFTER online time-series pipeline (https://arxiv.org/pdf/2304.03877), random
kernel k-NN regression (https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11246867/).

**DEAD** — https://arxiv.org/pdf/2310.00664 PDF fetch returned undecoded
binary. Refetched the abstract page successfully.

**FETCHED — NNTNNR, "Twin Neural Network Improved k-Nearest Neighbor
Regression"** [cite: https://arxiv.org/abs/2310.00664]. Fetched abstract
content: the twin network is trained to "predict differences between
regression targets rather than the targets themselves"; those predicted
differences are assembled using "the nearest neighbors of the unknown data
point" as anchor points; the algorithm "is shown to outperform both neural
networks and k-nearest neighbor regression on small to medium-sized data
sets".

That is the exact hybrid shape a brainstormer would reach for: retrieved
neighbours as anchors + a learned correction to their targets, averaged, with
a claimed advantage in the SMALL-DATA regime. It is scalar/vector regression,
not operator learning, and the anchors are targets rather than a
same-sample coarse solve.

Search-synthesis text (not fetched): the image-restoration KRF is "a K-nearest
neighbor-enhanced residual learning framework ... to handle diverse image
restoration tasks within a unified model"
(https://www.sciencedirect.com/science/article/abs/pii/S0952197626000977) —
another instance of the same composition in the image domain, alongside the
scouting sweep's RASR.

### Term 2 — "the simple baseline beats the trained model" as a discipline

Results list: The Baseline Manifesto
(https://willieboag.wordpress.com/2019/10/21/the-baseline-manifesto/),
"Revisiting Nearest Neighbor for Tabular Data: A Deep Tabular Baseline Two
Decades Later" (https://openreview.net/forum?id=JytL2MrlLT), SimpleShot
(nearest-neighbour few-shot baseline), "On 'Deep Learning' Misconduct"
(https://arxiv.org/pdf/2211.16350), Test-Time Training on Nearest Neighbors
(https://arxiv.org/html/2305.18466v3).

The framing is a well-established ML-methodology genre (weak-baseline
critiques, NN baselines revisited in tabular and few-shot learning) but
**none of the retrieved items is in PDE / operator learning**. No usable
PDE-specific result from this term.

### Term 3 — the PDE-benchmark version

Results list: REALM realistic multiphysics benchmark
(https://arxiv.org/pdf/2512.18595), PDEBench overview
(https://www.emergentmind.com/topics/pdebench), TRIE stochastic-PDE evaluation
framework (https://arxiv.org/html/2607.00196), Operator Boosting
(https://arxiv.org/html/2606.17460), Small Models Strong Priors
(https://arxiv.org/html/2605.25949v1). The search synthesis states explicitly
that these results "don't explicitly address weak baseline comparisons or
cases where linear models outperform neural approaches" — consistent with
batch 1's three independent passes.

**FETCHED (targeted re-fetch of the scouting sweep's C7 source, so the
citation is grounded in this loop) — "Optimal Linear Baseline Models for
Scientific Machine Learning"** [cite: https://arxiv.org/html/2508.05831]:
- "nonlinearity in the system does not guarantee that nonlinear neural network
  models outperform linear ones";
- "Linear models often capture the essential dynamics remarkably well and ...
  offer a powerful and interpretable baseline";
- "neural network-based methods can and should be evaluated against
  well-understood baselines"; the linear models are "ideal reference points"
  because they "require little to no hyperparameter tuning and admit optimal
  mappings".

## Interpretation

The hybrid (learned correction on retrieved neighbours' targets, averaged) is
published as NNTNNR in ordinary regression and as KRF/RASR in image
restoration — so direction (iii) inherits the same `preempted-but-MF-
composition-open` grade as (i) and (ii), not `novel`. On (d): the *general*
"evaluate against a cheap, well-understood baseline" discipline is published
(2508.05831 states it as a recommendation), but the specific instance we need
— a trained neural operator required to beat a **training-free retrieval
floor** on a multi-fidelity field benchmark — still has no retrieved instance;
it is a reporting convention we can adopt and cite, not a novelty claim.
