# code-reviewer — s3_warp-B1 (attempt 1)

**Verdict: SUGGEST** (submit as-is; four carry-forwards belong to the
initial-analyzer / mechanism-analyzer, and one to the operator)
**Reviewed diff**: `round1-substrate` (967562e) .. `4799abdec705d64e8300b18ab0650fb74e012c9b`
**Reviewer**: code-reviewer, 2026-07-29
**Both declared deviations are RULED FAITHFUL-TO-INTENT. Neither weakens the interlock.**

## Justification (one paragraph)

This is a correct, unusually well-instrumented diagnostic build and it should be
submitted. Every value in the locked `recipe` appears verbatim in
`scripts/01_train_eval.sh` (all 11 `S3W_*` knobs, the five-dataset string,
`--epochs 0`, `--seed $1`), every hyperparameter the code carries beyond the
recipe is enumerated in `build_notes` and echoed into the sidecar, and the locked
card fields are byte-identical to the starter's commit (verified by JSON key-wise
diff against `HEAD:experiment_cards/s3_warp/batch_1/B1.json`). The blast radius is
clean (`models_r1/ scripts/ notes/ scratchpad/` only), nothing was written into
`round1/eval/` (the smoke's `ROUND1_EVAL_RESULTS` redirect worked — no
`s3_warp_oracle` directory exists under `round1/eval/results/`), no guarded factory
surface is touched, and no §5 pre-falsified lever is re-proposed. On the two
declared deviations: **(a)** the gradient-normal EPE gate is faithful — the
tangential component of a displacement is unobservable from field values at a
smooth interface, so the literal all-pixel EPE gate would abort a *correct*
fitter; the substitution narrows the statistic to the identifiable subspace on
the interface mask, keeps the same 0.25-cell tolerance, keeps the hard
`WarpHardStop` abort, records the literal outcome
(`passed_epe_literal_all_pixels: false`), and is backed by a second, independent
gate. **(b)** the unattainability claim is **verified, not accepted on prose**: I
independently re-ran the exact-planted-φ path outside the family and reproduced
the builder's floors to four decimals — helmholtz 0.1829, pfc 0.1682, allen_cahn
0.1048 of unwarped — so the card's literal "< 5% of unwarped" is indeed
impossible for *any* optimiser under the card's own `pseudo_LF = warp(HF, d)`
construction, and the replacement `max(0.05 × unwarped, 1.5 × exact-planted-φ)`
is the tightest defensible form (the fitter in fact *beat* ground truth, ratio
0.656). The rung-0 seam is genuine rather than a bypass: warp-off flows through
the same `F.grid_sample` call as every other rung and the sidecar records
`identity_grid_sample_max_abs_dev = 4.44e-16` — a nonzero value that could only
arise if the sampler actually ran. Split-key discipline is exact (one `test*` key;
`_extract_test_metric` provably ignores `ref_*`), the s2 reuse is byte-identical
(sha256 matches, `cmp` exit 0) with the one gram-form NN substitution reproducing
s2's kernel 20/20 in five independent trials I ran myself, and the SLURM script is
syntactically clean and rule-compliant. The verdict is SUGGEST rather than PASS
only because four items must be carried into the analysis stage and one to the
operator; none of them blocks submission.

## Findings table (seven questions)

