# Iteration 2 — `r3s3_lf_value` batch 3 (revision of the ladder construction)

## Design context considered

Everything in `iteration_1.md`, plus the constraint it produced: the confirming ladder's **rung spacing** decides whether the step-max knee is resolvable at the certified floor. Additional inputs consulted for this revision:

- `state/anchors/film_denominator.json` — per-cell `nrmse_film_mean` and `c_ds`; `state/anchors_repaired/noise_floor.json` — per-cell `tau_rel`. Derived table (`tau_rel_film` = `tau_rel` x `c_ds`, exact identity since `skill_film = skill_copylf x c_ds`):

  | cell | `nrmse_film_mean` | `c_ds` | `tau_rel` (copy-LF) | `tau_rel` in nRMSE | **`tau_rel_film`** |
  |---|---|---|---|---|---|
  | `sharp__cahn_hilliard` | 0.694750 | 0.060170 | 0.361249 | 0.015101 | **0.021736** |
  | `sharp__allen_cahn_2d` | 0.503850 | 0.004087 | 18.619758 | 0.038345 | **0.076103** |
  | `sharp__fisher_kpp_2d` | 0.037465 | 0.004411 | 10.312814 | 0.001704 | **0.045486** |
  | `sharp__phase_field_crystal_2d` | 0.952757 | 0.012971 | — (none certified) | — | **undefined** |
  | `ifc_heat` | 0.036134 | 2.047957 | 0.164020 | 0.012137 | **0.335905** |
  | `ifc_poisson` | 0.044207 | 0.814353 | 0.691000 | 0.024876 | **0.562718** |

- `state/anchors_repaired/floors.json` floor arms (nRMSE): ch `nn_condition` 0.969007 / `train_mean` 1.001977 / `zero` 1.0; ac 0.979959 / 1.001702 / 1.0; fkpp 0.067797 / 0.064562 / 1.0; pfc 1.187748 / 0.877766 / 1.0; ifc_heat 0.103164 / 0.130729 / 1.0 (+ `affine_on_hf_train` 0.070918); ifc_poisson 0.289472 / 0.324149 / 1.0 (+ affine 0.057375).
- `experiment_cards/r3s4_audit/batch_2/B2.json`: pfc "is enumerated in NO falsification clause" — no certified pfc `tau_rel`.
- Base code: `models_r3/r3s3_row_efficiency` @ `eedcc655b70471687c9b7f8e537ad206eddd437c` (branch `round3/exp-r3s3_lf_value-B2`) — hardcodes `CAP_LADDERS` for ch/ifc_heat only and a ch-only hard mask, so it must be generalised. `models_r3/_common/ckpt_binding.py` @ `da855da` (branch `round3/exp-r3s4_audit-B2`), importing the unedited `round3/tools/ckpt_data_binding.py`.
- Timing: B2 measured 1.972 min/leg wall, 50 legs = 98.6 min/seed (`state/timing_ledger.json`), per-leg train max 145.9 s.

## Proposal reasoning

**The revision: a ratio-4 confirming ladder anchored on the prediction, not a ratio-2 bracket.** The dense ladder's adjacent steps are near-tied in the log-linear rise, so its argmax is noise. Widening the rung spacing to ratio 4 makes the step *into* the predicted knee aggregate the whole rise, and the step *after* it the saturated remainder. Re-measured on B2's own ch table with the ladder `{5, 20, 80, FULL=395}`:

- mean steps `{0.2704, 0.3922, 0.0956}` → knee **80**, deciding margin **0.1218 R** = 0.0894–0.1297 film units = **4.1–6.0x `tau_rel_film`(ch)**;
- per-seed knee **80 / 80 / 80** (3/3 unanimous, where the dense ladder flipped seed 2), per-seed margins 0.1378 / 0.0860 / 0.1416 R → the *worst* seed is still 2.9–4.2x the floor.

That is a 20x improvement in margin-to-floor from a pure ladder-geometry choice, and it converts the statistic from "inside its own fold spread" to "cleanly outside it". Crucially the ladder rule reproduces `{5, 20, 80, 395}` on ch *from the surrogate's own predicted cap 80*, so the retro-check is a genuine dress rehearsal of the mechanical rule, not a fit.

**Ladder rule (mechanical, no discretion, pre-declared in phase P).** With `FULL` = the per-rung uncovered pool size (the `A1_lf_all` arm) and `c_hat` = the surrogate's dense-ladder step-max knee on `{5,10,20,40,80,160,320,FULL}` (clipped/deduped per cell):
`r3 = c_hat`; `r2 = max(2, round(c_hat/4))`; `r1 = max(1, round(c_hat/16))`; `r4 = FULL`; enforce `1 <= r1 < r2 < r3 < r4` by decrementing to the next distinct integer. If `c_hat == FULL` (surrogate predicts no interior knee), use `r3 = round(FULL/4)`, `r2 = round(FULL/16)`, `r1 = max(1, round(FULL/64))` and the pre-declared knee is `FULL`. The surrogate's knee is then **recomputed on `{r1,r2,r3,r4}`** and *that* value is the registered prediction `c_pred` (normally `= c_hat`; any divergence is recorded as a flag before the legs run).

