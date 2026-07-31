# Iteration 3 — `r2s2_stacked` / batch 1 (start of §3.3 refutation work)

## Search rationale

Iterations 1–2 searched the *PDE-solver* vocabulary and found only solver-in-the-loop
hybrids. But the "predict the LF response with a surrogate, then correct it to HF" idea is
native to the **multi-fidelity statistics / MF-neural-network** literature, where the LF
model is itself emulated. If the mechanism is preempted anywhere, it is there. Targeted at
refuting novelty of the pre-directed B1 (condition → pseudo-LF → corrector): (1) composite
MF neural networks (Meng & Karniadakis lineage); (2) nonlinear autoregressive MF GPs (does
prediction use the LF *emulator* posterior rather than an LF run?); (3) the operator-learning
version (MF-DeepONet with predicted LF fed to a residual subnet).

## Search terms used

1. `composite neural network learns from multi-fidelity data low-fidelity network output fed into high-fidelity network Meng Karniadakis`
2. `nonlinear autoregressive multi-fidelity Gaussian process NARGP low-fidelity emulator posterior used at prediction no low-fidelity simulation required`
3. `multi-fidelity DeepONet predicted low-fidelity field input to high-fidelity operator inference without low-fidelity solve`

## Findings

### Term 1 — composite MF neural network

- **Meng & Karniadakis (2020), "A composite neural network that learns from multi-fidelity
  data", JCP 401:109020**, https://arxiv.org/abs/1903.00104 — abs fetched. Architecture per
  the fetched abstract: three networks — "the first NN trained using the low-fidelity data and
  coupled to two high-fidelity NNs, one with activation functions and another one without, in
  order to discover and exploit nonlinear and linear correlations". The abs fetch could **not**
  confirm the inference-time dataflow (whether NN_L's prediction is what NN_H consumes at
  test); a follow-up fetch of the PDF returned unparsable binary. **Status: mechanism is
  clearly "LF network output → HF networks", inference-time LF-free operation is strongly
  implied but NOT verbatim-verified here.** Treated below as a *nearest neighbour*, not a
  clean kill.

### Term 2 — NARGP / MF GPs

- **NARGP reference implementation**, https://github.com/paraklas/NARGP — README fetch gives
  the reference paper: Perdikaris, Raissi, Damianou, Lawrence, Karniadakis, "Nonlinear
  information fusion algorithms for data-efficient multi-fidelity modelling". README did not
  contain the prediction-time detail.
- Search snippet (unverified, snippet-level): NARGP writes level q as
  `g_q(x, f_{*q-1}(x))` where `f_{*q-1}` is **the GP posterior from the previous level**, and
  "most methods still require GPs as low-fidelity surrogate models". If that holds verbatim,
  scalar-valued MF surrogates have used an *emulated* LF input at prediction since 2017.
  Flagged as snippet-level — not usable as a citation on its own.
- Other MF-GP hits (not fetched): https://arxiv.org/pdf/2010.08349,
  https://iopscience.iop.org/article/10.1088/2632-2153/ad7ad5,
  https://arxiv.org/pdf/2603.22050 (MAGPI), https://arxiv.org/pdf/2306.03144 (MF-Box).

### Term 3 — MF-DeepONet with predicted LF

- **Xu, Cao, Yuan, Meschke (2023), "A multi-fidelity deep operator network (DeepONet) for
  fusing simulation and monitoring data"**, https://arxiv.org/abs/2310.00057 — abs fetched.
  "The low-fidelity outputs serve as inputs to the high-fidelity component, which learns the
  discrepancy". Search snippet (same paper family) adds: "at the offline stage, the
  low-fidelity subnet is trained using finite element simulations, and **at the online stage,
  the pre-trained low-fidelity subnet is loaded as a frozen module with only the residual
  subnet trained** using high-fidelity monitoring data" — i.e. **frozen LF *emulator* +
  trained residual corrector**, exactly the r2s2 topology, with the LF *simulation* replaced
  by a network. The fetched abstract confirms the composition and the frozen-LF-subnet
  framing; it does not spell out inference-time solver-freedom in the abstract text.
- **Yang, Lee, Kang, "Physics-Guided Multi-Fidelity DeepONet for Data-Efficient Flow Field
  Prediction"**, https://arxiv.org/html/2503.17941v1 — **VERIFIED BY HTML FETCH**. Two-phase:
  LF pretrain, then "freezes the pre-trained branch and trunk parameters" with "only the merge
  network trainable"; ablation over **fine-tuning (merge only) vs full-tuning vs linear
  probing**, fine-tuning best, "43.7% improvement … compared to single-fidelity training".
  Crucially, the paper *positions itself against* "residual-learning frameworks that
  sequentially combine low and high-fidelity predictions" and states "only the final HF
  DeepONet model in Phase 2 is needed for predictions" — direct evidence that the sequential
  predicted-LF→corrector composition is an **established, named baseline class** in operator
  learning, and that a frozen/partial/full-tuning ablation over MF stages is published.
- Other MF-DeepONet hits (not fetched, ScienceDirect paywalled):
  https://www.sciencedirect.com/science/article/pii/S0021999123005570 (Multifidelity deep
  operator networks, JCP), https://www.sciencedirect.com/science/article/abs/pii/S0045782525005262.

## Interpretation

The mechanism is **not novel**: composing a learned LF predictor with a residual/HF corrector,
with the LF stage frozen, is published in both MF-NN (Meng & Karniadakis) and MF-DeepONet
(Xu et al. 2023) form, and the freeze-vs-tune ablation axis is published too (Yang et al.
2025). What none of these do is *reuse a corrector that was trained on real coarse solves* and
*account for the resulting input distribution shift* — the pseudo-LF-vs-real-LF gap. Iteration
4 must test whether that specific accounting is published, and fix the final verdicts.
