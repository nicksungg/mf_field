---
name: fnospectralperspective2024
description: "Toward Better Understanding of FNO from a Spectral Perspective" (arXiv:2404.07200, Apr 2024). Enlarging the Fourier kernel does NOT necessarily improve accuracy — high-order modes contain minimal energy and mostly encode structural details; eliminating them can enhance generalization. Argues conservative end of cycle-010 HF-modes ladder.
metadata:
  type: reference
tags:
  - factory
  - source
  - paper
  - cycle-010
  - new-citation
  - fno-modes-saturation
  - generalization-warning
source: factory-archivist
date: 2026-06-02
bibtex_key: fnospectralperspective2024
cycle: cycle-010
---

# fnospectralperspective2024 — Toward Better Understanding of FNO from a Spectral Perspective

**Link**: [arXiv:2404.07200](https://arxiv.org/abs/2404.07200) (Apr 2024)
**Suggested bibtex_key**: `fnospectralperspective2024`

## Why this paper matters for cycle-010

**Saturation warning that bounds the cycle-010 H1 HF-modes step.**

Key observation: enlarging the Fourier kernel does **not necessarily improve accuracy**. High-order modes containing minimal energy mostly encode structural details; **eliminating them can enhance generalization**.

Implication: pushing HF modes past ~60-70% of Nyquist risks val→test inflation, not just compute cost.

## Cycle-010 H1 constraint

Argues for the **conservative** end of the cycle-010 HF-modes sweep:
- Cycle-009 H1+H2 ran HF modes = 20 (60% of Nyquist at 64×64; Nyquist limit = 33).
- Cycle-010 H1 proposed HF modes = 24 (73% Nyquist) — at the upper edge of the generalization-safe band per this paper.
- HARD HOLD: do NOT push HF modes past 24 on 64×64 elliptic until this paper's claim is empirically falsified in our setting.

Companion evidence:
- [[stresstest2025fno]] uses `modes=16` as a fixed config on elliptic Poisson — treats `~16` as sufficient.
- PhysicsX FNO blog (2024): "For elliptic and laminar problems, the dominant physics tends to be concentrated in the first few Fourier modes."

## Confidence

**HIGH for the saturation principle** — corroborated by two independent 2024-2025 sources (stresstest2025fno fixed config; PhysicsX practitioner blog).

## Related

- [[research-cycle-010]] — cycle-010 synthesis citing this
- [[stresstest2025fno]] — companion fixed-config evidence on elliptic Poisson
- [[mutransferfno2025]] — width-axis is the safer scaling axis given this paper's modes-axis warning
- [[li2020fno]] — FNO backbone (modes=8-32 canonical range)
- [[anisotropic-spectral-modes-fno]] — current modes_h/modes_w split in place
- [[papers-summary-csv-state]] — pending CSV update
