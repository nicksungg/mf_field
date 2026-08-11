# Handoff from code-reviewer — 2026-08-11T05:46Z

**For**: orchestrator, experiment-builder
**Experiment**: r3s3_lf_value-B3
**Build commit reviewed**: `5db0aeb` (50 files, +37803/-0, diff base `round3-substrate`)
**Verdict**: **FAIL** — one launch-blocking SLURM defect, one line per file to fix.

## Verdict paragraph

This is the strongest build I have reviewed in this round on every axis that
carries scientific weight, and it fails on one line of shell.
I independently re-verified every claim the builder made rather than accepting
any of them: the seal's payload recomputes to `e98f6dc7…3e2c`, `_sealed_utc
2026-08-11T04:59:09Z` equals the file's mtime to the second and precedes every
training artifact in the tree (smoke JSONs 05:05–05:34Z; `outputs_root/.../B3`
does not exist yet), `model.py` is byte-identical to `eedcc655`, four more
family files are identical modulo the mechanical `R3S3B2_`→`R3S3B3_` rename,
`_common/ckpt_binding.py` is byte-identical to `da855da`, `tools/ckpt_data_binding.py`
is byte-identical to the live round-3 tool, the re-vendored
`_spectral_zeropad_up` + `SPECTRAL_RUNG_DATASETS` are byte-verbatim from
`round2/eval/panel_data.py:53,114`, and a programmatic key-by-key compare shows
all **49/49** `recipe.env` keys present with byte-equal values (45 in
`COMMON_ENV`, 4 per-leg) with the single, correct exception of the sha256 the
locked card could not carry.
The phase-P discipline is real, not decorative: `prereg.py::load` recomputes the
digest from the file it actually read, refuses any value starting with `<` (so
the card's own placeholder cannot be passed through), and
`assert_sealed_before` compares `_sealed_utc` against the leg's own start —
script-side enforcement **is** sufficient for integrity, and the card-side
placeholder is a self-containment gap for a human auditor, not an attack
surface.
The blocker is unrelated to any of that: **neither submit script creates
`$OUTPUTS_ROOT/r3s3_lf_value/B3/slurm/` before `sbatch`, and that directory does
not exist**, so SLURM cannot open `--output`/`--error` and every submitted job
dies at launch before `01_train_eval.sh:58`'s `mkdir` can run.
Sibling B2 carries exactly that `mkdir` in both submit scripts; B3 dropped it.
Fix the two lines and the re-review is a confirmation, not a re-audit.

## Findings

| # | Question | Verdict | Finding |
|---|---|---|---|
| 3.1 | Card–implementation alignment | PASS | All four carded changes trace to code. (1) ladder read from the seal — `prereg.py::ladder_for`, `01_train_eval.sh:211-217`, **no ladder literal in any script or family file**; (2) `R3S3B3_HARD_MASK_MODE=rederive_model_free` / `TOPFRAC=0.27`; (3) `state["data_binding"] = binding_block` at **every** save (`smoke_eval.py:1126`), role derived from the arm's own `cond_set` (`:1564`) not a drift-prone table; (4) film units. Arms reduced to exactly the three `recipe.env._note` binds (`ARMS`, `:286-289`) with a hard binding assert (`:527-534`); B2's `A2_lf_covered`/`A5_hf_budget_nolf` deliberately absent. Grid 66 = 60+5+1 under ADR r3-0007 option C; the deviation from `_grid`'s `<=71` is stated, not silent. |
| 3.2 | Recipe fidelity | PASS | Programmatic compare of `recipe.env` vs `COMMON_ENV`: 49 card keys, 45 common + 4 per-leg overrides, **zero** missing, **zero** extra, all values byte-equal. Only diff is `R3S3B3_PREREG_SHA256` (card placeholder vs the real digest) — see 3.5-adjacent note below. `epochs=200` = `recipe.epochs`; guard leg `epochs=2` = contract tier per `_note`. `seeds [0,1,2]`. No hyperparameter appears in code that is absent from recipe ∪ part 3 ∪ build_notes. |
| 3.3 | §5 immutable compliance | PASS | No writes to `round2/eval/`, `project.yaml`, `program.md`, agent prompts, or any guarded factory surface (`git status` on the main tree shows only the carded seal + two cards). Scoring exclusively via `round2/eval/score_panel.py` — no hand-rolled metric, no direct `smoke_eval.py` number. Seeds {0,1,2}. Test path condition-only on `${STRIPPED_DATA_ROOT}`; phase P also loads the stripped view (`phase_p_prereg.py:95`) so the prediction is over the rungs the arm actually trains on; **no reference to the original `${DATA_ROOT}` anywhere** in the family, scripts or tools. `--datasets panel` never used. No pre-falsified lever re-proposed (no teacher/distillation/pretrain-finetune/aux-loss arm). Registration-of-lifts restored byte-exactly — see 3.8-adjacent note on the pfc fix. |
| 3.4 | Contract compliance | PASS | `manifest.json` present and accurate; `smoke_eval.py` exposes the exact 6-arg CLI (`:1990-1995`). **Checkpoint resume from `<ckpt_dir>/last.pt` implemented** (`:1095-1127`) with key-match, `done` short-circuit, `executed_steps` for the stale-ckpt instruments — and empirically reproduced (`resumed_from_step 50`, nRMSE `0.06968199941910011` to the last digit). Seeding covers `random`/`numpy`/`torch`/`torch.cuda` from `--seed` (`:611-615`). `INSPIRATION.md` quotes the prior-art verdict with all five `prior_art` citations verbatim. |
| 3.5 | SLURM correctness | **FAIL** | **BLOCKING**: `scripts/submit.sh:21` and `scripts/submit_seeds_2_3.sh:19` call `sbatch` without creating `$OUTPUTS_ROOT/r3s3_lf_value/B3/slurm/`, and that directory does not exist (`ls` → No such file or directory; only `B1`, `B2` exist under `r3s3_lf_value/`). SLURM opens `--output`/`--error` (`01_train_eval.sh:35-36`) **before** the script body, so `01_train_eval.sh:58`'s `mkdir -p "$OUT_DIR/slurm"` is too late and all three jobs die at launch. Sibling B2 carries `mkdir -p "$OUT_DIR/slurm"` at `submit.sh:11` and `submit_seeds_2_3.sh:12` — this is a regression from the round's own convention. **Minimal fix**: add `mkdir -p "/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch_outputs/round3/r3s3_lf_value/B3/slurm"` immediately before the `sbatch` in each of the two submit scripts. Everything else clean: `bash -n` passes on `01_train_eval.sh`, `submit.sh`, `submit_seeds_2_3.sh` and `scratchpad/contract_smoke.sh` (all `OK`, run this session); `py_compile` passes on all family/tool/driver `.py`. `--partition=gpu` + `--gres=gpu:nvidia_h200:1` match `project.yaml` `sbatch` (typed gres); job name `r3-r3s3_lf_value-B3-s$SEED` (overridden per seed at both submission sites); `--output/--error` under `${OUTPUTS_ROOT}/{stream}/B{N}/slurm/`; all paths absolute; `SEED="${1:?...}"`; `submit.sh` = seed 0 only; `submit_seeds_2_3.sh` present (submits 1,2 — round-3 seeds, legacy filename documented in its header); `--time=06:00:00` with `--mail-user`/`--mail-type=END,FAIL` wired as required for a ≥1 h job. Minor (non-blocking): the `#SBATCH --job-name` default is hardcoded `-s0`, so a direct `sbatch 01_train_eval.sh 1` would mislabel; both submit scripts override it, and the header says so. |
| 3.6 | Smoke-test evidence | SUGGEST | `build_notes[6]` cites the contract-tier command and `scratchpad/contract_smoke.sh` re-extracts the **production** `COMMON_ENV` out of `scripts/01_train_eval.sh` with `sed`, so the smoke provably cannot drift from the job — excellent discipline. Four result JSONs exist in `scratchpad/`. **However**: all four green runs record `R3S3B3_DATA_BINDING_ASSERT=0` in their own `env` block, so **no exit-0 leg exists under the unmodified 49-key production env**. The blocker is genuinely cured (`floors.json._copylf_def_hash` now `9794cc89…` == `copylf_baselines.json`, verified this session) and the orchestrator re-ran `assert_data_binding` standalone, but the artifact that closes this is a ~2-minute login-node re-run of one contract smoke with `COMMON_ENV` untouched. Do it alongside the 3.5 fix. |
| 3.7 | Blast radius | PASS | 50 files, +37803/−0, six worktree-local top-level dirs only: `models_r3/`, `notes/`, `prereg/`, `scratchpad/`, `scripts/`, `tools/`. No substrate contamination, no commits outside the experiment branch. `tools/ckpt_data_binding.py` is byte-identical to the live `round3/tools/ckpt_data_binding.py` (vendored unedited at the worktree-root path `ckpt_binding.py`'s own resolver requires — the r3s4_audit-B2 convention); `prereg/prereg_knees_B3.json` is byte-identical (`cmp`) to the carded main-tree seal. Both new dirs are carded, not discretionary. |
| 3.8 | Novelty / round-3 seal integrity | PASS, 2 notes | Not a rebadge: condition→field throughout, LF never a forward input at test (`test_lf` read by neither arm, declared in the binding block `:1597-1599`). The family is the carded byte-for-byte vendoring of the round-3 sibling `r3s3_row_efficiency @ eedcc655` with four declared deltas — mandated by `recipe.base_family`, so it is carded, not drift. Seal ordering **verified independently**, not accepted: payload recomputes to the recorded digest; `_sealed_utc` == mtime; every artifact postdates it. **(a)** `_sealed_utc`, `_instrument.sha256` and `_driver.sha256` sit **outside** `payload`, so the digest the ordering assert pins does not cover the timestamp the ordering assert reads. Mitigated — not cured — by the committed byte-copy at `prereg/` in `5db0aeb` and by the main-tree mtime; worth folding `_sealed_utc` into the payload on the next card of this shape. **(b)** `build_notes[3]` and `phase_p_prereg.py:57-60` both state the round-half-to-even tie is "not exercised by any cell's ladder"; the docstring even supplies the condition ("`c_hat` is 2 (mod 8)") — and `c_hat = 10` on **both** `sharp__fisher_kpp_2d` and `ifc_heat` satisfies it. `r2 = max(2, round(10/4)) = 2` under half-even, `3` under half-up. Harmless to the science (the card's `_ladder_rule` writes bare `round()`, the seal records the mode at `ladder.rounding`, and the surrogate re-run and the trained ladder share the same rungs, so `c_pred` is unaffected) but **false on a predictive cell carrying the primary falsification clause** — correct the note so the analyzer is not misled. |

## Answers to the four questions posed with this review

1. **Is script-side seal enforcement sufficient given the locked `recipe.env` placeholder?**
   For integrity, **yes**.
   `PREREG_SHA256` at `01_train_eval.sh:52` is a constant *external to the seal*, committed at `5db0aeb`, recomputed from the file actually read on every leg, and `prereg.py::load` refuses any value starting with `<` — so a wholesale seal replacement (payload *and* `_payload_sha256` restamped together) is still caught, and the card's literal placeholder cannot be smuggled through.
   Both submit scripts additionally gate at the submission site.
   What is **not** covered is card self-containment: an auditor reading only the card cannot verify the seal.
   Recommend the orchestrator/starter transcribe `e98f6dc78ab18d80d75f4ef1f819525682d0d01c61e11081939dee30fcea3e2c` into `recipe.env` — a starter/orchestrator write, correctly refused by the builder as a locked field.

2. **Did the two fixes touch locked card semantics?** No, on both.
   The rename is contents-identical (`git show eedcc655:.../data_binding.py | sed 's/R3S3B2_/R3S3B3_/g' | diff - eval_seam_binding.py` → empty, re-run this session), and no card field names the file.
   The pfc lift change is *required by* the immutables rather than a deviation from them: registration-of-lifts (round-2 §12 / ADR r2-0004) obliges the model-side lift to **be** the eval layer's, the new code is byte-verbatim from `panel_data.py`, and `_blocking_preflights` item 3 explicitly demands the pfc rung assert against the ADR r3-0005 convention — the fix implements a carded requirement.
   The 42-line delta is disclosed in `INSPIRATION.md` and `build_notes`.

3. **Are the `_builder_resolved` items within discretion?** Yes, with one correction.
   `hist_draw_seeds = 0..63` feeds only the fold-population histogram, which part 3 item 3 lists under "Also emit" and `_reporting_discipline` treats as reported-not-gating; it appears in neither `_statistic`, `_adjudicability`, nor `expected_falsification`, so it changes no registered semantics.
   `FULL = max-over-rungs uncovered pool` **is** a registered quantity (it is `r4`), but the card defines `r4 = FULL` as "the A1_lf_all arm" — the whole uncovered pool — and the builder added a draw-invariance assert (395 sharp / 95 ifc), which is the right discipline for the one item that does touch the ladder.
   All three are recorded inside the seal, so they are pre-registered rather than post-hoc.
   The **rounding** item is the exception: the resolution itself is correct and sealed, but its stated rationale is factually wrong (finding 3.8b).

4. **SLURM vs recipe env, resume, and the `ckpt_binding` save-hook contract.**
   Env 49/49 exact; resume implemented **and** empirically reproduced; the batch-3 save-hook contract is met at every save with the role derived from the arm's own `cond_set` and a role-mismatch assert at `:1566`.
   The SLURM defect is the missing `mkdir` alone — see 3.5.

## Minimal path to `reviewed_pass`

1. Add `mkdir -p "$OUT_DIR/slurm"` (with `OUT_DIR` defined, as in B2) before the `sbatch` in `scripts/submit.sh` and `scripts/submit_seeds_2_3.sh`.
2. Re-run one contract smoke with `COMMON_ENV` untouched (no `R3S3B3_DATA_BINDING_ASSERT=0`) and commit the resulting JSON — closes 3.6.
3. Correct the "tie not exercised" sentence in `build_notes[3]` and `phase_p_prereg.py:57-60` (`c_hat = 10` on `fisher_kpp` and `ifc_heat` **is** 2 mod 8) — closes 3.8b.

Items 2 and 3 are SUGGEST-level; only item 1 blocks submission.

---

# Micro-review addendum — 2026-08-11T06:02Z

**Fix commit**: `8aa09f3` (3 files, +8/−4) — scope verified as exactly the three prescriptions.
**Verdict**: **FAIL → reviewed_suggest. Cleared for submission.**

| Item | Verdict | Verification |
|---|---|---|
| 1 — 3.5 `mkdir` (blocking) | **PASS** | Present in both scripts immediately before `sbatch` (`submit.sh:21`→`:22`, `submit_seeds_2_3.sh:19`→`:20`). Target verified programmatically byte-equal to `dirname` of **both** `--output` and `--error` (`01_train_eval.sh:35-36`). `bash -n` clean on all three. Cosmetic only: the `mkdir` sits inside the `for` loop (idempotent) and `jid=` lost its indent — no behavioural effect. |
| 2 — 3.6 carded-config smoke | **PASS, stronger than prescribed** | 49 env keys; key-by-key compare vs the production `COMMON_ENV` shows **all 45 common values byte-equal**. `DATA_BINDING_ASSERT=1` **and** `gate_report.data_binding_assert.performed=True` (the gate ran, not merely set). `copylf_def_hash 9794cc89…` post-restamp. `seal_precedes_leg True`, `lead_seconds 3138`. `roles_read` = the `lf_at_train` set. `nRMSE 0.0696819994191001` / `skill 0.94164864079865` byte-equal to the committed `assert=0` artifact at all 16 digits — turning the gate on changed the gate and nothing else. |
| 3 — 3.8b rounding note | **PASS** | Driver comment corrected (`:55-62`); card `build_notes[13]` appended, `build_notes[2]` left in place. Seal re-verified independently: `cmp` identical to the main-tree copy, payload recomputes to `e98f6dc7…`, `_sealed_utc` unchanged, `fk`/`ifc_heat` ladders still `[1,2,10,395]`/`[1,2,10,95]` — the sealed rungs already embodied half-even, as the correction claims. |

## Two new non-blocking observations

**(A) Driver sha provenance drift — introduced by fix 3.**
The seal records `_driver.sha256 = 62aba4e6…`; `scripts/phase_p_prereg.py` now hashes to `db893bc5…`.
Nothing enforces the field (`prereg.py::cell_record` only *copies* `_driver` into every result JSON), so no leg breaks.
I confirmed `git show 5db0aeb:scripts/phase_p_prereg.py | sha256sum` still equals `62aba4e6…` and that the edit is provably comment-only (AST comparison ignoring docstrings: identical), so re-running phase P reproduces the payload bit-for-bit.
**Analyzer action**: resolve the driver as `git show 5db0aeb:scripts/phase_p_prereg.py`, not by hashing the working tree.

**(B) Smoke evidence uncommitted.**
`scratchpad/contract_smoke_A3c_lf_uncov_cap__ifc_heat__c1__dnative.json` and its training record are modified-in-worktree, not in `8aa09f3`.
Until committed, the branch's committed smoke evidence is still the `assert=0` diagnostic. One `git add` + commit closes it.

## 3.8a — confirmed non-blocking

As the first-pass report implied. Design note for the next card of this shape, not a fix for this one: the seal is now doubly anchored — byte-identical across the main tree and the committed `prereg/` copy at `5db0aeb`, which predates every leg — so editing `_sealed_utc` without moving the payload digest is detectable via `git show 5db0aeb:prereg/prereg_knees_B3.json`.
Recommend folding `_sealed_utc`, `_instrument.sha256` and `_driver.sha256` **into** `payload` on the next pre-registered card; that would also have prevented (A).
