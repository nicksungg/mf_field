# era5

**Paper:** ECMWF ERA5 reanalysis  
**Domain:** era5_reanalysis_2d  
**License:** MIT  

## Fidelity ladder (9 levels)

- L1: [144, 192]
- L2: [160, 320]
- L3: [192, 288]
- L4: [180, 288]
- L5: [120, 180]
- L6: [132, 156]
- L7: [80, 96]
- L8: [192, 384]
- L9: [721, 1440]

## Layout (symlinked)

Symlinked from the seed data:  
`/home/nicksung/Desktop/nicksung/mf_field_v2/data/full_dataset/era5_train_test` → `era5_train_test/`  

Inside `era5_train_test/`: `train_l1.npz` ... `train_l9.npz`, `test_l1.npz` ... `test_l9.npz`.

## Load example

```python
import mffpbench
X, Y, meta = mffpbench.load("era5", fidelity=1, split="train")
print(X.shape, Y.shape)  # (1222, 12), (1222, 27648)
```

⚠️ The native 721×1440 fidelity (L9) is ~10 GB to materialise in memory. Load lower fidelities first.
