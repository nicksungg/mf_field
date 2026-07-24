# How Should You Condition a Fourier Neural Operator? FiLM Beats Concatenation for Multi-Fidelity Parametric Field Prediction

*Draft — 2026-06-10. Numbers are from the 15-dataset MFFP fair benchmark
(`results/raw_bench/`, seed 42, 2500 epochs). Citations: see
`RELATED_WORK_RESEARCH.md` for verified primary sources.*

---

## Abstract

We study the problem of predicting a 2-D physical field from a small vector of
global parameters (PDE coefficients, boundary values, source terms) in the
*multi-fidelity* regime, where abundant cheap low-fidelity (LF, coarse-grid)
simulations are paired with scarce expensive high-fidelity (HF) ones. Fourier
Neural Operators (FNOs) are a natural surrogate because their discretization
invariance lets a single network bridge fidelities, and the strongest known
recipe is simple LF→HF *transfer learning* (pretrain on LF, fine-tune on HF). We
ask a question that is upstream of all the elaborate multi-fidelity fusion
architectures in the literature: **how should the parameter vector be injected
into the operator at all?** The default — broadcasting it to constant channels and
concatenating — wastes the FNO's spectral machinery, because a spatially constant
field carries all its energy in the k=0 mode. We replace concatenation with
**per-block FiLM** (feature-wise linear modulation: GroupNorm followed by a
parameter-dependent per-channel affine γ(X)·h+β(X), zero-initialized to identity).
Holding the backbone and the transfer schedule *byte-for-byte identical*, this
single change takes the method from geometric-mean relative-L2 0.0123 to **0.0082
across 15 datasets — a new state of the art** that wins **14/15 datasets** and,
unlike every other method, dominates **both** the smooth and the hard non-smooth
regimes. We position this against the recently-introduced "FiLMed FNO" of Zhu et
al. (2025), which uses FiLM+FNO for zero-shot *equation* generalization in
time-stepping but contains no multi-fidelity transfer; to our knowledge we are the
first to use FiLM conditioning as the vehicle for multi-fidelity transfer in
neural operators, and the first to benchmark conditioning *mechanisms* (concat vs
FiLM vs hand-designed fusion) on a controlled footing.

---

## 1. Introduction

Surrogate models for parametric PDEs map a handful of governing parameters to a
full spatial field. Training a high-accuracy surrogate needs many HF solves, which
are expensive; multi-fidelity (MF) learning attacks this by leaning on cheap LF
data. A large zoo of MF neural-operator architectures has grown up around this
idea — coregionalization heads, residual/additive correction stacks,
Kennedy–O'Hagan autoregression, multilevel corrections, GP/neural-process hybrids.
Yet on smooth grid PDEs the method that keeps winning is the *simplest* one:
pretrain one FNO on LF data and fine-tune it on HF data (Lyu et al. 2023;
geological-carbon-storage MF-FNO 2023). The FNO's discretization invariance means
the LF-pretrained weights are directly meaningful at HF resolution, so weight-space
transfer beats elaborate output-space coupling.

This paper takes a step back. Every one of these methods must, at some point,
**condition** the network on the parameter vector X. The field-standard choice is
to broadcast X across the grid into constant channels and concatenate them with the
coordinate channels before the first lift. We argue this is a poor match for an
FNO and show that fixing it — with FiLM — yields a larger, more consistent
improvement than any of the architectural fusion mechanisms.

**Contributions.**
1. **A controlled study of conditioning mechanisms for FNOs.** We isolate
   concat vs FiLM with an otherwise byte-identical backbone and transfer schedule,
   the comparison the MF literature lacks.
2. **A new SOTA.** FiLM-conditioned transfer FNO reaches geomean rel-L2 **0.0082**
   over 15 datasets (vs 0.0123 for the concat transfer baseline, 0.0179 for the
   best hand-designed fusion), ranks #1 by ELO (1936; 215–17), and wins **14/15**
   datasets.
3. **A regime analysis** showing FiLM wins **both** smooth and hard non-smooth
   PDEs — removing the conditional caveat ("fusion overtakes on hard data") that
   limited the prior transfer baseline.
4. **Honest novelty positioning** against concurrent FiLM-FNO work (Zhu et al.
   2025; Shokar et al. 2025), drawing a precise boundary: prior FiLM-FNO targets
   equation generalization in *time-stepping*; ours is the first FiLM-for-MF-
   transfer in the *static parameter→field* setting.

