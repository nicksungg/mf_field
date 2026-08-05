# Pre-return checklist template

Every subagent has a "Pre-return checklist (MANDATORY)" section before the
return format. This partial defines the SHAPE; each subagent fills in its own
items.

## Universal rule

**Verify each item by reading files back with `Read` / `Glob` / `Bash`.
Do NOT trust your memory.**

The point is to catch silent failures (a write that didn't happen, a state
file that wasn't updated). Memory says yes; the filesystem says no. Trust the
filesystem.

## Skeleton

```markdown
## {N}. Pre-return checklist (MANDATORY)

Verify each item by reading files back. Do NOT trust your memory.

**Structural**
- [ ] {file/path expectations specific to this subagent}

**Content**
- [ ] {content invariants specific to this subagent}

**Card integrity** (if this subagent edits the card — see _shared/card_update.md)
- [ ] Only allowlisted fields written for this subagent
- [ ] Locked fields (parts 1-4, expected_falsification, prior_art, recipe,
      card_type, anchor_reference) verified unchanged by spot-reading strings

**Honesty**
- [ ] No fabricated outputs; all claims traceable to read files
- [ ] If a tool was unreachable, noted explicitly

If any item fails:
1. Write `state/blocked.md` with the failure reason and auto-skip
   (program.md §5.3 — blocked.md is a log, not a queue)
2. Return `FAILURE` status
3. Do NOT silently continue
```

## What "Honesty" catches

The hardest failure class: the subagent thinks it did the work, but didn't —
claimed to run a smoke test but didn't (no output file, no command record);
claimed a checklist item passed without verifying; claimed to register a tool
but the file isn't in `tools/`. The meta-check: "if I had to defend each
claim, could I cite the file/output that proves it?" If not, it's not done.
