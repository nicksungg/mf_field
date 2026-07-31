# Iteration 1 — is "project the privileged teacher onto the student's observable space" a published diagnostic?

## Search rationale

B2's part 7 names the **teacher-projection diagnostic** as the analyst-recommended B3
(Option A): fit an out-of-fold condition -> prediction map to the LF-teacher arm's own
test predictions and score `proj(I1)` against `T0`, to decide whether the teacher's
measured information gap (I2/I1 = 3.16-95.3, claimable 5/5) is *condition-expressible* at
all. Batch 1 already established the LUPI framing and Yang et al.'s non-monotone law;
batch 2 established DOPD's advantage-gap split. What is NOT yet known is whether the
specific operation — regress the teacher's outputs on the student's features and score
the regression — is published as a diagnostic. Turn 1 attacks that from three angles:
LUPI theory (does the literature state the condition under which PI is untransferable?),
the projection operation itself, and the general "how much of an oracle's advantage is
recoverable" framing.

## Search terms used

1. `learning using privileged information theory when privileged features are not a function of observable features distillation limit`
2. `projecting teacher predictions onto student observable feature space diagnostic conditional expectation of teacher regression`
3. `irreducible aleatoric information gap oracle input surrogate model how much of oracle advantage is recoverable from parameters`

## Findings

### Term 1 — LUPI theory / transferability conditions

Search returned the LUPI/PFD cluster. Search-engine synthesis stated that the literature
gives "two necessary conditions for successful privileged learning based on information
theory: privileged features should provide relevant information to the output and
introduce novel insights not collected by regular features" (SNIPPET-LEVEL — not
attributed to a fetched source; **do-not-cite** until verified). Results:
- https://arxiv.org/abs/1903.03694 — "Everything old is new again: A multi-view learning
  approach to learning using privileged information and distillation" — **FETCHED**.
  Unifies LUPI and distillation under multi-view learning; the transferable content is a
  *positive* result: "encouraging agreement between the teacher and the student leads to
  reduced search space", improved convergence rates under regularized ERM. The fetch
  explicitly could **not** confirm any failure condition or bound on untransferable PI.
- https://arxiv.org/abs/2602.04942 — "Privileged Information Distillation for Language
  Models" (pi-Distill / OPSD) — **FETCHED**. Transfers capability learned with
  train-time-only privileged information to a model that lacks it at inference — the
  exact structural setting of an LF teacher + condition-only student. Empirical only:
  "the abstract does not explicitly state an upper bound on how much of the teacher's
  advantage is recoverable".
- Also returned (not fetched): https://arxiv.org/abs/2209.08754 (Yang et al., already
  binding from batch 1), https://www.sciencedirect.com/science/article/pii/S0950705125003855
  ("Teacher privileged distillation: How to deal with imperfect teachers?").

### Term 2 — the projection operation itself

- https://arxiv.org/abs/2606.01292 — "What Makes a Strong Model? A Unified Spectral
  Analysis of Knowledge Transfer over High-dimensional Linear Regression" — **FETCHED**.
  Real paper, relevant area (spectral horizon expansion in KD; spectral denoising in
  weak-to-strong). The search snippet claiming it lower-bounds the teacher's risk "by its
  projection onto the student's space" was **NOT confirmed** by the fetch: "I cannot
  locate any explicit statement about a teacher's risk being lower-bounded by projection
  onto the student's feature space... does not define a 'projected teacher' construct."
  **Do-not-cite that snippet.**
- The remaining hits were off-domain (education/early-warning systems, LM compression
  patents). No usable result for the projection-as-diagnostic operation.

### Term 3 — recoverable vs irreducible share of an oracle gap

- https://arxiv.org/abs/2607.03436 — "How Much of the Routing Gap Is Real? Decomposing
  the Router-to-Oracle Gap into Reproducible Specialist Advantage and Single-Draw Label
  Noise" — **FETCHED**, and this is the closest published relative of B3-D1 found so far.
  It decomposes an oracle-minus-achievable gap exactly the way B3 wants to:
  "the expected oracle decomposes as O^exp = O^repro + Delta, into reproducible
  single-commit headroom O^repro and a non-negative single-commit selection floor Delta."
  It also names a **recoverability asymmetry** — the noise floor "cannot be captured by
  any single-commit router", and it re-estimates the components with fresh k>=20
  resampling "avoiding non-identifiability at k=1". Empirically 12-36% of the routing gap
  is single-draw noise. Domain is LLM routing, not fields/PDEs.
- Surrogate-model hits (GP/UQ) were about aleatoric-vs-epistemic UQ, not about splitting
  an oracle's advantage into recoverable/irrecoverable parts. No usable result there.

## Interpretation

The *operation* B3-D1 wants (regress the privileged teacher's predictions on the
student's features, score the regression) was not found as a named published diagnostic,
but the *question shape* — split an oracle gap into a recoverable part and an irreducible
part, and warn that k=1 makes the split non-identifiable — is published verbatim in
arXiv:2607.03436 for LLM routing. The LUPI theory line (1903.03694, 2602.04942) is
positive-result-oriented and supplies no ceiling, which is itself the useful finding: the
"is any of it expressible in the condition?" question has no standard answer to cite.
