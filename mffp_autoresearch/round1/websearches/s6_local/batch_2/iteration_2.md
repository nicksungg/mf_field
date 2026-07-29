# Iteration 2 — circular vs zero padding on periodic domains (topic (b))

## Search rationale

B1's F10 is the largest quantified headroom item on the family: **45–81% of the
trained corrector's remaining squared error sits within 12 cells of the domain
boundary** on the periodic panel datasets (pfc 0.809 of the squared energy in
34% of pixels; allen_cahn 0.698 in 18%; fisher_kpp 0.453 in 18%), while the
implicitly-periodic FFT/LSI filter shows **no such excess** (0.225 / 0.256,
~= the pixel fraction). Part 7 prescribes circular padding as batch-2 item (1).
The decision this turn must settle is **framing, not feasibility**: is
zero-vs-circular padding on periodic PDE data a *documented pitfall* — in which
case the fix is hygiene and the card must say so — or an unreported effect that
could be claimed? Terms attack (i) the direct comparison, (ii) the boundary-
error-localization signature specifically, (iii) whether a peer-reviewed neural-
PDE paper has an actual padding ABLATION with numbers.

## Search terms used

1. `circular padding versus zero padding convolutional neural network PDE surrogate periodic boundary conditions ablation`
2. `zero padding boundary artifacts convolutional network scientific machine learning periodic domain error concentrated near boundary`
3. `SineNet circular padding crucial component periodic boundary conditions neural PDE surrogate ablation`

## Findings

### Term 1 — the direct comparison: DOCUMENTED, with a dedicated paper
- **"Effects of boundary conditions in fully convolutional networks for
  learning spatio-temporal dynamics"**, https://arxiv.org/pdf/2106.11160 —
  an entire paper on exactly this axis. Search-return quotes: *"the increasing
  use of neural networks as surrogates for physics-related problems calls for an
  improved understanding of boundary condition treatment and its influence on
  network accuracy"*; *"Results reveal a high sensitivity of both accuracy and
  stability on the boundary implementation in recurrent tasks, and the choice of
  the optimal padding strategy is directly linked to the data semantics."*
  **Fetch failed** (arXiv PDF returned FlateDecode binary; ResearchGate mirror
  HTTP 403) — so this is **search-return grade**, recorded as such.
- Also returned: *"Circular padding is similar to periodic boundary conditions
  in PDEs, where values from the opposite boundary of the cell are appended...
  whereas zero padding assumes that there are neighbours with values zero";
  "Convolution with zero padding does not produce translation invariance."*
- PhyCRNet, https://arxiv.org/pdf/2106.14103 — search-return: *"Periodic padding
  helps boost solution accuracy on the boundaries compared with zero-padding
  when extended to all feature maps produced by convolutional operations."*

### Term 2 — the boundary-localization signature
- Search-returns state the mechanism in exactly B1's terms: *"Standard
  zero-padding in convolutional layers destroys physical continuity, introducing
  artificial boundary artifacts"*; *"For periodic domains specifically,
  zero-padding disrupts periodicity, leading to information loss and degraded
  localization performance."*
- **"Towards Spatio-Temporal Extrapolation of Phase-Field Simulations with
  Convolution-Only Neural Networks"**, https://arxiv.org/pdf/2601.04510 —
  search-return; a phase-field (i.e. Allen-Cahn / Cahn-Hilliard class,
  = 2 of this panel's 4 winners) convolution-only surrogate paper surfaced by a
  padding-artifact query. Not fetched; flagged for the builder.
- Zero-padding *compensation* algorithms exist as their own literature:
  https://pmc.ncbi.nlm.nih.gov/articles/PMC11419638/ — *"compensation algorithms
  for zero padding can enhance the performance of deep convolutional neural
  networks by efficiently compensating convolutional output errors due to zero
  padded inputs"*.

### Term 3 — a peer-reviewed ablation with NUMBERS: SineNet (ICLR 2024)
- **SineNet**, https://ar5iv.labs.arxiv.org/html/2403.19507 — **FETCHED.**
  Table 3 padding ablation, Shallow Water Equations, SineNet-8:
  **zero padding 1-step 1.50% / rollout 4.19%; circular padding 1-step 1.02% /
  rollout 1.78%** (~58% rollout-error reduction). Rationale quoted: for periodic
  BCs *"points on opposite boundaries are identified with one another such that
  the field wraps around"*, and without circular padding the model "would waste
  capacity trying to connect spatially distant boundary points that are actually
  adjacent". **Framing (decisive for us): the fetch reports the authors treat it
  as "a simple yet crucial component for achieving optimal performance" —
  essential implementation hygiene, explicitly not a novel contribution**, and
  they draw the analogy to FNO's implicit periodicity assumption.
- Corroborating standard-practice statements: two-phase-flow neural PDE
  surrogates, https://arxiv.org/html/2405.17260v1 — architectures "adapted to
  respect horizontal periodic boundary conditions ... for convolutional models,
  adding appropriate circular padding takes care of this property".
- Exactly-periodic BC enforcement by construction (a stronger alternative to
  padding): https://arxiv.org/pdf/2007.07442 — search-return.

## Interpretation

Topic (b) is **settled and settled against novelty**: circular padding for
periodic PDE data is published, ablated with numbers in an ICLR 2024 paper, and
explicitly framed *by that paper* as hygiene rather than contribution; a
dedicated 2021 study exists on padding/BC treatment in FCN PDE surrogates. The
s6-B2 card must therefore file circular padding as a **bug fix / hygiene
repair** with SineNet as the citation, and its reportable content is only the
*measurement* that a 12-cell zero-padding band held 45–81% of the corrector's
error on this benchmark — never the fix itself. Next turn: per-sample trust
(topic (c)).
