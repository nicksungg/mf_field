# MFFP Autoresearch Round 3 — dashboard

**Status:** LIVE (2026-08-07). All gates GREEN (`state/gates.md`); HOLD cleared (operator adjudication 2026-08-06, repairs verified); batch 1 in flight.
**Program:** `program.md` · **Config:** `project.yaml` · **ADRs:** `docs/adr/` (0001 launch panel + A1, 0002 pfc crystalline box, 0003 estimator-integrity repairs) · **Runbook:** `HOW_TO_LAUNCH.md`
**Panel (scored, 6 — ADR A1):** pfc_2d (crystalline box, ADR r3-0002), allen_cahn_2d (trimmed test n=78, ADR r3-0003 D1), fisher_kpp_2d, cahn_hilliard (min-detectable-delta rule, D2), ifc_poisson, ifc_heat (both repaired ladders) — helmholtz report-only.
**Launch anchors:** best-floor geomean **36.3912** (lineage 75.0673 → 38.6300 → 36.3912); all 4 cards CERTIFIED 2026-08-07. Data hashes bound: `state/data_hashes.json`.

| stream | class | batch | stage | last card |
|---|---|---|---|---|
| r3s1_factorised | gap | 1 | websearch | — |
| r3s2_field_reach | gap | 1 | websearch | — |
| r3s3_lf_value | lever | 1 | websearch | — |
| r3s4_audit | diag | 1 | websearch done → brainstorm (B1 pre-directed: certify mce + floors first) | — |

Maintained by the maintainer cron once the round is live; hand-updated during launch.