| # | Question | Verdict | Finding |
|---|---|---|---|
| 3.1 | Card ↔ implementation alignment | **PASS** | All of M0–M9 + split-key discipline + `do_not_promote` + the `ROUND1_EVAL_RESULTS` redirect trace to code (`smoke_eval.py:538–893`). Two declared departures from part-3 literals, both ruled faithful (below). No paraphrase drift found. |
| 3.2 | Recipe fidelity | **PASS** | All 11 `S3W_*` knobs verbatim; `S3W_DIAG_OUT` correctly expanded to the literal absolute path (`01_train_eval.sh:52`); dataset string, `--epochs 0`, `--seed $1` exact. Every non-recipe constant (`SELFTEST_N/CONTROL/AMPLITUDE/FIXEDPOINT_ITERS`, `SELFTEST_GT_SLACK`, `MONOTONE_RTOL`, `OPTFLOW_*`, `CHUNK_*`, `align_corners`/`padding_mode`, the `‖HF‖²` normalisation, the topology threshold) is declared in `build_notes` and re-emitted in the sidecar. One wording nit: F-2. |
| 3.3 | §5 immutables | **PASS** | Data read-only (`panel_data.load_split`); eval layer untouched (`git status mffp_autoresearch/round1/eval/` empty); one nRMSE definition — `rel_l2_per_sample` is *exactly* `eval/nrmse.py`'s per-sample ratio (mean of the same ratios; smoke agrees to 2 ulp), so `score_panel`'s `per_sample_mean` route is not a hand-rolled metric; `nrmse_def_hash` cross-checked against `copylf_baselines.json` and aborts on mismatch (`smoke_eval.py:541`); seed 0; guarded surfaces clean; no pre-falsified lever. `epochs: 0` is the locked recipe value and matches the completed s2-B1 diagnostic precedent. |
| 3.4 | Contract compliance | **PASS** | `manifest.json` (with `"diagnostic": true`), 6-arg CLI (`smoke_eval.py:907–914`), `INSPIRATION.md` citing all four `prior_art` URLs plus the Keil–Craig provenance caveat. Checkpoint-resume from `<ckpt_dir>/last.pt` implemented (`:462–477`, written at `:898`) and gated on dataset+epochs+`nrmse_def_hash`+env+sidecar existence; builder verified a resume re-emit in 27 s. Seeding: `torch.manual_seed`/`np.random.seed`/`cuda.manual_seed_all` from `--seed` (`:517–520`); stdlib `random` is unused. Diagnostic writes `warp_oracle_<ds>.json` + `_phi.npz` under `S3W_DIAG_OUT` = outputs_root. |
| 3.5 | SLURM correctness | **PASS** | `bash -n` run on both scripts — both clean (output: `OK scripts/01_train_eval.sh`, `OK scripts/submit.sh`). `--partition=gpu` and `--gres=gpu:h100:1` match `project.yaml`; typed gres; job name `r1-s3_warp-B1-s0`; `--output/--error` under `<outputs_root>/s3_warp/B1/slurm/`; all paths absolute; `set -euo pipefail`; `mkdir -p`; venv activated; `--time=01:00:00`, `--mem=64G`, `--requeue`, `--exclude=hpc-93-36` (s2-B1 precedent). `01_train_eval.sh` takes `SEED=$1`; `submit.sh` is seed 0 only; **absence of `submit_seeds_2_3.sh` is correct** for a diagnostic (§4.3) and is documented in the script header and `scripts_path.seeds_2_3: null`. |
| 3.6 | Smoke evidence | **PASS** | `build_notes` cites the full `score_panel.py` command; `scratchpad/contract_smoke.json`, `.log` and the 25 kB sidecar are committed and I read all three. Run at `--epochs 0` = the *recipe* tier (correct here: epochs enters no computation, and this is the exact command the job will run). Exit 0, `metric_source: per_sample_mean`, split `test_hf`, nRMSE 0.231032, skill 0.70127, `nrmse_def_hash` matches `copylf_baselines.json`. |
| 3.7 | Blast radius | **PASS** | `git diff --name-only` = 13 files, all under `models_r1/ scripts/ notes/ scratchpad/`. No substrate contamination. Card locked fields verified byte-identical; only `status`, `scripts_path`, `output_paths`, `build_commit`, `build_notes` changed. |

## Ruling on declared deviation (a) — EPE gates on the gradient-normal component

**FAITHFUL TO INTENT. Not a weakened gate.**

Reasoning:

1. **The physics is right.** At a smooth interface, only the displacement
   component along ∇u changes any pixel value; the tangential component slides a
   feature along itself and is invisible to *any* data term. A perfect fitter
   therefore carries O(|d|) tangential endpoint error by construction. The
   builder's synthetic calibration (raw EPE 0.398, normal 0.013, tangential
   0.397 on a 2-cell planted warp) is exactly the signature of that, and the
   smoke reproduces it on real data: `epe_normal_interface_mask_mean` 0.0602 vs
   `epe_tangential_interface_mask_mean` 0.8452. The literal gate would abort a
   fitter that recovered the *entire identifiable* displacement to 0.06 cells.
   That is the precise inverse of M9's stated purpose ("prevents 'optimiser
   failed' being reported as 'no warp regime'").
2. **The gate is not softened.** Same 0.25-cell tolerance; the mask is *narrowed*
   to the interface cells, where the normal direction is well defined and where
   leg B's statistic lives — per-pixel this is a stricter locus, not a looser one
   (in the flat far field *every* direction is unidentifiable, so gating there
   would be meaningless, not conservative).
