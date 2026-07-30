# Handoff from code-reviewer — 2026-07-30T02:40Z

**For**: orchestrator, experiment-debugger, experiment-initial-analyzer,
experiment-mechanism-analyzer
**Experiment**: s4_hybrid_routing-B2 (card_type: model, 3 arms, 13-task array)
**Diff reviewed**: `round1-substrate..79b20d78cb55a7c36b3e3485a24144f49144f2a5`
**Attempt**: 1

## VERDICT: SUGGEST — submit as built, no builder fix required

Every load-bearing claim in this build is verifiable and verified: `model.py` is
byte-identical to the vendor (`diff` against `git show
4691d1f:models_r1/fno_transolver_seq/model.py` is empty; sha256
`9e8fbacd79377e39…` on both sides), the three arms' `--env` sets equal the
card's `recipe.env` non-underscore keys plus that arm's `_arms` deltas
**exactly** (20 keys each, machine-compared field-by-field against the card
JSON, no extras and no omissions), all seven scripts pass `bash -n`, the blast
radius is 28 files entirely inside `models_r1/ scripts/ notes/ scratchpad/`, and
no guarded surface is touched (`git status` on `round1/{eval,tools}/`,
`mf_field/akash/`, `factory_mffp/{eval,baselines,references,scripts,data}/`,
`program.md`, `project.yaml`, `subagents/` is empty; `eval/cache/` is
`.gitignore`d and is written by the eval layer itself, not edited). The card's
core instrument holds up under independent inspection: the four alpha legs are
computed from ONE pre-stage-3 correction field in `_alpha_diagnostics`
(smoke_eval.py:~790), the `zero`/`b1_insample` legs reproduce B1's own committed
contract smoke (22.613192981264618 vs `git show
4691d1f:scratchpad/contract_smoke.json` → 22.613192981264614, i.e. agreement to
16 significant digits, confirming the base path is unchanged), and no test data
enters any alpha fit — `a_ls` uses `R[val_idx]`/`C_val`, the repaired line
search uses `base_oof[val_idx]` vs `Y_hf[val_idx]`, the scalar blend's `a` is
fitted on the same HF-train val split (its test-fitted curve is emitted but
explicitly labelled `ORACLE_…`), and the LSI transfer function is fitted on
`LF_tr[fit]`/`R_tr[fit]` only. The repaired gate is exactly the B1 diagnosis's
target (`val_rel_l2_base_insample` 22.98 vs `val_rel_l2_base_oof` 14.19 in the
committed helmholtz diag, with the B1 protocol vetoing at alpha 0 where the
repaired one accepts 1.045), the 0-containing shrinkage grid is untouched
(`cands = sorted({0.0} | …)`, and the whole selection loop is line-for-line B1's),
arm C's copy-LF base is bit-equal to the frozen baseline
(`abs_dev_from_frozen = 0.0`; scored 0.32945012604380175 **is**
`copylf_baselines.json`'s 0.3294501260438018), and the vendored LSI reproduces
the promoted tool to 7 digits (`skill_LSI` 7.095512099613908 vs `tools/index.md`
7.095513). The verdict is SUGGEST rather than PASS purely because of five
next-stage items — chiefly that the dense-context path (16 384 context points)
has **never executed anywhere**, so the screen job is its first run and its
walltime is unmeasured, and that the C1 contrast as the card defines it mixes a
post-stage-3 scored number against a pre-stage-3 leg.

## Findings

| Q | Verdict | Finding |
|---|---|---|
| 3.1 card-implementation alignment | PASS | All four part-3 edits trace to code; nothing extra. See table below. |
| 3.2 recipe fidelity | PASS | 20-key `--env` set per arm == card recipe ∪ arm deltas, machine-verified; epochs 200, seed 0, family_dir, base_commit, datasets all match; no hyperparameter outside recipe ∪ part 3 ∪ build_notes. |
| 3.3 §5 immutables | PASS | No guarded path in the diff; scoring only via `score_panel.py`; seed 0 (ADR 0004); 200-epoch smoke tier; no pre-falsified lever re-proposed; ADR 0009 satisfied (no PDE at test time). |
| 3.4 model-card contract | PASS | manifest.json / smoke_eval.py 6-arg CLI / INSPIRATION.md (all 11 `prior_art.citations` present) / `last.pt` resume implemented **and drilled**. |
| 3.5 SLURM correctness | PASS | 7/7 `bash -n` OK; partition `gpu` + `gpu:h100:1` (project.yaml/ADR 0005); absolute paths; logs under `${OUTPUTS_ROOT}/…/B2/slurm/`; `--time` on every job; array map dry-run reproduces the card's 6+6+1; `submit.sh` = seed 0 only; `submit_seeds_2_3.sh` present. |
| 3.6 smoke evidence | PASS | Four contract-tier `score_panel.py` results committed under `scratchpad/`, exit 0, finite; all three arms exercised; command shape in build_notes. |
| 3.7 blast radius | PASS | 28 files, `models_r1/ scripts/ notes/ scratchpad/` only; card diff touches only builder-writable fields. |

### 3.1 — part-3 items → code

| card part 3 item | where |
|---|---|
| vendor @4691d1f, `model.py` byte-identical | `diff` empty vs the git object; sha256 table in `INSPIRATION.md` |
| edit 1: `_fit_alpha` gains a scoring base; `S4_GATE_BASE=oof` scores against `base_oof[val_idx]`; all four alphas + pre-stage-3 test nRMSE emitted | `smoke_eval.py::_fit_alpha` (new `base_val`/`keep_shrinkage` args), two calls with the same `(R[val_idx], C_val)`, `gate{}` block, `_alpha_diagnostics()` |
| edit 2: `S4_CTX_POINTS=full` → `n_ctx = Hc*Wc`, query chunking at 4096 | `n_ctx_req/n_ctx_eff/chunk`, threaded into `_train_corrector`, `c_idx`, `gamma_init_for`, `_joint_finetune`, `_corr_full_field` |
| edit 3: `S4_BASE_MODE=copylf` + `hf_minus_copylf`; stages 1/1b/3 skipped; base asserted vs `copylf_baselines.json` | the `copylf` block + `if cfg["base_mode"] == "copylf"` branches; V4 raises before training |
| edit 4: sidecars (LSI, scalar blend, anatomy, gamma, bands, arm-C ablations), all through `round1/eval/nrmse.py` | `_sidecars()` + `b2_ext.py` §3a/3b/4; every metric calls `ev["nrmse"].nrmse`, sha256 recorded in each diag |

## SUGGEST items (for the orchestrator / debugger / analyzers)

**S1 — the dense path has never run; the screen is its first execution
(orchestrator).** Every committed smoke is on a dataset where `full` == the
sparse count (helmholtz 576, ifc_poisson 1024), i.e. `S4_CTX_POINTS=full` was
never actually dense. On the four 256²/128²-context datasets the corrector jumps
from 1024 to 16 384 context points (fisher_kpp/allen_cahn/cahn_hilliard) or 4096
(pfc). The builder's reason is sound (login node = 1 CPU, no GPU; builders may
not submit SLURM) and `00_contract_screen.sh` is precisely the right gate — it
runs all 23 (arm, dataset-set) combinations at 2 epochs and everything else is
`afterok` on it. Two operational consequences: (a) if it OOMs or times out, the
whole chain sits in `DependencyNeverSatisfied` and must be `scancel`ed (submit.sh
lines 21–25 say so); (b) 23 runs of which 9 are dense at 2 epochs against
`--time=01:00:00` (the card's `_sbatch` number) is not obviously comfortable —
recommend the orchestrator submit the screen with a `--time=02:00:00` override
(a submit-time override, not a card change; ADR 0005 precedent) or be ready to
resubmit it.

**S2 — dense-arm walltime is an extrapolation (orchestrator/debugger).** The
02:00:00 per-task walltime is the card's own `_sbatch` value and is defensible
(ledger: B1 max 31.28 min/dataset on h100, `state/timing_ledger.json`), but the
"+~50 % for the dense corrector stage" is an assumption: the cross-attention
stage sees 16× more context tokens, and `TR` is unchanged (`corr_batch=4`,
`n_query=2048`, `eval_batch=1`). Because `last.pt` is written only after training
completes (B1 behaviour, inherited — see S3), a TIMEOUT on tasks 7–10 would burn
2 h and restart from scratch on requeue. Watch tasks 7–11 (`gate_repair_dense` ×
sharp panel) and task 12; a TIMEOUT there is a RESOURCE issue, not ALGO, and the
fix is a `--time` override on resubmit.

**S3 — mid-training preemption loses that task's progress; bounded and forced
(no action).** Immutable #8 is satisfied in the sense the contract states —
resume from `<ckpt_dir>/last.pt` is implemented, guarded on
`(epochs_target, grid, recipe_hash + every S4_* knob + 14 required keys)`, and
**drilled**: the finished-checkpoint drill reproduces the scored value to 1e-15
(`scratchpad/resume_gate_repair_helmholtz.json`, 5.535748952340294 vs
score_panel's 5.5357489523402945) and the SIGKILL drill shows no `last.pt`, a
fresh train, then a bit-identical resume (`interrupt_armC_b/c.json`,
0.3294501260438018 both). Intra-training checkpointing would require editing
`mf_field/akash/common/mffp.py::train_loop` — a guarded surface — or abandoning
`model.py` byte-identity, so the behaviour is forced by the card and precedented
by B1. Blast radius of one preemption is one array task (≤ walltime), and the
stage structure means a lost task is independently resubmittable.

**S4 — C1 as the card defines it is not a pure alpha contrast (analyzers).**
`recipe.env._primary_contrasts.C1_gate` compares the **scored** arm-A value
against the **pre-stage-3** `b1_insample` leg. Stage 3 (joint fine-tune) only
runs when `alpha > 0`, so the repaired gate *unlocks* stage 3 on exactly the
datasets where B1 was vetoed — observed already at contract tier: helmholtz
legs 22.61 (alpha 0) / 32.25 (alpha_oof) but scored **5.54** with
`stage3=True, alpha=1.0442` (`scratchpad/smoke_rest.log:143`). The instrumentation
supports separating the two effects and the analyzer should: pure gate protocol =
`alpha_protocol_legs.legs.oof` vs `.legs.b1_insample` (same base, same correction
field, bit-identical); gate + stage 3 = the scored value, read alongside
`extra.stage3_joint` and `extra.base_only_rel_l2_final_fno`. Note the diag JSON
itself does **not** carry `stage3_kept`; it lives in the family result JSON under
`results_<arm>/fno_transolver_seq_b2/<ds>_e200_s0.json` (`extra.stage3_joint`).
Also note the repaired gate scores against `base_oof` but applies alpha to the
full-data base — the card pre-registers this two-sided bias and its pfc downside
(part 4 "C1 downside"), so it is a declared property, not a defect.

**S5 — validity gates: read V2 on fisher_kpp; V1 is meaningless for arm C and at
contract tier (analyzers).** V1/V2/V3 are recorded, never raised (V4 raises); the
builder's justification — a score-neutral check must not kill a 45-min scored run
— is documented and I accept it, but the knob is named `S4_REPLICA_ASSERT=1`, so
do not read `within_tol: false` as "the job would have failed". Specifically:
(a) the V2 helmholtz miss (2.3376 vs s6-B1 F6's text 2.1750, +7.48 %) is a defect
in s6-B1's *transcription*, not in this family — I confirmed the vendored LSI
reproduces the promoted tool exactly (`skill_LSI` 7.095512099613908,
`rho_val_heldout` −43.878516815486726, switch 0.0 vs `tools/index.md`'s verified
7.095513 / −43.8785 / 0.0), so the builder's "read V2 on fisher_kpp" resolution
is correct and the arm-C keep bar 0.00692557 (= 0.9 × F6's 0.0076951) stands; the
+0.11 % fisher_kpp reproduction quoted in build_notes has **no committed
artifact**, so the analyzer should take it from the in-run
`sidecars.lsi_reference.V2_*` on the real fisher_kpp task rather than on faith
(same for the standalone fisher_kpp V4 check — though V4 also fires in-run and
raises, so arm C cannot silently score with a wrong base). (b) `V1_replica` is
emitted for arm C too, where it compares a copy-LF-based leg against B1's FNO
number (observed −94.97 % in `diag_attn_gap_fkpp_…`); it is undefined there —
ignore it for `S4_BASE_MODE=copylf`. (c) all V1 values in the committed evidence
are 2-epoch and therefore uninformative (ADR 0007: no screen number is
reportable).

## Verified-clean items the next stages can rely on

- **Per-arm isolation** (the s1 collision trap): every script exports
  `ROUND1_EVAL_RESULTS=<outputs>/eval/results_<arm>`; `recipe_hash` now carries
  all 18 hashed S4_* knobs (distinct: `ec7bbe4b26f7` / `bb1a9e769b0f` /
  `ce6f3fbdbf64`, reproduced in the committed diags), and the resume guard also
  rejects checkpoints missing any B2 key. Result-JSON and ckpt names carry
  `e{epochs}`, so the 2-epoch screen/guard cannot collide with the 200-epoch
  sweep in the same per-arm dir. Cache keys include the env set, so no arm can
  read another's cached number.
- **Chunking uniformity** is real and correctly reasoned: `model.py:204`
  `softmax(self_slice_proj(q_feat), dim=1)` pools over the query set, so a
  4096-query block is not equivalent to B1's unchunked pass on any dataset with
  HW > 4096. Applying it on every arm is what makes V3 exact and C1/C2/C3 paired.
  The cross-card caveat (arm A vs B1 where B1 had alpha > 0: pfc, fisher_kpp) is
  recorded in build_notes and the builder handoff — **carry it into part 5/6**.
  V1 is unaffected on B1's four alpha=0 datasets (no correction is applied there).
- **Deviations, all correct**: arm C excluded from `ifc_poisson` (no test LF ⇒
  copy-LF undefined, ADR 0002; the family raises and the screen runs arm C on the
  five LF-bearing datasets); stage 3 skipped for the copy-LF base (no trainable
  FNO); copy-LF-referenced sidecars emit an explicit `error` field instead of a
  fallback where copy-LF is unavailable (verified in
  `diag_gate_repair_ifc_poisson_e2_s0.json`); the scored path is untouched in
  every case.
- **Reference constants are transcriptions, not inventions**: all six
  `B2.B1_TEST_NRMSE` values equal B1 part 5 `per_seed_nrmse[0]` exactly, and
  `B1_ALPHA_ZERO_DATASETS` is exactly the four datasets where B1's alpha was 0.
- **One nRMSE definition**: `eval/nrmse.py::nrmse` (mean per-sample rel-L2) is
  the same quantity `score_panel.py` extracts (`metric_source:
  per_sample_mean`), so sidecar and scored numbers are comparable;
  `nrmse_def_hash d3d0ade9…` (the round's hash) is recorded in every diag.
- **`b2_ext.py` scope** is exactly: required-knob config (no protocol default;
  `ConfigError` verified to propagate as `ScoreContractError`), read-only eval
  import with sha256, the two vendored tools, and the ablation-aware forward
  (bit-exact at `drop=None`: `forward_selfcheck_max_abs_diff = 0.0` in-run). It
  contains one extra arm tag not in the card (`b1_replica`, from
  `B1_EQUIVALENT`); it is unreachable from the scripts and only documents how to
  reproduce B1 — noted, not a defect.

## Nits (no action)

- `01_train_eval.sh`'s header job name hardcodes `-s0`; correct only because
  `submit.sh` / `submit_seeds_2_3.sh` override `--job-name` per seed. Direct
  `sbatch 01_train_eval.sh 1` would mislabel.
- The `INSPIRATION.md` / build_notes sha256 table lists the **vendor's**
  `smoke_eval.py` hash annotated "modified"; the B2 file's own hash is
  `df79e2650f259bcd…`. Reads correctly but could be misparsed as a claim of
  identity.
- Job names `…-B2-screen`, `…-B2-guard-<arm>`, `…-B2-s0-agg-<arm>` deviate from
  the literal `r1-{stream}-B{N}-s{seed}` pattern; all are `r1-*` and card-scoped,
  and B1 set the same precedent (see `state/timing_ledger.json`).

## Evidence I ran myself

```
bash -n: 00_contract_screen.sh OK · 01_train_eval.sh OK · 02_guard_contract.sh OK
         03_aggregate_panel.sh OK · _arm_env.sh OK · submit_seeds_2_3.sh OK · submit.sh OK
py_compile: model.py b2_ext.py smoke_eval.py scratchpad/unit_b2_ext.py OK
diff <(git show 4691d1f:models_r1/fno_transolver_seq/model.py) models_r1/.../model.py  -> empty
env-set comparison vs card recipe: gate_repair / gate_repair_dense / attn_gap_fkpp -> EXACT (20 keys each)
array map dry-run: 13 tasks = 6 gate_repair x panel + 6 gate_repair_dense x panel + attn_gap_fkpp x sharp__fisher_kpp_2d
card field diff vs HEAD: only status, build_commit, scripts_path, output_paths, build_notes (locked fields byte-equal)
guarded-surface git status (eval, tools, akash, factory eval/baselines/references/scripts/data, program.md, project.yaml, subagents): clean
```
