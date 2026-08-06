# allen_cahn_generated

**Collection:** core  
**Domain:** 2-D PDE  
**Availability:** local  

## Fidelity ladder

3 levels, HF grid 16x16, condition vector 2-dimensional.
LF–HF Pearson correlation 0.936.

| file | `x` (conditions) | `y` (field) |
|---|---|---|
| `train_l1.npz` | (400, 2) | (400, 64) |
| `train_l2.npz` | (400, 2) | (400, 128) |
| `train_l3.npz` | (400, 2) | (400, 256) |

Test split: `test_l1.npz`, `test_l2.npz`, `test_l3.npz`.

`l1` is the coarsest rung. Fields are flattened; reshape to the grid above.

## Load example

```python
import numpy as np

z = np.load("train_l3.npz")
x, y = z["x"], z["y"]
```
