# ADR 0006 — G4 relaxed to submit-verified (operator action)

**Status:** accepted 2026-07-29 (Eloise questioned the serialization; the
orchestrator had recommended this relaxation earlier the same day)

## Decision

G4's purpose is pipeline validation, not result production. The gate is
split:

- **G4a (build-path, PASSED by evidence already in hand):** starter, builder,
  and code-review mechanics validated on s5_tuning-B1. s1-s4 starters and
  builders may run immediately; they do not touch SLURM.
- **G4b (submit-path):** recorded once s5-B1 seed 0 is RUNNING on SLURM and
  writing valid score_panel output (first dataset scored). s1-s4 SLURM
  submissions gate on G4b, not on s5's full completion.
- The analyzer path is still validated first on s5-B1 (its job finishes hours
  before s1-s4's), preserving the dry-run property for parts 5-7.

## Why

s5's remaining runtime (training) validates nothing the s1-s4 BUILDS depend
on; serializing ~4-6h of builds behind it bought no risk reduction. The
dry-run gate already caught real defects at every hop it was designed to
test (starter path convention, builder relocation bug, job-name/glob
mismatches).
