# Multi-Fidelity Field Prediction — Research Summary

*A study of how to combine cheap low-fidelity and scarce high-fidelity PDE data to predict
solution fields. What we tried, why we expected each idea to work, and what actually happened.*

---

## 1. Motivation

Many engineering and science workflows need the solution field of a PDE (temperature,
pressure, velocity…) as a function of input parameters `X` (boundary conditions, material
properties, source terms). Producing that field at **high fidelity (HF)** — fine grids,
converged solvers — is expensive, so HF data is scarce. **Low-fidelity (LF)** data — coarse
grids, cheap approximations — is abundant but biased.

**Multi-fidelity (MF) learning** tries to get HF accuracy from mostly LF data. The MF
literature offers a zoo of mechanisms — additive/multiplicative discrepancy, coregionalization,
recursive co-kriging, neural processes, transfer learning — but they are rarely compared
*fairly*: papers use different backbones, datasets, and metrics, so it is unclear whether a
fancy fusion scheme actually beats a simple one.

**This project's goal:** build one fair benchmark, put every reasonable MF mechanism on the
*same* neural-operator backbone, and find out which idea actually wins — and why.

**Headline answer:** the way you **inject the parameter vector** into the operator matters
more than any fusion scheme. A Fourier Neural Operator (FNO) that is simply pretrained on LF
and fine-tuned on HF, with `X` injected via **FiLM conditioning**, beats every hand-designed
fusion method, attention model, and Gaussian-process / neural-process baseline.

---

## 2. Datasets

15 datasets spanning three geometries (2-D square, 2-D rectangular, 1-D) and a wide range of
difficulty, parameter count `d`, fidelity levels `L`, and HF-data scarcity `N_HF`. The spread
is deliberate: it stops any single model from winning by overfitting one regime.

| Dataset | PDE / domain | d | L | HF grid | N_HF | Regime |
|---|---|---|---|---|---|---|
| ifc_heat | heat 2-D | 3 | 4 | 64² | 5 | smooth |
| ifc_poisson | Poisson 2-D | 5 | 4 | 64² | 5 | **hard** |
| heat_local | heat 2-D | 3 | 5 | 128² | 1024 | smooth |
| poisson_local | Poisson 2-D | 5 | 5 | 128² | 64 | smooth |
| fluid | fluid 2-D | 2 | 2 | 64² | 256 | smooth |
| heat_generated | heat 2-D | 3 | 3 | 64² | 400 | smooth |
| poisson_generated | Poisson 2-D | 5 | 3 | 64² | 400 | smooth |
| darcy_generated | Darcy 2-D | 16 | 3 | 128² | 160 | smooth |
| advection_diffusion_generated | adv–diff 2-D | 2 | 2 | 64² | 400 | smooth |
| lid_driven_cavity_generated | Navier–Stokes 2-D | 1 | 4 | 256² | 40 | smooth |
| allen_cahn_generated | Allen–Cahn 1-D | 2 | 3 | 1×256 | 400 | smooth |
| burgers_generated | Burgers 1-D | 8 | 3 | 1×256 | 400 | **hard** |
| burgers_param_generated | Burgers 1-D | 5 | 3 | 1×256 | 320 | **hard** |
| era5 | reanalysis 2-D | 12 | 9 | 721×1440 | 65 | **hard** |
| pm_test | reanalysis 2-D | 12 | 9 | 721×1440 | 65 | **hard** |

- **The "hard" set (5):** ifc_poisson, era5, pm_test, burgers, burgers_param. These are where
  model rankings scramble — sharp features, scale collapse, or real-world reanalysis noise.
  Everyone scores 1e-3…1e-2 on the smooth datasets, so the hard set carries the discriminating
  power.
- **Two `chin_chun_*` datasets are excluded** from the 15 (heavy 12 GB tarballs).
- **Quality control:** a fidelity audit confirmed 7/8 generated datasets have rigorously-
  converged HF. The exception — lid-driven cavity, which had been stopped before steady state —
  was regenerated (`v2`, validated against Ghia 1982).

### Fair-comparison protocol
Every model is trained with the **same** epoch budget (2500), seed (42), data splits, eval
metric, and a 256-capped working grid. We report **per-sample relative-L2 error with 95%
bootstrap confidence intervals**, an overall **geometric-mean error**, and a head-to-head
**ELO** rating from per-dataset pairwise wins. Crashing external baselines were made to *run*
on every dataset by tuning hyperparameters only — never by changing their architecture.

---

## 3. The shared backbone

All in-tree FNO families are built from one geometry-general backbone, so the comparison
isolates the **MF mechanism**, not the network. Structure: `lift → N FNO blocks → projection`.
Each FNO block runs a **spectral convolution** (FFT → keep the lowest Fourier modes → multiply
each by a learned complex weight → inverse FFT) in parallel with a **1×1 conv**, summed, then
normalized and activated. The spectral path learns global, resolution-independent structure;
the 1×1 path captures local detail. Models differ only in *what extra signal enters this
backbone* and *how it is trained*.

---

## 4. Models tried — hypothesis and result

