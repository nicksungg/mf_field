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

## Version note (2026-09-06)
Two versions exist. **v1** (400/100, HF 128x128, `mf_field/lid_driven_cavity_generated`) was produced by the original
generator with `MAX_STEPS = 8000`, which stops time-marching before steady state on fine grids (128^2 needs ~28k steps,
256^2 ~100k) — its "HF" fields are not converged and it should not be used as ground truth. **v2** (this dataset: 40/10,
levels 32/64/128/256, `gen_cavity/lid_driven_cavity.py`, `MAX_STEPS = 200000`, tol 1e-5) is converged. The paper's
dataset table (400/100, 128^2) describes v1; the harness has been running v2 since 2026-08-13.
A 500-sample converged set (400/100, same solver, Re seed 42 so samples 0-49 coincide with v2) is being generated as
`mf_field_v2/core/lid_driven_cavity_generated` (+ `_lfabund` with 4000 rows at 32^2/64^2).
Parameter: `x = [Re]`, log-uniform in [100, 1000]; field = steady vorticity.
