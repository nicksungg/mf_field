# Websearch Report — Stream `r2s3_lf_train_signal`, Batch 1

**Stream**: `r2s3_lf_train_signal` (lever — "how much does LF, available only
during training, help a condition→HF model?")
**Batch**: 1
**Total iterations**: 4 (cap 5)
**WebSearch calls**: 12 (3 per turn × 4)
**WebFetch calls**: 8 (5 succeeded, 2× HTTP 403 on the paywalled ScienceDirect
article, 1× `maxContentLength exceeded` on arXiv:2304.06972 PDF)
**Cap hit**: no — stopped at turn 4 by the `ENOUGH` rule (iteration_4.md
records the reason: field context saturated, prior-art verdict complete)

## Search trace

### Turn 1 — the three §12.3 mechanisms, broadly
Terms: (1) `knowledge distillation multi-fidelity teacher low-fidelity input student parameter-only PDE surrogate`;
(2) `learning using privileged information neural operator PDE surrogate low-fidelity available only at training`;
(3) `multi-resolution auxiliary loss coarse grid supervision neural operator few high-fidelity samples`.
Chosen because pretrain→finetune is already occupied by the mandatory declared
baseline, so turn 1 probed distillation + auxiliary-loss + the LUPI framing.
Key findings: a surrogate-modeling paper that distils privileged auxiliary
modalities into a deployment-input-only student
[cite: https://www.sciencedirect.com/science/article/abs/pii/S0952197625034293];
LF-trained emulators can beat their training solver against an HF reference
[cite: https://arxiv.org/html/2510.23111]; the closest multi-resolution operator
paper explicitly disclaims the multi-fidelity reading and does **not** use coarse
grids as auxiliary training signals [cite: https://arxiv.org/html/2510.23810].
→ `iteration_1.md`

### Turn 2 — pin down the candidate preemption; is "MF distillation" a named field?
Terms: (1) `"Learning from more to predict with less" …`;
(2) `multi-fidelity distillation low-fidelity teacher student network inference without low-fidelity model`;
(3) `privileged information distillation regression simulation surrogate "at inference" cheaper input unavailable`.
Key findings: the EAAI paper's abstract (returned twice, consistently) names
"full-field simulation outputs" as a privileged modality, uses
representation-level KD, and reports **outperforming the privileged teacher in
data-scarce regimes**
[cite: https://www.sciencedirect.com/science/article/abs/pii/S0952197625034293];
"multi-fidelity distillation" is **not** a populated named literature for PDE
field surrogates (term 2 returned only vision/NAS re-readings); PI-distillation
is 2026-active and its train→test transfer gap is called an open challenge
[cite: https://arxiv.org/abs/2602.04942]; LUPI canon
[cite: https://www.researchgate.net/publication/301362871_Learning_using_privileged_information_Similarity_control_and_knowledge_transfer].
→ `iteration_2.md`

### Turn 3 — joint/composite MF, coarse-to-fine curricula, value-of-LF ablations
Terms: (1) `multi-fidelity DeepONet parametric input predict low and high fidelity jointly auxiliary head multi-task`;
(2) `coarse-to-fine curriculum training target resolution neural PDE surrogate spectral bias low-pass supervision schedule`;
(3) `multi-fidelity neural network ablation with and without low-fidelity data value of low fidelity data 5 high-fidelity samples`.
Key findings: the composite MFNN whose LF sub-network maps the parameter input
to the LF value, with LF data used only in training and no LF solve at inference
[cite: https://arxiv.org/abs/1903.00104] — the canonical preemption of
"learn-LF-from-condition then correct"; MF-DeepONet input augmentation appends
the LF **prediction** to the trunk [cite: https://dl.acm.org/doi/10.1016/j.jcp.2023.112462];
a critical-perspective paper warning that coarse-graining causes "irreversible
information loss" [cite: https://arxiv.org/html/2604.20061v1]; and **no** prior
art at all for a matched with/without-LF value-of-information ablation at
N_hf ≈ 5 for field prediction. → `iteration_3.md`

### Turn 4 — targeted refutation of the three candidate directions (§3.3)
Terms: (1) `distill neural operator teacher that consumes low-fidelity field into student predicting from parameters only`;
(2) `auxiliary task predict coarse-grid solution same parameters regularize surrogate discard auxiliary head at test time`;
(3) `multilevel Monte Carlo training neural operators telescoping gradient coarse resolution control variate`.
Key findings: no work distils a field-consuming MF teacher into a
condition-only student (search engine said so explicitly); external published
prior art for the exact `mf_fno_transfer_film` recipe
[cite: https://arxiv.org/pdf/2304.06972]; auxiliary-heads-discarded-at-test is
generic ML but has no retrieved PDE-multi-fidelity instance; MLMC operator
training is a telescoping **cost-reduction** estimator on a mesh hierarchy, with
no treatment of coarse levels covering *different parameters*
[cite: https://arxiv.org/abs/2505.12940, https://arxiv.org/abs/2501.12739].
→ `iteration_4.md`

## Prior-art verdict

| Candidate direction | Verdict | Citations (fetched/returned this loop) | What remains open |
|---|---|---|---|
| **D1** — distil an LF-consuming multi-fidelity teacher (round-1 family, §5.10b, absent at test) into a condition-vector-only student predicting the HF field | **preempted-but-MF-composition-open** | https://www.sciencedirect.com/science/article/abs/pii/S0952197625034293 (EAAI Dec 2025 — privileged modalities incl. full-field simulation outputs → representation-level KD → deployment-input-only student; 403 on fetch, abstract returned by two independent searches); https://www.researchgate.net/publication/301362871_Learning_using_privileged_information_Similarity_control_and_knowledge_transfer (LUPI canon); https://arxiv.org/abs/2602.04942 (PI-distillation, LM domain, calls the transfer gap open) | No retrieved work makes the privileged modality a **coarse consistent solve of the same PDE**, with a **condition-vector-only student** emitting a **full (H,W) field**, at N_hf = 5 / 400-sample nested ladders. The targeted refutation search (turn 4 term 1) returned nothing in that slot. |
| **D2** — nested multi-resolution auxiliary target heads: shared condition→latent trunk with extra heads regressing the l1/l2 coarse-solve fields, heads discarded at test | **preempted-but-MF-composition-open** | https://arxiv.org/abs/1903.00104 (composite MFNN: LF net from parameter input, LF data train-only, no LF solve at inference); https://dl.acm.org/doi/10.1016/j.jcp.2023.112462 and https://arxiv.org/pdf/2310.00057 (MF-DeepONet, LF prediction fed into the trunk); https://proceedings.neurips.cc/paper/2020/file/4f87658ef0de194413056248a00ce009-Paper.pdf and https://arxiv.org/pdf/2508.06109 (auxiliary heads discarded at inference = standard deep supervision) | The published composites put LF **inside the test-time prediction path**; keeping the LF heads strictly out of that path, as a pure representation regularizer on a **fully nested** ladder (identical conditions, differing only by grid truncation), was not retrieved. Caveat to state on the card: https://arxiv.org/html/2604.20061v1 warns coarse-graining is irreversible information loss — the LF heads can only supply a spectral-truncation/curriculum prior, not new content (this is the on-disk nested-ladder fact from `summary_so_far.md`). |
| **D3** — LF-as-parameter-coverage on ifc_poisson: use the 100/50/20 LF samples at conditions **disjoint** from the 5 HF conditions, with a matched with/without-LF ablation | **novel** (nearest neighbors named) | Nearest: https://arxiv.org/abs/2505.12940 (MLMC operator training — telescopic gradient over mesh levels; abstract-fetched: benefit is efficiency "while maintaining a high level accuracy", Pareto curve accuracy-vs-time); https://arxiv.org/abs/2501.12739 (multiscale gradient estimation, same telescoping for CNNs, equal variance with fewer fine-mesh convolutions) | Both nearest neighbors are *resolution hierarchies of the same problem* aimed at *cost*. Neither covers a coarse level at **different parameter values** than the fine level. Also, iteration 3 term 3 found **no** matched with/without-LF value-of-information ablation at N_hf ≈ 5 for field prediction anywhere — that measurement (round-2 success criterion 1) is itself unclaimed. |

## Citations summary

- [EAAI 2025] "Learning from more to predict with less: Representation-level multimodal distillation to address training–inference data asymmetry in surrogate modeling" — https://www.sciencedirect.com/science/article/abs/pii/S0952197625034293 — used in: iteration_1 (term 1), iteration_2 (terms 1 & 3), iteration_4 (D1 verdict). **Fetch 403 on both URL forms; only search-returned abstract text was used, and iteration_2 quotes it verbatim.**
- [Meng & Karniadakis 2019] "A composite neural network that learns from multi-fidelity data" — https://arxiv.org/abs/1903.00104 — used in: iteration_3 (term 1, fetched abstract page), iteration_4 (D2 verdict).
- [Rowbottom et al. 2025/26] "Multi-Level Monte Carlo Training of Neural Operators" — https://arxiv.org/abs/2505.12940 (CMAME: https://www.sciencedirect.com/science/article/pii/S0045782526000745) — used in: iteration_4 (term 3, fetched abstract page), D3 verdict.
- [—] "Multiscale Training of Convolutional Neural Networks" — https://arxiv.org/abs/2501.12739 — used in: iteration_4 (term 3, search-returned).
- ["Neural Emulator Superiority"] "When Machine Learning for PDEs Surpasses its Training Data" — https://arxiv.org/html/2510.23111 — used in: iteration_2 (fetched; superiority ratio ξ[t]<1, state-space vs autoregressive superiority).
- [—] "A Physics-informed Multi-resolution Neural Operator" — https://arxiv.org/html/2510.23810 — used in: iteration_1 (term 3, fetched; explicitly disclaims multi-fidelity, no coarse auxiliary signals).
- [—] "Predictivity and Utility of Neural Surrogates of Multiscale PDEs" — https://arxiv.org/html/2604.20061v1 — used in: iteration_3 (term 2, fetched; "irreversible information loss" from coarse-graining).
- [Howard et al. 2023] "Multifidelity DeepONets" — https://dl.acm.org/doi/10.1016/j.jcp.2023.112462 — used in: iteration_3 (term 1, search-returned).
- [—] MF-DeepONet fusing simulation and monitoring data — https://arxiv.org/pdf/2310.00057 — used in: iteration_3 (term 1, search-returned).
- [—] "Multi-fidelity prediction of fluid flow and temperature field based on transfer learning using FNO" — https://arxiv.org/pdf/2304.06972 — used in: iteration_4 (term 1, search-returned; fetch failed on size).
- [Vapnik & Izmailov] "Learning using privileged information: similarity control and knowledge transfer" — https://www.researchgate.net/publication/301362871_Learning_using_privileged_information_Similarity_control_and_knowledge_transfer — used in: iteration_2 (term 3, search-returned).
- [2026] "Privileged Information Distillation for Language Models" — https://arxiv.org/abs/2602.04942 — used in: iteration_2 (term 3, search-returned).
- [—] "Auxiliary Task Reweighting for Minimum-data Learning" — https://proceedings.neurips.cc/paper/2020/file/4f87658ef0de194413056248a00ce009-Paper.pdf — used in: iteration_4 (term 2, search-returned).
- [—] "Incremental Spatial and Spectral Learning of Neural Operators" — https://openreview.net/pdf?id=xI6cPQObp0 — used in: iteration_3 (term 2, search-returned).
- [—] "Spectral bias in physics-informed and operator learning: analysis and mitigation guidelines" — https://arxiv.org/html/2602.19265v1 — used in: iteration_3 (term 2, search-returned).
- In-repo prior websearches (cited, not re-derived): `docs/reports/MF_Leaderboard_Beaters_2026_Report.md` §4.2–4.3 (F-Adapter arXiv:2509.23173, MLMC arXiv:2505.12940 as [LF-10], MF-DeepONet subsampling arXiv:2503.17941, FilDeep arXiv:2601.10031, DPOT arXiv:2403.03542, MOFS arXiv:2508.01211) and `docs/reports/MF_Sharp_HighFreq_Report.md` §2.3 (Tang arXiv:2308.09113, Howard arXiv:2204.09157) — used in `summary_so_far.md`.

## Dead ends

- `multi-fidelity distillation low-fidelity teacher student network inference without low-fidelity model` → every hit re-reads "multi-fidelity" as NAS budget levels or "multi-scale" as image resolution; the search engine itself noted the results do not address inference without the LF model. The term is not a named literature for PDE surrogates.
- `multi-fidelity neural network ablation with and without low-fidelity data … 5 high-fidelity samples` → the MF-NN literature assumes LF helps; no matched-budget with/without-LF accounting was returned. (Good news for round-2 criterion 1; a dead end as prior art.)
- `auxiliary task predict coarse-grid solution same parameters …` → only generic deep-supervision/auxiliary-head literature; no PDE-multi-fidelity instance retrieved.
- Two sources could not be verified first-hand and are flagged in the iteration files: the EAAI ScienceDirect article (HTTP 403 on both URL forms — abstract text only) and arXiv:2304.06972 (PDF exceeded the fetch size limit — snippet only).
- Two search-synthesis claims were explicitly marked **NOT citable** because they could not be attributed to a fetched paper: the "79% error reduction from coarse-to-fine training" figure (iteration_3) and "coarse solutions reused as auxiliary pre-training labels" (iteration_4). A batch-2 search should chase the latter.

## For the brainstormer

The brainstormer MUST quote the prior-art verdict above for whatever it proposes.

1. **Do not propose LF-pretrain→HF-finetune in any undifferentiated form.** It is
   the mandatory declared baseline (`mf_fno_transfer_film`, program.md §12.3),
   AND it is externally published for FNO
   (https://arxiv.org/pdf/2304.06972), AND the plasma-edge surrogate paper
   quantifies its small-data gain (order of magnitude,
   https://iopscience.iop.org/article/10.1088/1741-4326/adfdfb, iteration_1).
   Score it as an arm; never as the contribution.
2. **The ladder asymmetry is the design fulcrum** (verified on disk,
   `summary_so_far.md`): on all five sharp/helmholtz panel datasets the LF rungs
   carry the *same* condition vectors as HF (cahn_hilliard `x` is (400,19) at
   l1, l2 and l3), so LF adds **no parameter coverage** — only spectral
   truncation. On `ifc_poisson` the fidelity 8/16/32/64 sets hold 100/50/20/5
   samples at **disjoint** conditions (none of the 5 HF rows appears in the f8
   or f32 sets) — 170 extra conditions against 5 HF. Program.md §12.3 demands a
   statement of "what the LF rungs add"; this is that statement, and it differs
   per dataset. Expect the mechanism that works on ifc_poisson to fail on the
   sharp panel and say so in the falsification clause.
3. **D3 is the only `novel` verdict** and is the one that lines up with round-2
   success criterion 1. Its nearest neighbors (MLMC / multiscale gradient
   estimation) optimize *cost at equal accuracy* on nested mesh hierarchies —
   quote that when claiming the coverage variant is different.
4. **If proposing D1 (teacher distillation), quote
   `preempted-but-MF-composition-open` and cite
   https://www.sciencedirect.com/science/article/abs/pii/S0952197625034293**,
   stating the open composition explicitly: coarse *consistent solve* as the
   privileged modality, condition-vector-only student, full-field output,
   N_hf = 5. Note that paper's own claim that the student can *beat* the
   privileged teacher in data-scarce regimes — that is a testable prediction
   here, and also a warning that "student < teacher" is not automatic evidence
   of anything.
5. **If proposing D2 (auxiliary coarse-target heads), quote
   `preempted-but-MF-composition-open` and cite
   https://arxiv.org/abs/1903.00104** — the composite MFNN already learns LF
   from the parameter input with no LF solve at inference. The only defensible
   differentiator is keeping the LF heads out of the test-time path entirely, and
   the honest information claim is bounded by
   https://arxiv.org/html/2604.20061v1 ("irreversible information loss").
6. **Design against the anchor, not against optimism.** The launch anchor is the
   best-floor panel geomean **23.06** (per-dataset: helmholtz 3.34 zero, pfc
   59.81 mean, allen_cahn 269.20 NN, fisher_kpp 11.99 mean, cahn_hilliard 23.18
   NN, ifc_poisson 10.05 NN). Falsification thresholds must be judged directly
   (noise floor is provisional until r2s4-B1); the round-1-rescaled spreads are
   0.13–10.68 skill units, so a sub-unit sharp-panel delta is not a claim.
   `mf_fno_transfer_film` is the LF-arm reference and already ran here as a
   condition→HF model in round 1 — reuse its numbers rather than re-deriving.
