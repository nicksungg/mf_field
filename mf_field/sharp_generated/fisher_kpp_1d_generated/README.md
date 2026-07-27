# fisher_kpp_1d_generated

**PDE module:** fisher_kpp  
**Source:** Fisher 1937 / KPP 1937  
**ndim:** 1  
**Availability:** regenerable (eloise sharp-field solver)  

## Fidelity ladder (ablation-driven)

- L1: [128]
- L2: [256]
- L3: [512]

## Inputs/outputs
- `x`: (N,2) condition vector [D, r]
- `y`: (N, prod(grid)) flattened field at each fidelity

## Sample counts
- Train: **400**  Test: **100**

## File layout
`train_l1.npz`..`train_l3.npz`, `test_l1.npz`.. — MFRNP/factory npz convention (keys `x`,`y`).
