# code-reviewer — s6_local-B2 (attempt 1)

**Verdict: SUGGEST** — submit as built; two orchestrator-side actions are required
(one before the screen job, one after the sweep). No card drift, no §5 violation,
no recipe deviation.

**Diff reviewed**: `round1-substrate..caff5c97d7365c2c200daa30f67c6db3b627aee0`
(1 commit, 58 files, +6465/-0).

---

## Verdict paragraph

This build is the strongest I have reviewed in this round, and every load-bearing
claim in `build_notes` reproduced under independent verification rather than being
taken on the builder's word: all six vendoring pins match `git show 3abc0e3:` byte
for byte, `model.py`/`bands.py` are still byte-unchanged post-commit, and the
`local_corrector.py` diff is *only* the `padding_mode` keyword threaded through
`ConvNeXtLiteBlock`/`LocalCorrector`/`PixelGate`. I re-derived the bit-preservation
proof myself (B1's original module vs B2's, same torch seed, state-dict sha256 +
param count, `padding_mode` ∈ {zeros, circular} × grids {(128,128)K7, (256,256)K7,
(64,64)K1}: 12/12 EQ), and then went one step further than the builder did by
running B1's family and B2's `b1_replica` arm end-to-end on `sharp__sod_1d` at 2
epochs: identical corrector loss `5.2848e-02`, identical `alpha=1.500000`,
identical `val_rel_gated=0.031942`, and identical test nRMSE
`0.03227042226587238` to the last digit — with `alpha≠0`, so this exercises the
*trained* path, not the identity path. V1's premise is therefore proven at
contract tier, not merely argued. V2 is decided from committed sidecars: all four
defect datasets are bit-exact against B1 F6 (which I re-read out of
`worktrees/s6_local/B1/scratchpad/turn2_lsi_*.json` — `nrmse_LSI_transfer_only`
matches the card table exactly), `n_params=0` on all four, helmholtz `alpha=0.0`.
The periodicity switch reads `train["field_by_fid"][hf]` only (first 32 samples),
carries no physics, and lands in the diag sidecar. The trust head's features are
`X` + LF stats + own-output stats with a hard `S6ContractError` if the feature
string is tampered; the candidate set is asserted to be exactly
`{persample_head, global_scalar, zero}`; folds come from `default_rng(seed)` so the
torch RNG stages 0-2 depend on is untouched; standardization is in-fold and the
intercept unpenalized. `arm_env.sh` regenerates all five 35-knob blocks from the
card and I diffed the output against `recipe.env._arms` line by line — faithful.
I re-fired all six negative tests and all six raised the right
`S6ContractError` (plus a positive control that correctly did not raise). What
holds this back from PASS is not the science but two submission-mechanics gaps:
`00_screen.sh` is submitted with no wrapper and its `--output` directory does not
yet exist on disk, and `01_train_eval.sh` swallows the validity-gate exit code so
a V1/V2/C3 miss leaves the job in state COMPLETED. Both are one-line orchestrator
actions; neither requires a builder round-trip.

---

## Findings by review question

