# Related Work & Novelty — Research Findings

Deep-research pass (2026-06-10) supporting the MFFP "FiLM-conditioned FNO" paper.
Claims below were extracted from primary sources and adversarially verified
(2/3-vote refutation harness; most carry multiple independent high-confidence
verdicts). Where a verdict was only `medium` confidence the reason is noted.

> Provenance note: the deep-research workflow completed its search/fetch/verify
> phases but died before the final synthesis step; this report is reconstructed
> from the verified claim journal, not the auto-synthesis. All arXiv IDs and
> quotes were verified against primary sources by the verification agents.

---

## 1. NOVELTY — does "FiLM-conditioned FNO" already exist?

**Yes, FiLM+FNO exists — but not for our task or our multi-fidelity mechanism.**
Our exact combination (FiLM conditioning as the vehicle for LF→HF multi-fidelity
*transfer* in an FNO, for static parameter-vector→field prediction) appears
unpublished. The honest framing: we are **not** the first FiLMed FNO; we **are**
the first to use FiLM conditioning for multi-fidelity transfer in neural
operators, demonstrated by a controlled concat-vs-FiLM ablation + 15-dataset
benchmark.

### Closest prior art (THE paper to distinguish from)
- **Zhu, Raccuglia & Brenner, 2025 — "Generalizing PDE Emulation with
  Equation-Aware Neural Operators", arXiv:2511.09729** (Harvard / Google
  Research, submitted 12 Nov 2025). Explicitly builds a **"FiLMed FNO"**: *"FNO
  blocks are conditioned via Feature-wise Linear Modulation (FiLM) [perez2018film]
  and dynamically generated spectral weights"*; *"FiLM layers use c to apply a
  feature-wise affine transformation after spatial convolutions."* Conditions on
  a 7-dim PDE-equation/coefficient encoding. Cites Perez 2018 (FiLM) and Li 2020
  (FNO).
  - **How it differs from us (both axes that define our contribution):**
    1. Task = **autoregressive time-stepping** rollout u(t)→u(t+Δt), not static
       parameter-vector→field.
    2. Goal = **zero-shot generalization across equations**; the paper contains
       **no multi-fidelity** and **no LF→HF transfer learning** (verified: the
       words "multi-fidelity"/"transfer learning" do not appear). Its Method-4
       "Learned Correction" over a coarse solver is single-stage, not
       pretrain-LF-then-finetune-HF.
  - It is *also* a useful **conditioning-taxonomy** reference: across its four
    architectures it uses FiLM, **hypernetwork-generated spectral weights** (MLP
    on c → spectral-conv weights), **spectral gating** (Fourier modes × gate
    vector from c), and **global cross-attention** (latent=query, c→key/value).
    (One verdict flagged that it is a 4-architecture *proposal*, not a
    comparative taxonomy/survey, and does not isolate plain concat as a mechanism
    — cite it for "these mechanisms exist," not as a controlled comparison.)

