# Websearch Report — Stream `s5_tuning`, Batch 1

**Stream**: s5_tuning
**Batch**: 1
**Total iterations**: 4
**Total WebSearch calls**: 11
**Total WebFetch calls**: 13 (7 yielded usable content, 6 failed or returned
metadata-only — every one noted inline in the iteration files and in Dead ends)
**Cap hit**: no (stopped at 4 of 5 by explicit ENOUGH, `iteration_4.md` §ENOUGH)

**Pre-directed slot** (program.md §12.5, G4 dry-run card): `modes_cap` 12 -> 32 on the
champion recipe `mf_fno_transfer_film`. Prior-art verdict is in "For the brainstormer"
below.

## Search trace

### Turn 1 — is the knob's premise even true?
**Terms chosen** (and why): `summary_so_far.md` Q1-Q3 — the M1 proposal *assumes* more
modes is better while F22 only says the cap doesn't scale, so go at (a) published
mode-count ablations, (b) FNO spectral bias, (c) the field's normative defaults.
- "Fourier Neural Operator number of Fourier modes ablation overfitting truncation study"
  → [see iteration_1.md](iteration_1.md)
  - Key finding: mode-count ablations report **plateaus** (error stops improving past 8
    modes) and **overfitting** (severe train/val divergence past a small mode count),
    with truncation acting as smoothness regularization. [cite:
    https://arxiv.org/pdf/2311.05967 ; https://arxiv.org/pdf/2402.11568]
  - Key finding: per-PDE-family failure diagnosis — sharp-interface PDEs degrade even
    with more modes; phase-field intermediate/plateauing; Poisson improves most
    consistently. [cite: https://arxiv.org/abs/2601.11428 — paraphrase, low confidence]
- "FNO spectral bias fails to learn high frequency modes neural operator"
  → [see iteration_1.md](iteration_1.md)
  - Key finding: **"simply increasing the number of retained Fourier modes is
    insufficient to overcome the spectral bias"** — Fourier-space parameterization biases
    the loss to a few dominant frequencies; with expanded kernels FNO "cannot effectively
    learn the additional parameters to approximate non-dominant frequencies", with error
    curves *rising* near high frequencies inside the truncation zone. [cite:
    https://arxiv.org/abs/2404.07200]
- "neural operator hyperparameter sensitivity benchmark modes width depth PDE"
  → [see iteration_1.md](iteration_1.md)
  - Key finding: serious benchmarks compare operators at **capacity-aligned parameter
    presets**; and **(12,12) modes / width 20 is the canonical 2-D FNO default**, i.e.
    `modes_cap=12` is the field standard inherited from 64^2 benchmarks. [cite:
    https://arxiv.org/html/2510.05995v1 ; https://arxiv.org/pdf/2512.18595]

### Turn 2 — prior art, scarce data, and the transfer setting
**Terms chosen** (and why): §13.3 requires a *fetched* prior-art verdict (iFNO was only
second-hand in the internal docs); ntrain=400 / N_hf=5 makes the small-sample regime
load-bearing; and the champion is an LF-pretrain -> HF-finetune recipe.
- "iFNO incremental spatial and spectral learning ... 2211.15188"
  → [see iteration_2.md](iteration_2.md)
  - Key finding: iFNO **verified first-hand** — grows K and resolution during training
    via an explained-ratio criterion; **10% lower test error with 20% FEWER modes** and
    30% faster training. The mode-count question is published prior art. [cite:
    https://arxiv.org/abs/2211.15188]
- "Fourier neural operator limited training data overfitting number of modes regularization small sample"
  → [see iteration_2.md](iteration_2.md)
  - Key finding: the field's answer to a big mode budget under scarce data is an explicit
    *constraint* on the added parameters (amortized parameterization as "inherent
    regularization"; orthogonal attention for limited data), not bare allocation. [cite:
    https://proceedings.neurips.cc/paper_files/paper/2024/file/d06a797c436cd5136a6f45b063316278-Paper-Conference.pdf ;
    https://arxiv.org/pdf/2310.12487]
- "transfer learning pretrained Fourier neural operator fine-tuning number of modes multi-fidelity"
  → [see iteration_2.md](iteration_2.md)
  - Key finding (**the most actionable of the run**): under standard parametrization the
    **optimal learning rate shifts with mode count** — 1.8e-3 at K=3 down to 7.4e-4 at
    K=24 for FNO-3D on Navier-Stokes; muP-style rescaling by Theta(1/sqrt(d log K))
    stabilizes it. A fixed-LR 12 -> 32 comparison is therefore known to be mis-tuned.
    [cite: https://arxiv.org/html/2506.19396]
  - Key finding: the champion's LF-pretrain/HF-finetune structure is itself published
    multi-fidelity FNO transfer. [cite: https://arxiv.org/abs/2304.06972]

### Turn 3 — panel-specific evidence (sharp 2-D phase field) and the downside mechanism
**Terms chosen** (and why): five of six panel datasets are sharp-2D fronts while the
generic mode literature is Darcy/NS; `sharp__cahn_hilliard/meta.json` names E-UNO as its
own source paper; and aliasing is the concrete mechanism by which 12 -> 32 could hurt.
- "Fourier neural operator phase field sharp interface Allen-Cahn Cahn-Hilliard spectral resolution number of modes"
  → [see iteration_3.md](iteration_3.md)
  - Key finding: on this project's **own Cahn-Hilliard source paper**, plain FNO at
    **(16,16) flat modes** loses by an **order of magnitude** to a U-shaped operator using
    a **per-level mode schedule [[32,32],[16,16],[8,8],[4,4],...]**, and FNO's error is
    "spatially correlated ... particularly along evolving phase boundaries". [cite:
    https://arxiv.org/html/2509.01293v3]
- "selecting number of Fourier modes from power spectrum energy criterion neural operator Nyquist rule"
  → [see iteration_3.md](iteration_3.md)
  - Key finding: mode count should be set by **power-spectrum inspection under the
    Nyquist limit**; 12 (2-D) / 10 (3-D) are the canonical Nyquist-justified values and
    accuracy gains go marginal past a threshold. [cite: https://arxiv.org/pdf/2512.01421
    — from search snippet; the PDF fetch failed to surface this section]
  - Key finding: the principled measurement is the **residual energy spectrum** — the
    summed Fourier energy of the prediction residual equals the normalized MSE. [cite:
    https://arxiv.org/abs/2404.07200]
- "aliasing Fourier neural operator pointwise nonlinearity high frequency spectral neural operator"
  → [see iteration_3.md](iteration_3.md)
  - Key finding: pointwise nonlinearity causes cross-mode aliasing — **beneficial
    in-distribution** (it lets a truncated net work) but producing "spurious
    high-frequency tails" under shift; FNO has an "encode-process-decode" pattern where
    high-frequency output emerges only at late decoder stages. [cite:
    https://arxiv.org/html/2606.00677]
  - Key finding: in nonlinear high-frequency regimes FNOs show artificial dissipation,
    spectral aliasing and broadband error **irreducible regardless of training-set size**.
    [cite: https://arxiv.org/pdf/2604.00689]

### Turn 4 — decoupling modes from capacity; then ENOUGH
**Terms chosen** (and why): 12 -> 32 is a 7.1x spectral-parameter increase, so a win is
confounded with capacity; look for instruments that separate the two.
- "tensorized Fourier neural operator TFNO Tucker low-rank factorization more modes fewer parameters"
  → [see iteration_4.md](iteration_4.md)
  - Key finding: Tucker-factorized spectral weights buy modes without parameters —
    **>100x compression at equal-or-better accuracy, 400x on turbulent NS**, and the
    low-rank constraint acts as regularization: **TFNO matches FNO's test error with 50%
    of the training samples**, with a smaller train-test gap. [cite:
    https://arxiv.org/html/2310.00120 ;
    https://neuraloperator.github.io/dev/modules/generated/neuralop.models.TFNO.html]
- "FNO ablation number of Fourier modes matched parameter count capacity controlled comparison width"
  → [see iteration_4.md](iteration_4.md)
  - Key finding: published work sets modes to the **Nyquist maximum (50 at 101x101)
    explicitly as a control to rule out insufficient spectral resolution** as the cause of
    poor performance — precisely the control this card wants. [cite:
    https://arxiv.org/pdf/2606.08448]
  - Convention (**UNVERIFIED attribution**, search snippet only, do not cite as a paper
    claim): params scale as O(d_c^2 K^2) in 2-D so `d_c·K = C` is used as a fixed-budget
    proxy. Applied to the champion's own code (C=64, K=12 → 768) this gives the
    capacity-matched cap-32 point **C=24, K=32**.
- **ENOUGH** recorded at end of `iteration_4.md`: the direction, the counter-mechanism,
  both fairness confounds with a concrete control, panel-specific evidence, and the
  prior-art verdict are all in hand; turn 5 would add breadth, not decisions.

## Citations summary

- [George, Zhao, Kossaifi, Li, Anandkumar 2022/2024] "Incremental Spatial and Spectral
  Learning of Neural Operators for Solving Large-Scale PDEs" (iFNO) —
  https://arxiv.org/abs/2211.15188 (also https://openreview.net/forum?id=xI6cPQObp0 ,
  https://neurips.cc/virtual/2022/57971) — used in: iteration_2
- [Qin et al. 2024] "Toward a Better Understanding of Fourier Neural Operators from a
  Spectral Perspective" (SpecB-FNO) — https://arxiv.org/abs/2404.07200 (HTML fetched) —
  used in: iteration_1, iteration_3
- [2026] "Forcing and Diagnosing Failure Modes of Fourier Neural Operators Across Diverse
  PDE Families" — https://arxiv.org/abs/2601.11428 — used in: iteration_1 (paraphrase,
  low confidence)
- [Gopakumar et al. 2024] "Plasma Surrogate Modelling using Fourier Neural Operators" —
  https://arxiv.org/pdf/2311.05967 ,
  https://iopscience.iop.org/article/10.1088/1741-4326/ad313a — used in: iteration_1,
  iteration_3
- [Kashefi & Mukerji 2024] "A novel Fourier neural operator framework for classification
  of multi-sized images" — https://arxiv.org/pdf/2402.11568 — used in: iteration_1
- [2025 survey] "Fourier Neural Operators Explained: A Practical Perspective" —
  https://arxiv.org/pdf/2512.01421 — used in: iteration_1, iteration_2, iteration_3
  (snippet-level only; PDF fetch failed to surface the mode-selection section)
- [2025] "Mitigating Spectral Bias in Neural Operators via High-Frequency ..." —
  https://arxiv.org/pdf/2503.13695 — used in: iteration_1
- [2026] "SirenFNO: Efficient and Full Frequency Learning of Fourier Neural Operators" —
  https://arxiv.org/html/2606.11518 — used in: iteration_1
- [2026] "Frequency Bias and OOD Generalization in Neural Operators under a
  Variable-Coefficient Wave Equation" — https://arxiv.org/pdf/2605.12997 — used in:
  iteration_1
- [2026] "Iterative Refinement Neural Operators are Learned Fixed-Point Solvers" (IRNO) —
  https://arxiv.org/pdf/2605.24041 — used in: iteration_1
- [2025] "A comprehensive comparison of neural operators for 3D industry-scale
  engineering designs" — https://arxiv.org/html/2510.05995v1 — used in: iteration_1
- [2025] "Benchmarking neural surrogates on realistic spatiotemporal multiphysics flows" —
  https://arxiv.org/pdf/2512.18595 — used in: iteration_1
- [NeurIPS 2024] "Understanding the Expressivity and Trainability of Fourier Neural
  Operators" —
  https://proceedings.neurips.cc/paper_files/paper/2024/file/14da7aea05debb963b3d8d46449d51a0-Paper-Conference.pdf
  — used in: iteration_2 (**fetch failed; contents NOT cited**)
- [NeurIPS 2024] "Amortized Fourier Neural Operators" —
  https://proceedings.neurips.cc/paper_files/paper/2024/file/d06a797c436cd5136a6f45b063316278-Paper-Conference.pdf
  — used in: iteration_2
- [Xiao et al. 2023] "Improved Operator Learning by Orthogonal Attention" —
  https://arxiv.org/pdf/2310.12487 — used in: iteration_2
- [preprint] "Limitations of Fourier Neural Operators for Nonlinear Structural ..." —
  https://engrxiv.org/preprint/download/7702/12541/10834 — used in: iteration_2
- [Ye et al. 2023] "Multi-fidelity prediction of fluid flow and temperature field based on
  transfer learning using Fourier Neural Operator" — https://arxiv.org/abs/2304.06972 —
  used in: iteration_2
- [2024] "Multi-fidelity Fourier neural operator for ... geological carbon storage" —
  https://www.sciencedirect.com/science/article/abs/pii/S0022169424000350 — used in:
  iteration_2
- [2025] "Pretrain-finetune neural operator for multi-fidelity surrogate modeling of
  structural dynamic systems" —
  https://www.sciencedirect.com/science/article/abs/pii/S0141029625016098 — used in:
  iteration_2
- [2025] "Maximal Update Parametrization and Zero-Shot Hyperparameter Transfer for Fourier
  Neural Operators" (muTransfer-FNO) — https://arxiv.org/html/2506.19396 — used in:
  iteration_2
- [2025] "Equivariant U-Shaped Neural Operators for the Cahn-Hilliard Phase-Field Model"
  (E-UNO; source paper of `sharp__cahn_hilliard`) — https://arxiv.org/html/2509.01293v3 —
  used in: iteration_3
- [2025] "Learning coupled Allen-Cahn and Cahn-Hilliard phase-field equations using
  Physics-informed neural operator (PINO)" — https://arxiv.org/abs/2507.18731 — used in:
  iteration_3
- [review] "Fourier Spectral Methods for Phase Field and Interface Dynamics" —
  https://www.authorea.com/users/957555/articles/1326468/master/file/data/main2/main2.pdf?inline=true
  — used in: iteration_3
- [2024] "An end-to-end deep learning method for solving nonlocal Allen-Cahn and
  Cahn-Hilliard phase-field models" — https://arxiv.org/pdf/2410.08914 — used in:
  iteration_3
- [2026] "Limits of Resolution Equivariance in Fourier Neural Operators" —
  https://arxiv.org/html/2606.00677 — used in: iteration_3
- [2026] "Performance of Neural and Polynomial Operator Surrogates" —
  https://arxiv.org/pdf/2604.00689 — used in: iteration_3
- [Kossaifi et al. 2023] "Multi-Grid Tensorized Fourier Neural Operator for
  High-Resolution PDEs" (MG-TFNO) — https://arxiv.org/html/2310.00120 — used in:
  iteration_4
- [neuraloperator docs] `neuralop.models.TFNO` —
  https://neuraloperator.github.io/dev/modules/generated/neuralop.models.TFNO.html —
  used in: iteration_4
- [2025] "Tensor-GaLore: Memory-Efficient Training via Gradient Tensor Decomposition" —
  https://arxiv.org/html/2501.02379v1 — used in: iteration_4
- [2026] "Multiscale Fourier Neural Operator for Inverse Wave Scattering in Highly
  Oscillatory Media" — https://arxiv.org/pdf/2606.08448 — used in: iteration_4
- [Guibas et al.] "Adaptive Fourier Neural Operators" (AFNO) —
  https://openreview.net/pdf?id=EXHG-A3jlM — used in: iteration_4

## Dead ends

- **"neural operator hyperparameter sensitivity benchmark modes width depth PDE"**
  (turn 1) — returned mostly unrelated architecture papers; its only usable yield was the
  capacity-aligned-preset convention and the canonical (12,12)/width-20 default. Not a
  total dead end, but the lowest-yield term of the run.
- **WebFetch of arXiv:2404.07200 as PDF** — returned undecodable binary; the HTML
  endpoint (`arxiv.org/html/...`) worked. Lesson: prefer `/html/` for arXiv.
- **WebFetch of the NeurIPS 2024 "Expressivity and Trainability of FNO" PDF** — failed
  (undecodable binary). Directly on-topic and still unread; its contents are NOT cited
  anywhere in this report. A follow-up batch should retry via the OpenReview HTML page.
- **WebFetch of arXiv:2512.01421 (practical-perspective survey)** — 8.5 MB PDF; extractor
  returned only background sections and explicitly could not find the mode-selection
  guidance. The Nyquist/12-modes guidance therefore rests on the search snippet only and
  is flagged low-confidence wherever used.
- **WebFetch of arXiv:2304.06972 PDF** — aborted, exceeded the 10 MB content-length cap;
  the `/abs/` page was fetched instead (abstract-level detail only, no mode budget or HF
  sample count).
- **WebFetch of arXiv:2409.14660** — failed; consequently the `d_c·K = C` fixed-budget
  convention could not be attributed to a paper and is recorded as unverified.

## For the brainstormer

1. **PRIOR-ART VERDICT: not novel, and must not be claimed as such — but legitimate as a
   measurement.** The mode-count question is published prior art: **iFNO**
   (https://arxiv.org/abs/2211.15188, verified first-hand this run) grows K during
   training and gets **10% lower error with 20% FEWER modes**; **AFNO** sparsifies modes;
   **MG-TFNO** factorizes them. `modes_cap` 12 -> 32 is therefore a *measurement of this
   project's own spectral bottleneck* (F22), not a mechanism contribution — which is
   exactly what a `tuning`-class card should be, and it stays inside §12.5 (a
   hyperparameter, not a new mechanism/architecture). Note also that **(12,12) modes is
   the canonical 2-D FNO default from the 64^2 Darcy/NS era**, so "12 is arbitrary" is a
   real complaint at 256^2 but is not itself evidence that 32 wins.
2. **The literature predicts this knob will mostly NOT help — write the falsification
   clause to make that outcome informative.** The strongest directly-relevant statement in
   the field is "simply increasing the number of retained Fourier modes is insufficient to
   overcome the spectral bias", with error curves *rising* near high frequencies inside
   the truncation zone (https://arxiv.org/abs/2404.07200); independent ablations report a
   plateau at 8 modes (https://arxiv.org/pdf/2311.05967) and severe train/val divergence
   past a small mode count (https://arxiv.org/pdf/2402.11568). A null or negative result
   is the *expected* result and is a genuine finding under program.md §1 — it converts
   "the gap is knobs" into "the gap is not spectral bandwidth", which redirects
   `s2_beyond_copy` and `s4_hybrid_routing`.
3. **Two known confounds; both are cheap to control and both are pure knobs.**
   (a) **Learning rate**: under standard parametrization the optimal LR *shifts with K* —
   1.8e-3 at K=3 to 7.4e-4 at K=24 (https://arxiv.org/html/2506.19396) — so a fixed-LR
   12-vs-32 comparison is a known mis-tuned comparison and a loss at 32 would be
   uninterpretable. (b) **Capacity**: at C=64 the bump is **7.1x more spectral parameters**
   (9.4M → 67M), against ntrain=400 and **N_hf=5 on ifc_poisson**, where cap 32 is the
   *full* 64^2 spectrum. The capacity-matched control point implied by the champion's own
   `SpectralConv2d` (params ∝ C^2·mh·mw, so d_c·K const at 768) is **C=24, K=32**.
   Consider arms {cap12/C64 (anchor), cap32/C64, cap32/C24} and/or an LR co-sweep — all
   three are `SMOKE`-dict knobs.
4. **Mechanically, the plausible downside is aliasing, and it is measurable.** Modes
   beyond what the data resolves inject unresolved high-frequency energy that folds back
   into the low band through the pointwise nonlinearity
   (https://arxiv.org/html/2606.00677 , https://arxiv.org/pdf/2604.00689 — the latter
   calls the resulting broadband error irreducible regardless of training-set size). This
   gives part 6/7 a concrete probe: **per-band error vs copy-LF before and after the
   bump**, which also directly serves `s2_beyond_copy`'s batch-1 diagnostic.
5. **Panel-specific comparator: a flat cap is not what wins on our own datasets.** E-UNO —
   the cited source paper of `sharp__cahn_hilliard` — beats plain FNO (flat (16,16) modes)
   by an **order of magnitude** using a **per-level mode schedule peaking at 32 on
   full-resolution levels and dropping to 4 on coarse ones**, with FNO's residual error
   concentrated *along phase boundaries* (https://arxiv.org/html/2509.01293v3). A per-block
   mode schedule is already precedented in-zoo (`fno_coreg_residual` uses `(4,8,12,12)`),
   so "schedule" is arguably as much a knob as "flat 32" and is a stronger-prior variant if
   you want one arm to have a real chance of winning.
6. **Set the expected effect per dataset, not globally.** The knob's meaning varies
   enormously across the panel (`summary_so_far.md` table): cap 32 is 67% of available
   modes on helmholtz (96^2), 25% on the three 256^2 sharp datasets, and **100% — the full
   spectrum from 5 HF samples — on ifc_poisson (64^2)**. Expect the overfitting arm of the
   trade-off to bite hardest on `ifc_poisson` and the bandwidth arm to matter most on the
   256^2 sharp fronts. Whatever threshold is written must clear `state/noise_floor.json`,
   which **does not exist yet** (batch 0 pending, `state/gates.md` G3) — so phrase the
   falsification clause qualitatively or gate it on the anchor landing first.
7. **Out-of-scope-but-note**: the published *safe* way to buy modes is low-rank (Tucker)
   factorization of the spectral weights — MG-TFNO reports >100x compression at
   equal-or-better error and **matches FNO test error with 50% of the training samples**
   (https://arxiv.org/html/2310.00120). That is an architectural change (wrong stream under
   §12.5) but it is the natural follow-up if cap 32 wins only at inflated capacity, and
   worth recording as a cross-stream handoff.
