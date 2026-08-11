# Round-3 launch gates

**2026-08-10 (resolution): ADR r3-0005 phase 2 COMPLETE — pfc restored to the scored panel (6 datasets).**
Scored cell L1(32²)→L3(128²) with the exact spectral reference (0.012358); serving swap + `panel_data` amendment seam-verified byte-exact on every other dataset; 18 re-score cells landed stale-gate CLEAN (incl. the re-vendored r2s3 lift); fifth-class preflight on the new cell: `degenerate_rows` OK, `cell_stability` OUTLIER_DOMINATED (priced: MDD 65.8%), verdict PASS (`state/preflight_pfc_adr0005_2026-08-10.json`).
G3 re-certified on the 6-dataset panel: best-floor lineage 75.0673 → 38.6300 → 36.3912 → 34.4198 → **38.8368**; all 4 anchor cards CERTIFIED with pfc cells (r2s2-B1's pfc cell 63775 carries the known unregularised-LSI caveat, pre-flagged by r3s2 mechanism work).


**2026-08-10 (resolution): STOP-THE-LINE #2 HOLD cleared — stale-checkpoint anchor contamination repaired, G3 re-certified below.**
The launch-anchor ifc_poisson cells that had been re-scored with pre-repair weights (14 legs across the 4 anchor cards) were quarantined, fresh-trained (jobs 89201–89211, all COMPLETED, artifacts verified), re-audited CLEAN with `--fail-on-stale`, and the anchors rebuilt through the now-mandatory stale-checkpoint gate in `tools/make_round3_anchors.py`.
Diff confined to ifc_poisson columns + derived aggregates; best-floor geomean unchanged.

**2026-08-07 (resolution): HOLD cleared under ADR r3-0004 — pfc report-only, scored panel = 5 datasets.**
Lineage of the day: launch certified on 6 datasets (morning) → scored-cell repoint of the fifth-class checks (r3s4-B1 escalation) exposed pfc's scored cell (l2→l3) as spectrally converged, all 100 test rows task-void → HOLD set, G2/G3 re-opened → operator adjudication ("proceed with plan") → pfc to report-only, gates re-certified on the 5-dataset panel below.
The pfc finding and the pending frozen-eval spectral-lift repair ADR live in `docs/adr/0004-pfc-report-only.md`.

| gate | state | evidence |
|---|---|---|
| G1-r3 data | **GREEN** (2026-08-05) | ADR r3-0001 D1/D3 executed: option-A sharp swap (2026-08-03), repaired IFC adoption (`ifc_pairing_repair/adoption_manifest_2026-08-05.json`, in-place nesting verified), stripped view verified live-mirroring repaired arrays. |
| G2-r3 preflight | **GREEN** (2026-08-07, ADR r3-0004 scope) | `preflight_launch_5ds_2026-08-07.json` PASS over the 5-dataset scored panel + guards, fifth-class checks on the scored cell (post-repoint): ch `cell_stability` warn as priced (scored-cell MDD), ac_2d clean post-trim, fkpp fidelity_gap warn (adjudicated), 2 waivers carried. pfc's honest `degenerate_rows` FAIL is preserved in `preflight_launch_2026-08-07.json` as the ADR r3-0004 finding record (not a gate input — pfc is report-only). Full-root sweep archived at `preflight_fullroot_sweep_2026-08-07.json`. Data-hash manifest bound: `data_hashes.json` (6 datasets incl. report-only pfc, verify OK). |
| G3-r3 anchors | **GREEN** (2026-08-10, stale-checkpoint repair rebuild) | All 4 cards CERTIFIED over the 5-dataset scored panel with fresh-trained ifc_poisson cells (stale-gate enforced at build): r2s1-B2 [23.69, 23.79, 23.84], r2s1-B3 [25.59, 25.50, 25.45] (unchanged — family re-fits deterministically at score time), r2s2-B1 [20.14, 19.04, 33.87] (known ifc_poisson seed-2 instability; seed 2 was audited CLEAN and kept), r2s3-B3 [11.01, 11.20, 11.30]. Best-floor geomean **34.4198** unchanged (training-free floors are checkpoint-independent; lineage: 75.0673 → 38.6300 → 36.3912 → 34.4198). Validation seam unchanged (`PANEL6_R2` historical reproduction still passes). `state/anchors/launch_anchors.json`; repair record `state/stale_ckpt_repair_jobs_2026-08-09.json`. Prior 2026-08-07 evidence line superseded: its ifc_poisson columns were the contaminated values. |

Batch 1 dispatches only with all three gates GREEN (ADR D6, HOW_TO_LAUNCH §0).
