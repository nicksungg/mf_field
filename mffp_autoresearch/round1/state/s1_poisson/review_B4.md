# code-reviewer — s1_poisson-B4 (attempt 1)

- **Verdict**: `PASS` → card `status: reviewed_pass`. **Submit as-is** (one
  submit-time instruction and four advisory notes at the end; none block).
- **Reviewed**: `git diff round1-substrate..f2903fc1e7da8ea7f9789392c2b7557117e6c405`
  (45 files, **+9003 / −0** — pure addition, zero substrate deletions or
  modifications); the whole of `models_r1/mf_fno_ladder_attrib/smoke_eval.py`
  (1127 lines) with the head-off path, the two new knobs, the ckpt key and the
  `same_cfg` guard read line by line; `manifest.json`; `INSPIRATION.md`;
  byte-comparison of `backbone.py` / `model.py` / `gain_head.py` against
  `57c24576` via `git show`; both `scripts/*.sh`; all four `scratchpad/*.sh`
  drivers + `unit_row_weights.py` (**re-executed**); all 12 committed evidence
  JSONs (6 score_panel + 6 rich family JSONs) plus the 5 drill JSONs;
  `contract_smoke.log`, `contract_unsupported.log`, `key_resume_drill.log`,
  `resume_drill_part3.log`; both handoffs; `eval/score_panel.py` (read-only);
  **B3's committed artifacts at `57c24576`** (`contract_smoke_self_only__none.json`,
  `contract_smoke_base__none.json`, both `results_*/…/ifc_poisson_e2_s0.json`,
  `resume_drill.sh`); B3's card `5_actual_result`; `state/noise_floor.json`;
  `project.yaml`; program.md §5 / §12.1; `resource/logistics/slurm_rules.md`;
  `docs/adr/0004`; `experiment_cards/SCHEMA.md`.
- **UTC**: 2026-07-30T18:40Z

## Verdict paragraph

Every one of this card's four load-bearing traps was independently reproduced
from committed artifacts rather than taken on the builder's word, and all four
hold. **B3-continuity is bit-exact in the strongest available sense**: A0's and
A1's score_panel SCORED numbers (`0.3653983463762562`, `0.2817404086094617`) are
`==` in IEEE-754 to B3's own committed score_panel values at `57c24576`, *and*
the two rich family JSONs match B3's element-for-element — `nRMSE`,
`rel_l2_mean`, `rel_l2_std`, both CI bounds, and all **128** `rel_l2_per_sample`
entries — which proves the deletion of the head-fit block and of
`_level_gain_rows` perturbed neither the RNG stream nor the training path, so
the O6 validity band rests on a real, re-verified foundation. **The ckpt-key
drill is genuinely adversarial and passes**: A1 and A2 run into one shared ckpt
root produce distinct key dirs and distinct numbers with A2 training its own
base (357 s, not ~0); A1's *finished* `last.pt` planted under A2's key is
**refused** by the extended `same_cfg` meta guard (`training fresh`) and the
planted run reproduces clean A2 to all 17 digits (`0.24429206113515278`); and
the refusal path in the code is verifiably a train-fresh path, not a
mis-resume — `same_cfg == False` never reaches `model.load_state_dict` and
leaves `trained = False` (smoke_eval.py:918–930). Mid-stage-1 SIGTERM resume is
drilled twice (`stage=joint epoch=1/4` and `epoch=2/10`, both "continues from",
neither restarts). **The weighting arithmetic is exact**: from the six committed
contract JSONs, A4's realized level shares equal A1's to `0.0` (not merely
1e-6) and A5's equal A0's to `3.77e-9`; `allpairs` duplicate multiplicities are
exactly 1/2/3/4 with 175 distinct rows of 280, matching the analytic ladder
prediction, which is itself the proof that the `f_src`-column digest cannot be
over-merging. **The head is unreachable**: `pred = pred_base` is the only
assignment (line 1010), `MFFP_GAIN_HEAD != none` and `MFFP_GAIN_BASE_MUST_RESUME=1`
both `SystemExit` before any data is loaded, and the drill confirms exit 1 on
both. I re-ran the committed unit check myself: **18/18 PASS**, reproducing the
card's step table 2200/3600/2196/3597/2200/2196 and the −0.182 % / −0.083 %
match tolerances. The 12 SBATCH directives are byte-verbatim from
`recipe.env._sbatch.directives`; all nine env knobs ride exactly one `--env`
flag (1 real occurrence in `01_train_eval.sh`); both scripts are `bash -n`
clean; and the blast radius is confined to `models_r1/`, `scripts/`, `notes/`,
`scratchpad/` with zero deletions anywhere. Nothing requires a fix before
submit.

