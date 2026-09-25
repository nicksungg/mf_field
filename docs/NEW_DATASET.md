# Train AutoMF on a new dataset

The `FieldPredictor` interface trains the requested surrogate models, fits one ensemble weight per model, and predicts fine fields from parameter vectors. Your dataset does not need a name in the benchmark roster.

## Install

From the repository root, using Python 3.10 or newer:

```bash
python -m pip install -e .
```

The base installation supports M7, the POD GP model, and all ensemble rules. To train the neural models as well:

```bash
python -m pip install -e '.[neural]'
```

Use a PyTorch installation compatible with your hardware for GPU training. `device="auto"` uses an available GPU or falls back to CPU. AutoGluon is not a dependency.

## 1. Supply parameter vectors and fields

Each fidelity level is a pair of NumPy arrays:

| Array | Shape | Meaning |
|---|---|---|
| `X` | `(N, d)` | One row of numerical simulation parameters per case |
| `Y` | `(N, H, W)` | One scalar field on a rectangular grid per case |

All levels use the same parameter columns in the same units and order. Coarse and fine grids may have different sizes, and their parameter rows need not match. Keep the physical domain and field meaning consistent across fidelities. Supply a one dimensional field as `(N, 1, W)`. The current API does not accept meshes, vector fields, images as inputs, or missing values. Flattened fields can be loaded from files when their grid shape is recorded in the manifest below.

```python
from automf import FieldDataset, FieldPredictor

data = FieldDataset(
    low_fidelity=(X_coarse, Y_coarse),
    high_fidelity=(X_fine, Y_fine),
)
```

For several coarse levels, list them from cheapest to finest:

```python
data = FieldDataset(
    low_fidelity=[(X_coarsest, Y_coarsest), (X_middle, Y_middle)],
    high_fidelity=(X_fine, Y_fine),
)
```

No evaluation answers belong in these arrays. Reserve evaluation inputs before creating the training data, excluding matching parameter rows from every training fidelity if you want an unseen input evaluation.

## 2. Train and fit weights

```python
predictor = FieldPredictor(
    path="outputs/my_dataset",
    models="all",
    rule="fitted",
    device="auto",
    random_state=42,
).fit(data, fitting_size=5, presets="balanced", epochs=100)
```

The automatic split reserves `fitting_size` fine input and field pairs for choosing weights. It excludes those inputs from fine training and removes matching inputs from every coarse level before training. The remaining fine examples train the surrogates. Parameter standardization uses the remaining fine training inputs, and all model preprocessing excludes the reserved fitting examples.

Input matching uses exact parameter values, not row positions. Preserve the same numerical parameter values when exporting a shared case at different fidelities. If repeated inputs have different random realizations, include the realization identifier in the parameters so that one input describes one target.

For an explicit fitting set, provide it separately and leave its inputs out of every training level:

```python
predictor = FieldPredictor(path="outputs/explicit_split", models="all").fit(
    data,
    fitting_data=(X_fit, Y_fit),
    presets="balanced",
    epochs=100,
)
```

Overlapping explicit fitting and training inputs are rejected. Keep any held out evaluation set separate from both. Five is an example fitting allowance, not a guarantee of accurate weights on a new problem.

### Choose models and the rule

`models="all"` uses M1 through M9. Pass a list such as `models=["M1", "M3", "M7"]` to train a smaller library. `models=["M7"]` works with the base CPU installation. This single model example checks the interface but does not demonstrate a benefit from ensembling or coarse data.

| Rule | Argument | How fitting examples determine weights |
|---|---|---|
| Selected model | `rule="selected"` | Put all weight on the model with the smallest mean relative L2 error |
| Inverse error mixture | `rule="inverse"` | Normalize the inverse of each model's mean squared relative error |
| Fitted mixture | `rule="fitted"` | Jointly minimize squared relative ensemble error with nonnegative weights that sum to one |

The chosen rule is specified by you. The API fits its weights. Each fitted weight is shared by all spatial cells and future inputs. It does not train a separate gating model that changes weights for each query.

`presets="balanced"` provides starting settings for new fits. `presets="smoke"` uses small models for an execution check. `epochs` controls the neural training allowance. A smoke run is not evidence of convergence or expected benchmark accuracy. See [model definitions and adaptations](MODELS.md) for the nine models and [historical training procedures](TRAINING.md) for reproduction.

