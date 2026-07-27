---
name: pan2022hyperfno
description: HyperFNO (Pan et al., NeurIPS ML4PS 2022). Hypernetwork generates FNO weights conditioned on PDE parameters — ψ_λ = h(θ, λ); û = f(ψ_λ, x). Stronger conditioning than FiLM but parameter-heavy; out-of-budget for the cycle-008 smoke cap.
metadata:
  type: reference
tags:
  - factory
  - source
  - paper
  - cycle-008
  - carry-over-citation
  - parameter-conditioned-fno
  - deferred
source: factory-archivist
date: 2026-06-02
bibtex_key: pan2022hyperfno
cycle: cycle-008
---

# pan2022hyperfno — HyperFNO: Improving the Generalization Behavior of Fourier Neural Operators

**Authors**: Pan et al. (NeurIPS ML4PS 2022).
**Suggested bibtex_key**: `pan2022hyperfno`

## Why this paper matters for cycle-008

Cited as evidence that the **parameter-conditioned FNO** design space is
*live* in the literature (since 2022). Stronger conditioning than FiLM
(full-weight generation via hypernet) but **parameter-heavy** → out-of-budget
for the cycle-008 30-min smoke cap.

## Architecture summary

- Hypernetwork `h(θ, λ)` generates the full FNO weights ψ_λ conditioned on
  PDE parameter λ.
- Prediction: `û = f(ψ_λ, x)` where `f` is the FNO with hypernet-generated
  weights.
- The whole FNO is parameter-conditioned (not just LayerNorm affines).

## Cycle-008 disposition

- **NOT selected** as an H1/H2/H3 candidate.
- B1's FiLM-via-LayerNorm is preferred because it is **leaner** (only γ/β
  per channel, not whole weights) and has 2024-2025 follow-ups
  (`beggs2025pdecond`, `herde2024poseidon`) demonstrating the lighter
  pattern suffices.
- Listed in research §1 (External Findings) to show the literature genealogy
  of parameter-conditioned FNO (2022 hypernet → 2024-2025 FiLM-via-LayerNorm).

## Related

- [[research-cycle-008]] — cycle-008 web round
- [[beggs2025pdecond]] — leaner 2025 successor pattern
- [[herde2024poseidon]] — foundation-model FiLM scaffold
- [[li2020fno]] — FNO backbone (unconditioned baseline)
- [[papers-summary-csv-state]] — pending csv update
