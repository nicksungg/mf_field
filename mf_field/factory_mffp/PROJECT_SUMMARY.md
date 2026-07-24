# MFFP — Multi-Fidelity Field Prediction: Project Summary

*Generated 2026-06-22. Scope: the full `mf_field/factory_mffp` research project — the
benchmark, every model family, the autonomous factory run, the hardening experiments,
and the paper.*

---

## 1. What this project is

A study of **how to do multi-fidelity (MF) learning for parametric PDE field
prediction**: given a parameter vector `X` (viscosity, BCs, source terms…), predict a
2-D/1-D solution field, using *abundant cheap low-fidelity (LF)* data plus *scarce
expensive high-fidelity (HF)* data. The deliverable is a **fair benchmark** of every
sensible MF mechanism on a common backbone, plus a paper arguing for the winner.

**Headline finding:** holding the FNO backbone and the LF→HF transfer schedule *byte-for-byte
identical*, the way you **inject the parameter vector** matters more than any multi-fidelity
fusion scheme. Per-block **FiLM conditioning** (`mf_fno_transfer_film`) is #1, beating
hand-designed fusion, attention, GP/neural-process baselines, and an autonomous LLM factory.

| Axis | Winner | Number |
|---|---|---|
| Geomean rel-L2 (15 datasets) | `mf_fno_transfer_film` | **0.0082** (vs 0.0123 concat-transfer, 0.0179 best fusion) |
| Head-to-head ELO (30 models) | `mf_fno_transfer_film` | **1819.7** (353–66–2) |
| Datasets won | `mf_fno_transfer_film` | 14 / 15 |
| #1 in BOTH smooth & hard regimes | `mf_fno_transfer_film` | yes |

---

## 2. The benchmark

### 2.1 Protocol (agreed 2026-05-29)
- **Fair comparison:** same epoch budget (2500), same seed (42), same data splits, same
  eval metric, same 256-capped working grid, for every model on every dataset.
- **Error bars:** per-test-sample relative-L2 → 95 % **bootstrap CI** (not multi-seed).
- **Tracked per run:** `n_params`, train wall-time, eval latency (ms/sample), peak GPU mem.
- **Ranking:** geomean rel-L2 + an **ELO** from per-dataset pairwise wins (500 random orderings).
- **Baseline fairness rule:** crashing external SOTA (mfrnp, mf_deeponet, d_mfd) were fixed
  to *run* on every dataset by **hyperparameters/data only — never architecture changes**.
- **Backbone isolation:** all in-tree FNO families share one geometry-general spectral
  backbone (rectangular- & 1-D-safe) so the comparison isolates the *MF mechanism*, not the net.

### 2.2 The 15 datasets (2 `chin_chun_*` excluded)
2-D square, 2-D rectangular (era5/pm_test), and 1-D PDEs. `d`=# parameters, `L`=# fidelity
levels, N_HF = HF train count.

| Dataset | PDE | d | L | HF grid (work) | N_HF | Regime |
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
| era5 | reanalysis 2-D | 12 | 9 | 721×1440 (128×256) | 65 | **hard** |
| pm_test | reanalysis 2-D | 12 | 9 | 721×1440 (128×256) | 65 | **hard** |

**Hard set (5):** ifc_poisson, era5, pm_test, burgers, burgers_param — where errors scramble.
**Geometry fix (2026-05-28):** the original FNO families only handled square grids; a
`resolve_grid` adapter + a guarded rectangular spectral conv generalized them to 1-D and
rectangular grids (a 2-D spectral conv on a `(1,L)` grid *is* a 1-D FNO). A `WORK_CAP=256`
keeps era5's 721×1440 tractable.
**Data audit (2026-06-09):** 7/8 generated datasets have rigorously-converged HF. The one
flaw — lid-driven cavity not at steady state — was fixed by regenerating it (`v2`,
Ghia-1982 validated) in `gen_cavity/`.

---

## 3. The shared FNO backbone (the engine in every in-tree model)

`lift → N FNO blocks → projection`. Each **FNO block** = a **spectral conv** (FFT → keep
the lowest ~12×12 Fourier modes → multiply each by a learned complex weight → inverse FFT)
in parallel with a **1×1 conv**, summed, then GroupNorm + GELU. The spectral path learns
global resolution-independent kernels; the 1×1 path captures local pointwise detail.
The families below differ only in **what extra signal rides into that backbone** and **how
it is trained** (LF→HF transfer schedule).

