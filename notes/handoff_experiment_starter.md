# Handoff from experiment-starter — 2026-08-10T14:34:39Z

**For**: experiment-builder, code-reviewer
**Experiment**: r3s2_field_reach-B2

## What I did
- Transcribed the batch-2 brainstormer report verbatim into
  `experiment_cards/r3s2_field_reach/batch_2/B2.json` (card_type `model`,
  category `mf_composition/route_contrast_with_instrument_repair`).
  Parts 2/3/4, `expected_falsification` (G1 route + G2 instrument acceptance +
  G3 prospective approximability, with the affirmative-negative branch inside
  G1), `prior_art` (E2/E1/E3 verdicts + the "presenting ridge/band-limiting as
  the *idea* is a rebadge" warning + the 0-for-7 standing), and the full
  `recipe` (75 env keys, 7 `_arms`) were copied, not authored.
- Created this worktree on `round3/exp-r3s2_field_reach-B2` from
  `round3-substrate`, plus `notes/` and `scratchpad/`.

## What to watch for
- No `TBD:` fields; nothing was paraphrased or filled in.
- `anchor_reference` is `null` per program.md §4.5; the own-stream anchor
  12.9556 is carried instead as `R3S2B2_ANCHOR_REPLICATION_CHECK` and arm A5.
- `recipe.base_commit` (`76d15c2d…`) and `env._substrate_commit` (`d5069a74…`)
  differ in the report; both transcribed as written — confirm before building.
- Recipe `_`-prefixed keys are card directives, NOT `--env` arguments.
