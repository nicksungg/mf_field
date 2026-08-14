# Literature digest: interpretability-for-discovery angle on the FNO-FiLM benchmark winner

Prepared 2026-08-14 for a planned submission to the NeurIPS 2026 workshop "Interpretability for Discovery" (deadline 2026-08-29 AoE).
Verification tags: [VERIFIED] = claim checked against the actual arXiv abstract / page fetch; [UNVERIFIED] = search-snippet only.

## 1. The workshop itself

Source pages fetched directly: https://interpretability4discovery.github.io/ (main), /about.html, /cfp.html — all [VERIFIED via page fetch 2026-08-14].

### What "interpretability as a tool for discovery" means to the organizers

The premise: AI models now match or exceed human experts across domains (protein structure, clinical forecasting, astronomy, climate science, animal communication, games), and "to reach that performance, they appear to have learned patterns and regularities that humans have not yet articulated."
"Interpretability gives us a way to read those representations back out."
The workshop explicitly "reframes interpretability as a tool for discovery, not just explanation," aiming to "turn what models encode into knowledge that domain experts can test and validate."
Their three core questions: (Q1) how can interpretability methods adapt to architectures, inductive biases, and data modalities beyond standard language and vision models; (Q2) how can interpretable internal representations become actionable, testable new knowledge; (Q3) what questions can interpretability help answer that are currently unknown to humans.
They stress that "discovery requires more than a compelling visualization — it requires methods, translation, and validation."

### What contributions fit

Four topic buckets: (01) methods/models for knowledge discovery across unfamiliar architectures and modalities; (02) interpretability-driven discovery — "empirical case studies where examining model internals surfaces non-obvious, verifiable knowledge in science and expert domains"; (03) position/theory papers on epistemology and validation; (04) failure cases and negative results.
Our paper is a clean 01+02 fit: neural operators are exactly an "unfamiliar architecture/modality beyond language and vision," and explaining why the simple recipe wins is an empirical case study whose claims are verifiable against held-out datasets and known physics.
The bar the organizers set is validation: the interpretation should yield a testable claim (e.g., a predicted regime where the recipe fails, then confirmed on held-out datasets), not just visualizations.

### CFP mechanics (page marked "tentative")

Up to 5 pages main text, +1 page allowed at camera-ready (max 6); references and appendices excluded but main text must be self-contained; reviewers not required to read appendices.
Double-blind (remove names, affiliations, acknowledgments, GitHub/HuggingFace usernames; cite own prior work in third person); NeurIPS 2026 workshop LaTeX template; single PDF via OpenReview, private during review.
Non-archival: prior non-archival work and work concurrently under review elsewhere are welcome; already-archival-accepted work is excluded except via a NeurIPS 2026 fast track.
**Responsible-use statement: "Every submission must include a short statement covering potential societal impacts and suggested mitigations. A missing statement is grounds for desk rejection."**
Open-sourcing code/data/models is strongly encouraged and reviewers "will be specifically asked to consider reproducibility"; they recommend anonymous.4open.science for repos and anonymous HF accounts for weights/data.
Key dates: submission 2026-08-29 AoE; notification on/before 2026-09-29; workshop Dec 12 or 13, 2026, Atlanta.
OpenReview accounts without institutional email can take up to two weeks to approve — register early.
Organizers: Xiaoyan Bai and Chenhao Tan (UChicago), Yonatan Belinkov and Yaniv Nikankin (Technion), Ekdeep Singh Lubana (Goodfire), Amirtha Varshini A S (Montai); sponsor Goodfire; invited speakers include Been Kim (DeepMind), John F. Wu (JHU, astro), Katrin Franke (Stanford, neuro), Gašper Beguš (Berkeley).
Failure cases and negative results are explicitly welcomed — useful safety valve if some analyses come back null.

## 2. Interpretability / analysis methods applicable to an FNO-FiLM model

### Spectral / Fourier-mode analyses of FNO

