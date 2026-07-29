
## 2026-07-29T03:36:51Z — ROUND LAUNCHED (orchestrator = this session)
- Crons: pulse */10 (c00486f8), maintainer 7,27,47 (c9c02810), auto-sync 13,43 (f18c5e2c). Session-only, 7-day expiry.
- batch0 (G3) job 65956106 pending, planned start ~21:37 PDT; monitor armed.
- Dispatched batch-1 websearchers for s1_poisson, s2_beyond_copy, s3_testtime, s4_hybrid_routing (background).
- s5_tuning-B1: websearch complete; brainstormer gated on state/noise_floor.json (G3), then full G4 chain.
- Gate discipline: no stream past brainstormer until G3; only s5_tuning-B1 builds/submits before G4 PASS.
- 2026-07-29T03:43:59Z pulse: no-op. batch0: 3 COMPLETED / 18 RUNNING / rest pending, 0 failed. s1-s4 websearchers still running (no reports yet); s5 gated on G3 noise floor. Nothing unblocked.

## WEBSEARCH PHASE COMPLETE (all 5 streams, batch 1)
- s1_poisson: PARTIAL (agent couldn't Write .md — orchestrator persisted all 7 files verbatim). Verdict: all-ordered-pairs = preempted-but-MF-composition-open; D2/D3 preempted. Key: pair-set contrast (adjacent vs all-ordered vs LF->HF-only) is the falsifiable design; 0.036/0.018 method attribution UNRESOLVED — cards must not assert it.
- s2_beyond_copy: SUCCESS. All metrics for the diagnostic are published (band error, H(k), coherence, interface stratification, PFI) — but copy-LF-as-baseline is genuinely absent from MF operator learning (the round's framing is the novelty). Diagnostic card should include LF-permutation probe + same-parameter pairing sanity check.
- s3_testtime: SUCCESS. REFUTED program.md §12.3's -21% prior in-repo (mf_fno_ptr no-op outside ifc_*; -1.5% inside CI at 163x latency where it ran). True residual computable only for helmholtz_2d. Operator corrected §12.3 via ADR 0003. D4 (equilibrium projection, test-time) weakly novel.
- s4_hybrid_routing: SUCCESS. D1 (score fno_transolver_seq) = measurement, zero novelty claims; D2 LF-conditioned routing open (no published router reads LF/LF-HF disagreement); D3 adjacent to pre-falsified mf_fno_spectral — flagged.
- LESSON (all agents): subagent Write tool refuses .md report files; s2/s4/s5 used shell heredoc; s1 returned inline. Future dispatch prompts must include: "write report files via bash heredoc (cat > file <<'EOF'), not the Write tool."
- NEXT: all brainstormers gated on G3 noise floor (batch0 job 65956106).
- 2026-07-29T03:54:11Z pulse: no-op. batch0 healthy: 6 COMPLETED (JSONs verified on disk), 5 RUNNING, 25 pending, 0 failed; ~8-12 min/task. All streams at websearch_done_awaiting_G3_brainstormer. Nothing unblocked.
- 2026-07-29T04:03:58Z pulse: no-op. batch0: 6 done / 6 running / 24 queued (cluster-limited concurrency), 0 failed. Streams unchanged, G3 pending.
- 2026-07-29T04:14:04Z pulse: no-op. batch0: 6 done, 6 running (tasks 6-11, 20-33 min elapsed — the 256^2 sharp datasets are slower than helmholtz/PFC, within budget), 24 queued, 0 failed. G3 pending; streams unchanged.
- 2026-07-29T04:24:06Z pulse: no-op. batch0 unchanged: 6 done, tasks 6-11 running 30-43 min (256^2 sharp sets; within 3h budget), 24 queued, 0 failed. G3 pending.
- 2026-07-29T04:33:59Z pulse: no-op. batch0: 11/36 done (256^2 tasks ~45-50 min each), 4 running, 21 queued, 0 failed. G3 pending.
- 2026-07-29T04:43:57Z pulse: no-op. batch0: 14/36 done, 3 running, 19 queued, 0 failed. Family 1 (mf_fno_pinn_transfer) tasks up next. G3 pending.
- 2026-07-29T04:54:13Z pulse: no-op. batch0: 14/36 done (incl. fast ifc_poisson tasks 15-16), cahn_hilliard seeds 12-14 running ~24 min, 19 queued (Priority), 0 failed. G3 pending.
- 2026-07-29T05:03:55Z pulse: no-op. batch0: 14/36 done, 4 running, 0 failed. G3 pending; streams unchanged.
- 2026-07-29T05:14:05Z pulse: no-op. batch0: 16/36 done, cahn_hilliard seeds ~44 min (near done), 0 failed. Remaining 20 tasks = mf_fno_pinn_transfer family. G3 pending.
- 2026-07-29T05:23:55Z pulse: no-op. batch0: 21/36 done, 6 running, 9 queued, 0 failed. pinn_transfer family moving fast. G3 pending.
- 2026-07-29T05:34:02Z pulse: no-op. batch0: 24/36 done, 7 running (tasks 24-30), 5 queued (31-35 = pinn fisher/cahn/ifc tail), 0 failed. G3 close — expect completion within ~2 pulses.
- 2026-07-29T05:43:55Z pulse: no-op. batch0: 24/36 done, 7 running + 5 queued (256^2 tail), 0 failed. G3 pending.
- 2026-07-29T05:54:01Z pulse: no-op. batch0: 24/36 done; tasks 24-30 at 24-37 min (256^2, ~45 min expected), 5 queued, 0 failed. G3 likely next pulse.
- 2026-07-29T06:03:56Z pulse: no-op. batch0: 25/36 done, 6-7 in flight, 0 failed. G3 pending.
- 2026-07-29T06:14:06Z pulse: no-op. batch0: 30/36 done, last tasks in flight, 0 failed. G3 aggregation next pulse (or on monitor fire).
- 2026-07-29T06:24:03Z pulse: no-op. batch0: 31/36 done, final 5 tasks queued (Priority), 0 failed. G3 aggregation fires when they clear.
- 2026-07-29T06:34:06Z pulse: no-op. batch0: 31/36; final 5 tasks pending behind a deep gpu queue (253 pending jobs partition-wide), 0 failed. Waiting on fairshare.
- 2026-07-29T06:43:58Z pulse: no-op. batch0: 34/36 done, last 2 (cahn_hilliard tail) running, 0 failed. G3 aggregation imminent.
- 2026-07-29T06:53:56Z pulse: no-op. batch0: 34/36, last 2 running, 0 failed.
- 2026-07-29T07:03:55Z pulse: no-op. batch0: 34/36, final 2 cahn_hilliard seeds ~30 min elapsed (~44 expected), 0 failed.
- 2026-07-29T07:13:55Z pulse: no-op. batch0: 34/36, last 2 tasks ~34 min elapsed, 0 failed. G3 next.

## 2026-07-29T14:29:11Z — G3 PASS
- batch0 36/36, 0 failed. Anchors + noise floor certified (champion geomean skill 6.703 [6.219,7.102] @ 200ep).
- ALERT: helmholtz noise floor 9.695 (diverging seed) — claims there unfalsifiable at smoke tier; passed to brainstormers.
- Dispatching ALL 5 brainstormers (batch 1). s5_tuning continues the G4 chain (starter/builder/review/submit follow); s1-s4 hold after brainstormer until G4 PASS.

## Pulse — 2026-07-29T14:34Z

pulse: no-op. All 5 streams at brainstormer_running (batch 1); all 5 brainstormer
background agents still in flight; no r1-* SLURM jobs. Maintainer walk completed
clean (G3 flip confirmed, timing ledger 36/36, cards git-clean). Waiting on
brainstormer returns; s5_tuning-B1 will continue the G4 chain on completion.

## Brainstormer return — s1_poisson-B1 — 2026-07-29T14:41Z

SUCCESS / slot_filled (12/12 checklist). Stage → brainstormer_done_awaiting_G4
(holds per G4 rule; starter dispatch deferred until G4 PASS).

Load-bearing verified finding: ifc_poisson's 4 fidelity levels are NOT
sample-aligned (np.allclose(X8[:5], X64) False, max |diff| 0.581), while the
§12.1 seed family mf_fno_allpairs assumes index alignment in build_pairs and
finetune — corroborated by its 0.4657 ifc_poisson / 0.1457 ifc_heat bench rows
(~10-16x worse than transfer_film on exactly the non-aligned datasets).
Running the seed direction as-is would have reproduced that defect.

Slot: fix correspondence (conditions from TARGET fidelity + include self-pairs),
then sweep pair-set arms two_level/adjacent/allpairs/legacy_pairing on
ifc_poisson at N_hf=5. Recipe: base mf_fno_allpairs @967562e, family_dir
models_r1/mf_fno_ladder, 200 ep, seeds 0-2, env MFFP_LADDER_MODE,
--time=01:00:00. Falsification threshold 0.240 skill (certified floor); cratered
rule applies to primary arm (allpairs) only — legacy_pairing cratered by design.
Build traps recorded: per-arm ckpt key + ROUND1_EVAL_RESULTS (score_panel
out-path collision), vendor the family (code_hash cannot see akash imports).
prior_art.verdict maps to preempted-pivoted.

## Pulse + brainstormer return — s2_beyond_copy-B1 — 2026-07-29T14:44Z

Pulse: s1 holds at brainstormer_done_awaiting_G4; s3/s4/s5 brainstormers still
in flight; no r1 SLURM jobs. Only new action: s2 return processed.

s2_beyond_copy-B1: SUCCESS / slot_filled (12/12). Stage →
brainstormer_done_awaiting_G4 (starter deferred until G4 PASS).

Slot: DIAGNOSTIC card — copy-LF excess-error forensics
(models_r1/s2_copylf_forensics, epochs 0, seed 0): reload both batch-0 champion
checkpoints, decompose LF/model/HF on the 5 beyond-copy datasets (LF-blindness
forward-hook audit, X-only sufficiency ladder via score_panel, spectral band
ratios, interface stratification, amplitude/pairing controls).

Key reframe: both certified families appear structurally LF-BLIND at inference
(eval feeds condition vector only; MF lives in the training schedule) — so
"model destroys LF info" may be a category error. Calibration probes (marked
non-reportable, §2.1): fisher_kpp sits at a nearest-neighbour floor (two
failure modes on the panel, not one); on pfc a trivial 1-NN-in-X gives 0.019 vs
champion 0.515. Headline scored through eval layer with copy-LF seam check
(≤1e-9 vs copylf_baselines.json), _train monkeypatch tripwire, batch-0
reproduction check. helmholtz carries NO numeric claim (floor 9.695); other
thresholds ≥1.0/≥2.0/≥5.0 vs certified floors.

## Brainstormer return — s5_tuning-B1 — 2026-07-29T14:44Z — G4 CHAIN OPENS

SUCCESS / slot_filled (12/12). Stage → starter_running; dispatching
experiment-starter (G4 dry-run card; this is real s5_tuning batch 1).

Slot: modes_cap 12→32 on champion mf_fno_transfer_film via single env knob
MFFP_MODES_CAP=32, panel @200 ep, seeds {0,1,2}. One arm only — batch-0
certified the cap-12 control; family copy's ONLY behavioural change is the env
read, with contract-tier default-equivalence proof vs the untouched factory
family required before submit. Geomean threshold 0.884 skill units (13.2%) vs
anchor 6.703; per-dataset thresholds = certified min_claimable_effect verbatim;
helmholtz carries NO claim (floor 9.695). Build notes for starter/builder:
smoke_eval.py:37 REPO_ROOT relocation fix; knob-fired audit (n_params
4.77M→~3.36e7, extra.modes_cap); --time 08:00:00; divergence at cap 32 is a
result, not a bug.

## Returns — s3_testtime-B1 brainstormer + s5_tuning-B1 starter — 2026-07-29T14:50Z

s3_testtime-B1: SUCCESS / slot_filled (11/11). Stage → brainstormer_done_awaiting_G4.
DIAGNOSTIC card (epochs 0, ~10 GPU-min vs 7.7 GPU-h for the rejected model card):
is the exact Helmholtz residual a non-solver error signal, or does it re-solve /
annihilate? Design probes killed the D1 model card: (1) VACUITY — Helmholtz op
exactly diagonalised by 2-D DST-I; test HF fields reproducible to 2.2e-13 from
the condition vector by two FFTs (unbounded refinement = model-free re-solve);
(2) COLLAPSE — 1-dof residual-optimal rescale sends copy-LF 0.33→0.9964 (ENS
hazard instantiated); (3) champion Helmholtz output near-orthogonal to truth
(cos 0.37-0.54, oracle rescale only reaches skill ~2.8). Falsification threshold
10.78 > 9.695 floor with zero-predictor bar. Handed forward: global-scaler
normalisation knob (408x per-sample spread) for s5/s2; BENCHMARK-INTEGRITY FLAG
for mentor: helmholtz test HF is two-FFT reproducible from the condition vector —
any method with the exact operator at test time scores ~0 without a model.

s5_tuning-B1 starter: SUCCESS / drafted (13/13, no TBDs). Card at canonical
experiment_cards/s5_tuning/batch_1/B1.json (my .md path was wrong; SCHEMA wins).
Worktree worktrees/s5_tuning/B1 on round1/exp-s5_tuning-B1 @967562e. Recipe
family_dir is models_r1/mf_fno_transfer_film_modes (report verbatim — NOT
mf_fno_modescap as my launch note said). Stage → builder_running; dispatching
experiment-builder.

## Operator note — proposals backlog — 2026-07-29T14:51Z

Forked /btw session audited the 5 pre-kickoff docs/proposals files round-1
setup never read. Strong independent convergence (F01/nRMSE, A6/batch-0,
A9=s5-B1, MF-composition-as-thesis). Un-ingested items recorded as batch-2
candidate seeds in docs/operator_notes/2026-07-29-proposals-backlog.md:
warp/registration fusion (Candidate D), residual-spectrum FFT diagnostic (D1),
pinn_transfer attribution (A7), structural constraints (F14-F18). Batch-2
brainstormer dispatches will cite this note; numbers therein are uncertified.

## Brainstormer return — s4_hybrid_routing-B1 — 2026-07-29T14:52Z

SUCCESS / slot_filled (12/12). Stage → brainstormer_done_awaiting_G4. ALL FIVE
batch-1 brainstormers now complete; s5 builder in flight (G4 chain).

Slot: mf_composition_measurement / model card — benchmark the built-but-never-
scored fno_transolver_seq (FNO-FiLM base + zero-init alpha-gated Transolver
corrector on out-of-fold LF→HF residuals), panel @200 ep, seeds {0,1,2}. Why
informative: the certified champion NEVER consumes the LF field at test time —
fno_transolver_seq is the round's first model whose prediction path cross-
attends to real test-time LF. Free paired control: stage-1 base is byte-
identical SMOKE config to champion (base_only_rel_l2 = plumbing gate vs
anchor). alpha gate is self-testing (least-squares + line search containing 0),
so alpha=0 is a measured verdict needing no noise-floor argument — key on
helmholtz where score claims are unfalsifiable. Contract-tier CPU run verified:
ifc_poisson rel_l2 0.4386 vs base_only 0.4900 (-10.5%), alpha=1.5. Two
mechanical worktree edits specified (path resolution, MFFP_CTX_SOURCE env);
a third should draw reviewer FAIL. 256^2 p100 memory question left to builder
contract gate.

## Pulse — 2026-07-29T14:54Z

pulse: no-op. s1-s4 hold at brainstormer_done_awaiting_G4 (correct per gate);
s5_tuning builder agent still in flight; no r1-* SLURM jobs. Next action fires
on the builder's return (→ code-reviewer → seed-0 submit → G4).

## Pulse — 2026-07-29T15:04Z

pulse: no-op. s1-s4 hold at brainstormer_done_awaiting_G4; s5_tuning builder
agent still in flight (maintainer confirmed it actively writing the family
files); no r1-* SLURM jobs. Awaiting builder return → code-reviewer.

## Pulse — 2026-07-29T15:14Z

pulse: no-op. Unchanged: s1-s4 await G4; s5_tuning builder still in flight;
no r1-* SLURM jobs.

## Pulse — 2026-07-29T15:23Z

pulse: no-op. s1-s4 await G4; s5_tuning builder still in flight (maintainer:
family dir + all 3 launch scripts written, card mechanics fields not yet
committed — builder in final verification/commit phase). No r1-* SLURM jobs.

## Pulse — 2026-07-29T15:33Z

pulse: no-op. s1-s4 await G4; s5_tuning builder agent still in flight; no r1-*
SLURM jobs. Builder runtime is long but consistent with its verification suite
(contract smoke + resume + default-equivalence + knob audit = multiple 2-epoch
training runs).

## Pulse — 2026-07-29T15:43Z

pulse: no-op. s1-s4 await G4; s5_tuning builder in flight — maintainer's last
walk saw live contract-tier verification artifacts (default-equivalence + both
resume proofs) minutes old in the worktree scratchpad. No r1-* SLURM jobs.

## Pulse — 2026-07-29T15:53Z

pulse: no-op. Unchanged: s1-s4 await G4; s5_tuning builder in flight (progress
confirmed by maintainer 15:37Z walk); no r1-* SLURM jobs.

## Operator decision — ADR 0004 strict single-seed — 2026-07-29T16:05Z

Eloise directed (AskUserQuestion): strict 1-seed in-round; seeds 1-2 only for
the end-of-round top-3 confirmation. Applied: project.yaml seed_protocol,
program.md §2.4/§4.3/§4.4, docs/adr/0004-strict-single-seed.md. Card recipes'
locked seeds fields untouched; execution governed by ADR. s5_tuning-B1 will
submit seed 0 only; initial-analyzer reports provisional-single-seed.

## Pulse — 2026-07-29T16:06Z

s1-s4 await G4; no r1-* SLURM jobs. s5_tuning ANOMALY handled: builder handoff
filed ~45 min ago (all 3 proofs pass) but no build commit on the branch (HEAD
still 967562e) and card mechanics empty — agent still running with nothing
external to wait on. Sent the builder a status-check message: finalize (atomic
commit + card mechanics + return) or report what verification is still running;
also notified it of ADR 0004 (no deliverable change). Will dispatch
code-reviewer on its return.

## Builder return — s5_tuning-B1 — 2026-07-29T16:10Z

SUCCESS / built (14/14). Build commit ad29239 on round1/exp-s5_tuning-B1,
worktree clean. Proofs: default-equivalence identical to last digit (helmholtz
22.613192981264614, ifc_poisson 0.4900025652737081, both = untouched factory
family); mid-stage resume bit-identical; knob audit n_params 4,773,953 →
33,609,793 (Δ = 2·4·64²·(32²−12²) exact), JSON carries modes_cap 32 +
provenance. Deviations accepted (all evidence-backed): job name
r1-s5_tuning-B1-s{seed} (maintainer regex), outputs <outputs_root>/s5_tuning/
B1/eval/result_panel_s{seed}.json (analyzer glob + §10), ROUND1_EVAL_RESULTS
export for ckpt/preds relocation. OPEN: guard-set contract run ships as
02_guard_contract.sh (GPU) — to fire alongside seed 0; required by §2.3 before
any panel-win claim. Stage → review_running; dispatching code-reviewer.

## Pulse — 2026-07-29T16:13Z

pulse: no-op. s1-s4 await G4; s5_tuning code-reviewer in flight (dispatched
16:0x-ish, no review file yet); no r1-* SLURM jobs. On reviewer
PASS/SUGGEST: submit seed 0 via scripts/submit.sh + fire 02_guard_contract.sh.

## Operator decisions — ADR 0005 (H100) + ADR 0006 (G4 submit-verified) — 2026-07-29T16:17Z

Eloise: switch to H100 keeping 200 epochs (rejected 30-min wall cap; anchor
re-cert run fires alongside s5 seed 0). Eloise questioned s1-s4 serialization;
G4 split into G4a (build-path, already evidenced — starters/builders unblocked
NOW) and G4b (submit-path — s1-s4 SLURM submits wait until s5-B1 seed 0 is
running + writing valid output). Dispatching all four s1-s4 starters in
parallel; stages → starter_running. s5-B1 submit will use --gres=gpu:h100:1
--time=02:00:00 CLI overrides.

## Review verdict + submissions — s5_tuning-B1 — 2026-07-29T16:18Z

Code-reviewer: SUGGEST / submit-as-is (review_B1.md; 7 questions: 5 PASS, 2
SUGGEST — S1 job-name nit covered by submit path, S2 TIMEOUT→treat as INFRA,
S3 guard-set run to fire alongside). SUBMITTED on H100 (ADR 0005 CLI
overrides): seed 0 = job 65988184 (--gres=gpu:h100:1 --time=02:00:00), guard
contract = job 65988185, anchor re-cert (champion, --no_cache, H100) = job
65988186 via new eval/run_recert_h100.sbatch. Stage → seed0_running. G4a PASS
recorded (ADR 0006); G4b pending on first valid seed-0 output. Dispatching
s1-s4 starters (G4a unblock).

## Starter return — s3_testtime-B1 — 2026-07-29T16:21Z

SUCCESS / drafted (14/14, no TBDs). Card at experiment_cards/s3_testtime/
batch_1/B1.json (diagnostic: epochs 0, seed 0, family_dir models_r1/
hh_residual_anatomy, dataset ext__helmholtz_2d, six HHDIAG_* env knobs).
Handoff flags M0 as HARD-STOP build gate + read-only last.pt dependency under
round1/eval/results/mf_fno_transfer_film/. Stage → builder_running; dispatching
experiment-builder (G4a: builds allowed; submission waits on G4b).

## Starter return — s1_poisson-B1 — 2026-07-29T16:22Z

SUCCESS / drafted (13/13, no TBDs). Card at experiment_cards/s1_poisson/
batch_1/B1.json (model: base mf_fno_allpairs, family_dir models_r1/
mf_fno_ladder, ifc_poisson, 200 ep, MFFP_LADDER_MODE arms sweep). Handoff
records ADR 0004/0005 execution overrides vs card text. Build traps in part 3:
per-arm ckpt key + per-arm ROUND1_EVAL_RESULTS (path collision), vendored
family (no akash imports). Stage → builder_running; dispatching builder.

## Starter return — s2_beyond_copy-B1 — 2026-07-29T16:22Z

SUCCESS / drafted (13/13, no TBDs). Card at experiment_cards/s2_beyond_copy/
batch_1/B1.json (diagnostic: epochs 0, seed 0, family_dir models_r1/
s2_copylf_forensics, 8 S2B1_* env knobs). Starter flagged: prior_art.verdict
is the literal non-enum string "preempted-but-MF-composition-open" (verbatim >
normalize; reviewer should not read as error). Report §Notes lines 166-192
load-bearing for build: batch-0 last.pt sha256+mtime to build_notes, hard-stop-
never-retrain on missing/mismatched checkpoint, scored test_hf = training-free
1-NN-in-X (part 5 must say so). Stage → builder_running; dispatching builder.

## Pulse — G4 PASS + s4 starter return — 2026-07-29T16:24Z

G4b evidence: guard job 65988185 COMPLETED 46 s (valid seam-checked JSON,
geomean skill 4.88 at 2 ep incl. guard datasets); seed-0 job 65988184 RUNNING
on hpc-33-16; recert 65988186 pending. G4 recorded PASS — s1-s4 submissions
unblocked, will fire per-stream on review PASS/SUGGEST.

s4_hybrid_routing-B1 starter: SUCCESS / drafted (14/14, no TBDs; parts
extracted programmatically byte-verbatim). Stage → builder_running;
dispatching builder. Card mandates EXACTLY two mechanical edits (third =
reviewer FAIL); open risk: 256² GPU memory (n_query 2048 / n_ctx 1024 /
corr_batch 4) unobserved beyond ifc_poisson contract run — H100 80GB makes
this much less likely to bite than the p100 16GB the report assumed.

Streams: s1 builder_running, s2 builder_running, s3 builder_running,
s4 builder_running, s5 seed0_running.

## ADR 0007 — propose-many/screen-cheap/promote-few — 2026-07-29T16:25Z

Codified for batch >= 2 model cards with design freedom (diagnostics and
pre-directed slots exempt). Batch-2 brainstormer dispatches will cite it.
Batch 1 unaffected (cards locked, builds in flight).

## Pulse — 2026-07-29T16:34Z

pulse: no-op. Four builders in flight (s1-s4); s5 seed 0 RUNNING 15 min on
hpc-33-16 (score_panel caches per dataset as it finishes; panel JSON lands at
end); recert 65988186 still PENDING. G4 PASS recorded last pulse; next
advances fire on builder returns (→ reviewers → seed-0 submits).

## ADR 0004 clarification — 2026-07-29T16:37Z

Eloise confirmed: top-3 selection fires once at round end (after ~3-4 batches/
stream, all streams terminal or operator call), over the cumulative provisional
leaderboard. Appended to ADR 0004.

## Maintainer catch + fixes + ADR 0008 — 2026-07-29T16:40Z

Maintainer flagged recert job 65988186 FAILED 1s: my run_recert_h100.sbatch
sourced nonexistent venv (SURF_2026-main path); fixed to $PROJECT_ROOT/.venv
(matches run_batch0.sbatch) and resubmitted as 65989097. INFRA, orchestrator-
owned, no debugger needed, no ALGO count. s5-B1 card job_ids mechanics field
backfilled (was []). Seed 0 progressing: 3/6 panel datasets written at ~19 min.

ADR 0008: Eloise directed pinn (mf_fno_pinn_transfer) retired — no future
cards on it, excluded from leaderboard/top-3; batch-0 data retained (anchors
unaffected — all best-family skills were transfer_film's); s2-B1's locked
forensics card proceeds (measures pinn checkpoints as evidence, doesn't build
on them).

## Operator amendment — pinn removed from s2-B1 — 2026-07-29T16:43Z

Eloise: "delete pinn from current cards". Only s2_beyond_copy-B1 referenced
pinn. Card amended (operator_amendments entry, ADR 0008 updated):
S2B1_BASE_FAMILIES = mf_fno_transfer_film only. Messaging the in-flight s2
builder to drop the pinn measurement path.

## Pulse + recert correction — 2026-07-29T16:45Z

Pulse: s1-s4 builders in flight; s5 seed 0 RUNNING 26 min (healthy).

Recert 65989097 "COMPLETED 29s" investigated: NOT a training run — smoke_eval
checkpoint-resume found the finished batch-0 checkpoints under the default
results root and skipped to eval. What it DID establish: H100 inference on
p100 weights reproduces batch-0 metrics to ~6 digits (helmholtz 6.2023287 vs
6.2022660; geomean 7.1034 vs 7.102) — inference-path drift negligible vs
floors. For the actual training-dynamics check, run_recert_h100.sbatch now
exports a fresh ROUND1_EVAL_RESULTS (training_h100/) and writes
h100_champion_seed0_retrain.json; resubmitted as job 65989241. ADR 0005 anchor
carry-over verdict waits on the retrain comparison.

## Builder return — s2_beyond_copy-B1 — 2026-07-29T16:52Z

SUCCESS / built (10/10). Commits f38d8db (build) + ba48712 (ADR 0008 pinn
strip, smoke re-run after). Seam evidence: copy-LF delta 0.0 exact vs
baselines (all 5 datasets); _train tripwire armed, never fired; LF-blindness
M1 confirmed at contract tier (only the [16,3] condition vector enters the
net); checkpoint repro rel deltas 4.6e-7..8.7e-6. Deviation accepted:
card's 1e-9 checkpoint-repro tolerance is physically unachievable cross-
hardware (p100-trained weights, h100 eval, float32 kernels ~1e-6 rel);
implemented as abort >1e-3 rel + recorded repro_exact_1e9 boolean — interlock
purpose (checkpoint/data identity) preserved. No seeds_2_3 script (diagnostic,
§4.3). Stage → review_running; dispatching code-reviewer.

## Pulse — 2026-07-29T16:54Z

pulse: no-op. s2 in code review; s1/s3/s4 builders in flight; s5 seed 0
RUNNING 35 min (panel JSON lands at completion); recert retrain RUNNING 8 min
(genuinely training this time — past the 29s resume signature). All agents/
jobs healthy; nothing unblocked.

## Builder return — s1_poisson-B1 — 2026-07-29T16:54Z

SUCCESS / built (13/13). Commit d070f86. Four arms verified at contract tier
(distinct code_hash per arm = env knob in cache key); resume drills: finished
(train_seconds 1.4e-6), mid-stage SIGTERM (stage/epoch restored), cross-arm
isolation (bit-identical vs standalone), foreign-mode ckpt refused, bogus mode
errors. Correspondence fix verified: cross blocks bit-equal to target-fidelity
conds; row counts 110/250/280/280 match card; measured non-alignment recorded
score-neutrally (8→64 max diff 0.5809). Deviations recorded (full 200-ep
finetune per card; ckpt subdir per-arm; 02:00:00 per ADR 0005). Stage →
review_running; dispatching code-reviewer.

## s5-B1 seed 0 COMPLETE — 2026-07-29T17:01Z

Job 65988184 COMPLETED (maintainer walk): panel geomean skill 6.1958 vs anchor
6.703 [6.219, 7.102]. Improvement 0.507 < card threshold 0.884 (provisional-
single-seed; ADR 0004 — no seeds 1-2). Verdict belongs to the initial-
analyzer; dispatching it now. Stage → initial_analysis_running. Guard-set
result already on disk (guard_contract_s0.json). Recert retrain still RUNNING
(will serve as same-hardware cap-12 control for part-5 context).

## Review verdict + submit — s1_poisson-B1 — 2026-07-29T17:04Z

Code-reviewer: SUGGEST / submit-as-is (6/6; correction independently re-proven
offline: row counts 110/250/280/280 reproduced, aligned-ladder no-op
demonstrated byte-equal, legacy_pairing faithfully defective, backbone sha
identical to akash original). Analyzer notes recorded in review_B1.md: S2
amplitude-domination caveat (per-fid max|Y| spans 42x — read allpairs≈
two_level null against it), S3 seeds vary via init only, S4 legacy isolates
cross-row correspondence only. Submitted seed 0 via submit.sh → job 65991280
(H100). Stage → seed0_running; card job_ids updated.

## Pulse + review verdict + submit — s2_beyond_copy-B1 — 2026-07-29T17:04Z

Pulse state: s1 seed0 PENDING (65991280); s3/s4 builders in flight; s5 initial
analyzer in flight; recert retrain RUNNING 19 min.

s2 code-reviewer: SUGGEST / submit-as-is (6/6; independently re-hashed all 15
frozen batch-0 last.pt — sha/size/mtime unchanged after two reload passes;
copy-LF seam delta exactly 0.0; pinn strip structural; 1e-3 tolerance
deviation accepted with 500x failure-mode margin). Applied S1 at submit time:
exported ROUND1_EVAL_RESULTS=outputs/s2_beyond_copy/B1/eval/results (sbatch
--export=ALL default propagates; script does not override). S3 noted:
s2_copylf_forensics is a lookup, excluded from leaderboard. Submitted seed 0
→ job 65991328. Stage → seed0_running; card job_ids updated.

## ADR 0009 — unknown-physics constraint — 2026-07-29T17:13Z

Eloise (mentor guidance): models must not assume known PDE at test time
(weather = canonical case). s3-B1 diagnostic completes as designed (exempt:
measurement, and its outcome evidences the ADR). s3 batch 2 re-scopes to
physics-agnostic test-time levers or retires cleanly. Batch-2 brainstormer
dispatches will cite ADR 0009 for ALL streams (no physics-embedded model
candidates anywhere).

## Stream replacement — s3_testtime → s3_warp — 2026-07-29T17:15Z

Eloise: remove s3, replace. Builder stopped (no GPU spent, no SLURM ever
submitted). Card retired_by_operator (audit trail kept; not a skip). ADR 0010;
project.yaml + program.md §12.3 rewritten. New stream s3_warp (lever):
warp-then-correct registration fusion (NEW_MODELS.md Candidate D — only
un-preempted backlog candidate; physics-agnostic per ADR 0009; targets the
interface-displacement failure mode; topology-mismatch threat flagged).
Dispatching s3_warp batch-1 websearcher now (prior-art re-verification
mandatory).

## Pulse — s1 + s2 seed-0 COMPLETE — 2026-07-29T17:16Z

s1 job 65991280 COMPLETED 4m28s (4 arms x 200 ep, H100). Raw arm skills on
ifc_poisson (orchestrator glance; verdicts belong to analyzer): two_level
2.853 / adjacent 6.055 / allpairs 5.813 / legacy_pairing 8.362. Correspondence
fix clearly helps (allpairs vs legacy), but two_level dominating allpairs is
the headline pattern to analyze (reviewer's amplitude-domination caveat S2
applies). s2 job 65991328 COMPLETED 46s; result_beyond_copy5_s0.json + 5
per-dataset diagnostics JSONs present. Dispatching both initial-analyzers +
maintainer. s4 builder + s3_warp websearcher + s5 analyzer + recert (30 min)
still in flight.

## New stream s6_local — ADR 0011 — 2026-07-29T17:20Z

Eloise proposed additional streams. Added s6_local (lever, H2 test: FNO x
local-representation hybrids), filling the approved 4-6 envelope. FNO-
Transolver variants routed to s4 batch 2 instead (question ownership).
Motivation: s5-B1's H1 result (modes 12->32 = +0.507 < 0.884 floor) makes H2
the live hypothesis. Constraints: diagnose mentor's failed FNO-CNN attempt
first; convnext panel record says composition not capacity. Dispatching
batch-1 websearcher. program.md §12.6 to be appended by operator next edit
(conventions mirror ADR 0011).

## Initial analysis — s1_poisson-B1 — 2026-07-29T17:21Z

analyzed_single_seed. VERDICT: cratered (allpairs 5.813 > 2.35 = 1.5x anchor)
+ FALSIFIED per clause (allpairs must beat two_level by >0.240; measured
-2.960). But C1 CLEARS 10.6x floor: correspondence fix is real (+2.549 skill
at fixed rows, legacy 8.362 → allpairs 5.813). C3: controlling variable is
the LEVEL SET not the pair set (two_level 2.853 dominates, wins 125/128
samples, uniform 2x degradation). C2b adjacent≈allpairs noise-compatible.
Amplitude-domination caveat unresolved (42x max|Y| spread, shared scaler) —
top part-6 probe. No anomalies; 4.45 min total H100. Stage →
mechanism_analysis_running; dispatching mechanism-analyzer.

## New stream s7_loss (ADR 0012) + scouting search — 2026-07-29T17:25Z

Eloise asked for further streams from proposals/reports/deep-search. Added
s7_loss (interface-aware training objectives; F14-F18 backlog; metric
unchanged, objective changes; envelope now 7 by her direction). DEFERRED
s8_data (cross-dataset pretraining / N_hf leverage) pending s2-B1 part 5 (its
fisher_kpp NN-floor finding is the conditioning evidence). Dispatching
s7_loss batch-1 websearcher + one stream-level scouting websearcher
(websearches/_scouting/).

## ADR 0005 carry-over PASS + s2-B1 initial analysis — 2026-07-29T17:26Z

Anchor carry-over: PASS (geomean delta 0.0137 << 0.884; all per-dataset deltas
inside floors). Hardware confound closed.

s2-B1 verdict (diagnostic, deterministic): H1 FALSIFIED (legs A+C fire, B+D
don't). Headlines: (1) M1 5/5x3/3 — champion NEVER sees LF at test time
(category error confirmed); (2) fisher_kpp = information deficit (X-only
family collapses to ~4.1-4.2; champion-best lookup delta 0.070 = 6x below
floor; nn_over_random 0.937 at cond_dim 2) — STRONG evidence for deferred
s8_data; (3) pfc: knn10 8.466 BEATS champion 11.511 by 3.045 (above 1.151
floor) — a training-free lookup beats the trained champion; (4) allen_cahn +
cahn_hilliard are TRAINING-WINS (unanticipated); (5) M3: excess error in the
LOWEST spectral band 5/5 (not high-k — D3 dead; s6_local brainstormer must
confront this: H2's high-k story is challenged); (6) M4: pfc error NOT
interface-concentrated (mid-distance peak — s3_warp brainstormer must
confront this); (7) M5a: helmholtz amplitude share 0.865 (6.202 → 0.839
rescaled!) — normalization is the helmholtz story (s5/s7 lead); (8) M5b:
pairing sound — §12.2 data-defect branch CLOSED. Stage →
mechanism_analysis_running; dispatching mechanism-analyzer (top probe: pfc
NN-distance stratification, heavy-tailed LOO residual 23x median/mean gap).

## Websearch return — s3_warp-B1 — 2026-07-29T17:27Z

SUCCESS (5 iterations, 9/9). Verdicts: D1 mf_warp_correct preempted-but-MF-
composition-open (Flowers 2603.04430 owns the warp primitive but no MF
correction; MetaRegNet owns warp+appearance; Khamlich 2603.04232 owns OT-for-
MF on Allen-Cahn 128->512 but classical/no-warp-of-LF) — claimable novelty
NARROW: neural cross-fidelity field-level warp at N_hf 5-25. D2 warp-oracle
diagnostic cheapest defensible card and GATES D1. NEW_MODELS §8.4 literal
claim survives; surrounding "documented gap" claim does not. Design-changing:
(1) LF error regime question (position vs interfacial-thickness — warp fixes
only the former); (2) warp-off control required (champion is LF-blind, so any
D1 win could be mere use-LF-at-test-time). Stage → brainstormer_running;
dispatching with s2-B1 cross-findings (M4 pfc error NOT interface-peaked; M3
low-band concentration) which the design must confront.

## Pulse — 2026-07-29T17:28Z

pulse: no-op (all 7 streams have an agent in flight: s1/s2 mechanism analysis,
s3_warp brainstormer, s4 builder (pinged), s5 initial analyzer, s6/s7
websearchers; plus scouting websearcher). No r1 SLURM jobs; nothing queued or
failed. All advancement happens on agent returns.
