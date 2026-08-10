# Iteration 3 — slice discovery, gated residual correction, and ROM closure

## Search rationale

Three jobs. (a) Re-attempt iteration 2's failed term through the ML framing that actually owns it — **slice discovery** — since "identify a coherent, seed-invariant subpopulation where the model underperforms a trivial baseline" is precisely that literature's product. (b) Open the third candidate direction: a **gated** second-stage correction over the residual subspace (a stage that can be *rejected*, matching the card's empty-gate no-op). (c) Check the ROM-side framing of "what the discarded modes do", i.e. closure, since that is the classical name for fisher_kpp's stranded energy.

## Search terms used

1. `automatic slice discovery underperforming subgroup identification model errors coherent slices benchmark`
2. `gated residual correction second stage reduced basis coefficients boosting unselected modes surrogate model`
3. `hierarchical two-level POD coefficient regression leading modes predict trailing modes closure`

## Findings

### Term 1 — slice discovery is a mature, benchmarked subfield (one fetch)

**FETCHED** — Hua, Jin, Song, Mi, Zhang & Yu, *Discover, Explanation, Improvement: An Automatic Slice Detection Framework for NLP* (DEIM benchmark + Edisa SDM), arXiv:2211.04476 v2, TACL — [cite: https://arxiv.org/abs/2211.04476].
Verbatim: "research on **slice detection models (SDM), which automatically identify underperforming groups of datapoints**, has caught escalated attention in Computer Vision"; Edisa "discovers **coherent and underperforming groups of datapoints**"; and "**detecting difficult datapoints directly boosts model performance without tuning any original model parameters**".
Same turn, search returns (not fetched) confirm this is a crowded 2025–2026 area: *Error Slice Discovery via Manifold Compactness* [https://arxiv.org/html/2501.19032], *HiBug2* [https://arxiv.org/pdf/2501.16751], *CB-SLICE* [https://arxiv.org/html/2605.29836], *Where Does My Model Underperform? A Human Evaluation of Slice Discovery Algorithms* [https://arxiv.org/abs/2306.08167], and a medical-imaging multimodal slice framework [https://arxiv.org/html/2602.24183v1].
Note the *difference* that matters here: every returned SDM discovers slices in an **embedding/semantic feature space** and the diagnosis is "the model underperforms here"; the ch finding is the opposite shape — the slice is **invisible in input (condition) space** (0.448 sigma, NN-ratio 1.018) and only visible in **target/field** space, and the conclusion drawn is about the *benchmark's input completeness*, not the model's.

### Term 2 — gated stagewise residual correction in PDE surrogates (one fetch)

**FETCHED** — Shikhman, *Operator Boosting Produces Pareto-Efficient PDE Surrogates*, arXiv:2606.17460 v2, 24 Jun 2026 — [cite: https://arxiv.org/abs/2606.17460].
Verbatim: "**Starting from the empirical mean predictor** in normalized output coordinates, the method trains a sequence of tiny same-family neural operators **on residual fields** and incorporates each correction through **validation-selected shrinkage**"; instantiated with FNO, DeepONet and CNO across PDEBench / APEBench / The Well; "30 dataset-architecture pairs, 21 show positive mean accuracy gains and 17 have positive confidence intervals"; and it "expos[es] PDE- and architecture-dependent regimes where **residual boosting fails to offset compression**".
The same search's summary text (search-snippet level, describing this work) states the shrinkage grid "includes zero, making each stage **validation-safe** where untrained corrections can be **rejected**" — i.e. the *gate that can decline* is published, with the classical-boosting shrinkage reading.
Also returned (not fetched, but the relevant MF-ROM neighbour): a multi-fidelity ROM that "construct[s] mappings between mode coefficients from low-fidelity and high-fidelity data" with bases extracted separately by POD — [https://onlinelibrary.wiley.com/doi/10.1002/fld.4850] (snippet only).

### Term 3 — closure is the classical name for the truncated directions

Returns: *On closures for reduced order models — a spectrum of first-principle to machine-learned avenues* [https://arxiv.org/pdf/2106.14954], data-driven closure for projection ROMs [https://arxiv.org/pdf/2103.12727], POD closure model comparisons [https://arxiv.org/pdf/1106.3585], and a **multifidelity DeepONet closure** [https://arxiv.org/pdf/2303.08893] (snippet only, all).
The framing returned verbatim in the search summary: retaining only the first R POD modes "introduces a modeling error that results in the **closure problem**", and "the closure term represents the influence of the **discarded modes** on the retained dynamics".
Interpretation: this is *dynamical* closure (discarded modes feeding back into the retained modes' time evolution) — the r3s1 object is static/parametric (a condition→coefficient map with a clipped selection set), so closure is an adjacent vocabulary, not a preemption; but it is the term a reviewer will reach for, and the card should distinguish itself from it explicitly.

## Interpretation

Direction 3 (gated residual correction) took a heavy hit: arXiv:2606.17460 publishes stagewise residual correction with a validation-selected, zero-inclusive (rejectable) gate on PDE surrogates two months ago.
Direction 2 (two-population structure) is preempted *as an ML methodology* by slice discovery, but every fetched SDM discovers slices in input/embedding space, which is exactly what fails on ch.
Iterations 4–5 now run the §3.3 refutation searches on the precise composed claims.
