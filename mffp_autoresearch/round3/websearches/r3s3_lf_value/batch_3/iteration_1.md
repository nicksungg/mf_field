# iteration_1 — r3s3_lf_value batch 3

## Search rationale

The slot is fixed (knee-predictability, film units). Batch 2 already priced *the sweep*; what is unpriced is the new object: **naming a sample-efficiency knee BEFORE the curve exists**, from a training-free descriptor. Turn 1 therefore attacks the three literatures that could preempt that outright: (a) cheap-proxy prediction of learning-curve shape, (b) broken/piecewise scaling laws and whether anyone claims to locate a break from pre-break information, (c) multi-fidelity budget allocation as the "when does LF stop substituting for HF" framing.

## Search terms used

1. `predicting learning curve breakpoint sample efficiency from cheap proxy without training`
2. `broken neural scaling law breakpoint prediction piecewise power law fitting data scaling`
3. `multi-fidelity surrogate optimal budget allocation how many low-fidelity samples diminishing returns theory`

## Findings

### Term 1 — cheap-proxy learning-curve prediction
WebSearch returned (top 5 of 10): "Selection via Proxy: Efficient Data Selection for Deep Learning" (https://openreview.net/forum?id=HJg2b0VYDr); "Can Small Training Runs Reliably Guide Data Curation? Rethinking Proxy-Model Practice" (https://arxiv.org/html/2512.24503v1); "An imputation method for estimating the learning curve in classification problems" (https://arxiv.org/pdf/1203.2879); a Medium explainer on data-selection-via-proxy (https://medium.com/data-centric-ai/efficient-data-selection-via-proxy-f08738f7d940); two USPTO patents on managing ML with plural training-set sizes (https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11568300, .../9164961).
Snippet-level content: the genre is **small/short-trained neural proxies** (fewer layers, fewer epochs) used for *data selection* and for *forecasting final performance from early training dynamics*, plus power-law fitting/interpolation of learning curves between anchor points. **No result predicts a breakpoint, and every proxy in this genre still trains a network.** Bodies not fetched (search-snippet only) — none of these is cited as prior art below.

### Term 2 — broken scaling laws / breakpoint location (**body fetched**)
Search returned the BNSL cluster (https://arxiv.org/pdf/2210.14891, ICLR 2023; OpenReview mirrors; emergentmind summaries).
**Fetched** `https://arxiv.org/pdf/2210.14891` via `python3 urllib.request` + `pypdf` (38 pp, 98,193 chars). Verbatim, load-bearing:
- "Ideally, one would like to be able to extrapolate the entire scaling behavior by fitting only points from before the break."
- "we are only able to accurately extrapolate the scaling behavior if given some points from training runs with a training dataset size of at least 720, and the break ... happens at around training dataset size of 415" — and even in a **noiseless, infinite-seed** simulation the fit range must reach "at least 415, which is very close to the break."
- Implication (2), verbatim: "**If an additional break of sufficient sharpness happens at a scale that is sufficiently larger than the maximum (along the x-axis) of the points used for fitting, there does not (currently) exist a way to extrapolate the scaling behavior after that additional break.**"
- Stated limitation: "A potential limitation of the current approach is the need to collect enough samples of the system's performance ... A small number of samples sometimes may not be sufficient to accurately fit and extrapolate the BNSL functional form."
So the canonical broken-scaling-law work is a **post-hoc fitting form that requires observed points at or beyond the break**, and it names a-priori break location as an explicit open problem.

### Term 3 — MF budget allocation / diminishing returns
Search returned: "Recursive rounding of sample size estimation for multi-fidelity Monte Carlo" (https://arxiv.org/html/2607.29607); "Optimally balancing exploration and exploitation to automate multi-fidelity statistical estimation" (https://arxiv.org/pdf/2505.09828); "A novel low-fidelity-guided design of experiments for multi-fidelity surrogate modeling" (ScienceDirect S1474034625009693 — 403-walled per batch-1/2 dead ends); Springer MF-BO items; ANZIAM MF survey.
Snippet content: allocation is framed as **variance/MSE minimisation for MF Monte Carlo estimators** and as **cost-aware DoE**, i.e. a *decision* about the sample ratio, not a *prediction of a breakpoint in a trained surrogate's error curve*. Bodies not fetched this turn.

## Interpretation

The strongest single result of turn 1 is that BNSL — the reference work for breakpoints in data-scaling curves — states in its own text that break location cannot currently be extrapolated from points below it, which is exactly the gap the card would occupy (a *training-free structural surrogate* naming the cap before any leg runs). Turns 2–3 must now check the two remaining preemption routes: (i) kernel/GP/NTK surrogates that predict neural learning curves without training, and (ii) MF-specific "how many LF samples before HF is required" theory with a computable threshold.
