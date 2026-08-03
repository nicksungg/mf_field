# ifc pairing repair — staged regeneration (2026-08-03, cluster)

Executes the ifc half of CLUSTER_RUNBOOK step 4: the round-2 `ifc_poisson` pairing defect (round-2 report §5 item 5; preflight `pairing` hard-fail class).

## What was measured

The shipped `benchmark_42/core/{ifc_poisson,ifc_heat}` ladders draw an **independent condition set per fidelity rung**.
Measured on-disk 2026-08-03: 0 of the finer-rung condition rows appear at any coarser rung, for every rung pair, in both datasets.
So no derived-array rebuild can pair them — the fields simply do not exist at shared conditions — and every `hf − lf`, LF-teacher, and copy-LF construction on the shipped ladders is invalid.

Preflight's `pairing_check` on the shipped ladders (LF = fidelity_32, HF = fidelity_64, first 5 rows): `ifc_poisson` MISPAIRED (row-match 0.2), `ifc_heat` MISPAIRED (row-match 0.4).

## What was regenerated

Both datasets are local IFC-protocol replicas produced by `mf_field/generate_all_datasets.py` (`_make_poisson`, `_make_heat`; ifc_heat's condition ranges match `_make_heat.BOUNDS` exactly), so a faithful repaired ladder is available by re-solving.
`regenerate_ifc_paired.py` builds one shared condition pool per dataset and keeps nested prefixes per rung (train 100/50/20/5 at 8/16/32/64, test 128 at 64 only — the shipped protocol's counts), writing the ifc_raw layout to `regen_2026-08-03/ifc_paired/` (heavy arrays local-only, git-ignored).

Verification: nesting asserted row-by-row in-script (`pairing_report.json` per dataset), and preflight's `pairing_check` on the repaired arrays reads OK with row-match 1.0 for both datasets.

## What was deliberately NOT done

`benchmark_42/core/{ifc_poisson,ifc_heat}` are untouched: round-2 numbers were measured on the shipped ladders, and whether the repaired ladder replaces them on the round-3 panel is a launch-ADR panel-composition decision (`round3/PROGRAM_NOTE.md` §7.3), not this pipeline's call.
The staged arrays are the repair candidate for that ADR.

## Files

- `regenerate_ifc_paired.py` — the regeneration + nesting self-check.
- `regeneration_report.json` — machine-readable run record (seeds, counts, pairing checks).
