# ADR 0012 — Seventh stream s7_loss: interface-aware training objectives

**Status:** accepted 2026-07-29 (Eloise asked for further streams from the
proposals/reports backlog; expands the pilot envelope to 7 by her direction)

## Decision

New lever stream `s7_loss`: does changing WHAT is optimized (interface-aware,
gradient-domain, or sharp-region-weighted training losses) fix sharp-2D
fusion, holding architecture fixed (champion family)? Ingests the F14-F18
structural-constraint backlog from docs/proposals/MODEL_TWEAKS*.md.

## Ground rules

- The ROUND METRIC IS UNCHANGED: scoring remains per-sample rel-L2 through
  eval/nrmse.py (§2.1 immutable). The stream changes the TRAINING objective
  only; a win = better rel-L2 achieved by training against something else.
- Physics-agnostic losses only (ADR 0009): interface weights from the field's
  own gradients/level sets, not from governing equations.
- Loss-vs-metric mismatch is the known in-repo motivation (rel-L2 hides thin
  sharp regions — datasets_summary/SURF methodology notes; F14-F18).
- ADR 0004/0007 apply. Anchor: champion's certified panel geomean (§4.5).
- Failure-mode caution: sharp-region upweighting can trade bulk accuracy for
  interface accuracy and LOSE on rel-L2 — cards must pre-register that
  trade-off in expected_falsification.
