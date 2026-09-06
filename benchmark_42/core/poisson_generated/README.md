# poisson_generated

**Collection:** core  
**Domain:** 2-D PDE  
**Availability:** local  

## Fidelity ladder

3 levels, HF grid 64x64, condition vector 5-dimensional.
LF–HF Pearson correlation 0.977.

| file | `x` (conditions) | `y` (field) |
|---|---|---|
| `train_l1.npz` | (400, 5) | (400, 256) |
| `train_l2.npz` | (400, 5) | (400, 1024) |
| `train_l3.npz` | (400, 5) | (400, 4096) |

Test split: `test_l1.npz`, `test_l2.npz`, `test_l3.npz`.

`l1` is the coarsest rung. Fields are flattened; reshape to the grid above.

## Load example

```python
import numpy as np

z = np.load("train_l3.npz")
x, y = z["x"], z["y"]
```

## ⚠️ Known defect — resolution-dependent amplitude (found 2026-09-06)
The generator (`mf_field/generate_all_datasets.py::_make_poisson`) multiplies the Dirichlet boundary contribution by `dx**2`
(`b = dx**2 * g`), so every fidelity level solves a *different* problem: the stored field equals `dx(n)^2 x` the true
solution on that grid. Verified by re-solving sample 0 at 64x64: the shipped file matches the buggy RHS to 3e-15 and is
~4000x smaller than the correct solution (max 0.00037 vs 1.46). Per-level RMS ratios are 4.31 and 4.16 = (31/15)^2, (63/31)^2.
Consequences: the LF/HF "gap" is dominated by a 1/n^2 scalar (the manifest's `copy_lf_rel_l2 = 16.45` is this factor);
any multi-fidelity score here partly measures learning that scalar. The same scaling is present in `core/poisson_local`
and `core/ifc_poisson` (inherited IFC/MFRNP data), i.e. the defect originates upstream and was reproduced faithfully.
**Fix:** regenerated without the `dx**2` factor as `mf_field_v2/core/poisson_generated_v2` (same theta, seed 42, same
levels; plus a `_lfabund` variant with 4000 coarse rows). Do not report multi-fidelity results on this version.
**Parameters:** `x = [u(0,y), u(1,y), u(x,0), u(x,1), u_center]` — four Dirichlet boundary values and a centre point-source
value, each ~ U(0.1, 0.9). Field: 2-D solution on n x n interior nodes.