| # | Question | Verdict | Finding |
|---|---|---|---|
| 3.1 | Card ↔ implementation | **PASS** | Every part-3 item traces to code: 5 arms → `ARM_SPEC` + `s6_env_for_arm`; padding repair → `local_corrector.py` diff; data-driven switch → `periodicity.py`; zero-param floor → `lsi_filter.py` + `run_lsi_arm`; OOF head → `trust_head.py::select_and_fit`; K=1 control → `VARIANTS["pointwise_ctrl"]`. The dropped per-pixel arm is genuinely dropped and replaced by the measurement-only triple (`nrmse_pixel_oof`/`nrmse_persample`/`nrmse_global_scalar`) exactly as part 3 says. Guard legs at 200 epochs for the two `_guard_arms` present. No paraphrase drift found. |
| 3.2 | Recipe fidelity | **PASS** | `arm_env.sh` *generates* the `--env` block from `recipe.env` (base minus `_`-prefixed metadata + `_arms[tag]` deltas), asserts exactly 35 knobs and that `S6_ARM` matches the requested tag; I ran it for all five arms and every value matches the card verbatim. `base_family`/`base_commit`/`family_dir`/`datasets=panel`/`epochs=200`/`seeds=[0]` all honoured. Hyperparameter provenance is complete: recipe knobs, the base family's `SMOKE` dict verbatim, and the flagged builder choices (`N_PROBE=32`, relative `MIN_GAIN`, in-fold standardization, CV-λ argmin, `default_rng` folds). Two cosmetic notes, neither a silent choice: (a) `recipe._sweep` prose says `eval/results_<tag>` while the script uses `eval/results/<tag>` — path-only, score-neutral, and `output_paths.per_arm_results` matches the script; (b) the CV's degenerate-case rule `usable = n_val >= 2*folds → else fall back to global_scalar` is recorded in code and in `cv["note"]` but not in `build_notes`; with n_val=80 it cannot fire on the panel. |
| 3.3 | §5 immutables | **PASS** | No writes to `round1/eval/`, `round1/tools/`, `project.yaml`, `program.md`, ADRs or agent prompts (verified by diff paths and by `git status` on those paths in the main tree). No guarded factory surface (`factory_root/{eval,baselines,references,scripts,data}`, `factory.md`, `akash/**`) touched. Data read-only, reached only via `data_adapters` + `eval/panel_data.py::copylf_prediction`; B1's three leakage tripwires retained and live. All scoring flows through `score_panel.py` → `eval/nrmse.py` (`NRMSE_DEF_HASH d3d0ade9…` recorded); every new quantity is a diag-sidecar key and enters no scored split. Seeds {0} in-round with 1,2 reserved; epochs 200 (`tiers.smoke_epochs`) / 2 (`tiers.contract_epochs`). No pre-falsified lever (WNO swap, LF low-mode freezing, diffusion prior) re-proposed. Vendoring `lsi_filter.py` into the family instead of importing `round1/tools/` is *correct*, not a dodge: `score_panel.py::code_hash` hashes only the family dir, `models/_common`, and `{nrmse,panel_data,score_panel}.py`, so a `tools/` import would be cache-invisible. |
| 3.4 | Contract compliance | **PASS** | `manifest.json` has name/description/supports/frozen (plus the six base pins). `smoke_eval.py` exposes exactly `--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed`. Resume from `<ckpt_dir>/last.pt` implemented and **drilled 4×** (mid-stage-1 kill → resume at 160/200; per-arm dir deleted, bare `last.pt` alone still resumes; completed arm resumes at `stage=done` and reproduces the identical nRMSE). Meta guard covers (arm, variant, padding_mode, kernel, depth, width, path, dataset, seed, epochs_target, grid). Seeding: `random`/`numpy`/`torch`/`torch.cuda` all from `--seed`. `INSPIRATION.md` cites the card's `prior_art` per row with the verdict quoted and the no-novelty claims stated. |
| 3.5 | SLURM correctness | **SUGGEST** | `bash -n` run on all 5 shell scripts — all OK; both python scripts compile. partition `gpu` + typed `--gres=gpu:h100:1` match `project.yaml` sbatch (ADR 0005); `--time` present on both jobs; `--output/--error` under `<OUTPUTS_ROOT>/s6_local/B2/slurm/%x_%j.{out,err}`; every path absolute; `01_train_eval.sh` takes `SEED=$1`; `submit.sh` = seed 0 only and overrides `--job-name=r1-s6_local-B2-s0`; `submit_seeds_2_3.sh` exists and submits seeds 1,2 with correct names. bash 5.1 so the `"${EXTRA[@]}"` empty-array expansion under `set -u` is safe. **F1 (blocking-before-submit, orchestrator action):** `<OUTPUTS_ROOT>/s6_local/B2/slurm/` **does not exist**, and `00_screen.sh` is submitted directly with no wrapper — its `mkdir -p` runs in the job body, after SLURM has already tried to open `--output`. `submit.sh`/`submit_seeds_2_3.sh` both mkdir first, so only the screen is exposed. *Minimal fix:* `mkdir -p /resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch_outputs/round1/s6_local/B2/slurm` before `sbatch scripts/00_screen.sh`. |
| 3.6 | Smoke-test evidence | **PASS** | `build_notes` cites the contract-tier `score_panel.py` command; `scratchpad/run_smoke.sh` shows the real invocation (`--epochs 2 --seed 0 --no_cache`, env from `arm_env.sh`) and the result files exist: `contract_smoke_{5 arms}.json` (each a genuine `score_panel.py` output carrying `code_hash`, the 35-knob `env`, `nrmse_def_hash`, `per_dataset`), 4 × `smoke_lsi_<ds>.json`, 9 diag sidecars, 4 pair records, per-arm logs, and the driver log (all 9 runs OK). |
| 3.7 | Blast radius | **PASS** | Exactly one commit off `round1-substrate` (`round1-substrate` is an ancestor). All 58 paths under `models_r1/`, `scripts/`, `notes/`, `scratchpad/`. Zero substrate contamination. |

