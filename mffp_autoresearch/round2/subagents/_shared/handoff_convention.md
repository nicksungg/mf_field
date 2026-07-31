# Agent handoff convention

Per-experiment context that doesn't belong in the card's structured fields but
should survive between pipeline stages lives in the worktree's `notes/`
directory as `handoff_*.md` files. Every pipeline subagent reads them at start
and writes exactly one before returning.

## 1. Where they live

```
${ROUND_ROOT}/worktrees/{stream}/B{N}/notes/
```

Worktree-local only; never copied to the main tree.

## 2. File naming

| Agent | File | When |
|---|---|---|
| `experiment-starter` | `handoff_experiment_starter.md` | Always |
| `experiment-builder` | `handoff_experiment_builder.md` | Always; overwritten on re-build |
| `code-reviewer` | `handoff_code_reviewer.md` | Always; overwritten on re-review |
| `experiment-debugger` | `handoff_experiment_debugger_{n}.md` | `n` = next unused integer (glob, +1). Numbered files are IMMUTABLE. |
| `experiment-initial-analyzer` | `handoff_experiment_initial_analyzer.md` | After part 5 populated |
| `experiment-mechanism-analyzer` | `handoff_experiment_mechanism_analyzer.md` | Terminal |

## 3. Reading rule (every pipeline agent)

At the start of the run: `Glob` `<worktree>/notes/handoff_*.md`, `Read` every
match, keep in memory.

## 4. Writing rule

Before returning, write exactly ONE file — the one named after this agent.
Template (not enforced):

```markdown
# Handoff from <agent_name> — <ISO-8601 UTC>

**For**: <next agent(s)>
**Experiment**: {stream}-B{N}

## What I did
- <1-3 bullets>

## What to watch for
- <gotchas, assumptions, anomalies, working hypotheses>

## Suggested next steps
- <if relevant>
```

## 5. Relationship to card fields

If something can be captured structurally, it belongs in the card. If it's the
kind of thing the next agent would say "I wish I knew that before I started,"
it belongs in the handoff.

## 6. Hygiene

No secrets. No paths into other experiments. Keep under ~200 words. Never
edit a numbered debugger file after it's written. Never delete a handoff.
