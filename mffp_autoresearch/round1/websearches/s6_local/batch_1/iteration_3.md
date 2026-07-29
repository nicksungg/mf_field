# iteration_3 — composition: parallel vs sequential, gating, and the two-stage failure mode

## Search rationale

Open question 3, and the direct diagnosis job ADR 0011 assigns me. The
mentor's report proposes a **sequential** FNO->CNN with a physical LF field at
the boundary; NO-LIDK/U-FNO are **parallel-inside-the-block**. Whether that
distinction is real (and whether the sequential form has a known failure mode)
decides what the brainstormer may propose. Term 3 targets the mentor report's
own §5.1 risk ("exposure bias at the stage boundary") to see whether it is a
documented failure or a speculative one — it is the difference between "the
recipe is known-bad" and "the recipe is known-bad *unless* trained a specific
way".

## Search terms used

1. `SINO spectral starter module local convolutional iterator neural operator truncation compensation arXiv 2606.18305`
2. `hybrid neural operator gated fusion spectral branch and convolution branch learnable gate per location routing PDE`
3. `two-stage coarse-to-fine surrogate refiner trained on ground-truth coarse input exposure bias compounding error train on predicted inputs`

## Findings per term

### Term 1 — SINO (the closest sequential spectral->local architecture)

- **Qin et al., "Starter-Iterator Neural Operator: A Unified Architecture for
  High-Fidelity Forward and Inverse PDE Problems", arXiv:2606.18305** —
  https://arxiv.org/html/2606.18305 — FETCHED. Verbatim structure: starter
  `S_theta` = learnable Fourier filtering keeping low modes via projection
  `P_K`; iterator `I_theta(u,f) := u + B_theta(f - A_theta u)` implemented with
  **lightweight CNN blocks**, i.e. a preconditioned-residual sweep;
  composition `G_theta = I_theta^N o (S_theta, Id)` — **sequential, unrolled,
  weight-shared** across refinement steps. Training: **end-to-end joint, a
  single relative-L2 loss**; no staged training, no separate losses.
  "High-fidelity" means **accuracy**, not multi-fidelity: "lacks explicit
  multi-fidelity data or coarse-solver comparisons". **No few-sample
  experiments. No FiLM / parameter-vector conditioning.**
  This confirms `MF_FNO_CNN_Hybrid_Report.md` §6.1's characterization from a
  fresh fetch, and sharpens it: SINO's iterator is a *residual solver sweep
  driven by the forcing f*, not a refiner consuming a physically distinct
  coarse solve.
- Adjacent: "Spectral-inspired Operator Learning with **Limited Data** and
  Unknown Physics" https://arxiv.org/abs/2505.21573 — flagged for iteration 4.

### Term 2 — gated / routed spectral-vs-local composition

- **U-HNO, "A U-shaped Hybrid Neural Operator with Sparse-Point Adaptive
  Routing for Non-stationary PDE Dynamics", arXiv:2605.12965** —
  https://arxiv.org/abs/2605.12965 — FETCHED (abs page; the PDF fetch returned
  raw binary). Verbatim from the abstract: *"at every spatial location, a
  per-pixel hard mask selects whether the global Fourier branch or the local
  multi-scale Gaussian branch should dominate"*, and *"the sparsity ratio is a
  function of the local contrast of the routing signal, so smooth and
  **shock-aligned** regions receive different mixtures of global and local
  computation"*. Motivation is exactly this stream's: Fourier is good at
  long-range and bad at sharp features; local recovers detail but loses
  propagation stability. Losses: pointwise + finite-difference **H1 gradient
  term** + band-wise spectral consistency regularizer. **Not multi-fidelity.
  No identity / no-harm guarantee.** (Independently re-fetched here; also on
  file in `websearches/s4_hybrid_routing/batch_1/`.)
- Same family, not fetched: TF-SNO time-frequency gated spectral NO
  https://arxiv.org/pdf/2606.21189 ; Spectral Gating Networks
  https://arxiv.org/html/2602.07679 (learnable gate between a low-frequency
  base path and an RFF high-frequency path); Adaptive Memory Gate for NOs
  https://arxiv.org/html/2606.13443 (content gate + frequency-aware gate).
  Conclusion from the volume: **learnable spectral-vs-local gating is a
  crowded 2026 subfield.**

### Term 3 — exposure bias at a stage boundary (is the mentor's §5.1 risk real?)

- Documented, and named. From the fetched-search summary of **"Learning to
  Refine: Spectral-Decoupled Iterative Refinement Framework for Precipitation
  Nowcasting"** https://arxiv.org/pdf/2606.02661 : *"exposure bias occurs when
  training relies on **ground-truth low-frequency conditions** but inference
  uses model-generated ones"*, causing errors to accumulate "closely
  resembling the exposure bias phenomenon in sequence modeling". The
  documented mitigation is a **curriculum**: feed the fine stage ground-truth
  coarse outputs first, then transition to predicted ones (coarse-to-fine
  progressive training).
- Also surfaced: DiffRefiner https://arxiv.org/html/2511.17150v1 (two-stage
  coarse proposal + diffusion refiner); "Rethinking Refinement: Correcting
  Generative Bias without Noise Injection" https://arxiv.org/html/2601.21182v1 .

## Interpretation

Three compositions are separable and all three have published instances:
**parallel-in-block** (NO-LIDK, U-FNO), **sequential-unrolled-shared-weights,
one joint loss** (SINO), and **per-pixel routed** (U-HNO). The mentor's design
is a fourth: sequential with a **physically meaningful LF field** at the
boundary and **separately supervised** stages — which is exactly the form the
literature warns about (exposure bias) and which SINO deliberately avoids by
training end-to-end. In this benchmark the exposure-bias risk is **avoidable
for free**, because the true LF field is a real dataset input at test time,
not a stage-1 prediction — a distinction the mentor's report did not draw.
