# round3/tools — index

Shared, parameterized instruments for round 3.
Everything here takes CLI arguments only: **no hardcoded stream, batch or output paths**.
Run under the repo venv (`source ${PROJECT_ROOT}/.venv/bin/activate`) and, for anything heavier than a few seconds, under `timeout --kill-after=30s 1200 python ...`.

Every tool that scores imports `mffp_autoresearch/round2/eval/{nrmse.py,panel_data.py}` read-only, so all numbers are on the round's own metric definitions.

| tool | what it measures | invocation | provenance |
|---|---|---|---|
| `make_round3_anchors.py` | builds `state/anchors/launch_anchors.json` (per-card panel geomeans, training-free floors, repaired-ifc floors) from the anchor cards' output trees | `python tools/make_round3_anchors.py` | round-3 launch (ADR r3-0001 D6) |
| `recompute_ac_reference_floors.py` | recomputes the allen_cahn copy-LF reference and floors after the test-split trim | `python tools/recompute_ac_reference_floors.py` | ADR r3-0003 D1 |
| `trim_ac_task_void.py` | removes the task-void allen_cahn test rows (per-row copy-LF gap below threshold) | `python tools/trim_ac_task_void.py` | ADR r3-0003 D1 |
| `response_decomposition.py` | **whether a model learned a condition->field MAP at all**: per-arm response amplitude (`sigma_pred/sigma_hf`), response alignment (`cos(pred anomaly, HF anomaly)`), own spread, plus pairwise "how far apart are two arms AS FUNCTIONS" distances. Two arms can share an nRMSE for opposite reasons; alignment ~0 means condition-independent noise. | `python tools/response_decomposition.py --dataset <name> --pred LABEL=/path/preds.npz [--pred ...] [--pred-key pred_test] [--split test] [--out out.json]` | `r3s3_lf_value-B1` turn 1 |
| `stale_checkpoint_audit.py` | **result JSONs produced WITHOUT training** — the "re-score that resumed from a completed checkpoint" defect class, which every hash/floor seam passes because references are recomputed live while only the weights are stale. Flags `ckpt mtime < result mtime`, `resumed_from_step >= steps`, collapsed `train_seconds`, and (optionally) checkpoints predating a dataset swap. **Run after any re-score campaign, trim, or ladder repair.** **CAUTION (measured, `r3s4_audit-B1` turn 1):** the `train_seconds_collapsed` rule contributes no detection (sole reason on 0/20 ground-truth stale legs) and 62 false alarms in 859 live legs — read its verdicts alongside `zero_work_resume_scan.py`; and its default `--exclude` list does not cover this round's `results_stale_ckpt_*` quarantine dirs, so pass `--exclude stale_ckpt` when auditing an anchor tree. | `python tools/stale_checkpoint_audit.py --root <outputs dir> [--pattern '*_e*_s*.json'] [--data-changed-after 2026-08-05T18:33] [--out audit.json] [--fail-on-stale]` | `r3s3_lf_value-B1` turn 2 |
| `lsi_transfer_stability_audit.py` | **closed-form correctors that AMPLIFY instead of correcting.** Reads `T_band_mean_abs` / `band_contribution_profile` / `split_protocol` from any diag sidecar in the `s4_router → r2s2_stack → r3s2_stack_ic` lineage and flags `AMPLIFYING` (\|T\|>1 in a band), `SEED_UNSTABLE` (band \|T\| swings >2× across seeds), `SAMPLE_STARVED` (`n_fit` below the tolerance) and `UNREGULARISED` (ridge 0 on an amplifying cell). The failure it was written from turned a 3-sample unregularised Wiener fit above the LF Nyquist into a 15× scored-nRMSE swing. **Run after any card whose stage 2 contains an LSI/Wiener/deconvolution pre-stage, and after any change to the fit-fold protocol.** | `python tools/lsi_transfer_stability_audit.py --diag-root <eval dir> [--pattern 'diag_*_e200_s*.json'] [--amplify-tol 1.0] [--seed-ratio-tol 2.0] [--min-fit 32] [--out audit.json] [--fail-on-flag]` | `r3s2_field_reach-B1` turn 1 |
| `ckpt_data_binding.py` | **role-resolved checkpoint<->data content binding** — vendored verbatim (sha `2d7d8ee5...cf426d`) from `r3s4_audit-B2`, where its R1 predicate priced 108/108 (recall 27/27 · 18/18 · 18/18, 0/27 false RETRAIN, the ONLY rule with non-zero REREFERENCE recall), strictly dominating whole-dataset hashes and the wall-clock rules. `census`/`record` compute per-role sha256s over a dataset dir; `predicate_r1` maps mismatched consumed roles to RETRAIN / RESCORE / REREFERENCE / NONE. Promoted into `make_round3_anchors.py::binding_gate()` (2026-08-10, package item 3): any leg with a recorded binding that mismatches current data on a role it READ hard-fails the anchor build; CLEAN legs are exempted from the wall-clock audit via `--exempt-legs`; binding-less legs (all pre-contract legs today) stay under the clock fallback. The save hook (`models_r3/_common/ckpt_binding.py`) is a batch-3 contract requirement. | `python tools/ckpt_data_binding.py record --dataset_dir <d> --dataset_name <n> [--roles_read train_lf,train_hf,...]` · `verify-legs --legs <scan.json>` | `r3s4_audit-B2` |
| `zero_work_resume_scan.py` | **legs whose WEIGHTS DID NOT MOVE during the run that produced their result JSON** (`executed_steps == 0`), with no wall-clock term at all. Successor instrument to `stale_checkpoint_audit.py`'s wall-clock rules: priced over 859 live legs, `train_seconds_collapsed` was the SOLE reason on 62 legs that had all actually trained (53 of them the round's own 2-epoch contract tier) and the sole reason on **0** of the 20 ground-truth stale legs — it is strictly dominated by `ckpt_older_than_result`, since a run that trains rewrites `last.pt`. This tool reports only the necessary condition (a fact, not a proxy), derives the step count when families omit `steps`/`resumed_from_step`, groups by (family, dataset), names its own blind spot (`UNDERIVABLE`), and reports **checkpoint data-binding coverage** so the routed fix can be tracked. **`ZERO_WORK` is not a verdict** — it is contamination only if the TRAINING arrays changed, which no timestamp can decide (the round-3 repair copy preserved file mtimes, so the ifc arrays' mtimes predate the checkpoints they invalidated). | `python tools/zero_work_resume_scan.py --root <outputs dir> [--pattern '*_e*_s*.json'] [--exclude stale_ckpt] [--read-ckpt-binding] [--data-hashes state/data_hashes.json --verify-binding] [--out scan.json] [--fail-on-zero-work]` | `r3s4_audit-B1` turn 1 |
| `floor_precision_seam.py` | **SCOPED-ARM CAVEAT (measured, `r3s4_audit-B2` turn 2): `FROZEN_ARMS` excludes `affine_on_hf_train`, and `arms_from` (:138) raises `SystemExit` on it — so this tool cannot band the arm `program.md` §2 mandates on every ifc number; use `floor_arm_precision_band.py` for that arm.** **the floating-point precision band of each frozen training-free floor arm, per dataset** — the number an F1-class tolerance must be floored at. Two estimators: E1 = float64→float32 path difference (deterministic, but identically 0 where the arrays ship float32, so it under-measures exactly where no control exists), E2 = max over B random ±1-ULP dithers of the float32 view (defined everywhere; measured ≥ E1 on 10/10 datasets). Also a **defect detector**: a band orders of magnitude above the others means the arm is DISCONTINUOUS in its data, not merely imprecise — `--nn-stability` then reports the NN-index flip fraction, argmin margins and any `std == 0` condition dimension. **Run before pinning any exact-reproduction tolerance, and after any regeneration, trim or dtype change.** | `python tools/floor_precision_seam.py [--datasets a,b,c] [--floors-json PATH] [--arms nn_condition,train_mean,zero] [--b-dither 8] [--seed 0] [--nn-stability] [--floor-tol 1e-9] [--out seam.json] [--fail-on-discontinuity]` | `r3s4_audit-B1` turn 2 |
| `per_row_paired_decomposition.py` | **whether a paired arm delta is BROAD or a handful of rows, and whether the cell is one population or several.** The round's nRMSE is a *mean of per-row ratios*, so `mean_i (e_ref_i - e_arm_i)` is exactly the paired delta and decomposes per row for free. Reports sign counts, median-vs-mean, top-k concentration, a **row-level** bootstrap CI in skill units (read straight against a certified `tau_rel` via `--tau-rel`), and two TRIMMED re-scores — drop the k worst reference rows, and adversarially drop the k rows the effect most depends on. An outlier-driven effect dies under the adversarial trim; a real one does not. `--bimodal-split T` splits rows at a per-row reference error of T (`ref_zero` is 1.0 by construction, so T≈0.8 = "as bad as predicting zero") and scores the populations separately with each one's share of the total gain — a cell whose skill is a mixture statistic must be read as one. **Run on any card whose headline is a paired delta, and on any cell suspected of denominator/outlier domination.** Enforces a metric seam: refuses to decompose if `mean(rel_l2_per_sample) != nRMSE` at 1e-12. Two input modes: `--result` (any result JSON carrying `rel_l2_per_sample`; no dataset access) or `--pred LABEL=…npz --dataset` (per-row errors computed against the HF test split via `panel_data`). Warns on `sharp__allen_cahn_2d` in `--pred` mode (ADR r3-0003 trimmed the scored split; `load_split` returns the untrimmed original). | `python tools/per_row_paired_decomposition.py --arm A --ref B {--result <result.json> \| --pred A=/p/a.npz --pred B=/p/b.npz} [--dataset <name>] [--bimodal-split 0.8] [--tau-rel 0.3612] [--pred-key pred_test] [--split test] [--boot 10000] [--out out.json]` | `r3s1_factorised-B1` turns 2–3 |
| `task_linearity_audit.py` | **whether a cell is a closed-form task in disguise, and whether its condition→field map is learnable at all.** Model-free, seed-free, training-free, dataset-side only: oracle affine residual (same estimator as the certified `affine_on_hf_train` floor), PCA rank of the field ensemble, map-smoothness ratio (nearest-in-condition vs random-pair field difference), and mean-removed variance fraction. Verdicts `CLOSED_FORM_TASK` / `NON_SMOOTH_MAP` / `LEVEL_DOMINATED`. **Run before committing GPU time to a cell**: it separates cells where nonlinear MF fusion can pay from cells a 6-parameter closed form already solves, and it flags the project's `rel-l2-is-level-dominated` trap. | `python tools/task_linearity_audit.py --datasets a,b,c [--split test] [--max-samples 128] [--affine-tol 1e-4] [--smoothness-tol 0.95] [--out report.json]` | `r3s2_field_reach-B1` turns 2–3 |
| `amplitude_calibration_audit.py` | **whether a cell's score is an AMPLITUDE problem, and whether an arm is norm-blind.** The round's nRMSE is a *mean of per-row ratios*, so a cell whose test fields vary mainly in field NORM is scored almost entirely on amplitude, weighted hardest on the smallest-‖y‖ rows — and a model whose output parameterisation renormalises (factorised/`fact` centering, shape-only basis, renormalising decoder) is capped far above the floor no matter how good its shape is. **A residual-energy or per-band audit structurally cannot see this** — it can even report the model as BETTER than the floor. Dataset-side mode reports `CV(‖y‖)` and the **constant-norm oracle** (shape exact, one amplitude; closed form — the weighted median of ‖y‖ with weights 1/‖y‖, asserted against `nrmse()`), i.e. the best ANY norm-blind predictor can do, in skill units, with an `AMPLITUDE_CRITICAL` verdict against `--tau-rel`. Model-side mode adds `CV(‖pred‖)` per arm (0.0 ⇒ literally norm-blind), per-‖y‖-bin rel-L2, and for a paired `--arm`/`--ref` the correlation of the delta with 1/‖y‖ plus each bin's share of the gap. **Run before committing a batch to a cell, and after any card whose model has an encode/decode or basis parameterisation.** | `python tools/amplitude_calibration_audit.py --dataset <name> [--split test] [--tau-rel 10.3128] [--pred A=/p/a.npz --pred B=/p/b.npz --arm A --ref B] [--pred-key pred_test] [--quantiles 4] [--out out.json]` | `r3s1_factorised-B2` turns 3B–3C |
| `transfer_gain_anatomy.py` | **whether a reported band `\|T\| > 1` is a GAIN or a DISPERSION artefact.** `lsi_transfer_stability_audit.py` (and any `AMPLIFYING`-style clause) reads an **unweighted arithmetic mean of `\|T\|` over a band's modes**; this tool publishes the **energy-weighted** transfer beside it, plus the **signed** aggregate (which separates an amplifier from a *canceller* of the upsampler's own content), the coherence against its chance level `1/√n_fit`, and each band's share of the LF and residual energy. Verdicts `TRUE_AMPLIFICATION` / `DISPERSION_ARTEFACT` / `CANCELLER` / `OK` (checked in that order). Adds the two things the falsified card needed: a **`--ridge-ladder`** pricing each candidate's band `\|T\|` *and* its held-out explained variance (so "what shrinkage would have passed, at what cost?" is a number, with `min_ridge_passing_tol` per band), and **`--enumerate-folds`**, which enumerates all `C(Ntr, n_fit)` fit sets exactly — at `Ntr=5` the round's 3 seeds draw only 2 distinct folds, so a clause whose threshold sits inside the fold population is visible as such. Dataset-side, no model/GPU; the estimator is the round's `fit_transfer` arithmetic verbatim and the upsampled LF comes from the FROZEN `round2/eval/panel_data.py::copylf_prediction`. `--diag-root` cross-checks the reproduction against a shipped diag and names the ridge that matches. **Run after any card with an LSI/Wiener/deconvolution pre-stage, and before writing any clause whose threshold is a band-mean gain.** | `python tools/transfer_gain_anatomy.py --datasets a,b [--seeds 0,1,2] [--holdout-frac 0.2] [--n-bands 4] [--amplify-tol 1.0] [--k-cut ladder\|none\|FLOAT] [--ridge-ladder 0,1e-9,1e-6,1e-4,1e-2] [--enumerate-folds] [--diag-root DIR --diag-pattern 'diag_{ds}_e200_s{seed}.json' --diag-key lsi_repair.T_band_mean_abs_reg] [--out o.json]` | `r3s2_field_reach-B2` turns 1-2 |
| `subset_geomean_unit_audit.py` | **whether a panel-geomean delta is being read against a bar calibrated on a DIFFERENT cell subset, and whether the verdict survives a change of denominator.** The panel score is a geometric mean, so its *level* depends on which cells are in it: a skill-unit delta is not comparable across subsets, and ADR r3-0006's re-denomination (`skill_film = skill_copylf × c_ds`) rescales different subsets by different factors. Reports each cell's exact **share of the panel delta in log space** (the only scale-free cross-subset form), then per subset the delta and `\|delta\|/bar` in **both** unit systems with `UNIT_INVARIANT` / `UNIT_DEPENDENT`, a `SUBSET_BAR_MISMATCH` flag plus the exact rescaling factor, and a loud `VERDICT FLIPS ACROSS UNIT SYSTEMS` when the bar is crossed in one system and not the other. Optional `--tau` block asserts that per-CELL ratios are unit-invariant (delta and `tau_rel` share `c_ds`). Two input modes: `--skills-json {"ARM":{"DS":[per-seed skills]}}` or `--diag-root` + a dotted `--nrmse-key` + `--refs`. **Run on any card whose headline is a panel/subset geomean delta, and on every batch-2 card before its numbers are re-expressed in film units.** | `python tools/subset_geomean_unit_audit.py {--skills-json F \| --diag-root DIR --arms ARM,REF --refs ds=v,... [--nrmse-key 'arms.{arm}.nrmse'] [--diag-pattern ...]} --panel a,b,c,d,e [--subset NAME=a,b,c] --bar 0.7624 [--denominator-json state/anchors/film_denominator.json] [--tau ds=v,...] [--unit-tol 0.01] [--out o.json]` | `r3s2_field_reach-B2` turn 3 |
| `coverage_knee_surrogate.py` | **where a condition-coverage ladder's KNEE will be, before any GPU time.** Builds a TRAINING-FREE surrogate recovery curve `R_surr(c)`: RBF kernel ridge fit on (kept standardised conditions → that row's LF field lifted by the FROZEN `panel_data.copylf_prediction` convention), scored with `nrmse.py` against the HF test split, and normalised into the round's own R by using an `n_hf`-row HF fit as the A0 analogue and the full LF pool as the A1 analogue. Also prints the two structural nulls it was written to kill — `design_rank` of `[Z_kept,1]` (the "we ran out of condition-space directions" story) and the nearest-kept-condition FIELD oracle (the "coverage radius" story) — so the user sees *why* the knee sits where it does. Reproduces the round's own per-rung cap draw and its 5-of-400 HF draw independently, or replays a shipped card's exact kept sets with `--kept-from-training-root`. **Run before committing a batch to a coverage/row-count sweep, and to price a knee claim on a cell you have not trained on.** **CAVEAT (measured):** it predicts the SHAPE and KNEE, not the LEVEL (ch full-pool 0.5753 vs the trained arm's 0.5178, 11 % worse) — never quote it as a baseline; and `--kernel linear` does NOT work on a `NON_SMOOTH_MAP` cell (ch Pearson 0.622 vs the RBF's 0.984). Corroborated on 2 cells, so treat a new cell's knee as a pre-registered prediction. | `python tools/coverage_knee_surrogate.py --dataset <name> --caps 5,10,20,40,80,160,395 [--n-hf 5] [--draws 0,1,2\|native] [--kernel rbf\|linear\|both] [--lam 1e-3] [--strat-mask dump.npz::mask_key] [--kept-from-training-root DIR --kept-arm ARM --kept-seed 0] [--out o.json]` | `r3s3_lf_value-B2` turn 1 |
| `mediator_collapse_fitform_audit.py` | **whether a "does arm X collapse onto arm Y's mediator curve?" verdict is a finding or an artefact of the fit's functional form.** Three readouts: (1) the REFERENCE set's own residuals about its own linear fit, grouped by arm/cap — ≥2 sign changes across groups means the line is structurally biased in some x band; (2) the same collapse verdict under linear, quadratic and **isotonic** (PAVA, shape-free monotone) fits of the *same* reference cells; (3) bias vs scatter, by printing the reference cells' own RMS residual about each fit beside the test cells' max. Verdicts `FIT_FORM_ARTEFACT` / `FIT_FORM_ARTEFACT_MEAN_ONLY` / `GENUINE_OFFSET` / `SCATTER_ONLY` / `COLLAPSED`. **Run BEFORE shipping any clause of the form "X collapses onto Y's curve within tol", and in re-analysis of one that was.** Needs no model, data or GPU — just the per-cell (x, y, arm, seed) table. | `python tools/mediator_collapse_fitform_audit.py --cells cells.json --ref-arms A,B,C --test-arms D [--x-key alignment] [--y-key R] [--group-key arm] [--seed-key seed] [--tol 0.05] [--tol-mean 0.025] [--out o.json]` | `r3s3_lf_value-B2` turn 2 |
| `selection_multiplicity_audit.py` | **whether a permutation/p-value-calibrated selection rule is arithmetically sound and whether a correctly-sized rule would change anything.** Two checks a card can otherwise ship broken: (1) the **resolution floor** — a conservative permutation p-value `(1+#{null≥obs})/(1+B)` cannot go below `1/(1+B)`, so if your Bonferroni/Holm threshold is below that, FWER control is IMPOSSIBLE from your own null and the rule silently degenerates to the `SELECT_MIN` fallback; it prints the minimum `B ≥ m/α − 1`. (2) **significance vs effect size** — selected-set sizes under the raw p-threshold, Benjamini-Hochberg FDR, Holm, Bonferroni, and `p ≤ α AND effect ≥ t` for a ladder of `t`, plus set-equality against any number of shipped reference sets. Needs no model, data or GPU — only the emitted per-candidate p-value and effect-size tables, addressed by dotted JSON keys, so it works on any family that emits them. **Run before shipping any card whose selection is calibrated by a null, and in re-analysis of one that was.** | `python tools/selection_multiplicity_audit.py --result LABEL=/p.json [--result ...] --p-key a.b --effect-key c.d {--b-key e.f \| --b 200} [--alpha 0.05] [--fdr-q 0.05 0.01] [--effect-ladder 0.01 0.05 0.10] [--select-min 1] [--reference-set-key NAME=g.h] [--out out.json]` | `r3s1_factorised-B2` turn 1 |
| `fitset_matched_n_audit.py` | **whether a training-free reference floor is being compared at a FAIR fit-set size, and how much of the seam is BIAS versus the reference's own estimator VARIANCE.** A single deterministic refit at the scored arm's `n` (e.g. "the first 320 rows") cannot separate the two, and for a SELECTION arm like `nn_condition` (a discrete argmin over the fit set) it is one draw from a wide distribution: removing rows flips the neighbour for ~17 % of test rows and each flip moves that row by 70-85 `tau_rel`, so the cell number is the RESIDUAL of a cancelling sum, not an n-scaling law. Reports per cell per arm the `systematic_correction` (an EXPECTATION over fit sets, with a standard error), the `selection_noise_sd`, the `frac_folds_breaching_tau` (i.e. the POWER of a single-draw gate), the per-row re-selection anatomy, and optionally a comparand re-pricing with `verdict_sign_unchanged`. When `n_train <= --n-scored` the matched-n question is undefined, so it runs the ANSWERABLE analogue — **exhaustive leave-one-out over all `C(n, n-1)` folds** — instead of skipping: that is how the 5-row ifc `affine_on_hf_train` floor was found to move `ifc_heat` from skill 0.9584 to a LOO mean of 1.8469 (fold sd 10.9 `tau_rel`). **Run before pricing any claim against a floor whose fit-set size differs from the scored arm's, and on any few-row reference floor before quoting it in a rule.** Report-only; re-freezes nothing. | `python tools/fitset_matched_n_audit.py --datasets a,b,c [--arms nn_condition,train_mean,affine_on_hf_train] [--n-scored 320] [--draws 2000] [--draws-affine 50] [--seed 20260810] [--tau-rel ds=v,...] [--best-arm ds=arm,...] [--reference-nrmse ds=v,...] [--compare-skill ds=skill,...] [--floors-json P] [--noise-floor-json P] [--anchors-json P] [--out o.json]` | `r3s4_audit-B2` turns 1-2 |
| `floor_arm_precision_band.py` | **the per-ARM floating-point band of a training-free floor, including `affine_on_hf_train`, plus per-arm adjudication of reproduction misses.** `floor_precision_seam.py` hard-codes `FROZEN_ARMS = (nn_condition, train_mean, zero)` and raises `SystemExit` on anything else (`arms_from`, :138), so it cannot measure the one arm `program.md` §2 makes MANDATORY next to every ifc number — and measured, that arm's band is 1-2 orders of magnitude wider than the others and exceeds the round's per-DATASET recommended tolerances on 8 of 10 datasets, i.e. a per-dataset tolerance (a max over three arms that exclude affine) cannot adjudicate an affine reproduction claim at all. Uses that tool's estimators VERBATIM (`ulp_dither`, `rel`, E1 = float64-vs-native-dtype path difference, E2 = max over B ±1-ULP dithers, `band = max(E1,E2)`) and adds: the affine arm; `--check ds:arm=rel_diff`, which reads a recorded reproduction `rel_diff` against **that arm's own band** (`INSIDE_ARM_BAND` = metrology vs `OUTSIDE_ARM_BAND` = real failure); and the design matrix's rank + condition number, which is what predicts a wide affine band (a zero-variance condition dimension makes the design singular, and the `sd == 0 -> 1.0` remedy that fixes the standardized NN distance does NOT reach the affine arm, which fits on the RAW condition). **Run before pinning any exact-reproduction tolerance an affine or rank-deficient arm must pass, and to adjudicate a reproduction miss as metrology vs defect.** Report-only; does not edit `floor_precision_seam.py`. | `python tools/floor_arm_precision_band.py [--datasets a,b] [--arms affine_on_hf_train,nn_condition,train_mean,zero] [--b-dither 64] [--seed 1] [--tolerances-json P] [--check ds:arm=rel_diff ...] [--floors-json P] [--stripped-root P] [--data-root P] [--out o.json]` | `r3s4_audit-B2` turn 2 |

## Verified invocations (2026-08-10, r3s3_lf_value-B2)

```bash
# coverage_knee_surrogate — replay mode: the EXACT kept sets the card's legs saw.
# Reproduces r3s3-B2 turn 1 cell-for-cell.
python mffp_autoresearch/round3/tools/coverage_knee_surrogate.py \
  --dataset sharp__cahn_hilliard --caps 5,10,20,40,80,160,395 \
  --kept-from-training-root mffp_autoresearch_outputs/round3/r3s3_lf_value/B2/training \
  --kept-arm A3c_lf_uncov_cap
# -> R_surr 0.2430 / 0.4125 / 0.5193 / 0.6790 / 0.8776 / 0.9476 / 1.0003
#    PREDICTED KNEE (step-max) = cap 80, step into it +0.1986
#    (the TRAINED ladder: 0.2386 / 0.3853 / 0.5090 / 0.7021 / 0.9013 / 0.9671 / 0.9969,
#     knee cap 80, step +0.1991 -> agreement 0.0005 R = 2.0 % of one tau_rel;
#     Pearson over the 63 cells 0.9842, mean |dev| 0.0386 R = 1.57 tau_rel)
#    NULL 1 design rank saturates at cap 20 (7.2x below the knee) -> not a rank story
#    NULL 2 nearest-kept-condition field oracle 0.958..1.172 (never beats predicting
#           zero, while the trained full-pool arm reaches 0.5178) -> not a radius story

# coverage_knee_surrogate — STANDALONE (redraws both the HF rows and the per-rung caps
# from the round's own rules; the redrawn HF rows match the card's selected_train_rows
# [55, 88, 133, 202, 293] on draw 0 and the ladder's n_distinct exactly).
python mffp_autoresearch/round3/tools/coverage_knee_surrogate.py \
  --dataset ifc_heat --caps 1,2,5,10,15,45,95 --draws native
# -> R_surr 0.2312 / 0.0831 / 0.5822 / 0.8245 / 0.9308 / 1.0041 / 0.9939,
#    PREDICTED KNEE = cap 5 (n_distinct 15) — the SAME cap as the trained ladder's
#    step-max knee; Pearson over 21 trained cells 0.9774.

# mediator_collapse_fitform_audit — the pre-registered D-D clause of r3s3-B2.
# (cells.json = one record per leg with arm/seed/draw/alignment/R; built in that
#  card's scratchpad from the leg JSONs + eval/result_*.json)
python mffp_autoresearch/round3/tools/mediator_collapse_fitform_audit.py \
  --cells <scratchpad>/dd_cells.json \
  --ref-arms A0_nolf,A1_lf_all,A2_lf_covered,A3c_lf_uncov_cap \
  --test-arms A5_hf_budget_nolf --x-key alignment --y-key R --group-key group --tol 0.05
# -> reference relation is CONVEX: its own linear residuals run +0.0707 (A0, x=0.125),
#    -0.0698 / -0.0979 / -0.1036 / -0.0502 (caps 5-40), +0.0092 / +0.0502 / +0.0741 /
#    +0.0751 (caps 80-395, A1); 2 sign changes, span 0.1787. The TEST cells sit at
#    x = 0.295 / 0.438 / 0.605 — inside the over-predicted band.
#    linear     25/27 negative, mean -0.0834, per-seed max 0.2594 / 0.2292 / 0.1583
#               (reproduces the card's part 5 D-D bit-for-bit)
#    quadratic  13/27, mean -0.0120   isotonic 14/27, mean -0.0156
#    ref cells' own RMS 0.0896 -> 0.0473 -> 0.0259
#    VERDICT: FIT_FORM_ARTEFACT; surviving finding = scatter, not a directional offset.
```

## Verified invocations (2026-08-10, r3s2_field_reach-B2)

```bash
# transfer_gain_anatomy — the falsifying cell, with the shipped-diag seam and the
# fold population. Reproduces the card's own T_band_mean_abs to max abs dev 0.
python mffp_autoresearch/round3/tools/transfer_gain_anatomy.py \
  --datasets ifc_poisson,ifc_heat --seeds 0,1,2 --enumerate-folds \
  --diag-root mffp_autoresearch_outputs/round3/r3s2_field_reach/B2/eval
# -> ifc_poisson b3: unweighted |T| 1.1851 (the clause's statistic) but
#    ENERGY-weighted 0.7427, signed -0.7405, coherence 0.9968 vs chance 0.577,
#    LF energy share 1.18e-03  => DISPERSION_ARTEFACT (no band is TRUE_AMPLIFICATION).
#    ridge ladder: lam=1e-9 takes b3 to 0.9177 with heldout rho 0.998795 vs
#    0.998790 at lam=0 -> min ridge passing tol = 1e-09 (the card's grid floor was 1e-6).
#    FOLD POPULATION: 10 distinct 3-of-5 fit sets, the 3 seeds drew only 2;
#    b3 |T| min/med/max 0.9425 / 0.9995 / 1.1851, 5/10 folds above 1.0.
#    DIAG SEAM: 6 legs, max abs dev 0.

# transfer_gain_anatomy — cross-cell controls incl. the guard cell that trips the
# same audit, and a cell whose shipped fit used a non-zero ridge.
python mffp_autoresearch/round3/tools/transfer_gain_anatomy.py \
  --datasets ifc_poisson,fluid,sharp__cahn_hilliard --seeds 0 --ridge-ladder 0,1e-9,1e-6 \
  --diag-root mffp_autoresearch_outputs/round3/r3s2_field_reach/B2/eval
# -> fluid b3 1.7296 unweighted / 0.6473 energy-weighted => DISPERSION_ARTEFACT
#    (same mode as ifc_poisson), while fluid b4 IS TRUE_AMPLIFICATION (1.1217).
#    sharp__cahn_hilliard b4: signed aggregate -1.0000 at coherence 1.0000 -- the
#    top octave's transfer is an artefact CANCELLER, which the band-limit deletes.
#    Seam identifies ch seed 0's shipped ridge as 1e-06 (dev 0 there, 0.144 at ridge 0).

# subset_geomean_unit_audit — reproduces turn 3 and, independently, part 5's
# per-cell G1 deltas (ac -13.0733, fk -2.3758, ch +0.2454, ifcp -1.9255, ifch -0.1107)
python mffp_autoresearch/round3/tools/subset_geomean_unit_audit.py \
  --diag-root mffp_autoresearch_outputs/round3/r3s2_field_reach/B2/eval \
  --arms A1_stack_ic_reg,A3_direct_ic \
  --refs sharp__allen_cahn_2d=0.0020593576160366327,sharp__fisher_kpp_2d=0.00016524586579046429,sharp__cahn_hilliard=0.041802962686225575,ifc_poisson=0.036,ifc_heat=0.074 \
  --panel sharp__allen_cahn_2d,sharp__fisher_kpp_2d,sharp__cahn_hilliard,ifc_poisson,ifc_heat \
  --subset claimable=sharp__allen_cahn_2d,sharp__fisher_kpp_2d,sharp__cahn_hilliard \
  --bar 0.7624266197396405 \
  --denominator-json mffp_autoresearch/round3/state/anchors/film_denominator.json \
  --tau sharp__allen_cahn_2d=18.61975759925883,sharp__fisher_kpp_2d=10.312814173562199,sharp__cahn_hilliard=0.36124864423263325,ifc_poisson=0.6910000683054431,ifc_heat=0.1640195793751628
# -> per-cell share of the panel delta: ifc_poisson 65.1%, ac 19.6%, fk 10.2%,
#    ifc_heat 9.1%, ch -3.9%  (74.2% from the two floor-disqualified ifc cells).
#    panel        -1.6248 = 2.13x bar | film -0.11542 = 2.13x bar  UNIT_INVARIANT [OK]
#    claimable    -1.8464 = 2.42x bar | film -0.01897 = 0.35x bar  UNIT_DEPENDENT
#                 [SUBSET_BAR_MISMATCH, rescale 0.1446] *** VERDICT FLIPS ***
#    All five per-cell |delta|/(1.5 tau) ratios: UNIT_INVARIANT.
```

## Verified invocations (2026-08-10, r3s4_audit-B1)

```bash
# zero_work_resume_scan — POSITIVE control (the 6 legs quarantined by STOP-THE-LINE #2)
python mffp_autoresearch/round3/tools/zero_work_resume_scan.py \
  --root mffp_autoresearch_outputs/round3_anchors/r2s3_lf_train_signal-B3/results_stale_ckpt_2026-08-09 \
  --exclude __never__
# -> ZERO_WORK 6/6, all r2s3_coverage_panel/ifc_poisson, ckpt mtimes 2026-08-03T22:52..08-04T04:38

# zero_work_resume_scan — LIVE anchor tree (the finding this card contributes)
python mffp_autoresearch/round3/tools/zero_work_resume_scan.py \
  --root mffp_autoresearch_outputs/round3_anchors/r2s3_lf_train_signal-B3 --exclude stale_ckpt
# -> ZERO_WORK 36/111: 18 sharp__allen_cahn_2d (benign: only the TEST split was trimmed)
#    + 18 sharp__phase_field_crystal_2d (pre-box-swap weights scored post-swap).
#    Never surfaced before because the 2026-08-10 re-audit was pattern-scoped to ifc*.

# zero_work_resume_scan — NEGATIVE controls
python mffp_autoresearch/round3/tools/zero_work_resume_scan.py --root mffp_autoresearch_outputs/round3/r3s4_audit/B1
# -> ZERO_WORK 0/15   (the 4 legs stale_checkpoint_audit false-positives are WORK_DONE here)
python mffp_autoresearch/round3/tools/zero_work_resume_scan.py --root mffp_autoresearch_outputs/round3/r3s3_lf_value/B1
# -> ZERO_WORK 0/234

# zero_work_resume_scan — data-binding coverage (quantifies the routed gap)
python mffp_autoresearch/round3/tools/zero_work_resume_scan.py \
  --root mffp_autoresearch_outputs/round3_anchors/r2s3_lf_train_signal-B3 \
  --read-ckpt-binding --pattern 'sharp__phase*_e*_s*.json'
# -> checkpoint data-binding coverage on flagged legs: {'ABSENT': 18}

# floor_precision_seam — reproduces the F1 deciding numbers and finds the sod_1d defect
python mffp_autoresearch/round3/tools/floor_precision_seam.py \
  --datasets ifc_heat,ifc_poisson,sharp__sod_1d,fluid --nn-stability
# -> E1 ifc_heat 1.106e-09 (== the card's 1.1056e-09), sod_1d 7.740e-08 (== the adjudication's
#    7.74e-08), fluid 0.000e+00 (natively float32 -> the path difference measures nothing).
#    Bands: sod_1d 3.013e-01 DISCONTINUOUS, fluid 7.749e-09, ifc_heat 6.607e-09, ifc_poisson 2.530e-09.
#    --nn-stability: sod_1d 56% of test rows re-select their NN atom at 1 ULP, degenerate cond dim [2];
#    0.0% and [] on the other three.
```

## Verified invocations (2026-08-10)

```bash
# lsi_transfer_stability_audit — positive control (the defect it was written from)
python mffp_autoresearch/round3/tools/lsi_transfer_stability_audit.py \
  --diag-root mffp_autoresearch_outputs/round3/r3s2_field_reach/B1/eval \
  --pattern 'diag_*_e200_s*.json'
# -> FLAGGED 3/8. ifc_poisson: AMPLIFYING(b4:66.2), SEED_UNSTABLE(b4:10.6x),
#    SAMPLE_STARVED(n_fit=3), UNREGULARISED(ridge=0); band-4 error contribution
#    s0=4.625 s1=3.833 s2=2312. Also flags the guard cell `fluid` (b4 |T|=15.2,
#    n_fit=206 so seed-stable) and ifc_heat (SAMPLE_STARVED only).

# lsi_transfer_stability_audit — cross-card control on the round-2 anchor
python mffp_autoresearch/round3/tools/lsi_transfer_stability_audit.py \
  --diag-root mffp_autoresearch_outputs/round3_anchors/r2s2_stacked-B1/eval \
  --pattern 'diag_*_e200_s*.json'
# -> FLAGGED 4/7; ifc_poisson reproduces BIT-FOR-BIT (b4 = 6.2398/6.2398/66.219),
#    and sharp__phase_field_crystal_2d is independently flagged
#    AMPLIFYING(b4:10.4) with band-3 error contribution 5.8/10.6/29.2.

# task_linearity_audit — reproduces r3s2-B1 turns 2-3 exactly
python mffp_autoresearch/round3/tools/task_linearity_audit.py \
  --datasets sharp__allen_cahn_2d,sharp__cahn_hilliard,sharp__fisher_kpp_2d,ifc_poisson,ifc_heat,sharp__phase_field_crystal_2d \
  --split test --max-samples 128
# -> ifc_poisson oracle affine 2.92e-08, rank99=5, var@cond 1.000000 => CLOSED_FORM_TASK
#    ifc_heat 0.0376882 (== the certified launch_anchors oracle value) => LEVEL_DOMINATED
#    cahn_hilliard smoothness 0.9796 => NON_SMOOTH_MAP ; fisher_kpp meanrm var 0.00504 => LEVEL_DOMINATED
#    allen_cahn 0.459838 / 0.7912 => mf-fusion-relevant ; pfc 0.776563 / 0.9900 => NON_SMOOTH_MAP
```

## Verified invocations (2026-08-08)

```bash
# response_decomposition — reproduces r3s3-B1 turn 1 exactly
python mffp_autoresearch/round3/tools/response_decomposition.py \
  --dataset sharp__cahn_hilliard \
  --pred A0=.../A0_nolf__sharp__cahn_hilliard__d0__e200__s0/r3s3_lf_channels/sharp__cahn_hilliard_e200_s0_preds.npz \
  --pred A2=.../A2_lf_covered__.../sharp__cahn_hilliard_e200_s0_preds.npz \
  --pred A1=.../A1_lf_all__.../sharp__cahn_hilliard_e200_s0_preds.npz
# -> A0 nRMSE 1.257361 amp 0.5941 align 0.0957 | A2 1.291956 / 0.6147 / 0.1032 | A1 0.528166 / 0.7671 / 0.7128
#    pairwise A0->A2 0.31961, A0->A1 1.04031, A2->A1 1.09378

# stale_checkpoint_audit — positive control (the defect it was written from)
python mffp_autoresearch/round3/tools/stale_checkpoint_audit.py \
  --root mffp_autoresearch_outputs/round3_anchors/r2s3_lf_train_signal-B3/eval \
  --pattern 'ifc*_e200_s*.json' --data-changed-after 2026-08-05T18:33
# -> STALE 6/12 (all six ifc_poisson legs), OK on all six ifc_heat legs

# stale_checkpoint_audit — negative control
python mffp_autoresearch/round3/tools/stale_checkpoint_audit.py \
  --root mffp_autoresearch_outputs/round3/r3s3_lf_value/B1/work --pattern '*_e200_s*.json'
# -> STALE 0/225
```

## Verified invocations (2026-08-10, r3s1_factorised-B1)

```bash
# per_row_paired_decomposition — result-JSON mode; reproduces r3s1-B1 turn 2 part A/C exactly
python mffp_autoresearch/round3/tools/per_row_paired_decomposition.py \
  --result mffp_autoresearch_outputs/round3/r3s1_factorised/B1/training/r3s1_twostage_crosscoef/sharp__cahn_hilliard_e0_s0.json \
  --dataset sharp__cahn_hilliard --arm test_hf --ref ref_head_onestage \
  --bimodal-split 0.8 --tau-rel 0.36124864423263325
# -> delta +1.2455 skill, row CI95 [+1.0430,+1.4555], 3.45x tau_rel; 78/22 rows;
#    median +0.051669 (mean/median 1.008); top5 0.127 top10 0.239;
#    drop10_worst_ref_rows +1.3927, drop10_largest_abs_delta_rows +1.0532 (still 2.9x tau_rel);
#    two-population split: 27 hard / 73 easy, easy delta +1.7272 carrying 101.2% of the gain,
#    hard delta -0.0571 (those 27 rows score 1.0632 -- worse than ref_zero -- at every seed).

# per_row_paired_decomposition — npz mode, cross-stream (r3s3_lf_value-B1 arms)
W=mffp_autoresearch_outputs/round3/r3s3_lf_value/B1/work
python mffp_autoresearch/round3/tools/per_row_paired_decomposition.py \
  --dataset sharp__cahn_hilliard --arm A1 --ref A0 --bimodal-split 0.8 \
  --tau-rel 0.36124864423263325 \
  --pred A1=$W/A1_lf_all__sharp__cahn_hilliard__d0__e200__s0/r3s3_lf_channels/sharp__cahn_hilliard_e200_s0_preds.npz \
  --pred A0=$W/A0_nolf__sharp__cahn_hilliard__d0__e200__s0/r3s3_lf_channels/sharp__cahn_hilliard_e200_s0_preds.npz
# -> nRMSE A1 0.528166 vs A0 1.257361 (both match this file's response_decomposition entry);
#    delta +17.4436 skill, 91/9 rows, top5 0.099 -- LF-at-train is broad, not outlier-driven.
#    Bimodal split: 92 of A0's rows are worse than ref_zero and A1 fixes them (+18.42, 97% of the gain).

## Verified invocations (2026-08-10, r3s1_factorised-B2)

```bash
# amplitude_calibration_audit — dataset-side; reproduces the turn-3 mechanism independently
python mffp_autoresearch/round3/tools/amplitude_calibration_audit.py \
  --dataset sharp__fisher_kpp_2d --tau-rel 10.312814173562199
# -> CV(||y||) 0.0506; CONSTANT-NORM ORACLE nRMSE 0.0398226 = 240.9900 skill
#    => AMPLITUDE_CRITICAL, 23.37x tau_rel.  A norm-blind arm cannot beat 240.99 on
#    this cell; the r3s1 head's `fact` centering emits CV(||pred||) = 0.0000 exactly.
# Cross-cell controls (same command, other cells):
#    sharp__cahn_hilliard  CV 0.0372, oracle 0.6933 skill = 1.92x tau_rel (AMPLITUDE_CRITICAL)
#    ifc_heat              CV 0.0766, oracle 0.8472 skill = 1.23x tau_rel (AMPLITUDE_CRITICAL)
#    sharp__allen_cahn_2d  CV 0.0405, oracle 17.5108 skill = 0.94x tau_rel (not binding)
#    NOTE allen_cahn warns: ADR r3-0003 trimmed the scored test split, load_split is untrimmed.

# selection_multiplicity_audit — reproduces r3s1-B2 turn 1 part C exactly
T=mffp_autoresearch_outputs/round3/r3s1_factorised/B2/training/r3s1_predcrit_cascade
python mffp_autoresearch/round3/tools/selection_multiplicity_audit.py \
  --result ch_s0=$T/sharp__cahn_hilliard_e0_s0.json \
  --result ch_s1=$T/sharp__cahn_hilliard_e0_s1.json \
  --result ch_s2=$T/sharp__cahn_hilliard_e0_s2.json \
  --result fk_s0=$T/sharp__fisher_kpp_2d_e0_s0.json \
  --result ac_s0=$T/sharp__allen_cahn_2d_e0_s0.json \
  --p-key permutation_null.permutation_p_value_per_direction \
  --effect-key selection_context.best_oof_r2_per_direction \
  --b-key permutation_null.B \
  --reference-set-key A1_cap_lift=arms.A1_cap_lift.set_indices \
  --reference-set-key A2_shipped=arms.A2_predcrit.set_indices
# -> RESOLUTION: B=200, m=51 => p_min 0.004975 vs Bonferroni 0.000980 = *** UNREACHABLE ***
#    (min B for reachability: 1019).  n_set: shipped p<=0.05 gives ch 7/8/6, fk 49, ac 18;
#    BH q=0.05 gives ch 1/1/6 (unstable); Holm and Bonferroni give 1 everywhere.
#    `p<=0.05 AND effect>=0.05` equals the A1_cap_lift reference set on 5/5 artifacts.

## Verified invocations (2026-08-10, r3s4_audit-B2 re-analysis)

```bash
# fitset_matched_n_audit — few-row cells take the exhaustive-LOO branch automatically.
python mffp_autoresearch/round3/tools/fitset_matched_n_audit.py \
  --datasets ifc_heat,ifc_poisson \
  --arms nn_condition,train_mean,affine_on_hf_train \
  --compare-skill "ifc_heat=0.9099159980415482,ifc_poisson=5.177118584131835" \
  --out /tmp/fmn_ifc.json
# -> ifc_heat  mode=exhaustive_leave_one_out_C(5,4) arm=nn_condition full=1.3941 matched=1.4525
#              sys=+0.356 tau  sd=0.593 tau  breach=0.2
#    ifc_poisson                                      full=8.0409 matched=8.2822
#              sys=+0.349 tau  sd=0.520 tau  breach=0.2
#    per_arm.affine_on_hf_train: ifc_heat 0.9584 -> LOO mean 1.8469 (sd 10.935 tau, 3/5 folds breach);
#    ifc_poisson 1.5938 -> 4.2335 (5/5 folds breach)  <- the program.md §2 affine-floor rule's fold spread

# fitset_matched_n_audit — random-subset branch (n_train 400 > --n-scored 320).
python mffp_autoresearch/round3/tools/fitset_matched_n_audit.py \
  --datasets sharp__cahn_hilliard --arms nn_condition,train_mean --draws 500 \
  --compare-skill "sharp__cahn_hilliard=13.17806662874691" --out /tmp/fmn_ch.json
# -> full=23.1803 matched=23.5116 sys=+0.917 tau sd=1.751 tau breach=0.608  (B=4000 gives +0.842+-0.028, 0.613)
#    reselection_anatomy_first_n_fit: 17/100 rows change neighbour, skill_shift_over_tau 1.9333
#    (= the shipped G5 single-draw number), top1_row_share 0.4307, n_rows_for_50pct 4
#    comparand_repricing: margin 10.0023 -> 10.3336, verdict_sign_unchanged true

# floor_arm_precision_band — the affine band + per-arm adjudication of D4's @full misses.
python mffp_autoresearch/round3/tools/floor_arm_precision_band.py \
  --datasets ifc_poisson,ifc_heat,sharp__sod_1d \
  --arms affine_on_hf_train,nn_condition,train_mean \
  --tolerances-json mffp_autoresearch_outputs/round3/r3s4_audit/B2/eval/floor_tolerances.json \
  --check "ifc_poisson:affine_on_hf_train=4.842167032143965e-08" \
  --check "ifc_heat:affine_on_hf_train=3.59587222601487e-08" \
  --out /tmp/fapb.json
# -> ifc_poisson  affine=5.6542e-07 nn=3.5227e-09 tm=2.2858e-09 rank=5/6 exceeds_ds_tol=[affine]
#    ifc_heat     affine=3.3773e-07 nn=8.7227e-09 tm=3.1554e-09 rank=4/4 exceeds_ds_tol=[affine]
#    sharp__sod_1d affine=1.1734e-02 (rank 3/4, cond 5.4e15) <- a SECOND degenerate-dim victim G4 does not cover
#    both checks -> INSIDE_ARM_BAND (11.7x / 9.4x inside): D4's affine misses are metrology, not floor error
```
