# Experiment card update rules

Card path: `${ROUND_ROOT}/experiment_cards/{stream}/batch_{N}/B{N}.json`.
Full field list: `${ROUND_ROOT}/experiment_cards/SCHEMA.md`.

## Locked fields (NEVER write after the starter populates them)

- `id`, `stream`, `batch`, `category`, `card_type`, `created_utc`,
  `worktree_path`, `source_iteration`, `reopened_from`
- Parts 1–4: `1_id_category`, `2_motivation`, `3_description`, `4_expected_result`
- `expected_falsification`
- `anchor_reference`
- `prior_art` (verdict + citations, from the websearcher via the brainstormer)
- `recipe` (the structured config block — dataset(s), epochs, seeds, env
  knobs, base family/commit)

If your subagent thinks one of these needs to change, that's a design-intent
change, not a mechanics change. Write `state/blocked.md` with the reason and
auto-skip per the autonomous-loop policy (program.md §5.3).

## Subagent-specific writable fields

| Subagent | Allowed to write |
|---|---|
| `experiment-starter` | All locked fields (initial population) + `status="drafted"` or `"blocked"` or `"skipped"`, `skipped_reason`; scaffold all mechanics fields as empty |
| `experiment-builder` | `status="built"`, `scripts_path`, `output_paths`, `build_commit`, `build_notes[]` (append) |
| `code-reviewer` | `status="reviewed_pass"` \| `"reviewed_suggest"` \| `"reviewed_fail"`, `review_notes[]` (append) |
| `experiment-debugger` | `debug_notes[]` (append), `job_ids` (append), `status="running"`/`"skipped"`, `reopen_candidate` |
| `experiment-initial-analyzer` | `5_actual_result`, `status="analyzing"` |
| `experiment-mechanism-analyzer` | `6_analysis`, `7_gap_and_future`, `reanalysis_progress`, `status="complete"` |

## Card update procedure

1. `Read` the card.
2. Apply the change in memory (preserve all other fields verbatim).
3. `Write` the full updated JSON back to the same path.
4. Re-read to verify the write succeeded and locked fields are unchanged.

**Never** use `sed` / `awk` / partial bash edits on the card. Always
parse-and-rewrite via Write.

## Common mistake to avoid

The card lives in the MAIN tree (`${ROUND_ROOT}/experiment_cards/...`), NOT in
the worktree. It is the only main-tree file your subagent edits (alongside
`state/blocked.md` on fatal failure). Do not confuse it with the worktree's
`notes/` handoff files.
