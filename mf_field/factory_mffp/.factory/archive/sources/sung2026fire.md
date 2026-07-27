---
name: sung2026fire
description: FIRE — training-free MF regression via distribution-conditioned in-context learning on tabular foundation models. Novel "distribution-conditioned" twist. Adaptation to field prediction non-trivial. Deferred this cycle.
metadata:
  type: reference
tags:
  - factory
  - source
  - paper
  - mf-incontext
  - placeholder
source: factory-archivist
date: 2026-05-15
bibtex_key: sung2026fire
---

# sung2026fire — FIRE: Multi-fidelity Regression with Distribution-conditioned In-context Learning

**Authors**: Sung et al.
**Link**: [arXiv:2601.22371](https://arxiv.org/abs/2601.22371) (citation is a forward placeholder — Researcher explicitly noted "not in webfetch reach this pass"; arXiv ID has suspicious year 2601)

## Why this paper matters

- **Training-free** MF framework: a pre-trained tabular foundation model (TFM) acts as a zero-shot Bayesian in-context regressor conditioned on the LF model's posterior predictive distribution.
- "Distribution-conditioned" twist: give the HF model the *distribution* of LF predictions, not point predictions → may capture heteroscedastic fidelity errors.
- Attractive for the limited-HF-data regime (we have 5 HF samples).

## Why deferred this cycle

- Adapting to **field** prediction requires tokenizing patches or coordinates — non-trivial implementation.
- Researcher could not fetch the paper this cycle; the arXiv ID is a placeholder.
- Outside cycle 001 max_new=2 budget.

## Status

- **Citation needs verification** before promoting to a hypothesis. The bibkey is fine to keep as a placeholder for the family slot in the backlog (per CEO verdict, this is non-blocking and doesn't affect H1/H2).
- Flag for a future cycle: revisit if H1/H2 plateau, and verify the citation first.

## Related

- [[cycle-001-candidate-ranking]] — deferred from cycle 001.
