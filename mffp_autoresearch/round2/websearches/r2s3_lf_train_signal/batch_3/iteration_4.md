# Iteration 4 — refutation pass on the exact round-2 regime

## Search rationale

Iteration 3 showed the *genre* of the stream's deliverable is published. What
must now be tested is whether the **regime** is: (a) LF present only during
training, with **no LF solve at inference** and a **condition vector** as the
sole test input; (b) an explicit comparison of the trained surrogate against
*running the coarse solver and copying it* (our skill unit); (c) a
**rank/coverage** predictor of when auxiliary data pays. Those are the three
things B3's card would have to claim.

## Search terms used

1. `surrogate uses low-fidelity simulations only during training no low-fidelity solve required at inference parametric field prediction`
2. `is the learned surrogate better than running the coarse solver itself accuracy relative to low-fidelity simulation baseline parametric surrogate`
3. `parameter space coverage rank deficient design predicts when auxiliary training data helps surrogate few samples`

## Findings

### Term 1 — LF only at training, condition-only at test
- **MARIO** — https://arxiv.org/abs/2505.14704 (FETCHED): Neural-Field
  aerodynamic surrogate; "Neural Fields enable training on significantly
  downsampled meshes, while maintaining consistent accuracy during
  full-resolution inference"; it predicts full fields "without requiring CFD
  solves at inference time" and accepts parametric inputs (control-surface
  deflections) as well as geometry. Crucially, its cheap training data is
  **downsampled meshes, not genuinely coarser simulations**, and the fetch
  found **no multi-fidelity value ablation**. Under this project's own
  methodology rule (CLAUDE.md: LF must be a real coarse *consistent* solve,
  never downsampled HF), that is a different object from our LF.
- Other returns: MF CNN temperature-field surrogate
  (https://www.sciencedirect.com/science/article/abs/pii/S0952197623005389),
  MF GP regression in physics (https://arxiv.org/pdf/2404.11965) — classical
  MF, LF available at prediction time.

### Term 2 — beating the coarse solver itself
- https://arxiv.org/html/2510.23111v1 (fetched iteration 1) is the only
  retrieved work that scores a learned model **against the solver that
  produced its training data**, and it trains on LF **only** (no HF mixing).
- Engine synthesis of https://arxiv.org/html/2408.17075v1 (fetched iteration 3)
  adds: "multi-fidelity surrogates generally perform better than
  single-fidelity approaches, and as data increases, single-fidelity surrogates
  perform significantly worse than the best multi-fidelity surrogates".
- Nothing retrieved reports a *copy-the-LF-solution* denominator (our
  `skill = nRMSE(model)/nRMSE(copy-LF)`) for a condition-only surrogate.

### Term 3 — rank/coverage as a predictor of auxiliary-data value
**No usable results.** The engine explicitly reported that none of the returns
match "rank deficient design predicts when auxiliary training data helps
surrogate few samples"; returns were generic surrogate/DoE material
(https://arxiv.org/pdf/2306.07299, https://arxiv.org/pdf/1912.01917,
https://arxiv.org/pdf/1901.05125). Consistent with batch 2's finding that the
*gate feature* is unretrieved while the *gating framework* is preempted
(https://arxiv.org/abs/2403.08118).

## Interpretation

The regime survives the refutation pass on two of three axes: no retrieved
work (i) uses **genuine coarse consistent solves as a training-only signal for
a condition-vector-only field surrogate** (MARIO's cheap data is downsampled
HF; classical MF keeps LF in the prediction path), or (ii) prices the result
against **running the LF solver and copying it**. The measurement *genre* and
the *coverage explanation*, however, are both published (iteration 3), so B3's
claim has to be the composition, not either ingredient.
