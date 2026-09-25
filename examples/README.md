# Examples

## Train on new arrays

`fit_new_dataset.py` generates smooth scalar fields from three parameters, trains the requested models, fits their weights on reserved examples, and predicts new fields. It evaluates and reloads the saved predictor as well.

```bash
python -m pip install -e .
python examples/fit_new_dataset.py
```

The default uses M7 on CPU and needs no downloaded dataset. To check all nine model adapters:

```bash
python -m pip install -e '.[neural]'
python examples/fit_new_dataset.py --models all --presets smoke --epochs 2
```

These synthetic fields and short training runs demonstrate the interface. They are not numerical PDE solutions or benchmark accuracy results. See [the new dataset guide](../docs/NEW_DATASET.md) to replace them with your arrays.

## Fit weights on saved predictions

`heat_demo.npz` contains ten unchanged saved prediction rows for all nine Heat I surrogates on a 64 × 64 grid. It is stored in ordinary Git, so no LFS download is needed. `heat_demo.json` records source hashes and row identities.

```bash
python scripts/example_ensemble.py
```

Run from the repository root with `requirements-demo.txt` installed. Rows 0–4 fit weights and rows 5–9 evaluate predictions. Query targets are kept out of the prediction command. This is a usage example, not the benchmark's fixed reporting partition.

To rebuild the example from the original archives:

```bash
git lfs pull --include="results/predictions/historical/*__heat_generated.npz"
python scripts/build_demo_data.py
```
