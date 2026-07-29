# Iteration 4 — `s4_hybrid_routing` batch 1 — PRIOR-ART VERDICT (§3.3)

**ENOUGH** declared on field context after iteration 3: three iterations already
returned the same core cluster (SPAMoE / U-HNO / MoE-POT / 2508.21249 / LGFNet)
from four different phrasings, so the marginal return on more survey queries is
zero. This iteration spends its budget entirely on **refuting the novelty** of
the three directions this stream-batch is likely to propose.
**Loop stops here at k=4 of the 5-iteration cap** — the verdicts are decided and
a fifth turn would add citations, not change any verdict.

## The three candidate directions

Derived from program.md §12.4 (the stream's seed direction and its explicit
novelty boundary) plus the open questions in `summary_so_far.md`:

- **D1 — Benchmark the built hybrid.** Score
  `mf_field/akash/models/fno_transolver_seq` (FNO-FiLM base + zero-init,
  alpha-gated Transolver corrector trained on out-of-fold LF->HF residuals) on the
  round's 6-dataset panel at smoke tier. §12.4: *"BUILT but unbenchmarked — batch
  1 should start by scoring it on the panel (cheap, mostly evaluation)."*
- **D2 — LF-conditioned per-region routing.** A spatially-resolved gate that
  routes between an FNO expert and a Transolver expert, with the gate conditioned
  on the LF field (local LF structure / LF-HF disagreement proxy), initialized so
  the composition is exactly the per-dataset best expert at step 0.
- **D3 — Per-band fidelity routing.** Assign Fourier bands to LF-copy vs learned
  expert, with the cutoff `k_c` estimated from LF/HF cross-spectral coherence
  (the P4 mechanism in `docs/reports/MF_Sharp_HighFreq_Report.md`).

## Refutation searches run this turn

Terms used:
1. `Transolver Fourier neural operator combined hybrid residual correction physics attention slice` (attacks D1)
2. `error-aware spatial routing between two neural operator branches uncertainty gated correction identity initialization no-harm` (attacks D2)
3. `copy low-fidelity low frequency band predict only high frequency residual neural operator super-resolution spectral gate multi-fidelity PDE` (attacks D3)

### Term 1 results (D1)

- "Enhancing Solutions for Complex PDEs: Introducing Complementary Convolution
  and Equivariant Attention in Fourier Neural Operators" —
  https://arxiv.org/abs/2311.12902 / https://arxiv.org/pdf/2311.12902
- Transolver-is-a-Linear-Transformer (AAAI) — https://arxiv.org/pdf/2511.06294 ,
  https://ojs.aaai.org/index.php/AAAI/article/download/37003/40965
- Transolver architecture topic pages —
  https://www.emergentmind.com/topics/transolver-architecture ,
  https://www.emergentmind.com/topics/transolver-architectures
- GAIA geometry-adaptive operator learning — https://arxiv.org/pdf/2607.01128

**Fetched** https://arxiv.org/abs/2311.12902 (PDF fetch failed on binary; the
abstract page succeeded). Verbatim abstract obtained. It demonstrates
*"the FNO approximates kernels primarily in a relatively low-frequency domain"*
and proposes *"a novel hierarchical Fourier neural operator along with
convolution-residual layers and attention mechanisms to make them complementary
in the frequency domain to solve complex PDEs"*, tested on multiscale elliptic,
Navier-Stokes and other benchmarks. Composition is **sequential/hierarchical, no
gating, no multi-fidelity component.**

Also noted from the search synthesis (NOT fetched, therefore NOT citable): the
AAAI paper's claim that *"slice attention may even hurt the model performance"*
and that a plain Linear Attention Neural Operator beats Physics-Attention. If
true this is a material risk to D1's premise — flagged for the brainstormer as
an unverified caution, not a citation.

### Term 2 results (D2)

- ANCHOR, "Error-Controlled Adaptive Numerical Correction for Neural Operator
  Time Marching" — https://arxiv.org/pdf/2512.19643 (**fetch FAILED**:
  `maxContentLength size of 10485760 exceeded`; therefore not citable. From the
  search synthesis only: *"adaptive switching between the neural operator and
  numerical solver based on a physics-informed error estimator"* — routing between
  a network and a SOLVER, not between two operator experts, and time-marching.)
