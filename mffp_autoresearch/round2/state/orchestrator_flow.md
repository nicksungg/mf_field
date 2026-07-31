# Round-2 orchestrator decision log (append-only)

## 2026-07-31 — LAUNCH

- Launch authorized by Eloise ("launch round2 (use round1 results as
  guidance)", 2026-07-31). Round 1 CLOSED (report frozen).
- Between-rounds fixes landed in round2/eval (ADR r2-0001); floors frozen
  (G3-r2); gates G1-r2/G2-r2/G3-r2 all PASS (state/gates.md).
- Deviation from spec recorded: spec §5 claim "round-1 families cannot run
  at all on the stripped view" corrected — transfer-style families are
  condition→field at test; mf_fno_transfer_film reclassified as declared
  r2s3 baseline (program §3, §12.3; gates.md G1-r2 item 3).
- Round-1 top-3 seed confirms NOT launched (separately operator-gated;
  reported to Eloise as pending decision).
- Subagents installed (round-1 registry backed up to
  ~/.claude/agents.mffp-round1.bak). Outputs repo
  mffp_autoresearch_outputs/round2 on branch round2, pushed to origin.
- Dispatching batch-1 websearchers for all 4 streams in parallel
  (r2s2-B1 and r2s4-B1 pre-directed cores per program §12.2/§12.4).
- Orchestrator: THIS session. Crons: orchestrator pulse 10 min, maintainer
  20 min, auto-sync 30 min (ids recorded below once created).

- 2026-07-31 launch commit 9e10d41 (mffp-trunk-eloise, pushed); round2-substrate at 9e10d41.
- Batch-1 websearchers dispatched for all 4 streams (background).
- Crons live (session-only, 7-day auto-expiry — re-create on session restart per HOW_TO_LAUNCH §2):
  orchestrator pulse 03a7cf19 (every 10 min at :03), maintainer 60625c6e (every 20 min at :07),
  auto-sync 13995fd8 (every 30 min at :13/:43).

- 2026-07-31 ~15:0x r2s3 websearcher SUCCESS (4 iters, 8/8 checks): D3 (disjoint-condition LF
  exploitation + matched with/without-LF ablation) verdict NOVEL; D1/D2 preempted-but-MF-open.
  Key empirical: sharp ladders share x across rungs (LF = spectral truncation only);
  ifc_poisson has 170 disjoint LF conditions vs 5 HF. -> brainstormer dispatched.

- 2026-07-31 ~15:1x r2s1 websearcher SUCCESS: D1 (FiLM-decoder) and D2 (POD/RB trunk) PREEMPTED
  (baselines only); D3 (conditional-mean/identifiability certification) open. MAJOR: condition
  vector NOT complete on pfc/fisher_kpp/allen_cahn (random ICs only in fields) -> ADR r2-0003
  written; program §12.1/§13.1 corrected pre-first-card; mentor recommendation recorded in ADR.
- 2026-07-31 ~15:2x r2s2 websearcher SUCCESS: D1 stacked topology preempted (MF-DeepONet et al.);
  D2 open as ATTRIBUTION (emulator error vs distribution shift via frozen-finetuned delta);
  D3 intermediate-bottleneck preempted (arm only). Practical rule logged: fetch /abs not /pdf.
- Brainstormers dispatched for r2s1 + r2s2 (both told to honor ADR r2-0003).

- 2026-07-31 ~15:3x r2s4 websearcher SUCCESS (5 iters, cap): D1a seed-protocol PREEMPTED (adopt
  Agarwal et al. IQM/bootstrap + Du paired-delta; warning: conservative 3-seed protocols may
  declare nothing); D1b training-free floor panel open as composition; D2 value-of-LF open
  (Yang et al. NON-MONOTONE LUPI law: highly-predictive privileged LF may HURT the student —
  goes into r2s3/r2s4 falsification clauses); D3 open, low confidence. do-not-cite list in
  report.md. Websearcher's Write tool was rejected -> used Bash heredocs (infra note).
  -> brainstormer dispatched (told: fold or scope ADR r2-0003 conditional-mean floor).
- All 4 streams now at brainstormer stage.

- 2026-07-31 ~15:5x r2s4 brainstormer SUCCESS (12/12): B1 = diagnostic-with-training; floors
  reproduced from STRIPPED view (1e-9 seam) + LOO k-NN conditional-mean floor (ADR r2-0003
  folded in; k=1==NN, k=N==mean interpolant); minimal LF-free FiLM-FNO certifier (w32/2blk/
  16modes) seeds {0,1,2}; min_claimable_effect = max(spread, paired-bootstrap 95pct null);
  helmholtz report-only (provisional constant 10.68 > entire best floor 3.34 — a finding).
  ORCHESTRATOR OWES: install noise_floor_candidate.json over state/noise_floor.json at
  analysis time; seed jobs at 04:00:00 default. -> starter dispatched.

