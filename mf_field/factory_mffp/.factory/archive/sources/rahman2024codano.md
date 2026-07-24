---
name: rahman2024codano
description: CoDA-NO — Codomain Attention Neural Operator (Rahman et al., NeurIPS 2024). Tokenizes functions along the codomain (channel) axis via attention; pre-train one model, transfer to multiphysics PDEs with >36% few-shot improvement. Suggests treating fidelity index m as a codomain axis.
metadata:
  type: reference
tags:
  - factory
  - source
  - paper
  - foundation-model
  - cycle-008
  - new-citation
source: factory-archivist
date: 2026-06-02
bibtex_key: rahman2024codano
cycle: cycle-008
---

# rahman2024codano — Pretraining Codomain Attention Neural Operators for Solving Multiphysics PDEs

**Authors**: Rahman et al. (NeurIPS 2024).
**Link**: [arXiv:2403.12553](https://arxiv.org/abs/2403.12553)
**Code**: github.com/neuraloperator/CoDA-NO
**Suggested bibtex_key**: `rahman2024codano`

## Why this paper matters for cycle-008

- Validates the broader 2024-2025 trend of **single-model foundation operators
  conditioned on PDE-class / parameter axes**.
- Few-shot transfer improvement of **>36% over baselines** on multiphysics
  benchmarks — strong evidence that codomain/channel-level conditioning is
  expressive enough for cross-PDE generalisation.

## Architecture summary

- Tokenises functions along the **codomain (channel) dimension** via attention.
- One pre-trained model transfers to multiple downstream multiphysics PDE tasks.
- Conditioning is per-channel attention (not FiLM affines).

## Adaptation idea (cycle-008 context)

- Treat **fidelity index m as a codomain axis** rather than a scalar broadcast.
- Speculative — the default config is ≥3M params, near the upper end of our
  smoke budget.
- NOT selected as H1/H2 this cycle; the related but lighter-weight
  `beggs2025pdecond` + `herde2024poseidon` FiLM-via-LayerNorm pattern is
  used in B1 instead.

## Cycle-008 disposition

- Cited in research §1 (External Findings).
- Supports the broader thesis that **single-FNO conditioned on m** is a
  defensible 2024-2025 design pattern.
- Carry candidate for cycle-010+ if FiLM-via-LayerNorm in B1 underperforms
  and a heavier codomain-attention scaffold is justified.

## Related

- [[research-cycle-008]] — cycle-008 web round
- [[herde2024poseidon]] — FiLM-via-LayerNorm canonical pattern
- [[beggs2025pdecond]] — direct PDE-parameter FiLM precedent
- [[cao2025mflno]] — alternative linear+nonlinear MF residual decomposition
- [[papers-summary-csv-state]] — pending csv update
