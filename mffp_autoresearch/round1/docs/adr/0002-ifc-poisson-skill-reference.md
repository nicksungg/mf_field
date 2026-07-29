# ADR 0002 — `ifc_poisson` skill reference is the paper bar, not copy-LF

**Status:** accepted 2026-07-28

## Context

The spec (§2) defines `skill = nRMSE(model) / nRMSE(copy-LF)` per panel dataset.
During gate G2 the eval layer hit a data reality the spec missed: the IFC datasets'
test split ships **only the HF fidelity** (`ifc_poisson/test/fidelity_64/` — see the
dataset README: "test ships only at the top fidelity"). Copy-LF is therefore
undefined on the split we score.

## Decision

For `ifc_poisson` (and any future dataset whose test split has no LF), the skill
denominator is the **published paper bar** from the guarded, read-only
`baselines/paper_baselines.json` — for `ifc_poisson`: 0.036 (IFC-ODE2; the stronger
IFC-GPODE 0.018 stays a stretch reference in program.md §12).

`copylf_baselines.json` records `reference_type: copylf | paper_bar` per dataset, and
`score_panel.py` treats both uniformly.

## Consequences

- Skill < 1 on `ifc_poisson` now *means* "beats the published paper", which is exactly
  spec success criterion 1 — the semantics align rather than diverge.
- The panel geomean mixes two reference types; per-dataset skill tables (mandatory in
  every card part 5) keep this legible.
- Train-split copy-LF for IFC was considered and rejected: different sample
  distribution, N_hf = 5, and it would make the denominator an anecdote.
