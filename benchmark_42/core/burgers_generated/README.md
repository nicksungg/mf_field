# burgers_generated

**Collection:** core  
**Domain:** 2-D PDE  
**Availability:** local  

## ⚠️ Degeneracy warning

This dataset is flagged **degenerate** in `MANIFEST.csv`. It is not broken, but a model can score well on it without doing anything interesting, so results here should not be read as evidence of multi-fidelity skill.

- **operator-hard** — the condition vector barely predicts the field (param→field distance correlation 0.059, threshold 0.15). Nothing conditions the prediction. See the caveats in the collection README before excluding this dataset on that basis alone.

See the *Degeneracy flags* section of [`../../README.md`](../../README.md) for criteria, thresholds, and caveats.

## Fidelity ladder

3 levels, HF grid 16x16, condition vector 8-dimensional.
LF–HF Pearson correlation 0.947.

| file | `x` (conditions) | `y` (field) |
|---|---|---|
| `train_l1.npz` | (400, 8) | (400, 64) |
| `train_l2.npz` | (400, 8) | (400, 128) |
| `train_l3.npz` | (400, 8) | (400, 256) |

Test split: `test_l1.npz`, `test_l2.npz`, `test_l3.npz`.

`l1` is the coarsest rung. Fields are flattened; reshape to the grid above.

## Load example

```python
import numpy as np

z = np.load("train_l3.npz")
x, y = z["x"], z["y"]
```
