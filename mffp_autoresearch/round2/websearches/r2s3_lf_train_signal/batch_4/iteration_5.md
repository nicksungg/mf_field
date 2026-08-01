# Iteration 5 — final refutation calls + PRIOR-ART VERDICT (iteration cap 5 reached)

**Cap note**: this is iteration 5 of the maximum 5. No further searching is
permitted in this loop; the verdict below is final for batch 4.

## Search rationale

Two things were still unfalsified after turn 4: (i) direction (a)'s *framing*
as a control-baseline/substitution test ("does a cheap LF-free correction
erase the measured LF benefit?") and (ii) whether the stream's whole regime —
auxiliary data at train, deployment-feasible inputs at test — is a *named*
paradigm in surrogate modeling (batch 3 recorded three independent misses on
this and I wanted one more attempt with the LUPI vocabulary rather than the
multi-fidelity vocabulary).

## Search terms used

1. `stronger baseline eliminates reported improvement transfer learning gains disappear properly tuned baseline scientific machine learning`
2. `value of information auxiliary training data attribute benefit to which channel ablation surrogate model decomposition of transfer gain`
3. `"training-inference" data asymmetry surrogate modeling privileged information distillation predict with less modalities`

## Findings

### Term 1 — control baselines that erase apparent gains

- **"Simple Control Baselines for Evaluating Transfer Learning"** —
  https://arxiv.org/abs/2202.03365 **[curl-fetched, abstract]**. Verbatim:
  "there is not yet an agreed-upon set of **control baselines**, evaluation
  practices, and metrics to report, which often hinders a nuanced and
  calibrated understanding of the real efficacy of the methods… This is done
  by baking a number of simple yet critical control baselines in the
  evaluation method, particularly the **blind-guess** (quantifying the dataset
  bias), **scratch-model** (quantifying the architectural contribution), and
  **maximal-supervision** (quantifying the upper-bound)."
  This is the *methodological genre* of direction (a): add a cheap control
  that quantifies how much of a reported transfer gain is attributable to
  something other than the transferred information. It is prescribed for
  transfer learning generally; the round's floor arms (§2.2 NN-in-condition /
  train-mean / zero) are already this paper's blind-guess control, and an
  LF-free gain head would be a fourth control of the same species.
- **"Stronger Baseline Models – A Key Requirement for Aligning Machine
  Learning Research with Clinical Utility"** —
  https://arxiv.org/html/2409.12116v1 [search return]; **"Source-Optimal
  Training is Transfer-Suboptimal"** — https://arxiv.org/html/2511.08401v1
  [search return]. Same message from two directions: reported gains can
  vanish against a properly constructed baseline.

### Term 2 — attributing an auxiliary-data benefit to a channel

- **"Learning from more to predict with less: Representation-level multimodal
  distillation to address training–inference data asymmetry in surrogate
  modeling"** —
  https://www.sciencedirect.com/science/article/abs/pii/S0952197625034293
  [search return; **body NOT obtainable — ScienceDirect served a JS shell**].
  Metadata **verified by fetch** against the Crossref API
  (https://api.crossref.org/works?query.bibliographic=…): authors **Mazloom,
  Shafieezadeh, Hur, Jung, Ha, Hahm**, *Engineering Applications of Artificial
  Intelligence*, issued **2026-02**, **DOI 10.1016/j.engappai.2025.113398**.
  Content characterization is **engine synthesis only** (flagged): "A
  fundamental challenge … is the asymmetry between data-rich training
  environments and data-scarce inference scenarios. While development often
  leverages rich, multimodal auxiliary data (e.g., **full-field simulation
  outputs** or dense sensor arrays), deployed models must operate using only a
  limited set of primary inputs"; "By treating auxiliary modalities as
  privileged information and distilling their latent structure into the
  student, models can preserve the benefits of multimodal training while
  requiring only deployment-feasible inputs at inference"; "reduces prediction
  error by up to 30% … validated across benchmarks in fluid dynamics,
  structural mechanics, and geotechnical engineering", "outperforming even the
  privileged teacher in data-scarce regimes".
- **Vapnik & Izmailov, "Learning using privileged information: similarity
  control and knowledge transfer"** —
  https://www.researchgate.net/publication/301362871_Learning_using_privileged_information_Similarity_control_and_knowledge_transfer
  [search return]. LUPI is the named paradigm: "additional informative inputs
  … available during training but not at test time" [engine synthesis].
- **SIB-CL** — https://www.nature.com/articles/s41467-022-31915-y [search
  return]: "surrogate data obtained at near-zero cost" as an auxiliary source
  for data-scarce science, with an ablation separating the contrastive and
  transfer stages.
- No retrieved work decomposes an auxiliary-data benefit into a
  **scale/amplitude channel vs a map channel** — B3's M1 decomposition remains
  unmatched as a *measurement*.

### Term 3 — is the regime named? (**answer: yes, now**)

- Term 3 returned the same EAAI paper as the top hit plus a dense cluster of
  privileged-information distillation work: **Privileged Information
  Distillation for Language Models** https://arxiv.org/abs/2602.04942;
  **BLEND** https://arxiv.org/pdf/2410.13872; **JDCNet: Confidence-Gated
  Privileged-Modality Distillation for Cost-Preserving X-ray Inference**
  https://arxiv.org/pdf/2603.29167; **AVSD** https://arxiv.org/pdf/2605.20643
  [all search returns].
  **This closes batch 3's third "independent miss"**: the regime "rich
  auxiliary data at training, deployment-feasible inputs only at inference"
  IS a named paradigm (**LUPI / privileged-information distillation**), and
  as of 2026-02 it has an explicit **surrogate-modeling** instance
  (Mazloom et al., DOI 10.1016/j.engappai.2025.113398). r2s3's *genre* is
  therefore published; only its MF composition can be open.

