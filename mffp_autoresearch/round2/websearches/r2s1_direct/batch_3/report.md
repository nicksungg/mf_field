# Websearch Report — Stream `r2s1_direct`, Batch 3

**Stream**: `r2s1_direct` (class: gap)
**Batch**: 3
**Total iterations**: 5 (cap 5 — **CAP HIT**, noted in `iteration_5.md`)
**WebSearch calls**: 14 (turn 1: 3, turn 2: 3, turn 3: 3, turn 4: 3, turn 5: 2)
**WebFetch calls**: 13 — **5 usable as evidence**, 8 unusable
(HTTP: MDPI 403, RSPA 403, AGU 402, Springer 303 redirect-only-not-followed;
PDF text extraction failed: Hansen lecture notes, Jan Magnus JRM113a, Hastie
spca_JASA; low-information abstract page: arXiv:2303.08872).
**Cap hit**: yes (5/5)
**Process rule honoured**: **no arXiv `/pdf/` URL was fetched anywhere in this
loop** — only `/abs/` and `/html/` (and non-arXiv hosts).

## Search trace

### Turn 1 — map the three mechanism classes B2's part 7 points at
Terms: per-mode surrogate model selection for POD-coefficient regression;
predictable-mode vs energy-ranked basis selection; blending with a baseline /
optimal weights from error correlation.
- Per-mode **independent** regression on modal coefficients is standard practice
  ("K independent models employed, each associated with one modal coefficient")
  — *search return only*; the confirming fetch
  [https://link.springer.com/article/10.1007/s11831-026-10552-4] returned a
  **303 redirect to an IdP endpoint, not followed → cited for nothing**.
- Engine states no results exist for supervised/"predictable-mode" basis
  selection in the parameter→field surrogate literature (energy criteria only).
- Forecast-combination weight constraints paper: candidates treated
  **symmetrically**, "none receives special 'baseline' status", and it "does not
  explicitly derive optimal combination weights as functions of error
  correlation between candidates and a baseline"
  [cite (fetched): https://arxiv.org/html/2510.26456].
→ `iteration_1.md`

### Turn 2 — statistics vocabulary: Bates-Granger, PLS/supervised DR, per-mode CV
Terms: Bates-Granger two-forecast optimal weight; PLS vs POD supervised DR;
per-mode regressor family selected by CV.
- **Decisive fetched negative-space result**: the DR-in-surrogate-modeling review
  says "supervised methods produce more suitable topology representations of
  input–output maps", but "does **not** discuss or recommend selecting reduced
  bases specifically optimized for output predictability" and retains components
  by "captured variance … no discussion of selecting components based on their
  predictive contribution"
  [cite (fetched): https://pmc.ncbi.nlm.nih.gov/articles/PMC9633505/].
- Bates & Granger 1969 `w_opt = (Σ⁻¹1)/(1'Σ⁻¹1)` returned; confirming fetch
  (Hansen lecture PDF) **failed to extract text → cited for nothing**.
- arXiv:2303.08872 `/abs/` fetched but abstract-only → **not used as evidence**.
→ `iteration_2.md`

### Turn 3 — response-side predictable subspace, the ρ formula, per-mode hybrids
Terms: reduced-rank regression predictable response subspace; the explicit
`α*(ρ)` two-forecast formula; hybrid ROMs picking a regressor per mode.
- Engine draws the exact distinction we need (RRR predictable subspace vs
  response PCA "regardless of predictability") — *search return only*; the
  fetched RRR paper [https://arxiv.org/html/2601.07202] turned out to be about
  **predictor-side** PCs → **fetched but negative, not a preemption citation**.
- `α* = (σ₂² − ρσ₁σ₂)/(σ₁² + σ₂² − 2ρσ₁σ₂)` returned with no source attributed;
  confirming fetch [https://www.mdpi.com/2225-1146/7/3/39] **HTTP 403**.
- Third pass: "the typical approach … applying a **unified** regression strategy
  to the POD coefficients"; per-mode family selection not named.
→ `iteration_3.md`

### Turn 4 — refutation turn 1 (C1 / C2 / C3)
Terms: best regression model per mode by CV; post-hoc blending with a
climatology baseline as an evaluation artifact; low-variance-but-predictable
components / supervised PCA.
- C1: comparative ROM studies compare families **globally** (POD+PCE vs
  POD+PC-Kriging), never per mode. **Second miss.**
- C2: **No usable results** — engine states outright the topic (post-hoc
  blending inflating skill-score comparisons via decorrelation) is absent from
  returns. **First independent miss for C2's composition.**
- C3: supervised-PCA line squarely covers it ("PCs are not guaranteed to be
  informative of the response variable"; Bair & Tibshirani 2004); the confirming
  Hastie PDF **failed text extraction → cited for nothing** (fetched citation
  obtained in turn 5 instead).
→ `iteration_4.md`

### Turn 5 — refutation turn 2, then verdict (final; cap hit)
Terms: mode-wise selection of interpolation method per POD mode; multi-model
blending weights from error correlation (GRL 2025).
- C1 **third miss**: every "mode-wise" hit interpolates the **modes/subspaces**
  themselves or selects **snapshots**, not a per-mode regressor family. RSPA
  confirming fetch **HTTP 403**.
- **Mechanism citation for C2 secured**: `w_BG = (1'Σ⁻¹1)⁻¹1Σ⁻¹` from the
  prediction-error covariance, weights "can occasionally fall outside the [0,1]
  range", referenced to **Bates & Granger 1969**
  [cite (fetched): https://search.r-project.org/CRAN/refmans/MuMIn/html/BGweights.html].
  The AGU GRL 2025 blending paper fetch returned **HTTP 402 → cited for nothing**.
- **Citation for C3 secured**: SPCA "aim[s] to incorporate label information into
  PCA, so that the extracted features are more useful for a prediction task of
  interest"
  [cite (fetched): https://arxiv.org/abs/2011.05309, Ritchie et al. 2020].
→ `iteration_5.md` (contains the full verdict)

## Prior-art verdict

| Candidate direction | Verdict | Citations (fetched this loop) | What remains open |
|---|---|---|---|
| **C1** — per-mode **out-of-fold model-family selection** over a bank ({affine, quadratic, kernel ridge, k-NN}) for condition→POD-coefficient regression, priced against a trained decoder **before** any shared post-hoc stage | **`preempted-but-MF-composition-open (cite)`** | ASAMS whole-model automatic selection by grid+LOOCV over **trained** candidates — https://pmc.ncbi.nlm.nih.gov/articles/PMC7571090/ (fetched in batch 2); McGreivy & Hakim weak baselines — https://arxiv.org/abs/2407.07218 (fetched in batch 2); POD-NN/PCA-Net — https://arxiv.org/html/2504.18513v1/ (batch 1) | One-regressor-per-mode is **presumed prior art (do not claim)** — stated by three engine passes, **never fetched** (Springer 303, RSPA 403). Open after 3 targeted refutation searches with zero named sources: per-mode **family** selection by OOF R², used as the standing ~10¹–10²-parameter control arm a 10⁷-parameter decoder must beat on a **copy-LF-skill panel under the stripped no-LF-at-test view**, with the per-mode ORACLE ceiling reported. Bound to state: Lanthaler et al. https://arxiv.org/abs/2210.01074 (linear reconstruction inefficient for discontinuous operators — 4/6 panel datasets). |
| **C2** — **instrument/protocol**: a shared post-hoc baseline-blend / floor-hedge stage pays off as a closed form in ρ, so comparisons decided there are **decorrelation** verdicts; hence pre-stage scoring + blend-base decorrelation audit as a benchmark requirement | **`preempted-but-MF-composition-open (cite)`** — **best-supported novel composition for B3** | Bates & Granger (1969) minimum-variance combination `w_BG=(1'Σ⁻¹1)⁻¹1Σ⁻¹` from the prediction-error covariance, weights may leave [0,1] — https://search.r-project.org/CRAN/refmans/MuMIn/html/BGweights.html ; weight-constraint/covariance-shrinkage theory, candidates treated symmetrically with "none receives special 'baseline' status" — https://arxiv.org/html/2510.26456 | The **mechanism is preempted and must be named as Bates-Granger combination in the card.** Open: its use as an **evaluation-protocol defect detector** — appending a shared floor-blend stage to every arm of a benchmark converts an architecture comparison into a decorrelation comparison (arm class that IS the base at ρ=1.0000 unpayable; decisive cell reverses by 2.07–7.15× mce; λ ≤ 0.25 ⇒ reporting the base). One targeted search returned **no usable results**; the fetched combination literature never treats a candidate as a benchmark's shared post-hoc stage. |
| **C3** — identified-**SET** indexing / predictability-ordered output basis (fit the head on condition-identifiable modes, not the leading energy window) | **`preempted (cite)`** | Supervised PCA "aim[s] to incorporate label information into PCA, so that the extracted features are more useful for a prediction task of interest" — https://arxiv.org/abs/2011.05309 (Ritchie et al. 2020); "supervised methods produce more suitable topology representations of input–output maps" — https://pmc.ncbi.nlm.nih.gov/articles/PMC9633505/ | Nothing claimable. Thin residue only: the fetched DR review "does not discuss or recommend selecting reduced bases specifically optimized for output predictability" and retains components by "captured variance"; the one RRR paper fetched (https://arxiv.org/html/2601.07202) is predictor-side. SPCA/PLS/reduced-rank regression own the idea. **Ship as a bug fix / instrument, never as a contribution** (upgrades batch 2's "presumed prior art" to preempted-with-citation). |
| **C4** — H2 test (decoder advantage = spatial inductive bias reaching low-energy, low-OOF-R² modes) via projecting decoder predictions onto the fit-fold basis | **NOT PRIOR-ART-CHECKED THIS LOOP** (cap reached) | — | Must not be headlined as novel. Admissible only as a diagnostic inside a C1/C2-claimed card, and it requires the build gate B2 missed: every decoder arm ships `preds_test.npz`. |

## Citations summary

- [Weight constraints in forecast combination 2025] "A theoretical comparison of weight constraints in forecast combination and model averaging" — https://arxiv.org/html/2510.26456 — **fetched**, `iteration_1.md`
- [Dimensionality Reduction in Surrogate Modeling 2022] "Dimensionality Reduction in Surrogate Modeling: A Review of Combined Methods" (Data Sci. Eng.) — https://pmc.ncbi.nlm.nih.gov/articles/PMC9633505/ — **fetched**, `iteration_2.md`
- [Goto et al.] "Principal component-guided sparse reduced-rank regression" — https://arxiv.org/html/2601.07202 — **fetched, NEGATIVE for our question** (predictor-side PCs), `iteration_3.md`
- [Bates & Granger 1969, via CRAN MuMIn docs] "BGweights: Bates-Granger minimal variance model weights"; primary ref *The combination of forecasts*, J. Oper. Res. Soc. 20, 451–468 — https://search.r-project.org/CRAN/refmans/MuMIn/html/BGweights.html — **fetched**, `iteration_5.md`
- [Ritchie, Balzano, Kessler, Sripada, Scott 2020] "Supervised PCA: A Multiobjective Approach" — https://arxiv.org/abs/2011.05309 — **fetched**, `iteration_5.md`
- *Search-return only (NOT citations, recorded for audit)*: per-mode independent modal regression as standard practice (`iteration_1.md`, `iteration_2.md`, `iteration_3.md`); `α*=(σ₂²−ρσ₁σ₂)/(σ₁²+σ₂²−2ρσ₁σ₂)` (`iteration_3.md`); Bair & Tibshirani 2004 supervised PCA origin and "top PCs discard valuable information" (`iteration_4.md`); Wang et al. GRL 2025 blending (`iteration_5.md`).
- *Carried from earlier loops (fetched there, not re-fetched here; used as context/bounds only)*: ASAMS https://pmc.ncbi.nlm.nih.gov/articles/PMC7571090/ and McGreivy & Hakim https://arxiv.org/abs/2407.07218 and Wiener gain https://www.emergentmind.com/topics/non-causal-wiener-filter (batch 2); POD-NN/PCA-Net https://arxiv.org/html/2504.18513v1/ , REALM https://arxiv.org/html/2512.18595 , conditional-mean barrier https://arxiv.org/html/2605.28076 (batch 1); Lanthaler et al. https://arxiv.org/abs/2210.01074 (in-repo `docs/reports/MF_Sharp_HighFreq_Report.md:180`).

**Failed / discarded fetches (cited for nothing)**: https://link.springer.com/article/10.1007/s11831-026-10552-4 (303 redirect-only, not followed); https://www.mdpi.com/2225-1146/7/3/39 (403); https://royalsocietypublishing.org/rspa/article/480/2283/20230655/101080/Multi-fidelity-reduced-order-surrogate (403); https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2024GL111622 (402); https://users.ssc.wisc.edu/~behansen/390/390Lecture23.pdf , https://www.janmagnus.nl/papers/JRM113a.pdf , https://hastie.su.domains/Papers/spca_JASA.pdf (PDF text extraction failed); https://arxiv.org/abs/2303.08872 (abstract-only, low information).

## Dead ends

- `post-hoc blending with climatology baseline inflates skill score comparison … decorrelation artifact` → **no usable results**; engine declared the topic absent. This is exactly *why* C2's composition survives.
- `mode-wise selection of interpolation method for each POD mode …` → every hit is mode/subspace **interpolation** (MRPWI, manifold interpolation) or adaptive **snapshot** selection; nothing about per-mode regressor family choice.
- `reduced-rank regression predictable subspace of multivariate response …` → the fetched paper is predictor-side; the response-side statement exists only as an unattributed engine paraphrase. Left as **presumed prior art** (consistent with C3's verdict anyway).
- `optimal combination weight formula (σ₂²−ρσ₁σ₂)/(…)` → formula returned three times, source never fetchable (403/402/PDF). The covariance form via BGweights is the citation used instead.

## For the brainstormer

1. **Quote the verdict row you are actually proposing.** If B3's scored content
   is the closed-form per-mode head, quote **C1
   (`preempted-but-MF-composition-open`)** and declare in the card that
   *one regressor per POD mode is presumed prior art* and that ASAMS
   (https://pmc.ncbi.nlm.nih.gov/articles/PMC7571090/) already does automatic
   model selection over **trained** candidates. The contribution is the
   measurement (a ~10-parameter per-mode OOF-selected map vs a 1.6e7-parameter
   FiLM decoder, under copy-LF skill on the stripped view), not the estimator.
2. **The strongest available contribution shape is C2** — the instrument claim.
   Its mechanism is **Bates & Granger (1969)** minimum-variance combination
   (https://search.r-project.org/CRAN/refmans/MuMIn/html/BGweights.html) and must
   be named as such in the card (the reviewer's rebadge check, program.md §5.10,
   will look for exactly this). What is open is the *benchmark-protocol* reading:
   a shared post-hoc floor-blend stage makes cross-arm comparisons decorrelation
   verdicts. Ship it with the pre-stage raw column beside the post-stage one
   (B2 T2-F1: on allen_cahn the raw comparison has the **opposite sign** and 4.3×
   the magnitude).
3. **Do not claim predictability-ordered basis selection (C3).** It is now
   `preempted (cite)` — supervised PCA (https://arxiv.org/abs/2011.05309) and the
   supervised-DR review (https://pmc.ncbi.nlm.nih.gov/articles/PMC9633505/).
   The set-vs-window repair is a **correctness fix** (`tools/selection_set_vs_window_audit.py`),
   worth 5.62× mce on cahn_hilliard, and belongs in the recipe as a bug fix.
4. **C4 (the H2 spatial-inductive-bias test) carries no prior-art verdict** —
   the cap was reached first. It may appear only as a diagnostic, and only if the
   card makes `preds_test.npz` per decoder arm a **build gate** (B2 part 7 item 4).
5. **Design the falsification per dataset and on 3 datasets, not 6.** Certified
   `min_claimable_effect` (`state/noise_floor.json`): cahn_hilliard 0.09125, pfc
   0.2130, allen_cahn 0.8797, fisher_kpp 0.00071, ifc_poisson 0.9377, helmholtz
   2.9530 (report-only, zero-floor column mandatory). B2 part 7 item 5: pfc and
   fisher_kpp are **dead cells** in this view (0/30 leading POD coefficients
   identifiable OOF after DC removal; oracle blend λ = 0.00) and ifc_poisson is
   N_hf = 5 anecdote-grade — so a "≥ k of 5" clause is really "≥ k of 3" and must
   be written that way. No single-seed panel-geomean threshold (panel mce 1.1419).
6. **Constraints that will otherwise sink the card**: ADR r2-0003 (condition
   incomplete on pfc/fisher_kpp/allen_cahn — no clause may assume skill→1 there);
   mandatory floor arms NN/train_mean/zero plus `dc_only`, with the **blend bases
   decorrelation-audited before use** (a closed-form condition head IS `dc_only`
   at ρ = 1.0000 on allen_cahn); and the anchor to quote verbatim — best-floor
   panel geomean **23.0636**, per-dataset floors 3.3441 / 59.8118 / 269.1959 /
   11.9931 / 23.1803 / 10.0549. Also: **do not widen the Wiener grid** (B2 part 7
   item 3 — the [0,2] edge gain is a 40-sample calibration overfit; the
   least-squares-optimal band-3 gain is a shrink to 0.64).
