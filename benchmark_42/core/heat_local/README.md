# heat_local

**Paper:** niu2024mfrnp  
**Domain:** heat_pde_2d  
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

HERE = Path("heat_local")
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

## Clarifications (2026-09-06)
The field is **space-time**, not a 2-D spatial field: rows are the n implicit time steps (dt = dx, final time n/(n-1) ~ 1),
columns are the n spatial nodes of a 1-D rod. Initial condition u = 1 on 0.25 <= x <= 0.75 (row 0 is not stored).
Parameters: `x = [neumann_flux_left ~ U(0,1), neumann_flux_right ~ U(-1,0), diffusivity alpha ~ U(0.01, 0.1)]`.
Minor resolution inconsistency: the final time is n/(n-1) (1.07 at n=16, 1.016 at n=64). Amplitudes are consistent
across levels (RMS ratio 1.00-1.01); no scaling defect. An LF-abundant variant (4000 coarse rows) is at
`mf_field_v2/core/heat_generated_lfabund`.