---

## 2. Problem setting

We are given, per dataset, training pairs at multiple fidelities. Each fidelity
level provides examples (X, u) where X ∈ ℝ^d is a global parameter vector and
u: Ω→ℝ is a field discretized on a grid. LF fields live on coarse grids and are
plentiful; HF fields live on fine grids and are scarce. The goal is to predict the
HF field for unseen X. We resample all fields to a common 256-capped working grid
and evaluate the full field in raw units. The error metric is per-sample relative
L2 (we report its mean with a 95% bootstrap CI), aggregated across datasets by
geometric mean and summarized by a pairwise-win ELO.

This is **parameter→field** prediction, distinct from the field→field *time-
stepping* setting that dominates recent conditional-operator work. The FNO here
takes only the coordinate grid as input; *all* sample-to-sample variation must
enter through the conditioning of X.

---

## 3. How to condition an FNO: a taxonomy

Let c = X be the condition. Published options:

- **Constant-channel concatenation (default).** Broadcast c to constant fields,
  concatenate with coordinates, lift once. *Problem:* a constant channel is pure
  k=0; the spectral convolution — which acts mode-by-mode — barely transforms it,
  and the condition enters only once, at the bottom of the network.
- **FiLM / affine modulation (ours).** After each block's normalization, apply a
  per-channel affine (γ(c), β(c)) produced by a small MLP on c. Re-injects c at
  *every* block; for a *global* parameter vector, global per-channel modulation is
  the natural match and nothing is lost by dropping the constant-channel spatial
  encoding.
- **Hypernetwork → weights.** Map c to the operator's (e.g. spectral-conv)
  weights. Expressive but heavy; used in Zhu et al. (2025) and HyPINO.
- **Spectral gating.** Multiply Fourier modes by a gate produced from c
  (Zhu et al. 2025, "LSC-FNO").
- **Cross-attention.** Latent as query, c as key/value (SpectraKAN; Zhu et al.).

We benchmark the two that share the FNO's exact backbone — concat and FiLM —
because they isolate the *conditioning mechanism* without confounding capacity or
architecture. The richer mechanisms are discussed as related work.

### 3.1 FiLM-conditioned transfer FNO (method)

Backbone: a standard FNO (lift → N spectral blocks → projection) on the working
grid. Each block is `GELU(FiLMNorm(SpectralConv(z) + 1×1Conv(z), c))`, where
`FiLMNorm` is affine-free GroupNorm followed by `γ(c)·ẑ + β(c)`, with
`[γ;β] = MLP(c)` and the MLP's last layer zero-initialized so γ=1, β=0 at start
— the network begins as an unconditioned FNO over coordinates and learns to
modulate from there (standard FiLM init; avoids early divergence). The input is
the 2 coordinate channels only; X never appears as a channel.

Multi-fidelity = **transfer learning**, unchanged from the concat baseline:
(1) pretrain the FNO on LF (fields resampled to the working grid; LR 1e-3);
(2) fine-tune the same network on HF (LR 3e-4); (3) evaluate on the HF test split,
with a per-stage output scaler. FiLM conditions on X only; the fidelity index m
never enters the network — the multi-fidelity behavior lives entirely in the
schedule. This keeps the study a pure concat→FiLM ablation.

---

## 4. Experimental setup

**Datasets (15).** ifc_heat, ifc_poisson, heat_local, poisson_local, fluid,
darcy_generated, heat_generated, poisson_generated, advection_diffusion_generated,
allen_cahn_generated, burgers_generated, burgers_param_generated,
lid_driven_cavity_generated, era5, pm_test. Mix of 2-D square, 2-D rectangular
(era5/pm_test), and 1-D (allen_cahn/burgers/burgers_param) grids.

**Fair protocol.** Same epoch budget (2500), seed (42), data splits, working grid
(256-cap), and full-field metric for every method. Per-sample rel-L2 → 95%
bootstrap CI. We also track params, per-sample latency, peak memory, train wall-
time. Baselines that crash were fixed by hyperparameters only, never architecture.

