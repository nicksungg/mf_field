# Iteration 4 — the constant-predictor sanity bar, and MF-specific scaler practice

## Search rationale

Two remaining gaps. (i) Q5: B1 part 6's most consequential finding is that the
champion is **worse than a constant-field oracle** on three panel datasets;
if "beat the mean predictor" is a published sanity bar, that finding gains a
citable frame and the batch-2 card can adopt the bar without inventing it.
Iteration 1's snippet on The Well's VRMSE ("predicting the mean gives 1") is
exactly that, but was unfetched — retry via the arXiv HTML endpoint. (ii)
Verdict (iii) needs MF-specific evidence: does anyone in multi-fidelity
pretrain->finetune surrogate work state how LF and HF data are scaled?

## Search terms used

1. `VRMSE variance-scaled RMSE metric "the Well" benchmark predicting the mean baseline value 1 neural surrogate`
2. `trivial baseline constant predictor mean field sanity check neural operator PDE benchmark "persistence" baseline comparison`
3. `multi-fidelity neural network normalization low-fidelity high-fidelity data same scaling factor preprocessing transfer learning surrogate`

## Findings

### Term 1 — The Well / VRMSE — USABLE, and directly frames B1's oracle result
- Fetched https://arxiv.org/html/2412.00568 (Ohana et al., "The Well: a
  Large-Scale Collection of Diverse Physics Simulations for Machine Learning").
  Verbatim: **"predicting the mean value of the target field results in a score
  of 1."** The paper reports it uses VRMSE "over the more common Normalized
  RMSE (NRMSE)" because "the centered normalization is more appropriate for
  non-negative fields". In its own baseline table multiple architectures score
  **">>>10"** on datasets including `rayleigh_taylor_instability` (all four
  models) and `active_matter` (FNO, TFNO) — i.e. published neural operators
  routinely score **worse than predicting the mean**, in a flagship benchmark.
- The same fetch reports that the paper **does not specify its training-time
  field normalization** (per-field / training-split / per-sample) in the main
  text or appendices — so iteration 1's snippet claim about "training-split
  per-field statistics" stays **uncited**.
- Benchmark leaderboard endpoint located, not fetched:
  https://polymathic-ai.org/the_well/benchmarks/ .

### Term 2 — "weak baselines" in ML-for-PDEs — usable but for a different point
- Fetched https://arxiv.org/html/2407.07218v1 (McGreivy & Hakim, "Weak
  baselines and reporting biases lead to overoptimism in machine learning for
  fluid-related partial differential equations"). It quantifies the problem:
  **"Of articles that use ML to solve a fluid-related PDE and claim to
  outperform a standard numerical method, we determine that 79% (60/76) compare
  to a weak baseline."** Its two rules are "make comparisons at either equal
  accuracy or equal runtime" and "compare to an efficient numerical method".
- **It does NOT advocate trivial statistical baselines** (mean predictor,
  persistence) — its target is under-tuned numerical solvers. So it supports
  the *norm* of adversarial baselining (which is what B1's constant-field
  oracle and copy-LF are) but is not a citation for the mean-predictor bar
  itself; The Well is.
- Search-level lead, not fetched: DeltaPhi https://arxiv.org/pdf/2406.09795
  (residual learning for data-limited PDE solving) — adjacent to s2/s6, not
  this stream.

### Term 3 — MF-specific normalization practice — mostly a dead end
- Fetched https://arxiv.org/html/2511.01830 ("Towards Multi-Fidelity Scaling
  Laws of Neural Surrogates in CFD"): **"no explicit discussion of
  normalization procedures is provided"** for LF vs HF data; the only mention
  is "MSE of normalized fields" in a figure caption. Recorded as evidence that
  the MF-surrogate literature **leaves the LF/HF scaler unspecified**.
- Attempted the airfoil MF transfer-learning paper for the one search-snippet
  claim of a bespoke "logarithmic-exponential normalization" in an MF transfer
  pipeline: https://doi.org/10.3390/app151910820 redirected to
  https://www.mdpi.com/2076-3417/15/19/10820 , which returned **HTTP 403**.
  The claim is therefore **NOT citable**; noted as a lead only.
- Other located-but-unfetched MF references (leads only):
  https://arxiv.org/pdf/2306.06904 (differentiable MF fusion + NAS),
  https://arxiv.org/pdf/2410.12241 (transfer learning for surrogate modeling).

## Interpretation

The constant/mean-predictor bar is **published and load-bearing** in a flagship
PDE benchmark: The Well deliberately scales its primary metric so that the mean
predictor sits at exactly 1.0, and reports many strong architectures above it —
so B1's constant-field-oracle finding is a standard diagnostic, not a novel
one, and adopting it as a reported reference line in s5-B2 costs nothing and
claims nothing. Conversely the MF pretrain->finetune literature is essentially
**silent on how LF and HF targets are scaled** (the closest scaling-law paper
does not state it; the one bespoke-normalization MF-transfer hit is unfetchable),
which means a stage-consistency knob has no published prior to appeal to and no
published preemption either.

## ENOUGH

Field context is sufficient: Q1 (field-standard scaler), Q2 (per-sample
normalize/denormalize is a published model-agnostic wrapper, incl. a PDE-domain
instance in MPP), Q3 (robust vs max-abs, library-documented), Q4 (two opposed
fetched priors; no MF-specific statement exists), Q5 (The Well's mean-predictor
bar) are all answered from fetched sources. Iteration 5 spends the last turn on
§3.3 refutation searches for the three mandated verdicts.
