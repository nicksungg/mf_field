# Iteration 3 — r3s2_field_reach, batch 1

## Search rationale

Two jobs. (1) The stacked pseudo-LF direction (`round2/program.md` §12.2, this stream's inherited framing) was already ruled `preempted` in round 2 — but program.md §13.3 forbids re-citing another loop's sources, so its citations must be re-established by fetches made HERE, and I want to know whether the "frozen corrector receives generated inputs" attribution is still unaddressed.
(2) The stream's second possible output is a *certified negative* ("is the negative certifiable?", program §4) — so I searched for methodology for certifying that a model class cannot beat a bound, which the stream would otherwise have to invent.

## Search terms used

1. `emulate coarse solution then correct distribution shift frozen corrector trained on real low-fidelity receives generated inputs multi-fidelity neural network`
2. `certifying a negative result surrogate model class cannot beat baseline information-theoretic reachability bound scientific machine learning`
3. `multi-fidelity DeepONet predicted low-fidelity output fed into residual network inference no low-fidelity solve at test time`

## Findings

### Term 1 — emulate-then-correct with a frozen corrector
- Multi-Fidelity Delayed Acceptance MCMC, https://arxiv.org/pdf/2512.16430 (snippet-level; ScienceDirect mirror https://www.sciencedirect.com/science/article/pii/S0045782526001891) — neural nets learn a corrective map from coarse-solver output to the HF model, and *"in the online stage, multi-level sampling is performed using only coarse solvers, with outputs of all coarser solvers … provided as input to corresponding neural networks."* Coarse **solves are still run online**, so this is not the no-solver-at-test regime.
- Knowledge-Based Neural Networks, https://pmc.ncbi.nlm.nih.gov/articles/PMC8280202/ (snippet) — local additive correction to a coarse model's output.
- Multifidelity GNNs, https://onlinelibrary.wiley.com/doi/10.1111/mice.13312 (snippet) — LF GNN → upsample → HF GNN on residuals: the stacked topology, with a *learned* LF stage.
- APEBench, https://arxiv.org/pdf/2411.00180 and Neural Emulator Superiority, https://arxiv.org/pdf/2510.23111 (snippets) — autoregressive emulator benchmarking; noted for later, not the topology.
**Partial hit**: the emulate-then-correct class is dense, but nothing found isolates *frozen-corrector-on-generated-inputs* distribution shift.

### Term 2 — certifying a negative
The engine's own summary: *"The search results don't contain a paper that explicitly focuses on certifying that a particular surrogate model class cannot beat an information-theoretic reachability bound as a negative result."*
Nearest neighbours (snippet-level, none fetched): "Leveraging Interpolation Models and Error Bounds for Verifiable Scientific Machine Learning", https://arxiv.org/html/2404.03586v1 (error-bounded interpolation as a *verification* device — the closest methodological analogue: a computable bound a learned model is checked against); "Surrogates for Physics-based and Data-driven Modelling of Parametric Systems: Review and New Perspectives", https://arxiv.org/pdf/2603.12870; "Case for a unified surrogate modelling framework in the age of AI", https://arxiv.org/html/2502.06753v1.
**No usable result** for negative-certification methodology in SciML — the reachability hits are Hamilton–Jacobi control-safety, a different sense of the word.

### Term 3 — MF DeepONet with a predicted LF fed downstream (HIT, fetched this loop)
- **[FETCHED]** Demo, Tezzele & Rozza, "A DeepONet multi-fidelity approach for residual learning in reduced order modeling", https://arxiv.org/abs/2302.12682. Verbatim: *"We propose to couple the model reduction to a machine learning residual learning, such that the above-mentioned error can be learned by a neural network and inferred for new predictions"*; *"the framework maximizes the exploitation of high-fidelity information, using it for building the reduced order model and for learning the residual."* → cheap (reduced-order) stage + learned residual on top, evaluated for new parameters with no HF solve.
- **[FETCHED, re-established this loop]** Xu, Cao, Yuan & Meschke, "A multi-fidelity deep operator network (DeepONet) for fusing simulation and monitoring data", https://arxiv.org/abs/2310.00057. Verbatim: *"The presented framework comprises of two components: a low-fidelity subnet that captures the fundamental ground settlement patterns obtained from finite element simulations, and a high-fidelity subnet that learns the nonlinear correlation between numerical models and real engineering monitoring data."* → the LF stage is a **network**, so the downstream subnet consumes a *predicted* LF at inference. This is the stacked topology with a synthetic intermediate, published.
- Yang, Lee & Kang, data-efficient MF DeepONet with physics-guided subsampling, https://arxiv.org/pdf/2503.17941 / https://www.sciencedirect.com/science/article/abs/pii/S0045782525005262 (snippet-level here): *"the low-fidelity prediction is appended to the trunk net inputs to make the residual operator easier to learn"*, and the search summary notes the cost of *"requiring sequential two-network inference"*.

## Interpretation

The stacked pseudo-LF class is confirmed `preempted` by sources fetched in THIS loop (2302.12682, 2310.00057) — a learned LF stage feeding a residual/HF stage at inference is standard MF-DeepONet practice, so r3s2 must not claim that topology as a mechanism.
Certified-negative methodology is genuinely thin: nothing found certifies that a surrogate *class* cannot beat a bound, which makes the stream's "is the negative certifiable?" branch the more defensible novelty target — but it needs a refutation-targeted search of its own.
Iteration 4 will run the refutation searches for the three candidate directions (internal IC reconstruction; completeness-conditioned re-test of the stacked stack; certified negative / reachability audit).