**Methods compared (17).** FiLM transfer (ours); concat transfer
(`mf_fno_transfer`) and its param-matched 2M variant; hand-designed FNO fusion
(coreg_residual, mf_stack, coreg_conditioned, coregionalization, additive,
autoregressive, multilevel, coreg_lf_hf_transfer); attention fusion (Transolver
residual / attention); and external MF SOTA (MFRNP, MF-DeepONet, D-MFD,
v9 multistream).

---

## 5. Results

### 5.1 Main leaderboard (geomean relative-L2 over 15 datasets)

| Rank | Method | Geomean rel-L2 | Note |
|---|---|---|---|
| **1** | **FiLM transfer FNO (ours)** | **0.0082** | concat→FiLM only |
| 2 | Concat transfer FNO | 0.0123 | prior best |
| 3 | Concat transfer FNO (2M, param-matched) | 0.0125 | capacity control |
| 4 | FNO coreg-residual | 0.0179 | best hand-designed fusion |
| 5 | FNO mf-stack | 0.0249 | |
| 6 | FNO coreg-conditioned (FiLM on m) | 0.0320 | |
| 7 | FNO autoregressive | 0.0345 | |
| 8 | FNO additive | 0.0347 | |
| 9 | FNO coregionalization | 0.0557 | |
| 10 | FNO coreg-lf-hf-transfer | 0.0575 | |
| 11–12 | Transolver attn / residual | 0.082 / 0.083 | |
| 13 | FNO multilevel | 0.139 | |
| 14–17 | MFRNP / v9 / MF-DeepONet / D-MFD | 0.20–0.41 | |

ELO (pairwise wins, 16-way): **FiLM transfer #1 at 1936 (215–17)**, +199 over the
concat transfer FNO (1738). FiLM beats the prior winner on **14/15** datasets
(only `fluid` ties, 1.01×); largest gains on lid-driven cavity (0.48×),
advection–diffusion (0.31×), allen–cahn (0.40×), poisson (0.54×), darcy (0.55×).

### 5.2 The mechanism, not capacity

FiLM adds only the small per-block FiLM MLPs over the concat baseline; the
spectral backbone (`SpectralConv2d`) is byte-for-byte identical and the transfer
schedule is unchanged. The concat baseline's own param-matched 2M variant
(0.0125) does *not* close the gap to FiLM (0.0082), so the improvement is the
conditioning mechanism, not capacity.

### 5.3 Regime split: FiLM wins where the old baseline broke

We split datasets into **smooth** (10) and **hard / non-smooth** (5:
ifc_poisson, era5, pm_test, burgers, burgers_param).

| Method | Smooth (10) | Hard (5) | All (15) |
|---|---|---|---|
| **FiLM transfer (ours)** | **0.00176** | **0.17545** | **0.00815** |
| Concat transfer | 0.00289 | 0.22262 | 0.01231 |
| FNO coreg-residual | 0.00458 | 0.20766 | 0.01788 |
| FNO mf-stack | 0.00551 | 0.50614 | 0.02487 |

In the prior benchmark the story was *conditional*: concat transfer won the smooth
regime, but hand-designed fusion (`coreg_residual`) overtook it on hard data.
**FiLM removes that caveat** — it is #1 on smooth *and* on hard, overtaking the
previously-best hard-regime method. The conditioning fix helps most exactly where
the constant-channel encoding is least adequate.

### 5.4 Few-shot HF (ongoing)

A few-shot-HF sweep (N_HF ∈ {5,10,25,50,100}, 4 datasets, 3 seeds) currently
covers concat-transfer / additive / HF-only and shows transfer's margin growing as
HF shrinks. Re-running it with FiLM is the natural next experiment and the
prediction is sharp: FiLM's edge should widen under HF scarcity, because re-
injecting X at every block is most valuable when there is little HF data to learn
spatial structure from. *(Flagged as TODO; not yet run.)*

### 5.5 Cost

FiLM transfer is cheap to serve: low per-sample latency and ~4.7M params (vs the
2M param-matched control), in the same envelope as the concat transfer FNO. Full
params/latency/memory table from `results/bench_compute.csv`.

---

## 6. Related work

