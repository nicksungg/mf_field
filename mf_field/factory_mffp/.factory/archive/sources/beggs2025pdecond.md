---
name: beggs2025pdecond
description: Beggs et al. (arXiv:2509.09599, Sep 2025) — FiLM-via-LayerNorm for PDE-parameter conditioning. Affine parameters in LayerNorm replaced with a learned function of conditioning info; decouples scale/shift from conditioning to enable leaner pretraining and better fine-tune transfer. Architectural blueprint for fno_coreg_conditioned (B1).
metadata:
  type: reference
tags:
  - factory
  - source
  - paper
  - cycle-008
  - new-citation
  - film-via-layernorm
  - blueprint-fno-coreg-conditioned
source: factory-archivist
date: 2026-06-02
bibtex_key: beggs2025pdecond
cycle: cycle-008
---

# beggs2025pdecond — Conditioning on PDE Parameters to Generalise Deep Learning Emulation of Stochastic and Chaotic Dynamics

**Authors**: Beggs et al. (Sep 2025).
**Link**: [arXiv:2509.09599](https://arxiv.org/abs/2509.09599)
**Suggested bibtex_key**: `beggs2025pdecond`

## Why this paper matters for cycle-008

**Direct architectural blueprint for the cycle-008 B1 hypothesis
(`fno_coreg_conditioned`, NEW family).** Most explicit literature precedent
for **FiLM-via-LayerNorm in FNO conditioned on PDE parameters** — and the
exact mechanism we propose to use for m-conditioning.

## Architectural recipe (verbatim from Researcher's summary)

> Affine parameters in LayerNorm replaced with a learned function of the
> conditioning information (FiLM); decouples scale and shift from the
> conditioning variable to enable leaner pretraining and better fine-tune
> transfer.

That maps directly to:

```
LayerNorm(γ=γ(m), β=β(m))  where  γ, β: MLP([m, m²])
```

with `m` the IFC fidelity index. The MLP head `MLP([m, m²])` is identical
to the basis-MLP head already validated in cycle-005 H2 — so the
conditioning side reuses code we already trust.

## Where it lands in-tree (cycle-008 B1)

- **New family** `models/fno_coreg_conditioned/` (project rule: add new
  families, do not delete/rename).
- Re-use `FNOBlock` from `mf_fno_transfer_bar/model.py`.
- Replace each `GroupNorm` inside `FNOBlock` with `FiLMNorm(channels, m_feat_dim)`
  computing `γ(m), β(m) = MLP([m, m²])` and returning
  `γ * GroupNorm(z) + β`.
- Single full-resolution HF FNO; no separate B(m) basis matrix; no K-dim
  latent grid.

## Cycle-008 disposition

- Primary precedent for B1 Mode A (FiLM-via-LayerNorm). Mode B
  (broadcast-channel conditioning) is the fallback if Mode A wall-time exceeds
  the 25-min cap.
- B1 kill-switch: wall > 25 min OR Heat > 0.0194 → REVERT.
- **B1 is the only intervention in cycle-008 with plausible single-family
  collapse of FAMILY_PDE_SPECIALIZATION_ASYMMETRY.**

## Confidence and risk

- **Medium confidence** — FiLM-via-LayerNorm in FNO has 2024-2025 external
  precedent (Beggs + Poseidon + CoDA-NO), but the **specific composition
  with the IFC m-basis MLP** is a novel-for-this-dataset combination. Hence
  speculative upside.

## Related

- [[research-cycle-008]] — cycle-008 web round
- [[herde2024poseidon]] — foundation-model FiLM-via-LayerNorm precedent
- [[rahman2024codano]] — codomain-attention complement
- [[li2022ifc]] — 2022-era outer-product basis (pattern being replaced)
- [[li2020fno]] — FNO backbone
- [[lyu2023mffno]] — LF→HF schedule retained in B1
- [[papers-summary-csv-state]] — pending csv update
