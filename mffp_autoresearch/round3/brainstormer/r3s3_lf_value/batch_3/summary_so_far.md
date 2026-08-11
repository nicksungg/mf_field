# Summary So Far — Stream `r3s3_lf_value`, Batch 3

Paths are relative to `/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch/round3` unless absolute.

## 1. Websearch findings + prior-art verdict

Source: `websearches/r3s3_lf_value/batch_3/report.md` (5 iterations, 14 WebSearch calls, 10/10 bodies fetched).

The K1 row of the prior-art table is the one this batch is scoped to:

> **K1 — pre-registered knee prediction** on the film-transfer cells: emit the training-free surrogate's predicted step-max knee cap *before any leg runs*, then confirm with a minimal 3-cap ladder — **preempted-but-MF-composition-open** … "Do not claim saturation-point prediction, knee detection, or an exchange rate. Open: **zero anchors on the target cell** (all retrieved predictors consume a partial curve there); a **training-free structural** predictor rather than meta-features or a sibling-curve corpus; the **MF condition-coverage** axis with LF absent from the test path; and **pre-declaration + adjudication** of a numeric cap."

Method prior art that must be cited as method, never as our finding: projective early stopping / `b_sat` / pre-exponential point (`https://arxiv.org/pdf/2201.12150`); Kneedle knee detection (`https://kneed.readthedocs.io/en/stable/`); effective data transferred `D_T = k(D_F)^a N^b` (`https://arxiv.org/pdf/2102.01293`); pre-registration for predictive modelling (`https://arxiv.org/abs/2311.18807`). Two quotable novelty anchors: BNSL — "there does not (currently) exist a way to extrapolate the scaling behavior after that additional break" (`https://arxiv.org/pdf/2210.14891`); and the survey's meta-feature branch (Leite & Brazdil; Ruhkopf et al.) still consumes a partial empirical curve on the target dataset. The closest training-free theory (`https://arxiv.org/pdf/2510.14878`) predicts **KRR's own** curve and uses an **absolute-MSE-threshold** sample complexity — the websearcher explicitly flags that as the contrast to cite for using a threshold-free statistic instead.

Websearcher's brainstormer directives (§"For the brainstormer" 1–7): quote K1 verbatim; register on the step-max knee cap, not an absolute R threshold; price the instrument honestly (surrogate is 11 % worse in level on ch, 0.5753 vs 0.5178; Pearson collapses to 0.622 with `--kernel linear`); carry `--strat-mask` from the start; convert every clause through `c_ds` and carry `tau_rel`; name the forward-sensitive subpopulation correctly and never write "non-identifiable".

## 2. §12 conventions verbatim

Round-3 `program.md` is a 67-line delta document; its stream conventions live in `§4` (stream table) and `§5` (immutables), which incorporate round-2 §12 by reference. Verbatim:

> | `r3s3_lf_value` | lever | What is LF-at-train worth on the honest panel (coverage/amplitude mechanisms, ch identifiability-vs-trainability), with matched with/without arms at matched procedure? |

> ## 5. Immutables
> Round-2 §12 methodological rules apply verbatim (registration-of-lifts, zero-information nulls, matched-procedure arm comparisons, target-scaler pre-flight, "unidentifiable" phrasing rule, zero-information-null publication rule).
> Guarded surfaces unchanged: never edit `mf_field/factory_mffp/{data,baselines,eval,references,scripts}`, `factory.md`, or generator surfaces (`mf_field_eloise_data`, `benchmark_42` generation code) — the ADR-sanctioned data swaps of 2026-08-03/05 are complete and no further generator-side mutation is in scope for this round.
> Model/experiment code lives in each experiment's worktree under `models_r2/`-style family dirs (round-2 contract, `../round2/program.md` §9).

And from `program.md §2` (binding on every ifc number this card may emit):

> **Affine-floor rule (degeneracy audit 2026-08-05 …):** ifc_poisson's condition→HF map is EXACTLY affine on the repaired rows (oracle-affine residual 5.4e-16), and on ifc_heat a 6-dof affine fit on the 5 HF train rows already beats the paper bar (nRMSE 0.0709, skill 0.96). Every card reporting an ifc number therefore reports the fitted `affine_on_hf_train` floor next to it …

Batch-3 slot scope (`state/batch3_scope_2026-08-10.md`): "**r3s3_lf_value — ONE card: knee-predictability**, registered against the film-transfer baseline per the operator's round-orientation directive (ADR r3-0006 units)."

## 3. Within-stream prior cards

