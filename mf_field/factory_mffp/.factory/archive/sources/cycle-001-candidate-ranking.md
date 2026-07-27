---
name: cycle-001-candidate-ranking
description: Top-2 candidate model families for cycle 001 — H1 fno_coregionalization (~1-3 min smoke), H2 fno_mf_stack (~3-5 min smoke). Both fit 30 min H100 budget by ~10×. Ranking matches CEO prior.
metadata:
  type: reference
tags:
  - factory
  - source
  - candidate-ranking
  - cycle-001
source: factory-archivist
date: 2026-05-15
cycle: "001"
project: factory_mffp
---

# Cycle 001 — Top-2 Candidate Model Families

Per `hypothesis_budget.max_new = 2`. Ranking matches the CEO's prior (fno_coregionalization > fno_mf_stack > transolver_residual > siren_film_fidelity) and is confirmed by the Researcher with concrete cost and impact estimates.

## H1 — `fno_coregionalization` (strongly recommended pick #1)

- **Why best for F1**: F1 is fundamentally a value-scale-across-fidelities problem (see [[cycle-001-failure-diagnosis]]). [[li2022ifc]]'s `f(x, m) = B(m) · h(x, m)` is *built* to express this — as `m` increases continuously, the basis B(m) rescales the output. Pairing with an FNO backbone for h(·, m) keeps it cheap (regular-grid native, resolution-invariant) and avoids the neural-ODE training cost (~7.84 s/epoch in the paper) that makes full IFC-ODE infeasible at smoke speed.
- **Concrete design** (reference, not prescriptive):
  - Pad/upsample inputs to HF grid (64×64) using bilinear (matches paper §6.1).
  - FNO backbone: 3–4 spectral conv blocks, k_max=12, hidden=64. Output latent `h(x) ∈ R^{K × H × W}` with K=10–20.
  - Coregionalization head: small MLP `B(m) = MLP([m, m²])` (NOT neural ODE). Output `y(x) = Σ_k B_k(m) · h_k(x)`.
  - Loss: MSE summed across all fidelities present in batch; each element carries its own m. At inference, m=1.
- **Smoke wall time**: ~1–3 min for both datasets together. ~10× under 30 min budget.
- **Expected impact**: ifc_poisson 0.05–0.15 (massive drop from 18.5; still above paper's 0.036). ifc_heat 0.05–0.1 (within striking distance of paper 0.074).
- **Risk**: only 5 HF samples (2-3 after val split) → K-dim basis may overfit. Mitigation: small K (10), weight decay, use L3 (32×32) data as secondary supervision.
- **Inspirations**: [[li2022ifc]], [[li2020fno]].

## H2 — `fno_mf_stack` (recommended pick #2)

- **Why second**: MFRNP-style residual stacking has the strongest documented numbers on related `poisson_local`/`heat_local` (0.0046–0.0076 in MFRNP's setting). The residual `y_HF = aggregate(decoded_LFs) + δ` lets the model learn the **correction** rather than the full output → much better-conditioned given limited HF data.
- **Concrete design**:
  - One FNO per fidelity level (4 small FNOs, ~50k params each → ~200k total).
  - FNO_k predicts y at level k; aggregation trains LF decoders to maximize cross-fidelity info sharing (the MFRNP twist).
  - Final HF output = `aggregate(decoded_LFs upsampled to 64×64) + δ` where δ is the HF FNO's prediction.
- **Smoke wall time**: ~3–5 min. Under budget.
- **Expected impact**: similar order to H1 on ifc_poisson; possibly *better* on ifc_heat (MFRNP-on-heat_local hits 0.004 — well under IFC's 0.074 in a different setting).
- **Risk**: 4 FNOs is more wall-clock than 1 → keep smoke decoder small (hidden=32); put full sizes in `full_config.json`.
- **Inspirations**: [[niu2024mfrnp]], [[li2020fno]].

## Deferred to later cycles

- `transolver_residual` — hard HF−LF residual on Transolver. Useful ablation but outside budget.
- `siren_film_fidelity` — FiLM-conditioned SIREN. Diversity option, no specific reason to expect SOTA.
- `fire_field` — [[sung2026fire]] in-context regression adapted to fields. Non-trivial; defer.
- `deeponet_branch_fidelity` — [[yang2025mfdeeponet]]-style. Defer.
- `transolver_pinn_residual` — PINN-augmented Transolver. Defer.
- `transolver_autoencoder_fusion` — [[nietocentenero2025mfae]]-style. Defer.

## Shared implementation hygiene (both picks)

Propagated from [[cycle-001-cross-cutting-findings]]:
- **Per-fidelity output normalization** (largest single win — could drop ifc_poisson from 18.5 to ~1.0 even without backbone change).
- Use continuous-`m` index from `cat.pkl`'s `t_list`.
- Reduce `val_frac` from 0.2 → 0.1 (or stratified split) to preserve HF training samples.
- Builder MUST run `python smoke_eval.py --epochs 2 --dataset_dir data/ifc_heat --out /tmp/x.json --ckpt_dir /tmp/c --seed 0` before declaring ready.

## Backlog references

- H1 → `.factory/strategy/backlog.md` line 27 (`fno_coregionalization`).
- H2 → `.factory/strategy/backlog.md` line 26 (`fno_mf_stack`).

## Related

- [[cycle-001-failure-diagnosis]] — the F1/F2/F3 picture these candidates target.
- [[cycle-001-cross-cutting-findings]] — shared hygiene rules.
- [[li2022ifc]], [[niu2024mfrnp]], [[li2020fno]] — inspiration papers.
