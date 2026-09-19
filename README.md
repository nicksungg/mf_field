# AutoMF: Automated ensembles for multifidelity field prediction

AutoMF combines coarse and fine training data to build a library of field surrogates, then uses a small set of separate fine examples to fit ensemble weights. At prediction time, the input is a parameter vector **x** and the output is a fine field **y**.

**22 datasets · 9 surrogate models · 11 baseline implementations · 3 ensemble rules**

![AutoMF workflow using ERA5 fields, followed by bar charts comparing the ensemble rules, nine surrogates and eleven baselines.](assets/automf_overview.gif)

[Static overview](assets/overview.png) · [Surrogate chart](assets/surrogates.png) · [Baseline chart](assets/baselines.png) · [Results and definitions](docs/RESULTS.md)

## Try it on CPU

Python 3.12 is recommended. Download and extract `AutoMF_Anonymous_Review.zip`. The small example is included. No GPU, Git account or companion data download is needed.

```bash
unzip AutoMF_Anonymous_Review.zip
cd AutoMF_Anonymous
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-demo.txt
python scripts/example_ensemble.py
```

This fits all three rules using **five Heat I examples**, then predicts and scores **five different examples** using saved M1–M9 predictions. It prints the errors and writes weights, predictions and `metrics.json` to a new directory under `outputs/`. It demonstrates ensemble fitting, without retraining the surrogates. The benchmark uses its own fixed reporting partitions.

To check the reported results and export CSV tables, using the same environment:

```bash
python scripts/reproduce_results.py
```

Outputs: `outputs/results/comparison.csv` and `per_dataset.csv`. Add `--elo` to recompute the Elo rankings. See [full numerical reproduction](docs/REPRODUCIBILITY.md) for replay from per-case archives.

## What is being compared?

### The nine surrogates: M1–M9

These are the members of the ensemble library. Each produces a fine field from parameters, including any internally predicted or retrieved coarse reference.

| ID | Surrogate | How it uses the available data |
|---|---|---|
| M1 | FiLM FNO transfer | Parameter conditioning and coarse to fine transfer |
| M2 | All pairs FNO | Fidelity conditioning and training across fidelity pairs |
| M3 | ConvNeXt transfer | Convolutional field decoder with coarse to fine transfer |
| M4 | Distribution FNO | Correction using coarse ensemble distribution summaries |
| M5 | Wavelet transfer | Wavelet field decoder with coarse to fine transfer |
| M6 | Retrieved field DeepONet | Correction of a nearest neighbour coarse training field |
| M7 | POD GP | Fine field basis with Gaussian process coefficients |
| M8 | Slice attention corrector | Iterative correction of a predicted coarse field |
| M9 | ConvNeXt corrector | Convolutional correction of a predicted coarse field |

M7 is a fine-only member. The remaining members use coarse data. These are **adapted implementations**, with their source methods and changes documented in [model adaptations](docs/MODELS.md).

### Baselines: B1–B11

These are comparison methods. They are evaluated individually and are **not included in the M1–M9 mixture**.

| ID | Baseline implementation | Source method or idea |
|---|---|---|
| B1 | Autoregressive POD GP | Kennedy–O'Hagan autoregression |
| B2 | Nonlinear POD GP | Nonlinear autoregressive multifidelity GP |
| B3 | Composite MF MLP | Composite multifidelity neural network |
| B4 | Composite MF DeepONet | Composite multifidelity DeepONet |
| B5 | Latent MF network | Deep multifidelity active learning |
| B6 | Nonlinear decoder transfer | NOMAD |
| B7 | MFRNP adapter | Multifidelity residual neural processes |
| B8 | Fidelity basis FNO | Infinite fidelity coregionalization |
| B9 | FNO transfer I | Multifidelity FNO transfer |
| B10 | FNO transfer II | A separately archived FNO transfer entry |
| B11 | Affine POD GP | Affine calibration of a coarse surrogate |

**Additional controls:** B12 Parameter kNN and B13 Training mean. Source attribution, adaptation details and shared implementation identities are in [the model guide](docs/MODELS.md). A source citation does not imply an unchanged implementation of the original method.

### Ensemble rules

| Rule | CLI name | How the weights are chosen |
|---|---|---|
| **Selected model** | `selected` | Choose the M1–M9 model with the lowest mean relative L2 error on the fitting examples |
| **Inverse error mixture** | `inverse` | Give more weight to models with smaller mean squared relative errors, then normalize |
| **Fitted mixture** | `fitted` | Jointly fit nonnegative weights that sum to one to minimize combined squared relative error |

Each dataset has its own trained library and weights. **One weight per model applies to every query and spatial cell.** Fitting examples are separate from base-model training and evaluation. Query answers are never used to choose their own prediction weights. The selected model is the reference rule, with all weight on one member.

## Fit an ensemble on your predictions

Prepare `fitting.npz` with `predictions` shaped `(K, M, H, W)` and `targets` shaped `(K, H, W)`. Prepare `queries.npz` with `predictions` shaped `(N, M, H, W)`. Include the same `model_names` string array in both files to check model ordering. The CLI supports any number of models, not just nine.

```bash
python ensemble/fit_fields.py fit --fitting fitting.npz --rule fitted --output weights.json
python ensemble/fit_fields.py predict --predictions queries.npz --weights weights.json --output mixed.npz
```

The output key is `predictions`. Replace `fitted` with `inverse` or `selected` to change the rule. See [input format and example](docs/ENSEMBLES.md).

## Train a model

Use the separate `AutoMF_Anonymous_Data.zip` companion for training arrays. Place it next to the extracted review directory. For one Heat I experiment:

```bash
python scripts/import_data.py --archive ../AutoMF_Anonymous_Data.zip --include "datasets/core/heat_generated/*"
python -m pip install -r requirements-training.txt
python scripts/train.py --model M1 --dataset heat_generated --epochs 2500
```

Use a CUDA-compatible PyTorch installation for GPU training. `--model` accepts the IDs above. M8/M9 require coarse-model preparation, and ERA5 uses its unpaired-data adapter. Follow the [training guide](docs/TRAINING.md) for those procedures and exact campaign recipes. To restore all arrays, run `python scripts/import_data.py --archive ../AutoMF_Anonymous_Data.zip`. The companion stores duplicate arrays only once and verifies SHA256 hashes when importing. See [package contents](docs/ANONYMOUS_PACKAGE.md).

## Data and code

| Location | Contents |
|---|---|
| [datasets/](datasets/) · [dataset guide](docs/DATASETS.md) | 21 PDE datasets across seven classes, plus ERA5 |
| [generators/](generators/) | Dataset generators, parameter recipes and available verification code |
| [models/](models/) · [model guide](docs/MODELS.md) | Baselines and nine surrogates, with common adapters |
| [ensemble/](ensemble/) | Three ensemble rules and fit/predict CLI |
| [campaigns/](campaigns/) | Exact later training recipes, prepared splits and saved outputs |
| [results/](results/) | Saved predictions and raw benchmark records |
| [analysis/](analysis/) | Numerical summaries, per-case archives and reproduction scripts |
| [configs/](configs/) | Dataset roster and model IDs |

<details>
<summary>View all 22 datasets</summary>

![Fields from the 22 datasets, arranged by problem class.](assets/dataset_gallery.png)

</details>

The review ZIP and data companion together contain code, data and results; the manuscript is maintained separately. Saved predictions support numerical replay, and training code supports new fits. Not every historical trained checkpoint is included. See [reproduction scope](docs/REPRODUCIBILITY.md), [results interpretation](docs/RESULTS.md) and [third-party attribution](docs/THIRD_PARTY_NOTICES.md).
