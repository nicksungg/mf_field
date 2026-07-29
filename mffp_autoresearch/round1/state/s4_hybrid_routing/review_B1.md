# Handoff from code-reviewer — 2026-07-29T17:55Z

**For**: orchestrator, experiment-debugger, experiment-initial-analyzer
**Experiment**: s4_hybrid_routing-B1 (card_type: model)
**Diff reviewed**: `round1-substrate..4691d1fbaaa4dc9e0e6fbaf3bf607afef203404c`
**Attempt**: 1

## VERDICT: SUGGEST — submit as built

The critical constraint holds under byte-level verification: `model.py` and
`manifest.json` are byte-identical to `mf_field/akash/models/fno_transolver_seq`
@`967562e` (`diff -q` rc=0 on both), and `smoke_eval.py` carries exactly the two
mechanical edits card part 3 item 2 permits — the `_find_akash()` upward search
replacing `AKASH = Path(__file__).resolve().parents[2]`, and the `--ctx_source`
default `os.environ.get("MFFP_CTX_SOURCE", "auto")` — plus the single `import os`
line that edit (b) mechanically entails. No third substantive edit exists; the
argument that the two edits are behaviour-neutral is not merely asserted but
*demonstrated*, because the relocated family reproduces the brainstormer's
pre-relocation `ifc_poisson` numbers to every printed digit (0.438569 /
0.490003 / alpha 1.5001). `INSPIRATION.md` is a new documentation-only file, not
an edit to the copied artifact: program.md §5 and the model-card contract
*require* it (its absence would itself be a FAIL under review question 3.4), and
`eval/score_panel.py::code_hash` (line 62) hashes `Path(family_dir).rglob("*.py")`
only, so a `.md` file provably cannot move a number — it is required and
number-neutral, therefore not a rule-of-two violation. §5 immutables are clean
(no diff under `mf_field/akash/`, `round1/eval/`, `project.yaml`, `program.md`,
ADRs or prompts; scoring exclusively through `score_panel.py`; no pre-falsified
lever), blast radius is 17 files entirely inside `models_r1/ scripts/ notes/
scratchpad/`, all five scripts pass `bash -n`, and the card's three core readouts
are present in the family result JSONs I opened myself. The verdict is SUGGEST
rather than PASS only because of execution-side traps the next stages must know
about — chiefly that the six per-dataset result files each carry a
`panel_geomean_skill` key computed over ONE dataset, and that the per-dataset
walltimes live only in `submit.sh`.

## Findings

| Q | Verdict | Finding |
|---|---|---|
| 3.1 card-implementation alignment | PASS | All six part-3 items trace to code/scripts (see below). Three documented deviations, all defensible. |
| 3.2 recipe fidelity | PASS | Every `recipe` value appears exactly; no silent hyperparameter anywhere. |
| 3.3 §5 immutable compliance | PASS | No guarded-surface writes; scoring via `score_panel.py` only; no pre-falsified lever. |
| 3.4 contract compliance | PASS | Two-edit rule satisfied byte-for-byte; 6-arg CLI; `last.pt` resume implemented AND empirically verified; INSPIRATION.md present. |
| 3.5 SLURM correctness | SUGGEST | `bash -n` OK ×5; headers conform; five non-blocking notes (S1–S5). |
| 3.6 smoke-test evidence | PASS | Two contract-tier `score_panel.py` runs + a resume rerun; result files present in `scratchpad/`; readouts verified in the family JSONs. |
| 3.7 blast radius | PASS | 17 files, `models_r1/`(4) `notes/`(2) `scratchpad/`(6) `scripts/`(5). Zero substrate files. |

### 3.1 Card-implementation alignment — PASS

- item 1 (verbatim copy) ✓ — `diff -q` vs `git show 967562e:...` rc=0 for
  `model.py` and `manifest.json`.
- item 2 (exactly two edits) ✓ — see 3.4.
- item 3 (run only through `score_panel.py`, do NOT set `ROUND1_EVAL_RESULTS`) ✓
  — no script sets it. **I independently verified the card's premise**:
  `grep -n "export|ROUND1_" eval/run_batch0.sbatch` returns nothing, so batch 0
  indeed did not redirect. `eval/results/` and `eval/cache/` are gitignored
  (`round1/.gitignore:3-4`) and `score_panel.py:35-36` defaults there. The
  training artifacts landing in `round1/eval/results/fno_transolver_seq/` is
  therefore **correct card compliance, not sloppiness**, and is not a violation
  of immutable 3 (which forbids *editing* the eval layer, not writing its own
  gitignored output dir).
