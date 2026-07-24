---
name: wu2024transolver
description: Transolver — fast transformer solver for PDEs on general geometries. v9 baseline's backbone. ICML 2024 Spotlight. Mismatched inductive bias for regular-grid ifc_* data — deprioritized for cycle 001.
metadata:
  type: reference
tags:
  - factory
  - source
  - paper
  - backbone
source: factory-archivist
date: 2026-05-15
bibtex_key: wu2024transolver
---

# wu2024transolver — Transolver: A Fast Transformer Solver for PDEs on General Geometries

**Authors**: Wu et al. ICML 2024 Spotlight.
**Link**: [arXiv:2402.02366](https://arxiv.org/abs/2402.02366)

## Why this paper matters

- v9 baseline's backbone — slice-attention transformer designed for unstructured meshes.
- For regular-grid `ifc_*` PDE data, Transolver's slice-attention is **less efficient** than FNO's spectral conv (no inductive-bias benefit, higher cost).
- Code-level diagnosis of v9 (`references/v9_baseline/model_v9.py`) shows Transolver pairs with `gate_mlp(softmax)` to mix per-stream attention but has no continuous fidelity index → mechanism for F1 failure.

## How NOT to use in cycle 001

- Do **not** use Transolver as the backbone for H1 or H2. See [[li2020fno]] for the recommended backbone.
- A future cycle could try `transolver_residual` (hard HF−LF residual on top of Transolver) as an ablation — useful to isolate "is the MF fusion the bug, or the backbone?" — but deferred this cycle per hypothesis_budget.max_new=2.

## Related

- [[cycle-001-cross-cutting-findings]] — "FNO > Transolver for regular-grid data" is one of the propagated insights.
- [[li2020fno]] — recommended replacement backbone.
- [[cycle-001-failure-diagnosis]] — explains why v9's Transolver+gated-soft-prior structurally fails F1.
