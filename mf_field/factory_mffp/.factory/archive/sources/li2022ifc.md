---
name: li2022ifc
description: Source paper for ifc_heat / ifc_poisson datasets. Continuous-fidelity coregionalization f(x,m)=B(m)·h(x,m) with neural-ODE basis. Paper bar at m=1 — Poisson 0.036, Heat 0.074.
metadata:
  type: reference
tags:
  - factory
  - source
  - paper
  - core-mf
source: factory-archivist
date: 2026-05-15
bibtex_key: li2022ifc
---

# li2022ifc — Infinite-Fidelity Coregionalization for Physical Simulation

**Authors**: Li, Wang, Kirby, Zhe. NeurIPS 2022.
**Links**: [arXiv:2207.00678](https://arxiv.org/abs/2207.00678), [OpenReview PDF](https://openreview.net/pdf?id=dUYLikScE-)

## Why this paper matters for cycle 001

This is **the** source paper for the `ifc_heat` and `ifc_poisson` datasets used in our smoke suite. The dataset construction protocol (4 train fidelities at 8×8/16×16/32×32/64×64 with ns=[100,50,20,5], 128 test examples at 64×64, fidelity index m∈[0,1] mapped linearly from mesh size) confirmed identical to this repo's data (matches `cat.pkl t_list = [0.0, 0.143, 0.429, 1.0]` exactly).

## Architecture summary

- Continuous fidelity index `m ∈ [0,1]`.
- Output decomposition: `f(x, m) = B(m) · h(x, m)`, where `B(m) ∈ R^{K×1}` is a basis matrix and `h(x,m) ∈ R^K` is a low-dim latent representation.
- Two variants: **IFC-ODE2** uses a neural ODE for B(m); **IFC-GPODE** uses Gaussian processes for B(m).
- K (latent dim) sweep ∈ {5, 10, 15, 20}; results averaged over 5 seeds.
- Per-pass ODE solver is expensive (~7.84 s/epoch for K=20 on Poisson at 64×64).

## Numbers (from p.9 verbatim text)

> "The nRMSE of IFC-ODE2 at m=1 and m=2.14 is 0.036 vs. 0.018 and 0.074 vs. 0.061, for Poisson's and Heat equations, respectively."

- **ifc_poisson, m=1, K=20**: IFC-ODE2 → **0.036**, IFC-GPODE ~**0.03** (from Fig. 4(a)).
- **ifc_heat, m=1, K=20**: IFC-ODE2 → **0.074**, IFC-GPODE ~**0.04** (from Fig. 4(b)).
- **Paper std**: not explicitly stated; Fig. 1 error bars ≈ ±0.005 (estimated, must be flagged if used).

## How to use in cycle 001

- These numbers should be appended to `baselines/paper_baselines.json` as the "paper bar" for `ifc_heat` / `ifc_poisson`. **Human action** — Researcher cannot edit fixed surface. See [[paper-baselines-proposals]].
- Architectural template for **H1: fno_coregionalization**. The expensive neural-ODE basis is replaced with a cheap MLP `B(m) = MLP([m, m²])` to fit the 30 min H100 smoke budget. See [[cycle-001-candidate-ranking]].

## Caveats

- v9 baseline currently sits at **18.50 / 0.149** on ifc_poisson / ifc_heat — **~500× / 2× worse** than IFC-ODE2 at m=1.
- The proposed split key in this paper terms is `test_l4` (clarity), but `eval/score.py` likely uses `"test"` — verify before committing to baselines JSON.

## Related

- [[li2020fno]] — Fourier Neural Operator, the recommended backbone for coregionalization in cycle 001.
- [[niu2024mfrnp]] — alternative MF architecture (residual stacking) used in H2.
- [[cycle-001-failure-diagnosis]] — diagnosis that F1 is value-scale collapse; this paper's continuous-m basis is the architectural fix.
