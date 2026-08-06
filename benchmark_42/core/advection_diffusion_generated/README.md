# advection_diffusion_generated

**Collection:** core  
**Domain:** 2-D PDE  
**Availability:** local  

## ⚠️ Degeneracy warning

This dataset is flagged **degenerate** in `MANIFEST.csv`. It is not broken, but a model can score well on it without doing anything interesting, so results here should not be read as evidence of multi-fidelity skill.

- **copy-LF-trivial** — lifting LF onto the HF grid already reproduces HF to within 0.0057 relative L2 at full resolution. Copying the coarse field solves the task; there is no fidelity gap to learn.

See the *Degeneracy flags* section of [`../../README.md`](../../README.md) for the criteria, thresholds, and their caveats.

## Fidelity ladder

2 levels, HF grid 64x64, condition vector 2-dimensional.
LF–HF Pearson correlation 0.996.

| file | `x` (conditions) | `y` (field) |
|---|---|---|
| `train_l1.npz` | (400, 2) | (400, 1024) |
| `train_l2.npz` | (400, 2) | (400, 4096) |

Test split: `test_l1.npz`, `test_l2.npz`.

`l1` is the coarsest rung. Fields are flattened; reshape to the grid above.

## Load example

```python
import numpy as np

z = np.load("train_l2.npz")
x, y = z["x"], z["y"]
```
