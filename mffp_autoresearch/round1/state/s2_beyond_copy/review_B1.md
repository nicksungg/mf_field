# Code review — s2_beyond_copy-B1 (diagnostic / copy-LF excess-error forensics)

**Reviewer**: code-reviewer · **UTC**: 2026-07-29T17:40Z · **Attempt**: 1
**Diff reviewed**: `round1-substrate..ba487126` (2 commits: `f38d8db` build, `ba48712` pinn strip)
**Worktree**: `/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch/round1/worktrees/s2_beyond_copy/B1`
(clean at HEAD = `ba487126aef5fdf449b69e619ddee9a69d60220d` = card `build_commit`)

## VERDICT: **SUGGEST** — submit as-is; three non-blocking findings for the next stage.

The build is a faithful, unusually careful implementation of the amended card. Every
part-3 element traces to code (family dir + manifest + `smoke_eval.py` + `base_reload.py`
+ `forensics.py` + INSPIRATION; M1 forward-hook audit, M2 ladder with 1-NN-in-X as the
*scored* `test_hf` split and everything else under `ref_*`, M3 four dyadic radial bands
with `R_b`/`H_b`/coherence, M4 τ=0.1 interface distance transform in 4 strata, M5a
per-sample optimal rescale + M5b aligned-vs-shuffled pairing control, per-dataset
`diagnostics_<ds>.json` sidecar carrying `nrmse_def_hash`), the recipe is reproduced
byte-for-byte in the launch script (all 8 `S2B1_*` knobs, five datasets, `--epochs 0`,
seed 0), and the three interlocks are real rather than decorative: the module-level
`_train` is replaced by a raising stub *and* a forward-hook independently asserts zero
training-mode forward passes; the copy-LF seam is kept at the card's literal ≤1e-9 and
reproduces `eval/copylf_baselines.json` at delta exactly 0.0. I independently verified
the load-bearing safety property: all 15 frozen batch-0 `last.pt` files under
`round1/eval/results/mf_fno_transfer_film/` still carry the sha256 and mtimes recorded in
`build_notes` *after* two full smoke reloads, no `_forensics_unused.json` was left behind,
and the base family's only write path (`torch.save` at
`models/mf_fno_transfer_film/smoke_eval.py:171`) is unreachable because it sits behind the
tripwired `_train` call. The pinn strip is complete and structural, not env-gated. The
declared 1e-9 → 1e-3-relative deviation on seam check (ii) preserves the interlock's
purpose and is correctly declared. The findings below are hygiene and hand-off notes, not
defects: the run does not redirect `ROUND1_EVAL_RESULTS`, so `score_panel` will create a
new `round1/eval/results/s2_copylf_forensics/` tree inside the same frozen eval layer the
card reads its checkpoints from; and two facts (`repro_exact_1e9` will be `false`
everywhere; the scored split is a lookup table, not a model) must reach the analyzer and
the leaderboard.

## Per-question findings

