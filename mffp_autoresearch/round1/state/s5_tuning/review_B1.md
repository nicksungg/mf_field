# code-reviewer — s5_tuning-B1 (attempt 1)

- **Verdict**: `SUGGEST` → card `status: reviewed_suggest`. **Submit as-is.**
- **Reviewed**: `git diff round1-substrate..ad29239` (16 files, +909/-0), all four
  scripts, the family dir, the five contract-smoke JSONs, the `contract_smoke/`
  artifacts under `${OUTPUTS_ROOT}/s5_tuning/B1/`.
- **UTC**: 2026-07-29T17:05Z

## Verdict paragraph

This build does exactly what card `s5_tuning-B1` part 3 asks and nothing more.
`models_r1/mf_fno_transfer_film_modes/model.py` is byte-identical to
`mf_field/factory_mffp/models/mf_fno_transfer_film/model.py` at substrate `967562e`
(md5 `ebfc56ce69282984b601a806ba735b10`, confirmed against `git show 967562e:` as well
as the working tree), and every `smoke_eval.py` delta traces to a numbered card item:
the `REPO_ROOT` relocation fix (item 2, line 63), the `MFFP_MODES_CAP` env read with
default 12 (item 3, lines 74–79), the `modes_cap`/`modes` audit fields plus
`preds_test.npz` (item 4, lines 305–326), mid-stage checkpoint/resume (item 5, lines
107–172 and 223–280), and the family rename (item 1, line 312 + `manifest.json`). There
is no third substantive edit: the only two implementation choices not literally
enumerated by the card — `CKPT_SAVES_PER_STAGE = 5` and the `_state_dict_compatible`
pre-load guard — are non-behavioural checkpoint mechanics, both disclosed in
`build_notes` / in-code comments, and both are *inside* item 5's mandate. The
equivalence proof is real and I re-read it from the artifacts rather than the prose:
`contract_smoke_BASE_factory.json` and `contract_smoke_default.json` agree to the last
digit on both datasets and in `panel_geomean_skill` (30.565677880367627), which is the
strongest possible form of the test because at `--epochs 2` the checkpoint cadence
`max(1, 2//5) = 1` fires a save every single epoch and still perturbs nothing; the
mid-stage resume JSON reproduces `22.613192981264614` and `logs/resume_direct.log`
carries the three expected `[resume]` lines; the knob-fired audit is confirmed in the
per-dataset JSONs (`n_params` 4,773,953 → 33,609,793 and 4,774,465 → 33,610,305,
Δ = 28,835,840 = 2·4·64²·(32²−12²), `modes [32,32]`, `modes_cap_source
env:MFFP_MODES_CAP`). Blast radius is clean (all 16 files under `models_r1/`,
`scripts/`, `notes/`, `scratchpad/`; no guarded factory surface has an mtime after the
build), the recipe is mirrored verbatim, and all four scripts pass `bash -n`. The
verdict is SUGGEST rather than PASS only because card item 6(c) — the guard-set
contract run — is openly unfinished and ships as an sbatch script the orchestrator must
fire, plus two script-hygiene notes below. None of the three blocks submission.

## Findings (7 review questions)

