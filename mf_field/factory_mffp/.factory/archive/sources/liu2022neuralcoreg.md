---
name: liu2022neuralcoreg
description: Scalable Multi-Task GPs with Neural Embedding of Coregionalization (arXiv:2109.09261, KBS 2022). Canonical pre-FNO precedent for INPUT-DEPENDENT coregionalization — replaces LMC's static B matrix with a neural embedding mapping inputs to latent weights, i.e. B(x) instead of static B. Pre-2024 but new to our archive.
metadata:
  type: reference
tags:
  - factory
  - source
  - paper
  - cycle-010
  - new-citation
  - input-dependent-coregionalization
  - pre-fno-precedent
source: factory-archivist
date: 2026-06-02
bibtex_key: liu2022neuralcoreg
cycle: cycle-010
---

# liu2022neuralcoreg — Scalable Multi-Task GPs with Neural Embedding of Coregionalization

**Link**: [arXiv:2109.09261](https://arxiv.org/abs/2109.09261) (KBS 2022)
**Suggested bibtex_key**: `liu2022neuralcoreg`

## Why this paper matters for cycle-010

**Canonical pre-FNO precedent for input-dependent coregionalization.**

Replaces the Linear Model of Coregionalization (LMC) static coregionalization matrix `B` with a **neural embedding** mapping inputs to latent coregionalization weights — i.e., `B(x)` instead of static `B`. This is the architectural ancestor of any `B(m, x)` or `B(m, LF_features)` revision to `fno_coregionalization`'s K-basis.

Pre-2024 paper, but **new to our archive** — surfaced this cycle while searching the prior art for O3 (K-basis parametrization for coregionalization).

## Cycle-010 disposition

**O3 (RESERVE / DEFER).** Composite-mover prior is weak — `fno_coregionalization × poisson = 0.598` is the dominant per-family failure but recovering it to even 0.030 would not move the composite leader (`fno_mf_stack × poisson = 0.038`). NK1-adjacent (the LF-features pathway is precisely what NK1 required, so structurally distinct, but the family is the one where NK1 was set — pursue with caution).

If pursued at cycle-011+:
- Mode A (mean-pool LF features): `lf_feat = mean over spatial dims of intermediate LF FNO activations at m<1`. Cheap.
- Mode B (cross-attention over LF feature maps): more expensive; defer.

## Confidence

**MEDIUM-HIGH for the technique**; **LOW for cycle-010 priority** (non-leader cell + NK1-adjacency).

## Related

- [[research-cycle-010]] — cycle-010 synthesis citing this
- [[li2022ifc]] — IFC paper; current K-basis `B(m)=MLP([m, m²])` lives here
- [[ufnofilm2025]] — FNO-era input-dependent conditioning precedent
- [[cao2025mflno]] — two-branch (linear + nonlinear) basis decomposition
- [[rahman2024codano]] — codomain-attention complement
- [[papers-summary-csv-state]] — pending CSV update
