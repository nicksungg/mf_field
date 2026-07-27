---
name: cycle-001-cross-cutting-findings
description: Cross-cutting findings to propagate to both H1 and H2 — per-fidelity output normalization (likely largest single win), val_frac 0.2 → 0.1, FNO > Transolver for regular-grid PDE data, continuous fidelity index is the missing inductive bias.
metadata:
  type: reference
tags:
  - factory
  - source
  - cross-cutting
  - cycle-001
source: factory-archivist
date: 2026-05-15
cycle: "001"
project: factory_mffp
---

# Cycle 001 — Cross-Cutting Findings (must propagate to both H1 and H2)

These are not architecture-specific but apply across all candidate families and to any future MF model in this repo.

## 1. Per-fidelity output normalization is the immediate F1 fix

The single most impactful change identified this cycle. Even *without* changing the backbone:
- Predict `y / scaler[m]` where `scaler[m] = max-abs of training y at fidelity m` (computable from training data, no learning needed).
- This **alone would likely drop ifc_poisson from 18.5 to ~1.0** (per Researcher's magnitude analysis in [[cycle-001-failure-diagnosis]]).
- **Both H1 and H2 must implement this** — see CEO verdict in `.factory/reviews/ceo-verdict-researcher.md`.

## 2. Continuous fidelity index is the missing inductive bias

Every method that beats baselines on IFC datasets (IFC-ODE2, IFC-GPODE, MFRNP-on-local-data) encodes fidelity as either:
- a continuous variable in the architecture (e.g., [[li2022ifc]]'s B(m)), or
- a residual stack across discrete levels (e.g., [[niu2024mfrnp]]).

v9 does **neither** — its `gate_mlp(softmax)` only mixes per-stream attention with no explicit fidelity scalar. **Any new family must encode fidelity explicitly** (continuous-m basis, FiLM-from-m, fidelity-aware FNO, or per-fidelity stacked residual).

## 3. FNO > Transolver for regular-grid PDE data

- `ifc_heat` / `ifc_poisson` are regular-grid PDE data.
- [[wu2024transolver]]'s slice-attention is designed for unstructured meshes → O(N·K) cost per sample with no inductive-bias benefit on a regular grid.
- [[li2020fno]]'s spectral conv is O(N log N) per FFT with smaller hidden state. 64×64 FFTs are essentially free on H100.
- **Strict upgrade** for both H1 and H2.

## 4. HF data scarcity (5 samples) is the binding constraint

Every architectural choice should be evaluated through "what happens with only 5 HF training points?" lens:
- **Coregionalization** shares the few HF samples across all fidelity outputs via B(m) → good.
- **Residual stacking** learns the HF δ on top of an upsampled-LF prediction → good (HF δ has 5 samples but LF base has 100).
- **Pure HF training** → bad.
- **v9's gated mixing** → bad in practice (HF residual MLP starves of HF signal).

## 5. `val_frac=0.2` in the smoke wrapper is harmful for HF-limited datasets

- 5 HF samples × 0.2 val_frac = 1 HF sample lost to validation → only 4 HF samples for training.
- **Recommendation for both H1 and H2**: use `val_frac=0.1`, or implement stratified per-fidelity train/val splits so HF is preserved.

## How to apply

- Both H1 (fno_coregionalization) and H2 (fno_mf_stack) MUST adopt findings 1, 2, 3, 5.
- Finding 4 is a design constraint to keep in mind when choosing hyperparameters (small K, weight decay, secondary supervision).

## Related

- [[cycle-001-failure-diagnosis]] — the diagnosis that produced these findings.
- [[cycle-001-candidate-ranking]] — H1/H2 already incorporate these.
- [[li2020fno]], [[li2022ifc]], [[niu2024mfrnp]] — supporting evidence.
