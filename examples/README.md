# Small CPU example

`heat_demo.npz` contains ten unchanged saved prediction rows for all nine Heat I surrogates on a 64 × 64 grid. It is stored in ordinary Git, so no LFS download is needed. `heat_demo.json` records source hashes and row identities.

```bash
python scripts/example_ensemble.py
```

Run from the repository root with `requirements-demo.txt` installed. Rows 0–4 fit weights and rows 5–9 evaluate predictions. Query targets are kept out of the prediction command. This is a usage example, not the benchmark's fixed reporting partition.

To rebuild the example from the original archives:

```bash
python scripts/import_data.py --archive ../AutoMF_Anonymous_Data.zip --include "results/predictions/historical/*__heat_generated.npz"
python scripts/build_demo_data.py
```
