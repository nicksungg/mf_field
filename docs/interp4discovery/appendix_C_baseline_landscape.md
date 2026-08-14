# Baseline-set defensibility digest — MFFP workshop paper (deadline 2026-08-29)

Compiled 2026-08-14 from web research (WebSearch + direct arXiv/GitHub verification).
[VERIFIED] = confirmed against the arXiv abstract, paper HTML, or live repo during this session.
[UNVERIFIED] = from search snippets or prior knowledge only; ID/details not independently confirmed.

## 1. The canonical baseline set in multi-fidelity ML-for-PDE papers (2022-2026)

The literature splits into two nearly disjoint baseline lineages, and knowing which lineage a reviewer comes from predicts what they will ask for.

### Lineage A — GP / neural-process "vector-output surrogate" papers (params → field)

- **AR(1) cokriging (Kennedy & O'Hagan 2000)** — linear autoregressive coupling f_hi = ρ·f_lo + δ(x) with a GP discrepancy; the universal classical baseline.
  Appears as a baseline in FIRE (arXiv:2601.22371, Jan 2026) and is packaged as MFK in the SMT toolkit (smt.readthedocs.io). [VERIFIED]
- **NARGP (Perdikaris et al. 2017, Proc. R. Soc. A)** — nonlinear autoregressive multi-fidelity GP that feeds the LF posterior into the HF kernel; sequential training with nested inputs.
  Baseline in MFRNP (verified from paper HTML) and in FIRE's 7-baseline set. [VERIFIED]
- **ResGP** — residual GP (independent GP on the HF−LF residual); in FIRE's baseline list. [VERIFIED]
- **Deep Coregionalization / DRC (arXiv:1910.07577)** — LMC-style latent-process emulation of spatial-temporal fields; the usual "deep GP" baseline in this lineage. [VERIFIED-ID only]
- **DMF (Li et al. 2021)** — per-fidelity neural nets with latent propagation between fidelity levels; baseline in MFRNP. [VERIFIED]
- **MF-HNP (arXiv:2206.04872, KDD 2022)** — multi-fidelity hierarchical neural processes; latent-variable hierarchy across fidelities; baseline in MFRNP and D-MFD. [VERIFIED]
- **D-MFD / disentangled MF deep Bayesian active learning (arXiv:2305.04392)** — disentangles local/global latents per fidelity; the "previous SOTA" MFRNP compares against. [VERIFIED]
- **IFC (arXiv:2207.00678, NeurIPS 2022)** — infinite-fidelity coregionalization via a neural-ODE latent output over continuous fidelity; the team's existing published anchor.
  Public code: github.com/shib0li/Infinite-Fidelity-Coregionalization (datasets: Heat, Poisson, Burgers, TopOpt, Navier-Stokes). [VERIFIED]
- **GAR (arXiv:2301.05729, NeurIPS 2022)** — tensor-generalized autoregression handling arbitrary-dimensional outputs with tractable likelihood. [VERIFIED]
- **ContinuAR (NeurIPS 2023)** — continuous autoregression for infinite-fidelity fusion; reports up to 4x accuracy and 62,500x training speedup over IFC; baseline in FIRE. [VERIFIED via NeurIPS proceedings page; arXiv ID not confirmed]
- **MFRNP (arXiv:2402.18846, ICML 2024)** — residual neural process aggregating lower-fidelity outputs and modeling the HF residual; the team's other anchor.
  Its own baseline set, verified from the paper: SF-NP (single-fidelity lower bound), DMF, NARGP, MF-HNP, D-MFD; datasets Heat/Poisson/Fluid + climate. [VERIFIED]
  Public code: github.com/Rose-STL-Lab/MFRNP. [VERIFIED]
- **FIRE (arXiv:2601.22371, Jan 2026, MIT/Faez Ahmed group)** — multi-fidelity regression via distribution-conditioned in-context learning with TabPFNv2.5.
  Compares against exactly 7 baselines on 31 problems: AR(1), ResGP, NARGP, ContinuAR, MisoKG, MFBNN (DNN-LR-BNN), MFRNP — this is the most current statement of the canonical lineage-A set. [VERIFIED from paper HTML]

### Lineage B — neural-operator / field-to-field papers (LF field + params → HF field; the team's actual task)

- **Composite MF neural network (Meng & Karniadakis, arXiv:1903.00104, JCP 2020)** — linear + nonlinear correlation nets on top of an LF net; the foundational MF-PINN baseline, very widely cited. [VERIFIED-ID via search]
- **Multifidelity DeepONet (Howard, Perego, Karniadakis, Stinis; arXiv:2204.09157, JCP 2023)** — composite DeepONet trained on two fidelity levels; the standard MF operator-learning citation. [VERIFIED]
- **Transfer-learned FNO (arXiv:2304.06972, Phys. Fluids 2023)** — pretrain FNO on abundant LF data, fine-tune on scarce HF data, exploiting FNO grid invariance; direct published precedent for the team's transfer-FNO family. [VERIFIED]
- **MF-FNO for geological carbon storage (J. Hydrology 2024, ScienceDirect S0022169424000350)** — same pretrain/finetune recipe at field scale. [UNVERIFIED details]
- **Multi-Fidelity Flow Matching / MFFM (arXiv:2605.16118, May 2026)** — cascaded flow-matching refinement of LF PDE solutions to HF; the closest published work to the team's exact task shape.
  Its baseline set, verified from the paper HTML: **bilinear upsampling (explicit no-learning "task-difficulty zero line"), FNO-direct, FNO-residual, DeepONet-residual, F-FNO, CNO, PDE-Refiner, single-level FM**, on 8 benchmarks with global NRMSE. [VERIFIED]
  This paper is the best single template for what a 2026 reviewer in this niche expects a baseline table to look like.

### Frequency summary

Lineage-A papers (IFC, GAR, ContinuAR, MFRNP, FIRE) baseline almost exclusively against each other plus AR(1)/NARGP; they essentially never run FNO-class models.
Lineage-B papers baseline against FNO variants, DeepONet variants, U-Net/CNN correctors, and an interpolation control; they essentially never run the GP/NP stack.
The team's design (in-house FNO-family set + published IFC/MFRNP numbers as anchors) already covers both lineages — one by implementation, one by citation — which is a defensible and articulable position.

## 2. What the big PDE surrogate benchmarks use as reference baselines

- **PDEBench (arXiv:2210.07182, NeurIPS 2022 D&B)** — baselines: FNO, U-Net, PINN; FNO generally strongest. [VERIFIED]
- **PDEArena (arXiv:2209.15616, "Towards Multi-spatiotemporal-scale Generalized PDE Modeling")** — baselines: FNO variants, dilated ResNets, modern U-Nets; contributes U-FNet hybrids; code github.com/pdearena/pdearena (311 stars). [VERIFIED]
- **The Well (arXiv:2412.00568, Polymathic AI, 15 TB / 16 datasets)** — baselines: FNO, Tucker-factorized TFNO, U-Net, ConvNeXt U-Net (CNextU-net), each time-boxed to 12 H100-hours; code github.com/PolymathicAI/the_well (4.3k stars). [VERIFIED]
- **CFDBench (arXiv:2310.05963)** — baselines: feed-forward nets, DeepONet, FNO, U-Net and variants; 302K frames, 739 cases; code github.com/luo-yining/CFDBench (292 stars). [VERIFIED]
- **SuperBench (arXiv:2306.14070)** — scientific super-resolution benchmark (fluid, cosmology, weather) with bicubic interpolation among the reference methods; closest benchmark to the LF→HF upsampling framing. [VERIFIED abstract; model list UNVERIFIED]
- Takeaway: every major benchmark's floor set is {FNO, U-Net} plus one trivial control; none of them treat GP methods as required baselines; transformer models (Transolver/OFormer/DPOT/Poseidon) appear in follow-up papers, not in the benchmarks' own core tables. [VERIFIED for the four benchmarks above]

## 3. Recent strong general models (2024-2026) a reviewer might name-drop

- **Poseidon (arXiv:2405.19101, ETH)** — scOT (multiscale operator transformer, shifted-window attention) foundation model pretrained on fluid PDEs; evaluated by fine-tuning on 15 downstream tasks; strong sample efficiency.
  Public code + pretrained checkpoints: github.com/camlab-ethz/poseidon (194 stars). [VERIFIED]
  Adaptation to LF+params→HF: moderate — requires input-channel surgery (LF field as an input "state", params via their conditioning) and finetuning; days of work, GPU-cheap per dataset, but fairness tuning is the risk.
- **DPOT (arXiv:2403.03542, ICML 2024)** — auto-regressive denoising pretrained Fourier-attention transformer, up to 0.5B params, 10+ datasets; code github.com/thu-ml/DPOT (60 stars) + HuggingFace weights. [VERIFIED]
  Designed for autoregressive temporal rollout; adapting to a one-shot LF→HF mapping is a nontrivial re-purposing.
- **scOT** — the backbone of Poseidon; not a separate baseline to add. [VERIFIED via Poseidon abstract]
- **Transolver (arXiv:2402.02366 [UNVERIFIED-ID], ICML 2024)** — physics-attention over learned slices; code github.com/thuml/Transolver (399 stars) [VERIFIED repo].
  The team already has in-house Transolver hybrids, so this reviewer objection is pre-empted.
- **Transolver++ (arXiv:2502.02414)** — parallelized physics-attention for million-scale meshes; no official standalone public repo found (thuml/Transolver_plus_plus 404s). [VERIFIED absence as of 2026-08-14]
  Irrelevant scale regime for 64-256 px grids; safe to cite-and-dismiss.
- **AROMA (arXiv:2406.02176, NeurIPS 2024)** — latent local-neural-field PDE model with diffusion-based transformer dynamics; code github.com/LouisSerrano/aroma (28 stars). [VERIFIED]
- **UPT (arXiv:2402.12365, NeurIPS 2024)** — Universal Physics Transformers, unified grid/particle neural-operator scaling framework; code github.com/ml-jku/UPT (167 stars). [VERIFIED]
- **UPS (arXiv:2403.07187)** — LLM-warm-started FNO-transformer unified solver; SOTA on 8/10 PDEBench tasks with 4x less data. [VERIFIED abstract; code not checked]
- **FactFormer (arXiv:2305.17560, NeurIPS 2023)** — axial factorized attention for large-grid surrogates; code github.com/BaratiLab/FactFormer (57 stars). [VERIFIED]
- **F-FNO, CNO, PDE-Refiner** — appear as the operator-family baselines in MFFM 2026; all have public code (F-FNO arXiv:2111.13802, CNO arXiv:2302.01178, PDE-Refiner arXiv:2308.05732 [UNVERIFIED-IDs]).
  An F-FNO or CNO backbone swap inside the team's existing training harness is the cheapest way to add a "non-in-house architecture" if desired.
- Cheap-to-adapt ranking: F-FNO/CNO backbone swap (cheapest, drop-in), Poseidon finetune (moderate, highest name value), FactFormer (moderate), AROMA/UPT/DPOT/UPS (expensive re-purposing for a non-rollout task, poor fit).

## 4. Simple non-neural baselines reviewers expect in multi-fidelity settings

- **Bilinear/bicubic prolongation of LF, no learning** — MFFM (arXiv:2605.16118) not only includes it but builds §5.4 around "bilinear as the task-difficulty zero line": the bilinear NRMSE equals ‖HF−I(LF)‖/‖HF‖ and organizes datasets into low/intermediate/large-residual regimes. [VERIFIED from paper HTML]
  SRaFTE/RELift (arXiv:2509.12220) likewise adopt bicubic interpolation of the coarse solve as the standing baseline for coarse-to-fine propagation. [VERIFIED via search snippets]
  SuperBench institutionalizes bicubic as the reference in scientific super-resolution. [VERIFIED abstract]
- **Single-fidelity lower bound** — MFRNP includes SF-NP, "the naive single-fidelity neural process trained on the highest fidelity data, as the lower performance bound"; the analogous control here is an FNO trained on HF-only (no LF input). [VERIFIED]
- **Linear map on LF (AR(1) structure)** — the Kennedy-O'Hagan form ρ·LF + δ is literally a per-dataset linear regression from LF to HF; the SMT MFK implementation and FIRE's AR(1) baseline show it remains a live 2026 comparison. [VERIFIED]
- **Multi-fidelity GP on a subsampled grid / PCA coefficients** — standard in lineage A (NARGP, AR(1)); tractable on ~30 datasets only via output subsampling or PCA, and precedented since deep-coregionalization papers use exactly that reduction. [VERIFIED lineage; specific "GP-on-subsampled-grid in an operator paper" precedent UNVERIFIED]
- **Bicubic + learned correction (residual U-Net / CNN)** — MFFM's FNO-residual and DeepONet-residual are exactly "upsample then learn the correction"; PDEBench/The Well U-Net ubiquity makes a U-Net corrector the expected CNN instance. [VERIFIED precedents]
- Precedent papers insisting on such controls: MFFM (bilinear, structural), MFRNP (single-fidelity floor), SRaFTE (bicubic), SuperBench (bicubic); collectively this is now a norm, not an option, for LF→HF papers. [VERIFIED]

## 5. Baseline norms at analysis-focused workshop papers

- The NeurIPS ML4PS workshop (the archetype venue for this kind of paper) caps submissions at 4 pages, discourages appendices, and instructs reviewers not to read beyond page 4. [VERIFIED — ml4physicalsciences.github.io/2025/guidelines.html]
- ML4PS review criteria are novelty, correctness, relevance, and promise of future impact; "minor flaws will not be the sole reason to reject"; negative/null results and advanced-stage incomplete work are explicitly welcome. [VERIFIED]
- Only the ML4PS Datasets & Benchmarks track hard-requires baseline results plus public code, and it notes "the baselines need not use machine learning" — direct evidence that a non-neural control satisfies the venue's own definition of a baseline. [VERIFIED]
- The NeurIPS 2026 main-conference reviewer guidelines emphasize claims-evidence match rather than baseline count; workshops inherit a weaker version of this. [VERIFIED page exists; content not deep-read]
- Survey observation: typical accepted ML4PS-style papers run 2-5 baselines, most of them re-implementations or library models, and comparisons to published numbers are common and accepted practice when compute-matched reruns are impractical. [UNVERIFIED — qualitative reading of the field; no systematic count performed]
- An 8-family in-house set spanning FNO/transfer/fusion/stacking/Transolver/DINO variants is *larger* than typical workshop baseline sets; the exposure is not count but *independence* (all baselines share one codebase) and the missing no-learning control. [assessment]

## Recommendation inputs

### (a) Candidate additional baselines, ranked by reviewer-expectation × implementation cost

| Rank | Candidate | Reviewer expectation | Implementation cost | Notes |
|---|---|---|---|---|
| 1 | Bilinear/bicubic LF→HF prolongation (no learning) | Very high — structural in MFFM 2026, SRaFTE, SuperBench | Trivial (hours; fits smoke_eval contract as a degenerate family) | Doubles as the per-dataset difficulty axis for the interpretability story |
| 2 | HF-only FNO (single-fidelity floor, no LF input) | High — MFRNP's SF-NP precedent; isolates the value of LF | Trivial if not already present (ablate LF channel) | May already exist implicitly; promote to explicit table row |
| 3 | Linear AR(1)-style map: per-pixel ridge ρ·LF+δ(params) | High in MF niche — Kennedy-O'Hagan is the field's origin | Low (~1 day, scikit-learn) | Cheap, kills "is nonlinearity needed" question |
| 4 | U-Net corrector on upsampled LF | High — U-Net is in every major benchmark's floor set | Low-medium (2-3 days; standard architecture, existing harness) | Adds the one missing architecture class (pure CNN) |
| 5 | MFRNP official code on 2-3 team datasets | Medium-high — converts the published-number anchor into a head-to-head | Medium (code exists, Rose-STL-Lab/MFRNP; data-adapter work; params→field task shape matches) | Strongest possible defense of the anchor methodology |
| 6 | F-FNO or CNO backbone swap | Medium — MFFM uses both; "non-in-house code" optics | Medium (public repos, drop into training loop) | Marginal over existing FNO family |
| 7 | AR(1)/NARGP GP on PCA-reduced outputs | Medium (lineage-A reviewers only) | Medium (emukit/SMT + PCA; fragile on 30 datasets) | Anchors IFC/MFRNP numbers already cover this lineage |
| 8 | Poseidon-B finetune | Medium (name-drop risk) | Medium-high (channel surgery + per-dataset finetune + fairness tuning) | High blowback risk if under-tuned; deadline-hostile |
| 9 | DPOT / AROMA / UPT / UPS / FactFormer | Low for this task shape | High (rollout-oriented; re-purposing) | Cite in related work; do not run |

### (b) The 2-3 cheapest highest-credibility additions

1. **Bilinear/bicubic LF prolongation** — one afternoon, and it converts the benchmark's difficulty structure into an interpretable axis (MFFM's §5.4 move); by far the highest credibility-per-hour.
2. **Linear AR(1)-style regression (ρ·LF + δ, ridge, params-conditioned)** — one day; jointly with #1 it brackets the task (no learning / linear learning / deep learning) and pre-empts both classical-MF and "trivial-task" objections.
3. **HF-only FNO floor** (or, if that already exists, the **U-Net corrector**) — a few days; establishes that the LF input is doing the work, which is the core claim of any multi-fidelity paper.

