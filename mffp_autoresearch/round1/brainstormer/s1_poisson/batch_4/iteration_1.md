# Iteration 1 — `s1_poisson` batch 4 (self_only disambiguation slot)

## Design context considered

- `summary_so_far.md` §6 (unknowns 1-6), especially the three coupled
  differences (a) level weighting, (b) stage-1 steps, (c) `f_src` exposure.
- Prior-art verdicts D-A / D-B / D-C, quoted verbatim in the report.
- Anchor `state/anchors/s1_poisson.json` = 1.5656334312786022 skill
  (`mf_fno_transfer_film`); this card is far below it either way (0.61-0.95),
  so the anchor is not the binding threshold - the **B3-measured pair** is.
- Noise floor `state/noise_floor.json.ifc_poisson.min_claimable_effect`
  = **0.23990756041925798 skill** = 0.0086367 nRMSE (paper_bar 0.036).
- The §5 immutables block (self-check below) and the three pre-falsified
  levers (WNO backbone swap; LF low-mode freezing; diffusion prior).
- Substrate facts read out of
  `worktrees/s1_poisson/B3/models_r1/mf_fno_ladder_gain/smoke_eval.py`:
  - `SMOKE = dict(..., batch_size=16, lr_pretrain=1e-3, lr_finetune=3e-4, ...)`;
    280/16 -> **18** steps/epoch, 175/16 -> **11** steps/epoch.
  - `_train(...)` **already carries a per-row `weights` argument** (mean-1,
    `loss = (wb * (pred - yb) ** 2).mean()`), used today only by the
    `shared_reweight` scaler; `weights is None` is the bit-preserving path.
  - `CosineAnnealingLR(opt, T_max=max(epochs,1))`, stepped once per epoch.
  - Stage 2 (HF finetune on the 5 HF rows, eval query form) is identical in
    every arm and uses `args.epochs`.
  - ckpt key today is `<ckpt_dir>/mode_<MODE>__scal_<SCALER>/last.pt` with a
    meta guard on (epochs, grid, ladder_mode, ladder_scaler).
- B3's build scripts (`scripts/01_train_eval.sh`): BUILD TRAP 1 (per-arm
  `ROUND1_EVAL_RESULTS`), BUILD TRAP 2 (`--env` has `nargs="*"` without
  `action="append"`, so **all knobs must ride ONE `--env` flag**), the
  `[env-guard]` post-arm assertion pattern, `#SBATCH` block verbatim.

## Proposal reasoning (alternatives weighed and rejected)

**R1. What question is worth 200 epochs here?** None of the modelling
directions are: the level channel is spent (post-head level rel-err 0.00879;
remaining calibration ceiling 0.045x floor), the head must not be stacked on
`self_only` (measured 0.021913 -> 0.035890), and K>1 is priced below
resolution. The only live debt is attribution of the round's **best claimable
`ifc_poisson` number**, which the end-of-round confirmation slate is about to
spend 3 seeds on. That settles the slot.

**R2. Rejected: the literal "allpairs-dedup" arm.** The orchestrator's sketch
(ii) was "duplicates removed -> self_only's data, allpairs' schedule". Read
against F-T1.1, removing the 105 duplicate rows from `allpairs` yields
*exactly* the `self_only` row set, hence exactly 11 steps/epoch - so a dedup
arm **is** A0 and measures nothing. The schedule cannot be held at 18
steps/epoch while the rows are deduplicated. Rejected, and replaced by the two
constructions that *do* decouple the factors: an explicit per-row weight knob
(weighting without replication) and an explicit stage-1 step budget (steps
without changing the rows).

