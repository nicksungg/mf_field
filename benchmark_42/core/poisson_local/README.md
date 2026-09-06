# poisson_local

**Paper:** niu2024mfrnp  
**Domain:** poisson_pde_2d  
**License:** MIT  
**Availability:** local  

## Fidelity ladder

- L1: [16, 16]
- L2: [32, 32]
- L3: [64, 64]
- L4: [96, 96]
- L5: [128, 128]

## File layout

`train_l1.npz`, `train_l2.npz`, ..., `test_l1.npz`, ... — MFRNP npz convention with keys `x` and `y`.

## Load example

```python
import numpy as np
from pathlib import Path

HERE = Path("poisson_local")
# Load level 1 train
d = np.load(HERE / "train_l1.npz")
X, Y = d["x"], d["y"]
print(X.shape, Y.shape)

# Load every fidelity, train + test
for lvl in [1, 2, 3, 4, 5]:
    for split in ["train", "test"]:
        path = HERE / f"{split}_l{lvl}.npz"
        if path.exists():
            d = np.load(path)
            print(f"{split} L{lvl}: X={d['x'].shape}, Y={d['y'].shape}")
```
## OOD splits

`ood/l2/`, `ood/l3/`, `ood/l5/` — each contains `train_l*.npz` / `test_l*.npz` with samples from a shifted parameter regime. Use these for out-of-distribution evaluation.

## ⚠️ Known defect (found 2026-09-06)
Per-level RMS ratios are 4.22, 4.12, 2.27, 1.79 = (31/15)^2, (63/31)^2, (95/63)^2, (127/95)^2: the field amplitude scales
as dx^2, the signature of the boundary-data scaling bug documented in `core/poisson_generated/README.md`. This data is
inherited from the MFRNP / D-MFDAL / IFC releases, so the defect is upstream. `copy_lf_rel_l2 = 66.8` in MANIFEST.csv is
that scalar. Treat multi-fidelity results on this dataset as confounded; prefer `mf_field_v2/core/poisson_generated_v2`.
Parameters (5): four Dirichlet boundary values and a centre source value (IFC convention).
