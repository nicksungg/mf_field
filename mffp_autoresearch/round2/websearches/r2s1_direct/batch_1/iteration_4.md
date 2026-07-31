# Iteration 4 (FINAL) — prior-art verdict (§3.3 pass 2 of 2)

## Search rationale

Iteration 3 refuted D1 and D2 as mechanisms and left D3 partly standing. The
one refutation still owed: has anyone published the *multi-fidelity composition*
of D3 — "the parameter vector does not identify the field, and the coarse solve
is what carries the missing driver"? Second term probes the tiny-N regime
(N_hf = 5 on ifc_poisson) for an existing recipe we would otherwise reinvent.
Iteration cap is 5; I am stopping at 4 (`ENOUGH`: field context is sufficient
and every candidate direction now has at least one targeted refutation search
with a fetched source).

## Search terms used

1. `coarse solve carries initial condition information parameters insufficient multi-fidelity benchmark low-fidelity input necessary condition-only surrogate fails`  (refute D3's MF composition)
2. `operator learning few training samples 5 samples extreme data scarcity parametric PDE surrogate regularization low-rank output basis`  (refute a tiny-N recipe)

## Findings

### Term 1 — is "LF carries the information the condition lacks" published?

Top results:
- "Multi-Fidelity Flow Matching: Cascaded Refinement of PDE Solutions" —
  https://arxiv.org/pdf/2605.16118
- "Neural Emulator Superiority: When ML for PDEs Surpasses its Training Data" —
  https://arxiv.org/pdf/2510.23111
- "Multi-Fidelity Delayed Acceptance: hierarchical MCMC …" —
  https://arxiv.org/html/2512.16430
- "Finding efficient trade-offs in multi-fidelity response surface modelling" —
  https://www.tandfonline.com/doi/full/10.1080/0305215X.2022.2052286
- "MF2: A Collection of Multi-Fidelity Benchmark Functions in Python" —
  https://www.researchgate.net/publication/343860867_MF2_A_Collection_of_Multi-Fidelity_Benchmark_Functions_in_Python

**Fetched** https://arxiv.org/pdf/2510.23111 ("Neural Emulator Superiority:
When Machine Learning for PDEs Surpasses its Training Data", arXiv:2510.23111v2,
metadata date 2026-01-15): emulators *trained on coarse-resolution data* can beat
what that training data would suggest when scored against fine-resolution
references. That is the closest neighbor to a "train on LF, score on HF" claim
found in this loop — but it is a train-on-LF/test-on-HF *generalization* claim,
not an identifiability claim, and its models still consume a field input.

**No usable result** for the actual question. The search returned nothing that
frames a coarse solve as the *carrier of an unobserved driver* that the
parameter vector omits, and nothing that certifies per-dataset whether a
parameter-only surrogate is even well-posed. The search engine's own synthesis
restated the standard MF framing ("the coarse solver captures the macroscopic
structure; the residual has smaller variance") — the residual-learning
motivation, not an information-theoretic one.

### Term 2 — an existing recipe for N_hf ≈ 5

Top results:
- "Accelerating PDE Surrogates via RL-Guided Mesh Optimization" —
  https://arxiv.org/html/2603.02066
- "Pretraining a Neural Operator in Lower Dimensions" — https://arxiv.org/html/2407.17616v2
- "A novel data generation scheme for surrogate modelling with deep operator
  networks" — https://arxiv.org/pdf/2402.16903
- "Deep adaptive sampling for surrogate modeling without labeled data" —
  https://arxiv.org/pdf/2402.11283
- "Operator learning meets inverse problems: A probabilistic perspective" —
  https://arxiv.org/pdf/2508.20207

**Fetched** https://arxiv.org/html/2603.02066 (RLMesh, arXiv:2603.02066v1,
2026-03-02): attacks surrogate data hunger by RL-selecting sparse non-uniform
mesh points per instance under a fixed budget, with a kernel-ridge proxy for
rewards and an FNO retrained periodically; 33–50% labeling-cost reduction on
Burgers. Explicitly **does not** use coarse-grid / low-fidelity data as a
training signal. Not applicable to us — program.md §5.11 forbids new data and
our sample budget is fixed — but it confirms the field's answer to scarcity is
*acquire smarter*, not *certify the floor*. The synthesis also notes the
standard extreme-scarcity recipe is "fine-tune the final layer only", which is
the low-variance-head idea D2 would reach for.

## Prior-art verdict

| # | Candidate direction | Verdict | Citations (fetched this loop) | What remains open |
|---|---|---|---|---|
| D1 | FiLM/modulation-conditioned spectral (FNO) **decoder**: condition vector → latent → HF field, no field input | **preempted** | ModAFNO documented as AFNO + modulation for conditioning on auxiliary inputs incl. parameters — https://archive.docs.nvidia.com/physicsnemo/26.03/physicsnemo/api/models/fnos.html (search return, iteration_1/iteration_3); parameter-conditioned U-Net surrogate https://arxiv.org/html/2601.22654v1; equation-aware conditioning https://arxiv.org/html/2511.09729v1 | Nothing at the mechanism level. Legitimate only as a *measurement* arm: what does the standard conditioned decoder score on THIS panel against the floor arms. Must be labeled a baseline, not a contribution. |
| D2 | Condition → coefficients of a fixed/learned output basis (POD/RB "trunk"), pitched as the variance-reducing shape at N_hf = 5 | **preempted** | PODNO states PCA-Net / POD-NN project onto low-dim subspaces and "map coefficients with simple DNNs", and describes POD-DeepONet — https://arxiv.org/html/2504.18513v1/ (fetched); RB-DeepONet fixes the trunk to a greedy-built RB space and lets the branch predict only RB coefficients — https://arxiv.org/abs/2511.18260 (fetched) | The *number* (how much a fixed basis buys at N_hf = 5 vs a free decoder) is unmeasured here, but the mechanism is 2018-era prior art re-published under three names. Propose only as a declared baseline arm. |
| D3 | Per-dataset **identifiability certification** for a condition→HF panel: estimate the conditional-mean / aleatoric floor, and show the missing driver is recoverable from the withheld LF field | **preempted-but-MF-composition-open** | "Diagnosing the Conditional-Mean Barrier in Scientific ML Surrogates", arXiv:2605.28076v3, 2026-07-06 — https://arxiv.org/html/2605.28076 (fetched): gives residual-orthogonality probes, effect-size thresholding, and aleatoric-floor estimation σ̂_r² ≈ E[Var(Y\|X)], and prescribes reporting it next to model error; the fetch reports it **does not address unidentified random inputs such as random initial conditions**. REALM, the strongest recent surrogate benchmark, does **not** compare against trivial/mean/NN floors at all — https://arxiv.org/html/2512.18595 (fetched) | Open: (a) instantiating the barrier diagnostic on a *field* panel where the unobserved driver is not noise but a stored LF coarse solve, so the floor can be *validated* (LF-conditioned model recovers what the condition-only model cannot); (b) the training-free floor panel (NN-in-condition / train-mean / zero) as a standing certification arm — no fetched source does this. Term-1 search found nothing framing a coarse solve as the carrier of an omitted driver. |

## Interpretation

Every architecture r2s1 was seeded with (§12.1) is preempted; the stream's only
defensible novelty in batch 1 is measurement and certification, not mechanism —
which matches the stream's declared class (`gap`). The one genuinely open
composition is D3's: tying a published aleatoric-floor diagnostic to a
multi-fidelity panel where the hidden driver is observable in the withheld LF
field.