- item 4 (one task per (dataset, seed)) ✓ with deviations D1/D2 below.
- item 5 (guard at contract tier, seed 0) ✓ — `02_guard_contract.sh`
  `--datasets guard --epochs 2 --seed 0 --env MFFP_CTX_SOURCE=auto`.
- item 6 (no new measurement code) ✓ — nothing added; readouts confirmed present.

Deviations, all documented in `build_notes` and all judged sound:
- **D1** — separate `sbatch` jobs instead of a job array. Equivalent granularity
  and per-dataset walltimes; array would force one walltime. Fine.
- **D2** — per-dataset jobs pass `--datasets <one dataset>` rather than the
  card's literal `--datasets panel`; `03_aggregate_panel.sh` then runs the
  literal canonical command as a cache-only recombination. I verified this is
  numerically identical: `score_family` (score_panel.py:169-200) keys the cache
  per dataset as `sha256(chash|ds|epochs|seed)` and computes each dataset's skill
  independently, taking the geomean only at the end — there is no cross-dataset
  normalization, so splitting the panel cannot change any number.
- **D3** — walltimes 04:00:00/02:00:00 vs the card's 08:00:00/03:00:00. See S3.

### 3.2 Recipe fidelity — PASS

`base_family` `fno_transolver_seq` ✓ (`manifest.json::name`); `base_commit`
`967562e…` ✓ (diff-verified); `family_dir` `models_r1/fno_transolver_seq` ✓;
`datasets: panel` ✓ (the six-element `DATASETS` array in `submit.sh:31-32` is
`project.yaml::panel` verbatim, same members, same order); `epochs: 200` ✓
(`01_train_eval.sh:56`); `seeds [0,1,2]` ✓ parameterized, executed seed-0-only
per ADR 0004; `env {MFFP_CTX_SOURCE: auto}` ✓ verbatim as
`--env MFFP_CTX_SOURCE=auto` in all three run scripts. The knob is recipe-recorded
per immutable 5 and does enter the cache key (`code_hash` folds sorted env pairs,
score_panel.py:68-70). **No hyperparameter appears in any script that is absent
from `recipe` ∪ part 3**: the only flags passed are `--family_dir --datasets
--epochs --seed --out --env`.

### 3.3 §5 immutable compliance — PASS

1. Data read-only ✓ — no diff under `benchmark_42/` or `factory_root/data/`; no
   generation code.
2. Panel/guard fixed ✓ — both taken from `project.yaml` expansion / the verbatim
   panel list.
3. Eval layer byte-untouched ✓ — `git diff round1-substrate..HEAD` touches no
   path under `round1/eval/`, `project.yaml`, `program.md`, `docs/adr/`, or
   `subagents/`.
4. One nRMSE definition ✓ — all three evidence JSONs carry
   `nrmse_def_hash d3d0ade9…`; nothing recomputes a metric by hand.
5. Contract CLI fixed + env knobs recorded ✓ — see 3.2/3.4.
6. Seeds/epoch budgets ✓ — 200 (smoke) and 2 (contract) match
   `project.yaml::tiers`.
7. Guarded factory surfaces ✓ — `git diff 967562e..HEAD -- mf_field/akash/` is
   **empty**. This matters here because `_find_akash()` makes the family import
   `common/backbone.py` and `common/mffp.py` from the worktree's own akash
   checkout; those are read, never written, and are at the base-commit state.
8. Checkpoint-resume ✓ — see 3.4.

Pre-falsified levers: none re-proposed. This is FNO-FiLM + Transolver, unrelated
to the WNO backbone swap, LF low-mode freezing, or the diffusion prior.

### 3.4 Contract compliance — PASS (the critical constraint)

- **The two-edit rule.** `diff -u` of the vendored `smoke_eval.py` against
  `git show 967562e:mf_field/akash/models/fno_transolver_seq/smoke_eval.py` is
  29 insertions / 2 deletions in three hunks: `+import os` (line 49), the
  `_find_akash()` helper replacing the `AKASH = …parents[2]` line, and the
  `--ctx_source` default. Hunk 1 is the import that hunk 3 requires; the two
  *substantive* edits are exactly (a) and (b). **No third edit.** Both are
  behaviour-preserving at the recipe value, and this is demonstrated, not
  assumed — see 3.6.