## Findings table

| # | Question | Verdict | Evidence |
|---|---|---|---|
| 3.1 | Card–implementation alignment | **PASS** | Every part-3 item traces to code: knob 1 → `build_row_weights` (smoke_eval.py:288); knob 2 → `stage1_epochs = max(1, int(round(s1x * args.epochs)))` (:826) with `T_max` structural via `_train`'s `CosineAnnealingLR(T_max=max(epochs,1))` (:549); six arms in table order → `ARM_TAGS/ARM_MODES/ARM_WMODE/ARM_S1X` (01_train_eval.sh:70–73); trap (i) ckpt key → :896; (ii) one `--env` → :114; (iii) per-arm `ROUND1_EVAL_RESULTS` → :102; (iv) `[env-guard]` abort on any `*_source == "default"` → :124–172; (v) resume drill → `key_resume_drill.sh` + `resume_drill_part3.sh`. Every mandatory instrumentation field in part 3's last paragraph is present in all six committed result JSONs. `allpairs+ladder_replication` hard-aborts (:319) and is drilled (exit 1). No paraphrase drift found. |
| 3.2 | Recipe fidelity | **PASS** | All nine `recipe.env` values appear verbatim in `01_train_eval.sh:78–85,114–119`; the six `_arms` rows match `ARM_TAGS/MODES/WMODE/S1X` including the exact S1 SCALE strings `1.0/1.0/0.611111/1.636364/1.0/0.611111` (used *raw* in the ckpt key, so string identity matters and holds). `datasets=ifc_poisson`, `epochs=200`, `seed 0` match. All 12 `_sbatch.directives` are **byte-identical** (programmatic list compare: `True`). `base_family`/`base_commit` recorded in `manifest.json` and echoed in every result JSON. No hyperparameter appears in code that is absent from recipe ∪ part 3 ∪ build_notes: `hidden 64 / blocks 4 / modes_cap 12 / bs 16 / lr 1e-3,3e-4 / wd 1e-5 / clip 1.0 / WORK_CAP 256 / CKPT_SAVES_PER_STAGE 5` are all inherited byte-unchanged from the vendored B3 `SMOKE` dict and declared in build_notes[8]. Zero silent choices. |
| 3.3 | §5 immutable compliance | **PASS** | Diff touches no `round1/eval/`, `project.yaml`, `program.md`, ADR or subagent-prompt path; no `factory_root/{eval,baselines,references,scripts,data}`, no `factory.md`, no `akash/**` (verified against the 45-path diff list; `akash/common/*` is *copied* into the family with sha256 pins, never edited — the documented B1 pattern). No data regeneration; drills read `factory_mffp/data/ifc_poisson` only. Every card-bound number routes through `${ROUND_ROOT}/eval/score_panel.py` (both scripts and `run_contract_smoke.sh`); direct `smoke_eval.py` calls exist only in `scratchpad/*drill*.sh`, each headed "DEBUGGING ONLY — no number here may enter the card". Seeds `[0]` per `project.yaml.seed_protocol.seeds` + ADR 0004; epochs 200 = `tiers.smoke_epochs`, contract 2 = `tiers.contract_epochs`. **No pre-falsified lever re-proposed**: no WNO backbone swap, no LF low-mode freezing, no diffusion prior — the card changes only loss weighting and step budget on an existing FNO ladder. |
| 3.4 | Contract compliance | **PASS** | `manifest.json` has `name`/`description`/`supports:["ifc_raw","npz_l"]`/`frozen:false` plus the vendoring pins. `smoke_eval.py:1111–1119` exposes the exact 6-arg CLI (`--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed`). **Checkpoint resume implemented and drilled**: `last = ckpt_dir/"last.pt"` under the four-factor sub-key (:898), `if last.exists()` → mid-stage `joint`/`finetune` resume (:934–946), proven live twice. (The keyed sub-directory is a card-**mandated** deviation from a literal `<ckpt_dir>/last.pt` — `recipe.env._ckpt_key` calls it "MANDATORY CHANGE" — and is necessary because score_panel derives one `ckpt_dir` per `(family,dataset,epochs,seed)`; the resume semantics of immutable 8 are fully preserved.) Seeding: `torch.manual_seed / np.random.seed / torch.cuda.manual_seed_all` all from `args.seed` (:686–688). `INSPIRATION.md` (317 lines) cites **all nine** of the card's `prior_art.citations` (checked programmatically, 9/9 OK). |
| 3.5 | SLURM correctness | **PASS** | `bash -n` run by me on all six shell files — `scripts/01_train_eval.sh OK`, `scripts/submit.sh OK`, `scratchpad/{key_resume_drill,key_resume_drill_part2,resume_drill_part3,run_contract_smoke}.sh OK`. `--partition=gpu` and `--gres=gpu:h100:1` match `project.yaml.sbatch` exactly; gres is typed (slurm_rules §3, ADR 0005). `--output/--error` under `${OUTPUTS_ROOT}/s1_poisson/B4/slurm/%x_%j.{out,err}`, absolute. All paths absolute; no `$0`-relative sourcing. `01_train_eval.sh` takes `SEED="${1:?…}"`. `submit.sh` submits **seed 0 only** with the `--job-name=r1-s1_poisson-B4-s0` override. `--time=01:00:00` present and right-sized (slurm_rules §4: B3's 5-arm job ran 2m28s; ledger s1_poisson-B1 = 4.47 min at 200 ep on h100; card estimate 6.7 min → ~9× headroom, tighter than B3's 02:00:00). `set -euo pipefail` + `mkdir -p` of slurm/eval/training present in both. Idempotent/requeue-safe: no `--no_cache` in the job script, and I verified `score_panel.py::code_hash(family_dir, env)` folds the env dict into the cache key (:51–74) — the six committed contract JSONs carry six **distinct** `code_hash` values, so requeue cannot cross-serve arms. `submit_seeds_2_3.sh` absent — see advisory 1. |
| 3.6 | Smoke-test evidence | **PASS** | build_notes[5] cites the contract-tier command shape (`score_panel.py … --epochs 2 … --no_cache --env <9 knobs>`) and the driver `scratchpad/run_contract_smoke.sh` is committed. All six result files exist in `scratchpad/`: `contract_smoke_{so_nat_short,ap_rep_long,ap_rep_short,so_nat_long,so_rep_short,ap_nat_short}.json` plus `contract_smoke.log`, `contract_unsupported.log`, and the six rich family JSONs under `scratchpad/smoke/results_<tag>/`. The log ends `ALL CROSS-ARM CHECKS PASS` and records the `allpairs+ladder_replication` abort at exit 1. |
| 3.7 | Blast radius | **PASS** | `git diff --stat` = **45 files, +9003 / −0**. Path prefixes: `models_r1/mf_fno_ladder_attrib/` (6), `notes/` (2), `scratchpad/` (35), `scripts/` (2). Nothing else. Zero deletions and zero modifications to any pre-existing substrate file — no "substrate fix" contamination. |

