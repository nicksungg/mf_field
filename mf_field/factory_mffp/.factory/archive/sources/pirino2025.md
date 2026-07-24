---
name: pirino2025
description: PI-RINO — Physics-informed Multi-resolution Neural Operator (arXiv:2510.23810, Oct 2025). Function-encoder dictionary learning — encode LF function via SIREN dictionary, then condition operator MLP on the embedding. Two-stage LF-encode-then-condition pattern. Multi-resolution NOT multi-fidelity. Backlog reference for cycle-010.
metadata:
  type: reference
tags:
  - factory
  - source
  - paper
  - cycle-010
  - new-citation
  - function-encoder
  - multi-resolution
  - backlog-only
source: factory-archivist
date: 2026-06-02
bibtex_key: pirino2025
cycle: cycle-010
---

# pirino2025 — Physics-informed Multi-resolution Neural Operator (PI-RINO)

**Link**: [arXiv:2510.23810](https://arxiv.org/abs/2510.23810) (Oct 2025)
**Suggested bibtex_key**: `pirino2025`

## Why this paper matters for cycle-010

**Adjacent — multi-resolution, NOT multi-fidelity.** Function-encoder dictionary learning: encode LF function via a SIREN dictionary, then condition an operator MLP on the embedding.

The mechanism is different from FiLM (dictionary projection vs affine modulation), but the **two-stage LF-encode-then-condition pattern** is the same architectural family as O4 (γ(m, LF_features)). One of two readable HTML excerpts captured this cycle (the other was UFNO-FiLM).

## Cycle-010 disposition

**Backlog reference only.** Not pursued — multi-resolution is orthogonal to the ifc_* multi-fidelity ladder we work with.

If cycle-011+ revives O4, PI-RINO's function-encoder pattern is one of two architectural alternatives to FiLM:
1. UFNO-FiLM: pooled-spatial-features → γ, β.
2. PI-RINO: SIREN-encoded function → MLP context.

## Confidence

**MEDIUM for the pattern**; **LOW for cycle-010 priority** (multi-resolution scope mismatch).

## Related

- [[research-cycle-010]] — cycle-010 synthesis citing this
- [[ufnofilm2025]] — alternative LF-conditioning blueprint
- [[papers-summary-csv-state]] — pending CSV update