- Qin et al. 2024, "Toward a Better Understanding of Fourier Neural Operators from a Spectral Perspective," arXiv:2404.07200. [VERIFIED]
  Analyzes FNO behavior mode-by-mode in the spectral domain and shows FNO is ineffective with large Fourier kernels that parameterize more frequencies; the closest existing template for "open up the spectral weights of a trained FNO and read them."
- Rahaman et al. 2018, "On the Spectral Bias of Neural Networks," arXiv:1806.08734. [VERIFIED]
  Foundational result that gradient-trained networks learn low frequencies first; the theoretical backdrop for any claim that LF pretraining hands the FNO its low-frequency map "for free."
- George et al. 2022, "Incremental Spatial and Spectral Learning of Neural Operators for Solving Large-Scale PDEs," arXiv:2211.15188. [VERIFIED]
  Exploits the observation that FNO training dynamics fill in Fourier modes incrementally from low to high; supports a training-dynamics-in-frequency-space analysis of the warm start.
- Kalimuthu et al. 2025, "LOGLO-FNO: Efficient Learning of Local and Global Features in Fourier Neural Operators," arXiv:2504.04260. [VERIFIED]
  Documents FNO's high-frequency deficiency (spectral bias + explicit mode truncation) and adds a local branch plus a frequency-aware loss; useful for framing what the fine-tune stage must supply.
- Shi et al. 2026, "SirenFNO: Efficient and Full Frequency Learning of Fourier Neural Operators," arXiv:2606.11518. [VERIFIED]
  Recent confirmation that frequency truncation drives FNO's low-frequency bias; another citation that per-band error analysis is the community's accepted lens on FNOs.
- Bartolucci et al. 2023, "Representation Equivalent Neural Operators: a Framework for Alias-free Operator Learning," arXiv:2305.19913. [VERIFIED]
  Formalizes aliasing in discretized operator learning; relevant because LF→HF grids are exactly an aliasing-sensitive setting, and it grounds a "what does the model do at the grid-Nyquist boundary" probe.

### FiLM parameter interpretation

- Perez et al. 2017, "FiLM: Visual Reasoning with a General Conditioning Layer," arXiv:1709.07871. [VERIFIED]
  The original FiLM paper itself performs the canonical analyses: histograms of learned gamma/beta (finding many near-zero or negative gammas that switch channels off), t-SNE of FiLM parameters clustering by conditioning content, and ablations (scaling-only, shifting-only, restricted gamma).
  These analyses port directly to a physics condition vector: gamma/beta as functions of Reynolds number, diffusivity, etc.
- Dumoulin, Perez et al. 2018, "Feature-wise transformations," Distill, https://distill.pub/2018/feature-wise-transformations/. [VERIFIED via page fetch]
  Survey of FiLM-family conditioning showing the same mechanism underlies conditional instance norm, adaptive instance norm, and hypernetwork-style conditioning; establishes the interpretation vocabulary (feature selection, gating, task embedding geometry).
- Kirchmeyer et al. 2022, "Generalizing to New Physical Systems via Context-Informed Dynamics Model (CoDA)," arXiv:2202.01889. [VERIFIED]
  Adapts dynamics models across physical contexts via low-rank context-conditioned weight modulation; the learned context vectors are shown to organize by physical parameter — precedent for "the conditioning pathway encodes physical parameter geometry."
- Shokar et al. 2025, "Conditioning on PDE Parameters to Generalise Deep Learning Emulation of Stochastic and Chaotic Dynamics," arXiv:2509.09599. [VERIFIED]
  Pretrains on one parameter regime then generalizes by explicit PDE-parameter conditioning; closest recent precedent for the condition-vector half of our winner's recipe.

### Transfer / warm-start analyses (why pretraining works)

- Neyshabur, Sedghi, Zhang 2020, "What is being transferred in transfer learning?," arXiv:2008.11687 (NeurIPS 2020). [VERIFIED]
  The template paper for our transfer analysis: separates feature reuse from low-level data statistics, and shows pretrained-then-finetuned models stay in the same loss basin, close in parameter space and similar in feature space.
  Every one of its probes (basin membership via interpolation, module-wise criticality, feature similarity) has a direct LF→HF analogue.
