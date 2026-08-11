# Round-3 launch gates

**2026-08-10 (resolution): ADR r3-0007 executed — ifc_poisson report-only, scored panel = 5 datasets (option C, operator decision).**
Panel amended in `tools/make_round3_anchors.py` (PANEL explicit; `REPORT_ONLY = [ifc_poisson]`; both audit gates walk `AUDIT_PANEL` = scored + report-only, the pfc/r3-0004 precedent).
Anchors rebuilt through the binding gate (census: 0 bound legs, pure pass-through) and the stale gate: all 4 cards CERTIFIED on the 5-ds panel, best-floor lineage extends 38.8368 → **53.2146**; ifc_poisson values carried per-card as `report_only_per_dataset_mean_skill`.
Baselines: film 5-ds geomean 32.2165 (copy-LF units); U-Net/film panel ratio 0.9805 — a statistical DEAD HEAT (cross-seed ratios 0.94–1.04, 6/9 below 1), so the ADR r3-0006 film denominator STANDS; evidence reported to the operator per the recorded best-of-zoo rule.
G2 preflight scope is unchanged by construction: no data changed, ifc_poisson remains in `data_hashes.json` and the preflight record as a (now report-only) dataset.
ADR: `docs/adr/0007-ifc-panel-composition.md`.

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
| G2-r3 preflight | **GREEN** (2026-08-10, ADR r3-0005 scope) | Base certification `preflight_launch_5ds_2026-08-07.json` PASS over the then-5-dataset scored panel + guards (ch `cell_stability` warn priced, ac_2d clean post-trim, fkpp fidelity_gap warn adjudicated, 2 waivers carried); extended 2026-08-10 by `preflight_pfc_adr0005_2026-08-10.json` PASS on pfc's new scored cell L1→L3 (`degenerate_rows` OK 0/100 void, `cell_stability` OUTLIER_DOMINATED priced at MDD 65.8%) — pfc's old-cell `degenerate_rows` FAIL in `preflight_launch_2026-08-07.json` stands as the ADR r3-0004 finding record for the repaired defect. Full-root sweep archived at `preflight_fullroot_sweep_2026-08-07.json`. Data-hash manifest bound: `data_hashes.json` (6 datasets, verify OK). |
| G3-r3 anchors | **GREEN** (2026-08-10, ADR r3-0007 rebuild) | All 4 cards CERTIFIED over the 5-dataset scored panel (binding gate: 0 bound legs, pass-through; stale gate clean): r2s1-B2 [37.78, 37.84, 37.90], r2s1-B3 [39.19, 38.96, 38.89], r2s2-B1 [140.23, 135.40, 141.34], r2s3-B3 [18.16, 19.11, 18.89]. Best-floor geomean **53.2146** (lineage: 75.0673 → 38.6300 → 36.3912 → 34.4198 → 38.8368 → 53.2146). ifc_poisson carried per card as `report_only_per_dataset_mean_skill`. `PANEL6_R2` validation seam passes. `state/anchors/launch_anchors.json`; `docs/adr/0007-ifc-panel-composition.md`. Prior 6-ds row below retained as the ADR r3-0005-era record. |
| G3-r3 anchors (superseded 2026-08-10) | 6-ds era (ADR r3-0005 phase-2 rebuild) | All 4 cards CERTIFIED over the 6-dataset scored panel (stale-gate enforced at build; ifc_poisson cells fresh-trained per the STOP-THE-LINE #2 repair; pfc cells scored on the spectral rung-1 convention): r2s1-B2 [28.51, 28.54, 28.58], r2s1-B3 [30.23, 30.08, 30.04], r2s2-B1 [77.03, 72.59, 120.83] (carries the pfc cell 63775 unregularised-LSI blow-up, pre-flagged by r3s2 mechanism work and caveated on the anchor, plus the known ifc_poisson seed-2 instability, audited CLEAN and kept), r2s3-B3 [15.21, 15.43, 15.57] (re-vendored lift, ADR r2-0004 seam re-verified ≤1e-9). Best-floor geomean **38.8368** (lineage: 75.0673 → 38.6300 → 36.3912 → 34.4198 → 38.8368). Validation seam passes (`PANEL6_R2` historical reproduction; the seam also caught and blocked a SHARP4 double-count during this rebuild). `state/anchors/launch_anchors.json`; records: `state/stale_ckpt_repair_jobs_2026-08-09.json`, `docs/adr/0005-pfc-spectral-rung-repair.md`. Prior 2026-08-10 5-ds evidence line superseded by this row. |

Batch 1 dispatches only with all three gates GREEN (ADR D6, HOW_TO_LAUNCH §0).