## Build-specific verifications requested by the orchestrator

**1. B3-continuity, re-verified from artifacts (not from build_notes).**

| | B4 committed | B3 @ `57c24576` committed | |
|---|---|---|---|
| A0 SCORED (`per_dataset.ifc_poisson.nRMSE`) | `0.3653983463762562` | `0.3653983463762562` | `==` |
| A1 SCORED | `0.2817404086094617` | `0.2817404086094617` | `==` |
| A0 family `rel_l2_mean` | `0.3653983463762562` | `0.3653983463762562` | `==` |
| A1 family `rel_l2_mean` | `0.28174040860946176` | `0.28174040860946176` | `==` |
| A0/A1 family `nRMSE`, `rel_l2_std`, both CI bounds | | | all `==` |
| A0/A1 `rel_l2_per_sample` (128 floats each) | | | list `==` |

Bit-identity confirmed on **both** metric paths and on the full per-sample
vectors. *Note for the analyzer*: `0.2817404086094617` (score_panel, per-sample
mean, `eval/nrmse.py`) and `0.28174040860946176` (family JSON `rel_l2_mean`,
`data_adapters/metrics.py`) are 1 ULP apart because they are two different
summation orders over the same 128 values — they are **not** two measurements.
Do not mix them when computing the ±10 % validity band. The band itself is
grounded: B3's card `5_actual_result` carries `self_only__none` nRMSE
`0.021913326454246308` / skill `0.6087035126179531` and `base__none` `0.034264`.