- 2026-07-31 ~16:0x r2s2 brainstormer SUCCESS (11/11): B1 model card = FiLM-FNO NATIVE-GRID
  pseudo-LF emulator (one emulator shared across arms) -> vendored dc_cleaned corrector;
  arms decompose emulator error / distribution shift / cond-mean barrier; NEW A5 condmean_lf
  control (train-mean LF into frozen corrector) makes ADR r2-0003 measurable; falsification
  hangs on cahn_hilliard (only identifiable sharp dataset). ROUND-WIDE RESTATEMENT: r1
  dc_cleaned = 0.3306 corrected geomean (was 0.1232 under old refs) = real-LF oracle ceiling,
  69.8x better than launch anchor. Tripwire R2S2_REQUIRE_PSEUDO_LF=1; guard run = separate
  score_panel invocation. -> starter dispatched.

- 2026-07-31 ~16:1x r2s3 brainstormer SUCCESS (14/14): B1 model card = condition->HF FiLM-FNO
  forward(cond,out_hw), supervised at every rung's NATIVE resolution; matched no-LF control +
  upsample control. Verified: sharp/helmholtz x arrays bit-identical across rungs (LF adds 0
  param coverage on 5/6 panel); ifc_poisson rungs pairwise DISJOINT (100/50/20/5) -> teacher
  distillation D1 killed (untrainable where it helps). Baseline restated: transfer_film
  corrected geomean 19.0433 (beats 23.06 anchor). Rebadge hazard vs mf_fno_ladder_gain
  defused on 4 code axes. F1/F2 ifc_poisson threshold 0.2399 (predicted ~42x); F3 null
  pre-registered on aligned datasets. -> starter dispatched.

- 2026-07-31 ~16:3x r2s2 starter SUCCESS: B1.json drafted (no TBDs; recipe verbatim incl 39 env
  entries + _arms directives; prior_art verdict transcribed unnormalized as
  preempted-but-MF-composition-open). -> builder dispatched.

- 2026-07-31 ~16:4x r2s4 starter SUCCESS: B1.json drafted (diagnostic WITH training per §12.4,
  seeds [0,1,2], epochs 200; base_commit == round2-substrate verified; per-row prior-art
  verdicts preserved verbatim). -> builder dispatched.

- 2026-07-31 ~16:5x r2s1 brainstormer SUCCESS (12/12): B1 model card = amplitude(log||y||)/
  direction split decoder + OOF blend onto best floor + training-free identifiability
  certificate; prior_art verdict preempted-pivoted (D1 baseline, D2 control-with-predicted-
  failure, D3 scored). ADR r2-0003 REFINED: allen_cahn rising profile => maybe deterministic-
  undersampled (addendum appended); helmholtz cv(||y||)=12.27 explains r1 scaler failures;
  helmholtz report-only. Builder constraint: extra arms named ref_*/cert_*, never test*.
  -> starter dispatched.

- 2026-07-31 ~17:0x r2s3 starter SUCCESS (13/13): B1.json drafted, no TBDs; recipe env mixes 6
  real knobs + underscore card directives (not passed to --env, per brainstormer note).
  -> builder dispatched.

- 2026-07-31 ~17:1x r2s1 starter SUCCESS (20/20): B1.json drafted, verbatim-verified; _-prefixed
  env directives must be filtered by builder before score_panel. -> builder dispatched.
  ALL FOUR STREAMS NOW AT BUILD STAGE.

- 2026-07-31 ~17:4x r2s4 builder SUCCESS (10/10): build 870b62b; contract smoke exit 0
  (helmholtz e2 nRMSE 2.589); floors reproduce rel-diff 0.0; SIGKILL resume at epoch 90
  verified; scripts incl. 03_certify.sh (ORCHESTRATOR runs post-3-seeds, then installs
  noise_floor_candidate.json over state/noise_floor.json). -> code-reviewer dispatched.

- 2026-07-31 ~18:1x r2s4 code-reviewer SUGGEST (6/6): non-blocking findings (record eta_min etc.
  in part 5; submit via wrappers only; certify must read results ONLY from outputs_root eval/,
  never the committed synthetic scratchpad files). ORCHESTRATOR SUBMITTED seeds 0+1+2 (card's
  §12.4 pre-directed 3-seed protocol; deep build verification justified parallel submit):
  jobs 66161480/66161481/66161482, 04:00:00, first r2 SLURM jobs. Card -> running.
  On completion: initial-analyzer, then orchestrator runs scripts/03_certify.sh and installs
  noise_floor_candidate.json over state/noise_floor.json.