| # | Question | Result | Finding |
|---|---|---|---|
| 3.1 | Card-implementation alignment | **PASS** | Every part-3 item traces to code: family dir + 3 files (`smoke_eval.py`, `base_reload.py`, `forensics.py`), seam checks (i)/(ii)/(iii) at `smoke_eval.py:186-190,244-258` + `base_reload.py:124-136,188-194`, M1 `base_reload.py:150-166,205-213`, M2 `forensics.py:40-93` + `smoke_eval.py:193-199`, M3 `forensics.py:99-193`, M4 `forensics.py:199-263`, M5 `forensics.py:269-300`, sidecar `smoke_eval.py:347-385`. `ifc_poisson` excluded (not in `--datasets`, plus a hard stop at `smoke_eval.py:159-163` if a test split ships no LF). Every builder choice not in part 3 (M4 pooled-quartile strata, M3 open outer band, deranged controls) is declared in `build_notes` **and** re-derivable from the sidecar (`distance_quantile_edges_cells`, `area_share_by_stratum`, `edges_wavenumber`). One deliberate deviation, judged below. |
| 3.2 | Recipe fidelity | **PASS** | Programmatic compare of the `--env` block in `scripts/01_train_eval.sh` against the AMENDED `recipe.env`: all 8 keys match exactly (`MATCH: True`), including `S2B1_BASE_FAMILIES=mf_fno_transfer_film` post-ADR-0008. `--datasets` is the recipe string verbatim; `--epochs 0`; `submit.sh` passes seed 0 (`recipe.seeds == [0]`). All 8 knobs are *required* at runtime (`smoke_eval.py:74-82`), so a dropped knob is a hard stop, never a silent default — the strongest possible form of recipe fidelity. No hyperparameter appears in code that is absent from recipe ∪ part 3 ∪ build_notes; the two tolerance constants `REPRO_ABORT_RTOL`/`REPRO_EXACT_TOL` are declared with in-source rationale (`smoke_eval.py:51-66`). |
| 3.3 | §5 immutable compliance | **PASS (1 suggestion)** | Diff touches no `round1/eval/`, `project.yaml`, `program.md`, ADR or subagent file; no guarded factory surface (`factory_root/{eval,baselines,references,scripts,data}`, `factory.md`, `akash/`) appears in `git diff --stat`. `mf_field/factory_mffp/models/mf_fno_transfer_film/` is imported and monkeypatched **in-process only** — its files are untouched on disk. No data regeneration; data is read through `eval/panel_data.py`. Scoring routes through `score_panel.py` and the single `eval/nrmse.py` definition (`nrmse = mean_i ||p_i-t_i||/||t_i||`, identical to the `rel_l2_per_sample` mean `score_panel._extract_test_metric` consumes) — no hand-rolled metric. Seed 0, epochs 0 = the card's tier. No pre-falsified lever re-proposed (this card proposes no lever at all). **Suggestion S1**: `01_train_eval.sh` does not `export ROUND1_EVAL_RESULTS`, so `score_panel._run_one` will create `round1/eval/results/s2_copylf_forensics/{<ds>_e0_s0.json, ckpt_<ds>_e0_s0/last.pt}` inside the frozen eval layer — the same tree that holds the batch-0 checkpoints this card must not disturb. Precedent is mixed (s1-B1 and s5-B1 redirect; s4-B1 deliberately does not), so this is not a violation, but the one-line `export ROUND1_EVAL_RESULTS="$OUT_DIR/eval/results"` before the `python` call would keep all round-1 experiment bytes out of `eval/`. Safe: `S2B1_CKPT_ROOT` is an independent knob hard-coded to the real path, so the reload and the requeue short-circuit are unaffected. |
| 3.4 | Contract compliance | **PASS** | `manifest.json` has name/description/supports/frozen (+ an informative `"diagnostic": true`); `smoke_eval.py` exposes the exact 6-arg CLI (`--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed`, `smoke_eval.py:398-406`); result JSON carries `model`/`dataset`/`splits[*].nRMSE`. **Checkpoint-resume from `<ckpt_dir>/last.pt` is implemented** (`smoke_eval.py:130-147`, guarded on `complete`/`dataset`/`epochs_target`/`nrmse_def_hash`/sidecar existence, written at `:390-394`) — verified empirically by the builder's 11 s idempotent re-run. `INSPIRATION.md` cites all 6 `prior_art.citations` URLs, maps each to the measurement it licenses, and quotes the verdict's `quotable_gap` verbatim. Diagnostic findings JSON goes under `outputs_root` via `S2B1_DIAG_OUT` (`smoke_eval.py:382-385`) — the `run_diagnostic.py` convention satisfied through the contract runner, which is better (the number is scored, not self-reported). Seeding: `--seed` drives `np.random.default_rng` for the two control statistics; the reloaded base `run()` sets `torch.manual_seed`/`np.random.seed`. Nothing stochastic runs on GPU (eval only, no dropout), so the absence of an explicit `torch.cuda` seed is immaterial here. |
| 3.5 | SLURM correctness | **PASS** | `bash -n scripts/01_train_eval.sh` → OK; `bash -n scripts/submit.sh` → OK (both run by me, no output = clean parse); `python -m py_compile models_r1/s2_copylf_forensics/*.py` → OK. `--partition=gpu` and `--gres=gpu:h100:1` match `project.yaml` `sbatch.partition`/`sbatch.gres` (typed gres ✓); `--job-name=r1-s2_beyond_copy-B1-s0` matches the convention; `--output/--error` are absolute under `${OUTPUTS_ROOT}/s2_beyond_copy/B1/slurm/%x_%j.{out,err}`; `--time=00:45:00`, `--exclude=hpc-93-36`, `--requeue`, `--mem=32G`, `set -euo pipefail`, `mkdir -p` of eval/ and slurm/, venv activation, all paths absolute. `01_train_eval.sh` takes `SEED=$1` (`${1:?usage}`); `submit.sh` submits seed 0 only. **No `submit_seeds_2_3.sh` is CORRECT** for a `card_type: diagnostic` (program.md §4.3: one run, no seeds 1–2; the three batch-0 seeds are consumed model-side via `S2B1_CKPT_SEEDS`), and `scripts_path.seeds_2_3` is `null` in the card, consistently. The hardcoded `-s0` in the `#SBATCH` line is correct-and-documented (directives cannot read `$1`; only seed 0 is submitted). Walltime is right-sized, not guessed: I timed the M2–M5 kernels at the largest grid (256²: knn 4.5 s, degeneracy 7.1 s, spectral over 8 predictors 12.5 s, EDT 2.3 s, stratify 12.4 s, rescale 1.9 s, pairing 0.8 s ≈ **42 s of CPU per dataset**), and the three checkpoint reloads that dominated the 3m17s CPU-login smoke run on H100 instead. Five datasets should land well inside 45 min, and a TIMEOUT is recoverable because each dataset's own `last.pt` short-circuits on resubmit. Native grids confirmed ≤ 256 for all five datasets (96, 128, 256, 256, 256), so the `work_grid == native` assumption behind the `max|target - y_test| == 0` hard stop (`smoke_eval.py:229-234`) holds. |
| 3.6 | Smoke-test evidence | **PASS** | `build_notes[1]` cites the full `score_panel.py --family_dir ... --epochs 0 --seed 0 --no_cache --env ...` command at the card's own tier, re-run *after* the ADR-0008 amendment, and all three artifacts exist in the worktree: `scratchpad/contract_smoke.json` (exit 0, `test_hf` nRMSE 1.3113524474983618, skill 3.9804, `split=test_hf`, `metric_source=per_sample_mean`, env block = amended recipe), `scratchpad/contract_smoke_diagnostics_ext__helmholtz_2d.json` (full M1–M5 sidecar, seam `abs_delta 0.0`, `lf_at_inference=false` × 3 seeds, `n_forward_calls_train: 0`), `scratchpad/smoke_run.log` (`real 3m17.165s`). Outputs root and `eval/results/s2_copylf_forensics/` were cleaned afterwards (verified empty), so the H100 job recomputes from scratch and no login-node number can leak into the result. |
| 3.7 | Blast radius | **PASS** | `git diff round1-substrate..HEAD --stat` = 12 files, 1886 insertions, 0 deletions, confined to `models_r1/s2_copylf_forensics/` (5), `scripts/` (2), `notes/` (2), `scratchpad/` (3). No substrate file, no main-tree file, no `.gitignore`d artifact. `git status --porcelain` is empty at `build_commit`. |

