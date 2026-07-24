---
name: mfbpinn2026
description: MF-BPINN — Multi-Fidelity PINN with Bayesian UQ (arXiv:2602.01176, 2026). Hierarchical residual learning across fidelities with Bayesian uncertainty quantification. Adjacent — PINN family not FNO. Backlog reference for cycle-010.
metadata:
  type: reference
tags:
  - factory
  - source
  - paper
  - cycle-010
  - new-citation
  - mf-pinn
  - bayesian-uq
  - backlog-only
source: factory-archivist
date: 2026-06-02
bibtex_key: mfbpinn2026
cycle: cycle-010
---

# mfbpinn2026 — Multi-Fidelity Bayesian PINN

**Link**: [arXiv:2602.01176](https://arxiv.org/abs/2602.01176) (2026)
**Suggested bibtex_key**: `mfbpinn2026`

## Why this paper matters for cycle-010

**Adjacent — PINN family, not FNO.** Hierarchical residual learning across fidelities with Bayesian UQ.

The hierarchical-residual pattern is conceptually related to MFRNP (already the parent of `fno_mf_stack`), but the implementation is PINN-style (residual minimization on PDE operator) rather than data-driven operator learning. Useful as a 2026 reference point on the MF surrogate landscape.

## Cycle-010 disposition

**Backlog reference only.** PINN scope is orthogonal to our FNO+MFRNP stack; the Bayesian UQ angle does not align with our nRMSE-on-held-out-test target metric.

Carry forward as a 2026 citation marker for the cycle-011+ literature catalogue.

## Confidence

**MEDIUM for citation accuracy** (abstract reviewed via search snippet); **LOW for cycle-010 priority** (scope mismatch).

## Related

- [[research-cycle-010]] — cycle-010 synthesis citing this
- [[niu2024mfrnp]] — sibling hierarchical-residual approach (data-driven, not PINN)
- [[papers-summary-csv-state]] — pending CSV update