## PRIOR-ART VERDICT (batch 4)

Candidate directions are B3 part 7's ranked (a), (b), (c), plus the
stream-level framing (S) that any B4 write-up would assert.

### (a) LF-free gain head as a substitution test for LF's train-time value
**Verdict: `preempted-but-MF-composition-open`.**
Mechanism preempted three times, all fetched in this loop:
- **DiSOL** https://arxiv.org/abs/2601.09143 (body
  https://arxiv.org/html/2601.09143v1): "We define a **per-sample amplitude**
  u_lim … and the dimensionless solution pattern u_h := U_h/u_lim … All models
  … are trained to predict the normalized pattern û_h. If an
  absolute-amplitude prediction is required, it can be reconstructed as
  Û_h = û_lim·û_h using an **optional amplitude regressor**." — i.e. exactly
  "predict a per-sample scale, predict the normalized field", in PDE operator
  learning.
- **LCC / Tweedie de-shrinkage** https://arxiv.org/abs/2508.01341: "post-hoc
  correction methods … that substantially reduce **shrinkage-induced**
  prediction bias without relying on newly collected labeled data… LCC applies
  a simple linear transformation estimated on a **held-out calibration
  split**… much of the bias arises from a **first-order scaling distortion**".
- **FiLM as a scale-emitting hypernetwork**
  https://distill.pub/2018/feature-wise-transformations/.
**What remains open** (and is the only thing cardable): using such a head as
a **control baseline that prices auxiliary low-fidelity training data** —
no retrieved multi-fidelity ablation gives its single-fidelity baseline an
output-scale correction (turn 4, term 1), and the direct query "is the
auxiliary-data gain just output calibration?" returned **no usable results**
(turn 3, term 2). Composition also carries the round's four standing openers
(condition-vector-only test input with genuine coarse consistent solves at
train, N_hf = 5, copy-LF denominator, condition-completeness-varying panel).
**Framing rule**: the deliverable is the *measured share of the ±LF effect the
LF-free head absorbs*, never the head. Cite https://arxiv.org/abs/2202.03365
for the control-baseline discipline.

### (b) Budget-matched pricing of the no-LF ensemble alternative
**Verdict: `preempted-but-MF-composition-open` (weak — treat as a control, not
a contribution).**
- Ensemble-based MF emulation exists and beats single-model alternatives, but
  its members are themselves LF-consuming: https://arxiv.org/abs/2604.18045
  (fetched) — "hierarchical kriging emulators that systematically incorporate
  information from lower-fidelity models"; "outperforms single-model
  alternatives".
- The comparison machinery is already published:
  https://arxiv.org/abs/2103.03098 (fetched) — randomize every variance
  source; judge by "a high-enough **probability that in one run an algorithm
  outperforms another**"; prefer out-of-bootstrap to fixed splits; and it
  attributes the effect to bagging-style variance reduction.
- MF-vs-single-fidelity at fixed budget is standard framing
  [https://arxiv.org/html/2512.02868v1,
  https://link.springer.com/article/10.1186/s40323-025-00316-3 — search
  returns].
**Open**: nothing retrieved prices a **no-auxiliary-data ensemble against an
LF-trained arm at matched compute** for a condition→field surrogate. That gap
is real but it is an *evaluation control*, so it may appear as an arm inside
(a)'s card, never as the card's claim.

### (c) Repaired claimability protocol for draw-heteroscedastic effects
**Verdict: `preempted`.**
https://arxiv.org/abs/2103.03098 (fetched, body via ar5iv) states the
diagnosis — "**Bootstrapping data stands out as the most important source of
variance. In contrast, model initialization generally is less than 50% of the
variance of bootstrap** … these different contributions to the variance are
not independent, the total variance cannot be obtained by simply adding them
up" — and the remedy: randomize all sources, use a probability-of-improvement
criterion, prefer resampling to fixed held-out sets; it credits Hothorn et al.
(2005) for the data-sampling-dominates observation. Corrected-resampled-t /
5×2 CV / Friedman–Nemenyi cover the paired-dependence problem
[https://machinelearningmastery.com/statistical-significance-tests-for-comparing-machine-learning-algorithms/,
https://pmc.ncbi.nlm.nih.gov/articles/PMC10435952/ — search returns].
**Nothing remains open at contribution level.** Adopt it as *methodology* —
mandatory hygiene for any B4 clause — and cite it; do not card it.

### (S) Stream-level framing: "auxiliary/LF data at train, none at test"
**Verdict: `preempted (cite)` for the genre; MF composition open per batch 3's
P1.**
The regime is **LUPI / privileged-information distillation**, and it has a
2026 surrogate-modeling instance: Mazloom, Shafieezadeh, Hur, Jung, Ha, Hahm,
*Eng. Appl. Artif. Intell.* 2026, **DOI 10.1016/j.engappai.2025.113398**
(https://www.sciencedirect.com/science/article/abs/pii/S0952197625034293;
metadata Crossref-verified in this loop; body unobtainable, content
characterization is flagged engine synthesis) — "learn from more, predict with
less", auxiliary modalities incl. "full-field simulation outputs" treated as
privileged information, validated on fluid dynamics / structural mechanics /
geotechnical engineering. Any B4 or stream-closure write-up must stop calling
this regime unnamed; batch 3's third "independent miss" is retired.

## Interpretation

All three ranked B4 directions are preempted at mechanism level; (a) is the
only one whose *composition* is still open, and only in its role as a control
baseline that prices auxiliary low-fidelity data. Combined with B3's own
finding that the stream's affirmative evidence is 3/6 with unequal legs, the
retrieval says a B4 is defensible only as a **cheap, training-free-first
measurement with a pre-registered LF-free control**, not as a new mechanism.
