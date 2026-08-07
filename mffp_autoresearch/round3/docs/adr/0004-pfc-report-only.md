# ADR r3-0004: pfc moved to report-only (scored panel → 5 datasets)

**Status:** accepted (operator, Eloise, 2026-08-07 — "proceed with plan" on the scored-cell HOLD adjudication).
**Supersedes:** the scored-panel composition of ADR r3-0001 A1 for `sharp__phase_field_crystal_2d` only.
**Evidence:** `state/HOLD_history.jsonl` (2026-08-07 entry), orchestrator_flow stop-the-line record, preflight `degenerate_rows` on the scored cell.

## Finding

The eval layer scores pfc at `max(lf_fids)` = l2(64²) → l3(128²).
The crystalline-box fields (ADR r3-0002) are spectrally converged at 64²: exact per-row copy-LF gap ≤ 1.66e-6 on all 100 test rows — the scored cell contains no prediction task.
The certified reference 0.018257 is ~100% linear-interpolation error of the frozen ADR r2-0001 lift (`map_coordinates order=1`), not fidelity gap.
ADR r3-0002's "real gap" (bottom-rung median 4.5e-3 on test) is real but lives at l1→l3, which the eval layer never scores.
The regenerated arrays themselves are healthy physics; the defect is rung selection, structural to how smooth one-mode PFC crystals are.

## Decision

1. **Scored panel (round 3): 5 datasets** — `sharp__allen_cahn_2d`, `sharp__fisher_kpp_2d`, `sharp__cahn_hilliard`, `ifc_poisson`, `ifc_heat`.
   `sharp__phase_field_crystal_2d` becomes **report-only**, same status as `ext__helmholtz_2d` (ADR r3-0001 D2): models may still run it; its cells appear in reports flagged non-scoring; it does not enter the panel geomean or any claim clause.
2. **Anchors re-aggregate over the 5-dataset panel** (no new compute — per-cell values unchanged, pfc columns dropped from geomeans). Certified-reproduction seam unchanged (`PANEL6_R2` is historical).
3. **Batch-1 cards** (drafted pre-HOLD): pfc rows are removed from `recipe.datasets` and from falsification clauses via an `adr_r3_0004_addendum` field written by the orchestrator; locked brainstormer prose is untouched. Any literal `panel` datasets value is replaced by the explicit 5-name list (the literal resolves to the round-2 panel via `round2/project.yaml` — r3s3-B1 finding).
4. **The proper repair is prepared, not executed**: a draft ADR (coarse-rung scoring + spectral-lift reference) goes to the operator and mentor for sign-off, since it amends the frozen round-2 eval convention. If ratified, pfc can rejoin the scored panel mid-round under MUST #5.
5. **HF release**: the regenerated pfc arrays ship unchanged (they are correct physics); the dataset card and DEFECT_STATUS document the top-rung convergence prominently so downstream users do not grade interpolation error.

## Consequences

- Round-3 headline numbers are 5-dataset geomeans; not comparable to 6-dataset numbers computed before this ADR (three-instance lineage: ifc_heat promotion, ac trim, pfc exit).
- The launch preflight gate covers the 5 scored datasets + guards; pfc runs preflight in report-only mode (its `degenerate_rows` FAIL is the documented finding, not a gate blocker).
- `data_hashes.json` keeps pfc bound (drift detection for report-only use).
