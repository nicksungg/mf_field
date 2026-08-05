# Launch preflight evidence — round-3 panel, 2026-08-05

Companion to `preflight_launch_2026-08-05.json` (verdict PASS, 2 waivers).
Run post-IFC-swap (ADR r3-0001 D3) with the fixed `--waive` handling (repeated flags are now additive; `nargs="*"` without `action="extend"` silently kept only the last flag — an earlier run of this launch preflight produced a spurious helmholtz FAIL that way; selftest re-run green after the fix).

## Waivers (carried from 2026-08-03 adjudication, unchanged data)

- `ext__helmholtz_2d:completeness` — witness false-positive from resonance sensitivity; re-solve reproduces flagged rows at rel-L2 ~1e-15. Helmholtz is report-only in round 3 (ADR D2), so this waiver is documentation, not a scored-panel exception.
- `sharp__sod_1d:pairing` — best-match ambiguity among near-duplicate Riemann rows; cross-level condition arrays bit-identical. Guard dataset, not scored.

## ifc NO_DATA rows — covered by direct verification

Preflight's instruments read the factory npz layout only; `ifc_poisson`/`ifc_heat` are ifc_raw.
The decisive check for their defect class (pairing) was run directly on the swapped-in arrays (adoption manifest, `mffp_autoresearch/ifc_pairing_repair/adoption_manifest_2026-08-05.json`): every finer-rung condition row appears verbatim at the coarser rung, all rung pairs, both datasets (nested: true), matching the staged `pairing_report.json` (row-match 1.0).

## Expected warnings (documented, not waived)

- `sharp__phase_field_crystal_2d`, `sharp__fisher_kpp_2d` `fidelity_gap`: the known weak-gap physics under complete band-limited ICs; carried as standing caveats per ADR D4; `true_gap_sweep` remains the open recipe question.
- guards `heat_local`, `fluid` `nn_baseline`: triviality screen on guards; guards are not meant to be won.
