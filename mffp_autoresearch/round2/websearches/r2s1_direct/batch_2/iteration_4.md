# Iteration 4 — refutation turn 1 (E1 band gains, E3 control arm, E2 output form)

## Search rationale

Three candidate directions are now explicit (they follow directly from B1's
`7_gap_and_future.next_direction`, items 1-3):

- **E1** — out-of-fold **per-spectral-band gain calibration** of a frozen
  condition→field predictor's point output, with the fitted gain vector
  reported as an identifiability diagnostic.
- **E2** — **training-free, statistic-selected output parameterization**:
  centering form (unit-direction x amplitude vs plain additive) chosen by
  ||mean field||/geomean||y||, rank chosen by the condition-identifiable POD
  rank, *before* training.
- **E3** — a **mandatory ~10^2-parameter closed-form control arm** (PCA/POD +
  ridge from the condition) that any capacity claim must beat, with the
  capacity claim localized to the one dataset where it survives
  (`sharp__cahn_hilliard`).

Each term below is aimed at refuting one of them.

## Search terms used

1. `wavenumber band dependent rescaling of predicted field spectrum using validation data energy spectrum correction surrogate turbulence` (targets E1)
2. `neural operators fail to beat simple baselines benchmark critique linear regression control arm PDE surrogate` (targets E3)
3. `choosing output parameterization magnitude direction decomposition normalize target norm neural network field regression` (targets E2)

## Findings

### Term 1 (E1) — band-dependent rescaling of a predicted spectrum

**No usable results.** The returns are turbulence-physics spectrum papers
(band-wise assessment of turbulence-radiation interaction
https://www.sciencedirect.com/science/article/abs/pii/S0022407324001274 ;
spatio-temporal spectra of wall-bounded turbulence https://arxiv.org/pdf/1606.02456 ;
dissipation-range spectra https://arxiv.org/pdf/1705.04917), which analyze
*physical* spectra, not held-out-fitted corrections to a learned predictor.
The engine reported no paper on "rescaling predicted field spectra using
validation data for surrogate correction". Combined with iteration 1 (TF-SNO's
gate is in-architecture; FreqNO-DPS needs test observations) and iteration 3
(arXiv:2505.15354's post-training corrections are time-domain and global),
this is now three independent misses for the band-resolved post-hoc gain.

### Term 2 (E3) — the control-arm / weak-baseline critique

Top results:
- **Weak baselines and reporting biases lead to overoptimism in machine
  learning for fluid-related PDEs** (McGreivy & Hakim, Nature Machine
  Intelligence 2024) — https://arxiv.org/abs/2407.07218 ,
  https://www.nature.com/articles/s42256-024-00897-5
- Diagnosing Failure Modes of Neural Operators Across Diverse PDE Families — https://arxiv.org/pdf/2601.11428
- Operator Boosting Produces Pareto-Efficient PDE Surrogates — https://arxiv.org/abs/2606.17460
- Neural Emulator Superiority — https://arxiv.org/pdf/2510.23111 (already in batch 1)
- PDEBench — https://papers.neurips.cc/paper_files/paper/2022/file/0a9747136d411fb83f0cf81820d44afb-Paper-Datasets_and_Benchmarks.pdf ;
  APEBench — https://arxiv.org/html/2411.00180v1

**FETCHED** https://arxiv.org/abs/2407.07218 — the headline number is that
**79% (60/76) of articles claiming to outperform standard numerical methods
compare against a weak baseline**, and that outcome-reporting and publication
biases make the field "overoptimistic". Decisive nuance for us: on the fetched
abstract page, a *weak baseline* means "**comparisons against inadequate
standard numerical methods** rather than against simple ML alternatives", and
the paper "does not specify particular baseline protocols or reporting
requirements", calling instead for "bottom-up cultural changes ... as well as
top-down structural reforms". So the *critique* is famous; the *protocol*
("publish a ~10^2-parameter closed-form arm beside every learned arm, and
require the learned arm to beat it") is not what that paper prescribes, and it
is aimed at a different comparator (numerical solvers, not trivial learners).

**FETCHED** https://arxiv.org/pdf/2601.11428 — the fetch returned only
structural/metadata-level description ("appears to", "suggests") with no
quotable statement about band-resolved decomposition, trivial baselines or an
aleatoric ceiling. **Recorded as low-information; not used as evidence for or
against any verdict.**

### Term 3 (E2) — output parameterization by magnitude/direction

Top results:
- Improving Neural Network Training by Decoupling the Magnitude and Direction
  of Weight Vectors — https://arxiv.org/abs/2606.25971 (and the author's note
  https://haeggee.github.io/posts/magnitude-direction-decoupling)
- Stochastic Parameter Decomposition — https://arxiv.org/pdf/2506.20790

Magnitude-direction decoupling in the returned literature is applied to
**weight vectors** ("factorizes each weight into a fixed-norm direction on a
hypersphere and learnable magnitude gains", with scalar / per-row / per-column
gain modes) — an optimization technique, not an *output-field* factorization,
and certainly not one selected per dataset from a training-free statistic.
Weight-norm-style decoupling is old and standard; nothing returned selects the
output parameterization from data statistics.

## Interpretation

E3's motivation is published and famous (McGreivy & Hakim) but its comparator
class and prescription differ from ours, so the composition survives as a
protocol contribution rather than a mechanism. E1 has now survived three
distinct refutation attempts at the band-resolved level while being clearly
preempted at the global-scalar level (arXiv:2505.15354). E2's nearest
neighbors are about weights, not outputs; but "select the model form from
dataset statistics" is generic AutoML/meta-learning, which iteration 5 must
test before any novelty is claimed.
