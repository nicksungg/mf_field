# code-reviewer — s1_poisson-B1 (attempt 1)

- **Verdict**: `SUGGEST` → card `status: reviewed_suggest`. **Submit as-is.**
- **Reviewed**: `git diff round1-substrate..d070f86` (18 files, +1557/−0), all
  three scripts, the whole family dir, the eight `scratchpad/evidence/` JSONs,
  both handoffs, and the base family at `mf_field/akash/models/mf_fno_allpairs`
  @`967562e` (read-only, for vendoring and inheritance checks).
- **UTC**: 2026-07-29T17:20Z

## Verdict paragraph

This build implements card part 3 and nothing else. The correction is real and
provable: I re-ran `build_rows` offline against the actual `ifc_poisson` train
split and got exactly the card's table — `two_level` 110 (105 self + 5 cross),
`adjacent` 250 (175 + 75), `allpairs` 280 (175 + 105), `legacy_pairing` 280
(175 + 105) — with `cond_from=target` on the three corrected arms and
`cond_from=source` on `legacy_pairing`, whose 280 rows share bit-identical
targets with `allpairs` and differ in exactly the 105 cross rows. The
no-op-on-aligned claim also holds constructively: on a synthetic index-aligned
two-level ladder, `allpairs` and `legacy_pairing` produce byte-equal `(X, Y)`,
because the corrected path only swaps `cond_cache[s][:n]` for `cond_cache[t][:n]`
and the extra `n = min(n, |X^(t)|)` clamp is vacuous when `|X^(t)| == |Y^(t)|`
(`smoke_eval.py:213-234`). `legacy_pairing` is a faithful reproduction of the
base family's cross-row construction (`cond = Xsrc_list[:n]`,
`n = min(|X^(s)|, |Y^(t)|)` — identical to
`akash/models/mf_fno_allpairs/smoke_eval.py:62-67`) and is *not* quietly fixed.
Vendoring is clean: `backbone.py` is sha256-identical to
`akash/common/backbone.py` (`f56fa802…`, verified by `sha256sum` on both files),
the only `akash` strings anywhere in the family are in docstrings, and the sole
external import is `factory_root/data_adapters` — an ungated, read-only
adapter every round-1 family uses. All three collision traps are closed and
evidenced: per-arm `<ckpt_dir>/mode_<arm>/last.pt` with a `ladder_mode` meta
guard that prints "checkpoint config mismatch … got adjacent, want allpairs"
(`smoke_eval.py:379-419`), per-arm `ROUND1_EVAL_RESULTS` in the job loop
(`01_train_eval.sh:59-60`), and four distinct `code_hash` values in the four
committed contract-smoke JSONs (`8bbc456b` / `2621746d` / `f82a6f57` /
`ff744b97`) — which `score_panel.py:70-71,184` confirms is the mechanism that
keeps the arms' cache entries apart. All four builder deviations are licensed:
the full 200-epoch finetune is card part 3 verbatim (the base used
`epochs // 2` at its line 179), the `mode_<arm>/` subdir is compatible with
`MODEL_CONTRACT.md`'s "check `ckpt_dir` for an existing checkpoint" mandate
(`last.pt` is the *recommended* pattern, and card part 3 orders the arm into
the key), and `CKPT_SAVES_PER_STAGE=5` + `preds_test.npz` are score-neutral and
declared in `build_notes[6]`. `bash -n` is clean on all three scripts and every
family `.py` byte-compiles. The verdict is SUGGEST rather than PASS only for
the `#SBATCH --job-name` nit at `01_train_eval.sh:26` (S1 below, identical to
the accepted s5_tuning-B1 finding) plus three mechanism notes the analyzer
should carry; none of them blocks submission.

## Findings

