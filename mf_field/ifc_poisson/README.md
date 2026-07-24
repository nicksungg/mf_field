# ifc_poisson

**Paper:** li2022ifc  
**Domain:** poisson_pde_2d  
**License:** MIT  
**Availability:** local  

## Fidelity ladder

- L1: [8, 8]
- L2: [16, 16]
- L3: [32, 32]
- L4: [64, 64]

## File layout

Top-level: `train/fidelity_{8,16,32,64}/` + `test/fidelity_64/` (test ships only at the top fidelity).

## Load example

Use the mffpbench loader (handles the pickle/scaler structure):

```python
import mffpbench
X, Y, meta = mffpbench.load("ifc_poisson", fidelity=1, split="train")
print(X.shape, Y.shape)  # (100, 3), (100, 8, 8)
```
