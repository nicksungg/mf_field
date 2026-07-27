# advection_diffusion_generated

**Paper:** kent2026noisemf  
**Domain:** advection_diffusion_pde_2d  
**License:** MIT  
**Availability:** regenerable  
**Generator:** `mffpbench.generators.advection_diffusion:generate`

## Fidelity ladder

- L1: [32, 32]
- L2: [64, 64]

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

HERE = Path("advection_diffusion_generated")
# Load level 1 train
d = np.load(HERE / "train_l1.npz")
X, Y = d["x"], d["y"]
print(X.shape, Y.shape)

# Load every fidelity, train + test
for lvl in [1, 2]:
    for split in ["train", "test"]:
        path = HERE / f"{split}_l{lvl}.npz"
        if path.exists():
            d = np.load(path)
            print(f"{split} L{lvl}: X={d['x'].shape}, Y={d['y'].shape}")
```

## Regenerate from scratch

```bash
uv run python -c "from mffpbench.generators.advection_diffusion import generate; out = generate(fidelity_levels=[32, 64], n_samples=500, seed=42)"
```
