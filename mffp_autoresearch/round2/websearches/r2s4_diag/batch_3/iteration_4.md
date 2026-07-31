# iteration_4 — `r2s4_diag` batch 3 — REFUTATION PASS 1

## Search rationale

**ENOUGH declared on field context** after iteration 3: three turns have mapped
the LUPI/PFD literature, the fixed-budget subset-selection literature and the
low-data-surrogate-baseline literature; the remaining iterations are spent trying
to REFUTE the novelty of the candidate B3 directions.

Candidate directions being refuted:
- **D1** — *teacher-projection / distillability ledger*: fit an out-of-fold
  condition→prediction map to an LF-consuming teacher's own predictions and score
  `proj(teacher)` against the condition-only student, to decide whether any of the
  measured input-side LF advantage is condition-expressible (B2 part 7 Option A).
- **D2** — *coverage-greedy fit-fold selection at fixed N* on the one dataset a
  training-free diagnostic flagged as support-limited (B2 part 7 Option B).
- **D3** — *helmholtz metric restatement* (mean-of-ratios vs energy-pooled) as a
  reported diagnostic column.

## Search terms used

1. `"Learning from more to predict with less" representation-level multimodal distillation surrogate modeling training inference data asymmetry`
2. `measure how much of a privileged teacher's advantage is recoverable from student inputs regression diagnostic Bayes-optimal restricted feature set`
3. `low-fidelity simulation fields used only during training privileged information predict high-fidelity from design parameters no solver at inference`

## Findings per term

### Term 1 — the closest surrogate-domain preemption (D1)
The target paper resurfaced but remains unfetchable: *Learning from more to
predict with less: Representation-level multimodal distillation to address
training–inference data asymmetry in surrogate modeling*, Eng. Appl. Artif.
Intell. 2025 — https://www.sciencedirect.com/science/article/abs/pii/S0952197625034293
(iteration 3's fetch returned **HTTP 403**; no alternate host surfaced in this
search). Search-result description (SEARCH RESULT ONLY, not fetched — quote at
that confidence): the setting is one "where development leverages rich,
multimodal auxiliary data (such as full-field simulation outputs or dense sensor
arrays), but deployed models must operate using only a limited set of primary
inputs"; it treats "auxiliary modalities as privileged information", distils
"their latent structure into the student", "reduces prediction error by up to
30%", "outperform[s] even the privileged teacher in data-scarce regimes", and is
"validated across benchmarks in fluid dynamics, structural mechanics, and
geotechnical engineering".

→ This preempts the *method* "distil a field-consuming teacher into a
parameters-only student for engineering surrogates" (which is r2s3's lever
territory, not r2s4's). It does NOT, on the available evidence, provide a
*diagnostic that measures the condition-expressible fraction of the teacher's
advantage* — but that must be stated at search-result confidence.

### Term 2 — is "how much of the teacher's advantage is recoverable?" formalized?
Two fetches, both directly on point:

FETCHED https://arxiv.org/abs/2606.05718 — **ViCuR: Visual Cues as Recoverable
Privilege for Multimodal On-Policy Distillation**, Tian, Liu, Yan, Xia, Dong,
Wang (2026). The organising principle is exactly D1's question — "Because these
cues are derived from the same visual input available at inference, their
evidence is recoverable by the student" — contrasting privileges that are
recoverable from inference-time inputs against answer-side privileges that are
not. But the fetch is explicit that this is "a **design principle** guiding which
teacher privileges enable genuine reasoning transfer", **not** a formal
diagnostic/theorem, and the paper validates it by end-task benchmark deltas
(+1.19 to +1.24 points over answer-based baselines), not by measuring the
recoverable fraction.

FETCHED https://arxiv.org/html/2505.09546 — **Distilling Realizable Students from
Unrealizable Teachers**, Kim, Chin, Vasudev & Choudhury (Cornell, 2025). Gives
the structural statement that matches this project's ADR r2-0003 regime: "the
student state … is given by a surjective mapping f(s̃)=s, meaning multiple teacher
states s̃ may collapse to the same student state s. This state aliasing prevents
the student from distinguishing between different teacher-optimal actions", with
the consequence that "multiple teacher states collapse into the same student
observation, resulting in conflicting teacher actions for the same input". Their
remedy is *student-side* (CritiQ, ReTRy) and they "explicitly rejec[t] teacher
modification": "unlike modifications that produce realizable but sub-optimal
demonstrations, these methods keep the teacher unchanged while structuring
student learning." So the aliasing diagnosis is published; **projecting the
teacher onto the student-observable σ-algebra and scoring that projection as the
measurement** is not what they do.

Also returned (not fetched): *Weakly privileged learning with knowledge
extraction* (Pattern Recognition 2024,
https://www.sciencedirect.com/science/article/abs/pii/S0031320324002681);
*Enhancing Object Detection with Privileged Information* (arXiv 2601.02016);
*Solvable Model for Inheriting the Regularization through Knowledge Distillation*
(arXiv 2012.00194); Bayes-optimal extensive-width recoverability
(arXiv 2408.03733, 2605.10395), whose framing "which features of the teacher are
statistically recoverable [given a fixed dataset]" is the theory-side analogue in
a synthetic teacher-student setting.

### Term 3 — is our exact MF regime named anywhere?
**No usable results.** The engine stated outright that the results "don't
contain specific papers on the exact technique you're asking about (using
low-fidelity simulation fields as privileged information during training to
predict high-fidelity fields at inference without a solver)". Returned items were
standard MF transfer-learning surrogates (arXiv 2304.06972 FNO transfer;
MDPI airfoil MF transfer https://doi.org/10.3390/app151910820; arXiv 2603.02485
HF/LF decision analysis) — all of which consume LF at inference or are
optimization-loop framings.

## Interpretation

D1's *mechanism* (privileged teacher, student without the privileged channel,
even in engineering surrogates) is unambiguously published; the *specific
diagnostic* — regressing the teacher's own predictions on the student-observable
condition vector and scoring the projection in the task metric to bound what any
distillation could transfer — has not surfaced in two dedicated framings. One
last refutation pass is warranted on that exact phrasing plus on D2 and D3.