3. **The abort is still hard.** `WarpHardStop` is raised unconditionally at
   `smoke_eval.py:374–384`; there is no fallback branch, no `try/except` around
   `self_test`, and `score_panel._run_one` converts a nonzero exit into
   `ScoreContractError`, which under `set -euo pipefail` kills the whole job. A
   genuinely broken optimiser fails both the normal-EPE gate and the independent
   nRMSE gate.
4. **The literal number is preserved** (`passed_epe_literal_all_pixels: false`,
   `epe_cells_all_pixels_mean: 0.7320`), so nothing is hidden from the analyzer.

Carry-forward: see **F-1** — `expected_falsification` justifies leg B's 0.5-cell
threshold as "2× the pre-registered 0.25-cell self-test accuracy floor". That
inheritance no longer runs through raw EPE, so the analyzer must instead use the
recorded `leg_B_magnitude_bias` calibration (1.117 on the interface mask, 1.138 on
stratum 0) when evaluating leg B.

## Ruling on declared deviation (b) — the "< 5% of unwarped" clause

**FAITHFUL TO INTENT. The unattainability claim is INDEPENDENTLY VERIFIED.**

I did not take the prose. I re-ran the exact-planted-φ path myself, outside the
family, driving `warp_core` directly (`planted_displacement` seed `0+90210`,
4×4 control grid, peak |d| = 2.0 cells, 40 fixed-point inversion iterations,
8 test HF samples, scored through `eval/nrmse.py`):

```
ext__helmholtz_2d:             unwarped 0.047647  exact-phi 0.008716  frac 0.1829
sharp__phase_field_crystal_2d: unwarped 0.028009  exact-phi 0.004711  frac 0.1682
sharp__allen_cahn_2d:          unwarped 0.011055  exact-phi 0.001158  frac 0.1048
```

