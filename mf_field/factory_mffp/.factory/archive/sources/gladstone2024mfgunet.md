---
name: gladstone2024mfgunet
description: Multi-Fidelity Graph U-Net for physics simulations. GNN backbone with multigrid-style coarsening. Less directly applicable than FNO for regular-grid ifc_* data — deferred this cycle.
metadata:
  type: reference
tags:
  - factory
  - source
  - paper
  - mf-graph
source: factory-archivist
date: 2026-05-15
bibtex_key: gladstone2024mfgunet
---

# gladstone2024mfgunet — A Multi-Fidelity Graph U-Net Model for Accelerated Physics Simulations

**Authors**: Gladstone, Meidani.
**Link**: [arXiv:2412.15372](https://arxiv.org/abs/2412.15372)

## Why this paper matters (limited)

Graph U-Net architecture with multi-fidelity message passing; uses multigrid-style coarsening. Same caveat as [[taghizadeh2024mfgnn]] — designed for irregular meshes, less applicable to regular-grid `ifc_*` data than FNO.

## How to use in cycle 001

- **Not used** as a primary inspiration this cycle (regular grid → FNO is the right inductive bias).
- Future candidate if/when the factory tackles irregular-mesh datasets in `data/`.

## Related

- [[taghizadeh2024mfgnn]] — sibling GNN-based MF approach.
- [[li2020fno]] — preferred backbone for current smoke datasets.
