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

## Correction (2026-09-06)
This dataset is **1-D**, not 2-D: the levels are 64 / 128 / 256 points on [-1, 1] (the "16x16" above is an artefact of
16^2 = 256). It stores the final state (t = 1) of the 1-D Allen-Cahn equation, eps = 0.01, 200 implicit steps of dt = 0.005.
Parameters: `x = [interface_center ~ U(-0.7, 0.7), sign in {-1, +1}]`; the field is sign * tanh((x - c)/(sqrt(2) eps))
relaxed for one time unit. The interface width (~0.014) is unresolved at 64 and 128 points, which is the fidelity gap.
LF-abundant variant: `mf_field_v2/core/allen_cahn_generated_lfabund`.
