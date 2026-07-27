# poisson_generated

**Paper:** li2022ifc  
**Domain:** poisson_pde_2d  
**License:** MIT  
**Availability:** regenerable  
**Generator:** `mffpbench.generators.poisson:generate`

## Fidelity ladder

- L1: [16, 16]
- L2: [32, 32]
- L3: [64, 64]

## Sample counts

- Train: **400**
- Test: **100**
- Total: 500

## File layout

`train_l1.npz`, `train_l2.npz`, ..., `test_l1.npz`, ... — MFRNP npz convention with keys `x` and `y`.

## Load example

```python
import numpy as np
from pathlib import Path

HERE = Path("poisson_generated")
# Load level 1 train
d = np.load(HERE / "train_l1.npz")
X, Y = d["x"], d["y"]
print(X.shape, Y.shape)

# Load every fidelity, train + test
for lvl in [1, 2, 3]:
    for split in ["train", "test"]:
        path = HERE / f"{split}_l{lvl}.npz"
        if path.exists():
            d = np.load(path)
            print(f"{split} L{lvl}: X={d['x'].shape}, Y={d['y'].shape}")
```

## Regenerate from scratch

```bash
uv run python -c "from mffpbench.generators.poisson import generate; out = generate(fidelity_levels=[16, 32, 64], n_samples=500, seed=42)"
```
