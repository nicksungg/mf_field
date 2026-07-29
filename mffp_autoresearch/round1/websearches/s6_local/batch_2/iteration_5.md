# Iteration 5 (FINAL, cap 5/5) — adversarial prior-art verdicts

## Search rationale

Turns 1–4 built field context. This turn's only job is to try to **kill** the
three batch-2 directions. Adversarial framings chosen deliberately:
- For **(i) the data-estimated LSI defect filter**, the two places it is most
  likely already published are (a) **climate bias correction / spectral
  nudging**, where fitting a transfer function between a coarse model and a fine
  reference is an entire subfield, and (b) **neural-operator papers that ship a
  linear branch or a linear baseline** — if any of them solves that linear map in
  closed form, the arm is dead as a method.
- For **(iii) the per-sample trust head**, the most likely home outside
  selective prediction (turn 3) is **dynamic ensemble selection**, whose whole
  premise is a meta-model predicting per-instance competence.
- **(ii) circular padding** was already targeted for refutation in turn 2 term 3
  (the SineNet ablation search) and is refuted; it is not re-searched here.
- Richardson extrapolation itself is NOT re-searched: sibling
  `websearches/s1_poisson/batch_2/report.md` verdict (ii) already fetched
  Gauss–Richardson Extrapolation (https://pmc.ncbi.nlm.nih.gov/articles/PMC11985099/)
  and returned **preempted**. Cited as an in-round sibling, not re-derived.

## Search terms used

1. `spectral bias correction transfer function estimated from paired coarse and fine simulations climate downscaling linear filter`
2. `linear baseline competitive with neural operator benchmark should report simple linear regression FNO comparison`
3. `dynamic ensemble selection per-instance choose baseline or corrected prediction regression meta-learner predicts which model is better`

## Findings

### Term 1 — climate bias correction: the closest *practice*, and it needs pairing we get for free
- **Charalampopoulos, Zhang, Harrop, Leung, Sapsis, "Statistics of extreme events
  in coarse-scale climate simulations via machine learning correction operators
  trained on nudged datasets"**, https://arxiv.org/abs/2304.02117 — **FETCHED
  (abs; the PDF fetch returned binary and failed).** Abstract verbatim on the key
  point: high-resolution/reanalysis data *"cannot be directly used as training
  datasets to machine learn a correction for the coarse-scale climate model
  outputs, since chaotic divergence, inherent in the climate dynamics, makes
  datasets from different resolutions incompatible"*; they therefore nudge the
  coarse model to build *"a compatible pair of the ERA5 trajectory and the weakly
  nudged coarse-resolution E3SM output that is used as input training data to
  machine learn a correction operator."* The fetched abstract **does not state the
  operator class and reports no linear/zero-parameter baseline**.
  **Strategic reading: an entire paper exists to MANUFACTURE the aligned
  coarse/fine pairing that MFFP's nested LF/HF ladder has by construction** —
  which is exactly B1's M4 stationarity condition, and the reason a single fixed
  operator works here and not in climate.
- Search-return context: statistical downscaling *"creates a transfer function
  derived using observational data and historical climate model simulations to
  adjust the mean and distribution of values"*
  [https://www.sciencedirect.com/science/article/abs/pii/S0921818112002160];
  "Reverse Spectral Nudging" is used *"to match the energy spectrum of the nudged
  solution to that of the coarse-scale solution"* (the spectrum-matching idea, but
  applied to fix training-data mismatch, not as a corrector);
  *"Downscaling climate-model outputs presents challenges because there is no
  direct pairing between coarse- and fine-scale climate data"*
  [https://clima.caltech.edu/2023/07/27/unsupervised-downscaling-of-climate-simulations/].
  Also seen, not fetched: https://arxiv.org/pdf/2606.30821 ,
  https://arxiv.org/pdf/2412.15361 , https://arxiv.org/pdf/1906.10464 .

### Term 2 — does any neural-operator paper solve a linear map in closed form, or report a linear baseline? NO (in what was fetched)
- **"Linear–Nonlinear Fusion Neural Operator" (LNF-NO)**,
  https://arxiv.org/html/2603.24143 — **FETCHED.** Architecturally the nearest
  "linear + nonlinear" hybrid: `u_raw = alpha * (B_L(z) ⊙ B_N(z))`. But
  *"B_L,theta being affine' means it's a learned linear map trained via gradient
  descent like all other parameters—not solved in closed form"*, and *"The method
  contains no coarse-to-fine or hierarchical multi-fidelity structure."* It does
  not preempt a least-squares-solved transfer function.
- **"Neural Operators as Efficient Function Interpolators"**,
  https://arxiv.org/html/2605.07792 — **FETCHED.** Reframes NOs as finite-
  dimensional interpolators; compares against *"MLPs and Kolmogorov–Arnold
  Networks (KANs)"*, and — decisive for us — *"Notably absent are comparisons to
  polynomial/spline interpolation or linear spectral baselines. No closed-form
  linear operator fitting occurs."* Its nuclear-binding-energy application does
  learn WS4 **residuals** rather than absolute values (a correction framing) but
  *"lacks formal multi-fidelity formulation"*.
- **Explicit engine negative** (recorded as such): *"I didn't find a specific
  paper that explicitly discusses or emphasizes the importance of reporting simple
  linear regression as a baseline when comparing neural operator methods like
  FNO."* The nearest fetched licence to report one remains DeepFDM
  (https://arxiv.org/html/2507.21269v1, turn 1): neural PDE solvers *"have not,
  until now, been carefully compared to established numerical PDE methods."*

### Term 3 — dynamic ensemble selection: per-instance competence is published, for classifiers
- **META-DES (Cruz et al., Pattern Recognition)**,
  https://www.sciencedirect.com/science/article/abs/pii/S0031320314004919 /
  https://www.researchgate.net/publication/271448979_META-DES_A_dynamic_ensemble_selection_framework_using_meta-learning
  (**RG fetch failed, HTTP 403 — search-return grade**): *"train a meta-classifier
  to estimate classifier competence on a per-instance basis, using diverse
  meta-features"*; *"these meta-features are extracted from training data and used
  to train a meta-classifier to predict whether a base classifier is competent
  enough to classify an input instance"*; *"using local accuracy estimates alone
  is insufficient to achieve results close to Oracle performance."*
  **Search-return also notes the DES literature "focus[es] primarily on
  classification tasks"** — the mechanism analogue is real, the regression/field
  instantiation is not what these papers do.
- Adjacent, search-return: https://arxiv.org/pdf/2012.15151 (per-instance
  algorithm selection via clustering), https://arxiv.org/pdf/2111.14520 .

## PRIOR-ART VERDICTS (mandatory)

### (i) Data-estimated LSI defect filter (`LF + T*LF`, `T` solved by least squares on paired train solves) as a SCORED arm on an MF operator benchmark
**Verdict: `preempted-but-MF-composition-open (cite)` — and the open part is a
BASELINE, not a method.**
- Preempted at the mechanism level, three independent ways, all fetched or
  search-return in this loop: classical **defect correction + Fourier-symbol
  comparison of coarse vs fine operators**
  [https://www.researchgate.net/publication/255595433_COARSE_GRID_APPROXIMATION_GOVERNED_BY_LOCAL_FOURIER_ANALYSIS ,
  https://www.sciencedirect.com/science/article/abs/pii/S0045782522001967 — turn 1];
  **Wiener deconvolution of a blur, including as a learnable layer**
  [https://arxiv.org/html/2103.09962v2 — turn 1]; **ML correction operators for
  coarse simulations trained on paired coarse/fine data**
  [https://arxiv.org/abs/2304.02117 — fetched this turn]. Plus, from batch 1,
  learned coarse-grid correction [https://arxiv.org/pdf/2102.01010], and from the
  s1 sibling, Richardson/GRE [https://pmc.ncbi.nlm.nih.gov/articles/PMC11985099/].
- **What remains open**: no fetched source (a) **solves** the coarse→fine defect
  operator in closed form from paired nested solves and (b) **scores it beside
  trained neural operators on an MF field-prediction benchmark**. The closest
  learned analogue, NH-CSR [https://arxiv.org/html/2411.07576v2], *"provides no
  zero-parameter linear filter or transfer function comparison"*; LNF-NO's linear
  branch is gradient-trained, not solved [https://arxiv.org/html/2603.24143]; the
  interpolator-reframing paper has *"no closed-form linear operator fitting"*
  [https://arxiv.org/html/2605.07792]; and the engine returned an explicit
  negative on "report linear regression as an NO baseline".
- **Mandatory framing for the card**: claim **zero method novelty**. The
  contribution is a *measured floor* — "this MF composition has a zero-parameter
  closed-form floor, and on 3 of 4 datasets it is below the trained model" — with
  DeepFDM's under-comparison thesis [https://arxiv.org/html/2507.21269v1] as the
  licence to report it. Any card that says "we introduce an LSI defect filter"
  will be preempted on sight.

### (ii) Circular-padding repair on the periodic datasets
**Verdict: `preempted (cite)` — hygiene, not a contribution.**
- **SineNet (ICLR 2024)**, https://ar5iv.labs.arxiv.org/html/2403.19507 —
  fetched, Table 3, SWE, SineNet-8: **zero padding 1-step 1.50% / rollout 4.19%
  vs circular 1.02% / 1.78%**, and the authors themselves call it *"a simple yet
  crucial component for achieving optimal performance"*, i.e. **essential
  implementation hygiene rather than a novel contribution**. A dedicated study of
  padding/BC treatment in FCN PDE surrogates exists
  [https://arxiv.org/pdf/2106.11160 — fetch failed, search-return: *"high
  sensitivity of both accuracy and stability on the boundary implementation"*],
  and PhyCRNet states periodic padding *"helps boost solution accuracy on the
  boundaries compared with zero-padding"* [https://arxiv.org/pdf/2106.14103].
- **What remains open: nothing about the fix.** The only reportable content is
  B1's *measurement* — that zero padding held **45–81% of a defect corrector's
  remaining squared error** in a 12-cell band while an implicitly-periodic FFT
  filter showed no such excess — and the post-repair delta. File under "we fixed a
  known bug and quantified what it cost us".

### (iii) Per-sample trust head (predict `alpha_i` from `X_i` + cheap LF-field statistics, fitted out-of-fold, copy-LF fallback)
**Verdict: `preempted-but-MF-composition-open (cite)`.**
- Preempted components: **selective regression with a selection head**
  [SelectiveNet, https://ar5iv.labs.arxiv.org/html/1901.09192 — fetched];
  **per-sample MF trust weighting between corrected-LF and an HF model**
  [MAST, https://arxiv.org/html/2602.20974 — fetched]; **per-instance competence
  meta-learners** [META-DES,
  https://www.sciencedirect.com/science/article/abs/pii/S0031320314004919 —
  search-return]; **error-estimator-triggered fallback for operators**
  [ANCHOR, https://arxiv.org/html/2512.19643v2 — fetched].
- **What remains open, precisely**: every fetched instance misses on a stated
  axis. MAST is *"a scalar-output Gaussian process surrogate, not a field or
  operator model"* with a weight *"derived from distance and cost ratios, not
  learned from data features"*, and it trusts LF *far* from HF samples (a
  design-space device, not a validity estimate for a defect operator).
  SelectiveNet trains all heads *"jointly on the same data end-to-end ...
  not on held-out data"* — the exact defect B1 diagnosed. ANCHOR's estimator is
  *"inherently physics-informed, being computed from the PDE residual"*
  (**ADR-0009-disqualified**) and decides *"per-timestep across the entire spatial
  domain simultaneously—not per-pixel or per-sample"*. META-DES is classification.
  So: **a data-driven, physics-free, per-SAMPLE scalar, fitted out-of-fold, that
  decides whether a field-valued defect corrector is applied at all, with the
  scored copy-LF field as the exact fallback**, is not in any fetched source.
- **Pre-registration the card must carry**: B1's oracle numbers bound the prize
  (helmholtz 0.1623 vs copy-LF 0.3295; pfc -22.8%), and helmholtz's
  `min_claimable_effect` is **9.695** so no numeric claim is possible there —
  the arm is a *mechanism* claim on the panel's 4 winners plus a report-only
  helmholtz number.

### (iv) Moving gate training to a held-out fold (part 7 item 3)
**Verdict: `preempted (cite)` — it is the founding rule of stacking; report as a
protocol bug fix.**
- Out-of-fold construction of level-1 data is **Wolpert 1992's** defining
  requirement, confirmed via a fetched paper that cites it for exactly this rule
  [https://arxiv.org/pdf/1106.1684 — *"the combiner must be trained on
  predictions from base classifiers applied to held-out data, not the training
  instances used to build those classifiers"*, citing `wolpert92sg`], with the
  failure named in the stacking literature [*"Training the combiner (meta-learner)
  with the same data instances which are used for training the base classifiers
  will lead to overfitting"* — https://arxiv.org/pdf/1105.5466 ,
  https://www.ijcai.org/Proceedings/97-2/Papers/011.pdf , search-return].
- **What remains open**: only the *direction* of the artifact. Classic stacking
  leakage makes a combiner **spuriously confident**; B1's in-sample gate instead
  made the gate a **provable no-op** (uniform-gate landscape argmin exactly
  `c = 1.0` on fit/val/test, `J(0)` the maximum). Worth one sentence in the card;
  not worth a novelty claim. Note also this is **NOT** the MoE gate-degeneracy
  failure (load imbalance, auxiliary balancing loss) — the engine returned an
  explicit negative on the "gate always trusts the expert because it is scored
  in-sample" phrasing.

## Cap note

**Iteration cap reached (5/5).** 15 WebSearch calls (3 per turn; one malformed
call in turn 1 errored before reaching the engine and is not counted),
14 WebFetch attempts of which 9 succeeded. All verdicts above rest on sources
that appear with URLs in `iteration_1.md`–`iteration_5.md`.
