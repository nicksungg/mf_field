# code-reviewer — s1_poisson-B2 (attempt 1)

- **Verdict**: `SUGGEST` → card `status: reviewed_suggest`. **Submit as-is.**
- **Reviewed**: `git diff round1-substrate..21fdcdade463a4ceebb52a80d329790d8a401af7`
  (31 files, +4619/−0), the full `smoke_eval.py` diff against the vendored B1
  source at `d070f86`, all three `scripts/*`, both `scratchpad/*.sh` drivers,
  all 11 committed evidence JSONs, `scratchpad/resume_drill.log`,
  `scratchpad/contract_smoke.log`, both handoffs, `eval/score_panel.py`
  (read-only), B1's card `build_notes` + B1's four committed contract-smoke
  JSONs, `state/timing_ledger.json`, `project.yaml`, program.md §5/§12.1,
  slurm_rules, ADRs 0004/0005/0009.
- **UTC**: 2026-07-29T22:05Z

## Verdict paragraph

This is the cleanest vendoring-plus-one-knob build the round has produced, and
every load-bearing claim in `build_notes` reproduces under independent check.
The five sha256-16 pins in `recipe._source` match the vendored source exactly
(`git show d070f86:models_r1/mf_fno_ladder/<f> | sha256sum`), `backbone.py` is
still byte-identical to the guarded `akash/common/backbone.py`
(`f56fa8029fad2ffb503d1cd5905359ea34f2ed1b1853e26ac22428a64c02f2ec` on both
files), and post-edit `backbone.py` and `model.py` are **unchanged** — their
current sha256-16 are still `f56fa8029fad2ffb` / `740ed992efcda53e`, so the
scaler knob provably lives in `smoke_eval.py` only. The B1-reproduction gate is
not merely "within 10 %": B2's committed contract smokes are **bit-for-bit**
equal to B1's committed artifacts —
`two_level__shared 0.378663124272829` vs B1's
`scratchpad/evidence/contract_smoke_two_level.json 0.378663124272829`, and
`allpairs__shared 0.36541855303669557` vs B1's
`contract_smoke_allpairs.json 0.36541855303669557`, all 15 digits — which is the
strongest continuity proof available before a GPU run, and it is structurally
explained (max over a partition of the rows IS the global max, and the
unweighted branch still calls `F.mse_loss(pred, yb)` verbatim; only
`shared_reweight` can reach the weighted expression). The scaler
implementations match card part 3 term for term and, critically, derive from
data and not from card constants: I grepped the family for `125`, `1766`,
`0.0771`, `4.379`, `75.7` and the only hits are in docstrings — the numbers in
the result JSON (`S = 0.07714622467756271`, `level_scaler = {8: 0.077146225,
16: 0.023720205, 32: 0.006939544, 64: 0.0018356895}`, rows `{8:100, 16:100,
32:60, 64:20}` = 280, native RMS ratios `4.378791/4.195748/4.119846`,
end-to-end `75.691`, raw weights `1 / 10.5777 / 123.5855 / 1766.1635`,
normalized `0.0063787/0.0674720/0.7883134/11.2658062`, `mean(w)=1.0000001`,
range `1766.16`) are all computed from `Y_all`. The card's "125" for fid-32 is
`(S/s_32)² = 123.5855` to full precision — **presentation-only**: nothing in the
code reads the card, so the discrepancy cannot touch a number. The new `--env`
trap is real and I reproduced it directly (`argparse` with `nargs="*"` and no
`action="append"`: `--env A=1 --env B=2 → ['B=2']`, `--env A=1 B=2 →
['A=1','B=2']`), the single-flag fix is applied in **both** places that invoke
`score_panel.py` (`scripts/01_train_eval.sh:93`,
`scratchpad/run_contract_smoke.sh:18` — grep shows no other `--env` call site),
and I exercised the per-arm no-default assertion myself against the committed
evidence JSONs: positive → `[env-guard] OK arm=allpairs__per_level` exit 0,
mismatched arm → `AssertionError: ('allpairs','per_level')` exit 1, missing file
→ `SKIP` exit 0. Per-arm isolation is complete on both dimensions (ckpt subdir
`mode_<MODE>__scal_<SCALER>` exactly as the LOCKED card part 3 item 3 orders —
the builder correctly resolved the dispatch paraphrase `arm_<MODE>__<SCALER>` in
favour of the card; meta guard refuses a planted cross-scaler ckpt; five
distinct `code_hash`). `bash -n` is clean on all five scripts. All 17 locked
card fields are byte-identical to the starter's commit `1043ccb`. The verdict is
SUGGEST rather than PASS for one **analysis-affecting** mechanism caveat the
card's own dichotomy omits (S1 — `per_level` silently also fixes a
stage-1↔stage-2 unit discontinuity that `shared_reweight` does not, so the 5th
arm does not cleanly isolate the two channels the card names), plus three
smaller notes; none of them blocks submission or requires a code change.