Ordered roughly best-to-worst. ELO is the head-to-head rank (of 30); geomean is the relative-L2
error over the 15 datasets.

### 4.1 Transfer-learning FNO and its conditioning variants — *the winners*

**`mf_fno_transfer` (plain transfer)** — ELO #8, geomean 0.0123
*Hypothesis:* an FNO is discretization-invariant, so a single network pretrained on abundant
LF data already learns the right spatial operator; a short fine-tune on scarce HF data only
needs to adapt amplitude and fine detail. No per-fidelity networks, no fusion head — the MF
behavior lives entirely in the training schedule (Lyu 2023). A per-stage output scaler handles
LF/HF magnitude mismatch.
*Result:* strong and robust; the baseline that everything else had to beat. The per-stage
scaler is what lets it survive the Poisson scale-collapse where most fusion methods blow up.

**`mf_fno_transfer_film` (transfer + FiLM)** — **ELO #1, geomean 0.0082** — *the winner*
*Hypothesis:* in the plain model, `X` is broadcast to a constant channel and concatenated once
at the bottom. But a spatially-constant field puts all its energy in the k=0 Fourier mode, so
the spectral conv barely acts on it. Instead, inject `X` via **FiLM**: a small MLP produces
per-channel affine parameters γ(X), β(X) applied after normalization in *every* block, so the
condition is re-applied throughout the network. Zero-init means it starts as the plain model
and can only improve.
*Result:* the new SOTA — wins 14/15 datasets, #1 by both geomean and ELO, and uniquely #1 in
*both* the smooth and hard regimes. The only model with no catastrophic column. This reframed
the whole project: **conditioning, not fusion, is what MF neural operators need.**

**`mf_fno_pinn_transfer`** — ELO #2, geomean ~0.006 (Poisson subset)
*Hypothesis:* on datasets with a known governing equation (Poisson), add the exact PDE residual
as an auxiliary loss during HF fine-tuning so the model is physically consistent where HF data
is thinnest.
*Result:* #2 overall; the physics loss helps on the Poisson datasets specifically.

**`mf_fno_transfer_2m` (param-matched ablation)** — ELO #10, geomean 0.0125
*Hypothesis:* maybe transfer wins only because it's a bigger network. Shrink it to match the
fusion models' parameter count and re-test.
*Result:* still beats the fusion methods → **it's the mechanism, not the capacity.**

### 4.2 Hand-designed fusion FNOs — *the textbook MF taxonomy*

These implement the classical MF recipes as explicit architecture. Common hypothesis: *the
right inductive bias for cross-fidelity structure should beat naive transfer.*

| Model | Hypothesis (why it might win) | ELO | geomean |
|---|---|---|---|
| **fno_coreg_residual** | combine a learned multi-fidelity basis (coregionalization) with an explicit HF-minus-LF residual stack — get both shared structure and a correction term | #21 | 0.0179 |
| **fno_mf_stack** | per-fidelity FNOs feeding a residual stack let each fidelity specialize before fusion | #17 | 0.0249 |
| **fno_coreg_conditioned** | a single HF FNO conditioned on the fidelity index `m` via FiLM-on-`m` is simpler than separate networks | #13 | 0.0320 |
| **fno_autoregressive** | Kennedy–O'Hagan: HF = ρ·LF + δ, a learned scale plus additive correction | #22 | 0.0345 |
| **fno_additive** | the simplest discrepancy model: HF = LF + δ | #18 | 0.0347 |
| **fno_coregionalization** | a continuous-fidelity coregionalization head shares a low-rank basis across fidelities | #20 | 0.0557 |
| **fno_coreg_lf_hf_transfer** | coregionalization head *plus* a 2-stage LF→HF transfer schedule | #19 | 0.0575 |
| **fno_multilevel** | Le Gratiet recursive co-kriging: a telescoping cascade, one FNO per fidelity level | #25 | 0.1389 |

*Result:* the best fusion model (`fno_coreg_residual`, 0.0179) is **still ~2× worse than
FiLM-transfer (0.0082)**. The elaborate inductive biases did not pay off; in the regime split,
fusion overtakes *plain concat* transfer on the hard datasets, but not FiLM-transfer. **Verdict:
explicit fusion machinery is unnecessary.**

### 4.3 FIRE — distribution-conditioned residuals — *the best new idea*

**`fno_fire_distcond`** — **ELO #3, geomean 0.0274** — *the keeper*
*Hypothesis:* the LF model's error is **spatially heteroscedastic** — it concentrates at shocks,
boundaries, and vortex cores. A correction that sees only the LF *mean* can't know where the LF
prediction is untrustworthy. So first train a **deep ensemble of LF-FNOs** to get a per-pixel
*uncertainty distribution* (mean μ, std σ, quantiles), then condition the HF correction on those
distributional fields: HF = μ_LF + δ(x, [μ, σ, q10, q50, q90]). (Field analog of FIRE, Yu/Sung/
Ahmed 2026.)
*Result:* the strongest genuinely-new mechanism — #3 by ELO. Beats its mean-only ablation
(`fno_additive`) on 14/15 datasets, with the biggest gains exactly on the heteroscedastic,
non-smooth datasets the hypothesis predicted (era5, poisson_local, burgers).

