# Iteration 5 — refutation turn 2 and the VERDICT (**iteration cap 5 reached; this is the final iteration**)

## Search rationale

Two citations were still owed: a **fetched** source for the closed-form
combination weight from the error covariance (direction B's mechanism), and a
**fetched** source for predictability-guided component selection (direction C).
Both hunted with HTML/abs targets only, after four PDF extraction failures.

## Search terms used (2 of the 3 allowed)

1. `mode-wise selection of interpolation method for each POD mode adaptive choice per coefficient reduced order model`
2. `multi-model blending weights derived from error correlation random variables theory Geophysical Research Letters 2025`

## Findings

### Term 1 (direction A, third and final refutation search)
Returns: "Mode-realigned pointwise interpolation (MRPWI) for efficient
POD-Galerkin parametric reduced-order models" (arXiv:2604.25955); "Interpolation
Method for Adapting Reduced-Order Models and Application to Aeroelasticity"
(https://arc.aiaa.org/doi/10.2514/1.35374); POD with adaptive **snapshot**
selection (https://www.sciencedirect.com/science/article/abs/pii/S0021999119304814).
Every "mode-wise" hit is about interpolating **the modes/subspaces themselves**
(manifold interpolation, mode realignment) or about adaptive **snapshot**
selection -- not about choosing a different regression family per modal
coefficient. **Third independent miss for per-mode family selection.**
**Fetch attempted**: https://royalsocietypublishing.org/rspa/article/480/2283/20230655/101080/Multi-fidelity-reduced-order-surrogate
-> **HTTP 403. Cited for nothing.**

### Term 2 (direction B mechanism, final attempt)
Returns: Wang et al. 2025, GRL, "Explanation and Optimizing Multi-Model Blending
Algorithm Using Random Variables Theory"
(https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2024GL111622) --
engine text: the study *"modeled the multi-model blending process using random
variables and explicitly derived the distribution of the blended forecast error"*
and *"the model yielded negative weights, which contradict traditional
assumptions that weights should be positive"*.
**Fetch attempted**: that AGU URL -> **HTTP 402 Payment Required. Cited for
nothing.**
**Fetched (successful, from the iteration-3 return set)**:
https://search.r-project.org/CRAN/refmans/MuMIn/html/BGweights.html ->
*"Model weights are then calculated as `w_BG = (1' Sigma^-1 1)^-1 1 Sigma^-1`"*
where Sigma is *"the variance-covariance matrix between model predictions ...
derived by fitting models to a random half of the data and predicting on the
remaining half"*; reference given as **Bates, J. M. and Granger, C. W. J. 1969,
"The combination of forecasts", J. Oper. Res. Soc. 20, 451-468**; and *"the
weights can occasionally fall outside the [0,1] range"*.
**Fetched (successful, from the iteration-4 term-3 return set)**:
https://arxiv.org/abs/2011.05309 -> Ritchie, Balzano, Kessler, Sripada, Scott
(2020), "Supervised PCA: A Multiobjective Approach": *"Methods for supervised
principal component analysis (SPCA) aim to incorporate label information into
principal component analysis (PCA), so that the extracted features are more
useful for a prediction task of interest"*; prior work *"focused primarily on
optimizing prediction error, and has neglected the value of maximizing variance
explained"*.

## Cap note

**Iteration cap 5 hit.** Two threads are closed as UNRESOLVED-BY-FETCH and are
reported as such below: (a) the explicit two-forecast `alpha*(rho)` formula
(returned by the engine three times, never fetched: MDPI 403, AGU 402, two PDFs
unreadable) -- the fetched BGweights page carries the equivalent covariance form
and the 1969 primary reference, which is enough to declare the mechanism
preempted; (b) whether any ROM paper selects a regression **family** per POD
mode (three targeted searches, zero named sources; the Springer review and the
RSPA paper both refused fetch).

---

# PRIOR-ART VERDICT (batch 3)

Candidate directions a batch-3 card is likely to propose, from
`experiment_cards/r2s1_direct/batch_2/B2.json` part 7.

## C1 — Per-mode out-of-fold model-family selection over a bank ({affine, quadratic, kernel ridge, kNN}) for condition -> POD-coefficient regression, priced against a trained decoder BEFORE any shared post-hoc stage

**Verdict: `preempted-but-MF-composition-open (cite)`.**
Preempted parts, and they are the big ones: (i) *one independent regressor per
modal coefficient* is standard practice -- three separate engine passes state it
(iteration 1: *"K independent models employed, each associated with one modal
coefficient"*; iteration 2: *"Because POD reduced coefficients are decorrelated,
independent models can be designed for each reduced coefficient"*; iteration 3:
*"the typical approach ... applying a unified regression strategy to the POD
coefficients"*) -- **all search-return only, no fetch survived (Springer 303-only,
RSPA 403)**, so it is recorded as **presumed prior art: do not claim it**;
(ii) automatic surrogate-model selection by cross-validation over trained
candidates is published as ASAMS
(https://pmc.ncbi.nlm.nih.gov/articles/PMC7571090/ , fetched in
`websearches/r2s1_direct/batch_2/iteration_5.md`), at the whole-model level;
(iii) POD-NN / PCA-Net / RB-DeepONet coefficient regression is `preempted`
(batch-1 verdict D2).
What remains open after three targeted refutation searches with zero named
sources: selecting the **regression family per mode** by out-of-fold R^2, and
using the resulting 10-parameter map as the **standing control arm** that a
1.6e7-parameter conditioned decoder must beat **on a copy-LF-skill panel under a
stripped (no-LF-at-test) view**, with the per-mode ORACLE ceiling reported
beside it. Nearest neighbours: global family comparisons (POD+PCE vs
POD+PC-Kriging), ASAMS, and McGreivy & Hakim's weak-baseline critique
(https://arxiv.org/abs/2407.07218 , fetched in batch 2).
**Standing bound to state in the card**: Lanthaler et al.
(https://arxiv.org/abs/2210.01074 , via `docs/reports/MF_Sharp_HighFreq_Report.md:180`)
proves linear-reconstruction architectures are inefficient for discontinuous
solution operators -- 4 of 6 panel datasets.

## C2 — Instrument/protocol contribution: a shared post-hoc baseline-blend (or floor-hedge/ensemble) stage pays off as a closed-form monotone function of rho, so any cross-arm comparison decided at that stage is a decorrelation verdict, not an accuracy verdict; therefore arms must be scored pre-stage and blend bases decorrelation-audited

**Verdict: `preempted-but-MF-composition-open (cite)`.**
**Mechanism preempted, with a fetched citation**: the minimum-variance
combination weight is a closed form in the error covariance matrix,
`w_BG = (1' Sigma^-1 1)^-1 1 Sigma^-1`, and the weights *"can occasionally fall
outside the [0,1] range"* --
https://search.r-project.org/CRAN/refmans/MuMIn/html/BGweights.html , which
attributes it to **Bates & Granger (1969), "The combination of forecasts",
J. Oper. Res. Soc. 20, 451-468**. Weight shrinkage and covariance-shrinkage
constraints in combination are likewise mature
(https://arxiv.org/html/2510.26456 , fetched: constraints connect to
"covariance matrix shrinkage", Remark 1). So B2's "blend payoff is a function of
rho" is **not a discovery** and must be named as Bates-Granger combination in
the card.
What remains open (one search, zero usable results -- iteration 4 term 2, engine
declared the topic absent): the use of that law as an **evaluation-protocol
defect detector** -- i.e. the claim that appending a shared floor-blend stage to
every arm of a *benchmark* converts an architecture comparison into a
decorrelation comparison, with the quantified consequences B2 measured (an arm
class that IS the base at rho = 1.0000 cannot be paid; the decisive cell reverses
by 2.07-7.15x mce when the decoder's rho is substituted; lambda <= 0.25 means the
card is reporting the base, not the arm). The fetched combination literature
treats candidates **symmetrically** and never as a benchmark's shared post-hoc
stage (https://arxiv.org/html/2510.26456 : *"none receives special 'baseline'
status"*). **This is the best-supported novel composition available to B3**, and
it is a methodology claim, not an accuracy claim.

## C3 — Identified-SET indexing / predictability-ordered output basis (fit the head on the modes that are identifiable from the condition, not on the leading energy window)

**Verdict: `preempted (cite)`.**
Fetched: Ritchie et al. 2020, "Supervised PCA: A Multiobjective Approach"
(https://arxiv.org/abs/2011.05309): SPCA methods *"aim to incorporate label
information into principal component analysis (PCA), so that the extracted
features are more useful for a prediction task of interest"*. Fetched:
"Dimensionality Reduction in Surrogate Modeling: A Review of Combined Methods"
(https://pmc.ncbi.nlm.nih.gov/articles/PMC9633505/): *"supervised methods produce
more suitable topology representations of input-output maps compared to
unsupervised methods"*. Search-return support (iteration 4): PCs *"are not
guaranteed to be informative of the response variable"*; *"projecting data onto
the top principal components can thus discard valuable information"*; Bair &
Tibshirani 2004 named as the origin. Batch 2 already recorded identifiable-rank
truncation as **presumed prior art, do not claim**; this loop upgrades that to
**preempted with a fetched citation**.
Nearest neighbours / what is technically not covered: the fetched DR review
*"does not discuss or recommend selecting reduced bases specifically optimized
for output predictability"* and retains components by *"captured variance"*, and
the one reduced-rank-regression paper fetched (https://arxiv.org/html/2601.07202)
turned out to be about **predictor-side** PCs. That residue is far too thin to
claim: SPCA/PLS/reduced-rank regression own this idea. **Use it as a bug fix and
an instrument, never as a contribution.**

## C4 — H2: testing whether a trained decoder's advantage comes from spatial inductive bias reaching low-energy, low-OOF-R^2 modes (projection of decoder predictions onto the fit-fold basis)

**Verdict: NOT PRIOR-ART-CHECKED THIS LOOP** (iteration cap reached before a
targeted search could be run). It must not be headlined as novel. It is
admissible as a *diagnostic* inside a card whose claimed contribution is C1 or
C2, and it requires the build gate B2 missed: every decoder arm must ship
`preds_test.npz`.

## Carried-citation provenance (audit)

Citations reused from earlier loops of THIS stream, fetched there, not re-fetched
here, and used only as context/bounds (never as a batch-3 novelty verdict on
their own):
- ASAMS — https://pmc.ncbi.nlm.nih.gov/articles/PMC7571090/ (fetched in
  `websearches/r2s1_direct/batch_2/iteration_5.md`)
- McGreivy & Hakim — https://arxiv.org/abs/2407.07218 (fetched in
  `websearches/r2s1_direct/batch_2/iteration_4.md`)
- Wiener gain / Self-Wiener — https://www.emergentmind.com/topics/non-causal-wiener-filter
  (fetched in `websearches/r2s1_direct/batch_2/iteration_5.md`)
- PODNO (POD-NN / PCA-Net statement) — https://arxiv.org/html/2504.18513v1/
  (fetched in `websearches/r2s1_direct/batch_1/iteration_3.md`)
- REALM — https://arxiv.org/html/2512.18595 (fetched in
  `websearches/r2s1_direct/batch_1/iteration_2.md`)
- Conditional-mean barrier — https://arxiv.org/html/2605.28076 (fetched in
  `websearches/r2s1_direct/batch_1/iteration_3.md`)
- Lanthaler et al. — https://arxiv.org/abs/2210.01074 (in-repo prior websearch
  `docs/reports/MF_Sharp_HighFreq_Report.md:180`)
