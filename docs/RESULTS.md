# Reading the results

The comparison covers **22 datasets**, **M1–M9**, **B1–B11**, and the **Selected model**, **Inverse error mixture**, and **Fitted mixture** rules. B12 and B13 are additional reference controls, outside the 23-entry ranking.

## What a ratio means

For each dataset, first choose the M1–M9 model with the lowest mean relative L2 error on five separate fitting examples. Evaluate that selected model and the other methods on the held-out evaluation cases. Divide each method's evaluation error by the selected model's evaluation error.

- **1.00:** the same error as the selected model.
- **0.90:** 10% lower error.
- **1.20:** 20% higher error.

The selected model can differ between datasets and fitting partitions. It is not the best model chosen after seeing evaluation answers.

**Dataset ratio** takes the geometric mean of these ratios over all 22 datasets. **PDE class ratio** first takes the geometric mean within each PDE class, then across the seven classes, covering 21 PDE datasets and excluding ERA5. Per-dataset errors average cases and the prescribed fitting partitions before these aggregates are computed.

| Rule | Dataset ratio, 22 datasets | PDE class ratio, 21 PDE datasets |
|---|---:|---:|
| Selected model | 1.0000 | 1.0000 |
| Inverse error mixture | 0.9315 | 0.8876 |
| Fitted mixture | 0.9251 | 0.8840 |

The fitted mixture therefore reduces error by **7.5% across datasets** and **11.6% across PDE classes** relative to selected-model prediction. It improves by more than 1% on 16 datasets, worsens by more than 1% on five, and is within 1% on one. These are aggregate gains, not a guarantee for every task or against every baseline.

Comparisons use corresponding evaluation cases. Training resources, validation procedures and adaptations differ between implementations. The three fitting partitions reuse trained models and do not measure independent training-seed variation. See [reproduction scope](REPRODUCIBILITY.md).

## Charts and animation

The [GIF](../assets/automf_overview.gif) holds the ERA5 workflow fixed while cycling through three charts: ensemble rules, nine surrogates and eleven baselines. Every chart uses the dataset ratio above. The dashed line marks 1. Each chart starts at zero and has its own labeled linear scale. Static copies: [overview](../assets/overview.png), [surrogates](../assets/surrogates.png), [baselines](../assets/baselines.png).

The workflow uses actual ERA5 training fields at 192 × 384 and 721 × 1440. Its output illustrates a different reserved input, using saved inverse error weights. For display, the 128 × 256 model output is bilinearly interpolated onto the 721 × 1440 fine grid. This changes only the visualization, not the archived predictions, fitted weights or reported errors. The aggregate charts use all 22 datasets and are separate from that illustrative ERA5 case.

The [visual manifest](../assets/visuals_manifest.json) records the values and source hashes. Regenerate it with:

```bash
# The required overview arrays are included in the review ZIP.
python -m pip install -r requirements-visuals.txt
python scripts/build_readme_visuals.py --output outputs/readme_visuals
```

## Numeric tables and Elo

```bash
python scripts/reproduce_results.py --elo
```

This verifies the ratios from the unrounded per-dataset errors and writes:

- `outputs/results/comparison.csv`: every baseline, surrogate and ensemble rule, with ratios and Elo.
- `outputs/results/per_dataset.csv`: individual errors and ratios for every dataset.
- `outputs/results/checks.json`: verification results and source hash.

Elo ranks pairwise comparisons across datasets. Each pair plays once per dataset, starting at 1500 with K=32. We average the final rating over 500 shuffled match orders. The ordering variation is not a statistical confidence interval. The `--elo` option recomputes this ranking; the default command copies the archived Elo while verifying the error ratios. [Protocol and implementation](../analysis/scripts/elo_ranking.py).

The source table is [table2_ranking.json](../analysis/data/table2_ranking.json). This lightweight command checks aggregate reporting from saved errors. For refitting and replay from per-case records, use [the full reproduction workflow](REPRODUCIBILITY.md).