## Focus items requested by the orchestrator

**1. Diagnostic integrity — CONFIRMED.** The card trains nothing and the claim is enforced
three ways, not asserted: (a) `base_reload.py:131-136` refuses to run any family that has
no module-level `_train` to tripwire, then replaces it with a raiser whose message names
the family/dataset/seed; because `mf_fno_transfer_film.run()` calls `_train` unconditionally
on the not-resumed branch (`smoke_eval.py:162-170`), a failed resume aborts *before* the
`torch.save` on line 171 — so a botched resume can neither retrain nor overwrite a frozen
champion; (b) an independent forward-hook counts training-mode forward passes and raises if
any occurred (`base_reload.py:188-194`); (c) the reproduced metric must match the recorded
batch-0 value. Observed in the smoke: `n_forward_calls_train: 0` for all three seeds.
Copy-LF seam: recomputed 0.3294501260438018 vs `eval/copylf_baselines.json`
0.3294501260438018, `abs_delta` **exactly 0.0**, tolerance kept literal at 1e-9, and the
baselines file's `_nrmse_def_hash` is checked before the comparison. Scored split: `splits`
contains exactly one `test_*` key — `test_hf` = `knn1`, the training-free 1-NN-in-X lookup
(`smoke_eval.py:316-320`, plus a hard stop at `:122-126` if `S2B1_KNN_K` ever loses the 1);
every other predictor, including both certified models, lands under `ref_*`, which
`_extract_test_metric` ignores. That is exactly what the card specifies.

**2. Pinn strip — COMPLETE, not gated.** `ba48712` removes the `_train_pinn` tripwire loop,
the `PINN_POISSON` gate and its checkpoint-`pinn` provenance assertion, the `pinn` key from
`inspect_checkpoint`, and the pinn text from the manifest, INSPIRATION, docstrings and the
`--env` value; the smoke evidence was regenerated without it. The replacement is a stricter
single-family interlock (`hasattr(mod, "_train")` or hard stop), so nothing was weakened by
the removal. Grep for `pinn` over the worktree returns hits only in pre-existing substrate
documentation (`.lavish/*.html`, `docs/reports/*`, `docs/proposals/*`) that this diff does
not touch, and in `models_r1/.../INSPIRATION.md` line 59 as an explicit "retired by ADR 0008,
not measured" note. No dead branch, no env knob, no residual code path.