| # | Question | Verdict | Finding |
|---|---|---|---|
| 1 | Card–implementation alignment | **PASS** | Every part-3 item traces to code: correction → `smoke_eval.py:213-234` (`cond_from` target/source branch); self pairs → `:200-210`; `f = (log fid − log 8)/(log 64 − log 8)` → `_fnorm_fn` `:142-149` (verified `f(8)=0.000`, `f(64)=1.000`); stage 1 joint 200 ep → `:421-428`; stage 2 HF finetune on `(X^(64), f_src=0, f_tgt=1)` identical in every arm → `:340-348, 433-435`; eval query → `:350-356`; the `extra.rows.cond_alignment_max_abs_diff` + row counts → `:186-193, 238-250, 485`. Arm table reproduced offline exactly (110/250/280/280, `cross_pairs` `[[8,16],[8,32],[8,64],[16,32],[16,64],[32,64]]` for `allpairs`, `[[8,16],[16,32],[32,64]]` for `adjacent`, `[[8,64]]` for `two_level`). Measured alignment `{8→16: 0.7394, 8→32: 0.7095, 8→64: 0.5809, 16→32: 0.7016, 16→64: 0.7145, 32→64: 0.6819}` matches `build_notes[1]` to 4 dp. No paraphrase drift; no un-carded behaviour. Note **S2** below. |
| 2 | Recipe fidelity | **PASS** | `family_dir models_r1/mf_fno_ladder` (`01_train_eval.sh:63`), `datasets ifc_poisson` (`:48,64`), `epochs 200` (`:49,65`), `--env MFFP_LADDER_MODE=<arm>` (`:68`) with `ARMS=(two_level adjacent allpairs legacy_pairing)` (`:47`) = `recipe.env._arms` verbatim; `_sweep`'s `export ROUND1_EVAL_RESULTS=<outputs>/eval/results_<arm>` implemented verbatim at `:59`; `--out result_ifc_poisson_<arm>_s<seed>.json` at `:67` matches `recipe.env._sweep` and `output_paths.eval`. `base_family`/`base_commit` echoed in `manifest.json` and result `extra`. Hyperparameter audit: every constant in the family is either in part 3 (hidden 64 / blocks 4 / modes_cap 12 / batch 16 / 1e-3 / 3e-4 / 1e-5 / 1.0, `smoke_eval.py:97-98`), inherited byte-identically from the base (`AdamW`, `CosineAnnealingLR(T_max=epochs, eta_min=1e-6)`, `WORK_CAP=256` — all matching base `:79-86` and `akash/common/mffp.py:39-41`), or declared in `build_notes[6]` (`CKPT_SAVES_PER_STAGE=5`, `preds_test.npz`). Zero silent choices found. |
| 3 | §5 immutable compliance | **PASS** | Diff touches no `round1/eval/`, `project.yaml`, `program.md`, ADR, or subagent-prompt path; nothing under `factory_root/{eval,baselines,references,scripts,data}`, `factory.md`, or `mf_field/akash/**` (`git diff --stat`: 18 files, all under `models_r1/`, `scripts/`, `notes/`, `scratchpad/`; 0 deletions). `sha256sum` on `akash/common/backbone.py` still returns the manifest's `f56fa802…`, i.e. the guarded tree is untouched. No data regeneration; the family only reads `train`/`test` via `load_mf_dataset`. Scoring is routed through `score_panel.py` in the job script and in every committed evidence JSON (`nrmse_def_hash d3d0ade9…`, `metric_source per_sample_mean`, `split test_hf`); no hand-rolled metric and no direct `smoke_eval.py` number enters the card. `recipe.seeds [0,1,2]`, `epochs 200` = smoke tier. No pre-falsified lever (WNO swap / LF low-mode freezing / diffusion prior) is re-proposed — the card's lever is pair-set composition. |
| 4 | Contract compliance | **PASS** | `manifest.json` present (`name`, `description`, `supports ["ifc_raw","npz_l"]` — same token as the base family, `frozen: false`); `smoke_eval.py` exposes exactly the 6-arg CLI (`:490-497`); `INSPIRATION.md` cites the card's `prior_art` set (li2020fno, perez2018film, herde2024poseidon = the `nips.cc/.../95731` all2all citation, li2022ifc) and reproduces the published-vs-open split. Checkpoint resume **implemented**: `last = ckpt_dir/"last.pt"`, `if last.exists(): torch.load(...)` with finished / mid-`joint` / mid-`finetune` branches restoring `opt`/`sched`/generator state and `start_ep` (`:379-419`, `:286-291`), atomic `os.replace` save (`:257-262`). Evidence corroborates all three paths (`resume_allpairs.json` reproduces `0.36541855303669557` exactly; `midstage_resume_family_result.json` carries `ladder_mode=adjacent`, 250 rows). Seeding: `torch.manual_seed`/`np.random.seed`/`torch.cuda.manual_seed_all` all from `--seed` (`:317-319`); `PYTHONHASHSEED` is set by the eval layer. Note **S3**. |
| 5 | SLURM correctness | **SUGGEST** | `bash -n` run by the reviewer: `bash -n scripts/01_train_eval.sh => OK`, `bash -n scripts/submit_seeds_2_3.sh => OK`, `bash -n scripts/submit.sh => OK`. Partition `gpu` + typed `gres=gpu:h100:1` match `project.yaml sbatch:` / ADR 0005; `--time=02:00:00` = ADR 0005 default and is ~2 h against a `timing_ledger.json` analog of 0.78–0.98 min per `ifc_poisson`@200ep run (p100), so 4 arms fit with large margin; `--requeue` + `--exclude=hpc-93-36` have documented precedent (`state/gates.md:38`, s5_tuning-B1 review). `--output/--error` are absolute under `${OUTPUTS_ROOT}/s1_poisson/B1/slurm/%x_%j.{out,err}` and both `submit*.sh` `mkdir -p` that dir before `sbatch`. `01_train_eval.sh` takes `SEED="${1:?…}"`; `submit.sh` is seed 0 only (ADR 0004); `submit_seeds_2_3.sh` exists and is parked for the end-of-round pass. Every path is absolute; `set -euo pipefail` present. **S1 (non-blocking)**: the in-file `#SBATCH --job-name=r1-s1_poisson-B1` (`:26`) omits `-s{seed}`; only the `--job-name` overrides at `submit.sh:9` and `submit_seeds_2_3.sh:17` produce the `r1-{stream}-B{N}-s{seed}` form the maintainer matches on — never `sbatch 01_train_eval.sh 0` directly. |
| 6 | Smoke-test evidence | **PASS** | `build_notes[2]` cites the contract-tier command per arm (`score_panel.py --family_dir … --epochs 2 --seed 0 --env MFFP_LADDER_MODE=<arm> --no_cache`) and all four result files exist and are committed at `scratchpad/evidence/contract_smoke_{two_level,adjacent,allpairs,legacy_pairing}.json`, each exit-0 with a finite `test_hf` nRMSE (0.378663 / 0.387538 / 0.365419 / 0.365150), `metric_source per_sample_mean`, and a **distinct `code_hash`** — the direct proof that `MFFP_LADDER_MODE` enters the cache key. Four further drill artifacts are committed (`resume_allpairs`, `crossarm_two_level`, `family_result_two_level_shared_ckptdir`, `midstage_resume_family_result`); I spot-checked their contents rather than re-running, and they match `build_notes[3]`'s claims (cross-arm run under the `results_allpairs` tree wrote `…/mode_two_level/last.pt` with `rows.n_rows_total=110`). |
| 7 | Blast radius | **PASS** | `git diff round1-substrate..d070f86 --stat`: `models_r1/mf_fno_ladder/` (5), `scripts/` (3), `notes/` (2), `scratchpad/evidence/` (8). Nothing else; no substrate "fix" commits; `git status --porcelain` in the worktree is empty (HEAD == `build_commit`). |

