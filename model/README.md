# Model Zoo — Multi-Fidelity Field Prediction Benchmark

TL;DR of every model family benchmarked in this repo (30 families × 15 datasets, fair
protocol: per-sample relative-L2 with 95% bootstrap CIs, shared geometry-general
backbone + eval plumbing, 2500 epochs, seed 42).

**What multi-fidelity (MF) means here:** each task gives abundant *low-fidelity* (LF,
cheap/coarse) data and scarce *high-fidelity* (HF, expensive/fine) data. A model must
fuse them to predict the HF field. The families below differ almost entirely in *how*
they fuse — the backbone (a Fourier Neural Operator, "FNO") is held roughly constant so
the comparison isolates the MF mechanism.

**FNO primer:** a Fourier Neural Operator learns a mapping between function fields by
mixing features in the spectral domain (FFT → keep low modes → linear transform →
iFFT). It's resolution-flexible and the default backbone for ~22 of the 30 families.

Ranking is by **Elo** (per-dataset pairwise wins, outlier-robust); `med relL2` is the
median per-dataset relative-L2 error (lower is better). For the FIRE families the *mean*
relL2 is wrecked by a few blow-up datasets — trust the Elo and median columns.

## Leaderboard (current, 436/450 cells)

| Rk | Model | Elo | med relL2 | params | family |
|----|-------|----:|----:|----:|---|
| 1 | mf_fno_transfer_film | 1820 | 0.0154 | 4.77M | FNO · transfer |
| 2 | mf_fno_pinn_transfer | 1799 | 0.0122 | 4.77M | FNO · transfer+physics |
| 3 | fno_fire_distcond | 1671 | 0.0264 | 28.4M | FNO · FIRE |
| 4 | fno_fire_snapshot | 1643 | 0.0389 | 28.4M | FNO · FIRE |
| 5 | fno_fire_batchens | 1633 | 0.0407 | 9.50M | FNO · FIRE |
| 6 | fno_fire_mdn | 1626 | 0.0352 | 9.48M | FNO · FIRE |
| 7 | fno_fire_iqn | 1619 | 0.0373 | 9.48M | FNO · FIRE |
| 8 | mf_fno_transfer | 1616 | 0.0151 | 4.74M | FNO · transfer |
| 9 | fno_fire_quantile | 1603 | 0.0264 | 9.48M | FNO · FIRE |
| 10 | mf_fno_transfer_2m | 1595 | 0.0152 | 2.67M | FNO · transfer |
| 11 | fno_fire_laplace | 1584 | 0.0169 | 9.48M | FNO · FIRE |
| 12 | fno_fire_swag | 1567 | 0.0229 | 9.48M | FNO · FIRE |
| 13 | fno_coreg_conditioned | 1559 | 0.0455 | 4.76M | FNO · coregionalization |
| 14 | fno_fire_cqr | 1547 | 0.0462 | 28.4M | FNO · FIRE |
| 15 | fno_fire_dkl | 1524 | 0.0170 | 9.48M | FNO · FIRE |
| 16 | fno_dino_residual | 1502 | 0.0259 | 9.54M | FNO · vision-feature |
| 17 | fno_mf_stack | 1485 | 0.0344 | 2.35M | FNO · residual stack |
| 18 | fno_additive | 1452 | 0.0285 | 9.48M | FNO · discrepancy |
| 19 | fno_coreg_lf_hf_transfer | 1450 | 0.0551 | 1.19M | FNO · coregionalization |
| 20 | fno_coregionalization | 1450 | 0.0538 | 1.19M | FNO · coregionalization |
| 21 | fno_coreg_residual | 1450 | 0.0251 | 2.37M | FNO · coregionalization |
| 22 | fno_autoregressive | 1450 | 0.0263 | 9.48M | FNO · discrepancy |
| 23 | transolver_residual | 1392 | 0.116 | 0.70M | Transformer |
| 24 | fno_fire_mcdropout | 1368 | 0.0412 | 9.48M | FNO · FIRE |
| 25 | fno_multilevel | 1338 | 0.160 | 18.96M | FNO · discrepancy |
| 26 | transolver_attention_fusion | 1337 | 0.322 | 2.28M | Transformer |
| 27 | mfrnp | 1287 | 0.295 | 2.60M | Neural process |
| 28 | d_mfd | 1260 | 0.430 | 2.52M | Bayesian |
| 29 | mf_deeponet | 1197 | 0.0839 | 0.54M | DeepONet |
| 30 | v9_baseline | 1176 | 0.210 | 0.43M | Transformer (ref) |

---

# FNO-based models (22 of 30)

