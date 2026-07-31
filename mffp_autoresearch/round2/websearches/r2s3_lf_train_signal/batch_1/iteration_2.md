# iteration_2 — `r2s3_lf_train_signal`, batch 1

## Search rationale

Iteration 1 surfaced one paper that looks like a direct occupant of the
"distil a privileged-input teacher into a deployment-input-only student for
*surrogate modeling*" slot, but WebFetch 403'd on it. Turn 2's job is (i) pin
down that paper's actual scope, (ii) test whether "multi-fidelity distillation"
with the LF model absent at inference is a named, populated literature, and
(iii) test whether the LUPI/privileged-information vocabulary is live in the
regression/simulation setting (not just vision/LLM).

## Search terms used

1. `"Learning from more to predict with less" representation-level multimodal distillation surrogate modeling data asymmetry`
2. `multi-fidelity distillation low-fidelity teacher student network inference without low-fidelity model`
3. `privileged information distillation regression simulation surrogate "at inference" cheaper input unavailable`

## Findings per term

### Term 1 — pinning down the candidate preemption

**[Zhang-et-al-style, authors not resolved] "Learning from more to predict with
less: Representation-level multimodal distillation to address training–inference
data asymmetry in surrogate modeling"**, *Engineering Applications of Artificial
Intelligence*, published Dec 2025 —
https://www.sciencedirect.com/science/article/abs/pii/S0952197625034293
(also returned at .../article/pii/S0952197625034293).

WebFetch returned **HTTP 403 on both URL forms** (paywall). The following is the
abstract text as returned by the search engine in THIS loop (search 2.1 and
2.3, independently — two searches returned consistent wording):

> "the asymmetry between data-rich training environments and data-scarce
> inference scenarios, where development often leverages rich, multimodal
> auxiliary data (e.g., **full-field simulation outputs** or dense sensor
> arrays), but deployed models must operate using only a limited set of primary
> inputs… By treating auxiliary modalities as **privileged information** and
> distilling their latent structure into the student, the method preserves the
> benefits of multimodal training while requiring only deployment-feasible
> inputs at inference… reduces prediction error by up to 30% and demonstrates
> remarkable data efficiency, **outperforming even the privileged teacher in
> data-scarce regimes**… validated across benchmarks in fluid dynamics,
> structural mechanics, and geotechnical engineering."

Key facts established: (a) auxiliary modality explicitly includes *full-field
simulation outputs*; (b) student uses deployment-feasible inputs only;
(c) distillation is **representation/feature-level**, not output-level;
(d) claimed to beat the teacher in *data-scarce* regimes. Facts NOT established
(paywall): whether the privileged modality is a genuinely *lower-fidelity solve*
of the same PDE (vs a richer sensor/field modality of the same fidelity),
whether the student input is a small condition/parameter vector, whether the
student output is a *field* or a scalar QoI, and what N_train regimes were used.

Other term-1 hits (Hierarchical Multi-to-Single-Modal KD for disruption
prediction, https://arxiv.org/pdf/2607.04241 ; iMD4GC,
https://arxiv.org/pdf/2404.01192) are the same multi→single-modality KD pattern
in fusion/medical domains — corroborating that the *pattern* is generic and
published, outside PDE field prediction.

### Term 2 — "multi-fidelity distillation" as a named method

**No usable results.** Every hit reinterprets one of the two words: MF-NAS
(https://arxiv.org/pdf/2006.08341) uses KD to improve low-fidelity *architecture
evaluations*; multi-scale aligned distillation for low-resolution detection
(https://arxiv.org/pdf/2109.06875, and the USPTO filing
https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12136185) is
image-resolution KD in vision; SMFSwap / multi-teacher-prior papers are
unrelated. The search engine itself noted "the search results don't specifically
address inference without the low-fidelity model after training." So
*multi-fidelity distillation for PDE field surrogates* is not a named,
populated literature under this phrasing.

### Term 3 — LUPI vocabulary in the simulation/regression setting

- Vapnik & Izmailov, "Learning using privileged information: Similarity control
  and knowledge transfer" —
  https://www.researchgate.net/publication/301362871_Learning_using_privileged_information_Similarity_control_and_knowledge_transfer
  (the canonical LUPI reference; classification-centric).
- "Privileged Information Distillation for Language Models" —
  https://arxiv.org/abs/2602.04942 (also
  https://huggingface.co/papers/2602.04942). Search snippet: "Privileged
  information (PI) means training-time access to context unavailable at
  inference… transferring capabilities learned with PI to policies that must act
  without it at inference time remains a fundamental challenge." LM domain, but
  it establishes that the *transfer gap* is treated as an open problem, not a
  solved one, in 2026.
- GATES: self-distillation under privileged context
  (https://arxiv.org/html/2602.20574v1), AVSD
  (https://arxiv.org/pdf/2605.20643) — vision/LM.
- The only science/engineering-surrogate LUPI hit is the same ScienceDirect
  paper above.

### Carry-over fetch from term 2 of iteration 1

**"Neural Emulator Superiority: When Machine Learning for PDEs Surpasses its
Training Data"** — https://arxiv.org/html/2510.23111 . FETCHED. Defines a
"superiority ratio" ξ[t] < 1 for an emulator trained *only* on low-fidelity
solver data yet scored against a high-fidelity reference; demonstrated on
advection, diffusion, Poisson (unconverged iterative solver as the LF source),
and Burgers. Two mechanisms: **state-space superiority** (better generalization
across initial conditions than the training solver, present at step 1) and
**autoregressive superiority** (accumulates over rollout). Caveat for us: the
setup is field→field autoregressive emulation at fixed discretization, not
condition→field, and the Poisson LF proxy is solver non-convergence rather than
coarse-grid truncation.

## Interpretation

The generic mechanism "distil privileged training-time inputs into a
deployment-input-only surrogate" is **published** (ScienceDirect EAAI 2025), so
the brainstormer cannot claim it as novel; but the paper's specific instantiation
(feature-level KD, multimodal auxiliary data, unclear whether the privileged
modality is a coarse *solve* and whether the output is a field) leaves the
multi-fidelity composition — LF-coarse-solve as the privileged modality,
condition-vector-only student, full-field output, N_hf = 5 — unresolved from the
retrievable record. "Multi-fidelity distillation" as such is NOT an established
named method for PDE field surrogates. Separately, arXiv:2510.23111 gives a
citable precedent that LF-trained emulators can beat the LF solver, which is
exactly the skill<1 claim r2s3 needs — and it is field→field, so the
condition→field version is not preempted by it.
