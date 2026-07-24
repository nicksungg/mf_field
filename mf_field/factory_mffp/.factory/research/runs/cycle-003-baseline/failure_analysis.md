# Failure Analysis — Cycle 003 Entry

## Summary
- Instances (datasets): 1/2 beating paper (composite_nRMSE = 0.04420 geomean, beats paper geomean 0.0516 by 0.86x)
- Dataset coverage:
  - `ifc_heat`: PASS (0.02634 < 0.074 paper bar — beats by 2.81x)
  - `ifc_poisson`: FAIL (0.07416 > 0.036 paper bar — 2.06x over, gap = 0.0381)
- Dominant failure mode: **`ABSENT_POISSON_LOSS_WEIGHTING`** (single-instance, but it is the *only* dataset failing and the regression vs project-previous-best H4 is fully attributable to this cause)
- Comparison with prior cycle: H3 IMPROVING overall (0.0772 → 0.0442, -43%) but REGRESSING on ifc_poisson (0.0596 → 0.0742, +25%)

## Per-Instance Results

### Instance `ifc_heat`
- Status: PASS
- Stage: training / evaluation
- Failure: none
- Root cause: n/a — H3's basis-head + coregionalization unlocks heat (74% improvement over H4: 0.09994 → 0.02634); cross-fidelity dependence on continuous `m` is well-suited to heat's smooth spectral content
- Category: n/a
- Suggested fix: do not perturb the heat-favorable parts of the recipe when porting Poisson loss reweighting (i.e., loss weights must be dataset-conditional, not globally retuned)

### Instance `ifc_poisson`
- Status: FAIL
- Stage: training (loss composition)
- Failure: H3 test nRMSE 0.07416 vs paper bar 0.036 (2.06x over). Also worse than the project's prior-best Poisson result (H4 = 0.05961). Best val nRMSE was 0.02298 — train/val healthy, generalisation to test gap suggests the optimiser was not pushed hard enough toward the HF residual under uniform weighting (capacity is there; gradient signal allocation is wrong).
- Root cause: H3's training loop applies **uniform per-fidelity loss weights** for every dataset. The H4 family discovered (and the MFRNP Poisson5 published recipe corroborates) that Poisson specifically benefits from HF-up / LF-down weighting (HF_weight=2.0, LF_weight=0.25). H3's `SMOKE_DEFAULTS` ships `hf_loss_weight=1.0, lf_loss_weights=(1.0, 1.0, 1.0)`. H3's `full_config.json` documents the alternative weights under `_poisson_loss_knob` but states `"Off by default in the smoke harness; orchestrator must opt in by overriding hf_loss_weight and lf_loss_weights when running ifc_poisson"`. The smoke pipeline (`scripts/cycle_eval.sh` → SLURM → `smoke_eval.py`) never sets that override, so the knob is dead code at eval time.
- Category: **`ABSENT_POISSON_LOSS_WEIGHTING`** (subcategory of `DATASET_INVARIANT_TRAINING_RECIPE`)
- Suggested fix (behavioral): make H3's training-loss composition dataset-aware in the same way H4's `resolve_fidelity_weights(dataset_name, p)` is. Add a dataset-name conditional in `models/fno_coreg_residual/smoke_eval.py` that switches the active `hf_loss_weight` and `lf_loss_weights` based on whether the dataset is Poisson, mirroring H4's mechanism.

### Secondary candidate failure modes for `ifc_poisson` (worth probing only after the dominant cause is addressed)

| Candidate                                       | Why it might matter on Poisson                                                                                                                | Why it is *not* the dominant cause                                                                                                                                                |
|-------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `CAPACITY_OVERALLOC_TO_LF` on Poisson           | H3 grew model capacity (hidden=64, decoder_hidden=32, K=10) over H4 (hidden=32); the extra LF parameters may pull gradients away from the HF residual when LF and HF are weighted equally. | This is essentially the same root cause expressed differently — once HF/LF weighting is dataset-conditional, the capacity asymmetry stops dominating the gradient.                                |
| `MODES_TUNED_FOR_HEAT` (Poisson higher freq.)   | The spectral modes (4, 8, 12, 12) were retained from H4's heat-friendly capacity bump; Poisson's solution field may carry more energy at higher wavenumbers than 12.                       | val_nRMSE on Poisson is 0.02298, which says the in-distribution spectral budget is sufficient — the train/test gap is much larger than any mode-truncation bias would explain.                  |
| `BASIS_HEAD_MISCALIBRATION` for Poisson         | The continuous-m basis-head `B(m)=MLP([m, m²])` is zero-init by design (so the model starts as the pure aggregator). Under uniform loss weighting it may stay near zero for Poisson because LF gradients dominate. | Same gradient-allocation story as above — fixing per-fidelity weighting will unblock the basis head naturally. Worth re-checking after the fix; not worth changing the head right now.            |

