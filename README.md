# AutoMF: Automated ensembles for multifidelity field prediction

Review artifact for the 22-dataset manuscript. This repository bundles the data, dataset generation and preparation code, all nine surrogate implementations, eleven ranked baseline implementations and two additional baseline controls, ensemble fitting, saved experiment results, and the manuscript reproduction scripts.

## Start here

1. Read the manuscript at [`paper/main.pdf`](paper/main.pdf).
2. Check the archive with `python scripts/verify_release.py` (no third-party Python packages required).
3. Install the analysis environment and reproduce the tables and figures:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-analysis.txt
python scripts/reproduce_paper.py
```

To also rebuild and check the PDF, install a LaTeX distribution with `pdflatex`, `bibtex`, `make`, and Poppler's `pdftotext`, then run:

```bash
python scripts/reproduce_paper.py --pdf
```

Replaying the reported numbers uses the saved predictions and error statistics. It does not retrain networks. See [reproduction scope](docs/REPRODUCIBILITY.md), [training](docs/TRAINING.md), [datasets and generators](docs/DATASETS.md), and [model adaptations](docs/MODELS.md).

## Contents

| Directory | Contents |
|---|---|
| `datasets/` | All 22 dataset archives and the ERA5 source and reserved target arrays |
| `generators/` | In-house core, extension, sharp-field and cavity solver code, configurations and checks |
| `models/` | Nine library members and all baseline implementations, with common data adapters |
| `ensemble/` | Selected model, inverse error mixture and fitted mixture code |
| `campaigns/` | Exact later training recipes, prepared inputs, splits, metadata and saved predictions |
| `results/` | Historical prediction archives and raw benchmark results |
| `paper/` | Manuscript, per-case scores, Gram matrices, saved weights, tables, figures and replay scripts |
| `configs/` | The authoritative 22-dataset and 22-model-entry rosters |
| `verification/` | Integrity, import, compilation, data and reproduction checks |

The primary ensemble rules are **Selected model**, **Inverse error mixture** and **Fitted mixture**. Historical exploratory controls are retained in archived analysis sources but are not additional claimed methods. Each rule uses fitting examples that are separate from the evaluation examples. The model library and weights are trained separately for each dataset.

## Use the mixture on your own saved predictions

Prepare an NPZ with `predictions` of shape `(N, M, H, W)`, `targets` of shape `(N, H, W)`, and optional `model_names` as a string array of length `M`. Fitting targets must not have been used to train the base models. Query NPZ files contain only predictions and optional model names.

```bash
python ensemble/fit_fields.py fit --help
python ensemble/fit_fields.py predict --help
```

See [the ensemble example](docs/ENSEMBLES.md) for a runnable example using the bundled fields.

## Share through GitHub

**Extract the ZIP and push this folder. Do not commit the ZIP itself.** The included `.gitattributes` routes large array files through Git LFS. Install Git LFS before adding files:

```bash
git lfs install
git init
git add .
git commit -m "Add AutoMF review artifact"
```

Then add the intended remote and push both Git and LFS objects. A clone needs `git lfs pull` before running verification. Check the repository's LFS storage and bandwidth allowance against `release_manifest.json`; the datasets and prediction arrays are several GB. For double-blind review, use an anonymous review repository and avoid identifying account names, commit author details, or links in the submitted artifact. No remote repository was created by the packaging process.

Source-host paths and account identifiers have been normalized in the release copy. Scientific data and saved prediction arrays retain their original bytes. Third-party attribution and license notices remain in place. See [third-party notices](docs/THIRD_PARTY_NOTICES.md). The original project's public license is not assigned by this packaging operation.
