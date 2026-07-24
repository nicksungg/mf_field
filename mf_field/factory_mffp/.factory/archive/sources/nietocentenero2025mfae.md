---
name: nietocentenero2025mfae
description: Multi-fidelity autoencoder transfer learning for aerodynamic data fusion (Dec 2025). Pre-train encoder on LF, fine-tune decoder + bias-correction layer on HF. Useful when HF data is very limited.
metadata:
  type: reference
tags:
  - factory
  - source
  - paper
  - mf-autoencoder
source: factory-archivist
date: 2026-05-15
bibtex_key: nietocentenero2025mfae
---

# nietocentenero2025mfae — Multi-Fidelity Aerodynamic Data Fusion by Autoencoder Transfer Learning

**Link**: [arXiv:2512.13069](https://arxiv.org/abs/2512.13069) (Dec 2025)

## Why this paper matters

- Pre-train encoder on LF, fine-tune decoder + bias-correction layer on HF.
- Useful in the **very-limited-HF regime** — which matches our `ifc_poisson` (5 HF samples) well.
- Less directly applicable than coregionalization for *fixed*-fidelity-grid data; coregionalization explicitly parametrizes the per-fidelity scale via B(m).

## Why deferred this cycle

- Less direct fit than [[li2022ifc]] for fixed 4-fidelity setup with continuous index m.
- Outside cycle 001 max_new=2 budget.

## Related

- [[cycle-001-candidate-ranking]] — deferred.
- [[li2022ifc]] — preferred MF approach for fixed-fidelity-grid IFC datasets.
