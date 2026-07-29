# Iteration 1 — the core mechanism: does test-time residual refinement work?

## Search rationale

`summary_so_far.md` established that (a) the stream's own quantified prior is a
mis-attribution and the placeholder-residual mechanism measured **null**
(-1.5%, inside CI, at 163x inference cost), and (b) a *literal* governing
residual exists for only 1 of 6 panel datasets. So iteration 1 goes at the
three load-bearing questions before any design: **does anyone do field-space
test-time optimization against a real residual on neural-operator outputs**
(Q1); **verify IRNO first-hand** since program.md 12.3 names it as the second
lever and 13.3 forbids memory-citation (Q2); and **what is the known failure
mode** — because if residual minimization is a bad proxy for accuracy, the
whole stream premise changes (Q4).

## Search terms used

1. `test-time optimization neural operator output PDE residual refinement inference-time NITO`
2. `Iterative Refinement Neural Operators Learned Fixed-Point Solvers arXiv 2605.24041`
3. `physics-informed fine-tuning at inference time neural operator overfitting failure worse than base prediction`

## Findings

### Term 1 — test-time residual optimization of operator outputs

Search returned a dense cluster; the mechanism is a **well-populated published
family**, not a gap:

- **PRISMA** — "Beyond Loss Guidance: Using PDE Residuals as Spectral Attention
  in Diffusion Neural Operators", https://arxiv.org/html/2512.01370 . Framed
  explicitly against "the bottleneck of slow **gradient-based test-time
  optimization** routines that use PDE residuals for loss guidance" — i.e. the
  exact mechanism `mf_fno_ptr` implements is the *baseline* this 2025 paper is
  trying to replace, with a gradient-descent-free spectral-attention
  alternative. (search-snippet level; not fetched)
- **Error-Conditioned Neural Solvers (ENS)**, https://arxiv.org/abs/2606.27354
  — **FETCHED**. Two decisive statements:
  - Taxonomy: hybrid methods "target the PDE residual via gradient descent or
    Gauss-Newton steps" (this is `mf_fno_ptr`'s class).
  - **The refutation**: "numerically minimizing the PDE residual can be an
    **unreliable proxy for reconstruction accuracy in ill-conditioned
    systems**", explaining "why residual minimization fails despite achieving
    low residual values". ENS's own answer is to feed the residual **field as
    a network input** at each iteration and learn an update policy, rather
    than descend on it; it claims greatest relative advantage precisely in
    ill-conditioned regimes.
  - (Full PDF fetch failed: `maxContentLength size of 10485760 exceeded`;
    the abstract page fetch succeeded and is the source of the quotes above.)
- **PINO** (Physics-Informed Neural Operator), https://arxiv.org/pdf/2111.03794
  — named by the search summary as having "a test-time optimization phase that
  optimizes the pre-trained operator ansatz for the querying instance of the
  PDE". **PDF fetch FAILED** (returned binary/corrupted content, 8 MB) — so
  PINO is NOT citable from this loop beyond the search-summary paraphrase;
  retry in a later iteration if it becomes load-bearing.

### Term 2 — IRNO verified first-hand (program.md 12.3 lever 2)

https://arxiv.org/abs/2605.24041 , https://arxiv.org/html/2605.24041
(**FETCHED**), official code https://github.com/xiaotianliu-dartmouth/Iterative_Refinement_Neural_Operator .
Liu, Shang, Wang, Ren & Yang; ICML 2026.

- Mechanism confirmed: frozen pre-trained base operator gives `h_0`; a learned
  refinement operator is applied by fixed-point iteration
  `h_{k+1} = h_k + alpha * Phi_theta(x, h_k)`, alpha in {0.2, 0.25}; alpha=0.6
  **diverges** within the training horizon (Sec 4.7.3) — the step size is a
  real stability constraint, not a free knob.
- Progressive spectral loss: weight `rho(w, lambda_k) = 1 + (|w|/|w|_nyq)^lambda_k`
  with `lambda_k` increasing linearly across refinement steps. Ablation:
  VRMSE 0.039 vs 0.051-0.070 for fixed lambda (Table 6).
- Numbers: high-frequency-band normalized error ratio falls to **1.48-2.04%**
  of base by iteration 12 on Active Matter (Table 3) — this is the "~50x"
  claim in the in-repo report, confirmed. TR-2D 45-56% VRMSE improvement;
  Active Matter 51-80%; ERA5 34% RFNE / +19% ACC.
- Cross-operator transfer confirmed (Sec 4.5 / Table 4): IRNO trained on TFNO
  improves FNO predictions by 58.53% on TR-2D **without retraining**.
- **Two facts that define the open space for this stream**:
  1. "The refinement is entirely learned from training data — **no true PDE
     residuals are computed at test time**."
  2. "The paper makes **no mention of coarse-grid, low-fidelity inputs, or
     multi-fidelity training data**. All refinement is post-hoc correction of
     single-fidelity base operator outputs."

### Term 3 — the failure mode and the safeguard

- Search summary (multiple sources incl. https://www.mdpi.com/2077-1312/14/2/201
  and https://www.emergentmind.com/topics/zero-shot-physics-informed-fine-tuning):
  physics-residual training/fine-tuning "ignores the data distribution and
  overfits on the physical equation"; residual use "can bias the operator
  toward those few configurations, leading to overfitting and degraded
  generalization on out-of-distribution inputs".
- The published safeguard is exactly the term `mf_fno_ptr` already has:
  instance-wise fine-tuning with an **"anchor loss" to maintain proximity to
  the pre-trained operator**. So the anchor is prior art, not a novelty — and
  its presence is why ptr's measured effect was ~0: a strong anchor plus a
  weak (placeholder) residual is a no-op by construction.
- No fetch attempted beyond the failed PINO PDF; the MDPI and emergentmind
  items are search-summary level only and are **not** used as citations.

## Interpretation

The mechanism family this stream owns is heavily published (PINO test-time
optimization, PRISMA, ENS, IRNO), and one fetched source states the central
hazard outright: **minimizing the PDE residual is an unreliable proxy for
accuracy in ill-conditioned systems** — which is a direct threat, since
Helmholtz (the one panel dataset with a computable true residual) is the
canonical indefinite/ill-conditioned operator. Meanwhile IRNO is verified as
frozen-base + purely-learned + **single-fidelity**, so the multi-fidelity
composition remains untouched. Next iteration must (i) test the
ill-conditioning threat specifically for Helmholtz, (ii) find what replaces a
PDE residual for the four *time-snapshot phase-field* panel datasets where no
residual is evaluable.
