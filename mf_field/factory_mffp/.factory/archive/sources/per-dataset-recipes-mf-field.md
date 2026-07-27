---
name: per-dataset-recipes-mf-field
description: Empirical evidence that heat-equation and Poisson-equation MF training benefit from different loss-weight recipes — MFRNP YAML splits, IFC paper, and recent MF-NP work
metadata:
  type: reference
tags:
  - factory
  - source
  - mfrnp
  - per-dataset-recipe
  - loss-weighting
source: factory-archivist
date: 2026-06-02
cycle: cycle-007
---

# Per-Dataset Training Recipes for Multi-Fidelity Field Prediction

Compiled during cycle-007 R1.5 to back the Top-2 hypothesis: decoupling
`fno_coreg_residual` recipes per `args.dataset_name` so a knob that helps
Heat doesn't degrade Poisson. Reaffirms and consolidates findings already
documented in [[research-cycle-003]] / [[research-cycle-006]].

## Headline finding

**Elliptic-class PDEs (Poisson) and parabolic-class PDEs (Heat) need
different loss-weighting recipes.** MFRNP's repository ships **three
separate YAML configs**, split on PDE-class / fidelity-count:

| Config | Recipe | PDE class |
|---|---|---|
| [`Poisson5_config.yaml`](https://github.com/Rose-STL-Lab/MFRNP/blob/main/Poisson5_config.yaml) | `fidelity_weight: 2`, `lower_fidelity_weight: 0.25` | Poisson 5-fid (elliptic) |
| [`pde_config.yaml`](https://github.com/Rose-STL-Lab/MFRNP/blob/main/pde_config.yaml) | uniform weights | Heat5 + Poisson2/3 + Heat2/3 (mixed) |
| [`Fluid_config.yaml`](https://github.com/Rose-STL-Lab/MFRNP/blob/main/Fluid_config.yaml) | uniform weights | Navier–Stokes |

This is direct in-code evidence that **per-task hyperparameter sets are
the published norm**, not the exception. The (HF=2.0, LF=0.25) recipe is
**specific to elliptic Poisson** — it is NOT a universal MF recipe.

## Theoretical lenses (4 convergent; carried from cycle-003)

1. **Effective sample-mass view.** With per-fidelity counts
   `n_L1=100, n_L2=50, n_L3=20, n_L4=5`, uniform-weighted summed-batch MSE
   makes LF dominate gradients by sample count (L1 has 20× HF gradient
   mass). (HF=2.0, LF=0.25) rebalances to HF≈10 effective units vs
   L1≈25 — close to parity.
2. **Green's-function / global-support view.** `boulle2023ellipticdata`
   ([DOI:10.1073/pnas.2303904120](https://www.pnas.org/doi/10.1073/pnas.2303904120)):
   the Green's function for `−∇²` is globally supported — pointwise error
   anywhere couples to errors everywhere via the integral kernel. Heat
   (parabolic) operators have a smoothing property; LF errors decay
   temporally. **Elliptic LF noise back-propagates globally to HF; LF
   must be suppressed more aggressively.**
3. **Gradient-pathology view.** `wang2020gradpathologies`
   ([arXiv:2001.04536](https://arxiv.org/abs/2001.04536)): elliptic-class
   PDEs are the named failure mode driving PINN "gradient pathology".
   Elliptic residuals must balance across the entire domain at once.
4. **Empirical precedent in-repo.** The (HF=2.0, LF=0.25) recipe was
   ported to `fno_mf_stack` (cycle-003 H4) and produces **0.05961 on
   ifc_poisson at smoke** — confirming the recipe survives backbone change
   (NP → FNO) and fidelity-count change (5 → 4).

## IFC paper: a separate Poisson-SOTA path

- **Citation**: `li2022ifc` — [arXiv:2207.00678](https://arxiv.org/abs/2207.00678).
- IFC achieves **Poisson 0.036 SOTA with uniform weights** — but via
  architectural asymmetry (continuous-m basis + neural-ODE) **plus**
  a **K=20** basis budget and a **5000-epoch** training run.
- Two orthogonal Poisson-SOTA paths exist in the literature:
  - (a) **MFRNP-style reweighting** (HF=2.0, LF=0.25) — recipe-only.
  - (b) **IFC-style** (architectural asymmetry + long training).
- Smoke wall-time budget (≤30 min / family / dataset) **rules out the
  IFC 5k-epoch path** → cycle-007 leans on MFRNP-style reweighting.

## Recommended `_DATASET_RECIPES` dispatch (cycle-007 Focus 2)

```python
_DATASET_RECIPES = {
    "ifc_heat":    dict(pretrain_frac=0.40, pretrain_lr=1e-3, finetune_lr=3e-4, K=20),
    "ifc_poisson": dict(pretrain_frac=0.0,  pretrain_lr=3e-4, finetune_lr=3e-4,
                        poisson_hf_weight=2.0, poisson_lf_weight=0.25, K=20),
}
```

Merged into local `p` inside `run(args)` based on `args.dataset_name`.
Default-fallback path preserves current `SMOKE_DEFAULTS` — **cannot regress**
on a dataset that isn't keyed.

Applies to: `fno_coregionalization/smoke_eval.py` (heat path benefits from
longer LF dose; Poisson explicitly disables H2 since cycle-006 found H2
didn't help on Poisson for this family) AND `fno_coreg_residual/smoke_eval.py`
(Poisson path lands the MFRNP `(2.0, 0.25)` recipe that has been scoped
for three cycles and never landed).

## In-tree precedent

- `fno_mf_stack/smoke_eval.py:84-85, 326-330` ships
  `poisson_hf_weight=2.0, poisson_lf_weight=0.25` and a
  `resolve_fidelity_weights(dataset_name, p)` dispatcher. **This pattern
  is already accepted in-tree** — porting it to `fno_coreg_residual` is
  copy/paste with the same dispatch logic.
- `fno_coreg_residual/smoke_eval.py:465` currently ships
  `p["lf_loss_weights"] = tuple([1.0] * (n_levels - 1))` (uniform across
  ALL datasets including Poisson).
- `fno_coreg_residual/full_config.json` already declares a
  `_poisson_loss_knob` (HF=2.0, LF=0.25) but the smoke harness never
  reads it.

## Newly surfaced this cycle (cycle-007 web round)

- **No new published direct PDE-class-conditional MF reweighting paper
  surfaced.** The MFRNP 3-YAML evidence remains the single strongest
  signal.
- Adaptive per-task weighting (`chen2018gradnorm` —
  [arXiv:1711.02257](https://arxiv.org/abs/1711.02257), `kendall2018uncertainty` —
  [arXiv:1705.07115](https://arxiv.org/abs/1705.07115)) addresses the same
  problem **adaptively** but costs more and has no MF-PDE-specific
  variant. **Deferred.**

## Related notes

- [[research-cycle-003]] — original 20-citation Mode-4 sweep on HF/LF
  loss reweighting; all primary citations preserved.
- [[research-cycle-006]] — cycle-006 reframing as
  `PDE_CLASS_ARCH_RECIPE_COUPLING` (dominant failure mode).
- [[niu2024mfrnp]] — MFRNP decoder-in-the-aggregation residual stacking;
  source of the (HF=2.0, LF=0.25) recipe.
- [[li2022ifc]] — IFC paper, K=20 + 5000 epoch alternative Poisson-SOTA path.
- [[failure-analysis-cycle-007]] — diagnoses the recipe-overfit-across-datasets
  failure on `fno_coreg_residual` Poisson (+33.5% regression vs cycle-005).
