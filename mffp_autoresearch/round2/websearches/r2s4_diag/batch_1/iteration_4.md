# Iteration 4 — `r2s4_diag` batch 1 (refutation pass 1 of 2)

## Search rationale

Field context is now sufficient (iterations 1–3). **ENOUGH** on general field
survey — reason: three iterations produced consistent coverage of floors,
seed-variance practice, LUPI framing, and tiny-N remedies, and iteration 3's
term-3 returned nothing in-domain. Remaining budget goes to §3.3 refutation.

The three candidate directions r2s4-B1/B2 will propose (from program.md §12.4,
which pre-directs B1):

- **D1 — Floor + spread certification**: reproduce the training-free floor panel
  (NN-in-condition / train-mean / zero) and train ONE minimal condition→HF model
  at smoke tier over seeds {0,1,2} to certify a per-dataset seed spread that
  becomes the round's minimum-claimable-effect threshold, replacing the
  provisional `state/noise_floor.json`.
- **D2 — Value-of-LF accounting**: matched architecture, matched budget, ±
  LF-training-signal arms across the 6-dataset panel, gated by D1's certified
  effect threshold (success criterion 1 of program.md §1).
- **D3 — Overfitting anatomy at tiny N_hf**: train/test gap decomposition across
  the ifc ladder N_hf ∈ {5, 20, 50} and the sharp N = 400 datasets, with an
  effective-sample-count estimate feeding the drift-class rule.

Each term below is aimed at REFUTING the novelty of one direction.

## Search terms used

1. `random seed variance minimum detectable effect statistical precipice rliable protocol claiming improvement deep learning benchmark` (→ D1)
2. `nearest neighbor in parameter space baseline parametric PDE surrogate benchmark trivial predictor mandatory reporting` (→ D1 floor-panel half)
3. `measuring value of privileged information matched arms with and without teacher distillation controlled ablation benchmark protocol` (→ D2)

## Findings per term

### Term 1 (→ D1, spread half) — REFUTED as general methodology

