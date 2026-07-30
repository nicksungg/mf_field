# Code review — s3_warp-B2 (attempt 1) — 2026-07-30T19:05Z

**Verdict: SUGGEST (submit as-is).**
Card status → `reviewed_suggest`. Build commit `d9fb501`, branch
`round1/exp-s3_warp-B2`, diff vs `round1-substrate` = 20 files / +3025 / -0.

## Verdict paragraph

This build implements card part 3 faithfully and, unusually, its integrity core
is checkable — so I checked it rather than taking it on report. All five
hard-stop seams are runtime-enforced inside `smoke_eval.main()` (each raises
`SeamViolation` before any arm trains, so `set -e` in `01_train_eval.sh` kills
the job before the 200-epoch step), and I independently re-measured four of them
from the data with the family's own functions: S1 copy-LF `0.08765999100758841`,
delta **exactly 0.0** vs `eval/copylf_baselines.json`; S2 `ref_reg_corrected`
skill `0.47687619181488217` vs B1 F3 variant C 0.4769 (rel dev 5.0e-5) with the
torch sampler matching `scipy.map_coordinates(order=1, grid-wrap)` to **0.0**;
S4 vendored-LSI skill `0.4438847630364397` inside the widened s6_local-B1 band;
S5 by executing the family's own `seam_s5()` (decode(0), init coefficients, init
phi and warp-vs-warp_off forward deviation all exactly 0.0 with a de-zeroed
corrector delta 0.169). S3 is evidenced by the committed
`scratchpad/probe_seam_s3.json` (C16 9.05e-7 from B1's recorded value) and I
confirmed `warp_core.py` is B1@4799abd **byte-identical** apart from a 24-line
provenance header (`git show 4799abd:models_r1/s3_warp_oracle/warp_core.py |
diff` → header only), and `lsi_ref.py` character-for-character equal to
`tools/defect_correction_learnability.py`. ADR-0009 legality holds under
drilling: `DisplacementHead.forward(self, lf, cond)` is signature-asserted at
runtime, the supervision oracle is refit on `regc_tr`/`y_tr` (train only; B1's
`p_train` never loaded — no reference to it exists in the family), every training
tensor is row-count-asserted to `n_train=400`, and the only test-HF-fitted
objects (`seam_s3`, `ref_oracle_phi`) are consumed after training and/or as
scalars that never enter a loss. Both fixed bugs are real and I verified the
fixes myself rather than trusting the note: a state-dict round-trip through
`torch.save`/`load_state_dict` now succeeds with `node_y/node_x` contiguous
(strides `[65536,256,1]`), and `project_ball` gives `f(0)=0`, **finite gradient
1.0 at 0**, exact radius 4.0 on the boundary, identity inside — with two real
training steps on real data producing finite losses (0.00317, 0.01973) and all
parameters finite. Recipe fidelity is exact: a programmatic diff shows all 22
non-path knobs identical across `recipe.env`, the sbatch `ENV_BASE` array, and
the family's `ENV_DEFAULTS`. Blast radius is clean (only `models_r1/`,
`scripts/`, `notes/`, `scratchpad/`), no §5 immutable is touched, and no
pre-falsified lever is re-proposed. The findings below are all non-blocking:
the biggest is that the login-node contract smoke left **no result artifact on
disk** (§3.6's literal FAIL trigger), which I am downgrading because the
orchestrator explicitly authorized shipping without it (flow 15:55Z, s5-B1
precedent), the builder disclosed it prominently, SLURM step A is a genuine
seam-enforcing gate that runs before the expensive step, and I have now
reproduced the substance of that smoke myself.

## Findings (7 questions)

| # | Question | Verdict | Finding |
|---|---|---|---|
| Q1 | Card-implementation alignment | PASS | Every part-3 item traces to code: single node-aligned resample (`onesided.periodic_bilinear`, `smoke_eval.node_resample`), 16×16×2=512-dof band-limited decode (`bandlimited_upsample_matrix`), 4-cell ball projection, JUBW sub-cell offset channels (`Corrector.forward` 2 extra channels), grad-mask supervision `w=|∇LF|/mean|∇LF|` (`grad_weights`), μ 1.0→0.1 at 50 % (`train_arm` L605), 4-block/width-48 ConvNeXt corrector, all 7 arms as named split keys, all 8 free diagnostics one-function-each in `diagnostics.py`, sequential arms + `last.pt` resume. Only `test_hf` is scored: `score_panel._extract_test_metric` prefers `test_hf` and `ref_*` keys are not test keys (verified in `eval/score_panel.py:131-146`). |
| Q2 | Recipe fidelity | PASS | Programmatic 3-way diff (card `recipe.env` ↔ `01_train_eval.sh:66-89` ↔ `smoke_eval.ENV_DEFAULTS`): 22/22 knobs identical verbatim, no extras on either side. `S3W2_DIAG_OUT` is the card's literal `${OUTPUTS_ROOT}/…` expanded to the absolute path (and `smoke_eval.read_env` hard-stops if `${` survives); the screen step redirects it to `eval/screen` so the non-reportable pass cannot overwrite the scored sidecar — correct call. Non-recipe constants all carry cited provenance (`GRAD_CLIP=1.0` ← `mf_fno_transfer_film` SMOKE; ConvNeXt expansion 4 + dw-7×7 ← s6_local-B1; LSI holdout 0.2 / n_train 320 ← promoted tool defaults; `SEAM_S3_MAX_DISP=16` ← B1's own `S3W_MAX_DISP_CELLS`). |
| Q3 | §5 immutable compliance | PASS | No writes to `round1/eval/`, `project.yaml`, `program.md`, subagent prompts, or guarded factory surfaces (`factory_root/{eval,baselines,references,scripts,data}`, `factory.md`, `akash/`) — the diff touches none of them and at runtime the family only *reads* `eval/{nrmse,panel_data,copylf_baselines}`. `ROUND1_EVAL_RESULTS` is redirected to the outputs root (B1 precedent); the only thing landing under `round1/eval/` is `eval/cache/`, which is the eval layer's own gitignored artifact dir (`round1/.gitignore:4`). No data regeneration. Scoring runs through the unmodified `score_panel.py` in both steps; the family's own `nRMSE_round_def` uses `eval/nrmse.py` and equals score_panel's `mean(rel_l2_per_sample)` by construction. Seeds `[0]` (ADR 0004), epochs 200 = `tiers.smoke_epochs`, screen 2 = `contract_epochs`. No pre-falsified lever (WNO swap / LF low-mode freezing / diffusion prior) is re-proposed — the band-limited *displacement* parameterisation is not LF spectral freezing. |
| Q4 | Contract compliance | PASS | 6-arg CLI exact (`--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed`); `manifest.json` has name/description/supports/frozen; `INSPIRATION.md` cites all 11 `prior_art.citations` plus li2020fno/liu2022convnext for the re-implemented blocks and states nothing came from `references/v9_baseline/`. Resume from `<ckpt_dir>/last.pt` implemented (`load_ckpt`, atomic per-epoch `save_ckpt`, arm/epoch/optimizer/RNG/batch-generator/oracle cache) **and functionally verified by me** (state-dict round-trip, max param dev 0.0). `config_key` now includes a sha256 over the family's `.py` files, so cross-code resume is impossible. Seeding covers python/numpy/torch/cuda via `--seed`. Result JSON carries `model`, `dataset`, `splits.*.nRMSE`. |
| Q5 | SLURM correctness | PASS | `bash -n` run by me on all four shell files — `scripts/01_train_eval.sh` OK, `scripts/submit.sh` OK, `scripts/submit_seeds_2_3.sh` OK, `scratchpad/run_contract_smoke.sh` OK. `--partition=gpu` + typed `--gres=gpu:h100:1` match `project.yaml sbatch:`; `--nodes/--ntasks/--cpus-per-task=4`, `--mem=64G`, `--time=02:00:00`, `--requeue`, `--exclude=hpc-93-36` (precedent `state/gates.md:38`, s1-B1/B2/B3, s5-B3); `--output/--error` absolute under `${OUTPUTS_ROOT}/s3_warp/B2/slurm/%x_%j.{out,err}` and mkdir'd by both wrappers; every path absolute incl. the sibling-script path (spool lesson); `01_train_eval.sh` takes `SEED="${1:?…}"`; `submit.sh` = seed 0 only; `submit_seeds_2_3.sh` present for the end-of-round top-3 pass; job name `r1-s3_warp-B2-s{seed}` supplied by the wrappers' `--job-name` (the in-file default is the seed-0 name) — **submit via `scripts/submit.sh`, never `sbatch 01_train_eval.sh` directly**. All 22 knobs go in a single `--env` flag (`nargs="*"`, correct). Step A→B ordering is enforced by `set -euo pipefail`. See S3 below on walltime. |
| Q6 | Smoke-test evidence | SUGGEST (would be FAIL absent the authorization) | `build_notes` cites the contract-tier command and `scratchpad/run_contract_smoke.sh` is committed, but **no result JSON or log from that run survives**: `scratchpad/{contract_smoke.json,smoke_results/,diag/}` do not exist, so the claims "trained 2 of 3 arms", "per-epoch checkpoints", "a real cross-process RESUME" have no on-disk artifact. What *is* committed: `probe_seam_s3.{py,json,log}` (S3, full 100-sample split, C16 rel dev 9.05e-7) and `verify_eval_block.{py,json,log}` (whole post-training block on an 8-sample slice, exit 0, all values finite — but run with `--fresh`, so it did **not** exercise the checkpoint load path either). Downgraded to SUGGEST because (a) the orchestrator explicitly authorized shipping without a completed login smoke (flow 2026-07-30T15:55Z, s5-B1 precedent) and the builder disclosed it, (b) SLURM step A is a real 2-epoch, seams-ENFORCED `score_panel.py` gate that aborts before step B, and (c) I independently reproduced S1/S2/S4/S5, both bug fixes, and 2 finite training steps (drills below). |
| Q7 | Blast radius | PASS | `git diff round1-substrate..d9fb501 --stat`: `models_r1/s3_warp_onesided/*` (8), `notes/*` (2), `scratchpad/*` (6), `scripts/*` (3). Nothing else; no substrate "fix" commits; single atomic commit; worktree tree clean. |

