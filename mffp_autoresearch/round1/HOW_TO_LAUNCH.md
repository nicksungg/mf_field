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

## 6. Eloise — round1 launch checklist (round5b checklist, adapted)

**0. Research environment** (standing prerequisites): repo venv works
(`source .venv/bin/activate`; torch 2.6), `benchmark_42/` data landed (7.0 GB,
42 datasets), and the §0 gate table above — G1/G2 recorded PASS in
`state/gates.md`; G3 = SLURM batch 0; G4 = the `s5_tuning-B1` dry-run card.
No kkanbu profile to install — round 1 has no oracle (ADR 0001).

**1. Update the repo** (round lives on the working branch, not main):

```bash
cd /resnick/groups/Hippo/ezeng/mf_field
git checkout mffp-trunk-eloise && git pull origin mffp-trunk-eloise
ls mffp_autoresearch/round1/program.md    # verify
```

**2. Install the round1 subagents** (wraps the copy + verify; backs up the
quadruped set once, avoids the `_shared/_shared` nesting trap by per-file copy):

```bash
bash mffp_autoresearch/round1/install_agents.sh
# manual verify (silent = synced):
for f in mffp_autoresearch/round1/subagents/*.md; do diff -q "$f" ~/.claude/agents/$(basename "$f"); done
diff -rq mffp_autoresearch/round1/subagents/_shared ~/.claude/agents/_shared
```

**3. Outputs repo** — `mffp_autoresearch_outputs/round1/` (git-ignored by the
main repo, its own git repo on branch `round1`; keeps result JSONs + SLURM
logs, excludes checkpoints). Already initialized. To sync it off-cluster,
create an empty GitHub repo and:

```bash
cd mffp_autoresearch_outputs/round1
git remote add origin <your-outputs-repo-url> && git push -u origin round1
```

**4. Launch & kick off**: orchestrator kickoff prompt in §2 above, crons in
§3. For the 30-min auto-sync, run in a fresh session with the loop skill:

```
/loop 30m
Commit-and-push pass for the MFFP Round 1 autoresearch run. You do NOT run
experiments, dispatch subagents, or read the spec — only commit and push. Do
exactly this once, then stop (the loop re-runs you on the interval):

Two repos, handled INDEPENDENTLY (a failure in one must never stop the other;
never force-push):

A) Spec/loop repo — /resnick/groups/Hippo/ezeng/mf_field (branch
   `mffp-trunk-eloise`): stage ONLY the round folder —
   `git add mffp_autoresearch/round1` (experiment cards, state/, index.md,
   brainstormer/, websearches/, tools/; its .gitignore excludes worktrees and
   eval caches). Never stage anything outside `mffp_autoresearch/round1/`.

B) Outputs repo — /resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch_outputs/round1
   (branch `round1`): stage everything — `git add -A` (its .gitignore handles
   excludes). If it has no remote, commit locally and report `no remote`.

For EACH repo:
  - if nothing is staged → skip it (no empty commits);
  - else commit with message: `round1: auto-sync <UTC>` where
    <UTC> = `date -u +%Y-%m-%dT%H:%M:%SZ`;
  - push to its branch; if rejected (remote advanced), `git pull --rebase`
    then push again;
  - if a rebase hits a conflict you can't safely auto-resolve, leave that
    repo's changes uncommitted, report it, and move on.

End with a one-line status per repo: `committed <sha>` / `nothing to commit` /
`blocked: <reason>`.
```