### Second-closest (parallel FiLM-transfer design, different backbone)
- **Shokar, Kerswell & Haynes, 2025 — "Conditioning on PDE Parameters to
  Generalise Deep Learning Emulation of Stochastic and Chaotic Dynamics",
  arXiv:2509.09599** (Cambridge). Conditions a PDE emulator on PDE parameters via
  **FiLM-via-adaptive-LayerNorm**: *"we replace feature-wise affine transformation
  parameters in layer normalisation with a learned function of the conditioning
  information"*, generating per-block γ (scale) and δ (shift) for attention+MLP
  sublayers; **γ=1/δ=0 fixed during pretraining, adapted during fine-tuning** —
  i.e. zero-init FiLM + pretrain→finetune, *closely paralleling our exact design*.
  - **How it differs:** backbone is a **local-attention Transformer, NOT an FNO**
    (it explicitly contrasts with FNO and cites FNO's low-frequency bias); task is
    **time-stepping** of chaotic dynamics; its pretrain/finetune is **cross-domain-
    size generalization, not LF/HF multi-fidelity** data fusion.
  - **ACTION:** our code/manifest cites this as `beggs2025pdecond` — the authors
    are **Shokar, Kerswell & Haynes**, not "Beggs". Fix the citation key/name.

### The original FiLM
- **Perez, Strub, de Vries, Dumoulin & Courville, 2018 — "FiLM: Visual Reasoning
  with a General Conditioning Layer", arXiv:1709.07871** (AAAI 2018). Origin of
  feature-wise affine modulation γ(c)·h + β(c). Cited by both papers above and by us.

---

## 2. CONDITIONING TAXONOMY for FNOs / neural operators

How a global parameter/condition vector can be injected into a neural operator:

| Mechanism | What it does | Representative work |
|---|---|---|
| **Constant-channel concatenation** | broadcast c to a constant field, concat with input channels before the lift | standard practice; our `mf_fno_transfer_bar` baseline; Lyu 2023 (2304.06972) |
| **FiLM / affine modulation** | per-block per-channel γ(c)·h+β(c) (optionally via adaptive LayerNorm) | **Zhu 2025 (2511.09729, FiLMed FNO)**; **Shokar 2025 (2509.09599, adaLN)**; Perez 2018 (1709.07871); **OUR METHOD** |
| **Hypernetwork → weights** | an MLP/Transformer maps c to the operator's weights (incl. spectral-conv weights) | Zhu 2025 (MLP→spectral weights); **HyPINO** (Swin-Transformer→PINN weights) |
| **Spectral gating** | multiply Fourier modes of the latent by a gate vector from c | Zhu 2025 "LSC-FNO" |
| **Cross-attention** | latent=query, c (or input history)→key/value, modulating a Fourier trunk | Zhu 2025; **SpectraKAN, arXiv:2602.05187** (single-query cross-attention over a multi-scale Fourier trunk; conditions on spatio-temporal *history*, targets time-stepping) |

---

## 3. MULTI-FIDELITY NEURAL-OPERATOR FAMILIES (and how they condition on fidelity)

| Family | MF mechanism | Representative work |
|---|---|---|
| **Transfer learning (LF→HF)** — *our base* | pretrain one network on abundant LF, fine-tune same net on scarce HF; relies on FNO grid-invariance | **Lyu et al. 2023, arXiv:2304.06972** (MF-FNO, Phys. Fluids 35:077118; ~99% accuracy, fluid/temperature fields); **Geological Carbon Storage MF-FNO, arXiv:2308.09113** (110k→1M cells; works when HF extremely limited — relevant to few-shot-HF) |
| **Residual / additive correction** | model the residual between aggregated LF output and HF truth | **MFRNP** (neural-process MF; SOTA baseline; residual via decoder aggregation, *not* transfer); **MF-DeepONet** (couples two DeepONets via residual + input augmentation; ~10× lower error than single-fidelity at equal HF); **Demo, Tezzele & Rozza 2023** (DeepONet learns residual over a POD-ROM) |
| **Coregionalization** | continuous-fidelity outer-product basis head f(x,m)=B(m)·h(x,m) | IFC-style; our `fno_coregionalization` |
| **Discretization-invariance as MF** | one operator handles multiple mesh resolutions; resolution = fidelity, no explicit conditioning | discretization-independent MF operator-learning paper (claims "first comprehensive study" that discretization-independence enables MF) |
| **Multi-resolution active learning** | treat resolution as a cost/fidelity proxy; actively choose which fidelity to query | **MRA-FNO** |

**Fidelity is rarely a FiLM input.** Across these, fidelity is handled by network
reuse (transfer), an architectural residual link, a coregionalization head, or
discretization-invariance — **not** by feature-wise modulation. This is the gap our
method fills. (NB: our own `fno_coreg_conditioned` FiLMs on the *fidelity index m*
while still concatenating X — the opposite design from our winner, which FiLMs on
X and lets transfer carry the fidelity.)

---

## 4. POSITIONING — likely reviewer objections & responses

1. **"FiLMed FNO already exists (Zhu 2025)."** → True for the *mechanism*; we do
   not claim to invent FiLM-FNO. Our contribution is (a) FiLM as the
   *multi-fidelity transfer* vehicle (Zhu has no MF/transfer), (b) the
   static parameter→field task (Zhu is time-stepping), (c) a controlled
   concat-vs-FiLM ablation isolating the mechanism, and (d) the 15-dataset
   benchmark. Cite Zhu prominently and draw the boundary.
2. **"FNO obviously wins on smooth PDEs — foregone conclusion."** → Pre-empt with
   the regime split: FiLM wins **both** smooth (0.0018) *and* the hard,
   non-smooth regime (0.175), where it overtakes the previously-best hand-designed
   fusion (`fno_coreg_residual`, 0.208). The win is not regime-restricted.
3. **"Is it the mechanism or just capacity?"** → The concat baseline
   (`mf_fno_transfer_bar`) has the *identical* backbone + transfer schedule; only
   concat→FiLM changes. FiLM adds only the small per-block MLPs. Also the
   param-matched `mf_fno_transfer_2m` controls capacity for the transfer family.
4. **"Where's the closest existing benchmark of conditioning mechanisms?"** →
   No prior controlled benchmark isolates *conditioning mechanism* for MF neural
   operators; Zhu 2025 bundles multiple mechanisms per architecture and does not
   ablate them. Our concat-vs-FiLM (same everything else) is the controlled
   comparison the field lacks.

---

## Reference keys (arXiv) seen/verified this pass
- 1709.07871 — Perez et al. 2018, FiLM (original)
- 2304.06972 — Lyu et al. 2023, MF-FNO transfer (Phys. Fluids)
- 2308.09113 — MF-FNO for geological carbon storage (transfer, large-scale, few-shot HF)
- 2509.09599 — Shokar, Kerswell & Haynes 2025, FiLM-via-adaLN PDE-parameter conditioning (Transformer, time-stepping)
- 2511.09729 — Zhu, Raccuglia & Brenner 2025, "FiLMed FNO" equation-aware emulation (CLOSEST prior art)
- 2602.05187 — SpectraKAN, cross-attention-conditioned spectral operator (history-conditioned, time-stepping)
- Others surfaced (verify before citing): HyPINO (hypernetwork PINN), MRA-FNO (multi-res active learning), λ-FNO (sparse FNO + transfer across PDE variants), MFRNP, MF-DeepONet, Demo/Tezzele/Rozza 2023, a discretization-invariant MF operator paper — IDs among {2204.06684, 2302.12682, 2309.16971, 2402.18846, 2506.17582, 2507.07292, 2509.05117, 2511.20543, 2601.14745, 2603.11854}.
