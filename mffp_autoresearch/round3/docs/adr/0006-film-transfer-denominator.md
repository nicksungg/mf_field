# ADR r3-0006 (RATIFIED): scores re-denominated to the film-transfer baseline

**Status: RATIFIED 2026-08-10 — operator instruction (Eloise): "change the denominator to film transfer's RMSE", given after the orchestrator's written recommendation to keep copy-LF (recommendation and counter-arguments recorded in the session log; operator decision governs).**

## Decision

The benchmark's headline score becomes the ratio of a model's nRMSE to the certified nRMSE of `mf_fno_transfer_film` (the factory-zoo champion and §12.3 declared baseline), per dataset:

```
skill_film(model, ds) = nRMSE(model, ds) / nRMSE_film(ds)
```

`nRMSE_film(ds)` is the 3-seed mean of the film-transfer baseline on the repaired panel, certified through the round's own machinery (stale-checkpoint gate, floor seams), with its per-seed values and CI disclosed beside every use.

## Implementation principle: exact conversion, frozen eval untouched

Both the old and new scores are ratios to the same model nRMSE, so they inter-convert exactly per dataset:

```
skill_film = skill_copylf × c_ds,   c_ds = ref_copylf(ds) / nRMSE_film(ds)
```

Therefore:

- **No frozen-eval change and no re-scoring.** `round2/eval/` continues to compute copy-LF-referenced skills; `copylf_def_hash` seams are unaffected. The re-denomination is a round-3-side transform applied at aggregation/reporting (the same layer that already owns 5-dataset aggregation).
- **Floors, anchors, and thresholds rescale by the same `c_ds`** (panel geomeans rescale by geomean(c_ds)); rankings within a fixed panel are preserved by construction.
- The conversion constants live in `state/anchors/film_denominator.json` (per-dataset `nRMSE_film` mean, per-seed values, CI, `c_ds`, provenance job IDs), built only from stale-gate-clean legs.

## Phasing (mid-flight discipline, same pattern as ADR r3-0005)

1. **Now**: certify the denominator (3 seeds × 5 scored datasets, anchor-pattern jobs into `round3_anchors/film_baseline-R3/`); publish `film_denominator.json`; re-express leaderboards, anchors presentation, and the mentor-update figures in film units (copy-LF values retained alongside during the transition).
2. **Batch 2 verdicts evaluate in the units their falsification clauses were pre-registered in** (copy-LF-referenced) — a mid-batch unit swap would unmoor the registered thresholds. Their reports carry both unit systems.
3. **Batch 3 onward**: cards register clauses in film units (thresholds priced via the rescaled certified noise floor).

## Known properties accepted by this decision (recorded, not relitigated)

- The denominator is a trained, seed-dependent object; its own variance is disclosed in `film_denominator.json` and folded into threshold pricing at the batch-3 boundary.
- The denominator changes only by future ADR (retraining or data repair ⇒ re-certification + new conversion constants, archived like every sanctioned mutation).
- `skill_film < 1` reads as "beats the best known learned baseline"; copy-LF remains available as a reported column for physical interpretability and for the preflight instruments (task-void detection still uses the copy-LF gap — a dead fidelity gap is a data property, not a baseline property).