**R3. Rejected: epoch scaling of the CLI `--epochs` (327 for the short arm).**
This is the websearcher's control #1 and it is the natural reading of "scale
the short arm's epochs up", but `--epochs` is the tier budget (§2.4, immutable
6) and it also drives stage 2. Instead I scale **only the stage-1 (joint)
schedule** through a new env knob, keeping `--epochs 200` and stage 2 identical
in every arm. Precedent that internal stage schedules are card-settable
training procedure (§5 "What CAN be changed": *"training procedure ...
hyperparameters"*): the B3 family already sets stage-2 finetune epochs =
`args.epochs` where the base family used `epochs // 2`. Consequence, declared
up front: arms with stage-1 scale != 1.0 are **non-claimable measurements**,
never leaderboard entries.

**R4. Rejected: zero-GPU early read of B3's checkpoints** (sketch (iv)).
`_save_ckpt` overwrites a single `last.pt` (`CKPT_SAVES_PER_STAGE = 5` controls
frequency, not retention), and B3's stage-1 checkpoints were overwritten by
stage 2 and then by the final `stage="done"` save. There is no epoch-122
artifact on disk. The early read must be re-run - which costs ~40 s, so the
"free" version is not needed.

**R5. LR-schedule decision (pre-registered, not discovered).** Two ways to
realize a shorter stage-1: (i) stop at epoch 122 with `T_max` still 200
(truncated anneal - LR never reaches eta_min), or (ii) run a *complete* cosine
over 122 epochs (`T_max` = the arm's own stage-1 epochs). I choose **(ii)**:
it makes every arm a completed training run whose LR-vs-progress curve is
identical, so the only thing that changes is the number of gradient steps -
which is precisely the factor under test. It is also what the fetched precedent
does on its scaled-up arms ("train the short arms for 800 epochs"). Residual,
pre-registered: LR *granularity* per step differs (one LR update per 18 vs 11
steps); second-order, and it is stated as a limitation rather than measured.

**R6. Rejected: a 3-arm card.** With a 0.3431 skill gap and a 0.2399 floor,
one seed can only resolve "clears one floor from one control". A single
step-arm would leave the mirror direction unmeasured and any dead-band landing
uninterpretable. The 2x2 factorial (weighting x steps) with **both**
single-factor directions gives two independent tests of each story, exactly as
the websearcher demands ("Run BOTH matched controls, not one"). At ~40-75 s per
arm this costs minutes.

**R7. Why a closure arm (A5).** Factor (c), `f_src`-tag exposure, cannot be
removed from `allpairs` or added to `self_only` without changing the rows. A5
= allpairs rows + `uniform_distinct` weights + short step budget matches A0 on
*both* measured factors and differs only by (c) plus duplicate-in-minibatch
gradient noise. It converts an unbounded confound into a measured residual.

**R8. Rejected: making the weight knob the claim.** D-B is `preempted
(MF-general)`. The knob is an **instrument**: the card claims a measurement
about `self_only`'s win, never a weighting method.

**R9. Card type.** `model`. §4.3 defines `diagnostic` as *"a **measurement**,
no training"*; this card trains six stage-1 bases, so calling it a diagnostic
would misuse the type and mislead the maintainer's tier accounting. It is a
diagnostic-*purpose* model card: no arm is proposed as a candidate model, no
arm is promoted, and ADR 0007's propose-many does not apply (spec-pre-directed
slot with no candidate pool - all six arms are controls in one pre-registered
factorial, and all six run directly at 200 epochs; the contract-tier run is
plumbing only, per ADR 0007 "Screening numbers are NEVER reportable results").
ADR 0007's binding guardrail is satisfied: the decisive contrast (A2 and A4
against the A0/A1 controls) is fixed here, before submit.

## Proposal

**Category**: compute-vs-weighting attribution of the `self_only` win on the
ifc fidelity ladder (2x2 controlled factorial, in-repo measurement).

**Card type**: `model` (diagnostic purpose; see R9).

**Motivation**: quotes D-A verbatim (see report.md).

**Concrete config** - new family `models_r1/mf_fno_ladder_attrib`, vendored
from B3's build commit `57c24576abe6b045b837ccfd55f331a80e3f8b05`
(`models_r1/mf_fno_ladder_gain`), head OFF (`MFFP_GAIN_HEAD=none`) and
`MFFP_GAIN_BASE_MUST_RESUME=0` in every arm (the `self_only__none` form).
Two additive, default-inert env knobs:

1. **`MFFP_ROW_WEIGHT_MODE`** in {`natural`, `uniform_distinct`,
   `ladder_replication`}, default `natural` (= `weights=None`, bit-preserving).
   - `uniform_distinct`: `w_i = 1 / copies_i`, where `copies_i` is the number
     of stage-1 rows sharing row i's `(cond, f_tgt, Y)` up to the `f_src` tag
     (computed from the arm's own row set, the way
     `tools/ladder_pair_row_audit.py` does). On `self_only` all `copies_i = 1`,
     so it is a provable no-op there; on `allpairs` it restores `self_only`'s
     level shares exactly (0.571/0.286/0.114/0.0286).
   - `ladder_replication`: `w_i = 1 + #levels strictly below row i's target
     level` (the multiplicity `allpairs` induces, F-T1.2). On `self_only` this
     reproduces `allpairs`' level shares exactly (0.357/0.357/0.214/0.0714).
     Combination `allpairs + ladder_replication` squares the schedule and is
     **asserted unsupported**.
   - Weights are normalized to mean 1 and passed to the existing
     `_train(..., weights=...)` path (stage 1 only; stage 2 never weighted).
2. **`MFFP_STAGE1_EPOCH_SCALE`** (float, default `1.0`):
   `stage1_epochs = max(1, round(scale * args.epochs))`, and the stage-1
   `CosineAnnealingLR` gets `T_max = stage1_epochs` (R5). Stage 2 always runs
   `args.epochs`. Tier-relative by construction, so the contract tier scales
   without hard-coding 200.