These reproduce the builder's 0.1829 / 0.1682 / 0.1048 exactly, and the helmholtz
row matches the committed sidecar's `nrmse_fraction_at_exact_planted_phi`
(0.1829353318280264) to all printed digits. The 10–18% claim is therefore
established from the artifact, not asserted. The floor is *intrinsic*: the card
itself mandates the double-resample construction ("apply a known smooth random
displacement to HF to synthesise a pseudo-LF"), and the primitive is fixed to
bilinear `grid_sample`, so no optimiser can reach 5%. The literal clause is
unsatisfiable by construction.

The replacement `max(0.05 × unwarped, 1.5 × nRMSE(exact planted φ))` is the right
form: it re-anchors the gate to the *achievable* optimum rather than to an
arbitrary constant, and it is a genuinely demanding test — the fitter must land
within 50% of the ground-truth answer. In the smoke it landed at 0.656 of it,
i.e. the fitter beat the exact planted displacement. Implementation matches the
description (`smoke_eval.py:369–372`, an OR whose binding branch is the larger
threshold = the `max` semantics), the literal outcome is recorded
(`passed_nrmse_literal_5pct: false`), and the abort remains hard.

Carry-forward: see **F-5** — the *card's* M9 text now contains a threshold that
provably cannot be met. The clean resolution is an operator amendment to part 3's
M9 clause rather than leaving the contradiction in the locked record. That is the
operator's call, not the reviewer's; I did not touch the locked field.

## Answers to the specific review-focus questions

**2. Rung-0 seam — code-path identity CONFIRMED, the seam proves something.**
- `smoke_eval.py:546–557`: the M0 block builds `zero_phi` and calls
  `wc.warp(...)` → `sampling_grid` → `F.grid_sample(bilinear, border,
  align_corners=True)`. There is no `if phi == 0: return img` shortcut anywhere
  in `warp_core.warp`, `sampling_grid` or `objective`.
- `fit_ladder` rung 0 (`:185–213`) likewise builds an explicit zero `phi32`, runs
  it through `wc.objective` (which calls `warp`) and produces the reported field
  via `wc.warp(lf64, phi64, base64)`.
- The decisive evidence is `identity_grid_sample_max_abs_dev = 4.440892e-16` in
  the sidecar. A bypass would record exactly `0.0`; a nonzero round-off residual
  can only come from the sampler actually executing.
- Result: recomputed 0.32945012604380175 vs `copylf_baselines.json`
  0.3294501260438018, |Δ| = **5.551e-17** ≤ 1e-9. Additionally `:596` cross-asserts
  the ladder's own C0 against the M0 number under the same 1e-9 tolerance.
- Observation (**F-3**): the ladder's C0 is 0.3294501260721531, i.e. Δ = 2.8e-11
  from the baseline, not 5.55e-17 — because `fit_ladder` casts LF to float32
  before re-widening (`lf64 = lf32.double()`, `:180`). Both are far inside 1e-9,
  and the M0 block (the one quoted in `build_notes`) is the float64 path. The
  analyzer should quote 5.55e-17 for the M0 seam and not attribute it to the
  ladder rung.

**3. Split-key discipline — CONFIRMED, and the leaderboard risk is real but
non-code.** `score_panel._extract_test_metric:132` selects
`[k for k in splits if k == "test" or k.startswith("test_")]`; `ref_*` is
structurally invisible. `smoke_eval.py:769–780` emits exactly one `test*` key
(`test_hf` ← `transfer_field`) and routes copy-LF, all six oracle rungs and
`transfer_cond` to `ref_*`. The smoke's observed splits are the promised nine.
Leakage check on the scored predictor: `transfer_field` fits φ on *train* HF only,
selects the donor by nearest neighbour in **LF-field** space
(`nn_index_fields(copylf_test, copylf_train)`) and applies it to the test LF — no
test HF is read (`consults_test_hf: false`, and the train NN index list is
recorded). `do_not_promote: true` is in the result JSON and pre-registered in
part 4. **However** (F-4): `do_not_promote` is consumed by no tool in the round —
`grep` finds it only in `state/orchestrator_flow.md` prose; `tools/render_readme.py`
renders whatever the analyzer puts in `5_actual_result`. The exclusion is therefore
enforced by analyst discipline, and must be. Related: `score_panel` will report a
`panel_geomean_skill` over the five requested datasets; that is **not** the panel
score (the panel is six datasets and this card excludes `ifc_poisson` by design)
and must never be entered as one.

**4. s2 reuse — sha VERIFIED, equivalence test VERIFIED (independently).**
`sha256sum` on both files returns
`59b61cbcb09646539324fe874c0a26722beca0cab592ddf46b50f5eee53887f9`; `cmp` exits 0.
The one substitution is `warp_core.nn_index_fields` (gram form) replacing
`s2_forensics.pairwise_sq_dists` for the LF-field NN; the 21 GB figure is right
(100 × 400 × 65536 × 8 B ≈ 21 GB). I re-ran the equivalence myself over five
independent random `(20, 300)` × `(50, 300)` cases: **20/20 identical indices in
every trial**. The condition-space NN still uses s2's unmodified kernel. Downstream
comparability is additionally *asserted at runtime*: `:663–668` hard-stops unless
the M2/M4 near-interface mask is byte-for-byte s2's stratum 0, and the smoke
reproduced s2-B1's committed helmholtz band edges `[0.0, 6.0, 12.0, 24.0, 48.0]`
and strata edges `[1.0, 5.385164737701416, 11.180339813232422]` exactly (I diffed
against `worktrees/s2_beyond_copy/B1/scratchpad/contract_smoke_diagnostics_ext__helmholtz_2d.json`).

**5. Ladder + M9 evidence — CONFIRMED in the committed JSON.**
`skill_oracle_by_rung` = C0 1.0000000001 → C4 0.7708 → C8 0.5542 → C16 0.4204 →
C32 0.3632 → Cfull 0.3246; `monotonicity.monotone: true`, no violations, at
`tol_rtol` 1e-2. `epe_normal_interface_mask_mean` = 0.06019570 ≤ 0.25, `passed:
true`. `dof_by_rung` C16 = 512, matching the card's "512 dof" learnable rung.

**6. SLURM — all requested items confirmed.** `r1-s3_warp-B1-s0`, `gpu` /
`gpu:h100:1`, `01:00:00`, `--mem=64G`, `--requeue`, `--exclude=hpc-93-36`,
`--out .../result_beyond_copy5_s${SEED}.json` (matches
`output_paths.result_json`), `ROUND1_EVAL_RESULTS` exported before the call,
`S3W_DIAG_OUT` expanded to the literal absolute outputs path, no
`submit_seeds_2_3.sh` (correct for a diagnostic; documented in-script and as
`scripts_path.seeds_2_3: null`). `--no_cache` is justified in-script (a cache hit
would skip the sidecar measurement entirely). Walltime is the one *unmeasured*
quantity — the only GPU datapoint is s2-B1's 0.77 min inference-only diagnostic
and this adds ~3200–3600 Adam iterations per dataset on 100/400 fields at up to
256². My own estimate lands at 10–20 min total, comfortably inside 01:00:00, and
the per-dataset `last.pt` short-circuit makes a timeout recoverable by
resubmission rather than a restart from zero. Not a finding; a watch item.

**7. Guarded surfaces / locked fields — clean.** No path in the diff touches
`round1/eval/`, `project.yaml`, `program.md`, ADRs, subagent prompts,
`factory_root/{eval,baselines,references,scripts,data}`, `factory.md`, or
`akash/`. All 17 locked card fields verified identical to
`HEAD:experiment_cards/s3_warp/batch_1/B1.json`.

## Carry-forward findings (the reason this is SUGGEST, not PASS)

- **F-1 → initial/mechanism analyzer.** Leg B's 0.5-cell threshold was justified
  in `expected_falsification` as 2× the raw-EPE self-test floor; with deviation
  (a) that link is via the identifiable component only. Apply the recorded
  `M9_selftest.leg_B_magnitude_bias` (interface mask 1.117, stratum 0 1.138) when
  reading `leg_B_statistic_median_abs_phi_near_interface` — the statistic is
  biased **high** by ~12–14%, so leg B is harder to fire than its face value
  suggests. The builder flagged this too; it must not be dropped.
- **F-2 → record accuracy.** `build_notes` says the smoke passed "<all 11 S3W_*
  knobs verbatim from recipe.env>", but the smoke's `S3W_DIAG_OUT` was redirected
  to `<worktree>/scratchpad/smoke_diag` (visible in the smoke JSON's `env` block).
  That is *correct hygiene* for a login-node run — it is the reason nothing landed
  in the real outputs tree — but the wording overstates. Consequence to note: the
  smoke's `code_hash` (`ceac7a65…`) therefore differs from the job's, which is
  harmless because the job passes `--no_cache`.
- **F-3 → analyzer.** Quote the M0 seam as 5.551e-17 (the float64 M0 block); the
  ladder's own C0 sits at Δ ≈ 2.8e-11 because `fit_ladder` round-trips LF through
  float32. Both pass 1e-9; they are different numbers and should not be conflated.
- **F-4 → analyzer + maintainer.** `do_not_promote` is inert in tooling. The
  `test_hf` skill from this card must be kept out of the leaderboard, the anchors
  and the top-3 confirmation set by hand, and `score_panel`'s five-dataset
  `panel_geomean_skill` must never be recorded as a panel score.
- **F-5 → operator.** The card's part-3 M9 clause now contains a provably
  unsatisfiable threshold ("< 5% of unwarped"). The record would be cleanest with
  an operator amendment to that clause stating the resampling-floor-relative form.
  Locked field; not touched by this review.
- **F-6 → informational.** Two low-risk items, neither blocking: (i) the gram-form
  NN distance is algebraically equal but not bit-equal to s2's difference form, so
  a near-exact tie among train fields could in principle route one test sample to
  a different donor — bounded impact, and leg D is explicitly non-falsifying;
  (ii) `scratchpad/write_card_s3w_b1.py` (the starter's card generator, committed
  as provenance) would reset the card to `status: "drafted"` and wipe
  `build_notes`/`review_notes` if it were ever re-run. Nothing invokes it.

## Pre-return checklist

- [x] Handoff written with verdict + all seven findings
- [x] Card `status` → `reviewed_suggest`, matching the verdict
- [x] Exactly one entry appended to `review_notes[]`
- [x] Locked fields spot-checked unchanged (17/17 key-wise JSON comparison vs `HEAD`)
- [x] Every finding cites a specific file/line/artifact; no FAIL findings raised
- [x] `bash -n` actually run on both scripts (`OK scripts/01_train_eval.sh`, `OK scripts/submit.sh`)
- [x] Deviation (b)'s unattainability claim independently reproduced, not accepted on prose
- [x] No code or script modified by this review

---

# Post-debug ruling — s3_warp-B1, debug attempt 1 (commit `b72f243`)

**Scope**: focused ruling on the two M9 gate-statistic changes + three spot-checks.
Not a re-review of the build (attempt-1 SUGGEST above stands).
**Reviewer**: code-reviewer, 2026-07-29. **Diff reviewed**: `4799abd..b72f243`
(`models_r1/s3_warp_oracle/{smoke_eval.py,warp_core.py}` + notes/scratchpad).
**Overall verdict: SUGGEST — do NOT scancel job 66011595.** Neither change is a
FAIL. One record correction is mandatory before the analyzer quotes M9.

| # | Change | Verdict |
|---|--------|---------|
| 1 | M9 registers in the exactly-attainable direction | **PASS** (faithful *and* stricter) |
| 2 | Evidence-weighted (\|grad u\|) EPE mean | **SUGGEST** (legitimate correction; the claimed *runtime* teeth do not cover the EPE leg) |
| 3 | float64 reported field in `fit_ladder` | **PASS** (fit path verified bit-identical) |
| 4 | No locked-field edits | **PASS** (3 removed lines, all mechanics) |
| 5 | Stale-artifact quarantine | **PASS** (complete; one structural caveat) |

## 1. Fit direction — PASS (faithful, and stricter on both legs)

More literal than the code it replaces, not less. The card says "*apply a known
smooth random displacement to HF to synthesise a pseudo-LF … the fitter must
**recover it***". `smoke_eval.py:311` now measures `endpoint_error(phi_fit, d_np)`
— against `d` **itself**, the card's noun. The legacy code measured against the
fixed-point inverse `phi(x) = -d(x+phi(x))`, i.e. against a quantity the card
never names. On the nRMSE leg the threshold tightens from
`max(0.05·unwarped, 1.5·exact)` ≈ **0.15–0.27 of unwarped** to the card's literal
**0.05**, because the exact-`d` floor is now 0 by construction
(`gt_field = warp(hf64, d, base64)` is bit-identical to the synthesis, so
`gt_nrmse ≡ 0` and the amendment's slack term is provably inert). Verified in
evidence, not prose — job **66010125** (`dbg1c`) covers **all five** panel
datasets in the new direction with a faithful independent replica of the
implemented statistic (`diagnose_attempt_1c.py:110–112` computes
`(g[iface]*en[iface]).sum()/g[iface].sum()` over the same `dist==0.0` mask, same
`np.gradient`, same planted seed `0+90210`, same `d_np` target):

```
fitter (400 it, lr 0.02), new direction, literal 5% clause:
  pfc          nRMSE 3.12e-06 = 0.00011 unw  PASS   weighted EPE 0.0000
  helmholtz    nRMSE 1.31e-04 = 0.00274 unw  PASS   weighted EPE 0.0027
  allen_cahn   nRMSE 1.50e-05 = 0.00136 unw  PASS   weighted EPE 0.0003
  fisher_kpp   nRMSE 1.56e-06 = 0.00003 unw  PASS   weighted EPE 0.0000
  cahn_hilliard nRMSE 5.42e-04 = 0.01366 unw PASS   weighted EPE 0.0014
```
Margin 3.7×–1600× under the literal clause, versus 2× under the amended gate
pre-debug. Corroborated end-to-end: job **66010795** cleared pfc's M9 self-test
and aborted only later, at the (then-unfixed) seam assert. The legacy lossy
direction is still fitted and recorded non-gating with the
`legacy_target_is_not_the_argmin` certificate, so diagnostic coverage is not lost.

Carry-forwards (analyzer, non-blocking):
- **P-1.** M9 now exercises `moving = HF (sharp), target = pseudo-LF (attainable)`,
  whereas production fits `moving = LF (blurred), target = HF (unattainable)`.
  M9 therefore certifies the optimiser machinery **and identifiability**, not the
  conditioning of the production fit. Say so; do not over-claim.
- **P-2.** `unwarped` flipped argument order (`smoke_eval.py:335`,
  `nrmse(hf_flat, lf_np)`), so the ratio's denominator is now `‖pseudo_LF‖`, not
  `‖HF‖`. Direction-consistent and correct, but `nrmse_fraction_of_unwarped` is
  **not** comparable to the pre-debug field of the same name.
- **P-3.** The 2026-07-29T19:55Z operator amendment is now inert by construction.
  The record would read cleanest with a one-line operator addendum saying the fix
  restored the literal clause. Locked field; not touched.

## 2. Evidence weighting — SUGGEST (legitimate correction of an ill-posed statistic; but the *runtime* control does not give the EPE leg teeth)

**The correction is legitimate, and I am not ruling it a softening.**
Three independent reasons:

(a) *The statistic it replaces is genuinely undefined on pfc.* `warp_core.py:337`
normalises the normal by `gn + 1e-12`; on pfc's s2 mask the median `|grad u|` is
**2.1e-8** against a field-wide gradient RMS of **4.55e-2** — six orders of
magnitude. `n` there is the direction of numerical noise, so `|e·n|` is a
projection of an arbitrary vector onto an arbitrary direction. The fitter
reproduces the target to **1.1e-4 of unwarped** while the unweighted mask mean
sits at **0.3913**. An unweighted gate would abort a fitter that solved the
problem to five digits: the exact inverse of M9's stated purpose.

(b) *It is a no-op where the mask has support.* Support share of the interface
mask: allen_cahn 99.1%, fisher_kpp 100.0%, cahn_hilliard 100.0%. On those three
the weighted and unweighted values agree to ≤2e-4 (0.0003/0.0005, 0.0000/0.0000,
0.0014/0.0014). The change only bites on pfc (12.4%) and helmholtz (51.8%) —
i.e. exactly where the statistic is ill-posed. That is a targeted repair, not a
global loosening.

(c) *It is the physically correct unit.* A normal error `e` at gradient `g`
perturbs the field by `g·e`; `Σg·e/Σg` is the mean field perturbation per unit
gradient, scale-invariant in `u`, and is the statistic that couples to the nRMSE
leg. Mask, tolerance (0.25) and the hard `WarpHardStop` are untouched, and the
unweighted literal plus a support-masked variant are both recorded.

**However, the "runtime proof of teeth" claim does not survive checking, and this
is the reason for SUGGEST rather than PASS.** The implemented control is
`SELFTEST_SABOTAGE_ITERS = 5` (`smoke_eval.py:73`, fitted at `:355–360`). Job
66010125 measured that exact configuration on all five datasets:

```
[sab 5it] weighted EPE / nRMSE-of-unwarped   (gate: EPE < 0.25 AND nRMSE < 0.05)
  pfc           0.2276  PASSES EPE leg   |  0.60014  fails nRMSE leg
  helmholtz     0.2107  PASSES EPE leg   |  0.56725  fails nRMSE leg
  allen_cahn    0.2043  PASSES EPE leg   |  0.61819  fails nRMSE leg
  fisher_kpp    0.2123  PASSES EPE leg   |  0.62341  fails nRMSE leg
  cahn_hilliard 0.1760  PASSES EPE leg   |  0.52593  fails nRMSE leg
```

So on **5/5 datasets the wired-in control fails only the nRMSE leg**. The
0.33–0.35 figures quoted in the handoff and in `debug_notes[0].verification`
belong to a **different, unimplemented** sabotage (`sab lr1e-4`, i.e. lr/200),
which does fail the weighted EPE leg on all five. The runtime assert
(`sab_passes` at `:368–370`) tests the *composite* conjunction, so it is
satisfied by the nRMSE leg alone and certifies nothing about the EPE leg.

Why this is still not a FAIL: the gate is an **AND**, so a weak leg cannot let a
broken fitter through — total strictness is bounded below by the nRMSE leg, which
is now the literal 5% clause with a 10–20× violation by every sabotage variant
and a 3.7–1600× margin for the real fitter. The composite is *stronger* than
pre-debug. Note also that the EPE leg's weakness is largely **inherited, not
introduced**: `SELFTEST_AMPLITUDE = 2.0` is a *peak* displacement whose mean
normal projection over the mask is only ~0.2 cells, so the *unweighted* 5-iter
control already passed 0.25 on 3/5 datasets (0.1927, 0.2094, 0.1766). Weighting
flips 2 more (pfc 0.4195→0.2276, helmholtz 0.2886→0.2107).

Required actions (do not block the running job):
- **P-4 (mandatory, analyzer).** State that M9's operative teeth are the **nRMSE
  leg**; do not report "the 0.25-cell EPE gate certified the fit". Read
  `M9_selftest.broken_optimiser_control.epe_normal_interface_mask_weighted_mean`
  per dataset from the sidecar and record that it is < 0.25 (the control does not
  exercise that leg). Cite job 66010125.
- **P-5 (record accuracy).** `debug_notes[0].verification` and the handoff
  attribute the 0.33–0.35 teeth evidence to the implemented control. It belongs
  to the lr/200 variant. The analyzer should correct this when quoting M9.
- **P-6 (future warp card, one line).** Make the control the lr/200 fit
  (`sab_cfg["lr"] = cfg["lr"] / 200`) instead of / in addition to `iters = 5`, or
  raise `SELFTEST_AMPLITUDE` so the planted signal exceeds the tolerance in the
  gating statistic. Not worth a rebuild now.

## 3. float64 reported field — PASS (fit path verified untouched)

The bug was real and load-bearing, not cosmetic: job 66010795 aborted with
`rung-0 nRMSE from the ladder (0.04478044967257278) disagrees with the M0 seam
computation (0.04478044719481978)` — |Δ| = 2.48e-9 against a 1e-9 tolerance, on a
p100. The fix (`smoke_eval.py:184–186`) inverts the cast order only:

```python
lf64 = torch.as_tensor(lf_np[start:stop], dtype=torch.float64, device=device).view(...)
lf32 = lf64.float()                      # was: lf32 = as_tensor(..., float32); lf64 = lf32.double()
```

Fit path **is** bit-identical: `lf64.float()` and `as_tensor(lf_np, dtype=float32)`
are the same single IEEE round-to-nearest of the same source value for a float32
or float64 `lf_np` (float32 → float64 → float32 round-trips exactly). `grep`
confirms the optimiser sees only `lf32` (`:196 wc.objective(lf32, …)`,
`:204 wc.fit(lf32, …)`); `lf64` is consumed at exactly one site, `:220`, the
reported field. `hf32`/`hf_sq` unchanged. `py_compile` clean on both files.

## 4. Locked fields — PASS

Card diff since the review contains exactly three removed lines:
`"status": "reviewed_suggest"`, the single-element `job_ids` line, and
`"debug_notes": []`. Additions are `status: running`, one `job_ids` entry, one
`debug_notes` entry. All mechanics; every locked field, `recipe`, `build_notes`,
`review_notes` and `operator_amendments` byte-identical. No recipe knob touched
(`01_train_eval.sh` unchanged; `bash -n` clean on both scripts).

## 5. Stale-artifact quarantine — PASS, with a structural caveat

`.../outputs/round1/s3_warp/B1/eval/results/` is **empty**; every pre-fix
artifact sits under `eval/stale_pre_debug1/` (helmholtz `last.pt` + sidecar +
`_e0_s0.json`, and an empty pfc ckpt dir). `find -name last.pt | grep -v
stale_pre_debug1` → none. `score_panel` rebuilds
`_results_dir()/s3_warp_oracle/ckpt_<ds>_e0_s0` (`score_panel.py:85–88`) inside
the emptied tree, always invokes `smoke_eval.py`, and the job passes `--no_cache`
so the 155-entry shared cache is not read (its key covers the code hash anyway).
Nothing pre-fix can short-circuit resume.

- **P-7 (structural, future cards).** The resume guard (`smoke_eval.py:641–645`)
  keys on dataset + epochs + `nrmse_def_hash` + `env` + sidecar existence but
  **not** on a code hash. After any code change, correctness of a relaunch
  depends entirely on the manual quarantine done here. Add `code_hash` to the
  `last.pt` marker in a future family.
- **P-8 (informational).** `warp_core.normal_tangential_error` now returns a
  5-tuple; the committed `scratchpad/diagnose_attempt_1{,b,c}.py` unpack 4 and
  will raise on re-run at `b72f243`. They ran against the pre-change module and
  compute the weighted statistic independently — which is *better* evidence, but
  the analyzer should not expect them to re-execute as committed.

## Checklist

- [x] `bash -n` re-run on both scripts (`OK scripts/01_train_eval.sh`, `OK scripts/submit.sh`); `py_compile` OK on both changed modules
- [x] Teeth claim independently checked against the raw log of job 66010125, not accepted on prose — and found to be misattributed (P-5)
- [x] Exact-direction claim (floor 0, literal 5% restored) verified on all five datasets
- [x] Fit-path bit-identity of the float64 change verified by grep + cast analysis
- [x] Quarantine verified by `find`; `eval/results/` empty
- [x] Locked fields verified via removed-line audit of the card diff
- [x] No code, script or locked field modified by this review
- [x] Card `status` left at `running` (job 66011595 is live; a `reviewed_*` value would corrupt the run-state machine). Ruling recorded here and appended to `review_notes[]`.
