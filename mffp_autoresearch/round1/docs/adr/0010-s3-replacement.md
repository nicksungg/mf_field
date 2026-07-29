# ADR 0010 — s3_testtime retired; replaced by s3_warp (operator action)

**Status:** accepted 2026-07-29 (directed by Eloise: "remove s3 and replace
with something else", following mentor guidance recorded in ADR 0009)

## What was removed

- Stream `s3_testtime` (test-time refinement with real governing residuals).
- Its in-flight B1 builder agent was stopped mid-build (before contract smoke;
  no SLURM job was ever submitted, no GPU spent). Card
  `experiment_cards/s3_testtime/batch_1/B1.json` → `retired_by_operator`
  (locked fields preserved for audit). Worktree left in place, read-only.
- The retirement does NOT count as skips/abandonment (§4.2 failure semantics);
  it is an operator scope decision.

## Why

ADR 0009 (no known-physics assumptions at test time) removed the stream's
premise, and the stream's OWN batch-1 findings independently support removal:
residual computable on 1/6 panel datasets; where computable, the dataset is
two-FFT-solvable without a model (benchmark-integrity flag); the 1-dof
residual rescale collapses copy-LF (roughness meter, not error meter). The
evidence gathered stands in websearches/ and brainstormer/ as the recorded
dead end.

## Replacement: s3_warp (lever)

Warp-then-correct registration fusion — NEW_MODELS.md Candidate D, the one
un-ingested proposals-backlog candidate whose mechanism was not prior-art-
preempted. Physics-agnostic (ADR 0009-compliant). Conventions in program.md
§12.3 (rewritten). Starts at batch 1 with a fresh websearcher (prior-art
verdict mandatory; must re-verify non-preemption for MF PDE fusion
specifically) → brainstormer (ADR 0007 propose-many applies) → standard
pipeline.
