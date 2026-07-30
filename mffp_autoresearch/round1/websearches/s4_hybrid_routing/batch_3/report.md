# Websearch Report — Stream `s4_hybrid_routing`, Batch 3 (ROUTER synthesis)

**Stream**: `s4_hybrid_routing`
**Batch**: 3
**Total iterations**: 5 (**cap hit** — noted in the `iteration_5.md` header)
**WebSearch calls**: 15 (3 per iteration, never more)
**WebFetch calls**: 16 (12 usable, 4 failed: bepress Super Learner **HTTP 403**,
escholarship `qt4qn0067v` PDF binary, `arxiv.org/pdf/2102.01010` 3.1 MB binary
(**recovered via ar5iv**), `arxiv.org/pdf/2607.03693` 5.4 MB binary)
**Cap hit**: **YES**

**What this batch had to decide.** B3 is the round's pre-scoped synthesis slot
in ROUTER form, and its in-repo directives are already fixed by evidence
(OOF-gate every stage; corrector target = node-aligned/LSI-cleaned residual;
fitted taper not hard re-registration; no attention capacity). My job was
therefore **not** to relitigate those but to price their prior art — and the
bar is the round's highest, since this card, if it wins, is the headline and
the project's novelty record is 0-for-4 (program.md §13.3).

## Search trace

### Turn 1 — routing objects in SciML → `iteration_1.md`
Terms (why): correction-vs-surrogate routing; MoE over neural operators keyed
on a dataset property; MF behaviour when the LF input is missing at inference.
- **Nearest published router**: *"at each iteration, a solver is selected from
  an ensemble of solvers"* via *"an approximate greedy router"* keyed on
  **estimated error** — per-iteration, not per-dataset, not MF
  [cite: https://arxiv.org/abs/2509.24814 — **fetched**; the PDF
  https://arxiv.org/pdf/2509.24814 fetched but gave no verbatim decision rule].
- **Per-dataset routing IS published** as the fix for cross-dataset
  interference: dataset-level granularity, dataset identity as signal,
  *"porous routing"* against *"negative transfer"*
  [cite: https://arxiv.org/pdf/2605.15179 — **fetched**].
- **No usable results** on routing by LF *availability*: MF treats a missing LF
  as a latent variable to integrate out [https://arxiv.org/pdf/2301.05729 —
  search-return] or as an acquisition problem
  [https://dl.acm.org/doi/10.1007/978-981-95-7072-0_32 — search-return].

### Turn 2 — the OOF gate's canonical citations → `iteration_2.md`
Terms (why): super learner / CV-selector oracle inequality; double-ML
cross-fitting; an explicit statement of the in-sample-base artifact. The s6-B2
loop could only reach Wolpert *through* arXiv:1106.1684, so a fetchable
canonical source was owed.
- **DIRECT HIT**: *"In order to avoid overfitting, our construction also makes
  use of the K-fold sample splitting, which we call cross-fitting."*
  [cite: https://arxiv.org/abs/1608.00060 — **fetched**]. This is the name for
  what B3's per-stage OOF gate does.
- The published failure mode is an **inflated validation score**:
  *"inflates validation scores by 10-20% while producing poor production
  performance"*; *"Always use out-of-fold predictions"*
  [cite: https://mcpanalytics.ai/articles/stacking-ensemble-practical-guide-for-data-driven-decisions
  — **fetched**; practitioner guide, usable only for the statement of the
  artifact].
- Super Learner primary source **unreachable this turn** (bepress 403,
  escholarship binary) — rescued in turn 5.

### Turn 3 — corrector on an operator-cleaned residual → `iteration_3.md`
Terms (why): two-stage residual SR; ML defect correction on a coarse solve;
fit-linear-then-learn-the-residual.
- The CFD canon composes an NN correction with a **fixed classical solver**:
  *"model a residual correction to the discretized Navier-Stokes equations"*,
  `u_t = u_t* + LC(u_t*)`, base = *"a standard implementation of a finite
  volume method"*, and *"LI performs best, although learned correction (LC) is
  not far behind"* [cite: https://ar5iv.labs.arxiv.org/html/2102.01010 —
  **fetched via the ar5iv route** after the PDF returned binary].
- The clearest published "fit the parametric operator, learn only its residual"
  is outside PDEs, in RF power-amplifier linearization
  [cite: https://arxiv.org/pdf/2005.05655 — **fetched**, weak quote extraction
  recorded honestly].
- Two-stage residual SR is old but its pre-stage is a *learned* deconvolution
  or a parameter-free interpolator
  [https://openaccess.thecvf.com/content_cvpr_2017_workshops/w12/papers/Fan_Balanced_Two-Stage_Residual_CVPR_2017_paper.pdf
  — search-return].

### Turn 4 — fitted taper vs hard cutoff → `iteration_4.md`
Terms (why): Gibbs from a sharp cutoff; Wiener gain vs truncated inverse
filtering; node- vs cell-centred grid transfer.
- *"A sharp cut-off or truncation in the k-space is equivalent to a convolution
  in spatial domain with a sinc function"*; *"Only windows without an abrupt
  discontinuity will fully suppress Gibbs oscillations"*; *"Choosing a filter
  is a trade-off between the degree of suppression of the Gibbs artifacts and
  image blur"* [cite: https://pmc.ncbi.nlm.nih.gov/articles/PMC4915073/ —
  **fetched**].
- Truncated inverse filtering *"by cancelling the high frequencies"* vs
  Wiener's smoothly decreasing gain, where *"the problem of noise increase is
  no longer observed"*
  [cite: https://vincmazet.github.io/bip/restoration/deconvolution.html —
  **fetched**].
- **No usable fetched result** on node/cell-centred transfer, but the returns
  place it squarely in classical multigrid numerics
  [https://link.springer.com/article/10.1007/s10440-009-9533-2 ,
  https://www.researchgate.net/publication/225576806_Cell-centred_multigrid_revisited
  — search-returns].

### Turn 5 — FINAL, cap hit; refutation pass + verdict → `iteration_5.md`
Terms (why): the discrete super learner (the refutation of D1's selection rule,
and the citation rescue); missing-modality routing (the refutation of
availability-keying); a fitted linear stage before a neural MF residual (the
refutation of D3).
- **Citation rescued**: *"The discrete Super Learner, or cross-validation
  selector, is the algorithm in the library that minimizes the cross-validated
  empirical risk"*; *"proven to be asymptotically as accurate as the best
  possible prediction algorithm in the library"*; *"fits a metalearner on the
  validation-set predictions in a cross-validated manner, thereby avoiding
  overfitting"* [cite: https://tlverse.org/csp2020-workshop/sl3.html —
  **fetched**].
- **Availability-keyed routing is a whole subfield outside SciML**:
  *"the router explicitly incorporates both the modality-missing type and the
  visual content for gating"*, `m_type` = *"the missing-modality
  configuration"*, *"each expert corresponds to a pattern expert ... for a
  specific missing pattern"* [cite: https://arxiv.org/html/2511.11460v2 —
  **fetched**]. CoRE-VLA's availability mask **could not be fetched** and is
  recorded as an unattributed lead.