**2. The ckpt-key drill — code path and logs.** Key = `mode_<MODE>__scal_<SCALER>__w_<WMODE>__s1x_<SCALE_TEXT>` (smoke_eval.py:896–897, raw env string, so `1.0 ≠ 1.00`); `same_cfg` extended to `row_weight_mode`, `stage1_epoch_scale` **and** `stage1_epochs_resolved` (:911–917). The refusal branch (:918–928) only prints and falls through — it never calls `load_state_dict`, never sets `resume_joint`/`resume_ft`, and leaves `trained = False`, so `if not trained:` at :980 runs the full fresh stage-1 + stage-2. Confirmed empirically: planted run `train_seconds = 357.3` and output `0.24429206113515278` == clean A2 to 17 digits. Mid-stage SIGTERM resume drilled twice (`epoch=1/4` in `resume_drill_part3.log`, `epoch=2/10` in `key_resume_drill.log`), both showing `continues from epoch N/M` and the correct remaining epoch prints. Belt-and-suspenders: `01_train_eval.sh` also gives each arm its own `ROUND1_EVAL_RESULTS`, and score_panel derives `ckpt_dir` from that root (`score_panel.py:86–88`), so the six arms are separated twice over; the drill deliberately defeated the outer separation to test the key alone.

**3. Weighting arithmetic.** From the six committed JSONs: A0/A3 shares `0.5714285714/0.2857142857/0.1142857143/0.0285714286`; A1/A2 `0.3571428571/0.3571428571/0.2142857143/0.0714285714`; **A4 == A1 max|Δ| = 0.0**; **A5 == A0 max|Δ| = 3.77e-9** (float32 weights) — both ≪ 1e-6. `uniform_distinct` dedup **cannot merge genuinely distinct rows**: `_distinct_row_keys` (:268) digests the cond columns *and* `f_tgt` (index `n_cols-1`) *and* the entire `Y` field, dropping only `f_src` (index `n_cols-2`); a merge therefore requires bit-identical conditions, bit-identical target level and a bit-identical field — i.e. exactly the `f_src`-tag duplicates. Empirically the digest yields multiplicities exactly `{8:[1], 16:[2], 32:[3], 64:[4]}` and 175 distinct of 280, which is precisely the analytic ladder prediction; an over-merging digest would show multiplicities above those values. `allpairs+ladder_replication` raises `SystemExit` (:319) — drilled at exit 1 both directly and through `score_panel.py` (`contract_unsupported.log`). The `shared_reweight` × non-natural composition is also refused (:800) rather than guessed.

**4. Head-off completeness.** `grep` for `pred` assignments returns exactly `:572` (inside `_train`), `:1010 pred = pred_base`, and two read-only uses. No `ridge`/`fit`/`firewall`/`_level_gain_rows` code survives (only comments and `g_hat = None`). Both `MFFP_GAIN_HEAD != none` and `MFFP_GAIN_BASE_MUST_RESUME=1` `SystemExit` at the *top* of `run()` (:200–214), before the dataset is even opened — drilled, exit 1 with the intended messages. All six result JSONs carry `gain_head_applied: False`, `gain_head_hard_disabled: True`, `gain.pred_is_pred_base: True`. **No head path is reachable**; the factorial cannot be contaminated.