- **INSPIRATION.md**: judged NOT a violation. It adds no `.py`, program.md §5
  and this reviewer's own 3.4 checklist require it for a model card, and
  `code_hash` at score_panel.py:62 globs `*.py` only. It cites both card
  `prior_art` URLs (2602.11197, 2311.12902) with the websearcher's
  `preempted-but-MF-composition-open` verdict and the "claims no novelty"
  framing, plus the four `manifest.json::inspired_by` sources.
- 6-arg CLI ✓ — `--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed`
  at smoke_eval.py:574-579 (`--ctx_source` is an extra optional arg that
  `score_panel.py` never passes; the env default is the only route).
- `manifest.json` ✓ — `name`, `description`, `supports: [ifc_raw, npz_l]`,
  `frozen: false`, `smoke_entrypoint`.
- **Resume from `<ckpt_dir>/last.pt`** ✓ implemented at smoke_eval.py:321-337
  (load, guarded by an `(epochs_target, grid, recipe_hash)` key match), written
  at :448-454. I spot-checked the mechanism as asked: the checkpoint stores the
  full post-training state (`hybrid`, `fno_stage2`, `alpha`, `alpha_ls`,
  `scaler_r/ctx`, `stage3_kept`, `fold_ids`, `val_idx`), so the eval path is
  exactly reproducible from it — which is why the rerun is bit-identical rather
  than merely close. Empirically confirmed: `eval/results/fno_transolver_seq/
  ifc_poisson_e2_s0.json` now reads `train_seconds 0.852` (was 258.574) with
  `rel_l2_mean 0.43856861163734573` and `alpha 1.500100016593933` unchanged, and
  `scratchpad/contract_resume_ifc_poisson.json` is byte-identical to
  `contract_smoke_ifc_poisson.json`.
- **The TIMEOUT implication is real and correctly flagged.** `torch.save` is
  called ONCE, after all training stages complete, so `last.pt` is an
  all-or-nothing "finished" marker: a preemption or TIMEOUT at 95% loses
  everything and the requeue restarts from epoch 0. Strictly this is the
  condition slurm_rules §5 calls an ALGO bug — but the letter of immutable 8 is
  satisfied, the card itself asserts resume "is already implemented" and forbids
  further edits (adding intra-training checkpointing would be the third edit
  that draws a FAIL), so the builder is correctly boxed in. **Operational
  consequence for the debugger: classify a TIMEOUT/preemption on this card as a
  budget/INFRA event and resubmit with more walltime — do not count it as an
  ALGO attempt, and do not "fix" the checkpointing.**
- Seeding ✓ — smoke_eval.py:245 `torch.manual_seed(args.seed); np.random.seed(
  args.seed)` (`torch.manual_seed` covers CUDA), plus per-use
  `torch.Generator().manual_seed(args.seed)` at :247/:302; stdlib `random` is
  never imported or used; `score_panel.py:90-94` sets `PYTHONHASHSEED` and
  `CUBLAS_WORKSPACE_CONFIG`.

### 3.5 SLURM correctness — SUGGEST (5 non-blocking notes)

`bash -n` run by me on all five scripts, verbatim output:
```
bash -n OK: 01_train_eval.sh
bash -n OK: 02_guard_contract.sh
bash -n OK: 03_aggregate_panel.sh
bash -n OK: submit_seeds_2_3.sh
bash -n OK: submit.sh
```
Conforming: `--partition=gpu` and `--gres=gpu:h100:1` match `project.yaml
sbatch:` (ADR 0005) and the gres is typed; `--requeue`; `--exclude=hpc-93-36`
has precedent (`state/maintainer_report.md:18`, CUDA-busy node); `--output/
--error` absolute under `${OUTPUTS_ROOT}/s4_hybrid_routing/B1/slurm/%x_%j.{out,
err}` with `mkdir -p` before use in every script; all paths absolute;
`01_train_eval.sh:37` takes `SEED="${1:?…}"`; `submit.sh` is seed 0 only
(ADR 0004) and additionally fires the guard job; `submit_seeds_2_3.sh` exists
and is correctly parked for the end-of-round top-3 pass; `--time` present in
every header; `--dependency="afterok:jid:jid…"` syntax is correct; job names are
set at submit time as `r1-s4_hybrid_routing-B1-s{seed}`.

