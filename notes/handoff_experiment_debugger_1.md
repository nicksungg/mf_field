# Handoff from experiment-debugger (attempt 1) — 2026-08-11T18:05Z

**For**: experiment-initial-analyzer, any later debugger
**Experiment**: r3s2_field_reach-B3 (job 261188 FAILED, class ALGO)

## Diagnosis

The six-cell panel invocation **completed** (22.5 min, `result_all6_s0.json` written).
The separate `--datasets guard` invocation died on `fluid`:
`FloorMatchedNError: fluid: R3S2B3_FLOOR_MATCHED_N declares sharp:320 but the HOT plan's |T| is 205`.

`floor_matched_n.matched_n_band` decided the cell shape by *"does the plan carry a `T` array"*.
`hot_split.plan`'s **proportional 80/20 fallback** — the branch a cell matching neither card protocol takes — also returns a `T`.
`fluid` has `n_train_hf = 256` → fallback → `|T| = 205`, was read as the **sharp** shape, and was asked for the `sharp:320` obligation the recipe never gave it.
The recipe names exactly two shapes (`R3S2B3_HOT_SPLIT_SHARP`, `R3S2B3_HOT_SPLIT_IFC`); the module's own `spec is None` branch already said "the guard/fallback cells carry no matched-n obligation" — the classifier just never let a guard cell reach it.

## Fix (minimal, `models_r3/r3s2_ceiling/`)

`floor_matched_n.py`: the shape is now the **card knob the plan was built from** (`plan["knob"]`), not the presence of `T`.
`fluid` → `applicable: False` with the reason recorded in `clauses.C4_floor_arms.g5_band_disclosure`.
**The refusal itself is untouched and still fires** for a genuine sharp-shape `|T| ≠ 320` (regression-checked).
Folded in the cosmetic `ladder.py:235` duplicate comment the reviewer deferred (code_hash changes anyway).

## What to watch for

- Exactly **one** cell changes behaviour: `fluid`. `heat_local` (1024 rows) and `sharp__sod_1d` (400) legitimately take the sharp protocol at `|T| = 320` and still report a matched-n band; all six panel cells are byte-unchanged. Evidence: `scratchpad/diagnose_attempt_1.out`.
- The code_hash changed, so **nothing is cached** — the relaunch re-runs the full panel (~23 min) plus the guard.
- Guard-cell G5 bands are absent *by design* now; do not read that as a missing disclosure on a scored cell.
- Unrelated but visible in the evidence: on the sharp cells `state/anchors_repaired/floors.json` carries **no `affine_on_hf_train` entry**, so `certified_full_fit_nrmse` and `systematic_correction_nrmse` are `null` for that arm (the matched-n value itself is computed: AC 0.570048). The family correctly refuses to invent a comparand; it is a round-state gap, not a code defect, and it is not mine to edit.

## Contract-tier evidence (both through `score_panel.py`, 2 epochs, seed 0, `--no_cache`)

| cell | exit | result |
|---|---|---|
| `fluid` (the failing guard path) | 0 | nRMSE 0.445968, `g5_band_disclosure.applicable = False` with the guard/fallback reason recorded |
| `sharp__allen_cahn_2d` (scored) | 0 | nRMSE 0.922577, `g5_band_disclosure.applicable = True`, `cell_shape = sharp`, spec 320, `|T| = 320` |

Artifacts: `scratchpad/debug1_contract/` (logs, per-cell JSONs), `scratchpad/diagnose_attempt_1.{py,out}`.

## Next hypothesis if this fails again

Look for the same "guard cell routed through a scored-cell obligation" shape elsewhere in the F2 discharge — `disclosure_legs` keys off `plan["protocol"]` and is already safe, but any *new* consumer of the plan should key off `plan["knob"]` / `registered_unit_eligible`, never off array presence.
