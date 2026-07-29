# iteration_2 — s7_loss / batch 1

## Search rationale

Iteration 1 covered the derivative- and frequency-domain loss families but left
two of the task's four sub-questions untouched, both of which the s2-B1
evidence makes primary rather than secondary:
(b) **amplitude/scale calibration** (helmholtz error is 86.5% amplitude; one
per-sample scalar takes champion nRMSE 6.202 -> 0.839) and
(c) **low-frequency faithfulness** (excess error in the lowest band, 5/5).
I also re-ran the relative-vs-absolute normalization question with a citable
target (benchmark papers rather than a generic ablation) after iteration 1's
term 3 came back uncitable.

## Search terms used

1. `amplitude calibration scale mismatch neural operator prediction per-sample normalization scale-equivariant training field regression`
2. `PDEBench PDEArena normalized RMSE training loss choice nRMSE relative error benchmark`
3. `low-frequency consistency loss preserve input low band super-resolution avoid degrading coarse input`

## Findings

### Term 1 — amplitude / scale calibration objectives

Largely **no usable results for the objective-design question.** The retrieved
set was dominated by conformal-prediction / uncertainty-calibration work
(https://arxiv.org/html/2402.01960v1, https://arxiv.org/html/2606.09923) —
"calibration" in the UQ sense, not amplitude calibration of the point
prediction. One lead described exactly our failure mode ("predictions can have
a wrong overall amplitude ... may oscillate about a wrong mean level",
*Limitations of Fourier Neural Operators for Nonlinear Structural...*,
https://engrxiv.org/preprint/download/7702/12541/10834) but the PDF fetch
returned unparsable binary, so **I cannot cite it**; recorded as an unverified
lead only.
Assessment: no published *training objective* that explicitly decomposes field
error into an amplitude/gain component and a shape component surfaced for
neural PDE surrogates. This is the strongest novelty candidate so far and gets
a dedicated refutation search in the final iteration.

### Term 2 — normalized / relative losses in PDE benchmarks

- **Takamoto et al. (2022), "PDEBench: An Extensive Benchmark for Scientific
  Machine Learning"** — https://arxiv.org/abs/2210.07182 (abs fetched; the
  NeurIPS PDF again returned unparsable binary) — confirms the paper proposes
  "new evaluation metrics" for a holistic view, with FNO/U-Net/PINN baselines.
  A secondary fetched summary (https://www.emergentmind.com/topics/pdebench)
  enumerates the panel: RMSE, **nRMSE**, MaxErr, plus physics-inspired
  **cRMSE** (global integral conservation violation), **bRMSE** (boundary
  satisfaction), and **fRMSE** ("computed over low, middle, high Fourier bands
  to expose performance on different solution scales"). It also records the
  caveat that "normalized errors in weak-forcing Darcy may diverge despite
  small absolute error due to near-zero solution magnitude", and explicitly
  says the source does not state which loss trains the baselines.
- Bearing on us: **per-band error reporting (fRMSE) is standard published
  practice**, which retro-justifies s2-B1's M3 measurement but also means a
  band-decomposed *diagnostic* is not novel. The per-sample-relative *training*
  loss (F19) is likewise unremarkable as a technique. Neither is claimable as a
  contribution; both are legitimate as engineering.
- The "nRMSE training loss gives up to 9.3% lower training loss" claim that
  iteration 1 saw again appeared only as search-page text with no fetchable
  substantiation. **Not citable.**

### Term 3 — low-frequency faithfulness

- **Liu et al. (2026), "LatentFlowSR: High-Fidelity Audio Super-Resolution via
  Noise-Robust Latent Flow Matching"** — https://arxiv.org/html/2604.09188v2
  (fetched). Defines **low-frequency replacement (LFR)**: after decoding,
  "replace the low-frequency band of the generated audio signal with the
  corresponding low-frequency band from the input audio." Two facts that matter
  to s7: (i) it is **output post-processing, not a loss term** — "The paper
  provides no explicit loss function incorporating low-frequency constraints";
  (ii) motivation is exactly ours — "LFR helps preserve the reliable
  low-frequency information provided by the input, allowing the model to focus
  more effectively on restoring the missing high-frequency content", with an
  ablation (LSD 1.23 vs 1.27 without LFR).
- Additional un-fetched leads on the same page: low-frequency consistency (LFC)
  loss in sparse-view Gaussian splatting (PairDropGS, arXiv:2605.12072) — a
  *loss* form of the same idea in a non-PDE domain; degradation-consistency
  loss (predicted SR image re-degraded must reproduce the LR input) in
  hyperspectral SR (SR^2-Net, arXiv:2601.21338). The degradation-consistency
  idea is the closest published analogue of an **LF-anchoring loss** and is the
  main refutation target for candidate direction C.

## Interpretation

The low-frequency-faithfulness idea is well established *outside* PDE surrogate
learning, and in its dominant form (LFR) it is post-processing rather than an
objective; the loss form (LFC / degradation consistency) exists in graphics and
hyperspectral SR. Amplitude/gain-vs-shape decomposition as a training objective
did not surface at all, in any domain, for field regression — that gap is worth
one adversarial refutation search rather than a claim.
