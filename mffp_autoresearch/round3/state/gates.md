# Round-3 launch gates

| gate | state | evidence |
|---|---|---|
| G1-r3 data | **GREEN** (2026-08-05) | ADR r3-0001 D1/D3 executed: option-A sharp swap (2026-08-03), repaired IFC adoption (`ifc_pairing_repair/adoption_manifest_2026-08-05.json`, in-place nesting verified), stripped view verified live-mirroring repaired arrays. |
| G2-r3 preflight | **GREEN** (2026-08-05) | `preflight_launch_2026-08-05.json` PASS, 2 adjudicated waivers (`preflight_launch_waiver_evidence_2026-08-05.md`); selftest green after the `--waive` additive-flags fix. |
| G3-r3 anchors | **PENDING (re-opened by ADR r3-0002)** | ifc leg DONE: all 4 cards certified on repaired ifc (2026-08-06; r2s1-B2 29.54, r2s1-B3 29.87, r2s2-B1 28.30-wide-CI, r2s3-B3 arm-contrast; seam-trip + r2s2 datasets-arg fixes en route). pfc leg OPEN: ADR r3-0002 crystalline-box regeneration (SLURM 66604010) → swap → pfc reference + anchor-cell re-score → re-run `tools/make_round3_anchors.py`. Batch 1 waits on full certification. |

Batch 1 dispatches only with all three gates GREEN (ADR D6, HOW_TO_LAUNCH §0).