- Frankle et al. 2019, "Linear Mode Connectivity and the Lottery Ticket Hypothesis," arXiv:1912.05671. [VERIFIED]
  Defines linear mode connectivity (no loss barrier on the linear path between solutions); the standard tool to test whether the LF-pretrained and HF-finetuned solutions are "the same solution, refined" vs "different solutions."
- Kornblith et al. 2019, "Similarity of Neural Network Representations Revisited," arXiv:1905.00414 (CKA). [VERIFIED]
  CKA is the standard layer-wise representation-similarity metric across differently-trained models; note the known finite-sample bias caveat in high-dim/low-sample regimes (relevant because our HF sample counts are small).
- Lee et al. 2022, "Surgical Fine-Tuning Improves Adaptation to Distribution Shifts," arXiv:2210.11466. [VERIFIED]
  Shows which-layers-to-finetune depends on the type of shift (input-level shifts → early layers); LF→HF is an input/resolution-level shift, so this predicts a testable localization of the correction.
- Meyes et al. 2019, "Ablation Studies in Artificial Neural Networks," arXiv:1901.08644. [VERIFIED]
  Systematizes ablation (zero/mean ablation of units and components) as an interpretability method in its own right, borrowed from neuroscience lesion studies; the citation that legitimizes ablation-as-interpretability methodology.
- Tolooshams et al. 2025, "Mechanistic Interpretability with Sparse Autoencoder Neural Operators," arXiv:2509.03738. [VERIFIED]
  Introduces sparse autoencoders that operate in function space (SAE-NOs) and a "functional representation hypothesis"; the most direct bridge from LLM-style mechanistic interpretability to neural operators, and an on-theme citation for this workshop's audience.

## 3. Prior work interpreting PDE surrogates / physics-informed models

- Boullé, Earls, Townsend 2021/2022, "Data-driven discovery of Green's functions with human-understandable deep learning," arXiv:2105.00266 (Sci. Rep. 12:4824). [VERIFIED]
  Trains rational NNs to learn Green's functions of hidden linear PDEs and then reads physics back out of the learned kernel: symmetries, conservation laws, singularity/shock locations, boundary effects, dominant modes.
  The flagship precedent that a trained solution operator is itself a physically readable object; companion thesis Boullé 2022, arXiv:2210.16016. [VERIFIED]
- Cranmer et al. 2020, "Discovering Symbolic Models from Deep Learning with Inductive Biases," arXiv:2006.11287 (NeurIPS 2020). [VERIFIED]
  Distills symbolic force laws (and a new dark-matter formula) from trained GNNs via sparsity + symbolic regression, with the extracted formulas generalizing OOD better than the network; the canonical interpretability-for-discovery success story to cite in the intro.
- Krishnapriyan et al. 2021, "Characterizing possible failure modes in physics-informed neural networks," arXiv:2109.01050 (NeurIPS 2021). [VERIFIED]
  Explains PINN failures through loss-landscape analysis rather than proposing a new model; a strong precedent for "analysis paper about why a SciML method behaves as it does."
- Yang et al. 2024, "Interpretable Machine Learning for Weather and Climate Prediction: A Survey," arXiv:2403.18864. [VERIFIED]
  Organizes SciML interpretability into post-hoc attribution vs inherently interpretable designs and documents cases where attribution recovered physical mechanisms (e.g., precipitation triggering); a good taxonomy citation.
- Liu et al. 2025, "Neural Interpretable PDEs: Harmonizing Fourier Insights with Attention for Scalable and Interpretable Physics Discovery," arXiv:2505.23106. [VERIFIED]
  Builds interpretability into an FNO/attention hybrid whose latent representations are meant to expose governing structure; evidence the "interpretable neural operator" thread is active in 2025.
- Wang et al. 2026, "Discovering Physical Directions in Weight Space: Composing Neural PDE Experts," arXiv:2605.14546. [VERIFIED]
  Finds that fine-tuning updates of a shared PDE operator form physically meaningful directions in weight space that can be composed; directly relevant precedent for interpreting our warm-start fine-tune delta as a physical object.
