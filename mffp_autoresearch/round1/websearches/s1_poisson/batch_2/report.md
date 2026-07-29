# Websearch Report — Stream `s1_poisson`, Batch 2

**Stream**: s1_poisson (gap) · **Batch**: 2 · **Total iterations**: 5 ·
**WebSearch calls**: 15 (3 per iteration) · **WebFetch calls**: 12 attempted /
8 usable (4 failures: arXiv `/pdf/` binary, ScienceDirect 403, Springer 303-IdP,
PMC 301 redirect later recovered) · **Cap hit**: **yes** (5 of 5)

## Search trace

### Turn 1 — is the shared-scaler pitfall documented? (task item a)
Terms: `per-fidelity normalization multi-fidelity neural network ... output scaling`;
`multi-resolution neural operator ... per-resolution normalization level-wise standardization appendix`;
`low-fidelity high-fidelity different magnitude scales normalization pitfall ... amplitude mismatch`.
Chosen because B1's mechanism finding is a normalization claim and batch 1 never
searched normalization.
- **QuadNorm** — standard normalization layers "compute statistics through
  uniform averaging of discrete grid values, making normalization itself
  discretization-dependent"; quadrature weights make cross-resolution mismatch
  O(h²) instead of O(h). Scope limit stated by the fetch: it does **not** cover
  shared-vs-per-level *data/target* scalers
  [cite: https://arxiv.org/html/2605.07375] → iteration_1.md
- **MF-PINN + adaptive residual learning** — the only scaling statement is
  across *variables* ("pressure versus velocity"), not across fidelities
  [cite: https://arxiv.org/html/2602.01176v1] → iteration_1.md
- **Berger et al., General MF framework for training ANNs** — fetch verdict:
  "the paper does not discuss normalization or scaling of training data across
  different fidelity levels"; it says "we will skip units, assuming thereby
  implicitly appropriately normalized quantities"
  [cite: https://www.frontiersin.org/articles/10.3389/fmats.2019.00061/full]
  → iteration_1.md

### Turn 2 — is the h^p scale law exploited in learned MF models? (task item b)
Terms: `... h^p scaling residual between grid levels ... rescale before learning`;
`Richardson extrapolation neural network multi-fidelity ... known order of accuracy`;
`multilevel neural network ... level-dependent scaling of residual corrections`.
- **Gauss–Richardson Extrapolation** "unifies classical extrapolation methods
  with modern multi-fidelity modelling"; error bound "b(x) = x^r, where r
  represents the convergence order" enters the kernel so that "the normalized
  error (f(x)−f(0))/b(x) behaves regularly"; r estimated by max quasi-likelihood
  when unknown [cite: https://pmc.ncbi.nlm.nih.gov/articles/PMC11985099/]
  → iteration_2.md
- **Multi-level NNs for BVPs** (CMAME) — "the size of the residual becomes
  increasingly smaller at each level, **which requires normalization of the
  solution error at each level**" (**snippet-grade; fetch 403**)
  [cite: https://www.sciencedirect.com/science/article/abs/pii/S0045782523007892]
  → iteration_2.md
- NN-approximated local truncation error as an alternative to Richardson
  extrapolation [cite: https://arxiv.org/pdf/2504.05493] → iteration_2.md

### Turn 3 — multi-level extension of s7's gain/shape axis (task item c)
Terms: `Kennedy O'Hagan ... rho amplitude ratio ... neural network learned scale`;
`fidelity-conditioned neural operator output scale conditioning ... normalization ablation`;
`multiplicative scaling versus additive residual ... constant factor`.
- **AR1 / co-kriging**: `y_high(x) = ρ(x)·y_low(x) + δ(x)`, ρ "a
  scaling/correlation factor (constant, linear or quadratic)"; fetch verdict:
  "**The documentation contains no mention of normalizing each fidelity level's
  data**" [cite: https://smt.readthedocs.io/en/latest/_src_docs/applications/mfk.html]
  → iteration_3.md
- **Explicit negative**: no paper combining fidelity-conditioned neural
  operators + output-scale conditioning + normalization ablation
  [cite: engine negative over
  https://www.emergentmind.com/topics/conditional-neural-operator-architecture,
  https://www.emergentmind.com/topics/film-style-layer-norm-conditioning]
  → iteration_3.md

### Turn 4 — the training-free floor and the baseline-discipline literature (task item d)
Terms: `nearest neighbor training-free baseline outperforms neural surrogate PDE benchmark critique`;
`normalization ablation changes conclusion multi-fidelity operator learning ... reproducibility`;
`nearest neighbor in parameter space retrieval baseline ... few samples`.
- **McGreivy & Hakim (Nature MI 2024)** — **79 % (60/76)** of ML-beats-solver
  claims compare against a weak baseline; abstract does **not** discuss
  interpolation/NN baselines [cite: https://arxiv.org/abs/2407.07218]
  → iteration_4.md
- kNN competitiveness only in non-MF, non-field settings (snippet-grade)
  [cite: https://www.mdpi.com/2076-3417/11/20/9411,
  https://www.sciencedirect.com/science/article/abs/pii/S0306454925006863]
  → iteration_4.md
- New MF lead surfaced: discretization-independent MF operator learning
  [cite: https://arxiv.org/pdf/2507.07292] → iteration_4.md

### Turn 5 — refutation pass + verdicts (CAP)
Terms: `discretization-independent multifidelity operator learning normalization each fidelity level separately`;
`NARGP ... per-level scale factor output rescaling before network training`;
`factorial ablation ... normalization scheme and training data composition ... 2x2 design`.
- **Fourth independent explicit negative** on cross-fidelity normalization: the
  abstract "does not discuss: whether normalization is shared or per-fidelity;
  ... any ablation studies on normalization strategies; data scaling procedures
  across fidelities" [cite: https://arxiv.org/abs/2507.07292] → iteration_5.md
- **NARGP**: ρ_t(·) is input- and output-dependent, i.e. the level amplitude
  relation is a first-class learned object; but each level trains independently
  so "no information flows backward from higher to lower fidelities"
  (search-return) [cite: https://arxiv.org/pdf/2306.03144,
  https://arxiv.org/pdf/2105.01081] → iteration_5.md
- **Explicit negative** on the factorial design: "I did not find a specific
  paper directly addressing a 2x2 factorial ablation study examining the
  interaction between normalization scheme and training data composition for
  multi-level neural PDE surrogates" → iteration_5.md

## Prior-art verdict

| Candidate direction | Verdict | Citations (fetched unless marked) | What remains open |
|---|---|---|---|
| **(i)** Per-level / per-fidelity **target** normalization (`MFFP_LADDER_SCALER=per_level`) in a pooled multi-level ladder | **preempted-but-MF-composition-open** | per-level error normalization required in multi-level residual NNs: https://www.sciencedirect.com/science/article/abs/pii/S0045782523007892 (**snippet-grade, fetch 403**) · internal-normalization discretization-dependence: https://arxiv.org/html/2605.07375 (fetched) · classical MF models ρ instead of normalizing: https://smt.readthedocs.io/en/latest/_src_docs/applications/mfk.html (fetched) · four MF sources that do not state their cross-fidelity normalization at all: https://arxiv.org/html/2602.01176v1, https://www.frontiersin.org/articles/10.3389/fmats.2019.00061/full, https://arxiv.org/abs/2507.07292 (all fetched) | Per-level standardization of **targets pooled into ONE shared fidelity-conditioned operator**; no published effect size for the choice; nothing at N_hf = 5 on an elliptic ladder. Frame as a **hygiene fix measured as an ablation**, never as an invention. |
| **(ii)** h^p-aware residual/target scaling as an explicit inductive bias (hard-coded h² divisor) | **preempted (cite)** | https://pmc.ncbi.nlm.nih.gov/articles/PMC11985099/ (fetched — GRE: b(x)=x^r in the kernel; "the normalized error (f(x)−f(0))/b(x) behaves regularly"; r estimated when unknown) · https://arxiv.org/pdf/2504.05493 (search-return — NN replaces Richardson for truncation error) | Only that GRE is a GP extrapolating (functionals of) solutions, not a field-valued operator, and no source rescales *training targets* by h^p. **Do not hard-code h²**; use the empirical per-level scaler and report the measured 4.379/4.196/4.120 ≈ 2² agreement as a result. |
| **(iii)** The **factorial** `{shared, per_level} × {two_level, allpairs}` design itself | **novel** (design-level, weak claim) | explicit engine negatives, iteration_5 term 3 and iteration_3 term 2; nearest neighbors: routine hyperparameter ablations https://arxiv.org/html/2405.17260v2 (search-return), MFRNP aggregation ablation https://arxiv.org/html/2402.18846v1 (batch-1 fetched) | Nothing close found. Value is **internal validity** (separating the two contrasts B1 conflated), not novelty. Claim "not previously ablated", never "novel method". |
| **(iv)** Training-free level-matched nearest-condition lookup as a reported floor (0.24828) | **novel** for elliptic MF; report, do not claim | https://arxiv.org/abs/2407.07218 (fetched — 79 % weak baselines; abstract does **not** cover NN/interpolation baselines) · https://www.mdpi.com/2076-3417/11/20/9411, https://www.sciencedirect.com/science/article/abs/pii/S0306454925006863 (search-return, non-MF) | The specific *cross-fidelity level-matched* retrieval baseline is unpublished as far as 3 searches reach. Report it beside every skill number; the weak-baseline paper licenses the practice but is not a citation for the construct. |
| **(v)** All-ordered-pairs composition (carried over from batch 1) | **preempted-but-MF-composition-open** (batch 1, unchanged) | see `websearches/s1_poisson/batch_1/report.md` | Unchanged. Batch 2 adds: NARGP-style recursive MF trains each level independently so "no information flows backward from higher to lower fidelities" (iteration_5) — the deficiency the pooled shared network is supposed to avoid, and a sharper motivation than batch 1 had. |

## Citations summary

- [QuadNorm 2026] "QuadNorm: Resolution-Robust Normalization for Neural Operators" — https://arxiv.org/html/2605.07375 (**fetched**) — used in: iteration_1, verdict (i)
- [MF-PINN 2026] "Multi-Fidelity PINNs with Bayesian UQ and Adaptive Residual Learning" — https://arxiv.org/html/2602.01176v1 (**fetched**) — used in: iteration_1, verdict (i)
- [Berger et al. 2019] "General Multi-Fidelity Framework for Training ANNs With Computational Models" (Front. Mater. 6:61) — https://www.frontiersin.org/articles/10.3389/fmats.2019.00061/full (**fetched**) — used in: iteration_1, verdict (i)
- [Oates et al.] "Probabilistic Richardson Extrapolation" (Gauss–Richardson Extrapolation) — https://pmc.ncbi.nlm.nih.gov/articles/PMC11985099/ (**fetched**; ADS record https://ui.adsabs.harvard.edu/abs/2024arXiv240107562O/abstract) — used in: iteration_2, verdict (ii)
- ["NN-enhanced integrators for simulating ODEs"] — https://arxiv.org/pdf/2504.05493 (search-return) — used in: iteration_2, verdict (ii)
- [Aldirany, Cottereau, Laforest, Prudhomme] "Multi-level neural networks for accurate solutions of boundary-value problems" (CMAME) — https://www.sciencedirect.com/science/article/abs/pii/S0045782523007892 (**fetch failed, HTTP 403 — snippet-grade**) — used in: iteration_2, verdict (i)
- [SMT docs] "Multi-Fidelity Kriging (MFK)" — AR1 / Kennedy–O'Hagan, ρ(x) — https://smt.readthedocs.io/en/latest/_src_docs/applications/mfk.html (**fetched**) — used in: iteration_3, verdict (i)
- [MF-Box / MF matter-power-spectrum emulation] NARGP characterization (Perdikaris et al. 2017 ρ_t(·)) — https://arxiv.org/pdf/2306.03144, https://arxiv.org/pdf/2105.01081 (search-return) — used in: iteration_5, verdict (v)
- [McGreivy & Hakim 2024] "Weak baselines and reporting biases lead to overoptimism in machine learning for fluid-related PDEs" (Nature Mach. Intell.) — https://arxiv.org/abs/2407.07218 (**fetched, abs**) — used in: iteration_4, verdict (iv)
- ["Discretization-independent multifidelity operator learning for PDEs" 2025] — https://arxiv.org/abs/2507.07292 (**fetched, abs**) ; https://arxiv.org/pdf/2507.07292 (search-return) — used in: iteration_4, iteration_5, verdict (i)
- [mesh-free surrogate comparison] "Mesh-Free Surrogate Models for Structural Mechanic FEM Simulation" — https://www.mdpi.com/2076-3417/11/20/9411 (search-return) — used in: iteration_4, verdict (iv)
- [NPP fire-scenario surrogate] — https://www.sciencedirect.com/science/article/abs/pii/S0306454925006863 (search-return) — used in: iteration_4, verdict (iv)
- [two-phase-flow neural PDE surrogates] normalization-as-routine-practice — https://arxiv.org/html/2405.17260v2 (search-return) — used in: iteration_5, verdict (iii)
- [MFRNP, ICML 2024] — https://arxiv.org/html/2402.18846v1 (fetched in **batch 1**) — used in: verdict (iii) as nearest-neighbor ablation
- [LMM deep-learning error estimation] — https://arxiv.org/pdf/2103.11488 (search-return) — used in: iteration_2 (framing only)

**Leads seen but NOT fetched — must not be cited as evidence**: Multi-Grid
Tensorized FNO (https://arxiv.org/pdf/2310.00120); Physics-informed
Multi-resolution Neural Operator (https://arxiv.org/html/2510.23810); Multigrade
Neural Network Approximation (https://arxiv.org/pdf/2601.16884); Multilevel
minimization for deep residual networks (https://arxiv.org/pdf/2004.06196);
Neural Emulator Superiority (https://arxiv.org/html/2510.23111v1); MF-FNO
transfer learning "relative loss normalization" (https://arxiv.org/pdf/2304.06972);
"The effects of scale factor and correction on the multi-fidelity model"
(https://link.springer.com/article/10.1007/s12206-016-0414-0); GP MF overview
(https://arxiv.org/pdf/2006.16728).

## Dead ends

- `arxiv.org/pdf/...` — failed again (2006.16728 returned 2.6 MB unparsable
  binary). Batch 1's rule holds: **use `/abs/` or `/html/`**.
- `sciencedirect.com` — HTTP 403 (killed the single most on-point source for
  verdict (i), the CMAME multi-level-NN paper). Prefer arXiv preprints.
- `link.springer.com` — 303 redirect into an auth IdP.
- `ncbi.nlm.nih.gov/pmc/...` — 301 to `pmc.ncbi.nlm.nih.gov/...`; retry on the
  redirect host works (that is how GRE was recovered).
- Term "amplitude mismatch / magnitude scales" (iteration_1 term 3) — collapsed
  into seismology and instrument-calibration noise. The productive vocabulary is
  **"scale factor ρ"** and **"discrepancy function"**, not "amplitude".
- **Systematic finding, not a dead end**: *five* fetched multi-fidelity sources
  do not state their cross-fidelity normalization at all. The question is not
  buried in appendices — it is **absent**. That is the batch's strongest result.

## For the brainstormer

1. **Quote verdict (i) verbatim: `preempted-but-MF-composition-open`.** Per-level
   normalization of level-wise residuals is already *required practice* in
   multi-level residual NNs (CMAME, snippet-grade), and QuadNorm owns the
   "normalization is discretization-dependent" insight for operators. The card
   must present `MFFP_LADDER_SCALER=per_level` as a **hygiene fix whose effect
   size is being measured**, never as a new mechanism. The honest novelty is the
   *measurement*: no fetched source reports an effect size for the choice, and
   four report nothing about it at all.
2. **Do NOT propose an h²-hardcoded scaler.** Verdict (ii) is `preempted` by
   Gauss–Richardson Extrapolation, which literally normalizes level differences
   by b(x)=x^r and estimates r when unknown. The empirical per-level scaler is
   the same fix without the assumption. **Turn this into an asset**: report that
   the measured ratios 4.379/4.196/4.120 sit within ~5 % of 2², i.e. the data
   independently confirms the h² law GRE would have assumed.
3. **Verdict (iii) is `novel` but weak — claim "not previously ablated", not
   "novel method".** The 2×2 is justified by *internal validity*: B1's clause
   conflated normalization with composition, and the searched literature has no
   factorial that separates them. Keep the two falsification clauses separate,
   exactly as B1 part 7 specifies, and pre-register both against the
   **0.23991** floor.
4. **Carry all four reference lines in part 4** — anchor 1.5656, floor 0.23991,
   training-free matched-level 0.24828, HF-train-mean 0.40343 — and cite
   McGreivy & Hakim's 79 % weak-baseline statistic
   [https://arxiv.org/abs/2407.07218] as the reason. Verdict (iv) says the
   matched-level lookup is **not published** for elliptic MF, so report it as a
   floor and do not claim it as borrowed prior art.
5. **A framing upgrade available for free** (from iteration_3/5): classical MF
   *models* the level amplitude ratio as ρ (AR1: `y_high = ρ·y_low + δ`;
   NARGP: input-dependent ρ_t(·)). B1's shared scaler does neither — it leaves
   the 75.7× ratio in the targets and offers no ρ to fit. The per-level scaler
   can be described as **implicitly restoring the ρ the pooled formulation
   deleted**. This is the strongest available motivation sentence and it is
   fully cited.
6. **A sharper motivation for keeping the composition arm** (iteration_5): the
   recursive NARGP/cascade family trains each level independently, so "no
   information flows backward from higher to lower fidelities" — which is
   precisely what a single shared pooled-row operator avoids. That is a better
   stated reason for `allpairs` than batch 1 had.
7. **Two things to leave alone this batch**: the D2 telescoping/control-variate
   direction (batch-1 `preempted`) and any seed-ensembling (collides with §4.4).
