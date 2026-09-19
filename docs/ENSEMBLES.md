# Fit and apply an ensemble

The public interface exposes exactly three rules:

| Rule | CLI value | Fitting objective |
|---|---|---|
| Selected model | `selected` | Choose the individual model with the lowest mean relative L2 |
| Inverse error mixture | `inverse` | Normalize inverse mean squared relative errors |
| Fitted mixture | `fitted` | Jointly minimize mean squared relative error, with nonnegative weights summing to one |

One fixed weight per model is shared by all spatial cells and subsequent query cases. The weights are fitted separately for each dataset. Base-model training and ensemble fitting use different examples. Query answers are needed only to score the final predictions, not to choose their weights.

## Included CPU example

From the repository root:

```bash
python -m pip install -r requirements-demo.txt
python scripts/example_ensemble.py
```

The example uses saved predictions from all nine Heat I models. Five cases fit the weights and five different cases evaluate them. A new `outputs/ensemble_<timestamp>/` directory contains:

- `fitting.npz`: predictions and known fine answers for fitting.
- `queries.npz`: model predictions for query cases, without their answers.
- `selected_weights.json`, `inverse_weights.json`, `fitted_weights.json`: fitted weights and provenance.
- `<rule>_prediction.npz`: combined fields, model names and weights.
- `metrics.json`: evaluation errors.

You can set `--output outputs/my_example` to choose a new destination. Existing destinations are not overwritten. The ten-case example is a usage demonstration, not the fixed benchmark reporting partition.

## Your own model predictions

The number of models M can be any positive integer, not necessarily nine. All predictions must use the same target grid and physical units, with the same model and case ordering.

| File | Key | Shape |
|---|---|---|
| `fitting.npz` | `predictions` | `(K, M, H, W)` |
| `fitting.npz` | `targets` | `(K, H, W)` |
| `queries.npz` | `predictions` | `(N, M, H, W)` |
| Both | `model_names` | `(M,)`, strings, recommended |

For example, save your arrays with `np.savez_compressed('fitting.npz', predictions=fit_predictions, targets=fit_targets, model_names=names)`, and save query predictions similarly without targets.

```bash
python ensemble/fit_fields.py fit --fitting fitting.npz --rule fitted --output weights.json
python ensemble/fit_fields.py predict --predictions queries.npz --weights weights.json --output mixed.npz
```

The mixed fields are in `np.load('mixed.npz')['predictions']`, shaped `(N, H, W)`. The CLI also accepts other trailing field dimensions `(N, M, ...)`, including multiple channels, provided the targets have shape `(K, ...)`. Names are checked if supplied. Invalid arrays and inconsistent model ordering are rejected. Files are written to new paths to preserve fitted-weight records.

`--calibration` remains an alias for `--fitting` for compatibility with archived scripts. It denotes the same fitting examples. Historical rule-selection experiments are retained in the analysis archive and are not additional public CLI choices.

For the complete benchmark comparison, use [numerical reproduction](REPRODUCIBILITY.md).
