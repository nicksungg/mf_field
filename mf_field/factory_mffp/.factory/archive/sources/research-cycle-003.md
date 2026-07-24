---
name: research-cycle-003
description: Cycle-003 Mode-4 web research on HF/LF loss reweighting in multi-fidelity training — theory, PDE-class dependence, adaptive alternatives, and provenance of MFRNP's hand-tuned (2.0, 0.25) Poisson weights
metadata:
  type: reference
tags:
  - factory
  - source
  - research
  - cycle-003
  - loss-weighting
  - multi-fidelity
project: factory_mffp
cycle: 003
source: factory-archivist
date: 2026-05-15
---

# Research — Cycle 003: Per-Fidelity Loss Reweighting in MF Training

**Date:** 2026-05-15.
**Trigger:** R1 Failure Analyst named `ABSENT_POISSON_LOSS_WEIGHTING` as the *sole* remaining failure mode after cycle-002 H3. H3 holds the Heat win (0.02634, 2.81× under paper bar) but misses Poisson (0.07416 vs 0.036, 2.06× over) and regresses 25% vs H4's Poisson (0.0596) because H3 ships the per-fidelity loss-weight knob `OFF` in the smoke harness.
**CEO Verdict:** PROCEED (publish-quality). H1 only this cycle; defer GradNorm to cycle-004.
**Related notes:** [[niu2024mfrnp]], [[li2022ifc]], [[research-cycle-002]], [[cycle-001-cross-cutting-findings]].

---

## (Q1) Theoretical Grounding — Four Convergent Lenses for HF Up-weighting

No single canonical theory motivates the practice; four substantively-different lenses each prescribe HF up-weighting / LF down-weighting in MF training. The empirical (2.0, 0.25) numbers are *consistent with* all four but derived from none.

