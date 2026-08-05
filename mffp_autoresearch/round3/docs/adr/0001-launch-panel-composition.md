# ADR r3-0001: Round-3 launch — panel composition and fix-option assignment

**Status:** accepted (operator go, Eloise, 2026-08-05; mentor option-A endorsement 2026-08-05); **amended same day (A1: ifc_heat promoted — see Amendment A1)**.
**Supersedes:** the open panel-composition items in `round3/PROGRAM_NOTE.md` §7.3 and `CONDITION_COMPLETENESS_BRIEFING_2026-08-03.md` Part III "Still open".

## Context

Round 2 closed with four data-side defects found in-round: incomplete condition vectors on the pattern formers, helmholtz closed-form triviality, the ifc ladder pairing defect, and the pfc no-gap issue.
The repair pipeline (option A, band-limited parametric ICs) was executed 2026-08-03 and the five regenerated sharp variants are swapped in with COMPLETE certificates (reconstruction rel-L2 = 0.0).
The mentor reviewed the briefing and endorsed option A on 2026-08-05, ratifying the operator-approved repair (`condition_completeness_proposal/APPROVAL.md`).
Nested-condition repaired IFC ladders were regenerated and staged at `regen_2026-08-03/ifc_paired/` (row-match 1.0; `mffp_autoresearch/ifc_pairing_repair/regeneration_report.json`); the shipped ladders remained untouched pending this ADR.
The repaired-panel preflight passed with two adjudicated waivers (`round3/state/preflight_waiver_evidence_2026-08-03.md`).
Round-2's claimable slate was re-scored at 3 seeds on the repaired sharp data + shipped ifc rows (`round3/state/anchor_summary_3seed_2026-08-03.json`).

## Decisions

### D1 — Fix-option assignment: option A everywhere applicable

`sharp__phase_field_crystal_2d`, `sharp__fisher_kpp_2d`, `sharp__allen_cahn_2d` (and the 1-D variants) use option A, band-limited parametric ICs stored in the condition vector.
`sharp__cahn_hilliard` already satisfies option A in the broad sense (IC coefficients in its 19-D vector) and is unchanged.
No dataset declares option B (`stochastic_map`); it remains a standing option for a future distributional track.
Option C (IC field as model input) stays drafted in the briefing, not formalized; no round-3 dataset uses it.

### D2 — Helmholtz: excluded from the scored panel, retained report-only

`ext__helmholtz_2d` leaves the scored panel geomean.
Rationale (lineage: r1 ADRs 0009/0010, ADR r2-0004): its HF test fields reproduce from the condition vector alone to rel-L2 2.2e-13 via an exact closed-form solve, so a trained model can learn to *be* the exact operator without ever calling a solver — the dataset measures formula re-implementation, not multi-fidelity or learning skill.
This is distinct from the (banned) act of calling a solver at test time; the ban does not protect against a learnable exact closed form.
The dataset stays on disk; experiments may report helmholtz numbers, and every mention carries the standing triviality flag, exactly as in round 2.

### D3 — IFC ladders: adopt the repaired nested-condition ladders

The staged arrays at `regen_2026-08-03/ifc_paired/{ifc_poisson,ifc_heat}` replace the shipped `benchmark_42/core/{ifc_poisson,ifc_heat}` ladders.
The shipped (disjoint, mispaired) ladders are archived in place under `benchmark_42/core/_shipped_disjoint_backup_2026-08-05/` — archived, never deleted, mirroring the sharp-swap convention.
The swap is recorded in `mffp_autoresearch/ifc_pairing_repair/adoption_manifest_2026-08-05.json`.

**Consequence — ifc anchor cells are void.**
The 3-seed anchor re-score used the shipped ifc_poisson rows; the repaired ladder draws new train/test rows (seeds 20260803/20260804).
Every ifc model-anchor cell must be re-scored on the repaired rows before batch 1; training-free ifc floors are recomputed immediately post-swap.
Round-2 ifc numbers and repaired-ladder ifc numbers are never comparable; any side-by-side carries this flag.