---

## 4. Model families (32 dirs; 30 in the final leaderboard)

ELO from `results/bench_elo.csv`; params/latency from `results/bench_compute.csv`; geomean
rel-L2 from `paper/leaderboard_table.csv` († = computed from `bench_metrics.csv`).

### (a) Transfer-learning FNO + variants — *the winners*
| Family | Mechanism | Params | ELO | geomean | Origin |
|---|---|---|---|---|---|
| **mf_fno_transfer_film** | Transfer FNO; `X` injected by per-block **FiLM** (γ(X),β(X), zero-init) instead of concat | 4.77M | **1819.7 (#1)** | **0.0082** | factory-tuned |
| **mf_fno_pinn_transfer** | FiLM-transfer **+ exact closed-form Poisson PDE-residual loss** on Poisson datasets | 4.77M | **1799.0 (#2)** | 0.006† | factory-built |
| mf_fno_transfer | Canonical published MF-FNO (pretrain LF → fine-tune HF; Lyu 2023 / GCS 2023) | 4.74M | 1616.1 (#8) | 0.0123 | hand/external |
| mf_fno_transfer_2m | Param-matched (2.67M) ablation — proves it's the *mechanism* not capacity | 2.67M | 1595.3 (#10) | 0.0125 | external |
| mf_fno_transfer_pinn | FiLM-transfer + operator-matching (Laplacian) loss — **not benchmarked** | — | — | — | factory |
| mf_fno_transfer_bar | FROZEN incumbent "bar" the factory had to beat — reference, not a competitor | — | — | — | frozen ref |

### (b) Hand-designed fusion FNOs
| Family | Mechanism | Params | ELO | geomean |
|---|---|---|---|---|
| fno_coreg_residual | 4 per-fidelity FNOs + MFRNP-style residual stack + coregionalization basis head | 2.37M | 1450 (#21) | 0.0179 |
| fno_mf_stack | 4 small FNOs, MFRNP residual stacking; HF FNO predicts δ on aggregated LF | 2.35M | 1485 (#17) | 0.0249 |
| fno_coreg_conditioned | Single HF FNO, FiLM-via-LayerNorm on fidelity index `m` *(factory exp12)* | 4.76M | 1559 (#13) | 0.0320 |
| fno_autoregressive | Kennedy–O'Hagan: HF = ρ·LF_pred + δ, ρ learned | 9.48M | 1450 (#22) | 0.0345 |
| fno_additive | Additive discrepancy: HF = LF_pred + δ (LF frozen) | 9.48M | 1452 (#18) | 0.0347 |
| fno_coregionalization | FNO + IFC continuous-fidelity coregionalization head, K=10 | 1.19M | 1451 (#20) | 0.0557 |
| fno_coreg_lf_hf_transfer | Coregionalization head under a 2-stage LF→HF transfer schedule *(factory exp7)* | 1.19M | 1451 (#19) | 0.0575 |
| fno_multilevel | Le Gratiet recursive co-kriging cascade, one FNO/level | 18.96M | 1338 (#25) | 0.1389 |

### (c) FIRE-style distribution-conditioned / UQ families
Field analog of FIRE (Yu, Sung, Ahmed 2026, arXiv:2601.22371): an LF *uncertainty
distribution* (μ, σ, quantiles) conditions the HF correction. HF = μ_LF + δ(x, [μ,σ,q10,q50,q90]).
The ablation isolates the **uncertainty source**.

| Family | Uncertainty source | Params | ELO | geomean† |
|---|---|---|---|---|
| **fno_fire_distcond** | Deep ensemble of 5 LF-FNOs — **the keeper** | 28.4M | **1671 (#3)** | 0.0274 |
| fno_fire_snapshot | Snapshot ensemble (cyclic LR) | 28.4M | 1643 (#4) | 0.0269 |
| fno_fire_batchens | Multi-head batch ensemble | 9.50M | 1633 (#5) | 0.0292 |
| fno_fire_mdn | Mixture density network | 9.48M | 1626 (#6) | 0.0230 |
| fno_fire_iqn | Implicit quantile network | 9.48M | 1619 (#7) | 0.0229 |
| fno_fire_quantile | Pinball quantile regression | 9.48M | 1603 (#9) | 0.0248 |
| fno_fire_laplace | Last-layer Laplace | 9.48M | 1585 (#11) | 0.0264 |
| fno_fire_swag | SWAG weight posterior | 9.48M | 1567 (#12) | 0.0297 |
| fno_fire_cqr | Snapshot ens. + conformal calibration | 28.4M | 1547 (#14) | 0.0303 |
| fno_fire_dkl | Deep-kernel last-layer GP | 9.48M | 1524 (#15) | 0.0269 |
| fno_fire_mcdropout | Single FNO, MC-dropout — **honest negative** | 9.48M | 1368 (#24) | 0.0438 |

### (d) DINO / foundation-model families
| Family | Mechanism | Params | ELO | geomean† |
|---|---|---|---|---|
| fno_dino_residual | Frozen DINOv2-base CLS embedding of the LF field conditions the HF δ — **honest negative** | 9.54M | 1502 (#16) | 0.0409 |
| fno_dino_cond | Same idea, direct-prediction path — **not benchmarked** | — | — | — |

### (e) Attention / Transformer
| Family | Mechanism | Params | ELO | geomean |
|---|---|---|---|---|
| transolver_residual | Transolver cross-fidelity attention as a residual | 0.70M | 1392 (#23) | 0.0825 |
| transolver_attention_fusion | Iterated stacked cross-fidelity attention | 2.28M | 1337 (#26) | 0.0821 |

### (f) External SOTA baselines
| Family | Mechanism | Params | ELO | geomean |
|---|---|---|---|---|
| mfrnp | Multi-Fidelity Residual Neural Processes (Niu 2024) | 2.60M | 1287 (#27) | 0.2491 |
| d_mfd | Disentangled MF Deep Bayesian AL (Wu 2023) | 2.52M | 1260 (#28) | 0.4087 |
| mf_deeponet | Multifidelity DeepONet (Lu 2022) | 0.54M | 1197 (#29) | 0.2014 |

### (g) Prior baseline
| Family | Mechanism | Params | ELO | geomean |
|---|---|---|---|---|
| v9_baseline | Frozen MFTransolver_v9, point-wise gated LF-stream fusion | 0.43M | 1176 (#30, last) | 0.1188 |

### (h) Hybrid, under investigation (not benchmarked)
- **dg_fno / dg_transfer** — "discrepancy-gated FNO": LF uncertainty fields *modulate* the
  HF operator via spatial-FiLM + spectral-mode-gate, zero-init so they start as
  `mf_fno_transfer_film` / `fno_fire_distcond`. The explicit fusion of the #1 (FiLM) and #3
  (FIRE) ideas. See `models/DG_INVESTIGATION.md`.

---

## 5. Results summary

- **ELO ≈ geomean, but not identical.** FIRE-distcond ranks #3 by ELO yet has higher mean
  error than plain Transfer (#8) — ELO rewards consistent head-to-head wins; geomean is
  wrecked by catastrophic columns.
- **The Poisson scale-collapse is the discriminator.** On `ifc_poisson`, FIRE (22.9), DINO
  (19.4) and DeepONet (13.9) blow up >1000×; transfer/FiLM stay ~0.02 because of the
  **per-stage output scaler**. Errors >1.0 = worse than predicting zero.
- **Everyone is excellent on smooth diffusion datasets** (1e-3…1e-2); discriminating power
  lives entirely in the hard block. `mf_fno_transfer_film` is the only model with no
  catastrophic column — robustness, not peak accuracy, is why it's #1.

Figures produced this session: `results/plots/story_elo_vs_error.png` (ELO vs error bars,
7 representative models) and `results/plots/story_error_heatmap.png` (model×dataset heatmap).

---

## 6. The autonomous factory run

`factory_mffp` was wired as a **remote-factory** autonomous research loop (CEO → Scrummaster
→ Failure-Analyst → Researcher → Strategist → Builder → Reviewer → Evaluator → Archivist
agents, each a Claude API call) whose goal was to **invent a model family that beats the
frozen `mf_fno_transfer_bar`** on a 2-dataset smoke metric (`composite_nRMSE` = geomean of
ifc_heat + ifc_poisson nRMSE; bar ≈ 0.0274).

**Surfaces:** mutable = `models/**` only; fixed = `data/ baselines/ eval/ references/
scripts/ factory.md`. Per-cycle smoke ≤ ~30 min on one GPU. Hypothesis budget `max_new 2`.

### 6.1 Run timeline (from `.factory/events.jsonl`, `.factory/results.tsv`)
- 637 events spanning 2026-05-15 → 2026-06-02; 18 cycles started, **7 completed, 12 aborted**
  (all `consecutive_agent_failures`), 41 `agent.failed`.
- **14 experiments finalized — all 14 verdicts = `revert`** (none auto-merged; `--no-github`
  kept every attempt on a branch for human review).
- Three launch epochs: (1) 2026-05-15 tmux/login run (cycles 1–5, partial); (2) 2026-05-16
  login run (0 productive cycles — the no-GPU hang); (3) 2026-06-02 GPU sbatch retries
  (jobs 15320085, 15333937), each `--max-cycles 10` but **each delivered only 1 cycle**
  before hitting the Claude API rate limit.

### 6.2 Best-score trajectory (`composite_nRMSE`, lower better)
`baseline 1.6595 → exp1 0.1092 → exp4 0.0442` (first to beat IFC paper geomean 0.0516) `→
exp7 0.0294` (first sub-0.030) `→ exp11 0.0277 → exp14 0.0222` — **the bar (0.0274) was
beaten by 19.2 %** at experiment 14. *On its own smoke metric, the factory succeeded.*

### 6.3 What the factory built (and what survived into the real benchmark)
| Factory family | What it tried | Fate |
|---|---|---|
| fno_mf_stack | per-fidelity FNOs + MFRNP residual stack; exp14 capacity bump dethroned the bar | **survived** (#17) |
| fno_coreg_residual | coreg basis head + residual stack | **survived** (#21) |
| fno_coregionalization | IFC continuous-m coregionalization head | **survived** (#20) |
| fno_coreg_lf_hf_transfer | coreg + 2-stage LF→HF transfer (exp7) | **survived** (#19) |
| fno_coreg_conditioned | FiLM-on-fidelity single HF FNO (exp12) — reverted on Poisson | **survived** (#13) |
| fno_fire_distcond + 10 variants | FIRE distribution-conditioning | **survived — #3 keeper** + ranks 4–15 |
| fno_dino_residual | frozen DINO embedding conditioning | **survived as honest negative** (#16) |
| transolver_residual / _attention_fusion | cross-fidelity attention | **survived** (#23, #26) |
| fno_fire_hetero, fno_fire_ar1, fno_dino_cond, fno_mf_shared_trunk, fno_mf_stack_hfplus, fno_mf_stack_consistency | heteroscedastic / AR1 / shared-trunk / consistency-loss attempts | **abandoned** (branch only) |

### 6.4 Why the loop struggled (infra, not research)
1. **No-GPU login-node hang:** `score.py`'s CUDA probe hung on the contended login node
   until every agent timed out → the 2026-05-16 epoch committed 0 cycles. Fix: run the loop
   *inside* a GPU SLURM job (`bench/factory_gpu.sbatch`).
2. **Claude API rate limit:** each GPU job ran only 1 of its 10 budgeted cycles before
   "You've hit your limit". This, not GPU/walltime, was the binding constraint.
3. **Broken verdict bookkeeping:** all 14 finalized verdicts were forced `revert` by a
   precheck subsystem (inverted score polarity for lower-is-better, false leakage hits on
   dataset names in `factory.md`). The CEO logged "8th consecutive revert_bookkeeping_keep_intent"
   and flagged it for the operator. Real improvements were preserved by hand off the branches.
4. **Genuine correct reverts:** exp5/8/10 (MFRNP Poisson recipe not backbone-portable),
   exp12 (FiLM-on-HF falsified on Poisson), exp13 (frozen-LF curriculum tripped the kill-switch).
5. **Checkpoint-resume contamination** (stale ckpt "trained" Poisson in ~25 s) → fixed by a
   `recipe_hash` checkpoint guard (`models/_common/recipe_hash.py`).

### 6.5 Net assessment
- **Smoke metric: YES**, the factory beat `mf_fno_transfer_bar` (0.0222 vs 0.0274, −19 %).
- **Full benchmark: the factory did NOT invent the overall #1.** `mf_fno_transfer_film`
  (FiLM) and `mf_fno_pinn_transfer` — the eventual #1/#2 — postdate the bounded loop and have
  no factory cycle row; they are best read as **human-driven follow-up** (FiLM was promoted to
  the paper's headline method on 2026-06-10).
- **The factory's real, durable contribution is the FIRE family — `fno_fire_distcond` at #3**,
  the keeper — plus several mid-table fusion families and two instructive honest negatives
  (DINO, MC-dropout).

---

## 7. Hardening experiments

| Exp | Question | Method | Result |
|---|---|---|---|
| **EXP1 few-shot-HF** | Does transfer's edge grow as HF data shrinks? | transfer vs additive vs hf_only, N_HF∈{5,10,25,50,100} × 4 datasets × 3 seeds | **Raw JSONs only** (`results/raw_fewshot/`); no aggregate CSV/plot yet. FiLM version is **TODO/unrun**. Paper describes qualitatively. |
| **EXP2 regime split** | Is "transfer wins" universal or conditional? | geomean rel-L2 per regime (smooth=10, hard=5) | **Strong & key figure.** Concat-transfer #1 smooth (2.5e-3) but overtaken on hard by fno_coreg_residual (0.208 vs 0.223). *FiLM later wins BOTH regimes, removing the caveat.* CSV is **pre-FiLM**. |
| **EXP3 pairing** | Does transfer's edge scale with N_LF/N_HF mismatch? | correlate transfer advantage vs mismatch ratio | **Dropped, inconclusive** (Pearson 0.13; 13/15 datasets have N_LF=N_HF so no variance). |

Files: `results/exp2_regime_split.csv` + `plots/exp2_regime_split.png`;
`results/exp3_pairing.csv` + `plots/exp3_pairing_scatter.png`; `fewshot/` harness.

---

## 8. The paper

- **Location:** `paper/main.tex`, `paper/paper_draft.md`, compiled `paper/main.pdf`;
  figures via `paper/make_figures.py` → `paper/figures/`.
- **Title** (main.tex): *"A Multi-Fidelity Fourier Neural Operator via FiLM-Conditioned
  Transfer Learning"*, subtitle *"Conditioning, not fusion, is what multi-fidelity neural
  operators need."*
- **Thesis (exact):** the central question is *"how should the parameter vector be injected
  into the operator at all?"* — "the default — broadcasting it to constant channels and
  concatenating — wastes the FNO's spectral machinery, because a spatially constant field
  carries all its energy in the k=0 mode."
- **Contributions:** (1) controlled concat-vs-FiLM study on a byte-identical backbone;
  (2) new SOTA at geomean 0.0082, #1 ELO, 14/15 wins; (3) regime analysis showing FiLM wins
  both smooth and hard; (4) honest novelty positioning vs concurrent FiLM-FNO work
  (Zhu 2025 arXiv:2511.09729; Shokar 2025 arXiv:2509.09599) — "first to use FiLM for
  *multi-fidelity transfer* in static parameter→field."
- **Figures:** fig_leaderboard, fig_per_dataset_errorbars, fig_regime_split,
  fig_film_vs_concat_ratio, fig_elo.

---

## 9. Open items & known discrepancies

1. **ELO number is stale in the paper.** Paper text says FiLM ELO **1936 (215–17)** over
   ≤17 methods; the live 30-model `results/bench_elo.csv` says **1819.7 (353–66–2)**. Update
   before submission.
2. **EXP2 CSV is pre-FiLM.** The paper's regime table (FiLM #1 in both) is recomputed via
   `make_figures.py`/`leaderboard_table.csv`, not from `exp2_regime_split.csv`. Regenerate
   the CSV/plot with FiLM included.
3. **EXP1 (few-shot) unfinished** — raw JSONs exist but no aggregate/plot, and the FiLM arm
   is unrun. This is the highest-value remaining experiment (predicts transfer's margin grows
   under HF scarcity).
4. **`dg_fno`/`dg_transfer`** (FiLM × FIRE hybrid) are built but not yet benchmarked — the
   natural next family to evaluate.
5. **Lid-driven-cavity `v2`** (steady-state, Ghia-validated) should be re-benchmarked across
   families and the row updated in all plots.
6. **Op notes:** pi_faez `node2901` is faulty (hangs jobs silently — always `--exclude=node2901`);
   never run the factory loop and bench jobs concurrently on the same checkout (factory parks
   the tree on an experiment branch mid-run).
