# Iteration 4 — refutation pass on the MF side of all three verdicts

## Search rationale

Iterations 1-3 established the generic homes of the mechanisms (stacking
shrinkage = statistics; context density = AB-UPT; attention-vs-spectral =
geometry-scoped). This turn attacks the **multi-fidelity composition** of each,
because that is where any surviving novelty must live: (1) does any MF neural
corrector fit its blending coefficient on a split held out from the BASE's own
fit? (2) does any MF transformer take a FULL coarse field as cross-attention
context at few HF samples? (3) is there an attention-vs-convolution ablation
inside a coarse-correction network? Every term is phrased to find the paper that
kills the card.

## Search terms used

1. `multi-fidelity neural network blending coefficient fitted on validation split held out from base model training data leakage residual corrector scaling`
2. `transformer multi-fidelity correction full coarse field as context tokens limited high-fidelity samples cross-attention fidelity gap dense conditioning`
3. `ablation replace attention with convolution matched parameters coarse-to-fine correction network which performs better PDE fields`

## Findings

### Term 1 — MF residual correctors are everywhere; the SPLIT question is never addressed
- Returned cluster (search-returns): "Residual Multi-Fidelity Neural Network
  Computing" https://arxiv.org/pdf/2310.03572 (**FETCH FAILED** — 7.3 MB
  undecodable PDF binary; recorded as un-fetched, so its internals are NOT cited),
  also at https://link.springer.com/article/10.1007/s10543-025-01058-9 ;
  "Residual-based error corrector operator ... neural operator surrogates"
  https://www.sciencedirect.com/science/article/abs/pii/S0045782523007193 ;
  MFRNP (ICML 2024) https://github.com/Rose-STL-Lab/MFRNP ; multifidelity GNNs
  https://onlinelibrary.wiley.com/doi/10.1111/mice.13312 ; MF flow matching
  https://arxiv.org/pdf/2605.16118 .
  The engine's own summary of the class: *"Multi-fidelity neural network surrogate
  models ... formulating the correlation between an inexpensive low-fidelity model
  and an expensive high-fidelity model as a possibly non-linear residual
  function"*, and *"Recent adaptive approaches blend multiple experts—linear,
  nonlinear, and residual—via learnable weights."* Learnable = trained jointly by
  gradient descent, **not** fitted on a base-out-of-sample split.
- **Ensemble adaptive gated multi-fidelity neural network** (hydrofoil design),
  https://www.sciencedirect.com/science/article/abs/pii/S002980182502997X —
  search-return only, ScienceDirect paywall (this is the AGMF-Net that B1's
  report flagged as "the closest published thing to MoE gating inside an MF
  network"). It is an **ensemble + gate inside an MF network**, so any claim of
  the form "we introduce a gated MF ensemble" is at risk; but it is
  Bayesian-optimization/scalar-QoI, not field prediction, and remains **uncitable
  as evidence** (never fetched).
- **Explicit negative**: no return, in this or the s6-B2 loop, describes fitting
  an MF blend weight on a split held out from the base network's own fine-tune.
  Three independent phrasings now (s6-B2 turn 4, s4-B2 turn 1, this turn).

### Term 2 — No usable results in the PDE domain
- Every return was vision/audio/diffusion: HyperDiT https://arxiv.org/html/2605.15741 ,
  https://arxiv.org/pdf/2404.12382 , https://arxiv.org/html/2510.02187v1 ,
  cross-resolution land cover https://arxiv.org/pdf/2512.19990 . The engine's own
  synthesis was generic transformer-design advice, and one line of it is worth
  recording as a *hypothesis-consistent* (not citable-as-PDE-evidence) statement:
  *"Aggressive pooling and token reduction may limit fidelity unless compensated
  by high-resolution cross-attention updates"*, and *"Alternative designs utilize
  full encoder tokens as context through cross-attention layers"*.
  **No usable results for MF PDE correction with a dense coarse-field context.**
  This is the third domain-specific negative (iteration 2 term 3 found only
  particle/diffusion analogues; batch-1 found LGFNet, which uses a local sliding
  window + global self-attention on the LF field but is aerodynamics
  surrogate-fusion, not few-HF-sample field correction).

### Term 3 — coarse-correction ablations exist, and they are conv/spectral with NO attention arm
- **P2C2Net**, "PDE-Preserved Coarse Correction Network",
  https://arxiv.org/html/2411.00040 — **FETCHED.** Its corrector is spectral:
  *"we choose FNO as the neural correction operator performed on the coarse
  solution field in such a block."* Table-3 ablation numbers from the fetch:
  regular convolution RMSE **0.1450** vs symmetric-convolution full model
  **0.0064** (~22x); removing the Fourier correction block RMSE **0.1463**, with
  the authors' conclusion *"The network performs poorly when the Fourier block is
  removed, with error levels two orders of magnitude higher"*; and *"removing
  symmetry constraints leads to a significant increase in errors"*.
  Decisive for verdict (iii): the fetch states the paper *"does not employ
  attention mechanisms anywhere in the architecture, nor does it compare
  attention-based approaches against convolutional or spectral methods."*
- Adjacent returns (not fetched): "Learning Neural PDE Solvers with
  Parameter-Guided Channel Attention" https://arxiv.org/pdf/2304.14118 (attention
  over CHANNELS conditioned on parameters — closer to FiLM than to spatial
  cross-attention); "Deep learning of PDE correction and mesh adaption without
  automatic differentiation" https://link.springer.com/article/10.1007/s10994-025-06746-9 .

## Interpretation

The MF composition of all three mechanisms survives refutation, but weakly and
asymmetrically: the *split-repair* gate has a strong generic preemption
(Wolpert, via s6-B2's fetched arXiv:1106.1684) and no MF instance; the
*dense-coarse-field attention context* has no PDE-domain instance at all but a
generic saturation law (AB-UPT); and the *attention-vs-local* head-to-head
**does not exist** — P2C2Net's own coarse-corrector ablation has no attention
arm at all. That last gap is the one genuinely open, cheap, and stream-owned
measurement s4 can make.
