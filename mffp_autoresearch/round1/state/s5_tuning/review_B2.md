# code-reviewer — s5_tuning-B2 (tuning_target_scaler, 5 arms + ADR-0007 screen)

- **Reviewed diff**: `round1-substrate..a55c788eec97683061b8a049610de59377cfd332`
- **Worktree**: `/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch/round1/worktrees/s5_tuning/B2`
- **Verdict**: `SUGGEST` → card `status: reviewed_suggest`. **Submit as-is** (screen first, then seed 0).
- **UTC**: 2026-07-29T23:41:51Z

---

## Verdict paragraph

This build is the cleanest knob card in the stream so far and I could not find a
single drift between card part 3 and the code. `model.py` is byte-identical to
the base family (md5 `ebfc56ce69282984b601a806ba735b10`, verified against both
the working tree and `git show 967562e:…`), the base `smoke_eval.py` md5 the
card cites (`bd44251c…`) is correct, and the full `diff -u` base→worktree
contains exactly the six declared deltas and nothing else — no optimizer,
loss, schedule, batch-size, `WORK_CAP` or `modes_cap` change, no learnable
affine, and the HF test field provably never enters a scaler (arm A3 reads only
the test split's LF field, i.e. the same field copy-LF is scored on). All five
arm definitions match the card's arm table term for term, including the two
places where the card is most easily fudged: A2 `zscore` really does add the
centring term and denormalizes with the *same* constants
(`normalize=(t-mu)/sd`, `denormalize=t*sd+mu`, `sc["test"] is sc["hf"]`), and
A3 `revin_lf` really is per-sample `max|LF_i|` on the working grid for both
stages plus the card's *declared* `maxabs` fallback with
`scaler_fallback: true` + a reason string on splits with no usable LF (the
availability predicate checks train-LF row coverage, row-identical condition
vectors, and test-split LF presence — `ifc_poisson` fails two of three, as
declared). Arm isolation is belt-and-braces and I reproduced the reasoning:
`score_panel.py:87-88` derives both the per-dataset JSON path and `ckpt_dir`
from (family, dataset, epochs, seed) *only*, so without the card-required
`scaler_<mode>` subdir **and** `scaler_mode` in the resume `same_cfg` gate, arm
k would load arm k−1's `stage="done"` checkpoint, set `trained=True` and skip
training entirely — the builder implemented both, and the cross-arm refusal
drill (`scratchpad/resume_crossarm_reject.log`) shows the gate firing on a
planted checkpoint at the contract path. I independently re-verified every
contract-tier number in `CONTRACT_SMOKE_EVIDENCE.md` from the committed
`score_panel.py` JSONs (all `cached: false`, `split: test_hf`,
`metric_source: per_sample_mean`), including the two bitwise
default-equivalence proofs — `ifc_poisson` `0.4900025652737081` and `fluid`
`0.3700180774087174`, each identical to the last digit against the untouched
factory family, across *both* loader layouts. I judge the **helmholtz
equivalence deferral acceptable-with-verification-in-screen, not a submission
blocker**: `00_screen.sh:100-101` runs both families on exactly
`ext__helmholtz_2d,ifc_poisson` with the env unset before `submit.sh` may run,
the `maxabs` path is a literal `t/scale` ÷ `t*scale` with the base's own
`max(|Y|,1e-8) or 1.0` statistic and has no dataset-dependent branch that could
make helmholtz behave differently, and `screen_table.py` computes
`max|ΔnRMSE|` at full precision with `pass = (max_abs_diff == 0.0)` and prints
`DIVERGED — the default path is NOT the anchor's` at the top of
`screen_table.md` and to stdout. The verdict is `SUGGEST` rather than `PASS`
for two reader-side reasons, both for the next stage rather than the builder:
`screen_table.json`'s `decision{}` block does **not** carry the
default-equivalence verdict (so an orchestrator that reads only `decision`
could submit over a FAILED equivalence), and the card's `broken` rule is much
weaker at panel scale than the builder's dry-run implies — the builder's
synthetic dry-run used `ifc_poisson` alone as the "panel", so A4's 103× blow-up
*was* the geomean; over the real 6-dataset panel the same blow-up dilutes to
≈2.4× and A4 would **not** be flagged (I reproduced this: A0 gm 4.31 vs A4 gm
10.48 → 2.43× < 3×). Neither is a §5, recipe, or contract violation, and
neither can promote a broken arm in practice, but both must be on the record
before the screen is read.

---

## Findings table (the seven questions)

| # | Question | Verdict | Finding |
|---|---|---|---|
| 1 | Card–implementation alignment | **PASS** | Every part-3 item traces to code: family copy at `967562e` (`recipe.base_commit`) ✓; B1's three plumbing deltas (`REPO_ROOT = HERE.parents[1]/"mf_field"/"factory_mffp"` at `smoke_eval.py:80`, knob provenance in `extra`, periodic `last.pt` + config-match gate) ✓; the ONE behavioural change = `MFFP_TARGET_SCALER` selection, default `maxabs` (`scalers.py:63` `MODE_DEFAULT`) ✓; `modes_cap` held at 12 ✓; no learnable affine (grep: no `nn.Parameter`/`Linear` in `scalers.py`) ✓; HF test field never in any scaler (`build()` takes only `Y_lf, Y_hf`; A3's `test` array is the test **LF** field) ✓. Screen: 5 arms × panel @ 2 epochs seed 0 (`00_screen.sh:104-108`) ✓; item (a) equivalence pair on `ext__helmholtz_2d,ifc_poisson` (`:53,:100-101`) ✓; item (b) guard with the promoted env — implemented as a **superset**, guard for every arm (`:111-116`) ✓; item (c) `precheck_scale_ratio.py` → `notes/precheck_scale_ratio.json` (`:120-121`) ✓; `preds_test.npz` dumped (`smoke_eval.py:393-398`) ✓; both knobs in ONE `--env` (`:84`, `01_train_eval.sh:72`) ✓. The fixed promotion rule is transcribed verbatim into `screen_table.py:10-16` and implemented literally: `RANK_ORDER=["A2","A1","A3","A4"]`, `NEVER_PROMOTED="A0"`, `BROKEN_FACTOR=3.0`, `close calls never reorder` (no score-based sort anywhere — `survivors[0]` is taken from the fixed order). |
| 2 | Recipe fidelity | **PASS** | `recipe.base_family/base_commit/family_dir/datasets/epochs/seeds/env` all appear exactly: `--datasets panel --epochs 200` (`01_train_eval.sh:68-69`), `SCALER="${2:-zscore}"` + `MODES_CAP=12` (`:34-35`) → `--env MFFP_TARGET_SCALER=zscore MFFP_MODES_CAP=12` verbatim, `submit.sh` seed 0 only. **No silent hyperparameter**: `hidden 64 / blocks 4 / bs 16 / lr 1e-3,3e-4 / wd 1e-5 / clip 1.0 / WORK_CAP 256 / FLOOR 1e-8` are all the base family's (confirmed by `diff -u`: `SMOKE` dict unchanged apart from the env-read `modes_cap`); `P995_Q=99.5` and the four arm statistics are the card's arm-table text; `CKPT_SAVES_PER_STAGE=5` is declared in build_notes as B1's carried-over builder choice. Three builder-side constants sit outside the card but are inert: `_floor_per_sample`'s 1e-8 on A3's per-sample scales (the base family's own `FLOOR`, undocumented in build_notes — cosmetic), and `screen_table.py`'s `>2× A-def` guard **flag** (explicitly "a FLAG, not an auto-reject", `screen_table.py:32-33`, and it cannot reorder promotion). |
| 3 | §5 immutable compliance | **PASS** | Diff touches zero files under `round1/eval/`, `project.yaml`, `program.md`, `docs/adr/`, `subagents/`, or the guarded factory surfaces (`factory_root/{eval,baselines,references,scripts,data}`, `factory.md`, `mf_field/akash/**`) — see finding 7. No data regeneration: `precheck_scale_ratio.py` writes only its own JSON/MD (`grep` for `write/savez/open(…,"w")` → lines 157/168/182 only) and the family writes only under `ckpt_dir` (inside `ROUND1_EVAL_RESULTS`, i.e. the outputs root). **All scoring routes through `score_panel.py`** in every script and every evidence row; the only two direct `smoke_eval.py` calls are the resume drill, which yields no card number and is labelled as such. Seeds: `{0}` in-round, `{1,2}` in `submit_seeds_2_3.sh` (ADR 0004). Epochs: 200 = smoke tier in `01_train_eval.sh`, 2 = contract tier in `00_screen.sh` — no third budget. **No pre-falsified lever** re-proposed (WNO swap / LF low-mode freezing / diffusion prior are all absent; output-target scaling is not on the §5 list). §12.5 "knobs only" respected: `model.py` byte-identical ⇒ no architectural change, `F.mse_loss` untouched ⇒ no new loss, no new paradigm. Arm A3 is the only arm that widens the information set (one inference-available LF scalar per test sample); the card's prior-art row (i) licenses exactly that ("*K only if the scale comes from an inference-available statistic with zero new parameters*"), it is rank-3, and it is a measured no-op on the four sharp sets (`hf_lf_ratio_cv` 0.0024–0.0173) — not an immutable violation, but the analyzer should carry the caveat if A3 is ever promoted. |
| 4 | Contract compliance | **PASS** | `manifest.json` valid JSON with `name/description/supports/frozen` ✓. `smoke_eval.py` exposes the exact 6-arg CLI (`--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed`, `:419-425`) ✓. **Checkpoint-resume from `<ckpt_dir>/last.pt` implemented**: primary path `<ckpt_dir>/scaler_<mode>/last.pt` with the bare contract path `<ckpt_dir>/last.pt` read as a fallback (`:314`), atomic `tmp`+`os.replace` save, `stage∈{pretrain,finetune,done}` with optimizer/scheduler/shuffle-generator restore, and a `_state_dict_compatible` pre-check so a stale ckpt cannot half-load ✓; drilled by SIGKILL mid-pretrain (`resume_drill_verdict.json`: killed at `pretrain` epoch 1/5, re-run printed `[resume] mid-run checkpoint … stage=pretrain epoch=1/5` then `LF-pretrain continues from epoch 1/5`, finite `rel_l2_mean 0.2688`) ✓. `same_cfg` gate = `epochs_target ∧ grid ∧ modes_cap ∧ scaler_mode` (`:317-321`) — the card's requirement, and the cross-arm drill shows it refusing a planted `zscore` ckpt under `MFFP_TARGET_SCALER=maxabs` ✓. Seeding: `torch.manual_seed(args.seed); np.random.seed(args.seed)` (base-family line; `torch.manual_seed` also seeds CUDA), plus `PYTHONHASHSEED`/`CUBLAS_WORKSPACE_CONFIG` from `score_panel.py:89-91`. `INSPIRATION.md` present (101 lines) and cites the card's `prior_art` sources including sklearn scalers, neuraloperator `UnitGaussianNormalizer`, RevIN, The Well (`2412.00568`) and `2511.01830`. |
| 5 | SLURM correctness | **SUGGEST** | `bash -n` run by me on all five card scripts + the two scratchpad drivers — **all clean** (`scripts/00_screen.sh OK`, `01_train_eval.sh OK`, `submit.sh OK`, `submit_screen.sh OK`, `submit_seeds_2_3.sh OK`, `scratchpad/smoke_driver.sh OK`, `scratchpad/smoke_revin.sh OK`); `py_compile` clean on all `scripts/*.py` + the three family `.py`. Partition `gpu` ✓, typed `--gres=gpu:h100:1` ✓ (= `project.yaml sbatch.gres`, ADR 0005), `--requeue` + `--exclude=hpc-93-36` (documented precedent, `state/gates.md`, accepted in review_B1) ✓, `--mem=32G`, `--cpus-per-task=4`, `--output/--error` under `${OUTPUTS_ROOT}/s5_tuning/B2/slurm/%x_%j.{out,err}` ✓, every path absolute ✓, `01_train_eval.sh` takes `SEED="${1:?…}"` ✓, `submit.sh` = seed 0 only ✓, `submit_seeds_2_3.sh` present (seeds 1,2, explicitly not in-round) ✓. `--time` right-sized against the ledger: `02:00:00` vs the s5-B1 h100 panel@200 of **36.62 min** (3.3× headroom), `01:00:00` for the screen vs the s6-B1 5-variant contract screen of **8.6 min**. Three non-blocking notes: **(S1)** the in-file `#SBATCH --job-name=r1-s5_tuning-B2` (`01_train_eval.sh:19`) omits the seed; conformance to `r1-{stream}-B{N}-s{seed}` depends on `submit.sh:13`'s `--job-name` override, so a bare `sbatch 01_train_eval.sh 0` yields a name the maintainer's matcher can miss — **identical to B1's accepted precedent**. **(S2)** the job name carries no arm, so a promoted-non-A2 run is indistinguishable from an A2 run in `squeue`/`sacct` (it *is* auditable everywhere else — see finding 5b below). **(S3)** `00_screen.sh:120-123` writes `notes/precheck_scale_ratio.json` **inside the worktree** from a batch job, overwriting a tracked file and leaving the worktree git-dirty after the screen; slurm_rules §6 hygiene would prefer the outputs root as the primary target (the script already copies to `$SCREEN_DIR`). |
| 6 | Smoke-test evidence | **PASS** | build_notes cites the contract-tier `score_panel.py` command shape, and every result file exists in `<worktree>/scratchpad/` (10 `contract_smoke_*.json`, 7 `provenance_*.json`, `CONTRACT_SMOKE_EVIDENCE.md`, `resume_drill_verdict.json`, `resume_crossarm_reject.log`, `precheck_panel.out`). I re-parsed all ten score_panel JSONs myself and every number in build_notes and the evidence memo matches to the last digit, with `cached: false` on all of them; A4's `50.586683638221594` (skill 1405.19) and A3's exact equality with A0 on `ifc_poisson` (declared fallback) both reproduce. `check_knob_provenance.py` genuinely tests the trap (`score_panel.py:238` `--env nargs="*"` with no `action="append"` — I verified that line) and was exercised positive/negative/fallback. |
| 7 | Blast radius | **PASS** | `git diff round1-substrate..HEAD --stat` = 44 files, 2987 insertions, 0 deletions, entirely under `models_r1/mf_fno_transfer_film_scaler/` (5), `scripts/` (8), `notes/` (4), `scratchpad/` (27). No substrate contamination, no "substrate fix" commit, `git status` clean. |

