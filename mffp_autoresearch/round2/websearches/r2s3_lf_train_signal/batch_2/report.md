# Websearch Report — Stream `r2s3_lf_train_signal`, Batch 2

**Stream**: `r2s3_lf_train_signal` (lever — "how much does LF, available only
during training, help a condition→HF model?")
**Batch**: 2
**Total iterations**: 5 (cap 5 — **CAP HIT**, noted in `iteration_5.md`)
**WebSearch calls**: 14 (turns 1–4: 3 each; turn 5: 2)
**WebFetch calls**: 12 — 9 usable, 3 unusable (binary/unparseable PDFs:
kiwi.oden `multifidelity-regression-data-poor` , arXiv:2209.15265,
arXiv:2408.17075; the first was recovered via arXiv:2508.08517)
**Cap hit**: yes (5/5)

## Search trace

### Turn 1 — the linear/affine channel and the null-direction framing
Terms: non-nested MF linear regression; transfer learning where source data
spans the null space of the target design; linear/closed-form baselines vs
neural operators. Chosen because B1's part 7 makes both live directions
*statistical*, so the classical MF-regression and transfer-learning literatures
are where preemption would live.
- **LR-MFS**: "the system behavior (high-fidelity behavior) is approximated by a
  linear combination of the low-fidelity predictions and a polynomial-based
  discrepancy function", coefficients fitted in a **single least squares**
  [cite (fetched): https://arxiv.org/abs/1705.02956].
- **Retain-plus-transfer**: fine-tuning "retains target-learned signal in the
  span of n_0 target samples ... while transferring source information only into
  the null space S_0^perp where the target samples provide no information"
  [cite (fetched): https://arxiv.org/html/2510.15337].
- Classical KO/recursive MF-GP **assumes nested designs**; non-nested (different
  parameter values) is an explicitly worked setting
  [cite (fetched): https://arxiv.org/abs/2511.20183].
- Closed-form least-squares readouts are competitive with neural operators
  [search return: https://arxiv.org/pdf/2606.29440, also fetched in
  `websearches/r2s1_direct/batch_2`]. → `iteration_1.md`

### Turn 2 — the repaired-network trio (E3) and the per-dataset gate
Terms: multi-resolution operator training / normalization / aliasing; implicit
bias in underdetermined regression; training-free linear-vs-neural gating.
- **MG-TFNO**: normalization must be global/function-wise because batch-norm
  "depends on the spatial variables"; mode truncation keeps "the first α modes
  in each direction, where α is independent of the discretization"; it does NOT
  train on multiple resolutions simultaneously
  [cite (fetched): https://arxiv.org/html/2310.00120].
- **MRA-FNO** treats resolutions as fidelities inside an **active-learning**
  acquisition loop with cost annealing
  [cite (fetched): https://arxiv.org/abs/2309.16971].
- Min-norm implicit bias in the underdetermined regime
  [cite (fetched): https://arxiv.org/pdf/2006.07356 — the *extrapolation*
  sentence is fetch prose, flagged as a lead, not evidence].
- Training-free linear-vs-neural per-dataset gate: **No usable results** (engine
  stated the returns do not match). → `iteration_2.md`

### Turn 3 — refutation 1: E1's estimator, the "affine benchmark" claim, E3c
Terms: MF linear regression for full fields / data-poor; reduced-basis affine
parameter dependence; null-space regularization for neural operators.
- Surfaced "Projection-based multifidelity linear regression for data-poor
  applications" (Sella/Pham/Chaudhuri/Willcox) — **fetch failed** on the PDF.
- **Affine parameter dependence is the assumed-normal regime of reduced-basis
  methods** (whole sub-literatures exist for the non-affine case)
  [search returns: https://link.springer.com/chapter/10.1007/978-88-470-2592-9_16,
  https://arxiv.org/pdf/1911.08954, https://arxiv.org/pdf/1705.08349] → B1's
  "ifc_poisson is exactly affine" is a **benchmark-integrity** statement, not a
  mathematical discovery.
- **NPN** regularizes the *measurement operator's* null space because
  "conventional methods leave the null-space uncontrolled"
  [cite (fetched): https://arxiv.org/html/2510.01608]; deep null space learning
  [https://iopscience.iop.org/article/10.1088/1361-6420/aaf14a] and Safe
  Regularization [https://link.springer.com/chapter/10.1007/978-3-030-61616-8_18]
  round out the family. → `iteration_3.md`

### Turn 4 — refutation 2: the decisive hit
Terms: retrieve the Willcox data-poor MF linear regression; matched
with/without-LF value-of-LF ablations; NN-vs-OLS on exactly linear maps.
- **arXiv:2508.08517 (AIAA 2023-0916; ML for CSE 2025,
  DOI 10.1007/s44379-025-00049-5)**: three **MF linear regression** methods
  (additive KO / direct data augmentation / regression-mapping augmentation)
  with **POD projection of high-dimensional field outputs**, in the
  **data-scarce** regime; **"LF data can be evaluated at parameter values where
  no HF data exists"**; compared against **HF-only** regression, concluding
  "when LF data quality is high, multifidelity approaches provide benefits;
  conversely, poor LF data can degrade predictions"
  [cite (fetched): https://arxiv.org/pdf/2508.08517].
- Value-of-LF: only the qualitative "LF does not always help" position
  [search returns: https://arxiv.org/abs/2404.14456,
  https://dl.acm.org/doi/10.1007/978-981-95-7072-0_32]; **no** matched-architecture
  neural field ablation at N_hf ≈ 5 (second independent miss).
- Overparameterized nets fail to uniquely recover a linear ground truth below an
  n/d threshold [search-returned synthesis of https://arxiv.org/pdf/2209.15265;
  **fetch failed**, so cited as a search return only]. → `iteration_4.md`

### Turn 5 — refutation 3: the per-dataset gate; then the verdict (cap hit)
Terms: a-priori criterion for whether MF will help; automatic fallback when LF is
harmful.
- MF reviews make LF–HF correlation the standard admissibility check
  [search returns: https://arxiv.org/html/1609.07196v5,
  https://www.aimsciences.org/article/doi/10.3934/acse.2023015].
- **arXiv:2403.08118 "Characterising harmful data sources when constructing
  multi-fidelity surrogate models"**: identifies harmful LF sources using "only
  the limited data available to train a surrogate model", framed as **algorithm
  selection** via **Instance Space Analysis**, producing "an intuitive
  visualisation of when a low-fidelity source should be used"
  [cite (fetched): https://arxiv.org/abs/2403.08118]. → `iteration_5.md`

## Prior-art verdict

| Candidate direction | Verdict | Citations (fetched/returned this loop) | What remains open |
|---|---|---|---|
| **E1** — ship the linear/affine LF channel `c·A(cond) + R(cond)` (A on the best LF rung, c + residual ridge on the 5 HF rows) as the stream's B2 family | **preempted** | https://arxiv.org/abs/1705.02956 (LR-MFS: LF prediction as basis + polynomial discrepancy, one least-squares fit, motivated by few affordable HF runs — fetched); https://arxiv.org/pdf/2508.08517 (projection-based MF **linear** regression for **data-scarce** apps, **POD-projected field outputs**, additive-KO / direct-augmentation / regression-mapping variants — fetched) | Nothing at the mechanism level. Only implementation detail (rung selection by in-rung LOO) and the specific panel. Ship it as a **cited baseline**, never as a contribution. |
| **E2** — LF rows at **disjoint** conditions supply the null direction of the 5×6 HF design (rank completion at N_hf = 5) | **preempted-but-MF-composition-open** | https://arxiv.org/html/2510.15337 (retain-plus-transfer: source information transferred **only into the null space** of the target design — fetched); https://arxiv.org/pdf/2508.08517 ("LF data can be evaluated at parameter values where no HF data exists"; HF-only baseline; LF can degrade — fetched); https://arxiv.org/abs/2511.20183 (non-nested MF-GP; classical KO assumes nested designs — fetched) | The **field-valued, neural, certified-floor** instance: null direction of a *condition* design matrix filled by **coarse consistent PDE solves**, priced in skill units against a 3-seed `min_claimable_effect`, on a panel where 5/6 datasets have **condition-aligned** rungs (LF carries only spectral truncation). **Supersedes batch 1's `novel` verdict for D3.** |
| **E3a** — per-rung (resolution-dependent) output scaler | **novel but weak; against convention** | Nearest: https://arxiv.org/html/2310.00120 (normalization must be global/function-wise, not spatially dependent, to preserve discretization invariance — fetched) | Only as a dataset-specific bug fix for `ifc_poisson`'s h² amplitude convention. Not a contribution; must be justified against discretization invariance. |
| **E3b** — mode clipping pinned at the HF Nyquist for every rung | **preempted** | https://arxiv.org/html/2310.00120 ("the first α modes in each direction, where α is independent of the discretization" — fetched) | Nothing. This is the standard convention; B1 deviated from it. Bug fix. |
| **E3c** — explicit null-direction gain calibration / min-norm penalty | **preempted-but-MF-composition-open** | https://arxiv.org/html/2510.01608 (NPN, null space of the **measurement operator**, "conventional methods leave the null-space uncontrolled" — fetched); https://iopscience.iop.org/article/10.1088/1361-6420/aaf14a and https://link.springer.com/chapter/10.1007/978-3-030-61616-8_18 (search-returned); theory: https://arxiv.org/pdf/2006.07356 (fetched), https://arxiv.org/pdf/2209.15265 (search-returned synthesis: below an n/d threshold an overparameterized net fails to recover a linear truth) | The **measurement**, not the fix: a FiLM-FNO placing 27.7% of its implicit law energy in the unconstrained direction **anti-aligned** (cos −0.99) contradicts the min-norm implicit-bias prediction. No retrieved work reports null-space behaviour of a *neural field operator over a parametric design matrix*. |
| **E4** — training-free per-dataset gate (structural affinity test → LF channel vs no-LF control) | **preempted** | https://arxiv.org/abs/2403.08118 (harmful LF sources identified from "only the limited data available to train a surrogate model"; algorithm selection + Instance Space Analysis; "when a low-fidelity source should be used" — fetched); MF reviews' LF–HF correlation criterion (https://arxiv.org/html/1609.07196v5, search-returned); per-location ReLU-gated LF-vs-HF borrowing (https://hal.science/hal-04602579/document, search-returned) | The gate **feature** (affine-LOO residual of the condition→field map) is unretrieved, but it is a feature choice inside a preempted framework. Mandatory engineering; not a claim. |
| **E5** — the **measurement**: matched, budget-equal with/without-LF-training contrast for a **neural condition→field** surrogate at N_hf ≈ 5 (and N = 400 with condition-aligned rungs), per dataset, against a certified 3-seed noise floor | **novel** (nearest neighbours named) | Nearest: https://arxiv.org/pdf/2508.08517 (HF-only vs MF comparison — but linear POD regression, no neural arm, no seed-noise floor); https://arxiv.org/abs/2403.08118 (harmful-source characterisation, not a matched training ablation); qualitative "LF does not always help" (https://arxiv.org/abs/2404.14456, https://dl.acm.org/doi/10.1007/978-981-95-7072-0_32) | Everything: three independent search framings (batch 1 iter 3; batch 2 iters 4 and 5) failed to retrieve a matched-architecture with/without-LF accounting for neural field surrogates at this sample count. This is round-2 success criterion 1 and the stream's remaining publishable content. |

## Citations summary

- [Zhang et al. 2017/2018] "Multi-Fidelity Surrogate Based on Single Linear Regression" (LR-MFS) — https://arxiv.org/abs/1705.02956 (AIAA J. 10.2514/1.J057299) — used in: iteration_1 (term 1, fetched), iteration_3 (term 1), E1 verdict.
- [Sella, Pham, Chaudhuri & Willcox 2023/2025] "Projection-based multifidelity linear regression for data-scarce (data-poor) applications" — https://arxiv.org/pdf/2508.08517 (AIAA 2023-0916 https://dx.doi.org/10.2514/6.2023-0916; ML for CSE 2025 https://link.springer.com/article/10.1007/s44379-025-00049-5) — used in: iteration_3 (title only, fetch failed), iteration_4 (term 1, fetched), E1/E2/E5 verdicts.
- [2025] "Transfer Learning for Benign Overfitting in High-Dimensional Linear Regression" (retain-plus-transfer) — https://arxiv.org/html/2510.15337 — used in: iteration_1 (term 2, fetched), E2 verdict.
- [2025] "Efficient multi-fidelity Gaussian process regression for noisy outputs and non-nested experimental designs" — https://arxiv.org/abs/2511.20183 — used in: iteration_1 (term 1, fetched), E2 verdict.
- [Kossaifi et al.] "Multi-Grid Tensorized Fourier Neural Operator for High-Resolution PDEs" (MG-TFNO) — https://arxiv.org/html/2310.00120 — used in: iteration_2 (term 1, fetched), E3a/E3b verdicts.
- [Li et al. 2024] "Multi-Resolution Active Learning of Fourier Neural Operators" (MRA-FNO) — https://arxiv.org/abs/2309.16971 (PMLR v238 li24k) — used in: iteration_2 (term 1, fetched).
- [2020] "Implicit Bias of Gradient Descent for MSE Regression with Two-Layer Wide Neural Networks" — https://arxiv.org/pdf/2006.07356 — used in: iteration_2 (term 2, fetched; extrapolation sentence flagged as fetch prose), E3c verdict.
- [2025] "NPN: Non-Linear Projections of the Null-Space for Imaging Inverse Problems" — https://arxiv.org/html/2510.01608 — used in: iteration_3 (term 3, fetched), E3c verdict.
- [Schwab/Antholzer/Haltmeier] "Deep null space learning for inverse problems" — https://iopscience.iop.org/article/10.1088/1361-6420/aaf14a — used in: iteration_3 (term 3, search-returned).
- [—] "Neural Network Training with Safe Regularization in the Null Space of Batch Activations" — https://link.springer.com/chapter/10.1007/978-3-030-61616-8_18 — used in: iteration_3 (term 3, search-returned).
- [2024] "Characterising harmful data sources when constructing multi-fidelity surrogate models" — https://arxiv.org/abs/2403.08118 (Artificial Intelligence, S0004370224001437) — used in: iteration_5 (term 2, fetched), E4 verdict.
- [Peherstorfer/Willcox/Gunzburger] "Survey of multifidelity methods" / "Review of multi-fidelity models" — https://arxiv.org/html/1609.07196v5 — used in: iteration_5 (term 1, search-returned).
- [—] "Overparameterized ReLU Neural Networks Learn the Simplest Models: Neural Isometry and Exact Recovery" — https://arxiv.org/pdf/2209.15265 — used in: iteration_4 (term 3, **search-returned synthesis only; fetch failed**), E3c verdict.
- [—] "Multifidelity Surrogate Models: A New Data Fusion Perspective" — https://arxiv.org/abs/2404.14456 — used in: iteration_4 (term 2, search-returned).
- [PRICAI 2025] "Efficient Selection of Low-Fidelity Data for Multi-fidelity Surrogate Models" — https://dl.acm.org/doi/10.1007/978-981-95-7072-0_32 — used in: iteration_4 (term 2, search-returned).
- [—] "A survey on multi-fidelity surrogates for simulators with functional outputs: unified framework and benchmark" — https://arxiv.org/pdf/2408.17075 — used in: iteration_5 (**fetch failed**; existence/venue only).
- [—] "Adaptivity and uncertainty of multi-fidelity surrogate models" (ReLU-gated latent GP, per-location LF borrowing) — https://hal.science/hal-04602579/document — used in: iteration_5 (term 2, search-returned).
- Reduced-basis affine-parameter-dependence context — https://link.springer.com/chapter/10.1007/978-88-470-2592-9_16, https://arxiv.org/pdf/1911.08954, https://arxiv.org/pdf/1705.08349 — used in: iteration_3 (term 2, search-returned).
- [PCA-RaNN] "Randomized neural operator for parametric PDEs …" — https://arxiv.org/pdf/2606.29440 — used in: iteration_1 (term 3, search-returned; fetched in `websearches/r2s1_direct/batch_2`).
- In-repo prior websearches (cited, not re-derived): `docs/reports/MF_Sharp_HighFreq_Report.md` lines 162–165 (Kennedy & O'Hagan co-kriging, Biometrika 87(1) 2000; NARGP, Perdikaris et al., DOI 10.1098/rspa.2016.0751) and `websearches/r2s3_lf_train_signal/batch_1/report.md` (D1/D2/D3 verdicts, arXiv:1903.00104, arXiv:2304.06972).

## Dead ends

- `training-free model selection between closed-form linear surrogate and neural network per dataset gating linearity test` → engine explicitly reported no match; the concept exists only inside the *harmful-LF-source* framing found in turn 5.
- `how much does low-fidelity data help ablation … matched budget with without` → returns are LF-*selection* and DoE papers; no matched-architecture neural field ablation at N_hf ≈ 5 (second independent miss, consistent with batch 1).
- Three PDFs were unparseable and are cited for nothing beyond title/venue: kiwi.oden Sella preprint (recovered as arXiv:2508.08517), arXiv:2209.15265 (search-returned synthesis used, flagged), arXiv:2408.17075.
- The fetch-model's "minimal activity outside the span of the training data" sentence for arXiv:2006.07356 is **not** a verbatim quote and is recorded as a lead only.

## For the brainstormer

The brainstormer MUST quote the prior-art verdict above for whatever it proposes.

1. **The linear/affine LF channel (E1) is preempted twice over** — LR-MFS
   (https://arxiv.org/abs/1705.02956) and, decisively, projection-based MF linear
   regression for data-scarce applications with POD field outputs and LF at
   parameters where no HF data exists (https://arxiv.org/pdf/2508.08517). Ship it
   if B1's 0.2427 makes it the honest ifc_poisson baseline, but **card it as a
   cited baseline implementation**, and expect a reviewer rebadge check.
2. **Batch 1's `novel` verdict for D3 (LF-as-parameter-coverage) is superseded.**
   Any card repeating it must instead quote E2's
   `preempted-but-MF-composition-open` row and name what is left open (neural,
   field-valued, certified-floor, condition-aligned-vs-disjoint contrast).
3. **The contribution left standing is the measurement (E5), not the estimator.**
   A card whose deliverable is a matched, budget-equal, per-dataset
   with/without-LF contrast for a neural condition→field surrogate at N_hf ≈ 5,
   priced against `state/noise_floor.json`'s certified `min_claimable_effect`
   (ifc_poisson 0.93770, panel 1.14187), is the only `novel` verdict in this
   batch and is exactly round-2 success criterion 1.
4. **Two of B1's three repairs are bug fixes, not science.** Nyquist-pinned mode
   clipping is MG-TFNO's standard "α independent of the discretization"
   convention (**preempted**); the per-rung scaler is unretrieved but runs
   *against* the discretization-invariance norm and can only be justified as an
   ifc_poisson-specific amplitude fix. Do not let either carry a card's novelty.
5. **The one network-side observation worth a card is the null-direction
   anatomy** (E3c's open half): the theory says min-norm/conservative
   extrapolation (https://arxiv.org/pdf/2006.07356); B1 measured 27.7% of the
   law's energy anti-aligned at cos −0.99. Framing that as a *measured violation
   of the implicit-bias prediction for neural field operators*, with the fix as
   an ablation arm, is defensible; framing the fix itself as new is not
   (https://arxiv.org/html/2510.01608 and the null-space-learning family).
6. **The per-dataset gate is mandatory engineering, not a claim**
   (https://arxiv.org/abs/2403.08118). Include it, cite it, and put the card's
   falsification clauses per dataset and per mechanism — B1's part 7 warns that
   a single panel-geomean threshold is what let B1's F3 flip on provisional
   floors.
7. **Standing caveats to carry**: helmholtz is report-only (best floor = zero
   field, 3.3441); pfc claims carry the band-limited-denominator caveat; and any
   ifc_poisson criterion-2 claim must state that the dataset is an exactly affine
   (reduced-basis-regime) map, so the claim is rank recovery, not operator
   learning.
