# Iteration 2 — identifiable rank, relative-metric shrinkage, regime mixtures

## Search rationale

Iteration 1 left three gaps. (i) Rank selection by *condition-identifiability*
(out-of-fold R^2 of each POD coefficient regressed on the parameters) was not
returned — only the classical singular-value-energy criterion; B1's finding 1
is exactly an identifiable-rank ladder, so this needs a dedicated term.
(ii) B1's finding 2 (calibration zeroes non-DC gains) and r2s4-B1's
lambda* = 0 shrinkage oracle are both consequences of the round's **per-sample
relative-L2** score; is that shrinkage effect analyzed anywhere?
(iii) B1's cross-stream note 4 says pfc is two datasets with a
condition-predictable class (out-of-fold AUC 0.9998) — is regime
classification + per-regime scoring published for PDE surrogates?

## Search terms used

1. `how many POD modes are predictable from input parameters out-of-sample R2 coefficient regression reduced order model identifiability`
2. `relative L2 error metric biases predictions toward smaller magnitude optimal scaling shrinkage of surrogate output`
3. `regime classification before surrogate prediction mixture of experts parametric PDE stratified per-regime evaluation`

## Findings

### Term 1 — identifiable POD rank

Top results:
- Mode-realigned pointwise interpolation for POD-Galerkin parametric ROMs — https://arxiv.org/pdf/2604.25955
- Data-driven parameterized ROMs for distortion in metal 3D printing — https://arxiv.org/pdf/2412.04577
- ROM for parameterized LES of atmospheric pollutant dispersion — https://arxiv.org/pdf/2208.01518
- POD-DL-ROM — https://www.sciencedirect.com/science/article/pii/S0045782521005120
- POD-based MOR for discontinuous parameters — https://www.mdpi.com/2311-5521/7/7/242

**Load-bearing search return** (from the aggregated snippet over these
results): "*References suggest reducing the modes of a POD based on the
R^2-Score of the POD coefficients surrogate models*", alongside the standard
practice of mapping input parameters to POD coefficients with NN / polynomial
chaos / GPR. I attempted to confirm the criterion in the pollutant-dispersion
ROM: **FETCH FAILED** — https://arxiv.org/pdf/2208.01518 returned unreadable
binary, so nothing is quoted from it and the snippet stands as a *search
return only*. The engine also said explicitly that no result matched the
specific out-of-sample-R^2 identifiability question.

Treated as: truncating POD modes by the coefficient surrogate's R^2 is very
likely established practice; iteration 3 must confirm with a fetchable source
before any novelty claim is made either way.

### Term 2 — relative-L2 metric and output shrinkage

Top results:
- Lower Bounds and a Near-Optimal Shrinkage Estimator for Least Squares using
  Random Projections — https://arxiv.org/pdf/2006.08160
- Scaling laws for amplitude surrogates — https://arxiv.org/pdf/2601.13308
- Penalization/shrinkage unreliable at small sample size (clinical prediction) — https://pmc.ncbi.nlm.nih.gov/articles/PMC8026952/
- Survey of unsupervised learning for high-dim UQ — https://arxiv.org/pdf/2202.04648

**FETCHED** https://arxiv.org/pdf/2601.13308 — **NOT USABLE AS EVIDENCE.**
The paper is Bahl, Bresó-Pla, Butter & Iturriza Ramirez, "Scaling laws for
amplitude surrogates": *particle-physics scattering amplitudes*, scaling-law
(Kaplan/Hoffmann) analysis — a homonym of "amplitude", not field-norm
prediction. The fetch summary returned a sentence matching my prompt's own
phrasing ("the optimal predictor shrinks its output norm") which I could not
locate as an independent claim; **I am discarding it as prompt echo and citing
nothing from this paper.** (Recorded per program.md §13.3: recall and
unverifiable snippets are not citations.)

Usable finding: the only shrinkage results returned are the classical
statistical ones (James-Stein-family shrinkage estimators for least squares,
arXiv:2006.08160; shrinkage unreliability at small n, PMC8026952). This
matches what `websearches/r2s4_diag/batch_2/report.md` D3 already concluded
from a different angle — the shrinkage *operation* is textbook, and the
published surrogate calibrators rescale variance rather than the point
prediction.

### Term 3 — regime classification / mixture of experts before surrogate prediction

Top results:
- Surrogate Models and Mixtures of Experts in Aerodynamic Performance
  Prediction — https://www.sciencedirect.com/science/article/abs/pii/S1270963815000760
  (and the PDF mirror https://www.researchgate.net/publication/269228953_Surrogate_Models_and_Mixtures_of_Experts_in_Aerodynamic_Performance_Prediction_for_Mission_Analysis)
- On Least Square Estimation in Softmax Gating Mixture of Experts — https://arxiv.org/pdf/2402.02952
- Direct Learning of Calibration-Aware Uncertainty for Neural PDE Surrogates — https://arxiv.org/html/2602.11090
- Mixture of Experts Distributional Regression — https://arxiv.org/pdf/2211.09875

Search returns establish that mixture-of-experts surrogates exist precisely to
handle "piecewise continuous patterns" and regime changes (the transonic
regime is the canonical motivating example, where "conventional surrogate
models such as radial basis functions and kriging cannot model these functions
accurately"). Also returned: "regime-adaptive uncertainty scaling from held-out
gradients" (arXiv:2602.11090) — held-out-fit *uncertainty* scaling, again not
point-prediction gains.

No usable result for *per-regime stratified scoring of a benchmark test split*
as a reporting requirement; the MoE literature is about the model, not about
splitting the score.

## Interpretation

Regime-conditional prediction (pfc's two classes) is **preempted at the model
level** by the mixture-of-experts surrogate literature. The relative-metric
shrinkage phenomenon reduces to textbook shrinkage estimation, exactly as
r2s4-B2 independently concluded. The one live thread is whether "truncate the
basis at the identifiable rank (R^2 of the coefficient surrogate)" is
published — one search return says yes, and the confirming fetch failed;
iteration 3 must settle it, because B1's entire "identification over capacity"
framing rests on it.
