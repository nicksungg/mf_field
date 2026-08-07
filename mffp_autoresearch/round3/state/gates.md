# Round-3 launch gates

| gate | state | evidence |
|---|---|---|
| G1-r3 data | **GREEN** (2026-08-05) | ADR r3-0001 D1/D3 executed: option-A sharp swap (2026-08-03), repaired IFC adoption (`ifc_pairing_repair/adoption_manifest_2026-08-05.json`, in-place nesting verified), stripped view verified live-mirroring repaired arrays. |
| G2-r3 preflight | **GREEN** (2026-08-07, refreshed) | `preflight_launch_2026-08-07.json` PASS over panel+guard set with the fifth-class checks live (ADR r3-0003 D4): pfc/ch `cell_stability` warns as priced, ac_2d clean post-trim, 2 adjudicated waivers carried. Full-root sweep archived at `preflight_fullroot_sweep_2026-08-07.json` (new checks confirmed firing on known non-panel degenerates). Data-hash manifest bound: `data_hashes.json` (6 datasets, verify OK). Original 08-05 record retained. |
| G3-r3 anchors | **GREEN** (2026-08-07) | All 4 cards CERTIFIED on the final repaired panel (pfc box-swap + ac trim + repaired ifc): r2s1-B2 [29.08, 29.12, 29.16], r2s1-B3 [28.33, 28.18, 28.14], r2s2-B1 [24.24, 22.37, 35.92] (known ifc_poisson seed-2 instability), r2s3-B3 [15.21, 15.85, 15.71]. pfc re-score jobs 66610525–36 all COMPLETED, 27 fresh entries `cached:false` against reference 0.018257. Validation seam: certified-summary reproduction with pfc/ac/ifc void-substitution (loader restricted to `PANEL6_R2`). `state/anchors/launch_anchors.json`. HOLD cleared same day (operator adjudication 2026-08-06 "Repair, then launch"; `HOLD_history.jsonl`). |

Batch 1 dispatches only with all three gates GREEN (ADR D6, HOW_TO_LAUNCH §0).
