# Round-3 launch gates

| gate | state | evidence |
|---|---|---|
| G1-r3 data | **GREEN** (2026-08-05) | ADR r3-0001 D1/D3 executed: option-A sharp swap (2026-08-03), repaired IFC adoption (`ifc_pairing_repair/adoption_manifest_2026-08-05.json`, in-place nesting verified), stripped view verified live-mirroring repaired arrays. |
| G2-r3 preflight | **GREEN** (2026-08-05) | `preflight_launch_2026-08-05.json` PASS, 2 adjudicated waivers (`preflight_launch_waiver_evidence_2026-08-05.md`); selftest green after the `--waive` additive-flags fix. |
| G3-r3 anchors | **PENDING** | Best-floor certified 75.0673 (`anchors/launch_anchors.json`); 4 card anchors PENDING_IFC_RESCORE on SLURM 66546256–66546267 (`ifc_rescore_jobs_2026-08-05.json`). Flip GREEN by re-running `tools/make_round3_anchors.py` after the jobs land (all cards CERTIFIED). |

Batch 1 dispatches only with all three gates GREEN (ADR D6, HOW_TO_LAUNCH §0).
