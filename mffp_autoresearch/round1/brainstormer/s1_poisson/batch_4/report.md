# Brainstormer Report — Stream `s1_poisson`, Batch 4

**Stream**: s1_poisson (gap) · **Batch**: 4 (self_only disambiguation slot) ·
**Total iterations**: 1 · **Slot filled**: yes (1/1) ·
**Reopen candidates resolved**: 0 of 0 (none exist in the round)

## Slot

- **Category**: compute-vs-weighting attribution of the `self_only` win on the
  ifc fidelity ladder — a 2x2 controlled factorial (per-level loss weighting x
  stage-1 gradient-step budget) on `ifc_poisson`, run as an in-repo
  measurement.

- **Card type**: `model`. Justification: program.md §4.3 defines `diagnostic`
  as *"a **measurement**, no training"*; this card trains six stage-1 bases, so
  `diagnostic` would misuse the type and the maintainer's tier accounting. It
  is a diagnostic-**purpose** model card: no arm is proposed as a candidate
  model, none is promoted to the leaderboard, and ADR 0007 propose-many does
  not apply (spec-pre-directed slot, no candidate pool — all six arms are
  controls in one pre-registered factorial and all six run directly at 200
  epochs; the contract-tier run is plumbing only, per ADR 0007 *"Screening
  numbers are NEVER reportable results"*). ADR 0007's binding guardrail is met:
  the decisive contrast (A2 and A4 against the A0/A1 controls) is fixed here,
  before submit. ADR 0004: seed 0 only, every number `provisional-single-seed`.
  ADR 0009: trivially clean — no governing equations, residuals or known
  operators are used anywhere, at test time or otherwise.

- **Motivation**: B3 measured `self_only__none` at **0.021913 nRMSE / 0.6087
  skill** — the round's best claimable `ifc_poisson` number — against the
  `allpairs` control's **0.034264 / 0.9518**, a gap of **0.3431 skill =
  1.43x the certified floor**; and B3's mechanism turn 1 then proved the two
  row sets carry *identical* information (*"all six cross blocks are exact
  duplicates of the self block at their target level ... differing **only** in
  the `f_src` tag"*; distinct rows 175 of 280), so the knob is a per-level
  **replication schedule x1/x2/x3/x4** which simultaneously moves effective
  loss weight (0.625x/1.25x/1.875x/2.5x) **and** raises stage-1 gradient steps
  per epoch from 11 to 18. B3 part 7 states the debt verbatim: *"The decisive,
  cheap experiment is a THIRD row set with allpairs' 280 rows and self_only's
  per-level WEIGHTS (or self_only's 175 rows trained for 280/175 x the
  steps)."* The websearcher scores exactly this experiment **`preempted`
  (ML-general methodology) — open only as an in-repo measurement**, supplies
  the sentence that justifies the design — *"However, this comparison conflates
  algorithmic quality with compute: GRPO performs 8x more gradient updates per
  epoch than REINFORCE and POMO"* (https://arxiv.org/html/2606.10321v1) — and
  the live warning that in that same paper *"the epoch-matched ranking
  **reversed** under step-matching"*, i.e. the B4 outcome may flip the B3
  story. The card therefore claims the **measurement**, never the method
  (*"Any card text implying the step-matched control is an innovation
  contradicts this loop"*), and the per-level weight knob is used strictly as
  the **instrument** (D-B: *"`preempted` (MF-general)"*).

- **Concrete config**: new family `models_r1/mf_fno_ladder_attrib`, vendored
  from B3's build commit `57c24576abe6b045b837ccfd55f331a80e3f8b05`
  (`models_r1/mf_fno_ladder_gain`; §12 vendoring convention), head **OFF**
  everywhere (`MFFP_GAIN_HEAD=none`, `MFFP_GAIN_BASE_MUST_RESUME=0` — the
  `self_only__none` form), `MFFP_LADDER_SCALER=per_level` everywhere (under
  which row share *is* effective loss weight — B3 F-T1.2). Two additive,
  **default-inert** env knobs:
  1. **`MFFP_ROW_WEIGHT_MODE`** in {`natural`, `uniform_distinct`,
     `ladder_replication`}, default `natural` (= `weights=None`; the existing
     mean-1 per-row `weights` path in `_train` is reused, stage 1 only).
     `uniform_distinct`: `w_i = 1/copies_i` where `copies_i` counts stage-1
     rows sharing `(cond, f_tgt, Y)` up to the `f_src` tag — a provable no-op
     on `self_only`, and on `allpairs` it restores `self_only`'s level shares
     0.571/0.286/0.114/0.0286. `ladder_replication`: `w_i = 1 + #levels
     strictly below the row's target level` — on `self_only` it reproduces
     `allpairs`' shares 0.357/0.357/0.214/0.0714. `allpairs +
     ladder_replication` squares the schedule and is asserted **unsupported**.
  2. **`MFFP_STAGE1_EPOCH_SCALE`** (float, default `1.0`):
     `stage1_epochs = max(1, round(scale * args.epochs))` with the stage-1
     `CosineAnnealingLR` given `T_max = stage1_epochs`, so each arm runs a
     *complete* anneal over its own budget and the only thing that changes is
     the number of gradient steps. Stage 2 (HF finetune, 5 rows, eval query
     form) always runs `args.epochs` and is never weighted. Tier-relative, so
     the contract tier scales without hard-coding 200.

  **Six arms, one SLURM job, seed 0, serial, in this order** (steps = stage-1
  gradient steps at bs=16; 280/16 -> 18/epoch, 175/16 -> 11/epoch):

  | # | tag | LADDER_MODE | ROW_WEIGHT_MODE | S1 SCALE | s1 epochs | steps/ep | total steps | role |
  |---|---|---|---|---|---|---|---|---|
  | A0 | `so_nat_short` | self_only | natural | 1.0 | 200 | 11 | 2200 | CONTROL — must reproduce B3's 0.021913 |
  | A1 | `ap_rep_long` | allpairs | natural | 1.0 | 200 | 18 | 3600 | CONTROL — must reproduce B3's 0.034264 |
  | A2 | `ap_rep_short` | allpairs | natural | 0.611111 | 122 | 18 | 2196 | **DECISIVE-STEP** — long arm at matched steps |
  | A3 | `so_nat_long` | self_only | natural | 1.636364 | 327 | 11 | 3597 | mirror step control — short arm scaled up |
  | A4 | `so_rep_short` | self_only | ladder_replication | 1.0 | 200 | 11 | 2200 | **DECISIVE-WEIGHT** — allpairs' weighting, no duplicates, matched steps |
  | A5 | `ap_nat_short` | allpairs | uniform_distinct | 0.611111 | 122 | 18 | 2196 | CLOSURE — matches A0 on weighting AND steps; residual = `f_src` exposure + duplicate-minibatch noise |

  Matched-step accuracy: A2 2196 vs A0 2200 (−0.18 %), A3 3597 vs A1 3600
  (−0.08 %); both inside the ±1 % tolerance the analyzer asserts. A2 and A3 are
  the websearcher's **two** matched controls (*"Run BOTH matched controls, not
  one"*): read the long arm off at the short arm's update count, and scale the
  short arm up to the long arm's.

  **Build traps (must be honoured; stated so the builder needs no rediscovery)**:
  (i) the ckpt key **must** become
  `<ckpt_dir>/mode_<MODE>__scal_<SCALER>__w_<WMODE>__s1x_<SCALE>/last.pt` with
  the `same_cfg` meta guard extended to both new knobs — otherwise A1 and A2
  (identical mode+scaler) collide and A2 silently resumes A1's finished
  checkpoint; (ii) all **nine** env knobs ride ONE `--env` flag (B3 BUILD TRAP
  2: `--env` is `nargs="*"` without `action="append"`, so a second flag
  silently overwrites the first); (iii) per-arm `ROUND1_EVAL_RESULTS` (B3 BUILD
  TRAP 1); (iv) per-arm `[env-guard]` re-assertion from the shipped JSON — any
  `*_source == "default"` aborts the job; (v) re-run B3's
  `scratchpad/resume_drill.sh` against the new ckpt key before submit.

  **Mandatory score-neutral instrumentation** in every arm's result JSON:
  `row_weight_mode` + source, `stage1_epoch_scale` + source,
  `stage1_epochs_resolved`, `stage1_steps_per_epoch`, `stage1_total_steps`,
  per-target-level distinct-row counts and duplicate multiplicities, and the
  **realized effective level weight shares** (sum of `w_i` per target level /
  total). Self-consistency asserts: A4 shares == A1 shares and A5 shares == A0
  shares to 1e-6; A2/A3 realized total steps within 1 % of their match targets.

- **Recipe**:

```json
{
  "base_family": "mf_fno_ladder_gain",
  "base_commit": "57c24576abe6b045b837ccfd55f331a80e3f8b05",
  "family_dir": "models_r1/mf_fno_ladder_attrib",
  "datasets": "ifc_poisson",
  "epochs": 200,
  "seeds": [0],
  "env": {
    "MFFP_LADDER_MODE": "self_only",
    "MFFP_LADDER_SCALER": "per_level",
    "MFFP_ROW_WEIGHT_MODE": "natural",
    "MFFP_STAGE1_EPOCH_SCALE": "1.0",
    "MFFP_GAIN_HEAD": "none",
    "MFFP_GAIN_LAMBDA_GRID": "1e-6,1e-5,1e-4,1e-3,1e-2,1e-1,1,10",
    "MFFP_GAIN_CLIP": "0.5,2.0",
    "MFFP_GAIN_FSRC": "eval",
    "MFFP_GAIN_BASE_MUST_RESUME": "0",
    "_arms": [
      {"tag": "so_nat_short", "MFFP_LADDER_MODE": "self_only", "MFFP_ROW_WEIGHT_MODE": "natural", "MFFP_STAGE1_EPOCH_SCALE": "1.0", "s1_epochs": 200, "s1_steps": 2200, "role": "CONTROL (reproduce B3 self_only__none 0.021913)"},
      {"tag": "ap_rep_long", "MFFP_LADDER_MODE": "allpairs", "MFFP_ROW_WEIGHT_MODE": "natural", "MFFP_STAGE1_EPOCH_SCALE": "1.0", "s1_epochs": 200, "s1_steps": 3600, "role": "CONTROL (reproduce B3 base__none 0.034264)"},
      {"tag": "ap_rep_short", "MFFP_LADDER_MODE": "allpairs", "MFFP_ROW_WEIGHT_MODE": "natural", "MFFP_STAGE1_EPOCH_SCALE": "0.611111", "s1_epochs": 122, "s1_steps": 2196, "role": "DECISIVE-STEP (long arm read at matched steps)"},
      {"tag": "so_nat_long", "MFFP_LADDER_MODE": "self_only", "MFFP_ROW_WEIGHT_MODE": "natural", "MFFP_STAGE1_EPOCH_SCALE": "1.636364", "s1_epochs": 327, "s1_steps": 3597, "role": "mirror step control (short arm scaled up)"},
      {"tag": "so_rep_short", "MFFP_LADDER_MODE": "self_only", "MFFP_ROW_WEIGHT_MODE": "ladder_replication", "MFFP_STAGE1_EPOCH_SCALE": "1.0", "s1_epochs": 200, "s1_steps": 2200, "role": "DECISIVE-WEIGHT (allpairs weighting, no duplicates, matched steps)"},
      {"tag": "ap_nat_short", "MFFP_LADDER_MODE": "allpairs", "MFFP_ROW_WEIGHT_MODE": "uniform_distinct", "MFFP_STAGE1_EPOCH_SCALE": "0.611111", "s1_epochs": 122, "s1_steps": 2196, "role": "CLOSURE (matches A0 on weighting AND steps)"}
    ],
    "_primary_contrast": "ap_rep_short (A2) and so_rep_short (A4), each against the A0/A1 controls — fixed before submit (ADR 0007 guardrail); NO arm is promoted to the leaderboard",
    "_non_claimable_arms": ["ap_rep_short", "so_nat_long", "ap_nat_short"],
    "_design": "2x2 controlled factorial (per-level loss weighting x stage-1 gradient-step budget) plus one closure arm, all on ifc_poisson, seed 0, head OFF. Two new default-inert env knobs: MFFP_ROW_WEIGHT_MODE {natural|uniform_distinct|ladder_replication} (per-row stage-1 loss weight, mean-1, via the family's existing _train(weights=) path) and MFFP_STAGE1_EPOCH_SCALE (float; stage1_epochs = max(1, round(scale*args.epochs)) with the stage-1 CosineAnnealingLR T_max set to stage1_epochs, so every arm completes its own anneal). Stage 2 (HF finetune on the 5 HF rows, eval query form) runs args.epochs unweighted in EVERY arm. The CLI --epochs stays at the tier value (200 smoke / 2 contract) for every arm.",
    "_sweep": "ONE SLURM job, seed 0, six score_panel.py calls in table order, each with a single --env carrying all nine knobs; export ROUND1_EVAL_RESULTS=<outputs>/eval/results_<tag> per arm. NO base staging/sharing (unlike B3): every arm trains its own base from scratch, MFFP_GAIN_BASE_MUST_RESUME=0 throughout.",
    "_ckpt_key": "MANDATORY CHANGE: <ckpt_dir>/mode_<MODE>__scal_<SCALER>__w_<WMODE>__s1x_<SCALE>/last.pt, with the same_cfg meta guard extended to row_weight_mode and stage1_epoch_scale. Without it A1 and A2 (identical mode+scaler) collide and A2 silently resumes A1's finished checkpoint.",
    "_contract_check": "before submit, contract tier (--epochs 2) on ifc_poisson for all SIX arms, verifying: every *_source == env:MFFP_*, the six ckpt keys are distinct, stage1_epochs_resolved == max(1, round(scale*2)), the realized level weight shares match the expected tables (A4 == A1, A5 == A0, to 1e-6), and allpairs+ladder_replication aborts. Guard set NOT owed: this card claims no panel win (program.md §2.3); B3's guard debt is unchanged and remains owed by the confirmation pass. Contract numbers are plumbing, never results.",
    "_source": "vendor models_r1/mf_fno_ladder_gain from branch round1/exp-s1_poisson-B3 @ 57c24576abe6b045b837ccfd55f331a80e3f8b05 into models_r1/mf_fno_ladder_attrib (record sha256-16 of backbone.py, model.py, gain_head.py, smoke_eval.py, manifest.json, INSPIRATION.md before and after). akash/** and factory_root/{eval,baselines,references,scripts,data} are never touched.",
    "_cost": "~6.7 min GPU: 15989 stage-1 steps total + 6x200 stage-2 steps at ~19 ms/step (B3 measured 72.5 s for 3600+200 steps), plus ~12 s/arm eval overhead. B3's 5-arm job ran in 2m28s.",
    "_sbatch": {
      "directives": [
        "#SBATCH --job-name=r1-s1_poisson-B4",
        "#SBATCH --partition=gpu",
        "#SBATCH --nodes=1",
        "#SBATCH --ntasks=1",
        "#SBATCH --cpus-per-task=4",
        "#SBATCH --gres=gpu:h100:1",
        "#SBATCH --mem=32G",
        "#SBATCH --time=01:00:00",
        "#SBATCH --requeue",
        "#SBATCH --exclude=hpc-93-36",
        "#SBATCH --output=/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch_outputs/round1/s1_poisson/B4/slurm/%x_%j.out",
        "#SBATCH --error=/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch_outputs/round1/s1_poisson/B4/slurm/%x_%j.err"
      ],
      "gres_rationale": "ADR 0005 (H100 switch); --time=01:00:00 is ~9x the 6.7 min estimate, tighter than B3's 02:00:00 because there is no head-fit stage.",
      "submit_wrapper": "scripts/submit.sh: set -euo pipefail; mkdir -p <OUT_DIR>/{slurm,eval,training}; jid=$(sbatch --parsable --job-name=\"r1-s1_poisson-B4-s0\" \"$SCRIPT_DIR/01_train_eval.sh\" 0). NEVER sbatch 01_train_eval.sh directly (the in-file --job-name omits -s{seed}, which the maintainer matches on).",
      "body": [
        "set -euo pipefail; SEED=\"${1:?usage: 01_train_eval.sh <seed>}\"",
        "PROJECT_ROOT=/resnick/groups/Hippo/ezeng/mf_field; ROUND_ROOT=$PROJECT_ROOT/mffp_autoresearch/round1",
        "WORKTREE=$ROUND_ROOT/worktrees/s1_poisson/B4; OUT_DIR=$PROJECT_ROOT/mffp_autoresearch_outputs/round1/s1_poisson/B4; FAMILY=mf_fno_ladder_attrib",
        "ARM_TAGS=(so_nat_short ap_rep_long ap_rep_short so_nat_long so_rep_short ap_nat_short)",
        "ARM_MODES=(self_only allpairs allpairs self_only self_only allpairs)",
        "ARM_WMODE=(natural natural natural natural ladder_replication uniform_distinct)",
        "ARM_S1X=(1.0 1.0 0.611111 1.636364 1.0 0.611111)",
        "DATASET=ifc_poisson; EPOCHS=200; SCALER=per_level; HEAD=none; MRESU=0; LAMBDA_GRID=1e-6,1e-5,1e-4,1e-3,1e-2,1e-1,1,10; CLIP=0.5,2.0; FSRC=eval",
        "source \"$PROJECT_ROOT/.venv/bin/activate\"; mkdir -p \"$OUT_DIR/eval\" \"$OUT_DIR/slurm\" \"$OUT_DIR/training\"",
        "echo \"[$(date)] host=$(hostname) seed=$SEED gpu=$(nvidia-smi -L | head -1 || echo none)\"",
        "for i in \"${!ARM_TAGS[@]}\"; do TAG=${ARM_TAGS[$i]}; MODE=${ARM_MODES[$i]}; WMODE=${ARM_WMODE[$i]}; S1X=${ARM_S1X[$i]};",
        "  export ROUND1_EVAL_RESULTS=\"$OUT_DIR/eval/results_${TAG}\"; mkdir -p \"$ROUND1_EVAL_RESULTS\";",
        "  python \"$ROUND_ROOT/eval/score_panel.py\" --family_dir \"$WORKTREE/models_r1/$FAMILY\" --datasets \"$DATASET\" --epochs \"$EPOCHS\" --seed \"$SEED\" --out \"$OUT_DIR/eval/result_${DATASET}_${TAG}_s${SEED}.json\" --env \"MFFP_LADDER_MODE=${MODE}\" \"MFFP_LADDER_SCALER=${SCALER}\" \"MFFP_ROW_WEIGHT_MODE=${WMODE}\" \"MFFP_STAGE1_EPOCH_SCALE=${S1X}\" \"MFFP_GAIN_HEAD=${HEAD}\" \"MFFP_GAIN_LAMBDA_GRID=${LAMBDA_GRID}\" \"MFFP_GAIN_CLIP=${CLIP}\" \"MFFP_GAIN_FSRC=${FSRC}\" \"MFFP_GAIN_BASE_MUST_RESUME=${MRESU}\";",
        "  # [env-guard] python heredoc: assert ladder_mode_source/ladder_scaler_source/row_weight_mode_source/stage1_epoch_scale_source/gain_head_source all == env:MFFP_*, gain_head_applied == false, stage1_epochs_resolved and stage1_total_steps match the card table, level weight shares match the expected vector, and the ckpt key contains __w_${WMODE}__s1x_${S1X}; abort on any mismatch.",
        "done; echo \"[$(date)] done\"; for TAG in \"${ARM_TAGS[@]}\"; do echo \"--- $TAG\"; cat \"$OUT_DIR/eval/result_${DATASET}_${TAG}_s${SEED}.json\"; done"
      ],
      "idempotence": "Safe to requeue: all nine knobs enter code_hash so the six arms have distinct eval-cache keys, and an unfinished arm resumes mid-stage from its own extended ckpt key."
    }
  }
}
```

- **Expected outcome**:

  All comparisons are in skill (nRMSE / paper_bar 0.036, ADR 0002; **lower is
  better**), `provisional-single-seed` (ADR 0004). Reference points:
  `state/noise_floor.json.ifc_poisson.min_claimable_effect` = **0.23990756
  skill** (= 0.0086367 nRMSE); B3 measured A0-equivalent **0.6087** and
  A1-equivalent **0.9518**, gap **0.3431 = 1.43x floor**. Thresholds are
  computed from **this card's own re-run controls**, each exactly one floor
  away, so every verdict clears the floor by construction:

  - `T_recover   = skill(A1) − 0.2399` (= 0.7119 at B3's values; nRMSE 0.025628)
  - `T_no_recover = skill(A0) + 0.2399` (= 0.8486 at B3's values; nRMSE 0.030550)
  - **UNRESOLVED** dead band `(T_recover, T_no_recover)` — 0.1367 wide,
    sub-floor by construction, pre-registered as *not a result*.

  Validity gate (not a clause): A0 must land within ±10 % of B3's 0.021913
  (0.019722–0.024104) and A1 within ±10 % of 0.034264 (0.030838–0.037690); B3
  reproduced B2's control to 0.04 % on a re-train, so this is generous.

  **Pre-registered exhaustive outcome table** (A2 = step-only change from A1;
  A4 = weight-only change from A0; A3 mirrors A2; A5 closes):

  | # | A2 `ap_rep_short` | A4 `so_rep_short` | A3 `so_nat_long` | verdict | what it changes |
  |---|---|---|---|---|---|
  | **O1 STEP STORY** | RECOVERS (≤ T_recover) | does not degrade (≤ T_recover) | degrades (≥ T_no_recover) | the `self_only` win is an **optimization-budget** effect: 2200 stage-1 steps beat 3600 at fixed weighting | round report attributes the gap to schedule, NOT to dropping cross pairs; no cross-stream "audit your replication schedules" recommendation; a step-budget arm becomes a batch-5/confirmation candidate; if the 3-seed slate must choose between `self_only__none` and `gain__ladder_level_intercept`, **prefer the gain head** (closed-form, zero training, compute-matched by construction) |
  | **O2 WEIGHT STORY** | does not recover (≥ T_no_recover) | degrades (≥ T_no_recover) | does not degrade (≤ T_recover) | the win is a **condition-space / effective-N (level-weighting)** effect at fixed compute | round report states the transferable rule ("the replication schedule inverts the ladder's information ordering"), and the cross-stream warning fires for every ladder family (`heat_local` audits REPLICATION_ONLY too); if the slate must choose, **prefer `self_only__none`** |
  | **O3 MIXED** | partial (dead band) | partial (dead band) | any | both factors contribute; neither is sufficient alone | claim narrows to "jointly necessary"; slate **unchanged** (run both arms, rank neither) |
  | **O4 NEITHER** | does not recover | does not degrade | does not degrade | neither weighting nor steps reproduces the gap inside a row set → the cause is `f_src`-tag exposure and/or duplicate-minibatch gradient noise; **A5 adjudicates**: A5 ≤ T_recover ⇒ a weight×step interaction after all; A5 ≥ T_no_recover ⇒ **`f_src` exposure is a new mechanism** and the batch-5 direction | slate **unchanged**; a new s1 open question is opened |
  | **O5 BOTH-SUFFICIENT** | RECOVERS | degrades | any | each single-factor change alone reproduces the full gap → non-additive on this ladder | reports "either factor alone suffices"; does not disambiguate, but closes *"is it data?"* with a definitive **no**; slate **unchanged** |
  | **O6 VOID** | — | — | — | A0 or A1 outside its ±10 % validity band | nothing is attributed; debug the vendoring; card is void |

  **My prior**: O2 at ~60 % — B3 F-T1.6 (allpairs fits its 5 HF rows **1.34x
  tighter** and generalizes **1.56x worse**, test/train 7.12 vs 3.39) is the
  signature of 2.5x-upweighting a 5-condition level, and turn 3's coverage
  predictor (0.24828 at level 8 vs 0.39939 at level 64) says condition coverage
  is what predicts HF accuracy on this ladder; O1 ~20 %, carried entirely by
  the fetched rank-reversal precedent; O3/O4/O5 ~20 %.

  **Effect sizes vs the anchor and the floor**: the card produces no leaderboard
  claim, so `state/anchors/s1_poisson.json` (1.5656 skill,
  `mf_fno_transfer_film`) is not the operative threshold — every arm here sits
  far below it (0.61–0.95). The operative comparison is the B3 pair, and every
  band edge is exactly **1.00x the certified floor 0.23990756** away from a
  measured control; the 0.3431 gap being only 1.43x the floor is precisely why
  the dead band exists and is pre-registered rather than discovered.

  **Pre-registered limitation (card part 4, one line — websearch item 5)**:
  duplication-as-weighting is an approximation whose published caveat fires
  here — *"if two or more copies of the data point x_i appear in a minibatch"*
  (https://ar5iv.labs.arxiv.org/html/1806.02512) — and at bs=16 with the 5 HF
  rows replicated x4 duplicate co-occurrence is frequent, so `allpairs` is not
  exactly `self_only`-with-weights even at matched steps; A4/A5 match the level
  weight shares but **not** the gradient-noise structure, and A5-vs-A0 is our
  only bound on that residual. Second pre-registered limitation: the two
  step-matched arms match total steps but run a cosine anneal stretched or
  compressed over their own stage-1 epoch count, so LR *granularity* per step
  differs (one LR update per 18 vs 11 steps).

  **D-C remark to record verbatim in the card** (program.md §13.3 humility — a
  remark, not a contribution): *"We could not find this reported: on an
  aligned, nested fidelity ladder with conditions taken from the target level,
  all-ordered-pairs (all2all-style) cross-level supervision degenerates into
  pure replication — the cross rows duplicate the self rows up to the
  source-fidelity tag — so the construction is a per-level reweighting schedule
  (x1/x2/x3/x4 here), not data amplification. POSEIDON's O(K^2) amplification
  rests on the semi-group property with a source-varying input
  (https://ar5iv.labs.arxiv.org/html/2405.19101), which is absent under
  `cond_from = target`; `mf_fno_allpairs/manifest.json` nonetheless advertises
  'amplifies the data O(L^2)' — the manifest, not the paper, is what B3
  falsified. Three independently worded searches found no source stating this;
  it is an observation about a construction, not a method."*

- **Expected falsification**: the motivating "condition-space effective-N /
  level-weighting" hypothesis is falsified if the weight-only arm A4
  (`so_rep_short`: `self_only` rows and steps, `allpairs` level weight shares)
  fails to degrade — i.e. lands at skill ≤ `skill(A0) + 0.23990756` — while the
  step-only arm A2 (`ap_rep_short`: `allpairs` rows and weighting at
  `self_only`'s 2200 stage-1 steps) recovers to skill ≤ `skill(A1) −
  0.23990756`, which would attribute the round's best claimable `ifc_poisson`
  number to the optimization budget rather than to the ladder's information
  ordering (outcome O1).

- **Prior-art verdict quoted** (verbatim from
  `websearches/s1_poisson/batch_4/report.md`):
  - D-A: **"`preempted` (ML-general methodology) — open only as an in-repo
    measurement"**; *"Epoch-matched comparisons 'conflate algorithmic quality
    with compute' (8x updates/epoch), with BOTH matched controls constructed —
    https://arxiv.org/html/2606.10321v1 · https://arxiv.org/abs/2606.10321 ·
    'obscuring the source of empirical gains' + the Melis precedent —
    https://ar5iv.labs.arxiv.org/html/1807.03341 · dedup changes required train
    steps — https://arxiv.org/abs/2107.06499 ,
    https://arxiv.org/html/2407.06654"*; *"The card must claim the
    *measurement*, never the *method*. Note the documented failure mode: in
    https://arxiv.org/html/2606.10321v1 the epoch-matched ranking **reversed**
    under step-matching."*
  - D-B: **"`preempted` (MF-general)"**; *"Per-fidelity loss weights, incl.
    upweighting the scarce HF level: 'L_total = L_LF + λ_HF L_HF + ...' —
    https://arxiv.org/html/2602.01176v1 · duplication-as-weighting is named and
    published ('importance duplication', with discretization /
    minibatch-co-occurrence caveats) — https://ar5iv.labs.arxiv.org/html/1806.02512
    · hard-dedup vs soft-reweight framed as alternatives —
    https://arxiv.org/html/2407.06654"*; *"The knob is old."*
  - D-C: **"`novel` (narrow) — 'not previously reported', never 'novel
    method'"**; *"Three independently worded searches ... found **no source
    stating that all-pairs / cross-level fidelity supervision on an aligned
    nested ladder degenerates into pure replication** ... it is a one-line
    remark, not a contribution."* (nearest neighbours:
    https://ar5iv.labs.arxiv.org/html/2405.19101 ,
    https://arxiv.org/html/2503.17941v1 ,
    https://ar5iv.labs.arxiv.org/html/1806.02512)

- **Immutables self-check**: **pass (10/10)**. Item 6 was flagged during design
  and resolved in-place rather than by revision: the CLI `--epochs` stays at
  the tier value (200 smoke / 2 contract) for every arm and stage 2 is
  identical everywhere; `MFFP_STAGE1_EPOCH_SCALE` re-times an **internal stage
  schedule**, which §5 lists under "What CAN be changed" (*"training procedure
  ... hyperparameters"*) and for which the family already has precedent (B3 set
  stage-2 finetune epochs to `args.epochs` where the base family used
  `epochs // 2`); the three arms with scale ≠ 1.0 (A2, A3, A5) are declared
  **non-claimable measurements** in `recipe.env._non_claimable_arms`, so no
  leaderboard number is ever produced at an off-tier budget. Full
  positive-evidence text for all 10 items:
  [iteration_1.md](iteration_1.md) § "Immutables self-check".

- **Anchor reference**: `null` (gap stream — own-stream anchor implicit,
  program.md §4.5).

- **Source iteration**: [iteration_1.md](iteration_1.md)

## Reopen candidates

| Candidate | Verdict (retry/drop) | Eased conditions | Source iteration |
|---|---|---|---|
| *(none — `grep -l '"reopen_candidate": true'` over every card in the round returns no files; s1-B1/B2/B3 are all `status: complete`, `reopen_candidate: false`)* | n/a | n/a | [iteration_1.md](iteration_1.md) |

## Skipped slot

Not applicable — the slot is filled.

## Summary table

| Slot | Category | One-liner | Status |
|---|---|---|---|
| s1_poisson batch 4 | compute-vs-weighting attribution (2x2 factorial) | Six-arm `ifc_poisson` factorial over per-level loss weighting x stage-1 gradient-step budget, with both matched controls, to decide whether `self_only__none`'s 0.6087 is effective-N/weighting or 1.64x more gradient steps | filled (`model` card, diagnostic purpose, ~6.7 min GPU) |
