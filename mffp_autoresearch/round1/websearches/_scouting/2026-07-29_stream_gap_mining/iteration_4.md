# Iteration 4 — refutation pass in the multi-fidelity / operator vocabulary

## Search rationale

Iteration 3 found the candidate mechanisms preempted in CV but with no MF
composition. Per program.md §13.3 that is exactly where this project's
0-for-4 record was made: the next step is to re-run the same refutation in the
**multi-fidelity / neural-operator** vocabulary, where a hit would kill the
candidate outright. Three refutations: C1 (gated LF-fallback fusion), C2
(retrieval-augmented correction), C3 (cross-dataset pretraining = the deferred
`s8_data`).

## Search terms used

1. `multi-fidelity neural operator learned gating between low-fidelity input
   and correction network fallback baseline PDE field`
2. `nearest-neighbor retrieval of training examples to correct PDE surrogate
   prediction residual database operator learning`
3. `pretraining neural operator on multiple unrelated PDE datasets then
   fine-tuning improves few-shot accuracy negative results 2025`

## Findings per term

### T1 — refutation attempt on C1 (gated LF-fallback fusion)

Two near-misses, neither a kill:

- **Physics-guided correction for operator learning under model
  misspecification** — https://arxiv.org/html/2606.03469 — FETCHED. Serial
  DeepONet: prior operator produces a baseline, a correction operator learns
  the discrepancy conditioned on both input and prior prediction,
  `N†[v] ≈ G_θ(v) + G_ψ(v, u_θ)`. Three decisive facts from the fetch:
  (i) the composition is **simple additive, "without gating or trust
  weighting... No adaptive weighting or gating mechanism modulates their
  relative contributions"**; (ii) **"No formal guarantee exists" that
  correction improves upon the prior** (empirically it does on 4 benchmarks,
  e.g. hyperelasticity rel-L2 3.75±0.20 corrected vs 25.50±0.09 misspecified);
  (iii) the prior is **a physics-based model requiring PDE knowledge** — so
  the paper's own instantiation is excluded from this round by ADR 0009,
  though the authors note the prior may also be an approximate solver or a
  pretrained operator.
- **Ensemble adaptive gated multi-fidelity neural network (AGMF-Net) for
  Bayesian optimization: hydrofoil design** —
  https://www.sciencedirect.com/science/article/abs/pii/S002980182502997X —
  WebFetch returned **HTTP 403** (paywalled); I therefore claim only what the
  search-result snippet states: three specialized expert subnetworks combined
  through a deep Mixture-of-Experts gating network that adjusts contributions
  by input. It is a **Bayesian-optimization / design** application (hydrofoil),
  i.e. scalar-objective, not field prediction, and I cannot verify further.
  Recorded as an unresolved threat to C1's novelty that a builder must re-check.
- Also returned (hits only): multifidelity DeepONet with residual learning +
  input augmentation (https://link.aps.org/doi/10.1103/PhysRevResearch.4.023210);
  Multi-Fidelity Flow Matching cascaded refinement
  (https://arxiv.org/pdf/2605.16118); flow-matching residual-augmented
  probabilistic operator learning (https://arxiv.org/pdf/2512.12749);
  multi-task DeepONet synergistic learning
  (https://www.sciencedirect.com/science/article/abs/pii/S0893608024010426).

**Verdict material**: the standard MF-operator composition is *additive
residual on top of the LF/prior prediction*, explicitly ungated, explicitly
without a never-worse property. C1's distinguishing content — a learned
per-pixel/per-band **trust gate whose zero setting reproduces copy-LF exactly**
— was not found.

### T2 — refutation attempt on C2 (retrieval-augmented correction)

- No hit for retrieval-from-a-training-bank in operator learning. The engine's
  own conclusion: "the specific combination of nearest-neighbor retrieval with
  database operator learning for PDE surrogate residual correction appears to
  be a specialized or emerging technique that may not have extensive coverage."
- Closest returned: **Error-Conditioned Neural Solvers**
  https://arxiv.org/pdf/2606.27354 — feeds the **PDE residual field** back as
  network input each iteration so the model reads its own error structure
  (10x gains on Kolmogorov flow) — this is self-conditioning on physics, not
  retrieval, and ADR 0009 excludes it at test time. Also PDE-Refiner
  (https://papers.neurips.cc/paper_files/paper/2023/file/d529b943af3dba734f8a7d49efcb6d09-Paper-Conference.pdf),
  multiscale surrogates/downscaling with residual add-on
  (https://arxiv.org/html/2507.18067), and a generic "Explaining the Success
  of Nearest Neighbor Methods in Prediction" (https://arxiv.org/abs/2502.15900).

**Verdict material**: C2 has no PDE/operator-learning preemption across two
independent search framings (iteration 1 T1 and this one).

### T3 — refutation attempt on C3 (cross-dataset pretraining, `s8_data`)

Comprehensively preempted, and with a documented boundary condition:

- **Pre-Generating Multi-Difficulty PDE Data for Few-Shot Neural PDE Solvers**
  — https://arxiv.org/html/2512.00564v1 — FETCHED. Explicitly **not** a
  coarse/fine multi-fidelity setup: "difficulty" is defined by problem
  parameters and geometry (obstacle count 0/1/2-10; Reynolds bands easy
  100-1000, medium 2000-4000, hard 8000-10000), binned by classical-solver
  wall-clock. 6,400 OpenFOAM sims per setting, 20 timesteps at 128². Headline:
  **adding just 10% hard examples to 90% easy/medium recovers ~96% of
  hard-only performance, an 8.9x pre-generation compute reduction** (800 total
  training samples, held-out hard test); holds across CNO, FFNO and three
  Poseidon scales. Conclusion: "data curation across difficulty levels matters
  as much as total data volume."
- Other preemptions (hits): PDEformer-2 2-D foundation model
  https://arxiv.org/pdf/2507.15409; DPOT https://arxiv.org/pdf/2403.03542;
  "Towards Universal Neural Operators through Multiphysics Pretraining"
  https://ml4physicalsciences.github.io/2025/files/NeurIPS_ML4PS_2025_157.pdf;
  Pretraining a Neural Operator in Lower Dimensions
  https://arxiv.org/pdf/2407.17616; Data-Efficient Operator Learning via
  Unsupervised Pretraining (NeurIPS 2024)
  https://proceedings.neurips.cc/paper_files/paper/2024/file/0bac492172db3311c7e116098cfcf521-Paper-Conference.pdf;
  distributed multi-operator DeepONet pretraining
  https://www.sciencedirect.com/science/article/abs/pii/S0021999125008198.
- The engine's summary flags the known caveat: transfer helps when the target
  PDE resembles the pretraining set and "the advantage may be less obvious in
  the opposite case" — our panel is 6 mutually unrelated PDE families.

## Interpretation

C1 survives with one unresolved paywalled threat (AGMF-Net); C2 survives two
independent refutation framings; C3 is dead as a novelty claim — the mechanism
is a crowded field AND our own champion is already an LF-pretrain/HF-finetune
transfer model. Iteration 5 closes the remaining gap: the amplitude/
normalization mechanism the in-round helmholtz measurement points at, and the
final stream-worthiness assessment.
