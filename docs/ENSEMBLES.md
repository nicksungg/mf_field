# Fit and apply an ensemble

The primary rules are **Selected model**, **Inverse error mixture**, and **Fitted mixture**. The standalone CLI exposes these three choices as `selected`, `inverse` and `fitted`.

Run a complete small example using the bundled Heat I predictions:

```bash
python scripts/example_ensemble.py --output outputs/ensemble_example
```

This uses five fitting cases and five different query cases, runs each rule, saves the fixed weights, predicts without supplying query answers to the prediction command, then scores the predictions. It is a usage demonstration rather than the paper's reporting partition. Use a fresh output directory for each invocation.

For your own predictions:

```bash
python ensemble/fit_fields.py fit --calibration fitting.npz --rule fitted --output weights.json
python ensemble/fit_fields.py predict --predictions queries.npz --weights weights.json --output predicted_fields.npz
```

`fitting.npz` must contain `predictions` with shape `(K, M, H, W)` and `targets` with shape `(K, H, W)`. `queries.npz` contains `predictions` with shape `(N, M, H, W)` and no answers are required. Both may include a length-M string array `model_names`; use the same ordering in both files. The output NPZ uses the key `predictions` for the mixed fields and includes the weights and model names.

The `--calibration` spelling is retained from the archived API and means the ensemble fitting examples. These examples must be excluded from base-model training. Each fitted weight is shared by all spatial cells and query cases. The rule does not inspect an unknown fine field to choose its weights. Query targets are needed only to evaluate accuracy afterward.

For exact manuscript reproduction, use `scripts/reproduce_paper.py`; it loads the archived case partitions rather than this demonstration's first ten query rows.
