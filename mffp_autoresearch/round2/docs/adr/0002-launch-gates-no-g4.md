# ADR r2-0002: Round-2 launch gates — no hand-driven G4 card; floors replace batch 0

Date: 2026-07-31. Status: accepted.

## Context

Round 1 gated launch on G1 (eval smoke), G2 (baselines), G3 (batch-0 trained
anchors + noise floor, 3 seeds on SLURM), G4 (one hand-driven card end-to-end).
Round 2 inherits a pipeline that ran 18 cards across 7 streams without
structural failure.

## Decision

1. **No G4 hand-driven card.** In compensation the orchestrator drives every
   stream's B1 with extra scrutiny, and r2s4-B1 is a certification card.
2. **No trained batch 0.** Round-2 launch anchors are the deterministic
   training-free floors (NN-in-condition / train-mean / zero), frozen in
   `state/anchors/` before any experiment (spec §3) — no models of the
   round-2 class exist to certify a champion anchor from, and the floors are
   exactly reproducible without seeds.
3. **The noise floor is inherited provisionally** (round-1 batch-0 nRMSE seed
   spreads rescaled by the corrected denominators, `_provisional: true`).
   Per r1 program §4.5 a provisional floor is not a numeric threshold;
   falsification clauses are judged directly until r2s4-B1 trains a minimal
   condition→HF baseline at seeds {0,1,2} and replaces the file.

## Consequences

- Launch requires G1-r2/G2-r2/G3-r2 only (program §8).
- The first claimable numeric-effect comparisons (beyond falsification
  clauses) become available after r2s4-B1 completes.
