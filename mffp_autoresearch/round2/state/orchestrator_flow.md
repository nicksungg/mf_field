# Round-2 orchestrator decision log (append-only)

## 2026-07-31 — LAUNCH

- Launch authorized by Eloise ("launch round2 (use round1 results as
  guidance)", 2026-07-31). Round 1 CLOSED (report frozen).
- Between-rounds fixes landed in round2/eval (ADR r2-0001); floors frozen
  (G3-r2); gates G1-r2/G2-r2/G3-r2 all PASS (state/gates.md).
- Deviation from spec recorded: spec §5 claim "round-1 families cannot run
  at all on the stripped view" corrected — transfer-style families are
  condition→field at test; mf_fno_transfer_film reclassified as declared
  r2s3 baseline (program §3, §12.3; gates.md G1-r2 item 3).
- Round-1 top-3 seed confirms NOT launched (separately operator-gated;
  reported to Eloise as pending decision).
- Subagents installed (round-1 registry backed up to
  ~/.claude/agents.mffp-round1.bak). Outputs repo
  mffp_autoresearch_outputs/round2 on branch round2, pushed to origin.
- Dispatching batch-1 websearchers for all 4 streams in parallel
  (r2s2-B1 and r2s4-B1 pre-directed cores per program §12.2/§12.4).
- Orchestrator: THIS session. Crons: orchestrator pulse 10 min, maintainer
  20 min, auto-sync 30 min (ids recorded below once created).
