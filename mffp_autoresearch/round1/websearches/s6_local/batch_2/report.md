# Websearch Report — Stream `s6_local`, Batch 2

**Stream**: `s6_local` (lever; ADR 0011) — batch 2 is a **control-and-repair**
batch on the B1 family, not a new architecture (B1 part 7 `next_direction`).
**Batch**: 2
**Total iterations**: 5 (cap reached)
**WebSearch calls**: 15 (3 per turn; one malformed call in turn 1 errored before
reaching the engine and is not counted)
**WebFetch calls**: 14 attempts, **9 successful** (5 failures: arXiv PDFs
returning FlateDecode binary ×2, ResearchGate 403 ×2, bioRxiv 403,
martinsewell.com HTTP 425 — all under Dead ends)
**Cap hit**: YES — 5/5 iterations. Term cap (3/turn) respected in every turn.

## Search trace

### Turn 1 — is the data-estimated LSI defect filter published? (`iteration_1.md`)
Terms: classical defect-correction/LFA phrasing · Wiener-deconvolution phrasing ·
adversarial "linear filter beats NN on PDE SR" phrasing. Chosen because B1's F6
(a zero-parameter `T(k)` beats the trained 72k ConvNeXt on 3/4 datasets) and F7
(`|T(k)|` → 1 monotonically = the inverse of interpolation blur) make this the
round's central mechanism.
- Defect correction and **per-wavenumber comparison of coarse vs fine operator
  symbols** are textbook multigrid/LFA
  [cite: https://www.researchgate.net/publication/255595433_COARSE_GRID_APPROXIMATION_GOVERNED_BY_LOCAL_FOURIER_ANALYSIS ,
  https://www.sciencedirect.com/science/article/abs/pii/S0045782522001967] → `iteration_1.md`
- **NH-CSR** learns "a mapping from a potentially incorrect coarse-scale solution
  to an improved upscaled solution" — but with a *trained* SR network, 100k
  iterations, and **"provides no zero-parameter linear filter or transfer function
  comparison"**; no MF framing
  [cite: https://arxiv.org/html/2411.07576v2 — fetched] → `iteration_1.md`
- **DeepFDM**: neural PDE solvers "have not, until now, been carefully compared to
  established numerical PDE methods"; 1–2 orders of magnitude better than
  FNO/U-Net/ResNet with 5–50× fewer parameters — the **licence to report a
  zero-parameter floor**
  [cite: https://arxiv.org/html/2507.21269v1 — fetched] → `iteration_1.md`
- Independent support for F7's reading: an SR net decomposes into "linear ... low-pass"
  + "non-linear ... injects high-frequency" components
  [cite: https://arxiv.org/html/2405.07919v2] → `iteration_1.md`

### Turn 2 — circular vs zero padding on periodic domains (`iteration_2.md`)
Terms: direct padding comparison · boundary-error-localization signature · SineNet
ablation. Chosen because B1's F10 (45–81% of remaining squared error in a 12-cell
band; the implicitly-periodic LSI filter shows no excess) is the largest
quantified headroom item, and the only open question was **framing**.
- **SineNet (ICLR 2024) Table 3, SWE, SineNet-8: zero padding 1-step 1.50% /
  rollout 4.19% vs circular 1.02% / 1.78%**, and the authors call it "a simple yet
  crucial component" — **hygiene, explicitly not a contribution**
  [cite: https://ar5iv.labs.arxiv.org/html/2403.19507 — fetched] → `iteration_2.md`
- A whole paper exists on the axis: "high sensitivity of both accuracy and
  stability on the boundary implementation ... the choice of the optimal padding
  strategy is directly linked to the data semantics"
  [cite: https://arxiv.org/pdf/2106.11160 — fetch failed, search-return] → `iteration_2.md`
- PhyCRNet: "Periodic padding helps boost solution accuracy on the boundaries
  compared with zero-padding"
  [cite: https://arxiv.org/pdf/2106.14103] → `iteration_2.md`

### Turn 3 — per-sample trust / selective prediction (`iteration_3.md`)
Terms: selective prediction / reject-option regression · MF per-sample trust
weighting · learned error estimators for operators. Chosen because B1's F3 moved
the trust axis from per-pixel (≤4.1% oracle, −17% on cahn_hilliard) to per-sample
(helmholtz 0.1623 vs copy-LF 0.3295).
- **SelectiveNet**: selective *regression* is in scope, but "**All heads train
  jointly on the same data end-to-end ... not on held-out data**" — the canonical
  design has B1's exact defect
  [cite: https://ar5iv.labs.arxiv.org/html/1901.09192 — fetched] → `iteration_3.md`
- **MAST** — same vocabulary ("trust weighting", fusing corrected-LF with an HF
  model) but "**a scalar-output Gaussian process surrogate, not a field or operator
  model ... no involvement with images, PDE solution fields, or spatial grids**",
  and the weight is "**derived from distance and cost ratios, not learned from data
  features**"
  [cite: https://arxiv.org/html/2602.20974 — fetched] → `iteration_3.md`
- **ANCHOR** — error-triggered fallback to a solver, but "**inherently
  physics-informed, being computed from the PDE residual**" and per-timestep, not
  per-sample ⇒ ADR-0009-disqualified as a model
  [cite: https://arxiv.org/html/2512.19643v2 — fetched] → `iteration_3.md`

### Turn 4 — held-out-fold gate training / in-sample blindness (`iteration_4.md`)
Terms: stacking + out-of-fold leakage · MoE gate degeneracy · Wolpert 1992.
Chosen because B1's M2 says stage 2 "**CANNOT test the per-pixel-trust hypothesis
as posed**".
- Out-of-fold level-1 data is **Wolpert 1992's founding requirement**: "the
  combiner must be trained on predictions from base classifiers applied to held-out
  data, not the training instances used to build those classifiers"
  [cite: https://arxiv.org/pdf/1106.1684 — fetched, cites `wolpert92sg`] → `iteration_4.md`
- The failure is named: "Training the combiner (meta-learner) with the same data
  instances which are used for training the base classifiers will lead to
  overfitting the database and eventually result in poor generalization performance"
  [cite: https://arxiv.org/pdf/1105.5466 , https://www.ijcai.org/Proceedings/97-2/Papers/011.pdf] → `iteration_4.md`
- **NOT the MoE failure mode**: MoE's documented pathology is expert **load
  imbalance**, fixed by an auxiliary balancing loss; explicit engine negative on
  "gate always trusts the expert because it is scored in-sample"
  [cite: https://www.researchgate.net/publication/312619873_Outrageously_Large_Neural_Networks_The_Sparsely-Gated_Mixture-of-Experts_Layer] → `iteration_4.md`

### Turn 5 — adversarial refutation of all three directions (`iteration_5.md`)
Terms: climate bias-correction transfer functions · does any NO paper solve a
linear map in closed form / report a linear baseline · dynamic ensemble selection.
- **Charalampopoulos et al.**: HF/reanalysis data "**cannot be directly used as
  training datasets to machine learn a correction for the coarse-scale climate
  model outputs, since chaotic divergence ... makes datasets from different
  resolutions incompatible**"; they nudge to manufacture "**a compatible pair**".
  MFFP's nested ladder has that pairing for free — which *is* B1's M4 stationarity
  condition
  [cite: https://arxiv.org/abs/2304.02117 — fetched abs] → `iteration_5.md`
- **LNF-NO**: its linear branch is "**a learned linear map trained via gradient
  descent ... not solved in closed form**"; "no coarse-to-fine or hierarchical
  multi-fidelity structure"
  [cite: https://arxiv.org/html/2603.24143 — fetched] → `iteration_5.md`
- **Neural Operators as Function Interpolators**: "**Notably absent are
  comparisons to polynomial/spline interpolation or linear spectral baselines. No
  closed-form linear operator fitting occurs.**"
  [cite: https://arxiv.org/html/2605.07792 — fetched] → `iteration_5.md`
- **META-DES**: per-instance competence meta-classifiers exist, but the DES
  literature "focus[es] primarily on classification tasks"
  [cite: https://www.sciencedirect.com/science/article/abs/pii/S0031320314004919] → `iteration_5.md`

## Prior-art verdict

| Candidate direction | Verdict | Citations (fetched unless marked) | What remains open |
|---|---|---|---|
| **(i)** The closed-form **data-estimated LSI defect filter** `LF + T*LF` (`T` solved by least squares on paired train solves, held-out on/off switch) promoted to a **scored control arm** on the panel | **`preempted-but-MF-composition-open (cite)`** — preempted as a *method*, open as a *reported baseline* | Preempting: https://arxiv.org/abs/2304.02117 (fetched — ML correction operator for coarse sims trained on paired coarse/fine data) · https://arxiv.org/html/2103.09962v2 (search-return — Wiener deconvolution as a learnable layer) · https://www.researchgate.net/publication/255595433_COARSE_GRID_APPROXIMATION_GOVERNED_BY_LOCAL_FOURIER_ANALYSIS + https://www.sciencedirect.com/science/article/abs/pii/S0045782522001967 (search-return — defect correction + Fourier-symbol comparison of coarse vs fine operators) · batch-1: https://arxiv.org/pdf/2102.01010 · s1-B2 sibling: https://pmc.ncbi.nlm.nih.gov/articles/PMC11985099/ (Richardson/GRE = **preempted** there). Gaps: https://arxiv.org/html/2411.07576v2 (fetched — nearest learned analogue, "**provides no zero-parameter linear filter or transfer function comparison**") · https://arxiv.org/html/2603.24143 (fetched — linear branch is gradient-trained, "not solved in closed form") · https://arxiv.org/html/2605.07792 (fetched — "**No closed-form linear operator fitting occurs**") · https://arxiv.org/html/2507.21269v1 (fetched — the under-comparison thesis) | No fetched source **solves** the coarse→fine defect operator in closed form from paired nested solves **and scores it beside trained neural operators on an MF field benchmark**. Claim **zero method novelty**; the contribution is the *measured floor* ("this composition has a zero-parameter closed-form floor, below the trained model on 3/4 datasets"). A card that says "we introduce an LSI defect filter" dies on sight. |
| **(ii)** **Circular padding** on the four periodic panel datasets | **`preempted (cite)`** — hygiene, not a contribution | https://ar5iv.labs.arxiv.org/html/2403.19507 (**fetched** — SineNet ICLR 2024 Table 3: zero 1.50%/4.19% vs circular 1.02%/1.78%; authors' own framing "a simple yet crucial component", essential hygiene) · https://arxiv.org/pdf/2106.11160 (search-return, fetch failed — dedicated study, "high sensitivity of both accuracy and stability on the boundary implementation") · https://arxiv.org/pdf/2106.14103 (search-return — PhyCRNet periodic padding) · https://arxiv.org/html/2405.17260v1 (search-return — standard practice) | **Nothing about the fix.** Only reportable: B1's *measurement* that zero padding held **45–81%** of a defect corrector's remaining squared error in a 12-cell band (34%/18%/18% of pixels) while the implicitly-periodic filter showed none, plus the post-repair delta. Write it as "known bug, quantified cost". |
| **(iii)** **Per-sample trust head**: predict `alpha_i` from `(X_i, cheap LF-field statistics)`, fitted **out-of-fold**, corrector frozen, exact copy-LF fallback at `alpha=0` | **`preempted-but-MF-composition-open (cite)`** | https://ar5iv.labs.arxiv.org/html/1901.09192 (**fetched** — SelectiveNet: selective regression, but all heads "train jointly on the same data end-to-end ... not on held-out data") · https://arxiv.org/html/2602.20974 (**fetched** — MAST: per-sample MF trust weighting, but "scalar-output Gaussian process ... no involvement with ... PDE solution fields", weight "not learned from data features") · https://arxiv.org/html/2512.19643v2 (**fetched** — ANCHOR: "inherently physics-informed, being computed from the PDE residual", per-timestep ⇒ ADR-0009-disqualified) · https://www.sciencedirect.com/science/article/abs/pii/S0031320314004919 (search-return — META-DES per-instance competence, classification) | A **data-driven, physics-free, per-SAMPLE scalar, fitted out-of-fold, deciding whether a FIELD-VALUED defect corrector is applied at all, with the scored copy-LF field as the exact fallback** appears in no fetched source. Pre-register the prize from B1's oracles (helmholtz 0.1623 vs 0.3295; pfc −22.8%) **and** the fact that helmholtz's `min_claimable_effect` = 9.695 ⇒ report-only there. |
| **(iv)** Moving **gate training after the split** (held-out-fold gate; the true per-pixel-gate test) | **`preempted (cite)`** — the founding rule of stacking; file as a protocol bug fix | https://arxiv.org/pdf/1106.1684 (**fetched** — "the combiner must be trained on predictions from base classifiers applied to held-out data", citing Wolpert 1992) · https://arxiv.org/pdf/1105.5466 , https://www.ijcai.org/Proceedings/97-2/Papers/011.pdf (search-return — the overfitting failure named) · https://www.researchgate.net/publication/312619873_Outrageously_Large_Neural_Networks_The_Sparsely-Gated_Mixture-of-Experts_Layer (search-return — MoE's failure is load imbalance, a DIFFERENT mode) | Only the *direction of the artifact*: classic leakage makes a combiner spuriously confident, whereas B1's in-sample gate made it a **provable no-op** (uniform-gate argmin exactly 1.0 on fit/val/test, `J(0)` the maximum). One sentence in the card; not a claim. Also pre-register the ORACLE ceiling from `tools/trust_gate_headroom.py` (≤4.1%, negative on cahn_hilliard) so the arm is honestly framed as closing a mechanism claim, not moving the geomean. |
| **(v)** The owed **200-epoch `pointwise_ctrl`** (`S6_KERNEL=1`) | **not a novelty question** — a control arm | Nearest relevant fetched context: F15's stencil measurement (radius holding 50% of the optimal operator's energy = 1.4–3.0 cells) plus https://arxiv.org/html/2605.07792 (fetched) on what an operator model is actually doing | Nothing to claim. Run it as the promised control; the pre-registered expectation from B1-F15 is that a 1-cell kernel captures the band-0 gain term and misses the rest. |

## Citations summary

- [NH-CSR 2024] "Multiscale Corrections by Continuous Super-Resolution" — https://arxiv.org/html/2411.07576v2 — **fetched** — used in: iteration_1, verdict (i)
- [DeepFDM 2025] "Numerical PDE solvers outperform neural PDE solvers" — https://arxiv.org/html/2507.21269v1 — **fetched** — used in: iteration_1, verdict (i)
- [DWDN] "Deep Wiener Deconvolution Network for Non-Blind Image Deblurring" — https://arxiv.org/html/2103.09962v2 — search-return — used in: iteration_1, verdict (i)
- ["Coarse grid approximation governed by local Fourier analysis"] — https://www.researchgate.net/publication/255595433_COARSE_GRID_APPROXIMATION_GOVERNED_BY_LOCAL_FOURIER_ANALYSIS — search-return — used in: iteration_1, verdict (i)
- ["Multiscale coupling of FFT-based simulations with the LDC approach"] (Local Defect Correction) — https://www.sciencedirect.com/science/article/abs/pii/S0045782522001967 — search-return — used in: iteration_1, verdict (i)
- ["Exploring the Low-Pass Filtering Behavior in Image Super-Resolution"] — https://arxiv.org/html/2405.07919v2 — search-return — used in: iteration_1
- [Zhang et al. 2024] "SineNet: Learning Temporal Dynamics in Time-Dependent PDEs" (ICLR 2024) — https://ar5iv.labs.arxiv.org/html/2403.19507 (also https://proceedings.iclr.cc/paper_files/paper/2024/file/312237ba5de457df7bc8f88d4de21c4c-Paper-Conference.pdf) — **fetched** — used in: iteration_2, verdict (ii)
- ["Effects of boundary conditions in fully convolutional networks for learning spatio-temporal dynamics"] — https://arxiv.org/pdf/2106.11160 — **fetch failed (binary), search-return grade** — used in: iteration_2, verdict (ii)
- [PhyCRNet] — https://arxiv.org/pdf/2106.14103 — search-return — used in: iteration_2, verdict (ii)
- [two-phase-flow neural PDE surrogates] — https://arxiv.org/html/2405.17260v1 — search-return — used in: iteration_2, verdict (ii)
- ["Towards Spatio-Temporal Extrapolation of Phase-Field Simulations with Convolution-Only Neural Networks"] — https://arxiv.org/pdf/2601.04510 — search-return, NOT fetched — flagged only
- [Geifman & El-Yaniv 2019] "SelectiveNet: A Deep Neural Network with an Integrated Reject Option" (ICML) — https://ar5iv.labs.arxiv.org/html/1901.09192 , https://proceedings.mlr.press/v97/geifman19a.html — **fetched** — used in: iteration_3, verdict (iii)
- [MAST 2026] "A Multi-fidelity Augmented Surrogate model via Spatial Trust-weighting" — https://arxiv.org/html/2602.20974 — **fetched** — used in: iteration_3, verdict (iii)
- [ANCHOR] "Error-Controlled Adaptive Numerical Correction for Neural Operator Time Marching" — https://arxiv.org/html/2512.19643v2 — **fetched** — used in: iteration_3, verdict (iii)
- ["Learning to Reject with a Fixed Predictor"] — https://openreview.net/pdf?id=dCHbFDsCZz — search-return — used in: iteration_3
- ["Model Agnostic Explainable Selective Regression via Uncertainty Estimation"] — https://arxiv.org/pdf/2311.09145 — search-return — used in: iteration_3
- [residual-based error correctors for neural operators] — https://arxiv.org/pdf/2306.12047 , https://arxiv.org/pdf/2210.03008 , https://arxiv.org/html/2512.21319 — search-return — used in: iteration_3 (all physics-requiring)
- [Şen & Erdoğan] "Max-Margin Stacking and Sparse Regularization for Linear Classifier Combination and Selection" — https://arxiv.org/pdf/1106.1684 — **fetched**, cites Wolpert 1992 — used in: iteration_4, verdict (iv)
- ["Issues in Stacked Generalization"] (Ting & Witten) — https://arxiv.org/pdf/1105.5466 — search-return — used in: iteration_4, verdict (iv)
- ["Stacked Generalization: when does it work?"] (IJCAI-97) — https://www.ijcai.org/Proceedings/97-2/Papers/011.pdf — search-return — used in: iteration_4, verdict (iv)
- [Wolpert 1992] "Stacked Generalization" — https://www.semanticscholar.org/paper/Original-Contribution:-Stacked-generalization-Wolpert/bbc25a700e51984e560eae27df1587baa92e3afe — **NOT fetched** (PDF mirror returned HTTP 425); cited only *through* https://arxiv.org/pdf/1106.1684 — used in: iteration_4, verdict (iv)
- [Shazeer et al.] "Outrageously Large Neural Networks: The Sparsely-Gated MoE Layer" — https://www.researchgate.net/publication/312619873_Outrageously_Large_Neural_Networks_The_Sparsely-Gated_Mixture-of-Experts_Layer — search-return — used in: iteration_4, verdict (iv)
- [Charalampopoulos, Zhang, Harrop, Leung, Sapsis] "Statistics of extreme events in coarse-scale climate simulations via machine learning correction operators trained on nudged datasets" — https://arxiv.org/abs/2304.02117 — **fetched (abs; PDF failed)** — used in: iteration_5, verdict (i)
- [LNF-NO] "Linear–Nonlinear Fusion Neural Operator for PDEs" — https://arxiv.org/html/2603.24143 — **fetched** — used in: iteration_5, verdict (i)
- ["Neural Operators as Efficient Function Interpolators"] — https://arxiv.org/html/2605.07792 — **fetched** — used in: iteration_5, verdicts (i), (v)
- [Cruz et al.] "META-DES: A dynamic ensemble selection framework using meta-learning" (Pattern Recognition) — https://www.sciencedirect.com/science/article/abs/pii/S0031320314004919 — search-return (RG mirror 403) — used in: iteration_5, verdict (iii)
- [statistical downscaling / bias-correction transfer functions] — https://www.sciencedirect.com/science/article/abs/pii/S0921818112002160 ; https://clima.caltech.edu/2023/07/27/unsupervised-downscaling-of-climate-simulations/ — search-return — used in: iteration_5, verdict (i)
- **In-round siblings cited, NOT re-fetched**: `websearches/s6_local/batch_1/report.md` (D1–D3 verdicts; NO-LIDK, U-FNO, LOGLO-FNO, F-Adapter, Kochkov 2021 https://arxiv.org/pdf/2102.01010); `websearches/s1_poisson/batch_2/report.md` verdict (ii) (Gauss–Richardson Extrapolation https://pmc.ncbi.nlm.nih.gov/articles/PMC11985099/ = **preempted**); `docs/reports/MF_Sharp_HighFreq_Report.md:260` (unrolled deconvolution with a learned prior, arXiv:2211.01567 — **not fetched in this loop, must not be cited as evidence**, but it is the in-repo note that first named "fit the actual LF↔HF transfer kernel from training pairs").

**Leads seen but NOT fetched — must not be cited as evidence**: https://arxiv.org/pdf/2601.04510 (phase-field convolution-only surrogate — closest dataset-class match for the padding question); https://arxiv.org/html/2605.08517 ("A Deep Risk Estimator for Known Operator Learning" — the one possibly *data-driven* error estimator seen); https://arxiv.org/pdf/2007.07442 (exactly-periodic BCs by construction); https://arxiv.org/pdf/2606.30821 , https://arxiv.org/pdf/2412.15361 , https://arxiv.org/pdf/1906.10464 (downscaling/bias correction); https://arxiv.org/pdf/2012.15151 (per-instance algorithm selection); https://openreview.net/pdf/c6cf19bdd4fea96b63ecfd29a19199ef909a880b.pdf ("Gate to the Vessel: Residual Experts"); https://pmc.ncbi.nlm.nih.gov/articles/PMC11419638/ (zero-padding compensation algorithms).

## Dead ends

- `https://arxiv.org/pdf/2106.11160` → FlateDecode binary; no `/html/` rendering
  exists for that paper; ResearchGate mirror 403. Padding-study evidence stayed
  search-return grade.
- `https://arxiv.org/pdf/2304.02117` → 5.2 MB binary; `/abs/` worked and gave the
  full abstract (but not the operator class).
- `https://www.biorxiv.org/content/10.1101/172395.full.pdf` (Super Learner) → 403.
- `https://machine-learning.martinsewell.com/ensembles/stacking/Wolpert1992.pdf`
  → HTTP 425 Too Early. **Wolpert 1992 is therefore cited only through a fetched
  paper that cites it**, never as a direct fetch.
- ResearchGate generally (META-DES, "Effects of boundary conditions…", MoE) → 403.
- Query `linear baseline competitive with neural operator benchmark ...` → returned
  only architecture-vs-architecture comparisons; **explicit engine negative** on
  any paper arguing for linear-regression baselines in NO benchmarks. Recorded as
  a gap, which is itself the evidence for verdict (i)'s open part.
- Query `mixture of experts gate saturates degenerate in-sample ...` → returned
  only load-imbalance material; explicit negative on the in-sample-gate framing.

## For the brainstormer

**The brainstormer MUST quote the verdict row above for whatever it proposes.**

1. **The LSI filter arm is a BASELINE, not a method — write it that way or it is
   preempted.** Mechanism is triply published (defect correction + Fourier symbols;
   Wiener deconvolution; ML correction operators on paired coarse/fine sims,
   https://arxiv.org/abs/2304.02117). What no fetched source does is *solve* the
   defect operator in closed form and *score it beside trained neural operators*:
   NH-CSR "provides no zero-parameter linear filter or transfer function
   comparison", LNF-NO's linear branch is gradient-trained "not solved in closed
   form", and the interpolator paper has "**no closed-form linear operator
   fitting**". Cite DeepFDM's under-comparison thesis as the licence to report it.
2. **Circular padding is `preempted (cite)` and self-declared hygiene.** SineNet's
   own words: "a simple yet crucial component". So the card must file it as a bug
   fix with the SineNet ablation numbers (1.50%/4.19% → 1.02%/1.78%) as the
   citation, and its only reportable content is B1-F10's 45–81% measurement plus
   the post-repair delta. **Do not let circular padding be a card's headline.**
3. **The per-sample trust head is the batch's best open surface — and the gap is
   nameable in one sentence.** MAST owns "per-sample MF trust weighting" but is a
   scalar GP with a *geometric* weight and "no involvement with ... PDE solution
   fields"; SelectiveNet owns selective regression but trains the selector
   in-sample; ANCHOR owns error-triggered fallback but is "inherently
   physics-informed, being computed from the PDE residual" (ADR 0009 kills it).
   The open composition is: **a physics-free per-sample scalar, predicted from
   `X` + cheap LF statistics, fitted out-of-fold, gating a field-valued defect
   corrector with the scored copy-LF field as the exact `alpha=0` fallback.**
4. **The held-out-fold gate is Wolpert 1992.** Present the true per-pixel-gate
   test as *correcting B1's protocol*, cite
   https://arxiv.org/pdf/1106.1684 (which cites `wolpert92sg` for exactly this
   rule), and pre-register the oracle ceiling honestly: ≤4.1%, **negative on
   cahn_hilliard**. One genuinely new observation is available for free: classic
   leakage makes a combiner over-confident, whereas B1's in-sample gate made it a
   *provable* no-op — and this is **not** the MoE load-imbalance failure.
5. **Use the climate paper as the mechanism's boundary statement.**
   Charalampopoulos et al. needed nudging because "chaotic divergence ... makes
   datasets from different resolutions incompatible"; MFFP's nested LF/HF ladder
   supplies that compatible pairing by construction. That is B1's M4 stationarity
   condition stated by an independent literature, and it is the honest explanation
   of both why the filter works on 4 panel datasets and why helmholtz shuts off.
6. **Thresholds and framing guards.** `min_claimable_effect`: helmholtz **9.695**
   (report-only — the per-sample arm's best oracle number lives there and cannot
   be claimed), allen_cahn 1.633, pfc 1.151, cahn_hilliard 0.553, fisher_kpp
   0.418. ADR 0007 applies (3–5 variants, contract-tier screen, promote one);
   ADR 0009 rules out any residual-based estimator as a *model*. And per B1's
   cross-stream note 1: **every arm in this card must report `skill_LSI` beside
   its own number**, or the geomean is uninterpretable.
