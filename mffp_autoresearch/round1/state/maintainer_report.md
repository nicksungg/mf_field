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

## RUN START 2026-07-29T04:36:39Z
- Single in-flight check: last run START 2026-07-29T04:16:14Z has matching
  RUN END 2026-07-29T04:16:45Z (19 min ago, and closed) — no double-walk
  risk, proceeding.
- Cards walked: 0 (`experiment_cards/` still only `SCHEMA.md`; no B*.json
  cards exist yet). All 5 streams still `current_batch=1`,
  `current_stage=websearch_done_awaiting_G3_brainstormer` — no change.
  `state/streams/*.json` still empty (no stream card history yet, so no
  abandonment is possible).
- G1/G2: still PASS (per state/gates.md, unchanged).
- G3 array job 65956106 progressed since last walk: 11/36 COMPLETED (was
  6/36) — tasks 0-10 done, 0 FAILED throughout (confirmed via
  `sacct -P` parsable output, not lexical grep, to avoid double-counting
  .batch/.extern step lines). Tasks 11-14 RUNNING (mf_fno_transfer_film x
  sharp__fisher_kpp_2d seed2, then sharp__cahn_hilliard seeds 0-2, per the
  sbatch array-index formula f=i/18,d=(i%18)/3,s=i%18%3 read from
  eval/run_batch0.sbatch — confirms task 6-8=allen_cahn_2d, 9-11=
  fisher_kpp_2d, 12-14=cahn_hilliard). Tasks 15-35 PENDING (cluster
  concurrency cap, same as before). No stall — 256^2 sharp-field tasks run
  ~44 min each (vs ~7-12 min for helmholtz_2d/phase_field_crystal_2d),
  consistent with the prior walk's observation, still within the 6h sbatch
  time budget.
- Timing ledger: upserted 5 new COMPLETED-task entries (job IDs
  65956106_6..10: mf_fno_transfer_film x sharp__allen_cahn_2d x seeds
  {0,1,2} at ~44.4-44.5 min/task, and sharp__fisher_kpp_2d x seeds {0,1} at
  ~44.35-44.53 min/task; gpu_type p100, 200 epochs). `timing_ledger.json`
  now has 11 entries total (was 6); validated as parseable JSON after
  upsert. Still tagged `stream: "batch0"` (G3-gate runs, not stream-card
  runs).
- Abandonment check: no stream has any skipped/blocked batches (no cards
  exist yet) — no abandonment; no `state/streams/*.json` files created
  (nothing to record).
- state/anchors/, state/noise_floor.json: still absent — G3 not complete
  (25/36 tasks remain: 4 running + 21 pending).
- Transcript inbox: `state/transcripts/inbox/` still does not exist —
  nothing to archive.
- No card files touched (`git status --short experiment_cards/` clean,
  confirmed before and after this walk).
- index.md: regenerated (batch0 progress counts, running-jobs table, and
  timestamps refreshed; no structural/status changes to streams).
## RUN END 2026-07-29T04:36:39Z

## RUN START 2026-07-29T04:55:08Z
- Single in-flight check: last run START 2026-07-29T04:36:39Z has matching
  RUN END 2026-07-29T04:36:39Z (~18.5 min ago, closed) — no double-walk
  risk, proceeding.
- Cards walked: 0 (`experiment_cards/` still only `SCHEMA.md`; no B*.json
  cards exist yet). All 5 streams still `current_batch=1`,
  `current_stage=websearch_done_awaiting_G3_brainstormer` — no change.
  `state/streams/*.json` still empty (no stream card history yet, so no
  abandonment is possible).
