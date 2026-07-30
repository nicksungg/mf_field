# Iteration 1 — `s7_loss` batch 2

## Search rationale

B1's mechanism is closed, so batch 2's live space is (i) the *repaired* version
of the falsified lever — a per-sample relative objective with a **denominator
floor** and λ ≤ 1 — and (ii) whether such repairs are already standard practice
(i.e. unpublishable) or carry documented negative results. Turn 1 therefore
probes the three axes of open question 1, 2 and 4 in `summary_so_far.md`:
denominator flooring/clamping, a continuously tempered per-sample weight, and
published pathologies of relative-error training.

## Search terms used

1. `relative L2 loss neural operator training epsilon denominator clamp normalized loss small norm samples instability`
2. `per-sample norm weighted regression loss interpolation between MSE and relative error exponent beta imbalanced regression`
3. `pitfalls of relative error training loss operator learning degenerate solution collapse zero prediction stationary point`

## Findings

### Term 1 — floored/clamped relative losses

WebSearch top results: `https://www.emergentmind.com/topics/normalized-loss-function`,
`https://arxiv.org/pdf/2108.08481` (Neural Operator: Learning Maps Between
Function Spaces), `https://arxiv.org/pdf/2606.24851`, `https://arxiv.org/html/2607.19544`,
`https://mbrenndoerfer.com/writing/training-stability-loss-spikes-gradient-norm-debugging`.

**Fetched**: `https://www.emergentmind.com/topics/normalized-loss-function`.
It defines the general normalized loss `L̂(x) = L(x)/g(x)` and states the three
properties such losses are adopted for: boundedness, **scale-invariance**, and
interpretability. Denominator strategies documented: per-sample normalization by
target magnitude (style transfer, Gram-matrix norms, explicitly motivated as
equalizing *heteroscedastic task difficulty across samples* — exactly our
`hf_norm_spread` motivation), global geometric scaling, and class-aggregated
denominators (Active-Passive Loss, Ma et al. 2020). On epsilon: the page records
epsilon **only** as a numerical-stability patch inside a geometric
normalization, `H^z(x,y) = v^(z)(x,y) / (‖v^(z)(x,y)‖₂ + ε)`, and — quoting the
fetch — "provides no discussion of failure modes, degenerate optima, or collapse
phenomena." It also names **Normalized Hessian Loss (Huynh et al. 2021),
scale-invariant depth estimation** as a named method (the depth-estimation
lineage of B1's C-AMP verdict, cf. Eigen 2014).

The WebSearch answer summary additionally asserted (not from a fetched source,
so **not citable**) that relative-L2 training halves test error vs MSE, and that
relative-L2 "prevents the constant-output collapse that an unnormalized MSE can
induce" — the latter is the *opposite* of B1's measured mechanism and was
already flagged as an unverifiable folk claim in batch 1's report ("Unverified
leads — MUST NOT be cited").

### Term 2 — tempered per-sample norm weighting

No usable results for the specific construction. Top hits were generic
regression-metric pages (`https://keras.io/2/api/losses/regression_losses/`,
`https://nixtlaverse.nixtla.io/neuralforecast/losses.pytorch.html`,
`https://joyoshish.github.io/blog/2025/ds010-heartofml-regression4/`) and
unrelated arXiv PDFs. The search engine's own summary states the exponent-β
interpolation "doesn't appear directly in these results", but does record the
standard defensive form **denominator = max(|y|, c)** for relative-error loss —
a claim I have *not* yet grounded in a fetched source, so it cannot be cited
yet. Flagged for a targeted refutation search.

### Term 3 — documented pathologies of relative-error training

No usable results **for operator learning specifically**. Returned hits are
about classifier neural collapse (`https://spj.science.org/doi/10.34133/research.0024`),
flooding (`https://arxiv.org/abs/2002.08709`), and oracle-loss hypothesis
collapse (`https://arxiv.org/pdf/2405.15719`). One adjacent operator-learning
hit, "Operator learning without the adjoint"
(`https://arxiv.org/pdf/2401.17739`), is described as training with a
**relative mean-squared error** loss while measuring relative L2 error, and
reports an error *plateau* growing with operator non-self-adjointness — but the
PDF endpoint is the format batch 1 found unfetchable, and the plateau is
attributed to the operator, not the loss. **No published negative result on
per-sample relative training for PDE surrogates surfaced.**

## Interpretation

Denominator flooring is documented as a numerical-stability idiom, not as a
research contribution, and the general normalized-loss literature explicitly
does not treat degenerate optima — which means (a) a floored rel-loss is almost
certainly **preempted as a mechanism** and (b) B1's origin-stationary-point
result may be an *unoccupied negative result*, which is a claimable
contribution shape for this stream even though a new objective is not.
The tempered-β weighting is unresolved and needs a targeted second pass.