**Ten FIRE variants** swapped the uncertainty source (snapshot ensemble, multi-head, MDN, IQN,
quantile regression, Laplace, SWAG, conformal, deep-kernel GP). *Hypothesis for each:* a cheaper
or better-calibrated uncertainty estimate could match the deep ensemble. *Result:* they cluster
just below `distcond` (ELO #4–#15) — the uncertainty *source* matters less than the idea of
conditioning on it at all. The one clear loser:

**`fno_fire_mcdropout`** — ELO #24, geomean 0.0438 — *honest negative*
*Hypothesis:* MC-dropout could give the same uncertainty fields from a single cheap model.
*Result:* a much weaker epistemic estimate than a true ensemble — the ensemble cost is justified.

### 4.4 Vision foundation model — *honest negative*

**`fno_dino_residual`** — ELO #16, geomean 0.0409
*Hypothesis:* a pretrained vision transformer (DINOv2) sees the LF field as an image and returns
a rich semantic embedding capturing global structure (fronts, vortices, symmetry) that a small
FNO might miss; condition the HF correction on it.
*Result:* worse than the simple additive baseline; catastrophic on poisson_local (14× worse).
**ImageNet-pretrained features do not transfer reliably to PDE fields.** A clean negative result.

### 4.5 Attention / transformer

**`transolver_residual`, `transolver_attention_fusion`** — ELO #23, #26; geomean ~0.082
*Hypothesis:* cross-fidelity attention can learn the LF→HF relation more flexibly than a fixed
fusion rule.
*Result:* mid-to-low table; the extra flexibility didn't help and cost accuracy on this task.

### 4.6 Published external baselines

| Model | Hypothesis | ELO | geomean |
|---|---|---|---|
| **mfrnp** | multi-fidelity residual *neural processes* model cross-fidelity correlation probabilistically | #27 | 0.2491 |
| **mf_deeponet** | branch/trunk operator learning with a multifidelity head | #29 | 0.2014 |
| **d_mfd** | disentangled multi-fidelity deep Bayesian model | #28 | 0.4087 |
| **v9_baseline** | the project's prior best — point-wise gated fusion of LF streams | #30 | 0.1188 |

*Result:* all well behind the FNO-based methods. These are the published-SOTA reference points
the benchmark improves on by an order of magnitude.

### 4.7 Hybrid, still under investigation

**`dg_fno` / `dg_transfer`** — not yet benchmarked
*Hypothesis:* combine the #1 and #3 ideas — let FIRE's LF-uncertainty fields *gate* the
FiLM-transfer operator (spatial-FiLM + spectral-mode-gate), zero-init so it starts as the #1
model and can only add value. The natural next experiment.

---

## 5. Results at a glance

- **Ranking:** FiLM-transfer (0.0082) > FIRE-distcond (0.0274) > plain transfer (0.0123 — note
  it beats FIRE on raw error but loses on ELO) > DINO (0.0409) > Transolver (0.082) > neural-
  process / DeepONet baselines (0.20–0.41).
- **ELO vs error disagree at the margins:** FIRE ranks above plain transfer on ELO (more
  consistent head-to-head wins) but has higher mean error (one catastrophic dataset). ELO
  rewards consistency; geomean punishes any blow-up.
- **The Poisson scale-collapse is the discriminator.** On `ifc_poisson`, FIRE (22.9), DINO
  (19.4) and DeepONet (13.9) blow up >1000×, while transfer/FiLM stay ~0.02 thanks to the
  per-stage output scaler. (Error > 1.0 = worse than predicting zero.)
- **Robustness, not peak accuracy, wins.** FiLM-transfer is the only model with no catastrophic
  column — that, more than any single best score, is why it is #1.

Plots: `results/plots/story_elo_vs_error.png` (ELO vs error, 7 representative models),
`results/plots/story_error_heatmap.png` (model × dataset error heatmap).

### Hardening experiments
- **Regime split (the key figure):** plain transfer is #1 on smooth PDEs but is overtaken by
  fusion on the hard 5 — a *conditional* win. FiLM-transfer then wins *both* regimes, removing
  the caveat.
- **Few-shot-HF sweep:** raw data collected (transfer vs additive vs HF-only at N_HF ∈ {5…100});
  aggregate/plot and the FiLM arm are still TODO. Expected to show transfer's margin growing as
  HF data shrinks.
- **Pairing-difficulty correlation:** dropped — inconclusive (most datasets have equal LF/HF
  counts, so no variance to correlate).

---

## 6. Open items

1. Benchmark the **`dg_fno`/`dg_transfer`** FiLM×FIRE hybrid — the obvious next family.
2. Finish the **few-shot** experiment (aggregate + plot, add the FiLM arm) — the highest-value
   remaining test.
3. Re-benchmark **lid-driven-cavity v2** and update its row everywhere.
4. **Paper cleanup:** the ELO quoted in the draft (1936) is stale vs the live 30-model file
   (1819.7); the regime-split CSV/plot are pre-FiLM and should be regenerated.
