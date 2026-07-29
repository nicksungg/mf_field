# Operator note — docs/proposals backlog audit (2026-07-29)

Source: a forked session read the five pre-kickoff files in the repo-root
`docs/proposals/` (dated 2026-07-15..22) that round-1 setup never ingested
(setup used only PROMPT-7-28.md and AI_Scientist.pdf). This note is operator
input for batch-2 brainstormer dispatches; it does not modify program.md.

## Independently converged (no action — validation only)
- Round 1's single nRMSE definition + NRMSE_DEF_HASH resolves the audit's F01
  (three incompatible definitions).
- Batch 0 IS the proposed A6 noise-floor calibration (~36 runs matches).
- s5_tuning-B1 (modes_cap 12→32) IS A9/F22 — the never-tuned spectral cap.
- s1-B1's env-knob-invisible-to-cache trap was pre-warned in MODELS_TO_TRY §5.
- "Make the MF composition the thesis" (six mechanism-preempted proposals in a
  row) matches s2's copy-LF framing and the round's prior-art discipline.

## NOT ingested — candidate seeds for batch 2 (feed to brainstormers)
1. **Candidate D: warp-then-correct / registration fusion** (NEW_MODELS.md) —
   geometric misalignment mechanism; in no current stream; the only one of the
   four NEW_MODELS candidates NOT prior-art-preempted at mechanism level per
   its own scans. Natural fit: s4_hybrid_routing or s2 batch 2.
2. **D1 residual-spectrum FFT diagnostic** (MODELS_TO_TRY.md) — free,
   designed probe distinguishing H1 spectral-truncation vs H2 missing-local-
   representation. Natural fit: s2 batch 2 (complements the B1 forensics) or
   s5 (interprets the modes_cap result).
3. **A7 mf_fno_pinn_transfer attribution experiment** (MODEL_TWEAKS.md) —
   which stage of the transfer schedule carries the gain. Fit: s1/s5.
4. **F14-F18 structural-constraint ideas** (MODEL_TWEAKS_EVIDENCE.md) —
   loss/metric mismatch and constraint items not yet examined by any stream.

## Caveats
- These predate batch-0 certification; any numbers in them are uncertified and
  must not be quoted as priors — streams must re-derive through the eval layer.
- H1-vs-H2 framing (spectral capacity vs local representation) will be partly
  answered by s5-B1 + s2-B1; batch-2 dispatches should condition on those
  results rather than re-proposing the question.