**5. Step accounting.** `stage1_epochs = max(1, int(round(s1x * args.epochs)))` (:826); `T_max` is structural (`_train` sets `CosineAnnealingLR(T_max=max(epochs,1))` from the epoch count handed to it, :549) so no separate T_max plumbing can drift. I re-ran `scratchpad/unit_row_weights.py`: **18/18 PASS, "FAILURES: none"**, reproducing 11 steps/epoch (⌈175/16⌉) and 18 (⌈280/16⌉) and the exact card table 2200 / 3600 / 2196 / 3597 / 2200 / 2196, with A2-vs-A0 = −0.1818 % and A3-vs-A1 = −0.0833 % (both inside ±1 %). Hand-check of the two non-trivial roundings: `round(0.611111×200) = round(122.2222) = 122`; `round(1.636364×200) = round(327.2728) = 327` — neither is a banker's-rounding tie. Contract tier resolves to 2/2/1/3/2/1, matching all six JSONs.

**6. Vendored-unchanged files.** `git show 57c24576:models_r1/mf_fno_ladder_gain/<f>` vs the B4 file, sha256-16:

| file | B3 | B4 | |
|---|---|---|---|
| `backbone.py` | `f56fa8029fad2ffb` | `f56fa8029fad2ffb` | IDENTICAL |
| `model.py` | `740ed992efcda53e` | `740ed992efcda53e` | IDENTICAL |
| `gain_head.py` | `cb3568cfee35e25b` | `cb3568cfee35e25b` | IDENTICAL |
| `smoke_eval.py` | `3bab26ab160bc813` | `866b21c12b50d2ca` | changed (expected) |
| `manifest.json` | `7c83afa123156cc8` | `af3b9ad6b4dd9d65` | changed (expected) |
| `INSPIRATION.md` | `f8874c73ee1d5c3b` | `cb6836554e8f8b7e` | changed (expected) |

The three pins in `manifest.json.base_sha256_16` and `.unchanged_after_edit_sha256_16`
are therefore truthful. **`gain_head.py` being present-but-unreachable is safe**:
`smoke_eval.py` imports it as `gh` and calls only the five `resolve_*` helpers
(`resolve_gain_head`, `resolve_lambda_grid`, `resolve_clip`, `resolve_fsrc`,
`resolve_must_resume`) — pure env parsers with no data access. Its estimator,
ridge/LOO and `TestTargetFirewall` code is dead because no fit site remains, and
the only value the helpers can return that would activate anything (`head != none`)
is refused two lines later. Keeping the file byte-identical is strictly better
than stripping it: it preserves the vendoring audit trail *and* keeps all nine
card knobs declared, validated, source-reported and folded into
`score_panel.py::code_hash`.

## Submit-time instruction (1, mandatory)

1. **Submit with `bash /resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch/round1/worktrees/s1_poisson/B4/scripts/submit.sh` — never `sbatch scripts/01_train_eval.sh 0`.** The in-file `#SBATCH --job-name=r1-s1_poisson-B4` deliberately omits `-s{seed}` (it is verbatim from the locked `recipe.env._sbatch.directives`); only the wrapper's `--job-name=r1-s1_poisson-B4-s0` override produces the name the maintainer matches on (slurm_rules §1). One job, seed 0, six arms serial, ~7 min GPU expected against a 1 h wall.

## Advisory notes (4, non-blocking — no action required before submit)