- **S1 (non-blocking)** — `01_train_eval.sh:23` hard-codes
  `#SBATCH --job-name=r1-s4_hybrid_routing-B1` without `-s{seed}`; only the
  `--job-name` override in `submit.sh:45` / `submit_seeds_2_3.sh:30` conforms to
  the mandated pattern. Same S1 the s1/s5 reviewers raised; unavoidable (sbatch
  directives cannot interpolate `$1`). **Never `sbatch 01_train_eval.sh`
  directly.**
- **S2 (the one that can cost 4 GPU-hours)** — the per-dataset walltimes exist
  ONLY inside `submit.sh::walltime_for()` (`submit.sh:34-39`); the header default
  in `01_train_eval.sh:30` is `02:00:00`. A debugger resubmitting a single failed
  heavy dataset as `sbatch 01_train_eval.sh 0 sharp__allen_cahn_2d` silently gets
  2 h — under the builder's own p100 upper bound of 233 min — and, because of the
  end-of-training-only checkpoint, the TIMEOUT discards all work.
  **Minimal fix (no code change): always resubmit as
  `sbatch --time=04:00:00 --job-name=r1-s4_hybrid_routing-B1-s0 <wt>/scripts/01_train_eval.sh 0 <dataset>`,
  or re-run `submit.sh`.**
- **S3 (walltime deviation D3) — accepted, and better-supported than the builder
  argued.** The card's part 3 item 4 says 08:00:00/03:00:00; the scripts use
  04:00:00/02:00:00. The builder justified this only from p100 ledger entries
  ×5.25 stages, claiming "the h100 speedup for this workload is unmeasured" —
  but `state/timing_ledger.json` *does* contain an h100 panel analog the builder
  did not cite: job 65988184 (`mf_fno_transfer_film_modes`, all six panel
  datasets, 200 ep, h100) = **36.62 min**, against a p100 per-dataset sum of
  ≈154 min for the same architecture → **≈4.2× h100 speedup**. Applying it:
  allen_cahn ≈ 44.4/4.2 ≈ 10.6 min × 5.25 ≈ **56 min**, so `04:00:00` carries
  ~4× headroom and the card's `08:00:00` would be oversized — which slurm_rules
  §4 explicitly warns blocks backfill. The deviation from the locked card text
  is a mechanics call governed by slurm_rules §4 + ADR 0005 (which post-dates
  the card), not a design-intent change; it is correct.
- **S4 (waste, non-blocking)** — `03_aggregate_panel.sh:21` requests
  `--gres=gpu:h100:1` for a job that by construction performs zero GPU work (it
  is a cache-only recombination; a cache miss is *designed* to fail on the
  00:20:00 wall). It will occupy an H100 slot and queue behind GPU availability
  for a ~1 min JSON merge. Could be submitted with no gres; harmless as-is.
- **S5 (watch item)** — `02_guard_contract.sh:19` `--time=00:30:00` is the
  tightest budget in the set. The only h100 guard-set analog in the ledger is
  0.77 min (job 65988185, champion, 3 datasets @2 ep); ×5.25 stages plus this
  family's much heavier full-field corrector eval path should still fit, but the
  2-epoch CPU evidence (`ext__helmholtz_2d` train_seconds = 4525 s on the login
  node) means the margin is estimated, not measured. If the guard job TIMEOUTs,
  that is a budget event: resubmit with `--time=01:00:00`, not an ALGO attempt.

### 3.6 Smoke-test evidence — PASS

`build_notes[1..3]` quote the contract-tier commands verbatim
(`score_panel.py --family_dir <wt>/models_r1/fno_transolver_seq --datasets
{ext__helmholtz_2d|ifc_poisson} --epochs 2 --seed 0 --out <wt>/scratchpad/… 
--no_cache --env MFFP_CTX_SOURCE=auto`) and all three result files exist in
`<worktree>/scratchpad/` (+ `.log` copies). Verified contents:
`contract_smoke.json` → helmholtz nRMSE 22.6131929812646, skill 68.639,
`metric_source per_sample_mean`, `reference_type copylf`;
`contract_smoke_ifc_poisson.json` → 0.4385686116373455, skill 12.182,
`reference_type paper_bar` (ADR 0002 ✓); `contract_resume_ifc_poisson.json`
identical to the latter.

