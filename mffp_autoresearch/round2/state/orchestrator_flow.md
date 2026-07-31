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