- G1/G2: still PASS (per state/gates.md, unchanged).
- G3 array job 65956106 progressed since last walk: 14/36 COMPLETED (was
  11/36) — tasks 0-11 done (task 11 = mf_fno_transfer_film x
  sharp__fisher_kpp_2d x seed2, ~44.37 min, finished since last walk), plus
  tasks 15-16 newly completed (ifc_poisson seeds 0-1, ~47s each — fast,
  matches ifc_poisson's small-grid smoke tier). 0 FAILED throughout
  (confirmed via `sacct -P` parsable output). Tasks 12-14 RUNNING
  (mf_fno_transfer_film x sharp__cahn_hilliard x seeds 0-2, ~25-26 min
  elapsed per `squeue -o "%.18i ..."` with full array-task-id column —
  confirmed not the truncated-name aliasing risk from a narrower squeue
  format). Task 17 (ifc_poisson seed2) + tasks 18-35 (mf_fno_pinn_transfer
  x all 6 datasets x 3 seeds) still PENDING (cluster concurrency cap). No
  stall — consistent per-dataset timing pattern holds, still well within
  the 6h sbatch time budget.
- Timing ledger: upserted 3 new COMPLETED-task entries (job IDs
  65956106_11: sharp__fisher_kpp_2d seed2, 44.37 min; 65956106_15:
  ifc_poisson seed0, 0.78 min; 65956106_16: ifc_poisson seed1, 0.78 min;
  gpu_type p100, 200 epochs). `timing_ledger.json` now has 14 entries total
  (was 11); validated as parseable JSON after upsert.
- Abandonment check: no stream has any skipped/blocked batches (no cards
  exist yet) — no abandonment; no `state/streams/*.json` files created
  (nothing to record).
- state/anchors/, state/noise_floor.json: still absent — G3 not complete
  (22/36 tasks remain: 3 running + 19 pending).
- Transcript inbox: `state/transcripts/inbox/` still does not exist —
  nothing to archive.
- Non-r1 out-of-scope job note: `65952144` (plain `bash`) ended TIMEOUT at
  04:00:11 elapsed (2026-07-28T21:49:23) and is no longer in the queue;
  `65958904` (plain `bash`) still PENDING. Both out of scope for this round,
  noted only for index.md accuracy.
- No card files touched (`git status --short experiment_cards/` clean,
  confirmed before and after this walk).
- index.md: regenerated (batch0 progress counts 14/36, running-jobs table
  for tasks 12-14, pending-task description, non-r1 job note, and
  timestamps refreshed; no structural/status changes to streams).
## RUN END 2026-07-29T04:56:52Z

## RUN START 2026-07-29T05:15:35Z
- Single in-flight check: last run START 2026-07-29T04:55:08Z has matching
  RUN END 2026-07-29T04:56:52Z (~19 min ago, closed) — no double-walk risk,
  proceeding.
- Cards walked: 0 (`experiment_cards/` still only `SCHEMA.md`; no B*.json
  cards exist yet). All 5 streams still `current_batch=1`,
  `current_stage=websearch_done_awaiting_G3_brainstormer` — no change.
  `state/streams/*.json` still absent (no stream card history yet, so no
  abandonment is possible).
- G1/G2: still PASS (per state/gates.md, unchanged).
- G3 array job 65956106 progressed since last walk: 19/36 COMPLETED (was
  16/36 per prior orchestrator pulse) — family 0 (`mf_fno_transfer_film`,
  tasks 0-17, all 6 datasets x 3 seeds) is now fully COMPLETED (task 17 =
  ifc_poisson seed2, 0.98 min, finished since last walk); family 1
  (`mf_fno_pinn_transfer`) has begun: task 18 (ext__helmholtz_2d seed0)
  COMPLETED in 7.58 min, matching the family-0 helmholtz_2d timing prior.
  Tasks 19-20 (helmholtz_2d seeds 1-2) RUNNING, ~1 min elapsed (confirmed
  via `sacct -P` with full un-truncated JobID column — squeue's default
  `%.10i` format truncates array task suffixes to a misleading single
  digit, e.g. showed job "65956106_1"/"_2" when the true running tasks
  were "_19"/"_20"; cross-checked against sacct before trusting squeue).
  0 FAILED throughout this job. Tasks 21-35 PENDING (cluster concurrency
  cap). No stall — per-dataset timing pattern holds, well within the 6h
  sbatch time budget.
- Non-r1 wholesale-FAILED job `65955389` (prior batch-0 attempt, bad GPU
  node hpc-93-36) re-confirmed via sacct but already documented in prior
  walks and in commit f8256b4 — not a new delta, no fresh flag raised.
- Timing ledger: upserted 5 new COMPLETED-task entries (job IDs
  65956106_12/_13/_14: sharp__cahn_hilliard seeds 0/1/2, ~44.35 min each;
  65956106_17: ifc_poisson seed2, 0.98 min; 65956106_18:
  mf_fno_pinn_transfer x ext__helmholtz_2d seed0, 7.58 min; gpu_type p100,
  200 epochs). `timing_ledger.json` now has 19 entries total (was 14);
  validated as parseable JSON after upsert.
- Abandonment check: no stream has any skipped/blocked batches (no cards
  exist yet) — no abandonment; no `state/streams/*.json` files created
  (nothing to record).
- state/anchors/, state/noise_floor.json: still absent — G3 not complete
  (17/36 tasks remain: 2 running + 15 pending).
- Transcript inbox: `state/transcripts/inbox/` still does not exist —
  nothing to archive.
- Non-r1 out-of-scope job note: `65958904` (plain `bash`) still PENDING in
  queue — out of scope for this round, noted only for index.md accuracy.
- No card files touched (`git status --short experiment_cards/` clean,
  confirmed before and after this walk).
- index.md: regenerated (batch0 progress counts 19/36, running-jobs table
  for tasks 19-20 and the corrected pending-task dataset breakdown, and
  timestamps refreshed; no structural/status changes to streams).
## RUN END 2026-07-29T05:17:45Z
