# Iteration 5 — refutation turn 2 + PRIOR-ART VERDICT (final; iteration cap 5 reached)

**Cap note**: this is iteration 5 of 5. The loop stops here whether or not
threads remain open; unresolved threads are flagged as such below rather than
resolved by assumption.

## Search rationale

Two mechanisms still lacked a decisive refutation attempt. E1's band-gain fit
is, stated abstractly, "an optimal multiplicative gain per frequency" — which
is the definition of a **Wiener filter**, so the honest refutation term names
it. E2's "select the model form from dataset statistics" is, stated
abstractly, **meta-learning / AutoML model selection**, so the honest
refutation term names that.

## Search terms used

1. `Wiener filter optimal per-frequency gain applied to machine learning prediction spectral coefficients shrinkage estimator regression` (targets E1)
2. `meta-features dataset statistics automatic model configuration selection surrogate modeling engineering simulation AutoML` (targets E2)

## Findings

### Term 1 (E1) — the band-gain fit IS a Wiener filter

Top results:
- Non-Causal Wiener Filter for MMSE Estimation — https://www.emergentmind.com/topics/non-causal-wiener-filter
- Optimal spectral shrinkage and PCA with heteroscedastic noise — https://arxiv.org/pdf/1811.02201
- Numerical Recipes §13.3 "Optimal (Wiener) Filtering with the FFT" — https://123.physics.ucdavis.edu/week_5_files/filters/wiener_filter.pdf
- Analysis of the frequency-domain Wiener filter with the prediction gain — https://ieeexplore.ieee.org/document/5496034/
- A Probabilistic Generative Model for Spectral Speech Enhancement — https://arxiv.org/pdf/2603.28436

