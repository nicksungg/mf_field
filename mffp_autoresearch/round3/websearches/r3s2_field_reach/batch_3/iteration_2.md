# Iteration 2 — the MF-surrogate side, and model selection on the deployment distribution

## Search rationale

Iteration 1 established that the oracle-vs-predicted ladder is standard *outside* SciML (compound-AI pipelines, CV). Two things remain: (i) does the multi-fidelity surrogate corpus run the same decomposition, i.e. does anyone attribute a stacked MF error between the LF emulator and the downstream corrector; (ii) is component (b) — select the corrector's regularisation on the emulator's held-out output rather than on real LF — a known idea, since if it is, it is a rebadge of importance-weighted / target-domain model selection.

## Search terms used

1. `multi-fidelity surrogate replacing low-fidelity solver with learned emulator degrades correction error budget attribution`
2. `selecting regularization hyperparameter on model-predicted inputs deployment distribution instead of ground truth covariate shift model selection`
3. `"low-fidelity" emulator predictions substituted for low-fidelity simulations multi-fidelity Gaussian process error contribution stage-wise ablation oracle`

## Findings

### Term 1 — MF corpus, emulator-vs-corrector attribution

Returned: <https://arxiv.org/html/2506.11683v1>, <https://arxiv.org/pdf/2511.15934>, <https://arxiv.org/pdf/2503.08408>, <https://doi.org/10.3390/rs18111826>, <https://arxiv.org/pdf/2105.01081>, ScienceDirect non-hierarchical MF surrogate. The engine again conceded the gap explicitly: *"These results discuss the general framework of multi-fidelity surrogate modeling but don't specifically address your exact query about how replacing a low-fidelity solver with a learned emulator degrades the correction error budget."* — the **third independent engine-level concession** across batches 2–3 that this composition is not asked.

**Fetched — Choi, Zanoni, Schiavazzi & Marsden, "On the performance of multi-fidelity and reduced-dimensional neural emulators for inference of physiologic boundary conditions"** (<https://arxiv.org/html/2506.11683v1>, HTML body retrieved, 124,296 chars). This is the closest MF-side neighbour found: an upstream surrogate feeding a downstream *statistical estimator* (a Bayesian posterior), with the surrogate's error explicitly accounted for downstream. Verbatim: *"**Replacing the true model with an approximation inevitably introduces errors in posterior sampling, whose magnitude depends on the approximation error**"*; their remedy is to *"treat the discrepancy between the high-fidelity model and its surrogate as a random variable, whose distribution must be inferred … incorporate the approximation error into the Bayesian inverse problem by modifying the likelihood function."* Note the two structural differences from our card: (a) their LF 0D model is still *evaluated* (it is cheap), so there is no hallucinated intermediate; (b) their downstream object is a posterior estimator, not a frozen field corrector, and the accounting is probabilistic (modelling-error term in the likelihood) rather than a measured oracle-vs-predicted ladder.

### Term 2 — model selection under covariate shift

Returned: <https://arxiv.org/pdf/1712.10050> (Kernel Robust Bias-Aware Prediction under Covariate Shift), <https://arxiv.org/pdf/2506.12007> (SIMSHIFT), <https://arxiv.org/pdf/2111.08234>, <https://arxiv.org/pdf/2507.22647> (Transductive model selection under prior probability shift), plus researchgate entries for "Model Selection Under Covariate Shift" and "General regularization in covariate shift adaptation" (not fetched; researchgate is paywalled/403-prone).

**Fetched — arXiv:1712.10050** (PDF, 43,381 chars). Direct hit on the *principle* behind component (b), verbatim: *"We choose regularization parameter λ by 5-fold cross validation, or **importance weighted cross validation (IWCV)** … **Note that the traditional cross validation process is not correct anymore in the covariate shift setting, because under the covariate shift assumption, the source marginal data distribution of P(x) is diff[erent]**"*. This is precisely B2's M7 stated in the standard vocabulary: our LOOCV was run on the fit-fold *real-LF* rows while deployment is on *pseudo-LF* inputs, so the selection objective is measuring the wrong risk.

**Fetched — SIMSHIFT, arXiv:2506.12007v3 [cs.LG] 10 Feb 2026** (PDF, 200,257 chars). A benchmark for *neural surrogates* under distribution shift, and it treats model selection as a first-class object: *"After training, **unsupervised model selection strategies choose θ_k1, which is expected to perform best on the target domain**"*; contributions include *"a modular benchmarking suite that complements our datasets with baseline models and algorithms. It allows for easy integration of new simulations, machine learning methods, domain adaptation techniques, **and model selection strategies**."* Their shift is a *parameter/geometry* shift between design regimes (hot rolling, sheet-metal forming, electric motor, heatsink), with target-domain **inputs available but outputs not** — structurally the same information situation as ours (we can produce unlimited pseudo-LF inputs from the emulator; we lack HF labels for them beyond the 5 train rows).

### Term 3 — MF-GP stage-wise / substituted-LF ablation

Returned: <https://www.sciencedirect.com/science/article/pii/S0307904X21001724> (Residual GP), <https://arxiv.org/pdf/2105.01081> and <https://academic.oup.com/mnras/article/509/2/2551/6413553> (matter-power-spectrum MF emulation), <https://arxiv.org/html/2604.18045> (ensemble MF emulation + adaptive sampling), <https://arxiv.org/pdf/2108.00306> (graphical MF GP), <https://emukit.github.io/multifidelity-emulation/>. Snippet-level only; the recurring structure is *"a Gaussian process built to predict low fidelity simulation results at arbitrary [parameter], and second, a Gaussian process used to model a … correction function between low and high fidelity simulations."* That is a **two-stage stack whose LF stage is itself a learned emulator** — i.e. the topology of our stack exists in cosmology MF-GP emulation — but nothing in the snippets reports an oracle-vs-emulated-LF error split. **No usable result for the decomposition**; not fetched (deferred: the MF-GP-with-emulated-LF topology gets its own refutation term in iteration 3).

## Interpretation

Component (b) is preempted at the level of principle: choosing a regulariser on the deployment input distribution rather than the training one is exactly the covariate-shift model-selection problem, and IWCV/target-domain selection are its standard answers (1712.10050), with SIMSHIFT showing the neural-surrogate community already benchmarking model selection under shift. Component (a)'s *decomposition* remains unretrieved on the MF side — three engine-level concessions now — with 2506.11683 the nearest neighbour (surrogate error propagated into a downstream estimator, but the LF model is still evaluated and the accounting is probabilistic, not an oracle ladder).
