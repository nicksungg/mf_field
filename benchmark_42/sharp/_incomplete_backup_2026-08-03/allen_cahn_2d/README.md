# allen_cahn_2d_generated

**PDE module:** allen_cahn  
**Source:** APEBench (arXiv:2411.00180)  
**ndim:** 2  
**Availability:** regenerable (eloise sharp-field solver)  

## Fidelity ladder (ablation-driven)

- L1: [64, 64]
- L2: [128, 128]
- L3: [256, 256]

## Inputs/outputs
- `x`: (N,3) condition vector [eps, mobility, mean_composition]
- `y`: (N, prod(grid)) flattened field at each fidelity

## Sample counts
- Train: **400**  Test: **100**

## File layout
`train_l1.npz`..`train_l3.npz`, `test_l1.npz`.. — MFRNP/factory npz convention (keys `x`,`y`).
