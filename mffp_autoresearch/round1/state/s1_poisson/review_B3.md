# code-reviewer — s1_poisson-B3 (attempt 1)

- **Verdict**: `SUGGEST` → card `status: reviewed_suggest`. **Submit as-is** (see
  the two submit-time instructions at the end).
- **Reviewed**: `git diff round1-substrate..57c24576abe6b045b837ccfd55f331a80e3f8b05`
  (43 files, +18167/−0); the full `smoke_eval.py` diff against the vendored B2
  source at `21fdcda`; all of `gain_head.py` (635 lines) line by line; all three
  `scripts/*`; all three `scratchpad/*.sh` drivers + `leak_positive_control.py` +
  `unit_gain_head.py`; all 12 committed evidence JSONs (5 score_panel + 1 guard +
  6 rich family JSONs); `resume_drill.log`, `unit_gain_head.log`,
  `contract_smoke.log`, `contract_smoke_guard_small.log`; both handoffs;
  `eval/score_panel.py` (read-only); B2's committed contract smoke at `21fdcda`;
  `brainstormer/s1_poisson/batch_3/iteration_1.md`; `state/noise_floor.json`;
  `state/timing_ledger.json`; `project.yaml`; program.md §5/§12.1;
  `resource/logistics/slurm_rules.md`; `experiment_cards/SCHEMA.md`;
  B2's card `review_notes` (precedent).
- **UTC**: 2026-07-30T06:15Z

## Verdict paragraph

The single most important claim on this card — that no test target can enter the
head fit or the lambda selection — survives an adversarial audit, and it survives
it by construction rather than by assertion. `grep -n "\bY_te\b|\btarget\b"
smoke_eval.py` returns exactly four live uses of the test target (`:661` creation,
`:834` flatten, `:851` taint, `:966`/`:985` npz save + final metric); it appears
nowhere in the training loop, nowhere in model selection, and nowhere downstream
of `firewall.taint()` except the scored metric. Every array that reaches the
estimator is checked at its earliest constructor (`_level_gain_rows` checks
`train_target`/`train_cond`; `build_fit_rows` checks `gain`/`conditions`;
`gain_head_report` checks `Z_test`), the lambda is a closed-form PRESS over those
same rows only (`gain_head.py:271-311`), and `gain_head.py` imports neither torch
nor the loaders so it cannot reach around its arguments. The three detectors are
independently drilled (all five evasion routes blocked, `unit_gain_head.log`) and
the end-to-end positive control is real: planting `train_HF := test_HF` at the
`load_mf_dataset` seam aborts with `TEST-TARGET LEAK at _level_gain_rows(level=64)`
(`resume_drill.log` step 7). The derived-scalar hole a digest cannot see is closed
by the second guard (`fit_rows_are_train_rows` = 100/50/20/5 against
`n_test_samples_never_in_fit` = 128, verified in all five arm JSONs). Everything
else reproduces under independent check: B2-continuity is bit-for-bit — the
committed `base__none` contract smoke is `0.2817404086094617` against B2's
`21fdcda:scratchpad/contract_smoke_allpairs__per_level.json` `0.2817404086094617`,
all 17 digits, same `nrmse_def_hash d3d0ade9…`; `backbone.py` is still
byte-identical to the guarded `akash/common/backbone.py` (`diff -q` clean) and
both `backbone.py` (`f56fa8029fad2ffb`) and `model.py` (`740ed992efcda53e`) are
unchanged post-edit, so all three code changes provably live in `smoke_eval.py`
plus the new `gain_head.py`; I re-ran the job script's env-guard block verbatim
against all five committed family JSONs and it passed on all five, printing
`paired base OK sha256=6bfb2f3ce68a3234` for G1–G3 (G4 has its own,
`34000d7016d2fc82`, as designed); and `bash -n` is clean on all six scripts. The
staged-`cp` deviation from `recipe._sweep`'s literal "shared ckpt root" is
justified (a literally shared `ROUND1_EVAL_RESULTS` would make each arm overwrite
the previous arm's mandatory per-level coefficient table, since
`score_panel.py::_run_one` derives `out_json` from family+dataset+epochs+seed
only) and the stated goal — byte-identical base weights across G0–G3 — is met and
independently verifiable per arm. The verdict is SUGGEST rather than PASS for one
reason only: `recipe.env._contract_check` names three guard datasets and only two
were actually run (`fluid`, `sharp__sod_1d`); `heat_local` was abandoned on the
login node. That is a disclosed, scripted, cheap gap on the *easiest* of the three
cases for this head (5 levels), not a defect in the build.

## Findings

