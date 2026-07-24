---
name: engstruct2025mfft
description: Pretrain-finetune neural operator for multi-fidelity surrogate modeling of structural dynamic systems (Engineering Structures 2025, ScienceDirect S0141029625016098). Title and abstract confirm LF-pretrain → HF-fine-tune schedule beating joint training — 5th independent citation backing cycle-007 H2 schedule.
metadata:
  type: reference
tags:
  - factory
  - source
  - paper
  - cycle-008
  - new-citation
  - lf-hf-schedule
  - paywalled
source: factory-archivist
date: 2026-06-02
bibtex_key: engstruct2025mfft
cycle: cycle-008
---

# engstruct2025mfft — Pretrain-finetune neural operator for multi-fidelity surrogate modeling of structural dynamic systems

**Venue**: Engineering Structures 2025. ScienceDirect S0141029625016098.
**Access**: paywalled — title + abstract verified, full text not extracted.
**Suggested bibtex_key**: `engstruct2025mfft`

## Why this paper matters for cycle-008

5th **independent** citation (alongside Lyu 2023, GCS 2024, Yang
MF-DeepONet 2025, and the in-tree H2 schedule) for the
**LF-pretrain → HF-fine-tune** schedule pattern in MF neural operators.
Direct support for both A2 (re-bind cycle-007 H2 schedule — already banked)
and B3 (three-stage curriculum on `fno_coreg_residual`).

## Architectural takeaway

- Pretrain-on-LF, fine-tune-on-HF beats **joint** training (the alternative
  baseline).
- Schedule pattern is now well-replicated across 5 independent groups in
  3 application domains (fluids — Lyu; geological CCS — GCS; structural
  dynamics — this paper; PDE benchmarks — H2 in-tree; multi-fidelity
  deeponet — Yang). **Schedule is no longer speculative literature** — it
  is the de facto standard.

## Cycle-008 disposition

- Strengthens the citation set for B3 (Stage 1 LF pretrain → Stage 2 HF
  residual → Stage 3 basis-head unfreeze).
- Does NOT change the kill-switch or recipe-hash guard requirements on B3.
- Does NOT motivate a fresh re-run of A2 (cycle-007 H2 schedule) — that
  is already committed code, intact in the cycle-008 baseline state.

## Caveats

- Paywalled; only title + abstract verified.
- Domain (structural dynamics) is not PDE-class identical to our IFC
  Heat/Poisson — used as *schedule precedent*, not as transfer evidence
  for the specific datasets.

## Related

- [[research-cycle-008]] — cycle-008 web round
- [[lf-hf-pretrain-fraction-survey]] — pretrain_frac literature comparison
- [[lyu2023mffno]] — primary precedent for LF→HF schedule
- [[gcs2023mffno]] — geological CCS replication
- [[yang2025mfdeeponet]] — deeponet replication
- [[per-dataset-recipes-mf-field]] — recipe-dispatch survey
- [[papers-summary-csv-state]] — pending csv update
