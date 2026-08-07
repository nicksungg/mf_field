# Iteration 2 — r3s3_lf_value, batch 1

## Search rationale

Turn 1 identified the right theoretical frame (privileged information helps by
accelerating the *rate*, not by adding information about a target the input already
determines) but could only reach it through search-result summaries, because the
canonical LUPI paper is PDF-only and this box has no PDF extractor. Turn 2 therefore
(t1) hunts a **fetchable** statement of the rate claim; (t2) attacks the
identifiability-vs-trainability separation head on, since that is r2s3-B4's closing
question and r3s3's seed direction; (t3) asks the value-of-information question in the
form our panel now has it — *does LF still pay when the parameters fully determine the
solution?*

I also solved the fetch problem: PDFs are now readable by inflating the `FlateDecode`
streams with `zlib` and pulling the text-show operands (pure Python, no extractor).
Everything marked **fetched** below was read that way or via `urllib` + tag-strip.

## Search terms used

1. `unifying distillation and privileged information learning rate O(1/n) versus O(1/sqrt(n)) teacher student`
2. `auxiliary data improves optimization not identifiability distinguishing trainability limit from information limit neural network`
3. `multi-fidelity value of information ablation how much does low-fidelity data help when parameters fully determine solution PDE surrogate`

## Findings

### Term 1 — the rate claim, now fetched

- **Lopez-Paz, Bottou, Scholkopf & Vapnik, "Unifying distillation and privileged
  information", ICLR 2016** — **fetched (PDF body extracted)**
  https://leon.bottou.org/publications/pdf/iclr-2016.pdf ; arXiv record **fetched via
  the arXiv API**: http://arxiv.org/abs/1511.03643v3 ("unifies these two techniques
  into generalized distillation ... theoretical and causal insight").
  Verbatim from the extracted body (whitespace lost in extraction):
  > "For difficult (non-separable) problems the exponent is alpha = 1/2, which
  > translates into machines learning at a slow rate of O(n^-1/2). On the other hand,
  > for easy (separable) problems ... the exponent is alpha = 1, which translates into
  > machines learning at a fast rate of O(n^-1). The difference between these two rates
  > is huge: the O(n^-1) learning rate potentially only requires 1000 examples to
  > achieve the accuracy for which the O(n^-1/2) learning rate needs 10^6 examples. So,
  > given a student who learns from a fixed amount of data n and a function class F, a
  > good teacher can try to ease the problem at hand by **accelerating the learning
  > rate from O(n^-1/2) to O(n^-1)**."
  And on LUPI's mechanism:
  > "Since separable classification admits O(n^-1) fast learning rates, it would be
  > ideal to have a teacher that could supply slack values to us ... the framework of
  > learning using privileged information studies how to leverage these explanations
  > x*_i at training time, to build a classifier for test time that outperforms those
  > built on the regular features x_i alone."
  This is the exact mechanism r3s3 would be measuring: privileged (LF) data present at
  train, absent at test, whose value is a **sample-efficiency/rate** effect.

### Term 2 — separating a trainability limit from an information limit

- **Qi, "Conjugate Learning Theory: Uncovering the Mechanisms of Trainability and
  Generalization in Deep Neural Networks", arXiv:2602.16177 v2 (19 Feb 2026)** —
  **fetched** https://arxiv.org/abs/2602.16177. Relevant claim: derives "a
  model-agnostic **lower bound for the achievable empirical risk**, theoretically
  demonstrating that **data determines the fundamental limit of trainability**", and
  separately characterises how batch size / depth / parameter count / sparsity affect
  the non-convex optimisation. The vocabulary exists in the abstract; it is a general
  DNN theory paper, not a PDE-surrogate or multi-fidelity instance.
- Search returns, not fetched: https://arxiv.org/pdf/2007.02693 (Auxiliary Learning by
  Implicit Differentiation — auxiliary parameters optimised on a *separate auxiliary
  set* because "the goal of auxiliary learning is to improve generalization rather than
  help optimization on the training data" — i.e. the field distinguishes the two axes
  but treats optimisation-help as the *uninteresting* one);
  https://par.nsf.gov/biblio/10542257-identifiability-deep-generative-models-without-auxiliary-information
  (identifiability of deep generative models **without** auxiliary information; nonlinear
  ICA is unidentifiable without an auxiliary signal); https://arxiv.org/html/2403.07404v2;
  https://arxiv.org/html/2607.18305v1 (The Information Shadow — structural limits on
  what models can learn).
- **No usable result** for the exact composition "does the auxiliary/low-fidelity signal
  add information or merely ease optimisation, decided by a matched experiment".

### Term 3 — MF value-of-information when the parameters determine the solution

- Search returns (none fetched this turn):
  https://www.sciencedirect.com/science/article/abs/pii/S1270963824000610 (non-hierarchical
  LF data); https://www.sciencedirect.com/science/article/abs/pii/S1474034625009693
  (LF-guided design of experiments — LF used as prior information to allocate HF samples
  to high-variation regions); https://royalsocietypublishing.org/doi/10.1098/rspa.2023.0655
  (MF reduced-order surrogate modelling; LF models "fail to accurately capture the onset
  of instability and critical transients"); https://arxiv.org/abs/2507.03691 (noise-robust
  MF surrogate modelling for **parametric** PDEs);
  https://findanexpert.unimelb.edu.au/scholarlywork/2282466-efficient-selection-of-low-fidelity-data-for-multi-fidelity-surrogate-models
  ("not all low-fidelity data necessarily improves model performance").
- **No usable result** for the specific condition of our panel: an MF study where the
  parameter/condition vector **provably determines** the HF field (completeness
  certificate), asking what LF can still contribute.

## Interpretation

The rate-vs-information framing is now citable from a fetched primary source
(Lopez-Paz et al. 2016), which means r3s3 must **not** claim that framing as its own —
it is 10 years old and canonical. Conversely, two targeted queries returned nothing for
the composition that is actually ours: LF-at-train value measured on a panel whose
condition vector is *certified complete*, and a matched experiment that decides
information-limit vs trainability-limit. That asymmetry is the shape of a defensible
`preempted-but-MF-composition-open` verdict; turn 3 must try to refute it directly.