Top results: Deep RL at the Edge of the Statistical Precipice
(https://ar5iv.labs.arxiv.org/html/2108.13264 ;
https://papers.nips.cc/paper/2021/file/f514cec81cb148559cf475e7426eed5e-Paper.pdf),
"When +1% Is Not Enough: A Paired Bootstrap Protocol for Evaluating Small
Improvements" (https://arxiv.org/pdf/2511.19794), "A Tale of Two Variances: When
Single-Seed Benchmarks Fail in Bayesian Deep Learning"
(https://arxiv.org/pdf/2604.23114), "Torch.manual_seed(3407) is all you need"
(https://arxiv.org/abs/2109.08203), random effects in DL medical image
segmentation
(https://www.sciencedirect.com/science/article/pii/S0010482524010291), macro/micro
effects of random seeds on LLM fine-tuning (https://arxiv.org/pdf/2503.07329).

**Fetched — Agarwal et al., "Deep Reinforcement Learning at the Edge of the
Statistical Precipice" (https://ar5iv.labs.arxiv.org/html/2108.13264)**: warns
that "point estimates of aggregate performance such as mean and median scores
across tasks, ignoring the statistical uncertainty implied by the use of a finite
number of training runs" is unreliable; recommends (i) **stratified bootstrap
confidence intervals** (percentile bootstrap CIs give adequate coverage "with as
few as 10 runs"), (ii) **performance profiles** — empirical tail distribution
with pointwise bootstrap confidence bands, (iii) **interquartile mean (IQM)** as
the robust aggregate (discard bottom/top 25%), plus **optimality gap** and
**probability of improvement**. Explicitly targeted at the "3–10 runs per task"
regime. **This is exactly our 3-seed × 6-dataset regime, and it is published
protocol.**

**Fetched — Du, "When +1% Is Not Enough: A Paired Bootstrap Protocol for
Evaluating Small Improvements" (https://arxiv.org/abs/2511.19794)**: proposes
"paired multi-seed runs, bias-corrected and accelerated (BCa) bootstrap
confidence intervals, and a sign-flip permutation test on per-seed deltas". Key
number for us: on CIFAR-10/CIFAR-10N/AG News, "single runs and unpaired t-tests
often suggest significant gains for 0.6–2.0 point improvements", whereas **with
only three seeds the conservative paired protocol "never declares significance in
these settings"**. That is a direct, citable warning about what a 3-seed spread
can and cannot license — and it validates round 2's own **drift-class rule**
(paired in-job controls) from the opposite direction.

### Term 2 (→ D1, floor-panel half) — NOT refuted

Top results: Dimensionality Reduction in Surrogate Modeling review
(https://link.springer.com/article/10.1007/s41019-022-00193-5), VAE-DNN
surrogate for parametric PDEs (https://arxiv.org/pdf/2508.03839), PINNs and
neural operators for parametric PDEs (https://arxiv.org/pdf/2511.04576), Taking
the GP Out of the Loop (https://arxiv.org/pdf/2506.12818), deep surrogate for
Bayesian inversion (https://arxiv.org/pdf/1910.01547), Residual-Based Error
Corrector Operator (https://arxiv.org/pdf/2306.12047), Neural Surrogate Modeling
overview (https://www.emergentmind.com/topics/neural-surrogate-modeling).
**No usable results** for a *mandatory trivial-predictor floor panel* in
parametric-PDE surrogate benchmarking: the returned material discusses kNN only
as a modelling ingredient (epistemic nearest neighbours, kNN search failure modes
off the locally-linear patch) and GP/BNN as *baselines*, never a
nearest-neighbour-in-parameter / train-mean / zero panel as required reporting.
No fetch performed — nothing on the result list was close enough to be worth a
fetch. Combined with iteration 1's 2604.20061 (ROM-at-matched-offline-cost
interpolation diagnostic), the nearest published neighbours are ROM/GP baselines,
not training-free floors.

### Term 3 (→ D2) — REFUTED as general methodology

Top results: "Unifying distillation and privileged information" (Lopez-Paz et al.;
review at https://liner.com/review/unifying-distillation-and-privileged-information),
"Toward Understanding Privileged Features Distillation in Learning-to-Rank"
(https://proceedings.neurips.cc/paper_files/paper/2022/file/aa31dc84098add7dd2ffdd20646f2043-Paper-Conference.pdf),
Understanding Self-Distillation and Privileged Information Distillation
(https://emilianopp.github.io/Privileged-Information-Distillation-and-Self-Distillation/),
Privileged Information Distillation for Language Models
(https://arxiv.org/pdf/2602.04942), LUPI similarity control and knowledge
transfer (https://www.researchgate.net/publication/301362871_Learning_using_privileged_information_Similarity_control_and_knowledge_transfer).

Search-level finding (from the returned summaries of the NeurIPS 2022 PFD paper):
"Empirical ablation studies have been conducted on moderate-scale public and
industrial-scale proprietary datasets with deep-learning-to-rank models to
investigate why and when privileged feature distillation works and when it does
not", with PFD compared against **no-distillation, generalized distillation, and
self-distillation** baselines on Yahoo / Istella / MSLR-Web30k / an Amazon search
dataset. **Fetch of the NeurIPS PDF FAILED** (binary stream, unreadable) — so the
matched-arm design is, at this point, search-snippet-level only. Retry in
iteration 5 before I write the verdict, because this is the single most likely
preemption of D2.

## Interpretation

D1's *spread* half is preempted by a well-known, better-developed protocol
(Agarwal et al. 2021; Du 2025) which we should adopt rather than reinvent, and Du
gives a citable caution that three seeds rarely license a small-effect claim.
D1's *floor-panel* half survives one dedicated refutation attempt. D2's
refutation hinges on the PFD paper, which I must fetch in a readable form before
issuing the verdict.