**Arms (six, one job, seed 0, serial, this order)** - steps are stage-1
gradient steps at bs=16:

| # | tag | MODE | WEIGHT | S1 SCALE | s1 epochs | steps/ep | total steps | role |
|---|---|---|---|---|---|---|---|---|
| A0 | `so_nat_short` | self_only | natural | 1.0 | 200 | 11 | 2200 | CONTROL, must reproduce B3 0.021913 |
| A1 | `ap_rep_long` | allpairs | natural | 1.0 | 200 | 18 | 3600 | CONTROL, must reproduce B3 0.034264 |
| A2 | `ap_rep_short` | allpairs | natural | 0.611111 | 122 | 18 | 2196 | **DECISIVE-STEP**: long arm read at matched steps |
| A3 | `so_nat_long` | self_only | natural | 1.636364 | 327 | 11 | 3597 | mirror step control: short arm scaled up |
| A4 | `so_rep_short` | self_only | ladder_replication | 1.0 | 200 | 11 | 2200 | **DECISIVE-WEIGHT**: allpairs' weighting, no duplicates, matched steps |
| A5 | `ap_nat_short` | allpairs | uniform_distinct | 0.611111 | 122 | 18 | 2196 | CLOSURE: matches A0 on weighting AND steps; residual = `f_src` exposure + duplicate minibatch noise |

Matched-step accuracy: A2 2196 vs A0 2200 (-0.18 %); A3 3597 vs A1 3600
(-0.08 %). Both inside the +/-1 % tolerance the analyzer will assert.

**Build traps the builder must honour** (all inherited/derived, stated so the
card is buildable without rediscovery):
- **Ckpt key must be extended** to
  `mode_<MODE>__scal_<SCALER>__w_<WMODE>__s1x_<SCALE>/last.pt`, and the
  `same_cfg` meta guard must include both new knobs. Without this A1 and A2
  (same mode+scaler) collide and A2 silently resumes A1's finished
  checkpoint - a silent, result-destroying failure.
- All **nine** env knobs ride ONE `--env` flag (B3 BUILD TRAP 2).
- Per-arm `ROUND1_EVAL_RESULTS` (B3 BUILD TRAP 1).
- `[env-guard]` re-assertion per arm from the shipped JSON: every
  `*_source == "env:MFFP_*"`, never `default`, including the two new knobs.
- Re-run the resume drill (`scratchpad/resume_drill.sh`) against the new key.

**Mandatory score-neutral instrumentation** (each arm's result JSON):
`row_weight_mode` + source, `stage1_epoch_scale` + source,
`stage1_epochs_resolved`, `stage1_steps_per_epoch`, `stage1_total_steps`,
per-target-level distinct-row counts and duplicate multiplicities, and the
**realized effective level weight shares** (sum of w_i per target level /
total). Self-consistency asserts: A4's shares == A1's shares and A5's shares ==
A0's shares to 1e-6; A2/A3 realized total steps within 1 % of the match target.

**Expected outcome**: see the pre-registered outcome table in report.md. My
prior is O2 (weighting), ~60 %, because F-T1.6's signature (fits the 5 HF rows
1.34x tighter, generalizes 1.56x worse) is what 2.5x upweighting a
5-condition level produces, and turn 3's coverage predictor says condition
coverage is what predicts HF accuracy on this ladder; O1 (steps) ~20 %,
carried by the fetched rank-reversal precedent; O3/O4/O5 ~20 %.

**Expected falsification** (one sentence, in report.md).

**Anchor reference**: `null` (gap stream, §4.5).