## Findings

| # | Question | Verdict | Finding |
|---|---|---|---|
| 1 | Card–implementation alignment | **PASS** | Every part-3 item traces to code. Item 1 (per-row `scal`): `smoke_eval.py:525-531` builds `tgt_level` from `rows_info["row_blocks"]` (`build_rows:278-303` tags `tgt` on every self and cross block) with a hard `raise SystemExit` on a row-count mismatch (`:532-536`); `level_scaler[f] = max(|Y_all[tgt==f]|.max(), 1e-8)` at `:538-539`; `shared` = `max(level_scaler.values())` `:543`; `per_level` = per-row lookup `:544-546`; `shared_reweight` = shared `scal` + `w ∝ (S/s_f)²` mean-normalized `:549-552`, loss `(wb*(pred-yb)**2).mean()` at `:383-387` (= card's `mean(w_b·(pred − y/S)²)`, since `yb = y/S`). Item 2 (stage 2 untouched): `scal_ft` is a constant `scaler_hf` vector `:568` and `weights=None` is passed explicitly `:655`. Item 3 (both traps): ckpt key `:594`, meta `:598-601`, guard `:607-616`, per-arm `ROUND1_EVAL_RESULTS` `01_train_eval.sh:85`. Item 4 (all four instrumentation pieces): `_scaler_instrumentation` `:404-441`, `_ftgt_sweep` over `FTGT_SWEEP=(0,1/3,2/3,1)` `:444-482`, `preds_test.npz` carried `:683-685`. The five-arm table, the primary arm and the validity gate all appear verbatim in the job script's arrays (`ARM_TAGS/ARM_MODES/ARM_SCALS`, `:74-76`). No paraphrase drift found. See **S1**. |
| 2 | Recipe fidelity | **PASS** | `family_dir models_r1/mf_fno_ladder_norm` (`01_train_eval.sh:89`), `datasets ifc_poisson` (`:78,90`), `epochs 200` (`:79,91`), `seed $SEED` with `submit.sh` = seed 0 (`recipe.seeds [0]`), `base_family mf_fno_ladder` + `base_commit d070f86…` echoed in `manifest.json` and in every result JSON's `extra`. `recipe.env` is implemented **exactly**: the five `_arms` in `_arms` order, the `_sweep` sentence verbatim (per-arm `ROUND1_EVAL_RESULTS=<outputs>/eval/results_<tag>`, `--out result_ifc_poisson_<tag>_s0.json`, ckpt `mode_<m>__scal_<s>/last.pt`, meta-guard extended to the scaler), and the `_sbatch` header (partition gpu, `gpu:h100:1`, `02:00:00`). The `--env` flag carries the two knob names verbatim. Hyperparameter audit: zero new hyperparameters — the `SMOKE` dict, `AdamW`, `CosineAnnealingLR(T_max=epochs, eta_min=1e-6)`, `WORK_CAP`, `CKPT_SAVES_PER_STAGE=5` and the `torch.Generator().manual_seed(0)` shuffle generator (`:365`) are all untouched by the diff (inherited from B1/akash); the only new constants are `LADDER_SCALERS`, `LADDER_SCALER_DEFAULT="shared"` and `FTGT_SWEEP`, all three quoted from card part 3. No silent choice found. See **S4**. |
| 3 | §5 immutable compliance | **PASS** | Diff touches no `round1/eval/`, `project.yaml`, `program.md`, ADR or subagent-prompt path, and nothing under `factory_root/{eval,baselines,references,scripts,data}`, `factory.md` or `mf_field/akash/**` — `git diff --name-only` top-level components are exactly `models_r1 notes scratchpad scripts`, 0 deletions, and `sha256sum akash/common/backbone.py` still returns `f56fa802…503d1cd…`. No data regeneration: the family only reads `train`/`test` through `load_mf_dataset`, and `n_ft = min(|X_hf|,|Y_hf_tr|)` (`:509`) consumes the dataset's own 5 HF train samples — no extra HF. Scoring routed through `score_panel.py` in the job script and in all five committed smoke JSONs (`nrmse_def_hash d3d0ade9…`, `metric_source per_sample_mean`, `split test_hf`); the eval path is byte-unchanged (`pred = model(xb) * scaler_hf`, `:669`), so the knob cannot touch the metric. Seeds `[0]` per ADR 0004 with `{1,2}` parked; epochs 200 = `tiers.smoke_epochs`, contract smoke 2 = `tiers.contract_epochs`. **No pre-falsified lever re-proposed**: the levers are stage-1 target normalization and pair-set composition — not the WNO backbone swap, not LF low-mode freezing, not a diffusion prior. **ADR 0009 clean**: `level_scaler` is an empirical statistic of the training targets, h² is explicitly NOT hard-coded (prior-art verdict (ii)), and test time needs only `scaler_hf` (a train-split statistic) — no governing equations anywhere. |
| 4 | Contract compliance | **PASS** | `manifest.json` present with `name`/`description`/`supports ["ifc_raw","npz_l"]` (same token B1 shipped)/`frozen:false`, plus `env_knobs` documenting both knobs and their defaults and a `checkpoint_key` field. `smoke_eval.py:726-731` exposes exactly the 6-arg CLI (`--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed`). `INSPIRATION.md` cites **all 11** of the card's `prior_art.citations` (S0045782523007892:107, 2605.07375:111, smt mfk:114, PMC11985099:118, 2504.05493:120, 2602.01176v1:126, frontiersin fmats.2019.00061:127, 2507.07292:128, 2405.17260v2:129, 2402.18846v1:130, 2407.07218:140). **Checkpoint-resume implemented**: `last = ckpt_dir/"last.pt"` under the arm subdir, `if last.exists()` with finished-/mid-`joint`/mid-`finetune` branches restoring `opt`/`sched`/generator/`epoch` (`:597-637`), atomic save (`_save_ckpt`), and the drill log proves the mid-stage path end-to-end (`[resume] joint[allpairs|per_level] continues from epoch 1/4`, exit 0, no epoch-0 restart). Seeding from `--seed` for numpy/torch/torch.cuda (`:481-483`); `PYTHONHASHSEED` set by the eval layer. Card is `card_type: model`, so `submit_seeds_2_3.sh` is required — present, and `scripts_path.seeds_2_3` points at it. |
| 5 | SLURM correctness | **SUGGEST** | `bash -n` run by me on all five scripts, all clean: `bash -n scripts/01_train_eval.sh → OK`, `scripts/submit.sh → OK`, `scripts/submit_seeds_2_3.sh → OK`, `scratchpad/run_contract_smoke.sh → OK`, `scratchpad/resume_drill.sh → OK` (no output = clean parse; I echoed `bash -n OK` after each). Partition `gpu` + typed `--gres=gpu:h100:1` match `project.yaml sbatch:` and ADR 0005; `--time=02:00:00`, `--requeue`, `--exclude=hpc-93-36` (precedent `state/gates.md:38`), `--mem=32G`, `--cpus-per-task=4`; `--output/--error` absolute under `${OUTPUTS_ROOT}/s1_poisson/B2/slurm/%x_%j.{out,err}`, and both submit wrappers `mkdir -p` that dir before `sbatch`; every path in the body is absolute; `set -euo pipefail`; venv activated; `01_train_eval.sh` takes `SEED="${1:?usage…}"`; `submit.sh` submits seed 0 only with `--job-name=r1-s1_poisson-B2-s0`; `submit_seeds_2_3.sh` exists and is explicitly parked for the end-of-round pass. Serial 5-arm loop with per-arm `ROUND1_EVAL_RESULTS` + per-arm `--out`. Notes **S2** (header job name) and **S3** (walltime headroom), both non-blocking. |
| 6 | Smoke-test evidence | **PASS** | `build_notes[2]` cites the contract-tier `score_panel.py` command per arm (`--epochs 2 --seed 0 --env MFFP_LADDER_MODE=<m> MFFP_LADDER_SCALER=<s> --no_cache`) and the driver is committed at `scratchpad/run_contract_smoke.sh`; **all five** result files exist in `<worktree>/scratchpad/` (`contract_smoke_{two_level__shared,allpairs__shared,two_level__per_level,allpairs__per_level,allpairs__shared_reweight}.json`) plus the five family-level JSONs under `scratchpad/evidence/`. Each is exit-0 with a finite `test_hf` nRMSE (0.378663124272829 / 0.36541855303669557 / 0.40924520412614573 / 0.2817404086094617 / 0.6616470389897807), `metric_source per_sample_mean`, and **five distinct `code_hash`** (`c336f1bc` / `18d30a3d` / `f56e0ceb` / `9b2481f9` / `51875587`) — which `score_panel.py:70-71,184` confirms is the mechanism putting both knobs in the cache key (immutable 5). The two `shared` cells are bit-identical to B1's committed JSONs (verified by reading both files, 15 digits). Every committed JSON shows `ladder_mode_source == "env:MFFP_LADDER_MODE"` and `ladder_scaler_source == "env:MFFP_LADDER_SCALER"`. No cache-collision risk at submit: the e2 cache entries are keyed on `epochs=2`, the job runs `epochs=200`, and `${OUTPUTS_ROOT}/s1_poisson/B2` currently contains 0 files (only the dry-run's empty per-arm dirs), so nothing stale can be mistaken for a result. |
| 7 | Blast radius | **PASS** | `git diff round1-substrate..21fdcda --stat` = 31 files, +4619/−0, top-level components exactly `models_r1/` (5), `scripts/` (3), `notes/` (2), `scratchpad/` (21). No substrate "fix" commit, no `_shared/`, no `eval/`, no `state/`, no `docs/`. `git status --porcelain` in the worktree is **empty** (HEAD == `build_commit` 21fdcda). Card locked-field spot-check: all 17 locked fields (`id … recipe`) are byte-identical to the starter's commit `1043ccb`; the only changed non-locked fields are `status`, `scripts_path`, `output_paths`, `build_commit`, `build_notes` — exactly the builder's allowlist. |