With several coarse levels, M1, M3, M4, M5, and M6 use the first supplied level. M8 and M9 use the finest supplied coarse level and share the coarse ensemble preparation. M7 uses only fine training data.

M2 uses source and target fidelity labels for every `source < target` pair and learns from each pair's target table. With exactly two total levels, the only pair targets the fine table, so its training does not use coarse field labels. With three or more levels, the pair pool includes intermediate coarse targets. This follows the archived pair training construction rather than adding a new pretraining stage.

For M8 and M9, the balanced preset trains four coarse models in each of up to five folds before fitting the two correctors. This extra training prevents their fine training references from using coarse models fitted on the same parameter inputs. The two correctors reuse that preparation when fitted together.

## 3. Predict, inspect, and evaluate

```python
Y_pred = predictor.predict(X_new)
print(Y_pred.shape)                  # (N_new, H_fine, W_fine)

for row in predictor.leaderboard():
    print(row)                      # Fitting errors and ensemble weights

individual = predictor.predict_models(X_new)
print(individual.keys())            # The requested model IDs

metrics = predictor.evaluate(X_test, Y_test)
print(metrics)
```

`predict` needs only parameters. A model that needs a coarse reference predicts or retrieves it internally. No fresh coarse simulation is required.

The leaderboard reports errors on the fitting examples, not independent test accuracy. `evaluate` scores an unseen input set without changing the models or ensemble weights. It rejects inputs already used in training or fitting. Lower relative L2 error means a more accurate field prediction. Use evaluation answers only after choosing and fitting your procedure.

## 4. Reuse a trained predictor

Successful fitting saves the predictor to its `path`. Load it later with the same code and dependencies available:

```python
predictor = FieldPredictor.load("outputs/my_dataset")
Y_pred = predictor.predict(X_new)
predictor.save()
```

Keep the complete output directory. Only load saved predictors from a source you trust because model serialization may execute Python code.

The output directory also contains `metadata.json`, recording the model IDs, ensemble weights, training settings, grid, fitting and training identities, and per model implementation details. Choose a new empty output directory for a new fit.

## Read arrays from a directory

Create a directory with one NPZ file per level. Each file contains `x` and `y` arrays:

```python
import numpy as np
from pathlib import Path

Path("my_data").mkdir(exist_ok=True)
np.savez_compressed("my_data/coarse.npz", x=X_coarse, y=Y_coarse)
np.savez_compressed("my_data/fine.npz", x=X_fine, y=Y_fine)
```

Add `my_data/dataset.json`:

```json
{
  "low_fidelity": [{"path": "coarse.npz"}],
  "high_fidelity": {"path": "fine.npz"}
}
```

Then load and fit:

```python
data = FieldDataset.from_directory("my_data")
predictor = FieldPredictor(path="outputs/my_data", models="all").fit(
    data, fitting_size=5, epochs=100,
)
```

For flattened `y` shaped `(N, H * W)`, supply `"grid_shape": [H, W]` inside that level's JSON object. Paths are relative to the manifest directory. Add further low fidelity entries in increasing fidelity order. Evaluation files are not listed in this manifest.

## Complete runnable example

```bash
python examples/fit_new_dataset.py
python examples/fit_new_dataset.py --models all --presets smoke --epochs 2
```

The first command trains M7 on newly generated smooth scalar fields using only the base installation. The second trains all nine models with the neural dependencies. Both commands reserve fitting data, predict unseen inputs, evaluate, save, and reload the predictor. They do not download data or use archived predictions. The synthetic fields are an API demonstration, not numerical PDE solutions or a scientific benchmark.

## New fits and reported experiments

This API makes the archived surrogate architectures callable through one training workflow. Different papers and historical campaigns used different training schedules and data preparation. A generic call is therefore a new experiment rather than an exact reproduction of a reported table. The interface is inspired by AutoGluon's `fit`, `predict`, `leaderboard`, and `load` workflow. It does not implement AutoGluon's model search or its ensemble training algorithm.

Use [reproducibility instructions](REPRODUCIBILITY.md) for reported errors, [the ensemble CLI](ENSEMBLES.md) to combine predictions from models you already trained, and [the training guide](TRAINING.md) for individual baselines or exact campaign runs. B1 to B11 remain comparison baselines and are not included in `models="all"`.