**Limitation to state in card part 4, one line** (websearch item 5): the
duplication-as-weighting equivalence is an approximation whose published caveat
- *"if two or more copies of the data point x_i appear in a minibatch"*
(https://ar5iv.labs.arxiv.org/html/1806.02512) - fires here at bs=16 with the 5
HF rows replicated x4, so A4/A5 match `allpairs`/`self_only` on the level
weight shares but **not** on gradient-noise structure, and A5-vs-A0 is the only
bound on that difference.

**D-C remark to record verbatim in the card** (one line, program.md §13.3
humility - a remark, not a contribution): see report.md.

## Status

- Slot covered (one proposal, six arms, one card).
- Reopen candidates resolved: **none exist** for this stream (§5 of
  summary_so_far.md) - nothing to retry or drop.
- Immutables self-check: **pass (10/10)**, with item 6 flagged and resolved
  in-place (R3: CLI `--epochs` stays at the tier value; the stage-1 schedule
  is training procedure; arms with scale != 1.0 are declared non-claimable).
  Full evidence in report.md.

### Immutables self-check (positive evidence, all 10)

1. **Data read-only.** No dataset path is written; `build_rows` and
   `load_mf_dataset` are inherited unchanged; the two new knobs touch only the
   per-row loss weight vector and the stage-1 epoch count, never row content -
   `N_hf` stays 5 and stage 2 trains on exactly the same 5 HF rows as B3.
2. **Panel + guard set fixed.** `recipe.datasets = "ifc_poisson"` only, a
   member of the fixed panel; no dataset is added, removed, or re-split, and
   the card claims no panel win so no guard leg is owed (§2.3); B3's
   outstanding guard debt is unchanged and re-flagged for confirmation.
3. **Eval layer untouched.** Scoring is `python ${ROUND_ROOT}/eval/score_panel.py
   --family_dir ... --datasets ... --epochs ... --seed ... --out ... --env ...`
   invoked exactly as `worktrees/s1_poisson/B3/scripts/01_train_eval.sh` does;
   writes go only to `worktrees/s1_poisson/B4/**` and
   `mffp_autoresearch_outputs/round1/s1_poisson/B4/**`.
4. **One nRMSE definition.** Every arm's number comes from
   `finalize_and_write` via `score_panel.py`; the analyzer asserts
   `nrmse_def_hash == d3d0ade9191c13bacc40702f3eb26ad290e01641cacee22a1d2233b74c035850`
   (B3's, and the anchor's) across all six arms; only differences and ratios of
   published skills are formed by hand. The per-row loss weight changes the
   TRAINING loss only - explicitly free under §5 ("training loss is free; the
   SCORED metric is not").
5. **Contract CLI fixed.** `smoke_eval.py` keeps
   `--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed`; both new
   knobs are environment-only and are listed in `recipe.env`, so they enter
   `score_panel.py`'s `code_hash`/cache key exactly as B3's seven knobs did.
6. **Seeds and tier epochs fixed.** `recipe.seeds = [0]` (ADR 0004 strict
   single-seed) and `--epochs 200` (smoke tier) is passed to every arm, with a
   2-epoch contract pre-check; stage 2 runs `args.epochs` in every arm.
   `MFFP_STAGE1_EPOCH_SCALE` re-times an internal stage schedule - "training
   procedure" under §5's CAN-be-changed list, with in-family precedent (B3's
   stage-2 budget change from `epochs//2` to `args.epochs`) - and the three
   arms with scale != 1.0 (A2, A3, A5) are declared **non-claimable
   measurements** in card part 4, so no leaderboard number is produced at an
   off-tier budget. A0/A1/A4 are tier-legal 200-epoch runs.
7. **Guarded surfaces untouched.** The only new code is
   `worktrees/s1_poisson/B4/models_r1/mf_fno_ladder_attrib/` (a copy of the B4
   worktree's own `models_r1` B3 family) plus `worktrees/s1_poisson/B4/scripts/`;
   `factory_root/{eval,baselines,references,scripts,data}`, `factory.md` and
   `mf_field/akash/**` are read-only here (`akash/models/mf_fno_allpairs` was
   only read, by the websearcher).
8. **Checkpoint-resume.** The inherited `_save_ckpt`/`resume` path
   (`CKPT_SAVES_PER_STAGE = 5`, opt+sched+generator state saved) is preserved
   verbatim; the card requires the ckpt key and the `same_cfg` meta guard to be
   extended with `row_weight_mode` and `stage1_epoch_scale` so a requeue cannot
   cross arms, and requires B3's `resume_drill.sh` to be re-run on the new key
   before submit.
9. **Threshold vs noise floor.** Both decision thresholds sit exactly one
   certified floor away from a measured control:
   `T_recover = skill(A1) - 0.23990756 = 0.9518 - 0.2399 = 0.7119` and
   `T_no_recover = skill(A0) + 0.23990756 = 0.6087 + 0.2399 = 0.8486`
   (floor = `state/noise_floor.json.ifc_poisson.min_claimable_effect` =
   0.23990756041925798 skill = 0.0086367 nRMSE). Every verdict the card can
   issue therefore requires a move strictly larger than the floor; the interval
   (0.7119, 0.8486) is pre-registered as UNRESOLVED, not as a result.
10. **Not a pre-falsified lever.** The three §5 pre-falsified levers are the
    WNO backbone swap, LF low-mode freezing, and the diffusion prior; the
    nearest is *none of them* - this card changes no backbone, no spectral
    treatment and adds no generative prior. It adds no architecture at all: the
    model, optimizer, LR values, batch size and loss functional form are B3's
    verbatim, and only the stage-1 row weights and stage-1 epoch count vary.
