# heat_generated

**Collection:** core  
**Domain:** 2-D PDE  
**Availability:** local  

## Fidelity ladder

3 levels, HF grid 64x64, condition vector 3-dimensional.
LF–HF Pearson correlation 0.989.

| file | `x` (conditions) | `y` (field) |
|---|---|---|
| `train_l1.npz` | (400, 3) | (400, 256) |
| `train_l2.npz` | (400, 3) | (400, 1024) |
| `train_l3.npz` | (400, 3) | (400, 4096) |

Test split: `test_l1.npz`, `test_l2.npz`, `test_l3.npz`.

`l1` is the coarsest rung. Fields are flattened; reshape to the grid above.

## Load example

```python
import numpy as np

z = np.load("train_l3.npz")
x, y = z["x"], z["y"]
```
