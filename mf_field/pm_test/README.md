# pm_test

**This dataset is an alias of `era5`** — both point at the same underlying ERA5 reanalysis data,
shipped under two different folder names by the original distributor. The catalog explicitly marks
`pm_test.alias_of = era5`.

Load example:

```python
import mffpbench
X, Y, meta = mffpbench.load("pm_test", fidelity=1, split="train")
# Identical to mffpbench.load("era5", fidelity=1, split="train")
```