All share an FNO backbone; they differ in the multi-fidelity fusion mechanism.

## Transfer-learning FNO — *the winners*

The canonical "pretrain on LF, fine-tune on HF" paradigm. MF lives in the training
*schedule*, not in extra architecture.

- **mf_fno_transfer** (#8) — Canonical Lyu-2023 MF-FNO: one FNO pretrained on abundant
  LF data, then fine-tuned on scarce HF. No per-fidelity nets, residual head, or
  coregionalization. The published-baseline reference for "what transfer alone buys you."
- **mf_fno_transfer_2m** (#10) — Parameter-matched control of the above (width 64→48,
  ~2.67M params) so the comparison separates the transfer *mechanism* from raw capacity.
- **mf_fno_transfer_film** (#1, **best overall**) — Same transfer-FNO, but the condition
  vector X is injected by **per-block FiLM affine modulation** (γ,β) instead of
  channel-concatenation. The only change vs. `mf_fno_transfer` is concat→FiLM, so its #1
  finish pins the win on the *conditioning mechanism*. (FiLM conditions on X only; m never
  enters — MF stays in the schedule.)
- **mf_fno_pinn_transfer** (#2) — `mf_fno_transfer_film` **+ a PDE-residual (PINN) loss**
  during HF fine-tuning on the Poisson datasets, where the source f(x) of ∇²u=f is
  recovered exactly in closed form from X (validated rel-L2 ~1e-7). Non-Poisson datasets
  fall back to plain FiLM-transfer, isolating the physics contribution. Tests whether known
  governing physics beats the strong pure-data transfer baseline.

## Coregionalization FNO — continuous-fidelity latent head

Infinite-Fidelity-Coregionalization (IFC, Li 2022) style: a head that modulates the
latent field by a continuous fidelity index m via a basis B(m)=MLP([m, m²]).

- **fno_coregionalization** (#20) — FNO backbone + IFC coregionalization head
  f(x,m)=B(m)·h(x,m), K=10 latent, per-fidelity output normalization. The clean baseline.
- **fno_coreg_conditioned** (#13) — Replaces the coregionalization head with
  **FiLM-via-LayerNorm** on m: each block does GroupNorm then per-channel affine (γ(m),β(m))
  from an MLP on [m, m²]. Puts the m-modulation in the normalization layer instead of a
  K-dim head.
- **fno_coreg_lf_hf_transfer** (#19) — Coregionalization FNO trained with an explicit
  LF→HF transfer schedule (coregionalization × transfer).
- **fno_coreg_residual** (#21) — Hybrid: 4 per-fidelity FNOs + MFRNP-style
  decoder-in-the-aggregation + a continuous-m coregionalization basis head on the HF latent,
  zero-initialized so the net starts as the pure aggregator and *grows* the residual.

## Discrepancy / multi-level correction FNO — classical MF rules, FNO-ized

The textbook surrogate-correction families (Peherstorfer survey), each as two+ FNOs.

- **fno_additive** (#18) — Additive correction **HF = LF_pred + δ**. Frozen FNO_LF on
  abundant LF data; FNO_δ fits the HF residual. Pure 2-fidelity additive rule.
- **fno_autoregressive** (#22) — Multiplicative/AR correction **HF = ρ·LF_pred + δ** with a
  *learned scalar* ρ (Kennedy & O'Hagan 2000). Adds a learned gain on the LF prior.
- **fno_multilevel** (#25) — Recursive telescoping cascade **pred_k = pred_{k-1} + δ_k**
  (Le Gratiet recursive co-kriging), one FNO per fidelity level. Largest model (18.96M).
- **fno_mf_stack** (#17) — 4 small per-fidelity FNOs with MFRNP-style residual stacking:
  decoder-in-the-aggregation, HF FNO predicts δ on top of upsampled-aggregate LF predictions.

## FIRE distribution-conditioned FNO — *uncertainty-source ablation*

Field analog of **FIRE** (Yu, Sung & Ahmed 2026, arXiv:2601.22371). Core idea: an LF
*predictive distribution* (not just its mean) carries information about where the LF→HF
gap is large. An uncertainty estimator produces per-pixel summary **fields** (mean μ,
std σ, q10/q50/q90); the HF correction FNO is conditioned on those distributional channels
and predicts **HF = μ_LF + δ(x, [μ,σ,q10,q50,q90])**. The 9 variants below share one
backbone+pipeline (`models/_common/fire_core`, `fire_methods`) and *only* swap the
uncertainty source — a clean ablation of "which uncertainty estimate helps most."

- **fno_fire_distcond** (#3, **the keeper**) — uncertainty from a deep **ensemble** of
  LF-FNOs. Strongest FIRE variant; conditioning on LF uncertainty handles spatially
  heteroscedastic cross-fidelity error that mean-only `fno_additive` can't.
- **fno_fire_snapshot** (#4) — snapshot ensemble (cyclic-LR, 5 snapshots, 1 training).
- **fno_fire_batchens** (#5) — multi-head / batch ensemble (shared trunk, 5 heads).
- **fno_fire_mdn** (#6) — mixture density network (3 Gaussians per pixel).
- **fno_fire_iqn** (#7) — implicit quantile network (τ-conditioned quantiles).
- **fno_fire_quantile** (#9) — direct quantile regression (pinball loss, q10/q50/q90 heads).
- **fno_fire_laplace** (#11) — last-layer Laplace (Gaussian weight posterior via GGN).
- **fno_fire_swag** (#12) — SWAG (diagonal Gaussian over the SGD-tail weights, 10 samples).
- **fno_fire_cqr** (#14) — snapshot ensemble **+ conformal** calibration (coverage-guaranteed
  percentiles).
- **fno_fire_dkl** (#15) — deep-kernel last-layer GP (Bayesian linear layer on FNO features).
- **fno_fire_mcdropout** (#24, *honest negative*) — cheap single-model FIRE: one dropout
  LF-FNO, MC-dropout (T stochastic passes) for the distribution fields instead of a
  5-member ensemble. The cheap shortcut underperforms the real ensemble.

## Vision-foundation-feature FNO

- **fno_dino_residual** (#16, *honest negative*) — additive FNO correction where a **frozen
  DINOv2** encodes the LF field *as an image* into a 768-d embedding that conditions FNO_δ
  (embeddings precomputed once, so no per-epoch cost). Direct ablation partner to
  `fno_additive` (same additive rule, minus the DINO feature). Vision features did not help.

---

# Transformer-based models

- **transolver_residual** (#23) — Transolver (physics-attention slice-attention) backbone
  trained as a **hard MF residual**: HF = LF_interp(query) + transolver_δ(query, LF_context).
  Isolates the delta-learning capacity of slice attention. Smallest non-baseline net (0.70M).
- **transolver_attention_fusion** (#26) — Transolver with **iterated cross-fidelity
  attention** as the fusion: HF queries attend through N stacked cross-attention blocks, each
  refining HF against LF context. Stress-tests the "attention *is* the fusion" hypothesis
  (no explicit residual or gate).
- **v9_baseline** (#30) — Frozen `MFTransolver_v9`, point-wise **gated fusion** over
  multiple LF streams. The prior best in-house model; runs every cycle as the reference
  baseline to beat (not the published yardstick).

---

# External SOTA wrappers (neural-process / DeepONet / Bayesian)

Faithful wrappers of published upstream code, plugged into the same fair-eval plumbing.

- **mfrnp** (#27) — Multi-Fidelity Residual Neural Processes (Niu et al. 2024, ICML).
  github.com/Rose-STL-Lab/MFRNP (MIT).
- **mf_deeponet** (#29) — Multifidelity DeepONet (Lu et al. 2022, Phys. Rev. Research).
  github.com/lu-group/multifidelity-deeponet (Apache-2.0).
- **d_mfd** (#28) — Disentangled Multi-Fidelity Deep Bayesian Active Learning (Wu et al.
  2023, ICML). github.com/Rose-STL-Lab/Multi-Fidelity-Deep-Active-Learning (research-only).

---

## Headline takeaways

1. **Conditioning mechanism > extra architecture.** `mf_fno_transfer_film` (#1) beats plain
   `mf_fno_transfer` (#8) with an identical backbone and schedule — the sole change is
   concat→FiLM conditioning. Simple transfer + the right conditioning tops everything.
2. **Known physics adds a little more.** `mf_fno_pinn_transfer` (#2) edges out by adding an
   exact Poisson PDE-residual term on top of FiLM-transfer.
3. **LF uncertainty is a useful conditioning signal.** The FIRE family (#3–#15) clusters high;
   `fno_fire_distcond` is the keeper. But the cheap MC-dropout shortcut (#24) and DINO vision
   features (#16) are honest negatives.
4. **Classic correction rules and external NP/DeepONet/Bayesian baselines trail** the
   transfer + FIRE FNO families on these datasets.

*Numbers regenerate from `results/bench_elo.csv`, `results/bench_metrics.csv`, and
`results/bench_compute.csv`. Per-family source: `models/<family>/` or
`references/external_sota/<family>/` (`manifest.json` + `smoke_eval.py`).*
