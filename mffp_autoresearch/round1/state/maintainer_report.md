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

## RUN START 2026-07-29T05:35:13Z
- Single in-flight check: last run START 2026-07-29T05:15:35Z has matching
  RUN END 2026-07-29T05:17:45Z (~18 min ago, closed) — no double-walk risk,
  proceeding.
- Cards walked: 0 (`experiment_cards/` still only `SCHEMA.md`; no B*.json
  cards exist yet). All 5 streams still `current_batch=1`,
  `current_stage=websearch_done_awaiting_G3_brainstormer` — no change.
  `state/streams/*.json` still absent (no stream card history yet, so no
  abandonment is possible).
- G1/G2: still PASS (per state/gates.md, unchanged).
- G3 array job 65956106 progressed since last walk: 24/36 COMPLETED (was
  19/36 per prior maintainer walk); confirmed via `sacct -P` with the full
  un-truncated JobID column (`squeue -r` also correctly expands array
  tasks when using `-r`, cross-checked, matches sacct). New completions
  since last walk: tasks 19-20 (mf_fno_pinn_transfer × ext__helmholtz_2d
  seeds 1-2, ~7.6 min each, matching the seed0/family-0 helmholtz_2d
  timing prior) and tasks 21-23 (mf_fno_pinn_transfer ×
  sharp__phase_field_crystal_2d seeds 0-2, ~12.2 min each, matching the
  family-0 PFC timing prior). Tasks 24-30 now RUNNING (allen_cahn_2d x3,
  fisher_kpp_2d x3, cahn_hilliard seed0 — the slower 256^2 datasets, 7-20
  min elapsed so far, within the ~44 min family-0 prior for these
  datasets). Tasks 31-35 PENDING (cahn_hilliard seeds1-2 + ifc_poisson
  x3, cluster concurrency cap). 0 FAILED throughout this job — no stall,
  well within the 6h sbatch time budget.
- Non-r1 job note (index.md accuracy only, out of scope for this round):
  `65958904` (plain `bash`), previously PENDING in queue, has since ended
  `CANCELLED by 28156` at 2026-07-28T22:20:58 and is no longer in
  `squeue`. No other non-r1 jobs remain in the queue this walk (confirmed
  via full `squeue -u $USER -r` and `sacct` — only 65956106_* tasks
  present).
- Timing ledger: upserted 5 new COMPLETED-task entries (job IDs
  65956106_19/_20: mf_fno_pinn_transfer x ext__helmholtz_2d seeds 1-2,
  7.60/7.57 min; 65956106_21/_22/_23: mf_fno_pinn_transfer x
  sharp__phase_field_crystal_2d seeds 0-2, 12.17/12.18/12.18 min; gpu_type
  p100, 200 epochs). `timing_ledger.json` now has 24 entries total (was
  19); validated as parseable JSON after upsert.
- Abandonment check: no stream has any skipped/blocked batches (no cards
  exist yet) — no abandonment; no `state/streams/*.json` files created
  (nothing to record).
- state/anchors/, state/noise_floor.json: still absent — G3 not complete
  (12/36 tasks remain: 7 running + 5 pending).
- Transcript inbox: `state/transcripts/inbox/` still does not exist —
  nothing to archive.
- No card files touched (`git status --short experiment_cards/` clean,
  confirmed before and after this walk).
- index.md: regenerated (batch0 progress counts 24/36, running-jobs table
  for tasks 24-30 with per-task node names, updated pending-task dataset
  breakdown for tasks 31-35, non-r1 job note updated to reflect 65958904's
  cancellation, and timestamps refreshed; no structural/status changes to
  streams).
## RUN END 2026-07-29T05:37:02Z

## RUN START 2026-07-29T05:56:26Z
- Single in-flight check: last run START 2026-07-29T05:35:13Z has matching
  RUN END 2026-07-29T05:37:02Z (~19 min ago, closed) — no double-walk risk,
  proceeding.
- no changes: cards walked 0 (`experiment_cards/` still only `SCHEMA.md`),
  all 5 streams still `current_batch=1`,
  `current_stage=websearch_done_awaiting_G3_brainstormer`. G1/G2 still PASS
  (state/gates.md unchanged). G3 array job 65956106 unchanged at 24/36
  COMPLETED (0 new completions since the 05:37 walk), 7 RUNNING (tasks
  24-30, now 26-39 min elapsed, still within the ~44 min family-0 prior for
  these datasets — no stall), 5 PENDING (tasks 31-35), 0 FAILED throughout
  — confirmed via `sacct -P` full un-truncated JobID column cross-checked
  against `squeue -u $USER -r`. No new r1-{stream}-B{N}-s{seed} jobs (no
  cards exist). Timing ledger: 0 new COMPLETED-task entries since last
  walk (still 24 entries, matches 24/36 COMPLETED tasks) — validated as
  parseable JSON, no upsert needed. Abandonment check: no cards exist, no
  abandonment possible, no `state/streams/*.json` files created. Anchors
  (`state/anchors/`) and `state/noise_floor.json` still absent — G3 not
  complete. Transcript inbox: `state/transcripts/inbox/` still does not
  exist — nothing to archive. Non-r1 queue: confirmed empty (previously
  noted `65958904` remains CANCELLED, no new non-r1 jobs). No card files
  touched (`git status --short experiment_cards/` clean, confirmed before
  and after this walk).
- index.md: regenerated (fresh timestamp, elapsed times for tasks 24-30
  updated to 26-39 min; all counts/structure unchanged from prior walk).
## RUN END 2026-07-29T05:57:11Z

## RUN START 2026-07-29T06:18:09Z
- Single in-flight check: last run START 2026-07-29T05:56:26Z has matching
  RUN END 2026-07-29T05:57:11Z (closed, ~20 min before this walk started) —
  no double-walk risk, proceeding.