| # | Question | Grade | Finding |
|---|---|---|---|
| Q1 | Card–implementation alignment | **PASS** | Every part-3 item traces to code. (1) `MFFP_GAIN_HEAD ∈ {none, ladder_level_intercept, ladder_pooled, hf_only}` default `none` = `gain_head.py:68-69`; the estimator `g_i = <p_i,y_i>/<p_i,p_i>` with `p = model([X,f_src,f_tgt=fnorm(f)]) * out_scale(f)` = `smoke_eval.py:_level_gain_rows` (`:595-604`); the card's claimed exactness at f=64 is *measured*, not assumed — `gain.level_scaler_hf_equals_scaler_hf: true`, both `0.0018356895307078958`, in all five arm JSONs, matching the card's literal constant; application `pred = pred_base * clip(exp(a_used + b·z), [0.5,2.0])` = `gain_head.py:608-612` + `smoke_eval.py:894-897`; LOO lambda on the arm's own fit rows = `gain_head.py:255-294`. (2) `self_only` = `arm_cross_pairs` early return (`:291-292`); the committed arm JSON reports `n_rows_total 175`, `cross_pairs []` — the card's exact number. (3) `MFFP_GAIN_BASE_MUST_RESUME` hard stop = `smoke_eval.py:783-795`. Fit-row split matches the card exactly: `ladder_level_intercept` `n_fit_rows 170` `fit_rows_from aux_levels_slope_plus_hf_train_intercept`, `hf_only` `n_fit_rows 5`. All nine mandatory instrumentation items present in the shipped `gain` payload (`per_level_coefficient_table` with a/b/r2/loo_r2/g/log_g stats for 8/16/32/64; `slope_cosines` incl. `pre_registered_threshold 0.7`; `estimators` with lambda + PRESS curve; `leave_one_level_out_aux` AND `_all_levels`; `a_hf_stderr`; `g_hat_test` with `clip_fraction`; `fsrc_sidecar` convention `self`; `pred_base` + `g_hat` in `preds_test.npz`; `std_log_g_over_b2_test_gain_std`). Arm order in `01_train_eval.sh:80-83` == `recipe.env._arms` order. No paraphrase drift. |
| Q2 | Recipe fidelity | **SUGGEST** | All seven `recipe.env` values appear verbatim in `01_train_eval.sh:86-90,136-141` (`MFFP_GAIN_LAMBDA_GRID=1e-6,1e-5,1e-4,1e-3,1e-2,1e-1,1,10`, `MFFP_GAIN_CLIP=0.5,2.0`, `MFFP_GAIN_FSRC=eval`, `MFFP_LADDER_SCALER=per_level`), all as values of ONE `--env` flag (build trap 2), and the committed JSONs echo all seven with `*_source == env:*` and none `default`. `datasets ifc_poisson` / `epochs 200` / `seed 0` / `family_dir` / `base_family mf_fno_ladder_norm` / `base_commit 21fdcda…` all match; the card's `recipe` block is byte-equivalent to the source iteration's. Zero new hyperparameters: the `SMOKE` dict, optimizer, scheduler and schedule are inherited untouched, and the five score-neutral builder choices are all declared in `build_notes[13]` — including the one that is *not* strictly score-neutral, standardizing `z = (X−μ)/σ` (ridge shrinkage is basis-dependent, so this does change the fitted `b`); that choice nevertheless traces to the source iteration line 228 ("`log g = a_f + b.X` (X standardised by ladder-row mean/std…)"), so it is card-sanctioned, not silent. **S1**: `recipe.env._contract_check` requires the guard-set contract leg on *three* datasets; only `fluid` and `sharp__sod_1d` ran (`contract_smoke_guard_small.json`). `heat_local` is disclosed as abandoned on the login node and the script defaults to the full `guard` expansion — the recipe step is incomplete, not falsified. **S2**: deviation from `_sweep`'s literal "shared ckpt root" (staged byte-identical `cp` + sha256 check + `MUST_RESUME=1` + post-arm sha equality assert). Disclosed in `build_notes[5]`; the stated goal is met and verified (G0–G3 all `6bfb2f3ce68a3234`). |
| Q3 | §5 immutable compliance | **PASS** | Diff touches only `models_r1/`, `scripts/`, `notes/`, `scratchpad/` — no `round1/eval/`, no `project.yaml`, no `program.md`, no ADRs, no subagent prompts. Guarded factory surfaces untouched: `diff -q models_r1/mf_fno_ladder_gain/backbone.py mf_field/akash/common/backbone.py` is clean, and nothing under `factory_root/{eval,baselines,references,scripts,data}`, `factory.md` or `akash/**` appears in the diff. No data regeneration; the head reads only the already-loaded train split and consumes no extra HF samples (level 64 uses exactly the dataset's 5 HF train rows). Scoring is routed through `${ROUND_ROOT}/eval/score_panel.py` in every arm — no hand-rolled metric and no direct `smoke_eval.py` number enters the card (`build_notes[6]` explicitly quarantines the drill's direct-invocation numbers). Seeds {0} in-round with {1,2} parked; epochs 200 = `tiers.smoke_epochs`; contract legs at 2 = `tiers.contract_epochs`. No pre-falsified lever re-proposed: the card is a post-hoc multiplicative calibration head, unrelated to the WNO backbone swap, LF low-mode freezing, or the diffusion prior. |
| Q4 | Contract compliance | **PASS** | `manifest.json` carries `name`/`description`/`supports ["ifc_raw","npz_l"]` (inherited verbatim from B2)/`frozen false`, plus `env_knobs`, `checkpoint_key` and a `test_target_firewall` clause. Exact 6-arg CLI at `smoke_eval.py:1018-1024` (`--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed`). `INSPIRATION.md` cites **all eight** `prior_art.citations` (1405.5170, 1609.07196, 1705.02956, 2207.00678, PMC10100049, 2605.26732, 2606.17513, 2210.03008 — grepped, all present). Checkpoint-resume implemented at `smoke_eval.py:741` (`last = ckpt_dir / "last.pt"` under the inherited `mode_<MODE>__scal_<SCALER>` sub-key, the build-trap-1 disambiguator carried unchanged from B1/B2, both of which passed review with it), with finished / mid-joint / mid-finetune branches and a meta guard on epochs/grid/mode/scaler. Drilled end to end: SIGTERM mid-joint → `[resume] joint[allpairs|per_level] continues from epoch 1/4` → exit 0; empty ckpt dir + `MUST_RESUME=1` → exit 1; mid-stage ckpt + `MUST_RESUME=1` → exit 1; wrong-mode ckpt → refused. Seeding: `torch.manual_seed(args.seed)`, `np.random.seed(args.seed)`, `torch.cuda.manual_seed_all` at `run()` entry; the head draws no RNG at all (pure numpy, no `np.random`), which is why the `none` arms are bit-preserving. |
| Q5 | SLURM script correctness | **SUGGEST** | `bash -n` run by the reviewer on all six scripts — all clean (`scripts/{01_train_eval,submit,submit_seeds_2_3}.sh`, `scratchpad/{resume_drill,run_contract_smoke,run_guard_contract}.sh`). `--partition=gpu` and typed `--gres=gpu:h100:1` match `project.yaml sbatch` exactly; `--nodes=1 --ntasks=1 --cpus-per-task=4 --mem=32G --time=02:00:00 --requeue --exclude=hpc-93-36` — headers byte-identical in shape to B2's reviewed script. `--output`/`--error` absolute under `${OUTPUTS_ROOT}/s1_poisson/B3/slurm/%x_%j.{out,err}`, and `submit.sh` `mkdir -p`s that directory before `sbatch`. All paths absolute; no relative path anywhere. `SEED="${1:?…}"`; `submit.sh` submits seed 0 only; `submit_seeds_2_3.sh` exists and is correctly parked for end-of-round confirmation. Staging logic is sound: `CONTROL_CKPT` hardcodes `mode_allpairs` (correct — G0 is the allpairs control), the `cp` target lives under a *different* `ROUND1_EVAL_RESULTS` root so there is no self-overwrite, and a missing control ckpt fails loudly (`:115-118`). `${OUTPUTS_ROOT}/s1_poisson/B3` does not yet exist, so there is no stale-checkpoint hazard on first submit. **S3** (carried from B2's S2): the in-file `#SBATCH --job-name=r1-s1_poisson-B3` omits `-s{seed}`; only the wrapper's `--job-name` override produces the maintainer-matchable name. Submit via `scripts/submit.sh`, never `sbatch scripts/01_train_eval.sh 0`. **S4** (carried from B2's S3): `--time=02:00:00` is ~20× the ledger analog (`s1_poisson` B1, 4 arms, ifc_poisson, e200, h100 = 4.47 min; B2's 5 arms = 5.6 min). It is card-locked in `recipe._sbatch`; right-size at submit time if it pends, do not edit the card. |
| Q6 | Smoke-test evidence | **PASS** | `build_notes[3]` cites the contract-tier `score_panel.py` command form verbatim and every claimed number reproduces **inside the artifact JSONs**, not just in prose: `base__none 0.2817404086094617`, `gain__ladder_level_intercept 0.17663150882196565`, `gain__hf_only 0.21398211638816717`, `gain__ladder_pooled 0.17556054679728325`, `self_only__none 0.3653983463762562` — all five read directly from `scratchpad/contract_smoke_<tag>.json` `per_dataset.ifc_poisson.nRMSE`, each `cached:false`, `metric_source: per_sample_mean`, five distinct `code_hash`. Guard leg: `fluid 0.3123267561968301`, `sharp__sod_1d 0.024271656851296987`, both matching `build_notes[7]`. **B2-continuity verified independently**: `git show 21fdcda:scratchpad/contract_smoke_allpairs__per_level.json` → `0.2817404086094617`, identical to 17 digits, identical `nrmse_def_hash`. `build_notes[4]`'s paired-base claim verified: G0–G3 all `base_ckpt_sha256` prefix `6bfb2f3ce68a3234`, `base_resumed_finished_checkpoint true`, `train_seconds ≈ 1e-6`; G4 `34000d7016d2fc82`. `build_notes[12]`'s dry-run claim verified by re-running the job script's env-guard heredoc against all five committed family JSONs — passed on all five. Firewall `status: clean` with 256 tainted row digests / 34 arrays checked in every ifc_poisson arm; `fit_rows_are_train_rows` 100/50/20/5 vs `n_test 128` in every arm. |
| Q7 | Blast radius | **PASS** | `git diff round1-substrate..HEAD --stat` = 43 files, +18167/−0, top-level components exactly `models_r1/`, `scripts/`, `notes/`, `scratchpad/`. No substrate-fix commit; single build commit; `git status --porcelain` empty in the worktree and `HEAD == 57c24576abe6b045b837ccfd55f331a80e3f8b05` == `build_commit`. (Informational: the main tree carries an unrelated pre-existing modification to `mf_field/factory_mffp/results/contract_test.json` from mentor-side factory activity; `results/` is not a §5-guarded surface and the modification is not in this build commit.) |

## Notes for the analyzer (not build defects)

- **N1 — every fit row is in-sample.** The gain at *all* levels, including the 5
  HF rows, is measured on rows the base was trained on. The card pre-registers
  the attenuation check for exactly this
  (`std_log_g_over_b2_test_gain_std`); at contract tier it reads 7.1–8.4×, which
  is meaningless at 2 epochs. It must be re-read at 200 epochs before the
  mechanism-decider table is interpreted: a value *below* 1 means the ladder law
  is in-sample-attenuated and a G1 null is a base-overfit artifact, not physics.
- **N2 — the contract-smoke control was itself a resume.** `base__none`'s smoke
  JSON reports `base_resumed_finished_checkpoint: true` with `train_seconds ≈
  1e-6`, i.e. the builder's control arm reused a finished ckpt rather than
  training fresh. This does not weaken the B2-continuity gate (identical weights
  → identical eval path → identical 17 digits is precisely the claim), and the
  training path for `allpairs` is provably unchanged anyway — the only training
  edits are the `LADDER_MODES` tuple extension and an `if mode == "self_only":
  return []` guard that cannot fire for `allpairs`. On SLURM, `${OUTPUTS_ROOT}
  /s1_poisson/B3` does not exist, so G0 will train from scratch.
- **N3 — the 200-epoch validity gate is not machine-enforced.** The card's
  "control reproduces B2's 0.034250 within 10 % (0.030825–0.037675)" is checked
  by the analyzer post-hoc (`build_notes[2]`), not asserted in the job script.
  That is the correct division of labour, but the analyzer must actually run it.
- **N4 — firewall coverage is call-site-based.** `assert_clean` gates the three
  constructors, and `fit_estimator`/`ridge_loo_fit` are closed because they only
  consume `rows`. A future edit that builds a design matrix outside
  `build_fit_rows` would bypass the check. Worth a comment if this family is
  vendored again in batch 4 (K > 1).

## Submit-time instructions for the orchestrator

1. **Submit via `scripts/submit.sh`** (never `sbatch scripts/01_train_eval.sh 0`)
   — the seed-bearing job name exists only in the wrapper's `--job-name`
   override.
2. **Close the `heat_local` guard leg on a GPU** (S1). It is one cheap 2-epoch
   call and the script is already written:
   `GUARD_DATASETS=heat_local GUARD_TAG=_heat bash
   <worktree>/scratchpad/run_guard_contract.sh`. It creates no guard obligation
   (family defaults stay `head=none` + `scaler=shared`, bit-preserving) and does
   not gate the main job — run it alongside or after. If it is skipped entirely,
   record that `recipe.env._contract_check` was satisfied on 2 of 3 guard
   datasets, with graceful degradation already demonstrated on the harder cases
   (`fluid`: 2 levels = exactly one auxiliary level, `leave_one_level_out` →
   `skipped_no_other_level`; `sharp__sod_1d`: 1-D fields; plus unit-tested
   2-level and single-level declines).
3. If the job pends on `--time=02:00:00` (~20× the ledger analog), right-size at
   submit time and do **not** edit the card (S4).
