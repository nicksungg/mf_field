# Code review — s2_beyond_copy-B2 (model / LF-residual control + training-free retrieval floors)

**Reviewer**: code-reviewer · **UTC**: 2026-07-30T00:20Z · **Attempt**: 1
**Diff reviewed**: `round1-substrate..5bf0e86c292042b3050979f5c35af538305f1152` (1 commit, 43 files, all `A`dded)
**Worktree**: `/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch/round1/worktrees/s2_beyond_copy/B2`
(clean at `HEAD = 5bf0e86c…` = card `build_commit`)

## VERDICT: **SUGGEST** — submit as-is; four findings for the next stage, two of them about the screen, none about the scored run.

This is a faithful and unusually well-evidenced implementation of the card. Every part-3
element traces to code, and the three interlocks the card makes load-bearing are *measured
and committed*, not asserted. (1) **Identity**: `LF_up` is literally
`panel_data.copylf_prediction(split)` in float64 (`smoke_eval.py:478-479`, read-only import
of the frozen eval layer), the final 1x1 of `proj` is zero-initialised
(`model.py:140-144`), and the pre-checkpoint identity probe (`smoke_eval.py:638-660`)
measures `abs_delta_nrmse = 0.0` **and** `max_abs_field_delta_vs_LF_up = 0.0` against
`eval/copylf_baselines.json` on all five recipe datasets plus `fluid`, hard-stopping above
`IDENTITY_TOL = 1e-6`; at `--epochs 0` the *scored* `skill_test_hf` is exactly `1.0`
(`scratchpad/cov_hybrid_pfc.json`), so the identity holds through `score_panel`, not just in
a probe. (2) **Floor reproduction**: I diffed `retrieval.py` against
`tools/lf_conditioned_headroom.py:76-97,143-151` line by line — same block-mean signature,
same train-fitted z-score applied to both splits, same squared-Euclidean distance, same
`np.argsort(kind="stable")`, k=5, mean of the k **train** residuals added to the query's own
`lf_te`; the only delta is query-chunking, which is arithmetically identical — and the six
committed sidecars reproduce B1-F6 at deltas 2.16e-05 / 5.53e-05 / 6.56e-05 / 2.99e-04 /
4.07e-04 (max 49x inside `S2_FLOOR_F6_TOL=0.02`), with the leak ratios independently
reproducing B1-F9 to three decimals (pfc 1.3104 vs 1.31, cahn_hilliard 1.0001 vs 1.00,
helmholtz 0.9958 vs 1.00, allen_cahn 0.9890 vs 0.99, fisher_kpp 1.0033 vs 1.00) and zero
duplicate-signature hits. (3) **Leakage/discipline**: retrieval keys and the residual bank
are TRAIN-only, train queries use a masked diagonal (`retrieval.py:115-122`), the blend
weight is fitted on a TRAIN holdout against a complementary archive, and the holdout bias is
*recorded in every result JSON* (`blend.caveat`, `reportable: false`), not hidden; the floors
reach the JSON only as `ref_*` splits with `reportable: false` behind a hard stop that
rejects any floor key that looks like a test split (`smoke_eval.py:778-780`), and
`score_panel._extract_test_metric` scores `test_hf` only. I independently verified the
builder's `--env` claim (two `--env` flags → argparse keeps only the last; the family then
hard-stops `required env knob S2_ARM is unset`, exit 1), the 26-knob verbatim match between
both scripts and `recipe.env`, `bash -n` on all seven shell scripts, that the locked card
fields are byte-identical to the starter's committed version, and — by running
`screen_table.py` on my own synthetic inputs — that the anti-hijack hybrid gate blocks a
hybrid with a learned margin on only one Class-A dataset. That same reviewer-run experiment
is what produces finding **F1**: the *crater* half of the promotion rule, implemented exactly
as the card words it, lets the hybrid's training-free term set the bar that declares the
pinned literature-standard arm "cratered". The rule is card-verbatim, so this is a hole in
the card's text rather than builder drift, and ADR 0007 puts a human/orchestrator gate
between the screen table and the submit — hence SUGGEST, not FAIL, with explicit guidance
below.