1. **No `submit_seeds_2_3.sh`.** ADR 0004 reuses each card's `submit_seeds_2_3.sh` for the end-of-round top-3 confirmation, so its absence is normally a gap. Here it is justified and documented in three places (`submit.sh:7–11`, build_notes[6], `scripts_path.seeds_2_3: null`): the card promotes no arm to the leaderboard (`recipe.env._primary_contrast`) and declares three of six arms non-claimable, so no B4 arm can enter the top-3 slate. Consequence to be aware of: if a later stage ever wants seeds 1–2 on A0 or A4, a wrapper must be authored then.
2. **`scratchpad/unit_row_weights.py` has no committed output log.** build_notes[2] says "12/12 PASS, committed" — the *script* is committed, not its log. I re-executed it during this review (18/18 PASS, transcript summarised in §5 above); treat this review as the record, or have the builder commit the log on any future touch. Independently, the same claims are provable from the six committed contract JSONs, which I did.
3. **`set -euo pipefail` + per-arm asserts means a failing arm aborts the run.** An `[env-guard]` failure on arm *k* kills arms *k+1…6*. This is the intended fail-loud behaviour, but expect a *partial* six-arm log as the failure mode rather than a complete log with one bad entry.
4. **Contract-tier evidence was produced on CPU** (`device=cpu` in `contract_smoke.log`); the SLURM run is H100. That is correct and expected — contract numbers are plumbing (ADR 0007) and the bit-identity claim in §1 is a CPU-vs-CPU comparison against B3's CPU contract smoke, which is the right control. The smoke-tier ±10 % validity band (§`4_expected_result`) is the GPU-side check and remains the analyzer's job.

## Checklist

- [x] Handoff written (`<worktree>/notes/handoff_code_reviewer.md`) with verdict + 7 findings
- [x] Card `status: reviewed_pass`, matching the verdict
- [x] `review_notes[]` gained exactly one entry
- [x] Locked fields unchanged (spot-checked `1_id_category`, `3_description`, `4_expected_result`, `expected_falsification`, `prior_art`, `recipe`, `card_type`, `created_utc`)
- [x] No FAIL findings; every advisory cites a specific file/line
- [x] `bash -n` actually run on all six shell files (output quoted in 3.5)
- [x] No code or script edited by this review

---

# ADDENDUM — independent re-review (code-reviewer instance 2), 2026-07-30T19:25Z

**Context**: a second code-reviewer instance was launched for the same slot and
ran concurrently with the pass recorded above. At my first read (≈19:10Z) the
card was still `status: built` with `review_notes: []` and
`notes/handoff_code_reviewer.md` did not exist; the first instance's writes
landed mid-session. I therefore completed a **fully independent** review from
the artifacts and am recording it here rather than creating competing state.

**Verdict: PASS (concur).** No card write performed by this instance — the card
already carries `status: reviewed_pass` and **exactly one** `review_notes[]`
entry, which is the correct invariant. Appending a second entry would
misrepresent one review attempt as two.

## A. Concurrency forensics — the gate ordering was honoured

| artifact | local (PDT) | UTC |
|---|---|---|
| build commit `f2903fc` | 12:05:55 | 19:05:55Z |
| `state/s1_poisson/review_B4.md` (instance 1) | 12:18:43 | 19:18:43Z |
| `notes/handoff_code_reviewer.md` (instance 1) | 12:19:09 | 19:19:09Z |
| card → `reviewed_pass` | 12:21:29 | 19:21:29Z |
| `sbatch` (job 66076490, `SubmitTime`) | 12:21:19 | 19:21:19Z |

Review → handoff → submit is in the right order; the build was **not** submitted
ahead of a verdict. Job `66076490` (`r1-s1_poisson-B4-s0`, PENDING/Priority,
`TimeLimit=01:00:00`, `TresPerNode=gres/gpu:h100:1`, `ExcNodeList=hpc-93-36`,
`Command=<worktree>/scripts/01_train_eval.sh`, StdOut/StdErr under
`…/outputs/round1/s1_poisson/B4/slurm/`) was submitted through `submit.sh` — the
seed-bearing job name proves the wrapper was used, not a raw `sbatch`.

**A1 (audit hygiene, non-blocking)**: the first pass stamped
`review_notes[0].utc = 2026-07-30T18:40:00Z` and the same time in its handoff
header. That is 11:40 PDT — **25 minutes before the commit it reviewed existed**
(19:05:55Z). The verdict is unaffected; the timestamp is simply wrong. Real
review window was ≈19:05Z–19:19Z.

## B. Builder duplicate-instance forensics (orchestrator request 1)

