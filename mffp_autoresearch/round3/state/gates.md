# Round-3 launch gates

**2026-08-07 (resolution): HOLD cleared under ADR r3-0004 — pfc report-only, scored panel = 5 datasets.**
Lineage of the day: launch certified on 6 datasets (morning) → scored-cell repoint of the fifth-class checks (r3s4-B1 escalation) exposed pfc's scored cell (l2→l3) as spectrally converged, all 100 test rows task-void → HOLD set, G2/G3 re-opened → operator adjudication ("proceed with plan") → pfc to report-only, gates re-certified on the 5-dataset panel below.
The pfc finding and the pending frozen-eval spectral-lift repair ADR live in `docs/adr/0004-pfc-report-only.md`.

| gate | state | evidence |
|---|---|---|
| G1-r3 data | **GREEN** (2026-08-05) | ADR r3-0001 D1/D3 executed: option-A sharp swap (2026-08-03), repaired IFC adoption (`ifc_pairing_repair/adoption_manifest_2026-08-05.json`, in-place nesting verified), stripped view verified live-mirroring repaired arrays. |
| G2-r3 preflight | **GREEN** (2026-08-07, ADR r3-0004 scope) | `preflight_launch_5ds_2026-08-07.json` PASS over the 5-dataset scored panel + guards, fifth-class checks on the scored cell (post-repoint): ch `cell_stability` warn as priced (scored-cell MDD), ac_2d clean post-trim, fkpp fidelity_gap warn (adjudicated), 2 waivers carried. pfc's honest `degenerate_rows` FAIL is preserved in `preflight_launch_2026-08-07.json` as the ADR r3-0004 finding record (not a gate input — pfc is report-only). Full-root sweep archived at `preflight_fullroot_sweep_2026-08-07.json`. Data-hash manifest bound: `data_hashes.json` (6 datasets incl. report-only pfc, verify OK). |
| G3-r3 anchors | **GREEN** (2026-08-07, ADR r3-0004 re-aggregation) | All 4 cards CERTIFIED over the 5-dataset scored panel (aggregation-only change; per-cell values unchanged): r2s1-B2 [26.24, 26.35, 26.40], r2s1-B3 [25.59, 25.50, 25.45], r2s2-B1 [21.14, 19.18, 33.87] (known ifc_poisson seed-2 instability), r2s3-B3 [11.98, 12.56, 12.45]. Best-floor geomean **34.4198** (lineage: 75.0673 → 38.6300 → 36.3912 → 34.4198). Validation seam unchanged (`PANEL6_R2` historical reproduction still passes). `state/anchors/launch_anchors.json`. |

Batch 1 dispatches only with all three gates GREEN (ADR D6, HOW_TO_LAUNCH §0).