## Per-question findings

| # | Question | Result | Finding |
|---|---|---|---|
| 3.1 | Card-implementation alignment | **PASS** | Every part-3 item traces to code. `model.py` changes *exactly* the three things the card names — I diffed it against `mf_fno_transfer_film/model.py` @967562e: `SpectralConv2d`/`FiLMNorm`/`FNOBlock` differ only in docstrings, and the code deltas are `lift = Conv2d(2+n_extra, h, 1)` (`model.py:131`), the zero-init final 1x1 (`:140-144`), and the optional `w_retr` scalar init 0 (`:146,173-178`). All four ranked arms exist and were each exercised end-to-end (`scratchpad/cov_{ladderpre,multichan,hybrid}_pfc.json`, `cov_ladderfallback_helm.json`, `path_coverage.log`, six legs, all exit 0): arm 2's `ladderpre_pair=[1,2]` = (fid1→fid2) pretrain then (fid2→fid3), and the card's one-LF-rung fallback fires on helmholtz with `ladderpre_fellback_to_arm1=true`. `max(lf_fids)` is mandatory and enforced (`read_knobs` rejects `S2_LF_FID != "max"`; `smoke_eval.py:484`). All five floors + the blend are emitted as `ref_*` only. Tripwires all present: strictly-coarser-LF (`:486-488`), copy-LF seam ≤1e-9 measured at 0.0, WORK_CAP-vs-native hard stop (`:431-436`), leakage tripwire, `--dataset_dir` == the eval layer's own path (`:411-412`). No paraphrase drift found. |
| 3.2 | Recipe fidelity | **PASS** | All **26** `recipe.env` knobs appear verbatim, in ONE `--env` list, in both `00_screen.sh` and `01_train_eval.sh` (programmatic diff: 0 missing, 0 extra, 0 value mismatches; only `S2_ARM=$ARM`, which defaults to the card's pinned `lf_resid_fno`). `epochs 200`, `seeds [0]`, the five datasets, `family_dir`, `base_family`/`base_commit` all match; `SMOKE` in `smoke_eval.py:78-79` is byte-equal to the base family's dict. `contract_smoke.json` records all 26 knobs with the card's values. Every non-card choice is declared in `build_notes` **and** re-derivable from the result JSON (`blend.candidates`, `input_channels.channel_scales`/`normalization`, `floors.diagnostics.patch.sub_sig`, `stages[].lr`). Only nit: `S2_LF_CHANNELS=max_only` is *required* by `read_knobs()` but never validated or consumed (the channel set follows the arm name) — decorative, no drift. |
| 3.3 | §5 immutable compliance | **PASS** | No writes to `round1/eval/`, `project.yaml`, `program.md`, ADRs or agent prompts (`git status` on `round1/eval` clean; the family only *imports* `nrmse.py`/`panel_data.py` and *reads* `copylf_baselines.json`). No guarded factory path in the diff; `data_adapters` used read-only. `eval/results/` and `eval/cache/` writes are sanctioned — both are listed in `round1/.gitignore`. No data regeneration; no extra HF samples (floors read the existing train split). Scoring is routed through `score_panel.py` in both scripts and in the committed contract smoke; the hand-computed per-sample rel-L2 in `_ref_split`/`_blend` is the *same expression* as `eval/nrmse.py:29` and its aggregates come from `nrmse()` itself — see F3 for the one key-naming trap. Seeds `{0}` in-round with `submit_seeds_2_3.sh` parameterised for 1/2; epochs 200 (smoke) and 2 (contract) match the tiers. No pre-falsified lever re-proposed: this is an LF-input-channel residual head on the FNO backbone — not a WNO swap, not LF low-mode freezing, not a diffusion prior. |
| 3.4 | Contract compliance | **PASS** | `manifest.json` (name/description/supports/frozen + card/base provenance), `smoke_eval.py` with the exact 6-arg CLI (`:845-853`), `INSPIRATION.md` citing every `prior_art` entry by verdict row (i)/(ii)/(iii) plus the batch-1 overclaim correction and the resolved KRF URL — which I confirmed against `websearches/s2_beyond_copy/batch_2/report.md:116,152` while the locked `prior_art` TBD cell is untouched. **Checkpoint-resume from `<ckpt_dir>/last.pt` implemented and drilled**: atomic `tmp`+`os.replace`, 5 saves/stage, mid-stage restore of model/opt/sched/generator (`:207-211,248-253,662-717`), and a real SIGKILL drill on `fluid` shows `[resume] mid-run checkpoint: stage=finetune epoch=1/2` → `[resume] HFresid-train continues from epoch 1/2` → exit 0 (`cov_resume_leg1.log`, `cov_resume_leg2.json`). I traced the stage-skip logic for all four resume states (fresh / mid-pretrain / pretrain-complete / mid-finetune / done) — all correct. Seeding: `torch.manual_seed(args.seed)`, `np.random.seed(args.seed)` (`:399`) plus the blend's `default_rng(seed)`; `score_panel` adds `PYTHONHASHSEED`/`CUBLAS_WORKSPACE_CONFIG`. Identity probe runs *before* the checkpoint load, so it stays meaningful on a requeued job. |
| 3.5 | SLURM script correctness | **SUGGEST** | All seven scripts pass `bash -n` (run by me: `00_screen.sh`, `01_train_eval.sh`, `submit.sh`, `submit_screen.sh`, `submit_seeds_2_3.sh`, `scratchpad/cov_rest.sh`, `scratchpad/path_coverage.sh` — all OK; `py_compile` clean on all five `.py`). Partition `gpu` + typed `--gres=gpu:h100:1` match `project.yaml` (ADR 0005); `--exclude=hpc-93-36` and `--requeue` follow round convention (every other B-card); cpus 4, mem 32G; job names `r1-s2_beyond_copy-B2-screen` and `r1-s2_beyond_copy-B2-s$SEED` (set on the sbatch command line so seeds 1/2 get their own names; the `-screen` suffix has precedent — `r1-s4_hybrid_routing-B1-guard`/`-agg`); `--output/--error` under `<outputs>/s2_beyond_copy/B2/slurm/%x_%j.{out,err}`; every path absolute; `01_train_eval.sh` takes `SEED=$1` (+ optional promoted `ARM=$2`, validated against the card's arm list); `submit.sh` = seed 0 only; `submit_seeds_2_3.sh` present and correctly marked not-for-in-round. `--time` right-sized against the ledger: screen 01:00:00 (analogs: s5-B1 3-dataset 2-epoch h100 0.77 min, s6-B1 5-variant screen+guard 8.6 min, floors 32-76 s/dataset and pre-warmed), main 02:00:00 (analog: s5-B1 6-dataset 200-epoch h100 36.62 min, and arm 1 is single-stage) — roughly 3-4x headroom, not oversized. Output paths in the card match what the scripts and `score_panel` actually write (`result_beyond_copy5_s<seed>.json`, `results/<arm>/s2_lf_residual_control/{<ds>_e200_s<seed>.json, ckpt_<ds>_e200_s<seed>/last.pt}`, `screen/<arm>__{beyond_copy5,guard}_s0.json`, `eval/floor_<ds>.json`). **Finding F2** is the one defect: `set -euo pipefail` makes the first failing screen leg abort the whole single job. |
| 3.6 | Smoke-test evidence | **PASS** | `build_notes[1]` cites the contract-tier command through `score_panel.py` (`--datasets ext__helmholtz_2d --epochs 2 --seed 0 --no_cache` + all 26 `--env` knobs) and the artifact exists at `<worktree>/scratchpad/contract_smoke.json` (+ `.log`): exit 0, `test_hf` nRMSE 15.35036816703397, `metric_source per_sample_mean`, finite, `split test_hf`, 26 knobs recorded. The 2-epoch magnitude is correctly labelled a plumbing check, not a signal (zero-init head overshoot; ADR 0007). Supporting evidence is unusually complete: floor sidecars for all 5 + `fluid`, per-arm coverage JSONs, the resume drill, and a branch-complete `screen_table.py` dry run whose `README.md` marks every number **SYNTHETIC** except one real contract-smoke cell and the (real) floor row. Note: `contract_smoke.log` is `score_panel`'s stdout (the summary JSON), so the child's `[identity]`/`[F6]` lines for that specific run are not captured — but they are captured for direct runs on all five datasets, and both interlocks are unconditional hard stops, so exit 0 implies they passed. |
| 3.7 | Blast radius | **PASS** | 43 files, all additions, all under `models_r1/s2_lf_residual_control/`, `scripts/`, `notes/`, `scratchpad/{,dryrun_screen/}`. Zero paths outside the allowlist (checked with an inverted grep). No substrate "fix" commit; the base family was not edited. Card locked fields verified byte-identical to the starter's committed version (`ceb47c0`) across all 17 locked keys; only `status`, `scripts_path`, `output_paths`, `build_commit`, `build_notes` changed. |

## Ruling on the builder's flagged judgment call

**APPROVED — grounded, not invented.** The base family's own semantics
(`mf_fno_transfer_film/smoke_eval.py:165,170` and its docstring line 22) are: `lr_pretrain =
1e-3` for the **from-scratch** stage, `lr_finetune = 3e-4` for the stage that follows a
pretrain, with `--epochs` applied **per stage**. The builder's assignment — single-stage arms
(1, 3, 4, and ladderpre's 1-rung fallback) at 1e-3; ladderpre's second stage at 3e-4 — is
exactly that mapping, both values are card-pinned, and each run records the assignment in the
result JSON (`stages[].lr`; verified `cov_ladderpre_pfc.json` = `[('LFpair-pretrain',
'pretrain', 0.001), ('HFresid-train', 'finetune', 0.0003)]`, `cov_multichan_pfc.json` =
single stage @0.001, `cov_champion_sod1d.json` = the base schedule 0.001→0.0003). No
hyperparameter was invented. **Carry-forward caveat**: this makes arm 1 (200 epochs @1e-3)
and arm 2 (400 epochs total, second stage @3e-4) non-isoparametric in both budget and LR.
That is card-level design (the card defines ladderpre as the 2-stage arm), but it is the
mechanism behind F1: at 2 epochs the arms' skills are dominated by zero-init-head *overshoot
magnitude*, and a 3.3x smaller second-stage LR systematically overshoots less, so the crater
ratio can order the arms by LR rather than by quality.

## Findings

**F1 — SUGGEST (`scripts/screen_table.py:91-105`) — the crater bar can be set by the
hybrid's training-free term, hijacking the pinned arm.** `best[ds]` is the min over *all*
non-crashed arms, including a hybrid that failed its own learned-margin gate. This is
verbatim-faithful to the card ("1.5x the best surviving arm's"), and the hybrid gate itself is
exactly right — I confirmed with a reviewer-run synthetic case (hybrid margin on only
`ext__helmholtz_2d`) that `hybrid_gate_passed=False → promotable=False`. But in that same
case, with a perfectly healthy rank-1 at skill 1.20 and the hybrid at 0.55-0.70, the ratio
test declares **all three learned arms cratered** and returns `promoted_arm: null`. *Minimal
fix, only if the real screen returns `null` or a non-rank-1 arm*: restrict `best[ds]` to arms
whose `hybrid_gate_passed` is true — "surviving" then reads as "promotable", which is still
inside the card's wording and closes the hole without a card edit. *Orchestrator guidance
regardless*: `promoted_arm` is advisory. Per ADR 0007 ("discarding only clearly-broken /
cratered variants, not close calls") and the card's pinned default, submit `lf_resid_fno`
unless it literally crashed or NaN'd; do not auto-switch arms on a 2-epoch ratio test applied
to a zero-init head far from convergence (the builder flagged this same magnitude caveat).

**F2 — SUGGEST (`scripts/00_screen.sh:19` + the loop at `:40-87`).** `set -euo pipefail`
plus one job covering eight `(arm, dataset-set)` legs means the **first** non-zero exit
aborts the entire screen, so `screen_table.py` (`:89-95`) never runs and the crash/NaN
crater branch (`screen_table.py:72-73,99-100`, which handles `MISSING screen output`) is
unreachable in practice — the rule can only ever see *slow* failures, never *hard* ones.
Minimal fix: tolerate a per-leg failure, e.g. wrap the `score_panel` + `assert_env` pair in
`|| { echo "[screen] FAILED arm=$ARM tag=$TAG"; }`, leaving the final `screen_table.py` call
unconditional.

**F3 — SUGGEST (for the analyzer; `smoke_eval.py:791` vs `data_adapters/metrics.py:110`).**
The `nRMSE` key means two different things inside one result JSON: per-sample-mean in the
`ref_*` splits, ratio-of-sums in `test_hf`. `rel_l2_mean`, `skill_vs_copylf`,
`res["skill_test_hf"]` and `res["floors"]["skill"]` are all per-sample-mean and therefore
internally consistent, so every comparison the card actually makes (trained arm vs floor, vs
the 0.512/0.555 falsification thresholds) is apples-to-apples. The analyzer must read
`rel_l2_mean` / `skill_vs_copylf`, never compare `splits.test_hf.nRMSE` against
`splits.ref_*.nRMSE`.

**F4 — NOTE (two small evidence gaps + two doc nits).** (a) A live cache entry from the
builder's contract smoke exists at `round1/eval/cache/64c6fd92….json` for
`(lf_resid_fno, ext__helmholtz_2d, e2, s0)`; the screen's arm-1 helmholtz cell will be a
cache hit, so no per-run JSON lands in that arm's dir for it and `assert_env.py:75-98` will
check 4 of 5 per-run JSONs on that leg. Harmless (the cached number was itself produced
under the identity and F6 hard stops), but pass `--no_cache` on the screen if you want all
interlocks re-asserted. (b) The arm-keyed checkpoint **rejection** path
(`smoke_eval.py:665-677`) is code-correct but not drilled — no `config mismatch … training
fresh` line appears in any committed log; the primary defence is directory-level
(`ROUND1_EVAL_RESULTS=<…>/results/<arm>`, which relocates both per-run JSONs and
`ckpt_<ds>_e<ep>_s<seed>/`), so this is belt-and-braces only. (c) `notes/handoff_experiment_builder.md`
says "F6 reproduction `<=6.6e-5`"; the true max delta is 4.07e-04 (`sharp__fisher_kpp_2d`) —
the *card* `build_notes` state this correctly, so it is a handoff-only stale figure with no
numeric consequence (49x inside tolerance either way). (d) `screen_table.py`'s docstring says
its Class-A rule is "the rule `tools/lf_conditioned_headroom.py` itself uses"; the tool
thresholds the *best* LF-keyed rung at 0.95 while the script thresholds `retr_blockmean16_k5`
specifically. Same partition on these five datasets (A: pfc 0.562 / cahn_hilliard 0.625 /
helmholtz 0.785; B: allen_cahn 1.042 / fisher_kpp 1.062), so the derivation is sound — only
the docstring overstates.

## Green-light conditions for the orchestrator

1. Submit `submit_screen.sh` first (ADR 0007), then read `screen/screen_table.md`.
2. If `promoted_arm` is `lf_resid_fno` → fix it in the card and run `submit.sh`.
3. If `promoted_arm` is `null` or **not** `lf_resid_fno`, check whether the switch is driven
   by an actual crash/NaN. If it is not, promote `lf_resid_fno` anyway (F1) and record the
   reasoning; optionally send F1's minimal fix to the debugger first.
4. Carry F3 into part 5 so the analyzer compares `skill_vs_copylf` / `rel_l2_mean`, never the
   raw `nRMSE` key, across `test_hf` and `ref_*`.