- **D3's gap confirmed from the inside**: the canonical residual-MF method has
  **no** linear stage — *"A widely used neural network based approach ...
  assumes a linear correlation between models ... unable to capture a possibly
  nonlinear correlations"*, *"we ... formulate the non-linearity in terms of
  the residual"* [cite: https://arxiv.org/html/2310.03572 — **fetched via the
  `/html/` route**; the same arXiv id whose PDF fetch **failed in batch 2**].

## Prior-art verdict

| Candidate direction | Verdict | Citations (fetched) | What remains open |
|---|---|---|---|
| **D1 — per-dataset ROUTER: LF-defect-correction wherever the test split ships an LF fidelity, champion transfer path only where it does not (`ifc_poisson`), each branch OOF-gated** | **`preempted-but-MF-composition-open (cite)`** | https://tlverse.org/csp2020-workshop/sl3.html (**fetched** — the *"cross-validation selector"*, *"proven to be asymptotically as accurate as the best possible prediction algorithm in the library"*) · https://arxiv.org/html/2511.11460v2 (**fetched** — router gated on *"the modality-missing type"*, `m_type` = *"the missing-modality configuration"*) · https://arxiv.org/pdf/2605.15179 (**fetched** — dataset-level *"porous routing"* vs *"negative transfer"*) · https://arxiv.org/abs/2509.24814 (**fetched** — per-iteration greedy solver router keyed on estimated error) · negatives: https://arxiv.org/pdf/2301.05729 , https://dl.acm.org/doi/10.1007/978-981-95-7072-0_32 (search-returns — MF answers a missing LF by imputation or acquisition) | The **selection rule is not open** (discrete super learner) and **availability-keyed gating is not open** (missing-modality MoE). Open: no fetched source routes on **fidelity availability inside a multi-fidelity PDE surrogate**, and none routes between a **defect-correction** path and a **transfer-learning** path. **Claim zero novelty for the router.** The card's contribution is the composition + its controls; the honest framing is "the discrete super learner applied per dataset over a 2-element library, where library membership is itself determined by a data property (does the test split ship LF?)". |
| **D2 — OOF-gate EVERY stage (stage-3 keep test scored against `base_oof[val_idx]`; no joint-SGD re-tuning of alpha; `val_base_oof/val_base_insample` printed per stage)** | **`preempted (cite)`** — outright | https://arxiv.org/abs/1608.00060 (**fetched** — *"K-fold sample splitting, which we call cross-fitting"*) · https://tlverse.org/csp2020-workshop/sl3.html (**fetched** — metalearner on *"validation-set predictions in a cross-validated manner, thereby avoiding overfitting"*) · https://mcpanalytics.ai/articles/stacking-ensemble-practical-guide-for-data-driven-decisions (**fetched** — *"inflates validation scores by 10-20%"*) · in-round siblings, verified with URLs in their own loops: https://arxiv.org/pdf/1106.1684 (s6-B2 iteration_4), https://arxiv.org/html/2606.17460 (s4-B2 iteration_5) | Only the **measurement**: the published artifact is an *inflated validation score* of order 10-20 %, whereas B2 measured a **16.4x** optimism ratio and a **sign inversion of the keep/discard decision on 5/5 cells** (claims +14…+85 %, delivers −5…−28 %) costing +0.9317 skill units on `sharp__cahn_hilliard` vs the 0.5533 floor. No fetched source states that validation-selected shrinkage can flip a *decision*'s sign. The card cites the estimator and claims only the number. |
| **D3 — change the TARGET: train the corrector on the node-aligned / LSI-cleaned residual (fitted linear pre-stage → neural residual on what it leaves), with LSI-alone and corrector-alone controls in the same JSON** | **`preempted-but-MF-composition-open (cite)`** — **the card's strongest open surface** | https://ar5iv.labs.arxiv.org/html/2102.01010 (**fetched** — *"model a residual correction to the discretized Navier-Stokes equations"*, `u_t = u_t* + LC(u_t*)`, base = *"a standard implementation of a finite volume method"*, *"LI performs best, although learned correction (LC) is not far behind"*) · https://arxiv.org/html/2310.03572 (**fetched** — the canonical residual-MF method has **no** linear stage: *"A widely used neural network based approach ... assumes a linear correlation between models ... unable to capture a possibly nonlinear correlations"*) · https://arxiv.org/pdf/2005.05655 (**fetched**, weak extraction — GMP baseline then *"residual learning"* for what it misses) · https://openaccess.thecvf.com/content_cvpr_2017_workshops/w12/papers/Fan_Balanced_Two-Stage_Residual_CVPR_2017_paper.pdf (search-return — two-stage residual SR) | In **every** fetched source the pre-stage is a *fixed classical solver*, a *learned* deconvolution layer, or a *scalar/affine* fidelity correlation. **Nobody fits a |k|-dependent LSI transfer function to the fidelity gap and then trains a corrector on ITS residual**, and nobody reports the zero-parameter filter as a scored floor beside the trained model. That is the composition B2's part 7 directs and s6-B1's F6 motivates (the filter beats the 72k ConvNeXt on 3/4). |
| **D4 — band-limited composition via a FITTED taper rather than a hard re-registration / cutoff** | **`preempted (cite)`** — textbook, twice; **nothing open** | https://pmc.ncbi.nlm.nih.gov/articles/PMC4915073/ (**fetched** — *"A sharp cut-off or truncation in the k-space is equivalent to a convolution in spatial domain with a sinc function"*; *"Only windows without an abrupt discontinuity will fully suppress Gibbs oscillations"*; *"Choosing a filter is a trade-off between the degree of suppression of the Gibbs artifacts and image blur"*) · https://vincmazet.github.io/bip/restoration/deconvolution.html (**fetched** — truncation *"by cancelling the high frequencies"* vs Wiener where *"the problem of noise increase is no longer observed"*) | Nothing. B2's *"pure re-registration is 5.17x harmful above 0.5 Nyquist"* is a **measurement of a known artifact on this benchmark**, and s3_warp-B1's node/cell-centred misregistration is classical multigrid numerics (https://link.springer.com/article/10.1007/s10440-009-9533-2 , https://www.researchgate.net/publication/225576806_Cell-centred_multigrid_revisited — search-returns). Present as an inherited design constraint, never as a finding. |
| **D5 — mandatory LSI-alone + corrector-alone controls** | **`preempted (cite)`** as methodology; the *practice of reporting them* is what is open | https://ar5iv.labs.arxiv.org/html/2102.01010 (**fetched** — *"LI performs best, although learned correction (LC) is not far behind"* = the published form of "the simpler composition is competitive") · https://arxiv.org/html/2511.09729v1 (fetched in the s4-B2 loop — the winning coarse-field corrector is *"a deep FiLMed residual network with spectral convolutions"*, not attention) | Ablations are not a contribution. But **no fetched MF source reports a zero-parameter fitted-filter floor next to its trained model**, and s6-B1 F6 shows why it matters (filter 2.19x/1.56x/1.07x better than the trained net on 3/4). The transferable output is the *reporting standard*, which s6-B1's part 7 already made a round-wide rule. |

