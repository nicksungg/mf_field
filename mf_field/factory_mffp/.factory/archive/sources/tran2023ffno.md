---
name: tran2023ffno
description: Factorized FNO (Tran et al., ICLR 2023). Replaces the standard SpectralConv2d with separate 1-D FFTs over each axis with independent smaller weight tensors. Reports 31–85% error reduction on Navier–Stokes / airfoil / elasticity / plastic forging. Architectural refactor, not IFC-style coregionalization.
metadata:
  type: reference
tags:
  - factory
  - source
  - paper
  - cycle-008
  - carry-over-citation
  - fno-spectral-refactor
  - deferred
source: factory-archivist
date: 2026-06-02
bibtex_key: tran2023ffno
cycle: cycle-008
---

# tran2023ffno — Factorized Fourier Neural Operators

**Authors**: Tran et al. (ICLR 2023).
**Link**: [arXiv:2111.13802](https://arxiv.org/abs/2111.13802)
**Suggested bibtex_key**: `tran2023ffno`

## Why this paper matters for cycle-008

Already referenced in [[anisotropic-spectral-modes-fno]] as a defensible
follow-up. Cycle-008 web round **re-confirmed** the reported 31–85% error
reduction on Navier-Stokes / airfoil / elasticity / plastic forging
benchmarks. Cited as the cycle-008 A3 hypothesis (DEFERRED) — a full
spectral-layer refactor that is a NEW-family-scale change rather than a
tight fit for the 30-min smoke budget.

## Architecture summary

- Replace the standard `SpectralConv2d` with the **factorized variant**:
  separate 1-D FFTs over each axis with independent smaller weight tensors.
- Drop-in replacement at the spectral-layer level (the rest of FNO is
  unchanged).

## Cycle-008 disposition

- **A3 hypothesis — DEFERRED** in favour of A1 (paper-config wire-up on
  existing `fno_coregionalization` architecture).
- Reason: full new-family scaffold cost; A1 is a tighter wall-time fit and
  has higher-confidence paper-config evidence.
- Carry candidate for cycle-009+ if A1 + B1 both land below kill-switch
  thresholds.

## Cited evidence

- 31-85% error reduction across NS / airfoil / elasticity / plastic forging
  benchmarks (2023 baselines).
- **NOT IFC-specific** — no direct evidence on multi-fidelity coregionalization
  datasets. Speculative extrapolation to our smoke datasets.

## Related

- [[research-cycle-008]] — cycle-008 web round
- [[anisotropic-spectral-modes-fno]] — sibling spectral-modes note
- [[li2020fno]] — original FNO backbone being refactored
- [[papers-summary-csv-state]] — pending csv update
