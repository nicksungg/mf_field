# How to launch MFFP Autoresearch Round 2

Launch authorized by Eloise 2026-07-31 ("launch round2"). Round-1 runbook:
`../round1/HOW_TO_LAUNCH.md` (this file mirrors it with round-2 deltas).

## 0. Prerequisites (gates — all green before the crons start)

| Gate | What | Verify |
|---|---|---|
| G1-r2 | eval tests green (35, incl. registration regressions) + stripped-view structural enforcement | `state/gates.md` |
| G2-r2 | corrected copy-LF baselines with seam checks vs r1 + audit | `eval/copylf_baselines.json` |
| G3-r2 | floors + stream anchors frozen pre-experiment; provisional noise floor recorded | `state/anchors/`, `state/noise_floor.json` |

No G4 hand-driven card (ADR r2-0002): orchestrator drives every stream's B1
with extra scrutiny; r2s4-B1 is the certification card.

Also required before agents dispatch:

```bash
cd /resnick/groups/Hippo/ezeng/mf_field
python mffp_autoresearch/round2/eval/make_stripped_view.py      # idempotent
git branch round2-substrate                                     # worktree fork point
bash mffp_autoresearch/round2/install_agents.sh                 # OVERWRITES the r1 registry set
mkdir -p mffp_autoresearch_outputs/round2 && cd mffp_autoresearch_outputs/round2 \
  && git init -b round2   # outputs repo (round1 pattern; add remote when ready)
```

## 1. Kick off the orchestrator (one persistent Claude Code session)

Paste exactly:

> You are the MFFP Autoresearch Round 2 ORCHESTRATOR for this repo. Read
> `mffp_autoresearch/round2/program.md` and act as defined there (your role:
> §6; structure: §4; prerequisites: §8). Confirm gates G1-r2–G3-r2 are green
> in `state/gates.md`, then run the per-stream flow for all 4 streams
> (r2s1_direct, r2s2_stacked, r2s3_lf_train_signal, r2s4_diag) in parallel,
> starting each at batch 1 (websearcher first). r2s2-B1 and r2s4-B1 are
> pre-directed by program §12.2/§12.4 — the websearcher/brainstormer still
> run, but the design core is fixed. Drive every B1 with extra scrutiny
> (ADR r2-0002). Maintain `state/{stream}/current_batch.txt`,
> `current_stage.txt`, and append decisions to `state/orchestrator_flow.md`.

Dispatch pattern per stage (background; python-running agents need
bypassPermissions; `description` is the maintainer's archive key):

```
Agent(subagent_type="websearcher", description="r2s1_direct-B1",
      prompt="Stream: r2s1_direct. Batch: 1.", run_in_background=True)
```

Per-stream flow (unchanged from round 1): websearcher → brainstormer →
starter → builder → code-reviewer → [PASS/SUGGEST: orchestrator runs
`submit.sh` (seed 0)] → [FAIL: back to builder, ≤3] → SLURM → (debugger on
failure, ≤5 ALGO) → initial-analyzer (seed 0) → mechanism-analyzer turns
1/2/3/register → complete. Strict 1-seed; seeds 1–2 only for the end-of-round
top-3. Diagnostic cards: single run, then analyzer turns (exception: r2s4-B1
trains its minimal baseline at seeds {0,1,2} — program §12.4).

## 2. Start the crons

- **Orchestrator pulse, every 10 min**: "For each of the 4 streams, where are
  you in the flow? Re-read state/, advance whatever is unblocked."
- **Maintainer, every 20 min**: dispatch the `maintainer` subagent.
- **Auto-sync, every 30 min** (this session or a `/loop 30m` session): stage
  ONLY `mffp_autoresearch/round2` in the main repo (commit
  `round2: auto-sync <UTC>`, push `mffp-trunk-eloise`); stage everything in
  `mffp_autoresearch_outputs/round2` (branch `round2`; if no remote, commit
  locally and report `no remote`). Never force-push; never stage outside the
  round folder.

Crons pulse; they do not drive logic. Record cron ids in
`state/orchestrator_flow.md`. After any session hiccup, re-verify the cron
list.

## 3. Recovery / shutdown

Identical to round 1 (`../round1/HOW_TO_LAUNCH.md` §4–§5): `state/` +
worktrees + cards + SLURM queue are ground truth; a fresh session given the
§1 kickoff prompt continues. To pause: stop crons; running SLURM jobs are
safe (checkpoint-resume is contractual).