## Citations summary

Every entry appears with its URL in the named iteration file.

- [Chernozhukov, Chetverikov, Demirer, Duflo, Hansen, Newey, Robins 2016] "Double/Debiased Machine Learning for Treatment and Causal Parameters" — https://arxiv.org/abs/1608.00060 — **fetched** — iteration_2, verdict D2
- [van der Laan group, tlverse/sl3 workshop] "Super (Machine) Learning" — https://tlverse.org/csp2020-workshop/sl3.html — **fetched** — iteration_5, verdicts D1, D2
- [van der Laan, Polley & Hubbard 2007] "Super Learner" — https://biostats.bepress.com/ucbbiostat/paper222/ ; https://escholarship.org/uc/item/4qn0067v — **NOT fetched** (bepress `viewcontent.cgi` HTTP 403; escholarship PDF binary). Cited **only through** the tlverse text — iteration_2, iteration_5
- [Kochkov et al. 2021] "Machine learning accelerated computational fluid dynamics" — https://ar5iv.labs.arxiv.org/html/2102.01010 — **fetched (ar5iv route)**; https://arxiv.org/pdf/2102.01010 failed (3.1 MB binary) — iteration_3, verdicts D3, D5
- ["Residual Multi-Fidelity Neural Network Computing"] — https://arxiv.org/html/2310.03572 — **fetched (`/html/` route)**; the PDF failed in the batch-2 loop — iteration_5, verdict D3
- ["Residual Neural Networks for Digital Predistortion"] — https://arxiv.org/pdf/2005.05655 — **fetched, weak quote extraction** (fragments only; the rest is the fetcher's paraphrase and is not quoted) — iteration_3, verdict D3
- ["A Greedy PDE Router for Blending Neural Operators and Classical Methods"] — https://arxiv.org/abs/2509.24814 (**fetched**, abstract) ; https://arxiv.org/pdf/2509.24814 (**fetched**, no verbatim rule) — iteration_1, verdict D1
- ["Eradicating Negative Transfer in Multi-Physics Foundation Models via Sparse Mixture-of-Experts Routing"] — https://arxiv.org/pdf/2605.15179 — **fetched** — iteration_1, verdict D1
- ["Rethinking Efficient Mixture-of-Experts for Remote Sensing Modality-Missing Classification"] — https://arxiv.org/html/2511.11460v2 — **fetched** — iteration_5, verdict D1
- ["Gibbs Ringing in Diffusion MRI"] — https://pmc.ncbi.nlm.nih.gov/articles/PMC4915073/ — **fetched** — iteration_4, verdict D4
- ["Deconvolution", Basics of Image Processing] — https://vincmazet.github.io/bip/restoration/deconvolution.html — **fetched** — iteration_4, verdict D4
- [stacking practitioner guide] — https://mcpanalytics.ai/articles/stacking-ensemble-practical-guide-for-data-driven-decisions — **fetched**; NOT peer-reviewed, usable only for the statement of the leakage artifact — iteration_2, verdict D2
- [GAR] "Generalized Autoregression for Multi-Fidelity Fusion" — https://arxiv.org/pdf/2301.05729 — search-return — iteration_1, verdict D1 (negative)
- ["Efficient Selection of Low-Fidelity Data for Multi-fidelity Surrogate Models"] — https://dl.acm.org/doi/10.1007/978-981-95-7072-0_32 — search-return — iteration_1, verdict D1 (negative)
- [BTSRN] "Balanced Two-Stage Residual Networks for Image Super-Resolution" — https://openaccess.thecvf.com/content_cvpr_2017_workshops/w12/papers/Fan_Balanced_Two-Stage_Residual_CVPR_2017_paper.pdf — search-return — iteration_3, verdict D3
- [multigrid transfer-operator cluster] https://link.springer.com/article/10.1007/s10440-009-9533-2 ; https://www.researchgate.net/publication/225576806_Cell-centred_multigrid_revisited ; https://arxiv.org/pdf/2604.19501 — search-returns — iteration_4, verdict D4
- [missing-modality cluster] https://arxiv.org/pdf/2605.15235 ; https://arxiv.org/pdf/2603.01632 ; https://arxiv.org/html/2603.09316 ; https://www.emergentmind.com/topics/modality-aware-routing-mechanism — search-returns — iteration_5, verdict D1
- **In-round siblings cited, NOT re-fetched** (each verified to appear with its URL in the named loop's iteration files): https://arxiv.org/pdf/1106.1684 (Wolpert-1992's rule — `websearches/s6_local/batch_2/` iteration_4) ; https://arxiv.org/html/2606.17460 (Operator Boosting's 0-containing validation-selected shrinkage grid — `websearches/s4_hybrid_routing/batch_2/` iteration_5) ; https://arxiv.org/html/2511.09729v1 (LC = FiLMed residual net with spectral convolutions — same loop, iteration_3) ; https://arxiv.org/abs/2511.06294 (Physics-Attention *"may even hurt"* — same loop, iteration_3) ; https://arxiv.org/abs/2510.25803 (MoE-POT — `websearches/s4_hybrid_routing/batch_1/`). In-repo prior websearch: `docs/reports/MF_Leaderboard_Beaters_2026_Report.md` L266 (a dictionary of correction operators selected at eval by LF-consistency) and L270/335 (ARC-STAR risk-routed block refiner).