### 5b — the optional-arm-arg deviation (`01_train_eval.sh:34`), judged

`SCALER="${2:-zscore}"` defaults to the recipe arm, so the **safe** path is the
default and a non-A2 promotion needs no emergency code edit. I judge this an
acceptable deviation from a strict "recipe arm hard-coded" reading, because the
substitution is auditable in six independent places: the result filename
(`result_panel_${SCALER}_s${SEED}.json`, matching
`output_paths.eval_result_pattern`), `ROUND1_EVAL_RESULTS=…/scaler_${SCALER}`,
`score_panel.json.env`, every per-dataset JSON's `scaler_mode` +
`scaler_mode_source`, the `scaler_<mode>` ckpt subdir recorded as
`ckpt_dir_arm`, and the job's stdout header. The **fatal** knob assertion at
`01_train_eval.sh:76-80` then refuses to let a run be recorded under an arm it
did not actually train (`--expect_scaler "$SCALER"` with no `--soft`). The one
thing the script cannot check is the *discipline* clause — that the card was
amended before submit. Minimal hardening if anyone wants it later: have
`01_train_eval.sh` read `recipe.env.MFFP_TARGET_SCALER` from the card and abort
unless it equals `$SCALER`. Not required for this submission; it is the
orchestrator's step in ADR 0007 either way.

