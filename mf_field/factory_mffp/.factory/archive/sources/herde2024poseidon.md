---
name: herde2024poseidon
description: Poseidon / scOT (Herde et al., NeurIPS 2024). Foundation model for PDEs — multiscale vision transformer with time-conditioned LayerNorm (FiLM-style). Validates FiLM-via-LayerNorm as the canonical lean conditioning channel in modern PDE neural operators.
metadata:
  type: reference
tags:
  - factory
  - source
  - paper
  - foundation-model
  - cycle-008
  - new-citation
  - film-via-layernorm
source: factory-archivist
date: 2026-06-02
bibtex_key: herde2024poseidon
cycle: cycle-008
---

# herde2024poseidon — Poseidon: Efficient Foundation Models for PDEs

**Authors**: Herde et al. (NeurIPS 2024).
**Link**: [arXiv:2405.19101](https://arxiv.org/abs/2405.19101)
**Suggested bibtex_key**: `herde2024poseidon`

## Why this paper matters for cycle-008

Together with `beggs2025pdecond` and `rahman2024codano`, this paper canonicalises
**FiLM-via-LayerNorm** as the modern (2024-2025) PDE-operator conditioning
channel. **The IFC outer-product basis `f(x,m) = B(m) · h(x)` is a 2022-era
design** — the contemporary composition is `f(x, m) = FNO(x; γ(m), β(m))`
with FiLM affines inside spectral blocks.

## Architecture summary

- Foundation model for PDEs; **multiscale vision transformer (scOT)**.
- **Time-conditioned LayerNorm** (FiLM-style conditioning on physical time).
- Pretrained on fluid dynamics; transfers to 15 downstream PDE tasks.

## Where the architectural lesson lands in-tree

- Indirect support for replacing the IFC outer-product `B(m) · h(x)` with
  **FiLM modulation `γ(m), β(m)`** on FNO hidden channels.
- Validates the FiLM-via-LayerNorm pattern at foundation-model scale →
  reduces risk of B1 (`fno_coreg_conditioned`) being an under-supported novel
  composition.

## Cycle-008 disposition

- Cited in research §1 (External Findings).
- One of two foundation-model FiLM-via-LayerNorm precedents (with
  `beggs2025pdecond`) backing B1.
- B1 (cycle-008 H2 / H3) uses Mode A — FiLM-via-LayerNorm inside `FNOBlock`
  GroupNorm — directly inspired by this pattern.

## Related

- [[research-cycle-008]] — cycle-008 web round
- [[beggs2025pdecond]] — direct FNO+FiLM precedent for parameter conditioning
- [[rahman2024codano]] — codomain-attention complement
- [[li2022ifc]] — 2022-era outer-product basis (pattern being replaced in B1)
- [[papers-summary-csv-state]] — pending csv update
