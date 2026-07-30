# code-reviewer — s5_tuning-B3 (review of record)

**Verdict: SUGGEST** (`status: reviewed_suggest`) — submit the main job, screen first.
**Reviewed**: build commit `863983efed34b01774e7ed9a2bc318b1152e0f9a`, branch
`round1/exp-s5_tuning-B3`, diff `round1-substrate..HEAD` (73 files, +12242, all additions).
**UTC**: 2026-07-30.

> This file supersedes and extends the 12:10 pass (same verdict, findings 1/5a/5b/6
> carried forward verbatim in substance). It adds three things that pass could not
> have: the **live GPU screen evidence** for the deferred default-equivalence legs
> (job `66075574`, running at review time), a **logging defect** in `00_screen.sh`,
> and a caveat on the screen's GPU resume drill. The card's `review_notes[]` records
> this single reviewed_suggest entry.

## Verdict paragraph

The two hazards this card carries — oracle leakage and knob drift — are both closed
structurally rather than by prose, and I verified both against the code and the
artifacts rather than the build notes. The four-way default-equivalence claim is
exactly true on deterministic CPU (`0.4900025652737081` for the untouched factory
family, the B2 family, this family, and this family *after the last code edit*), and
I independently confirmed the fourth run was produced by the **committed** code by
recomputing `score_panel.code_hash` over the committed family dir and matching
`4c48904ce26829c5`; every one of the seven arm/branch smokes in `scratchpad/smoke/`
carries a code_hash consistent with the committed tree, so no smoke number predates
the final edit. A4's oracle fence holds on every leg I drilled: `ref_oracle_persample`
structurally cannot match `score_panel._extract_test_metric`'s
`k == "test" or k.startswith("test_")` selector; the scored split is captured with
`json.dumps(..., sort_keys=True)` before the append and a mismatch raises rather than
reports; and the committed A4 artifact shows the scored `test_hf` denormalized by the
D1 **train-only** zscore constant (`mu/sd` byte-identical to A0's), the ORACLE block
carrying all five fence labels, and a firewall report with 6 fit-entrypoint array
checks, `test_target_entered_training: false`, and exactly the two card-sanctioned
fenced uses. The A1-is-a-no-op-on-ifc_poisson result is the card's own declared
expectation and is **not** a global no-op: the per-sample branch demonstrably fires on
`fluid` (n=256, cv 0.184, A1 0.33834 reproducing B2's 0.3383, A5 flooring 64/256 train
and 59/256 test at q25), and `precheck_persample.json` shows `revin_lf` available on
helmholtz *and* both sharp sets, so the branch runs on 3 of the 4 card datasets in the
main job. Knob provenance is mechanically clean: I re-derived the `--env` block and it
is exactly the 12 unprefixed `recipe.env` keys, in ONE `--env` flag (the `nargs="*"`
replacement trap), with every value verbatim; the per-arm overrides match
`recipe.env._arms` row for row; and the resume gate's cross-arm refusal was drilled to
the number — the forced collision run reproduced **A3's** nRMSE `0.3480064534039751`
exactly, proving the refusal path trains fresh rather than mis-resuming. The findings
below are accuracy and contingency defects, not correctness defects: no submitted
number can be corrupted by any of them, but every one is something the orchestrator
must know **before** it reads the screen table and promotes.

## Findings

| # | question | verdict | finding |
|---|---|---|---|
| 1 | card↔implementation | **SUGGEST** | D1–D7, the 4-dataset eligibility 2×2, the 6 arms and instrumentation items 1–6 all trace to code, and every non-trivial choice traces to part 3, the recipe, or `build_notes[13]`. **Gap**: the card's A5 row ("screen only **unless A1 broken**") and `_promotion_rank` rank 2 have no 200-epoch code path — `01_train_eval.sh:123-127` hardcodes `_scored_arms_200ep` (A0,A1,A2,A3,A4) and A5 appears nowhere in it. If `screen_table.py` computes `promoted = A5_revin_lf_floorq25`, `submit.sh` still runs A1 at 200 epochs. Minimal fix (only if that branch fires): add one `run_arm A5_revin_lf_floorq25 "$DS_ALL" revin_lf 1.0 off 0.25` line. |
| 2 | recipe fidelity | **PASS** | Re-derived mechanically, not trusted: the `run_arm` `--env` block carries exactly the 12 unprefixed `recipe.env` keys, key-set equal, all A1 values byte-equal to the card including `MFFP_INSTR_OUT=.../s5_tuning/B3/instr`; exactly **one** `--env` flag per invocation in both scripts (the `score_panel.py:238 nargs="*"` no-append trap). Per-arm overrides match `recipe.env._arms` exactly (A2/A3 on `DS_H3`, A0/A1/A4 on `DS_ALL`, A5 screen-only); `--epochs 200` = `tiers.smoke_epochs`; `--seed "$SEED"` from `$1`; `--datasets` = `recipe.datasets` verbatim. No hyperparameter outside recipe ∪ part 3 ∪ build_notes: `CKPT_SAVES_PER_STAGE=5` is B1/B2-inherited and declared, `BROKEN_FACTOR=3.0`, `PROMOTION_RANK`, tripwire `0.01` and `floor_q 0.25` are card-verbatim. |
| 3 | §5 immutables | **PASS** | Diff touches no `round1/eval/`, `project.yaml`, `program.md`, ADR, subagent prompt, `factory_root/{eval,baselines,references,scripts,data}`, `factory.md`, `akash/`, or `benchmark_42/`. No data regeneration; the B2 vendoring source is read-only and I confirmed `git diff a55c788e..HEAD` on that family in the B2 worktree is empty and the B2 worktree is clean, so the screen's equivalence reference is what the script says it is. All scoring flows through `round1/eval/score_panel.py`; the only direct `smoke_eval.py` calls are the kill+resubmit **drills**, explicitly labelled a DEBUG/DRILL path, and I confirmed **no drill nRMSE is quoted anywhere in the card**. Seed 0 ∈ {0,1,2}; 200 epochs = smoke tier, screen 2 = contract tier; all 12 knobs recorded in `recipe` (immutable #5). No pre-falsified lever (WNO backbone swap / LF low-mode freezing / diffusion prior) re-proposed. |
| 4 | contract compliance | **PASS** | `manifest.json` carries name/description/supports/frozen; `smoke_eval.py` exposes the exact 6-arg CLI (`--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed`); `INSPIRATION.md` cites **8/8** of `prior_art.citations` (checked by string match, not by eye). Resume implemented and drilled mid-stage (`smoke_D.out`: ckpt meta `stage=pretrain epoch=2`, re-invocation printed `[resume] mid-run checkpoint … stage=pretrain epoch=2/10` and continued). Seeding: `torch.manual_seed(args.seed)` (covers all CUDA devices) + `np.random.seed(args.seed)`. **Documented deviation**: checkpoints live at `<ckpt_dir>/<arm_tag>/last.pt` with the flat contract path `<ckpt_dir>/last.pt` read as a **gated** fallback — required because `score_panel` derives one `ckpt_dir` per (family,dataset,epochs,seed) and six arms share it; B2 precedent; drilled to the number (collision refused with `config mismatch ['grad_clip'] … training fresh`, and the refused run reproduced A3's value exactly). |
| 5 | SLURM correctness | **SUGGEST** | `bash -n` run by me on all five `.sh`: **all five clean** (`00_screen.sh OK`, `01_train_eval.sh OK`, `submit.sh OK`, `submit_screen.sh OK`, `submit_seeds_2_3.sh OK`); all three helper `.py` pass `py_compile`. `01_train_eval.sh`'s `#SBATCH` block is `recipe.sbatch.main.directives_verbatim` **character-for-character** (verified by string equality, not inspection). partition `gpu` / typed `gpu:h100:1` = `project.yaml`; `--time` on both jobs; every path absolute; `--output/--error` under `<outputs_root>/s5_tuning/B3/slurm/` and both submitters `mkdir -p` it first; `01_train_eval.sh` takes `SEED=$1`; `submit.sh` = seed 0 only and **hard-refuses without the screen table** (read and confirmed: `exit 1`); `submit_seeds_2_3.sh` present and parked per ADR 0004. **Three residuals**: (a) `set -euo pipefail` with arm order A0→A1→A2→A3→**A4** means a deterministic crash in the non-promotable H3 leg A2 or A3 aborts before **A4, the PRIMARY numeric leg** — and A2 is the one arm never smoked (finding 6); (b) the in-file `--job-name=r1-s5_tuning-B3` lacks the `-s{seed}` suffix `slurm_rules` §1 requires, restored by `submit.sh --job-name=r1-s5_tuning-B3-s0`, so it only bites if someone `sbatch`es `01_train_eval.sh` directly; (c) **new**: `00_screen.sh:155,207,212` write `echo "[$(date)] … exit=$?"` — bash expands `$(date)` first, which resets `$?`, so these three lines **always print `exit=0`** regardless of outcome. Confirmed empirically (`bash -c 'false; echo "[$(date +%s)] exit=$?"'` → `exit=0`). Affected: the `equiv_B2zscore` leg and both resume-drill runs never log their true exit status. Cosmetic for the arms (their results are read from JSON) but it silently hides a failure of the equivalence leg. Minimal fix: `rc=$?` on its own line, then echo `$rc` (the pattern already used correctly at line 74 and inside `run_arm`). |
| 6 | smoke evidence | **SUGGEST** | The contract-tier `score_panel.py` commands are cited and the artifacts exist under `<worktree>/scratchpad/smoke/`; four-way default-equivalence `0.4900025652737081` verified in `poisson__default_{BASE,B2,B3,B3_final}.json`, and the `_final` run's `code_hash` matches a recomputation over the committed tree. **Two overstatements that must be corrected in the card**: (i) `build_notes[3]` and `CONTRACT_SMOKE_EVIDENCE.md` §2/§8 claim "**ALL SIX ARMS**" smoked on `ifc_poisson` — the table lists **five**, and `A2_zscore_noclip` has **no artifact anywhere**; it was scheduled only in `run_smoke_B.sh`, the helmholtz chain that died after one line. `build_notes[11]`'s "verified positive on all six smoked arms" inherits the error. (Mitigation: every code path A2 exercises is covered by A0's zscore branch ∪ A3's `clip=off` branch, and the running screen covers A2 on all 4 datasets — but the card claim is false as written.) (ii) `build_notes[13]` and §8 say `00_screen.sh` re-runs the deferred equivalence legs "including helmholtz and **both sharp sets**" — `00_screen.sh:55` sets `DS_EQUIV=ext__helmholtz_2d,ifc_poisson` only. The **script is card-correct** (`recipe.env._screen` item (a) scopes equivalence to exactly those two datasets); the prose is wrong. |
| 7 | blast radius | **PASS** | `git diff round1-substrate..HEAD --name-status`: 73 files, **all `A`** (no modifications, no deletions), top-level `models_r1` 7 / `notes` 2 / `scratchpad` 56 / `scripts` 8. Zero files outside the allowed four directories; zero guarded paths; worktree `git status --porcelain` empty; single build commit. No substrate-fix contamination. |

## The deferred default-equivalence legs — now discharged on GPU (new evidence)

`build_notes[14]` disclosed, honestly, that the `ext__helmholtz_2d` and
`sharp__fisher_kpp_2d` equivalence legs did not complete on the contended login node
and deferred them to `00_screen.sh`. Screen job **`66075574`** (H100, `hpc-33-13`) was
running during this review and has already produced them. Both card-required legs ran;
the sharp leg was never in the card's scope.

**Screen item (a), first half — env UNSET, three families, same GPU, `--no_cache`:**

| dataset | BASE (factory) | B2 family | B3 family | B2-vs-BASE | B3-vs-B2 |
|---|---|---|---|---|---|
| `ext__helmholtz_2d` | 22.717107316167866 | 22.717078942982294 | 22.71631678149746 | −1.249e−06 | **−3.355e−05** |
| `ifc_poisson` | 0.4902224686159996 | 0.49022214606368447 | 0.4902221997941954 | −6.580e−07 | **+1.096e−07** |

**Screen item (a), second half — B3 arm A0 (`zscore`) vs s5-B2's contract-tier `zscore`:**
`ext__helmholtz_2d` 2.2232125301132375 → 2.2230572247942386 (−6.986e−05);
`ifc_poisson` 0.405026832088504 → 0.4050269175559218 (**+2.110e−07**).

**Reading.** On GPU the agreement is close but **not bit-identical**, on all pairs
including the two families B2's own review already certified as equivalent. The
`BASE`-vs-`B2` pair is therefore the noise calibrator, and the evidence says
nondeterminism rather than a B3 behaviour change: (i) on CPU all four families agree to
**16 digits** on `ifc_poisson`, so the default code path is numerically identical;
(ii) on `ifc_poisson` B3 sits **6× closer** to B2 (1.1e−07) than B2 sits to BASE
(6.6e−07) — a real code difference would push B3 further out on *both* datasets, not
one; (iii) `ext__helmholtz_2d` at 2 epochs is a wildly underfit regime (nRMSE 22.7,
HF-stage `n_eff` 1.01/400, i.e. a single sample owning the entire loss), exactly where
float-reduction-order differences amplify. I could find no code path that can move a
number: with the env unset, `parse_env` returns `maxabs`, `build()` takes the literal
base-family branch, D2/D4/D5/D7 are all off, and the one declared default difference
(no `preds_test.npz`) writes a file without touching a tensor or an RNG draw.

**Consequence for the submit decision: none.** Every falsification leg in this card is
scored against the **paired in-job A0** (same node, same seed, same code_hash), never
against a cross-family continuity number; and `ext__helmholtz_2d` is REPORT-ONLY by
falsification leg (e) (`5.766462 − 9.694961 < 0`, no attainable value clears its floor),
so no helmholtz number carries a threshold anyway. **Gap worth closing cheaply**: there
is no automated assertion or tolerance verdict for item (a) anywhere —
`screen_table.py` globs only `cards4_*.json`, so the `equiv_*.json` never reach
`screen_table.md`, and item (c) got an inline PASS/FAIL block while item (a) got none.
A bit-identity assertion would in fact have **failed spuriously** here, so the right
instrument is a tolerance check calibrated on the BASE-vs-B2 pair. Until one exists,
the orchestrator must read the four `equiv_*.json` by hand (step 2 below).

## Live screen signal at review time (ADR 0007: NOT reportable, orientation only)

`A0` and `A1` both cleared `check_knob_provenance.py` on all four datasets —
`VERDICT: PASS — all 12 knobs arrived from the env on every dataset; leakage fence
intact` — and the D4 instrument is producing exactly the quantities falsification legs
(c) and (d) need: helmholtz HF `n_eff_pooled` A0 **1.0149/400** (B2 measured
1.0179/400 for `zscore` — continuity holds) → A1 **10.863/400**, with `clip_rate` 0.04
(A0) / 0.02 (A1). Contract-tier numbers, never quotable in parts 5–7.

## Independently verified (not taken from build_notes)

- `score_panel.py:132` selector `[k for k in splits if k == "test" or k.startswith("test_")]`
  — `ref_oracle_persample` is structurally unscoreable; `_extract_test_metric` then
  prefers `mean(rel_l2_per_sample)` (`metric_source="per_sample_mean"`), which is the
  round's one definition.
- `smoke_eval.py:659-668` — the `before != after` byte-equality assert on the scored
  split and the `test_like != ['test_hf']` assert, both `SystemExit`.
- A4 artifact: scored `test_hf` `mu/sd` (2.6556e-04 / 1.8622e-04) **identical** to A0's
  and to A1's fallback → the legal readout is a train-only statistic, as pre-registered.
- `scalers.py::_apply_floor_q` — the TEST vector is floored with `ref=per_sample["hf"]`,
  the HF-stage **train** denominators; `fluid__A5` shows the same `floor_value` on all
  three stages (no test-side quantile is ever computed).
- `instr.py` D4 cannot move the trajectory: `per_sample_energy` runs under `no_grad` on
  detached tensors, `grad_global_norm` only when clipping is off, and with clipping on
  the pre-clip norm is `clip_grad_norm_`'s already-computed return value.
- Resume gate `GATE_KEYS` = (epochs_target, grid, modes_cap, scaler_mode, arm_tag,
  scaler_fallback_mode, scaler_floor_q, oracle, grad_clip). **No false-refusal hazard on
  requeue**: every key is re-derived from the same `--env` + CLI the requeued job
  re-supplies and `ROUND1_EVAL_RESULTS` is a fixed absolute path per arm. The gate can
  only refuse a *foreign* checkpoint, and refusal costs a fresh train.
- `score_panel` folds `env` into `code_hash` and the cache key, so the five arms cannot
  collide in the eval cache; the screen's 2-epoch checkpoints live under
  `screen/results/<name>` and cannot contaminate `eval/results_<TAG>`.
- Tool CLIs match the call sites: `dc_pattern_split.py --preds LABEL=path`,
  `paired_arm_displacement.py --datasets/--arm_root/--ctrl_root` (its `_find` uses a
  recursive `ckpt_{ds}*/**/preds_test.npz` glob, so the `<arm_tag>/` subdir is handled),
  `target_range_placement_audit.py --datasets --out`.
- Builder choices `build_notes[13]` (a)–(d) are all **within card discretion**, none
  needs an amendment: (a) A4's legal readout via D1 is precisely what the card's D5 row
  calls "fallback global constant"; (b) `MFFP_REF_SPLITS_ARE_REF_ONLY` defaults to `1`
  and hard-raises if `!= 1` while the oracle is on — strictly tightens the card's fence;
  (c) D2-inert-when-fallen-back is required or A5 crashes on `ifc_poisson`, it is
  recorded in the JSON, and `scalers.build` still raises for direct callers; (d) the
  stricter resume gate can only cause a fresh train, never a wrong resume.

## Submit-time instructions (ADR 0007 — screen first)

1. The screen (`r1-s5_tuning-B3-screen`, job `66075574`) is already running. Let it
   finish. `submit.sh` refuses until `.../B3/screen/screen_table.md` exists (verified
   refusal, `exit 1`) — do not bypass it.
2. Before promoting, read **three** artifacts, because `screen_table.md` contains only
   the `cards4_*` rows:
   - `screen_table.md` — promotion trace + the broken rule;
   - the screen's slurm `.out` — the `[identity] VERDICT` line (A1 == A0 on
     `ifc_poisson`), the `[drill] VERDICT` line, and `precheck exit=0` (**the part-3
     item-5 tripwire reports; it does not abort** — the screen continues either way);
   - `.../B3/screen/equiv_{BASEfactory,B2default,B3default,B2zscore}.json` — the
     default-equivalence legs. **There is no automated verdict for these** (finding
     above). The numbers are already tabled in this review; treat BASE-vs-B2 as the
     nondeterminism calibrator, not zero. There is no sharp-set equivalence leg and the
     card does not ask for one.
3. Confirm `cards4_A2_zscore_noclip.json` exists and is finite before `submit.sh` —
   A2 is the one arm never smoked (finding 6), and `set -e` means an A2 crash takes
   **A4, the PRIMARY leg**, with it (finding 5a). If A2 crashed in the screen, route to
   the debugger *before* `submit.sh`, not after.
4. If the screen promotes **A5** rather than A1 (finding 1), do **not** run `submit.sh`
   as-is — it would run A1 at 200 epochs regardless. Route back to the builder for the
   one-line arm-list amendment first.
5. Then `bash <worktree>/scripts/submit.sh` (seed 0, all five scored arms, one job,
   ~69 min inside a 03:00:00 budget). Do **not** invoke `submit_seeds_2_3.sh` in-round
   (ADR 0004).
6. Ask the builder/debugger to correct `build_notes[3]`, `build_notes[11]` and
   `build_notes[13]` (the "all six arms" and "both sharp sets" overstatements) — the
   analyzer will otherwise read them as fact.

## Notes for the initial-analyzer

- The PRIMARY leg (falsification (a)) must be read from
  `splits.ref_oracle_persample.rel_l2_mean` / `rel_l2_per_sample`, **not** its `nRMSE`
  field. `_ref_split` mirrors the scored split's schema, in which `nRMSE` is the
  backward-compat ratio-of-sums while the round's one definition is the per-sample
  rel-L2 mean (what `score_panel` uses for `test_hf`). At contract tier the two differ
  by 15% (0.7237 vs 0.6285) — comparing the ratio-of-sums against a skill bar derived
  from the per-sample metric would be an apples-to-oranges error. Label the row
  LEAKED/ORACLE per part 4 (g)(5).
- The `cv` in `precheck_persample.json` is the CV of the denominators `s_i` (helmholtz
  5.4765); the card's 0.689 / 0.0024 / 0.0100 are B2's `hf_lf_ratio_cv` — different
  statistics, do not conflate (`build_notes[10]` flags this correctly).
- The screen's GPU resume drill is weaker than the build-time one: it runs
  `--epochs 200` under `timeout 120`, and at ~35 s per 200-epoch `ifc_poisson` train on
  an H100 run 1 will **complete** rather than be killed, so run 2 will print
  `[resume] loaded finished checkpoint` (finished-checkpoint reload) rather than the
  mid-stage `stage=pretrain epoch=k/N`. Both satisfy the grep, so the drill will report
  PASS. The **mid-stage** resume evidence is the build-time login-node drill in
  `build_notes[8]` / `scratchpad/smoke_D.out`, which I verified directly.
- `00_screen.sh` reads the B2 family from a live path in another card's worktree
  (`worktrees/s5_tuning/B2/models_r1/mf_fno_transfer_film_scaler`). I confirmed it is
  byte-identical to `a55c788e` and clean today; if that worktree is ever rebuilt the
  equivalence legs would silently soft-fail (the screen has no `-e`).

---

## POST-SCREEN ADDENDUM (screen `66075574` completed 12:20:47 PDT, 8m21s)

The screen finished during this review. Three findings are resolved operationally,
and one screen verdict line needs adjudication before the orchestrator reads it.

**Resolved.** (i) The screen **promoted `A1_revin_lf`** ("rank 1 A1_revin_lf: not
broken -> PROMOTED"), so finding 1's A5 contingency does not trigger. (ii)
`cards4_A2_zscore_noclip.json` exists and is **finite on all four datasets**
(2.020932 / 0.409504 / 0.907771 / 0.248162), retiring the never-smoked-A2 risk
behind the `set -e` arm ordering (findings 5a + 6). (iii) No arm is broken — all
six 4-dataset geomeans lie in 6.07–14.57 against A0's 7.48, none near the 3.0×
bar.

**`[identity] VERDICT: FAIL` is SPURIOUS — do not treat it as a blocker.**
`00_screen.sh:189` asserts screen item (c) with **strict float equality**
(`v0 == v1`) on a nondeterministic GPU:

| comparison | ifc_poisson rel. gap |
|---|---|
| **A0 vs A1 (the asserted identity)** | **+2.156e−07** |
| BASE vs B2, env unset — *certified-equivalent families, same job* | −6.580e−07 |
| B2zscore vs B3 arm A0 — *both zscore* | +2.110e−07 |
| B2 vs B3, env unset | +1.096e−07 |
| A2 vs A3 — *the clip-off twin of the same fallback pair* | +2.680e−06 |
| A1 vs A5 — *D2 provably inert after fallback* | +1.887e−06 |
| **A0 vs A1 on deterministic CPU (login node)** | **0.000e+00** (bit-identical) |

The asserted gap is *smaller* than the same-code nondeterminism floor measured on
already-certified families in the same job, and the mechanism is recorded in every
artifact (`scaler_mode_effective: zscore`, `scaler_per_sample_available: false`,
reason `"train LF/HF condition vectors are not row-aligned"`) — A1 on `ifc_poisson`
executes literally A0's zscore code path. **The card's declared A1-fallback identity
holds.** The assertion needs a tolerance, not the code. Minimal fix (post-hoc, does
not block this submit): `math.isclose(v0, v1, rel_tol=1e-5)` and print the relative
gap next to the verdict. Same root cause as the missing tolerance on item (a) — I
flagged before seeing this that a strict bit-identity assertion would fail spuriously
on GPU; item (c) is that prediction realized.

**Resume-drill prediction confirmed.** The screen logged `[resume] loaded finished
checkpoint …` + `[drill] VERDICT: PASS`. Run 1 *completed* (~35 s) rather than being
SIGKILLed at the 120 s timeout, so the GPU drill shows finished-checkpoint reload,
not mid-stage resume. Immutable #8 rests on the build-time login-node drill
(`stage=pretrain epoch=2/10`, verified directly) plus the code path.

**Net ruling: proceed.** Record `A1_revin_lf` as the promoted identity in the card
(ADR 0007), then `bash <worktree>/scripts/submit.sh`. The two screen lines an
operator would stop on — the `[identity]` FAIL and the *absence* of any equivalence
verdict — are both adjudicated here; neither is a blocker.