## Non-blocking notes for the debugger / analyzer

- **S1** — job-name header nit, see Q5. Submit via `scripts/submit.sh`, not by
  `sbatch`-ing `01_train_eval.sh` directly.
- **S2 (mechanism, checked and benign for the arm contrast; real for
  interpretation)** — the stage-1 target scaler is
  `max|Y_all|` over the arm's row set (`smoke_eval.py:359`, inherited from base
  `:147`). I computed it for all four arms on the real data: **identical**
  (0.077146), because fid 8 is in every level set and dominates — so it is
  *not* an arm confound. But the per-fidelity field magnitudes are
  `max|Y|` = 0.0773 / 0.0237 / 0.0069 / **0.00184** at fid 8/16/32/64, a 42×
  spread, and stage 2 renormalizes by `scaler_hf = 0.001836`. The joint stage's
  MSE is therefore dominated by the 8² rows, and the 32²/64² rows the card's
  mechanism argument leans on ("the 32² level's 20 samples are the only
  supervision … covering modes 4–12") enter with ~1–10% of the normalized
  amplitude. This is inherited base behaviour, score-neutral across arms, and
  exactly the kind of thing part 6 should test — but a null on
  `allpairs` vs `two_level` should be read against this amplitude weighting
  before it is read as "the intermediate fidelities carry no information".
- **S3** — the minibatch generator is `torch.Generator().manual_seed(0)`
  (`smoke_eval.py:284`), seed-independent and byte-inherited from the base
  (`:86`). Seeds 1–2 in the end-of-round confirmation will therefore vary only
  through weight init / CUDA nondeterminism, not shuffling; the resulting CI is
  narrower than a fully reseeded protocol would give. Label accordingly.
- **S4 (scope of the negative control)** — `legacy_pairing` reproduces the base
  family's *cross-row* construction only. Per card part 3 ("Stage 2 …
  identical in every arm") it keeps the corrected HF finetune and the added
  self pairs, so its Δ vs `allpairs` isolates the cross-row correspondence and
  nothing else. It must **not** be reported as "the base family's number"
  (0.4657 in `akash/results/bench_full_metrics.csv`). Consistent with
  `recipe.env._primary_arm = allpairs`, the cratered rule applies to
  `allpairs`; `legacy_pairing` cratering is the predicted result.
- **S5 (cosmetic)** — `01_train_eval.sh:52` creates `$OUT_DIR/training`, which
  stays empty: `output_paths.training` actually resolves under
  `$OUT_DIR/eval/results_<arm>/mf_fno_ladder/`. Harmless.