## FOR THE RECORD — the round-relevant `--env` trap

`${ROUND_ROOT}/eval/score_panel.py:238` declares
`p.add_argument("--env", nargs="*", default=[], metavar="KEY=VAL")` **without**
`action="append"`. Reproduced directly:

```
--env A=1 --env B=2   ->  ['B=2']        # first flag SILENTLY DISCARDED
--env A=1 B=2         ->  ['A=1','B=2']  # correct
```

Consequences for any multi-knob card: the dropped knob falls back to the
family default (silent-default drift, which the round forbids) **and** the
dropped knob never enters `code_hash`, so the cache key and the recorded
`env` in the result JSON both describe a configuration that was not run. B1
never hit it because it passed a single knob. B2 hit it on its first smoke
attempt (asked `two_level`, got the default `allpairs`, wrote its checkpoint to
`mode_allpairs__scal_shared`), and closed it two ways: one `--env` flag with
both values, plus a per-arm post-run assertion on
`ladder_mode_source`/`ladder_scaler_source`/`arm_tag`. **Every future card that
passes two or more env knobs must use one `--env` flag with multiple values and
carry the source-assertion.** The eval layer is immutable during the round, so
the fix is at the call site, not in `score_panel.py`.

## SUGGEST items (non-blocking; for the debugger / analyzers)

