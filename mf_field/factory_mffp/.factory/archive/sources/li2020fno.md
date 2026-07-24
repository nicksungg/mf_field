---
name: li2020fno
description: Fourier Neural Operator. Canonical operator-learning architecture for regular-grid PDE data. Recommended backbone for both H1 (fno_coregionalization) and H2 (fno_mf_stack) in cycle 001.
metadata:
  type: reference
tags:
  - factory
  - source
  - paper
  - backbone
source: factory-archivist
date: 2026-05-15
bibtex_key: li2020fno
---

# li2020fno — Fourier Neural Operator for Parametric PDEs

**Authors**: Li et al.
**Link**: [arXiv:2010.08895](https://arxiv.org/abs/2010.08895)

## Why this paper matters

FNO is the canonical operator-learning architecture for **regular-grid PDE data** — resolution-invariant by design. The `ifc_heat` and `ifc_poisson` datasets are both regular-grid PDE data → FNO is the natural backbone.

## Why FNO beats Transolver here

- `ifc_*` data lives on uniform grids (8×8 → 16×16 → 32×32 → 64×64).
- [[wu2024transolver]]'s slice-attention is designed for *unstructured meshes* → O(N·K) per-sample with K slice clusters, adds cost without inductive-bias benefit on a regular grid.
- FNO's spectral conv is **O(N log N) per FFT** with much smaller hidden state; 64×64 FFTs are essentially free on H100.

## How to use in cycle 001

- **Backbone for both H1 (fno_coregionalization) and H2 (fno_mf_stack)**.
- H1 concrete: 3–4 spectral conv blocks, k_max=12, hidden_channels=64, output as low-dim latent grid h(x) ∈ R^{K × H × W} with K=10–20.
- H2 concrete: one FNO per fidelity level, smaller (~50k params each).

## Cross-cutting finding propagated

**FNO is a strict upgrade over Transolver for these specific datasets** — see [[cycle-001-cross-cutting-findings]]. v9 used Transolver; this is one of the two structural reasons v9 has a 2× gap on ifc_heat (the other being no continuous fidelity index).

## Related

- [[li2022ifc]] — pairs FNO with coregionalization for H1.
- [[niu2024mfrnp]] — pairs FNO with residual stacking for H2.
- [[wu2024transolver]] — v9's backbone, deprecated for regular-grid datasets.
