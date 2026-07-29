# ADR 0008 — mf_fno_pinn_transfer retired from the round (operator action)

**Status:** accepted 2026-07-29 (directed by Eloise: "we should ignore pinn")

- No future card may use `mf_fno_pinn_transfer` as base_family, comparison
  target, or design seed; batch-2+ brainstormer dispatches cite this ADR.
- Its batch-0 runs REMAIN as data (they fed the noise floor; the per-dataset
  best-family skills all came from `mf_fno_transfer_film` anyway, so anchors
  are unaffected).
- The one in-flight use is s2_beyond_copy-B1 (locked card, reloads both
  batch-0 champions' checkpoints for forensics). It proceeds unchanged —
  measuring pinn's checkpoints is evidence about the failure mode, not
  building on pinn.
- It is excluded from the provisional leaderboard and from end-of-round
  top-3 eligibility (ADR 0004).

## Amendment (2026-07-29, Eloise): removed from current cards too

The s2_beyond_copy-B1 forensics exception is revoked by direct instruction
("delete pinn from current cards"). The card was amended by operator action
(recorded in its operator_amendments field): S2B1_BASE_FAMILIES narrowed to
mf_fno_transfer_film; the diagnostic measures the champion's checkpoints only.
This halves the card's measurement matrix; its falsification clauses are
unaffected (they were stated per-family). No other current card references
pinn.