**S1 — the mechanism arm does not isolate the two channels the card names
(analysis-affecting; for the mechanism-analyzer).** Card part 3 frames
`shared_reweight` as separating "(a) equalizing each level's loss contribution
vs (b) removing the 75.7× gain law from the represented function". There is a
**third** channel the framing omits, and the code makes it visible:
`level_scaler[64] = 0.0018356895307078958` is *identical* to
`scaler_hf = 0.0018356895307078958` (both are `max|Y_hf_train|` on the work
grid — read straight off the committed JSON). So under `per_level`, stage 1's
HF-target units and stage 2's finetune units and the eval rescale
(`pred * scaler_hf`, `:669`) all agree, whereas under `shared`
(and therefore under `shared_reweight`) stage 1 trains in units of `S = 0.0771`
and stage 2 abruptly switches to `0.0018357` — a **42× unit discontinuity
between the two stages** that `per_level` silently repairs and
`shared_reweight` does not. Consequence: `per_level ≫ shared_reweight` is
consistent with B1 part 6's amplitude-channel-capture story **and** with a pure
stage-1↔stage-2 continuity story, so the card's stated inference rule ("if it
≈ `shared`, B1 part 6 is confirmed at production capacity") is not sound as
written. `two_level__per_level` vs `two_level__shared` carries the same
confound. Recommended handling (no new run needed): report the F1/F2 contrasts
as pre-registered, but in part 6 state the three-channel decomposition and use
the `ftgt_output_rms_sweep` — which is exactly the amplitude-channel probe, and
is already instrumented per arm — as the discriminator, since only the
"removing the gain law" story predicts the sweep range collapsing toward ~1×
under `per_level`.