**FLOOR justification for the grid (scope rule 3).** `r1 = c_hat/16` is not cosmetic: it must sit two ratio-4 steps below the predicted knee so the ladder can *express* a knee at `r2` as well as at `r3` — otherwise the deciding step would be the first step by construction and the test would be vacuous. The ch retro-check confirms the floor rung is low enough that the step into it (0.2704) is genuinely smaller than the deciding step (0.3922) rather than an artefact of truncation. Ceiling (`r4 = FULL`) is forced: `R(FULL) = 1` by definition for both instruments, so the saturation step is measured, not assumed.

**Registered statistic (identical formula for both instruments).** `R(c) = (nRMSE(A0_nolf) - nRMSE(arm@c)) / (nRMSE(A0_nolf) - nRMSE(A1_lf_all))` per fold (HF draw x training seed), mean over folds; steps `s_i = R(r_{i+1}) - R(r_i)`, `i = 1..3`; `K = r_{argmax(s)+1} in {r2, r3, FULL}`; margin `M_R = max(s) - second-max(s)`; `M_film = M_R x E_ds / nrmse_film_mean(ds)` with `E_ds` the fold-mean `nRMSE(A0) - nRMSE(A1)`. Threshold-free in R, exactly as B2 part 7 and websearcher directive 4 demand. Null probability of a chance match is 1/3 per cell.

**Adjudicability gate per cell (pre-declared).** A cell is ADJUDICABLE iff (a) `M_film > tau_rel_film(ds)` with a *certified* `tau_rel`, and (b) the per-seed knee is unanimous over seeds {0,1,2}. Reported alongside, not gating: the 9-fold leave-one-out jackknife modal knee and its frequency. Non-adjudicable cells are reported as UNRESOLVED — a pre-declared, publishable metrology outcome, never silently dropped.

**Cell roles (ADR-robust by construction).** Predictive (zero anchors on the cell): `sharp__allen_cahn_2d`, `sharp__fisher_kpp_2d`, `sharp__phase_field_crystal_2d`, `ifc_poisson`. Reproduction controls (knee already measured by B2): `sharp__cahn_hilliard` (cap 80), `ifc_heat` (cap 5). All four sharp cells are present under every ADR r3-0007 option, so the primary clause never moves; the ifc clauses are per-cell and simply disappear if their cells are demoted. Quantitatively the ifc cells are near-certainly UNRESOLVED anyway — clearing `tau_rel_film` 0.3359 (ifc_heat) / 0.5627 (ifc_poisson) needs `M_R x E > 0.01214` / `0.02488` nRMSE against effects of order 0.025–0.03 nRMSE, i.e. `M_R > 0.4`–0.8 — so the ADR outcome cannot change the card's verdict. pfc is pre-declared and run, but adjudicated only if a certified pfc `tau_rel` exists at analysis time (it does not today); otherwise it is reported with its margin in film units and an explicit "no certified tau — not adjudicated" flag.

**Enumerating the closed-form fold population (scope rule 3).** The surrogate's `A0` analogue is a closed-form kernel-ridge fit at `n_fit = 5`. Instead of buying GPU seeds for it, phase P runs the surrogate at **64 HF draws** and pre-declares the histogram of restricted-ladder knees over those draws (free, CPU-only), alongside the 3-draw matched prediction that is the registered one. A draw-unstable prediction is thus declared *before* the legs run.

**Instrument honesty (websearcher directive 5).** The prereg file declares, before any leg: `--kernel both`, with the **rbf** knee as the registered prediction and the **linear** knee as a specificity control (B2: Pearson 0.622, excursions to -2.5 R); and the standing level caveat (surrogate full-pool ch nRMSE 0.5753 vs trained 0.5178, 11 % worse) so no reviewer reads a level miss as a failed prediction.

**Rejected within this iteration.** (i) A 3-rung ladder `{r2, r3, FULL}` — only 2 steps, chance-match probability 1/2; rejected for power. (ii) Adding `A0` as a cap-0 rung — the first step would then always dominate on a concave curve, making the statistic degenerate; rejected (and it is not what `coverage_knee_surrogate.py` computes, so it would also break instrument identity). (iii) A shape clause (mean |R_surr - R_trained| under a bar) as a *falsification* leg — it is a level-ish statistic and ch's own measured deviation is already 1.57 `tau_rel`; kept as a reported secondary only.

## Proposal

- **Category**: `lf_value / pre-declared knee-predictability of the coverage ladder — zero-anchor structural prediction of the step-max knee cap on the film-transfer cells, sealed before any leg, confirmed by a minimal ratio-4 ladder in film units`
- **Card type**: `model` (phase P is CPU-only diagnostic; phase C trains 200-epoch legs)
- **Motivation**: the K1 verdict (quoted verbatim in `report.md`) — preempted-but-MF-composition-open, with "zero anchors on the target cell", "a training-free structural predictor", "LF absent from the test path", and "pre-declaration + adjudication of a numeric cap" listed as what remains open.
- **Concrete config, recipe, expected outcome, expected falsification, anchor reference**: as transcribed in `report.md` §Slot (single source of truth for the starter).

## Status

Slot covered. Reopen candidates: none exist for this stream (all round-3 cards `reopen_candidate: false`). Immutables self-check: **pass (11/11)** — recorded in full in `report.md`. No further revision pass required (k = 2 <= 5).