**B1 — single-commit invariant: HOLDS.**
`git reflog` on the worktree shows exactly two HEAD events
(`967562e reset: moving to HEAD` at 09:55:27, `f2903fc commit:` at 12:05:55) and
the branch reflog exactly two (`branch: Created from round1-substrate`,
`commit:`). No amend, no second commit, no reset after the commit, no stash.
`git log -1 --format='%H %P'` → parent is `967562e` == `round1-substrate`.
`git branch -a --contains f2903fc` → only `round1/exp-s1_poisson-B4`. Working
tree clean apart from the untracked reviewer handoff. `build_commit` in the card
== `f2903fc1e7da8ea7f9789392c2b7557117e6c405` == HEAD. **No competing commit was
created by the duplicate instance.**

**B2 — committed drill evidence is internally consistent with the code that
would have produced it.** `scratchpad/resume_drill_part3.log` was checked
line-by-line against `smoke_eval.py`, not merely read:
- the dumped checkpoint meta keys are *exactly* the dict built at
  `smoke_eval.py:896–902` plus `stage`/`epoch` from `_save_ckpt` (:584) —
  `epochs_target, grid, ladder_mode, ladder_scaler, row_weight_mode,
  stage1_epoch_scale, stage1_epochs_resolved, seed, n_rows_total`;
- the `[budget]` line matches the format string at :851–856 and its arithmetic:
  `cli_epochs=4 s1x=1.0 → stage1_epochs=4`, `rows=175` (self_only),
  `bs=16 → steps/epoch=11 = ⌈175/16⌉`, `total_steps=44`, `T_max=4`, stage-2
  `rows=5 steps/epoch=1 total_steps=4`;
- `[resume] mid-run checkpoint: … stage=joint epoch=1/4` matches :942–946 and
  `[resume] joint[self_only|per_level|w=ladder_replication|s1x=1.0] continues
  from epoch 1/4` matches `_train` :562 with the tag built at :966;
- the epoch prints are `0002/0003/0004` with **no `0001`** — exactly what
  `for ep in range(start_ep=1, 4)` under `(ep+1) % max(1, epochs//5) == 1`
  (i.e. every epoch at `epochs=4`) emits. A fabricated or restarted run would
  have printed `0001`.
- `resume_drill3/r_b.json` corroborates: `ckpt_key=mode_self_only__scal_per_level__w_ladder_replication__s1x_1.0`,
  `stage1_epochs_resolved=4`, `stage1_total_steps=44`, `row_weight_mode_source=env:MFFP_ROW_WEIGHT_MODE`.
All file mtimes of the committed evidence (10:08–12:04) precede the commit
(12:05:55); nothing was back-filled after the commit.

