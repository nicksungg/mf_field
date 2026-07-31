# Iteration 4 — `r2s2_stacked` / batch 1 — FINAL (§3.3 prior-art verdicts)

**ENOUGH declared for field context** after iteration 3: three iterations of PDE-surrogate,
MF-statistics and operator-learning vocabulary converged on the same picture (learned-LF →
corrector compositions are published; solver-in-the-loop hybrids dominate the PDE side).
Remaining budget spent entirely on refuting novelty of the concrete B1 directions. Stopping
at k = 4 of the 5-iteration cap (cap NOT hit).

## Candidate directions this stream-batch is likely to propose

Derived from program.md §12.2 (B1 is pre-directed by Eloise's stacking proposal) and the
stream question in `project.yaml`:

- **D1** — condition → **pseudo-LF emulator** (FiLM-FNO) → **frozen** round-1 DC/`dc_cleaned`
  corrector, scored on the stripped view against direct condition→HF (r2s1) and the
  training-free floors (anchor 23.06).
- **D2** — the **frozen / fine-tuned / end-to-end** three-arm ablation that separates
  *emulator error* from *pseudo-LF distribution shift* for the downstream corrector.
- **D3** — LF as an **intermediate supervised bottleneck** inside one condition→HF network
  (predict LF as an auxiliary intermediate, correct to HF), i.e. the end-to-end limit of D1.

## Search terms used (refutation-targeted)

1. `corrector trained on real low-fidelity inputs tested on surrogate-generated low-fidelity inputs performance degradation quantified multi-fidelity`
2. `multifidelity deep operator networks Howard Perego Karniadakis Stinis low-fidelity DeepONet output input to high-fidelity network residual`
3. `is composing low-fidelity surrogate with correction better than direct high-fidelity surrogate comparison ablation multi-fidelity benchmark functional outputs`

## Findings

### Term 1 — generated-vs-real LF inputs to a corrector

- **Conti, Guo, Frangi, Manzoni (2025), "Progressive multi-fidelity learning for physical
  system predictions"**, https://arxiv.org/html/2510.13762v1 — **VERIFIED BY HTML FETCH**.
  Progressive levels with **frozen lower levels**: "at the l-th level, the optimization
  process determines only the current encoder and decoder networks, while the network weights
  … for j<l remain fixed … thus preventing catastrophic forgetting"; "each new level
  configures itself as a correction to be applied to the previous level". Crucially, **LF data
  must still be supplied at test**: "if at testing time the budget allows for acquiring
  low-fidelity inputs {x^(l)}, the model will produce the corresponding prediction". So:
  freeze-lower-fidelity + additive correction is standard; graceful degradation when LF is
  missing exists, but *substituting an emulated LF and accounting for the shift* is not what
  they do.
- Snippet-level (not fetched, recorded as leads only): a corrective-approach description
  "the overall multi-fidelity prediction is evaluated as a low-fidelity trained surrogate
  corrected with the surrogates of the errors between consecutive fidelity levels", and
  "in corrective approaches, the high-fidelity output field is not modeled directly, but
  rather a surrogate serves as a corrective function added to the low-fidelity simulator".
  Related paywalled lead on train/inference asymmetry (r2s3-adjacent):
  https://www.sciencedirect.com/science/article/abs/pii/S0952197625034293
  ("Learning from more to predict with less … training–inference data asymmetry in surrogate
  modeling").
- **No usable result**: nobody found quantifying the degradation of a corrector trained on
  *real* LF when fed *emulated* LF, in a field-valued PDE benchmark.

### Term 2 — the canonical MF-DeepONet composition

- **Howard, Perego, Karniadakis, Stinis, "Multifidelity Deep Operator Networks for Data-Driven
  and Physics-Informed Problems"** (JCP 2023), https://arxiv.org/abs/2204.09157 — abs fetched:
  "composite DeepONet" over two fidelity datasets; demonstrated on ice-sheet dynamics with
  "two different fidelity models" and "the same physical model at two different resolutions"
  (the nested-ladder setting we run). The abstract does **not** disclose whether the LF
  DeepONet's prediction feeds the HF network at inference — flagged as unverified detail.
- The already-fetched Xu et al. (https://arxiv.org/abs/2310.00057) and Yang et al.
  (https://arxiv.org/html/2503.17941v1) from iteration 3 remain the verified evidence.

### Term 3 — composed-LF+correction vs direct HF

- **Survey/benchmark of MF surrogates for simulators with functional outputs** (ScienceDirect
  https://www.sciencedirect.com/science/article/abs/pii/S0045782524008314, arXiv PDF
  https://arxiv.org/pdf/2408.17075 — PDF fetch returned unparsable binary; abstract-level
  snippets only): implements "more than a dozen existing multi-fidelity surrogates under a
  unified framework"; "most multi-fidelity surrogates outperform their tested single-fidelity
  counterparts"; "no particular surrogate performs better on every test case", with the
  decisive factors being LF↔HF correlation, training-set size, and "local nonlinear variations
  in the residual fields". The figures referenced in the binary dump mention "corrective",
  "mapping" and "fusion" families — consistent with the snippet taxonomy but not verbatim
  verified.
- Interpretation for us: the *comparison itself* (composed vs direct) is a standard
  benchmark axis; what is NOT standard is running it where the LF branch is emulated from the
  condition vector and the HF reference is copy-LF skill.

## Prior-art verdicts

**D1 — condition → pseudo-LF emulator → frozen corrector: `preempted (cite)`.**
The topology (a trained LF-predicting network, frozen, whose *predicted* output is consumed by
a residual/HF network) is published:
- Xu, Cao, Yuan, Meschke (2023), https://arxiv.org/abs/2310.00057 — "the low-fidelity outputs
  serve as inputs to the high-fidelity component, which learns the discrepancy"; the
  LF subnet is loaded as a **frozen module** while only the residual subnet is trained.
- Yang, Lee, Kang (2025), https://arxiv.org/html/2503.17941v1 — explicitly names
  "residual-learning frameworks that sequentially combine low and high-fidelity predictions"
  as the class it is differentiating itself from.
- Nearest neighbour in MF-NN form: Meng & Karniadakis (2020),
  https://arxiv.org/abs/1903.00104 (LF NN coupled to two HF NNs for linear/nonlinear
  correlation; inference-time dataflow not verbatim confirmed here).
**What remains open**: none of these reuses a corrector that was *trained on real coarse
solves* (our DC corrector's train inputs are real LF fields, its test inputs would be
emulated) — i.e. the deliberate train/test input mismatch is not their setting; and none
reports the result against a **copy-LF skill** denominator in a no-solver-at-test regime with
N_hf ∈ {5, 400}. The proposal must be framed as *measuring a known composition in an
unmeasured regime*, not as a new mechanism.

**D2 — frozen / fine-tuned / end-to-end arms decomposing emulator error vs pseudo-LF
distribution shift: `preempted-but-MF-composition-open (cite)`.**
The ablation axis is published:
- Yang, Lee, Kang (2025), https://arxiv.org/html/2503.17941v1 — fine-tuning (merge net only)
  vs full-tuning vs linear probing, fine-tuning best, "43.7% improvement … compared to
  single-fidelity training".
- Hagnberger, Musekamp, Niepert, CALM-PDE (NeurIPS 2025), https://arxiv.org/abs/2505.12944 —
  §4.3 verbatim: end-to-end "more stable compared to a two-stage training procedure that first
  trains the encoder-decoder using a self-reconstruction loss and, after that, trains the
  processor". A directional prior: expect end-to-end ≥ frozen.
- Conti et al. (2025), https://arxiv.org/html/2510.13762v1 — frozen lower fidelity levels as
  the default training discipline.
**What remains open**: the *attribution* — no fetched source decomposes the stacked model's
error into (emulator error) + (distribution shift suffered by a downstream module trained on
real inputs), nor measures the shift by the frozen-vs-finetuned delta. That decomposition, on
a field-valued PDE panel, is this stream's genuine contribution and its falsification framing
(§12.2: "if pseudo-LF → corrector loses to r2s1's direct models, the LF representation is not
a useful bottleneck").

**D3 — LF as intermediate supervised bottleneck in one condition→HF network:
`preempted (cite)`.**
This is the jointly-trained limit of D1 and is the Meng & Karniadakis composite-NN design
(https://arxiv.org/abs/1903.00104) and the MF-DeepONet composite design
(https://arxiv.org/abs/2204.09157). Nearest physics-based neighbour: PANIS
(Chatzopoulos & Koutsourelakis, arXiv:2405.19019, verified via arXiv API in iteration 2) uses
"a coarser discretized version of the original PDE" as an information bottleneck — but with
explicit physics, which round 2 forbids at test (§12.1 / ADR 0009).
**What remains open**: only the empirical question — whether the LF bottleneck helps or hurts
versus direct condition→HF on sharp, few-HF fields under the corrected copy-LF denominators.
Propose it as an *arm*, never as a mechanism claim.

## Honesty notes

- Every citation above appears in this loop's iteration files with a URL.
- Verified-by-fetch: 2505.12944 (HTML §4.3), 2503.17941 (HTML), 2510.13762 (HTML),
  2310.00057 (abs), 1903.00104 (abs, architecture only — inference dataflow NOT confirmed),
  2204.09157 (abs, architecture NOT confirmed), 1902.00148 (abs), 2405.19019 (arXiv API).
- Snippet-level-only (NOT citable as evidence on their own): NARGP prediction-time detail,
  INC (s3Uk3lrfjy), ANCHOR, 2604.20061, the 2408.17075 survey taxonomy quotes.
- One WebFetch (the 1902.00148 PDF, iteration 1) produced a summary contradicted by the
  paper's own abstract; it is discarded and recorded as such.