- Li et al. 2026, "From Basis to Basis: Gaussian Particle Representation for Interpretable PDE Operators," arXiv:2602.21551. [VERIFIED]
  Motivated by the complaint that neural-operator latent features and attention weights are rarely tied to physically meaningful modes; proposes an interpretable particle basis.
- Kastor et al. 2026, "Parameter conditioned interpretable U-Net surrogate model for data-driven predictions of convection-diffusion-reaction processes," arXiv:2601.22654. [VERIFIED]
  Parameter-conditioned surrogate marketed on interpretability; shows parameter-conditioning + interpretability is a recognized combination but at single-model scale, not benchmark scale.

## 4. Framing precedents: "benchmark finds simple baseline wins, paper explains why"

- Grinsztajn, Oyallon, Varoquaux 2022, "Why do tree-based models still outperform deep learning on tabular data?," arXiv:2207.08815 (NeurIPS 2022 D&B). [VERIFIED]
  The archetype for our paper's shape: large benchmark → simple/classical method wins → controlled empirical investigation of inductive biases → three distilled explanations (robustness to uninformative features, preserving data orientation, learning irregular functions).
  Its methodology — transform the data to break one hypothesized advantage at a time and watch the gap close — is directly portable ("ablation-as-explanation").
- Zeng et al. 2022, "Are Transformers Effective for Time Series Forecasting?," arXiv:2205.13504 (DLinear, AAAI 2023). [VERIFIED]
  One-layer linear models beat sophisticated Transformer forecasters on nine benchmarks; the famous "embarrassingly simple baseline" paper (note the ensuing debate — PatchTST etc. — as a caution to make our win claims tight).
- Dacrema, Cremonesi, Jannach 2019, "Are We Really Making Much Progress? A Worrying Analysis of Recent Neural Recommendation Approaches," arXiv:1907.06902. [VERIFIED]
  Shows most neural recommenders lose to tuned simple heuristics; precedent for benchmark-driven deflation of architectural complexity.
- Gulrajani, Lopez-Paz 2020, "In Search of Lost Domain Generalization," arXiv:2007.01434 (DomainBed). [VERIFIED]
  Under equalized model selection, plain ERM beats a myriad of domain-generalization algorithms; the standard citation that careful benchmarking often crowns the simple method.
- Huang et al. 2020, "Combining Label Propagation and Simple Models Out-performs Graph Neural Networks," arXiv:2010.13993. [VERIFIED]
  Simple classical pipeline beats GNNs on node classification; explicitly frames the question "why are GNNs successful and are they necessary."
- McGreivy, Hakim 2024, "Weak baselines and reporting biases lead to overoptimism in machine learning for fluid-related partial differential equations," arXiv:2407.07218 (Nat. Mach. Intell.). [VERIFIED]
  79% of ML-for-PDE papers claiming to beat numerics compared against weak baselines; ammunition for why a strong-baseline finding on a large PDE benchmark is itself a contribution, and why explaining the strong baseline matters.
- Gupta, Brandstetter 2022, "Towards Multi-spatiotemporal-scale Generalized PDE Modeling," arXiv:2209.15616. [VERIFIED]
  Large-scale comparison showing modern U-Nets are highly competitive with FNOs on PDE surrogacy; in-domain precedent that architecture novelty ≠ benchmark wins.
- Benchmark context to cite for the benchmark half: Takamoto et al. 2022, PDEBench, arXiv:2210.07182 [VERIFIED]; Ohana et al. 2024, "The Well," arXiv:2412.00568 (NeurIPS 2024 D&B) [VERIFIED]; McCabe et al. 2023, "Multiple Physics Pretraining for Physical Surrogate Models," arXiv:2310.02994 [VERIFIED].

## 5. Interpreting multi-fidelity ML models specifically

- Meng, Karniadakis 2019, "A composite neural network that learns from multi-fidelity data," arXiv:1903.00104 (JCP 2020). [VERIFIED]
  The classic MF architecture explicitly decomposes the LF→HF map into a linear correlator plus a nonlinear correction network; the decomposition itself is an interpretability statement (where is the fidelity gap linear vs nonlinear), and it grounds a linear-vs-nonlinear LF↔HF correlation probe.
