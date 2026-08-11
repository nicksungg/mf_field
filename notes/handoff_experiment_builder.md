# Handoff from experiment-builder — r3s2_field_reach-B3

**For**: code-reviewer, experiment-debugger, analyzers

## Adjudications

1. **`recipe.base_commit` vs `env._substrate_commit`.** `23018cc5` is a TRUNK
   commit carrying **no `models_r3/` tree at all** and is not an ancestor of the
   B2 branch. `e606a4f1` is the B2 branch tip, carries the family, and is what
   `_vendor_source` names. **e606a4f1 governs.** B2's builder recorded the
   identical discrepancy one batch earlier (`upsample.py` header). Full record in
   `_vendor_manifest.json::_base_commit_adjudication`.
2. **Round state and the eval layer are read from the MAIN checkout, not this
   worktree.** This worktree forked at 44f2404 (08-07), which predates the
   08-08 mce certification and the ADR r3-0005 `panel_data.py` amendment. Reading
   the worktree snapshots made the rung/lift tripwire crash and made `ifc_heat`
   read UNCERTIFIED. `nrmse.py` is asserted byte-identical across both paths.

## Provenance of every hyperparameter

All 74 non-`_` `recipe.env` keys are in `KNOB_RECIPE_VALUES` verbatim and in
`scripts/01_train_eval.sh --env` verbatim (both diffed against the card: 74/74,
zero mismatches). Optimiser constants (`SMOKE`, LRs, `DIRECT_VAL_THRESHOLD=20`)
are the base family's, unchanged. **Nothing is a builder guess.** Two thresholds
are DERIVED, not typed: `tau_film = tau_rel * c_ds` and
`tau_phi = tau_rel / skill_level` — both reproduce the card's quoted 0.076103 /
0.045486 / 0.021736 / 0.562718 and 0.07921 / 0.05128 / 0.02741 / 0.13347 exactly.
The target-scaler thresholds are `round2/tools/target_scale_spread_audit.py`'s own
argparse defaults (ADR 0004 §2), not new numbers.

## Two builder choices the card did not specify — watch these

- **Neural stages are trained once per distinct train-row set, not per leg.** On
  sharp cells all 5 legs share T=320, so the legs vary only the CLOSED-FORM stage
  (which is what `kfold5_within_T` is). On ifc every C(5,3) fold has its own T=3,
  so the stages DO retrain per fold (10x, cheap at 5 rows). Recorded per leg as
  `neural_stages_shared_with_other_legs`. This is what keeps the card's 03:00:00.
- **Cells matching neither HOT protocol** (guard cells) get a proportional 80/20
  fallback flagged `registered_unit_eligible = False` — they can never carry a
  clause.

## Fragile

- `d2_select` reuses fit accumulators across the 10x2 grid for speed; I proved it
  bit-identical to a naive refit loop (`lsi_filter._solve` IS `fit_transfer`'s
  arithmetic). If anyone edits `lsi_filter.py`, re-check that.
- C3 failed on `ifc_heat` at 2 epochs (gap 0.351 > 0.25). Expected at contract
  tier; at 200 epochs it is a real gate. `registration.ceiling_report_only_due_to_C3`
  carries the consequence.
- ifc surfaced a checkpoint-payload merge bug the single-group helmholtz run could
  not reach. Fixed; run both cell shapes on any future change.

## TBD

None.

---

# Follow-up build — 2026-08-11 (code-review F1/F2/F3 discharge)

**For**: code-reviewer (micro-review before the hold is released), analyzers

## What changed

- **F1** `d2_select.restrict_folds_to_rows` + `smoke_eval.py:1163-1189`: the D2
  selection folds are intersected with the leg's `val_rows` (operator's
  VAL_ROWS RESTRICTION; the emulator-retrain variant was NOT taken). Selection
  rows per leg: sharp 64 → 7-18, ifc 3 → 2. `d2_select.select` now takes
  `emu_fit_rows` and REFUSES an in-sample selection row.
- **F2** new `floor_matched_n.py`: the C(5,4) disclosure legs are scored
  (closed form) and `R3S2B3_G5_BAND_DISCLOSURE` is wired into C4's per-arm
  margins. `floor_arms.py` is left byte-identical (vendored).
- Label inversion fixed (`smoke_eval.py:1160`, `Counter` over leg train-rows).
- **F3** preflight suite run + archived under `scratchpad/preflight/`.

## Watch

- **The F1 repair MOVES C1/C2/C3.** They read R1/R2 nRMSEs, which depend on
  `T_leg`, which depends on the selection. Measured at contract tier on
  helmholtz: leg 3's ridge 0.1 → 0.0, C2 min 0.97158 → 0.94300. Not a
  regression — nothing had run.
- Every subset sentence B3 can write is UNIT_DEPENDENT (see the preflight INDEX).
- `transfer_gain_anatomy.py --enumerate-folds` is computable on the ifc cells
  ONLY: it materialises `list(combinations(range(400), 320))` before applying
  `--max-folds` and is OOM-killed on every sharp cell. The band anatomy + ridge
  ladder ARE archived for all four sharp cells; the enumerated-fold spread is
  not. Fixing the tool is out of a builder's scope.
- The original build note's "exactly out-of-sample" claim was overstated; the
  correction is `build_notes[13]`.
