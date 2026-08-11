# iteration_3 — r3s3_lf_value batch 3

## Search rationale

Three residual holes before the refutation turn. (1) **Knee/elbow detection as methodology** — the card's statistic is a "step-max knee cap"; if a standard named algorithm exists, the card must cite it (and justify deviating), not reinvent it. (2) **PDE/operator-learning data-requirement forecasting** — does the surrogate community already predict its own sample needs before training? (3) **Transfer scaling laws** — the film-transfer baseline the slot must register against is literally a pretrain→finetune setup, so the closest exchange-rate formalism (effective data transferred) has to be checked, including whether it claims an a-priori ratio.

## Search terms used

1. `knee elbow detection algorithm Kneedle curvature discrete curve knee point selection`
2. `neural operator surrogate data scaling law predict how many training samples needed PDE before training`
3. `scaling laws for transfer effective data transferred pretraining predicts when fine-tuning data makes pretraining irrelevant`

## Findings

### Term 1 — knee detection is a named, packaged methodology (**body fetched**)
Search returned: kneed docs (https://kneed.readthedocs.io/en/stable/), kneed on PyPI/GitHub (https://github.com/arvkevi/kneed), a multi-knee library (https://github.com/mariolpantunes/knee), and "Kneeliverse: A universal knee-detection library for performance curves" (https://www.sciencedirect.com/science/article/pii/S2352711025001281, ScienceDirect — not fetched, 403 genre).
**Fetched** https://kneed.readthedocs.io/en/stable/ (7,812 chars), verbatim: "kneed is a Python library for detecting knee (elbow) points in curves using the Kneedle algorithm. Given a set of x and y values, it identifies the point of maximum curvature — the 'knee' or 'elbow' of the curve"; features include "Multiple knee detection via online mode" and a "Tunable sensitivity parameter (S)"; citation given as **Satopää, Albrecht, Irwin & Raghavan (2011), "Finding a 'Kneedle' in a Haystack: Detecting Knee Points in System Behavior", 31st ICDCS Workshops, pp. 166–171**. Search-snippet only (Kneeliverse): the field has "Menger, L-method, Kneedle, and DFDT" as established knee detectors.
⇒ **Detecting a knee in an observed curve is off-the-shelf and preempted.** Nothing here predicts a knee that has not been measured.

### Term 2 — PDE-surrogate data requirements
Search returned: "Data-Efficient Time-Dependent PDE Surrogates: GNS vs. Neural Operators" (https://arxiv.org/html/2509.06154v1 — already fetched in **batch 2, iteration 1**), "Structure-Aware Epistemic UQ for Neural Operator PDE Surrogates" (https://arxiv.org/html/2603.11052), "Towards Multi-spatiotemporal-scale Generalized PDE Modeling" (https://arxiv.org/pdf/2209.15616), Neural-Parareal (https://arxiv.org/pdf/2405.01355), a data-free surrogate PMC article.
Snippet content only: sample-size choices are **reported empirically** (train sizes 30/50/70/100; "less than 1 % relative L2 error using only 3 % of available trajectories"; PCA+KMeans sample-selection strategies). **No result forecasts the required sample count before training.** No bodies fetched this turn — nothing cited from this term.

### Term 3 — transfer scaling laws / exchange rate (**body fetched**)
Search returned Hernandez, Kaplan, Henighan & McCandlish, "Scaling Laws for Transfer" (https://arxiv.org/pdf/2102.01293), plus "Scaling Laws for Data-Efficient Visual Transfer Learning" (https://arxiv.org/html/2504.13219v1), "An Empirical Study of Scaling Laws for Transfer" (https://arxiv.org/pdf/2408.16947), "A Scaling Law for Synthetic-to-Real Transfer" (https://arxiv.org/pdf/2108.11018).
**Fetched** https://arxiv.org/pdf/2102.01293 (19 pp, 46,033 chars). Verbatim:
- Definition of the exchange rate: "D_T - effective data transferred, the amount of additional python ... that a model trained on python from-scratch of the same size would have needed to achieve the same loss ... as a pre-trained model", with the fitted law "D_T = effective data transferred = k(D_F)^α (N)^β (1.1)".
- The saturation mechanism: "the weights can saturate or 'ossify', where they become unable to absorb new information well, and that ossification scales predictably ... the prior learned in pre-training becomes counterproductive if it's learned with too much relative strength."
- Future-work item 6, verbatim: "**A method to cheaply predict the ideal pre-training ratio for a pair of datasets A and B to maximize performance on a target distribution C, for which we have limited data.** It'd be exciting if that ratio were a relatively simple function of the transfer coefficients."
⇒ The **exchange-rate formalism is fully preempted** (and stronger than ours: a fitted two-variable power law). But the *cheap a-priori prediction of the pretrain/finetune (here LF/HF) ratio* is listed by that same paper as an **open problem**, and their D_T is obtained by **fitting measured runs**, not predicted from a descriptor.

## Interpretation

Two of the card's components are now firmly preempted as generic method — **knee detection** (Kneedle/Kneeliverse) and **the data exchange rate** (Hernandez et al.) — and must be cited, not claimed. What survives is precisely the *direction of inference*: every retrieved work locates the knee/ratio **by fitting curves it has already measured**, while the slot's object is to name the cap **from a training-free descriptor of the cell, before any leg runs**, and then be judged by whether the confirming ladder lands on it. Turn 4 spends its budget on the explicit refutation searches for that composition.
