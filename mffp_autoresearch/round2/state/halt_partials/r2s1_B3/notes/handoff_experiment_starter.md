# Handoff from experiment-starter — 2026-07-31T18:20Z

**For**: experiment-builder, code-reviewer
**Experiment**: r2s1_direct-B3

## What I did
- Transcribed the batch-3 brainstormer report verbatim into
  `experiment_cards/r2s1_direct/batch_3/B3.json` (parts 1-4,
  expected_falsification, prior_art, recipe). Slices were taken
  programmatically from `report.md` line ranges, so no rewording occurred.
- Created worktree `worktrees/r2s1_direct/B3` on branch
  `round2/exp-r2s1_direct-B3` forked from `round2-substrate` (9e10d41),
  with `notes/` and `scratchpad/`.

## What to watch for
- **TBD fields: none.**
- Transcription ambiguity: the brainstormer gave per-row verdicts (C1-C4) but
  no single card-level `prior_art.verdict` token. I copied the headline C2 row
  verdict string `preempted-but-MF-composition-open (cite)` verbatim; the full
  four-row block is preserved in `prior_art.verdict_quoted`. Do not read this
  as a schema-vocabulary verdict ("novel"/"preempted-pivoted"/"preempted").
- `recipe.env` has 80 keys; the 9 keys starting with `_` are card directives
  (build gates G-A..G-E, sbatch time, prior-art declarations) and per the
  brainstormer's `_note` must NOT be passed to `--env`.
- `anchor_reference` is `null` per program.md §4.5 (gap stream).
