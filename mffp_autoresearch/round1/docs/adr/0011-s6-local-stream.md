# ADR 0011 — Sixth stream s6_local: FNO x local-representation hybrids

**Status:** accepted 2026-07-29 (Eloise proposed more streams incl. FNO-CNN
hybrids; orchestrator scoped it; fills the approved 4-6 pilot envelope)

## Decision

New lever stream `s6_local`: does adding a local representation (CNN /
ConvNeXt branch, local kernels) to the FNO fix sharp-2D fusion? This is the
direct test of hypothesis H2 (missing local representation), now live because
s5-B1's H1 test (modes_cap 12->32) improved geomean by only 0.507 — below the
0.884 claimable floor (provisional-single-seed).

FNO-Transolver variants were explicitly ROUTED TO s4 batch 2 (stream owns the
question; ADR 0007 propose-many applies there) — not a new stream.

## Constraints carried at birth

- Mentor's FNO-CNN hybrid attempt went poorly; the batch-1 websearcher must
  read docs/reports/MF_FNO_CNN_Hybrid_Report.md and the brainstormer must
  diagnose the failure mode before proposing (do not re-run a known-bad
  recipe).
- convnext_unet_film's zoo record: rank-2 overall but does NOT beat
  transfer_film on the panel (verified 2026-07-29 vs bench_full_metrics.csv)
  — pure-CNN capacity is not the lever; the composition is the question.
- ADR 0009 (physics-agnostic), ADR 0004 (single seed), ADR 0007
  (propose-many at brainstormer), standard pipeline and caps.
- Anchor: champion's certified panel geomean (lever class, §4.5).
