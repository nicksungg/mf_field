# ADR 0007 — Propose-many / screen-cheap / promote-few (batch ≥ 2)

**Status:** accepted 2026-07-29 (proposed by the orchestrator after the
H100 switch made contract-tier screens ~free — guard-contract precedent:
46 s for a 3-dataset 2-epoch run; interest confirmed by Eloise)

## Decision

From batch 2 onward, for MODEL cards with genuine design freedom (not
spec-pre-directed slots and not diagnostics):

1. **Propose-many**: the brainstormer emits 3–5 ranked candidate variants
   for its slot, each with a complete recipe delta (env knob or small
   family variant) and the SAME falsification clause structure.
2. **Screen-cheap**: the builder implements the shared substrate once,
   parameterizes the variants, and the orchestrator submits ONE contract-tier
   (2-epoch) screening job covering all variants on the card's datasets
   (H100, minutes). Screening numbers are NEVER reportable results — they
   are plumbing + gross-ordering signal only (2-epoch rankings are noisy;
   treat as a coarse filter, discarding only clearly-broken/cratered
   variants, not close calls).
3. **Promote-few**: the best surviving variant becomes the card's single
   200-epoch seed-0 run (ADR 0004). The card records the screen table in
   build_notes so the un-promoted variants are auditable dead ends, not
   silent drops.

## Why

Same generate-vs-verify asymmetry the round already exploits, moved one
stage earlier: candidate generation is cheap (brainstormer already does the
analysis), and the H100 makes the verifier's cheap tier nearly free. This
widens search without touching the falsifiability contract — the reportable
unit is still one pre-registered 200-epoch experiment per card.

## Guardrails

- One card, one worktree, one SLURM chain per batch — unchanged (§4.2).
- Diagnostics and spec-pre-directed slots are exempt (no candidate pool).
- The promoted variant's identity is fixed in the card BEFORE the 200-epoch
  submit (no post-hoc arm switching).
- Screen results must not be quoted as evidence for/against any hypothesis
  in parts 5-7; they exist only in build_notes.