---

## The two deviations I was asked to judge

**`--time=04:00:00` vs the brief's `02:00:00` — builder is right, no action.**
`recipe.env._sbatch` is a LOCKED field and specifies `04:00:00` for the sweep; the
builder followed the card over my brief, which is the correct precedence, and
flagged it explicitly. The cost model checks out against
`state/timing_ledger.json` (job 66001535: s6_local-B1, panel × 200 epochs, h100,
17.95 min). If anything the recipe's estimate is *optimistic*: it budgets ~12 min
for two 200-epoch guard legs, but guard is 3 datasets, so those legs plausibly
cost closer to a panel leg each (~30 min total), putting the job near 120-130 min
— which makes `02:00:00` genuinely risky and `04:00:00` the safer read.
`slurm_rules` §4 also names `04:00:00` as the panel × 200-epoch default. The
orchestrator retains control either way: `submit.sh --time HH:MM:SS` passes a
command-line `--time` that overrides the directive, and the job is idempotent and
resumes, so a wall-clock kill is recoverable. If h100 queue pressure is bad,
`--time 02:30:00` is a defensible right-size.

**V1/V2 adjudicated post-hoc by `02_verify_gates.py` — sound design, but the
exit code is currently swallowed.** The soft/hard split is correct: identity-floor
and C3-pairing are *construction* invariants and raise in-process
(`S6ContractError`, C3's message carries `max|dw|` so GPU nondeterminism is
distinguishable from a config divergence); V1/V2 are *reproduction* gates against
another card's numbers, and raising on them would abort a five-arm sweep and
destroy the numbers a debugger needs. The checker itself is faithful — I diffed
its `B1_SEED0` and `B1_F6` tables against `recipe.env._validity_gates` and against
B1's `turn2_lsi_*.json`: all ten values match exactly — and its exit-code contract
(0 pass / 2 ALGO / 3 missing-inputs, with 2 taking precedence over 3) is right.

**F2 (blocking-after-sweep, orchestrator action):** the gate is *not yet binding*
at the job level. `scripts/01_train_eval.sh:109` reads

```bash
    --out "$OUT_DIR/eval/validity_gates_s${SEED}.json" || GATE_RC=$?
echo "[$(date)] gate checker exit=${GATE_RC:-0} (non-zero => ALGO: ...)"
```

