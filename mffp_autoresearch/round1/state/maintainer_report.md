# Maintainer report — Round 1

## RUN START 2026-07-29T03:58:21Z
- First maintainer walk this round (no prior report file found; no
  double-walk risk — proceeding).
- Cards walked: 0. `experiment_cards/` holds only `SCHEMA.md` — no
  `B*.json` cards exist yet in any stream.
- All 5 streams (s1_poisson, s2_beyond_copy, s3_testtime, s4_hybrid_routing,
  s5_tuning) are at `current_batch=1`, `current_stage=
  websearch_done_awaiting_G3_brainstormer` — batch-1 websearch reports filed
  for all 5 (`websearches/{stream}/batch_1/report.md`); brainstormers
  correctly gated pending G3.
- G1/G2: PASS (per `state/gates.md`, unchanged this run).
- G3 (batch 0 anchor/noise-floor certification): PENDING. Array job
  `65956106` (r1-batch0, 36 tasks = 2 families x 6 panel datasets x 3
  seeds) is healthy: 6 COMPLETED / 6 RUNNING / 24 PENDING / 0 FAILED so far.
  Prior attempt `65955389` FAILED wholesale (14/14 launched tasks fast-failed
  in 4-6s on node `hpc-93-36`, INFRA: CUDA busy per commit f8256b4) — fixed
  same day by excluding that node; no action needed from maintainer, already
  resolved upstream.
- G4 (s5_tuning-B1 dry-run card): PENDING, gated on G3.
- state/anchors/{stream}.json: none exist yet (dir has only .gitkeep) —
  index.md renders "not yet certified" per anchor, no values computed here.
- state/noise_floor.json: does not exist yet (expected — G3 not complete).
- Timing ledger: created `state/timing_ledger.json` (did not exist before)
  and upserted 6 entries from the 6 COMPLETED r1-batch0 tasks (job
  65956106_0..5; mf_fno_transfer_film x {ext__helmholtz_2d,
  sharp__phase_field_crystal_2d} x seeds {0,1,2}; ~7.7 min/task on
  helmholtz_2d, ~12.3 min/task on phase_field_crystal_2d, gpu_type p100,
  200 epochs). Tagged `stream: "batch0"` since these are G3-gate runs, not
  stream-card runs — kept as a smoke-tier timing prior for builders.
- Abandonment check: no stream has any skipped/blocked batches (none exist
  yet) — no abandonment.
- Transcript inbox: `state/transcripts/inbox/` does not exist — nothing to
  file.
- No card files touched (`git status --short experiment_cards/` clean,
  confirmed both before and after this walk).
- index.md: created fresh (did not exist before this run).
## RUN END 2026-07-29T03:58:21Z

## RUN START 2026-07-29T04:16:14Z
- Single in-flight check: last run START 2026-07-29T03:58:21Z had a matching
  RUN END at the same timestamp — no double-walk risk, proceeding.
- no changes: cards walked 0 (`experiment_cards/` still only `SCHEMA.md`);
  all 5 streams still `current_batch=1`,
  `current_stage=websearch_done_awaiting_G3_brainstormer`; G1/G2 still PASS,
  G3/G4 still PENDING.
- G3 array job 65956106: still 6/36 COMPLETED (identical set, tasks 0-5),
  0 FAILED; tasks 6-11 (sharp__allen_cahn_2d, sharp__fisher_kpp_2d) still
  RUNNING (same 6 tasks as the prior walk, now ~22-35 min elapsed — not a
  stall, the 256^2 sharp datasets simply run longer at 200 epochs than
  helmholtz_2d/phase_field_crystal_2d); 24 tasks still PENDING (cluster
  concurrency limit).
- Timing ledger: no new COMPLETED r1- tasks since last upsert — no changes
  to `state/timing_ledger.json` (still 6 entries).
- Abandonment check: no stream has any skipped/blocked batches — no
  abandonment.
- state/anchors/, state/noise_floor.json: still absent (G3 not complete).
- Transcript inbox: `state/transcripts/inbox/` still does not exist —
  nothing to archive.
- No card files touched (`git status --short experiment_cards/` clean,
  confirmed before and after this walk).
- index.md: regenerated (timestamps/elapsed refreshed; no structural
  changes — dashboard content otherwise identical to the prior walk).
## RUN END 2026-07-29T04:16:45Z
