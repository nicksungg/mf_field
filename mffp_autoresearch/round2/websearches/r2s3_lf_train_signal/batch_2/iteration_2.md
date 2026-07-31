# Iteration 2 — the repaired-network trio (E3) and the per-dataset gate

## Search rationale

B1's part 7 alternative to the linear channel is a *repaired* network carrying
three specific fixes: (a) per-rung output scaler, (b) mode clipping pinned at
the HF Nyquist for every rung, (c) null-direction gain calibration / min-norm
penalty. (a)+(b) are claims about multi-resolution operator training; (c) is a
claim about implicit bias in the underdetermined regime — B1 measured the
FiLM-FNO putting 27.7% of its implicit law energy in the unconstrained
direction ANTI-aligned (cos -0.99) with truth. Turn 2 tests whether each is
already published, and also probes E1's mandatory guard (a training-free
per-dataset gate choosing between a closed-form and a neural surrogate).

## Search terms used

1. `multi-resolution training neural operator per-resolution normalization aliasing mixed resolution training data Fourier neural operator`
2. `implicit bias neural network underdetermined regression extrapolation in directions not spanned by training data null space regularization`
3. `training-free model selection between closed-form linear surrogate and neural network per dataset gating linearity test`

## Findings

### Term 1 — multi-resolution operator training, normalization, mode handling

Returns: arXiv:2310.00120 (MG-TFNO); arXiv:2309.16971 / PMLR v238 li24k
(MRA-FNO); arXiv:2603.15669 (V2Rho-FNO).

**Fetched — MG-TFNO, arXiv:2310.00120** [cite: https://arxiv.org/html/2310.00120]:
normalization in neural operators "requires special care to preserve
discretization invariance"; batch-norm is rejected because it "depends on the
spatial variables"; instance/layer norm (global or function-wise) is used
instead. **It does NOT train simultaneously on multiple resolutions** — it uses
multi-grid domain decomposition feeding one region hierarchical context — and
it keeps "the first alpha modes in each direction, where alpha is independent
of the discretization", i.e. **identical mode truncation at every resolution,
explicitly avoiding Nyquist complications**. No LF data at different parameter
values; single Re=500 high-resolution training set.
→ E3(b) — "pin mode clipping at the HF Nyquist for every rung" — is the
standard discretization-independent-alpha convention in this paper, i.e. the
*fix* is published practice and B1's grid-dependent clipping was the deviation.
E3(a) — a **per-rung (resolution-dependent) output scaler** — is in direct
tension with this literature's discretization-invariance requirement, and no
retrieved paper proposes one.

**Fetched — MRA-FNO, arXiv:2309.16971** [cite: https://arxiv.org/abs/2309.16971]:
treats resolutions as fidelities in an **active-learning** framework, selecting
input functions AND resolutions to optimize a utility/cost ratio, with a "cost
annealing framework to avoid over-penalizing high-resolution queries" and a
probabilistic multi-resolution FNO with ensemble MC inference. The fetched
abstract does not state whether coarse data sits at different input values, nor
its normalization/mode-truncation scheme.
→ Nearest neighbour for "mix resolutions in one operator's training set", but
its purpose is *acquisition* (which resolution to query next), not a
value-of-information contrast on a fixed corpus.

### Term 2 — implicit bias in the underdetermined regime

Returns: arXiv:2010.02501 (unifying view, linear nets); arXiv:2006.07356;
arXiv:2202.04302 (temporal extrapolation); PMLR v336 lai26a / arXiv:2603.04895
(ReLU effect on implicit bias in high-dim NN regression).

**Fetched — arXiv:2006.07356 "Implicit Bias of Gradient Descent for MSE
Regression with Two-Layer Wide Neural Networks"**
[cite: https://arxiv.org/pdf/2006.07356]: in the underdetermined regime GD
converges to a minimum-norm-like solution (the fetch summary renders it as
minimizing an l2-type norm of the network output in the infinite-width limit;
the search snippet phrased it as "a norm-like function that interpolates
between weighted l1 and l2 norms in the transformed input space" — the two
renderings disagree, so **only the qualitative min-norm claim is used here**),
and the fetch summary adds that outside the directions spanned by training data
the learned network shows minimal activity (conservative extrapolation).
**CAUTION: that extrapolation sentence is fetch-model prose, not a verbatim
quote; it is recorded as a lead, not as an established citation.**
→ The *theory* predicts min-norm/conservative behaviour in unconstrained
directions. B1 measured the opposite for a FiLM-FNO decoder (27.7% of law
energy, anti-aligned). That contrast is a candidate finding for B2, and the
E3(c) fix ("penalize the null component toward min-norm") is *implicitly*
the theory's prescription — the retrieval so far shows the theory but no
explicit null-space penalty for operator learning.

### Term 3 — training-free per-dataset gate (closed-form vs neural)

**No usable results.** The search engine stated plainly that the returns "don't
match the very specific technical concept ... a training-free method to select
between linear and neural network models based on a linearity test applied per
dataset as a gating mechanism". Only adjacent material returned: a MoE gating
network for aerodynamics surrogates [search return:
https://arxiv.org/abs/2508.21249] (learned gating, not training-free) and
generic surrogate-comparison studies.

## Interpretation

E3's three repairs split cleanly: (b) is published convention (MG-TFNO's
discretization-independent mode count) so it can only be a bug-fix, (a) is
unretrieved but sits *against* the discretization-invariance norm of that
literature (a defensible but arguable deviation that must be justified as
dataset-specific to ifc_poisson's h^2 amplitude convention), and (c) has
theory behind it (min-norm implicit bias) but no retrieved operator-learning
instantiation. The training-free per-dataset gate returned nothing — first
evidence that E1's guard, not E1's estimator, is where the open surface is.
