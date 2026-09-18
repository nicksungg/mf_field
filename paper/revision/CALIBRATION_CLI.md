# Portable calibration stage

The new `scripts/calibrate_fields.py` exposes the paper's existing calibration rules as a command line interface. It uses the bundled `data/ensemble_rules.py` unchanged. Its only nonstandard dependencies are NumPy and SciPy. Paths are resolved relative to the script or supplied explicitly, so it can run outside the original workspace.

This is a usable calibration and prediction stage for already trained models. It is not a complete base model training system. It does not bundle missing training datasets, checkpoints, scientific input definitions, or resource measurements. Supplying a new parameter vector to each base model remains the caller's responsibility. The command combines the resulting saved fields.

## Input contract

The calibration file is an NPZ archive with these arrays:

- `predictions`: a finite real numeric array with shape `(N, M, ...)`, where `N` is the number of reserved calibration cases, `M` is the number of models, and the remaining axes describe the field. A flattened `(N, M, P)` field is also accepted.
- `targets`: a finite real array with shape `(N, ...)` containing the known fine fields for exactly these calibration cases.
- `model_names`: an optional one dimensional Unicode string array of length `M`. Names must be distinct and nonempty. Named libraries are recommended.

The prediction file requires `predictions` with shape `(N_query, M, ...)`. Its model order and field shape must match calibration. When names were supplied for calibration, the prediction file must provide exactly the same names in the same order. Permuted names are rejected instead of silently reordering fields. When calibration names are absent, the saved names are `model_0`, `model_1`, and so on, and matching is positional. The caller must preserve that order.

All field axes are flattened for the same unweighted relative Euclidean error used by the bundled rules. The CLI does not infer physical quadrature weights, temperature transformations, or a geographical metric. Query targets are not an input to prediction. If an NPZ happens to contain a `targets` array, that array is not accessed.

## Exact usage

From the extracted source directory, install dependencies if they are not already available:

```sh
python3 -m pip install numpy scipy
```

Fit one predetermined rule on reserved calibration cases:

```sh
python3 scripts/calibrate_fields.py fit \
  --calibration calibration.npz \
  --rule inverse \
  --output fitted_weights.json
```

Apply the saved weights to predictions for new cases:

```sh
python3 scripts/calibrate_fields.py predict \
  --predictions query_predictions.npz \
  --weights fitted_weights.json \
  --output combined_predictions.npz
```

The `--rule` choices are:

| CLI name | Bundled rule | Fitting behavior |
| --- | --- | --- |
| `selected` | `selected_single` | Select the model with lowest mean relative error on calibration cases. |
| `inverse` | `inverse_mse` | Assign weights inversely proportional to mean squared relative calibration error. |
| `fitted` | `full` | Fit nonnegative weights summing to one using mean squared relative calibration error. |
| `auto` | `fit_auto` | Select among the three preceding rules by leaving out one calibration case at a time, then refit the selected rule on all calibration cases. |

Automatic rule selection requires at least two calibration cases. Its scoring objective is mean relative error, whereas the fitted rule's inner optimization uses squared relative error. The difference is preserved exactly rather than silently changing the manuscript's evaluated procedure. The names above concern one fixed weight per model for a dataset. They do not implement a spatial or input dependent gate.

The weights JSON records the requested and selected rules, weights, model names, original calibration array shapes, field shape, numerical fitting settings, calibration file SHA256, and the SHA256 of the bundled rule implementation. The automatic option also records its three calibration validation scores. The prediction NPZ contains the combined field as `predictions`, its fixed weights and model names, the chosen rule, and the SHA256 of the weights JSON. Prediction does not modify the weights file. Existing output paths are rejected to avoid overwriting a previous fit or prediction.

## Separation and reproducibility limits

The calibration archive must be assembled from inputs whose fine answers were reserved from base model fitting. Where the scientific protocol requires exclusion from low fidelity training, the caller must enforce that exclusion as well. This CLI cannot reconstruct or audit historical base training membership from output arrays alone. A calibration input hash records the supplied file but does not prove data separation or independence.

The prediction command has no target option, performs no scoring, and uses no future fine answers. It only loads `predictions` and optional `model_names` from the query archive. This separation makes calibration decisions replayable and prevents the command from fitting to evaluation answers. It cannot prevent a caller from choosing a rule after inspecting external evaluation results. A confirmatory experiment must freeze the rule, model library, and protocol before that inspection.

The current implementation loads the supplied predictions in memory and evaluates the existing SLSQP rule. It is suitable for stored field arrays that fit available RAM. It does not establish training cost savings or make a complete AutoML system reproducible from raw simulations.

## Validation

Run the integration checks with:

```sh
python3 scripts/check_calibration_cli.py
```

The checks copy only the CLI and `ensemble_rules.py` into isolated temporary directories. They verify all four rules against the bundled numerical implementation, preservation of field shape and source hashes, cancellation of opposite signed field errors, prediction without query answers, rejection of model order mistakes, and rejection of malformed or nonfinite arrays. A query archive with an object `targets` array that cannot be loaded under `allow_pickle=False` still predicts correctly, demonstrating that query targets are not accessed. Tests also verify immutable saved weights during prediction, rejection of invalid simplex weights, minimum automatic calibration size, and protection against existing output paths.

Revision validation: all eight integration checks passed in 8.600 seconds on 15 September 2026. These checks validate the supplied calibration interface, not base model training or scientific generalization.
