# Recent Papers That Could Beat the MFFP Leaderboard

**A July 2026 literature scan for high-frequency and low-frequency PDE regimes**

*Prepared 2026-07-13 · mf_field / MFFP project · all sources verified against arXiv / ICML / OpenReview at scan time.*
*High-frequency claims passed a 3-vote adversarial verification, followed by a two-round Codex↔Claude adversarial pass (verdict: no material errors); one disputed claim was corrected against the source PDF — see §6.*

---

## 1. Executive summary

The anchor paper is real and stronger than expected.
**"Iterative Refinement Neural Operators are Learned Fixed-Point Solvers" (IRNO)** is arXiv:2605.24041, accepted to **ICML 2026 as a Spotlight** (poster #66317, presented 2026-07-07 in Seoul).
It freezes a pre-trained neural operator and learns a refinement module applied by fixed-point iteration — coarse initialization plus successive residual corrections — trained with a progressive spectral loss.
On its benchmarks it cuts high-frequency-band error to **1.5–2 % of the base operator's**, and the refinement module transfers across base operators without retraining.
That last property is exactly the hook MFFP needs: the "base operator" can be our LF pipeline or the frozen leaderboard winner, and IRNO becomes a bolt-on HF corrector.

Across both sweeps (26 verified papers), the recommendations split cleanly by regime:

| Priority | Regime | Proposal | Source paper(s) | Why it can beat the leaderboard |
|---|---|---|---|---|
| 1 | High-freq | `mf_fno_irno` — frozen-base iterative residual corrector + progressive spectral loss | IRNO (arXiv:2605.24041, ICML'26 Spotlight) | Only peer-reviewed mechanism with ~50× high-frequency-band error reduction; supersedes proposal P5 |
| 2 | Low-freq | `mf_fno_solve` — predict-then-solve: FNO warm-start + fixed CG budget on known-PDE datasets | NOWS (2511.02481) + NPO (2502.01337) + DL-HIM (2408.08540) | Final error bounded by solver iterations, not by 4–32 HF samples; breaks the data-scarcity ceiling entirely |
| 3 | High-freq | `mf_fno_flowdelta` — flow-matching residual δ = u_HF − u_LF, distilled to 1 step/level | MFFM (2605.16118) + FM operators (2512.12749) | Best NRMSE on 7/8 public benchmarks; concretizes proposal P7 at deterministic-inference cost |
| 4 | Low-freq | `mf_fno_fadapter` — frequency-banded adapters on a frozen LF-pretrained FNO | F-Adapter (2509.23173, NeurIPS'25) | Provably better than LoRA in Fourier layers; concentrates scarce-HF capacity on energy-dominant modes |
| 5 | Low-freq | `mf_fno_multistage` — stagewise residual networks with spectrum-informed rescaling | Wang & Lai (2307.08934, JCP'24) | The proven recipe for pushing past the 1e-2–1e-3 single-network accuracy plateau |
| 6 | Both | FIRE upgrades: post-hoc GP UQ source, quantile level-link, risk-routed block refiner | REEF-GP (2606.17513), MF-QR (2605.10406), ARC-STAR (2605.22222) | Three cheap deltas targeting the FIRE-vs-transfer gap (goal: 0.026 → ~0.015 median relL2 — our hypothesis, not a paper result) |

Two cross-cutting lessons from the verified literature:

1. **Frequency-blind fusion reintroduces LF bias.**
   FreqNO-DPS shows that fusing a biased surrogate isotropically re-imports its spectral bias; only frequency-calibrated weighting removes it.
   Every MFFP fusion family currently mixes LF and HF information isotropically across modes — a per-frequency-band trust weighting is a cheap, general upgrade.
2. **The residual δ = u_HF − u_LF is becoming the standard learning target.**
   Three independent 2025–26 lines (IRNO's corrections, MFFM's calibrated flow source, infinite-dimensional flow-matching operators) all learn the fidelity residual rather than the full field — converging on the contract FIRE already uses, and validating `HF = μ_LF + δ` as the right decomposition.

---

## 2. Where the leaderboard stands, and what "beating it" means

The 30-family zoo is currently led by three FNO families
(Elo over 15 datasets, per-sample relative-L2, shared backbone protocol):

| Rk | Family | Elo | med relL2 | Mechanism |
|----|--------|----:|----------:|-----------|
| 1 | `mf_fno_transfer_film` | 1820 | 0.0154 | LF-pretrain → HF fine-tune, FiLM conditioning |
| 2 | `mf_fno_pinn_transfer` | 1799 | 0.0122 | FiLM-transfer + exact Poisson PDE-residual loss |
| 3 | `fno_fire_distcond` | 1671 | 0.0264 | Residual FNO conditioned on LF-ensemble uncertainty fields |

These leaders were built for — and evaluated mostly on — **smooth, low-frequency-dominated fields**
(Poisson, heat, Darcy, advection–diffusion, potential flow).
The benchmark's two failure regimes are different problems that need different literature:

**Low-frequency regime (the current datasets).**
Spectral bias is *not* the bottleneck: an FNO's truncated low-mode parameterization matches the target's energy distribution.
The bottleneck is (a) HF scarcity — often 4–32 HF samples — and (b) an accuracy *floor*:
single-network training plateaus around 1e-2–1e-3 rel-L2, and more epochs do not push through it.
Beating the leaderboard here means going from ~1.2–1.5 % toward 0.1 % rel-L2, or matching current accuracy with less HF data and better OOD behavior.

**High-frequency regime (sharp fields: shocks, interfaces, turbulence-like spectra).**
Here spectral bias *is* the bottleneck: mode truncation and MSE-flavored losses systematically blur exactly the structures that carry the error.
Spectral bias is now a consensus, actively studied limitation of FNO-style surrogates — it is the shared motivating problem of at least three independent 2025–26 papers verified below.
The earlier `MF_Sharp_HighFreq_Report` (2026-07-02) diagnosed three walls
(12-mode spectral wall, additive-residual misalignment dipole, rel-L2 blur preference)
and proposed families P1–P9.
This report updates that picture with the newest literature and asks which mechanisms supersede or strengthen P1–P9.

---

## 3. Part 1 — High-frequency regime: iterative refinement, spectral-bias mitigation, generative residual transport

Every claim in this part survived 3-vote adversarial verification against primary sources (arXiv full text, ICML virtual site); votes were unanimous.

### 3.1 The anchor paper: IRNO

**[HF-1] Iterative Refinement Neural Operators are Learned Fixed-Point Solvers: A Principled Approach to Spectral Bias Mitigation** —
Liu, Shang, Wang, Ren & Yang, **ICML 2026 Spotlight**, [arXiv:2605.24041](https://arxiv.org/abs/2605.24041)
(ICML poster #66317, Poster Session 1, 2026-07-07, COEX Seoul; 47 pages).

**Mechanism.**
IRNO augments a *frozen* pre-trained neural operator with a learned refinement module applied via fixed-point iteration:

> h₀ = T_base(x);  h_{k+1} = h_k + α · Φ_θ(x, h_k)

The prediction decomposes into a coarse initialization plus successive residual corrections.
Training uses a **progressive spectral loss** that adaptively increases the penalty on high-frequency components over refinement steps — early iterates are only asked to get the low frequencies right; later iterates are pushed onto the fine structure.
Only the refinement parameters are trained (Algorithm 1); the base operator stays frozen throughout.

**Verified results (author-reported, peer-reviewed).**
Up to 56.05 % error reduction on turbulent flow.
On Active Matter, error relative to the base operator drops to 27.7–36.1 % in the low-frequency band, 5.1–6.7 % mid-band, and **1.48–2.04 % in the high-frequency band** — i.e., the mechanism attacks precisely the band where MFFP's sharp-field families fail.
Iteration is stable beyond the trained iteration count, and — critically — **Section 4.5 shows the refinement module transfers across different base operators without retraining**: the initialization source is decoupled from the corrector.

**MFFP adaptation (flagship, high-freq).**
The MF reading is immediate: LF prediction (or interpolated LF field, or the frozen `mf_fno_transfer_film` output) = coarse initialization; the refinement FNO = learned HF corrector conditioned on the input and current iterate.
Weight-tied iteration means the corrector's parameter count stays small (one module, applied K times), which suits HF scarcity better than K independent stages.
The progressive spectral loss is separately transferable to *any* existing residual family today.
See proposal N1 in §5.

### 3.2 Spectral-bias mitigation for fusion models

**[HF-2] FreqNO-DPS: frequency-calibrated diffusion guidance for surrogate–observation fusion** —
Perrone, Lehmann, Fresca & Gatti, arXiv June 2026, [arXiv:2606.03936](https://arxiv.org/abs/2606.03936) (code: github.com/niccoloperrone/FreqNO-DPS).
Fuses a frozen neural-operator surrogate with sparse observations inside diffusion posterior sampling:
a closed-form, **spectrally shaped guidance score weights the surrogate by its frequency-dependent accuracy** (two FFTs per reverse step, no backprop through the denoiser).
The verified headline (medium confidence — one-month-old preprint, single benchmark family):
on 3D elastic wavefields, high-frequency spectral bias falls to +0.002 (rFFT_high, 5 % sensor coverage) versus −0.210 for isotropic guidance and −0.239 for the surrogate alone.
**Key insight for MFFP:** naive/isotropic integration of a biased surrogate *reintroduces its spectral bias* — it is the frequency-dependent calibration, not fusion per se, that removes it.
**Adaptation:** the diffusion prior needs abundant HF samples, which fights our premise; the transferable piece is the **per-frequency-band trust weighting** applied to LF information inside any deterministic fusion family (see N7).

**[HF-3] HFS: High-Frequency Scaling inside convolutional operators** —
Khodakarami, Oommen, Bora & Karniadakis, [arXiv:2503.13695](https://arxiv.org/abs/2503.13695)
(listed in *Neural Networks* on ScienceDirect, PII S0893608025009074; the arXiv page itself carries no journal-ref field).
Rescales low- and high-frequency latent components separately inside convolutional (UNet-variant) neural operators — a patch-mean vs patch-residual decomposition with learnable scale factors λ_DC, λ_HFC — mitigating spectral bias with no FFT cost.
Author-reported results, checked directly against the PDF: HFS-enhanced operators cut relative errors by 23.5 % and energy-spectrum errors by 15.2 % on average, and reduce 2D-Kolmogorov relative error from 5.3 % to 4.7 %.
**Attribution caveat (§6):** the oft-quoted 21 %/42 % boiling RMSE reductions are attributed *in the paper* to baseline architecture/training upgrades (residual blocks, better optimizer and normalization), not to HFS itself — do not cite them as HFS gains.
**Adaptation:** a cheap bolt-on for the zoo's convolutional members and for FNO lifting/projection layers; directly relevant to the U-Net/ConvNeXt datasets where sharp fields dominate.

### 3.3 Generative LF→HF residual transport

**[HF-4] MFFM: multi-fidelity cascaded flow matching on the fidelity residual** —
Chen, Liu, Tang & Li, arXiv May 2026, [arXiv:2605.16118](https://arxiv.org/abs/2605.16118).
Learns **δ = u_HF − u_LF directly** as a conditional flow:
the flow-matching source distribution is calibrated to the empirical LF→HF residual scale (with local Gaussian-blur correlation), and the velocity network is conditioned on u_LF.
After level-wise pretraining, the cascade is fine-tuned end-to-end with a **deterministic one-step rollout**, so inference costs exactly one network evaluation per cascade level — the NFE ablation confirms best-or-tied NRMSE at NFE/level = 1.
Verified results (medium confidence, preprint): **best NRMSE on 7 of 8 benchmarks** (Darcy & Burgers super-resolution, PDEBench Shallow-Water & Diffusion-Reaction, The Well's Shear-T/Shear-P/Active-Matter, FNO Navier–Stokes), losing only Darcy to F-FNO.
**Adaptation:** the most direct blueprint in this survey for a new family — a generative-then-distilled residual corrector matched to our LF-abundant/HF-scarce regime with cheap deterministic inference (see N2).

**[HF-5] Flow-matching operators in function space** —
Bhola & Duraisamy, arXiv Dec 2025, [arXiv:2512.12749](https://arxiv.org/abs/2512.12749).
Formulates flow matching in infinite-dimensional function space to learn a **probabilistic transport from LF approximations to the HF solution manifold via learned residual corrections**, using a FiLM-conditioned FNO vector field, resolution-invariant inference, and uncertainty estimates under scarce HF data.
This is the same `HF = μ_LF + δ` contract as FIRE, but with a generative δ that yields samples — hence UQ — instead of a point residual.
**Adaptation:** keep `fire_core`'s LF summary conditioning, replace the deterministic residual FNO with a conditional flow-matching δ; together with MFFM this defines the FIRE-generative hybrid (N2).

### 3.4 Cross-regime: uncertainty-aware residual learning (FIRE-relevant)

**[U-1] REEF-GP: post-hoc GP on a frozen operator's residuals** —
Vendrell-Gallart, Negarandeh & Bostanabad, arXiv June 2026, [arXiv:2606.17513](https://arxiv.org/abs/2606.17513).
Fits a Gaussian process to the residuals of a frozen neural operator **using the operator's own internal embeddings as the GP kernel feature space** (no separately learned feature map), yielding geometry-aware calibrated uncertainties competitive with deep ensembles at a fraction of the cost (medium confidence — young preprint; mechanism itself unambiguous).
**Adaptation:** a training-free **tenth FIRE uncertainty source** — post-hoc GP on the LF-FNO's embeddings — far cheaper than the snapshot/SWAG/batch-ensemble sources; note its residual is model error, not the LF→HF gap, so the summary fields need re-deriving.

**[U-2] Multi-fidelity quantile regression via a local quantile link** —
Liu & Zhang, arXiv May 2026 (v2 June 2026), [arXiv:2605.10406](https://arxiv.org/abs/2605.10406).
Represents the HF quantile at each covariate as an **LF quantile evaluated at a covariate-dependent level**, reducing HF quantile estimation to estimating a *level function* that is smoother — hence learnable from scarce HF data — when LF and HF conditional distributions share shape, with convergence theory and a correction step for when the assumption weakens.
**Adaptation:** near-drop-in upgrade for `fno_fire_quantile` / `fno_fire_iqn` / `fno_fire_cqr`: they already produce per-pixel q10/q50/q90 LF fields; learn the level-link instead of regressing HF quantiles from scratch.

**Cross-validation note.**
The correlation-based MF-emulator benchmark ([LF-13] below, arXiv:2512.02868) was independently surfaced by *both* sweeps.
The high-frequency sweep adds: it explicitly varies backbone spectral bias (MLP vs SIREN vs KAN) and finds complementary spectral strengths — KAN best across frequencies with limited data, MLP best at low frequencies, SIREN best on high-frequency oscillatory content.
Caveat: it studies pointwise emulation, not field prediction, so it informs backbone/encoding choices rather than providing a drop-in family.

---

## 4. Part 2 — Low-frequency regime: breaking the HF-scarcity and accuracy floor

All 18 papers below were existence-verified against their arXiv abstract pages (or the arXiv API) during the scan.
Venue claims sourced only from arXiv comments (rather than fetched proceedings pages) are flagged where relevant.

### 4.1 High-precision / machine-accuracy training

**[LF-1] Multi-stage Neural Networks: Function Approximator of Machine Precision** —
Wang & Lai, *J. Comput. Phys.* 504:112865 (2024), [arXiv:2307.08934](https://arxiv.org/abs/2307.08934).
Trains a *sequence* of networks, each fitting the rescaled residue of the combined previous stages, with the residue's dominant frequency setting the next stage's input scaling.
Residues decay by an inverse power law across stages, pushing regression and PINN error from the usual O(1e-5) plateau toward machine precision.
The follow-up *Spectrum-Informed Multistage Neural Networks* ([arXiv:2407.17213](https://arxiv.org/abs/2407.17213), ICML 2024 AI4Science workshop) initializes each stage from the residue's FFT.
**MFFP adaptation:** stage 0 = `mf_fno_transfer_film` as-is; stages 1..K = small, strongly regularized residual FNOs (few modes, weight decay) trained on the normalized HF residual of the stack.
This is the most direct attack on the "last 10×" for smooth fields; 2–3 cheap stages fit the 30-min smoke budget.
Main risk: each stage still sees only the scarce HF samples, so per-stage capacity must stay tiny.

**[LF-2] Spectral-Refiner: Accurate Fine-Tuning of Spatiotemporal FNO** —
Cao, Brarda, Li & Xi, ICLR 2025, [arXiv:2405.17211](https://arxiv.org/abs/2405.17211) (OpenReview `MKP1g8wU0P`).
After a few end-to-end epochs, fine-tunes *only* one untruncated spectral convolution layer using a negative-Sobolev (H⁻¹) a-posteriori error estimator evaluated exactly in Fourier space via Parseval.
**MFFP adaptation:** on the known-PDE datasets (`poisson_generated`, `poisson_local`), replace `mf_fno_pinn_transfer`'s pointwise strong-form residual loss with the dual-norm estimator and fine-tune only the last spectral layer on HF.
A small delta on an existing winning family.

**[LF-3] Hybrid iterative neural solver with spectral analysis (DL-HIM / HINTS line)** —
Cui, Jiang, Liu & Shu, *J. Comput. Phys.* (2025), [arXiv:2408.08540](https://arxiv.org/abs/2408.08540).
Analyzes hybrid iterations that alternate cheap relaxation sweeps (kill high-frequency error) with a neural operator (kill low-frequency error), deriving conditions for grid- and parameter-independent convergence.
**MFFP adaptation:** wrap the MF-FNO prediction as initial iterate + low-frequency corrector inside a few differentiable Jacobi/CG sweeps on known-operator datasets.
Convergence becomes iteration-bound rather than data-bound — exactly the right trade when HF data is the scarce resource.

### 4.2 Data-efficient fine-tuning, transfer, and foundation-model recipes

**[LF-4] F-Adapter: Frequency-Adaptive Parameter-Efficient Fine-Tuning** —
Zhang, Kang, Wang & Zou, NeurIPS 2025, [arXiv:2509.23173](https://arxiv.org/abs/2509.23173).
First systematic PEFT study for pretrained operator models: proves stacked LoRA suffers a depth-amplified approximation-error lower bound inside Fourier layers, while bottleneck adapters retain universal approximation.
Allocates adapter width by spectral energy — wide on low modes, narrow on high.
**MFFP adaptation:** freeze the LF-pretrained FNO; insert frequency-banded adapters with capacity ∝ per-band LF energy; tune only adapters (+FiLM) on the 4–32 HF pairs.
Lowest-risk upgrade to `mf_fno_transfer_film`: fewer trainable parameters directly cut HF overfitting.

**[LF-5] Physics-informed fine-tuning of PDE foundation models** —
Medvedev, Armbruster, Straub, Kruse & Rosskopf, ICLR 2026 Workshop on AI and PDEs, [arXiv:2603.15431](https://arxiv.org/abs/2603.15431).
Shows a *hybrid* data + physics fine-tuning objective (PDE residual + boundary terms on unlabeled collocation inputs) gives the best OOD generalization when labels are minimal.
**MFFP adaptation:** external validation of `mf_fno_pinn_transfer`, plus two concrete upgrades: add a boundary-condition penalty, and add physics-only batches on unlabeled (incl. OOD) inputs beyond the HF training set.

**[LF-6] Poseidon: Efficient Foundation Models for PDEs** —
Herde et al., NeurIPS 2024 (confirmed via the NeurIPS virtual site), [arXiv:2405.19101](https://arxiv.org/abs/2405.19101) (OpenReview `JC1VKK3UXk`).
Multiscale operator transformer pretrained with an "all2all" pairing strategy exploiting the semigroup property; matches FNO-trained-on-1024-samples with tens of samples downstream.
**MFFP adaptation (in-spirit, no weight downloads):** treat the abundant LF corpus as the pretraining distribution, use all2all-style pair augmentation on LF trajectories, then few-shot HF fine-tuning with fidelity-conditioned layer norms.

**[LF-7] DPOT: Auto-Regressive Denoising Operator Transformer** —
Hao et al., ICML 2024, [arXiv:2403.03542](https://arxiv.org/abs/2403.03542).
Denoising pretraining — Gaussian noise injected into inputs — stabilizes rollout and improves downstream transfer for a 0.5B-param Fourier-attention transformer.
**MFFP adaptation:** the transferable idea is *denoising LF pretraining* for the existing FNO: LF fields are effectively noisy/biased HF fields, so noise-injected pretraining should absorb the LF→HF discrepancy better.
Nearly free to add to the transfer family.

**[LF-8] VICON: Vision In-Context Operator Networks** —
Cao, Liu, Yang, Yu, Schaeffer & Osher, TMLR (2025/26; venue via arXiv comment), [arXiv:2411.16063](https://arxiv.org/abs/2411.16063).
Makes in-context operator learning practical in 2D via ViT-patch tokens: k (input, output) demonstration pairs in the prompt, no weight updates at test time.
**MFFP adaptation:** frame LF→HF as in-context regression — prompt = the few (LF, HF) training pairs, query = test LF field — with pair-tasks manufactured from LF-only data (coarse→fine at two resolutions).
Uniquely matched to "few HF pairs define the task", but transformer training makes the 30-min smoke budget the main risk.

**[LF-9] MOFS: Multi-Operator Few-Shot Learning** —
Li & Zhe, arXiv Aug 2025 (no venue), [arXiv:2508.01211](https://arxiv.org/abs/2508.01211).
Few-shot generalization to unseen operators via self-supervised FNO-encoder pretraining (masked-field reconstruction + spectrum prediction), operator embeddings, and memory-augmented prompting.
**MFFP adaptation:** the cheap transplant is the self-supervised LF pretraining tasks — masked-patch reconstruction and radial-spectrum prediction on abundant LF fields — extracting strictly more supervision from the same LF data before HF fine-tuning.

### 4.3 Multi-fidelity fusion mechanisms for smooth problems

**[LF-10] Multi-Level Monte Carlo Training of Neural Operators** —
Rowbottom, Fresca, Liò, Schönlieb & Boullé, accepted CMAME (per arXiv comment), [arXiv:2505.12940](https://arxiv.org/abs/2505.12940).
Estimates the training gradient as a telescoping sum over a resolution hierarchy: many cheap coarse-resolution gradient samples plus few fine-resolution gradient *corrections* — a control-variate estimator of the fine-level gradient.
**MFFP adaptation:** a principled single-loop replacement for pretrain→fine-tune: per batch, gradient = LF-loss gradient (many pairs) + correction gradient from the few paired HF samples.
Directly implementable with `resolve_grid` handling level→grid mapping.

**[LF-11] Data-efficient multi-fidelity DeepONet with physics-guided subsampling** —
Yang, Lee & Kang, arXiv Mar 2025, [arXiv:2503.17941](https://arxiv.org/abs/2503.17941).
Freezes the LF-pretrained branch/trunk and trains only a small nonlinear merge head on HF (−50 % error, −96 % training time); physics-guided subsampling picks the most dynamically informative HF points (−40 % HF need).
**MFFP adaptation:** freeze the LF-pretrained FNO trunk and train only a tiny fusion head — an even lower-variance HF adaptation than FiLM; weight HF pixels by LF-residual magnitude during fine-tuning.

**[LF-12] FilDeep: fidelity-based learning for elastic-plastic deformation fields** —
Tang et al., KDD 2026 (per arXiv comment), [arXiv:2601.10031](https://arxiv.org/abs/2601.10031).
Joint (not sequential) LF+HF training with fidelity-aware attention, positioned explicitly against pretrain-then-finetune.
**MFFP adaptation:** one FNO trained simultaneously on LF and HF with a fidelity gate and a loss schedule annealing LF→HF-dominated — removes the catastrophic-forgetting failure mode of two-phase transfer.

**[LF-13] Correlation-based multi-fidelity neural emulators: a systematic assessment** —
Villatoro, Geraci & Schiavazzi, arXiv Dec 2025, [arXiv:2512.02868](https://arxiv.org/abs/2512.02868).
Benchmarks correlation-based MF emulators across dimensionality, oscillatory character, discontinuities, and *corrupted* LF sources, while explicitly varying backbone spectral bias (MLP vs SIREN vs KAN; complementary strengths — see §3.4 cross-validation note).
**MFFP relevance:** design guidance rather than a new mechanism — quantifies when correlation-based fusion (the FIRE/residual families) fails as HF shrinks or LF is biased, and motivates multi-source LF conditioning (LF at several resolutions) over a single LF mean.
Caveat: pointwise emulation, not field prediction; its "coordinate encoding" aligns LF/HF parameterizations, not Fourier-feature positional encoding.

### 4.4 Physics-constrained correction beyond soft residual losses

**[LF-14] NOWS: Neural Operator Warm Starts for iterative solvers** —
Eshaghi, Anitescu, Valizadeh, Wang, Zhuang & Rabczuk, arXiv Nov 2025, [arXiv:2511.02481](https://arxiv.org/abs/2511.02481).
Uses the neural prediction as the initial guess for Krylov solvers (CG/GMRES) on the discretized system; numerics contract the remaining error with guarantees, ending at solver accuracy regardless of surrogate quality.
**MFFP adaptation:** "predict-then-solve" family for known-PDE datasets: MF-FNO output → assemble the coefficient-weighted 5-point operator from `data_adapters.geometry` → fixed small CG budget at eval.
Even 20–50 sparse CG steps from a 1.5 %-error start could cut rel-L2 by an order of magnitude, with all-local compute.

**[LF-15] ANCHOR: error-controlled adaptive numerical correction for NO time marching** —
Roy, Nayak & Goswami, arXiv Dec 2025, [arXiv:2512.19643](https://arxiv.org/abs/2512.19643).
An EMA of the normalized PDE residual acts as a label-free, per-instance error estimator during neural-operator rollout; threshold crossings trigger classical corrective solver steps.
**MFFP adaptation:** for time-dependent smooth datasets (heat, advection–diffusion), residual-EMA-triggered coarse-solver correction at eval; the residual estimator doubles as an uncertainty signal.

**[LF-16] NPO: Neural Preconditioning Operator** —
Li, Xiao, Lai & Wang, arXiv Feb 2025, [arXiv:2502.01337](https://arxiv.org/abs/2502.01337).
Learns a multigrid-flavored preconditioner for Krylov methods with condition-number and residual losses; generalizes to 4096² grids far beyond training size.
**MFFP adaptation:** complementary to NOWS — warm-start from the MF-FNO *and* precondition CG with a small operator trained on abundant LF discretizations.
Degrades gracefully to plain transfer on unknown-PDE datasets, mirroring how `mf_fno_pinn_transfer` special-cases Poisson.

### 4.5 OOD and test-time robustness

**[LF-17] Test-time generalization through neural operator splitting (DISCO dictionary)** —
Serrano, Han, Oyallon, Ho & Morel, arXiv Jan 2026, [arXiv:2602.00884](https://arxiv.org/abs/2602.00884).
Zero-shot OOD via test-time beam search composing a dictionary of pretrained operators through operator splitting, adapting search effort to distribution shift.
**MFFP adaptation:** train a small dictionary of correction operators (per dataset cluster, from LF data) and select/compose at eval by minimizing LF-consistency or PDE residual on the test input — no HF labels needed.

**[LF-18] ARC-STAR: auditable post-hoc correction for PDE foundation models** —
Li et al., arXiv May 2026, [arXiv:2605.22222](https://arxiv.org/abs/2605.22222).
Frozen-host, three-stage correction: global corrector → blockwise local refiner → deployment-time label-free risk score routing refinement compute to high-risk blocks under a budget.
**MFFP adaptation:** maps directly onto FIRE — keep the LF model frozen, keep the global residual FNO, add a lightweight blockwise refiner, and use FIRE's σ/quantile fields as the risk score deciding *where* second-stage capacity is spent.
A plausible route to close the FIRE-vs-transfer gap (0.026 → ~0.015 median).

### 4.6 Low-frequency shortlist

Ranked by expected chance of beating `mf_fno_transfer_film` / `mf_fno_pinn_transfer` at 1.2–1.5 % rel-L2 on smooth fields:

1. **Predict-then-solve** ([LF-14] NOWS + [LF-16] NPO): the only mechanism whose final error is bounded by numerics, not by 4–32 HF samples.
2. **Multi-stage residual stacking** ([LF-1]): the proven recipe for pushing past the 1e-2–1e-3 plateau; smooth residues are its easiest case.
3. **F-Adapter** ([LF-4]): frequency-adaptive adapters concentrate scarce-HF capacity on the energy-dominant low modes; provably beats LoRA in Fourier layers.
4. **Spectral-Refiner** ([LF-2]): exact H⁻¹ a-posteriori loss + last-spectral-layer fine-tuning; natural upgrade of the pointwise PINN loss.
5. **MLMC training** ([LF-10]): principled control-variate formulation of exactly our LF-abundant/HF-scarce regime.

---

## 5. Part 3 — Proposed new model families

Each proposal names a candidate `models/<family>/` implementation, its regime, and its relation to the existing zoo and the P1–P9 proposals from `MF_Sharp_HighFreq_Report` (2026-07-02).
All fit the model contract (LF+HF in, HF field out, checkpoint-resume, ≤30-min smoke on one H100) unless noted.

### N1. `mf_fno_irno` — frozen-base iterative refinement corrector 🔴 high-freq flagship

From [HF-1].
Freeze the best available base (start with interpolated LF; then try the trained `mf_fno_transfer_film` checkpoint as base).
Train one small refinement FNO Φ_θ(x, h_k, LF-features) applied K≈4–8 times with step size α, under the progressive spectral loss (ramp the high-frequency penalty with k).
**vs existing zoo:** `fno_mf_stack` (#17) stacks *independent* residual blocks with a plain loss; IRNO's weight-tied fixed-point iteration + frequency-progressive objective is the principled version, with spotlight-verified ~50× high-band error reduction and iterate-count extrapolation.
**vs P-proposals:** supersedes **P5** (SpecB residual stage) and strengthens **P9** (FAS multigrid — IRNO is the single-grid learned analog).
Cheapest de-risking step: add the progressive spectral loss alone to `fno_mf_stack` before building the full family.

### N2. `mf_fno_flowdelta` — flow-matching fidelity residual, distilled to one step 🔴 high-freq

From [HF-4] + [HF-5].
Learn δ = u_HF − u_LF as a conditional flow: source distribution calibrated to the empirical LF→HF residual scale, velocity FNO FiLM-conditioned on u_LF (and optionally on FIRE's [μ, σ, q] summary fields — the FIRE-generative hybrid).
Fine-tune end-to-end with deterministic one-step rollout so eval cost is one network evaluation per level.
**vs existing zoo:** upgrades the FIRE contract from point-δ to distributional-δ with sampling-based UQ.
**vs P-proposals:** concretizes **P7** (generative refiner) — MFFM's one-step distillation removes P7's main objection (inference cost / smoke budget).

### N3. `mf_fno_solve` — predict-then-solve with Krylov refinement 🔵 low-freq flagship

From [LF-14] + [LF-16] + [LF-3].
On known-PDE datasets (Poisson variants, heat, Darcy): MF-FNO prediction → assemble the discrete operator via `data_adapters.geometry` → fixed CG budget (optionally NPO-preconditioned, preconditioner trained on abundant LF discretizations) at eval.
Elsewhere: degrade gracefully to plain transfer, exactly as `mf_fno_pinn_transfer` already special-cases Poisson.
**Why flagship:** the only proposal whose final error is bounded by solver iterations rather than HF sample count; plausibly reaches discretization accuracy (≪0.1 % rel-L2) where the PDE is known.
**vs P-proposals:** orthogonal to all of P1–P9; pairs with N1 (IRNO handles unknown-PDE datasets, N3 handles known-PDE ones).

### N4. `mf_fno_multistage` — stagewise residual networks 🔵 low-freq

From [LF-1].
Stage 0 = FiLM-transfer as-is; stages 1..K = tiny residual FNOs on the rescaled HF residue, spectrum-informed initialization per stage.
**vs existing zoo:** differs from `fno_mf_stack` by residue *rescaling* (each stage sees an O(1) target) and per-stage frequency adaptation — the two ingredients the JCP paper shows are what break the plateau.
**vs P-proposals:** complements P4 (band-split); the stagewise frequency schedule is a soft, data-driven version of P4's hard band assignment.

### N5. `mf_fno_fadapter` — frequency-banded adapter fine-tuning 🔵 low-freq

From [LF-4], with [LF-2]'s H⁻¹ loss and [LF-5]'s hybrid physics objective as optional additions.
Freeze the LF-pretrained FNO; insert bottleneck adapters into each spectral layer with width proportional to per-band LF spectral energy; tune adapters + FiLM only.
**vs existing zoo:** strictly fewer trainable parameters than `mf_fno_transfer_film`'s full fine-tune — the direct treatment for HF overfitting at 4–32 samples.

### N6. FIRE upgrades — `fno_fire_reefgp`, `fno_fire_qlink`, `fno_fire_blockrefine` 🟣 both regimes

From [U-1], [U-2], [LF-18].
Three independent deltas on the shared `fire_core`/`fire_methods` infrastructure:
(a) **reefgp** — tenth uncertainty source: post-hoc GP on LF-FNO embeddings, no extra training runs;
(b) **qlink** — replace direct HF-quantile regression with the smoother LF→HF quantile level-link function;
(c) **blockrefine** — ARC-STAR-style second-stage blockwise refiner routed by FIRE's own σ/quantile fields as a label-free risk score.
Goal: close the FIRE-vs-transfer gap (median 0.026 → ~0.015) while keeping FIRE's UQ advantage.

### N7. Training-recipe deltas (not new families)

Cheap, compounding modifications to existing winners, in rough order of expected value per effort:

1. **Progressive spectral loss** ([HF-1]) on any residual family — the ramp schedule alone is a one-liner.
2. **Per-frequency-band LF trust weighting** ([HF-2]'s key insight) inside fusion: weight LF-derived features by their per-band accuracy measured on the HF training pairs.
3. **Hybrid physics fine-tuning with unlabeled collocation batches + BC penalty** ([LF-5]) for `mf_fno_pinn_transfer`.
4. **MLMC telescoped gradients** ([LF-10]) replacing the two-phase transfer schedule.
5. **Denoising LF pretraining** ([LF-7]) and **self-supervised LF tasks** (masked reconstruction + spectrum prediction, [LF-9]).
6. **Joint fidelity-annealed training** ([LF-12]) as an ablation against pretrain→fine-tune.

### Suggested build order

1. **N7.1 + N7.2** (days): loss/weighting deltas on existing families — immediate signal on whether spectral scheduling helps our datasets.
2. **N1 `mf_fno_irno`** (the high-freq bet) and **N3 `mf_fno_solve`** (the low-freq bet) in parallel — they attack disjoint dataset subsets.
3. **N5 `mf_fno_fadapter`** — lowest-risk new family; a likely new #1 on smooth datasets even if the gain is modest.
4. **N2 `mf_fno_flowdelta`** — highest ceiling, highest implementation risk; build after N1 confirms the residual-corrector plumbing.
5. **N6 FIRE upgrades** — parallelizable onto the existing `_common` infrastructure at any point.

---

## 6. Verification notes and methodology

**How the paper count was chosen.**
The 26 papers were not a quota; the count is the output of two filters.
The high-frequency sweep ran a fixed harness shape — 5 search angles in parallel, URL dedup, top-~15 source fetch, falsifiable-claim extraction, 3-vote adversarial verification — and its 8 papers are simply what survived relevance filtering plus verification.
The low-frequency sweep was given a soft target of 10–15, set by three constraints: coverage (~2–3 papers per each of its 5 mechanism angles), verification cost (every candidate needed a primary-source existence check, with unverifiable ones dropped rather than listed), and deliverable format (each entry carries a per-paper adaptation assessment, which stops being useful as a bare bibliography past ~20 entries); 18 cleared the bar and all were kept.
One paper ([LF-13]) surfaced independently in both sweeps and was merged.
**Scope caveat:** this is one pass per regime, not a loop-until-dry exhaustive review — coverage is a ranked shortlist of actionable mechanisms, not a systematic survey.
Before committing to a large build (N1/N3), an escalation path is additional search rounds seeded with the citation graphs of these 26 papers, iterated until two consecutive rounds surface nothing new.

**High-frequency sweep (deep-research workflow).**
Five parallel search angles → source fetch → falsifiable-claim extraction → 3-vote adversarial verification per claim (a claim dies on ≥2/3 refute votes) → synthesis; 102 agents in total.
Every surviving claim was verified 3–0 against primary sources (arXiv abstracts + full text, ICML 2026 virtual site, GitHub repos).
**A disputed claim, resolved by direct PDF check:** the 3-vote panel refuted (0–3) a bundled claim attributing ≈21 %/42 % boiling RMSE reductions plus a 23.5 % average to HFS.
A subsequent primary-source pass (Codex round plus our own PDF text extraction) resolved the dispute: the 23.5 % average relative-error reduction is a genuine HFS result, while the 21 %/42 % figures are attributed by the paper to baseline architecture/training upgrades, not to HFS.
Section 3.2 carries the corrected attribution.
An apparent ICML date conflict for the anchor paper (Jul 6 PDT vs Jul 7) resolves to the same instant in Seoul local time.

**Low-frequency sweep (single research agent).**
Every listed paper was existence-verified by fetching its arXiv abstract page or the arXiv API; unverifiable candidates were dropped rather than listed.
Venue claims for VICON (TMLR), MLMC (CMAME), and FilDeep (KDD 2026) rest on arXiv comments; Poseidon (NeurIPS 2024) and Spectral-Refiner (ICLR 2025) were subsequently confirmed against the conference virtual sites.
OpenReview IDs quoted in this report could not be re-fetched directly (browser-verification wall) and rest on the original sweep.
These entries did **not** receive the 3-vote adversarial treatment; author-reported numbers quoted in Part 2 should be read as claims, not replicated results.

**Codex↔Claude adversarial round (2026-07-13).**
An independent Codex fact-check re-fetched all 26 arXiv IDs (all resolved; titles and authors match), re-verified the IRNO / MFFM / FreqNO-DPS quantitative claims against the PDFs, and returned **no material errors**.
Its five minor flags — HFS venue sourcing, HFS number attribution, Poseidon venue sourcing, unverifiable OpenReview IDs, and hypothesis-phrasing in the executive summary — are fixed in this version.

**Confidence conventions.**
"High confidence" = peer-reviewed venue or multiple independent primary sources; "medium" = recent preprint, self-reported numbers, no independent replication.
All quantitative results in this report are author-reported on the papers' own benchmarks, not on MFFP's 17 datasets — the proposals in §5 are hypotheses to be tested under `eval/score.py`, not established wins.

---

## 7. References

Bibtex-style keys follow the repo convention for `papers_summary.csv` merging (append rows for keys not yet present).

| Key | Paper | Venue | Link |
|---|---|---|---|
| `liu2026irno` | Iterative Refinement Neural Operators are Learned Fixed-Point Solvers | ICML 2026 (Spotlight) | [arXiv:2605.24041](https://arxiv.org/abs/2605.24041) |
| `perrone2026freqnodps` | FreqNO-DPS: frequency-calibrated diffusion posterior sampling for NO fusion | preprint | [arXiv:2606.03936](https://arxiv.org/abs/2606.03936) |
| `khodakarami2025hfs` | High-Frequency Scaling for spectral-bias mitigation in convolutional NOs | Neural Networks (per ScienceDirect) | [arXiv:2503.13695](https://arxiv.org/abs/2503.13695) |
| `chen2026mffm` | MFFM: multi-fidelity cascaded flow matching | preprint | [arXiv:2605.16118](https://arxiv.org/abs/2605.16118) |
| `bhola2025fmoperator` | Flow-matching operators in function space | preprint | [arXiv:2512.12749](https://arxiv.org/abs/2512.12749) |
| `vendrell2026reefgp` | REEF-GP: post-hoc GP UQ from frozen-operator embeddings | preprint | [arXiv:2606.17513](https://arxiv.org/abs/2606.17513) |
| `liu2026mfquantile` | Multi-fidelity quantile regression via local quantile link | preprint | [arXiv:2605.10406](https://arxiv.org/abs/2605.10406) |
| `wang2024multistage` | Multi-stage neural networks: function approximator of machine precision | J. Comput. Phys. | [arXiv:2307.08934](https://arxiv.org/abs/2307.08934) |
| `ng2024siminn` | Spectrum-informed multistage neural networks | ICML'24 AI4Science WS | [arXiv:2407.17213](https://arxiv.org/abs/2407.17213) |
| `cao2025spectralrefiner` | Spectral-Refiner: fine-tuning spatiotemporal FNO | ICLR 2025 | [arXiv:2405.17211](https://arxiv.org/abs/2405.17211) |
| `cui2025dlhim` | Hybrid iterative neural solver based on spectral analysis | J. Comput. Phys. | [arXiv:2408.08540](https://arxiv.org/abs/2408.08540) |
| `zhang2025fadapter` | F-Adapter: frequency-adaptive PEFT for scientific ML | NeurIPS 2025 | [arXiv:2509.23173](https://arxiv.org/abs/2509.23173) |
| `medvedev2026pift` | Physics-informed fine-tuning of PDE foundation models | ICLR'26 WS AI+PDEs | [arXiv:2603.15431](https://arxiv.org/abs/2603.15431) |
| `herde2024poseidon` | Poseidon: efficient foundation models for PDEs | NeurIPS 2024 | [arXiv:2405.19101](https://arxiv.org/abs/2405.19101) |
| `hao2024dpot` | DPOT: auto-regressive denoising operator transformer | ICML 2024 | [arXiv:2403.03542](https://arxiv.org/abs/2403.03542) |
| `cao2024vicon` | VICON: vision in-context operator networks | TMLR | [arXiv:2411.16063](https://arxiv.org/abs/2411.16063) |
| `li2025mofs` | MOFS: multi-operator few-shot learning | preprint | [arXiv:2508.01211](https://arxiv.org/abs/2508.01211) |
| `rowbottom2025mlmc` | Multi-level Monte Carlo training of neural operators | CMAME (accepted) | [arXiv:2505.12940](https://arxiv.org/abs/2505.12940) |
| `yang2025mfdeeponet` | Data-efficient MF DeepONet with physics-guided subsampling | preprint | [arXiv:2503.17941](https://arxiv.org/abs/2503.17941) |
| `tang2026fildeep` | FilDeep: fidelity-based learning for large-deformation fields | KDD 2026 | [arXiv:2601.10031](https://arxiv.org/abs/2601.10031) |
| `villatoro2025mfcorr` | Assessing correlation-based multi-fidelity neural emulators | preprint | [arXiv:2512.02868](https://arxiv.org/abs/2512.02868) |
| `eshaghi2025nows` | NOWS: neural operator warm starts for iterative solvers | preprint | [arXiv:2511.02481](https://arxiv.org/abs/2511.02481) |
| `roy2025anchor` | ANCHOR: error-controlled adaptive numerical correction | preprint | [arXiv:2512.19643](https://arxiv.org/abs/2512.19643) |
| `li2025npo` | NPO: neural preconditioning operator | preprint | [arXiv:2502.01337](https://arxiv.org/abs/2502.01337) |
| `serrano2026disco` | Test-time generalization through neural operator splitting | preprint | [arXiv:2602.00884](https://arxiv.org/abs/2602.00884) |
| `li2026arcstar` | ARC-STAR: auditable post-hoc correction for PDE foundation models | preprint | [arXiv:2605.22222](https://arxiv.org/abs/2605.22222) |
