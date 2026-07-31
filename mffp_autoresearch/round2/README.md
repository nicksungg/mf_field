# MFFP Autoresearch Round 2 — condition-vector → HF

**Regime**: LF at train only; at test, models receive ONLY the condition
vector (the stripped test view makes test LF files physically absent).
**Question**: how well can condition→HF models predict the HF field, and how
much does train-time LF help?

- `program.md` — the universal guideline (goal §1, score §2, immutables §5,
  streams §12). Read it first.
- Spec: `docs/superpowers/specs/2026-07-30-mffp-autoresearch-round2-design.md`
  (repo root docs/). Approved 2026-07-30; launch authorized 2026-07-31.
- `HOW_TO_LAUNCH.md` — operator runbook.
- `index.md` — maintainer dashboard.
- `eval/` — round-2 eval layer: CORRECTED copy-LF references (ADR r2-0001,
  the round-1 registration/wrap-seam fixes), stripped-view scoring,
  `COPYLF_DEF_HASH` seam.
- `state/anchors/` — frozen floors + stream anchors (best-floor panel
  geomean 23.06).
- Streams: `r2s1_direct`, `r2s2_stacked`, `r2s3_lf_train_signal`, `r2s4_diag`.
- Round-1 results (authoritative): `../round1/docs/round1_report.md`.