- 2026-07-31 ~18:4x r2s1 builder SUCCESS (12/12): build 0af8b38; contract smoke exit 0
  (helmholtz e2 nRMSE 0.930 — amplitude head already below zero floor at 2 epochs);
  floors seam 0.0 on 9/9; resume verified both branches; leakage tripwire asserts
  stripped view. One TBD (denominator floor p25 vs median knob-selectable); one
  documented deviation (closest-pair D3 certificate fit) -> reviewer told to judge it.
  -> code-reviewer dispatched.

- 2026-07-31 09:13 PDT: maintainer flagged r2s2 builder-card lag; orchestrator verified worktree
  mtimes — builder ACTIVE (dbg2.log/smoke_eval.py modified <1 min ago, iterating contract
  smoke on the 5-arm stack). Not stalled; no intervention. r2s4 jobs still PENDING in queue.

- 2026-07-31 ~09:4x PDT r2s1 code-reviewer SUGGEST (6/6, 8 PASS findings): certificate deviation
  judged sound/disclosed/non-biasing but NOT converged (helmholtz cert window-sensitive
  0.000->2.013 across windows; report-only, regenerates offline — analysis-time caveat for the
  initial-analyzer: quote allen_cahn aleatoric as a RANGE, distrust helmholtz cert). p25 TBD
  inert. ORCHESTRATOR SUBMITTED seed 0: job 66163572 (strict 1-seed). Card -> running.

- 2026-07-31 ~09:5x PDT pulse: 4 r2 jobs PENDING (Priority) on h100 gres; p100/h200 idle but
  NOT switching tier (single-hardware-tier comparability, r1 H100 envelope finding / ADR 0005).
  Patience over churn; revisit only if still pending in ~2h.

- 2026-07-31 ~10:2x PDT r2s3 builder SUCCESS (10/10): build 0acc7cf; contract smoke exit 0;
  ifc_poisson contract-tier arms hf_only 0.419 vs rung_native 17.49 (single-scaler confound
  at 2 epochs — card-specified, watch item); SIGKILL mid-stage resume verified.
  -> code-reviewer dispatched with 3 watch items.

