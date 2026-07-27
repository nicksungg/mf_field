---
name: papers-summary-csv-state
description: Human-side TODO — papers_summary.csv referenced by factory.md/models/README.md/HOWTO.md but does not exist at repo root. 9 proposed bibtex_keys ready to populate it. Until then, per-family INSPIRATION.md carries bibtex inline.
metadata:
  type: reference
tags:
  - factory
  - source
  - human-action
  - cycle-001
  - missing-file
source: factory-archivist
date: 2026-05-15
cycle: "001"
project: factory_mffp
---

# `papers_summary.csv` — State and Proposed Rows

## State

The file **does not exist at the repo root** despite being referenced in:
- `factory.md:39`
- `models/README.md:36`
- `HOWTO.md:61`

The only literature-comparison CSV that exists is `references/v9_baseline/paper_comparison_table.csv` — but that file is scoped to v9's runs against `poisson_local`/`heat_local`/`fluid`, not a general literature catalogue.

## Why this is a human-side action

- A new top-level `.csv` file is arguably outside `models/**` (the only mutable surface in `.factory/config.json`).
- Any new `.csv` at repo root is fundamentally a literature catalogue, not model code.
- The CEO/user owns this — Researcher cannot create.

## Workaround until file exists

Each new family's `models/<family>/INSPIRATION.md` carries the bibtex inline. This is fine for cycle 001 (only H1 and H2).

## Proposed bibtex_keys for the file (when a human creates it)

Core MF surrogate methods:
- [[li2022ifc]] — Infinite-Fidelity Coregionalization (NeurIPS 2022) — **source paper for ifc datasets**.
- [[niu2024mfrnp]] — MFRNP residual stacking (ICML 2024).
- [[gladstone2024mfgunet]] — MF Graph U-Net.
- [[taghizadeh2024mfgnn]] — MF GNN.
- [[yang2025mfdeeponet]] — Physics-Guided MF-DeepONet.
- [[nietocentenero2025mfae]] — MF autoencoder transfer learning.
- [[sung2026fire]] — FIRE (training-free in-context MF). **Citation needs verification** (forward placeholder, suspicious arXiv year).

Backbone / inductive-bias references:
- [[li2020fno]] — Fourier Neural Operator.
- [[wu2024transolver]] — Transolver (v9's backbone).
- `lu2021deeponet` — DeepONet (planned, not yet sourced this cycle).
- `sitzmann2020siren` — SIREN (planned).
- `perez2018film` — FiLM (planned).

## Suggested CSV columns

`bibtex_key, title, authors, year, venue, url, summary, relevance_to_mf_field_pred`

Most direct: also include arXiv ID and DOI columns when available.

## Cycle-010 update (2026-06-02)

The cycle-010 web round added **6 new validated bibtex keys** (5 new + 1
pre-2024 newly-archived) and **corrected one arXiv ID** carried from
cycle-009. Total ready for the pending csv: **15 keys**.

New 2024-2026 keys (cycle-010):

- [[mutransferfno2025]] — μTransfer-FNO ([arXiv:2506.19396](https://arxiv.org/abs/2506.19396), Jun 2025). Width-axis LR-transfer guarantee for FNO. Backs O1 H1 capacity bump.
- [[ufnofilm2025]] — Feature-Modulated UFNO ([arXiv:2511.20543](https://arxiv.org/abs/2511.20543), Nov 2025). γ(scalar, LF_field) on FNO-family; 21% MAE gain on multiphase flow. NK1-safe blueprint missing from cycle-008. O3/O4 — DEFERRED.
- [[pirino2025]] — PI-RINO ([arXiv:2510.23810](https://arxiv.org/abs/2510.23810), Oct 2025). Function-encoder dict learning; multi-resolution NOT multi-fidelity. Backlog reference.
- [[fnospectralperspective2024]] — Spectral Perspective on FNO ([arXiv:2404.07200](https://arxiv.org/abs/2404.07200), Apr 2024). Fourier-kernel saturation warning. Backs O1 H1's `modes ≤ 24` hold.
- [[mfbpinn2026]] — MF-BPINN ([arXiv:2602.01176](https://arxiv.org/abs/2602.01176), 2026). Hierarchical residual + Bayesian UQ; PINN family. Backlog reference.

Pre-2024 key newly archived (cycle-010):

- [[liu2022neuralcoreg]] — Neural Embedding of Coregionalization ([arXiv:2109.09261](https://arxiv.org/abs/2109.09261), KBS 2022). Canonical pre-FNO precedent for B(x) input-dependent coregionalization. O3.

arXiv ID correction (cycle-010):

- [[stresstest2025fno]] — corrected from `2501.11428` → **`2601.11428`** (Jan 2026). Same paper, same use (O1 H1 elliptic saturation evidence).

See [[research-cycle-010]] for the full disposition table (which
hypotheses cite which keys; what was deferred and why).

## Cycle-008 update (2026-06-02)

The cycle-008 web round added **5 new validated bibtex keys** (research-
cycle-008 CEO PROCEED) and re-confirmed **4 carry-over keys**. Total
ready for the pending csv: **9 keys**.

New 2024-2025 keys (cycle-008):

- [[cao2025mflno]] — MF-LNO (arXiv:2502.00550, Feb 2025).
- [[rahman2024codano]] — CoDA-NO (NeurIPS 2024).
- [[herde2024poseidon]] — Poseidon foundation model (NeurIPS 2024).
- [[beggs2025pdecond]] — PDE-parameter FiLM-via-LayerNorm (arXiv:2509.09599,
  Sep 2025).
- [[engstruct2025mfft]] — MF pretrain-finetune (Eng. Struct. 2025,
  paywalled).

Carry-over keys re-confirmed (cycle-008):

- [[lyu2023mffno]] — Phys. Fluids 2023 LF→HF schedule.
- [[gcs2023mffno]] — Geological CCS replication.
- [[tran2023ffno]] — Factorized FNO (ICLR 2023).
- [[pan2022hyperfno]] — Parameter-conditioned FNO precursor (NeurIPS
  ML4PS 2022).

See [[research-cycle-008]] for the full disposition table (which
hypotheses cite which keys).

## Related

- [[paper-baselines-proposals]] — sibling human-side TODO.
- [[research-cycle-008]] — cycle-008 research synthesis.
- All `[[li2022ifc]]`, `[[niu2024mfrnp]]`, etc., source notes link here.
