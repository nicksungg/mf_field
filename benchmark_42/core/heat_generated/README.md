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

## Clarifications (2026-09-06)
The field is **space-time**, not a 2-D spatial field: rows are the n implicit time steps (dt = dx, final time n/(n-1) ~ 1),
columns are the n spatial nodes of a 1-D rod. Initial condition u = 1 on 0.25 <= x <= 0.75 (row 0 is not stored).
Parameters: `x = [neumann_flux_left ~ U(0,1), neumann_flux_right ~ U(-1,0), diffusivity alpha ~ U(0.01, 0.1)]`.
Minor resolution inconsistency: the final time is n/(n-1) (1.07 at n=16, 1.016 at n=64). Amplitudes are consistent
across levels (RMS ratio 1.00-1.01); no scaling defect. An LF-abundant variant (4000 coarse rows) is at
`mf_field_v2/core/heat_generated_lfabund`.