- 2026-07-31 ~10:4x PDT r2s2 builder SUCCESS (14/14): build 6b4e1d4; all 5 arms + gates V1-V7
  green; resume verified. DISCLOSED: ifc_poisson ladder UNPAIRED (min cond distance 0.08-0.30
  every rung; matches r2s3's independent disjoint-rungs finding) -> A2/A5 degraded with
  arm_semantics_degraded=true + V6b gate, no silent mispairing. NOTE cross-stream: this also
  means round-1 copylf lf[:n_hf] truncation semantics on ifc train were never valid pairs —
  benchmark-integrity item for the round report. -> code-reviewer dispatched.

- 2026-07-31 ~11:0x PDT HARDWARE TIER SWITCH (ADR r2-0004): h100 queue estimated 2026-08-07
  (169 backlog) while 3 h200 nodes idle; scontrol update Gres -> nvidia_h200 on all 4 pending
  jobs (zero results existed -> uniform tier preserved); ALL 4 STARTED WITHIN MINUTES
  (r2s4 s0/s1/s2 on hpc-sm-01-04, r2s1 s0 on hpc-sm-01-15). project.yaml gres updated with
  ADR pointer. All future submissions: SBATCH_GRES=gpu:nvidia_h200:1.
- 2026-07-31 ~11:0x PDT r2s3 code-reviewer SUGGEST (6/6): faithful build; card-internal
  shared-scaler confound travels as interpretation constraint (rung-8 scaler 42x vs hf_only;
  null F1 on ifc_poisson NOT evidence LF adds nothing; B2 = per-rung scaler variant);
  eta_min undeclared (build_notes fix); F1 epoch- but not step-matched (2nd confound).
  ORCHESTRATOR SUBMITTED seed 0: job 66165379 (h200, verified TresPerNode). Card -> running.

- 2026-07-31 ~11:3x PDT r2s4-B1 ALL 3 SEEDS COMPLETED (66161480/81/82, h200). Orchestrator ran
  03_certify.sh: certified MCEs 10-1700x tighter than provisional (helmholtz 2.95, ifc 0.94,
  allen_cahn 0.88, ch 0.091, fisher 0.0007, pfc 0.213); certifier IQM geomean ~19.9 beats the
  23.06 floor anchor; F1/F2 not fired, F3 pass. noise_floor_candidate INSTALLED over
  state/noise_floor.json (provisional backed up as .bak; sanity-checked non-synthetic).
  -> initial-analyzer dispatched (3-seed).

- 2026-07-31 ~11:5x PDT r2s1-B1 seed 0 COMPLETED (66163572, h200). -> initial-analyzer
  dispatched (judge pre-registered clauses as written vs provisional floor; also report
  deltas vs the newly certified floor; certificate caveats forwarded).

- 2026-07-31 ~12:1x PDT r2s2 code-reviewer SUGGEST (6/6): ifc unpaired-ladder deviation
  independently REPRODUCED (0.08-0.30 every rung; agrees with r2s3 websearcher — established
  finding). Analyzer-facing: A2-A3 is an UPPER BOUND on shift (not epoch-matched); "identically
  zero" code string false at smoke tier (fix next build); panel JSON carries no degradation
  flag -> analyzer must open diag_ifc_poisson. ORCHESTRATOR SUBMITTED seed 0 panel 66166237 +
  guard 66166238 (h200). Card -> running. BATCH-1 WAVE FULLY SUBMITTED (all 4 streams).

- 2026-07-31 ~12:2x PDT r2s1-B1 initial-analyzer SUCCESS: geomean 19.6444 (provisional-single-
  seed) vs anchor 23.0636 (-14.8%, resolvable vs certified panel mce 1.1419); floors beaten
  resolvably on pfc/allen_cahn/fisher/ch; falsification LEG 1 FIRED by 0.0444 (3.9% of mce —
  inside seed noise, caveat recorded); guard heat_local flag fired (6.24x copylf; beats NN
  floor; noted not auto-reject). Leads: ref_pod_lin BEATS scored arm on allen_cahn; best_epoch
  2-24/200 overfit; wall clock 6.95 min vs 4h request (timing ledger). -> mechanism-analyzer.

- 2026-07-31 ~12:5x PDT r2s4-B1 initial-analyzer SUCCESS (10/10, 3-seed): geomean 19.8178
  [19.3853, 20.5271] CONFIRMED (F1 1/5, F2 1/6, F3 pass 9/9 floors exact); stream anchor
  UPDATED 23.0636 -> 19.8178 (supersedes block preserved). Guard flags heat_local 16x /
  sod_1d 2.1x recorded as regime artefacts (no auto-reject). Certified constants are RERUN
  spreads; 3 seeds can't push sign-flip p < 0.25. k*-NN cond-mean floor beats frozen best
  floor 5/6 (ADR r2-0003 evidence). -> mechanism-analyzer dispatched.

- 2026-07-31 ~13:1x PDT r2s1-B1 mechanism turn 1 (6/6): ROUND-DEFINING — condition determines
  only 1-3 field DOF per dataset (OOF R2>0.1 modes: 5/2/1/1/3/1); decoder INFORMATION-limited
  not representation-limited; two regimes (coefficient-unidentifiable: helmholtz/pfc/ch/ifc,
  1-2 decade oracle gap = missing info; basis-inadequate: allen_cahn/fisher). allen_cahn's
  learnable map = ONE scalar (mode-1 R2 0.979); 16M-param decoder overfits rediscovering it;
  lambda blend repairs decoder damage. Lanthaler POD-failure prediction fired only on SMOOTH
  helmholtz (408x ||y|| spread — amplitude effect). -> turn 2 dispatched (H1 closed-form head
  vs H2 lambda predictor).

- 2026-07-31 ~13:4x PDT r2s2-B1 panel job COMPLETED (66166237; guard 66166238 completed
  earlier). -> initial-analyzer dispatched (unpaired-ifc + A2-A3 upper-bound caveats
  forwarded; oracle ceiling 0.3306 context).

- 2026-07-31 ~14:1x PDT r2s1-B1 mechanism turn 2 (7/7): 156-param closed-form head geomean
  19.0553 vs shipped 15.9M-param 19.6444 — delta 0.59 = 0.52x mce -> capacity buys nothing
  measurable (1e5 compression); tiny head's edge is allen_cahn alone (LODO sign-flip);
  amplitude head = re-centering effect (helmholtz 3.82x from geometric centering, ratio
  ||mean||/geomean||y|| orders it); falsification leg-1 verdict noise-decided (tiny head
  under identical protocol would NOT have fired). -> turn 3 dispatched (pfc phase DOF).

- 2026-07-31 ~14:3x PDT r2s2-B1 initial-analyzer SUCCESS (6/6): geomean 14.0756 single-seed BUT
  artifact of degraded ifc column — on 5 paired datasets frozen 19.1843 vs emul_only 19.1863
  (delta 0.002, 15x below floor): STACKING ADDS NOTHING beyond the emulator at seed 0; S2:
  corrector+real-LF near-perfect vs pseudo-LF 0.24-0.46 -> all stack error is emulator error.
  Falsification 'confirmed' only via AND-clause semantics (sub-test failed resolvably —
  brainstormer B2 should re-clause). CALM-PDE e2e prediction inverted on panel, held on guard.
  Guards all improve (no flags). -> mechanism-analyzer dispatched.

- 2026-07-31 ~15:0x PDT r2s2-B1 mechanism turn 1 (5/5): emulator NEVER FIT cond->LF on 5/6
  panel (in-sample==held-out); closed-form ridge matches/beats it (ifc: ridge EXACT 0.0000 —
  LF affine in condition); emulator IS the linear law on ADR r2-0003 datasets; spectral
  signature hard low-pass with band-1 null INSIDE mode budget -> I2 architectural hypothesis
  (coords-only FNO + spatially-constant FiLM = global-rescale-of-fixed-patterns class);
  cahn_hilliard the ONLY genuine info ceiling (I3). Guard inversion explained (pseudo-LF
  accurate there). -> turn 2 dispatched (test I2 reachable set).

- 2026-07-31 ~15:2x PDT r2s3-B1 seed 0 COMPLETED (66165379, ~1h13m, all legs). Mid-run signal:
  rung_native WORSE than hf_only on ifc_poisson by 7.35 skill units (inversion of predicted
  +10; reviewer's shared-scaler confound the prime suspect). LAST BATCH-1 JOB DONE.
  -> initial-analyzer dispatched with confound caveats.

- 2026-07-31 ~15:5x PDT r2s3-B1 initial-analyzer SUCCESS (6/6): CRATERED + FALSIFIED (F1
  sign-inverted, -7.35 units on ifc, 7.8x certified floor; C2 confound ran IN FAVOR of the
  losing arm). F2 survives vs diverged comparator (rung_upsampled test 23.3 vs train 0.23).
  F3 threshold-dependent (provisional 1/5 vs certified 3/5 — both recorded). Declared
  baseline transfer_film ifc skill 1.5455 (best r2 ifc number; per-stage scalers decisive
  suspect). Wall 77 min. Anchor untouched. -> mechanism-analyzer dispatched. NOTE for B2
  brainstormer: per-rung scaler variant is the obvious follow-up; batch-2 planning begins
  when this card completes.

- 2026-07-31 ~15:2x PDT maintainer flags: (1) ahead-of-clock self-declared header timestamps in
  two subagent handoffs (code-reviewer r2s1, mechanism-analyzer r2s4) — systemic cosmetic
  issue, note for round report; (2) r2s4 mechanism handoff claims parts 6/7 + tool promotions
  not yet on disk (7_gap_and_future null; tools not in index) — agent has NOT returned yet,
  ORCHESTRATOR OWES verification of part 7 + tools/index.md on its completion notification
  before advancing r2s4 to complete.

- 2026-07-31 ~16:1x PDT r2s4-B1 COMPLETE (first terminal card; mechanism turns 1-3 + register
  in one invocation, 9/9; disk-verified parts 6/7 + 2 tools promoted+indexed). ROUND-REPORT
  finding: criterion 2 (skill<1) EXCLUDED by information argument on fisher_kpp (barrier
  ~11.44), pfc (~38.6-42.1), allen_cahn (~132.7) for ANY condition->HF model; certifier is
  1.01-1.14x the barrier on those (nearly optimal) and 1.655x on helmholtz (fixable);
  noise-floor constants are a LOWER bound for less-collapsed successors — B2 should
  re-certify on the compared arm. -> B2 websearcher dispatched (batch counter -> 2).

- 2026-07-31 ~16:3x PDT r2s3-B1 mechanism turn 1 (5/5): C1 does NOT explain inversion (LF arms
  3.8x structurally worse after per-sample gain oracle — genuine negative transfer); ifc is
  the ONLY mesh-scaled ladder (p=+2.09; shared-scaler deflation 1772x; all other datasets
  inflation 1.000); rung_upsampled "divergence" = ONE amplitude scalar (23.31 -> 0.564 with
  global gain; never overfit). F2's credit = amplitude switch, no structural info. -> turn 2
  dispatched (spectral attribution + LF-info-after-n^2 test; r2s2's ifc-affine finding
  cross-referenced).