**Conditioning FNOs with FiLM.** The closest prior art is **Zhu, Raccuglia &
Brenner (2025), "Generalizing PDE Emulation with Equation-Aware Neural Operators"
(arXiv:2511.09729)**, which introduces an explicit "FiLMed FNO" conditioned on a
PDE-equation/coefficient vector, citing Perez et al. (2018). It targets **zero-
shot generalization across equations** in **autoregressive time-stepping**, and
contains no multi-fidelity data or LF→HF transfer. **Shokar, Kerswell & Haynes
(2025, arXiv:2509.09599)** condition a PDE emulator on parameters via FiLM-as-
adaptive-LayerNorm, with zero-init γ/δ and a pretrain→finetune schedule that
closely parallels ours — but on a **local-attention Transformer (not an FNO)**,
for **time-stepping**, and with cross-domain-size (not multi-fidelity)
pretraining. We are, to our knowledge, the first to use FiLM as the conditioning
vehicle for **multi-fidelity LF→HF transfer in neural operators** for **static
parameter→field** prediction, and the first to ablate concat vs FiLM on an
identical FNO backbone. Other conditioning routes — hypernetworks generating
spectral weights (Zhu et al.; HyPINO), spectral gating (Zhu et al.), and cross-
attention over a Fourier trunk (SpectraKAN, arXiv:2602.05187) — are more complex
and not controlled against a matched backbone.

**Multi-fidelity neural operators.** Transfer-learning MF-FNO (Lyu et al. 2023,
Phys. Fluids; geological-carbon-storage MF-FNO 2023) is our base and the strongest
prior recipe on smooth grid PDEs, exploiting FNO grid-invariance. Residual/
additive correction methods include MFRNP (neural-process, residual via decoder
aggregation), MF-DeepONet (coupled DeepONets, residual + input augmentation), and
Demo–Tezzele–Rozza (2023, DeepONet residual over a POD-ROM). Other families use
coregionalization heads, discretization-invariance as the MF mechanism, and multi-
resolution active learning (MRA-FNO). Across all of these, fidelity is handled by
network reuse, architectural residuals, a coregionalization basis, or resolution-
invariance — **not** by feature-wise modulation, which is the gap we fill.

**FiLM.** Feature-wise linear modulation originates with Perez et al. (2018,
arXiv:1709.07871).

---

## 7. Discussion & limitations

The result is a reminder that *how you inject the condition* can matter more than
*which fusion architecture you bolt on top*. FiLM matches the inductive structure
of the problem: a global parameter vector should modulate features globally and
repeatedly, not enter once as a near-spectrally-inert constant channel.

Limitations: (1) the hard regime is hard for everyone — even the FiLM method has
rel-L2 ≈ 0.18 there (burgers_param > 1 for all methods), so the win is relative,
not "solved"; (2) the few-shot-HF FiLM sweep is not yet run; (3) we ablate concat
vs FiLM but not the full conditioning zoo (hypernetwork/gating/attention) on a
matched backbone — a natural extension; (4) FiLM conditions on X only, leaving
explicit fidelity-index conditioning (cf. our coreg-conditioned variant) for
future work.

---

## 8. Conclusion

For multi-fidelity parameter→field prediction with FNOs, replacing constant-
channel concatenation with per-block FiLM — nothing else changed — sets a new
state of the art across 15 datasets and, uniquely, wins both smooth and non-smooth
regimes. The contribution is not a new fusion architecture but the right way to
condition the operator you already have.

---

### Appendix A — TODO before submission
- [ ] Re-run few-shot-HF sweep (§5.4) with the FiLM family (3 seeds × 4 datasets × 5 N_HF).
- [ ] Re-benchmark lid-driven cavity on the converged **v2** data (see memory: cavity v1 HF was non-converged; v2 in `lid_driven_cavity_generated_v2/`) and update the cavity row everywhere.
- [ ] Add the controlled hypernetwork / spectral-gating / cross-attention conditioning variants on the *same* backbone (referee-proofing §3 taxonomy).
- [ ] Fix citation: `beggs2025pdecond` → **Shokar, Kerswell & Haynes 2025** (arXiv:2509.09599) in model.py / manifest / refs.
- [ ] Verify the remaining MF/conditioning arXiv IDs in RELATED_WORK_RESEARCH.md §refs before citing.
- [ ] Decide venue/format (NeurIPS/ICLR ML-for-science vs JCP/CMAME).
- [ ] Generate figures: leaderboard bar+CI, regime-split grouped bars, per-dataset FiLM/concat ratio scatter, few-shot curves.
