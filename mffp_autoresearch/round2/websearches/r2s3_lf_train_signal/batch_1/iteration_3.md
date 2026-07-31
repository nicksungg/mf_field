# iteration_3 — `r2s3_lf_train_signal`, batch 1

## Search rationale

Iteration 2 settled the distillation branch. Turn 3 covers the other two
mechanisms named in program.md §12.3: (i) **auxiliary multi-fidelity losses /
joint LF+HF prediction from the condition vector** — which, on a fully nested
sharp ladder, is literally "predict the same solution at 3 resolutions from the
same x"; (ii) whether a **coarse-to-fine target-resolution curriculum** is
established prior art (this is the only information-theoretically defensible
reading of nested-LF supervision); and (iii) whether anyone reports the
**matched with/without-LF ablation** that round-2 success criterion 1 demands,
at N_hf of order 5.

## Search terms used

1. `multi-fidelity DeepONet parametric input predict low and high fidelity jointly auxiliary head multi-task`
2. `coarse-to-fine curriculum training target resolution neural PDE surrogate spectral bias low-pass supervision schedule`
3. `multi-fidelity neural network ablation with and without low-fidelity data value of low fidelity data 5 high-fidelity samples`

## Findings per term

### Term 1 — joint / multi-task MF prediction from parametric input

- **[MAJOR] Meng & Karniadakis, "A composite neural network that learns from
  multi-fidelity data: Application to function approximation and inverse PDE
  problems"** — https://arxiv.org/abs/1903.00104 . FETCHED (abstract page).
  Three coupled networks: NN₁ trained on the **low-fidelity data** to map the
  parameter/coordinate input to the LF value, coupled to two HF networks (one
  with, one without activations) that learn the nonlinear and linear parts of
  the LF→HF correlation, with a relaxation parameter mixing them. Fetch summary:
  the LF network "processes input parameters/coordinates to generate
  predictions"; LF data "is primarily used during training"; the design allows
  the composite "without requiring explicit low-fidelity solves at inference
  time."
  **This is the canonical preemption of "learn LF from the condition vector and
  compose it with an HF correction" — i.e. of the generic mechanism behind BOTH
  r2s2's stacking and any r2s3 joint-LF+HF-head design.** Scope limit that keeps
  something open: it is pointwise function approximation / inverse PDE problems
  in low dimension, not (H,W) field output, and not N_hf = 5 with a 400-sample
  nested ladder.
- **Synergistic Learning with Multi-Task DeepONet for Efficient PDE Problem
  Solving** — https://arxiv.org/html/2408.02198v1 . Multi-task DeepONet: one
  network, multiple output tasks/heads. Occupies the "multi-task heads on a
  shared operator trunk" slot in general, though the tasks are different PDEs,
  not different fidelities of the same solution.
- **Multifidelity DeepONets** — Howard et al., J. Comput. Phys. 2023,
  https://dl.acm.org/doi/10.1016/j.jcp.2023.112462 (the arXiv:2204.09157 already
  cited in `docs/reports/MF_Sharp_HighFreq_Report.md` §2.3). Search snippet:
  "the input augmentation approach appends the **low-fidelity prediction** to the
  trunk net inputs to make the residual operator easier to learn" — note
  *prediction*, not solve, consistent with the Meng-style composite.
- MF-DeepONet fusing simulation + monitoring data
  (https://arxiv.org/pdf/2310.00057 / ScienceDirect S0952197624003142): LF subnet
  on FE simulations, HF subnet on monitoring data — again LF-subnet-as-surrogate.
- Data-efficient MF-DeepONet with physics-guided subsampling
  (https://arxiv.org/pdf/2503.17941) — already in the in-repo report as [LF-11].
- DeepONet MF residual learning: https://arxiv.org/pdf/2302.12682 .

### Term 2 — coarse-to-fine / frequency-progressive supervision

- **Predictivity and Utility of Neural Surrogates of Multiscale PDEs** —
  https://arxiv.org/html/2604.20061v1 . FETCHED. It is a *critical perspective*
  paper, not a method paper: no three-phase coarse-to-fine recipe, no coarse-grid
  auxiliary targets. It does state that "coarse graining introduces a deeper
  problem: **irreversible information loss**" — a direct, citable warning about
  what nested-LF supervision can and cannot supply.
- Incremental Spatial and Spectral Learning of Neural Operators (iFNO) —
  https://openreview.net/pdf?id=xI6cPQObp0 : progressively grows spatial
  resolution and Fourier modes during training. Nearest neighbor to a
  "coarse-target curriculum", but it is a *mode/resolution schedule on one
  dataset*, not supervision from separately-solved coarse fields. (Repo caveat,
  program.md §13.2: the mentor's off-repo iFNO results are unknown-but-poor;
  never cite in-repo absence about them.)
- Spectral bias in physics-informed and operator learning: analysis and
  mitigation guidelines — https://arxiv.org/html/2602.19265v1 : surveys
  "frequency-progressive training curricula" as an established mitigation class.
- **The "79% error reduction from coarse-to-fine" phrasing in the search
  engine's synthesis could NOT be attributed to any fetched paper** (2604.20061
  does not contain it). Recorded as NOT citable.
- Correcting neural-operator spectral bias via diffusion posterior sampling —
  https://arxiv.org/html/2606.03936 (out of scope: pre-falsified diffusion-prior
  lever, program.md §5).

### Term 3 — matched with/without-LF ablations at tiny N_hf

**No usable results for the specific ablation.** The MF-NN literature returned
(composite MFNN https://arxiv.org/abs/1903.00104 ; MF-BNN
https://arxiv.org/pdf/2012.13294 and https://arxiv.org/pdf/2407.05684 ;
MFPC-Net https://arxiv.org/pdf/2010.01378 ; MF data aggregation CNN
https://www.sciencedirect.com/science/article/abs/pii/S0045782521007015 ;
MF interatomic potentials https://arxiv.org/html/2409.07947v1 ; MF molecular
property GNN transfer https://www.nature.com/articles/s41467-024-45566-8)
uniformly *assumes* LF helps and reports MF-vs-HF-only accuracy on curated
tasks; none returned a matched-architecture, matched-budget with/without-LF
value-of-information accounting across a multi-PDE panel, and none at the
N_hf ≈ 5 field-prediction regime. This is consistent with round-2 success
criterion 1 being a genuine contribution rather than a re-measurement.

## Interpretation

The composite/joint MF architecture that learns LF from the parameter input and
composes a correction is **thoroughly preempted** (Meng & Karniadakis 2019 and
the MF-DeepONet line) — a joint LF+HF-head proposal is a rebadge risk on
literature grounds, independent of the §5.10 in-repo rebadge check. What is not
preempted: (a) that composition at *field* output with N_hf = 5 and a nested
400-sample ladder, (b) coarse-solve fields as auxiliary *targets* (as opposed to
resolution/mode schedules on one dataset), and (c) the matched value-of-LF
ablation itself, for which turn 3 found no prior art at all.
