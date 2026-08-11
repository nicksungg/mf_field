# Iteration 1 — `r3s3_lf_value` batch 3

## Design context considered

- Slot scope is fixed, not chosen: `state/batch3_scope_2026-08-10.md` — "**r3s3_lf_value — ONE card: knee-predictability**, registered against the film-transfer baseline per the operator's round-orientation directive (ADR r3-0006 units)". Copy-LF is not a target (rule 1). Every batch-3 family must adopt `models_r3/_common/ckpt_binding.py` (rule 2). Clause hygiene rule 3: no falsification leg whose threshold sits inside the fold-to-fold spread of its own statistic; justify a grid's FLOOR; no 0-epoch selector admitting candidates unscorable out-of-sample; enumerate the fold population instead of spending seeds on closed-form stages at `n_fit <= 5`.
- **REGISTRATION HOLD**: ADR r3-0007 (`docs/adr/0007-ifc-panel-composition-PROPOSED.md`) is PROPOSED; the card may be transcribed but registers nothing until the ADR is decided. Design must be identical under options A (keep both ifc), B (demote both), C (demote ifc_poisson only). Decisive fact read out of the ADR execution plan: "Recompute `film_denominator.json` / `unet_baseline.json` panel aggregates on the new composition (**per-dataset cells unchanged**)" — so `c_ds`, `nrmse_film_mean` and `tau_rel` are ADR-invariant per cell; only panel aggregates move. A per-cell clause set is therefore automatically robust.
- Immutables block (program.md §5) held verbatim in view; round-2 §12 rules inherited.
- Anchors: `state/anchors/film_denominator.json` (ADR r3-0006), `state/anchors_repaired/noise_floor.json` (certified 2026-08-08, 5 cells), `state/anchors_repaired/floors.json` (floor arms), `state/anchors/launch_anchors.json` (best-floor geomean 38.8368).
- Instrument: `tools/coverage_knee_surrogate.py` (promoted by B2). CPU-only, no checkpoint, no GPU. Statistic it emits: `knee_by_stepmax` = the ladder rung entered by the largest successive step of the mean recovery curve `R_surr(c)`, plus `design_rank` and `nnc` structural nulls, `--kernel {rbf,linear,both}`, `--strat-mask`.
- Prior-art verdict K1 (quoted in full in the report) and the websearcher's seven brainstormer directives.

## Proposal reasoning

**Alternatives weighed and rejected.**

1. *Consolidation of B2 (more caps / seeds / draws on ch).* Rejected by B2 part 7 itself: "the consolidation a normal batch 3 would buy here … is now the cheapest thing in the round — `tools/coverage_knee_surrogate.py` produces it in minutes with no GPU". Also out of scope.
2. *The ch forward-sensitive-27 dataset card ("is the condition vector complete?").* B2 part 7's stated alternative, and genuinely the sharper question — but the operator's directive is "do stream rec" with knee-predictability as the named card, and a dataset card would touch generator surfaces (immutable, program.md §5). Rejected; carried instead as a **reported stratified readout** on every cell (websearcher directive 6).
3. *Distillation / LF-pretrain→HF-finetune / auxiliary-loss arms* (the §12.3-style menu). Rejected: all `preempted (cite)` or certified null on B1, and `mf_fno_transfer_film` is now the *denominator* (ADR r3-0006), not an arm.
4. *Registering on an absolute recovery threshold (`R >= 0.90`).* Rejected on B2's own knife-edge (seed 1 at 0.89838, 6.5 % of a `tau_rel` under the line) and on the websearcher's directive 4, which contrasts it with `https://arxiv.org/pdf/2510.14878`'s absolute-MSE-threshold sample complexity.
5. *Re-running the D-D mediator clause.* Rejected — B2 part 7 item (4) forbids it in that form.

**Chosen shape.** A two-phase card. Phase P (CPU-only, zero GPU, before any leg): run the surrogate on every film-transfer cell of the decided panel, build the confirming ladder by a fixed mechanical rule, recompute the surrogate's knee **on that restricted ladder**, and seal the whole prediction set (sha256 + commit + UTC) into `state/r3s3_lf_value/prereg_knees_B3.json` and into the card. Phase C: run the minimal confirming ladder as 200-epoch legs; the training driver refuses to start unless the sealed prereg hash matches.

**Confirming-ladder design, first attempt (bracket at the dense ladder's own spacing).** B2 part 7 says "three caps bracketing the predicted knee, not seven", i.e. `{c_prev, c_hat, c_next}` from the dense ratio-2 ladder `{5,10,20,40,80,160,395}`, plus `A0` and `A1` for the R denominator — 5 legs per (cell, draw, seed).

**Why that first attempt fails clause hygiene — measured, not hypothesised.** Recomputing from B2's own `D_A_ch_knee.per_cap` table:

- dense-ladder steps (mean over 9 cells): `{0.1466, 0.1238, 0.1931, 0.1991, 0.0658, 0.0298}` → knee 80, but the **deciding margin is 0.00606 R**;
- converted through the card's own units (margin x E / `nrmse_film_mean`, E = 0.51–0.74 nRMSE): **0.0044–0.0064 film units against `tau_rel_film`(ch) = 0.021736 — i.e. 0.20–0.30x the certified floor**;
- per-seed the dense knee **flips**: seed 0 → 80, seed 1 → 80, **seed 2 → 40**.

So a falsification leg registered on the dense-ladder argmax would put its threshold strictly *inside* the fold-to-fold spread of its own statistic — exactly what scope rule 3 forbids, and a defect B2 did not catch. Iteration 1 therefore does not produce a registrable proposal; it produces the constraint that the ladder spacing itself is a design variable that must be chosen so the argmax is resolvable.

## Proposal

Withheld — see Status. The shape (two-phase, sealed pre-declaration, step-max statistic, film units, stratified readout, floor arms) is carried into iteration 2; the ladder construction is revised there.

## Status

Slot not yet covered; immutables self-check **pending** (blocked on the ladder-resolvability defect above). No reopen candidates exist for this stream (all cards `reopen_candidate: false`). Proceed to `iteration_2.md`.
