# Subagent return format to orchestrator

Every subagent returns a markdown block following this shape:

```markdown
## {subagent-name} complete — {stream}-B{N}[ turn {k}]

**Status**: SUCCESS | PARTIAL | FAILURE
**Action**: <one word, e.g. built | drafted | gave_up | no-op | reviewed_pass | slot_filled>

**<Subagent-specific summary lines>**

**Checklist passes**: <n>/<m>
**Blockers** (only if PARTIAL or FAILURE): <description>
```

## Status semantics

Orchestrator advances only on `SUCCESS`.

| Status | Meaning | Orchestrator behavior |
|---|---|---|
| `SUCCESS` | Required work is done. | Continue per the flow |
| `PARTIAL` | Some required work missing but recoverable. | May retry once with same parameters |
| `FAILURE` | Invocation failed (infra error, contract violation, missing precondition). | Read `state/blocked.md`; auto-skip the slot if the relevant cap fired (5 SLURM-ALGO, 3 review-FAILs, 3 consecutive stream skips) |

## Important: SUCCESS is about YOUR invocation, not the work's outcome

- A debugger that gives up after 5 ALGO attempts returns `SUCCESS` /
  `gave_up` — the retry rule fired correctly.
- A code-reviewer whose verdict is FAIL returns `SUCCESS` / `reviewed_fail`.
- A brainstormer whose slot is `skipped` returns `SUCCESS` / `slot_skipped`.
- Return `FAILURE` only if YOU could not perform your contracted work
  (couldn't read the card, worktree git broken, etc.).

## Action vocabulary (suggested)

| Subagent | Common actions |
|---|---|
| `experiment-starter` | drafted, skipped, blocked |
| `experiment-builder` | built, no-op |
| `code-reviewer` | reviewed_pass, reviewed_suggest, reviewed_fail |
| `experiment-debugger` | fixed_and_relaunched, gave_up, infrastructure_retry |
| `experiment-initial-analyzer` | analyzed_single_seed, analyzed_three_seed |
| `experiment-mechanism-analyzer` | turn_{1,2,3}_complete, register_complete |
| `brainstormer` | slot_filled, slot_skipped |
| `websearcher` | search_complete, search_failed |
| `advisor-consult` | consulted |
| `maintainer` | report_updated, stream_abandoned |
