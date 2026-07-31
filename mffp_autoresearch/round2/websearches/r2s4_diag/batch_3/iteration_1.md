# iteration_1 — `r2s4_diag` batch 3

## Search rationale

B2's part 7 recommends Option A: the **teacher-projection / distillability**
diagnostic — fit an out-of-fold condition→prediction map to the LF-teacher arm's
own predictions and score `proj(I1)` against the condition-only student T0, to
decide whether ANY of the measured input-side LF advantage (information gap
I2/I1 = 3.16–95.3) is expressible as a function of the condition vector, i.e.
whether a train-only distillation channel can exist at all. This turn asks the
field-context question: does the LUPI / privileged-features-distillation
literature already contain (a) a formal statement that a student converges to
the projection of the teacher onto the student's observable inputs, and/or
(b) a *diagnostic* that measures how much of a teacher's advantage is
student-expressible?

## Search terms used

1. `distillation privileged information student cannot recover teacher advantage conditional expectation bound`
2. `knowledge distillation teacher with extra modality unavailable at test time diagnostic whether advantage is transferable`
3. `project teacher predictions onto student measurable input subspace test distillability privileged features`

## Findings per term

### Term 1 — irreducible-gap / conditional-expectation framing
Top results: *Privileged Information Distillation for Language Models*
(https://arxiv.org/abs/2602.04942, also https://arxiv.org/html/2602.04942v1);
*Teacher privileged distillation: how to deal with imperfect teachers?*
(https://www.sciencedirect.com/science/article/pii/S0950705125003855);
*Using Time-Series Privileged Information for Provably Efficient Learning*
(https://arxiv.org/pdf/2110.14993, not fetched — PDF); DemoPSD
(https://arxiv.org/html/2607.02502v1); Self-Distilled RLVR
(https://arxiv.org/html/2604.03128v1).

FETCHED https://arxiv.org/abs/2602.04942 — confirmed title *"Privileged
Information Distillation for Language Models"*, Penaloza, Vattikonda, Gontier,
Lacoste, Charlin, Caccia; submitted 2026-02-04, revised 2026-02-16. Introduces
π-Distill and On-Policy Self-Distillation (OPSD) for "multi-turn agentic
environments" where "successful behavior is observable, but the reasoning process
is not". The fetch reports the abstract does **not** claim a formal irreducible
information gap and does **not** propose a predictive diagnostic.

FETCHED https://arxiv.org/html/2602.04942v1 — the paper's analysis section is
an **empirical diagnostic**, not a theorem: it measures (i) *divergence*, the
initial teacher↔student KL ("as the initial KL increases, final performance tends
to decrease"), and (ii) *utility*, "Δ=score(π_T^base)−score(π_S^base)", and
reports that "the strongest predictor of performance for OPSD is the information
content of the PI", with the explicit caveat that "our analysis in Section 7 is
limited to observational studies, where we do not systematically control for all
variables". The fetch states plainly that the paper "lacks formal theoretical
analysis of the irreducible gap — it remains an empirical characterization
rather than a principled theoretical bound on how much teacher advantage is
structurally unexpressible by the student's input space."

**Note (honesty)**: the search-engine summary for this term asserted a formal
"I(y_t; y* | x, y_<t) > 0" mutual-information-gap statement. Two fetches of the
paper it linked do NOT support attributing that formula to it. The formula is
therefore on this batch's **do-not-cite** list unless independently fetched.

### Term 2 — cross-modal KD with a train-only modality
Top results: *Information-Theoretic Criteria for Knowledge Distillation in
Multimodal Learning* (https://arxiv.org/html/2510.13182); MST-Distill
(https://arxiv.org/html/2507.07015); MMANet (arXiv 2304.08028, PDF only);
KD survey (arXiv 2006.05525, PDF only).

FETCHED https://arxiv.org/html/2510.13182 — proposes the **Cross-modal
Complementarity Hypothesis (CCH)**: cross-modal KD succeeds when
"I(H₁;H₂) > I(H₂;Y)" (H₁ = teacher representation, H₂ = student representation,
Y = label) — "if the mutual information between H₁ and H₂ exceeds the mutual
information between H₂ and Y, the first term contains more information than the
second term". The fetch notes the criterion uses representations *learned during
training* rather than a purely a-priori quantity, though the paper frames it as a
principle to "a priori decide on whether cross-modal KD can be successful".
arXiv preprint 2510.13182v1 (Oct 2025). Search context also confirms the failure
mode is documented: "alongside success stories, there are also reports of
instances where cross-modal KD fails to improve or even degrades student
performance", usually attributed to the "modality gap".

### Term 3 — explicit "projection onto the student-measurable subspace"
Top results are all *methods*, not diagnostics: PFD at Taobao
(https://arxiv.org/pdf/1907.05171), Yang et al. LTR PFD (NeurIPS 2022 proceedings
PDF; the arXiv abs https://arxiv.org/abs/2209.08754 is already cited in this
stream's batch-1 report), calibration-compatible listwise PFD
(https://arxiv.org/pdf/2312.08727), CPFD (https://arxiv.org/pdf/2410.03038),
DOPD (https://arxiv.org/pdf/2606.30626 — the html version is already cited in
batch 2). No fetch spent: no result in the top ~9 describes fitting a map from
student-observable inputs to *teacher predictions* and scoring that projection
as a measurement of how much advantage is distillable. Standard framing is
"train a teacher with privileged features, distill, measure the student's task
metric".

## Interpretation

The mechanism (a privileged/train-only teacher whose input is absent at test) is
thoroughly published and the *failure* of such teachers to transfer is documented
— but the two closest things to B3's Option-A diagnostic are (i) an empirical
divergence/utility characterization in an LM agentic setting and (ii) a
representation-level mutual-information criterion for classification labels.
Neither fits a *scored projection of the teacher's own predictions* onto the
condition vector for a field-valued regression target. That gap is the likely
locus of the D1 verdict; it needs one dedicated refutation search (planned for
iteration 4).
