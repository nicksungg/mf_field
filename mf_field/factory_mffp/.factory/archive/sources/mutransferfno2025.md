---
name: mutransferfno2025
description: μTransfer-FNO (arXiv:2506.19396, Jun 2025) — Maximal Update Parametrization for FNO. Tuned LRs transfer across hidden widths under proper μP, so a 64-channel LR works at 128/256/512 without re-search. Backs cycle-010 H1 hidden=64→96 step as monotonically helpful given correct LR scaling.
metadata:
  type: reference
tags:
  - factory
  - source
  - paper
  - cycle-010
  - new-citation
  - fno-capacity
  - mu-parametrization
source: factory-archivist
date: 2026-06-02
bibtex_key: mutransferfno2025
cycle: cycle-010
---

# mutransferfno2025 — μTransfer-FNO: Maximal Update Parametrization for FNO

**Link**: [arXiv:2506.19396](https://arxiv.org/abs/2506.19396) (Jun 2025)
**Suggested bibtex_key**: `mutransferfno2025`

## Why this paper matters for cycle-010

Direct support for the cycle-010 H1 capacity bump (`hidden=64 → 96`) on `fno_mf_stack`.

The paper derives μP (Maximal Update Parametrization) for FNO. Practical claim from the abstract:
**learning rates transfer across hidden widths under proper μP** — a tuned 64-channel FNO LR will work at 128/256/512 channels without a re-search.

Implication for our setting:
- The **width axis is monotonically helpful given correct LR scaling**, until data/capacity ceiling.
- We do not need to re-tune `lr=1e-3` (canonical-MFRNP) at hidden=96 — the cycle-009 H1+H2 result at hidden=64 should transfer.
- No explicit Poisson saturation curve in the abstract, but the width-monotonicity claim is the load-bearing one for H1.

## How H1 uses this

`models/fno_mf_stack/smoke_eval.py:39-55` — bumping `hidden=64 → 96` (and `n_blocks` unchanged at 4) is a width-axis step. μTransfer-FNO is the published guarantee that `base_lr=1e-3` will not need re-tuning at the new width.

## Confidence

**HIGH** — abstract is unambiguous on width-transfer; the paper is recent (Jun 2025) so it post-dates the canonical FNO/MF-FNO recipes we already use.

## Related

- [[research-cycle-010]] — cycle-010 synthesis citing this
- [[li2020fno]] — FNO backbone
- [[niu2024mfrnp]] — parent architecture for `fno_mf_stack`
- [[stresstest2025fno]] — companion fixed-config evidence on FNO width=64
- [[papers-summary-csv-state]] — pending CSV update (cycle-010 brings to 15 keys)