- Cards walked: 0 (`experiment_cards/` still only `SCHEMA.md`; no B*.json
  cards exist yet). All 5 streams still `current_batch=1`,
  `current_stage=websearch_done_awaiting_G3_brainstormer` — no change.
  `state/streams/*.json` still absent (no stream card history yet).
- G1/G2: still PASS (state/gates.md unchanged).
- G3 array job 65956106 progressed: 31/36 COMPLETED (was 24/36 at last
  walk), 0 RUNNING, 5 PENDING (tasks 31-35), 0 FAILED. Confirmed via
  `sacct -j 65956106 -P` full un-truncated JobID column cross-checked
  against `squeue -u $USER -r` (array fully expanded — only 31-35 remain,
  all PENDING/Priority, no RUNNING tasks currently). New completions
  since last walk: tasks 24-26 (mf_fno_pinn_transfer x
  sharp__allen_cahn_2d seeds 0-2, ~44.3 min each) and tasks 27-30
  (mf_fno_pinn_transfer x sharp__fisher_kpp_2d seeds 0-2 ~44.3 min each,
  plus sharp__cahn_hilliard seed 0 ~44.3 min) — all within the ~44 min
  family-0 prior for these 256^2 datasets, no stall. Remaining tasks
  31-32 (cahn_hilliard seeds 1-2) and 33-35 (ifc_poisson seeds 0-2) are
  PENDING on cluster concurrency, not stalled.
- Non-r1 job note (index.md accuracy only, out of scope for this round):
  sacct also shows `65958902` and `65960289` (both plain `bash`,
  `CANCELLED by 28156`, ended 2026-07-28T20:09 and 20:33 respectively) —
  both predate this round's active window and are not currently in
  `squeue`; no new non-r1 activity this walk (squeue confirmed clean of
  non-r1 jobs).
- Timing ledger: upserted 7 new COMPLETED-task entries (job IDs
  65956106_24/_25/_26: mf_fno_pinn_transfer x sharp__allen_cahn_2d seeds
  0-2, 44.3/44.3/44.28 min; 65956106_27/_28/_29: mf_fno_pinn_transfer x
  sharp__fisher_kpp_2d seeds 0-2, 44.28/44.33/44.33 min; 65956106_30:
  mf_fno_pinn_transfer x sharp__cahn_hilliard seed 0, 44.32 min; gpu_type
  p100, 200 epochs). `timing_ledger.json` now has 31 entries total (was
  24); validated as parseable JSON after upsert.
- Abandonment check: no stream has any skipped/blocked batches (no cards
  exist yet) — no abandonment; no `state/streams/*.json` files created.
- state/anchors/, state/noise_floor.json: still absent — G3 not complete
  (5/36 tasks remain, all pending).
- Transcript inbox: `state/transcripts/inbox/` still does not exist —
  nothing to archive.
- No card files touched (`git status --short experiment_cards/` clean,
  confirmed before and after this walk).
- index.md: regenerated (batch0 progress counts 31/36, running-jobs table
  now shows 0 RUNNING / 5 PENDING (tasks 31-35 only, node-running rows
  removed since all prior running tasks completed), non-r1 job note
  updated with 65958902/65960289, added a "G3 close to completion" flag,
  timestamps refreshed; no structural/status changes to streams).
## RUN END 2026-07-29T06:19:02Z

## RUN START 2026-07-29T06:35:26Z
- Single in-flight check: last run START 2026-07-29T06:18:09Z has matching
  RUN END 2026-07-29T06:19:02Z (~16 min ago, closed) — no double-walk risk,
  proceeding.
- no changes: cards walked 0 (`experiment_cards/` still only `SCHEMA.md` +
  `.gitkeep`; no B*.json cards exist). All 5 streams still `current_batch=1`,
  `current_stage=websearch_done_awaiting_G3_brainstormer`. G1/G2 still PASS
  (state/gates.md unchanged).
- G3 array job 65956106 unchanged at 31/36 COMPLETED, 0 RUNNING, 5 PENDING
  (tasks 31-35), 0 FAILED — identical counts to the prior walk (0 new
  completions since 06:19). Confirmed via `squeue -j 65956106 -a -r` (all
  5 remaining tasks `PD (Priority)`, 0:00 elapsed — never started, not
  vanished) cross-checked against `sacct -j 65956106 -P` (no records for
  tasks 31-35, consistent with never-started). `gpu` partition shows 238
  PENDING jobs cluster-wide (informational only, down from ~253 last
  walk) — consistent with slow fairshare drain, not a stall.
- Non-r1 queue: confirmed empty of new activity; historical CANCELLED jobs
  `65958902`/`65958904`/`65960289` unchanged, out of round scope.
- Timing ledger: 0 new COMPLETED-task entries since last walk (still 2
  top-level keys / same entry count as before — validated `json.load`
  succeeds, parseable).
- Abandonment check: no cards exist, no abandonment possible; no
  `state/streams/*.json` files exist or created this walk.
- state/anchors/, state/noise_floor.json: still absent (only `.gitkeep`)
  — G3 not complete (5/36 tasks remain, all pending).
- Transcript inbox: `state/transcripts/` directory does not exist —
  nothing to archive.
- No card files touched (`git status --short experiment_cards/` clean,
  confirmed before and after this walk).
- index.md: regenerated (fresh timestamp; G3 flag reworded to clarify the
  5 remaining tasks are fairshare-queued rather than running, since 0 are
  currently RUNNING this walk vs 7 running two walks ago; queue-depth note
  updated 253->238; all other counts/structure unchanged).
## RUN END 2026-07-29T06:37:40Z
