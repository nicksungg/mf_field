# iteration_4 — s1_poisson batch 2

## Search rationale

Task item (d) plus the methodological framing B1's part 7 forces: on
ifc_poisson a **training-free nearest-condition matched-8² lookup with one
calibration gain scores nRMSE 0.24828 and beats three of B1's four trained
arms**, and the HF-train-mean field scores 0.40343. Before batch 2 spends SLURM
on a 2×2, I need to know (i) whether such trivial retrieval baselines are
published practice for MF / elliptic surrogates, and (ii) whether the
"weak-baseline" critique literature already licenses reporting them (it changes
how the brainstormer must *frame* the card, even if it changes no mechanism).
Third term keeps hunting the appendix-buried normalization ablation.

## Search terms used

1. `nearest neighbor training-free baseline outperforms neural surrogate PDE benchmark trivial baseline critique operator learning`
2. `normalization ablation changes conclusion multi-fidelity operator learning data preprocessing choice reproducibility scientific machine learning`
3. `nearest neighbor in parameter space retrieval baseline small training set beats trained surrogate physics simulation few samples`

## Findings

### Term 1 — the weak-baseline critique — USABLE

**McGreivy & Hakim, "Weak baselines and reporting biases lead to overoptimism in
machine learning for fluid-related partial differential equations"** (Nature
Machine Intelligence 2024) [https://arxiv.org/abs/2407.07218] (fetched, abs).
Systematic review: **79 % (60/76)** of articles claiming ML beats a standard
numerical method compare against a **weak baseline**; plus outcome-reporting and
publication bias. Attribution: "researcher degrees of freedom and a bias towards
positive results." **Limit of what I can cite**: the abstract page does *not*
specify recommended baselines and does **not** discuss interpolation /
nearest-neighbor / coarse-solution-directly baselines — the fetch says so
explicitly. So this supports *reporting* a cheap floor as a discipline norm; it
is **not** a citation for the specific matched-level-lookup baseline.

Adjacent: "Neural Emulator Superiority: When ML for PDEs Surpasses its Training
Data" [https://arxiv.org/html/2510.23111v1] (not fetched) — the inverse
question (beating the training data), noted for a later batch.

### Term 2 — normalization ablations in MF operator learning

No paper whose contribution is a normalization ablation. Two items worth
recording, both engine-synthesis over returned hits (**snippet-grade**):
"feature normalization is shown to be important for performance, and
normalization also helps to lower variance for operator learning" and
"different normalization methods influence model performance ... emphasizing the
importance of choosing normalization targets" — attributable to the returned
operator-learning-with-attention papers
[https://arxiv.org/pdf/2310.12487, https://arxiv.org/pdf/2205.13671], not to any
MF paper. New MF-specific lead not seen in batch 1:
**"Discretization-independent multifidelity operator learning for PDEs"**
[https://arxiv.org/pdf/2507.07292] — not fetched this turn (arXiv `/pdf/`
fetches have failed repeatedly); flagged for turn 5.

### Term 3 — retrieval / kNN baselines vs trained surrogates

Diffuse and mostly out-of-domain (multimodal retrieval, geostatistics, NER).
The two on-domain, **snippet-grade** items: "relatively simple algorithms such
as k-nearest neighbor regression can be competitive in applications with low
geometrical complexity and extrapolation requirements" — mesh-free surrogates
comparative study [https://www.mdpi.com/2076-3417/11/20/9411]; and a kNN model
attaining the best accuracy among ML surrogates in an NPP fire-scenario study
[https://www.sciencedirect.com/science/article/abs/pii/S0306454925006863].
Neither is a **multi-fidelity** or **field-valued elliptic-PDE** setting, and
neither is the *level-matched cross-fidelity* lookup B1 measured. **No usable
result for the specific baseline.**

## Interpretation

The cheap floor is under-published as a *named baseline*: three searches
produced only generic kNN-competitiveness snippets and nothing multi-fidelity.
The weak-baseline critique (fetched, hard number 79 %) licenses *reporting* the
floor next to every skill number but does not preempt it as a construct. This
makes B1's 0.24828 matched-level floor a **reportable finding of the round**,
not a literature-borrowed baseline — and it means the brainstormer must not
claim it as prior art either way.