**S2 — header job name omits the seed** (`01_train_eval.sh:53`:
`#SBATCH --job-name=r1-s1_poisson-B2`). The maintainer matches on
`r1-{stream}-B{N}-s{seed}`, which only materializes via the
`--job-name=r1-s1_poisson-B2-s0` override in `submit.sh:8` /
`submit_seeds_2_3.sh:19`. A direct `sbatch scripts/01_train_eval.sh 0` would
produce a name the matcher can miss. Identical to the accepted s5_tuning-B1 /
s6_local-B1 finding and documented in `build_notes[7]`; **the orchestrator must
submit via `submit.sh`, never by sbatch'ing `01_train_eval.sh` directly.**

**S3 — `--time=02:00:00` is ~21× the ledger estimate.** `state/timing_ledger.json`
has the exact analog: s1_poisson B1, `ifc_poisson`, 200 epochs, h100, **4.47 min
for 4 arms** → ~5.6 min for 5. slurm_rules §4 warns oversized `--time` blocks
backfill. Not a builder defect: `recipe._sbatch` (locked) states
`--time=02:00:00` and ADR 0005 makes it the default, so the builder was
required to write it. Note only: if the job pends, the orchestrator may
right-size at submit time (`sbatch --time=00:30:00 …` beats the header, ADR 0005
mechanics) without touching the locked card.

**S4 — `shared_reweight` mean-normalization rescales the global loss by
1/156.77** (`weights = raw_w / raw_w.mean()`, `:551`). This is card-specified
(`mean(w) = 1`) and AdamW is near-invariant to a global loss scale (decoupled
weight decay is unaffected; the Adam update is scale-free except through
`eps = 1e-8`), so the arm is not confounded in any first-order way — but with
`shared` normalization the HF rows' residuals are already ~0.024 in magnitude,
so an `eps`-floor interaction is not impossible. If `allpairs__shared_reweight`
comes back anomalously bad (its 2-epoch plumbing number, 0.6616, is the worst
of the five), the analyzer should consider optimizer-scale before mechanism.
The arm is in no clause, so nothing depends on it.

**S5 — `build_notes[4]`'s env-guard test has no committed log.** The claim
("tested positively, negatively, and on a missing per-run JSON") is true — I
re-ran the guard body myself against `scratchpad/evidence/family_result_*.json`
and got `[env-guard] OK arm=allpairs__per_level` (exit 0), `AssertionError:
('allpairs','per_level')` (exit 1) and `[env-guard] SKIP` (exit 0) — but unlike
the resume drill there is no `scratchpad/*.log` artifact for it. Evidence
hygiene note for future builds; the guard itself is verified.

## Informational (no action)

- `scripts/01_train_eval.sh` deliberately omits `--no_cache` so a requeue is
  idempotent (documented in the header). Correct: the e200 key has never been
  computed for this family, so no arm can be served a stale number.
- `score_panel.py` writes its cache under `${ROUND_ROOT}/eval/cache/` (its own
  default, `ROUND1_EVAL_CACHE` unset). That is the eval layer's designed runtime
  behaviour shared by every card, not an agent edit of `round1/eval/`.
- The batch-shuffle generator is `torch.Generator().manual_seed(0)`
  (`:365`), i.e. seed-independent — inherited from B1/akash **unchanged** by
  this diff. Harmless here (seed 0 only, and identical shuffling across arms is
  if anything favourable for a factorial), but it means the parked
  `submit_seeds_2_3.sh` seeds would vary only in init, not in batch order.
- `resume_drill.log` reports `nRMSE 0.148451` from a **direct** `smoke_eval.py`
  invocation at 4 epochs. Correctly labelled debugging-only in the drill script
  header; it must never reach `5_actual_result` (B1 precedent, same shape).