- UQNO / residual operator predicting local error magnitude (search synthesis;
  no fetched URL)
- "Residual-based error correction for neural operator accelerated
  infinite-dimensional Bayesian inverse problems" — https://arxiv.org/pdf/2210.03008
- "Adaptive Branch Specialization in Spectral-Spatial GNNs" — https://arxiv.org/pdf/2505.08320
- "Topology-Preserving Neural Operator Learning via Hodge Decomposition" — https://arxiv.org/pdf/2605.13834

**No fetched source shows a router whose input is a low-fidelity solution field.**
Third independent negative on that specific cell (iteration 2 term 2, iteration 3
term 1, here).

### Term 3 results (D3)

- "Correcting Neural Operator Spectral Bias via Diffusion Posterior Sampling with
  Sparse Observations" — https://arxiv.org/pdf/2606.03936
- IRNO — https://arxiv.org/pdf/2605.24041 (owned by `s3_testtime`)
- "Spatial-Frequency Gated Swin Transformer for Remote Sensing SISR" —
  https://arxiv.org/html/2605.09687v1 (estimate low-frequency content via a
  depthwise-blur branch, extract HF residual by subtraction, refine and
  adaptively inject — the vision analogue of D3, but the "LF" is a blur of the
  input, not an independent coarse solve)
- Contourlet Refinement Gate framework (infrared SR) —
  https://link.springer.com/article/10.1007/s11263-025-02668-0
- Super-Resolution Neural Operator, V2Rho-FNO, audio Time-Frequency Networks

Search synthesis named **SpecBoost** (*"trains a secondary residual operator
specifically tasked with learning the high-frequency residuals left by the
primary model"*) — **not fetched, not citable**, but a strong lead that
high-frequency residual boosting of an FNO is published. **No fetched source**
sets a band cutoff from LF/HF cross-spectral coherence or hard-copies a real
coarse-solve LF band. Third independent negative on that cell.

## VERDICTS

### D1 — benchmark `fno_transolver_seq` on the panel
**`preempted-but-MF-composition-open`**

- The mechanism "spectral operator handles the smooth global field, an
  attention/transformer module corrects where it is locally wrong" is published:
  **"Hybrid operator learning of wave scattering maps in high-contrast media"**,
  https://arxiv.org/html/2602.11197 (FNO for the smooth background field + a
  ViT-based corrector for the high-contrast scattering part; found and recorded
  in iteration_1.md), and **arXiv:2311.12902** (hierarchical FNO +
  convolution-residual + attention made *complementary in the frequency domain*;
  fetched this turn).
- **What remains open:** neither fetched source is multi-fidelity. The specific
  MF composition in the built family — out-of-fold LF->HF residual targets from a
  K-fold rerun of the HF fine-tune, the *real LF field* as the corrector's
  attention context, and a scalar gate `alpha` set by least-squares + line search
  containing 0 (so a useless correction reduces the hybrid **exactly** to the
  FNO) under N_hf-scarce conditions — appears in no fetched source.
- **Practical note:** D1 is a *measurement* card. It should not claim novelty at
  all; the honest framing is "this composition is published (2602.11197,
  2311.12902); we are measuring whether the +30.6% oracle survives when the
  composition is scored against copy-LF on sharp 2-D fields."

### D2 — LF-conditioned per-region routing between FNO and Transolver experts
**`preempted-but-MF-composition-open`**

- **Spatially-resolved gating over heterogeneous operator experts, weighted by
  each expert's localized performance, is published**: "A Mixture of Experts
  Gating Network for Enhanced Surrogate Modeling in External Aerodynamics",
  https://arxiv.org/abs/2508.21249 — gates DoMINO / X-MeshGraphNet / FigConvNet
  with *"a spatially-variant weighting strategy, assigning credibility to each
  expert based on its localized performance"*; beats both the ensemble average
  and the best single expert (no formal no-harm guarantee).
- **Per-location HARD routing between a spectral branch and a local/attention
  branch is published**: U-HNO, https://arxiv.org/pdf/2605.12965 — Sparse-Point
  Adaptive Routing emits a per-location hard branch choice with gradient masking,
  gating weights zero-initialized. Benchmarks Burgers/Darcy/NS/shallow-water,
  **no multi-fidelity input**.
