# Iteration 4 — refutation pass 1 (§3.3): can I kill D1 (regularised/band-limited `T(k)`) and D2 (route contrast)?

## Search rationale

Field context is `ENOUGH` (iteration 3). This turn and the next are pure refutation: for each candidate direction, run a search whose *goal* is to find the publication that preempts it.

- **D1** — regularised / band-limited / shrunk spectral transfer-function estimation as the stability repair for a multi-fidelity correction stage fit from ~3 HF/LF pairs.
- **D2** — the route contrast: condition -> pseudo-LF -> corrector vs a direct condition -> HF head at matched total budget, with **no LF available at test**.

## Search terms used

1. `regularizing learned transfer function correction stage multi-fidelity super-resolution instability high frequency blow-up few high-fidelity training pairs` — **engine returned `Web search error: unavailable`**; re-issued once, reworded, as `Wiener filter multi-fidelity correction regularization few samples instability neural operator high wavenumber amplification` (one term slot, two issuances — recorded honestly).
2. `predicting coarse solution as intermediate representation versus predicting fine solution directly from parameters surrogate ablation no solver at inference`
3. `auxiliary intermediate low-fidelity prediction target hurts neural surrogate ablation bottleneck stacked versus single stage`

## Findings

### Term 1 — D1 refutation: the mechanism is preempted, in a form closer than expected (FETCHED)

- [Perrone, Lehmann, Fresca & Gatti] "Correcting Neural Operator Spectral Bias via Diffusion Posterior Sampling with Sparse Observations" (FreqNO-DPS) — <https://arxiv.org/pdf/2606.03936> — **FETCHED this loop (pypdf)**. Verbatim: *"Naïve integration of the surrogate reintroduces its spectral bias into the prediction; we resolve this by **deriving a closed-form, spectrally shaped guidance score that weights the surrogate contribution according to its frequency-dependent accuracy** and requires no backpropagation through the denoiser. A distribution-free analysis bounds the approximation error across the frequency–diffusion-time plane"*, applied with *"a **frozen** neural operator"*. This is a published closed-form, per-band down-weighting of a frozen upstream stage by its own per-band reliability — the same object as "band-limit / coherence-weight `T(k)` where the LF has no power", in a different inference framework.
- The rest of the term returns the standard regularised-deconvolution corpus, **snippet-only**, with the engine stating the general fact plainly: *"Deconvolution without regularization will amplify the high frequency components, which is a key instability issue in inverse problems"*, and *"Regularization is the main technique used to transform ill-posed problems into well-posed ones"*. Sources: <https://ieeexplore.ieee.org/document/797627> (Wiener filter and regularization for image restoration), <https://www.sciencedirect.com/science/article/abs/pii/S0165168498001613> (deconvolution using optimal Wiener filtering and regularization), <https://doi.org/10.1080/17415977.2015.1101760> (impact-force reconstruction using the **regularized Wiener filter method**), <https://aferro.dynu.net/math/wiener_deconvolution/>, <https://www.mdpi.com/2076-3417/11/17/7774> (fetch 403 in iteration 1).

**D1 is dead as a mechanism claim.** Nothing survives except the composition question (does anyone do it *inside an MF correction stage at n_fit ~ 3, in the no-LF-at-test regime*), which stays open only because that regime is itself unrepresented (batch-1 D1 verdict).

### Term 2 — D2 refutation: the coarse-intermediate topology is published; the *ablation against a direct route* is not

- [Liu, Maier & Rupp] "Multiscale Corrections by Continuous Super-Resolution" — <https://arxiv.org/abs/2411.07576> — **FETCHED**. Verbatim: *"we study the implicit neural representation and propose a continuous super-resolution network as a correction strategy for multiscale effects. It can **take coarse finite element data** to learn both in-distribution and out-of-distribution high-resolution finite element predictions"*, with *"Gabor wavelet-based coordinate encodings, which can overcome the bias of neural networks learning low-frequency features"*. Note the decisive regime difference: the coarse FE field is a **real coarse solve supplied at inference**, so this is the classic corrector, not our condition-only stack; and there is no direct-from-parameters arm.
- The engine's own verdict on the ablation: *"the results don't contain a specific paper or study that directly addresses comparing 'predicting coarse solution as intermediate representation versus predicting fine solution directly from parameters' with a 'surrogate ablation no solver at inference'"*. Other returns **snippet-only**: <https://www.nature.com/articles/s41598-023-41039-y> (adaptive PI neural operator for coarse-grained flows), <https://arxiv.org/pdf/2211.11144> (CoSF-Net, coarse->SR->fine end-to-end in 4D-MRI), <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6651435/> (MF local surrogate for microwave design).

### Term 3 — D2 refutation, second angle: does anyone report the intermediate *hurting*?

**No usable results for the negative.** The corpus reports the MF-beats-SF direction only: *"Studies comparing single-fidelity versus multi-fidelity surrogate modeling approaches, showing multi-fidelity methods outperform single-fidelity approaches"*. Snippet-only sources: <https://arxiv.org/pdf/2402.18846> (Multi-Fidelity Residual Neural Processes — *"aggregate predictions across lower-fidelity levels and employ surrogates to capture residuals"*), <https://www.sciencedirect.com/science/article/abs/pii/S0045782522007678> (MF surrogates with LSTMs), <https://www.nature.com/articles/s41467-024-45566-8> (MF transfer learning with GNNs), <https://arxiv.org/html/2606.20053v1> (comparative study of neural surrogate architectures). The fetched 2512.02868 (iteration 3) is the rigorous version of this positive claim and is the strongest counter-prior to any B2 hypothesis that the intermediate helps: it reports MF beating matched single-fidelity *"consistently ... particularly in data-scarce scenarios"* — but with the LF **callable at test**.

Combined with `docs/reports/MF_Sharp_HighFreq_Report.md` line 101 (in-repo prior websearch: the zoo's discrepancy/stack families that run on **model-generated LF only** are weak) and batch-1's <https://arxiv.org/html/2606.17460v2> snippet (boosted stacks fail when *"the full-size baseline already captures the dominant dynamics"*), the published expectation for our regime is genuinely two-sided, and B1's F2 falsification is the only measurement of it on this benchmark.

## Interpretation

D1's mechanism is preempted from two independent directions (classical regularised Wiener deconvolution; FreqNO-DPS's closed-form per-band reliability weighting of a frozen surrogate), so it can only be shipped as an **instrument repair with citations**. D2's topology is preempted (2411.07576, plus batch-1's 2302.12682 / 2310.00057), and the *matched single-vs-multi-fidelity arm protocol* is now also preempted (2512.02868) — but across three searches in two batches, **no source runs a direct-from-parameters arm against a coarse-intermediate arm in a regime where the coarse field cannot be obtained at test**, which is precisely the contrast card part 7 proposes.
