# Iteration 3 — s2_beyond_copy batch 3

## Search rationale
Two directions still needed their *multi-fidelity* framing tested rather than
their generic one: (a) does the MF-correction literature ever scale/normalize
the residual per sample (F10's defect)? (b) does anyone in downscaling report
grid mismatch or an inflated interpolation baseline (mentor-note prior art)?
Third, the honest B3 target itself: is there a published statement that a
trained coarse-to-fine corrector cannot beat what the coarse field already
contains?

## Search terms used
1. `multi-fidelity correction network per-sample scaling residual normalization varying residual magnitude across samples`
2. `deep learning downscaling fails to beat bilinear interpolation baseline climate super-resolution reference grid mismatch inflated skill`
3. `neural network correction of coarse PDE solution no better than interpolation negative result multi-fidelity surrogate reports failure`

## Findings

### Term 1 — per-sample residual scaling in MF correction networks
- **Residual Multi-Fidelity Neural Network Computing (RMFNN)** — FETCHED
  https://arxiv.org/html/2310.03572. The residual/bridge is
  `Q_HF(theta) - Q_LF(theta) = F(theta, Q_LF(theta))`; the framework *assumes*
  `||F||_Linf << ||Q_HF||_Linf` and motivates it by network-complexity bounds
  on the uniform norm of the target. Explicit answers from the fetch: the paper
  **does not** discuss scaling factors or normalization of the residual, and
  contains **"no discussion of per-sample or instance-wise scaling of
  residuals"**. It contrasts nonlinear residual learning with linear correction
  ("low-fidelity solutions lose their linear correlation with high-fidelity
  solution on parts of parameter domain").
- **Spectral-Prior Guided Multistage PINNs** (https://arxiv.org/pdf/2508.17902,
  search-listed; fetch failed on size, see Dead ends). Search summary states
  multi-stage networks fit "the residual of the previous stage" and that "the
  key idea is to normalize the residual magnitude and adjust the scale factor
  based on the residual characteristics of different stages", because "if the
  residual magnitude is much smaller than the original data, conventional
  weight initialization methods are difficult to effectively capture small
  signals". This is our pfc pathology (targets numerically zero after a global
  scaler) named in another setting — but PER-STAGE, not per-sample, and
  unfetched, so it is context, not a citation.
- Also surfaced: MF residual NN surrogate for structured sand
  (https://onlinelibrary.wiley.com/doi/10.1002/nag.3787), MF emulation with
  physics-guided KANs (https://arxiv.org/abs/2605.10958, "supports the need for
  a nonlinear residual model rather than a simple global correction factor").

### Term 2 — downscaling: grid mismatch and interpolation baselines
- **"Interpolation-Free Deep Learning for Meteorological Downscaling on
  Unaligned Grids"** https://arxiv.org/abs/2410.03945 (search-listed) — the
  existence proof that LR-HR **grid misalignment** is a recognized, named
  problem addressed by learned alignment rather than by fixing the reference.
- Precipitation-downscaling generalization benchmark
  https://www.nature.com/articles/s41598-025-34557-4 (search-listed):
  bilinear-interpolation baselines are built "to assess whether poor model
  performance in specific regions stems from generalization issues or
  challenges inherent to the input data"; baseline error varies strongly by
  region, so "comparative skill assessments are sensitive to baseline
  construction".
- No source found stating that a **misregistered** interpolation reference
  inflated published skill. Third framing attempted in iteration 4.

### Term 3 — the honest target: can a corrector beat the coarse field? (STRONG)
- **"Predictivity and Utility of Neural Surrogates of Multiscale PDEs"** —
  FETCHED https://arxiv.org/html/2604.20061v1. Three usable quotes:
  (i) *"Many successful benchmarks live on low-dimensional solution manifolds
  where any competent reduced model will interpolate well."*
  (ii) *"A network trained with mean-squared error converges to the conditional
  expectation u^(uc) = E[u | uc], i.e. the average over all fine states
  consistent with the coarse input"*; *"The resulting prediction is
  over-smoothed by construction, and no architecture or training procedure can
  recover information the coarse representation discards."*
  (iii) On baselines it advocates fair assessment ("fair comparison should be
  accompanied by ... end-to-end cost curves versus optimized solver and ROM
  baselines") but **does not** recommend comparing against the model's own LF
  input or a no-learning reference — consistent with batch 1's reading that
  this reference is a named gap.
- MF-GNN (https://onlinelibrary.wiley.com/doi/10.1111/mice.13312, search-listed)
  is another instance of the preempted composition: "a high-fidelity GNN
  refines estimations by computing residuals between upsampled low-fidelity
  estimates and actual high-fidelity solutions".

## Dead ends
- `https://arxiv.org/pdf/2508.17902` → fetch aborted, maxContentLength
  exceeded. Left as search-listed context only.

## Interpretation
The MF literature's own canonical residual formulation (RMFNN) explicitly does
NOT normalize the residual per sample and instead *assumes* a uniformly small
residual — an assumption our panel violates by 4-5 orders of magnitude
(F10: max/median per-sample ||r|| = 82379 on pfc). That is a concrete,
citable gap for the normalization arm. Meanwhile 2604.20061 supplies the exact
theoretical statement B3's open question needs: MSE-trained coarse-to-fine
correction converges to a conditional expectation and cannot recover discarded
information — a published reason to expect "no dataset beats the corrected
reference", which B3 must pre-register as a live outcome, not a failure.
ENOUGH on field context; iterations 4-5 go to refutation.
