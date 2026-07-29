# iteration_1 — published spectral+local hybrid operators, and their sharp-field evidence

## Search rationale

Open question 1 of `summary_so_far.md`: establish (adversarially) how
thoroughly "add a local branch to the FNO" is already published, and with what
measured evidence on sharp/discontinuous fields. Three targets chosen because
the in-repo reports name them but never fetched two of them:
`MF_FNO_CNN_Hybrid_Report.md` §6.6 flags **NO-LIDK** as "plausibly *tighter*
FNO+local-conv prior art than anything verified here — not fetched";
`MF_Sharp_HighFreq_Report.md` §1.2 names **U-FNO** as "the single most
consistently validated fix" and **CNO** as the alias-free backbone
replacement. If those are as strong as claimed, "FNO + local branch" cannot be
claimed as a mechanism by this stream at all, and the whole novelty budget has
to move to the multi-fidelity composition.

## Search terms used

1. `neural operator localized integral differential kernels Liu-Schiaffini ICML 2024 local kernels FNO`
2. `U-FNO enhanced Fourier neural operator U-Net path sharp saturation front multiphase flow`
3. `Convolutional Neural Operator CNO alias-free discontinuous transport benchmark beats FNO Raonic`

## Findings per term

### Term 1 — NO-LIDK (localized integral and differential kernels)

- **Liu-Schiaffini, Berner, Bonev, Kurth, Azizzadenesheli, Anandkumar,
  "Neural Operators with Localized Integral and Differential Kernels", ICML
  2024** — https://arxiv.org/abs/2402.16845 ,
  https://proceedings.mlr.press/v235/liu-schiaffini24a.html (PMLR
  235:32576-32594). FETCHED (arXiv abs page + PMLR page; the arXiv PDF and the
  OpenReview PDF both failed to extract — binary / browser-check).
  Fetched content: two discretization-invariant local layers — (1) a
  **differential operator** obtained "under an appropriate scaling of the
  kernel values of CNNs" (stencil scaling), (2) a **local integral operator**
  based on discrete-continuous convolutions. PMLR page, on placement:
  *"Rather than replacing Fourier layers entirely, the localized differential
  and integral kernel layers function as **parallel additions to FNO
  architectures**"*. Motivation, verbatim from the abstract: FNO's *"global
  operations are often prone to **over-smoothing** and may fail to capture
  local details"*, while *"CNNs capture local features but are limited to
  training and inference at a single resolution"*. Result: **relative L2 error
  reduced 34–72%** on 2-D turbulent Navier-Stokes and spherical shallow water.
  **No** mention of few-sample/data-efficiency or multi-fidelity in the
  fetched material; benchmarks are smooth-turbulent, **not** sharp-interface.
- **LOGLO-FNO, "Efficient Learning of Local and Global Features in Fourier
  Neural Operators"**, https://arxiv.org/pdf/2504.04260 (TMLR 12/2025) —
  FETCHED. Confirms the same motif independently: **parallel branches**, a
  local branch using "convolution kernels" beside the global Fourier branch,
  plus explicit **high-frequency-targeted loss terms** to counter spectral
  bias; testing "focuses on problems with sharp discontinuities and
  high-frequency phenomena"; claims comparable-or-fewer parameters. **No
  prominent few-shot / minimal-data claims; no multi-fidelity.**
- Also surfaced (not fetched): SAOT "locality-aware spectral transformer"
  https://arxiv.org/pdf/2511.18777 .

### Term 2 — U-FNO

- **Wen, Li, Azizzadenesheli, Anandkumar, Benson, "U-FNO — an enhanced Fourier
  neural operator-based deep-learning model for multiphase flow"**,
  https://arxiv.org/abs/2109.03697 , *Advances in Water Resources* 2022.
  Search-result summary (not fetched this loop): U-FNO adds a **U-Net
  convolutional pathway inside the Fourier block** so the network "preserves
  global low-frequency structure (via FNO) and infuses high-frequency/local
  information (via U-Net)", motivated by **sharp saturation fronts**. Reported
  more accurate than both plain FNO and a CNN benchmark, and — directly
  relevant to this stream — **"requiring only a third of the training data to
  achieve the equivalent accuracy as CNN"**. Code: github.com/gegewen/ufno.
  (Treat the data-efficiency number as search-summary-grade until fetched.)

### Term 3 — CNO (alias-free convolutional operator)

- **Raonić et al., "Convolutional Neural Operators for robust and accurate
  learning of PDEs", NeurIPS 2023** —
  https://papers.nips.cc/paper_files/paper/2023/file/f3c1951b34f7f55ffaecada7fde6bd5a-Paper-Conference.pdf ,
  https://openreview.net/pdf?id=GT8p40tiVlB . Search-result summary: CNO is
  built to *"mitigate aliasing errors caused by not respecting the
  continuous-discrete equivalence, providing an alias-free architecture
  capable of capturing high-frequency details often lost by spectral
  truncation"*; it outperforms FNO on their Representative PDE Benchmarks. One
  number that matters here: on **Discontinuous Transport OOD, a plain U-Net
  (1.35%) slightly beats CNO (1.61%)** — i.e. on discontinuous data the
  *local* architecture is already at or above the alias-free operator.
- Adjacent hits, not fetched: WHNO (Walsh-Hadamard operator for discontinuous
  coefficients) https://arxiv.org/pdf/2511.07347 ; Res-FNO "dual-view feature
  fusion" https://www.sciencedirect.com/science/article/abs/pii/S1051200424000939 ;
  "Pre-Generating Multi-Difficulty PDE Data for **Few-Shot** Neural PDE
  Solvers" https://arxiv.org/pdf/2512.00564 (flagged for iteration 4).

## Interpretation

"Put a local branch in parallel with the Fourier layer" is **published, peer
reviewed, and quantified** (NO-LIDK, ICML 2024, 34–72% error reduction; U-FNO,
AWR 2022) — so `s6_local` cannot claim the *mechanism*, only a composition.
Two exploitable gaps are already visible: (i) every one of these is
**single-fidelity** and their headline benchmarks are turbulent-but-smooth,
not sharp-interface phase-field; (ii) none of the fetched material addresses
the tiny-N_hf regime, while U-FNO's data-efficiency claim is *relative to a
CNN*, not at N=5.
