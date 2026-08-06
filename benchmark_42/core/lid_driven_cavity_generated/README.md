# lid_driven_cavity_generated

**Collection:** core  
**Domain:** 2-D PDE  
**Availability:** local  

## Fidelity ladder

4 levels, HF grid 256x256, condition vector 1-dimensional.
LF–HF Pearson correlation 0.799.

| file | `x` (conditions) | `y` (field) |
|---|---|---|
| `train_l1.npz` | (40, 1) | (40, 1024) |
| `train_l2.npz` | (40, 1) | (40, 4096) |
| `train_l3.npz` | (40, 1) | (40, 16384) |
| `train_l4.npz` | (40, 1) | (40, 65536) |

Test split: `test_l1.npz`, `test_l2.npz`, `test_l3.npz`, `test_l4.npz`.

`l1` is the coarsest rung. Fields are flattened; reshape to the grid above.

## Load example

```python
import numpy as np

z = np.load("train_l4.npz")
x, y = z["x"], z["y"]
```
