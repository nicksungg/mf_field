# iteration_3 — `r2s4_diag` batch 3

## Search rationale

Three loose ends before the refutation passes. (i) B2's T2-F5 says the round's
mean-of-ratios rel-L2 makes helmholtz undecidable (3-seed spread 1.6363 vs 0.0656
energy-pooled, 24.9×) — B3 will restate helmholtz that way, so is the
sample-weighting artifact of the metric documented (cite) or a project remark?
(ii) The MF composition of D1: is "distil a low-fidelity-consuming teacher into a
parameters-only student" already published for PDE surrogates? (iii) B2's T3-F7
found the 1.06M-param FiLM-FNO at or below a kNN-in-condition estimator on 5/5
datasets — is "neural surrogate does not beat a trivial/neighbour baseline in the
low-data regime" citable beyond batch 1's McGreivy & Hakim?

## Search terms used

1. `relative L2 error averaged per sample bias small-norm samples benchmark metric neural operator mean of ratios critique`
2. `multi-fidelity knowledge distillation low-fidelity teacher student parameters-only PDE surrogate train-time only low fidelity`
3. `neural surrogate fails to beat nearest neighbor baseline parametric PDE low data regime comparison`

## Findings per term

### Term 1 — mean-of-ratios rel-L2 as a metric artifact
Results were all neural-operator method papers that *use* the metric
(arXiv 2510.16816, 2406.06486, 2505.12020, 2606.24851, 2601.17090, 2508.08087,
2409.05508, 2307.02494 — all PDF-only links). The search engine synthesised a
statement that per-sample normalisation "can introduce bias, as dividing by small
denominators (small-norm ground truth values) amplifies errors on those samples"
but **attributed it to no specific fetched source**, so it cannot be cited.

**No usable results** for a fetched, citable treatment of the mean-of-ratios
sample-weighting artifact. Recorded on the do-not-cite list: the small-denominator
bias sentence above, and the "relative-L2 prevents constant-output collapse on
small-amplitude zero-mean targets" sentence, both unattributed.

### Term 2 — MF distillation into a parameters-only student
Top results: *Learning from more to predict with less: Representation-level
multimodal distillation to address training–inference data asymmetry in surrogate
modeling* (Eng. Appl. Artif. Intell. 2025,
https://www.sciencedirect.com/science/article/abs/pii/S0952197625034293);
*Differentiable Multi-Fidelity Fusion* (arXiv 2306.06904, PDF only);
*Multi-fidelity Neural Architecture Search with Knowledge Distillation*
(arXiv 2006.08341, PDF only); *Multi-fidelity reduced-order surrogate modelling*
(Proc. R. Soc. A 480:20230655).

FETCH ATTEMPTED and FAILED: the ScienceDirect abs page returned **HTTP 403
Forbidden** (add to the fetch-failure list alongside batch 2's springer/ncbi
failures). From the search-result text only (NOT citable as a fetched claim):
"multimodal knowledge distillation frameworks distill knowledge into lightweight
student models designed to operate solely on deployment-feasible inputs,
distilling knowledge from privileged modalities via representation-level
learning" — i.e. the training–inference data-asymmetry framing exists **in
surrogate modelling**, which is the nearest neighbour yet found to D1's
composition. A second attempt to reach it through another host is scheduled for
iteration 4; until then it is a snippet, not a citation.

### Term 3 — neural surrogate vs simple baselines in the low-data regime
Top results: *Predictivity and Utility of Neural Surrogates of Multiscale PDEs*
(https://arxiv.org/html/2604.20061v1 — already fetched and cited in this
stream's batches 1 and 2; its framing "whether the method beats optimized
classical baselines at fixed QoI tolerance, including amortization" is the
citation for B3's kNN-comparison column); *Data-Efficient Time-Dependent PDE
Surrogates* (https://arxiv.org/abs/2509.06154); DIPNet (arXiv 2011.15110, PDF).

FETCHED https://arxiv.org/abs/2509.06154 — Nayak & Goswami, 2025. Introduces
"a PCA combined with KMeans trajectory selection strategy" to choose training
data, and reports "GNS is markedly more data-efficient, achieving less than 1%
relative L2 error using only 3% of available trajectories", with "82.5% lower
autoregressive error than FNO, 99.9% lower than DeepONet". This is a second
published instance of *fixed-budget training-subset selection by coverage in a
reduced space* for PDE surrogates (compare iteration 2's FPS/fill-distance and
PICore), reinforcing the Option-B preemption.

No fetched source found that reports a neural surrogate losing to a
nearest-neighbour-in-parameter baseline; the citable framings remain
McGreivy & Hakim (weak baselines, batch 1), Westermann et al. (polynomial beats
neural at low data, batch 1) and 2604.20061's predictivity-vs-utility separation.

## Interpretation

The metric-artifact remark is currently *uncited* — B3 must present it as a
project-local diagnostic (as B2 already does) and not imply literature support.
The MF-distillation composition has one strong potential preemption
(training–inference data asymmetry in surrogate modelling) that could not be
fetched; resolving it is the highest-value action left, and drives iteration 4.
Option B accumulates a third independent preemption of its selection mechanism.