### (c) For/against adding baselines given the 5-page interpretability framing

**For adding only the cheap controls (recommended):**
The paper's contribution is analysis of *why* FiLM-conditioned transfer wins across ~30 datasets, not a new architecture, so the reviewer question is "are the comparisons meaningful", not "is every 2026 model present".
The two real vulnerabilities of an all-in-house set are (i) no no-learning control, so a skeptic cannot see whether the datasets are hard, and (ii) no evidence the LF input matters; ranks 1-3 above close both for under a week of work.
The MFFM 2026 paper (arXiv:2605.16118) is same-task published precedent whose entire baseline table is interpolation + FNO/DeepONet variants — mirroring its structure lets the team cite it as the community standard they meet.
The IFC and MFRNP published-number anchors legitimately cover the GP/NP lineage, since those papers themselves never run FNO-class baselines against their own methods; symmetry is a defensible argument to state explicitly in the paper.
ML4PS-style venues explicitly tolerate non-ML baselines, minor flaws, and in-progress work; an 8-family set plus anchors plus two trivial controls is above the venue norm.

**Against adding external heavyweight models:**
Fifteen days is not enough to *fairly* tune Poseidon/DPOT-class models on 30 datasets, and an under-tuned foundation-model baseline is a bigger review liability than its absence ("you strawmanned Poseidon").
Foundation models are pretrained for autoregressive temporal rollout, not LF+params→HF regression, so any adaptation is itself a contested design choice that dilutes a 5-page analysis paper.
The correct treatment for Poseidon/DPOT/Transolver++/AROMA/UPT is one related-work sentence explaining the task-shape mismatch, with the Transolver objection already answered by the in-house Transolver hybrids.

**Bottom line:** the in-house set is defensible *if and only if* the paper adds the no-learning prolongation control and a linear/single-fidelity floor, states the two-lineage coverage argument explicitly, and cites MFFM (2605.16118) as the same-task precedent whose baseline design it matches.
