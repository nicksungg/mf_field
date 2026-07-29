# Iteration 1 — Stream `s1_poisson`, Batch 1

> Persisted verbatim by the orchestrator from the websearcher's return.

## Search rationale
Establish the bar (Q1) and the shape of the benchmark's own method before proposing anything against it. §13.3 forbids relying on recall for the IFC numbers, and the whole stream is defined by a number (0.036) whose provenance I had only read second-hand in `baselines/paper_baselines.json`.

## Search terms used
1. `infinite-fidelity coregionalization neural operator Poisson benchmark Li Zhe 2022 nRMSE`
2. `multi-fidelity operator learning all-pairs fidelity training nested fidelity ladder data amplification`
3. `IFC-GPODE "infinite-fidelity" surrogate learning high-order Gaussian processes Poisson Heat nRMSE results table`

## Findings

**Term 1** — top results: IFC arXiv abs (https://arxiv.org/abs/2207.00678), IFC OpenReview PDF (https://openreview.net/pdf?id=dUYLikScE-), IF-HOGP OpenReview (https://openreview.net/forum?id=jqsDUUzo2B), MFRNP (https://arxiv.org/html/2402.18846v1), MF Flow Matching (https://arxiv.org/html/2605.16118v1), COMPOL (https://arxiv.org/pdf/2501.17296).
- Search engine confirmed authorship/venue: Li, Wang, Kirby, Zhe, *NeurIPS* 35:25965–25978 (2022); IFC "models the latent output as a neural ODE to capture the complex relationships within and integrate information throughout the continuous fidelities."
- **WebFetch https://openreview.net/pdf?id=dUYLikScE- → FAILED** (browser-verification wall, no content).
- **WebFetch https://arxiv.org/abs/2207.00678 → OK (~150w):** IFC treats fidelity as **continuous/infinite**, not as discrete levels: it models "a low-dimensional latent output as a continuous function of the fidelity and input", multiplied by basis matrices to produce the high-dimensional field. Three components — a **neural ODE** over the latent along the fidelity axis, **GPs or a second ODE** for fidelity-varying bases, and a **tensor-Gaussian variational posterior** for scalable inference with massive outputs. Fidelity is tied to a continuous physical parameter (mesh spacing / finite-element length). Benchmarks described only as "several benchmark tasks in computational physics"; **no nRMSE numbers in the abstract**.
- **WebFetch https://arxiv.org/pdf/2207.00678v2 → FAILED** (binary PDF, extractor could not read the results table). Retried specifically to resolve the 0.036/0.018 attribution; unresolved.

**Term 2** — top results: MF-WNO (https://arxiv.org/abs/2208.05606), physics-guided-subsampling MF-DeepONet (https://arxiv.org/html/2503.17941v2), multifidelity DeepONet (https://www.sciencedirect.com/science/article/pii/S0021999123005570), MF-FNO transfer (https://arxiv.org/pdf/2304.06972), MF-KAN (https://iopscience.iop.org/article/10.1088/2632-2153/adf702), MF Bayesian neural operator (https://arxiv.org/pdf/2602.13257), MF GP regression (https://arxiv.org/pdf/2404.11965).
- Engine synthesis: the standard MF-operator recipe is **two fidelities** — much LF + little HF — via LF/HF branch fusion or HF−LF discrepancy learning. For **>2 levels with nested data**, the described convention is a **cascade/stack**: a surrogate at the lowest level, then each higher level trained *using the previous level*, "forming a stacked surrogate when cascaded". **No result described all-ordered-pairs training.**

**Term 3** — top results: same IFC/IF-HOGP pages plus MFRNP PDF (https://arxiv.org/pdf/2402.18846).
- Engine returned the numeric line: *"The nRMSE of IFC-ODE2 at m = 1 and m = 2.14 is 0.036 vs. 0.018 and 0.074 vs. 0.061, for Poisson's and Heat equations, respectively."* Also: "IFC-GPODE is better in interpolation but IFC-ODE2 is promising in extrapolation."
- **WebFetch https://arxiv.org/html/2402.18846v1 (MFRNP) → OK (~150w):** MFRNP is a neural-process MF framework that "models residual between the aggregation and ground truth on the highest fidelity", sharing information through **decoded outputs** rather than latents. Aggregation = **average** of interpolated lower-fidelity predictions; the NP then learns R(x) = f_K(x) − [aggregated lower-fidelity predictions]; final prediction = aggregate + residual. On Poisson, full in-distribution, two fidelities: **nRMSE 0.0076 ± 7.49e-4**, vs next-best baseline D-MFD 0.07 ± 2.99e-4. HF sample count not stated.

## Interpretation
The benchmark's own method is a **continuous-fidelity latent ODE**, not a discrete pairwise scheme — which is both the thing to beat and the nearest neighbour to any fidelity-conditioning proposal. Two material flags: (a) the engine's numeric line suggests **0.036 and 0.018 may be the same method (IFC-ODE2) at two different target mesh spacings m=1 vs m=2.14**, not IFC-ODE2 vs IFC-GPODE as `baselines/paper_baselines.json` records — unresolved, both PDF endpoints failed; (b) MFRNP's Poisson **0.0076 ± 7.49e-4** is *byte-for-byte* the `poisson_local` `test_l2` entry in `baselines/paper_baselines.json` (`paper: 0.0076, paper_std: 0.000749`, source "li2022ifc / niu2024mfrnp") — so MFRNP is confirmed as a source of this repo's own bars, and its mechanism is therefore prior art, not an idea.
