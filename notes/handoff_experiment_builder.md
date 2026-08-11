# Handoff from experiment-builder — 2026-08-11T05:20Z

**For**: code-reviewer, experiment-debugger, orchestrator
**Experiment**: r3s3_lf_value-B3

## What I did
- **Phase P ran first and is sealed** (`state/r3s3_lf_value/prereg_knees_B3.json`,
  `_sealed_utc 2026-08-11T04:59:09Z`, payload sha256 `e98f6dc7…3e2c`, byte copy at
  `prereg/`). Predictions: ch **80** `[5,20,80,395]`, ac **20** `[1,5,20,395]`,
  fk **10** `[1,2,10,395]`, pfc **320** `[20,80,320,395]`, ifc_heat **10** `[1,2,10,95]`.
  The driver imports `tools/coverage_knee_surrogate.py` read-only and its per-cap
  `R` table is **bit-identical to the bare CLI on all 4 comparable cells**.
- Built `models_r3/r3s3_knee_prereg` (4 carded changes), vendored `_common/ckpt_binding.py`
  @ `da855da` + `tools/ckpt_data_binding.py` verbatim, and the 3 SLURM scripts (66 legs/seed).

## What to watch for
- **BLOCKED, not by this card**: `floors.json._copylf_def_hash` is stale vs the ADR
  r3-0005 eval layer, so `assert_data_binding` refuses **every** leg. Full finding,
  root cause and blast radius: `state/blocked.md`. The carded-config smoke reproduces it;
  the green smokes ran with `R3S3B3_DATA_BINDING_ASSERT=0` and are **DIAGNOSTIC**.
- **Two build-time bugs the smokes caught and I fixed** (both would have failed every
  pfc leg / every leg): (1) the family's `data_binding.py` shadowed the shipped
  `preflight/data_binding.py` that `ckpt_data_binding` imports → renamed to
  `eval_seam_binding.py`, contents unchanged; (2) B2's `lf_reference.py` predates ADR
  r3-0005, so its pfc lift was linear, not spectral — the per-leg seam assert fired at
  `max abs diff 0.14`. The ADR entry is now vendored verbatim from `panel_data.py`;
  re-verified **0.0** on all six datasets. `lf_reference.py` is therefore no longer
  byte-identical to the base blob — see the INSPIRATION vendoring table.
- Builder-resolved, NOT in the card: the 64 histogram draw seeds are `0..63`; `round()`
  is Python's; `FULL` = max-over-rungs uncovered pool (asserted draw-invariant); phase P
  loads the **stripped** view so pfc gets its ADR-r3-0005 rungs `{1}` (the CLI would use
  `{1,2}`); `data_binding.py` → `eval_seam_binding.py` (name collision, contents unchanged).
- **ifc_heat cannot reproduce B2's cap 5**: the card's own dense ladder starts at 5, so 5
  is unreachable as a step-max knee. Flagged mechanically in the seal
  (`reproduction_control.cap_in_registered_ladder = false`). Nothing was adjusted.
- The seal's fold histogram says the per-fold knee is **not** stable on ch (modal 20 at
  66 %, `c_pred=80` at 34 %) but is on pfc (98 %). Read part 5 against it.

## Suggested next steps
Orchestrator: adjudicate the floors stamp, then `scripts/submit.sh` (the seal predates
every leg and stays valid).