- **`experiment_cards/r3s3_lf_value/batch_1/B1.json`** (model, complete): LF-at-train value on the honest panel is *entirely* the supply of distinct condition rows (E_cov/E_total in [0.972, 1.024] on 30/30 cells); `A2_lf_covered` is the same learned function as `A0_nolf`. Left the *cost* curve unmeasured; demanded the arm-invariant scaler repair.
- **`experiment_cards/r3s3_lf_value/batch_2/B2.json`** (model, complete, `falsification_verdict: confirmed`): ch + ifc_heat, 150 legs, 98.6 min/seed (1.972 min/leg, `state/timing_ledger.json`). Measured ch mean-R ladder over caps {5,10,20,40,80,160,395} = {0.2386, 0.3853, 0.5090, 0.7021, 0.9013, 0.9671, 0.9969}; step-max knee cap **80**. Delivered the training-free instrument `tools/coverage_knee_surrogate.py`, which reproduced that ladder at Pearson 0.9842 (63 cells, mean |dev| 0.0386 R = 1.57 `tau_rel`), put its step-max knee on the **same** cap on ch (80) and ifc_heat (5), and matched the ch deciding step to 2.0 % of one `tau_rel`. Also: 27/100 ch test rows are forward-sensitive (no knee at any cap, 52–64 % of residual error, unmoved by 8x HF budget); the D-D mediator clause's headline was a linear-fit artifact (`tools/mediator_collapse_fitform_audit.py`).
- Part 7 `next_direction` (verbatim, the scope basis): "Batch 3 of this stream should choose KNEE-PREDICTABILITY over consolidation … (1) run the surrogate on the film-transfer cells and EMIT the predicted knee caps as a pre-registered clause before any leg is launched, with the falsification stated on the step-max knee cap (the seed-stable statistic) and NOT on an absolute R threshold — part 5's own knife-edge at 0.90 (seed 1 at 0.89838, 6.5 % of a tau_rel under the line) …; (2) run a MINIMAL confirming ladder — three caps bracketing the predicted knee, not seven …; (3) carry the stratified readout from the start …; (4) do NOT re-run the D-D mediator clause in its B2 form."

## 4. Cross-stream cards

- `experiment_cards/r3s1_factorised/batch_1/B1.json` — independently found the same 27 hard ch rows (two-population split, 1.0632, worse than `ref_zero`, at every seed). Caps any ch bulk-mean claim.
- `experiment_cards/r3s2_field_reach/batch_2/B2.json` — source of the stream-wide clause-hygiene rules now in the scope doc (no threshold inside its own statistic's fold spread; justify a grid's FLOOR; no 0-epoch selector admitting out-of-sample-unscorable candidates).
- `experiment_cards/r3s4_audit/batch_2/B2.json` — G5 fit-set re-pricing (adopted); F1 ULP tolerances; `models_r3/_common/ckpt_binding.py` (branch `round3/exp-r3s4_audit-B2`, commit `da855da`) which every batch-3 family must adopt. Confirms `sharp__phase_field_crystal_2d` "is enumerated in NO falsification clause" as of its era — i.e. **no certified pfc `tau_rel` exists** (`state/anchors_repaired/noise_floor.json` covers only the 5 pre-ADR-r3-0005 cells).

## 5. Reopen candidates

None. All eight round-3 cards carry `reopen_candidate: false` (scan of `experiment_cards/*/*/*.json`).

## 6. Prior-round record

- Round-2 `r2s3_lf_train_signal-B3` is this stream's inherited anchor (11.1689 [10.9988, 11.3390] copy-LF skill units). **Confirmed** and re-reproduced by B1/B2's A1 legs (post-repair seam -0.75..+0.10 %/seed) — a reproduction seam, not a target.
- Distillation from an LF-consuming teacher, LF-pretrain→HF-finetune (`mf_fno_transfer_film` — now the *denominator*, ADR r3-0006), and auxiliary MF losses: **refuted / preempted** for this stream by B1 (all `preempted (cite)` or certified null). Not re-proposed.
- Round-1's `revin_lf` two-scaler finding: superseded on the repaired panel by B2's `per_rung_max_fullpool` arm-invariant scaler (**untested-on-repaired-panel** in its original form; not revisited).
- Round-2 §12 arm-comparison mis-specification rule ("compare at matched rows and matched procedure"): **confirmed** and discharged by B2's scaler repair; inherited here unchanged.
- Absolute-threshold recovery clauses (B2's R >= 0.90 leg): **refuted as an instrument** — seed 1 landed at 0.89838, 6.5 % of a `tau_rel` under the line. Any batch-3 clause must be threshold-free in R.

## 7. What is UNKNOWN

1. **Does the surrogate predict, or only postdict?** Both its successes (ch, ifc_heat) were fits to ladders that already existed. There is no measurement of it on a cell it was not tuned against, and the websearch verdict says every retrieved competitor consumes a partial curve on the target cell — so a zero-anchor prediction is untested by us *and* by the literature.
2. **Is the step-max knee even resolvable on the ratio-2 dense ladder?** Recomputed here from B2's own per-cap table: the ch deciding step (40→80, 0.1991) beats the runner-up (20→40, 0.1931) by **0.0060 R**, and per-seed the knee *flips* (seed 0 → 80, seed 1 → 80, seed 2 → 40). B2's headline knee is a mean-curve argmax whose margin sits *inside* the certified floor (`tau_rel` ch = 0.0151 nRMSE => 0.020–0.029 R). This was not noticed on B2 and is the single most important unknown for the batch-3 design.
3. **What are the knees on `sharp__allen_cahn_2d`, `sharp__fisher_kpp_2d`, `sharp__phase_field_crystal_2d`, `ifc_poisson`?** Never measured, never predicted. Only ch and ifc_heat have ladders.
4. **Is any cell other than ch adjudicable at its own certified floor?** `tau_rel` in film units (= `tau_rel` x `c_ds`) is 0.0217 (ch), 0.0455 (fkpp), 0.0761 (ac), 0.3359 (ifc_heat), 0.5627 (ifc_poisson), and **undefined for pfc**. The two ifc cells' floors are 15–26x ch's — whether *any* ladder statistic can clear them is unknown and directly relevant to ADR r3-0007.
5. **Does the forward-sensitive no-knee subpopulation exist off ch?** Unknown; B2 measured it only on ch.
6. **Is the surrogate's own prediction draw-stable?** Its A0 analogue is a closed-form fit on `n_hf = 5` rows; only 3 draws were ever run. The fold population of the closed-form stage has never been enumerated (scope rule 3).
