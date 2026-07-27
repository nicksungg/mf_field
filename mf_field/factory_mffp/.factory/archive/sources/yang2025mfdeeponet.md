---
name: yang2025mfdeeponet
description: Physics-Guided MF-DeepONet (March 2025). Two-phase transfer learning — pre-train LF DeepONet, freeze branch/trunk, fine-tune merge net on HF. Less natural fit for regular-grid 4-fidelity ladder than FNO+IFC.
metadata:
  type: reference
tags:
  - factory
  - source
  - paper
  - mf-deeponet
source: factory-archivist
date: 2026-05-15
bibtex_key: yang2025mfdeeponet
---

# yang2025mfdeeponet — Physics-Guided MF-DeepONet

**Link**: [arXiv:2503.17941](https://arxiv.org/abs/2503.17941) (March 2025)

## Why this paper matters

Two-phase MF-DeepONet variant:
1. Pre-train LF DeepONet.
2. Transfer: freeze branch/trunk, fine-tune merge network on HF.

Branch/trunk decomposition is conceptually attractive for fidelity-conditioned fields. Physics-guided HF subsampling helps in the small-HF regime.

## Why deferred this cycle

- Less natural fit than FNO+coregionalization for the regular-grid 4-fidelity ladder of `ifc_*`.
- Two-phase training is more bookkeeping than a single end-to-end model.
- Not in cycle 001's max_new=2 budget.

## Related

- [[lu2021deeponet]] (planned bibkey) — base DeepONet architecture (branch+trunk).
- [[cycle-001-candidate-ranking]] — explicitly deferred to a later cycle.