and then the script ends, so the job exits **0** even when V1/V2/C3/identity fail.
An orchestrator that gates on SLURM job state alone would submit-and-forget a
sweep whose replica gate missed. *Minimal fix (builder, one line):* end
`01_train_eval.sh` with `exit ${GATE_RC:-0}` — the gate runs after every
`score_panel.py` call, so all per-arm results, diags and pair records are already
on disk and nothing is lost by a non-zero exit; `--requeue` does not requeue on
non-zero exit, only on preemption/node failure. *Orchestrator mitigation if the
build is submitted as-is (required):* after the sweep, read
`<OUTPUTS_ROOT>/s6_local/B2/eval/validity_gates_s0.json` and treat
`all_pass == false` with a non-empty `failures[]` as **ALGO → debugger** (a
non-empty `incomplete[]`/`missing_inputs[]` with empty `failures[]` is INFRA), or
simply re-run `scripts/02_verify_gates.py --eval_dir <out>/eval --diag_dir
<out>/eval --epochs 200 --seed 0` and treat exit 2 as a debugger trigger. Do not
read any C1/C2/C3 contrast before that check passes.

---

## Notes forwarded to the analyzer / debugger (not findings)

1. **If the CV does not select the head, `trust_head_circ` is bit-identical to
   `circ_repair` by construction** — `head_on` is false, so
   `pred = LF_te + fitted["alpha"] * C_te` with `alpha` from the same `fit_alpha`
   on the same `val_idx`, on the same corrector. Two identical numbers in the
   results table is then the *correct* "head not selected" outcome and the
   C3 mechanism leg's binary answer, not a duplicated-run bug.
2. `lsi_ctrl` is **not** zero-parameter on `ifc_poisson` (champion fallback) — the
   builder flagged this; the zero-parameter floor claim covers the four defect
   datasets only.
3. Arm order (`circ_repair` before `trust_head_circ`) is load-bearing for the C3
   pairing record. If a debugger reruns a single arm, `assert_pairing` records
   `unverified_partner_absent` rather than silently passing, and
   `02_verify_gates.py` still compares the two arms' `corrector_state_sha256`
   out-of-band from the diags.
4. Every arm's diag carries the padding decision, its reason, and the raw wrap
   ratios, so the pre-registered switch table is auditable per dataset from the
   sweep output alone. `sharp__sod_1d` is `degenerate_denominator → zeros`,
   recorded explicitly.
5. `01_train_eval.sh` mkdirs `<out>/training` but nothing writes there (per-arm
   checkpoints live under `<out>/eval/results/<arm>/s6_local_repair/ckpt_*`);
   `output_paths.training` will stay empty. Harmless.

---

## Independent verification actually performed (not taken on trust)

```
six pins vs `git show 3abc0e3:`        bands 42b869598fcc864e SAME  local_corrector dcf531f8207b93a3 (edited)
                                      model 80d8940d8b90a4ac SAME  smoke_eval/manifest/INSPIRATION (edited)
post-commit byte state                model.py + bands.py unchanged  ✓
state-dict bit-preservation            12/12 EQ (LocalCorrector, PixelGate) × {zeros, circular} × 3 shapes
trained-path proxy for V1              B1 family vs B2 b1_replica, sod_1d e2 s0:
                                       loss 5.2848e-02 == 5.2848e-02, alpha 1.500000 == 1.500000,
                                       test nRMSE 0.03227042226587238 == 0.03227042226587238  (alpha != 0)
V2 from committed sidecars             4/4 bit-exact vs B1 F6, n_params=0, helmholtz alpha=0.0
arm_env.sh × 5 arms                    35/35 knobs each, all values == card recipe (incl. per-arm deltas)
six negative knob tests                N1..N6 all raise S6ContractError; positive control does not raise
bash -n                                00_screen.sh 01_train_eval.sh arm_env.sh submit.sh submit_seeds_2_3.sh
                                       (+ scratchpad/run_smoke.sh) — all OK
py_compile                             02_verify_gates.py + all 6 family .py — OK
gate tables vs card + B1 turn 2        10/10 reference values exact
immutable surfaces                     git status clean on round1/{eval,tools,program.md,project.yaml},
                                       factory_mffp/{eval,baselines,references,scripts}, akash/
lineage                                1 commit; round1-substrate is ancestor
```

Checklist passes: **7/7 review questions answered; 2 SUGGEST findings, 0 FAIL.**
