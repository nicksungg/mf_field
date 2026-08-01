# Iteration 3 — claimability protocol (direction c) and the calibration-explains-LF refutation

## Search rationale

Direction (c) proposes a repaired claimability protocol for
**draw-heteroscedastic** effects: a worst-split gate, an axis-appropriate
variance constant, and ≥5 draws. B3's T1-3 is the motivating defect — the
certified `min_claimable_effect` comes from 3 *training seeds* at the full
400-row split, while the card's dominant noise source is the *HF-subset draw*
(825× mismatch on allen_cahn). The right refutation question is therefore
"has the ML-benchmarking-statistics literature already settled which variance
axis dominates and what to do about it?" Term 2 is the head-on refutation
attempt for direction (a): has anyone shown that a *plain output calibration*
reproduces gains that were attributed to auxiliary/low-fidelity data?

## Search terms used

1. `paired comparison across data subsets heteroscedastic significance protocol machine learning benchmark worst-case split minimum number of seeds`
2. `simple output calibration matches gains attributed to auxiliary data ablation shows benefit explained by normalization not extra information`
3. `training subset resampling variance versus seed variance deep learning evaluation which dominates error bars data split`

## Findings

### Term 1 — paired/heteroscedastic comparison protocols

- Standard-practice returns only: corrected resampled paired t-test / 5×2 CV,
  McNemar, Friedman + Nemenyi, Wilcoxon signed-rank with Bonferroni
  [search returns: https://machinelearningmastery.com/statistical-significance-tests-for-comparing-machine-learning-algorithms/,
  https://pmc.ncbi.nlm.nih.gov/articles/PMC10435952/ (paired evaluation of ML
  models under confounders/outliers), https://arxiv.org/pdf/1901.03678 (MLaut)].
  Engine verdict, quoted: "The search results **don't contain specific
  information about heteroscedastic significance protocols, worst-case split
  analysis, or minimum number of seeds recommendations**."
- The **corrected resampled t-test** point matters for direction (c): the
  engine states "a key assumption of the paired Student's t-test is violated
  because the observations in each sample are not independent" when splits are
  reused — the same dependence B3's 3 shared HF-subset draws have.

### Term 2 — does calibration explain away an auxiliary-data gain? (**refutation attempt for (a)**)

- **No usable results.** Three successive result sets returned generic
  calibration literature (probability calibration, post-hoc recalibration,
  batch-norm feature calibration, chemometrics standardization patents) and
  the engine explicitly reported it could not find the study
  [search returns: https://arxiv.org/pdf/1905.10713 (field-aware calibration),
  https://arxiv.org/pdf/2503.00334 (MCNet monotonic calibration),
  https://arxiv.org/pdf/2104.12376 (recalibration of aleatoric/epistemic
  regression uncertainty), https://arxiv.org/html/2511.13250 (species-wise
  normalization + post-hoc calibration + cost–accuracy trade-offs)].
- Reading: nobody retrieved has run the **"is the auxiliary-data gain just an
  output-scale calibration?" ablation**. That is the exact question B4
  direction (a) asks, and it is the strongest remaining novelty surface in
  this stream. (Consistent with batch 3's three independent misses.)

### Term 3 — which variance axis dominates (the decisive hit for (c))

- **Bouthillier, Delaunay, Bronzi, Trofimov, Nichyporuk, Szeto, Sepah, Raff,
  Madan, Voleti, Ebrahimi Kahou, Michalski, Serdyuk, Arbel, Pal, Varoquaux et
  al., "Accounting for Variance in Machine Learning Benchmarks"** —
  https://arxiv.org/abs/2103.03098 **[curl-fetched: abstract; body via
  https://ar5iv.labs.arxiv.org/html/2103.03098]**. Verbatim from the body:
  "**Bootstrapping data stands out as the most important source of variance.
  In contrast, model initialization generally is less than 50% of the variance
  of bootstrap, on par with the visit order of stochastic gradient descent.
  Note that these different contributions to the variance are not independent,
  the total variance cannot be obtained by simply adding them up.**"
  Its three recommendations, verbatim: "**1) As many sources of variation as
  possible should be randomized whenever possible. These include weight
  initialization, data sampling, random data augmentation and the whole
  hyperparameter optimization… 2) Deciding of whether the benchmarks give
  evidence that one algorithm outperforms another should not build solely on
  comparing average performance but account for variance. We propose a simple
  decision criterion based on requiring a high-enough probability that in one
  run an algorithm outperforms another. 3) Resampling techniques such as
  out-of-bootstrap should be favored instead of fixed held-out test sets to
  improve capacity of detecting small improvements.**" Abstract adds the
  headline: "adding more sources of variation to an imperfect estimator
  approaches better the ideal estimator at a **51 times reduction in compute
  cost**", validated "on five different deep-learning tasks/architectures".
  Also cites **Hothorn et al. (2005)** as prior work that "focuses on the
  dataset sampling as the most important source of variation".
  **This preempts the diagnosis behind direction (c)** — "the data-sampling
  axis dominates the seed axis, so a seed-certified constant is the wrong
  ruler" is published, quantified, and comes with a decision criterion
  (probability-of-improvement in a single run) that is *stronger* than a
  worst-split gate.
- **"The FID Lottery: Quantifying Hidden Randomness in Generative-Model
  Evaluation"** — https://arxiv.org/pdf/2606.20536 [search return]. Engine
  synthesis: "Retraining the same recipe moves FID 3.2× more than redrawing
  samples does, so most of the variance hides in the single training run."
  Same genre, different domain: a recent re-measurement of which randomness
  axis dominates a benchmark metric.
- **"On the Variance of Neural Network Training"** —
  https://arxiv.org/pdf/2304.01910 and **Variational-resampling assessment of
  DNNs** — https://arxiv.org/pdf/1906.02972 [search returns]; engine
  synthesis: "variance across random seeds … can be large enough to reverse
  the ranking of competing methods."

## Interpretation

Direction (c) is preempted at the level of both diagnosis and remedy
(https://arxiv.org/abs/2103.03098: data-sampling variance dominates
initialization variance; randomize every axis; judge by probability that one
run beats another; prefer out-of-bootstrap to a fixed split) — a B4 that
proposes a "repaired claimability protocol" as a *contribution* is a rebadge,
though adopting Bouthillier's criterion as *methodology* is mandatory hygiene.
Conversely, term 2's clean miss says the specific question in direction (a) —
whether a cheap output-scale calibration reproduces what was credited to
low-fidelity training data — has not been asked, which makes (a) the stream's
last genuinely open surface. Turn 4 must try hardest to kill (a) and (b)
directly.
