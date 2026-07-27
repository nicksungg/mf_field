---
name: niu2024mfrnp
description: MFRNP — multi-fidelity residual neural processes with decoder-in-the-aggregation. ICML 2024. Source for H2 fno_mf_stack architecture template. Existing source for poisson_local/heat_local baselines.
metadata:
  type: reference
tags:
  - factory
  - source
  - paper
  - core-mf
source: factory-archivist
date: 2026-05-15
bibtex_key: niu2024mfrnp
---

# niu2024mfrnp — Multi-Fidelity Residual Neural Processes

**Authors**: Niu, Wu, Kim, Ma, Watson-Parris, Yu. ICML 2024.
**Links**: [arXiv:2402.18846](https://arxiv.org/abs/2402.18846), [GitHub](https://github.com/Rose-STL-Lab/MFRNP)

## Why this paper matters

- **Architectural template for H2: `fno_mf_stack`** — MFRNP-style residual stacking with decoder-in-the-aggregation. The pattern: `y_HF = aggregate(decoded_LFs upsampled) + δ_HF` lets the HF model learn the correction rather than the full output, which is much better-conditioned given limited HF data (only 5 HF samples in `ifc_poisson`).
- **Existing baseline source**: MFRNP Table 1 (Full setup) numbers — Poisson-2/3/5 fidelities nRMSE 0.0076/0.0073/0.0046; Heat-2/3/5 nRMSE 0.005/0.0039/0.0045 — match what's currently in `baselines/paper_baselines.json` for `poisson_local`/`heat_local`. Sanity-check confirmed.

## Critical caveat

MFRNP's setup is **not the same** as the `ifc_*` datasets:
- Different fidelity counts (MFRNP varies 2/3/5; `ifc_*` is fixed at 4).
- Different train/test split conventions.

→ MFRNP's published numbers are **not directly usable** as the `ifc_*` paper bar. Use [[li2022ifc]] for `ifc_*` numbers. MFRNP's architectural idea (residual stacking with decoder aggregation) is portable.

## How to use in cycle 001

- Inspiration for **H2: `fno_mf_stack`**. Builder writes `models/fno_mf_stack/INSPIRATION.md` citing this and [[li2020fno]].
- Concrete design: one FNO per fidelity level (4 small FNOs, ~50k params each → ~200k total); FNO_k predicts y at level k; aggregation step trains LF decoders to maximize cross-fidelity info sharing; final HF output = aggregate(decoded_LFs upsampled to 64×64) + δ from HF FNO.
- Estimated smoke wall time: **3–5 min** for both datasets, comfortably under 30 min budget.

## Related

- [[li2020fno]] — backbone of choice for the per-fidelity FNOs in H2.
- [[li2022ifc]] — alternative MF approach (continuous basis) used in H1.
- [[cycle-001-candidate-ranking]] — H2 ranked #2.
