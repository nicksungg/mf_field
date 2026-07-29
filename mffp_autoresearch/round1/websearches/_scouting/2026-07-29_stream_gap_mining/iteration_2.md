# Iteration 2 — angles (b) uncertainty/trust-region fusion, (e) recurring mechanisms

## Search rationale

Iteration 1 established that (a) is preempted-as-stated and (d) is aimed at a
different problem. This turn opens (b) — the operator brief's
"when to trust LF vs model" — and (e), the open sweep. (b) is the angle most
directly implied by the in-round measurement: copy-LF is better than every
learned predictor on 5/5 datasets, so the value of an explicit "fall back to
LF unless confident" mechanism is the single largest unexploited lever the
diagnostic exposes. I also deliberately searched for the NEGATIVE-result
literature ("fusion worse than its own input"), because if that is a known,
named phenomenon with known remedies, an 8th stream is unnecessary.

## Search terms used

1. `uncertainty-weighted multi-fidelity fusion trust region when to trust
   low-fidelity surrogate gating`
2. `neural network fusion worse than low-fidelity baseline negative transfer
   multi-fidelity guarantee never worse`
3. `multi-fidelity neural operator 2026 survey recent advances mechanisms`

## Findings per term

### T1 — trust-region / uncertainty-weighted fusion

- **MAST: A Multi-fidelity Augmented Surrogate model via Spatial
  Trust-weighting** — https://arxiv.org/html/2602.20974 — FETCHED. This is the
  closest published relative of angle (b). Mechanism: per-point trust weights
  from **geometric proximity to HF samples** — "corrected low-fidelity
  observations should be trusted far from high-fidelity samples where no
  calibration information exists, but should progressively yield to
  high-fidelity predictions as high-fidelity data become available nearby."
  Adaptive radius r_i = sqrt(d_min); cost-aware decay w_j = 1 - d_ij^alpha_m
  with alpha_m = log10(C_M/C_m)/2; blend
  y~_i = W·(y_i + discrepancy) + (1-W)·mu_M(x_i) with propagated
  heteroscedastic variance.
  **Critical scoping facts from the fetch**: (i) it is a **Gaussian-process**
  method, independent GPs per fidelity + augmented-input discrepancy GP;
  (ii) **scalar QoI only** — "No field-prediction or multioutput capability is
  discussed"; (iii) budget ~5D HF-equivalent evaluations (~115 HF for 23D
  DrivAerNet); (iv) **no guarantee** against baselines — worst-case RMSE
  bounded at ~2.04x HF-only in practice, "a practical bound, not a theoretical
  guarantee".
- Also surfaced (hits only, not fetched): variance-weighted-sum MF surrogates
  for non-hierarchical LF data (https://link.springer.com/article/10.1007/s00158-021-03055-2);
  Multi-Fidelity Methods for Optimization survey https://arxiv.org/pdf/2402.09638;
  Peherstorfer/Willcox/Gunzburger MF survey https://arxiv.org/pdf/1806.10761.

### T2 — negative transfer / "fusion worse than its own input"

- Search-engine synthesis over the returned set (flagged as synthesis, not a
  fetched claim): "naive pretraining-fine-tuning methods often perform poorly
  when high-fidelity data are scarce and there are significant discrepancies";
  negative transfer is documented with the signature "training for more epochs
  increases the error on the high-fidelity data even when it decreases the
  error on the low-fidelity data"; and the engine's own conclusion: the
  results "don't explicitly discuss guarantees that fusion is never worse than
  low-fidelity baselines... this remains a challenge in the field."
- Hits: Differentiable Multi-Fidelity Fusion (NAS + transfer)
  https://arxiv.org/pdf/2306.06904; concatenated-NN MF information fusion
  https://www.nature.com/articles/s41598-022-09938-8; multi-channel-fusion MF
  transfer https://www.sciencedirect.com/science/article/abs/pii/S0021999124002018.
- **Assessing the performance of correlation-based multi-fidelity neural
  emulators** — https://arxiv.org/pdf/2512.02868 — FETCHED (PDF partially
  extractable; I record only what the fetch actually returned). Villatoro,
  Geraci & Schiavazzi. Evaluates when MF beats single-fidelity; the fetched
  content identifies **LF-HF correlation strength** as the governing variable,
  flags **normalization** as an effect on whether fusion succeeds, and its
  recommendation is to *measure correlation before committing to fusion*.
  Numeric thresholds were not extractable from the fetch — I make no numeric
  claim from it.

### T3 — recurring 2024-2026 mechanisms sweep

- **The False Promise of Zero-Shot Super-Resolution in Machine-Learned
  Operators** — https://arxiv.org/pdf/2510.06646 — FETCHED. Refutes zero-shot
  super-resolution for neural operators; **aliasing** is the mechanism —
  coarse-trained operators "cannot distinguish between information lost during
  coarse discretization and genuinely smooth behavior". Recommends
  resolution-aware / principled multi-resolution training.
- Hits (not fetched): Multi-Fidelity Flow Matching: Cascaded Refinement of PDE
  Solutions https://arxiv.org/pdf/2605.16118; COMPOL unified multi-physics
  operator framework https://arxiv.org/pdf/2501.17296; Data-Efficient DeepONet
  with physics-guided subsampling https://arxiv.org/pdf/2503.17941;
  "Numerics as Neural Networks: A Compact Low-Fidelity Layer for Multi-fidelity
  Modelling" https://link.springer.com/chapter/10.1007/978-3-032-07690-8_31;
  MF-PINN with Bayesian UQ + adaptive residual learning
  https://arxiv.org/html/2602.01176.

## Interpretation

(b) has exactly one close published relative, MAST, and it is a **scalar-QoI
GP** method — the spatial-trust-weighting idea has not been carried into
**field-valued neural-operator fusion**, which is our setting. Independently,
the negative-transfer literature confirms that "fusion can be worse than its
inputs" is known qualitatively but that a *never-worse-than-LF* construction
is explicitly not established. Together these make (b) the strongest 8th-stream
candidate so far. Iteration 3 must (i) refute (b)'s novelty harder with a
neural-operator-specific query, (ii) refute (c) retrieval, and (iii) check the
one mechanism the panel's own numbers scream for — an architecture that takes
the LF field as input with an identity/skip guarantee.