**FETCHED** https://www.emergentmind.com/topics/non-causal-wiener-filter —
gives the non-causal Wiener filter as a per-frequency gain
`H_nc(e^{jw}) = S_hy(e^{jw}) / S_yy(e^{jw})` ("a cross-spectrum divided by the
observation power spectral density"), and quotes the Self-Wiener extension:
"**SW adapts the shrinkage factor to local, data-driven SNR estimates,
ultimately recovering the classical Wiener solution at high SNR ... SW
hard-thresholds frequency components with low SNR, improving noise suppression
for bandlimited or sparse signals.**"

This is decisive for E1's mechanism. B1's per-band gain
`g_b = <y_b, yhat_b> / ||yhat_b||^2` fitted out of fold IS the empirical
non-causal Wiener gain of the prediction, and B1's observed behaviour ("all
non-DC band gains go to zero on every sharp dataset") is exactly Self-Wiener's
"hard-thresholds frequency components with low SNR". The search return also
records that "in the classical regime, optimal shrinkage with whitening
converges to the Wiener filter" (arXiv:1811.02201, search return, not fetched).

**FETCH FAILED** https://123.physics.ucdavis.edu/week_5_files/filters/wiener_filter.pdf
(Numerical Recipes §13.3) — PDF text not extractable; the canonical textbook
statement is therefore *not* quoted, and the emergentmind page carries the
citation instead.

### Term 2 (E2) — automatic surrogate-model selection

Top results:
- ASAMS: Adaptive Sequential Sampling and Automatic Model Selection for AI
  Surrogate Modeling — https://pmc.ncbi.nlm.nih.gov/articles/PMC7571090/
- A Recommendation System for Meta-modeling: A Meta-learning based Approach — https://www.sciencedirect.com/science/article/am/pii/S0957417415007162 (**FETCH FAILED, HTTP 403** — not used as evidence)
- Automatic selection for general surrogate models — https://www.researchgate.net/publication/316999697_Automatic_selection_for_general_surrogate_models
- Meta-learning for model selection and hyperparameters — https://www.ml4devs.com/what-is/meta-learning-for-model-selection-and-hyper-parameters/

**FETCHED** https://pmc.ncbi.nlm.nih.gov/articles/PMC7571090/ (ASAMS):
"**Yes, ASAMS automatically selects the surrogate model type**", but the
selection is by grid search + leave-one-out cross-validation — "In each
iteration, this framework uses a grid search algorithm to determine the best
candidate models and perform a leave-one-out cross-validation to calculate the
performance of each sampled point" — and it "requires training candidate
models ... rather than purely statistical analysis of the raw dataset".
**It is explicitly NOT training-free.**

Search-return note: the generic AutoML meta-feature menu ("number of instances
and features, class imbalance ratio, linearity measures, cluster tendency,
dimensionality reduction quality, **landmarking performance from simple
baselines**, and statistical moments") is standard — but landmarking still runs
models, and nothing returned selects the **output parameterization of a field
predictor** (centering form, basis rank) from a training-free statistic.

## Unresolved thread (declared, not assumed)

Whether "truncate the POD basis at the rank whose coefficients are actually
*predictable* (R^2 of the coefficient surrogate)" is published remains
**UNRESOLVED after two search turns** (iterations 2 and 3 returned opposite
snippets, and both confirming fetches failed). Any B2 card must treat
identifiable-rank truncation as **presumed prior art** and must not claim it as
a contribution.

---

# PRIOR-ART VERDICT

Directions are E1-E4 as defined in `iteration_4.md` (they follow B1's
`7_gap_and_future.next_direction`, items 1-3, plus its cross-stream note 4).

## E1 — out-of-fold per-spectral-band gain calibration of a frozen
## condition→field predictor's POINT output

**Verdict: `preempted (cite)`** — at the mechanism level, decisively.

- The optimal per-frequency multiplicative gain is the **Wiener filter**:
  `H_nc = S_hy / S_yy` [fetched: https://www.emergentmind.com/topics/non-causal-wiener-filter].
- The observed "zero all non-DC bands" behaviour is the **Self-Wiener**
  hard-threshold of low-SNR frequency components [same fetched source].
- Fitting a post-hoc correction to a **frozen** predictor's point output on
  held-out data, selected from a library, is published, including the
  closed-form optimal affine gain `a* = Cov(Y,Z)/Var(Z)` and a "scale
  amplitude" rescale [fetched: https://arxiv.org/html/2505.15354].

**What remains open** (three refutation attempts found nothing on any of
these): (i) no fetched source applies the gain **band-resolved** to a learned
PDE-surrogate's point prediction as a post-hoc, out-of-fold stage — the band
gates that exist are learned *inside* the architecture
[https://arxiv.org/pdf/2606.21189, fetched] or need **test-time observations**
[FreqNO-DPS https://arxiv.org/html/2606.03936, search return + in-repo report];
(ii) no source reads the **fitted gain vector as an identifiability
diagnostic** (which bands carry condition-predictable signal); (iii) none of
this is done under a **per-sample relative-L2** score where the shrinkage is
not a bug but the scored optimum.
**Consequence for B2**: band-gain calibration may be used as *machinery* and
its *diagnostic reading* may be the contribution — it may NOT be claimed as a
new correction method. Cite the Wiener filter in the card.

## E2 — training-free, statistic-selected output parameterization
## (centering form by ||mean field||/geomean||y||; rank by identifiable rank)

**Verdict: `preempted-but-MF-composition-open (cite)`.**

- Automatic surrogate-model selection is established, but the fetched
  instance selects by **grid search + LOOCV over trained candidates**, i.e. it
  is explicitly not training-free [fetched: ASAMS
  https://pmc.ncbi.nlm.nih.gov/articles/PMC7571090/].
- Generic AutoML meta-features exist, and "landmarking from simple baselines"
  is one of them (search return) — again requiring model runs.
- Magnitude/direction factorization in the returned literature applies to
  **weight vectors**, not output fields [https://arxiv.org/abs/2606.25971,
  search return].
- Basis-rank truncation by energy is classical; truncation by coefficient
  predictability is **presumed prior art** (unresolved above).

**What remains open**: selecting the *output parameterization of a field
predictor* (direction x amplitude vs additive; basis rank) from **training-free
statistics computed on the train split alone**, and doing so per dataset on a
fixed panel with the selection rule pre-registered. No fetched source does this.
**Consequence for B2**: the selection *rule* can be the contribution; the
individual ingredients (POD rank, amplitude factorization, CV model selection)
are all baselines and must be declared as such.

## E3 — mandatory ~10^2-parameter closed-form control arm that any capacity
## claim must beat, with the capacity claim localized to `sharp__cahn_hilliard`

**Verdict: `preempted-but-MF-composition-open (cite)`.**

- The **architecture** of the control arm is published: PCA coefficients
  regressed from the input with a **closed-form ridge solve** on top of random
  features, benchmarked against DeepONet/FNO [fetched: PCA-RaNN
  https://arxiv.org/pdf/2606.29440]; and the linear-reconstruction class
  (POD-NN / PCA-Net / RB-DeepONet) was already `preempted` in batch 1.
- The **critique motivating it** is famous: 79% (60/76) of ML-for-PDE papers
  claiming to beat standard methods use a weak baseline [fetched:
  https://arxiv.org/abs/2407.07218, McGreivy & Hakim, Nature Mach. Intell.
  2024].

**What remains open**: that paper's "weak baseline" means an **inadequate
classical numerical solver**, not a trivial learner, and the fetched abstract
page states it "does not specify particular baseline protocols or reporting
requirements", calling for cultural/structural reform instead. So: **a standing
protocol requiring a ~10^2-parameter closed-form arm beside every learned arm
on a copy-LF-skill panel, with per-dataset localization of where capacity
survives, is not prescribed anywhere I fetched** — and batch 1 already found
that the strongest current surrogate benchmark (REALM
https://arxiv.org/html/2512.18595) compares against no trivial baselines at
all.
**Consequence for B2**: this is the best-supported contribution shape available
to the stream. It must cite McGreivy & Hakim as the motivation and PCA-RaNN as
the control arm's prior art, and claim only the protocol + the localization
result.

## E4 (secondary) — regime/class-conditional prediction and per-class scoring
## on the two-population `sharp__phase_field_crystal_2d`

**Verdict: `preempted (cite — SEARCH-RETURN ONLY, NOT FETCHED; provisional)`.**

Mixture-of-experts surrogates exist precisely for regime-piecewise responses
(the transonic regime is the canonical example, where "conventional surrogate
models such as radial basis functions and kriging cannot model these functions
accurately") [search return:
https://www.sciencedirect.com/science/article/abs/pii/S1270963815000760].
Open: per-class **scoring** of a benchmark test split as a reporting
requirement was not returned. **Because no source was fetched for this row, E4
must not be the card's headline contribution without a batch-3 confirmation
fetch**; use it as a reporting refinement (B1's cross-stream note 4 already
demands per-class pfc scoring on internal-validity grounds, independent of
novelty).

## Interpretation

The stream's B1 conclusion ("stop buying capacity, spend on identification and
calibration") survives contact with the literature, but with the ownership
line drawn sharply: **the calibration operation is Wiener filtering (old), the
control-arm architecture is PCA+ridge (published), and the model-selection idea
is AutoML (published)** — what is not published is the **protocol**: a
training-free selection rule plus a standing closed-form control arm plus a
band-gain vector read as an identifiability diagnostic, evaluated on a
copy-LF-skill panel where the ceiling is itself certified.
