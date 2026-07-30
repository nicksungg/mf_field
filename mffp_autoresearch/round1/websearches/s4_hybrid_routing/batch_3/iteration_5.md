# iteration_5 — FINAL (iteration cap 5 reached); prior-art verdict work

**Cap note**: this is iteration 5 of 5. No further search turns are permitted;
the verdict below is closed on the evidence in `iteration_1..5.md`.

## Search rationale

Three targeted refutation searches, one per open verdict:
- **D1 (the ROUTER)** — the strongest refutation is that the *discrete super
  learner* IS a per-dataset router; and iteration 2 failed to fetch a Super
  Learner primary source, so this doubles as the citation rescue.
- **D1b (availability keying)** — the sharpest refutation of "route on whether
  the LF input exists" comes from outside SciML: missing-modality MoE.
- **D3 (operator-cleaned residual)** — refute directly in the MF literature:
  is there already a fitted linear correlation stage with a neural residual
  on top?

## Search terms used

1. `discrete super learner selects single best algorithm per dataset cross-validation library of learners tlverse`
2. `missing modality at inference routing to modality-specific expert branch availability-aware model selection`
3. `multi-fidelity correction linear regression prestage then neural network residual coarse solve two stage linear plus nonlinear discrepancy`

## Findings

### Term 1 — the discrete super learner — **fetched, citation rescued**
https://tlverse.org/csp2020-workshop/sl3.html (van der Laan group's own
tlverse/sl3 workshop text), **fetched**, verbatim:
- *"The discrete Super Learner, or cross-validation selector, is the algorithm
  in the library that minimizes the cross-validated empirical risk."*
- *"The continuous/ensemble Super Learner, often referred to as Super Learner
  is a weighted average of the library of algorithms, where the weights are
  chosen to minimize the cross-validated empirical risk of the library."*
- *"The cross-validated empirical risk of an algorithm is defined as the
  empirical mean over a validation sample of the loss of the algorithm fitted
  on the training sample, averaged across the splits of the data."*
- *"The Super Learner is proven to be asymptotically as accurate as the best
  possible prediction algorithm in the library."*
- *"The Super Learner algorithm fits a metalearner on the validation-set
  predictions in a cross-validated manner, thereby avoiding overfitting."*
This is the fetchable canonical statement iteration 2 could not obtain
(bepress 403, escholarship PDF binary). Primary paper (van der Laan, Polley &
Hubbard 2007) landing pages, returned but **not fetched**:
https://biostats.bepress.com/ucbbiostat/paper222/ , https://escholarship.org/uc/item/4qn0067v .
Other returns: https://github.com/tlverse/sl3 ,
https://cran.r-project.org/web/packages/SuperLearner/vignettes/Guide-to-SuperLearner.html ,
https://tlverse.org/enar2021-workshop/sl3.html .
**Consequence for D1**: choosing the better of {DC path, transfer path}
per dataset by cross-validated risk **is** the discrete super learner. The
ROUTER's selection rule is preempted, and preempted by a method with an oracle
guarantee.

### Term 2 — routing keyed on input availability — **1 fetched, 1 failed**
- https://arxiv.org/html/2511.11460v2 (*Rethinking Efficient Mixture-of-Experts
  for Remote Sensing Modality-Missing Classification*), **fetched**, verbatim:
  *"the router explicitly incorporates both the modality-missing type and the
  visual content for gating"*; router `g_t = softmax(W_t f_t([z; m_type]))`
  where *"m_type encodes the missing-modality configuration"*; *"each expert
  corresponds to a pattern expert that captures the characteristic feature
  transformation required for a specific missing pattern"*.
- https://arxiv.org/pdf/2607.03693 (CoRE-VLA) — **fetch failed** (5.4 MB PDF;
  the fetcher could not locate the availability-mask text). The engine's
  summary of an *"availability mask [that] defines whether an expert is
  available based on whether the auxiliary modality is present, physically
  disabling modality-specialized experts"* is therefore recorded as an
  **unattributed lead, NOT a citation**.
- Search-returns, not fetched: https://arxiv.org/pdf/2605.15235 (MuteBench —
  modality-unavailability tolerance benchmark), https://arxiv.org/pdf/2603.01632
  (DeLo), https://arxiv.org/html/2603.09316 (CLoE),
  https://www.emergentmind.com/topics/modality-aware-routing-mechanism .
