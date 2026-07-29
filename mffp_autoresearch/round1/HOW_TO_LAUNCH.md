# How to launch MFFP Autoresearch Round 1

## 0. Prerequisites (gates — all green before the crons start)

| Gate | What | Verify |
|---|---|---|
| G1 | eval-layer smoke on a real family + assertion drill | `state/gates.md` has "G1 PASS" |
| G2 | copy-LF baselines computed, divergences noted | `eval/copylf_baselines.json` exists; `_notes` covers ifc_poisson + heat_local |
| G3 | batch 0: anchors + noise floor, 3 seeds | `state/anchors/*.json` (5 files, `provisional: false`) + `state/noise_floor.json` |
| G4 | one hand-driven card end-to-end (`s5_tuning-B1`) | `state/gates.md` has "G4 PASS"; the card is `complete` |

Also: `python -m pytest` green in `eval/tests/` (24 tests), and
`bash -n` clean on `resource/logistics/example_scripts/*.sh`.

## 1. Install the agent definitions

```bash
bash mffp_autoresearch/round1/install_agents.sh
```

Re-run after ANY edit to `subagents/` — the registry copy is what executes.

## 2. Kick off the orchestrator (one persistent Claude Code session)

Paste exactly (a bare "read program.md" makes a fresh session summarize
instead of orchestrate — assign the role + give the launch imperative):

> You are the MFFP Autoresearch Round 1 ORCHESTRATOR for this repo. Read
> `mffp_autoresearch/round1/program.md` and act as defined there (your role:
> §6; structure: §4; prerequisites: §8). Confirm gates G1–G4 are green in
> `state/gates.md`, then run the per-stream flow for all 5 streams in
> parallel. Batch 0 (anchors + noise floor) is already certified; s5_tuning
> batch 1 was the G4 dry-run — check its card status and continue from there;
> the other four streams start at batch 1 (websearcher first). Maintain
> `state/{stream}/current_batch.txt`, `current_stage.txt`, and append
> decisions to `state/orchestrator_flow.md` as you go.

Dispatch pattern per stage (background; python-running agents need
bypassPermissions; `description` is the maintainer's archive key):

```
Agent(subagent_type="websearcher", description="s1_poisson-B1",
      prompt="Stream: s1_poisson. Batch: 1.", run_in_background=True)
```

Per-stream flow (program.md §4): websearcher → brainstormer → starter →
builder → code-reviewer → [PASS/SUGGEST: orchestrator runs `submit.sh` (seed
0)] → [FAIL: back to builder, ≤3] → SLURM → (debugger on failure, ≤5 ALGO) →
initial-analyzer (seed 0) → `submit_seeds_2_3.sh` unless cratered →
initial-analyzer (3-seed) → mechanism-analyzer turns 1/2/3/register →
complete. Diagnostic cards: single run, no seeds 1–2, then analyzer turns.

## 3. Start the crons

- **Orchestrator pulse, every 10 min**: "For each of the 5 streams, where are
  you in the flow? Re-read state/, advance whatever is unblocked (dispatch
  the next agent, submit gated seeds, invoke the debugger on failed jobs)."
- **Maintainer, every 20 min**: dispatch the `maintainer` subagent
  (single-in-flight rule is enforced by the agent itself).

Crons pulse; they do not drive logic. Record cron ids in
`state/orchestrator_flow.md`. After any session/MCP hiccup, re-verify the
cron list (round-5 lesson: disconnects can wipe session crons).

## 4. Recovery

State lives in `state/` — a fresh session given the §2 kickoff prompt
re-reads it and continues. Worktrees, cards, and SLURM queues are the ground
truth; `state/orchestrator_flow.md` is the narrative. Check
`state/blocked.md` for auto-skip reasons (it is a log, not a queue).

## 5. Shutdown / pause

Stop the crons; running SLURM jobs are safe to leave (checkpoint-resume is
contractual). To resume, re-run §2–§3.