### 5c — the A4 / broken-arm sensitivity finding (the substantive one)

`screen_table.py` implements the card's `broken` rule **verbatim** (crash /
non-finite / panel geomean > 3× A0), so this is a card-design property, not
implementation drift — but the builder's dry-run overstates what it
demonstrates. The dry-run inputs (still on disk from the build session) used
`ifc_poisson` **alone** as the panel, so A4's geomean *was* its 103×
single-dataset blow-up and the rule fired (`1405.1857 > 3.0x A0 (40.8335)`).
I re-ran `screen_table.py` on synthetic **6-dataset** inputs that keep A4's
observed 103× on `ifc_poisson`, ~2× on helmholtz and ~1× on the four sharp
sets: A0 gm 4.3127, A4 gm 10.4808 → **2.43× < 3×, A4 NOT flagged broken**. The
6th root of a single-dataset catastrophe is simply small. Practical exposure is
near zero (A4 is rank 4 and is promoted only if A2, A1 *and* A3 are all broken,
and all three ran finite at contract tier), and A4 is separately caught by the
guard `FLAG` and by any human reading the per-dataset row. But two things follow:
(i) do **not** read build_notes' "the rule fired correctly (A4 broken by the 3×
test)" as evidence that the rule catches A4 at panel scale; (ii) the analyzer
should judge brokenness from the per-dataset table, not the geomean alone.

