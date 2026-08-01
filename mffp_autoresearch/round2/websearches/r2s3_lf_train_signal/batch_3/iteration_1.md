# Iteration 1 — the coverage explanation and the panel-scale measurement

## Search rationale

B2's part 5 M5 / part 7 make **design coverage** (LF rows at conditions that
carry no HF row) the active ingredient of the stream's value-of-LF effect, and
part 7 asks B3 to scale the matched ±LF contrast from 3 to 6 panel datasets.
Two preemption surfaces therefore matter first: (a) the classical
**nested-vs-non-nested multi-fidelity design** literature, which is where
"LF at uncovered parameter locations" would already live; (b) any
**benchmark-scale ±LF ablation** for neural operators, which is where a
6-dataset value-of-LF accounting would already live. A third term probes the
LF-augmentation / bias-correction family, the obvious alternative B3 mechanism
if the brainstormer wants more than measurement.

## Search terms used

1. `nested versus non-nested design multi-fidelity surrogate low-fidelity samples at parameter locations without high-fidelity data benefit`
2. `benchmark study value of low-fidelity data ablation across multiple PDE datasets neural operator with and without low fidelity training`
3. `multi-fidelity neural network low-fidelity data augmentation bias correction few high-fidelity samples parametric PDE field`

## Findings

### Term 1 — nested vs non-nested MF design
Search returns (not fetched):
- "Bayesian hierarchical surrogate model for reliability analysis under nested
  and non-nested multi-fidelity data" —
  https://www.sciencedirect.com/science/article/abs/pii/S2352012425024324 —
  engine-reported content: mainstream MF approaches "suffer from hyperparameter
  bias and restrictive nested-design assumptions"; non-nested MF scenarios are
  handled "through a data augmentation procedure that samples the missing
  low-fidelity responses, thereby stabilizing model training without additional
  HF evaluations".
- "Review of multi-fidelity models" —
  https://www.aimsciences.org//article/doi/10.3934/acse.2023015 (already cited
  in batch 2 iteration 5).
- Non-hierarchical LF fusion family —
  https://www.sciencedirect.com/science/article/abs/pii/S1474034621001828,
  https://dl.acm.org/doi/abs/10.1016/j.aei.2021.101430,
  https://www.sciencedirect.com/science/article/abs/pii/S1270963824000610.
- Recursive AR(1) GP "can accommodate arbitrary (non-nested) training
  locations" (engine synthesis; consistent with the fetched
  https://arxiv.org/abs/2511.20183 of batch 2 iteration 1).

Reading: non-nested designs (LF where HF is absent) are **standard and named**
in the GP/kriging MF literature. This is the same preemption surface batch 2's
E2 row already records; nothing here is new against it, and nothing here is a
*neural field* instance.

### Term 2 — benchmark-scale ±LF ablation for neural operators
- **Neural operator surrogates of plasma edge simulations (Nucl. Fusion 2025)**
  — https://iopscience.iop.org/article/10.1088/1741-4326/adfdfb — FETCHED:
  "Transfer learning significantly reduced errors for small dataset sizes and
  short rollouts, achieving an order-of-magnitude reduction when transferring
  from low- to high-fidelity datasets", but "its effectiveness diminished with
  longer rollouts and larger dataset sizes". Fetch model reports **no matched
  with/without-LF-pretraining ablation**, and the **inputs are spatial fields
  across a 2-D grid, not a condition/parameter vector**.
- **"Neural Emulator Superiority: When ML for PDEs Surpasses its Training
  Data"** — https://arxiv.org/html/2510.23111v1 — FETCHED: emulators trained
  **purely on low-fidelity solver data** can beat that solver when scored
  against a higher-fidelity reference; the authors explicitly distinguish this
  from prior work that "mixed low-fidelity data with high-fidelity data";
  mechanism is the architecture's inductive bias acting as regularization;
  superiority holds "within specific operating regimes rather than as a
  universal guarantee".
- Benchmark suites named by the engine (PDEBench, PDEArena, APEBench, The
  Well; https://arxiv.org/html/2411.00180v1, https://arxiv.org/pdf/2306.05805)
  — none reported as carrying an LF-ablation axis. Engine stated plainly it
  "did not find a single study that exactly matches" the ±LF ablation query.

### Term 3 — LF augmentation / bias correction with few HF samples
- Composite multi-fidelity NN — https://arxiv.org/abs/1903.00104 (already
  cited, batch 1 D2 row).
- MF-PINN with Bayesian UQ and adaptive residual learning —
  https://arxiv.org/html/2602.01176v1 — engine-reported framing: three
  inductive biases (coarse solution manifold from LF data, gated correction,
  physics residual) that "reduce the effective hypothesis space that must be
  identified from scarce high-fidelity labels". Physics-residual arm is out of
  scope here (round-1 ADR 0009: physics-agnostic at test), but the
  hypothesis-space framing is the standard justification for LF-as-signal.

## Interpretation

The coverage explanation (LF at uncovered conditions) is squarely inside the
long-established non-nested-design MF literature and must not be carded as
novel; the **panel-scale matched ±LF ablation for a condition→field neural
surrogate still returns nothing**, which is the third independent framing to
miss it (batch 1 iter 3, batch 2 iters 4–5, here). The emulator-superiority
paper is a new and directly relevant nearest neighbour: it is the closest
retrieved statement about *what an LF-trained network can be worth relative to
the solver that produced its data*, but it trains **only** on LF and evaluates
rollouts, not a matched ±LF contrast at N_hf = 5.
