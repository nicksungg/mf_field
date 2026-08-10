# Iteration 2 — the route contrast, and what happens when a frozen corrector is fed generated inputs

## Search rationale

B1's F2 falsification says the stack's second stage buys nothing, while the mechanism analysis says the *same frozen corrector fed REAL LF* beats the ifc affine floors by 2.7x / 16x. That is a textbook train/test input-distribution mismatch — the corrector was fit on real coarse solves and is served pseudo-LF at test. Card part 7 therefore proposes a **ROUTE contrast** (direct condition->HF head vs the stack, matched total budget). Two things must be priced here: (a) is the "frozen downstream stage degrades on generated upstream inputs" phenomenon named and published in SciML, and (b) does the direct-vs-two-stage ablation exist? Batch 1 asked (b) once in generic wording and got "no usable results" (`batch_1/report.md`, Turn 2 term 2); this iteration retries with corrector/emulator-cascade phrasing.

## Search terms used

1. `cascade surrogate error accumulation downstream model trained on ground-truth inputs receives predicted inputs distribution shift exposure bias scientific machine learning`
2. `direct parameter-to-solution surrogate versus two-stage coarse emulator plus correction network ablation which is better`
3. `neural coarse solver emulator feeding super-resolution correction network compounding error multi-fidelity PDE` — **the engine returned `Web search error: unavailable`**; re-issued once, reworded, as `learned coarse solver emulator feeding correction network compounding error multi-fidelity PDE surrogate` (recorded honestly: one term slot, two issuances).

## Findings

### Term 1 — cascade / exposure-bias framing

The named-and-published phenomenon in this literature is **autoregressive** error accumulation (a model consuming *its own* previous output), not "stage-2 consumes stage-1's output once". Engine summary of the returned corpus: *"When surrogate models are deployed autoregressively and feed their own predictions back as inputs, small one-step errors compound, the input distribution drifts from the training data, and accuracy degrades"*.

**FETCHED, and the strongest single hit of this loop**: [Duraisamy 2026] "Predictivity and Utility of Neural Surrogates of Multiscale PDEs" (CiSE theme article) — <https://arxiv.org/html/2604.20061>. Verbatim quotes, all retrieved this loop:

- *"The first situation is interpolation on a benign manifold. When the parameter-to-solution map is smooth and the solution set has low intrinsic dimension: rapidly decaying Kolmogorov n-width, any competent approximation method will succeed. Polynomial surrogates, projection-based Reduced Order Models (ROMs), or neural networks all achieve similar accuracy on such problems. **The key diagnostic is whether classical reduced-order methods with comparable offline cost achieve similar accuracy; if so, the benchmark tests interpolation, not the capacity to handle multiscale physics.**"*
- *"A network trained with mean-squared error converges to the conditional expectation u_hat(u_c) = E[u | u_c] ... The resulting prediction is over-smoothed by construction, and **no architecture or training procedure can recover information the coarse representation discards.**"*
- Reporting standard: *"fair comparison should be accompanied by: (1) problem characterization (**intrinsic dimension / n-width proxy**, scale separation, and where possible a Lyapunov-time estimate); (2) test horizon in physical units; (3) **scale-aware metrics (band-limited errors, H1/H2 norms, and flux/dissipation-relevant quantities)**"*; and *"many papers compare against weak baselines, use mismatched hardware, or ignore amortization"*.
- On hybrids: *"use the surrogate where it is fast and accurate ... and return to the full solver to regenerate the high-frequency content that spectral bias suppresses"*, with the open question *"Can the full solver correct only high-k modes while the surrogate handles low-k evolution, achieving scale-selective hybridization?"*

Snippet-only neighbours: <https://arxiv.org/pdf/2506.12007> (SIMSHIFT, a benchmark for neural surrogates under distribution shift); <https://iopscience.iop.org/article/10.1088/2632-2153/ae2e7b> (conformal prediction for downstream surrogate use); <https://www.tandfonline.com/doi/full/10.1080/19942060.2025.2453080> (cascaded neural-network surrogates).

### Term 2 — direct vs two-stage ablation

**Still not found as a controlled ablation.** The engine surfaced two-stage *advocacy* papers (<https://arxiv.org/pdf/2401.02008> two-stage surrogate modelling for design optimisation, "standard deviation reduced by almost a factor of 5 compared to the single-stage counterpart"; <https://arxiv.org/pdf/2604.25890> observation-guided surrogate, "the neural correction stage improves not only aggregate simulator agreement but also worst-case local behavior when compared to a coarse surrogate baseline" — **both snippet-only; a direct PDF fetch of 2604.25890 returned a PDF whose text layer did not extract**) but nothing that runs direct-parameter->HF against emulator+corrector at **matched total optimizer budget**, and nothing in the condition-only regime. The batch-1 negative replicates under new wording.

### Term 3 — learned coarse solver + corrector, compounding error (FETCHED x2)

- [Wei, Franz, List & Thuerey, NeurIPS 2025] "INC: An Indirect Neural Corrector for Auto-Regressive Hybrid PDE Solvers" — <https://arxiv.org/abs/2511.12764> — **FETCHED**. Verbatim: *"hybrid solvers combine coarse numerical solvers with learned correctors ... **directly applying learned corrections to solver outputs leads to significant autoregressive errors, which originate from amplified perturbations that accumulate during long-term rollouts**"*; INC instead *"integrates learned corrections into the governing equations rather than applying direct state updates"*, reducing error amplification *"on the order of dt^-1 + L"*. Note the coarse stage here is a **real numerical solver**, not a learned emulator, and the failure is autoregressive.
- [Koehler & Thuerey, NeurIPS 2025] "Neural Emulator Superiority: When Machine Learning for PDEs Surpasses its Training Data" — <https://arxiv.org/abs/2510.23111> — **FETCHED**. Verbatim: *"neural networks trained purely on low-fidelity solver data can achieve higher accuracy than those solvers when evaluated against a higher-fidelity reference"* — i.e. a pseudo-LF emulator is **not** bounded by the LF solver it imitates. This is a published counterweight to any B2 framing that treats the pseudo-LF stage as a strict information bottleneck.

Snippet-only: <https://arxiv.org/pdf/2605.16118> (Multi-Fidelity Flow Matching: cascaded refinement of PDE solutions); <https://arxiv.org/html/2602.01176> (MF-PINN with adaptive residual learning); <https://ar5iv.labs.arxiv.org/html/2606.27354> (Error-Conditioned Neural Solvers); <https://arxiv.org/html/2504.11383> (time-marching neural-operator/FE coupling); <https://arxiv.org/html/2512.05241> (quantum-classical multifidelity).

## Interpretation

The "corrector degrades on generated inputs" story is published only in its **autoregressive** form (INC), where the coarse stage is a real solver and the damage accumulates over rollout; our single-shot condition->pseudo-LF->corrector composition, with LF unavailable at test, is not that object. The direct-vs-two-stage route ablation at matched budget remains unretrievable after two independent attempts across two batches — the strongest open slot for B2 — but Duraisamy's reporting standard and the "if a classical reduced model matches you, the benchmark tests interpolation" diagnostic squarely preempt any claim that our affine-floor / band-limited-error accounting is methodologically new.
