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

- 2026-07-31 ~17:0x PDT r2s1-B1 mechanism turn 3 (5/5): H3 FALSIFIED — no phase/registration
  DOF anywhere (ring phase cos ~0 all arms); pfc win = 100x amplitude shrinkage of the
  unpredictable ring; 6 fitted band gains close tiny-head deficit to 0.06%; pfc "is two
  datasets" (44/100 patterned, class OOF AUC 0.9998 from 2-dim condition; scoreable content
  = spatial mean, DC OOF R2 0.9997; 35-param DC-only arm 0.3502 beats shipped 0.3840).
  ch's +4.6% = only surviving capacity claim. -> register turn dispatched (3 tool promotions,
  name-collision warning given).

- 2026-07-31 ~17:2x PDT r2s4-B2 websearcher SUCCESS (7/7, cap hit): D2 CORRECTION — B1's
  ceiling estimators are published objects (differogram + difference-based variance class;
  19-dim no-support is theorem-level; N_hf=5 ceiling claims indefensible per 2410.23440);
  D1 value-of-LF open as composition (DOPD privilege-illusion advantage-gap ablation +
  pre-registered nulls from training-free ceiling); D3 sell lambda* diagnostic (James-Stein;
  FALCON warns few-point calibration needs UQ); no PDE n_eff estimator exists (define
  locally). -> B2 brainstormer dispatched.

- 2026-07-31 ~17:5x PDT r2s3-B1 mechanism turn 2 (6/6): ROUND HEADLINE — ifc_poisson EXACTLY
  affine in condition (3.2e-08 at every rung + test HF); 5 HF rows rank-deficient by ONE
  affine direction (18.83% of law energy); LF rungs transfer slope fields at cos 0.9995;
  linear probe (rung-32 affine + 1 scalar + 5-row residual) reaches SKILL 0.2427 vs shipped
  16.80 — value-of-LF = +3.23 units = 13.5x floor, in the ARCHITECTURE-not-information
  direction. B1 family failure = mode clipping + 1772x loss deflation (per-rung scaler
  necessary but plausibly insufficient; pin mode clipping at HF Nyquist). BENCHMARK-INTEGRITY:
  ifc criterion-2 claims measure rank recovery, not operator learning (report §5 item).
  -> turn 3 dispatched.

- 2026-07-31 ~18:2x PDT r2s2-B1 mechanism turn 2 (6/6): I2 FALSIFIED in strong form — emulator
  emits rank-22 (cahn_hilliard) / rank-6 (fluid) matching truth rank; rank-1 collapse on
  pfc/allen_cahn/fisher = TRAINED response to unlearnable targets (nn band>=1 cosine ~0 —
  pattern not a function of X; emulator within 0.002 of its oracle rank-1 bound there).
  Three-way ceiling taxonomy: structural (pfc/ac/fk) / sampling (ch, 3.91 sd nn distance) /
  learning (helmholtz continuous but FiLM code collapsed; ifc affine reachable 6.2e-08).
  -> turn 3 dispatched (part 6 + postmortem).

- 2026-07-31 ~18:5x PDT r2s4-B2 brainstormer SUCCESS (10/10): diagnostic-with-training =
  DOPD advantage-gap value-of-LF (transfer leg cond-only test; information leg on inner
  train fold where LF legal — positive control via ADR r2-0003; capability leg free) +
  N_fit sweep {20,80,320}; LF pinned to copy-LF's own rung/convention; thresholds
  max(certified mce, in-job paired spread); seeds [0,1,2]; ceiling work deliberately NOT
  attempted (D2 verdict binding). Honest prediction: claimable transfer on 1-2 datasets
  (criterion-1 adjudication reserved). -> starter dispatched.