- **Generic MoE-over-operators is published**: MoE-POT,
  https://arxiv.org/abs/2510.25803 (16 routed + 2 shared experts, layer-wise
  router-gating, Fourier/AFNO token mixer per block; routing specializes by PDE
  *equation family*).
- **What remains open (exactly):** (i) a router whose **input is the LF field or
  the LF-HF disagreement** — three independent negative queries, and the leading
  MF operator-learning paper (**arXiv:2507.07292**, fetched) states explicitly
  that it *"does not employ routing, gating, or mixture-of-experts mechanisms
  between different operator architectures"*; (ii) an **identity-safe routing
  construction** that provably reduces to the per-dataset best expert (needed by
  §12.4's requirement that routing preserve `transolver_residual` on the 4
  beyond-copy datasets it wins) — 2508.21249 has no such guarantee, U-HNO's
  zero-init only balances branches at init.
- Nearest neighbor overall: **arXiv:2508.21249**. A card must cite it and state
  that the LF-conditioning of the router is what is new.

### D3 — per-band fidelity routing with `k_c` from LF/HF coherence
**`preempted-but-MF-composition-open`** — and **flagged against a pre-falsified
lever**.

- **Soft frequency-band routing over complementary operator experts is
  published**: SPAMoE, https://arxiv.org/html/2604.07421 — concentric soft
  frequency-band decomposition (Gaussian masks, K overlapping bands), a learnable
  per-expert **frequency-preference** parameter, and a **spectral-energy attention
  router** with Top-k=2 over FNO (low-freq global) / MNO (mid) / LNO (high-freq
  sharp interfaces) experts. Explicitly **no multi-fidelity component**.
- Frequency-complementary FNO+conv+attention composition also published
  (**arXiv:2311.12902**, fetched this turn).
- Treating the LF field as a *"low-frequency carrier"* and learning only the
  nonlinear fidelity-gap delta is published: **LGFNet**,
  https://arxiv.org/abs/2603.29303 (verbatim abstract fetched; local
  sliding-window branch + global self-attention branch; **no router**; fidelity
  axis is CFD vs wind-tunnel/flight-test, not coarse-vs-fine solve).
- **What remains open:** no fetched source estimates the band cutoff from
  **LF/HF cross-spectral coherence** on the scarce HF pairs, nor hard-copies a
  real coarse-solve LF band while predicting only `k > k_c`.
- **MANDATORY CAUTION (program.md §5 pre-falsified levers):** *"LF low-mode
  freezing (`mf_fno_spectral`): worst on sharp, catastrophic on lid-cavity."*
  D3 in its hard-constraint form **is** LF low-mode freezing. §5 permits
  attacking the mechanism behind a falsified lever *with a new composition*, but
  the card must cite the falsification and state exactly what differs (e.g. a
  data-derived, per-dataset `k_c` and a learned low-band correction rather than a
  fixed frozen low-mode block). Without that, D3 is a re-proposal of a
  pre-falsified lever and the brainstormer's immutables self-check should reject
  it.

## Uncitable leads (recorded so no one cites them from memory)

- "A MULTI-FIDELITY MIXTURE-OF-EXPERT FRAMEWORK" (OpenReview PDF) — fetch blocked
  by browser verification; no arXiv mirror found. **Not citable.**
- AGMF-Net adaptive gated multi-fidelity network with a deep-MoE gating
  sub-network (ScienceDirect, paywalled) — **not citable**, but if real it is the
  closest published thing to "MoE gating inside a multi-fidelity network". Any
  novelty claim of that exact shape is **at risk**.
- SpecBoost (secondary residual operator for the HF residual left by the primary)
  — search synthesis only, **not citable**.
- ANCHOR arXiv:2512.19643 — fetch failed (size cap). **Not citable.**
- LCWF-MFS local-correlation-weighted multi-fidelity fusion (ScienceDirect) —
  not fetched, **not citable**.
- AAAI "Transolver is a Linear Transformer" claim that slice attention may hurt —
  synthesis only, **not citable**, but a real risk to D1's premise.