## Failure Distribution

```
Failure Distribution (per dataset, cycle-002 H3 = cycle-003 baseline):
  PASS:                            1 / 2 (50%)   ifc_heat
  ABSENT_POISSON_LOSS_WEIGHTING:   1 / 2 (50%)   ifc_poisson

Dominant failure mode: ABSENT_POISSON_LOSS_WEIGHTING (100% of failing datasets)
```

The dominant mode owns the entirety of the remaining gap to the per-dataset paper bar.

## Cross-Cycle Comparison (cycle-002 H4 → cycle-002 H3, used as cycle-003 baseline)

```
Composite (geomean):  0.07719 → 0.04420  (delta: -0.0330, -43%, IMPROVING)
ifc_heat:             0.09994 → 0.02634  (delta: -0.0736, -74%, IMPROVING — now beats paper)
ifc_poisson:          0.05961 → 0.07416  (delta: +0.0146, +25%, REGRESSING)
n_datasets_beating_paper: 0 → 1
```

- Improvements: Heat improved dramatically because the H3 hybrid (basis-head + MFRNP decoder-in-the-aggregation + coregionalization on the HF latent) is well-matched to heat's smooth, low-mode spectral content. The continuous-m formulation lets the HF residual learn a structured correction without competing for capacity with the LF backbones.
- Regressions: Poisson regressed because H4's *dataset-conditional* loss reweighting (HF=2.0, LF=0.25 for Poisson; uniform for Heat) was not carried into H3's training loop. H3 raised the model's capacity (hidden 32 → 64, decoder_hidden 0 → 32, added K=10 basis head) — under uniform weights, more capacity ends up serving the LF terms whose gradients are no longer downweighted, starving the HF residual that the test split actually scores.
- New failure modes: `ABSENT_POISSON_LOSS_WEIGHTING` — strictly a porting/regression class. H4 had the mechanism; H3 dropped it.

## Recommended Interventions

Ranked by expected impact / cost ratio. All interventions stay within the mutable surface `models/**`.

1. **Port H4's per-fidelity loss reweighting into H3.** Highest leverage. Cheap, isolated.
   - File: `models/fno_coreg_residual/smoke_eval.py`
   - Behaviorally: add a helper analogous to H4's `resolve_fidelity_weights(dataset_name, p)` that detects whether the dataset name contains `"poisson"` and returns the elevated HF / suppressed LF weights; pass those into the existing `compute_losses` call. The data path, model, and optimiser stay untouched.
   - Expected effect (sourced from H4's measured Poisson result, not from a forecasting model): ifc_poisson nRMSE should land in H4's neighbourhood (~0.060) at minimum, and the combination of H3's basis-head capacity with H4's loss weighting should plausibly do better. The composite has substantial headroom even at exactly H4's Poisson number: composite geomean would drop from 0.0442 to roughly sqrt(0.02634 * 0.0596) ≈ 0.0396 (a further -10%).
   - Risk: the heat result depends on the existing uniform weighting; make the override strictly Poisson-conditional to avoid disturbing the heat win.

2. **(Conditional on intervention 1 not fully closing the Poisson gap)** Spot-check Poisson-specific capacity allocation.
   - Files: `models/fno_coreg_residual/smoke_eval.py`, `models/fno_coreg_residual/full_config.json`
   - Behaviorally: parameterise the per-fidelity FNO `hidden` and `n_blocks` to allow a small Poisson-specific override — only if Poisson still misses paper after intervention 1. Do NOT pre-emptively re-tune.

3. **(Conditional on interventions 1+2 not closing the gap)** Investigate basis-head calibration on Poisson.
   - Files: `models/fno_coreg_residual/model.py`, `models/fno_coreg_residual/smoke_eval.py`
   - Behaviorally: probe whether the continuous-m basis-head `B(m)` activates non-trivially after training on Poisson (i.e., does the HF residual actually correct the aggregator, or does it stay at the zero-init?). If it stays near zero even with corrected loss weights, the residual path is being out-competed and the head structure may need adjustment — but this is third-priority because (1) likely makes it moot.

The first intervention is the only one that should be acted on for cycle-003 H5; the rest are contingent and intentionally not pre-committed.

## Failure Taxonomy Update

New category added this cycle:

- **`ABSENT_POISSON_LOSS_WEIGHTING`**: A successor family removed a dataset-conditional loss-reweighting mechanism that an ancestor family had introduced and that was the source of the ancestor's gains on the dataset in question. Detection: a per-dataset regression appears between a strictly-more-capable model and its weaker ancestor, while the ancestor's training loop applied dataset-name-conditional weights and the successor's does not.
  - Parent: `DATASET_INVARIANT_TRAINING_RECIPE` (a model treats all eval datasets identically during training even though the published recipe / a prior in-project family used dataset-conditional knobs).
