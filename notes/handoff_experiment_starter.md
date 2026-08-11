# Handoff from experiment-starter — 2026-08-11T03:45Z

**For**: experiment-builder, code-reviewer
**Experiment**: r3s2_field_reach-B3

## What I did
- Transcribed the batch-3 brainstormer report verbatim into
  `experiment_cards/r3s2_field_reach/batch_3/B3.json` (parts 2/3/4,
  `expected_falsification`, `prior_art`, and the full 83-key `recipe.env`
  parsed straight from the report's fenced JSON — byte-identical).
- Created this worktree on branch `round3/exp-r3s2_field_reach-B3` forked from
  `round3-substrate` (44f2404), plus `notes/` and `scratchpad/`.

## What to watch for
- **No TBD fields.** Nothing was inferred or filled in by me.
- The registration hold is LIFTED: ADR r3-0007 ratified as **option C** (scored
  panel = four sharp cells + ifc_heat; ifc_poisson report-only). Per the design,
  all six cells still RUN; `R3S2B3_REGISTRATION_PREDICATE`
  (`scored_and_certified_mce_and_not_floor_disqualified`) resolves REGISTERED vs
  REPORT-ONLY with zero redesign. Both ifc units stay report-only.
- pfc has **no certified `min_claimable_effect`** yet (certification running in
  parallel) → its unit is REPORT-ONLY unless certified before registration. The
  card's conditional adjudication language is preserved as written.
- Mandatory and transcribed verbatim: `R3S2B3_RUNG_LIFT_TRIPWIRE=1` (family LF
  rung + lift must equal `panel_data.py`'s scored-cell choice; pfc = rung 1 +
  spectral zero-pad, ADR r3-0005) and the pfc target-scaler pre-flight
  (`R3S2_TARGET_SCALER_PREFLIGHT`).
- `recipe.base_commit` (23018cc5) and `env._substrate_commit` (e606a4f1) differ
  in the report; both transcribed as given — do not reconcile silently.
- `env._script_env` (ROUND2_EVAL_RESULTS / ROUND2_EVAL_CACHE) is mandatory:
  without it the job writes into the frozen round-2 eval layer.

## Suggested next steps
- Vendor `models_r3/r3s2_ceiling` from B2's `r3s2_route` per `_vendor_source`;
  run the `_preflight` zero-GPU audits before any submission.