**The card's core readouts are present** — I opened the family JSONs myself
(`round1/eval/results/fno_transolver_seq/*_e2_s0.json`):

| dataset | alpha | alpha_least_squares | base_only_rel_l2 | ctx_source | stage3_joint |
|---|---|---|---|---|---|
| `ext__helmholtz_2d` | **0.0** | 0.8390567 | 22.613192981264618 | **real_lf** (ctx_fidelity 1) | false |
| `ifc_poisson` | **1.500100016593933** | 1.5 | 0.4900025652737079 | **fno_base** (ctx_fidelity 32) | true |

Both branches of the context path are exercised, and helmholtz confirms the
paper claim that the gate collapses the hybrid **exactly** to the FNO when the
correction is useless: `alpha = 0.0` and `rel_l2_mean == base_only_rel_l2 ==
base_only_rel_l2_final_fno = 22.613192981264618` to the last digit. On
`ifc_poisson`, 0.438569 vs base_only 0.490003 = **−10.5%**, reproducing the
brainstormer's pre-relocation numbers exactly — the strongest available evidence
that edits (a) and (b) are behaviour-neutral.

**Note for the initial-analyzer**: none of these readouts appear in the
`score_panel.py` aggregate. They live only in
`${ROUND_ROOT}/eval/results/fno_transolver_seq/<dataset>_e200_s0.json`
(gitignored, main tree, NOT under `outputs_root` — by card mandate).

### 3.7 Blast radius — PASS

`git diff round1-substrate..HEAD --stat` = 17 files, 1370 insertions, 0
deletions: `models_r1/fno_transolver_seq/{INSPIRATION.md,manifest.json,model.py,
smoke_eval.py}`, `notes/handoff_experiment_{starter,builder}.md`,
`scratchpad/contract_*.{json,log}` (6), `scripts/*.sh` (5). No substrate file,
no factory surface, no eval-layer file. `git status --porcelain` is clean;
`models_r1/fno_transolver_seq/__pycache__/` exists from the login-node runs but
is gitignored (`round1/.gitignore:5`) and holds only `.pyc`, which `code_hash`'s
`rglob("*.py")` cannot pick up.

## Card-field check

Locked fields verified programmatically against the starter's committed version
(`git show 9646a8e:…/B1.json`): **NONE changed**. The builder wrote exactly its
allowed set — `status`, `scripts_path`, `output_paths`, `build_commit`,
`build_notes`. `build_commit` matches worktree HEAD `4691d1f…`; all five
`scripts_path` entries exist; `output_paths.{eval,slurm}` are under
`${OUTPUTS_ROOT}/s4_hybrid_routing/B1/` and `output_paths.training` correctly
records the card-mandated `round1/eval/results/fno_transolver_seq`.

## Action items for the next stages

1. **Orchestrator**: submit via `scripts/submit.sh` (seed 0 + guard + afterok
   aggregate). Do not launch `submit_seeds_2_3.sh` (ADR 0004).
2. **Initial-analyzer**: the panel geomean is **only** in
   `${OUTPUTS_ROOT}/s4_hybrid_routing/B1/eval/result_panel_s0.json`. The
   documented glob `result_*_s*.json` will also match six per-dataset files
   (`result_ext__helmholtz_2d_s0.json` etc.), and **each of those carries a
   top-level `panel_geomean_skill` key that is the geomean over that ONE
   dataset** (the contract smoke shows `panel_geomean_skill: 68.639` for
   helmholtz alone). Read the per-dataset files for per-dataset skills only.
   Pull `alpha` / `base_only_rel_l2` / `ctx_source` from the family JSONs named
   in 3.6, and remember to check `peak_mem_mb` in the first 256² sharp result
   (the builder's unresolved open risk).
3. **Debugger**: see S2 (resubmit with explicit `--time`) and the
   end-of-training-only checkpoint — a TIMEOUT/preemption on this card is a
   budget event, not an ALGO attempt, and the family must NOT be edited to fix
   it (card part 3 item 2).
