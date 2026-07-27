# MFFP-Bench unified datasets

All 15 datasets that produce real multi-fidelity field arrays, in one place.

- **7 local** (`*_local`, `era5`, `pm_test`, `ifc_*`) — pre-existing data from papers
- **8 regenerable** (`*_generated`) — produced by `mffpbench/generators/` on demand; current copy was generated with seed=42

> Note: the `chin_chun_*` urban-wind datasets were removed (2026-06-23).

## Two access patterns

### A. The Python package (works for all 15 with uniform signature)

```python
import mffpbench
X, Y, meta = mffpbench.load("darcy_generated", fidelity=1, split="train")
# Same call shape works for poisson_local, ifc_heat, etc.
```

### B. Direct npz loading (works for everything except IFC)

```python
import numpy as np
d = np.load("poisson_local/train_l1.npz")
X, Y = d["x"], d["y"]
```

Every subdirectory has its own README with the exact load snippet, fidelity ladder, and sample counts.

## Full inventory

See `../generated/datasets_summary.csv` for the canonical per-dataset table
(paper, resolutions, N_train, N_test, license).

## Storage

Some datasets are symlinked rather than copied to avoid duplicating GB of seed data:

- `era5/` → seed `data/full_dataset/era5_train_test/` (1.2 GB)
- `pm_test/` → seed `data/full_dataset/pm_test/` (1.2 GB, alias of era5)

All other datasets are real copies (~1.1 GB total).