Two smaller latent soft spots in the same file, both worth the orchestrator's
eyes and neither blocking:

- `a0_geomean_panel is None` (A0 itself crashes) ⇒ `cap = None` ⇒ the 3× test
  silently does not fire for *any* arm, and the md table prints `broken: no`.
  Minimal fix: record `broken_test_evaluable = (a0_gm is not None)` in
  `decision` and treat `False` as blocking.
- `equiv["pass"] = (max_abs_diff == 0.0)` does not require both
  `EQUIV_DATASETS` to be present, so a per-dataset gap would pass on the other
  dataset alone. Unreachable in practice (`score_panel.py` raises on any failing
  dataset ⇒ the whole `equiv_*.json` is missing ⇒ `pass=False`), but the exact
  guard is `and len(ad) == len(EQUIV_DATASETS)`.

---

## Actions handed to the orchestrator (SUGGEST, submit anyway)

1. **Gate `submit.sh` on the equivalence verdict.** After `00_screen.sh`
   finishes, read
   `${OUTPUTS_ROOT}/s5_tuning/B2/screen/screen_table.json` →
   `default_equivalence.pass` and `default_equivalence.per_dataset` (expect
   `bitwise_identical: true` on **both** `ext__helmholtz_2d` and
   `ifc_poisson`). `pass: false`, or `ext__helmholtz_2d` absent from
   `per_dataset`, is a **blocker** — the family's numbers would no longer be
   comparable to the certified 6.703 anchor. `decision{}` does not carry this
   flag, so reading `decision` alone is not sufficient.
2. **Record the promotion in the card before `submit.sh`** (ADR 0007). If
   `decision.requires_recipe_amendment` is `true`, that is a `recipe` change =
   design intent ⇒ `state/blocked.md` per `_shared/card_update.md`, not a
   silent `bash submit.sh <arm>`.
3. When reading the screen table, judge `broken` from the **per-dataset**
   skills, not the panel geomean alone (finding 5c).
4. Expect the worktree to be git-dirty in `notes/precheck_scale_ratio.{json,md}`
   after the screen (finding 5, S3) — that is the screen rewriting its own
   pre-check, not a substrate edit.
