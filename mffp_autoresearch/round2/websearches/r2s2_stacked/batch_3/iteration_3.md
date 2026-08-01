# Iteration 3 — field context: seed/fold variance protocol and shrinkage-gated stagewise correctors

## Search rationale

Direction (ii) is a *methodology* proposal: re-run allen_cahn's gated-CNN increment (9.443 skill units,
49.1 % of the scored gain, one fold seed, one fit) under the round's 1+2-seed protocol to decide whether the
class needs a network. I need (a) the field's own conventions for deciding that a reported gain exceeds seed
variance, (b) whether "out-of-fold shrinkage weight goes to zero, so drop the learner" is standard stacking
practice with a citable name, and (c) whether anyone has already published the ablation "the learned residual
stage is unnecessary; a linear filter suffices" for coarse-to-fine PDE fields.

## Search terms used

1. `random seed variance ablation neural PDE surrogate reported improvements disappear across seeds benchmark`
2. `stacked generalization out-of-fold non-negative least squares weight zero drops base learner meta-learner`
3. `ablation shows linear filter suffices learned residual correction unnecessary coarse-to-fine PDE field`

## Findings

### Term 1 — seed variance as a decision rule

**FETCHED (abstract extracted this loop)** — "Operator Boosting Produces Pareto-Efficient PDE Surrogates"
https://arxiv.org/abs/2606.17460 (html https://arxiv.org/html/2606.17460v2): *"Starting from the empirical
mean predictor in normalized output coordinates, the method trains a sequence of tiny same-family neural
operators on residual fields and incorporates each correction through validation-selected shrinkage...
Across 30 dataset-architecture pairs, 21 show positive mean accuracy gains and 17 have positive confidence
intervals... while also exposing PDE- and architecture-dependent regimes where residual boosting fails to
offset compression."*
This is a **direct hit on two of r2s2-B2's structures at once**: (a) a residual corrector stage folded in
through *validation-selected shrinkage* is exactly B2's `alpha_nn` out-of-fold line search, and (b) the paper
already reports the per-cell decision in the form direction (ii) proposes — mean gain vs confidence interval,
with cells where the learned residual stage does not pay.

**FETCHED** — "Quantifying Variance in Evaluation Benchmarks" https://arxiv.org/abs/2406.10229: *"we rarely
quantify the variance in our evaluation benchmarks, which dictates whether differences in performance are
meaningful. Here, we define and measure a range of metrics geared towards measuring variance in evaluation
benchmarks, including seed variance across initialisations..."* (LLM-benchmark domain, but the standing
citation for "seed variance decides whether a difference is meaningful"). The round already implements this
via `state/noise_floor.json`'s certified `min_claimable_effect`.

**FETCHED** — "Gradient-Informed Temporal Sampling..." https://arxiv.org/abs/2603.18237: relevant only as the
source of a snippet about seed sensitivity across sampler configurations; its content is data sampling, not
variance methodology. Recorded to keep the trace honest — it is NOT support for direction (ii).

### Term 2 — shrinkage/stacking weight going to zero

Snippet-level only (no fetch): `pystacked` https://doi.org/10.1177/1536867x231212426 and the Super Learner
introduction https://www.biorxiv.org/content/10.1101/172395v1.full describe the standard construction —
*"train heterogeneous base learners, collect their out-of-fold (OOF) predictions, and blend them through a
non-negative convex meta-learner"*, where *"the default choice for the final learner is nonnegative least
squares with the additional constraint that coefficients sum to one"* and *"coefficients near zero suggest a
model adds little unique information"*.
Reading: **B2's finding that the out-of-fold line search set `alpha_nn = 0` on 5/8 rung cells is textbook
Super-Learner behaviour** ("this base learner adds nothing"), and the honest way to describe it is in that
established vocabulary — it is a *result about this panel*, not a new selection mechanism.

### Term 3 — "the linear stage suffices" ablations

**No usable results for the exact claim.** Returned work is the opposite family: P2C2Net (PDE-preserved coarse
correction, https://gsai.ruc.edu.cn/uploads/20241101/6848e3dd8cb571a8cf728ca4c80e6495.pdf,
https://www.researchgate.net/publication/385510915_... 403) whose ablation shows the *learnable* filter bank
with symmetry constraints is essential (removing the Fourier block raised error two orders of magnitude);
PhyRes-MDNF https://arxiv.org/pdf/2607.06237 whose ablation *credits* the GNN residual stage; Error-Conditioned
Neural Solvers https://arxiv.org/html/2606.27354; Meta-Learned Basis Adaptation for Parametric Linear PDEs
https://arxiv.org/html/2604.09289v1.
Reading: the published ablations in this space consistently **support** the learned correction stage; no
fetched source reports the inverse (closed-form linear stage carries the gain, learned stage switched off).

## Interpretation

Direction (ii)'s protocol is standard practice, and Operator Boosting (arXiv:2606.17460) has already published
the *shrinkage-gated residual corrector over a cheap base predictor*, decided per cell against confidence
intervals — so neither the gate nor the re-run protocol can be claimed. The gap that survives all three terms
is the *sign of the result*: fetched ablations credit the learned stage, and none reports a panel where the
closed-form stage carries 33-100 % of the gain and the network is switched off out of fold. Iterations 4-5
must now run refutation-targeted searches on that exact composition.
