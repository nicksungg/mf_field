# Websearch Report — Stream `r2s1_direct`, Batch 2

**Stream**: `r2s1_direct` (class: gap)
**Batch**: 2
**Total iterations**: 5 (cap 5 — **CAP HIT**, noted in `iteration_5.md`)
**WebSearch calls**: 13 (turn 1: 3, turn 2: 3, turn 3: 2, turn 4: 3, turn 5: 2)
**WebFetch calls**: 12 — 8 usable, 4 unusable (2 PDFs unreadable:
arXiv:2208.01518, arXiv:1405.5170, Numerical-Recipes Wiener PDF [3rd]; 1 HTTP 403:
S0957417415007162; 1 redirect-only notice re-issued successfully). **1 fetch
(arXiv:2601.13308) was DISCARDED as prompt-echo and is cited for nothing.**
**Cap hit**: yes (5/5)

## Search trace

### Turn 1 — map the three B2 mechanism classes (B1 part 7 says: stop buying capacity, spend on identification + calibration)
Terms: band-wise gain calibration / spectral shrinkage of neural operators;
small-parameter closed-form baselines vs neural operators; training-free
selection of surrogate model form.
- TF-SNO's band gating is **learned end-to-end inside the architecture**, not a
  post-hoc held-out fit, and shows no shrink-to-zero band gains
  [cite (fetched): https://arxiv.org/pdf/2606.21189].
- **PCA-RaNN**: random features + **closed-form ridge** onto **PCA
  coefficients**, benchmarked against DeepONet/FNO — the published form of B1's
  "~150-parameter closed-form head"
  [cite (fetched): https://arxiv.org/pdf/2606.29440].
- Training-free model-form selection: only the classical singular-value-energy
  rank criterion returned; the engine reported no match for the actual question.
→ `iteration_1.md`

### Turn 2 — identifiable rank, relative-metric shrinkage, regime mixtures
Terms: predictable-POD-mode count from parameters; relative-L2 metric and
output shrinkage; regime classification / MoE before surrogate prediction.
- Aggregated return: "references suggest reducing the modes of a POD based on
  the R^2-Score of the POD coefficients surrogate models" — confirming fetch
  **FAILED** (https://arxiv.org/pdf/2208.01518 unreadable), so no citation.
- **arXiv:2601.13308 "Scaling laws for amplitude surrogates" is a
  particle-physics amplitudes paper — a homonym. Fetch summary echoed my prompt;
  DISCARDED, cited for nothing** (program.md §13.3).
- MoE surrogates are the established answer to regime-piecewise responses
  [search return: https://www.sciencedirect.com/science/article/abs/pii/S1270963815000760].
→ `iteration_2.md`

### Turn 3 — settle R^2-rank truncation and post-hoc point-prediction gains
Terms: POD truncation by coefficient-surrogate R^2; post-hoc multiplicative
gain correction of point predictions.
- Engine states plainly it found no literature truncating a POD basis by
  coefficient-regression R^2 "as an alternative to singular value energy-based
  selection" — **directly contradicting turn 2's snippet; thread declared
  UNRESOLVED, no citation either way**.
- **Decisive hit**: post-training corrections applied to a **frozen**
  forecaster, selected on held-out data — affine (`a*=Cov(Y,Z)/Var(Z)`), "scale
  amplitude: globally rescales the forecast around its mean", piecewise
  scaling — but "**none explicitly target multiplicative gains per frequency
  band or spectral component**"
  [cite (fetched): https://arxiv.org/html/2505.15354].
→ `iteration_3.md`

### Turn 4 — refutation turn 1 (E1 / E3 / E2)
Terms: wavenumber-band rescaling of predicted spectra using validation data;
neural operators vs simple baselines critique; magnitude-direction output
parameterization.
- Term 1: **No usable results** (returns are turbulence-physics spectra) — third
  independent miss for the band-resolved post-hoc gain.
- **McGreivy & Hakim**: 79% (60/76) of ML-for-PDE papers claiming to beat
  standard methods use a weak baseline; but a weak baseline there means an
  **inadequate classical numerical solver**, and the paper "does not specify
  particular baseline protocols or reporting requirements"
  [cite (fetched): https://arxiv.org/abs/2407.07218].
- Magnitude/direction decoupling in the literature is about **weight vectors**
  [search return: https://arxiv.org/abs/2606.25971], not output fields.
- https://arxiv.org/pdf/2601.11428 fetched but returned only hedged
  metadata-level description — **recorded low-information, not used as evidence**.
→ `iteration_4.md`

### Turn 5 — refutation turn 2, then verdict (final; cap hit)
Terms: Wiener filter as optimal per-frequency gain / spectral shrinkage;
meta-features + AutoML model selection for surrogates.
- **B1's band-gain fit is an empirical non-causal Wiener filter**,
  `H_nc = S_hy/S_yy`; and "SW adapts the shrinkage factor to local, data-driven
  SNR estimates ... **hard-thresholds frequency components with low SNR**" —
  i.e. B1's "all non-DC gains go to zero" is a named, old phenomenon
  [cite (fetched): https://www.emergentmind.com/topics/non-causal-wiener-filter].
- **ASAMS** automatically selects the surrogate model type but by grid search +
  LOOCV over **trained** candidates — "requires training candidate models ...
  rather than purely statistical analysis of the raw dataset"
  [cite (fetched): https://pmc.ncbi.nlm.nih.gov/articles/PMC7571090/].
→ `iteration_5.md` (contains the full verdict)

## Prior-art verdict

| Candidate direction | Verdict | Citations (fetched this loop) | What remains open |
|---|---|---|---|
| **E1** — out-of-fold **per-spectral-band gain calibration** of a frozen condition→field predictor's POINT output, gain vector read as an identifiability diagnostic | **`preempted (cite)`** at the mechanism level | Wiener gain `H_nc=S_hy/S_yy` + Self-Wiener low-SNR hard-thresholding — https://www.emergentmind.com/topics/non-causal-wiener-filter ; frozen-model post-hoc affine/amplitude correction fitted on held-out data, `a*=Cov(Y,Z)/Var(Z)` — https://arxiv.org/html/2505.15354 ; in-architecture band gating — https://arxiv.org/pdf/2606.21189 | (i) **band-resolved, out-of-fold, post-hoc** gains on a learned PDE surrogate's point output — the band gates found are in-architecture or need test-time observations; (ii) the fitted gain vector as an **identifiability diagnostic**; (iii) any of it under a **per-sample relative-L2** score where shrinkage is the scored optimum. Use as machinery, never as the claimed method. |
| **E2** — **training-free statistic-selected output parameterization** (centering form by `\|\|mean field\|\|/geomean\|\|y\|\|`; rank by condition-identifiable POD rank) | **`preempted-but-MF-composition-open (cite)`** | ASAMS automatic surrogate-model selection, grid+LOOCV over **trained** candidates — https://pmc.ncbi.nlm.nih.gov/articles/PMC7571090/ ; PCA+ridge coefficient regression — https://arxiv.org/pdf/2606.29440 ; (batch 1) POD-NN/PCA-Net — https://arxiv.org/html/2504.18513v1/ | Selecting a **field predictor's output parameterization** from statistics computable on the train split **without training any candidate**, pre-registered per dataset. Not found. Caveat: rank-truncation-by-predictability is **presumed prior art** (unresolved, see below). |
| **E3** — **mandatory ~10^2-parameter closed-form control arm** every capacity claim must beat, with the surviving capacity benefit localized to `sharp__cahn_hilliard` | **`preempted-but-MF-composition-open (cite)`** | McGreivy & Hakim, weak baselines, Nature Mach. Intell. 2024 — https://arxiv.org/abs/2407.07218 ; PCA-RaNN closed-form ridge control arm — https://arxiv.org/pdf/2606.29440 ; (batch 1) REALM compares against no trivial baselines — https://arxiv.org/html/2512.18595 | McGreivy & Hakim's "weak baseline" = an inadequate **classical numerical solver**, and it prescribes **no baseline protocol**. A standing requirement to beat a ~10^2-parameter closed-form arm on a **copy-LF-skill** panel, plus per-dataset localization of where capacity is worth anything, is unprescribed. **Best-supported contribution shape for B2.** |
| **E4** (secondary) — regime/class-conditional prediction + **per-class scoring** on the two-population pfc | **`preempted (cite — SEARCH-RETURN ONLY, NOT FETCHED; PROVISIONAL)`** | MoE surrogates for regime-piecewise responses — https://www.sciencedirect.com/science/article/abs/pii/S1270963815000760 (**search return, not fetched**) | Per-class **scoring of a benchmark split** as a reporting requirement was not returned. **Do not headline E4 without a batch-3 confirming fetch**; B1's cross-stream note 4 already demands per-class pfc scoring for internal validity regardless of novelty. |

**Unresolved thread (declared)**: whether truncating a POD basis at the
*predictable* rank (R^2 of the coefficient surrogate) is published could not be
settled in two turns (iterations 2 and 3 returned contradictory snippets; both
confirming fetches failed). **Treat identifiable-rank truncation as presumed
prior art and do not claim it.**

## Citations summary

- [TF-SNO 2026] "Time-Frequency Gated Spectral Neural Operators for Learning Non-Stationary PDEs" — https://arxiv.org/pdf/2606.21189 — **fetched**, iteration_1.md
- [PCA-RaNN 2026] "Randomized neural operator for parametric PDEs with fast training and conformal uncertainty quantification" — https://arxiv.org/pdf/2606.29440 — **fetched**, iteration_1.md
- [Post-Training Corrections 2025] "Post-Training Corrections for Improved Time-Series Forecasting" — https://arxiv.org/html/2505.15354 — **fetched**, iteration_3.md
- [McGreivy & Hakim 2024] "Weak baselines and reporting biases lead to overoptimism in machine learning for fluid-related partial differential equations", Nature Mach. Intell. — https://arxiv.org/abs/2407.07218 (journal: https://www.nature.com/articles/s42256-024-00897-5) — **fetched**, iteration_4.md
- [Non-causal Wiener filter / Self-Wiener] topic page with `H_nc=S_hy/S_yy` and the low-SNR hard-threshold quote — https://www.emergentmind.com/topics/non-causal-wiener-filter — **fetched**, iteration_5.md
- [ASAMS 2020] "Adaptive Sequential Sampling and Automatic Model Selection for AI Surrogate Modeling" — https://pmc.ncbi.nlm.nih.gov/articles/PMC7571090/ — **fetched**, iteration_5.md
- [Bartov?/aerodynamic MoE] "Surrogate models and mixtures of experts in aerodynamic performance prediction for aircraft mission analysis" — https://www.sciencedirect.com/science/article/abs/pii/S1270963815000760 — *search return only*, iteration_2.md
- [MD-decoupling 2026] "Improving Neural Network Training by Decoupling the Magnitude and Direction of Weight Vectors" — https://arxiv.org/abs/2606.25971 — *search return only*, iteration_4.md
- [FreqNO-DPS] "Correcting Neural Operator Spectral Bias via Diffusion Posterior Sampling with Sparse Observations" — https://arxiv.org/html/2606.03936 — *search return this loop*, iteration_1.md (also in-repo `docs/reports/MF_Leaderboard_Beaters_2026_Report.md:32,102`)
- [Optimal spectral shrinkage] "Optimal spectral shrinkage and PCA with heteroscedastic noise" — https://arxiv.org/pdf/1811.02201 — *search return only*, iteration_5.md
- Carried from batch 1 (`websearches/r2s1_direct/batch_1/report.md`, fetched there, not re-fetched here): conditional-mean barrier https://arxiv.org/html/2605.28076 ; REALM https://arxiv.org/html/2512.18595 ; PODNO https://arxiv.org/html/2504.18513v1/ ; RB-DeepONet https://arxiv.org/abs/2511.18260 ; Lanthaler https://arxiv.org/abs/2210.01074 (via `docs/reports/MF_Sharp_HighFreq_Report.md:180`).

**Discarded / not evidence** (recorded for audit):
- https://arxiv.org/pdf/2601.13308 — particle-physics "amplitudes"; fetch summary echoed the prompt. **Cited for nothing.**
- https://arxiv.org/pdf/2601.11428 — fetch returned hedged metadata only. **Cited for nothing.**
- Failed fetches: https://arxiv.org/pdf/2208.01518 , https://arxiv.org/pdf/1405.5170 , https://123.physics.ucdavis.edu/week_5_files/filters/wiener_filter.pdf (unreadable PDFs); https://www.sciencedirect.com/science/article/am/pii/S0957417415007162 (HTTP 403).

## Dead ends

- `wavenumber band dependent rescaling of predicted field spectrum using validation data ...` → turbulence-physics spectra only; no post-hoc surrogate correction. (Third miss — this is *why* E1's composition survives.)
- `truncate POD basis by R2 score of coefficient regression ...` → engine reports the combination is unliterature'd, contradicting iteration 2's snippet; both fetches failed. Left UNRESOLVED on purpose.
- `choosing output parameterization magnitude direction decomposition ...` → weight-vector decoupling and parameter decomposition; nothing about output-field parameterization chosen from data statistics.
- `relative L2 error metric biases predictions toward smaller magnitude ...` → generic ridge/James-Stein material plus one homonym paper; confirms r2s4-B2's D3 independently but adds no new mechanism.

## For the brainstormer

1. **Quote the verdict, and quote the right row.** If the card contains a
   per-band gain calibration stage, it is **`preempted (cite)`** — the operation
   is the **Wiener filter** (`H_nc=S_hy/S_yy`,
   https://www.emergentmind.com/topics/non-causal-wiener-filter) and the
   "non-DC gains collapse to zero" result is Self-Wiener's low-SNR
   hard-thresholding. Ship it as machinery and *name it as a Wiener gain in the
   card*; the reviewer's rebadge check (program.md §5.10) will look for exactly
   this. Post-hoc global affine/amplitude correction of a frozen model is also
   published (https://arxiv.org/html/2505.15354).
2. **The strongest available contribution shape is E3** — the standing
   ~10^2-parameter **closed-form control arm** plus per-dataset localization of
   where capacity is worth anything. Motivation cites McGreivy & Hakim
   (https://arxiv.org/abs/2407.07218, 79%/60-of-76 weak baselines) while stating
   the difference: their weak baseline is a classical *solver*, they prescribe
   no protocol, and REALM (batch 1) compares against no trivial baselines at
   all. The control arm's architecture is PCA-RaNN prior art
   (https://arxiv.org/pdf/2606.29440) and must be declared as a baseline.
3. **E2 is claimable only as a rule, not as ingredients.** Automatic surrogate
   model selection is published but **trains its candidates** (ASAMS,
   grid+LOOCV, https://pmc.ncbi.nlm.nih.gov/articles/PMC7571090/). A
   **training-free** selection rule for the *output parameterization* is open —
   but pre-register the rule and its thresholds in the recipe, or it is
   post-hoc curve-fitting on 6 datasets.
4. **Do not claim identifiable-rank truncation.** Two search turns gave
   contradictory answers and both confirming fetches failed; it is **presumed
   prior art**. `tools/condition_identifiable_rank.py` is an instrument here,
   not a contribution.
5. **Design the falsification per-dataset, not on the geomean.** B1's card part
   7 item 4 is explicit: the B1 pass/fail (19.6444 vs a 19.60 threshold) was
   decided inside the certified `min_claimable_effect` of 1.1419
   (`state/noise_floor.json`). Use per-dataset `min_claimable_effect` values
   (cahn_hilliard 0.0912, pfc 0.2130, allen_cahn 0.8797, fisher_kpp 0.00071,
   ifc_poisson 0.9377, helmholtz 2.9530 → helmholtz stays report-only) or run
   the 3-seed protocol.
6. **Two constraints that will otherwise sink the card**: (a) ADR r2-0003 — on
   pfc/fisher_kpp/allen_cahn the condition vector is incomplete, so any
   falsification clause assuming skill→1 is invalid there; (b) the mandatory
   floor arms (NN / train_mean / zero) plus the DC-only ridge (B1 finding 3,
   which beat a 14.4 M-parameter decoder on pfc) belong in the arm set — an arm
   that does not beat a per-sample **constant field** is measuring mean-level
   regression, and batch 1 established that reporting trivial floors at all is
   itself unprecedented in the fetched benchmark literature (REALM).
