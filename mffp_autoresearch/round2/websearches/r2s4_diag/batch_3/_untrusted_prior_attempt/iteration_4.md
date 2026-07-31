# Iteration 4 — refutation pass 1 (D1 input-side channel, D1 predicted outcome, D2 support repair)

**ENOUGH declared at end of iteration 3**: field context is sufficient (three turns covered
the projection/LUPI axis, the subset-selection/learning-curve axis, and the
metric/complexity axis); turns 4-5 are spent entirely on §3.3 refutation of the candidate
B3 directions.

## Search rationale

Targets: (a) find a **fetchable** version of the "training-inference data asymmetry"
surrogate-distillation paper, which is the single most dangerous preemption for D1;
(b) refute D1's *predicted outcome* — that the residual is realisation (initial-condition)
information rather than condition-learnable structure — by looking for a published design
that separates IC-driven from parameter-driven error; (c) refute D2 (coverage-greedy fit
fold as a support diagnostic).

## Search terms used

1. `"learning from more to predict with less" representation-level multimodal distillation surrogate modeling arXiv preprint`
2. `parametric PDE surrogate random initial condition not in parameter vector conditional mean limit stochastic map irreducible error`
3. `greedy maxmin distance subset selection training samples diagnostic distinguish sample-limited from information-limited regime surrogate`

## Findings

### Term 1 — the training-inference asymmetry paper (fetchable version hunt)

**No fetchable version found.** Only the paywalled ScienceDirect landing page reappears:
https://www.sciencedirect.com/science/article/abs/pii/S0952197625034293 (403 in iteration 3;
no arXiv/institutional mirror surfaced). The search engine's description this turn is more
specific and consistent with the title: a "modality-flexible teacher-student framework that
resolves training-inference data asymmetry via representation-level distillation", where
development "leverages rich, multimodal auxiliary data (e.g., full-field simulation outputs
or dense sensor arrays)" while deployment uses "only a limited set of primary inputs", "by
treating auxiliary modalities as privileged information and distilling their latent
structure into the student", reporting error reductions "up to 30%" across fluid dynamics,
structural mechanics and geotechnical benchmarks (published Dec 2025). **All numeric and
mechanism claims here are SNIPPET-LEVEL and do-not-cite**; the title, venue and URL are
citable as a search result and are enough to establish that the *design* is published.
Nearest fetchable relatives returned: https://arxiv.org/html/2411.17141v1 (unimodal +
cross-modal distillation for anymodal segmentation), https://arxiv.org/pdf/2607.04241
(hierarchical multi-to-single-modal KD for disruption prediction) — same privileged-modality
shape, different domains; search results only.

### Term 2 — is the residual realisation information? (D1's predicted outcome)

- https://arxiv.org/html/2601.22654v1 — "Parameter conditioned interpretable U-Net surrogate
  model for data-driven predictions of convection-diffusion-reaction processes" — **FETCHED**.
  Contains a directly adoptable published design for the IC-vs-condition attribution:
  a **factorial test set** of "50 distinct initial conditions and 50 different parameter
  combinations, yielding 2,500 total test pairs", scored into a 50x50 error matrix and
  decomposed by rows (ICs) vs columns (parameters). Headline: "The results reveal that
  approximation difficulty varies primarily with the conditioning vector (i.e., the induced
  PDE regime), rather than with the initial conditions" — variance "substantially larger
  across parameter indices than initial condition indices". NOTE this is the *opposite*
  polarity to ADR r2-0003's grounding for our panel (where the unrecorded random IC is
  claimed to dominate) — so it is both a prior-art hit and a live counter-hypothesis.
- https://arxiv.org/html/2607.00196v1 — TRIE, "An Evaluation Framework for Stochastic PDE
  Surrogates" — **FETCHED**. Rejects pointwise scoring for stochastic systems outright:
  because "the forcing realization is not observed at forecast time, a surrogate cannot
  track a single reference trajectory indefinitely", and "for chaotic and stochastic
  systems, long rollouts should reproduce the statistical structure of the dynamics after
  transients have decayed"; it scores invariant measures, spectra and CRPS instead, finding
  that "pointwise-trained neural surrogates fail".
- Also returned (search results only): https://arxiv.org/pdf/2311.00553 (PCE for random
  fields with parametric uncertainty — "no explicit control over the sample space element"),
  https://arxiv.org/pdf/2301.11040 (random-grid neural processes).

### Term 3 — coverage-greedy selection as a regime diagnostic

Mechanism confirmed published and named: the farthest-point/k-center greedy is standard
("The subset selection is formulated as a k-center problem... a farthest-point greedy
heuristic is employed, where in each iteration, the next center is chosen as the point that
maximizes the distance to the existing set of centers" — SNIPPET synthesis over
https://www.researchgate.net/publication/380974390_GIST_Greedy_Independent_Set_Thresholding_for_Diverse_Data_Summarization
and https://proceedings.mlr.press/v180/cheng22a/cheng22a.pdf; **do-not-cite the wording**,
cite arXiv:2012.03541 from iteration 2 instead, which was fetched). The search engine
stated explicitly: "I didn't find specific content explicitly addressing the distinction
between 'sample-limited' and 'information-limited' regimes using diagnostic tools with
surrogates." **No usable result** for the diagnostic framing.

## Interpretation

D1's *design* (privileged-input teacher -> deployment-input student for engineering
surrogates) is published, though only behind a paywall; D1's *diagnostic* (projecting the
teacher onto the condition-measurable subspace to decide whether the advantage is
transferable at all) still has no match. D1's predicted outcome now has a published
counter-example worth pre-registering against (2601.22654: parameters, not ICs, dominated
difficulty there). D2's mechanism is standard k-center greedy; only its use as a
regime diagnostic survives two failed searches.
