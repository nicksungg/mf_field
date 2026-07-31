# Websearch Report — Stream `r2s4_diag`, Batch 2

**Stream**: `r2s4_diag` (class: diag)
**Batch**: 2
**Total iterations**: 5 (CAP HIT)
**WebSearch calls**: 15 (3 per iteration x 5; no turn exceeded 3 terms)
**WebFetch calls**: 13 (9 usable, 4 failed: `link.springer.com/chapter/...` 303 auth
redirect, `arxiv.org/pdf/2205.11412` undecodable PDF, `ncbi.nlm.nih.gov/pmc/...PMC12185630`
301 cross-host redirect, `arxiv.org/abs/2104.08878` returned abstract-only and the
fetcher declined to attribute claims). <=2 fetches per term throughout.
**Cap hit**: YES — 5/5 iterations used.

## Search trace

### Turn 1 — Q1: does a published aleatoric-ceiling estimator exist for our regime?
Terms: (1) difference-based noise-variance estimation in high dimensions;
(2) nearest-neighbour aleatoric uncertainty; (3) intrinsic stochasticity in
parametric PDE surrogates.
- B1's matched-pair-extrapolation estimator **is the differogram**, published for
  model selection [cite: https://www.sciencedirect.com/science/article/abs/pii/S0925231205001682].
- The 19-dim failure B1 hit is a known property of the estimator class: "the first
  order difference based estimator that achieves minimax rate … in the one-dimensional
  case does not do the same in the high dimensional case … the optimal order of
  differences depends on the number of dimensions" (SNIPPET; the review chapter's
  fetch was blocked) [cite: https://link.springer.com/chapter/10.1007/978-3-032-07178-1_19].
- High-dimensional noise-variance estimation is an active named problem
  [cite: https://arxiv.org/abs/1711.09208, FETCHED].
- TRINE estimates intrinsic noise without repeated measurements at identical inputs
  but is 1-2D, trajectory-based, "no explicit discussion of high-dimensional
  scalability" [cite: https://arxiv.org/html/2511.13701, FETCHED].
-> `iteration_1.md`

### Turn 2 — Q2: is shrink-toward-own-mean a published calibration operation?
Terms: (1) post-hoc shrinkage / calibration in regression; (2) conditional-mean
collapse in neural operators; (3) amplitude/spectral recalibration post-processing.
- The phenomenon B1's lambda* diagnoses is stated verbatim in the literature: "A network
  trained with mean-squared error converges to the conditional expectation … The
  resulting prediction is over-smoothed by construction … This is not a training
  failure — it is the *optimal* MSE solution given the information available"
  [cite: https://arxiv.org/html/2604.20061v1, FETCHED].
- Every published post-hoc surrogate calibrator found rescales variance/interval
  width and leaves the point prediction alone: "the central amplitude A_NN remains
  unchanged"; needs ~1000+ calibration points [cite: https://arxiv.org/html/2607.01354v1, FETCHED].
-> `iteration_2.md`

### Turn 3 — Q4: the overfitting-anatomy direction batch 1 deferred
Terms: (1) generalization-gap / bias-variance-noise decomposition at small N;
(2) effective sample size / redundancy; (3) HF sample complexity for operator learning.
- The decomposition is textbook and generic; its **noise** term is precisely B1's
  aleatoric barrier (unifying framing, not a new method).
- Still **no PDE-domain n_eff estimator** after two batches; the nearest handle is
  redundancy pruning, whose abstract defines no such statistic
  [cite: https://arxiv.org/abs/1905.12737v1, FETCHED].
- The load-bearing negative result: "No method to approximate Lipschitz operators
  based on m linear samples can achieve algebraic convergence rates in m" absent fast
  covariance decay [cite: https://arxiv.org/abs/2410.23440, FETCHED].
-> `iteration_3.md`

### Turn 4 — refutation pass 1 (ENOUGH declared on field survey)
Terms aimed at D2 (active subspace before neighbour matching), D1 (matched-budget MF
ablation), D1-methodology (pre-registered negative controls).
- Closest published relative of D1: "the first study of empirical scaling laws for
  multi-fidelity neural surrogate datasets", dataset axis decomposed into compute
  budget and composition [cite: https://arxiv.org/abs/2511.01830, FETCHED abstract].
- Active subspaces are published dimension reduction, "robust with respect to noise or
  lack of smoothness" [cite: https://arxiv.org/pdf/2304.14142, FETCHED]; the
  active-subspace-**before**-kNN combination appeared only as an unconfirmed snippet.
- No source found pre-registers an ablation's null datasets **because a measured
  aleatoric ceiling says so**.
-> `iteration_4.md`

### Turn 5 — refutation pass 2 (CAP)
Terms aimed at D3 (James-Stein), D1-mechanism (PI that fails to transfer), D2 reworded
(Bayes error for field-valued outputs).
- "the apparent superiority of a privileged teacher does not always correspond to
  transferable capability, but may instead arise from information asymmetry" — the
  **"privilege illusion"**, separated experimentally via an advantage-gap ablation
  [cite: https://arxiv.org/html/2606.30626v1, FETCHED].
- "a consistent and severe asymmetric transfer of negative knowledge to the student"
  [cite: https://arxiv.org/abs/2510.12615, FETCHED].
- Bayes-error estimation for **field-valued** outputs at few/paired samples: **no
  usable results** (second independent framing to fail).
-> `iteration_5.md` (contains the full verdict text)

## Prior-art verdict

| Candidate direction | Verdict | Citations (fetched this loop) | What remains open |
|---|---|---|---|
| **D1** — value-of-LF accounting: matched architecture/budget +/- LF-training-signal, helmholtz-first (only certified headroom), fisher_kpp/pfc/allen_cahn **pre-registered as nulls** by B1's measured aleatoric barrier | `preempted-but-MF-composition-open (cite)` | MF scaling laws — https://arxiv.org/abs/2511.01830 ; DOPD "privilege illusion" — https://arxiv.org/html/2606.30626v1 ; negative asymmetric transfer — https://arxiv.org/abs/2510.12615 ; (batch 1) Yang et al. non-monotone LUPI law — https://arxiv.org/abs/2209.08754 | Nothing found pre-registers the null datasets **from a measured training-free ceiling**, nor uses LF *fields* as privileged info for a *field-valued* output scored in copy-LF skill. Concrete adoptable design: DOPD's advantage-gap split (capability gap vs information gap) ported to fields. |
| **D2** — ceiling estimator with support at 19 condition dims and N_hf = 5 | `preempted (cite)` for the method class; composition open for this regime | differogram — https://www.sciencedirect.com/science/article/abs/pii/S0925231205001682 ; high-dim noise variance — https://arxiv.org/abs/1711.09208 ; review (snippet, fetch blocked) — https://link.springer.com/chapter/10.1007/978-3-032-07178-1_19 ; NNVE — https://www.tandfonline.com/doi/abs/10.1198/016214502388618780 ; active subspaces — https://arxiv.org/pdf/2304.14142 ; TRINE — https://arxiv.org/html/2511.13701 ; hard limit — https://arxiv.org/abs/2410.23440 | The 19-dim failure is a **known theorem-level property**, not a bug. No fetched source estimates irreducible error for a **field-valued** output at ~400 samples / 19 dims, and none at N = 5 (two framings failed). Frame as "compose active-subspace projection with a named variance estimator; report where support fails". At N_hf = 5, arXiv:2410.23440 says no ceiling claim is defensible. |
| **D3** — mandatory post-hoc shrinkage-toward-own-mean arm; lambda* as diagnostic | `preempted-but-MF-composition-open (cite)` | MSE->conditional mean — https://arxiv.org/html/2604.20061v1 ; FALCON (variance-only post-processing, ~1000-pt calibration set) — https://arxiv.org/html/2607.01354v1 ; James-Stein/ridge (snippet-level) — https://efron.ckirby.su.domains/other/CASI_Chap7_Nov2014.pdf , https://web-docs.stern.nyu.edu/old_web/emplibrary/shrink3.pdf ; FreqNO-DPS — https://arxiv.org/pdf/2606.03936 | The shrinkage operation is James-Stein; the collapse it corrects is the textbook MSE result. Open: every published post-hoc surrogate calibrator rescales *variance/interval width*, not the point prediction, and the amplitude-correcting ones need test-time observations or ~1000 calibration points. **lambda\* as a reported diagnostic statistic** (lambda\* = 0 certifying net-harmful condition-dependence) was not found. |
| **D4** — overfitting anatomy at N_hf in {5,20,50}, train/test gap decomposition + n_eff | `preempted-but-MF-composition-open (cite)` — confidence **upgraded LOW -> MEDIUM** (batch 1's requested re-search delivered) | Lipschitz-operator sample complexity — https://arxiv.org/abs/2410.23440 ; fine-grained bias-variance — https://arxiv.org/pdf/2011.03321 ; Deep Bootstrap — https://arxiv.org/pdf/2010.08127 ; redundancy pruning — https://arxiv.org/abs/1905.12737v1 | Decomposition is textbook; its **noise term is B1's aleatoric barrier** (same instrument, two views). Still no PDE-domain **n_eff estimator** after two batches — if B2/B3 uses one it must define it locally and say so. |

## Citations summary

- [Anon. 2026] "Predictivity and Utility of Neural Surrogates of Multiscale PDEs" — https://arxiv.org/html/2604.20061v1 — FETCHED — used in: iteration_2.md term 2 (also cited in batch 1)
- [Anon. 2026] "Local Conformal Predictions for Calibrated Surrogates" (FALCON) — https://arxiv.org/html/2607.01354v1 — FETCHED — used in: iteration_2.md term 3
- [Anon. 2026] "DOPD: Dual On-policy Distillation" — https://arxiv.org/html/2606.30626v1 — FETCHED — used in: iteration_5.md term 2
- [Anon. 2025] "A Functional Perspective on Knowledge Distillation in Neural Networks" — https://arxiv.org/abs/2510.12615 — FETCHED (abstract) — used in: iteration_5.md term 2
- [Anon. 2025] "Towards Multi-Fidelity Scaling Laws of Neural Surrogates in CFD" — https://arxiv.org/abs/2511.01830 — FETCHED (abstract) — used in: iteration_4.md term 2
- [Anon. 2024] "The Sample Complexity of Learning Lipschitz Operators with respect to Gaussian Measures" — https://arxiv.org/abs/2410.23440 — FETCHED (abstract) — used in: iteration_3.md term 3
- [Anon. 2019] "Less is More: An Exploration of Data Redundancy with Active Dataset Subsampling" — https://arxiv.org/abs/1905.12737v1 — FETCHED (abstract) — used in: iteration_3.md term 2
- [Anon. 2023] "The Global Active Subspace Method" — https://arxiv.org/pdf/2304.14142 — FETCHED — used in: iteration_4.md term 1
- [Anon. 2025] "Learning stochasticity: a nonparametric framework for intrinsic noise estimation" (TRINE) — https://arxiv.org/html/2511.13701 — FETCHED — used in: iteration_1.md term 3
- [Anon. 2017] "On estimation of the noise variance in high-dimensional linear models" — https://arxiv.org/abs/1711.09208 — FETCHED (abstract) — used in: iteration_1.md term 1
- [Pelckmans et al.] "The differogram: Non-parametric noise variance estimation and its use for model selection" — https://www.sciencedirect.com/science/article/abs/pii/S0925231205001682 — search result only (not fetched) — used in: iteration_1.md term 1
- ["Nonparametric Error Variance Estimation in Regression: A Review"] — https://link.springer.com/chapter/10.1007/978-3-032-07178-1_19 — FETCH BLOCKED (303 auth redirect); snippet only — used in: iteration_1.md term 1
- [Wang & Raftery] "Nearest-Neighbor Variance Estimation (NNVE)" JASA 97:460 — https://www.tandfonline.com/doi/abs/10.1198/016214502388618780 — search result only — used in: iteration_4.md term 1
- [Efron & Hastie, CASI ch.7] "James-Stein Estimation and Ridge Regression" — https://efron.ckirby.su.domains/other/CASI_Chap7_Nov2014.pdf — search result only — used in: iteration_5.md term 1
- [Hansen] "Generalized Shrinkage Estimators" — https://web-docs.stern.nyu.edu/old_web/emplibrary/shrink3.pdf — search result only — used in: iteration_5.md term 1
- [Perrone et al. 2026] FreqNO-DPS — https://arxiv.org/pdf/2606.03936 — search result here; substantive summary in `docs/reports/MF_Leaderboard_Beaters_2026_Report.md` — used in: iteration_2.md term 3
- [Anon.] "Dead Science Walking: Publication Bias and the AI Scientist Pipeline" — https://arxiv.org/pdf/2606.04220 — search result only — used in: iteration_4.md term 3

**Batch-1 citations still binding** (do not re-derive): Agarwal et al. IQM/stratified
bootstrap https://ar5iv.labs.arxiv.org/html/2108.13264 ; Du paired bootstrap
https://arxiv.org/abs/2511.19794 ; Yang et al. LUPI non-monotone law
https://arxiv.org/abs/2209.08754 ; McGreivy & Hakim weak baselines
https://arxiv.org/abs/2407.07218 ; Westermann et al. https://arxiv.org/abs/2604.00689 .

**Do-not-cite list** (surfaced only as search snippets in THIS loop; re-verify before
any card quotes them): the claim that active subspaces have been tested for kNN
regression by projecting then computing Euclidean distance (contradicted by the
fetched abstract of 2304.14142); arXiv:2511.01830's specific claims that model size
was fixed and that "allocating all resources to high-fidelity samples does not lead to
optimal test performance" (fetch returned only a high-level abstract summary); the
`VarianceScaling`/`GPNormal` closed-form NLL calibration detail; the redundancy "<10%
test-accuracy degradation" threshold. Batch 1's do-not-cite list (FNO rate r=0.28, the
60.1K figure, SPDEBench's factor-of-two, the 20-sample MF anecdote) remains in force.

## Dead ends

- `estimate Bayes error irreducible error field-valued output surrogate few samples paired samples identical parameters` -> generic classification-oriented Bayes-error exposition only; the search engine stated outright that the results do not cover field-valued outputs or few/paired-sample estimation. Second independent framing to fail (after iteration 1 term 3).
- `effective number of independent training samples redundancy dataset deep learning estimate` -> dataset-*pruning* literature (ADS, entropy-based redundancy scoring), no effective-sample-size statistic, nothing PDE-domain. Confirms batch 1's identical dead end.
- `preregistered negative control dataset machine learning experiment predicted null result methodology` -> preregistration advocacy + biomedical negative controls; nothing that pre-registers nulls from a measured information ceiling.
- Fetch failures to avoid repeating: `link.springer.com/chapter/*` (303 -> `idp.springer.com`), `www.ncbi.nlm.nih.gov/pmc/*` (301 -> `pmc.ncbi.nlm.nih.gov/*`, use the latter), `arxiv.org/pdf/*` for scanned/compressed PDFs (2205.11412) — prefer `arxiv.org/abs/*` or `arxiv.org/html/*`.

## For the brainstormer

The brainstormer MUST quote the applicable verdict row above for whatever it proposes.

1. **D1 is the batch's strongest card and it is now an adjudication, not a hunt for a
   gain.** r2s3-B1 is `cratered`/`falsified` and r2s2-B1's stack adds ~nothing
   (`state/maintainer_report.md`) — so a matched +/-LF contrast is measuring a
   near-zero-or-negative effect. Three fetched sources make that a *predicted*, citable
   outcome rather than a disappointment: the "privilege illusion"
   (https://arxiv.org/html/2606.30626v1), negative asymmetric transfer
   (https://arxiv.org/abs/2510.12615), and batch 1's Yang et al. non-monotone LUPI law.
   Write the null as the pre-registered expectation.
2. **Adopt DOPD's advantage-gap design instead of inventing a contrast.** Compare an
   LF-consuming teacher and a condition-only student *on the same samples* and split
   the error into a capability gap and an information gap. It is fetched, citable, and
   directly answers "what is LF worth?" without needing an LF-fed model to win.
3. **Do not propose "build a ceiling estimator".** D2's verdict is `preempted` at the
   method level — B1 already implemented the differogram and a neighbour-based variance
   estimator, and the 19-dim breakdown is a documented property of that class. Propose
   "project onto an active subspace (https://arxiv.org/pdf/2304.14142) then re-run the
   named estimator, and report the datasets where support provably fails". On
   ifc_poisson (N_hf = 5) state plainly, citing https://arxiv.org/abs/2410.23440, that
   no ceiling claim is defensible.
4. **Keep the shrinkage arm, but sell lambda*, not the shrinkage.** Shrinkage is
   James-Stein and the collapse it corrects is the textbook MSE-conditional-mean result
   quoted verbatim in https://arxiv.org/html/2604.20061v1. What no source does is
   *report lambda\* as a mandatory diagnostic column*. Also note the practical
   constraint: FALCON's ~1000-point calibration requirement
   (https://arxiv.org/html/2607.01354v1) means the train-fold lambda\* must be fit on
   very few points — quantify that uncertainty or the arm is not certifiable.
5. **D3/D4 both now have a hard external constraint to quote.** arXiv:2410.23440's "no
   algebraic convergence rates in m" result is the citation for why the ifc_poisson
   N_hf = 5 column is information-starved rather than architecture-starved — use it in
   `expected_falsification` instead of asserting it.
6. **n_eff is still uncited after two batches.** If the card wants effective sample
   counts (program.md 12.4's drift-class rule), it must define the statistic in the
   recipe and label it a project convention. Do not imply a literature standard exists.
7. **Re-certification is owed.** B1's part 7 item (4): the installed noise-floor
   constants were measured on a model that is conditional-mean-collapsed on 3 of 6
   datasets and therefore **under-state** a less-collapsed successor's noise. Any B2
   claim against those constants must either re-certify on the compared arm or state
   the bias direction explicitly.
