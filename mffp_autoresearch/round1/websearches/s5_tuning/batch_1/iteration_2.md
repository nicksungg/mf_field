# Iteration 2 — Stream `s5_tuning`, Batch 1

## Search rationale

Iteration 1 established that (a) raising the mode count does not by itself defeat FNO
spectral bias (2404.07200), and (b) mode ablations in serious benchmarks are run at
**capacity-aligned** budgets — which our 12 -> 32 bump (7.1x spectral params) is not.
That leaves three things unresolved before the brainstormer can write a defensible
falsification clause:

- **Q5 (prior art)** — `iFNO` is cited second-hand in `docs/proposals/MODELS_TO_TRY.md`
  as already solving "how many modes"; §13.3 requires a *fetched* prior-art verdict, so
  verify it directly rather than trusting the internal doc.
- **Q4a (scarce data)** — panel datasets have ntrain=400 and `ifc_poisson` has N_hf=5;
  does the literature document a mode-count/overfitting interaction specifically in the
  small-sample regime?
- **Q4b (transfer)** — the champion is an **LF-pretrain -> HF-finetune FiLM transfer**
  recipe. Does mode count behave differently under transfer / multi-fidelity finetuning?

Three terms, no truncation needed.

## Search terms used
1. "iFNO incremental spatial and spectral learning Fourier neural operator growing modes 2211.15188"
2. "Fourier neural operator limited training data overfitting number of modes regularization small sample"
3. "transfer learning pretrained Fourier neural operator fine-tuning number of modes multi-fidelity"

## Findings

### Term 1: "iFNO incremental spatial and spectral learning ... 2211.15188"

- [George, Zhao, Kossaifi, Li, Anandkumar 2022/2024] "Incremental Spatial and Spectral
  Learning of Neural Operators for Solving Large-Scale PDEs" (iFNO) — **VERIFIED
  first-hand** (previously only second-hand in `MODELS_TO_TRY.md`). States our exact
  problem verbatim: selecting the frequency set is hard because "too many modes can
  lead to overfitting while too few can lead to underfitting". iFNO **progressively and
  automatically increases the number of frequency modes K and the training resolution
  R**, using an *explained-ratio* criterion to decide when to add modes. Claimed:
  **10% lower test error using 20% FEWER frequency modes, and 30% faster training.**
  URL: https://arxiv.org/abs/2211.15188 ; OpenReview:
  https://openreview.net/forum?id=xI6cPQObp0
- **Prior-art verdict consequence**: a fixed `modes_cap` bump 12 -> 32 is NOT novel and
  should not be claimed as such; it is a *measurement* of this project's specific
  bottleneck. The mechanism that would be novel (learned/scheduled mode growth) is
  published and, under program.md §12.5, out of scope for `s5_tuning` anyway (it is a
  new mechanism, not a knob).

### Term 2: "Fourier neural operator limited training data overfitting number of modes regularization small sample"

- [George et al. 2022] iFNO, restated in the small-data framing — "too few frequency
  modes and low-resolution data hurt generalization, while too many frequency modes and
  high-resolution data are computationally expensive and **lead to over-fitting**".
  URL: https://neurips.cc/virtual/2022/57971
- [NeurIPS 2024] "Understanding the Expressivity and Trainability of Fourier Neural
  Operators" — the expressivity-vs-trainability split for FNO mode/width choices.
  URL: https://proceedings.neurips.cc/paper_files/paper/2024/file/14da7aea05debb963b3d8d46449d51a0-Paper-Conference.pdf
  **WebFetch FAILED** — the PDF came back as undecodable binary; no content extracted.
  Recorded as a known-relevant but unread source (do not cite its contents).
- [NeurIPS 2024] "Amortized Fourier Neural Operators" — amortized parameterization of
  the spectral weights is described as providing "an inherent regularization mechanism
  for resisting overfitting to potential high-frequency noise", i.e. the field's answer
  to large mode budgets is to *constrain* the added parameters, not just allocate them.
  URL: https://proceedings.neurips.cc/paper_files/paper/2024/file/d06a797c436cd5136a6f45b063316278-Paper-Conference.pdf
