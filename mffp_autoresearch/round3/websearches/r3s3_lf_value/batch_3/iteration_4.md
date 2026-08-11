# iteration_4 — r3s3_lf_value batch 3 (refutation turn 1 of 2)

## Search rationale

First of the two mandatory §3.3 turns. The candidate directions the brainstormer can propose in this slot are, from B2 part 7:
- **K1** — *pre-registered knee prediction*: run the training-free surrogate on the film-transfer cells, emit the predicted step-max knee cap **before any GPU leg**, confirm with a minimal 3-cap ladder bracketing it.
- **K2** — *the cross-cell instrument*: a training-free structural proxy that reproduces a trained FNO ladder's **shape** (not level), transferred to a cell it was not built on.
- **K3** — *stratified knee*: a subpopulation with **no knee** whose absence is hidden by the bulk mean.
This turn attacks K1 and K3 head-on plus the general "is a-priori saturation prediction already done in MF" question.

## Search terms used

1. `a priori prediction of saturation point multi-fidelity training data before running experiments validated on held-out problem`
2. `subgroup learning curves heterogeneous saturation subpopulation does not improve with more data scaling`
3. `training-free proxy predicts where adding more low-fidelity simulation data stops improving neural surrogate knee prediction confirmed`

## Findings

### Term 1 — a-priori MF saturation (**body fetched**)
Search returned: "Improvise, Adapt, Overcome: An On-The-Fly Multifidelity Algorithm for Efficient Machine Learning" (https://arxiv.org/html/2606.02662); MF-FNO for geological carbon storage (https://arxiv.org/pdf/2308.09113); MF force fields (https://arxiv.org/pdf/2511.11361, snippet-only, also seen in batch 2); "An adaptive strategy for sequential designs of multilevel computer experiments" (https://arxiv.org/pdf/2104.02037); two ScienceDirect items (403 genre).
**Fetched** https://arxiv.org/html/2606.02662 (Vinod & Zaspel, Univ. Wuppertal, 1 Jun 2026; 49,709 chars). Verbatim:
- "standard MFML schemes rely on **pre-defined scaling factors** to determine sparse data ratio across fidelities, often generating redundant multifidelity data" — i.e. the incumbent a-priori device is a fixed heuristic ratio (N_{f-1} = 2·N_f), not a prediction.
- Their method is **reactive, not predictive**: "If the improvement falls below a predefined **local tolerance**, the algorithm advances to the next fidelity"; the improvement "is assessed over a moving average of the MAE"; "the algorithm **saturates model accuracy at lower fidelities** before moving up to more expensive reference calculations."
- Saturation is reported **post hoc and attributed to the data**: "For larger cost budgets, the learning curves for all three models begin to plateau out and saturate ... **it is not an artifact of the MFML or adaptive scheme itself but rather an intrinsic property of the underlying chemical space being learned**."
⇒ The closest MF work decides sample counts by **watching a measured validation curve against a tolerance**. It never names the saturation point in advance, and it needs the HF/LF labels it is deciding whether to buy.

### Term 2 — subgroup saturation → surfaced the canonical survey (**body fetched**)
Search returned (2 sub-queries): "Learning Curves for Noisy Heterogeneous Feature-Subsampled Ridge Ensembles" (https://arxiv.org/pdf/2307.03176), "Learning Shrinks the Hard Tail: Training-Dependent Inference Scaling in a Solvable Linear Model" (https://arxiv.org/html/2601.03764), "**Learning Curves for Decision Making in Supervised Machine Learning: A Survey**" (https://arxiv.org/pdf/2201.12150), "Shape-Constrained Bayesian Active Learning of Self-Limiting Saturation Curves" (https://arxiv.org/html/2606.26577), "When AI Benchmarks Plateau: A Systematic Study of Benchmark Saturation" (https://arxiv.org/html/2602.16763).
**Fetched** https://arxiv.org/pdf/2201.12150 (Mohr & van Rijn survey, 65 pp, 183,938 chars). Verbatim and load-bearing:
- Terminology the card should adopt: "the **saturation point** is the anchor after which the performance convergences ... all values are in a distance of less than some pre-defined and typically very small ε ... we will denote the saturation point itself as **b_sat**"; "the right-sided open interval bounded by the saturation point from the left is consistently called the **plateau**"; also **pre-exponential point** ("the smallest anchor point for which an increase by a factor of q leads to a performance improvement of less than some δ") and **anchors** for the ladder rungs.
- The named problem: "**Projective early stopping means to predict the saturation point before it is reached** and stop precisely at the (believed) saturation point. The projective approach is particularly important in the case of sample-wise curves."
- The state of descriptor-based prediction, verbatim: "**To the best of our knowledge, the only line of research utilising meta-features for learning curve modelling is the work of Leite and Brazdil (2008, 2010); Ruhkopf et al (2023).**" Both described methods still consume a **partial empirical learning curve on the target dataset** and combine it with meta-feature distance to *other datasets'* curves ("the distance between the partial learning curves and the distance in terms of meta-features"; MASIF "takes partial learning curves ... and combines them with dataset meta-features").
No subgroup-stratified saturation result was retrieved; the search engine's own synthesis was that subgroup-level saturation dynamics is "an active area of investigation" (synthesis, not a citation — not used below).

### Term 3 — direct refutation attempt: training-free proxy for the LF-supply knee
**No usable results.** Three sub-queries returned MF surrogate/proxy-model work with no bearing (reservoir proxies, ship-hull MF proxies, NAS zero-cost proxies — https://arxiv.org/html/2505.09344v1, https://arxiv.org/pdf/2302.00932) and the query term "knee" was captured by **biomechanics** (knee arthroplasty surrogates). The search engine explicitly reported it could not find such work. Treat this as a *null return*, not as proof of absence.

## Interpretation

K1's *concept* has a name in the literature — **projective early stopping / predicting the saturation point b_sat** (Mohr & van Rijn) — so it must be cited and cannot be presented as a new idea; but every retrieved instance of it consumes a **partial empirical curve on the target dataset**, and the only meta-feature line of work is two citations deep by the survey's own admission. In multi-fidelity specifically, the incumbents are a fixed ratio heuristic and a reactive tolerance rule (2606.02662). Nothing retrieved predicts the location from a **training-free structural descriptor with zero observed anchors on the target cell**. Turn 5 closes K2 and issues the verdict.