## Dead ends

- `per-dataset model routing scientific machine learning selecting between correction model and surrogate model PDE` → OOD-generalization and knowledge-guided-correction papers only; the engine itself reported that per-dataset routing *"wasn't prominently featured"*. **Explicit gap.**
- `multi-fidelity model missing low-fidelity data at inference fallback single-fidelity prediction` → imputation (GAR) and LF-acquisition only. **No MF work routes on availability.** (4th independent negative in this stream on "MF ablates counts, never structure".)
- `learn residual of a fitted linear shift-invariant transfer function neural network corrects what the linear filter misses` → domain adaptation, patents, generic ResNet; only the RF-predistortion instance was on-target. **No PDE/MF instance of a fitted-LSI pre-stage.**
- `grid interpolation phase shift misregistration node-centered cell-centered ...` → classical multigrid literature, nothing fetchable with a usable quote; enough to establish the mechanism is known numerics, not enough to cite a sentence.
- Fetch failures (recorded so nothing is cited from memory): https://biostats.bepress.com/cgi/viewcontent.cgi?article=1269&context=ucbbiostat **403** ; https://escholarship.org/content/qt4qn0067v/qt4qn0067v_noSplash_3d914a3ffc0c837588da377e4239d245.pdf (1.5 MB binary) ; https://arxiv.org/pdf/2102.01010 (3.1 MB binary — **recovered via ar5iv**) ; https://arxiv.org/pdf/2607.03693 (5.4 MB binary — CoRE-VLA availability mask **NOT** citable).
- **Unattributed leads, deliberately NOT cited**: CoRE-VLA's *"availability mask [that] ... physically disabl[es] modality-specialized experts"* (engine summary only) ; the Wiley MF-residual paper's *"linear correlator ... plus residual component"* split (https://onlinelibrary.wiley.com/doi/10.1002/nag.3787 , engine summary only). Either would strengthen D1/D3's preemption if a future batch can fetch them.

## For the brainstormer

The brainstormer MUST quote the verdict above for whatever it proposes.

1. **Claim ZERO novelty for the router itself.** Selection between two paths by
   cross-validated risk is the **discrete super learner / cross-validation
   selector** with an oracle guarantee
   (https://tlverse.org/csp2020-workshop/sl3.html, fetched), and gating on
   *which inputs exist* is the missing-modality MoE subfield
   (https://arxiv.org/html/2511.11460v2, fetched). Frame the card as *"the
   discrete super learner over a 2-element library whose membership is set by a
   data property (does the test split ship an LF fidelity?)"* — a composition
   and its controls, not a mechanism.
2. **Claim ZERO novelty for the OOF gate; claim the measurement instead.**
   Cite https://arxiv.org/abs/1608.00060 for the name (*"K-fold sample
   splitting, which we call cross-fitting"*). The published artifact is a
   10-20 % inflated validation score; B2 measured a **16.4x** optimism ratio
   and a **decision sign-inversion on 5/5 cells**. That delta — the flip of a
   keep/discard decision, not merely an optimistic number — is the only claimable
   content, and its per-dataset bar is `sharp__cahn_hilliard` (+0.9317
   measured vs the 0.5533 floor; the panel move +0.36/+0.29 is **inside** the
   0.884 geomean floor, so do NOT pre-register a panel claim for the gate arm).
3. **D3 is the card's only strong open surface — build the card around the
   TARGET.** No fetched source fits a **|k|-dependent LSI transfer function to
   the fidelity gap** and trains a corrector on **its** residual: the CFD canon's
   pre-stage is a fixed solver (https://ar5iv.labs.arxiv.org/html/2102.01010),
   SR's is a learned deconvolution, and the canonical residual-MF method has
   **no linear stage at all** (https://arxiv.org/html/2310.03572, fetched:
   *"we ... formulate the non-linearity in terms of the residual"*). Pre-register
   the corrector-on-cleaned-residual arm against the **LSI-alone** number, not
   against copy-LF.
4. **D4 is textbook — inherit it, do not claim it.** A hard cutoff is a sinc
   convolution that rings and *"Only windows without an abrupt discontinuity
   will fully suppress Gibbs oscillations"*
   (https://pmc.ncbi.nlm.nih.gov/articles/PMC4915073/, fetched); truncated
   inverse filtering vs a smoothly decreasing gain is the Wiener textbook
   contrast (https://vincmazet.github.io/bip/restoration/deconvolution.html,
   fetched). So the "fitted taper, never a hard shift" rule is a **design
   constraint**, and B2's 5.17x above-0.5-Nyquist harm is a measurement of a
   known artifact on this benchmark.
5. **The controls are mandatory and are also the card's most transferable
   output.** 2102.01010's own verdict — *"LI performs best, although learned
   correction (LC) is not far behind"* — is the published warning that the
   simpler composition is competitive; s6-B1 F6 is the in-round version (the
   zero-parameter filter beats the 72k ConvNeXt on 3/4). Ship **LSI-alone** and
   **corrector-alone** in the same JSON as the router, per s6-B1's part-7
   round-wide rule, or the geomean is uninterpretable.
6. **Two things the prior art says will happen — pre-register them.** (a) The
   router's `ifc_poisson` leg inherits the champion path, and s6-B1 part 7 item
   4 records that the identical held-out-alpha machinery chose `alpha = 0` on
   **6/6** datasets on a champion-generated base: expect the transfer branch to
   contribute nothing beyond its own baseline, and say so in advance. (b) MoE
   prior art's stated benefit is **avoiding negative transfer**
   (https://arxiv.org/pdf/2605.15179, fetched), not raw accuracy — so the
   router's honest predicted gain is *"no dataset is worse than the better of
   its two branches"*, a **no-harm** claim, and the falsification clause should
   be written against that, with every threshold above the per-dataset
   `min_claimable_effect` (pfc 1.1511, allen_cahn 1.6334, fisher_kpp 0.41774,
   cahn_hilliard 0.55335, ifc_poisson 0.23991; geomean 0.884; helmholtz
   report-only).
