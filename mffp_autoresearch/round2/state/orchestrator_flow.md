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