- 2026-07-31 ~19:1x PDT r2s1-B1 COMPLETE (register 6/6; disk-verified part 7 + 2 tools
  promoted/indexed; capacity-audit tool deliberately NOT promoted — family-coupled).
  Register-turn bonus measurement: full 31-gain calibration on ch in 75.5s -> decoder
  advantage narrowed to 4.29% but = 6.0x certified mce (REAL candidate; B2's question).
  next_direction: spend on identification/calibration not capacity; DC-only arm mandatory
  floor. Cross-stream: identifiable-rank convergence 1/1/1 pfc-ac-fk, 3 ch across three
  independent probes. -> B2 websearcher dispatched (batch counter -> 2).

- 2026-07-31 ~19:3x PDT r2s3-B1 mechanism turn 3 (8/8): LF gain does NOT survive the network
  channel (inverts to -6.12 under identical repairs; architecture tax 60x with-LF, 2.72x
  no-LF); inductive-bias finding: net puts 27.7% of affine-law energy ANTI-ALIGNED in the
  unconstrained direction (min-norm linear puts 0); H7 low-pass repair minor (+1.6 of 7.35);
  rung_upsampled = pointwise memorisation, train-row diagnostics blind to it. Postmortem:
  F1 falsified-as-architecture / confirmed-as-information. -> register turn dispatched
  (overlap check vs r2s1's condition_identifiable_rank tool flagged).

- 2026-07-31 ~19:5x PDT r2s4-B2 starter SUCCESS (13/13): B2.json drafted, no TBDs; 3-seed
  §12.4 exception flagged for reviewer adjudication. -> builder dispatched.

- 2026-07-31 ~20:2x PDT r2s1-B2 websearcher SUCCESS (9/9, cap hit): E1 band-gain calibration =
  non-causal WIENER FILTER (preempted; B1's gain collapse = Self-Wiener low-SNR thresholding);
  E2/E3 preempted-but-open (E3 = closed-form-control protocol, best contribution shape);
  E4 provisional; predictable-rank truncation = presumed prior art (do not claim).
  -> B2 brainstormer dispatched.

- 2026-07-31 ~21:0x PDT r2s1-B2 brainstormer SUCCESS (10/10): model card = closed-form spectral
  head selected by pre-registered training-free rule vs 4-point capacity ladder, ALL arms
  under same OOF Wiener calibration + floor blend; per-dataset falsification legs (no panel-
  geomean leg — B1 showed it noise-decided); ch decision leg at 3x mce; seeds [0] correct;
  helmholtz report-only. -> starter dispatched.

- 2026-07-31 ~21:2x PDT r2s3-B1 COMPLETE (register 5/5; disk-verified; 2 tools promoted with
  explicit non-overlap documentation vs r2s1's; honesty item: +3.23 gain clears BOTH the
  provisional (13.5x) and certified (3.45x) floors). Third card closed. B2 direction from
  part 7: linear/affine channel as contract family (0.2427 existence proof) vs network trio
  (per-rung scaler + HF-Nyquist mode pinning + null-direction regularization).
  -> B2 websearcher dispatched (batch counter -> 2).

- 2026-07-31 ~21:4x PDT r2s1-B2 starter SUCCESS (28/28): B2.json drafted, no TBDs; 54 env keys
  (5 _-prefixed directives to filter); E4 citation honestly marked SEARCH-RETURN ONLY.
  -> builder dispatched.

- 2026-07-31 ~22:0x PDT r2s3-B2 websearcher SUCCESS (9/9, cap hit): E1 linear channel PREEMPTED
  (Willcox 2508.08517 projection-based MF linear regression w/ disjoint-condition LF + HF-only
  baseline) -> declared baseline only; E2 supersedes B1's D3 novel verdict (retain-plus-
  transfer); E3b Nyquist pinning = bug fix; E5 matched ±LF neural contrast at N_hf~5 vs
  certified floor = NOVEL (the stream's remaining claim). Honesty: ifc-affine = standard RB
  knowledge (integrity statement not discovery); architecture tax must cite 2209.15265.
  -> B2 brainstormer dispatched WITH r2s4-B2 turf boundary (accounting vs optimizing).

- 2026-07-31 ~23:0x PDT r2s2-B1 mechanism turn 3 (6/6): corrector value governed by input
  REALISATION COHERENCE (32-100% reduction at gamma~1.0 -> <=0.08% at gamma<=0.52; correction
  rotates orthogonal to residual); even ORACLE Wiener on this pseudo-LF < the clause's 2.0
  bar on ch; I8 STRUCTURAL: deterministic pseudo-LF = re-parameterisation, not information
  channel — the stack cannot leave the condition->HF class. I2->I2' correction + three-way
  taxonomy in part 6. 1-CPU cgroup disclosure noted. -> register turn dispatched (triad
  tool-relationship documentation requested).

- 2026-07-31 ~23:2x PDT r2s3-B2 brainstormer SUCCESS (12/12): model card = r2s3_null_supply
  (per-rung scalers + Nyquist-pinned modes + null-direction paired-difference penalty from
  LF rungs); step/normalization-matched ±LF at N_hf=5 on ifc (m=1) / ch (m=15, 3 HF draws) /
  fisher (m=0 structural null control); E1 linear channel as cited reference arm only;
  turf with r2s4-B2 explicitly partitioned (paired full-N vs disjoint-condition N_hf=5).
  -> starter dispatched.

- 2026-07-31 ~23:4x PDT r2s3-B2 starter SUCCESS (12/12): B2.json drafted, verdict novel (E5);
  17-leg matrix; env-key count discrepancy (note says 25, lists 30) transcribed verbatim +
  flagged -> builder told: 30 listed keys authoritative. -> builder dispatched.

- 2026-07-31 ~20:4x PDT r2s4-B2 builder SUCCESS (14/14): build a1f3da4; smoke exit 0
  (helmholtz e2 2.007); floors reproduce exactly on 4 extra datasets incl. ifc 22-leg LOO
  path; builder FOUND+FIXED resume summary bug via its own all-legs-complete test; 3-seed
  scope flagged for reviewer adjudication. -> code-reviewer dispatched.

- 2026-07-31 ~21:1x PDT r2s2-B1 COMPLETE (register 5/5; disk-verified; 2 tools promoted with
  triad table — field-basis/condition-side/model-output axes). BATCH 1 FULLY CLOSED: 4/4
  cards complete (2 confirmed incl. 1 certified-3-seed; 1 falsified-with-caveat; 1 cratered-
  but-informative). B2 fork for brainstormer: A) realisation-aware emulator on ch (~1.6 skill
  units max, pre-registered in gamma units) vs B) pivot to helmholtz/ifc learning-failure
  gaps (would be a condition->HF card — near r2s1 turf). -> B2 websearcher dispatched
  (batch counter -> 2).

- 2026-07-31 ~21:5x PDT r2s2-B2 websearcher SUCCESS (8/9, honest summary-length deviation):
  D1 realisation-aware open but predicted negative x3; D2a thin-novel; D2b preempted-baseline
  (Hesthaven-Ubbiali); D3 coherence-threshold CALIBRATION open (FreqNO-DPS ships the check,
  nobody calibrates it); D4 I8-closure preempted-as-principle (data-processing inequality),
  open as measurement. STANDING PROCESS RULE (2nd occurrence): arXiv /pdf/ fetches fabricate
  content — always /abs/ or /html/ (added to future websearcher dispatch prompts).
  -> B2 brainstormer dispatched with fork A/B/calibration/skip options.

- 2026-07-31 ~22:3x PDT r2s2-B2 brainstormer SUCCESS (12/12): diagnostic card
  r2s2_correctability — two training-free intermediate ladders (oracle spectral mix +
  test-legal kNN-LF ladder) with DC corrector refit per rung at matched steps; calibrates
  the coherence threshold (M1), nonlinear stress test (M1c), DPI closure w/ permutation
  null (M2), settles option A test-side (M3). Rejected: A-generative (§5.9 logic), B
  (r2s1-B2 duplication), skip (uncalibrated export is worst outcome). -> starter dispatched.

- 2026-07-31 ~22:5x PDT r2s2-B2 starter SUCCESS (14/14): B2.json drafted, no TBDs; guard leg
  separate invocation per _note. ALL FOUR B2 SLOTS NOW DRAFTED+IN PIPELINE. -> builder
  dispatched.

- 2026-07-31 ~23:1x PDT r2s4-B2 code-reviewer SUGGEST (6/6): 3-seed ADMISSIBLE (§12.4 + B1
  part-7 directive + operative-threshold column); reviewer recommends NORMAL SEED-0 GATE
  (unlike B1's parallel submit) — honored. Analyzer obligations: config-table additions
  (WORK_CAP, transductive P_bar, 2 inert knobs); fold-fixed spread must NOT overwrite
  state/noise_floor.json without label; read only outputs eval/ (dbg_* are 2-epoch).
  ORCHESTRATOR SUBMITTED seed 0: job 66181609 (h200). Card -> running.

- 2026-07-31 ~23:5x PDT r2s4-B2 seed 0 COMPLETED (66181609, 17:15, exit 0:0, geomean 19.2799
  finite on 6/6). Seed-0 gate passed -> seeds 1-2 submitted: 66182923/66182924 (h200).
  Initial-analyzer dispatches after all three (card needs the 3-seed paired spread).

- 2026-08-01 ~00:1x PDT r2s4-B2 ALL SEEDS COMPLETED (~17 min each, h200). Orchestrator ran
  03_accounting.sh: T0 3-seed geomean 19.8829 (matches B1 certifier band); T1-T0 transfer
  deltas below MCE on all datasets (predicted value-of-LF NULL with sensitivity-proven
  instrument); F3_scaling FIRED, F1/F2/F4 not. -> initial-analyzer dispatched (fold-fixed
  spread labeling obligation forwarded).

- 2026-08-01 ~00:4x PDT r2s4-B2 initial-analyzer SUCCESS (6/6, 3-seed): CRITERION-1 MEASUREMENT
  LANDED — 0/6 claimable transfer effects (value-of-LF null at every N) vs instrument with
  claimable information gap 5/5 (ratios 13.5-95.3x) => interpretable null; F3 fired on a
  null (not resolved opposite effect — honestly recorded); T0 reproduces B1 certifier
  bit-identically on ifc (instrument validation); fold-fixed spread NOT installed (labeled);
  2 part-4 predictions not borne out (ch info gap 39.55 vs predicted 1.2-3). -> mechanism-
  analyzer dispatched (4 leads incl. I-vs-T dissociation vs r2s3's linear-channel success).

- 2026-08-01 ~01:0x PDT r2s3-B2 builder SUCCESS (10/10): build 945ee65; smoke exit 0 (ifc e2
  0.3013); resume bit-identical; m/alpha match pre-registered values; vendored lift agrees
  0.0; estimators reproduce B1 digits (3.4744/0.2427/0.18828). Builder caught --env nargs
  footgun (multi-flag silently discards). -> code-reviewer dispatched.

- 2026-08-01 ~01:3x PDT r2s3-B2 code-reviewer SUGGEST (6/6): all findings analyst-facing
  (quote per_rung 32 not ref_linear_mf; 0.551 amplitude gain = first suspect on null;
  F2 instrument-not-capacity contrast; TIMEOUT = resubmit not ALGO). ORCHESTRATOR SUBMITTED
  seed 0: job 66185845 (h200, 17 serial legs). Card -> running.

- 2026-08-01 ~02:0x PDT r2s2-B2 builder SUCCESS (10/10): build bd54bcb; smoke exit 0 (9 splits);
  floor/upsampler/ladder-identity seams all 0.0; one TBD (k* statistic = argmin raw calib
  nRMSE, alternative recorded); F1 oracle-ceiling-negative semantics flagged; free corrector-
  fit-noise estimate via ladder identity. -> code-reviewer dispatched.

- 2026-08-01 ~02:3x PDT r2s4-B2 mechanism turn 1 (6/6): I-vs-T dissociation EXPLAINED — aux-LF
  target exactly as condition-unidentifiable as HF on 4/5 (aux head duplicates main task;
  the certified "information gap" is an INPUT statement, transfer null a TARGET statement —
  different channels); helmholtz lone harmful exception; ch miss = support failure (d_min
  3.12 in 19d) vs fisher = aleatoric (two mechanisms one null); STRUCTURAL: lf[:n_hf] gave
  aux head 5/170 ifc rows -> could not reach r2s3's win by construction. Fast float32
  ceiling-tool variant staged for register promotion. -> turn 2 dispatched (helmholtz sign
  flip; cross-ref r2s3-B2 as the direct null-supply test).

- 2026-08-01 ~02:5x PDT r2s2-B2 code-reviewer SUGGEST (6/6): F1 survives oracle-negative
  semantics via its max(3xspread,0.05) margin (analyzer must substitute M1b spread + say so);
  k* selection-variance risk (helmholtz argmin picked k=1, 52% worse than k=all on test —
  report k* stability across fold seeds); A:1≡B:1 gap = init-variance LOWER bound only.
  ORCHESTRATOR SUBMITTED seed 0 panel 66187052 (walltime raised 2h->3h30 per reviewer
  finding 5) + guard 66187053 (h200). Card -> running.

- 2026-08-01 ~03:1x PDT r2s1-B2 builder SUCCESS (10/10, longest build ~10.1M tokens/2.8h):
  build d844bec; smoke exit 0 (helmholtz e2 0.9327); resume both branches bit-identical;
  3 speedups verified to 1 ulp (540s->80s); TBD: rank-statistic shipped affine+LOO with
  r_sel divergence from tool baseline (reviewer to adjudicate L4 decidability); est 30-45
  min runtime. LAST B2 BUILD DONE — all four batch-2 cards now built. -> code-reviewer
  dispatched.

- 2026-08-01 ~04:0x PDT r2s4-B2 mechanism turn 2 (6/6): helmholtz sign flip = unlearnable aux
  gradient confined to fluctuation channel (60.3% of irreducible loss, 10.56x upweighted by
  separate LF scaler; trunk UNDAMAGED — own-mean broadcast equal-or-better); helmholtz seed
  spread 24.9x METRIC ARTIFACT (mean-of-ratios vs energy-pooled; no arm contrast decidable
  there at 3 seeds); ifc I-leg VOID (lf[:n_hf] mispairing, 0/5 nearest — why I2/I1=0.905).
  -> turn 3 dispatched (N-scaling law + part 6).

- 2026-08-01 ~04:2x PDT r2s3-B2 seed 0 COMPLETED (66185845, ~45 min, 17 legs). -> initial-
  analyzer dispatched (reviewer carry-forwards + r2s4-B2 cross-stream context forwarded).

- 2026-08-01 ~05:0x PDT r2s4-B2 mechanism turn 3 (6/6): 4/5 datasets AT N->inf ASYMPTOTE at
  N=320 (ch the only sample-limited, slope 0.233 accelerating); lambda*(N) crosses 1 on ch
  (0.767->1.117: over-amplified starved, over-smoothed fed) — the §12.4 overfitting anatomy;
  F3 = certified null on sensitive instrument (N-effects resolved 7.4-101x floor while all
  15 transfer cells below); support-not-identifiability predicts regime 5/5 training-free.
  LICENSED: aux-LF-TARGET head worth nothing at any N (certified). NOT licensed: "LF doesn't
  help" (input-side + disjoint-supply channels untouched — r2s3-B2 running the latter).
  -> register turn dispatched (3 promotions incl. pair-alignment pre-flight).

- 2026-08-01 ~05:2x PDT r2s3-B2 initial-analyzer SUCCESS (6/6): F1 CONFIRMED SIGN-FLIPPED —
  A0-A2 = +4.6794 on ifc (4.99x certified floor; B1 was -7.35): NEURAL CHANNEL CAN CONSUME
  DISJOINT-CONDITION LF. Twist: A1 (no null penalty) BEATS primary A2 (penalty hurts, 1.37x
  floor); fisher_kpp +1.22 resolvable DESPITE m=0 (contradicts pre-registered null; coverage
  as condition-completion?); ch A3_paired worse than no-LF (coverage not curriculum).
  F5 wording-ambiguous on fisher (both readings recorded). Answers r2s4-B2's open question.
  Wall 41.6 min. -> mechanism-analyzer dispatched.

- 2026-08-01 ~05:4x PDT r2s2-B2 panel job COMPLETED (66187052, 33:35, exit 0:0; guard done
  earlier). ALL FOUR B2 SLURM RUNS COMPLETE. -> initial-analyzer dispatched (oracle-negative
  F1 semantics + k*-stability + init-variance-bound carry-forwards).

- 2026-08-01 ~06:0x PDT r2s3-B2 mechanism turn 1 (8/8): null penalty aimed RIGHT (cos 0.98-
  0.99) but amplitude 1.72-1.79x too large — exactly the reported-not-applied 0.551 gain;
  A1 had already recovered the direction to 1.8% -> penalty could only push away (0.665 =
  51.7% of A1->A2 regression via that one direction); value-of-LF +5.97 decomposes ~57-60%
  direction-supply + ~40% row-space fit (NOT just identifiability). -> turn 2 dispatched
  (fisher m=0 channel; coarsest-rung selection cost).

- 2026-08-01 ~06:2x PDT r2s4-B2 COMPLETE (register 6/6; disk-verified; 3 tools promoted:
  ladder_pair_alignment_audit [pre-flight, --fail-on gate works], shrinkage_curve_anatomy,
  ceiling_fast [frozen original untouched]). Part 7: last untouched channel = INPUT-SIDE
  privileged info; teacher-projection diagnostic named (Option A recommended for B3, needs
  preds dumped); support-not-identifiability = round-rule CANDIDATE pending 2nd card;
  benchmark-integrity item (ifc_raw eval assumption failed 4 independent places) for Eloise.
  Reporting instruction: B2 + r2s3-B2 reported as a pair. -> B3 websearcher dispatched
  (batch counter -> 3).

- 2026-08-01 ~06:5x PDT r2s1-B2 code-reviewer SUGGEST (6/6): strongest-evidenced build;
  L4 decidability verified intact (rank reading cancels as common factor); card's
  illustrative r_sel/param counts unreachable under the card's own mandate (recording item);
  decoder shuffle RNG not checkpointed (minimal fix noted for B3); reviewer ran the never-
  exercised pfc_class_split itself (exit 0, AUC 0.9996). ORCHESTRATOR SUBMITTED seed 0:
  job 66189580 (h200, walltime 2h->3h per reviewer). Card -> running. ALL FOUR B2 CARDS
  NOW SUBMITTED-OR-BEYOND.

- 2026-08-01 ~07:1x PDT r2s2-B2 initial-analyzer SUCCESS (6/6): geomean 19.3868 (band met);
  FALSIFIED 3/4 clauses — BUT all F1-firing cells are B:all LOO-ARTIFACT cells (train side
  = exact scaled copy of own real LF; test side = train_mean; excluding them F1 -> 0 cells,
  F3 survives on 2). F2 INVERTED (k=1 beats k=all — empirical posterior sample beats
  conditional mean). k* unstable 3/6 (helmholtz flips B:1<->B:4, blend contains). Reviewer
  carry-forwards discharged. -> mechanism-analyzer dispatched (artifact-vs-substance is THE
  question).

- 2026-08-01 ~07:4x PDT USAGE-LIMIT INCIDENT: three agents killed early by weekly API limit
  (r2s2-B2 mech t1, r2s3-B2 mech t2, r2s4-B3 websearch); operator re-logged-in; all three
  RE-DISPATCHED with partial-file-distrust instructions. SLURM jobs unaffected.

- 2026-08-01 ~08:1x PDT r2s3-B2 mechanism turn 2 (7/7): fisher m=0 gain = conditional-mean
  VARIANCE REDUCTION (level-swap reproduces 76.8%; LF adds no condition info; alignment
  unchanged) — r2s4's barrier claim NOT overturned (LF affine 1.0133x barrier); F5 sharp
  limb = task property (all condition-response arms lose to constant, useful share negative);
  H8: penalty over-amplitude monotone in rung coarseness, in_rung_loo picked worst on 1e-8
  tie (cost 0.64 = 0.68x floor, not individually claimable). -> turn 3 dispatched (H9 ch
  channel decomposition + part 6).

- 2026-08-01 ~08:3x PDT r2s1-B2 seed 0 COMPLETED (66189580, 16:50, exit 0:0 — well under the
  3h budget). -> initial-analyzer dispatched (per-dataset legs L1-L4; realized-not-
  illustrative r_sel values; ch decision leg at 3x mce).

- 2026-08-01 ~09:0x PDT r2s2-B2 mechanism turn 1 (6/6, redo after limit kill): F1 fired on
  STATISTIC MIS-SPECIFICATION — uncentered cross-spectra + bias-free ceiling vs affine
  corrector class; centred repair flips B:all gamma to 0.99-1.00 (== real-LF rung) and
  F1 -> 0 cells. The COHERENCE RULE SURVIVES; the calibration card caught its own
  instrument's spec error (this IS the calibration deliverable working). Bonus: Fourier-
  energy oracle not a bound under rel-L2 (corrector beats it at real-LF rungs). -> turn 2
  dispatched (real closure question = 2 non-B:all F3 cells; F2 restatement).

- 2026-08-01 ~09:2x PDT r2s4-B3 websearcher PARTIAL-ACCEPTED (7/8; sole failure = 1-iteration
  cap overrun, self-reported; content complete, 16/16 citations traced, 2 attributions
  actively REFUTED, prior killed attempt quarantined). D1 teacher-projection diagnostic =
  the unpublished composition; D2 selection preempted (gating open); mean-of-ratios artifact
  must be presented PROJECT-LOCAL. -> B3 brainstormer dispatched (strict-1-seed operator
  note included per Eloise's structure question).

- 2026-08-01 ~10:0x PDT r2s1-B2 initial-analyzer SUCCESS (6/6): FALSIFIED (L1 2/5: allen_cahn
  +6.15=7x mce, ch +1.30=14x mce vs in-job decoder; L2 4.7x, every resample >4x) — B1's
  "capacity buys nothing" OVERTURNED on ch (advantage grew 0.55->1.30; no rank rescues;
  band-3 gain pinned on grid edge as B1 reviewer predicted). L3/L4 not fired (floors beaten
  everywhere; selection rule vindicated on distinguishable cells). pfc/fisher = dead cells
  (all arms collapse to dc_only). geomean 18.3622 (informational). -> mechanism-analyzer
  dispatched (real-capacity characterization on ch is THE question).

- 2026-08-01 ~10:3x PDT r2s3-B2 mechanism turn 3 (6/6): ch three-channel anatomy — 68.3% of
  A0-A2 gap = the 15 unseeable affine directions (coverage-of-design fact, not curriculum:
  A3's pool leaves design rank BIT-IDENTICAL while fields differ 0.398); LF calibrates
  amplitude but does NOT teach direction on ch; dimension control shows "condition-response
  repair" not "null-aligned defect". Part 6 written incl. all 4 postmortem items; M5:
  A0-vs-A1 COVERAGE CONTRAST is the claimable deliverable (ifc +5.97, ch +17.44), A2
  reported beside as pre-registered-mechanism-that-failed. -> register turn dispatched.

- 2026-08-01 ~11:0x PDT r2s4-B3 brainstormer SUCCESS (10/10): D1 teacher-projection ledger
  (advantage_reachable/unreachable split, OOF-target two-level folds — vacuity-proofed);
  STRICT 1-SEED argued via 5-fold paired deltas + imported B2 spread (no §12.4 exception —
  per operator structure preference); B2's non-implementable test-side phrasing FIXED
  (measured on held-out train per §5.9); free test-split distillation contrast; ch predicted
  the one reachable-component dataset (2nd test of support rule). 184 legs, ~60-110 min.
  -> starter dispatched.

- 2026-08-01 ~11:3x PDT r2s4-B3 starter SUCCESS (12/12): B3.json drafted, no TBDs, strict
  1-seed (no seeds-2-3 leg). -> builder dispatched.

- 2026-08-01 ~11:5x PDT r2s1-B2 mechanism turn 1 (7/7): ch L2 deficit >=40% = SELECTION-RULE
  ARITY BUG (rule kept cardinality, fitted window {0,1,2,3} vs identifiable SET {0,1,12,13};
  modes 12-13 = 43-47% DC energy; set-head DC cos 0.9948 vs window 0.0593; recovers 0.513 =
  5.6x mce non-oracle). Band-3 pinning = calibration overfit (Wiener stage COST 0.098 test;
  oracle band headroom only 1.0x mce). Basis NOT bottleneck (decoder worse than oracle
  rank-2; edge = coefficient accuracy). Non-contiguous identifiable sets on 3/6 datasets.
  Residual 0.784 = coefficient-map question. -> turn 2 dispatched.

- 2026-08-01 ~12:3x PDT r2s2-B2 mechanism turn 2 (6/6): F3 surviving firings = ESTIMATOR BIAS
  (intermediate sigma(cond)-measurable -> true statistic 0 by DPI; zero-information control
  reproduces firings to <=0.005; excess anti-correlates with conditioner residual -0.560);
  F2 = endpoint comparison (interior k beats both ends 4/4; job's k* already interior).
  ALL THREE fired clauses now traced to statistic defects. Real lead: training-free
  interior-k LF average beats trained corrector on ac/ch. -> turn 3 dispatched (part 6:
  card falsified its own instruments; calibration deliverable = centred repair + artifact
  taxonomy).

- 2026-08-01 ~13:0x PDT r2s3-B2 COMPLETE (register 5/5; disk-verified; 2 tools promoted —
  identifiability/coverage family now SIX instruments with standing relationship note).
  Part 7: penalty family dead on ifc, inverted premise on ch (amplitude-corrected A1' =
  the one live question, needs training); B3 = measurement-completion card (ch draws 1-2 +
  coverage-audited extension) with explicit close-on-B2 fallback if timing forces.
  SIXTH CARD CLOSED. -> B3 websearcher dispatched (batch counter -> 3).

- 2026-08-01 ~13:3x PDT r2s3-B3 websearcher SUCCESS (7/7, cap hit, pdf-rule honored): E5's
  novel verdict SUPERSEDED (±LF-ablation genre published: 2511.01830 fixed-budget fidelity
  sweep, 2408.17075); P2 mechanism claim preempted (survey states it); P3 taxonomy open only
  in the level channel + measured shares; P4/P5 preempted. B3 = regime-specific composition
  or close-on-B2 skip. -> brainstormer dispatched with both options live.

- 2026-08-01 ~14:0x PDT r2s1-B2 mechanism turn 2 (7/7): allen_cahn L1 = POST-HOC-STAGE
  ARTIFACT (head beats decoder RAW +26.70 = 30.3x mce; blend = error-decorrelation ensemble
  — head error cos 0.998 with dc_only so blend pays it nothing; 65% of "winning decoder"
  prediction = (d+1)-param ridge); 10-param per-mode OOF quadratic beats 15.85M decoder
  23.6x mce there. ch: nonlinearity refuted (affine selected all modes), residual 8.55x mce
  with H2 (spatial bias on unidentifiable modes 2-3) needing decoder preds. pfc/fisher empty
  cells (0/30 identifiable post-DC). -> turn 3 dispatched (part 6).

- 2026-08-01 ~14:4x PDT r2s3-B3 brainstormer SUCCESS (12/12): 33-leg measurement-completion
  model card (A0 vs A1 ±LF, 6 panel datasets x 3 draws, penalty DELETED); pre-flight
  coverage audit RUN pre-design — all 3 extension datasets m_reduction_full=0, so F2
  discriminates direction-supply vs pure-coverage; close-on-B2 REJECTED (4 grounds incl.
  r2s4-B2 falsification making this the only live criterion-1 route); A1' dropped on B2's
  own numbers (alignment not amplitude defect); helmholtz marginal (~1.0x mce) -> F1 needs
  5/6. ~85 min est. -> starter dispatched.

- 2026-08-01 ~15:1x PDT r2s1-B2 mechanism turn 3 (6/6): closed-form decorrelation-payoff law
  fitted (1 param, resid <=0.047) — allen_cahn head IS dc_only numerically (rho=1.0000) so
  blend can't pay it; equal-rho counterfactual REVERSES L1 there (head wins 2.1-7.2x mce);
  ch control clean (blend moves delta 0.0000; 8.55x residual stands, H2 needs decoder
  preds). Part 6 written (15 findings, 4-part postmortem: L1 was effectively ">=2 of 3"
  after empty cells). -> register turn dispatched.

- 2026-08-01 ~15:3x PDT r2s3-B3 starter SUCCESS (15/15): B3.json drafted, no TBDs; P1
  supersession recorded on card. -> builder dispatched.

- 2026-08-01 ~16:0x PDT r2s1-B2 COMPLETE (register 8/8; disk-verified; 2 tools promoted:
  blend_decorrelation_payoff [equal-rho counterfactual], selection_set_vs_window_audit
  [arity-bug detector]). SEVENTH CARD CLOSED. Part 7: ch residual 8.55x mce untestable
  without decoder preds (standing build gate); three instrument repairs prerequisite to any
  further capacity claim; B3-or-close explicitly posed. Round instrument-defect section now
  has r2s1-B2's 3 defects + r2s2-B2's 3 statistic defects. -> B3 websearcher dispatched
  (brainstormer owns the close decision per §4.6).

- 2026-08-01 ~16:4x PDT r2s1-B3 websearcher SUCCESS (7/7, cap hit, pdf-rule honored): C2
  (blend = Bates-Granger 1969 minimum-variance combination; evaluation-artifact reading
  unpublished) = best-supported composition; C1 open-but-thin; C3 PREEMPTED (supervised-PCA
  — bug fix only); C4 unchecked (diagnostic only). -> B3 brainstormer dispatched with
  B3-or-close + instrument-repair-card option framed.

- 2026-08-01 ~17:0x PDT r2s3-B3 builder SUCCESS (10/10): build dfcd46c; smokes exit 0 (incl.
  A0 resume bit-identical); deleted-surface negative tests RAISE; 26/26 env keys + 33/33
  legs verified; penalty family fully deleted per card. -> code-reviewer dispatched.

- 2026-08-01 ~17:4x PDT r2s4-B3 builder SUCCESS (10/10): build fb00237; smoke exit 0 (36 legs,
  ledger identity residual 0.0); full+partial resume bit-identical; pair-alignment pre-flight
  PAIRED_ALIGNED 5/5; builder caught card's ridge-arithmetic error (degree-fallback fires on
  ch, correctly implemented as carded rule). -> code-reviewer dispatched.

- 2026-08-01 ~18:1x PDT r2s1-B3 brainstormer SUCCESS (13/13): B3 chosen over close (4 grounds:
  converts post-hoc findings to pre-registered OOS tests; lifts preds gate; measured cost
  ~17 min; instrument value is stream's remaining value). Stage-free scored column (no
  Wiener/blend on scored arm); Bates-Granger prelude written from calib moments BEFORE test
  read (L2: predict realized post-stage skill within 1.5x mce on >=2); SET repair L3; the
  ~19.1-worse-than-staged-18.36 expectation PRE-REGISTERED as part of the claim. -> starter
  dispatched.

- 2026-08-01 ~18:4x PDT r2s3-B3 code-reviewer PASS (6/6 — round's first clean PASS; AST-level
  F3 seam verification; draws exact; walltime overrun pre-classified INFRA). ORCHESTRATOR
  SUBMITTED seed 0: job 66196690 (h200). Card -> running.

- 2026-08-01 ~19:0x PDT r2s1-B3 starter SUCCESS (23/23): B3.json drafted, no TBDs; C2 headline
  verdict transcribed unnormalized; 5 build gates in _build_gates. -> builder dispatched.

- 2026-08-01 ~19:3x PDT r2s2-B2 mechanism turn 3 (8/8): scored stack's value = closed-form
  LSI Wiener (100/97/77/33% of gain; CNN rejected OOF 5/8 cells; lambda inert 3/4); B1's
  corrector-futility calibration off by 7-180x at scored rungs; rule's 0.05 relative floor
  = 0.6-9.5 skill units = 10-817x mce (UNITS defect — dimensionless thresholds don't price
  decisions). Part 6 written. -> register turn dispatched (decision-cost audit = exportable
  fix; close recommendation acceptable).

- 2026-08-01 ~19:5x PDT r2s4-B3 code-reviewer SUGGEST (6/6): fold construction verified
  leakage-free BY EXECUTION; degree-fallback = card's own rule; 320-vs-280 proj_best data
  advantage flagged as UPWARD bias on advantage_reachable (analyzer standing caveat);
  PRE-ANALYSIS ACTION OWED: signed-reach fix in teacher_projection_ledger.py (abs->signed;
  03_ledger.sh re-runs standalone). ORCHESTRATOR SUBMITTED seed 0: job 66197075 (h200).
  Card -> running. Both B3 SLURM jobs now on cluster.

- 2026-08-01 ~20:1x PDT OPERATOR HALT (Eloise: "halt everything (except currently running
  slurm jobs)"). Actions: 3 crons DELETED (orchestrator pulse 03a7cf19, maintainer 60625c6e,
  auto-sync 13995fd8); in-flight agents KILLED: r2s1-B3 builder (mid-build — worktree may
  hold partial family code, card still 'drafted'; REBUILD FROM SCRATCH on resume, distrust
  partials), r2s2-B2 register turn (mid-tool-promotion — part 7 NOT written, card still
  'analyzing'/turn_3; tools/index.md may hold a partial entry — VERIFY before trusting;
  re-dispatch register turn on resume), maintainer walk (read-only, no cleanup needed);
  2 SLURM monitors stopped. LEFT RUNNING per operator: jobs 66196690 (r2s3-B3-s0) and
  66197075 (r2s4-B3-s0) — both checkpoint-resume-safe.
  RESUME CHECKLIST: (1) check job outcomes via sacct; (2) re-dispatch r2s2-B2 register turn
  (verify/clean partial index entry first); (3) re-dispatch r2s1-B3 builder fresh;
  (4) on job completion: r2s4-B3 needs the SIGNED-REACH probe fix (03_ledger.sh re-run)
  BEFORE its initial-analyzer; (5) re-create crons per HOW_TO_LAUNCH §2-3; (6) commit this
  state (auto-sync cron is gone — manual git add mffp_autoresearch/round2 + push).

- 2026-08-01 ~08:1x PDT OPERATOR RESUME (Eloise, after restart-vs-resume + contamination
  review: resume approved; generator ladder.py fix runs as a parallel mentor-gated proposal
  track, NO retraining — no model trains on the stored pre-aligned arrays). Checklist walked:
  (1) sacct: 66196690 r2s3-B3-s0 COMPLETED 0:0 54:57; 66197075 r2s4-B3-s0 COMPLETED 0:0
  1:31:34. (4) already satisfied in halt window (signed-reach fix 09e2c6b, 03_ledger.sh
  re-run, diagnostic.json regenerated, no verdict flip). tools/index.md re-verified clean
  (mtime predates killed register turn). r2s1-B3 worktree partials (untracked models_r2/,
  notes/) archived to state/halt_partials/r2s1_B3/ — worktree git-clean at 9e10d41; builder
  must not reuse them. DISPATCHED (background): r2s2-B2 register turn (re-dispatch),
  r2s1-B3 builder (fresh), r2s3-B3 initial-analyzer (s0), r2s4-B3 initial-analyzer (s0,
  post-fix artifacts, 320-vs-280 upward-bias caveat carried), + off-round ladder-fix
  proposal agent (mentor package under mffp_autoresearch/ladder_fix_proposal/; no pushes,
  sample-round only). (5) crons re-created (session-only, 7-day auto-expiry): orchestrator
  pulse 8de33a00 (4-59/10), maintainer 75c00bb0 (9-59/20), auto-sync f14a9d81 (17-59/30).
  (6) this commit.

- 2026-08-01 post-resume session log (compressed). r2s4-B3 initial-analyzer: FALSIFIED
  F3+F4a (advantage_total claimable 4/4 but reachable ~0; anchor untouched) -> mechanism
  turns: T1 ceiling analysis (pfc/hz cells tautological, ch genuine; ridge-flip discovered),
  T2 row-count+capacity controls (flip does NOT survive: 72% row bias, 99.2% function-class
  term; teacher-target term 50-90x below threshold; F4a definitional artifact, corrected
  reading 0/4) -> T3 dispatched (spatial structure of unreachable half + part 6).
  r2s3-B3 initial-analyzer: FALSIFIED F1 3/6 F2 0/4 with knife-edge vs mce-only reading ->
  T1 (knife edge resolves FOR falsified: mce imports variance constant from wrong regime;
  H1 variance-reducer quantified), T2 (F4 adjudicated on degenerate single-member set +
  timeout-stall recovery, all 14 legs; M1 gain channel 96.9%; M2 pfc structural harm;
  M3 capacity non-binding), T3 (M1b scale-not-map; M5 no-LF ensemble beats LF on fk/pfc;
  part 6, 23 findings) -> register: tools effect_threshold_readings.py +
  map_dispersion_scale_shape.py promoted; CARD COMPLETE (10th). B4 websearcher dispatched
  (batch counter -> 4); part 7 ranks gain-head learnability / budget-matched ensemble /
  repaired claimability; do-not: no LF-supply engineering on fk/pfc.
  r2s2-B2 register (re-dispatch) COMPLETE: tools zero_gradient_stage_ladder.py +
  relative_gain_units_audit.py promoted + coherence-gate standing amendment; card closed
  (9th) -> B3 websearcher (verdicts: composition open, Operator Boosting closest prior art;
  WebFetch disabled in env — routed around, fix subagents/websearcher.md before batch-5) ->
  brainstormer: B3-NOT-close, 4-arm zero-gradient scored design (A1_lsi scored; OB base-swap
  control; 5 in-job fold/train seeds vs certified mce; est 60-80 min) -> starter drafted
  card (no TBDs) -> builder dispatched.
  r2s1-B3 builder (fresh) COMPLETE: build 2b030f0, 13/13, G-B structural TestLockError,
  72/72 env keys, registration vendored -> code-reviewer SUGGEST (6/6): headline = disjoint
  smoke stale vs HEAD; orchestrator discharged the gate (re-ran contract smoke at HEAD with
  full ENV_ARGS: exit 0, nRMSE bit-identical 1.140818334879289; code_hash delta explained =
  env-inclusion in code_hash(), empty-env hash at HEAD == d8cc06f0 exactly) -> ORCHESTRATOR
  SUBMITTED seed 0: job 66262741 (h200). Card -> running.
  Maintainer walks 1-5: clean; walk-3 caught r2s3-B3 F4 producer timeout stall (resolved via
  orchestrator nudge); timing ledger current; auto-sync hazard noted (cron sweeps pre-staged
  index — guard added to orchestrator sync procedure).

- 2026-08-01 ~20:4x PDT OPERATOR RESUME (Eloise: "resume round 2", new session). State on
  arrival: all 4 round-2 jobs still PENDING on GPU priority (66262741 r2s1-B3-s0,
  66267438 r2s2-B3-s0, 66267441 r2s2-B3-guard-s0, 66269660 r2s4-B4-s0); r2s3 closed;
  no agent stages in flight; nothing to advance — round is compute-bound. Only resume
  action needed: crons re-created (session-only, 7-day auto-expiry): orchestrator pulse
  aa4dcb66 (4-59/10), maintainer 2c7fed88 (9-59/20), auto-sync a45bd18b (17-59/30).
  Index-clean guard verified before manual sync commit of this entry.

- 2026-08-02 ~05:3x UTC pulse: QUEUE UNSTUCK after ~12h stall — 66262741 (r2s1-B3-s0,
  limit 3:00:00) and 66267438 (r2s2-B3-s0, limit 2:30:00) transitioned PENDING->RUNNING
  on hpc-sm-02-17. 66267441 (r2s2-B3-guard-s0) and 66269660 (r2s4-B4-s0) still PENDING.
  No dispatches due (analyzers gate on COMPLETED). Maintainer resumes full 20-min cadence.
  On completion: r2s1-B3 -> initial-analyzer (s0); r2s2-B3 -> initial-analyzer once BOTH
  main and guard jobs are done (guard is part of the B3 design).

- 2026-08-02 ~05:4x UTC pulse: 66262741 r2s1-B3-s0 FAILED (1:0, 13:21 elapsed) ->
  experiment-debugger dispatched (attempt 1, ALGO/INFRA TBD). 66267441 r2s2-B3-guard-s0
  COMPLETED 0:0 (1:09); 66267438 r2s2-B3-s0 main still RUNNING (~16 min) — initial-analyzer
  gates on BOTH r2s2 jobs done. 66269660 r2s4-B4-s0 PENDING->RUNNING on hpc-sm-02-17.

- 2026-08-02 ~05:5x UTC pulse: 66269660 r2s4-B4-s0 COMPLETED 0:0 (5:58) ->
  initial-analyzer dispatched (diagnostic card, single run). 66267438 r2s2-B3-s0 main
  still RUNNING (~26 min). r2s1-B3 debugger attempt 1 still in flight (no re-dispatch).

- 2026-08-02 ~06:1x UTC r2s4-B4 initial-analyzer COMPLETE (6/6): FALSIFIED per ANY-of rule —
  F4 fired (rung gap_ratio drop 5.47 < in-job fold spread 13.52; drop monotone and in
  predicted direction but below its own resolution scale — recorded with caveat, not spun).
  F1/F2/F3/F5 held; F5 perfect (all 3 frozen ifc floors reproduce at rel dev 0.0 — no ifc
  number in the round invalidated). Delta_5_1 = 4.679 CI [4.02, 5.33] => O1_EFFECT,
  replicates B1's certified +4.68. Anchor untouched. heat_local guard flagged (14.46x
  copy-LF, but better than own B2/B3 legs at same tier). Ladder-audit exit 2 = by-design
  MISPAIRED certificate. -> mechanism-analyzer turn 1 dispatched (probe menu: fidelity_64
  rung spread; n=1 band floor failures; ~1e-6 B1-seed reproduction instrument check).

- 2026-08-02 ~06:3x UTC pulse: 66267438 r2s2-B3-s0 main COMPLETED 0:0 (44:46) — both r2s2
  legs done -> initial-analyzer dispatched. In flight: r2s1-B3 debugger attempt 1,
  r2s4-B4 mechanism turn 1. SLURM queue now empty of r2-* jobs.

- 2026-08-02 ~06:4x UTC r2s4-B4 mechanism turn 1 COMPLETE (6/6): B1-seed reproduction
  RESOLVED = common random numbers (leg_seed formula makes replicate seeds {0,1,2} = B1
  card seeds; init-only channel at n=5) — re-implementation equivalence check, not an
  independent draw. ifc MCE decomposed: design-effect 91.5% / init 2.7% / interaction 5.8%
  over 31 independent draws (MCE at 48th pct of own sampling dist); F4 re-priced under 8
  readings (3 fire, 5 don't; all measurement-channel readings clear); fidelity_64 spread
  82% deterministic fold effect, driven by outlier HF row 4 (3.23x harder than row 3).
  No existing ifc verdict flips (B4 4.679 = 1.68x max init range; r2s3-B3 5.984 = 2.15x).
  -> turn 2 dispatched (H1: 5-row design = 4 rows + outlier; row-4 membership vs 91.5%
  design variance; n=1 band 5/15 floor record same phenomenon?).

- 2026-08-02 ~06:5x UTC r2s1-B3 debugger attempt 1 COMPLETE (6/6, ALGO 1/5): root cause =
  pod_basis rank screen (s_i > sqrt(eps)*s_max) has zero margin vs Gram squaring; admitted
  a ||v||=0.366 roundoff eigenvector on heat_local (GUARD leg — panel leg had finished
  green, geomean skill 18.7500, helmholtz 1.140818 matches contract smoke). Fix: self-
  validating _orthonormal_rank truncation (tuned-constant fix rejected by margin sweep).
  Panel invariance verified: all scored datasets identical mode counts; only heat_local
  changes (33->17 modes, now rank-limited — read clip_rule as rank-limited). Commit
  568522c; debug_notes[0] appended; RELAUNCHED seed 0 as job 66285051 (PENDING).
  Pulse: no other transitions; in flight r2s2-B3 initial-analyzer + r2s4-B4 turn 2.

- 2026-08-02 ~07:0x UTC r2s2-B3 initial-analyzer COMPLETE (6/6): FALSIFIED in the positive
  direction — trained scored stage HELPS. Geomean 20.0315 (s0, provisional) vs anchor
  23.0636: delta -3.0321 = 2.66x panel mce, inside part-4 predicted band 19.2-20.7.
  F1 fired 9.2305 vs 1.7594 (5.25x, 5/5 sign); F2 2/4 decidable (ac 10.49x, fk 46.84x;
  pfc/hz nulls degenerate alpha_nn==0 cells); F3 no-fire (A3 no-LF swap worse everywhere
  62x/23x/6x/2.5x mce); F4 no-fire. cratered_verdict="cratered" via third disjunct ONLY
  (falsification fired) — NOT a performance crater; basis recorded. heat_local guard
  flagged 4.14x (non-blocking). Anchor untouched (needs 3-seed). STRONG end-of-round
  3-seed candidate. Guard job renamed itself to panel name — ledger match by job ID
  (reviewer R1 materialized). -> mechanism turn 1 dispatched (ac-vs-ch contrast probe).

- 2026-08-02 ~07:2x UTC r2s4-B4 mechanism turn 2 COMPLETE (6/6): H1 REFUTED at sign level
  via exact 5-player Shapley (31 coalitions x 3 inits, validated 141/141 legs at 0.0 diff).
  Row 4 = MOST valuable row (phi 4.383, 22.5%, complement: worst alone/best to add;
  1[row4]x1[n>=2] interaction lifts design R^2 0.814->0.923); row 0 = redundant/interfering.
  Coverage stats ANTI-informative (Spearman -0.60 vs row value). n=1 floor record =
  floor-side artifact. F4 postmortem: treatment effect vs coverage-unevenness statistic.
  F3 incidentally no-fire. New: H3 (redundant row 0), H4 (coverage-based row selection
  picks exactly wrong rows — cross-stream actionable). Self-corrected card reformat
  (indent slip, final diff 1/1). -> turn 3 dispatched (capacity axis, matched-n {1,3,5}
  sub-lattice; part 6 due).

- 2026-08-02 ~06:2x UTC pulse: 66285051 r2s1-B3-s0 (post-fix relaunch) COMPLETED 0:0 in
  1:49 — VERIFIED against artifacts before analyzer dispatch (checkpoint resume: panel
  geomean 18.749954 matches pre-failure leg; all 6 panel + 3 guard result entries fresh
  in outputs repo eval/; zero-byte .err). -> initial-analyzer dispatched. r2-* queue now
  empty. In flight: r2s1-B3 initial-analyzer, r2s2-B3 mech turn 1, r2s4-B4 mech turn 3,
  maintainer walk 26.

- 2026-08-02 ~06:4x UTC r2s2-B3 mechanism turn 1 COMPLETE (8/8): seam-exact A0/A1 repro
  (0.0 dev, 4/4 datasets). Headline 9.2305 ac win = per-sample LEVEL recalibration —
  52.7% reached by condition-blind pointwise remap (level-only +5.340, pattern-only
  -0.460; level oracle +36.43 = 3.95x CNN gain). ch = mirror image (pattern channel;
  free remap 9.89x CNN gain; DC share 0.0045 vs ac 0.981; only ch interface-local 3.64x).
  A1 band-0-only class (band rel err ~1.00 above k_max/8 all datasets). pfc alpha_nn=0
  CORRECT. fk 46.84x-mce reading = only 0.16% relative (units flag). Card ships no dumps/
  ckpts — A2 unreconstructable, stand-ins labelled. -> turn 2 dispatched (alpha_nn calib
  criterion level-dominance on ch; ac level oracle reachable from condition vector alone?).

- 2026-08-02 ~07:0x UTC r2s4-B4 mechanism turn 3 COMPLETE (8/8), part 6 written (13
  findings): capacity axis resolved — row-4 complementarity is DATA GEOMETRY not capacity
  (both widths rank row 4 first; w8 margin larger 1.82x vs 1.65x mce); turn-2 "one effect"
  conjecture refuted (w8-w32 penalty ANTI-concentrated on row 4's partition); capacity
  penalty is pure structure while w8's amplitude calib is better at n>=3; the WIDE model
  is the collapsed one (49.2% of condition-driven variation at best); HF rows = amplitude
  calibration set (phi_structure negative for rows 0-3); 65.4% of n=5 scored error
  removable by per-sample oracle gain vs 0.19% global. -> REGISTER turn dispatched
  (candidates: hf_row_shapley_value.py, gain_channel_ladder.py; cross-stream flags H4/H5
  into part 7).

- 2026-08-02 ~07:2x UTC r2s1-B3 initial-analyzer COMPLETE (14/14): geomean 18.749954 (s0)
  — best single-seed panel of the round, 4.3137 BETTER than anchor = 3.78x mce; anchor
  candidate for end-of-round 3-seed confirm (strict 1-seed policy holds — no seeds 1-2
  now). FALSIFIED via L2: calibration-fold BG prelude misses realized post-stage skill
  3/3 (needs 2/3), both arms, both correspondences, min miss 2.69x mce; L1 passed 75.1x
  (10-param dc_meanfield closed-form head beats 15.8M-param FiLM-FNO decoder on ac by
  66.06); L3 passed narrowly but attribution wrong (T1-F7 basis repair, not arity).
  sod_1d guard flagged 3.21x (not excused — epoch-independent head). Pre/post-fix panels
  bit-identical (debugger nil blast radius CONFIRMED). Anchor untouched. -> mechanism
  turn 1 dispatched (probes: ac 1-direction oracle saturation; ch capacity band; prelude
  sign bias + two-mode lambda collapse).

- 2026-08-02 ~07:4x UTC r2s4-B4 REGISTER COMPLETE — CARD CLOSED (11th; tools
  hf_row_shapley_value.py + gain_channel_ladder.py promoted, verified by exact repro +
  foreign-data smoke; part 7 carries H4/H5 + provenance caveat). r2s4 stream at 4 batches
  vs ~3-batch budget (program L164): marked CLOSE CANDIDATE in current_stage.txt — no B5
  without end-of-round decision. ORCHESTRATOR ran the register turn's decidable follow-up
  (one read-only gain_channel_ladder call on r2s3-B3's shipped ifc A0/A1 preds + stripped
  test targets; result archived state/adhoc_measurements/r2s4B4_register_followup_*.json):
  A1_lf_cov raw 2.150 BEATS A0_nolf's per-sample amplitude ORACLE 2.761 => LF moved
  STRUCTURE, not just per-sample gain (H5 refined, second alternative excluded for
  amplitude-only; note A1 itself globally amplitude-miscalibrated — global rescale removes
  46.8% of its error, oracle scalar 0.938, dispersion 1.06 = no collapse). Seam hash
  d3d0ade9 matches round eval.

- 2026-08-02 ~07:4x UTC r2s1-B3 mechanism turn 1 COMPLETE (8/8): L2 UNPASSABLE BY
  CONSTRUCTION — 10/12 blend cells degenerate lambda (8x 1.00, 2x 0.00) so the "law"
  evaluated to identity (law-form error exactly 0 in all 10); 100% of misses =
  calibration->test transfer of a 40-sample nRMSE estimate, all within 1.16 sigma of its
  own sampling noise; L2 tolerance only 0.026-0.107 sigma (resolvable test needs 3468-
  28043 calib samples vs 40). C2 headline neither supported nor refuted by L2 — but the
  lambda census itself (10/12 degenerate) IS the protocol defect the card set out to
  detect. NEW separable instrument defect F6: fit-set-asymmetric blend bases (calib bases
  fit on n=320 fit_idx vs test bases = frozen floors on full 400; signed gap +93.8%
  helmholtz) — not this falsification's driver but corrupts any future intermediate-
  lambda card; carry into part 7 as recipe fix. -> turn 2 dispatched (allen_cahn
  1-direction SET capacity probe).

- 2026-08-02 ~08:0x UTC r2s2-B3 mechanism turn 2 COMPLETE (5/5): headline ac win = partial
  gradient-trained solve of a CLOSED-FORM scalar regression — 9-feature quadratic ridge on
  the 3-dim condition vector predicts HF spatial mean to 1-R^2 3.4e-4, worth 34.32 units =
  96.6% of level oracle = 3.76x the CNN's entire gain (5/5). ch level law EXACT (3.9e-15)
  but fluctuation headroom condition-UNREACHABLE (all neg held-out R^2) = genuine class
  ceiling. pfc could_not_fire SUPERSEDED (6.03x mce closed-form channel, 5/5). fk CNN
  effect IS the scalar (0.99x). Non-scored counterfactual: scalar-law substitution moves
  geomean only -0.800 = 0.70x panel mce. M4 alpha_nn probe rejected as partly self-
  refuting (reasoning recorded). -> turn 3 dispatched (residual HF - level_law
  decomposition: second scalar channel vs field-structured; LF-pool obtainability;
  part 6 due).