**3. The ≤1e-9 → 1e-3-relative deviation — ACCEPTED.** The interlock's purpose is checkpoint
and data identity, and 1e-3 relative serves that purpose completely: the failure modes it
guards (wrong checkpoint, wrong seed, wrong split, actual retraining) move the number by
O(1) — e.g. the helmholtz seeds sit at rel-L2 6.20 / 3.01 / 4.45, so a seed swap shows up as
a ~50% deviation, 500× above the abort threshold — while the observed cross-hardware float32
noise is 4.6e-7…8.7e-6 relative, 100–2000× *below* it. A literal 1e-9 on a float32 FNO
forward pass compared across P100-recorded and H100-computed numbers is not a check, it is a
guaranteed false abort; keeping it would have made the diagnostic unrunnable. The builder
did the right three things: aborted rather than warned, recorded the card's literal criterion
as the per-checkpoint boolean `repro_exact_1e9` plus the measured abs/rel deltas in the
sidecar so the criterion is still *reportable*, and declared the deviation in-source
(`smoke_eval.py:54-66`), in `build_notes[3]` and in the handoff. The literal ≤1e-9 is kept
where it is achievable (copy-LF, pure numpy — and it passes at delta 0.0), which is the
correct place to draw the line. **Finding S2 (hand-off)**: `repro_exact_1e9` will be `false`
for every checkpoint on every dataset; the analyzer must read it as "the literal criterion,
recorded as required" and not as a failed seam. The `abort_rtol` field is in every entry to
make that unambiguous.

**4. Frozen-checkpoint safety — VERIFIED INDEPENDENTLY.** I re-hashed all 15
`round1/eval/results/mf_fno_transfer_film/ckpt_<ds>_e200_s{0,1,2}/last.pt`: every sha256 and
size matches `build_notes[4]` exactly, and every mtime is still `2026-07-28 20:43…22:15 PDT`
(= the `2026-07-29T03:43…05:15Z` recorded at build time) — i.e. unchanged *through two full
smoke runs that reloaded them*. The containing directories' mtimes are likewise unchanged, so
no file was created or removed inside them. No `_forensics_unused.json` exists anywhere under
`eval/results` (the family also hard-fails if one appears, `base_reload.py:182-186`), because
`finalize_and_write` is monkeypatched before `run()` and the base `run()` — unlike `main()` —
never touches `out_path` itself. The batch-0 *result JSONs* for s0 were rewritten at
2026-07-29 09:41 PDT, but that is the operator's H100 re-certification (checkpoint bytes
unchanged), not this card; it merely explains why the s0 `recorded_batch0_rel_l2_mean` moved
between the two smoke runs (6.202266 → 6.202329) and it moves the H100 job's repro delta
*down*, further from the abort threshold.

**5. SLURM correctness — CONFIRMED** (see row 3.5; job name, gres, walltime, exclude,
requeue, output paths, `--env` byte-match, and the correctly-absent seeds_2_3 script all check
out).

**6. Guarded surfaces and locked fields — CLEAN.** The diff writes nothing outside the
worktree; the card's `operator_amendments` entry and the mechanics fields (`status`,
`scripts_path`, `output_paths`, `build_commit`, `build_notes`) are the only main-tree changes
and are all legitimate for the builder role. Locked fields (parts 1–4,
`expected_falsification`, `prior_art`, `recipe`, identity fields) are unmodified by this
review; `recipe.env.S2B1_BASE_FAMILIES` correctly reflects the ADR-0008 amendment.

## Suggestions (non-blocking, for the next stage)

- **S1 (script hygiene, orchestrator or a follow-up build)** — add
  `export ROUND1_EVAL_RESULTS="$OUT_DIR/eval/results"` (and optionally `ROUND1_EVAL_CACHE`)
  before the `score_panel.py` call in `scripts/01_train_eval.sh`, so this diagnostic writes
  no new bytes into `round1/eval/results/` — the tree that holds the frozen batch-0
  certification artifacts it reloads. `S2B1_CKPT_ROOT` is independent, so the reload path,
  the seam checks and the requeue short-circuit are all unaffected. Submit-blocking: **no**.
- **S2 (analyzer hand-off)** — `repro_exact_1e9 == false` everywhere is the *expected,
  declared* outcome of the accepted deviation, not a seam failure; the meaningful field is
  `rel_delta` versus `abort_rtol = 1e-3`.
- **S3 (maintainer / leaderboard)** — the scored `test_hf` number this card produces is a
  1-NN-in-X **lookup table**, not a model (helmholtz smoke: skill 3.98). `manifest.json`
  carries `"diagnostic": true` and the split carries a `predictor_note`, but no leaderboard
  tool reads either yet (`round1/tools/` is empty). `s2_copylf_forensics` must be excluded
  from the provisional leaderboard and from top-3 eligibility.

## Checklist

- [x] Handoff written with verdict + 7 findings (`<worktree>/notes/handoff_code_reviewer.md`)
- [x] Card status set to `reviewed_suggest`, matching the verdict
- [x] Exactly one `review_notes[]` entry appended
- [x] Locked fields verified byte-identical after the card write
- [x] `bash -n` actually run on every script (both OK; `py_compile` on all 4 family modules OK)
- [x] No code or script modified by this review