### D4 — Round-3 scored panel and guards (as amended by A1: 6 datasets)

Scored panel: `sharp__phase_field_crystal_2d`, `sharp__allen_cahn_2d`, `sharp__fisher_kpp_2d`, `sharp__cahn_hilliard`, `ifc_poisson` (repaired ladder), and — per Amendment A1 — `ifc_heat` (repaired ladder).
Guard set unchanged: `heat_local`, `fluid`, `sharp__sod_1d`.
Standing caveats carried into every claim: pfc and fisher_kpp weak fidelity gap under the complete band-limited IC (preflight "expected warnings"; `true_gap_sweep` remains the open recipe question), and ifc_poisson's affine structure.
Per PROGRAM_NOTE MUST #5 the panel is mutable in-round only under an explicit ADR.

### D5 — Preflight waivers folded in

`ext__helmholtz_2d:completeness` — witness false-positive from legitimate resonance sensitivity (re-solve reproduces flagged rows at rel-L2 ~1e-15); moot for the scored panel after D2, retained for report-only use.
`sharp__sod_1d:pairing` — best-match ambiguity among near-duplicate Riemann rows; cross-level condition arrays bit-identical; sod is a guard, not scored.
Preflight is re-run after the D3 swap and archived to `round3/state/`; launch refuses on any new unwaived hard fail (PROGRAM_NOTE MUST #1).

### D6 — Launch anchors recomputed over the D4 panel

The certified 6-dataset anchor values (best-floor 46.3911; r2s2-B1 24.3725 etc.) do not transfer to the 5-dataset panel.
Best-floor and noise-floor anchors are recomputed from per-dataset floor artifacts (helmholtz dropped; ifc floor from repaired rows).
The four anchor cards (r2s2-B1, r2s3-B3, r2s1-B2, r2s1-B3) are re-scored at 3 seeds on repaired-ifc only; their sharp-panel per-seed cells are reused from the existing re-score artifacts.
Round 3 does not launch batch 1 until the recomputed anchors are certified into `round3/state/anchors/`.

## Consequences

- The scored panel is 100% completeness-certified: every dataset's HF field is exactly reconstructible from its stored condition vector, so the round-2 aleatoric exclusion of criterion 2 no longer applies to the sharp panel.
- One SLURM re-anchor job (4 cards × 3 seeds × ifc_poisson-repaired, plus training-free floors) is a launch prerequisite; completion mail wired per operator convention.
- The regime question round 3 can now genuinely ask: with complete condition vectors, can any condition→HF model reach field-level structure beyond the scalar-deep law, and does LF-at-train still matter on an honest panel?

## Amendment A1 (2026-08-05, operator-approved): ifc_heat promoted to the scored panel

Eloise asked whether round 3 should score 6 datasets with a helmholtz replacement; adjudicated A (promote `ifc_heat`) over certifying `ext/gray_scott_2d` (needs a registration-convention audit, gap measurement, and floors — instrument work that would delay G3) or staying at 5.
Evidence for readiness, measured 2026-08-05 on the repaired ladder: NN-in-condition floor nRMSE 0.10316 and train-mean 0.13073 (non-trivial), LF32→HF64 gap ≈ 0.01143 at shared nested rows (real multi-fidelity content), published paper bar 0.074 as skill denominator (li2022ifc IFC-ODE2, mirroring ifc_poisson's 0.036 convention — test ships HF only), parabolic physics the panel otherwise lacks, and a hedge against ifc_poisson's affine degeneracy.
Executed with the amendment: `ifc_heat` entry added to `round2/eval/copylf_baselines.json` (pre-amendment file archived at `copylf_baselines_pre_ifc_heat_2026-08-05.json`), stripped view built (test = fidelity_64 only), floors + anchor-card cells added to the launch re-score (D6 applies to ifc_heat identically), launch anchors recomputed over the 6-dataset panel.
`ext/gray_scott_2d` remains the standing candidate for an in-round panel addition under PROGRAM_NOTE MUST #5.
