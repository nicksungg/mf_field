# Iteration 2 — MDE certification when the *reference's* uncertainty is unobservable (C2)

## Search rationale

Batch 1's D1 verdict was `preempted-but-MF-composition-open` on the *fusion* of numerator (seed) and denominator (reference-cell) noise.
Batch 1's mechanism turn then produced a sharper, previously unasked question: on the two paper-bar cells the reference term is **not merely uncertain but unobservable** — `mdd_scored ≡ 0` collapses `tau_abs ≡ tau_rel`, while the copy-LF cells carry `tau_abs/tau_rel` up to 62×, and the round's own bootstrap estimator says the missing term would inflate `tau_abs` by ~2.15–2.17×.
The candidate M11 recommendation is to **certify the pair** `(mdd_scored = 0, mdd_reference_unobservable = <model-based estimate>)` and license on the max.
So the searches ask: (1) is "the published number I compare to has no error bar" treated as a claim-licensing problem; (2) is per-cell MDE certification with a pre-registered budget published; (3) does forecast verification — where the skill-score reference (climatology) is itself estimated — already supply the machinery.

## Search terms used

1. `comparing to published baseline number without error bars reproducibility uncertainty of the reported reference benchmark claim`
2. `minimum detectable effect size certification benchmark cell test set bootstrap machine learning claim licensing threshold 2026`
3. `skill score significance test uncertainty in the reference forecast climatology sampling error verification both terms estimated`

## Findings

### Term 1 — comparing against a published number with no error bar

Results: Uncertainty Baselines https://arxiv.org/pdf/2106.04015 ; "Towards Reproducible LLM Evaluation: Quantifying Uncertainty in LLM Benchmark Scores" https://arxiv.org/html/2410.03492 ; ORBIT hidden-test recommendation benchmark https://arxiv.org/pdf/2510.26095 ; Nature Communications "Error, reproducibility and uncertainty in experiments for electrochemical energy technologies" https://www.nature.com/articles/s41467-022-34594-x .
Search-snippet level (not fetched): the electrochemistry paper's framing is the closest general statement — "data reported for novel materials often exhibit high (or unstated) uncertainty and often prove challenging to reproduce quantitatively" — but the prescription is *report your own error bars*, not *license a comparison against a bar whose uncertainty you cannot observe*.
The ML entries all quantify uncertainty of the **evaluated system's** score, not of the historical constant it is compared to.
**No usable result** for the specific question.

### Term 2 — per-cell MDE certification / pre-registered budgets

Results: **Paired-MDE budget** https://arxiv.org/html/2605.28873 ; **paired bootstrap for small improvements** https://arxiv.org/html/2511.19794 ; paired noise-floor protocol for multi-agent LLM benchmarks https://arxiv.org/pdf/2606.20695 ; matched-FP-control benchmarking https://arxiv.org/pdf/2606.00329 ; MDE atlas https://www.tmls.nyc/research/eval-sample-complexity (already cited batch 1).

**FETCHED — "Pre-Registering the Detectable Effect: A Paired-MDE Budget for 4-bit Quantization Benchmarks, with a Pilot Audit"** (Zhuang, Li, Fan; arXiv:2605.28873v1, 25 May 2026), https://arxiv.org/html/2605.28873 (65,653 chars).
Adapts the classical paired-binary sample-size calculation (Miettinen 1968) to give a **conservative MDE bound** from the item count `m` and the disagreement rate ρ_d, turning "how reliable is my claim?" into "a one-line budget a benchmark designer can commit to **before running**".
Structure that matches this stream's job almost item-for-item: §5.1 "Observed Accuracy and the **Binomial Reference SD**", §5.4 a per-cell **Quantization Reliability Index** ("a single-split signal-to-noise heuristic ... **not a hypothesis test**"), §6 "**Cross-split SD is a misleading noise proxy here**", §7 Recommendations, **§8 Pre-Registration Template**, Appendix B "Per-Cell Binomial Reference SD", Appendix D Wilson CIs, Appendix E power curves.
Most relevant mechanism for C2: when the noise term cannot be observed by replication they substitute an **analytic model-based reference SD** (√(p̂(1−p̂)/n)) and compare the *observed* cross-split σ̂ against it per cell, precisely to diagnose "how much of the observed variance is sampling and how much is real".
That is the same move as our "estimate the unobservable reference term with the round's own shipped estimator and certify the pair".

**FETCHED — "When +1% Is Not Enough: A Paired Bootstrap Protocol for Evaluating Small Improvements"** (Du Wenzhang; arXiv:2511.19794), https://arxiv.org/html/2511.19794 (30,823 chars).
Paired multi-seed design + **BCa bootstrap CIs** + **sign-flip permutation test** + an explicit **decision rule**, motivated by "recent ML papers often report one–two percentage point improvements from a single run ... rarely accompanied by uncertainty estimates", and noting that when authors do repeat experiments "they often apply **unpaired**" comparisons.
This is the published version of batch 1's "use paired per-seed deltas + bootstrap, never max−min" recommendation, and it adds BCa + sign-flip as the concrete estimator pair.

### Term 3 — reference-forecast sampling error in skill scores

Results: **Bradley, Schwartz & Hashino (2008), "Sampling Uncertainty and Confidence Intervals for the Brier Score and Brier Skill Score"**, Wea. Forecasting 23(5), https://journals.ametsoc.org/view/journals/wefo/23/5/2007waf2007049_1.xml (PDF: https://journals.ametsoc.org/downloadpdf/view/journals/wefo/23/5/2007waf2007049_1.pdf) ; `SpecsVerification::SkillScore` https://rdrr.io/cran/SpecsVerification/man/SkillScore.html (batch-1 citation, second mirror) ; "Measuring forecast skill: Is it real skill or is it the varying climatology?" https://www.researchgate.net/publication/227616535_Measuring_forecast_skill_Is_it_real_skill_or_is_it_the_varying_climatology .
Search-snippet level: the Brier-skill-score paper states directly that **"the Brier skill score (with climatology as a reference forecast) is a biased estimator, and approximations are needed to estimate its bias and sampling variance"**, that the uncertainty estimators "depend only on the moments of the forecasts and observations, so it is easy to routinely compute them at the same time as the score", and that the results give CIs/hypothesis tests.
i.e. the *estimated-reference* problem for a ratio-form skill score is a solved, 2008-vintage problem in forecast verification — for a reference estimated **from the same sample**.

## Interpretation

C2's generic machinery is thoroughly published: pre-registered per-cell MDE budgets with an analytic reference SD (arXiv:2605.28873), paired-bootstrap decision rules (arXiv:2511.19794), and closed-form bias/sampling-variance for a skill score whose reference is itself estimated (Bradley et al. 2008).
What none of the retrieved sources covers is our actual configuration — a reference that is an **external published constant** from somebody else's finite test set, whose sampling error is unobservable in principle from our data, forcing a *counterfactual* estimate and a two-number certificate.
Term 1 returned no usable result on exactly that question, which strengthens the "MF/benchmark-composition open" shape rather than a novelty claim.
Iteration 3 turns to C3 (ULP-band tolerances) and C4 (the fit-set size seam).