**Consequence for D1**: gating on *which inputs exist* is published outside
SciML and is a whole subfield (missing-modality MoE). It is NOT published for
multi-fidelity PDE surrogates (iteration 1 term 3: MF's answer to a missing LF
is imputation — GAR https://arxiv.org/pdf/2301.05729 — or acquisition).

### Term 3 — fitted linear stage + neural residual in MF — **fetched**
https://arxiv.org/html/2310.03572 (*Residual Multi-Fidelity Neural Network
Computing*; the same arXiv id whose **PDF fetch failed in batch 2** — the
`/html/` route works), **fetched**, verbatim:
- *"Q_HF(θ) − Q_LF(θ) = F(θ, Q_LF(θ))"* — the residual is a function of the
  parameters **and** the LF output.
- *"A widely used neural network based approach ... assumes a linear
  correlation between models ... The main limitation of this strategy is its
  inability to capture a possibly nonlinear correlations."*
- *"we do not write Q_HF(θ) = F(θ, Q_LF(θ)). Instead, we formulate the
  non-linearity in terms of the residual"*, motivated by approximation bounds
  for functions of **small uniform norm**.
- The fetch states explicitly: the method **"does not include a fitted linear
  correlation stage"**.
Other returns (not fetched): https://onlinelibrary.wiley.com/doi/10.1002/nag.3787
(MF residual NN for structured sand — engine summary describes *"a linear
correlator [capturing] predominantly linear effects ... while a residual
component models nonlinear effects"*, recorded as an unattributed lead),
https://arxiv.org/html/2602.01176 , https://link.springer.com/article/10.1007/s10543-025-01058-9 .
**Consequence for D3**: the MF literature knows the linear-vs-nonlinear
correlation split (Kennedy–O'Hagan-style ρ-scaling vs a nonlinear residual
net) and knows residual-on-LF-output correctors — but the fetched sources'
linear stage is a **scalar/affine correlation**, never a **fitted |k|-dependent
LSI transfer function**, and 2310.03572 has no linear stage at all.

## Prior-art verdict (final)

Candidate directions the B3 ROUTER card is likely to propose, each with a
retrieval-grounded verdict. Citations are only from URLs appearing in
`iteration_1..5.md` with their fetched/returned status stated.

**D1 — per-dataset router: LF-defect-correction where test LF exists, champion
transfer path where it does not (`ifc_poisson`), each branch OOF-gated.**
→ **`preempted-but-MF-composition-open (cite)`**.
Preempted twice over: (a) *selection by cross-validated risk over a library* is
the **discrete super learner / cross-validation selector**
(https://tlverse.org/csp2020-workshop/sl3.html, fetched — *"the algorithm in
the library that minimizes the cross-validated empirical risk"*, *"proven to be
asymptotically as accurate as the best possible prediction algorithm in the
library"*); (b) *gating on which inputs are available* is the missing-modality
MoE subfield (https://arxiv.org/html/2511.11460v2, fetched — *"the router
explicitly incorporates both the modality-missing type ... for gating"*,
`m_type` = *"the missing-modality configuration"*). Nearest SciML neighbours:
per-**iteration** solver selection by estimated error
(https://arxiv.org/abs/2509.24814, fetched) and per-**dataset** MoE keyed on
dataset identity for negative-transfer control
(https://arxiv.org/pdf/2605.15179, fetched — *"porous routing"*).
**Open**: no fetched source routes on **fidelity availability** in a
multi-fidelity PDE surrogate; MF's published answers to a missing LF are
imputation (https://arxiv.org/pdf/2301.05729, search-return) or acquisition
(https://dl.acm.org/doi/10.1007/978-981-95-7072-0_32, search-return). Claim
**zero** novelty for the selection rule; the card's contribution is the
*empirical composition and its controls*, and it should say so.

**D2 — OOF-gate every stage (cross-fitted keep test at stage 3, with the
`val_base_oof / val_base_insample` screening ratio printed).**
→ **`preempted (cite)`** — outright, and now with a canonical name.
https://arxiv.org/abs/1608.00060 (fetched — *"In order to avoid overfitting,
our construction also makes use of the K-fold sample splitting, which we call
cross-fitting."*) · https://tlverse.org/csp2020-workshop/sl3.html (fetched —
*"fits a metalearner on the validation-set predictions in a cross-validated
manner, thereby avoiding overfitting"*) · in-round sibling
https://arxiv.org/pdf/1106.1684 (fetched in the s6-B2 loop — Wolpert 1992's
rule) · https://arxiv.org/html/2606.17460 (fetched in the s4-B2 loop — the
0-containing validation-selected shrinkage grid).
**Open**: only the *direction and size of the artifact on this benchmark*. The
published statement of the failure mode is an **inflated validation score** of
order 10-20 % (https://mcpanalytics.ai/articles/stacking-ensemble-practical-guide-for-data-driven-decisions,
fetched — *"inflates validation scores by 10-20%"*); B2 measured a **16.4x**
optimism ratio and, crucially, a **sign inversion of the keep/discard decision
on 5/5 cells**, which no fetched source states. The card cites the estimator,
claims only the measurement.

**D3 — hand the corrector the OPERATOR: train on the node-aligned / LSI-cleaned
residual instead of the raw copy-LF residual (fitted linear pre-stage, neural
residual on what it leaves), with the LSI-alone and corrector-alone controls.**
→ **`preempted-but-MF-composition-open (cite)`** — the strongest genuinely open
surface on this card.
The *shape* is published in three separate literatures: two-stage residual SR
(https://openaccess.thecvf.com/content_cvpr_2017_workshops/w12/papers/Fan_Balanced_Two-Stage_Residual_CVPR_2017_paper.pdf,
search-return), NN-correction-on-a-coarse-solve
(https://ar5iv.labs.arxiv.org/html/2102.01010, fetched — *"model a residual
correction to the discretized Navier-Stokes equations"*, `u = u* + LC(u*)`,
*"LI performs best, although learned correction (LC) is not far behind"*), and
fit-the-parametric-model-then-learn-its-residual in RF predistortion
(https://arxiv.org/pdf/2005.05655, fetched — weak quote extraction, recorded).
**Open, precisely**: in every fetched source the pre-stage is either a *fixed
classical solver* (2102.01010), a *learned* deconvolution layer (SR), or a
*scalar/affine* fidelity correlation — and the canonical MF residual method
states it has **no** linear stage at all
(https://arxiv.org/html/2310.03572, fetched — *"A widely used neural network
based approach ... assumes a linear correlation between models ... unable to
capture a possibly nonlinear correlations"*; *"we ... formulate the
non-linearity in terms of the residual"*). Nobody fits a **|k|-dependent LSI
transfer function to the fidelity gap** and then trains a corrector on **its**
residual, and nobody reports the zero-parameter filter as a scored control
alongside the trained model.

**D4 — band-limited composition with a FITTED taper rather than a hard
re-registration/cutoff.**
→ **`preempted (cite)`**, textbook, twice.
https://pmc.ncbi.nlm.nih.gov/articles/PMC4915073/ (fetched — *"A sharp cut-off
or truncation in the k-space is equivalent to a convolution in spatial domain
with a sinc function"*; *"Only windows without an abrupt discontinuity will
fully suppress Gibbs oscillations"*; *"Choosing a filter is a trade-off between
the degree of suppression of the Gibbs artifacts and image blur"*) ·
https://vincmazet.github.io/bip/restoration/deconvolution.html (fetched —
truncation *"by cancelling the high frequencies"* vs Wiener, where *"the
problem of noise increase is no longer observed"*).
**Open**: nothing. B2's 5.17x above-0.5-Nyquist harm is a *measurement of a
known artifact on this benchmark*. The card must present it as a design
constraint inherited from signal processing, not as a finding.

**D5 — the mandatory LSI-alone and corrector-alone controls.**
→ **`preempted (cite)`** as methodology (ablation/control practice is not a
contribution) — but note the fetched prior art *supports the concern*: the
best coarse-field corrector in the batch-2 four-way comparison was
conv+spectral (https://arxiv.org/html/2511.09729v1, fetched in the s4-B2 loop),
and 2102.01010's *"LI performs best, although learned correction (LC) is not
far behind"* is the published version of "the simpler composition is
competitive". **Open**: nobody in the fetched MF literature reports a
zero-parameter fitted-filter floor next to their trained model — s6-B1's F6
(the filter beats the 72k ConvNeXt on 3/4) is the reason this control is the
card's most transferable methodological output.

## Interpretation

Every *component* of the ROUTER is published; the *composition* — a
fidelity-availability-keyed router over an LSI-cleaned defect-correction target
with cross-fitted per-stage gating and a zero-parameter floor reported in the
same JSON — is not. The card's honest claim surface is D3's target and D1's
composition, and it must claim **zero** novelty for D2 and D4.
