# ADR 0003 — Correction of program.md §12.3's quantified prior (operator action)

**Status:** accepted 2026-07-28 (operator: the orchestrator session, under Eloise's
"keep going" delegation)

## What was wrong

program.md §12.3 claimed: *"`mf_fno_ptr` achieved −21% on era5/pm_test with a
placeholder Laplacian residual"*, sourced from `akash/results/FINDINGS.md`. The
s3_testtime batch-1 websearcher refuted this **in-repo**:

- `mf_field/akash/models/mf_fno_ptr/refine.py`'s `RESIDUAL_REGISTRY` contains only
  `ifc_poisson` and `ifc_heat` — on era5/pm_test refinement is a documented NO-OP.
- In `mf_field/akash/results/bench_metrics_subset.csv`, `mf_fno_ptr` and
  `mf_fno_transfer_film` are byte-identical on era5 to 17 digits
  (`0.07231217372227801`); the "0.0585" was `mf_fno_foundation`'s era5 number,
  mis-read across rows.
- Where the mechanism DID run (`ifc_poisson`): −1.5%, inside the CI, at 163×
  inference latency (17.61 ms vs 0.108 ms per sample).

Additionally: a true governing residual is computable for only **1 of 6** panel
datasets (`ext__helmholtz_2d`; steady, condition vector fully determines `f`).
The four phase-field/reaction snapshots lack ∂ₜu and (except Cahn-Hilliard) the
IC; `ifc_poisson`'s source decode is not shipped.

## Decision

program.md §12.3 is corrected (minimal edit): the false −21% prior is replaced
with the verified facts above, and the batch-1 seed direction is re-scoped to
Helmholtz-only exact-residual refinement (or equilibrium-projection alternatives),
with the ill-conditioning caveat (ENS, arXiv:2606.27354) noted.

## Why this does not violate immutable #3

§5.3 forbids the loop's AGENTS from editing the spec. This is an operator
correction of a factual error in the spec's own evidence base, recorded here with
the full refutation trail (websearches/s3_testtime/batch_1/). The metric, panel,
seeds, caps, and all other spec surfaces are untouched.