- Howard et al. 2022, "Multifidelity Deep Operator Networks For Data-Driven and Physics-Informed Problems," arXiv:2204.09157 (JCP 2023). [VERIFIED]
  MF DeepONet via residual learning + input augmentation; the operator-learning instantiation of the Meng decomposition.
- Lu et al. 2022, "Multifidelity deep neural operators for efficient learning of PDEs with application to fast inverse design of nanoscale heat transport," Phys. Rev. Research 4:023210. [UNVERIFIED search-snippet only]
  MF DeepONet applied to nanoscale heat transport; cited here as additional evidence for the MF-operator line.
- Lyu et al. 2023, "Multi-fidelity prediction of fluid flow and temperature field based on transfer learning using Fourier Neural Operator," arXiv:2304.06972. [VERIFIED]
  Pretrains an FNO on cheap LF data and fine-tunes on scarce HF data by migrating the LF parameters as initialization — this is essentially our winning recipe, published as a method paper for one application; it contains no analysis of *why* it works, which is exactly the gap our paper fills.
- De et al. 2020, "On transfer learning of neural networks using bi-fidelity data for uncertainty propagation," arXiv:2002.04495. [VERIFIED]
  Early systematic study of bi-fidelity transfer (partial freezing vs full fine-tune) for surrogate UQ.
- Goswami et al. 2022, "Deep transfer operator learning for partial differential equations under conditional shift," arXiv:2204.09810 (Nat. Mach. Intell.). [VERIFIED]
  Transfer learning framework for operator learning under conditional shift; the citable bridge between transfer-learning theory and operator learning.
- Villatoro et al. 2025, "Assessing the performance of correlation-based multi-fidelity neural emulators," arXiv:2512.02868. [VERIFIED]
  Evaluates when correlation-based MF emulation actually helps as a function of LF quality/correlation — the closest existing thing to an "LF-informativeness analysis," but framed as performance assessment, not interpretation of what the network learned.
- Chen et al. 2024, "Data-Efficient Operator Learning via Unsupervised Pretraining and In-Context Learning," arXiv:2402.15734. [VERIFIED]
  Pretraining for data-efficient operator learning; context for why LF-pretraining is the cheap-data path.
- Gap statement: I found no paper that mechanistically interprets what a multi-fidelity surrogate's correction pathway has learned (spectrally, layer-wise, or in weight space) across a broad benchmark.
  The nearest neighbors are Villatoro 2512.02868 (performance-level, not mechanism), Meng 1903.00104 (interpretation by architectural construction), and Wang 2605.14546 (weight-space physics, but single-fidelity fine-tuning).
  That gap is the paper's novelty claim; it should be stated with this citation set as evidence of due diligence.

## Candidate interpretability angles for the paper (ranked)

1. **Spectral division-of-labor analysis of the warm start.**
   Hypothesis: LF pretraining hands the FNO the low-frequency map essentially for free, and HF fine-tuning edits only the high-wavenumber tail plus interface bands.
   Method: per-frequency-band nRMSE before/after fine-tuning, energy spectra of the predicted correction (HF − LF), and direct inspection of the spectral-weight matrices R(k) of each FNO layer pre/post fine-tune (delta-norm per mode).
   Grounded in Qin arXiv:2404.07200, Rahaman arXiv:1806.08734, George arXiv:2211.15188; note the round-3 per-band spectral probes in the repo already implement much of the measurement.
   This is the strongest angle because it turns the benchmark win into a physics statement: which spectral content of the HF solution the LF solve already determines.