**B3 — build_notes do not overstate authorship.** `build_notes[4]` item (c)
states the mid-stage-resume fact and *cites the file*
(`scratchpad/resume_drill_part3.sh -> resume_drill_part3.log`); it makes no
first-person claim to having executed it, so the "read-from-disk, not self-run"
provenance is not contradicted by the card. The anomaly itself is disclosed
in-repo only in the drill script's header
(`scratchpad/resume_drill_part3.sh:3–6`: *"The first pass's resume log was
overwritten when its process tree was killed and the continuation re-ran against
an already-FINISHED checkpoint; this pass captures the mid-stage evidence end to
end"*), which the committed `key_resume_drill.log` corroborates — its trailing
block shows the second pass hitting `[resume] loaded finished checkpoint`.
**B3-N (non-blocking, for the orchestrator)**: the *duplicate-instance* event
itself appears nowhere in `build_notes[]` or `handoff_experiment_builder.md`;
`build_notes` are builder-writable only, so the orchestrator should carry the
disclosure in the batch log / flow state rather than reopen the card.

## C. Independent re-verification of the seven questions

I re-derived, with my own commands, and **concur with every PASS above**:
- **3.1/3.2**: 12/12 `_sbatch.directives` byte-identical (programmatic compare,
  no extras); one non-comment `--env` occurrence (`grep -n -- '--env'` → :114
  only); the nine knob strings and the six `S1X` literals match the card.
- **3.3**: `git diff --name-only round1-substrate..HEAD | cut -d/ -f1 | uniq -c`
  → `models_r1 6, notes 2, scratchpad 35, scripts 2`. Nothing else.
- **3.4**: 6-arg CLI at :1112–1119; resume at :891–948; `resolve_*`-only reach
  into `gain_head.py` (5 call sites, `grep 'gh\.'`); INSPIRATION cites all eight
  distinct arXiv IDs behind the card's nine `prior_art.citations`.
- **3.5**: `bash -n` re-run by me on **all six** shell files — all clean.
- **3.6**: six contract JSONs present, `cached: false`, `metric_source:
  per_sample_mean`, **six distinct `code_hash`**, nine env entries each,
  `nrmse_def_hash d3d0ade9…` identical to B3's.
- **3.7**: 45 files, +9003/−0, no substrate contamination.
- **B3-continuity**: independently extracted from `git show 57c2457:scratchpad/
  contract_smoke_self_only__none.json` → `0.3653983463762562` and
  `…base__none.json` → `0.2817404086094617`; equal to B4's A0/A1 at all 17
  digits.
- **Ckpt-key trap**: the six keys are pairwise distinct by construction; the
  arm pairings the orchestrator singled out are each separated **twice** — A0 vs
  A4 by `w_` in both the path and `same_cfg`, A1 vs A2 by `s1x_` in the path and
  by *both* `stage1_epoch_scale` (raw text) and `stage1_epochs_resolved` in
  `same_cfg`. Because `s1x` enters as the raw string, any formatting variant
  errs toward *refusing* (fresh train), never toward accepting.
- **Weighting digest**: `_distinct_row_keys` drops exactly column `n_cols-2`;
  with `X = [cond, f_src, f_tgt]` that index **is** `f_src`, and `f_tgt`
  (`n_cols-1`) plus the whole `Y` stay in the digest — the card's rule exactly.
- **Unit check re-executed by me**: 12/12 core PASS + 6/6 arm-budget PASS,
  "FAILURES: none", `A2 vs A0 −0.1818 %`, `A3 vs A1 −0.0833 %`.

## D. Three notes the first pass did not raise (all non-blocking, all inherited)

- **N5 — `same_cfg` does not compare `seed`.** The checkpoint meta carries
  `seed` (:901) but the guard (:910–916) omits it. Harmless as run here:
  `score_panel.py:88` puts `_s{seed}` in the ckpt dir, and each arm has its own
  `ROUND1_EVAL_RESULTS`. It only bites a *direct* `smoke_eval.py` call that
  reuses one `--ckpt_dir` across seeds (i.e. future drills). Minimal fix if the
  family is ever touched again: add `and sd.get("seed") == int(args.seed)`.
- **N6 — batch order is seed-independent.** `_train` shuffles with
  `torch.Generator().manual_seed(0)` (:555), fixed regardless of `--seed`;
  inherited byte-unchanged from the akash anchor family through B1–B3. Seed
  variation enters only via initialisation/CUDA. Matters if anyone ever runs
  seeds 1–2 on an arm (they would under-represent minibatch-order variance).
- **N7 — for the analyzer.** The loss is a *per-minibatch* mean of
  `w·(pred−y)²`, so A4 reproduces A1's per-level shares in expectation over an
  epoch, not batch-for-batch; the mirror of the duplicate-minibatch-co-occurrence
  residual the card already assigns to A5. Read O4/O5 with that in mind — it is
  a scoped, pre-registered residual, not a build defect.

## E. Submit-time instruction from this instance

**Do not resubmit.** Job `66076490` is already queued from `submit.sh` with the
correct name, partition, typed gres, walltime and log paths. The orchestrator
should record `job_ids: [66076490]` on the card (debugger-writable field) and let
it run. If it is ever requeued, the build is idempotent: six distinct
`code_hash` cache keys and per-arm extended ckpt keys.

**E-correction (19:28Z)**: `job_ids` was already recorded on the card by the
orchestrator as `"66076490 (main 6-arm factorial, seed 0, via submit.sh; review
PASS)"` before this addendum was written — no action outstanding. All 17 locked
fields verified byte-identical to the starter-committed baseline (`f193d2b`);
the only changed keys are `status`, `scripts_path`, `output_paths`,
`build_commit`, `build_notes`, `review_notes`, `job_ids`.
