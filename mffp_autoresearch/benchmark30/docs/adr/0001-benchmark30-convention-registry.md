# ADR b30-0001 — upsample-convention registry extension for benchmark_30

Status: ACCEPTED 2026-08-12 (campaign-scoped extension of ADR r2-0001; spec D4).
Scope: the two VENDORED registries only (`benchmark30/eval/panel_data.py`, `benchmark30/family/r3s2_route_b30/upsample.py`); round-2/3 files untouched.
Evidence: `0001-convention-evidence-DRAFT.md` (per-dataset generator/solver citations); reference-legitimacy audit in §3 below.
Enforcement: `tests/test_registry.py` (coverage, cross-copy agreement of new IDs, synthetic semantics, pinned totals) + the append-only guards in `tests/test_vendor_integrity.py` and `tests/test_family_integrity.py`.

## 1. Decision

The 16 previously unclassified 2-D benchmark_30 datasets are classified as follows; the 5 1-D datasets (`sharp__sod_1d` [already classified], `sharp__burgers_1d`, `sharp__shallow_water_1d`, `sharp__porous_medium_1d`, `allen_cahn_generated`) take the family's 1-D path, which bypasses `resolve_convention` entirely.

| convention | new datasets |
| --- | --- |
| `dirichlet_node` (+3) | poisson_generated, darcy_generated, sharp__helmholtz_2d |
| `periodic_node` (+1) | sharp__porous_medium_2d |
| `legacy_cell` (+12) | poisson_local, heat_generated, lid_driven_cavity_generated, era5, ext__rayleigh_benard_2d, ext__wave_2d, ext__eikonal_2d, ext__cahn_hilliard_2d, ext__pressure_poisson_poiseuille, sharp__euler, sharp__burgers_2d, sharp__shallow_water_2d |

`allen_cahn_generated` is 1-D by the authoritative `data_adapters.geometry.KNOWN_GRIDS` registration (`(1, L)`); its dataset README's "16x16" is wrong and must not be trusted by any tooling.

## 2. Rationale (summary; full citations in the evidence draft)

- **dirichlet_node**: all three are interior-node finite-difference Dirichlet solves with `h = 1/(n+1)` grid construction — structurally identical to the certified variant-E case `ext__helmholtz_2d`.
- **periodic_node**: `sharp__porous_medium_2d` is a node-registered periodic solve (`j·L/res` coordinates, periodic roll stencil) on an exactly nested 64/128/256 ladder, satisfying variant C's nesting assert.
- **legacy_cell** splits into three sub-cases, all documented per dataset in the evidence draft:
  - genuine cell-centred discretizations (sharp__euler and sharp__shallow_water_2d, PyClaw finite-volume; ext__pressure_poisson_poiseuille, explicit `(j+0.5)/n` centres);
  - **accepted approximations** (spec D4): endpoint-node `linspace` grids that no existing variant implements (lid_driven_cavity_generated, ext__rayleigh_benard_2d, ext__wave_2d, ext__eikonal_2d, heat_generated's spatial axis, era5's latitude axis) — minting an `endpoint_node` variant is ruled out by D2/D3 (frozen family, byte-identical metric path), so the certified fallback is recorded WITH its known mismatch;
  - the special case `ext__cahn_hilliard_2d`: structurally periodic-node but on a NON-nested 24→64 ladder that variant C's assert rejects; classified legacy_cell as an accepted approximation, misfit documented (exactness at shared `j·L/24 ↔ k·L/64` nodes is missed by a fixed offset), carried as a report caveat.
  - `sharp__burgers_2d` is cell-centred but periodic, so legacy's clamped edges approximate the wrap seam — accepted, documented.

## 3. Reference-legitimacy audit (r2-0001 tradition)

For every dataset where the structural evidence proposed a NON-default convention, the copy-LF reference was computed under both candidates on the real test split (audit of the REFERENCE construction, not model selection; the same criterion ADR r2-0001's audit used: a convention change must not make the reference worse).

| dataset | proposed | copy-LF nRMSE (proposed) | copy-LF nRMSE (legacy_cell) | verdict |
| --- | --- | --- | --- | --- |
| poisson_generated | dirichlet_node | 3.116437 | 3.152770 | proposed better — CONFIRMED |
| darcy_generated | dirichlet_node | 0.013662 | 0.018201 | proposed 25% better — CONFIRMED |
| sharp__helmholtz_2d | dirichlet_node | 0.988898 | 0.996634 | proposed better — CONFIRMED |
| sharp__porous_medium_2d | periodic_node | 0.016992 | 0.042321 | proposed 2.5x better — CONFIRMED |

The lineage tension flagged in the evidence draft (same-generator ifc datasets certified legacy_cell in round 2) is resolved by these numbers: the dirichlet mapping improves the reference for the three `h = 1/(n+1)` datasets, so the structural classification stands.

## 4. Registry revision

`registry_revision = b30-0001` — recorded in the sealed staging manifest (D12) and thereby bound into every cache/checkpoint/result identity.

## 5. What this ADR does NOT do

- No change to any round-2/3 file, hash, or state.
- No new upsample variants, no assert relaxation (D2/D3).
- No reclassification of any previously classified dataset; the pre-existing pfc cross-copy divergence (ADR r3-0005) is preserved and exempted from the agreement guard.
