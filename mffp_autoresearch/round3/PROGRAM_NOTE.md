# Round-3 program note — process fixes from the round-2 post-close audit

**Status:** program-level rules for the next round; authored 2026-08-03 from the round-2 audit (report §5–§8, ADR r2-0003, `condition_completeness_proposal/`).
**Enforcement tooling already landed:** `mffp_autoresearch/preflight/` (`preflight.py`, `hold.py`, wiring contract in its README) and the generation-time completeness gate in `mffp_sharp.common.completeness` / `generate_standardized.py`.
Round 3 does not launch until the launch script satisfies every MUST below.

## 1. Integrity certificates run before batch 1 (enforced)

Round 2 found the incomplete condition vectors, the helmholtz triviality, the ifc pairing defect, and the pfc no-fidelity-gap *during* the round, when the frozen panel could not respond.
All four are training-free detections that take under a minute per dataset.
**MUST:** the launch script runs `preflight/preflight.py` over the panel, archives the report into `round3/state/`, and refuses to launch on a hard fail without a waiver recorded in the launch ADR.
The archived demo (`preflight/preflight_round2_panel_demo.json`) shows the round-2 panel would have failed preflight at launch — the whole class of "batch N+1 audits batch N's instruments" firefighting was avoidable for the data-side defects.

## 2. A defect discovery pauses the round (enforced)

**MUST:** every batch-dispatch path (including cron/poll loops) calls `preflight/hold.py check` first and refuses to dispatch on a held round.
**MUST:** any agent that finds a defect on a mentor-owned surface (generator code, dataset arrays, scoring instruments) sets the HOLD immediately, before writing the finding up.
Only the operator clears a hold, choosing repair + preflight re-run, waive with rationale, or round close.
This encodes the standing stop-the-line directive into the harness instead of agent memory.

## 3. Streams close on an evidence criterion, not a batch count

In this harness batch N+1 is the error-detector for batch N (seven independent instrument-defect confirmations in round 2; r2s1-B3 re-priced B2, r2s4-B4 resolved B3's falsification as a measurement-units failure).
Closing every stream at the ~3-batch budget therefore guarantees the terminal card — the one that gets reported — is the least-audited card in the stream.
**MUST:** a stream closes only when its terminal card has passed an independent instrument audit (a batch, or a training-free check, whose sole job is to attack the card's instruments), or when the operator closes it explicitly.

## 4. Seed confirms happen inside the round, as a close precondition

Round 2 deferred seeds 1–2 confirms to "on operator go"; they never ran, leaving 10 of 11 leaderboard rows single-seed.
The round's own numbers show single-seed rankings are inside the noise: the only 3-seed CI (r2s4-B1, [19.385, 20.527]) is ~1.14 units wide — equal to the certified `min_claimable_effect` 1.1419 — while ranks 3–10 span ~1.67 units, and on ifc the 3-init spread (median 0.938) is itself ~1 mce.
**MUST:** 1-seed screening in-round for triage; any card that will be *reported as claimable* runs seeds 1–2 before its stream closes.
A card without its confirm is reported as "screened, unconfirmed", never ranked against confirmed cards.

## 5. The panel is mutable in-round, under an explicit ADR

Round 2's objective geomeaned over six datasets of which, by the round's own findings, only cahn_hilliard could carry a learning claim.
**MUST:** a mid-round panel change (drop, repair, regenerate) is allowed via an ADR that records the defect, the change, and a fresh preflight report; the objective is recomputed from the change forward, with pre-change numbers kept but labelled.

## 6. Pollers die with the round

Round 2's polling crons burned ~10 h of idle pulses against frozen state after close.
**MUST:** the close procedure tears down every cron/poll loop the round created, and (per §2) a held round's pollers stop dispatching by construction.

## 7. Round-3 launch prerequisites (sequencing)

1. Approval of the two generator-surface packages: `condition_completeness_proposal/` (IC-encoding + generation gate, implemented and sample-round-certified) and `ladder_fix_proposal/` (patch rebased to apply at current HEAD). Granted 2026-08-03 by operator authority (Eloise; mentor sign-off waived — see `condition_completeness_proposal/APPROVAL.md`).
2. Regeneration of pfc / fisher_kpp / allen_cahn on the cluster through the fixed package path (500×3 ladder levels each, solver time only; SLURM with completion mail).
3. Preflight PASS on the regenerated panel, plus explicit panel-composition decisions for helmholtz (trivially re-solvable) and ifc_poisson (pairing repair via the ladder fix) recorded in the launch ADR.
4. 3-seed re-score of round 2's claimable slate (r2s2-B1, r2s3-B3, r2s1-B2/B3) on the repaired panel — these become round 3's certified launch anchors and measure how much of round 2's story survives the data fix.
5. Operator go.

Steps 2–5 spend cluster compute and are operator-gated; nothing launches on autopilot.