1. **Control-variate / variance-reduction view** — rooted in MF Monte Carlo ([Peherstorfer, Willcox, Gunzburger SIAM Review 2018](https://epubs.siam.org/doi/abs/10.1137/16M1082469)).
   Optimal CV coefficient α* = cov(LF, HF) / var(LF). Training-loss analogue: weight LF by the inverse of cross-fidelity variance ratio. Static (2.0, 0.25) is a static approximation to what an adaptive variance-normalized scheme would compute.

2. **Effective-sample-mass view** — folklore, matches IFC dataset structure exactly.
   `ifc_poisson` per-fidelity sample counts: `n_L1=100, n_L2=50, n_L3=20, n_L4=5`. Under uniform weighting, summed-batch MSE makes LF dominate gradient flow purely by sample count (L1 has 20× HF gradient mass). Setting (HF=2.0, LF=0.25) rebalances HF (n=5, weight=2) → 10 effective units vs L1 (n=100, weight=0.25) → 25. Simplest argument; requires no noise model.

3. **Multi-task learning view** — [Kendall, Gal, Cipolla 2018](https://arxiv.org/abs/1705.07115) (homoscedastic-uncertainty: `w_i = 1/(2σ_i²)` with learnable σ_i) and [Chen et al. 2018 GradNorm](https://arxiv.org/abs/1711.02257) (equalize ||∇L_i||·λ_i across tasks, single asymmetry hyperparam α). L_HF and L_LF are mathematically MTL losses over a shared backbone; both methods reduce to static weights at their fixed points but discover them from data. Neither has been benchmarked in MF-PDE.

4. **PINN gradient-pathology view** — [Wang, Teng, Perdikaris 2020](https://arxiv.org/abs/2001.04536) (LRA: λ_i ∝ max(|∇L_i|) / mean(|∇L_i|), 50–100× accuracy improvements on Helmholtz-class), [Wang 2021 NTK](https://arxiv.org/abs/2007.14527), [Liu 2025 NTK sketching](https://arxiv.org/abs/2511.15530). MF-applicable in principle (per-fidelity terms are extra "tasks"); not published in MF setting.

**Synthesis:** all four prescribe some form of HF up-weighting / LF down-weighting when LF is dominant by sample mass (lens 2), correlation-noise (lens 1), gradient magnitude (lens 4), or learned uncertainty (lens 3). The theoretical headroom over (2.0, 0.25) is the gap between hand-tuned static and adaptive — small in expectation (the Poisson5 hand-tuning was for this PDE class) but worth a low-cost test.

---

## (Q2) PDE-Class Dependence — The Smoking Gun is In-Code, Not In-Paper

The strongest empirical signal lives in MFRNP's own released YAMLs:

| Config file              | Task(s)                   | `fidelity_weight` (HF) | `lower_fidelity_weight` (LF) | Notes                       |
|---                       |---                        |---:                    |---:                          |---                          |
| `Poisson5_config.yaml`   | Poisson5 (5-fidelity)     | 2                      | **0.25**                     | The *only* config with LF≠1 |
| `pde_config.yaml`        | Heat5, Poisson2/3, Heat2/3| 2                      | 1.0                          | Default — uniform LF        |
| `Fluid_config.yaml`      | Fluid (5-fidelity)        | 2                      | 1.0                          | Bumps hidden=128 instead    |

Sources: [Poisson5_config.yaml](https://github.com/Rose-STL-Lab/MFRNP/blob/main/Poisson5_config.yaml), [pde_config.yaml](https://github.com/Rose-STL-Lab/MFRNP/blob/main/pde_config.yaml), [Fluid_config.yaml](https://github.com/Rose-STL-Lab/MFRNP/blob/main/Fluid_config.yaml). This is the **single strongest empirical signal** in the published MF literature that elliptic (Poisson) problems require LF down-weighting that other PDE classes (parabolic Heat, Navier-Stokes Fluid) do not.

**Three convergent threads explain why elliptic is different:**

- **Global support of elliptic operators** ([Boullé & Townsend PNAS 2023](https://www.pnas.org/doi/10.1073/pnas.2303904120)). Green's function for −∇² is globally supported — pointwise error anywhere couples to errors everywhere via the integral kernel. Heat (parabolic) operators have a *smoothing* property — local errors decay temporally; LF noise gets filtered. Elliptic: LF noise back-propagates globally to HF; LF must be suppressed more aggressively.
- **Stiffness in stationary problems** — [Wang 2020](https://arxiv.org/abs/2001.04536) explicitly identifies elliptic-class PDEs as the failure mode driving "gradient pathology." Elliptic residuals must balance across the entire domain at once; canonical PINN failure mode for Helmholtz/Poisson.
- **Value-scale collapse** (cycle-001 in-repo finding). HF target magnitudes ~40× smaller than LF on `ifc_poisson` (finite-difference normalization ∝ h²). H3's per-fidelity output normalization already addresses this — the remaining asymmetry is sample-count and SNR, not raw scale.

**Heat empirically doesn't need it.** MFRNP Heat5 uses uniform LF weight (`pde_config.yaml`). H4 in this repo uses uniform Heat weights; matches H2 on Heat (0.0999). H3 wins Heat by 2.81× under paper bar (0.02634) *without* loss reweighting — its basis-head inductive bias does the work.

**IFC paper caveat (a second SOTA route).** [Li, Wang, Kirby, Zhe NeurIPS 2022](https://arxiv.org/abs/2207.00678) reaches Poisson 0.036 with **uniform** per-fidelity weights — confirmed by [`infras/configs.py`](https://github.com/shib0li/Infinite-Fidelity-Coregionalization/blob/main/infras/configs.py): no `fidelity_weight` / `lower_fidelity_weight` field. IFC achieves Poisson SOTA via *architectural* asymmetry (continuous-m basis × low-dim latent + neural-ODE for B(m)) + 5000-epoch budget. **Two orthogonal paths to Poisson SOTA**: (a) MFRNP — discrete-fidelity residual stack + Poisson-specific loss reweighting + 50k epochs; (b) IFC — continuous-m architectural rescaling + uniform weights + 5k epochs.

---

## (Q3) Adaptive Alternatives — Ranked

| Method                                       | Reference                       | Mechanism                                                          | Cost on H3                        | Expected reduction vs (2.0, 0.25)     | Used in MF-PDE?           |
|---                                           |---                              |---                                                                  |---                                |---                                    |---                        |
| **Per-fidelity variance normalization**      | folklore / control-variate      | weight ∝ 1/Var(L_i) from moving window                              | ~20 LOC                           | Marginal — robustness gain            | No published MF-PDE work |
| **GradNorm**                                 | [Chen 2018](https://arxiv.org/abs/1711.02257) | Equalize ‖∇_θ L_i‖·λ_i across tasks; single α                       | ~50 LOC; backward/task            | Moderate — matches grid search in MTL | Not in MF-PDE; common MTL |
| **Homoscedastic uncertainty weighting**      | [Kendall 2018](https://arxiv.org/abs/1705.07115) | Loss = Σ (1/(2σ_i²)) L_i + log σ_i; learnable σ_i                  | ~10 LOC; 4 scalars                | Low — typically recovers static       | Not in MF-PDE; common MTL |
| **Learning-rate annealing (LRA)**            | [Wang 2020](https://arxiv.org/abs/2001.04536) | λ_i ∝ max(|∇L_i|)/mean(|∇L_i|) every K epochs                       | ~30 LOC; backward/term per K      | Moderate-high in PINN; unknown in MF  | PINN-only published       |
| **NTK-based weighting (sketched)**           | [Wang 2021](https://arxiv.org/abs/2007.14527), [Liu 2025](https://arxiv.org/abs/2511.15530) | λ_i ∝ 1/eigenvalue_i of NTK; sketching for O(N·d)                   | ~100 LOC                          | High in PINN literature; unknown MF   | PINN-only published       |
| **Ada2MF Adaptive Fast Weighting (AFW)**     | [Zhan 2024](https://www.sciencedirect.com/science/article/abs/pii/S0952197624012193) | Dynamic loss-weighting; exact formula paywalled                     | Unknown                           | Claims 66%/41% over MFNN baseline     | **Yes — MF-specific** (wind-turbine, not PDE) |
| **Curriculum / annealed weighting**          | folklore ([survey](https://arxiv.org/html/2410.13228v1)) | LF→HF dominance over epochs                                         | ~5 LOC                            | Speculative                           | Not specifically MF-PDE   |

**Bottom-line for cycle-003:**
- **Fixed (2.0, 0.25) is the EV-positive H1 mechanism.** Only option with measured in-repo cross-architecture evidence (H2→H4 on `fno_mf_stack`; pre-registered as a knob in H3's `full_config.json`).
- **GradNorm is the lowest-cost / highest-confidence adaptive upgrade** for H2 — but never benchmarked in MF-PDE, so result novel either direction. Cost: ~50 LOC.
- **Kendall uncertainty** = lowest cost, lowest upside (recovers static at convergence).
- **LRA / NTK** = PINN-class fixes, unproven in MF supervised-loss settings. Skip for cycle-003.
- **Ada2MF AFW** = only published MF-specific adaptive scheme but formula is paywalled → reproducibility risk.

---

## (Q4) Provenance of (2.0, 0.25) — Hand-tuned MFRNP, NOT in Paper

**Definitive answer: hand-tuned by the MFRNP authors, published only in the released YAML configs.**

Evidence:

1. **The MFRNP paper does not mention per-fidelity loss weighting.** Careful read of [arXiv:2402.18846v1](https://arxiv.org/html/2402.18846v1) returns zero hits for `fidelity_weight`, `lower_fidelity_weight`, `loss weighting`, or `per-fidelity weight` in methodology (Eqs. 5–7) or appendices. Verbatim from methodology: *"We choose to average over other aggregation methods because this stabilizes the aggregation and ensures the equal contribution of lower fidelity surrogates."*
2. **Values exist only in `Poisson5_config.yaml`.** Of three task-specific YAMLs in the MFRNP repo, only Poisson5 has `lower_fidelity_weight: 0.25`. The default `pde_config.yaml` (Heat5, Poisson2/3, Heat2/3) and `Fluid_config.yaml` ship `lower_fidelity_weight: 1`.
3. **No ablation table in the paper.** Table 3 (only ablation) compares MFRNP vs MFRNP-H (hierarchical variant) — not loss weights.
4. **Single inline comment** in `Poisson5_config.yaml`: `"# highest fidelity weight"` next to `fidelity_weight: 2`. No rationale offered for the (2, 0.25) split.

**Operational implication:**
- (2.0, 0.25) is **empirically calibrated for the MFRNP Poisson5 setup** (5 fidelities 8/16/32/64/128); unpublished sweep.
- IFC Poisson is a 4-fidelity setup (8/16/32/64); recipe transfers via *similarity of inductive setting* (Poisson-class, value-scale-collapse, geometric refinement), not by re-derivation.
- In-repo measurement: H4's port produced 0.0596 on 4-fidelity IFC Poisson with FNO backbone — **strongest external validation**. Recipe survives:
  - Backbone change (NP → FNO)
  - Fidelity count change (5 → 4)
  - Train-set size change (different per-fidelity ns)
- Consistent with [[patterns]] §"MFRNP Poisson5_config.yaml knobs are inductive-bias-agnostic" — the recipe is **PDE-class-bound, not backbone-bound**.
- **For other Poisson-class datasets** (when smoke suite expands), (2.0, 0.25) must be re-validated. If a future dataset has 50 HF samples (not 5), the optimal weights may shift — an adaptive scheme becomes attractive at that scale.

---

## Critical Compositional Argument

**H3 already provides IFC-path architectural asymmetry** (continuous-m basis head `B(m)`, zero-init residual, decoder-in-the-aggregation, coregionalization on HF latent). **Cycle-003 H1 adds MFRNP-path loss-weighting asymmetry** (HF=2.0, LF=0.25, Poisson-only).

**This is the first time in this project both SOTA routes are composed on the same model.** The two paths are orthogonal:
- IFC's continuous-m basis × low-dim latent operates at the **architectural** level (gradient signal allocation across fidelities is fixed by structure).
- MFRNP's HF/LF reweighting operates at the **loss** level (gradient signal allocation across fidelities is reweighted post-architecture).

Either path alone produces Poisson SOTA against the paper bar in its source paper. Their composition has no published precedent — cycle-003 H1 is the first measurement.

**Expected effect** (anchored to *measured*, not forecast):
- `ifc_poisson` lands at H4 level (≈0.0596) at minimum; H3's basis-head + capacity advantage plausibly does better.
- `ifc_heat` unchanged at ~0.02634 (Poisson-only override doesn't touch Heat path).
- **Composite floor (H4-Poisson parity):** geomean(0.02634, 0.0596) ≈ **0.0396** (−10% vs cycle-002 H3's 0.0442).
- **Composite stretch:** ≈0.030–0.035 (both datasets near/below paper bar).
- **Risk:** low. Purely additive on top of known-good H3 baseline. Only failure mode is the override accidentally activating on Heat path.

---

## New Bibtex Citations Proposed (7 entries)

Pending creation of `papers_summary.csv` at repo root (human action). For cycle-003, inline bibtex citations in `models/fno_coreg_residual/INSPIRATION.md` is the correct path.

| bibtex_key                  | reference                                                                                       | role in cycle-003 |
|---                          |---                                                                                              |---                |
| **chen2018gradnorm**         | [ICML 2018, arXiv:1711.02257](https://arxiv.org/abs/1711.02257)                                | Q1 lens 3 + Q3 H2 reference for adaptive MF loss weighting (cycle-004) |
| **kendall2018uncertainty**   | [CVPR 2018, arXiv:1705.07115](https://arxiv.org/abs/1705.07115)                                | Q1 lens 3 + backbone of any future learnable-weight MF family |
| **wang2020gradpathologies**  | [SIAM SISC 2021, arXiv:2001.04536](https://arxiv.org/abs/2001.04536)                           | Q1 lens 4 + Q2 stiffness argument for elliptic-class HF up-weighting |
| **wang2021ntkpinn**          | [J. Comput. Phys. 2022, arXiv:2007.14527](https://arxiv.org/abs/2007.14527)                    | Q1 lens 4 NTK formulation |
| **boulle2023ellipticdata**   | [PNAS 2023, DOI:10.1073/pnas.2303904120](https://www.pnas.org/doi/10.1073/pnas.2303904120)     | Q2 Green's-function global support — why elliptic is different |
| **zhan2024ada2mf**           | [Eng. Appl. AI 2024](https://www.sciencedirect.com/science/article/abs/pii/S0952197624012193)  | Q3 only MF-specific adaptive scheme (paywalled — reproducibility risk) |
| **mfrnp_poisson5_config**    | [Rose-STL-Lab/MFRNP/Poisson5_config.yaml](https://github.com/Rose-STL-Lab/MFRNP/blob/main/Poisson5_config.yaml) | Q4 provenance citation — source artifact for (HF=2.0, LF=0.25) |

---

## CEO Preference — H1 Only This Cycle

**Defer GradNorm (H2) to cycle-004** for cleaner attribution. Rationale: cleanly attribute the composite move from cycle-003 H1; cycle-004 then has a known H1-only baseline to compare GradNorm against. The hypothesis_budget.max_new=2 allowance is not exercised this cycle on CEO instruction.

---

## Strategist Hand-off (R2)

**H1 (REQUIRED):**
- Port `resolve_fidelity_weights(dataset_name, p)` from `models/fno_mf_stack/smoke_eval.py` into `models/fno_coreg_residual/smoke_eval.py`.
- Defaults: `poisson_hf_weight=2.0`, `poisson_lf_weight=0.25` (verbatim MFRNP Poisson5 values).
- Wire into existing `compute_losses` call. Heat path uniform (unchanged).
- Update `models/fno_coreg_residual/INSPIRATION.md` to cite `mfrnp_poisson5_config` and articulate the IFC-path × MFRNP-path compositional argument.
- Verify surface constraint: only `models/fno_coreg_residual/**` modifications.
- Verify leakage scan: hypothesis is about gradient allocation, not ground truth — should pass cleanly.

**H2 (OPTIONAL, deferred):** GradNorm-lite. CEO preference is single hypothesis. Save for cycle-004.
