---
name: stresstest2025fno
description: "Forcing and Diagnosing Failure Modes of FNO Across Diverse PDE Families" (arXiv:2601.11428, Jan 2026 — arXiv ID corrected from 2501.11428 this cycle). Fixed config `width=64, depth=4, 16 Fourier modes in 1D` across 5 PDE families including elliptic Poisson. Treats `modes≈16` as sufficient for elliptic problems in published practice.
metadata:
  type: reference
tags:
  - factory
  - source
  - paper
  - cycle-009
  - cycle-010
  - fno-failure-modes
  - elliptic-saturation
  - arxiv-id-corrected
source: factory-archivist
date: 2026-06-02
bibtex_key: stresstest2025fno
cycle: cycle-010
---

# stresstest2025fno — Forcing and Diagnosing Failure Modes of FNO Across Diverse PDE Families

**Link**: [arXiv:2601.11428](https://arxiv.org/abs/2601.11428) (Jan 2026)
**Suggested bibtex_key**: `stresstest2025fno`
**arXiv ID correction (cycle-010):** prior cycle-009 archive note used `2501.11428`; correct ID is **`2601.11428`** (verified in cycle-010 web round).

## Why this paper matters for cycle-010

**Re-verified bound on the cycle-010 H1 HF-modes step.**

Paper uses a fixed config across 5 PDE families (dispersive, elliptic Poisson, multi-scale fluid, financial, chaotic):
- `FNO width=64`
- `depth=4`
- `16 Fourier modes in 1D`

The fact that practitioners use `modes=16` as the *fixed* config across all families — including elliptic Poisson — confirms `modes≈16` is treated as sufficient in published practice.

**Caveat:** the paper's experiments are 1D. On our 2D 64×64 problem, the HF Nyquist limit is 33, so cycle-009's HF=20 (≈60% Nyquist) is mid-range, and cycle-010 H1's proposed HF=24 (~73% Nyquist) still has headroom toward 28 (~85%) before strict diminishing returns. The qualitative warning carries; the precise threshold does not.

## Cycle-010 H1 implication

- Width-axis (`hidden=64 → 96`) is the safer scaling step than mode-axis ([[fnospectralperspective2024]] companion warning).
- Holding `modes_per_level[3] ≤ 24` (no further than 73% Nyquist) is the principled upper bound.

## Confidence

**HIGH** — corroborated by two independent 2024-2025 sources ([[fnospectralperspective2024]]; PhysicsX 2024 practitioner blog).

## Related

- [[research-cycle-009]] — first cycle that surfaced this paper (with incorrect arXiv ID)
- [[research-cycle-010]] — cycle-010 synthesis re-citing with corrected ID
- [[fnospectralperspective2024]] — companion saturation warning
- [[mutransferfno2025]] — width-axis transfer guarantee
- [[li2020fno]] — FNO backbone (`modes=8-32` canonical range)
- [[papers-summary-csv-state]] — pending CSV update