| # | Question | Verdict | Finding |
|---|---|---|---|
| 1 | Card–implementation alignment | **PASS** | All seven part-3 items trace to code or a script flag; both non-enumerated choices (`CKPT_SAVES_PER_STAGE=5` at `smoke_eval.py:80`, `_state_dict_compatible` at `:115`) are disclosed checkpoint mechanics inside item 5's mandate. No paraphrase drift. |
| 2 | Recipe fidelity | **PASS** | `base_family`/`base_commit` verified by md5 vs `git show 967562e:`; `family_dir`, `datasets: panel`, `epochs: 200`, `seeds: [0,1,2]` (parameterized), `env: {MFFP_MODES_CAP: "32"}` → `--env MFFP_MODES_CAP=32` verbatim at `01_train_eval.sh:52` and `02_guard_contract.sh:44`. The `SMOKE` dict is otherwise byte-identical to the base — no invented hyperparameter. |
| 3 | §5 immutable compliance | **PASS** | Diff touches no `round1/eval/`, `project.yaml`, `program.md`, ADR, or agent prompt; `find` over `factory_mffp/{eval,baselines,references,scripts}` + `akash/` shows no file modified after the build; no data regeneration; every card number comes from `score_panel.py` (the single direct `smoke_eval.py` call is a resume drill explicitly flagged as producing no card number); seeds {0,1,2}, epochs 200 = smoke tier. Not a re-proposal of the pre-falsified `mf_fno_spectral` LF low-mode *freezing* lever — this changes the truncation cap uniformly on a transfer family, and §12.5 pre-directs the card by name. |
| 4 | Contract compliance | **PASS** | `manifest.json` + `smoke_eval.py` 6-arg CLI (`:330–335`) + `INSPIRATION.md` citing all seven of the card's `prior_art` URLs. Resume from `<ckpt_dir>/last.pt` implemented **and drill-verified mid-stage**, with the config guard at `:234–236` refusing to load a cap-12 checkpoint into a cap-32 model. `--seed` reaches `torch.manual_seed`/`np.random.seed` at `:181`, inherited verbatim from the base (correct — changing it would break the equivalence proof). |
| 5 | SLURM correctness | **SUGGEST** | `bash -n` clean on all four (output quoted below). Partition `gpu`, typed `gres=gpu:p100:1` per `project.yaml sbatch:`; `--time 08:00:00`; `--output/--error` under `${OUTPUTS_ROOT}/s5_tuning/B1/slurm/%x_%j.{out,err}`; absolute paths; `01_train_eval.sh` takes `SEED="${1:?...}"`; `submit.sh` = seed 0 only; `submit_seeds_2_3.sh` present; `--exclude=hpc-93-36` has documented precedent (`state/gates.md`, the batch-0 array). Two non-blocking notes: **(S1)** the in-file `#SBATCH --job-name=r1-s5_tuning-B1` (`:12`) omits the seed and only `submit.sh:7` / `submit_seeds_2_3.sh:10` `--job-name` overrides make it conform to `r1-{stream}-B{N}-s{seed}` — a direct `sbatch 01_train_eval.sh 0` would produce a name the maintainer's matcher can miss. **(S2)** `--time 08:00:00` is 3.1× the ledger's 154.1 min cap-12 panel; if the spectral einsum is a larger share of the 44 min/dataset sharp runs than the builder's 1.3–2.5× estimate, the job TIMEOUTs — and `--requeue` does **not** cover TIMEOUT. Recovery is cheap (eval cache holds finished datasets, `last.pt` resumes the in-flight one), so the debugger should classify a TIMEOUT as INFRA-ish resubmit, not ALGO. |
| 6 | Smoke-test evidence | **SUGGEST** | `build_notes[1]` cites the exact contract-tier `score_panel.py` command and all five result JSONs exist in `<worktree>/scratchpad/`; I verified the claimed numbers inside them, not just in the prose. **(S3)** card item 6(c), the guard-set contract run, was not executed (1-CPU login node) and ships as `scripts/02_guard_contract.sh`. Openly disclosed in `build_notes[4]` and the handoff. Not a submit blocker (the card's expected result is a null, and §2.3 requires the guard set before a panel-*win* claim), but the orchestrator should fire it alongside seed 0 so the analyzer is not blocked later. |
| 7 | Blast radius | **PASS** | `git diff --name-status` = 16 added files, all under `models_r1/`, `scripts/`, `notes/`, `scratchpad/`. Zero substrate contamination. |

### `bash -n` (run by the reviewer, not taken from build_notes)

```
OK  01_train_eval.sh
OK  02_guard_contract.sh
OK  submit_seeds_2_3.sh
OK  submit.sh
```

## Non-blocking observations (no action required before submit)

1. **Stale path in the evidence JSONs.** `extra.preds_test_npz` in the
   `contract_smoke/results*` JSONs points at
   `.../mffp_autoresearch_outputs/round1/experiments/s5_tuning/B1/...`, a layout the
   builder relocated mid-session; that directory no longer exists. Build-time artifact
   only — the SLURM run records the correct `ROUND1_EVAL_RESULTS` path. Do not chase it.
2. **Equivalence was proven on CPU.** The login-node runs report `device: cpu`. The
   argument that bit-equivalence carries to the P100 is structural (the added code
   consumes no RNG draw and changes no tensor op), and the builder already handled the
   one GPU-specific resume hazard — `g.set_state(...)` needs a CPU `ByteTensor`, handled
   at `smoke_eval.py:153`. No action.
3. **Disk.** A cap-32 `last.pt` is ~806 MB; six panel datasets ⇒ ~4.8 GB/seed under
   `outputs/training`, with a transient `.tmp` double during the atomic save. 3.4 T free
   on `/resnick/groups`. Fine.
4. **Out of scope, for the record.** The main tree carries uncommitted edits to
   `round1/program.md` and `round1/project.yaml` (the ADR-0004 strict-single-seed
   amendment, mtime 09:04–09:05, operator-authored). Not attributable to this build —
   the build commit touches no main-tree file. Flagged only so the next §5.3 audit does
   not misread it.

## What the orchestrator should do

1. Submit seed 0 via `scripts/submit.sh` (ADR 0004: seed 0 only; `submit_seeds_2_3.sh`
   is correctly parked for end-of-round confirmation).
2. Fire `sbatch scripts/02_guard_contract.sh` alongside it (S3).
3. If the seed-0 job hits TIMEOUT rather than a crash, resubmit rather than counting an
   ALGO attempt (S2).
