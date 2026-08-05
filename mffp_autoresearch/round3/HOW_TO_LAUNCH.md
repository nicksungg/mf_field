# How to launch MFFP Autoresearch Round 3

Launch authorized by Eloise 2026-08-05 (go recorded in ADR r3-0001; mentor option-A ratification same day).
Round-2 runbook: `../round2/HOW_TO_LAUNCH.md` (this file mirrors it with round-3 deltas).

## 0. Prerequisites (gates — all green before the crons start)

- **G1-r3 — data**: ADR r3-0001 executed: five option-A sharp variants swapped in (2026-08-03), repaired IFC ladders adopted (2026-08-05, `ifc_pairing_repair/adoption_manifest_2026-08-05.json`), stripped view verified live-mirroring the repaired arrays.
- **G2-r3 — preflight**: `state/preflight_launch_2026-08-05.json` PASS with the two adjudicated waivers (`state/preflight_launch_waiver_evidence_2026-08-05.md`); PROGRAM_NOTE MUST #1 satisfied.
- **G3-r3 — anchors**: `state/anchors/launch_anchors.json` — best-floor certified (75.0673); the four card anchors flip PENDING→CERTIFIED when SLURM jobs 66546256–66546267 land and `tools/make_round3_anchors.py` is re-run. **Batch 1 does not dispatch while any card is PENDING (ADR D6).**
- Track gate state in `state/gates.md`.

## 1. Kick off the orchestrator (one persistent Claude Code session)

Paste exactly:

> You are the MFFP Autoresearch Round 3 ORCHESTRATOR for this repo. Read
> `mffp_autoresearch/round3/program.md` and act as defined there. Confirm
> gates G1-r3–G3-r3 are green in `state/gates.md`, then run the per-stream
> flow for all 4 streams (r3s1_factorised, r3s2_field_reach, r3s3_lf_value,
> r3s4_audit) in parallel, starting each at batch 1 (websearcher first).
> r3s4-B1 is pre-directed: certify repaired-panel mce + floors before any
> other stream's B1 claims are adjudicated. Maintain
> `state/{stream}/current_batch.txt`, `current_stage.txt`, and append
> decisions to `state/orchestrator_flow.md`.

Dispatch pattern per stage (background; python-running agents need bypassPermissions; `description` is the maintainer's archive key):

```
Agent(subagent_type="websearcher", description="r3s1_factorised-B1",
      prompt="Stream: r3s1_factorised. Batch: 1.", run_in_background=True)
```

Per-stream flow (round-2 shape, PROGRAM_NOTE amendments): websearcher → brainstormer → starter → builder → code-reviewer → [PASS/SUGGEST: orchestrator submits seed 0] → [FAIL: back to builder, ≤3] → SLURM → (debugger on failure, ≤5 ALGO) → initial-analyzer → mechanism-analyzer turns 1/2/3/register → complete.
Deltas from round 2: claimable cards run seeds 1–2 IN-ROUND as a close precondition (MUST #4); a stream closes only on close-evidence (MUST #3); every sbatch expected ≥ 1 h carries `--mail-user=ezeng@caltech.edu --mail-type=END,FAIL`.

## 2. Start the crons

- **Orchestrator pulse, every 10 min**: advance whatever is unblocked per stream.
- **Maintainer, every 20 min**: dispatch the `maintainer` subagent.
- **Auto-sync, every 30 min**: stage ONLY `mffp_autoresearch/round3` in the main repo (commit `round3: auto-sync <UTC>`, push `mffp-trunk-eloise`); stage everything in `mffp_autoresearch_outputs/round3` (branch `round3`). Never force-push; never stage outside the round folder; check `git diff --cached --quiet` before staging (round-2 hazard: auto-sync commits whatever is already in the index).

Crons pulse; they do not drive logic.
Record cron ids in `state/orchestrator_flow.md`.
Kill every cron at round close (MUST #6 — pollers die with the round).

## 3. Recovery / shutdown

Round-2 runbook §3 applies: after any session hiccup re-verify the cron list; on a defect discovery run `preflight/hold.py` (MUST #2) and wait for operator adjudication.
