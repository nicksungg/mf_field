---
name: ufnofilm2025
description: Feature-Modulated UFNO (arXiv:2511.20543, Nov 2025) — FiLM context derived from BOTH scalar parameters AND spatial low-fidelity features (permeability field). 21% MAE reduction on multiphase flow. Direct precedent for γ(scalar, LF_field) on FNO-family — the NK1-safe blueprint missing from cycle-008.
metadata:
  type: reference
tags:
  - factory
  - source
  - paper
  - cycle-010
  - new-citation
  - film-with-lf-features
  - nk1-safe-blueprint
source: factory-archivist
date: 2026-06-02
bibtex_key: ufnofilm2025
cycle: cycle-010
---

# ufnofilm2025 — Feature-Modulated UFNO for Multiphase Flow

**Link**: [arXiv:2511.20543](https://arxiv.org/abs/2511.20543) (Nov 2025)
**Suggested bibtex_key**: `ufnofilm2025`

## Why this paper matters for cycle-010

**First direct precedent for γ(scalar, LF_field) in an FNO-family architecture.** This is the NK1-safe FiLM formulation that cycle-008 H2 (`fno_coreg_conditioned` with γ(m, m²) HF-only) was missing.

Context = scalar parameters + **spatial LF features (permeability field)**. The paper reports a **21% MAE reduction** on multiphase flow, which is the most concrete external evidence we have that conditioning a FiLM context on LF features (not just scalars) pays off.

The paper does not disclose pooling strategy in the abstract, but FiLM context vectors are conventionally fixed-length so a pooling step is implicit.

## NK1 carve-out implication

NK1 closed pure-m HF-only conditioning (cycle-008 H2 falsified at 12.6× over leader on Poisson). UFNO-FiLM's mechanism — conditioning context on a spatial LF field — is **structurally distinct** from NK1: the LF field IS the LF→HF pathway NK1 required. This is the right blueprint for any future `fno_coreg_conditioned_v2` revival.

## Cycle-010 disposition

- O3/O4 (basis revision / FiLM-with-LF-features): **DEFERRED** to backlog. Composite-mover prior is weak (recovering non-leader cells doesn't move the metric).
- Reserved for cycle-011+ if H1/H2 plateau on the load-bearing `fno_mf_stack × poisson` cell.

## Where it would land in-tree (deferred)

- NEW family `models/fno_coreg_conditioned_v2/` (or rewrite empty `models/fno_coreg_conditioned/`).
- `model.py` FNOBlock with FiLMNorm replacing GroupNorm: `γ, β = MLP([m, m², pooled_lf_feat])`.
- `smoke_eval.py` two-pass inference: run LF FNO → pool features → run HF FNO conditioned on pooled vector. ~1.5× wall vs single FNO.

## Confidence

**MEDIUM-HIGH for the technique** at later cycles. **LOW for cycle-010** (high implementation cost; weak composite prior since family is not a current leader on either dataset).

## Related

- [[research-cycle-010]] — cycle-010 synthesis citing this
- [[beggs2025pdecond]] — γ(scalar)-only precedent (cycle-008 H2's blueprint, NK1-closed)
- [[herde2024poseidon]] — FiLM-via-LayerNorm precedent at foundation-model scale
- [[rahman2024codano]] — codomain-attention complement
- [[liu2022neuralcoreg]] — input-dependent coregionalization, pre-FNO precedent
- [[papers-summary-csv-state]] — pending CSV update