## Independent verification I ran (read-only, outside the repo)

| drill | result |
|---|---|
| `git show 4799abd:models_r1/s3_warp_oracle/warp_core.py` vs vendored | identical apart from the 24-line provenance header |
| `lsi_ref.fit_transfer/apply_transfer/rho` vs `tools/defect_correction_learnability.py:76-93` | character-for-character identical |
| S1 re-measure | `nrmse(copylf, HF_test) = 0.08765999100758841`, delta **0.0** |
| S2 re-measure | variant-C nRMSE `0.041802962686225575` → skill `0.47687619181488217`, rel dev **5.0e-5** (build_notes says 2.6e-5 — see S6) |
| torch vs scipy `grid-wrap` sampler | max abs dev **0.0** over the 100-sample test split |
| S4 re-measure | LSI (misregistered) skill `0.4438847630364397` ∈ [0.4312, 0.4501] ✓; LSI on the corrected path (the actual `ref_lsi` arm) = **0.4426** (card predicted 0.42–0.46 ✓) |
| S5 (family's own `seam_s5`, float64/CPU) | decode(0)=0.0, init coeffs 0.0, init φ 0.0, warp−warp_off **0.0**, corrector delta 0.169 → pass |
| resume fix | `save`→`load_state_dict` round-trip OK; `node_y/node_x` strides `[65536,256,1]`, contiguous; max param dev after reload 0.0 |
| NaN fix | `project_ball(0)=0`, grad at 0 = **1.0** (finite), boundary radius exactly 4.0, identity inside; 2 real training steps: losses 0.003175 / 0.019731, grad norms 1.39 / 3.41, `max|φ|` 0→0.0133 cells, all params finite |
| param counts | head **591,722** / corrector **84,913** / total 676,635 |
| regime shift | variant-C train `0.009369736584907532` vs test `0.041802962686225575` → **4.46×**; copy-LF 0.058087 vs 0.087660 (build_notes' claim confirmed) |

## Non-blocking findings (for the debugger / analyzer, in priority order)

- **S1 — walltime is the one real operational risk.** `--time=02:00:00` comes from
  the card's own part-3 suggestion (locked), but `slurm_rules.md §4` would give
  more: the ledger analog is `fno_transolver_seq / sharp__cahn_hilliard / 200 ep
  / h100 = 30.73 min` for **one** trained model, and this job trains **three**
  arms and runs **six** oracle ladder fits (S3 + train + test, once in step A and
  again in step B — step A and step B have different `config_key`s and different
  ckpt dirs, so nothing is shared). B1's GPU ladder on this dataset took 105.8 s
  for 100 samples, so ≈17 min of the budget is ladder fitting alone. Plausible
  total 50–115 min. *Submit-time instruction*: submit as-is; if the job hits
  `TIMEOUT`, **just resubmit `scripts/submit.sh`** — resume is verified, per-epoch
  checkpoints are atomic, and `config_key` is stable across resubmits (step A will
  re-run ~10 min first, which is the intended gate). Only if it times out twice
  should the debugger raise `--time` as an INFRA fix.
- **S2 — the displacement head is 591,722 params (7× the corrector), fit on 400
  train samples.** The card only says "small FNO-style encoder", and width 24 /
  2 blocks *is* small versus the zoo default (64/4 → ~10.5 M), so this is inside
  builder discretion and needs **no operator amendment**. But the in-code
  rationale (`onesided.py:54-56`: "chosen small … so the head cannot dominate the
  ~86 k corrector") is factually wrong — it dominates 7:1. The analyzer should
  read Leg C knowing the mechanism under test has 592 k parameters predicting
  512 dof from 400 samples; if `test_hf` ≈ `ref_warp_off`, head capacity/overfit
  is a live alternative explanation to "displacement is not LF-predictable".
- **S3 — corrector 84,913 params vs the card's "~70–80 k" prose estimate.** No
  amendment needed: `S3W2_CORR_BLOCKS=4` / `S3W2_CORR_WIDTH=48` are in the locked
  `recipe.env`, so the estimate is what moved, not the recipe; 84.9 k is the same
  class as s6_local-B1's 77 k, as the card intends.
- **S4 — batch order does not depend on `--seed`.** `train_arm` seeds its shuffle
  generator from `sha256(arm)` only (`smoke_eval.py:589-590`), so seeds 1/2 differ
  from seed 0 in weight init and bootstrap only, not in minibatch composition.
  Harmless for seed 0; it will mildly *understate* seed spread if this card enters
  the end-of-round top-3 confirmation. Note it there; do not change it now (it
  would invalidate the seed-0 checkpoint).
- **S5 — two small inaccuracies in `build_notes`.** (i) S2's rel dev is 5.0e-5,
  not 2.6e-5 (both are ~400× inside the 2 % tol; the seam passes either way).
  (ii) "the family's `ENV_DEFAULTS` equal the recipe too (a bare run reproduces
  the card)" is not exact: `ENV_DEFAULTS["S3W2_DIAG_OUT"] = ""`, so a bare run
  writes **no** diagnostics sidecar. All 22 scoring-relevant knobs do match.
- **S6 — `LockedHF` is an audit, not a capability boundary.** `reference_read()`
  returns the live array with no copy and no restriction, so the guard rests on
  `assert_train_only` (row counts) plus the `DisplacementHead.forward` signature
  assert. Both are real and both fire at runtime; for this card that is
  sufficient, and the audit trail lands in the result JSON. Worth hardening only
  if a later card reuses the class.
- **S7 — the analyzer must read `non_reportable` / `seams_all_pass` before
  quoting any number.** If S3's fit config ever deviates, the job still exits 0
  and writes a result JSON stamped `non_reportable: true`, `seams_all_pass:
  false`. With the recipe as pinned this cannot fire, but the check is one line
  and it is the design's only non-aborting failure mode.
- **S8 — Leg C context, already flagged by the builder and confirmed by me.** The
  supervision oracle is fitted where the corrected LF→HF gap is 4.46× smaller
  (train 0.00937) than where the model is scored (test 0.04180). It reaches the
  analyzer through `build_notes[9]` and, machine-readably, through
  `oracle_train.nrmse_regc_vs_train_hf` in the diagnostics sidecar.
- **S9 — pre-registered comparator, measured now for free.** `ref_lsi` (the
  zero-parameter arm on the corrected path) will land at **0.4426**. Leg B
  therefore needs `skill(test_hf) < min(controls) − 0.20`, i.e. roughly
  `< 0.20–0.24` depending on where the two trained controls land.

## Submit-time instructions

1. Submit **`scripts/submit.sh`** (seed 0 only). Never `sbatch
   scripts/01_train_eval.sh` directly — the conforming job name comes from the
   wrapper's `--job-name`.
2. Do not run `scripts/submit_seeds_2_3.sh` now; it is parked for the
   end-of-round top-3 confirmation (ADR 0004).
3. Expect step A (2-epoch, seams enforced, `non_reportable`) to take ~10–15 min
   and to print `[S1]…[S5]` before any training. **A step-A seam violation is an
   ALGO signal, not infra** — the job exits non-zero by design.
4. On `TIMEOUT`: resubmit the same script once (resume verified). On a second
   timeout, hand to the debugger to raise `--time`.
5. The reportable number is `splits.test_hf` in
   `…/s3_warp/B2/eval/result_sharp__cahn_hilliard_s0.json`, valid only if
   `seams_all_pass: true` and `non_reportable: false`.

## Checklist

- [x] Handoff written with verdict + 7 findings
- [x] Card status set to `reviewed_suggest`, matching the verdict
- [x] `review_notes[]` gained exactly one entry
- [x] Locked fields unchanged (verified by re-read + field-by-field compare)
- [x] Every finding cites a file/line or a measured number
- [x] `bash -n` actually run on all 4 shell scripts (output cited in Q5)