2. **Feature reuse vs rediscovery à la Neyshabur.**
   Method: layer-wise CKA between LF-pretrained and HF-finetuned checkpoints, parameter-space distance, and linear-interpolation loss barriers (LF-pretrained ↔ finetuned, and finetuned-from-warm-start ↔ trained-from-scratch) to show warm start keeps the model in the LF basin while cold starts land elsewhere; correlate basin membership with the win margin per dataset.
   Grounded in Neyshabur arXiv:2008.11687, Frankle arXiv:1912.05671, Kornblith arXiv:1905.00414 (mind CKA's small-sample bias — our HF sets are small).

3. **FiLM gamma/beta atlas over physical parameters.**
   Method: plot learned gamma/beta per channel as functions of the condition vector across datasets; quantify channel switch-off (near-zero gamma) and gating sparsity; embed FiLM parameter vectors (PCA/t-SNE) and check they organize by physical regime (e.g., diffusive vs advective, sharpness of interfaces); compare gamma-sensitivity per parameter against finite-difference sensitivity of the true field to that parameter.
   Grounded in the analyses in Perez arXiv:1709.07871 and Dumoulin et al. Distill 2018, with CoDA arXiv:2202.01889 as physics-side precedent.
   Discovery framing: the FiLM pathway is a learned, readable map of which physical parameters matter where.

4. **LF-informativeness map: where the recipe wins and why.**
   Method: per-dataset, measure the linear vs nonlinear LF↔HF correlation (linear probe / Meng-style linear correlator vs full model; spectral coherence between LF and HF fields) and regress the winner's margin over competitors against these dataset-level quantities across the ~30 datasets.
   Grounded in Meng arXiv:1903.00104 and Villatoro arXiv:2512.02868.
   This is the analysis only a large benchmark can do, and it yields the testable prediction the workshop wants: a pre-computable dataset statistic that forecasts when the simple recipe will win (validate on held-out datasets).

5. **Causal ablation of the conditioning and fusion pathways.**
   Method: ablate FiLM to identity (gamma=1, beta=0), shuffle/swap condition vectors between samples, and ablate the LF input (replace with dataset-mean field); measure per-dataset degradation to attribute the win between LF-informativeness and parameter-conditioning; mirror the Grinsztajn transform-the-data methodology by degrading LF quality (coarser consistent solves) to trace the dose-response.
   Grounded in Meyes arXiv:1901.08644 (ablation-as-interpretability), Perez arXiv:1709.07871 (FiLM ablations), Grinsztajn arXiv:2207.08815 (ablation-as-explanation shape).

6. **Surgical re-freezing to localize the fidelity correction.**
   Method: fine-tune with only one block unfrozen at a time (lifting layer, each Fourier block's spectral weights vs pointwise path, FiLM generator, projection head) and with spectral weights unfrozen only above/below a mode cutoff; report where 90% of the warm-start gain lives.
   Grounded in Lee arXiv:2210.11466 (shift type predicts effective layers) with Wang arXiv:2605.14546 as precedent that fine-tune deltas carry physical meaning.

7. **Effective-kernel / Green's-function readout on near-linear datasets.**
   Method: probe the trained operator with impulse and GP inputs on the datasets whose PDEs are (near-)linear, reconstruct the effective kernel, and compare with the analytic Green's function: symmetry, locality/decay length, boundary behavior; report where fine-tuning changed the kernel.
   Grounded in Boullé arXiv:2105.00266; highest wow-factor per unit risk on the subset of linear datasets (Poisson/heat families in the benchmark are ideal).

8. **Function-space SAE probe of the winner's latents (stretch goal).**
   Method: train an SAE-NO on the winner's intermediate function-space activations, inspect discovered features for physical structure (interface detectors, band-limited modes), and test them by causal ablation.
   Grounded in Tolooshams arXiv:2509.03738; maximally on-theme for this workshop's mechanistic-interpretability audience but the least mature method, so position it as an appendix or future-work teaser unless results are strong.

### Practical framing notes

Lead with the Grinsztajn shape: benchmark result (1 figure) → three named hypotheses → one analysis per hypothesis → a distilled "what the win teaches us about multi-fidelity PDE data" section with a validated prediction.
Cite McGreivy arXiv:2407.07218 in the motivation: the field's baseline hygiene problem makes a strong-simple-baseline finding, plus its explanation, a community service.
State the novelty gap explicitly with the Section-5 citation set: no prior work mechanistically interprets a multi-fidelity surrogate at benchmark scale.
Do not forget the responsible-use statement (desk-reject if missing) and the anonymized code release (anonymous.4open.science), which reviewers are told to weigh.
