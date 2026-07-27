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
