# Iteration 2 — Stream `s1_poisson`, Batch 1

> Persisted verbatim by the orchestrator from the websearcher's return.

## Search rationale
§12.1 tells this stream to prefer **variance reduction** or **added information** over capacity. That maps to three literatures I had not verified: multi-level/control-variate training (variance reduction using the ladder), the N_hf≈5 regime specifically (Q3), and physics residuals for an elliptic operator (Q4).

## Search terms used
1. `multilevel Monte Carlo training neural operators telescoping control variate resolution hierarchy`
2. `neural operator extremely few high-fidelity samples 5 samples multi-fidelity variance reduction ensembling scarce data`
3. `physics-informed correction Poisson neural operator discrete residual few high-fidelity labels elliptic global coupling`

## Findings

**Term 1** — top results: MLMC-NO arXiv (https://arxiv.org/abs/2505.12940), PDF (https://arxiv.org/pdf/2505.12940), CMAME (https://www.sciencedirect.com/science/article/pii/S0045782526000745), Cambridge repository (https://www.repository.cam.ac.uk/items/de988071-9631-4e30-9bd5-53353d7c527d), multilevel control functional (https://arxiv.org/html/2305.12996).
- Engine synthesis (abstract-level): MLMC-NO "relies on using gradient corrections from fewer samples of fine-resolution data to decrease the computational cost of training while maintaining a high level of accuracy"; applicable to **any architecture accepting multi-resolution data**; and — importantly — "the input and output training data is **downsampled** from fine to coarse resolutions."
- **WebFetch https://arxiv.org/pdf/2505.12940 → OK (~150w):** telescoping estimator ∇L_MLMC = ∇L₀^coarse + Σ ∇(L_ℓ^fine − L_ℓ^coarse); cheap coarse samples plus few expensive fine corrections; the extractor asserted the hierarchy comes from **separate coarse solves on progressively coarser FEM meshes, not downsampling**; framed as **compute at fixed accuracy** rather than accuracy at fixed data; tested on **FNO and GNNs**, **Darcy and Poisson** with varying coefficients, 2-D. **This directly contradicts the search-snippet claim above — flagged, unresolved.**

**Term 2** — top results: MF-FNO carbon storage (https://www.sciencedirect.com/science/article/abs/pii/S0022169424000350), multifidelity deep neural operators (https://arxiv.org/abs/2204.06684), MLMC-NO again (https://arxiv.org/pdf/2505.12940), MF regression with ANNs (https://www.sciencedirect.com/science/article/pii/S0045782521006411), MF-BNN (https://arxiv.org/html/2407.05684v1), adaptive MF stratified sampling (https://arxiv.org/html/2508.00734).
- Engine synthesis: the canonical MF-DeepONet result is "two standard DeepONets coupled by **residual learning and input augmentation**", reported to "significantly reduce the required amount of high-fidelity data" and achieve "**one order of magnitude smaller error when using the same amount of high-fidelity data**" (arXiv:2204.06684). On variance reduction: LF models "need only to be **sufficiently correlated** with high-fidelity outputs in the region of interest", and even weak LF models "provide substantial variance-reduction over single-fidelity Monte Carlo". Embedding MLMC in mini-batch SGD needs explicit **sample-allocation formulas and subsampling schemes**.
- **No source returned a result at N_hf ≈ 5.** Q3 is answered only qualitatively.

**Term 3** — top results: physics-informed low-rank NO for parametric elliptic PDEs (https://arxiv.org/pdf/2509.07687), residual-based error correction for NO (https://www.osti.gov/servlets/purl/2421120), physics-guided correction under misspecification (https://arxiv.org/pdf/2606.03469), PI Laplace NO (https://arxiv.org/html/2602.12706v1), compositional NOs incl. a Poisson solver (https://arxiv.org/html/2605.11691), PI partitioned coupled NO (https://www.sciencedirect.com/science/article/abs/pii/S0952197625015696).
- Engine synthesis on **PINO**: combines PINN data-efficiency with NO generalization, "integrates training data with PDE residual loss evaluated at high-resolution", and "by enforcing PDE constraints at finer spatial and temporal resolutions, it **compensates for coarse or limited data**". This is precisely the mechanism `mf_fno_pinn_transfer` already implements in-zoo.
- **WebFetch https://arxiv.org/pdf/2509.07687 → OK but thin (~150w):** low-rank operator parameterization + physics residual; Poisson is a primary benchmark among parametric elliptic PDEs; "competitive accuracy while significantly reducing the model's parameter count"; sample-efficiency claimed qualitatively ("moderate training sample sizes"); the extractor could not confirm a multi-fidelity component. **No numbers extracted — low confidence.**

## Interpretation
Both §12.1-sanctioned routes are occupied territory: the variance-reduction route by MLMC-NO's telescoping control variate (published, and demonstrated on **Poisson** with **FNO**), and the added-information route by PINO-style residual training (published, and already the in-zoo best at 0.042). The one thing the literature does **not** supply is any quantified behaviour at HF budget ≈ 5, and there is an unresolved and methodologically load-bearing ambiguity about whether MLMC-NO's coarse levels are downsampled or separately solved — under this repo's law (LF must be a real coarse solve) those are different methods.
