---
name: cao2025mflno
description: Multi-fidelity Laplace Neural Operator (Cao et al., arXiv:2502.00550, Feb 2025) — LF base + parallel linear + nonlinear HF correctors with dynamic inter-fidelity weighting and UQ via replica exchange. Closest analogue to a non-monotone fidelity-correlation fix for Poisson.
metadata:
  type: reference
tags:
  - factory
  - source
  - paper
  - multi-fidelity
  - cycle-008
  - new-citation
source: factory-archivist
date: 2026-06-02
bibtex_key: cao2025mflno
cycle: cycle-008
---

# cao2025mflno — Multi-fidelity Prediction and Uncertainty Quantification with Laplace Neural Operators for Parametric PDEs

**Authors**: Cao et al. (Feb 2025).
**Link**: [arXiv:2502.00550](https://arxiv.org/abs/2502.00550)
**Suggested bibtex_key**: `cao2025mflno`

## Why this paper matters for cycle-008

Captures the **non-monotone fidelity-correlation** architecture pattern that
directly addresses the `fno_coregionalization × ifc_poisson` 0.7501 failure
mode where Poisson has non-monotone m-correlation across its 4 fidelity
levels (vs Heat's smooth monotone m-modulation).

## Architecture summary

- LF base model + **parallel linear and nonlinear HF correctors** + dynamic
  inter-fidelity weighting.
- UQ via replica exchange (orthogonal to our smoke goals).
- Splits the residual into a *linear LF→HF map* PLUS a *nonlinear corrector*,
  rather than a single MLP basis on `[m, m²]`.

## Where the architectural lesson lands in-tree

- Current `fno_coregionalization` uses `B(m) = MLP([m, m²])` — nonlinear-in-m
  but constrained to a K-dim outer product.
- The MF-LNO recipe is to replace that single nonlinear basis with a
  **two-branch residual decomposition**: a linear LF→HF map + nonlinear
  corrector. **Cheaper speculative alternative to B1 (`fno_coreg_conditioned`)**.

## Cycle-008 disposition

- Cited in cycle-008 research §1 (External Findings) as architectural prior
  for non-monotone fidelity-correlation fixes.
- NOT selected as an H1/H2/H3 hypothesis this cycle — B1's FiLM-via-LayerNorm
  pattern has stronger 2024-2025 precedent (Poseidon, Beggs, CoDA-NO).
- Carry candidate for cycle-009 if B1 lands negative.

## Benchmarks

- Lorenz, Duffing, Burgers, Brusselator. **NOT Poisson/Heat directly** —
  architectural lesson is portable but transfer to IFC datasets is
  speculative.

## Related

- [[research-cycle-008]] — cycle-008 web round
- [[li2022ifc]] — IFC paper (current outer-product basis)
- [[beggs2025pdecond]] — preferred 2024-2025 conditioning pattern
- [[herde2024poseidon]] — FiLM-via-LayerNorm scaffold
- [[rahman2024codano]] — codomain-attention conditioning
- [[papers-summary-csv-state]] — pending csv update