- [Xiao et al. 2023] "Improved Operator Learning by Orthogonal Attention" — explicitly
  targets the performance decline of neural operators under **limited training data**
  via a regularization mechanism. URL: https://arxiv.org/pdf/2310.12487
- [preprint] "Limitations of Fourier Neural Operators for Nonlinear Structural
  [mechanics]" — negative-result literature on FNO limits. URL:
  https://engrxiv.org/preprint/download/7702/12541/10834
- [2025 survey] "Fourier Neural Operators Explained: A Practical Perspective" —
  practitioner guidance: too many modes "inject unresolved high-frequency energy that
  **aliases back into lower frequency modes through nonlinearities**, and severely
  compromise generalization to different resolutions"; recommends choosing modes by
  **inspecting the power spectrum** and Nyquist constraints. URL:
  https://arxiv.org/pdf/2512.01421

### Term 3: "transfer learning pretrained Fourier neural operator fine-tuning number of modes multi-fidelity"

- [Ye et al. 2023] "Multi-fidelity prediction of fluid flow and temperature field based
  on transfer learning using Fourier Neural Operator" — the champion's exact paradigm
  in the literature: train LF model on abundant cheap data, **fine-tune with a small
  amount of HF data**, exploiting FNO grid-invariance so the transfer works across
  discretizations; reports ~99% accuracy on its field problems. The abstract does not
  state the HF sample count or the mode budget. URL: https://arxiv.org/abs/2304.06972
  (PDF fetch aborted: >10 MB content-length cap; abstract fetched instead.)
- [2024] "Multi-fidelity Fourier neural operator for fast modeling of large-scale
  geological carbon storage" — same LF-pretrain/HF-finetune structure in a different
  domain. URL: https://www.sciencedirect.com/science/article/abs/pii/S0022169424000350
- [2025] "Pretrain-finetune neural operator for multi-fidelity surrogate modeling of
  structural dynamic systems" — ditto. URL:
  https://www.sciencedirect.com/science/article/abs/pii/S0141029625016098
- [2025] **"Maximal Update Parametrization and Zero-Shot Hyperparameter Transfer for
  Fourier Neural Operators" (muTransfer-FNO)** — the most actionable hit of this turn.
  URL: https://arxiv.org/html/2506.19396

**WebFetch (arXiv:2506.19396).** Under **standard parametrization the optimal learning
rate shifts substantially as the number of Fourier modes K grows**: FNO-3D on
Navier-Stokes has optimal LR **1.8e-3 at K=3 falling to 7.4e-4 at K=24** (~2.4x), and
FNO-2D on Darcy shows "a clear shift in the optimal learning rate as K increases".
Their muP-style reparametrization (scale initialization variance and LR by
Theta(1/sqrt(d log K)), d = PDE dimension) makes the optimum stable — ~4.2e-3 across all
K for FNO-3D, "remarkably stable" for FNO-2D. The paper states directly that "naively
transferring hyperparameter across scales can lead to sub-optimal performance" because
"the optimal hyperparameter changes as model scales".

## Interpretation (1-3 sentences)

The single most important operational finding for this card: **changing `modes_cap`
while holding the learning rate fixed is a known mis-tuned comparison** — optimal LR
falls ~2.4x from K=3 to K=24 under the standard parametrization the zoo uses — so a
naive 12 -> 32 run that loses is ambiguous between "more modes don't help" and "the LR
was wrong for 32". Second, iFNO is verified first-hand as prior art for the mode-count
question and even reports its best results at *fewer* modes, so this batch must be framed
as a measurement of the project's own spectral bottleneck, never as a novel mechanism.
Third, the small-data literature consistently pairs large mode budgets with an explicit
regularizer (amortized parameterization, orthogonal attention), which matters at
ntrain=400 and especially at N_hf=5.
